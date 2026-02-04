# Response to Founder Review #1

**Date:** 2026-01-21
**Review Conducted By:** Tom Brady (Product Owner), Andy Flower (Cricket Domain), Brad Stevens (Requirements)
**Status:** ACTION REQUIRED

---

## Executive Summary

The Founder Review #1 identified **37 data quality issues** in the Experience CSV and **9 methodology concerns** in the clustering model. This response categorizes each issue, assigns ownership, and outlines remediation steps.

**Severity Breakdown:**
- **P0 (Critical):** 10 issues - Player ID mismatches causing wrong stats attribution
- **P1 (High):** 18 issues - Incorrect bowling type classifications
- **P2 (Medium):** 6 issues - Missing players / squad discrepancies
- **P3 (Enhancement):** 9 issues - Clustering methodology improvements

---

## PART A: Tom Brady (Product Owner) Response

### Assessment

The founder's review reveals two systemic problems:

1. **Player ID Collision Problem (P0):** Our Cricsheet ID matching algorithm incorrectly mapped 10 uncapped IPL 2026 players to historical players with similar names. This is a data integrity failure.

2. **Bowling Type Source Gap (P1):** The bowling_type field was populated from incomplete sources, resulting in 18+ incorrect classifications.

### Immediate Actions (Sprint 2.4 - Priority Override)

| # | Action | Owner | ETA |
|---|--------|-------|-----|
| 1 | Freeze all stat pack generation until data fixes complete | Tom Brady | Immediate |
| 2 | Create `uncapped_players` flag in ipl_2026_squads table | Brock Purdy | Day 1 |
| 3 | Manual correction of all 37 flagged items | Andy Flower | Day 2-3 |
| 4 | Add data validation rule: if player has 0 IPL matches, mark as uncapped | Brock Purdy | Day 2 |
| 5 | Re-verify all 231 players against official IPL 2026 auction results | Andy Flower | Day 3-4 |
| 6 | Regenerate experience CSV with corrections | Stephen Curry | Day 5 |

### Process Improvement

We need a **Founder QA Gate** before any data artifact is marked as complete. Adding to KANBAN:
- All player data CSVs require founder spot-check before "DONE"
- Clustering outputs require founder validation of edge cases

---

## PART B: Andy Flower (Cricket Domain Expert) Response

### Issue-by-Issue Analysis

#### Category 1: Player ID Mismatches (P0 - CRITICAL)

These players are **uncapped in IPL** but were incorrectly mapped to other players' historical stats:

| # | Player | Team | Mapped To (Incorrect) | Correct Action |
|---|--------|------|----------------------|----------------|
| 1 | Kartik Sharma | CSK | Karn Sharma | Mark uncapped, clear stats |
| 2 | Gurjapneet Singh | CSK | Gurkeerat Singh Mann | Mark uncapped, clear stats |
| 6 | Mohammed Izhar | MI | Unknown player | Mark uncapped, clear stats |
| 7 | Harnoor Singh | PBKS | Harbhajan Singh | Mark uncapped, clear stats |
| 8 | Ravi Singh | RR | Rinku Singh | Mark uncapped, clear stats |
| 9 | Brijesh Sharma | RR | Unknown | Mark uncapped, clear stats |
| 10 | Abhinandan Singh | RCB | Arshdeep Singh | Mark uncapped, clear stats |
| 35 | Shivang Kumar | - | Unknown | Mark uncapped, clear stats |
| 36 | Amit Kumar | - | Unknown | Mark uncapped, clear stats |

**Root Cause:** The ID matching used fuzzy name matching which failed for common Indian surnames (Singh, Sharma, Kumar).

#### Category 2: Bowling Type Corrections (P1 - HIGH)

