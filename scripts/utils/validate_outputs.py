#!/usr/bin/env python3
"""
Cricket Playbook - Output Validation Script
Author: Andy Flower (Analytics QA)
Sprint: 2.9 - Logical Rules Validation

Validates all output CSVs for logical impossibilities in T20 cricket:
- Entry points must be 1-120 (legal balls in T20)
- Overs must be 0-19 (0-indexed) or 1-20
- Strike rates typically 50-300
- Economy rates typically 4-15
- No negative values for balls, runs, wickets
"""

import pandas as pd
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "outputs"

# T20 constraints
MAX_LEGAL_BALLS = 120
MAX_OVERS = 20
MIN_STRIKE_RATE = 30  # Very defensive
MAX_STRIKE_RATE = 400  # Extreme but possible
MIN_ECONOMY = 2.0  # Very economical
MAX_ECONOMY = 20.0  # Very expensive


class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_error(self, msg):
        self.errors.append(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)

    @property
    def is_valid(self):
        return len(self.errors) == 0


def validate_batter_entry_points(result: ValidationResult):
    """Validate batter_entry_points.csv"""

    path = OUTPUT_DIR / "batter_entry_points.csv"
    if not path.exists():
        result.add_warning(f"File not found: {path.name}")
        return

    df = pd.read_csv(path)
    print(f"\n  Validating {path.name} ({len(df)} rows)...")

    # Check entry ball bounds (1-120)
    for col in [
        "min_entry_ball",
        "max_entry_ball",
        "median_entry_ball",
        "mean_entry_ball",
    ]:
        if col in df.columns:
            invalid = df[(df[col] < 1) | (df[col] > MAX_LEGAL_BALLS)]
            if len(invalid) > 0:
                result.add_error(
                    f"{path.name}: {len(invalid)} rows with {col} outside 1-{MAX_LEGAL_BALLS}"
                )
                for _, row in invalid.head(3).iterrows():
                    result.add_error(f"  - {row['batter_name']}: {col}={row[col]}")

    # Check over bounds
    for col in ["median_entry_over", "mean_entry_over", "mode_entry_over"]:
        if col in df.columns:
            max_over = MAX_OVERS
            invalid = df[(df[col] < 0) | (df[col] > max_over)]
            if len(invalid) > 0:
                result.add_error(
                    f"{path.name}: {len(invalid)} rows with {col} outside 0-{max_over}"
                )

    print("    ✓ Entry ball bounds checked")
    print("    ✓ Entry over bounds checked")


def validate_bowler_phase_performance(result: ValidationResult):
    """Validate bowler_phase_performance.csv"""

    path = OUTPUT_DIR / "bowler_phase_performance.csv"
    if not path.exists():
        result.add_warning(f"File not found: {path.name}")
        return

    df = pd.read_csv(path)
    print(f"\n  Validating {path.name} ({len(df)} rows)...")

    # Check economy rate bounds
    for phase in ["powerplay", "middle", "death"]:
        eco_col = f"{phase}_economy"
        if eco_col in df.columns:
            # Filter out NaN values
            valid_df = df[df[eco_col].notna()]
            invalid = valid_df[
                (valid_df[eco_col] < MIN_ECONOMY) | (valid_df[eco_col] > MAX_ECONOMY)
            ]
            if len(invalid) > 0:
                result.add_warning(
                    f"{path.name}: {len(invalid)} rows with {eco_col} outside {MIN_ECONOMY}-{MAX_ECONOMY}"
                )
                for _, row in invalid.head(3).iterrows():
                    result.add_warning(f"  - {row['bowler_name']}: {eco_col}={row[eco_col]:.2f}")

    # Check for negative values
    for col in [
        "powerplay_overs",
        "middle_overs",
        "death_overs",
        "powerplay_wickets",
        "middle_wickets",
        "death_wickets",
    ]:
        if col in df.columns:
            invalid = df[df[col] < 0]
            if len(invalid) > 0:
                result.add_error(f"{path.name}: {len(invalid)} rows with negative {col}")

    print("    ✓ Economy rate bounds checked")
    print("    ✓ Non-negative values checked")


