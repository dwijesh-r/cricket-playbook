# PFF (Pro Football Focus) Grading System Research

**Author:** Ime Udoka, ML Ops Engineer
**Date:** January 26, 2026
**Purpose:** Examine PFF methodology for potential application to Cricket Playbook

---

## Executive Summary

Pro Football Focus (PFF) changed how player evaluation works in American football through their systematic, play-by-play grading methodology. Their approach offers valuable lessons for cricket analytics, particularly in isolating individual contributions, contextualizing performance, and creating meaningful composite metrics.

This document synthesizes research findings and proposes actionable applications for Cricket Playbook's player evaluation system.

---

## 1. What is PFF Grading?

### 1.1 The Grading Scale

PFF uses a **two-tier grading system**:

#### Play-Level Grades: -2 to +2 Scale
- Each player receives a grade from **-2 to +2 in 0.5 increments** on every play
- **0 represents "expected" performance** - a player doing their job at a reasonable level
- Most plays feature many players earning neutral (0) grades
- Scale captures catastrophic failures (-2) to exceptional plays (+2)

| Grade | Meaning |
|-------|---------|
| +2.0 | Elite/Exceptional play |
| +1.5 | Very good play |
| +1.0 | Good play |
| +0.5 | Above average |
| 0.0 | Expected/Average |
| -0.5 | Below average |
| -1.0 | Poor play |
| -1.5 | Very poor play |
| -2.0 | Catastrophic failure |

#### Converted Grades: 0-100 Scale
The play-level grades are aggregated and converted to a 0-100 scale for easier interpretation:

| Grade Range | Classification |
|-------------|----------------|
| 90-100 | Elite |
| 85-89 | Pro Bowler |
| 70-84 | Starter |
| 60-69 | Backup |
| 0-59 | Replaceable |

**Key Properties:**
- Mean grade is normalized to approximately **60-65**
- Standard deviation is approximately **8 points**
- Grades below 30 are extremely rare
- The distribution follows a normal bell curve

### 1.2 What Makes PFF Different from Traditional Stats

| Traditional Stats | PFF Grading |
|-------------------|-------------|
| Outcome-based (yards, TDs) | Process-based (quality of execution) |
| Credits/blames single player | Isolates individual contribution |
| Context-blind | Context-aware (situation, opponent) |
| Binary (completion/incompletion) | Granular (-2 to +2 spectrum) |
| Rewards luck | Penalizes poor decisions even if outcome is good |

**Concrete Examples:**

1. **Quarterback throws dropped interception**: Traditional stats show no INT; PFF assigns negative grade because decision was poor

2. **70-yard TD on dump-off pass**: Traditional stats credit QB with 70-yard TD; PFF gives neutral grade because the throw itself was routine

3. **4-yard run for TD**: Gets +2 (touchdown context); same 4-yard run failing to convert 3rd-and-5 gets negative grade

---

## 2. Methodology Deep Dive

### 2.1 Play-by-Play Grading Process

#### Step 1: Film Review
- Every play is reviewed using **All-22 coaches' tape** (full-field camera angle)
- Multiple camera angles examined for comprehensive view
- Graders look at player alignment, responsibilities, and off-ball actions

#### Step 2: Multi-Grader System
- **5-7 graders** work simultaneously on specific facets of each match
- Creates natural audit system through parallel grading
- Grading workload distributed to prevent same humans grading same teams (reduces bias)

#### Step 3: Quality Control Pipeline
```
First Grader --> Second Grader --> Third Grader --> Senior Analyst Review
                                                           |
                                                    Mismatch Detection
                                                           |
                                                    Algorithm Processing
                                                           |
                                                    Normal Distribution Fit
```

#### Step 4: Final Review
- Senior analysts (top 2-3% of staff) finalize grades
- Uncertain grades flagged for additional review
- Major grade checks performed regularly

### 2.2 Expert Grader Qualifications

PFF employs **600+ analysts** (full and part-time), but:
- Less than **10%** are trained to grade plays
- Top **2-3%** become senior analysts for final review
- Training requires **months to years** of preparation
- 350+ page training manual covers every scenario
- Staff includes former players, coaches, and scouts

### 2.3 Handling Context

