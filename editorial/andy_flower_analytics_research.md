# Groundbreaking Cricket Analytics Research
## Beyond Traditional Statistics: Novel Metrics for Editorial & Broadcast Teams

**Author:** Andy Flower, Cricket Domain Expert
**Version:** 1.0
**Date:** 2026-01-25
**For:** Stephen Curry (Analytics Lead) - Implementation Reference

---

## Executive Summary

This document proposes analytical approaches that move beyond traditional cricket statistics (runs, wickets, averages) to capture the nuances that make cricket compelling. These metrics are designed for editorial storytelling and broadcast enhancement, helping audiences understand *why* matches unfold as they do.

Each concept includes:
- Cricket context and significance
- Proposed calculation methodology
- Data requirements (mapped to our `fact_ball` schema)
- Feasibility rating and implementation priority

---

## 1. Match Phase Dynamics

### 1.1 Momentum Shift Detection

**Cricket Context:**
In T20 cricket, momentum is tangible. A team can be cruising at 60/0 in 6 overs, then lose 3 wickets in 8 balls and suddenly be on the back foot. Broadcast commentators speak of "momentum shifts" but we currently have no way to quantify them.

**Proposed Metric: Momentum Index (MI)**

The Momentum Index tracks the cumulative advantage for the batting team, updating ball-by-ball:

```
MI(n) = MI(n-1) + Ball_Impact(n)

Where Ball_Impact =
  + (runs_scored - expected_runs_this_phase) * run_weight
  - (wicket_cost * is_wicket)
  + (dot_penalty * is_dot_ball)
```

**Phase-adjusted expected runs:**
| Phase | Expected RPB | Dot Penalty | Wicket Cost |
|-------|--------------|-------------|-------------|
| Powerplay (1-6) | 1.35 | -0.3 | -12 |
| Middle (7-15) | 1.25 | -0.2 | -10 |
| Death (16-20) | 1.65 | -0.4 | -8 |

**Momentum Shift Detection:**
A shift occurs when:
1. MI changes by more than 15 points in 12 balls (2 overs)
2. The sign of MI change reverses (positive to negative or vice versa)
3. A cluster event occurs (defined in 1.2)

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| ball_seq | fact_ball.ball_seq | YES |
| total_runs | fact_ball.total_runs | YES |
| is_wicket | fact_ball.is_wicket | YES |
| match_phase | fact_ball.match_phase | YES |
| innings | fact_ball.innings | YES |

**Feasibility: EASY**
All required data exists. Calculation is straightforward window function.

**Implementation Priority: HIGH**
This is the foundational metric for real-time match narratives.

---

### 1.2 Pressure Sequence Definition

**Cricket Context:**
Pressure in cricket builds through sequences, not isolated events. Three dot balls create doubt; a fourth creates panic. Two wickets in an over can turn a match. We need to capture these sequences.

**Proposed Metric: Pressure Sequence Index (PSI)**

A pressure sequence is triggered when any of these conditions occur:

**Type A - Dot Ball Accumulation:**
```sql
-- 4+ consecutive dots (any phase)
-- 3+ consecutive dots in death overs
COUNT(*) FILTER (WHERE batter_runs = 0 AND extra_type IS NULL)
  OVER (ORDER BY ball_seq ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
```

**Type B - Wicket Clusters:**
```sql
-- 2+ wickets within 12 balls
COUNT(*) FILTER (WHERE is_wicket = TRUE)
  OVER (ORDER BY ball_seq ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
```

**Type C - Scoring Stagnation:**
```sql
-- Run rate drops below 6.0 for 18+ balls in death overs
SUM(total_runs) OVER (ORDER BY ball_seq ROWS BETWEEN 17 PRECEDING AND CURRENT ROW) < 18
```

**PSI Calculation:**
```
PSI = (dot_sequence_length * 2) + (wickets_in_cluster * 15) + (stagnation_balls / 6)
```

**Sequence Classification:**
| PSI Range | Label | Editorial Use |
|-----------|-------|---------------|
| 0-5 | Normal | No highlight |
| 6-15 | Building | "Pressure mounting" |
| 16-25 | High | "Crucial phase" |
| 26+ | Critical | "Match-defining moment" |

**Data Requirements:**
All available in `fact_ball` - requires window functions over ball_seq.

**Feasibility: EASY**
Standard SQL window functions. No external data needed.

