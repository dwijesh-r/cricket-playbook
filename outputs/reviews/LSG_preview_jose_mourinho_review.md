# LSG Season Preview -- Jose Mourinho Quant Review v1.0

**Reviewer:** Jose Mourinho (Quant Researcher)
**Date:** 2026-02-22
**Document Reviewed:** `outputs/season_previews/LSG_season_preview.md` (v1.0)
**Data Source:** `data/cricket_playbook.duckdb` (DuckDB, read-only)
**Confidence System:** HIGH >= 200 balls/50 overs, MEDIUM >= 50 balls/15 overs, LOW < 50 balls/15 overs

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Statistical Rigor | 40% | 7.5/10 | 3.00 |
| Analytical Depth | 30% | 8.5/10 | 2.55 |
| Methodology Transparency | 20% | 8.0/10 | 1.60 |
| Quantitative Consistency | 10% | 6.5/10 | 0.65 |
| **Overall** | **100%** | | **7.80/10** |

**Verdict: FAIL (threshold 9.0). Requires fixes to 5 blocking errors and 4 non-blocking issues.**

---

## Executive Summary

The LSG Season Preview is an analytically ambitious document. It covers team-level phase evolution across three seasons, individual player vs bowler-type matchups, innings context splits (setting vs chasing) at both team and individual levels, and a bold take grounded in phase economics. The narrative architecture is strong, and the analytical depth is among the best I have reviewed.

However, the document contains 5 blocking statistical errors -- most critically, a fabricated match count in the setting/chasing section (85 total matches claimed when LSG played 43), an incorrect CSK head-to-head record, a wrong death bowling aggregate economy, league average inaccuracies, and unverifiable Mayank Yadav stats. There are also 4 non-blocking issues related to minor rounding/overs discrepancies and an inconsistent death batting league average. These must be corrected before publication.

---

## Verification Ledger: Stats Checked Against DuckDB

### VERIFIED CORRECT (22 stats)

| # | Claim | Preview Value | DB Value | Status |
|---|-------|--------------|----------|--------|
| 1 | Pooran SR since 2023 | 183.9 SR, 751 balls, HIGH | 183.89 SR, 751 balls, HIGH | PASS |
| 2 | Pant SR since 2023 | 146.2 SR, 489 balls, MEDIUM | 146.22 SR, 489 balls, MEDIUM | PASS |
| 3 | Marsh SR since 2023 | 158.1 SR, 516 balls, MEDIUM | 158.14 SR, 516 balls, MEDIUM | PASS |
| 4 | Markram SR since 2023 | 136.3 SR, 670 balls, HIGH | 136.27 SR, 670 balls, HIGH | PASS |
| 5 | Samad SR since 2023 | 158.0 SR, 326 balls, HIGH | 157.98 SR, 326 balls, HIGH | PASS |
| 6 | Badoni SR since 2023 | 142.5 SR, 563 balls, HIGH | 142.45 SR, 563 balls, HIGH | PASS |
| 7 | Inglis SR since 2023 | 162.6 SR, 171 balls, MEDIUM | 162.57 SR, 171 balls, MEDIUM | PASS |
| 8 | Shahbaz Ahmed SR since 2023 | 124.9 SR, 213 balls, MEDIUM | 124.88 SR, 213 balls, MEDIUM | PASS |
| 9 | Shami economy since 2023 | 9.25 econ, 95.2 ov, 34 wkts, MEDIUM | 9.25 econ, 95.2 ov, 34 wkts, MEDIUM | PASS |
| 10 | Avesh economy since 2023 | 9.96 econ, 131.2 ov, 40 wkts, HIGH | 9.96 econ, 131.2 ov, 40 wkts, HIGH | PASS |
| 11 | Hasaranga economy since 2023 | 9.07 econ, 70 ov, 20 wkts, MEDIUM | 9.07 econ, 70 ov, 20 wkts, MEDIUM (as PWH de Silva) | PASS |
| 12 | Rathi economy since 2023 | 8.37 econ, 52 ov, 14 wkts, MEDIUM | 8.37 econ, 52 ov, 14 wkts, MEDIUM | PASS |
| 13 | Nortje economy since 2023 | 10.94 econ, 69 ov, 18 wkts, MEDIUM | 10.94 econ, 69 ov, 18 wkts, MEDIUM | PASS |
| 14 | Shami PP economy | 8.67 econ, 66 ov, 22 wkts, 49.0% dot, MEDIUM | 8.67 econ, 66 ov, 22 wkts, 48.99% dot, MEDIUM | PASS |
| 15 | Pant death SR | 210.0 SR, 100 balls, MEDIUM | 210.00 SR, 100 balls, MEDIUM | PASS |
| 16 | Pooran middle SR | 183.9 SR, 390 balls, MEDIUM | 183.85 SR, 390 balls, MEDIUM | PASS |
| 17 | Samad death SR | 178.9 SR, 194 balls, MEDIUM | 178.87 SR, 194 balls, MEDIUM | PASS |
| 18 | LSG PP batting aggregate SR | 133.9 | 133.9 (2073/1548*100) | PASS |
| 19 | LSG middle batting aggregate SR | 142.1 | 142.1 (3302/2323*100) | PASS |
| 20 | LSG death batting aggregate SR | 161.5 | 161.5 (1899/1176*100) | PASS |
| 21 | LSG PP bowling aggregate economy | 9.91 | 9.91 (2498*6/1513) | PASS |
| 22 | LSG middle bowling aggregate economy | 8.54 | 8.54 (3184*6/2236) | PASS |

