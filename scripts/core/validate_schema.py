#!/usr/bin/env python3
"""
Cricket Playbook - Schema Validation Script
============================================

Validates:
1. Required tables exist
2. Required columns present
3. Data type verification
4. Foreign key integrity (logical)
5. Data quality checks

Usage: python scripts/validate_schema.py
"""

import sys
from pathlib import Path
from typing import Tuple

import duckdb

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"

# Color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color


def print_pass(msg: str) -> None:
    print(f"  {GREEN}PASS{NC}: {msg}")


def print_fail(msg: str) -> None:
    print(f"  {RED}FAIL{NC}: {msg}")


def print_warn(msg: str) -> None:
    print(f"  {YELLOW}WARN{NC}: {msg}")


# Schema definitions for validation
REQUIRED_TABLES = {
    "fact_ball": [
        ("match_id", "VARCHAR"),
        ("innings", None),  # BIGINT in actual
        ("over", None),  # BIGINT in actual
        ("ball", None),  # BIGINT in actual
        ("batter_id", "VARCHAR"),
        ("bowler_id", "VARCHAR"),
        ("batter_runs", None),  # BIGINT in actual
        ("total_runs", None),  # BIGINT in actual
        ("is_wicket", "BOOLEAN"),
        ("is_legal_ball", "BOOLEAN"),
        ("match_phase", "VARCHAR"),
    ],
    "dim_player": [
        ("player_id", "VARCHAR"),
        ("current_name", "VARCHAR"),
    ],
    "dim_match": [
        ("match_id", "VARCHAR"),
        ("tournament_id", "VARCHAR"),
        ("venue_id", "VARCHAR"),
        ("match_date", None),  # Date type varies
    ],
    "dim_tournament": [
        ("tournament_id", "VARCHAR"),
        ("tournament_name", "VARCHAR"),
    ],
    "dim_team": [
        ("team_id", "VARCHAR"),
        ("team_name", "VARCHAR"),
    ],
    "ipl_2026_squads": [
        ("team_name", "VARCHAR"),
        ("player_name", "VARCHAR"),
        ("player_id", "VARCHAR"),
        ("role", "VARCHAR"),
        ("bowling_style", "VARCHAR"),
    ],
    "dim_bowler_classification": [
        ("player_id", "VARCHAR"),
        ("player_name", "VARCHAR"),
        ("bowling_style", "VARCHAR"),
    ],
    "dim_franchise_alias": [
        ("team_name", "VARCHAR"),
        ("canonical_name", "VARCHAR"),
    ],
}

REQUIRED_VIEWS = [
    "analytics_ipl_batting_career",
    "analytics_ipl_bowling_career",
    "analytics_ipl_batter_phase",
    "analytics_ipl_bowler_phase",
    "analytics_ipl_batter_vs_bowler",
    "analytics_ipl_batter_vs_bowler_type",
    "analytics_ipl_batter_vs_team",
    "analytics_ipl_bowler_vs_team",
    "analytics_ipl_squad_batting",
    "analytics_ipl_squad_bowling",
    "analytics_ipl_batting_percentiles",
    "analytics_ipl_bowling_percentiles",
    "analytics_ipl_batting_benchmarks",
    "analytics_ipl_bowling_benchmarks",
]


