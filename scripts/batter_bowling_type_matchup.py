#!/usr/bin/env python3
"""
Cricket Playbook - Batter vs Bowling Type Matchup Analysis
Author: Stephen Curry (Analytics Lead)
Sprint: 2.6 - Founder Review #2

Analyzes batter performance against different bowling types and generates matchup tags.

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
MIN_BALLS_VS_TYPE = 30  # ~5 overs

# Thresholds for tags
# Updated per Founder Review #3: Include quality (average), not just quantity (SR)
SPECIALIST_SR_THRESHOLD = 130
SPECIALIST_AVG_THRESHOLD = 25  # Minimum average to be specialist
SPECIALIST_BPD_THRESHOLD = 20  # Minimum balls per dismissal

VULNERABLE_SR_THRESHOLD = 105
VULNERABLE_AVG_THRESHOLD = 15  # Below this average = vulnerable
VULNERABLE_BPD_THRESHOLD = 15  # Below this balls per dismissal = vulnerable

# Bowling type categories
PACE_TYPES = ['Fast', 'Medium']
SPIN_TYPES = ['Off-spin', 'Leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin']


def get_batter_vs_bowling_type(conn) -> pd.DataFrame:
    """Get batter performance split by bowling type."""

    df = conn.execute("""
        WITH batter_vs_type AS (
            SELECT
                fb.batter_id,
                dp.current_name as batter_name,
                sq.bowling_type,
                COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as dismissals,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dots
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            JOIN ipl_2026_squads sq ON fb.bowler_id = sq.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND sq.bowling_type IS NOT NULL
            GROUP BY fb.batter_id, dp.current_name, sq.bowling_type
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
            dots,
            ROUND(runs * 100.0 / NULLIF(balls, 0), 2) as strike_rate,
            ROUND(runs * 1.0 / NULLIF(dismissals, 0), 2) as average,
            ROUND(dots * 100.0 / NULLIF(balls, 0), 2) as dot_pct,
            ROUND((fours + sixes) * 100.0 / NULLIF(balls, 0), 2) as boundary_pct
        FROM batter_vs_type
        WHERE balls >= {min_balls}
        ORDER BY batter_name, bowling_type
    """.format(min_balls=MIN_BALLS_VS_TYPE)).df()

    return df


def aggregate_by_pace_spin(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate stats into Pace vs Spin categories."""

    results = []

    for batter_id in df['batter_id'].unique():
        batter_df = df[df['batter_id'] == batter_id]
        batter_name = batter_df['batter_name'].iloc[0]

        # Pace stats
        pace_df = batter_df[batter_df['bowling_type'].isin(PACE_TYPES)]
        if len(pace_df) > 0:
            pace_balls = pace_df['balls'].sum()
            pace_runs = pace_df['runs'].sum()
            pace_dismissals = pace_df['dismissals'].sum()
            pace_sr = round(pace_runs * 100 / pace_balls, 2) if pace_balls > 0 else 0
            pace_avg = round(pace_runs / pace_dismissals, 2) if pace_dismissals > 0 else None
        else:
            pace_balls, pace_runs, pace_dismissals, pace_sr, pace_avg = 0, 0, 0, 0, None

        # Spin stats
        spin_df = batter_df[batter_df['bowling_type'].isin(SPIN_TYPES)]
        if len(spin_df) > 0:
            spin_balls = spin_df['balls'].sum()
            spin_runs = spin_df['runs'].sum()
            spin_dismissals = spin_df['dismissals'].sum()
            spin_sr = round(spin_runs * 100 / spin_balls, 2) if spin_balls > 0 else 0
            spin_avg = round(spin_runs / spin_dismissals, 2) if spin_dismissals > 0 else None
        else:
            spin_balls, spin_runs, spin_dismissals, spin_sr, spin_avg = 0, 0, 0, 0, None

        results.append({
            'batter_id': batter_id,
            'batter_name': batter_name,
            'pace_balls': pace_balls,
            'pace_sr': pace_sr,
            'pace_avg': pace_avg,
            'pace_dismissals': pace_dismissals,
            'spin_balls': spin_balls,
            'spin_sr': spin_sr,
            'spin_avg': spin_avg,
            'spin_dismissals': spin_dismissals,
        })

    return pd.DataFrame(results)


def assign_matchup_tags(raw_df: pd.DataFrame, pace_spin_df: pd.DataFrame) -> pd.DataFrame:
    """Assign batting matchup tags based on performance vs bowling types."""

    tags_dict = {}

    for _, row in pace_spin_df.iterrows():
        batter_id = row['batter_id']
        player_tags = []

        # Pace vs Spin tags (need minimum balls)
        if row['pace_balls'] >= MIN_BALLS_VS_TYPE:
            if row['pace_sr'] >= SPECIALIST_SR_THRESHOLD:
                player_tags.append('SPECIALIST_VS_PACE')
            elif row['pace_sr'] < VULNERABLE_SR_THRESHOLD:
                player_tags.append('VULNERABLE_VS_PACE')

        if row['spin_balls'] >= MIN_BALLS_VS_TYPE:
            if row['spin_sr'] >= SPECIALIST_SR_THRESHOLD:
                player_tags.append('SPECIALIST_VS_SPIN')
            elif row['spin_sr'] < VULNERABLE_SR_THRESHOLD:
                player_tags.append('VULNERABLE_VS_SPIN')

        tags_dict[batter_id] = player_tags

    # Now add specific bowling type tags
    # Updated per Founder Review #3: Include average (quality) not just SR (quantity)
    for _, row in raw_df.iterrows():
        batter_id = row['batter_id']
        bowling_type = row['bowling_type']
        sr = row['strike_rate'] or 0
        avg = row['average']  # runs per dismissal
        balls = row['balls']
        dismissals = row['dismissals']

        # Calculate balls per dismissal
        bpd = balls / dismissals if dismissals > 0 else 999

        if batter_id not in tags_dict:
            tags_dict[batter_id] = []

        # Map bowling type to tag suffix
        type_map = {
            'Off-spin': 'OFF_SPIN',
            'Leg-spin': 'LEG_SPIN',
            'Left-arm orthodox': 'LEFT_ARM_SPIN',
            'Left-arm wrist spin': 'LEFT_ARM_WRIST_SPIN',
        }

        if bowling_type in type_map:
            suffix = type_map[bowling_type]

            # SPECIALIST: Good SR AND good average AND doesn't get out often
            # Example: Markram has SR 130 but avg 18 and bpd 13.75 - NOT a specialist
            is_specialist = (
                sr >= SPECIALIST_SR_THRESHOLD and
                (avg is None or avg >= SPECIALIST_AVG_THRESHOLD) and
                bpd >= SPECIALIST_BPD_THRESHOLD
            )

            # VULNERABLE: Poor SR OR poor average OR gets out too often
            is_vulnerable = (
                sr < VULNERABLE_SR_THRESHOLD or
                (avg is not None and avg < VULNERABLE_AVG_THRESHOLD) or
                (dismissals >= 3 and bpd < VULNERABLE_BPD_THRESHOLD)
            )

            if is_specialist:
                tag = f'SPECIALIST_VS_{suffix}'
                if tag not in tags_dict[batter_id]:
                    tags_dict[batter_id].append(tag)
            elif is_vulnerable:
                tag = f'VULNERABLE_VS_{suffix}'
                if tag not in tags_dict[batter_id]:
                    tags_dict[batter_id].append(tag)

    # Convert to DataFrame
    result_df = pace_spin_df.copy()
    result_df['bowling_type_tags'] = result_df['batter_id'].map(tags_dict)

    return result_df


def print_analysis(df: pd.DataFrame, raw_df: pd.DataFrame):
    """Print summary analysis."""

    print("\n" + "="*70)
    print("BATTER VS BOWLING TYPE MATCHUP ANALYSIS")
    print("="*70)

    print(f"\n  Batters with sufficient data: {len(df)}")

    # Count tags
    pace_specialists = df[df['bowling_type_tags'].apply(lambda x: 'SPECIALIST_VS_PACE' in x if x else False)]
    spin_specialists = df[df['bowling_type_tags'].apply(lambda x: 'SPECIALIST_VS_SPIN' in x if x else False)]
    pace_vulnerable = df[df['bowling_type_tags'].apply(lambda x: 'VULNERABLE_VS_PACE' in x if x else False)]
    spin_vulnerable = df[df['bowling_type_tags'].apply(lambda x: 'VULNERABLE_VS_SPIN' in x if x else False)]

    print(f"\n  SPECIALIST_VS_PACE (SR ≥{SPECIALIST_SR_THRESHOLD}): {len(pace_specialists)}")
    print(f"  SPECIALIST_VS_SPIN (SR ≥{SPECIALIST_SR_THRESHOLD}): {len(spin_specialists)}")
    print(f"  VULNERABLE_VS_PACE (SR <{VULNERABLE_SR_THRESHOLD}): {len(pace_vulnerable)}")
    print(f"  VULNERABLE_VS_SPIN (SR <{VULNERABLE_SR_THRESHOLD}): {len(spin_vulnerable)}")

    # Specific type tags
    for tag_type in ['OFF_SPIN', 'LEG_SPIN', 'LEFT_ARM_SPIN']:
        spec_tag = f'SPECIALIST_VS_{tag_type}'
        vuln_tag = f'VULNERABLE_VS_{tag_type}'
        spec_count = len(df[df['bowling_type_tags'].apply(lambda x: spec_tag in x if x else False)])
        vuln_count = len(df[df['bowling_type_tags'].apply(lambda x: vuln_tag in x if x else False)])
        print(f"  {spec_tag}: {spec_count}, {vuln_tag}: {vuln_count}")

    # Top pace specialists
    print("\n  TOP PACE SPECIALISTS:")
    top_pace = df[df['pace_balls'] >= MIN_BALLS_VS_TYPE].nlargest(10, 'pace_sr')
    for _, row in top_pace.iterrows():
        print(f"    {row['batter_name']}: SR {row['pace_sr']:.1f} ({row['pace_balls']} balls)")

    # Top spin specialists
    print("\n  TOP SPIN SPECIALISTS:")
    top_spin = df[df['spin_balls'] >= MIN_BALLS_VS_TYPE].nlargest(10, 'spin_sr')
    for _, row in top_spin.iterrows():
        print(f"    {row['batter_name']}: SR {row['spin_sr']:.1f} ({row['spin_balls']} balls)")

    # Most vulnerable vs pace
    print("\n  MOST VULNERABLE VS PACE:")
    vuln_pace = df[(df['pace_balls'] >= MIN_BALLS_VS_TYPE) & (df['pace_sr'] < VULNERABLE_SR_THRESHOLD)].nsmallest(10, 'pace_sr')
    for _, row in vuln_pace.iterrows():
        print(f"    {row['batter_name']}: SR {row['pace_sr']:.1f} ({row['pace_balls']} balls)")

    # Most vulnerable vs spin
    print("\n  MOST VULNERABLE VS SPIN:")
    vuln_spin = df[(df['spin_balls'] >= MIN_BALLS_VS_TYPE) & (df['spin_sr'] < VULNERABLE_SR_THRESHOLD)].nsmallest(10, 'spin_sr')
    for _, row in vuln_spin.iterrows():
        print(f"    {row['batter_name']}: SR {row['spin_sr']:.1f} ({row['spin_balls']} balls)")


def update_player_tags_json(matchup_df: pd.DataFrame):
    """Update player_tags.json with bowling type matchup tags."""

    tags_path = OUTPUT_DIR / "player_tags.json"

    if tags_path.exists():
        with open(tags_path) as f:
            tags_data = json.load(f)
    else:
        tags_data = {"batters": [], "bowlers": []}

    # Create lookup for matchup tags
    matchup_lookup = {}
    for _, row in matchup_df.iterrows():
        if row['bowling_type_tags']:
            matchup_lookup[row['batter_id']] = row['bowling_type_tags']

    # All possible bowling type tags to remove before updating
    bowling_type_tags = {
        'SPECIALIST_VS_PACE', 'SPECIALIST_VS_SPIN', 'VULNERABLE_VS_PACE', 'VULNERABLE_VS_SPIN',
        'SPECIALIST_VS_OFF_SPIN', 'SPECIALIST_VS_LEG_SPIN', 'SPECIALIST_VS_LEFT_ARM_SPIN',
        'SPECIALIST_VS_LEFT_ARM_WRIST_SPIN',
        'VULNERABLE_VS_OFF_SPIN', 'VULNERABLE_VS_LEG_SPIN', 'VULNERABLE_VS_LEFT_ARM_SPIN',
        'VULNERABLE_VS_LEFT_ARM_WRIST_SPIN',
    }

    # Update batter tags
    updated_count = 0
    for batter in tags_data.get('batters', []):
        player_id = batter.get('player_id')
        if player_id in matchup_lookup:
            existing_tags = set(batter.get('tags', []))
            new_tags = set(matchup_lookup[player_id])
            # Remove old bowling type tags first
            existing_tags -= bowling_type_tags
            # Add new ones
            existing_tags.update(new_tags)
            batter['tags'] = list(existing_tags)
            updated_count += 1

    # Save updated file
    with open(tags_path, 'w') as f:
        json.dump(tags_data, f, indent=2)

    print(f"\n  Updated {updated_count} batters in player_tags.json")

    return updated_count


def save_matchup_data(df: pd.DataFrame, raw_df: pd.DataFrame):
    """Save matchup data to CSV for review."""

    output_path = OUTPUT_DIR / "batter_bowling_type_matchup.csv"

    # Select columns for output
    output_df = df[[
        'batter_id', 'batter_name',
        'pace_balls', 'pace_sr', 'pace_avg', 'pace_dismissals',
        'spin_balls', 'spin_sr', 'spin_avg', 'spin_dismissals',
        'bowling_type_tags'
    ]].copy()

    # Convert tags list to string
    output_df['bowling_type_tags'] = output_df['bowling_type_tags'].apply(lambda x: ', '.join(x) if x else '')

    output_df.to_csv(output_path, index=False)
    print(f"\n  Matchup data saved to: {output_path}")

    # Also save detailed breakdown
    detail_path = OUTPUT_DIR / "batter_bowling_type_detail.csv"
    raw_df.to_csv(detail_path, index=False)
    print(f"  Detailed data saved to: {detail_path}")


def main():
    print("="*70)
    print("Cricket Playbook - Batter vs Bowling Type Matchup Analysis")
    print("Author: Stephen Curry | Sprint 2.6")
    print("="*70)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Get batter performance by bowling type
    print("\n1. Extracting batter vs bowling type data...")
    raw_df = get_batter_vs_bowling_type(conn)
    print(f"   Records: {len(raw_df)}")

    # Aggregate into Pace vs Spin
    print("\n2. Aggregating Pace vs Spin stats...")
    pace_spin_df = aggregate_by_pace_spin(raw_df)
    print(f"   Batters: {len(pace_spin_df)}")

    # Assign tags
    print("\n3. Assigning bowling type matchup tags...")
    matchup_df = assign_matchup_tags(raw_df, pace_spin_df)

    # Print analysis
    print_analysis(matchup_df, raw_df)

    # Save data
    print("\n4. Saving results...")
    save_matchup_data(matchup_df, raw_df)

    # Update player_tags.json
    print("\n5. Updating player_tags.json...")
    update_player_tags_json(matchup_df)

    conn.close()

    print("\n" + "="*70)
    print("BATTER VS BOWLING TYPE ANALYSIS COMPLETE")
    print("="*70)

    return 0


if __name__ == "__main__":
    exit(main())
