# Sprint 4.0 Plan - Mega Review Implementation (v2.0)

**Sprint Owner:** Tom Brady
**Start Date:** 2026-01-31 (Constitution Approved)
**Binding Documents:** Mega Review #1, Review 5
**Last Updated:** 2026-02-01
**Version:** 2.0 (Governance Compliant)

---

## Sprint Theme

**"Foundation & Editorial Excellence"**

This sprint establishes the governance framework from Mega Review #1 while addressing critical product issues from Review 5. Focus on building sustainable processes and improving the core stat pack product.

**Core Philosophy (from Founder):**
> "Cricket fans don't pay for analytics, they pay for confidence, narrative clarity and authority. What will make money is ruthless editorial compression, strong opinions based on transparent data and zero temptation to be only analytical heavy."

---

## Governance Compliance

This sprint follows the Task Integrity Loop (8 steps) and Constitution v2.0:

| Gate | Owner | When |
|------|-------|------|
| PRD Creation (Step 0) | Task Owner | Before work begins |
| Florentino Gate (Step 1) | Florentino Perez | After PRD, before build |
| Domain Sanity (Step 3) | Jose Mourinho, Andy Flower, Pep Guardiola | After build |
| Enforcement Check (Step 4) | Tom Brady | Before merge |
| System Check (Step 7) | N'Golo Kanté | After merge |

---

## Current Status Summary

| Phase | Status | Progress |
|-------|--------|----------|
| Pre-Sprint | ✅ COMPLETE | 3/3 |
| Phase 0: Vision & Criteria | ✅ COMPLETE | 7/7 |
| Phase 1: Governance | ✅ COMPLETE | 7/10 |
| Phase 2: Data & Tags | 🔄 IN PROGRESS | 5/12 |
| Phase 3: Output Quality | 🔄 IN PROGRESS | 5/11 |
| Phase 4: Stat Pack | 🔄 IN PROGRESS | 3/21 |
| Phase 5: ML Ops & Docs | ❌ NOT STARTED | 0/9 |
| Phase 6: Testing | 🔄 IN PROGRESS | 1/6 |
| Phase 7: Script Quality | ❌ NOT STARTED | 0/4 |

**Overall: 31/83 tasks complete (37%)**

---

## Pre-Sprint Requirements (BLOCKERS) ✅ COMPLETE

| Item | Owner | Status |
|------|-------|--------|
| Create Florentino Perez agent | Brad Stevens | ✅ Done |
| Create Jose Mourinho agent | Brad Stevens | ✅ Done |
| Draft CONSTITUTION.md v2.0 | Brad Stevens + Tom Brady | ✅ Founder Approved |

---

## Phase 0: Product Vision & Governance Criteria ✅ COMPLETE

**Goal:** Establish product clarity and operational criteria for new governance agents.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Update PRD for magazine-style focus | Tom Brady | `docs/PRD_CRICKET_PLAYBOOK.md` v3.0.0 | ✅ Done |
| Create product positioning document | Tom Brady + Virat Kohli | `docs/PRODUCT_POSITIONING.md` | ✅ Done |
| Define Editorial vs Analytics boundary | Brad Stevens | `governance/EDITORIAL_ANALYTICS_BOUNDARY.md` | ✅ Done |
| Define Florentino Gate criteria | Florentino Perez + Tom Brady | Embedded in `governance/TASK_INTEGRITY_LOOP.md` | ✅ Exists |
| Define Jose Mourinho review criteria | Jose Mourinho | Embedded in `governance/TASK_INTEGRITY_LOOP.md` | ✅ Exists |
| Create Task PRD template | Tom Brady | `governance/templates/TASK_PRD_TEMPLATE.md` | ✅ Exists |
| Create Domain Sanity checklist template | Andy Flower | `governance/templates/DOMAIN_SANITY_CHECKLIST.md` | ✅ Done |

**Phase 0 Definition of Done:**
- [x] All criteria documents reviewed by Florentino Perez
- [x] Templates usable for Phase 1+ tasks
- [x] Product vision clear to all agents

---

## Phase 1: Governance Setup ✅ COMPLETE

