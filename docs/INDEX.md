# Cricket Playbook - Repository Index

**Last Updated:** 2026-02-04 | **Version:** v4.0.0 | **Algorithm:** SUPER SELECTOR v3.0

---

## Quick Links

| Category | Key Files |
|----------|-----------|
| **Start Here** | [README](../README.md) · [CLAUDE.md](../CLAUDE.md) · [Constitution](../config/CONSTITUTION.md) |
| **Current Sprint** | [Sprint 4 Status](./sprints/SPRINT_4_STATUS_020426.md) · [Sprint 4 Plan](./SPRINT_4_PLAN.md) |
| **Algorithm** | [SUPER SELECTOR v3.0](./SUPER_SELECTOR.md) · [PRD](../governance/tasks/PREDICTED_XII_V3_PRD.md) |

---

## 1. Governance (`/governance/`)

### Core Documents
| File | Description |
|------|-------------|
| [TASK_INTEGRITY_LOOP.md](../governance/TASK_INTEGRITY_LOOP.md) | 8-step quality process |
| [CONSTITUTION.md](../config/CONSTITUTION.md) | Binding governance framework |
| [CLAUDE.md](../CLAUDE.md) | AI assistant operating principles |

### Task PRDs (`/governance/tasks/`)
| File | Description |
|------|-------------|
| [PREDICTED_XII_V3_PRD.md](../governance/tasks/PREDICTED_XII_V3_PRD.md) | SUPER SELECTOR algorithm PRD |

---

## 2. Configuration (`/config/`)

### Agent Personas (`/config/agents/`)
| Agent | Role |
|-------|------|
| [andy_flower.md](../config/agents/andy_flower.md) | Domain Expert (Cricket) |
| [brad_stevens.md](../config/agents/brad_stevens.md) | Ops Lead |
| [brock_purdy.md](../config/agents/brock_purdy.md) | Data Quality |
| [florentino_perez.md](../config/agents/florentino_perez.md) | Gate Keeper |
| [ime_udoka.md](../config/agents/ime_udoka.md) | DevOps Lead |
| [kevin_de_bruyne.md](../config/agents/kevin_de_bruyne.md) | Visualization |
| [n_golo_kante.md](../config/agents/n_golo_kante.md) | QA Lead |
| [stephen_curry.md](../config/agents/stephen_curry.md) | Analytics Lead |
| [tom_brady.md](../config/agents/tom_brady.md) | Project Lead |

### Templates (`/config/templates/`)
- Agent templates and configuration files

---

## 3. Data (`/data/`)

### Primary Data Files
| File | Description |
|------|-------------|
| `cricket_playbook.duckdb` | Main analytics database (159MB) |
| [ipl_2026_squads.csv](../data/ipl_2026_squads.csv) | Team rosters (231 players) |
| [ipl_2026_player_contracts.csv](../data/ipl_2026_player_contracts.csv) | Contract/auction data |
| [bowler_classifications_v3.csv](../data/bowler_classifications_v3.csv) | Bowler type classifications |

### Subdirectories
| Directory | Contents |
|-----------|----------|
| `/data/raw/` | Cricsheet source data (18 ZIP files) |
| `/data/processed/` | Intermediate processed files |
| `/data/manifests/` | Data manifest files |
| `/data/archive/` | Old data versions |

---

## 4. Scripts (`/scripts/`)

### Core Pipeline (`/scripts/core/`)
| Script | Purpose |
|--------|---------|
| `ingest_cricsheet.py` | Data ingestion from Cricsheet |
| `analytics_pipeline.py` | Main analytics processing |
| `validation_checks.py` | Data validation |

### Generators (`/scripts/generators/`)
| Script | Purpose |
|--------|---------|
| [generate_predicted_xii.py](../scripts/generators/generate_predicted_xii.py) | **SUPER SELECTOR v3.0** - Predicted XI algorithm |
| `generate_depth_charts.py` | Team depth chart generation |
| `generate_stat_packs.py` | Team stat pack generation |

### Analysis (`/scripts/analysis/`)
| Script | Purpose |
|--------|---------|
| `player_clustering.py` | Player type clustering |
| `phase_analysis.py` | Phase-based performance analysis |

### Utilities (`/scripts/utils/`)
- Helper functions and utilities

### Hooks (`/scripts/hooks/`)
- Git hooks and automation scripts

---

## 5. Outputs (`/outputs/`)

