# Task PRD: Predicted XII Algorithm v3.0 - "SUPER SELECTOR"

**Date:** 2026-02-04
**Owner:** Steph Curry (Analytics Lead)
**Status:** PENDING APPROVAL

---

## Problem Statement

The current Predicted XII algorithm (v2.0) has critical issues:

1. **Missing Key Players:** Shivam Dube (₹12Cr retained, CSK) excluded due to:
   - Empty `batter_classification` field
   - Only tag is "ACCUMULATOR" which gets 0 bonus

2. **Underutilized Data:** We have rich metrics that aren't being used:
   - `boundary_pct` (batting efficiency)
   - `dot_ball_pct` (bowling pressure)
   - Entry point analysis (position validation)

3. **Missing Classification Scores:** Only 5 classifications scored, missing ACCUMULATOR and others

4. **No Variety Weighting:** Algorithm claims "65% Competency / 35% Variety" but variety isn't explicitly weighted

---

## Proposed Solution: "SUPER SELECTOR" v3.0

A metrics-driven XI prediction algorithm with:

### 1. Data Quality Fix
- Fix Shivam Dube classification in `ipl_2026_squads.csv`
- Add missing batter_tags for key players

### 2. Classification Scoring Update
```python
classification_scores = {
    "Elite Top-Order": 30,
    "Power Finisher": 25,
    "Aggressive Opener": 25,
    "All-Round Finisher": 20,
    "Anchor": 15,
    "ACCUMULATOR": 12,  # NEW
}
```

### 3. Metrics-Based Scoring (NEW)

**Batting Efficiency (balls/boundary%):**
```python
if boundary_pct >= 28%: +15
elif boundary_pct >= 24%: +10
elif boundary_pct >= 20%: +5
```

**Bowling Pressure (dot ball%):**
```python
if death_dot_pct >= 35%: +15
elif death_dot_pct >= 30%: +10
elif death_dot_pct >= 25%: +5
```

**Consistency Bonus:**
```python
if consistency_index >= 55: +8
elif consistency_index >= 45: +4
```

### 4. Entry Point Validation
- Use `avg_entry_ball` to VALIDATE position assignments
- Not primary signal, but confirms fit is correct

### 5. Algorithm Name: "SUPER SELECTOR"
Like FiveThirtyEight's PECOTA, CARMELO, RAPTOR - a memorable branded algorithm.

---

## Success Criteria

| Criteria | Measure |
|----------|---------|
| Shivam Dube in CSK XI | ✅ Selected |
| All retained players (≥10Cr) considered | ✅ High scores |
| Metrics integrated | ✅ boundary%, dot_ball% used |
| Documentation complete | ✅ Algorithm brief created |
| All constraints satisfied | ✅ 10/10 teams pass |

---

## Scope

### In Scope
- Fix `ipl_2026_squads.csv` data for Shivam Dube
- Add ACCUMULATOR classification bonus
- Integrate metrics from `batter_consistency_index.csv`
- Integrate metrics from `bowler_pressure_sequences.csv`
- Use entry points as position validator
- Create algorithm documentation with "SUPER SELECTOR" branding
- Regenerate all predicted XIIs

### Out of Scope
- Matchup-specific optimizations
- Form data integration (not available)
- Injury/availability flags

---

## Dependencies

| Dependency | Status |
|------------|--------|
| `batter_consistency_index.csv` | ✅ Exists |
| `bowler_pressure_sequences.csv` | ✅ Exists |
| `batter_entry_points_2023.csv` | ✅ Exists |
| `ipl_2026_squads.csv` | ✅ Exists (needs fix) |

---

## Estimated Effort

**Medium** - Algorithm modifications + data fix + documentation + regeneration

---

## Algorithm Brief: SUPER SELECTOR

### Name Origin
**S.U.P.E.R. SELECTOR** = **S**tatistical **U**nified **P**layer **E**valuation and **R**anking SELECTOR

### Scoring Formula

```
PLAYER_SCORE = BASE + CLASSIFICATION + TAGS + PRICE + METRICS + VARIETY

Where:
- BASE = 50 (batters) or 40 (bowlers)
- CLASSIFICATION = 0-30 points based on player type
- TAGS = Sum of tag bonuses (phase-specific performance)
- PRICE = 5-15% bonus for high-investment players
- METRICS = NEW: boundary%, consistency, dot_ball%, economy
- VARIETY = Left-hand bonus, spinner/pacer balance
```

### Constraint Satisfaction
- C1: Max 4 overseas
- C2: Min 20 overs bowling
- C3: At least 1 wicketkeeper
- C4: Min 4 primary bowlers
- C5: At least 1 spinner

### Position Assignment
1. Score all players
2. Assign to tiers using entry_point_classification
3. Validate with avg_entry_ball
4. Optimize for balance

---

**PRD Version:** 1.0
**Requesting Agent:** Steph Curry
**Date:** 2026-02-04
