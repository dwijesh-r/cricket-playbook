# ML Models

**Owner:** Ime Udoka (MLOps Lead)

---

## Contents

| Document | Description |
|----------|-------------|
| [MODEL_VERSIONING.md](MODEL_VERSIONING.md) | Semantic versioning and lifecycle stages |
| [model_registry.json](model_registry.json) | Centralized model metadata (v2.0.0 schema) |
| [DEPLOYMENT_MANIFEST.md](DEPLOYMENT_MANIFEST.md) | Deployment checklist and status |

---

## Model Registry Overview

### Production Models

| Model | Version | Status | Last Updated |
|-------|---------|--------|--------------|
| Player Clustering | v2.0.0 | Production | 2026-02-06 |
| Predicted XI | v2.0.0 | Production | 2026-02-06 |

### Lifecycle Stages

```
development → staging → production → deprecated → archived
```

### Quality Gates

| Gate | Threshold |
|------|-----------|
| PCA Variance (Batters) | > 70% |
| PCA Variance (Bowlers) | > 50% |
| Correlation Cleanup | r < 0.90 |
| Min Cluster Size | >= 10 players |

---

*Ime Udoka - MLOps Lead*
