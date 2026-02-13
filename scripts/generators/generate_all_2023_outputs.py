#!/usr/bin/env python3
"""
Cricket Playbook - Generate All 2023+ Output Files
Author: Stephen Curry (Analytics Lead)
Sprint: 3.0 - Create 2023+ versions of all output files

This script generates 2023+ filtered versions of:
1. batter_bowling_type_detail_2023.csv
2. batter_bowling_type_matchup_2023.csv
3. bowler_handedness_matchup_2023.csv
4. player_tags_2023.json
5. player_clustering_2023.csv

Data filter: match_date >= 2023-01-01
"""

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import duckdb
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # scripts/generators -> scripts -> project root
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Date filter for 2023+ data
IPL_MIN_DATE = "2023-01-01"

# Thresholds (Updated per Andy Flower review - Sprint 4.0)
MIN_BALLS_VS_TYPE = 50  # Aggregate pace/spin minimum for tag assignment
MIN_BALLS_PER_TYPE = 20  # Individual bowling type minimum for per-type tags
MIN_BALLS_VS_HAND = 60

# Bowling type categories
PACE_TYPES = ["Right-arm pace", "Left-arm pace"]
SPIN_TYPES = [
    "Right-arm off-spin",
    "Right-arm leg-spin",
    "Left-arm orthodox",
    "Left-arm wrist spin",
]

# Tag thresholds
SPECIALIST_SR_THRESHOLD = 130
SPECIALIST_AVG_THRESHOLD = 20
SPECIALIST_BPD_THRESHOLD = 15
VULNERABLE_SR_THRESHOLD = 110
VULNERABLE_AVG_THRESHOLD = 12
VULNERABLE_BPD_THRESHOLD = 12

# =============================================================================
# MULTI-METRIC PHASE THRESHOLDS (Data-driven from IPL 2023+ percentiles)
# Sprint 4.0 - Validated by Andy Flower (Cricket) + Tom Brady (Standards)
# =============================================================================

# BATTER PHASE THRESHOLDS - All 4 metrics per phase
# Format: {"elite": top_25_percentile, "exploitable": bottom_25_percentile}
BATTER_PHASE_THRESHOLDS = {
    "powerplay": {
        "sr": {"elite": 156.0, "exploitable": 130.0},  # 75th: 155.9, 25th: 130.5
        "dot_pct": {
            "elite": 38.0,
            "exploitable": 47.0,
        },  # 25th: 38.6, 75th: 47.2 (lower is better)
        "balls_per_dismissal": {
            "elite": 32.0,
            "exploitable": 17.0,
        },  # 75th: 31.9, 25th: 17.4
        "boundary_pct": {"elite": 27.0, "exploitable": 21.0},  # 75th: 27.0, 25th: 21.0
    },
    "middle": {
        "sr": {"elite": 157.0, "exploitable": 125.0},  # 75th: 156.7, 25th: 125.0
        "dot_pct": {"elite": 25.0, "exploitable": 33.0},  # 25th: 25.4, 75th: 33.1
        "balls_per_dismissal": {
            "elite": 28.0,
            "exploitable": 15.0,
        },  # 75th: 28.4, 25th: 15.4
        "boundary_pct": {"elite": 20.0, "exploitable": 14.0},  # 75th: 20.1, 25th: 13.7
    },
    "death": {
        "sr": {"elite": 192.0, "exploitable": 149.0},  # 75th: 191.8, 25th: 149.2
        "dot_pct": {"elite": 22.0, "exploitable": 33.0},  # 25th: 22.4, 75th: 32.7
        "balls_per_dismissal": {
            "elite": 15.0,
            "exploitable": 9.0,
        },  # 75th: 14.5, 25th: 9.0
        "boundary_pct": {"elite": 28.0, "exploitable": 18.0},  # 75th: 28.0, 25th: 18.0
    },
}

# BOWLER PHASE THRESHOLDS - All 4 metrics per phase
BOWLER_PHASE_THRESHOLDS = {
    "powerplay": {
        "economy": {
            "elite": 8.53,
            "exploitable": 9.71,
        },  # 25th: 8.53, 75th: 9.71 (lower is better)
        "dot_pct": {"elite": 45.0, "exploitable": 39.0},  # 75th: 44.9, 25th: 39.4
        "wickets_per_ball": {
            "elite": 0.049,
            "exploitable": 0.034,
        },  # 75th: 0.049, 25th: 0.034
        "boundary_pct": {
            "elite": 21.6,
            "exploitable": 26.4,
        },  # 25th: 21.6, 75th: 26.4 (lower is better)
    },
    "middle": {
        "economy": {"elite": 8.16, "exploitable": 9.52},  # 25th: 8.16, 75th: 9.52
        "dot_pct": {"elite": 31.0, "exploitable": 26.0},  # 75th: 31.4, 25th: 25.6
        "wickets_per_ball": {
            "elite": 0.055,
            "exploitable": 0.037,
        },  # 75th: 0.055, 25th: 0.037
        "boundary_pct": {"elite": 14.2, "exploitable": 19.4},  # 25th: 14.2, 75th: 19.4
    },
    "death": {
        "economy": {"elite": 10.14, "exploitable": 11.42},  # 25th: 10.14, 75th: 11.42
        "dot_pct": {"elite": 32.0, "exploitable": 26.0},  # 75th: 31.9, 25th: 25.9
        "wickets_per_ball": {
            "elite": 0.101,
            "exploitable": 0.074,
        },  # 75th: 0.101, 25th: 0.074
        "boundary_pct": {"elite": 21.2, "exploitable": 25.3},  # 25th: 21.2, 75th: 25.3
    },
}

# Minimum sample sizes per phase (Lowered in Sprint 4.0 to capture more players)
# Original: Batter 50/50/30, Bowler 100/100/80
# Lowered to improve coverage for players like Fraser-McGurk, Buttler, Dhoni
BATTER_MIN_BALLS = {"powerplay": 30, "middle": 30, "death": 20}
BOWLER_MIN_BALLS = {"powerplay": 60, "middle": 60, "death": 50}


# =============================================================================
# BATTER VS BOWLING TYPE (2023+)
# =============================================================================


