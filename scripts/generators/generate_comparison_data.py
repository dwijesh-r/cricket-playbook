#!/usr/bin/env python3
"""
Cricket Playbook - Player Comparison Data Generator (TKT-216 / EPIC-020)
Author: Stephen Curry (Analytics Lead)
Sprint: SPRINT-005

Queries DuckDB analytics views and produces a JavaScript data file
(comparison_data.js) for The Lab dashboard's player comparison feature.

For every qualified player (batters: 500+ balls since 2023, bowlers: 300+ balls),
this generator extracts:
    1. Career summary (matches, innings, runs/wickets, avg, SR/economy)
    2. Phase breakdown (Powerplay / Middle / Death stats)
    3. vs bowling type (batters): SR, avg, balls vs each bowling classification
    4. vs handedness (bowlers): economy, SR vs LHB and RHB
    5. Recent form (last 10 innings weighted stats)
    6. Rankings position from composite views

Data Source: DuckDB views created by analytics_ipl.py.
Output: scripts/the_lab/dashboard/data/comparison_data.js

Usage:
    python -m scripts.generators.generate_comparison_data
    python scripts/generators/generate_comparison_data.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_JS = PROJECT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "comparison_data.js"

# =============================================================================
# CONSTANTS
# =============================================================================

# Qualification thresholds (since 2023)
BATTER_MIN_BALLS = 500
BOWLER_MIN_BALLS = 300

# Phase display order
PHASE_ORDER = ["powerplay", "middle", "death"]

# Bowling types to include (excludes Unknown and very small sub-categories)
BOWLING_TYPES = [
    "Right-arm pace",
    "Fast",
    "Fast-Medium",
    "Left-arm pace",
    "Right-arm off-spin",
    "Right-arm leg-spin",
    "Leg-spin",
    "Off-spin",
    "LA Orthodox",
    "Left-arm orthodox",
    "Medium",
    "Wrist-spin",
]

# Handedness categories
HANDEDNESS = ["Left-hand", "Right-hand"]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _safe_float(val: Any) -> Optional[float]:
    """Convert a value to float, returning None for NaN/None."""
    if val is None:
        return None
    try:
        f = float(val)
        if f != f:  # NaN check
            return None
        return f
    except (TypeError, ValueError):
        return None


def _fmt(val: Any, decimals: int = 1) -> Any:
    """Format a number to specified decimals, pass through None."""
    f = _safe_float(val)
    if f is None:
        return None
    return round(f, decimals)


def _safe_int(val: Any) -> Optional[int]:
    """Convert a value to int, returning None for None/NaN."""
    f = _safe_float(val)
    if f is None:
        return None
    return int(f)


# =============================================================================
# BATTER DATA EXTRACTION
# =============================================================================


def get_qualified_batters(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Get list of qualified batters (500+ balls since 2023) with career summary."""
    rows = conn.execute(
        """
        SELECT
            player_id, player_name, innings, runs, balls_faced,
            dismissals, highest_score, fifties, hundreds,
            fours, sixes, dot_balls,
            strike_rate, batting_average, boundary_pct, dot_ball_pct
        FROM analytics_ipl_batting_career_since2023
        WHERE balls_faced >= ?
        ORDER BY balls_faced DESC
        """,
        [BATTER_MIN_BALLS],
    ).fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "innings": _safe_int(r[2]),
            "runs": _safe_int(r[3]),
            "balls": _safe_int(r[4]),
            "dismissals": _safe_int(r[5]),
            "hs": _safe_int(r[6]),
            "fifties": _safe_int(r[7]),
            "hundreds": _safe_int(r[8]),
            "fours": _safe_int(r[9]),
            "sixes": _safe_int(r[10]),
            "dots": _safe_int(r[11]),
            "sr": _fmt(r[12]),
            "avg": _fmt(r[13]),
            "boundaryPct": _fmt(r[14]),
            "dotPct": _fmt(r[15]),
        }
        for r in rows
    ]


