"""Tests for agent config parsing."""

import pytest

from scripts.claude_orchestrator.config.agent_parser import (
    AgentConfig,
    get_agent,
    parse_agent_file,
    parse_all_agents,
    reload_agents,
)
from scripts.claude_orchestrator import AGENT_CONFIGS_DIR


class TestParseAllAgents:
    """Test parsing all 14 agent config files."""

    def setup_method(self):
        reload_agents()

    def test_parses_all_14_agents(self):
        agents = parse_all_agents()
        assert len(agents) == 14

    def test_all_agents_have_names(self):
        agents = parse_all_agents()
        for name, config in agents.items():
            assert config.name
            assert config.name == name

    def test_all_agents_have_models(self):
        agents = parse_all_agents()
        for config in agents.values():
            assert config.model

    def test_all_agents_have_temperatures(self):
        agents = parse_all_agents()
        for config in agents.values():
            assert 0.0 <= config.temperature <= 1.0

    def test_all_agents_have_role_content(self):
        agents = parse_all_agents()
        for config in agents.values():
            assert config.role_content

    def test_expected_agent_names(self):
        agents = parse_all_agents()
        names = set(agents.keys())
        assert "Tom Brady" in names
        assert "Florentino Perez" in names
        assert "Stephen Curry" in names
        assert len(names) == 14


class TestYamlAgents:
    """Test agents with YAML frontmatter."""

    def test_tom_brady(self):
        filepath = AGENT_CONFIGS_DIR / "tom-brady.agent.md"
        config = parse_agent_file(filepath)
        assert config.name == "Tom Brady"
        assert config.temperature == 0.2
        assert config.model == "claude-3-5-sonnet"
        assert "read_file" in config.tools

    def test_stephen_curry(self):
        filepath = AGENT_CONFIGS_DIR / "stephen-curry.agent.md"
        config = parse_agent_file(filepath)
        assert config.name == "Stephen Curry"
        assert config.temperature == 0.25

    def test_ngolo_kante_has_veto(self):
        filepath = AGENT_CONFIGS_DIR / "n-golo-kante.agent.md"
        config = parse_agent_file(filepath)
        assert config.name == "N'Golo Kanté"
        assert config.veto_authority is not None
        assert "Founder" in config.override_chain

    def test_andy_flower_veto_chain(self):
        filepath = AGENT_CONFIGS_DIR / "andy-flower.agent.md"
        config = parse_agent_file(filepath)
        assert config.veto_authority is not None
        assert "Tom Brady" in config.override_chain
        assert "Founder" in config.override_chain

    def test_ime_udoka_extra_tool(self):
        filepath = AGENT_CONFIGS_DIR / "ime-udoka.agent.md"
        config = parse_agent_file(filepath)
        assert "bash" in config.tools


class TestFlorentino:
    """Test Florentino Perez's pure-markdown format."""

    def test_florentino_no_yaml(self):
        filepath = AGENT_CONFIGS_DIR / "florentino-perez.agent.md"
        config = parse_agent_file(filepath)
        assert config.name == "Florentino Perez"
        assert config.temperature == 0.20
        assert config.veto_authority is not None

    def test_florentino_has_role_content(self):
        filepath = AGENT_CONFIGS_DIR / "florentino-perez.agent.md"
        config = parse_agent_file(filepath)
        assert "Program Director" in config.role_content

    def test_florentino_guardrails(self):
        filepath = AGENT_CONFIGS_DIR / "florentino-perez.agent.md"
        config = parse_agent_file(filepath)
        assert len(config.guardrails) > 0


class TestOutputPaths:
    """Test extraction of output file paths."""

    def test_curry_output_paths(self):
        filepath = AGENT_CONFIGS_DIR / "stephen-curry.agent.md"
        config = parse_agent_file(filepath)
        assert any("metric_pack" in p for p in config.output_paths)

    def test_kante_output_paths(self):
        filepath = AGENT_CONFIGS_DIR / "n-golo-kante.agent.md"
        config = parse_agent_file(filepath)
        assert isinstance(config.output_paths, list)

    def test_mourinho_output_paths(self):
        filepath = AGENT_CONFIGS_DIR / "jose-mourinho.agent.md"
        config = parse_agent_file(filepath)
        assert any("mourinho" in p for p in config.output_paths)


class TestGetAgent:
    """Test the get_agent convenience function."""

    def setup_method(self):
        reload_agents()

    def test_get_existing_agent(self):
        config = get_agent("Tom Brady")
        assert config.name == "Tom Brady"

    def test_get_case_insensitive(self):
        config = get_agent("tom brady")
        assert config.name == "Tom Brady"

    def test_get_missing_agent_raises(self):
        with pytest.raises(KeyError, match="not found"):
            get_agent("Nonexistent Agent")


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_agent_config_dataclass(self):
        config = AgentConfig(
            name="Test Agent",
            description="Test",
            model="claude-3-5-sonnet",
            temperature=0.5,
        )
        assert config.name == "Test Agent"
        assert config.tools == []
        assert config.guardrails == []

    def test_agent_config_defaults(self):
        config = AgentConfig(
            name="Minimal",
            description="",
            model="claude-3-5-sonnet",
            temperature=0.0,
        )
        assert config.output_paths == []
        assert config.collaboration == []
        assert config.veto_authority is None
        assert config.source_file == ""
