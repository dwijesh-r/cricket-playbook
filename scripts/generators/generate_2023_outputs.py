#!/usr/bin/env python3
"""
Cricket Playbook - Generate 2023+ Output Files
Author: Stephen Curry (Analytics Lead)
Sprint: 3.0 - Create 2023+ versions of all output files

This script generates 2023+ filtered versions of:
1. batter_bowling_type_detail_2023.csv
2. batter_bowling_type_matchup_2023.csv
3. bowler_handedness_matchup_2023.csv

Performance Optimization (TKT-099):
- Replaced iterative DataFrame filtering with groupby operations
- Reduced O(n*m) complexity to O(n) in batter vs bowling type aggregation
- Bowler handedness uses set_index + .loc for O(1) lookups
"""

from pathlib import Path
from typing import Tuple

import duckdb
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # scripts/generators -> scripts -> project root
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "matchups"

# Date filter for 2023+ data
MIN_DATE = "2023-01-01"

# Thresholds (Updated per Andy Flower review - Sprint 4.0)
MIN_BALLS_VS_TYPE = 50  # Increased from 30 for more stable sample
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


def generate_batter_bowling_type_2023(
    conn: duckdb.DuckDBPyConnection,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
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
              AND dm.match_date >= '{MIN_DATE}'
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
    # TKT-099: Use groupby instead of repeated DataFrame filtering
    # This reduces complexity from O(n*m) to O(n) where n=rows, m=unique batters
    matchup_results = []
    grouped = detail_df.groupby("batter_id")

    for batter_id, batter_df in grouped:
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
    tags_dict = {}
    for _, row in matchup_df.iterrows():
        batter_id = row["batter_id"]
        player_tags = []

        # Pace tags
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
            spin_bpd = row["spin_balls"] / spin_dismissals if spin_dismissals > 0 else 999

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

        tags_dict[batter_id] = player_tags

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

        if batter_id not in tags_dict:
            tags_dict[batter_id] = []

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
                if tag not in tags_dict[batter_id]:
                    tags_dict[batter_id].append(tag)
            elif is_vulnerable:
                tag = f"VULNERABLE_VS_{suffix}"
                if tag not in tags_dict[batter_id]:
                    tags_dict[batter_id].append(tag)

    matchup_df["bowling_type_tags"] = matchup_df["batter_id"].map(tags_dict)
    matchup_df["bowling_type_tags"] = matchup_df["bowling_type_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )

    print(f"   Matchup records: {len(matchup_df)}")

    return detail_df, matchup_df


def generate_bowler_handedness_2023(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
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
              AND dm.match_date >= '{MIN_DATE}'
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
    # TKT-099: set_index provides O(1) lookup, avoiding repeated DataFrame filtering
    lhb = raw_df[raw_df["batting_hand"] == "Left-hand"].set_index("bowler_id")
    rhb = raw_df[raw_df["batting_hand"] == "Right-hand"].set_index("bowler_id")
    common_bowlers = lhb.index.intersection(rhb.index)

    results = []
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

    # Assign handedness tags
    tags = []
    for _, row in matchup_df.iterrows():
        player_tags = []
        eco_diff = row["economy_diff"]
        sr_diff = row["strike_rate_diff"]

        if eco_diff <= -1.0:
            player_tags.append("LHB_SPECIALIST")
        elif eco_diff >= 1.0:
            player_tags.append("RHB_SPECIALIST")

        if eco_diff >= 1.0:
            player_tags.append("LHB_VULNERABLE")
        elif eco_diff <= -1.0:
            player_tags.append("RHB_VULNERABLE")

        if sr_diff <= -6.0 and row["lhb_wickets"] >= 3:
            player_tags.append("LHB_WICKET_TAKER")
        elif sr_diff >= 6.0 and row["rhb_wickets"] >= 3:
            player_tags.append("RHB_WICKET_TAKER")

        tags.append(player_tags)

    matchup_df["handedness_tags"] = tags
    matchup_df["handedness_tags"] = matchup_df["handedness_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )

    print(f"   Matchup records: {len(matchup_df)}")

    return matchup_df


def main() -> int:
    print("=" * 70)
    print("Cricket Playbook - Generate 2023+ Output Files")
    print("Author: Stephen Curry | Sprint 3.0")
    print("=" * 70)
    print(f"\nData filter: match_date >= {MIN_DATE}")

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Generate batter vs bowling type 2023+
    detail_df, matchup_df = generate_batter_bowling_type_2023(conn)

    detail_path = OUTPUT_DIR / "batter_bowling_type_detail_2023.csv"
    detail_df.to_csv(detail_path, index=False)
    print(f"   Saved: {detail_path}")

    matchup_path = OUTPUT_DIR / "batter_bowling_type_matchup_2023.csv"
    matchup_df.to_csv(matchup_path, index=False)
    print(f"   Saved: {matchup_path}")

    # Generate bowler vs handedness 2023+
    handedness_df = generate_bowler_handedness_2023(conn)

    handedness_path = OUTPUT_DIR / "bowler_handedness_matchup_2023.csv"
    handedness_df.to_csv(handedness_path, index=False)
    print(f"   Saved: {handedness_path}")

    conn.close()

    print("\n" + "=" * 70)
    print("2023+ OUTPUT FILES GENERATED SUCCESSFULLY")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
