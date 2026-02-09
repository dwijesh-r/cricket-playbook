# CricPom Prototype Specification

## IDEA-002 | Florentino Gate: APPROVED | Classification: ANALYTICS_ONLY

**Author:** Jose Mourinho, Quant Researcher / Data Scientist
**Version:** 1.0
**Date:** 2026-02-09
**Status:** SPEC ONLY -- Not Implementation
**Scope Cap:** Enforced. No code. No infrastructure changes. No deployment artifacts.

---

## 0. Preamble

I have read both the KenPom methodology research (Andy Flower, 2026-01-26) and the PFF grading system research (Ime Udoka, 2026-01-26). Both are solid foundational documents. What follows is a prototype specification that is honest about what transfers from basketball to cricket, what does not, and where the landmines are buried.

Let me be direct: the temptation with a project like this is to build everything KenPom does and call it "CricPom." That would be a mistake. Basketball and cricket share structural similarities -- efficiency measurement, opponent adjustment, tempo normalization -- but they diverge in critical ways. This spec respects those divergences. We build what the data supports, defer what it does not, and we do not pretend.

**Everything in this document is ANALYTICS_ONLY.** No editorial framing, no fan-facing narratives, no product decisions. Pure methodology.

---

## 1. What Is CricPom?

### 1.1 The One-Sentence Definition

CricPom is an opponent-adjusted, venue-normalized, phase-aware efficiency rating system for T20 cricket teams and players, built on ball-by-ball data.

### 1.2 The KenPom Analogy, Translated Honestly

KenPom answers one question for college basketball: "How good is this team, really, once you strip away who they played, where they played, and how fast they played?"

CricPom answers the equivalent for T20 cricket: "How good is this team/player, really, once you adjust for the quality of opposition faced, the venues played at, and the phase of the innings?"

| KenPom Concept | CricPom Translation | Fidelity of Transfer |
|----------------|---------------------|----------------------|
| Points per 100 possessions | Runs per over (adjusted) | HIGH -- direct parallel |
| Adjusted Offensive Efficiency (AdjO) | Adjusted Batting Run Rate (AdjBRR) | HIGH |
| Adjusted Defensive Efficiency (AdjD) | Adjusted Bowling Economy (AdjBE) | HIGH |
| Adjusted Efficiency Margin (AdjEM) | Cricket Efficiency Margin (CEM) | HIGH |
| Adjusted Tempo (AdjT) | No direct equivalent* | LOW -- see Section 2 |
| Strength of Schedule (SOS) | Opposition Strength Index (OSI) | MEDIUM -- different structure |
| Pythagorean Win Expectation | Run-rate Pythagorean Win% | MEDIUM -- needs calibration |
| Four Factors (Dean Oliver) | Cricket Four Factors | MEDIUM -- conceptual, not structural |
| Preseason Priors | Tournament Priors | HIGH -- IPL needs this badly |

*In basketball, tempo is a team choice (how fast you push the ball). In T20 cricket, the tempo is fixed: 120 balls per innings, full stop. The closest equivalent is "scoring acceleration profile" -- how a team distributes aggression across phases -- but this is a style descriptor, not a normalization variable. We do not pretend this is the same thing.

### 1.3 What CricPom Is Not

I want this on the record before anyone gets excited:

1. **CricPom is not a match prediction engine.** It produces ratings. Ratings are inputs to prediction models. They are not predictions themselves. Conflating the two is how you lose credibility.

2. **CricPom is not a player grading system.** That is PFF territory (IDEA-003, if it ever gets approved). CricPom measures efficiency outcomes adjusted for context. PFF-style grading measures process quality on each delivery. Different tools, different jobs.

3. **CricPom is not a replacement for domain expertise.** It is a lens. A very good lens. But if the model says Bumrah is average, you check the model before you check Bumrah.

---

## 2. Feature Mapping: What Transfers, What Does Not

### 2.1 Concepts That Transfer Cleanly

#### A. Per-Unit Efficiency Measurement

Basketball moved from "points per game" to "points per possession." Cricket already thinks in runs per over and strike rate per ball. The conceptual leap is smaller. Our ball-by-ball data gives us the denominator (balls faced / balls bowled) at maximum granularity.

**Verdict:** TRANSFERS. This is the foundation.

#### B. Opponent Adjustment via Iterative Convergence

The chicken-and-egg problem exists identically in cricket. To know if a batter is truly good, you need to know the quality of the bowlers they faced. To know bowler quality, you need to know the batters they bowled to. KenPom's iterative convergence (initialize, adjust, repeat until stable) is sport-agnostic.

**Verdict:** TRANSFERS. This is the core innovation we are importing.

#### C. Venue Normalization (Park Factors)

This actually transfers better to cricket than basketball. KenPom adjusts for home/away advantage. Cricket venues vary far more dramatically than basketball arenas -- Chinnaswamy is not Chepauk is not Wankhede. Park factors are borrowed from baseball, and they work.

**Verdict:** TRANSFERS. Arguably more important in cricket than basketball.

#### D. Recency Weighting

Recent performance is more predictive than ancient performance. True in basketball, true in cricket, true in life. The specific decay function needs cricket-specific calibration, but the principle is universal.