def generate_batter_bowling_type_2023(
    conn: duckdb.DuckDBPyConnection,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Generate batter vs bowling type data for 2023+ only."""

    print("\n1. Generating batter vs bowling type data (2023+)...")

    # Get raw batter vs bowling type data with 2023+ filter
    detail_df = conn.execute(
        f"""
        WITH bowler_classification AS (
            SELECT player_id, bowling_style
            FROM dim_bowler_classification
            WHERE bowling_style IS NOT NULL
        ),
        batter_vs_type AS (
            SELECT
                fb.batter_id,
                dp.current_name as batter_name,
                bc.bowling_style as bowling_type,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as dismissals,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) as dots
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            JOIN bowler_classification bc ON fb.bowler_id = bc.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.batter_id, dp.current_name, bc.bowling_style
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 1
        )
        SELECT
            batter_id,
            batter_name,
            bowling_type,
            balls,
            runs,
            dismissals,
            fours,
            sixes,
            dots as dot_balls,
            ROUND(runs * 100.0 / NULLIF(balls, 0), 2) as strike_rate,
            ROUND(runs * 1.0 / NULLIF(dismissals, 0), 2) as average,
            ROUND(dots * 100.0 / NULLIF(balls, 0), 2) as dot_pct,
            ROUND((fours + sixes) * 100.0 / NULLIF(balls, 0), 2) as boundary_pct
        FROM batter_vs_type
        WHERE bowling_type != 'Unknown'
        ORDER BY batter_name, bowling_type
    """
    ).df()

    print(f"   Detail records: {len(detail_df)}")

    # Aggregate into pace vs spin matchup
    matchup_results = []
    batter_tags_dict = {}  # Store tags for player_tags.json

    for batter_id in detail_df["batter_id"].unique():
        batter_df = detail_df[detail_df["batter_id"] == batter_id]
        batter_name = batter_df["batter_name"].iloc[0]

        # Pace stats
        pace_df = batter_df[batter_df["bowling_type"].isin(PACE_TYPES)]
        if len(pace_df) > 0:
            pace_balls = int(pace_df["balls"].sum())
            pace_runs = pace_df["runs"].sum()
            pace_dismissals = pace_df["dismissals"].sum()
            pace_sr = round(pace_runs * 100 / pace_balls, 2) if pace_balls > 0 else 0
            pace_avg = round(pace_runs / pace_dismissals, 2) if pace_dismissals > 0 else None
        else:
            pace_balls, pace_runs, pace_dismissals, pace_sr, pace_avg = 0, 0, 0, 0, None

        # Spin stats
        spin_df = batter_df[batter_df["bowling_type"].isin(SPIN_TYPES)]
        if len(spin_df) > 0:
            spin_balls = int(spin_df["balls"].sum())
            spin_runs = spin_df["runs"].sum()
            spin_dismissals = spin_df["dismissals"].sum()
            spin_sr = round(spin_runs * 100 / spin_balls, 2) if spin_balls > 0 else 0
            spin_avg = round(spin_runs / spin_dismissals, 2) if spin_dismissals > 0 else None
        else:
            spin_balls, spin_runs, spin_dismissals, spin_sr, spin_avg = 0, 0, 0, 0, None

        if pace_balls >= MIN_BALLS_VS_TYPE or spin_balls >= MIN_BALLS_VS_TYPE:
            matchup_results.append(
                {
                    "batter_id": batter_id,
                    "batter_name": batter_name,
                    "pace_balls": pace_balls,
                    "pace_sr": pace_sr,
                    "pace_avg": pace_avg,
                    "pace_dismissals": pace_dismissals,
                    "spin_balls": spin_balls,
                    "spin_sr": spin_sr,
                    "spin_avg": spin_avg,
                    "spin_dismissals": spin_dismissals,
                }
            )

    matchup_df = pd.DataFrame(matchup_results)

    # Assign tags
    for _, row in matchup_df.iterrows():
        batter_id = row["batter_id"]
        player_tags = []

        # Pace tags (aggregate across all pace types)
        if row["pace_balls"] >= MIN_BALLS_VS_TYPE:
            pace_sr = row["pace_sr"] or 0
            pace_avg = row["pace_avg"]
            pace_dismissals = row["pace_dismissals"] or 0
            pace_bpd = row["pace_balls"] / pace_dismissals if pace_dismissals > 0 else 999

            if (
                pace_sr >= SPECIALIST_SR_THRESHOLD
                and (pace_avg is None or pace_avg >= SPECIALIST_AVG_THRESHOLD)
                and pace_bpd >= SPECIALIST_BPD_THRESHOLD
            ):
                player_tags.append("SPECIALIST_VS_PACE")
            else:
                # Require 2+ vulnerability signals to avoid false positives
                # (e.g. slow scorer with high survival, or power hitter with frequent dismissals)
                pace_vuln = 0
                if pace_sr < VULNERABLE_SR_THRESHOLD:
                    pace_vuln += 1
                if pace_avg is not None and pace_avg < VULNERABLE_AVG_THRESHOLD:
                    pace_vuln += 1
                if pace_dismissals >= 3 and pace_bpd < VULNERABLE_BPD_THRESHOLD:
                    pace_vuln += 1
                if pace_vuln >= 2:
                    player_tags.append("VULNERABLE_VS_PACE")

        # Spin tags (aggregate across all spin types)
        if row["spin_balls"] >= MIN_BALLS_VS_TYPE:
            spin_sr = row["spin_sr"] or 0
            spin_avg = row["spin_avg"]
            spin_dismissals = row["spin_dismissals"] or 0
            spin_bpd = row["spin_balls"] / spin_dismissals if spin_dismissals > 0 else 999

            if (
                spin_sr >= SPECIALIST_SR_THRESHOLD
                and (spin_avg is None or spin_avg >= SPECIALIST_AVG_THRESHOLD)
                and spin_bpd >= SPECIALIST_BPD_THRESHOLD
            ):
                player_tags.append("SPECIALIST_VS_SPIN")
            else:
                spin_vuln = 0
                if spin_sr < VULNERABLE_SR_THRESHOLD:
                    spin_vuln += 1
                if spin_avg is not None and spin_avg < VULNERABLE_AVG_THRESHOLD:
                    spin_vuln += 1
                if spin_dismissals >= 3 and spin_bpd < VULNERABLE_BPD_THRESHOLD:
                    spin_vuln += 1
                if spin_vuln >= 2:
                    player_tags.append("VULNERABLE_VS_SPIN")

        batter_tags_dict[batter_id] = {
            "name": row["batter_name"],
            "tags": player_tags,
            "overall_sr": (row["pace_sr"] * row["pace_balls"] + row["spin_sr"] * row["spin_balls"])
            / (row["pace_balls"] + row["spin_balls"])
            if (row["pace_balls"] + row["spin_balls"]) > 0
            else 0,
        }

    # Add specific bowling type tags
    type_map = {
        "Right-arm off-spin": "OFF_SPIN",
        "Right-arm leg-spin": "LEG_SPIN",
        "Left-arm orthodox": "LEFT_ARM_SPIN",
        "Left-arm wrist spin": "LEFT_ARM_WRIST_SPIN",
    }

    for _, row in detail_df.iterrows():
        batter_id = row["batter_id"]
        bowling_type = row["bowling_type"]
        sr = row["strike_rate"] or 0
        avg = row["average"]
        balls = row["balls"]
        dismissals = row["dismissals"]
        bpd = balls / dismissals if dismissals > 0 else 999

        if batter_id not in batter_tags_dict:
            batter_tags_dict[batter_id] = {
                "name": row["batter_name"],
                "tags": [],
                "overall_sr": sr,
            }

        if bowling_type in type_map and balls >= MIN_BALLS_PER_TYPE:
            suffix = type_map[bowling_type]
            is_specialist = (
                sr >= SPECIALIST_SR_THRESHOLD
                and (avg is None or avg >= SPECIALIST_AVG_THRESHOLD)
                and bpd >= SPECIALIST_BPD_THRESHOLD
            )
            # Require 2+ vulnerability signals for individual types too
            type_vuln = 0
            if sr < VULNERABLE_SR_THRESHOLD:
                type_vuln += 1
            if avg is not None and avg < VULNERABLE_AVG_THRESHOLD:
                type_vuln += 1
            if dismissals >= 3 and bpd < VULNERABLE_BPD_THRESHOLD:
                type_vuln += 1
            is_vulnerable = type_vuln >= 2

            if is_specialist:
                tag = f"SPECIALIST_VS_{suffix}"
                if tag not in batter_tags_dict[batter_id]["tags"]:
                    batter_tags_dict[batter_id]["tags"].append(tag)
            elif is_vulnerable:
                tag = f"VULNERABLE_VS_{suffix}"
                if tag not in batter_tags_dict[batter_id]["tags"]:
                    batter_tags_dict[batter_id]["tags"].append(tag)

    # Create tags column for matchup_df
    tags_for_csv = {}
    for batter_id, data in batter_tags_dict.items():
        tags_for_csv[batter_id] = data["tags"]

    matchup_df["bowling_type_tags"] = matchup_df["batter_id"].map(tags_for_csv)
    matchup_df["bowling_type_tags"] = matchup_df["bowling_type_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )

    print(f"   Matchup records: {len(matchup_df)}")

    return detail_df, matchup_df, batter_tags_dict


# =============================================================================
# BOWLER VS HANDEDNESS (2023+)
# =============================================================================


def generate_bowler_handedness_2023(
    conn: duckdb.DuckDBPyConnection,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    """Generate bowler vs handedness data for 2023+ only."""

    print("\n2. Generating bowler vs handedness data (2023+)...")

    raw_df = conn.execute(
        f"""
        WITH bowler_vs_hand AS (
            SELECT
                fb.bowler_id,
                dp.current_name as bowler_name,
                sq.batting_hand,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
                SUM(fb.batter_runs + fb.extra_runs) as runs,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dots,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            JOIN ipl_2026_squads sq ON fb.batter_id = sq.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND sq.batting_hand IS NOT NULL
            GROUP BY fb.bowler_id, dp.current_name, sq.batting_hand
        )
        SELECT
            bowler_id,
            bowler_name,
            batting_hand,
            balls,
            runs,
            wickets,
            dots,
            fours,
            sixes,
            ROUND(runs * 6.0 / NULLIF(balls, 0), 2) as economy,
            ROUND(balls * 1.0 / NULLIF(wickets, 0), 2) as strike_rate,
            ROUND(dots * 100.0 / NULLIF(balls, 0), 2) as dot_pct,
            ROUND((fours + sixes) * 100.0 / NULLIF(balls, 0), 2) as boundary_pct
        FROM bowler_vs_hand
        WHERE balls >= {MIN_BALLS_VS_HAND}
        ORDER BY bowler_name, batting_hand
    """
    ).df()

    print(f"   Raw records: {len(raw_df)}")

    # Calculate differentials
    lhb = raw_df[raw_df["batting_hand"] == "Left-hand"].set_index("bowler_id")
    rhb = raw_df[raw_df["batting_hand"] == "Right-hand"].set_index("bowler_id")
    common_bowlers = lhb.index.intersection(rhb.index)

    results = []
    bowler_tags_dict = {}

    for bowler_id in common_bowlers:
        lhb_row = lhb.loc[bowler_id]
        rhb_row = rhb.loc[bowler_id]

        results.append(
            {
                "bowler_id": bowler_id,
                "bowler_name": lhb_row["bowler_name"],
                "lhb_balls": lhb_row["balls"],
                "lhb_economy": lhb_row["economy"],
                "lhb_strike_rate": lhb_row["strike_rate"],
                "lhb_wickets": lhb_row["wickets"],
                "rhb_balls": rhb_row["balls"],
                "rhb_economy": rhb_row["economy"],
                "rhb_strike_rate": rhb_row["strike_rate"],
                "rhb_wickets": rhb_row["wickets"],
                "economy_diff": lhb_row["economy"] - rhb_row["economy"],
                "strike_rate_diff": (lhb_row["strike_rate"] or 999)
                - (rhb_row["strike_rate"] or 999),
            }
        )

    matchup_df = pd.DataFrame(results)

    # Add wickets_per_ball columns for better tagging
    matchup_df["lhb_wickets_per_ball"] = matchup_df.apply(
        lambda r: r["lhb_wickets"] / r["lhb_balls"] if r["lhb_balls"] > 0 else 0, axis=1
    )
    matchup_df["rhb_wickets_per_ball"] = matchup_df.apply(
        lambda r: r["rhb_wickets"] / r["rhb_balls"] if r["rhb_balls"] > 0 else 0, axis=1
    )
    matchup_df["wickets_per_ball_diff"] = (
        matchup_df["lhb_wickets_per_ball"] - matchup_df["rhb_wickets_per_ball"]
    )

    # Assign handedness tags using wickets/ball ratio (Sprint 3.0 fix)
    wpb_threshold = 0.02  # 2% wickets/ball difference for wicket-taker tags
    min_wpb = 0.03  # Minimum meaningful wickets/ball ratio
    tags = []
    for _, row in matchup_df.iterrows():
        player_tags = []
        eco_diff = row["economy_diff"]
        wpb_diff = row["wickets_per_ball_diff"]
        lhb_wpb = row["lhb_wickets_per_ball"]
        rhb_wpb = row["rhb_wickets_per_ball"]

        if eco_diff <= -1.0:
            player_tags.append("LHB_SPECIALIST")
        elif eco_diff >= 1.0:
            player_tags.append("RHB_SPECIALIST")

        if eco_diff >= 1.0:
            player_tags.append("LHB_VULNERABLE")
        elif eco_diff <= -1.0:
            player_tags.append("RHB_VULNERABLE")

        # Wicket-taking tags using wickets/ball ratio (Sprint 3.0 fix)
        if wpb_diff >= wpb_threshold and lhb_wpb >= min_wpb:
            player_tags.append("LHB_WICKET_TAKER")
        elif wpb_diff <= -wpb_threshold and rhb_wpb >= min_wpb:
            player_tags.append("RHB_WICKET_TAKER")

        tags.append(player_tags)

        # Store for player_tags.json
        bowler_tags_dict[row["bowler_id"]] = {
            "name": row["bowler_name"],
            "tags": player_tags,
            "economy": (
                row["lhb_economy"] * row["lhb_balls"] + row["rhb_economy"] * row["rhb_balls"]
            )
            / (row["lhb_balls"] + row["rhb_balls"])
            if (row["lhb_balls"] + row["rhb_balls"]) > 0
            else 0,
        }

    matchup_df["handedness_tags"] = tags
    matchup_df["handedness_tags"] = matchup_df["handedness_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )

    print(f"   Matchup records: {len(matchup_df)}")

    return matchup_df, bowler_tags_dict


# =============================================================================
# PLAYER TAGS JSON (2023+)
# =============================================================================


def generate_player_tags_2023(
    conn: duckdb.DuckDBPyConnection,
    batter_tags_dict: Dict[str, Dict[str, Any]],
    bowler_tags_dict: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate player_tags_2023.json with multi-metric phase tags.

    Sprint 4.0 - Multi-metric tagging validated by Andy Flower (Cricket) + Tom Brady (Standards)
    Each phase uses 4 metrics: SR/Eco, Dot%, Dismissal/Wicket Rate, Boundary%
    """

    print("\n3. Generating player_tags_2023.json (multi-metric phase tags)...")

    # Get batter stats with ALL 4 metrics per phase
    batter_career_df = conn.execute(f"""
        WITH career AS (
            SELECT
                fb.batter_id as player_id,
                dp.current_name as player_name,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_faced,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as dismissals,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as overall_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as overall_dot_pct,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as overall_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.batter_id, dp.current_name
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 100
        ),
        pp_stats AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as pp_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as pp_dismissals,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_dot_pct,
                ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 /
                      NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as pp_balls_per_dismissal,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'powerplay'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {BATTER_MIN_BALLS["powerplay"]}
        ),
        mid_stats AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as mid_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as mid_dismissals,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_dot_pct,
                ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 /
                      NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as mid_balls_per_dismissal,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'middle'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {BATTER_MIN_BALLS["middle"]}
        ),
        death_stats AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as death_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as death_dismissals,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_dot_pct,
                ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 /
                      NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as death_balls_per_dismissal,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'death'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {BATTER_MIN_BALLS["death"]}
        )
        SELECT
            c.*,
            pp.pp_balls, pp.pp_sr, pp.pp_dot_pct, pp.pp_balls_per_dismissal, pp.pp_boundary_pct,
            m.mid_balls, m.mid_sr, m.mid_dot_pct, m.mid_balls_per_dismissal, m.mid_boundary_pct,
            d.death_balls, d.death_sr, d.death_dot_pct, d.death_balls_per_dismissal, d.death_boundary_pct
        FROM career c
        LEFT JOIN pp_stats pp ON c.player_id = pp.player_id
        LEFT JOIN mid_stats m ON c.player_id = m.player_id
        LEFT JOIN death_stats d ON c.player_id = d.player_id
        ORDER BY c.runs DESC
    """).df()

    # Get bowler stats with ALL 4 metrics per phase
    bowler_career_df = conn.execute(f"""
        WITH career AS (
            SELECT
                fb.bowler_id as player_id,
                dp.current_name as player_name,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_bowled,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_pct,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.bowler_id, dp.current_name
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 60
        ),
        pp_stats AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as pp_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as pp_wickets,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_dot_pct,
                ROUND(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) * 1.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 4) as pp_wickets_per_ball,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'powerplay'
            GROUP BY fb.bowler_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {BOWLER_MIN_BALLS["powerplay"]}
        ),
        mid_stats AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as mid_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as mid_wickets,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_dot_pct,
                ROUND(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) * 1.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 4) as mid_wickets_per_ball,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'middle'
            GROUP BY fb.bowler_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {BOWLER_MIN_BALLS["middle"]}
        ),
        death_stats AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as death_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as death_wickets,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_dot_pct,
                ROUND(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) * 1.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 4) as death_wickets_per_ball,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'death'
            GROUP BY fb.bowler_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {BOWLER_MIN_BALLS["death"]}
        )
        SELECT
            c.*,
            pp.pp_balls, pp.pp_economy, pp.pp_dot_pct, pp.pp_wickets_per_ball, pp.pp_boundary_pct,
            m.mid_balls, m.mid_economy, m.mid_dot_pct, m.mid_wickets_per_ball, m.mid_boundary_pct,
            d.death_balls, d.death_economy, d.death_dot_pct, d.death_wickets_per_ball, d.death_boundary_pct
        FROM career c
        LEFT JOIN pp_stats pp ON c.player_id = pp.player_id
        LEFT JOIN mid_stats m ON c.player_id = m.player_id
        LEFT JOIN death_stats d ON c.player_id = d.player_id
        ORDER BY c.wickets DESC
    """).df()

    # ==========================================================================
    # ALLTIME CAREER CONTEXT (no date filter) — used to override recency-biased LIABILITY tags
    # If a player is career-long elite in a phase but 2023+ data dipped, tag as RECENT_DIP not LIABILITY
    # ==========================================================================
    alltime_batter_df = conn.execute("""
        WITH pp_alltime AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as pp_balls,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_boundary_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND fb.match_phase = 'powerplay'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 100
        ),
        mid_alltime AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as mid_balls,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_sr
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND fb.match_phase = 'middle'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 100
        ),
        death_alltime AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as death_balls,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_sr
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND fb.match_phase = 'death'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 60
        )
        SELECT
            pp.player_id,
            pp.pp_sr, pp.pp_boundary_pct,
            m.mid_sr,
            d.death_sr
        FROM pp_alltime pp
        LEFT JOIN mid_alltime m ON pp.player_id = m.player_id
        LEFT JOIN death_alltime d ON pp.player_id = d.player_id
    """).df()

    alltime_lookup = {}
    for _, arow in alltime_batter_df.iterrows():
        alltime_lookup[arow["player_id"]] = {
            "pp_sr": float(arow["pp_sr"]) if pd.notna(arow.get("pp_sr")) else None,
            "mid_sr": float(arow["mid_sr"]) if pd.notna(arow.get("mid_sr")) else None,
            "death_sr": float(arow["death_sr"]) if pd.notna(arow.get("death_sr")) else None,
        }
    print(f"   Alltime career context: {len(alltime_lookup)} batters")

    # ==========================================================================
    # BATTER MULTI-METRIC PROFILE TAGGING
    # ==========================================================================
    batters = []
    for _, row in batter_career_df.iterrows():
        player_id = row["player_id"]
        entry = {
            "player_name": row["player_name"],
            "player_id": player_id,
            "overall_sr": float(row["overall_sr"]) if pd.notna(row["overall_sr"]) else 0,
            "tags": batter_tags_dict.get(player_id, {}).get("tags", []).copy(),
        }

        # --- POWERPLAY PROFILE TAGS (Multi-metric) ---
        if pd.notna(row.get("pp_sr")) and pd.notna(row.get("pp_balls")):
            pp = BATTER_PHASE_THRESHOLDS["powerplay"]
            pp_sr = row["pp_sr"] or 0
            pp_dots = row.get("pp_dot_pct") or 50
            pp_bpd = row.get("pp_balls_per_dismissal") or 0
            pp_boundary = row.get("pp_boundary_pct") or 0

            # Count elite/exploitable metrics
            pp_elite_count = sum(
                [
                    pp_sr >= pp["sr"]["elite"],
                    pp_dots <= pp["dot_pct"]["elite"],
                    (pp_bpd >= pp["balls_per_dismissal"]["elite"])
                    if pd.notna(row.get("pp_balls_per_dismissal"))
                    else False,
                    pp_boundary >= pp["boundary_pct"]["elite"],
                ]
            )
            pp_exploitable_count = sum(
                [
                    pp_sr <= pp["sr"]["exploitable"],
                    pp_dots >= pp["dot_pct"]["exploitable"],
                    (pp_bpd <= pp["balls_per_dismissal"]["exploitable"])
                    if pd.notna(row.get("pp_balls_per_dismissal"))
                    else False,
                    pp_boundary <= pp["boundary_pct"]["exploitable"],
                ]
            )

            # Profile-based tags (Updated Sprint 4.0 - more inclusive)
            if pp_elite_count >= 3:
                entry["tags"].append("PP_DOMINATOR")
            elif pp_sr >= pp["sr"]["elite"] and pp_boundary >= pp["boundary_pct"]["elite"]:
                # Elite SR + Elite Boundary = aggressive profile
                if pp_dots >= pp["dot_pct"]["exploitable"]:
                    entry["tags"].append("PP_BOOM_OR_BUST")
                else:
                    entry["tags"].append("PP_AGGRESSOR")
            elif pp_sr >= pp["sr"]["elite"]:
                # Elite SR alone = still aggressive
                entry["tags"].append("PP_AGGRESSOR")
            elif (
                pp_bpd
                and pp_bpd >= pp["balls_per_dismissal"]["elite"]
                and pp_sr < pp["sr"]["elite"]
            ):
                entry["tags"].append("PP_ACCUMULATOR")
            elif pp_exploitable_count >= 2:
                alltime = alltime_lookup.get(player_id)
                if alltime and alltime.get("pp_sr") and alltime["pp_sr"] >= pp["sr"]["elite"]:
                    entry["tags"].append("PP_RECENT_DIP")
                else:
                    entry["tags"].append("PP_LIABILITY")

        # --- MIDDLE OVERS PROFILE TAGS (Multi-metric) ---
        if pd.notna(row.get("mid_sr")) and pd.notna(row.get("mid_balls")):
            mid = BATTER_PHASE_THRESHOLDS["middle"]
            mid_sr = row["mid_sr"] or 0
            mid_dots = row.get("mid_dot_pct") or 50
            mid_bpd = row.get("mid_balls_per_dismissal") or 0
            mid_boundary = row.get("mid_boundary_pct") or 0

            mid_elite_count = sum(
                [
                    mid_sr >= mid["sr"]["elite"],
                    mid_dots <= mid["dot_pct"]["elite"],
                    (mid_bpd >= mid["balls_per_dismissal"]["elite"])
                    if pd.notna(row.get("mid_balls_per_dismissal"))
                    else False,
                    mid_boundary >= mid["boundary_pct"]["elite"],
                ]
            )
            mid_exploitable_count = sum(
                [
                    mid_sr <= mid["sr"]["exploitable"],
                    mid_dots >= mid["dot_pct"]["exploitable"],
                    (mid_bpd <= mid["balls_per_dismissal"]["exploitable"])
                    if pd.notna(row.get("mid_balls_per_dismissal"))
                    else False,
                    mid_boundary <= mid["boundary_pct"]["exploitable"],
                ]
            )

            # Profile-based tags (Updated Sprint 4.0 - more inclusive)
            if (
                mid_bpd
                and mid_bpd >= mid["balls_per_dismissal"]["elite"]
                and mid_dots <= mid["dot_pct"]["elite"]
            ):
                entry["tags"].append("MIDDLE_ANCHOR")
            elif mid_sr >= mid["sr"]["elite"] and mid_boundary >= mid["boundary_pct"]["elite"]:
                entry["tags"].append("MIDDLE_ACCELERATOR")
            elif mid_sr >= mid["sr"]["elite"]:
                # Elite SR alone = accelerator profile
                entry["tags"].append("MIDDLE_ACCELERATOR")
            elif mid_bpd and mid_bpd >= mid["balls_per_dismissal"]["elite"]:
                # Elite survival alone = anchor profile
                entry["tags"].append("MIDDLE_ANCHOR")
            elif mid_exploitable_count >= 2:
                alltime = alltime_lookup.get(player_id)
                if alltime and alltime.get("mid_sr") and alltime["mid_sr"] >= mid["sr"]["elite"]:
                    entry["tags"].append("MIDDLE_RECENT_DIP")
                else:
                    entry["tags"].append("MIDDLE_LIABILITY")

        # --- DEATH OVERS PROFILE TAGS (Multi-metric) ---
        if pd.notna(row.get("death_sr")) and pd.notna(row.get("death_balls")):
            death = BATTER_PHASE_THRESHOLDS["death"]
            death_sr = row["death_sr"] or 0
            death_dots = row.get("death_dot_pct") or 50
            death_bpd = row.get("death_balls_per_dismissal") or 0
            death_boundary = row.get("death_boundary_pct") or 0

            death_elite_count = sum(
                [
                    death_sr >= death["sr"]["elite"],
                    death_dots <= death["dot_pct"]["elite"],
                    (death_bpd >= death["balls_per_dismissal"]["elite"])
                    if pd.notna(row.get("death_balls_per_dismissal"))
                    else False,
                    death_boundary >= death["boundary_pct"]["elite"],
                ]
            )
            death_exploitable_count = sum(
                [
                    death_sr <= death["sr"]["exploitable"],
                    death_dots >= death["dot_pct"]["exploitable"],
                    (death_bpd <= death["balls_per_dismissal"]["exploitable"])
                    if pd.notna(row.get("death_balls_per_dismissal"))
                    else False,
                    death_boundary <= death["boundary_pct"]["exploitable"],
                ]
            )

            # Profile-based tags (Updated Sprint 4.0 - more inclusive for finishers)
            if death_elite_count >= 3:
                # Elite in 3+ metrics = true finisher
                entry["tags"].append("DEATH_FINISHER")
            elif (
                death_sr >= death["sr"]["elite"]
                and death_boundary >= death["boundary_pct"]["elite"]
            ):
                if death_bpd and death_bpd >= death["balls_per_dismissal"]["elite"]:
                    entry["tags"].append("DEATH_FINISHER")
                else:
                    entry["tags"].append("DEATH_HITTER")
            elif death_sr >= death["sr"]["elite"]:
                # Elite SR alone = hitter profile
                entry["tags"].append("DEATH_HITTER")
            elif death_elite_count >= 2:
                # Elite in 2 metrics = capable finisher
                entry["tags"].append("DEATH_FINISHER")
            elif death_exploitable_count >= 2:
                alltime = alltime_lookup.get(player_id)
                if (
                    alltime
                    and alltime.get("death_sr")
                    and alltime["death_sr"] >= death["sr"]["elite"]
                ):
                    entry["tags"].append("DEATH_RECENT_DIP")
                else:
                    entry["tags"].append("DEATH_LIABILITY")

        batters.append(entry)

    # ==========================================================================
    # BOWLER MULTI-METRIC PROFILE TAGGING
    # ==========================================================================
    bowlers = []
    for _, row in bowler_career_df.iterrows():
        player_id = row["player_id"]
        entry = {
            "player_name": row["player_name"],
            "player_id": player_id,
            "economy": float(row["economy"]) if pd.notna(row["economy"]) else 0,
            "tags": bowler_tags_dict.get(player_id, {}).get("tags", []).copy(),
        }

        # --- POWERPLAY PROFILE TAGS (Multi-metric) ---
        if pd.notna(row.get("pp_economy")) and pd.notna(row.get("pp_balls")):
            pp = BOWLER_PHASE_THRESHOLDS["powerplay"]
            pp_eco = row["pp_economy"] or 10
            pp_dots = row.get("pp_dot_pct") or 0
            pp_wpb = row.get("pp_wickets_per_ball") or 0
            pp_boundary = row.get("pp_boundary_pct") or 30

            pp_elite_count = sum(
                [
                    pp_eco <= pp["economy"]["elite"],
                    pp_dots >= pp["dot_pct"]["elite"],
                    pp_wpb >= pp["wickets_per_ball"]["elite"],
                    pp_boundary <= pp["boundary_pct"]["elite"],
                ]
            )
            pp_exploitable_count = sum(
                [
                    pp_eco >= pp["economy"]["exploitable"],
                    pp_dots <= pp["dot_pct"]["exploitable"],
                    pp_wpb <= pp["wickets_per_ball"]["exploitable"],
                    pp_boundary >= pp["boundary_pct"]["exploitable"],
                ]
            )

            # Profile-based tags
            if pp_wpb >= pp["wickets_per_ball"]["elite"] and pp_dots >= pp["dot_pct"]["elite"]:
                entry["tags"].append("PP_STRIKE")
            elif pp_eco <= pp["economy"]["elite"] and pp_dots >= pp["dot_pct"]["elite"]:
                entry["tags"].append("PP_CONTAINER")
            elif pp_exploitable_count >= 2:
                entry["tags"].append("PP_LIABILITY")

        # --- MIDDLE OVERS PROFILE TAGS (Multi-metric) ---
        if pd.notna(row.get("mid_economy")) and pd.notna(row.get("mid_balls")):
            mid = BOWLER_PHASE_THRESHOLDS["middle"]
            mid_eco = row["mid_economy"] or 10
            mid_dots = row.get("mid_dot_pct") or 0
            mid_wpb = row.get("mid_wickets_per_ball") or 0
            mid_boundary = row.get("mid_boundary_pct") or 30

            mid_elite_count = sum(
                [
                    mid_eco <= mid["economy"]["elite"],
                    mid_dots >= mid["dot_pct"]["elite"],
                    mid_wpb >= mid["wickets_per_ball"]["elite"],
                    mid_boundary <= mid["boundary_pct"]["elite"],
                ]
            )
            mid_exploitable_count = sum(
                [
                    mid_eco >= mid["economy"]["exploitable"],
                    mid_dots <= mid["dot_pct"]["exploitable"],
                    mid_wpb <= mid["wickets_per_ball"]["exploitable"],
                    mid_boundary >= mid["boundary_pct"]["exploitable"],
                ]
            )

            # Profile-based tags
            if mid_dots >= mid["dot_pct"]["elite"] and mid_eco <= mid["economy"]["elite"]:
                entry["tags"].append("MIDDLE_STRANGLER")
            elif mid_wpb >= mid["wickets_per_ball"]["elite"]:
                entry["tags"].append("MIDDLE_WICKET_TAKER")
            elif mid_elite_count >= 3:
                # Elite in 3+ metrics = complete middle overs bowler
                entry["tags"].append("MIDDLE_STRANGLER")
            elif mid_exploitable_count >= 2:
                entry["tags"].append("MIDDLE_LIABILITY")

        # --- DEATH OVERS PROFILE TAGS (Multi-metric) ---
        if pd.notna(row.get("death_economy")) and pd.notna(row.get("death_balls")):
            death = BOWLER_PHASE_THRESHOLDS["death"]
            death_eco = row["death_economy"] or 12
            death_dots = row.get("death_dot_pct") or 0
            death_wpb = row.get("death_wickets_per_ball") or 0
            death_boundary = row.get("death_boundary_pct") or 30

            death_elite_count = sum(
                [
                    death_eco <= death["economy"]["elite"],
                    death_dots >= death["dot_pct"]["elite"],
                    death_wpb >= death["wickets_per_ball"]["elite"],
                    death_boundary <= death["boundary_pct"]["elite"],
                ]
            )
            death_exploitable_count = sum(
                [
                    death_eco >= death["economy"]["exploitable"],
                    death_dots <= death["dot_pct"]["exploitable"],
                    death_wpb <= death["wickets_per_ball"]["exploitable"],
                    death_boundary >= death["boundary_pct"]["exploitable"],
                ]
            )

            # Profile-based tags (Andy Flower's framework)
            if (
                death_eco <= death["economy"]["elite"]
                and death_wpb >= death["wickets_per_ball"]["elite"]
            ):
                entry["tags"].append("DEATH_COMPLETE")
            elif death_wpb >= death["wickets_per_ball"]["elite"]:
                entry["tags"].append("DEATH_STRIKE")
            elif death_eco <= death["economy"]["elite"]:
                entry["tags"].append("DEATH_CONTAINER")
            elif death_exploitable_count >= 2:
                entry["tags"].append("DEATH_LIABILITY")

        bowlers.append(entry)

    player_tags = {
        "batters": batters,
        "bowlers": bowlers,
        "metadata": {
            "data_filter": f"match_date >= {IPL_MIN_DATE}",
            "generated_by": "generate_all_2023_outputs.py",
            "sprint": "4.0",
            "min_balls_batter": BATTER_MIN_BALLS,
            "min_balls_bowler": BOWLER_MIN_BALLS,
            "note": "Empty phase tags = insufficient phase-specific sample size, not neutral performance",
        },
    }

    print(f"   Batters: {len(batters)}")
    print(f"   Bowlers: {len(bowlers)}")

    return player_tags


