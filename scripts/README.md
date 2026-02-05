# Scripts

Python scripts organized by purpose for the Cricket Playbook analytics platform.

**Version:** 4.1.0 | **Last Updated:** 2026-02-05

---

## Quick Start

```bash
# Full data pipeline (run in order)
python scripts/core/ingest.py
python scripts/core/analytics_ipl.py
python scripts/core/validate_schema.py

# Generate outputs
python scripts/generators/generate_stat_packs.py
python scripts/generators/generate_predicted_xii.py
python scripts/generators/generate_depth_charts.py

# Update dashboard
python scripts/the_lab/update_the_lab.py
```

---

## Directory Structure

```
scripts/
├── README.md               # This file
├── run_stat_packs.sh       # CLI entry point for stat pack generation
│
├── core/                   # Data pipeline and validation
│   ├── ingest.py           # Load Cricsheet data into DuckDB
│   ├── analytics_ipl.py    # Create 35+ analytics views
│   └── validate_schema.py  # Run 33 schema validation checks
│
├── generators/             # Output file generators
│   ├── README.md           # Detailed generator documentation
│   ├── generate_stat_packs.py      # Generate all 10 team stat packs
│   ├── generate_predicted_xii.py   # SUPER SELECTOR v3.0 - Predicted XI
│   ├── generate_depth_charts.py    # Team depth chart generation
│   ├── generate_2023_outputs.py    # Generate 2023+ filtered outputs
│   ├── generate_all_2023_outputs.py # Batch generate all 2023+ files
│   └── sprint_3_p1_features.py     # P1 feature outputs
│
├── the_lab/                # The Lab Dashboard data pipeline
│   ├── update_the_lab.py   # Regenerate JS data files for dashboard
│   └── dashboard/          # Static dashboard (GitHub Pages)
│       ├── index.html      # Home page
│       ├── teams.html      # Team analysis with depth charts
│       ├── analysis.html   # League-wide analysis
│       └── data/           # Generated JS data files
│
├── analysis/               # Player analysis and clustering
│   ├── player_clustering_v2.py       # K-means clustering (current)
│   ├── batter_bowling_type_matchup.py # Batter vs bowling style
│   ├── bowler_handedness_matchup.py  # Bowler vs LHB/RHB
│   ├── bowler_phase_tags.py          # Phase-based tagging
│   └── entry_point_analysis.py       # Entry position classification
│
├── utils/                  # Utility functions
│   ├── model_serializer.py      # Serialize ML models (joblib)
│   ├── validate_outputs.py      # Validate output integrity
│   └── generate_experience_csv.py # Squad experience data
│
├── mission_control/        # Task management CLI
│   ├── mc.py               # CLI entry point
│   └── ...                 # See mission_control docs
│
├── hooks/                  # Git hooks
│   └── check_naming_convention.py # Pre-commit naming checks
│
└── archive/                # Legacy scripts (deprecated)
    └── README.md           # Archive documentation
```

---

## Core Pipeline (`core/`)

The main data pipeline scripts. **Run in order** for fresh database setup.

### `ingest.py` - Data Ingestion

**Purpose:** Ingests Cricsheet T20 ball-by-ball JSON data into DuckDB.

**Usage:**
```bash
python scripts/core/ingest.py
```

**Input:**
- `data/raw/*.zip` - Cricsheet data archives (T20, IPL, etc.)

**Output:**
- `data/cricket_playbook.duckdb` - Main database
- `data/manifests/manifest.json` - Ingestion log
- `data/processed/schema.md` - Schema documentation

**Tables Created:**
| Table | Description |
|-------|-------------|
| `dim_tournament` | Tournament metadata |
| `dim_team` | Team dimension |
| `dim_venue` | Venue dimension |
| `dim_player` | Player dimension with role detection |
| `dim_player_name_history` | Player name changes over time |
| `dim_match` | Match metadata |
| `fact_ball` | Ball-by-ball data with match_phase |
| `fact_powerplay` | Powerplay overs |
| `fact_player_match_performance` | Per-match player stats |

### `analytics_ipl.py` - Analytics Views

**Purpose:** Creates 35+ IPL-specific analytical views for batting, bowling, and matchup analysis.

**Usage:**
```bash
python scripts/core/analytics_ipl.py
```

**Input:**
- `data/cricket_playbook.duckdb` - Database from ingest
- `data/ipl_2026_squads.csv` - IPL 2026 squad data
- `data/ipl_2026_player_contracts.csv` - Contract data

**Output:**
- Creates views in DuckDB (no file output)