---

### 1.3 Match Turning Point Detection

**Cricket Context:**
Every match has 2-3 moments that "turn" it. These aren't always wickets - a dropped catch, a big over, or a crucial boundary in a tight chase. We need to identify these retrospectively and potentially in real-time.

**Proposed Metric: Win Probability Delta (WPD)**

**Methodology:**
1. Calculate Win Probability (WP) after each ball using historical data
2. Identify balls where WP changes by more than 8% in a single delivery
3. Rank by absolute WPD to find the "turning points"

**Win Probability Model (simplified):**
```
WP_batting_team = f(
  runs_remaining,
  balls_remaining,
  wickets_in_hand,
  required_run_rate,
  current_run_rate_last_30_balls,
  match_phase
)
```

**Historical Baseline Required:**
| Scenario | Historical WP |
|----------|---------------|
| Chasing, need 36 off 18, 6 wickets | ~55% |
| Chasing, need 36 off 18, 3 wickets | ~28% |
| Setting, 180/4 after 18 overs | ~52% |

**Turning Point Classification:**
| WPD | Impact Level | Example |
|-----|--------------|---------|
| 5-8% | Notable | Important boundary |
| 8-15% | Significant | Key wicket |
| 15-25% | Major | Match-changing moment |
| 25%+ | Decisive | Game over moment |

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| All ball data | fact_ball | YES |
| Historical match outcomes | dim_match.winner_id | YES |
| Historical scenario data | Derived from fact_ball | YES |

**Feasibility: MEDIUM**
Requires building a historical win probability model from our data. Not complex ML, but needs careful calibration.

**Implementation Priority: HIGH**
This is the "hero metric" for post-match analysis and highlight packages.

---

## 2. Player Impact Beyond Traditional Stats

### 2.1 Clutch Performance Measurement

**Cricket Context:**
Some players rise in pressure moments; others shrink. MS Dhoni's legend is built on clutch performances. Current stats (SR, average) don't differentiate between runs in a dead match vs runs that win games.

**Proposed Metric: Clutch Factor (CF)**

**Defining "Clutch Situations":**

| Situation | Clutch Score |
|-----------|--------------|
| Death overs (16-20), margin < 30 runs | 3 |
| Chasing, RRR > 10 | 3 |
| 4+ wickets down in powerplay | 2 |
| Chasing in last 5 overs, any margin | 2 |
| Setting, 5+ wickets down before over 15 | 2 |
| Any situation with PSI > 20 | 2 |

**Clutch Factor Calculation:**
```
CF = (Clutch_Performance_Index) / (Normal_Performance_Index)

Clutch_Performance_Index =
  (Runs_in_clutch / Expected_runs_in_clutch) *
  (1 - Dismissal_rate_in_clutch)

Normal_Performance_Index = Same calculation for non-clutch situations
```

**CF Interpretation:**
| CF Value | Label | Player Examples |
|----------|-------|-----------------|
| > 1.20 | Elite Clutch | MS Dhoni, AB de Villiers |
| 1.05 - 1.20 | Clutch Performer | Hardik Pandya |
| 0.95 - 1.05 | Neutral | Average player |
| 0.80 - 0.95 | Pressure-affected | |
| < 0.80 | Struggles under pressure | |

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| Ball-by-ball data | fact_ball | YES |
| Match situation (margin) | Derived from fact_ball cumulative | YES |
| Required run rate | Derived from innings totals | YES |
| Match outcome | dim_match | YES |

**Feasibility: MEDIUM**
Requires defining clutch situations clearly and building derived columns. Conceptually straightforward.

**Implementation Priority: HIGH**
This metric will generate significant editorial interest. "Who performs when it matters most?"

---

### 2.2 Partnership Synergy Analysis

**Cricket Context:**
Some batting pairs click better than others. Kohli-AB had extraordinary synergy; some pairs never find rhythm together. Beyond aggregate partnership runs, we need to understand *why* partnerships work.

**Proposed Metric: Partnership Synergy Score (PSS)**

**Components:**

**1. Strike Rotation Efficiency:**
```sql
-- How well do they rotate strike?
singles_and_threes / total_balls_faced
```
Optimal rotation keeps both batters in rhythm and facing preferred bowlers.

**2. Boundary Distribution:**
```sql
-- Are boundaries evenly distributed or one-sided?
ABS(batter1_boundary_pct - batter2_boundary_pct)
```
Lower variance = better balance = harder to bowl to.

