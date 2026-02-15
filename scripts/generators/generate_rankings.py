#!/usr/bin/env python3
"""
Cricket Playbook - Ranking Generator (TKT-236 / EPIC-021)
Author: Stephen Curry (Analytics Lead)
Sprint: SPRINT-005 (Signature Feature)

Queries the 7 composite ranking view categories from analytics_ipl.py and produces
a JavaScript data file (rankings.js) for The Lab dashboard Rankings tab.

Categories:
    1. Batter Phase Rankings       (powerplay / middle / death)
    2. Bowler Phase Rankings        (powerplay / middle / death)
    3. Batter vs Bowling Type       (pace / spin / medium sub-types)
    4. Bowler vs Handedness          (vs Left-hand / vs Right-hand)
    5. Player Matchup Rankings      (batter-favored / bowler-favored)
    6. Overall Batter Composite     (top-20 leaderboard)
    7. Overall Bowler Composite     (top-20 leaderboard)

Data Source: DuckDB views created by create_composite_ranking_views() in analytics_ipl.py.
Output: scripts/the_lab/dashboard/data/rankings.js

Usage:
    python -m scripts.generators.generate_rankings
    python scripts/generators/generate_rankings.py
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
OUTPUT_JS = PROJECT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "rankings.js"

# =============================================================================
# CONSTANTS
# =============================================================================

# Top N players per leaderboard
TOP_N = 20

# Bowler types to include in batter-vs-bowling-type rankings (minimum 20 qualifiers).
# Excludes "Unknown" and very small sub-categories.
BOWLING_TYPE_ORDER = [
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

# Phase display order
PHASE_ORDER = ["powerplay", "middle", "death"]
PHASE_TITLES = {
    "powerplay": "Powerplay (Overs 1-6)",
    "middle": "Middle Overs (7-15)",
    "death": "Death Overs (16-20)",
}

# Handedness display
HAND_TITLES = {
    "Left-hand": "vs Left-Hand Batters",
    "Right-hand": "vs Right-Hand Batters",
}


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


def _format_num(val: Any, decimals: int = 1) -> Any:
    """Format a number to specified decimals, pass through None."""
    f = _safe_float(val)
    if f is None:
        return None
    return round(f, decimals)


# =============================================================================
# QUERY FUNCTIONS — one per ranking category
# =============================================================================


def query_batter_phase_rankings(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 1: Batter phase rankings (powerplay/middle/death)."""
    subcategories = []
    for phase in PHASE_ORDER:
        rows = conn.execute(
            """
            SELECT
                phase_rank, player_name, balls_faced, strike_rate,
                batting_average, boundary_pct, weighted_composite
            FROM analytics_ipl_batter_phase_rankings
            WHERE match_phase = ?
            ORDER BY phase_rank
            LIMIT ?
            """,
            [phase, TOP_N],
        ).fetchall()

        subcategories.append(
            {
                "id": phase,
                "title": PHASE_TITLES[phase],
                "headers": ["Rank", "Player", "Balls", "SR", "Avg", "Boundary%", "Composite"],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]),
                        _format_num(r[3]),
                        _format_num(r[4]),
                        _format_num(r[5]),
                        _format_num(r[6]),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    "SELECT COUNT(*) FROM analytics_ipl_batter_phase_rankings WHERE match_phase = ?",
                    [phase],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_bowler_phase_rankings(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 2: Bowler phase rankings (powerplay/middle/death)."""
    subcategories = []
    for phase in PHASE_ORDER:
        rows = conn.execute(
            """
            SELECT
                phase_rank, player_name, balls_bowled, economy_rate,
                dot_ball_pct, weighted_composite
            FROM analytics_ipl_bowler_phase_rankings
            WHERE match_phase = ?
            ORDER BY phase_rank
            LIMIT ?
            """,
            [phase, TOP_N],
        ).fetchall()

        subcategories.append(
            {
                "id": phase,
                "title": PHASE_TITLES[phase],
                "headers": ["Rank", "Player", "Balls", "Econ", "Dot%", "Composite"],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]),
                        _format_num(r[3], 2),
                        _format_num(r[4]),
                        _format_num(r[5]),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    "SELECT COUNT(*) FROM analytics_ipl_bowler_phase_rankings WHERE match_phase = ?",
                    [phase],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_batter_vs_bowling_type(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 3: Batter vs bowling type rankings."""
    subcategories = []

    # Only include types present in the data
    available_types = [
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT bowler_type FROM analytics_ipl_batter_vs_bowling_type_rankings ORDER BY bowler_type"
        ).fetchall()
    ]

    # Use ordered list, filtered to available
    ordered_types = [t for t in BOWLING_TYPE_ORDER if t in available_types]
    # Add any types in data but not in our order list (safety net)
    ordered_types += [t for t in available_types if t not in ordered_types and t != "Unknown"]

    for btype in ordered_types:
        rows = conn.execute(
            """
            SELECT
                vs_type_rank, player_name, balls, strike_rate,
                average, weighted_composite
            FROM analytics_ipl_batter_vs_bowling_type_rankings
            WHERE bowler_type = ?
            ORDER BY vs_type_rank
            LIMIT ?
            """,
            [btype, TOP_N],
        ).fetchall()

        if not rows:
            continue

        subcategories.append(
            {
                "id": btype.lower().replace(" ", "_").replace("-", "_"),
                "title": f"vs {btype}",
                "headers": ["Rank", "Player", "Balls", "SR", "Avg", "Composite"],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]),
                        _format_num(r[3]),
                        _format_num(r[4]),
                        _format_num(r[5]),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    "SELECT COUNT(*) FROM analytics_ipl_batter_vs_bowling_type_rankings WHERE bowler_type = ?",
                    [btype],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_bowler_vs_handedness(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 4: Bowler vs batter handedness rankings."""
    subcategories = []
    for hand in ["Left-hand", "Right-hand"]:
        rows = conn.execute(
            """
            SELECT
                vs_hand_rank, player_name, balls, wickets,
                economy, weighted_composite
            FROM analytics_ipl_bowler_vs_handedness_rankings
            WHERE batting_hand = ?
            ORDER BY vs_hand_rank
            LIMIT ?
            """,
            [hand, TOP_N],
        ).fetchall()

        subcategories.append(
            {
                "id": hand.lower().replace("-", "_"),
                "title": HAND_TITLES[hand],
                "headers": ["Rank", "Player", "Balls", "Wkts", "Econ", "Composite"],
                "rows": [
                    [int(r[0]), r[1], int(r[2]), int(r[3]), _format_num(r[4], 2), _format_num(r[5])]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    "SELECT COUNT(*) FROM analytics_ipl_bowler_vs_handedness_rankings WHERE batting_hand = ?",
                    [hand],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_player_matchup_rankings(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 5: Player matchup rankings (batter-favored + bowler-favored)."""
    # Batter-favored matchups (highest weighted dominance)
    batter_rows = conn.execute(
        """
        SELECT
            batter_name, bowler_name, balls, runs, dismissals,
            strike_rate, dominance_index, weighted_dominance
        FROM analytics_ipl_player_matchup_rankings
        ORDER BY weighted_dominance DESC
        LIMIT ?
        """,
        [TOP_N],
    ).fetchall()

    # Bowler-favored matchups (lowest weighted dominance)
    bowler_rows = conn.execute(
        """
        SELECT
            batter_name, bowler_name, balls, runs, dismissals,
            strike_rate, dominance_index, weighted_dominance
        FROM analytics_ipl_player_matchup_rankings
        ORDER BY weighted_dominance ASC
        LIMIT ?
        """,
        [TOP_N],
    ).fetchall()

    total_matchups = conn.execute(
        "SELECT COUNT(*) FROM analytics_ipl_player_matchup_rankings"
    ).fetchone()[0]

    return [
        {
            "id": "batter_favored",
            "title": "Batter-Favored Matchups",
            "description": "Matchups where the batter dominates (high SR, high avg, low dismissal rate)",
            "headers": ["Rank", "Batter", "Bowler", "Balls", "Runs", "Outs", "SR", "Dominance"],
            "rows": [
                [
                    i + 1,
                    r[0],
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5]),
                    _format_num(r[7]),
                ]
                for i, r in enumerate(batter_rows)
            ],
            "qualifiedCount": total_matchups,
        },
        {
            "id": "bowler_favored",
            "title": "Bowler-Favored Matchups",
            "description": "Matchups where the bowler dominates (low SR, frequent dismissals)",
            "headers": ["Rank", "Batter", "Bowler", "Balls", "Runs", "Outs", "SR", "Dominance"],
            "rows": [
                [
                    i + 1,
                    r[0],
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5]),
                    _format_num(r[7]),
                ]
                for i, r in enumerate(bowler_rows)
            ],
            "qualifiedCount": total_matchups,
        },
    ]


