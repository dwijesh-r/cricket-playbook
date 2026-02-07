# Model Versioning Guide

**Owner:** Ime Udoka (DevOps Lead)
**Last Updated:** 2026-02-06
**Status:** Active

---

## Overview

This document defines the model versioning system for Cricket Playbook. All machine learning models must follow these guidelines to ensure reproducibility, traceability, and proper lifecycle management.

---

## Versioning Policy

### Semantic Versioning

All models use **Semantic Versioning** (SemVer) format: `MAJOR.MINOR.PATCH`

| Version Component | When to Increment | Example |
|-------------------|-------------------|---------|
| **MAJOR** | Breaking changes to model interface, feature schema, or output format | 1.0.0 -> 2.0.0 |
| **MINOR** | New features, hyperparameter changes, or performance improvements | 1.0.0 -> 1.1.0 |
| **PATCH** | Bug fixes, documentation updates, or minor adjustments | 1.0.0 -> 1.0.1 |

### Version Lifecycle Stages

| Stage | Description | Criteria |
|-------|-------------|----------|
| **development** | Active development, not production-ready | In progress |
| **staging** | Ready for validation testing | All tests pass |
| **production** | Live, serving outputs | All validations complete |
| **deprecated** | Still available but replaced | Newer version is production |
| **archived** | Historical reference only | Beyond retention window |

---

## Model Registry

### Location

All model metadata is stored in `ml_ops/model_registry.json`.

### Registry Schema

```json
{
  "registry_meta": {
    "schema_version": "2.0.0",
    "last_updated": "YYYY-MM-DD",
    "maintainer": "Ime Udoka (DevOps Lead)"
  },
  "models": {
    "model_id": {
      "model_id": "unique_identifier",
      "display_name": "Human Readable Name",
      "owner": "Owner Name (Role)",
      "validator": "Validator Name (Role)",
      "versions": { ... },
      "active_version": "X.Y.Z",
      "latest_version": "X.Y.Z"
    }
  }
}
```

### Model Version Schema

Each version entry must include:

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | SemVer string |
| `status` | Yes | active, deprecated, archived |
| `lifecycle_stage` | Yes | development, staging, production, deprecated, archived |
| `created_date` | Yes | YYYY-MM-DD format |
| `source.script` | Yes | Path to training script |
| `algorithm` | Yes | Algorithm details and library |
| `features` | Yes | Input feature specifications |
| `hyperparameters` | Yes | Model hyperparameters |
| `data_requirements` | Yes | Sample size and data source info |
| `outputs` | Yes | Output counts and formats |
| `artifacts` | Yes | Paths to model files |
| `validation` | Yes | Validation status and results |
| `dependencies` | Yes | Python and package requirements |

---

## Artifact Management

### Storage Structure

```
ml_ops/
  artifacts/
    {model_id}/
      v{version}/
        model.joblib          # Trained model object
        scaler.joblib         # Preprocessing scaler
        metadata.json         # Version metadata snapshot
        training_log.txt      # Training output log
```

### Naming Convention

`{model_id}_v{version}_{timestamp}.{ext}`

Example: `player_clustering_v2.0.0_20260206.joblib`

### Supported Formats

| Format | Use Case |
|--------|----------|
| `.joblib` | scikit-learn models (recommended) |
| `.pickle` | General Python objects |
| `.json` | Metadata and configurations |
| `.csv` | Output data tables |

---

## Quality Gates

Before a model can be promoted to production, it must pass these gates:

### 1. Technical Gates

| Gate | Threshold | Measurement |
|------|-----------|-------------|
| PCA Variance (Batters) | > 70% | Cumulative explained variance |
| PCA Variance (Bowlers) | > 50% | Cumulative explained variance |
| Correlation Cleanup | r < 0.90 | Remove highly correlated features |
| Min Cluster Size | >= 10 | Players per cluster |

### 2. Testing Gates

| Gate | Requirement |
|------|-------------|
| Unit Tests | All pass |
| Smoke Tests | Model outputs valid |
| Integration Tests | End-to-end pipeline works |

### 3. Validation Gates

