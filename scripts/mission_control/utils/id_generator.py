"""
ID generation utilities for Mission Control.

Generates unique, sequential IDs for tickets, epics, and sprints.
"""

from pathlib import Path

from scripts.mission_control import MISSION_CONTROL_ROOT


class IdGenerator:
    """Generates unique IDs for Mission Control entities."""

    PREFIXES = {"ticket": "TKT", "epic": "EPIC", "sprint": "SPRINT", "subtask": "ST"}

    @classmethod
    def generate(cls, entity_type: str, data_dir: Path = None) -> str:
        """
        Generate the next available ID for an entity type.

        Args:
            entity_type: One of 'ticket', 'epic', 'sprint', 'subtask'
            data_dir: Optional custom data directory

        Returns:
            Next available ID (e.g., 'TKT-001', 'EPIC-002')

        Raises:
            ValueError: If entity_type is invalid
        """
        if entity_type not in cls.PREFIXES:
            raise ValueError(
                f"Invalid entity type: {entity_type}. "
                f"Must be one of: {list(cls.PREFIXES.keys())}"
            )

        prefix = cls.PREFIXES[entity_type]

        # Map entity type to directory
        dir_map = {
            "ticket": "tickets",
            "epic": "epics",
            "sprint": "sprints",
            "subtask": "tickets",  # Subtasks are within tickets
        }

        if data_dir is None:
            data_dir = MISSION_CONTROL_ROOT / "data" / dir_map[entity_type]

        # Find existing IDs
        existing_ids = []
        if data_dir.exists():
            for f in data_dir.glob("*.json"):
                existing_ids.append(f.stem)

        # Extract numbers for this prefix
        numbers = []
        for eid in existing_ids:
            if eid.startswith(prefix):
                try:
                    num = int(eid.split("-")[1])
                    numbers.append(num)
                except (IndexError, ValueError):
                    continue

        # Generate next ID
        next_num = max(numbers) + 1 if numbers else 1
        return f"{prefix}-{next_num:03d}"

    @classmethod
    def validate(cls, entity_id: str, entity_type: str) -> bool:
        """
        Validate an entity ID format.

        Args:
            entity_id: ID to validate
            entity_type: Expected entity type

        Returns:
            True if valid, False otherwise
        """
        if entity_type not in cls.PREFIXES:
            return False

        prefix = cls.PREFIXES[entity_type]

        # Check format: PREFIX-NNN
        parts = entity_id.split("-")
        if len(parts) != 2:
            return False

        if parts[0] != prefix:
            return False

        try:
            int(parts[1])
            return True
        except ValueError:
            return False

    @classmethod
    def parse(cls, entity_id: str) -> tuple[str, int]:
        """
        Parse an entity ID into its components.

        Args:
            entity_id: ID to parse (e.g., 'TKT-001')

        Returns:
            Tuple of (prefix, number)

        Raises:
            ValueError: If ID format is invalid
        """
        parts = entity_id.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid ID format: {entity_id}")

        try:
            return parts[0], int(parts[1])
        except ValueError:
            raise ValueError(f"Invalid ID format: {entity_id}")
