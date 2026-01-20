"""
Cricket Playbook - Smoke Tests for Stat Packs
==============================================

Tests to verify:
1. Database tables exist and have data
2. Analytics views are queryable
3. Stat pack files are generated correctly
4. Data integrity checks

Run with: pytest tests/test_stat_packs.py -v
"""

import pytest
from pathlib import Path
import duckdb

# Paths
PROJECT_DIR = Path(__file__).parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
STAT_PACK_DIR = PROJECT_DIR / "stat_packs"

# Team constants
IPL_TEAMS = ["CSK", "DC", "GT", "KKR", "LSG", "MI", "PBKS", "RCB", "RR", "SRH"]


@pytest.fixture(scope="module")
def db_connection():
    """Create a database connection for tests."""
    if not DB_PATH.exists():
        pytest.skip(f"Database not found at {DB_PATH}")
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    yield conn
    conn.close()


class TestDatabaseTables:
    """Test that required database tables exist and have data."""

    def test_fact_ball_exists(self, db_connection):
        """Verify fact_ball table exists with data."""
        result = db_connection.execute("SELECT COUNT(*) FROM fact_ball").fetchone()
        assert result[0] > 0, "fact_ball table should have records"

    def test_dim_player_exists(self, db_connection):
        """Verify dim_player table exists with data."""
        result = db_connection.execute("SELECT COUNT(*) FROM dim_player").fetchone()
        assert result[0] > 0, "dim_player table should have records"

    def test_dim_match_exists(self, db_connection):
        """Verify dim_match table exists with data."""
        result = db_connection.execute("SELECT COUNT(*) FROM dim_match").fetchone()
        assert result[0] > 0, "dim_match table should have records"

    def test_ipl_2026_squads_exists(self, db_connection):
        """Verify IPL 2026 squads table exists."""
        result = db_connection.execute("SELECT COUNT(*) FROM ipl_2026_squads").fetchone()
        assert result[0] >= 200, "Should have at least 200 players in squads"

    def test_dim_bowler_classification_exists(self, db_connection):
        """Verify bowler classification table exists."""
        result = db_connection.execute("SELECT COUNT(*) FROM dim_bowler_classification").fetchone()
        assert result[0] >= 250, "Should have at least 250 bowler classifications"

    def test_dim_franchise_alias_exists(self, db_connection):
        """Verify franchise alias table exists."""
        result = db_connection.execute("SELECT COUNT(*) FROM dim_franchise_alias").fetchone()
        assert result[0] >= 3, "Should have at least 3 franchise aliases"


class TestAnalyticsViews:
    """Test that analytics views are queryable."""

    @pytest.mark.parametrize("view_name", [
        "analytics_ipl_batting_career",
        "analytics_ipl_bowling_career",
        "analytics_ipl_batter_phase",
        "analytics_ipl_bowler_phase",
        "analytics_ipl_batter_vs_bowler",
        "analytics_ipl_batter_vs_bowler_type",
        "analytics_ipl_batter_vs_team",
        "analytics_ipl_bowler_vs_team",
        "analytics_ipl_squad_batting",
        "analytics_ipl_squad_bowling",
    ])
    def test_view_queryable(self, db_connection, view_name):
        """Verify that each analytics view can be queried."""
        result = db_connection.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
        assert result[0] > 0, f"{view_name} should return results"

    @pytest.mark.parametrize("view_name", [
        "analytics_ipl_batting_percentiles",
        "analytics_ipl_bowling_percentiles",
        "analytics_ipl_batter_phase_percentiles",
        "analytics_ipl_bowler_phase_percentiles",
    ])
    def test_percentile_views_queryable(self, db_connection, view_name):
        """Verify percentile views are queryable."""
        result = db_connection.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
        assert result[0] > 0, f"{view_name} should return results"

    @pytest.mark.parametrize("view_name", [
        "analytics_ipl_batting_benchmarks",
        "analytics_ipl_bowling_benchmarks",
        "analytics_ipl_vs_bowler_type_benchmarks",
        "analytics_ipl_career_benchmarks",
    ])
    def test_benchmark_views_queryable(self, db_connection, view_name):
        """Verify benchmark views are queryable."""
        result = db_connection.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
        assert result[0] > 0, f"{view_name} should return results"


