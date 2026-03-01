#!/usr/bin/env python3
"""
Cricket Playbook - Head-to-Head Data Generator
Author: Stephen Curry (Analytics Lead)

Queries DuckDB analytics views and produces a JavaScript data file
(h2h_data.js) for The Lab dashboard's head-to-head batter-vs-bowler page.

For every qualified batter-vs-bowler matchup (6+ balls), this generator extracts:
    1. Career aggregate H2H stats (all-time)
    2. Since 2023 H2H stats
    3. Phase breakdown (Powerplay / Middle / Death)
    4. Yearly breakdown
    5. Over-wise split (overs 0-19)
    6. Dominance index from matchup rankings

Data Source: DuckDB views created by analytics_ipl.py + direct fact_ball queries.
Output: scripts/the_lab/dashboard/data/h2h_data.js

Usage:
    python -m scripts.generators.generate_h2h_data
    python scripts/generators/generate_h2h_data.py
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
OUTPUT_JS = PROJECT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "h2h_data.js"

# =============================================================================
# CONSTANTS
# =============================================================================

MIN_BALLS = 10  # Minimum balls per matchup pair
IPL_MIN_DATE = "2023-01-01"


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


def _strip_none(d: Any) -> Any:
    """Recursively remove None values from dicts to reduce JSON size."""
    if isinstance(d, dict):
        return {k: _strip_none(v) for k, v in d.items() if v is not None and v != {}}
    if isinstance(d, list):
        return [_strip_none(v) for v in d]
    return d


def _sample_label(balls: int) -> str:
    """Return sample size label based on ball count."""
    if balls < 10:
        return "LOW"
    if balls < 30:
        return "MEDIUM"
    return "HIGH"


# =============================================================================
# DATA EXTRACTION
# =============================================================================


def get_career_matchups(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Get all-time batter vs bowler matchup data."""
    rows = conn.execute(
        """
        SELECT
            batter_id, batter_name, bowler_id, bowler_name,
            balls, runs, dismissals, strike_rate, average,
            dot_balls, fours, sixes, dot_ball_pct, boundary_pct,
            sample_size
        FROM analytics_ipl_batter_vs_bowler_alltime
        WHERE balls >= ?
        ORDER BY balls DESC
        """,
        [MIN_BALLS],
    ).fetchall()

    return [
        {
            "batter_id": r[0],
            "batter_name": r[1],
            "bowler_id": r[2],
            "bowler_name": r[3],
            "balls": _safe_int(r[4]),
            "runs": _safe_int(r[5]),
            "dismissals": _safe_int(r[6]),
            "sr": _fmt(r[7]),
            "avg": _fmt(r[8]),
            "dots": _safe_int(r[9]),
            "fours": _safe_int(r[10]),
            "sixes": _safe_int(r[11]),
            "dotPct": _fmt(r[12]),
            "boundaryPct": _fmt(r[13]),
            "sampleSize": r[14],
        }
        for r in rows
    ]


