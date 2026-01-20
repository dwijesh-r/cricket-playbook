# Cricket Playbook

IPL 2026 Analytics Platform for editorial and broadcast use.

## Overview

Cricket Playbook is a comprehensive cricket analytics system built on ball-by-ball T20 data. It provides detailed statistical analysis for all 10 IPL 2026 teams, including player performance metrics, phase-wise breakdowns, matchup analysis, and tactical insights.

## Quick Start

```bash
# Run analytics pipeline
python scripts/analytics_ipl.py

# Generate stat packs for all teams
python scripts/generate_stat_packs.py

# Or use the CLI runner with validation
./scripts/run_stat_packs.sh --validate
```

## Data Summary

| Metric | Value |
|--------|-------|
| Total T20 Matches | 9,357 |
| IPL Matches | 1,169 |
| Ball-by-ball Records | 2,137,915 |
| IPL 2026 Squad Players | 231 |
| Bowler Classifications | 280 (98.8% coverage) |
| Analytics Views | 34 |

## Project Structure

```
cricket-playbook/
├── data/                          # Data files
│   ├── cricket_playbook.duckdb    # Main DuckDB database
│   ├── ipl_2026_squads.csv        # IPL 2026 team rosters
│   ├── ipl_2026_player_contracts.csv
│   └── bowler_classifications.csv # Bowling style mappings
├── scripts/                       # Python scripts
│   ├── analytics_ipl.py           # Creates 34 analytics views
│   ├── generate_stat_packs.py     # Generates team stat packs
│   ├── run_stat_packs.sh          # CLI runner with validation
│   └── validate_schema.py         # Schema validation (33 checks)
├── stat_packs/                    # Generated team stat packs
│   ├── CSK_stat_pack.md
│   ├── MI_stat_pack.md
│   ├── RCB_stat_pack.md
│   └── ... (10 teams)
├── tests/                         # Test suite
│   └── test_stat_packs.py         # 65 pytest smoke tests
├── notebooks/                     # Jupyter notebooks
│   └── view_explorer.ipynb        # Interactive SQL queries
└── .editorial/                    # Editorial documents
    ├── rework_plan_v2.1.md
    ├── sprint_review_2026-01-20.md
    └── flower_review_v2.1.md
```

## Analytics Views

### Career Statistics
- `analytics_ipl_batting_career` - IPL batting career stats
- `analytics_ipl_bowling_career` - IPL bowling career stats

### Phase Analysis (Powerplay / Middle / Death)
- `analytics_ipl_batter_phase` - Batting by match phase
- `analytics_ipl_bowler_phase` - Bowling by match phase

### Matchup Analysis
- `analytics_ipl_batter_vs_bowler` - Head-to-head records
- `analytics_ipl_batter_vs_bowler_type` - Performance vs bowling styles
- `analytics_ipl_batter_vs_team` - Performance vs each team

### Percentile Rankings
- `analytics_ipl_batting_percentiles` - Batting percentile rankings
- `analytics_ipl_bowling_percentiles` - Bowling percentile rankings

### Benchmarks
- `analytics_ipl_batting_benchmarks` - IPL-wide batting averages by phase
- `analytics_ipl_bowling_benchmarks` - IPL-wide bowling averages by phase
- `analytics_ipl_career_benchmarks` - Qualified player averages

### Squad Integration
- `analytics_ipl_squad_batting` - 2026 squad batting stats
- `analytics_ipl_squad_bowling` - 2026 squad bowling stats

## Bowling Style Categories

| Style | Coverage |
|-------|----------|
| Right-arm pace | 49.4% |
| Left-arm pace | 13.6% |
| Right-arm off-spin | 12.4% |
| Right-arm leg-spin | 11.8% |
| Left-arm orthodox | 10.4% |
| Left-arm wrist spin | 1.2% |
| Unknown | 1.2% |

## Franchise Aliases

Historical team names are mapped to current franchises:

| Current | Historical |
|---------|------------|
| Delhi Capitals | Delhi Daredevils |
| Punjab Kings | Kings XI Punjab |
| Royal Challengers Bengaluru | Royal Challengers Bangalore |

## Sample Size Indicators

All views include sample size indicators:

| Indicator | Batting | Bowling |
|-----------|---------|---------|
| HIGH | 500+ balls | 300+ balls |
| MEDIUM | 100-499 balls | 60-299 balls |
| LOW | <100 balls | <60 balls |

## Testing

```bash
# Run smoke tests (65 tests)
pytest tests/test_stat_packs.py -v

# Run schema validation (33 checks)
python scripts/validate_schema.py
```

## Interactive Exploration

Open `notebooks/view_explorer.ipynb` in VS Code or Jupyter to run interactive SQL queries against the analytics views.

## Tech Stack

- **Database:** DuckDB (embedded OLAP)
- **Language:** Python 3.12
- **Testing:** pytest
- **Data Source:** Cricsheet (ball-by-ball JSON)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.1.0 | 2026-01-20 | Percentiles, benchmarks, tests, CLI |
| v2.0.0 | 2026-01-19 | IPL 2026 squads, 26 analytics views |
| v1.1.0 | 2026-01-18 | Match phase column, wicketkeeper detection |
| v1.0.0 | 2026-01-17 | Initial data ingestion |

## Team

| Agent | Role |
|-------|------|
| Tom Brady | Product Owner |
| Stephen Curry | Analytics Lead |
| Andy Flower | Cricket Technical Advisor |
| Brock Purdy | Data Pipeline |
| Brad Stevens | Performance & Accountability |
| N'Golo Kanté | QA |

## License

Internal use only - Cricket Playbook Editorial Team

---

*Cricket Playbook v2.1.0 - IPL 2026 Analytics Platform*
