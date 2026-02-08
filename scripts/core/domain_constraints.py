"""
Domain Constraints for Cricket Data
====================================
Enforces realistic value ranges for cricket metrics.

Owner: Brock Purdy (Data Pipeline)
Tickets: TKT-133 (CHECK constraints), TKT-135 (Domain validation)
EPIC: EPIC-014 (Foundation Fortification)

This module provides:
1. SQL CHECK constraints for DuckDB schema
2. Python validation functions for data pipeline
3. Integration with threshold_loader.py for centralized config
"""

import logging
from typing import Any, Dict, List, Optional

import duckdb

from scripts.utils.threshold_loader import get_threshold

logger = logging.getLogger(__name__)


# =============================================================================
# SQL CHECK CONSTRAINTS
# These are added to DuckDB tables after creation
# =============================================================================


def get_check_constraints() -> Dict[str, List[str]]:
    """
    Return CHECK constraint SQL statements organized by table.

    Note: DuckDB supports CHECK constraints but they must be added
    during table creation or via ALTER TABLE ADD CONSTRAINT.
    """

    # Load thresholds from config
    sr_max = get_threshold("validation.strike_rate.error_max", 500)
    eco_max = get_threshold("validation.economy.error_max", 30)
    pos_max = get_threshold("validation.batting_position.max", 11)
    over_max = get_threshold("validation.over_number.max", 19)

    constraints = {
        "fact_ball": [
            # Runs cannot be negative
            "CHECK (runs_batter >= 0)",
            "CHECK (runs_extras >= 0)",
            "CHECK (runs_total >= 0)",
            # Over number valid for T20 (0-indexed: 0-19)
            f"CHECK (over_number >= 0 AND over_number <= {over_max})",
            # Ball number within over (0-5 for legal, can exceed with wides/no-balls)
            "CHECK (ball_number >= 0 AND ball_number <= 9)",
            # Batting position valid
            f"CHECK (batter_batting_position >= 1 AND batter_batting_position <= {pos_max})",
            # Wickets binary
            "CHECK (is_wicket IN (0, 1))",
        ],
        "dim_player": [
            # Player names not empty
            "CHECK (LENGTH(player_name) > 0)",
        ],
        "dim_match": [
            # Valid match outcomes
            "CHECK (winner IS NULL OR LENGTH(winner) > 0)",
            # Margin values non-negative when present
            "CHECK (margin_runs IS NULL OR margin_runs >= 0)",
            "CHECK (margin_wickets IS NULL OR (margin_wickets >= 0 AND margin_wickets <= 10))",
        ],
        "fact_player_match_performance": [
            # Batting stats non-negative
            "CHECK (runs_scored IS NULL OR runs_scored >= 0)",
            "CHECK (balls_faced IS NULL OR balls_faced >= 0)",
            "CHECK (fours IS NULL OR fours >= 0)",
            "CHECK (sixes IS NULL OR sixes >= 0)",
            # Bowling stats non-negative
            "CHECK (wickets_taken IS NULL OR (wickets_taken >= 0 AND wickets_taken <= 10))",
            "CHECK (runs_conceded IS NULL OR runs_conceded >= 0)",
            "CHECK (overs_bowled IS NULL OR overs_bowled >= 0)",
            # Strike rate bounds (if calculated)
            f"CHECK (strike_rate IS NULL OR (strike_rate >= 0 AND strike_rate <= {sr_max}))",
            # Economy bounds (if calculated)
            f"CHECK (economy IS NULL OR (economy >= 0 AND economy <= {eco_max}))",
        ],
    }

    return constraints


