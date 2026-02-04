"""
Approve CLI commands for Mission Control gate management.

Implements the Task Integrity Loop gates:
- Florentino Gate (Step 1)
- Domain Sanity (Step 3)
- Enforcement Check (Step 4)
- System Check (Step 5)
- Founder Validation (Step 6)
"""

import argparse

from scripts.mission_control.models.ticket import Ticket
from scripts.mission_control.workflow.gates import GateValidator, GateError


def add_approve_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add approve commands to the argument parser."""
    approve_parser = subparsers.add_parser("approve", help="Gate approval commands")
    approve_subparsers = approve_parser.add_subparsers(
        dest="approve_action", help="Approval actions"
    )

    # approve florentino
    florentino_parser = approve_subparsers.add_parser(
        "florentino", help="Florentino Gate approval (Step 1)"
    )
    florentino_parser.add_argument("ticket_id", help="Ticket ID")
    florentino_parser.add_argument(
        "--status",
        "-s",
        choices=["APPROVED", "NOT_APPROVED", "ANALYTICS_ONLY"],
        required=True,
        help="Approval status",
    )
    florentino_parser.add_argument("--reason", "-r", required=True, help="Reason for decision")
    florentino_parser.add_argument("--by", "-b", default="Florentino Perez", help="Approved by")

    # approve domain-sanity
    domain_parser = approve_subparsers.add_parser(
        "domain-sanity", help="Domain Sanity check (Step 3)"
    )
    domain_parser.add_argument("ticket_id", help="Ticket ID")
    domain_parser.add_argument(
        "--validator",
        "-v",
        choices=["jose_mourinho", "andy_flower", "pep_guardiola"],
        required=True,
        help="Validator name",
    )
    domain_parser.add_argument(
        "--status",
        "-s",
        choices=["YES", "NO", "FIX"],
        required=True,
        help="Validation status",
    )
    domain_parser.add_argument("--by", "-b", help="Approved by (defaults to validator name)")

    # approve enforcement
    enforcement_parser = approve_subparsers.add_parser(
        "enforcement", help="Enforcement Check (Step 4)"
    )
    enforcement_parser.add_argument("ticket_id", help="Ticket ID")
    enforcement_parser.add_argument(
        "--status", "-s", choices=["PASS", "FAIL"], required=True, help="Check status"
    )
    enforcement_parser.add_argument("--issues", "-i", nargs="*", default=[], help="Issues found")
    enforcement_parser.add_argument("--by", "-b", default="Brad Stevens", help="Checked by")

    # approve system-check
    system_parser = approve_subparsers.add_parser("system-check", help="System Check / QA (Step 5)")
    system_parser.add_argument("ticket_id", help="Ticket ID")
    system_parser.add_argument(
        "--status", "-s", choices=["PASS", "FAIL"], required=True, help="Check status"
    )
    system_parser.add_argument(
        "--tests", "-t", required=True, help="Tests passed/total (e.g., 43/43)"
    )
    system_parser.add_argument("--by", "-b", default="N'Golo Kanté", help="Checked by")

    # approve founder (FINAL GATE)
    founder_parser = approve_subparsers.add_parser(
        "founder", help="Founder Validation (Step 6 - FINAL GATE)"
    )
    founder_parser.add_argument("ticket_id", help="Ticket ID")
    founder_parser.add_argument(
        "--status",
        "-s",
        choices=["APPROVED", "CHANGES_REQUESTED"],
        required=True,
        help="Validation status",
    )
    founder_parser.add_argument("--feedback", "-f", required=True, help="Founder feedback")

    # approve show - show gate status
    show_parser = approve_subparsers.add_parser("show", help="Show gate status for a ticket")
    show_parser.add_argument("ticket_id", help="Ticket ID")


def approve_group(args: argparse.Namespace) -> int:
    """Handle approve commands."""
    action = args.approve_action

    if action == "florentino":
        return _approve_florentino(args)
    elif action == "domain-sanity":
        return _approve_domain_sanity(args)
    elif action == "enforcement":
        return _approve_enforcement(args)
    elif action == "system-check":
        return _approve_system_check(args)
    elif action == "founder":
        return _approve_founder(args)
    elif action == "show":
        return _approve_show(args)
    else:
        print("Usage: mc approve <florentino|domain-sanity|enforcement|...")
        return 1


def _approve_florentino(args: argparse.Namespace) -> int:
    """Process Florentino Gate approval."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        result = GateValidator.approve_florentino_gate(
            ticket=ticket, status=args.status, reason=args.reason, approved_by=args.by
        )

        ticket.save()

        icon = (
            "✅"
            if result.status == "APPROVED"
            else "⚠️"
            if result.status == "ANALYTICS_ONLY"
            else "❌"
        )
        print(f"\n{icon} Florentino Gate: {result.status}")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   Reason: {args.reason}")
        print(f"   By: {args.by}")
        print("\n   📋 Task Integrity Loop: Step 1 Complete")

        # Auto-transition to BACKLOG if approved
        if result.status in ["APPROVED", "ANALYTICS_ONLY"] and ticket.state == "IDEA":
            ticket.transition_to("BACKLOG", validate_gates=False)
            ticket.save()
            print("   → Auto-transitioned to BACKLOG")

        return 0
    except GateError as e:
        print(f"❌ Gate Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _approve_domain_sanity(args: argparse.Namespace) -> int:
    """Process Domain Sanity check."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        approved_by = args.by or args.validator.replace("_", " ").title()

        result = GateValidator.approve_domain_sanity(
            ticket=ticket,
            validator=args.validator,
            status=args.status,
            approved_by=approved_by,
        )

        ticket.save()

        icon = "✅" if result.status == "YES" else "🔧" if result.status == "FIX" else "❌"
        validator_display = args.validator.replace("_", " ").title()

        print(f"\n{icon} Domain Sanity: {result.status}")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   Validator: {validator_display}")
        print(f"   By: {approved_by}")
        print(f"\n   📋 Task Integrity Loop: Step 3 ({validator_display})")

        return 0
    except GateError as e:
        print(f"❌ Gate Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _approve_enforcement(args: argparse.Namespace) -> int:
    """Process Enforcement Check."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        result = GateValidator.approve_enforcement_check(
            ticket=ticket, status=args.status, issues=args.issues, approved_by=args.by
        )

        ticket.save()

        icon = "✅" if result.status == "PASS" else "❌"

        print(f"\n{icon} Enforcement Check: {result.status}")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   By: {args.by}")
        if args.issues:
            print(f"   Issues: {', '.join(args.issues)}")
        print("\n   📋 Task Integrity Loop: Step 4 Complete")

        return 0
    except GateError as e:
        print(f"❌ Gate Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _approve_system_check(args: argparse.Namespace) -> int:
    """Process System Check."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        # Parse tests (e.g., "43/43")
        try:
            passed, total = map(int, args.tests.split("/"))
        except ValueError:
            print("❌ Invalid tests format. Use: --tests 43/43")
            return 1

        result = GateValidator.approve_system_check(
            ticket=ticket,
            status=args.status,
            tests_passed=passed,
            tests_total=total,
            approved_by=args.by,
        )

        ticket.save()

        icon = "✅" if result.status == "PASS" else "❌"

        print(f"\n{icon} System Check: {result.status}")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   Tests: {passed}/{total}")
        print(f"   By: {args.by}")
        print("\n   📋 Task Integrity Loop: Step 5 Complete")

        return 0
    except GateError as e:
        print(f"❌ Gate Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _approve_founder(args: argparse.Namespace) -> int:
    """Process Founder Validation (FINAL GATE)."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        result = GateValidator.approve_founder_validation(
            ticket=ticket,
            status=args.status,
            feedback=args.feedback,
            approved_by="Founder",
        )

        ticket.save()

        icon = "✅" if result.status == "APPROVED" else "🔄"

        print(f"\n{'='*60}")
        print(f"{icon} FOUNDER VALIDATION: {result.status}")
        print(f"{'='*60}")
        print(f"   Ticket: {args.ticket_id}")
        print(f"   Title: {ticket.title}")
        print(f"   Feedback: {args.feedback}")
        step6_status = "COMPLETE" if result.status == "APPROVED" else "Changes Requested"
        print(f"\n   📋 Task Integrity Loop: Step 6 {step6_status}")

        # Auto-transition based on result
        if result.status == "APPROVED" and ticket.state == "VALIDATION":
            ticket.transition_to("DONE", validate_gates=False)
            ticket.save()
            print("\n   🎉 Auto-transitioned to DONE")
            print("   📋 Task Integrity Loop: Steps 7-8 (Commit & Ship) - COMPLETE")
        elif result.status == "CHANGES_REQUESTED":
            ticket.transition_to("RUNNING", validate_gates=False)
            ticket.save()
            print("\n   🔄 Returned to RUNNING for changes")

        print(f"{'='*60}\n")
        return 0
    except GateError as e:
        print(f"❌ Gate Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def _approve_show(args: argparse.Namespace) -> int:
    """Show gate status for a ticket."""
    try:
        ticket = Ticket.get(args.ticket_id)
        if not ticket:
            print(f"❌ Ticket not found: {args.ticket_id}")
            return 1

        summary = GateValidator.get_gate_summary(ticket)

        print(f"\n{'='*60}")
        print(f"Gate Status: {ticket.id}")
        print(f"Title: {ticket.title}")
        print(f"Current State: {ticket.state}")
        print(f"{'='*60}")

        # Florentino Gate (Step 1)
        fg = summary["florentino_gate"]
        icon = "✅" if fg["passed"] else "⬜"
        print(f"\n{icon} Step 1: Florentino Gate")
        print(f"   Status: {fg['status']}")

        # Domain Sanity (Step 3)
        ds = summary["domain_sanity"]
        icon = "✅" if ds["status"] == "PASS" else "⬜"
        print(f"\n{icon} Step 3: Domain Sanity ({ds['approvals']}/3 approvals)")
        for validator, status in ds["validators"].items():
            v_icon = (
                "✅"
                if status == "YES"
                else "🔧"
                if status == "FIX"
                else "❌"
                if status == "NO"
                else "⬜"
            )
            print(f"   {v_icon} {validator.replace('_', ' ').title()}: {status}")

        # Enforcement Check (Step 4)
        ec = summary["enforcement_check"]
        icon = "✅" if ec["passed"] else "⬜"
        print(f"\n{icon} Step 4: Enforcement Check")
        print(f"   Status: {ec['status']}")

        # System Check (Step 5)
        sc = summary["system_check"]
        icon = "✅" if sc["passed"] else "⬜"
        print(f"\n{icon} Step 5: System Check")
        print(f"   Status: {sc['status']}")
        print(f"   Tests: {sc['tests']}")

        # Founder Validation (Step 6)
        fv = summary["founder_validation"]
        icon = "✅" if fv["passed"] else "⬜"
        print(f"\n{icon} Step 6: Founder Validation (FINAL)")
        print(f"   Status: {fv['status']}")

        # Overall status
        print(f"\n{'─'*60}")
        if summary["task_integrity_complete"]:
            print("🎉 TASK INTEGRITY LOOP: COMPLETE")
        else:
            print("📋 TASK INTEGRITY LOOP: In Progress")
        print(f"{'='*60}\n")

        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