**3. Run Rate Progression:**
```sql
-- Does the partnership accelerate or stagnate?
(run_rate_last_18_balls - run_rate_first_18_balls) / partnership_balls
```

**4. Pressure Absorption:**
```sql
-- How do they perform when one batter is struggling?
performance_after_partner_dot_sequence
```

**PSS Calculation:**
```
PSS = (Rotation_Score * 0.25) +
      (Balance_Score * 0.20) +
      (Acceleration_Score * 0.30) +
      (Absorption_Score * 0.25)
```

**Editorial Output Example:**
> "Kohli-Patidar partnership synergy: 8.4/10
> - Exceptional rotation (92% singles converted to 2s when running hard)
> - Balanced threat (Kohli 19.2% boundaries, Patidar 21.1%)
> - Strong acceleration (+2.4 RR in second half of partnership)
> - Kohli absorbs pressure well when Patidar plays dots"

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| batter_id | fact_ball.batter_id | YES |
| non_striker_id | fact_ball.non_striker_id | YES |
| batter_runs | fact_ball.batter_runs | YES |
| Partnership tracking | Derived (same two batters consecutive) | YES |

**Feasibility: MEDIUM**
Requires building partnership detection logic (when both batters are same across consecutive balls). Not in current schema but derivable.

**Implementation Priority: MEDIUM**
Interesting for feature pieces but not essential for every match.

---

### 2.3 Fielding Impact Quantification

**Cricket Context:**
Fielding is the least quantified aspect of cricket. A diving save at the boundary in the 19th over is worth more than a routine catch in the 3rd over, but our stats treat them equally.

**Proposed Metric: Fielding Impact Points (FIP)**

**Event Classification:**

| Event | Base Points | Context Multiplier |
|-------|-------------|-------------------|
| Catch (regular) | 3 | Phase multiplier |
| Catch (diving/spectacular) | 5 | Phase multiplier |
| Run out (direct hit) | 5 | Phase multiplier |
| Run out (relay) | 3 | Phase multiplier |
| Stumping | 4 | Phase multiplier |
| Boundary save (sliding) | 2 | Phase multiplier |
| Dropped catch | -4 | Phase multiplier |
| Misfield leading to extra runs | -2 | Phase multiplier |

**Phase Multipliers:**
| Phase | Multiplier | Rationale |
|-------|------------|-----------|
| Powerplay | 1.0 | Standard importance |
| Middle overs | 1.0 | Standard importance |
| Death (16-18) | 1.3 | Higher stakes |
| Death (19-20) | 1.6 | Critical phase |
| Last over, margin < 15 | 2.0 | Match-defining |

**Match Situation Multiplier:**
```
Situation_Multiplier = 1 + (Win_Probability_Change * 0.5)
```

**FIP Calculation:**
```
FIP = Base_Points * Phase_Multiplier * Situation_Multiplier
```

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| fielder_id | fact_ball.fielder_id | YES |
| wicket_type | fact_ball.wicket_type | YES (catches, run outs, stumpings) |
| match_phase | fact_ball.match_phase | YES |
| Ball sequence for context | fact_ball.ball_seq | YES |

**Missing Data:**
- **Dropped catches** - NOT in fact_ball (not recorded in Cricsheet)
- **Boundary saves** - NOT in fact_ball
- **Misfields** - NOT in fact_ball

**Feasibility: HARD (for complete picture)**
Partial implementation (catches, run outs, stumpings) is EASY.
Full implementation requires additional data sources or manual tagging.

**Implementation Priority: LOW (partial), FUTURE (full)**
Start with what we have; flag for future data enrichment.

---

## 3. Tactical Pattern Recognition

### 3.1 Bowling Pattern Analysis

**Cricket Context:**
Elite bowlers don't just bowl fast or spin hard - they set up batters with sequences. Bumrah's slower ball is devastating because of the 10 yorkers before it. We need to capture these patterns.

**Proposed Metrics:**

**1. Variation Timing Index (VTI):**
```sql
-- When does a bowler introduce variation?
-- Count balls bowled before first slower/bouncer/yorker

AVG(balls_before_variation) OVER (PARTITION BY bowler_id, match_id)
```

