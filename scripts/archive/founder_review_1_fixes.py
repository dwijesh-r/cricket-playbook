#!/usr/bin/env python3
"""
Cricket Playbook - Founder Review #1 Data Fixes
Sprint 2.4 - Data Fix Sprint

Author: Brock Purdy (Data Pipeline) & Andy Flower (Cricket Domain)
Date: 2026-01-21

Fixes:
- P0: 10 player ID mismatches (uncapped players mapped to wrong historical players)
- P1: 18+ bowling type corrections
- P2: RCB squad composition fixes
- Schema: Add is_ipl_uncapped flag and bowling_type_secondary column
"""

import duckdb
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"

# =============================================================================
# P0: UNCAPPED PLAYERS - These players have 0 IPL matches but were incorrectly
# mapped to other players' stats. We need to:
# 1. Mark them as uncapped
# 2. Clear their incorrect player_id (set to NULL or generate new one)
# =============================================================================

UNCAPPED_PLAYERS = [
    # (player_name, team_name, notes)
    ("Kartik Sharma", "Chennai Super Kings", "Mapped to Karn Sharma incorrectly"),
    ("Gurjapneet Singh", "Chennai Super Kings", "Mapped to Gurkeerat Singh Mann"),
    ("Mohammed Izhar", "Mumbai Indians", "Mapped to unknown player"),
    ("Harnoor Singh", "Punjab Kings", "Mapped to Harbhajan Singh"),
    ("Ravi Singh", "Rajasthan Royals", "Mapped to Rinku Singh"),
    ("Brijesh Sharma", "Rajasthan Royals", "Uncapped"),
    ("Abhinandan Singh", "Royal Challengers Bengaluru", "Mapped to Arshdeep Singh"),
    ("Shivang Kumar", "Sunrisers Hyderabad", "Uncapped, bowls left-arm wrist spin"),
    ("Amit Kumar", "Punjab Kings", "Uncapped, bowls right-arm leg spin"),
]

# =============================================================================
# P1: BOWLING TYPE CORRECTIONS
# Format: (player_name, team_name, correct_bowling_type, correct_bowling_type_secondary, notes)
# =============================================================================

BOWLING_TYPE_FIXES = [
    # Single bowling type corrections
    ("Aman Khan", "Chennai Super Kings", "Medium", None, "Medium pacer, not off-spin"),
    (
        "Ayush Badoni",
        "Lucknow Super Giants",
        "Off-spin",
        None,
        "Off-spin, not leg-spin",
    ),
    (
        "Prashant Veer",
        "Chennai Super Kings",
        "Left-arm orthodox",
        None,
        "Left-arm orthodox",
    ),
    ("Nitish Rana", "Delhi Capitals", "Off-spin", None, "Right-arm off-spin"),
    ("Tristan Stubbs", "Delhi Capitals", "Off-spin", None, "Right-arm off-spin"),
    ("Vipraj Nigam", "Delhi Capitals", "Leg-spin", None, "Right-arm leg-spin"),
    ("Shahrukh Khan", "Gujarat Titans", "Off-spin", None, "Right-arm off-spin"),
    ("Gurnoor Brar", "Gujarat Titans", "Fast", None, "Right-arm fast bowler"),
    ("Rinku Singh", "Kolkata Knight Riders", "Off-spin", None, "Right-arm off-spin"),
    (
        "Prashant Solanki",
        "Kolkata Knight Riders",
        "Leg-spin",
        None,
        "Right-arm leg-spin",
    ),
    ("Daksh Kamra", "Lucknow Super Giants", "Leg-spin", None, "Right-arm leg-spin"),
    ("Digvesh Rathi", "Lucknow Super Giants", "Leg-spin", None, "Right-arm leg-spin"),
    ("Naman Dhir", "Mumbai Indians", "Off-spin", None, "Right-arm off-spin"),
    ("Suryansh Shedge", "Mumbai Indians", "Medium", None, "Medium pacer"),
    ("Riyan Parag", "Rajasthan Royals", "Leg-spin", None, "Right-arm leg-spin"),
    ("Yashasvi Jaiswal", "Rajasthan Royals", "Leg-spin", None, "Right-arm leg-spin"),
    (
        "Vaibhav Sooryavanshi",
        "Rajasthan Royals",
        "Left-arm orthodox",
        None,
        "Left-arm orthodox",
    ),
    (
        "Vignesh Puthur",
        "Rajasthan Royals",
        "Left-arm wrist spin",
        None,
        "Left-arm chinaman",
    ),
    ("Travis Head", "Sunrisers Hyderabad", "Off-spin", None, "Right-arm off-spin"),
    ("Nitish Reddy", "Sunrisers Hyderabad", "Medium", None, "Medium pacer"),
    (
        "Harsh Dubey",
        "Sunrisers Hyderabad",
        "Left-arm orthodox",
        None,
        "Left-arm orthodox",
    ),
    # Players who don't bowl - set to NULL
    ("Lhuan-dre Pretorius", "Gujarat Titans", None, None, "Doesn't bowl"),
    # Dual bowling type players
    (
        "Liam Livingstone",
        "Sunrisers Hyderabad",
        "Leg-spin",
        "Off-spin",
        "Bowls both leg-spin and off-spin",
    ),
    (
        "Kamindu Mendis",
        "Sunrisers Hyderabad",
        "Off-spin",
        "Left-arm orthodox",
        "Bowls both RA off-spin and LA orthodox",
    ),
]

