# KKR Season Preview -- Andy Flower Domain Review

**Reviewer:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-22
**Document Reviewed:** `outputs/season_previews/KKR_season_preview.md` (v1.0)
**Cross-Referenced Against:** DuckDB raw queries on `analytics_ipl_*_since2023` and `analytics_ipl_*_alltime` views
**Data Window Declared:** IPL 2023-2025 (match_date >= '2023-01-01')
**Stats Cross-Checked:** 47 individual stat claims verified against DuckDB

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Cricket Accuracy | 30% | 5.5/10 | 1.65 |
| Tactical Credibility | 25% | 8.0/10 | 2.00 |
| Sample Size Honesty | 20% | 5.0/10 | 1.00 |
| Domain Nuance | 25% | 8.5/10 | 2.125 |
| **Overall** | **100%** | | **6.78** |

**Verdict: FAIL (threshold 9.0). Requires significant corrections before publication.**

---

## Summary of Findings

The KKR season preview demonstrates strong tactical reasoning and genuine cricket domain knowledge. The narrative structure is excellent and the bold takes are well-argued. However, the document suffers from three systematic data integrity problems that render it unpublishable in its current form:

1. **All-time vs since-2023 scope mixing (CRITICAL):** At least 7 stat claims use all-time data while the document explicitly declares a "since 2023" data window. This violates the fundamental promise to the reader.

2. **Fabricated league averages (CRITICAL):** All 6 league average figures cited in the Category Ratings and Phase-Wise Batting tables are incorrect, producing vastly inflated differentials that make KKR appear significantly better relative to the league than they actually are.

3. **Phase x Bowling Type cross-reference table mislabeled (HIGH):** All 5 entries in the Phase x Bowling Type table use overall (all-phases-combined) batter-vs-type data but present them as phase-specific figures.

4. **Overall innings context SR errors (MEDIUM):** The overall Setting/Chasing SR figures are mathematically incorrect.

5. **Eden Gardens venue discrepancies (MEDIUM):** Match count, RPO, and dot ball percentage claims deviate from DB values.

---

## Error Log: All Errors Found

### BLOCKING Errors (Must Fix Before Publication)

#### Error 1: Narine Powerplay SR Uses All-Time Data
**Lines:** 128, 136
**Preview Claims:** "Narine at 171.1 PP SR (672 balls, HIGH)"
**DB Since-2023:** 167.24 SR, 290 balls, MEDIUM (`analytics_ipl_batter_phase_since2023`)
**DB All-Time:** 171.13 SR, 672 balls, HIGH (`analytics_ipl_batter_phase_alltime`)
**Impact:** Wrong SR (171.1 vs 167.2), wrong ball count (672 vs 290), wrong confidence label (HIGH vs MEDIUM). The since-2023 figure is 3.9 points lower. The ball count of 672 exceeds Narine's entire since-2023 batting career of 439 balls, making the scope violation obvious.

#### Error 2: Rahane All-Time Powerplay SR Used Alongside Since-2023 Data
**Line:** 22
**Preview Claims:** "a powerplay SR of 122.8 (2,083 balls career, HIGH), 23.5 points below the league average of 146.3"
**DB Since-2023:** 168.77 SR, 301 balls, MEDIUM (`analytics_ipl_batter_phase_since2023`)
**DB All-Time:** 122.76 SR, 2,083 balls, HIGH (`analytics_ipl_batter_phase_alltime`)
**Impact:** The preview uses Rahane's all-time PP SR (122.8) in a document scoped to since-2023, where his PP SR is actually 168.8 -- a 46-point difference that completely inverts the narrative. Rahane's since-2023 PP batting is excellent, not "23.5 points below league average." The league average of 146.3 cited here is itself only correct as a DB benchmark figure, while the 121.2 used elsewhere in the preview for the same "league average" is wrong. This error fundamentally mischaracterizes Rahane's PP contribution.

