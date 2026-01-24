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
| **IPL Analytics Data** | **2023-2025 (219 matches)** |
| Ball-by-ball Records | 2,137,915 |
| IPL 2026 Squad Players | 231 |
| Bowler Classifications | 280 (98.8% coverage) |
| Analytics Views | 34 |

**Note:** All IPL analytics use 2023-2025 data only (219 matches) to account for stat drift due to game evolution. Historical data (2008-2022) is available but not used for player classifications or stat packs.

## Project Structure

```
cricket-playbook/
├── config/                        # Configuration
│   ├── agents/                    # Agent definitions (12 agents)
│   ├── templates/                 # Output templates
│   └── CONSTITUTION.md            # Agent framework
├── data/                          # Source data
│   ├── cricket_playbook.duckdb    # Main DuckDB database (159MB)
│   ├── ipl_2026_squads.csv        # IPL 2026 team rosters
│   ├── ipl_2026_player_contracts.csv
│   ├── bowler_classifications.csv # Bowling style mappings
│   └── raw/                       # Source ZIP files (18 T20 datasets)
├── outputs/                       # Generated outputs
│   ├── player_tags.json           # Multi-tag classification (155 players)
│   ├── bowler_handedness_matchup.csv  # LHB/RHB matchup analysis
│   ├── batter_bowling_type_matchup.csv  # Pace/spin matchups
│   ├── bowler_phase_performance.csv  # Phase economy tags
│   ├── batter_entry_points.csv    # Entry position analysis
│   ├── bowler_over_timing.csv     # Bowler over distribution
│   └── ipl_2026_squad_experience.csv
├── scripts/                       # Python scripts
│   ├── analytics_ipl.py           # Creates 34 analytics views
│   ├── generate_stat_packs.py     # Generates team stat packs
│   ├── player_clustering_v2.py    # K-means clustering model
│   ├── bowler_handedness_matchup.py # LHB/RHB analysis
│   ├── run_stat_packs.sh          # CLI runner
│   └── validate_schema.py         # Schema validation (33 checks)
├── stat_packs/                    # Generated team stat packs (10 teams)
├── tests/                         # Test suite (65 pytest tests)
├── notebooks/                     # Jupyter notebooks
│   ├── explore.ipynb              # Data exploration
│   └── view_explorer.ipynb        # Interactive SQL queries
├── editorial/                     # Reviews & analysis
│   ├── flower_reviews/            # Cricket domain reviews
│   ├── sprint_reviews/            # Sprint summaries
│   └── clustering/                # Clustering PRD & archetypes
├── founder_review/                # Founder review & responses
├── ml_ops/                        # ML operations
│   ├── model_registry.json        # Model versioning
│   └── deployment_manifest.md     # Deployment status
└── docs/                          # Documentation
    └── PRD_CRICKET_PLAYBOOK.md    # Product requirements
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

## Player Classification Models

### Clustering Model (K-means V2)

**Algorithm:** K-means clustering with PCA dimensionality reduction

**Batter Role Tags:**
| Tag | Count | Description |
|-----|-------|-------------|
| EXPLOSIVE_OPENER | 15 | Aggressive openers with 163+ SR |
| PLAYMAKER | 24 | Creative stroke-makers, adaptable |
| ANCHOR | 21 | Stabilizers, build innings |
| ACCUMULATOR | 49 | Consistent run-scorers |
| MIDDLE_ORDER | 45 | Middle-order specialists (#3-5) |
| FINISHER | 21 | Death-overs specialists |

**Bowler Role Tags:**
| Tag | Count | Description |
|-----|-------|-------------|
| PACER | 116 | Fast/medium-fast bowlers |
| SPINNER | 68 | Spin bowlers |
| WORKHORSE | 112 | High-volume, multi-phase bowlers |
| NEW_BALL_SPECIALIST | 43 | Opening bowlers |
| MIDDLE_OVERS_CONTROLLER | 50 | Middle-phase specialists |
| DEATH_SPECIALIST | 19 | Death-overs specialists |
| PART_TIMER | 44 | Part-time bowling options |

**PCA Variance:** 76.8% (batters), 63.4% (bowlers)

### Matchup Tags

**Bowling Type Matchups (Batters):**
- Tags require **three conditions** to be a specialist: SR ≥130 AND Average ≥25 AND Balls/Dismissal ≥20
- This prevents misclassification of players with high SR but poor dismissal quality
- Example: Aiden Markram has SR 130.9 vs left-arm orthodox but Average 18.0 and BPD 13.75 = NOT specialist

**Phase Performance Tags (Bowlers):**
| Tag | Economy Threshold | Minimum Overs |
|-----|-------------------|---------------|
| PP_BEAST | <7.0 | 30 |
| PP_LIABILITY | >9.5 | 30 |
| MIDDLE_OVERS_BEAST | <7.0 | 50 |
| MIDDLE_OVERS_LIABILITY | >8.5 | 50 |
| DEATH_BEAST | <8.5 | 30 |
| DEATH_LIABILITY | >10.5 | 30 |

**Handedness Tags (Bowlers):**
- `LHB_SPECIALIST` / `RHB_SPECIALIST`: ≥5% better economy vs that handedness
- `LHB_WICKET_TAKER` / `RHB_WICKET_TAKER`: ≥3 wickets + SR <25 vs that handedness
- `LHB_PRESSURE` / `RHB_PRESSURE`: ≥5% higher dot ball % vs that handedness

See `outputs/README.md` for complete tag documentation.

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
| v2.8.0 | 2026-01-25 | **2023+ data filter**, standardized cluster labels, CSV schema docs, Andy Flower review |
| v2.7.0 | 2026-01-24 | Founder Review #3 fixes, phase tags, dismissal quality metrics |
| v2.6.0 | 2026-01-23 | Founder Review #2 fixes, entry point analysis, batter vs bowling type matchups |
| v2.5.0 | 2026-01-21 | Clustering V2, LHB/RHB matchups, ML Ops, repo reorganization |
| v2.4.0 | 2026-01-21 | Founder Review #1 fixes, uncapped player handling |
| v2.3.0 | 2026-01-21 | Multi-tag classification, phase specialists |
| v2.2.0 | 2026-01-20 | Player clustering (K-means, 10 archetypes) |
| v2.1.0 | 2026-01-20 | Percentiles, benchmarks, tests, CLI |
| v2.0.0 | 2026-01-19 | IPL 2026 squads, 26 analytics views |
| v1.0.0 | 2026-01-17 | Initial data ingestion (9,357 matches) |

---

## Next Steps

### Sprint 2.9 - Production Readiness

| Priority | Task | Owner | Status |
|----------|------|-------|--------|
| P0 | Add GitHub Actions CI workflow (lint + test) | Brad Stevens | Planned |
| P0 | Pre-commit hooks (Ruff, mypy) | Brad Stevens | Planned |
| P1 | Model serialization with joblib | Ime Udoka | Planned |
| P1 | Add recency weighting option (toggle 2023+ vs weighted) | Stephen Curry | Planned |
| P2 | Interactive dashboard (Streamlit/Gradio) | Kevin de Bruyne | Planned |
| P2 | Great Expectations data validation | Brock Purdy | Planned |
| P3 | API endpoint for real-time queries | Jayson Tatum | Planned |

### Backlog

- **Venue-specific analysis:** Pitch conditions, toss impact
- **Form tracking:** Rolling 10-match performance
- **Opposition-specific tactics:** Matchup recommendations per opponent
- **Historical trend analysis:** Year-over-year player evolution
- **Injury/availability tracking:** Squad fitness monitoring

## Team

| Agent | Role |
|-------|------|
| Tom Brady | Product Owner |
| Stephen Curry | Analytics Lead |
| Andy Flower | Cricket Domain Expert |
| Brock Purdy | Data Pipeline |
| N'Golo Kanté | QA Engineer |
| Brad Stevens | Requirements & Architecture |
| Ime Udoka | ML Ops Engineer |
| Kevin de Bruyne | Visualization Editor |
| Virat Kohli | Editorial Agent |

## License

Internal use only - Cricket Playbook Editorial Team

---

*Cricket Playbook v2.8.0 - IPL 2026 Analytics Platform*
