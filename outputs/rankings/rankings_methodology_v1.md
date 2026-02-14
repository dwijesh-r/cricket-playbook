# Cricket Playbook Rankings -- Methodology & Breakdown

**Version:** 1.0
**Date:** 2026-02-14
**Authors:** Stephen Curry (Analytics Lead), Tom Brady (PO & Editor-in-Chief)
**Ticket:** TKT-235 (EPIC-021)
**Governance:** thresholds.yaml v1.1.0 | Constitution v2.2.0

---

## Executive Summary

The Cricket Playbook Rankings are a proprietary, composite player evaluation system built for the IPL 2026 pre-tournament preview magazine. They answer the question every serious cricket analyst and team strategist asks before a tournament: **Who are the best players, and why -- backed by data, not narrative?**

### What It Is

A seven-category ranking framework that evaluates IPL players across career performance, phase specialization, matchup dominance, and role-specific metrics. Every ranking is derived from percentile-based composites -- meaning a player is measured not in raw numbers, but in how they compare to the entire qualified IPL population.

### Why It Matters

Traditional cricket rankings (ICC, MVP indices) rely on points-per-match or weighted aggregates that struggle with T20's volatility. A batter who scores 40(18) in the death overs is providing dramatically different value than 40(30) in the powerplay, yet most systems treat them identically. Our rankings decompose performance by phase, matchup type, and role to produce evaluations that reflect how T20 cricket is actually coached and played.

### How It Compares

| System | Approach | Limitation |
|--------|----------|------------|
| ICC Rankings | Points-per-match decay model | No phase/matchup granularity; all formats weighted |
| CricViz Impact | Ball-by-ball expected value | Proprietary; not reproducible |
| ESPN QBR (NFL analog) | Situation-adjusted composite | Our model for transparency -- QBR publishes weights |
| PFF Grades (NFL analog) | Film-graded per-play evaluation | Our editorial model -- expert + data combined |
| **Cricket Playbook** | **Percentile-composite, phase-aware, matchup-decomposed** | **Requires minimum sample sizes** |

The closest analog in American sports is PFF's grading system crossed with ESPN's QBR: we publish the weights, we show the work, and we let the data speak. This is "pro team internal prep packaged for public consumption."

### Data Foundation at a Glance

- **9,496 matches** across all T20 formats in the database (278,034 IPL-specific balls)
- **2.17 million total ball records** in the fact table
- **18 IPL seasons** (2008--2025) feeding career and phase analytics
- **161+ analytics views** powering every ranking, stat pack, and depth chart
- **DuckDB star schema** with fact_ball, dim_match, dim_player, dim_tournament architecture

---

## The 7 Ranking Categories

Each category follows the same architecture:

1. **Qualify** -- meet minimum ball/match thresholds (from `config/thresholds.yaml`)
2. **Compute** -- calculate raw metrics from upstream analytics views
3. **Percentile** -- convert raw metrics to `PERCENT_RANK()` within the qualified population
4. **Composite** -- weight percentiles into a single score (0--100 scale)
5. **Rank** -- apply `RANK() OVER (ORDER BY composite DESC)`
6. **Dual-scope** -- create both `_alltime` and `_since2023` variants

---

### Category 1: Overall Batter Composite Rankings

**What it measures:** A batter's total value across career performance, phase versatility, boundary-hitting, and discipline -- the single best answer to "who is the best IPL batter?"

**Input views:**
- `analytics_ipl_batting_percentiles` (career stats + percentiles, 36 qualified batters)
- `analytics_ipl_batter_phase_percentiles` (phase-split percentiles, 493 rows across PP/Middle/Death)

**Qualification:** >= 500 career balls faced (from `rankings.qualification.min_balls_batter`)

**Composite formula:**

```
composite_score =
    (career_sr_pctl + career_avg_pctl) / 2   * 0.30    -- Career Performance
  + (phase_sr_pctl + phase_avg_pctl) / 2     * 0.30    -- Phase Versatility
  + career_boundary_pctl                     * 0.20    -- Boundary Hitting
  + career_avg_pctl                          * 0.10    -- Batting Average (survivability)
  + career_dotball_pctl                      * 0.10    -- Dot Ball Discipline
```

| Component | Weight | Metric Source | Rationale |
|-----------|--------|---------------|-----------|
| Career Performance | 30% | SR + Avg percentiles averaged | Baseline: how good are you overall? |
| Phase Versatility | 30% | Average of phase-specific SR + Avg percentiles | T20 demands phase adaptability |
| Boundary Hitting | 20% | Boundary % percentile | Scoring rate accelerator in T20 |
| Batting Average | 10% | Career average percentile | Survivability / consistency measure |
| Dot Ball Discipline | 10% | Dot ball % percentile (inverted -- lower is better) | Strike rotation under pressure |

**Top 10 IPL Batter Composite Rankings:**

