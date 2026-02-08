"""
Edge Case Tests for Cricket Playbook
=====================================
TKT-155: Enforce test coverage baselines and add edge case tests
EPIC: EPIC-015 (Operational Maturity)
Owner: N'Golo Kante (Quality & Testing)

Tests cover:
1. Empty DataFrame handling
2. Null/missing value handling
3. Duplicate record detection
4. Out-of-range / impossible values
5. Malformed input (missing columns, wrong types)
6. Boundary conditions (exact boundary values)
7. Domain constraint validation functions
8. GE expectation suite definitions
9. Threshold loader edge cases

Run with: pytest tests/test_edge_cases.py -v
"""

import math
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Project root (used by threshold_loader to locate config/thresholds.yaml)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def empty_ball_df() -> pd.DataFrame:
    """Return an empty DataFrame with fact_ball column schema."""
    columns = [
        "ball_id",
        "match_id",
        "innings",
        "over",
        "ball",
        "batter_id",
        "bowler_id",
        "batter_runs",
        "extra_runs",
        "total_runs",
        "is_wicket",
        "match_phase",
    ]
    return pd.DataFrame(columns=columns)


@pytest.fixture
def empty_player_df() -> pd.DataFrame:
    """Return an empty DataFrame with dim_player column schema."""
    columns = [
        "player_id",
        "current_name",
        "matches_played",
    ]
    return pd.DataFrame(columns=columns)


@pytest.fixture
def valid_ball_df() -> pd.DataFrame:
    """Return a small valid DataFrame mimicking fact_ball rows."""
    return pd.DataFrame(
        {
            "ball_id": ["b1", "b2", "b3"],
            "match_id": ["m1", "m1", "m1"],
            "innings": [1, 1, 1],
            "over": [0, 10, 19],
            "ball": [1, 2, 3],
            "batter_id": ["p1", "p2", "p3"],
            "bowler_id": ["p4", "p5", "p6"],
            "batter_runs": [0, 4, 6],
            "extra_runs": [0, 0, 1],
            "total_runs": [0, 4, 7],
            "is_wicket": [False, False, True],
            "match_phase": ["powerplay", "middle", "death"],
        }
    )


@pytest.fixture
def valid_ball_record() -> Dict[str, Any]:
    """Return a valid ball record dictionary for domain validation."""
    return {
        "match_id": "m1",
        "over_number": 5,
        "batter_batting_position": 3,
        "runs_total": 4,
    }


@pytest.fixture
def valid_performance_record() -> Dict[str, Any]:
    """Return a valid player performance record dictionary."""
    return {
        "player_id": "p1",
        "match_id": "m1",
        "strike_rate": 135.0,
        "economy": 7.5,
        "wickets_taken": 2,
    }


# =============================================================================
# 1. EMPTY DATAFRAME HANDLING
# =============================================================================


class TestEmptyDataFrameHandling:
    """Verify pipeline helpers behave safely on empty DataFrames."""

    def test_empty_ball_df_has_no_rows(self, empty_ball_df: pd.DataFrame):
        """An empty fact_ball DataFrame should have zero rows."""
        assert len(empty_ball_df) == 0
        assert "match_id" in empty_ball_df.columns

    def test_empty_player_df_has_no_rows(self, empty_player_df: pd.DataFrame):
        """An empty dim_player DataFrame should have zero rows."""
        assert len(empty_player_df) == 0
        assert "player_id" in empty_player_df.columns

    def test_groupby_on_empty_df(self, empty_ball_df: pd.DataFrame):
        """Groupby on an empty DataFrame should produce no groups."""
        grouped = empty_ball_df.groupby("match_id")
        assert len(grouped) == 0

    def test_agg_on_empty_df(self, empty_ball_df: pd.DataFrame):
        """Aggregation on empty DataFrame should return empty result."""
        result = empty_ball_df.groupby("match_id").agg(
            total=("total_runs", "sum"),
            balls=("ball_id", "count"),
        )
        assert len(result) == 0

    def test_merge_with_empty_df(self, empty_ball_df: pd.DataFrame, empty_player_df: pd.DataFrame):
        """Merging two empty DataFrames should produce an empty result."""
        merged = empty_ball_df.merge(
            empty_player_df,
            left_on="batter_id",
            right_on="player_id",
            how="left",
        )
        assert len(merged) == 0

    def test_describe_on_empty_df(self, empty_ball_df: pd.DataFrame):
        """Calling describe on an empty DataFrame should not raise."""
        desc = empty_ball_df.describe()
        assert desc is not None

    def test_empty_df_strike_rate_calculation(self, empty_ball_df: pd.DataFrame):
        """Strike rate computation on empty DF should produce NaN, not error."""
        total_runs = empty_ball_df["batter_runs"].sum()
        total_balls = len(empty_ball_df)
        sr = (total_runs / total_balls * 100) if total_balls > 0 else float("nan")
        assert math.isnan(sr)