**Verdict:** TRANSFERS. Decay parameters need empirical tuning.

#### E. Preseason Priors for Small Samples

IPL teams play 14 league matches. That is a tiny sample. KenPom uses preseason priors (worth ~5 games equivalent) that decay as real data accumulates. We need this. Possibly more urgently than basketball does, because 14 games is worse than 30+ for establishing stable ratings.

**Verdict:** TRANSFERS. Critical for IPL application.

### 2.2 Concepts That Transfer With Modification

#### F. The Four Factors

Dean Oliver's Four Factors decompose basketball efficiency into four independent-ish components: shooting efficiency, turnover rate, offensive rebounding, free throw rate. Andy Flower's research proposes cricket equivalents: boundary rate, dot ball rate, dismissal rate, extras rate.

The concept is sound. The execution needs care. In basketball, the four factors are empirically validated as largely independent and collectively explanatory. In cricket, we have not validated this yet. Boundary rate and dot ball rate are inversely correlated by construction (more boundaries = fewer dots, usually). Dismissal rate may confound with batting position and phase. The weights (35/25/25/15) proposed in the KenPom research are reasonable starting points but are not empirically derived from our data.

**Verdict:** TRANSFERS WITH CAVEATS. Validate independence. Derive weights empirically. Do not assume basketball's factor structure maps cleanly.

#### G. Strength of Schedule

KenPom uses Sagarin's WIN50 method: the rating required to win 50% of games against a given schedule. In basketball, schedules are long (30+ games) and varied. In IPL, every team plays every other team at least once, sometimes twice. The schedule is shorter and more uniform. SOS still matters -- some teams face opponents at their peaks, others face them in troughs -- but the variance is compressed.

Additionally, in cricket, "strength of schedule" operates at two levels:
- **Team level:** Which teams did you play, and when?
- **Matchup level:** Which specific bowlers did this batter face? Which batters did this bowler bowl to?

The matchup level is more granular and more valuable. A batter who faced Bumrah for 20 balls and Rashid Khan for 15 balls had a harder assignment than one who faced part-time offspinners for the same number of deliveries. Ball-by-ball data gives us this.

**Verdict:** TRANSFERS, but cricket benefits from matchup-level granularity that basketball SOS does not attempt.

### 2.3 Concepts That Do Not Transfer

#### H. Adjusted Tempo (AdjT)

In basketball, tempo is a strategic choice. Virginia plays at 60 possessions per game. Gonzaga plays at 75. This fundamentally changes how you interpret raw scoring. You must normalize.

In T20 cricket, the "clock" is fixed. Both teams get 120 legal deliveries (barring DLS scenarios). There is no tempo to adjust for. What varies is the *distribution* of aggression across phases (how much a team scores in the powerplay vs. death), but this is a stylistic profile, not a normalization axis.

**Verdict:** DOES NOT TRANSFER. Do not force-fit it. Build phase-specific metrics instead.

#### I. Home/Away Binary

KenPom adjusts for home-court advantage as a binary: +3.5 points per game for the home team (empirically derived). Cricket does not work this way. IPL teams have "home" venues, but the advantage is not a simple additive constant. It is mediated by:
- Pitch familiarity (some players are better on spinning tracks)
- Altitude and boundary dimensions
- Travel fatigue patterns
- Crowd effects (less quantifiable)

Venue park factors subsume most of this. A separate "home" adjustment on top of venue factors risks double-counting.

**Verdict:** DOES NOT TRANSFER as a separate adjustment. Venue normalization handles this. If residual home advantage exists after venue adjustment, we can test for it empirically. Do not assume it.

#### J. Garbage Time Filtering

KenPom reduces the weight of possessions when the game outcome is decided (30+ point leads late). In T20 cricket, the equivalent would be the death overs of a dead-rubber chase or a first innings after a team is 50/6 in the powerplay. The problem: T20 cricket is compact enough that "garbage time" barely exists. Even a team chasing 220 might score 80 in the last 5 overs against defensive bowling. Context collapses differently.

**Verdict:** DOES NOT TRANSFER in the same form. We should weight by match situation (required run rate, wickets in hand) rather than binary "garbage time" detection.

---

## 3. Proposed Metrics

### 3.1 Tier 1: Core Team Metrics

These are the metrics that constitute the "CricPom rating" at the team level.

#### 3.1.1 Adjusted Batting Run Rate (AdjBRR)

**Definition:** Expected runs per over a team would score against a league-average bowling attack on a neutral venue.

**Formula (Additive Model):**
```
AdjBRR_team = League_Avg_RR + Team_Batting_Deviation

Where:
  Team_Batting_Deviation = Mean(
    (Actual_RR_match_i - Expected_RR_match_i) for all matches
  )

  Expected_RR_match_i = League_Avg_RR + Opponent_Bowling_Deviation_match_i + Venue_Factor_match_i
```

We use the additive model following KenPom's post-2014 methodology. The multiplicative model has known asymmetry problems (great defense beats great offense, which does not match cricket reality either).

