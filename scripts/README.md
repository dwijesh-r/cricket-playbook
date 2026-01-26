# Scripts

Python scripts organized by purpose.

**Version:** 3.1.0 | **Last Updated:** 2026-01-26

---

## Directory Structure

```
scripts/
├── README.md               # This file
├── run_stat_packs.sh       # CLI entry point
│
├── core/                   # Data pipeline and validation
│   ├── ingest.py           # Load Cricsheet data into DuckDB
│   ├── analytics_ipl.py    # Create 34 analytics views
│   └── validate_schema.py  # Run 33 schema validation checks
│
├── generators/             # Output file generators
│   ├── generate_stat_packs.py      # Generate all 10 team stat packs
│   ├── generate_2023_outputs.py    # Generate 2023+ filtered outputs
│   ├── generate_all_2023_outputs.py # Batch generate all 2023+ files
│   └── sprint_3_p1_features.py     # P1 feature outputs
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
└── archive/                # Legacy scripts (deprecated)
    ├── analytics.py              # Superseded by core/analytics_ipl.py
    ├── player_clustering.py      # Superseded by analysis/player_clustering_v2.py
    ├── founder_review_1_fixes.py # One-time fix script
    └── founder_review_2_fixes.py # One-time fix script
```

---

## Core Pipeline (`core/`)

The main data pipeline scripts. Run in order.

| Script | Description | Output |
|--------|-------------|--------|
| `ingest.py` | Load Cricsheet JSON into DuckDB | `data/cricket_playbook.duckdb` |
| `analytics_ipl.py` | Create 34 analytics views | Views in DuckDB |
| `validate_schema.py` | 33 schema validation checks | Pass/fail report |

```bash
# Full pipeline
python scripts/core/ingest.py
python scripts/core/analytics_ipl.py
python scripts/core/validate_schema.py
```

---

## Generators (`generators/`)

Scripts that produce output files.

| Script | Description | Output |
|--------|-------------|--------|
| `generate_stat_packs.py` | Generate all 10 team stat packs | `stat_packs/*.md` |
| `generate_2023_outputs.py` | Generate 2023+ filtered outputs | `outputs/*_2023.csv` |
| `generate_all_2023_outputs.py` | Batch all 2023+ outputs | Multiple files |
| `sprint_3_p1_features.py` | P1 feature outputs | Consistency, synergy, pressure |

```bash
# Generate stat packs
python scripts/generators/generate_stat_packs.py

# Generate all 2023+ outputs
python scripts/generators/generate_all_2023_outputs.py
```

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
| `model_serializer.py` | Serialize/load ML models | Model persistence |
| `validate_outputs.py` | Validate output file integrity | QA checks |
| `generate_experience_csv.py` | Generate squad experience | Team analysis |

---

## Archive (`archive/`)

**Do not use in production.** Legacy scripts kept for reference.

| Script | Status | Replacement |
|--------|--------|-------------|
| `analytics.py` | Deprecated | `core/analytics_ipl.py` |
| `player_clustering.py` | Deprecated | `analysis/player_clustering_v2.py` |
| `founder_review_*_fixes.py` | One-time | N/A |

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
python scripts/generators/generate_stat_packs.py
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

---

## Script Owners

| Script Category | Owner |
|-----------------|-------|
| core/ | Brock Purdy |
| generators/ | Stephen Curry |
| analysis/ | Stephen Curry |
| utils/ | Ime Udoka |

---

*Cricket Playbook v3.1.0*
