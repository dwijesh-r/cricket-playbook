"""
Anthropic SDK wrapper for per-agent API calls.

Each AgentClient is bound to a specific agent's model and temperature,
providing a clean interface for sending messages and streaming responses.
"""

import os
import time
from dataclasses import dataclass
from typing import Iterator, Optional

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]

from scripts.claude_orchestrator.config.agent_parser import AgentConfig
from scripts.claude_orchestrator.config.model_mapping import resolve


@dataclass
class MessageResult:
    """Result from an API call."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    stop_reason: str


class AgentClient:
    """Anthropic API client bound to a specific agent configuration."""

    def __init__(self, agent_config: AgentConfig, api_key: Optional[str] = None):
        """
        Initialize client for a specific agent.

        Args:
            agent_config: Parsed agent configuration
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        if anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env or environment.")

        self._client = anthropic.Anthropic(api_key=self._api_key)

        self.agent_config = agent_config
        self.model = resolve(agent_config.model)
        self.temperature = agent_config.temperature

    def send(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int = 4096,
    ) -> MessageResult:
        """
        Send a message to the API and return the result.

        Args:
            messages: List of message dicts (role, content)
            system: System prompt
            max_tokens: Maximum tokens in response

        Returns:
            MessageResult with content and usage
        """
        response = self._call_with_retry(
            messages=messages,
            system=system,
            max_tokens=max_tokens,
        )

        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        return MessageResult(
            content=content,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model=response.model,
            stop_reason=response.stop_reason,
        )

    def stream(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        """
        Stream a response from the API.

        Args:
            messages: List of message dicts (role, content)
            system: System prompt
            max_tokens: Maximum tokens in response

        Yields:
            Text chunks as they arrive
        """
        with self._client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def _call_with_retry(
        self,
        messages: list[dict],
        system: str,
        max_tokens: int,
        max_retries: int = 3,
    ):
        """Call API with exponential backoff on rate limits."""
        for attempt in range(max_retries):
            try:
                return self._client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    system=system,
                    messages=messages,
                )
            except anthropic.RateLimitError:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** (attempt + 1)
                print(f"Rate limited. Retrying in {wait}s...")
                time.sleep(wait)
            except anthropic.AuthenticationError:
                raise ValueError("Invalid ANTHROPIC_API_KEY. Check your .env file.")
