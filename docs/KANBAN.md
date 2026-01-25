# Cricket Playbook - Kanban Board

**Product Owner:** Tom Brady
**Version:** 2.9.0
**Last Updated:** 2026-01-25

---

## Board Overview

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│    BACKLOG      │    TO DO        │   IN PROGRESS   │    REVIEW       │     DONE        │
│    (Icebox)     │  (Sprint 3.0)   │                 │                 │   (Sprint 2.9)  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

---

## ✅ DONE (Sprint 2.9 - Completed)

### Bug Fixes & Data Quality

| ID | Task | Owner | Completed | Commit |
|----|------|-------|-----------|--------|
| S2.9-01 | Entry point bug fix (ball_seq > 120) | Andy Flower + Stephen Curry | 2026-01-25 | `d320501` |
| S2.9-02 | Output validation script | Andy Flower | 2026-01-25 | `d320501` |
| S2.9-03 | Matchup missing data fix (use analytics table) | Stephen Curry | 2026-01-25 | `e085a58` |
| S2.9-04 | Matchup tag criteria (add BPD check) | Stephen Curry | 2026-01-25 | `e085a58` |
| S2.9-05 | Player clustering ball_seq fix | Stephen Curry | 2026-01-25 | `ef3effd` |

### CI/CD & Infrastructure

| ID | Task | Owner | Completed | Commit |
|----|------|-------|-----------|--------|
| S2.9-06 | GitHub Actions CI workflow | Ime Udoka | 2026-01-25 | `d320501` |
| S2.9-07 | Pre-commit hooks (Ruff linter/formatter) | Ime Udoka | 2026-01-25 | `d320501` |

### Sprint 2.8 (Prior Sprint)

| ID | Task | Owner | Completed |
|----|------|-------|-----------|
| S2.8-01 | Filter all analytics to 2023+ data | Stephen Curry | 2026-01-25 |
| S2.8-02 | Standardize cluster labels across codebase | Stephen Curry | 2026-01-25 |
| S2.8-03 | CSV schema documentation | Stephen Curry | 2026-01-25 |
| S2.8-04 | Andy Flower domain review | Andy Flower | 2026-01-25 |
| S2.8-05 | Regenerate all stat packs (2023+ data) | Stephen Curry | 2026-01-25 |
| S2.8-06 | Update all README files to v2.8.0 | Tom Brady | 2026-01-25 |
| S2.8-07 | Fix generate_stat_packs.py cluster lookups | Stephen Curry | 2026-01-25 |
| S2.8-08 | Glossary with all definitions and criteria | Tom Brady | 2026-01-25 |

---

## 🔍 REVIEW (Awaiting Founder Approval)

| ID | Task | Owner | Reviewer | Status |
|----|------|-------|----------|--------|
| **FR-4** | **Founder Review #4** | Tom Brady | Founder | **READY FOR REVIEW** |

### Founder Review #4 Checklist

**Data Quality & Accuracy:**
- [x] 2023+ data filter implementation (219 IPL matches)
- [x] Entry point bug fixed (max_entry_ball ≤ 120)
- [x] Matchup data complete (422 batters, was 125)
- [x] ball_seq bugs fixed across codebase

**Cluster Labels & Tags:**
- [x] Standardized 6 batter roles + 7 bowler roles
- [x] Tag criteria documented with thresholds
- [x] BPD (balls per dismissal) added to matchup tags

**Documentation:**
- [x] CSV schema documentation in outputs/README.md
- [x] Glossary with phases, metrics, tag criteria
- [x] All README files updated to v2.9.0

**Infrastructure:**
- [x] GitHub Actions CI workflow
- [x] Pre-commit hooks (Ruff)
- [x] Output validation script

**Outputs to Review:**
- `outputs/batter_entry_points.csv` - All values 1-120 ✓
- `outputs/batter_bowling_type_matchup.csv` - 422 batters (was 125) ✓
- `outputs/bowler_phase_performance.csv` - 208 bowlers ✓
- `stat_packs/*.md` - All 10 team stat packs regenerated ✓

---

## 🚧 IN PROGRESS

| ID | Task | Owner | Priority | Notes |
|----|------|-------|----------|-------|
| - | *Awaiting Founder Review #4* | - | - | - |

---

## 📋 TO DO (Sprint 3.0 - Post-Founder Review)

### P0 - Critical (Must Have)

| ID | Task | Owner | Estimate | Dependencies |
|----|------|-------|----------|--------------|
| S3.0-01 | Founder Review #4 response | Tom Brady | 2h | FR-4 |
| S3.0-02 | Address any Founder feedback | Stephen Curry | 4h | S3.0-01 |

### P1 - High (Should Have)

| ID | Task | Owner | Estimate | Dependencies |
|----|------|-------|----------|--------------|
| S3.0-03 | Model serialization (joblib) | Ime Udoka | 3h | None |
| S3.0-04 | Recency weighting toggle | Stephen Curry | 4h | None |
| S3.0-05 | Unit test restructuring | N'Golo Kanté | 4h | None |
| S3.0-06 | Andy Flower analytics implementation | Stephen Curry | 8h | See research agenda |

### P2 - Medium (Nice to Have)

| ID | Task | Owner | Estimate | Dependencies |
|----|------|-------|----------|--------------|
| S3.0-07 | Interactive dashboard (Streamlit) | Kevin de Bruyne | 8h | None |
| S3.0-08 | Great Expectations validation | Brock Purdy | 6h | None |
| S3.0-09 | Type hints (mypy strict) | Brad Stevens | 4h | None |
| S3.0-10 | Bowler handedness matchup fixes | Stephen Curry | 3h | Similar to batter matchup |

