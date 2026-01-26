#!/usr/bin/env python3
"""
Cricket Playbook - Bowler Phase Performance Tags
Author: Stephen Curry (Analytics Lead)
Sprint: 2.7 - Founder Review #3

Generates phase-wise performance tags for bowlers:
- PP_BEAST / PP_LIABILITY (Powerplay economy)
- MIDDLE_OVERS_BEAST / MIDDLE_OVERS_LIABILITY
- DEATH_BEAST / DEATH_LIABILITY
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
# This accounts for drift in stats due to evolution of the game
IPL_MIN_DATE = "2023-01-01"  # IPL 2023, 2024, 2025

# Minimum overs to qualify for phase tags
MIN_PP_OVERS = 30
MIN_MIDDLE_OVERS = 50
MIN_DEATH_OVERS = 30

# Thresholds for tags
# Note: Thresholds should be based on percentiles, not arbitrary values
# Death overs median economy is ~10.8, 75th percentile is ~11.5
PP_BEAST_ECO = 7.0
PP_LIABILITY_ECO = 9.5
MIDDLE_BEAST_ECO = 7.0
MIDDLE_LIABILITY_ECO = 8.5
DEATH_BEAST_ECO = 9.0  # Raised from 8.5 (was too strict)
DEATH_LIABILITY_ECO = 12.0  # Raised from 10.5 (was below median, too harsh)

# Strike rate thresholds (balls per wicket) - higher = worse
# Median death SR is ~12.3, 75th percentile is ~15.0
DEATH_LIABILITY_SR = 18.0  # Only liability if ALSO poor strike rate


def get_bowler_phase_stats(conn) -> pd.DataFrame:
    """Get bowler performance by match phase."""

    df = conn.execute(f"""
        SELECT
            fb.bowler_id,
            dp.current_name as bowler_name,
            fb.match_phase,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
            SUM(fb.batter_runs + fb.extra_runs) as runs,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dots,
            ROUND(balls / 6.0, 1) as overs,
            ROUND(runs * 6.0 / NULLIF(balls, 0), 2) as economy,
            ROUND(balls * 1.0 / NULLIF(wickets, 0), 2) as strike_rate,
            ROUND(dots * 100.0 / NULLIF(balls, 0), 2) as dot_pct
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
          AND fb.match_phase IS NOT NULL
        GROUP BY fb.bowler_id, dp.current_name, fb.match_phase
        ORDER BY bowler_name, match_phase
    """).df()

    return df


def pivot_phase_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot phase stats to have one row per bowler."""

    results = []

    for bowler_id in df["bowler_id"].unique():
        bowler_df = df[df["bowler_id"] == bowler_id]
        bowler_name = bowler_df["bowler_name"].iloc[0]

        row = {
            "bowler_id": bowler_id,
            "bowler_name": bowler_name,
        }

        for phase in ["powerplay", "middle", "death"]:
            phase_df = bowler_df[bowler_df["match_phase"] == phase]
            if len(phase_df) > 0:
                row[f"{phase}_overs"] = phase_df["overs"].iloc[0]
                row[f"{phase}_economy"] = phase_df["economy"].iloc[0]
                row[f"{phase}_wickets"] = phase_df["wickets"].iloc[0]
                row[f"{phase}_dot_pct"] = phase_df["dot_pct"].iloc[0]
            else:
                row[f"{phase}_overs"] = 0
                row[f"{phase}_economy"] = None
                row[f"{phase}_wickets"] = 0
                row[f"{phase}_dot_pct"] = None

        results.append(row)

    return pd.DataFrame(results)


def assign_phase_tags(df: pd.DataFrame) -> pd.DataFrame:
    """Assign phase performance tags based on economy and strike rate.

    DEATH_LIABILITY requires BOTH high economy AND poor strike rate.
    A bowler who is expensive but takes wickets is aggressive, not a liability.
    """

    tags = []

    for _, row in df.iterrows():
        player_tags = []

        # Powerplay tags
        if row["powerplay_overs"] and row["powerplay_overs"] >= MIN_PP_OVERS:
            eco = row["powerplay_economy"]
            if eco and eco <= PP_BEAST_ECO:
                player_tags.append("PP_BEAST")
            elif eco and eco >= PP_LIABILITY_ECO:
                player_tags.append("PP_LIABILITY")

        # Middle overs tags
        if row["middle_overs"] and row["middle_overs"] >= MIN_MIDDLE_OVERS:
            eco = row["middle_economy"]
            if eco and eco <= MIDDLE_BEAST_ECO:
                player_tags.append("MIDDLE_OVERS_BEAST")
            elif eco and eco >= MIDDLE_LIABILITY_ECO:
                player_tags.append("MIDDLE_OVERS_LIABILITY")

        # Death overs tags - requires BOTH high economy AND poor strike rate
        if row["death_overs"] and row["death_overs"] >= MIN_DEATH_OVERS:
            eco = row["death_economy"]
            wickets = row.get("death_wickets", 0) or 0
            balls = row["death_overs"] * 6 if row["death_overs"] else 0
            death_sr = balls / wickets if wickets > 0 else 999

            if eco and eco <= DEATH_BEAST_ECO:
                player_tags.append("DEATH_BEAST")
            elif eco and eco >= DEATH_LIABILITY_ECO and death_sr >= DEATH_LIABILITY_SR:
                # Only tag as liability if BOTH expensive AND poor wicket-taker
                player_tags.append("DEATH_LIABILITY")

        tags.append(player_tags)

    df["phase_tags"] = tags
    return df


