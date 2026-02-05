#!/usr/bin/env python3
"""
Cricket Playbook - Entry Point Analysis
Author: Stephen Curry (Analytics Lead)
Sprint: 2.9 - Entry Point Bug Fix

Enhanced entry point analysis with:
1. Entry point in LEGAL balls only (not ball_seq which includes wides/no-balls)
2. Median and mode entry points (not just average)
3. Bowler over distribution (when they bowl 1st, 2nd, 3rd, 4th overs)

Entry Point Definition:
- For opener: Entry ball = 1 (first ball of innings)
- For batter at position N: Entry ball = ball after (N-1)th wicket falls
- Example: Batter at 3 comes in after wicket at ball 29 → Entry ball = 30

Bug Fix (Sprint 2.9):
- Previous version used ball_seq which includes ALL deliveries (wides, no-balls)
- T20 has 120 legal balls but ball_seq can go to 140+ due to extras
- Now uses cumulative legal ball count, capped at max 120
"""

import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Data filter - only use recent IPL seasons (2023 onwards)
# This accounts for drift in stats due to evolution of the game
IPL_MIN_DATE = "2023-01-01"  # IPL 2023, 2024, 2025

# Minimum innings to include
MIN_INNINGS = 15  # Increased from 5 per Founder Review #3


def get_batter_entry_points(conn) -> pd.DataFrame:
    """Calculate entry ball for each batter in each innings.

    Uses cumulative LEGAL ball count (not ball_seq which includes extras).
    T20 innings have max 120 legal balls.
    """

    # Get all batting appearances with legal ball count (not ball_seq)
    df = conn.execute(f"""
        WITH legal_balls_numbered AS (
            -- First, number only legal balls within each innings
            SELECT
                fb.match_id,
                fb.innings,
                fb.batter_id,
                fb.ball_seq,
                fb.is_legal_ball,
                -- Cumulative count of legal balls in the innings
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) as legal_ball_num
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        batter_first_legal_ball AS (
            -- Get the first LEGAL ball faced by each batter
            SELECT
                match_id,
                innings,
                batter_id,
                MIN(legal_ball_num) as entry_ball
            FROM legal_balls_numbered
            WHERE is_legal_ball = true
            GROUP BY match_id, innings, batter_id
        )
        SELECT
            fb.batter_id,
            dp.current_name as batter_name,
            fb.match_id,
            fb.innings,
            -- Cap at 120 (max legal balls in T20)
            LEAST(fb.entry_ball, 120) as entry_ball
        FROM batter_first_legal_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        ORDER BY batter_id, match_id, innings
    """).df()

    return df


