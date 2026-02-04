# Baselines vs Tags: Understanding the Difference

**Author:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-02
**Version:** 1.0

---

## Overview

This document clarifies the distinction between **baselines** and **tags** in Cricket Playbook, two concepts that serve different purposes in our analytics framework.

---

## Baselines

**Definition:** Baselines are league-wide statistical benchmarks that represent average or expected performance levels.

**Purpose:** To provide context for individual player performance by comparing against league norms.

### Key Baselines

| Metric | IPL Baseline (2023-2025) | "Good" Threshold |
|--------|--------------------------|------------------|
| Batting Strike Rate | 135.0 | > 140 |
| Batting Average | 28.5 | > 30 |
| Bowling Economy | 8.5 | < 8.0 |
| Bowling Strike Rate | 18.0 | < 20 |
| Dot Ball % (Batting) | 35% | < 30% |
| Dot Ball % (Bowling) | 38% | > 40% |
| Boundary % | 14% | > 15% |

### Phase-Specific Baselines

| Phase | Expected SR | Expected Economy |
|-------|-------------|------------------|
| Powerplay (1-6) | 135 | 8.0 |
| Middle (7-15) | 125 | 7.5 |
| Death (16-20) | 155 | 10.5 |

### Usage
- Compare individual performance to baseline
- Calculate "above/below average" metrics
- Normalize cross-phase comparisons

---

## Tags

**Definition:** Tags are categorical labels assigned to players based on meeting specific criteria thresholds.

**Purpose:** To classify players into actionable categories for team selection, matchup analysis, and editorial storytelling.

### Tag Types

#### 1. Role Tags (Archetypes)
Describe a player's primary function:

**Batters:** EXPLOSIVE_OPENER, PLAYMAKER, ANCHOR, ACCUMULATOR, MIDDLE_ORDER, FINISHER

**Bowlers:** PACER, SPINNER, WORKHORSE, NEW_BALL_SPECIALIST, MIDDLE_OVERS_CONTROLLER, DEATH_SPECIALIST, PART_TIMER

#### 2. Matchup Tags
Describe performance vs specific bowling/batting types:

| Tag | Criteria (ALL required) |
|-----|-------------------------|
| SPECIALIST_VS_PACE | SR ≥ 130, Avg ≥ 25, BPD ≥ 20 vs pace |
| SPECIALIST_VS_SPIN | SR ≥ 130, Avg ≥ 25, BPD ≥ 20 vs spin |
| VULNERABLE_VS_PACE | SR < 105 OR Avg < 15 OR BPD < 15 vs pace |
| VULNERABLE_VS_SPIN | SR < 105 OR Avg < 15 OR BPD < 15 vs spin |

#### 3. Phase Tags
Describe exceptional phase-specific performance:

| Tag | Economy Threshold | Min Overs |
|-----|-------------------|-----------|
| PP_BEAST | < 7.0 | 30 |
| PP_LIABILITY | > 9.5 | 30 |
| DEATH_BEAST | < 9.0 | 30 |
| DEATH_LIABILITY | > 12.0 AND SR > 18.0 | 30 |

### Usage
- Quick player identification for specific roles
- Matchup-based team selection
- Editorial narratives ("pace specialists", "death bowlers")

---

## Key Differences

| Aspect | Baselines | Tags |
|--------|-----------|------|
| **Type** | Continuous numbers | Categorical labels |
| **Purpose** | Context/comparison | Classification/action |
| **Updates** | Recalculated each season | Applied based on thresholds |
| **Granularity** | Fine-grained metrics | Broad categories |
| **Example** | "SR 145 vs baseline 135" | "EXPLOSIVE_OPENER" |

---

## When to Use Which

### Use Baselines When:
- Comparing player performance to league average
- Calculating adjusted metrics (AdjSR, AdjEcon)
- Normalizing cross-phase comparisons
- Building quantitative models

### Use Tags When:
- Making team selection decisions
- Identifying matchup advantages
- Writing editorial content
- Quick player categorization