def get_batter_phases(conn: duckdb.DuckDBPyConnection, player_ids: List[str]) -> Dict[str, Dict]:
    """Get phase breakdown for all qualified batters."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            player_id, match_phase, innings, runs, balls_faced,
            strike_rate, batting_average, boundary_pct, dot_ball_pct
        FROM analytics_ipl_batter_phase_since2023
        WHERE player_id IN (SELECT UNNEST(?::VARCHAR[]))
        ORDER BY player_id, match_phase
        """,
        [player_ids],
    ).fetchall()

    phases: Dict[str, Dict] = {}
    for r in rows:
        pid = r[0]
        phase = r[1]
        if pid not in phases:
            phases[pid] = {}
        phases[pid][phase] = {
            "innings": _safe_int(r[2]),
            "runs": _safe_int(r[3]),
            "balls": _safe_int(r[4]),
            "sr": _fmt(r[5]),
            "avg": _fmt(r[6]),
            "boundaryPct": _fmt(r[7]),
            "dotPct": _fmt(r[8]),
        }
    return phases


def get_batter_vs_bowling_type(
    conn: duckdb.DuckDBPyConnection, player_ids: List[str]
) -> Dict[str, Dict]:
    """Get batter performance vs each bowling type."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            batter_id, bowler_type, balls, runs, dismissals,
            strike_rate, average, boundary_pct, dot_ball_pct
        FROM analytics_ipl_batter_vs_bowler_type_since2023
        WHERE batter_id IN (SELECT UNNEST(?::VARCHAR[]))
          AND bowler_type != 'Unknown'
        ORDER BY batter_id, bowler_type
        """,
        [player_ids],
    ).fetchall()

    vs_type: Dict[str, Dict] = {}
    for r in rows:
        pid = r[0]
        btype = r[1]
        if pid not in vs_type:
            vs_type[pid] = {}
        vs_type[pid][btype] = {
            "balls": _safe_int(r[2]),
            "runs": _safe_int(r[3]),
            "dismissals": _safe_int(r[4]),
            "sr": _fmt(r[5]),
            "avg": _fmt(r[6]),
            "boundaryPct": _fmt(r[7]),
            "dotPct": _fmt(r[8]),
        }
    return vs_type


def get_batter_recent_form(
    conn: duckdb.DuckDBPyConnection, player_ids: List[str]
) -> Dict[str, Dict]:
    """Get recent form data for batters."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            batter_id, team_name,
            last10_innings, last10_runs, last10_balls, last10_sr, last10_avg,
            last10_boundary_pct, last10_dot_pct,
            career_sr, career_avg, sr_delta_last10
        FROM analytics_ipl_batter_recent_form
        WHERE batter_id IN (SELECT UNNEST(?::VARCHAR[]))
        """,
        [player_ids],
    ).fetchall()

    form: Dict[str, Dict] = {}
    for r in rows:
        form[r[0]] = {
            "team": r[1],
            "last10Innings": _safe_int(r[2]),
            "last10Runs": _safe_int(r[3]),
            "last10Balls": _safe_int(r[4]),
            "last10Sr": _fmt(r[5]),
            "last10Avg": _fmt(r[6]),
            "last10BoundaryPct": _fmt(r[7]),
            "last10DotPct": _fmt(r[8]),
            "careerSr": _fmt(r[9]),
            "careerAvg": _fmt(r[10]),
            "srDelta": _fmt(r[11]),
        }
    return form


def get_batter_rankings(conn: duckdb.DuckDBPyConnection, player_ids: List[str]) -> Dict[str, Dict]:
    """Get composite ranking position for batters."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            player_id, overall_rank, weighted_composite,
            composite_score, sample_size_factor
        FROM analytics_ipl_batter_composite_rankings
        WHERE player_id IN (SELECT UNNEST(?::VARCHAR[]))
        """,
        [player_ids],
    ).fetchall()

    rankings: Dict[str, Dict] = {}
    for r in rows:
        rankings[r[0]] = {
            "rank": _safe_int(r[1]),
            "composite": _fmt(r[2]),
            "rawScore": _fmt(r[3]),
            "sampleFactor": _fmt(r[4], 2),
        }
    return rankings


# =============================================================================
# BOWLER DATA EXTRACTION
# =============================================================================


