# Cricket Playbook - Kanban Board

**Product Owner:** Tom Brady
**Version:** 3.1.0
**Last Updated:** 2026-01-26
**Current Sprint:** 3.1 - Founder Review #5 Preparation
**Previous Sprint:** 3.0 - Founder Review #4 Response - **COMPLETE**

---

## Board Overview

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│    BACKLOG      │    TO DO        │   IN PROGRESS   │    REVIEW       │     DONE        │
│    (Icebox)     │  (Sprint 3.1)   │   (Sprint 3.1)  │  (Sprint 3.1)   │   (Sprint 3.0)  │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ REST API        │ S3.1-01 to -13  │                 │                 │ 22 tasks (92%)  │
│ Win Probability │ Repo Restructure│                 │                 │ 16 new outputs  │
│ Form Tracker    │ Founder Rev #5  │                 │                 │ 197 batters     │
│ Dashboard       │                 │                 │                 │ 15 ID issues    │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Sprint 3.1 Focus:** Founder Review #5 Preparation + Repo Restructure

---

## ✅ DONE (Sprint 3.0) - Founder Review #4 Response

### P0 - Critical Data Quality ✅

| ID | Task | Owner | Completed | Commit |
|----|------|-------|-----------|--------|
| S3.0-01 | All Outputs 2023+ Versions | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-02 | Player Clustering Output | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-03 | Player ID Mismatch Audit (ALL) | Brock Purdy | 2026-01-26 | cd08d7a |
| S3.0-04 | Batter Entry Point Audit (ALL) | Stephen Curry | 2026-01-26 | fbe0327 |
| S3.0-05 | Krunal Pandya Vulnerability Fix | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-06 | Batter Entry Thresholds Revision | Stephen Curry | 2026-01-26 | 3b3d10b |

### P1 - EDA & New Features ✅

| ID | Task | Owner | Completed | Commit |
|----|------|-------|-----------|--------|
| S3.0-07 | EDA for All Tag Thresholds | Stephen Curry | 2026-01-26 | 3b3d10b |
| S3.0-08 | Bowler Handedness Fixes | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-09 | Bowler Role Tags Revision | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-10 | Consistency Index Implementation | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-11 | Partnership Synergy Score | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-12 | Pressure Sequence for Bowlers | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-13 | Venue Win/Loss Per Team | Stephen Curry | 2026-01-26 | cd08d7a |
| S3.0-14 | Bowler Phase Distribution Tables | Stephen Curry | 2026-01-26 | cd08d7a |

### P2 - Definitions & Scoping ✅

| ID | Task | Owner | Completed | Deliverable |
|----|------|-------|-----------|-------------|
| S3.0-15 | WORKHORSE/PART_TIMER Definitions | Andy Flower | 2026-01-26 | Documented |
| S3.0-16 | ACCUMULATOR/PLAYMAKER Clarity | Andy Flower | 2026-01-26 | Documented |
| S3.0-17 | Batting Aggression Score Scoping | Andy Flower | 2026-01-26 | Documented |
| S3.0-18 | Bowling Level Threat Scoping | Andy Flower | 2026-01-26 | Documented |
| S3.0-19 | Clutch Factor Methodology | Andy Flower | 2026-01-26 | Documented |
| S3.0-20 | DOCR/CI/EVS Yearly Versions | Stephen Curry | 2026-01-26 | SQL templates |
| S3.0-21 | Venue-Pitch Conditions Analysis | Andy Flower | 2026-01-26 | SQL templates |

### Background Work

| ID | Task | Owner | Status |
|----|------|-------|--------|
| S3.0-BG-01 | CI/CD Improvements | Ime Udoka | **Deferred to 3.1** |
| S3.0-BG-02 | Model Serialization | Ime Udoka | Partial (script created) |
| S3.0-BG-03 | Great Expectations Validation | Brock Purdy | Documented |

---

## 📊 Sprint 3.0 Metrics