**2. Length Sequence Pattern:**
```sql
-- Classify each ball by length (derived from runs pattern)
-- Good length: 0-1 runs, no boundaries
-- Short: Often pulled/cut (4s to leg side)
-- Full: Driven (4s through covers)
-- Yorker: Low scoring in death overs

-- Pattern recognition for setup deliveries
```

**3. Line/Length Consistency Score:**
```sql
-- Measure variance in scoring off consecutive balls
STDDEV(batter_runs) OVER (
  PARTITION BY bowler_id, batter_id
  ORDER BY ball_seq
  ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
)
```
Lower variance = more consistent execution.

**Challenge: Line/Length Data**

Our `fact_ball` table does NOT contain:
- Ball pitch location (line)
- Ball length (good length, short, full, yorker)
- Ball speed
- Swing/seam/spin amount

**What We CAN Derive:**
| Derivable Insight | Method |
|-------------------|--------|
| Ball is likely short | Batter hooks/pulls (high runs to leg side) |
| Ball is likely full | Batter drives (runs through off side) |
| Ball is likely yorker | Death overs, 0-1 runs, not a wide |
| Variation ball | Unexpected outcome in sequence |

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| bowler_id | fact_ball.bowler_id | YES |
| batter_runs | fact_ball.batter_runs | YES |
| extra_type | fact_ball.extra_type | YES |
| is_wicket | fact_ball.is_wicket | YES |
| Ball tracking data | NOT AVAILABLE | NO |

**Feasibility: MEDIUM (proxy metrics), HARD (true line/length)**
We can build useful proxies; true analysis needs ball-tracking data.

**Implementation Priority: MEDIUM**
Build what we can; document limitations clearly.

---

### 3.2 Batting Intent Classification

**Cricket Context:**
Not all balls faced are equal. A batter defending to see off a dangerous spell shows different intent than one looking to attack. Current stats don't distinguish between a defensive block and a missed slog.

**Proposed Metric: Intent Classification**

**Classification Rules:**

| Intent Class | Indicators |
|--------------|------------|
| **Defend** | Dot ball, not in death overs, low risk pattern |
| **Rotate** | 1-2 runs, running between wickets |
| **Attack** | 4 or 6, or 3 runs (indicates big shot) |
| **Failed Attack** | Wicket via caught/bowled after dot (likely playing shot) |
| **Survival** | Dot in pressure sequence, high RRR |

**Intent Score Calculation:**
```sql
Intent_Score = (
  (attack_balls * 3) +
  (rotate_balls * 1) +
  (defend_balls * 0) +
  (failed_attack_balls * -2)
) / total_balls
```

**Phase-Adjusted Intent:**
| Phase | Expected Intent Score | Interpretation |
|-------|----------------------|----------------|
| Powerplay | 1.2-1.5 | Moderate aggression |
| Middle (chasing) | 1.0-1.3 | Depends on RRR |
| Middle (setting) | 0.8-1.2 | Building platform |
| Death | 1.8-2.5 | High aggression expected |

**Batting Aggression Score (BAS):**
```
BAS = (Actual_Intent_Score / Expected_Intent_Score) * 100
```

| BAS Range | Classification |
|-----------|----------------|
| < 70 | Conservative |
| 70-90 | Measured |
| 90-110 | Balanced |
| 110-130 | Aggressive |
| > 130 | Ultra-aggressive |

**Data Requirements:**
All available in `fact_ball`.

**Feasibility: EASY**
Straightforward classification based on available data.

**Implementation Priority: HIGH**
This directly enhances strike rate interpretation.

---

### 3.3 Optimal Field Placement Analysis

**Cricket Context:**
Captains set fields based on batter tendencies, but we rarely see this quantified. Where does Kohli score most runs? Where should you place fielders for a left-arm spinner against right-handers?

**Challenge: No Field Placement Data**

Our `fact_ball` does NOT contain:
- Field positions
- Shot direction
- Wagon wheel data

**What We CAN Derive:**

**1. Boundary Concession by Bowler Type:**
```sql
-- Which bowler types get hit for boundaries by which batters?
SELECT
  batter_id,
  bowler_type,
  COUNT(*) FILTER (WHERE batter_runs >= 4) AS boundaries,
  COUNT(*) AS balls
FROM fact_ball fb
JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
GROUP BY 1, 2
```

**2. Phase-Specific Scoring Patterns:**
```sql
-- Does batter score differently in different phases?
-- Suggests different shot selection = different field needed
```

