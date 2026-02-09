"""
Central orchestration: dispatch, chat, and agent handoffs.

The Coordinator manages AgentClient instances, ConversationManager lifecycle,
and routes work to the correct agents.
"""

import subprocess
import sys
from typing import Optional

from scripts.claude_orchestrator.config.agent_parser import AgentConfig, get_agent
from scripts.claude_orchestrator.core.client import AgentClient
from scripts.claude_orchestrator.core.conversation import Conversation, ConversationManager
from scripts.claude_orchestrator.core.prompt_builder import build_system_prompt
from scripts.claude_orchestrator.core.token_tracker import TokenTracker


class Coordinator:
    """Central orchestration for multi-agent workflows."""

    def __init__(self):
        self._clients: dict[str, AgentClient] = {}
        self._conversations = ConversationManager()
        self._tracker = TokenTracker()

    def _get_client(self, agent_name: str) -> AgentClient:
        """Get or create an AgentClient for the named agent."""
        if agent_name not in self._clients:
            config = get_agent(agent_name)
            self._clients[agent_name] = AgentClient(config)
        return self._clients[agent_name]

    def _get_config(self, agent_name: str) -> AgentConfig:
        """Get agent config by name."""
        return get_agent(agent_name)

    def chat(
        self,
        agent_name: str,
        message: str,
        ticket_id: Optional[str] = None,
        conversation: Optional[Conversation] = None,
    ) -> tuple[str, Conversation]:
        """
        Send a message to an agent and get a response.

        Args:
            agent_name: Agent to chat with
            message: User message
            ticket_id: Optional ticket context
            conversation: Existing conversation to continue

        Returns:
            Tuple of (response text, conversation)
        """
        config = self._get_config(agent_name)
        client = self._get_client(agent_name)

        # Get or create conversation
        if conversation is None:
            conversation = self._conversations.create(agent_name, ticket_id)

        # Add user message
        conversation.add_user_message(message)

        # Build system prompt
        system = build_system_prompt(config, ticket_id=ticket_id)

        # Get API messages (with truncation)
        api_messages = conversation.get_api_messages()

        # Send to API
        result = client.send(api_messages, system=system)

        # Track tokens
        self._tracker.record(
            agent=agent_name,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            ticket_id=ticket_id,
            model=result.model,
        )

        # Add assistant response
        conversation.add_assistant_message(result.content)

        # Persist conversation
        self._conversations.save(conversation)

        return result.content, conversation

    def chat_stream(
        self,
        agent_name: str,
        message: str,
        ticket_id: Optional[str] = None,
        conversation: Optional[Conversation] = None,
    ):
        """
        Stream a response from an agent.

        Args:
            agent_name: Agent to chat with
            message: User message
            ticket_id: Optional ticket context
            conversation: Existing conversation to continue

        Yields:
            Text chunks as they arrive

        Returns via conversation reference:
            Updated conversation (caller should save)
        """
        config = self._get_config(agent_name)
        client = self._get_client(agent_name)

        if conversation is None:
            conversation = self._conversations.create(agent_name, ticket_id)

        conversation.add_user_message(message)
        system = build_system_prompt(config, ticket_id=ticket_id)
        api_messages = conversation.get_api_messages()

        full_response = []
        for chunk in client.stream(api_messages, system=system):
            full_response.append(chunk)
            yield chunk

        response_text = "".join(full_response)
        conversation.add_assistant_message(response_text)
        self._conversations.save(conversation)

    def dispatch(self, ticket_id: str) -> str:
        """
        Dispatch a ticket to its assigned agent.

        Looks up the ticket assignee via mc.py and sends the ticket
        context to that agent.

        Args:
            ticket_id: Ticket ID (e.g., "TKT-042")

        Returns:
            Agent's response
        """
        # Look up ticket via mc.py
        ticket_info = self._get_ticket_info(ticket_id)
        if not ticket_info:
            return f"Ticket {ticket_id} not found."

        assignee = ticket_info.get("assignee")
        if not assignee:
            return f"Ticket {ticket_id} has no assignee."

        title = ticket_info.get("title", "")
        state = ticket_info.get("state", "")
        description = ticket_info.get("description", "")

        # Build dispatch message
        message = (
            f"You have been assigned ticket {ticket_id}.\n\n"
            f"**Title:** {title}\n"
            f"**State:** {state}\n"
        )
        if description:
            message += f"\n**Description:**\n{description}\n"
        message += (
            "\nPlease analyze this ticket and provide your assessment, "
            "plan of action, and any concerns."
        )

        response, _ = self.chat(
            agent_name=assignee,
            message=message,
            ticket_id=ticket_id,
        )
        return response

    def handoff(
        self,
        from_agent: str,
        to_agent: str,
        context: str,
        ticket_id: Optional[str] = None,
    ) -> str:
        """
        Hand off work from one agent to another.

        Args:
            from_agent: Agent passing the work
            to_agent: Agent receiving the work
            context: Summary/output from from_agent
            ticket_id: Optional ticket context

        Returns:
            Response from to_agent
        """
        handoff_message = (
            f"**Handoff from {from_agent}:**\n\n"
            f"{context}\n\n"
            "Please review and provide your assessment."
        )

        response, _ = self.chat(
            agent_name=to_agent,
            message=handoff_message,
            ticket_id=ticket_id,
        )
        return response

    def _get_ticket_info(self, ticket_id: str) -> Optional[dict]:
        """Get ticket info via mc.py CLI."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "scripts.mission_control.mc",
                    "ticket",
                    "show",
                    ticket_id,
                    "--json",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                import json

                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, Exception):
            pass

        # Fallback: read ticket file directly
        from scripts.claude_orchestrator import MISSION_CONTROL_ROOT
        import json

        ticket_file = MISSION_CONTROL_ROOT / "data" / "tickets" / f"{ticket_id}.json"
        if ticket_file.exists():
            with open(ticket_file, "r") as f:
                return json.load(f)
        return None