# =============================================================================
# P2: RCB SQUAD FIXES
# =============================================================================

RCB_FIXES = {
    "remove": [
        ("Raqibul Hasan", "Should be Rasikh Salam Dar"),
    ],
    "add": [
        # (player_name, role, bowling_type, batting_hand, notes)
        ("Rasikh Salam Dar", "Bowler", "Fast", "Right-hand", "Replaces Raqibul Hasan"),
        (
            "Vicky Ostwal",
            "Bowler",
            "Left-arm orthodox",
            "Left-hand",
            "Missing from squad",
        ),
        ("Vihaan Malhotra", "Batter", "Medium", "Right-hand", "Missing from squad"),
        ("Kanishk Chouhan", "Bowler", "Leg-spin", "Right-hand", "Missing from squad"),
    ],
}


def apply_schema_changes(conn):
    """Add new columns to ipl_2026_squads table."""
    print("\n" + "=" * 70)
    print("STEP 1: SCHEMA CHANGES")
    print("=" * 70)

    # Check if columns already exist
    cols = [c[0] for c in conn.execute("DESCRIBE ipl_2026_squads").fetchall()]

    if "is_ipl_uncapped" not in cols:
        print("  Adding is_ipl_uncapped column...")
        conn.execute("ALTER TABLE ipl_2026_squads ADD COLUMN is_ipl_uncapped BOOLEAN DEFAULT FALSE")
        print("    - Added is_ipl_uncapped (BOOLEAN)")
    else:
        print("  is_ipl_uncapped column already exists")

    if "bowling_type_secondary" not in cols:
        print("  Adding bowling_type_secondary column...")
        conn.execute("ALTER TABLE ipl_2026_squads ADD COLUMN bowling_type_secondary VARCHAR")
        print("    - Added bowling_type_secondary (VARCHAR)")
    else:
        print("  bowling_type_secondary column already exists")

    print("  Schema changes complete.")


def fix_uncapped_players(conn):
    """Mark uncapped players and clear their incorrect player_id."""
    print("\n" + "=" * 70)
    print("STEP 2: FIX UNCAPPED PLAYER MAPPINGS (P0)")
    print("=" * 70)

    for player_name, team_name, notes in UNCAPPED_PLAYERS:
        # Check if player exists
        result = conn.execute(
            """
            SELECT player_id FROM ipl_2026_squads
            WHERE player_name = ? AND team_name = ?
        """,
            [player_name, team_name],
        ).fetchone()

        if result:
            old_id = result[0]
            # Generate a new unique ID for uncapped player (prefix with 'uncapped_')
            new_id = f"uncapped_{player_name.lower().replace(' ', '_')}"

            conn.execute(
                """
                UPDATE ipl_2026_squads
                SET player_id = ?, is_ipl_uncapped = TRUE
                WHERE player_name = ? AND team_name = ?
            """,
                [new_id, player_name, team_name],
            )

            print(f"  FIXED: {player_name} ({team_name})")
            print(f"         Old ID: {old_id} -> New ID: {new_id}")
            print("         Marked as IPL uncapped")
            print(f"         Note: {notes}")
        else:
            print(f"  WARNING: {player_name} ({team_name}) not found in squad")