#### Error 3: Rinku Death SR Uses All-Time Data
**Lines:** 56, 130, 302, 432
**Preview Claims:** "191.8 death SR (317 balls, MEDIUM)"
**DB Since-2023:** 197.1 SR, 241 balls, MEDIUM (`analytics_ipl_batter_phase_since2023`)
**DB All-Time:** 191.8 SR, 317 balls, MEDIUM (`analytics_ipl_batter_phase_alltime`)
**Impact:** Wrong SR (191.8 vs 197.1), wrong ball count (317 vs 241). The since-2023 figure is actually higher (197.1), which strengthens the narrative. Used at 4 different locations in the document.

#### Error 4: Rinku Middle SR Uses All-Time Data
**Line:** 302
**Preview Claims:** "112.1 SR, 406 balls, MEDIUM"
**DB Since-2023:** 116.89 SR, 296 balls, MEDIUM (`analytics_ipl_batter_phase_since2023`)
**DB All-Time:** 112.07 SR, 406 balls, MEDIUM (`analytics_ipl_batter_phase_alltime`)
**Impact:** Wrong SR (112.1 vs 116.9), wrong ball count (406 vs 296). The narrative about Rinku being "average" in the middle overs is weaker with the since-2023 figure (116.9 vs 112.1).

#### Error 5: Narine Death Batting SR Uses All-Time Data
**Line:** 292
**Preview Claims:** "his 128.9 death SR (121 balls, MEDIUM)"
**DB Since-2023:** 176.92 SR, 26 balls, LOW (`analytics_ipl_batter_phase_since2023`)
**DB All-Time:** 128.93 SR, 121 balls, MEDIUM (`analytics_ipl_batter_phase_alltime`)
**Impact:** Extremely wrong. Since-2023 shows 176.9 SR (26 balls, LOW), not 128.9 (121 balls, MEDIUM). The since-2023 sample is tiny (26 balls) with LOW confidence, which should be explicitly caveated. The all-time figure makes Narine appear far less dangerous at the death than his recent form suggests.

#### Error 6: Powell Death SR Uses All-Time Data
**Line:** 72, 432
**Preview Claims:** "193.4 death SR (121 balls, MEDIUM)"
**DB Since-2023:** 172.41 SR, 58 balls, LOW (`analytics_ipl_batter_phase_since2023`)
**DB All-Time:** 193.39 SR, 121 balls, MEDIUM (`analytics_ipl_batter_phase_alltime`)
**Impact:** Wrong SR (193.4 vs 172.4), wrong ball count (121 vs 58), wrong confidence label (MEDIUM vs LOW). The since-2023 figure is 21 points lower and carries LOW confidence. This overstates Powell's finishing value in the current window.

#### Error 7: All League Average Figures Are Incorrect
**Lines:** 128-134, 136, 146-151, 159-163
**Preview Claims (Category Ratings):**
- PP Batting League Avg SR: 121.2
- Middle Batting League Avg SR: 120.4
- Death Batting League Avg SR: 145.9
- PP Bowling League Avg RPO: 7.82
- Death Bowling League Avg RPO: 9.32

**DB Values (`analytics_ipl_batting_benchmarks_since2023` and `analytics_ipl_bowling_benchmarks_since2023`):**
- PP Batting League Avg SR: **146.3**
- Middle Batting League Avg SR: **140.3**
- Death Batting League Avg SR: **170.2**
- PP Bowling League Avg Economy: **9.26**
- Death Bowling League Avg Economy: **10.87**

**Impact:** CRITICAL. Every league average is wrong. The effect is to vastly inflate KKR's relative performance. For example:
- KKR PP batting (150.4 SR) is presented as "+29.2 above league" when the actual differential is **+4.1**.
- KKR middle batting (139.9 SR) is presented as "+19.5 above league" when KKR is actually **-0.4 below league average**.
- KKR death batting (174.7 SR) is presented as "+28.8 above league" when the actual differential is **+4.5**.
- KKR PP bowling (9.68 econ) is presented as "1.86 above league" when the actual differential is **+0.42 above league**.
- KKR death bowling (10.26 econ) is presented as "above league (9.32)" when the actual league average is **10.87**, making KKR actually **0.61 below (better than) league average**.

