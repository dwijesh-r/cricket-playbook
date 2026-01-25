# Cricket Playbook - Kanban Board

**Product Owner:** Tom Brady
**Version:** 3.0.0
**Last Updated:** 2026-01-25
**Sprint:** 3.0 - Founder Review #4 Response

---

## Board Overview

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│    BACKLOG      │    TO DO        │   IN PROGRESS   │    REVIEW       │     DONE        │
│    (Icebox)     │  (Sprint 3.0)   │                 │                 │   (Sprint 2.9)  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

---

## ✅ DONE (Sprint 2.9)

| ID | Task | Owner | Completed |
|----|------|-------|-----------|
| S2.9-01 | Entry point bug fix (ball_seq > 120) | Stephen Curry | 2026-01-25 |
| S2.9-02 | Output validation script | Andy Flower | 2026-01-25 |
| S2.9-03 | Matchup missing data fix | Stephen Curry | 2026-01-25 |
| S2.9-04 | Matchup tag criteria (add BPD) | Stephen Curry | 2026-01-25 |
| S2.9-05 | Player clustering ball_seq fix | Stephen Curry | 2026-01-25 |
| S2.9-06 | GitHub Actions CI workflow | Ime Udoka | 2026-01-25 |
| S2.9-07 | Pre-commit hooks (Ruff) | Ime Udoka | 2026-01-25 |
| S2.9-08 | DEATH_LIABILITY threshold fix | Stephen Curry | 2026-01-25 |

---

## 🔍 REVIEW

| ID | Task | Status |
|----|------|--------|
| FR-4 | Founder Review #4 Scoping | **COMPLETE - See `founder_review/review_4_response.md`** |

---

## 📋 TO DO (Sprint 3.0)

### P0 - Critical Data Quality

---

#### S3.0-01: All Outputs 2023+ Versions
**Owner:** Stephen Curry | **Est:** 4h

Create 2023+ versions of all output files. Currently most are all-time IPL.

**Files requiring 2023+ versions:**
- `batter_bowling_type_detail.csv`
- `batter_bowling_type_matchup.csv`
- `bowler_handedness_matchup.csv`
- `player_tags.json`

---

#### S3.0-02: Player Clustering Output
**Owner:** Stephen Curry | **Est:** 2h

Create exportable clustering output for Founder review. Ensure it uses 2023+ data.

**Deliverable:** `outputs/player_clustering_2023.csv` with cluster assignments and features.

---

#### S3.0-03: Gurjapneet Singh Mismatch Fix
**Owner:** Brock Purdy | **Est:** 1h

CSK stat pack shows Gurjapneet Singh mapped to Gurkeerat Singh stats. Audit all packs for similar mismatches.

---

#### S3.0-04: Sanju Samson Entry Point Fix
**Owner:** Stephen Curry | **Est:** 2h

Sanju Samson classified as "middle order" when he bats 1-3. Root cause is likely flawed entry point logic or 2023+ filter missing.

---

#### S3.0-05: Krunal Pandya Vulnerability Fix
**Owner:** Stephen Curry | **Est:** 2h

RCB pack shows Krunal vulnerable to left-arm orthodox but not off-spin (which is worse). Show ALL vulnerabilities, not just one.

---

#### S3.0-06: Batter Entry Thresholds Revision
**Owner:** Stephen Curry | **Est:** 3h

Founder proposed new thresholds:
- **Top Order:** 7-72 balls (overs 2-12)
- **Middle Order:** 60-90 balls (overs 10-15)
- **Lower Order:** 90+ balls (overs 15+)

Overlap is acceptable. Derive final values from EDA.

---

### P1 - EDA & Threshold Revision

---

#### S3.0-07: EDA for All Tag Thresholds
**Owner:** Stephen Curry | **Est:** 4h

Run comprehensive EDA on IPL 2023+ data to derive data-backed thresholds for:
- Batter specialist tags (SR, avg, BPD)
- Batter vulnerability tags (include dismissals, boundaries)
- Death specialist SR (currently too low)
- Bowler phase tags
- Bowler handedness tags (wickets/ball instead of 3+ wickets)

**Output:** `analysis/threshold_eda_2023.md` with percentile analysis and recommendations.

---

#### S3.0-08: Bowler Handedness Fixes
**Owner:** Stephen Curry | **Est:** 3h

Apply same fixes as batter matchup:
- Use analytics tables
- Fix aggregation order
- Use wickets/ball ratio (not just 3+ wickets)

---

#### S3.0-09: Bowler Role Tags Revision
**Owner:** Stephen Curry | **Est:** 2h

- Death specialist: ≥1 over in overs 16+ (not just ≥3 overs)
- Add MIDDLE_AND_DEATH_SPECIALIST for bowlers who bowl both phases

---

