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

**PCA Variance Explained:** 76.8% (3 components)

**Role Tags Generated:**
| Tag | Count | Key Characteristics |
|-----|-------|---------------------|
| EXPLOSIVE_OPENER | 15 | Position 1-2, aggressive openers 163+ SR |
| PLAYMAKER | 24 | Creative stroke-makers, adaptable across phases |
| ANCHOR | 21 | Stabilizers, build innings, lower SR but consistent |
| ACCUMULATOR | 49 | Position 3-4, middle-order stabilizers |
| MIDDLE_ORDER | 45 | Position 3-5, middle-order specialists |
| FINISHER | 21 | Position 5-7, death-overs specialists |

### Bowler Features

| Feature | Description | Weight |
|---------|-------------|--------|
| `economy` | Runs conceded per over | High |
| `strike_rate` | Balls per wicket | High |
| `pp_wickets_pct` | % of wickets in powerplay | Medium |
| `middle_wickets_pct` | % of wickets in middle overs | Medium |
| `death_wickets_pct` | % of wickets at death | Medium |
| `dot_pct` | Dot balls / total balls | Low |

**PCA Variance Explained:** 63.4% (3 components)

**Role Tags Generated:**
| Tag | Count | Key Characteristics |
|-----|-------|---------------------|
| PACER | 116 | Fast/medium-fast bowlers |
| SPINNER | 68 | Spin bowlers (all types) |
| WORKHORSE | 112 | High-volume, multi-phase bowlers |
| NEW_BALL_SPECIALIST | 43 | Opening bowlers, powerplay focus |
| MIDDLE_OVERS_CONTROLLER | 50 | Middle-phase specialists, economy focus |
| DEATH_SPECIALIST | 19 | Death-overs specialists |
| PART_TIMER | 44 | Part-time bowling options |

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

## Data Range

**Important:** All models now use **IPL 2023-2025 data only** (219 matches) to account for stat drift due to game evolution. This ensures classifications reflect current player form.

## Known Limitations

1. **Small sample bias:** Players with <100 balls may have volatile classifications
2. **Recent data only:** Model uses 2023-2025 data (3 seasons), may miss career trends
3. **Context ignorance:** Doesn't account for pitch conditions, opposition strength
4. **Tag overlap:** Some players may have multiple role tags (e.g., FINISHER + MIDDLE_ORDER)

---

## Maintainer

- **Ime Udoka** - ML Ops Engineer
- Coordinates with **Andy Flower** for cricket domain validation
- Coordinates with **Stephen Curry** for feature engineering

---

*Cricket Playbook v2.8.0 - Sprint 2.8*
