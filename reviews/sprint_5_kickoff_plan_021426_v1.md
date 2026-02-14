# Sprint 5.0 Kickoff Plan

**Document:** sprint_5_kickoff_plan_021426_v1.md
**Date:** February 14, 2026
**Author:** Tom Brady (PO & Editor-in-Chief)
**Sprint:** SPRINT-002 — Interactive Intelligence & ML
**Duration:** Feb 15 - Feb 28, 2026 (2 weeks)
**Token Budget:** 500K tokens (Founder-approved)

---

## 1. Sprint Goals

Sprint 5.0 advances Cricket Playbook from a static analytics product to an interactive intelligence platform. Three parallel workstreams:

### Workstream 1: Win Probability Model (EPIC-018)
Build an in-match prediction engine using ball-by-ball features from the DuckDB fact_ball data (2.38M rows). This is the first ML-powered real-time analytics feature.

### Workstream 2: React Interactive Dashboard (EPIC-019)
Replace the static HTML Lab dashboard with a React-based SPA featuring DuckDB-WASM for browser-native SQL, a design system with theme tokens, and migrated team/research pages.

### Workstream 3: Player Comparison Tool (EPIC-020)
Head-to-head analytics with radar charts, side-by-side stats, multi-player comparison (3+), and shareable/exportable results.

---

## 2. Epic Breakdown with Tickets

### EPIC-018: Win Probability Model (5 tickets, Owner: Jose Mourinho)

| Ticket | Title | Priority | Assignee | Effort |
|--------|-------|----------|----------|--------|
| TKT-205 | Research & define win probability model architecture | P0 | Jose Mourinho | Deep Work |
| TKT-206 | Feature engineering from fact_ball data | P0 | Stephen Curry | Deep Work |
| TKT-207 | Train & validate win probability model | P0 | Ime Udoka | Marathon |
| TKT-208 | Integrate win probability into The Lab dashboard | P1 | Kevin de Bruyne | Deep Work |
| TKT-209 | Model monitoring & drift detection setup | P1 | Ime Udoka | Hustle |

**Critical Path:** TKT-205 -> TKT-206 -> TKT-207 -> TKT-208 (sequential dependency)
**Parallel Track:** TKT-209 can start after TKT-207

### EPIC-019: Interactive React Dashboard (6 tickets, Owner: Kevin de Bruyne)

| Ticket | Title | Priority | Assignee | Effort |
|--------|-------|----------|----------|--------|
| TKT-210 | React project setup + build pipeline | P0 | Brad Stevens | Deep Work |
| TKT-211 | Design system — component library + theme tokens | P0 | Kevin de Bruyne | Deep Work |
| TKT-212 | Data layer — DuckDB-WASM integration + React hooks | P0 | Brad Stevens | Marathon |
| TKT-213 | Team pages — migrate squad, depth chart, pressure tabs | P1 | Kevin de Bruyne | Marathon |
| TKT-214 | Research Desk — migrate NL search + SQL Lab to React | P1 | Kevin de Bruyne | Deep Work |
| TKT-215 | Testing + CI integration for React dashboard | P1 | Brad Stevens | Hustle |

**Critical Path:** TKT-210 -> TKT-211 + TKT-212 (parallel) -> TKT-213 + TKT-214 (parallel) -> TKT-215
**Note:** TKT-210 must complete before any other React work can begin

### EPIC-020: Player Comparison Tool (4 tickets, Owner: Stephen Curry)

| Ticket | Title | Priority | Assignee | Effort |
|--------|-------|----------|----------|--------|
| TKT-216 | Head-to-head comparison data pipeline | P0 | Stephen Curry | Deep Work |
| TKT-217 | Comparison UI — radar charts + side-by-side stats | P0 | Kevin de Bruyne | Deep Work |
| TKT-218 | Multi-player comparison (3+ players) | P1 | Stephen Curry | Hustle |
| TKT-219 | Shareable comparison links + PNG export | P2 | Kevin de Bruyne | Hustle |

**Critical Path:** TKT-216 -> TKT-217 -> TKT-218 -> TKT-219 (sequential)

---

## 3. Key Dependencies

### Cross-Epic Dependencies
- **EPIC-019 blocks EPIC-018 integration**: TKT-208 (win prob in dashboard) may need to target the React dashboard (TKT-210/211/212) rather than the static HTML Lab
- **EPIC-020 data pipeline**: TKT-216 relies on the existing DuckDB infrastructure but may benefit from React hooks (TKT-212) for the UI layer
- **Design system**: TKT-211 (component library) is shared infrastructure for both TKT-208 and TKT-217

