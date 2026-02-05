# Documentation

Project documentation, specifications, and research.

**Version:** 4.0.0 | **Last Updated:** 2026-02-04

---

## Directory Structure

```
docs/
├── README.md                      # This file
├── PRD_CRICKET_PLAYBOOK.md        # Product requirements document
├── KANBAN.md                      # Sprint board (current: Sprint 3.1)
├── REPO_RESTRUCTURE_PROPOSAL.md   # Repository reorganization plan
├── cicd_best_practices.md         # CI/CD and code quality guide
├── specs/                         # Technical specifications
│   ├── WIREFRAMES_V1.md           # UI Wireframes V6 (Predicted XII + Depth Chart)
│   ├── player_clustering_prd.md
│   ├── cluster_archetypes_creative.md
│   ├── cluster_labels_v1.0.md
│   └── andy_flower_v2_validation.md
└── research/                      # Cross-sport analytics research
    ├── pff_grading_system_research.md
    └── kenpom_methodology_research.md
```

---

## Core Documents

| Document | Description | Owner |
|----------|-------------|-------|
| `PRD_CRICKET_PLAYBOOK.md` | Product requirements, data architecture, sprint roadmap | Tom Brady |
| `KANBAN.md` | Sprint board with task tracking (Sprint 3.1 active) | Tom Brady |
| `REPO_RESTRUCTURE_PROPOSAL.md` | Repository reorganization plan with phases | Brad Stevens |
| `cicd_best_practices.md` | CI/CD pipeline, code quality, testing strategy | Brad Stevens |

---

## Technical Specifications (`specs/`)

| Document | Description | Owner |
|----------|-------------|-------|
| `WIREFRAMES_V1.md` | **UI Wireframes V6** - Predicted XII + Depth Chart views (all agents 9.0+) | Kevin de Bruyne |
| `player_clustering_prd.md` | K-means clustering model requirements | Stephen Curry |
| `cluster_archetypes_creative.md` | Player archetype definitions and naming | Andy Flower |
| `cluster_labels_v1.0.md` | Cluster label mappings and criteria | Stephen Curry |
| `andy_flower_v2_validation.md` | Domain validation for clustering v2 | Andy Flower |

---

## Research (`research/`)

Cross-sport analytics research for methodology development.

| Document | Description | Author |
|----------|-------------|--------|
| `pff_grading_system_research.md` | PFF (Pro Football Focus) grading methodology | Ime Udoka |
| `kenpom_methodology_research.md` | KenPom basketball efficiency metrics | Andy Flower |

### Key Research Findings

**PFF Grading:**
- Play-by-play grading (-2 to +2 scale)
- Process over outcome evaluation
- Context-aware adjustments
- Multi-grader quality control

**KenPom Methodology:**
- Adjusted efficiency (opponent-normalized)
- Tempo-free statistics (per-possession)
- Four Factors decomposition
- Venue park factors

### Proposed Cricket Adaptations
- **Adjusted Run Rate (AdjRR)** - Opponent-normalized batting
- **Cricket's Four Factors** - Boundary%, Dot%, Wicket%, Extras%
- **Opposition Strength Index (OSI)** - Schedule difficulty
- **Cricket Efficiency Margin (CEM)** - Team overall quality

---

## Related Documentation

| Location | Description |
|----------|-------------|
| `README.md` (root) | Project overview, quick start, full reference |
| `analysis/README.md` | EDA reports and data audits |
| `outputs/README.md` | Output file documentation |
| `scripts/README.md` | Script documentation by category |
| `reviews/README.md` | Founder and domain reviews |
| `stat_packs/README.md` | Team stat pack structure |
| `ml_ops/README.md` | Model registry and deployment |
| `config/README.md` | Agent and template definitions |
| `data/README.md` | Database schema and data sources |
| `.mission-control/README.md` | Mission Control CLI documentation |
| `governance/README.md` | Task Integrity Loop and governance |

---

## Mission Control

**Live Dashboard:** [https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/)

All sprint tasks are tracked on Mission Control. See `governance/TASK_INTEGRITY_LOOP.md` for the mandatory quality process.

---

## Document Owners

| Owner | Documents |
|-------|-----------|
| Tom Brady | PRD, KANBAN, main README |
| Brad Stevens | CI/CD guide, repo restructure, architecture |
| Stephen Curry | Technical specs, clustering PRD |
| Andy Flower | Domain validation, archetype definitions |
| Ime Udoka | PFF research, ML Ops documentation |

---

*Cricket Playbook v4.0.0*