def calculate_batter_entry_stats(entry_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate median, mode, and average entry points for each batter."""

    results = []

    for batter_id in entry_df["batter_id"].unique():
        batter_df = entry_df[entry_df["batter_id"] == batter_id]
        batter_name = batter_df["batter_name"].iloc[0]

        entry_balls = batter_df["entry_ball"].values
        innings_count = len(entry_balls)

        if innings_count < MIN_INNINGS:
            continue

        # Calculate stats
        mean_entry = np.mean(entry_balls)
        median_entry = np.median(entry_balls)

        # Mode (most common entry ball, binned to nearest 6 balls = 1 over)
        binned_entries = [int(e // 6) * 6 for e in entry_balls]
        mode_entry = Counter(binned_entries).most_common(1)[0][0]

        # Convert to overs.balls format
        mean_over = mean_entry / 6
        median_over = median_entry / 6
        mode_over = mode_entry / 6

        # Classify batting position
        if median_entry <= 6:
            position_category = "OPENER"
        elif median_entry <= 24:
            position_category = "TOP_ORDER"
        elif median_entry <= 60:
            position_category = "MIDDLE_ORDER"
        else:
            position_category = "LOWER_ORDER"

        results.append(
            {
                "batter_id": batter_id,
                "batter_name": batter_name,
                "innings_count": innings_count,
                "mean_entry_ball": round(mean_entry, 1),
                "median_entry_ball": round(median_entry, 1),
                "mode_entry_ball": mode_entry,
                "mean_entry_over": round(mean_over, 2),
                "median_entry_over": round(median_over, 2),
                "mode_entry_over": round(mode_over, 2),
                "position_category": position_category,
                "min_entry_ball": int(entry_balls.min()),
                "max_entry_ball": int(entry_balls.max()),
            }
        )

    return pd.DataFrame(results)


def get_bowler_over_distribution(conn) -> pd.DataFrame:
    """Calculate when bowlers typically bowl their overs."""

    df = conn.execute(f"""
        WITH bowler_overs AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.bowler_id,
                fb.over,
                MIN(fb.ball_seq) as over_start_ball,
                ROW_NUMBER() OVER (PARTITION BY fb.match_id, fb.innings, fb.bowler_id ORDER BY fb.over) as bowler_over_num
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.is_legal_ball
            GROUP BY fb.match_id, fb.innings, fb.bowler_id, fb.over
        )
        SELECT
            bo.bowler_id,
            dp.current_name as bowler_name,
            bo.match_id,
            bo.innings,
            bo.bowler_over_num,
            bo.over as actual_over,
            bo.over_start_ball
        FROM bowler_overs bo
        JOIN dim_player dp ON bo.bowler_id = dp.player_id
        WHERE bo.bowler_over_num <= 4
        ORDER BY bowler_id, match_id, innings, bowler_over_num
    """).df()

    return df


def calculate_bowler_over_timing(over_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate when bowlers typically bowl their 1st, 2nd, 3rd, 4th overs."""

    results = []

    for bowler_id in over_df["bowler_id"].unique():
        bowler_df = over_df[over_df["bowler_id"] == bowler_id]
        bowler_name = bowler_df["bowler_name"].iloc[0]

        # Get matches with this bowler
        matches = bowler_df[["match_id", "innings"]].drop_duplicates()
        match_count = len(matches)

        if match_count < MIN_INNINGS:
            continue

        # Calculate stats for each of their first 4 overs
        over_stats = {}
        for over_num in [1, 2, 3, 4]:
            over_data = bowler_df[bowler_df["bowler_over_num"] == over_num]["actual_over"].values

            if len(over_data) > 0:
                median_over = int(np.median(over_data))
                mode_over = Counter(over_data).most_common(1)[0][0]
                over_stats[f"over{over_num}_median"] = median_over
                over_stats[f"over{over_num}_mode"] = mode_over
                over_stats[f"over{over_num}_count"] = len(over_data)
            else:
                over_stats[f"over{over_num}_median"] = None
                over_stats[f"over{over_num}_mode"] = None
                over_stats[f"over{over_num}_count"] = 0

        # Classify bowling role based on when they bowl
        # Fixed: Handle 0 values properly (0 is falsy in Python!)
        first_over_median = over_stats.get("over1_median")
        fourth_over_median = over_stats.get("over4_median")

        # Determine primary role based on first over timing
        # PP = overs 0-5, Middle = overs 6-15, Death = overs 16-19
        role_categories = []

        if first_over_median is not None and first_over_median <= 5:
            role_categories.append("POWERPLAY_BOWLER")

        if fourth_over_median is not None and fourth_over_median >= 16:
            role_categories.append("DEATH_BOWLER")

        # If bowls both PP and death (like Malinga, Bumrah), mark as dual-phase
        if len(role_categories) == 2:
            role_category = "PP_AND_DEATH_SPECIALIST"
        elif len(role_categories) == 1:
            role_category = role_categories[0]
        else:
            role_category = "MIDDLE_OVERS_BOWLER"

        results.append(
            {
                "bowler_id": bowler_id,
                "bowler_name": bowler_name,
                "match_count": match_count,
                **over_stats,
                "role_category": role_category,
            }
        )

    return pd.DataFrame(results)


def print_batter_analysis(df: pd.DataFrame):
    """Print batter entry point analysis."""

    print("\n" + "=" * 70)
    print("BATTER ENTRY POINT ANALYSIS")
    print("=" * 70)

    print(f"\n  Batters analyzed: {len(df)}")

    # By position category
    for cat in ["OPENER", "TOP_ORDER", "MIDDLE_ORDER", "LOWER_ORDER"]:
        count = len(df[df["position_category"] == cat])
        print(f"  {cat}: {count}")

    # Top openers (lowest entry)
    print("\n  OPENERS (median entry ≤ ball 6):")
    openers = df[df["position_category"] == "OPENER"].nsmallest(10, "median_entry_ball")
    for _, row in openers.iterrows():
        print(
            f"    {row['batter_name']}: median ball {row['median_entry_ball']:.0f} ({row['innings_count']} innings)"
        )

    # Typical finishers (highest entry)
    print("\n  FINISHERS (median entry > ball 60):")
    finishers = df[df["position_category"] == "LOWER_ORDER"].nlargest(10, "median_entry_ball")
    for _, row in finishers.iterrows():
        print(
            f"    {row['batter_name']}: median ball {row['median_entry_ball']:.0f} ({row['innings_count']} innings)"
        )


