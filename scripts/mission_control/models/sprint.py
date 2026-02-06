"""
Sprint model for Mission Control.

Represents a time-boxed iteration with ticket assignments and budget tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from scripts.mission_control.storage.json_store import JsonStore
from scripts.mission_control.utils.id_generator import IdGenerator
from scripts.mission_control.utils.schema_validator import SchemaValidator

# Valid sprint statuses
VALID_STATUSES = ["PLANNING", "ACTIVE", "COMPLETED", "CANCELLED"]


@dataclass
class LLMBudget:
    """LLM token budget for a sprint."""

    total_tokens: int = 100000
    used_tokens: int = 0
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = {"total_tokens": self.total_tokens, "used_tokens": self.used_tokens}
        if self.approved_by:
            data["approved_by"] = self.approved_by
        if self.approved_date:
            data["approved_date"] = self.approved_date
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "LLMBudget":
        """Create from dictionary."""
        return cls(
            total_tokens=data.get("total_tokens", 100000),
            used_tokens=data.get("used_tokens", 0),
            approved_by=data.get("approved_by"),
            approved_date=data.get("approved_date"),
        )

    @property
    def remaining_tokens(self) -> int:
        """Get remaining token budget."""
        return self.total_tokens - self.used_tokens

    @property
    def utilization_pct(self) -> float:
        """Get budget utilization percentage."""
        if self.total_tokens == 0:
            return 0.0
        return (self.used_tokens / self.total_tokens) * 100


@dataclass
class Velocity:
    """Sprint velocity metrics."""

    planned_points: int = 0
    completed_points: int = 0
    burndown: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "planned_points": self.planned_points,
            "completed_points": self.completed_points,
            "burndown": self.burndown,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Velocity":
        """Create from dictionary."""
        return cls(
            planned_points=data.get("planned_points", 0),
            completed_points=data.get("completed_points", 0),
            burndown=data.get("burndown", []),
        )

    @property
    def completion_pct(self) -> float:
        """Get velocity completion percentage."""
        if self.planned_points == 0:
            return 0.0
        return (self.completed_points / self.planned_points) * 100


@dataclass
class Sprint:
    """A Mission Control sprint representing a time-boxed iteration."""

    id: str
    title: str
    start_date: str
    end_date: str
    description: Optional[str] = None
    duration_weeks: int = 2
    epics: list[str] = field(default_factory=list)
    tickets: list[str] = field(default_factory=list)
    llm_budget: LLMBudget = field(default_factory=LLMBudget)
    velocity: Velocity = field(default_factory=Velocity)
    status: str = "PLANNING"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    _store = JsonStore("sprints")

    def __post_init__(self):
        """Validate after initialization."""
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = {
            "id": self.id,
            "title": self.title,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "duration_weeks": self.duration_weeks,
            "epics": self.epics,
            "tickets": self.tickets,
            "llm_budget": self.llm_budget.to_dict(),
            "velocity": self.velocity.to_dict(),
            "status": self.status,
        }

        if self.description:
            data["description"] = self.description
        if self.created_at:
            data["created_at"] = self.created_at
        if self.updated_at:
            data["updated_at"] = self.updated_at

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Sprint":
        """Create a Sprint from a dictionary."""
        llm_budget = LLMBudget.from_dict(data.get("llm_budget", {}))
        velocity = Velocity.from_dict(data.get("velocity", {}))

        return cls(
            id=data["id"],
            title=data["title"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            description=data.get("description"),
            duration_weeks=data.get("duration_weeks", 2),
            epics=data.get("epics", []),
            tickets=data.get("tickets", []),
            llm_budget=llm_budget,
            velocity=velocity,
            status=data.get("status", "PLANNING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def save(self) -> "Sprint":
        """Save the sprint to storage."""

        # Ensure timestamps are set for new sprints
        now = datetime.utcnow().isoformat() + "Z"
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

        data = self.to_dict()

        # Validate before saving
        is_valid, errors = SchemaValidator.validate(data, "sprint")
        if not is_valid:
            raise ValueError(f"Validation failed: {errors}")

        if self._store.read(self.id):
            self._store.update(self.id, data)
        else:
            self._store.create(self.id, data)

        return self

    def delete(self) -> bool:
        """Delete the sprint from storage."""
        return self._store.delete(self.id)

    def add_ticket(self, ticket_id: str) -> "Sprint":
        """Add a ticket to this sprint."""
        if ticket_id not in self.tickets:
            self.tickets.append(ticket_id)
        return self

    def add_epic(self, epic_id: str) -> "Sprint":
        """Add an epic to this sprint."""
        if epic_id not in self.epics:
            self.epics.append(epic_id)
        return self

    def remove_ticket(self, ticket_id: str) -> "Sprint":
        """Remove a ticket from this sprint."""
        if ticket_id in self.tickets:
            self.tickets.remove(ticket_id)
        return self

    def consume_tokens(self, tokens: int) -> bool:
        """
        Consume tokens from the LLM budget.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if budget available, False if exceeds budget
        """
        if self.llm_budget.used_tokens + tokens > self.llm_budget.total_tokens:
            return False
        self.llm_budget.used_tokens += tokens
        return True

    @classmethod
    def create(cls, title: str, start_date: str, end_date: str, **kwargs) -> "Sprint":
        """
        Create and save a new sprint.

        Args:
            title: Sprint title
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            **kwargs: Additional fields

        Returns:
            Created sprint
        """
        sprint_id = IdGenerator.generate("sprint")
        sprint = cls(
            id=sprint_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )
        sprint.save()
        return sprint

    @classmethod
    def get(cls, sprint_id: str) -> Optional["Sprint"]:
        """
        Get a sprint by ID.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Sprint or None if not found
        """
        data = cls._store.read(sprint_id)
        if data:
            return cls.from_dict(data)
        return None

    @classmethod
    def list(cls, status: Optional[str] = None) -> list["Sprint"]:
        """
        List sprints with optional filters.

        Args:
            status: Filter by status

        Returns:
            List of sprints
        """
        if status:
            data_list = cls._store.filter_by(status=status)
        else:
            data_list = cls._store.list_all()

        return [cls.from_dict(d) for d in data_list]

    @classmethod
    def get_active(cls) -> Optional["Sprint"]:
        """Get the currently active sprint."""
        active = cls.list(status="ACTIVE")
        return active[0] if active else None