| Rank | Player | Inn | Runs | Balls | SR | Avg | Boundary% | Composite |
|------|--------|-----|------|-------|----|-----|-----------|-----------|
| 1 | H Klaasen | 39 | 1,414 | 807 | 175.22 | 45.61 | 22.43% | **86.9** |
| 2 | N Pooran | 43 | 1,381 | 751 | 183.89 | 46.03 | 27.70% | **86.2** |
| 3 | SA Yadav | 43 | 1,667 | 964 | 172.93 | 47.63 | 26.35% | **84.0** |
| 4 | TM Head | 27 | 941 | 520 | 180.96 | 36.19 | 30.96% | **74.9** |
| 5 | SS Iyer | 31 | 955 | 582 | 164.09 | 45.48 | 22.34% | **74.9** |
| 6 | Shubman Gill | 44 | 1,966 | 1,263 | 155.66 | 51.74 | 20.27% | **74.4** |
| 7 | B Sai Sudharsan | 35 | 1,648 | 1,108 | 148.74 | 53.16 | 19.77% | **72.9** |
| 8 | YBK Jaiswal | 43 | 1,619 | 1,009 | 160.46 | 41.51 | 26.46% | **70.1** |
| 9 | PD Salt | 34 | 1,056 | 595 | 177.48 | 34.06 | 29.92% | **69.1** |
| 10 | JC Buttler | 38 | 1,289 | 865 | 149.02 | 40.28 | 20.81% | **65.8** |

**Interpretation:** Klaasen's 86.9 composite means he sits in the ~87th percentile across all weighted dimensions combined. His phase versatility (death + middle dominance) and elite strike rate combine to edge out Pooran's marginally higher raw SR. The gap between the top 3 (84--87 range) and positions 4--10 (65--75 range) reflects how rare it is to be elite in every dimension simultaneously.

---

### Category 2: Overall Bowler Composite Rankings

**What it measures:** A bowler's total value across career economy, phase control, wicket-taking ability, and dot ball pressure -- the single best answer to "who is the best IPL bowler?"

**Input views:**
- `analytics_ipl_bowling_percentiles` (career stats + percentiles, 62 qualified bowlers)
- `analytics_ipl_bowler_phase_percentiles` (phase-split percentiles, 751 rows across PP/Middle/Death)

**Qualification:** >= 300 career balls bowled (from `rankings.qualification.min_balls_bowler`)

**Composite formula:**

```
composite_score =
    (career_econ_pctl + career_avg_pctl) / 2   * 0.30    -- Career Performance
  + (phase_econ_pctl + phase_dotball_pctl) / 2 * 0.30    -- Phase Control
  + career_econ_pctl                           * 0.20    -- Economy Mastery
  + career_sr_pctl                             * 0.10    -- Wicket-Taking Ability
  + career_dotball_pctl                        * 0.10    -- Dot Ball Pressure
```

| Component | Weight | Metric Source | Rationale |
|-----------|--------|---------------|-----------|
| Career Performance | 30% | Economy + Avg percentiles averaged | Baseline: how restrictive and effective? |
| Phase Control | 30% | Average of phase economy + dot ball percentiles | Consistent across PP/Middle/Death |
| Economy Mastery | 20% | Career economy percentile | T20 bowling's primary currency |
| Wicket-Taking | 10% | Bowling strike rate percentile | Breakthroughs change games |
| Dot Ball Pressure | 10% | Dot ball % percentile | Building scoreboard pressure |

**Top 10 IPL Bowler Composite Rankings:**

| Rank | Player | Matches | Balls | Wkts | Econ | Bowl SR | Dot% | Composite |
|------|--------|---------|-------|------|------|---------|------|-----------|
| 1 | JJ Bumrah | 25 | 595 | 38 | 6.69 | 15.66 | 45.21% | **94.7** |
| 2 | CV Varun | 41 | 917 | 58 | 8.15 | 15.81 | 38.17% | **81.9** |
| 3 | JR Hazlewood | 15 | 318 | 25 | 8.77 | 12.72 | 45.91% | **78.8** |
| 4 | M Prasidh Krishna | 15 | 354 | 25 | 8.58 | 14.16 | 38.14% | **78.5** |
| 5 | Noor Ahmad | 37 | 792 | 48 | 8.24 | 16.50 | 34.47% | **78.3** |
| 6 | MM Ali | 20 | 300 | 17 | 8.10 | 17.65 | 31.67% | **77.2** |
| 7 | SP Narine | 40 | 888 | 40 | 7.58 | 22.20 | 32.66% | **76.8** |
| 8 | PP Chawla | 27 | 576 | 35 | 8.45 | 16.46 | 32.12% | **72.4** |
| 9 | M Pathirana | 30 | 661 | 45 | 9.00 | 14.69 | 33.28% | **69.6** |
| 10 | MJ Santner | 19 | 363 | 15 | 7.64 | 24.20 | 33.06% | **66.0** |

**Interpretation:** Bumrah's 94.7 is the single highest composite score in the entire system -- batter or bowler. The 12.8-point gap between Bumrah and #2 Varun Chakravarthy is the largest gap between any #1 and #2 across all seven categories. His 6.69 economy and 45.21% dot ball rate in recent IPL seasons are generationally dominant. Note Narine at #7: his 7.58 economy is excellent, but a 22.20 bowling SR (reflecting fewer wickets per ball) pulls down his wicket-taking component.

---

### Category 3: Batter Phase Rankings (Powerplay / Middle / Death)

**What it measures:** How batters perform within each specific phase of a T20 innings. Three separate leaderboards -- one per phase.

