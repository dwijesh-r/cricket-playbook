"""
Cross-Tournament Enrichment Tests
===================================
Validates the output schema and enrichment logic for uncapped players.

Run with: pytest tests/test_cross_tournament.py -v
"""

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
CROSS_TOURNAMENT_PATH = PROJECT_ROOT / "outputs" / "tags" / "cross_tournament_profiles.json"
PROFILES_PATH = PROJECT_ROOT / "outputs" / "player_profiles" / "player_profiles_2023.json"


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def cross_tournament_data():
    """Load cross-tournament profiles if they exist."""
    if not CROSS_TOURNAMENT_PATH.exists():
        pytest.skip("Cross-tournament profiles not yet generated")
    with open(CROSS_TOURNAMENT_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def player_profiles():
    """Load player profiles if they exist."""
    if not PROFILES_PATH.exists():
        pytest.skip("Player profiles not yet generated")
    with open(PROFILES_PATH, encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# SCHEMA TESTS
# =============================================================================


class TestOutputJsonSchema:
    """Validate cross-tournament output structure."""

    def test_top_level_keys(self, cross_tournament_data):
        """Output must have generated_at, data_scope, and players."""
        assert "generated_at" in cross_tournament_data
        assert "data_scope" in cross_tournament_data
        assert "players" in cross_tournament_data

    def test_data_scope(self, cross_tournament_data):
        """Data scope should indicate all T20 excluding IPL."""
        assert "t20" in cross_tournament_data["data_scope"].lower()

    def test_player_entry_structure(self, cross_tournament_data):
        """Each player entry must have required keys."""
        players = cross_tournament_data["players"]
        if not players:
            pytest.skip("No enriched players found")

        for pid, entry in players.items():
            assert "batting" in entry or "bowling" in entry, (
                f"Player {pid} has neither batting nor bowling"
            )
            assert "cluster_label" in entry
            assert "tournaments" in entry
            assert "total_balls" in entry
            assert isinstance(entry["tournaments"], list)
            assert entry["total_balls"] > 0


class TestEnrichedPlayerData:
    """Validate enriched player data quality."""

    def test_enriched_player_has_batting_data(self, cross_tournament_data):
        """Players with batting data should have valid stats."""
        players = cross_tournament_data["players"]
        batting_players = {pid: p for pid, p in players.items() if p.get("batting")}
        if not batting_players:
            pytest.skip("No players with batting data")

        for pid, entry in batting_players.items():
            bat = entry["batting"]
            assert bat["balls_faced"] > 0, f"Player {pid} has 0 balls_faced"
            assert bat["runs"] >= 0, f"Player {pid} has negative runs"
            assert bat["strike_rate"] is not None, f"Player {pid} has null strike_rate"
            assert bat["strike_rate"] > 0, f"Player {pid} has non-positive strike_rate"
            assert bat["innings"] is not None, f"Player {pid} has null innings"
            assert "fifties" in bat, f"Player {pid} missing fifties"
            assert "hundreds" in bat, f"Player {pid} missing hundreds"
            assert "dot_ball_pct" in bat, f"Player {pid} missing dot_ball_pct"

    def test_enriched_player_has_tournaments(self, cross_tournament_data):
        """Every enriched player must have at least one tournament."""
        players = cross_tournament_data["players"]
        for pid, entry in players.items():
            assert len(entry["tournaments"]) > 0, f"Player {pid} has no tournaments"


class TestProfileIntegration:
    """Validate that cross-tournament data is properly integrated into profiles."""

    def test_data_source_field(self, player_profiles):
        """Profiles should have a data_source field."""
        players = player_profiles.get("players", {})
        for pid, profile in players.items():
            assert "data_source" in profile, (
                f"Player {pid} ({profile.get('player_name')}) missing data_source"
            )
            assert profile["data_source"] in ("ipl", "cross_tournament", "none"), (
                f"Player {pid} has invalid data_source: {profile['data_source']}"
            )

    def test_cross_tournament_players_have_data(self, player_profiles):
        """Players with data_source=cross_tournament should have batting or bowling."""
        players = player_profiles.get("players", {})
        ct_players = {
            pid: p for pid, p in players.items() if p.get("data_source") == "cross_tournament"
        }
        for pid, profile in ct_players.items():
            has_data = profile.get("batting") is not None or profile.get("bowling") is not None
            assert has_data, (
                f"Cross-tournament player {pid} ({profile.get('player_name')}) "
                f"has no batting or bowling data"
            )

    def test_cross_tournament_players_have_tournaments(self, player_profiles):
        """Players with cross-tournament data should list their tournaments."""
        players = player_profiles.get("players", {})
        ct_players = {
            pid: p for pid, p in players.items() if p.get("data_source") == "cross_tournament"
        }
        for pid, profile in ct_players.items():
            assert profile.get("data_tournaments"), (
                f"Cross-tournament player {pid} ({profile.get('player_name')}) "
                f"has empty data_tournaments"
            )
