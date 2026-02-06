# Codebase Optimization Audit Report

**Ticket:** TKT-096
**Author:** Brad Stevens (Ops Lead / Code Quality)
**Date:** 2026-02-06
**Sprint:** Optimization Audit

---

## Executive Summary

This audit analyzed 15+ Python scripts across the Cricket Playbook codebase, focusing on code quality, maintainability, and performance. The codebase is generally well-structured with clear separation of concerns, but has significant opportunities for consolidation and standardization.

### Key Findings

| Category | Issues Found | Quick Wins Implemented | Future Tickets |
|----------|-------------|------------------------|----------------|
| Code Duplication | 8 | 1 | 3 |
| Missing Type Hints | High | - | 1 |
| Inefficient Patterns | 2 | - | 1 |
| Import Optimization | 3 | - | - |
| Scalability Concerns | 2 | - | 1 |
| Best Practices | 5 | - | 2 |

---

## Phase 1: Detailed Audit Findings

### 1. Code Duplication (HIGH PRIORITY)

#### 1.1 Path Setup Pattern
**Files Affected:** ALL scripts (15+)
**Pattern:**
```python
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # Varies by depth
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"
```

**Impact:**
- Same logic repeated in every file
- Inconsistent path depth calculations (`.parent` vs `.parent.parent`)
- Risk of path errors when moving files

**Quick Win Implemented:** Created `/scripts/utils/constants.py` with centralized path constants.

#### 1.2 IPL Teams and Abbreviations
**Files Affected:**
- `generate_predicted_xii.py` (lines 41-66)
- `generate_depth_charts.py` (lines 48-73)
- `generate_stat_packs.py`
- `generate_2023_outputs.py`

**Pattern:**
```python
IPL_TEAMS = [
    "Chennai Super Kings",
    "Mumbai Indians",
    ...
]

TEAM_ABBREV = {
    "Chennai Super Kings": "CSK",
    ...
}
```

**Impact:**
- If a team name changes, requires updates in multiple files
- Inconsistency risk between files

**Quick Win Implemented:** Consolidated into `/scripts/utils/constants.py`.

#### 1.3 Overseas Players List
**Files Affected:**
- `generate_predicted_xii.py` (lines 398-488)
- `generate_depth_charts.py` (lines 233-317)

**Pattern:** ~85 overseas player names duplicated in two files.

**Quick Win Implemented:** Consolidated into `/scripts/utils/constants.py`.

#### 1.4 Threshold Constants
**Files Affected:**
- `batter_bowling_type_matchup.py` (lines 57-73)
- `generate_2023_outputs.py` (lines 39-44)
- `generate_all_2023_outputs.py`
- `bowler_phase_tags.py` (lines 35-44)
- `bowler_handedness_matchup.py` (lines 143-144)

**Pattern:**
```python
MIN_BALLS_VS_TYPE = 50
SPECIALIST_SR_THRESHOLD = 130
VULNERABLE_SR_THRESHOLD = 110
# etc.
```

**Impact:**
- Thresholds defined in 5+ places
- Andy Flower review updates had to be made in multiple files
- Risk of inconsistency between analyses

**Quick Win Implemented:** Consolidated into `/scripts/utils/constants.py`.

#### 1.5 `update_player_tags_json()` Function
**Files Affected:**
- `batter_bowling_type_matchup.py` (lines 351-404)
- `bowler_handedness_matchup.py` (lines 269-315)
- `bowler_phase_tags.py` (lines 212-259)

**Pattern:** Each file has nearly identical logic for:
1. Loading player_tags.json
2. Creating tag lookup
3. Removing old tags
4. Adding new tags
5. Saving updated file

**Recommendation:** Extract to shared utility function in `utils/player_tags.py`.

**Future Ticket:** TKT-XXX - Consolidate player_tags.json update logic

---

### 2. Missing Type Hints (MEDIUM PRIORITY)

**Files Affected:** ALL scripts

**Pattern:** Functions lack parameter and return type annotations.

**Example (Before):**
```python
def get_bowler_phase_stats(conn):
    """Get bowler performance by match phase."""
    ...
```

**Example (After):**
```python
def get_bowler_phase_stats(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Get bowler performance by match phase."""
    ...
```

**Impact:**
- IDE autocompletion reduced
- Type errors not caught until runtime
- Documentation less clear

**Future Ticket:** TKT-XXX - Add type hints to all script functions

---

### 3. Inefficient Patterns (MEDIUM PRIORITY)

#### 3.1 Repeated DataFrame Filtering in Loops
**Files Affected:**
- `generate_2023_outputs.py` (lines 105-145)
- `bowler_handedness_matchup.py` (lines 91-136)
- `batter_bowling_type_matchup.py` (lines 119-162)