**Key Views Created:**
| Category | Views |
|----------|-------|
| Batting Career | `analytics_ipl_batting_career`, `analytics_ipl_batter_phase` |
| Bowling Career | `analytics_ipl_bowling_career`, `analytics_ipl_bowler_phase` |
| Matchups | `analytics_ipl_batter_vs_bowler`, `analytics_ipl_batter_vs_bowler_type` |
| Team Analysis | `analytics_ipl_batter_vs_team`, `analytics_ipl_bowler_vs_team` |
| Squad Views | `analytics_ipl_squad_batting`, `analytics_ipl_squad_bowling` |
| Benchmarks | `analytics_ipl_batting_percentiles`, `analytics_ipl_bowling_benchmarks` |

### `validate_schema.py` - Schema Validation

**Purpose:** Runs 33 validation checks to ensure database integrity.

**Usage:**
```bash
python scripts/core/validate_schema.py
```

**Validations:**
1. Required tables exist with correct columns
2. Required views are queryable
3. Referential integrity (FK relationships)
4. Data quality metrics (counts, coverage)
5. Bowling style classification coverage

**Exit Codes:**
- `0` - All validations passed
- `1` - One or more validations failed

---

## Generators (`generators/`)

Scripts that produce output files. See [`generators/README.md`](generators/README.md) for detailed documentation.

| Script | Description | Output |
|--------|-------------|--------|
| `generate_stat_packs.py` | Generate all 10 team stat packs | `stat_packs/*.md` |
| `generate_predicted_xii.py` | **SUPER SELECTOR v3.0** - Predicted XI algorithm | `outputs/predicted_xii/*.json` |
| `generate_depth_charts.py` | Team depth chart generation | `outputs/depth_charts/*.json` |
| `generate_2023_outputs.py` | Generate 2023+ filtered outputs | `outputs/*_2023.csv` |
| `generate_all_2023_outputs.py` | Batch all 2023+ outputs | Multiple files |
| `sprint_3_p1_features.py` | P1 feature outputs | Consistency, synergy, pressure |

**Quick Generation:**
```bash
# Generate stat packs
python scripts/generators/generate_stat_packs.py

# Generate predicted XIIs for all teams
python scripts/generators/generate_predicted_xii.py

# Generate depth charts
python scripts/generators/generate_depth_charts.py

# Generate all 2023+ outputs
python scripts/generators/generate_all_2023_outputs.py
```

---

## The Lab (`the_lab/`)

Interactive analytics dashboard for showcasing IPL 2026 pre-season insights.

