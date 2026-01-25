# Tom Brady - Founder Review #4 Response

**Date:** 2026-01-25
**Product Owner:** Tom Brady
**Status:** SCOPING COMPLETE - READY FOR SPRINT 3.0

---

## Executive Summary

Founder Review #4 contains **32 action items** across 4 categories. I've categorized them by priority and assigned to appropriate agents.

| Priority | Count | Focus Area |
|----------|-------|------------|
| P0 (Critical) | 8 | Data quality bugs, 2023+ versions |
| P1 (High) | 12 | EDA-driven threshold revision, new outputs |
| P2 (Medium) | 8 | Classification improvements, new metrics |
| Background | 4 | CI/CD, Great Expectations (side work) |

---

## PART A: Background/Side Work Assignments

Per Founder directive, these run in parallel without blocking main sprint:

| Agent | Task | Priority |
|-------|------|----------|
| **Ime Udoka** | CI/CD improvements + Model Serialization | Background |
| **Brock Purdy** | Great Expectations Validation | Background |
| **Stephen Curry** | Bowler handedness matchup fixes | P1 |
| **Andy Flower** | Venue-Pitch Conditions Analysis | P2 |

---

## PART B: Andy Flower Research - Founder Decisions

### Items APPROVED for Implementation

| # | Item | Action | Owner |
|---|------|--------|-------|
| 2 | Pressure Sequence Definition | Reuse for **bowlers historically** | Stephen Curry |
| 3 | Clutch Factor | Clarify scoring methodology (why 3s?) | Andy Flower |
| 4 | Partnership Synergy Score | Implement overall + year-wise | Stephen Curry |
| 10 | Batting Aggression Score | Scope with edge cases (edged boundaries) | Andy Flower |
| 10 | Bowling Level Threat | Scope assumptions (caught/bowled = wicket-taking?) | Andy Flower |
| 11 | Consistency Index | Implement since 2023 + year-wise + quality metrics | Stephen Curry |
| 12 | 9.4, 9.5 (DOCR, CI, EVS, etc.) | Add yearly versions | Stephen Curry |

### Items DEFERRED to Backlog

| # | Item | Reason |
|---|------|--------|
| 1 | In-match metrics | Pre-season magazine focus |
| 1 | Match Phase Dynamics | Pre-season magazine focus |
| 5 | Fielding Impact Quantification | Founder directive |
| 6 | Tactical Pattern Recognition | No variation/length/line data |
| 7 | Intent Scoring | Edge cases need refinement first |
| 8 | Field Analysis | No field placement data |
| 9 | Section 4 (Strategic Framework) | Founder directive |
| 12 | 9.6 (TIS) | Better for post-season |

---

## PART C: Output Data Requirements

### P0 - All Outputs Need 2023+ Versions

| Output File | Current | Required | Owner |
|-------------|---------|----------|-------|
| batter_bowling_type_detail.csv | All-time IPL | Add 2023+ version | Stephen Curry |
| batter_bowling_type_matchup.csv | All-time IPL | Add 2023+ version | Stephen Curry |
| bowler_handedness_matchup.csv | All-time IPL | Add 2023+ version | Stephen Curry |
| bowler_phase_performance.csv | 2023+ only | ✅ Already done | - |
| player_tags.json | Mixed | Add 2023+ version | Stephen Curry |
| Player Clustering Output | Unknown | Create + ensure 2023+ | Stephen Curry |

### P1 - EDA-Driven Threshold Revision

All thresholds must be derived from 2023+ IPL data analysis, not arbitrary values.

| Threshold Category | Current Issue | Owner | Approach |
|--------------------|---------------|-------|----------|
| **Batter Specialist Tags** | Rigid SR/avg/BPD | Stephen Curry | Run EDA, find percentiles |
| **Batter Vulnerability Tags** | Same as specialist | Stephen Curry | Include dismissals, boundaries |
| **Batter Performance Tags** | death_specialist SR too low | Stephen Curry | Derive from 2023 death phase data |
| **Bowler Phase Tags** | Arbitrary thresholds | Stephen Curry | Already improved, validate with EDA |
| **Bowler Handedness Tags** | 3+ wickets too lenient | Stephen Curry | Use wickets/ball ratio from EDA |

### P1 - Batter Entry Thresholds (MAJOR REVISION)

Founder proposed new thresholds:

| Position | Current Logic | Founder Proposal | Notes |
|----------|--------------|------------------|-------|
| **Top Order** | ≤6 balls (1 over) | 7-72 balls (2-12 overs) | Can overlap |
| **Middle Order** | 7-24 balls | 60-90 balls (10-15 overs) | Can overlap |
| **Lower Order** | >24 balls | 90+ balls (15+ overs) | - |

**Action:** Scope this properly with EDA. Current logic may be why Sanju Samson is "middle order" when he opens.

### P1 - Bowler Role Tags Revision

| Issue | Current | Founder Proposal |
|-------|---------|------------------|
| Death specialist | ≥3 overs in 16-20 | ≥1 over in 16+ |
| Middle+Death combo | Not captured | Add "MIDDLE_AND_DEATH_SPECIALIST" |

---

## PART D: Stat Pack Issues

### P0 - Data Quality Bugs

