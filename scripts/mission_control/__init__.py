"""
Mission Control - Local JIRA-style task board for Cricket Playbook agents.

This module provides ticket, epic, and sprint management with:
- 8 workflow states (IDEA → BACKLOG → READY → RUNNING → BLOCKED → etc.)
- Role-based permissions
- Gate approval workflow
- Task Integrity Loop integration
"""

__version__ = "0.1.0"
__author__ = "Cricket Playbook Team"

from pathlib import Path

# Base path for mission control data
MISSION_CONTROL_ROOT = Path(__file__).parent.parent.parent / ".mission-control"
