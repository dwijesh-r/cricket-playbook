# Cricket Playbook

**IPL 2026 Analytics Platform** for editorial and broadcast use.

**Version:** 4.0.0 | **Sprint:** 4.0 | **Last Updated:** 2026-02-02

---

## Overview

Cricket Playbook is a comprehensive cricket analytics system built on ball-by-ball T20 data. It provides detailed statistical analysis for all 10 IPL 2026 teams, including player performance metrics, phase-wise breakdowns, matchup analysis, and tactical insights.

**Key Features:**
- 34 DuckDB analytics views for career stats, phase analysis, and matchups
- K-means clustering with 6 batter + 7 bowler archetypes
- Multi-tag player classification system (specialist, vulnerable, phase tags)
- Team stat packs with Andy Flower's tactical insights
- 2023-2025 data focus for current player form analysis
- **NEW:** Predicted XII - Algorithm-generated optimal playing XI + Impact Player
- **NEW:** Depth Charts - Position-by-position rankings with ratings (0-10 scale)

---

## New Here? Start Here.

*A guide from Tom Brady (Product Owner) and Andy Flower (Cricket Domain Expert)*

Welcome to Cricket Playbook. Here's how to get your bearings:

### First 5 Minutes
1. **Read this README** - You're doing it. Good start.
2. **Check `docs/KANBAN.md`** - See what we're working on right now (Sprint 4.0)
3. **Browse `stat_packs/`** - Open any team file (try `MI_stat_pack.md`). This is what we produce.
4. **Check `outputs/predicted_xii/`** - See our algorithm-generated best XIs
5. **Check `outputs/depth_charts/`** - See position-by-position team rankings

### Understanding the Data Flow
```
data/raw/ (Cricsheet ZIPs)
    ↓
scripts/core/ingest.py → data/cricket_playbook.duckdb
    ↓
scripts/core/analytics_ipl.py → 34 analytics views
    ↓
scripts/analysis/*.py → outputs/ (tags, matchups, metrics)
    ↓
scripts/generators/generate_stat_packs.py → stat_packs/
```

### Where to Find What

| You Want | Go Here |
|----------|---------|
| See the final product | `stat_packs/*.md` |
| See predicted best XIs | `outputs/predicted_xii/` |
| See team depth charts | `outputs/depth_charts/` |
| Understand player tags | `outputs/tags/player_tags.json` |
| Run SQL queries | `notebooks/view_explorer.ipynb` |
| See how we classify players | `scripts/analysis/player_clustering_v2.py` |
| Understand our methodology | `docs/research/` (PFF + KenPom studies) |
| Check sprint progress | `docs/KANBAN.md` |
| See founder feedback | `reviews/founder/` |

### The Key Numbers to Know
- **219 matches** - IPL 2023-2025, our analysis window
- **231 players** - IPL 2026 squad size
- **34 views** - Analytics views in DuckDB
- **6 batter archetypes** - EXPLOSIVE_OPENER to FINISHER
- **7 bowler archetypes** - PACER to PART_TIMER

### Andy's Cricket Context Tips
> "If you're not from a cricket background, focus on these concepts first:
> - **Strike Rate** is king in T20. It's runs per 100 balls. Above 140 is good.
> - **Economy** for bowlers. Below 8 runs per over is solid.
> - **Phases matter**: Powerplay (overs 1-6), Middle (7-15), Death (16-20). Different skills needed for each.
> - A 'good' T20 innings is often 30 runs off 20 balls, not 50 off 40."

### Tom's Process Tips
> "We work in sprints. Each sprint responds to Founder feedback. Check `reviews/founder/` to see the feedback cycle. The KANBAN tells you what's done and what's next. When in doubt, ask in the sprint channel."

### Don't
- Don't modify `data/cricket_playbook.duckdb` directly
- Don't commit to main without tests passing
- Don't use data before 2023 for player analysis (stat drift)