def get_since2023_matchups(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Get since-2023 batter vs bowler matchup data."""
    rows = conn.execute(
        """
        SELECT
            batter_id, bowler_id,
            balls, runs, dismissals, strike_rate, average,
            dot_balls, fours, sixes, dot_ball_pct, boundary_pct
        FROM analytics_ipl_batter_vs_bowler_since2023
        WHERE balls >= 1
        ORDER BY balls DESC
        """
    ).fetchall()

    result: Dict[str, Dict] = {}
    for r in rows:
        key = f"{r[0]}__{r[1]}"
        result[key] = {
            "balls": _safe_int(r[2]),
            "runs": _safe_int(r[3]),
            "dismissals": _safe_int(r[4]),
            "sr": _fmt(r[5]),
            "avg": _fmt(r[6]),
            "dots": _safe_int(r[7]),
            "fours": _safe_int(r[8]),
            "sixes": _safe_int(r[9]),
            "dotPct": _fmt(r[10]),
            "boundaryPct": _fmt(r[11]),
        }
    return result


def get_phase_matchups(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Get phase breakdown for batter vs bowler matchups."""
    rows = conn.execute(
        """
        SELECT
            batter_id, bowler_id, match_phase,
            balls, runs, dismissals, strike_rate, average,
            dot_ball_pct, boundary_pct
        FROM analytics_ipl_batter_vs_bowler_phase_alltime
        WHERE balls >= 1
        """
    ).fetchall()

    result: Dict[str, Dict] = {}
    for r in rows:
        key = f"{r[0]}__{r[1]}"
        phase = r[2]
        if key not in result:
            result[key] = {}
        result[key][phase] = {
            "balls": _safe_int(r[3]),
            "runs": _safe_int(r[4]),
            "dismissals": _safe_int(r[5]),
            "sr": _fmt(r[6]),
            "avg": _fmt(r[7]),
            "dotPct": _fmt(r[8]),
            "boundaryPct": _fmt(r[9]),
        }
    return result


def get_yearly_breakdown(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Get yearly breakdown for batter vs bowler matchups from fact_ball."""
    rows = conn.execute(
        """
        SELECT
            fb.batter_id, fb.bowler_id,
            EXTRACT(YEAR FROM dm.match_date::DATE)::INT as year,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id
                THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball
                THEN 1 ELSE 0 END) as dots
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND fb.is_legal_ball = TRUE
        GROUP BY fb.batter_id, fb.bowler_id, year
        HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 1
        ORDER BY fb.batter_id, fb.bowler_id, year
        """
    ).fetchall()

    result: Dict[str, Dict] = {}
    for r in rows:
        key = f"{r[0]}__{r[1]}"
        year = str(r[2])
        if key not in result:
            result[key] = {}
        balls = _safe_int(r[3]) or 0
        runs = _safe_int(r[4]) or 0
        dismissals = _safe_int(r[5]) or 0
        fours = _safe_int(r[6]) or 0
        sixes = _safe_int(r[7]) or 0
        dots = _safe_int(r[8]) or 0
        result[key][year] = {
            "balls": balls,
            "runs": runs,
            "dismissals": dismissals,
            "fours": fours,
            "sixes": sixes,
            "sr": _fmt(runs * 100.0 / balls if balls > 0 else None),
            "avg": _fmt(runs / dismissals if dismissals > 0 else None),
            "dotPct": _fmt(dots * 100.0 / balls if balls > 0 else None),
            "boundaryPct": _fmt((fours + sixes) * 100.0 / balls if balls > 0 else None),
        }
    return result


def get_overwise_split(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Get over-wise split for batter vs bowler matchups from fact_ball."""
    rows = conn.execute(
        """
        SELECT
            fb.batter_id, fb.bowler_id, fb.over,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id
                THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball
                THEN 1 ELSE 0 END) as dots,
            SUM(CASE WHEN fb.batter_runs IN (4, 6) AND fb.is_legal_ball
                THEN 1 ELSE 0 END) as boundaries
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND fb.is_legal_ball = TRUE
        GROUP BY fb.batter_id, fb.bowler_id, fb.over
        HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 1
        ORDER BY fb.batter_id, fb.bowler_id, fb.over
        """
    ).fetchall()

    result: Dict[str, Dict] = {}
    for r in rows:
        key = f"{r[0]}__{r[1]}"
        over = str(_safe_int(r[2]))
        if key not in result:
            result[key] = {}
        balls = _safe_int(r[3]) or 0
        runs = _safe_int(r[4]) or 0
        wickets = _safe_int(r[5]) or 0
        dots = _safe_int(r[6]) or 0
        boundaries = _safe_int(r[7]) or 0
        result[key][over] = {
            "balls": balls,
            "runs": runs,
            "wickets": wickets,
            "sr": _fmt(runs * 100.0 / balls if balls > 0 else None),
            "dotPct": _fmt(dots * 100.0 / balls if balls > 0 else None),
            "boundaryPct": _fmt(boundaries * 100.0 / balls if balls > 0 else None),
        }
    return result


def get_dominance_data(conn: duckdb.DuckDBPyConnection) -> Dict[str, Dict]:
    """Get dominance index from matchup rankings (all-time)."""
    rows = conn.execute(
        """
        SELECT
            batter_id, bowler_id,
            dominance_index, sample_size_factor, weighted_dominance
        FROM analytics_ipl_player_matchup_rankings_alltime
        """
    ).fetchall()

    result: Dict[str, Dict] = {}
    for r in rows:
        key = f"{r[0]}__{r[1]}"
        dom_index = _fmt(r[2])
        sample_factor = _fmt(r[3], 3)
        weighted = _fmt(r[4])

        verdict = "Even"
        if dom_index is not None:
            if dom_index > 5:
                verdict = "Batter-favored"
            elif dom_index < -5:
                verdict = "Bowler-favored"

        result[key] = {
            "index": dom_index,
            "sampleFactor": sample_factor,
            "weighted": weighted,
            "verdict": verdict,
        }
    return result


def get_player_teams(conn: duckdb.DuckDBPyConnection) -> Dict[str, str]:
    """Get team assignments for 2026 squad players."""
    rows = conn.execute(
        """
        SELECT player_id, team_name
        FROM ipl_2026_squads
        """
    ).fetchall()
    return {r[0]: r[1] for r in rows}


def get_player_types(conn: duckdb.DuckDBPyConnection) -> Dict[str, str]:
    """Detect player type from comparison data pools (batters/bowlers)."""
    # We detect type from the analytics views rather than a squad column
    types: Dict[str, str] = {}
    try:
        bat_rows = conn.execute(
            "SELECT DISTINCT player_id FROM analytics_ipl_batting_career_since2023"
        ).fetchall()
        for r in bat_rows:
            types[r[0]] = "batter"
    except Exception:
        pass
    try:
        bowl_rows = conn.execute(
            "SELECT DISTINCT player_id FROM analytics_ipl_bowling_career_since2023"
        ).fetchall()
        for r in bowl_rows:
            if r[0] not in types:
                types[r[0]] = "bowler"
            # If already batter, keep as batter (primary role)
    except Exception:
        pass
    return types


# =============================================================================
# MAIN GENERATOR
# =============================================================================


def generate_h2h_data() -> Dict[str, Any]:
    """Query all views and build the full H2H data structure."""
    print("=" * 60)
    print("  HEAD-TO-HEAD DATA GENERATOR")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # -----------------------------------------------------------------
        # CAREER MATCHUPS (all-time)
        # -----------------------------------------------------------------
        print("\n[1/7] Fetching career matchup data (all-time)...")
        career_matchups = get_career_matchups(conn)
        print(f"  {len(career_matchups)} matchups qualified ({MIN_BALLS}+ balls)")

        # -----------------------------------------------------------------
        # SINCE 2023 MATCHUPS
        # -----------------------------------------------------------------
        print("[2/7] Fetching since-2023 matchup data...")
        since2023 = get_since2023_matchups(conn)
        print(f"  {len(since2023)} since-2023 pairs found")

        # -----------------------------------------------------------------
        # PHASE BREAKDOWN
        # -----------------------------------------------------------------
        print("[3/7] Fetching phase breakdown...")
        phases = get_phase_matchups(conn)
        print(f"  {len(phases)} pairs with phase data")

        # -----------------------------------------------------------------
        # YEARLY BREAKDOWN
        # -----------------------------------------------------------------
        print("[4/7] Fetching yearly breakdown...")
        yearly = get_yearly_breakdown(conn)
        print(f"  {len(yearly)} pairs with yearly data")

        # -----------------------------------------------------------------
        # OVER-WISE SPLIT
        # -----------------------------------------------------------------
        print("[5/7] Fetching over-wise split...")
        overwise = get_overwise_split(conn)
        print(f"  {len(overwise)} pairs with over-wise data")

        # -----------------------------------------------------------------
        # DOMINANCE DATA
        # -----------------------------------------------------------------
        print("[6/7] Fetching dominance index...")
        dominance = get_dominance_data(conn)
        print(f"  {len(dominance)} pairs with dominance data")

        # -----------------------------------------------------------------
        # PLAYER METADATA
        # -----------------------------------------------------------------
        print("[7/7] Building player metadata...")
        teams = get_player_teams(conn)
        player_types = get_player_types(conn)

        # -----------------------------------------------------------------
        # ASSEMBLE MATCHUP OBJECTS
        # -----------------------------------------------------------------
        matchups: Dict[str, Dict] = {}
        player_index: Dict[str, str] = {}
        player_meta: Dict[str, Dict] = {}

        for m in career_matchups:
            key = f"{m['batter_id']}__{m['bowler_id']}"

            # Build player index and meta
            bat_id = m["batter_id"]
            bowl_id = m["bowler_id"]
            bat_name = m["batter_name"]
            bowl_name = m["bowler_name"]

            player_index[bat_name] = bat_id
            player_index[bowl_name] = bowl_id

            if bat_id not in player_meta:
                player_meta[bat_id] = {
                    "name": bat_name,
                    "team": teams.get(bat_id, "Unknown"),
                    "type": player_types.get(bat_id, "batter"),
                }
            if bowl_id not in player_meta:
                player_meta[bowl_id] = {
                    "name": bowl_name,
                    "team": teams.get(bowl_id, "Unknown"),
                    "type": player_types.get(bowl_id, "bowler"),
                }

            # Compute sixPct
            balls = m["balls"] or 0
            sixes = m["sixes"] or 0
            six_pct = _fmt(sixes * 100.0 / balls if balls > 0 else None)

            matchups[key] = {
                "batter": {
                    "id": bat_id,
                    "name": bat_name,
                    "team": teams.get(bat_id, "Unknown"),
                },
                "bowler": {
                    "id": bowl_id,
                    "name": bowl_name,
                    "team": teams.get(bowl_id, "Unknown"),
                },
                "career": {
                    "balls": m["balls"],
                    "runs": m["runs"],
                    "dismissals": m["dismissals"],
                    "sr": m["sr"],
                    "avg": m["avg"],
                    "dots": m["dots"],
                    "fours": m["fours"],
                    "sixes": m["sixes"],
                    "dotPct": m["dotPct"],
                    "boundaryPct": m["boundaryPct"],
                    "sixPct": six_pct,
                },
                "since2023": since2023.get(key, {}),
                "phases": phases.get(key, {}) if balls >= 20 else {},
                "byYear": yearly.get(key, {}) if balls >= 30 else {},
                "byOver": overwise.get(key, {}) if balls >= 30 else {},
                "dominance": dominance.get(
                    key,
                    {
                        "index": None,
                        "sampleFactor": None,
                        "weighted": None,
                        "verdict": "N/A",
                    },
                ),
            }

        # -----------------------------------------------------------------
        # FINAL ASSEMBLY
        # -----------------------------------------------------------------
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        h2h_data = {
            "matchups": matchups,
            "playerIndex": player_index,
            "playerMeta": player_meta,
            "metadata": {
                "generated": now,
                "dataWindow": "IPL All-time",
                "totalMatchups": len(matchups),
                "minBalls": MIN_BALLS,
            },
        }

        return h2h_data

    finally:
        conn.close()


def write_js_output(data: Dict[str, Any]) -> None:
    """Write the H2H data as a JavaScript file for The Lab dashboard."""
    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)

    cleaned = _strip_none(data)
    json_str = json.dumps(cleaned, separators=(",", ":"), ensure_ascii=False, default=str)

    js_content = (
        "/**\n"
        " * The Lab - Head-to-Head Matchup Data\n"
        " * IPL Batter vs Bowler Analytics\n"
        f" * Auto-generated: {data['metadata']['generated']}\n"
        " * Generator: scripts/generators/generate_h2h_data.py\n"
        " *\n"
        f" * Total matchups: {data['metadata']['totalMatchups']}\n"
        f" * Min balls: {data['metadata']['minBalls']}\n"
        " * Data window: IPL All-time\n"
        " */\n"
        "\n"
        f"const H2H_DATA = {json_str};\n"
    )

    OUTPUT_JS.write_text(js_content, encoding="utf-8")
    size_kb = OUTPUT_JS.stat().st_size / 1024
    print(f"\nOutput written to: {OUTPUT_JS}")
    print(f"  Size: {size_kb:.1f} KB")


def print_summary(data: Dict[str, Any]) -> None:
    """Print a summary of generated H2H data."""
    print("\n" + "=" * 60)
    print("  HEAD-TO-HEAD DATA SUMMARY")
    print("=" * 60)

    print(f"\n  Total matchups: {data['metadata']['totalMatchups']}")
    print(f"  Total players in index: {len(data['playerIndex'])}")
    print(f"  Min balls threshold: {data['metadata']['minBalls']}")

    # Show top 5 matchups by balls
    top = sorted(
        data["matchups"].items(),
        key=lambda x: x[1]["career"].get("balls") or 0,
        reverse=True,
    )[:5]
    print("\n  Top 5 matchups by balls faced:")
    for key, m in top:
        c = m["career"]
        dom = m.get("dominance", {})
        print(
            f"    {m['batter']['name']} vs {m['bowler']['name']}: "
            f"{c['balls']} balls, {c['runs']} runs, "
            f"SR {c['sr']}, {dom.get('verdict', 'N/A')}"
        )

    print(f"\n  Generated: {data['metadata']['generated']}")
    print("=" * 60)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    h2h = generate_h2h_data()
    write_js_output(h2h)
    print_summary(h2h)
    print("\nDone.")
