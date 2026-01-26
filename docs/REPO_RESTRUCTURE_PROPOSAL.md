# Repository Restructure Proposal

**Authors:** Brad Stevens (Architecture) & Tom Brady (Product Owner)
**Date:** 2026-01-26
**Version:** 1.0

---

## Executive Summary

This document proposes a cleaner, more efficient repository structure for Cricket Playbook. The goal is to make it easy for any team member to find what they need within 3 clicks/commands.

---

## Current Issues Identified

### 1. Duplicate Files
| Issue | Location(s) | Action |
|-------|-------------|--------|
| KANBAN.md duplicated | `./KANBAN.md` (v2.3.0, stale) + `docs/KANBAN.md` (v3.0.1, current) | Delete root KANBAN.md |
| ipl_2026_squad_experience.csv | `data/` + `outputs/` | Keep only in `outputs/` |
| bowler_classifications (v1 & v2) | `data/` | Archive v1, rename v2 to main |

### 2. Scattered Reviews
| Current | Proposed |
|---------|----------|
| `editorial/flower_reviews/` | Merge into `reviews/domain/` |
| `editorial/sprint_reviews/` | Merge into `reviews/sprint/` |
| `editorial/clustering/` | Move to `docs/specs/` |
| `founder_review/` | Merge into `reviews/founder/` |

### 3. Script Naming Convention
| Current (Unclear) | Proposed (Clear) |
|-------------------|------------------|
| `founder_review_1_fixes.py` | Archive to `scripts/archive/` |
| `founder_review_2_fixes.py` | Archive to `scripts/archive/` |
| `generate_2023_outputs.py` | Keep (utility script) |
| `generate_all_2023_outputs.py` | Consolidate with above |

### 4. Outputs Organization
Current: 29 files mixed together
Proposed: Organize by category

---

## Proposed Directory Structure

```
cricket-playbook/
├── README.md                      # Project overview (keep)
├── requirements.txt               # Dependencies (keep)
├── .pre-commit-config.yaml        # Hooks config (keep)
│
├── config/                        # Configuration (keep as-is)
│   ├── agents/                    # Agent definitions
│   ├── templates/                 # Output templates
│   └── CONSTITUTION.md
│
├── data/                          # Source data (reorganize)
│   ├── database/                  # NEW: DuckDB files
│   │   └── cricket_playbook.duckdb
│   ├── squads/                    # NEW: IPL squad data
│   │   ├── ipl_2026_squads.csv
│   │   └── ipl_2026_player_contracts.csv
│   ├── reference/                 # NEW: Reference data
│   │   └── bowler_classifications.csv
│   ├── raw/                       # Source ZIPs (keep)
│   └── processed/                 # Processed data (keep)
│
├── docs/                          # Documentation (reorganize)
│   ├── README.md                  # Docs index
│   ├── PRD_CRICKET_PLAYBOOK.md    # Product requirements
│   ├── KANBAN.md                  # Sprint board (single source)
│   ├── cicd_best_practices.md     # CI/CD guide
│   └── specs/                     # NEW: Technical specs
│       ├── clustering_prd.md      # From editorial/clustering/
│       └── archetype_definitions.md
│
├── reviews/                       # NEW: All reviews consolidated
│   ├── founder/                   # Founder reviews & responses
│   │   ├── review_1.pdf
│   │   ├── response_1.md
│   │   ├── review_2.pdf
│   │   ├── response_2.md
│   │   ├── review_3.pdf
│   │   ├── response_3.md
│   │   ├── review_4.pdf
│   │   └── review_4_response.md
│   ├── domain/                    # Domain expert reviews
│   │   └── andy_flower_*.md
│   └── sprint/                    # Sprint reviews
│       └── sprint_*.md
│
├── analysis/                      # EDA & audits (keep, expand)
│   ├── entry_point_audit_report.md
│   ├── threshold_eda_2023.md
│   └── player_id_audit_report.md  # Move from outputs/
│
├── outputs/                       # Generated outputs (reorganize)
│   ├── README.md                  # Outputs documentation
│   ├── tags/                      # NEW: Player classifications
│   │   ├── player_tags.json
│   │   ├── player_tags_2023.json
│   │   ├── player_clustering_2023.csv
│   │   └── bowler_role_tags.csv
│   ├── matchups/                  # NEW: Matchup analysis
│   │   ├── batter_bowling_type_*.csv
│   │   ├── bowler_handedness_*.csv
│   │   └── batter_entry_points_*.csv
│   ├── metrics/                   # NEW: Performance metrics
│   │   ├── batter_consistency_*.csv
│   │   ├── bowler_pressure_*.csv
│   │   ├── bowler_phase_*.csv
│   │   └── partnership_synergy_*.csv
│   ├── team/                      # NEW: Team-level outputs
│   │   ├── team_venue_records_*.csv
│   │   └── ipl_2026_squad_experience.csv
│   └── logs/                      # Run logs
│       └── run_logs/
│
├── scripts/                       # Python scripts (reorganize)
│   ├── README.md                  # NEW: Script documentation
│   ├── core/                      # NEW: Core pipeline
│   │   ├── ingest.py
│   │   ├── analytics_ipl.py
│   │   └── validate_schema.py
│   ├── generators/                # NEW: Output generators
│   │   ├── generate_stat_packs.py
│   │   ├── generate_2023_outputs.py
│   │   └── sprint_3_p1_features.py
│   ├── analysis/                  # NEW: Analysis scripts
│   │   ├── player_clustering_v2.py
│   │   ├── batter_bowling_type_matchup.py
│   │   ├── bowler_handedness_matchup.py
│   │   ├── bowler_phase_tags.py
│   │   └── entry_point_analysis.py
│   ├── utils/                     # NEW: Utilities
│   │   ├── model_serializer.py
│   │   ├── validate_outputs.py
│   │   └── generate_experience_csv.py
│   ├── run_stat_packs.sh          # CLI runner (keep at root)
│   └── archive/                   # NEW: Legacy/one-time scripts
│       ├── founder_review_1_fixes.py
│       ├── founder_review_2_fixes.py
│       ├── analytics.py           # Superseded by analytics_ipl.py
│       └── player_clustering.py   # Superseded by v2
│
├── stat_packs/                    # Team stat packs (keep as-is)
│   ├── README.md
│   └── *_stat_pack.md             # 10 team files
│
├── ml_ops/                        # ML operations (keep as-is)
│   ├── README.md
│   ├── model_registry.json
│   └── deployment_manifest.md
│
├── tests/                         # Test suite (expand)
│   ├── unit/                      # NEW: Unit tests
│   ├── integration/               # NEW: Integration tests
│   └── test_stat_packs.py         # Current tests
│
├── notebooks/                     # Jupyter notebooks (keep)
│   ├── explore.ipynb
│   └── view_explorer.ipynb
│
└── .github/                       # GitHub config (keep)
    └── workflows/
```