def fix_bowling_types(conn):
    """Correct bowling type classifications."""
    print("\n" + "=" * 70)
    print("STEP 3: FIX BOWLING TYPE CLASSIFICATIONS (P1)")
    print("=" * 70)

    fixed_count = 0
    for (
        player_name,
        team_name,
        bowling_type,
        bowling_type_secondary,
        notes,
    ) in BOWLING_TYPE_FIXES:
        # Check current value
        result = conn.execute(
            """
            SELECT bowling_type, bowling_type_secondary FROM ipl_2026_squads
            WHERE player_name = ? AND team_name = ?
        """,
            [player_name, team_name],
        ).fetchone()

        if result:
            old_type = result[0]
            old_secondary = result[1] if len(result) > 1 else None

            conn.execute(
                """
                UPDATE ipl_2026_squads
                SET bowling_type = ?, bowling_type_secondary = ?
                WHERE player_name = ? AND team_name = ?
            """,
                [bowling_type, bowling_type_secondary, player_name, team_name],
            )

            print(f"  FIXED: {player_name} ({team_name})")
            print(f"         bowling_type: {old_type} -> {bowling_type}")
            if bowling_type_secondary:
                print(
                    f"         bowling_type_secondary: {old_secondary} -> {bowling_type_secondary}"
                )
            print(f"         Note: {notes}")
            fixed_count += 1
        else:
            # Try fuzzy match
            result = conn.execute(
                """
                SELECT player_name, team_name FROM ipl_2026_squads
                WHERE player_name LIKE ? AND team_name = ?
            """,
                [f"%{player_name.split()[-1]}%", team_name],
            ).fetchall()

            if result:
                print(f"  WARNING: {player_name} not found. Similar names in {team_name}:")
                for r in result:
                    print(f"           - {r[0]}")
            else:
                print(f"  WARNING: {player_name} ({team_name}) not found in squad")

    print(f"\n  Total bowling types fixed: {fixed_count}")


def fix_rcb_squad(conn):
    """Fix RCB squad composition."""
    print("\n" + "=" * 70)
    print("STEP 4: FIX RCB SQUAD COMPOSITION (P2)")
    print("=" * 70)

    # Remove incorrect players
    for player_name, reason in RCB_FIXES["remove"]:
        result = conn.execute(
            """
            SELECT player_name FROM ipl_2026_squads
            WHERE player_name = ? AND team_name = 'Royal Challengers Bengaluru'
        """,
            [player_name],
        ).fetchone()

        if result:
            conn.execute(
                """
                DELETE FROM ipl_2026_squads
                WHERE player_name = ? AND team_name = 'Royal Challengers Bengaluru'
            """,
                [player_name],
            )
            print(f"  REMOVED: {player_name}")
            print(f"           Reason: {reason}")
        else:
            print(f"  NOTE: {player_name} not found in RCB squad (may already be removed)")

    # Add missing players
    for player_name, role, bowling_type, batting_hand, notes in RCB_FIXES["add"]:
        # Check if already exists
        result = conn.execute(
            """
            SELECT player_name FROM ipl_2026_squads
            WHERE player_name = ? AND team_name = 'Royal Challengers Bengaluru'
        """,
            [player_name],
        ).fetchone()

        if not result:
            # Generate uncapped ID
            player_id = f"uncapped_{player_name.lower().replace(' ', '_')}"

            conn.execute(
                """
                INSERT INTO ipl_2026_squads
                (team_name, player_name, player_id, role, bowling_type, batting_hand, is_ipl_uncapped)
                VALUES ('Royal Challengers Bengaluru', ?, ?, ?, ?, ?, TRUE)
            """,
                [player_name, player_id, role, bowling_type, batting_hand],
            )

            print(f"  ADDED: {player_name}")
            print(f"         Role: {role}, Bowling: {bowling_type}")
            print(f"         Note: {notes}")
        else:
            print(f"  NOTE: {player_name} already exists in RCB squad")


