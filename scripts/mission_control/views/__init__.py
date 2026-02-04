"""Mission Control views - Kanban, Scoreboard, Cockpit."""

from .kanban import KanbanView
from .scoreboard import ScoreboardView
from .cockpit import CockpitView

__all__ = ["KanbanView", "ScoreboardView", "CockpitView"]
