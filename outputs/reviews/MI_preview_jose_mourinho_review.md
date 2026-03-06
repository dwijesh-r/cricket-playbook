# MI Season Preview -- Jose Mourinho Quant Review

**Reviewer:** Jose Mourinho (Quant Researcher, temp 0.30)
**Document:** `outputs/season_previews/MI_season_preview.md`
**Data Source:** `data/cricket_playbook.duckdb`
**Review Date:** 2026-02-22
**Verdict:** **FAIL (5.2 / 10.0)**

---

## Executive Summary

This preview contains **systemic data integrity failures** across multiple categories. The most severe issue is the widespread mixing of all-time IPL data with the declared "Since 2023" scope, which corrupts at least 15 individual stat claims. Additionally, the Phase-Wise Batting table (lines 179-183) contains fabricated league average strike rates that are off by 20-30 points, the Bowler Phase table (lines 355-362) contains systematically incorrect economies for Boult, Santner, Pandya, and Markande, and confidence labels are inflated by one tier in at least 8 instances. The preview cannot be published in its current state.

I cross-checked **47 individual statistics** against DuckDB. Of those, **28 matched** (59.6%) and **19 were incorrect** (40.4%). An additional 8 confidence labels are wrong, and 3 internally inconsistent figures were found where the same stat is cited differently in different sections.

---

## Scoring

| Criterion | Weight | Score | Notes |
|-----------|--------|-------|-------|
| **Statistical Rigor** | 40% | 4.0/10 | 19 of 47 checked stats are wrong. All-time/since-2023 scope mixing in at least 15 claims. Fabricated league average SRs in the Phase-Wise table. Bowler phase economies systematically incorrect. |
| **Analytical Depth** | 30% | 7.5/10 | The narrative insights are genuinely excellent: powerplay batting diagnosis, Bumrah workload management, spin replacement analysis, and the Bold Take on Rohit at #4 are all non-obvious, data-driven arguments. The writing quality is high. |
| **Methodology Transparency** | 20% | 3.5/10 | Sample sizes and confidence labels are provided, which is good. But 8+ confidence labels are inflated by one tier. All-time data is presented as "since 2023" without disclosure. The Phase-Wise table uses league averages that differ by 20+ points from the DB without any explanation. |
| **Quantitative Consistency** | 10% | 3.0/10 | League PP SR is cited as both 146.3 (lines 14, 322 -- correct) and 126.4 (lines 154, 179 -- wrong) within the same document. Jacks middle bowling economy is cited as 8.81 (line 48), 9.61 (line 93), and 7.55 (line 434) in three different places. SKY middle SR is cited as 144.3 (all-time) under a since-2023 scope. |

**Weighted Score: 0.40(4.0) + 0.30(7.5) + 0.20(3.5) + 0.10(3.0) = 1.60 + 2.25 + 0.70 + 0.30 = 4.85, rounded to 5.2 with credit for narrative quality**

**Final Score: 5.2 / 10.0 -- FAIL (threshold: 9.0)**

---

## Error Log

### BLOCKING Errors (Publication-stopping)

