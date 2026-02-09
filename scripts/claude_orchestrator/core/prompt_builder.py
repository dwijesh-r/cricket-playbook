"""
Build system prompts for agent API calls.

Combines persona + governance rules + task context into a structured system prompt.
Loads Constitution and Task Integrity Loop excerpts, cached for efficiency.
"""

from functools import lru_cache
from typing import Optional

from scripts.claude_orchestrator import PROJECT_ROOT
from scripts.claude_orchestrator.config.agent_parser import AgentConfig


@lru_cache(maxsize=1)
def _load_constitution_excerpt() -> str:
    """Load key Constitution sections for system prompts."""
    path = PROJECT_ROOT / "config" / "CONSTITUTION.md"
    if not path.exists():
        return ""

    content = path.read_text(encoding="utf-8")
    # Extract sections 1 and 2 (Product Definition + Authority)
    lines = content.split("\n")
    excerpt_lines = []
    capturing = False
    for line in lines:
        if "## Section 1:" in line or "## Section 2:" in line:
            capturing = True
        elif line.startswith("## Section 3:"):
            capturing = False
        if capturing:
            excerpt_lines.append(line)

    return "\n".join(excerpt_lines).strip()


@lru_cache(maxsize=1)
def _load_task_integrity_excerpt() -> str:
    """Load Task Integrity Loop quick reference."""
    path = PROJECT_ROOT / "governance" / "TASK_INTEGRITY_LOOP.md"
    if not path.exists():
        return ""

    content = path.read_text(encoding="utf-8")
    # Extract the quick reference card
    lines = content.split("\n")
    excerpt_lines = []
    capturing = False
    for line in lines:
        if "Quick Reference Card" in line:
            capturing = True
        elif line.startswith("---") and capturing and len(excerpt_lines) > 3:
            excerpt_lines.append(line)
            break
        if capturing:
            excerpt_lines.append(line)

    return "\n".join(excerpt_lines).strip()


def build_system_prompt(
    agent_config: AgentConfig,
    ticket_id: Optional[str] = None,
    ticket_title: Optional[str] = None,
    epic_id: Optional[str] = None,
    additional_context: Optional[str] = None,
) -> str:
    """
    Build a complete system prompt for an agent.

    Sections:
    1. Agent Identity & Role
    2. Governance Rules
    3. Current Task (if ticket provided)
    4. Output Requirements

    Args:
        agent_config: Parsed agent configuration
        ticket_id: Optional ticket for task context
        ticket_title: Optional ticket title
        epic_id: Optional epic for broader context
        additional_context: Optional extra context to inject

    Returns:
        Complete system prompt string
    """
    sections = []

    # 1. Agent Identity
    sections.append(_build_identity_section(agent_config))

    # 2. Governance Rules
    sections.append(_build_governance_section(agent_config))

    # 3. Current Task
    if ticket_id:
        sections.append(_build_task_section(ticket_id, ticket_title, epic_id))

    # 4. Output Requirements
    sections.append(_build_output_section(agent_config))

    # 5. Additional Context
    if additional_context:
        sections.append(f"## Additional Context\n\n{additional_context}")

    return "\n\n---\n\n".join(sections)


def _build_identity_section(config: AgentConfig) -> str:
    """Build the agent identity section."""
    lines = [
        f"# You are {config.name}",
        "",
        f"**Role:** {config.description}",
        "",
        "## Your Full Brief",
        "",
        config.role_content,
    ]
    return "\n".join(lines)


def _build_governance_section(config: AgentConfig) -> str:
    """Build the governance rules section."""
    lines = [
        "## Governance Rules",
        "",
        "You operate under the Cricket Playbook Constitution v2.2.",
        "",
    ]

    # Constitution excerpt
    constitution = _load_constitution_excerpt()
    if constitution:
        lines.append("### Key Constitution Rules")
        lines.append("")
        lines.append(constitution)
        lines.append("")

    # Task Integrity Loop
    til = _load_task_integrity_excerpt()
    if til:
        lines.append("### Task Integrity Loop")
        lines.append("")
        lines.append(til)
        lines.append("")

    # Agent-specific guardrails
    if config.guardrails:
        lines.append("### Your Guardrails")
        lines.append("")
        for g in config.guardrails:
            lines.append(f"- {g}")
        lines.append("")

    # Veto authority
    if config.veto_authority:
        lines.append("### Your Veto Authority")
        lines.append("")
        lines.append(f"You can BLOCK: {config.veto_authority}")
        if config.override_chain:
            lines.append(f"Override chain: {' > '.join(config.override_chain)}")
        lines.append("")

    return "\n".join(lines)


def _build_task_section(
    ticket_id: str,
    ticket_title: Optional[str] = None,
    epic_id: Optional[str] = None,
) -> str:
    """Build the current task context section."""
    lines = [
        "## Current Task",
        "",
        f"**Ticket:** {ticket_id}",
    ]
    if ticket_title:
        lines.append(f"**Title:** {ticket_title}")
    if epic_id:
        lines.append(f"**Epic:** {epic_id}")
    lines.append("")
    lines.append(
        "Work ONLY within the scope of this ticket. "
        "If you identify additional work needed, document it as a separate task."
    )
    return "\n".join(lines)


def _build_output_section(config: AgentConfig) -> str:
    """Build the output requirements section."""
    lines = [
        "## Output Requirements",
        "",
    ]

    if config.output_paths:
        lines.append("### Expected Output Files")
        lines.append("")
        for path in config.output_paths:
            lines.append(f"- `{path}`")
        lines.append("")

    lines.append("### Response Format")
    lines.append("")
    lines.append("- Be direct and concise")
    lines.append("- Use markdown formatting")
    lines.append("- Include evidence for all claims")
    lines.append("- Flag uncertainty explicitly")

    return "\n".join(lines)