These errors fundamentally alter every relative assessment in the document. The same wrong league averages cascade through the vs. Bowling Types table (lines 146-151), where 145.9 is used for pace and 120.4 for spin. Actual benchmarks: Fast 152.6, Fast-Medium 150.6, Leg-spin 144.6, LA Orthodox 133.2, RA Off-spin 137.8, Wrist-spin 129.1.

---

### HIGH Errors (Should Fix Before Publication)

#### Error 8: Phase x Bowling Type Cross-Reference Table Is Systematically Mislabeled
**Lines:** 169-176
All 5 entries in this table present overall (all-phases-combined) batter-vs-type data as phase-specific figures.

| Row | Preview Claim | What Data Actually Shows | DB Phase-Specific Value |
|-----|--------------|--------------------------|------------------------|
| PP vs Fast-Medium | "167.1 (Narine), 161 balls" | Narine overall vs FM: 167.08, 161 balls | Narine PP vs FM: **168.12 SR, 138 balls, HIGH** |
| Middle vs Off-spin | "87.8 (Rinku), 49 balls" | Rinku overall vs RA off-spin: 87.76, 49 balls | Rinku middle vs RA off-spin: **84.09 SR, 44 balls, MEDIUM** |
| Death vs Fast | "175.0 (Rinku), 200.0 (Green), 156 + 128 balls" | Rinku overall vs Fast: 175.0, 156; Green overall vs Fast: 171.88, 128 | Rinku death vs Fast: **200.0 SR, 104 balls, HIGH**; Green death vs Fast: **198.33 SR, 60 balls, MEDIUM** |
| Middle vs LA Orthodox | "103.0 (Raghuvanshi), 33 balls" | Raghuvanshi overall vs LA Orth: 103.03, 33 balls | Raghuvanshi middle vs LA Orth: **106.45 SR, 31 balls, MEDIUM** |
| PP vs Leg-spin | "187.8 (Narine), 41 balls" | Narine overall vs Leg-spin: 187.8, 41 balls | Narine PP vs Leg-spin: **0.0 SR, 1 ball, LOW** (essentially no sample) |

**Impact:** The table purports to show "Phase x Bowling Type" cross-references, which is the most granular and revealing analysis possible. Instead, it shows overall figures with phase labels, which is misleading. In the case of "PP vs Leg-spin" for Narine, the actual PP vs leg-spin sample is 1 ball -- effectively zero data -- while the preview presents 41 balls of overall data as if it were PP-specific. The death-overs figures for Rinku and Green are actually much higher in the phase-specific data (200.0 and 198.3 respectively) than the overall figures presented (175.0 and 171.9), meaning the table actually understates KKR's death batting strength vs pace.

#### Error 9: Overall Innings Context SR Figures Are Incorrect
**Lines:** 199
**Preview Claims:** Setting Overall 152.7, Chasing Overall 151.3, Delta -1.4
**DB Computed (from analytics_ipl_team_batting_by_innings_since2023):**
- Setting: (1184+1663+1083) / (792+1188+614) * 100 = 3930/2594 * 100 = **151.5**
- Chasing: (993+1270+512) / (655+909+299) * 100 = 2775/1863 * 100 = **149.0**
- Delta: **-2.5**, not -1.4

**Impact:** Both overall SR figures are inflated by approximately 1-2 points. The delta is also wrong (-2.5 vs -1.4), though the directional conclusion (marginally better when setting) holds.

---

### MEDIUM Errors (Should Fix)

#### Error 10: Eden Gardens Match Count
**Lines:** 207
**Preview Claims:** "22 IPL matches since 2023"
**DB Value:** 21 matches (verified from `dim_match`)
**Impact:** Minor numerical error. Affects venue stat context.

#### Error 11: Eden Gardens Venue Phase Stats
**Lines:** 212-215
Several venue phase RPO figures deviate from DB values:

| Phase | Preview RPO | DB Computed RPO | Delta |
|-------|------------|----------------|-------|
| Powerplay | 9.95 | 9.99 | -0.04 |
| Middle | 8.92 | 8.97 | -0.05 |
| Death | 11.67 | 11.81 | -0.14 |

