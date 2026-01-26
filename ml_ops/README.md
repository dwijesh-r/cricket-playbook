# ML Ops

Model registry and deployment tracking.

---

## Contents

| File | Description |
|------|-------------|
| `model_registry.json` | Model version registry |
| `deployment_manifest.md` | Deployment status and gates |

---

## Current Models

| Model | Version | Status |
|-------|---------|--------|
| Player Clustering | v2.0.0 | Active |

---

## Clustering Model V2

**Algorithm:** K-means with PCA dimensionality reduction

| Component | Batters | Bowlers |
|-----------|---------|---------|
| PCA Variance | 76.8% | 63.4% |
| Clusters | 5 | 5 |
| Min Balls | 100 | 60 |

**Batter Roles:** EXPLOSIVE_OPENER, PLAYMAKER, ANCHOR, ACCUMULATOR, MIDDLE_ORDER, FINISHER

**Bowler Roles:** PACER, SPINNER, WORKHORSE, NEW_BALL_SPECIALIST, MIDDLE_OVERS_CONTROLLER, DEATH_SPECIALIST, PART_TIMER

---

## Deployment Gates

| Gate | Criteria |
|------|----------|
| PCA Variance | Batters >70%, Bowlers >50% |
| Smoke Tests | 76 pytest tests pass |
| Domain Review | Andy Flower approval |
| Founder Review | Final sign-off |

---

## Maintainer

**Ime Udoka** - ML Ops Engineer

---

*Cricket Playbook v3.1.0*
