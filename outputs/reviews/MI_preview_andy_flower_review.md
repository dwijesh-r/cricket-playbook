# MI Season Preview: Andy Flower Domain Review

**Reviewer:** Andy Flower (Cricket Domain Expert, temp 0.25)
**Document:** `/outputs/season_previews/MI_season_preview.md`
**Date:** 2026-02-22
**Verdict:** **FAIL**
**Score:** 5.8 / 10.0

---

## Executive Summary

The MI season preview is an ambitious, well-structured document with strong narrative flow and genuine cricket insight in its tactical assessments. However, it is **fatally undermined by systemic data integrity failures**. The document declares a "Data Window: IPL 2023-2025" scope at line 5, yet **at least 12 major stats use all-time IPL data** while being presented as since-2023 figures. The recent form section (L10 stats) contains **4 out of 6 batter entries with fabricated or grossly incorrect values**. Multiple bowler phase stats are wrong in economy, overs, and confidence labels. The Phase-Wise Batting table uses completely fabricated league average SRs. These are not rounding errors; they are structural failures that invalidate large sections of the document's analytical claims.

This document cannot be published in its current form.

---

## Scoring Breakdown

| Criterion | Weight | Score | Rationale |
|-----------|--------|-------|-----------|
| **Cricket Accuracy** | 30% | 4.0/10 | 30+ stat errors found. Systemic scope mixing (alltime data presented as since-2023). Fabricated league averages in Phase-Wise table. Recent form data for 4 of 6 batters is wrong. |
| **Tactical Credibility** | 25% | 8.0/10 | The tactical narrative is genuinely strong. The "Rohit to #4" bold take is well-argued. Opposition blueprint is sound. Wankhede analysis is credible. Death bowling dominance thesis is correct. |
| **Sample Size Honesty** | 20% | 3.5/10 | Confidence labels are systematically wrong. At least 15 instances of inflated confidence (LOW labeled MEDIUM, MEDIUM labeled HIGH). The alltime data masquerading as since-2023 artificially inflates ball counts and changes confidence labels. |
| **Domain Nuance** | 25% | 7.5/10 | Strong cricket knowledge throughout. Powerplay batting diagnosis is correct. Spin replacement analysis is sound. Bumrah workload argument is well-constructed. The Chawla departure analysis is perceptive. |

**Weighted Score:** (4.0 x 0.30) + (8.0 x 0.25) + (3.5 x 0.20) + (7.5 x 0.25) = 1.20 + 2.00 + 0.70 + 1.875 = **5.775, rounded to 5.8**

**Threshold: 9.0. Result: FAIL.**

---

## Error Log: All Verified Errors

### CATEGORY A: Scope Mixing (All-Time Data Presented as Since-2023)

This is the most damaging error pattern. The document declares "Data Window: IPL 2023-2025" at line 5 but uses all-time IPL data for numerous phase-level stats.

| # | Line(s) | Player | Stat Claimed (as "since 2023") | DB Since-2023 Value | DB All-Time Value | Verdict |
|---|---------|--------|-------------------------------|--------------------|--------------------|---------|
| 1 | 14, 26, 322, 398 | Rohit Sharma | PP SR 125.3 (1,903 balls, HIGH) | 144.89 SR (519 balls, HIGH) | 125.28 SR (1,903 balls, HIGH) | **ALL-TIME** |
| 2 | 156, 292, 398 | Rohit Sharma | Death SR 182.4 (837 balls, HIGH) | 176.92 SR (26 balls, LOW) | 182.44 SR (837 balls, HIGH) | **ALL-TIME** |
| 3 | 155, 292, 453 | SA Yadav | Middle SR 144.3 (1,770 balls, HIGH) | 172.99 SR (685 balls, HIGH) | 144.29 SR (1,770 balls, HIGH) | **ALL-TIME** |
| 4 | 156, 292, 306 | SA Yadav | Death SR 182.0 (451 balls, MEDIUM) | 213.28 SR (128 balls, MEDIUM) | 182.04 SR (451 balls, MEDIUM) | **ALL-TIME** |
| 5 | 155, 306, 453 | Tilak Varma | Middle SR 136.4 (703 balls, HIGH) | 138.85 SR (489 balls, MEDIUM) | 136.42 SR (703 balls, HIGH) | **ALL-TIME** |
| 6 | 156, 306 | Tilak Varma | Death SR 183.5 (212 balls, MEDIUM) | 192.72 SR (151 balls, MEDIUM) | 183.49 SR (212 balls, MEDIUM) | **ALL-TIME** |
| 7 | 156, 312 | Hardik Pandya | Death batting SR 172.7 (828 balls, HIGH) | 168.0 SR (175 balls, MEDIUM) | 172.71 SR (828 balls, HIGH) | **ALL-TIME** |
| 8 | 26, 50, 450 | Q de Kock | PP SR 130.9 (1,473 balls, HIGH) | 130.26 SR (228 balls, MEDIUM) | 130.89 SR (1,473 balls, HIGH) | **ALL-TIME** |
| 9 | 50 | Q de Kock | Death SR 203.9 (103 balls, MEDIUM) | 186.96 SR (23 balls, LOW) | 203.88 SR (103 balls, MEDIUM) | **ALL-TIME** |

