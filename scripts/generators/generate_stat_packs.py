#!/usr/bin/env python3
"""
Cricket Playbook - IPL 2026 Team Stat Pack Generator
Author: Tom Brady (Product Owner) & Stephen Curry (Analytics)
Domain Review: Andy Flower
Refactored by: Brad Stevens (Architecture Lead) - TKT-082

Generates comprehensive stat packs for each IPL 2026 team including:
- Team overview and roster
- Historical records vs each opposition
- Venue performance breakdown
- Individual player statistics
- Phase-wise analysis
- Key matchups and insights

Architecture:
- Configuration constants at module level
- Dedicated SQL query builder functions
- Separate section generators for each stat pack part
- Centralized error handling and logging
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from scripts.utils.logging_config import setup_logger

# ML Health Check integration (TKT-073)
try:
    from scripts.ml_ops.run_health_check import run_health_check as ml_health_check

    ML_HEALTH_CHECK_AVAILABLE = True
except ImportError:
    ML_HEALTH_CHECK_AVAILABLE = False

# Initialize logger
logger = setup_logger(__name__)


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # Go up two levels: generators -> scripts -> project root
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "stat_packs"
PLAYER_TAGS_PATH = PROJECT_DIR / "outputs" / "player_tags.json"


# =============================================================================
# PLAYER ARCHETYPE CONSTANTS (K-means V2 Model)
# =============================================================================

BATTER_CLUSTERS = frozenset(
    {
        "EXPLOSIVE_OPENER",
        "PLAYMAKER",
        "ANCHOR",
        "ACCUMULATOR",
        "MIDDLE_ORDER",
        "FINISHER",
    }
)

BOWLER_CLUSTERS = frozenset(
    {
        "PACER",
        "SPINNER",
        "WORKHORSE",
        "NEW_BALL_SPECIALIST",
        "MIDDLE_OVERS_CONTROLLER",
        "DEATH_SPECIALIST",
        "PART_TIMER",
    }
)

# Ordered lists for display purposes
BATTER_CLUSTERS_ORDERED = [
    "EXPLOSIVE_OPENER",
    "PLAYMAKER",
    "ANCHOR",
    "ACCUMULATOR",
    "MIDDLE_ORDER",
    "FINISHER",
]

BOWLER_CLUSTERS_ORDERED = [
    "PACER",
    "SPINNER",
    "WORKHORSE",
    "NEW_BALL_SPECIALIST",
    "MIDDLE_OVERS_CONTROLLER",
    "DEATH_SPECIALIST",
    "PART_TIMER",
]


# =============================================================================
# ANALYSIS THRESHOLDS
# =============================================================================


class Thresholds:
    """Configuration class for analysis thresholds."""

    # Batting thresholds
    MIN_RUNS_SEASON = 150  # Minimum runs per season for top scorers
    MIN_RUNS_EVOLUTION = 100  # Minimum runs for SR evolution analysis
    MIN_RUNS_CAREER = 500  # Minimum career runs for key batter analysis
    MIN_RUNS_VENUE = 100  # Minimum runs for venue specialist

    # Bowling thresholds
    MIN_WICKETS_SEASON = 5  # Minimum wickets per season for top wicket takers
    MIN_WICKETS_CAREER = 30  # Minimum career wickets for key bowler analysis
    MIN_WICKETS_VENUE = 5  # Minimum wickets for venue specialist
    MIN_OVERS_DEATH = 10  # Minimum death overs for specialist analysis

    # Form trajectory thresholds
    RUNS_DIFF_TRENDING = 50  # Minimum runs difference for trending
    SR_DIFF_TRENDING = 10  # Minimum SR difference for trending

    # Venue analysis
    MIN_VENUE_MATCHES = 2  # Minimum matches for away venue stats
    MIN_VENUE_MATCHES_PITCH = 5  # Minimum matches for pitch characteristics

    # Phase performance
    POWERPLAY_SR_THRESHOLD = 130  # Minimum SR for powerplay hitters
    ECONOMY_DEATH_BEAST = 8.5  # Economy threshold for death specialists
    ECONOMY_SPIN_FRIENDLY = 5  # Pitch bias threshold

    # Spin bowling thresholds (TKT-051)
    SPIN_PP_BEAST_ECON = 6.5
    SPIN_PP_LIABILITY_ECON = 9.0
    SPIN_MID_BEAST_ECON = 6.5
    SPIN_MID_LIABILITY_ECON = 8.5
    SPIN_DEATH_BEAST_ECON = 8.0
    SPIN_DEATH_LIABILITY_ECON = 11.0

    # Pitch bias classification (TKT-051)
    PITCH_BIAS_DIFFERENTIAL = 5.0  # SR difference for spin/pace classification
    MIN_SPIN_BALLS_VENUE = 200  # Minimum spin deliveries for venue bias
    MIN_PACE_BALLS_VENUE = 200  # Minimum pace deliveries for venue bias

    # Vulnerability thresholds
    SPIN_VULNERABILITY_SR = 110  # SR below this indicates spin vulnerability
    SPIN_VULNERABILITY_AVG = 12  # Average below this indicates vulnerability
    SPIN_VULNERABILITY_BPD = 12  # Balls per dismissal below this


# =============================================================================
# LEAGUE BENCHMARKS (IPL 2023-2025)
# =============================================================================

LEAGUE_BENCHMARKS = {
    "batting": {
        "powerplay": {"sr": 146.34, "avg": 36.38, "boundary_pct": 24.25, "dot_pct": 44.02},
        "middle": {"sr": 140.26, "avg": 31.02, "boundary_pct": 16.80, "dot_pct": 30.51},
        "death": {"sr": 170.22, "avg": 22.58, "boundary_pct": 23.39, "dot_pct": 30.25},
    },
    "bowling": {
        "powerplay": {"economy": 9.26, "avg": 38.35, "sr": 24.86, "dot_pct": 42.21},
        "middle": {"economy": 8.76, "avg": 32.29, "sr": 22.12, "dot_pct": 29.32},
        "death": {"economy": 10.87, "avg": 24.03, "sr": 13.27, "dot_pct": 28.06},
    },
    "vs_bowling_type": {
        "Fast": {"sr": 151.12, "avg": 27.26, "boundary_pct": 22.47},
        "Right-arm off-spin": {"sr": 137.79, "avg": 34.02, "boundary_pct": 15.97},
        "Right-arm leg-spin": {"sr": 142.81, "avg": 26.89, "boundary_pct": 17.16},
        "Left-arm orthodox": {"sr": 138.65, "avg": 33.49, "boundary_pct": 16.91},
        "Left-arm wrist spin": {"sr": 127.62, "avg": 23.83, "boundary_pct": 13.96},
    },
}

# Pace bowling types for filtering
PACE_BOWLING_TYPES = ("Fast", "Medium")
# Spin bowling types for filtering
SPIN_BOWLING_TYPES = ("Off-spin", "Leg-spin", "Left-arm orthodox", "Left-arm wrist spin")
# Pace bowler types for batter-vs-type aggregation (from batter_vs_bowler_type view)
PACE_BATTER_VS_TYPES = ("Fast", "Right-arm pace", "Left-arm pace", "Medium")
# Spin bowler types for batter-vs-type aggregation (from batter_vs_bowler_type view)
SPIN_BATTER_VS_TYPES = (
    "Right-arm off-spin",
    "Right-arm leg-spin",
    "Left-arm orthodox",
    "Left-arm wrist spin",
    "Off-spin",
    "Leg-spin",
)


# =============================================================================
# PLAYER TAGS MANAGEMENT
# =============================================================================


def load_player_tags() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load player tags from JSON file.

    Returns:
        Dict containing 'batters' and 'bowlers' lists with player tag data.
        Returns empty lists if file not found.
    """
    if not PLAYER_TAGS_PATH.exists():
        logger.warning("Player tags file not found at %s", PLAYER_TAGS_PATH)
        return {"batters": [], "bowlers": []}

    try:
        with open(PLAYER_TAGS_PATH) as f:
            data = json.load(f)
            logger.debug(
                "Loaded player tags: %d batters, %d bowlers",
                len(data.get("batters", [])),
                len(data.get("bowlers", [])),
            )
            return data
    except json.JSONDecodeError as e:
        logger.error("Failed to parse player tags JSON: %s", e)
        return {"batters": [], "bowlers": []}


def _extract_cluster_from_tags(tags: List[str], cluster_set: frozenset) -> str:
    """
    Extract the first matching cluster tag from a list of tags.

    Args:
        tags: List of player tags
        cluster_set: Set of valid cluster names to match against

    Returns:
        The matching cluster name or empty string if none found
    """
    for tag in tags:
        if tag in cluster_set:
            return tag
    return ""


def get_player_tags_lookup(tags_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    """
    Create lookup dictionary from player_id to tags.

    Merges batter and bowler tags for all-rounders into single entries.

    Args:
        tags_data: Dict with 'batters' and 'bowlers' lists from player_tags.json

    Returns:
        Dict mapping player_id to {'cluster': str, 'tags': List[str], 'bowler_cluster': str}
    """
    lookup: Dict[str, Dict[str, Any]] = {}

    # Process batters
    for batter in tags_data.get("batters", []):
        player_id = batter.get("player_id")
        if not player_id:
            continue

        tags = batter.get("tags", [])
        cluster = _extract_cluster_from_tags(tags, BATTER_CLUSTERS)
        lookup[player_id] = {"cluster": cluster, "tags": tags}

    # Process bowlers (merge with existing batter entries for all-rounders)
    for bowler in tags_data.get("bowlers", []):
        player_id = bowler.get("player_id")
        if not player_id:
            continue

        tags = bowler.get("tags", [])
        cluster = _extract_cluster_from_tags(tags, BOWLER_CLUSTERS)

        if player_id in lookup:
            # Merge bowler tags into existing entry (all-rounder)
            lookup[player_id]["tags"].extend(tags)
            if not lookup[player_id]["cluster"] and cluster:
                lookup[player_id]["bowler_cluster"] = cluster
        else:
            lookup[player_id] = {"cluster": cluster, "tags": tags}

    return lookup


# =============================================================================
# FRANCHISE AND TEAM CONFIGURATION
# =============================================================================

# Franchise name mappings for historical data
FRANCHISE_ALIASES = {
    "Delhi Capitals": ["Delhi Capitals", "Delhi Daredevils"],
    "Punjab Kings": ["Punjab Kings", "Kings XI Punjab"],
    "Royal Challengers Bengaluru": [
        "Royal Challengers Bengaluru",
        "Royal Challengers Bangalore",
    ],
    "Chennai Super Kings": ["Chennai Super Kings"],
    "Mumbai Indians": ["Mumbai Indians"],
    "Kolkata Knight Riders": ["Kolkata Knight Riders"],
    "Rajasthan Royals": ["Rajasthan Royals"],
    "Sunrisers Hyderabad": ["Sunrisers Hyderabad"],
    "Gujarat Titans": ["Gujarat Titans"],
    "Lucknow Super Giants": ["Lucknow Super Giants"],
}

# Team short codes
TEAM_CODES = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
}

# Home venue mappings for each IPL team
# Note: Some teams have moved venues over the years, these are current (2023+) home grounds
TEAM_HOME_VENUES = {
    "Chennai Super Kings": ["MA Chidambaram Stadium, Chepauk, Chennai"],
    "Mumbai Indians": ["Wankhede Stadium, Mumbai"],
    "Royal Challengers Bengaluru": ["M Chinnaswamy Stadium, Bengaluru"],
    "Kolkata Knight Riders": ["Eden Gardens, Kolkata"],
    "Delhi Capitals": ["Arun Jaitley Stadium, Delhi"],
    "Punjab Kings": [
        "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
    ],
    "Rajasthan Royals": ["Sawai Mansingh Stadium, Jaipur"],
    "Sunrisers Hyderabad": ["Rajiv Gandhi International Stadium, Uppal, Hyderabad"],
    "Gujarat Titans": ["Narendra Modi Stadium, Ahmedabad"],
    "Lucknow Super Giants": [
        "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"
    ],
}


# =============================================================================
# SQL CLAUSE BUILDERS
# =============================================================================


def build_sql_in_clause(values: List[str]) -> str:
    """
    Build a SQL IN clause from a list of string values.

    Args:
        values: List of string values to include in IN clause

    Returns:
        SQL-formatted string like "'value1', 'value2', 'value3'"
    """
    return ", ".join([f"'{v}'" for v in values])


def get_team_alias_clause(team_name: str) -> str:
    """
    Generate SQL IN clause for a team including historical aliases.

    Args:
        team_name: Current team name (e.g., "Delhi Capitals")

    Returns:
        SQL IN clause string including all aliases
    """
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    return build_sql_in_clause(aliases)


def get_home_venue_clause(team_name: str) -> str:
    """
    Generate SQL IN clause for a team's home venues.

    Args:
        team_name: Team name

    Returns:
        SQL IN clause string for home venues, or "''" if none found
    """
    home_venues = TEAM_HOME_VENUES.get(team_name, [])
    return build_sql_in_clause(home_venues) if home_venues else "''"


def get_opposition_clause(team_name: str) -> str:
    """
    Generate SQL IN clause for opposition team names (handles aliases).

    Args:
        team_name: Opposition team name

    Returns:
        SQL IN clause for all aliases of the opposition team
    """
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    return build_sql_in_clause(aliases)


# =============================================================================
# DATABASE QUERY HELPERS
# =============================================================================


def execute_query_safe(
    conn: duckdb.DuckDBPyConnection, query: str, default: Any = None, fetch_one: bool = False
) -> Any:
    """
    Execute a SQL query with error handling.

    Args:
        conn: DuckDB connection
        query: SQL query string
        default: Default value to return on error
        fetch_one: If True, fetch single row; otherwise fetch all

    Returns:
        Query result or default value on error
    """
    try:
        result = conn.execute(query)
        return result.fetchone() if fetch_one else result.fetchall()
    except Exception as e:
        logger.warning("Query execution failed: %s", str(e)[:100])
        return default


# =============================================================================
# MARKDOWN TABLE HELPERS
# =============================================================================


def format_stat(value: Any, default: str = "-") -> str:
    """
    Format a statistic value for display.

    Args:
        value: The value to format
        default: Default string if value is None or falsy

    Returns:
        Formatted string representation
    """
    if value is None:
        return default
    if isinstance(value, float):
        if value == int(value):
            return str(int(value))
        return f"{value:.1f}" if abs(value) < 100 else f"{value:.0f}"
    return str(value) if value else default


def truncate_venue_name(venue: str, max_length: int = 35) -> str:
    """
    Truncate venue name for table display.

    Args:
        venue: Full venue name
        max_length: Maximum characters to display

    Returns:
        Truncated venue name (city portion if comma-separated)
    """
    if not venue:
        return "-"
    # Take first part before comma (usually city/stadium name)
    short = venue.split(",")[0]
    if len(short) > max_length:
        return short[: max_length - 3] + "..."
    return short


def determine_trend(values: List[float], threshold: float = 5.0) -> str:
    """
    Determine trend direction from a list of values.

    Args:
        values: List of numeric values (chronological order)
        threshold: Minimum difference for UP/DOWN classification

    Returns:
        "UP", "DOWN", "STEADY", or "-" if insufficient data
    """
    # Filter out None/invalid values
    valid_values = [v for v in values if v is not None and v != "-"]
    if len(valid_values) < 2:
        return "-"

    diff = valid_values[-1] - valid_values[0]
    if diff > threshold:
        return "UP"
    elif diff < -threshold:
        return "DOWN"
    return "STEADY"


def determine_economy_trend(values: List[Tuple[float, int]], threshold: float = 0.5) -> str:
    """
    Determine economy rate trend (lower is better for bowling).

    Args:
        values: List of (economy, wickets) tuples
        threshold: Minimum difference for IMPROVING/DECLINING

    Returns:
        "IMPROVING", "DECLINING", "STEADY", or "-"
    """
    valid_values = [v[0] for v in values if v[0] is not None and v[0] != "-"]
    if len(valid_values) < 2:
        return "-"

    diff = valid_values[-1] - valid_values[0]
    if diff < -threshold:
        return "IMPROVING"
    elif diff > threshold:
        return "DECLINING"
    return "STEADY"


def get_playoff_status(stage: Optional[str]) -> str:
    """
    Convert playoff stage to display abbreviation.

    Args:
        stage: Playoff stage from database (e.g., "Final", "Qualifier 1")

    Returns:
        Abbreviated status string
    """
    if not stage:
        return "No"

    stage_map = {
        "Final": "Final",
        "Qualifier 1": "Q1",
        "Qualifier 2": "Q2",
        "Eliminator": "Elim",
    }
    return stage_map.get(stage, stage[:4] if len(stage) > 4 else stage)


