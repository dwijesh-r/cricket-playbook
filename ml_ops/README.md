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

---

## Player Clustering Model V2

### Algorithm

**Type:** K-means Clustering (scikit-learn)

**Pipeline:**
1. Feature extraction from DuckDB analytics views
2. StandardScaler normalization (mean=0, std=1)
3. PCA dimensionality reduction
4. K-means clustering with k=5
5. Label assignment based on cluster centroids

### Batter Features

| Feature | Description | Weight |
|---------|-------------|--------|
| `strike_rate` | Overall runs per 100 balls | High |
| `avg_position` | Weighted average batting position | High |
| `pp_strike_rate` | Strike rate in powerplay (overs 1-6) | Medium |
| `death_strike_rate` | Strike rate at death (overs 16-20) | Medium |
| `boundary_pct` | (4s + 6s) / total balls | Medium |
| `dot_pct` | Dot balls / total balls | Low |

**PCA Variance Explained:** 83.6% (2 components)

**Cluster Assignments:**
| Cluster | Label | Key Characteristics |
|---------|-------|---------------------|
| 0 | CLASSIC_OPENER | Position 1.8, platform builders, steady SR |
| 1 | ACCUMULATOR | Position 3.8, middle-order stabilizers |
| 2 | DEATH_FINISHER | Position 4.6, lower-order finishers |
| 3 | ELITE_EXPLOSIVE | SR 158+, match-winners across phases |
| 4 | POWER_OPENER | Position 2.3, aggressive openers 163+ SR |

### Bowler Features

| Feature | Description | Weight |
|---------|-------------|--------|
| `economy` | Runs conceded per over | High |
| `strike_rate` | Balls per wicket | High |
| `pp_wickets_pct` | % of wickets in powerplay | Medium |
| `middle_wickets_pct` | % of wickets in middle overs | Medium |
| `death_wickets_pct` | % of wickets at death | Medium |
| `dot_pct` | Dot balls / total balls | Low |

**PCA Variance Explained:** 63.8% (2 components)

**Cluster Assignments:**
| Cluster | Label | Key Characteristics |
|---------|-------|---------------------|
| 0 | DEATH_SPECIALIST | PP 43.8%, Death 31.8% (dual-phase) |
| 1 | DEVELOPING | Higher economy, mixed phases |
| 2 | SPIN_CONTROLLER | Middle 71.3%, elite spinners |
| 3 | NEW_BALL_PACER | PP 47.7%, opening bowlers |
| 4 | SECONDARY_OPTION | Middle 61.9%, backup options |

### Hyperparameters

```python
# Clustering
N_CLUSTERS = 5
RANDOM_STATE = 42
N_INIT = 10
MAX_ITER = 300

# PCA
N_COMPONENTS = 2  # For visualization
WHITEN = False

# Minimum samples
MIN_BATTER_BALLS = 100
MIN_BOWLER_BALLS = 60
```

### Sample Code

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# 1. Extract features
features_df = extract_features(conn)

# 2. Normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features_df)

# 3. PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
print(f"Variance explained: {sum(pca.explained_variance_ratio_):.1%}")

# 4. Cluster
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_pca)

# 5. Assign labels based on centroid analysis
cluster_labels = assign_cluster_labels(features_df, labels)
```

---

## Model Registry

The `model_registry.json` tracks:
- Model versions and timestamps
- Feature sets used
- PCA variance explained
- Cluster assignments
- Validation status

### Registry Schema

```json
{
  "models": {
    "player_clustering_v2": {
      "version": "2.0.0",
      "created_at": "2026-01-21T12:00:00Z",
      "status": "active",
      "features": {
        "batters": ["strike_rate", "avg_position", ...],
        "bowlers": ["economy", "strike_rate", ...]
      },
      "metrics": {
        "batter_pca_variance": 0.836,
        "bowler_pca_variance": 0.638,
        "silhouette_score": 0.42
      },
      "validation": {
        "andy_flower_approved": true,
        "smoke_tests_pass": true
      }
    }
  }
}
```

---

## Deployment Gates

Before production deployment:

| Gate | Criteria | Status |
|------|----------|--------|
| PCA Variance | Batters >70%, Bowlers >50% | PASS |
| Cluster Size | Min 10 players per cluster | PASS |
| Known Player Check | Kohli=PLAYMAKER, Bumrah=DEATH_SPECIALIST | PASS |
| Andy Flower Review | Cricket domain validation | APPROVED |
| Smoke Tests | 65 pytest tests pass | PASS |

### Validation Process

1. **Automated Tests:** Run `pytest tests/` (65 tests)
2. **Schema Validation:** Run `python scripts/validate_schema.py` (33 checks)
3. **Domain Review:** Andy Flower validates cluster labels
4. **Founder Review:** Final sign-off before broadcast use

---

## Known Limitations

1. **Small sample bias:** Players with <100 balls may have volatile classifications
2. **Recency bias:** Model uses full IPL history (2008-2025), not weighted by recency
3. **Context ignorance:** Doesn't account for pitch conditions, opposition strength
4. **Cluster overlap:** Some players near cluster boundaries may be misclassified

---

## Maintainer

- **Ime Udoka** - ML Ops Engineer
- Coordinates with **Andy Flower** for cricket domain validation
- Coordinates with **Stephen Curry** for feature engineering

---

*Cricket Playbook v2.7.0 - Sprint 2.7*