class TestDataIntegrity:
    """Test data integrity and correctness."""

    def test_ipl_match_count(self, db_connection):
        """Verify IPL match count is reasonable."""
        result = db_connection.execute("""
            SELECT COUNT(DISTINCT dm.match_id)
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        """).fetchone()
        assert result[0] >= 1000, "Should have at least 1000 IPL matches"

    def test_kohli_exists_in_batting(self, db_connection):
        """Verify Virat Kohli exists in batting stats."""
        result = db_connection.execute("""
            SELECT runs FROM analytics_ipl_batting_career
            WHERE player_name LIKE '%Kohli%'
        """).fetchone()
        assert result is not None, "Virat Kohli should exist in batting stats"
        assert result[0] > 8000, "Kohli should have more than 8000 IPL runs"

    def test_all_10_teams_in_squads(self, db_connection):
        """Verify all 10 IPL teams are in squads."""
        result = db_connection.execute("""
            SELECT COUNT(DISTINCT team_name) FROM ipl_2026_squads
        """).fetchone()
        assert result[0] == 10, "Should have exactly 10 teams in squads"

    def test_bowling_style_coverage(self, db_connection):
        """Verify bowling style classification coverage."""
        result = db_connection.execute("""
            SELECT
                SUM(CASE WHEN bowler_type != 'Unknown' THEN balls ELSE 0 END) * 100.0 /
                SUM(balls) as coverage_pct
            FROM analytics_ipl_batter_vs_bowler_type
        """).fetchone()
        assert result[0] >= 95, "Bowling style coverage should be at least 95%"

    def test_franchise_aliases_working(self, db_connection):
        """Verify franchise aliases combine historical data."""
        result = db_connection.execute("""
            SELECT COUNT(DISTINCT opposition)
            FROM analytics_ipl_batter_vs_team
            WHERE opposition IN ('Delhi Daredevils', 'Kings XI Punjab', 'Royal Challengers Bangalore')
        """).fetchone()
        # These old names should NOT appear if aliases are working
        assert result[0] == 0, "Old franchise names should be aliased to current names"

    def test_sample_size_indicators_present(self, db_connection):
        """Verify sample size indicators are in views."""
        result = db_connection.execute("""
            SELECT DISTINCT sample_size FROM analytics_ipl_batter_phase
        """).fetchall()
        sample_sizes = [r[0] for r in result]
        assert "HIGH" in sample_sizes, "Should have HIGH sample size"
        assert "MEDIUM" in sample_sizes, "Should have MEDIUM sample size"
        assert "LOW" in sample_sizes, "Should have LOW sample size"


class TestStatPackFiles:
    """Test that stat pack files are generated correctly."""

    @pytest.mark.parametrize("team", IPL_TEAMS)
    def test_stat_pack_exists(self, team):
        """Verify stat pack file exists for each team."""
        stat_pack = STAT_PACK_DIR / f"{team}_stat_pack.md"
        assert stat_pack.exists(), f"Stat pack should exist for {team}"

    @pytest.mark.parametrize("team", IPL_TEAMS)
    def test_stat_pack_size(self, team):
        """Verify stat pack file is not empty."""
        stat_pack = STAT_PACK_DIR / f"{team}_stat_pack.md"
        if stat_pack.exists():
            size = stat_pack.stat().st_size
            assert size > 10000, f"Stat pack for {team} should be > 10KB, got {size}"

    @pytest.mark.parametrize("team", IPL_TEAMS)
    def test_stat_pack_has_required_sections(self, team):
        """Verify stat pack has all required sections."""
        stat_pack = STAT_PACK_DIR / f"{team}_stat_pack.md"
        if stat_pack.exists():
            content = stat_pack.read_text()
            assert "## 1. Squad Overview" in content, "Missing Squad Overview"
            assert "## 2. Historical Record" in content, "Missing Historical Record"
            assert "## 9. Andy Flower" in content, "Missing Tactical Insights"

    def test_readme_exists(self):
        """Verify README.md exists in stat_packs directory."""
        readme = STAT_PACK_DIR / "README.md"
        assert readme.exists(), "README.md should exist in stat_packs"


class TestPercentileRankings:
    """Test percentile ranking calculations."""

    def test_percentile_range(self, db_connection):
        """Verify percentiles are in 0-100 range."""
        result = db_connection.execute("""
            SELECT MIN(sr_percentile), MAX(sr_percentile)
            FROM analytics_ipl_batting_percentiles
        """).fetchone()
        assert result[0] >= 0, "Min percentile should be >= 0"
        assert result[1] <= 100, "Max percentile should be <= 100"

    def test_qualified_batters_count(self, db_connection):
        """Verify qualified batters threshold (500 balls)."""
        result = db_connection.execute("""
            SELECT COUNT(*), MIN(balls_faced)
            FROM analytics_ipl_batting_percentiles
        """).fetchone()
        assert result[0] > 100, "Should have at least 100 qualified batters"
        assert result[1] >= 500, "All batters should have >= 500 balls faced"


class TestBenchmarks:
    """Test benchmark/average calculations."""

    def test_phase_benchmarks_exist(self, db_connection):
        """Verify all 3 phases have benchmarks."""
        result = db_connection.execute("""
            SELECT COUNT(DISTINCT match_phase)
            FROM analytics_ipl_batting_benchmarks
        """).fetchone()
        assert result[0] == 3, "Should have benchmarks for 3 phases"

    def test_benchmark_strike_rates_reasonable(self, db_connection):
        """Verify benchmark strike rates are reasonable."""
        result = db_connection.execute("""
            SELECT match_phase, avg_strike_rate
            FROM analytics_ipl_batting_benchmarks
        """).fetchall()
        for phase, sr in result:
            assert 100 < sr < 200, f"{phase} avg SR {sr} seems unreasonable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
