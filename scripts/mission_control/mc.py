#!/usr/bin/env python3
"""
Mission Control CLI - Task management for Cricket Playbook agents.

Usage:
    mc ticket create --title "..." --priority P0
    mc ticket list [--state STATE] [--assignee AGENT]
    mc ticket show TKT-001
    mc ticket update TKT-001 --state RUNNING
    mc epic create --title "..." --owner "Tom Brady"
    mc epic list
    mc sprint create --title "..." --start YYYY-MM-DD --end YYYY-MM-DD
    mc sprint active
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports when running directly
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from scripts.mission_control import __version__, MISSION_CONTROL_ROOT
from scripts.mission_control.commands.ticket_cmd import (
    add_ticket_subparser,
    ticket_group,
)
from scripts.mission_control.commands.epic_cmd import add_epic_subparser, epic_group
from scripts.mission_control.commands.sprint_cmd import (
    add_sprint_subparser,
    sprint_group,
)
from scripts.mission_control.commands.approve_cmd import (
    add_approve_subparser,
    approve_group,
)
from scripts.mission_control.commands.view_cmd import (
    add_view_subparser,
    view_board,
    view_score,
    view_cockpit,
)
from scripts.mission_control.commands.llm_cmd import add_llm_subparser, llm_group


def ensure_directories():
    """Ensure all Mission Control directories exist."""
    dirs = [
        MISSION_CONTROL_ROOT / "data" / "tickets",
        MISSION_CONTROL_ROOT / "data" / "epics",
        MISSION_CONTROL_ROOT / "data" / "sprints",
        MISSION_CONTROL_ROOT / "data" / "agents",
        MISSION_CONTROL_ROOT / "indexes",
        MISSION_CONTROL_ROOT / "views",
        MISSION_CONTROL_ROOT / "logs",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="mc",
        description="Mission Control - Task management for Cricket Playbook agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mc ticket create --title "Fix authentication bug" --priority P0
  mc ticket list --state RUNNING
  mc ticket show TKT-001
  mc ticket update TKT-001 --state REVIEW

  mc epic create --title "Sprint 4 Goals" --owner "Tom Brady"
  mc epic list --status ACTIVE

  mc sprint create --title "Sprint 4" --start 2026-01-31 --end 2026-02-14
  mc sprint active

For more information, see: governance/MISSION_CONTROL_DESIGN_020426_v1.md
        """,
    )

    parser.add_argument(
        "--version", "-v", action="version", version=f"Mission Control v{__version__}"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    # Add subcommand parsers
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add entity subparsers
    add_ticket_subparser(subparsers)
    add_epic_subparser(subparsers)
    add_sprint_subparser(subparsers)
    add_approve_subparser(subparsers)

    # Add view subparsers (board, score, cockpit)
    add_view_subparser(subparsers)

    # Add LLM approval commands
    add_llm_subparser(subparsers)

    # Status command
    subparsers.add_parser("status", help="Show Mission Control status")

    return parser


def cmd_status(args: argparse.Namespace) -> int:
    """Show Mission Control status."""
    from scripts.mission_control.models.ticket import Ticket
    from scripts.mission_control.models.epic import Epic
    from scripts.mission_control.models.sprint import Sprint

    print(f"\n🚀 Mission Control v{__version__}")
    print(f"{'─' * 40}")

    # Count entities
    tickets = Ticket.list()
    epics = Epic.list()
    sprints = Sprint.list()

    print(f"Tickets: {len(tickets)}")
    print(f"EPICs:   {len(epics)}")
    print(f"Sprints: {len(sprints)}")

    # Show active sprint
    active_sprint = Sprint.get_active()
    if active_sprint:
        print(f"\n🏃 Active Sprint: {active_sprint.id}")
        print(f"   {active_sprint.title}")

    # Show tickets by state
    if tickets:
        state_counts = {}
        for t in tickets:
            state_counts[t.state] = state_counts.get(t.state, 0) + 1
        print("\nTickets by State:")
        for state in [
            "IDEA",
            "BACKLOG",
            "READY",
            "RUNNING",
            "BLOCKED",
            "REVIEW",
            "VALIDATION",
            "DONE",
        ]:
            count = state_counts.get(state, 0)
            if count > 0:
                print(f"  {state}: {count}")

    print(f"{'─' * 40}\n")
    return 0


def main() -> int:
    """Main entry point."""
    # Ensure directories exist
    ensure_directories()

    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()

    if args.debug:
        print(f"Debug: args = {args}")

    # Route to appropriate handler
    if args.command == "ticket":
        return ticket_group(args)
    elif args.command == "epic":
        return epic_group(args)
    elif args.command == "sprint":
        return sprint_group(args)
    elif args.command == "approve":
        return approve_group(args)
    elif args.command == "board":
        return view_board(args)
    elif args.command == "score":
        return view_score(args)
    elif args.command == "cockpit":
        return view_cockpit(args)
    elif args.command == "llm":
        return llm_group(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command is None:
        parser.print_help()
        return 0
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
