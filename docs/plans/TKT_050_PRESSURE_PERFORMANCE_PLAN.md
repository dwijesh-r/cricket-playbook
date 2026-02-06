# TKT-050: Pressure Performance Section Plan

**Author:** Stephen Curry (Analytics Lead)
**Status:** AWAITING FOUNDER APPROVAL
**Created:** 2026-02-06
**Ticket:** TKT-050

---

## Executive Summary

This document outlines the plan to add a **Pressure Performance** section to Cricket Playbook stat packs. This section will analyze how players perform under high-pressure situations in T20 cricket - a key differentiator for understanding clutch performers versus flat-track bullies.

**Goal:** Identify which players elevate their game under pressure and which players falter - providing readers with actionable insights for match predictions and fantasy decisions.

---

## 1. What is Pressure Performance?

### 1.1 Definition

**Pressure Performance** measures how a player's statistics change when the match situation is tense versus when it is comfortable. A "pressure performer" maintains or improves their numbers under duress; a "pressure struggler" sees significant degradation.

### 1.2 Why It Matters for Cricket Playbook

From our PRD philosophy:
> "Cricket fans don't pay for analytics, they pay for confidence, narrative clarity and authority."

Knowing who to trust in crunch moments IS the narrative readers want. This section answers:
- Who should bat when the RRR is 12+?
- Who can defend 8 runs in the final over?
- Which players are "big-game" performers vs "flat-track bullies"?

### 1.3 Pressure Scenarios in T20 Cricket

| Scenario | Description | Impact |
|----------|-------------|--------|
| **Death Overs Chasing** | Batting in overs 16-20 while chasing | Highest batting pressure |
| **High Required Run Rate** | RRR > 10 (needing 10+ runs per over) | Increased urgency, risky shots |
| **Wickets Falling** | 3+ wickets down in powerplay, 5+ down in middle | Rebuilding under pressure |
| **Close Match Defense** | Defending < 10 runs in final over | Bowling under extreme pressure |
| **Knockout Stages** | Playoffs, eliminators, finals | Tournament pressure |
| **Target Setting (High)** | Batting first, score > 180 projected | Pressure to maximize |

---

## 2. Pressure Metrics Framework

### 2.1 What Constitutes "Pressure" in T20 Cricket

Pressure is context-dependent. We define pressure through a **Pressure Index (PI)** that considers multiple factors:

#### Batting Pressure Factors

| Factor | Low Pressure (0-2) | Medium Pressure (3-5) | High Pressure (6-10) |
|--------|-------------------|----------------------|---------------------|
| **Required Run Rate** | RRR < 7 | RRR 7-10 | RRR > 10 |
| **Wickets Down** | 0-2 wickets | 3-4 wickets | 5+ wickets |
| **Overs Remaining** | > 10 overs | 5-10 overs | < 5 overs |
| **Match Stage** | Group stage | Qualifier | Final/Eliminator |
| **Runs Required** | > 60 with > 10 overs | 30-60 with 5-10 overs | < 30 with < 3 overs |

#### Bowling Pressure Factors

| Factor | Low Pressure (0-2) | Medium Pressure (3-5) | High Pressure (6-10) |
|--------|-------------------|----------------------|---------------------|
| **Runs to Defend** | > 50 in > 5 overs | 30-50 in 3-5 overs | < 20 in < 3 overs |
| **Wickets in Hand (Opp)** | 2-3 wickets left | 4-6 wickets left | 7+ wickets left |
| **Current RRR** | Opposition RRR < 7 | RRR 7-10 | RRR > 10 |
| **Match Stage** | Group stage | Qualifier | Final/Eliminator |

### 2.2 Pressure Index Formula

```
Pressure_Index = w1 * RRR_factor + w2 * Wickets_factor + w3 * Overs_factor + w4 * Stage_factor
```

**Proposed Weights:**
- RRR_factor: 35%
- Wickets_factor: 25%
- Overs_factor: 25%
- Stage_factor: 15%

**Scale:** 0-10 (0 = no pressure, 10 = maximum pressure)

**Thresholds:**
- PI 0-3: "Low Pressure"
- PI 4-6: "Medium Pressure"
- PI 7-10: "High Pressure"

### 2.3 Simplified Binary Approach (V1 Alternative)

If the full Pressure Index is too complex for V1, we can use a **binary pressure flag** based on clear triggers:

**High Pressure Batting:**
- Chasing with RRR > 10, OR
- 5+ wickets down before over 15, OR
- Playoff/knockout match

**High Pressure Bowling:**
- Defending < 12 runs per over remaining in death, OR
- Opposition has 7+ wickets in hand chasing in death, OR
- Playoff/knockout match

---

## 3. Data Sources

### 3.1 Required Data (Already Available)