**Goal:** Establish Task Integrity Loop and governance framework.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Create `governance/` folder | Brad Stevens | Folder structure | ✅ Done |
| Create Florentino Perez agent | Brad Stevens | `config/agents/florentino-perez.agent.md` | ✅ Done |
| Create Jose Mourinho agent | Brad Stevens | `config/agents/jose-mourinho.agent.md` | ✅ Done |
| Create Task Integrity Loop doc | Florentino Perez + Tom Brady | `governance/TASK_INTEGRITY_LOOP.md` | ✅ Done |
| Draft CONSTITUTION.md v2.0 | Brad Stevens + Tom Brady | `config/CONSTITUTION.md` | ✅ Approved |
| Create HOW_IT_WORKS.md | Tom Brady + Brad Stevens | `docs/HOW_IT_WORKS.md` | ✅ Done |
| Add .DS_Store to .gitignore | Brad Stevens | `.gitignore` update | ✅ Done |
| Remove committed .DS_Store files | Brad Stevens | Clean repo | ❌ To Do |
| Create auto-updating manifest system | Brock Purdy | Manifest automation | ❌ To Do |
| Create outputs changelog generator | Brock Purdy | Changelog on each run | ❌ To Do |

**Phase 1 Definition of Done:**
- [x] Florentino Gate: APPROVED
- [x] Constitution: Founder APPROVED
- [x] Task Integrity Loop: Documented
- [ ] Manifest automation: Working
- [x] Committed to main

---

## Phase 2: Data & Tag Standardization 🔄 IN PROGRESS

**Goal:** Fix data issues and establish single tag nomenclature.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Create data/PROVENANCE.md | Brock Purdy | Data source documentation | ✅ Done |
| Create data/archive/ folder | Brock Purdy | Archive structure | ❌ To Do |
| Move deprecated files to archive | Brock Purdy | Clean data folder | ❌ To Do |
| **Tag Standardization Audit** | Stephen Curry (Lead) + Andy Flower (Review) | Tag nomenclature document | ✅ Done |
| Audit Workhorse Seamer classification | Andy Flower | Classification review | ✅ Done |
| Fix bowler tags (Bumrah example) | Stephen Curry | Updated tags | ✅ Done |
| Verify 2023+ data only for tagging | Stephen Curry | Verification report | ✅ Done |
| Audit view counts across docs | Stephen Curry | Consistency report | ❌ To Do |
| Reconcile archetype counts across docs | Stephen Curry + Andy Flower | Alignment report | ❌ To Do |
| Define baselines vs tags | Andy Flower + Stephen Curry | `analysis/baselines_vs_tags.md` | ❌ To Do |
| Verify PCA variance alignment | Ime Udoka | Validation report | ❌ To Do |
| Add Limitations section to outputs/README | Andy Flower | Updated README | ❌ To Do |

**Phase 2 Definition of Done:**
- [ ] Florentino Gate: APPROVED
- [ ] Jose Mourinho: YES (data robustness)
- [ ] Andy Flower: YES (cricket truth)
- [ ] Pep Guardiola: YES (system coherence)
- [ ] Tom Brady Enforcement: PASS
- [ ] Single tag system across all outputs
- [ ] Baselines documented for each tag

---

## Phase 3: Output Quality & Completeness 🔄 IN PROGRESS

**Goal:** Fix incomplete matchup data and add documentation.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Fix Aiden Markram matchup data | Stephen Curry | Complete data | ✅ Done |
| Fix Devdutt Padikkal pace data | Stephen Curry | Complete data | ✅ Done |
| Fix Cameron Green pace data | Stephen Curry | Complete data | ✅ Done |
| Verify all 231 players in matchups | Stephen Curry | Validation report | 🔄 98.3% |
| Add threshold justification with EDA links | Stephen Curry | `reviews/phase_tag_criteria.md` | ✅ Done |
| Create outputs/matchups/README.md | Stephen Curry (Lead) + LeBron James (Review) | README file | ❌ To Do |
| Create outputs/tags/README.md | Andy Flower | README file | ❌ To Do |
| Create outputs/metrics/README.md | Stephen Curry | README file | ❌ To Do |
| Create outputs/team/README.md | Stephen Curry | README file | ❌ To Do |
| Create outputs/run-logs/README.md | Brock Purdy | README file | ❌ To Do |
| Editorial review of Phase 3 outputs | Virat Kohli | Sign-off | ❌ To Do |

**Phase 3 Definition of Done:**
- [ ] Florentino Gate: APPROVED
- [ ] Jose Mourinho: YES
- [ ] Andy Flower: YES
- [ ] Pep Guardiola: YES
- [ ] Virat Kohli Editorial: APPROVED
- [ ] Tom Brady Enforcement: PASS
- [ ] All 231 players verified
- [ ] All subdirectory READMEs complete

---

## Phase 4: Stat Pack Enhancement 🔄 IN PROGRESS

**Goal:** Transform stat packs to magazine-style editorial.