**Live Dashboard:** [https://dwijesh-r.github.io/cricket-playbook/scripts/the_lab/dashboard/](https://dwijesh-r.github.io/cricket-playbook/scripts/the_lab/dashboard/)

### `update_the_lab.py` - Dashboard Data Pipeline

**Purpose:** Regenerates JavaScript data files from JSON/CSV outputs for the static dashboard.

**Usage:**
```bash
python scripts/the_lab/update_the_lab.py
```

**Input:**
- `outputs/predicted_xii/*.json` - Predicted XI data
- `outputs/depth_charts/*.json` - Depth chart data
- `outputs/tags/player_tags.json` - Player tags

**Output:**
- `scripts/the_lab/dashboard/data/teams.js` - Team metadata
- `scripts/the_lab/dashboard/data/predicted_xii.js` - Predicted XI + ratings
- `scripts/the_lab/dashboard/data/depth_charts.js` - Full depth chart data

### Dashboard Features (v4.1)
- Squad Search & Filters - Search players, filter by role/nationality/age
- Team Comparison View - Side-by-side metrics comparison
- Inline Depth Charts - Full position-by-position breakdown
- CSV Export - Download squad data for offline analysis
- Phil Steele Style Roster - Compact squad overview

---

## Analysis (`analysis/`)

Player analysis and classification scripts.

| Script | Description | Output |
|--------|-------------|--------|
| `player_clustering_v2.py` | K-means clustering (5 clusters) | `outputs/tags/player_clustering_2023.csv` |
| `batter_bowling_type_matchup.py` | Batter vs 6 bowling styles | `outputs/matchups/batter_bowling_type_*.csv` |
| `bowler_handedness_matchup.py` | Bowler vs LHB/RHB | `outputs/matchups/bowler_handedness_*.csv` |
| `bowler_phase_tags.py` | Phase-based bowler tags | `outputs/metrics/bowler_phase_*.csv` |
| `entry_point_analysis.py` | Batter entry classification | `outputs/matchups/batter_entry_points_*.csv` |

**Usage:**
```bash
# Run clustering
python scripts/analysis/player_clustering_v2.py

# Run matchup analysis
python scripts/analysis/batter_bowling_type_matchup.py
python scripts/analysis/bowler_handedness_matchup.py
```

---

## Utils (`utils/`)

Utility and helper scripts.

| Script | Description | Usage |
|--------|-------------|-------|
| `logging_config.py` | Shared logging configuration | All scripts |
| `model_serializer.py` | Serialize/load ML models | Model persistence |
| `validate_outputs.py` | Validate output file integrity | QA checks |
| `generate_experience_csv.py` | Generate squad experience | Team analysis |

### Logging Configuration

All scripts use a shared logging configuration via `utils/logging_config.py`. This provides consistent log formatting across the project.

**Usage in scripts:**
```python
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Usage examples:
logger.info("Starting stat pack generation for %s", team)
logger.debug("Query returned %d rows", len(results))
logger.warning("Missing data for player: %s", player_name)
logger.error("Failed to generate stat pack: %s", str(e))
```

**Log Levels:**
| Level | Description | When to Use |
|-------|-------------|-------------|
| `INFO` | Key milestones | Starting, completed, counts |
| `DEBUG` | Detailed info | Query results, intermediate values |
| `WARNING` | Non-fatal issues | Missing data, fallbacks used |
| `ERROR` | Failures | Exceptions that don't crash the script |

**Log Format:**
```
2026-02-05 10:30:45 | INFO     | module_name | Starting process
```

**File Logging (Optional):**
```python
# Enable file logging to outputs/logs/
logger = setup_logger(__name__, log_to_file=True)
```

**Environment Variable:**
Set `LOG_LEVEL` environment variable to control verbosity:
- `quiet` - Only warnings and errors
- `normal` - Info and above (default)
- `verbose` - Debug and above

---

## Mission Control (`mission_control/`)

Task management CLI and dashboard for coordinating agent work.

**Live Dashboard:** [https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/)

| Component | Description |
|-----------|-------------|
| `mc.py` | CLI entry point for ticket/sprint/epic management |
| `models/` | Data models (Ticket, Epic, Sprint) |
| `commands/` | CLI command handlers |
| `workflow/` | State machine and transition logic |
| `dashboard/` | Static HTML dashboard (GitHub Pages) |

**Quick Commands:**
```bash
# Show status
python scripts/mission_control/mc.py status

# List tickets
python scripts/mission_control/mc.py ticket list

# View kanban board
python scripts/mission_control/mc.py board
```

See `.mission-control/README.md` for full CLI documentation.

---

## Archive (`archive/`)

**Do not use in production.** Legacy scripts kept for reference.

| Script | Status | Replacement |
|--------|--------|-------------|
| `analytics.py` | Deprecated | `core/analytics_ipl.py` |
| `player_clustering.py` | Deprecated | `analysis/player_clustering_v2.py` |
| `founder_review_*_fixes.py` | One-time | N/A |

See [`archive/README.md`](archive/README.md) for archive policy.

---

## CLI Runner

```bash
# Run with validation
./scripts/run_stat_packs.sh --validate

# Run without validation
./scripts/run_stat_packs.sh
```

---

## Common Workflows

### Full Regeneration
```bash
python scripts/core/analytics_ipl.py
python scripts/analysis/player_clustering_v2.py
python scripts/generators/generate_all_2023_outputs.py
python scripts/generators/generate_predicted_xii.py
python scripts/generators/generate_depth_charts.py
python scripts/generators/generate_stat_packs.py
python scripts/the_lab/update_the_lab.py
```

### After Data Update
```bash
python scripts/core/ingest.py
python scripts/core/analytics_ipl.py
python scripts/core/validate_schema.py
```

### Before Commit
```bash
python scripts/core/validate_schema.py
python scripts/utils/validate_outputs.py
pytest tests/ -v
```

### Dashboard Update Only
```bash
python scripts/the_lab/update_the_lab.py
# Then commit and push to trigger GitHub Pages deploy
```

---

## Environment Setup

**Required Python packages:**
```bash
pip install duckdb pandas numpy scikit-learn joblib
```

**Database path:** `data/cricket_playbook.duckdb`

**Data dependencies:**
- `data/raw/*.zip` - Cricsheet archives
- `data/ipl_2026_squads.csv` - Squad data
- `data/ipl_2026_player_contracts.csv` - Contract data

---

## Script Owners

| Script Category | Owner |
|-----------------|-------|
| core/ | Brock Purdy |
| generators/ | Stephen Curry |
| analysis/ | Stephen Curry |
| utils/ | Ime Udoka |
| the_lab/ | Kevin de Bruyne (visualization), Stephen Curry (data) |
| mission_control/ | Tom Brady (ownership), Brad Stevens (architecture) |

---

## Troubleshooting

### Database not found
```bash
# Ensure database exists
ls -la data/cricket_playbook.duckdb

# If missing, run ingestion
python scripts/core/ingest.py
```

### View does not exist
```bash
# Recreate analytics views
python scripts/core/analytics_ipl.py
```

### Validation failures
```bash
# Check specific validation
python scripts/core/validate_schema.py

# Review errors and fix data issues
```

### Import errors
```bash
# Ensure running from project root
cd /path/to/cricket-playbook
python scripts/generators/generate_stat_packs.py
```

---

*Cricket Playbook v4.1.0*