From our existing `fact_ball` table:

| Field | Usage |
|-------|-------|
| `match_id` | Link to match context |
| `innings` | 1st or 2nd innings |
| `over` | Current over (for RRR calculation) |
| `ball_seq` | Sequential position |
| `batting_team_id` | Team batting |
| `batter_id` | Player being analyzed |
| `bowler_id` | Player being analyzed |
| `total_runs` | Runs scored |
| `is_wicket` | Wicket fell |
| `batter_runs` | Runs off bat |
| `match_phase` | PP/Middle/Death (already computed) |

From `dim_match`:

| Field | Usage |
|-------|-------|
| `winner_id` | Match outcome |
| `outcome_type` | Runs/wickets |
| `outcome_margin` | How close |
| `stage` | Group/Qualifier/Final |
| `team1_id`, `team2_id` | Teams involved |

### 3.2 Derived Fields Needed (To Calculate)

| Derived Field | Calculation |
|---------------|-------------|
| `runs_required` | Target - cumulative_runs (2nd innings only) |
| `balls_remaining` | 120 - ball_seq |
| `required_run_rate` | (runs_required / balls_remaining) * 6 |
| `wickets_down` | COUNT(is_wicket) prior in innings |
| `pressure_index` | Calculated per formula above |
| `pressure_category` | Low/Medium/High based on PI |

### 3.3 Data Volume Estimate

For IPL 2023-2025 (219 matches):
- Total balls: ~52,000
- 2nd innings balls (where RRR matters): ~26,000
- High pressure balls (estimated 20%): ~5,200
- Per player sample sizes will vary significantly

**Sample Size Concern:** Many players will have insufficient high-pressure sample. Need minimum thresholds.

---

## 4. Methodology

### 4.1 Step 1: Calculate Match Context at Each Ball

For every ball in `fact_ball`, we need to know:
1. Current score
2. Wickets fallen
3. Balls remaining
4. Target (if 2nd innings)
5. Required run rate (if 2nd innings)

This requires a **running aggregate** computed via window functions.

### 4.2 Step 2: Assign Pressure Index

Apply the Pressure Index formula to each ball based on context.

```sql
CASE
    WHEN pressure_index >= 7 THEN 'HIGH'
    WHEN pressure_index >= 4 THEN 'MEDIUM'
    ELSE 'LOW'
END as pressure_category
```

### 4.3 Step 3: Aggregate Player Performance by Pressure

For each player, calculate metrics split by pressure category:

**Batting:**
| Metric | Low Pressure | Medium Pressure | High Pressure |
|--------|--------------|-----------------|---------------|
| Strike Rate | X | Y | Z |
| Average | X | Y | Z |
| Boundary % | X | Y | Z |
| Dot % | X | Y | Z |

**Bowling:**
| Metric | Low Pressure | Medium Pressure | High Pressure |
|--------|--------------|-----------------|---------------|
| Economy | X | Y | Z |
| Strike Rate | X | Y | Z |
| Dot % | X | Y | Z |
| Boundary Conceded % | X | Y | Z |

### 4.4 Step 4: Calculate Pressure Performance Delta

The key insight is the **change** from normal to pressure:

```
Pressure_Delta = (High_Pressure_Metric - Overall_Metric) / Overall_Metric * 100
```

**Interpretation:**
- Positive delta = Player improves under pressure (clutch)
- Negative delta = Player struggles under pressure (choker)
- Near-zero = Consistent regardless of pressure

### 4.5 Step 5: Statistical Significance

Given small sample sizes, we need to:

1. **Minimum Sample:** At least 30 balls in high pressure situations
2. **Confidence Indicator:** Flag players with < 50 balls as "LOW" sample
3. **Z-Score Comparison:** For statistical rigor, compare player's pressure SR to population mean pressure SR

```
Z_score = (Player_Pressure_SR - Population_Pressure_SR) / Population_Pressure_StdDev
```

A Z-score > 1.5 indicates statistically significant over-performance.

### 4.6 Clustering Approach (Optional V2)

If we want richer insights, we can cluster players into archetypes:
- **Clutch Performers:** Significantly better under pressure
- **Pressure-Proof:** Consistent across all situations
- **Pressure-Sensitive:** Significantly worse under pressure
- **Inconsistent:** High variance regardless of pressure

---

## 5. Output Format

### 5.1 Stat Pack Section Layout

The Pressure Performance section will appear after existing sections (suggest: Section 11).

