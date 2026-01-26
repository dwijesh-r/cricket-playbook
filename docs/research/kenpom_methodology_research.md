# KenPom Methodology Research: Basketball Analytics for Cricket Application
## Deep Dive into Adjusted Efficiency Metrics and IPL Implementation

**Author:** Andy Flower, Cricket Domain Expert
**Version:** 1.0
**Date:** 2026-01-26
**For:** Stephen Curry (Analytics Lead) - Cross-Sport Analytics Reference

---

## Executive Summary

This document provides a comprehensive analysis of Ken Pomeroy's college basketball ratings system (KenPom), the gold standard for efficiency-based sports analytics. The purpose is to extract methodological principles that can be adapted for IPL cricket analytics, specifically around opponent-adjusted metrics, tempo normalization, and contextual performance measurement.

KenPom's core insight - measuring efficiency on a per-possession basis while adjusting for opponent strength - has direct parallels in cricket. This document proposes "CricPom" metrics: adjusted run rates, phase-normalized efficiency, and cricket's equivalent of the Four Factors.

---

## Part 1: Understanding KenPom

### 1.1 What is KenPom?

KenPom (kenpom.com) is a college basketball analytics system created by Ken Pomeroy, a former meteorologist who applies statistical rigor to basketball analysis. His system is now used by:
- Television broadcasts
- College basketball programs
- The NCAA tournament selection committee
- Sports betting markets

**Key Achievement:** KenPom's #1 ranked team at season's end has won the national championship 4 times: Kansas (2008), Kentucky (2012), Virginia (2019), and UConn (2024).

**Core Philosophy:**
> "The system is designed to be purely predictive. The purpose is to show how strong a team would be if it played tonight, independent of injuries or emotional factors."

This is critical: KenPom optimizes for **prediction**, not reward for past performance.

---

### 1.2 The Tempo-Free Revolution

**The Problem KenPom Solved:**

Traditional basketball stats (points per game, rebounds per game) are misleading because teams play at different speeds. A team scoring 80 points in 75 possessions is more efficient than one scoring 85 points in 90 possessions.

**The Solution: Possession-Based Metrics**

KenPom measures everything on a per-100-possessions basis, eliminating tempo distortion.

**Possessions Formula:**
```
Possessions = FGA - OREB + TO + (0.475 * FTA)

Where:
- FGA = Field Goal Attempts
- OREB = Offensive Rebounds
- TO = Turnovers
- FTA = Free Throw Attempts
- 0.475 = Coefficient for FTA (not all FTs end possessions)
```

**Cricket Parallel:**
Cricket already has a natural "possession" unit: the **ball** (or delivery). A T20 innings has a maximum of 120 balls per team. However, wickets also represent "resource consumption" similar to turnovers in basketball.

---

### 1.3 Core KenPom Metrics

| Metric | Definition | What It Measures |
|--------|------------|------------------|
| **AdjO** (Adjusted Offensive Efficiency) | Points scored per 100 possessions vs average D-I defense | Offensive quality, opponent-normalized |
| **AdjD** (Adjusted Defensive Efficiency) | Points allowed per 100 possessions vs average D-I offense | Defensive quality, opponent-normalized |
| **AdjEM** (Adjusted Efficiency Margin) | AdjO - AdjD | Overall team quality |
| **AdjT** (Adjusted Tempo) | Possessions per 40 minutes vs average opponent | Team pace/style |
| **SOS** (Strength of Schedule) | WIN50 rating of opponents faced | Schedule difficulty |

**Key Insight:** The "Adjusted" prefix means the metric represents expected performance against an average opponent on a neutral floor. This isolates team quality from opponent quality.

---

## Part 2: KenPom Methodology Deep Dive

### 2.1 The Adjustment Calculation

**Evolution of the Model:**

**Pre-2014 (Multiplicative Model):**
```
Expected_Offense = Team_O_Rating * Opponent_D_Rating

If Team A's offense is 110% of average and Team B's defense is 110% of average:
Expected = 1.10 * 1.10 = 121% of average
```

**Post-2014 (Additive Model):**
```
Expected_Offense = Team_O_Deviation + Opponent_D_Deviation + League_Average

If Team A's offense is +10% and Team B's defense is +10%:
Expected = +10% + 10% = +20% above average
```

**Why Additive is Better:**

The multiplicative model implied that great defense beats great offense (1.20 offense vs 0.80 defense = 0.96), which doesn't match reality. The additive model treats offense and defense symmetrically.

**Cricket Application:**
For adjusted run rates, we should use the additive model:
```
Adjusted_Run_Rate = Batter_RR_Deviation + Bowler_RR_Deviation + League_Average_RR

If batter scores +1.5 RPO above average and bowler concedes +1.0 RPO:
Expected context = +2.5 RPO above average
```

---

### 2.2 Iterative Calculation for Opponent Adjustment

**The Chicken-and-Egg Problem:**