### Do
- Explore the notebooks - they're interactive
- Read the stat packs - they're the end product
- Check `analysis/` for our data quality audits
- Run `pytest tests/ -v` before pushing

---

## Quick Start

```bash
# 1. Create analytics views (34 views)
python scripts/core/analytics_ipl.py

# 2. Generate player tags and classifications
python scripts/analysis/player_clustering_v2.py

# 3. Generate team stat packs (10 teams)
python scripts/generators/generate_stat_packs.py

# Or use the CLI with validation
./scripts/run_stat_packs.sh --validate
```

---

## Directory Structure

```
cricket-playbook/
├── README.md               # This file
├── requirements.txt        # Python dependencies
│
├── analysis/               # EDA reports and data audits
│   ├── entry_point_audit_report.md
│   ├── threshold_eda_2023.md
│   └── player_id_audit_report.md
│
├── config/                 # Configuration
│   ├── agents/             # Agent persona definitions (12 agents)
│   ├── templates/          # Output templates
│   └── CONSTITUTION.md     # Agent framework guidelines
│
├── data/                   # Source data
│   ├── cricket_playbook.duckdb    # Main database (159MB)
│   ├── ipl_2026_squads.csv        # Team rosters (231 players)
│   ├── ipl_2026_player_contracts.csv
│   ├── bowler_classifications_v2.csv
│   ├── raw/                # Cricsheet ZIP files (18 datasets)
│   └── processed/          # Intermediate data
│
├── docs/                   # Documentation
│   ├── PRD_CRICKET_PLAYBOOK.md    # Product requirements
│   ├── KANBAN.md                  # Sprint board
│   ├── REPO_RESTRUCTURE_PROPOSAL.md
│   ├── cicd_best_practices.md
│   ├── specs/              # Technical specifications
│   └── research/           # Cross-sport analytics research
│
├── ml_ops/                 # ML operations
│   ├── model_registry.json
│   └── deployment_manifest.md
│
├── notebooks/              # Jupyter notebooks
│   ├── explore.ipynb
│   └── view_explorer.ipynb
│
├── outputs/                # Generated outputs
│   ├── tags/               # Player classifications
│   ├── matchups/           # Head-to-head analysis
│   ├── metrics/            # Performance metrics
│   └── team/               # Team-level data
│
├── reviews/                # All reviews
│   ├── founder/            # Founder reviews & responses
│   ├── domain/             # Cricket domain reviews
│   └── sprint/             # Sprint reviews
│
├── scripts/                # Python scripts
│   ├── core/               # Data pipeline
│   ├── generators/         # Output generators
│   ├── analysis/           # Player analysis
│   ├── utils/              # Utilities
│   └── archive/            # Legacy scripts
│
├── stat_packs/             # Team stat packs (10 teams)
│
└── tests/                  # Test suite
```

---

## Data Summary

| Metric | Value |
|--------|-------|
| Total T20 Matches | 9,357 |
| **IPL Analytics Data** | **2023-2025 (219 matches)** |
| Ball-by-ball Records | 2,137,915 |
| IPL 2026 Squad Players | 231 |
| Bowler Classifications | 280 (98.8% ball coverage) |
| Analytics Views | 34 |

**Note:** All analytics use 2023-2025 IPL data only to reflect current player form and game evolution.

---

## Analytics Views

### Career Statistics
| View | Description |
|------|-------------|
| `analytics_ipl_batting_career` | IPL batting career stats |
| `analytics_ipl_bowling_career` | IPL bowling career stats |

### Phase Analysis
| View | Description |
|------|-------------|
| `analytics_ipl_batter_phase` | Batting by powerplay/middle/death |
| `analytics_ipl_bowler_phase` | Bowling by powerplay/middle/death |

### Matchup Analysis
| View | Description |
|------|-------------|
| `analytics_ipl_batter_vs_bowler` | Head-to-head records |
| `analytics_ipl_batter_vs_bowler_type` | Performance vs bowling styles |
| `analytics_ipl_batter_vs_team` | Performance vs each team |

