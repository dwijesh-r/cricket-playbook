# SRH Season Preview -- Jose Mourinho Quant Review v1.0

**Reviewer:** Jose Mourinho (Quant Researcher)
**Date:** 2026-02-22
**Document Reviewed:** `outputs/season_previews/SRH_season_preview.md` (v1.0)
**Stat Pack Referenced:** `stat_packs/SRH/SRH_stat_pack.md`
**Data Source:** `data/cricket_playbook.duckdb` (DuckDB, read-only)
**Confidence System:** HIGH >= 200 balls/50 overs, MEDIUM >= 50 balls/15 overs, LOW < 50 balls/15 overs

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Statistical Rigor | 40% | 6.0/10 | 2.40 |
| Analytical Depth | 30% | 8.5/10 | 2.55 |
| Methodology Transparency | 20% | 5.5/10 | 1.10 |
| Quantitative Consistency | 10% | 4.0/10 | 0.40 |
| **Overall** | **100%** | | **6.45/10** |

**Verdict: FAIL (threshold 9.0). Requires fixes to 7 blocking errors and 5 non-blocking issues before publication.**

---

## Executive Summary

The SRH Season Preview is an analytically ambitious and narratively compelling document. The architecture is strong: season-by-season phase evolution, innings context analysis, vs-bowling-type matrices, phase x bowling type cross-references, and a bold take section built on a clear thesis. The writing quality is among the best in the series.

However, the document contains **7 blocking errors** that undermine its credibility. The most damaging is a fundamentally incorrect batting-first vs chasing win rate that forms the backbone of the preview's entire thesis. The preview claims SRH have a 35.0% batting-first win rate (20 matches, 7 wins) versus 52.2% chasing (23 matches, 12 wins). The database shows 44.0% batting first (25 matches, 11 wins) versus 44.4% batting second (18 matches, 8 wins). The difference is not marginal; the preview fabricates a 17.2-point gap where none exists. The chase-centric narrative that permeates multiple sections (Bold Take, Keys to Victory, Verdict) is consequently built on false premises.

Additionally, there is systematic **scope mixing** between "since 2023" and all-time IPL data. Several player phase stats (Livingstone death SR, Abhishek PP SR in the stat pack) use all-time IPL scope while the document header declares "IPL 2023-2025." Multiple individual bowler phase economies (Cummins middle, Cummins death, Harshal death) do not match either the since-2023 or all-time values in the database, suggesting calculation errors.

---

## Verification Ledger: Stats Checked Against DuckDB

### VERIFIED CORRECT (18 stats)

| # | Claim | Preview Value | DB Value | Status |
|---|-------|--------------|----------|--------|
| 1 | Klaasen career SR since 2023 | 175.2 SR, 807 balls, HIGH | 175.22 SR, 807 balls | PASS |
| 2 | Klaasen runs since 2023 | 1,414 runs | 1,414 runs | PASS |
| 3 | Abhishek career SR since 2023 | 186.5 SR, 616 balls, HIGH | 186.53 SR, 616 balls | PASS |
| 4 | Head career SR since 2023 | 181.0 SR, 520 balls, HIGH | 180.96 SR, 520 balls | PASS |
| 5 | Livingstone career SR since 2023 | 153.1 SR, 328 balls, MEDIUM | 153.05 SR, 328 balls | PASS |
| 6 | Cummins economy since 2023 | 9.32 econ, 110.7 ov, 34 wkts, HIGH | 9.32 econ, 110.7 ov, 34 wkts | PASS |
| 7 | Harshal economy since 2023 | 9.91 econ, 140 ov, HIGH | 9.91 econ, 140.0 ov | PASS |
| 8 | SRH PP batting SR since 2023 | 152.3 | 152.3 (2357/1548*100) | PASS |
| 9 | SRH middle batting SR since 2023 | 144.1 | 144.1 (3299/2290*100) | PASS |
| 10 | SRH death batting SR since 2023 | 164.4 | 164.4 (1896/1153*100) | PASS |
| 11 | SRH PP bowling economy since 2023 | 9.68 | 9.68 (2556*6/1584) | PASS |
| 12 | SRH middle bowling economy since 2023 | 9.09 | 9.09 (3548*6/2342) | PASS |
| 13 | SRH death bowling economy since 2023 | 11.13 | 11.13 (1982*6/1068) | PASS |
| 14 | Abhishek setting SR | 166.3 SR, 326 balls | 166.26 SR, 326 balls | PASS |
| 15 | Abhishek chasing SR | 209.3 SR, 290 balls | 209.31 SR, 290 balls | PASS |
| 16 | SRH home record | 8-10, 42.1%, 19 matches | 8W-10L, 42.1%, 19 matches | PASS |
| 17 | Head at Arun Jaitley | 229.2 SR, 72 balls | 229.17 SR, 72 balls | PASS |
| 18 | Klaasen vs CSK | 96.4 SR, 56 balls | 96.43 SR, 56 balls | PASS |