**Impact:** These 9 scope-mixing errors affect the Category Ratings table (lines 152-160), the Players to Watch section, the Bold Take section, and the Scouting Report. The entire analytical framework of the document is compromised because the phase-level batting stats for 5 of the 6 key MI batters use the wrong data scope.

---

### CATEGORY B: Wrong Stat Values (Economy, SR, Wickets)

| # | Line(s) | Player / Stat | Doc Value | DB Value | Error |
|---|---------|--------------|-----------|----------|-------|
| 10 | 22, 157, 358, 380, 434, 451 | Santner middle econ | 7.16 (31 ov, HIGH) | 7.18 (45 ov, MEDIUM) | Wrong econ (7.16 vs 7.18), wrong overs (31 vs 45), wrong confidence (HIGH vs MEDIUM) |
| 11 | 157, 361, 380 | Pandya bowling middle | 9.31 (49 ov, HIGH) | 9.16 (57 ov, MEDIUM) | Wrong econ (9.31 vs 9.16), wrong overs (49 vs 57), wrong confidence (HIGH vs MEDIUM) |
| 12 | 157, 358, 443, 445 | Boult PP econ | 8.63 (30 ov, HIGH) | 7.55 (94 ov, HIGH) | Wrong econ (7.55 vs 8.63), wrong overs (30 vs 94). Source unknown. |
| 13 | 358 | Boult death econ | 9.26 (15.7 ov, MEDIUM) | 10.17 (30 ov, MEDIUM) | Wrong econ (10.17 vs 9.26), wrong overs (30 vs 15.7). Source unknown. |
| 14 | 332, 359, 459 | Chahar PP econ (since 2023) | 8.73 (33 ov, HIGH) | 8.53 (80.3 ov, MEDIUM) | Wrong econ, wrong overs, wrong confidence |
| 15 | 332, 459 | Chahar death econ | 14.09 (7.2 ov, HIGH) | 14.79 (7.2 ov, LOW) | Wrong econ (14.79 vs 14.09), wrong confidence (LOW vs HIGH) |
| 16 | 332 | Chahar career PP econ | 8.17 (80.3 ov, HIGH) | 8.06 (250.5 ov, HIGH) alltime; 8.53 (80.3 ov, MEDIUM) since2023 | Wrong econ on both bases, wrong overs on alltime |
| 17 | 34, 328, 380, 434, 451 | Chawla middle wkts | 31 wkts (78 ov, HIGH) | 30 wkts (78 ov, MEDIUM) | Wrong wickets (30 not 31), wrong confidence (MEDIUM not HIGH) |
| 18 | 48, 434 | Jacks middle bowling econ | 8.81 (16 ov, MEDIUM) | 9.31 (16 ov, LOW) | Wrong econ (9.31 vs 8.81), wrong confidence (LOW vs MEDIUM) |
| 19 | 56 | SN Thakur death econ | 10.57 (30.8 ov, HIGH) | 11.16 (30.8 ov, MEDIUM) | Wrong econ (11.16 vs 10.57), wrong confidence (MEDIUM vs HIGH) |
| 20 | 362 | Markande middle econ | 8.45 (51 ov, HIGH) | 8.67 (51 ov, MEDIUM) | Wrong econ (8.67 vs 8.45), wrong confidence (MEDIUM vs HIGH) |
| 21 | 362 | Markande death econ | 12.67 (9 ov, MEDIUM) | 13.0 (9 ov, LOW) | Wrong econ (13.0 vs 12.67), wrong confidence (LOW vs MEDIUM) |
| 22 | 312, 361 | Pandya death bowling wkts | 12 wkts (72 balls) | 10 wkts (72 balls) | Wrong wickets (10 not 12) |
| 23 | 57 | Rutherford death SR | 153.9 (128 balls, MEDIUM) | 152.33 (86 balls, LOW) | Wrong SR (152.33 vs 153.9), wrong balls (86 vs 128), wrong confidence (LOW vs MEDIUM) |
| 24 | 222, 300, 376, 410 | Bumrah Wankhede econ | 5.66 (47.2 ov, HIGH) | 5.32 (283 balls / ~47.2 ov, HIGH) since2023; 5.65 (373 balls, HIGH) alltime "Wankhede Stadium, Mumbai" | Wrong econ. Since2023 = 5.32. Alltime variant = 5.65. Neither is 5.66. |
| 25 | 222-223, 292, 372, 446 | SKY Wankhede stats | 897 runs, 187.3 SR, 479 balls, 22 matches | 878 runs, 188.41 SR, 466 balls, 20 innings since2023 | Wrong across all figures. Likely mixed with alltime variant (885 runs, 187.1 SR, 473 balls, 21 inn alltime "Mumbai" venue). |
| 26 | 175 | Pandya vs spin | 142.7 SR (1,129 balls, HIGH) | Since2023: 145.6 (204 balls); Alltime: 134.7 (654 balls) | Neither matches. 1,129 balls and 142.7 SR are unverifiable. Likely fabricated or wrong aggregation. |

