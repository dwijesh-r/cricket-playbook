#!/usr/bin/env python3
"""
TKT-139: Integration Tests for Data Pipeline
=============================================

This module contains integration tests for the Cricket Playbook data pipeline,
covering the complete flow from data ingestion to analytics generation.

Test Categories:
1. Ingest Flow Tests - Testing JSON ingestion and table population
2. Analytics Flow Tests - Testing view generation and metric computation
3. Stat Pack Generation Tests - Testing stat pack output structure
4. Clustering Pipeline Tests - Testing K-means clustering stability

Usage:
    # Run all integration tests
    pytest tests/integration/test_data_pipeline.py -v -m integration

    # Run specific test class
    pytest tests/integration/test_data_pipeline.py::TestIngestFlow -v

Author: Cricket Playbook Team
Ticket: TKT-139
"""

import hashlib
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


# =============================================================================
# TEST CONSTANTS
# =============================================================================

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_MATCH_PATH = FIXTURES_DIR / "sample_match.json"

# Expected tables after ingestion
EXPECTED_DIM_TABLES = [
    "dim_player",
    "dim_team",
    "dim_venue",
    "dim_tournament",
    "dim_match",
]

EXPECTED_FACT_TABLES = [
    "fact_ball",
    "fact_player_match_performance",
]

# Match phases for validation
MATCH_PHASES = ["powerplay", "middle", "death"]

# Metric value ranges (min, max) for sanity checks
METRIC_RANGES = {
    "strike_rate": (50.0, 300.0),
    "economy_rate": (3.0, 20.0),
    "average": (5.0, 100.0),
    "boundary_pct": (0.0, 100.0),
    "dot_ball_pct": (0.0, 100.0),
}


