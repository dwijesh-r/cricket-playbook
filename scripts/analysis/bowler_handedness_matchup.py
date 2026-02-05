#!/usr/bin/env python3
"""
Cricket Playbook - Bowler vs LHB/RHB Matchup Analysis
Author: Stephen Curry (Analytics Lead)
Sprint: 3.0 - Analytics Tables & Wickets/Ball Ratio (S3.0-08)

Analyzes bowler performance against left-handed vs right-handed batters
and generates matchup tags.

Fixes from Sprint 3.0:
- Uses analytics_ipl_bowler_vs_batter_handedness view (pre-computed)
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
"""

import duckdb
import pandas as pd
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Data filter - only use recent IPL seasons (2023 onwards)
IPL_MIN_DATE = "2023-01-01"

# Minimum balls faced to consider for analysis
MIN_BALLS_VS_HAND = 60  # ~10 overs


def get_bowler_vs_handedness(conn) -> pd.DataFrame:
    """Get bowler performance split by batter handedness.

    Uses the pre-computed analytics_ipl_bowler_vs_batter_handedness view
    which includes wickets_per_ball ratio for better wicket-taker tagging.
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
        FROM analytics_ipl_bowler_vs_batter_handedness
        WHERE balls >= {MIN_BALLS_VS_HAND}
        ORDER BY bowler_name, batting_hand
    """
    ).df()

    return df