**Phase Decomposition:**
```
AdjBRR = w_pp * AdjBRR_powerplay + w_mid * AdjBRR_middle + w_death * AdjBRR_death

Where:
  w_pp = 6/20 = 0.30 (proportion of innings in powerplay)
  w_mid = 9/20 = 0.45 (proportion of innings in middle overs)
  w_death = 5/20 = 0.25 (proportion of innings in death overs)
```

Note: These are ball-proportion weights, not importance weights. The phase-specific AdjBRR values themselves capture the relative difficulty of scoring in each phase.

#### 3.1.2 Adjusted Bowling Economy (AdjBE)

**Definition:** Expected runs per over a team's bowling attack would concede against a league-average batting lineup on a neutral venue.

**Formula:**
```
AdjBE_team = League_Avg_RR + Team_Bowling_Deviation

Where:
  Team_Bowling_Deviation = Mean(
    (Actual_Economy_match_i - Expected_Economy_match_i) for all matches
  )

  Expected_Economy_match_i = League_Avg_RR + Opponent_Batting_Deviation_match_i + Venue_Factor_match_i
```

Lower is better. A team with AdjBE below league average has a bowling attack that restricts scoring better than expected.

#### 3.1.3 Cricket Efficiency Margin (CEM)

**Definition:** The gap between adjusted batting and adjusted bowling. This is the master team-quality metric, equivalent to KenPom's AdjEM.

**Formula:**
```
CEM = AdjBRR - AdjBE
```

**Interpretation Scale (Preliminary -- Must Be Calibrated Against Our Data):**

| CEM Range | Interpretation |
|-----------|----------------|
| > +1.50 | Elite. Title contender. |
| +0.75 to +1.50 | Playoff quality. Genuine threat. |
| +0.25 to +0.75 | Above average. Could go either way. |
| -0.25 to +0.25 | Average. The muddled middle. |
| -0.75 to -0.25 | Below average. Needs improvement. |
| < -0.75 | Poor. Structural problems. |

These thresholds are hypothetical. After running the model on IPL 2023-2025 data, the actual distribution will determine the cutoffs. If the standard deviation of CEM is 0.6 RPO, then +1.50 would be 2.5 sigma -- extremely rare. If the SD is 1.2 RPO, then +1.50 is only 1.25 sigma -- relatively common. The data decides.

#### 3.1.4 Opposition Strength Index (OSI)

**Definition:** A ball-weighted measure of the quality of opponents a team has faced.

**Team-Level Formula:**
```
OSI_batting = Weighted_Avg(Opponent_AdjBE for each match, weighted by balls bowled to us)
OSI_bowling = Weighted_Avg(Opponent_AdjBRR for each match, weighted by balls we bowled)
```

This tells us: "Has this team's batting line-up faced elite bowling attacks, or have they padded stats against part-timers?" Same question, inverted, for bowling.

#### 3.1.5 Pythagorean Win Expectation

**Definition:** Expected win percentage derived from run-rate efficiency margin.

**Formula:**
```
Pyth_Win% = (AdjBRR)^n / ((AdjBRR)^n + (AdjBE)^n)
```

Where n is a sport-specific exponent. In baseball n ~ 2. In basketball n ~ 10.25. For T20 cricket, we do not know n. It must be empirically derived from our 9,357-match dataset by fitting the exponent that minimizes the residual between predicted and actual win percentages across seasons.

**Estimation approach:** Grid search over n in [3, 15], minimize RMSE(predicted_wins, actual_wins) across team-seasons. My hypothesis: n will land somewhere in [6, 10] for T20s, reflecting that T20 outcomes are more volatile than basketball but less volatile than Test cricket.

### 3.2 Tier 2: Core Player Metrics

#### 3.2.1 Adjusted Strike Rate (AdjSR)

**Definition:** Expected strike rate a batter would achieve against a league-average bowling attack on a neutral venue.

**Formula:**
```
AdjSR_batter = League_Avg_SR + Batter_SR_Deviation

Where:
  Batter_SR_Deviation is calculated via iterative convergence:

  For each innings i:
    Deviation_i = Actual_SR_i - (League_Avg_SR + Bowler_Quality_Faced_i + Venue_Factor_i)

  Batter_SR_Deviation = Weighted_Mean(Deviation_i, weights = recency * balls_faced_i)
```

The bowler quality faced is itself calculated iteratively (see Section 3.4).

#### 3.2.2 Adjusted Economy Rate (AdjEcon)

**Definition:** Expected economy rate a bowler would concede against a league-average batting lineup on a neutral venue.

**Formula:**
```
AdjEcon_bowler = League_Avg_Economy + Bowler_Economy_Deviation

Where:
  Bowler_Economy_Deviation is calculated via iterative convergence:

  For each spell i:
    Deviation_i = Actual_Econ_i - (League_Avg_Economy + Batter_Quality_Faced_i + Venue_Factor_i)

  Bowler_Economy_Deviation = Weighted_Mean(Deviation_i, weights = recency * balls_bowled_i)
```

#### 3.2.3 Player Opposition Strength Index (Player OSI)

**Definition:** Ball-weighted average quality of opponents a specific player has faced.

```
Player_OSI_batter = Sum(Bowler_AdjEcon_j * Balls_Faced_vs_j) / Total_Balls_Faced

Player_OSI_bowler = Sum(Batter_AdjSR_j * Balls_Bowled_to_j) / Total_Balls_Bowled
```