def verify_fixes(conn):
    """Verify all fixes were applied correctly."""
    print("\n" + "=" * 70)
    print("STEP 5: VERIFICATION")
    print("=" * 70)

    # Count uncapped players
    result = conn.execute("""
        SELECT COUNT(*) FROM ipl_2026_squads WHERE is_ipl_uncapped = TRUE
    """).fetchone()
    print(f"  Uncapped players marked: {result[0]}")

    # Count players with secondary bowling type
    result = conn.execute("""
        SELECT COUNT(*) FROM ipl_2026_squads WHERE bowling_type_secondary IS NOT NULL
    """).fetchone()
    print(f"  Players with dual bowling type: {result[0]}")

    # Show RCB squad size
    result = conn.execute("""
        SELECT COUNT(*) FROM ipl_2026_squads WHERE team_name = 'Royal Challengers Bengaluru'
    """).fetchone()
    print(f"  RCB squad size: {result[0]}")

    # List uncapped players
    print("\n  Uncapped players:")
    result = conn.execute("""
        SELECT player_name, team_name FROM ipl_2026_squads
        WHERE is_ipl_uncapped = TRUE
        ORDER BY team_name, player_name
    """).fetchall()
    for r in result:
        print(f"    - {r[0]} ({r[1]})")

    # List dual-type bowlers
    print("\n  Dual-type bowlers:")
    result = conn.execute("""
        SELECT player_name, team_name, bowling_type, bowling_type_secondary
        FROM ipl_2026_squads
        WHERE bowling_type_secondary IS NOT NULL
        ORDER BY team_name, player_name
    """).fetchall()
    for r in result:
        print(f"    - {r[0]} ({r[1]}): {r[2]} + {r[3]}")


def generate_fix_report(conn):
    """Generate a summary report of all fixes."""
    print("\n" + "=" * 70)
    print("FIX REPORT SUMMARY")
    print("=" * 70)

    # Schema changes
    cols = [c[0] for c in conn.execute("DESCRIBE ipl_2026_squads").fetchall()]
    print(f"\n  Schema columns: {len(cols)}")
    print(f"    - is_ipl_uncapped: {'YES' if 'is_ipl_uncapped' in cols else 'NO'}")
    print(f"    - bowling_type_secondary: {'YES' if 'bowling_type_secondary' in cols else 'NO'}")

    # Data fixes
    uncapped = conn.execute(
        "SELECT COUNT(*) FROM ipl_2026_squads WHERE is_ipl_uncapped = TRUE"
    ).fetchone()[0]
    dual_type = conn.execute(
        "SELECT COUNT(*) FROM ipl_2026_squads WHERE bowling_type_secondary IS NOT NULL"
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM ipl_2026_squads").fetchone()[0]

    print("\n  Data summary:")
    print(f"    - Total players: {total}")
    print(f"    - Uncapped players: {uncapped}")
    print(f"    - Dual-type bowlers: {dual_type}")

    print("\n  Status: FIXES APPLIED SUCCESSFULLY")
    print("  Next step: Regenerate experience CSV")


def main():
    print("=" * 70)
    print("CRICKET PLAYBOOK - FOUNDER REVIEW #1 FIXES")
    print("Sprint 2.4 - Data Fix Sprint")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH))

    try:
        # Apply all fixes
        apply_schema_changes(conn)
        fix_uncapped_players(conn)
        fix_bowling_types(conn)
        fix_rcb_squad(conn)
        verify_fixes(conn)
        generate_fix_report(conn)

        conn.close()
        print("\n" + "=" * 70)
        print("ALL FIXES COMPLETE")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        conn.close()
        return 1


if __name__ == "__main__":
    exit(main())