### VERIFIED CORRECT -- Team Season Phase Data (All 18 cells)

All 18 data points in the year-over-year Team Style Analysis tables match the database exactly:

| Season | Phase | Batting SR (Preview/DB) | Bowling Econ (Preview/DB) |
|--------|-------|------------------------|--------------------------|
| 2023 | PP | 125.2 / 125.2 | 9.30 / 9.30 |
| 2023 | Middle | 134.5 / 134.5 | 8.50 / 8.50 |
| 2023 | Death | 154.2 / 154.2 | 10.30 / 10.30 |
| 2024 | PP | 177.6 / 177.6 | 9.48 / 9.48 |
| 2024 | Middle | 143.1 / 143.1 | 9.58 / 9.58 |
| 2024 | Death | 166.7 / 166.7 | 11.91 / 11.91 |
| 2025 | PP | 150.2 / 150.2 | 10.30 / 10.30 |
| 2025 | Middle | 155.4 / 155.4 | 9.13 / 9.13 |
| 2025 | Death | 173.8 / 173.8 | 11.14 / 11.14 |

### VERIFIED CORRECT -- Selected Recent Form Data

| Player | L10 SR (Preview/DB) | Career SR (Preview/DB) |
|--------|--------------------|-----------------------|
| Abhishek Sharma | 197.1 / 197.10 | 186.5 / 186.53 (since 2023) |
| Klaasen | 171.0 / 171.00 | 175.2 / 175.22 (since 2023) |
| Livingstone | 124.2 / 124.21 | 153.1 / 153.05 (since 2023) |
| Cummins | 157.1 / 157.14 | 153.0 / 153.00 (since 2023) |

### VERIFIED CORRECT -- Head-to-Head Since 2023

| Opponent | Preview W-L (Win%) | DB W-L (Win%) | Status |
|----------|-------------------|---------------|--------|
| Punjab Kings | 4-0 (100.0%) | 4-0 (100.0%) | PASS |
| Rajasthan Royals | 4-1 (80.0%) | 4-1 (80.0%) | PASS |
| RCB (combined) | 2-2 (50.0%) | 2-2 (50.0%) | PASS (split alias 2-1 + 0-1) |
| CSK | 2-2 (50.0%) | 2-2 (50.0%) | PASS |
| KKR | 2-5 (28.6%) | 2-5 (28.6%) | PASS |
| MI | 1-5 (16.7%) | 1-5 (16.7%) | PASS |
| GT | 0-4 (0.0%) | 0-4 (0.0%) | PASS |
| LSG | 2-3 (40.0%) | 2-3 (40.0%) | PASS |

---

## BLOCKING ERRORS (7)

### ERROR 1: Batting First vs Chasing Win Rate (CRITICAL -- Thesis-Breaking)

**Location:** Innings Context section, Bold Take section, Keys to Victory #1, Verdict

**Preview Claims:**
- Batting first: 20 matches, 7 wins, 35.0%
- Batting second: 23 matches, 12 wins, 52.2%
- "17.2 percentage point gap"
- "SRH are a markedly better chasing team"

