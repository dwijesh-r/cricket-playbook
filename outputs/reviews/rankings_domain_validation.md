# Rankings Domain Validation Report

**Ticket:** TKT-238 (Hustle)
**Reviewer:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-26
**Scope:** Domain validation of all 7 ranking categories across alltime and since-2023 scopes
**Methodology Reference:** `outputs/rankings/rankings_methodology_v1.md` (v1.1)
**Database:** `data/cricket_playbook.duckdb`

---

## Overall Assessment: PASS

The ranking system produces sensible, defensible leaderboards across all seven categories. The composite weights, qualification thresholds, and sample size weighting work together to surface genuinely elite performers while suppressing small-sample noise. No blocking anomalies found.

---

## Category 1: Overall Batter Composite Rankings (Alltime)

**View:** `analytics_ipl_batter_composite_rankings_alltime` (128 qualified batters)

| Rank | Player | Inn | Runs | SR | Avg | Composite |
|------|--------|-----|------|----|-----|-----------|
| 1 | H Klaasen | 45 | 1,480 | 171.49 | 41.11 | 93.4 |
| 2 | B Sai Sudharsan | 40 | 1,793 | 146.85 | 51.23 | 87.0 |
| 3 | TM Head | 37 | 1,146 | 171.81 | 35.81 | 86.1 |
| 4 | N Pooran | 86 | 2,293 | 169.48 | 35.83 | 85.5 |
| 5 | AB de Villiers | 170 | 5,162 | 152.18 | 42.31 | 84.9 |

**Bottom 5:** PP Chawla (4.3), R Ashwin (10.8), AM Nayar (11.9), NV Ojha (16.3), MS Bisla (18.0)

**Domain Assessment:** PASS

- Klaasen at #1 is defensible. His 171.49 SR combined with 41.11 average and elite phase versatility (95.4 SR percentile across phases) reflects a genuinely dominant recent-era T20 batter.
- AB de Villiers at #5 validates the system's respect for large sample sizes (170 innings, 3,392 balls). His alltime credentials are beyond question.
- Sai Sudharsan at #2 is the one result that may raise editorial eyebrows. His 51.23 average (highest among top 10) and strong phase consistency drive the score, but his 146.85 SR is the lowest in the top 5. The system is correctly weighting his exceptional survivability and phase versatility, but editorial commentary should note his accumulator profile relative to Klaasen/Head/Pooran.
- Bottom 5 are primarily lower-order batters or part-timers who faced 500+ balls -- PP Chawla, R Ashwin. This is correct: they qualify on volume but their batting metrics are appropriately poor.

**Key Player Check:**
- V Kohli: Rank #28 (alltime), composite 67.0. His 133.23 SR across 259 innings pulls him down in a system that heavily weights strike rate. This is analytically correct for T20 evaluation -- Kohli's IPL SR has been below the qualified-population median (150.44) for his career. His 39.91 average keeps him in the upper half but not elite by this system's standards.
- Shubman Gill: Rank #20 (alltime), composite 74.1. SR of 139.37 with 40.69 average. Reasonable mid-table position.
- SA Yadav (SKY): Rank #8 (alltime), composite 81.6. Top-10 presence is correct given his 149.27 SR, 36.23 average, and strong phase numbers.

**Since-2023 Scope:**
- Top 5: Pooran (86.4), Klaasen (83.6), SS Iyer (82.1), SA Yadav (81.7), Shubman Gill (74.6)
- Kohli at #12 (62.9) with 146.55 SR and 56.58 average. His elite average cannot fully compensate for a strike rate that sits below T20 elite thresholds in a SR-weighted system. Analytically sound.
- Retired players (ABD, Gayle) correctly absent from since-2023. Warner present at #31 (played 2023-2025).

---

## Category 2: Overall Bowler Composite Rankings (Alltime)

**View:** `analytics_ipl_bowler_composite_rankings_alltime` (199 qualified bowlers)

