# ML Features

**Owner:** Stephen Curry (Analytics Lead)

---

## Overview

Feature engineering documentation for Cricket Playbook's ML models.

---

## Batter Clustering Features (8 features after cleanup)

| Feature | Description | Source |
|---------|-------------|--------|
| `overall_sr` | Overall strike rate | DuckDB analytics |
| `batting_avg` | Batting average | DuckDB analytics |
| `boundary_pct` | Boundary percentage | DuckDB analytics |
| `dot_pct` | Dot ball percentage | DuckDB analytics |
| `avg_batting_position` | Average batting position (v2 NEW) | DuckDB analytics |
| `pp_sr` | Powerplay strike rate | Phase analysis |
| `mid_sr` | Middle overs strike rate | Phase analysis |
| `death_sr` | Death overs strike rate | Phase analysis |

### Correlation Cleanup
Features removed due to high correlation (r > 0.90):
- `balls_faced` (correlated with runs)
- Phase-specific averages (correlated with overall)

---

## Bowler Clustering Features (16 features after cleanup)

| Feature | Description | Source |
|---------|-------------|--------|
| `overall_economy` | Overall economy rate | DuckDB analytics |
| `overall_sr` | Overall strike rate | DuckDB analytics |
| `overall_dot_pct` | Overall dot ball % | DuckDB analytics |
| `overall_boundary_pct` | Overall boundary % | DuckDB analytics |
| `pp_economy` | Powerplay economy | Phase analysis |
| `pp_dot_pct` | Powerplay dot % | Phase analysis |
| `pp_boundary_pct` | Powerplay boundary % | Phase analysis |
| `mid_economy` | Middle overs economy | Phase analysis |
| `mid_dot_pct` | Middle overs dot % | Phase analysis |
| `mid_boundary_pct` | Middle overs boundary % | Phase analysis |
| `death_economy` | Death overs economy | Phase analysis |
| `death_dot_pct` | Death overs dot % | Phase analysis |
| `death_boundary_pct` | Death overs boundary % | Phase analysis |
| `pp_wickets` | Powerplay wickets (v2 NEW) | Phase analysis |
| `mid_wickets` | Middle overs wickets (v2 NEW) | Phase analysis |
| `death_wickets` | Death overs wickets (v2 NEW) | Phase analysis |

---

## Sample Size Requirements

| Type | Minimum | Rationale |
|------|---------|-----------|
| Batters | 500 balls faced | Statistical significance |
| Bowlers | 300 balls bowled | Statistical significance |

---

## Recency Weighting

- **2021-2025 data:** 2x weight
- **Pre-2021 data:** 1x weight

---

*Stephen Curry - Analytics Lead*