def validate_tables(conn: duckdb.DuckDBPyConnection) -> Tuple[int, int]:
    """Validate required tables exist with correct columns."""
    print("\n1. Validating Required Tables...")

    passes = 0
    fails = 0

    for table_name, columns in REQUIRED_TABLES.items():
        try:
            # Check table exists
            result = conn.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = '{table_name}'
            """).fetchone()

            if result[0] == 0:
                print_fail(f"Table '{table_name}' does not exist")
                fails += 1
                continue

            # Check columns
            existing_cols = conn.execute(f"DESCRIBE {table_name}").fetchall()
            existing_col_names = {col[0].lower() for col in existing_cols}
            existing_col_types = {col[0].lower(): col[1] for col in existing_cols}

            table_pass = True
            for col_name, expected_type in columns:
                if col_name.lower() not in existing_col_names:
                    print_fail(f"Table '{table_name}' missing column '{col_name}'")
                    fails += 1
                    table_pass = False
                elif (
                    expected_type
                    and expected_type.upper() not in existing_col_types[col_name.lower()].upper()
                ):
                    print_warn(
                        f"Table '{table_name}'.{col_name} type mismatch: expected {expected_type}, got {existing_col_types[col_name.lower()]}"
                    )

            if table_pass:
                print_pass(f"Table '{table_name}' structure valid")
                passes += 1

        except duckdb.Error as e:
            print_fail(f"Error checking table '{table_name}': {e}")
            fails += 1

    return passes, fails


def validate_views(conn: duckdb.DuckDBPyConnection) -> Tuple[int, int]:
    """Validate required views exist and are queryable."""
    print("\n2. Validating Required Views...")

    passes = 0
    fails = 0

    for view_name in REQUIRED_VIEWS:
        try:
            # Try to query the view
            result = conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
            if result[0] > 0:
                print_pass(f"View '{view_name}' exists and has data ({result[0]:,} rows)")
                passes += 1
            else:
                print_warn(f"View '{view_name}' exists but has no data")
                passes += 1
        except duckdb.Error as e:
            print_fail(f"View '{view_name}' not queryable: {e}")
            fails += 1

    return passes, fails


def validate_referential_integrity(conn: duckdb.DuckDBPyConnection) -> Tuple[int, int]:
    """Check logical foreign key relationships."""
    print("\n3. Validating Referential Integrity...")

    passes = 0
    fails = 0

    checks = [
        # (description, query that should return 0 for valid data)
        (
            "All fact_ball.batter_id exists in dim_player",
            """
            SELECT COUNT(DISTINCT fb.batter_id)
            FROM fact_ball fb
            LEFT JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE dp.player_id IS NULL
            """,
        ),
        (
            "All fact_ball.bowler_id exists in dim_player",
            """
            SELECT COUNT(DISTINCT fb.bowler_id)
            FROM fact_ball fb
            LEFT JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE dp.player_id IS NULL
            """,
        ),
        (
            "All fact_ball.match_id exists in dim_match",
            """
            SELECT COUNT(DISTINCT fb.match_id)
            FROM fact_ball fb
            LEFT JOIN dim_match dm ON fb.match_id = dm.match_id
            WHERE dm.match_id IS NULL
            """,
        ),
        (
            "All ipl_2026_squads.player_id exists in dim_player (mapped players)",
            """
            SELECT COUNT(*)
            FROM ipl_2026_squads sq
            LEFT JOIN dim_player dp ON sq.player_id = dp.player_id
            WHERE sq.player_id IS NOT NULL AND dp.player_id IS NULL
            """,
        ),
    ]

    for description, query in checks:
        try:
            result = conn.execute(query).fetchone()
            if result[0] == 0:
                print_pass(description)
                passes += 1
            else:
                print_warn(f"{description} - {result[0]} orphaned records")
                passes += 1  # Warnings still count as passes
        except duckdb.Error as e:
            print_fail(f"Error checking '{description}': {e}")
            fails += 1

    return passes, fails


def validate_data_quality(conn: duckdb.DuckDBPyConnection) -> Tuple[int, int]:
    """Check data quality metrics."""
    print("\n4. Validating Data Quality...")

    passes = 0
    fails = 0

    checks = [
        (
            "IPL matches count",
            """
            SELECT COUNT(DISTINCT dm.match_id)
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
            """,
            1000,
            ">=",
        ),
        (
            "Ball records count",
            "SELECT COUNT(*) FROM fact_ball",
            2000000,
            ">=",
        ),
        (
            "Players in squads",
            "SELECT COUNT(*) FROM ipl_2026_squads",
            200,
            ">=",
        ),
        (
            "Bowler classifications",
            "SELECT COUNT(*) FROM dim_bowler_classification",
            250,
            ">=",
        ),
        (
            "Franchise aliases",
            "SELECT COUNT(*) FROM dim_franchise_alias",
            3,
            ">=",
        ),
        (
            "All 10 IPL teams in squads",
            "SELECT COUNT(DISTINCT team_name) FROM ipl_2026_squads",
            10,
            "==",
        ),
    ]

    for description, query, expected, operator in checks:
        try:
            result = conn.execute(query).fetchone()[0]
            if operator == ">=" and result >= expected:
                print_pass(f"{description}: {result:,} (expected >= {expected:,})")
                passes += 1
            elif operator == "==" and result == expected:
                print_pass(f"{description}: {result:,} (expected == {expected:,})")
                passes += 1
            else:
                print_fail(f"{description}: {result:,} (expected {operator} {expected:,})")
                fails += 1
        except duckdb.Error as e:
            print_fail(f"Error checking '{description}': {e}")
            fails += 1

    return passes, fails


def validate_bowling_coverage(conn: duckdb.DuckDBPyConnection) -> Tuple[int, int]:
    """Check bowling style classification coverage."""
    print("\n5. Validating Bowling Style Coverage...")

    passes = 0
    fails = 0

    try:
        result = conn.execute("""
            SELECT bowler_type, SUM(balls) as balls
            FROM analytics_ipl_batter_vs_bowler_type
            GROUP BY bowler_type
            ORDER BY balls DESC
        """).fetchall()

        total_balls = sum(r[1] for r in result)
        unknown_balls = sum(r[1] for r in result if r[0] == "Unknown")
        coverage = (total_balls - unknown_balls) / total_balls * 100

        print("  Bowling style distribution:")
        for btype, balls in result:
            pct = balls / total_balls * 100
            print(f"    - {btype}: {balls:,} balls ({pct:.1f}%)")

        if coverage >= 95:
            print_pass(f"Bowling style coverage: {coverage:.1f}%")
            passes += 1
        else:
            print_warn(f"Bowling style coverage below 95%: {coverage:.1f}%")
            passes += 1

    except duckdb.Error as e:
        print_fail(f"Error checking bowling coverage: {e}")
        fails += 1

    return passes, fails


def main() -> int:
    """Main validation entry point."""
    print("=" * 60)
    print("Cricket Playbook - Schema Validation")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"\n{RED}ERROR: Database not found at {DB_PATH}{NC}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    total_passes = 0
    total_fails = 0

    # Run all validations
    p, f = validate_tables(conn)
    total_passes += p
    total_fails += f

    p, f = validate_views(conn)
    total_passes += p
    total_fails += f

    p, f = validate_referential_integrity(conn)
    total_passes += p
    total_fails += f

    p, f = validate_data_quality(conn)
    total_passes += p
    total_fails += f

    p, f = validate_bowling_coverage(conn)
    total_passes += p
    total_fails += f

    conn.close()

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"  Total Passes: {total_passes}")
    print(f"  Total Fails:  {total_fails}")

    if total_fails == 0:
        print(f"\n{GREEN}All validations passed!{NC}")
        return 0
    else:
        print(f"\n{RED}{total_fails} validations failed.{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
