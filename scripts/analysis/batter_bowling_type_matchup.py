#!/usr/bin/env python3
"""
Cricket Playbook - Batter vs Bowling Type Matchup Analysis
Author: Stephen Curry (Analytics Lead)
Sprint: 2.9 - Missing Matchup Data Fix

Analyzes batter performance against different bowling types and generates matchup tags.

Bug Fix (Sprint 2.9):
- Previous: Joined on ipl_2026_squads (only current squad bowlers, missing historical data)
- Previous: Used wrong bowling types ("Fast"/"Medium" vs actual "Right-arm pace"/"Left-arm pace")
- Now: Uses dim_bowler_classification for ALL historical bowlers
- Now: Uses correct bowling style names from the database

Tags Generated:
- SPECIALIST_VS_PACE: SR ≥130 vs pace bowling
- SPECIALIST_VS_SPIN: SR ≥130 vs spin bowling
- SPECIALIST_VS_LEFT_ARM_SPIN: SR ≥130 vs left-arm orthodox
- SPECIALIST_VS_OFF_SPIN: SR ≥130 vs off-spin
- SPECIALIST_VS_LEG_SPIN: SR ≥130 vs leg-spin
- VULNERABLE_VS_PACE: SR <105 vs pace bowling
- VULNERABLE_VS_SPIN: SR <105 vs spin bowling
- VULNERABLE_VS_LEFT_ARM_SPIN: SR <105 vs left-arm orthodox
- VULNERABLE_VS_OFF_SPIN: SR <105 vs off-spin
- VULNERABLE_VS_LEG_SPIN: SR <105 vs leg-spin

Performance Optimization (TKT-099):
- Replaced iterative DataFrame filtering with groupby operations
- Reduced O(n*m) complexity to O(n) in aggregate_by_pace_spin function
"""

import duckdb
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

from utils.player_tags import update_player_tags
from utils.logging_config import setup_logger
from config import config

# Initialize logger
logger = setup_logger(__name__)

PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = config.DB_PATH
OUTPUT_DIR = config.OUTPUT_DIR

# Data filter - only use recent IPL seasons (2023 onwards)
IPL_MIN_DATE = config.IPL_MIN_DATE

# Minimum balls faced to consider for analysis
MIN_BALLS_VS_TYPE = config.MIN_BALLS_VS_TYPE

# Thresholds for tags
# Updated Sprint 2.9: Better balance between SR and dismissal rate
#
# SPECIALIST criteria (ALL must be true):
#   - SR >= 130 (scores fast - 7.8+ runs/over)
#   - avg >= 20 (quality runs, not just slogging)
#   - bpd >= 15 (doesn't get out too often - survives 2.5+ overs per dismissal)
#
# VULNERABLE criteria (ANY can be true):
#   - SR < 110 (scores slowly - below 6.6 runs/over)
#   - avg < 12 (poor quality)
#   - bpd < 12 with 3+ dismissals (gets out every 2 overs - too risky)
#
SPECIALIST_SR_THRESHOLD = config.SPECIALIST_SR_THRESHOLD
SPECIALIST_AVG_THRESHOLD = config.SPECIALIST_AVG_THRESHOLD
SPECIALIST_BPD_THRESHOLD = config.SPECIALIST_BPD_THRESHOLD

VULNERABLE_SR_THRESHOLD = config.VULNERABLE_SR_THRESHOLD
VULNERABLE_AVG_THRESHOLD = config.VULNERABLE_AVG_THRESHOLD
VULNERABLE_BPD_THRESHOLD = config.VULNERABLE_BPD_THRESHOLD

# Bowling type categories (must match dim_bowler_classification.bowling_style values)
PACE_TYPES = ["Right-arm pace", "Left-arm pace"]
SPIN_TYPES = [
    "Right-arm off-spin",
    "Right-arm leg-spin",
    "Left-arm orthodox",
    "Left-arm wrist spin",
]