The dot ball percentages also differ: PP dot preview says 45.1%, DB computes 41.8% (a 3.3-point error). These are computed from `analytics_ipl_venue_profile_since2023` aggregated across both innings.

#### Error 12: KKR Home Record Loss Count
**Line:** 231
**Preview Claims:** "9-11 (42.9% win rate)"
**DB Value:** 9 wins, 11 losses, 1 no-result in 21 total matches. 9/21 = 42.9%.
**Impact:** The W-L record of 9-11 omits the 1 no-result. Should read "9-11-1" or "9-11 (1 NR)". Win percentage is technically correct as 9/21.

---

### LOW Errors / Minor Issues

#### Error 13: Varun Bowler Phase Description
**Line:** 354
**Preview Claims:** "His 7.36 middle-overs economy is 1.24 runs below Varun's 8.60 death economy"
**Assessment:** While arithmetically correct (8.60 - 7.36 = 1.24), comparing Narine's middle-overs economy to Varun's death-overs economy is a confusing cross-metric comparison that doesn't prove the stated conclusion ("he is the best bowler in every phase he bowls"). A more meaningful comparison would be Narine's middle-overs economy (7.36) vs Varun's middle-overs economy (8.01).

#### Error 14: Rinku Wrist-Spin SR in Table
**Line:** 151
**Preview Claims:** "Wrist-spin: 128.9 (Rinku 128.9)"
**DB Value:** 128.95 SR (38 balls, LOW)
**Impact:** Correctly rounded. No error in the value itself, but the LOW confidence label should be noted.

---

## Stats Verified as Correct (25+ cross-checks)

The following claims were verified against DuckDB and found to be correct or within acceptable rounding:

