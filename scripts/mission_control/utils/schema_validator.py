"""
JSON Schema validation utilities for Mission Control.

Validates tickets, epics, and sprints against their JSON schemas.
"""

import json

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

from scripts.mission_control import MISSION_CONTROL_ROOT


class SchemaValidator:
    """Validates Mission Control entities against JSON schemas."""

    SCHEMA_FILES = {
        "ticket": "ticket.schema.json",
        "epic": "epic.schema.json",
        "sprint": "sprint.schema.json",
    }

    _schemas: dict = {}

    @classmethod
    def _load_schema(cls, entity_type: str) -> dict:
        """Load and cache a schema file."""
        if entity_type in cls._schemas:
            return cls._schemas[entity_type]

        if entity_type not in cls.SCHEMA_FILES:
            raise ValueError(f"Unknown entity type: {entity_type}")

        schema_path = MISSION_CONTROL_ROOT / "config" / "schemas" / cls.SCHEMA_FILES[entity_type]

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as f:
            schema = json.load(f)

        cls._schemas[entity_type] = schema
        return schema

    @classmethod
    def validate(cls, data: dict, entity_type: str) -> tuple[bool, list[str]]:
        """
        Validate data against a schema.

        Args:
            data: Data to validate
            entity_type: Type of entity ('ticket', 'epic', 'sprint')

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not HAS_JSONSCHEMA:
            # If jsonschema not installed, do basic validation
            return cls._basic_validate(data, entity_type)

        try:
            schema = cls._load_schema(entity_type)
            jsonschema.validate(instance=data, schema=schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e.message)]
        except jsonschema.SchemaError as e:
            return False, [f"Schema error: {e.message}"]

    @classmethod
    def _basic_validate(cls, data: dict, entity_type: str) -> tuple[bool, list[str]]:
        """
        Perform basic validation without jsonschema library.

        Checks required fields and basic type constraints.
        """
        errors = []

        if entity_type == "ticket":
            required = ["id", "title", "state", "priority"]
            valid_states = [
                "IDEA",
                "BACKLOG",
                "READY",
                "RUNNING",
                "BLOCKED",
                "REVIEW",
                "VALIDATION",
                "DONE",
            ]
            valid_priorities = ["P0", "P1", "P2", "P3"]

            for field in required:
                if field not in data:
                    errors.append(f"Missing required field: {field}")

            if "state" in data and data["state"] not in valid_states:
                errors.append(f"Invalid state: {data['state']}")

            if "priority" in data and data["priority"] not in valid_priorities:
                errors.append(f"Invalid priority: {data['priority']}")

        elif entity_type == "epic":
            required = ["id", "title", "owner"]
            for field in required:
                if field not in data:
                    errors.append(f"Missing required field: {field}")

        elif entity_type == "sprint":
            required = ["id", "title", "start_date", "end_date"]
            for field in required:
                if field not in data:
                    errors.append(f"Missing required field: {field}")

        return len(errors) == 0, errors

    @classmethod
    def get_required_fields(cls, entity_type: str) -> list[str]:
        """Get required fields for an entity type."""
        schema = cls._load_schema(entity_type)
        return schema.get("required", [])

    @classmethod
    def get_valid_states(cls) -> list[str]:
        """Get valid workflow states for tickets."""
        return [
            "IDEA",
            "BACKLOG",
            "READY",
            "RUNNING",
            "BLOCKED",
            "REVIEW",
            "VALIDATION",
            "DONE",
        ]

    @classmethod
    def get_valid_priorities(cls) -> list[str]:
        """Get valid priority levels."""
        return ["P0", "P1", "P2", "P3"]