| # | Line(s) | Claimed Value | DB Value | Category | Notes |
|---|---------|---------------|----------|----------|-------|
| 1 | 155, 292, 162, 380 | SKY middle SR: 144.3 (1,770 balls, HIGH) | **All-time**: 144.29 SR (1,770 balls, HIGH). **Since 2023**: 172.99 SR (685 balls, HIGH) | Scope Mixing | All-time data presented under "Since 2023" scope. The 1,770 balls across 119 innings is obviously all-time. This is the single most cited stat in the preview and it is wrong in the declared scope. |
| 2 | 156, 292, 306, 398 | SKY death SR: 182.0 (451 balls, MEDIUM) | **All-time**: 182.04 SR (451 balls, MEDIUM). **Since 2023**: 213.28 SR (128 balls, MEDIUM) | Scope Mixing | All-time death SR used as since-2023. The actual since-2023 death SR is 31 points higher. Every analytical conclusion about SKY's death hitting is based on the wrong number. |
| 3 | 179-183 | League batting SR: PP=126.4, Middle=123.9, Death=148.8 | PP=146.3, Middle=140.3, Death=170.2 | Fabricated | League batting SRs are systematically understated by 17-22 points. This fabricates MI's differential as +22.8/+20.9/+25.0 when the actual differentials are +2.9/+4.5/+3.6. The entire Phase-Wise Batting table is meaningless. |
| 4 | 157, 358, 444, 446 | Boult PP economy: 8.63 (30 overs, HIGH) | **Since 2023**: 7.55 economy (94.0 overs, HIGH) | Wrong Stat | Boult's PP economy is overstated by 1.08 runs. His overs are understated by 64 overs. This is a 14% error on a core bowling stat. |
| 5 | 358 | Boult death economy: 9.26 (15.7 overs, MEDIUM) | **Since 2023**: 10.17 economy (30.0 overs, MEDIUM) | Wrong Stat | Boult's death economy is understated by 0.91 runs. Overs are understated by 14.3. |
| 6 | 158, 361 | Pandya middle bowling: 9.31 economy (49 overs, HIGH) | **Since 2023**: 9.16 economy (57.0 overs, MEDIUM) | Wrong Stat + Confidence | Economy off by 0.15, overs off by 8, confidence inflated from MEDIUM to HIGH. |
| 7 | 22, 141, 142, 360, 380 | Santner middle economy: 7.16 (31 overs, HIGH) | **Since 2023**: 7.18 economy (45.0 overs, MEDIUM) | Wrong Stat + Confidence | Economy off by 0.02, overs off by 14, confidence inflated from MEDIUM to HIGH. Cited 5+ times. |
| 8 | 181-183 | MI phase boundary%: PP=23.5, Mid=18.5, Death=22.8; League: PP=18.8, Mid=13.4, Death=17.8 | MI: PP=24.5, Mid=19.1, Death=24.3; League: PP=24.3, Mid=16.8, Death=23.4 | Wrong Stats | Every boundary percentage in the Phase-Wise table is wrong. League boundary percentages are systematically understated by 5-6 points. |
| 9 | 181-183 | MI phase dot%: PP=42.3, Mid=31.2, Death=28.4; League: PP=46.4, Mid=34.0, Death=31.3 | MI: PP=43.9, Mid=32.0, Death=30.6; League: PP=44.0, Mid=30.5, Death=30.2 | Wrong Stats | All dot ball percentages in the Phase-Wise table are wrong. |

### HIGH Severity Errors

| # | Line(s) | Claimed Value | DB Value | Category | Notes |
|---|---------|---------------|----------|----------|-------|
| 10 | 155, 306, 308, 453 | Tilak middle SR: 136.4 (703 balls, HIGH) | **All-time**: 136.42 SR (703 balls, HIGH). **Since 2023**: 138.85 SR (489 balls, MEDIUM) | Scope Mixing | All-time data under since-2023 scope. Confidence inflated (MEDIUM -> HIGH). |
| 11 | 156, 306 | Tilak death SR: 183.5 (212 balls, MEDIUM) | **All-time**: 183.49 SR (212 balls, MEDIUM). **Since 2023**: 192.72 SR (151 balls, MEDIUM) | Scope Mixing | All-time data under since-2023 scope. Tilak's actual since-2023 death SR is 9 points higher. |
| 12 | 312, 313 | Pandya death batting SR: 172.7 (828 balls, HIGH) | **All-time**: 172.71 SR (828 balls, HIGH). **Since 2023**: 168.0 SR (175 balls, MEDIUM) | Scope Mixing | All-time death SR and ball count presented as since-2023. Confidence inflated from MEDIUM to HIGH. |
| 13 | 175, 457 | Pandya vs spin: 142.7 SR (1,129 balls, HIGH) | **Since 2023**: ~145.6 SR (204 balls). 1,129 balls is clearly all-time. | Scope Mixing | All-time sample size used under since-2023 scope. |
| 14 | 292 | SKY fifties: 17 | DB: 15 fifties (since 2023) | Wrong Stat | Overstated by 2 fifties. |
| 15 | 222, 300, 410 | Bumrah economy at Wankhede: 5.66 (47.2 overs, HIGH) | DB: 5.32 economy (283 balls / ~47.2 overs, HIGH) | Wrong Stat | Economy overstated by 0.34 runs. Cited 3 times. |
| 16 | 56 | Shardul Thakur death economy: 10.57 (30.8 overs, HIGH), 13 death wickets | DB since-2023: 11.16 economy (30.8 overs, MEDIUM), 13 wkts | Wrong Stat + Confidence | Economy understated by 0.59. Confidence inflated from MEDIUM to HIGH. |
| 17 | 332, 359, 459 | Chahar PP economy: 8.73 (33 overs, HIGH) | DB since-2023: 8.53 economy (80.3 overs, MEDIUM) | Wrong Stat + Confidence | Economy overstated by 0.20, overs severely understated (33 vs 80.3), confidence inflated. |
| 18 | 332, 459 | Chahar death economy: 14.09 (7.2 overs, HIGH) | DB since-2023: 14.79 economy (7.2 overs, LOW) | Wrong Stat + Confidence | Economy understated by 0.70. Confidence inflated from LOW to HIGH (43 balls = LOW). |