```markdown
## 11. Pressure Performance Analysis

*How players perform under high-pressure situations (chases, death overs, close games)*

### 11.1 High-Pressure Batting

| Player | Normal SR | Pressure SR | Delta | Normal Avg | Pressure Avg | Delta | Sample | Rating |
|--------|-----------|-------------|-------|------------|--------------|-------|--------|--------|
| MS Dhoni | 165.1 | 182.3 | +10.4% | 30.7 | 42.1 | +37.1% | HIGH | CLUTCH |
| Ruturaj Gaikwad | 145.3 | 128.6 | -11.5% | 44.7 | 28.3 | -36.7% | MEDIUM | STRUGGLES |

### 11.2 High-Pressure Bowling

| Player | Normal Econ | Pressure Econ | Delta | Normal SR | Pressure SR | Delta | Sample | Rating |
|--------|-------------|---------------|-------|-----------|-------------|-------|--------|--------|
| Noor Ahmad | 8.24 | 7.45 | -9.6% | 16.5 | 14.2 | -13.9% | HIGH | CLUTCH |

### 11.3 Pressure Performance Ratings

**CLUTCH Performers (improve under pressure):**
- MS Dhoni: +10.4% SR, +37.1% Avg in high pressure
- Noor Ahmad: -9.6% Econ (better) in high pressure

**PRESSURE-PROOF (consistent):**
- Shivam Dube: +2.1% SR, -4.2% Avg (within normal variance)

**STRUGGLES Under Pressure:**
- [Player]: -15%+ degradation in key metrics
```

### 5.2 Example Metrics Per Player

For a player like **MS Dhoni** (known pressure player), the output might look like:

```
MS Dhoni - Pressure Performance

Overall (219 matches, 2023-2025):
- Career SR: 170.1
- Career Avg: 30.7
- Death Overs SR: 176.5

High Pressure Situations (43 innings, 181 balls):
- Pressure SR: 182.3 (+7.2% vs overall)
- Pressure Avg: 42.1 (+37.1% vs overall)
- Chases with RRR > 10: 14 innings, SR 189.2
- Close finishes (< 10 required in final over): 8 times, won 6

Pressure Rating: ELITE CLUTCH
Insight: Dhoni's SR increases 7% under pressure while his dismissal rate drops significantly.
         He is one of IPL's most reliable finishers in high-stakes situations.
```

### 5.3 Visual Elements (Future)

- **Pressure Performance Chart:** Scatter plot of Normal SR vs Pressure SR
- **Clutch Ranking:** Ordered list by pressure delta
- **Situation Heatmap:** Performance across different pressure scenarios

---

## 6. Implementation Steps

### Phase 1: Data Preparation (Effort: Small)

| Step | Description | Dependency | Estimate |
|------|-------------|------------|----------|
| 1.1 | Create running aggregate view for match context | fact_ball | 2 hours |
| 1.2 | Calculate runs_required, balls_remaining per ball | Step 1.1 | 1 hour |
| 1.3 | Calculate required_run_rate for 2nd innings | Step 1.2 | 1 hour |
| 1.4 | Calculate wickets_down at each ball | Step 1.1 | 1 hour |

### Phase 2: Pressure Index Calculation (Effort: Medium)

| Step | Description | Dependency | Estimate |
|------|-------------|------------|----------|
| 2.1 | Implement Pressure Index formula | Phase 1 | 2 hours |
| 2.2 | Validate PI against known high-pressure moments | Step 2.1 | 2 hours |
| 2.3 | Create pressure_category column | Step 2.1 | 1 hour |
| 2.4 | Build analytics_pressure_batting view | Step 2.3 | 2 hours |
| 2.5 | Build analytics_pressure_bowling view | Step 2.3 | 2 hours |

### Phase 3: Player Aggregation (Effort: Medium)

| Step | Description | Dependency | Estimate |
|------|-------------|------------|----------|
| 3.1 | Aggregate batting metrics by pressure category | Phase 2 | 2 hours |
| 3.2 | Aggregate bowling metrics by pressure category | Phase 2 | 2 hours |
| 3.3 | Calculate pressure deltas | Steps 3.1, 3.2 | 1 hour |
| 3.4 | Add sample size indicators | Step 3.3 | 1 hour |
| 3.5 | Calculate Z-scores for significance | Step 3.3 | 2 hours |

### Phase 4: Integration with Stat Packs (Effort: Small-Medium)

| Step | Description | Dependency | Estimate |
|------|-------------|------------|----------|
| 4.1 | Create pressure performance template | Phase 3 | 1 hour |
| 4.2 | Integrate with generate_stat_packs.py | Step 4.1 | 3 hours |
| 4.3 | Generate sample output for 1 team | Step 4.2 | 1 hour |
| 4.4 | Review with Andy Flower (domain validation) | Step 4.3 | 1 hour |
| 4.5 | Generate for all 10 teams | Step 4.4 | 1 hour |

### Phase 5: Quality Assurance (Effort: Small)