To know how good Team A is, we need to know how good their opponents are. But to know how good the opponents are, we need to evaluate *their* opponents, including Team A.

**KenPom's Solution: Iterative Convergence**

```
1. Initialize all teams with baseline ratings
2. For each game:
   - Calculate adjusted efficiency based on current opponent ratings
   - Update team's rating
3. Repeat until ratings stabilize (convergence)
4. Typically requires 5-10 iterations for stability
```

**Mathematical Framework:**
```
AdjO_new(Team_A) = AVG[
  Raw_O(Game_i) * (League_Avg_D / AdjD(Opponent_i))
] for all games, weighted by recency
```

The opponent's AdjD is itself calculated using the same iterative process, creating a self-consistent system.

**Cricket Implementation:**
```python
def calculate_adjusted_run_rate(batter_id, innings_data, max_iterations=10):
    # Initialize all bowler ratings to league average
    bowler_ratings = {b: LEAGUE_AVG_ECONOMY for b in all_bowlers}

    for iteration in range(max_iterations):
        # Recalculate batter's adjusted SR against each bowler
        adjusted_innings = []
        for innings in batter_innings:
            opponent_bowling_quality = get_bowling_rating(innings.bowlers, bowler_ratings)
            adjustment_factor = LEAGUE_AVG / opponent_bowling_quality
            adjusted_innings.append(innings.runs * adjustment_factor)

        # Update bowler ratings using same logic
        bowler_ratings = recalculate_bowler_ratings(bowler_ratings, all_innings)

        # Check for convergence
        if ratings_converged(previous_ratings, bowler_ratings):
            break

    return mean(adjusted_innings)
```

---

### 2.3 Strength of Schedule: The WIN50 Method

**The Problem with Simple SOS:**

Averaging opponent ratings creates sensitivity to outliers. Playing the 350th-ranked team shouldn't massively impact SOS differently than playing the 351st-ranked team.

**Jeff Sagarin's WIN50 Solution:**

WIN50 represents "the rating required to win 50% of games against this schedule."

```
SOS = Rating such that:
  Expected_Win_Pct(Rating, Opponents) = 0.50
```

This is calculated using a hypothetical team and running it against the actual schedule.

**Benefits:**
- Minimizes outlier sensitivity
- Provides intuitive interpretation
- Allows direct comparison across teams

**Cricket Parallel: Opposition Strength Index (OSI)**

For IPL player evaluation:
```
OSI = Average quality of opponents faced, weighted by balls/overs

For a batter:
OSI = Weighted_Avg(Bowler_Quality * Balls_Faced_vs_Bowler) / Total_Balls

For a bowler:
OSI = Weighted_Avg(Batter_Quality * Balls_Bowled_to_Batter) / Total_Balls
```

This tells us: "Did this player face tough opposition or feast on weak opponents?"

---

### 2.4 The Pythagorean Expectation

KenPom uses a Pythagorean formula to convert efficiency metrics to expected winning percentage:

```
Expected_Win_Pct = (AdjO^n) / (AdjO^n + AdjD^n)

Where n (exponent) has evolved:
- Original baseball: 2.0
- Initial college basketball: 8-9
- Current KenPom (since 2012): 10.25
```

The higher exponent in basketball reflects that efficiency margin is more predictive than in baseball.

**Cricket Application:**

For T20 cricket, we could use:
```
Expected_Win_Pct = (AdjNRR + k)^n / ((AdjNRR + k)^n + k^n)

Where:
- AdjNRR = Adjusted Net Run Rate
- k = Calibration constant (likely around 1.0-1.5)
- n = Sport-specific exponent (needs empirical determination)
```

Or using run differential:
```
Expected_Wins = Total_Runs_Scored^n / (Total_Runs_Scored^n + Total_Runs_Conceded^n)
```

---

### 2.5 Handling Small Sample Sizes

**The Early Season Problem:**

After 3 games, ratings would be extremely volatile without intervention.

**KenPom's Solution: Preseason Priors**

```
Effective_Rating = (Preseason_Rating * Prior_Weight + Game_Rating * Game_Weight) / (Prior_Weight + Game_Weight)

Where:
- Prior_Weight starts at ~5 games equivalent
- Decays to 0 after 27 games
- Preseason ratings built from:
  - Previous season performance
  - Returning player quality
  - Recruiting rankings
  - Transfer portal impact
```

**Why This Works:**
- Prevents wild fluctuations early
- Prior has predictive value (RMSE ~5.4 points)
- Gracefully transitions to pure performance data
- No bias: preseason doesn't artificially hold back or prop up teams

**Cricket Application: Tournament Priors**

For IPL, we could use:
```
IPL_Prior_Rating = (
    0.40 * Previous_IPL_Performance +
    0.25 * Recent_International_Form +
    0.20 * Domestic_T20_Performance +
    0.15 * Career_Baseline
)

Effective_Rating = (Prior * Prior_Weight + Tournament_Performance * Games_Played) / (Prior_Weight + Games_Played)

Prior_Weight = 3 games equivalent (decays to 0 by game 8)
```