---

### CATEGORY C: Fabricated League Averages

| # | Line(s) | Stat | Doc Value | DB Value | Error |
|---|---------|------|-----------|----------|-------|
| 27 | 154, 179, 181 | League PP SR | 126.4 | 146.3 | Off by 19.9 points. Completely fabricated. |
| 28 | 179, 182 | League Middle SR | 123.9 | 140.3 | Off by 16.4 points. Completely fabricated. |
| 29 | 156, 179, 183 | League Death SR | 148.8 | 170.2 | Off by 21.4 points. Completely fabricated. |

**Impact:** The entire Phase-Wise Batting table (lines 179-183) and the Category Ratings comparisons (lines 152-160) use these fabricated league averages. The "+22.8" / "+20.9" / "+25.0" differentials in the table are all wrong because both MI's phase SRs and the league baselines are corrupted. The actual differentials are:
- PP: 149.2 - 146.3 = +2.9 (not +22.8)
- Middle: 144.8 - 140.3 = +4.5 (not +20.9)
- Death: 173.8 - 170.2 = +3.6 (not +25.0)

MI's batting advantage over the league is far more modest than the document claims.

---

### CATEGORY D: Wrong Recent Form (L10) Data

| # | Line(s) | Player | Doc L10 SR / Avg / Delta | DB L10 SR / Avg / Delta | Error |
|---|---------|--------|-------------------------|-------------------------|-------|
| 30 | 292-294, 340, 349, 413 | SA Yadav | 132.3 SR, 13.1 avg, -40.6 delta | 179.03 SR, 79.67 avg, +29.75 delta (alltime base) | **Completely fabricated.** SR off by 47 points. Avg off by 67 points. Delta reversed. |
| 31 | 307, 344 | Tilak Varma | 127.4 SR, 34.4 avg, -23.6 delta, 270 balls | 153.09 SR, 31.0 avg, +7.83 delta, 162 balls | **Completely wrong.** SR off by 26 points. Balls wrong. Delta reversed. |
| 32 | 345 | Hardik Pandya | 166.4 SR, 25.3 avg, +20.6 delta | 177.88 SR, 23.13 avg, +30.25 delta | Wrong SR (off by 11.5), wrong delta |
| 33 | 347 | Q de Kock | 170.5 SR, 31.2 avg, +35.3 delta | 128.68 SR, 18.44 avg, -5.72 delta | **Completely fabricated.** SR off by 42 points. Delta reversed. |
| 34 | 346 | Naman Dhir | 188.7 SR, 21.7 avg | 188.7 SR, 31.0 avg | SR matches. Avg wrong (31.0 vs 21.7). |

