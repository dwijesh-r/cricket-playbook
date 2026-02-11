# TKT-050: Pressure Performance Section Plan

**Author:** Stephen Curry (Analytics Lead)
**Status:** FOUNDER REVIEW — v2
**Created:** 2026-02-06 | **Revised:** 2026-02-11
**Ticket:** TKT-050 | **Epic:** EPIC-006

---

## Founder Feedback (2026-02-11)

1. Multi-band RRR analysis (not single >10 threshold) — for BOTH batters and bowlers
2. Boundary% and dot ball% are key metrics per band
3. Dot ball sequences and boundary sequences under pressure
4. All analysis from IPL 2023+ only (using `_since2023` views)
5. Unified batters + bowlers section in stat packs

---

## 1. Executive Summary

Add a **Pressure Performance** section to stat packs analyzing how players perform across escalating pressure bands in T20 cricket. Uses multi-band Required Run Rate (RRR) tiers rather than a binary cutoff, covering **both batters and bowlers** in a unified section.

**Data scope:** IPL 2023-2025 only (Founder Decision #6 — 2023 baseline locked).

---

## 2. Pressure Band Definitions

### 2.1 RRR-Based Pressure Bands (Batting — 2nd Innings Chases)

| Band | RRR Range | Description | Typical Scenario |
|------|-----------|-------------|------------------|
| **Comfortable** | < 8 | Cruising | Need 64 off 48 balls |
| **Building** | 8–10 | Above par, manageable | Need 80 off 48 balls |
| **High Pressure** | 10–12 | Aggressive required | Need 60 off 30 balls |
| **Extreme** | 12–15 | Six-hitting territory | Need 45 off 18 balls |
| **Near-Impossible** | 15+ | Miracle needed | Need 30 off 12 balls |

### 2.2 RRR-Based Pressure Bands (Bowling — Defending in 2nd Innings)

Same bands, inverted perspective — what does the bowler face when opposition RRR is at these levels:

| Band | Opposition RRR | Bowler Context |
|------|----------------|----------------|
| **Comfortable** | < 8 | Batters under no rush — bowler can attack |
| **Building** | 8–10 | Batters getting aggressive — dots valuable |
| **High Pressure** | 10–12 | Batters swinging hard — execution critical |
| **Extreme** | 12–15 | Full attack mode — one bad ball = boundary |
| **Near-Impossible** | 15+ | Batters desperate — bowler holds the cards |

### 2.3 Additional Pressure Contexts

| Context | Definition | Applies To |
|---------|------------|------------|
| **Death Overs** | Overs 16–20 (regardless of RRR) | Both |
| **Wickets Falling** | 5+ wickets down before over 15 | Batting |
| **Close Defense** | < 15 to defend in last 2 overs | Bowling |

---

## 3. Metrics Per Band

### 3.1 Batting Metrics (Per RRR Band)

| Metric | Description |
|--------|-------------|
| **Innings** | Number of innings in this band |
| **Balls Faced** | Sample size |
| **Strike Rate** | Runs per 100 balls |
| **Average** | Runs per dismissal |
| **Boundary%** | % of balls hit for 4 or 6 |
| **Dot Ball%** | % of balls scoring 0 (legal deliveries) |
| **Six%** | % of balls hit for 6 |
| **Dismissal Rate** | Wickets per ball |

### 3.2 Bowling Metrics (Per Opposition RRR Band)

| Metric | Description |
|--------|-------------|
| **Overs** | Sample size (legal balls / 6) |
| **Economy** | Runs conceded per over |
| **Dot Ball%** | % of legal deliveries that are dots |
| **Boundary% Conceded** | % of balls going for 4 or 6 |
| **Six% Conceded** | % of balls hit for 6 |
| **Strike Rate** | Balls per wicket |
| **Wickets** | Total wickets taken in this band |

### 3.3 Sequence Metrics (Under Pressure — RRR > 10 bands)

| Sequence Metric | Description |
|-----------------|-------------|
| **Dot Ball Sequences** | Consecutive dot balls delivered/faced under pressure |
| **Avg Dot Sequence Length** | Mean length of dot sequences in high-RRR situations |
| **Max Dot Sequence** | Longest dot streak under pressure |
| **Boundary Sequences** | Consecutive boundary balls under pressure |
| **Avg Boundary Sequence Length** | Mean length of boundary streaks |
| **Dot-to-Boundary Break Rate** | How often a dot sequence is broken by a boundary |
| **Boundary-to-Dot Recovery Rate** | How often a bowler recovers with dots after conceding a boundary |

---

## 4. Pressure Performance Delta

The key analytical insight — how performance **changes** across bands:

```
Delta = ((Band_Metric - Overall_Metric) / Overall_Metric) * 100
```

### 4.1 Batter Rating System

| Rating | Criteria |
|--------|----------|
| **CLUTCH** | SR improves by 10%+ AND dot% drops in 12+ RRR bands |
| **PRESSURE-PROOF** | Metrics within +/- 5% of overall across all bands |
| **PRESSURE-SENSITIVE** | SR drops 10%+ OR dot% rises 10%+ in 12+ RRR bands |
| **FINISHER** | SR in 15+ band exceeds 170 with adequate sample |

### 4.2 Bowler Rating System

| Rating | Criteria |
|--------|----------|
| **CLUTCH** | Economy improves (drops) AND dot% rises in 12+ RRR bands |
| **PRESSURE-PROOF** | Metrics within +/- 5% of overall across all bands |
| **LEAKS** | Economy rises 15%+ OR boundary% conceded rises 10%+ in 12+ bands |
| **CLOSER** | Economy < 8.5 in 15+ band with 5+ overs bowled |

---

## 5. Data Pipeline

### 5.1 Data Scope

**IPL 2023-2025 only** (Founder Decision #6)
- ~219 matches, ~52,000 balls
- 2nd innings balls: ~26,000 (where RRR is calculable)
- Minimum thresholds: 30 balls per band per player (HIGH confidence), 15-29 (MEDIUM), <15 (excluded)

### 5.2 SQL Architecture

```
fact_ball (2023+)
  → CTE: running_match_context (cumulative score, wickets, balls remaining, RRR)
  → CTE: pressure_classified (assign RRR band per ball)
  → Aggregation: batter_pressure_bands (metrics per batter per band)
  → Aggregation: bowler_pressure_bands (metrics per bowler per opposition RRR band)
  → Aggregation: dot_sequences_under_pressure (sequence analysis for RRR > 10)
  → Aggregation: boundary_sequences_under_pressure (sequence analysis for RRR > 10)
```

### 5.3 New DuckDB Views

| View Name | Description |
|-----------|-------------|
| `analytics_ipl_batter_pressure_bands_since2023` | Batter metrics by RRR band |
| `analytics_ipl_bowler_pressure_bands_since2023` | Bowler metrics by opposition RRR band |
| `analytics_ipl_pressure_dot_sequences_since2023` | Dot ball sequence analysis under pressure |
| `analytics_ipl_pressure_boundary_sequences_since2023` | Boundary sequence analysis under pressure |
| `analytics_ipl_pressure_deltas_since2023` | Pre-computed deltas for stat pack generation |

### 5.4 Key SQL Logic — RRR Calculation

```sql
WITH running_context AS (
    SELECT fb.*,
        SUM(fb.total_runs) OVER (
            PARTITION BY fb.match_id, fb.innings
            ORDER BY fb.ball_seq
        ) AS cumulative_runs,
        SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) OVER (
            PARTITION BY fb.match_id, fb.innings
            ORDER BY fb.ball_seq
        ) AS wickets_down,
        dm.target_runs,
        (120 - fb.ball_seq) AS balls_remaining
    FROM fact_ball fb
    JOIN dim_match dm ON fb.match_id = dm.match_id
    WHERE fb.innings = 2  -- 2nd innings only for RRR
),
pressure_bands AS (
    SELECT *,
        CASE
            WHEN balls_remaining = 0 THEN NULL
            ELSE (target_runs - cumulative_runs) * 6.0 / balls_remaining
        END AS required_run_rate,
        CASE
            WHEN (target_runs - cumulative_runs) * 6.0 / NULLIF(balls_remaining, 0) >= 15 THEN 'NEAR_IMPOSSIBLE'
            WHEN (target_runs - cumulative_runs) * 6.0 / NULLIF(balls_remaining, 0) >= 12 THEN 'EXTREME'
            WHEN (target_runs - cumulative_runs) * 6.0 / NULLIF(balls_remaining, 0) >= 10 THEN 'HIGH'
            WHEN (target_runs - cumulative_runs) * 6.0 / NULLIF(balls_remaining, 0) >= 8  THEN 'BUILDING'
            ELSE 'COMFORTABLE'
        END AS pressure_band
    FROM running_context
)
```

---

## 6. Stat Pack Output Format

### Section 11: Pressure Performance (Unified Batters + Bowlers)

```markdown
## 11. Pressure Performance

*How players perform across escalating pressure bands (IPL 2023-2025)*

### Batting Under Pressure (2nd Innings Chases by RRR Band)

| Player | Band | Balls | SR | Avg | Boundary% | Dot% | Six% | Delta SR | Rating |
|--------|------|-------|-----|-----|-----------|------|------|----------|--------|
| SA Yadav | Comfortable (<8) | 245 | 156.3 | 42.1 | 18.8% | 32.6% | 8.2% | — | — |
| SA Yadav | Building (8-10) | 118 | 163.6 | 35.8 | 21.2% | 28.8% | 10.2% | +4.7% | — |
| SA Yadav | High (10-12) | 67 | 178.5 | 28.2 | 25.4% | 23.9% | 13.4% | +14.2% | CLUTCH |
| SA Yadav | Extreme (12-15) | 34 | 191.2 | 22.1 | 29.4% | 20.6% | 17.6% | +22.3% | CLUTCH |
| SA Yadav | Near-Impossible (15+) | 12 | 200.0 | — | 33.3% | 16.7% | 25.0% | +27.9% | LOW SAMPLE |

### Bowling Under Pressure (Opposition RRR Band)

| Player | Band | Overs | Econ | Dot% | Bdry% Conc | Wkts | SR | Delta Econ | Rating |
|--------|------|-------|------|------|------------|------|----|------------|--------|
| JJ Bumrah | Comfortable (<8) | 18.3 | 6.54 | 38.2% | 10.9% | 12 | 9.2 | — | — |
| JJ Bumrah | Building (8-10) | 12.1 | 7.12 | 35.6% | 12.3% | 8 | 9.1 | +8.9% | — |
| JJ Bumrah | High (10-12) | 8.4 | 6.84 | 36.8% | 11.1% | 7 | 7.2 | +4.6% | CLUTCH |
| JJ Bumrah | Extreme (12-15) | 4.2 | 7.52 | 33.3% | 14.3% | 4 | 6.3 | +15.0% | PRESSURE-PROOF |

### Pressure Sequences (RRR > 10 situations)

**Dot Ball Sequences Under Pressure:**
| Player (Bowler) | Avg Dot Seq | Max Dot Seq | Dot Sequences | Recovery Rate |
|-----------------|-------------|-------------|---------------|---------------|
| JJ Bumrah | 2.8 | 6 | 14 | 71.4% |

**Boundary Sequences Under Pressure:**
| Player (Batter) | Avg Bdry Seq | Max Bdry Seq | Bdry Sequences | Break-Out Rate |
|-----------------|--------------|--------------|----------------|----------------|
| SA Yadav | 1.8 | 3 | 9 | 44.4% |

### Pressure Ratings Summary
| Player | Role | Rating | Key Insight |
|--------|------|--------|-------------|
| SA Yadav | BAT | CLUTCH | SR rises 22%+ in Extreme band |
| JJ Bumrah | BOWL | CLOSER | Econ drops below 7 in High band |
```

---

## 7. Implementation Phases

### Phase 1: Pressure Views (2 days)

| Step | Description | Owner |
|------|-------------|-------|
| 1.1 | Create `running_match_context` CTE with cumulative score, RRR | Stephen Curry |
| 1.2 | Build `analytics_ipl_batter_pressure_bands_since2023` | Stephen Curry |
| 1.3 | Build `analytics_ipl_bowler_pressure_bands_since2023` | Stephen Curry |
| 1.4 | Validate RRR calculations against known match situations | Stephen Curry |

### Phase 2: Sequence Analysis (1 day)

| Step | Description | Owner |
|------|-------------|-------|
| 2.1 | Build `analytics_ipl_pressure_dot_sequences_since2023` | Stephen Curry |
| 2.2 | Build `analytics_ipl_pressure_boundary_sequences_since2023` | Stephen Curry |
| 2.3 | Calculate recovery rates and break-out rates | Stephen Curry |

### Phase 3: Delta Calculation & Ratings (1 day)

| Step | Description | Owner |
|------|-------------|-------|
| 3.1 | Compute pressure deltas per player per band | Stephen Curry |
| 3.2 | Apply rating system (CLUTCH/PRESSURE-PROOF/etc.) | Stephen Curry |
| 3.3 | Sample size confidence flagging (HIGH/MEDIUM/EXCLUDED) | Stephen Curry |

### Phase 4: Stat Pack Integration (1 day)

| Step | Description | Owner |
|------|-------------|-------|
| 4.1 | Add Section 11 template to `generate_stat_packs.py` | Stephen Curry |
| 4.2 | Generate sample output for MI, CSK | Stephen Curry |
| 4.3 | Regenerate all 10 stat packs | Stephen Curry |

### Phase 5: Validation (1 day)

| Step | Description | Owner |
|------|-------------|-------|
| 5.1 | Domain sanity check (Andy Flower) | Andy Flower |
| 5.2 | Statistical robustness check (Jose Mourinho) | Jose Mourinho |
| 5.3 | Founder review of sample stat pack output | Founder |

**Total: ~6 days post-approval**

---

## 8. Dependencies

| Dependency | Status | Blocker? |
|------------|--------|----------|
| `fact_ball` with `is_legal_ball`, `match_phase` | Available | No |
| `dim_match` with `target_runs` | Need to verify column exists | Check |
| `_since2023` dual-scope views (TKT-181) | 90% complete | No |
| `generate_stat_packs.py` | Available | No |
| Andy Flower domain validation | Required at Phase 5 | Soft |

---

## 9. Sample Size Thresholds

| Confidence | Balls Per Band | Display |
|------------|----------------|---------|
| **HIGH** | >= 30 | Full metrics + rating |
| **MEDIUM** | 15–29 | Metrics shown, rating flagged |
| **EXCLUDED** | < 15 | Not displayed |

For sequence metrics: minimum 5 sequences per player in RRR > 10 bands.

---

## 10. Existing Assets to Leverage

| Asset | Location | Reuse |
|-------|----------|-------|
| Bowler Pressure Sequences (S3.0-12) | `sprint_3_p1_features.py` | Refactor into multi-band |
| `analytics_ipl_dot_ball_pressure` | `analytics_ipl.py` view #8 | Extend for RRR-band context |
| `bowler_pressure_sequences.csv` | `outputs/` | Replace with multi-band version |
| The Lab Pressure card | `analysis.html` | Update to show multi-band data |

---

## 11. Success Criteria

| Criteria | Target |
|----------|--------|
| Coverage | > 60% of IPL 2023+ regular starters with HIGH sample in at least 3 bands |
| Accuracy | Known clutch performers (Dhoni, SKY, Bumrah) rated correctly |
| Bands populated | All 5 bands have meaningful data for top teams |
| Sequence insights | Dot/boundary sequences visible for 20+ bowlers and 20+ batters |
| Stat pack integration | All 10 teams have Section 11 |

---

## Approval Request

This revised plan incorporates all Founder feedback (2026-02-11):
- Multi-band RRR analysis for both batters AND bowlers
- Boundary% and dot ball% as core metrics per band
- Dot ball sequences and boundary sequences under pressure
- IPL 2023+ only
- Unified batters + bowlers section

**Awaiting Founder approval to begin implementation.**

---

*Plan revised by Stephen Curry, Analytics Lead*
*Cricket Playbook v4.1.0*
*2026-02-11*