### VERIFIED CORRECT -- Team Season Phase Data (All 18 cells)

All 18 data points in the Team Style Analysis year-over-year tables (2023, 2024, 2025 x 3 phases x batting SR and bowling economy) match the database exactly:

| Season | Phase | Batting SR (Preview/DB) | Bowling Econ (Preview/DB) |
|--------|-------|------------------------|--------------------------|
| 2023 | PP | 124.1 / 124.1 | 9.15 / 9.15 |
| 2023 | Middle | 127.4 / 127.4 | 7.59 / 7.59 |
| 2023 | Death | 156.5 / 156.5 | 9.68 / 9.68 |
| 2024 | PP | 131.0 / 131.0 | 9.84 / 9.84 |
| 2024 | Middle | 141.4 / 141.4 | 8.52 / 8.52 |
| 2024 | Death | 161.7 / 161.7 | 11.80 / 11.80 |
| 2025 | PP | 147.4 / 147.4 | 10.73 / 10.73 |
| 2025 | Middle | 158.7 / 158.7 | 9.52 / 9.52 |
| 2025 | Death | 166.2 / 166.2 | 11.27 / 11.27 |

### VERIFIED CORRECT -- Recent Form (All 14 data points)

All batter recent form stats (L10 SR, career SR, delta) match the DB within rounding tolerance (max 0.05 deviation from rounding to 1 decimal). All bowler recent form stats (L10 economy, career economy, delta) match precisely.

### VERIFIED CORRECT -- Setting vs Chasing SR (Team and Individual)

Team and individual setting/chasing SRs all match the database:
- Team setting: PP 132.2, Mid 144.9, Death 173.9 -- all match DB exactly
- Team chasing: PP 136.3, Mid 138.3, Death 139.9 -- all match DB exactly (DB: 136.27, 138.27, 139.86)
- Individual splits for all 6 batters match precisely

### VERIFIED CORRECT -- Bowler Innings Context Splits

All bowler bowl-first vs defending economies match the DB exactly (Shami 9.89/8.53, Avesh 10.73/9.09, Hasaranga 8.52/9.57, Rathi 10.25/7.53, Mohsin 10.54/10.05).

### VERIFIED CORRECT -- Head-to-Head (Majority)

MI 4-2, SRH 3-2, GT 3-2, KKR 2-2, RR 2-2, RCB 2-2 (combined Bangalore+Bengaluru), DC 1-4, PBKS 2-3 -- all match DB. All-time records for MI 6-2, KKR 4-2, SRH 4-2, DC 3-4, GT 3-4, RR 2-4, RCB 2-4 -- all match DB.

### VERIFIED CORRECT -- Season Win Counts

2023: 8 wins (15 matches), 2024: 7 wins (14 matches), 2025: 6 wins (14 matches) -- all match DB exactly. Home record at Ekana: 3-4 (2023), 4-3 (2024), 2-5 (2025) -- matches DB exactly.

---

## BLOCKING ERRORS (5)

### ERROR-1: Setting vs Chasing Match Counts Are Fabricated [CRITICAL]

**Location:** Section 9a, "Innings Context: Setting vs Chasing"

**Claimed:**
> Batting First: 43 matches, 21 wins (48.8%)
> Batting Second: 42 matches, 21 wins (50.0%)

This totals 85 matches. LSG have played exactly **43 matches since 2023** (15 in 2023, 14 in 2024, 14 in 2025).

**DB shows:**
- Batting First (Setting): **17 matches, 9 wins (52.9%)**
- Batting Second (Chasing): **26 matches, 12 wins (46.2%)**
- Total decisive: 42 matches, 21-21 (1 no-result vs CSK on 2023-05-03)