### Deliverables Created

**New Output Files (16):**
- `batter_bowling_type_detail_2023.csv`
- `batter_bowling_type_matchup_2023.csv`
- `bowler_handedness_matchup_2023.csv`
- `player_tags_2023.json`
- `player_clustering_2023.csv`
- `batter_entry_points_2023.csv`
- `batter_consistency_index.csv`
- `batter_consistency_by_year.csv`
- `partnership_synergy.csv`
- `partnership_synergy_by_year.csv`
- `bowler_pressure_sequences.csv`
- `bowler_pressure_by_year.csv`
- `bowler_role_tags.csv`
- `team_venue_records.csv`
- `team_venue_records_by_year.csv`
- `bowler_phase_distribution_grouped.csv`

**New Scripts (4):**
- `scripts/generate_all_2023_outputs.py`
- `scripts/sprint_3_p1_features.py`
- `scripts/model_serializer.py`
- `scripts/generate_2023_outputs.py`

**Analysis Documents (2):**
- `analysis/entry_point_audit_report.md`
- `analysis/threshold_eda_2023.md`

**Audit Reports (1):**
- `analysis/player_id_audit_report.md` (15 mismatches documented)

### Code Changes

| Metric | Value |
|--------|-------|
| Files Changed | 37 |
| Insertions | 10,472+ |
| Commits | 4 |
| Stat Packs Updated | 10 |

### Task Completion

| Priority | Planned | Completed | Rate |
|----------|---------|-----------|------|
| P0 | 6 | 6 | 100% |
| P1 | 8 | 8 | 100% |
| P2 | 7 | 7 | 100% |
| Background | 3 | 1 | 33% |
| **Total** | **24** | **22** | **92%** |

---

## 🔍 Key Findings

### Player ID Audit (Brock Purdy)
- **15 player ID mismatches identified**
- 6 critical (completely wrong stats)
- Root cause: Surname collisions (Singh, Sharma, Kumar, Khan)
- Full report: `analysis/player_id_audit_report.md`

### Entry Point Audit (Stephen Curry)
- **197 batters classified** with 2023+ data
- Sanju Samson: ✅ Correctly TOP_ORDER (avg 25.8 balls)
- Revised thresholds: TOP <30, MIDDLE 30-72, LOWER 72+
- Full report: `analysis/entry_point_audit_report.md`

### Vulnerability Fix
- Krunal Pandya: ✅ All vulnerabilities now shown (off-spin, LA orthodox, LA wrist spin)
- Bowler handedness: Now uses wickets/ball ratio instead of raw counts

---

## 📋 Sprint 3.1 - Founder Review #5 Preparation

**Sprint Goal:** Prepare for Founder Review #5 with clean data, clean repo, and comprehensive documentation.

**Sprint Duration:** 2026-01-27 to 2026-02-02

---

### 🎯 Major Milestone: Founder Review #5

| Phase | Description | Status |
|-------|-------------|--------|
| Pre-Review | Fix player IDs, regenerate outputs, clean repo | **TO DO** |
| Review | Present to Founder for feedback | Scheduled |
| Post-Review | Address feedback items | TBD |

---

### P0 - Critical (Must Have for Review)

| ID | Task | Owner | Priority | Status |
|----|------|-------|----------|--------|
| S3.1-01 | Fix 15 Player ID mismatches in ETL | Brock Purdy | P0 | To Do |
| S3.1-02 | Regenerate all outputs with fixed IDs | Stephen Curry | P0 | Blocked by S3.1-01 |
| S3.1-03 | Regenerate stat packs with corrected data | Stephen Curry | P0 | Blocked by S3.1-02 |
| S3.1-04 | Validate corrected outputs (QA) | N'Golo Kanté | P0 | Blocked by S3.1-03 |

### P1 - Repo Restructure (Brad Stevens + Tom Brady)