# =============================================================================
# 2. NULL / MISSING VALUE HANDLING
# =============================================================================


class TestNullMissingValueHandling:
    """Verify graceful handling of NaN and None values."""

    def test_df_with_null_batter_id(self):
        """Rows with null batter_id should be filterable."""
        df = pd.DataFrame(
            {
                "ball_id": ["b1", "b2"],
                "batter_id": ["p1", None],
                "batter_runs": [4, 0],
            }
        )
        non_null = df.dropna(subset=["batter_id"])
        assert len(non_null) == 1

    def test_df_with_nan_runs(self):
        """NaN in runs columns should be handled by fillna."""
        df = pd.DataFrame(
            {
                "batter_runs": [4, float("nan"), 6],
                "extra_runs": [0, float("nan"), 1],
            }
        )
        filled = df.fillna(0)
        assert filled["batter_runs"].sum() == 10.0
        assert filled["extra_runs"].sum() == 1.0

    def test_strike_rate_with_nan(self):
        """Strike rate validation should treat None as valid (no value)."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(None)
        assert result.valid is True
        assert result.level == "info"

    def test_economy_with_nan(self):
        """Economy validation should treat None as valid (no value)."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(None)
        assert result.valid is True
        assert result.level == "info"

    def test_batting_position_with_none(self):
        """Batting position validation should treat None as valid."""
        from scripts.core.domain_constraints import validate_batting_position

        result = validate_batting_position(None)
        assert result.valid is True

    def test_over_number_with_none(self):
        """Over number validation should treat None as valid."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(None)
        assert result.valid is True

    def test_wickets_with_none(self):
        """Wickets validation should treat None as valid."""
        from scripts.core.domain_constraints import validate_wickets

        result = validate_wickets(None)
        assert result.valid is True

    def test_validate_ball_record_with_missing_keys(self):
        """validate_ball_record should handle a record with missing keys."""
        from scripts.core.domain_constraints import validate_ball_record

        # Completely empty dict -- all .get() calls return None
        results = validate_ball_record({})
        assert len(results) > 0
        # All None values should pass (no value provided)
        for r in results:
            assert r.valid is True

    def test_validate_player_performance_with_missing_keys(self):
        """validate_player_performance should handle a record with missing keys."""
        from scripts.core.domain_constraints import validate_player_performance

        results = validate_player_performance({})
        assert len(results) > 0
        for r in results:
            assert r.valid is True

    def test_df_with_all_nulls_in_column(self):
        """A column of all NaN values should not crash mean/sum."""
        df = pd.DataFrame({"runs": [float("nan"), float("nan"), float("nan")]})
        assert math.isnan(df["runs"].mean())
        assert df["runs"].sum() == 0.0  # pandas sum treats NaN as 0


# =============================================================================
# 3. DUPLICATE RECORD DETECTION
# =============================================================================


class TestDuplicateRecordDetection:
    """Verify detection and handling of duplicate records."""

    def test_duplicate_ball_ids(self, valid_ball_df: pd.DataFrame):
        """Duplicate ball_ids should be detectable."""
        df_with_dups = pd.concat([valid_ball_df, valid_ball_df.iloc[[0]]])
        dups = df_with_dups[df_with_dups.duplicated(subset=["ball_id"], keep=False)]
        assert len(dups) == 2  # original + duplicate

    def test_duplicate_match_ids_in_dim(self):
        """Duplicate match_ids in a dimension table should be detectable."""
        df = pd.DataFrame(
            {
                "match_id": ["m1", "m1", "m2"],
                "venue": ["Stadium A", "Stadium B", "Stadium C"],
            }
        )
        assert df["match_id"].duplicated().any()

    def test_drop_duplicates_preserves_first(self, valid_ball_df: pd.DataFrame):
        """drop_duplicates should keep the first occurrence."""
        df_with_dups = pd.concat([valid_ball_df, valid_ball_df])
        cleaned = df_with_dups.drop_duplicates(subset=["ball_id"], keep="first")
        assert len(cleaned) == len(valid_ball_df)

    def test_duplicate_player_ids(self):
        """Duplicate player_ids in dim_player should be flagged."""
        df = pd.DataFrame(
            {
                "player_id": ["p1", "p1", "p2"],
                "current_name": ["Alice", "Alice Copy", "Bob"],
                "matches_played": [10, 10, 5],
            }
        )
        assert not df["player_id"].is_unique

    def test_nunique_detects_duplicates(self):
        """nunique should differ from len when duplicates exist."""
        ids = ["m1", "m2", "m2", "m3"]
        df = pd.DataFrame({"match_id": ids})
        assert df["match_id"].nunique() < len(df)

    def test_deduplication_with_concat(self, valid_ball_df: pd.DataFrame):
        """Concatenating identical DataFrames should double the row count."""
        doubled = pd.concat([valid_ball_df, valid_ball_df], ignore_index=True)
        assert len(doubled) == 2 * len(valid_ball_df)
        # Dedup back
        deduped = doubled.drop_duplicates(subset=["ball_id"])
        assert len(deduped) == len(valid_ball_df)


# =============================================================================
# 4. OUT-OF-RANGE / IMPOSSIBLE VALUES
# =============================================================================


class TestOutOfRangeValues:
    """Verify domain constraint functions catch impossible values."""

    # --- Strike Rate ---

    def test_negative_strike_rate(self):
        """Negative strike rate should be flagged as error."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(-10.0)
        assert result.valid is False
        assert result.level == "error"

    def test_impossible_strike_rate(self):
        """Strike rate > 500 (error_max) should be flagged as error."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(600.0)
        assert result.valid is False
        assert result.level == "error"

    def test_warning_strike_rate(self):
        """Strike rate between 300 and 500 should produce a warning."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(350.0)
        assert result.valid is True
        assert result.level == "warning"

    def test_valid_strike_rate(self):
        """Strike rate of 135 should be perfectly valid."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(135.0)
        assert result.valid is True
        assert result.level == "info"

    # --- Economy ---

    def test_negative_economy(self):
        """Negative economy should be flagged as error."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(-2.0)
        assert result.valid is False
        assert result.level == "error"

    def test_impossible_economy(self):
        """Economy > 30 (error_max) should be flagged as error."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(35.0)
        assert result.valid is False
        assert result.level == "error"

    def test_warning_economy(self):
        """Economy between 20 and 30 should produce a warning."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(25.0)
        assert result.valid is True
        assert result.level == "warning"

    def test_valid_economy(self):
        """Economy of 7.5 should be perfectly valid."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(7.5)
        assert result.valid is True
        assert result.level == "info"

    # --- Batting Position ---

    def test_batting_position_zero(self):
        """Batting position 0 is invalid (minimum is 1)."""
        from scripts.core.domain_constraints import validate_batting_position

        result = validate_batting_position(0)
        assert result.valid is False

    def test_batting_position_twelve(self):
        """Batting position 12 is invalid (maximum is 11)."""
        from scripts.core.domain_constraints import validate_batting_position

        result = validate_batting_position(12)
        assert result.valid is False

    def test_batting_position_negative(self):
        """Negative batting position is invalid."""
        from scripts.core.domain_constraints import validate_batting_position

        result = validate_batting_position(-1)
        assert result.valid is False

    # --- Over Number ---

    def test_negative_over_number(self):
        """Negative over number should be flagged."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(-1)
        assert result.valid is False

    def test_over_number_20_t20(self):
        """Over 20 exceeds T20 limit of 19 (0-indexed)."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(20, "T20")
        assert result.valid is False

    def test_over_number_50_odi(self):
        """Over 50 exceeds ODI limit of 49 (0-indexed)."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(50, "ODI")
        assert result.valid is False

    # --- Wickets ---

    def test_negative_wickets(self):
        """Negative wickets should be flagged."""
        from scripts.core.domain_constraints import validate_wickets

        result = validate_wickets(-1)
        assert result.valid is False

    def test_eleven_wickets(self):
        """11 wickets in an innings is impossible (max 10)."""
        from scripts.core.domain_constraints import validate_wickets

        result = validate_wickets(11)
        assert result.valid is False

    # --- Runs ---

    def test_negative_runs_in_ball_record(self):
        """Negative runs_total should produce an error ValidationResult."""
        from scripts.core.domain_constraints import validate_ball_record

        ball = {
            "match_id": "m1",
            "over_number": 5,
            "batter_batting_position": 1,
            "runs_total": -3,
        }
        results = validate_ball_record(ball)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1
        assert any("Negative runs" in r.message for r in errors)