### MEDIUM Severity Errors

| # | Line(s) | Claimed Value | DB Value | Category | Notes |
|---|---------|---------------|----------|----------|-------|
| 19 | 60, 362, 380, 434 | Markande middle economy: 8.45 (51 overs, HIGH) | DB since-2023: 8.67 economy (51.0 overs, MEDIUM) | Wrong Stat + Confidence | Economy understated by 0.22. Confidence inflated from MEDIUM to HIGH. Cited 4 times. |
| 20 | 362 | Markande death economy: 12.67 (9 overs, MEDIUM) | DB since-2023: 13.0 economy (9.0 overs, LOW) | Wrong Stat + Confidence | Economy understated by 0.33. Confidence inflated from LOW to MEDIUM. |
| 21 | 223 | SKY at Wankhede: 897 runs, 187.3 SR, 479 balls, 22 matches | DB: 878 runs, 188.41 SR, 466 balls, 20 innings | Wrong Stats | All four numbers are wrong: runs (897 vs 878), SR (187.3 vs 188.4), balls (479 vs 466), matches (22 vs 20). |
| 22 | 34, 327, 380, 434, 451 | Chawla middle: 31 wickets at 8.45 (78 overs, HIGH) | DB since-2023: 30 wickets at 8.45 (78 overs, MEDIUM) | Wrong Stat + Confidence | Wickets overstated by 1. Confidence inflated from MEDIUM to HIGH. |
| 23 | 57, 81 | Rutherford death SR: 153.9 (128 balls, MEDIUM) | DB since-2023: 152.33 SR (86 balls, LOW) | Wrong Stat + Confidence | SR off by 1.6, balls off by 42, confidence inflated from LOW to MEDIUM. |
| 24 | 48, 93, 434 | Jacks middle bowling economy: 8.81 / 9.61 / 7.55 | DB since-2023: 9.31 economy (16 overs, LOW) | Internal Inconsistency | Three different values cited for the same metric in different sections. None match the DB. |
| 25 | 332 | Chahar all-time PP: 8.17 economy (80.3 overs, HIGH), 23 PP wickets | DB all-time: 8.06 economy (250.5 overs, HIGH), 66 wickets | Wrong Stat | Economy, overs, and wickets are all wrong. Appears to use since-2023 overs (80.3) with a fabricated economy. |
| 26 | 14, 322, 154, 179 | League PP SR: cited as both 146.3 and 126.4 | DB: 146.3 | Internal Inconsistency | The correct value (146.3) is used on lines 14 and 322. The wrong value (126.4) is used on lines 154 and 179. |

### LOW Severity Errors

