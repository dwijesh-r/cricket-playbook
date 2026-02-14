# Teams Tab Data Validation Report

**Ticket:** TKT-224
**Author:** Stephen Curry (Analytics Lead)
**Date:** 2026-02-14
**Version:** 1.0
**Scope:** Read-only validation of all Teams tab data files in The Lab

---

## Executive Summary

Validated all 10 IPL 2026 team data files across teams.js, depth_charts.js, predicted_xii.js, player_profiles.js, and four supporting data files (pressure_metrics.js, momentum_insights.js, venue_data.js, historic_trends.js).

**Overall Teams Tab Grade: B+**

The data is largely complete and well-structured. Two teams (MI and RR) show budget overruns in player_profiles.js, and LSG has a phantom player (Shahbaz Ahmed) in its predicted XI who does not exist in any squad roster. Several teams have predicted XI players absent from their depth chart positions. These are addressable issues that do not break the dashboard but reduce data integrity.

---

## 1. Teams Data Completeness (teams.js)

| Team | Present | All Fields | Captain | Coach | Venue Bias | Titles | Result |
|------|---------|------------|---------|-------|------------|--------|--------|
| MI | Yes | Yes | Hardik Pandya | Mahela Jayawardene | pace | 5 | PASS |
| CSK | Yes | Yes | Ruturaj Gaikwad | Stephen Fleming | spin | 5 | PASS |
| RCB | Yes | Yes | Rajat Patidar | Andy Flower | pace | 1 | PASS |
| KKR | Yes | Yes | Ajinkya Rahane | Abhishek Nayar | spin | 3 | PASS |
| DC | Yes | Yes | Axar Patel | Hemang Badani | neutral | 0 | PASS |
| PBKS | Yes | Yes | Shreyas Iyer | Ricky Ponting | neutral | 0 | PASS |
| RR | Yes | Yes | Riyan Parag | Kumar Sangakkara | neutral | 1 | PASS |
| SRH | Yes | Yes | Pat Cummins | Daniel Vettori | pace | 1 | PASS |
| GT | Yes | Yes | Shubman Gill | Ashish Nehra | neutral | 1 | PASS |
| LSG | Yes | Yes | Rishabh Pant | Justin Langer | neutral | 0 | PASS |

**Required fields checked:** abbrev, name, fullName, homeVenue, venueBias, primaryColor, secondaryColor, titles, captain, coach, icon

**Result: 10/10 PASS**

---

## 2. Squad Rosters (player_profiles.js)

### Squad Sizes

| Team | Squad Size | Range Check (18-25) | Result |
|------|-----------|---------------------|--------|
| MI | 24 | Within range | PASS |
| CSK | 25 | Within range | PASS |
| RCB | 21 | Within range | PASS |
| KKR | 24 | Within range | PASS |
| DC | 25 | Within range | PASS |
| PBKS | 22 | Within range | PASS |
| RR | 25 | Within range | PASS |
| SRH | 25 | Within range | PASS |
| GT | 20 | Within range | PASS |
| LSG | 20 | Within range | PASS |

**Total players: 231** (matches QUICK_STATS.totalPlayers in teams.js)

### Budget Validation (120 Cr Cap)

| Team | Total Spend (Cr) | Remaining (Cr) | Result |
|------|-----------------|-----------------|--------|
| MI | 120.60 | -0.60 | **FAIL** |
| CSK | 113.60 | 6.40 | PASS |
| RCB | 116.15 | 3.85 | PASS |
| KKR | 107.60 | 12.40 | PASS |
| DC | 112.95 | 7.05 | PASS |
| PBKS | 116.05 | 3.95 | PASS |
| RR | 125.40 | -5.40 | **FAIL** |
| SRH | 115.20 | 4.80 | PASS |
| GT | 112.10 | 7.90 | PASS |
| LSG | 116.95 | 3.05 | PASS |

**Issues Found:**
- **MI exceeds 120 Cr cap by 0.60 Cr.** Top spends: Jasprit Bumrah (18.0), Hardik Pandya (16.35), Suryakumar Yadav (16.35), Rohit Sharma (16.3), Trent Boult (12.5).
- **RR exceeds 120 Cr cap by 5.40 Cr.** Top spends: Yashasvi Jaiswal (18.0), Ravindra Jadeja (17.5), Riyan Parag (14.0), Dhruv Jurel (14.0), Jofra Archer (12.5).

