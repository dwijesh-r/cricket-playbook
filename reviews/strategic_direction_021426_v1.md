# Cricket Playbook -- Strategic Direction Rundown

**From:** Florentino Perez, Program Director
**Date:** 2026-02-14
**Document:** strategic_direction_021426_v1.md
**Status:** FORMAL STRATEGIC ASSESSMENT
**TKT:** TKT-234

---

## Executive Summary

Cricket Playbook has completed Sprint 4.0 at approximately 90% ticket closure (171/190), delivering a production-grade analytics platform with 43+ views, 10 team stat packs, depth charts, predicted XIs, an interactive Research Desk with DuckDB-WASM, player profiles, and a tournament quality weighting system -- all governed by a mature Task Integrity Loop and a system health score of 92/100. Sprint 5 proposes three ambitious workstreams (Win Probability ML, React Dashboard, Player Comparison Tool) totaling 15 tickets across 3 epics with a 500K token budget. **My assessment: Sprint 5 is over-scoped by approximately 40%. The React Dashboard migration must be phased across 2 sprints, and the Win Probability model requires careful alignment with our "no predictions" constitutional principle. We must protect what we have built.**

---

## 1. Current State Assessment -- Where We Are

### 1.1 Sprint 4 Achievements

Sprint 4.0 "Foundation & Editorial Excellence" ran January 31 through February 14, 2026. The numbers speak for themselves:

| Metric | Value |
|--------|-------|
| Tickets Closed | 171 / 190 (90%) |
| Epics Completed | 15 / 17 (EPIC-005 at 92%, EPIC-007 at 83%) |
| System Health Score | 92 / 100 (target was 85) |
| Token Budget | 125K / 500K used (25%) |
| Planned Points | 83 |
| Completed Points | 58 (70% of planned -- velocity gap noted) |

**Major Deliverables:**
- Constitution v2.2.0 -- binding governance document with full authority hierarchy
- Task Integrity Loop -- 8-step mandatory process, enforced across all work
- Mission Control -- full Kanban/ticket system with EPIC-Parent-Child hierarchy
- 10 team stat packs with 13 sections each (magazine style)
- Depth charts for all 10 IPL teams (33 output files)
- Predicted XIIs with captain, overseas, impact player logic
- The Lab dashboard with DuckDB-WASM (deployed on GitHub Pages)
- The Research Desk -- interactive SQL Lab with 55+ NL templates, 150+ player aliases
- Player Profile modal system (EPIC-017, fully delivered)
- Tournament Quality Weighting System (5-factor composite, EPIC-016)
- CricPom prototype spec (Jose Mourinho, 231 players weighted feed)
- 6 GitHub Actions workflows for CI/CD automation (82% coverage)
- Great Expectations data validation pipeline
- AI coding benchmark compliance: Anthropic 97%, Microsoft 90%, Google 82%

### 1.2 System Maturity

The foundation is genuinely strong. I want to be clear about this because the temptation in Sprint 5 will be to start building shiny new things on top of a foundation that still has open items.

**What is solid:**
- Data pipeline: Cricsheet -> DuckDB (9,357 matches, 2.1M+ ball-by-ball records)
- Analytics layer: 143 DuckDB views covering career, phase, matchup, venue, opposition, squad
- Governance: Constitution, Task Integrity Loop, quality gates, agent boundaries
- Testing: System health 92/100, comprehensive validation
- CI/CD: Gate-check -> generate-outputs -> deploy-dashboard chain

**What remains incomplete from Sprint 4:**
- EPIC-005 (Output Quality & Completeness) at 92% -- not closed
- EPIC-007 (ML Ops & Documentation) at 83% -- not closed
- 19 tickets still open (190 - 171 = 19)
- Velocity gap: 58 completed points vs 83 planned (30% shortfall)
- Automation coverage at 82% vs 90% target
- Model registry still missing (known gap per CLAUDE.md)
- No token accounting per task

### 1.3 Product Readiness

The stat packs are presentable. The Lab is functional. The Research Desk is a genuine differentiator. But we are not yet at "paid artifact" quality. The Sprint 4 Check-In identified P0 data integrity issues (Digvesh Rathi misclassification, captain identification errors, overseas count issues) that, if they persisted into a paid product, would destroy credibility. I must assume the majority of P0 items have been resolved given 90% closure, but this must be verified before any external distribution.

---

## 2. Sprint 5 Analysis -- Where We Are Going

### 2.1 Proposed Scope

Sprint 5 "Interactive Intelligence & ML" runs February 15-28, 2026. Three epics:

