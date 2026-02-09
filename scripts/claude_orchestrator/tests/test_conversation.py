"""Tests for conversation management."""

import pytest

from scripts.claude_orchestrator.core.conversation import (
    Conversation,
    ConversationManager,
)


@pytest.fixture
def tmp_conv_dir(tmp_path):
    """Temporary directory for conversation storage."""
    return tmp_path / "conversations"


@pytest.fixture
def manager(tmp_conv_dir):
    return ConversationManager(base_dir=tmp_conv_dir)


class TestConversation:
    """Test the Conversation dataclass."""

    def test_create_with_defaults(self):
        conv = Conversation(id="test1", agent_name="Tom Brady")
        assert conv.id == "test1"
        assert conv.agent_name == "Tom Brady"
        assert conv.messages == []
        assert conv.created_at

    def test_add_messages(self):
        conv = Conversation(id="test1", agent_name="Tom Brady")
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi there")

        assert len(conv.messages) == 2
        assert conv.messages[0] == {"role": "user", "content": "Hello"}
        assert conv.messages[1] == {"role": "assistant", "content": "Hi there"}

    def test_api_messages_no_truncation(self):
        conv = Conversation(id="test1", agent_name="Tom Brady")
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi")
        conv.add_user_message("How are you?")

        msgs = conv.get_api_messages()
        assert len(msgs) == 3

    def test_api_messages_truncation(self):
        conv = Conversation(id="test1", agent_name="Tom Brady")
        # Add many messages exceeding the limit
        for i in range(100):
            conv.add_user_message("x" * 5000)
            conv.add_assistant_message("y" * 5000)

        msgs = conv.get_api_messages(max_chars=20000)
        # Should be truncated
        assert len(msgs) < 200
        # Should start with user message
        assert msgs[0]["role"] == "user"

    def test_serialization_round_trip(self):
        conv = Conversation(
            id="test1",
            agent_name="Tom Brady",
            ticket_id="TKT-042",
        )
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi")

        data = conv.to_dict()
        restored = Conversation.from_dict(data)

        assert restored.id == conv.id
        assert restored.agent_name == conv.agent_name
        assert restored.ticket_id == conv.ticket_id
        assert len(restored.messages) == 2


class TestConversationManager:
    """Test conversation persistence."""

    def test_create_conversation(self, manager):
        conv = manager.create("Tom Brady")
        assert conv.agent_name == "Tom Brady"
        assert conv.id

    def test_save_and_load(self, manager):
        conv = manager.create("Tom Brady", ticket_id="TKT-001")
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi")
        manager.save(conv)

        loaded = manager.load("Tom Brady", conv.id)
        assert loaded is not None
        assert loaded.id == conv.id
        assert len(loaded.messages) == 2
        assert loaded.ticket_id == "TKT-001"

    def test_load_nonexistent(self, manager):
        result = manager.load("Tom Brady", "nonexistent")
        assert result is None

    def test_list_conversations(self, manager):
        conv1 = manager.create("Tom Brady")
        conv2 = manager.create("Tom Brady")

        convs = manager.list_conversations("Tom Brady")
        assert len(convs) == 2
        assert conv1.id in convs
        assert conv2.id in convs

    def test_list_empty(self, manager):
        convs = manager.list_conversations("Nobody")
        assert convs == []

    def test_agent_dir_sanitization(self, manager):
        conv = manager.create("N'Golo Kanté")
        manager.save(conv)

        # Should create a sanitized directory name
        loaded = manager.load("N'Golo Kanté", conv.id)
        assert loaded is not None
