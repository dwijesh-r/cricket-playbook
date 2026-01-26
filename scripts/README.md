# Scripts

Python scripts organized by purpose.

---

## Directory Structure

```
scripts/
├── core/           # Data pipeline and validation
├── generators/     # Output file generators
├── analysis/       # Player analysis and clustering
├── utils/          # Utility functions
├── archive/        # Legacy scripts (deprecated)
└── run_stat_packs.sh  # CLI entry point
```

---

## Core (`core/`)

| Script | Description |
|--------|-------------|
| `ingest.py` | Load Cricsheet data into DuckDB |
| `analytics_ipl.py` | Create 34 analytics views |
| `validate_schema.py` | Run 33 schema validation checks |

---

## Generators (`generators/`)

| Script | Description |
|--------|-------------|
| `generate_stat_packs.py` | Generate all 10 team stat packs |
| `generate_2023_outputs.py` | Generate 2023+ filtered outputs |
| `generate_all_2023_outputs.py` | Batch generate all 2023+ files |
| `sprint_3_p1_features.py` | Generate P1 feature outputs |

---

## Analysis (`analysis/`)

| Script | Description |
|--------|-------------|
| `player_clustering_v2.py` | K-means clustering for player archetypes |
| `batter_bowling_type_matchup.py` | Batter vs bowling type analysis |
| `bowler_handedness_matchup.py` | Bowler vs LHB/RHB analysis |
| `bowler_phase_tags.py` | Phase-based bowler tagging |
| `entry_point_analysis.py` | Batter entry point classification |

---

## Utils (`utils/`)

| Script | Description |
|--------|-------------|
| `model_serializer.py` | Serialize ML models with joblib |
| `validate_outputs.py` | Validate output file integrity |
| `generate_experience_csv.py` | Generate squad experience data |

---

## Archive (`archive/`)

Legacy scripts kept for reference. Do not use in production.

| Script | Superseded By |
|--------|---------------|
| `analytics.py` | `core/analytics_ipl.py` |
| `player_clustering.py` | `analysis/player_clustering_v2.py` |
| `founder_review_*_fixes.py` | One-time fix scripts |

---

## Usage

```bash
# Full pipeline
python scripts/core/ingest.py
python scripts/core/analytics_ipl.py
python scripts/generators/generate_stat_packs.py

# Or use CLI
./scripts/run_stat_packs.sh --validate
```

---

*Cricket Playbook v3.1.0*
