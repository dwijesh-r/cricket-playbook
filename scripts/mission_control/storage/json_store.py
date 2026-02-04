"""
JSON-based storage layer for Mission Control.

Handles CRUD operations for tickets, epics, and sprints using JSON files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from scripts.mission_control import MISSION_CONTROL_ROOT


class JsonStore:
    """JSON file-based storage for Mission Control entities."""

    def __init__(self, entity_type: str):
        """
        Initialize the store for a specific entity type.

        Args:
            entity_type: One of 'tickets', 'epics', 'sprints', 'agents'
        """
        self.entity_type = entity_type
        self.data_dir = MISSION_CONTROL_ROOT / "data" / entity_type
        self.indexes_dir = MISSION_CONTROL_ROOT / "indexes"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.indexes_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, entity_id: str) -> Path:
        """Get the file path for an entity."""
        return self.data_dir / f"{entity_id}.json"

    def create(self, entity_id: str, data: dict) -> dict:
        """
        Create a new entity.

        Args:
            entity_id: Unique identifier for the entity
            data: Entity data to store

        Returns:
            The created entity data

        Raises:
            FileExistsError: If entity already exists
        """
        file_path = self._get_file_path(entity_id)
        if file_path.exists():
            raise FileExistsError(f"Entity {entity_id} already exists")

        # Add timestamps
        now = datetime.utcnow().isoformat() + "Z"
        data["created_at"] = now
        data["updated_at"] = now

        self._write_json(file_path, data)
        self._log_audit("create", entity_id, data)
        return data

    def read(self, entity_id: str) -> Optional[dict]:
        """
        Read an entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Entity data or None if not found
        """
        file_path = self._get_file_path(entity_id)
        if not file_path.exists():
            return None
        return self._read_json(file_path)

    def update(self, entity_id: str, data: dict) -> dict:
        """
        Update an existing entity.

        Args:
            entity_id: Entity identifier
            data: Updated entity data

        Returns:
            The updated entity data

        Raises:
            FileNotFoundError: If entity doesn't exist
        """
        file_path = self._get_file_path(entity_id)
        if not file_path.exists():
            raise FileNotFoundError(f"Entity {entity_id} not found")

        # Preserve created_at, update updated_at
        existing = self._read_json(file_path)
        data["created_at"] = existing.get("created_at")
        data["updated_at"] = datetime.utcnow().isoformat() + "Z"

        self._write_json(file_path, data)
        self._log_audit("update", entity_id, data)
        return data

    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity identifier

        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_file_path(entity_id)
        if not file_path.exists():
            return False

        data = self._read_json(file_path)
        file_path.unlink()
        self._log_audit("delete", entity_id, data)
        return True

    def list_all(self) -> list[dict]:
        """
        List all entities of this type.

        Returns:
            List of all entity data
        """
        entities = []
        for file_path in sorted(self.data_dir.glob("*.json")):
            data = self._read_json(file_path)
            if data:
                entities.append(data)
        return entities

    def filter_by(self, **kwargs) -> list[dict]:
        """
        Filter entities by field values.

        Args:
            **kwargs: Field names and values to filter by

        Returns:
            List of matching entities
        """
        all_entities = self.list_all()
        results = []
        for entity in all_entities:
            matches = True
            for key, value in kwargs.items():
                if entity.get(key) != value:
                    matches = False
                    break
            if matches:
                results.append(entity)
        return results

    def get_next_id(self, prefix: str) -> str:
        """
        Get the next available ID for an entity type.

        Args:
            prefix: ID prefix (e.g., 'TKT', 'EPIC', 'SPRINT')

        Returns:
            Next available ID
        """
        existing_ids = [f.stem for f in self.data_dir.glob("*.json")]
        if not existing_ids:
            return f"{prefix}-001"

        # Extract numbers and find max
        numbers = []
        for eid in existing_ids:
            try:
                num = int(eid.split("-")[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue

        next_num = max(numbers) + 1 if numbers else 1
        return f"{prefix}-{next_num:03d}"

    def _read_json(self, file_path: Path) -> dict:
        """Read JSON from file."""
        with open(file_path, "r") as f:
            return json.load(f)

    def _write_json(self, file_path: Path, data: dict) -> None:
        """Write JSON to file with pretty formatting."""
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def _log_audit(self, action: str, entity_id: str, data: dict) -> None:
        """Log action to audit file."""
        audit_file = MISSION_CONTROL_ROOT / "logs" / "audit.jsonl"
        audit_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "entity_type": self.entity_type,
            "entity_id": entity_id,
            "data_summary": {
                "id": data.get("id"),
                "title": data.get("title"),
                "state": data.get("state"),
            },
        }

        with open(audit_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def rebuild_index(self, index_name: str, key_field: str) -> dict:
        """
        Rebuild an index by a specific field.

        Args:
            index_name: Name of the index (e.g., 'by_state')
            key_field: Field to index by

        Returns:
            The generated index
        """
        index = {}
        for entity in self.list_all():
            key_value = entity.get(key_field)
            if key_value:
                if key_value not in index:
                    index[key_value] = []
                index[key_value].append(entity.get("id"))

        index_file = self.indexes_dir / f"{index_name}.json"
        self._write_json(index_file, index)
        return index