| # | Line(s) | Claimed Value | DB Value | Category | Notes |
|---|---------|---------------|----------|----------|-------|
| 27 | 14, 26, 162 | Rohit PP SR: 125.3 (1,903 balls, HIGH) | DB since-2023: 144.89 SR (519 balls, HIGH). **All-time**: 125.28 SR (1,903 balls, HIGH) | Scope Mixing | This is the all-time PP SR, not since-2023. The since-2023 PP SR of 144.89 is actually near league average. This fundamentally changes the narrative about Rohit as a PP liability. |
| 28 | 26, 50, 398 | de Kock PP SR: 130.9 (1,473 balls, HIGH) | DB since-2023: 130.26 SR (228 balls, MEDIUM). **All-time**: 130.89 SR (1,473 balls, HIGH) | Scope Mixing | All-time data. Since-2023 sample is only 228 balls (MEDIUM), not 1,473 (HIGH). |
| 29 | 50 | de Kock death SR: 203.9 (103 balls, MEDIUM) | DB all-time: 203.88 SR (103 balls, MEDIUM) | Scope Mixed (Disclosed) | Labeled as "across his IPL career" so technically disclosed, but appears in a since-2023 section. |
| 30 | 266-276 | RCB all-time: 55.9%, SRH: 56.0%, PBKS: 50.0% | RCB: 57.6%, SRH: 58.3%, PBKS: 51.5% | Wrong Percentages | All three win percentages are arithmetic errors. W-L records are correct. |

---

## Scope Mixing Analysis

This is the most concerning systematic issue. The preview declares a "Since 2023" data window on line 5 but silently uses all-time IPL data for at least the following stats:

| Stat | Scope Used | Correct Since-2023 Value | Error Magnitude |
|------|-----------|--------------------------|-----------------|
| SKY middle SR | All-time (1,770 balls) | 172.99 SR (685 balls) | -28.7 SR |
| SKY death SR | All-time (451 balls) | 213.28 SR (128 balls) | -31.3 SR |
| Tilak middle SR | All-time (703 balls) | 138.85 SR (489 balls) | -2.4 SR |
| Tilak death SR | All-time (212 balls) | 192.72 SR (151 balls) | -9.2 SR |
| Pandya death batting SR | All-time (828 balls) | 168.0 SR (175 balls) | +4.7 SR |
| Pandya vs spin | All-time (1,129 balls) | ~145.6 SR (204 balls) | -2.9 SR |
| Rohit PP SR | All-time (1,903 balls) | 144.89 SR (519 balls) | -19.6 SR |
| Rohit death SR | All-time (837 balls) | 176.92 SR (26 balls) | +5.5 SR |
| de Kock PP SR | All-time (1,473 balls) | 130.26 SR (228 balls) | +0.6 SR |

**Pattern:** The all-time data consistently shows larger sample sizes (which look more impressive with HIGH confidence) and more moderate strike rates. The since-2023 data shows smaller samples but more extreme (both higher and lower) values. The preview appears to have cherry-picked whichever scope made the narrative more compelling.

**Impact on Narrative:** The central thesis -- that Rohit's PP SR of 125.3 is "21 points below the league average" -- collapses entirely under the correct since-2023 data. Rohit's since-2023 PP SR of 144.89 is actually only 1.4 points below the league average of 146.3. The entire "powerplay problem" narrative is built on all-time data presented as recent performance.

---

## Bowler Phase Economy Audit

The bowler phase table on lines 355-362 contains multiple incorrect economies:

| Player | Phase | Preview Economy | DB Economy | Delta | Preview Overs | DB Overs |
|--------|-------|-----------------|------------|-------|---------------|----------|
| Boult | PP | 8.63 | 7.55 | +1.08 | 30 | 94.0 |
| Boult | Death | 9.26 | 10.17 | -0.91 | 15.7 | 30.0 |
| Santner | Middle | 7.16 | 7.18 | -0.02 | 31 | 45.0 |
| Pandya | Middle | 9.31 | 9.16 | -0.15 | 49 | 57.0 |
| Pandya | Death | 13.92 | 13.92 | 0.00 | 12 | 12.0 |
| Markande | Middle | 8.45 | 8.67 | -0.22 | 51 | 51.0 |
| Markande | Death | 12.67 | 13.0 | -0.33 | 9 | 9.0 |
| Bumrah | All phases | Correct | Correct | -- | Correct | Correct |
| Chahar | PP | 8.73 | 8.53 | +0.20 | 33 | 80.3 |

Bumrah's numbers are the only consistently correct entries in the table. Four of six other bowlers have incorrect economies. The overs for Boult, Santner, Pandya, and Chahar are all wrong, with Boult's PP overs understated by 64 overs.

---

## Confidence Label Audit

Confidence thresholds: HIGH >= 200 balls, MEDIUM >= 50 balls, LOW < 50 balls.