#### Game Situation Factors
PFF collects **200+ fields of data** per play to establish baselines:

- Down and distance
- Time remaining
- Score differential
- Field position
- Formation/alignment
- Play type/concept
- Personnel groupings

#### Contextual Adjustment Framework
```
Raw Grade --> Situational Adjustment --> Normalized Grade

If situation is favorable: Grade adjusted DOWN slightly
If situation is unfavorable: Grade adjusted UP slightly
```

#### Opponent Strength
- Grades adjusted for strength of opponent
- An average FBS player has a per-play grade of zero after opponent adjustment
- Prevents inflated grades from weak competition

### 2.4 Aggregation: Play to Game to Season

#### Play to Game Aggregation
1. Sum all play-level grades
2. Apply normalization factor based on play-specific elements:
   - Depth of drop
   - QB rollouts
   - Down and distance
   - Alignment
3. Convert to 0-100 scale using percentile rank

#### Game to Season Aggregation
**Important:** Season grade is NOT simply an average of game grades

- Season grade reflects **entire body of work**
- 16 games of 80.0 grades = outstanding consistency = potentially top season historically
- A player can have a **season grade higher than their highest game grade**
- Sustained excellence is valued over sporadic brilliance

#### Small Sample Size Handling
- **Half-saturation point** calculated to prevent small samples from skewing rankings
- Player with 2 shots in a season shouldn't rank at top/bottom
- Mean and standard deviation adjusted based on sample size

---

## 3. Key Innovations

### 3.1 Expected vs Actual Performance

PFF developed the **WAR (Wins Above Replacement)** model:

#### How WAR Works
1. **Measure quality** using PFF grades
2. **Map production to wins** using relative importance of each facet
3. **Simulate team performance** with player vs. with average replacement
4. **Calculate difference** = Wins Above Replacement

#### Technical Framework (Massey Matrix)
```python
# Pseudocode representation
team_strength_vector = ML_model(facet_weights) * player_grades
simulated_wins_with_player = simulate_season(team_with_player)
simulated_wins_with_replacement = simulate_season(team_with_avg_player)
WAR = mean(simulated_wins_with_player - simulated_wins_with_replacement)
```

#### Validation
- **Spearman correlation: 0.74** for players with 250+ snaps year-to-year
- More stable than traditional or advanced performance measures
- Quarterback WAR is the most stable positional metric

### 3.2 Position-Specific Grading Criteria

Each position has **custom grading rubrics**:

#### Quarterbacks
- Focus: Timing, decision-making, accuracy
- Throw quality graded independently of result
- Dropped picks still count as negative grades
- Isolates QB contribution from receiver/line performance

#### Running Backs
- Separates runner's work from blocker's work
- Adjustments for:
  - Run concept
  - Down and distance
  - Quality of blocking
  - Defenders in box
- Fumble impact weighted by game situation

#### Offensive Linemen
- **Two separate grades**: Pass-blocking and run-blocking
- Per-snap efficiency matters most
- Consistency valued over highlight plays
- Zero-sum with defensive linemen (positive for one = negative for other)

#### Pass Rushers (Credit-Based System)
- Best rushers expected to win at high rate
- Each play assigned difficulty level based on:
  - Down and distance
  - QB dropback depth
  - Pass concept
- Failure to win = fractional negative based on expectations

### 3.3 Isolation of Individual Contribution

PFF's core philosophy: **Grade contribution to production, not the production itself**

#### Techniques for Isolation

1. **Film Analysis**: Determine each player's assignment/responsibility
2. **Expected Value Framework**: What would average player do in same situation?
3. **Independent Outcome Grading**: Grade throw quality regardless of catch/drop
4. **Scheme Agnosticism**: Don't care about player reputation or team system

#### Example: Running Back Isolation
```
Observed: 15-yard run
Traditional: +15 yards credited to RB

PFF Analysis:
- Offensive line created 10-yard gap
- RB broke one tackle (+0.5)
- RB made good cut (+0.5)
- Expected outcome given blocking: 12 yards
- RB contribution: +3 yards above expected
- Grade: +1.0
```

### 3.4 Weighting Schemes

#### Per-Snap Efficiency Metrics