**Severity:** Medium. The auction data source may have rounding differences or RTM adjustments. This should be cross-checked against the official IPL 2026 auction data.

---

## 3. Depth Charts Validation (depth_charts.js)

### Position Coverage

All 10 teams have exactly 12 positions:
1. opener
2. number_3
3. middle_order
4. finisher
5. wicketkeeper
6. allrounder_batting
7. allrounder_bowling
8. right_arm_pace
9. left_arm_pace
10. off_spin
11. leg_spin
12. middle_overs_specialist

**Result: 10/10 PASS** -- all teams have complete position coverage.

### Ratings Validation (0-10 Scale)

| Team | Overall | All Ratings in 0-10 | Result |
|------|---------|---------------------|--------|
| MI | 7.2 | Yes | PASS |
| CSK | 6.5 | Yes | PASS |
| RCB | 6.8 | Yes | PASS |
| KKR | 6.3 | Yes | PASS |
| DC | 7.7 | Yes | PASS |
| PBKS | 6.6 | Yes | PASS |
| RR | 7.9 | Yes | PASS |
| SRH | 7.0 | Yes | PASS |
| GT | 6.5 | Yes | PASS |
| LSG | 6.4 | Yes | PASS |

### Notable Low-Rated Positions (< 3.0)

| Team | Position | Rating | Comment |
|------|----------|--------|---------|
| CSK | Off Spin | 2.4 | Thin depth |
| RCB | Off Spin | 1.4 | Very thin |
| KKR | Left-arm Pace | 0.0 | No coverage |
| KKR | Leg Spin | 1.1 | Very thin |
| PBKS | Off Spin | 0.0 | No coverage |
| SRH | Off Spin | 0.0 | No coverage |
| GT | Left-arm Pace | 2.1 | Thin depth |

### Weakest Position Reference Inconsistency

The `weakest` field for MI, RCB, GT, and LSG references "Left-arm Wrist Spin" but this is NOT one of the 12 tracked position keys. The position list includes `leg_spin` and `off_spin` but not `left_arm_wrist_spin`. The vulnerability text also references ratings (e.g., "Left-arm Wrist Spin: thin depth (rating 0.0)") for positions not in the positions array.

**Severity:** Low. This appears to be a computed field from a broader bowling type analysis rather than a tracked depth chart position. However, there is a data model inconsistency since the "weakest" field points to a category that cannot be visually drilled into via the positions array.

---

## 4. Predicted XII Validation (predicted_xii.js)

### XI Size and Overseas Constraints

| Team | XI Size | Overseas | Impact Sub | Size Check | Overseas Check |
|------|---------|----------|------------|------------|----------------|
| MI | 11 | 4 | Mayank Markande | PASS | PASS |
| CSK | 11 | 4 | Anshul Kamboj | PASS | PASS |
| RCB | 11 | 4 | Yash Dayal | PASS | PASS |
| KKR | 11 | 4 | Vaibhav Arora | PASS | PASS |
| DC | 11 | 4 | T Natarajan | PASS | PASS |
| PBKS | 11 | 4 | Harpreet Brar | PASS | PASS |
| RR | 11 | 4 | Tushar Deshpande | PASS | PASS |
| SRH | 11 | 4 | Harsh Dubey | PASS | PASS |
| GT | 11 | 4 | Prasidh Krishna | PASS | PASS |
| LSG | 11 | 4 | Mayank Yadav | PASS | PASS |

### Composition Balance

| Team | Batters | Keepers | All-rounders | Pace | Spin | Other | Balance Check |
|------|---------|---------|--------------|------|------|-------|---------------|
| MI | 3 | 1 | 4 | 3 | 0 | 0 | PASS (spin via AR) |
| CSK | 3 | 2 | 3 | 2 | 1 | 0 | PASS |
| RCB | 2 | 2 | 4 | 2 | 1 | 0 | PASS |
| KKR | 3 | 1 | 4 | 2 | 1 | 0 | PASS |
| DC | 2 | 2 | 4 | 2 | 1 | 0 | PASS |
| PBKS | 3 | 1 | 4 | 2 | 1 | 0 | PASS |
| RR | 3 | 1 | 3 | 3 | 1 | 0 | PASS |
| SRH | 1 | 2 | 4 | 2 | 1 | 1 | PASS (Middle Order role) |
| GT | 2 | 1 | 5 | 2 | 1 | 0 | PASS |
| LSG | 0 | 3 | 5 | 2 | 1 | 0 | **WARN** (no specialist batter, 3 WK) |

