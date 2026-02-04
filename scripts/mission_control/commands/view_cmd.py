"""
View CLI commands for Mission Control.

Provides commands for Kanban board, Scoreboard, and Agent Cockpit views.
"""

import argparse

from scripts.mission_control.views.kanban import KanbanView
from scripts.mission_control.views.scoreboard import ScoreboardView
from scripts.mission_control.views.cockpit import CockpitView


def add_view_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add view commands to the argument parser."""

    # Board (Kanban)
    board_parser = subparsers.add_parser("board", help="Show Kanban board")
    board_parser.add_argument("--sprint", "-s", help="Sprint ID to filter")
    board_parser.add_argument("--assignee", "-a", help="Filter by assignee")
    board_parser.add_argument("--compact", "-c", action="store_true", help="Compact view")
    board_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # Scoreboard
    score_parser = subparsers.add_parser("score", help="Show scoreboard")
    score_parser.add_argument("--sprint", "-s", help="Sprint ID (default: active sprint)")
    score_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # Cockpit
    cockpit_parser = subparsers.add_parser("cockpit", help="Show agent cockpit")
    cockpit_parser.add_argument("--agent", "-a", help="Specific agent to show")
    cockpit_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")


def view_board(args: argparse.Namespace) -> int:
    """Show Kanban board."""
    try:
        if args.json:
            import json

            data = KanbanView.to_json(sprint_id=args.sprint)
            print(json.dumps(data, indent=2))
        else:
            output = KanbanView.render(
                sprint_id=args.sprint, assignee=args.assignee, compact=args.compact
            )
            print(output)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def view_score(args: argparse.Namespace) -> int:
    """Show scoreboard."""
    try:
        if args.json:
            import json

            data = ScoreboardView.to_json(sprint_id=args.sprint)
            print(json.dumps(data, indent=2))
        else:
            output = ScoreboardView.render(sprint_id=args.sprint)
            print(output)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def view_cockpit(args: argparse.Namespace) -> int:
    """Show agent cockpit."""
    try:
        if args.json:
            import json

            data = CockpitView.to_json(agent=args.agent)
            print(json.dumps(data, indent=2))
        else:
            output = CockpitView.render(agent=args.agent)
            print(output)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
