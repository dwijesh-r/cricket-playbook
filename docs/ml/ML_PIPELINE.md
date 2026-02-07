# ML Pipeline Documentation

**Owner:** Ime Udoka (MLOps Lead)
**Version:** 1.0.0
**Created:** 2026-02-07
**Status:** Active

---

## Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [Data Pipeline](#2-data-pipeline)
3. [Feature Engineering](#3-feature-engineering)
4. [Training Pipeline](#4-training-pipeline)
5. [Inference and Serving](#5-inference-and-serving)
6. [Reproducibility Guide](#6-reproducibility-guide)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Pipeline Overview

### Architecture Diagram

```
+-------------------+     +--------------------+     +---------------------+
|   DATA SOURCES    |     |  FEATURE PIPELINE  |     |   TRAINING PIPELINE |
+-------------------+     +--------------------+     +---------------------+
|                   |     |                    |     |                     |
| cricket_playbook  |     | 1. Extract from    |     | 1. StandardScaler   |
|    .duckdb        |---->|    DuckDB views    |---->|    normalization    |
|                   |     |                    |     |                     |
| Tables:           |     | 2. Recency weight  |     | 2. K-Means (k=5)    |
| - fact_ball       |     |    (2021-2025)     |     |    clustering       |
| - dim_player      |     |                    |     |                     |
| - dim_match       |     | 3. Correlation     |     | 3. PCA variance     |
| - dim_tournament  |     |    cleanup (r>0.9) |     |    analysis         |
+-------------------+     +--------------------+     +---------------------+
                                                              |
                                                              v
+-------------------+     +--------------------+     +---------------------+
|     OUTPUTS       |<----|  QUALITY GATES     |<----|   CLUSTER LABELS    |
+-------------------+     +--------------------+     +---------------------+
|                   |     |                    |     |                     |
| outputs/tags/     |     | Batters PCA > 70%  |     | Batters:            |
| - player_tags.json|     | Bowlers PCA > 50%  |     |  - Conductor        |
| - player_tags.csv |     | Min 10 per cluster |     |  - Hurricane        |
| - bowler_role.csv |     |                    |     |  - Assassin         |
|                   |     | Domain Validation: |     |  - Warrior          |
| ipl_2026_squads   |     | - Andy Flower      |     |  - Architect        |
| (table update)    |     | - Founder sign-off |     |                     |
+-------------------+     +--------------------+     | Bowlers:            |
                                                     |  - General          |
                                                     |  - Surgeon          |
                                                     |  - Sentry           |
                                                     |  - Trooper          |
                                                     |  - Gambler          |
                                                     +---------------------+
```

### Component Summary

| Component | Script/Location | Owner |
|-----------|-----------------|-------|
| Data Source | `data/cricket_playbook.duckdb` | Brock Purdy |
| Training Script | `scripts/analysis/player_clustering_v2.py` | Stephen Curry |
| Model Registry | `docs/ml/models/model_registry.json` | Ime Udoka |
| Cluster Labels | `docs/ml/algorithms/archetype_definitions.md` | Andy Flower |
| Output Tags | `outputs/tags/` | Stephen Curry |

---

## 2. Data Pipeline

### 2.1 Data Source

**Database:** `data/cricket_playbook.duckdb`

The pipeline reads from a DuckDB database containing 2.1M+ ball-by-ball records from T20 matches worldwide.

### 2.2 Source Tables

| Table | Description | Row Count |
|-------|-------------|-----------|
| `fact_ball` | Ball-by-ball delivery records | 2,137,915 |
| `dim_player` | Player dimension (all T20 players) | 7,864 |
| `dim_match` | Match-level metadata | 9,357 |
| `dim_tournament` | Tournament information | 426 |

### 2.3 Analytics Views Used

The pipeline primarily uses pre-computed analytics views:

| View | Purpose |
|------|---------|
| `analytics_ipl_batting_career` | Career batting stats (runs, SR, avg, boundaries) |
| `analytics_ipl_bowling_career` | Career bowling stats (wickets, economy, avg) |
| `analytics_ipl_batter_phase` | Batter performance by match phase |
| `analytics_ipl_bowler_phase` | Bowler performance by match phase |
| `analytics_ipl_bowler_phase_distribution` | Bowler workload distribution by phase |

### 2.4 Data Filtering

```sql
-- Tournament Filter
WHERE tournament_name = 'Indian Premier League'

-- Season Filter (for recency weighting)
WHERE season LIKE '2021%' OR season LIKE '2022%'
   OR season LIKE '2023%' OR season LIKE '2024%'
   OR season LIKE '2025%'

-- Legal Balls Only
WHERE is_legal_ball = TRUE
```

### 2.5 Sample Size Requirements

| Player Type | Minimum Balls | Rationale |
|-------------|---------------|-----------|
| Batters | 300 | ~50 innings equivalent |
| Bowlers | 200 | ~33 overs equivalent |

**Note:** Thresholds were lowered from v1 (500/300) to include more players in v2.

---

## 3. Feature Engineering

### 3.1 Batter Features (8 features after correlation cleanup)

| Feature | Description | Source |
|---------|-------------|--------|
| `overall_sr` | Career strike rate | `analytics_ipl_batting_career` |
| `overall_avg` | Career batting average | `analytics_ipl_batting_career` |
| `overall_boundary` | Overall boundary percentage | `analytics_ipl_batting_career` |
| `overall_dot` | Overall dot ball percentage | `analytics_ipl_batting_career` |
| `avg_batting_position` | Average entry position (1-6) | Derived from `fact_ball` |
| `pp_sr` | Powerplay strike rate | `analytics_ipl_batter_phase` |
| `mid_sr` | Middle overs strike rate | `analytics_ipl_batter_phase` |
| `death_sr` | Death overs strike rate | `analytics_ipl_batter_phase` |

**Removed by Correlation (r > 0.90):**
- `pp_boundary` (correlated with `pp_sr`)
- `mid_boundary` (correlated with `mid_sr`)
- `death_boundary` (correlated with `death_sr`)

### 3.2 Bowler Features (16 features)

| Feature | Description | Source |
|---------|-------------|--------|
| `overall_economy` | Career economy rate | `analytics_ipl_bowling_career` |
| `overall_sr` | Career bowling strike rate | `analytics_ipl_bowling_career` |
| `overall_dot` | Overall dot ball percentage | `analytics_ipl_bowling_career` |
| `overall_boundary` | Boundary conceded percentage | `analytics_ipl_bowling_career` |
| `pp_economy` | Powerplay economy rate | `analytics_ipl_bowler_phase` |
| `pp_dot` | Powerplay dot ball percentage | `analytics_ipl_bowler_phase` |
| `mid_economy` | Middle overs economy rate | `analytics_ipl_bowler_phase` |
| `mid_dot` | Middle overs dot ball percentage | `analytics_ipl_bowler_phase` |
| `death_economy` | Death overs economy rate | `analytics_ipl_bowler_phase` |
| `death_dot` | Death overs dot ball percentage | `analytics_ipl_bowler_phase` |
| `pp_pct` | Percentage of overs in powerplay | Phase distribution |
| `mid_pct` | Percentage of overs in middle | Phase distribution |
| `death_pct` | Percentage of overs at death | Phase distribution |
| `pp_wickets` | Wickets in powerplay | Derived from `fact_ball` |
| `mid_wickets` | Wickets in middle overs | Derived from `fact_ball` |
| `death_wickets` | Wickets in death overs | Derived from `fact_ball` |

### 3.3 Recency Weighting

Players with more recent data receive higher weights:

```python
# Recency weight calculation
recency_weight = 1.0 + (recent_balls / total_balls)

# Weight range: 1.0 (no recent data) to 2.0 (all data recent)
# Applied as: X = X * sqrt(recency_weight)
```

**Recent Seasons:** 2021, 2022, 2023, 2024, 2025

### 3.4 Batting Position Derivation

The `avg_batting_position` feature estimates when a batter typically enters:

```sql
-- Uses LEGAL ball count, not ball_seq (which includes wides/no-balls)
CASE
    WHEN MIN(legal_ball_num) <= 6 THEN 1   -- Opener
    WHEN MIN(legal_ball_num) <= 24 THEN 2  -- #3
    WHEN MIN(legal_ball_num) <= 48 THEN 3  -- #4
    WHEN MIN(legal_ball_num) <= 72 THEN 4  -- #5
    WHEN MIN(legal_ball_num) <= 96 THEN 5  -- #6
    ELSE 6                                  -- Lower order
END as batting_position
```

### 3.5 Correlation Cleanup

Features with Pearson correlation > 0.90 are removed:

```python
def analyze_correlations(df, feature_cols, threshold=0.9):
    corr_matrix = df[feature_cols].corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    to_drop = []
    for col in upper.columns:
        if any(upper[col] > threshold):
            to_drop.append(col)
    return to_drop
```

---

## 4. Training Pipeline

### 4.1 Preprocessing

**StandardScaler Normalization:**

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X = scaler.fit_transform(df_clean[feature_cols])

# Apply recency weighting
weights = df_clean["recency_weight"].values.reshape(-1, 1)
X = X * np.sqrt(weights)
```

### 4.2 K-Means Clustering

**Algorithm:** K-Means with scikit-learn

**Hyperparameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_clusters` | 5 | Elbow method + cricket interpretability |
| `random_state` | 42 | Reproducibility |
| `n_init` | 10 | 10 random initializations |
| `max_iter` | 300 | Default convergence |
| `algorithm` | lloyd | Standard K-Means |

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
df_clean["cluster"] = kmeans.fit_predict(X)
```

### 4.3 PCA Variance Analysis

PCA is used to validate feature quality, not dimensionality reduction:

```python
from sklearn.decomposition import PCA

pca = PCA()
pca.fit(X)
cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

# Report variance explained by first 3 components
print(f"First 3 PCs: {cumulative_variance[2] * 100:.1f}%")
```

### 4.4 Quality Gates

| Gate | Target | Current (v2.0.0) | Status |
|------|--------|------------------|--------|
| Batter PCA (3 components) | > 70% | 83.6% | PASS |
| Bowler PCA (3 components) | > 50% | 63.8% | PASS |
| Min players per cluster | >= 10 | Yes | PASS |
| Correlation threshold | < 0.90 | Cleaned | PASS |

### 4.5 Training Outputs

| Metric | Batters | Bowlers |
|--------|---------|---------|
| Players clustered | 173 | 268 |
| Features used | 8 | 16 |
| Clusters | 5 | 5 |
| PCA (3 components) | 83.6% | 63.8% |

---

## 5. Inference and Serving

### 5.1 Model Artifacts

Models are not persisted as serialized objects. Instead, the clustering pipeline is re-run when needed:

```
scripts/analysis/player_clustering_v2.py  # Training + inference script
```

### 5.2 Output Files

| File | Format | Location |
|------|--------|----------|
| Player Tags | JSON | `outputs/tags/player_tags.json` |
| Batter Clusters | CSV | `outputs/tags/player_clustering_2023.csv` |
| Bowler Roles | CSV | `outputs/tags/bowler_role_tags.csv` |

### 5.3 Predicted XI Integration

The clustering results feed into the Predicted XI algorithm:

```
1. Player clusters assigned -> batter_classification, bowler_classification
2. Phase performance -> batter_tags, bowler_tags
3. Tags stored in ipl_2026_squads table
4. Predicted XII Algorithm uses classifications for team selection
```

**Integration Flow:**

```
player_clustering_v2.py
        |
        v
[Cluster Assignments] --> ipl_2026_squads.batter_classification
        |                 ipl_2026_squads.bowler_classification
        v
[Performance Tags]    --> ipl_2026_squads.batter_tags
                          ipl_2026_squads.bowler_tags
        |
        v
predicted_xii_algorithm_v2 (uses classifications + tags for scoring)
        |
        v
[Predicted XI per team]
```

### 5.4 Cluster Label Mapping

**Batter Archetypes (v2.0.0):**

| Cluster ID | Label | Description |
|------------|-------|-------------|
| 0 | CLASSIC_OPENER | Balanced top-order batters |
| 1 | ACCUMULATOR | Foundation builders, low risk |
| 2 | DEATH_FINISHER | Death-over specialists |
| 3 | ELITE_EXPLOSIVE | Highest SR across all phases |
| 4 | POWER_OPENER | Aggressive powerplay hitters |

**Bowler Archetypes (v2.0.0):**

| Cluster ID | Label | Description |
|------------|-------|-------------|
| 0 | DEATH_SPECIALIST | Death-over containment |
| 1 | DEVELOPING | Part-time or inconsistent |
| 2 | SPIN_CONTROLLER | Middle-overs spin dominance |
| 3 | NEW_BALL_PACER | Powerplay specialists |
| 4 | ALL_ROUNDER | Multi-phase utility |

---

## 6. Reproducibility Guide

### 6.1 Environment Setup

**Python Version:** >= 3.10

**Install Dependencies:**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

**Required Packages:**

```
duckdb>=0.9.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.4.0
```

### 6.2 Data Requirements

1. **Database must exist:** `data/cricket_playbook.duckdb`
2. **Analytics views created:** All 51 pre-built analytics views
3. **IPL data present:** Matches from 2008-2025

### 6.3 Retraining Steps

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Navigate to project root
cd /path/to/cricket-playbook

# 3. Run clustering script
python scripts/analysis/player_clustering_v2.py

# 4. Review output
# - Console shows cluster analysis
# - Validates specific players (Buttler, Dhoni, Nortje)
# - Reports PCA variance

# 5. Output files generated in outputs/tags/
```

### 6.4 Expected Output

```
======================================================================
Cricket Playbook - Player Clustering Model V2
Author: Stephen Curry | Sprint 2.5
======================================================================

V2 Improvements:
  - Batting position / entry point feature
  - Wickets per phase for bowlers
  - Recency weighting (2021-2025)
  - PCA variance analysis
  - Correlation cleanup

======================================================================
1. EXTRACTING PLAYER FEATURES (V2)
======================================================================

  Batters with data: 173
  Bowlers with data: 268

======================================================================
2. CLUSTERING BATTERS (V2)
======================================================================

  Correlation Analysis:
    Removing highly correlated: ['pp_boundary', 'mid_boundary', 'death_boundary']

  PCA Variance Analysis:
    Components for 50% variance: 2 of 8
    Variance explained by first 3 PCs: 83.6%

[... cluster analysis output ...]

======================================================================
V2 CLUSTERING SUMMARY
======================================================================

  Batters clustered: 173
  Bowlers clustered: 268

  PCA Variance (Batters):
    Components for 50%: 2/8
    First 3 PCs explain: 83.6%

  PCA Variance (Bowlers):
    Components for 50%: 2/16
    First 3 PCs explain: 63.8%
```

### 6.5 Validation Checklist

After retraining, verify:

- [ ] PCA variance (batters) > 70%
- [ ] PCA variance (bowlers) > 50%
- [ ] All 5 clusters have >= 10 players
- [ ] Known players correctly classified:
  - Jos Buttler: ELITE_EXPLOSIVE or DEATH_FINISHER
  - MS Dhoni: DEATH_FINISHER
  - Anrich Nortje: NEW_BALL_PACER (not part-timer)
- [ ] No highly correlated features (r > 0.9) remain

---

## 7. Troubleshooting

### 7.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `Database not found` | Missing DuckDB file | Ensure `data/cricket_playbook.duckdb` exists |
| `ImportError: sklearn` | Missing dependency | `pip install scikit-learn>=1.4.0` |
| Low batter count | Sample size threshold too high | Reduce `MIN_BALLS_BATTER` (currently 300) |
| Poor PCA variance | Correlated features | Run correlation cleanup |
| Wrong cluster labels | Cluster IDs shifted | Re-validate with player spot checks |

### 7.2 Database Connection Issues

```python
# Verify database exists
from pathlib import Path
db_path = Path("data/cricket_playbook.duckdb")
if not db_path.exists():
    raise FileNotFoundError(f"Database not found at {db_path}")

# Test connection
import duckdb
conn = duckdb.connect(str(db_path))
result = conn.execute("SELECT COUNT(*) FROM fact_ball").fetchone()
print(f"Ball records: {result[0]}")
```

### 7.3 Feature Extraction Debugging

```python
# Check analytics view exists
conn.execute("SELECT * FROM analytics_ipl_batting_career LIMIT 5").df()

# Verify IPL filter
conn.execute("""
    SELECT COUNT(DISTINCT player_id)
    FROM analytics_ipl_batting_career
    WHERE balls_faced >= 300
""").fetchone()
```

### 7.4 Cluster Validation

If clusters look wrong after retraining:

1. **Check random_state:** Must be 42 for reproducibility
2. **Verify feature order:** Column order affects clustering
3. **Review recency weights:** Ensure 2021-2025 data is present
4. **Inspect PCA:** Low variance indicates feature issues

```python
# Quick cluster sanity check
for cluster_id in sorted(df_clean["cluster"].unique()):
    cluster_players = df_clean[df_clean["cluster"] == cluster_id]
    print(f"Cluster {cluster_id}: {len(cluster_players)} players")
    print(f"  Avg SR: {cluster_players['overall_sr'].mean():.1f}")
```

### 7.5 Known Limitations

1. **Static clustering:** Does not track player evolution over time
2. **IPL-only:** Uses only IPL data (non-IPL T20 excluded from clustering)
3. **Sample bias:** Players with < 300/200 balls excluded
4. **No matchup context:** Ignores vs-bowler-type performance
5. **Historical players included:** Retired players affect cluster centroids

### 7.6 Support Contacts

| Issue Type | Contact | Role |
|------------|---------|------|
| Pipeline/DevOps | Ime Udoka | MLOps Lead |
| Feature Engineering | Stephen Curry | Analytics Lead |
| Data Issues | Brock Purdy | Data Pipeline Lead |
| Domain Validation | Andy Flower | Cricket Domain Expert |

---

## Appendix A: Model Registry Reference

See `docs/ml/models/model_registry.json` for complete model metadata including:

- Version history
- Hyperparameters
- Feature lists
- Validation status
- Artifact locations

## Appendix B: Related Documentation

| Document | Location |
|----------|----------|
| Data Dictionary | `docs/DATA_DICTIONARY.md` |
| Model Versioning | `docs/ml/models/MODEL_VERSIONING.md` |
| Clustering PRD | `docs/ml/algorithms/player_clustering_prd.md` |
| Archetype Definitions | `docs/ml/algorithms/archetype_definitions.md` |
| Predicted XII Algorithm | `docs/ml/algorithms/predicted_xii_algorithm_v2.md` |

---

*Ime Udoka - MLOps Lead*
*Cricket Playbook v4.1.0*
*TKT-072 - Document ML Pipeline*
