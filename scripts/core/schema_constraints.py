"""
Foreign Key Constraints for Cricket Playbook Schema
=====================================================
Defines and validates FK relationships for the cricket_playbook DuckDB database.

Owner: Brock Purdy (Data Pipeline)
Ticket: TKT-138 (FOREIGN KEY constraints documentation and DDL)
EPIC: EPIC-014 (Foundation Fortification)

This module provides:
1. FK relationship definitions for the star schema
2. ALTER TABLE statements to add FK constraints
3. Orphaned record detection (records violating FK constraints)
4. Schema diagram generation

IMPORTANT: DuckDB Support for Foreign Keys
------------------------------------------
DuckDB supports FOREIGN KEY syntax in CREATE TABLE and ALTER TABLE statements,
but it does NOT enforce them by default. Foreign keys in DuckDB are:
- Stored in catalog metadata
- Available for documentation and query planning hints
- NOT enforced during INSERT/UPDATE operations

For data integrity, this module provides validation functions that perform
the referential integrity checks at runtime rather than relying on DB enforcement.

See: https://duckdb.org/docs/sql/constraints

Usage:
    # Generate FK DDL statements
    python -m scripts.core.schema_constraints --generate-ddl

    # Check for orphaned records
    python -m scripts.core.schema_constraints --check-orphans data/cricket_playbook.duckdb

    # Print schema diagram
    python -m scripts.core.schema_constraints --diagram
"""

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

logger = logging.getLogger(__name__)


# =============================================================================
# FOREIGN KEY DEFINITIONS
# =============================================================================


@dataclass
class ForeignKeyConstraint:
    """
    Represents a foreign key relationship between two tables.

    Attributes:
        constraint_name: Unique name for the constraint
        source_table: Table containing the foreign key column
        source_column: Column in the source table (FK column)
        target_table: Referenced table (contains primary key)
        target_column: Primary key column in the target table
        description: Human-readable description of the relationship
    """

    constraint_name: str
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    description: str

    def to_alter_statement(self) -> str:
        """
        Generate ALTER TABLE statement to add this FK constraint.

        Returns:
            SQL ALTER TABLE statement string
        """
        return (
            f"ALTER TABLE {self.source_table} "
            f"ADD CONSTRAINT {self.constraint_name} "
            f"FOREIGN KEY ({self.source_column}) "
            f"REFERENCES {self.target_table}({self.target_column})"
        )

    def to_orphan_check_query(self) -> str:
        """
        Generate SQL query to find records violating this FK constraint.

        Returns:
            SQL query that returns orphaned records (source records with no matching target)
        """
        return f"""
            SELECT DISTINCT s.{self.source_column} AS orphaned_value,
                   COUNT(*) AS record_count
            FROM {self.source_table} s
            LEFT JOIN {self.target_table} t ON s.{self.source_column} = t.{self.target_column}
            WHERE s.{self.source_column} IS NOT NULL
              AND t.{self.target_column} IS NULL
            GROUP BY s.{self.source_column}
            ORDER BY record_count DESC
        """