### Predicted XIIs (`/outputs/predicted_xii/`)
| Team | JSON |
|------|------|
| All Teams | [predicted_xii_2026.json](../outputs/predicted_xii/predicted_xii_2026.json) |
| CSK | [csk_predicted_xii.json](../outputs/predicted_xii/csk_predicted_xii.json) |
| MI | [mi_predicted_xii.json](../outputs/predicted_xii/mi_predicted_xii.json) |
| RCB | [rcb_predicted_xii.json](../outputs/predicted_xii/rcb_predicted_xii.json) |
| KKR | [kkr_predicted_xii.json](../outputs/predicted_xii/kkr_predicted_xii.json) |
| DC | [dc_predicted_xii.json](../outputs/predicted_xii/dc_predicted_xii.json) |
| PBKS | [pbks_predicted_xii.json](../outputs/predicted_xii/pbks_predicted_xii.json) |
| RR | [rr_predicted_xii.json](../outputs/predicted_xii/rr_predicted_xii.json) |
| SRH | [srh_predicted_xii.json](../outputs/predicted_xii/srh_predicted_xii.json) |
| GT | [gt_predicted_xii.json](../outputs/predicted_xii/gt_predicted_xii.json) |
| LSG | [lsg_predicted_xii.json](../outputs/predicted_xii/lsg_predicted_xii.json) |

### Depth Charts (`/outputs/depth_charts/`)
| Team | Markdown | HTML |
|------|----------|------|
| MI | [MI_depth_chart.md](../outputs/depth_charts/MI_depth_chart.md) | [MI_depth_chart.html](../outputs/depth_charts/MI_depth_chart.html) |
| CSK | [CSK_depth_chart.md](../outputs/depth_charts/CSK_depth_chart.md) | [CSK_depth_chart.html](../outputs/depth_charts/CSK_depth_chart.html) |
| RCB | [RCB_depth_chart.md](../outputs/depth_charts/RCB_depth_chart.md) | [RCB_depth_chart.html](../outputs/depth_charts/RCB_depth_chart.html) |
| KKR | [KKR_depth_chart.md](../outputs/depth_charts/KKR_depth_chart.md) | [KKR_depth_chart.html](../outputs/depth_charts/KKR_depth_chart.html) |

### Tags (`/outputs/tags/`)
| File | Description |
|------|-------------|
| `player_tags_2023.json` | Player classification tags |
| `player_clustering_2023.csv` | Cluster assignments |

### Metrics (`/outputs/metrics/`)
| File | Description |
|------|-------------|
| `batter_consistency_index.csv` | Batting consistency scores |
| `bowler_pressure_sequences.csv` | Bowling pressure metrics |
| `bowler_phase_performance.csv` | Phase-based bowling stats |

### Matchups (`/outputs/matchups/`)
| File | Description |
|------|-------------|
| `batter_entry_points_2023.csv` | Batting entry point analysis |

---

## 6. Stat Packs (`/stat_packs/`)

| Team | Stat Pack |
|------|-----------|
| CSK | [CSK_stat_pack.md](../stat_packs/CSK/CSK_stat_pack.md) |
| MI | [MI_stat_pack.md](../stat_packs/MI/MI_stat_pack.md) |
| RCB | [RCB_stat_pack.md](../stat_packs/RCB/RCB_stat_pack.md) |
| KKR | [KKR_stat_pack.md](../stat_packs/KKR/KKR_stat_pack.md) |
| DC | [DC_stat_pack.md](../stat_packs/DC/DC_stat_pack.md) |
| PBKS | [PBKS_stat_pack.md](../stat_packs/PBKS/PBKS_stat_pack.md) |
| RR | [RR_stat_pack.md](../stat_packs/RR/RR_stat_pack.md) |
| SRH | [SRH_stat_pack.md](../stat_packs/SRH/SRH_stat_pack.md) |
| GT | [GT_stat_pack.md](../stat_packs/GT/GT_stat_pack.md) |
| LSG | [LSG_stat_pack.md](../stat_packs/LSG/LSG_stat_pack.md) |

---

## 7. Documentation (`/docs/`)

### Algorithm Documentation
| File | Description |
|------|-------------|
| [SUPER_SELECTOR.md](./SUPER_SELECTOR.md) | **Predicted XII algorithm v3.0** |
| [PRD_CRICKET_PLAYBOOK.md](./PRD_CRICKET_PLAYBOOK.md) | Product requirements |

### Sprint Documentation (`/docs/sprints/`)
| File | Description |
|------|-------------|
| [SPRINT_4_STATUS_020426.md](./sprints/SPRINT_4_STATUS_020426.md) | Current sprint status |
| [SPRINT_4_PLAN.md](./SPRINT_4_PLAN.md) | Sprint 4 plan |