def calculate_matchup_differential(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate differential between LHB and RHB performance.

    Uses wickets_per_ball ratio from analytics view for more accurate
    wicket-taker comparisons instead of raw wicket counts.
    """

    # Pivot to get LHB and RHB side by side
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


def print_analysis(df: pd.DataFrame):
    """Print summary analysis."""

    print("\n" + "=" * 70)
    print("BOWLER VS LHB/RHB MATCHUP ANALYSIS")
    print("=" * 70)

    print(f"\n  Bowlers with sufficient data vs both hands: {len(df)}")

    # Count tags
    lhb_specialists = df[df["handedness_tags"].apply(lambda x: "LHB_SPECIALIST" in x)]
    rhb_specialists = df[df["handedness_tags"].apply(lambda x: "RHB_SPECIALIST" in x)]

    lhb_wicket_takers = df[df["handedness_tags"].apply(lambda x: "LHB_WICKET_TAKER" in x)]
    rhb_wicket_takers = df[df["handedness_tags"].apply(lambda x: "RHB_WICKET_TAKER" in x)]

    print(f"\n  LHB Specialists (economy ≥1.0 better vs lefties): {len(lhb_specialists)}")
    print(f"  RHB Specialists (economy ≥1.0 better vs righties): {len(rhb_specialists)}")
    print(f"  LHB Wicket Takers (higher wickets/ball ratio vs lefties): {len(lhb_wicket_takers)}")
    print(f"  RHB Wicket Takers (higher wickets/ball ratio vs righties): {len(rhb_wicket_takers)}")

    # Top LHB specialists
    print("\n  TOP LHB SPECIALISTS (by economy differential):")
    top_lhb = df.nsmallest(10, "economy_diff")
    for _, row in top_lhb.iterrows():
        print(
            f"    {row['bowler_name']}: LHB Eco {row['lhb_economy']:.2f} vs RHB Eco {row['rhb_economy']:.2f} (diff: {row['economy_diff']:.2f})"
        )

    # Top RHB specialists
    print("\n  TOP RHB SPECIALISTS (by economy differential):")
    top_rhb = df.nlargest(10, "economy_diff")
    for _, row in top_rhb.iterrows():
        print(
            f"    {row['bowler_name']}: LHB Eco {row['lhb_economy']:.2f} vs RHB Eco {row['rhb_economy']:.2f} (diff: {row['economy_diff']:.2f})"
        )

    # Top LHB wicket-takers by wickets/ball ratio
    print("\n  TOP LHB WICKET-TAKERS (by wickets/ball ratio):")
    top_lhb_wt = df[df["lhb_wickets_per_ball"] >= 0.03].nlargest(10, "wickets_per_ball_diff")
    for _, row in top_lhb_wt.iterrows():
        lhb_wpb = row.get("lhb_wickets_per_ball", 0) or 0
        rhb_wpb = row.get("rhb_wickets_per_ball", 0) or 0
        wpb_diff = row.get("wickets_per_ball_diff", 0) or 0
        print(
            f"    {row['bowler_name']}: LHB {lhb_wpb:.4f} vs RHB {rhb_wpb:.4f} (diff: {wpb_diff:+.4f})"
        )

    # Top RHB wicket-takers by wickets/ball ratio
    print("\n  TOP RHB WICKET-TAKERS (by wickets/ball ratio):")
    top_rhb_wt = df[df["rhb_wickets_per_ball"] >= 0.03].nsmallest(10, "wickets_per_ball_diff")
    for _, row in top_rhb_wt.iterrows():
        lhb_wpb = row.get("lhb_wickets_per_ball", 0) or 0
        rhb_wpb = row.get("rhb_wickets_per_ball", 0) or 0
        wpb_diff = row.get("wickets_per_ball_diff", 0) or 0
        print(
            f"    {row['bowler_name']}: LHB {lhb_wpb:.4f} vs RHB {rhb_wpb:.4f} (diff: {wpb_diff:+.4f})"
        )

    # Neutral bowlers
    neutral = df[(df["economy_diff"].abs() < 0.5)]
    print(f"\n  Neutral bowlers (diff < 0.5): {len(neutral)}")


def update_player_tags_json(matchup_df: pd.DataFrame):
    """Update player_tags.json with handedness matchup tags."""

    tags_path = OUTPUT_DIR / "player_tags.json"

    if tags_path.exists():
        with open(tags_path) as f:
            tags_data = json.load(f)
    else:
        tags_data = {"batters": [], "bowlers": []}

    # Create lookup for handedness tags
    handedness_lookup = {}
    for _, row in matchup_df.iterrows():
        if row["handedness_tags"]:
            handedness_lookup[row["bowler_id"]] = row["handedness_tags"]

    # Update bowler tags
    updated_count = 0
    for bowler in tags_data.get("bowlers", []):
        player_id = bowler.get("player_id")
        if player_id in handedness_lookup:
            existing_tags = set(bowler.get("tags", []))
            new_tags = set(handedness_lookup[player_id])
            # Remove old handedness tags first
            existing_tags -= {
                "LHB_SPECIALIST",
                "RHB_SPECIALIST",
                "LHB_VULNERABLE",
                "RHB_VULNERABLE",
                "LHB_PRESSURE",
                "RHB_PRESSURE",
                "LHB_WICKET_TAKER",
                "RHB_WICKET_TAKER",
            }
            # Add new ones
            existing_tags.update(new_tags)
            bowler["tags"] = list(existing_tags)
            updated_count += 1

    # Save updated file
    with open(tags_path, "w") as f:
        json.dump(tags_data, f, indent=2)

    print(f"\n  Updated {updated_count} bowlers in player_tags.json")

    return updated_count


def save_matchup_data(df: pd.DataFrame):
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
    print(f"\n  Matchup data saved to: {output_path}")


def main():
    print("=" * 70)
    print("Cricket Playbook - Bowler vs LHB/RHB Matchup Analysis")
    print("Author: Stephen Curry | Sprint 3.0 - Analytics Tables & Wickets/Ball Ratio")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Get bowler performance by batter handedness
    print("\n1. Extracting bowler vs handedness data...")
    raw_df = get_bowler_vs_handedness(conn)
    print(f"   Records: {len(raw_df)}")

    # Calculate differentials
    print("\n2. Calculating matchup differentials...")
    matchup_df = calculate_matchup_differential(raw_df)
    print(f"   Bowlers with data vs both hands: {len(matchup_df)}")

    # Assign tags
    print("\n3. Assigning handedness tags...")
    matchup_df = assign_handedness_tags(matchup_df)

    # Print analysis
    print_analysis(matchup_df)

    # Save data
    print("\n4. Saving results...")
    save_matchup_data(matchup_df)

    # Update player_tags.json
    print("\n5. Updating player_tags.json...")
    update_player_tags_json(matchup_df)

    conn.close()

    print("\n" + "=" * 70)
    print("LHB/RHB MATCHUP ANALYSIS COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