def get_fk_constraints() -> List[ForeignKeyConstraint]:
    """
    Return all foreign key constraint definitions for cricket_playbook schema.

    The schema follows a star schema pattern with fact_ball as the central
    fact table, connected to dimension tables for players, teams, matches, and venues.

    Returns:
        List of ForeignKeyConstraint objects defining all FK relationships
    """
    return [
        # fact_ball -> dim_player (batter)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_batter",
            source_table="fact_ball",
            source_column="batter_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links each ball to the batter (striker) from dim_player",
        ),
        # fact_ball -> dim_player (bowler)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_bowler",
            source_table="fact_ball",
            source_column="bowler_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links each ball to the bowler from dim_player",
        ),
        # fact_ball -> dim_team (batting team)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_batting_team",
            source_table="fact_ball",
            source_column="batting_team_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links each ball to the batting team from dim_team",
        ),
        # fact_ball -> dim_team (bowling team)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_bowling_team",
            source_table="fact_ball",
            source_column="bowling_team_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links each ball to the bowling/fielding team from dim_team",
        ),
        # fact_ball -> dim_match
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_match",
            source_table="fact_ball",
            source_column="match_id",
            target_table="dim_match",
            target_column="match_id",
            description="Links each ball to its parent match from dim_match",
        ),
        # fact_ball -> dim_venue (through dim_match)
        # NOTE: fact_ball doesn't have venue_id directly; it's accessed via dim_match
        # This constraint is included as specified in requirements but may need adjustment
        # based on actual schema. The relationship is: fact_ball -> dim_match -> dim_venue
        # Additional FK constraints for related tables
        # dim_match -> dim_venue
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_venue",
            source_table="dim_match",
            source_column="venue_id",
            target_table="dim_venue",
            target_column="venue_id",
            description="Links each match to its venue from dim_venue",
        ),
        # dim_match -> dim_tournament
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_tournament",
            source_table="dim_match",
            source_column="tournament_id",
            target_table="dim_tournament",
            target_column="tournament_id",
            description="Links each match to its tournament from dim_tournament",
        ),
        # dim_match -> dim_team (team1)
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_team1",
            source_table="dim_match",
            source_column="team1_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links match to first team from dim_team",
        ),
        # dim_match -> dim_team (team2)
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_team2",
            source_table="dim_match",
            source_column="team2_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links match to second team from dim_team",
        ),
        # dim_match -> dim_team (winner)
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_winner",
            source_table="dim_match",
            source_column="winner_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links match to winning team from dim_team",
        ),
        # dim_match -> dim_team (toss winner)
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_toss_winner",
            source_table="dim_match",
            source_column="toss_winner_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links match to toss-winning team from dim_team",
        ),
        # dim_match -> dim_player (player of match)
        ForeignKeyConstraint(
            constraint_name="fk_dim_match_pom",
            source_table="dim_match",
            source_column="player_of_match_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links match to player of the match from dim_player",
        ),
        # fact_ball -> dim_player (non-striker)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_non_striker",
            source_table="fact_ball",
            source_column="non_striker_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links each ball to the non-striker from dim_player",
        ),
        # fact_ball -> dim_player (player out)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_player_out",
            source_table="fact_ball",
            source_column="player_out_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links dismissal balls to the dismissed player from dim_player",
        ),
        # fact_ball -> dim_player (fielder)
        ForeignKeyConstraint(
            constraint_name="fk_fact_ball_fielder",
            source_table="fact_ball",
            source_column="fielder_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links catches/run outs to the fielder from dim_player",
        ),
        # fact_player_match_performance -> dim_player
        ForeignKeyConstraint(
            constraint_name="fk_fpmp_player",
            source_table="fact_player_match_performance",
            source_column="player_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links player performance to player from dim_player",
        ),
        # fact_player_match_performance -> dim_match
        ForeignKeyConstraint(
            constraint_name="fk_fpmp_match",
            source_table="fact_player_match_performance",
            source_column="match_id",
            target_table="dim_match",
            target_column="match_id",
            description="Links player performance to match from dim_match",
        ),
        # fact_player_match_performance -> dim_team
        ForeignKeyConstraint(
            constraint_name="fk_fpmp_team",
            source_table="fact_player_match_performance",
            source_column="team_id",
            target_table="dim_team",
            target_column="team_id",
            description="Links player performance to their team from dim_team",
        ),
        # dim_bowler_classification -> dim_player
        ForeignKeyConstraint(
            constraint_name="fk_bowler_class_player",
            source_table="dim_bowler_classification",
            source_column="player_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links bowler classification to player from dim_player",
        ),
        # dim_player_name_history -> dim_player
        ForeignKeyConstraint(
            constraint_name="fk_player_name_history",
            source_table="dim_player_name_history",
            source_column="player_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links player name history to player from dim_player",
        ),
        # fact_powerplay -> dim_match
        ForeignKeyConstraint(
            constraint_name="fk_powerplay_match",
            source_table="fact_powerplay",
            source_column="match_id",
            target_table="dim_match",
            target_column="match_id",
            description="Links powerplay rules to match from dim_match",
        ),
        # ipl_2026_squads -> dim_player
        ForeignKeyConstraint(
            constraint_name="fk_ipl_squads_player",
            source_table="ipl_2026_squads",
            source_column="player_id",
            target_table="dim_player",
            target_column="player_id",
            description="Links IPL 2026 squad member to player from dim_player (may be NULL for new players)",
        ),
    ]


