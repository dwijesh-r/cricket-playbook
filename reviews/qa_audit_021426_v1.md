# QA Audit Report - TKT-231

**Agent:** N'Golo Kante (QA / Stats Integrity)
**Date:** 2026-02-14
**Sprint:** 4.0 "Foundation & Editorial Excellence"
**Scope:** Comprehensive QA pass across all systems

---

## 1. Test Results Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 288 collected |
| **Passed** | 280 |
| **Skipped** | 8 |
| **Failed** | 0 |
| **Duration** | 6.60s |
| **Warnings** | 41 (non-blocking) |

**Result: PASS**

All 280 executed tests pass. 8 tests skipped (acceptable). Zero failures. 41 warnings are all deprecation-related (`datetime.utcnow()` in Mission Control modules and `ChangedInMarshmallow4Warning` from `great_expectations` dependency) -- neither is blocking.

---

## 2. Linting Results

```
ruff check . -> All checks passed!
```

**Result: PASS**

Zero violations. Code quality is clean across the entire codebase.

---

## 3. System Health Score

| Category | Weight | Score | Contribution |
|----------|--------|-------|-------------|
| Governance | 15% | 100/100 | 15.0 |
| Code Quality | 20% | 80/100 | 16.0 |
| Data Robustness | 20% | 100/100 | 20.0 |
| ML Rigor | 20% | 80/100 | 16.0 |
| Testing | 15% | 100/100 | 15.0 |
| Documentation | 10% | 100/100 | 10.0 |
| **TOTAL** | | **92.0/100** | **EXCELLENT** |

**Target: 85 | Actual: 92.0 | Gap: +7.0 above target**

**Result: PASS (exceeds target by 7 points)**

---

## 4. Data Integrity

### 4a. The Lab JS Data Files

| File | Size | Status |
|------|------|--------|
| depth_charts.js | 84,461 bytes | PASS |
| full_squads.js | 106,195 bytes | PASS |
| historic_trends.js | 13,089 bytes | PASS |
| momentum_insights.js | 34,488 bytes | PASS |
| player_profiles.js | 494,475 bytes | PASS |
| predicted_xii.js | 19,511 bytes | PASS |
| pressure_metrics.js | 130,316 bytes | PASS |
| teams.js | 3,966 bytes | PASS |
| tournament_weights.js | 8,166 bytes | PASS |
| venue_data.js | 17,813 bytes | PASS |

All 10 JS data files are non-empty and begin with valid comment headers (`/**`).

**Result: PASS**

### 4b. SQL Lab Parquet Files

- **Location:** `scripts/the_lab/dashboard/data/sql_lab/tables/`
- **Files:** 17 parquet files
- **Total size:** 15.3 MB
- **Smallest file:** dim_franchise_alias.parquet (957 bytes) -- valid, small dimension table
- **Largest file:** fact_ball.parquet (14.7 MB) -- primary fact table

All parquet files present and non-trivially sized.

**Result: PASS**

### 4c. views.sql

- **Location:** `scripts/the_lab/dashboard/data/sql_lab/views.sql`
- **Size:** 232,379 bytes
- **CREATE statements:** 163

**Result: PASS**

### 4d. table_metadata.json

- **Location:** `scripts/the_lab/dashboard/data/sql_lab/table_metadata.json`
- **Size:** 320,298 bytes

**Result: PASS**

### 4e. DuckDB Databases

| Database | Size | Tables | Status |
|----------|------|--------|--------|
| cricket_playbook.duckdb | 154.0 MB | 179 | PASS (primary) |
| ipl_ball_by_ball.duckdb | 12 KB | 0 | STALE (empty) |

**Note:** `ipl_ball_by_ball.duckdb` is empty (0 tables, 12KB). No code references this file. The actual data lives in `cricket_playbook.duckdb` (179 tables, 154MB). The stale file should be removed or documented.

**Result: PASS (with advisory)**

---

## 5. Generator Scripts

| Script | Syntax Check |
|--------|-------------|
| generate_2023_outputs.py | PASS |
| generate_all_2023_outputs.py | PASS |
| generate_depth_charts.py | PASS |
| generate_outputs.py | PASS |
| generate_player_profiles.py | PASS |
| generate_predicted_xii.py | PASS |
| generate_stat_packs.py | PASS |
| parse_founder_review.py | PASS |
| sprint_3_p1_features.py | PASS |

All 9 generator scripts pass `py_compile` with zero syntax errors.

**Result: PASS**

---

## 6. Ticket Integrity

### Ticket State Distribution

| State | Count |
|-------|-------|
| DONE | 206 (including 4 with `status` field) |
| BACKLOG | 29 |
| IDEA | 3 |
| IN_PROGRESS | 1 |
| **TOTAL** | **239** |