### 4A: Template Updates

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Embed archetypes in tables | Virat Kohli + Stephen Curry | Updated template | ✅ Done |
| Embed tags in overview table | Virat Kohli + Stephen Curry | Updated template | ✅ Done |
| Remove standalone archetype section | Virat Kohli | Cleaner template | ❌ To Do |
| Tabular historical record (markdown table) | Virat Kohli | Updated section | ✅ Done |
| Venue: W-L only + dot%/boundary% | Stephen Curry + Virat Kohli | Updated section | ❌ To Do |

### 4B: Tactical Insights (CRITICAL)

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Review all tactical insights | Andy Flower + Virat Kohli | Audit report | ❌ To Do |
| Make insights specific and data-backed | Virat Kohli | Updated insights | ❌ To Do |
| Add editorial narrative | Virat Kohli | Prose improvements | ❌ To Do |
| Ensure each insight is actionable | Andy Flower | Validation | ❌ To Do |
| Reader experience review | LeBron James | Reader perspective report | ❌ To Do |

### 4C: Predicted XI (NEW FEATURE - Requires Graduation)

**Graduation Requirements per Constitution Section 6:**
- [ ] Stephen Curry: Evidence proposal
- [ ] Andy Flower: Cricket truth validation
- [ ] Virat Kohli: Editorial value sign-off
- [ ] Florentino Perez: Paid artifact approval
- [ ] Tom Brady: Scheduling

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Define Predicted XI optimization criteria | Andy Flower | Criteria document | ❌ To Do |
| Implement role fit scoring | Stephen Curry | Algorithm | ❌ To Do |
| Implement depth scoring | Stephen Curry | Algorithm | ❌ To Do |
| Account for variety (pace/spin, LHB/RHB) | Stephen Curry | Variety logic | ❌ To Do |
| Integrate matchup considerations | Stephen Curry | Matchup logic | ❌ To Do |
| Create Predicted XI algorithm | Stephen Curry + Pep Guardiola | Working algorithm | ❌ To Do |
| Create explanation narrative | Virat Kohli | Editorial prose | ❌ To Do |

### 4D: Depth Charts (NEW FEATURE - Requires Graduation)

**Graduation Requirements per Constitution Section 6:**
- [ ] Stephen Curry: Evidence proposal
- [ ] Andy Flower: Cricket truth validation
- [ ] Virat Kohli: Editorial value sign-off
- [ ] Florentino Perez: Paid artifact approval
- [ ] Tom Brady: Scheduling

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Define depth chart positions (9 roles) | Andy Flower | Position definitions | ❌ To Do |
| Create ranking algorithm per position | Stephen Curry | Algorithm | ❌ To Do |
| Generate depth charts for all 10 teams | Stephen Curry | Output files | ❌ To Do |
| Add to stat pack template | Virat Kohli | Template update | ❌ To Do |

**Depth Chart Positions:**
1. Opener (Top 3)
2. #3 (Top 3)
3. Middle Order #4-5 (Top 3)
4. Finisher #6-7 (Top 3)
5. Wicketkeeper (Primary + backup)
6. Lead Pacer (Top 2)
7. Supporting Pacer (Top 3)
8. Lead Spinner (Top 2)
9. All-rounder (Batting + Bowling options)

**Phase 4 Definition of Done:**
- [ ] Florentino Gate: APPROVED for all new features
- [ ] Graduation process complete for Predicted XI
- [ ] Graduation process complete for Depth Charts
- [ ] Jose Mourinho: YES
- [ ] Andy Flower: YES
- [ ] Pep Guardiola: YES
- [ ] LeBron James: Reader experience validated
- [ ] Tom Brady Enforcement: PASS
- [ ] All 10 team stat packs regenerated

---

## Phase 5: ML Ops & Documentation ❌ NOT STARTED

**Goal:** Transparency in models and processes.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| ML Ops Product Description | Ime Udoka | `ml_ops/PRODUCT_DESCRIPTION.md` | ❌ To Do |
| Add ML Ops interpretation guide | Andy Flower | Interpretation section | ❌ To Do |
| Add visualizations | Kevin de Bruyne | Charts/diagrams | ❌ To Do |
| Create notebooks/USER_GUIDE.md | Stephen Curry | User guide | ❌ To Do |
| Agent performance review | Brad Stevens | Performance report | ❌ To Do |
| Identify repetitive agent issues | Brad Stevens | Issue log | ❌ To Do |
| Create agent rating system | Brad Stevens | Rating framework | ❌ To Do |
| Jose Mourinho ecosystem analysis | Jose Mourinho | Analysis report | ❌ To Do |
| Create .github/workflows/README.md | Brad Stevens | Workflow documentation | ❌ To Do |

