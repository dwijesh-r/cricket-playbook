"""
Veto rights and authority chain enforcement.

Based on Constitution v2.2, Section 2.2:

| Agent              | Can Block                              | Override Authority      |
|--------------------|----------------------------------------|-------------------------|
| Florentino Perez   | Any task not improving paid artifact   | Founder only            |
| N'Golo Kante       | Integrity/data quality issues          | Founder only            |
| Andy Flower        | Cricket-untrue insights                | Tom Brady + Founder     |
| Kevin De Bruyne    | Misleading visuals                     | Tom Brady               |
| Jose Mourinho      | Unrobust/unscalable solutions          | Florentino Perez        |
"""

VETO_RULES: dict[str, dict] = {
    "Florentino Perez": {
        "can_block": "Any task that doesn't improve paid artifact",
        "override_by": ["Founder"],
        "authority_level": 2,
    },
    "N'Golo Kante": {
        "can_block": "Integrity/data quality issues",
        "override_by": ["Founder"],
        "authority_level": 4,
    },
    "Andy Flower": {
        "can_block": "Cricket-untrue insights",
        "override_by": ["Tom Brady", "Founder"],
        "authority_level": 4,
    },
    "Kevin De Bruyne": {
        "can_block": "Misleading visuals",
        "override_by": ["Tom Brady"],
        "authority_level": 4,
    },
    "Jose Mourinho": {
        "can_block": "Unrobust/unscalable solutions",
        "override_by": ["Florentino Perez"],
        "authority_level": 4,
    },
}

# Authority hierarchy (lower number = higher authority)
AUTHORITY_LEVELS: dict[str, int] = {
    "Founder": 1,
    "Florentino Perez": 2,
    "Tom Brady": 3,
    # All other agents are level 4 (functional owners)
}


def can_veto(agent_name: str) -> bool:
    """Check if an agent has veto authority."""
    return agent_name in VETO_RULES


def get_veto_scope(agent_name: str) -> str:
    """Get what an agent can block."""
    if agent_name not in VETO_RULES:
        return ""
    return VETO_RULES[agent_name]["can_block"]


def can_override(overrider: str, vetoing_agent: str) -> bool:
    """
    Check if overrider can override a veto by vetoing_agent.

    Args:
        overrider: Agent attempting to override
        vetoing_agent: Agent who issued the veto

    Returns:
        True if override is allowed
    """
    if vetoing_agent not in VETO_RULES:
        return False

    allowed = VETO_RULES[vetoing_agent]["override_by"]
    return overrider in allowed


def get_authority_level(agent_name: str) -> int:
    """Get authority level for an agent (lower = higher authority)."""
    return AUTHORITY_LEVELS.get(agent_name, 4)


def outranks(agent_a: str, agent_b: str) -> bool:
    """Check if agent_a outranks agent_b in the authority chain."""
    return get_authority_level(agent_a) < get_authority_level(agent_b)