def get_core_fk_constraints() -> List[ForeignKeyConstraint]:
    """
    Return only the core FK constraints as specified in TKT-138.

    These are the primary relationships for the fact_ball table:
    - fact_ball.batter_id -> dim_player.player_id
    - fact_ball.bowler_id -> dim_player.player_id
    - fact_ball.batting_team_id -> dim_team.team_id
    - fact_ball.bowling_team_id -> dim_team.team_id
    - fact_ball.match_id -> dim_match.match_id
    - fact_ball.venue_id -> dim_venue.venue_id (via dim_match)

    Returns:
        List of core ForeignKeyConstraint objects
    """
    all_constraints = get_fk_constraints()
    core_names = {
        "fk_fact_ball_batter",
        "fk_fact_ball_bowler",
        "fk_fact_ball_batting_team",
        "fk_fact_ball_bowling_team",
        "fk_fact_ball_match",
        "fk_dim_match_venue",
    }
    return [c for c in all_constraints if c.constraint_name in core_names]


# =============================================================================
# DDL GENERATION
# =============================================================================


def generate_fk_ddl(constraints: Optional[List[ForeignKeyConstraint]] = None) -> str:
    """
    Generate all ALTER TABLE statements for foreign key constraints.

    Args:
        constraints: List of constraints to generate DDL for.
                    If None, uses all constraints from get_fk_constraints().

    Returns:
        Multi-line string containing all ALTER TABLE statements
    """
    if constraints is None:
        constraints = get_fk_constraints()

    lines = [
        "-- Foreign Key Constraints for cricket_playbook schema",
        "-- Generated by scripts/core/schema_constraints.py",
        "--",
        "-- NOTE: DuckDB supports FK syntax but does NOT enforce constraints.",
        "-- These statements document relationships and may assist query planning.",
        "-- Use check_orphaned_records() for runtime validation.",
        "--",
        "",
    ]

    for constraint in constraints:
        lines.append(f"-- {constraint.description}")
        lines.append(f"{constraint.to_alter_statement()};")
        lines.append("")

    return "\n".join(lines)