**Database Values:**
- Batting first: 25 matches, 11 wins, 44.0%
- Batting second: 19 matches, 8 wins, 44.4% (excluding 1 NR)
- Gap: 0.4 percentage points (functionally zero)

**Impact:** CRITICAL. The entire strategic thesis of the preview is built on this claim. The Bold Take ("SRH's biggest problem is not their bowling. It is that they bat first too often and too passively when they do"), Keys to Victory #1 ("Win the Toss and Chase"), and the Verdict are all predicated on a massive batting-first vs chasing gap that does not exist. The match counts (20 + 23 = 43) also do not reconcile with the total matches since 2023 (44 including 1 NR).

**Fix:** Replace all batting-first/chasing claims with the correct values: 25 matches batting first (11W, 44.0%), 19 matches batting second (8W, 44.4%). Rewrite the Bold Take section to reflect the actual equilibrium between contexts. Remove the chase-centric strategic recommendations or replace with a different analytical angle.

### ERROR 2: Harshal Patel Death-Overs Economy

**Location:** Category Ratings (Bowling, Death), Bowler Phase table, Scouting Report

**Preview Claims:**
- Harshal death economy: 9.78 (56.8 overs, HIGH)
- "Harshal Patel carries the [death bowling] unit"

**Database Values (since 2023, analytics view):**
- Harshal death economy: 10.80 (56.8 overs, MEDIUM in analytics view, or 10.54 bowler-charged runs)
- All-time IPL death economy: 10.24 (140 overs)

**Impact:** The claimed 9.78 does not match any calculation method (total runs, bowler-charged runs, since 2023, or all-time). The actual death economy of 10.80 is 1.02 runs per over worse than claimed, which changes the death bowling rating from "adequate specialist" to "expensive."

**Fix:** Replace 9.78 with 10.80 (since 2023, 56.8 overs). Adjust the Bowling Death rating and associated narrative accordingly.

### ERROR 3: Livingstone Death SR Scope Error

**Location:** Predicted XII table, Livingstone profile, Category Ratings (Batting, Death), Scouting Report

**Preview Claims:**
- Livingstone death SR: 227.8 (151 balls, MEDIUM)

**Database Values:**
- IPL since 2023: 234.0 SR (100 balls, MEDIUM)
- All-time IPL: 227.8 SR (151 balls) -- this is the value used, but it is all-time, not since 2023
- All T20 since 2023: 202.9 SR (477 balls)

**Impact:** The document header declares "IPL 2023-2025" as the data window. Using all-time IPL data for Livingstone's death SR while other players use since-2023 scope creates a methodological inconsistency. The since-2023 IPL value (234.0, 100 balls) is actually higher, so this understates his death SR within the declared scope, but the ball count is lower (100 vs 151), which changes the confidence assessment.

**Fix:** Use 234.0 SR (100 balls, MEDIUM) for since-2023 IPL scope, or explicitly note this is all-time IPL career data. Adjust the "57.6 points above league average" calculation accordingly (if league average of 170.2 is used: 234.0 - 170.2 = 63.8 above).

### ERROR 4: Cummins Middle-Overs Economy

**Location:** Story section, Category Ratings, Keys to Victory #3, Scouting Report

**Preview Claims:**
- Cummins middle-overs economy: 7.50 (36 overs, HIGH)

**Database Values:**
- Since 2023 (analytics view): 7.72 (36 overs, 216 balls, 278 runs, MEDIUM)
- Since 2023 (bowler-charged): 7.72 (278 runs)
- All-time IPL: 8.04 (79 overs)

**Impact:** The claimed 7.50 does not match any calculation method. The actual 7.72 is 0.22 runs per over higher. While directionally still positive (below league average), the specific number cited is fabricated.

**Fix:** Replace 7.50 with 7.72 in all occurrences.

### ERROR 5: Cummins Death Economy

**Location:** Players to Watch (Cummins), Category Ratings

**Preview Claims:**
- Cummins death economy: 10.63 (30.7 overs, HIGH)