# =============================================================================
# PLAYER CLUSTERING (2023+)
# =============================================================================


def get_batter_features_2023(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Extract batter feature vectors for clustering (2023+ only)."""

    df = conn.execute(f"""
        WITH legal_balls_numbered AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.batter_id,
                fb.ball_seq,
                fb.is_legal_ball,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) as legal_ball_num
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
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
        career AS (
            SELECT
                fb.batter_id as player_id,
                dp.current_name as player_name,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_faced,
                SUM(fb.batter_runs) as runs,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as strike_rate,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as batting_average,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_pct,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_ball_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.batter_id, dp.current_name
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 200
        ),
        powerplay AS (
            SELECT
                fb.batter_id as player_id,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_boundary,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_dot
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'powerplay'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 50
        ),
        middle AS (
            SELECT
                fb.batter_id as player_id,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_boundary,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_dot
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'middle'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 50
        ),
        death AS (
            SELECT
                fb.batter_id as player_id,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_sr,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_boundary,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_dot
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'death'
            GROUP BY fb.batter_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 30
        )
        SELECT
            c.player_id,
            c.player_name,
            c.balls_faced,
            c.runs,
            c.strike_rate as overall_sr,
            c.batting_average as overall_avg,
            c.boundary_pct as overall_boundary,
            c.dot_ball_pct as overall_dot,
            pp.pp_sr,
            pp.pp_boundary,
            pp.pp_dot,
            m.mid_sr,
            m.mid_boundary,
            m.mid_dot,
            d.death_sr,
            d.death_boundary,
            d.death_dot,
            COALESCE(bp.avg_batting_position, 4) as avg_batting_position
        FROM career c
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        LEFT JOIN batting_position bp ON c.player_id = bp.player_id
        WHERE pp.pp_sr IS NOT NULL
          AND m.mid_sr IS NOT NULL
    """).df()

    return df


def get_bowler_features_2023(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Extract bowler feature vectors for clustering (2023+ only)."""

    df = conn.execute(f"""
        WITH career AS (
            SELECT
                fb.bowler_id as player_id,
                dp.current_name as player_name,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_bowled,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as economy_rate,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as bowling_average,
                ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as bowling_strike_rate,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_ball_pct,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_conceded_pct
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.bowler_id, dp.current_name
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 120
        ),
        powerplay AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as pp_balls,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_dot,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as pp_boundary
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'powerplay'
            GROUP BY fb.bowler_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 30
        ),
        middle AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as mid_balls,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_dot,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as mid_boundary
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'middle'
            GROUP BY fb.bowler_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 30
        ),
        death AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as death_balls,
                ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_economy,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_dot,
                ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as death_boundary
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.match_phase = 'death'
            GROUP BY fb.bowler_id
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 30
        )
        SELECT
            c.player_id,
            c.player_name,
            c.balls_bowled,
            c.wickets,
            c.economy_rate as overall_economy,
            c.bowling_average as overall_avg,
            c.bowling_strike_rate as overall_sr,
            c.dot_ball_pct as overall_dot,
            c.boundary_conceded_pct as overall_boundary,
            pp.pp_economy,
            pp.pp_dot,
            pp.pp_boundary,
            pp.pp_balls,
            m.mid_economy,
            m.mid_dot,
            m.mid_boundary,
            m.mid_balls,
            d.death_economy,
            d.death_dot,
            d.death_boundary,
            d.death_balls,
            ROUND(pp.pp_balls * 100.0 / NULLIF(c.balls_bowled, 0), 2) as pp_pct,
            ROUND(m.mid_balls * 100.0 / NULLIF(c.balls_bowled, 0), 2) as mid_pct,
            ROUND(d.death_balls * 100.0 / NULLIF(c.balls_bowled, 0), 2) as death_pct
        FROM career c
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        WHERE pp.pp_economy IS NOT NULL
          AND m.mid_economy IS NOT NULL
          AND d.death_economy IS NOT NULL
    """).df()

    return df