def print_analysis(df: pd.DataFrame):
    """Print summary analysis."""

    print("\n" + "=" * 70)
    print("BOWLER PHASE PERFORMANCE TAGS")
    print("=" * 70)

    # Count tags
    tag_counts = {}
    for tags_list in df["phase_tags"]:
        for tag in tags_list:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print("\n  Tag Distribution:")
    for tag in [
        "PP_BEAST",
        "PP_LIABILITY",
        "MIDDLE_OVERS_BEAST",
        "MIDDLE_OVERS_LIABILITY",
        "DEATH_BEAST",
        "DEATH_LIABILITY",
    ]:
        count = tag_counts.get(tag, 0)
        print(f"    {tag}: {count}")

    # Top PP beasts
    print("\n  TOP POWERPLAY BEASTS:")
    pp_beasts = df[df["phase_tags"].apply(lambda x: "PP_BEAST" in x)].nsmallest(
        10, "powerplay_economy"
    )
    for _, row in pp_beasts.iterrows():
        print(
            f"    {row['bowler_name']}: PP Eco {row['powerplay_economy']:.2f} ({row['powerplay_overs']:.0f} overs)"
        )

    # Top death beasts
    print("\n  TOP DEATH BEASTS:")
    death_beasts = df[df["phase_tags"].apply(lambda x: "DEATH_BEAST" in x)].nsmallest(
        10, "death_economy"
    )
    for _, row in death_beasts.iterrows():
        print(
            f"    {row['bowler_name']}: Death Eco {row['death_economy']:.2f} ({row['death_overs']:.0f} overs)"
        )

    # Death liabilities
    print("\n  DEATH LIABILITIES:")
    death_liab = df[df["phase_tags"].apply(lambda x: "DEATH_LIABILITY" in x)].nlargest(
        10, "death_economy"
    )
    for _, row in death_liab.iterrows():
        print(
            f"    {row['bowler_name']}: Death Eco {row['death_economy']:.2f} ({row['death_overs']:.0f} overs)"
        )


def update_player_tags_json(phase_df: pd.DataFrame):
    """Update player_tags.json with phase performance tags."""

    tags_path = OUTPUT_DIR / "player_tags.json"

    if tags_path.exists():
        with open(tags_path) as f:
            tags_data = json.load(f)
    else:
        tags_data = {"batters": [], "bowlers": []}

    # Create lookup for phase tags
    phase_lookup = {}
    for _, row in phase_df.iterrows():
        if row["phase_tags"]:
            phase_lookup[row["bowler_id"]] = row["phase_tags"]

    # All phase tags to remove before updating
    phase_tags_set = {
        "PP_BEAST",
        "PP_LIABILITY",
        "MIDDLE_OVERS_BEAST",
        "MIDDLE_OVERS_LIABILITY",
        "DEATH_BEAST",
        "DEATH_LIABILITY",
    }

    # Update bowler tags
    updated_count = 0
    for bowler in tags_data.get("bowlers", []):
        player_id = bowler.get("player_id")
        if player_id in phase_lookup:
            existing_tags = set(bowler.get("tags", []))
            new_tags = set(phase_lookup[player_id])
            # Remove old phase tags first
            existing_tags -= phase_tags_set
            # Add new ones
            existing_tags.update(new_tags)
            bowler["tags"] = list(existing_tags)
            updated_count += 1

    # Save updated file
    with open(tags_path, "w") as f:
        json.dump(tags_data, f, indent=2)

    print(f"\n  Updated {updated_count} bowlers in player_tags.json")

    return updated_count


def save_data(df: pd.DataFrame):
    """Save phase data to CSV."""

    output_path = OUTPUT_DIR / "bowler_phase_performance.csv"

    output_df = df[
        [
            "bowler_id",
            "bowler_name",
            "powerplay_overs",
            "powerplay_economy",
            "powerplay_wickets",
            "middle_overs",
            "middle_economy",
            "middle_wickets",
            "death_overs",
            "death_economy",
            "death_wickets",
            "phase_tags",
        ]
    ].copy()

    output_df["phase_tags"] = output_df["phase_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )
    output_df.to_csv(output_path, index=False)
    print(f"\n  Phase data saved to: {output_path}")


def main():
    print("=" * 70)
    print("Cricket Playbook - Bowler Phase Performance Tags")
    print("Author: Stephen Curry | Sprint 2.7")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Get bowler phase stats
    print("\n1. Extracting bowler phase performance...")
    raw_df = get_bowler_phase_stats(conn)
    print(f"   Records: {len(raw_df)}")

    # Pivot to one row per bowler
    print("\n2. Pivoting phase stats...")
    pivot_df = pivot_phase_stats(raw_df)
    print(f"   Bowlers: {len(pivot_df)}")

    # Assign tags
    print("\n3. Assigning phase tags...")
    tagged_df = assign_phase_tags(pivot_df)

    # Print analysis
    print_analysis(tagged_df)

    # Save data
    print("\n4. Saving results...")
    save_data(tagged_df)

    # Update player_tags.json
    print("\n5. Updating player_tags.json...")
    update_player_tags_json(tagged_df)

    conn.close()

    print("\n" + "=" * 70)
    print("BOWLER PHASE TAGS COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
