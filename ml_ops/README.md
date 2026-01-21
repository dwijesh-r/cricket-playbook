# ML Ops

Machine learning operations, model versioning, and deployment tracking.

## Contents

| File | Description |
|------|-------------|
| `model_registry.json` | Version tracking for ML models |
| `deployment_manifest.md` | Deployment status and QA gates |

## Current Models

| Model | Version | Status | Script |
|-------|---------|--------|--------|
| Player Clustering | v2.0.0 | ACTIVE | `scripts/player_clustering_v2.py` |

## Model Registry

The `model_registry.json` tracks:
- Model versions and timestamps
- Feature sets used
- PCA variance explained
- Cluster assignments

## Deployment Gates

Before production deployment:
1. PCA variance > 50% (PASS)
2. Minimum cluster size > 10 (PASS)
3. Andy Flower domain validation (PENDING)
4. Smoke tests (PENDING)

## Maintainer

- **Ime Udoka** - ML Ops Engineer
- Coordinates with **Andy Flower** for cricket domain validation

---

*Cricket Playbook v2.5.0*
