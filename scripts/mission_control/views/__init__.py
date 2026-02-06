"""Mission Control views - Kanban, Scoreboard, Cockpit."""

from .cockpit import CockpitView
from .kanban import KanbanView
from .scoreboard import ScoreboardView

__all__ = ["KanbanView", "ScoreboardView", "CockpitView"]
