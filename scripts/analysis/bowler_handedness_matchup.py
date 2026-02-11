#!/usr/bin/env python3
"""
Cricket Playbook - Bowler vs LHB/RHB Matchup Analysis
Author: Stephen Curry (Analytics Lead)
Sprint: 3.0 - Analytics Tables & Wickets/Ball Ratio (S3.0-08)

Analyzes bowler performance against left-handed vs right-handed batters
and generates matchup tags.

Fixes from Sprint 3.0:
- Uses analytics_ipl_bowler_vs_batter_handedness_since2023 view (pre-computed)
- Uses wickets/ball ratio instead of raw wicket count for wicket-taker tags
- Consistent with batter matchup script methodology

Tags Generated:
- LHB_SPECIALIST: Economy vs LHB at least 1.0 better than vs RHB
- RHB_SPECIALIST: Economy vs RHB at least 1.0 better than vs LHB
- LHB_VULNERABLE: Economy vs LHB at least 1.0 worse than vs RHB
- RHB_VULNERABLE: Economy vs RHB at least 1.0 worse than vs LHB
- LHB_WICKET_TAKER: Higher wickets/ball ratio vs LHB (takes wickets more efficiently)
- RHB_WICKET_TAKER: Higher wickets/ball ratio vs RHB (takes wickets more efficiently)
- LHB_PRESSURE / RHB_PRESSURE: Higher dot ball % vs respective hand

Performance Note (TKT-099):
- calculate_matchup_differential uses set_index + .loc for O(1) lookups
- This pattern is already optimized for the LHB/RHB join operation
"""

from pathlib import Path

import duckdb
import pandas as pd

SCRIPT_DIR = Path(__file__).parent

from scripts.utils.logging_config import setup_logger
from scripts.utils.player_tags import update_player_tags
from scripts.config import config

# Initialize logger
logger = setup_logger(__name__)

PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = config.DB_PATH
OUTPUT_DIR = config.OUTPUT_DIR

# Data filter - only use recent IPL seasons (2023 onwards)
IPL_MIN_DATE = config.IPL_MIN_DATE

# Minimum balls faced to consider for analysis
MIN_BALLS_VS_HAND = config.MIN_BALLS_VS_HAND


