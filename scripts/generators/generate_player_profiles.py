#!/usr/bin/env python3
"""
Cricket Playbook - IPL 2026 Player Profile Generator
=====================================================
Generates pre-computed JSON player profiles for all 231 IPL 2026 squad players.

Covers:
  - TKT-196: Profile schema definition
  - TKT-197: Batter profiles (career, phase, vs bowling type, vs teams, entry points)
  - TKT-198: Bowler profiles (career, phase, vs batting hand, vs teams, classification)
  - TKT-199: All-rounder profiles (both batting and bowling sections)

Data Sources:
  - DuckDB analytics views (since 2023)
  - Squad CSV, contract CSV
  - Player tags JSON, clustering CSV
  - Entry points CSV, bowler handedness matchup CSV

Author: Stephen Curry (Analytics Lead) & Brock Purdy (Data Pipeline)
Domain Review: Andy Flower
Architecture: Brad Stevens
Version: 1.0.0
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

from scripts.utils.logging_config import setup_logger

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
SQUADS_PATH = PROJECT_DIR / "data" / "ipl_2026_squads.csv"
CONTRACTS_PATH = PROJECT_DIR / "data" / "ipl_2026_player_contracts.csv"
TAGS_PATH = PROJECT_DIR / "outputs" / "tags" / "player_tags_2023.json"
CLUSTERING_PATH = PROJECT_DIR / "outputs" / "tags" / "player_clustering_2023.csv"
ENTRY_POINTS_PATH = PROJECT_DIR / "outputs" / "matchups" / "batter_entry_points_2023.csv"
HANDEDNESS_PATH = PROJECT_DIR / "outputs" / "matchups" / "bowler_handedness_matchup_2023.csv"

OUTPUT_DIR = PROJECT_DIR / "outputs" / "player_profiles"
OUTPUT_FILE = OUTPUT_DIR / "player_profiles_2023.json"
BY_TEAM_DIR = OUTPUT_DIR / "by_team"

VERSION = "1.0.0"

# Standard IPL team abbreviation mapping (overrides dim_team where needed)
IPL_TEAM_ABBREV = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bengaluru": "RCB",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
}

logger = setup_logger(__name__)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def _round(value: Any, decimals: int = 2) -> Any:
    """Round a numeric value to the specified decimal places, handling None/NaN."""
    if value is None:
        return None
    try:
        import math

        fval = float(value)
        if math.isnan(fval) or math.isinf(fval):
            return None
        return round(fval, decimals)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert a value to int, returning None for non-numeric values."""
    if value is None:
        return None
    try:
        import math

        fval = float(value)
        if math.isnan(fval) or math.isinf(fval):
            return None
        return int(fval)
    except (TypeError, ValueError):
        return None


def _get_team_abbrev(team_name: str) -> str:
    """Get the standard IPL team abbreviation for a team name."""
    return IPL_TEAM_ABBREV.get(team_name, team_name)


# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================


