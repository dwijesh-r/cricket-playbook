"""
Transition hooks for Mission Control workflow.

Hooks execute before and after state transitions to:
- Validate business rules
- Update related entities
- Trigger notifications
- Maintain audit trails
"""

import json
from datetime import datetime
from typing import Any, Callable, Optional

from scripts.mission_control import MISSION_CONTROL_ROOT


class HookRegistry:
    """Registry for workflow transition hooks."""

    _pre_hooks: dict[str, list[Callable]] = {}
    _post_hooks: dict[str, list[Callable]] = {}
    _global_pre_hooks: list[Callable] = []
    _global_post_hooks: list[Callable] = []

    @classmethod
    def register_pre(
        cls, from_state: Optional[str] = None, to_state: Optional[str] = None
    ) -> Callable:
        """
        Decorator to register a pre-transition hook.

        Args:
            from_state: Specific source state (None for all)
            to_state: Specific target state (None for all)
        """

        def decorator(func: Callable) -> Callable:
            if from_state is None and to_state is None:
                cls._global_pre_hooks.append(func)
            else:
                key = f"{from_state or '*'}:{to_state or '*'}"
                if key not in cls._pre_hooks:
                    cls._pre_hooks[key] = []
                cls._pre_hooks[key].append(func)
            return func

        return decorator

    @classmethod
    def register_post(
        cls, from_state: Optional[str] = None, to_state: Optional[str] = None
    ) -> Callable:
        """
        Decorator to register a post-transition hook.

        Args:
            from_state: Specific source state (None for all)
            to_state: Specific target state (None for all)
        """

        def decorator(func: Callable) -> Callable:
            if from_state is None and to_state is None:
                cls._global_post_hooks.append(func)
            else:
                key = f"{from_state or '*'}:{to_state or '*'}"
                if key not in cls._post_hooks:
                    cls._post_hooks[key] = []
                cls._post_hooks[key].append(func)
            return func

        return decorator

    @classmethod
    def get_pre_hooks(cls, from_state: str, to_state: str) -> list[Callable]:
        """Get all applicable pre-hooks for a transition."""
        hooks = list(cls._global_pre_hooks)

        # Check specific transition
        key = f"{from_state}:{to_state}"
        hooks.extend(cls._pre_hooks.get(key, []))

        # Check wildcard from_state
        key = f"*:{to_state}"
        hooks.extend(cls._pre_hooks.get(key, []))

        # Check wildcard to_state
        key = f"{from_state}:*"
        hooks.extend(cls._pre_hooks.get(key, []))

        return hooks

    @classmethod
    def get_post_hooks(cls, from_state: str, to_state: str) -> list[Callable]:
        """Get all applicable post-hooks for a transition."""
        hooks = list(cls._global_post_hooks)

        # Check specific transition
        key = f"{from_state}:{to_state}"
        hooks.extend(cls._post_hooks.get(key, []))

        # Check wildcard from_state
        key = f"*:{to_state}"
        hooks.extend(cls._post_hooks.get(key, []))

        # Check wildcard to_state
        key = f"{from_state}:*"
        hooks.extend(cls._post_hooks.get(key, []))

        return hooks

    @classmethod
    def clear_all(cls) -> None:
        """Clear all registered hooks (for testing)."""
        cls._pre_hooks.clear()
        cls._post_hooks.clear()
        cls._global_pre_hooks.clear()
        cls._global_post_hooks.clear()


# Convenience decorators
def pre_transition(from_state: Optional[str] = None, to_state: Optional[str] = None) -> Callable:
    """Decorator for pre-transition hooks."""
    return HookRegistry.register_pre(from_state, to_state)


def post_transition(from_state: Optional[str] = None, to_state: Optional[str] = None) -> Callable:
    """Decorator for post-transition hooks."""
    return HookRegistry.register_post(from_state, to_state)


# ============================================================================
# Built-in Hooks (Task Integrity Loop Compliance)
# ============================================================================


@post_transition()
def audit_log_transition(ticket: Any, from_state: str, to_state: str) -> None:
    """Log all state transitions to audit trail."""
    audit_file = MISSION_CONTROL_ROOT / "logs" / "audit.jsonl"
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "state_transition",
        "ticket_id": ticket.id,
        "from_state": from_state,
        "to_state": to_state,
        "assignee": ticket.assignee,
        "task_integrity_step": _get_integrity_step(to_state),
    }

    with open(audit_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


@post_transition(to_state="DONE")
def update_epic_progress(ticket: Any, from_state: str, to_state: str) -> None:
    """Update parent EPIC progress when ticket completes."""
    if not ticket.epic_id:
        return

    from scripts.mission_control.models.epic import Epic

    epic = Epic.get(ticket.epic_id)
    if epic:
        epic.calculate_progress()
        epic.save()


@post_transition(to_state="DONE")
def update_sprint_velocity(ticket: Any, from_state: str, to_state: str) -> None:
    """Update sprint velocity when ticket completes."""
    if not ticket.sprint_id:
        return

    from scripts.mission_control.models.sprint import Sprint

    sprint = Sprint.get(ticket.sprint_id)
    if sprint:
        # Increment completed points (assuming 1 point per ticket for now)
        sprint.velocity.completed_points += 1
        sprint.velocity.burndown.append(sprint.velocity.completed_points)
        sprint.save()


@post_transition(to_state="VALIDATION")
def notify_founder_validation(ticket: Any, from_state: str, to_state: str) -> None:
    """
    Notify that a ticket requires Founder validation.

    In a real system, this would send a notification.
    For now, we log it to the audit trail.
    """
    audit_file = MISSION_CONTROL_ROOT / "logs" / "audit.jsonl"
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "founder_validation_required",
        "ticket_id": ticket.id,
        "title": ticket.title,
        "message": f"Ticket {ticket.id} requires Founder validation (Task Integrity Step 6)",
    }

    with open(audit_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


@pre_transition(from_state="READY", to_state="RUNNING")
def check_llm_approval(ticket: Any, from_state: str, to_state: str) -> dict:
    """Check LLM approval before starting work that requires it."""
    result = {"llm_check": "not_required"}

    if ticket.llm_required:
        if ticket.llm_approved_by:
            result["llm_check"] = "approved"
            result["llm_approved_by"] = ticket.llm_approved_by
        else:
            result["llm_check"] = "pending"

    return result


@post_transition(from_state="RUNNING", to_state="BLOCKED")
def log_blocker(ticket: Any, from_state: str, to_state: str) -> None:
    """Log when a ticket becomes blocked."""
    audit_file = MISSION_CONTROL_ROOT / "logs" / "audit.jsonl"
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": "ticket_blocked",
        "ticket_id": ticket.id,
        "title": ticket.title,
        "assignee": ticket.assignee,
    }

    with open(audit_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _get_integrity_step(state: str) -> str:
    """Map state to Task Integrity Loop step."""
    mapping = {
        "IDEA": "Step 0: PRD Creation",
        "BACKLOG": "Step 1: Florentino Gate",
        "READY": "Sprint Assigned",
        "RUNNING": "Step 2: Build",
        "BLOCKED": "Blocked",
        "REVIEW": "Steps 3-5: Technical Gates",
        "VALIDATION": "Step 6: Founder Validation",
        "DONE": "Steps 7-8: Complete",
    }
    return mapping.get(state, "Unknown")
