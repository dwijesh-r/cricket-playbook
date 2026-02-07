# ML Implementation

**Owner:** Stephen Curry (Analytics Lead) / Ime Udoka (MLOps)

---

## Script Locations

| Script | Purpose | Owner |
|--------|---------|-------|
| `scripts/analysis/player_clustering_v2.py` | K-Means clustering training | Stephen Curry |
| `scripts/analysis/generate_predicted_xii.py` | Predicted XI generation | Stephen Curry |
| `scripts/utils/model_serializer.py` | Model save/load utilities | Ime Udoka |

---

## Training Pipeline

```
1. Load data from DuckDB
2. Apply sample size filters (500+ balls batters, 300+ bowlers)
3. Apply recency weighting (2x for 2021-2025)
4. Remove correlated features (r > 0.90)
5. StandardScaler normalization
6. K-Means clustering (n_clusters=5, random_state=42)
7. PCA for visualization
8. Save model artifacts
```

---

## Output Artifacts

| Artifact | Location | Format |
|----------|----------|--------|
| Batter clusters | `outputs/tags/` | JSON, CSV |
| Bowler clusters | `outputs/tags/` | JSON, CSV |
| Model metadata | `ml_ops/model_registry.json` | JSON |

---

## CI/CD Integration

Tests run via GitHub Actions:
```yaml
pytest tests/test_model_performance.py -v --tb=short
```

---

*Ime Udoka - MLOps Lead*