**Input view:** `analytics_ipl_batter_phase_percentiles`

**Qualification:** >= 100 balls faced in the specific phase (from `rankings.qualification.min_balls_phase`)

**Composite formula per phase:**

```
phase_composite = sr_percentile * 0.4 + avg_percentile * 0.4 + boundary_percentile * 0.2
```

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Strike Rate Percentile | 40% | Scoring rate is the primary phase currency |
| Average Percentile | 40% | Survivability determines sustained output |
| Boundary Percentile | 20% | Boundary frequency differentiates good from elite |

**Top 10 -- Powerplay Phase:**

| Rank | Player | Balls | SR | Avg | Boundary% | Phase Composite |
|------|--------|-------|----|-----|-----------|-----------------|
| 1 | C Green | 119 | 164.71 | 49.00 | 28.57% | **93.7** |
| 2 | TM Head | 365 | 184.38 | 44.87 | 33.97% | **92.8** |
| 3 | JM Bairstow | 623 | 151.52 | 49.68 | 25.52% | **91.4** |
| 4 | YBK Jaiswal | 864 | 159.49 | 44.45 | 29.17% | **89.6** |
| 5 | CA Lynn | 537 | 145.07 | 48.69 | 25.33% | **87.9** |
| 6 | SA Yadav | 667 | 140.33 | 58.50 | 23.84% | **87.0** |
| 7 | PD Salt | 409 | 176.53 | 38.00 | 31.30% | **86.5** |
| 8 | RD Rickelton | 193 | 153.89 | 42.43 | 26.42% | **86.1** |
| 9 | Abhishek Sharma | 629 | 161.84 | 36.36 | 27.19% | **82.4** |
| 10 | B Sai Sudharsan | 489 | 137.83 | 112.33 | 20.65% | **82.3** |

**Top 10 -- Middle Overs Phase:**

| Rank | Player | Balls | SR | Avg | Boundary% | Phase Composite |
|------|--------|-------|----|-----|-----------|-----------------|
| 1 | H Klaasen | 526 | 159.32 | 59.86 | 18.63% | **95.7** |
| 2 | DP Conway | 341 | 152.79 | 65.13 | 19.35% | **95.4** |
| 3 | N Pooran | 764 | 167.02 | 44.00 | 23.30% | **94.1** |
| 4 | CH Gayle | 1,285 | 156.50 | 44.69 | 20.70% | **93.2** |
| 4 | SE Marsh | 971 | 149.12 | 51.71 | 19.57% | **93.2** |
| 6 | SE Rutherford | 144 | 136.11 | 98.00 | 17.36% | **86.9** |
| 7 | JC Buttler | 1,180 | 144.41 | 43.69 | 17.71% | **86.8** |
| 8 | RM Patidar | 480 | 162.50 | 37.14 | 19.17% | **86.7** |
| 9 | B Sai Sudharsan | 620 | 143.06 | 46.68 | 16.29% | **86.3** |
| 9 | N Wadhera | 380 | 140.26 | 44.42 | 18.95% | **86.3** |

**Top 10 -- Death Overs Phase:**

| Rank | Player | Balls | SR | Avg | Boundary% | Phase Composite |
|------|--------|-------|----|-----|-----------|-----------------|
| 1 | AB de Villiers | 829 | 225.33 | 46.70 | 33.17% | **99.2** |
| 2 | T Stubbs | 199 | 220.60 | 87.80 | 32.66% | **99.0** |
| 3 | CH Gayle | 280 | 207.50 | 38.73 | 31.79% | **97.3** |
| 4 | C Green | 102 | 200.00 | 102.00 | 27.45% | **95.7** |
| 5 | Naman Dhir | 121 | 204.13 | 30.88 | 31.40% | **93.1** |
| 6 | Shashank Singh | 219 | 193.61 | 42.40 | 26.48% | **93.0** |
| 7 | JC Buttler | 368 | 198.10 | 33.14 | 27.72% | **91.7** |
| 8 | MEK Hussey | 136 | 191.91 | 37.29 | 27.21% | **91.6** |
| 9 | LS Livingstone | 151 | 227.81 | 26.46 | 34.44% | **90.0** |
| 10 | H Klaasen | 277 | 199.64 | 29.11 | 27.44% | **89.0** |

**Interpretation:** The death overs leaderboard shows the most extreme separation. AB de Villiers' 99.2 composite (225.33 SR, 33.17% boundary rate at death) is functionally a perfect score. Klaasen dominates the middle overs (95.7, rank #1) and appears at death (#10), validating his overall #1 batter composite. The powerplay leaderboard shows more parity, with the 93.7--82.3 range reflecting the relative predictability of fielding restrictions.

---

### Category 4: Bowler Phase Rankings (Powerplay / Middle / Death)

**What it measures:** How bowlers perform within each specific phase of a T20 innings.

**Input view:** `analytics_ipl_bowler_phase_percentiles`

**Qualification:** Phase-specific minimum overs (from `thresholds.yaml`): PP >= 30 overs, Middle >= 50 overs, Death >= 30 overs

**Composite formula per phase:**

