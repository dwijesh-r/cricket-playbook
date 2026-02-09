"""Tests for the Anthropic SDK client wrapper."""

import os
import pytest
from unittest.mock import MagicMock, patch

from scripts.claude_orchestrator.config.agent_parser import AgentConfig
from scripts.claude_orchestrator.core.client import AgentClient, MessageResult


@pytest.fixture
def agent_config():
    return AgentConfig(
        name="Test Agent",
        description="Test agent for unit tests",
        model="claude-3-5-sonnet",
        temperature=0.25,
    )


def _make_mock_response(text="Test response", input_tokens=100, output_tokens=50):
    """Create a mock API response."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(type="text", text=text)]
    mock_response.usage.input_tokens = input_tokens
    mock_response.usage.output_tokens = output_tokens
    mock_response.model = "claude-sonnet-4-5-20250929"
    mock_response.stop_reason = "end_turn"
    return mock_response


class TestAgentClient:
    """Test AgentClient initialization and API calls."""

    def test_no_api_key_raises(self, agent_config):
        # Temporarily remove ANTHROPIC_API_KEY from env and prevent dotenv loading
        env_copy = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env_copy, clear=True):
            with patch("scripts.claude_orchestrator.core.client.anthropic"):
                with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                    AgentClient(agent_config)

    def test_send_passes_correct_params(self, agent_config):
        mock_response = _make_mock_response()
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"}):
            with patch("scripts.claude_orchestrator.core.client.anthropic") as mock_mod:
                mock_mod.Anthropic.return_value.messages.create.return_value = mock_response
                client = AgentClient(agent_config)
                messages = [{"role": "user", "content": "Hello"}]
                client.send(messages, system="You are a test agent")

                call_kwargs = mock_mod.Anthropic.return_value.messages.create.call_args[1]
                assert call_kwargs["temperature"] == 0.25
                assert call_kwargs["system"] == "You are a test agent"
                assert call_kwargs["messages"] == messages

    def test_send_returns_message_result(self, agent_config):
        mock_response = _make_mock_response()
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"}):
            with patch("scripts.claude_orchestrator.core.client.anthropic") as mock_mod:
                mock_mod.Anthropic.return_value.messages.create.return_value = mock_response
                client = AgentClient(agent_config)
                result = client.send([{"role": "user", "content": "Hello"}], system="test")

                assert isinstance(result, MessageResult)
                assert result.content == "Test response"
                assert result.input_tokens == 100
                assert result.output_tokens == 50

    def test_model_resolution(self, agent_config):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"}):
            with patch("scripts.claude_orchestrator.core.client.anthropic"):
                client = AgentClient(agent_config)
                assert client.model == "claude-sonnet-4-5-20250929"

    def test_retry_on_rate_limit(self, agent_config):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"}):
            with patch("scripts.claude_orchestrator.core.client.anthropic") as mock_mod:
                # Define custom exception classes on the mock module
                class MockRateLimitError(Exception):
                    pass

                mock_mod.RateLimitError = MockRateLimitError

                mock_response = _make_mock_response(text="OK", input_tokens=10, output_tokens=5)
                mock_client = mock_mod.Anthropic.return_value
                mock_client.messages.create.side_effect = [
                    MockRateLimitError("rate limited"),
                    mock_response,
                ]

                client = AgentClient(agent_config)
                with patch("time.sleep"):
                    result = client.send([{"role": "user", "content": "test"}], system="test")

                assert result.content == "OK"
                assert mock_client.messages.create.call_count == 2

    def test_auth_error_raises_value_error(self, agent_config):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"}):
            with patch("scripts.claude_orchestrator.core.client.anthropic") as mock_mod:

                class MockRateLimitError(Exception):
                    pass

                class MockAuthError(Exception):
                    pass

                mock_mod.RateLimitError = MockRateLimitError
                mock_mod.AuthenticationError = MockAuthError
                mock_mod.Anthropic.return_value.messages.create.side_effect = MockAuthError(
                    "invalid key"
                )

                client = AgentClient(agent_config)
                with pytest.raises(ValueError, match="Invalid ANTHROPIC_API_KEY"):
                    client.send([{"role": "user", "content": "test"}], system="test")