def load_squad_data() -> Dict[str, Dict]:
    """Load IPL 2026 squad data from CSV, keyed by player_id."""
    logger.info("Loading squad data from %s", SQUADS_PATH)
    squads = {}
    with open(SQUADS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["player_id"].strip()
            squads[pid] = {
                "team_name": row["team_name"].strip(),
                "player_name": row["player_name"].strip(),
                "player_id": pid,
                "nationality": row["nationality"].strip(),
                "age": _safe_int(row.get("age")),
                "role": row["role"].strip(),
                "bowling_arm": row.get("bowling_arm", "").strip() or None,
                "bowling_type": row.get("bowling_type", "").strip() or None,
                "batting_hand": row.get("batting_hand", "").strip() or None,
                "batter_classification": row.get("batter_classification", "").strip() or None,
                "bowler_classification": row.get("bowler_classification", "").strip() or None,
                "batter_tags": [
                    t.strip() for t in row.get("batter_tags", "").split("|") if t.strip()
                ],
                "bowler_tags": [
                    t.strip() for t in row.get("bowler_tags", "").split("|") if t.strip()
                ],
                "is_captain": row.get("is_captain", "").strip().upper() == "TRUE",
            }
    logger.info("Loaded %d squad players", len(squads))
    return squads


def load_contract_data() -> Dict[str, Dict]:
    """Load contract data from CSV, keyed by (team_name, player_name) tuple.

    Since the contracts CSV lacks player_id, we create a lookup by
    (team_name, player_name) for matching.
    """
    logger.info("Loading contract data from %s", CONTRACTS_PATH)
    contracts = {}
    with open(CONTRACTS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["team_name"].strip(), row["player_name"].strip())
            contracts[key] = {
                "price_cr": _round(row.get("price_cr", 0)),
                "acquisition_type": row.get("acquisition_type", "").strip() or None,
            }
    logger.info("Loaded %d contract entries", len(contracts))
    return contracts


def load_batting_career(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Load career batting stats from DuckDB, keyed by player_id."""
    logger.info("Loading batting career stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_batting_career_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_batting_career_since2023 LIMIT 0"
        ).description
    ]
    result = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["player_id"]
        result[pid] = {
            "innings": _safe_int(d.get("innings")),
            "runs": _safe_int(d.get("runs")),
            "balls_faced": _safe_int(d.get("balls_faced")),
            "average": _round(d.get("batting_average")),
            "strike_rate": _round(d.get("strike_rate")),
            "fifties": _safe_int(d.get("fifties")),
            "hundreds": _safe_int(d.get("hundreds")),
            "fours": _safe_int(d.get("fours")),
            "sixes": _safe_int(d.get("sixes")),
            "boundary_pct": _round(d.get("boundary_pct")),
            "dot_ball_pct": _round(d.get("dot_ball_pct")),
            "highest_score": _safe_int(d.get("highest_score")),
            "sample_size": d.get("sample_size"),
        }
    logger.info("Loaded batting career stats for %d players", len(result))
    return result


def load_bowling_career(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Load career bowling stats from DuckDB, keyed by player_id."""
    logger.info("Loading bowling career stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_bowling_career_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_bowling_career_since2023 LIMIT 0"
        ).description
    ]
    result = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["player_id"]
        result[pid] = {
            "matches": _safe_int(d.get("matches_bowled")),
            "wickets": _safe_int(d.get("wickets")),
            "overs": _round(d.get("overs_bowled")),
            "runs_conceded": _safe_int(d.get("runs_conceded")),
            "economy": _round(d.get("economy_rate")),
            "average": _round(d.get("bowling_average")),
            "strike_rate": _round(d.get("bowling_strike_rate")),
            "dot_ball_pct": _round(d.get("dot_ball_pct")),
            "boundary_conceded_pct": _round(d.get("boundary_conceded_pct")),
            "sample_size": d.get("sample_size"),
        }
    logger.info("Loaded bowling career stats for %d players", len(result))
    return result


def load_batter_phase(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Load phase-wise batting stats, keyed by player_id -> {powerplay, middle, death}."""
    logger.info("Loading batter phase stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_batter_phase_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_batter_phase_since2023 LIMIT 0"
        ).description
    ]
    result: Dict[str, Dict] = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["player_id"]
        phase = d["match_phase"]
        if pid not in result:
            result[pid] = {}
        result[pid][phase] = {
            "sr": _round(d.get("strike_rate")),
            "avg": _round(d.get("batting_average")),
            "boundary_pct": _round(d.get("boundary_pct")),
            "balls": _safe_int(d.get("balls_faced")),
            "runs": _safe_int(d.get("runs")),
            "sample_size": d.get("sample_size"),
        }
    logger.info("Loaded batter phase stats for %d players", len(result))
    return result


def load_bowler_phase(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Load phase-wise bowling stats, keyed by player_id -> {powerplay, middle, death}."""
    logger.info("Loading bowler phase stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_bowler_phase_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_bowler_phase_since2023 LIMIT 0"
        ).description
    ]
    result: Dict[str, Dict] = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["player_id"]
        phase = d["match_phase"]
        if pid not in result:
            result[pid] = {}
        overs_val = d.get("overs") or 0
        wickets_val = d.get("wickets") or 0
        balls_approx = float(overs_val) * 6 if overs_val else 0
        bowl_sr = round(balls_approx / wickets_val, 1) if wickets_val > 0 else None
        result[pid][phase] = {
            "economy": _round(d.get("economy_rate")),
            "wickets": _safe_int(d.get("wickets")),
            "overs": _round(d.get("overs")),
            "sr": bowl_sr,
            "avg": _round(d.get("bowling_average")),
            "sample_size": d.get("sample_size"),
        }
    logger.info("Loaded bowler phase stats for %d players", len(result))
    return result


def load_batter_vs_teams(conn: duckdb.DuckDBPyConnection) -> Dict[str, List[Dict]]:
    """Load batter vs team matchup stats, keyed by player_id -> list of matchups."""
    logger.info("Loading batter vs team stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_batter_vs_team_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_batter_vs_team_since2023 LIMIT 0"
        ).description
    ]
    result: Dict[str, List[Dict]] = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["batter_id"]
        if pid not in result:
            result[pid] = []
        result[pid].append(
            {
                "team": _get_team_abbrev(d["opposition"]),
                "sr": _round(d.get("strike_rate")),
                "avg": _round(d.get("average")),
                "innings": _safe_int(d.get("innings")),
            }
        )
    logger.info("Loaded batter vs team data for %d players", len(result))
    return result


