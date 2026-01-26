# Data

Source data and database files.

---

## Contents

| File/Directory | Description |
|----------------|-------------|
| `cricket_playbook.duckdb` | Main DuckDB database (159MB) |
| `ipl_2026_squads.csv` | IPL 2026 team rosters (231 players) |
| `ipl_2026_player_contracts.csv` | Player contract prices |
| `bowler_classifications_v2.csv` | Bowling style mappings (280 bowlers) |
| `raw/` | Source Cricsheet ZIP files (18 datasets) |
| `processed/` | Intermediate processed data |
| `manifests/` | Data manifest files |

---

## Database Schema

Key tables in DuckDB:
- `fact_ball` - Ball-by-ball records (2.1M rows)
- `dim_player` - Player dimension
- `dim_match` - Match dimension
- `dim_team` - Team dimension

---

## Data Sources

| Source | Records |
|--------|---------|
| Cricsheet T20 | 9,357 matches |
| IPL 2023-2025 | 219 matches |

---

*Cricket Playbook v3.1.0*
