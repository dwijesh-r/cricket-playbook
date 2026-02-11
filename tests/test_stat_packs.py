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

    @pytest.mark.parametrize(
        "view_name",
        [
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
        ],
    )
    def test_view_queryable(self, db_connection, view_name):
        """Verify that each analytics view can be queried."""
        result = db_connection.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
        assert result[0] > 0, f"{view_name} should return results"

    @pytest.mark.parametrize(
        "view_name",
        [
            "analytics_ipl_batting_percentiles",
            "analytics_ipl_bowling_percentiles",
            "analytics_ipl_batter_phase_percentiles",
            "analytics_ipl_bowler_phase_percentiles",
        ],
    )
    def test_percentile_views_queryable(self, db_connection, view_name):
        """Verify percentile views are queryable."""
        result = db_connection.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
        assert result[0] > 0, f"{view_name} should return results"

    @pytest.mark.parametrize(
        "view_name",
        [
            "analytics_ipl_batting_benchmarks",
            "analytics_ipl_bowling_benchmarks",
            "analytics_ipl_vs_bowler_type_benchmarks",
            "analytics_ipl_career_benchmarks",
        ],
    )
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
        """Verify Virat Kohli exists in batting stats (2023+ data only)."""
        result = db_connection.execute("""
            SELECT runs FROM analytics_ipl_batting_career
            WHERE player_name LIKE '%Kohli%'
        """).fetchone()
        assert result is not None, "Virat Kohli should exist in batting stats"
        assert result[0] > 1500, "Kohli should have more than 1500 IPL runs (2023-2025)"

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
        # Stat packs are in subdirectories: stat_packs/{team}/{team}_stat_pack.md
        stat_pack = STAT_PACK_DIR / team / f"{team}_stat_pack.md"
        assert stat_pack.exists(), f"Stat pack should exist for {team}"

    @pytest.mark.parametrize("team", IPL_TEAMS)
    def test_stat_pack_size(self, team):
        """Verify stat pack file is not empty."""
        stat_pack = STAT_PACK_DIR / team / f"{team}_stat_pack.md"
        if stat_pack.exists():
            size = stat_pack.stat().st_size
            assert size > 10000, f"Stat pack for {team} should be > 10KB, got {size}"

    @pytest.mark.parametrize("team", IPL_TEAMS)
    def test_stat_pack_has_required_sections(self, team):
        """Verify stat pack has all required sections."""
        stat_pack = STAT_PACK_DIR / team / f"{team}_stat_pack.md"
        if stat_pack.exists():
            content = stat_pack.read_text()
            assert "## 1. Squad Overview" in content, "Missing Squad Overview"
            assert "## 2. Historical Record" in content, "Missing Historical Record"
            assert "## 3. Historical Trends" in content, "Missing Historical Trends"
            assert "## 4. Venue Analysis" in content, "Missing Venue Analysis"
            assert "## 10. Andy Flower" in content, "Missing Tactical Insights"

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
        """Verify qualified batters threshold (500 balls, 2023+ data)."""
        result = db_connection.execute("""
            SELECT COUNT(*), MIN(balls_faced)
            FROM analytics_ipl_batting_percentiles
        """).fetchone()
        # With 2023+ filter (219 matches), fewer batters qualify for 500 ball threshold
        assert result[0] > 25, "Should have at least 25 qualified batters (2023-2025)"
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


