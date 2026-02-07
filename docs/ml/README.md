# Machine Learning Documentation

**Owner:** Ime Udoka (MLOps Lead)
**Last Updated:** February 7, 2026
**Version:** 1.0.0

---

## Overview

This directory contains all machine learning documentation for Cricket Playbook, including algorithm specifications, model versioning, feature engineering, and validation reports.

---

## Directory Structure

```
docs/ml/
├── README.md                 # This file - ML documentation index
├── algorithms/               # Algorithm specifications and PRDs
├── models/                   # Model registry, versioning, deployment
├── features/                 # Feature engineering documentation
├── validation/               # Domain validation and quality gates
├── research/                 # Cross-sport methodology research
└── implementation/           # Implementation guides and scripts reference
```

---

## Quick Links

### Algorithms
- [Player Clustering PRD](algorithms/player_clustering_prd.md) - K-Means clustering for player archetypes
- [Predicted XI Algorithm](algorithms/predicted_xii_algorithm_v2.md) - Team selection algorithm
- [Archetype Definitions](algorithms/archetype_definitions.md) - Cluster label mappings

### Models
- [Model Versioning](models/MODEL_VERSIONING.md) - Semantic versioning and lifecycle
- [Model Registry](models/model_registry.json) - Centralized model metadata
- [Deployment Manifest](models/DEPLOYMENT_MANIFEST.md) - Deployment tracking

### Features
- [Batter Features](features/batter_features.md) - 15 batter clustering features
- [Bowler Features](features/bowler_features.md) - 15 bowler clustering features

### Validation
- [Quality Gates](validation/quality_gates.md) - Technical and domain validation gates
- [Andy Flower Review](validation/andy_flower_clustering_review.md) - Domain expert validation
- [Cluster Labels](validation/cluster_labels.md) - Label mappings and definitions

### Research
- [PFF Grading System](research/pff_grading_system.md) - Pro Football Focus methodology
- [KenPom Methodology](research/kenpom_methodology.md) - Basketball efficiency metrics

---

## Current Production Models

| Model | Version | Status | Owner |
|-------|---------|--------|-------|
| Player Clustering | v2.0.0 | Production | Stephen Curry |
| Predicted XI | v2.0.0 | Production | Andy Flower |

---

## Key Metrics

### Batter Clustering (v2.0.0)
- **Clusters:** 5 (Playmaker, Accumulator, Anchor, Finisher, Explosive)
- **Features:** 8 (after correlation cleanup)
- **PCA Variance:** 83.6% (threshold: >70%)
- **Players:** 173

### Bowler Clustering (v2.0.0)
- **Clusters:** 5 (Controller, Workhorse, Strike Bowler, Support Spinner, Part-timer)
- **Features:** 16 (after correlation cleanup)
- **PCA Variance:** 63.8% (threshold: >50%)
- **Players:** 268

---

## Ownership

| Role | Owner | Responsibilities |
|------|-------|------------------|
| Analytics Lead | Stephen Curry | Algorithms, feature engineering, model training |
| Cricket Domain | Andy Flower | Validation, archetype definitions, cricket context |
| MLOps Lead | Ime Udoka | Model registry, versioning, deployment, CI/CD |
| Data Engineering | Brock Purdy | Data pipeline, feature sources |

---

## Related Documentation

- [Data Dictionary](../DATA_DICTIONARY.md) - Database schema and field definitions
- [PRD](../PRD_CRICKET_PLAYBOOK.md) - Product requirements document
- [Task Integrity Loop](../../governance/TASK_INTEGRITY_LOOP.md) - Governance process

---

*Tom Brady - Delivery Owner*
*Cricket Playbook v4.1.0*