### Issue: Schema Inconsistency (4 tickets)

Tickets TKT-089, TKT-092, TKT-094, TKT-095 use `status` field instead of `state`. All other 228 TKT tickets use `state`. The 4 outliers are functionally DONE but their state is not queryable via the standard `state` field.

**Affected tickets:**
- TKT-089 (Toss Advantage Index) - `status: DONE`
- TKT-092 (CI/CD artifact comparison) - `status: DONE`
- TKT-094 (Insight Confidence Framework) - `status: DONE`
- TKT-095 (Silhouette score validation) - `status: DONE`

### Issue: Orphaned Sprint Reference

10 tickets (TKT-181 through TKT-190) reference `sprint_id: SPRINT-004`, but only SPRINT-000, SPRINT-001, and SPRINT-002 exist in `.mission-control/data/sprints/`. SPRINT-004 has no corresponding file.

### IDEA Tickets

7 IDEA tickets exist: 4 DONE, 3 in IDEA state. No issues.

**Result: WARN (2 issues found)**

---

## 7. Dashboard File Integrity

### The Lab Dashboard

| File | Size | Status |
|------|------|--------|
| index.html | 153,635 bytes | PASS |
| analysis.html | 95,723 bytes | PASS |
| teams.html | 275,156 bytes | PASS |
| research.html | 51,534 bytes | PASS |
| research-desk.html | 381,908 bytes | PASS |
| artifacts.html | 50,446 bytes | PASS |
| about.html | 42,367 bytes | PASS |

7 HTML files, all substantial and healthy.

**Result: PASS**

### Mission Control Dashboard

| File | Size | Status |
|------|------|--------|
| index.html | 571,160 bytes | PASS |
| sprints.html | 70,705 bytes | PASS |
| about.html | 96,485 bytes | PASS |

3 HTML files, all substantial and healthy.

**Result: PASS**

---

## Issues Summary

### Critical Issues (BLOCK-worthy)

**None.** No blocking issues found. The system is in excellent health.

### Medium Issues

| # | Issue | Impact | Recommendation |
|---|-------|--------|----------------|
| M1 | 4 tickets use `status` instead of `state` field (TKT-089, 092, 094, 095) | Dashboard/queries may miscount these tickets; currently appear as "UNKNOWN" state | Migrate these 4 tickets to use `state` field |
| M2 | SPRINT-004 referenced by 10 tickets but sprint file does not exist | Sprint tracking incomplete for TKT-181 through TKT-190 | Create SPRINT-004.json or remap tickets to correct sprint |

### Low Issues

| # | Issue | Impact | Recommendation |
|---|-------|--------|----------------|
| L1 | `ipl_ball_by_ball.duckdb` is empty/stale (12KB, 0 tables) | Confusing; no code references it | Delete or document as deprecated |
| L2 | 41 pytest warnings (datetime.utcnow deprecation) | No functional impact; Python 3.12+ deprecation | Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` in Mission Control modules |
| L3 | Model registry missing (per system health score) | ML Rigor capped at 80/100 | Implement model registry for future sprints |
| L4 | Type hint coverage at 26% | Code Quality score at 80/100 | Incremental type hint improvement |

---

## Overall QA Grade

### Grade: A-

| Area | Grade | Notes |
|------|-------|-------|
| Tests | A+ | 280/280 pass, 0 failures |
| Linting | A+ | Zero violations |
| System Health | A | 92/100, exceeds 85 target |
| Data Integrity | A | All data files valid, all dashboards healthy |
| Generator Scripts | A+ | All 9 scripts compile clean |
| Ticket Integrity | B+ | 2 medium issues (schema inconsistency + orphaned sprint) |
| Dashboard Files | A+ | All 10 HTML files present and substantial |

**Overall: A-** (no blocking issues, 2 medium issues requiring attention, 4 low-priority items)

---

## Recommendations

1. **Immediate (this sprint):** Fix the 4 tickets with `status` -> `state` field migration (TKT-089, 092, 094, 095). This is a 5-minute fix that improves data consistency.

2. **Immediate (this sprint):** Create SPRINT-004.json or remap TKT-181-190 to the correct sprint file to resolve orphaned references.

3. **Next sprint:** Remove stale `ipl_ball_by_ball.duckdb` from the data directory.

4. **Next sprint:** Address `datetime.utcnow()` deprecation warnings in Mission Control modules (`json_store.py`, `ticket.py`, `sprint.py`, `epic.py`, `state_machine.py`, `hooks.py`).

5. **Ongoing:** Continue improving type hint coverage (currently 26%) and work toward model registry implementation.

---

*Report generated by N'Golo Kante | QA / Stats Integrity*
*Cricket Playbook v4.0.0 | Sprint 4.0*