| Stat Claim | Preview Value | DB Value | Location | Verdict |
|-----------|---------------|----------|----------|---------|
| Narine career batting SR | 172.0 (439 balls, HIGH) | 171.98 (439, HIGH) | L59 | MATCH |
| Narine middle bowling econ | 7.36 (117 ov, HIGH) | 7.36 (117.0, HIGH) | L59, 132 | MATCH |
| Narine death bowling econ | 7.47 (17 ov, MEDIUM) | 7.47 (17.0, MEDIUM) | L40, 347 | MATCH |
| Varun career economy | 8.15 (152.8 ov, HIGH), 58 wkts | 8.15 (152.8, 58, HIGH) | L62 | MATCH |
| Varun middle econ | 8.01 (94.2 ov, HIGH) | 8.01 (94.2, HIGH) | L132, 348 | MATCH |
| Varun death econ | 8.60 (27.7 ov, MEDIUM) | 8.60 (27.7, MEDIUM) | L348 | MATCH |
| Pathirana career econ | 9.00 (110.2 ov, HIGH), 45 wkts | 9.00 (110.2, 45, HIGH) | L61 | MATCH |
| Pathirana death econ | 9.46 (64.2 ov, MEDIUM), 33 wkts | 9.46 (64.2, 33, MEDIUM) | L61, 349 | MATCH |
| Pathirana middle econ | 8.35 (46 ov, MEDIUM) | 8.35 (46.0, MEDIUM) | L349 | MATCH |
| Harshit career econ | 9.64 (103.2 ov, HIGH), 39 wkts | 9.64 (103.2, 39, HIGH) | L60 | MATCH |
| Harshit PP econ | 9.74 (47 ov, MEDIUM) | 9.74 (47.0, MEDIUM) | L350 | MATCH |
| Harshit death econ | 9.82 (26.2 ov, MEDIUM) | 9.82 (26.2, MEDIUM) | L350 | MATCH |
| Green career batting SR | 154.7 (457 balls, MEDIUM) | 154.7 (457, MEDIUM) | L54 | MATCH |
| Green death batting SR | 200.0 (102 balls, MEDIUM) | 200.0 (102, MEDIUM) | L54 | MATCH |
| Green middle bowling econ | 8.24 (41 ov, MEDIUM) | 8.24 (41.0, MEDIUM) | L351 | MATCH |
| Rahane career SR | 147.6 (649 balls, HIGH) | 147.61 (649, HIGH) | L32, 53 | MATCH |
| Raghuvanshi career SR | 145.1 (319 balls, MEDIUM) | 145.14 (319, MEDIUM) | L55 | MATCH |
| Raghuvanshi middle SR | 136.4 (184 balls, MEDIUM) | 136.41 (184, MEDIUM) | L314 | MATCH |
| Rinku career SR | 152.2 (557 balls, HIGH) | 152.24 (557, HIGH) | L56 | MATCH |
| Arora PP econ | 9.03 (58.2 ov, MEDIUM) | 9.03 (58.2, MEDIUM) | L131, 352 | MATCH |
| Arora death econ | 10.59 (20.5 ov, MEDIUM) | 10.59 (20.5, MEDIUM) | L352 | MATCH |
| Ramandeep SR | 179.2 (96 balls, MEDIUM) | 179.17 (96, MEDIUM) | L57 | MATCH |
| Tripathi SR | 129.1 (382 balls, MEDIUM) | 129.06 (382, MEDIUM) | L70 | MATCH |
| Pandey SR | 122.5 (240 balls, MEDIUM) | 122.5 (240, MEDIUM) | L71 | MATCH |
| Ravindra SR | 145.4 (284 balls, MEDIUM) | 145.42 (284, MEDIUM) | L69 | MATCH |
| KKR 2023 PP batting SR | 129.2 | 129.2 | L94 | MATCH |
| KKR 2024 PP batting SR | 168.1 | 168.1 | L104 | MATCH |
| KKR 2025 middle batting SR | 121.8 | 121.8 | L115 | MATCH |
| Innings context (Setting) | 22 matches, 12 wins (54.5%) | 22-12 (54.5%) | L187 | MATCH |
| Innings context (Chasing) | 19 matches, 10 wins (52.6%) | 19-10 (52.6%) | L188 | MATCH |
| H2H: KKR vs RCB since 2023 | 4-1, 80.0% | 4-1, 80.0% (combined RCB names) | L256 | MATCH |
| H2H: KKR vs SRH since 2023 | 5-2, 71.4% | 5-2, 71.4% | L258 | MATCH |
| H2H total since 2023 | 22-18, 55.0% | 22-18, 55.0% | L266 | MATCH |
| Varun vs RCB | 9 wkts, 8.04 econ | 9 wkts, 8.04 econ | L256 | MATCH |
| Varun vs GT | 0 wkts, 10.20 econ | 0 wkts, 10.2 econ | L263 | MATCH |
| Harshit vs PBKS | 12.17 economy | 12.17 econ | L264 | MATCH |
| Arora vs SRH | 8 wkts, 7.44 econ | 8 wkts, 7.44 econ | L258 | MATCH |
| Rinku at Eden Gardens | 497 runs, 160.3 SR (310 balls, HIGH) | 497, 160.32, 310, HIGH | L229 | MATCH |
| Narine at Eden Gardens | 359 runs, 160.3 SR (224 balls, HIGH) | 359, 160.27, 224, HIGH | L229 | MATCH |
| Narine bowling at Eden | 7.16 econ, 16 wkts, 21 matches | 7.16, 16, 21 | L227 | MATCH |
| Varun bowling at Eden | 8.52 econ, 29 wkts, 21 matches (HIGH) | 8.52, 29, 21, HIGH | L227 | MATCH |
| All-time H2H total | 120-115, 51.1% | 120-115 (current teams combined) | L282 | MATCH |
| KKR all-time vs MI | 11-24, 31.4% | 11-24, 31.4% | L277 | MATCH |
| KKR all-time vs CSK | 11-20, 35.5% | 11-20, 35.5% | L278 | MATCH |

---

## Criterion-by-Criterion Assessment

### 1. Cricket Accuracy (30%): 5.5/10

The foundational stat work is strong -- 40+ individual player stats verified as correct. The bowler phase data is accurate across the board. The team phase yearly data is accurate. H2H records are correct. Venue-specific player stats are correct.