This is the most granular SOS measure possible. It uses every ball faced, weighted by the adjusted quality of the specific opponent on the other end. A batter with Player OSI of 7.2 (elite bowling) who still scores at 150 SR is far more impressive than one with Player OSI of 9.5 (poor bowling) scoring at 160 SR.

### 3.3 Tier 3: Decomposition Metrics (The Four Factors)

The Four Factors decompose efficiency into its components. They answer "how does this team/player achieve their efficiency?"

#### Batting Four Factors

| Factor | Definition | Measurement |
|--------|-----------|-------------|
| Boundary Rate (BR%) | Proportion of balls resulting in 4 or 6 | (4s + 6s) / Balls_Faced |
| Dot Ball Rate (DB%) | Proportion of balls resulting in zero batter runs | Dots / Balls_Faced |
| Dismissal Rate (DR%) | Proportion of balls resulting in wicket | Wickets / Balls_Faced |
| Extras Won Rate (EW%) | Proportion of balls yielding extras | Extras_Balls / Balls_Faced |

#### Bowling Four Factors

| Factor | Definition | Measurement |
|--------|-----------|-------------|
| Dot Pressure Rate (DP%) | Proportion of balls resulting in dot | Dots / Balls_Bowled |
| Boundary Prevention Rate (BP%) | 1 - (Boundaries conceded / Balls_Bowled) | 1 - (4s_6s_conceded / Balls_Bowled) |
| Wicket Taking Rate (WT%) | Proportion of balls resulting in wicket | Wickets / Balls_Bowled |
| Extras Conceded Rate (EC%) | 1 - (Extras conceded / Balls_Bowled) | 1 - (Extras / Balls_Bowled) |

#### Weight Derivation

The KenPom research proposes weights of 35/25/25/15 for these factors. I do not accept these weights as given. They are starting hypotheses borrowed from basketball's factor structure, which has been empirically validated in that sport over 20+ years.

For the prototype, we will:
1. Calculate all four factors for every team-match in our dataset
2. Run a multiple regression: `Match_Win ~ BR% + DB% + DR% + EW%`
3. Use the standardized regression coefficients as empirical weights
4. Compare to the proposed 35/25/25/15 and report the delta

If the empirical weights are close (within 5pp on each factor), the basketball-derived weights are acceptable. If they diverge materially, we use the cricket-derived weights.

### 3.4 The Iterative Convergence Engine

This is the core computational mechanism. Without this, "adjusted" metrics are just raw metrics with a fancy label.

**Algorithm:**

```
INITIALIZE:
  For all players P:
    AdjSR(P) = League_Avg_SR
    AdjEcon(P) = League_Avg_Economy

ITERATE (max 15 iterations):
  For each batter B:
    For each innings I of batter B:
      opponent_quality_I = ball_weighted_avg(AdjEcon of bowlers faced in I)
      venue_factor_I = park_factor(venue of I)
      expected_SR_I = League_Avg_SR + (opponent_quality_I - League_Avg_Economy) + venue_factor_I
      deviation_I = actual_SR_I - expected_SR_I
    AdjSR(B) = League_Avg_SR + weighted_mean(deviation_I, weights=recency * balls_I)

  For each bowler W:
    For each spell S of bowler W:
      opponent_quality_S = ball_weighted_avg(AdjSR of batters faced in S)
      venue_factor_S = park_factor(venue of S)
      expected_Econ_S = League_Avg_Economy + (opponent_quality_S - League_Avg_SR) / 100 * 6 + venue_factor_S
      deviation_S = actual_Econ_S - expected_Econ_S
    AdjEcon(W) = League_Avg_Economy + weighted_mean(deviation_S, weights=recency * balls_S)

  CHECK CONVERGENCE:
    delta = max(|AdjSR_new - AdjSR_old|) across all players
    if delta < 0.01: STOP

OUTPUT:
  Final AdjSR for all batters
  Final AdjEcon for all bowlers
```

**Convergence expectations:** Based on KenPom's experience (5-10 iterations for basketball), I expect 5-8 iterations for cricket with our dataset size. The larger the network of matchups, the faster convergence. With 9,357 matches and millions of balls, the matchup network is dense.

**Potential convergence failure modes:**
- Players with very few balls (< 30 in a season) can oscillate. Solution: Bayesian shrinkage toward league average, proportional to sample size.
- Disconnected subgraphs in the matchup network (e.g., players who only appear in one league). Solution: Use cross-league priors cautiously, or restrict to within-league ratings.

### 3.5 Venue Park Factors

**Calculation:**

```
Park_Factor(venue, season) = Avg_Runs_Per_Over_at_Venue / League_Avg_Runs_Per_Over

With optional phase decomposition:
  PF_powerplay(venue) = Avg_PP_RPO_at_Venue / League_Avg_PP_RPO
  PF_middle(venue) = Avg_Mid_RPO_at_Venue / League_Avg_Mid_RPO
  PF_death(venue) = Avg_Death_RPO_at_Venue / League_Avg_Death_RPO
```

**Minimum sample requirement:** At least 10 matches at a venue in a season for a season-specific park factor. Below that threshold, use a multi-season blended factor with exponential decay.