| Epic | Tickets | Sizes | Owner | Target |
|------|---------|-------|-------|--------|
| EPIC-018: Win Probability Model | 5 (TKT-205 to 209) | M+L+L+M+S | Ime Udoka | Feb 28 |
| EPIC-019: React Dashboard (Lab v2) | 6 (TKT-210 to 215) | M+L+L+XL+XL+M | Kevin de Bruyne | Mar 15 |
| EPIC-020: Player Comparison Tool | 4 (TKT-216 to 219) | M+L+M+S | Kevin de Bruyne / Stephen Curry | Feb 28 |

**Total: 15 tickets. Size distribution: 2 XL, 3 L, 5 M, 2 S, 3 unweighted.**

### 2.2 Critical Dependency Chain

The dependency structure is deeply sequential, which is the single biggest risk:

```
EPIC-018 (Win Prob):
TKT-205 (arch) -> TKT-206 (features) -> TKT-207 (train) -> TKT-208 (dashboard) + TKT-209 (monitoring)

EPIC-019 (React):
TKT-210 (setup) -> TKT-211 (design) + TKT-212 (data layer) -> TKT-213 (team pages, XL) + TKT-214 (research desk, XL) -> TKT-215 (testing)

EPIC-020 (Comparison):
TKT-216 (data pipeline) -> TKT-217 (UI) -> TKT-218 (multi-player) + TKT-219 (share links)
```

Any delay in TKT-205, TKT-210, or TKT-216 cascades through their entire epic. TKT-213 and TKT-214 are both XL and both depend on TKT-211 and TKT-212. This is a chokepoint.

### 2.3 Scope Concerns

**EPIC-019 is too large for one sprint.** Six tickets including two XLs (TKT-213: migrate all team pages, TKT-214: migrate Research Desk). The existing static HTML Lab works. The React migration is an improvement, not a crisis. EPIC-019 itself acknowledges this with a target date of March 15, which extends beyond Sprint 5. This is already a signal that the scope does not fit.

**EPIC-018 presents a constitutional tension.** The Constitution explicitly forbids "predictions, win probabilities, odds, points-table forecasts" in Section 8.3 (Forbidden Content). A Win Probability model, by definition, produces predictions. This must be carefully positioned as a *historical replay tool* ("What was the win probability at ball X in past matches?") rather than a forward-looking prediction engine. If it becomes "who will win tonight," we violate our own founding document.

**Kevin de Bruyne is overloaded.** He owns EPIC-019 (6 tickets) and EPIC-020 (3 tickets) -- 9 of 15 Sprint 5 tickets. That is 60% of the sprint load on one agent. Even with parallel work, this is unsustainable and creates a single point of failure.

### 2.4 Florentino Gate Assessment for Sprint 5 Epics

| Epic | Gate Decision | Rationale |
|------|---------------|-----------|
| EPIC-018: Win Prob | APPROVED WITH CONDITIONS | Historical replay only. Must never surface as forward prediction. Label "EXPERIMENTAL" per Section 7.3. Jose Mourinho must validate Brier score target. |
| EPIC-019: React Dashboard | PHASE 1 ONLY (TKT-210, 211, 212, 215) | Setup, design system, data layer, testing. Defer TKT-213 (XL) and TKT-214 (XL) to Sprint 6. Static HTML fallback is adequate. |
| EPIC-020: Player Comparison | APPROVED | Directly improves paid artifact. Head-to-head comparison is high editorial value. Radar charts are magazine-worthy. |

---

## 3. Product Vision Alignment

### 3.1 USP Integrity Check

Our USP: "Pro team internal prep packaged for public consumption."

| Sprint 5 Feature | USP Alignment | Rating |
|-------------------|---------------|--------|
| Win Probability Model | Neutral to Risky. Pro teams do not show fans win probability curves. This is a broadcasting/analytics tool, not a scouting tool. | 5/10 |
| React Dashboard | Neutral. Better UX does not change content quality. The magazine is the product, not the framework. | 6/10 |
| Player Comparison | Strong. Comparing players side-by-side is exactly what a scouting department does. Radar charts, phase breakdowns, matchup matrices -- this is the core product. | 9/10 |

**Verdict:** Sprint 5 is drifting toward "analytics showcase" territory. The Founder's mandate was explicit: *"Cricket fans don't pay for analytics, they pay for confidence, narrative clarity and authority."* A React rewrite and a win probability model are engineering ambitions, not editorial improvements. The Player Comparison tool is the only Sprint 5 feature that directly strengthens the paid artifact.

### 3.2 What Should Sprint 5 Actually Prioritize?