def get_bowler_vs_handedness(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Get bowler performance split by batter handedness.

    Uses the pre-computed analytics_ipl_bowler_vs_batter_handedness_since2023 view (IPL 2023+)
    which includes wickets_per_ball ratio for better wicket-taker tagging. All-time data
    available via analytics_ipl_bowler_vs_batter_handedness_alltime if historical context needed.
    """

    df = conn.execute(
        f"""
        SELECT
            bowler_id,
            bowler_name,
            batting_hand,
            balls,
            runs,
            wickets,
            dot_balls as dots,
            fours,
            sixes,
            economy,
            strike_rate,
            dot_pct,
            boundary_pct,
            wickets_per_ball,
            sample_size
        FROM analytics_ipl_bowler_vs_batter_handedness_since2023
        WHERE balls >= {MIN_BALLS_VS_HAND}
        ORDER BY bowler_name, batting_hand
    """
    ).df()

    return df


def calculate_matchup_differential(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate differential between LHB and RHB performance.

    Uses wickets_per_ball ratio from analytics view for more accurate
    wicket-taker comparisons instead of raw wicket counts.

    Performance Note (TKT-099):
    - Uses set_index + .loc for O(1) lookups per bowler (already optimized)
    - Alternative groupby approach would not improve this pattern since we need
      to join LHB and RHB rows side-by-side for differential calculation
    """

    # Pivot to get LHB and RHB side by side
    # TKT-099: set_index provides O(1) lookup, avoiding repeated DataFrame filtering
    lhb = df[df["batting_hand"] == "Left-hand"].set_index("bowler_id")
    rhb = df[df["batting_hand"] == "Right-hand"].set_index("bowler_id")

    # Get bowlers who have faced both
    common_bowlers = lhb.index.intersection(rhb.index)

    results = []
    for bowler_id in common_bowlers:
        lhb_row = lhb.loc[bowler_id]
        rhb_row = rhb.loc[bowler_id]

        # Get wickets_per_ball from analytics view (or compute if not available)
        lhb_wpb = lhb_row.get(
            "wickets_per_ball",
            lhb_row["wickets"] / lhb_row["balls"] if lhb_row["balls"] > 0 else 0,
        )
        rhb_wpb = rhb_row.get(
            "wickets_per_ball",
            rhb_row["wickets"] / rhb_row["balls"] if rhb_row["balls"] > 0 else 0,
        )

        results.append(
            {
                "bowler_id": bowler_id,
                "bowler_name": lhb_row["bowler_name"],
                # LHB stats
                "lhb_balls": lhb_row["balls"],
                "lhb_economy": lhb_row["economy"],
                "lhb_strike_rate": lhb_row["strike_rate"],
                "lhb_dot_pct": lhb_row["dot_pct"],
                "lhb_boundary_pct": lhb_row["boundary_pct"],
                "lhb_wickets": lhb_row["wickets"],
                "lhb_wickets_per_ball": lhb_wpb,
                # RHB stats
                "rhb_balls": rhb_row["balls"],
                "rhb_economy": rhb_row["economy"],
                "rhb_strike_rate": rhb_row["strike_rate"],
                "rhb_dot_pct": rhb_row["dot_pct"],
                "rhb_boundary_pct": rhb_row["boundary_pct"],
                "rhb_wickets": rhb_row["wickets"],
                "rhb_wickets_per_ball": rhb_wpb,
                # Differentials (negative = better vs LHB)
                "economy_diff": lhb_row["economy"] - rhb_row["economy"],
                "dot_pct_diff": lhb_row["dot_pct"] - rhb_row["dot_pct"],
                "boundary_pct_diff": lhb_row["boundary_pct"] - rhb_row["boundary_pct"],
                # Strike rate differential (lower SR = takes wickets more often)
                # Negative = better vs LHB (lower SR means quicker wickets)
                "strike_rate_diff": (lhb_row["strike_rate"] or 999)
                - (rhb_row["strike_rate"] or 999),
                # Wickets per ball differential (higher = takes wickets more efficiently)
                # Positive = better vs LHB
                "wickets_per_ball_diff": (lhb_wpb or 0) - (rhb_wpb or 0),
            }
        )

    return pd.DataFrame(results)


def assign_handedness_tags(
    df: pd.DataFrame, economy_threshold: float = 1.0, wpb_threshold: float = 0.02
) -> pd.DataFrame:
    """Assign LHB/RHB matchup tags based on differential.

    Args:
        df: DataFrame with matchup differentials
        economy_threshold: Min economy difference for specialist/vulnerable tags (default 1.0)
        wpb_threshold: Min wickets/ball difference for wicket-taker tags (default 0.02 = 2% more wickets per ball)

    Sprint 3.0 Fix: Uses wickets/ball ratio instead of raw wicket count for wicket-taker tags.
    This is more fair as it normalizes for the number of balls bowled vs each hand.
    """

    tags = []

    for _, row in df.iterrows():
        player_tags = []

        # Economy differential
        eco_diff = row["economy_diff"]

        if eco_diff <= -economy_threshold:
            # Better vs LHB (lower economy)
            player_tags.append("LHB_SPECIALIST")
        elif eco_diff >= economy_threshold:
            # Better vs RHB (lower economy)
            player_tags.append("RHB_SPECIALIST")

        # Also check if vulnerable
        if eco_diff >= economy_threshold:
            player_tags.append("LHB_VULNERABLE")
        elif eco_diff <= -economy_threshold:
            player_tags.append("RHB_VULNERABLE")

        # Wicket-taking tags using wickets/ball ratio (Sprint 3.0 fix)
        # Positive wpb_diff means higher wickets/ball ratio vs LHB
        wpb_diff = row.get("wickets_per_ball_diff", 0) or 0
        lhb_wpb = row.get("lhb_wickets_per_ball", 0) or 0
        rhb_wpb = row.get("rhb_wickets_per_ball", 0) or 0

        # Need meaningful wickets/ball ratio (>= 0.03 = roughly 1 wicket per 33 balls) to qualify
        min_wpb = 0.03
        if wpb_diff >= wpb_threshold and lhb_wpb >= min_wpb:
            # Higher wickets/ball ratio vs LHB (takes wickets more efficiently)
            player_tags.append("LHB_WICKET_TAKER")
        elif wpb_diff <= -wpb_threshold and rhb_wpb >= min_wpb:
            # Higher wickets/ball ratio vs RHB
            player_tags.append("RHB_WICKET_TAKER")

        # Add dot ball differential tags
        dot_diff = row["dot_pct_diff"]
        if dot_diff >= 5:  # 5% more dots vs LHB
            player_tags.append("LHB_PRESSURE")
        elif dot_diff <= -5:  # 5% more dots vs RHB
            player_tags.append("RHB_PRESSURE")

        tags.append(player_tags)

    df["handedness_tags"] = tags
    return df


def log_analysis(df: pd.DataFrame) -> None:
    """Log summary analysis using logger."""

    logger.info("=" * 70)
    logger.info("BOWLER VS LHB/RHB MATCHUP ANALYSIS")
    logger.info("=" * 70)

    logger.info("Bowlers with sufficient data vs both hands: %d", len(df))

    # Count tags
    lhb_specialists = df[df["handedness_tags"].apply(lambda x: "LHB_SPECIALIST" in x)]
    rhb_specialists = df[df["handedness_tags"].apply(lambda x: "RHB_SPECIALIST" in x)]

    lhb_wicket_takers = df[df["handedness_tags"].apply(lambda x: "LHB_WICKET_TAKER" in x)]
    rhb_wicket_takers = df[df["handedness_tags"].apply(lambda x: "RHB_WICKET_TAKER" in x)]

    logger.info("LHB Specialists (economy >=1.0 better vs lefties): %d", len(lhb_specialists))
    logger.info("RHB Specialists (economy >=1.0 better vs righties): %d", len(rhb_specialists))
    logger.info(
        "LHB Wicket Takers (higher wickets/ball ratio vs lefties): %d", len(lhb_wicket_takers)
    )
    logger.info(
        "RHB Wicket Takers (higher wickets/ball ratio vs righties): %d", len(rhb_wicket_takers)
    )

    # Top LHB specialists
    logger.info("TOP LHB SPECIALISTS (by economy differential):")
    top_lhb = df.nsmallest(10, "economy_diff")
    for _, row in top_lhb.iterrows():
        logger.debug(
            "  %s: LHB Eco %.2f vs RHB Eco %.2f (diff: %.2f)",
            row["bowler_name"],
            row["lhb_economy"],
            row["rhb_economy"],
            row["economy_diff"],
        )

    # Top RHB specialists
    logger.info("TOP RHB SPECIALISTS (by economy differential):")
    top_rhb = df.nlargest(10, "economy_diff")
    for _, row in top_rhb.iterrows():
        logger.debug(
            "  %s: LHB Eco %.2f vs RHB Eco %.2f (diff: %.2f)",
            row["bowler_name"],
            row["lhb_economy"],
            row["rhb_economy"],
            row["economy_diff"],
        )

    # Top LHB wicket-takers by wickets/ball ratio
    logger.info("TOP LHB WICKET-TAKERS (by wickets/ball ratio):")
    top_lhb_wt = df[df["lhb_wickets_per_ball"] >= 0.03].nlargest(10, "wickets_per_ball_diff")
    for _, row in top_lhb_wt.iterrows():
        lhb_wpb = row.get("lhb_wickets_per_ball", 0) or 0
        rhb_wpb = row.get("rhb_wickets_per_ball", 0) or 0
        wpb_diff = row.get("wickets_per_ball_diff", 0) or 0
        logger.debug(
            "  %s: LHB %.4f vs RHB %.4f (diff: %+.4f)",
            row["bowler_name"],
            lhb_wpb,
            rhb_wpb,
            wpb_diff,
        )

    # Top RHB wicket-takers by wickets/ball ratio
    logger.info("TOP RHB WICKET-TAKERS (by wickets/ball ratio):")
    top_rhb_wt = df[df["rhb_wickets_per_ball"] >= 0.03].nsmallest(10, "wickets_per_ball_diff")
    for _, row in top_rhb_wt.iterrows():
        lhb_wpb = row.get("lhb_wickets_per_ball", 0) or 0
        rhb_wpb = row.get("rhb_wickets_per_ball", 0) or 0
        wpb_diff = row.get("wickets_per_ball_diff", 0) or 0
        logger.debug(
            "  %s: LHB %.4f vs RHB %.4f (diff: %+.4f)",
            row["bowler_name"],
            lhb_wpb,
            rhb_wpb,
            wpb_diff,
        )

    # Neutral bowlers
    neutral = df[(df["economy_diff"].abs() < 0.5)]
    logger.info("Neutral bowlers (diff < 0.5): %d", len(neutral))


def update_player_tags_json(matchup_df: pd.DataFrame) -> int:
    """Update player_tags.json with handedness matchup tags.

    TKT-097: Refactored to use shared utils/player_tags.py module.
    """
    # Create lookup for handedness tags
    handedness_lookup = {}
    for _, row in matchup_df.iterrows():
        if row["handedness_tags"]:
            handedness_lookup[row["bowler_id"]] = row["handedness_tags"]

    # Use shared utility to update tags
    updated_count = update_player_tags(
        category="handedness",
        new_tags_lookup=handedness_lookup,
        player_type="bowlers",
    )

    logger.info("Updated %d bowlers in player_tags.json", updated_count)

    return updated_count


def save_matchup_data(df: pd.DataFrame) -> None:
    """Save matchup data to CSV for review."""

    output_path = OUTPUT_DIR / "bowler_handedness_matchup.csv"

    # Select columns for output (including new wickets_per_ball columns)
    output_df = df[
        [
            "bowler_id",
            "bowler_name",
            "lhb_balls",
            "lhb_economy",
            "lhb_strike_rate",
            "lhb_wickets",
            "lhb_wickets_per_ball",
            "rhb_balls",
            "rhb_economy",
            "rhb_strike_rate",
            "rhb_wickets",
            "rhb_wickets_per_ball",
            "economy_diff",
            "wickets_per_ball_diff",
            "handedness_tags",
        ]
    ].copy()

    # Convert tags list to string
    output_df["handedness_tags"] = output_df["handedness_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )

    output_df.to_csv(output_path, index=False)
    logger.info("Matchup data saved to: %s", output_path)


def main() -> int:
    logger.info("=" * 70)
    logger.info("Cricket Playbook - Bowler vs LHB/RHB Matchup Analysis")
    logger.info("Author: Stephen Curry | Sprint 3.0 - Analytics Tables & Wickets/Ball Ratio")
    logger.info("=" * 70)

    if not DB_PATH.exists():
        logger.error("Database not found at %s", DB_PATH)
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Get bowler performance by batter handedness
    logger.info("[1/5] Extracting bowler vs handedness data...")
    raw_df = get_bowler_vs_handedness(conn)
    logger.info("Records: %d", len(raw_df))

    # Calculate differentials
    logger.info("[2/5] Calculating matchup differentials...")
    matchup_df = calculate_matchup_differential(raw_df)
    logger.info("Bowlers with data vs both hands: %d", len(matchup_df))

    # Assign tags
    logger.info("[3/5] Assigning handedness tags...")
    matchup_df = assign_handedness_tags(matchup_df)

    # Log analysis
    log_analysis(matchup_df)

    # Save data
    logger.info("[4/5] Saving results...")
    save_matchup_data(matchup_df)

    # Update player_tags.json
    logger.info("[5/5] Updating player_tags.json...")
    update_player_tags_json(matchup_df)

    conn.close()

    logger.info("=" * 70)
    logger.info("LHB/RHB MATCHUP ANALYSIS COMPLETE")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