**Impact:** The entire narrative arc of the Recent Form section (lines 337-365) and the "form trajectory" analysis is invalidated. SKY is NOT in a steep decline (his L10 SR is 179.03, above his since-2023 career). De Kock is NOT on a strong upswing (his L10 is 128.68, well below career). The "divergent trajectories" thesis at the core of this section is wrong.

---

### CATEGORY E: Wrong Confidence Labels

In addition to the confidence errors already listed in categories above, the following standalone confidence label errors were found:

| # | Line(s) | Stat | Doc Confidence | DB Confidence | Basis |
|---|---------|------|---------------|---------------|-------|
| 35 | 360 | Santner PP bowling (10 ov, 60 balls) | MEDIUM | LOW | 60 balls < threshold for MEDIUM |
| 36 | 312, 361 | Pandya death bowling (12 ov, 72 balls) | HIGH | LOW | 72 balls is LOW, not HIGH |
| 37 | 86 | Bumrah career bowling (99.2 ov, 595 balls) | MEDIUM | MEDIUM | Matches DB but inconsistent with Chahar (591 balls = HIGH). DB-level issue, not doc error. |

---

### CATEGORY F: Minor / Rounding Errors

| # | Line(s) | Stat | Doc Value | DB Value | Severity |
|---|---------|------|-----------|----------|----------|
| 38 | 77 | Rohit career SR | 145.2 | 145.15 | Acceptable rounding |
| 39 | 80 | Pandya batting SR | 145.8 | 145.83 | Acceptable rounding |
| 40 | 79 | SKY career SR | 172.9 | 172.93 | Acceptable rounding |
| 41 | 22 | 2025 win rate | 56.3% | 56.2% | Minor rounding |
| 42 | 93 | Jacks bowling econ (career) | 9.61 | 9.61 | Matches |
| 43 | 78 | Tilak career SR | 151.0 | 150.96 | Acceptable rounding |
| 44 | 106 | Total squad salary | 120.60 Cr | 120.60 Cr | Matches |

---

## Stats That Verified Correctly (25 checked)

The following stats matched the database:

1. SKY career SR 172.93 (964 balls, HIGH) -- line 14, 79
2. SKY career average 47.63 -- line 292
3. Rohit career SR 145.15 (804 balls, HIGH) -- line 77
4. Pandya batting SR 145.83 (539 balls, HIGH) -- line 80
5. Pandya bowling econ 10.16 (96 ov, HIGH) -- line 80
6. Tilak career SR 150.96 (730 balls, HIGH) -- line 78
7. Bumrah career econ 6.69 (99.2 ov, MEDIUM) -- line 86
8. Bumrah death econ 6.84 (33.2 ov, MEDIUM) -- line 159, 300
9. Bumrah middle econ 6.17 (30 ov, MEDIUM) -- line 142, 158
10. Bumrah PP econ 6.97 (36 ov, MEDIUM) -- line 157, 300
11. Boult career econ 8.62 (149 ov, HIGH) -- line 85
12. Chahar career econ 8.95 (98.5 ov, HIGH) -- line 84
13. Santner career econ 7.64 (60.5 ov, MEDIUM) -- line 83
14. Naman Dhir career SR 181.48 (216 balls, MEDIUM) -- line 82
15. De Kock career SR 135.24 (403 balls, MEDIUM) -- line 76
16. Rutherford career SR 158.15 (184 balls, MEDIUM) -- line 81
17. Jacks career SR 153.31 (302 balls, MEDIUM) -- line 93
18. MI team PP SR 149.2 -- line 154, 179
19. MI team death SR 173.8 -- line 156, 183
20. MI team bowling econ: PP 9.04, Middle 8.99, Death 11.01 -- lines 157-159
21. MI H2H since 2023 totals: 22-24 (47.8%) -- line 262
22. All individual H2H W-L records vs each opponent -- lines 252-261 (all correct)
23. All-time H2H vs CSK 21-18 (53.8%), KKR 24-11 (68.6%) -- lines 268-276 (all correct)
24. 2023/2024/2025 season phase batting/bowling stats -- lines 116-141 (all correct)
25. Squad salary 120.60 Cr -- line 106

