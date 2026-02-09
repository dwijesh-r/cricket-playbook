"""
Multi-turn conversation management for agent interactions.

Stores conversations as JSON in .mission-control/conversations/{agent}/{conv_id}.json.
Handles message history, truncation, and persistence.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from scripts.claude_orchestrator import CONVERSATIONS_DIR


@dataclass
class Conversation:
    """A multi-turn conversation with an agent."""

    id: str
    agent_name: str
    ticket_id: Optional[str] = None
    messages: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation."""
        self.messages.append({"role": "assistant", "content": content})
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def get_api_messages(self, max_chars: int = 320_000) -> list[dict]:
        """
        Get messages formatted for the API, with truncation if needed.

        Keeps the most recent messages that fit within ~80k tokens
        (estimated at 4 chars/token = 320k chars).

        Args:
            max_chars: Maximum total characters across all messages

        Returns:
            List of message dicts for the API
        """
        if not self.messages:
            return []

        # Calculate total character count
        total = sum(len(m["content"]) for m in self.messages)
        if total <= max_chars:
            return list(self.messages)

        # Truncate: keep most recent messages
        truncated = []
        running = 0
        for msg in reversed(self.messages):
            msg_len = len(msg["content"])
            if running + msg_len > max_chars:
                break
            truncated.insert(0, msg)
            running += msg_len

        # Ensure we start with a user message (API requirement)
        if truncated and truncated[0]["role"] != "user":
            truncated = truncated[1:]

        return truncated

    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage."""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "ticket_id": self.ticket_id,
            "messages": self.messages,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            agent_name=data["agent_name"],
            ticket_id=data.get("ticket_id"),
            messages=data.get("messages", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


class ConversationManager:
    """Manage conversation persistence."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or CONVERSATIONS_DIR

    def _get_agent_dir(self, agent_name: str) -> Path:
        """Get directory for an agent's conversations."""
        safe_name = agent_name.lower().replace(" ", "-").replace("'", "")
        agent_dir = self.base_dir / safe_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir

    def save(self, conversation: Conversation) -> Path:
        """Save a conversation to disk."""
        agent_dir = self._get_agent_dir(conversation.agent_name)
        filepath = agent_dir / f"{conversation.id}.json"
        with open(filepath, "w") as f:
            json.dump(conversation.to_dict(), f, indent=2)
            f.write("\n")
        return filepath

    def load(self, agent_name: str, conv_id: str) -> Optional[Conversation]:
        """Load a conversation by agent name and ID."""
        agent_dir = self._get_agent_dir(agent_name)
        filepath = agent_dir / f"{conv_id}.json"
        if not filepath.exists():
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return Conversation.from_dict(data)

    def list_conversations(self, agent_name: str) -> list[str]:
        """List all conversation IDs for an agent."""
        agent_dir = self._get_agent_dir(agent_name)
        if not agent_dir.exists():
            return []
        return sorted(f.stem for f in agent_dir.glob("*.json"))

    def create(
        self,
        agent_name: str,
        ticket_id: Optional[str] = None,
    ) -> Conversation:
        """Create and persist a new conversation."""
        conv = Conversation(
            id=str(uuid.uuid4())[:8],
            agent_name=agent_name,
            ticket_id=ticket_id,
        )
        self.save(conv)
        return conv