def cluster_players_2023(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Cluster batters and bowlers based on 2023+ data."""

    print("\n4. Generating player clustering data (2023+)...")

    # Get features
    batter_df = get_batter_features_2023(conn)
    bowler_df = get_bowler_features_2023(conn)

    print(f"   Batters with complete 2023+ data: {len(batter_df)}")
    print(f"   Bowlers with complete 2023+ data: {len(bowler_df)}")

    results = []

    # Cluster batters
    if len(batter_df) >= 4:
        batter_feature_cols = [
            "overall_sr",
            "overall_avg",
            "overall_boundary",
            "overall_dot",
            "pp_sr",
            "pp_boundary",
            "pp_dot",
            "mid_sr",
            "mid_boundary",
            "mid_dot",
            "death_sr",
            "death_boundary",
            "death_dot",
        ]

        batter_clean = batter_df.dropna(subset=batter_feature_cols).copy()
        n_batter_clusters = min(5, len(batter_clean))

        if len(batter_clean) >= n_batter_clusters:
            scaler = StandardScaler()
            X_batter = scaler.fit_transform(batter_clean[batter_feature_cols])

            kmeans = KMeans(n_clusters=n_batter_clusters, random_state=42, n_init=10)
            batter_clean["cluster"] = kmeans.fit_predict(X_batter)

            # Map cluster IDs to descriptive labels based on characteristics
            cluster_centers = pd.DataFrame(
                scaler.inverse_transform(kmeans.cluster_centers_),
                columns=batter_feature_cols,
            )

            # Position threshold for top-order guard
            TOP_ORDER_POS_THRESHOLD = 2.5

            for _, row in batter_clean.iterrows():
                cluster_id = int(row["cluster"])
                center = cluster_centers.iloc[cluster_id]
                avg_pos = row.get("avg_batting_position", 4.0)

                # Determine cluster label based on center characteristics
                # Position guard: top-order batters (avg_pos <= 2.5) cannot be DEATH_FINISHER
                if avg_pos <= TOP_ORDER_POS_THRESHOLD:
                    # Top-order labeling (no DEATH_FINISHER)
                    if center["pp_sr"] > 145:
                        cluster_label = "POWERPLAY_AGGRESSOR"
                    elif center["overall_sr"] < 125 and center["overall_avg"] > 35:
                        cluster_label = "ANCHOR"
                    elif center["overall_boundary"] > 18:
                        cluster_label = "BOUNDARY_HITTER"
                    else:
                        cluster_label = "BALANCED"
                else:
                    # Middle/lower order — DEATH_FINISHER allowed
                    if center["death_sr"] > 150 and center["death_boundary"] > 20:
                        cluster_label = "DEATH_FINISHER"
                    elif center["pp_sr"] > 145:
                        cluster_label = "POWERPLAY_AGGRESSOR"
                    elif center["overall_sr"] < 125 and center["overall_avg"] > 35:
                        cluster_label = "ANCHOR"
                    elif center["overall_boundary"] > 18:
                        cluster_label = "BOUNDARY_HITTER"
                    else:
                        cluster_label = "BALANCED"

                results.append(
                    {
                        "player_id": row["player_id"],
                        "player_name": row["player_name"],
                        "player_type": "batter",
                        "cluster_id": cluster_id,
                        "cluster_label": cluster_label,
                        "balls": int(row["balls_faced"]),
                        "overall_sr": row["overall_sr"],
                        "overall_avg": row["overall_avg"],
                        "overall_boundary_pct": row["overall_boundary"],
                        "overall_dot_pct": row["overall_dot"],
                        "pp_sr": row["pp_sr"],
                        "mid_sr": row["mid_sr"],
                        "death_sr": row["death_sr"],
                        "death_boundary_pct": row["death_boundary"],
                        "avg_batting_position": round(float(avg_pos), 1),
                    }
                )

            print(f"   Batter clusters created: {n_batter_clusters}")

    # Cluster bowlers
    if len(bowler_df) >= 4:
        bowler_feature_cols = [
            "overall_economy",
            "overall_avg",
            "overall_sr",
            "overall_dot",
            "overall_boundary",
            "pp_economy",
            "pp_dot",
            "pp_boundary",
            "mid_economy",
            "mid_dot",
            "mid_boundary",
            "death_economy",
            "death_dot",
            "death_boundary",
            "pp_pct",
            "mid_pct",
            "death_pct",
        ]

        bowler_clean = bowler_df.dropna(subset=bowler_feature_cols).copy()
        n_bowler_clusters = min(5, len(bowler_clean))

        if len(bowler_clean) >= n_bowler_clusters:
            scaler = StandardScaler()
            X_bowler = scaler.fit_transform(bowler_clean[bowler_feature_cols])

            kmeans = KMeans(n_clusters=n_bowler_clusters, random_state=42, n_init=10)
            bowler_clean["cluster"] = kmeans.fit_predict(X_bowler)

            cluster_centers = pd.DataFrame(
                scaler.inverse_transform(kmeans.cluster_centers_),
                columns=bowler_feature_cols,
            )

            for _, row in bowler_clean.iterrows():
                cluster_id = int(row["cluster"])
                center = cluster_centers.iloc[cluster_id]

                # Determine cluster label based on center characteristics
                if center["pp_pct"] > 35:
                    cluster_label = "POWERPLAY_SPECIALIST"
                elif center["death_pct"] > 35:
                    cluster_label = "DEATH_SPECIALIST"
                elif center["overall_dot"] > 45:
                    cluster_label = "DOT_BALL_MACHINE"
                elif center["overall_economy"] < 7.5:
                    cluster_label = "ECONOMICAL"
                else:
                    cluster_label = "BALANCED"

                results.append(
                    {
                        "player_id": row["player_id"],
                        "player_name": row["player_name"],
                        "player_type": "bowler",
                        "cluster_id": cluster_id,
                        "cluster_label": cluster_label,
                        "balls": int(row["balls_bowled"]),
                        "wickets": int(row["wickets"]),
                        "overall_economy": row["overall_economy"],
                        "overall_avg": row["overall_avg"],
                        "overall_dot_pct": row["overall_dot"],
                        "pp_economy": row["pp_economy"],
                        "mid_economy": row["mid_economy"],
                        "death_economy": row["death_economy"],
                        "pp_pct": row["pp_pct"],
                        "mid_pct": row["mid_pct"],
                        "death_pct": row["death_pct"],
                    }
                )

            print(f"   Bowler clusters created: {n_bowler_clusters}")

    clustering_df = pd.DataFrame(results)
    print(f"   Total players clustered: {len(clustering_df)}")

    return clustering_df


# =============================================================================
# MAIN
# =============================================================================


def main() -> int:
    print("=" * 70)
    print("Cricket Playbook - Generate All 2023+ Output Files")
    print("Author: Stephen Curry | Sprint 3.0")
    print("=" * 70)
    print(f"\nData filter: match_date >= {IPL_MIN_DATE}")

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Generate batter vs bowling type 2023+
    detail_df, matchup_df, batter_tags_dict = generate_batter_bowling_type_2023(conn)

    detail_path = OUTPUT_DIR / "batter_bowling_type_detail_2023.csv"
    detail_df.to_csv(detail_path, index=False)
    print(f"   Saved: {detail_path}")

    matchup_path = OUTPUT_DIR / "batter_bowling_type_matchup_2023.csv"
    matchup_df.to_csv(matchup_path, index=False)
    print(f"   Saved: {matchup_path}")

    # Generate bowler vs handedness 2023+
    handedness_df, bowler_tags_dict = generate_bowler_handedness_2023(conn)

    handedness_path = OUTPUT_DIR / "bowler_handedness_matchup_2023.csv"
    handedness_df.to_csv(handedness_path, index=False)
    print(f"   Saved: {handedness_path}")

    # Generate player_tags_2023.json
    player_tags = generate_player_tags_2023(conn, batter_tags_dict, bowler_tags_dict)

    tags_path = OUTPUT_DIR / "tags" / "player_tags_2023.json"
    with open(tags_path, "w") as f:
        json.dump(player_tags, f, indent=2)
    print(f"   Saved: {tags_path}")

    # Generate player clustering 2023+
    clustering_df = cluster_players_2023(conn)

    clustering_path = OUTPUT_DIR / "tags" / "player_clustering_2023.csv"
    clustering_df.to_csv(clustering_path, index=False)
    print(f"   Saved: {clustering_path}")

    conn.close()

    print("\n" + "=" * 70)
    print("2023+ OUTPUT FILES GENERATED SUCCESSFULLY")
    print("=" * 70)
    print("\nFiles created:")
    print(f"  1. {detail_path}")
    print(f"  2. {matchup_path}")
    print(f"  3. {handedness_path}")
    print(f"  4. {tags_path}")
    print(f"  5. {clustering_path}")

    return 0


if __name__ == "__main__":
    exit(main())