1. **Player Comparison Tool (EPIC-020)** -- ships to paid artifact immediately
2. **Stat Pack Editorial Pass** -- the 10 stat packs need narrative polish, not more data
3. **Win Probability as historical replay** -- research value, marked EXPERIMENTAL
4. **React foundation only** -- setup, design system, data layer; no full migration yet
5. **Close Sprint 4 remainders** -- EPIC-005 (92%), EPIC-007 (83%), model registry gap

---

## 4. Risk Assessment

### 4.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| React migration breaks existing Lab | HIGH | HIGH | Keep static HTML as parallel fallback. Never delete old code until React reaches parity. |
| Win Prob model overfits on 1,169 IPL matches | MEDIUM | HIGH | Temporal cross-validation mandatory. Use broader T20 dataset (9,357 matches) for training. |
| DuckDB-WASM performance degrades with React overhead | MEDIUM | MEDIUM | Benchmark before and after. Connection pooling in TKT-212. |
| Kevin de Bruyne burnout / bottleneck | HIGH | HIGH | Reduce his ticket load from 9 to 5-6. Reassign TKT-213 and TKT-214 to Sprint 6. |
| Sprint 4 incomplete items compound | MEDIUM | MEDIUM | Close EPIC-005 and EPIC-007 before starting new work. |

### 4.2 Scope Creep Risks

| Risk | Source | Mitigation |
|------|--------|------------|
| Win Prob becomes a "live prediction" feature | Natural temptation once model exists | Constitutional enforcement. Florentino veto if any ticket moves toward live prediction. |
| React migration grows to include Mission Control, Boardroom | Adjacent pages will want React too | Strict scope: only Team pages and Research Desk in Sprint 5-6. |
| Comparison tool expands to bowling comparisons, fielding, fantasy | Feature creep on popular tool | Cap at batting + bowling radar charts. No fielding. No fantasy integration. |

### 4.3 Timeline Risk

Sprint 5 ends February 28. IPL 2026 presumably starts in late March. That gives us approximately 3-4 weeks post-Sprint 5 to finalize the paid artifact. **We cannot afford a Sprint 5 that runs over.** Every day of overrun is a day not spent on editorial polish. The React migration's March 15 target date (2 weeks past Sprint 5 end) is already a red flag.

---

## 5. Resource & Budget Analysis

### 5.1 Agent Utilization Matrix

| Agent | Sprint 4 Load | Sprint 5 Load | Assessment |
|-------|---------------|---------------|------------|
| **Kevin de Bruyne** | High (Lab, Research Desk) | OVERLOADED (9 tickets) | Reduce to 5-6. Defer XL migrations. |
| **Ime Udoka** | Medium (ML Ops) | High (5 Win Prob tickets) | Appropriate if focused solely on EPIC-018. |
| **Stephen Curry** | Very High (analytics lead) | Medium (1 ticket: TKT-216) | Under-utilized. Assign editorial review work. |
| **Brad Stevens** | High (infrastructure) | Low (1 ticket: TKT-215) | Under-utilized. Could take React CI setup (TKT-210). |
| **Tom Brady** | Very High (governance, sprints) | Low (no assigned tickets) | Should own Sprint 4 closure + stat pack editorial pass. |
| **Jose Mourinho** | High (tournament weights, CricPom) | Reviewer only | Under-utilized. Should co-own Win Prob validation. |
| **Andy Flower** | Medium (domain validation) | Reviewer only (TKT-216) | Under-utilized. Should own editorial review of stat packs. |
| **Virat Kohli** | Medium (narrative) | No tickets | WASTED. The narrative lead has zero Sprint 5 work. This is wrong. |
| **Brock Purdy** | Medium (data pipeline) | No tickets | Under-utilized. Assign data pipeline for comparison tool. |
| **N'Golo Kante** | Medium (QA) | Reviewer only (TKT-209, 215) | Appropriate but should formally close Sprint 4 QA. |
| **LeBron James** | Low | Reviewer only (TKT-219) | Under-utilized. Social atomization has no Sprint 5 plan. |
| **Pep Guardiola** | Medium (retrospectives) | No tickets | Should run Sprint 4 retrospective. |
| **Jayson Tatum** | Medium (UX) | Reviewer only (4 tickets) | Appropriate. |
| **Florentino Perez** | Low (gate approvals) | This document | Appropriate. |

### 5.2 Key Observation: Editorial Team is Idle in Sprint 5

