# Metrics

Performance metrics and derived statistics for batters and bowlers.

**Last Updated:** 2026-02-02

---

## Files

### Batter Metrics

| File | Records | Description |
|------|---------|-------------|
| `batter_consistency_index.csv` | ~200 | Consistency scores (CV-based) |
| `batter_consistency_by_year.csv` | ~500 | Yearly breakdown |

### Partnership Metrics

| File | Records | Description |
|------|---------|-------------|
| `partnership_synergy.csv` | ~300 | Partnership performance scores |
| `partnership_synergy_by_year.csv` | ~800 | Yearly partnership data |

### Bowler Metrics

| File | Records | Description |
|------|---------|-------------|
| `bowler_pressure_sequences.csv` | ~250 | Dot ball sequence analysis |
| `bowler_pressure_by_year.csv` | ~600 | Yearly pressure data |
| `bowler_phase_performance.csv` | ~400 | PP/Middle/Death stats |
| `bowler_phase_distribution_grouped.csv` | ~300 | Phase distribution tables |
| `bowler_over_timing.csv` | ~200 | Over timing patterns |

---

## Key Metrics Explained

### Consistency Index

Measures scoring reliability using Coefficient of Variation (CV):

```
Consistency Index = 100 - (CV * 100)
```

| Score | Interpretation |
|-------|----------------|
| 80+ | Very consistent |
| 60-80 | Consistent |
| 40-60 | Moderate |
| <40 | Inconsistent |

### Partnership Synergy Score

Measures how well two batters perform together:

```
Synergy = (Partnership_RR / Expected_RR) * 100
```

| Score | Interpretation |
|-------|----------------|
| 110+ | Strong synergy |
| 90-110 | Neutral |
| <90 | Poor synergy |

### Bowler Pressure Sequences

Tracks consecutive dot balls:

| Metric | Description |
|--------|-------------|
| `max_dot_sequence` | Longest consecutive dots |
| `avg_dot_sequence` | Average sequence length |
| `pressure_index` | Composite pressure score |

---

## Phase Definitions

| Phase | Overs | Balls |
|-------|-------|-------|
| Powerplay | 1-6 | 1-36 |
| Middle | 7-15 | 37-90 |
| Death | 16-20 | 91-120 |

---

## Regenerating

```bash
python scripts/generators/sprint_3_p1_features.py
```

---

*Cricket Playbook v4.0.0*