def validate_bowler_over_timing(result: ValidationResult):
    """Validate bowler_over_timing.csv"""

    path = OUTPUT_DIR / "bowler_over_timing.csv"
    if not path.exists():
        result.add_warning(f"File not found: {path.name}")
        return

    df = pd.read_csv(path)
    print(f"\n  Validating {path.name} ({len(df)} rows)...")

    # Check over timing bounds (0-19 for 0-indexed overs)
    for i in [1, 2, 3, 4]:
        for stat in ["median", "mode"]:
            col = f"over{i}_{stat}"
            if col in df.columns:
                valid_df = df[df[col].notna()]
                invalid = valid_df[(valid_df[col] < 0) | (valid_df[col] > 19)]
                if len(invalid) > 0:
                    result.add_error(f"{path.name}: {len(invalid)} rows with {col} outside 0-19")

    print("    ✓ Over timing bounds checked")


def validate_squad_experience(result: ValidationResult):
    """Validate ipl_2026_squad_experience.csv"""

    path = OUTPUT_DIR / "ipl_2026_squad_experience.csv"
    if not path.exists():
        result.add_warning(f"File not found: {path.name}")
        return

    df = pd.read_csv(path)
    print(f"\n  Validating {path.name} ({len(df)} rows)...")

    # Check for negative values
    for col in [
        "ipl_batting_innings",
        "ipl_batting_balls",
        "ipl_batting_runs",
        "ipl_bowling_matches",
        "ipl_bowling_balls",
        "ipl_bowling_wickets",
    ]:
        if col in df.columns:
            invalid = df[df[col] < 0]
            if len(invalid) > 0:
                result.add_error(f"{path.name}: {len(invalid)} rows with negative {col}")

    # Check strike rate bounds
    if "ipl_batting_sr" in df.columns:
        valid_df = df[(df["ipl_batting_sr"].notna()) & (df["ipl_batting_sr"] > 0)]
        outliers = valid_df[
            (valid_df["ipl_batting_sr"] < MIN_STRIKE_RATE)
            | (valid_df["ipl_batting_sr"] > MAX_STRIKE_RATE)
        ]
        if len(outliers) > 0:
            result.add_warning(
                f"{path.name}: {len(outliers)} rows with strike rate outside {MIN_STRIKE_RATE}-{MAX_STRIKE_RATE}"
            )

    # Check economy bounds
    if "ipl_bowling_economy" in df.columns:
        valid_df = df[(df["ipl_bowling_economy"].notna()) & (df["ipl_bowling_economy"] > 0)]
        outliers = valid_df[
            (valid_df["ipl_bowling_economy"] < MIN_ECONOMY)
            | (valid_df["ipl_bowling_economy"] > MAX_ECONOMY)
        ]
        if len(outliers) > 0:
            result.add_warning(
                f"{path.name}: {len(outliers)} rows with economy outside {MIN_ECONOMY}-{MAX_ECONOMY}"
            )

    print("    ✓ Non-negative values checked")
    print("    ✓ Strike rate bounds checked")
    print("    ✓ Economy bounds checked")


def validate_matchups(result: ValidationResult):
    """Validate matchup CSVs"""

    for filename in [
        "batter_bowling_type_matchup.csv",
        "bowler_handedness_matchup.csv",
    ]:
        path = OUTPUT_DIR / filename
        if not path.exists():
            result.add_warning(f"File not found: {filename}")
            continue

        df = pd.read_csv(path)
        print(f"\n  Validating {filename} ({len(df)} rows)...")

        # Check for negative values in key columns
        for col in df.columns:
            if any(x in col.lower() for x in ["balls", "runs", "wickets", "innings"]):
                if df[col].dtype in ["int64", "float64"]:
                    invalid = df[df[col] < 0]
                    if len(invalid) > 0:
                        result.add_error(f"{filename}: {len(invalid)} rows with negative {col}")

        print("    ✓ Non-negative values checked")


def main():
    print("=" * 70)
    print("Cricket Playbook - Output Validation")
    print("Author: Andy Flower | Sprint 2.9")
    print("=" * 70)

    result = ValidationResult()

    # Validate each output file
    validate_batter_entry_points(result)
    validate_bowler_phase_performance(result)
    validate_bowler_over_timing(result)
    validate_squad_experience(result)
    validate_matchups(result)

    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    if result.warnings:
        print(f"\n  WARNINGS ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"    ⚠ {w}")

    if result.errors:
        print(f"\n  ERRORS ({len(result.errors)}):")
        for e in result.errors:
            print(f"    ✗ {e}")
        print("\n  VALIDATION FAILED")
        return 1
    else:
        print("\n  ✓ ALL VALIDATIONS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
