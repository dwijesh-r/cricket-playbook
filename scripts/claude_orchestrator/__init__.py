"""
Claude Orchestrator - Multi-agent orchestration for Cricket Playbook.

Uses the Anthropic SDK to create API-driven agents from config/agents/*.agent.md,
each with the correct persona, temperature, model, and governance rules.
"""

__version__ = "0.1.0"
__author__ = "Cricket Playbook Team"

from pathlib import Path

# Project root (cricket-playbook/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Agent config directory
AGENT_CONFIGS_DIR = PROJECT_ROOT / "config" / "agents"

# Mission Control root
MISSION_CONTROL_ROOT = PROJECT_ROOT / ".mission-control"

# Orchestrator data directories
CONVERSATIONS_DIR = MISSION_CONTROL_ROOT / "conversations"
TOKEN_DATA_DIR = MISSION_CONTROL_ROOT / "token_usage"
