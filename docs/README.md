# Documentation

Project documentation, requirements, and technical guides.

---

## Contents

| Document | Description | Owner |
|----------|-------------|-------|
| `PRD_CRICKET_PLAYBOOK.md` | Product Requirements Document | Tom Brady |
| `KANBAN.md` | Sprint Kanban Board (Sprint 3.0 complete) | Tom Brady |
| `cicd_best_practices.md` | CI/CD and codebase maintenance guide | Brad Stevens |

---

## PRD_CRICKET_PLAYBOOK.md

The Product Requirements Document defines:

- **Project Overview**: IPL 2026 Analytics Platform for editorial and broadcast use
- **Data Sources**: Cricsheet ball-by-ball JSON (9,357 T20 matches)
- **Analytics Views**: 34 DuckDB views for career stats, phase analysis, matchups
- **Player Classification**: K-means clustering with 5 batter + 5 bowler archetypes
- **Output Formats**: Team stat packs, CSV exports, JSON tags
- **Quality Gates**: Schema validation (33 checks), smoke tests (76 tests)

**Key Sections:**
1. Executive Summary
2. Data Architecture
3. Analytics Views Specification
4. Player Classification Model
5. Output Requirements
6. Quality Assurance
7. Sprint Roadmap

---

## cicd_best_practices.md

Comprehensive CI/CD and codebase maintenance recommendations by Brad Stevens.

**Contents:**
1. Current State Assessment
2. CI/CD Pipeline Recommendations (multi-stage)
3. Code Quality Tools (Ruff, mypy, pre-commit)
4. Testing Strategy (unit/integration/e2e pyramid)
5. Documentation Standards
6. Version Control Practices
7. Data Validation Pipelines
8. Model Versioning and MLOps
9. Sample GitHub Actions Workflows
10. Implementation Priority Matrix

**Key Recommendations:**
- Add CI workflow with lint + test stages (P0)
- Configure Ruff + pre-commit hooks (P1)
- Restructure tests into unit/integration/e2e (P1)
- Add model serialization with joblib (P2)
- Implement Great Expectations for data validation (P3)

**Estimated Effort:** 40-50 developer hours over 4 weeks

---

## Related Documentation

| Location | Content |
|----------|---------|
| `README.md` (root) | Project overview, quick start, analytics views |
| `outputs/README.md` | Output files (25+), tag definitions, data ranges |
| `analysis/` | **NEW** EDA reports, entry point audit |
| `ml_ops/README.md` | Model architecture, features, deployment gates |
| `config/README.md` | Agent definitions, workflows |
| `stat_packs/README.md` | Stat pack structure, player archetypes |
| `founder_review/` | Founder reviews and responses |
| `editorial/` | Sprint reviews, clustering PRD, domain validation |

---

## Document Owners

| Owner | Documents |
|-------|-----------|
| Tom Brady | PRD, KANBAN, main README, founder review responses |
| Brad Stevens | CI/CD guide, contributing guide (planned) |
| Stephen Curry | Technical specs in ml_ops/, outputs/, analysis/ |
| Andy Flower | Domain validation in editorial/clustering/ |

---

*Cricket Playbook v3.0.1*