---

## Example: Virat Kohli Analysis

**Using Baselines:**
```
Overall SR: 152.3 (baseline: 135.0) → +12.8% above average
vs Spin SR: 148.5 (baseline: 130.0) → +14.2% above average
Death SR: 165.2 (baseline: 155.0) → +6.6% above average
```

**Using Tags:**
```
Role: ANCHOR
Matchup: SPECIALIST_VS_SPIN
Phase: (none - doesn't meet PP_BEAST/DEATH_BEAST thresholds)
```

**Combined Insight:**
"Kohli is an ANCHOR who performs 12.8% above baseline, with particular strength against spin (+14.2%). While not tagged as a phase specialist, his death-over numbers (+6.6%) are solid."

---

## Relationship to Outputs

| Output File | Uses Baselines | Uses Tags |
|-------------|----------------|-----------|
| `player_tags.json` | Thresholds derived from | Primary output |
| `batter_bowling_type_matchup.csv` | Context for interpretation | Tag assignment |
| `predicted_xii.json` | Score normalization | Role selection |
| `depth_charts.json` | Rating calculation | Position classification |
| `stat_packs/*.md` | "Above/below average" text | Player descriptions |

---

## Maintenance

**Baselines:** Should be recalculated at the start of each IPL season using the most recent 3 years of data.

**Tags:** Thresholds should be reviewed annually with Andy Flower to ensure cricket relevance. Tag assignments are recalculated whenever underlying data changes.

---

## Appendix A: Comprehensive Role Tag Definitions (P1-08)

This section provides detailed definitions for all 25 role tags used in Cricket Playbook, including specific thresholds and cricket context.

### A.1 Batter Role Tags (15 Tags)

#### EXPLOSIVE_OPENER
**Definition:** Top-order batter who attacks from ball one, setting aggressive tone for the innings.

**Criteria:**
- Overall Strike Rate ≥ 155
- Powerplay Strike Rate ≥ 160
- Boundary % ≥ 22%
- Typical batting position: 1-2

**Cricket Context:** These batters put pressure on opposition bowlers immediately. Examples: Jos Buttler, Jonny Bairstow. Teams need at least one explosive opener to capitalize on powerplay fielding restrictions.

---

#### PP_DOMINATOR
**Definition:** Elite powerplay performer who excels across multiple attacking metrics during overs 1-6.

**Criteria:**
- Must be in top 25% across at least 3 of:
  - Powerplay Strike Rate (≥ 150)
  - Powerplay Boundary % (≥ 25%)
  - Powerplay Balls per Dismissal (≥ 20)
  - Powerplay Average (≥ 35)
- Minimum 100 powerplay balls faced

**Cricket Context:** Rare and valuable. PP_DOMINATOR is a superset - players tagged EXPLOSIVE_OPENER may also be PP_DOMINATOR if they meet consistency thresholds.

---

#### PLAYMAKER
**Definition:** Versatile top-order batter who adapts approach based on match situation.

**Criteria:**
- Strike Rate: 135-155 (aggressive but controlled)
- Average ≥ 35
- Low variance across phases (performs in PP, middle, death)
- Typical batting position: 2-4

**Cricket Context:** The glue of an innings. Can anchor when wickets fall or accelerate when set. Examples: Virat Kohli, Kane Williamson (pre-2023). Essential for chasing targets or building totals.

---

#### ANCHOR
**Definition:** Stability-first batter who prioritizes occupation over acceleration.

**Criteria:**
- Strike Rate < 125
- Average ≥ 28
- Dot Ball % ≥ 35%
- Low dismissal rate in middle overs

**Cricket Context:** Can be valuable or liability depending on team composition. Need FINISHERS around them. If team lacks finishing power, ANCHOR becomes a problem. Use sparingly - max 1 per XI.

---

#### ACCUMULATOR
**Definition:** Middle-order batter who rotates strike efficiently rather than boundary hitting.

**Criteria:**
- Typical batting position: 4-6
- Strike Rate: 120-140
- Powerplay Workload < 15% (rarely faces new ball)
- Singles % ≥ 45%