| Issue | Description | Owner | Priority |
|-------|-------------|-------|----------|
| **Gurjapneet Singh → Gurkeerat Singh** | CSK pack has wrong player mapping | Brock Purdy | P0 |
| **Sanju Samson as Middle Order** | Should be opener (bats 1-3) | Stephen Curry | P0 |
| **Krunal Pandya vulnerability** | Off-spin worse than left-arm orthodox but not shown | Stephen Curry | P0 |

### P1 - Classification Clarifications

| Term | Issue | Action |
|------|-------|--------|
| **WORKHORSE** | Unclear definition | Andy Flower to define |
| **PART_TIMER** | Misleading for actual bowlers | Rename or refine criteria |
| **ACCUMULATOR** | May overlap with MIDDLE_ORDER | Clarify distinction |
| **PLAYMAKER** | Definition unclear | Andy Flower to define |

**Nortje Part-Timer Fix Status:** ✅ Already addressed - Nortje does NOT have PART_TIMER tag. The DEATH_LIABILITY threshold was improved with dual criteria (economy + strike rate).

### P1 - New Stat Pack Features

| Feature | Description | Owner |
|---------|-------------|-------|
| Venue-based win/loss | Per team, per venue | Stephen Curry |
| Bowler Phase distribution table | Group by phase, tabular display | Stephen Curry |

---

## PART E: Sprint 3.0 Task Breakdown

### P0 - Critical (Must Fix)

| ID | Task | Owner | Est |
|----|------|-------|-----|
| S3.0-P0-01 | All outputs 2023+ versions | Stephen Curry | 4h |
| S3.0-P0-02 | Player Clustering output for Founder | Stephen Curry | 2h |
| S3.0-P0-03 | Gurjapneet/Gurkeerat mismatch fix | Brock Purdy | 1h |
| S3.0-P0-04 | Sanju Samson entry point fix | Stephen Curry | 2h |
| S3.0-P0-05 | Krunal Pandya all vulnerabilities | Stephen Curry | 2h |
| S3.0-P0-06 | Batter Entry thresholds revision | Stephen Curry | 3h |

### P1 - High Priority

| ID | Task | Owner | Est |
|----|------|-------|-----|
| S3.0-P1-01 | EDA for all tag thresholds | Stephen Curry | 4h |
| S3.0-P1-02 | Bowler handedness fixes | Stephen Curry | 3h |
| S3.0-P1-03 | Bowler Role Tags revision | Stephen Curry | 2h |
| S3.0-P1-04 | Consistency Index (2023+ yearly) | Stephen Curry | 3h |
| S3.0-P1-05 | Partnership Synergy Score | Stephen Curry | 3h |
| S3.0-P1-06 | Pressure Sequence for bowlers | Stephen Curry | 2h |
| S3.0-P1-07 | Venue win/loss per team | Stephen Curry | 2h |
| S3.0-P1-08 | Bowler phase distribution tables | Stephen Curry | 1h |

### P2 - Medium Priority

| ID | Task | Owner | Est |
|----|------|-------|-----|
| S3.0-P2-01 | WORKHORSE/PART_TIMER definitions | Andy Flower | 2h |
| S3.0-P2-02 | ACCUMULATOR/PLAYMAKER clarity | Andy Flower | 2h |
| S3.0-P2-03 | Batting Aggression Score scoping | Andy Flower | 2h |
| S3.0-P2-04 | Bowling Level Threat scoping | Andy Flower | 2h |
| S3.0-P2-05 | Clutch Factor methodology | Andy Flower | 2h |
| S3.0-P2-06 | DOCR/CI/EVS yearly versions | Stephen Curry | 2h |
| S3.0-P2-07 | Venue-Pitch Conditions Analysis | Andy Flower | 4h |

### Background (Parallel Work)

| ID | Task | Owner | Est |
|----|------|-------|-----|
| S3.0-BG-01 | CI/CD improvements | Ime Udoka | 4h |
| S3.0-BG-02 | Model Serialization (joblib) | Ime Udoka | 3h |
| S3.0-BG-03 | Great Expectations setup | Brock Purdy | 6h |

---

## PART F: Agent Assignments Summary

| Agent | Tasks | Total Est. Hours |
|-------|-------|------------------|
| **Stephen Curry** | 16 tasks | ~35h |
| **Andy Flower** | 7 tasks | ~16h |
| **Brock Purdy** | 2 tasks | ~7h |
| **Ime Udoka** | 2 tasks | ~7h |

---

## PART G: Recommended Sprint Plan

### Week 1: Data Quality & 2023+ Versions
- All P0 bug fixes (Gurjapneet, Sanju, Krunal)
- All outputs get 2023+ versions
- Player Clustering output ready for Founder

### Week 2: EDA & Threshold Revision
- Run comprehensive EDA on 2023+ data
- Revise all tag thresholds with data backing
- Implement Batter Entry changes

### Week 3: New Features
- Consistency Index, Partnership Synergy
- Venue win/loss, Phase distribution tables
- Pressure Sequence for bowlers

### Week 4: Polish & Documentation
- Andy Flower scoping documents
- Classification definitions finalized
- Founder Review #5 preparation

---

## Sign-off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Tom Brady | SCOPING COMPLETE | 2026-01-25 |
| Founder | - | AWAITING APPROVAL | - |

---

*Tom Brady*
*Product Owner - Cricket Playbook*
