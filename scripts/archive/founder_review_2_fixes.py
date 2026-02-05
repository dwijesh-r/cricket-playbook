#!/usr/bin/env python3
"""
Cricket Playbook - Founder Review #2 Fixes
Author: Brock Purdy (Data Pipeline)
Sprint: 2.6

Fixes data issues identified in Founder Review #2:
1. Aman Khan (CSK) - mapped to Avesh Khan instead of Aman Hakim Khan
2. Shahrukh Khan (GT) - mapped to SN Khan instead of M Shahrukh Khan
3. Rasikh Salam Dar (RCB) - marked uncapped but has IPL history
"""

import duckdb
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
SQUAD_CSV_PATH = PROJECT_DIR / "data" / "ipl_2026_squads.csv"

# Player ID corrections
PLAYER_ID_FIXES = {
    # (team, player_name): (old_id, correct_id, correct_db_name)
    ("Chennai Super Kings", "Aman Khan"): ("eef2536f", "378daa89", "Aman Hakim Khan"),
    ("Gujarat Titans", "Shahrukh Khan"): ("f088b960", "7dcb9bc9", "M Shahrukh Khan"),
    ("Royal Challengers Bengaluru", "Rasikh Salam Dar"): (
        "uncapped_rasikh_salam_dar",
        "b8527c3d",
        "Rasikh Salam",
    ),
}


def fix_squad_csv():
    """Fix player IDs in the squad CSV file."""
    print("\n1. Fixing squad CSV player IDs...")

    df = pd.read_csv(SQUAD_CSV_PATH)

    for (team, player_name), (old_id, correct_id, db_name) in PLAYER_ID_FIXES.items():
        mask = (df["team_name"] == team) & (df["player_name"] == player_name)
        if mask.any():
            old_val = df.loc[mask, "player_id"].values[0]
            df.loc[mask, "player_id"] = correct_id
            print(f"   {player_name} ({team}): {old_val} -> {correct_id}")
        else:
            print(f"   WARNING: {player_name} not found in {team}")

    df.to_csv(SQUAD_CSV_PATH, index=False)
    print(f"   Saved to {SQUAD_CSV_PATH}")

    return df


def fix_database_squad_table(conn):
    """Fix player IDs in the database squad table."""
    print("\n2. Fixing database squad table...")

    for (team, player_name), (old_id, correct_id, db_name) in PLAYER_ID_FIXES.items():
        # Update player_id
        conn.execute(
            """
            UPDATE ipl_2026_squads
            SET player_id = ?, is_ipl_uncapped = FALSE
            WHERE team_name = ? AND player_name = ?
        """,
            [correct_id, team, player_name],
        )
        print(f"   Updated {player_name}: {old_id} -> {correct_id}")

    conn.commit()


def verify_fixes(conn):
    """Verify the fixes were applied correctly."""
    print("\n3. Verifying fixes...")

    for (team, player_name), (old_id, correct_id, db_name) in PLAYER_ID_FIXES.items():
        # Check squad table
        result = conn.execute(
            """
            SELECT player_id, is_ipl_uncapped
            FROM ipl_2026_squads
            WHERE team_name = ? AND player_name = ?
        """,
            [team, player_name],
        ).fetchone()

        if result:
            pid, uncapped = result
            status = "PASS" if pid == correct_id else "FAIL"
            print(f"   {player_name}: player_id={pid}, uncapped={uncapped} [{status}]")

        # Check if player has IPL data
        stats = conn.execute(
            """
            SELECT
                COUNT(DISTINCT fb.match_id) as matches,
                SUM(fb.batter_runs) FILTER (WHERE fb.batter_id = ?) as runs,
                SUM(CASE WHEN fb.bowler_id = ? AND fb.is_wicket THEN 1 ELSE 0 END) as wickets
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE (fb.batter_id = ? OR fb.bowler_id = ?)
              AND dt.tournament_name = 'Indian Premier League'
        """,
            [correct_id, correct_id, correct_id, correct_id],
        ).fetchone()

        print(f"      IPL Stats: {stats[0]} matches, {stats[1] or 0} runs, {stats[2] or 0} wickets")


def regenerate_experience_csv(conn):
    """Regenerate the experience CSV with corrected data."""
    print("\n4. Regenerating experience CSV...")

    # Import and run the experience generator
    import sys

    sys.path.insert(0, str(SCRIPT_DIR))
    from generate_experience_csv import generate_experience_csv

    generate_experience_csv()
    print("   Experience CSV regenerated")


def main():
    print("=" * 70)
    print("Cricket Playbook - Founder Review #2 Fixes")
    print("Author: Brock Purdy | Sprint 2.6")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    # Fix CSV first
    fix_squad_csv()

    # Then fix database
    conn = duckdb.connect(str(DB_PATH))
    fix_database_squad_table(conn)
    verify_fixes(conn)

    # Regenerate experience CSV
    regenerate_experience_csv(conn)

    conn.close()

    print("\n" + "=" * 70)
    print("FOUNDER REVIEW #2 DATA FIXES COMPLETE")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
