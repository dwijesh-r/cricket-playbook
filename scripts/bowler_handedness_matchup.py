#!/usr/bin/env python3
"""
Cricket Playbook - Bowler vs LHB/RHB Matchup Analysis
Author: Stephen Curry (Analytics Lead)
Sprint: 2.6 - Enhanced with Wickets & Strike Rate (Founder Review #2)

Analyzes bowler performance against left-handed vs right-handed batters
and generates matchup tags.

Tags Generated:
- LHB_SPECIALIST: Economy vs LHB at least 1.0 better than vs RHB
- RHB_SPECIALIST: Economy vs RHB at least 1.0 better than vs LHB
- LHB_VULNERABLE: Economy vs LHB at least 1.0 worse than vs RHB
- RHB_VULNERABLE: Economy vs RHB at least 1.0 worse than vs LHB
- LHB_WICKET_TAKER: Better bowling SR vs LHB (takes wickets more frequently)
- RHB_WICKET_TAKER: Better bowling SR vs RHB (takes wickets more frequently)
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

# Minimum balls faced to consider for analysis
MIN_BALLS_VS_HAND = 60  # ~10 overs


def get_bowler_vs_handedness(conn) -> pd.DataFrame:
    """Get bowler performance split by batter handedness."""

    df = conn.execute("""
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
        WHERE balls >= {min_balls}
        ORDER BY bowler_name, batting_hand
    """.format(min_balls=MIN_BALLS_VS_HAND)).df()

    return df


def calculate_matchup_differential(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate differential between LHB and RHB performance."""

    # Pivot to get LHB and RHB side by side
    lhb = df[df['batting_hand'] == 'Left-hand'].set_index('bowler_id')
    rhb = df[df['batting_hand'] == 'Right-hand'].set_index('bowler_id')

    # Get bowlers who have faced both
    common_bowlers = lhb.index.intersection(rhb.index)

    results = []
    for bowler_id in common_bowlers:
        lhb_row = lhb.loc[bowler_id]
        rhb_row = rhb.loc[bowler_id]

        results.append({
            'bowler_id': bowler_id,
            'bowler_name': lhb_row['bowler_name'],
            # LHB stats
            'lhb_balls': lhb_row['balls'],
            'lhb_economy': lhb_row['economy'],
            'lhb_strike_rate': lhb_row['strike_rate'],
            'lhb_dot_pct': lhb_row['dot_pct'],
            'lhb_boundary_pct': lhb_row['boundary_pct'],
            'lhb_wickets': lhb_row['wickets'],
            # RHB stats
            'rhb_balls': rhb_row['balls'],
            'rhb_economy': rhb_row['economy'],
            'rhb_strike_rate': rhb_row['strike_rate'],
            'rhb_dot_pct': rhb_row['dot_pct'],
            'rhb_boundary_pct': rhb_row['boundary_pct'],
            'rhb_wickets': rhb_row['wickets'],
            # Differentials (negative = better vs LHB)
            'economy_diff': lhb_row['economy'] - rhb_row['economy'],
            'dot_pct_diff': lhb_row['dot_pct'] - rhb_row['dot_pct'],
            'boundary_pct_diff': lhb_row['boundary_pct'] - rhb_row['boundary_pct'],
            # Strike rate differential (lower SR = takes wickets more often)
            # Negative = better vs LHB (lower SR means quicker wickets)
            'strike_rate_diff': (lhb_row['strike_rate'] or 999) - (rhb_row['strike_rate'] or 999),
            # Wickets per 100 balls differential
            'wickets_per_100_lhb': (lhb_row['wickets'] * 100 / lhb_row['balls']) if lhb_row['balls'] > 0 else 0,
            'wickets_per_100_rhb': (rhb_row['wickets'] * 100 / rhb_row['balls']) if rhb_row['balls'] > 0 else 0,
        })

    return pd.DataFrame(results)


def assign_handedness_tags(df: pd.DataFrame, economy_threshold: float = 1.0, sr_threshold: float = 6.0) -> pd.DataFrame:
    """Assign LHB/RHB matchup tags based on differential.

    Args:
        df: DataFrame with matchup differentials
        economy_threshold: Min economy difference for specialist/vulnerable tags (default 1.0)
        sr_threshold: Min strike rate difference for wicket-taker tags (default 6.0 balls)
    """

    tags = []

    for _, row in df.iterrows():
        player_tags = []

        # Economy differential
        eco_diff = row['economy_diff']

        if eco_diff <= -economy_threshold:
            # Better vs LHB (lower economy)
            player_tags.append('LHB_SPECIALIST')
        elif eco_diff >= economy_threshold:
            # Better vs RHB (lower economy)
            player_tags.append('RHB_SPECIALIST')

        # Also check if vulnerable
        if eco_diff >= economy_threshold:
            player_tags.append('LHB_VULNERABLE')
        elif eco_diff <= -economy_threshold:
            player_tags.append('RHB_VULNERABLE')

        # Strike rate / wicket-taking tags (lower SR = takes wickets faster)
        sr_diff = row['strike_rate_diff']
        # Need at least 3 wickets vs that hand to qualify
        if sr_diff <= -sr_threshold and row['lhb_wickets'] >= 3:
            # Better SR vs LHB (takes wickets more frequently)
            player_tags.append('LHB_WICKET_TAKER')
        elif sr_diff >= sr_threshold and row['rhb_wickets'] >= 3:
            # Better SR vs RHB
            player_tags.append('RHB_WICKET_TAKER')

        # Add dot ball differential tags
        dot_diff = row['dot_pct_diff']
        if dot_diff >= 5:  # 5% more dots vs LHB
            player_tags.append('LHB_PRESSURE')
        elif dot_diff <= -5:  # 5% more dots vs RHB
            player_tags.append('RHB_PRESSURE')

        tags.append(player_tags)

    df['handedness_tags'] = tags
    return df