**Cricket Context:** Bridge between builders and finishers. Keep scoreboard ticking but won't win you games alone. Useful when partnered with explosive batters at either end.

---

#### MIDDLE_ORDER
**Definition:** Generic middle-order batter without distinctive specialist characteristics.

**Criteria:**
- Average batting position: 4.0-6.0
- Does not qualify for ANCHOR, ACCUMULATOR, or FINISHER tags
- Moderate metrics across all dimensions

**Cricket Context:** Flexible option. Can bat in various positions. May be developing players or consistent performers without extreme strengths/weaknesses.

---

#### FINISHER
**Definition:** Death overs specialist who accelerates scoring in final 5 overs.

**Criteria:**
- Death Strike Rate ≥ 170
- Death Boundary % ≥ 22%
- Typical batting position: 5+
- Has faced 50+ death over balls

**Cricket Context:** Game-changers. Can add 40-50 runs in final 3 overs. Examples: MS Dhoni (prime), Dinesh Karthik. Essential for competitive totals. Every squad needs 2-3 options.

---

#### DEATH_SPECIALIST
**Definition:** Elite death-over performer exceeding FINISHER thresholds significantly.

**Criteria:**
- Death Strike Rate ≥ 192 (top 10%)
- Elite in at least 3 of:
  - Death Boundary %
  - Death Average
  - Death Balls per Dismissal
  - Death Six %

**Cricket Context:** Rare. Pure match-winners in final overs. Should bat no higher than 5-6. Examples: Andre Russell, Glenn Maxwell (at peak). Worth building XI around.

---

#### SIX_HITTER
**Definition:** Batter with exceptional ability to clear the boundary.

**Criteria:**
- Six % ≥ 7% (6+ sixes per 100 balls)
- Overall Boundary % ≥ 20%
- Has scored 500+ T20 runs (sample size)

**Cricket Context:** Valuable at all phases but especially death overs. Ground size matters - may perform better at smaller venues. Matchup against spin bowlers often determines effectiveness.

---

#### MIDDLE_OVERS_ACCELERATOR
**Definition:** Prevents scoring stagnation during overs 7-15.

**Criteria:**
- Middle Overs Strike Rate ≥ 157 (top 15%)
- Elite in at least 2 of:
  - Middle Boundary %
  - Middle Rotation Rate
  - Middle Dot Ball % (inverted - low is good)

**Cricket Context:** Underrated skill. Middle overs typically see SR drop to 125-130. These batters maintain pressure. Essential for setting 180+ totals or successful chases.

---

#### CONSISTENT
**Definition:** Low-variance performer with reliable output.

**Criteria:**
- Coefficient of Variation (CV) < 0.8 for key metrics
- Failure Rate ≤ 25% (innings < 10 runs with opportunity)
- Minimum 30 innings

**Cricket Context:** Reduces risk in team selection. You know what you're getting. May not be explosive but rarely fails completely. Valuable for batting first on uncertain pitches.

---

#### PACE_SPECIALIST (Batter)
**Definition:** Batter who excels against pace bowling.

**Criteria:**
- Strike Rate vs Pace ≥ 130
- Differential vs Spin ≥ 15 (SR vs Pace - SR vs Spin ≥ 15)
- Average vs Pace ≥ 25
- Has faced 200+ pace balls

**Cricket Context:** Use against pace-heavy attacks. Place higher in order vs teams like MI, LSG. Consider for away games against pace-friendly pitches (Chepauk, Wankhede).

---

#### SPIN_SPECIALIST (Batter)
**Definition:** Batter who excels against spin bowling.

**Criteria:**
- Strike Rate vs Spin ≥ 130
- Differential vs Pace ≥ 15 (SR vs Spin - SR vs Pace ≥ 15)
- Average vs Spin ≥ 25
- Has faced 200+ spin balls

**Cricket Context:** Use against spin-heavy attacks. Essential for middle overs scoring. Place in positions 3-5 to face spinners. Consider for subcontinent spin-friendly pitches.

