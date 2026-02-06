"""
EPIC model for Mission Control.

Represents a collection of related tickets with progress tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from scripts.mission_control.storage.json_store import JsonStore
from scripts.mission_control.utils.id_generator import IdGenerator
from scripts.mission_control.utils.schema_validator import SchemaValidator

# Valid EPIC statuses
VALID_STATUSES = ["PLANNING", "ACTIVE", "COMPLETED", "ARCHIVED"]


@dataclass
class Epic:
    """A Mission Control EPIC representing a project or major feature."""

    id: str
    title: str
    owner: str
    description: Optional[str] = None
    sprint_id: Optional[str] = None
    tickets: list[str] = field(default_factory=list)
    progress_pct: int = 0
    status: str = "PLANNING"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    target_date: Optional[str] = None

    _store = JsonStore("epics")

    def __post_init__(self):
        """Validate after initialization."""
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}")

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = {
            "id": self.id,
            "title": self.title,
            "owner": self.owner,
            "tickets": self.tickets,
            "progress_pct": self.progress_pct,
            "status": self.status,
        }

        if self.description:
            data["description"] = self.description
        if self.sprint_id:
            data["sprint_id"] = self.sprint_id
        if self.created_at:
            data["created_at"] = self.created_at
        if self.updated_at:
            data["updated_at"] = self.updated_at
        if self.target_date:
            data["target_date"] = self.target_date

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Epic":
        """Create an Epic from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            owner=data["owner"],
            description=data.get("description"),
            sprint_id=data.get("sprint_id"),
            tickets=data.get("tickets", []),
            progress_pct=data.get("progress_pct", 0),
            status=data.get("status", "PLANNING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            target_date=data.get("target_date"),
        )

    def save(self) -> "Epic":
        """Save the epic to storage."""

        # Ensure timestamps are set for new epics
        now = datetime.utcnow().isoformat() + "Z"
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

        data = self.to_dict()

        # Validate before saving
        is_valid, errors = SchemaValidator.validate(data, "epic")
        if not is_valid:
            raise ValueError(f"Validation failed: {errors}")

        if self._store.read(self.id):
            self._store.update(self.id, data)
        else:
            self._store.create(self.id, data)

        return self

    def delete(self) -> bool:
        """Delete the epic from storage."""
        return self._store.delete(self.id)

    def add_ticket(self, ticket_id: str) -> "Epic":
        """Add a ticket to this epic."""
        if ticket_id not in self.tickets:
            self.tickets.append(ticket_id)
        return self

    def remove_ticket(self, ticket_id: str) -> "Epic":
        """Remove a ticket from this epic."""
        if ticket_id in self.tickets:
            self.tickets.remove(ticket_id)
        return self

    def calculate_progress(self) -> int:
        """
        Calculate progress based on ticket completion.

        Returns:
            Progress percentage
        """
        if not self.tickets:
            return 0

        # Import here to avoid circular import
        from scripts.mission_control.models.ticket import Ticket

        done_count = 0
        for ticket_id in self.tickets:
            ticket = Ticket.get(ticket_id)
            if ticket and ticket.state == "DONE":
                done_count += 1

        self.progress_pct = int((done_count / len(self.tickets)) * 100)
        return self.progress_pct

    @classmethod
    def create(cls, title: str, owner: str, **kwargs) -> "Epic":
        """
        Create and save a new epic.

        Args:
            title: Epic title
            owner: Epic owner
            **kwargs: Additional fields

        Returns:
            Created epic
        """
        epic_id = IdGenerator.generate("epic")
        epic = cls(id=epic_id, title=title, owner=owner, **kwargs)
        epic.save()
        return epic

    @classmethod
    def get(cls, epic_id: str) -> Optional["Epic"]:
        """
        Get an epic by ID.

        Args:
            epic_id: Epic identifier

        Returns:
            Epic or None if not found
        """
        data = cls._store.read(epic_id)
        if data:
            return cls.from_dict(data)
        return None

    @classmethod
    def list(
        cls,
        status: Optional[str] = None,
        owner: Optional[str] = None,
        sprint_id: Optional[str] = None,
    ) -> list["Epic"]:
        """
        List epics with optional filters.

        Args:
            status: Filter by status
            owner: Filter by owner
            sprint_id: Filter by sprint

        Returns:
            List of epics
        """
        filters = {}
        if status:
            filters["status"] = status
        if owner:
            filters["owner"] = owner
        if sprint_id:
            filters["sprint_id"] = sprint_id

        if filters:
            data_list = cls._store.filter_by(**filters)
        else:
            data_list = cls._store.list_all()

        return [cls.from_dict(d) for d in data_list]