| ID | Task | Owner | Priority | Status |
|----|------|-------|----------|--------|
| S3.1-05 | Delete stale root KANBAN.md | Tom Brady | P1 | To Do |
| S3.1-06 | Delete duplicate files (see proposal) | Brad Stevens | P1 | To Do |
| S3.1-07 | Consolidate reviews into `reviews/` directory | Brad Stevens | P1 | To Do |
| S3.1-08 | Create `docs/specs/` and move clustering docs | Brad Stevens | P1 | To Do |
| S3.1-09 | Archive legacy scripts to `scripts/archive/` | Brad Stevens | P1 | To Do |
| S3.1-10 | Update docs/README.md with new structure | Tom Brady | P1 | To Do |

**Reference:** See `docs/REPO_RESTRUCTURE_PROPOSAL.md` for full details.

### P2 - Infrastructure (Carryover)

| ID | Task | Owner | Priority | Status |
|----|------|-------|----------|--------|
| S3.1-11 | CI/CD caching and artifacts | Ime Udoka | P2 | Deferred |
| S3.1-12 | Great Expectations pipeline integration | Brock Purdy | P2 | To Do |
| S3.1-13 | Model serialization completion | Ime Udoka | P2 | Partial |

### Background Work

| ID | Task | Owner | Status |
|----|------|-------|--------|
| S3.1-BG-01 | Test coverage expansion | N'Golo Kanté | To Do |
| S3.1-BG-02 | Script documentation (README) | Brad Stevens | To Do |

---

### Sprint 3.1 Success Criteria

- [ ] All 15 player ID mismatches fixed in ETL
- [ ] All outputs regenerated with correct IDs
- [ ] All 10 stat packs regenerated
- [ ] Repo restructure Phase 1 & 2 complete
- [ ] Founder Review #5 ready

---

### Dependencies

```
S3.1-01 (Fix IDs)
    └── S3.1-02 (Regenerate outputs)
            └── S3.1-03 (Regenerate stat packs)
                    └── S3.1-04 (QA validation)
                            └── Founder Review #5
```

---

## 📦 BACKLOG (Icebox)

### Deferred Items

| Item | Reason |
|------|--------|
| In-match metrics | Pre-season magazine focus |
| Match Phase Dynamics | Pre-season magazine focus |
| Fielding Impact Quantification | Founder directive |
| Tactical Pattern Recognition | No variation/length/line data |
| Intent Scoring | Edge cases need refinement |
| Field Analysis | No field placement data |
| Section 4 (Strategic Framework) | Founder directive |
| TIS (9.6) | Better for post-season |

### Future Sprints

| ID | Task | Priority |
|----|------|----------|
| S3.2-01 | REST API (FastAPI) | P2 |
| S3.2-02 | Real-time Match Simulation | P3 |
| S3.3-01 | Win Probability Model | P2 |
| S3.3-02 | Player Form Tracker | P2 |

---

## ✅ Definition of Done - Sprint 3.0

- [x] All P0 bugs fixed
- [x] All outputs have 2023+ versions
- [x] EDA-backed thresholds documented
- [x] Classification definitions clarified
- [x] Tests pass (pytest 76+)
- [x] CI passes (Ruff lint/format)
- [ ] Founder Review #5 ready (pending ID fixes)

---

## Sprint 3.0 Retrospective

### What Went Well
- All P0 and P1 tasks completed in single day
- Comprehensive player audits (197 batters, 15 ID mismatches)
- 16 new 2023+ output files created
- Full EDA documentation with percentile analysis

### What Could Improve
- Background tasks (CI/CD) deprioritized due to rate limits
- Player ID fixes identified but not yet implemented in ETL

### Action Items for Sprint 3.1
1. Fix 15 player ID mismatches in ETL pipeline
2. Regenerate stat packs with corrected player mappings
3. Complete CI/CD improvements

---

*Tom Brady - Product Owner*
*Sprint 3.0 Closed: 2026-01-26*
*Cricket Playbook v3.0.1*