| Gate | Owner | Requirement |
|------|-------|-------------|
| Founder Review | Brad Stevens | Feature checklist verified |
| Domain Validation | Andy Flower | Cluster labels approved |
| Player Spot Checks | Andy Flower | Key players correctly classified |

---

## Model Lifecycle Workflow

### 1. Development Phase

```
1. Create new version in registry (status: active, stage: development)
2. Develop and test locally
3. Document features and hyperparameters
4. Run unit tests
```

### 2. Staging Phase

```
1. Update lifecycle_stage to "staging"
2. Run full test suite
3. Generate validation outputs
4. Request domain review
```

### 3. Production Promotion

```
1. Obtain Andy Flower validation
2. Obtain Founder sign-off
3. Update lifecycle_stage to "production"
4. Update active_version pointer
5. Serialize and store artifacts
```

### 4. Deprecation

```
1. Identify replacement version
2. Update status to "deprecated"
3. Set deprecated_date and deprecated_reason
4. Keep available for deprecation_window_days (30 days)
```

### 5. Archival

```
1. After retention window (90 days)
2. Move to archived lifecycle_stage
3. Remove from active rotation
4. Retain for historical reference
```

---

## Current Models

### Player Clustering Model

| Attribute | Value |
|-----------|-------|
| Model ID | `player_clustering` |
| Active Version | 2.0.0 |
| Owner | Stephen Curry (Analytics Lead) |
| Validator | Andy Flower (Cricket Domain Expert) |
| Algorithm | K-Means |
| Status | Production |

#### Version History

| Version | Status | Created | Notes |
|---------|--------|---------|-------|
| 2.0.0 | Active | 2026-01-21 | Added batting position, wickets per phase |
| 1.0.0 | Archived | 2026-01-20 | Initial version |

---

## Retention Policy

| Category | Retention |
|----------|-----------|
| Active versions | 2 most recent |
| Deprecated versions | 3 most recent |
| Archive after | 90 days |

---

## Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **Stephen Curry** (Analytics Lead) | Model development, feature engineering |
| **Andy Flower** (Cricket Domain Expert) | Cluster label validation, player spot checks |
| **Ime Udoka** (DevOps Lead) | Registry maintenance, artifact management, deployment |
| **Brad Stevens** (Founder) | Final sign-off on major changes |

---

## Adding a New Model

### Step 1: Register Model

Add a new entry to `ml_ops/model_registry.json`:

```json
{
  "models": {
    "new_model_id": {
      "model_id": "new_model_id",
      "display_name": "New Model Name",
      "owner": "Owner Name (Role)",
      "validator": "Validator Name (Role)",
      "versions": {},
      "active_version": null,
      "latest_version": null
    }
  }
}
```

### Step 2: Add First Version

```json
{
  "versions": {
    "1.0.0": {
      "version": "1.0.0",
      "status": "active",
      "lifecycle_stage": "development",
      "created_date": "YYYY-MM-DD",
      ...
    }
  }
}
```

### Step 3: Complete Development

1. Develop the model
2. Document all metadata fields
3. Pass quality gates
4. Obtain validations
5. Promote to production

---

## Model Comparison

When comparing versions, document:

| Metric | v1.0.0 | v2.0.0 |
|--------|--------|--------|
| Feature Count | X | Y |
| Sample Size | X | Y |
| Clusters | X | Y |
| PCA Variance | X% | Y% |
| Validated | Yes/No | Yes/No |

---

## Troubleshooting

### Common Issues

| Issue | Resolution |
|-------|------------|
| Version conflict | Check active_version pointer |
| Missing artifact | Regenerate from source script |
| Validation failure | Review quality gate criteria |
| Deprecated model in use | Update downstream dependencies |

---

## References

- Model Registry: `ml_ops/model_registry.json`
- Deployment Manifest: `ml_ops/deployment_manifest.md`
- Clustering Script: `scripts/analysis/player_clustering_v2.py`
- Output Tags: `outputs/tags/`
- Governance: `governance/TASK_INTEGRITY_LOOP.md`

---

*Ime Udoka - DevOps Lead*
*Cricket Playbook v4.0.0*