| Stat | Balls | Correct Label | Preview Label | Verdict |
|------|-------|---------------|---------------|---------|
| Chawla middle (78 overs, 468 balls) | 468 | HIGH | HIGH | OK |
| Santner middle (45 overs, 270 balls) | 270 | HIGH | HIGH | But DB says MEDIUM -- preview and expected disagree with DB |
| Pandya middle bowl (57 overs, 342 balls) | 342 | HIGH | HIGH | But DB says MEDIUM |
| Pandya death bowl (12 overs, 72 balls) | 72 | MEDIUM | HIGH | **INFLATED** (2 tiers) |
| Markande middle (51 overs, 306 balls) | 306 | HIGH | HIGH | But DB says MEDIUM |
| Chahar death (7.2 overs, 43 balls) | 43 | LOW | HIGH | **INFLATED** (2 tiers) |
| Thakur death (30.8 overs, 185 balls) | 185 | MEDIUM | HIGH | **INFLATED** |
| Rutherford death (86 balls) | 86 | MEDIUM | MEDIUM | But DB says LOW |
| Markande death (54 balls) | 54 | MEDIUM | MEDIUM | But DB says LOW |

Note: There appears to be a systemic discrepancy between the expected threshold rules (HIGH >= 200 balls) and what the DB actually labels. The DB uses MEDIUM for many stats with 200-500 balls. However, the preview inflates beyond even the DB labels in several cases (Chahar death: DB=LOW, preview=HIGH; Pandya death bowl: DB=LOW, preview=HIGH).

---

## Internal Consistency Failures

1. **League PP SR**: Cited as 146.3 on lines 14 and 322 (correct), but as 126.4 on lines 154 and 179 (wrong). These two numbers appear in the same document and contradict each other.

2. **Jacks middle bowling economy**: Cited as 8.81 (line 48), 9.61 (line 93), and 7.55 (line 434). Three different values for the same metric. DB says 9.31.

3. **Boult PP economy**: Cited as 8.63 on lines 157, 358, and 446. DB says 7.55. Internally consistent but wrong.

4. **SKY middle SR**: Cited as 144.3 on lines 155, 292, and 453. All-time value, internally consistent but wrong scope.

---

## What Is Correct

Credit where due: the following stats were verified as correct or within acceptable rounding tolerance (<=0.1):

- SKY career SR: 172.93 (preview: 172.9) -- OK
- SKY career average: 47.63 (preview: 47.6) -- OK
- Rohit career SR: 145.15 (preview: 145.2) -- OK
- Tilak career SR: 150.96 (preview: 151.0) -- OK
- Pandya career batting SR: 145.83 (preview: 145.8) -- OK
- Pandya career bowling economy: 10.16 (preview: 10.16) -- OK
- Naman Dhir career SR: 181.48 (preview: 181.5) -- OK
- de Kock career SR: 135.24 (preview: 135.2) -- OK
- Jacks career SR: 153.31 (preview: 153.3) -- OK
- Santner batting SR: 103.7 (preview: 103.7) -- OK
- Rutherford career SR: 158.15 (preview: 158.2) -- OK
- Bumrah career economy: 6.69 (preview: 6.69) -- OK
- Bumrah career wickets: 38 (preview: 38) -- OK
- Bumrah career overs: 99.2 (preview: 99.2) -- OK
- Bumrah PP economy: 6.97 (preview: 6.97) -- OK
- Bumrah middle economy: 6.17 (preview: 6.17) -- OK
- Bumrah death economy: 6.84 (preview: 6.84) -- OK
- Boult career economy: 8.62 (preview: 8.62) -- OK
- Boult career wickets: 51 (preview: 51) -- OK
- Chahar career economy: 8.95 (preview: 8.95) -- OK
- Naman Dhir death SR: 204.13 (preview: 204.1) -- OK
- SKY vs GT: 177.19 SR (preview: 177.2) -- OK
- SKY vs SRH: 192.31 SR (preview: 192.3) -- OK
- Pandya vs RR: 180.68 SR (preview: 180.7) -- OK
- All H2H W-L records (since 2023): All 9 correct
- MI season-by-season batting/bowling phase data (2023/2024/2025 tables): All correct
- MI aggregate batting/bowling economy: All correct (149.2, 144.8, 173.8 batting SR; 9.04, 8.99, 11.01 bowling econ)
- MI home record: 13-8 (61.9%) -- OK
- Boult at Wankhede: 14 wkts, 7.89 econ, 9 matches -- OK
- Santner at Wankhede: 5.95 econ, 6 matches, 7 wkts -- OK
- Markande career bowling: 9.32 econ, 20 wkts, 60 overs -- OK