**Pattern:**
```python
for batter_id in df["batter_id"].unique():
    batter_df = df[df["batter_id"] == batter_id]
    pace_df = batter_df[batter_df["bowling_type"].isin(PACE_TYPES)]
    spin_df = batter_df[batter_df["bowling_type"].isin(SPIN_TYPES)]
```

**Impact:**
- O(n*m) complexity where n = batters, m = records
- Creates intermediate DataFrames on each iteration

**Recommendation:** Use `groupby` for better performance:
```python
grouped = df.groupby('batter_id')
for batter_id, batter_df in grouped:
    ...
```

**Future Ticket:** TKT-XXX - Optimize DataFrame operations in matchup scripts

#### 3.2 Repeated Database Queries
**Files Affected:**
- `generate_all_2023_outputs.py` (multiple similar CTEs)
- `analytics_ipl.py` (view creation patterns)

**Pattern:** Similar SQL CTEs repeated across functions.

**Recommendation:** Create shared SQL templates or use parameterized view functions.

---

### 4. Import Optimization (LOW PRIORITY)

#### 4.1 sys.path Manipulation
**Files Affected:**
- `generate_predicted_xii.py` (line 24)
- `generate_depth_charts.py` (line 30)
- `generate_stat_packs.py`

**Pattern:**
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging_config import setup_logger
```

**Impact:**
- Modifies global state
- Makes imports less explicit
- Can cause import order issues

**Recommendation:** Use proper package structure with `__init__.py` files or relative imports.

#### 4.2 Unused Imports
**Files Affected:** Various

**Examples:**
- Some files import `json` but don't use it
- Some files import all of `pandas` when only specific functions needed

**Recommendation:** Run `ruff` or `autoflake` to remove unused imports.

---

### 5. Scalability Concerns (MEDIUM PRIORITY)

#### 5.1 In-Memory Processing
**Files Affected:**
- `player_clustering_v2.py` (loads all ball-by-ball data)
- `generate_all_2023_outputs.py` (large SQL results)

**Pattern:** All data loaded into memory for processing.

**Impact:**
- Memory usage scales linearly with data size
- May fail with larger datasets

**Recommendation:**
- Use chunked processing for large datasets
- Consider streaming or lazy evaluation patterns

#### 5.2 Hardcoded Date Filters
**Files Affected:** ALL analysis scripts

**Pattern:**
```python
IPL_MIN_DATE = "2023-01-01"
```

**Impact:**
- Requires code changes each season
- Not configurable at runtime

**Recommendation:** Move to environment variables or config file.

**Future Ticket:** TKT-XXX - Externalize date configuration

---

### 6. Best Practices Violations (LOW PRIORITY)

#### 6.1 Global Mutable State
**Files Affected:**
- `generate_predicted_xii.py` (lines 387-389)

**Pattern:**
```python
BATTER_METRICS = {}
BOWLER_METRICS = {}

def main():
    global BATTER_METRICS, BOWLER_METRICS
    BATTER_METRICS = load_batter_metrics()
```

**Impact:**
- Makes testing difficult
- Can cause unexpected side effects

**Recommendation:** Pass metrics as function parameters.

#### 6.2 Magic Numbers
**Files Affected:** Multiple scoring functions

**Pattern:**
```python
if player.price_cr >= 15:
    return 0.15
elif player.price_cr >= 10:
    return 0.10