Virat Kohli (Editorial Lead), Andy Flower (Cricket Expert), and LeBron James (Social Atomization) have **zero assigned tickets** in Sprint 5. This is the clearest signal that Sprint 5 has tilted too far toward engineering and away from the paid artifact. The editorial team should be spending Sprint 5 doing a comprehensive editorial pass on all 10 stat packs, writing tactical insights, and preparing social-ready content extracts.

### 5.3 Token Budget

Sprint 5 has 500K tokens. Sprint 4 used only 125K of its 500K allocation (25%).

| Workstream | Estimated Token Cost | Rationale |
|------------|---------------------|-----------|
| Win Prob ML (EPIC-018) | 120K | Research, feature engineering, training iteration, validation |
| React Setup (EPIC-019 Phase 1) | 80K | Boilerplate, component library, DuckDB hooks |
| Player Comparison (EPIC-020) | 60K | SQL views + UI, well-scoped |
| Sprint 4 Closure | 40K | Close EPIC-005, EPIC-007 remainders |
| Editorial Pass (NEW) | 80K | Stat pack narrative review, Andy Flower + Virat Kohli |
| Sprint 4 Retrospective | 20K | Pep Guardiola |
| Buffer | 100K | Contingency |
| **Total** | **500K** | Fits if scope is controlled |

**Verdict:** 500K is sufficient *if* we reduce EPIC-019 to Phase 1 only. A full React migration (including TKT-213 and TKT-214 at XL) would burn 150-200K additional tokens and blow the budget.

---

## 6. Kill-Switch Recommendations

I am exercising my authority as Program Director. The following decisions are binding unless overridden by the Founder.

### 6.1 KILL: Full React Migration in Sprint 5

**TKT-213 (Team Pages Migration, XL) and TKT-214 (Research Desk Migration, XL) are deferred to Sprint 6.**

Rationale: The existing static HTML Lab works. It is deployed, functional, and users can access it today. A full React rewrite mid-sprint, 4-6 weeks before IPL 2026, is an unacceptable risk. We are not a SaaS startup; we are producing a magazine. The framework does not matter to the reader.

EPIC-019 Sprint 5 scope is reduced to: TKT-210 (setup), TKT-211 (design system), TKT-212 (data layer), TKT-215 (testing). This gives us the React foundation without the migration risk.

### 6.2 CONDITION: Win Probability Model

**EPIC-018 is approved as EXPERIMENTAL / ANALYTICS ONLY.**

It must never appear in the paid stat packs. It lives in The Lab as a historical replay tool only. Constitution Section 8.3 explicitly forbids predictions. The model card (TKT-205) must include a "Limitations and Forbidden Use Cases" section that cites the constitutional prohibition. If any ticket in EPIC-018 attempts to surface win probability as a forward-looking prediction, I will kill the entire epic.

### 6.3 DEPRIORITIZE: TKT-219 (Shareable Links + PNG Export)

**Deferred to Sprint 6 or later.**

Shareable links and PNG export for the comparison tool is a nice-to-have. The comparison tool itself (TKT-216, 217, 218) is the value. Social sharing features can wait until the tool is validated.

### 6.4 ADD: Stat Pack Editorial Pass

**New work for Sprint 5: Virat Kohli + Andy Flower conduct editorial review of all 10 stat packs.**

The stat packs were generated algorithmically. They need human editorial judgment: narrative framing, tactical insights that only Andy Flower can provide, tone adjustments from Virat Kohli. This is the single highest-value work we can do before IPL 2026. It directly improves the paid artifact.

### 6.5 ADD: Sprint 4 Retrospective

**Pep Guardiola runs a formal Sprint 4 retrospective before Sprint 5 begins.**

We completed 90% of tickets but only 70% of story points. That gap needs to be understood. Were tickets over-scoped? Were estimates wrong? Were there blockers we did not anticipate? We cannot plan Sprint 5 intelligently without understanding Sprint 4's velocity reality.

---

## 7. Long-Term Roadmap Vision -- 3-Sprint Horizon

### Sprint 5 (Feb 15-28): "Selective Intelligence"
**Theme:** Ship what matters most, build foundations for what comes next.

| Priority | Work | Owner |
|----------|------|-------|
| P0 | Close Sprint 4 remainders (EPIC-005, EPIC-007) | Stephen Curry, Ime Udoka |
| P0 | Player Comparison Tool (EPIC-020, TKT-216/217/218) | Stephen Curry, Kevin de Bruyne |
| P0 | Stat Pack Editorial Pass (10 teams) | Virat Kohli, Andy Flower |
| P1 | Win Probability Model - research + train (TKT-205/206/207) | Ime Udoka |
| P1 | React Foundation (TKT-210/211/212/215) | Kevin de Bruyne, Brad Stevens |
| P2 | Sprint 4 Retrospective | Pep Guardiola |