# =============================================================================
# 5. MALFORMED INPUT (missing columns, wrong types)
# =============================================================================


class TestMalformedInput:
    """Verify handling of DataFrames with missing columns or wrong dtypes."""

    def test_missing_column_raises_on_access(self):
        """Accessing a non-existent column should raise KeyError."""
        df = pd.DataFrame({"batter_runs": [4, 6]})
        with pytest.raises(KeyError):
            _ = df["nonexistent_column"]

    def test_missing_column_detectable_with_in(self):
        """Column presence check with 'in' should work for missing columns."""
        df = pd.DataFrame({"batter_runs": [4, 6]})
        assert "batter_runs" in df.columns
        assert "extra_runs" not in df.columns

    def test_wrong_dtype_string_as_runs(self):
        """String values in a runs column should fail numeric operations."""
        df = pd.DataFrame({"batter_runs": ["four", "six", "zero"]})
        with pytest.raises(TypeError):
            _ = df["batter_runs"].sum() + 1  # strings concat, not add

    def test_mixed_types_in_column(self):
        """A column with mixed int/str types should be object dtype."""
        df = pd.DataFrame({"over": [0, "one", 2, None]})
        assert df["over"].dtype == object

    def test_validate_ball_record_extra_keys_ignored(self):
        """Extra keys in a ball record should not cause errors."""
        from scripts.core.domain_constraints import validate_ball_record

        ball = {
            "match_id": "m1",
            "over_number": 10,
            "batter_batting_position": 5,
            "runs_total": 2,
            "extra_field_1": "ignored",
            "extra_field_2": 999,
        }
        results = validate_ball_record(ball)
        # Should still validate the known fields without error
        for r in results:
            assert r.valid is True

    def test_validate_performance_extra_keys_ignored(self):
        """Extra keys in a performance record should not cause errors."""
        from scripts.core.domain_constraints import validate_player_performance

        perf = {
            "player_id": "p1",
            "match_id": "m1",
            "strike_rate": 120.0,
            "economy": 8.0,
            "wickets_taken": 3,
            "bogus_field": "should be ignored",
        }
        results = validate_player_performance(perf)
        for r in results:
            assert r.valid is True

    def test_empty_string_column_values(self):
        """Empty string player names should be detectable."""
        df = pd.DataFrame(
            {
                "player_id": ["p1", "p2"],
                "current_name": ["Valid Name", ""],
            }
        )
        empty_names = df[df["current_name"].str.len() == 0]
        assert len(empty_names) == 1