def _get_season_match_stats(
    conn: duckdb.DuckDBPyConnection, season: str, alias_clause: str
) -> Tuple[int, int, int]:
    """
    Get match statistics for a team in a specific season.

    Args:
        conn: Database connection
        season: Season year (e.g., "2023")
        alias_clause: SQL IN clause for team aliases

    Returns:
        Tuple of (matches, wins, losses)
    """
    query = f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, dm.season, dm.stage, dt1.team_name as team1, dt2.team_name as team2,
                   dtw.team_name as winner
            FROM dim_match dm
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
            JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
            LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.season = '{season}'
        )
        SELECT
            COUNT(*) as matches,
            SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN winner IS NOT NULL AND winner NOT IN ({alias_clause}) THEN 1 ELSE 0 END) as losses
        FROM ipl_matches
        WHERE team1 IN ({alias_clause}) OR team2 IN ({alias_clause})
    """
    result = execute_query_safe(conn, query, default=(0, 0, 0), fetch_one=True)
    return (result[0] or 0, result[1] or 0, result[2] or 0) if result else (0, 0, 0)


def _get_season_avg_score(
    conn: duckdb.DuckDBPyConnection, season: str, alias_clause: str
) -> Optional[float]:
    """
    Get average innings score for a team in a specific season.

    Args:
        conn: Database connection
        season: Season year
        alias_clause: SQL IN clause for team aliases

    Returns:
        Average score or None if no data
    """
    query = f"""
        WITH innings_scores AS (
            SELECT dm.season, dt.team_name,
                   SUM(fb.total_runs) as innings_runs
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dt ON fb.batting_team_id = dt.team_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.season = '{season}'
              AND dt.team_name IN ({alias_clause})
            GROUP BY dm.season, dm.match_id, fb.innings, dt.team_name
        )
        SELECT ROUND(AVG(innings_runs), 1) as avg_score
        FROM innings_scores
    """
    result = execute_query_safe(conn, query, fetch_one=True)
    return result[0] if result and result[0] else None


def _get_season_playoff_status(
    conn: duckdb.DuckDBPyConnection, season: str, alias_clause: str
) -> str:
    """
    Get playoff status for a team in a specific season.

    Args:
        conn: Database connection
        season: Season year
        alias_clause: SQL IN clause for team aliases

    Returns:
        Playoff status string (e.g., "Final", "Q1", "No")
    """
    query = f"""
        SELECT dm.stage
        FROM dim_match dm
        JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
        JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
        JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
        WHERE dtr.tournament_name = 'Indian Premier League'
          AND dm.season = '{season}'
          AND dm.stage != 'None'
          AND (dt1.team_name IN ({alias_clause}) OR dt2.team_name IN ({alias_clause}))
        ORDER BY CASE dm.stage
            WHEN 'Final' THEN 4
            WHEN 'Qualifier 2' THEN 3
            WHEN 'Qualifier 1' THEN 2
            WHEN 'Eliminator' THEN 1
        END DESC
        LIMIT 1
    """
    result = execute_query_safe(conn, query, fetch_one=True)
    return get_playoff_status(result[0] if result else None)


def _generate_season_performance_table(
    conn: duckdb.DuckDBPyConnection, alias_clause: str, seasons: List[str]
) -> List[str]:
    """
    Generate the season performance summary table.

    Args:
        conn: Database connection
        alias_clause: SQL IN clause for team aliases
        seasons: List of seasons to include

    Returns:
        List of markdown lines for the table
    """
    md = ["### Season Performance\n"]

    season_data = []
    for season in seasons:
        matches, wins, losses = _get_season_match_stats(conn, season, alias_clause)
        avg_score = _get_season_avg_score(conn, season, alias_clause)
        playoff_status = _get_season_playoff_status(conn, season, alias_clause)

        win_pct = round(wins * 100 / matches, 1) if matches > 0 else 0
        avg_score_str = format_stat(avg_score)

        season_data.append((season, matches, wins, losses, win_pct, avg_score_str, playoff_status))

    md.append("| Season | Matches | Wins | Losses | Win% | Avg Score | Playoff |")
    md.append("|--------|---------|------|--------|------|-----------|---------|")
    for row in season_data:
        season, matches, wins, losses, win_pct, avg_score, playoff = row
        md.append(
            f"| {season} | {matches} | {wins} | {losses} | {win_pct}% | {avg_score} | {playoff} |"
        )

    md.append("")
    return md


def _generate_batting_trends(
    conn: duckdb.DuckDBPyConnection, team_name: str, alias_clause: str, seasons: List[str]
) -> List[str]:
    """
    Generate batting trends subsection for historical trends.

    Args:
        conn: Database connection
        team_name: Full team name
        alias_clause: SQL IN clause for team aliases
        seasons: List of seasons to analyze

    Returns:
        List of markdown lines for batting trends
    """
    md = ["### Batting Trends\n", "**Top Run Scorers by Season:**\n"]

    # Top run scorers by season
    for season in seasons:
        query = f"""
            WITH season_batting AS (
                SELECT dm.season, dp.current_name as player_name,
                       COUNT(DISTINCT fb.match_id) as innings,
                       SUM(fb.batter_runs) as runs,
                       COUNT(*) as balls_faced
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_team dt ON fb.batting_team_id = dt.team_id
                JOIN dim_player dp ON fb.batter_id = dp.player_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.season = '{season}'
                  AND dt.team_name IN ({alias_clause})
                GROUP BY dm.season, dp.current_name
            )
            SELECT player_name, runs, innings,
                   ROUND(runs * 100.0 / NULLIF(balls_faced, 0), 1) as sr
            FROM season_batting
            WHERE runs >= {Thresholds.MIN_RUNS_SEASON}
            ORDER BY runs DESC
            LIMIT 3
        """
        batters = execute_query_safe(conn, query, default=[])

        if batters:
            batter_str = ", ".join([f"{b[0]} ({b[1]} @ {b[3]})" for b in batters])
            md.append(f"- **{season}:** {batter_str}")

    md.append("")

    # Strike rate evolution for key players
    md.append("**Strike Rate Evolution (Key Batters):**\n")

    sr_query = f"""
        WITH season_batting AS (
            SELECT dm.season, dp.current_name as player_name, dp.player_id,
                   SUM(fb.batter_runs) as runs,
                   COUNT(*) as balls_faced
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dt ON fb.batting_team_id = dt.team_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.season IN ('2023', '2024', '2025')
              AND dt.team_name IN ({alias_clause})
            GROUP BY dm.season, dp.current_name, dp.player_id
            HAVING SUM(fb.batter_runs) >= {Thresholds.MIN_RUNS_EVOLUTION}
        ),
        player_seasons AS (
            SELECT player_name, player_id, COUNT(DISTINCT season) as seasons_played
            FROM season_batting
            GROUP BY player_name, player_id
            HAVING COUNT(DISTINCT season) >= 2
        )
        SELECT sb.player_name, sb.season,
               ROUND(sb.runs * 100.0 / NULLIF(sb.balls_faced, 0), 1) as sr
        FROM season_batting sb
        JOIN player_seasons ps ON sb.player_id = ps.player_id
        JOIN ipl_2026_squads sq ON sb.player_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
        ORDER BY sb.player_name, sb.season
    """
    sr_evolution = execute_query_safe(conn, sr_query, default=[])

    if sr_evolution:
        # Group by player
        player_sr: Dict[str, Dict[str, float]] = {}
        for player, season, sr in sr_evolution:
            if player not in player_sr:
                player_sr[player] = {}
            player_sr[player][season] = sr

        md.append("| Player | 2023 | 2024 | 2025 | Trend |")
        md.append("|--------|------|------|------|-------|")
        for player, seasons_sr in player_sr.items():
            sr_2023 = seasons_sr.get("2023", "-")
            sr_2024 = seasons_sr.get("2024", "-")
            sr_2025 = seasons_sr.get("2025", "-")

            trend = determine_trend(
                [sr_2023, sr_2024, sr_2025], threshold=Thresholds.SR_DIFF_TRENDING / 2
            )
            md.append(f"| {player} | {sr_2023} | {sr_2024} | {sr_2025} | {trend} |")

    md.append("")
    return md


def _generate_bowling_trends(
    conn: duckdb.DuckDBPyConnection, team_name: str, alias_clause: str, seasons: List[str]
) -> List[str]:
    """
    Generate bowling trends subsection for historical trends.

    Args:
        conn: Database connection
        team_name: Full team name
        alias_clause: SQL IN clause for team aliases
        seasons: List of seasons to analyze

    Returns:
        List of markdown lines for bowling trends
    """
    md = ["### Bowling Trends\n", "**Top Wicket Takers by Season:**\n"]

    for season in seasons:
        query = f"""
            WITH season_bowling AS (
                SELECT dm.season, dp.current_name as player_name,
                       COUNT(DISTINCT fb.match_id) as matches,
                       COUNT(*) as balls,
                       SUM(fb.total_runs) as runs,
                       SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_team dt ON fb.bowling_team_id = dt.team_id
                JOIN dim_player dp ON fb.bowler_id = dp.player_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.season = '{season}'
                  AND dt.team_name IN ({alias_clause})
                GROUP BY dm.season, dp.current_name
            )
            SELECT player_name, wickets, matches,
                   ROUND(runs * 6.0 / NULLIF(balls, 0), 2) as economy
            FROM season_bowling
            WHERE wickets >= {Thresholds.MIN_WICKETS_SEASON}
            ORDER BY wickets DESC
            LIMIT 3
        """
        bowlers = execute_query_safe(conn, query, default=[])

        if bowlers:
            bowler_str = ", ".join([f"{b[0]} ({b[1]}w @ {b[3]})" for b in bowlers])
            md.append(f"- **{season}:** {bowler_str}")

    md.append("")

    # Economy rate evolution for key bowlers
    md.append("**Economy Rate Evolution (Key Bowlers):**\n")

    econ_query = f"""
        WITH season_bowling AS (
            SELECT dm.season, dp.current_name as player_name, dp.player_id,
                   COUNT(*) as balls,
                   SUM(fb.total_runs) as runs,
                   SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dt ON fb.bowling_team_id = dt.team_id
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.season IN ('2023', '2024', '2025')
              AND dt.team_name IN ({alias_clause})
            GROUP BY dm.season, dp.current_name, dp.player_id
            HAVING SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) >= {Thresholds.MIN_WICKETS_SEASON}
        ),
        player_seasons AS (
            SELECT player_name, player_id, COUNT(DISTINCT season) as seasons_played
            FROM season_bowling
            GROUP BY player_name, player_id
            HAVING COUNT(DISTINCT season) >= 2
        )
        SELECT sb.player_name, sb.season,
               ROUND(sb.runs * 6.0 / NULLIF(sb.balls, 0), 2) as economy,
               sb.wickets
        FROM season_bowling sb
        JOIN player_seasons ps ON sb.player_id = ps.player_id
        JOIN ipl_2026_squads sq ON sb.player_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
        ORDER BY sb.player_name, sb.season
    """
    econ_evolution = execute_query_safe(conn, econ_query, default=[])

    if econ_evolution:
        # Group by player
        player_econ: Dict[str, Dict[str, Tuple[float, int]]] = {}
        for player, season, econ, wkts in econ_evolution:
            if player not in player_econ:
                player_econ[player] = {}
            player_econ[player][season] = (econ, wkts)

        md.append("| Player | 2023 | 2024 | 2025 | Trend |")
        md.append("|--------|------|------|------|-------|")
        for player, seasons_econ in player_econ.items():
            e_2023 = seasons_econ.get("2023", ("-", 0))
            e_2024 = seasons_econ.get("2024", ("-", 0))
            e_2025 = seasons_econ.get("2025", ("-", 0))

            trend = determine_economy_trend([e_2023, e_2024, e_2025])

            e23_str = format_stat(e_2023[0]) if e_2023[0] != "-" else "-"
            e24_str = format_stat(e_2024[0]) if e_2024[0] != "-" else "-"
            e25_str = format_stat(e_2025[0]) if e_2025[0] != "-" else "-"
            md.append(f"| {player} | {e23_str} | {e24_str} | {e25_str} | {trend} |")

    md.append("")
    return md


def _generate_form_trajectory(
    conn: duckdb.DuckDBPyConnection, team_name: str, alias_clause: str
) -> List[str]:
    """
    Generate form trajectory subsection comparing 2024 vs 2025 performance.

    Args:
        conn: Database connection
        team_name: Full team name
        alias_clause: SQL IN clause for team aliases

    Returns:
        List of markdown lines for form trajectory
    """
    md = [
        "### Form Trajectory\n",
        "*Players trending up/down based on 2024-2025 performance comparison*\n",
    ]

    # Common CTE for season batting comparison
    base_query = f"""
        WITH season_batting AS (
            SELECT dm.season, dp.current_name as player_name, dp.player_id,
                   SUM(fb.batter_runs) as runs,
                   COUNT(*) as balls,
                   ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 1) as sr
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dt ON fb.batting_team_id = dt.team_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.season IN ('2024', '2025')
              AND dt.team_name IN ({alias_clause})
            GROUP BY dm.season, dp.current_name, dp.player_id
            HAVING SUM(fb.batter_runs) >= {Thresholds.MIN_RUNS_EVOLUTION}
        ),
        comparison AS (
            SELECT
                s25.player_name,
                s24.runs as runs_2024, s25.runs as runs_2025,
                s24.sr as sr_2024, s25.sr as sr_2025,
                (s25.runs - s24.runs) as runs_diff,
                (s25.sr - s24.sr) as sr_diff
            FROM season_batting s25
            JOIN season_batting s24 ON s25.player_id = s24.player_id
            JOIN ipl_2026_squads sq ON s25.player_id = sq.player_id
            WHERE s25.season = '2025' AND s24.season = '2024'
              AND sq.team_name = '{team_name}'
        )
    """

    # Trending UP
    trending_up = execute_query_safe(
        conn,
        base_query
        + f"""
            SELECT player_name, runs_2024, runs_2025, sr_2024, sr_2025, runs_diff, sr_diff
            FROM comparison
            WHERE runs_diff > {Thresholds.RUNS_DIFF_TRENDING} OR sr_diff > {Thresholds.SR_DIFF_TRENDING}
            ORDER BY runs_diff DESC
            LIMIT 3
        """,
        default=[],
    )

    if trending_up:
        md.append("**Trending UP:**")
        for player, r24, r25, sr24, sr25, r_diff, sr_diff in trending_up:
            reasons = []
            if r_diff > Thresholds.RUNS_DIFF_TRENDING:
                reasons.append(f"+{r_diff} runs")
            if sr_diff > Thresholds.SR_DIFF_TRENDING:
                reasons.append(f"+{sr_diff:.1f} SR")
            md.append(
                f"- {player}: {', '.join(reasons)} (2024: {r24} @ {sr24} -> 2025: {r25} @ {sr25})"
            )
        md.append("")

    # Trending DOWN
    trending_down = execute_query_safe(
        conn,
        base_query
        + f"""
            SELECT player_name, runs_2024, runs_2025, sr_2024, sr_2025, runs_diff, sr_diff
            FROM comparison
            WHERE runs_diff < -{Thresholds.RUNS_DIFF_TRENDING} OR sr_diff < -{Thresholds.SR_DIFF_TRENDING}
            ORDER BY runs_diff ASC
            LIMIT 3
        """,
        default=[],
    )

    if trending_down:
        md.append("**Trending DOWN:**")
        for player, r24, r25, sr24, sr25, r_diff, sr_diff in trending_down:
            reasons = []
            if r_diff < -Thresholds.RUNS_DIFF_TRENDING:
                reasons.append(f"{r_diff} runs")
            if sr_diff < -Thresholds.SR_DIFF_TRENDING:
                reasons.append(f"{sr_diff:.1f} SR")
            md.append(
                f"- {player}: {', '.join(reasons)} (2024: {r24} @ {sr24} -> 2025: {r25} @ {sr25})"
            )
        md.append("")

    if not trending_up and not trending_down:
        md.append("*Insufficient multi-season data for form trajectory analysis*\n")

    return md


def generate_historical_trends(
    conn: duckdb.DuckDBPyConnection, team_name: str, alias_clause: str
) -> List[str]:
    """
    Generate historical trends section showing season-over-season performance.

    Covers IPL seasons 2023-2025 and includes:
    - Season performance summary (matches, wins, win%, avg score, playoff status)
    - Batting trends (top run scorers, strike rate evolution)
    - Bowling trends (top wicket takers, economy rate changes)
    - Form trajectory (players trending up/down)

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")
        alias_clause: SQL IN clause for team historical aliases

    Returns:
        List of markdown-formatted strings for the historical trends section
    """
    md = []
    md.append("## 3. Historical Trends (2023-2025)\n")
    md.append("*Season-over-season performance analysis (IPL 2023-2025)*\n")

    seasons = ["2023", "2024", "2025"]

    # Season Performance Summary
    md.extend(_generate_season_performance_table(conn, alias_clause, seasons))

    # Batting Trends
    md.extend(_generate_batting_trends(conn, team_name, alias_clause, seasons))

    # Bowling Trends
    md.extend(_generate_bowling_trends(conn, team_name, alias_clause, seasons))

    # Form Trajectory
    md.extend(_generate_form_trajectory(conn, team_name, alias_clause))

    # Add limitations note
    md.append("---")
    md.append(
        "*Note: Historical trends limited to IPL 2023-2025 data. Some players may not have data across all seasons due to team changes or limited playing time.*\n"
    )

    return md


def _classify_pp_approach(sr: float, boundary_pct: float) -> str:
    """Classify powerplay approach from SR and boundary%."""
    if sr > 145 and boundary_pct > 20:
        return "All-Out Attack"
    if sr > 135:
        return "Aggressive"
    if sr >= 125:
        return "Balanced"
    return "Conservative"


def _classify_middle_style(sr: float) -> str:
    """Classify middle overs style from SR."""
    if sr > 145:
        return "Accelerating"
    if sr >= 130:
        return "Steady"
    return "Consolidating"


def _classify_death_batting(sr: float) -> str:
    """Classify death batting from SR."""
    if sr > 175:
        return "Explosive"
    if sr >= 155:
        return "Strong"
    return "Average"


def _classify_death_bowling(economy: float) -> str:
    """Classify death bowling from economy."""
    if economy < 9.5:
        return "Elite"
    if economy <= 11.0:
        return "Good"
    return "Vulnerable"


def _classify_lineup_balance(top_pct: float) -> str:
    """Classify lineup balance from top-3 contribution%."""
    if top_pct > 50:
        return "Top-Heavy"
    if top_pct >= 40:
        return "Balanced"
    return "Deep Lineup"


def _trend_arrow(vals: list) -> str:
    """Return trend arrow based on values progression."""
    if len(vals) < 2:
        return ""
    diff = vals[-1] - vals[0]
    if diff > 5:
        return " ↑↑"
    if diff > 1:
        return " ↑"
    if diff < -5:
        return " ↓↓"
    if diff < -1:
        return " ↓"
    return " →"


def generate_team_phase_approach(
    conn: duckdb.DuckDBPyConnection, team_name: str, alias_clause: str
) -> List[str]:
    """
    Generate team-level phase approach analysis (TKT-052 / Item 3).

    Shows how the team approaches powerplay, middle, and death overs
    with 2023-2025 trends, plus batting order balance assessment.
    """
    md = []
    md.append("## 3.5 Team Phase Approach (2023-2025)\n")
    md.append("*How the team approaches each phase of the game — strategy DNA across seasons*\n")

    # --- Powerplay Batting ---
    md.append("### Powerplay DNA (Batting)\n")
    query = f"""
        SELECT season, strike_rate, boundary_pct, dot_ball_pct, wickets_lost, run_rate, matches
        FROM analytics_ipl_team_phase_batting_since2023
        WHERE batting_team IN ({alias_clause})
          AND match_phase = 'powerplay'
        ORDER BY season
    """
    rows = execute_query_safe(conn, query)
    if rows:
        md.append("| Season | SR | Boundary% | Dot% | Wkts Lost | RR | Approach |")
        md.append("|--------|-----|-----------|------|-----------|------|----------|")
        srs = []
        for r in rows:
            season, sr, bpct, dpct, wkts, rr, matches = r
            approach = _classify_pp_approach(sr, bpct)
            srs.append(sr)
            wkts_per = round(wkts / matches, 1) if matches else 0
            md.append(
                f"| {season} | {sr:.1f} | {bpct:.1f}% | {dpct:.1f}% | {wkts_per}/inn | {rr:.2f} | {approach}{_trend_arrow(srs)} |"
            )
        md.append("")

    # --- Middle Overs Batting ---
    md.append("### Middle Overs Identity (Batting)\n")
    query = f"""
        SELECT season, strike_rate, boundary_pct, dot_ball_pct, wickets_lost, run_rate, matches
        FROM analytics_ipl_team_phase_batting_since2023
        WHERE batting_team IN ({alias_clause})
          AND match_phase = 'middle'
        ORDER BY season
    """
    rows = execute_query_safe(conn, query)
    if rows:
        md.append("| Season | SR | Boundary% | Dot% | Wkts Lost | RR | Style |")
        md.append("|--------|-----|-----------|------|-----------|------|-------|")
        srs = []
        for r in rows:
            season, sr, bpct, dpct, wkts, rr, matches = r
            style = _classify_middle_style(sr)
            srs.append(sr)
            wkts_per = round(wkts / matches, 1) if matches else 0
            md.append(
                f"| {season} | {sr:.1f} | {bpct:.1f}% | {dpct:.1f}% | {wkts_per}/inn | {rr:.2f} | {style}{_trend_arrow(srs)} |"
            )
        md.append("")

    # --- Death Overs Batting ---
    md.append("### Death Overs Execution (Batting)\n")
    query = f"""
        SELECT season, strike_rate, boundary_pct, dot_ball_pct, wickets_lost, run_rate, matches
        FROM analytics_ipl_team_phase_batting_since2023
        WHERE batting_team IN ({alias_clause})
          AND match_phase = 'death'
        ORDER BY season
    """
    rows = execute_query_safe(conn, query)
    if rows:
        md.append("| Season | SR | Boundary% | Dot% | Wkts Lost | RR | Rating |")
        md.append("|--------|-----|-----------|------|-----------|------|--------|")
        srs = []
        for r in rows:
            season, sr, bpct, dpct, wkts, rr, matches = r
            rating = _classify_death_batting(sr)
            srs.append(sr)
            wkts_per = round(wkts / matches, 1) if matches else 0
            md.append(
                f"| {season} | {sr:.1f} | {bpct:.1f}% | {dpct:.1f}% | {wkts_per}/inn | {rr:.2f} | {rating}{_trend_arrow(srs)} |"
            )
        md.append("")

    # --- Death Overs Bowling ---
    md.append("### Death Overs Bowling\n")
    query = f"""
        SELECT season, economy, dot_ball_pct, boundary_conceded_pct, wickets_taken, matches
        FROM analytics_ipl_team_phase_bowling_since2023
        WHERE bowling_team IN ({alias_clause})
          AND match_phase = 'death'
        ORDER BY season
    """
    rows = execute_query_safe(conn, query)
    if rows:
        md.append("| Season | Economy | Dot% | Boundary Conceded% | Wkts/Match | Rating |")
        md.append("|--------|---------|------|-------------------|------------|--------|")
        econs = []
        for r in rows:
            season, econ, dpct, bcon, wkts, matches = r
            rating = _classify_death_bowling(econ)
            econs.append(econ)
            wpm = round(wkts / matches, 1) if matches else 0
            md.append(
                f"| {season} | {econ:.2f} | {dpct:.1f}% | {bcon:.1f}% | {wpm} | {rating}{_trend_arrow(econs)} |"
            )
        md.append("")

    # --- Lineup Balance ---
    md.append("### Lineup Balance\n")
    lineup_rows = []
    query = f"""
        SELECT season, order_segment, runs, balls, strike_rate
        FROM analytics_ipl_team_batting_order_since2023
        WHERE batting_team IN ({alias_clause})
        ORDER BY season,
            CASE order_segment WHEN 'top_order' THEN 1 WHEN 'middle_order' THEN 2 ELSE 3 END
    """
    lineup_rows = execute_query_safe(conn, query)
    if lineup_rows:
        md.append("| Season | Top 3 Runs% | Middle Order% | Lower Order% | Top 3 SR | Assessment |")
        md.append("|--------|------------|---------------|-------------|----------|------------|")
        # Group by season
        season_data: dict = {}
        for r in lineup_rows:
            season, segment, runs, balls, sr = r
            if season not in season_data:
                season_data[season] = {}
            season_data[season][segment] = {"runs": runs or 0, "sr": sr or 0}

        top_pcts = []
        for season in sorted(season_data.keys()):
            d = season_data[season]
            total = sum(seg["runs"] for seg in d.values())
            if total == 0:
                continue
            top = d.get("top_order", {}).get("runs", 0)
            mid = d.get("middle_order", {}).get("runs", 0)
            low = d.get("lower_order", {}).get("runs", 0)
            top_pct = round(top / total * 100, 1)
            mid_pct = round(mid / total * 100, 1)
            low_pct = round(low / total * 100, 1)
            top_sr = d.get("top_order", {}).get("sr", 0)
            assessment = _classify_lineup_balance(top_pct)
            top_pcts.append(top_pct)
            md.append(
                f"| {season} | {top_pct}% | {mid_pct}% | {low_pct}% | {top_sr:.1f} | {assessment}{_trend_arrow(top_pcts)} |"
            )
        md.append("")

    # --- Key Phase Players (current squad only, min sample sizes) ---
    # Minimums: 50 balls batting, 60 balls bowling (~10 overs)
    MIN_BAT_BALLS = 50
    MIN_BOWL_BALLS = 60
    md.append("### Key Phase Players (2026 Squad)\n")

    squad_filter = f"""
        JOIN ipl_2026_squads sq ON dp.player_id = sq.player_id
            AND sq.team_name = '{team_name}'
    """

    def _phase_batters(phase: str) -> list:
        return (
            execute_query_safe(
                conn,
                f"""
            SELECT dp.current_name, sq.role,
                COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
                SUM(fb.batter_runs) as runs,
                ROUND(SUM(fb.batter_runs)*100.0
                    /NULLIF(COUNT(CASE WHEN fb.is_legal_ball THEN 1 END),0),1) as sr
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dtt ON fb.batting_team_id = dtt.team_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            {squad_filter}
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '2023-01-01'
              AND dtt.team_name IN ({alias_clause})
              AND fb.match_phase = '{phase}'
            GROUP BY dp.current_name, sq.role
            HAVING COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) >= {MIN_BAT_BALLS}
            ORDER BY runs DESC LIMIT 3
            """,
            )
            or []
        )

    def _phase_bowlers(phase: str) -> list:
        return (
            execute_query_safe(
                conn,
                f"""
            SELECT dp.current_name, sq.role,
                COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) as balls,
                ROUND(SUM(fb.total_runs)*6.0
                    /NULLIF(COUNT(CASE WHEN fb.is_legal_ball THEN 1 END),0),2) as economy,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_team dtt ON fb.bowling_team_id = dtt.team_id
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            {squad_filter}
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '2023-01-01'
              AND dtt.team_name IN ({alias_clause})
              AND fb.match_phase = '{phase}'
            GROUP BY dp.current_name, sq.role
            HAVING COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) >= {MIN_BOWL_BALLS}
            ORDER BY economy ASC LIMIT 3
            """,
            )
            or []
        )

    pp_bat = _phase_batters("powerplay")
    pp_bowl = _phase_bowlers("powerplay")
    mid_bat = _phase_batters("middle")
    mid_bowl = _phase_bowlers("middle")
    death_bat = _phase_batters("death")
    death_bowl = _phase_bowlers("death")

    md.append("| Phase | Role | Player | Key Stat | Sample |")
    md.append("|-------|------|--------|----------|--------|")
    if pp_bat:
        for p in pp_bat[:2]:
            md.append(f"| Powerplay | Bat | {p[0]} | {p[3]} runs @ {p[4]} SR | {p[2]} balls |")
    if pp_bowl:
        for p in pp_bowl[:2]:
            md.append(f"| Powerplay | Bowl | {p[0]} | Econ {p[3]} ({p[4]} wkts) | {p[2]} balls |")
    if mid_bat:
        for p in mid_bat[:2]:
            md.append(f"| Middle | Bat | {p[0]} | {p[3]} runs @ {p[4]} SR | {p[2]} balls |")
    if mid_bowl:
        for p in mid_bowl[:2]:
            md.append(f"| Middle | Bowl | {p[0]} | Econ {p[3]} ({p[4]} wkts) | {p[2]} balls |")
    if death_bat:
        for p in death_bat[:2]:
            md.append(f"| Death | Bat | {p[0]} | {p[3]} runs @ {p[4]} SR | {p[2]} balls |")
    if death_bowl:
        for p in death_bowl[:2]:
            md.append(f"| Death | Bowl | {p[0]} | Econ {p[3]} ({p[4]} wkts) | {p[2]} balls |")
    md.append("")

    # --- Keys to Victory ---
    md.append("### Keys to Victory\n")
    keys = _build_keys_to_victory(
        pp_bat,
        pp_bowl,
        mid_bat,
        mid_bowl,
        death_bat,
        death_bowl,
        lineup_rows if lineup_rows else [],
    )
    for i, key in enumerate(keys, 1):
        md.append(f"{i}. {key}")
    md.append("")

    md.append("---")
    md.append(
        "*Phase approach analysis based on IPL 2023-2025 ball-by-ball data. "
        "Key players filtered to 2026 squad only.*\n"
    )

    return md


def _build_keys_to_victory(
    pp_bat: list,
    pp_bowl: list,
    mid_bat: list,
    mid_bowl: list,
    death_bat: list,
    death_bowl: list,
    lineup_rows: list,
) -> List[str]:
    """Build data-driven Keys to Victory bullets from phase data."""
    keys = []

    # PP batting key
    if pp_bat:
        top = pp_bat[0]
        keys.append(
            f"**Powerplay aggression from {top[0]}** — {top[3]} runs at {top[4]} SR "
            f"sets the tone; need early intent without reckless wicket loss."
        )

    # PP bowling key
    if pp_bowl:
        top = pp_bowl[0]
        keys.append(
            f"**{top[0]} must control the new ball** — {top[3]} economy with {top[4]} "
            f"wickets in the powerplay; early breakthroughs are non-negotiable."
        )

    # Middle overs batting key
    if mid_bat and len(mid_bat) >= 2:
        names = f"{mid_bat[0][0]} and {mid_bat[1][0]}"
        keys.append(
            f"**Middle-overs accumulation through {names}** — building partnerships "
            f"in overs 7-15 prevents middle-order collapses and sets up the death."
        )
    elif mid_bat:
        keys.append(
            f"**{mid_bat[0][0]} anchors the middle phase** — {mid_bat[0][3]} runs "
            f"at {mid_bat[0][4]} SR; needs support from the other end."
        )

    # Middle overs bowling key
    if mid_bowl:
        top = mid_bowl[0]
        keys.append(
            f"**{top[0]} must squeeze in the middle** — {top[3]} economy in overs "
            f"7-15 with {top[4]} wickets; choking run flow here builds scoreboard "
            f"pressure."
        )

    # Death batting key
    if death_bat:
        top = death_bat[0]
        keys.append(
            f"**Death hitting from {top[0]}** — {top[4]} SR in overs 16-20; "
            f"maximizing the last 5 overs is the difference between 170 and 190+."
        )

    # Death bowling key
    if death_bowl:
        top = death_bowl[0]
        if top[3] < 8.0:
            qualifier = "elite"
        elif top[3] < 10.0:
            qualifier = "strong"
        else:
            qualifier = "reliable"
        keys.append(
            f"**{top[0]}'s {qualifier} death bowling** — {top[3]} economy at the death; "
            f"defending totals requires yorker accuracy and nerve under pressure."
        )

    # Lineup balance key (from batting order data)
    if lineup_rows:
        season_data: dict = {}
        for r in lineup_rows:
            season, segment, runs, _balls, _sr = r
            if season not in season_data:
                season_data[season] = {}
            season_data[season][segment] = runs or 0
        latest = sorted(season_data.keys())[-1] if season_data else None
        if latest:
            d = season_data[latest]
            total = sum(d.values())
            if total > 0:
                top_pct = d.get("top_order", 0) / total * 100
                if top_pct > 50:
                    keys.append(
                        f"**Reduce top-order dependency** — top 3 contributed "
                        f"{top_pct:.0f}% of runs in {latest}; middle order must "
                        f"step up to avoid batting collapses if openers fail."
                    )
                elif top_pct < 35:
                    keys.append(
                        f"**Top order needs to fire** — only {top_pct:.0f}% of runs "
                        f"from top 3 in {latest}; set a platform so the middle "
                        f"order isn't always chasing."
                    )

    if not keys:
        keys.append("Insufficient data to generate data-driven keys to victory.")

    return keys


def generate_venue_analysis(
    conn: duckdb.DuckDBPyConnection, team_name: str, alias_clause: str
) -> List[str]:
    """
    Generate comprehensive venue analysis section for a team.

    Includes:
    - Home venue performance (win rate, avg score, key stats)
    - Away venue performance breakdown
    - Venue-specific pitch characteristics (pace vs spin friendly)
    - Venue specialists (players who perform best at specific venues)

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")
        alias_clause: SQL IN clause for team historical aliases

    Returns:
        List of markdown-formatted strings for the venue analysis section
    """
    md = []
    md.append("## 4. Venue Analysis\n")
    md.append("*Performance breakdown by venue (2023+ IPL data)*\n")

    home_venues = TEAM_HOME_VENUES.get(team_name, [])
    home_venue_clause = get_home_venue_clause(team_name)

    # ==========================================================================
    # HOME VENUE PERFORMANCE
    # ==========================================================================
    if home_venues:
        md.append(f"### Home Venue: {home_venues[0].split(',')[0]}\n")

        # Get home venue win rate and match stats
        home_stats = conn.execute(f"""
            WITH ipl_matches AS (
                SELECT dm.match_id, dv.venue_name, dt1.team_name as team1, dt2.team_name as team2,
                       dtw.team_name as winner
                FROM dim_match dm
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_venue dv ON dm.venue_id = dv.venue_id
                JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
                JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
                LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dv.venue_name IN ({home_venue_clause})
            )
            SELECT
                COUNT(*) as matches,
                SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN winner IS NOT NULL AND winner NOT IN ({alias_clause}) THEN 1 ELSE 0 END) as losses
            FROM ipl_matches
            WHERE team1 IN ({alias_clause}) OR team2 IN ({alias_clause})
        """).fetchone()

        if home_stats and home_stats[0] > 0:
            matches, wins, losses = home_stats
            win_pct = (wins / matches * 100) if matches > 0 else 0
            md.append(f"- **Matches:** {matches}")
            md.append(f"- **Win Rate:** {win_pct:.1f}% ({wins}W - {losses}L)")

        # Get average score at home venue
        home_avg_score = conn.execute(f"""
            WITH ipl_innings AS (
                SELECT fb.match_id, fb.innings, dv.venue_name, dt.team_name,
                       SUM(fb.total_runs) as innings_runs
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_venue dv ON dm.venue_id = dv.venue_id
                JOIN dim_team dt ON fb.batting_team_id = dt.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dv.venue_name IN ({home_venue_clause})
                GROUP BY fb.match_id, fb.innings, dv.venue_name, dt.team_name
            )
            SELECT
                COUNT(*) as innings,
                ROUND(AVG(innings_runs), 1) as avg_score,
                MAX(innings_runs) as highest,
                MIN(innings_runs) as lowest
            FROM ipl_innings
            WHERE team_name IN ({alias_clause})
        """).fetchone()

        if home_avg_score and home_avg_score[0] > 0:
            innings, avg_score, highest, lowest = home_avg_score
            md.append(f"- **Avg Score (batting):** {avg_score}")
            md.append(f"- **Highest/Lowest:** {highest}/{lowest}")

        # Get pitch characteristics at home venue
        home_pitch = conn.execute(f"""
            WITH ipl_balls AS (
                SELECT fb.*, dv.venue_name,
                       COALESCE(bc.bowling_style, 'Unknown') as bowling_style
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
                JOIN dim_venue dv ON dm.venue_id = dv.venue_id
                LEFT JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
                WHERE dt.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dv.venue_name IN ({home_venue_clause})
            )
            SELECT
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_wickets,
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_wickets,
                SUM(CASE WHEN bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_balls,
                SUM(CASE WHEN bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_balls
            FROM ipl_balls
        """).fetchone()

        if home_pitch and home_pitch[2] and home_pitch[3]:
            pace_wkts, spin_wkts, pace_balls, spin_balls = home_pitch
            pace_sr = round(pace_balls / pace_wkts, 1) if pace_wkts > 0 else 0
            spin_sr = round(spin_balls / spin_wkts, 1) if spin_wkts > 0 else 0

            # Determine pitch bias (TKT-051: use configurable differential)
            diff = Thresholds.PITCH_BIAS_DIFFERENTIAL
            if pace_sr > 0 and spin_sr > 0:
                if pace_sr < spin_sr - diff:
                    pitch_type = "Pace-friendly"
                elif spin_sr < pace_sr - diff:
                    pitch_type = "Spin-friendly"
                else:
                    pitch_type = "Balanced"
            else:
                pitch_type = "Unknown"

            md.append(f"- **Pitch Type:** {pitch_type}")
            md.append(f"- **Pace SR:** {pace_sr} | **Spin SR:** {spin_sr}")

        md.append("")

    # ==========================================================================
    # AWAY PERFORMANCE BREAKDOWN
    # ==========================================================================
    md.append("### Away Performance\n")

    away_stats = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name, dt1.team_name as team1, dt2.team_name as team2,
                   dtw.team_name as winner
            FROM dim_match dm
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
            JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
            LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '2023-01-01'
              AND dv.venue_name NOT IN ({home_venue_clause})
        ),
        venue_stats AS (
            SELECT
                venue_name,
                COUNT(*) as matches,
                SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins
            FROM ipl_matches
            WHERE team1 IN ({alias_clause}) OR team2 IN ({alias_clause})
            GROUP BY venue_name
            HAVING COUNT(*) >= 2
        ),
        venue_scores AS (
            SELECT dv.venue_name,
                   ROUND(AVG(innings_runs), 1) as avg_score
            FROM (
                SELECT fb.match_id, fb.innings, dm.venue_id,
                       SUM(fb.total_runs) as innings_runs
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_team dt ON fb.batting_team_id = dt.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dt.team_name IN ({alias_clause})
                GROUP BY fb.match_id, fb.innings, dm.venue_id
            ) innings
            JOIN dim_venue dv ON innings.venue_id = dv.venue_id
            GROUP BY dv.venue_name
        )
        SELECT vs.venue_name, vs.matches, vs.wins,
               ROUND(vs.wins * 100.0 / vs.matches, 1) as win_pct,
               COALESCE(vsc.avg_score, 0) as avg_score
        FROM venue_stats vs
        LEFT JOIN venue_scores vsc ON vs.venue_name = vsc.venue_name
        ORDER BY vs.matches DESC
        LIMIT 10
    """).fetchall()

    if away_stats:
        md.append("| Venue | Matches | Wins | Win% | Avg Score |")
        md.append("|-------|---------|------|------|-----------|")
        for row in away_stats:
            venue, matches, wins, win_pct, avg_score = row
            venue_short = venue.split(",")[0][:35]
            md.append(f"| {venue_short} | {matches} | {wins} | {win_pct}% | {avg_score or '-'} |")
    else:
        md.append("*Insufficient away match data (2023+)*")

    md.append("")

    # ==========================================================================
    # PITCH BIAS INDICATORS
    # ==========================================================================
    md.append("### Pitch Characteristics (All IPL Venues 2023+)\n")
    md.append("*Based on bowling strike rates - lower SR = more effective*\n")

    pitch_bias = conn.execute(f"""
        WITH ipl_balls AS (
            SELECT fb.*, dv.venue_name,
                   COALESCE(bc.bowling_style, 'Unknown') as bowling_style
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            LEFT JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '2023-01-01'
        ),
        venue_pitch AS (
            SELECT
                venue_name,
                COUNT(DISTINCT match_id) as matches,
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_wickets,
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_wickets,
                SUM(CASE WHEN bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_balls,
                SUM(CASE WHEN bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_balls
            FROM ipl_balls
            GROUP BY venue_name
            HAVING COUNT(DISTINCT match_id) >= 5
        )
        SELECT
            venue_name,
            matches,
            ROUND(pace_balls * 1.0 / NULLIF(pace_wickets, 0), 1) as pace_sr,
            ROUND(spin_balls * 1.0 / NULLIF(spin_wickets, 0), 1) as spin_sr,
            CASE
                WHEN pace_balls * 1.0 / NULLIF(pace_wickets, 0) < spin_balls * 1.0 / NULLIF(spin_wickets, 0) - {Thresholds.PITCH_BIAS_DIFFERENTIAL} THEN 'PACE'
                WHEN spin_balls * 1.0 / NULLIF(spin_wickets, 0) < pace_balls * 1.0 / NULLIF(pace_wickets, 0) - {Thresholds.PITCH_BIAS_DIFFERENTIAL} THEN 'SPIN'
                ELSE 'BALANCED'
            END as pitch_bias
        FROM venue_pitch
        ORDER BY matches DESC
        LIMIT 10
    """).fetchall()

    if pitch_bias:
        md.append("| Venue | Matches | Pace SR | Spin SR | Bias |")
        md.append("|-------|---------|---------|---------|------|")
        for row in pitch_bias:
            venue, matches, pace_sr, spin_sr, bias = row
            venue_short = venue.split(",")[0][:30]
            md.append(
                f"| {venue_short} | {matches} | {pace_sr or '-'} | {spin_sr or '-'} | {bias} |"
            )

    md.append("")

    # ==========================================================================
    # VENUE SPECIALISTS
    # ==========================================================================
    md.append("### Venue Specialists\n")
    md.append(
        "*Squad players with exceptional performance at specific venues (min 100 runs or 5 wickets)*\n"
    )

    # Batting specialists
    batter_specialists = conn.execute(f"""
        SELECT bv.batter_name, bv.venue, bv.innings, bv.runs, bv.strike_rate, bv.average
        FROM analytics_ipl_batter_venue_since2023 bv
        JOIN ipl_2026_squads sq ON bv.batter_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bv.runs >= 100
          AND bv.sample_size IN ('MEDIUM', 'HIGH')
          AND (bv.strike_rate >= 150 OR bv.average >= 40)
        ORDER BY bv.runs DESC
        LIMIT 8
    """).fetchall()

    if batter_specialists:
        md.append("**Top Batting Performances:**\n")
        md.append("| Player | Venue | Inn | Runs | SR | Avg |")
        md.append("|--------|-------|-----|------|-----|-----|")
        for row in batter_specialists:
            name, venue, inn, runs, sr, avg = row
            venue_short = venue.split(",")[0][:25]
            md.append(f"| {name} | {venue_short} | {inn} | {runs} | {sr or '-'} | {avg or '-'} |")
        md.append("")

    # Bowling specialists
    bowler_specialists = conn.execute(f"""
        SELECT bv.bowler_name, bv.venue, bv.matches, bv.wickets, bv.economy, bv.strike_rate
        FROM analytics_ipl_bowler_venue_since2023 bv
        JOIN ipl_2026_squads sq ON bv.bowler_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bv.wickets >= 5
          AND bv.sample_size IN ('MEDIUM', 'HIGH')
          AND (bv.economy <= 8.5 OR bv.strike_rate <= 18)
        ORDER BY bv.wickets DESC
        LIMIT 8
    """).fetchall()

    if bowler_specialists:
        md.append("**Top Bowling Performances:**\n")
        md.append("| Player | Venue | Matches | Wkts | Econ | SR |")
        md.append("|--------|-------|---------|------|------|-----|")
        for row in bowler_specialists:
            name, venue, matches, wkts, econ, sr = row
            venue_short = venue.split(",")[0][:25]
            md.append(
                f"| {name} | {venue_short} | {matches} | {wkts} | {econ or '-'} | {sr or '-'} |"
            )
        md.append("")

    if not batter_specialists and not bowler_specialists:
        md.append("*No venue specialists identified in current squad*\n")

    return md


# =============================================================================
# PRESSURE PERFORMANCE CONSTANTS
# =============================================================================

PRESSURE_BAND_ORDER = ["COMFORTABLE", "BUILDING", "HIGH", "EXTREME", "NEAR_IMPOSSIBLE"]

# Balls threshold for pressure band confidence
PRESSURE_CONFIDENCE_HIGH = 100
PRESSURE_CONFIDENCE_MEDIUM = 50

# Minimum balls for a player to appear in any pressure band table
PRESSURE_MIN_BALLS_THRESHOLD = 30


def _pressure_confidence_label(balls: int) -> str:
    """
    Derive a confidence label from ball count for pressure band data.

    Args:
        balls: Number of balls faced/bowled in a pressure band

    Returns:
        Confidence label: HIGH, MEDIUM, or LOW
    """
    if balls >= PRESSURE_CONFIDENCE_HIGH:
        return "HIGH"
    elif balls >= PRESSURE_CONFIDENCE_MEDIUM:
        return "MEDIUM"
    return "LOW"


def _generate_batting_under_pressure(conn: duckdb.DuckDBPyConnection, team_name: str) -> List[str]:
    """
    Generate Batting Under Pressure subsection.

    Shows batter performance across Required Run Rate bands (COMFORTABLE through
    NEAR_IMPOSSIBLE) for players on the team's IPL 2026 squad.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted lines for the batting pressure table
    """
    md = ["### 11.1 Batting Under Pressure\n"]
    md.append("*Performance across Required Run Rate (RRR) bands — IPL 2023+*\n")

    rows = execute_query_safe(
        conn,
        f"""
        WITH qualified AS (
            SELECT bp.player_id
            FROM analytics_ipl_batter_pressure_bands_since2023 bp
            JOIN ipl_2026_squads sq ON bp.player_id = sq.player_id
            WHERE sq.team_name = '{team_name}'
            GROUP BY bp.player_id
            HAVING MAX(bp.balls_faced) >= {PRESSURE_MIN_BALLS_THRESHOLD}
        )
        SELECT bp.player_name, bp.pressure_band, bp.balls_faced,
               bp.strike_rate, bp.batting_average, bp.boundary_pct,
               bp.dot_ball_pct, bp.entry_context
        FROM analytics_ipl_batter_pressure_bands_since2023 bp
        JOIN ipl_2026_squads sq ON bp.player_id = sq.player_id
        JOIN qualified q ON bp.player_id = q.player_id
        WHERE sq.team_name = '{team_name}'
        ORDER BY bp.player_name,
            CASE bp.pressure_band
                WHEN 'COMFORTABLE' THEN 1
                WHEN 'BUILDING' THEN 2
                WHEN 'HIGH' THEN 3
                WHEN 'EXTREME' THEN 4
                WHEN 'NEAR_IMPOSSIBLE' THEN 5
            END
        """,
        default=[],
    )

    if rows:
        md.append("| Player | Band | Balls | SR | Avg | Boundary% | Dot% | Entry | Confidence |")
        md.append("|--------|------|-------|----|-----|-----------|------|-------|------------|")
        for player, band, balls, sr, avg, bound_pct, dot_pct, entry_ctx in rows:
            confidence = _pressure_confidence_label(balls)
            entry_display = entry_ctx if entry_ctx else "-"
            md.append(
                f"| {player} | {band} | {balls} | {format_stat(sr)} | "
                f"{format_stat(avg)} | {format_stat(bound_pct)} | "
                f"{format_stat(dot_pct)} | {entry_display} | {confidence} |"
            )
    else:
        md.append("*No qualifying batting pressure data available for this squad*")

    md.append("")
    return md


def _generate_bowling_under_pressure(conn: duckdb.DuckDBPyConnection, team_name: str) -> List[str]:
    """
    Generate Bowling Under Pressure subsection.

    Shows bowler performance across Required Run Rate bands for players on the
    team's IPL 2026 squad.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted lines for the bowling pressure table
    """
    md = ["### 11.2 Bowling Under Pressure\n"]
    md.append("*Bowling performance across RRR bands — IPL 2023+*\n")

    rows = execute_query_safe(
        conn,
        f"""
        WITH qualified AS (
            SELECT bp.player_id
            FROM analytics_ipl_bowler_pressure_bands_since2023 bp
            JOIN ipl_2026_squads sq ON bp.player_id = sq.player_id
            WHERE sq.team_name = '{team_name}'
            GROUP BY bp.player_id
            HAVING MAX(bp.legal_balls) >= {PRESSURE_MIN_BALLS_THRESHOLD}
        )
        SELECT bp.player_name, bp.pressure_band, bp.legal_balls,
               bp.economy, bp.dot_ball_pct, bp.boundary_conceded_pct,
               bp.wickets
        FROM analytics_ipl_bowler_pressure_bands_since2023 bp
        JOIN ipl_2026_squads sq ON bp.player_id = sq.player_id
        JOIN qualified q ON bp.player_id = q.player_id
        WHERE sq.team_name = '{team_name}'
        ORDER BY bp.player_name,
            CASE bp.pressure_band
                WHEN 'COMFORTABLE' THEN 1
                WHEN 'BUILDING' THEN 2
                WHEN 'HIGH' THEN 3
                WHEN 'EXTREME' THEN 4
                WHEN 'NEAR_IMPOSSIBLE' THEN 5
            END
        """,
        default=[],
    )

    if rows:
        md.append("| Player | Band | Balls | Economy | Dot% | Bdry% Conc | Wickets | Confidence |")
        md.append("|--------|------|-------|---------|------|------------|---------|------------|")
        for player, band, balls, econ, dot_pct, bdry_conc, wkts in rows:
            confidence = _pressure_confidence_label(balls)
            md.append(
                f"| {player} | {band} | {balls} | {format_stat(econ)} | "
                f"{format_stat(dot_pct)} | {format_stat(bdry_conc)} | "
                f"{wkts or 0} | {confidence} |"
            )
    else:
        md.append("*No qualifying bowling pressure data available for this squad*")

    md.append("")
    return md


def _generate_pressure_ratings(conn: duckdb.DuckDBPyConnection, team_name: str) -> List[str]:
    """
    Generate Pressure Ratings subsection showing delta ratings.

    Displays how key players' performance changes under pressure compared to
    their overall numbers. Highlights CLUTCH and PRESSURE_PROOF ratings.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted lines for the pressure ratings table
    """
    md = ["### 11.3 Pressure Ratings\n"]
    md.append("*How player performance shifts under pressure vs overall — IPL 2023+*\n")
    md.append("*Weighted Score = SR Delta x sample-size bonus x death-overs bonus*\n")

    rows = execute_query_safe(
        conn,
        f"""
        SELECT pd.player_name, pd.role, pd.sr_delta_pct,
               pd.pressure_rating, pd.sample_confidence,
               pd.pressure_balls, pd.pressure_score,
               pd.entry_context
        FROM analytics_ipl_pressure_deltas_since2023 pd
        JOIN ipl_2026_squads sq ON pd.player_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
        ORDER BY pd.pressure_score DESC
        """,
        default=[],
    )

    if rows:
        md.append("| Player | Role | Balls | Delta% | W.Score | Rating | Entry | Confidence |")
        md.append("|--------|------|-------|--------|---------|--------|-------|------------|")
        for player, role, delta_pct, rating, confidence, balls, score, entry_ctx in rows:
            # Highlight positive ratings
            if rating in ("CLUTCH", "PRESSURE_PROOF"):
                rating_display = f"**{rating}**"
            else:
                rating_display = rating
            delta_str = f"+{delta_pct:.1f}" if delta_pct > 0 else f"{delta_pct:.1f}"
            score_str = format_stat(score) if score is not None else "-"
            balls_str = str(balls) if balls is not None else "-"
            entry_display = entry_ctx if entry_ctx else "-"
            md.append(
                f"| {player} | {role} | {balls_str} | {delta_str}% | "
                f"{score_str} | {rating_display} | {entry_display} | {confidence} |"
            )
    else:
        md.append("*No pressure delta ratings available for this squad*")

    md.append("")
    return md


# =============================================================================
# UNCAPPED WATCH HELPERS (TKT-182)
# =============================================================================

# Top T20 franchise tournaments for display in Uncapped Watch
T20_FRANCHISE_TOURNAMENTS = (
    "Big Bash League",
    "Vitality Blast",
    "Vitality Blast Men",
    "NatWest T20 Blast",
    "Pakistan Super League",
    "Caribbean Premier League",
    "SA20",
    "The Hundred Men's Competition",
    "Super Smash",
    "International League T20",
    "Lanka Premier League",
    "Major League Cricket",
    "Syed Mushtaq Ali Trophy",
    "CSA T20 Challenge",
    "Mzansi Super League",
    "Nepal Premier League",
)

# Minimum T20 innings/matches to qualify as "meaningful" data
MIN_T20_INNINGS_MEANINGFUL = 5
MIN_T20_MATCHES_BOWLING_MEANINGFUL = 3


def _classify_t20_confidence(t20_innings_or_matches: Optional[int]) -> str:
    """
    Classify confidence level for T20 fallback data.

    Args:
        t20_innings_or_matches: Number of T20 innings (batting) or matches (bowling)

    Returns:
        "HIGH" if >= 20, "MEDIUM" if 10-19, "LOW" if < 10, "NONE" if None/0
    """
    if not t20_innings_or_matches:
        return "NONE"
    if t20_innings_or_matches >= 20:
        return "HIGH"
    if t20_innings_or_matches >= 10:
        return "MEDIUM"
    return "LOW"


def _compute_weighted_trust_score(
    avg_weight: Optional[float], total_t20_balls: Optional[int]
) -> float:
    """
    Compute a weighted trust score combining tournament quality and sample size.

    Formula: (avg_weight * min(total_t20_balls / 500, 1.0)) * 100, capped at 100.

    A player who has played 500+ balls in high-weight tournaments (avg_weight ~0.55+)
    gets a trust score near 55. A player with fewer balls or lower-weight tournaments
    gets proportionally less.

    Args:
        avg_weight: Average tournament weight for the player's cross-tournament data
        total_t20_balls: Total T20 balls (faced or bowled) across all non-IPL tournaments

    Returns:
        Trust score as a float between 0 and 100
    """
    if not avg_weight or not total_t20_balls:
        return 0.0
    sample_factor = min(total_t20_balls / 500.0, 1.0)
    score = avg_weight * sample_factor * 100.0
    return min(score, 100.0)


def _get_uncapped_weighted_trust(
    conn: duckdb.DuckDBPyConnection, player_id: str, mode: str = "batting"
) -> Optional[float]:
    """
    Get the weighted trust score for an uncapped player from their cross-tournament data.

    Queries the weighted composite views to get avg_weight and total_balls,
    then computes the trust score.

    Args:
        conn: Database connection
        player_id: Player ID to look up
        mode: 'batting' or 'bowling'

    Returns:
        Trust score as float, or None if no composite data available
    """
    if mode == "batting":
        query = f"""
            SELECT avg_weight, total_balls
            FROM analytics_weighted_composite_batting
            WHERE player_id = '{player_id}'
        """
    else:
        query = f"""
            SELECT avg_weight, total_balls
            FROM analytics_weighted_composite_bowling
            WHERE player_id = '{player_id}'
        """

    row = execute_query_safe(conn, query, fetch_one=True)
    if not row or row[0] is None:
        return None
    return _compute_weighted_trust_score(row[0], row[1])


def _get_top_tournaments_for_player(
    conn: duckdb.DuckDBPyConnection, player_id: str, mode: str = "batting"
) -> str:
    """
    Get the top 3 non-IPL T20 tournaments where a player has played.

    Args:
        conn: Database connection
        player_id: Player ID to look up
        mode: 'batting' or 'bowling'

    Returns:
        Comma-separated string of tournament short names, or '-' if none
    """
    if mode == "batting":
        query = f"""
            SELECT tournament_name, innings
            FROM analytics_batting_by_tournament
            WHERE player_id = '{player_id}'
              AND tournament_name != 'Indian Premier League'
            ORDER BY innings DESC
            LIMIT 3
        """
    else:
        query = f"""
            SELECT tournament_name, matches
            FROM analytics_bowling_by_tournament
            WHERE player_id = '{player_id}'
              AND tournament_name != 'Indian Premier League'
            ORDER BY matches DESC
            LIMIT 3
        """

    rows = execute_query_safe(conn, query, default=[])
    if not rows:
        return "-"

    # Shorten tournament names for display
    short_names = {
        "Big Bash League": "BBL",
        "Vitality Blast": "Blast",
        "Vitality Blast Men": "Blast",
        "NatWest T20 Blast": "Blast",
        "Pakistan Super League": "PSL",
        "Caribbean Premier League": "CPL",
        "SA20": "SA20",
        "The Hundred Men's Competition": "100",
        "Super Smash": "SS",
        "International League T20": "ILT20",
        "Lanka Premier League": "LPL",
        "Major League Cricket": "MLC",
        "Syed Mushtaq Ali Trophy": "SMAT",
        "CSA T20 Challenge": "CSA",
        "Mzansi Super League": "MSL",
        "Nepal Premier League": "NPL",
        "ICC Men's T20 World Cup": "T20WC",
        "ICC World Twenty20": "T20WC",
        "World T20": "T20WC",
        "Ram Slam T20 Challenge": "Ram Slam",
    }

    def _shorten(name: str) -> str:
        if name in short_names:
            return short_names[name]
        if name.startswith("ICC"):
            return "ICC T20"
        if " tour of " in name or "T20I Series" in name:
            return "Intl"
        first_word = name.split()[0] if name else name
        return first_word[:6]

    names = []
    for row in rows:
        t_name = row[0]
        short = _shorten(t_name)
        names.append(short)

    return ", ".join(names)


def generate_uncapped_watch(conn: duckdb.DuckDBPyConnection, team_name: str) -> List[str]:
    """
    Generate Section 12: Uncapped Watch for a team's stat pack.

    Lists players in the squad with zero IPL 2023+ data, showing their T20
    career stats from other tournaments as fallback data. Players are split
    into batting and bowling profiles with confidence levels.

    Subsections:
    - 12.1 T20 Batting Profile — batting stats from non-IPL T20 career
    - 12.2 T20 Bowling Profile — bowling stats from non-IPL T20 career
    - 12.3 No Data Available — players with zero T20 data anywhere

    Data sourced from analytics_ipl_squad_batting_since2023 and
    analytics_ipl_squad_bowling_since2023 views (T20 columns), plus
    analytics_batting_by_tournament for tournament breakdown.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted strings for the uncapped watch section
    """
    md: List[str] = []
    md.append("## 12. Uncapped Watch\n")
    md.append(
        "*Players with zero IPL 2023+ appearances — T20 career data from other tournaments*\n"
    )

    # -------------------------------------------------------------------------
    # Identify uncapped players for this team
    # -------------------------------------------------------------------------
    uncapped_query = f"""
        WITH ipl_bat AS (
            SELECT player_id, innings AS bat_inn
            FROM analytics_ipl_batting_career_since2023
        ),
        ipl_bowl AS (
            SELECT player_id, matches_bowled AS bowl_m
            FROM analytics_ipl_bowling_career_since2023
        )
        SELECT sq.player_id, sq.player_name, sq.role, sq.nationality
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_bat ib ON sq.player_id = ib.player_id
        LEFT JOIN ipl_bowl ibl ON sq.player_id = ibl.player_id
        WHERE sq.team_name = '{team_name}'
          AND COALESCE(ib.bat_inn, 0) = 0
          AND COALESCE(ibl.bowl_m, 0) = 0
        ORDER BY sq.player_name
    """
    uncapped_players = execute_query_safe(conn, uncapped_query, default=[])

    if not uncapped_players:
        md.append("*All squad members have IPL 2023+ data — no uncapped players.*\n")
        return md

    md.append(f"**{len(uncapped_players)} uncapped player(s) in squad**\n")

    # -------------------------------------------------------------------------
    # 12.1  T20 Batting Profile
    # -------------------------------------------------------------------------
    md.append("### 12.1 T20 Batting Profile\n")

    bat_query = f"""
        SELECT player_name, role, t20_innings, t20_runs, t20_sr, t20_avg, t20_sample_size
        FROM analytics_ipl_squad_batting_since2023
        WHERE team_name = '{team_name}'
          AND (ipl_innings IS NULL OR ipl_innings = 0)
          AND t20_innings IS NOT NULL
          AND t20_innings >= {MIN_T20_INNINGS_MEANINGFUL}
        ORDER BY t20_runs DESC NULLS LAST
    """
    bat_rows = execute_query_safe(conn, bat_query, default=[])

    if bat_rows:
        md.append(
            "| Player | Role | T20 Inn | T20 Runs | T20 SR | T20 Avg | Confidence | Trust | Tournaments |"
        )
        md.append(
            "|--------|------|---------|----------|--------|---------|------------|-------|-------------|"
        )
        for row in bat_rows:
            name, role, t20_inn, t20_runs, t20_sr, t20_avg, t20_sample = row
            confidence = _classify_t20_confidence(t20_inn)
            # Look up player_id for tournament breakdown and trust score
            pid_row = execute_query_safe(
                conn,
                f"SELECT player_id FROM ipl_2026_squads WHERE team_name = '{team_name}' AND player_name = '{name}' LIMIT 1",
                fetch_one=True,
            )
            tournaments = "-"
            trust_str = "-"
            if pid_row:
                tournaments = _get_top_tournaments_for_player(conn, pid_row[0], mode="batting")
                trust = _get_uncapped_weighted_trust(conn, pid_row[0], mode="batting")
                if trust is not None:
                    trust_str = f"{trust:.0f}"
            md.append(
                f"| {name} | {role or '-'} | {t20_inn or 0} | {t20_runs or 0} | "
                f"{format_stat(t20_sr)} | {format_stat(t20_avg)} | {confidence} | {trust_str} | {tournaments} |"
            )
    else:
        md.append("*No uncapped players with meaningful T20 batting data (5+ innings)*\n")

    md.append("")

    # -------------------------------------------------------------------------
    # 12.2  T20 Bowling Profile
    # -------------------------------------------------------------------------
    md.append("### 12.2 T20 Bowling Profile\n")

    bowl_query = f"""
        SELECT player_name, role, bowling_type, t20_matches, t20_wickets, t20_economy, t20_avg, t20_sample_size
        FROM analytics_ipl_squad_bowling_since2023
        WHERE team_name = '{team_name}'
          AND (ipl_matches IS NULL OR ipl_matches = 0)
          AND t20_matches IS NOT NULL
          AND t20_matches >= {MIN_T20_MATCHES_BOWLING_MEANINGFUL}
        ORDER BY t20_wickets DESC NULLS LAST
    """
    bowl_rows = execute_query_safe(conn, bowl_query, default=[])

    if bowl_rows:
        md.append(
            "| Player | Type | T20 Matches | T20 Wkts | T20 Econ | T20 Avg | Confidence | Trust | Tournaments |"
        )
        md.append(
            "|--------|------|-------------|----------|----------|---------|------------|-------|-------------|"
        )
        for row in bowl_rows:
            name, role, btype, t20_m, t20_w, t20_econ, t20_avg, t20_sample = row
            confidence = _classify_t20_confidence(t20_m)
            btype_short = (btype or "-")[:12]
            pid_row = execute_query_safe(
                conn,
                f"SELECT player_id FROM ipl_2026_squads WHERE team_name = '{team_name}' AND player_name = '{name}' LIMIT 1",
                fetch_one=True,
            )
            tournaments = "-"
            trust_str = "-"
            if pid_row:
                tournaments = _get_top_tournaments_for_player(conn, pid_row[0], mode="bowling")
                trust = _get_uncapped_weighted_trust(conn, pid_row[0], mode="bowling")
                if trust is not None:
                    trust_str = f"{trust:.0f}"
            md.append(
                f"| {name} | {btype_short} | {t20_m or 0} | {t20_w or 0} | "
                f"{format_stat(t20_econ)} | {format_stat(t20_avg)} | {confidence} | {trust_str} | {tournaments} |"
            )
    else:
        md.append("*No uncapped players with meaningful T20 bowling data (3+ matches)*\n")

    md.append("")

    # -------------------------------------------------------------------------
    # 12.3  No Data Available
    # -------------------------------------------------------------------------
    # Find players with truly zero T20 data anywhere
    no_data_players = []
    for player_id, player_name, role, nationality in uncapped_players:
        bat_check = execute_query_safe(
            conn,
            f"SELECT t20_innings FROM analytics_ipl_squad_batting_since2023 WHERE team_name = '{team_name}' AND player_name = '{player_name}'",
            fetch_one=True,
        )
        bowl_check = execute_query_safe(
            conn,
            f"SELECT t20_matches FROM analytics_ipl_squad_bowling_since2023 WHERE team_name = '{team_name}' AND player_name = '{player_name}'",
            fetch_one=True,
        )
        has_bat = bat_check and bat_check[0] and bat_check[0] >= MIN_T20_INNINGS_MEANINGFUL
        has_bowl = (
            bowl_check and bowl_check[0] and bowl_check[0] >= MIN_T20_MATCHES_BOWLING_MEANINGFUL
        )
        if not has_bat and not has_bowl:
            no_data_players.append((player_name, role, nationality))

    if no_data_players:
        md.append("### 12.3 Limited / No T20 Data\n")
        md.append(
            "*These players have insufficient T20 data for profiling "
            f"(<{MIN_T20_INNINGS_MEANINGFUL} batting innings and <{MIN_T20_MATCHES_BOWLING_MEANINGFUL} bowling matches)*\n"
        )
        md.append("| Player | Role | Nationality |")
        md.append("|--------|------|-------------|")
        for name, role, nat in no_data_players:
            md.append(f"| {name} | {role or '-'} | {nat or '-'} |")

    md.append("")
    return md


def _format_top_tournaments_struct(top_tournaments: Optional[list], mode: str = "batting") -> str:
    """
    Format the top_tournaments STRUCT array from weighted composite views for display.

    Each tournament entry is a dict with keys: t (name), w (weight), b (balls),
    and either sr (batting) or econ (bowling).

    Args:
        top_tournaments: List of tournament structs from DuckDB
        mode: 'batting' or 'bowling' to determine which stat to show

    Returns:
        Formatted string like "BBL (0.53, SR 142.1), PSL (0.51, SR 135.0)"
    """
    if not top_tournaments:
        return "-"

    # Reuse short names from the uncapped watch helper
    short_names = {
        "Big Bash League": "BBL",
        "Vitality Blast": "Blast",
        "Vitality Blast Men": "Blast",
        "NatWest T20 Blast": "Blast",
        "Pakistan Super League": "PSL",
        "Caribbean Premier League": "CPL",
        "SA20": "SA20",
        "The Hundred Men's Competition": "100",
        "Super Smash": "SS",
        "International League T20": "ILT20",
        "Lanka Premier League": "LPL",
        "Major League Cricket": "MLC",
        "Syed Mushtaq Ali Trophy": "SMAT",
        "CSA T20 Challenge": "CSA",
        "Mzansi Super League": "MSL",
        "Nepal Premier League": "NPL",
        "ICC Men's T20 World Cup": "T20WC",
        "Indian Premier League": "IPL",
    }

    parts = []
    for entry in top_tournaments[:3]:
        t_name = entry.get("t", "")
        weight = entry.get("w", 0)
        short = short_names.get(t_name, t_name[:6] if t_name else "?")
        if mode == "batting":
            stat_val = entry.get("sr", 0)
            stat_label = "SR"
        else:
            stat_val = entry.get("econ", 0)
            stat_label = "Econ"
        stat_str = f"{stat_val:.1f}" if stat_val else "-"
        parts.append(f"{short} ({weight:.2f}, {stat_label} {stat_str})")

    return "; ".join(parts)


def generate_cross_tournament_intelligence(
    conn: duckdb.DuckDBPyConnection, team_name: str
) -> List[str]:
    """
    Generate Section 13: Cross-Tournament Intelligence for a team's stat pack.

    Lists all small-sample players (from analytics_ipl_small_sample_enrichment)
    for the team, showing weighted cross-tournament stats, trust scores, and
    top tournament breakdowns. Separates batters and bowlers.

    Small-sample thresholds: <300 IPL batting balls or <200 IPL bowling balls.

    Subsections:
    - 13.1 Batting Intelligence — weighted batting stats for small-sample batters
    - 13.2 Bowling Intelligence — weighted bowling stats for small-sample bowlers
    - 13.3 Methodology — explanation of the weighting system

    Data sourced from analytics_ipl_small_sample_enrichment,
    analytics_weighted_composite_batting, and analytics_weighted_composite_bowling views.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted strings for the cross-tournament intelligence section
    """
    md: List[str] = []
    md.append("## 13. Cross-Tournament Intelligence\n")
    md.append(
        "*Weighted cross-tournament context for squad players with limited IPL samples "
        "(<300 batting balls / <200 bowling balls since 2023)*\n"
    )

    # -------------------------------------------------------------------------
    # 13.1  Batting Intelligence
    # -------------------------------------------------------------------------
    md.append("### 13.1 Batting Intelligence\n")

    bat_query = f"""
        SELECT e.player_name, e.role, e.ipl_bat_balls,
               w.weighted_sr, w.weighted_avg, w.avg_weight,
               w.tournaments_played, w.total_balls,
               w.top_tournaments
        FROM analytics_ipl_small_sample_enrichment e
        JOIN analytics_weighted_composite_batting w ON e.player_id = w.player_id
        WHERE e.team_name = '{team_name}'
          AND e.bat_small_sample = true
        ORDER BY w.total_balls DESC
    """
    bat_rows = execute_query_safe(conn, bat_query, default=[])

    if bat_rows:
        md.append(
            "| Player | Role | IPL Balls | Wt SR | Wt Avg | Tournaments | "
            "T20 Balls | Trust | Top Tournaments (weight, SR) |"
        )
        md.append(
            "|--------|------|-----------|-------|--------|-------------|"
            "-----------|-------|-------------------------------|"
        )
        for row in bat_rows:
            (
                name,
                role,
                ipl_balls,
                w_sr,
                w_avg,
                avg_weight,
                tournaments,
                total_balls,
                top_tournaments,
            ) = row
            trust = _compute_weighted_trust_score(avg_weight, total_balls)
            trust_str = f"{trust:.0f}"
            top_str = _format_top_tournaments_struct(top_tournaments, mode="batting")
            md.append(
                f"| {name} | {role or '-'} | {ipl_balls or 0} | "
                f"{format_stat(w_sr)} | {format_stat(w_avg)} | "
                f"{tournaments or 0} | {total_balls or 0} | {trust_str} | {top_str} |"
            )
    else:
        md.append("*No small-sample batters with cross-tournament data for this squad*\n")

    md.append("")

    # -------------------------------------------------------------------------
    # 13.2  Bowling Intelligence
    # -------------------------------------------------------------------------
    md.append("### 13.2 Bowling Intelligence\n")

    bowl_query = f"""
        SELECT e.player_name, e.role, e.ipl_bowl_balls,
               w.weighted_economy, w.weighted_bowling_sr, w.avg_weight,
               w.tournaments_played, w.total_balls,
               w.top_tournaments
        FROM analytics_ipl_small_sample_enrichment e
        JOIN analytics_weighted_composite_bowling w ON e.player_id = w.player_id
        WHERE e.team_name = '{team_name}'
          AND e.bowl_small_sample = true
        ORDER BY w.total_balls DESC
    """
    bowl_rows = execute_query_safe(conn, bowl_query, default=[])

    if bowl_rows:
        md.append(
            "| Player | Role | IPL Balls | Wt Econ | Wt SR | Tournaments | "
            "T20 Balls | Trust | Top Tournaments (weight, Econ) |"
        )
        md.append(
            "|--------|------|-----------|---------|-------|-------------|"
            "-----------|-------|--------------------------------|"
        )
        for row in bowl_rows:
            (
                name,
                role,
                ipl_balls,
                w_econ,
                w_sr,
                avg_weight,
                tournaments,
                total_balls,
                top_tournaments,
            ) = row
            trust = _compute_weighted_trust_score(avg_weight, total_balls)
            trust_str = f"{trust:.0f}"
            top_str = _format_top_tournaments_struct(top_tournaments, mode="bowling")
            md.append(
                f"| {name} | {role or '-'} | {ipl_balls or 0} | "
                f"{format_stat(w_econ)} | {format_stat(w_sr)} | "
                f"{tournaments or 0} | {total_balls or 0} | {trust_str} | {top_str} |"
            )
    else:
        md.append("*No small-sample bowlers with cross-tournament data for this squad*\n")

    md.append("")

    # -------------------------------------------------------------------------
    # 13.3  Methodology
    # -------------------------------------------------------------------------
    md.append("### 13.3 Methodology\n")
    md.append(
        "Cross-tournament intelligence uses a weighted composite model across 14 T20 "
        "tournaments to provide context for players with limited IPL data.\n"
    )
    md.append("**Weighting factors** (from `dim_tournament_weights`):\n")
    md.append(
        "- **Player Quality Index (PQI)**: Strength of playing talent in the tournament\n"
        "- **Competitiveness**: How closely contested matches are\n"
        "- **Conditions Similarity**: How similar playing conditions are to IPL venues\n"
        "- **Recency**: More recent tournaments weighted higher\n"
        "- **Sample Confidence**: Larger tournaments with more matches get higher confidence\n"
    )
    md.append(
        "**Trust Score** = (avg tournament weight x min(total T20 balls / 500, 1.0)) x 100, "
        "capped at 100. Combines tournament quality with sample size — a player with 500+ balls "
        "in high-quality tournaments (BBL, PSL, The Hundred) earns a higher trust score than one "
        "with the same balls in lower-tier competitions.\n"
    )
    md.append(
        "**Tier examples**: IPL (0.87), SMAT (0.65), BBL (0.53), PSL (0.51), "
        "The Hundred (0.50), CPL (0.50), Super Smash (0.36)\n"
    )

    md.append("")
    return md


def generate_pressure_performance(conn: duckdb.DuckDBPyConnection, team_name: str) -> List[str]:
    """
    Generate Section 11: Pressure Performance for a team's stat pack.

    Combines four subsections:
    - 11.1 Batting Under Pressure — batter performance across RRR bands
    - 11.2 Bowling Under Pressure — bowler performance across RRR bands
    - 11.3 Pressure Ratings — delta ratings highlighting clutch performers
    - 11.4 Glossary — definitions of pressure bands, ratings, and metrics

    Data sourced from analytics_ipl_*_pressure_*_since2023 views, filtered
    to the team's IPL 2026 squad via ipl_2026_squads join.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted strings for the full pressure section
    """
    md = []
    md.append("## 11. Pressure Performance\n")
    md.append("*How the squad performs when the required run rate escalates — IPL 2023+ data*\n")

    # 11.1 Batting Under Pressure
    md.extend(_generate_batting_under_pressure(conn, team_name))

    # 11.2 Bowling Under Pressure
    md.extend(_generate_bowling_under_pressure(conn, team_name))

    # 11.3 Pressure Ratings
    md.extend(_generate_pressure_ratings(conn, team_name))

    # 11.4 Glossary
    md.append("### 11.4 Glossary\n")
    md.append(
        "*Quick reference for all pressure metrics, bands, and ratings used in this section.*\n"
    )

    md.append("#### Pressure Bands (RRR-Based)\n")
    md.append("| Band | RRR Range | What It Means |")
    md.append("|------|-----------|---------------|")
    md.append(
        "| COMFORTABLE | < 8 | Cruising — run rate is manageable, batters can play normally |"
    )
    md.append("| BUILDING | 8–10 | Above par — scoring needs to accelerate, risk-taking begins |")
    md.append("| HIGH | 10–12 | Aggressive required — boundaries needed every 2-3 balls |")
    md.append("| EXTREME | 12–15 | Six-hitting territory — almost every ball must score |")
    md.append("| NEAR_IMPOSSIBLE | 15+ | Miracle needed — requires continuous boundaries to win |")
    md.append("")

    md.append("#### Pressure Ratings (Performance Tags)\n")
    md.append("| Rating | For Batters | For Bowlers |")
    md.append("|--------|------------|-------------|")
    md.append(
        "| CLUTCH | SR improves 10%+ AND dot% drops in 12+ RRR bands "
        "| Economy improves AND dot% rises in 12+ RRR bands |"
    )
    md.append(
        "| PRESSURE_PROOF | Metrics within +/-5% of overall across all bands "
        "| Metrics within +/-5% of overall across all bands |"
    )
    md.append(
        "| MODERATE | Performance changes between 5-10% under pressure "
        "| Economy/dot% changes 5-10% under pressure |"
    )
    md.append(
        "| PRESSURE_SENSITIVE | SR drops 10%+ OR dot% rises 10%+ in 12+ RRR bands "
        "| Economy rises 15%+ OR boundary% conceded rises 10%+ |"
    )
    md.append("| FINISHER | SR in 15+ band exceeds 170 with adequate sample | N/A |")
    md.append("| CLOSER | N/A | Economy < 8.5 in 15+ band with 5+ overs |")
    md.append("")

    md.append("#### Entry Context (Batter Only)\n")
    md.append("| Context | Balls Before Pressure | Meaning |")
    md.append("|---------|----------------------|---------|")
    md.append("| FRESH | < 10 | Walked in during pressure phase — facing it cold |")
    md.append("| BUILDING | 10–25 | Getting set when pressure hit — partially established |")
    md.append("| SET | 25–40 | Well established before pressure phase |")
    md.append("| DEEP_SET | 40+ | Long innings before pressure — fully in rhythm |")
    md.append("")

    md.append("#### Other Terms\n")
    md.append(
        "- **Weighted Score (W.Score)**: Composite metric that combines SR delta with "
        "sample size (log2 scaling) and death overs bonus (30% weight for overs 16-20 execution)"
    )
    md.append(
        "- **SR Delta**: Percentage change in strike rate between overall performance "
        "and pressure situations. Positive = better under pressure."
    )
    md.append(
        "- **Death Pressure Ratio**: Proportion of pressure balls faced in overs 16-20 "
        "vs all pressure balls"
    )
    md.append("")

    # Section note
    md.append("---")
    md.append(
        "*Note: Players must have faced/bowled >= 30 balls in pressure bands and >= 50 overall to qualify.*\n"
    )

    return md


# =============================================================================
# SECTION 10: ANDY FLOWER'S TACTICAL INSIGHTS (REWRITTEN)
# =============================================================================


def _format_vs_league(
    value: Optional[float], benchmark: float, higher_is_better: bool = True
) -> str:
    """Format a vs-league comparison value as a signed string."""
    if value is None:
        return "-"
    diff = value - benchmark if higher_is_better else benchmark - value
    sign = "+" if diff > 0 else ""
    return f"{sign}{diff:.1f}"


def _classify_pace_spin_tendency(pace_sr: Optional[float], spin_sr: Optional[float]) -> str:
    """Classify a batter as Pace Dominant, Spin Dominant, or Balanced."""
    if pace_sr is None or spin_sr is None:
        return "Insufficient data"
    if pace_sr > spin_sr + 15:
        return "Pace Dominant"
    if spin_sr > pace_sr + 15:
        return "Spin Dominant"
    return "Balanced"


def _generate_phase_batting(
    conn: duckdb.DuckDBPyConnection, team_name: str, phase: str
) -> Tuple[List[str], list]:
    """Generate batting table for a single phase. Returns (md_lines, raw_rows)."""
    md: List[str] = []
    bench = LEAGUE_BENCHMARKS["batting"][phase]

    rows = execute_query_safe(
        conn,
        f"""
        SELECT player_name, innings, strike_rate, batting_average, boundary_pct
        FROM analytics_ipl_squad_batting_phase_since2023
        WHERE team_name = '{team_name}'
          AND match_phase = '{phase}'
          AND innings >= 5
        ORDER BY runs DESC
        LIMIT 4
        """,
        default=[],
    )

    if rows:
        md.append("| Player | Inn | SR | Avg | Bdry% | vs League SR |")
        md.append("|--------|-----|-----|-----|-------|--------------|")
        for name, inn, sr, avg, bdry in rows:
            vs_lg = _format_vs_league(sr, bench["sr"], higher_is_better=True)
            md.append(
                f"| **{name}** | {inn} | {format_stat(sr)} | {format_stat(avg)} "
                f"| {format_stat(bdry)} | {vs_lg} |"
            )
    else:
        md.append("*Insufficient batting data for this phase*\n")

    return md, rows


def _generate_phase_bowling(
    conn: duckdb.DuckDBPyConnection, team_name: str, phase: str
) -> Tuple[List[str], list]:
    """Generate bowling table for a single phase. Returns (md_lines, raw_rows)."""
    md: List[str] = []
    bench = LEAGUE_BENCHMARKS["bowling"][phase]

    rows = execute_query_safe(
        conn,
        f"""
        SELECT player_name, overs, economy_rate, wickets, dot_ball_pct
        FROM analytics_ipl_squad_bowling_phase_since2023
        WHERE team_name = '{team_name}'
          AND match_phase = '{phase}'
          AND sample_size IN ('MEDIUM', 'HIGH')
        ORDER BY wickets DESC
        LIMIT 3
        """,
        default=[],
    )

    if rows:
        md.append("| Bowler | Overs | Econ | Wkts | Dot% | vs League Econ |")
        md.append("|--------|-------|------|------|------|----------------|")
        for name, overs, econ, wkts, dot in rows:
            # For economy, lower is better, so vs_league = league_avg - player_econ
            vs_lg = _format_vs_league(econ, bench["economy"], higher_is_better=False)
            md.append(
                f"| **{name}** | {format_stat(overs)} | {format_stat(econ)} "
                f"| {wkts} | {format_stat(dot)} | {vs_lg} |"
            )
    else:
        md.append("*Insufficient bowling data for this phase*\n")

    return md, rows


def _generate_phase_editorial(
    phase: str,
    bat_rows: list,
    bowl_rows: list,
) -> str:
    """Generate 1-2 sentence editorial synthesis for a phase."""
    bench_bat = LEAGUE_BENCHMARKS["batting"][phase]
    bench_bowl = LEAGUE_BENCHMARKS["bowling"][phase]
    phase_label = {"powerplay": "Powerplay", "middle": "Middle overs", "death": "Death overs"}[
        phase
    ]
    lines = []

    # Batting insight
    if bat_rows:
        top = bat_rows[0]
        name, inn, sr, avg, bdry = top
        if sr is not None and sr > bench_bat["sr"] + 10:
            lines.append(
                f"**{name}** is a standout in the {phase_label.lower()} with a SR of "
                f"{sr:.1f} — {sr - bench_bat['sr']:.1f} points above the league average of "
                f"{bench_bat['sr']:.1f}."
            )
        elif sr is not None and sr < bench_bat["sr"] - 10:
            lines.append(
                f"Batting intent in the {phase_label.lower()} is a concern — the top option "
                f"**{name}** strikes at just {sr:.1f}, well below the league benchmark of "
                f"{bench_bat['sr']:.1f}."
            )
        else:
            lines.append(
                f"Batting in the {phase_label.lower()} is league-standard, led by **{name}** "
                f"({format_stat(sr)} SR across {inn} innings)."
            )

    # Bowling insight
    if bowl_rows:
        top = bowl_rows[0]
        name, overs, econ, wkts, dot = top
        if econ is not None and econ < bench_bowl["economy"] - 1.0:
            lines.append(
                f"**{name}** provides elite {phase_label.lower()} control at "
                f"{econ:.1f} economy — {bench_bowl['economy'] - econ:.1f} runs per over cheaper "
                f"than the league average."
            )
        elif econ is not None and econ > bench_bowl["economy"] + 1.0:
            lines.append(
                f"Bowling in the {phase_label.lower()} is a vulnerability — best option "
                f"**{name}** concedes {econ:.1f} RPO, above the league average of "
                f"{bench_bowl['economy']:.1f}."
            )
        elif econ is not None:
            lines.append(
                f"**{name}** leads the {phase_label.lower()} bowling at {econ:.1f} economy "
                f"with {wkts} wickets — adequate but not dominant against the league "
                f"average of {bench_bowl['economy']:.1f}."
            )

    return (
        " ".join(lines)
        if lines
        else f"Insufficient data to assess {phase_label.lower()} performance."
    )


def generate_tactical_insights(conn: duckdb.DuckDBPyConnection, team_name: str) -> List[str]:
    """
    Generate Section 10: Andy Flower's Tactical Insights.

    A comprehensive, data-backed tactical analysis with editorial synthesis covering:
    - 10.1 Phase-by-Phase Tactical Profile (batting & bowling per phase)
    - 10.2 Batter Tendencies: Pace vs Spin Profile
    - 10.3 Pace Attack Intelligence
    - 10.4 Spin Attack Intelligence
    - 10.5 Key Vulnerabilities & Matchup Risks
    - 10.6 Andy Flower's Tactical Summary

    All data filtered to IPL 2023+ with league benchmark comparisons.

    Args:
        conn: DuckDB database connection
        team_name: Full team name (e.g., "Chennai Super Kings")

    Returns:
        List of markdown-formatted strings for the full tactical insights section
    """
    md: List[str] = []
    md.append("## 10. Andy Flower's Tactical Insights\n")
    md.append(
        "*Comprehensive tactical analysis — IPL 2023+ data with league benchmark context. "
        '"Pro team prep, packaged for public consumption."*\n'
    )

    # Store data for cross-subsection synthesis
    phase_data: Dict[str, Dict[str, list]] = {}

    # =========================================================================
    # 10.1 Phase-by-Phase Tactical Profile
    # =========================================================================
    md.append("### 10.1 Phase-by-Phase Tactical Profile\n")

    for phase in ("powerplay", "middle", "death"):
        phase_label = {
            "powerplay": "Powerplay (overs 1-6)",
            "middle": "Middle Overs (7-15)",
            "death": "Death Overs (16-20)",
        }[phase]
        md.append(f"#### {phase_label}\n")

        md.append("**Batting**\n")
        bat_md, bat_rows = _generate_phase_batting(conn, team_name, phase)
        md.extend(bat_md)
        md.append("")

        md.append("**Bowling**\n")
        bowl_md, bowl_rows = _generate_phase_bowling(conn, team_name, phase)
        md.extend(bowl_md)
        md.append("")

        # Editorial synthesis
        editorial = _generate_phase_editorial(phase, bat_rows, bowl_rows)
        md.append(f"*{editorial}*\n")

        phase_data[phase] = {"batting": bat_rows, "bowling": bowl_rows}

    # =========================================================================
    # 10.2 Batter Tendencies: Pace vs Spin Profile
    # =========================================================================
    md.append("### 10.2 Batter Tendencies: Pace vs Spin Profile\n")

    pace_types_sql = ", ".join([f"'{t}'" for t in PACE_BATTER_VS_TYPES])
    spin_types_sql = ", ".join([f"'{t}'" for t in SPIN_BATTER_VS_TYPES])

    try:
        # Get top batters by total innings across types
        batter_tendency_rows = conn.execute(f"""
            WITH batter_innings AS (
                SELECT bt.batter_id, bt.batter_name, SUM(bt.balls) as total_balls
                FROM analytics_ipl_batter_vs_bowler_type_since2023 bt
                JOIN ipl_2026_squads sq ON bt.batter_id = sq.player_id
                WHERE sq.team_name = '{team_name}'
                GROUP BY bt.batter_id, bt.batter_name
                HAVING SUM(bt.balls) >= 50
                ORDER BY SUM(bt.balls) DESC
                LIMIT 8
            ),
            pace_agg AS (
                SELECT bt.batter_id,
                       SUM(bt.runs) as pace_runs,
                       SUM(bt.balls) as pace_balls,
                       ROUND(SUM(bt.runs) * 100.0 / NULLIF(SUM(bt.balls), 0), 2) as pace_sr,
                       ROUND(SUM(bt.fours + bt.sixes) * 100.0 / NULLIF(SUM(bt.balls), 0), 2) as pace_bdry_pct
                FROM analytics_ipl_batter_vs_bowler_type_since2023 bt
                WHERE bt.bowler_type IN ({pace_types_sql})
                GROUP BY bt.batter_id
            ),
            spin_agg AS (
                SELECT bt.batter_id,
                       SUM(bt.runs) as spin_runs,
                       SUM(bt.balls) as spin_balls,
                       ROUND(SUM(bt.runs) * 100.0 / NULLIF(SUM(bt.balls), 0), 2) as spin_sr,
                       ROUND(SUM(bt.fours + bt.sixes) * 100.0 / NULLIF(SUM(bt.balls), 0), 2) as spin_bdry_pct
                FROM analytics_ipl_batter_vs_bowler_type_since2023 bt
                WHERE bt.bowler_type IN ({spin_types_sql})
                GROUP BY bt.batter_id
            )
            SELECT bi.batter_name, p.pace_sr, s.spin_sr, p.pace_bdry_pct, s.spin_bdry_pct,
                   p.pace_balls, s.spin_balls
            FROM batter_innings bi
            LEFT JOIN pace_agg p ON bi.batter_id = p.batter_id
            LEFT JOIN spin_agg s ON bi.batter_id = s.batter_id
            ORDER BY bi.total_balls DESC
        """).fetchall()

        if batter_tendency_rows:
            md.append("| Batter | vs Pace SR | vs Spin SR | Pace Bdry% | Spin Bdry% | Tendency |")
            md.append("|--------|-----------|-----------|-----------|-----------|----------|")
            spin_vulnerable = []
            pace_thrivers = []
            for (
                name,
                pace_sr,
                spin_sr,
                pace_bdry,
                spin_bdry,
                pace_balls,
                spin_balls,
            ) in batter_tendency_rows:
                tendency = _classify_pace_spin_tendency(pace_sr, spin_sr)
                md.append(
                    f"| **{name}** | {format_stat(pace_sr)} | {format_stat(spin_sr)} "
                    f"| {format_stat(pace_bdry)} | {format_stat(spin_bdry)} | {tendency} |"
                )
                if spin_sr is not None and spin_sr < 120:
                    spin_vulnerable.append((name, spin_sr))
                if pace_sr is not None and pace_sr > 160:
                    pace_thrivers.append((name, pace_sr))

            md.append("")
            lg_pace = LEAGUE_BENCHMARKS["vs_bowling_type"]["Fast"]["sr"]
            lg_spin_avg = (
                sum(
                    LEAGUE_BENCHMARKS["vs_bowling_type"][t]["sr"]
                    for t in (
                        "Right-arm off-spin",
                        "Right-arm leg-spin",
                        "Left-arm orthodox",
                        "Left-arm wrist spin",
                    )
                )
                / 4
            )

            # Editorial synthesis
            editorial_parts = []
            if spin_vulnerable:
                names = ", ".join([f"**{n}** ({sr:.0f} SR)" for n, sr in spin_vulnerable])
                editorial_parts.append(
                    f"Exploitable vs spin: {names} — all below the league average of ~{lg_spin_avg:.0f} SR. "
                    f"Opposition teams with quality wrist spinners should target these batters in the middle overs."
                )
            if pace_thrivers:
                names = ", ".join([f"**{n}** ({sr:.0f} SR)" for n, sr in pace_thrivers])
                editorial_parts.append(
                    f"Pace-hitting strength: {names} thrive against pace (league avg {lg_pace:.0f} SR), "
                    f"making them dangerous against teams reliant on pace-heavy attacks."
                )
            if not editorial_parts:
                editorial_parts.append(
                    "The batting lineup shows a balanced pace-spin profile with no extreme vulnerabilities. "
                    "Matchup planning should focus on individual bowler-batter history rather than type-level exploitation."
                )
            md.append(f"*{' '.join(editorial_parts)}*\n")
        else:
            md.append("*Insufficient batter vs bowling type data for this squad*\n")

    except Exception as e:
        logger.warning("Section 10.2 query failed for %s: %s", team_name, str(e)[:100])
        md.append("*Data unavailable for pace vs spin profile*\n")

    # =========================================================================
    # 10.3 Pace Attack Intelligence
    # =========================================================================
    md.append("### 10.3 Pace Attack Intelligence\n")

    pace_types_squad_sql = ", ".join([f"'{t}'" for t in PACE_BOWLING_TYPES])

    try:
        pace_bowlers = conn.execute(f"""
            SELECT bpd.bowler_name,
                   MAX(CASE WHEN bpd.match_phase = 'powerplay' THEN bpd.economy END) as pp_econ,
                   MAX(CASE WHEN bpd.match_phase = 'middle' THEN bpd.economy END) as mid_econ,
                   MAX(CASE WHEN bpd.match_phase = 'death' THEN bpd.economy END) as death_econ,
                   SUM(bpd.wickets) as total_wkts,
                   SUM(bpd.overs) as total_overs
            FROM analytics_ipl_bowler_phase_distribution_since2023 bpd
            JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
            WHERE sq.team_name = '{team_name}'
              AND sq.bowling_type IN ({pace_types_squad_sql})
              AND bpd.sample_size IN ('MEDIUM', 'HIGH')
            GROUP BY bpd.bowler_name
            HAVING SUM(bpd.overs) >= 5
            ORDER BY SUM(bpd.wickets) DESC
        """).fetchall()

        if pace_bowlers:
            md.append("| Bowler | PP Econ | Mid Econ | Death Econ | Best Phase | Wkt Rate |")
            md.append("|--------|---------|----------|------------|------------|----------|")
            death_specialist = None
            pp_specialist = None
            mid_gap = False

            for name, pp_econ, mid_econ, death_econ, total_wkts, total_overs in pace_bowlers:
                # Determine best phase
                phase_econs = {}
                if pp_econ is not None:
                    phase_econs["PP"] = pp_econ
                if mid_econ is not None:
                    phase_econs["Middle"] = mid_econ
                if death_econ is not None:
                    phase_econs["Death"] = death_econ

                best_phase = min(phase_econs, key=phase_econs.get) if phase_econs else "-"
                wkt_rate = (
                    f"{total_wkts / total_overs:.2f}" if total_overs and total_overs > 0 else "-"
                )

                md.append(
                    f"| **{name}** | {format_stat(pp_econ)} | {format_stat(mid_econ)} "
                    f"| {format_stat(death_econ)} | {best_phase} | {wkt_rate} |"
                )

                if (
                    death_econ is not None
                    and death_econ < LEAGUE_BENCHMARKS["bowling"]["death"]["economy"]
                ):
                    death_specialist = (name, death_econ)
                if (
                    pp_econ is not None
                    and pp_econ < LEAGUE_BENCHMARKS["bowling"]["powerplay"]["economy"]
                ):
                    pp_specialist = (name, pp_econ)
                if (
                    mid_econ is not None
                    and mid_econ > LEAGUE_BENCHMARKS["bowling"]["middle"]["economy"] + 1.5
                ):
                    mid_gap = True

            md.append("")

            # Editorial
            editorial_parts = []
            if death_specialist:
                editorial_parts.append(
                    f"**{death_specialist[0]}** is the designated death option at {death_specialist[1]:.1f} economy "
                    f"(league avg {LEAGUE_BENCHMARKS['bowling']['death']['economy']:.1f})."
                )
            else:
                editorial_parts.append(
                    f"No pace bowler operates below the league death average of "
                    f"{LEAGUE_BENCHMARKS['bowling']['death']['economy']:.1f} — death bowling is a structural concern."
                )
            if pp_specialist:
                editorial_parts.append(
                    f"**{pp_specialist[0]}** should lead the powerplay attack ({pp_specialist[1]:.1f} economy)."
                )
            if mid_gap:
                editorial_parts.append(
                    "Middle-overs pace economy is above league average — consider deploying spin "
                    "through this phase to contain."
                )
            md.append(f"*{' '.join(editorial_parts)}*\n")
        else:
            md.append("*No qualified pace bowlers with sufficient phase data*\n")

    except Exception as e:
        logger.warning("Section 10.3 query failed for %s: %s", team_name, str(e)[:100])
        md.append("*Data unavailable for pace attack intelligence*\n")

    # =========================================================================
    # 10.4 Spin Attack Intelligence
    # =========================================================================
    md.append("### 10.4 Spin Attack Intelligence\n")

    spin_types_squad_sql = ", ".join([f"'{t}'" for t in SPIN_BOWLING_TYPES])

    try:
        spin_bowlers = conn.execute(f"""
            SELECT bpd.bowler_name,
                   MAX(CASE WHEN bpd.match_phase = 'powerplay' THEN bpd.economy END) as pp_econ,
                   MAX(CASE WHEN bpd.match_phase = 'middle' THEN bpd.economy END) as mid_econ,
                   MAX(CASE WHEN bpd.match_phase = 'death' THEN bpd.economy END) as death_econ,
                   SUM(bpd.wickets) as total_wkts,
                   SUM(bpd.overs) as total_overs,
                   ROUND(SUM(bpd.dot_balls) * 100.0 / NULLIF(SUM(bpd.balls), 0), 1) as overall_dot_pct
            FROM analytics_ipl_bowler_phase_distribution_since2023 bpd
            JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
            WHERE sq.team_name = '{team_name}'
              AND sq.bowling_type IN ({spin_types_squad_sql})
              AND bpd.sample_size IN ('MEDIUM', 'HIGH')
            GROUP BY bpd.bowler_name
            HAVING SUM(bpd.overs) >= 5
            ORDER BY SUM(bpd.wickets) DESC
        """).fetchall()

        if spin_bowlers:
            md.append("| Bowler | PP Econ | Mid Econ | Death Econ | Best Phase | Control Rating |")
            md.append("|--------|---------|----------|------------|------------|----------------|")
            mid_controller = None
            death_capable_spin = None
            total_spin_overs = 0.0

            for (
                name,
                pp_econ,
                mid_econ,
                death_econ,
                total_wkts,
                total_overs,
                dot_pct,
            ) in spin_bowlers:
                phase_econs = {}
                if pp_econ is not None:
                    phase_econs["PP"] = pp_econ
                if mid_econ is not None:
                    phase_econs["Middle"] = mid_econ
                if death_econ is not None:
                    phase_econs["Death"] = death_econ

                best_phase = min(phase_econs, key=phase_econs.get) if phase_econs else "-"
                control = f"{dot_pct:.1f}%" if dot_pct is not None else "-"
                total_spin_overs += total_overs if total_overs else 0

                md.append(
                    f"| **{name}** | {format_stat(pp_econ)} | {format_stat(mid_econ)} "
                    f"| {format_stat(death_econ)} | {best_phase} | {control} |"
                )

                if (
                    mid_econ is not None
                    and mid_econ < LEAGUE_BENCHMARKS["bowling"]["middle"]["economy"]
                ):
                    if mid_controller is None or mid_econ < mid_controller[1]:
                        mid_controller = (name, mid_econ)
                if (
                    death_econ is not None
                    and death_econ < LEAGUE_BENCHMARKS["bowling"]["death"]["economy"]
                ):
                    death_capable_spin = (name, death_econ)

            md.append("")

            # Editorial
            editorial_parts = []
            if mid_controller:
                editorial_parts.append(
                    f"**{mid_controller[0]}** is the middle-overs anchor at {mid_controller[1]:.1f} economy "
                    f"(league avg {LEAGUE_BENCHMARKS['bowling']['middle']['economy']:.1f}) — must bowl 3-4 overs "
                    f"through the middle phase."
                )
            if death_capable_spin:
                editorial_parts.append(
                    f"**{death_capable_spin[0]}** offers a viable death option at "
                    f"{death_capable_spin[1]:.1f} economy, giving the captain tactical flexibility."
                )
            else:
                editorial_parts.append(
                    "No spinner operates below league average at the death — all death bowling falls on the pace unit."
                )
            if len(spin_bowlers) <= 1:
                editorial_parts.append(
                    "Spin depth is thin — injury to the primary spinner would expose the middle overs significantly."
                )
            elif total_spin_overs > 100:
                editorial_parts.append(
                    f"Spin dependency is high with {total_spin_overs:.0f} combined overs across {len(spin_bowlers)} "
                    f"spinners — a strength on turning pitches but a risk on pace-friendly surfaces."
                )
            md.append(f"*{' '.join(editorial_parts)}*\n")
        else:
            md.append("*No qualified spin bowlers with sufficient phase data*\n")

    except Exception as e:
        logger.warning("Section 10.4 query failed for %s: %s", team_name, str(e)[:100])
        md.append("*Data unavailable for spin attack intelligence*\n")

    # =========================================================================
    # 10.5 Key Vulnerabilities & Matchup Risks
    # =========================================================================
    md.append("### 10.5 Key Vulnerabilities & Matchup Risks\n")

    md.append("#### Phase Gaps\n")

    # Compare team phase batting/bowling vs league benchmarks
    try:
        team_phase_bat = execute_query_safe(
            conn,
            f"""
            SELECT match_phase,
                   ROUND(AVG(strike_rate), 2) as avg_sr,
                   ROUND(AVG(batting_average), 2) as avg_avg
            FROM analytics_ipl_squad_batting_phase_since2023
            WHERE team_name = '{team_name}'
              AND match_phase IS NOT NULL
              AND innings >= 5
            GROUP BY match_phase
            """,
            default=[],
        )
        team_phase_bowl = execute_query_safe(
            conn,
            f"""
            SELECT match_phase,
                   ROUND(AVG(economy_rate), 2) as avg_econ
            FROM analytics_ipl_squad_bowling_phase_since2023
            WHERE team_name = '{team_name}'
              AND match_phase IS NOT NULL
              AND sample_size IN ('MEDIUM', 'HIGH')
            GROUP BY match_phase
            """,
            default=[],
        )

        bat_by_phase = {r[0]: (r[1], r[2]) for r in team_phase_bat} if team_phase_bat else {}
        bowl_by_phase = {r[0]: r[1] for r in team_phase_bowl} if team_phase_bowl else {}

        phase_gap_found = False
        for phase in ("powerplay", "middle", "death"):
            phase_label = {"powerplay": "Powerplay", "middle": "Middle", "death": "Death"}[phase]
            bat_bench = LEAGUE_BENCHMARKS["batting"][phase]
            bowl_bench = LEAGUE_BENCHMARKS["bowling"][phase]

            issues = []
            if phase in bat_by_phase:
                team_sr, team_avg = bat_by_phase[phase]
                if team_sr is not None and team_sr < bat_bench["sr"] - 10:
                    issues.append(f"batting SR {team_sr:.1f} vs league {bat_bench['sr']:.1f}")
            if phase in bowl_by_phase:
                team_econ = bowl_by_phase[phase]
                if team_econ is not None and team_econ > bowl_bench["economy"] + 1.0:
                    issues.append(
                        f"bowling economy {team_econ:.1f} vs league {bowl_bench['economy']:.1f}"
                    )

            if issues:
                md.append(f"- **{phase_label}**: {'; '.join(issues)}")
                phase_gap_found = True

        if not phase_gap_found:
            md.append(
                "- No significant phase gaps identified — team averages are within league norms across all phases."
            )
        md.append("")

    except Exception as e:
        logger.warning("Phase gaps query failed for %s: %s", team_name, str(e)[:100])
        md.append("*Phase gap analysis unavailable*\n")

    # Spin Vulnerability Risk
    md.append("#### Spin Vulnerability Risk\n")

    vs_spin_vuln = execute_query_safe(
        conn,
        f"""
        SELECT
            batter_name,
            bowler_type,
            balls,
            strike_rate,
            average,
            ROUND(balls * 1.0 / NULLIF(dismissals, 0), 2) as balls_per_dismissal
        FROM analytics_ipl_batter_vs_bowler_type_since2023
        WHERE batter_id IN (SELECT player_id FROM ipl_2026_squads WHERE team_name = '{team_name}')
          AND bowler_type IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin')
          AND sample_size IN ('MEDIUM', 'HIGH')
          AND (
              strike_rate < {Thresholds.SPIN_VULNERABILITY_SR}
              OR (average IS NOT NULL AND average < {Thresholds.SPIN_VULNERABILITY_AVG})
              OR (dismissals >= 3 AND balls * 1.0 / dismissals < {Thresholds.SPIN_VULNERABILITY_BPD})
          )
        ORDER BY batter_name, strike_rate ASC
        """,
        default=[],
    )

    if vs_spin_vuln:
        for name, btype, balls, sr, avg, bpd in vs_spin_vuln:
            league_sr = LEAGUE_BENCHMARKS["vs_bowling_type"].get(btype, {}).get("sr", 0)
            btype_short = btype.replace("Right-arm ", "").replace("Left-arm ", "LA ")
            deficit = f"league avg {league_sr:.1f}" if league_sr else ""
            md.append(
                f"- **{name}** vs {btype_short}: SR {format_stat(sr)}, "
                f"Avg {format_stat(avg)}, BPD {format_stat(bpd)} "
                f"({balls} balls{', ' + deficit if deficit else ''})"
            )
    else:
        md.append("- No significant spin vulnerabilities identified in MEDIUM/HIGH sample data.")
    md.append("")

    # Pace Vulnerability Risk
    md.append("#### Pace Vulnerability Risk\n")

    vs_pace_vuln = execute_query_safe(
        conn,
        f"""
        SELECT
            batter_name,
            bowler_type,
            balls,
            strike_rate,
            average
        FROM analytics_ipl_batter_vs_bowler_type_since2023
        WHERE batter_id IN (SELECT player_id FROM ipl_2026_squads WHERE team_name = '{team_name}')
          AND bowler_type IN ('Fast', 'Right-arm pace', 'Left-arm pace', 'Medium')
          AND sample_size IN ('MEDIUM', 'HIGH')
          AND strike_rate < 130
        ORDER BY batter_name, strike_rate ASC
        """,
        default=[],
    )

    if vs_pace_vuln:
        lg_pace_sr = LEAGUE_BENCHMARKS["vs_bowling_type"]["Fast"]["sr"]
        for name, btype, balls, sr, avg in vs_pace_vuln:
            md.append(
                f"- **{name}** vs {btype}: SR {format_stat(sr)}, "
                f"Avg {format_stat(avg)} ({balls} balls, league avg vs pace ~{lg_pace_sr:.0f})"
            )
    else:
        md.append(
            "- No significant pace vulnerabilities identified — squad handles pace adequately."
        )
    md.append("")

    # Structural Concerns
    md.append("#### Structural Concerns\n")

    try:
        # Check death bowling depth
        death_bowlers_count = execute_query_safe(
            conn,
            f"""
            SELECT COUNT(DISTINCT bpd.bowler_name) as cnt
            FROM analytics_ipl_bowler_phase_distribution_since2023 bpd
            JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
            WHERE sq.team_name = '{team_name}'
              AND bpd.match_phase = 'death'
              AND bpd.overs >= {Thresholds.MIN_OVERS_DEATH}
              AND bpd.sample_size IN ('MEDIUM', 'HIGH')
            """,
            default=[(0,)],
            fetch_one=True,
        )
        death_count = death_bowlers_count[0] if death_bowlers_count else 0

        structural_items = []
        if death_count < 3:
            structural_items.append(
                f"Only **{death_count} bowler(s)** with {Thresholds.MIN_OVERS_DEATH}+ death overs at MEDIUM/HIGH sample — "
                f"thin depth means any injury to a death specialist leaves the team exposed in overs 16-20."
            )

        # Check top-order dependency (from phase batting)
        pp_data = phase_data.get("powerplay", {}).get("batting", [])
        death_data = phase_data.get("death", {}).get("batting", [])
        if pp_data and len(pp_data) >= 2 and death_data:
            # Check if death batting SR is below league benchmarks
            death_top_sr = death_data[0][2] if death_data[0][2] is not None else 0
            if death_top_sr < LEAGUE_BENCHMARKS["batting"]["death"]["sr"] - 15:
                structural_items.append(
                    "Death batting strike rate below league benchmarks — the finisher role needs clarity, "
                    "especially in chases."
                )

        if not structural_items:
            structural_items.append(
                "No critical structural concerns identified — squad depth is adequate across all phases."
            )

        for item in structural_items:
            md.append(f"- {item}")
        md.append("")

    except Exception as e:
        logger.warning("Structural concerns query failed for %s: %s", team_name, str(e)[:100])
        md.append("- *Structural analysis unavailable*\n")

    # =========================================================================
    # 10.6 Andy Flower's Tactical Summary
    # =========================================================================
    md.append("### 10.6 Andy Flower's Tactical Summary\n")

    try:
        # Build the summary from phase data
        summary_parts = []

        # Paragraph 1: Strengths
        strengths = []
        for phase in ("powerplay", "middle", "death"):
            bat_rows = phase_data.get(phase, {}).get("batting", [])
            bowl_rows = phase_data.get(phase, {}).get("bowling", [])
            bat_bench = LEAGUE_BENCHMARKS["batting"][phase]
            bowl_bench = LEAGUE_BENCHMARKS["bowling"][phase]

            if bat_rows and bat_rows[0][2] is not None and bat_rows[0][2] > bat_bench["sr"] + 10:
                phase_label = {
                    "powerplay": "powerplay",
                    "middle": "middle-overs",
                    "death": "death",
                }[phase]
                strengths.append(
                    f"{phase_label} batting ({bat_rows[0][0]} at {bat_rows[0][2]:.0f} SR)"
                )
            if (
                bowl_rows
                and bowl_rows[0][2] is not None
                and bowl_rows[0][2] < bowl_bench["economy"] - 1
            ):
                phase_label = {
                    "powerplay": "powerplay",
                    "middle": "middle-overs",
                    "death": "death",
                }[phase]
                strengths.append(
                    f"{phase_label} bowling ({bowl_rows[0][0]} at {bowl_rows[0][2]:.1f} economy)"
                )

        if strengths:
            summary_parts.append(
                f"This squad's competitive advantages are clear: {', '.join(strengths)}. "
                f"These are non-negotiable pillars — the coaching staff must build match plans around protecting "
                f"and maximizing these phase strengths. Any game plan that doesn't feature these assets prominently "
                f"is leaving runs on the table."
            )
        else:
            summary_parts.append(
                "This squad lacks a standout phase advantage over league benchmarks — the margin for error is thin. "
                "Execution discipline across all three phases is non-negotiable; there is no single phase strength to "
                "fall back on when plans break down."
            )

        # Paragraph 2: Vulnerabilities and matchup implications
        vuln_parts = []
        for phase in ("powerplay", "middle", "death"):
            bat_rows = phase_data.get(phase, {}).get("batting", [])
            bowl_rows = phase_data.get(phase, {}).get("bowling", [])
            bat_bench = LEAGUE_BENCHMARKS["batting"][phase]
            bowl_bench = LEAGUE_BENCHMARKS["bowling"][phase]

            if bat_rows and bat_rows[0][2] is not None and bat_rows[0][2] < bat_bench["sr"] - 10:
                phase_label = {
                    "powerplay": "powerplay",
                    "middle": "middle-overs",
                    "death": "death",
                }[phase]
                vuln_parts.append(f"under-par {phase_label} batting")
            if (
                bowl_rows
                and bowl_rows[0][2] is not None
                and bowl_rows[0][2] > bowl_bench["economy"] + 1
            ):
                phase_label = {
                    "powerplay": "powerplay",
                    "middle": "middle-overs",
                    "death": "death",
                }[phase]
                vuln_parts.append(f"expensive {phase_label} bowling")

        if vuln_parts:
            summary_parts.append(
                f"The vulnerability to exploit: {', '.join(vuln_parts)}. "
                f"Opposition teams will target these phases — the captain must have contingency plans ready. "
                f"In high-stakes matches, these weaknesses will be tested repeatedly, and the response "
                f"must be pre-planned, not reactive."
            )
        else:
            summary_parts.append(
                "No glaring phase vulnerabilities exist, but complacency is the real risk. "
                "The squad must maintain execution standards across all phases — any dip in "
                "discipline will be punished at this level."
            )

        # Paragraph 3: Strategic priorities
        spin_vuln_count = len(vs_spin_vuln) if vs_spin_vuln else 0
        pace_vuln_count = len(vs_pace_vuln) if vs_pace_vuln else 0

        priorities = []
        if spin_vuln_count >= 3:
            priorities.append(
                f"address the spin vulnerability ({spin_vuln_count} batters flagged) "
                f"through targeted batting practice against quality wrist spin"
            )
        if pace_vuln_count >= 3:
            priorities.append(
                f"shore up pace-hitting deficiencies ({pace_vuln_count} batters below threshold)"
            )
        if death_count < 3:
            priorities.append(
                "develop a third death bowling option to reduce over-reliance on a thin death unit"
            )

        if priorities:
            summary_parts.append(
                f"Pre-tournament priorities must include: {'; '.join(priorities)}. "
                f"These are the controllable edges that separate playoff teams from also-rans. "
                f"The data is clear — the coaching staff must execute on these priorities before "
                f"the first ball is bowled."
            )
        else:
            summary_parts.append(
                "The data suggests a well-rounded squad with no glaring tactical gaps. "
                "The coaching priority should be maintaining peak performance levels across phases "
                "and ensuring tactical flexibility for different match situations. Roster management "
                "and workload planning across the tournament will be the real differentiator."
            )

        for part in summary_parts:
            md.append(part)
            md.append("")

    except Exception as e:
        logger.warning("Tactical summary failed for %s: %s", team_name, str(e)[:100])
        md.append(
            "*Tactical summary generation failed — see subsections above for detailed analysis.*\n"
        )

    md.append("---")
    md.append(
        "*Tactical analysis based on IPL 2023-2025 ball-by-ball data with league benchmark comparisons. "
        "All players filtered to 2026 squad.*\n"
    )

    return md


def generate_team_stat_pack(
    conn: duckdb.DuckDBPyConnection, team_name: str, tags_lookup: Dict[str, Dict[str, Any]]
) -> str:
    """
    Generate comprehensive stat pack markdown document for a team.

    Creates a detailed analysis document covering:
    1. Squad Overview - roster, archetypes, and player tags
    2. Historical Record vs Opposition - head-to-head records
    3. Historical Trends (2023-2025) - season performance, batting/bowling trends
    4. Venue Analysis - home/away performance, pitch characteristics
    5. Squad Batting Analysis - career and phase-wise stats
    6. Squad Bowling Analysis - career and phase distribution
    7. Key Batter vs Opposition - top batters' matchup data
    8. Key Bowler vs Opposition - top bowlers' matchup data
    9. Key Player Venue Performance - venue-specific stats
    10. Andy Flower's Tactical Insights - phase profiles, pace/spin profiles, vulnerabilities
    11. Pressure Performance - batting/bowling under pressure, pressure ratings, glossary
    12. Uncapped Watch - T20 fallback data for players without IPL 2023+ history (TKT-182)
    13. Cross-Tournament Intelligence - weighted composite stats for small-sample players (TKT-190)

    Args:
        conn: DuckDB database connection (read-only recommended)
        team_name: Full team name (e.g., "Chennai Super Kings")
        tags_lookup: Dict mapping player_id to tags and cluster info

    Returns:
        Complete stat pack as markdown-formatted string

    Raises:
        Exception: If database queries fail (logged but re-raised)
    """
    logger.info("Generating stat pack for %s", team_name)

    team_code = TEAM_CODES.get(team_name, team_name[:3].upper())
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    alias_clause = ", ".join([f"'{a}'" for a in aliases])

    md = []
    md.append(f"# {team_name} ({team_code}) - IPL 2026 Stat Pack")
    md.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("**Data Source:** Cricket Playbook Analytics Engine")
    md.append("**Prepared by:** Tom Brady (PO), Stephen Curry (Analytics), Andy Flower (Cricket)")
    md.append("\n---\n")

    # ==========================================================================
    # SECTION 1: TEAM ROSTER
    # ==========================================================================
    md.append("## 1. Squad Overview\n")

    roster = conn.execute(f"""
        SELECT player_name, role, bowling_type, batting_hand, price_cr, acquisition_type, year_joined
        FROM analytics_ipl_team_roster
        WHERE team_name = '{team_name}'
        ORDER BY price_cr DESC
    """).fetchall()

    md.append("### 1.1 Full Roster\n")
    md.append("| Player | Role | Bowling | Batting | Price (Cr) | Type | Joined |")
    md.append("|--------|------|---------|---------|------------|------|--------|")

    total_spend = 0
    role_counts = {}
    for row in roster:
        player, role, bowling, batting, price, acq, year = row
        price = price or 0
        total_spend += price
        role_counts[role] = role_counts.get(role, 0) + 1
        md.append(
            f"| {player} | {role} | {bowling or '-'} | {batting or '-'} | {price:.2f} | {acq or '-'} | {year or '-'} |"
        )

    md.append(f"\n**Total Squad Size:** {len(roster)} players")
    md.append(f"**Total Spend:** ₹{total_spend:.2f} Cr")
    md.append(
        "\n**Role Breakdown:** " + ", ".join([f"{k}: {v}" for k, v in sorted(role_counts.items())])
    )

    # ==========================================================================
    # SECTION 1.2: PLAYER ARCHETYPES AND TAGS
    # ==========================================================================
    md.append("\n### 1.2 Player Archetypes (K-means V2 Model)\n")
    md.append("*Based on clustering analysis of IPL career performance*\n")

    # Get player IDs for this team
    squad_players = conn.execute(f"""
        SELECT player_id, player_name, role
        FROM ipl_2026_squads
        WHERE team_name = '{team_name}'
        ORDER BY role, player_name
    """).fetchall()

    # Group players by archetype using module-level cluster constants
    batters_by_cluster: Dict[str, List[Tuple[str, List[str]]]] = {}
    bowlers_by_cluster: Dict[str, List[Tuple[str, List[str]]]] = {}

    for player_id, player_name, role in squad_players:
        if player_id in tags_lookup:
            tags = tags_lookup[player_id].get("tags", [])

            if role in ("Batter", "Wicketkeeper", "All-rounder"):
                # Find batter cluster tag using module constant
                cluster = _extract_cluster_from_tags(tags, BATTER_CLUSTERS)
                if cluster:
                    if cluster not in batters_by_cluster:
                        batters_by_cluster[cluster] = []
                    batters_by_cluster[cluster].append((player_name, tags))

            if role in ("Bowler", "All-rounder"):
                # Find bowler cluster tag using module constant
                cluster = _extract_cluster_from_tags(tags, BOWLER_CLUSTERS)
                if cluster:
                    if cluster not in bowlers_by_cluster:
                        bowlers_by_cluster[cluster] = []
                    bowlers_by_cluster[cluster].append((player_name, tags))

    if batters_by_cluster:
        md.append("**Batter Archetypes:**\n")
        for cluster in BATTER_CLUSTERS_ORDERED:
            if cluster in batters_by_cluster:
                players = batters_by_cluster[cluster]
                player_list = ", ".join([p[0] for p in players])
                md.append(f"- **{cluster}**: {player_list}")
        md.append("")

    if bowlers_by_cluster:
        md.append("**Bowler Archetypes:**\n")
        for cluster in BOWLER_CLUSTERS_ORDERED:
            if cluster in bowlers_by_cluster:
                players = bowlers_by_cluster[cluster]
                player_list = ", ".join([p[0] for p in players])
                md.append(f"- **{cluster}**: {player_list}")
        md.append("")

    # Show key player tags
    md.append("### 1.3 Key Player Tags\n")
    md.append("*Performance tags based on phase analysis, matchups, and specializations*\n")

    md.append("| Player | Tags |")
    md.append("|--------|------|")
    for player_id, player_name, role in squad_players:
        if player_id in tags_lookup:
            tags = tags_lookup[player_id].get("tags", [])
            if tags:
                # Show up to 5 most relevant tags
                display_tags = tags[:5]
                tags_str = ", ".join(display_tags)
                if len(tags) > 5:
                    tags_str += f" (+{len(tags) - 5} more)"
                md.append(f"| {player_name} | {tags_str} |")

    # ==========================================================================
    # SECTION 2: TEAM HISTORICAL RECORD VS OPPOSITION
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 2. Historical Record vs Opposition\n")
    md.append(
        "*Combined records for franchise aliases (e.g., Delhi Capitals + Delhi Daredevils)*\n"
    )

    # Get team vs team records
    for opp_name, opp_aliases in FRANCHISE_ALIASES.items():
        if opp_name == team_name:
            continue

        opp_clause = ", ".join([f"'{a}'" for a in opp_aliases])

        # Get head-to-head match results
        h2h = conn.execute(f"""
            WITH ipl_matches AS (
                SELECT dm.match_id, dm.winner_id, dt1.team_name as team1, dt2.team_name as team2,
                       dtw.team_name as winner, dm.venue_id
                FROM dim_match dm
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
                JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
                LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
            )
            SELECT
                COUNT(*) as matches,
                SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN winner IN ({opp_clause}) THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN winner IS NULL THEN 1 ELSE 0 END) as no_result
            FROM ipl_matches
            WHERE (team1 IN ({alias_clause}) AND team2 IN ({opp_clause}))
               OR (team1 IN ({opp_clause}) AND team2 IN ({alias_clause}))
        """).fetchone()

        if h2h and h2h[0] > 0:
            matches, wins, losses, nr = h2h
            opp_code = TEAM_CODES.get(opp_name, opp_name[:3].upper())
            md.append(f"### vs {opp_name} ({opp_code})")
            md.append(f"**Record:** {wins}W - {losses}L - {nr}NR (Matches: {matches})")
            win_pct = (wins / matches * 100) if matches > 0 else 0
            md.append(f"**Win %:** {win_pct:.1f}%\n")

    # ==========================================================================
    # SECTION 3: HISTORICAL TRENDS (2023-2025)
    # ==========================================================================
    md.append("\n---\n")
    historical_trends = generate_historical_trends(conn, team_name, alias_clause)
    md.extend(historical_trends)

    # ==========================================================================
    # SECTION 3.5: TEAM PHASE APPROACH (PP / MIDDLE / DEATH)
    # ==========================================================================
    team_phase = generate_team_phase_approach(conn, team_name, alias_clause)
    md.extend(team_phase)

    # ==========================================================================
    # SECTION 4: VENUE ANALYSIS (COMPREHENSIVE SECTION)
    # ==========================================================================
    md.append("\n---\n")
    venue_analysis = generate_venue_analysis(conn, team_name, alias_clause)
    md.extend(venue_analysis)

    # ==========================================================================
    # SECTION 5: SQUAD BATTING ANALYSIS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 5. Squad Batting Analysis\n")

    # Career batting stats
    md.append("### 5.1 IPL Career Batting\n")

    batting = conn.execute(f"""
        SELECT player_name, role, price_cr,
               ipl_innings, ipl_runs, ipl_balls, ipl_sr, ipl_avg,
               ipl_boundary_pct, ipl_dot_pct, ipl_fifties, ipl_hundreds, ipl_sample_size
        FROM analytics_ipl_squad_batting
        WHERE team_name = '{team_name}'
        ORDER BY ipl_runs DESC NULLS LAST
    """).fetchall()

    md.append(
        "| Player | Role | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | 50s | 100s | Sample |"
    )
    md.append(
        "|--------|------|-----|------|-------|-----|-----|--------|------|-----|------|--------|"
    )
    for row in batting:
        (
            name,
            role,
            price,
            inn,
            runs,
            balls,
            sr,
            avg,
            bound,
            dot,
            fifties,
            hundreds,
            sample,
        ) = row
        md.append(
            f"| {name} | {role} | {inn or 0} | {runs or 0} | {balls or 0} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {dot or '-'} | {fifties or 0} | {hundreds or 0} | {sample or '-'} |"
        )

    # Phase-wise batting
    md.append("\n### 5.2 Phase-wise Batting (Qualified players)\n")

    phase_batting = conn.execute(f"""
        SELECT player_name, match_phase, innings, runs, balls_faced, strike_rate,
               batting_average, boundary_pct, dot_ball_pct, sample_size
        FROM analytics_ipl_squad_batting_phase
        WHERE team_name = '{team_name}'
          AND sample_size IN ('MEDIUM', 'HIGH')
        ORDER BY player_name,
            CASE match_phase WHEN 'powerplay' THEN 1 WHEN 'middle' THEN 2 WHEN 'death' THEN 3 END
    """).fetchall()

    md.append("| Player | Phase | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | Sample |")
    md.append("|--------|-------|-----|------|-------|-----|-----|--------|------|--------|")
    for row in phase_batting:
        name, phase, inn, runs, balls, sr, avg, bound, dot, sample = row
        md.append(
            f"| {name} | {phase} | {inn or 0} | {runs or 0} | {balls or 0} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {dot or '-'} | {sample or '-'} |"
        )

    # ==========================================================================
    # SECTION 6: SQUAD BOWLING ANALYSIS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 6. Squad Bowling Analysis\n")

    # Career bowling stats
    md.append("### 6.1 IPL Career Bowling\n")

    bowling = conn.execute(f"""
        SELECT player_name, role, bowling_type, price_cr,
               ipl_matches, ipl_overs, ipl_wickets, ipl_economy, ipl_avg, ipl_sr,
               ipl_dot_pct, ipl_boundary_pct, ipl_sample_size
        FROM analytics_ipl_squad_bowling
        WHERE team_name = '{team_name}'
          AND ipl_matches > 0
        ORDER BY ipl_wickets DESC NULLS LAST
    """).fetchall()

    md.append(
        "| Player | Type | Matches | Overs | Wkts | Econ | Avg | SR | Dot% | Bound% | Sample |"
    )
    md.append(
        "|--------|------|---------|-------|------|------|-----|-----|------|--------|--------|"
    )
    for row in bowling:
        (
            name,
            role,
            btype,
            price,
            matches,
            overs,
            wkts,
            econ,
            avg,
            sr,
            dot,
            bound,
            sample,
        ) = row
        btype_short = (btype or "-")[:10]
        md.append(
            f"| {name} | {btype_short} | {matches or 0} | {overs or 0:.1f} | {wkts or 0} | {econ or '-'} | {avg or '-'} | {sr or '-'} | {dot or '-'} | {bound or '-'} | {sample or '-'} |"
        )

    # Phase distribution
    md.append("\n### 6.2 Bowler Phase Distribution\n")
    md.append("*Shows % of overs bowled and % of wickets taken in each phase*\n")

    phase_dist = conn.execute(f"""
        SELECT bpd.bowler_name, bpd.match_phase,
               bpd.overs, bpd.wickets, bpd.economy, bpd.dot_ball_pct,
               bpd.pct_overs_in_phase, bpd.pct_wickets_in_phase, bpd.wicket_efficiency,
               bpd.sample_size
        FROM analytics_ipl_bowler_phase_distribution_since2023 bpd
        JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bpd.sample_size IN ('MEDIUM', 'HIGH')
        ORDER BY bpd.bowler_name,
            CASE bpd.match_phase WHEN 'powerplay' THEN 1 WHEN 'middle' THEN 2 WHEN 'death' THEN 3 END
    """).fetchall()

    md.append(
        "| Bowler | Phase | Overs | Wkts | Econ | Dot% | %Overs | %Wkts | Efficiency | Sample |"
    )
    md.append(
        "|--------|-------|-------|------|------|------|--------|-------|------------|--------|"
    )
    for row in phase_dist:
        name, phase, overs, wkts, econ, dot, pct_ov, pct_wk, eff, sample = row
        eff_str = f"+{eff}" if eff and eff > 0 else str(eff or "-")
        md.append(
            f"| {name} | {phase} | {overs or 0:.1f} | {wkts or 0} | {econ or '-'} | {dot or '-'} | {pct_ov or '-'}% | {pct_wk or '-'}% | {eff_str} | {sample or '-'} |"
        )

    # ==========================================================================
    # SECTION 7: KEY PLAYER VS OPPOSITION MATCHUPS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 7. Key Batter vs Opposition\n")
    md.append("*Top batters' performance against each IPL team*\n")

    # Get top 5 batters by runs (using career threshold from config)
    top_batters = execute_query_safe(
        conn,
        f"""
        SELECT DISTINCT sq.player_id, sq.player_name
        FROM ipl_2026_squads sq
        JOIN analytics_ipl_batting_career_since2023 bc ON sq.player_id = bc.player_id
        WHERE sq.team_name = '{team_name}'
          AND bc.runs > {Thresholds.MIN_RUNS_CAREER}
        ORDER BY bc.runs DESC
        LIMIT 5
    """,
        default=[],
    )

    for batter_id, batter_name in top_batters:
        md.append(f"\n### {batter_name}\n")

        vs_team = conn.execute(f"""
            SELECT opposition, innings, runs, balls, strike_rate, average,
                   boundary_pct, dot_ball_pct, dismissals, sample_size
            FROM analytics_ipl_batter_vs_team_since2023
            WHERE batter_id = '{batter_id}'
              AND sample_size IN ('MEDIUM', 'HIGH')
            ORDER BY runs DESC
        """).fetchall()

        if vs_team:
            md.append(
                "| Opposition | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | Outs | Sample |"
            )
            md.append(
                "|------------|-----|------|-------|-----|-----|--------|------|------|--------|"
            )
            for row in vs_team:
                opp, inn, runs, balls, sr, avg, bound, dot, outs, sample = row
                md.append(
                    f"| {opp} | {inn} | {runs} | {balls} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {dot or '-'} | {outs} | {sample or '-'} |"
                )

    # ==========================================================================
    # SECTION 8: KEY BOWLER VS OPPOSITION
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 8. Key Bowler vs Opposition\n")

    # Get top 5 bowlers by wickets (using career threshold from config)
    top_bowlers = execute_query_safe(
        conn,
        f"""
        SELECT DISTINCT sq.player_id, sq.player_name
        FROM ipl_2026_squads sq
        JOIN analytics_ipl_bowling_career_since2023 bc ON sq.player_id = bc.player_id
        WHERE sq.team_name = '{team_name}'
          AND bc.wickets > {Thresholds.MIN_WICKETS_CAREER}
        ORDER BY bc.wickets DESC
        LIMIT 5
    """,
        default=[],
    )

    for bowler_id, bowler_name in top_bowlers:
        md.append(f"\n### {bowler_name}\n")

        vs_team = conn.execute(f"""
            SELECT opposition, matches, balls, runs_conceded, wickets, economy,
                   average, strike_rate, dot_ball_pct, boundary_conceded_pct, sample_size
            FROM analytics_ipl_bowler_vs_team_since2023
            WHERE bowler_id = '{bowler_id}'
              AND sample_size IN ('MEDIUM', 'HIGH')
            ORDER BY wickets DESC
        """).fetchall()

        if vs_team:
            md.append(
                "| Opposition | Matches | Balls | Runs | Wkts | Econ | Avg | SR | Dot% | Bound% | Sample |"
            )
            md.append(
                "|------------|---------|-------|------|------|------|-----|-----|------|--------|--------|"
            )
            for row in vs_team:
                opp, m, balls, runs, wkts, econ, avg, sr, dot, bound, sample = row
                md.append(
                    f"| {opp} | {m} | {balls} | {runs} | {wkts} | {econ or '-'} | {avg or '-'} | {sr or '-'} | {dot or '-'} | {bound or '-'} | {sample or '-'} |"
                )

    # ==========================================================================
    # SECTION 9: PLAYER VENUE PERFORMANCE
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 9. Key Player Venue Performance\n")

    # Top batter venue stats
    md.append("### 9.1 Top Batters by Venue\n")

    batter_venues = conn.execute(f"""
        SELECT bv.batter_name, bv.venue, bv.innings, bv.runs, bv.balls,
               bv.strike_rate, bv.average, bv.boundary_pct, bv.sample_size
        FROM analytics_ipl_batter_venue_since2023 bv
        JOIN ipl_2026_squads sq ON bv.batter_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bv.sample_size IN ('MEDIUM', 'HIGH')
          AND bv.runs >= 100
        ORDER BY bv.batter_name, bv.runs DESC
    """).fetchall()

    if batter_venues:
        md.append("| Player | Venue | Inn | Runs | Balls | SR | Avg | Bound% | Sample |")
        md.append("|--------|-------|-----|------|-------|-----|-----|--------|--------|")
        for row in batter_venues:
            name, venue, inn, runs, balls, sr, avg, bound, sample = row
            venue_short = venue[:35] + "..." if len(venue) > 35 else venue
            md.append(
                f"| {name} | {venue_short} | {inn} | {runs} | {balls} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {sample or '-'} |"
            )

    # ==========================================================================
    # SECTION 10: ANDY FLOWER'S TACTICAL INSIGHTS (REWRITTEN)
    # ==========================================================================
    md.append("\n---\n")
    tactical_section = generate_tactical_insights(conn, team_name)
    md.extend(tactical_section)

    # ==========================================================================
    # SECTION 11: PRESSURE PERFORMANCE
    # ==========================================================================
    md.append("\n---\n")
    pressure_section = generate_pressure_performance(conn, team_name)
    md.extend(pressure_section)

    # ==========================================================================
    # SECTION 12: UNCAPPED WATCH (TKT-182)
    # ==========================================================================
    md.append("\n---\n")
    uncapped_section = generate_uncapped_watch(conn, team_name)
    md.extend(uncapped_section)

    # ==========================================================================
    # SECTION 13: CROSS-TOURNAMENT INTELLIGENCE (TKT-190)
    # ==========================================================================
    md.append("\n---\n")
    cross_tournament_section = generate_cross_tournament_intelligence(conn, team_name)
    md.extend(cross_tournament_section)

    md.append("\n---\n")
    md.append(f"*End of {team_name} Stat Pack*")

    return "\n".join(md)


def main() -> int:
    """
    Generate stat packs for all 10 IPL 2026 teams.

    This is the main entry point for the stat pack generator. It:
    1. Validates database existence
    2. Loads player tags from JSON
    3. Iterates through all teams in ipl_2026_squads
    4. Generates and writes markdown stat packs

    Returns:
        0 if all teams generated successfully, 1 if any failed
    """
    logger.info("=" * 60)
    logger.info("Cricket Playbook - IPL 2026 Stat Pack Generator")
    logger.info("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    logger.debug("Output directory: %s", OUTPUT_DIR)

    # Validate database exists
    if not DB_PATH.exists():
        logger.error("Database not found at %s", DB_PATH)
        return 1

    # =========================================================================
    # PRE-EXECUTION HOOK: ML Health Check (TKT-073)
    # =========================================================================
    if ML_HEALTH_CHECK_AVAILABLE:
        logger.info("Running ML health check before stat pack generation...")
        try:
            health_result = ml_health_check(verbose=False, export=False)
            health_status = health_result.get("status", "UNKNOWN")

            if "CRITICAL" in health_status:
                logger.error("ML health check CRITICAL - aborting stat pack generation")
                logger.error(
                    "Run 'python scripts/ml_ops/run_health_check.py --verbose' for details"
                )
                return 1
            elif "DEGRADED" in health_status:
                logger.warning("ML health check DEGRADED - proceeding with warnings")
            else:
                logger.info("ML health check PASSED (%s)", health_status)
        except Exception as e:
            logger.warning("ML health check failed (non-blocking): %s", str(e))
    else:
        logger.debug("ML health check not available - skipping pre-execution hook")

    # Connect to database with context manager pattern
    logger.info("Connecting to database: %s", DB_PATH)
    conn: Optional[duckdb.DuckDBPyConnection] = None

    try:
        conn = duckdb.connect(str(DB_PATH), read_only=True)

        # Load player tags
        logger.info("Loading player tags...")
        tags_data = load_player_tags()
        tags_lookup = get_player_tags_lookup(tags_data)
        logger.info("Loaded tags for %d players", len(tags_lookup))

        # Get all teams
        teams = conn.execute("""
            SELECT DISTINCT team_name FROM ipl_2026_squads ORDER BY team_name
        """).fetchall()

        if not teams:
            logger.error("No teams found in ipl_2026_squads table")
            return 1

        logger.info("Generating stat packs for %d teams...", len(teams))

        success_count = 0
        error_count = 0

        for (team_name,) in teams:
            team_code = TEAM_CODES.get(team_name, team_name[:3].upper())
            logger.debug("Processing team: %s (%s)", team_name, team_code)

            try:
                stat_pack = generate_team_stat_pack(conn, team_name, tags_lookup)

                # Write to team subdirectory (stat_packs/MI/MI_stat_pack.md)
                filename = f"{team_code}_stat_pack.md"
                team_dir = OUTPUT_DIR / team_code
                team_dir.mkdir(exist_ok=True)
                filepath = team_dir / filename
                filepath.write_text(stat_pack)

                logger.info("Generated %s -> %s", team_code, filepath)
                success_count += 1
            except Exception as e:
                logger.error("Failed to generate stat pack for %s: %s", team_name, str(e))
                logger.exception("Full traceback:")
                error_count += 1

        logger.info("=" * 60)
        logger.info("Generation complete: %d succeeded, %d failed", success_count, error_count)
        logger.info("Stat packs generated in: %s", OUTPUT_DIR)
        logger.info("=" * 60)

        return 0 if error_count == 0 else 1

    except Exception as e:
        logger.error("Fatal error during stat pack generation: %s", str(e))
        logger.exception("Full traceback:")
        return 1

    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


if __name__ == "__main__":
    exit(main())
