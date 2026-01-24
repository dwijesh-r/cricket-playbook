# Cricket Playbook - Kanban Board

**Product Owner:** Tom Brady
**Version:** 2.8.0
**Last Updated:** 2026-01-25

---

## Board Overview

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│    BACKLOG      │    TO DO        │   IN PROGRESS   │    REVIEW       │     DONE        │
│    (Icebox)     │  (Sprint 2.9)   │                 │                 │   (Sprint 2.8)  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

---

## ✅ DONE (Sprint 2.8 - Completed)

| ID | Task | Owner | Completed |
|----|------|-------|-----------|
| S2.8-01 | Filter all analytics to 2023+ data | Stephen Curry | 2026-01-25 |
| S2.8-02 | Standardize cluster labels across codebase | Stephen Curry | 2026-01-25 |
| S2.8-03 | CSV schema documentation | Stephen Curry | 2026-01-25 |
| S2.8-04 | Andy Flower domain review | Andy Flower | 2026-01-25 |
| S2.8-05 | Regenerate all stat packs (2023+ data) | Stephen Curry | 2026-01-25 |
| S2.8-06 | Update all README files to v2.8.0 | Tom Brady | 2026-01-25 |
| S2.8-07 | Fix generate_stat_packs.py cluster lookups | Stephen Curry | 2026-01-25 |

---

## 🔍 REVIEW (Awaiting Approval)

| ID | Task | Owner | Reviewer | Status |
|----|------|-------|----------|--------|
| S2.9-00 | **Founder Review #4** | Tom Brady | Founder | PENDING |

### Founder Review #4 Checklist
- [ ] 2023+ data filter implementation
- [ ] Standardized cluster labels (6 batter, 7 bowler roles)
- [ ] CSV output documentation
- [ ] Stat pack accuracy with new tags
- [ ] README completeness

---

## 🚧 IN PROGRESS

| ID | Task | Owner | Priority | Notes |
|----|------|-------|----------|-------|
| S2.9-01 | Advanced cricket analytics research | Andy Flower | P1 | See research agenda below |

---

## 📋 TO DO (Sprint 2.9 - Production Readiness)

### P0 - Critical (Must Have)

| ID | Task | Owner | Estimate | Dependencies |
|----|------|-------|----------|--------------|
| S2.9-02 | GitHub Actions CI workflow | **Ime Udoka** | 4h | None |
| S2.9-03 | Pre-commit hooks setup | **Ime Udoka** | 2h | None |
| S2.9-04 | Founder Review #4 response | Tom Brady | 2h | S2.9-00 |

*Note: CI/CD reassigned from Brad Stevens to Ime Udoka (ML Ops includes DevOps)*

### P1 - High (Should Have)

| ID | Task | Owner | Estimate | Dependencies |
|----|------|-------|----------|--------------|
| S2.9-05 | Model serialization (joblib) | Ime Udoka | 3h | S2.9-03 |
| S2.9-06 | Recency weighting toggle | Stephen Curry | 4h | None |
| S2.9-07 | Unit test restructuring | N'Golo Kanté | 4h | S2.9-02 |
| S2.9-08 | Andy Flower analytics implementation | Stephen Curry | 8h | S2.9-01 |

### P2 - Medium (Nice to Have)

| ID | Task | Owner | Estimate | Dependencies |
|----|------|-------|----------|--------------|
| S2.9-09 | Interactive dashboard (Streamlit) | Kevin de Bruyne | 8h | None |
| S2.9-10 | Great Expectations validation | Brock Purdy | 6h | None |
| S2.9-11 | Type hints (mypy strict) | Brad Stevens | 4h | S2.9-03 |

---

## 📦 BACKLOG (Future Sprints)

### Sprint 2.10 - API & Integration

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| S2.10-01 | REST API endpoint (FastAPI) | Jayson Tatum | P2 |
| S2.10-02 | Real-time match simulation | Stephen Curry | P3 |
| S2.10-03 | Webhook for live data feeds | Brock Purdy | P3 |

### Sprint 2.11 - Advanced Analytics

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| S2.11-01 | Win probability model | Stephen Curry | P2 |
| S2.11-02 | Player form tracker (rolling 10 matches) | Stephen Curry | P2 |
| S2.11-03 | Venue-pitch condition analysis | Andy Flower | P2 |
| S2.11-04 | Opposition-specific tactics engine | Pep Guardiola | P3 |

### Icebox (Unscheduled)

| ID | Task | Owner | Priority |
|----|------|-------|----------|
| ICE-01 | Historical trend analysis (year-over-year) | Stephen Curry | P3 |
| ICE-02 | Injury/availability tracking | Tom Brady | P3 |
| ICE-03 | Player valuation model (auction pricing) | Stephen Curry | P3 |
| ICE-04 | Commentary auto-generation | Virat Kohli | P3 |
| ICE-05 | Video highlight tagging integration | Kevin de Bruyne | P4 |

---

## 🔬 Andy Flower Research Agenda (S2.9-01)

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
- Research document with cricket domain insights
- Proposed metrics and calculations
- Implementation recommendations for Stephen Curry

---

## Sprint 2.9 Timeline

```
Week 1 (Jan 27-31):
├── Mon: Ime Udoka - CI/CD setup (S2.9-02, S2.9-03)
├── Tue: Andy Flower - Research document complete (S2.9-01) ✓
├── Wed: Founder Review submitted (S2.9-00)
├── Thu: Tom Brady - Review response (S2.9-04)
└── Fri: Ime Udoka - Model serialization (S2.9-05)

Week 2 (Feb 3-7):
├── Mon: Stephen Curry - Recency weighting (S2.9-06)
├── Tue: N'Golo Kanté - Test restructuring (S2.9-07)
├── Wed-Thu: Stephen Curry - Analytics implementation (S2.9-08)
└── Fri: Sprint 2.9 review & retrospective
```

## Agent Role Clarification

| Agent | Primary Role | CI/CD Role |
|-------|--------------|------------|
| **Ime Udoka** | ML Ops Engineer | **Implements** CI/CD, pre-commit, deployment |
| **Brad Stevens** | Architecture & Best Practices | **Advises** on standards, reviews configs |
| **Brock Purdy** | Data Pipeline | **Implements** Great Expectations (data validation) |

---

## Definition of Done

- [ ] Code passes all tests (pytest)
- [ ] Code passes linting (Ruff)
- [ ] Documentation updated
- [ ] README reflects changes
- [ ] Committed to main branch
- [ ] Peer reviewed (if applicable)

---

## Blockers & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Founder Review delays | High | Prepare detailed documentation |
| Small sample size (2023+ only) | Medium | Add optional full-history mode |
| CI/CD complexity | Low | Start with simple workflow |

---

*Cricket Playbook v2.8.0 - Sprint Planning*