### External Dependencies
- **DuckDB-WASM compatibility**: Browser support for WASM must be validated early (TKT-212)
- **Sprint 4.0 close-out**: 15 close-out tickets (TKT-220 to TKT-234) running in parallel during Sprint 5.0 Week 1 — some agents will be split across both sprints
- **Cricsheet data freshness**: TKT-229 (data pipeline) from Sprint 4.0 close-out may impact feature engineering (TKT-206)

### Agent Allocation Conflicts
| Agent | Sprint 4 Close-out | Sprint 5 Load | Risk |
|-------|-------------------|---------------|------|
| Kevin de Bruyne | TKT-225, TKT-226, TKT-232 | TKT-208, TKT-211, TKT-213, TKT-214, TKT-217, TKT-219 | HIGH — heaviest workload |
| Brad Stevens | None | TKT-210, TKT-212, TKT-215 | LOW |
| Stephen Curry | TKT-224 | TKT-206, TKT-216, TKT-218 | MEDIUM |
| Ime Udoka | None | TKT-207, TKT-209 | LOW |
| Jose Mourinho | TKT-223 | TKT-205 | LOW |

**Mitigation:** Kevin de Bruyne is the bottleneck. Sprint 4 close-out tasks (TKT-225, 226, 232) should be completed in Week 1 before Sprint 5 ramps up.

---

## 4. Success Criteria

### Sprint-Level Success
- [ ] All 15 Sprint 5.0 tickets reach at least REVIEW state by Feb 28
- [ ] At least 10/15 tickets marked DONE
- [ ] System health score remains >= 85/100
- [ ] Win probability model achieves >= 70% accuracy on validation set

### Epic-Level Success
| Epic | Success Criteria |
|------|-----------------|
| EPIC-018 | Trained model with documented accuracy, integrated into dashboard, monitoring active |
| EPIC-019 | React app building, design system documented, at least team pages migrated |
| EPIC-020 | 2-player comparison working end-to-end, radar charts rendering, data pipeline validated |

### Quality Gates (from Task Integrity Loop)
- All P0 tickets must pass Florentino Gate before execution
- All ML tickets (TKT-205, 206, 207) must pass Domain Sanity review (Andy Flower + Jose Mourinho)
- React dashboard (TKT-210-215) must pass System Check (Kante QA)
- Founder validation required for each epic before marking DONE

---

## 5. Token Budget

| Allocation | Tokens | Notes |
|-----------|--------|-------|
| **Total Budget** | 500,000 | Founder-approved 2026-02-14 |
| EPIC-018 (Win Prob) | ~180,000 | ML research + training is token-heavy |
| EPIC-019 (React) | ~200,000 | Code generation for React migration |
| EPIC-020 (Comparison) | ~80,000 | Moderate complexity |
| Buffer | ~40,000 | For close-out overlap and rework |

---

## 6. Week-by-Week Plan

### Week 1 (Feb 15-21): Foundation
- **EPIC-018:** TKT-205 (research) + TKT-206 (feature engineering) — both must complete
- **EPIC-019:** TKT-210 (React setup) — critical foundation
- **EPIC-020:** TKT-216 (data pipeline) — can start immediately
- **Close-out:** Complete remaining Sprint 4.0 close-out tickets

### Week 2 (Feb 22-28): Build & Integrate
- **EPIC-018:** TKT-207 (train model) + TKT-208 (integrate) + TKT-209 (monitoring)
- **EPIC-019:** TKT-211 (design system) + TKT-212 (DuckDB-WASM) + TKT-213/214 (migration)
- **EPIC-020:** TKT-217 (comparison UI) + TKT-218 (multi-player) + TKT-219 (export)

---

## 7. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| DuckDB-WASM performance issues | Medium | High | Early prototype in Week 1 (TKT-212) |
| Win prob model accuracy < 70% | Medium | Medium | Fallback to simpler logistic regression |
| Kevin de Bruyne overload | High | High | Prioritize P0 tickets, defer P1/P2 to Sprint 6 |
| React migration breaks existing Lab | Low | High | Feature branch + staging deploy before merge |
| Sprint 4 close-out delays Sprint 5 | Medium | Medium | Hard deadline: close-out must finish by Feb 18 |

---

*Sprint 5.0: Where we go from "pro team internal prep" to "interactive intelligence platform."*

*Prepared by Tom Brady, PO & Editor-in-Chief*
*Cricket Playbook v5.0.0*