---

#### VULNERABLE_VS_PACE
**Definition:** Batter with clear weakness against pace bowling.

**Criteria:** At least ONE of:
- Strike Rate vs Pace < 110
- Average vs Pace < 12
- Balls per Dismissal vs Pace < 12

**Cricket Context:** Liability against pace attacks. Shield from new ball. Consider dropping against teams with premium pace options. May still be valuable against spin-heavy attacks.

---

#### VULNERABLE_VS_SPIN
**Definition:** Batter with clear weakness against spin bowling.

**Criteria:** At least ONE of:
- Strike Rate vs Spin < 110
- Average vs Spin < 12
- Balls per Dismissal vs Spin < 12

**Cricket Context:** Liability in middle overs. May struggle at spin-friendly venues (Chepauk, Kotla). Consider partnering with spin specialist to rotate strike. Work on footwork in nets.

---

### A.2 Bowler Role Tags (10 Tags)

#### WORKHORSE
**Definition:** All-phase reliable bowler who can bowl in any situation.

**Criteria:**
- Phase Distribution: PP 30-40% / Mid 25-35% / Death 25-35%
- Economy: 7.5-9.5 (consistent but not elite)
- Has bowled 100+ overs
- Low variance in economy across matches

**Cricket Context:** Captain's dream. Can be used flexibly based on match situation. Not a specialist but dependable. Every team needs 1-2 workhorses for tactical flexibility.

---

#### NEW_BALL_SPECIALIST
**Definition:** Bowler focused on powerplay overs with new ball.

**Criteria:**
- Powerplay Workload ≥ 45%
- Powerplay Economy ≤ 8.5
- Powerplay Dot Ball % ≥ 42%
- Has bowled 50+ powerplay overs

**Cricket Context:** Sets the tone with early wickets or containment. Must execute yorkers and short balls with field up. Examples: Trent Boult, Deepak Chahar. Critical for early momentum.

---

#### PP_ELITE
**Definition:** Elite powerplay performer exceeding NEW_BALL_SPECIALIST thresholds.

**Criteria:**
- Powerplay Economy ≤ 8.53 (top 25%)
- Elite in at least 3 of:
  - PP Strike Rate
  - PP Dot Ball %
  - PP Wickets per Match
  - PP Average

**Cricket Context:** Game-changers with new ball. Worth prioritizing in auction. Can restrict batting teams to 35-40 in first 6 overs instead of 50-55. Massive impact on match outcomes.

---

#### MIDDLE_OVERS_CONTROLLER
**Definition:** Bowler who strangles scoring during overs 7-15.

**Criteria:**
- Middle Overs Workload ≥ 55%
- Middle Overs Economy ≤ 8.5
- Middle Overs Dot Ball % ≥ 40%
- Has bowled 80+ middle overs

**Cricket Context:** Usually spinners. Create pressure in transition phase. Allow pace bowlers to rest for death. Examples: Ravindra Jadeja, Sunil Narine. Essential for building pressure.

---

#### MID_OVERS_ELITE
**Definition:** Elite middle-overs performer exceeding MIDDLE_OVERS_CONTROLLER thresholds.

**Criteria:**
- Middle Overs Economy ≤ 8.16 (top 25%)
- Elite in at least 3 of:
  - Mid Strike Rate
  - Mid Dot Ball %
  - Mid Boundary Conceded %
  - Mid Average

**Cricket Context:** Rare spinners who can go 4 overs for 25 runs while taking wickets. Force batters to take risks. Examples: Rashid Khan (peak), Kuldeep Yadav. Worth overseas spot.

---

#### DEATH_SPECIALIST (Bowler)
**Definition:** Bowler who executes in pressure-filled final overs.

**Criteria:**
- Death Overs Workload ≥ 25%
- Death Overs Economy ≤ 10.5
- Has bowled 40+ death overs
- Death Yorker/Short Ball success rate considered

