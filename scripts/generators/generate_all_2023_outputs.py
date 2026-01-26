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

import duckdb
import pandas as pd
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Date filter for 2023+ data
IPL_MIN_DATE = "2023-01-01"

# Thresholds
MIN_BALLS_VS_TYPE = 30
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
# BATTER VS BOWLING TYPE (2023+)
# =============================================================================


def generate_batter_bowling_type_2023(conn) -> tuple:
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
            HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= {MIN_BALLS_VS_TYPE}
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
            pace_avg = (
                round(pace_runs / pace_dismissals, 2) if pace_dismissals > 0 else None
            )
        else:
            pace_balls, pace_runs, pace_dismissals, pace_sr, pace_avg = 0, 0, 0, 0, None

        # Spin stats
        spin_df = batter_df[batter_df["bowling_type"].isin(SPIN_TYPES)]
        if len(spin_df) > 0:
            spin_balls = int(spin_df["balls"].sum())
            spin_runs = spin_df["runs"].sum()
            spin_dismissals = spin_df["dismissals"].sum()
            spin_sr = round(spin_runs * 100 / spin_balls, 2) if spin_balls > 0 else 0
            spin_avg = (
                round(spin_runs / spin_dismissals, 2) if spin_dismissals > 0 else None
            )
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

        # Pace tags
        if row["pace_balls"] >= MIN_BALLS_VS_TYPE:
            pace_sr = row["pace_sr"] or 0
            pace_avg = row["pace_avg"]
            pace_dismissals = row["pace_dismissals"] or 0
            pace_bpd = (
                row["pace_balls"] / pace_dismissals if pace_dismissals > 0 else 999
            )

            if (
                pace_sr >= SPECIALIST_SR_THRESHOLD
                and (pace_avg is None or pace_avg >= SPECIALIST_AVG_THRESHOLD)
                and pace_bpd >= SPECIALIST_BPD_THRESHOLD
            ):
                player_tags.append("SPECIALIST_VS_PACE")
            elif (
                pace_sr < VULNERABLE_SR_THRESHOLD
                or (pace_avg is not None and pace_avg < VULNERABLE_AVG_THRESHOLD)
                or (pace_dismissals >= 3 and pace_bpd < VULNERABLE_BPD_THRESHOLD)
            ):
                player_tags.append("VULNERABLE_VS_PACE")

        # Spin tags
        if row["spin_balls"] >= MIN_BALLS_VS_TYPE:
            spin_sr = row["spin_sr"] or 0
            spin_avg = row["spin_avg"]
            spin_dismissals = row["spin_dismissals"] or 0
            spin_bpd = (
                row["spin_balls"] / spin_dismissals if spin_dismissals > 0 else 999
            )

            if (
                spin_sr >= SPECIALIST_SR_THRESHOLD
                and (spin_avg is None or spin_avg >= SPECIALIST_AVG_THRESHOLD)
                and spin_bpd >= SPECIALIST_BPD_THRESHOLD
            ):
                player_tags.append("SPECIALIST_VS_SPIN")
            elif (
                spin_sr < VULNERABLE_SR_THRESHOLD
                or (spin_avg is not None and spin_avg < VULNERABLE_AVG_THRESHOLD)
                or (spin_dismissals >= 3 and spin_bpd < VULNERABLE_BPD_THRESHOLD)
            ):
                player_tags.append("VULNERABLE_VS_SPIN")

        batter_tags_dict[batter_id] = {
            "name": row["batter_name"],
            "tags": player_tags,
            "overall_sr": (
                row["pace_sr"] * row["pace_balls"] + row["spin_sr"] * row["spin_balls"]
            )
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

        if bowling_type in type_map:
            suffix = type_map[bowling_type]
            is_specialist = (
                sr >= SPECIALIST_SR_THRESHOLD
                and (avg is None or avg >= SPECIALIST_AVG_THRESHOLD)
                and bpd >= SPECIALIST_BPD_THRESHOLD
            )
            is_vulnerable = (
                sr < VULNERABLE_SR_THRESHOLD
                or (avg is not None and avg < VULNERABLE_AVG_THRESHOLD)
                or (dismissals >= 3 and bpd < VULNERABLE_BPD_THRESHOLD)
            )

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


def generate_bowler_handedness_2023(conn) -> tuple:
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
                row["lhb_economy"] * row["lhb_balls"]
                + row["rhb_economy"] * row["rhb_balls"]
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


def generate_player_tags_2023(conn, batter_tags_dict: dict, bowler_tags_dict: dict):
    """Generate player_tags_2023.json with 2023+ data."""

    print("\n3. Generating player_tags_2023.json...")

    # Get additional batter stats for context
    batter_career_df = conn.execute(f"""
        SELECT
            fb.batter_id as player_id,
            dp.current_name as player_name,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_faced,
            SUM(fb.batter_runs) as runs,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as overall_sr,
            ROUND(SUM(CASE WHEN fb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_pct
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
        GROUP BY fb.batter_id, dp.current_name
        HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 100
        ORDER BY runs DESC
    """).df()

    # Get additional bowler stats
    bowler_career_df = conn.execute(f"""
        SELECT
            fb.bowler_id as player_id,
            dp.current_name as player_name,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls_bowled,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
            ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 /
                  NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as economy,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_pct
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
        GROUP BY fb.bowler_id, dp.current_name
        HAVING COUNT(*) FILTER (WHERE fb.is_legal_ball) >= 60
        ORDER BY wickets DESC
    """).df()

    # Build batters list
    batters = []
    for _, row in batter_career_df.iterrows():
        player_id = row["player_id"]
        entry = {
            "player_name": row["player_name"],
            "player_id": player_id,
            "overall_sr": float(row["overall_sr"]) if row["overall_sr"] else 0,
            "tags": batter_tags_dict.get(player_id, {}).get("tags", []),
        }

        # Add role-based tags
        sr = row["overall_sr"] or 0
        boundary_pct = row["boundary_pct"] or 0

        if sr >= 150:
            if "PLAYMAKER" not in entry["tags"]:
                entry["tags"].append("PLAYMAKER")
        elif sr >= 140:
            if "AGGRESSIVE" not in entry["tags"]:
                entry["tags"].append("AGGRESSIVE")
        elif sr < 120 and row["balls_faced"] >= 300:
            if "ANCHOR" not in entry["tags"]:
                entry["tags"].append("ANCHOR")

        if boundary_pct >= 20:
            if "SIX_HITTER" not in entry["tags"]:
                entry["tags"].append("SIX_HITTER")

        batters.append(entry)

    # Build bowlers list
    bowlers = []
    for _, row in bowler_career_df.iterrows():
        player_id = row["player_id"]
        entry = {
            "player_name": row["player_name"],
            "player_id": player_id,
            "economy": float(row["economy"]) if row["economy"] else 0,
            "tags": bowler_tags_dict.get(player_id, {}).get("tags", []),
        }

        # Add role-based tags
        economy = row["economy"] or 10
        dot_pct = row["dot_pct"] or 0

        if economy <= 7.0:
            if "ECONOMICAL" not in entry["tags"]:
                entry["tags"].append("ECONOMICAL")
        elif economy >= 9.5:
            if "EXPENSIVE" not in entry["tags"]:
                entry["tags"].append("EXPENSIVE")

        if dot_pct >= 45:
            if "DOT_BALL_KING" not in entry["tags"]:
                entry["tags"].append("DOT_BALL_KING")

        bowlers.append(entry)

    player_tags = {
        "batters": batters,
        "bowlers": bowlers,
        "metadata": {
            "data_filter": f"match_date >= {IPL_MIN_DATE}",
            "generated_by": "generate_all_2023_outputs.py",
            "sprint": "3.0",
        },
    }

    print(f"   Batters: {len(batters)}")
    print(f"   Bowlers: {len(bowlers)}")

    return player_tags


# =============================================================================
# PLAYER CLUSTERING (2023+)
# =============================================================================


def get_batter_features_2023(conn) -> pd.DataFrame:
    """Extract batter feature vectors for clustering (2023+ only)."""

    df = conn.execute(f"""
        WITH career AS (
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
            d.death_dot
        FROM career c
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        WHERE pp.pp_sr IS NOT NULL
          AND m.mid_sr IS NOT NULL
    """).df()

    return df


def get_bowler_features_2023(conn) -> pd.DataFrame:
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


def cluster_players_2023(conn) -> pd.DataFrame:
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

            for _, row in batter_clean.iterrows():
                cluster_id = int(row["cluster"])
                center = cluster_centers.iloc[cluster_id]

                # Determine cluster label based on center characteristics
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


def main():
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

    tags_path = OUTPUT_DIR / "player_tags_2023.json"
    with open(tags_path, "w") as f:
        json.dump(player_tags, f, indent=2)
    print(f"   Saved: {tags_path}")

    # Generate player clustering 2023+
    clustering_df = cluster_players_2023(conn)

    clustering_path = OUTPUT_DIR / "player_clustering_2023.csv"
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