### Rankings & Benchmarks
| View | Description |
|------|-------------|
| `analytics_ipl_batting_percentiles` | Batting percentile rankings |
| `analytics_ipl_bowling_percentiles` | Bowling percentile rankings |
| `analytics_ipl_batting_benchmarks` | IPL-wide batting averages |
| `analytics_ipl_bowling_benchmarks` | IPL-wide bowling averages |

---

## Player Classification Model

### Batter Role Tags
| Tag | Count | Description |
|-----|-------|-------------|
| EXPLOSIVE_OPENER | 15 | Aggressive openers, 163+ SR |
| PLAYMAKER | 24 | Creative stroke-makers, adaptable |
| ANCHOR | 21 | Stabilizers, build innings |
| ACCUMULATOR | 49 | Consistent run-scorers |
| MIDDLE_ORDER | 45 | Middle-order specialists (#3-5) |
| FINISHER | 21 | Death-overs specialists (#5-7) |

### Bowler Role Tags
| Tag | Count | Description |
|-----|-------|-------------|
| PACER | 116 | Fast/medium-fast bowlers |
| SPINNER | 68 | Spin bowlers (all types) |
| WORKHORSE | 112 | High-volume, multi-phase bowlers |
| NEW_BALL_SPECIALIST | 43 | Opening bowlers, powerplay focus |
| MIDDLE_OVERS_CONTROLLER | 50 | Middle-phase specialists |
| DEATH_SPECIALIST | 19 | Death-overs specialists |
| MIDDLE_AND_DEATH_SPECIALIST | - | Bowls both middle and death |
| PART_TIMER | 44 | Part-time bowling options |

### Matchup Tags
| Tag | Criteria |
|-----|----------|
| SPECIALIST_VS_PACE/SPIN | SR ≥130 AND Avg ≥25 AND BPD ≥20 |
| VULNERABLE_VS_PACE/SPIN | SR <105 OR Avg <15 OR BPD <15 |

### Phase Tags (Bowlers)
| Tag | Threshold | Min Overs |
|-----|-----------|-----------|
| PP_BEAST | Economy <7.0 | 30 |
| PP_LIABILITY | Economy >9.5 | 30 |
| DEATH_BEAST | Economy <9.0 | 30 |
| DEATH_LIABILITY | Economy >12.0 AND SR >18.0 | 30 |

---

## Match Phase Definitions

| Phase | Overs | Balls | Description |
|-------|-------|-------|-------------|
| **Powerplay** | 1-6 | 1-36 | Only 2 fielders outside 30-yard circle |
| **Middle Overs** | 7-15 | 37-90 | 4-5 fielders allowed outside |
| **Death Overs** | 16-20 | 91-120 | Final acceleration phase |

---

## Key Metrics

| Metric | Formula | Good Value (T20) |
|--------|---------|------------------|
| **Strike Rate (SR)** | (Runs ÷ Balls) × 100 | >140 |
| **Economy Rate** | (Runs ÷ Balls) × 6 | <8.0 |
| **Batting Average** | Runs ÷ Dismissals | >30 |
| **Bowling Strike Rate** | Balls ÷ Wickets | <20 |
| **Dot Ball %** | (Dots ÷ Balls) × 100 | Batter: lower; Bowler: higher |
| **Boundary %** | (4s + 6s) ÷ Balls × 100 | >15% = power hitter |

---

## Sample Size Indicators

| Indicator | Balls | Interpretation |
|-----------|-------|----------------|
| HIGH | 100+ (batter) / 300+ (bowler) | Reliable sample |
| MEDIUM | 30-99 / 60-299 | Moderate confidence |
| LOW | <30 / <60 | Use with caution |

---

## Bowling Style Coverage

| Style | Coverage |
|-------|----------|
| Right-arm pace | 49.4% |
| Left-arm pace | 13.6% |
| Right-arm off-spin | 12.4% |
| Right-arm leg-spin | 11.8% |
| Left-arm orthodox | 10.4% |
| Left-arm wrist spin | 1.2% |
| Unknown | 1.2% |

---

## Franchise Aliases

| Current Name | Historical Name |
|--------------|-----------------|
| Delhi Capitals | Delhi Daredevils |
| Punjab Kings | Kings XI Punjab |
| Royal Challengers Bengaluru | Royal Challengers Bangalore |

---

## Testing

```bash
# Run all tests (76 tests)
pytest tests/ -v

# Schema validation (33 checks)
python scripts/core/validate_schema.py

# Output validation
python scripts/utils/validate_outputs.py
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **v4.0.0** | 2026-02-02 | Predicted XII algorithm, Depth Charts, Task Integrity Loop governance |
| v3.1.0 | 2026-01-26 | Repo restructure, PFF/KenPom research, comprehensive READMEs |
| v3.0.1 | 2026-01-26 | Sprint 3.0: 16 new 2023+ outputs, entry point audit, player ID audit |
| v2.9.0 | 2026-01-25 | CI/CD (GitHub Actions, pre-commit), DEATH_LIABILITY threshold fix |
| v2.8.0 | 2026-01-25 | 2023+ data filter, standardized cluster labels, Andy Flower review |
| v2.7.0 | 2026-01-24 | Founder Review #3 fixes, phase tags, dismissal quality metrics |
| v2.6.0 | 2026-01-23 | Founder Review #2 fixes, entry point analysis |
| v2.5.0 | 2026-01-21 | Clustering V2, LHB/RHB matchups, ML Ops |
| v2.0.0 | 2026-01-19 | IPL 2026 squads, 26 analytics views |
| v1.0.0 | 2026-01-17 | Initial data ingestion (9,357 matches) |

---

## Sprint Roadmap

### Current: Sprint 4.0 - Foundation & Editorial Excellence

| Priority | Task | Owner | Status |
|----------|------|-------|--------|
| P0 | Fix 15 player ID mismatches | Brock Purdy | To Do |
| P0 | Regenerate outputs with fixed IDs | Stephen Curry | Blocked |
| P1 | Tactical Insights Review | Andy Flower | To Do |
| P2 | Great Expectations integration | Brock Purdy | To Do |

### Completed in Sprint 4.0
- Predicted XII algorithm (all 10 teams)
- Depth Charts (all 10 teams)
- Task Integrity Loop governance
- Constitution v2.0

### Backlog (Sprint 5.0+)
- KenPom/CricPom Implementation
- REST API (FastAPI)
- Win Probability Model
- Player Form Tracker
- Interactive Dashboard

---

## Team

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Tom Brady** | Product Owner | Sprint planning, PRD, stakeholder coordination |
| **Stephen Curry** | Analytics Lead | SQL views, clustering models, tag generation |
| **Andy Flower** | Cricket Domain Expert | Cluster validation, tactical insights, thresholds |
| **Brock Purdy** | Data Pipeline | Ingestion, schema validation, data quality |
| **N'Golo Kanté** | QA Engineer | Test suite, smoke tests, regression testing |
| **Brad Stevens** | Architecture | CI/CD, code quality, repo structure |
| **Ime Udoka** | ML Ops Engineer | Model registry, deployment, versioning |
| **Kevin de Bruyne** | Visualization | Charts, dashboards, visual outputs |
| **Virat Kohli** | Editorial | Stat pack content, narrative insights |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Database | DuckDB (embedded OLAP) |
| Language | Python 3.12 |
| Testing | pytest |
| Linting | Ruff |
| Pre-commit | ruff, trailing whitespace, EOF |
| Data Source | Cricsheet (ball-by-ball JSON) |

---

## License

Internal use only - Cricket Playbook Editorial Team

---

## Contact

| Role | Owner |
|------|-------|
| Product Owner | Tom Brady |
| Analytics Questions | Stephen Curry |
| Cricket Domain | Andy Flower |
| Data Pipeline | Brock Purdy |

---

*Cricket Playbook v4.0.0 - IPL 2026 Analytics Platform*