| Rank | Player | Matches | Balls | Wkts | Econ | Composite |
|------|--------|---------|-------|------|------|-----------|
| 1 | DE Bollinger | 27 | 576 | 37 | 7.46 | 90.2 |
| 2 | SL Malinga | 122 | 2,828 | 170 | 7.40 | 88.7 |
| 3 | AD Mascarenhas | 13 | 308 | 19 | 7.11 | 88.4 |
| 4 | A Kumble | 42 | 965 | 45 | 6.77 | 88.1 |
| 5 | JJ Bumrah | 145 | 3,337 | 183 | 7.43 | 88.1 |

**Bottom 5:** Shahbaz Ahmed (6.8), Basil Thampi (11.7), Abhishek Sharma (14.2), MP Stoinis (15.2), R McLaren (15.3)

**Domain Assessment:** PASS (with minor observations)

- Bumrah at #5 alltime is slightly lower than intuition might suggest, but the methodology document correctly noted his since-2023 dominance (97.6 composite, clear #1). The alltime view includes his earlier career when he was developing.
- Malinga at #2 is excellent -- 2,828 balls, 170 wickets, 7.40 economy. One of the greatest IPL bowlers ever, correctly positioned.
- Bollinger at #1 is the mild surprise. With only 27 matches and 576 balls, he sits at the qualification floor relative to Malinga. His 7.46 economy and 44.10% dot ball rate are strong, and his phase consistency (83.3 economy pctl, 85.4 dot ball pctl) pushes the composite. The sample size weighting does not penalize him here because 576 balls exceeds the 300-ball career target. This is defensible but worth editorial annotation.
- Mascarenhas at #3 with only 13 matches / 308 balls is the weakest result. He barely exceeds the 300-ball qualification. His numbers are genuinely excellent (7.11 economy, 19.21 average) but the small sample deserves a footnote.
- Bottom 5 are correctly populated with part-time or underperforming bowlers.

**Since-2023 Scope:**
- Bumrah dominates at 97.6 (6.69 economy, 38 wickets in 25 matches). The 12.2-point gap to #2 Varun Chakravarthy (85.4) is the largest in the system. Domain-validated: Bumrah's 2023-2025 IPL form was generationally dominant.

---

## Category 3: Batter Phase Rankings (Alltime)

### Powerplay

| Rank | Player | Balls | SR | Avg | Composite |
|------|--------|-------|----|-----|-----------|
| 1 | TM Head | 365 | 184.38 | 44.87 | 92.8 |
| 2 | JM Bairstow | 623 | 151.52 | 49.68 | 91.4 |
| 3 | YBK Jaiswal | 864 | 159.49 | 44.45 | 89.6 |
| 4 | CA Lynn | 537 | 145.07 | 48.69 | 87.9 |
| 5 | SA Yadav | 667 | 140.33 | 58.50 | 87.0 |

**Assessment:** PASS. Head's 184.38 PP SR is genuinely elite. Jaiswal at #3 with 864 balls validates his opening prowess. Lynn and Bairstow are known PP destroyers. SKY's 58.50 PP average is extraordinary.

### Middle Overs

| Rank | Player | Balls | SR | Avg | Composite |
|------|--------|-------|----|-----|-----------|
| 1 | H Klaasen | 526 | 159.32 | 59.86 | 95.7 |
| 2 | DP Conway | 341 | 152.79 | 65.13 | 95.4 |
| 3 | N Pooran | 764 | 167.02 | 44.00 | 94.1 |
| 4 | CH Gayle | 1,285 | 156.50 | 44.69 | 93.2 |
| 4 | SE Marsh | 971 | 149.12 | 51.71 | 93.2 |

**Assessment:** PASS. Klaasen's middle-overs dominance (159.32 SR, 59.86 avg) is well-documented. Conway's 65.13 average reflects his anchoring role. Gayle with 1,285 middle-overs balls is a massive validation sample.

### Death Overs

| Rank | Player | Balls | SR | Avg | Composite |
|------|--------|-------|----|-----|-----------|
| 1 | AB de Villiers | 829 | 225.33 | 46.70 | 99.2 |
| 2 | T Stubbs | 199 | 220.60 | 87.80 | 98.5 |
| 3 | CH Gayle | 280 | 207.50 | 38.73 | 97.3 |
| 4 | Shashank Singh | 219 | 193.61 | 42.40 | 93.0 |
| 5 | JC Buttler | 368 | 198.10 | 33.14 | 91.7 |