---

## Implementation Plan

### Phase 1: Quick Wins (No Code Changes)
| Task | Risk | Effort |
|------|------|--------|
| Delete stale `./KANBAN.md` | None | 1 min |
| Delete duplicate squad_experience.csv from `data/` | None | 1 min |
| Archive `bowler_classifications.csv` (v1) | None | 1 min |
| Delete corrupted file in `data/` | None | 1 min |
| Move `player_id_audit_report.md` to `analysis/` | None | 1 min |

### Phase 2: Directory Reorganization
| Task | Risk | Effort |
|------|------|--------|
| Create `reviews/` and move founder/editorial reviews | Low | 15 min |
| Create `docs/specs/` and move clustering docs | Low | 5 min |
| Create `scripts/archive/` and move legacy scripts | Low | 5 min |

### Phase 3: Outputs Reorganization (Higher Risk)
| Task | Risk | Effort |
|------|------|--------|
| Create subdirectories in `outputs/` | Medium | 10 min |
| Update `outputs/README.md` paths | Medium | 15 min |
| Update scripts that read/write outputs | Medium | 30 min |

### Phase 4: Scripts Reorganization (Highest Risk)
| Task | Risk | Effort |
|------|------|--------|
| Create `scripts/core/`, `scripts/generators/`, etc. | High | 20 min |
| Update import paths in all scripts | High | 60 min |
| Update CI/CD workflow paths | High | 15 min |
| Update `run_stat_packs.sh` | High | 10 min |

---

## Recommendation

**Sprint 3.1 Scope:**
- Execute Phase 1 (Quick Wins) immediately
- Execute Phase 2 (Reviews consolidation) in Sprint 3.1
- Defer Phase 3 & 4 to Sprint 3.2 (requires test coverage first)

**Rationale:**
- Phase 1 & 2 have zero impact on code functionality
- Phase 3 & 4 require updating import paths and could break existing scripts
- Better to have comprehensive test coverage before large refactors

---

## Directory Navigation Guide

After restructure, here's how to find things:

| Looking For | Go To |
|-------------|-------|
| Project overview | `README.md` |
| Sprint status | `docs/KANBAN.md` |
| Product requirements | `docs/PRD_CRICKET_PLAYBOOK.md` |
| Founder feedback | `reviews/founder/` |
| Domain reviews | `reviews/domain/` |
| Player tags | `outputs/tags/` |
| Matchup data | `outputs/matchups/` |
| Team stat packs | `stat_packs/` |
| Run analytics | `scripts/core/analytics_ipl.py` |
| Generate outputs | `scripts/generators/` |
| IPL squad data | `data/squads/` |
| Raw match data | `data/raw/` |

---

## Sign-off

| Role | Name | Approved |
|------|------|----------|
| Architecture Lead | Brad Stevens | Pending |
| Product Owner | Tom Brady | Pending |
| Analytics Lead | Stephen Curry | Pending |
| Data Pipeline | Brock Purdy | Pending |

---

*Cricket Playbook v3.0.1*
