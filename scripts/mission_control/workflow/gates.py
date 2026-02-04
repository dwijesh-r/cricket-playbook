"""
Gate validation for Task Integrity Loop compliance.

Implements the five gates required for work completion:
1. Florentino Gate (Product Owner approval)
2. Domain Sanity (Technical validators)
3. Enforcement Check (Governance review)
4. System Check (QA validation)
5. Founder Validation (Final approval)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
from enum import Enum
import json

from scripts.mission_control import MISSION_CONTROL_ROOT


class GateStatus(str, Enum):
    """Status values for gates."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    NOT_APPROVED = "NOT_APPROVED"
    ANALYTICS_ONLY = "ANALYTICS_ONLY"
    YES = "YES"
    NO = "NO"
    FIX = "FIX"
    PASS = "PASS"
    FAIL = "FAIL"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"


class GateError(Exception):
    """Raised when a gate operation fails."""

    def __init__(self, gate_name: str, message: str):
        self.gate_name = gate_name
        super().__init__(f"{gate_name}: {message}")


@dataclass
class GateResult:
    """Result of a gate approval operation."""

    gate_name: str
    status: str
    approved_by: Optional[str]
    timestamp: str
    reason: Optional[str] = None
    details: Optional[dict] = None


class GateValidator:
    """
    Validates and manages gates for Task Integrity Loop.

    Each gate corresponds to a step in the Task Integrity Loop:
    - florentino_gate: Step 1 - Product scope approval
    - domain_sanity: Step 3 - Technical domain validation
    - enforcement_check: Step 4 - Governance compliance
    - system_check: Step 5 - QA/testing validation
    - founder_validation: Step 6 - Final approval
    """

    # Role permissions for each gate
    GATE_PERMISSIONS = {
        "florentino_gate": ["founder", "product_owner"],
        "domain_sanity": ["founder", "validator"],
        "enforcement_check": ["founder", "architect"],
        "system_check": ["founder", "qa"],
        "founder_validation": ["founder"],  # Only Founder can approve
    }

    # Validators for domain sanity
    DOMAIN_VALIDATORS = ["jose_mourinho", "andy_flower", "pep_guardiola"]

    @classmethod
    def approve_florentino_gate(
        cls, ticket: Any, status: str, reason: str, approved_by: str
    ) -> GateResult:
        """
        Approve or reject at Florentino Gate (Step 1).

        Args:
            ticket: Ticket to approve
            status: APPROVED, NOT_APPROVED, or ANALYTICS_ONLY
            reason: Reason for decision
            approved_by: Who made the decision

        Returns:
            GateResult with details
        """
        if status not in [
            GateStatus.APPROVED.value,
            GateStatus.NOT_APPROVED.value,
            GateStatus.ANALYTICS_ONLY.value,
        ]:
            raise GateError(
                "florentino_gate",
                f"Invalid status: {status}. Use APPROVED, NOT_APPROVED, or ANALYTICS_ONLY",
            )

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Update ticket gates
        if not ticket.gates.florentino_gate:
            ticket.gates.florentino_gate = {}

        ticket.gates.florentino_gate = {
            "status": status,
            "reason": reason,
            "approved_by": approved_by,
            "date": timestamp[:10],
        }

        # Log to audit
        cls._log_gate_decision("florentino_gate", ticket, status, approved_by, reason)

        return GateResult(
            gate_name="florentino_gate",
            status=status,
            approved_by=approved_by,
            timestamp=timestamp,
            reason=reason,
        )

    @classmethod
    def approve_domain_sanity(
        cls, ticket: Any, validator: str, status: str, approved_by: str
    ) -> GateResult:
        """
        Record domain sanity approval from a validator (Step 3).

        Args:
            ticket: Ticket to validate
            validator: One of jose_mourinho, andy_flower, pep_guardiola
            status: YES, NO, or FIX
            approved_by: Who made the decision

        Returns:
            GateResult with details
        """
        if validator not in cls.DOMAIN_VALIDATORS:
            raise GateError(
                "domain_sanity",
                f"Invalid validator: {validator}. Use: {cls.DOMAIN_VALIDATORS}",
            )

        if status not in [
            GateStatus.YES.value,
            GateStatus.NO.value,
            GateStatus.FIX.value,
        ]:
            raise GateError("domain_sanity", f"Invalid status: {status}. Use YES, NO, or FIX")

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Update ticket gates
        if not ticket.gates.domain_sanity:
            ticket.gates.domain_sanity = {}

        ticket.gates.domain_sanity[validator] = status
        ticket.gates.domain_sanity["date"] = timestamp[:10]

        # Log to audit
        cls._log_gate_decision(
            "domain_sanity", ticket, status, approved_by, f"Validator: {validator}"
        )

        return GateResult(
            gate_name="domain_sanity",
            status=status,
            approved_by=approved_by,
            timestamp=timestamp,
            details={"validator": validator},
        )

    @classmethod
    def approve_enforcement_check(
        cls, ticket: Any, status: str, issues: list[str], approved_by: str
    ) -> GateResult:
        """
        Record enforcement check result (Step 4).

        Args:
            ticket: Ticket to check
            status: PASS or FAIL
            issues: List of issues found (if any)
            approved_by: Who performed the check

        Returns:
            GateResult with details
        """
        if status not in [GateStatus.PASS.value, GateStatus.FAIL.value]:
            raise GateError("enforcement_check", f"Invalid status: {status}. Use PASS or FAIL")

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Update ticket gates
        if not ticket.gates.enforcement_check:
            ticket.gates.enforcement_check = {}

        ticket.gates.enforcement_check = {
            "status": status,
            "issues": issues,
            "checked_by": approved_by,
            "date": timestamp[:10],
        }

        # Log to audit
        cls._log_gate_decision(
            "enforcement_check", ticket, status, approved_by, f"Issues: {len(issues)}"
        )

        return GateResult(
            gate_name="enforcement_check",
            status=status,
            approved_by=approved_by,
            timestamp=timestamp,
            details={"issues": issues},
        )

    @classmethod
    def approve_system_check(
        cls,
        ticket: Any,
        status: str,
        tests_passed: int,
        tests_total: int,
        approved_by: str,
    ) -> GateResult:
        """
        Record system check result (Step 5).

        Args:
            ticket: Ticket to check
            status: PASS or FAIL
            tests_passed: Number of tests passed
            tests_total: Total number of tests
            approved_by: Who performed the check

        Returns:
            GateResult with details
        """
        if status not in [GateStatus.PASS.value, GateStatus.FAIL.value]:
            raise GateError("system_check", f"Invalid status: {status}. Use PASS or FAIL")

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Update ticket gates
        if not ticket.gates.system_check:
            ticket.gates.system_check = {}

        ticket.gates.system_check = {
            "status": status,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "checked_by": approved_by,
            "date": timestamp[:10],
        }

        # Log to audit
        cls._log_gate_decision(
            "system_check",
            ticket,
            status,
            approved_by,
            f"Tests: {tests_passed}/{tests_total}",
        )

        return GateResult(
            gate_name="system_check",
            status=status,
            approved_by=approved_by,
            timestamp=timestamp,
            details={"tests_passed": tests_passed, "tests_total": tests_total},
        )

    @classmethod
    def approve_founder_validation(
        cls, ticket: Any, status: str, feedback: str, approved_by: str = "Founder"
    ) -> GateResult:
        """
        Record Founder validation (Step 6 - FINAL GATE).

        This is the most critical gate - only the Founder can approve.

        Args:
            ticket: Ticket to validate
            status: APPROVED or CHANGES_REQUESTED
            feedback: Founder feedback
            approved_by: Must be "Founder"

        Returns:
            GateResult with details
        """
        if status not in [
            GateStatus.APPROVED.value,
            GateStatus.CHANGES_REQUESTED.value,
        ]:
            raise GateError(
                "founder_validation",
                f"Invalid status: {status}. Use APPROVED or CHANGES_REQUESTED",
            )

        # Enforce Founder-only
        if approved_by != "Founder":
            raise GateError("founder_validation", "Only the Founder can perform final validation")

        timestamp = datetime.utcnow().isoformat() + "Z"

        # Update ticket gates
        if not ticket.gates.founder_validation:
            ticket.gates.founder_validation = {}

        ticket.gates.founder_validation = {
            "status": status,
            "feedback": feedback,
            "validated_by": "Founder",
            "date": timestamp[:10],
        }

        # Log to audit
        cls._log_gate_decision("founder_validation", ticket, status, "Founder", feedback)

        return GateResult(
            gate_name="founder_validation",
            status=status,
            approved_by="Founder",
            timestamp=timestamp,
            reason=feedback,
        )

    @classmethod
    def get_gate_summary(cls, ticket: Any) -> dict:
        """
        Get summary of all gates for a ticket.

        Returns:
            Dict with gate statuses and Task Integrity Loop compliance
        """
        gates = ticket.gates

        # Check each gate
        fg = gates.florentino_gate or {}
        ds = gates.domain_sanity or {}
        ec = gates.enforcement_check or {}
        sc = gates.system_check or {}
        fv = gates.founder_validation or {}

        # Domain sanity requires at least one YES
        ds_approvals = [ds.get(v) for v in cls.DOMAIN_VALIDATORS if ds.get(v) == "YES"]

        return {
            "florentino_gate": {
                "status": fg.get("status", "PENDING"),
                "passed": fg.get("status") in ["APPROVED", "ANALYTICS_ONLY"],
            },
            "domain_sanity": {
                "status": "PASS" if ds_approvals else "PENDING",
                "approvals": len(ds_approvals),
                "validators": {v: ds.get(v, "PENDING") for v in cls.DOMAIN_VALIDATORS},
            },
            "enforcement_check": {
                "status": ec.get("status", "PENDING"),
                "passed": ec.get("status") == "PASS",
            },
            "system_check": {
                "status": sc.get("status", "PENDING"),
                "passed": sc.get("status") == "PASS",
                "tests": f"{sc.get('tests_passed', 0)}/{sc.get('tests_total', 0)}",
            },
            "founder_validation": {
                "status": fv.get("status", "PENDING"),
                "passed": fv.get("status") == "APPROVED",
            },
            "task_integrity_complete": all(
                [
                    fg.get("status") in ["APPROVED", "ANALYTICS_ONLY"],
                    len(ds_approvals) > 0,
                    ec.get("status") == "PASS",
                    sc.get("status") == "PASS",
                    fv.get("status") == "APPROVED",
                ]
            ),
        }

    @classmethod
    def _log_gate_decision(
        cls, gate_name: str, ticket: Any, status: str, approved_by: str, details: str
    ) -> None:
        """Log gate decision to audit trail."""
        audit_file = MISSION_CONTROL_ROOT / "logs" / "audit.jsonl"
        audit_file.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "gate_decision",
            "gate": gate_name,
            "ticket_id": ticket.id,
            "status": status,
            "approved_by": approved_by,
            "details": details,
        }

        with open(audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
