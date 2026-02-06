# ML Ops

Model registry, versioning, and deployment tracking for Cricket Playbook.

**Maintainer:** Ime Udoka (DevOps Lead)
**Last Updated:** 2026-02-06

---

## Contents

| File | Description |
|------|-------------|
| `model_registry.json` | Centralized model version registry (v2.0.0) |
| `MODEL_VERSIONING.md` | Model versioning policies and procedures |
| `deployment_manifest.md` | Deployment status, checklists, and gates |

---

## Quick Reference

### Current Production Models

| Model | Version | Status | Owner |
|-------|---------|--------|-------|
| Player Clustering | v2.0.0 | Active | Stephen Curry |

### Model Registry Schema Version

**Registry Schema:** 2.0.0

The registry uses semantic versioning (MAJOR.MINOR.PATCH) for all models.

---

## Versioning System

### Semantic Versioning

| Component | Description |
|-----------|-------------|
| **MAJOR** | Breaking changes (interface, features, output format) |
| **MINOR** | New features, hyperparameter changes |
| **PATCH** | Bug fixes, documentation updates |

### Lifecycle Stages

```
development -> staging -> production -> deprecated -> archived
```

### Quality Gates

All models must pass:
1. **Technical Gates** - PCA variance, correlation, cluster size
2. **Testing Gates** - Unit, smoke, integration tests
3. **Validation Gates** - Domain expert review, founder sign-off

---

## Clustering Model V2

**Algorithm:** K-means with PCA dimensionality reduction

| Component | Batters | Bowlers |
|-----------|---------|---------|
| PCA Variance | 83.6% | 63.8% |
| Clusters | 5 | 5 |
| Min Balls | 300 | 200 |

### Batter Archetypes
- CLASSIC_OPENER
- ACCUMULATOR
- DEATH_FINISHER
- ELITE_EXPLOSIVE
- POWER_OPENER

### Bowler Archetypes
- DEATH_SPECIALIST
- DEVELOPING
- SPIN_CONTROLLER
- NEW_BALL_PACER
- ALL_ROUNDER

---

## Deployment Gates

| Gate | Criteria | Status |
|------|----------|--------|
| PCA Variance | Batters >70%, Bowlers >50% | PASS |
| Smoke Tests | All tests pass | PENDING |
| Domain Review | Andy Flower approval | PENDING |
| Founder Review | Final sign-off | COMPLETE |

---

## File Structure

```
ml_ops/
  model_registry.json     # Model metadata and versions
  MODEL_VERSIONING.md     # Versioning documentation
  deployment_manifest.md  # Deployment tracking
  README.md               # This file
  artifacts/              # Model artifacts (planned)
    player_clustering/
      v2.0.0/
        model.joblib
        scaler.joblib
        metadata.json
```

---

## Key Workflows

### Adding a New Model Version

1. Update `model_registry.json` with new version entry
2. Set `lifecycle_stage` to "development"
3. Develop and test the model
4. Pass quality gates
5. Obtain domain validation
6. Promote to production

### Deprecating a Model Version

1. Update `status` to "deprecated"
2. Set `deprecated_date` and `deprecated_reason`
3. Wait for deprecation window (30 days)
4. Move to "archived" stage

### Rollback Procedure

1. Identify issue and affected version
2. Revert `active_version` pointer
3. Regenerate outputs from previous version
4. Document in changelog

---

## Related Documentation

- Governance: `governance/TASK_INTEGRITY_LOOP.md`
- Constitution: `config/CONSTITUTION.md`
- Player Tags: `outputs/tags/README.md`
- Clustering Script: `scripts/analysis/player_clustering_v2.py`

---

*Ime Udoka - DevOps Lead*
*Cricket Playbook v4.0.0*