class TestV2ClusteringAndFounderReview3Fixes:
    """
    V2 Smoke Tests - Clustering Model and Founder Review #3 Fixes

    These tests validate:
    1. Bowler timing classification bug fixes (Chahar, Boult)
    2. Batter matchup dismissal quality checks (Markram)
    3. Phase-wise bowler tags (PP_BEAST, DEATH_BEAST, etc.)
    4. V2 cluster validation
    5. CSV output structure
    """

    # CSV Paths
    BOWLER_OVER_TIMING_CSV = STAT_PACK_DIR.parent / "outputs" / "bowler_over_timing.csv"
    BOWLER_PHASE_PERF_CSV = STAT_PACK_DIR.parent / "outputs" / "bowler_phase_performance.csv"
    BATTER_BOWLING_TYPE_MATCHUP_CSV = (
        STAT_PACK_DIR.parent / "outputs" / "batter_bowling_type_matchup.csv"
    )
    BATTER_BOWLING_TYPE_DETAIL_CSV = (
        STAT_PACK_DIR.parent / "outputs" / "batter_bowling_type_detail.csv"
    )

    # =========================================================================
    # Founder Review #3 Fix: Bowler Timing Classification Bug (Issues 6, 7)
    # =========================================================================

    def test_chahar_is_powerplay_bowler(self):
        """
        Founder Review #3 Issue 6: Deepak Chahar should be POWERPLAY_BOWLER.

        Bug: 0 was treated as falsy in Python, causing over1_median=0 to be
        incorrectly evaluated. Chahar (over1_median=0) was wrongly classified
        as MIDDLE_OVERS_BOWLER.
        """
        import pandas as pd

        if not self.BOWLER_OVER_TIMING_CSV.exists():
            pytest.skip(f"bowler_over_timing.csv not found at {self.BOWLER_OVER_TIMING_CSV}")

        df = pd.read_csv(self.BOWLER_OVER_TIMING_CSV)
        chahar = df[df["bowler_name"] == "DL Chahar"]

        assert len(chahar) == 1, "DL Chahar should exist in bowler_over_timing.csv"

        role = chahar.iloc[0]["role_category"]
        assert role == "POWERPLAY_BOWLER", (
            f"DL Chahar should be POWERPLAY_BOWLER (over1_median=0), "
            f"but got {role}. This was a bug where 0 was treated as falsy."
        )

    def test_boult_is_not_middle_overs_bowler(self):
        """
        Founder Review #3 Issue 7: Trent Boult should NOT be MIDDLE_OVERS_BOWLER.

        Bug: Same as Issue 6. Boult (over1_median=0, over2_median=2) was wrongly
        classified as MIDDLE_OVERS_BOWLER when he clearly bowls powerplay overs.

        Expected: PP_AND_DEATH_SPECIALIST or POWERPLAY_BOWLER (not MIDDLE_OVERS_BOWLER)
        """
        import pandas as pd

        if not self.BOWLER_OVER_TIMING_CSV.exists():
            pytest.skip(f"bowler_over_timing.csv not found at {self.BOWLER_OVER_TIMING_CSV}")

        df = pd.read_csv(self.BOWLER_OVER_TIMING_CSV)
        boult = df[df["bowler_name"] == "TA Boult"]

        assert len(boult) == 1, "TA Boult should exist in bowler_over_timing.csv"

        role = boult.iloc[0]["role_category"]
        assert role != "MIDDLE_OVERS_BOWLER", (
            f"TA Boult should NOT be MIDDLE_OVERS_BOWLER (over1_median=0, over2_median=2), "
            f"but got {role}. He bowls PP and death overs."
        )
        # Verify he is classified as a PP or death specialist
        assert role in [
            "POWERPLAY_BOWLER",
            "PP_AND_DEATH_SPECIALIST",
            "DEATH_BOWLER",
        ], f"TA Boult should be POWERPLAY_BOWLER or PP_AND_DEATH_SPECIALIST, got {role}"

    # =========================================================================
    # Founder Review #3 Fix: Batter Matchup Dismissal Quality (Issue 3)
    # =========================================================================

    def test_markram_not_specialist_vs_left_arm_spin(self):
        """
        Founder Review #3 Issue 3: Aiden Markram should NOT be SPECIALIST_VS_LEFT_ARM_SPIN.

        Why: Despite SR 130.9 vs left-arm orthodox, his stats show:
        - Average: 18.0 (LOW - indicates frequent dismissals)
        - Balls per dismissal: 13.75 (VERY HIGH dismissal rate)

        The fix added Average and Balls/Dismissal checks to specialist criteria.
        49 players were corrected by this fix.
        """
        import pandas as pd

        if not self.BATTER_BOWLING_TYPE_MATCHUP_CSV.exists():
            pytest.skip("batter_bowling_type_matchup.csv not found")

        df = pd.read_csv(self.BATTER_BOWLING_TYPE_MATCHUP_CSV)
        markram = df[df["batter_name"] == "AK Markram"]

        assert len(markram) == 1, "AK Markram should exist in batter_bowling_type_matchup.csv"

        tags = markram.iloc[0]["bowling_type_tags"]
        tags_str = str(tags) if pd.notna(tags) else ""

        assert "SPECIALIST_VS_LEFT_ARM_SPIN" not in tags_str, (
            f"AK Markram should NOT be SPECIALIST_VS_LEFT_ARM_SPIN. "
            f"SR 130.9 but Avg 18.0, BPD 13.75 (gets out too often). "
            f"Tags found: {tags_str}"
        )

    def test_batter_matchup_has_average_columns(self):
        """
        Founder Review #3 Issue 3: batter_bowling_type_matchup.csv must have average columns.

        Required for dismissal quality checks: SR alone is not enough.
        """
        import pandas as pd

        if not self.BATTER_BOWLING_TYPE_MATCHUP_CSV.exists():
            pytest.skip("batter_bowling_type_matchup.csv not found")

        df = pd.read_csv(self.BATTER_BOWLING_TYPE_MATCHUP_CSV)

        # Check for average columns
        assert "pace_avg" in df.columns, (
            "batter_bowling_type_matchup.csv should have pace_avg column"
        )
        assert "spin_avg" in df.columns, (
            "batter_bowling_type_matchup.csv should have spin_avg column"
        )

        # Check for dismissals columns (needed to compute balls_per_dismissal)
        assert "pace_dismissals" in df.columns, (
            "batter_bowling_type_matchup.csv should have pace_dismissals column"
        )
        assert "spin_dismissals" in df.columns, (
            "batter_bowling_type_matchup.csv should have spin_dismissals column"
        )

    def test_batter_detail_has_required_columns(self):
        """
        batter_bowling_type_detail.csv should have columns for dismissal quality analysis.
        """
        import pandas as pd

        if not self.BATTER_BOWLING_TYPE_DETAIL_CSV.exists():
            pytest.skip("batter_bowling_type_detail.csv not found")

        df = pd.read_csv(self.BATTER_BOWLING_TYPE_DETAIL_CSV)

        required_cols = [
            "batter_id",
            "batter_name",
            "bowling_type",
            "balls",
            "runs",
            "dismissals",
            "strike_rate",
            "average",
        ]
        for col in required_cols:
            assert col in df.columns, f"batter_bowling_type_detail.csv should have {col} column"

    # =========================================================================
    # Founder Review #3 Fix: Phase-wise Bowler Tags (Issue 2)
    # =========================================================================

    def test_phase_tags_exist_in_bowler_phase_performance(self):
        """
        Founder Review #3 Issue 2: Phase-wise tags should be generated.

        Tags: PP_BEAST, PP_LIABILITY, MIDDLE_OVERS_BEAST, MIDDLE_OVERS_LIABILITY,
              DEATH_BEAST, DEATH_LIABILITY
        """
        import pandas as pd

        if not self.BOWLER_PHASE_PERF_CSV.exists():
            pytest.skip("bowler_phase_performance.csv not found")

        df = pd.read_csv(self.BOWLER_PHASE_PERF_CSV)

        # Check phase_tags column exists
        assert "phase_tags" in df.columns, (
            "bowler_phase_performance.csv should have phase_tags column"
        )

        # Concatenate all tags to check for presence
        all_tags = df["phase_tags"].dropna().str.cat(sep=", ")

        # Check that at least some key phase tags exist
        expected_tags = ["PP_BEAST", "PP_LIABILITY", "DEATH_BEAST", "DEATH_LIABILITY"]
        found_tags = [tag for tag in expected_tags if tag in all_tags]

        assert len(found_tags) >= 3, (
            f"Expected at least 3 of {expected_tags} in phase_tags, but only found: {found_tags}"
        )

    def test_bowler_phase_performance_csv_structure(self):
        """
        bowler_phase_performance.csv should have correct column structure.
        """
        import pandas as pd

        if not self.BOWLER_PHASE_PERF_CSV.exists():
            pytest.skip("bowler_phase_performance.csv not found")

        df = pd.read_csv(self.BOWLER_PHASE_PERF_CSV)

        required_cols = [
            "bowler_id",
            "bowler_name",
            "powerplay_overs",
            "powerplay_economy",
            "powerplay_wickets",
            "middle_overs",
            "middle_economy",
            "middle_wickets",
            "death_overs",
            "death_economy",
            "death_wickets",
            "phase_tags",
        ]

        for col in required_cols:
            assert col in df.columns, f"bowler_phase_performance.csv missing required column: {col}"

    def test_steyn_is_death_beast(self):
        """
        Validate phase tag assignment: Dale Steyn should be DEATH_BEAST.

        DW Steyn: death_economy=8.47 (<8.5 threshold), death_overs=105.7 (>30)
        """
        import pandas as pd

        if not self.BOWLER_PHASE_PERF_CSV.exists():
            pytest.skip("bowler_phase_performance.csv not found")

        df = pd.read_csv(self.BOWLER_PHASE_PERF_CSV)
        steyn = df[df["bowler_name"] == "DW Steyn"]

        if len(steyn) == 0:
            pytest.skip("DW Steyn not found in bowler_phase_performance.csv")

        tags = str(steyn.iloc[0]["phase_tags"]) if pd.notna(steyn.iloc[0]["phase_tags"]) else ""
        assert "DEATH_BEAST" in tags, f"DW Steyn should have DEATH_BEAST tag, got: {tags}"

    # =========================================================================
    # V2 Cluster Validation (Andy Flower Approved)
    # =========================================================================

    def test_bowler_over_timing_csv_has_required_columns(self):
        """
        bowler_over_timing.csv should have all required columns for classification.
        """
        import pandas as pd

        if not self.BOWLER_OVER_TIMING_CSV.exists():
            pytest.skip("bowler_over_timing.csv not found")

        df = pd.read_csv(self.BOWLER_OVER_TIMING_CSV)

        required_cols = [
            "bowler_id",
            "bowler_name",
            "match_count",
            "over1_median",
            "over1_mode",
            "over1_count",
            "over2_median",
            "over2_mode",
            "over2_count",
            "role_category",
        ]

        for col in required_cols:
            assert col in df.columns, f"bowler_over_timing.csv missing required column: {col}"

    def test_role_categories_are_valid(self):
        """
        role_category in bowler_over_timing.csv should only contain valid values.

        Valid categories (from Founder Review #3 Issue 8):
        - POWERPLAY_BOWLER
        - MIDDLE_OVERS_BOWLER
        - DEATH_BOWLER
        - PP_AND_DEATH_SPECIALIST (for bowlers like Malinga who bowl both)
        """
        import pandas as pd

        if not self.BOWLER_OVER_TIMING_CSV.exists():
            pytest.skip("bowler_over_timing.csv not found")

        df = pd.read_csv(self.BOWLER_OVER_TIMING_CSV)

        valid_categories = {
            "POWERPLAY_BOWLER",
            "MIDDLE_OVERS_BOWLER",
            "DEATH_BOWLER",
            "PP_AND_DEATH_SPECIALIST",
        }

        actual_categories = set(df["role_category"].dropna().unique())
        invalid = actual_categories - valid_categories

        assert len(invalid) == 0, (
            f"Found invalid role categories: {invalid}. Valid categories are: {valid_categories}"
        )

    def test_pp_and_death_specialist_exists(self):
        """
        Founder Review #3 Issue 8: PP_AND_DEATH_SPECIALIST category should exist.

        Bowlers like Malinga who bowl both PP and death should have this tag.
        """
        import pandas as pd

        if not self.BOWLER_OVER_TIMING_CSV.exists():
            pytest.skip("bowler_over_timing.csv not found")

        df = pd.read_csv(self.BOWLER_OVER_TIMING_CSV)

        pp_and_death = df[df["role_category"] == "PP_AND_DEATH_SPECIALIST"]

        assert len(pp_and_death) > 0, (
            "PP_AND_DEATH_SPECIALIST category should have at least one bowler. "
            "Bowlers like Malinga who bowl PP and death overs should have this tag."
        )

    def test_dhoni_has_finisher_tag(self):
        """
        V2 Cluster Validation: MS Dhoni should have FINISHER tag.

        Andy Flower approved cluster: DEATH_FINISHER
        Dhoni is the quintessential finisher in IPL history.
        """
        import json

        player_tags_path = STAT_PACK_DIR.parent / "outputs" / "tags" / "player_tags.json"

        if not player_tags_path.exists():
            pytest.skip("player_tags.json not found")

        with open(player_tags_path) as f:
            data = json.load(f)

        # Find Dhoni in batters
        dhoni = None
        for batter in data.get("batters", []):
            if batter.get("player_name") == "MS Dhoni":
                dhoni = batter
                break

        assert dhoni is not None, "MS Dhoni should exist in player_tags.json batters"

        tags = dhoni.get("tags", [])
        assert "FINISHER" in tags, (
            f"MS Dhoni should have FINISHER tag (Andy Flower V2 cluster: DEATH_FINISHER). "
            f"Actual tags: {tags}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
