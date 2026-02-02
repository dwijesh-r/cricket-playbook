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

*Cricket Playbook v4.0.0*
*Andy Flower - Cricket Domain Expert*
