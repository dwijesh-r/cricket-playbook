# ML Ops Deployment Manifest

**Maintainer:** Ime Udoka (DevOps Lead)
**Last Updated:** 2026-02-06
**Coordinated with:** Andy Flower (Cricket Domain Validation)

---

## Model Registry Integration

This manifest is linked to the centralized model registry at `ml_ops/model_registry.json`.

For versioning policies and artifact management, see `ml_ops/MODEL_VERSIONING.md`.

---

## Current Production Models

| Model | Version | Status | Registry ID | Script |
|-------|---------|--------|-------------|--------|
| Player Clustering | v2.0.0 | **ACTIVE** | `player_clustering` | `scripts/analysis/player_clustering_v2.py` |

---

## Model V2 Deployment Checklist

### Data Pipeline (Brock Purdy)
- [x] Database schema stable
- [x] Analytics views available
- [x] Uncapped player handling (Sprint 2.4)
- [x] Bowling type corrections applied

### Feature Engineering (Stephen Curry)
- [x] Batting position feature implemented
- [x] Wickets per phase implemented
- [x] Recency weighting (2021-2025)
- [x] Correlation cleanup (r > 0.9)

### Quality Gates (N'Golo Kante)
- [x] PCA variance > 50% - PASS (Batters: 83.6%, Bowlers: 63.8%)
- [x] Minimum cluster size > 10 - PASS
- [ ] Smoke tests for V2 - PENDING
- [ ] Integration tests - PENDING

### Cricket Domain (Andy Flower)
- [ ] Batter cluster labels validated
- [ ] Bowler cluster labels validated
- [ ] Key player classifications reviewed
- [ ] Archetype definitions approved

### ML Ops (Ime Udoka)
- [x] Model registry created
- [x] Version tracking implemented
- [x] Model versioning documentation created
- [ ] Model serialization (.joblib)
- [ ] Reproducibility tests
- [ ] Monitoring dashboards

---

## Cluster Interpretations (Pending Andy Flower Review)

### Batter Clusters V2

| Cluster | Proposed Label | Avg Position | Key Characteristics |
|---------|---------------|--------------|---------------------|
| 0 | **CLASSIC_OPENER** | 1.8 | Traditional openers, PP focused |
| 1 | **ACCUMULATOR** | 3.8 | Middle order stabilizers |
| 2 | **DEATH_FINISHER** | 4.6 | Late order hitters, high death SR |
| 3 | **ELITE_EXPLOSIVE** | 3.4 | Match winners, 158+ SR |
| 4 | **POWER_OPENER** | 2.3 | Aggressive openers, 163+ SR |

### Bowler Clusters V2

| Cluster | Proposed Label | Phase Focus | Key Characteristics |
|---------|---------------|-------------|---------------------|
| 0 | **DEATH_SPECIALIST** | PP 43.8%, Death 31.8% | Bumrah, Rabada |
| 1 | **DEVELOPING** | Mixed | Higher economy, fewer wickets |
| 2 | **SPIN_CONTROLLER** | Mid 71.3% | Mishra, Kuldeep |
| 3 | **NEW_BALL_PACER** | PP 47.7% | Hazlewood, Archer |
| 4 | **ALL_ROUNDER** | Mid 61.9% | Part-timers, versatile |

---

## Production Readiness Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Algorithm | 5/5 | K-Means, interpretable |
| Features | 4/5 | V2 improvements complete |
| Data Quality | 4/5 | Sprint 2.4 fixes applied |
| Validation | 3/5 | Andy Flower review pending |
| Reproducibility | 4/5 | Random state fixed |
| Documentation | 5/5 | Registry and versioning docs complete |
| **Overall** | **4.2/5** | Ready for Andy Flower review |

---

## Deployment Environments

| Environment | Description | Status |
|-------------|-------------|--------|
| **development** | Local development and testing | Available |
| **staging** | Pre-production validation | Available |
| **production** | Live model serving outputs | Active |

---

## Artifact Locations

| Artifact | Path | Status |
|----------|------|--------|
| Model Registry | `ml_ops/model_registry.json` | Active |
| Versioning Guide | `ml_ops/MODEL_VERSIONING.md` | Active |
| Player Tags | `outputs/tags/player_tags.json` | Active |
| Clustering CSV | `outputs/tags/player_clustering_2023.csv` | Active |
| Training Script | `scripts/analysis/player_clustering_v2.py` | Active |
| Archived V1 | `scripts/archive/player_clustering.py` | Archived |

---

## Version Transition Log

| Date | From | To | Reason | Author |
|------|------|-----|--------|--------|
| 2026-01-21 | v1.0.0 | v2.0.0 | Feature improvements (position, wickets, recency) | Stephen Curry |
| 2026-02-06 | - | Registry v2.0.0 | Enhanced versioning schema | Ime Udoka |

---

## Next Steps

1. **Andy Flower Review** - Validate cluster labels
2. **Serialize Models** - Save trained K-Means objects to `.joblib`
3. **Create Smoke Tests** - Verify model outputs
4. **MS Dhoni / Nortje Review** - Specific player validation
5. **Reproducibility Tests** - Verify random state consistency

---

## Rollback Procedure

If production issues are detected:

1. Identify the issue and affected version
2. Revert `active_version` pointer in registry
3. Regenerate outputs from previous version script
4. Document incident in changelog
5. Create hotfix version if needed

---

*Ime Udoka - DevOps Lead*
*In coordination with Andy Flower (Cricket Domain)*
*Cricket Playbook v4.0.0*