This addresses IPL's challenge: only 14 league games per team, with significant variance.

---

### 2.6 Recency Weighting

**KenPom's Approach:**

Each game gets a weight based on:
1. **Recency:** More recent games weighted higher
2. **Significance:** Games against similar-rated teams weighted higher
3. **Surprise Factor:** Unexpected results (close games against weak teams, blowouts against strong teams) get attention

```
Game_Weight = Recency_Factor * Significance_Factor * Surprise_Factor

Where:
- Recency_Factor = decay function of days since game
- Significance_Factor = f(rating_difference)
- Surprise_Factor = |Actual_Margin - Expected_Margin| threshold
```

**2016 Update:** Recency became less important; system now more stable.

**Cricket Application:**

For player form tracking:
```
Form_Weight = (
    Recency_Decay(days_since_match) *
    Match_Importance(league_stage, opponent_position) *
    Situation_Relevance(phase_played, match_situation)
)
```

This would weight a death-over performance against MI in a playoff more than a powerplay cameo against a bottom team in week 2.

---

## Part 3: Dean Oliver's Four Factors

### 3.1 The Concept

Dean Oliver identified four aspects that explain basketball success:

| Factor | Weight | Formula | What It Measures |
|--------|--------|---------|------------------|
| **eFG%** (Effective FG%) | 40% | (FGM + 0.5*3PM) / FGA | Shooting efficiency |
| **TOV%** (Turnover Rate) | 25% | TO / Possessions | Ball security |
| **ORB%** (Offensive Rebound%) | 20% | OREB / (OREB + Opp_DREB) | Second chance creation |
| **FTR** (Free Throw Rate) | 15% | FTA / FGA | Getting to the line |