**Database Values:**
- Since 2023 (analytics view): 10.89 (30.7 overs, 184 balls, 334 runs, MEDIUM)
- Since 2023 (bowler-charged): 10.76
- All-time IPL: 10.52 (74.5 overs)

**Impact:** The claimed 10.63 does not match any scope or calculation method. The since-2023 value is 10.89 (total runs) or 10.76 (bowler-charged). Neither matches 10.63.

**Fix:** Replace 10.63 with 10.89 (total runs) or 10.76 (bowler-charged), using whichever methodology is standard for the preview series. Clarify in methodology notes.

### ERROR 6: DC Head-to-Head Record Omission

**Location:** Head-to-Head table

**Preview Claims:**
- Delhi Capitals: 2-2 (50.0%)

**Database Values:**
- 2-2-1 (5 matches: 2 wins, 2 losses, 1 no result). Win percentage: 40.0% (2/5) or 50.0% (2/4 excluding NR).

**Impact:** The preview reports 2-2 without noting the 5th match (a no-result on 2025-05-05). While the win percentage of 50.0% may be defensible if NR matches are excluded, the match count is wrong by omission. Across the H2H table, total matches (4+5+3+4+5+5+7+6+4 = 43) reconcile with 43 decided results + 1 NR = 44 total. The DC row should show 5 matches.

**Fix:** Change DC entry to show 5 matches total with the NR noted: "2-2 (1 NR)" or "2-2-1 (40.0% / 50.0% excl. NR)."

### ERROR 7: Harshal Total Wickets

**Location:** Predicted XII table, Full Squad Table

**Preview Claims:**
- Harshal Patel: 9.91 econ / 54 wkts (140 overs, HIGH)

**Database Values:**
- Bowling wickets (excl. run outs): 54
- All wickets (incl. run outs credited to bowler): 62
- The stat pack section 6.1 also says 54 wkts, which matches bowling wickets only

**Impact:** This is marginal. The 54 wickets figure represents bowling-attributed dismissals only. The stat pack section 6.2 shows 35 death wickets (HV Patel death) + 15 middle + 4 PP = 54. However, the stat pack section 3.5 shows "HV Patel: Econ 10.25 (9 wkts)" at the death for the "Key Phase Players (2026 Squad)" table, while section 6.2 shows 35 death wickets. This internal discrepancy within the stat pack suggests the 54 is consistently used but the Key Phase Players table uses a different methodology.

**Fix:** Verify whether 54 or 62 is the intended convention and apply consistently. If using bowling-only wickets (54), this is correct. Add a methodology note.

---

## NON-BLOCKING ISSUES (5)

### ISSUE 1: Scope Mixing Between "Since 2023" and All-Time IPL

**Affected Areas:** Livingstone death SR (227.8 = all-time, not since 2023), Abhishek PP SR in stat pack section 5.2 (161.84 from 629 balls = all-time, vs 178.22 from 404 balls since 2023), Livingstone PP SR (141.5 from 118 balls = all-time, vs 84.6 from 39 balls since 2023).

The stat pack section 5.2 ("Phase-wise Batting") uses all-time IPL career data, but the preview header declares "Data Window: IPL 2023-2025." When the preview draws on stat pack section 5.2 data (as it does for Livingstone), it inherits the scope inconsistency.

**Fix:** Audit all player-level phase stats against the `analytics_ipl_batter_phase_since2023` and `analytics_ipl_bowler_phase_since2023` views. Replace any all-time values with since-2023 values, or explicitly flag when all-time data is used.

### ISSUE 2: Klaasen Death SR Discrepancy Between Preview and Stat Pack

**Preview Claims:** 199.6 SR (277 balls, MEDIUM)
**Stat Pack Section 5.2:** 199.64 SR (277 balls) -- this is the all-time IPL value
**DB Since 2023:** 206.5 SR (246 balls)
**DB All-Time IPL:** 199.64 SR (277 balls)