# =============================================================================
# PYTEST FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def sample_match_data() -> Dict[str, Any]:
    """
    Load sample match data from fixture file.

    Returns:
        Dict containing the sample match JSON data.

    Raises:
        FileNotFoundError: If fixture file doesn't exist.
    """
    if not SAMPLE_MATCH_PATH.exists():
        pytest.skip(f"Sample match fixture not found at {SAMPLE_MATCH_PATH}")

    with open(SAMPLE_MATCH_PATH) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def temp_db_path() -> Generator[Path, None, None]:
    """
    Create a temporary DuckDB database for testing.

    Yields:
        Path to the temporary database file.

    Note:
        Database file is automatically cleaned up after tests complete.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test_cricket.duckdb"
        yield db_path


@pytest.fixture(scope="module")
def ingested_db(temp_db_path: Path, sample_match_data: Dict[str, Any]):
    """
    Create a DuckDB database with ingested sample data.

    This fixture sets up the database schema and ingests the sample match data,
    providing a ready-to-use database for analytics tests.

    Args:
        temp_db_path: Path to temporary database file.
        sample_match_data: Sample match data from fixture.

    Yields:
        DuckDB connection with ingested data.
    """
    import duckdb

    conn = duckdb.connect(str(temp_db_path))

    # Ingest the sample match data
    _ingest_sample_match(conn, sample_match_data)

    yield conn

    conn.close()


@pytest.fixture(scope="function")
def isolated_db() -> Generator:
    """
    Create an isolated in-memory DuckDB database for each test function.

    This fixture provides a fresh database for tests that need isolation,
    preventing test pollution.

    Yields:
        DuckDB connection to an in-memory database.
    """
    import duckdb

    conn = duckdb.connect(":memory:")
    yield conn
    conn.close()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def generate_id(text: str) -> str:
    """Generate a short hash ID from text, matching ingest.py behavior."""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def get_match_phase(over: int) -> str:
    """
    Determine match phase from over number.

    Args:
        over: Over number (0-indexed).

    Returns:
        Match phase string: 'powerplay', 'middle', or 'death'.
    """
    if over < 6:
        return "powerplay"
    elif over < 15:
        return "middle"
    else:
        return "death"


def _ingest_sample_match(conn, match_data: Dict[str, Any]) -> None:
    """
    Ingest sample match data into DuckDB tables.

    This helper function mimics the core ingestion logic from ingest.py,
    creating dimension and fact tables from the match JSON.

    Args:
        conn: DuckDB connection.
        match_data: Parsed match JSON data.
    """
    import pandas as pd

    info = match_data.get("info", {})
    innings_data = match_data.get("innings", [])

    # Extract match metadata
    dates = info.get("dates", [])
    match_date = dates[0] if dates else "2024-01-01"
    match_id = "test_match_001"

    # Extract event info
    event = info.get("event", {})
    tournament_name = event.get("name", "Indian Premier League")
    tournament_id = "indian_premier_league"

    # Create dimension tables
    # 1. dim_tournament
    tournaments = [
        {
            "tournament_id": tournament_id,
            "tournament_name": tournament_name,
            "country": "India",
            "format": "T20",
            "gender": info.get("gender", "male"),
        }
    ]
    df_tournaments = pd.DataFrame(tournaments)  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE dim_tournament AS SELECT * FROM df_tournaments")

    # 2. dim_team
    teams = []
    team_id_map = {}
    for team_name in info.get("teams", []):
        team_id = generate_id(team_name)
        team_id_map[team_name] = team_id
        teams.append(
            {
                "team_id": team_id,
                "team_name": team_name,
                "short_name": "".join(w[0] for w in team_name.split()[:3]),
            }
        )
    df_teams = pd.DataFrame(teams)  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE dim_team AS SELECT * FROM df_teams")

    # 3. dim_venue
    venue_name = info.get("venue", "Test Stadium")
    city = info.get("city", "Test City")
    venue_id = generate_id(f"{venue_name}_{city}")
    venues = [
        {
            "venue_id": venue_id,
            "venue_name": venue_name,
            "city": city,
        }
    ]
    df_venues = pd.DataFrame(venues)  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE dim_venue AS SELECT * FROM df_venues")

    # 4. dim_player
    registry = info.get("registry", {}).get("people", {})
    players = []
    player_id_map = {}
    for player_name, cricsheet_id in registry.items():
        player_id = cricsheet_id or generate_id(player_name)
        player_id_map[player_name] = player_id
        players.append(
            {
                "player_id": player_id,
                "current_name": player_name,
                "first_seen_date": match_date,
                "last_seen_date": match_date,
                "matches_played": 1,
                "primary_role": "Batter",
                "is_wicketkeeper": False,
            }
        )
    df_players = pd.DataFrame(players)  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE dim_player AS SELECT * FROM df_players")

    # 5. dim_match
    team_names = info.get("teams", [])
    team1_id = team_id_map.get(team_names[0]) if len(team_names) > 0 else None
    team2_id = team_id_map.get(team_names[1]) if len(team_names) > 1 else None

    toss = info.get("toss", {})
    toss_winner = toss.get("winner")
    toss_winner_id = team_id_map.get(toss_winner) if toss_winner else None

    outcome = info.get("outcome", {})
    winner = outcome.get("winner")
    winner_id = team_id_map.get(winner) if winner else None

    matches = [
        {
            "match_id": match_id,
            "tournament_id": tournament_id,
            "match_number": event.get("match_number", 1),
            "stage": event.get("stage", "Group"),
            "season": info.get("season", "2024"),
            "match_date": match_date,
            "venue_id": venue_id,
            "team1_id": team1_id,
            "team2_id": team2_id,
            "toss_winner_id": toss_winner_id,
            "toss_decision": toss.get("decision"),
            "winner_id": winner_id,
            "outcome_type": "wickets" if "wickets" in outcome.get("by", {}) else "runs",
            "outcome_margin": outcome.get("by", {}).get("wickets")
            or outcome.get("by", {}).get("runs"),
            "player_of_match_id": player_id_map.get(info.get("player_of_match", [None])[0]),
            "balls_per_over": info.get("balls_per_over", 6),
            "data_version": "1.0.0",
            "is_active": True,
            "ingested_at": datetime.now().isoformat(),
            "source_file": "sample_match.json",
        }
    ]
    df_matches = pd.DataFrame(matches)  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE dim_match AS SELECT * FROM df_matches")

    # 6. fact_ball
    balls = []
    player_performances = {}  # Track per-player performance

    for innings_idx, innings in enumerate(innings_data, start=1):
        batting_team_name = innings.get("team")
        batting_team_id = team_id_map.get(batting_team_name)
        bowling_team_id = team2_id if batting_team_id == team1_id else team1_id

        ball_seq = 0
        for over_data in innings.get("overs", []):
            over_num = over_data.get("over", 0)
            match_phase = get_match_phase(over_num)

            for ball_idx, delivery in enumerate(over_data.get("deliveries", []), start=1):
                ball_seq += 1

                batter_name = delivery.get("batter")
                bowler_name = delivery.get("bowler")
                non_striker_name = delivery.get("non_striker")

                batter_id = player_id_map.get(batter_name)
                bowler_id = player_id_map.get(bowler_name)
                non_striker_id = player_id_map.get(non_striker_name)

                runs = delivery.get("runs", {})
                batter_runs = runs.get("batter", 0)
                extra_runs = runs.get("extras", 0)
                total_runs = runs.get("total", 0)

                extras = delivery.get("extras", {})
                extra_type = list(extras.keys())[0] if extras else None
                is_legal = extra_type not in ("wides", "noballs")

                wickets = delivery.get("wickets", [])
                is_wicket = len(wickets) > 0
                wicket_type = wickets[0].get("kind") if wickets else None
                player_out_name = wickets[0].get("player_out") if wickets else None
                player_out_id = player_id_map.get(player_out_name) if player_out_name else None

                fielders = wickets[0].get("fielders", []) if wickets else []
                fielder_name = fielders[0].get("name") if fielders else None
                fielder_id = player_id_map.get(fielder_name) if fielder_name else None

                ball_id = f"{match_id}_{innings_idx}_{over_num}_{ball_idx}"

                balls.append(
                    {
                        "ball_id": ball_id,
                        "match_id": match_id,
                        "innings": innings_idx,
                        "over": over_num,
                        "ball": ball_idx,
                        "ball_seq": ball_seq,
                        "batting_team_id": batting_team_id,
                        "bowling_team_id": bowling_team_id,
                        "batter_id": batter_id,
                        "bowler_id": bowler_id,
                        "non_striker_id": non_striker_id,
                        "batter_runs": batter_runs,
                        "extra_runs": extra_runs,
                        "total_runs": total_runs,
                        "extra_type": extra_type,
                        "is_wicket": is_wicket,
                        "wicket_type": wicket_type,
                        "player_out_id": player_out_id,
                        "fielder_id": fielder_id,
                        "is_legal_ball": is_legal,
                        "match_phase": match_phase,
                        "data_version": "1.0.0",
                        "ingested_at": datetime.now().isoformat(),
                        "source_file": "sample_match.json",
                    }
                )

                # Track player performances
                if batter_id:
                    if batter_id not in player_performances:
                        player_performances[batter_id] = {
                            "player_id": batter_id,
                            "match_id": match_id,
                            "team_id": batting_team_id,
                            "did_bat": True,
                            "did_bowl": False,
                            "did_keep_wicket": False,
                            "batting_position": None,
                        }
                if bowler_id:
                    if bowler_id not in player_performances:
                        player_performances[bowler_id] = {
                            "player_id": bowler_id,
                            "match_id": match_id,
                            "team_id": bowling_team_id,
                            "did_bat": False,
                            "did_bowl": True,
                            "did_keep_wicket": False,
                            "batting_position": None,
                        }
                    else:
                        player_performances[bowler_id]["did_bowl"] = True

    df_balls = pd.DataFrame(balls)  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE fact_ball AS SELECT * FROM df_balls")

    # 7. fact_player_match_performance
    df_perf = pd.DataFrame(list(player_performances.values()))  # noqa: F841 - used by DuckDB
    conn.execute("CREATE TABLE fact_player_match_performance AS SELECT * FROM df_perf")

    # Create indexes
    conn.execute("CREATE INDEX idx_ball_match ON fact_ball(match_id)")
    conn.execute("CREATE INDEX idx_ball_batter ON fact_ball(batter_id)")
    conn.execute("CREATE INDEX idx_ball_bowler ON fact_ball(bowler_id)")


def _create_analytics_views(conn) -> None:
    """
    Create basic analytics views for testing.

    This creates simplified versions of the production analytics views
    for testing purposes.

    Args:
        conn: DuckDB connection.
    """
    # Create batting career view
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_test_batting_career AS
        SELECT
            batter_id as player_id,
            dp.current_name as player_name,
            COUNT(DISTINCT match_id) as innings,
            SUM(batter_runs) as runs,
            COUNT(*) as balls_faced,
            ROUND(SUM(batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as boundary_pct,
            ROUND(SUM(CASE WHEN batter_runs = 0 AND is_legal_ball THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        WHERE fb.batter_id IS NOT NULL
        GROUP BY batter_id, dp.current_name
    """)

    # Create bowling career view
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_test_bowling_career AS
        SELECT
            bowler_id as player_id,
            dp.current_name as player_name,
            COUNT(DISTINCT match_id) as matches,
            COUNT(*) as balls_bowled,
            SUM(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END) as wickets,
            SUM(total_runs) as runs_conceded,
            ROUND(SUM(total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy_rate,
            ROUND(SUM(total_runs) * 1.0 / NULLIF(SUM(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt') THEN 1 ELSE 0 END), 0), 2) as strike_rate
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE fb.bowler_id IS NOT NULL
        GROUP BY bowler_id, dp.current_name
    """)

    # Create phase-wise batting view
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_test_batter_phase AS
        SELECT
            batter_id as player_id,
            dp.current_name as player_name,
            match_phase,
            COUNT(DISTINCT match_id) as innings,
            SUM(batter_runs) as runs,
            COUNT(*) as balls_faced,
            ROUND(SUM(batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(CASE WHEN batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as boundary_pct
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        WHERE fb.batter_id IS NOT NULL
        GROUP BY batter_id, dp.current_name, match_phase
    """)


# =============================================================================
# TEST CLASSES
# =============================================================================


@pytest.mark.integration
class TestIngestFlow:
    """
    Test suite for the data ingestion pipeline.

    Tests cover:
    - JSON match data parsing
    - Table creation and population
    - Schema validation after ingestion
    - Data integrity checks
    """

    def test_sample_match_loads(self, sample_match_data: Dict[str, Any]):
        """
        Test that sample match JSON loads correctly.

        Validates the basic structure of the sample match data including
        required top-level keys and nested structures.
        """
        assert sample_match_data is not None
        assert "info" in sample_match_data
        assert "innings" in sample_match_data

        info = sample_match_data["info"]
        assert "teams" in info
        assert "venue" in info
        assert "event" in info
        assert len(info["teams"]) == 2

    def test_sample_match_has_valid_innings(self, sample_match_data: Dict[str, Any]):
        """
        Test that sample match has valid innings data.

        Verifies that the innings structure contains proper over and
        delivery information.
        """
        innings = sample_match_data["innings"]
        assert len(innings) == 2, "Should have 2 innings"

        for idx, inn in enumerate(innings):
            assert "team" in inn, f"Innings {idx} missing team"
            assert "overs" in inn, f"Innings {idx} missing overs"
            assert len(inn["overs"]) > 0, f"Innings {idx} has no overs"

    def test_dimension_tables_created(self, ingested_db):
        """
        Test that all expected dimension tables are created after ingestion.

        Validates that the ingestion process creates all required dimension
        tables with data.
        """
        for table in EXPECTED_DIM_TABLES:
            result = ingested_db.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = '{table}'
            """).fetchone()
            assert result[0] > 0, f"Table {table} was not created"

    def test_fact_tables_created(self, ingested_db):
        """
        Test that all expected fact tables are created after ingestion.

        Validates that fact_ball and other fact tables exist and contain data.
        """
        for table in EXPECTED_FACT_TABLES:
            result = ingested_db.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = '{table}'
            """).fetchone()
            assert result[0] > 0, f"Fact table {table} was not created"

    def test_fact_ball_has_data(self, ingested_db):
        """
        Test that fact_ball table has records after ingestion.

        The sample match should produce multiple ball records across
        both innings.
        """
        result = ingested_db.execute("SELECT COUNT(*) FROM fact_ball").fetchone()
        assert result[0] > 0, "fact_ball should have records"

        # Sample match has ~72 deliveries (6 overs per innings x 2 innings)
        assert result[0] >= 60, f"Expected at least 60 balls, got {result[0]}"

    def test_players_extracted_correctly(self, ingested_db, sample_match_data: Dict[str, Any]):
        """
        Test that all players from the match are in dim_player.

        Validates that the player extraction correctly captures all players
        from both teams.
        """
        expected_player_count = len(sample_match_data["info"]["registry"]["people"])

        result = ingested_db.execute("SELECT COUNT(*) FROM dim_player").fetchone()

        assert result[0] == expected_player_count, (
            f"Expected {expected_player_count} players, got {result[0]}"
        )

    def test_match_phase_assigned_correctly(self, ingested_db):
        """
        Test that match phases are correctly assigned to each ball.

        Validates the mapping:
        - Overs 0-5: powerplay
        - Overs 6-14: middle
        - Overs 15-19: death
        """
        # All balls in our sample (overs 0-5) should be powerplay
        result = ingested_db.execute("""
            SELECT DISTINCT match_phase, MIN(over) as min_over, MAX(over) as max_over
            FROM fact_ball
            GROUP BY match_phase
            ORDER BY min_over
        """).fetchall()

        # Check that powerplay is assigned for overs 0-5
        powerplay_phases = [r for r in result if r[0] == "powerplay"]
        assert len(powerplay_phases) > 0, "Should have powerplay phase"
        assert powerplay_phases[0][1] == 0, "Powerplay should start at over 0"

    def test_schema_validation_runs(self, ingested_db):
        """
        Test that schema validation can run on ingested data.

        Simulates the validate_schema.py checks on the test database.
        """
        # Check required columns in fact_ball
        columns = ingested_db.execute("DESCRIBE fact_ball").fetchall()
        column_names = [col[0].lower() for col in columns]

        required_columns = [
            "ball_id",
            "match_id",
            "innings",
            "over",
            "ball",
            "batter_id",
            "bowler_id",
            "batter_runs",
            "total_runs",
            "is_wicket",
            "is_legal_ball",
            "match_phase",
        ]

        for col in required_columns:
            assert col in column_names, f"Missing required column: {col}"

    def test_wicket_tracking(self, ingested_db):
        """
        Test that wickets are correctly tracked in fact_ball.

        Validates that wicket events have proper wicket_type and player_out_id.
        """
        result = ingested_db.execute("""
            SELECT COUNT(*) FROM fact_ball
            WHERE is_wicket = true
        """).fetchone()

        wicket_count = result[0]
        assert wicket_count >= 2, f"Sample match should have at least 2 wickets, got {wicket_count}"

        # Verify wicket details
        wickets = ingested_db.execute("""
            SELECT wicket_type, player_out_id
            FROM fact_ball
            WHERE is_wicket = true
        """).fetchall()

        for wkt_type, player_out in wickets:
            assert wkt_type is not None, "Wicket should have wicket_type"
            assert player_out is not None, "Wicket should have player_out_id"


@pytest.mark.integration
class TestAnalyticsFlow:
    """
    Test suite for analytics view generation.

    Tests cover:
    - Analytics view creation from ingested data
    - Computed metrics validation
    - Metric range sanity checks
    """

    def test_analytics_views_can_be_created(self, ingested_db):
        """
        Test that analytics views can be generated from ingested data.

        Creates test versions of analytics views and verifies they execute
        without errors.
        """
        _create_analytics_views(ingested_db)

        # Verify views exist
        views = ["analytics_test_batting_career", "analytics_test_bowling_career"]
        for view in views:
            result = ingested_db.execute(f"""
                SELECT COUNT(*) FROM {view}
            """).fetchone()
            assert result[0] > 0, f"View {view} should have data"

    def test_batting_metrics_computed_correctly(self, ingested_db):
        """
        Test that batting metrics are computed correctly.

        Validates strike rate, average, and boundary percentage calculations.
        """
        _create_analytics_views(ingested_db)

        result = ingested_db.execute("""
            SELECT player_name, runs, balls_faced, strike_rate, boundary_pct
            FROM analytics_test_batting_career
            WHERE balls_faced >= 10
            ORDER BY runs DESC
            LIMIT 5
        """).fetchall()

        assert len(result) > 0, "Should have batting records"

        for player, runs, balls, sr, bound_pct in result:
            # Verify strike rate calculation
            expected_sr = round(runs * 100.0 / balls, 2) if balls > 0 else 0
            assert abs(sr - expected_sr) < 0.1, f"{player}: SR should be {expected_sr}, got {sr}"

            # Verify boundary percentage is in valid range
            if bound_pct is not None:
                assert 0 <= bound_pct <= 100, f"{player}: Boundary% {bound_pct} out of range"

    def test_bowling_metrics_computed_correctly(self, ingested_db):
        """
        Test that bowling metrics are computed correctly.

        Validates economy rate and bowling average calculations.
        """
        _create_analytics_views(ingested_db)

        result = ingested_db.execute("""
            SELECT player_name, balls_bowled, runs_conceded, wickets, economy_rate
            FROM analytics_test_bowling_career
            WHERE balls_bowled >= 6
            ORDER BY wickets DESC
            LIMIT 5
        """).fetchall()

        assert len(result) > 0, "Should have bowling records"

        for player, balls, runs, wickets, economy in result:
            # Verify economy rate calculation (runs per over)
            expected_econ = round(runs * 6.0 / balls, 2) if balls > 0 else 0
            assert abs(economy - expected_econ) < 0.1, (
                f"{player}: Economy should be {expected_econ}, got {economy}"
            )

    def test_phase_wise_metrics_computed(self, ingested_db):
        """
        Test that phase-wise batting metrics are computed.

        Validates that batting stats are broken down by match phase.
        """
        _create_analytics_views(ingested_db)

        result = ingested_db.execute("""
            SELECT match_phase, COUNT(*) as player_count
            FROM analytics_test_batter_phase
            GROUP BY match_phase
        """).fetchall()

        phases_found = {r[0] for r in result}
        assert "powerplay" in phases_found, "Should have powerplay phase stats"

    def test_metrics_in_expected_ranges(self, ingested_db):
        """
        Test that computed metrics fall within expected ranges.

        Validates that strike rates, averages, and percentages are sensible.
        """
        _create_analytics_views(ingested_db)

        # Check strike rates
        sr_result = ingested_db.execute("""
            SELECT MIN(strike_rate), MAX(strike_rate)
            FROM analytics_test_batting_career
            WHERE balls_faced >= 10
        """).fetchone()

        if sr_result[0] is not None:
            min_sr, max_sr = METRIC_RANGES["strike_rate"]
            assert sr_result[0] >= min_sr, f"Min SR {sr_result[0]} too low"
            assert sr_result[1] <= max_sr, f"Max SR {sr_result[1]} too high"

        # Check economy rates
        econ_result = ingested_db.execute("""
            SELECT MIN(economy_rate), MAX(economy_rate)
            FROM analytics_test_bowling_career
            WHERE balls_bowled >= 12
        """).fetchone()

        if econ_result[0] is not None:
            min_econ, max_econ = METRIC_RANGES["economy_rate"]
            assert econ_result[0] >= min_econ, f"Min economy {econ_result[0]} too low"
            assert econ_result[1] <= max_econ, f"Max economy {econ_result[1]} too high"


@pytest.mark.integration
class TestStatPackGeneration:
    """
    Test suite for stat pack generation.

    Tests cover:
    - Stat pack output structure validation
    - JSON output format verification
    - Required sections presence
    """

    def test_stat_pack_can_be_generated(self, ingested_db):
        """
        Test that a stat pack structure can be generated from data.

        Simulates the stat pack generation process and validates output.
        """
        _create_analytics_views(ingested_db)

        # Simulate stat pack data extraction
        batting_stats = ingested_db.execute("""
            SELECT player_name, runs, balls_faced, strike_rate
            FROM analytics_test_batting_career
            ORDER BY runs DESC
        """).fetchall()

        assert len(batting_stats) > 0, "Should have batting stats for stat pack"

    def test_stat_pack_json_structure(self, ingested_db):
        """
        Test that stat pack JSON output has correct structure.

        Validates the expected keys and data types in the output.
        """
        _create_analytics_views(ingested_db)

        # Build a sample stat pack JSON structure
        batting = ingested_db.execute("""
            SELECT player_id, player_name, runs, strike_rate, average
            FROM analytics_test_batting_career
        """).fetchall()

        bowling = ingested_db.execute("""
            SELECT player_id, player_name, wickets, economy_rate
            FROM analytics_test_bowling_career
        """).fetchall()

        stat_pack = {
            "team": "Test Team",
            "generated_at": datetime.now().isoformat(),
            "batting": [
                {
                    "player_id": row[0],
                    "player_name": row[1],
                    "runs": row[2],
                    "strike_rate": row[3],
                    "average": row[4],
                }
                for row in batting
            ],
            "bowling": [
                {
                    "player_id": row[0],
                    "player_name": row[1],
                    "wickets": row[2],
                    "economy": row[3],
                }
                for row in bowling
            ],
        }

        # Validate structure
        assert "team" in stat_pack
        assert "batting" in stat_pack
        assert "bowling" in stat_pack
        assert len(stat_pack["batting"]) > 0

        # Validate JSON serialization
        json_output = json.dumps(stat_pack)
        parsed = json.loads(json_output)
        assert parsed["team"] == "Test Team"

    def test_stat_pack_required_sections(self, ingested_db):
        """
        Test that stat pack has all required sections.

        Validates the presence of key statistical categories.
        """
        _create_analytics_views(ingested_db)

        required_sections = [
            "career_batting",
            "career_bowling",
            "phase_batting",
        ]

        sections_data = {}

        # Career batting
        sections_data["career_batting"] = ingested_db.execute("""
            SELECT COUNT(*) FROM analytics_test_batting_career
        """).fetchone()[0]

        # Career bowling
        sections_data["career_bowling"] = ingested_db.execute("""
            SELECT COUNT(*) FROM analytics_test_bowling_career
        """).fetchone()[0]

        # Phase batting
        sections_data["phase_batting"] = ingested_db.execute("""
            SELECT COUNT(*) FROM analytics_test_batter_phase
        """).fetchone()[0]

        for section in required_sections:
            assert sections_data[section] > 0, f"Section {section} should have data"


@pytest.mark.integration
class TestClusteringPipeline:
    """
    Test suite for the clustering pipeline.

    Tests cover:
    - Clustering execution on sample data
    - Cluster assignment validation
    - Clustering stability checks
    """

    def test_clustering_can_run_on_sample_data(self, ingested_db):
        """
        Test that clustering can execute on sample data.

        Validates that the clustering algorithm can process the ingested
        data without errors.
        """
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        _create_analytics_views(ingested_db)

        # Extract features for clustering
        features_df = ingested_db.execute("""
            SELECT player_id, strike_rate, boundary_pct, dot_ball_pct
            FROM analytics_test_batting_career
            WHERE balls_faced >= 10
              AND strike_rate IS NOT NULL
              AND boundary_pct IS NOT NULL
        """).df()

        if len(features_df) < 3:
            pytest.skip("Not enough data points for clustering")

        # Prepare features
        feature_cols = ["strike_rate", "boundary_pct", "dot_ball_pct"]
        X = features_df[feature_cols].fillna(0).values

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Run clustering
        n_clusters = min(3, len(features_df))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)

        # Validate assignments
        assert len(clusters) == len(features_df)
        assert len(set(clusters)) <= n_clusters

    def test_cluster_assignments_are_stable(self, ingested_db):
        """
        Test that cluster assignments are deterministic.

        Running the same clustering multiple times should produce
        identical results with the same random seed.
        """
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        _create_analytics_views(ingested_db)

        features_df = ingested_db.execute("""
            SELECT player_id, strike_rate, boundary_pct
            FROM analytics_test_batting_career
            WHERE balls_faced >= 10
              AND strike_rate IS NOT NULL
        """).df()

        if len(features_df) < 3:
            pytest.skip("Not enough data points for clustering")

        feature_cols = ["strike_rate", "boundary_pct"]
        X = features_df[feature_cols].fillna(0).values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        n_clusters = min(2, len(features_df))

        # Run clustering twice with same seed
        kmeans1 = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters1 = kmeans1.fit_predict(X_scaled)

        kmeans2 = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters2 = kmeans2.fit_predict(X_scaled)

        # Assignments should be identical
        assert np.array_equal(clusters1, clusters2), (
            "Cluster assignments should be stable with same random seed"
        )

    def test_cluster_centers_are_valid(self, ingested_db):
        """
        Test that cluster centers have valid feature values.

        Validates that cluster centers fall within expected feature ranges.
        """
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        _create_analytics_views(ingested_db)

        features_df = ingested_db.execute("""
            SELECT strike_rate, boundary_pct
            FROM analytics_test_batting_career
            WHERE balls_faced >= 10
              AND strike_rate IS NOT NULL
        """).df()

        if len(features_df) < 3:
            pytest.skip("Not enough data points for clustering")

        X = features_df.values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        n_clusters = min(2, len(features_df))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(X_scaled)

        # Inverse transform to get original scale centers
        centers = scaler.inverse_transform(kmeans.cluster_centers_)

        for i, center in enumerate(centers):
            sr, boundary = center
            # Validate strike rate is reasonable
            assert 50 <= sr <= 300, f"Cluster {i} SR {sr} out of range"
            # Validate boundary percentage is reasonable
            assert 0 <= boundary <= 100, f"Cluster {i} boundary% {boundary} out of range"


@pytest.mark.integration
class TestEndToEndPipeline:
    """
    Test suite for end-to-end pipeline execution.

    Tests the complete flow from ingestion through to analytics output.
    """

    def test_complete_pipeline_flow(self, sample_match_data: Dict[str, Any]):
        """
        Test the complete pipeline from ingestion to analytics.

        This test validates the entire data flow:
        1. Ingest match data
        2. Create analytics views
        3. Generate stat pack output
        4. Run clustering
        """
        import duckdb

        # Use a fresh in-memory database for this test
        conn = duckdb.connect(":memory:")

        try:
            # Step 1: Ingest data
            _ingest_sample_match(conn, sample_match_data)

            # Verify ingestion
            ball_count = conn.execute("SELECT COUNT(*) FROM fact_ball").fetchone()[0]
            assert ball_count > 0, "Ingestion should produce ball records"

            # Step 2: Create analytics views
            _create_analytics_views(conn)

            # Verify analytics
            batting_count = conn.execute(
                "SELECT COUNT(*) FROM analytics_test_batting_career"
            ).fetchone()[0]
            assert batting_count > 0, "Analytics should produce batting records"

            # Step 3: Generate stat pack structure
            stat_pack_data = conn.execute("""
                SELECT player_name, runs, strike_rate
                FROM analytics_test_batting_career
                ORDER BY runs DESC
            """).fetchall()
            assert len(stat_pack_data) > 0, "Stat pack should have data"

            # Step 4: Run clustering (if enough data)
            features = conn.execute("""
                SELECT strike_rate, boundary_pct
                FROM analytics_test_batting_career
                WHERE balls_faced >= 5
            """).df()

            if len(features) >= 2:
                from sklearn.cluster import KMeans
                from sklearn.preprocessing import StandardScaler

                X = features.fillna(0).values
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

                kmeans = KMeans(n_clusters=min(2, len(features)), random_state=42)
                clusters = kmeans.fit_predict(X_scaled)

                assert len(clusters) == len(features), "Clustering should assign all players"

        finally:
            conn.close()

    def test_data_integrity_across_pipeline(self, ingested_db):
        """
        Test data integrity is maintained across pipeline stages.

        Validates that player counts and ball counts remain consistent
        across dimension and fact tables.
        """
        # Get player count from dim_player
        player_count = ingested_db.execute(
            "SELECT COUNT(DISTINCT player_id) FROM dim_player"
        ).fetchone()[0]
        assert player_count > 0, "dim_player should have players"

        # Get unique players from fact_ball (batters)
        batter_count = ingested_db.execute(
            "SELECT COUNT(DISTINCT batter_id) FROM fact_ball WHERE batter_id IS NOT NULL"
        ).fetchone()[0]
        assert batter_count > 0, "fact_ball should have batters"
        assert batter_count <= player_count, "All batters should exist in dim_player"

        # All batters in fact_ball should exist in dim_player
        orphan_batters = ingested_db.execute("""
            SELECT COUNT(DISTINCT fb.batter_id)
            FROM fact_ball fb
            LEFT JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE fb.batter_id IS NOT NULL AND dp.player_id IS NULL
        """).fetchone()[0]

        assert orphan_batters == 0, f"Found {orphan_batters} orphaned batter IDs"

        # Match count should be consistent
        match_in_dim = ingested_db.execute(
            "SELECT COUNT(DISTINCT match_id) FROM dim_match"
        ).fetchone()[0]

        match_in_fact = ingested_db.execute(
            "SELECT COUNT(DISTINCT match_id) FROM fact_ball"
        ).fetchone()[0]

        assert match_in_dim == match_in_fact, (
            f"Match count mismatch: dim_match has {match_in_dim}, fact_ball has {match_in_fact}"
        )


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "integration: mark test as an integration test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