The win percentages, match counts, and the resulting 48.8%/50.0% split are entirely wrong. The actual data tells a different story: LSG have batted second far more often (26 vs 17), yet win more frequently when batting first (52.9% vs 46.2%). This supports the same bat-first conclusion but from very different underlying numbers.

**Fix:** Replace Section 9a with:

| Scenario | Matches | Wins | Win % |
|----------|---------|------|-------|
| Batting First | 17 | 9 | 52.9% |
| Batting Second | 26 | 12 | 46.2% |

Add note: "1 no-result excluded (vs CSK, 2023-05-03). LSG have batted second in 60.5% of matches but win more frequently when setting."

**Severity:** BLOCKING. The match counts are mathematically impossible (85 > 43). This undermines the entire innings context analysis credibility.

---

### ERROR-2: CSK Head-to-Head Record Omits No-Result Context [BLOCKING]

**Location:** Head-to-Head table, CSK since-2023 row

**Claimed:** CSK 2-2 (50.0%)

**DB shows:** 5 matches played: LSG won 2, CSK won 2, 1 no-result. The 2-2 record is technically correct if no-results are excluded, but the presentation is misleading. The table shows 5 matches for PBKS (2-3) and DC (1-4) with implicit assumption that W+L = total matches. For CSK, 2+2 = 4, but 5 matches were played.

More critically, the all-time table says "3-2 (60.0%)" for CSK. DB shows 6 matches: 3W, 2L, 1 no-result. This is again technically correct but inconsistent in presentation -- no other row has a no-result, so the reader assumes W+L = total matches.

**Fix:** Add a footnote: "CSK record excludes 1 no-result (2023-05-03). 5 matches played since 2023; 6 all-time." Alternatively, present as "2-2 (NR 1)" and "3-2 (NR 1)".