The preview uses the all-time figure (199.6) while the since-2023 value is 206.5. This is another instance of scope mixing. Since 2023, Klaasen's death SR is actually *higher* (206.5) than the reported 199.6.

**Fix:** Use 206.5 SR (246 balls, MEDIUM) for since-2023 scope. Adjust "27.4% boundary rate" and related claims accordingly.

### ISSUE 3: Zeeshan Ansari Middle Economy

**Preview Claims:** 9.87 economy across 33.8 overs (overall)
**Also Claims:** "SRH's best spin option" with economy "1.11 runs above the league middle-overs average of 8.76"

The preview uses Ansari's overall economy (9.87) when comparing to the league middle-overs average. His actual middle-overs economy from the analytics view is 9.47 (30 overs, 284 runs). The difference from league average would then be 0.71, not 1.11.

**Fix:** Use middle-overs specific economy (9.47) when making phase-specific comparisons, not overall economy.

### ISSUE 4: Livingstone PP Dot Ball Rate

**Preview Claims:** 51.7% PP dot ball rate (118 balls, MEDIUM)

This is from the all-time IPL data (stat pack section 5.2: 118 balls). The since-2023 IPL data shows 39 balls in the PP with 64.1% dot rate. The number used is from a different scope and is more optimistic than the since-2023 reality (64.1% vs 51.7%).

**Fix:** Use since-2023 IPL data (64.1%, 39 balls, LOW) or flag the scope explicitly.

### ISSUE 5: Klaasen at Arun Jaitley Stadium -- Minor Data Discrepancy

**Preview Claims:** 236.1 SR across 72 balls, average of 170.0
**Analytics View:** 236.11 SR, 170 runs, 72 balls
**Raw DB Query:** 240.28 SR, 173 batter_runs, 72 balls

There is a 3-run discrepancy between the analytics view (170 runs) and the raw fact_ball query (173 batter_runs). The preview uses the analytics view value (236.1/170), so it is internally consistent with the view, but the underlying data suggests 240.3 SR from 173 runs. This appears to be a data processing artifact in the venue view generation.

**Fix:** Investigate the analytics view generation for venue batting to identify the source of the 3-run discrepancy. Low priority as the difference is minor, but it affects data integrity.

---

## Analytical Depth Assessment

Despite the statistical errors, the preview demonstrates strong analytical architecture:

1. **Phase x Bowling Type Cross-Reference:** The death vs fast (208.1 SR) and middle vs off-spin (126.8 SR) breakdowns are exactly the kind of layered analysis that separates this product from typical previews. This is well-constructed.

2. **Season-over-Season Phase Evolution:** The 2023-2024-2025 progression tables are well-designed and verified accurate (all 18 cells match the DB).

3. **Individual Setting/Chasing Splits:** The Abhishek Sharma setting/chasing analysis is excellent and verified (166.3 vs 209.3 SR). However, the team-level setting/chasing thesis built on top of these individual stats is invalidated by the wrong win rate data.

4. **Venue Phase Profile:** The Uppal venue breakdown by phase and innings is well-structured.

5. **Opposition Blueprint in Scouting Report:** The specific matchup recommendations (bowl off-spin middle overs, left-arm orthodox to Livingstone, avoid fast bowling to Klaasen at death) are tactically sound and supported by the data.

---

## Methodology Transparency Assessment

The methodology transparency score is low because:

1. **No explicit scope declaration per stat.** The header says "IPL 2023-2025" but multiple stats use all-time IPL data without flagging the scope change. A reader cannot distinguish which stats are since-2023 and which are all-time.

2. **Economy calculation method is unclear.** Some numbers appear to use total_runs (batter runs + all extras), others use bowler-charged runs (batter + wides + noballs only). The Harshal death economy (9.78) matches neither method.

3. **The setting/chasing methodology is not explained.** The incorrect match counts (20 + 23 = 43 vs actual 25 + 19 = 44) suggest the methodology for determining batting context may be flawed at the source.

---

## Quantitative Consistency Assessment

The consistency score is low because:

1. **Cummins overall economy (9.32) uses total_runs,** but his phase economies (7.50 middle, 10.63 death) do not sum to the overall when weighted by overs. The weighted sum of the claimed phase economies: (9.32 * 44 + 7.50 * 36 + 10.63 * 30.7) / 110.7 = 9.16, which does not match the claimed 9.32 overall. This is internally inconsistent.

2. **Harshal death economy (9.78) is inconsistent** with the stat pack (10.25 in section 3.5 Key Phase Players) and the analytics view (10.80).

3. **The setting/chasing data does not reconcile** with the season records (2023: 4W, 2024: 9W, 2025: 6W = 19 total wins, but preview claims 7 + 12 = 19 wins in different splits vs DB's 11 + 8 = 19 wins in different splits).

---

## Required Fixes Summary

### Blocking (Must fix before publication)

| # | Error | Current Value | Correct Value | Sections Affected |
|---|-------|--------------|---------------|-------------------|
| 1 | Batting 1st/2nd win rate | 35.0% / 52.2% (20/23 matches) | 44.0% / 44.4% (25/19 matches) | Innings Context, Bold Take, Keys to Victory #1, Verdict |
| 2 | Harshal death economy | 9.78 (56.8 ov) | 10.80 (56.8 ov) | Category Ratings, Bowler Phase, Scouting Report |
| 3 | Livingstone death SR scope | 227.8 (151 balls, all-time) | 234.0 (100 balls, since 2023) | XII table, Livingstone profile, Ratings, Scouting Report |
| 4 | Cummins middle economy | 7.50 (36 ov) | 7.72 (36 ov) | Story, Ratings, Keys #3, Scouting Report |
| 5 | Cummins death economy | 10.63 (30.7 ov) | 10.89 (30.7 ov) | Cummins profile, Ratings |
| 6 | DC H2H match count | 2-2 (4 matches) | 2-2-1 (5 matches) | Head-to-Head table |
| 7 | Harshal wickets convention | 54 wkts (inconsistent with stat pack 3.5) | Clarify: 54 bowling wkts or note discrepancy | XII table, stat pack alignment |

### Non-Blocking (Should fix)

| # | Issue | Action |
|---|-------|--------|
| 1 | Scope mixing (since 2023 vs all-time) | Audit all player phase stats against since2023 views |
| 2 | Klaasen death SR | Update from 199.6 (all-time) to 206.5 (since 2023) |
| 3 | Ansari middle economy comparison | Use 9.47 (middle-specific) not 9.87 (overall) for phase comparison |
| 4 | Livingstone PP dot ball rate | Use since-2023 value (64.1%, LOW) or flag scope |
| 5 | Klaasen Delhi venue SR | Investigate 3-run gap between view (170) and raw data (173) |

---

## Structural Recommendation

The single most important fix is ERROR 1. The chase-centric thesis is foundational to the preview's narrative architecture. With the correct data showing virtually identical win rates in both contexts (44.0% vs 44.4%), the Bold Take, Keys to Victory #1, and the strategic framing throughout the document must be substantially rewritten.

Possible alternative analytical angles that are supported by the verified data:
- SRH's true structural problem is the gap between batting quality (6.5-7.5/10 across phases) and bowling quality (3.5-4.5/10), which is correctly identified but undercut by the chase thesis
- Abhishek Sharma's individual setting/chasing split (166.3 vs 209.3) is real and analytically interesting, even if it does not translate to team-level context advantage
- The 2024 to 2025 powerplay regression (177.6 to 150.2 SR) and what it means for 2026 is a strong analytical thread already present

The team-level and individual-level data are strong where correctly sourced. The problems are in cherry-picked stats that use the wrong scope and in the fabricated setting/chasing win rate. Fix those, and this is a high-quality preview.

---

*Jose Mourinho | Quant Researcher | Cricket Playbook v5.0.0*
*All claims verified against `data/cricket_playbook.duckdb` via direct SQL queries on fact_ball, dim_match, dim_team, dim_player, and analytics views.*