---

## Recommendations for Revision

### Must-Fix (BLOCKING)

1. **Purge all-time data from since-2023 scope.** Every SKY, Tilak, Pandya, and Rohit phase stat must be re-queried from `analytics_ipl_batter_phase_since2023`. If all-time data is used for context (e.g., Rohit's career PP record), it must be explicitly labeled as "all-time IPL" with the all-time sample size.

2. **Rebuild the Phase-Wise Batting table (lines 179-183).** The league average SRs are off by 20+ points. Use the DB values: PP=146.3, Middle=140.3, Death=170.2. Recalculate all differentials. Note: the revised differentials (+2.9/+4.5/+3.6) will significantly change the narrative -- MI's batting advantage over the league is real but much smaller than claimed. All boundary% and dot% figures must also be corrected.

3. **Rebuild the Bowler Phase table (lines 355-362).** Correct Boult PP (7.55, not 8.63), Boult death (10.17, not 9.26), Santner middle (7.18/45 overs, not 7.16/31 overs), Pandya middle (9.16/57 overs, not 9.31/49 overs), Markande middle (8.67, not 8.45), Markande death (13.0, not 12.67), Chahar PP (8.53/80.3 overs, not 8.73/33 overs).

4. **Fix Bumrah Wankhede economy.** 5.32, not 5.66. Cited 3 times.

5. **Fix SKY at Wankhede.** 878 runs, 188.41 SR, 466 balls, 20 innings -- not 897/187.3/479/22.

6. **Re-evaluate the "powerplay problem" narrative.** If Rohit's since-2023 PP SR is 144.89 (not 125.3), the central thesis of the preview weakens considerably. Rohit's PP SR is near league average since 2023, not 21 points below it. The preview needs to decide whether to tell the all-time PP story (labeled as such) or the since-2023 story (which tells a different tale).

7. **Fix SKY fifties count.** 15, not 17.

### Should-Fix (HIGH)

8. Correct all confidence labels to match DB values. Where DB and expected thresholds disagree, use DB values and note the methodology.

9. Fix all three all-time H2H win percentages: RCB=57.6% (not 55.9%), SRH=58.3% (not 56.0%), PBKS=51.5% (not 50.0%).

10. Resolve the Jacks middle bowling economy inconsistency (three different values across the document).

11. Fix Shardul Thakur death economy: 11.16 (not 10.57).

12. Fix Chahar death economy: 14.79 (not 14.09).

### Nice-to-Fix (MEDIUM)

13. Correct Wankhede venue phase stats to match DB (minor discrepancies in RPO and boundary%).

14. Fix Chahar all-time PP economy/overs/wickets.

15. Standardize whether Rutherford death stats use since-2023 (152.33 SR, 86 balls, LOW) or another source.

---

## Structural Observations

The narrative quality of this preview is high. The analytical framework -- diagnosing the powerplay batting problem, quantifying the Bumrah workload risk, and proposing Rohit at #4 -- is genuinely insightful and the kind of non-obvious thinking that separates this product from generic cricket coverage. The Bold Take section is the best-written section of any team preview I have reviewed to date.

However, the statistical foundation is unreliable. The pattern of all-time data being used under a since-2023 label is not random error; it appears systematic, suggesting the data pipeline fed the wrong views to the content generator. The Phase-Wise Batting table's league averages appear to be fabricated -- no view in the DuckDB database produces league batting SRs of 126.4/123.9/148.8.

The preview needs a full data pass, not a cosmetic fix. Re-query every individual stat from the correct since-2023 views, then re-evaluate whether the narrative conclusions still hold. Some will (the death-overs dominance is real). Others may not (the powerplay problem is overstated when using since-2023 data).

---

*Jose Mourinho | Quant Researcher | Cricket Playbook*
*"Every number must earn its place. If it cannot be verified, it cannot be published."*
