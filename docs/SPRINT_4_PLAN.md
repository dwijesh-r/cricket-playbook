# Sprint 4.0 Plan - Mega Review Implementation

**Sprint Owner:** Tom Brady
**Start Date:** TBD (Awaiting Founder Approval)
**Binding Document:** Mega Review #1

---

## Sprint Theme

**"Foundation & Editorial Excellence"**

This sprint establishes the governance framework from Mega Review #1 while addressing critical product issues from Review 5. Focus on building sustainable processes and improving the core stat pack product.

---

## Pre-Sprint Requirements (BLOCKERS)

These must be completed BEFORE sprint work begins:

| Item | Owner | Approval Required |
|------|-------|-------------------|
| Create Florentino Perez agent | Brad Stevens | No |
| Create Jose Mourinho agent | Brad Stevens | No |
| Draft CONSTITUTION.md v2.0 | Brad Stevens + Tom Brady | **YES - Founder** |

---

## Sprint Phases

### Phase 1: Governance Setup (Week 1)

**Goal:** Establish Task Integrity Loop and governance framework.

| Task | Owner | Deliverable |
|------|-------|-------------|
| Create `governance/` folder | Brad Stevens | Folder structure |
| Create Florentino Perez agent | Brad Stevens | `config/agents/florentino-perez.agent.md` |
| Create Jose Mourinho agent | Brad Stevens | `config/agents/jose-mourinho.agent.md` |
| Create Task Integrity Loop doc | Florentino Perez + Tom Brady | `governance/TASK_INTEGRITY_LOOP.md` |
| Draft CONSTITUTION.md v2.0 | Brad Stevens + Tom Brady | `config/CONSTITUTION.md` (await approval) |
| Create HOW_IT_WORKS.md | Tom Brady + Brad Stevens | `docs/HOW_IT_WORKS.md` |
| Add .DS_Store to .gitignore | Brad Stevens | `.gitignore` update |

### Phase 2: Data & Tag Standardization (Week 1-2)

**Goal:** Fix data issues and establish single tag nomenclature.

| Task | Owner | Deliverable |
|------|-------|-------------|
| Create data/PROVENANCE.md | Brock Purdy | Data source documentation |
| Create data/archive/ folder | Brock Purdy | Archive structure |
| **Tag Standardization Audit** | Andy Flower | Tag nomenclature document |
| Audit Workhorse Seamer classification | Andy Flower | Classification review |
| Fix bowler tags (Bumrah example) | Stephen Curry | Updated tags |
| Audit view counts across docs | Stephen Curry | Consistency report |
| Define baselines vs tags | Andy Flower + Stephen Curry | `analysis/baselines_vs_tags.md` |

### Phase 3: Output Quality & Completeness (Week 2)

**Goal:** Fix incomplete matchup data and add documentation.

| Task | Owner | Deliverable |
|------|-------|-------------|
| Fix Aiden Markram matchup data | Stephen Curry | Complete data |
| Fix Devdutt Padikkal pace data | Stephen Curry | Complete data |
| Fix Cameron Green pace data | Stephen Curry | Complete data |
| Verify all 231 players in matchups | Stephen Curry | Validation report |
| Add threshold justification | Stephen Curry | Updated analysis docs |
| Create outputs/matchups/README.md | Stephen Curry | README file |
| Create outputs/tags/README.md | Andy Flower | README file |

### Phase 4: Stat Pack Enhancement (Week 2-3)

**Goal:** Transform stat packs to magazine-style editorial.

| Task | Owner | Deliverable |
|------|-------|-------------|
| Embed archetypes in tables | Virat Kohli + Stephen Curry | Updated template |
| Embed tags in overview table | Virat Kohli + Stephen Curry | Updated template |
| Tabular historical record | Virat Kohli | Updated section |
| Venue: W-L + dot%/boundary% | Stephen Curry + Virat Kohli | Updated section |
| **Improve tactical insights** | Andy Flower + Virat Kohli | Data-backed insights |
| **Create Predicted XI** | Stephen Curry + Pep Guardiola | New section |
| **Create Depth Charts** | Stephen Curry + Andy Flower | New section |

### Phase 5: ML Ops & Documentation (Week 3)

**Goal:** Transparency in models and processes.

| Task | Owner | Deliverable |
|------|-------|-------------|
| ML Ops Product Description | Ime Udoka | `ml_ops/PRODUCT_DESCRIPTION.md` |
| Add visualizations | Kevin de Bruyne | Charts/diagrams |
| Create notebooks/USER_GUIDE.md | Stephen Curry | User guide |
| Agent performance review | Brad Stevens | Performance report |
| Jose Mourinho ecosystem analysis | Jose Mourinho | Analysis report |

### Phase 6: Testing & Quality (Week 3-4)

**Goal:** Robust validation and testing.

| Task | Owner | Deliverable |
|------|-------|-------------|
| Schema validation tests | N'Golo Kanté | Test suite |
| Output existence tests | N'Golo Kanté | Test suite |
| Null check tests | N'Golo Kanté | Test suite |
| Update tests/README.md | N'Golo Kanté | Documentation |
| Define expected schemas per output | N'Golo Kanté | Schema contracts |