# =============================================================================
# 6. BOUNDARY CONDITIONS (exact edge values)
# =============================================================================


class TestBoundaryConditions:
    """Verify behavior at exact boundary values for domain constraints."""

    # --- Over boundaries ---

    def test_over_zero_valid(self):
        """Over 0 (first over) should be valid in T20."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(0, "T20")
        assert result.valid is True

    def test_over_19_valid(self):
        """Over 19 (last over) should be valid in T20."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(19, "T20")
        assert result.valid is True

    def test_over_49_valid_odi(self):
        """Over 49 (last over) should be valid in ODI."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(49, "ODI")
        assert result.valid is True

    def test_over_unknown_format_defaults_to_19(self):
        """Unknown format should default to 19 max overs."""
        from scripts.core.domain_constraints import validate_over_number

        result = validate_over_number(19, "UNKNOWN_FORMAT")
        assert result.valid is True

        result_20 = validate_over_number(20, "UNKNOWN_FORMAT")
        assert result_20.valid is False

    # --- Batting position boundaries ---

    def test_batting_position_1_valid(self):
        """Batting position 1 (opener) should be valid."""
        from scripts.core.domain_constraints import validate_batting_position

        result = validate_batting_position(1)
        assert result.valid is True

    def test_batting_position_11_valid(self):
        """Batting position 11 (tail-ender) should be valid."""
        from scripts.core.domain_constraints import validate_batting_position

        result = validate_batting_position(11)
        assert result.valid is True

    # --- Batter runs boundaries ---

    def test_batter_runs_zero(self, valid_ball_df: pd.DataFrame):
        """Batter runs of 0 (dot ball) should be in the data."""
        assert (valid_ball_df["batter_runs"] == 0).any()

    def test_batter_runs_seven_boundary(self):
        """Batter runs of 7 is the GE max per the SUITES definition."""
        from scripts.core.ge_validation import SUITES

        fact_ball_suite = SUITES.get("fact_ball", [])
        batter_runs_exp = [e for e in fact_ball_suite if e.get("column") == "batter_runs"]
        assert len(batter_runs_exp) == 1
        assert batter_runs_exp[0]["kwargs"]["max_value"] == 7

    # --- Strike rate boundaries ---

    def test_strike_rate_zero_valid(self):
        """Strike rate of 0 should be valid (batted, scored nothing)."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(0.0)
        assert result.valid is True

    def test_strike_rate_at_warning_boundary(self):
        """Strike rate of exactly 300 should be valid (at warning_max)."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(300.0)
        assert result.valid is True
        # Exactly at warning should still be valid (> check, not >=)
        assert result.level == "info"

    def test_strike_rate_just_above_warning(self):
        """Strike rate of 300.1 should trigger warning."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(300.1)
        assert result.valid is True
        assert result.level == "warning"

    def test_strike_rate_at_error_boundary(self):
        """Strike rate of exactly 500 should be valid (at error_max)."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(500.0)
        assert result.valid is True
        # Exactly at error_max should still be valid (> check, not >=)
        assert result.level == "warning"

    def test_strike_rate_just_above_error(self):
        """Strike rate of 500.1 should be invalid."""
        from scripts.core.domain_constraints import validate_strike_rate

        result = validate_strike_rate(500.1)
        assert result.valid is False
        assert result.level == "error"

    # --- Economy boundaries ---

    def test_economy_zero_valid(self):
        """Economy of 0 should be valid (maiden-only analysis)."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(0.0)
        assert result.valid is True

    def test_economy_at_warning_boundary(self):
        """Economy of exactly 20 should be valid."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(20.0)
        assert result.valid is True
        assert result.level == "info"

    def test_economy_just_above_warning(self):
        """Economy of 20.1 should trigger warning."""
        from scripts.core.domain_constraints import validate_economy

        result = validate_economy(20.1)
        assert result.valid is True
        assert result.level == "warning"

    # --- Wickets boundaries ---

    def test_zero_wickets_valid(self):
        """Zero wickets should be valid."""
        from scripts.core.domain_constraints import validate_wickets

        result = validate_wickets(0)
        assert result.valid is True

    def test_ten_wickets_valid(self):
        """Ten wickets (all out) should be valid."""
        from scripts.core.domain_constraints import validate_wickets

        result = validate_wickets(10)
        assert result.valid is True


# =============================================================================
# 7. DOMAIN CONSTRAINT VALIDATION - COMPOSITE FUNCTIONS
# =============================================================================


class TestDomainConstraintComposite:
    """Test composite validation functions with varied inputs."""

    def test_validate_ball_record_valid(self, valid_ball_record: Dict[str, Any]):
        """A fully valid ball record should produce no errors."""
        from scripts.core.domain_constraints import validate_ball_record

        results = validate_ball_record(valid_ball_record)
        errors = [r for r in results if not r.valid]
        assert len(errors) == 0

    def test_validate_ball_record_invalid_over(self):
        """A ball record with over=25 should fail validation."""
        from scripts.core.domain_constraints import validate_ball_record

        ball = {
            "match_id": "m1",
            "over_number": 25,
            "batter_batting_position": 3,
            "runs_total": 4,
        }
        results = validate_ball_record(ball)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1

    def test_validate_ball_record_invalid_position(self):
        """A ball record with batting position 0 should fail."""
        from scripts.core.domain_constraints import validate_ball_record

        ball = {
            "match_id": "m1",
            "over_number": 5,
            "batter_batting_position": 0,
            "runs_total": 1,
        }
        results = validate_ball_record(ball)
        errors = [r for r in results if not r.valid]
        assert len(errors) >= 1

    def test_validate_player_performance_valid(self, valid_performance_record: Dict[str, Any]):
        """A fully valid performance record should produce no errors."""
        from scripts.core.domain_constraints import validate_player_performance

        results = validate_player_performance(valid_performance_record)
        errors = [r for r in results if not r.valid]
        assert len(errors) == 0

    def test_validate_player_performance_all_invalid(self):
        """A performance record with all invalid values should flag errors."""
        from scripts.core.domain_constraints import validate_player_performance

        perf = {
            "player_id": "p1",
            "match_id": "m1",
            "strike_rate": -10.0,
            "economy": -5.0,
            "wickets_taken": -2,
        }
        results = validate_player_performance(perf)
        errors = [r for r in results if not r.valid]
        assert len(errors) == 3  # all three should fail

    def test_validation_result_repr(self):
        """ValidationResult.__repr__ should include PASS/FAIL status."""
        from scripts.core.domain_constraints import ValidationResult

        passing = ValidationResult("test", 42, True, "info", "All good")
        assert "PASS" in repr(passing)

        failing = ValidationResult("test", -1, False, "error", "Bad value")
        assert "ERROR" in repr(failing)

    def test_get_check_constraints_returns_dict(self):
        """get_check_constraints should return a dict of table -> constraints."""
        from scripts.core.domain_constraints import get_check_constraints

        constraints = get_check_constraints()
        assert isinstance(constraints, dict)
        assert "fact_ball" in constraints
        assert "dim_player" in constraints
        assert "dim_match" in constraints
        assert "fact_player_match_performance" in constraints

    def test_check_constraints_are_strings(self):
        """Each constraint should be a CHECK string."""
        from scripts.core.domain_constraints import get_check_constraints

        constraints = get_check_constraints()
        for table, checks in constraints.items():
            assert isinstance(checks, list)
            for check in checks:
                assert check.startswith("CHECK ("), (
                    f"Constraint for {table} should start with 'CHECK (': {check}"
                )


# =============================================================================
# 8. GE VALIDATION SUITE DEFINITIONS
# =============================================================================


class TestGEValidationSuiteDefinitions:
    """Verify GE expectation suite definitions are well-formed."""

    def test_suites_dict_has_expected_tables(self):
        """SUITES should define expectations for known tables."""
        from scripts.core.ge_validation import SUITES

        expected_tables = ["fact_ball", "dim_player", "dim_match", "dim_team", "dim_venue"]
        for table in expected_tables:
            assert table in SUITES, f"Missing suite definition for {table}"

    def test_each_suite_is_list(self):
        """Each suite should be a list of expectation dicts."""
        from scripts.core.ge_validation import SUITES

        for table, expectations in SUITES.items():
            assert isinstance(expectations, list), f"Suite for {table} should be a list"

    def test_each_expectation_has_type(self):
        """Every expectation dict must have a 'type' key."""
        from scripts.core.ge_validation import SUITES

        for table, expectations in SUITES.items():
            for exp in expectations:
                assert "type" in exp, f"Expectation in {table} missing 'type' key: {exp}"

    def test_between_expectations_have_kwargs(self):
        """Between expectations should have min_value or max_value."""
        from scripts.core.ge_validation import SUITES

        for table, expectations in SUITES.items():
            for exp in expectations:
                if exp["type"] == "expect_column_values_to_be_between":
                    assert "kwargs" in exp, f"Between expectation in {table} missing kwargs"
                    kwargs = exp["kwargs"]
                    assert "min_value" in kwargs or "max_value" in kwargs

    def test_fact_ball_has_over_expectation(self):
        """fact_ball suite should validate over is between 0 and 19."""
        from scripts.core.ge_validation import SUITES

        over_exp = [
            e
            for e in SUITES["fact_ball"]
            if e.get("column") == "over" and e["type"] == "expect_column_values_to_be_between"
        ]
        assert len(over_exp) == 1
        assert over_exp[0]["kwargs"]["min_value"] == 0
        assert over_exp[0]["kwargs"]["max_value"] == 19

    def test_fact_ball_has_is_wicket_set_expectation(self):
        """fact_ball suite should validate is_wicket values."""
        from scripts.core.ge_validation import SUITES

        wicket_exp = [
            e
            for e in SUITES["fact_ball"]
            if e.get("column") == "is_wicket" and e["type"] == "expect_column_values_to_be_in_set"
        ]
        assert len(wicket_exp) == 1
        value_set = wicket_exp[0]["kwargs"]["value_set"]
        assert True in value_set or 1 in value_set

    def test_dim_player_has_uniqueness_check(self):
        """dim_player suite should check player_id uniqueness."""
        from scripts.core.ge_validation import SUITES

        unique_exp = [
            e
            for e in SUITES["dim_player"]
            if e.get("column") == "player_id" and e["type"] == "expect_column_values_to_be_unique"
        ]
        assert len(unique_exp) == 1

    def test_row_minimums_defined(self):
        """ROW_MINIMUMS should be defined for key tables."""
        from scripts.core.ge_validation import ROW_MINIMUMS

        assert "fact_ball" in ROW_MINIMUMS
        assert "dim_player" in ROW_MINIMUMS
        assert ROW_MINIMUMS["fact_ball"] >= 100_000

    def test_expectation_class_mapping_covers_all_types(self):
        """_get_expectation_class should handle all types used in SUITES."""
        from scripts.core.ge_validation import SUITES, _get_expectation_class

        all_types = set()
        for expectations in SUITES.values():
            for exp in expectations:
                all_types.add(exp["type"])

        for exp_type in all_types:
            cls = _get_expectation_class(exp_type)
            assert cls is not None, f"_get_expectation_class returned None for '{exp_type}'"

    def test_get_expectation_class_unknown_returns_none(self):
        """Unknown expectation type should return None, not raise."""
        from scripts.core.ge_validation import _get_expectation_class

        assert _get_expectation_class("expect_bogus_thing") is None

    def test_match_phase_values_in_suite(self):
        """Match phase expectation should include powerplay, middle, death."""
        from scripts.core.ge_validation import SUITES

        phase_exp = [e for e in SUITES["fact_ball"] if e.get("column") == "match_phase"]
        assert len(phase_exp) == 1
        value_set = phase_exp[0]["kwargs"]["value_set"]
        assert "powerplay" in value_set
        assert "middle" in value_set
        assert "death" in value_set


# =============================================================================
# 9. THRESHOLD LOADER EDGE CASES
# =============================================================================


class TestThresholdLoaderEdgeCases:
    """Test threshold_loader.py with edge cases and error conditions."""

    def test_get_threshold_with_default(self):
        """get_threshold should return default for missing path."""
        from scripts.utils.threshold_loader import get_threshold

        result = get_threshold("nonexistent.path.here", default=42)
        assert result == 42

    def test_get_threshold_no_default_raises(self):
        """get_threshold without default should raise KeyError for missing path."""
        from scripts.utils.threshold_loader import get_threshold

        with pytest.raises(KeyError):
            get_threshold("nonexistent.path.here")

    def test_get_thresholds_full_config(self):
        """get_thresholds() with no args should return the full config dict."""
        from scripts.utils.threshold_loader import get_thresholds

        config = get_thresholds()
        assert isinstance(config, dict)
        assert "sample_size" in config
        assert "batting" in config
        assert "metadata" in config

    def test_get_thresholds_section(self):
        """get_thresholds('batting') should return the batting section."""
        from scripts.utils.threshold_loader import get_thresholds

        batting = get_thresholds("batting")
        assert isinstance(batting, dict)
        assert "specialist" in batting

    def test_get_thresholds_nested_section(self):
        """get_thresholds('ml.pca') should navigate nested keys."""
        from scripts.utils.threshold_loader import get_thresholds

        pca = get_thresholds("ml.pca")
        assert isinstance(pca, dict)
        assert "target_variance" in pca

    def test_get_thresholds_invalid_section_raises(self):
        """get_thresholds with an invalid section should raise KeyError."""
        from scripts.utils.threshold_loader import get_thresholds

        with pytest.raises(KeyError):
            get_thresholds("totally.fake.section")

    def test_validate_thresholds_passes(self):
        """validate_thresholds should return True for valid config."""
        from scripts.utils.threshold_loader import validate_thresholds

        assert validate_thresholds() is True

    def test_reload_thresholds(self):
        """reload_thresholds should return a dict and clear cache."""
        from scripts.utils.threshold_loader import reload_thresholds

        result = reload_thresholds()
        assert isinstance(result, dict)
        assert "metadata" in result

    def test_known_threshold_values(self):
        """Spot-check specific threshold values from config."""
        from scripts.utils.threshold_loader import get_threshold

        assert get_threshold("sample_size.min_balls_batter") == 300
        assert get_threshold("validation.strike_rate.error_max") == 500
        assert get_threshold("validation.economy.error_max") == 30
        assert get_threshold("validation.batting_position.max") == 11
        assert get_threshold("validation.over_number.max") == 19

    def test_sample_size_class(self):
        """SampleSize convenience class should return expected values."""
        from scripts.utils.threshold_loader import SampleSize

        assert SampleSize.min_balls_batter() == 300
        assert SampleSize.min_balls_bowler() == 200

    def test_batting_class(self):
        """Batting convenience class should return expected values."""
        from scripts.utils.threshold_loader import Batting

        assert Batting.specialist_sr() == 130
        assert Batting.specialist_avg() == 20

    def test_validation_class(self):
        """Validation convenience class should return expected values."""
        from scripts.utils.threshold_loader import Validation

        assert Validation.sr_max_error() == 500
        assert Validation.economy_max_error() == 30

    def test_metadata_version_exists(self):
        """Metadata should have a version field."""
        from scripts.utils.threshold_loader import get_threshold

        version = get_threshold("metadata.version")
        assert version is not None
        assert isinstance(version, str)

    def test_threshold_default_none_raises_on_miss(self):
        """When default is explicitly None, missing key should raise."""
        from scripts.utils.threshold_loader import get_threshold

        with pytest.raises(KeyError):
            get_threshold("does.not.exist", default=None)

    def test_threshold_default_zero_returns_zero(self):
        """Default of 0 (falsy) should still be returned for missing keys."""
        from scripts.utils.threshold_loader import get_threshold

        result = get_threshold("does.not.exist", default=0)
        assert result == 0

    def test_threshold_default_empty_string(self):
        """Default of empty string should be returned for missing keys."""
        from scripts.utils.threshold_loader import get_threshold

        result = get_threshold("does.not.exist", default="")
        assert result == ""


# =============================================================================
# 10. VALIDATION RESULT OBJECT TESTS
# =============================================================================


class TestValidationResultObject:
    """Test the ValidationResult dataclass behavior."""

    def test_valid_result_attributes(self):
        """A valid ValidationResult should have correct attributes."""
        from scripts.core.domain_constraints import ValidationResult

        vr = ValidationResult("test_field", 100, True, "info", "Looks good")
        assert vr.field == "test_field"
        assert vr.value == 100
        assert vr.valid is True
        assert vr.level == "info"
        assert vr.message == "Looks good"

    def test_invalid_result_attributes(self):
        """An invalid ValidationResult should have correct attributes."""
        from scripts.core.domain_constraints import ValidationResult

        vr = ValidationResult("test_field", -5, False, "error", "Bad")
        assert vr.valid is False
        assert vr.level == "error"

    def test_warning_result_repr(self):
        """A warning result should show PASS in repr (valid=True)."""
        from scripts.core.domain_constraints import ValidationResult

        vr = ValidationResult("sr", 350, True, "warning", "Unusually high")
        assert "PASS" in repr(vr)

    def test_error_result_repr(self):
        """An error result should show ERROR in repr."""
        from scripts.core.domain_constraints import ValidationResult

        vr = ValidationResult("sr", -10, False, "error", "Negative")
        assert "ERROR" in repr(vr)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
