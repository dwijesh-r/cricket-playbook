"""
Sprint CLI commands for Mission Control.

Provides commands for creating, listing, and managing sprints.
"""

import argparse

from scripts.mission_control.models.sprint import Sprint, VALID_STATUSES


def add_sprint_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add sprint commands to the argument parser."""
    sprint_parser = subparsers.add_parser("sprint", help="Sprint management commands")
    sprint_subparsers = sprint_parser.add_subparsers(dest="sprint_action", help="Sprint actions")

    # sprint create
    create_parser = sprint_subparsers.add_parser("create", help="Create a new sprint")
    create_parser.add_argument("--title", "-t", required=True, help="Sprint title")
    create_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    create_parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    create_parser.add_argument("--description", "-d", help="Sprint description")
    create_parser.add_argument(
        "--duration", type=int, default=2, help="Duration in weeks (default: 2)"
    )
    create_parser.add_argument("--budget", type=int, default=100000, help="LLM token budget")

    # sprint list
    list_parser = sprint_subparsers.add_parser("list", help="List sprints")
    list_parser.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    list_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json", "brief"],
        default="table",
        help="Output format",
    )

    # sprint show
    show_parser = sprint_subparsers.add_parser("show", help="Show sprint details")
    show_parser.add_argument("sprint_id", help="Sprint ID (e.g., SPRINT-4)")

    # sprint update
    update_parser = sprint_subparsers.add_parser("update", help="Update a sprint")
    update_parser.add_argument("sprint_id", help="Sprint ID")
    update_parser.add_argument("--status", choices=VALID_STATUSES, help="New status")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--budget", type=int, help="New LLM token budget")

    # sprint add-ticket
    add_ticket_parser = sprint_subparsers.add_parser("add-ticket", help="Add ticket to sprint")
    add_ticket_parser.add_argument("sprint_id", help="Sprint ID")
    add_ticket_parser.add_argument("ticket_id", help="Ticket ID to add")

    # sprint active
    sprint_subparsers.add_parser("active", help="Show active sprint")


def sprint_group(args: argparse.Namespace) -> int:
    """Handle sprint commands."""
    action = args.sprint_action

    if action == "create":
        return _sprint_create(args)
    elif action == "list":
        return _sprint_list(args)
    elif action == "show":
        return _sprint_show(args)
    elif action == "update":
        return _sprint_update(args)
    elif action == "add-ticket":
        return _sprint_add_ticket(args)
    elif action == "active":
        return _sprint_active(args)
    else:
        print("Usage: mc sprint <create|list|show|update|add-ticket|active>")
        return 1


def _sprint_create(args: argparse.Namespace) -> int:
    """Create a new sprint."""
    try:
        from scripts.mission_control.models.sprint import LLMBudget

        kwargs = {
            "duration_weeks": args.duration,
        }
        if args.description:
            kwargs["description"] = args.description

        # Create with LLM budget
        kwargs["llm_budget"] = LLMBudget(total_tokens=args.budget)

        sprint = Sprint.create(title=args.title, start_date=args.start, end_date=args.end, **kwargs)

        print(f"✅ Created sprint: {sprint.id}")
        print(f"   Title: {sprint.title}")
        print(f"   Duration: {sprint.duration_weeks} weeks")
        print(f"   Period: {sprint.start_date} → {sprint.end_date}")
        print(f"   LLM Budget: {sprint.llm_budget.total_tokens:,} tokens")
        return 0
    except Exception as e:
        print(f"❌ Error creating sprint: {e}")
        return 1


def _sprint_list(args: argparse.Namespace) -> int:
    """List sprints with optional filters."""
    try:
        sprints = Sprint.list(status=args.status)

        if not sprints:
            print("No sprints found.")
            return 0

        if args.format == "json":
            import json

            print(json.dumps([s.to_dict() for s in sprints], indent=2))
        elif args.format == "brief":
            for s in sprints:
                print(f"{s.id}: {s.title}")
        else:
            # Table format
            print(f"\n{'ID':<12} {'Status':<12} {'Period':<25} {'Tickets':<8} {'Title':<30}")
            print("-" * 87)
            for s in sprints:
                title = s.title[:28] + ".." if len(s.title) > 30 else s.title
                period = f"{s.start_date} → {s.end_date}"
                tickets = str(len(s.tickets))
                print(f"{s.id:<12} {s.status:<12} {period:<25} {tickets:<8} {title:<30}")
            print(f"\nTotal: {len(sprints)} sprint(s)")

        return 0
    except Exception as e:
        print(f"❌ Error listing sprints: {e}")
        return 1


def _sprint_show(args: argparse.Namespace) -> int:
    """Show sprint details."""
    try:
        sprint = Sprint.get(args.sprint_id)
        if not sprint:
            print(f"❌ Sprint not found: {args.sprint_id}")
            return 1

        print(f"\n{'='*60}")
        print(f"Sprint: {sprint.id}")
        print(f"{'='*60}")
        print(f"Title:       {sprint.title}")
        print(f"Status:      {sprint.status}")
        print(f"Duration:    {sprint.duration_weeks} weeks")
        print(f"{'─'*60}")
        print(f"Start Date:  {sprint.start_date}")
        print(f"End Date:    {sprint.end_date}")
        print(f"{'─'*60}")

        # LLM Budget
        budget = sprint.llm_budget
        print("LLM Budget:")
        print(f"  Total:     {budget.total_tokens:,} tokens")
        print(f"  Used:      {budget.used_tokens:,} tokens")
        print(f"  Remaining: {budget.remaining_tokens:,} tokens")
        print(f"  Usage:     {budget.utilization_pct:.1f}%")

        # Velocity
        velocity = sprint.velocity
        print(f"{'─'*60}")
        print("Velocity:")
        print(f"  Planned:   {velocity.planned_points} points")
        print(f"  Completed: {velocity.completed_points} points")
        print(f"  Progress:  {velocity.completion_pct:.1f}%")

        # EPICs
        print(f"{'─'*60}")
        print(f"EPICs ({len(sprint.epics)}):")
        if sprint.epics:
            from scripts.mission_control.models.epic import Epic

            for epic_id in sprint.epics:
                epic = Epic.get(epic_id)
                if epic:
                    print(f"  • {epic.id}: {epic.title} [{epic.status}]")
                else:
                    print(f"  ⚠️  {epic_id}: (not found)")
        else:
            print("  (no EPICs)")

        # Tickets
        print(f"\nTickets ({len(sprint.tickets)}):")
        if sprint.tickets:
            from scripts.mission_control.models.ticket import Ticket

            state_counts = {}
            for ticket_id in sprint.tickets:
                ticket = Ticket.get(ticket_id)
                if ticket:
                    state = ticket.state
                    state_counts[state] = state_counts.get(state, 0) + 1
                    state_icon = "✅" if state == "DONE" else "🔄" if state == "RUNNING" else "⬜"
                    print(f"  {state_icon} {ticket.id}: {ticket.title[:40]} [{state}]")
            print(f"\n  Summary: {state_counts}")
        else:
            print("  (no tickets)")

        print(f"{'─'*60}")
        print(f"Created:     {sprint.created_at or '-'}")
        print(f"Updated:     {sprint.updated_at or '-'}")
        print(f"{'='*60}\n")
        return 0
    except Exception as e:
        print(f"❌ Error showing sprint: {e}")
        return 1


def _sprint_update(args: argparse.Namespace) -> int:
    """Update a sprint."""
    try:
        sprint = Sprint.get(args.sprint_id)
        if not sprint:
            print(f"❌ Sprint not found: {args.sprint_id}")
            return 1

        updated = False

        if args.status:
            sprint.status = args.status
            print(f"   Status: {args.status}")
            updated = True

        if args.title:
            sprint.title = args.title
            print(f"   Title: {args.title}")
            updated = True

        if args.budget:
            sprint.llm_budget.total_tokens = args.budget
            print(f"   LLM Budget: {args.budget:,} tokens")
            updated = True

        if updated:
            sprint.save()
            print(f"✅ Updated sprint: {sprint.id}")
        else:
            print("No updates specified.")

        return 0
    except Exception as e:
        print(f"❌ Error updating sprint: {e}")
        return 1


def _sprint_add_ticket(args: argparse.Namespace) -> int:
    """Add a ticket to a sprint."""
    try:
        sprint = Sprint.get(args.sprint_id)
        if not sprint:
            print(f"❌ Sprint not found: {args.sprint_id}")
            return 1

        # Verify ticket exists
        from scripts.mission_control.models.ticket import Ticket

        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        # Add ticket to sprint
        sprint.add_ticket(args.ticket_id)
        sprint.save()

        # Update ticket's sprint_id
        ticket.sprint_id = args.sprint_id
        ticket.save()

        print(f"✅ Added {args.ticket_id} to {args.sprint_id}")
        return 0
    except Exception as e:
        print(f"❌ Error adding ticket: {e}")
        return 1


def _sprint_active(args: argparse.Namespace) -> int:
    """Show the active sprint."""
    try:
        sprint = Sprint.get_active()
        if not sprint:
            print("No active sprint found.")
            return 0

        print(f"\n🏃 Active Sprint: {sprint.id}")
        print(f"   {sprint.title}")
        print(f"   {sprint.start_date} → {sprint.end_date}")
        print(f"   Tickets: {len(sprint.tickets)}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