def get_batter_vs_bowling_type(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Get batter performance split by bowling type.

    Uses the pre-computed analytics_ipl_batter_vs_bowler_type table which has
    comprehensive bowler type classification for all historical bowlers.

    Note: No threshold applied here - we get ALL data so we can aggregate
    pace/spin totals first, then apply thresholds to the aggregated values.
    """

    df = conn.execute(
        """
        SELECT
            batter_id,
            batter_name,
            bowler_type as bowling_type,
            balls,
            runs,
            dismissals,
            fours,
            sixes,
            dot_balls as dots,
            strike_rate,
            average,
            dot_ball_pct as dot_pct,
            boundary_pct
        FROM analytics_ipl_batter_vs_bowler_type
        WHERE bowler_type != 'Unknown'
        ORDER BY batter_name, bowler_type
    """
    ).df()

    return df


def aggregate_by_pace_spin(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate stats into Pace vs Spin categories.

    Sums ALL bowling types (including those below individual thresholds)
    to get complete pace/spin totals, then filters at the end.

    Performance Optimization (TKT-099):
    - Changed from O(n*m) to O(n) complexity using pandas groupby
    - Previous: Filtered full DataFrame for each unique batter_id
    - Now: Single pass groupby operation, then filter within pre-grouped data
    """

    results = []

    # TKT-099: Use groupby instead of repeated DataFrame filtering
    # This reduces complexity from O(n*m) to O(n) where n=rows, m=unique batters
    grouped = df.groupby("batter_id")

    for batter_id, batter_df in grouped:
        batter_name = batter_df["batter_name"].iloc[0]

        # Pace stats - sum ALL pace bowling types
        pace_df = batter_df[batter_df["bowling_type"].isin(PACE_TYPES)]
        if len(pace_df) > 0:
            pace_balls = int(pace_df["balls"].sum())
            pace_runs = pace_df["runs"].sum()
            pace_dismissals = pace_df["dismissals"].sum()
            pace_sr = round(pace_runs * 100 / pace_balls, 2) if pace_balls > 0 else 0
            pace_avg = round(pace_runs / pace_dismissals, 2) if pace_dismissals > 0 else None
        else:
            pace_balls, pace_runs, pace_dismissals, pace_sr, pace_avg = 0, 0, 0, 0, None

        # Spin stats - sum ALL spin bowling types
        spin_df = batter_df[batter_df["bowling_type"].isin(SPIN_TYPES)]
        if len(spin_df) > 0:
            spin_balls = int(spin_df["balls"].sum())
            spin_runs = spin_df["runs"].sum()
            spin_dismissals = spin_df["dismissals"].sum()
            spin_sr = round(spin_runs * 100 / spin_balls, 2) if spin_balls > 0 else 0
            spin_avg = round(spin_runs / spin_dismissals, 2) if spin_dismissals > 0 else None
        else:
            spin_balls, spin_runs, spin_dismissals, spin_sr, spin_avg = 0, 0, 0, 0, None

        # Only include batters with sufficient sample size in EITHER category
        if pace_balls >= MIN_BALLS_VS_TYPE or spin_balls >= MIN_BALLS_VS_TYPE:
            results.append(
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

    return pd.DataFrame(results)


def assign_matchup_tags(raw_df: pd.DataFrame, pace_spin_df: pd.DataFrame) -> pd.DataFrame:
    """Assign batting matchup tags based on performance vs bowling types."""

    tags_dict = {}

    for _, row in pace_spin_df.iterrows():
        batter_id = row["batter_id"]
        player_tags = []

        # Pace tags - check SR, average, AND balls per dismissal
        if row["pace_balls"] >= MIN_BALLS_VS_TYPE:
            pace_sr = row["pace_sr"] or 0
            pace_avg = row["pace_avg"]
            pace_dismissals = row["pace_dismissals"] or 0
            pace_bpd = row["pace_balls"] / pace_dismissals if pace_dismissals > 0 else 999

            # SPECIALIST: High SR + decent average + doesn't get out too often
            is_pace_specialist = (
                pace_sr >= SPECIALIST_SR_THRESHOLD
                and (pace_avg is None or pace_avg >= SPECIALIST_AVG_THRESHOLD)
                and pace_bpd >= SPECIALIST_BPD_THRESHOLD
            )

            # VULNERABLE: Low SR OR poor average OR gets out too often
            is_pace_vulnerable = (
                pace_sr < VULNERABLE_SR_THRESHOLD
                or (pace_avg is not None and pace_avg < VULNERABLE_AVG_THRESHOLD)
                or (pace_dismissals >= 3 and pace_bpd < VULNERABLE_BPD_THRESHOLD)
            )

            if is_pace_specialist:
                player_tags.append("SPECIALIST_VS_PACE")
            elif is_pace_vulnerable:
                player_tags.append("VULNERABLE_VS_PACE")

        # Spin tags - check SR, average, AND balls per dismissal
        if row["spin_balls"] >= MIN_BALLS_VS_TYPE:
            spin_sr = row["spin_sr"] or 0
            spin_avg = row["spin_avg"]
            spin_dismissals = row["spin_dismissals"] or 0
            spin_bpd = row["spin_balls"] / spin_dismissals if spin_dismissals > 0 else 999

            # SPECIALIST: High SR + decent average + doesn't get out too often
            is_spin_specialist = (
                spin_sr >= SPECIALIST_SR_THRESHOLD
                and (spin_avg is None or spin_avg >= SPECIALIST_AVG_THRESHOLD)
                and spin_bpd >= SPECIALIST_BPD_THRESHOLD
            )

            # VULNERABLE: Low SR OR poor average OR gets out too often
            is_spin_vulnerable = (
                spin_sr < VULNERABLE_SR_THRESHOLD
                or (spin_avg is not None and spin_avg < VULNERABLE_AVG_THRESHOLD)
                or (spin_dismissals >= 3 and spin_bpd < VULNERABLE_BPD_THRESHOLD)
            )

            if is_spin_specialist:
                player_tags.append("SPECIALIST_VS_SPIN")
            elif is_spin_vulnerable:
                player_tags.append("VULNERABLE_VS_SPIN")

        tags_dict[batter_id] = player_tags

    # Now add specific bowling type tags
    # Updated per Founder Review #3: Include average (quality) not just SR (quantity)
    for _, row in raw_df.iterrows():
        batter_id = row["batter_id"]
        bowling_type = row["bowling_type"]
        sr = row["strike_rate"] or 0
        avg = row["average"]  # runs per dismissal
        balls = row["balls"]
        dismissals = row["dismissals"]

        # Calculate balls per dismissal
        bpd = balls / dismissals if dismissals > 0 else 999

        if batter_id not in tags_dict:
            tags_dict[batter_id] = []

        # Map bowling type to tag suffix (uses dim_bowler_classification values)
        type_map = {
            "Right-arm off-spin": "OFF_SPIN",
            "Right-arm leg-spin": "LEG_SPIN",
            "Left-arm orthodox": "LEFT_ARM_SPIN",
            "Left-arm wrist spin": "LEFT_ARM_WRIST_SPIN",
        }

        if bowling_type in type_map:
            suffix = type_map[bowling_type]

            # SPECIALIST: Good SR AND good average AND doesn't get out often
            # Example: Markram has SR 130 but avg 18 and bpd 13.75 - NOT a specialist
            is_specialist = (
                sr >= SPECIALIST_SR_THRESHOLD
                and (avg is None or avg >= SPECIALIST_AVG_THRESHOLD)
                and bpd >= SPECIALIST_BPD_THRESHOLD
            )

            # VULNERABLE: Poor SR OR poor average OR gets out too often
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

    # Convert to DataFrame
    result_df = pace_spin_df.copy()
    result_df["bowling_type_tags"] = result_df["batter_id"].map(tags_dict)

    return result_df


def log_analysis(df: pd.DataFrame, raw_df: pd.DataFrame) -> None:
    """Log summary analysis using logger."""

    logger.info("=" * 70)
    logger.info("BATTER VS BOWLING TYPE MATCHUP ANALYSIS")
    logger.info("=" * 70)

    logger.info("Batters with sufficient data: %d", len(df))

    # Count tags
    pace_specialists = df[
        df["bowling_type_tags"].apply(lambda x: "SPECIALIST_VS_PACE" in x if x else False)
    ]
    spin_specialists = df[
        df["bowling_type_tags"].apply(lambda x: "SPECIALIST_VS_SPIN" in x if x else False)
    ]
    pace_vulnerable = df[
        df["bowling_type_tags"].apply(lambda x: "VULNERABLE_VS_PACE" in x if x else False)
    ]
    spin_vulnerable = df[
        df["bowling_type_tags"].apply(lambda x: "VULNERABLE_VS_SPIN" in x if x else False)
    ]

    logger.info("SPECIALIST_VS_PACE (SR >=%d): %d", SPECIALIST_SR_THRESHOLD, len(pace_specialists))
    logger.info("SPECIALIST_VS_SPIN (SR >=%d): %d", SPECIALIST_SR_THRESHOLD, len(spin_specialists))
    logger.info("VULNERABLE_VS_PACE (SR <%d): %d", VULNERABLE_SR_THRESHOLD, len(pace_vulnerable))
    logger.info("VULNERABLE_VS_SPIN (SR <%d): %d", VULNERABLE_SR_THRESHOLD, len(spin_vulnerable))

    # Specific type tags
    for tag_type in ["OFF_SPIN", "LEG_SPIN", "LEFT_ARM_SPIN"]:
        spec_tag = f"SPECIALIST_VS_{tag_type}"
        vuln_tag = f"VULNERABLE_VS_{tag_type}"
        spec_count = len(df[df["bowling_type_tags"].apply(lambda x: spec_tag in x if x else False)])
        vuln_count = len(df[df["bowling_type_tags"].apply(lambda x: vuln_tag in x if x else False)])
        logger.info("  %s: %d, %s: %d", spec_tag, spec_count, vuln_tag, vuln_count)

    # Top pace specialists
    logger.info("TOP PACE SPECIALISTS:")
    top_pace = df[df["pace_balls"] >= MIN_BALLS_VS_TYPE].nlargest(10, "pace_sr")
    for _, row in top_pace.iterrows():
        logger.debug(
            "  %s: SR %.1f (%d balls)", row["batter_name"], row["pace_sr"], row["pace_balls"]
        )

    # Top spin specialists
    logger.info("TOP SPIN SPECIALISTS:")
    top_spin = df[df["spin_balls"] >= MIN_BALLS_VS_TYPE].nlargest(10, "spin_sr")
    for _, row in top_spin.iterrows():
        logger.debug(
            "  %s: SR %.1f (%d balls)", row["batter_name"], row["spin_sr"], row["spin_balls"]
        )

    # Most vulnerable vs pace
    logger.info("MOST VULNERABLE VS PACE:")
    vuln_pace = df[
        (df["pace_balls"] >= MIN_BALLS_VS_TYPE) & (df["pace_sr"] < VULNERABLE_SR_THRESHOLD)
    ].nsmallest(10, "pace_sr")
    for _, row in vuln_pace.iterrows():
        logger.debug(
            "  %s: SR %.1f (%d balls)", row["batter_name"], row["pace_sr"], row["pace_balls"]
        )

    # Most vulnerable vs spin
    logger.info("MOST VULNERABLE VS SPIN:")
    vuln_spin = df[
        (df["spin_balls"] >= MIN_BALLS_VS_TYPE) & (df["spin_sr"] < VULNERABLE_SR_THRESHOLD)
    ].nsmallest(10, "spin_sr")
    for _, row in vuln_spin.iterrows():
        logger.debug(
            "  %s: SR %.1f (%d balls)", row["batter_name"], row["spin_sr"], row["spin_balls"]
        )


def update_player_tags_json(matchup_df: pd.DataFrame) -> int:
    """Update player_tags.json with bowling type matchup tags.

    TKT-097: Refactored to use shared utils/player_tags.py module.
    """
    # Create lookup for matchup tags
    matchup_lookup = {}
    for _, row in matchup_df.iterrows():
        if row["bowling_type_tags"]:
            matchup_lookup[row["batter_id"]] = row["bowling_type_tags"]

    # Use shared utility to update tags
    updated_count = update_player_tags(
        category="bowling_type",
        new_tags_lookup=matchup_lookup,
        player_type="batters",
    )

    logger.info("Updated %d batters in player_tags.json", updated_count)

    return updated_count


def save_matchup_data(df: pd.DataFrame, raw_df: pd.DataFrame) -> None:
    """Save matchup data to CSV for review."""

    output_path = OUTPUT_DIR / "batter_bowling_type_matchup.csv"

    # Select columns for output
    output_df = df[
        [
            "batter_id",
            "batter_name",
            "pace_balls",
            "pace_sr",
            "pace_avg",
            "pace_dismissals",
            "spin_balls",
            "spin_sr",
            "spin_avg",
            "spin_dismissals",
            "bowling_type_tags",
        ]
    ].copy()

    # Convert tags list to string
    output_df["bowling_type_tags"] = output_df["bowling_type_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )

    output_df.to_csv(output_path, index=False)
    logger.info("Matchup data saved to: %s", output_path)

    # Also save detailed breakdown
    detail_path = OUTPUT_DIR / "batter_bowling_type_detail.csv"
    raw_df.to_csv(detail_path, index=False)
    logger.info("Detailed data saved to: %s", detail_path)


def main() -> int:
    logger.info("=" * 70)
    logger.info("Cricket Playbook - Batter vs Bowling Type Matchup Analysis")
    logger.info("Author: Stephen Curry | Sprint 2.9 - Missing Data Fix")
    logger.info("=" * 70)

    if not DB_PATH.exists():
        logger.error("Database not found at %s", DB_PATH)
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Get batter performance by bowling type
    logger.info("[1/5] Extracting batter vs bowling type data...")
    raw_df = get_batter_vs_bowling_type(conn)
    logger.info("Records: %d", len(raw_df))

    # Aggregate into Pace vs Spin
    logger.info("[2/5] Aggregating Pace vs Spin stats...")
    pace_spin_df = aggregate_by_pace_spin(raw_df)
    logger.info("Batters: %d", len(pace_spin_df))

    # Assign tags
    logger.info("[3/5] Assigning bowling type matchup tags...")
    matchup_df = assign_matchup_tags(raw_df, pace_spin_df)

    # Log analysis
    log_analysis(matchup_df, raw_df)

    # Save data
    logger.info("[4/5] Saving results...")
    save_matchup_data(matchup_df, raw_df)

    # Update player_tags.json
    logger.info("[5/5] Updating player_tags.json...")
    update_player_tags_json(matchup_df)

    conn.close()

    logger.info("=" * 70)
    logger.info("BATTER VS BOWLING TYPE ANALYSIS COMPLETE")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