However, the document is undermined by three systematic failures:
- **7 instances of all-time data used in a since-2023 document** (Narine PP SR, Rahane PP SR, Rinku death SR, Rinku middle SR, Narine death SR, Powell death SR, plus cascading references)
- **All 6 league averages are wrong**, inflating every relative comparison
- **All 5 phase x type cross-reference entries use wrong data scope** (overall vs phase-specific)

These are not random transcription errors; they suggest a systematic pipeline issue where all-time and overall-scope data are being pulled when phase-specific since-2023 data is required. The volume of correct stats (40+) shows the underlying data infrastructure works. The errors are concentrated in derived/comparative figures.

### 2. Tactical Credibility (25%): 8.0/10

The tactical analysis is the preview's strongest section. Specific highlights:

- **The off-spin vulnerability thesis** is directionally correct. Rinku vs RA off-spin (87.76 SR, 49 balls), Green vs RA off-spin (100.0 SR, 31 balls), and Rahane vs RA off-spin (95.45 SR, 44 balls) all verify. The tactical recommendation to bowl off-spin in overs 7-15 is sound cricket.
- **The Narine deployment dilemma** (open vs #8) is a genuine tactical question with well-argued trade-offs.
- **The Pathirana middle-overs deployment insight** (8.35 middle econ vs 9.46 death econ) is a genuinely useful coaching observation.
- **The opposition blueprint** is tactically credible and actionable.

Score is capped at 8.0 because the wrong league averages distort the magnitude of KKR's advantages. When the league PP batting SR is actually 146.3 (not 121.2), KKR's 150.4 is only marginally above average, not "29.2 points above" -- which changes the tactical emphasis from "dominant PP approach" to "slightly above average PP approach."

### 3. Sample Size Honesty (20%): 5.0/10

The document includes confidence labels (HIGH/MEDIUM/LOW) on most stats, which is good practice. However:

- **6 confidence labels are wrong** due to using all-time data. When the since-2023 figure is used, several MEDIUM labels become LOW (e.g., Powell death: 58 balls = LOW, not 121 balls = MEDIUM; Narine death batting: 26 balls = LOW, not 121 balls = MEDIUM).
- **The phase x bowling type table uses overall ball counts** which inflate apparent sample sizes (e.g., Narine "PP vs Leg-spin: 41 balls" when actual PP vs leg-spin is 1 ball).
- **LOW samples are generally caveated well** in the narrative text. The writing around Rinku's off-spin vulnerability ("49 balls, LOW") and Green's injury concerns is epistemically honest.
- **Cross-tournament confidence labels** (Finn Allen, Tim Seifert) are appropriately flagged as "cross-tournament" to distinguish from IPL-specific data.

The structural problem is that wrong data sourcing (all-time instead of since-2023) cascades into wrong confidence labels, creating a false sense of reliability for several key claims.

### 4. Domain Nuance (25%): 8.5/10

This is the preview's strength. Specific instances of genuine cricket knowledge:

- **The 2023-2024-2025 trajectory analysis** correctly identifies the 32.7-point middle-overs SR collapse as the defining story of KKR's recent history. The year-by-year tables are accurate.
- **The Green deployment analysis** (batting at 3, bowling in the middle, not at the death given his 12.0 death economy) shows sophisticated role understanding.
- **The Narine workload concern** (148 overs in 2 seasons at age 37) is a genuine cricket insight about the physical demands of the dual role.
- **The Allen uncertainty framing** is excellent: acknowledging that cross-tournament dominance (177 SR) may not translate to IPL spin conditions, without dismissing the potential.
- **The Raghuvanshi leg-spin strength** (167.2 SR vs leg-spin, 67 balls, MEDIUM) is a correctly identified and verified prospect insight.
- **The "spin-first, pace-finishing" identity** accurately captures KKR's squad construction philosophy.

Score is 8.5 rather than 9+ because the wrong league averages lead to some inflated claims about KKR's dominance that a domain expert would question. When the middle-overs batting SR (139.9) is actually below league average (140.3), the narrative framing of "+19.5 above league" is not just wrong -- it's the opposite of reality.

---

## Required Fixes (Priority Order)

### BLOCKING (Must Fix)

1. **Replace all league average figures** with correct DB values from `analytics_ipl_batting_benchmarks_since2023` and `analytics_ipl_bowling_benchmarks_since2023`. Recalculate all differentials. This affects lines 128-136, 146-151, 159-163, 317, 410, 439, and all "above/below league" language.

2. **Replace all all-time data with since-2023 data.** Specifically:
   - Narine PP SR: 167.2 (290 balls, MEDIUM), not 171.1 (672 balls, HIGH)
   - Rahane PP SR context on line 22: since-2023 is 168.8 (301 balls, MEDIUM), not 122.8 (2,083 balls, HIGH). The narrative about Rahane being below league PP average must be rewritten since he is actually above average in the since-2023 window.
   - Rinku death SR: 197.1 (241 balls, MEDIUM), not 191.8 (317 balls, MEDIUM). Update at lines 56, 130, 302, 432.
   - Rinku middle SR: 116.9 (296 balls, MEDIUM), not 112.1 (406 balls, MEDIUM). Update at line 302.
   - Narine death batting SR: 176.9 (26 balls, LOW), not 128.9 (121 balls, MEDIUM). Update at line 292. This requires narrative adjustment and LOW confidence caveat.
   - Powell death SR: 172.4 (58 balls, LOW), not 193.4 (121 balls, MEDIUM). Update at lines 72, 432.

3. **Rebuild the Phase x Bowling Type Cross-Reference table** (lines 169-176) using data from `analytics_ipl_batter_vs_bowler_type_phase_since2023` instead of `analytics_ipl_batter_vs_bowler_type_since2023`. Add proper confidence labels from the phase-specific data.

### HIGH (Should Fix)

4. **Correct overall innings context SR** (line 199): Setting should be 151.5 (not 152.7), Chasing should be 149.0 (not 151.3), Delta should be -2.5 (not -1.4).

5. **Correct Eden Gardens match count** (line 207): 21 matches, not 22.

6. **Correct Eden Gardens venue phase stats** (lines 212-215): Death RPO should be 11.81 (not 11.67), PP dot% should be ~41.8% (not 45.1%).

### MEDIUM (Should Fix)

7. **Clarify home record** (line 231): Should note 1 no-result in the 21 matches.

8. **Fix the cross-metric comparison** (line 354): Compare Narine middle to Varun middle (not Varun death) to support the "best bowler in every phase" claim.

---

## Structural Recommendations

1. **Implement a scope validation check** in the generation pipeline. Any stat where the ball count exceeds the player's since-2023 career total should be automatically flagged. Narine's 672-ball PP claim (vs 439 career balls) would have been caught instantly.

2. **League averages should be pulled from benchmark views**, not hardcoded or generated independently. The `analytics_ipl_batting_benchmarks_since2023` and `analytics_ipl_bowling_benchmarks_since2023` views exist and contain correct values.

3. **Phase x Bowling Type analysis should use the dedicated phase-specific view** (`analytics_ipl_batter_vs_bowler_type_phase_since2023`), not the overall view with phase labels added narratively.

---

## Final Assessment

The KKR preview reads well as cricket analysis. The tactical sections demonstrate genuine understanding of T20 dynamics, squad construction trade-offs, and matchup exploitation. The narrative voice is engaging and the bold takes are defensible.

However, the data integrity failures are too numerous and too systematic to pass at the 9.0 threshold. The wrong league averages alone would be a blocking issue, as they distort every relative assessment in the document. Combined with 7 instances of all-time data in a since-2023 document and a systematically mislabeled cross-reference table, the accuracy score cannot exceed 5.5.

Once the blocking and high-priority fixes are applied, this preview has the potential to score 9.0+ on re-review. The underlying cricket intelligence is strong; it is the data plumbing that needs correction.

**Score: 6.78/10 -- FAIL. Resubmit after corrections.**

---

*Review generated by Andy Flower (Cricket Domain Expert) | Cricket Playbook v5.0.0*
*47 stats cross-checked against DuckDB | 14 errors identified | 40+ stats verified correct*