**Assessment:** PASS. ABD at 225.33 death SR over 829 balls is arguably the greatest death-overs batting record in IPL history. Stubbs' sample size weighting (factor 0.995 at 199 balls vs 200 target) is minimal but present. Shashank Singh is an emerging death-overs finisher -- his inclusion validates the system catching current form.

**Bottom Entries:** B Kumar (94.70 death SR), Z Khan, DW Steyn, Mohammed Siraj -- all bowlers batting at death. Correct.

---

## Category 4: Bowler Phase Rankings (Alltime)

### Powerplay

| Rank | Player | Balls | Econ | Dot% | Composite |
|------|--------|-------|------|------|-----------|
| 1 | R Rampaul | 156 | 5.85 | 58.33% | 97.9 |
| 2 | GD McGrath | 222 | 5.89 | 57.21% | 97.3 |
| 3 | WPUJC Vaas | 198 | 6.39 | 57.07% | 94.3 |
| 4 | Sohail Tanvir | 132 | 6.59 | 57.58% | 94.1 |
| 5 | BW Hilfenhaus | 240 | 6.50 | 55.42% | 93.3 |

**Assessment:** PASS. Early-IPL era seamers (2008-2012 conditions, less batting-friendly) dominate PP bowling. McGrath at 5.89 economy and 57% dot ball rate is extraordinary. These are legitimate historical performances even if the era context differs. Sample size weighting correctly removed AG Murtaza and FH Edwards (78 balls each) from the top.

### Middle Overs

| Rank | Player | Balls | Econ | Dot% | Composite |
|------|--------|-------|------|------|-----------|
| 1 | MM Patel | 396 | 6.17 | 39.39% | 97.6 |
| 2 | Azhar Mahmood | 186 | 6.61 | 40.86% | 96.6 |
| 3 | DW Steyn | 408 | 6.75 | 43.38% | 96.1 |
| 4 | Shivam Mavi | 162 | 6.85 | 43.83% | 95.6 |
| 5 | JJ Bumrah | 870 | 6.66 | 39.66% | 95.4 |

**Assessment:** PASS. Bumrah at #5 with 870 middle-overs balls is the most trusted entry on this list. MM Patel (Munaf Patel) at 6.17 economy in the middle overs is a genuine performance. Steyn's 408-ball sample at 6.75 economy validates his elite multi-phase bowling.

### Death Overs

| Rank | Player | Balls | Econ | Dot% | Composite |
|------|--------|-------|------|------|-----------|
| 1 | DE Bollinger | 234 | 7.62 | 37.61% | 98.3 |
| 2 | SP Narine | 1,051 | 7.50 | 36.44% | 97.2 |
| 3 | M Muralitharan | 275 | 8.29 | 37.45% | 95.2 |
| 4 | A Kumble | 167 | 7.80 | 34.73% | 95.0 |
| 5 | Noor Ahmad | 127 | 8.41 | 42.52% | 94.7 |

**Assessment:** PASS. Narine's 1,051 death-overs balls at 7.50 economy is the single most impressive line in any ranking. The spinner-heavy composition (Narine, Muralitharan, Kumble, Noor Ahmad) at death is counter-intuitive but data-supported -- these spinners genuinely restricted scoring at death through dot-ball pressure, not just wicket-taking.

---

## Category 5: Batter vs Bowling Type Rankings (Alltime)

**View:** `analytics_ipl_batter_vs_bowling_type_rankings_alltime`

**Sample Top-5 by Bowling Type:**

| vs Fast | vs Off-spin | vs Leg-spin | vs Left-arm Orthodox |
|---------|------------|------------|---------------------|
| LS Livingstone (91.1) | HH Pandya (86.2) | RM Patidar (89.5) | DA Warner (94.9) |
| JP Inglis (90.4) | H Klaasen (85.3) | N Wadhera (89.0) | SPD Smith (87.9) |
| RA Jadeja (87.2) | JC Buttler (77.2) | H Klaasen (85.3) | AB de Villiers (87.7) |
| A Badoni (83.4) | DA Warner (75.9) | N Pooran (84.1) | CH Gayle (86.1) |
| KD Karthik (81.5) | RA Tripathi (72.1) | SA Yadav (83.7) | F du Plessis (81.3) |