```
phase_composite = economy_percentile * 0.5 + dot_ball_percentile * 0.5
```

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Economy Percentile | 50% | Run prevention is the primary bowling currency |
| Dot Ball Percentile | 50% | Pressure building through scoreless deliveries |

**Top 10 -- Powerplay Phase:**

| Rank | Player | Balls | Econ | Dot% | Phase Composite |
|------|--------|-------|------|------|-----------------|
| 1 | AG Murtaza | 78 | 4.00 | 60.26% | **99.8** |
| 1 | FH Edwards | 78 | 4.69 | 64.10% | **99.8** |
| 3 | A Kumble | 108 | 5.00 | 59.26% | **99.2** |
| 4 | R Rampaul | 156 | 5.85 | 58.33% | **97.9** |
| 5 | GD McGrath | 222 | 5.89 | 57.21% | **97.3** |
| 6 | A Symonds | 114 | 5.79 | 54.39% | **95.1** |
| 7 | WPUJC Vaas | 198 | 6.39 | 57.07% | **94.3** |
| 8 | Sohail Tanvir | 132 | 6.59 | 57.58% | **94.1** |
| 9 | BW Hilfenhaus | 240 | 6.50 | 55.42% | **93.3** |
| 10 | DW Steyn | 1,134 | 6.42 | 55.03% | **92.8** |

**Top 10 -- Middle Overs Phase:**

| Rank | Player | Balls | Econ | Dot% | Phase Composite |
|------|--------|-------|------|------|-----------------|
| 1 | MM Patel | 396 | 6.17 | 39.39% | **97.6** |
| 1 | B Lee | 78 | 6.23 | 39.74% | **97.6** |
| 3 | SB Styris | 108 | 6.56 | 40.74% | **96.9** |
| 4 | Azhar Mahmood | 186 | 6.61 | 40.86% | **96.6** |
| 5 | DW Steyn | 408 | 6.75 | 43.38% | **96.1** |
| 6 | Shivam Mavi | 162 | 6.85 | 43.83% | **95.6** |
| 7 | CRD Fernando | 72 | 7.00 | 50.00% | **95.5** |
| 8 | JJ Bumrah | 870 | 6.66 | 39.66% | **95.4** |
| 9 | J Yadav | 210 | 6.29 | 38.10% | **94.8** |
| 10 | NM Coulter-Nile | 249 | 6.89 | 40.96% | **94.3** |

**Top 10 -- Death Overs Phase:**

| Rank | Player | Balls | Econ | Dot% | Phase Composite |
|------|--------|-------|------|------|-----------------|
| 1 | VY Mahesh | 63 | 7.71 | 46.03% | **99.3** |
| 2 | DE Bollinger | 234 | 7.62 | 37.61% | **98.3** |
| 3 | Sohail Tanvir | 103 | 7.11 | 36.89% | **97.8** |
| 4 | GB Hogg | 92 | 7.89 | 39.13% | **97.5** |
| 5 | SP Narine | 1,051 | 7.50 | 36.44% | **97.2** |
| 6 | M Muralitharan | 275 | 8.29 | 37.45% | **95.2** |
| 7 | A Kumble | 167 | 7.80 | 34.73% | **95.0** |
| 8 | Noor Ahmad | 127 | 8.41 | 42.52% | **94.7** |
| 9 | Harmeet Singh | 129 | 8.28 | 35.66% | **93.9** |
| 10 | PWH de Silva | 120 | 8.50 | 37.50% | **93.0** |

