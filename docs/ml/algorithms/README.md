# ML Algorithms

**Owner:** Stephen Curry (Analytics Lead)

---

## Contents

| Document | Description |
|----------|-------------|
| [player_clustering_prd.md](player_clustering_prd.md) | K-Means clustering PRD for player archetypes |
| [predicted_xii_algorithm_v2.md](predicted_xii_algorithm_v2.md) | Predicted XI + Impact Player selection |
| [archetype_definitions.md](archetype_definitions.md) | Creative archetype names and mappings |

---

## Current Algorithms

### 1. Player Clustering (v2.0.0)
- **Type:** K-Means Clustering
- **Batter Clusters:** 5 (Playmaker, Accumulator, Anchor, Finisher, Explosive)
- **Bowler Clusters:** 5 (Controller, Workhorse, Strike Bowler, Support Spinner, Part-timer)
- **Implementation:** `scripts/analysis/player_clustering_v2.py`

### 2. Predicted XI Selection (v2.0.0)
- **Formula:** 65% Competency + 35% Variety
- **Constraints:** Captain exclusion, overseas limits, role capping
- **Implementation:** `scripts/analysis/generate_predicted_xii.py`

---

*Stephen Curry - Analytics Lead*