**LSG Composition Concern:** The LSG predicted XI has zero specialist "Batter" role players and three wicketkeepers (Pooran, Pant, Inglis). While this is technically balanced since keepers bat, having 3 WKs and 0 specialist batters is unusual and may warrant review.

### Predicted XII Players in Squad

| Team | All XI in Squad | Issues | Result |
|------|----------------|--------|--------|
| MI | Yes | None | PASS |
| CSK | Yes | None | PASS |
| RCB | Yes | None | PASS |
| KKR | Yes | None | PASS |
| DC | Yes | None | PASS |
| PBKS | Yes | None | PASS |
| RR | Yes | None | PASS |
| SRH | Yes | None | PASS |
| GT | Yes | None | PASS |
| LSG | **No** | **Shahbaz Ahmed not in any squad** | **FAIL** |

**Critical Issue: LSG - Shahbaz Ahmed is a phantom player.** He appears at position 8 in the LSG predicted XI with a price of 0.0 Cr but does not exist in any team's player_profiles.js roster. He must be replaced with an actual LSG squad member.

---

## 5. Cross-Reference Checks

### Predicted XII Players in Depth Charts

| Team | All XII in DC | Missing from DC | Result |
|------|--------------|-----------------|--------|
| MI | Yes | None | PASS |
| CSK | Yes | None | PASS |
| RCB | Yes | None | PASS |
| KKR | No | Angkrish Raghuvanshi, Ramandeep Singh | WARN |
| DC | No | Auqib Nabi Dar, Ashutosh Sharma | WARN |
| PBKS | Yes | None | PASS |
| RR | Yes | None | PASS |
| SRH | No | Aniket Verma, Harsh Dubey | WARN |
| GT | No | Glenn Phillips, Sai Kishore | WARN |
| LSG | No | Shahbaz Ahmed, Mayank Yadav | FAIL |

**Note:** 5 teams have predicted XI players missing from depth charts. These players are selected for the XI but their depth chart rankings are not recorded, meaning users cannot see why they were selected.

### Price Consistency (predicted_xii.js vs player_profiles.js)

| Team | Result |
|------|--------|
| MI | PASS |
| CSK | PASS |
| RCB | PASS |
| KKR | PASS |
| DC | PASS |
| PBKS | PASS |
| RR | PASS |
| SRH | PASS |
| GT | PASS |
| LSG | FAIL (Shahbaz Ahmed: 0.0 Cr in XII, not in profiles) |

### Captain Consistency (teams.js vs predicted_xii.js)

All 10 teams: **PASS** -- captains match across both files.

### Team Names Consistency

All 10 teams: **PASS** -- fullName in teams.js matches teamName in predicted_xii.js.

### Home Venue Consistency

| Team | Result | Detail |
|------|--------|--------|
| MI-LSG (9 teams) | PASS | Venues match |
| PBKS | **WARN** | teams.js: "PCA Stadium, Mohali" vs predicted_xii.js: "Punjab Cricket Association Stadium" |

Same venue, different naming convention. Minor cosmetic inconsistency.

### Team Abbreviation Consistency Across All Data Files

All 8 data files use consistent team abbreviations (MI, CSK, RCB, KKR, DC, PBKS, RR, SRH, GT, LSG). No legacy abbreviations (DD, KXIP, PWI, etc.) found.

**Result: PASS** for all files: teams.js, depth_charts.js, predicted_xii.js, player_profiles.js, pressure_metrics.js, momentum_insights.js, venue_data.js, historic_trends.js.

### DEPTH_CHART_RATINGS Consistency (predicted_xii.js vs depth_charts.js)

All 10 teams: **PASS** -- overall ratings, strongest, and weakest fields match perfectly between the DEPTH_CHART_RATINGS object in predicted_xii.js and the FULL_DEPTH_CHARTS object in depth_charts.js.

---

## 6. Data Quality Scores