**Assessment:** PASS

- Klaasen appearing in both off-spin (#2) and leg-spin (#3) top-5 validates his known spin-hitting dominance. His 181.82 SR vs off-spin (88 balls) is a concrete scouting signal.
- Warner's 158.45 SR vs left-arm orthodox (142 balls) with 112.50 average is remarkable -- well-known for punishing left-arm spin.
- Livingstone topping the vs-Fast chart (201.48 SR, 135 balls) is cricket-sensible: he is an aggressive middle-order hitter known for taking on pace.
- Sample size weighting correctly adjusts Inglis (91 balls, factor < 1.0) below Livingstone.

---

## Category 6: Bowler vs Handedness Rankings (Alltime)

**View:** `analytics_ipl_bowler_vs_handedness_rankings_alltime`

| vs Left-hand Top 5 | vs Right-hand Top 5 |
|---------------------|---------------------|
| M Prasidh Krishna (96.2) | TA Boult (87.2) |
| JJ Bumrah (96.2) | PP Chawla (84.4) |
| Noor Ahmad (92.4) | JJ Bumrah (83.5) |
| RD Chahar (87.5) | E Malinga (82.6) |
| M Pathirana (81.5) | M Prasidh Krishna (81.2) |

**Assessment:** PASS

- Bumrah appearing in both top-5 lists (#1 tied vs LHB, #3 vs RHB) reinforces his handedness-agnostic dominance. This is the strongest cross-category validation signal in the system.
- Boult at #1 vs right-handers (388 balls, 28 wickets, 8.46 economy) is cricket-sensible: his left-arm swing angle creates natural danger to right-hand batters.
- Noor Ahmad at #3 vs left-handers as a left-arm wrist spinner is a genuine matchup insight -- his stock delivery (away from the left-hander) creates dismissal opportunities.

---

## Category 7: Player Matchup Rankings (Alltime)

**View:** `analytics_ipl_player_matchup_rankings_alltime`

**Top 5 Batter-Favored (by weighted dominance):**

| Batter | Bowler | Balls | SR | Dominance |
|--------|--------|-------|----|-----------|
| RR Pant | B Kumar | 54 | 222.22 | +79.02 |
| MS Dhoni | JD Unadkat | 44 | 240.91 | +73.54 |
| KL Rahul | Mohammed Siraj | 79 | 170.89 | +56.27 |
| JC Buttler | Sandeep Sharma | 48 | 189.58 | +49.93 |
| Abhishek Sharma | Rashid Khan | 36 | 227.78 | +49.75 |

**Top 5 Bowler-Favored (by weighted dominance):**

| Batter | Bowler | Balls | SR | Dominance |
|--------|--------|-------|----|-----------|
| MS Dhoni | SP Narine | 77 | 51.95 | -43.27 |
| JC Buttler | Rashid Khan | 50 | 60.00 | -43.25 |
| MK Pandey | AR Patel | 67 | 64.18 | -36.36 |
| MS Dhoni | RD Chahar | 34 | 55.88 | -30.00 |
| SV Samson | SP Narine | 81 | 80.25 | -27.89 |

**Assessment:** PASS

- Pant vs Bhuvi Kumar (54 balls, 222.22 SR) is a well-known IPL matchup where Pant has historically dominated. Correct.
- Dhoni vs Unadkat (240.91 SR over 44 balls) is a documented mismatch. Correct.
- Dhoni vs Narine (51.95 SR over 77 balls) is equally well-documented -- Narine's mystery spin troubled Dhoni consistently. This is the strongest bowler-favored validation.
- Buttler vs Rashid Khan (60.00 SR, 4 dismissals in 50 balls) is a known weakness. Correct.
- Sample size weighting appropriately promotes higher-ball-count matchups (Pant-Bhuvi at 54 balls) above the raw-dominance leaders from the methodology doc (TH David-Mukesh Kumar at 13 balls).

---

## Cross-Category Consistency Checks

| Check | Result | Notes |
|-------|--------|-------|
| All composites in 0-100 range | PASS | Zero rows outside range in batter and bowler composites |
| No null composites | PASS | Zero nulls across 128 batter rows and 199 bowler rows |
| Retired players absent from since-2023 | PASS | ABD and Gayle correctly absent; Warner present (played 2023-25) |
| Sample size factors all in [0,1] | PASS | All factors between 0 and 1, capped at 1.0 |
| Dual-scope separation | PASS | Alltime and since-2023 produce distinct rankings reflecting career vs current form |
| Bottom entries sensible | PASS | Bottom-ranked batters are bowling all-rounders/part-timers; bottom bowlers are batting all-rounders |

---

## Anomalies and Observations (Non-Blocking)

1. **Sai Sudharsan at #2 alltime batter composite.** His 146.85 SR is the lowest among the top 5, but his 51.23 average (highest) and strong phase consistency inflate the composite. Editorially, this should be annotated -- he is an accumulator in an aggressor-rewarding system, yet the average and phase weights lift him. Not incorrect, but readers may question it without context.

2. **Mascarenhas at #3 alltime bowler composite.** Only 13 matches and 308 balls (barely above 300-ball threshold). His numbers are genuine but the small sample means he benefits from the binary qualification cutoff. The sample size weighting only applies within sub-categories (phase, matchup), not to career composites where all players exceed the target. Consider whether career composites should also apply graduated weighting above the minimum.

3. **Bollinger at #1 alltime bowler composite.** Similar to Mascarenhas -- 27 matches, 576 balls. His numbers are strong but the body of work is thin compared to Malinga (2,828 balls) and Bumrah (3,337 balls). The system cannot distinguish between "small sample elite" and "large sample elite" at the career composite level because all exceed 300 balls.

4. **Early-era bowler dominance in phase rankings.** PP bowling top-5 is dominated by 2008-2012 era bowlers (McGrath, Vaas, Rampaul, Hilfenhaus). This reflects genuine historical performance but lower batting standards in early IPL. The since-2023 scope addresses this for current-form analysis, but the alltime view inherently includes era effects. This is a known limitation, not a bug.

5. **Kohli at #28 alltime / #12 since-2023.** This will be the most questioned ranking among readers. The system is analytically correct -- Kohli's career IPL SR of 133.23 is well below the qualified-population average (152.98). His 2023-2025 improvement to 146.55 SR moves him to #12. Editorial framing is critical: Kohli is one of the greatest IPL batters by volume and clutch performance, but a percentile-composite system that weights SR at 30% will not place him in the top 10. This is a feature of the methodology, not a flaw. Recommend a sidebar explaining this.

---

## Recommendations

1. **Editorial annotation for Sai Sudharsan (#2) and Kohli (#28/#12).** These are the two results most likely to generate reader pushback. Both are analytically defensible but need contextual framing.

2. **Consider graduated career composite weighting.** Currently, career composites treat a 308-ball bowler and a 3,337-ball bowler identically (both get factor 1.0). The phase/matchup views correctly apply sample size weighting, but career composites do not differentiate above the minimum. A higher target (e.g., 1,000 balls for bowlers, 1,500 for batters) at the career level would further separate sustained excellence from qualified-but-small samples.

3. **Era-adjustment disclaimer.** The alltime bowler phase rankings should carry an editorial note about early-IPL conditions. The since-2023 scope is the actionable one for pre-tournament use.

---

## Verdict

**PASS** -- All seven ranking categories produce sensible, defensible leaderboards. The composite weights, qualification thresholds, sample size weighting, and dual-scope architecture work as designed. The observations above are editorial considerations, not analytical errors. The rankings are ready for integration into stat packs and the magazine.

---

**Signed:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-26
**Ticket:** TKT-238 VALIDATED

*Cricket Playbook v5.0.0 | Rankings Domain Validation*
