"""
LLM approval CLI commands for Mission Control.

Manages LLM usage approval and budget tracking for tickets and sprints.
"""

import argparse
from datetime import datetime

from scripts.mission_control.models.ticket import Ticket
from scripts.mission_control.models.sprint import Sprint
from scripts.mission_control import MISSION_CONTROL_ROOT
import json


def add_llm_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add LLM commands to the argument parser."""
    llm_parser = subparsers.add_parser("llm", help="LLM usage approval and tracking")
    llm_subparsers = llm_parser.add_subparsers(dest="llm_action", help="LLM actions")

    # llm approve - approve LLM usage for a ticket
    approve_parser = llm_subparsers.add_parser("approve", help="Approve LLM usage for a ticket")
    approve_parser.add_argument("ticket_id", help="Ticket ID")
    approve_parser.add_argument(
        "--tokens", "-t", type=int, required=True, help="Token budget to allocate"
    )
    approve_parser.add_argument("--by", "-b", default="Founder", help="Approved by")
    approve_parser.add_argument("--reason", "-r", help="Reason for LLM usage")

    # llm consume - record token consumption
    consume_parser = llm_subparsers.add_parser(
        "consume", help="Record token consumption for a ticket"
    )
    consume_parser.add_argument("ticket_id", help="Ticket ID")
    consume_parser.add_argument("--tokens", "-t", type=int, required=True, help="Tokens consumed")

    # llm budget - show/set sprint LLM budget
    budget_parser = llm_subparsers.add_parser("budget", help="Show or set sprint LLM budget")
    budget_parser.add_argument("--sprint", "-s", help="Sprint ID (default: active)")
    budget_parser.add_argument("--set", type=int, help="Set new total budget")
    budget_parser.add_argument("--approve-by", help="Who approved the budget")

    # llm status - show LLM usage status
    status_parser = llm_subparsers.add_parser("status", help="Show LLM usage status")
    status_parser.add_argument("--sprint", "-s", help="Sprint ID (default: active)")


def llm_group(args: argparse.Namespace) -> int:
    """Handle LLM commands."""
    action = args.llm_action

    if action == "approve":
        return _llm_approve(args)
    elif action == "consume":
        return _llm_consume(args)
    elif action == "budget":
        return _llm_budget(args)
    elif action == "status":
        return _llm_status(args)
    else:
        print("Usage: mc llm <approve|consume|budget|status>")
        return 1


def _llm_approve(args: argparse.Namespace) -> int:
    """Approve LLM usage for a ticket."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        # Update ticket
        ticket.llm_required = True
        ticket.llm_budget_tokens = args.tokens
        ticket.llm_approved_by = args.by

        ticket.save()

        # Log to audit
        _log_llm_action(
            "approve",
            args.ticket_id,
            {"tokens": args.tokens, "approved_by": args.by, "reason": args.reason},
        )

        print("\n✅ LLM Usage Approved")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   Budget: {args.tokens:,} tokens")
        print(f"   Approved by: {args.by}")
        if args.reason:
            print(f"   Reason: {args.reason}")
        print("\n   ⚠️  Work requiring LLM can now proceed")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _llm_consume(args: argparse.Namespace) -> int:
    """Record token consumption."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        if not ticket.llm_required:
            print(f"❌ Ticket {args.ticket_id} is not marked for LLM usage")
            return 1

        # Check if within budget
        if ticket.llm_budget_tokens and args.tokens > ticket.llm_budget_tokens:
            print(
                f"⚠️  Warning: Consumption ({args.tokens:,}) exceeds budget ({ticket.llm_budget_tokens:,})"
            )

        # Update sprint budget if ticket is in a sprint
        if ticket.sprint_id:
            sprint = Sprint.get(ticket.sprint_id)
            if sprint:
                if not sprint.consume_tokens(args.tokens):
                    print(
                        f"❌ Sprint budget exceeded! Remaining: {sprint.llm_budget.remaining_tokens:,}"
                    )
                    return 1
                sprint.save()

        # Log consumption
        _log_llm_action(
            "consume",
            args.ticket_id,
            {"tokens": args.tokens, "sprint_id": ticket.sprint_id},
        )

        print("\n📊 LLM Tokens Recorded")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   Consumed: {args.tokens:,} tokens")
        if ticket.sprint_id:
            sprint = Sprint.get(ticket.sprint_id)
            if sprint:
                print(
                    f"   Sprint Budget: {sprint.llm_budget.used_tokens:,}/{sprint.llm_budget.total_tokens:,}"
                )
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _llm_budget(args: argparse.Namespace) -> int:
    """Show or set sprint LLM budget."""
    try:
        if args.sprint:
            sprint = Sprint.get(args.sprint)
        else:
            sprint = Sprint.get_active()

        if not sprint:
            print("❌ No sprint found")
            return 1

        if args.set:
            # Update budget
            sprint.llm_budget.total_tokens = args.set
            if args.approve_by:
                sprint.llm_budget.approved_by = args.approve_by
                sprint.llm_budget.approved_date = datetime.utcnow().strftime("%Y-%m-%d")
            sprint.save()

            _log_llm_action(
                "budget_update",
                sprint.id,
                {"new_total": args.set, "approved_by": args.approve_by},
            )

            print("\n✅ LLM Budget Updated")
            print(f"   Sprint: {sprint.id}")
            print(f"   New Budget: {args.set:,} tokens")
            return 0

        # Show current budget
        budget = sprint.llm_budget

        print(f"\n{'=' * 50}")
        print(f"📊 LLM Budget: {sprint.id}")
        print(f"{'=' * 50}")
        print(f"   Total:     {budget.total_tokens:,} tokens")
        print(f"   Used:      {budget.used_tokens:,} tokens")
        print(f"   Remaining: {budget.remaining_tokens:,} tokens")
        print(f"   Usage:     {budget.utilization_pct:.1f}%")

        # Progress bar
        bar_width = 30
        filled = int(bar_width * budget.utilization_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"\n   [{bar}]")

        if budget.approved_by:
            print(f"\n   Approved by: {budget.approved_by}")
            print(f"   Approved on: {budget.approved_date}")
        print(f"{'=' * 50}\n")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _llm_status(args: argparse.Namespace) -> int:
    """Show LLM usage status."""
    try:
        if args.sprint:
            sprint = Sprint.get(args.sprint)
        else:
            sprint = Sprint.get_active()

        print(f"\n{'=' * 60}")
        print("📊 LLM USAGE STATUS")
        print(f"{'=' * 60}")

        if sprint:
            budget = sprint.llm_budget
            print(f"\n🏃 Sprint: {sprint.id}")
            print(
                f"   Budget: {budget.used_tokens:,}/{budget.total_tokens:,} ({budget.utilization_pct:.1f}%)"
            )

        # Show tickets with LLM approval
        all_tickets = Ticket.list()
        llm_tickets = [t for t in all_tickets if t.llm_required]

        if llm_tickets:
            print(f"\n📋 Tickets with LLM Approval ({len(llm_tickets)}):")
            print(f"   {'ID':<12} {'Budget':<12} {'Approved By':<20} {'State':<12}")
            print("   " + "-" * 56)

            for t in llm_tickets:
                budget_str = f"{t.llm_budget_tokens:,}" if t.llm_budget_tokens else "-"
                approved_by = t.llm_approved_by or "-"
                print(f"   {t.id:<12} {budget_str:<12} {approved_by:<20} {t.state:<12}")
        else:
            print("\n   No tickets with LLM approval")

        # Pending approval
        pending = [t for t in all_tickets if not t.llm_required and t.state == "READY"]
        if pending:
            print(f"\n⚠️  Tickets potentially needing LLM approval: {len(pending)}")

        print(f"{'=' * 60}\n")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _log_llm_action(action: str, entity_id: str, details: dict) -> None:
    """Log LLM action to audit trail."""
    audit_file = MISSION_CONTROL_ROOT / "logs" / "audit.jsonl"
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": f"llm_{action}",
        "entity_id": entity_id,
        "details": details,
    }

    with open(audit_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
