#!/usr/bin/env python3
"""
Great Expectations Data Validation for Cricket Playbook
=======================================================
Owner: Brock Purdy (Data Pipeline)
Ticket: IDEA-006
EPIC: EPIC-014 (Foundation Fortification)

Validates DuckDB tables against expectation suites derived from
domain_constraints.py. Reads tables into pandas and uses GE's
in-memory validation engine.

Usage:
    python scripts/core/ge_validation.py
    python scripts/core/ge_validation.py --db data/cricket_playbook.duckdb
    python scripts/core/ge_validation.py --table fact_ball
    python scripts/core/ge_validation.py --json  # Output as JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb
import great_expectations as gx
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"

# ─────────────────────────────────────────────────────────────
# Expectation Suite Definitions
# Translated from domain_constraints.py CHECK constraints
# ─────────────────────────────────────────────────────────────

SUITES: dict[str, list[dict]] = {
    "fact_ball": [
        {"type": "expect_column_values_to_not_be_null", "column": "match_id"},
        {"type": "expect_column_values_to_not_be_null", "column": "innings"},
        {
            "type": "expect_column_values_to_be_between",
            "column": "over",
            "kwargs": {"min_value": 0, "max_value": 19},
        },
        {
            "type": "expect_column_values_to_be_between",
            "column": "ball",
            "kwargs": {"min_value": 0, "max_value": 20},
        },  # Wides/no-balls extend ball count
        {
            "type": "expect_column_values_to_be_between",
            "column": "batter_runs",
            "kwargs": {"min_value": 0, "max_value": 7},
        },
        {
            "type": "expect_column_values_to_be_between",
            "column": "extra_runs",
            "kwargs": {"min_value": 0, "max_value": 15},
        },  # Wides + overthrows can stack
        {
            "type": "expect_column_values_to_be_between",
            "column": "total_runs",
            "kwargs": {"min_value": 0, "max_value": 20},
        },  # Batter + extras combined
        {
            "type": "expect_column_values_to_be_in_set",
            "column": "is_wicket",
            "kwargs": {"value_set": [True, False, 0, 1]},
        },
        {
            "type": "expect_column_values_to_be_in_set",
            "column": "match_phase",
            "kwargs": {"value_set": ["powerplay", "middle", "death", None]},
        },
    ],
    "dim_player": [
        {"type": "expect_column_values_to_not_be_null", "column": "player_id"},
        {"type": "expect_column_values_to_be_unique", "column": "player_id"},
        {"type": "expect_column_values_to_not_be_null", "column": "current_name"},
        {
            "type": "expect_column_value_lengths_to_be_between",
            "column": "current_name",
            "kwargs": {"min_value": 1},
        },
        {
            "type": "expect_column_values_to_be_between",
            "column": "matches_played",
            "kwargs": {"min_value": 0},
        },
    ],
    "dim_match": [
        {"type": "expect_column_values_to_not_be_null", "column": "match_id"},
        {"type": "expect_column_values_to_be_unique", "column": "match_id"},
        {"type": "expect_column_values_to_not_be_null", "column": "match_date"},
        {"type": "expect_column_values_to_not_be_null", "column": "venue_id"},
    ],
    "dim_team": [
        {"type": "expect_column_values_to_not_be_null", "column": "team_id"},
        {"type": "expect_column_values_to_be_unique", "column": "team_id"},
        {"type": "expect_column_values_to_not_be_null", "column": "team_name"},
        {
            "type": "expect_column_value_lengths_to_be_between",
            "column": "team_name",
            "kwargs": {"min_value": 1},
        },
    ],
    "dim_venue": [
        {"type": "expect_column_values_to_not_be_null", "column": "venue_id"},
        {"type": "expect_column_values_to_be_unique", "column": "venue_id"},
        {"type": "expect_column_values_to_not_be_null", "column": "venue_name"},
    ],
}

# Row count expectations (sanity checks)
ROW_MINIMUMS = {
    "fact_ball": 100_000,
    "dim_player": 1_000,
    "dim_match": 500,
    "dim_team": 10,
    "dim_venue": 10,
}


def get_table_df(db_path: Path, table: str) -> pd.DataFrame:
    """Read a DuckDB table into a pandas DataFrame."""
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        df = con.execute(f"SELECT * FROM {table}").fetchdf()  # noqa: S608
    finally:
        con.close()
    return df


def get_available_tables(db_path: Path) -> list[str]:
    """List all tables in the DuckDB database."""
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        tables = con.execute("SHOW TABLES").fetchdf()["name"].tolist()
    finally:
        con.close()
    return tables


def validate_table(
    table: str, db_path: Path, context: gx.data_context.EphemeralDataContext
) -> dict:
    """Validate a single table against its expectation suite."""
    if table not in SUITES:
        return {"table": table, "status": "SKIPPED", "reason": "No suite defined"}

    df = get_table_df(db_path, table)
    row_count = len(df)

    # Create datasource and asset
    ds_name = f"ds_{table}"
    datasource = context.data_sources.add_pandas(ds_name)
    asset = datasource.add_dataframe_asset(name=f"asset_{table}")
    batch_definition = asset.add_batch_definition_whole_dataframe(f"batch_{table}")
    batch_definition.get_batch(batch_parameters={"dataframe": df})

    # Build expectation suite
    suite = gx.ExpectationSuite(name=f"suite_{table}")

    # Row count minimum check
    if table in ROW_MINIMUMS:
        suite.add_expectation(
            gx.expectations.ExpectTableRowCountToBeBetween(min_value=ROW_MINIMUMS[table])
        )

    # Column-level expectations
    for exp_def in SUITES[table]:
        exp_type = exp_def["type"]
        column = exp_def.get("column")
        kwargs = exp_def.get("kwargs", {})

        # Map string type to GE expectation class
        exp_class = _get_expectation_class(exp_type)
        if exp_class is None:
            continue

        params = {}
        if column:
            params["column"] = column
        params.update(kwargs)
        suite.add_expectation(exp_class(**params))

    suite = context.suites.add(suite)

    # Run validation
    validation_definition = gx.ValidationDefinition(
        name=f"validate_{table}",
        data=batch_definition,
        suite=suite,
    )
    validation_definition = context.validation_definitions.add(validation_definition)
    results = validation_definition.run(batch_parameters={"dataframe": df})

    # Extract results
    passed = results.success
    total_exp = len(results.results)
    success_exp = sum(1 for r in results.results if r.success)
    failed_exp = total_exp - success_exp

    failures = []
    for r in results.results:
        if not r.success:
            col = r.expectation_config.kwargs.get("column", "")
            unexpected = (
                r.result.get("partial_unexpected_list", [])[:5]
                if hasattr(r, "result") and r.result
                else []
            )
            failures.append(
                {
                    "expectation": r.expectation_config.type,
                    "column": col,
                    "details": str(unexpected)[:200],
                }
            )

    return {
        "table": table,
        "status": "PASS" if passed else "FAIL",
        "rows": row_count,
        "expectations": total_exp,
        "successful": success_exp,
        "failed": failed_exp,
        "success_pct": round(success_exp / total_exp * 100, 1) if total_exp else 0,
        "failures": failures,
    }


def _get_expectation_class(type_name: str):
    """Map expectation type string to GE class."""
    mapping = {
        "expect_column_values_to_not_be_null": gx.expectations.ExpectColumnValuesToNotBeNull,
        "expect_column_values_to_be_unique": gx.expectations.ExpectColumnValuesToBeUnique,
        "expect_column_values_to_be_between": gx.expectations.ExpectColumnValuesToBeBetween,
        "expect_column_values_to_be_in_set": gx.expectations.ExpectColumnValuesToBeInSet,
        "expect_column_value_lengths_to_be_between": gx.expectations.ExpectColumnValueLengthsToBeBetween,
    }
    return mapping.get(type_name)


def run_validation(
    db_path: Path, tables: list[str] | None = None, output_json: bool = False
) -> int:
    """Run GE validation on specified tables. Returns 0 if all pass."""
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return 1

    available = get_available_tables(db_path)
    target_tables = tables if tables else [t for t in SUITES if t in available]

    context = gx.get_context(mode="ephemeral")
    results = []
    all_pass = True

    if not output_json:
        print("=" * 65)
        print("Cricket Playbook — Great Expectations Validation")
        print("Owner: Brock Purdy | Ticket: IDEA-006")
        print(f"Database: {db_path.name}")
        print("=" * 65)
        print()

    for table in target_tables:
        if not output_json:
            print(f"  Validating {table}...", end=" ", flush=True)
        result = validate_table(table, db_path, context)
        results.append(result)
        if result["status"] == "FAIL":
            all_pass = False
        if not output_json:
            icon = (
                "PASS"
                if result["status"] == "PASS"
                else "SKIP"
                if result["status"] == "SKIPPED"
                else "FAIL"
            )
            detail = (
                f"{result.get('rows', 0):,} rows, {result.get('expectations', 0)} checks"
                if result["status"] != "SKIPPED"
                else result.get("reason", "")
            )
            print(f"[{icon}] {detail}")
            for f in result.get("failures", []):
                print(f"         FAIL: {f['expectation']} on '{f['column']}'")

    if output_json:
        print(json.dumps({"success": all_pass, "tables": results}, indent=2))
    else:
        print()
        passed_count = sum(1 for r in results if r["status"] == "PASS")
        total = len(results)
        print("=" * 65)
        print(f"  Result: {passed_count}/{total} tables passed")
        print(f"  Status: {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
        print("=" * 65)

    return 0 if all_pass else 1


def main():
    parser = argparse.ArgumentParser(description="Great Expectations data validation")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="Path to DuckDB database")
    parser.add_argument("--table", type=str, help="Validate a single table")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    tables = [args.table] if args.table else None
    sys.exit(run_validation(args.db, tables, args.json))


if __name__ == "__main__":
    main()