def apply_constraints_to_db(db_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Apply CHECK constraints to existing DuckDB database.

    Args:
        db_path: Path to DuckDB database file
        dry_run: If True, only print SQL without executing

    Returns:
        Dict with results: {applied: [...], skipped: [...], errors: [...]}
    """
    results = {"applied": [], "skipped": [], "errors": []}
    constraints = get_check_constraints()

    conn = duckdb.connect(db_path)

    try:
        for table_name, table_constraints in constraints.items():
            # Check if table exists
            table_exists = (
                conn.execute(
                    f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
                ).fetchone()[0]
                > 0
            )

            if not table_exists:
                results["skipped"].append(f"{table_name}: table does not exist")
                continue

            for i, constraint_sql in enumerate(table_constraints):
                constraint_name = f"chk_{table_name}_{i}"
                full_sql = (
                    f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} {constraint_sql}"
                )

                if dry_run:
                    logger.info(f"[DRY RUN] {full_sql}")
                    results["applied"].append(f"{constraint_name}: {constraint_sql}")
                else:
                    try:
                        conn.execute(full_sql)
                        results["applied"].append(f"{constraint_name}: {constraint_sql}")
                        logger.info(f"Applied: {constraint_name}")
                    except duckdb.ConstraintException as e:
                        # Constraint already exists or data violates it
                        results["errors"].append(f"{constraint_name}: {str(e)}")
                        logger.warning(f"Failed to apply {constraint_name}: {e}")
                    except Exception as e:
                        results["errors"].append(f"{constraint_name}: {str(e)}")
                        logger.error(f"Error applying {constraint_name}: {e}")

    finally:
        conn.close()

    return results


# =============================================================================
# PYTHON VALIDATION FUNCTIONS
# For validating data before insertion (TKT-135)
# =============================================================================


class ValidationResult:
    """Result of a validation check."""

    def __init__(self, field: str, value: Any, valid: bool, level: str, message: str):
        self.field = field
        self.value = value
        self.valid = valid
        self.level = level  # "error", "warning", "info"
        self.message = message

    def __repr__(self):
        status = "PASS" if self.valid else self.level.upper()
        return f"[{status}] {self.field}: {self.message}"


def validate_strike_rate(sr: Optional[float], context: str = "") -> ValidationResult:
    """Validate strike rate is within realistic bounds."""
    if sr is None:
        return ValidationResult("strike_rate", sr, True, "info", "No value provided")

    warning_max = get_threshold("validation.strike_rate.warning_max", 300)
    error_max = get_threshold("validation.strike_rate.error_max", 500)

    if sr < 0:
        return ValidationResult(
            "strike_rate", sr, False, "error", f"Negative strike rate: {sr} {context}"
        )
    elif sr > error_max:
        return ValidationResult(
            "strike_rate",
            sr,
            False,
            "error",
            f"Impossible strike rate: {sr} > {error_max} {context}",
        )
    elif sr > warning_max:
        return ValidationResult(
            "strike_rate",
            sr,
            True,
            "warning",
            f"Unusually high strike rate: {sr} > {warning_max} {context}",
        )

    return ValidationResult("strike_rate", sr, True, "info", f"Valid: {sr}")


def validate_economy(eco: Optional[float], context: str = "") -> ValidationResult:
    """Validate economy rate is within realistic bounds."""
    if eco is None:
        return ValidationResult("economy", eco, True, "info", "No value provided")

    warning_max = get_threshold("validation.economy.warning_max", 20)
    error_max = get_threshold("validation.economy.error_max", 30)

    if eco < 0:
        return ValidationResult(
            "economy", eco, False, "error", f"Negative economy: {eco} {context}"
        )
    elif eco > error_max:
        return ValidationResult(
            "economy", eco, False, "error", f"Impossible economy: {eco} > {error_max} {context}"
        )
    elif eco > warning_max:
        return ValidationResult(
            "economy",
            eco,
            True,
            "warning",
            f"Unusually high economy: {eco} > {warning_max} {context}",
        )

    return ValidationResult("economy", eco, True, "info", f"Valid: {eco}")


def validate_batting_position(pos: Optional[int], context: str = "") -> ValidationResult:
    """Validate batting position is 1-11."""
    if pos is None:
        return ValidationResult("batting_position", pos, True, "info", "No value provided")

    min_pos = get_threshold("validation.batting_position.min", 1)
    max_pos = get_threshold("validation.batting_position.max", 11)

    if pos < min_pos or pos > max_pos:
        return ValidationResult(
            "batting_position",
            pos,
            False,
            "error",
            f"Invalid batting position: {pos} (must be {min_pos}-{max_pos}) {context}",
        )

    return ValidationResult("batting_position", pos, True, "info", f"Valid: {pos}")


def validate_over_number(
    over: Optional[int], match_format: str = "T20", context: str = ""
) -> ValidationResult:
    """Validate over number for match format."""
    if over is None:
        return ValidationResult("over_number", over, True, "info", "No value provided")

    max_overs = {
        "T20": 19,  # 0-indexed
        "ODI": 49,
        "TEST": 999,
    }
    max_over = max_overs.get(match_format, 19)

    if over < 0:
        return ValidationResult(
            "over_number", over, False, "error", f"Negative over number: {over} {context}"
        )
    elif over > max_over:
        return ValidationResult(
            "over_number",
            over,
            False,
            "error",
            f"Over {over} exceeds {match_format} limit ({max_over}) {context}",
        )

    return ValidationResult("over_number", over, True, "info", f"Valid: {over}")


def validate_wickets(wickets: Optional[int], context: str = "") -> ValidationResult:
    """Validate wickets count."""
    if wickets is None:
        return ValidationResult("wickets", wickets, True, "info", "No value provided")

    max_wickets = get_threshold("validation.wickets.max", 10)

    if wickets < 0:
        return ValidationResult(
            "wickets", wickets, False, "error", f"Negative wickets: {wickets} {context}"
        )
    elif wickets > max_wickets:
        return ValidationResult(
            "wickets",
            wickets,
            False,
            "error",
            f"Wickets {wickets} exceeds max ({max_wickets}) {context}",
        )

    return ValidationResult("wickets", wickets, True, "info", f"Valid: {wickets}")


def validate_ball_record(ball: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validate all fields in a ball-by-ball record.

    Args:
        ball: Dictionary with ball data

    Returns:
        List of ValidationResult objects
    """
    results = []
    context = f"(match: {ball.get('match_id', 'unknown')}, over: {ball.get('over_number', '?')})"

    # Validate over number
    results.append(validate_over_number(ball.get("over_number"), "T20", context))

    # Validate batting position
    results.append(validate_batting_position(ball.get("batter_batting_position"), context))

    # Validate runs (basic check)
    runs = ball.get("runs_total")
    if runs is not None and runs < 0:
        results.append(
            ValidationResult("runs_total", runs, False, "error", f"Negative runs: {runs} {context}")
        )

    return results


def validate_player_performance(perf: Dict[str, Any]) -> List[ValidationResult]:
    """
    Validate player match performance record.

    Args:
        perf: Dictionary with performance data

    Returns:
        List of ValidationResult objects
    """
    results = []
    context = (
        f"(player: {perf.get('player_id', 'unknown')}, match: {perf.get('match_id', 'unknown')})"
    )

    # Validate strike rate
    results.append(validate_strike_rate(perf.get("strike_rate"), context))

    # Validate economy
    results.append(validate_economy(perf.get("economy"), context))

    # Validate wickets
    results.append(validate_wickets(perf.get("wickets_taken"), context))

    return results


# =============================================================================
# SUMMARY FUNCTIONS
# =============================================================================


def run_validation_report(db_path: str) -> Dict[str, Any]:
    """
    Run validation checks on existing database and return report.

    Args:
        db_path: Path to DuckDB database

    Returns:
        Dict with validation summary
    """
    conn = duckdb.connect(db_path, read_only=True)
    report = {"errors": [], "warnings": [], "stats": {}}

    try:
        # Check for impossible strike rates
        sr_max = get_threshold("validation.strike_rate.error_max", 500)
        result = conn.execute(f"""
            SELECT COUNT(*) FROM fact_player_match_performance
            WHERE strike_rate > {sr_max}
        """).fetchone()[0]
        if result > 0:
            report["errors"].append(f"{result} records with strike_rate > {sr_max}")
        report["stats"]["invalid_sr_count"] = result

        # Check for impossible economies
        eco_max = get_threshold("validation.economy.error_max", 30)
        result = conn.execute(f"""
            SELECT COUNT(*) FROM fact_player_match_performance
            WHERE economy > {eco_max}
        """).fetchone()[0]
        if result > 0:
            report["errors"].append(f"{result} records with economy > {eco_max}")
        report["stats"]["invalid_eco_count"] = result

        # Check for invalid over numbers
        result = conn.execute("""
            SELECT COUNT(*) FROM fact_ball
            WHERE over_number < 0 OR over_number > 19
        """).fetchone()[0]
        if result > 0:
            report["errors"].append(f"{result} balls with invalid over_number")
        report["stats"]["invalid_over_count"] = result

        # Check for invalid batting positions
        result = conn.execute("""
            SELECT COUNT(*) FROM fact_ball
            WHERE batter_batting_position < 1 OR batter_batting_position > 11
        """).fetchone()[0]
        if result > 0:
            report["errors"].append(f"{result} balls with invalid batting_position")
        report["stats"]["invalid_position_count"] = result

        # Summary
        total_errors = len(report["errors"])
        report["valid"] = total_errors == 0
        report["summary"] = (
            f"Found {total_errors} validation issues"
            if total_errors > 0
            else "All validations passed"
        )

    finally:
        conn.close()

    return report


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        db_path = sys.argv[1]

        print("=" * 60)
        print("Domain Constraints Validation Report")
        print("=" * 60)

        # Run validation
        report = run_validation_report(db_path)

        print(f"\nStatus: {'PASS' if report['valid'] else 'FAIL'}")
        print(f"Summary: {report['summary']}")

        if report["errors"]:
            print("\nErrors:")
            for err in report["errors"]:
                print(f"  - {err}")

        print("\nStats:")
        for key, value in report["stats"].items():
            print(f"  {key}: {value}")
    else:
        print("Usage: python domain_constraints.py <path_to_duckdb>")
        print("\nAvailable CHECK constraints:")
        for table, constraints in get_check_constraints().items():
            print(f"\n{table}:")
            for c in constraints:
                print(f"  {c}")