**Interpretation:** The alltime bowler phase data reveals fascinating era effects. Early-IPL bowlers (McGrath, Steyn, Edwards) dominate powerplay rankings due to a less aggressive batting meta in 2008--2012. Narine's death overs ranking (#5, 7.50 economy across 1,051 balls) is perhaps the single most impressive line in the data given sample size. Bumrah's middle overs presence (#8, 6.66 economy across 870 balls) adds context to his overall #1 composite.

---

### Category 5: Batter vs Bowling Type Rankings

**What it measures:** How batters perform against specific bowling types (Pace, Spin, and their sub-classifications). Thirteen distinct bowler types are tracked.

**Input view:** `analytics_ipl_batter_vs_bowler_type` (5,042 batter-type combinations)

**Qualification:** >= 50 balls faced against the specific bowling type (from `rankings.qualification.min_balls_vs_type`)

**Bowler types tracked:**

| Category | Types |
|----------|-------|
| Pace | Fast, Fast-Medium, Left-arm pace, Right-arm pace, Medium |
| Spin | Off-spin, Leg-spin, Left-arm orthodox, Right-arm leg-spin, Right-arm off-spin, Wrist-spin, LA Orthodox |
| Other | Unknown |

**Composite formula:**

```
vs_type_composite = sr_percentile * 0.4 + avg_percentile * 0.4 + survival_percentile * 0.2
```

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Strike Rate Percentile | 40% | Scoring ability vs the specific type |
| Average Percentile | 40% | Survival and consistency vs the type |
| Survival Percentile | 20% | Dismissal rate (lower dismissal rate = higher percentile) |

**Sample Top 10 -- vs Fast Bowling:**

| Rank | Player | Balls | SR | Avg | Composite |
|------|--------|-------|----|-----|-----------|
| 1 | JP Inglis | 81 | 195.06 | 158.00 | **98.7** |
| 2 | Atharva Taide | 57 | 182.46 | 104.00 | **97.3** |

**Sample Top 10 -- vs Off-spin:**

| Rank | Player | Balls | SR | Avg | Composite |
|------|--------|-------|----|-----|-----------|
| 1 | H Klaasen | 88 | 181.82 | 160.00 | **96.9** |
| 2 | YBK Jaiswal | 66 | 189.39 | 125.00 | **94.1** |

**Sample Top 10 -- vs Leg-spin:**

| Rank | Player | Balls | SR | Avg | Composite |
|------|--------|-------|----|-----|-----------|
| 1 | A Raghuvanshi | 67 | 167.16 | 112.00 | **95.6** |
| 2 | Nithish Kumar Reddy | 57 | 157.89 | 90.00 | **92.2** |

**Interpretation:** This is where the system reveals actionable scouting intelligence. Klaasen's 96.9 composite vs off-spin (181.82 SR, 160.00 avg across 88 balls) is a concrete matchup signal: do not bowl off-spin to this player. Conversely, a team can cross-reference a batter's low composite vs wrist-spin (say, V Kohli at 65.0 vs wrist-spin) against the death-specialist wrist spinners in a rival squad to identify tactical pressure points.

---

### Category 6: Bowler vs Handedness Rankings

**What it measures:** How bowlers perform against left-handed vs right-handed batters.

**Input view:** `analytics_ipl_bowler_vs_batter_handedness` (395 bowler-hand combinations)

**Qualification:** >= 50 balls bowled against the specific handedness

**Composite formula:**

```
vs_hand_composite = economy_percentile * 0.5 + sr_percentile * 0.5
```

Note: Percentiles are ordered `DESC` for both economy and SR -- lower economy and lower bowling SR (more wickets per ball) yield higher percentiles. This reflects the bowling perspective where lower numbers are better.

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Economy Percentile | 50% | Run restriction against the handedness |
| Bowling SR Percentile | 50% | Wicket-taking frequency against the handedness |

**Top 10 -- vs Left-Hand Batters (93 qualified bowlers):**

| Rank | Player | Balls | Wkts | Econ | Bowl SR | Composite |
|------|--------|-------|------|------|---------|-----------|
| 1 | M Prasidh Krishna | 107 | 9 | 6.84 | 11.89 | **96.2** |
| 1 | JJ Bumrah | 210 | 17 | 5.94 | 12.35 | **96.2** |
| 3 | Noor Ahmad | 219 | 18 | 7.89 | 12.17 | **92.4** |
| 4 | R Parag | 56 | 0 | 8.79 | -- | **87.5** |
| 4 | RD Chahar | 127 | 8 | 6.94 | 15.88 | **87.5** |
| 6 | M Pathirana | 213 | 21 | 8.99 | 10.14 | **81.5** |
| 7 | VG Arora | 167 | 13 | 8.95 | 12.85 | **78.3** |
| 7 | Rashid Khan | 317 | 19 | 8.27 | 16.68 | **78.3** |
| 7 | DL Chahar | 184 | 11 | 8.25 | 16.73 | **78.3** |
| 10 | JR Hazlewood | 104 | 11 | 9.29 | 9.45 | **77.2** |

**Top 10 -- vs Right-Hand Batters (110 qualified bowlers):**

| Rank | Player | Balls | Wkts | Econ | Bowl SR | Composite |
|------|--------|-------|------|------|---------|-----------|
| 1 | GJ Maxwell | 69 | 6 | 8.09 | 11.50 | **93.1** |
| 2 | Akash Singh | 73 | 5 | 7.81 | 14.60 | **89.9** |
| 3 | TA Boult | 388 | 28 | 8.46 | 13.86 | **87.2** |
| 4 | PP Chawla | 233 | 16 | 8.65 | 14.56 | **84.4** |
| 5 | JJ Bumrah | 305 | 18 | 7.18 | 16.94 | **83.5** |
| 6 | E Malinga | 123 | 11 | 9.17 | 11.18 | **82.6** |
| 7 | M Prasidh Krishna | 218 | 16 | 9.03 | 13.63 | **81.2** |
| 8 | CV Varun | 498 | 30 | 7.86 | 16.60 | **80.7** |
| 9 | M Siddharth | 52 | 3 | 7.38 | 17.33 | **80.3** |
| 10 | M Markande | 159 | 10 | 8.79 | 15.90 | **78.0** |

**Interpretation:** Bumrah appears in both top-2 lists (vs Left #1 tied, vs Right #5), reinforcing his overall dominance. The practical application: if your franchise has Bumrah, you do not need to worry about the opponent's batting handedness mix. Boult at #3 vs right-handers (388 balls, 28 wickets, 8.46 economy) combined with his known swing angle makes him a targeted weapon against right-hand-heavy lineups.

---

### Category 7: Player Matchup Rankings (Dominance Index)

**What it measures:** Head-to-head batter vs bowler dominance in specific matchups. Unlike the other six categories, this produces a **signed** index: positive values indicate batter-favored matchups, negative values indicate bowler-favored matchups.

**Input view:** `analytics_ipl_player_matchup_matrix` (1,155 qualified matchup pairs)

**Qualification:** >= 12 balls in the specific batter-bowler matchup

**Dominance Index formula:**

```
dominance_index =
    (strike_rate - 130)  * 0.5     -- SR deviation from T20 par (130)
  + (average - 25)       * 0.3     -- Avg deviation from T20 par (25)
  + (boundary_pct - 15)  * 0.2     -- Boundary% deviation from T20 par (15%)
```

| Component | Weight | Baseline | Rationale |
|-----------|--------|----------|-----------|
| SR Deviation | 50% | 130 (T20 par SR) | Primary scoring measure |
| Average Deviation | 30% | 25 (T20 par avg) | Batter survival in the matchup |
| Boundary% Deviation | 20% | 15% (T20 par boundary rate) | Explosive scoring potential |

The baselines (130 SR, 25 avg, 15% boundaries) represent approximate T20 population averages, meaning a dominance index of 0 indicates a perfectly neutral matchup.

**Top 10 Batter-Favored Matchups:**

| Batter | Bowler | Balls | Runs | Dis | SR | Avg | Dominance |
|--------|--------|-------|------|-----|-----|-----|-----------|
| TH David | Mukesh Kumar | 13 | 46 | 1 | 353.85 | 46.00 | **+129.07** |
| RM Patidar | M Markande | 14 | 43 | 1 | 307.14 | 43.00 | **+99.54** |
| VR Iyer | Yash Dayal | 13 | 37 | 1 | 284.62 | 37.00 | **+88.68** |
| Abhishek Sharma | Kuldeep Yadav | 13 | 38 | 2 | 292.31 | 19.00 | **+85.58** |
| SA Yadav | M Jansen | 18 | 45 | 1 | 250.00 | 45.00 | **+71.89** |
| TM Head | Avesh Khan | 18 | 44 | 1 | 244.44 | 44.00 | **+68.81** |
| N Pooran | A Kamboj | 13 | 32 | 1 | 246.15 | 32.00 | **+66.41** |
| SA Yadav | SM Curran | 23 | 54 | 1 | 234.78 | 54.00 | **+65.92** |
| DA Miller | Mukesh Kumar | 14 | 34 | 1 | 242.86 | 34.00 | **+64.70** |
| VR Iyer | T Natarajan | 12 | 29 | 1 | 241.67 | 29.00 | **+64.03** |

**Top 10 Bowler-Favored Matchups:**

| Batter | Bowler | Balls | Runs | Dis | SR | Avg | Dominance |
|--------|--------|-------|------|-----|-----|-----|-----------|
| RG Sharma | CV Varun | 14 | 5 | 1 | 35.71 | 5.00 | **-56.14** |
| JM Sharma | M Jansen | 13 | 5 | 1 | 38.46 | 5.00 | **-53.23** |
| Abhishek Sharma | VG Arora | 12 | 6 | 1 | 50.00 | 6.00 | **-48.70** |
| AR Patel | CV Varun | 24 | 12 | 1 | 50.00 | 12.00 | **-46.07** |
| A Badoni | TA Boult | 12 | 7 | 2 | 58.33 | 3.50 | **-45.28** |
| AK Markram | Kuldeep Yadav | 12 | 7 | 1 | 58.33 | 7.00 | **-44.23** |
| AK Markram | JJ Bumrah | 12 | 7 | 1 | 58.33 | 7.00 | **-44.23** |
| Nithish Kumar Reddy | MA Starc | 12 | 7 | 2 | 58.33 | 3.50 | **-43.62** |
| T Stubbs | JJ Bumrah | 13 | 8 | 1 | 61.54 | 8.00 | **-42.33** |
| RA Tripathi | Ravi Bishnoi | 13 | 8 | 1 | 61.54 | 8.00 | **-42.33** |

**Interpretation:** This is the "film room" category -- direct head-to-head intelligence. CV Varun owns Rohit Sharma (-56.14; 14 balls, 5 runs, 35.71 SR). Suryakumar Yadav dominates Marco Jansen (+71.89; 18 balls, 45 runs, 250 SR). These matchups feed directly into predicted XI selection and tactical bowling order decisions in the stat packs. Note the minimum 12-ball qualification: small samples are flagged but still informative for tournament preparation.

---

## Composite Weight Rationale

### Design Philosophy

The weights were calibrated through three lenses:

1. **Statistical analysis** (Stephen Curry): Correlation testing of individual metrics against match-winning contributions. Career SR and phase versatility showed the highest explanatory power for batters; economy and phase consistency for bowlers.

2. **Cricket domain expertise** (Andy Flower): Phase performance must be co-equal with career numbers. A batter who averages 35 overall but 55 in the death overs is categorically more valuable than one who averages 40 overall with 20 at death. The 30/30 career-phase split reflects this.

3. **Analytical precedent** (PFF/QBR model): Composite systems in the NFL and NBA typically weight "primary skill" at 50--60% and "secondary dimensions" at 40--50%. Our 60% primary (career + phase) vs 40% secondary (boundary + avg + discipline) follows this pattern.

### Batter Weight Justification

| Weight | Component | Why This Number |
|--------|-----------|-----------------|
| 30% Career | Career SR + Avg | Floor: no batter should rank highly without strong career numbers |
| 30% Phase | Phase-averaged SR + Avg | T20's defining characteristic: phase specialization matters as much as career totals |
| 20% Boundaries | Boundary % | Boundary rate separates T20 specialists from accumulator-style batters |
| 10% Average | Career batting avg | Survivability tiebreaker -- rewards batters who are hard to dismiss |
| 10% Dot Balls | Dot ball % discipline | Strike rotation under pressure -- punishes ball-hoggers |

### Bowler Weight Justification

| Weight | Component | Why This Number |
|--------|-----------|-----------------|
| 30% Career | Economy + Avg | Floor: no bowler should rank highly without strong career economy |
| 30% Phase | Phase economy + dot ball avg | Multi-phase consistency is the hallmark of elite T20 bowlers |
| 20% Economy | Career economy | Run prevention is the single most valuable bowling metric in T20 |
| 10% Wicket-Taking | Bowling SR | Breakthroughs change the game; SR captures wicket-taking frequency |
| 10% Dot Balls | Dot ball % | Scoreboard pressure and partnership disruption |

### Why Not Equal Weights?

Equal weighting (14.3% each for 7 components) would mathematically dilute phase performance, which our domain analysis shows is the single most predictive dimension of T20 value. The 30/30/20/10/10 structure creates a clear hierarchy: career baseline, phase specialization, primary differentiator, and two secondary tiebreakers.

---

## Qualification & Small Sample Handling

### Minimum Thresholds

All thresholds are defined in `config/thresholds.yaml` as the single source of truth:

| Category | Threshold | Value | Rationale |
|----------|-----------|-------|-----------|
| Batter Composite | Career balls faced | >= 500 | ~30 innings minimum at ~17 balls/innings |
| Bowler Composite | Career balls bowled | >= 300 | ~50 overs, approximately 12--15 matches |
| Batter Phase | Phase-specific balls | >= 100 | Approximately 6--8 phase-innings worth of data |
| Batter vs Type | Balls vs bowling type | >= 50 | ~3 meaningful matchup innings |
| Bowler vs Hand | Balls vs handedness | >= 50 | ~8 overs against the specific hand |
| Player Matchup | Head-to-head balls | >= 12 | 2 overs of direct confrontation |

### Population Sizes After Qualification

| View | Qualified Players/Rows |
|------|----------------------|
| Batter Composite | 36 batters |
| Bowler Composite | 62 bowlers |
| Batter Phase Percentiles | 493 player-phase combinations |
| Bowler Phase Percentiles | 751 player-phase combinations |
| Batter vs Bowling Type | 5,042 batter-type combinations |
| Bowler vs Handedness | 395 bowler-hand combinations |
| Player Matchups | 1,155 head-to-head pairs |

### Dual-Scope Architecture (Alltime vs Since 2023)

Every ranking view exists in three forms:

| Scope | Suffix | Purpose |
|-------|--------|---------|
| Base | (none) | Default computation (typically alltime) |
| Alltime | `_alltime` | Full IPL history (2008--2025), 18 seasons |
| Since 2023 | `_since2023` | Recent form window (IPL 2023--2025), 3 seasons |

**Why two scopes?**

1. **Alltime** captures the full body of work -- essential for career composites and historical context
2. **Since 2023** captures current form and contemporary bowling conditions -- essential for pre-tournament predictions where the question is "who is good *right now*?"

The since-2023 scope uses a date filter (`match_date >= '2023-01-01'`) applied at the CTE level, re-computing all aggregates from raw ball data. It is not a subset of the alltime view; it is an independent calculation.

### COALESCE for Cross-Scope Enrichment

In the composite rankings, the SQL uses `COALESCE(phase_percentile, career_percentile)` to handle players who qualify for career rankings but lack phase-specific data. This prevents penalizing batters/bowlers who have strong career numbers but limited phase-level ball counts. The fallback to career percentile is a conservative estimate -- it assumes "if we do not have phase data, your phase performance is approximately your career performance."

### Sample Size Flags

The upstream percentile views tag every row with a `sample_size` classification:

| Flag | Balls | Interpretation |
|------|-------|----------------|
| LOW | < 100 | Directional only; treat with caution |
| MEDIUM | 100--499 | Usable for analysis with caveats |
| HIGH | >= 500 | Full statistical confidence |

---

## Data Foundation

### Database Architecture

```
Cricsheet ZIP files
    |
    v
ingest.py (Brock Purdy)
    |
    v
DuckDB Star Schema (159 MB)
    |-- fact_ball (2,166,065 rows)
    |-- dim_match (9,496 matches)
    |-- dim_player
    |-- dim_tournament
    |-- dim_bowler_classification
    |-- ipl_2026_squads
    |
    v
analytics_ipl.py (Stephen Curry)
    |-- 161+ analytics views
    |-- 7 ranking categories x 3 scopes = 21 ranking views
    |-- Benchmark views for IPL-wide averages
    |
    v
Stat Packs / Depth Charts / Predicted XIs / The Lab
```

### IPL Data Coverage

| Metric | Value |
|--------|-------|
| Total matches (all T20) | 9,496 |
| Total ball records | 2,166,065 |
| IPL-specific balls | 278,034 |
| IPL seasons covered | 18 (2008--2025) |
| IPL matches per season | 57--76 |
| Analytics views | 161+ |
| Ranking views | 21 (7 categories x 3 scopes) |

### IPL Career Benchmarks (Qualified Population)

These are the population averages against which all percentiles are calculated:

| Metric | Batting (36 qualified) | Bowling (62 qualified) |
|--------|----------------------|----------------------|
| Avg Strike Rate | 152.98 | -- |
| Median Strike Rate | 150.44 | -- |
| Avg Batting Average | 36.76 | -- |
| Median Batting Average | 35.41 | -- |
| Avg Boundary% | 21.36% | -- |
| Avg Dot Ball% | 33.10% | -- |
| Avg Economy | -- | 9.22 |
| Median Economy | -- | 9.26 |
| Avg Bowling Average | -- | 30.04 |
| Median Bowling Average | -- | 29.81 |
| Avg Dot Ball% | -- | 33.54% |
| Avg Boundary Conceded% | -- | 20.06% |

### Percentile Methodology

All percentiles use SQL `PERCENT_RANK()`, which produces a value between 0 and 1 (scaled to 0--100):

```sql
PERCENT_RANK() OVER (PARTITION BY dimension ORDER BY metric) * 100
```

`PERCENT_RANK()` returns `(rank - 1) / (total_rows - 1)`, meaning:
- The lowest value gets 0.0
- The highest value gets 100.0
- Each player's score represents the percentage of qualified players they outperform

This is mathematically identical to how the NFL's PFF grades work: a "90th percentile" player is better than 90% of qualified players at that specific metric.

---

## Glossary

| Term | Definition |
|------|------------|
| **Composite Score** | A weighted sum of multiple percentile-based metrics, producing a single 0--100 value that represents a player's overall ranking within a category |
| **Percentile** | A player's rank expressed as a percentage of the qualified population they outperform. A 90th-percentile strike rate means 90% of qualified players have a lower strike rate |
| **Dual-Scope** | The practice of computing every ranking in both `_alltime` (full IPL history) and `_since2023` (recent 3-season window) variants |
| **Phase** | One of three T20 innings segments: Powerplay (overs 1--6), Middle (overs 7--15), Death (overs 16--20) |
| **Dominance Index** | A signed metric for head-to-head matchups. Positive = batter-favored, negative = bowler-favored. Zero = neutral matchup |
| **Qualification Threshold** | The minimum number of balls (or overs/innings) a player must have to be included in a ranking. Prevents small-sample noise from distorting rankings |
| **PERCENT_RANK()** | SQL window function that returns `(rank - 1) / (n - 1)` where n is the partition size. Ranges from 0 (worst) to 1 (best) |
| **COALESCE Fallback** | When a player qualifies for career rankings but lacks phase-specific data, their career percentile is used as a proxy for missing phase percentiles |
| **Boundary%** | Percentage of legal balls faced that were hit for 4 or 6 |
| **Dot Ball%** | Percentage of legal balls where the batter scored zero runs (batting) or where zero runs were conceded (bowling) |
| **Bowling Strike Rate** | Balls bowled per wicket taken. Lower is better (more frequent wickets) |
| **Economy Rate** | Runs conceded per over (6 balls). The primary measure of bowling restrictiveness in T20 |
| **Sample Size Flag** | LOW (< 100 balls), MEDIUM (100--499), HIGH (>= 500). Applied to upstream views to signal data confidence |
| **Star Schema** | Database design with a central fact table (fact_ball) linked to dimension tables (dim_match, dim_player, etc.) |
| **Upstream View** | An analytics view that feeds data into ranking views. Rankings never query fact_ball directly; they build on pre-computed analytics layers |

---

## Appendix: View Dependency Map

```
fact_ball + dim_* tables
    |
    +-- analytics_ipl_batting_career -----> analytics_ipl_batting_percentiles
    |                                            |
    |                                            +-----> [Cat 6] Batter Composite Rankings
    |                                            |
    +-- analytics_ipl_batter_phase -------> analytics_ipl_batter_phase_percentiles
    |                                            |
    |                                            +-----> [Cat 3] Batter Phase Rankings
    |                                            +-----> [Cat 6] Batter Composite (phase avg)
    |
    +-- analytics_ipl_batter_vs_bowler_type ----------> [Cat 5] Batter vs Bowling Type Rankings
    |
    +-- analytics_ipl_bowling_career -----> analytics_ipl_bowling_percentiles
    |                                            |
    |                                            +-----> [Cat 7] Bowler Composite Rankings
    |                                            |
    +-- analytics_ipl_bowler_phase -------> analytics_ipl_bowler_phase_percentiles
    |                                            |
    |                                            +-----> [Cat 4] Bowler Phase Rankings
    |                                            +-----> [Cat 7] Bowler Composite (phase avg)
    |
    +-- analytics_ipl_bowler_vs_batter_handedness ----> [Cat 6] Bowler vs Handedness Rankings
    |
    +-- analytics_ipl_player_matchup_matrix ----------> [Cat 5] Player Matchup Rankings
```

---

*Cricket Playbook v5.0.0 | Rankings Module TKT-235 (EPIC-021)*
*Data current through IPL 2025 (match date: 2025-06-03)*
*Generated: 2026-02-14*
