"""
Ticket CLI commands for Mission Control.

Provides commands for creating, listing, updating, and managing tickets.
"""

import argparse

from scripts.mission_control.models.ticket import Ticket, VALID_STATES, VALID_PRIORITIES


def add_ticket_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add ticket commands to the argument parser."""
    ticket_parser = subparsers.add_parser("ticket", help="Ticket management commands")
    ticket_subparsers = ticket_parser.add_subparsers(dest="ticket_action", help="Ticket actions")

    # ticket create
    create_parser = ticket_subparsers.add_parser("create", help="Create a new ticket")
    create_parser.add_argument("--title", "-t", required=True, help="Ticket title")
    create_parser.add_argument(
        "--priority",
        "-p",
        choices=VALID_PRIORITIES,
        default="P2",
        help="Priority level (default: P2)",
    )
    create_parser.add_argument("--epic", "-e", help="Parent EPIC ID")
    create_parser.add_argument("--owner", "-o", help="Ticket owner")
    create_parser.add_argument("--assignee", "-a", help="Ticket assignee")
    create_parser.add_argument("--description", "-d", help="Ticket description")
    create_parser.add_argument("--llm", action="store_true", help="Mark as requiring LLM")

    # ticket list
    list_parser = ticket_subparsers.add_parser("list", help="List tickets")
    list_parser.add_argument("--state", "-s", choices=VALID_STATES, help="Filter by state")
    list_parser.add_argument("--assignee", "-a", help="Filter by assignee")
    list_parser.add_argument("--sprint", help="Filter by sprint ID")
    list_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json", "brief"],
        default="table",
        help="Output format",
    )

    # ticket show
    show_parser = ticket_subparsers.add_parser("show", help="Show ticket details")
    show_parser.add_argument("ticket_id", help="Ticket ID (e.g., TKT-001)")

    # ticket update
    update_parser = ticket_subparsers.add_parser("update", help="Update a ticket")
    update_parser.add_argument("ticket_id", help="Ticket ID (e.g., TKT-001)")
    update_parser.add_argument("--state", "-s", choices=VALID_STATES, help="New state")
    update_parser.add_argument("--priority", "-p", choices=VALID_PRIORITIES, help="New priority")
    update_parser.add_argument("--assignee", "-a", help="New assignee")
    update_parser.add_argument("--sprint", help="Assign to sprint")
    update_parser.add_argument("--title", "-t", help="New title")

    # ticket delete
    delete_parser = ticket_subparsers.add_parser("delete", help="Delete a ticket")
    delete_parser.add_argument("ticket_id", help="Ticket ID (e.g., TKT-001)")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")


def ticket_group(args: argparse.Namespace) -> int:
    """Handle ticket commands."""
    action = args.ticket_action

    if action == "create":
        return _ticket_create(args)
    elif action == "list":
        return _ticket_list(args)
    elif action == "show":
        return _ticket_show(args)
    elif action == "update":
        return _ticket_update(args)
    elif action == "delete":
        return _ticket_delete(args)
    else:
        print("Usage: mc ticket <create|list|show|update|delete>")
        return 1


def _ticket_create(args: argparse.Namespace) -> int:
    """Create a new ticket."""
    try:
        kwargs = {}
        if args.epic:
            kwargs["epic_id"] = args.epic
        if args.owner:
            kwargs["owner"] = args.owner
        if args.assignee:
            kwargs["assignee"] = args.assignee
        if args.description:
            kwargs["description"] = args.description
        if args.llm:
            kwargs["llm_required"] = True

        ticket = Ticket.create(title=args.title, priority=args.priority, **kwargs)

        print(f"✅ Created ticket: {ticket.id}")
        print(f"   Title: {ticket.title}")
        print(f"   Priority: {ticket.priority}")
        print(f"   State: {ticket.state}")
        return 0
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return 1


def _ticket_list(args: argparse.Namespace) -> int:
    """List tickets with optional filters."""
    try:
        tickets = Ticket.list(state=args.state, assignee=args.assignee, sprint_id=args.sprint)

        if not tickets:
            print("No tickets found.")
            return 0

        if args.format == "json":
            import json

            print(json.dumps([t.to_dict() for t in tickets], indent=2))
        elif args.format == "brief":
            for t in tickets:
                print(f"{t.id}: {t.title}")
        else:
            # Table format
            print(f"\n{'ID':<10} {'Priority':<8} {'State':<12} {'Assignee':<15} {'Title':<40}")
            print("-" * 85)
            for t in tickets:
                assignee = t.assignee or "-"
                title = t.title[:38] + ".." if len(t.title) > 40 else t.title
                print(f"{t.id:<10} {t.priority:<8} {t.state:<12} {assignee:<15} {title:<40}")
            print(f"\nTotal: {len(tickets)} ticket(s)")

        return 0
    except Exception as e:
        print(f"❌ Error listing tickets: {e}")
        return 1


def _ticket_show(args: argparse.Namespace) -> int:
    """Show ticket details."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        print(f"\n{'='*60}")
        print(f"Ticket: {ticket.id}")
        print(f"{'='*60}")
        print(f"Title:       {ticket.title}")
        print(f"State:       {ticket.state}")
        print(f"Priority:    {ticket.priority}")
        print(f"Progress:    {ticket.progress_pct}%")
        print(f"{'─'*60}")
        print(f"Owner:       {ticket.owner or '-'}")
        print(f"Assignee:    {ticket.assignee or '-'}")
        print(f"EPIC:        {ticket.epic_id or '-'}")
        print(f"Sprint:      {ticket.sprint_id or '-'}")
        print(f"{'─'*60}")
        print(f"LLM Required: {ticket.llm_required}")
        if ticket.llm_budget_tokens:
            print(f"LLM Budget:   {ticket.llm_budget_tokens:,} tokens")
        print(f"{'─'*60}")
        print(f"Created:     {ticket.created_at or '-'}")
        print(f"Updated:     {ticket.updated_at or '-'}")
        if ticket.completed_at:
            print(f"Completed:   {ticket.completed_at}")

        if ticket.description:
            print(f"\nDescription:\n{ticket.description}")

        if ticket.subtasks:
            print(f"\nSubtasks ({len(ticket.subtasks)}):")
            for st in ticket.subtasks:
                status_icon = (
                    "✅" if st.status == "done" else "⏳" if st.status == "in_progress" else "⬜"
                )
                print(f"  {status_icon} {st.id}: {st.title}")

        gates = ticket.gates.to_dict()
        if gates:
            print("\nGates:")
            for gate_name, gate_data in gates.items():
                status = gate_data.get("status", "PENDING")
                print(f"  • {gate_name}: {status}")

        print(f"{'='*60}\n")
        return 0
    except Exception as e:
        print(f"❌ Error showing ticket: {e}")
        return 1


