"""
EPIC CLI commands for Mission Control.

Provides commands for creating, listing, and managing EPICs.
"""

import argparse

from scripts.mission_control.models.epic import Epic, VALID_STATUSES


def add_epic_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add epic commands to the argument parser."""
    epic_parser = subparsers.add_parser("epic", help="EPIC management commands")
    epic_subparsers = epic_parser.add_subparsers(dest="epic_action", help="EPIC actions")

    # epic create
    create_parser = epic_subparsers.add_parser("create", help="Create a new EPIC")
    create_parser.add_argument("--title", "-t", required=True, help="EPIC title")
    create_parser.add_argument("--owner", "-o", required=True, help="EPIC owner")
    create_parser.add_argument("--description", "-d", help="EPIC description")
    create_parser.add_argument("--sprint", "-s", help="Sprint ID to assign to")
    create_parser.add_argument("--target-date", help="Target completion date (YYYY-MM-DD)")

    # epic list
    list_parser = epic_subparsers.add_parser("list", help="List EPICs")
    list_parser.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    list_parser.add_argument("--owner", "-o", help="Filter by owner")
    list_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json", "brief"],
        default="table",
        help="Output format",
    )

    # epic show
    show_parser = epic_subparsers.add_parser("show", help="Show EPIC details")
    show_parser.add_argument("epic_id", help="EPIC ID (e.g., EPIC-001)")

    # epic update
    update_parser = epic_subparsers.add_parser("update", help="Update an EPIC")
    update_parser.add_argument("epic_id", help="EPIC ID (e.g., EPIC-001)")
    update_parser.add_argument("--status", choices=VALID_STATUSES, help="New status")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--owner", "-o", help="New owner")
    update_parser.add_argument("--sprint", "-s", help="Assign to sprint")

    # epic add-ticket
    add_ticket_parser = epic_subparsers.add_parser("add-ticket", help="Add a ticket to an EPIC")
    add_ticket_parser.add_argument("epic_id", help="EPIC ID")
    add_ticket_parser.add_argument("ticket_id", help="Ticket ID to add")

    # epic delete
    delete_parser = epic_subparsers.add_parser("delete", help="Delete an EPIC")
    delete_parser.add_argument("epic_id", help="EPIC ID (e.g., EPIC-001)")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")


def epic_group(args: argparse.Namespace) -> int:
    """Handle epic commands."""
    action = args.epic_action

    if action == "create":
        return _epic_create(args)
    elif action == "list":
        return _epic_list(args)
    elif action == "show":
        return _epic_show(args)
    elif action == "update":
        return _epic_update(args)
    elif action == "add-ticket":
        return _epic_add_ticket(args)
    elif action == "delete":
        return _epic_delete(args)
    else:
        print("Usage: mc epic <create|list|show|update|add-ticket|delete>")
        return 1


def _epic_create(args: argparse.Namespace) -> int:
    """Create a new EPIC."""
    try:
        kwargs = {}
        if args.description:
            kwargs["description"] = args.description
        if args.sprint:
            kwargs["sprint_id"] = args.sprint
        if args.target_date:
            kwargs["target_date"] = args.target_date

        epic = Epic.create(title=args.title, owner=args.owner, **kwargs)

        print(f"✅ Created EPIC: {epic.id}")
        print(f"   Title: {epic.title}")
        print(f"   Owner: {epic.owner}")
        print(f"   Status: {epic.status}")
        return 0
    except Exception as e:
        print(f"❌ Error creating EPIC: {e}")
        return 1


def _epic_list(args: argparse.Namespace) -> int:
    """List EPICs with optional filters."""
    try:
        epics = Epic.list(status=args.status, owner=args.owner)

        if not epics:
            print("No EPICs found.")
            return 0

        if args.format == "json":
            import json

            print(json.dumps([e.to_dict() for e in epics], indent=2))
        elif args.format == "brief":
            for e in epics:
                print(f"{e.id}: {e.title}")
        else:
            # Table format
            hdr = f"\n{'ID':<12} {'Status':<12} {'Progress':<10} {'Owner':<15} {'Title'}"
            print(hdr)
            print("-" * 70)
            for e in epics:
                title = e.title[:30] + ".." if len(e.title) > 32 else e.title
                progress = f"{e.progress_pct}%"
                print(f"{e.id:<12} {e.status:<12} {progress:<10} {e.owner:<15} {title}")
            print(f"\nTotal: {len(epics)} EPIC(s)")

        return 0
    except Exception as e:
        print(f"❌ Error listing EPICs: {e}")
        return 1


def _epic_show(args: argparse.Namespace) -> int:
    """Show EPIC details."""
    try:
        epic = Epic.get(args.epic_id)
        if not epic:
            print(f"❌ EPIC not found: {args.epic_id}")
            return 1

        print(f"\n{'=' * 60}")
        print(f"EPIC: {epic.id}")
        print(f"{'=' * 60}")
        print(f"Title:       {epic.title}")
        print(f"Status:      {epic.status}")
        print(f"Progress:    {epic.progress_pct}%")
        print(f"{'─' * 60}")
        print(f"Owner:       {epic.owner}")
        print(f"Sprint:      {epic.sprint_id or '-'}")
        print(f"Target Date: {epic.target_date or '-'}")
        print(f"{'─' * 60}")
        print(f"Created:     {epic.created_at or '-'}")
        print(f"Updated:     {epic.updated_at or '-'}")

        if epic.description:
            print(f"\nDescription:\n{epic.description}")

        print(f"\nTickets ({len(epic.tickets)}):")
        if epic.tickets:
            from scripts.mission_control.models.ticket import Ticket

            for ticket_id in epic.tickets:
                ticket = Ticket.get(ticket_id)
                if ticket:
                    state_icon = (
                        "✅"
                        if ticket.state == "DONE"
                        else "🔄"
                        if ticket.state == "RUNNING"
                        else "⬜"
                    )
                    print(f"  {state_icon} {ticket.id}: {ticket.title} [{ticket.state}]")
                else:
                    print(f"  ⚠️  {ticket_id}: (not found)")
        else:
            print("  (no tickets)")

        print(f"{'=' * 60}\n")
        return 0
    except Exception as e:
        print(f"❌ Error showing EPIC: {e}")
        return 1


def _epic_update(args: argparse.Namespace) -> int:
    """Update an EPIC."""
    try:
        epic = Epic.get(args.epic_id)
        if not epic:
            print(f"❌ EPIC not found: {args.epic_id}")
            return 1

        updated = False

        if args.status:
            epic.status = args.status
            print(f"   Status: {args.status}")
            updated = True

        if args.title:
            epic.title = args.title
            print(f"   Title: {args.title}")
            updated = True

        if args.owner:
            epic.owner = args.owner
            print(f"   Owner: {args.owner}")
            updated = True

        if args.sprint:
            epic.sprint_id = args.sprint
            print(f"   Sprint: {args.sprint}")
            updated = True

        if updated:
            epic.save()
            print(f"✅ Updated EPIC: {epic.id}")
        else:
            print("No updates specified.")

        return 0
    except Exception as e:
        print(f"❌ Error updating EPIC: {e}")
        return 1


def _epic_add_ticket(args: argparse.Namespace) -> int:
    """Add a ticket to an EPIC."""
    try:
        epic = Epic.get(args.epic_id)
        if not epic:
            print(f"❌ EPIC not found: {args.epic_id}")
            return 1

        # Verify ticket exists
        from scripts.mission_control.models.ticket import Ticket

        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        # Add ticket to epic
        epic.add_ticket(args.ticket_id)
        epic.save()

        # Update ticket's epic_id
        ticket.epic_id = args.epic_id
        ticket.save()

        print(f"✅ Added {args.ticket_id} to {args.epic_id}")
        return 0
    except Exception as e:
        print(f"❌ Error adding ticket: {e}")
        return 1


def _epic_delete(args: argparse.Namespace) -> int:
    """Delete an EPIC."""
    try:
        epic = Epic.get(args.epic_id)
        if not epic:
            print(f"❌ EPIC not found: {args.epic_id}")
            return 1

        if not args.force:
            msg = f"Delete EPIC {args.epic_id}: {epic.title}"
            if epic.tickets:
                msg += f" ({len(epic.tickets)} tickets will be orphaned)"
            confirm = input(f"{msg}? [y/N] ")
            if confirm.lower() != "y":
                print("Cancelled.")
                return 0

        epic.delete()
        print(f"✅ Deleted EPIC: {args.epic_id}")
        return 0
    except Exception as e:
        print(f"❌ Error deleting EPIC: {e}")
        return 1