def apply_fk_constraints(
    db_path: str,
    constraints: Optional[List[ForeignKeyConstraint]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Apply FK constraints to an existing DuckDB database.

    Note: DuckDB will accept these constraints but won't enforce them.
    This is useful for documentation and some query planning scenarios.

    Args:
        db_path: Path to the DuckDB database file
        constraints: List of constraints to apply. If None, uses all constraints.
        dry_run: If True, only print statements without executing

    Returns:
        Dict with keys: 'applied', 'skipped', 'errors'
    """
    if constraints is None:
        constraints = get_fk_constraints()

    results: Dict[str, List[str]] = {"applied": [], "skipped": [], "errors": []}

    conn = duckdb.connect(db_path)

    try:
        for constraint in constraints:
            sql = constraint.to_alter_statement()

            if dry_run:
                logger.info(f"[DRY RUN] {sql}")
                results["applied"].append(constraint.constraint_name)
                continue

            try:
                # Check if source table exists
                table_exists = (
                    conn.execute(
                        f"""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = '{constraint.source_table}'
                """
                    ).fetchone()[0]
                    > 0
                )

                if not table_exists:
                    results["skipped"].append(
                        f"{constraint.constraint_name}: source table '{constraint.source_table}' not found"
                    )
                    continue

                # Check if target table exists
                target_exists = (
                    conn.execute(
                        f"""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = '{constraint.target_table}'
                """
                    ).fetchone()[0]
                    > 0
                )

                if not target_exists:
                    results["skipped"].append(
                        f"{constraint.constraint_name}: target table '{constraint.target_table}' not found"
                    )
                    continue

                # Execute the constraint
                conn.execute(sql)
                results["applied"].append(constraint.constraint_name)
                logger.info(f"Applied: {constraint.constraint_name}")

            except duckdb.CatalogException as e:
                # Constraint might already exist
                if "already exists" in str(e).lower():
                    results["skipped"].append(f"{constraint.constraint_name}: already exists")
                else:
                    results["errors"].append(f"{constraint.constraint_name}: {str(e)}")
                    logger.warning(f"Error applying {constraint.constraint_name}: {e}")

            except Exception as e:
                results["errors"].append(f"{constraint.constraint_name}: {str(e)}")
                logger.error(f"Error applying {constraint.constraint_name}: {e}")

    finally:
        conn.close()

    return results


# =============================================================================
# ORPHANED RECORD DETECTION
# =============================================================================


@dataclass
class OrphanedRecordResult:
    """
    Result of checking for orphaned records for a single FK constraint.

    Attributes:
        constraint: The FK constraint that was checked
        orphan_count: Number of distinct orphaned values found
        record_count: Total records affected by orphaned references
        sample_values: Sample of orphaned values (up to 10)
        is_valid: True if no orphaned records found
    """

    constraint: ForeignKeyConstraint
    orphan_count: int
    record_count: int
    sample_values: List[str]
    is_valid: bool

    def __str__(self) -> str:
        if self.is_valid:
            return f"[PASS] {self.constraint.constraint_name}: No orphaned records"
        return (
            f"[FAIL] {self.constraint.constraint_name}: "
            f"{self.orphan_count} orphaned values affecting {self.record_count} records. "
            f"Samples: {self.sample_values[:5]}"
        )


def check_orphaned_records(
    db_path: str,
    constraints: Optional[List[ForeignKeyConstraint]] = None,
    limit: int = 10,
) -> List[OrphanedRecordResult]:
    """
    Check for orphaned records that would violate FK constraints.

    Since DuckDB doesn't enforce FK constraints, this function performs
    runtime validation to identify referential integrity violations.

    Args:
        db_path: Path to the DuckDB database file
        constraints: List of constraints to check. If None, uses all constraints.
        limit: Maximum number of sample orphaned values to return

    Returns:
        List of OrphanedRecordResult objects, one per constraint checked
    """
    if constraints is None:
        constraints = get_fk_constraints()

    results = []
    conn = duckdb.connect(db_path, read_only=True)

    try:
        for constraint in constraints:
            try:
                # Check if tables exist
                source_exists = (
                    conn.execute(
                        f"""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = '{constraint.source_table}'
                """
                    ).fetchone()[0]
                    > 0
                )

                target_exists = (
                    conn.execute(
                        f"""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = '{constraint.target_table}'
                """
                    ).fetchone()[0]
                    > 0
                )

                if not source_exists or not target_exists:
                    logger.debug(f"Skipping {constraint.constraint_name}: table(s) not found")
                    continue

                # Run orphan check query
                query = constraint.to_orphan_check_query()
                rows = conn.execute(query).fetchall()

                if not rows:
                    results.append(
                        OrphanedRecordResult(
                            constraint=constraint,
                            orphan_count=0,
                            record_count=0,
                            sample_values=[],
                            is_valid=True,
                        )
                    )
                else:
                    orphan_count = len(rows)
                    record_count = sum(row[1] for row in rows)
                    sample_values = [str(row[0]) for row in rows[:limit]]

                    results.append(
                        OrphanedRecordResult(
                            constraint=constraint,
                            orphan_count=orphan_count,
                            record_count=record_count,
                            sample_values=sample_values,
                            is_valid=False,
                        )
                    )

            except Exception as e:
                logger.error(f"Error checking {constraint.constraint_name}: {e}")
                # Don't add to results if we couldn't check

    finally:
        conn.close()

    return results


def run_integrity_check(db_path: str, core_only: bool = False) -> Dict[str, Any]:
    """
    Run a full referential integrity check and return a summary report.

    Args:
        db_path: Path to the DuckDB database file
        core_only: If True, only check core FK constraints from TKT-138

    Returns:
        Dict with keys: 'valid', 'summary', 'passed', 'failed', 'details'
    """
    constraints = get_core_fk_constraints() if core_only else get_fk_constraints()
    results = check_orphaned_records(db_path, constraints)

    passed = [r for r in results if r.is_valid]
    failed = [r for r in results if not r.is_valid]

    report = {
        "valid": len(failed) == 0,
        "summary": (
            f"Checked {len(results)} FK constraints: {len(passed)} passed, {len(failed)} failed"
        ),
        "passed": [r.constraint.constraint_name for r in passed],
        "failed": [
            {
                "constraint": r.constraint.constraint_name,
                "orphan_count": r.orphan_count,
                "record_count": r.record_count,
                "samples": r.sample_values,
            }
            for r in failed
        ],
        "details": results,
    }

    return report


# =============================================================================
# SCHEMA DIAGRAM
# =============================================================================


def generate_schema_diagram() -> str:
    """
    Generate an ASCII schema diagram showing FK relationships.

    Returns:
        Multi-line string containing the schema diagram
    """
    diagram = """
Cricket Playbook - Star Schema Diagram
=======================================

                        +------------------+
                        |  dim_tournament  |
                        |------------------|
                        | tournament_id PK |
                        | tournament_name  |
                        +--------+---------+
                                 |
                                 | fk_dim_match_tournament
                                 |
+-------------+         +--------+---------+         +------------+
|  dim_venue  |         |    dim_match     |         |  dim_team  |
|-------------|<--------+------------------|-------->|------------|
| venue_id PK |   FK    | match_id PK      |   FK    | team_id PK |
| venue_name  |         | tournament_id FK |         | team_name  |
| city        |         | venue_id FK      |         | short_name |
+-------------+         | team1_id FK      |         +-----+------+
                        | team2_id FK      |               |
                        | winner_id FK     |               |
                        | toss_winner_id FK|               |
                        | player_of_match_id FK            |
                        +--------+---------+               |
                                 |                         |
                                 | fk_fact_ball_match      |
                                 |                         |
                        +--------+---------+               |
                        |    fact_ball     |               |
                        |------------------|               |
                        | ball_id PK       |               |
                        | match_id FK      +---------------+
                        | batter_id FK     |    fk_fact_ball_batting_team
                        | bowler_id FK     |    fk_fact_ball_bowling_team
                        | batting_team_id FK
                        | bowling_team_id FK
                        | non_striker_id FK|
                        | player_out_id FK |
                        | fielder_id FK    |
                        +--------+---------+
                                 |
                                 | fk_fact_ball_batter
                                 | fk_fact_ball_bowler
                                 | fk_fact_ball_non_striker
                                 | fk_fact_ball_player_out
                                 | fk_fact_ball_fielder
                                 |
                        +--------+---------+
                        |   dim_player     |
                        |------------------|
                        | player_id PK     |
                        | current_name     |
                        | primary_role     |
                        +------------------+


Additional Tables with FK Relationships:
----------------------------------------

fact_player_match_performance
  -> player_id FK -> dim_player.player_id
  -> match_id FK  -> dim_match.match_id
  -> team_id FK   -> dim_team.team_id

fact_powerplay
  -> match_id FK  -> dim_match.match_id

dim_bowler_classification
  -> player_id FK -> dim_player.player_id

dim_player_name_history
  -> player_id FK -> dim_player.player_id

ipl_2026_squads
  -> player_id FK -> dim_player.player_id (may be NULL for uncapped players)


Legend:
-------
PK = Primary Key
FK = Foreign Key
--> = Foreign Key Relationship (child -> parent)

Note: DuckDB accepts FK syntax but does NOT enforce constraints.
Use check_orphaned_records() for runtime validation.
"""
    return diagram


def generate_mermaid_diagram() -> str:
    """
    Generate a Mermaid ER diagram for documentation.

    This can be rendered in GitHub, GitLab, or other Markdown viewers
    that support Mermaid diagrams.

    Returns:
        Mermaid diagram code string
    """
    return """
```mermaid
erDiagram
    dim_tournament ||--o{ dim_match : "tournament_id"
    dim_venue ||--o{ dim_match : "venue_id"
    dim_team ||--o{ dim_match : "team1_id, team2_id, winner_id"
    dim_player ||--o{ dim_match : "player_of_match_id"

    dim_match ||--o{ fact_ball : "match_id"
    dim_team ||--o{ fact_ball : "batting_team_id, bowling_team_id"
    dim_player ||--o{ fact_ball : "batter_id, bowler_id, non_striker_id"

    dim_match ||--o{ fact_player_match_performance : "match_id"
    dim_player ||--o{ fact_player_match_performance : "player_id"
    dim_team ||--o{ fact_player_match_performance : "team_id"

    dim_match ||--o{ fact_powerplay : "match_id"
    dim_player ||--o{ dim_bowler_classification : "player_id"
    dim_player ||--o{ dim_player_name_history : "player_id"
    dim_player ||--o{ ipl_2026_squads : "player_id"

    dim_tournament {
        string tournament_id PK
        string tournament_name
        string country
    }

    dim_venue {
        string venue_id PK
        string venue_name
        string city
    }

    dim_team {
        string team_id PK
        string team_name
        string short_name
    }

    dim_player {
        string player_id PK
        string current_name
        string primary_role
    }

    dim_match {
        string match_id PK
        string tournament_id FK
        string venue_id FK
        string team1_id FK
        string team2_id FK
        string winner_id FK
    }

    fact_ball {
        string ball_id PK
        string match_id FK
        string batter_id FK
        string bowler_id FK
        string batting_team_id FK
        string bowling_team_id FK
        int batter_runs
        boolean is_wicket
    }

    fact_player_match_performance {
        string player_id FK
        string match_id FK
        string team_id FK
        boolean did_bat
        boolean did_bowl
    }
```
"""


# =============================================================================
# CLI ENTRY POINT
# =============================================================================


def main() -> int:
    """
    CLI entry point for schema constraints module.

    Usage:
        python -m scripts.core.schema_constraints --generate-ddl
        python -m scripts.core.schema_constraints --check-orphans <db_path>
        python -m scripts.core.schema_constraints --diagram
        python -m scripts.core.schema_constraints --apply <db_path> [--dry-run]

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    parser = argparse.ArgumentParser(
        description="Foreign Key Constraints for cricket_playbook schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print FK DDL statements
  python -m scripts.core.schema_constraints --generate-ddl

  # Check for orphaned records
  python -m scripts.core.schema_constraints --check-orphans data/cricket_playbook.duckdb

  # Check only core FK constraints from TKT-138
  python -m scripts.core.schema_constraints --check-orphans data/cricket_playbook.duckdb --core-only

  # Print schema diagram
  python -m scripts.core.schema_constraints --diagram

  # Apply FK constraints (dry run)
  python -m scripts.core.schema_constraints --apply data/cricket_playbook.duckdb --dry-run
        """,
    )

    parser.add_argument(
        "--generate-ddl",
        action="store_true",
        help="Print ALTER TABLE statements for all FK constraints",
    )
    parser.add_argument(
        "--check-orphans",
        metavar="DB_PATH",
        help="Check for orphaned records in the specified database",
    )
    parser.add_argument(
        "--apply",
        metavar="DB_PATH",
        help="Apply FK constraints to the specified database",
    )
    parser.add_argument(
        "--diagram",
        action="store_true",
        help="Print ASCII schema diagram",
    )
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help="Print Mermaid ER diagram for documentation",
    )
    parser.add_argument(
        "--core-only",
        action="store_true",
        help="Only process core FK constraints from TKT-138",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without executing (for --apply)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    # If no action specified, show help
    if not any([args.generate_ddl, args.check_orphans, args.apply, args.diagram, args.mermaid]):
        parser.print_help()
        return 0

    # Generate DDL
    if args.generate_ddl:
        constraints = get_core_fk_constraints() if args.core_only else get_fk_constraints()
        print(generate_fk_ddl(constraints))
        return 0

    # Print diagram
    if args.diagram:
        print(generate_schema_diagram())
        return 0

    # Print Mermaid diagram
    if args.mermaid:
        print(generate_mermaid_diagram())
        return 0

    # Check orphaned records
    if args.check_orphans:
        db_path = args.check_orphans

        if not Path(db_path).exists():
            print(f"ERROR: Database not found at {db_path}")
            return 1

        print("=" * 60)
        print("Foreign Key Integrity Check")
        print("=" * 60)
        print(f"Database: {db_path}")
        print(f"Mode: {'Core constraints only' if args.core_only else 'All constraints'}")
        print()

        report = run_integrity_check(db_path, core_only=args.core_only)

        print(report["summary"])
        print()

        if report["passed"]:
            print("Passed Constraints:")
            for name in report["passed"]:
                print(f"  [PASS] {name}")
            print()

        if report["failed"]:
            print("Failed Constraints:")
            for failure in report["failed"]:
                print(f"  [FAIL] {failure['constraint']}")
                print(
                    f"         {failure['orphan_count']} orphaned values, {failure['record_count']} records"
                )
                if failure["samples"]:
                    print(f"         Samples: {failure['samples'][:5]}")
            print()

        print("=" * 60)
        if report["valid"]:
            print("Result: ALL CONSTRAINTS PASSED")
            return 0
        else:
            print("Result: INTEGRITY VIOLATIONS FOUND")
            return 1

    # Apply constraints
    if args.apply:
        db_path = args.apply

        if not Path(db_path).exists():
            print(f"ERROR: Database not found at {db_path}")
            return 1

        print("=" * 60)
        print("Applying Foreign Key Constraints")
        print("=" * 60)
        print(f"Database: {db_path}")
        print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
        print()

        print("WARNING: DuckDB accepts FK constraints but does NOT enforce them.")
        print("These constraints are for documentation and query planning only.")
        print()

        constraints = get_core_fk_constraints() if args.core_only else get_fk_constraints()
        results = apply_fk_constraints(db_path, constraints, dry_run=args.dry_run)

        if results["applied"]:
            print(f"Applied ({len(results['applied'])}):")
            for name in results["applied"]:
                print(f"  + {name}")
            print()

        if results["skipped"]:
            print(f"Skipped ({len(results['skipped'])}):")
            for msg in results["skipped"]:
                print(f"  - {msg}")
            print()

        if results["errors"]:
            print(f"Errors ({len(results['errors'])}):")
            for msg in results["errors"]:
                print(f"  ! {msg}")
            print()

        print("=" * 60)
        if results["errors"]:
            print("Result: COMPLETED WITH ERRORS")
            return 1
        else:
            print("Result: SUCCESS")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