**Known issue:** IPL venues change across seasons. A venue might host 8 matches one year and 3 the next. The multi-season blend handles this, but we must flag park factors computed from small samples with a confidence indicator.

### 3.6 Tournament Priors (Small Sample Stabilization)

**The Problem:** IPL has 14 league matches per team. After 3 matches, raw ratings are noise. After 7 matches, they are shaky. After 14, they are reasonable but not stable.

**The Solution (Adapted from KenPom):**

```
Effective_Rating(match_k) = (Prior * Prior_Weight + Observed_Rating * k) / (Prior_Weight + k)

Where:
  k = number of matches played
  Prior_Weight = 3.0 (equivalent to 3 matches of prior data)
  Prior = previous season's end-of-tournament rating, regressed toward mean

  Prior regression:
    Prior = 0.60 * Previous_Season_Final_Rating + 0.40 * League_Average
```

**Why 60/40 regression?** Year-to-year correlation of team quality in IPL is moderate (squads change via auction, players age, conditions shift). In college basketball, KenPom uses stronger priors because the sport has more structural stability. Cricket's auction-driven franchise model means last year's champion can become this year's bottom dweller. 60/40 hedges appropriately.

**Decay schedule:**

| Matches Played | Prior Weight | Observed Weight | Prior Influence |
|---------------|-------------|-----------------|-----------------|
| 0 (pre-tournament) | 3.0 | 0 | 100% |
| 3 | 3.0 | 3 | 50% |
| 7 | 3.0 | 7 | 30% |
| 10 | 3.0 | 10 | 23% |
| 14 | 3.0 | 14 | 18% |

By match 14, the prior still contributes 18%. This may feel too high. If backtesting shows that zeroing out the prior by match 10 improves prediction, we do that. The data decides, not my intuition.

---

## 4. Data Availability Assessment

### 4.1 What We Have

We are working with the following confirmed data assets:

| Asset | Scope | Records | Granularity |
|-------|-------|---------|-------------|
| Ball-by-ball data | Multiple T20 leagues | 2.1M deliveries | Per-ball |
| Match metadata | Multiple T20 leagues | 9,357 matches | Per-match |
| IPL specific | IPL 2023-2025 | 219 matches | Per-ball + per-match |
| Analytics views | Pre-built | 35 views | Various |

**Key fields available (from KenPom research data mapping, Section 5.1):**

| Required Field | Available Column | Confirmed |
|---------------|-----------------|-----------|
| Runs scored per ball | fact_ball.total_runs, fact_ball.batter_runs | YES |
| Ball count | COUNT(fact_ball) | YES |
| Batter identity | fact_ball.batter_id | YES |
| Bowler identity | fact_ball.bowler_id | YES |
| Wicket indicator | fact_ball.is_wicket | YES |
| Extras | fact_ball.extra_runs | YES |
| Venue | dim_match.venue_id | YES |
| Match date | dim_match.match_date | YES |
| Boundary indicator | fact_ball.batter_runs >= 4 | YES (derivable) |
| Match phase | Derivable from over number | YES (derivable) |

### 4.2 What We Can Build With This Data

**Fully Buildable (High Confidence):**

| Metric | Data Requirement | Status |
|--------|-----------------|--------|
| AdjBRR (team) | Runs, balls, opponent IDs, venue | ALL AVAILABLE |
| AdjBE (team) | Runs conceded, balls, opponent IDs, venue | ALL AVAILABLE |
| CEM | AdjBRR, AdjBE | DERIVED |
| AdjSR (player) | Runs, balls faced, bowler IDs, venue | ALL AVAILABLE |
| AdjEcon (player) | Runs conceded, balls bowled, batter IDs, venue | ALL AVAILABLE |
| Batting Four Factors | Boundaries, dots, wickets, extras per ball | ALL AVAILABLE |
| Bowling Four Factors | Same, from bowler perspective | ALL AVAILABLE |
| Venue Park Factors | Runs per over by venue | ALL AVAILABLE |
| OSI (team and player) | Opponent adjusted ratings, ball counts | DERIVED |
| Pythagorean Win% | AdjBRR, AdjBE | DERIVED |
| Tournament Priors | Previous season ratings | AVAILABLE (2024-2025 baseline) |
| Phase decomposition | Over number (derivable to PP/mid/death) | ALL AVAILABLE |

**Partially Buildable (Medium Confidence):**

| Metric | Data Requirement | Gap |
|--------|-----------------|-----|
| Recency weighting | Match dates, days between matches | Available, but optimal decay function unknown |
| Innings-context adjustment | 1st vs 2nd innings, target score | Need to verify 1st/2nd innings flag in schema |
| Toss impact factor | Toss result, toss decision | Need to verify toss data availability |
| Batting position context | Batting order position per innings | Need to verify availability |

### 4.3 What We Cannot Build (Data Gaps)

**Not Buildable Without Additional Data Sources:**