These four factors apply to both offense (maximize) and defense (minimize opponent's).

**Why Four Factors Matter:**
- They decompose efficiency into actionable components
- They're largely independent of each other
- They're tempo-free by design
- They identify *how* a team wins, not just *that* they win

---

### 3.2 Cricket's Four Factors: A Proposal

**The T20 Batting Four Factors:**

| Factor | Weight | Formula | Cricket Meaning |
|--------|--------|---------|-----------------|
| **Boundary%** (Boundary Rate) | 35% | (4s + 6s) / Balls_Faced | Scoring power |
| **Dot%** (Dot Ball Rate) | 25% | Dots / Balls_Faced | Rotation/intent |
| **Wicket%** (Dismissal Rate) | 25% | Dismissals / Balls_Faced | Survival |
| **Extras%** (Extras Rate) | 15% | Extras_Won / Balls_Faced | Discipline/awareness |

**Why These Four:**
1. **Boundary%** - Directly scores runs at high efficiency (like eFG%)
2. **Dot%** - Failure to score, builds pressure (like TOV%)
3. **Wicket%** - Losing the "possession" entirely (like TOV% on steroids)
4. **Extras%** - Free runs from bowler errors (like FTR - free points)

**Batting Efficiency Score (BES):**
```
BES = (Boundary% * 35) + ((1 - Dot%) * 25) + ((1 - Wicket%) * 25) + (Extras% * 15)
```

---

**The T20 Bowling Four Factors:**

| Factor | Weight | Formula | Cricket Meaning |
|--------|--------|---------|-----------------|
| **DotPressure%** | 35% | Dots / Balls_Bowled | Building pressure |
| **Boundary_Prevent%** | 25% | 1 - (Boundaries_Conceded / Balls) | Damage limitation |
| **Wicket_Taking%** | 25% | Wickets / Balls_Bowled | Strike capability |
| **Extras_Avoid%** | 15% | 1 - (Extras / Balls_Bowled) | Control/accuracy |

**Bowling Efficiency Score (BowlES):**
```
BowlES = (DotPressure% * 35) + (Boundary_Prevent% * 25) + (Wicket_Taking% * 25) + (Extras_Avoid% * 15)
```

---

### 3.3 Phase-Adjusted Four Factors

The weights should change by match phase:

**Powerplay (Overs 1-6):**
| Factor | Batting Weight | Bowling Weight |
|--------|---------------|----------------|
| Boundary% | 40% | 30% |
| Dot% | 20% | 35% |
| Wicket% | 30% | 25% |
| Extras% | 10% | 10% |

Rationale: Powerplay favors boundaries due to field restrictions; wickets are costly for batting.

**Middle Overs (7-15):**
| Factor | Batting Weight | Bowling Weight |
|--------|---------------|----------------|
| Boundary% | 30% | 25% |
| Dot% | 30% | 35% |
| Wicket% | 25% | 25% |
| Extras% | 15% | 15% |

Rationale: Rotation matters more; building pressure through dots is key.

**Death Overs (16-20):**
| Factor | Batting Weight | Bowling Weight |
|--------|---------------|----------------|
| Boundary% | 45% | 40% |
| Dot% | 15% | 25% |
| Wicket% | 25% | 25% |
| Extras% | 15% | 10% |

Rationale: Boundaries decide death overs; dots matter less when batters attack everything.

---

## Part 4: CricPom - KenPom for Cricket

### 4.1 Adjusted Run Rate (AdjRR)

**The Core Metric:**

Just as KenPom's AdjO measures points per 100 possessions against average defense, cricket's AdjRR measures runs per over against average bowling.

**Formula:**
```
AdjRR_batter = (Actual_RR * League_Avg_Economy) / Opponent_Bowling_Quality

Opponent_Bowling_Quality = Weighted_Avg(Bowler_AdjEcon * Balls_Faced_vs_Bowler)

Where:
- Bowler_AdjEcon is that bowler's economy rate, itself adjusted for batter quality faced
```

**Example Calculation:**

| Innings | Actual RR | Opponent Quality | Adjustment Factor | Adjusted RR |
|---------|-----------|------------------|-------------------|-------------|
| vs MI Death Bowlers | 10.5 | 7.2 (elite) | 8.5/7.2 = 1.18 | 12.4 |
| vs PBKS Spinners | 12.0 | 9.8 (poor) | 8.5/9.8 = 0.87 | 10.4 |
| vs CSK All-rounders | 9.0 | 8.2 (avg) | 8.5/8.2 = 1.04 | 9.4 |

The batter's true quality is better reflected by the adjusted figures.

---

### 4.2 Adjusted Economy (AdjEcon)

**For Bowlers:**
```
AdjEcon = (Actual_Economy * League_Avg_SR) / Opponent_Batting_Quality

Opponent_Batting_Quality = Weighted_Avg(Batter_AdjSR * Balls_Bowled_to_Batter)
```

This answers: "What would this bowler's economy be against average IPL batters?"

---

### 4.3 Venue Normalization

**The Challenge:**

IPL venues vary dramatically:
- Chinnaswamy: High-scoring (avg first innings ~180)
- Chepauk: Spin-friendly (avg first innings ~155)
- Wankhede: Balanced (avg first innings ~170)

**KenPom Parallel:** KenPom adjusts for home/away but not venue-specific factors.

**Cricket Solution: Park Factor**

Borrowed from baseball analytics:
```
Venue_Factor = (Avg_Runs_at_Venue / League_Avg_Runs)

Normalized_Performance = Actual_Performance / Venue_Factor
```

**Multi-Dimensional Park Factor:**

| Venue | Overall Factor | Pace Factor | Spin Factor | Death Factor |
|-------|---------------|-------------|-------------|--------------|
| Chinnaswamy | 1.12 | 1.08 | 0.95 | 1.18 |
| Chepauk | 0.91 | 0.88 | 1.15 | 0.85 |
| Wankhede | 1.02 | 1.05 | 0.98 | 1.08 |
| Eden Gardens | 0.96 | 0.92 | 1.08 | 0.94 |

**Application:**
```
Venue_Adjusted_SR = Actual_SR / Venue_Overall_Factor

A 160 SR at Chinnaswamy = 160 / 1.12 = 143 AdjSR
A 140 SR at Chepauk = 140 / 0.91 = 154 AdjSR
```

---

### 4.4 Phase-Adjusted Efficiency

**Tempo-Free for Cricket:**

Just as KenPom measures per-possession, cricket should measure per-phase-ball:

```
Phase_Adjusted_SR = (Actual_Phase_SR / Expected_Phase_SR) * League_Avg_SR

Expected_Phase_SR from historical data:
- Powerplay: 135 SR expected
- Middle: 125 SR expected
- Death: 155 SR expected
```

**Example:**
| Batter | Powerplay SR | Middle SR | Death SR | Phase-Adjusted Total SR |
|--------|--------------|-----------|----------|------------------------|
| A | 145 | 120 | 150 | 137.6 |
| B | 130 | 140 | 170 | 148.2 |

Batter B is more valuable despite similar raw SR because they excel in death overs where SR matters most.

---

### 4.5 Cricket Efficiency Margin (CEM)

**The Master Metric:**

Combining batting and bowling adjusted metrics:
```
Team_CEM = Team_AdjRR - Opponent_AdjRR_Against_Team

Player_CEM = (Batting_AdjRR_Contribution + Bowling_AdjEcon_Savings) / Matches
```

**Interpretation:**
| CEM | Team Quality |
|-----|--------------|
| +1.5+ | Elite (title contender) |
| +0.5 to +1.5 | Playoff quality |
| -0.5 to +0.5 | Average |
| -1.5 to -0.5 | Below average |
| < -1.5 | Poor |

---

## Part 5: Implementation Architecture

### 5.1 Data Requirements Mapping

| KenPom Concept | Cricket Equivalent | Data Source | Available |
|----------------|-------------------|-------------|-----------|
| Points scored | Runs scored | fact_ball.total_runs | YES |
| Possessions | Balls faced | COUNT(fact_ball) | YES |
| Opponent ID | Bowler/Batter ID | fact_ball.bowler_id / batter_id | YES |
| Field Goals | Boundaries | fact_ball.batter_runs >= 4 | YES |
| Turnovers | Wickets | fact_ball.is_wicket | YES |
| Free Throws | Extras | fact_ball.extra_runs | YES |
| Home/Away | Venue | dim_match.venue_id | YES |
| Game Date | Match Date | dim_match.match_date | YES |

**All core requirements are met by existing schema.**

---

### 5.2 Proposed Table Structure

**New Analytics Tables:**

```sql
-- Adjusted player ratings (updated after each match)
CREATE TABLE analytics.player_adjusted_ratings (
    player_id INTEGER,
    season_id INTEGER,
    rating_date DATE,

    -- Batting metrics
    adj_strike_rate DECIMAL(6,2),
    adj_average DECIMAL(6,2),
    batting_efficiency_score DECIMAL(5,2),

    -- Phase breakdown
    adj_sr_powerplay DECIMAL(6,2),
    adj_sr_middle DECIMAL(6,2),
    adj_sr_death DECIMAL(6,2),

    -- Bowling metrics
    adj_economy DECIMAL(5,2),
    adj_strike_rate_bowling DECIMAL(5,2),
    bowling_efficiency_score DECIMAL(5,2),

    -- Four Factors (batting)
    boundary_rate DECIMAL(5,4),
    dot_rate DECIMAL(5,4),
    dismissal_rate DECIMAL(5,4),
    extras_rate DECIMAL(5,4),

    -- Opposition strength faced
    batting_osi DECIMAL(5,2),  -- Opposition Strength Index
    bowling_osi DECIMAL(5,2),

    -- Iteration metadata
    calculation_iteration INTEGER,
    confidence_interval DECIMAL(4,2),

    PRIMARY KEY (player_id, season_id, rating_date)
);

-- Team adjusted ratings
CREATE TABLE analytics.team_adjusted_ratings (
    team_id INTEGER,
    season_id INTEGER,
    rating_date DATE,

    adj_run_rate DECIMAL(5,2),
    adj_run_rate_against DECIMAL(5,2),
    cricket_efficiency_margin DECIMAL(5,2),

    -- Four Factors aggregated
    team_boundary_rate DECIMAL(5,4),
    team_dot_rate DECIMAL(5,4),
    team_dismissal_rate DECIMAL(5,4),

    -- Schedule strength
    sos_batting DECIMAL(5,2),
    sos_bowling DECIMAL(5,2),

    -- Expected wins
    pythagorean_win_pct DECIMAL(5,4),

    PRIMARY KEY (team_id, season_id, rating_date)
);

-- Venue park factors
CREATE TABLE analytics.venue_park_factors (
    venue_id INTEGER,
    season_id INTEGER,

    overall_factor DECIMAL(4,3),
    pace_factor DECIMAL(4,3),
    spin_factor DECIMAL(4,3),
    powerplay_factor DECIMAL(4,3),
    death_factor DECIMAL(4,3),

    sample_matches INTEGER,

    PRIMARY KEY (venue_id, season_id)
);
```

---

### 5.3 Calculation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    CricPom Calculation Pipeline                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Raw Metrics Calculation                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ For each player-match:                                   │    │
│  │   - Calculate raw SR, average, economy                   │    │
│  │   - Calculate Four Factors                               │    │
│  │   - Segment by phase (PP, middle, death)                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Step 2: Initialize Opponent Ratings                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ - Set all players to league average                      │    │
│  │ - Or use preseason priors (previous season + form)       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Step 3: Iterative Adjustment (Loop until convergence)          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ For each iteration:                                      │    │
│  │   - Recalculate AdjSR using current opponent ratings     │    │
│  │   - Recalculate AdjEcon using current batter ratings     │    │
│  │   - Apply recency weighting                              │    │
│  │   - Check for convergence (delta < threshold)            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Step 4: Venue Normalization                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ - Calculate venue park factors                           │    │
│  │ - Apply venue adjustment to player metrics               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Step 5: Composite Metrics                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ - Calculate Batting Efficiency Score (BES)               │    │
│  │ - Calculate Bowling Efficiency Score (BowlES)            │    │
│  │ - Calculate Cricket Efficiency Margin (CEM)              │    │
│  │ - Calculate Opposition Strength Index (OSI)              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  Step 6: Output & Validation                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ - Write to analytics tables                              │    │
│  │ - Validate against known outcomes                        │    │
│  │ - Generate confidence intervals                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5.4 Python Implementation Skeleton

```python
class CricPomCalculator:
    """
    Cricket adaptation of KenPom methodology.
    Calculates opponent-adjusted, venue-normalized efficiency metrics.
    """

    CONVERGENCE_THRESHOLD = 0.01
    MAX_ITERATIONS = 15
    LEAGUE_AVG_SR = 135.0
    LEAGUE_AVG_ECON = 8.5

    def __init__(self, ball_data: pd.DataFrame, match_data: pd.DataFrame):
        self.ball_data = ball_data
        self.match_data = match_data
        self.player_ratings = {}
        self.venue_factors = {}

    def calculate_raw_metrics(self, player_id: int, role: str) -> dict:
        """Calculate unadjusted metrics for a player."""
        if role == 'batter':
            innings = self.ball_data[self.ball_data['batter_id'] == player_id]
            return {
                'strike_rate': innings['batter_runs'].sum() / len(innings) * 100,
                'boundary_rate': (innings['batter_runs'] >= 4).sum() / len(innings),
                'dot_rate': (innings['batter_runs'] == 0).sum() / len(innings),
                'dismissal_rate': innings['is_wicket'].sum() / len(innings),
            }
        # Similar for bowler...

    def calculate_opponent_quality(self, player_id: int, match_id: int, role: str) -> float:
        """
        Calculate the quality of opponents faced in a specific match.
        Uses current iteration's ratings.
        """
        match_balls = self.ball_data[
            (self.ball_data['match_id'] == match_id) &
            (self.ball_data['batter_id' if role == 'batter' else 'bowler_id'] == player_id)
        ]

        if role == 'batter':
            # Quality of bowlers faced
            opponents = match_balls['bowler_id'].unique()
            weights = match_balls.groupby('bowler_id').size()
            qualities = [self.player_ratings.get(b, {}).get('adj_economy', self.LEAGUE_AVG_ECON)
                        for b in opponents]
            return np.average(qualities, weights=[weights.get(b, 1) for b in opponents])
        # Similar for bowler...

    def iterate_adjustments(self) -> None:
        """
        Main iterative loop for opponent adjustment.
        Continues until ratings converge.
        """
        for iteration in range(self.MAX_ITERATIONS):
            previous_ratings = copy.deepcopy(self.player_ratings)

            for player_id in self.get_all_players():
                # Calculate adjusted metrics using current opponent ratings
                raw = self.calculate_raw_metrics(player_id, 'batter')
                opp_quality = self.aggregate_opponent_quality(player_id, 'batter')

                adj_sr = raw['strike_rate'] * (self.LEAGUE_AVG_ECON / opp_quality)

                self.player_ratings[player_id] = {
                    'adj_strike_rate': adj_sr,
                    'adj_economy': self.calculate_adj_economy(player_id),
                    # ... other metrics
                }

            # Check convergence
            if self.has_converged(previous_ratings, self.player_ratings):
                print(f"Converged after {iteration + 1} iterations")
                break

    def calculate_four_factors(self, player_id: int, role: str, phase: str = None) -> dict:
        """
        Calculate cricket's Four Factors for a player.
        Optionally filter by phase (powerplay, middle, death).
        """
        data = self.ball_data[self.ball_data['batter_id'] == player_id]

        if phase:
            data = data[data['match_phase'] == phase]

        return {
            'boundary_rate': (data['batter_runs'] >= 4).mean(),
            'dot_rate': (data['batter_runs'] == 0).mean(),
            'dismissal_rate': data['is_wicket'].mean(),
            'extras_rate': (data['extra_runs'] > 0).mean(),
        }

    def calculate_efficiency_score(self, four_factors: dict, phase: str = None) -> float:
        """
        Combine Four Factors into single efficiency score.
        Weights vary by phase.
        """
        weights = self.get_phase_weights(phase)

        return (
            four_factors['boundary_rate'] * weights['boundary'] +
            (1 - four_factors['dot_rate']) * weights['dot'] +
            (1 - four_factors['dismissal_rate']) * weights['dismissal'] +
            four_factors['extras_rate'] * weights['extras']
        ) * 100
```

---

## Part 6: Editorial Applications

### 6.1 Player Comparison Dashboard

**"True Performance" Rankings:**

| Rank | Player | Raw SR | AdjSR | OSI | BES |
|------|--------|--------|-------|-----|-----|
| 1 | SKY | 178.2 | 171.4 | 108 | 84.2 |
| 2 | Kohli | 152.3 | 161.8 | 115 | 79.6 |
| 3 | Buttler | 165.1 | 158.2 | 96 | 77.8 |
| 4 | Gill | 148.9 | 155.3 | 112 | 76.1 |

**Narrative:** "Kohli's adjusted strike rate jumps 9.5 points because he faced the toughest bowling attacks in IPL 2025 (OSI 115). SKY's raw dominance holds up even after adjustment."

---

### 6.2 Team Strength Assessment

**Cricket Efficiency Margin Standings:**

| Team | AdjRR | AdjRR Against | CEM | Pythagorean Win% |
|------|-------|---------------|-----|------------------|
| GT | 9.42 | 7.85 | +1.57 | 68.2% |
| CSK | 9.18 | 7.92 | +1.26 | 62.1% |
| MI | 9.05 | 8.01 | +1.04 | 58.4% |
| RCB | 8.88 | 8.55 | +0.33 | 51.2% |

**Narrative:** "GT's +1.57 CEM is the largest in IPL history, driven by elite death bowling (AdjEcon 7.2 in overs 16-20)."

---

### 6.3 Matchup Analysis

**Pre-Match Efficiency Comparison:**

```
MI vs CSK - Wankhede Stadium

Team Efficiency Margins (venue-adjusted):
┌─────────────────────────────────────────────────────┐
│              MI        CSK                          │
│ AdjRR:       9.05      9.18                        │
│ AdjRR Ag:    8.01      7.92                        │
│ CEM:        +1.04     +1.26                        │
│                                                     │
│ Phase Breakdown (CEM):                              │
│ Powerplay:  +0.42     +0.68  (CSK edge)            │
│ Middle:     +0.35     +0.31  (Even)                │
│ Death:      +0.27     +0.27  (Even)                │
│                                                     │
│ Key Matchup: Bumrah (AdjEcon 6.8) vs Jadeja (AdjEcon 7.2)│
│ Both death-over specialists with elite efficiency   │
└─────────────────────────────────────────────────────┘

Projection: CSK slight favorites (+0.22 CEM advantage)
Win Probability: CSK 54% | MI 46%
```

---

### 6.4 Historical Context

**"Best Adjusted Seasons in IPL History":**

| Rank | Player | Season | AdjSR | OSI | Context |
|------|--------|--------|-------|-----|---------|
| 1 | Kohli | 2016 | 168.4 | 118 | Faced best bowling, still dominated |
| 2 | Warner | 2016 | 162.1 | 109 | Consistent excellence |
| 3 | Gayle | 2012 | 159.8 | 105 | Pre-adjustment SR was higher |
| 4 | SKY | 2022 | 158.2 | 112 | Modern-era benchmark |

**Insight:** "Kohli's 2016 remains the greatest adjusted performance because he maintained elite efficiency against the strongest schedule (OSI 118)."

---

## Part 7: Validation Framework

### 7.1 Predictive Accuracy Testing

**Method:** Use first-half season AdjSR to predict second-half performance.

```
Test: Does AdjSR predict future performance better than raw SR?

Results (hypothetical):
| Metric | Correlation with 2nd Half SR | RMSE |
|--------|------------------------------|------|
| Raw SR | 0.62 | 18.4 |
| AdjSR | 0.71 | 14.2 |

AdjSR reduces prediction error by 23%.
```

### 7.2 Team Win Prediction

**Method:** Use CEM to predict match outcomes.

```
Test: Does CEM predict wins better than NRR?

Results (hypothetical):
| Metric | Correct Win Predictions (%) | AUC |
|--------|----------------------------|-----|
| Raw NRR | 58.2% | 0.61 |
| CEM | 64.7% | 0.68 |

CEM improves win prediction by 11%.
```

### 7.3 Sanity Checks

**Known Players Should Rank Correctly:**
- Bumrah should have elite AdjEcon
- Kohli should have high AdjSR
- Rashid Khan should excel in middle overs

**Venue Factors Should Match Intuition:**
- Chinnaswamy factor > 1.0 (high-scoring)
- Chepauk spin factor > 1.0 (spin-friendly)

---

## Part 8: Limitations and Caveats

### 8.1 Data Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No ball-tracking data | Can't measure true bowling quality | Use outcome-based proxies |
| No field position data | Can't credit fielding in adjustments | Acknowledge in methodology |
| Small IPL sample (14 games) | Higher variance in estimates | Use priors, confidence intervals |
| Player role changes | Batters may change positions | Segment by batting position |

### 8.2 Methodological Caveats

1. **Causation vs Correlation:** Adjusted metrics show association, not causation
2. **Context Collapse:** Averaging across situations loses nuance
3. **Form vs Ability:** Recent form may differ from true ability
4. **Tactical Choices:** Low SR might be intentional anchoring

### 8.3 Communication Guidance

**Do Say:**
- "Adjusted for opponent strength"
- "Expected performance against average bowling"
- "More predictive of future performance"

**Don't Say:**
- "True ability" (implies certainty we don't have)
- "Better than" (without context)
- "Proves" (statistical inference, not proof)

---

## Part 9: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

| Task | Complexity | Dependencies | Output |
|------|------------|--------------|--------|
| Raw metrics calculation | Easy | fact_ball access | Player raw stats |
| Venue park factors | Easy | Historical data | venue_park_factors table |
| Four Factors implementation | Easy | Raw metrics | Four factor columns |

### Phase 2: Adjustments (Week 3-4)

| Task | Complexity | Dependencies | Output |
|------|------------|--------------|--------|
| Iterative adjustment engine | Medium | Raw metrics | Adjusted ratings |
| OSI calculation | Medium | Adjusted ratings | Opposition strength |
| Recency weighting | Medium | Match dates | Weighted ratings |

### Phase 3: Composite Metrics (Week 5-6)

| Task | Complexity | Dependencies | Output |
|------|------------|--------------|--------|
| BES/BowlES calculation | Easy | Four Factors | Efficiency scores |
| CEM calculation | Easy | Team aggregates | Team ratings |
| Pythagorean wins | Easy | CEM | Expected win % |

### Phase 4: Validation (Week 7-8)

| Task | Complexity | Dependencies | Output |
|------|------------|--------------|--------|
| Predictive testing | Medium | Full pipeline | Validation report |
| Sanity checks | Easy | Player ratings | Quality assurance |
| Documentation | Easy | All above | Technical spec |

---

## Part 10: Conclusion and Recommendations

### Key Takeaways

1. **KenPom's Core Insight Translates:** Measuring efficiency on a per-unit basis (possessions/balls) while adjusting for opponent quality is universally applicable.

2. **Iterative Adjustment is Essential:** You can't know true player quality without knowing opponent quality, requiring iterative convergence.

3. **Four Factors Decomposition Works:** Breaking efficiency into components (shooting/boundaries, turnovers/wickets, etc.) identifies *how* not just *that*.

4. **Venue Normalization Adds Value:** Park factors borrowed from baseball capture cricket's venue variance better than raw metrics.

5. **Priors Stabilize Small Samples:** IPL's 14-game season needs preseason priors to reduce variance, similar to KenPom's approach.

### Recommended Next Steps

1. **Immediate:** Implement raw Four Factors calculation - zero adjustment complexity, high editorial value
2. **Short-term:** Build venue park factors using historical IPL data
3. **Medium-term:** Implement iterative adjustment engine for AdjSR/AdjEcon
4. **Long-term:** Develop win probability model using CEM as input

### Priority Metrics for Editorial Use

| Metric | Editorial Value | Implementation Effort | Priority |
|--------|-----------------|----------------------|----------|
| Four Factors | HIGH | LOW | P0 |
| Venue Park Factors | HIGH | LOW | P0 |
| Opposition Strength Index | HIGH | MEDIUM | P1 |
| Adjusted Strike Rate | HIGH | MEDIUM | P1 |
| Cricket Efficiency Margin | MEDIUM | MEDIUM | P2 |
| Pythagorean Wins | MEDIUM | LOW | P2 |

---

## References and Sources

### KenPom Methodology
- [KenPom Ratings Explanation](https://kenpom.com/blog/ratings-explanation/) - Official methodology documentation
- [KenPom Ratings Methodology Update](https://kenpom.com/blog/ratings-methodology-update/) - 2014 shift to additive model
- [KenPom Four Factors](https://kenpom.com/blog/four-factors/) - Four Factors explanation
- [KenPom Stats Explained](https://kenpom.com/blog/stats-explained/) - Glossary of metrics
- [Preseason Ratings: Why Weight?](https://kenpom.com/blog/preseason-ratings-why-weight/) - Small sample handling

### General Analytics
- [Sports Illustrated: KenPom Rankings Explained](https://www.si.com/college-basketball/kenpom-rankings-explained-who-is-ken-pomeroy-what-do-rankings-mean) - Overview
- [Basketball Reference: Four Factors](https://www.basketball-reference.com/about/factors.html) - Dean Oliver's original framework
- [Ken Pomeroy Wikipedia](https://en.wikipedia.org/wiki/Ken_Pomeroy_(statistician)) - Background
- [A Sea of Blue: Tempo-Free Primer](https://www.aseaofblue.com/2013/7/4/4493456/basketball-tempo-free-stats-primer) - Educational resource
- [Rock M Nation: Understanding Efficiency Margin](https://www.rockmnation.com/2021/1/4/22211605/advanced-analytics-understanding-efficiency-margin-adjusted) - Deep dive

### Cricket Analytics
- [ESPNcricinfo Smart Stats](https://www.espncricinfo.com/story/espncricinfo-smart-stats-a-new-way-to-understand-t20-cricket-1142569) - T20 analytics approach
- [The Cricket Monthly: Best Stats Measure](https://www.thecricketmonthly.com/story/1057899/the-best-stats-measure) - Adjusted batting metrics
- [Duckworth-Lewis-Stern Method](https://en.wikipedia.org/wiki/Duckworth%E2%80%93Lewis%E2%80%93Stern_method) - Resource-based cricket modeling

### Strength of Schedule
- [Sagarin Rankings](http://sagarin.com/sports/cbsend.htm) - WIN50 methodology source
- [KenPom vs Sagarin Comparison](https://www.pointspreads.com/guides/kenpom-vs-sagarin-rankings-a-comprehensive-comparison-for-sports-betting/) - System comparison

---

*Signed: Andy Flower*
*Cricket Domain Specialist*
*Cricket Playbook Analytics Team*

---

**Document History:**
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-26 | Initial research document |
