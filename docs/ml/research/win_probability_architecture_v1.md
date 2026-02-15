# Win Probability Model Architecture v1.0

**Ticket:** TKT-205
**Authors:** Ime Udoka (ML Ops), Jose Mourinho (Quant Research)
**Reviewers:** Andy Flower (Domain), Stephen Curry (Analytics)
**Status:** ARCHITECTURE DEFINED
**Date:** 2026-02-15
**Classification:** Research Document (Sprint 5 Interactive Feature)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Literature Review](#2-literature-review)
3. [Data Inventory](#3-data-inventory)
4. [Feature Set](#4-feature-set)
5. [Model Architecture](#5-model-architecture)
6. [Evaluation Metrics](#6-evaluation-metrics)
7. [Training Strategy](#7-training-strategy)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Risks and Mitigations](#9-risks-and-mitigations)
10. [Domain Sanity Review](#10-domain-sanity-review)
11. [References](#11-references)

---

## 1. Executive Summary

### What We Are Building

A ball-by-ball win probability model for IPL T20 cricket that computes
P(batting_team_wins | match_state) at every legal delivery in a completed match.
The model powers a **historical match replay visualization** in The Lab dashboard,
allowing readers to see how win probability shifted through pivotal moments in
past IPL matches.

### What We Are NOT Building

- A live prediction or in-play betting tool
- A match-outcome forecasting product
- A pre-match win predictor

This is editorial analytics -- the same class of content as ESPN's WinViz replay
graphs or FiveThirtyEight's historical game win probability charts. It enriches
the Cricket Playbook magazine by making match narratives quantifiable and visual.

### Why This Matters for Cricket Playbook

Win probability curves are the single most effective way to compress an entire
T20 innings into one visual story. A match where CSK chase 220 with Dhoni at the
crease reads differently when the win probability was 4% at the 15th over and
92% at the 19th. This model transforms our 1,169 IPL matches and 278,034 balls
into interactive narrative assets.

---

## 2. Literature Review

### 2.1 CricViz WinViz

CricViz's WinViz is the industry standard for cricket win probability. It powers
the win predictor on Sky Sports, Star Sports, and ESPNcricinfo broadcasts.

**Methodology (inferred from public disclosures):**
- Built on top of a Duckworth-Lewis-Stern (DLS) resource model as a baseline
- Maps remaining resources (balls + wickets) to expected runs
- Enhanced with AI/ML layer calibrated on "the world's most extensive cricket database"
- Accounts for current match situation, team strength, and venue history
- Recently upgraded from parametric model to AI-powered approach

**Strengths:** Proprietary dataset spanning all international and franchise cricket.
Deep integration with broadcasting (real-time updates at each delivery).

**Weaknesses (for our purposes):** Fully proprietary, no reproducibility. Designed for
live prediction with team-strength adjustments that may over-fit to recent form.
We need historical replay, not live prediction.

**Source:** [CricViz WinViz](https://cricviz.com/winviz/),
[CricViz Enhanced WinViz Launch](https://cricviz.com/cricviz-launches-enhanced-winviz-model/)

### 2.2 WASP (Winning and Score Predictor)

Developed by Dr. Scott Brooker and Dr. Seamus Hogan at the University of Canterbury
(New Zealand). First deployed on Sky Sport NZ in November 2012.

**Methodology:**
- Grounded in **dynamic programming** theory
- First innings model: estimates additional runs as f(balls_remaining, wickets_remaining)
- Second innings model: estimates P(win) as f(balls_remaining, wickets_remaining,
  runs_scored, target)
- Incorporates pitch/weather/boundary size as adjustments
- Assumes "average team vs average team" -- no team-strength differentiation
- Database: all non-shortened ODI and T20 games between top-8 nations since 2006

**Strengths:** Transparent methodology, grounded in well-understood DLS resource theory.
Clean separation of 1st vs 2nd innings models.

**Weaknesses:** No team-strength adjustment. No player-level features. Dynamic
programming approach is elegant but limited in feature dimensionality.

**Source:** [WASP Wikipedia](https://en.wikipedia.org/wiki/WASP_(cricket_calculation_tool)),
[WASP Working Explained](https://www.sportskeeda.com/cricket/win-and-score-prediction-working-wasp-cricket)

### 2.3 Asif & McHale (2016) -- Dynamic Logistic Regression

The foundational academic paper: "In-play forecasting of win probability in One-Day
International cricket: A dynamic logistic regression model" (International Journal
of Forecasting, 2016).

**Methodology:**
- Dynamic logistic regression where model parameters evolve smoothly as the match
  progresses
- Reduces from 1,196 parameters to 25 parameters via dynamic approach
- Separate models for 1st and 2nd innings
- Validated using leave-one-out cross-validation
- Calibrated against betting market probabilities

**Key Finding:** Model forecasts are quantitatively similar to betting market
probabilities, validating the approach without requiring team-strength variables.

**Strengths:** Statistically rigorous, interpretable, well-calibrated.

**Weaknesses:** ODI-focused (not T20). Logistic regression limits feature interactions.
Published in 2016, predates modern gradient boosting approaches.

**Source:** [Asif & McHale 2016 (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0169207015000618)

### 2.4 Recent Academic Work (2024-2025)

Multiple recent papers have applied ML to T20 match outcome prediction:

- **Chakraborty et al. (2024):** "Cricket data analytics: Forecasting T20 match
  winners through machine learning" (Knowledge-based and Intelligent Engineering
  Systems). Tested RF, SVM, Naive Bayes, Neural Nets, Decision Trees, XGBoost, KNN
  on 458 T20I matches. **Random Forest and Decision Tree models were most accurate
  and reliable.**

- **ScienceDirect (2024):** "Optimal model for predicting highest runs chase outcomes
  in T-20 international cricket using modern classification algorithms." Focus on
  2nd innings chases specifically.

- **IPL-specific study:** Random Forest on comprehensive player statistics (matches
  played, batting/bowling averages, fielding contributions) to predict IPL 2024
  outcomes.

**Key consensus across recent literature:**
1. Ensemble methods (Random Forest, XGBoost) consistently outperform single models
2. Ball-by-ball features dominate pre-match features for in-play prediction
3. Wickets-in-hand and required run rate are the two most important features
4. Calibration (not just accuracy) is the critical evaluation dimension

### 2.5 Cross-Sport Analogues

- **ESPN Win Probability (NFL/NBA):** Uses logistic regression trained on historical
  play-by-play. Score differential, time remaining, possession, and field position
  are primary features. Published methodology, widely replicated.

- **FiveThirtyEight (now archived):** Elo-based pre-game priors updated with in-game
  state via logistic regression. Known for excellent calibration.

- **Part-Time Analyst T20 WPA:** Open-source T20 Win Probability Added model.
  Uses balls remaining, wickets in hand, runs scored, and target as core features.
  XGBoost-based. Demonstrated that T20 win probability is dominated by the "resources
  remaining" concept from DLS.

**Source:** [T20 Win Probability Added](https://theparttimeanalyst.com/2020/06/20/twenty20-win-probability-added/)

### 2.6 Literature Review Summary

| Model | Type | Key Features | Team Strength? | Calibration |
|-------|------|-------------|----------------|-------------|
| CricViz WinViz | ML (proprietary) | DLS + AI | Yes | Unknown |
| WASP | Dynamic Programming | Balls, wickets, target | No | Implicit |
| Asif & McHale | Dynamic Logistic Reg | 25 dynamic params | No | vs Betting Market |
| Academic 2024 | RF/XGBoost | Player stats + match state | Varies | Accuracy-focused |
| ESPN (NFL/NBA) | Logistic Regression | Score, time, possession | Pre-game Elo | Excellent |

**Our approach:** Gradient boosted trees (XGBoost/LightGBM) with match-state features
as the primary model, incorporating team/player quality indices as secondary features.
This combines the interpretability of the DLS-resource framework with the flexibility
of modern ML. For historical replay, we do NOT need team-strength predictions --
we can use actual match data.

---

## 3. Data Inventory

### 3.1 Primary Table: `fact_ball`

The core training data source. Each row represents one delivery in a match.

| Column | Type | Description | Win Prob Relevance |
|--------|------|-------------|-------------------|
| `ball_id` | VARCHAR | Unique delivery ID | Row identifier |
| `match_id` | VARCHAR | Match identifier | Group-by key for labels |
| `innings` | BIGINT | Innings number (1 or 2) | Critical: model behavior differs by innings |
| `over` | BIGINT | Over number (0-19) | Core feature: time remaining |
| `ball` | BIGINT | Ball within over (1-6+) | Fine-grained time |
| `ball_seq` | BIGINT | Sequential ball number | Monotonic time index |
| `batting_team_id` | VARCHAR | Team batting | Join key for team features |
| `bowling_team_id` | VARCHAR | Team bowling | Join key for team features |
| `batter_id` | VARCHAR | Batter on strike | Join key for player quality |
| `bowler_id` | VARCHAR | Active bowler | Join key for bowler quality |
| `non_striker_id` | VARCHAR | Non-striker | Partnership context |
| `batter_runs` | BIGINT | Runs off bat | Cumulative score computation |
| `extra_runs` | BIGINT | Extras | Cumulative score computation |
| `total_runs` | BIGINT | Total delivery runs | Cumulative score computation |
| `extra_type` | VARCHAR | Wide/no-ball/bye/etc. | Legal ball filtering |
| `is_wicket` | BOOLEAN | Wicket fell | Cumulative wickets computation |
| `wicket_type` | VARCHAR | Dismissal mode | Wicket context |
| `player_out_id` | VARCHAR | Dismissed player | Quality of dismissed batter |
| `is_legal_ball` | BOOLEAN | Legal delivery flag | Ball count filtering |
| `match_phase` | VARCHAR | powerplay/middle/death | Phase classification |

**Volume:** 2,166,065 total balls across all tournaments; 278,034 IPL-specific balls.

### 3.2 Dimension Tables

| Table | Key Columns | Win Prob Use |
|-------|-------------|-------------|
| `dim_match` | winner_id, toss_winner_id, toss_decision, venue_id, season, stage, outcome_type | Label source (winner), toss features, venue join, match context |
| `dim_venue` | venue_id, venue_name, city | Venue join key |
| `dim_team` | team_id, team_name | Team identity |
| `dim_player` | player_id, primary_role, matches_played | Player quality proxy |
| `dim_bowler_classification` | player_id, bowling_style | Bowling type feature |
| `fact_player_match_performance` | batting_position, did_bat, did_bowl | Batting order context |

### 3.3 Pre-Computed Analytics Views

These provide pre-aggregated features that can be joined at training time:

| View | Key Metrics | Feature Use |
|------|-------------|-------------|
| `analytics_ipl_venue_profile_alltime` | run_rate, boundary_pct, wickets_per_match, dot_ball_pct by venue/innings/phase | Venue bias features |
| `analytics_ipl_innings_progression_alltime` | cumulative_runs, cumulative_wickets, run_rate, required_run_rate by match/over | Core match state (over-level) |
| `analytics_ipl_team_phase_scoring_alltime` | team run_rate, boundary_pct, dot_ball_pct by phase | Team strength by phase |
| `analytics_ipl_batter_phase_alltime` | Batter SR, average by phase | Batter quality index |
| `analytics_ipl_bowler_phase_alltime` | Bowler economy, wickets by phase | Bowler quality index |
| `analytics_ipl_match_context_alltime` | Full match context: scores, toss, winner | Match-level features |

### 3.4 Data Volume Assessment

| Metric | Value |
|--------|-------|
| IPL matches (2008-2025) | 1,169 |
| IPL balls (legal + extras) | 278,034 |
| Avg balls per match | ~238 |
| Training samples (ball-level) | ~278,000 |
| Distinct venues | 63 |
| Seasons | 18 (2007/08 - 2025) |
| Matches with ties | 15 (1.3%) |
| No results | 8 (0.7%) |
| Outcome: chasing team wins (wickets) | 52.6% |
| Outcome: batting first wins (runs) | 45.4% |
| Average 1st innings score | 167.0 |
| Average 2nd innings score | 153.5 |

**Assessment:** 278K ball-level samples from 1,169 matches is a strong training set
for gradient boosted trees. The IPL-only focus provides consistency in competition
quality while spanning 18 seasons of evolution.

### 3.5 Optional: T20 Augmentation Pool

If IPL-only proves insufficient, we have access to additional T20 data:

| Tournament | Matches | Quality Tier |
|-----------|---------|-------------|
| Big Bash League | 662 | High |
| Vitality Blast | 835 | Medium-High |
| Caribbean Premier League | 407 | Medium |
| Pakistan Super League | 314 | Medium |
| SA20 | 130 | High |
| ICC T20 World Cup | 124 | High |
| **Total T20 pool** | **~9,500** | Mixed |

**Recommendation:** Train on IPL-only first. If calibration is poor in specific
match phases, consider augmenting with BBL/CPL/SA20 data with a tournament-weight
decay factor.

---

## 4. Feature Set

Features are organized into 8 categories. Each feature is derived from `fact_ball`
and dimension tables using SQL window functions computed at each delivery.

### 4.1 Core Match State (Highest Importance -- Expected)

These features encode the DLS-equivalent "resources remaining" concept.

| Feature | Formula | Type | Innings |
|---------|---------|------|---------|
| `cumulative_runs` | SUM(total_runs) OVER (PARTITION BY match_id, innings ORDER BY ball_seq) | INT | Both |
| `wickets_fallen` | SUM(is_wicket) OVER (PARTITION BY match_id, innings ORDER BY ball_seq) | INT (0-10) | Both |
| `legal_balls_bowled` | SUM(is_legal_ball) OVER (...) | INT (0-120) | Both |
| `balls_remaining` | 120 - legal_balls_bowled | INT | Both |
| `current_run_rate` | cumulative_runs / (legal_balls_bowled / 6.0) | FLOAT | Both |
| `resources_remaining` | f(balls_remaining, wickets_remaining) -- DLS-inspired | FLOAT | Both |
| `runs_remaining` | chase_target - cumulative_runs | INT | 2nd only |
| `required_run_rate` | runs_remaining / (balls_remaining / 6.0) | FLOAT | 2nd only |
| `run_rate_pressure` | required_run_rate - current_run_rate | FLOAT | 2nd only |
| `is_second_innings` | innings == 2 | BOOL | Both |
| `first_innings_total` | Total from innings 1 (set at start of innings 2) | INT | 2nd only |

**DLS Resources Remaining Approximation:**
We implement a simplified DLS resource percentage as a single feature:
`resources_pct = f(balls_remaining, 10 - wickets_fallen)`
using the standard DLS resource table. This gives the model a strong prior on
match state without manually engineering dozens of interaction features.

### 4.2 Phase Context

| Feature | Formula | Type |
|---------|---------|------|
| `match_phase` | powerplay (0-5) / middle (6-14) / death (15-19) | CATEGORICAL |
| `over_number` | over (0-19) | INT |
| `ball_in_over` | ball (1-6) | INT |
| `phase_progress` | Position within current phase (0.0-1.0) | FLOAT |
| `is_powerplay` | over < 6 | BOOL |
| `is_death` | over >= 15 | BOOL |

### 4.3 Batting Strength (Pre-Computed)

These are looked up from historical analytics views, NOT computed in real-time.
They represent the batting team's general quality entering the match.

| Feature | Source | Type |
|---------|--------|------|
| `batting_team_phase_sr` | analytics_ipl_team_phase_scoring | FLOAT |
| `batting_team_phase_rr` | analytics_ipl_team_phase_scoring | FLOAT |
| `batting_team_boundary_pct` | analytics_ipl_team_phase_scoring | FLOAT |
| `current_batter_career_sr` | analytics_ipl_batter_phase | FLOAT |
| `current_batter_phase_sr` | analytics_ipl_batter_phase (filtered to current phase) | FLOAT |
| `non_striker_career_sr` | analytics_ipl_batter_phase | FLOAT |
| `wickets_in_hand_quality` | Weighted SR of batters yet to bat | FLOAT |

**`wickets_in_hand_quality` computation:**
For each ball, we know which batters have been dismissed. The remaining batting
lineup quality is estimated as the average career strike rate of batters who
have not yet batted, weighted by their historical balls-faced volume.

### 4.4 Bowling Strength (Pre-Computed)

| Feature | Source | Type |
|---------|--------|------|
| `bowling_team_phase_economy` | analytics_ipl_team_phase_scoring (bowling perspective) | FLOAT |
| `bowling_team_phase_wickets_per_match` | analytics_ipl_bowler_phase | FLOAT |
| `current_bowler_economy` | analytics_ipl_bowler_phase | FLOAT |
| `current_bowler_phase_economy` | analytics_ipl_bowler_phase (filtered to phase) | FLOAT |
| `current_bowler_sr` | analytics_ipl_bowler_phase (balls per wicket) | FLOAT |
| `bowler_type` | dim_bowler_classification.bowling_style | CATEGORICAL |

### 4.5 Venue Bias

| Feature | Source | Type |
|---------|--------|------|
| `venue_avg_1st_innings_score` | analytics_ipl_venue_profile + match_context | FLOAT |
| `venue_run_rate_phase` | analytics_ipl_venue_profile (current phase) | FLOAT |
| `venue_boundary_pct` | analytics_ipl_venue_profile | FLOAT |
| `venue_wickets_per_match` | analytics_ipl_venue_profile | FLOAT |
| `venue_chasing_win_pct` | Computed from match_context for this venue | FLOAT |

### 4.6 Toss Effect

| Feature | Source | Type |
|---------|--------|------|
| `toss_winner_is_batting` | dim_match.toss_winner_id == batting_team_id | BOOL |
| `chose_to_bat` | dim_match.toss_decision == 'bat' | BOOL |
| `toss_advantage_at_venue` | Historical win % when winning toss at this venue | FLOAT |

### 4.7 Momentum (Rolling Window)

Computed from the last N deliveries using window functions.

| Feature | Window | Type |
|---------|--------|------|
| `last_18_balls_run_rate` | Last 3 overs (18 legal balls) | FLOAT |
| `last_18_balls_wickets` | Wickets in last 3 overs | INT |
| `last_18_balls_dot_pct` | Dot ball % in last 3 overs | FLOAT |
| `last_18_balls_boundary_pct` | Boundary % in last 3 overs | FLOAT |
| `last_6_balls_runs` | Last over runs | INT |
| `consecutive_dots` | Current streak of dot balls | INT |
| `balls_since_boundary` | Balls since last 4 or 6 | INT |
| `balls_since_wicket` | Balls since last wicket | INT |

### 4.8 Match Context

| Feature | Source | Type |
|---------|--------|------|
| `match_stage` | dim_match.stage (group/playoff/final) | CATEGORICAL |
| `season` | dim_match.season | CATEGORICAL (for era effects) |
| `is_playoff` | stage IN ('Qualifier 1','Qualifier 2','Eliminator','Final') | BOOL |

### 4.9 Feature Summary

| Category | Feature Count | Expected Importance |
|----------|--------------|-------------------|
| Core Match State | 11 | Very High (60-70% of model) |
| Phase Context | 6 | High |
| Batting Strength | 7 | Medium |
| Bowling Strength | 6 | Medium |
| Venue Bias | 5 | Medium-Low |
| Toss Effect | 3 | Low |
| Momentum | 8 | Medium |
| Match Context | 3 | Low |
| **Total** | **49** | |

**Feature importance hypothesis (Jose Mourinho):**
Based on the literature review and DLS theory, the expected feature importance
ranking is:
1. `resources_remaining` (balls + wickets combined)
2. `required_run_rate` (2nd innings) / `cumulative_runs` (1st innings)
3. `run_rate_pressure`
4. `wickets_fallen`
5. `over_number`
6. Momentum features (recent run rate, recent wickets)
7. Player quality indices
8. Venue/toss features

This will be validated empirically via SHAP values after training.

---

## 5. Model Architecture

### 5.1 Recommended Primary Model: XGBoost / LightGBM

**Justification:**
- Gradient boosted trees are the proven best approach for tabular data with mixed
  feature types (continuous + categorical)
- XGBoost/LightGBM handle missing values natively (important for 1st innings where
  2nd-innings-only features are null)
- Built-in feature importance ranking via gain/SHAP
- Fast inference (critical for generating win prob curves for 1,169 matches)
- Well-calibrated probability outputs with proper sigmoid transformation
- Extensive literature support: RF/XGBoost consistently top-performing in all
  recent cricket prediction papers

**Specific recommendation: LightGBM** for primary training due to:
- Faster training on 278K samples
- Native categorical feature support (no one-hot encoding needed)
- Leaf-wise growth produces better calibration than level-wise

### 5.2 Two-Model Architecture

Following WASP and Asif & McHale, we split into two models:

#### Model A: First Innings Win Probability
- **Input:** Match state at each delivery in innings 1
- **Target:** P(batting_team_wins_the_match)
- **Challenge:** Without a target score, first innings win prob is about
  "are you building a winning total?" This is harder and inherently noisier.
- **Key features:** cumulative_runs, resources_remaining, run_rate, phase,
  batting/bowling strength, venue_avg_score
- **Expected accuracy:** Lower than Model B (Brier score ~0.22-0.25)

#### Model B: Second Innings Win Probability
- **Input:** Match state at each delivery in innings 2
- **Target:** P(batting_team_wins_the_match)
- **Challenge:** Well-defined problem -- chasing a known target.
- **Key features:** runs_remaining, required_run_rate, resources_remaining,
  run_rate_pressure, momentum
- **Expected accuracy:** Higher (Brier score ~0.15-0.20)

**Why two models?** The feature space is fundamentally different. In innings 1,
there is no target, no required run rate, no run_rate_pressure. Forcing a single
model to handle both leads to feature leakage or null-value complexity. Two models
with shared preprocessing logic is cleaner and more interpretable.

### 5.3 Alternative: LSTM Sequence Model

**Architecture:** Bi-directional LSTM operating on the full ball-by-ball sequence.

| Layer | Configuration |
|-------|--------------|
| Input | Sequence of ball-level feature vectors (max length 120) |
| Embedding | Categorical features embedded (team, venue, bowler_type) |
| LSTM | 2 layers, 128 hidden units, bidirectional |
| Attention | Self-attention over delivery sequence |
| Output | Sigmoid: P(batting_team_wins) at each timestep |

**Pros:** Captures sequential dependencies (e.g., momentum shifts, partnership
building) that tree models must approximate via engineered rolling features.
Can learn non-obvious patterns in ball sequences.

**Cons:** Requires more data. Harder to interpret. Slower inference. More complex
training pipeline. For 1,169 matches (not millions), the LSTM likely overfits.

**Recommendation:** Build XGBoost/LightGBM first. If calibration analysis reveals
systematic momentum-related errors, investigate LSTM as a Phase 2 enhancement.
The LSTM is a future option, not the v1 architecture.

### 5.4 Probability Calibration

Raw model outputs from tree ensembles may not be perfectly calibrated. We apply:

1. **Platt Scaling:** Fit a logistic regression on validation-set predictions to
   map raw scores to calibrated probabilities.
2. **Isotonic Regression:** Non-parametric alternative if Platt scaling underfits.
3. **Post-hoc binning check:** Group predictions into deciles and verify that
   predicted probabilities match observed win rates.

Calibration is MORE important than accuracy for this use case. A model that says
"70% win probability" should correspond to teams winning ~70% of the time across
all such predictions.

### 5.5 Architecture Diagram

```
                   +-----------------+
                   |   fact_ball     |
                   | (278K IPL rows) |
                   +--------+--------+
                            |
                   +--------v--------+
                   | Feature Engine  |
                   | (SQL + Python)  |
                   +--------+--------+
                            |
              +-------------+-------------+
              |                           |
     +--------v--------+        +--------v--------+
     | Innings 1 Data  |        | Innings 2 Data  |
     | (no target)     |        | (with target)   |
     +--------+--------+        +--------+--------+
              |                           |
     +--------v--------+        +--------v--------+
     | Model A:        |        | Model B:        |
     | LightGBM        |        | LightGBM        |
     | 1st Inn WinProb |        | 2nd Inn WinProb |
     +--------+--------+        +--------+--------+
              |                           |
     +--------v--------+        +--------v--------+
     | Platt Scaling   |        | Platt Scaling   |
     | Calibration     |        | Calibration     |
     +--------+--------+        +--------+--------+
              |                           |
              +-------------+-------------+
                            |
                   +--------v--------+
                   | Win Prob Curve  |
                   | Generator       |
                   +--------+--------+
                            |
                   +--------v--------+
                   | The Lab         |
                   | Dashboard       |
                   +-----------------+
```

### 5.6 Hyperparameter Search Space

| Parameter | Search Range | Notes |
|-----------|-------------|-------|
| `n_estimators` | 200-1000 | Early stopping on validation |
| `max_depth` | 4-8 | Deeper for feature interactions |
| `learning_rate` | 0.01-0.1 | Lower for better calibration |
| `min_child_weight` | 5-50 | Prevent overfitting to rare states |
| `subsample` | 0.7-0.9 | Row sampling |
| `colsample_bytree` | 0.6-0.9 | Feature sampling |
| `reg_alpha` | 0-1.0 | L1 regularization |
| `reg_lambda` | 1.0-5.0 | L2 regularization |
| `scale_pos_weight` | ~1.0 | Near-balanced classes |

Optimization via Optuna with 100 trials, optimizing Brier score on validation fold.

---

## 6. Evaluation Metrics

### 6.1 Primary Metric: Brier Score

The Brier score measures calibration quality:

```
Brier = (1/N) * SUM((predicted_prob - actual_outcome)^2)
```

- Range: 0 (perfect) to 1 (worst)
- A naive "always predict 50%" gives Brier = 0.25
- Target: < 0.20 overall, < 0.17 for 2nd innings

**Why Brier over accuracy?** For win probability, we care about the quality of
probability estimates, not binary classification accuracy. A model that predicts
52% for a team that wins is "accurate" but uninformative. Brier score penalizes
overconfident wrong predictions more than underconfident ones.

### 6.2 Secondary Metrics

| Metric | Formula | Target | Purpose |
|--------|---------|--------|---------|
| Log Loss | -mean(y*log(p) + (1-y)*log(1-p)) | < 0.60 | Penalizes confident wrong predictions |
| AUC-ROC | Area under ROC curve | > 0.80 | Discrimination ability |
| Calibration Error (ECE) | Mean abs(predicted - observed) in bins | < 0.05 | Bin-level calibration |

### 6.3 Phase-Specific Evaluation

Win probability difficulty varies dramatically by match phase. We evaluate separately:

| Phase | Overs | Expected Brier | Rationale |
|-------|-------|---------------|-----------|
| Powerplay (1st inn) | 0-5 | 0.24-0.25 | Near-random; too early to predict |
| Middle (1st inn) | 6-14 | 0.22-0.24 | Some signal emerging |
| Death (1st inn) | 15-19 | 0.20-0.22 | Total becoming clearer |
| Powerplay (2nd inn) | 0-5 | 0.22-0.24 | Target known but early |
| Middle (2nd inn) | 6-14 | 0.16-0.20 | Chase taking shape |
| Death (2nd inn) | 15-19 | 0.10-0.15 | Outcome nearly determined |

### 6.4 Calibration Plot

The key visual diagnostic. For each probability bin (0-10%, 10-20%, ..., 90-100%):
- X-axis: mean predicted probability
- Y-axis: observed win rate
- Perfect calibration: points lie on the diagonal

A well-calibrated model has all points within 5 percentage points of the diagonal.
This is the single most important evaluation artifact.

### 6.5 Win Probability Curve Quality

Beyond numerical metrics, we evaluate the narrative quality of win probability
curves for specific famous matches:

- Do the curves correctly identify turning points?
- Are momentum shifts reflected (not smoothed away)?
- Does the curve reach ~100% / ~0% at the right moment?
- Are "miracle chase" matches properly shown as low-probability events?

This qualitative evaluation is performed by Andy Flower (domain review) on a
curated set of 20 memorable IPL matches.

---

## 7. Training Strategy

### 7.1 Data Split

| Split | Seasons | Matches | Balls | Purpose |
|-------|---------|---------|-------|---------|
| Train | 2008-2023 | ~976 | ~232K | Model training |
| Validation | 2024 | ~71 | ~17K | Hyperparameter tuning |
| Test | 2025 | ~74 | ~18K | Final evaluation (HELD OUT) |

**Why season-based splits?** Random ball-level splits would leak information
(balls from the same match in train and test). Season-based splits also test
the model's ability to generalize across cricket's evolution (rule changes,
Impact Player rule, etc.).

### 7.2 Cross-Validation

5-fold cross-validation grouped by season for hyperparameter tuning:

| Fold | Train Seasons | Val Seasons |
|------|--------------|-------------|
| 1 | 2012-2023 | 2008-2011 |
| 2 | 2008-2011, 2016-2023 | 2012-2015 |
| 3 | 2008-2015, 2020-2023 | 2016-2019 |
| 4 | 2008-2019, 2023 | 2020-2022 |
| 5 | 2008-2022 | 2023 |

Grouped-by-season ensures no data leakage. Each fold trains on 4 era groups
and validates on 1, testing robustness across different IPL eras.

### 7.3 Label Construction

| Scenario | Label | Handling |
|----------|-------|---------|
| Batting team wins | 1.0 | Standard |
| Batting team loses | 0.0 | Standard |
| Tie (Super Over) | Use Super Over result | 15 matches |
| No Result | **Exclude** from training | 8 matches |
| DLS match | Include but flag | Rare in IPL |

**Tie handling detail:** In IPL ties that go to Super Over, the label is based on
the Super Over winner. The regular-innings win probability curve should reflect
that neither team had a decisive advantage, naturally producing curves that
converge toward 50% as the match heads to a tie.

### 7.4 Feature Engineering Pipeline

```
Step 1: Ball-level cumulative features (SQL window functions)
        - cumulative_runs, cumulative_wickets, legal_balls_bowled

Step 2: DLS resource mapping (Python lookup table)
        - Map (balls_remaining, wickets_in_hand) -> resource_pct

Step 3: Rolling momentum features (SQL window functions)
        - last_18_balls_run_rate, consecutive_dots, etc.

Step 4: Pre-match static features (JOIN to dim tables + analytics views)
        - venue_profile, team_phase_scoring, player quality indices

Step 5: Feature assembly (Python pandas/polars DataFrame)
        - Merge all feature groups
        - Handle nulls (1st innings: null target features)
        - Encode categoricals (LightGBM native or ordinal)

Step 6: Train/val/test split by season
```

### 7.5 Class Balance

IPL outcomes are near-balanced:
- Batting first wins (runs): 45.4%
- Chasing team wins (wickets): 52.6%
- Ties: 1.3%

At the ball level, the class distribution depends on innings. In innings 1,
~47% of balls belong to eventually-winning teams. In innings 2, ~53% of balls
belong to eventually-winning teams (because chasing teams win slightly more often).

**No resampling needed.** The slight imbalance is natural and informative.

### 7.6 Handling IPL Evolution

The IPL has changed significantly across 18 seasons:
- 2008-2012: Lower scoring, 130-150 average first innings
- 2013-2017: Run rate inflation begins
- 2018-2022: Consistently 170+ average first innings
- 2023-2025: Impact Player rule, even higher scoring (167+ avg)

**Strategy:** Include `season` as a feature (ordinal encoded) so the model learns
era-dependent scoring patterns. Additionally, apply time-weighted sampling:
more recent seasons receive higher weight (exponential decay with half-life of
4 seasons).

---

## 8. Implementation Roadmap

### Phase 1: Feature Engineering (TKT-206)

**Owner:** Stephen Curry (Analytics) + Brock Purdy (Data Pipeline)
**Estimated effort:** Deep Work
**Deliverables:**
- SQL script: `scripts/ml/win_prob_features.sql` -- all fact_ball window functions
- Python script: `scripts/ml/win_prob_feature_pipeline.py` -- full feature assembly
- Feature validation: statistical distributions, null rates, correlation matrix
- DLS resource lookup table implementation
- Output: `data/ml/win_prob_features.parquet` (one row per legal delivery)

### Phase 2: Model Training + Evaluation (TKT-207)

**Owner:** Ime Udoka (ML Ops) + Jose Mourinho (Quant)
**Estimated effort:** Deep Work
**Deliverables:**
- Training script: `scripts/ml/win_prob_train.py`
- Two trained models: `models/win_prob_innings1_v1.lgbm`, `models/win_prob_innings2_v1.lgbm`
- Calibration module: Platt scaling fitted on validation set
- Evaluation report: Brier score, log loss, calibration plots, SHAP analysis
- Phase-specific performance breakdown
- Qualitative review on 20 curated matches (Andy Flower)

### Phase 3: Curve Generation + Dashboard Integration (TKT-208)

**Owner:** Kevin De Bruyne (Visualization) + Brad Stevens (Architecture)
**Estimated effort:** Deep Work
**Deliverables:**
- Batch inference script: generate win prob curves for all 1,169 IPL matches
- Output: `data/ml/win_prob_curves.json` (one entry per match, array of ball-level probs)
- The Lab dashboard component: interactive win probability chart
  - X-axis: ball number (0-240)
  - Y-axis: batting team win probability (0-100%)
  - Hover: show ball details (batter, bowler, runs, wicket)
  - Vertical line at innings break
  - Color-coded by match phase
- Match selector: dropdown to pick any historical IPL match

### Phase 4: Editorial Integration (TKT-209)

**Owner:** Virat Kohli (Narrative) + LeBron James (Social)
**Estimated effort:** Standard Work
**Deliverables:**
- Win probability annotations for key moments in season preview narratives
- "Signature Moments" section: top-10 most dramatic win probability swings per team
- Social card format: single-match win probability curves for shareable content

### Timeline Estimate

| Phase | Tickets | Sprint | Duration |
|-------|---------|--------|----------|
| Phase 1: Feature Engineering | TKT-206 | Sprint 5 | Week 1-2 |
| Phase 2: Training + Evaluation | TKT-207 | Sprint 5 | Week 2-3 |
| Phase 3: Dashboard Integration | TKT-208 | Sprint 5-6 | Week 3-4 |
| Phase 4: Editorial Integration | TKT-209 | Sprint 6 | Week 4-5 |

---

## 9. Risks and Mitigations

### 9.1 Statistical Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| **Small sample per venue** | Medium | High | Pool similar venues by scoring profile; use venue-cluster features instead of venue-specific |
| **Small sample per player** | Medium | High | Use career aggregates with minimum ball thresholds (from thresholds.yaml: 300 balls batter, 200 balls bowler); fallback to team-average for low-volume players |
| **First innings model noise** | High | High | Accept higher Brier score for innings 1; use DLS resource curve as strong baseline |
| **Season drift** | Medium | Medium | Time-weighted training; include season as feature; retrain annually |
| **Overfitting to IPL-specific patterns** | Medium | Low | Cross-validation by season; regularization; optional T20 augmentation |

### 9.2 Data Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| **Missing player quality data** | Low | Medium | Graceful null handling; team-average fallback |
| **DLS matches** | Low | Low | Flag and handle; fewer than 5 IPL matches affected |
| **Impact Player rule (2023+)** | Medium | Certain | Include as binary feature; may need separate evaluation for 2023+ era |
| **Venue changes over time** | Medium | Medium | Use rolling 3-season venue profiles rather than all-time |

### 9.3 Product Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| **Model perceived as "betting tool"** | High | Low | Explicit disclaimers; historical replay only; no future predictions |
| **Poor calibration undermines credibility** | High | Medium | Extensive calibration analysis; publish Brier scores transparently |
| **Win prob curves are boring for one-sided matches** | Medium | Medium | Curate "most dramatic" matches; highlight swing moments |
| **Inference latency for 1,169 matches** | Low | Low | Batch pre-compute all curves; store as static JSON |

### 9.4 Technical Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|-----------|------------|
| **Feature leakage** | High | Medium | Strict temporal ordering; no future-ball information in features |
| **Probability boundary behavior** | Medium | Medium | Ensure P approaches 1.0 / 0.0 correctly at match end; clip to [0.001, 0.999] during training |
| **Model size for dashboard** | Low | Low | LightGBM models are <10MB; pre-computed curves are ~50MB JSON |

---

## 10. Domain Sanity Review

### 10.1 Jose Mourinho -- Quant Research Review

**Statistical Methodology: SOUND**

The two-model architecture (split by innings) is well-justified by the fundamental
asymmetry of the prediction problem. In the first innings, without a target, the
model must implicitly learn what constitutes a "par score" -- this is genuinely
harder and the expected Brier scores reflect that reality.

The feature set is comprehensive without being bloated. 49 features for 278K samples
gives a healthy feature-to-sample ratio of ~1:5,700. The DLS resource percentage
as a single composite feature is an elegant way to inject domain knowledge without
over-constraining the model.

**Evaluation metrics: APPROPRIATE**

Brier score as the primary metric is the correct choice for probability calibration.
Log loss as a secondary metric provides additional sensitivity to confident wrong
predictions. The phase-specific breakdown will reveal if the model is genuinely
useful or merely predicting the obvious (death overs in 2nd innings are easy).

**Key concern:** The first innings model may degenerate to a "runs scored vs par"
regressor that only becomes meaningful after over 10. Early first-innings predictions
(overs 0-5) may be indistinguishable from a coin flip. This should be documented
honestly rather than presented as a model weakness.

**Season-grouped cross-validation** is essential and correctly specified. The
exponential time-weighting (half-life = 4 seasons) is a reasonable prior that
should be validated empirically.

### 10.2 Andy Flower -- Cricket Domain Review

**Cricket Feature Coverage: COMPREHENSIVE**

The feature set captures the critical dimensions of T20 match outcomes:

1. **Resources remaining (balls + wickets):** This is the single most important
   concept in limited-overs cricket. The DLS resource mapping is correct.

2. **Required run rate / pressure:** The difference between current RR and required
   RR is the defining tension of a T20 chase. Well captured.

3. **Momentum features (last 3 overs):** Cricket is a momentum sport. A spell of
   3 wickets in 2 overs completely transforms a match. The 18-ball rolling window
   is appropriate (3 overs = roughly one bowling spell).

4. **Phase-specific evaluation:** This is critical. The powerplay, middle, and death
   overs are genuinely different games with different tactics, strike rates, and
   risk profiles. Evaluating separately will reveal model strengths.

**What the feature set correctly omits:**
- Ball-by-ball line/length data (not in our dataset)
- Weather conditions (not reliably available)
- Pitch deterioration over time (not quantifiable from our data)

**What could be added in v2 (not v1):**
- Partnership duration (balls faced together by current pair)
- Batter's current innings score and SR (in-match form, not career)
- Left-hand/right-hand matchup with current bowler
- Powerplay field restriction implications on scoring patterns

**Qualitative evaluation set:** The 20-match curated review should include:
- A record chase (e.g., RCB 263 vs PWI 2013)
- A last-ball thriller
- A dominant batting-first victory
- A low-scoring death bowling masterclass
- A Super Over match
- At least 2 playoff/final matches

**Overall assessment:** The architecture is sound for a v1 editorial feature.
The two-model split, feature set, and evaluation framework align with how
cricket analysts think about match dynamics.

---

## 11. References

### Academic Papers
1. Asif, M. & McHale, I.G. (2016). "In-play forecasting of win probability in
   One-Day International cricket: A dynamic logistic regression model."
   *International Journal of Forecasting*, 32(3), 862-873.
   [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0169207015000618)

2. Chakraborty, S. et al. (2024). "Cricket data analytics: Forecasting T20 match
   winners through machine learning." *Knowledge-based and Intelligent Engineering
   Systems*, 28(1).
   [SAGE](https://journals.sagepub.com/doi/full/10.3233/KES-230060)

3. Brooker, S. & Hogan, S. (2012). WASP: Winning and Score Predictor.
   University of Canterbury, New Zealand.
   [Wikipedia](https://en.wikipedia.org/wiki/WASP_(cricket_calculation_tool))

### Industry Models
4. CricViz WinViz. [https://cricviz.com/winviz/](https://cricviz.com/winviz/)
5. CricViz Enhanced WinViz Launch.
   [https://cricviz.com/cricviz-launches-enhanced-winviz-model/](https://cricviz.com/cricviz-launches-enhanced-winviz-model/)

### Open Source
6. "Twenty20 Win Probability Added." The Part-Time Analyst (2020).
   [https://theparttimeanalyst.com/2020/06/20/twenty20-win-probability-added/](https://theparttimeanalyst.com/2020/06/20/twenty20-win-probability-added/)

### Cross-Sport
7. ESPN Win Probability methodology (NFL/NBA).
8. FiveThirtyEight Elo + in-game model (archived).

---

## Appendix A: DLS Resource Table (Simplified)

Standard DLS resource percentages for T20 (20 overs):

| Wickets Lost | 20 overs | 15 overs | 10 overs | 5 overs | 1 over |
|-------------|----------|----------|----------|---------|--------|
| 0 | 100.0% | 83.2% | 62.4% | 35.9% | 8.6% |
| 1 | 95.0% | 80.3% | 61.0% | 35.4% | 8.6% |
| 2 | 87.5% | 75.9% | 58.5% | 34.6% | 8.5% |
| 3 | 77.8% | 69.5% | 54.8% | 33.2% | 8.4% |
| 5 | 55.8% | 52.5% | 43.7% | 28.5% | 7.9% |
| 7 | 32.6% | 31.8% | 28.5% | 21.2% | 6.8% |
| 9 | 10.5% | 10.5% | 10.3% | 9.2% | 4.4% |

These values will be interpolated for ball-level granularity using cubic spline
interpolation to create the `resources_remaining` feature.

---

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| Brier Score | Mean squared error between predicted probability and binary outcome |
| DLS | Duckworth-Lewis-Stern method for rain-affected matches |
| ECE | Expected Calibration Error -- average gap between predicted and observed probabilities in bins |
| LightGBM | Light Gradient Boosting Machine -- Microsoft's fast gradient boosting framework |
| SHAP | SHapley Additive exPlanations -- feature importance via game theory |
| WPA | Win Probability Added -- change in win probability attributed to a single event |
| XGBoost | eXtreme Gradient Boosting -- Chen & Guestrin's gradient boosting framework |

---

*Document produced under TKT-205 governance.*
*Ime Udoka (ML Ops) + Jose Mourinho (Quant Research)*
*Cricket Playbook v5.0.0*