| # | Player | Current | Correct | Source |
|---|--------|---------|---------|--------|
| 3 | Aman Khan | Off-spin | Medium pace | Founder verification |
| 4 | Shahrukh Khan | Medium | Right-arm off-spin | Founder verification |
| 5 | Ayush Badoni | Leg-spin | Off-spin | Founder verification |
| 11 | Prashant Veer | Off-spin | Left-arm orthodox | Founder verification |
| 12 | Nitish Rana | Left-arm orthodox | Right-arm off-spin | Founder verification |
| 13 | Tristan Stubbs | Medium | Right-arm off-spin | Founder verification |
| 14 | Vipraj Nigam | Medium | Right-arm leg-spin | Founder verification |
| 16 | Gurnoor Brar | Left-arm orthodox | Right-arm fast | Founder verification |
| 17 | Rinku Singh | Medium | Right-arm off-spin | Founder verification |
| 18 | Prashant Solanki | Left-arm orthodox | Right-arm leg-spin | Founder verification |
| 19 | Daksh Kamra | - | Right-arm leg-spin | Founder verification |
| 20 | Digvesh Rathi | - | Right-arm leg-spin | Founder verification |
| 21 | Naman Dhir | - | Right-arm off-spin | Founder verification |
| 22 | Suryansh Shedge | - | Medium pace | Founder verification |
| 23 | Riyan Parag | - | Right-arm leg-spin | Founder verification |
| 24 | Yashasvi Jaiswal | - | Right-arm leg-spin | Founder verification |
| 25 | Ravi Singh | Medium | Right-arm leg-spin | Founder verification |
| 26 | Vaibhav Sooryavanshi | - | Left-arm orthodox | Founder verification |
| 27 | Vignesh Puthur | - | Left-arm leg-spin (chinaman) | Founder verification |
| 28 | Lhuan Dre Pretorius | - | NULL (doesn't bowl) | Founder verification |
| 31 | Travis Head | Left-arm orthodox | Right-arm off-spin | Founder verification |
| 32 | Liam Livingstone | Leg-spin | Both (leg-spin & off-spin) | Founder verification |
| 33 | Nitish Reddy | - | Medium pace | Founder verification |
| 34 | Kamindu Mendis | Left-arm orthodox | Both (off-spin & left-arm orthodox) | Founder verification |
| 37 | Harsh Dubey | - | Left-arm orthodox | Founder verification |

#### Category 3: Squad Composition Issues (P2 - MEDIUM)

| # | Issue | Action |
|---|-------|--------|
| 29 | RCB has Raqibul Hasan listed, should be Rasikh Salam Dar | Verify against official auction results |
| 30 | Missing from RCB: Vicky Ostwal, Vihaan Malhotra, Kanishk Chouhan | Add to squad if in official auction |

#### Category 4: Stats Corrections (P1)

| # | Player | Issue | Action |
|---|--------|-------|--------|
| 3 | Aman Khan | Listed with 75 bowling matches, actually 1 | Recalculate - clear misattributed stats |
| 4 | Shahrukh Khan | Listed with 0 bowling innings, actually 3 | Verify and update |

### Andy Flower's Recommendations

1. **Bowling Type Data Source:** We should use ESPNCricinfo player profiles as the authoritative source, cross-referenced with IPL official auction documents.

2. **Dual-Type Bowlers:** Need a schema change to support players who bowl multiple styles:
   - Liam Livingstone: Leg-spin, Off-spin
   - Kamindu Mendis: Right-arm off-spin, Left-arm orthodox

3. **Uncapped Player Handling:** Create explicit handling for players with 0 IPL matches:
   - Don't attempt Cricsheet ID matching
   - Mark as "IPL Uncapped" in all outputs
   - Exclude from historical analytics until they debut

---

## PART C: Brad Stevens (Requirements Review) Response

### Clustering Methodology Review

The founder raised 9 valid concerns about the clustering approach:

#### 1. Time Window (Recency Bias)

**Founder Question:** *"Is it better if we take only since 2021?"*

**Analysis:**
- Current: Uses all IPL history (2008-2025)
- Issue: Player styles evolve; early-career data may not reflect current form
- Recommendation: **Weight recent seasons (2021-2025) at 2x**
- Alternative: Create two cluster sets - "Career" and "Recent Form"

#### 2. Entry Points / Batting Position

**Founder Question:** *"Can we look at entry points of batters on average?"*

**Analysis:**
- Current: Not captured in clustering features
- This is a **critical missing dimension** for batter classification
- Requirement: Add `avg_batting_position` feature derived from innings data
- This distinguishes openers from middle-order from finishers

**New Feature Required:**
```sql
AVG(batting_position) AS avg_entry_point
```

#### 3. Wickets Across Phases

**Founder Question:** *"Need to look at wickets also across phases"*

**Analysis:**
- Current bowler features: economy, dot_ball_pct, boundary_conceded_pct per phase
- Missing: **wickets per phase, strike rate per phase**
- This is essential for identifying "wicket-taking" vs "containing" bowlers

**New Features Required:**
- `pp_wickets`, `mid_wickets`, `death_wickets`
- `pp_bowling_sr`, `mid_bowling_sr`, `death_bowling_sr`

#### 4. Sample Size Requirements

**Founder Question:** *"Look at overall population and then decide sample size requirements"*

**Analysis:**
- Current thresholds: 500 balls (batters), 300 balls (bowlers)
- Should be data-driven based on confidence intervals
- Recommendation: **Run population analysis to determine minimum sample for stable metrics**

#### 5. Variance Explanation Target

**Founder Question:** *"Aim for 50% variance explanation"*

**Analysis:**
- Current: No reported variance explanation
- Requirement: **Add PCA variance analysis to clustering output**
- Target: 50% variance explained by first 2-3 principal components

#### 6. Feature Overlap (Boundary/Ball)

**Founder Question:** *"Boundary/ball metric probably overlaps with boundary %"*

**Analysis:**
- Correct - these are highly correlated
- Recommendation: **Run correlation matrix and remove features with r > 0.9**

#### 7-8. Specific Player Classifications

**MS Dhoni:**
- Founder notes: "Pretty good in the death, often termed a finisher"
- Current tag: FINISHER (correct)
- Issue: Need to verify death-over performance metrics support this

**Jos Buttler, Patidar, Pant, Surya:**
- Founder notes: "Bat at 1-4 more often, then go berzerk"
- Current: May be classified as FINISHER when they're actually PLAYMAKER/EXPLOSIVE_OPENER
- Issue: Entry point analysis (item #2) would fix this

#### 9. Nortje Classification

**Founder Question:** *"Nortje isn't a part timer, re-think this"*

**Analysis:**
- Anrich Nortje is a specialist fast bowler
- If classified as PART_TIMER, this is a bug
- Need to verify his cluster assignment and fix

### Brad Stevens' Requirements Summary

| Req # | Requirement | Priority | Effort |
|-------|-------------|----------|--------|
| R1 | Add recency weighting (2x for 2021-2025) | P1 | Medium |
| R2 | Add avg_batting_position feature | P0 | Medium |
| R3 | Add wickets/strike_rate per phase for bowlers | P0 | Medium |
| R4 | Population-based sample size analysis | P1 | Low |
| R5 | PCA variance reporting (target 50%) | P2 | Low |
| R6 | Feature correlation analysis and deduplication | P2 | Low |
| R7 | Validate Dhoni/Buttler/Patidar/Pant/Surya classifications | P1 | Low |
| R8 | Fix Nortje classification | P0 | Low |

---

## Consolidated Action Plan

### Sprint 2.4 (Immediate - Data Fix Sprint)

**Theme:** Data integrity fixes before any new features

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 1 | Create uncapped player flag | Brock Purdy | Schema update |
| 1 | Document all 37 corrections in tracking sheet | Andy Flower | Corrections spreadsheet |
| 2 | Fix player ID mappings for 10 uncapped players | Brock Purdy | Updated ipl_2026_squads |
| 2 | Correct bowling types for 18 players | Andy Flower | Updated ipl_2026_squads |
| 3 | Verify RCB squad (Rasikh vs Raqibul, missing players) | Andy Flower | Squad verification |
| 3 | Add dual-bowling-type support to schema | Brock Purdy | Schema update |
| 4 | Regenerate experience CSV | Stephen Curry | New CSV |
| 5 | Founder re-validation | Founder | Sign-off |

### Sprint 2.5 (Clustering V2)

**Theme:** Methodology improvements

| Task | Owner | Deliverable |
|------|-------|-------------|
| Add batting position feature | Stephen Curry | Updated batter features |
| Add wickets/SR per phase for bowlers | Stephen Curry | Updated bowler features |
| Implement recency weighting | Stephen Curry | Weighted feature extraction |
| PCA variance analysis | Stephen Curry | Variance report |
| Feature correlation cleanup | Stephen Curry | Reduced feature set |
| Validate specific players (Dhoni, Buttler, Nortje, etc.) | Andy Flower | Classification review |
| Re-run clustering with V2 methodology | Stephen Curry | New clusters |

---

## Sign-off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Tom Brady | ACKNOWLEDGED | 2026-01-21 |
| Cricket Domain | Andy Flower | ACKNOWLEDGED | 2026-01-21 |
| Requirements | Brad Stevens | ACKNOWLEDGED | 2026-01-21 |
| Founder | - | PENDING REVIEW | - |

---

*This response was prepared in response to Founder Review #1.*
*Next review checkpoint: After Sprint 2.4 completion.*