| Metric / Feature | Missing Data | Impact |
|-----------------|-------------|--------|
| Ball-tracking quality metrics | Hawk-Eye / ball trajectory data | Cannot grade delivery quality (PFF-style). Limited to outcome-based analysis. |
| Fielding contribution | Fielder position, catch difficulty | Cannot isolate fielding in CEM. Fielding remains a black box. |
| Expected Runs (xR) model | Ball speed, length, line, movement | Cannot build process-based expected value. Stuck with outcome-based proxies. |
| Pitch deterioration curves | Pitch hardness, moisture, cracks over time | Cannot model within-match pitch changes. Venue factors are static per match. |
| Player fitness / workload | Training load, injury status | Cannot adjust for fatigue effects. |
| Squad composition effects | Playing XI confirmation, batting order pre-match | Cannot model selection bias in advance. |
| Weather conditions | Temperature, humidity, dew | Cannot adjust for dew factor (massive in subcontinental T20s). |
| Crowd / travel fatigue | Travel schedules, crowd size | Non-quantifiable with available data. |

**Honest assessment:** The absence of ball-tracking data is the single largest constraint. KenPom benefits from basketball being a relatively simple outcome space (made/missed shots from known locations). Cricket's outcome space is richer (the same "4 runs" can come from a perfectly timed drive or a top edge over the keeper), and without ball-tracking data, we cannot distinguish between them. We are building outcome-adjusted metrics, not process-adjusted metrics. This is a meaningful limitation.

---

## 5. What Must Be Deferred

### 5.1 Deferred: Phase 2+ (Requires Ball-Tracking Data)

| Feature | Why Deferred | What It Would Enable |
|---------|-------------|---------------------|
| Delivery Quality Index | No ball trajectory data | Grade each ball's difficulty independent of outcome |
| Expected Runs Above Expected (xRAE) | No ball-tracking data | True batter skill isolation |
| Expected Wickets Above Expected (xWAE) | No ball-tracking data | True bowler skill isolation |
| Process-Based Grading (PFF-style) | No video review pipeline | Separate execution quality from outcome quality |
| Fielding Value Model | No fielder tracking data | Quantify fielding contribution to CEM |

### 5.2 Deferred: Phase 2+ (Requires Additional Research)

| Feature | Why Deferred | Research Required |
|---------|-------------|-------------------|
| Matchup-specific adjustments | Need to establish batter-bowler matchup stability | Test if specific batter-vs-bowler histories are predictive or just noise |
| Batting position adjustment | Need to model positional effects on SR expectations | Different SR expectations for openers vs. #6. Need position-specific baselines. |
| Toss/innings adjustment | Need to model first vs. second innings bias | Chasing teams have known advantages. Need to quantify and separate from team quality. |
| Pressure-adjusted metrics | Need situational win probability model | Weight contributions by match leverage |
| Multi-format prior blending | Need cross-format correlation analysis | Does international T20 form predict IPL form? At what weight? |

### 5.3 Deferred: Explicitly Out of Scope

| Item | Reason |
|------|--------|
| Real-time in-match ratings | This is a batch analytics system, not a live engine |
| Fan-facing product | ANALYTICS_ONLY classification. No editorial layer. |
| Auction valuation model | Requires economic modeling beyond CricPom's scope |
| Automated narrative generation | PFF's AI narrative tool is a product feature, not an analytics feature |
| Fantasy sports integration | Commercial application, not analytics research |

---

## 6. Minimum Viable Prototype (MVP) Scope

### 6.1 The MVP Question

"What is the smallest version of CricPom that produces genuine analytical value and validates the methodology?"

### 6.2 MVP Definition

**Dataset:** IPL 2023-2025 (219 matches, approximately 50,000+ overs of ball-by-ball data).

**Why IPL only for MVP:** Contained league, consistent teams across seasons, known team/player quality for sanity-checking results. Expanding to other T20 leagues introduces cross-league comparability problems that are out of scope for a prototype.

**MVP Metrics (Build These):**

| # | Metric | Level | Priority |
|---|--------|-------|----------|
| 1 | Venue Park Factors (overall + by phase) | Venue | P0 |
| 2 | Raw Four Factors (batting + bowling) | Player + Team | P0 |
| 3 | Iterative Opponent-Adjusted SR (AdjSR) | Player | P0 |
| 4 | Iterative Opponent-Adjusted Economy (AdjEcon) | Player | P0 |
| 5 | Team AdjBRR | Team | P0 |
| 6 | Team AdjBE | Team | P0 |
| 7 | Cricket Efficiency Margin (CEM) | Team | P0 |
| 8 | Opposition Strength Index (OSI) | Player + Team | P1 |
| 9 | Tournament Priors (using 2023-2024 to predict 2025) | Team + Player | P1 |
| 10 | Pythagorean Win% | Team | P1 |

**MVP Deliverables:**

| Deliverable | Description |
|-------------|-------------|
| CricPom Rating Table (Teams) | All 10 IPL teams ranked by CEM for each season (2023, 2024, 2025) |
| CricPom Rating Table (Batters) | Top 50 batters by AdjSR, with OSI and Four Factors |
| CricPom Rating Table (Bowlers) | Top 50 bowlers by AdjEcon, with OSI and Four Factors |
| Venue Park Factor Table | All IPL venues with overall and phase-specific park factors |
| Validation Report | Predictive accuracy of CricPom ratings vs. raw metrics |

### 6.3 MVP Validation Criteria