**Phase 5 Definition of Done:**
- [ ] Florentino Gate: APPROVED
- [ ] Jose Mourinho: YES
- [ ] Andy Flower: YES
- [ ] Pep Guardiola: YES
- [ ] Tom Brady Enforcement: PASS
- [ ] ML Ops fully documented with visualizations

---

## Phase 6: Testing & Quality 🔄 IN PROGRESS

**Goal:** Robust validation and testing.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Schema validation tests | N'Golo Kanté | Test suite | 🔄 33 tests exist |
| Output existence tests | N'Golo Kanté | Test suite | 🔄 43 tests exist |
| Null check tests | N'Golo Kanté | Test suite | ❌ To Do |
| Manifest update tests | N'Golo Kanté | Test suite | ❌ To Do |
| Update tests/README.md with purpose/plan | N'Golo Kanté | Documentation | ✅ Done |
| Define expected schemas per output | N'Golo Kanté | Schema contracts | ❌ To Do |

**Phase 6 Definition of Done:**
- [ ] Florentino Gate: APPROVED
- [ ] All tests passing
- [ ] Schema contracts defined
- [ ] Tom Brady Enforcement: PASS

---

## Phase 7: Script Quality ❌ NOT STARTED

**Goal:** Ensure all scripts are well-documented and maintainable.

| Task | Owner | Deliverable | Status |
|------|-------|-------------|--------|
| Audit all scripts for documentation | Brad Stevens | Audit report | ❌ To Do |
| Add docstrings to all functions | Stephen Curry + Brock Purdy | Updated scripts | ❌ To Do |
| Add script header comments | Stephen Curry + Brock Purdy | Updated scripts | ❌ To Do |
| Create script documentation template | Brad Stevens | Template file | ❌ To Do |

---

## Sprint 4.0 Deliverables Summary

### New Files

| File | Owner | Status |
|------|-------|--------|
| `config/agents/florentino-perez.agent.md` | Brad Stevens | ✅ Done |
| `config/agents/jose-mourinho.agent.md` | Brad Stevens | ✅ Done |
| `governance/TASK_INTEGRITY_LOOP.md` | Florentino Perez + Tom Brady | ✅ Done |
| `config/CONSTITUTION.md` v2.0 | Brad Stevens + Tom Brady | ✅ Approved |
| `docs/HOW_IT_WORKS.md` | Tom Brady + Brad Stevens | ✅ Done |
| `docs/PRD_CRICKET_PLAYBOOK.md` v3.0.0 | Tom Brady | ✅ Done |
| `docs/PRODUCT_POSITIONING.md` | Tom Brady + Virat Kohli | ✅ Done |
| `governance/EDITORIAL_ANALYTICS_BOUNDARY.md` | Brad Stevens | ✅ Done |
| `governance/templates/TASK_PRD_TEMPLATE.md` | Tom Brady | ✅ Exists |
| `governance/templates/DOMAIN_SANITY_CHECKLIST.md` | Andy Flower | ✅ Done |
| `data/PROVENANCE.md` | Brock Purdy | ✅ Done |
| `analysis/baselines_vs_tags.md` | Stephen Curry + Andy Flower | ❌ To Do |
| `outputs/matchups/README.md` | Stephen Curry | ❌ To Do |
| `outputs/tags/README.md` | Andy Flower | ❌ To Do |
| `outputs/metrics/README.md` | Stephen Curry | ❌ To Do |
| `outputs/team/README.md` | Stephen Curry | ❌ To Do |
| `outputs/run-logs/README.md` | Brock Purdy | ❌ To Do |
| `ml_ops/PRODUCT_DESCRIPTION.md` | Ime Udoka | ❌ To Do |
| `notebooks/USER_GUIDE.md` | Stephen Curry | ❌ To Do |
| `.github/workflows/README.md` | Brad Stevens | ❌ To Do |

### New Features

| Feature | Description | Owner | Status |
|---------|-------------|-------|--------|
| **Multi-Metric Phase Tags** | 4-metric framework per phase | Stephen Curry + Andy Flower | ✅ Done |
| **Predicted XI** | Algorithm-based best XI | Stephen Curry + Pep Guardiola | ❌ To Do |
| **Depth Charts** | Position-by-position rankings | Stephen Curry + Andy Flower | ❌ To Do |
| **Baselines vs Tags** | Delta comparison | Andy Flower + Stephen Curry | ❌ To Do |

---

