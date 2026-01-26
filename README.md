# Cricket Playbook

IPL 2026 Analytics Platform for editorial and broadcast use.

---

## Quick Start

```bash
python scripts/core/analytics_ipl.py      # Create analytics views
python scripts/generators/generate_stat_packs.py  # Generate team stat packs
```

---

## Directory Structure

```
cricket-playbook/
├── analysis/       # EDA reports and data audits
├── config/         # Agent definitions and templates
├── data/           # Source data and DuckDB database
├── docs/           # Documentation and specifications
├── ml_ops/         # Model registry and deployment
├── notebooks/      # Jupyter notebooks for exploration
├── outputs/        # Generated CSV/JSON outputs
├── reviews/        # Founder, domain, and sprint reviews
├── scripts/        # Python scripts (organized by purpose)
├── stat_packs/     # Team statistical reports (10 teams)
└── tests/          # Test suite
```

---

## Data Summary

| Metric | Value |
|--------|-------|
| IPL Analytics Data | 2023-2025 (219 matches) |
| Ball-by-ball Records | 2,137,915 |
| IPL 2026 Squad Players | 231 |
| Analytics Views | 34 |

---

## Key Directories

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `scripts/core/` | Data pipeline | `ingest.py`, `analytics_ipl.py` |
| `scripts/generators/` | Output generation | `generate_stat_packs.py` |
| `scripts/analysis/` | Player analysis | `player_clustering_v2.py` |
| `outputs/tags/` | Player classifications | `player_tags.json` |
| `outputs/matchups/` | Head-to-head data | `batter_bowling_type_*.csv` |
| `outputs/metrics/` | Performance metrics | `batter_consistency_*.csv` |
| `stat_packs/` | Team reports | `*_stat_pack.md` |
| `reviews/founder/` | Founder feedback | `review_*.pdf`, `response_*.md` |

---

## Match Phases

| Phase | Overs | Description |
|-------|-------|-------------|
| Powerplay | 1-6 | 2 fielders outside circle |
| Middle | 7-15 | Consolidation phase |
| Death | 16-20 | Final acceleration |

---

## Testing

```bash
pytest tests/ -v                          # Run all tests
python scripts/core/validate_schema.py    # Schema validation
```

---

## Version

**v3.1.0** - Sprint 3.1 (Repo Restructure)

---

## Team

| Role | Owner |
|------|-------|
| Product Owner | Tom Brady |
| Analytics Lead | Stephen Curry |
| Domain Expert | Andy Flower |
| Data Pipeline | Brock Purdy |

---

*Cricket Playbook - IPL 2026 Analytics Platform*
