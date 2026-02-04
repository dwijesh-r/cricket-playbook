# Notebooks

Jupyter notebooks for data exploration and analysis.

**Version:** 4.0.0 | **Last Updated:** 2026-02-04

---

## Contents

| Notebook | Description |
|----------|-------------|
| `explore.ipynb` | General data exploration |
| `view_explorer.ipynb` | Interactive SQL queries against analytics views |

---

## Quick Start

```bash
# Option 1: Jupyter Notebook
jupyter notebook notebooks/

# Option 2: VS Code with Jupyter extension
code notebooks/view_explorer.ipynb
```

---

## Database Connection

The notebooks connect to DuckDB at `data/cricket_playbook.duckdb`:

```python
import duckdb

con = duckdb.connect('data/cricket_playbook.duckdb', read_only=True)
```

---

## Sample Queries

### Career Stats

```sql
-- Top 10 IPL batters by strike rate (min 500 balls)
SELECT player_name, matches, runs, balls, strike_rate, average
FROM analytics_ipl_batting_career
WHERE balls >= 500
ORDER BY strike_rate DESC
LIMIT 10;
```

### Phase Analysis

```sql
-- Death overs specialists (batters)
SELECT player_name, phase, runs, balls, strike_rate, boundary_pct
FROM analytics_ipl_batter_phase
WHERE phase = 'death' AND balls >= 100
ORDER BY strike_rate DESC
LIMIT 10;
```

### Matchup Analysis

```sql
-- Virat Kohli vs different bowling types
SELECT bowling_type, balls, runs, strike_rate, dismissals
FROM analytics_ipl_batter_vs_bowler_type
WHERE batter_name = 'V Kohli'
ORDER BY balls DESC;
```

### Team Queries

```sql
-- MI squad with roles
SELECT player_name, role, batting_style, bowling_style
FROM dim_player dp
JOIN ipl_2026_squads s ON dp.player_id = s.player_id
WHERE s.team = 'MI';
```

### View List

```sql
-- List all analytics views
SELECT table_name
FROM information_schema.tables
WHERE table_name LIKE 'analytics_%';
```

---

## Available Analytics Views (35)

### Career Stats
- `analytics_ipl_batting_career`
- `analytics_ipl_bowling_career`

### Phase Analysis
- `analytics_ipl_batter_phase`
- `analytics_ipl_bowler_phase`

### Matchups
- `analytics_ipl_batter_vs_bowler`
- `analytics_ipl_batter_vs_bowler_type`
- `analytics_ipl_batter_vs_team`
- `analytics_ipl_bowler_vs_batter_hand`

### Benchmarks
- `analytics_ipl_batting_benchmarks`
- `analytics_ipl_bowling_benchmarks`
- `analytics_ipl_batting_percentiles`
- `analytics_ipl_bowling_percentiles`

---

## Tips

1. **Always use read_only=True** when exploring to prevent accidental modifications
2. **Filter by year >= 2023** for current form analysis
3. **Check sample sizes** - views include `balls` column for confidence assessment
4. **Use EXPLAIN** for complex queries to understand performance

---

*Cricket Playbook v4.0.0*