def print_analysis(df: pd.DataFrame):
    """Print summary analysis."""

    print("\n" + "="*70)
    print("BOWLER VS LHB/RHB MATCHUP ANALYSIS")
    print("="*70)

    print(f"\n  Bowlers with sufficient data vs both hands: {len(df)}")

    # Count tags
    lhb_specialists = df[df['handedness_tags'].apply(lambda x: 'LHB_SPECIALIST' in x)]
    rhb_specialists = df[df['handedness_tags'].apply(lambda x: 'RHB_SPECIALIST' in x)]

    lhb_wicket_takers = df[df['handedness_tags'].apply(lambda x: 'LHB_WICKET_TAKER' in x)]
    rhb_wicket_takers = df[df['handedness_tags'].apply(lambda x: 'RHB_WICKET_TAKER' in x)]

    print(f"\n  LHB Specialists (economy ≥1.0 better vs lefties): {len(lhb_specialists)}")
    print(f"  RHB Specialists (economy ≥1.0 better vs righties): {len(rhb_specialists)}")
    print(f"  LHB Wicket Takers (better SR vs lefties): {len(lhb_wicket_takers)}")
    print(f"  RHB Wicket Takers (better SR vs righties): {len(rhb_wicket_takers)}")

    # Top LHB specialists
    print("\n  TOP LHB SPECIALISTS:")
    top_lhb = df.nsmallest(10, 'economy_diff')
    for _, row in top_lhb.iterrows():
        print(f"    {row['bowler_name']}: LHB Eco {row['lhb_economy']:.2f} vs RHB Eco {row['rhb_economy']:.2f} (diff: {row['economy_diff']:.2f})")

    # Top RHB specialists
    print("\n  TOP RHB SPECIALISTS:")
    top_rhb = df.nlargest(10, 'economy_diff')
    for _, row in top_rhb.iterrows():
        print(f"    {row['bowler_name']}: LHB Eco {row['lhb_economy']:.2f} vs RHB Eco {row['rhb_economy']:.2f} (diff: {row['economy_diff']:.2f})")

    # Neutral bowlers
    neutral = df[(df['economy_diff'].abs() < 0.5)]
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
        if row['handedness_tags']:
            handedness_lookup[row['bowler_id']] = row['handedness_tags']

    # Update bowler tags
    updated_count = 0
    for bowler in tags_data.get('bowlers', []):
        player_id = bowler.get('player_id')
        if player_id in handedness_lookup:
            existing_tags = set(bowler.get('tags', []))
            new_tags = set(handedness_lookup[player_id])
            # Remove old handedness tags first
            existing_tags -= {'LHB_SPECIALIST', 'RHB_SPECIALIST', 'LHB_VULNERABLE', 'RHB_VULNERABLE',
                            'LHB_PRESSURE', 'RHB_PRESSURE', 'LHB_WICKET_TAKER', 'RHB_WICKET_TAKER'}
            # Add new ones
            existing_tags.update(new_tags)
            bowler['tags'] = list(existing_tags)
            updated_count += 1

    # Save updated file
    with open(tags_path, 'w') as f:
        json.dump(tags_data, f, indent=2)

    print(f"\n  Updated {updated_count} bowlers in player_tags.json")

    return updated_count


def save_matchup_data(df: pd.DataFrame):
    """Save matchup data to CSV for review."""

    output_path = OUTPUT_DIR / "bowler_handedness_matchup.csv"

    # Select columns for output
    output_df = df[[
        'bowler_id', 'bowler_name',
        'lhb_balls', 'lhb_economy', 'lhb_strike_rate', 'lhb_wickets',
        'rhb_balls', 'rhb_economy', 'rhb_strike_rate', 'rhb_wickets',
        'economy_diff', 'strike_rate_diff', 'handedness_tags'
    ]].copy()

    # Convert tags list to string
    output_df['handedness_tags'] = output_df['handedness_tags'].apply(lambda x: ', '.join(x) if x else '')

    output_df.to_csv(output_path, index=False)
    print(f"\n  Matchup data saved to: {output_path}")


def main():
    print("="*70)
    print("Cricket Playbook - Bowler vs LHB/RHB Matchup Analysis")
    print("Author: Stephen Curry | Sprint 2.5")
    print("="*70)

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

    print("\n" + "="*70)
    print("LHB/RHB MATCHUP ANALYSIS COMPLETE")
    print("="*70)

    return 0


if __name__ == "__main__":
    exit(main())