**Cricket Context:** Hardest role in T20 cricket. Must execute under pressure with field spread. Wide yorkers, slow bouncers, variations. Examples: Jasprit Bumrah, Harshal Patel.

---

#### DEATH_ELITE
**Definition:** Elite death-over performer exceeding DEATH_SPECIALIST thresholds.

**Criteria:**
- Death Economy ≤ 10.14 (top 25%)
- Elite in at least 3 of:
  - Death Strike Rate
  - Death Dot Ball %
  - Death Boundary Conceded %
  - Death Wide/No-ball %

**Cricket Context:** Match-winners. Can defend 12 off final over. Worth premium price. Examples: Jasprit Bumrah, Mustafizur Rahman (at peak). Build bowling attack around them.

---

#### PRESSURE_BUILDER
**Definition:** Bowler who creates dot-ball pressure regardless of phase.

**Criteria:**
- Overall Dot Ball % ≥ 38%
- Economy ≤ 8.5
- Low boundary concession rate
- Has bowled 100+ overs

**Cricket Context:** Create chances for other bowlers. Batters take risks after dot balls. Useful in pairs - pressure builder followed by wicket-taker. Reduces required run rate consistently.

---

#### PROVEN_WICKET_TAKER
**Definition:** Bowler with substantial wicket-taking record in T20s.

**Criteria:**
- 50+ T20 wickets
- Strike Rate ≤ 20 (ball per wicket)
- 30+ T20 matches
- Consistent wicket-taking across seasons

**Cricket Context:** Experience matters in crunch moments. Knows how to set up batters. Can be trusted in any situation. Examples: Bumrah, Bhuvneshwar, Chahal. Essential for knockout games.

---

#### PART_TIMER
**Definition:** Occasional bowler used situationally rather than as primary option.

**Criteria:**
- Average overs per match < 2
- Not a designated bowling role in squad
- Used for matchup exploitation or over relief

**Cricket Context:** Sneaky option. Often batters who can roll their arm. Can surprise opposition. Use against specific batters or to complete overs. Examples: Virat Kohli (leg-spin), Rohit Sharma (off-spin).

---

## Appendix B: Bowler Over Timing Analysis (P1-10)

### B.1 Overview

This analysis examines when bowlers bowl their overs during a T20 innings, providing insights for Predicted XII validation.

### B.2 Bowler Over Patterns

Based on existing data in `outputs/metrics/bowler_over_timing.csv`:

| Category | Description | Typical Over Pattern |
|----------|-------------|---------------------|
| PP_AND_DEATH | Bowl overs 1-4 AND 17-20 | Bookend pattern |
| POWERPLAY_BOWLER | Heavy powerplay concentration | Overs 1-6 |
| MIDDLE_OVERS_BOWLER | Bowl overs 7-15 (spinners) | Central cluster |
| DEATH_BOWLER | Late overs focus | Overs 16-20 |

### B.3 Pace vs Spin Patterns

**Pace Bowlers (Typical):**
- 1st over: Overs 0-3 (new ball)
- 2nd over: Overs 2-5 (complete powerplay)
- 3rd over: Overs 14-17 (return at death)
- 4th over: Overs 17-19 (final death)

**Spin Bowlers (Typical):**
- 1st over: Overs 5-8 (end of powerplay/start of middle)
- 2nd over: Overs 7-10 (middle overs)
- 3rd over: Overs 10-13 (middle overs)
- 4th over: Overs 12-16 (late middle/early death)

### B.4 Predicted XII Implications

When validating Predicted XIs, ensure:
1. ✅ At least 2 pace bowlers for new ball (overs 1-6)
2. ✅ At least 2 bowlers for middle overs (overs 7-15)
3. ✅ At least 2 bowlers capable of death overs (overs 16-20)
4. ⚠️ Flag teams missing coverage for any phase
5. ⚠️ Flag over-reliance on single bowler for specific phases

---

*Cricket Playbook v4.0.0*
*Andy Flower - Cricket Domain Expert*
*Updated: 2026-02-04*