---

## Sprint 4.0 Deliverables Summary

### New Files

| File | Owner |
|------|-------|
| `config/agents/florentino-perez.agent.md` | Brad Stevens |
| `config/agents/jose-mourinho.agent.md` | Brad Stevens |
| `governance/TASK_INTEGRITY_LOOP.md` | Florentino Perez + Tom Brady |
| `config/CONSTITUTION.md` v2.0 | Brad Stevens + Tom Brady |
| `docs/HOW_IT_WORKS.md` | Tom Brady + Brad Stevens |
| `data/PROVENANCE.md` | Brock Purdy |
| `analysis/baselines_vs_tags.md` | Stephen Curry + Andy Flower |
| `outputs/matchups/README.md` | Stephen Curry |
| `outputs/tags/README.md` | Andy Flower |
| `ml_ops/PRODUCT_DESCRIPTION.md` | Ime Udoka |
| `notebooks/USER_GUIDE.md` | Stephen Curry |

### Updated Files

| File | Changes | Owner |
|------|---------|-------|
| `.gitignore` | Add .DS_Store | Brad Stevens |
| `data/ipl_2026_squads.csv` | Fix bowler classifications | Stephen Curry |
| All stat packs | Embedded tags, new sections | Virat Kohli |
| Analysis outputs | Fixed completeness | Stephen Curry |
| `tests/README.md` | Purpose and plan | N'Golo Kanté |

### New Features

| Feature | Description | Owner |
|---------|-------------|-------|
| **Predicted XI** | Algorithm-based best XI recommendation | Stephen Curry + Pep Guardiola |
| **Depth Charts** | Position-by-position player rankings | Stephen Curry + Andy Flower |
| **Baselines vs Tags** | Delta comparison to defend methodology | Andy Flower + Stephen Curry |

---

## Success Criteria

| Criteria | Measurement |
|----------|-------------|
| Governance | Task Integrity Loop documented and ready |
| Data Quality | All 231 players in matchup files |
| Tag Consistency | Single nomenclature across all files |
| Stat Packs | Predicted XI and Depth Charts for all 10 teams |
| Documentation | All READMEs complete with purpose |
| Testing | Schema validation tests passing |

---

## Risk Register

| Risk | Mitigation | Owner |
|------|------------|-------|
| Constitution not approved | Work on non-blocked items first | Tom Brady |
| Tag standardization conflicts | Andy Flower final arbiter | Andy Flower |
| Predicted XI algorithm complexity | Start simple, iterate | Stephen Curry |
| Data completeness issues | Audit before fixes | Stephen Curry |

---

## Dependencies

```
Constitution Approval
    ↓
Task Integrity Loop
    ↓
Phase 2-6 can proceed in parallel
    ↓
Stat Pack regeneration (after tag standardization)
```

---

## Agent Assignments

| Agent | Primary Tasks |
|-------|---------------|
| **Tom Brady** | Constitution, HOW_IT_WORKS, sprint management |
| **Brad Stevens** | Agents, governance folder, .gitignore, performance review |
| **Andy Flower** | Tag standardization, baselines, tactical insights |
| **Stephen Curry** | Data fixes, Predicted XI, Depth Charts, matchup completion |
| **Virat Kohli** | Stat pack editorial, presentation |
| **Pep Guardiola** | Predicted XI optimization logic |
| **Brock Purdy** | PROVENANCE, archive, data quality |
| **Ime Udoka** | ML Ops documentation |
| **Kevin de Bruyne** | Visualizations |
| **N'Golo Kanté** | Testing, schema contracts |
| **Florentino Perez** (NEW) | Task Integrity Loop, value gating |
| **Jose Mourinho** (NEW) | Ecosystem analysis, robustness review |

---

## Estimated Effort

| Phase | Duration | Parallel |
|-------|----------|----------|
| Phase 1 | 3-4 days | No |
| Phase 2 | 5-6 days | After Phase 1 |
| Phase 3 | 4-5 days | With Phase 2 |
| Phase 4 | 6-7 days | After Phase 2-3 |
| Phase 5 | 4-5 days | With Phase 4 |
| Phase 6 | 3-4 days | With Phase 4-5 |

**Total Sprint Duration:** ~3-4 weeks

---

## Post-Sprint: Future Scope

Items deferred to Sprint 5.0+:

| Item | Source | Priority |
|------|--------|----------|
| Match Phase Index (historical) | Review 5 | P1 |
| Clutch Performance Measurement | Review 5 | P1 |
| Toss Advantage Index | Review 5 | P1 |
| Novel Composite Metrics | Review 5 | P2 |
| DuckDB scalability | Mega Review | P2 |
| CI/CD artifact comparison | Mega Review | P2 |
| KenPom pre-season model | Review 5 | P2 |

---

*Cricket Playbook Sprint 4.0*
*Tom Brady, Product Owner*
*2026-01-31*