### Specifications (`/docs/specs/`)
| File | Description |
|------|-------------|
| [player_clustering_prd.md](./specs/player_clustering_prd.md) | Clustering methodology |
| [cluster_labels_v1.0.md](./specs/cluster_labels_v1.0.md) | Label definitions |

### Research (`/docs/research/`)
| File | Description |
|------|-------------|
| [kenpom_methodology_research.md](./research/kenpom_methodology_research.md) | Rating system research |
| [pff_grading_system_research.md](./research/pff_grading_system_research.md) | Grading research |

---

## 8. Analysis (`/analysis/`)

| File | Description |
|------|-------------|
| [threshold_eda_2023.md](../analysis/threshold_eda_2023.md) | Statistical thresholds |
| [player_id_audit_report.md](../analysis/player_id_audit_report.md) | ID mismatch report |
| [entry_point_audit_report.md](../analysis/entry_point_audit_report.md) | Batter positions |
| [baselines_vs_tags.md](../analysis/baselines_vs_tags.md) | Methodology explanation |

---

## 9. Reviews (`/reviews/`)

### Founder Reviews (`/reviews/founder/`)
| File | Description |
|------|-------------|
| [sprint_4_checkin_response_020426_v1.md](../reviews/founder/sprint_4_checkin_response_020426_v1.md) | Latest check-in |
| [Mission Control PRD Draft.md](../reviews/founder/Mission%20Control%20PRD%20Draft.md) | Infrastructure PRD |
| [review_5.pdf](../reviews/founder/review_5.pdf) | Review 5 |
| [mega_review_1.pdf](../reviews/founder/mega_review_1.pdf) | Mega Review 1 |

### Domain Reviews (`/reviews/domain/`)
| File | Description |
|------|-------------|
| [andy_flower_analytics_research.md](../reviews/domain/andy_flower_analytics_research.md) | Analytics review |
| [andy_flower_tag_validation.md](../reviews/domain/andy_flower_tag_validation.md) | Tag validation |
| [phase_metrics_review.md](../reviews/domain/phase_metrics_review.md) | Phase metrics |
| [phase_tag_criteria.md](../reviews/domain/phase_tag_criteria.md) | Tag thresholds |

---

## 10. ML Ops (`/ml_ops/`)

- Model training and serving infrastructure
- Feature engineering pipelines

---

## 11. Notebooks (`/notebooks/`)

- Jupyter notebooks for exploration and analysis

---

## 12. Archive (`/archive/`)

| Directory | Contents |
|-----------|----------|
| `/archive/2026-02-04/` | Latest archive |
| `/archive/2026-02-04/data_old_versions/` | Old data files |
| `/archive/2026-02-04/docs_superseded/` | Superseded docs |
| `/archive/2026-02-04/outputs_duplicates/` | Duplicate outputs |
| `/archive/2026-02-04/reviews_historical/` | Historical reviews |

---

## 13. CI/CD (`.github/workflows/`)

| File | Purpose |
|------|---------|
| Pre-commit hooks | Ruff linting, formatting, naming conventions |

---

## Directory Tree Summary

```
cricket-playbook/
├── analysis/           # Analysis reports
├── archive/            # Historical files
├── config/             # Configuration & agents
│   ├── agents/         # 14 agent personas
│   └── templates/      # Templates
├── data/               # Data files
│   ├── raw/            # Source data
│   └── processed/      # Processed data
├── docs/               # Documentation
│   ├── specs/          # Specifications
│   ├── sprints/        # Sprint docs
│   └── research/       # Research
├── governance/         # Governance docs
│   └── tasks/          # Task PRDs
├── ml_ops/             # ML infrastructure
├── notebooks/          # Jupyter notebooks
├── outputs/            # Generated outputs
│   ├── predicted_xii/  # Predicted XIs
│   ├── depth_charts/   # Depth charts
│   ├── tags/           # Player tags
│   └── metrics/        # Metrics
├── reviews/            # Reviews
│   ├── founder/        # Founder reviews
│   └── domain/         # Domain reviews
├── scripts/            # Python scripts
│   ├── core/           # Pipeline
│   ├── generators/     # Generators
│   └── analysis/       # Analysis
└── stat_packs/         # Team stat packs
    ├── CSK/
    ├── MI/
    └── ...
```

---

*Cricket Playbook v4.0.0 | SUPER SELECTOR v3.0*
*Index generated: 2026-02-04*
