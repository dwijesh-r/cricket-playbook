#!/usr/bin/env python3
"""
Cricket Playbook - IPL 2026 Squad Experience CSV Generator
Sprint 2.4 - Regenerated after Founder Review #1 fixes

Author: Stephen Curry (Analytics)
Date: 2026-01-21

Generates a CSV with all IPL 2026 squad players and their historical IPL statistics.
Players marked as uncapped will have zeroed stats.
"""

import duckdb
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "ipl_2026_squad_experience.csv"


def generate_experience_csv():
    """Generate the squad experience CSV with corrected data."""

    print("=" * 70)
    print("GENERATING IPL 2026 SQUAD EXPERIENCE CSV")
    print("=" * 70)

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Get all squad players with their info
    squad_df = conn.execute("""
        SELECT
            s.team_name,
            s.player_name,
            s.player_id,
            s.role,
            s.bowling_type,
            s.bowling_style,
            s.batting_hand
        FROM ipl_2026_squads s
        ORDER BY s.team_name, s.player_name
    """).df()

    print(f"  Total players in squad: {len(squad_df)}")

    # Get batting stats for capped players
    batting_stats = conn.execute("""
        SELECT
            player_id,
            innings as ipl_batting_innings,
            balls_faced as ipl_batting_balls,
            runs as ipl_batting_runs,
            strike_rate as ipl_batting_sr
        FROM analytics_ipl_batting_career
    """).df()

    # Get bowling stats for capped players
    bowling_stats = conn.execute("""
        SELECT
            player_id,
            matches_bowled as ipl_bowling_matches,
            balls_bowled as ipl_bowling_balls,
            wickets as ipl_bowling_wickets,
            economy_rate as ipl_bowling_economy
        FROM analytics_ipl_bowling_career
    """).df()

    # Merge squad with batting stats
    result_df = squad_df.merge(batting_stats, on="player_id", how="left")

    # Merge with bowling stats
    result_df = result_df.merge(bowling_stats, on="player_id", how="left")

    # Define stat columns
    stat_columns = [
        "ipl_batting_innings",
        "ipl_batting_balls",
        "ipl_batting_runs",
        "ipl_batting_sr",
        "ipl_bowling_matches",
        "ipl_bowling_balls",
        "ipl_bowling_wickets",
        "ipl_bowling_economy",
    ]

    # Fill NaN with 0 for stats
    result_df[stat_columns] = result_df[stat_columns].fillna(0)

    # Identify uncapped players (no batting innings and no bowling matches)
    result_df["is_uncapped"] = (result_df["ipl_batting_innings"] == 0) & (
        result_df["ipl_bowling_matches"] == 0
    )

    # Select final columns for output
    output_df = result_df[
        [
            "team_name",
            "player_name",
            "player_id",
            "role",
            "bowling_type",
            "bowling_style",
            "batting_hand",
            "is_uncapped",
            "ipl_batting_innings",
            "ipl_batting_balls",
            "ipl_batting_runs",
            "ipl_batting_sr",
            "ipl_bowling_matches",
            "ipl_bowling_balls",
            "ipl_bowling_wickets",
            "ipl_bowling_economy",
        ]
    ]

    # Sort by team and then by batting runs (descending) for better readability
    output_df = output_df.sort_values(["team_name", "ipl_batting_runs"], ascending=[True, False])

    # Save to CSV
    output_df.to_csv(OUTPUT_PATH, index=False)

    print(f"\n  Output saved to: {OUTPUT_PATH}")
    print(f"  Total rows: {len(output_df)}")

    # Print summary by team
    print("\n  Players per team:")
    team_counts = output_df.groupby("team_name").size()
    for team, count in team_counts.items():
        uncapped = output_df[(output_df["team_name"] == team) & output_df["is_uncapped"]].shape[0]
        print(f"    {team}: {count} players ({uncapped} uncapped)")

    # Count uncapped players
    uncapped_count = output_df["is_uncapped"].sum()
    print(f"\n  Total uncapped players (no IPL 2023+ stats): {uncapped_count}")

    conn.close()

    print("\n" + "=" * 70)
    print("CSV GENERATION COMPLETE")
    print("=" * 70)

    return output_df


if __name__ == "__main__":
    generate_experience_csv()
