"""
Map config model names to Anthropic API model IDs.

Agent configs use short names like "claude-3-5-sonnet".
The API requires full model IDs like "claude-sonnet-4-5-20250929".
"""

MODEL_MAP: dict[str, str] = {
    "claude-3-5-sonnet": "claude-sonnet-4-5-20250929",
    "claude-3-5-haiku": "claude-haiku-4-5-20251001",
    "claude-3-opus": "claude-opus-4-6",
    "claude-sonnet-4-5": "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5": "claude-haiku-4-5-20251001",
    "claude-opus-4-6": "claude-opus-4-6",
}

DEFAULT_MODEL = "claude-sonnet-4-5-20250929"


def resolve(config_model: str) -> str:
    """
    Resolve a config model name to an API model ID.

    Args:
        config_model: Model name from agent config (e.g., "claude-3-5-sonnet")

    Returns:
        Full API model ID
    """
    return MODEL_MAP.get(config_model, DEFAULT_MODEL)
