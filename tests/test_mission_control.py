"""
Tests for Mission Control - Task management for Cricket Playbook agents.

Run with: pytest tests/test_mission_control.py -v
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Override MISSION_CONTROL_ROOT for testing
import scripts.mission_control as mc_module
import scripts.mission_control.storage.json_store as json_store_module


@pytest.fixture(scope="function")
def temp_mission_control(tmp_path):
    """Create a temporary Mission Control directory for testing."""
    # Create temp structure
    mc_root = tmp_path / ".mission-control"
    (mc_root / "config" / "schemas").mkdir(parents=True)
    (mc_root / "data" / "tickets").mkdir(parents=True)
    (mc_root / "data" / "epics").mkdir(parents=True)
    (mc_root / "data" / "sprints").mkdir(parents=True)
    (mc_root / "data" / "agents").mkdir(parents=True)
    (mc_root / "indexes").mkdir(parents=True)
    (mc_root / "views").mkdir(parents=True)
    (mc_root / "logs").mkdir(parents=True)

    # Copy schemas from actual location
    real_schemas = project_root / ".mission-control" / "config" / "schemas"
    if real_schemas.exists():
        for schema_file in real_schemas.glob("*.json"):
            shutil.copy(schema_file, mc_root / "config" / "schemas")

    # Override the module root in both places where it's imported
    original_root = mc_module.MISSION_CONTROL_ROOT
    original_json_store_root = json_store_module.MISSION_CONTROL_ROOT
    mc_module.MISSION_CONTROL_ROOT = mc_root
    json_store_module.MISSION_CONTROL_ROOT = mc_root

    yield mc_root

    # Restore originals
    mc_module.MISSION_CONTROL_ROOT = original_root
    json_store_module.MISSION_CONTROL_ROOT = original_json_store_root


class TestIdGenerator:
    """Tests for ID generation."""

    def test_generate_ticket_id(self, temp_mission_control):
        """Test generating ticket IDs."""
        from scripts.mission_control.utils.id_generator import IdGenerator

        # First ticket should be TKT-001
        ticket_id = IdGenerator.generate("ticket", temp_mission_control / "data" / "tickets")
        assert ticket_id == "TKT-001"

    def test_generate_epic_id(self, temp_mission_control):
        """Test generating EPIC IDs."""
        from scripts.mission_control.utils.id_generator import IdGenerator

        epic_id = IdGenerator.generate("epic", temp_mission_control / "data" / "epics")
        assert epic_id == "EPIC-001"

    def test_generate_sprint_id(self, temp_mission_control):
        """Test generating sprint IDs."""
        from scripts.mission_control.utils.id_generator import IdGenerator

        sprint_id = IdGenerator.generate("sprint", temp_mission_control / "data" / "sprints")
        assert sprint_id == "SPRINT-001"

    def test_validate_ticket_id(self):
        """Test ticket ID validation."""
        from scripts.mission_control.utils.id_generator import IdGenerator

        assert IdGenerator.validate("TKT-001", "ticket") is True
        assert IdGenerator.validate("TKT-999", "ticket") is True
        assert IdGenerator.validate("EPIC-001", "ticket") is False
        assert IdGenerator.validate("invalid", "ticket") is False

    def test_parse_id(self):
        """Test ID parsing."""
        from scripts.mission_control.utils.id_generator import IdGenerator

        prefix, num = IdGenerator.parse("TKT-042")
        assert prefix == "TKT"
        assert num == 42


class TestSchemaValidator:
    """Tests for schema validation."""

    def test_validate_valid_ticket(self, temp_mission_control):
        """Test validating a valid ticket."""
        from scripts.mission_control.utils.schema_validator import SchemaValidator

        valid_ticket = {
            "id": "TKT-001",
            "title": "Test ticket",
            "state": "IDEA",
            "priority": "P2",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }

        is_valid, errors = SchemaValidator.validate(valid_ticket, "ticket")
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_state(self, temp_mission_control):
        """Test validating a ticket with invalid state."""
        from scripts.mission_control.utils.schema_validator import SchemaValidator

        invalid_ticket = {
            "id": "TKT-001",
            "title": "Test ticket",
            "state": "INVALID_STATE",
            "priority": "P2",
        }

        is_valid, errors = SchemaValidator.validate(invalid_ticket, "ticket")
        assert is_valid is False

    def test_validate_missing_required(self, temp_mission_control):
        """Test validating a ticket with missing required fields."""
        from scripts.mission_control.utils.schema_validator import SchemaValidator

        invalid_ticket = {
            "id": "TKT-001"
            # Missing title, state, priority
        }

        is_valid, errors = SchemaValidator.validate(invalid_ticket, "ticket")
        assert is_valid is False

    def test_get_valid_states(self):
        """Test getting valid states."""
        from scripts.mission_control.utils.schema_validator import SchemaValidator

        states = SchemaValidator.get_valid_states()
        assert "IDEA" in states
        assert "DONE" in states
        assert "VALIDATION" in states
        assert len(states) == 8


class TestJsonStore:
    """Tests for JSON storage layer."""

    def test_create_and_read(self, temp_mission_control):
        """Test creating and reading an entity."""
        from scripts.mission_control.storage.json_store import JsonStore

        store = JsonStore("tickets")
        store.data_dir = temp_mission_control / "data" / "tickets"
        store.indexes_dir = temp_mission_control / "indexes"

        data = {
            "id": "TKT-001",
            "title": "Test ticket",
            "state": "IDEA",
            "priority": "P2",
        }

        created = store.create("TKT-001", data)
        assert created["id"] == "TKT-001"
        assert "created_at" in created

        # Read back
        retrieved = store.read("TKT-001")
        assert retrieved["title"] == "Test ticket"

    def test_update(self, temp_mission_control):
        """Test updating an entity."""
        from scripts.mission_control.storage.json_store import JsonStore

        store = JsonStore("tickets")
        store.data_dir = temp_mission_control / "data" / "tickets"
        store.indexes_dir = temp_mission_control / "indexes"

        data = {"id": "TKT-001", "title": "Original", "state": "IDEA", "priority": "P2"}
        store.create("TKT-001", data)

        # Update
        data["title"] = "Updated"
        data["state"] = "RUNNING"
        updated = store.update("TKT-001", data)

        assert updated["title"] == "Updated"
        assert updated["state"] == "RUNNING"

    def test_delete(self, temp_mission_control):
        """Test deleting an entity."""
        from scripts.mission_control.storage.json_store import JsonStore

        store = JsonStore("tickets")
        store.data_dir = temp_mission_control / "data" / "tickets"
        store.indexes_dir = temp_mission_control / "indexes"

        data = {
            "id": "TKT-001",
            "title": "Delete me",
            "state": "IDEA",
            "priority": "P2",
        }
        store.create("TKT-001", data)

        assert store.delete("TKT-001") is True
        assert store.read("TKT-001") is None

    def test_list_all(self, temp_mission_control):
        """Test listing all entities."""
        from scripts.mission_control.storage.json_store import JsonStore

        store = JsonStore("tickets")
        store.data_dir = temp_mission_control / "data" / "tickets"
        store.indexes_dir = temp_mission_control / "indexes"

        store.create(
            "TKT-001",
            {"id": "TKT-001", "title": "First", "state": "IDEA", "priority": "P0"},
        )
        store.create(
            "TKT-002",
            {"id": "TKT-002", "title": "Second", "state": "RUNNING", "priority": "P1"},
        )

        all_items = store.list_all()
        assert len(all_items) == 2

    def test_filter_by(self, temp_mission_control):
        """Test filtering entities."""
        from scripts.mission_control.storage.json_store import JsonStore

        store = JsonStore("tickets")
        store.data_dir = temp_mission_control / "data" / "tickets"
        store.indexes_dir = temp_mission_control / "indexes"

        store.create(
            "TKT-001",
            {"id": "TKT-001", "title": "First", "state": "IDEA", "priority": "P0"},
        )
        store.create(
            "TKT-002",
            {"id": "TKT-002", "title": "Second", "state": "RUNNING", "priority": "P1"},
        )
        store.create(
            "TKT-003",
            {"id": "TKT-003", "title": "Third", "state": "RUNNING", "priority": "P0"},
        )

        running = store.filter_by(state="RUNNING")
        assert len(running) == 2

        p0 = store.filter_by(priority="P0")
        assert len(p0) == 2


class TestTicketModel:
    """Tests for Ticket model."""

    def test_create_ticket(self, temp_mission_control):
        """Test creating a ticket."""
        from scripts.mission_control.models.ticket import Ticket

        # Reset store path
        Ticket._store.data_dir = temp_mission_control / "data" / "tickets"
        Ticket._store.indexes_dir = temp_mission_control / "indexes"

        ticket = Ticket.create(title="Test Ticket", priority="P0")

        assert ticket.id.startswith("TKT-")
        assert ticket.title == "Test Ticket"
        assert ticket.priority == "P0"
        assert ticket.state == "IDEA"

    def test_ticket_transition(self, temp_mission_control):
        """Test ticket state transitions with proper workflow."""
        from scripts.mission_control.models.ticket import Ticket

        Ticket._store.data_dir = temp_mission_control / "data" / "tickets"
        Ticket._store.indexes_dir = temp_mission_control / "indexes"

        ticket = Ticket.create(title="Transition Test", priority="P1")
        assert ticket.state == "IDEA"

        # Approve through Florentino Gate (required before BACKLOG)
        # Gates is a dataclass with attribute access, not dict
        ticket.gates.florentino_gate = {"status": "APPROVED", "approved_at": "2026-01-01"}
        ticket.transition_to("BACKLOG")
        assert ticket.state == "BACKLOG"

        # Assign to sprint (required before READY)
        ticket.sprint_id = "SPRINT-001"
        ticket.transition_to("READY")
        assert ticket.state == "READY"

        ticket.transition_to("RUNNING")
        assert ticket.state == "RUNNING"

    def test_ticket_to_dict(self, temp_mission_control):
        """Test ticket serialization."""
        from scripts.mission_control.models.ticket import Ticket

        Ticket._store.data_dir = temp_mission_control / "data" / "tickets"
        Ticket._store.indexes_dir = temp_mission_control / "indexes"

        ticket = Ticket(id="TKT-001", title="Serialize Test", priority="P2", owner="Tom Brady")

        data = ticket.to_dict()
        assert data["id"] == "TKT-001"
        assert data["title"] == "Serialize Test"
        assert data["owner"] == "Tom Brady"

    def test_invalid_state_raises(self):
        """Test that invalid state raises ValueError."""
        from scripts.mission_control.models.ticket import Ticket

        with pytest.raises(ValueError):
            Ticket(id="TKT-001", title="Bad State", state="INVALID", priority="P2")

    def test_calculate_progress(self, temp_mission_control):
        """Test progress calculation from subtasks."""
        from scripts.mission_control.models.ticket import Ticket, Subtask

        Ticket._store.data_dir = temp_mission_control / "data" / "tickets"
        Ticket._store.indexes_dir = temp_mission_control / "indexes"

        ticket = Ticket(
            id="TKT-001",
            title="Progress Test",
            priority="P2",
            subtasks=[
                Subtask(id="ST-1", title="Task 1", status="done"),
                Subtask(id="ST-2", title="Task 2", status="done"),
                Subtask(id="ST-3", title="Task 3", status="pending"),
                Subtask(id="ST-4", title="Task 4", status="pending"),
            ],
        )

        progress = ticket.calculate_progress()
        assert progress == 50  # 2 out of 4 done


class TestEpicModel:
    """Tests for EPIC model."""

    def test_create_epic(self, temp_mission_control):
        """Test creating an EPIC."""
        from scripts.mission_control.models.epic import Epic

        Epic._store.data_dir = temp_mission_control / "data" / "epics"
        Epic._store.indexes_dir = temp_mission_control / "indexes"

        epic = Epic.create(title="Test Epic", owner="Tom Brady")

        assert epic.id.startswith("EPIC-")
        assert epic.title == "Test Epic"
        assert epic.owner == "Tom Brady"
        assert epic.status == "PLANNING"

    def test_add_ticket_to_epic(self, temp_mission_control):
        """Test adding tickets to an EPIC."""
        from scripts.mission_control.models.epic import Epic

        Epic._store.data_dir = temp_mission_control / "data" / "epics"
        Epic._store.indexes_dir = temp_mission_control / "indexes"

        epic = Epic(id="EPIC-001", title="Test Epic", owner="Tom Brady")
        epic.add_ticket("TKT-001")
        epic.add_ticket("TKT-002")

        assert "TKT-001" in epic.tickets
        assert "TKT-002" in epic.tickets
        assert len(epic.tickets) == 2


class TestSprintModel:
    """Tests for Sprint model."""

    def test_create_sprint(self, temp_mission_control):
        """Test creating a sprint."""
        from scripts.mission_control.models.sprint import Sprint

        Sprint._store.data_dir = temp_mission_control / "data" / "sprints"
        Sprint._store.indexes_dir = temp_mission_control / "indexes"

        sprint = Sprint.create(title="Sprint 4", start_date="2026-01-31", end_date="2026-02-14")

        assert sprint.id.startswith("SPRINT-")
        assert sprint.title == "Sprint 4"
        assert sprint.status == "PLANNING"

    def test_llm_budget(self, temp_mission_control):
        """Test LLM budget tracking."""
        from scripts.mission_control.models.sprint import Sprint, LLMBudget

        Sprint._store.data_dir = temp_mission_control / "data" / "sprints"
        Sprint._store.indexes_dir = temp_mission_control / "indexes"

        sprint = Sprint(
            id="SPRINT-001",
            title="Test Sprint",
            start_date="2026-01-31",
            end_date="2026-02-14",
            llm_budget=LLMBudget(total_tokens=100000),
        )

        assert sprint.llm_budget.total_tokens == 100000
        assert sprint.llm_budget.used_tokens == 0
        assert sprint.llm_budget.remaining_tokens == 100000

        # Consume tokens
        assert sprint.consume_tokens(25000) is True
        assert sprint.llm_budget.used_tokens == 25000
        assert sprint.llm_budget.remaining_tokens == 75000

        # Try to exceed budget
        assert sprint.consume_tokens(100000) is False  # Would exceed

    def test_velocity_tracking(self):
        """Test velocity metrics."""
        from scripts.mission_control.models.sprint import Velocity

        velocity = Velocity(planned_points=100, completed_points=75)
        assert velocity.completion_pct == 75.0


class TestAuditLogging:
    """Tests for audit logging."""

    def test_audit_log_created(self, temp_mission_control):
        """Test that audit log entries are created."""
        from scripts.mission_control.storage.json_store import JsonStore

        store = JsonStore("tickets")
        store.data_dir = temp_mission_control / "data" / "tickets"
        store.indexes_dir = temp_mission_control / "indexes"

        # Create a ticket
        store.create(
            "TKT-001",
            {"id": "TKT-001", "title": "Audit Test", "state": "IDEA", "priority": "P2"},
        )

        # Check audit log
        audit_file = temp_mission_control / "logs" / "audit.jsonl"
        assert audit_file.exists()

        with open(audit_file) as f:
            lines = f.readlines()
            assert len(lines) >= 1

            entry = json.loads(lines[0])
            assert entry["action"] == "create"
            assert entry["entity_id"] == "TKT-001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