def query_batter_composite_rankings(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 6: Overall batter composite rankings."""
    rows = conn.execute(
        """
        SELECT
            overall_rank, player_name, innings, runs, balls_faced,
            strike_rate, batting_average, boundary_pct,
            composite_score, weighted_composite
        FROM analytics_ipl_batter_composite_rankings
        ORDER BY overall_rank
        LIMIT ?
        """,
        [TOP_N],
    ).fetchall()

    total = conn.execute("SELECT COUNT(*) FROM analytics_ipl_batter_composite_rankings").fetchone()[
        0
    ]

    return [
        {
            "id": "overall",
            "title": "Overall Batter Rankings",
            "description": (
                "Composite score: Career SR+Avg (30%) + Phase Performance (30%) "
                "+ Boundary% (20%) + Average (10%) + Dot Ball Discipline (10%). "
                "Sample-size weighted. Min 500 balls."
            ),
            "headers": [
                "Rank",
                "Player",
                "Inn",
                "Runs",
                "Balls",
                "SR",
                "Avg",
                "Boundary%",
                "Raw Score",
                "Weighted",
            ],
            "rows": [
                [
                    int(r[0]),
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5]),
                    _format_num(r[6]),
                    _format_num(r[7]),
                    _format_num(r[8]),
                    _format_num(r[9]),
                ]
                for r in rows
            ],
            "qualifiedCount": total,
        }
    ]


def query_bowler_composite_rankings(conn: duckdb.DuckDBPyConnection) -> List[Dict]:
    """Category 7: Overall bowler composite rankings."""
    rows = conn.execute(
        """
        SELECT
            overall_rank, player_name, matches_bowled, balls_bowled,
            wickets, economy_rate, bowling_average, bowling_strike_rate,
            composite_score, weighted_composite
        FROM analytics_ipl_bowler_composite_rankings
        ORDER BY overall_rank
        LIMIT ?
        """,
        [TOP_N],
    ).fetchall()

    total = conn.execute("SELECT COUNT(*) FROM analytics_ipl_bowler_composite_rankings").fetchone()[
        0
    ]

    return [
        {
            "id": "overall",
            "title": "Overall Bowler Rankings",
            "description": (
                "Composite score: Career Econ+Avg (30%) + Phase Performance (30%) "
                "+ Economy (20%) + Wicket-taking (10%) + Dot Ball% (10%). "
                "Sample-size weighted. Min 300 balls."
            ),
            "headers": [
                "Rank",
                "Player",
                "Matches",
                "Balls",
                "Wkts",
                "Econ",
                "Avg",
                "Bowl SR",
                "Raw Score",
                "Weighted",
            ],
            "rows": [
                [
                    int(r[0]),
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5], 2),
                    _format_num(r[6]),
                    _format_num(r[7]),
                    _format_num(r[8]),
                    _format_num(r[9]),
                ]
                for r in rows
            ],
            "qualifiedCount": total,
        }
    ]


# =============================================================================
# MAIN GENERATOR
# =============================================================================


def generate_rankings() -> Dict[str, Any]:
    """Query all 7 ranking categories and build the full rankings data structure."""
    print("=" * 60)
    print("  RANKING GENERATOR (TKT-236 / EPIC-021)")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        categories = []
        stats = {}

        # Category 1: Batter Phase Rankings
        print("\n[1/7] Batter Phase Rankings...")
        subs = query_batter_phase_rankings(conn)
        total_rows = sum(s["qualifiedCount"] for s in subs)
        categories.append(
            {
                "id": "batter_phase",
                "title": "Batter Phase Rankings",
                "description": (
                    "Phase-specific batter composites. Combines SR percentile (40%), "
                    "Avg percentile (40%), and Boundary% percentile (20%). "
                    "Sample-size weighted (target: 200 balls per phase)."
                ),
                "subcategories": subs,
            }
        )
        stats["batter_phase"] = total_rows
        print(f"  {len(subs)} phases, {total_rows} total qualified players")

        # Category 2: Bowler Phase Rankings
        print("\n[2/7] Bowler Phase Rankings...")
        subs = query_bowler_phase_rankings(conn)
        total_rows = sum(s["qualifiedCount"] for s in subs)
        categories.append(
            {
                "id": "bowler_phase",
                "title": "Bowler Phase Rankings",
                "description": (
                    "Phase-specific bowler composites. Combines Economy percentile (50%) "
                    "and Dot Ball% percentile (50%). "
                    "Sample-size weighted (target: 120 balls per phase)."
                ),
                "subcategories": subs,
            }
        )
        stats["bowler_phase"] = total_rows
        print(f"  {len(subs)} phases, {total_rows} total qualified players")

        # Category 3: Batter vs Bowling Type
        print("\n[3/7] Batter vs Bowling Type Rankings...")
        subs = query_batter_vs_bowling_type(conn)
        total_rows = sum(s["qualifiedCount"] for s in subs)
        categories.append(
            {
                "id": "batter_vs_bowling_type",
                "title": "Batter vs Bowling Type",
                "description": (
                    "How batters perform against each bowling classification. "
                    "Composite: SR (40%) + Avg (40%) + Survival Rate (20%). "
                    "Min 50 balls. Sample-size weighted (target: 100 balls)."
                ),
                "subcategories": subs,
            }
        )
        stats["batter_vs_bowling_type"] = total_rows
        print(f"  {len(subs)} bowling types, {total_rows} total qualified entries")

        # Category 4: Bowler vs Handedness
        print("\n[4/7] Bowler vs Handedness Rankings...")
        subs = query_bowler_vs_handedness(conn)
        total_rows = sum(s["qualifiedCount"] for s in subs)
        categories.append(
            {
                "id": "bowler_vs_handedness",
                "title": "Bowler vs Batter Handedness",
                "description": (
                    "Bowler effectiveness against left-hand and right-hand batters. "
                    "Composite: Economy percentile (50%) + SR percentile (50%). "
                    "Min 50 balls. Sample-size weighted (target: 100 balls)."
                ),
                "subcategories": subs,
            }
        )
        stats["bowler_vs_handedness"] = total_rows
        print(f"  {len(subs)} hand splits, {total_rows} total qualified entries")

        # Category 5: Player Matchup Rankings
        print("\n[5/7] Player Matchup Rankings...")
        subs = query_player_matchup_rankings(conn)
        total_matchups = subs[0]["qualifiedCount"]
        categories.append(
            {
                "id": "player_matchups",
                "title": "Player Matchup Rankings",
                "description": (
                    "Head-to-head dominance index. Positive = batter-favored, "
                    "negative = bowler-favored. Factors: SR deviation (50%), "
                    "Avg deviation (30%), Boundary% deviation (20%). "
                    "Min 12 balls. Sample-size weighted (target: 50 balls)."
                ),
                "subcategories": subs,
            }
        )
        stats["player_matchups"] = total_matchups
        print(f"  {total_matchups} qualified matchups")

        # Category 6: Overall Batter Composite
        print("\n[6/7] Overall Batter Composite Rankings...")
        subs = query_batter_composite_rankings(conn)
        total = subs[0]["qualifiedCount"]
        categories.append(
            {
                "id": "batter_composite",
                "title": "Overall Batter Rankings",
                "description": subs[0]["description"],
                "subcategories": subs,
            }
        )
        stats["batter_composite"] = total
        print(f"  {total} qualified batters")

        # Category 7: Overall Bowler Composite
        print("\n[7/7] Overall Bowler Composite Rankings...")
        subs = query_bowler_composite_rankings(conn)
        total = subs[0]["qualifiedCount"]
        categories.append(
            {
                "id": "bowler_composite",
                "title": "Overall Bowler Rankings",
                "description": subs[0]["description"],
                "subcategories": subs,
            }
        )
        stats["bowler_composite"] = total
        print(f"  {total} qualified bowlers")

        # Build final data structure
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rankings_data = {
            "meta": {
                "generated": now,
                "dataWindow": "IPL 2008-2025 (All-Time)",
                "categories": len(categories),
                "ticket": "TKT-236",
                "epic": "EPIC-021",
            },
            "stats": stats,
            "categories": categories,
        }

        return rankings_data

    finally:
        conn.close()


def write_js_output(data: Dict[str, Any]) -> None:
    """Write the rankings data as a JavaScript file for The Lab dashboard."""
    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with readable formatting
    json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)

    js_content = (
        "/**\n"
        " * The Lab - Player Rankings Data\n"
        " * IPL Pre-Season Analytics (EPIC-021 Signature Feature)\n"
        f" * Auto-generated: {data['meta']['generated']}\n"
        " * Generator: scripts/generators/generate_rankings.py (TKT-236)\n"
        " *\n"
        f" * Categories: {data['meta']['categories']}\n"
        " * Composite methodology: see config/thresholds.yaml > rankings\n"
        " */\n"
        "\n"
        f"const RANKINGS_DATA = {json_str};\n"
    )

    OUTPUT_JS.write_text(js_content, encoding="utf-8")
    size_kb = OUTPUT_JS.stat().st_size / 1024
    print(f"\nOutput written to: {OUTPUT_JS}")
    print(f"  Size: {size_kb:.1f} KB")


def print_summary(data: Dict[str, Any]) -> None:
    """Print a summary of generated rankings for verification."""
    print("\n" + "=" * 60)
    print("  RANKINGS SUMMARY")
    print("=" * 60)

    for cat in data["categories"]:
        print(f"\n--- {cat['title']} ---")
        for sub in cat["subcategories"]:
            rows = sub["rows"]
            qualified = sub.get("qualifiedCount", len(rows))
            top3 = ", ".join(str(r[1]) if len(r) > 1 else "?" for r in rows[:3])
            print(f"  {sub['title']}: {qualified} qualified | Top 3: {top3}")

    print("\n" + "=" * 60)
    print(f"  Total categories: {data['meta']['categories']}")
    print(f"  Generated: {data['meta']['generated']}")
    print("=" * 60)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    rankings = generate_rankings()
    write_js_output(rankings)
    print_summary(rankings)
    print("\nDone.")