def _ticket_update(args: argparse.Namespace) -> int:
    """Update a ticket."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        updated = False

        if args.state:
            old_state = ticket.state
            ticket.transition_to(args.state)
            print(f"   State: {old_state} → {args.state}")
            updated = True

        if args.priority:
            ticket.priority = args.priority
            print(f"   Priority: {args.priority}")
            updated = True

        if args.assignee:
            ticket.assignee = args.assignee
            print(f"   Assignee: {args.assignee}")
            updated = True

        if args.sprint:
            ticket.sprint_id = args.sprint
            print(f"   Sprint: {args.sprint}")
            updated = True

        if args.title:
            ticket.title = args.title
            print(f"   Title: {args.title}")
            updated = True

        if updated:
            ticket.save()
            print(f"✅ Updated ticket: {ticket.id}")
        else:
            print("No updates specified.")

        return 0
    except Exception as e:
        print(f"❌ Error updating ticket: {e}")
        return 1


def _ticket_delete(args: argparse.Namespace) -> int:
    """Delete a ticket."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        if not args.force:
            confirm = input(f"Delete ticket {args.ticket_id}: {ticket.title}? [y/N] ")
            if confirm.lower() != "y":
                print("Cancelled.")
                return 0

        ticket.delete()
        print(f"✅ Deleted ticket: {args.ticket_id}")
        return 0
    except Exception as e:
        print(f"❌ Error deleting ticket: {e}")
        return 1