## Success Criteria

| Criteria | Measurement | Status |
|----------|-------------|--------|
| Governance | Task Integrity Loop documented and operational | ✅ Documented, ✅ Operational criteria complete |
| Product Vision | PRD and positioning docs complete | ✅ Complete |
| Data Quality | All 231 players in matchup files | 🔄 98.3% |
| Tag Consistency | Single nomenclature across all files | ✅ Done |
| Stat Packs | Predicted XI and Depth Charts for all 10 teams | ❌ Pending |
| Documentation | All READMEs complete with purpose | 🔄 Partial |
| Testing | Schema validation tests passing | 🔄 Partial |

---

## Agent Assignments

### Governance Team
| Agent | Primary Tasks | Status |
|-------|---------------|--------|
| **Tom Brady** | Constitution, HOW_IT_WORKS, PRD, sprint enforcement | 🔄 Active |
| **Brad Stevens** | Agents, governance folder, performance review, workflows | 🔄 Active |
| **Florentino Perez** | Task Integrity Loop, Gate criteria, value gating | ❌ Criteria pending |
| **N'Golo Kanté** | Testing, schema contracts, system checks | 🔄 Active |

### Domain Team
| Agent | Primary Tasks | Status |
|-------|---------------|--------|
| **Andy Flower** | Tag standardization, baselines, tactical insights, cricket truth | 🔄 Active |
| **Jose Mourinho** | Ecosystem analysis, robustness review, criteria definition | ❌ Criteria pending |
| **Pep Guardiola** | Predicted XI optimization, system coherence | ❌ Pending |

### Editorial Team
| Agent | Primary Tasks | Status |
|-------|---------------|--------|
| **Virat Kohli** | Stat pack editorial, presentation, product positioning | 🔄 Active |
| **Kevin de Bruyne** | Visualizations, ML Ops diagrams | ❌ Pending |
| **LeBron James** | Reader experience, cross-team coordination | ❌ Not assigned |

### Analytical Team
| Agent | Primary Tasks | Status |
|-------|---------------|--------|
| **Stephen Curry** | Data fixes, Predicted XI, Depth Charts, matchups | 🔄 Active |
| **Brock Purdy** | PROVENANCE, archive, manifest automation, data quality | 🔄 Active |
| **Ime Udoka** | ML Ops documentation, PCA validation | ❌ Pending |

---

## Risk Register

| Risk | Mitigation | Owner | Status |
|------|------------|-------|--------|
| Governance criteria not defined | Complete Phase 0 first | Tom Brady | ✅ Resolved |
| Tag standardization conflicts | Andy Flower final arbiter | Andy Flower | ✅ Resolved |
| Predicted XI algorithm complexity | Start simple, iterate | Stephen Curry | ❌ Not started |
| Data completeness issues | Audit before fixes | Stephen Curry | ✅ 98.3% done |
| Editorial/Analytical mixing | Enforce Constitution team separation | Tom Brady | ⚠️ Active |

---

## Dependencies

```
Phase 0 (Governance Criteria) - NEW
    ↓
Phase 1 (Governance Setup) ✅ COMPLETE
    ↓
Phase 2-3 can proceed in parallel
    ↓
Phase 4 (requires Phase 2-3 + Graduation)
    ↓
Phase 5-6-7 can proceed in parallel
    ↓
Stat Pack regeneration (after Phase 4)
```

---

## Post-Sprint: Future Scope (Sprint 5.0+)

| Item | Source | Priority |
|------|--------|----------|
| Match Phase Index (historical) | Review 5 | P1 |
| Clutch Performance Measurement | Review 5 | P1 |
| Toss Advantage Index | Review 5 | P1 |
| Novel Composite Metrics | Review 5 | P2 |
| DuckDB scalability | Mega Review | P2 |
| CI/CD artifact comparison | Mega Review | P2 |
| KenPom pre-season model | Review 5 | P2 |
| Insight Confidence Framework | Mega Review | P1 |
| Silhouette score validation | Mega Review | P1 |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-31 | Initial sprint plan |
| 2.0 | 2026-02-01 | Added Phase 0, governance compliance, missing items from action plans, status tracking, DoD per phase, LeBron James tasks, fixed agent assignments |
| 2.1 | 2026-02-01 | Completed Phase 0: PRD v3.0.0, Product Positioning, Editorial/Analytics Boundary, Domain Sanity Checklist. Verified existing templates (Task PRD, Gate criteria) |

---

*Cricket Playbook Sprint 4.0 v2.0*
*Tom Brady, Product Owner*
*2026-02-01*