| Step | Description | Dependency | Estimate |
|------|-------------|------------|----------|
| 5.1 | Validate against known pressure performers | Phase 4 | 2 hours |
| 5.2 | Check sample size adequacy per team | Phase 4 | 1 hour |
| 5.3 | Domain expert review (Andy Flower) | Steps 5.1, 5.2 | 1 hour |

### Total Estimated Effort

| Phase | Effort |
|-------|--------|
| Phase 1: Data Preparation | 5 hours |
| Phase 2: Pressure Index | 9 hours |
| Phase 3: Player Aggregation | 8 hours |
| Phase 4: Stat Pack Integration | 7 hours |
| Phase 5: QA | 4 hours |
| **Total** | **33 hours** (~4-5 days) |

---

## 7. Dependencies

| Dependency | Status | Owner | Blocker? |
|------------|--------|-------|----------|
| fact_ball table with match_phase | Available | Data Team | No |
| dim_match with stage field | Available | Data Team | No |
| Match target calculation | To Build | Stephen Curry | No |
| Running aggregate for context | To Build | Stephen Curry | No |
| generate_stat_packs.py | Available | Stephen Curry | No |
| Sample size validation | To Define | Stephen Curry | No |
| Domain validation criteria | Required | Andy Flower | Soft |

---

## 8. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Small sample sizes for many players | Many "LOW" confidence ratings | High | Binary pressure flag approach, minimum 30-ball threshold |
| Pressure Index too complex | Implementation delays | Medium | Start with simplified binary approach, iterate |
| Pressure definition subjective | Domain expert disagreement | Low | Pre-align with Andy Flower on thresholds |
| Performance impact of window functions | Slow query times | Medium | Materialize intermediate views |
| Missing target data for some matches | Incomplete analysis | Low | Flag matches with missing data |

---

## 9. Founder Decision Points

The following items require Founder input before proceeding:

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Pressure Index vs Binary Flag | Full PI (more nuanced) vs Binary (simpler) | Start with Binary for V1, add PI in V2 |
| 2 | Minimum sample size | 20, 30, or 50 balls | 30 balls for HIGH confidence |
| 3 | Include knockout stage weighting? | Yes (adds complexity) vs No | Yes - playoffs matter |
| 4 | Section placement in stat pack | After Tactical Insights (Section 10) vs Earlier | Section 11 (new section) |
| 5 | Include historical pressure moments? | Yes (narrative value) vs No (scope creep) | No for V1, consider V2 |

---

## 10. Success Criteria

| Criteria | Measurement | Target |
|----------|-------------|--------|
| Coverage | % of key batters/bowlers with HIGH sample | > 60% of starters |
| Accuracy | Domain expert validation | Andy Flower approves ratings |
| Insight Quality | Pressure ratings match known clutch players | MS Dhoni = CLUTCH, etc. |
| Integration | Successfully added to all 10 stat packs | 100% |
| Performance | Query time for pressure views | < 5 seconds |

---

## 11. Relationship to Other Features

### Predicted XI Integration
- Pressure ratings can inform XI selection in high-stakes matches
- "For playoff matches, consider [player] who performs 15% better under pressure"

### Depth Charts Integration
- Finisher rankings could weight pressure performance
- "Backup finisher has higher pressure delta than starter"

### Tactical Insights
- Feed pressure findings into Andy Flower's tactical section
- "In chases requiring RRR > 10, promote [player] up the order"

---

## 12. V1 Scope Summary

### In Scope (V1)
- Binary pressure classification (High/Not High)
- Batting pressure metrics (SR, Avg, Boundary%, Dot%)
- Bowling pressure metrics (Econ, SR, Dot%, Boundary Conceded%)
- Pressure deltas with sample size indicators
- Simple ratings (CLUTCH, CONSISTENT, STRUGGLES)
- Integration into stat pack Section 11

### Out of Scope (V1)
- Full Pressure Index with weighted factors
- Match situation simulator
- Historical pressure moment narratives
- Player-specific pressure triggers
- Pressure performance trends over seasons

### Future Considerations (V2+)
- Full Pressure Index implementation
- Pressure clustering (archetypes)
- Interactive pressure scenario explorer
- Video links to pressure moments
- Pressure performance trends over seasons

---

## 13. Approval Request

This plan is submitted for Founder approval before implementation begins.

**Recommended Decision Points:**
1. Approve Binary Pressure approach for V1
2. Confirm 30-ball minimum sample threshold
3. Approve Section 11 placement in stat packs
4. Confirm scope boundaries

**Upon Approval:**
- Stephen Curry (Analytics Lead) will proceed with Phase 1-2
- Coordination with Andy Flower for domain validation
- Target delivery: 4-5 working days post-approval

---

*Plan prepared by Stephen Curry, Analytics Lead*
*Cricket Playbook v4.1.0*
*2026-02-06*