The prototype is considered successful if it meets ALL of the following:

| Criterion | Test | Pass Threshold |
|-----------|------|---------------|
| Convergence | Iterative engine converges within 15 iterations | delta < 0.01 on all player ratings |
| Sanity | Known elite players rank in top quartile | Bumrah AdjEcon top-5, Kohli/SKY AdjSR top-10 |
| Predictive lift | AdjSR predicts future SR better than raw SR | Correlation improvement >= 0.05 (absolute) |
| Win prediction | CEM predicts match outcomes better than NRR | AUC improvement >= 0.03 over raw NRR |
| Stability | Ratings do not wildly oscillate match-to-match | Max single-match rating change < 2 SD |
| Venue validity | Park factors match known venue characteristics | Chinnaswamy > 1.0, Chepauk < 1.0 |

If ANY criterion fails, the model has a bug or a structural flaw. We do not ship metrics that fail sanity checks, no matter how elegant the math.

### 6.4 MVP Non-Scope (Do Not Build for Prototype)

- Phase-specific weights for Four Factors (use equal weights or basketball-derived as placeholder)
- Multi-format prior blending (IPL-only for MVP)
- Recency weighting beyond simple linear decay
- Batting position adjustment
- First/second innings adjustment
- Matchup-specific ratings (batter vs. specific bowler)
- Any visualization or dashboard
- Any API or data service

### 6.5 Estimated Effort

| Component | Estimated Effort | Dependencies |
|-----------|-----------------|--------------|
| Venue Park Factors | 2-3 hours | DuckDB access, venue-match mapping |
| Raw Four Factors | 3-4 hours | Ball-by-ball schema understanding |
| Iterative Convergence Engine | 8-12 hours | Core algorithm, testing convergence |
| Team Aggregation (AdjBRR, AdjBE, CEM) | 3-4 hours | Player-level adjusted metrics |
| OSI Calculation | 2-3 hours | Adjusted ratings as input |
| Tournament Priors | 4-6 hours | Multi-season data, regression analysis |
| Pythagorean Win% | 2-3 hours | CEM, historical win data |
| Validation Suite | 6-8 hours | All metrics, test framework |
| **Total** | **30-43 hours** | |

This is a prototype, not production. No hardening, no CI/CD, no monitoring. Just the math, the data, and the validation.

---

## 7. Risk Register

### 7.1 Technical Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| T-01 | Iterative convergence fails or oscillates | LOW | HIGH | Cap iterations at 15. Apply damping factor (0.5 * old + 0.5 * new) if oscillation detected. Fall back to single-pass adjustment if convergence fails entirely. |
| T-02 | Small sample players dominate/distort rankings | MEDIUM | MEDIUM | Bayesian shrinkage toward league average. Minimum 50 balls faced/bowled to receive a rating. Below threshold, player rated at prior or league average. |
| T-03 | Venue park factors unstable for low-sample venues | MEDIUM | LOW | Multi-season blending with exponential decay. Flag low-confidence factors (< 10 matches). |
| T-04 | Phase classification edge cases (super overs, DLS, retired hurt) | LOW | LOW | Exclude super overs from ratings. Handle DLS matches by using actual balls bowled (not projected). Flag retired-hurt innings. |
| T-05 | Additive model produces impossible values (negative economy rates) | LOW | MEDIUM | Clamp outputs to sensible ranges. If AdjEcon < 3.0 or AdjSR > 300, flag for review. These would indicate model error, not real performance. |
| T-06 | Cross-season comparability breaks down | MEDIUM | MEDIUM | Normalize to within-season league averages. Do not directly compare 2023 CEM to 2025 CEM without re-centering. |

### 7.2 Methodological Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| M-01 | Four Factors are not independent in cricket (boundary rate and dot rate are mechanically correlated) | HIGH | MEDIUM | Test correlation matrix. If factors are > 0.7 correlated, consider dimensionality reduction or dropping a factor. Report correlation structure honestly. |
| M-02 | Opponent adjustment over-corrects for strong teams (elite players only face each other) | MEDIUM | MEDIUM | Monitor for "adjustment paradox" where all elite players regress to average because they all face each other. If detected, apply ceiling on adjustment magnitude. |
| M-03 | Venue factors confound with team identity (CSK always plays at Chepauk) | MEDIUM | HIGH | Use both home AND away performances to calculate team ratings. If a team only plays half its matches at home, the venue factor should wash out in the team-level aggregate. Test by comparing home-only vs. away-only ratings for each team. |
| M-04 | Pythagorean exponent poorly calibrated | MEDIUM | LOW | This is a P1 metric, not P0. If the exponent fit produces R-squared < 0.5, defer Pythagorean Win% to Phase 2. It is not essential for the core rating system. |
| M-05 | Tournament priors are too strong or too weak | MEDIUM | MEDIUM | Backtest: use 2023 priors to predict 2024, and 2024 priors to predict 2025. Optimize prior weight (currently set at 3.0 match-equivalents) to minimize prediction error. Report optimal weight with confidence interval. |
| M-06 | Recency weighting introduces instability | LOW | LOW | For MVP, use simple linear decay (most recent match = weight 1.0, oldest match = weight 0.5). More sophisticated decay functions are Phase 2. |