def get_qualified_bowlers(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Get list of qualified bowlers (300+ balls since 2023) with career summary."""
    rows = conn.execute(
        """
        SELECT
            player_id, player_name, matches_bowled, balls_bowled,
            overs_bowled, runs_conceded, wickets,
            best_wickets, best_runs,
            dot_balls, fours_conceded, sixes_conceded,
            economy_rate, bowling_average, bowling_strike_rate,
            dot_ball_pct, boundary_conceded_pct
        FROM analytics_ipl_bowling_career_since2023
        WHERE balls_bowled >= ?
        ORDER BY balls_bowled DESC
        """,
        [BOWLER_MIN_BALLS],
    ).fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "matches": _safe_int(r[2]),
            "balls": _safe_int(r[3]),
            "overs": _fmt(r[4]),
            "runsConceded": _safe_int(r[5]),
            "wickets": _safe_int(r[6]),
            "bestWkts": _safe_int(r[7]),
            "bestRuns": _safe_int(r[8]),
            "dots": _safe_int(r[9]),
            "foursConceded": _safe_int(r[10]),
            "sixesConceded": _safe_int(r[11]),
            "economy": _fmt(r[12], 2),
            "avg": _fmt(r[13]),
            "sr": _fmt(r[14]),
            "dotPct": _fmt(r[15]),
            "boundaryConcededPct": _fmt(r[16]),
        }
        for r in rows
    ]


def get_bowler_phases(conn: duckdb.DuckDBPyConnection, player_ids: List[str]) -> Dict[str, Dict]:
    """Get phase breakdown for all qualified bowlers."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            player_id, match_phase, matches, balls_bowled, overs,
            runs_conceded, wickets, dot_balls,
            economy_rate, bowling_average, dot_ball_pct,
            boundary_conceded_pct
        FROM analytics_ipl_bowler_phase_since2023
        WHERE player_id IN (SELECT UNNEST(?::VARCHAR[]))
        ORDER BY player_id, match_phase
        """,
        [player_ids],
    ).fetchall()

    phases: Dict[str, Dict] = {}
    for r in rows:
        pid = r[0]
        phase = r[1]
        if pid not in phases:
            phases[pid] = {}
        phases[pid][phase] = {
            "matches": _safe_int(r[2]),
            "balls": _safe_int(r[3]),
            "overs": _fmt(r[4]),
            "runsConceded": _safe_int(r[5]),
            "wickets": _safe_int(r[6]),
            "dots": _safe_int(r[7]),
            "economy": _fmt(r[8], 2),
            "avg": _fmt(r[9]),
            "dotPct": _fmt(r[10]),
            "boundaryConcededPct": _fmt(r[11]),
        }
    return phases


def get_bowler_vs_handedness(
    conn: duckdb.DuckDBPyConnection, player_ids: List[str]
) -> Dict[str, Dict]:
    """Get bowler performance vs LHB and RHB."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            bowler_id, batting_hand, balls, runs, wickets,
            economy, strike_rate, dot_pct, boundary_pct
        FROM analytics_ipl_bowler_vs_batter_handedness_since2023
        WHERE bowler_id IN (SELECT UNNEST(?::VARCHAR[]))
        ORDER BY bowler_id, batting_hand
        """,
        [player_ids],
    ).fetchall()

    vs_hand: Dict[str, Dict] = {}
    for r in rows:
        pid = r[0]
        hand = r[1]
        if pid not in vs_hand:
            vs_hand[pid] = {}
        vs_hand[pid][hand] = {
            "balls": _safe_int(r[2]),
            "runs": _safe_int(r[3]),
            "wickets": _safe_int(r[4]),
            "economy": _fmt(r[5], 2),
            "sr": _fmt(r[6]),
            "dotPct": _fmt(r[7]),
            "boundaryPct": _fmt(r[8]),
        }
    return vs_hand


def get_bowler_recent_form(
    conn: duckdb.DuckDBPyConnection, player_ids: List[str]
) -> Dict[str, Dict]:
    """Get recent form data for bowlers."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            bowler_id, team_name,
            last10_matches, last10_overs, last10_wickets,
            last10_economy, last10_sr, last10_dot_pct,
            career_economy, career_sr, economy_delta_last10
        FROM analytics_ipl_bowler_recent_form
        WHERE bowler_id IN (SELECT UNNEST(?::VARCHAR[]))
        """,
        [player_ids],
    ).fetchall()

    form: Dict[str, Dict] = {}
    for r in rows:
        form[r[0]] = {
            "team": r[1],
            "last10Matches": _safe_int(r[2]),
            "last10Overs": _fmt(r[3]),
            "last10Wickets": _safe_int(r[4]),
            "last10Economy": _fmt(r[5], 2),
            "last10Sr": _fmt(r[6]),
            "last10DotPct": _fmt(r[7]),
            "careerEconomy": _fmt(r[8], 2),
            "careerSr": _fmt(r[9]),
            "economyDelta": _fmt(r[10], 2),
        }
    return form


def get_bowler_rankings(conn: duckdb.DuckDBPyConnection, player_ids: List[str]) -> Dict[str, Dict]:
    """Get composite ranking position for bowlers."""
    if not player_ids:
        return {}

    rows = conn.execute(
        """
        SELECT
            player_id, overall_rank, weighted_composite,
            composite_score, sample_size_factor
        FROM analytics_ipl_bowler_composite_rankings
        WHERE player_id IN (SELECT UNNEST(?::VARCHAR[]))
        """,
        [player_ids],
    ).fetchall()

    rankings: Dict[str, Dict] = {}
    for r in rows:
        rankings[r[0]] = {
            "rank": _safe_int(r[1]),
            "composite": _fmt(r[2]),
            "rawScore": _fmt(r[3]),
            "sampleFactor": _fmt(r[4], 2),
        }
    return rankings


# =============================================================================
# MAIN GENERATOR
# =============================================================================


def generate_comparison_data() -> Dict[str, Any]:
    """Query all views and build the full comparison data structure."""
    print("=" * 60)
    print("  COMPARISON DATA GENERATOR (TKT-216 / EPIC-020)")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # -----------------------------------------------------------------
        # BATTERS
        # -----------------------------------------------------------------
        print("\n[1/6] Fetching qualified batters (career summary)...")
        batters_list = get_qualified_batters(conn)
        batter_ids = [b["id"] for b in batters_list]
        print(f"  {len(batters_list)} batters qualified ({BATTER_MIN_BALLS}+ balls)")

        print("[2/6] Fetching batter phases, vs bowling type, form, rankings...")
        bat_phases = get_batter_phases(conn, batter_ids)
        bat_vs_type = get_batter_vs_bowling_type(conn, batter_ids)
        bat_form = get_batter_recent_form(conn, batter_ids)
        bat_ranks = get_batter_rankings(conn, batter_ids)

        # Assemble batter objects keyed by player_id
        batters: Dict[str, Dict] = {}
        for b in batters_list:
            pid = b["id"]
            batters[pid] = {
                "career": {k: v for k, v in b.items() if k != "id"},
                "phases": bat_phases.get(pid, {}),
                "vsBowlingType": bat_vs_type.get(pid, {}),
                "recentForm": bat_form.get(pid, {}),
                "ranking": bat_ranks.get(pid, {}),
            }

        phase_count = sum(1 for pid in batter_ids if pid in bat_phases)
        type_count = sum(1 for pid in batter_ids if pid in bat_vs_type)
        form_count = sum(1 for pid in batter_ids if pid in bat_form)
        rank_count = sum(1 for pid in batter_ids if pid in bat_ranks)
        print(
            f"  Phases: {phase_count}, VsType: {type_count}, "
            f"Form: {form_count}, Rankings: {rank_count}"
        )

        # -----------------------------------------------------------------
        # BOWLERS
        # -----------------------------------------------------------------
        print("\n[3/6] Fetching qualified bowlers (career summary)...")
        bowlers_list = get_qualified_bowlers(conn)
        bowler_ids = [b["id"] for b in bowlers_list]
        print(f"  {len(bowlers_list)} bowlers qualified ({BOWLER_MIN_BALLS}+ balls)")

        print("[4/6] Fetching bowler phases, vs handedness, form, rankings...")
        bowl_phases = get_bowler_phases(conn, bowler_ids)
        bowl_vs_hand = get_bowler_vs_handedness(conn, bowler_ids)
        bowl_form = get_bowler_recent_form(conn, bowler_ids)
        bowl_ranks = get_bowler_rankings(conn, bowler_ids)

        # Assemble bowler objects keyed by player_id
        bowlers: Dict[str, Dict] = {}
        for b in bowlers_list:
            pid = b["id"]
            bowlers[pid] = {
                "career": {k: v for k, v in b.items() if k != "id"},
                "phases": bowl_phases.get(pid, {}),
                "vsHandedness": bowl_vs_hand.get(pid, {}),
                "recentForm": bowl_form.get(pid, {}),
                "ranking": bowl_ranks.get(pid, {}),
            }

        phase_count = sum(1 for pid in bowler_ids if pid in bowl_phases)
        hand_count = sum(1 for pid in bowler_ids if pid in bowl_vs_hand)
        form_count = sum(1 for pid in bowler_ids if pid in bowl_form)
        rank_count = sum(1 for pid in bowler_ids if pid in bowl_ranks)
        print(
            f"  Phases: {phase_count}, VsHand: {hand_count}, "
            f"Form: {form_count}, Rankings: {rank_count}"
        )

        # -----------------------------------------------------------------
        # METADATA
        # -----------------------------------------------------------------
        print("\n[5/6] Building metadata...")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build name-to-id lookup for dashboard search
        batter_index = {b["career"]["name"]: pid for pid, b in batters.items()}
        bowler_index = {b["career"]["name"]: pid for pid, b in bowlers.items()}

        metadata = {
            "generated": now,
            "dataWindow": "IPL Since 2023",
            "batterQualification": f"{BATTER_MIN_BALLS}+ balls faced",
            "bowlerQualification": f"{BOWLER_MIN_BALLS}+ balls bowled",
            "totalBatters": len(batters),
            "totalBowlers": len(bowlers),
            "phases": PHASE_ORDER,
            "bowlingTypes": BOWLING_TYPES,
            "handedness": HANDEDNESS,
            "ticket": "TKT-216",
            "epic": "EPIC-020",
        }

        # -----------------------------------------------------------------
        # FINAL ASSEMBLY
        # -----------------------------------------------------------------
        print("[6/6] Assembling comparison data structure...")
        comparison_data = {
            "batters": batters,
            "bowlers": bowlers,
            "batterIndex": batter_index,
            "bowlerIndex": bowler_index,
            "metadata": metadata,
        }

        return comparison_data

    finally:
        conn.close()


def write_js_output(data: Dict[str, Any]) -> None:
    """Write the comparison data as a JavaScript file for The Lab dashboard."""
    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)

    json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)

    js_content = (
        "/**\n"
        " * The Lab - Player Comparison Data\n"
        " * IPL Pre-Season Analytics (TKT-216 / EPIC-020)\n"
        f" * Auto-generated: {data['metadata']['generated']}\n"
        " * Generator: scripts/generators/generate_comparison_data.py\n"
        " *\n"
        f" * Batters: {data['metadata']['totalBatters']} qualified"
        f" ({data['metadata']['batterQualification']})\n"
        f" * Bowlers: {data['metadata']['totalBowlers']} qualified"
        f" ({data['metadata']['bowlerQualification']})\n"
        " * Data window: IPL Since 2023\n"
        " */\n"
        "\n"
        f"const COMPARISON_DATA = {json_str};\n"
    )

    OUTPUT_JS.write_text(js_content, encoding="utf-8")
    size_kb = OUTPUT_JS.stat().st_size / 1024
    print(f"\nOutput written to: {OUTPUT_JS}")
    print(f"  Size: {size_kb:.1f} KB")


def print_summary(data: Dict[str, Any]) -> None:
    """Print a summary of generated comparison data for verification."""
    print("\n" + "=" * 60)
    print("  COMPARISON DATA SUMMARY")
    print("=" * 60)

    print(f"\n  Batters: {data['metadata']['totalBatters']} qualified")
    # Show top 5 batters by runs
    top_batters = sorted(
        data["batters"].items(),
        key=lambda x: x[1]["career"].get("runs") or 0,
        reverse=True,
    )[:5]
    for pid, b in top_batters:
        career = b["career"]
        rank_info = b.get("ranking", {})
        rank_str = f"#{rank_info['rank']}" if rank_info.get("rank") else "N/R"
        phases_count = len(b.get("phases", {}))
        types_count = len(b.get("vsBowlingType", {}))
        print(
            f"    {career['name']}: {career['runs']} runs, "
            f"SR {career['sr']}, Rank {rank_str}, "
            f"{phases_count} phases, {types_count} bowling types"
        )

    print(f"\n  Bowlers: {data['metadata']['totalBowlers']} qualified")
    top_bowlers = sorted(
        data["bowlers"].items(),
        key=lambda x: x[1]["career"].get("wickets") or 0,
        reverse=True,
    )[:5]
    for pid, b in top_bowlers:
        career = b["career"]
        rank_info = b.get("ranking", {})
        rank_str = f"#{rank_info['rank']}" if rank_info.get("rank") else "N/R"
        phases_count = len(b.get("phases", {}))
        hand_count = len(b.get("vsHandedness", {}))
        print(
            f"    {career['name']}: {career['wickets']} wkts, "
            f"Econ {career['economy']}, Rank {rank_str}, "
            f"{phases_count} phases, {hand_count} hand splits"
        )

    print(f"\n  Generated: {data['metadata']['generated']}")
    print("=" * 60)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    comparison = generate_comparison_data()
    write_js_output(comparison)
    print_summary(comparison)
    print("\nDone.")