### Sprint 6 (Mar 1-14): "Editorial Excellence"
**Theme:** Finalize the paid artifact for IPL 2026 launch.

| Priority | Work | Owner |
|----------|------|-------|
| P0 | React Team Pages migration (TKT-213) | Kevin de Bruyne |
| P0 | Final stat pack production (all 10 teams, editorial-approved) | Virat Kohli |
| P0 | Win Prob dashboard integration (TKT-208, if model passes validation) | Kevin de Bruyne |
| P1 | React Research Desk migration (TKT-214) | Kevin de Bruyne |
| P1 | Social atomization content (LeBron James) | LeBron James |
| P1 | Win Prob monitoring (TKT-209) | Ime Udoka |
| P2 | Shareable comparison links (TKT-219) | Kevin de Bruyne |

### Sprint 7 (Mar 15-28): "Launch Hardening"
**Theme:** IPL 2026 starts. Polish, distribute, monitor.

| Priority | Work | Owner |
|----------|------|-------|
| P0 | Final QA pass on all paid artifacts | N'Golo Kante |
| P0 | Distribution packaging (PDF, web, social) | Tom Brady, LeBron James |
| P0 | CricPom integration into Lab (if Founder approves) | Jose Mourinho |
| P1 | React parity verification (Lab v2 replaces Lab v1) | Brad Stevens |
| P1 | Post-launch monitoring and feedback loop | Pep Guardiola |
| P2 | IPL 2026 in-tournament match replay (win prob curves) | Ime Udoka |

---

## 8. Strategic Priorities for Next 30 Days

In order of non-negotiable importance:

1. **Close Sprint 4 completely.** The 19 remaining tickets and 2 incomplete epics must be resolved before any Sprint 5 work begins. Do not carry debt forward.

2. **Editorial pass on all 10 stat packs.** This is the paid artifact. It must be excellent. Virat Kohli and Andy Flower must review every section of every team. Strong opinions, narrative clarity, authority -- per the Founder's mandate.

3. **Ship the Player Comparison Tool.** This is the highest-value new feature. Radar charts, phase breakdowns, head-to-head analytics. This is what makes Cricket Playbook different from Cricinfo.

4. **Lay React foundation without migrating.** Setup, design system, data layer, tests. Do not touch the existing Lab. The migration happens in Sprint 6 when the foundation is solid.

5. **Win Probability as research only.** Build it, validate it, document it. Do not surface it in paid content. If the model is good, it becomes a Lab feature in Sprint 6. If it is not good, we kill it without having wasted editorial credibility.

6. **Run the Sprint 4 retrospective.** Understand the velocity gap. Recalibrate estimates for Sprint 5+.

7. **Begin social content planning.** LeBron James should be developing the social atomization strategy now. IPL 2026 is weeks away. We need shareable content fragments ready.

8. **Model registry.** The ML Rigor category is at 80% (lowest score in system health). The model registry has been a known gap since CLAUDE.md was written. Sprint 5 must close this.

---

## 9. Closing Directive

I am directing Tom Brady to revise the Sprint 5 plan according to the kill-switch decisions in Section 6. Specifically:

- Remove TKT-213 and TKT-214 from Sprint 5 (defer to Sprint 6)
- Remove TKT-219 from Sprint 5 (defer to Sprint 6+)
- Add stat pack editorial pass tickets for Virat Kohli and Andy Flower
- Add Sprint 4 retrospective ticket for Pep Guardiola
- Add model registry ticket for Ime Udoka
- Ensure EPIC-005 and EPIC-007 closure tickets are in Sprint 5

The revised Sprint 5 should contain approximately 14-16 tickets with a balanced load across agents, not 60% on Kevin de Bruyne.

Cricket Playbook is in a strong position. The foundation is real. The data is comprehensive. The governance is mature. The risk is not that we fail -- the risk is that we chase engineering ambition instead of editorial excellence. We are building a magazine, not a web application. The React framework, the ML model, the interactive tools -- they are delivery mechanisms. The product is the editorial insight. Never forget that.

---

*Florentino Perez*
*Program Director*
*Cricket Playbook*

---

**Document Version:** strategic_direction_021426_v1.md
**Classification:** STRATEGIC -- Program Director Assessment
**Distribution:** Founder, Tom Brady, Brad Stevens, all functional leads
**Next Review:** Sprint 5 mid-point (Feb 21, 2026)
