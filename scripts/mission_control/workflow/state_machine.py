"""
State Machine for Mission Control workflow.

Implements the 8-state workflow with Task Integrity Loop enforcement:
IDEA → BACKLOG → READY → RUNNING → BLOCKED → REVIEW → VALIDATION → DONE

Each transition is validated against:
1. Valid transition rules
2. Role permissions
3. Gate requirements (Task Integrity Loop)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable, Any
from enum import Enum


class State(str, Enum):
    """Workflow states aligned with Task Integrity Loop."""

    IDEA = "IDEA"  # Step 0: PRD Creation
    BACKLOG = "BACKLOG"  # Step 1: Florentino Gate approved
    READY = "READY"  # Assigned to sprint
    RUNNING = "RUNNING"  # Step 2: Build in progress
    BLOCKED = "BLOCKED"  # Dependency or issue
    REVIEW = "REVIEW"  # Steps 3-5: Domain Sanity, Enforcement, System Check
    VALIDATION = "VALIDATION"  # Step 6: Founder Validation
    DONE = "DONE"  # Steps 7-8: Commit, Ship, Post Task Note


class TransitionError(Exception):
    """Raised when a state transition is invalid."""

    def __init__(self, message: str, from_state: str, to_state: str, reason: Optional[str] = None):
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        super().__init__(message)


# Valid state transitions based on design spec
VALID_TRANSITIONS = {
    State.IDEA: [State.BACKLOG],  # Florentino approves
    State.BACKLOG: [State.READY],  # Sprint assigned
    State.READY: [State.RUNNING],  # Agent picks up
    State.RUNNING: [State.REVIEW, State.BLOCKED],  # Submit or blocked
    State.BLOCKED: [State.READY],  # Blocker resolved
    State.REVIEW: [State.VALIDATION, State.RUNNING],  # Gates pass or fix needed
    State.VALIDATION: [State.DONE, State.RUNNING],  # Founder approves or changes
    State.DONE: [],  # Terminal state
}

# Task Integrity Loop step mapping
TASK_INTEGRITY_STEPS = {
    State.IDEA: "Step 0: PRD Creation",
    State.BACKLOG: "Step 1: Florentino Gate",
    State.READY: "Sprint Assigned",
    State.RUNNING: "Step 2: Build",
    State.BLOCKED: "Blocked",
    State.REVIEW: "Steps 3-5: Domain Sanity, Enforcement, System Check",
    State.VALIDATION: "Step 6: Founder Validation",
    State.DONE: "Steps 7-8: Commit and Ship",
}


@dataclass
class TransitionResult:
    """Result of a state transition."""

    success: bool
    from_state: State
    to_state: State
    timestamp: str
    task_integrity_step: str
    gate_checks: dict
    message: str


class StateMachine:
    """
    State machine for Mission Control workflow.

    Enforces valid transitions and Task Integrity Loop compliance.
    """

    def __init__(self):
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []

    def can_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is valid."""
        try:
            from_s = State(from_state)
            to_s = State(to_state)
            return to_s in VALID_TRANSITIONS.get(from_s, [])
        except ValueError:
            return False

    def get_valid_transitions(self, current_state: str) -> list[str]:
        """Get list of valid next states from current state."""
        try:
            state = State(current_state)
            return [s.value for s in VALID_TRANSITIONS.get(state, [])]
        except ValueError:
            return []

    def validate_transition(self, ticket: "Any", to_state: str) -> tuple[bool, list[str]]:
        """
        Validate a transition against all rules.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        from_state = ticket.state

        # Check basic transition validity
        if not self.can_transition(from_state, to_state):
            errors.append(
                f"Invalid transition: {from_state} → {to_state}. "
                f"Valid targets: {self.get_valid_transitions(from_state)}"
            )
            return False, errors

        # Check gate requirements based on Task Integrity Loop
        gate_errors = self._check_gate_requirements(ticket, to_state)
        errors.extend(gate_errors)

        # Check LLM approval if required
        if to_state == State.RUNNING.value and ticket.llm_required:
            if not ticket.llm_approved_by:
                errors.append("LLM usage requires approval before starting work")

        return len(errors) == 0, errors

    def _check_gate_requirements(self, ticket: "Any", to_state: str) -> list[str]:
        """Check gate requirements for Task Integrity Loop compliance."""
        errors = []
        gates = ticket.gates

        # IDEA → BACKLOG: Requires Florentino Gate approval
        if ticket.state == State.IDEA.value and to_state == State.BACKLOG.value:
            fg = gates.florentino_gate
            if not fg or fg.get("status") not in ["APPROVED", "ANALYTICS_ONLY"]:
                errors.append(
                    "Task Integrity Loop: Florentino Gate approval required "
                    "(APPROVED or ANALYTICS_ONLY)"
                )

        # BACKLOG → READY: Requires sprint assignment
        if ticket.state == State.BACKLOG.value and to_state == State.READY.value:
            if not ticket.sprint_id:
                errors.append("Any must be assigned to a sprint before READY")

        # REVIEW → VALIDATION: All technical gates must pass
        if ticket.state == State.REVIEW.value and to_state == State.VALIDATION.value:
            # Check Domain Sanity (at least one validator)
            ds = gates.domain_sanity
            if ds:
                validators = ["jose_mourinho", "andy_flower", "pep_guardiola"]
                approvals = [ds.get(v) for v in validators if ds.get(v) in ["YES"]]
                if len(approvals) == 0:
                    errors.append(
                        "Task Integrity Loop: At least one Domain Sanity approval required"
                    )
            else:
                errors.append("Task Integrity Loop: Domain Sanity check not completed")

            # Check System Check
            sc = gates.system_check
            if not sc or sc.get("status") != "PASS":
                errors.append("Task Integrity Loop: System Check must PASS")

        # VALIDATION → DONE: Requires Founder validation
        if ticket.state == State.VALIDATION.value and to_state == State.DONE.value:
            fv = gates.founder_validation
            if not fv or fv.get("status") != "APPROVED":
                errors.append("Task Integrity Loop: Founder Validation required (Step 6)")

        return errors

    def transition(
        self,
        ticket: "Any",
        to_state: str,
        actor: Optional[str] = None,
        force: bool = False,
    ) -> TransitionResult:
        """
        Execute a state transition.

        Args:
            ticket: The ticket to transition
            to_state: Target state
            actor: Who is making the transition
            force: Override validation (Founder only)

        Returns:
            TransitionResult with details

        Raises:
            TransitionError: If transition is invalid and not forced
        """
        from_state = ticket.state
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Validate unless forced
        if not force:
            is_valid, errors = self.validate_transition(ticket, to_state)
            if not is_valid:
                raise TransitionError(
                    f"Cannot transition from {from_state} to {to_state}",
                    from_state=from_state,
                    to_state=to_state,
                    reason="; ".join(errors),
                )

        # Execute pre-transition hooks
        gate_checks = {}
        for hook in self._pre_hooks:
            result = hook(ticket, from_state, to_state)
            if result:
                gate_checks.update(result)

        # Perform the transition
        old_state = ticket.state
        ticket.state = to_state
        ticket.updated_at = timestamp

        # Handle terminal state
        if to_state == State.DONE.value:
            ticket.completed_at = timestamp
            ticket.progress_pct = 100

        # Execute post-transition hooks
        for hook in self._post_hooks:
            hook(ticket, old_state, to_state)

        # Get Task Integrity step info
        try:
            ti_step = TASK_INTEGRITY_STEPS.get(State(to_state), "Unknown")
        except ValueError:
            ti_step = "Unknown"

        return TransitionResult(
            success=True,
            from_state=State(from_state),
            to_state=State(to_state),
            timestamp=timestamp,
            task_integrity_step=ti_step,
            gate_checks=gate_checks,
            message=f"Transitioned {from_state} → {to_state}",
        )

    def register_pre_hook(self, hook: Callable) -> None:
        """Register a pre-transition hook."""
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable) -> None:
        """Register a post-transition hook."""
        self._post_hooks.append(hook)

    @staticmethod
    def get_task_integrity_status(ticket: "Any") -> dict:
        """
        Get Task Integrity Loop status for a ticket.

        Returns a dict showing which steps are complete.
        """
        gates = ticket.gates

        return {
            "step_0_prd_creation": ticket.state != State.IDEA.value,
            "step_1_florentino_gate": (
                gates.florentino_gate
                and gates.florentino_gate.get("status") in ["APPROVED", "ANALYTICS_ONLY"]
            ),
            "step_2_build": ticket.state
            in [
                State.RUNNING.value,
                State.REVIEW.value,
                State.VALIDATION.value,
                State.DONE.value,
            ],
            "step_3_domain_sanity": (
                gates.domain_sanity
                and any(
                    gates.domain_sanity.get(v) == "YES"
                    for v in ["jose_mourinho", "andy_flower", "pep_guardiola"]
                )
            ),
            "step_4_enforcement_check": (
                gates.enforcement_check and gates.enforcement_check.get("status") == "PASS"
            ),
            "step_5_system_check": (
                gates.system_check and gates.system_check.get("status") == "PASS"
            ),
            "step_6_founder_validation": (
                gates.founder_validation and gates.founder_validation.get("status") == "APPROVED"
            ),
            "step_7_commit_ship": ticket.state == State.DONE.value,
            "current_state": ticket.state,
            "current_step": TASK_INTEGRITY_STEPS.get(
                State(ticket.state) if ticket.state in [s.value for s in State] else None,
                "Unknown",
            ),
        }