---

## 📦 BACKLOG (Future Sprints)

### Sprint 3.1 - API & Integration

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| S3.1-01 | REST API endpoint (FastAPI) | Jayson Tatum | P2 |
| S3.1-02 | Real-time match simulation | Stephen Curry | P3 |
| S3.1-03 | Webhook for live data feeds | Brock Purdy | P3 |

### Sprint 3.2 - Advanced Analytics

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| S3.2-01 | Win probability model | Stephen Curry | P2 |
| S3.2-02 | Player form tracker (rolling 10 matches) | Stephen Curry | P2 |
| S3.2-03 | Venue-pitch condition analysis | Andy Flower | P2 |
| S3.2-04 | Opposition-specific tactics engine | Pep Guardiola | P3 |

### Icebox (Unscheduled)

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| ICE-01 | Historical trend analysis (year-over-year) | Stephen Curry | P3 |
| ICE-02 | Injury/availability tracking | Tom Brady | P3 |
| ICE-03 | Player valuation model (auction pricing) | Stephen Curry | P3 |
| ICE-04 | Commentary auto-generation | Virat Kohli | P3 |
| ICE-05 | Video highlight tagging integration | Kevin de Bruyne | P4 |

---

## 🔬 Andy Flower Research Agenda

### Groundbreaking Cricket Analytics Approaches

**Research Areas:**

1. **Match Phase Dynamics**
   - Momentum shift detection (when does a match "turn"?)
   - Pressure index by ball (dot ball sequences, wicket clusters)
   - Optimal declaration/chase timing models

2. **Player Impact Beyond Stats**
   - "Clutch" performance metric (pressure situations)
   - Partnership value (how players combine)
   - Fielding impact quantification

3. **Tactical Pattern Recognition**
   - Field placement optimization by batter type
   - Bowling pattern detection (line/length sequences)
   - Batting intent classification (attack/defend/rotate)

4. **Contextual Performance**
   - Toss impact by venue
   - Dew factor modeling (2nd innings advantage)
   - Pitch deterioration tracking

5. **Team Composition Analytics**
   - Optimal batting order simulation
   - Bowling rotation strategies
   - Impact player selection criteria

**Deliverables:**
- Research document: `editorial/andy_flower_analytics_research.md` ✓
- Proposed metrics and calculations
- Implementation recommendations for Stephen Curry

---

## Sprint 2.9 Summary

### Key Achievements

| Category | Metric | Before | After |
|----------|--------|--------|-------|
| Batter matchup data | Total batters | 125 | 422 |
| Entry point validation | max_entry_ball | 136 | 120 |
| CI/CD | Automated checks | None | Ruff + pre-commit |
| Documentation | Glossary | Missing | Complete |

### Bug Fixes Summary

| Bug | Root Cause | Fix |
|-----|------------|-----|
| Entry point > 120 | `ball_seq` includes extras | Use legal ball count |
| Missing matchup data | Joined only 2026 squad bowlers | Use analytics table |
| Wrong tag criteria | Only checked SR | Added BPD check |
| Clustering position | `ball_seq` for batting position | Use legal ball count |

### Commits This Sprint

1. `d320501` - Entry point fix + validation + CI/CD
2. `e085a58` - Matchup data fixes + tag criteria
3. `ef3effd` - Player clustering ball_seq fix

---

## Sprint 3.0 Timeline (Post-Review)

```
After Founder Review #4 Approval:

Day 1-2:
├── Tom Brady - Process Founder feedback (S3.0-01)
└── Stephen Curry - Address any issues (S3.0-02)

Day 3-5:
├── Ime Udoka - Model serialization (S3.0-03)
├── Stephen Curry - Recency weighting toggle (S3.0-04)
└── N'Golo Kanté - Test restructuring (S3.0-05)

Day 6-10:
├── Stephen Curry - Andy Flower analytics (S3.0-06)
├── Kevin de Bruyne - Dashboard prototype (S3.0-07)
└── Sprint 3.0 review & retrospective
```

---

## Agent Role Clarification

| Agent | Primary Role | Sprint 2.9 Contribution |
|-------|--------------|-------------------------|
| **Andy Flower** | Cricket Analytics QA | Entry point bug investigation, validation script |
| **Stephen Curry** | Analytics Lead | All bug fixes, matchup improvements |
| **Ime Udoka** | ML Ops Engineer | CI/CD setup, pre-commit hooks |
| **Tom Brady** | Product Owner | Kanban management, documentation |
| **Brad Stevens** | Architecture | Standards review |
| **N'Golo Kanté** | QA Engineer | Test coverage (pending) |

---

## Definition of Done

- [x] Code passes all tests (pytest)
- [x] Code passes linting (Ruff)
- [x] Pre-commit hooks pass
- [x] Documentation updated
- [x] README reflects changes
- [x] Committed to main branch
- [ ] **Founder Review #4 approved**

---

## Blockers & Risks

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Founder Review delays | High | Comprehensive documentation prepared | Ready |
| Small sample size (2023+ only) | Medium | Add optional full-history mode | Backlog |
| ball_seq bugs in other scripts | High | Grep audit completed | ✅ Fixed |

---

*Cricket Playbook v2.9.0 - Ready for Founder Review #4*