def print_bowler_analysis(df: pd.DataFrame):
    """Print bowler over timing analysis."""

    print("\n" + "=" * 70)
    print("BOWLER OVER TIMING ANALYSIS")
    print("=" * 70)

    print(f"\n  Bowlers analyzed: {len(df)}")

    # By role category
    for cat in [
        "POWERPLAY_BOWLER",
        "MIDDLE_OVERS_BOWLER",
        "DEATH_BOWLER",
        "PP_AND_DEATH_SPECIALIST",
    ]:
        count = len(df[df["role_category"] == cat])
        print(f"  {cat}: {count}")

    # Powerplay specialists
    print("\n  POWERPLAY BOWLERS (1st over typically in PP):")
    pp_bowlers = df[df["role_category"] == "POWERPLAY_BOWLER"].head(10)
    for _, row in pp_bowlers.iterrows():
        o1 = row.get("over1_median", "N/A")
        print(
            f"    {row['bowler_name']}: 1st over typically over {o1} ({row['match_count']} matches)"
        )

    # Death specialists
    print("\n  DEATH BOWLERS (4th over typically at death):")
    death_bowlers = df[df["role_category"] == "DEATH_BOWLER"].head(10)
    for _, row in death_bowlers.iterrows():
        o4 = row.get("over4_median", "N/A")
        print(
            f"    {row['bowler_name']}: 4th over typically over {o4} ({row['match_count']} matches)"
        )

    # Dual-phase specialists (PP + Death)
    print("\n  PP AND DEATH SPECIALISTS (bowl both phases):")
    dual_bowlers = df[df["role_category"] == "PP_AND_DEATH_SPECIALIST"].head(10)
    for _, row in dual_bowlers.iterrows():
        o1 = row.get("over1_median", "N/A")
        o4 = row.get("over4_median", "N/A")
        print(
            f"    {row['bowler_name']}: 1st over={o1}, 4th over={o4} ({row['match_count']} matches)"
        )


def save_data(batter_df: pd.DataFrame, bowler_df: pd.DataFrame):
    """Save entry point data to CSV."""

    batter_path = OUTPUT_DIR / "batter_entry_points.csv"
    batter_df.to_csv(batter_path, index=False)
    print(f"\n  Batter entry points saved to: {batter_path}")

    bowler_path = OUTPUT_DIR / "bowler_over_timing.csv"
    bowler_df.to_csv(bowler_path, index=False)
    print(f"  Bowler over timing saved to: {bowler_path}")


def main():
    print("=" * 70)
    print("Cricket Playbook - Entry Point Analysis")
    print("Author: Stephen Curry | Sprint 2.9 - Entry Point Bug Fix")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Batter entry points
    print("\n1. Extracting batter entry points...")
    batter_entry_df = get_batter_entry_points(conn)
    print(f"   Records: {len(batter_entry_df)}")

    print("\n2. Calculating batter entry statistics...")
    batter_stats_df = calculate_batter_entry_stats(batter_entry_df)
    print(f"   Batters: {len(batter_stats_df)}")

    # Bowler over timing
    print("\n3. Extracting bowler over distribution...")
    bowler_over_df = get_bowler_over_distribution(conn)
    print(f"   Records: {len(bowler_over_df)}")

    print("\n4. Calculating bowler over timing...")
    bowler_stats_df = calculate_bowler_over_timing(bowler_over_df)
    print(f"   Bowlers: {len(bowler_stats_df)}")

    # Print analysis
    print_batter_analysis(batter_stats_df)
    print_bowler_analysis(bowler_stats_df)

    # Save data
    print("\n5. Saving results...")
    save_data(batter_stats_df, bowler_stats_df)

    conn.close()

    print("\n" + "=" * 70)
    print("ENTRY POINT ANALYSIS COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