def load_bowler_vs_teams(conn: duckdb.DuckDBPyConnection) -> Dict[str, List[Dict]]:
    """Load bowler vs team matchup stats, keyed by player_id -> list of matchups."""
    logger.info("Loading bowler vs team stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_bowler_vs_team_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_bowler_vs_team_since2023 LIMIT 0"
        ).description
    ]
    result: Dict[str, List[Dict]] = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["bowler_id"]
        if pid not in result:
            result[pid] = []
        result[pid].append(
            {
                "team": _get_team_abbrev(d["opposition"]),
                "economy": _round(d.get("economy")),
                "sr": _round(d.get("strike_rate")),
                "wickets": _safe_int(d.get("wickets")),
                "overs": _round(float(d.get("balls", 0) or 0) / 6, 1),
                "balls": _safe_int(d.get("balls")),
            }
        )
    logger.info("Loaded bowler vs team data for %d players", len(result))
    return result


def load_batter_vs_bowling_type(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Load batter vs bowling type stats, keyed by player_id -> {type: stats}."""
    logger.info("Loading batter vs bowling type stats...")
    rows = conn.execute("SELECT * FROM analytics_ipl_batter_vs_bowler_type_since2023").fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_batter_vs_bowler_type_since2023 LIMIT 0"
        ).description
    ]
    result: Dict[str, Dict] = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["batter_id"]
        btype = d["bowler_type"]
        if pid not in result:
            result[pid] = {}
        result[pid][btype] = {
            "sr": _round(d.get("strike_rate")),
            "avg": _round(d.get("average")),
            "balls": _safe_int(d.get("balls")),
            "sample_size": d.get("sample_size"),
        }
    logger.info("Loaded batter vs bowling type for %d players", len(result))
    return result


def load_bowler_vs_handedness(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Load bowler vs batter handedness from DuckDB, keyed by player_id."""
    logger.info("Loading bowler vs handedness stats from DuckDB...")
    rows = conn.execute(
        "SELECT * FROM analytics_ipl_bowler_vs_batter_handedness_since2023"
    ).fetchall()
    cols = [
        desc[0]
        for desc in conn.execute(
            "SELECT * FROM analytics_ipl_bowler_vs_batter_handedness_since2023 LIMIT 0"
        ).description
    ]
    result: Dict[str, Dict] = {}
    for row in rows:
        d = dict(zip(cols, row))
        pid = d["bowler_id"]
        hand = d["batting_hand"]
        if pid not in result:
            result[pid] = {}
        result[pid][hand] = {
            "economy": _round(d.get("economy")),
            "sr": _round(d.get("strike_rate")),
            "wickets": _safe_int(d.get("wickets")),
            "balls": _safe_int(d.get("balls")),
            "sample_size": d.get("sample_size"),
        }
    logger.info("Loaded bowler vs handedness for %d players", len(result))
    return result


def load_bowler_handedness_csv() -> Dict[str, Dict]:
    """Load bowler handedness matchup from pre-computed CSV, keyed by bowler_id.

    This CSV has pre-computed LHB/RHB stats and handedness_tags.
    """
    logger.info("Loading bowler handedness matchup CSV from %s", HANDEDNESS_PATH)
    result = {}
    with open(HANDEDNESS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bid = row["bowler_id"].strip()
            result[bid] = {
                "lhb_balls": _safe_int(row.get("lhb_balls")),
                "lhb_economy": _round(row.get("lhb_economy")),
                "lhb_strike_rate": _round(row.get("lhb_strike_rate")),
                "lhb_wickets": _safe_int(row.get("lhb_wickets")),
                "rhb_balls": _safe_int(row.get("rhb_balls")),
                "rhb_economy": _round(row.get("rhb_economy")),
                "rhb_strike_rate": _round(row.get("rhb_strike_rate")),
                "rhb_wickets": _safe_int(row.get("rhb_wickets")),
                "economy_diff": _round(row.get("economy_diff")),
                "strike_rate_diff": _round(row.get("strike_rate_diff")),
                "handedness_tags": [
                    t.strip() for t in row.get("handedness_tags", "").split(",") if t.strip()
                ],
            }
    logger.info("Loaded handedness matchup for %d bowlers", len(result))
    return result


def load_tags() -> Dict[str, Dict]:
    """Load player tags from JSON, keyed by player_id -> {batter_tags, bowler_tags}."""
    logger.info("Loading player tags from %s", TAGS_PATH)
    result: Dict[str, Dict] = {}
    with open(TAGS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for batter in data.get("batters", []):
        pid = batter["player_id"]
        if pid not in result:
            result[pid] = {"batter_tags": [], "bowler_tags": []}
        result[pid]["batter_tags"] = batter.get("tags", [])

    for bowler in data.get("bowlers", []):
        pid = bowler["player_id"]
        if pid not in result:
            result[pid] = {"batter_tags": [], "bowler_tags": []}
        result[pid]["bowler_tags"] = bowler.get("tags", [])

    logger.info("Loaded tags for %d players", len(result))
    return result


def load_clusters() -> Dict[str, str]:
    """Load cluster labels from CSV, keyed by player_id -> cluster_label."""
    logger.info("Loading cluster labels from %s", CLUSTERING_PATH)
    result = {}
    with open(CLUSTERING_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["player_id"].strip()
            result[pid] = row["cluster_label"].strip()
    logger.info("Loaded cluster labels for %d players", len(result))
    return result


def load_entry_points() -> Dict[str, Dict]:
    """Load batter entry point data from CSV, keyed by player_id."""
    logger.info("Loading batter entry points from %s", ENTRY_POINTS_PATH)
    result = {}
    with open(ENTRY_POINTS_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["player_id"].strip()
            result[pid] = {
                "classification": row.get("entry_point_classification", "").strip() or None,
                "mode_batting_position": _safe_int(row.get("mode_batting_position")),
                "mean_batting_position": _round(row.get("mean_batting_position"), 1),
                "avg_entry_ball": _round(row.get("avg_entry_ball"), 1),
                "innings": _safe_int(row.get("innings")),
            }
    logger.info("Loaded entry points for %d batters", len(result))
    return result


# =============================================================================
# PROFILE BUILDING
# =============================================================================


def _determine_player_type(role: str) -> str:
    """Determine the player_type based on squad role."""
    role_lower = role.lower().strip()
    if role_lower in ("batter", "wicketkeeper"):
        return "batter"
    elif role_lower == "bowler":
        return "bowler"
    elif role_lower == "all-rounder":
        return "allrounder"
    return "batter"  # fallback


def _build_batter_vs_teams(matchups: List[Dict]) -> Dict[str, List[Dict]]:
    """Build best/worst vs teams for batters.

    Best: top 3 by strike_rate descending (min 2 innings).
    Worst: bottom 3 by strike_rate ascending (min 2 innings).
    """
    qualified = [
        m
        for m in matchups
        if m.get("innings") is not None and m["innings"] >= 2 and m.get("sr") is not None
    ]
    if not qualified:
        return {"best": [], "worst": []}

    by_sr_desc = sorted(qualified, key=lambda x: x["sr"], reverse=True)
    by_sr_asc = sorted(qualified, key=lambda x: x["sr"])

    best = [
        {"team": m["team"], "sr": m["sr"], "avg": m.get("avg"), "innings": m["innings"]}
        for m in by_sr_desc[:3]
    ]
    worst = [
        {"team": m["team"], "sr": m["sr"], "avg": m.get("avg"), "innings": m["innings"]}
        for m in by_sr_asc[:3]
    ]

    return {"best": best, "worst": worst}


def _build_bowler_vs_teams(matchups: List[Dict]) -> Dict[str, List[Dict]]:
    """Build best/worst vs teams for bowlers.

    Best: top 3 by economy ascending (min 18 balls / 3 overs).
    Worst: bottom 3 by economy descending (min 18 balls / 3 overs).
    """
    qualified = [
        m
        for m in matchups
        if m.get("balls") is not None and m["balls"] >= 18 and m.get("economy") is not None
    ]
    if not qualified:
        return {"best": [], "worst": []}

    by_econ_asc = sorted(qualified, key=lambda x: x["economy"])
    by_econ_desc = sorted(qualified, key=lambda x: x["economy"], reverse=True)

    best = [
        {
            "team": m["team"],
            "economy": m["economy"],
            "sr": m.get("sr"),
            "wickets": m.get("wickets"),
            "overs": m["overs"],
        }
        for m in by_econ_asc[:3]
    ]
    worst = [
        {
            "team": m["team"],
            "economy": m["economy"],
            "sr": m.get("sr"),
            "wickets": m.get("wickets"),
            "overs": m["overs"],
        }
        for m in by_econ_desc[:3]
    ]

    return {"best": best, "worst": worst}


def _merge_tags(json_tags: List[str], csv_tags: List[str]) -> List[str]:
    """Merge and deduplicate tags from JSON and CSV sources, preserving order."""
    seen = set()
    merged = []
    for tag in json_tags + csv_tags:
        tag_upper = tag.strip().upper()
        if tag_upper and tag_upper not in seen:
            seen.add(tag_upper)
            merged.append(tag.strip().upper())
    return merged


def _build_batting_section(
    player_id: str,
    batting_career: Dict[str, Dict],
    batter_phase: Dict[str, Dict],
    batter_vs_teams: Dict[str, List[Dict]],
    batter_vs_bowling_type: Dict[str, Dict],
    entry_points: Dict[str, Dict],
    batter_tags: List[str],
) -> Optional[Dict]:
    """Build the batting section of a player profile."""
    career = batting_career.get(player_id)
    if career is None:
        return None

    # Phase data
    phase_data = batter_phase.get(player_id, {})
    phase = {}
    for p in ("powerplay", "middle", "death"):
        if p in phase_data:
            phase[p] = phase_data[p]
        else:
            phase[p] = {
                "sr": None,
                "avg": None,
                "boundary_pct": None,
                "balls": None,
                "runs": None,
                "sample_size": None,
            }

    # Vs bowling type
    vs_bt = batter_vs_bowling_type.get(player_id, {})

    # Vs teams
    matchups = batter_vs_teams.get(player_id, [])
    vs_teams = _build_batter_vs_teams(matchups)

    # Entry point
    entry = entry_points.get(player_id)

    return {
        "career": career,
        "phase": phase,
        "vs_bowling_type": vs_bt,
        "vs_teams": vs_teams,
        "entry_point": entry,
        "tags": batter_tags,
    }


def _build_bowling_section(
    player_id: str,
    bowling_career: Dict[str, Dict],
    bowler_phase: Dict[str, Dict],
    bowler_vs_teams: Dict[str, List[Dict]],
    bowler_vs_hand_db: Dict[str, Dict],
    bowler_hand_csv: Dict[str, Dict],
    squad_info: Dict,
    bowler_tags: List[str],
    cluster_label: Optional[str],
) -> Optional[Dict]:
    """Build the bowling section of a player profile."""
    career = bowling_career.get(player_id)
    if career is None:
        return None

    # Phase data
    phase_data = bowler_phase.get(player_id, {})
    phase = {}
    for p in ("powerplay", "middle", "death"):
        if p in phase_data:
            phase[p] = phase_data[p]
        else:
            phase[p] = {
                "economy": None,
                "wickets": None,
                "overs": None,
                "sr": None,
                "sample_size": None,
            }

    # Vs batting hand -- prefer the CSV data which has more structure
    vs_hand: Dict[str, Any] = {}
    csv_hand = bowler_hand_csv.get(player_id)
    db_hand = bowler_vs_hand_db.get(player_id, {})

    if csv_hand:
        # Build from CSV
        vs_hand["Left-hand"] = {
            "economy": csv_hand.get("lhb_economy"),
            "sr": csv_hand.get("lhb_strike_rate"),
            "wickets": csv_hand.get("lhb_wickets"),
            "balls": csv_hand.get("lhb_balls"),
            "sample_size": _classify_sample(csv_hand.get("lhb_balls")),
        }
        vs_hand["Right-hand"] = {
            "economy": csv_hand.get("rhb_economy"),
            "sr": csv_hand.get("rhb_strike_rate"),
            "wickets": csv_hand.get("rhb_wickets"),
            "balls": csv_hand.get("rhb_balls"),
            "sample_size": _classify_sample(csv_hand.get("rhb_balls")),
        }
        # Merge handedness tags into bowler tags
        h_tags = csv_hand.get("handedness_tags", [])
        if h_tags:
            for ht in h_tags:
                ht_clean = ht.strip().upper()
                if ht_clean and ht_clean not in [t.upper() for t in bowler_tags]:
                    bowler_tags.append(ht_clean)
    elif db_hand:
        # Fall back to DuckDB data
        for hand_key in ("Left-hand", "Right-hand"):
            if hand_key in db_hand:
                vs_hand[hand_key] = db_hand[hand_key]
            else:
                vs_hand[hand_key] = {
                    "economy": None,
                    "sr": None,
                    "wickets": None,
                    "balls": None,
                    "sample_size": None,
                }

    # Vs teams
    matchups = bowler_vs_teams.get(player_id, [])
    vs_teams = _build_bowler_vs_teams(matchups)

    # Classification
    classification = {
        "arm": squad_info.get("bowling_arm"),
        "type": squad_info.get("bowling_type"),
        "archetype": cluster_label if cluster_label else squad_info.get("bowler_classification"),
    }

    return {
        "career": career,
        "phase": phase,
        "vs_batting_hand": vs_hand,
        "vs_teams": vs_teams,
        "classification": classification,
        "tags": bowler_tags,
    }


def _classify_sample(balls: Optional[int]) -> Optional[str]:
    """Classify sample size based on balls count."""
    if balls is None:
        return None
    if balls >= 200:
        return "HIGH"
    elif balls >= 50:
        return "MEDIUM"
    else:
        return "LOW"


def build_profile(
    player_id: str,
    squad_data: Dict[str, Dict],
    contract_data: Dict[str, Dict],
    batting_career: Dict[str, Dict],
    bowling_career: Dict[str, Dict],
    batter_phase: Dict[str, Dict],
    bowler_phase: Dict[str, Dict],
    batter_vs_teams: Dict[str, List[Dict]],
    bowler_vs_teams: Dict[str, List[Dict]],
    batter_vs_bowling_type: Dict[str, Dict],
    bowler_vs_hand_db: Dict[str, Dict],
    bowler_hand_csv: Dict[str, Dict],
    tags_data: Dict[str, Dict],
    clusters: Dict[str, str],
    entry_points: Dict[str, Dict],
) -> Dict:
    """Build a complete player profile dict."""
    squad = squad_data[player_id]
    team_name = squad["team_name"]
    team_abbrev = _get_team_abbrev(team_name)
    player_type = _determine_player_type(squad["role"])

    # Contract lookup by (team_name, player_name)
    contract_key = (team_name, squad["player_name"])
    contract = contract_data.get(contract_key, {})

    # Cluster/archetype
    cluster_label = clusters.get(player_id)
    archetype = (
        cluster_label
        if cluster_label
        else (squad.get("batter_classification") or squad.get("bowler_classification"))
    )

    # Tags: merge JSON tags with CSV tags from squads
    tag_info = tags_data.get(player_id, {"batter_tags": [], "bowler_tags": []})
    merged_batter_tags = _merge_tags(
        tag_info.get("batter_tags", []),
        squad.get("batter_tags", []),
    )
    merged_bowler_tags = _merge_tags(
        tag_info.get("bowler_tags", []),
        squad.get("bowler_tags", []),
    )

    # Determine IPL data availability
    has_batting_data = player_id in batting_career
    has_bowling_data = player_id in bowling_career
    has_ipl_data = has_batting_data or has_bowling_data

    # Build profile
    profile: Dict[str, Any] = {
        "player_id": player_id,
        "player_name": squad["player_name"],
        "team_name": team_name,
        "team_abbrev": team_abbrev,
        "role": squad["role"],
        "price_cr": contract.get("price_cr"),
        "acquisition_type": contract.get("acquisition_type"),
        "nationality": squad["nationality"],
        "age": squad["age"],
        "batting_hand": squad["batting_hand"],
        "bowling_arm": squad["bowling_arm"],
        "bowling_type": squad["bowling_type"],
        "is_captain": squad["is_captain"],
        "archetype": archetype,
        "player_type": player_type,
        "has_ipl_data": has_ipl_data,
    }

    # Batting section
    if player_type == "batter":
        # Always include batting for batters
        if has_batting_data:
            profile["batting"] = _build_batting_section(
                player_id,
                batting_career,
                batter_phase,
                batter_vs_teams,
                batter_vs_bowling_type,
                entry_points,
                merged_batter_tags,
            )
        else:
            profile["batting"] = None
        profile["bowling"] = None

    elif player_type == "bowler":
        # Always include bowling for bowlers
        if has_bowling_data:
            profile["bowling"] = _build_bowling_section(
                player_id,
                bowling_career,
                bowler_phase,
                bowler_vs_teams,
                bowler_vs_hand_db,
                bowler_hand_csv,
                squad,
                merged_bowler_tags,
                cluster_label,
            )
        else:
            profile["bowling"] = None
        # Include batting if they have batting stats
        if has_batting_data:
            profile["batting"] = _build_batting_section(
                player_id,
                batting_career,
                batter_phase,
                batter_vs_teams,
                batter_vs_bowling_type,
                entry_points,
                merged_batter_tags,
            )
        else:
            profile["batting"] = None

    elif player_type == "allrounder":
        # Include both sections
        if has_batting_data:
            profile["batting"] = _build_batting_section(
                player_id,
                batting_career,
                batter_phase,
                batter_vs_teams,
                batter_vs_bowling_type,
                entry_points,
                merged_batter_tags,
            )
        else:
            profile["batting"] = None

        if has_bowling_data:
            profile["bowling"] = _build_bowling_section(
                player_id,
                bowling_career,
                bowler_phase,
                bowler_vs_teams,
                bowler_vs_hand_db,
                bowler_hand_csv,
                squad,
                merged_bowler_tags,
                cluster_label,
            )
        else:
            profile["bowling"] = None

    return profile


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================


def main() -> None:
    """Main entry point: load all data, build profiles, write output."""
    logger.info("=" * 60)
    logger.info("IPL 2026 Player Profile Generator v%s", VERSION)
    logger.info("=" * 60)

    # Ensure output directories exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BY_TEAM_DIR.mkdir(parents=True, exist_ok=True)

    # Load squad and contract data (CSV)
    squad_data = load_squad_data()
    contract_data = load_contract_data()

    # Load auxiliary CSV/JSON data
    tags_data = load_tags()
    clusters = load_clusters()
    entry_points = load_entry_points()
    bowler_hand_csv = load_bowler_handedness_csv()

    # Load DuckDB data
    logger.info("Connecting to DuckDB at %s", DB_PATH)
    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        batting_career = load_batting_career(conn)
        bowling_career = load_bowling_career(conn)
        batter_phase = load_batter_phase(conn)
        bowler_phase = load_bowler_phase(conn)
        batter_vs_teams = load_batter_vs_teams(conn)
        bowler_vs_teams = load_bowler_vs_teams(conn)
        batter_vs_bowling_type = load_batter_vs_bowling_type(conn)
        bowler_vs_hand_db = load_bowler_vs_handedness(conn)
    finally:
        conn.close()
        logger.info("DuckDB connection closed")

    # Build profiles for all squad players
    logger.info("Building profiles for %d squad players...", len(squad_data))
    profiles: Dict[str, Dict] = {}
    team_profiles: Dict[str, Dict[str, Dict]] = {}

    players_with_data = 0
    players_without_data = 0

    for player_id, squad_info in squad_data.items():
        team = squad_info["team_name"]
        logger.debug("Processing %s (%s)", squad_info["player_name"], team)

        profile = build_profile(
            player_id=player_id,
            squad_data=squad_data,
            contract_data=contract_data,
            batting_career=batting_career,
            bowling_career=bowling_career,
            batter_phase=batter_phase,
            bowler_phase=bowler_phase,
            batter_vs_teams=batter_vs_teams,
            bowler_vs_teams=bowler_vs_teams,
            batter_vs_bowling_type=batter_vs_bowling_type,
            bowler_vs_hand_db=bowler_vs_hand_db,
            bowler_hand_csv=bowler_hand_csv,
            tags_data=tags_data,
            clusters=clusters,
            entry_points=entry_points,
        )

        profiles[player_id] = profile

        if profile.get("has_ipl_data"):
            players_with_data += 1
        else:
            players_without_data += 1

        # Group by team
        team_abbrev = _get_team_abbrev(team)
        if team_abbrev not in team_profiles:
            team_profiles[team_abbrev] = {}
        team_profiles[team_abbrev][player_id] = profile

    logger.info(
        "Generated %d profiles: %d with IPL data, %d without",
        len(profiles),
        players_with_data,
        players_without_data,
    )

    # Build output payload
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
        "total_players": len(profiles),
        "players": profiles,
    }

    # Write main output file
    logger.info("Writing main output to %s", OUTPUT_FILE)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    logger.info("Main output written: %s", OUTPUT_FILE)

    # Write per-team files
    for team_abbrev, team_players in sorted(team_profiles.items()):
        team_file = BY_TEAM_DIR / f"{team_abbrev}_profiles.json"
        team_output = {
            "generated_at": output["generated_at"],
            "version": VERSION,
            "team": team_abbrev,
            "total_players": len(team_players),
            "players": team_players,
        }
        with open(team_file, "w", encoding="utf-8") as f:
            json.dump(team_output, f, indent=2, ensure_ascii=False, default=str)
        logger.info("  Written %s (%d players)", team_file.name, len(team_players))

    logger.info("=" * 60)
    logger.info("Player profile generation complete!")
    logger.info("  Total profiles: %d", len(profiles))
    logger.info("  Output: %s", OUTPUT_FILE)
    logger.info("  Per-team files: %s", BY_TEAM_DIR)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