**Pass Blocking Efficiency (PBE)**:
- Pressures allowed per snap
- **Weighted towards sacks** (sacks more impactful than hurries)

**Run Stop Percentage**:
- Defensive stops per snap in run defense
- Normalizes for playing time differences

**Yards Per Route Run**:
- Receiving yards per route run
- Identifies true game-changers vs. volume receivers

#### Facet Weighting for WAR
Machine learning model determines how each facet maps to wins:
- Passing offense contribution to wins
- Run defense contribution to wins
- Special teams contribution to wins
- Etc.

---

## 4. Technical Implementation

### 4.1 Data Collection Methods

#### Manual Data Collection
- 200+ fields captured per play
- Human graders watch every snap
- All-22 film (full-field view) is primary source
- Multiple camera angles cross-referenced

#### Automated Data Collection
- Partnership with **Sportlogiq** for player tracking data
- Computer vision and machine learning for position tracking
- Combines tracking data with human grades

### 4.2 Technology Stack

- **Cloud Provider**: AWS (official provider since 2019)
- **Services Used**: Compute, storage, database, serverless, analytics, ML
- **PFF IQ Product**: Data science + ML + computer vision + player tracking

### 4.3 AI/ML Applications

#### Key Insights (Launched January 2025)
AI-powered matchup analysis tool with three components:

1. **Predictive Modeling**: Data scientists develop models for outlier metrics and predictive behaviors
2. **Expert Analysis**: Human analysts identify player vs. unit matchup scenarios
3. **AI-Generated Narratives**: LLM synthesizes data and analysis into natural language

#### Model Architecture (Inferred)
```
Input Features:
- Play-by-play grades (-2 to +2)
- Situational context (200+ fields)
- Historical performance data
- Player tracking data

Processing:
- Normalization algorithms
- Percentile rank calculation
- Smoother formula for sample size adjustment
- Facet weighting optimization

Output:
- 0-100 grades per player per facet
- WAR calculations
- Predictive matchup insights
```

### 4.4 Handling Subjectivity vs Objectivity

