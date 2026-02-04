"""
Ticket model for Mission Control.

Represents a single unit of work with state management and gate tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from scripts.mission_control.storage.json_store import JsonStore
from scripts.mission_control.utils.id_generator import IdGenerator
from scripts.mission_control.utils.schema_validator import SchemaValidator


# Valid workflow states
VALID_STATES = [
    "IDEA",
    "BACKLOG",
    "READY",
    "RUNNING",
    "BLOCKED",
    "REVIEW",
    "VALIDATION",
    "DONE",
]
VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]


@dataclass
class Subtask:
    """A subtask within a ticket."""

    id: str
    title: str
    status: str = "pending"  # pending, in_progress, done
    assignee: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assignee": self.assignee,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Subtask":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            status=data.get("status", "pending"),
            assignee=data.get("assignee"),
        )


@dataclass
class Gates:
    """Gate statuses for a ticket."""

    florentino_gate: Optional[dict] = None
    domain_sanity: Optional[dict] = None
    enforcement_check: Optional[dict] = None
    system_check: Optional[dict] = None
    founder_validation: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        result = {}
        if self.florentino_gate:
            result["florentino_gate"] = self.florentino_gate
        if self.domain_sanity:
            result["domain_sanity"] = self.domain_sanity
        if self.enforcement_check:
            result["enforcement_check"] = self.enforcement_check
        if self.system_check:
            result["system_check"] = self.system_check
        if self.founder_validation:
            result["founder_validation"] = self.founder_validation
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Gates":
        """Create from dictionary."""
        return cls(
            florentino_gate=data.get("florentino_gate"),
            domain_sanity=data.get("domain_sanity"),
            enforcement_check=data.get("enforcement_check"),
            system_check=data.get("system_check"),
            founder_validation=data.get("founder_validation"),
        )


@dataclass
class Ticket:
    """A Mission Control ticket representing a unit of work."""

    id: str
    title: str
    state: str = "IDEA"
    priority: str = "P2"
    description: Optional[str] = None
    epic_id: Optional[str] = None
    owner: Optional[str] = None
    assignee: Optional[str] = None
    sprint_id: Optional[str] = None
    llm_required: bool = False
    llm_budget_tokens: Optional[int] = None
    llm_approved_by: Optional[str] = None
    subtasks: list[Subtask] = field(default_factory=list)
    gates: Gates = field(default_factory=Gates)
    progress_pct: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None

    _store = JsonStore("tickets")

    def __post_init__(self):
        """Validate after initialization."""
        if self.state not in VALID_STATES:
            raise ValueError(f"Invalid state: {self.state}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}")

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = {
            "id": self.id,
            "title": self.title,
            "state": self.state,
            "priority": self.priority,
            "progress_pct": self.progress_pct,
        }

        # Add optional fields if set
        if self.description:
            data["description"] = self.description
        if self.epic_id:
            data["epic_id"] = self.epic_id
        if self.owner:
            data["owner"] = self.owner
        if self.assignee:
            data["assignee"] = self.assignee
        if self.sprint_id:
            data["sprint_id"] = self.sprint_id
        if self.llm_required:
            data["llm_required"] = self.llm_required
        if self.llm_budget_tokens:
            data["llm_budget_tokens"] = self.llm_budget_tokens
        if self.llm_approved_by:
            data["llm_approved_by"] = self.llm_approved_by
        if self.subtasks:
            data["subtasks"] = [s.to_dict() for s in self.subtasks]
        if self.gates.to_dict():
            data["gates"] = self.gates.to_dict()
        if self.created_at:
            data["created_at"] = self.created_at
        if self.updated_at:
            data["updated_at"] = self.updated_at
        if self.completed_at:
            data["completed_at"] = self.completed_at

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        """Create a Ticket from a dictionary."""
        subtasks = [Subtask.from_dict(s) for s in data.get("subtasks", [])]
        gates = Gates.from_dict(data.get("gates", {}))

        return cls(
            id=data["id"],
            title=data["title"],
            state=data.get("state", "IDEA"),
            priority=data.get("priority", "P2"),
            description=data.get("description"),
            epic_id=data.get("epic_id"),
            owner=data.get("owner"),
            assignee=data.get("assignee"),
            sprint_id=data.get("sprint_id"),
            llm_required=data.get("llm_required", False),
            llm_budget_tokens=data.get("llm_budget_tokens"),
            llm_approved_by=data.get("llm_approved_by"),
            subtasks=subtasks,
            gates=gates,
            progress_pct=data.get("progress_pct", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
        )

    def save(self) -> "Ticket":
        """Save the ticket to storage."""
        # Ensure timestamps are set for new tickets
        now = datetime.utcnow().isoformat() + "Z"
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

        data = self.to_dict()

        # Validate before saving
        is_valid, errors = SchemaValidator.validate(data, "ticket")
        if not is_valid:
            raise ValueError(f"Validation failed: {errors}")

        if self._store.read(self.id):
            self._store.update(self.id, data)
        else:
            self._store.create(self.id, data)

        return self

    def delete(self) -> bool:
        """Delete the ticket from storage."""
        return self._store.delete(self.id)

    def transition_to(
        self, new_state: str, force: bool = False, validate_gates: bool = True
    ) -> "Ticket":
        """
        Transition to a new state with Task Integrity Loop validation.

        Args:
            new_state: Target state
            force: Override validation (Founder only)
            validate_gates: Whether to validate gate requirements

        Returns:
            Updated ticket

        Raises:
            ValueError: If transition is invalid
            TransitionError: If gate requirements not met
        """
        if new_state not in VALID_STATES:
            raise ValueError(f"Invalid state: {new_state}")

        if validate_gates:
            from scripts.mission_control.workflow.state_machine import StateMachine
            from scripts.mission_control.workflow.hooks import HookRegistry

            sm = StateMachine()

            # Run pre-transition hooks
            for hook in HookRegistry.get_pre_hooks(self.state, new_state):
                hook(self, self.state, new_state)

            # Validate and transition
            sm.transition(self, new_state, force=force)

            # Run post-transition hooks
            for hook in HookRegistry.get_post_hooks(self.state, new_state):
                hook(self, self.state, new_state)
        else:
            # Simple transition without validation (for basic updates)
            self.state = new_state

            # If completing, set completed_at
            if new_state == "DONE" and not self.completed_at:
                self.completed_at = datetime.utcnow().isoformat() + "Z"
                self.progress_pct = 100

        return self

    def get_task_integrity_status(self) -> dict:
        """Get Task Integrity Loop status for this ticket."""
        from scripts.mission_control.workflow.state_machine import StateMachine

        return StateMachine.get_task_integrity_status(self)

    def get_gate_summary(self) -> dict:
        """Get summary of all gate statuses."""
        from scripts.mission_control.workflow.gates import GateValidator

        return GateValidator.get_gate_summary(self)

    def calculate_progress(self) -> int:
        """Calculate progress based on subtasks."""
        if not self.subtasks:
            return self.progress_pct

        done_count = sum(1 for s in self.subtasks if s.status == "done")
        self.progress_pct = int((done_count / len(self.subtasks)) * 100)
        return self.progress_pct

    @classmethod
    def create(cls, title: str, priority: str = "P2", **kwargs) -> "Ticket":
        """
        Create and save a new ticket.

        Args:
            title: Ticket title
            priority: Priority level
            **kwargs: Additional fields

        Returns:
            Created ticket
        """
        ticket_id = IdGenerator.generate("ticket")
        ticket = cls(id=ticket_id, title=title, priority=priority, **kwargs)
        ticket.save()
        return ticket

    @classmethod
    def get(cls, ticket_id: str) -> Optional["Ticket"]:
        """
        Get a ticket by ID.

        Args:
            ticket_id: Ticket identifier

        Returns:
            Ticket or None if not found
        """
        data = cls._store.read(ticket_id)
        if data:
            return cls.from_dict(data)
        return None

    @classmethod
    def list(
        cls,
        state: Optional[str] = None,
        assignee: Optional[str] = None,
        sprint_id: Optional[str] = None,
    ) -> list["Ticket"]:
        """
        List tickets with optional filters.

        Args:
            state: Filter by state
            assignee: Filter by assignee
            sprint_id: Filter by sprint

        Returns:
            List of tickets
        """
        filters = {}
        if state:
            filters["state"] = state
        if assignee:
            filters["assignee"] = assignee
        if sprint_id:
            filters["sprint_id"] = sprint_id

        if filters:
            data_list = cls._store.filter_by(**filters)
        else:
            data_list = cls._store.list_all()

        return [cls.from_dict(d) for d in data_list]