```

**Recommendation:** Define named constants for auction price tiers.

#### 6.3 Long Functions
**Files Affected:**
- `generate_predicted_xii.py`: `reorder_batting_positions()` (347 lines)
- `generate_depth_charts.py`: `generate_team_depth_chart()` (178 lines)
- `player_clustering_v2.py`: `main()` (200+ lines)

**Recommendation:** Break into smaller, focused functions.

#### 6.4 Error Handling
**Files Affected:** Most scripts

**Pattern:** Minimal error handling for file operations and database queries.

**Recommendation:** Add try/except blocks with meaningful error messages.

#### 6.5 Logging Inconsistency
**Files Affected:**
- Some scripts use `utils.logging_config.setup_logger()`
- Others use `print()` statements

**Recommendation:** Standardize on logging module throughout.

---

## Phase 2: Quick Wins Implemented

### QW-1: Created Shared Constants Module

**File:** `/scripts/utils/constants.py`

**Contents:**
1. **Path Constants:** `PROJECT_DIR`, `DATA_DIR`, `OUTPUT_DIR`, `DB_PATH`, subdirectories
2. **Date Filters:** `IPL_MIN_DATE`
3. **Sample Size Thresholds:** `MIN_BALLS_VS_TYPE`, `MIN_BALLS_VS_HAND`, phase minimums
4. **Bowling Categories:** `PACE_TYPES`, `SPIN_TYPES`
5. **Tag Thresholds:** Specialist/Vulnerable thresholds for batting, bowling phases, handedness
6. **Team Data:** `IPL_TEAMS`, `TEAM_ABBREV`
7. **Overseas Players:** `OVERSEAS_PLAYERS` set with `is_overseas_player()` helper

**Usage Example:**
```python
from utils.constants import (
    DB_PATH,
    OUTPUT_DIR,
    IPL_MIN_DATE,
    MIN_BALLS_VS_TYPE,
    SPECIALIST_SR_THRESHOLD,
    IPL_TEAMS,
    TEAM_ABBREV,
    is_overseas_player,
)
```

**Migration Note:** Scripts can incrementally adopt the shared constants. No breaking changes - the module supplements existing code.

---

## Phase 3: Recommended Future Tickets

### TKT-XXX: Consolidate Player Tags Update Logic
**Priority:** High
**Effort:** 2-3 hours
**Description:** Extract the repeated `update_player_tags_json()` function into a shared utility module. Should handle:
- Loading existing tags
- Removing old tags by category
- Adding new tags
- Saving with proper formatting

### TKT-XXX: Add Type Hints Throughout Codebase
**Priority:** Medium
**Effort:** 4-6 hours
**Description:** Add Python type hints to all function signatures and key variables. Include:
- Function parameters
- Return types
- Class attributes
- Complex data structures

### TKT-XXX: Optimize DataFrame Operations
**Priority:** Medium
**Effort:** 3-4 hours
**Description:** Replace iterative DataFrame filtering with groupby operations in:
- `batter_bowling_type_matchup.py`
- `bowler_handedness_matchup.py`
- `generate_2023_outputs.py`

### TKT-XXX: Externalize Configuration
**Priority:** Low
**Effort:** 2-3 hours
**Description:** Move hardcoded values to a config file or environment variables:
- Date filters (`IPL_MIN_DATE`)
- Threshold values
- File paths

### TKT-XXX: Standardize Logging
**Priority:** Low
**Effort:** 2-3 hours
**Description:** Replace all `print()` statements with proper logging. Ensure consistent log format across all scripts.

### TKT-XXX: Break Up Long Functions
**Priority:** Low
**Effort:** 4-6 hours
**Description:** Refactor long functions (>100 lines) into smaller, focused helper functions. Priority targets:
- `reorder_batting_positions()` in generate_predicted_xii.py
- `generate_team_depth_chart()` in generate_depth_charts.py

---

## Summary

The Cricket Playbook codebase is functional and delivers its intended outputs. The main optimization opportunities are:

1. **Consolidation:** Significant code duplication that should be centralized
2. **Standardization:** Inconsistent patterns across scripts
3. **Performance:** Some inefficient DataFrame operations
4. **Maintainability:** Type hints and logging would improve developer experience

The quick win implemented (shared constants module) provides immediate value and sets a pattern for future consolidation work.

---

## Appendix: Files Audited

| Directory | Files | Lines of Code |
|-----------|-------|---------------|
| scripts/core/ | 3 | ~1,500 |
| scripts/generators/ | 5 | ~4,500 |
| scripts/analysis/ | 5 | ~2,500 |
| scripts/utils/ | 4 | ~500 |
| **Total** | **17** | **~9,000** |

### Key Files Reviewed

1. `/scripts/core/analytics_ipl.py` - Analytics view creation
2. `/scripts/core/ingest.py` - Data ingestion
3. `/scripts/core/validate_schema.py` - Schema validation
4. `/scripts/generators/generate_predicted_xii.py` - Predicted XII algorithm
5. `/scripts/generators/generate_depth_charts.py` - Depth charts algorithm
6. `/scripts/generators/generate_stat_packs.py` - Stat pack generation
7. `/scripts/generators/generate_2023_outputs.py` - 2023+ output generation
8. `/scripts/generators/generate_all_2023_outputs.py` - Comprehensive 2023+ generation
9. `/scripts/analysis/batter_bowling_type_matchup.py` - Batter vs bowling type analysis
10. `/scripts/analysis/bowler_handedness_matchup.py` - Bowler vs LHB/RHB analysis
11. `/scripts/analysis/bowler_phase_tags.py` - Bowler phase performance tags
12. `/scripts/analysis/player_clustering_v2.py` - K-means clustering
13. `/scripts/analysis/entry_point_analysis.py` - Batting entry point analysis
14. `/scripts/utils/logging_config.py` - Logging configuration
15. `/scripts/utils/validate_outputs.py` - Output validation
16. `/scripts/utils/model_serializer.py` - Model serialization
17. `/scripts/utils/generate_experience_csv.py` - Experience data generation