#### Subjectivity Sources
- Assignment determination (can't always know player's responsibility)
- Grade assignment for ambiguous situations
- Coverage of untargeted receivers (can't grade "getting open" without target)

#### Objectivity Measures
1. **Standardized Training**: 350+ page manual for all scenarios
2. **Multi-Grader Auditing**: 5-7 graders per facet, parallel processing
3. **Senior Review**: Top analysts verify contested grades
4. **Rotation Policy**: Graders don't consistently grade same teams
5. **Algorithm Normalization**: Statistical processing removes individual bias
6. **Default to Neutral**: Uncertain situations default to 0 grade

### 4.5 Validation Approaches

#### Internal Validation
- Routine grader audits
- Mismatch detection between graders
- Quality control team reviews
- Regular grading analysis

#### External Validation
- NFL coach feedback (suggests bias is "statistically insignificant")
- Year-to-year stability (r = 0.50 for wins implied by WAR)
- Correlation with team success
- Predictive accuracy for future performance

#### Known Limitations
- Cannot grade untargeted receivers/coverage players
- Cannot know assignments with 100% certainty
- Some scheme-dependent effects persist
- Small sample sizes require adjustment

---

## 5. Cricket Application Ideas

### 5.1 Ball-by-Ball Grading System

#### Proposed Scale: -2 to +2 (Following PFF Model)

**For Batters:**
| Grade | Description | Example |
|-------|-------------|---------|
| +2.0 | Exceptional shot selection and execution | Boundary off excellent delivery |
| +1.5 | Very good shot | Well-timed drive for 2-3 runs |
| +1.0 | Good shot | Rotating strike with good intent |
| +0.5 | Above average | Leaving good ball, defending well |
| 0.0 | Expected | Routine defense or leave |
| -0.5 | Below average | Mistimed shot, lucky edge |
| -1.0 | Poor | Playing wrong line, dropped catch opportunity |
| -1.5 | Very poor | Playing and missing repeatedly |
| -2.0 | Catastrophic | Wicket on poor shot selection |

**For Bowlers:**
| Grade | Description | Example |
|-------|-------------|---------|
| +2.0 | Exceptional delivery | Wicket, unplayable delivery |
| +1.5 | Very good | Beat bat, create chance |
| +1.0 | Good | Hit desired area, pressure delivery |
| +0.5 | Above average | Variation well executed |
| 0.0 | Expected | Routine delivery, nothing wrong |
| -0.5 | Below average | Slightly off target |
| -1.0 | Poor | Bad length, width offered |
| -1.5 | Very poor | Free hit opportunity created |
| -2.0 | Catastrophic | Boundary from full toss/long hop |

### 5.2 Context Factors for Cricket

#### Situational Variables (Cricket's "200+ Fields")

1. **Match Phase**
   - Powerplay (overs 1-6)
   - Middle overs (7-15)
   - Death overs (16-20)
   - First/second innings

2. **Match Situation**
   - Required run rate
   - Wickets in hand
   - Partnership situation
   - Target pressure (chasing/defending)

3. **Ball Properties**
   - Line and length (pitch map coordinates)
   - Speed
   - Movement (swing/seam/spin)
   - Bounce/trajectory

4. **Environmental Factors**
   - Pitch type and deterioration
   - Ground dimensions
   - Weather conditions
   - Altitude

5. **Opponent Quality**
   - Bowler/batter ranking/rating
   - Historical head-to-head
   - Current form

### 5.3 Phase-Specific Grading

Following PFF's position-specific approach, create **phase-specific rubrics**:

#### Powerplay Grading (Overs 1-6)
- **Batters**: Weight aggression, boundary hitting, field exploitation
- **Bowlers**: Weight dot ball percentage, wicket-taking, new ball skill

#### Middle Overs Grading (Overs 7-15)
- **Batters**: Weight rotation, risk management, boundary % maintenance
- **Bowlers**: Weight economy, spin utilization, partnership breaking

#### Death Overs Grading (Overs 16-20)
- **Batters**: Weight finishing ability, boundary conversion, calm under pressure
- **Bowlers**: Weight yorker execution, variation, wide control

### 5.4 Isolation of Individual Contribution

#### Batting Isolation
```
Observed: 6 runs off delivery
Traditional: +6 runs to batter

Cricket Playbook Analysis:
- Delivery quality: Poor (long hop, leg stump)
- Expected runs vs average batter: 4.2
- Actual runs: 6
- Batter contribution above expected: +1.8
- Grade: +0.5 to +1.0
```

#### Bowling Isolation
```
Observed: Wicket taken
Traditional: +1 wicket to bowler

Cricket Playbook Analysis:
- Delivery quality: Average
- Batter shot quality: Very poor
- Fielder contribution: Excellent catch
- Bowler contribution: 40% of wicket value
- Grade: +1.0 (not +2.0)
```

### 5.5 Expected Metrics Integration

Combine PFF concepts with existing cricket xR models:

#### Expected Runs Above Expected (xRAE)
```
xRAE = Actual Runs - Expected Runs (given delivery quality)
```

#### Expected Wickets Above Expected (xWAE)
```
xWAE = Actual Wickets - Expected Wickets (given delivery quality)
```

### 5.6 Proposed Cricket WAR Model

**Cricket Wins Added (CWA)**:

1. **Batting CWA**: Runs contributed above replacement batter
2. **Bowling CWA**: Runs prevented above replacement bowler
3. **Fielding CWA**: Catches/run-outs above replacement fielder

```python
# Conceptual model
def calculate_cricket_war(player):
    batting_contribution = (actual_runs - expected_runs_replacement) * situation_weight
    bowling_contribution = (expected_runs - actual_runs_conceded) * situation_weight
    fielding_contribution = calculate_fielding_value(catches, run_outs, misfields)

    return batting_contribution + bowling_contribution + fielding_contribution
```

---

## 6. Implementation Roadmap for Cricket Playbook

### Phase 1: Data Foundation (Months 1-2)
- Define ball-by-ball data schema (equivalent to PFF's 200+ fields)
- Create delivery quality model (xR foundation)
- Build phase-specific baseline expectations

### Phase 2: Grading System (Months 3-4)
- Develop -2 to +2 grading rubric for batters and bowlers
- Create training materials (PFF has 350+ pages)
- Build grading interface for human annotators (if needed)

### Phase 3: Aggregation & Normalization (Months 5-6)
- Implement grade aggregation (ball -> innings -> match -> season)
- Build normalization algorithms
- Create 0-100 conversion with appropriate distribution

### Phase 4: Context Modeling (Months 7-8)
- Build situational adjustment models
- Implement opponent strength adjustments
- Create phase-specific weighting schemes

### Phase 5: WAR Equivalent (Months 9-10)
- Develop Cricket Wins Added model
- Validate against match outcomes
- Test predictive accuracy

### Phase 6: AI Enhancement (Months 11-12)
- Automated delivery grading using ball-tracking data
- ML-based context adjustment optimization
- Predictive matchup analysis

---

## 7. Key Takeaways for Cricket Playbook

### What to Adopt from PFF

1. **Play-by-play granularity**: Grade every ball, not just aggregate stats
2. **Process over outcome**: Grade quality of execution, not just results
3. **Context adjustment**: Account for situation, opponent, conditions
4. **Individual isolation**: Separate batter skill from bowling quality and vice versa
5. **Rigorous methodology**: Document everything, train graders, audit regularly
6. **Multi-tier metrics**: Play grades (-2 to +2) + normalized grades (0-100)
7. **Phase-specific evaluation**: Different criteria for different game phases

### What to Adapt for Cricket

1. **Ball-tracking data**: Cricket has better automated data than football
2. **Simpler isolation**: 1v1 contest (batter vs bowler) vs 11v11 in football
3. **Natural phases**: Powerplay/middle/death vs football's continuous play
4. **Global contexts**: Multiple formats (T20/ODI/Test), diverse conditions

### Competitive Advantage Opportunities

1. First mover in **comprehensive ball-by-ball grading** for cricket
2. Integration with **ball-tracking technology** for semi-automated grading
3. **Phase-specific player ratings** (no current standard exists)
4. **Cricket WAR model** for true player value quantification

---

## References and Sources

### Primary Sources
- [PFF Player Grades](https://www.pff.com/grades)
- [PFF WAR: Modeling Player Value in American Football](https://www.sloansportsconference.com/research-papers/pff-war-modeling-player-value-in-american-football)
- [How PFF grades all positions at the NCAA and NFL levels](https://www.pff.com/news/pro-how-pff-grades-all-positions-at-the-ncaa-and-nfl-levels)
- [PFF FC's Grading System Deep Dive](https://www.blog.fc.pff.com/blog/pff-fc-grades-explained)
- [All you need to know about how PFF FC grades are calculated](https://www.pff.com/news/pff-fc-all-you-need-to-know-about-how-grades-are-calculated)

### Supporting Sources
- [Pro Football Focus - Wikipedia](https://en.wikipedia.org/wiki/Pro_Football_Focus)
- [From +2.0 to -2.0: Understanding quarterback grading](https://www.pff.com/news/nfl-quarterback-play-level-data)
- [How we grade offensive and defensive linemen](https://www.pff.com/news/pro-how-we-grade-offensive-and-defensive-linemen)
- [PFF and Sportlogiq partnership](https://www.pff.com/news/pff-and-sportlogiq-enter-partnership-to-bring-player-tracking-data-to-football-teams)
- [Introducing Key Insights: AI-Powered Matchup Analysis](https://www.pff.com/news/introducing-pff-key-insights)
- [AWS and PFF Partnership](https://press.aboutamazon.com/2019/7/pro-football-focus-selects-aws-as-its-official-cloud-and-machine-learning-provider)

### Cricket Analytics Sources
- [CricViz batting and bowling metrics](https://cricviz.com/cricviz-develops-new-batting-and-bowling-metrics-for-the-world-cup/)
- [Introducing Expected Runs - Cricket Savant](https://cricketsavant.wordpress.com/2016/12/26/introducing-expected-runs/)
- [Player Evaluation in Twenty20 Cricket](https://www.sfu.ca/~tswartz/papers/moneyball.pdf)
- [White Ball Analytics - Win Probability Model](https://www.whiteballanalytics.com/win-probability-model)
- [BEREX: Average vs Strike Rate](https://medium.com/@cricketscience/average-vs-strike-rate-part-i-introducing-berex-aa35585d152e)

---

*Document prepared for Cricket Playbook internal research. Last updated: January 26, 2026*