### 7.3 Data Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| D-01 | Ball-by-ball data has quality issues (missing balls, incorrect attribution) | LOW | HIGH | Run data quality checks before model execution. Verify: total balls per innings <= 120 (excluding extras), no duplicate ball records, every ball has batter_id and bowler_id populated. |
| D-02 | Player ID inconsistency across seasons | LOW | MEDIUM | Verify player ID mapping is consistent in dim tables. Spot-check 20 players who played across all 3 seasons. |
| D-03 | IPL 2023-2025 sample too small for stable venue factors | MEDIUM | MEDIUM | 219 matches across ~8-10 venues = ~22-27 matches per venue on average. Marginal. Supplement with broader T20 data for venue factors only if needed. |
| D-04 | Extras classification inconsistency | LOW | LOW | Extras are the least important of the Four Factors (15% weight). Even if extras data has issues, impact on overall ratings is minimal. Flag but do not block. |

### 7.4 Interpretation Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| I-01 | Stakeholders interpret CricPom ratings as "truth" rather than estimates | HIGH | HIGH | Every output table must include confidence intervals or sample size indicators. Documentation must state: "These are estimates with uncertainty, not ground truth." |
| I-02 | Adjusted metrics used to make roster decisions | MEDIUM | HIGH | ANALYTICS_ONLY classification. CricPom is an analytical tool, not a decision system. If anyone uses these numbers to justify a trade, that is on them, not on the model. The spec does not endorse decision-making applications. |
| I-03 | Small rating differences treated as meaningful | HIGH | MEDIUM | Report the minimum detectable difference. If the standard error of CEM is 0.4 RPO, then a CEM difference of 0.2 is noise. State this explicitly. |
| I-04 | Year-over-year comparisons without re-centering | MEDIUM | MEDIUM | CricPom ratings are relative to season average. A CEM of +1.0 in 2023 is not the same as +1.0 in 2025 unless the league environment is identical. Always compare within-season ranks, not across-season raw values. |

---

## 8. Open Questions for Resolution Before Implementation

| # | Question | Owner | Required Before |
|---|----------|-------|----------------|
| 1 | Is first/second innings indicator available in the ball-by-ball schema? | Data Engineer (Brock Purdy) | Implementation start |
| 2 | Is batting position available per innings? | Data Engineer (Brock Purdy) | Phase 2 (not MVP) |
| 3 | What is the actual league-average SR and economy for IPL 2023-2025? | Analyst (pre-calculation) | Iteration engine build |
| 4 | Do we have toss data in dim_match? | Data Engineer (Brock Purdy) | Phase 2 (not MVP) |
| 5 | Should we restrict MVP to IPL only or include other T20 leagues for venue factors? | Jose Mourinho + Andy Flower | Design decision |
| 6 | What is the minimum ball threshold for a player to receive a rating? | Jose Mourinho | Implementation start |
| 7 | How do we handle players who appear in multiple leagues within the same timeframe? | Jose Mourinho | Phase 2 (not MVP) |
| 8 | Is there appetite for a "CricPom Lite" output in the next stat pack cycle? | Product (Florentino) | Post-MVP |

---

## 9. Relationship to Other IDEA Track Items

| IDEA | Relationship to CricPom | Dependency Direction |
|------|------------------------|---------------------|
| IDEA-001 (Player Clustering) | CricPom adjusted metrics could be inputs to clustering features | CricPom feeds clustering |
| IDEA-003 (PFF-Style Grading) | Process-based grading is complementary but independent. CricPom is outcome-adjusted; PFF is process-graded. | Independent. Could merge later. |
| IDEA-004 (Win Probability Model) | CricPom CEM is a natural input feature for match-level win probability | CricPom feeds win probability |
| IDEA-005 (Auction Valuation) | Adjusted player metrics from CricPom could inform player valuation | CricPom feeds valuation |

CricPom is a foundational analytics layer. It does not depend on other IDEA items, but several downstream items depend on it. This is why the Florentino Gate approved it first.

---

## 10. Summary

CricPom is a well-scoped, evidence-based adaptation of KenPom's basketball efficiency rating system for T20 cricket. The core innovations -- opponent-adjusted metrics via iterative convergence, venue normalization, and decomposition into Four Factors -- transfer cleanly from basketball to cricket with the modifications documented above.

The prototype scope is deliberately narrow: IPL 2023-2025, 10 core metrics, 30-43 hours of estimated effort, with clear validation criteria that must be met before any downstream use.

What we are NOT doing is equally important: no ball-tracking models, no process grading, no prediction engine, no product features. This is a methodology validation exercise. If the math works on 219 IPL matches, we expand. If it does not, we learn why and adjust.

I would rather build a small thing that is correct than a large thing that is impressive but wrong.

---

**Classification:** ANALYTICS_ONLY
**Approval Gate:** Florentino Gate APPROVED (IDEA-002)
**Next Action:** Resolve open questions (Section 8), then proceed to implementation ticket creation via Mission Control.

---

*Signed: Jose Mourinho*
*Quant Researcher / Data Scientist*
*Cricket Playbook Analytics Team*

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-09 | Jose Mourinho | Initial prototype specification |