**Severity:** BLOCKING. Inconsistent handling of no-results misrepresents the H2H and makes the "Since 2023: 21-21" total appear to disagree with the per-opponent sum (which adds to 20-21 without CSK's NR accounted for).

---

### ERROR-3: Death Bowling Aggregate Economy Is Wrong

**Location:** Category Ratings table, "Bowling, Death" row

**Claimed:** 10.92 econ (agg.)

**DB shows:** 10.84 economy (2016 runs conceded / 1116 balls * 6 = 10.84)

The difference is 0.08 RPO, which is material in a rating context. The "at league (10.88)" comparison also shifts: 10.84 is actually 0.03 below the league average of 10.87, not above it.

**Fix:** Correct to "10.84 econ (agg.)" and update the context to "Below league (10.87) by 0.03 -- essentially at par." The rating of 4.0/10 may also warrant a slight upward adjustment given the economy is actually at league average rather than above it.

**Severity:** BLOCKING. The wrong number changes the directional conclusion (above league vs below league).

---

### ERROR-4: Death Batting League Average SR Is Incorrect

**Location:** Category Ratings table, "Batting, Death" row; Phase-Wise Batting table

**Claimed:** League death batting SR = 170.6

**DB shows:** League death batting SR = **170.2** (aggregated across all teams since 2023)

The preview says LSG death batting at 161.5 is "Below league (170.6)" with a -9.1 gap. Corrected: the gap is -8.7 (161.5 vs 170.2). This also affects the Phase-Wise Batting table's "Diff" column (-9.1 should be -8.7).

**Fix:** Replace 170.6 with 170.2 across all occurrences. Update the diff column in Phase-Wise Batting from -9.1 to -8.7. The death batting rating of 8.0/10 and the contextual analysis are not materially affected.

**Severity:** BLOCKING. Incorrect league benchmark propagates through multiple sections and inflates the perceived gap.

---

### ERROR-5: Mayank Yadav Stats Are Unverifiable

**Location:** Squad Table (IP row), Bowler Phase table, Individual Bowler Splits (9e), Interesting Data Insights (#5)

**Claimed:**
- 9.32 econ (20.2 ov, LOW)
- Defending economy: 6.22 (9 overs, LOW)
- Bowl-first economy: 11.82 (11.2 overs, LOW)
- Middle overs: 8.18 (11 ov, LOW), Death: 7.58 (3.2 ov, LOW)

**DB shows:** Mayank Yadav does not appear in `analytics_ipl_bowling_career_since2023`, `analytics_ipl_bowler_phase_since2023`, or `analytics_ipl_player_bowling_by_innings_since2023`. The only "Mayank" in the bowling tables is "Mayank Dagar" (different player, different role).

These stats cannot be verified against the database. They may have been sourced from raw fact_ball queries or external sources, but without DB traceability, they fail the statistical rigor standard.

**Fix:** Either (a) add a footnote stating "Mayank Yadav stats computed from raw fact_ball data; not present in analytics views due to sample size threshold" with the exact query methodology, or (b) remove Mayank Yadav's specific economy numbers and replace with "Insufficient IPL data for phase analysis (LOW confidence across all metrics)." The "Interesting Data Insights" section 5 about his 6.22 defending economy should be downgraded from a featured insight to a parenthetical note given the extreme sample limitation.

**Severity:** BLOCKING. Unverifiable stats in a publication that promises "Every claim above is backed by data" (final line) is a credibility risk.

---

## NON-BLOCKING ISSUES (4)

### ISSUE-1: League Average SR for Powerplay and Middle Overs Rounded Down

**Location:** Category Ratings, Phase-Wise Batting table

**Claimed:** PP league SR = 146.0, Middle league SR = 140.0
**DB shows:** PP league SR = 146.3, Middle league SR = 140.3

These are rounded down by 0.3 in both cases. While not materially affecting conclusions, the consistent rounding in one direction introduces minor systematic bias. The PP diff should be -12.4 (not -12.1) and the middle diff should be +1.8 (not +2.1).

**Fix:** Use 146.3 and 140.3 for league averages. Update diffs accordingly.

---

### ISSUE-2: Shami Bowl-First Overs Minor Discrepancy

**Location:** Individual Player Splits: Bowlers (9e)

**Claimed:** Shami bowl-first sample = 50.2 overs
**DB shows:** 301 balls = 50.1 overs (50 overs and 1 ball, not 2 balls)

Similarly, Avesh defending: claimed 61.2 overs, DB shows 367 balls = 61.1 overs.

**Fix:** Correct Shami to 50.1 overs and Avesh to 61.1 overs.

---

### ISSUE-3: Avesh Career Economy Inconsistency Across Sections

**Location:** "Players Who Need to Step Up" section vs Bowler Recent Form

The "Players Who Need to Step Up" section states Avesh's overall economy is 9.96, with "his 9.96 economy is 0.69 runs above the league bowling average (9.27)." But 9.96 is Avesh's **since-2023** economy. His **all-time career** economy (which the recent form table uses as the baseline) is 9.25. The recent form section then says "Avesh at 10.24 L10 (vs 9.25 career)" -- here "career" means all-time, not since-2023.

This creates a scope ambiguity. When the document says "career" it sometimes means since-2023 and sometimes means all-time.

**Fix:** Explicitly label each reference as "since-2023" or "all-time (career)" to avoid confusion. The recent form section's "career" column header should be labeled "Career (All-Time)" to distinguish from the since-2023 scope used elsewhere.

---

### ISSUE-4: "Combined economy of 10.17 in 2025" Claim Is Unverified

**Location:** The Story section, paragraph 3

**Claimed:** "the bowling unit's combined economy of 10.17 in 2025 was the second-worst in the league"

This aggregated economy is not directly verifiable from the phase-level data. The 2025 phase economies are PP 10.73, Middle 9.52, Death 11.27. A balls-weighted average across these phases would yield the combined figure, but the exact calculation and the "second-worst in the league" ranking claim require cross-team comparison that I have not independently verified. This is flagged as non-blocking because the directional claim (LSG's bowling was poor in 2025) is supported by the phase data.

**Fix:** Either provide the exact calculation methodology or remove the "second-worst" ranking claim unless verified against all 10 teams.

---

## Analytical Depth Assessment

The preview excels in several dimensions:

1. **Three-season evolution tables** (Section "Team Style Analysis") are the strongest section. All 18 data points verified correct. The delta analysis between seasons is genuinely insightful and well-structured.

2. **Innings context analysis** (Sections 9a-9f) is the most ambitious analytical section I have seen in any preview. The team-level and individual-level setting/chasing splits, combined with the bowler defending/bowling-first splits, provide a coherent tactical prescription. The ERROR-1 in match counts is critical but the underlying SR/economy data is all correct.

3. **The Bold Take** on Rathi vs Shami is quantitatively rigorous. The phase-economics argument (middle overs = 9 overs vs powerplay = 6 overs, therefore middle-overs economy improvement has higher marginal impact) is mathematically sound and well-articulated. The 0.30 Cr vs 10.00 Cr value comparison adds a financial dimension.

4. **Batter vs bowler type analysis** is comprehensive. All verified stats for Pooran, Pant, Markram, Samad, Badoni, and Marsh match the DB exactly. The identification of Pant's off-spin weakness (90.3 SR, 31 balls, LOW) and Badoni's off-spin vulnerability (105.7, 53 balls, MEDIUM) is analytically sound.

5. **Opposition blueprint** in Andy Flower's scouting report is actionable and data-backed. The prescription to bowl off-spin through overs 7-15 targeting Badoni/Pant, and to never bowl leg-spin to Pooran, is directly supported by the matchup data.

**Gaps in analytical depth:**
- No discussion of LSG's powerplay batting dot ball % (46.7%) vs league (44.1%) as a key tactical metric for the openers
- The venue analysis lacks a first-innings vs second-innings comparison, which would strengthen the bat-first argument
- No partnership analysis for the Marsh-Markram opening pair

---

## Methodology Transparency Assessment

The preview consistently labels confidence tiers (HIGH/MEDIUM/LOW) alongside ball/over counts and uses the since-2023 data window as the primary scope. This is commendable and exceeds most previews.

However:
- The scope switching between "since 2023" and "career (all-time)" in the recent form section is not explicitly flagged (ISSUE-3)
- Mayank Yadav's data source is opaque (ERROR-5)
- The "9,496 matches / 2.14M balls" header does not clarify that team-specific analysis uses a much smaller subset
- The aggregation method for phase-wise team batting (is it balls-weighted across seasons, or runs-weighted?) is not stated

---

## Quantitative Consistency Assessment

The biggest consistency failures are:
1. The 85-match total in setting/chasing (ERROR-1) -- mathematically impossible
2. The death bowling economy 10.92 vs DB 10.84 (ERROR-3) -- changes directional conclusion
3. League average death SR 170.6 vs DB 170.2 (ERROR-4) -- propagates through multiple sections

The rest of the document is remarkably consistent. Over 50 individual stats were verified, and 45+ matched precisely. The rounding conventions are generally consistent (1 decimal place for SR, 2 for economy).

---

## Summary of Required Fixes

### Blocking (Must Fix Before Publication)

| ID | Section | Issue | Current | Corrected |
|----|---------|-------|---------|-----------|
| ERROR-1 | 9a Setting vs Chasing | Match counts fabricated | BF 43/21 (48.8%), BS 42/21 (50.0%) | BF 17/9 (52.9%), BS 26/12 (46.2%) |
| ERROR-2 | Head-to-Head | CSK no-result omitted | 2-2 since 2023, 3-2 all-time | 2-2 (NR 1) since 2023, 3-2 (NR 1) all-time |
| ERROR-3 | Category Ratings | Death bowling aggregate economy | 10.92 | 10.84 |
| ERROR-4 | Category Ratings, Phase-Wise | Death batting league SR | 170.6 | 170.2 |
| ERROR-5 | Multiple sections | Mayank Yadav stats unverifiable | 9.32 econ, 6.22 defend, etc. | Add source footnote or remove specific numbers |

### Non-Blocking (Should Fix)

| ID | Section | Issue | Current | Corrected |
|----|---------|-------|---------|-----------|
| ISSUE-1 | Category Ratings, Phase-Wise | PP/Middle league SR rounded down | 146.0, 140.0 | 146.3, 140.3 |
| ISSUE-2 | Bowler Innings Splits | Shami/Avesh overs minor error | 50.2, 61.2 | 50.1, 61.1 |
| ISSUE-3 | Recent Form, Step Up | Career scope ambiguity | "career" used for both scopes | Label "Career (All-Time)" vs "Since 2023" |
| ISSUE-4 | The Story | Combined economy 10.17 unverified | "second-worst in the league" | Verify or remove ranking claim |

---

## Post-Fix Projected Score

If all 5 blocking errors and 4 non-blocking issues are addressed:

| Criterion | Weight | Projected Score | Weighted |
|-----------|--------|----------------|----------|
| Statistical Rigor | 40% | 9.5/10 | 3.80 |
| Analytical Depth | 30% | 8.5/10 | 2.55 |
| Methodology Transparency | 20% | 9.0/10 | 1.80 |
| Quantitative Consistency | 10% | 9.0/10 | 0.90 |
| **Overall** | **100%** | | **9.05/10** |

The underlying analytical work is strong. The errors are concentrated in a few sections and are correctable. Once fixed, this preview meets publication standard.

---

*Reviewed by Jose Mourinho, Quant Researcher | Temperature: 0.30*
*Cricket Playbook v5.0.0 | DuckDB verification: 50+ stats cross-referenced*