Scoring methodology: 100 points possible per team.
- Squad presence and completeness: 15 pts
- Squad size in range (18-25): 10 pts
- Budget within 120 Cr: 15 pts
- Depth chart 12 positions: 10 pts
- Ratings in 0-10: 5 pts
- Predicted XI = 11 players: 10 pts
- Overseas <= 4: 5 pts
- All XI in squad: 10 pts
- All XII in depth charts: 10 pts
- Cross-file consistency: 10 pts

| Team | Score | Issues Deducted For |
|------|-------|---------------------|
| MI | 85/100 | Budget overrun (-15) |
| CSK | 100/100 | None |
| RCB | 100/100 | None |
| KKR | 90/100 | 2 XII players missing from DC (-10) |
| DC | 90/100 | 2 XII players missing from DC (-10) |
| PBKS | 98/100 | Venue name inconsistency (-2) |
| RR | 85/100 | Budget overrun (-15) |
| SRH | 90/100 | 2 XII players missing from DC (-10) |
| GT | 90/100 | 2 XII players missing from DC (-10) |
| LSG | 65/100 | Phantom player (-10), 2 XII missing from DC (-10), composition concern (-5), price mismatch (-10) |

**Average Data Quality Score: 89.3/100**

---

## 7. Issues Summary

### Critical (Must Fix)

| # | Issue | Team | Detail |
|---|-------|------|--------|
| 1 | Phantom player in predicted XI | LSG | Shahbaz Ahmed (position 8, 0.0 Cr) does not exist in any team's squad. Must replace with actual LSG player. |

### High (Should Fix)

| # | Issue | Team | Detail |
|---|-------|------|--------|
| 2 | Budget overrun | MI | Total spend 120.60 Cr exceeds 120 Cr cap by 0.60 Cr. |
| 3 | Budget overrun | RR | Total spend 125.40 Cr exceeds 120 Cr cap by 5.40 Cr. |
| 4 | XII players missing from depth charts | KKR | Angkrish Raghuvanshi and Ramandeep Singh selected for XI but not in depth charts. |
| 5 | XII players missing from depth charts | DC | Auqib Nabi Dar and Ashutosh Sharma selected for XI but not in depth charts. |
| 6 | XII players missing from depth charts | SRH | Aniket Verma and Harsh Dubey selected for XI but not in depth charts. |
| 7 | XII players missing from depth charts | GT | Glenn Phillips and Sai Kishore selected for XI but not in depth charts. |
| 8 | XII players missing from depth charts | LSG | Shahbaz Ahmed and Mayank Yadav not in depth charts. |

### Low (Nice to Fix)

| # | Issue | Team | Detail |
|---|-------|------|--------|
| 9 | Venue naming inconsistency | PBKS | "PCA Stadium, Mohali" vs "Punjab Cricket Association Stadium" across files. |
| 10 | Weakest position not in position list | MI, RCB, GT, LSG | "Left-arm Wrist Spin" referenced as weakest but not a tracked depth chart position. |
| 11 | Unusual XI composition | LSG | 3 wicketkeepers, 0 specialist batters, 5 all-rounders. |

---

## 8. Overall Assessment

**Overall Teams Tab Grade: B+**

| Category | Grade | Notes |
|----------|-------|-------|
| Data Completeness | A | All 10 teams present, all fields populated, 231 players profiled |
| Structural Integrity | A | Consistent schemas, 12 positions per team, proper JS const exports |
| Cross-File Consistency | B | Captains, names, ratings all match; venue naming and budget issues |
| Predicted XI Accuracy | B- | Phantom player (LSG), 9 players across 5 teams missing from depth charts |
| Budget Accuracy | B- | 2 teams over 120 Cr cap |
| Domain Correctness | B+ | Valid compositions, proper overseas constraints, reasonable ratings |

The Teams tab in The Lab is structurally sound and provides comprehensive data for all 10 IPL 2026 franchises. The critical Shahbaz Ahmed issue in LSG should be addressed immediately. Budget overruns for MI and RR should be investigated against source auction data. The depth chart coverage gaps for predicted XI players are a data pipeline issue that should be resolved to ensure the depth chart view fully supports the predicted XI selections.

---

*Report generated by Stephen Curry, Analytics Lead*
*Cricket Playbook v4.0.0 | Sprint 4.0*
