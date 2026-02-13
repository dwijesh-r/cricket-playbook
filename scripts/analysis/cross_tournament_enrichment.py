#!/usr/bin/env python3
"""
Cricket Playbook - Cross-Tournament Enrichment for Uncapped Players
====================================================================
Queries DuckDB for all T20 data (2023+) for IPL 2026 squad players
who have zero IPL data since 2023. Covers BBL, PSL, Vitality Blast,
CPL, SA20, The Hundred, MLC, Super Smash, ILT20, Syed Mushtaq Ali
Trophy, international T20s, etc.

Output: outputs/tags/cross_tournament_profiles.json

Author: Stephen Curry (Analytics Lead)
Domain Review: Andy Flower
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Set

import duckdb
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
SQUADS_PATH = PROJECT_DIR / "data" / "ipl_2026_squads.csv"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "tags" / "cross_tournament_profiles.json"

T20_MIN_DATE = "2023-01-01"
TOP_ORDER_POS_THRESHOLD = 2.5


def get_uncapped_player_ids(squad_csv: Path, conn: duckdb.DuckDBPyConnection) -> Set[str]:
    """Find squad players with zero IPL balls faced AND zero IPL balls bowled since 2023."""
    # Load all squad player IDs
    squad_ids = set()
    with open(squad_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            squad_ids.add(row["player_id"].strip())

    # Find players with IPL data since 2023
    ipl_batters = conn.execute(f"""
        SELECT DISTINCT fb.batter_id as player_id
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{T20_MIN_DATE}'
          AND fb.is_legal_ball = true
    """).df()

    ipl_bowlers = conn.execute(f"""
        SELECT DISTINCT fb.bowler_id as player_id
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{T20_MIN_DATE}'
          AND fb.is_legal_ball = true
    """).df()

    ipl_player_ids = set(ipl_batters["player_id"].tolist()) | set(ipl_bowlers["player_id"].tolist())

    uncapped = squad_ids - ipl_player_ids
    print(f"  Squad players: {len(squad_ids)}")
    print(f"  With IPL data: {len(squad_ids & ipl_player_ids)}")
    print(f"  Uncapped (no IPL): {len(uncapped)}")
    return uncapped


def get_all_t20_batting(conn: duckdb.DuckDBPyConnection, player_ids: Set[str]) -> pd.DataFrame:
    """Get batting stats from all T20 tournaments since 2023 (excluding IPL)."""
    if not player_ids:
        return pd.DataFrame()

    ids_str = ", ".join(f"'{pid}'" for pid in player_ids)

    df = conn.execute(f"""
        WITH legal_balls_numbered AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.batter_id,
                fb.ball_seq,
                fb.is_legal_ball,
                fb.batter_runs,
                fb.extra_runs,
                fb.is_wicket,
                fb.match_phase,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) as legal_ball_num
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.batter_id IN ({ids_str})
        ),
        batting_position AS (
            SELECT
                batter_id as player_id,
                AVG(batting_position) as avg_batting_position
            FROM (
                SELECT
                    batter_id,
                    match_id,
                    innings,
                    MIN(legal_ball_num) as first_legal_ball,
                    CASE
                        WHEN MIN(legal_ball_num) <= 6 THEN 1
                        WHEN MIN(legal_ball_num) <= 24 THEN 2
                        WHEN MIN(legal_ball_num) <= 48 THEN 3
                        WHEN MIN(legal_ball_num) <= 72 THEN 4
                        WHEN MIN(legal_ball_num) <= 96 THEN 5
                        ELSE 6
                    END as batting_position
                FROM legal_balls_numbered
                WHERE is_legal_ball = true
                GROUP BY batter_id, match_id, innings
            ) t
            GROUP BY batter_id
        ),
        innings_scores AS (
            SELECT
                batter_id as player_id,
                match_id,
                innings,
                SUM(batter_runs) as innings_runs
            FROM legal_balls_numbered
            GROUP BY batter_id, match_id, innings
        ),
        career AS (
            SELECT
                fb.batter_id as player_id,
                dp.current_name as player_name,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_faced,
                SUM(fb.batter_runs) as runs,
                COUNT(DISTINCT CONCAT(fb.match_id, '_', fb.innings)) as innings,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as dismissals,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as strike_rate,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as average,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_pct,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_ball_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.batter_id IN ({ids_str})
            GROUP BY fb.batter_id, dp.current_name
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 30
        ),
        milestones AS (
            SELECT
                player_id,
                MAX(innings_runs) as highest_score,
                SUM(CASE WHEN innings_runs >= 50 AND innings_runs < 100 THEN 1 ELSE 0 END) as fifties,
                SUM(CASE WHEN innings_runs >= 100 THEN 1 ELSE 0 END) as hundreds
            FROM innings_scores
            GROUP BY player_id
        ),
        tournaments AS (
            SELECT
                fb.batter_id as player_id,
                LIST(DISTINCT dt.tournament_name ORDER BY dt.tournament_name) as tournament_list
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.batter_id IN ({ids_str})
              AND fb.is_legal_ball = true
            GROUP BY fb.batter_id
        ),
        pp AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as pp_balls,
                SUM(fb.batter_runs) as pp_runs,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_sr,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as pp_avg,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.match_phase = 'powerplay'
              AND fb.batter_id IN ({ids_str})
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 20
        ),
        mid AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as mid_balls,
                SUM(fb.batter_runs) as mid_runs,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_sr,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as mid_avg,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.match_phase = 'middle'
              AND fb.batter_id IN ({ids_str})
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 15
        ),
        death AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as death_balls,
                SUM(fb.batter_runs) as death_runs,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_sr,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as death_avg,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.match_phase = 'death'
              AND fb.batter_id IN ({ids_str})
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 10
        )
        SELECT
            c.*,
            COALESCE(ms.highest_score, 0) as highest_score,
            COALESCE(ms.fifties, 0) as fifties,
            COALESCE(ms.hundreds, 0) as hundreds,
            t.tournament_list,
            COALESCE(bp.avg_batting_position, 4) as avg_batting_position,
            p.pp_balls, p.pp_runs, p.pp_sr, p.pp_avg, p.pp_boundary_pct,
            m.mid_balls, m.mid_runs, m.mid_sr, m.mid_avg, m.mid_boundary_pct,
            d.death_balls, d.death_runs, d.death_sr, d.death_avg, d.death_boundary_pct
        FROM career c
        LEFT JOIN milestones ms ON c.player_id = ms.player_id
        LEFT JOIN tournaments t ON c.player_id = t.player_id
        LEFT JOIN batting_position bp ON c.player_id = bp.player_id
        LEFT JOIN pp p ON c.player_id = p.player_id
        LEFT JOIN mid m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
    """).df()

    return df


def get_all_t20_bowling(conn: duckdb.DuckDBPyConnection, player_ids: Set[str]) -> pd.DataFrame:
    """Get bowling stats from all T20 tournaments since 2023 (excluding IPL)."""
    if not player_ids:
        return pd.DataFrame()

    ids_str = ", ".join(f"'{pid}'" for pid in player_ids)

    df = conn.execute(f"""
        WITH career AS (
            SELECT
                fb.bowler_id as player_id,
                dp.current_name as player_name,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
                COUNT(DISTINCT fb.match_id) as matches,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as economy,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as avg,
                ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as sr,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.bowler_id IN ({ids_str})
            GROUP BY fb.bowler_id, dp.current_name
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 60
        ),
        tournaments AS (
            SELECT
                fb.bowler_id as player_id,
                LIST(DISTINCT dt.tournament_name ORDER BY dt.tournament_name) as tournament_list
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dm.match_date >= '{T20_MIN_DATE}'
              AND dt.tournament_name != 'Indian Premier League'
              AND fb.bowler_id IN ({ids_str})
              AND fb.is_legal_ball = true
            GROUP BY fb.bowler_id
        )
        SELECT c.*, t.tournament_list
        FROM career c
        LEFT JOIN tournaments t ON c.player_id = t.player_id
    """).df()

    return df


def assign_label(row: pd.Series) -> str:
    """Assign cluster label using same rules as Phase 2 with position guard."""
    avg_pos = row.get("avg_batting_position", 4.0)
    pp_sr = row.get("pp_sr")
    death_sr = row.get("death_sr")
    death_boundary = row.get("death_boundary_pct")
    overall_sr = row.get("strike_rate", 130)
    overall_avg = row.get("average", 25)
    boundary_pct = row.get("boundary_pct", 15)

    if avg_pos <= TOP_ORDER_POS_THRESHOLD:
        # Top-order: no DEATH_FINISHER
        if pp_sr is not None and pp_sr > 145:
            return "POWERPLAY_AGGRESSOR"
        elif overall_sr < 125 and overall_avg is not None and overall_avg > 35:
            return "ANCHOR"
        elif boundary_pct is not None and boundary_pct > 18:
            return "BOUNDARY_HITTER"
        else:
            return "BALANCED"
    else:
        # Middle/lower order
        if (
            death_sr is not None
            and death_sr > 150
            and death_boundary is not None
            and death_boundary > 20
        ):
            return "DEATH_FINISHER"
        elif pp_sr is not None and pp_sr > 145:
            return "POWERPLAY_AGGRESSOR"
        elif overall_sr < 125 and overall_avg is not None and overall_avg > 35:
            return "ANCHOR"
        elif boundary_pct is not None and boundary_pct > 18:
            return "BOUNDARY_HITTER"
        else:
            return "BALANCED"


def _safe_float(val) -> Optional[float]:
    """Safely convert to float, returning None for NaN/None."""
    if val is None:
        return None
    try:
        import math

        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else round(f, 2)
    except (TypeError, ValueError):
        return None


def _safe_int_val(val) -> Optional[int]:
    """Safely convert to int, returning None for NaN/None."""
    if val is None:
        return None
    try:
        import math

        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else int(f)
    except (TypeError, ValueError):
        return None


def _classify_sample(balls: Optional[int]) -> str:
    """Classify sample size based on balls faced/bowled."""
    if balls is None or balls < 30:
        return "LOW"
    elif balls < 100:
        return "MEDIUM"
    else:
        return "HIGH"


def main() -> None:
    """Orchestrate cross-tournament enrichment."""
    print("=" * 60)
    print("Cross-Tournament Enrichment for Uncapped Players")
    print("=" * 60)

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # Step 1: Find uncapped players
        print("\n1. Identifying uncapped players...")
        uncapped_ids = get_uncapped_player_ids(SQUADS_PATH, conn)

        if not uncapped_ids:
            print("  No uncapped players found.")
            return

        # Step 2: Get cross-tournament batting data
        print("\n2. Querying cross-tournament batting data...")
        batting_df = get_all_t20_batting(conn, uncapped_ids)
        print(f"  Players with batting data: {len(batting_df)}")

        # Step 3: Get cross-tournament bowling data
        print("\n3. Querying cross-tournament bowling data...")
        bowling_df = get_all_t20_bowling(conn, uncapped_ids)
        print(f"  Players with bowling data: {len(bowling_df)}")

    finally:
        conn.close()

    # Step 4: Build output
    print("\n4. Building cross-tournament profiles...")
    players: Dict[str, dict] = {}

    # Index bowling by player_id
    bowling_by_id: Dict[str, pd.Series] = {}
    if not bowling_df.empty:
        for _, brow in bowling_df.iterrows():
            bowling_by_id[brow["player_id"]] = brow

    # Process batting data
    if not batting_df.empty:
        for _, row in batting_df.iterrows():
            pid = row["player_id"]
            tournaments = row.get("tournament_list", [])
            if isinstance(tournaments, str):
                tournaments = [tournaments]
            elif tournaments is None:
                tournaments = []

            cluster_label = assign_label(row)

            # Build phase data matching IPL profile convention
            phase: dict = {}
            if row.get("pp_sr") is not None:
                phase["powerplay"] = {
                    "sr": _safe_float(row["pp_sr"]),
                    "avg": _safe_float(row.get("pp_avg")),
                    "boundary_pct": _safe_float(row.get("pp_boundary_pct")),
                    "balls": _safe_int_val(row.get("pp_balls")),
                    "runs": _safe_int_val(row.get("pp_runs")),
                    "sample_size": _classify_sample(_safe_int_val(row.get("pp_balls"))),
                }
            if row.get("mid_sr") is not None:
                phase["middle"] = {
                    "sr": _safe_float(row["mid_sr"]),
                    "avg": _safe_float(row.get("mid_avg")),
                    "boundary_pct": _safe_float(row.get("mid_boundary_pct")),
                    "balls": _safe_int_val(row.get("mid_balls")),
                    "runs": _safe_int_val(row.get("mid_runs")),
                    "sample_size": _classify_sample(_safe_int_val(row.get("mid_balls"))),
                }
            if row.get("death_sr") is not None:
                phase["death"] = {
                    "sr": _safe_float(row["death_sr"]),
                    "avg": _safe_float(row.get("death_avg")),
                    "boundary_pct": _safe_float(row.get("death_boundary_pct")),
                    "balls": _safe_int_val(row.get("death_balls")),
                    "runs": _safe_int_val(row.get("death_runs")),
                    "sample_size": _classify_sample(_safe_int_val(row.get("death_balls"))),
                }

            player_entry: dict = {
                "batting": {
                    "innings": _safe_int_val(row["innings"]),
                    "runs": _safe_int_val(row["runs"]),
                    "balls_faced": _safe_int_val(row["balls_faced"]),
                    "average": _safe_float(row["average"]),
                    "strike_rate": _safe_float(row["strike_rate"]),
                    "fifties": _safe_int_val(row.get("fifties", 0)),
                    "hundreds": _safe_int_val(row.get("hundreds", 0)),
                    "fours": _safe_int_val(row.get("fours", 0)),
                    "sixes": _safe_int_val(row.get("sixes", 0)),
                    "boundary_pct": _safe_float(row.get("boundary_pct")),
                    "dot_ball_pct": _safe_float(row.get("dot_ball_pct")),
                    "highest_score": _safe_int_val(row.get("highest_score", 0)),
                    "sample_size": _classify_sample(_safe_int_val(row["balls_faced"])),
                    "avg_batting_position": _safe_float(row.get("avg_batting_position")),
                },
                "phase": phase,
                "bowling": None,
                "cluster_label": cluster_label,
                "tournaments": list(tournaments),
                "total_balls": _safe_int_val(row["balls_faced"]),
            }

            # Add bowling if available
            if pid in bowling_by_id:
                brow = bowling_by_id[pid]
                bowl_tournaments = brow.get("tournament_list", [])
                if isinstance(bowl_tournaments, str):
                    bowl_tournaments = [bowl_tournaments]
                elif bowl_tournaments is None:
                    bowl_tournaments = []

                player_entry["bowling"] = {
                    "matches": _safe_int_val(brow["matches"]),
                    "wickets": _safe_int_val(brow["wickets"]),
                    "balls_bowled": _safe_int_val(brow["balls"]),
                    "economy": _safe_float(brow["economy"]),
                    "average": _safe_float(brow["avg"]),
                    "strike_rate": _safe_float(brow["sr"]),
                    "dot_ball_pct": _safe_float(brow.get("dot_pct")),
                    "sample_size": _classify_sample(_safe_int_val(brow["balls"])),
                }
                player_entry["total_balls"] += _safe_int_val(brow["balls"]) or 0
                # Merge tournament lists
                all_tournaments = set(tournaments) | set(bowl_tournaments)
                player_entry["tournaments"] = sorted(all_tournaments)
                del bowling_by_id[pid]

            players[pid] = player_entry

    # Process bowling-only players (no batting data but have bowling)
    for pid, brow in bowling_by_id.items():
        tournaments = brow.get("tournament_list", [])
        if isinstance(tournaments, str):
            tournaments = [tournaments]
        elif tournaments is None:
            tournaments = []

        players[pid] = {
            "batting": None,
            "phase": {},
            "bowling": {
                "matches": _safe_int_val(brow["matches"]),
                "wickets": _safe_int_val(brow["wickets"]),
                "balls_bowled": _safe_int_val(brow["balls"]),
                "economy": _safe_float(brow["economy"]),
                "average": _safe_float(brow["avg"]),
                "strike_rate": _safe_float(brow["sr"]),
                "dot_ball_pct": _safe_float(brow.get("dot_pct")),
                "sample_size": _classify_sample(_safe_int_val(brow["balls"])),
            },
            "cluster_label": None,
            "tournaments": list(tournaments),
            "total_balls": _safe_int_val(brow["balls"]) or 0,
        }

    # Step 5: Write output
    print(f"\n5. Writing {len(players)} cross-tournament profiles...")
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_scope": "all_t20_since_2023_excl_ipl",
        "players": players,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  Output: {OUTPUT_PATH}")
    print(f"  Players enriched: {len(players)}")
    enriched_with_batting = sum(1 for p in players.values() if p["batting"])
    enriched_with_bowling = sum(1 for p in players.values() if p["bowling"])
    print(f"  With batting: {enriched_with_batting}")
    print(f"  With bowling: {enriched_with_bowling}")
    print("\nDone.")


if __name__ == "__main__":
    main()