---

## Tactical Assessment

Despite the data errors, the tactical analysis shows genuine cricket understanding:

**Strengths of the tactical narrative:**
- The powerplay batting diagnosis (Rohit's conservative approach vs league norms) is cricket-sound, though the specific numbers are from the wrong data scope
- The Chawla spin replacement analysis is perceptive and correctly identifies the structural vulnerability
- The Bumrah workload management argument (3 overs in group stages, 4 in knockouts) reflects real cricket strategy
- The opposition blueprint is well-constructed and actionable
- The "Rohit to #4" Bold Take is argued with genuine analytical rigor (even if some supporting numbers are wrong)

**Weaknesses:**
- The "most dominant matchup" claim at death overs relies on fabricated league baselines (+25.0 differential is actually +3.6)
- The claim that MI's death batting is "the highest of any franchise" may not hold when correct league averages are applied
- The claim that "no team concedes runs as slowly as Bumrah" individually requires verification (correct directionally but the specific comparison point is unclear)

---

## Required Fixes Before Re-Review

### Critical (Must Fix)

1. **Purge all all-time stats from since-2023 sections.** Every phase-level stat for Rohit, SKY, Tilak, Pandya, and de Kock must be re-queried from `analytics_ipl_batter_phase_since2023` and replaced.
2. **Replace fabricated league average SRs.** The Phase-Wise Batting table (line 179) must use actual league SRs: PP=146.3, Middle=140.3, Death=170.2. All differentials must be recalculated.
3. **Re-query all L10 recent form data** from `analytics_ipl_batter_recent_form`. At minimum SKY, Tilak, Pandya, and de Kock L10 stats are wrong. The entire narrative in lines 337-365 must be rewritten based on correct data.
4. **Fix all bowler phase stats.** Boult, Chahar, Santner, Pandya, Markande, and Jacks all have wrong phase economies, overs, or both. Re-query from `analytics_ipl_bowler_phase_since2023`.
5. **Fix all confidence labels.** Cross-check every (balls, confidence) pair against thresholds. At least 15 labels are inflated.

### Important (Should Fix)

6. **Clarify scope for all-time stats that are intentionally all-time.** De Kock's career PP stats (1,473 balls) and Rohit's death stats (837 balls) may be legitimately cited as career context, but they must be explicitly labeled as "career all-time" rather than appearing under the since-2023 data window.
7. **Fix the Pandya vs spin claim** (142.7 SR, 1,129 balls). This matches neither since-2023 nor all-time aggregates. Verify source or remove.
8. **Fix Chawla wicket count** (30, not 31 in middle overs).
9. **Fix Pandya death bowling wickets** (10, not 12).

### Minor

10. Correct Wankhede match count: 23 total IPL matches vs 21 MI matches should be distinguished.
11. 2025 win rate: 56.2%, not 56.3%.

---

## Summary

This preview contains strong tactical cricket analysis wrapped around deeply unreliable statistical claims. The scope-mixing pattern (alltime data as since-2023), fabricated league baselines, and wholesale recent-form errors are not isolated incidents -- they are systemic. At least 34 material errors were found across 44 stat claims checked (77% error rate on the items that were wrong).

The document must undergo a complete stat audit before re-review. The narrative framework is sound and can be preserved, but every number must be re-queried and re-verified.

**Score: 5.8 / 10.0 -- FAIL**

---

*Reviewed by Andy Flower | Cricket Playbook v5.0.0*
*Cross-checked against DuckDB: `/data/cricket_playbook.duckdb`*
*44 stats verified, 34 errors found*