**3. Bowler-Specific Vulnerability:**
```sql
-- Which bowlers does a batter dominate?
-- Suggests poor matchup = need defensive field
```

**Proxy Recommendation Engine:**
```
IF batter has >25% boundary rate vs pace in death overs
THEN recommend "long-on, long-off protection"

IF batter has <15% boundary rate vs off-spin
THEN recommend "attacking field, slips in place"
```

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| Batter scoring patterns | fact_ball aggregations | YES |
| Bowler type | dim_bowler_classification | YES |
| Actual field positions | NOT AVAILABLE | NO |

**Feasibility: HARD (true field analysis), MEDIUM (proxy recommendations)**

**Implementation Priority: LOW**
More of a future enhancement when we get wagon wheel data.

---

## 4. Contextual Factors

### 4.1 Toss Impact Analysis

**Cricket Context:**
The toss advantage varies dramatically by venue. In UAE during IPL 2020-21, chasing was overwhelming favored. At Chepauk, batting first often wins. We need venue-specific toss analysis.

**Proposed Metric: Toss Advantage Index (TAI)**

**Calculation:**
```sql
TAI = (
  (Wins_batting_first_after_winning_toss / Total_toss_wins_batting_first) -
  (Wins_batting_first_after_losing_toss / Total_toss_losses_batting_first)
) * 100
```

**Venue-Specific Analysis:**
```sql
SELECT
  v.venue_name,
  COUNT(*) AS matches,
  AVG(CASE WHEN m.toss_winner_id = m.winner_id THEN 1.0 ELSE 0.0 END) AS toss_win_rate,
  AVG(CASE WHEN m.toss_decision = 'field' AND m.winner_id = m.toss_winner_id
      THEN 1.0 ELSE 0.0 END) AS chase_win_rate_when_chose,
  AVG(CASE WHEN innings_1_total < innings_2_total THEN 1.0 ELSE 0.0 END) AS overall_chase_win_rate
FROM dim_match m
JOIN dim_venue v ON m.venue_id = v.venue_id
GROUP BY 1
HAVING COUNT(*) >= 10
```

**TAI Interpretation:**
| TAI Range | Interpretation |
|-----------|----------------|
| > 15 | Strong toss advantage |
| 5 to 15 | Moderate advantage |
| -5 to 5 | Neutral venue |
| -15 to -5 | Slight disadvantage to toss winner |
| < -15 | Counter-intuitive venue (rare) |

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| toss_winner_id | dim_match.toss_winner_id | YES |
| toss_decision | dim_match.toss_decision | YES |
| winner_id | dim_match.winner_id | YES |
| venue_id | dim_match.venue_id | YES |
| Innings totals | Derived from fact_ball | YES |

**Feasibility: EASY**
All data available. Simple aggregation.

**Implementation Priority: HIGH**
Essential context for any venue-based analysis.

---

### 4.2 Dew Factor Quantification

**Cricket Context:**
Dew makes the ball wet and slippery, helping batters and hindering bowlers (especially spinners). It typically affects the second innings in evening matches. This is talked about but rarely quantified.

**Proposed Metric: Dew Impact Score (DIS)**