#### S3.0-10: Consistency Index Implementation
**Owner:** Stephen Curry | **Est:** 3h

Implement from Andy Flower research:
- Overall since 2023
- Year-wise breakdown
- Include quality metrics (SR, economy, boundaries)

---

#### S3.0-11: Partnership Synergy Score
**Owner:** Stephen Curry | **Est:** 3h

Implement Partnership Synergy Score:
- Overall level
- Year-wise breakdown

---

#### S3.0-12: Pressure Sequence for Bowlers
**Owner:** Stephen Curry | **Est:** 2h

Reuse Pressure Sequence Definition for historical bowler analysis.

---

#### S3.0-13: Venue Win/Loss Per Team
**Owner:** Stephen Curry | **Est:** 2h

Add venue-based win/loss record for each team to stat packs.

---

#### S3.0-14: Bowler Phase Distribution Tables
**Owner:** Stephen Curry | **Est:** 1h

In stat packs, group bowler phase distribution by phase with proper tables.

---

### P2 - Classification & Definitions

---

#### S3.0-15: WORKHORSE/PART_TIMER Definitions
**Owner:** Andy Flower | **Est:** 2h

Clarify what WORKHORSE and PART_TIMER mean in bowler archetypes. Current definitions unclear.

**Note:** Nortje does NOT have PART_TIMER tag. DEATH_LIABILITY threshold already improved.

---

#### S3.0-16: ACCUMULATOR/PLAYMAKER Clarity
**Owner:** Andy Flower | **Est:** 2h

Define clear distinction between:
- ACCUMULATOR vs MIDDLE_ORDER
- PLAYMAKER role

---

#### S3.0-17: Batting Aggression Score Scoping
**Owner:** Andy Flower | **Est:** 2h

Scope with edge cases:
- Edged shot going for boundary = not attack-minded
- How to identify intent from ball-by-ball data

---

#### S3.0-18: Bowling Level Threat Scoping
**Owner:** Andy Flower | **Est:** 2h

Scope assumption: "caught/bowled = genuine edge with wicket-taking ability"
- Is this valid?
- What about LBW, stumped, run out?

---

#### S3.0-19: Clutch Factor Methodology
**Owner:** Andy Flower | **Est:** 2h

Clarify scoring methodology:
- Why are scores 3s?
- How are pressure situations weighted?

---

#### S3.0-20: DOCR/CI/EVS Yearly Versions
**Owner:** Stephen Curry | **Est:** 2h

Add yearly versions for fan-focused metrics (9.4, 9.5).

---

#### S3.0-21: Venue-Pitch Conditions Analysis
**Owner:** Andy Flower | **Est:** 4h

Quantify venue characteristics:
- Pace vs spin friendly
- First vs second innings advantage
- Boundary rates by venue

---

### Background Work (Parallel)

---

#### S3.0-BG-01: CI/CD Improvements
**Owner:** Ime Udoka | **Est:** 4h

Per Founder directive - work on this in parallel without blocking sprint.

---

#### S3.0-BG-02: Model Serialization
**Owner:** Ime Udoka | **Est:** 3h

Save trained models with joblib for reproducibility.

---

#### S3.0-BG-03: Great Expectations Validation
**Owner:** Brock Purdy | **Est:** 6h

Setup Great Expectations for automated data quality validation.

---

## 📦 BACKLOG (Deferred per Founder Review #4)

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
| S3.1-01 | REST API (FastAPI) | P2 |
| S3.1-02 | Real-time Match Simulation | P3 |
| S3.2-01 | Win Probability Model | P2 |
| S3.2-02 | Player Form Tracker | P2 |

---

## Agent Workload Summary

| Agent | P0 | P1 | P2 | BG | Total Tasks |
|-------|----|----|----|----|-------------|
| **Stephen Curry** | 5 | 8 | 1 | 0 | 14 |
| **Andy Flower** | 0 | 0 | 6 | 0 | 6 |
| **Brock Purdy** | 1 | 0 | 0 | 1 | 2 |
| **Ime Udoka** | 0 | 0 | 0 | 2 | 2 |

---

## Sprint 3.0 Timeline

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Data Quality | P0 fixes, 2023+ versions |
| 2 | EDA & Thresholds | Threshold revision, entry point fix |
| 3 | New Features | Consistency Index, Partnership, Venue |
| 4 | Polish | Definitions, documentation, FR-5 prep |

---

## Definition of Done

- [ ] All P0 bugs fixed
- [ ] All outputs have 2023+ versions
- [ ] EDA-backed thresholds documented
- [ ] Classification definitions clarified
- [ ] Tests pass (pytest 76+)
- [ ] CI passes (Ruff lint/format)
- [ ] Founder Review #5 ready

---

*Cricket Playbook v3.0.0 - Sprint 3.0 Kickoff*
