"""
Parse agent configuration files from config/agents/*.agent.md.

Handles two formats:
- YAML frontmatter (13 agents): name, description, model, temperature, tools
- Pure markdown (Florentino Perez): parsed from ## headings
"""

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from scripts.claude_orchestrator import AGENT_CONFIGS_DIR


@dataclass
class AgentConfig:
    """Parsed agent configuration."""

    name: str
    description: str
    model: str
    temperature: float
    tools: list[str] = field(default_factory=list)
    role_content: str = ""
    output_paths: list[str] = field(default_factory=list)
    veto_authority: Optional[str] = None
    override_chain: list[str] = field(default_factory=list)
    guardrails: list[str] = field(default_factory=list)
    collaboration: list[str] = field(default_factory=list)
    source_file: str = ""


def _parse_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and remaining markdown body."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)
    return frontmatter or {}, body


def _extract_output_paths(body: str) -> list[str]:
    """Extract output file paths from markdown body."""
    paths = []
    for match in re.finditer(r"`([^`]+(?:\.md|\.json|\.jsonl|\.yaml))`", body):
        path = match.group(1)
        if "/" in path or path.startswith("."):
            paths.append(path)
    return list(dict.fromkeys(paths))  # deduplicate, preserve order


def _extract_section(body: str, heading: str) -> str:
    """Extract content under a specific ## heading."""
    pattern = rf"## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, body, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_bullet_items(section_text: str) -> list[str]:
    """Extract bullet-pointed items from a section."""
    items = []
    for line in section_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def _parse_florentino(content: str, source_file: str) -> AgentConfig:
    """Parse Florentino Perez's pure-markdown format (no YAML frontmatter)."""
    name = "Florentino Perez"
    description = ""

    core_identity = _extract_section(content, "Core Identity")
    if core_identity:
        first_sentence = core_identity.split(".")[0] + "."
        description = first_sentence.strip()

    kill_switch = _extract_section(content, "Kill-Switch Authority")

    role_content = content  # Use full body as role content

    veto_authority = None
    if kill_switch:
        veto_authority = "Kill features that dilute the USP; halt unjustified work"

    return AgentConfig(
        name=name,
        description=description or "Program Director & Strategic Operator",
        model="claude-3-5-sonnet",
        temperature=0.20,
        tools=["read_file", "write_file", "list_files", "search"],
        role_content=role_content,
        output_paths=_extract_output_paths(content),
        veto_authority=veto_authority,
        override_chain=["Founder"],
        guardrails=[
            "No new ideas after scope freeze",
            "No experimental metrics in paid artifacts without explicit approval",
            "Saying no is a competitive advantage",
        ],
        collaboration=_extract_bullet_items(_extract_section(content, "Collaboration Model")),
        source_file=source_file,
    )


# Veto rights from Constitution v2.2, Section 2.2
_VETO_MAP = {
    "Florentino Perez": {
        "authority": "Any task that doesn't improve paid artifact",
        "override": ["Founder"],
    },
    "N'Golo Kante": {
        "authority": "Integrity/data quality issues",
        "override": ["Founder"],
    },
    "Andy Flower": {
        "authority": "Cricket-untrue insights",
        "override": ["Tom Brady", "Founder"],
    },
    "Kevin De Bruyne": {
        "authority": "Misleading visuals",
        "override": ["Tom Brady"],
    },
    "Jose Mourinho": {
        "authority": "Unrobust/unscalable solutions",
        "override": ["Florentino Perez"],
    },
}

# Canonical name mapping (handles variations in filenames)
_NAME_NORMALIZATION = {
    "N'Golo Kanté": "N'Golo Kante",
    "Florentino Pérez": "Florentino Perez",
    "Kevin de Bruyne": "Kevin De Bruyne",
}


def _normalize_name(name: str) -> str:
    """Normalize agent name for consistent lookups."""
    return _NAME_NORMALIZATION.get(name, name)


def parse_agent_file(filepath: Path) -> AgentConfig:
    """Parse a single .agent.md file into an AgentConfig."""
    content = filepath.read_text(encoding="utf-8")
    source_file = str(filepath)

    # Check for Florentino's pure-markdown format
    if not content.startswith("---"):
        return _parse_florentino(content, source_file)

    frontmatter, body = _parse_yaml_frontmatter(content)

    name = frontmatter.get("name", filepath.stem.replace("-", " ").title())
    normalized = _normalize_name(name)

    # Extract veto info from Constitution mapping
    veto_info = _VETO_MAP.get(normalized, {})

    # Extract guardrails
    guardrails_text = _extract_section(body, "Guardrails")
    if not guardrails_text:
        guardrails_text = _extract_section(body, "Non-negotiables")
    if not guardrails_text:
        guardrails_text = _extract_section(body, "Rules")
    guardrails = _extract_bullet_items(guardrails_text) if guardrails_text else []

    # Extract collaboration
    collab_text = _extract_section(body, "Collaboration")
    if not collab_text:
        collab_text = _extract_section(body, "Working relationships")
    collaboration = _extract_bullet_items(collab_text) if collab_text else []

    return AgentConfig(
        name=name,
        description=frontmatter.get("description", ""),
        model=frontmatter.get("model", "claude-3-5-sonnet"),
        temperature=float(frontmatter.get("temperature", 0.25)),
        tools=frontmatter.get("tools", []),
        role_content=body.strip(),
        output_paths=_extract_output_paths(body),
        veto_authority=veto_info.get("authority"),
        override_chain=veto_info.get("override", []),
        guardrails=guardrails,
        collaboration=collaboration,
        source_file=source_file,
    )


@lru_cache(maxsize=1)
def parse_all_agents() -> dict[str, AgentConfig]:
    """
    Parse all agent config files and return as a name-keyed dict.

    Returns:
        Dictionary mapping agent name -> AgentConfig
    """
    agents = {}
    if not AGENT_CONFIGS_DIR.exists():
        raise FileNotFoundError(f"Agent configs directory not found: {AGENT_CONFIGS_DIR}")

    for filepath in sorted(AGENT_CONFIGS_DIR.glob("*.agent.md")):
        config = parse_agent_file(filepath)
        agents[config.name] = config

    return agents


def reload_agents() -> dict[str, AgentConfig]:
    """Force reload agent configs (clears cache)."""
    parse_all_agents.cache_clear()
    return parse_all_agents()


def get_agent(name: str) -> AgentConfig:
    """
    Get a single agent config by name.

    Raises:
        KeyError: If agent not found
    """
    agents = parse_all_agents()
    if name not in agents:
        # Try case-insensitive match
        for agent_name, config in agents.items():
            if agent_name.lower() == name.lower():
                return config
        available = ", ".join(sorted(agents.keys()))
        raise KeyError(f"Agent '{name}' not found. Available: {available}")
    return agents[name]