**Proxy Measurement (since we don't have actual dew data):**

**1. Second Innings Advantage by Venue:**
```sql
-- Compare 1st vs 2nd innings performance
SELECT
  venue_id,
  AVG(innings_1_economy) - AVG(innings_2_economy) AS economy_diff,
  AVG(innings_1_boundary_pct) - AVG(innings_2_boundary_pct) AS boundary_pct_diff,
  AVG(innings_1_dot_pct) - AVG(innings_2_dot_pct) AS dot_pct_diff
FROM innings_aggregates
GROUP BY venue_id
```

**2. Spinner Degradation Index:**
```sql
-- Do spinners perform worse in 2nd innings at this venue?
SELECT
  venue_id,
  AVG(CASE WHEN innings = 1 THEN spin_economy END) AS spin_eco_inn1,
  AVG(CASE WHEN innings = 2 THEN spin_economy END) AS spin_eco_inn2,
  (spin_eco_inn2 - spin_eco_inn1) AS spinner_degradation
FROM bowling_by_type_innings
GROUP BY venue_id
```

**DIS Calculation:**
```
DIS = (Economy_Diff * 0.4) + (Boundary_Pct_Diff * 0.3) + (Spinner_Degradation * 0.3)
```

**DIS Interpretation:**
| DIS Range | Dew Assessment |
|-----------|----------------|
| > 0.8 | Heavy dew impact |
| 0.4 to 0.8 | Moderate dew |
| 0 to 0.4 | Slight dew |
| < 0 | No dew advantage (or reverse) |

**Limitation:**
This is correlation, not causation. Some venues might have 2nd innings advantage for other reasons (better batting track, pressure of chasing, etc.).

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| Innings number | fact_ball.innings | YES |
| Venue | dim_match.venue_id | YES |
| Bowling type | dim_bowler_classification | YES |
| All ball data | fact_ball | YES |
| Actual dew readings | NOT AVAILABLE | NO |

**Feasibility: MEDIUM**
Proxy is calculable; true dew measurement needs external data.

**Implementation Priority: MEDIUM**
Useful for venue previews and pre-match analysis.

---

### 4.3 Pitch Behavior Evolution

**Cricket Context:**
Pitches change during a match. They can start green and flatten out, or start flat and take turn later. Currently, we describe this qualitatively. Can we quantify it?

**Proposed Metric: Pitch Behavior Index (PBI)**

**Segmented Analysis:**
Divide each innings into thirds and compare:

```sql
SELECT
  match_id,
  innings,
  NTILE(3) OVER (PARTITION BY match_id, innings ORDER BY ball_seq) AS innings_third,
  AVG(batter_runs) AS avg_runs,
  AVG(CASE WHEN is_wicket THEN 1.0 ELSE 0.0 END) AS wicket_rate,
  AVG(CASE WHEN batter_runs = 0 THEN 1.0 ELSE 0.0 END) AS dot_rate
FROM fact_ball
GROUP BY 1, 2, 3
```

**Pitch Degradation Score:**
```
PDS = (Third3_dot_rate / Third1_dot_rate) - 1

If PDS > 0.15: "Pitch slowing down"
If PDS < -0.15: "Pitch getting better for batting"
If -0.15 <= PDS <= 0.15: "Pitch consistent"
```

**Spinner Assistance Index:**
```sql
-- Compare spin vs pace effectiveness across match
spin_advantage_third1 = spin_dot_rate_t1 - pace_dot_rate_t1
spin_advantage_third3 = spin_dot_rate_t3 - pace_dot_rate_t3

Spin_Assistance_Growth = spin_advantage_third3 - spin_advantage_third1
```

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| Ball sequence | fact_ball.ball_seq | YES |
| Bowling type | dim_bowler_classification | YES |
| All outcome data | fact_ball | YES |
| Actual pitch readings | NOT AVAILABLE | NO |

**Feasibility: MEDIUM**
Calculable from existing data with careful methodology.

**Implementation Priority: MEDIUM**
Valuable for venue-specific insights and match context.

---

## 5. Novel Composite Metrics

### 5.1 Match Control Index (MCI)

**Cricket Context:**
At any point in a T20 match, one team has "control." This isn't just about runs on the board - it's about momentum, wickets in hand, run rate, and pressure. We want a single number that says "who's winning right now?"

**Proposed Calculation:**

**For Innings 1 (Setting):**
```
MCI_batting = (
  (Current_RR / Par_RR_for_phase) * 30 +
  (Wickets_in_hand / 10) * 30 +
  (1 - Recent_dot_rate) * 20 +
  (Momentum_Index / 100) * 20
)
```

**For Innings 2 (Chasing):**
```
MCI_chasing = (
  (Current_RR / Required_RR) * 35 +
  (Wickets_in_hand / 10) * 35 +
  (1 - Recent_dot_rate) * 15 +
  (Momentum_Index / 100) * 15
)
```

**MCI Display:**
| MCI Range | Control State |
|-----------|---------------|
| 70-100 | Dominant control |
| 55-70 | Clear advantage |
| 45-55 | Evenly poised |
| 30-45 | Under pressure |
| 0-30 | In trouble |

**Broadcast Use:**
- Display MCI as a graphic that updates ball-by-ball
- Highlight when MCI crosses key thresholds
- Show MCI trajectory over the innings

**Data Requirements:**
All derived from `fact_ball` plus Momentum Index (section 1.1).

**Feasibility: MEDIUM**
Requires combining multiple calculations; conceptually straightforward.

**Implementation Priority: HIGH**
This is the flagship metric for broadcast integration.

---

### 5.2 Batting Aggression Score (BAS) - Enhanced

**Cricket Context:**
Strike rate doesn't capture intent. A batter with SR 150 might be slogging recklessly or timing everything perfectly. We need to understand *how* runs are being scored.

**Enhanced BAS Calculation:**

**Component 1: Boundary Quality**
```
Boundary_Quality = (
  (Sixes / Boundaries) * 1.2 +  -- Sixes show more intent
  (Boundaries_off_good_balls) * 1.5  -- Hitting good balls shows skill
)
```

**Component 2: Rotation Efficiency**
```
Rotation_Score = (
  (Singles_converted_to_twos / Possible_twos) +
  (Strike_rotation_rate)  -- How often batter keeps strike
)
```

**Component 3: Risk Index**
```
Risk_Index = (
  (Dot_balls_after_boundary / Total_dots) +  -- Playing shots after success
  (False_shots / Total_balls)  -- Estimated from wicket types
)
```

**BAS Formula:**
```
BAS = (SR_normalized * 0.35) +
      (Boundary_Quality * 0.30) +
      (Rotation_Score * 0.20) +
      (1 - Risk_Index) * 0.15)
```

**BAS Interpretation:**
| BAS Range | Player Type |
|-----------|-------------|
| > 85 | Elite aggressor (Gayle, Sehwag) |
| 70-85 | Smart aggressor (ABD, SKY) |
| 55-70 | Balanced (Kohli, Williamson) |
| 40-55 | Accumulator (Dhawan, Rahul) |
| < 40 | Anchor (Pujara-style) |

**Data Requirements:**
| Field | Source | Available |
|-------|--------|-----------|
| batter_runs | fact_ball | YES |
| Boundary detection | batter_runs >= 4 | YES |
| Wicket analysis | wicket_type | YES |
| Sequence analysis | Window functions | YES |

**Feasibility: EASY-MEDIUM**
Most components derivable; "false shots" is an approximation.

**Implementation Priority: HIGH**
Direct enhancement to existing player analysis.

---

### 5.3 Bowling Threat Level (BTL)

**Cricket Context:**
Economy rate and strike rate don't tell the full story. A bowler might have 8.5 economy but be genuinely threatening with swing and bounce. Another might have 7.0 economy by being steady but never looking like taking wickets.

**Proposed Calculation:**

**Component 1: Wicket-Taking Ability**
```
Wicket_Threat = (
  (Wickets_per_over * 10) +
  (Caught_bowled_ratio * 5) +  -- Shows genuine edges
  (LBW_bowled_ratio * 5)  -- Shows hitting stumps
)
```

**Component 2: Dot Ball Pressure**
```
Pressure_Score = (
  (Dot_ball_pct * 1.5) +
  (Consecutive_dot_frequency * 2)  -- Creates pressure
)
```

**Component 3: Boundary Prevention**
```
Control_Score = (
  (1 - Boundary_pct) * 20 +
  (1 - Six_pct) * 10  -- Sixes show lack of control
)
```

**Component 4: Phase Effectiveness**
```
Phase_Premium = CASE
  WHEN powerplay_specialist AND pp_economy < 7.5 THEN 1.2
  WHEN death_specialist AND death_economy < 9.5 THEN 1.3
  ELSE 1.0
END
```

**BTL Formula:**
```
BTL = (Wicket_Threat * 0.35 +
       Pressure_Score * 0.25 +
       Control_Score * 0.25 +
       Phase_Premium * 0.15) * 10
```

**BTL Scale (0-100):**
| BTL Range | Threat Level |
|-----------|--------------|
| 80+ | Elite threat (Bumrah, Rashid) |
| 65-80 | High threat |
| 50-65 | Moderate threat |
| 35-50 | Holding option |
| < 35 | Fifth bowler |

**Data Requirements:**
All available in `fact_ball` + `dim_bowler_classification`.

**Feasibility: EASY-MEDIUM**
Straightforward calculation from existing data.

**Implementation Priority: HIGH**
Complements existing bowler archetypes.

---

## 6. Implementation Roadmap

### Phase 1: Quick Wins (1-2 weeks)

| Metric | Complexity | Data Ready | Priority |
|--------|------------|------------|----------|
| Toss Advantage Index (TAI) | Easy | Yes | HIGH |
| Batting Aggression Score (basic) | Easy | Yes | HIGH |
| Pressure Sequence Index (PSI) | Easy | Yes | HIGH |
| Intent Classification | Easy | Yes | HIGH |

### Phase 2: Core Metrics (2-4 weeks)

| Metric | Complexity | Data Ready | Priority |
|--------|------------|------------|----------|
| Momentum Index (MI) | Medium | Yes | HIGH |
| Match Control Index (MCI) | Medium | Yes | HIGH |
| Clutch Factor (CF) | Medium | Yes | HIGH |
| Bowling Threat Level (BTL) | Medium | Yes | HIGH |

### Phase 3: Advanced Analytics (4-8 weeks)

| Metric | Complexity | Data Ready | Priority |
|--------|------------|------------|----------|
| Win Probability Model | Medium | Yes | HIGH |
| Turning Point Detection | Medium | Yes | HIGH |
| Partnership Synergy | Medium | Yes | MEDIUM |
| Dew Impact Score | Medium | Partial | MEDIUM |
| Pitch Behavior Index | Medium | Yes | MEDIUM |

### Phase 4: Future Enhancements (requires new data)

| Metric | Complexity | Data Ready | Priority |
|--------|------------|------------|----------|
| Full Fielding Impact | Hard | No | LOW |
| True Bowling Patterns | Hard | No | LOW |
| Field Placement Analysis | Hard | No | LOW |

---

## 7. Data Gaps and Recommendations

### Critical Missing Data

| Data Element | Impact | Source Options |
|--------------|--------|----------------|
| Ball tracking (line/length) | Enables true bowling analysis | Hawk-Eye, BCCI data |
| Wagon wheel (shot direction) | Enables field analysis | Hawk-Eye, broadcast feeds |
| Dropped catches | Complete fielding picture | Manual tagging, Opta |
| Actual field positions | Tactical analysis | Computer vision on broadcast |
| Dew readings | Environmental context | Weather APIs, ground reports |

### Recommended Data Enrichment

1. **Ball-by-ball commentary** - Extract from ESPNCricinfo for shot descriptions
2. **Player profiles** - Complete bowling styles for all historical players
3. **Venue conditions** - Weather, pitch reports per match
4. **Broadcast metadata** - If accessible, contains rich tactical data

---

## 8. Editorial Use Cases

### Pre-Match Package

1. **Venue Profile**
   - TAI (Toss Advantage Index)
   - DIS (Dew Impact Score)
   - Historical chase success rate

2. **Head-to-Head**
   - Key player Clutch Factors
   - Partnership synergy history
   - Bowler-batter matchup threat levels

### Live Match Graphics

1. **Ball-by-Ball**
   - MCI (Match Control Index) - updating gauge
   - PSI (Pressure Sequence) - heat indicator
   - Current batter BAS - aggression meter

2. **Key Moments**
   - Momentum shift alerts
   - Turning point markers
   - Phase transition summaries

### Post-Match Analysis

1. **Match Narrative**
   - Top 3 turning points with WPD
   - Momentum graph overlay
   - Clutch performances highlighted

2. **Player Ratings**
   - BTL for bowlers
   - BAS for batters
   - FIP for key fielding moments

---

## 9. Sign-Off

This research document represents my assessment of analytical opportunities that go beyond traditional cricket statistics. The metrics proposed here are designed to be:

1. **Cricket-true** - They reflect how the game actually works
2. **Calculable** - Most can be derived from our existing `fact_ball` data
3. **Editorial-ready** - They tell stories, not just show numbers
4. **Broadcast-friendly** - They can be visualized in real-time

I recommend Stephen Curry begin with Phase 1 metrics immediately, as they provide high impact with minimal implementation effort. The win probability model (Phase 3) should be prioritized as it unlocks the most powerful narrative tool: turning point detection.

**Feasibility Summary:**
| Rating | Count | Examples |
|--------|-------|----------|
| EASY | 6 | TAI, PSI, Intent Classification |
| MEDIUM | 8 | MCI, Clutch Factor, Partnership Synergy |
| HARD | 3 | Full Fielding, True Bowling Patterns |

---

*Signed: Andy Flower*
*Cricket Domain Specialist*
*Cricket Playbook Analytics Team*

---

**Document History:**
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-25 | Initial research document |
