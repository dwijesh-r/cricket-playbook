# Sprint 5.0 Kickoff Plan (v2 -- Post-Florentino Review)

**Document:** sprint_5_kickoff_plan_021426_v2.md
**Date:** February 14, 2026
**Author:** Tom Brady (PO & Editor-in-Chief)
**Sprint:** SPRINT-002 -- Interactive Intelligence & Rankings
**Duration:** Feb 15 - Feb 28, 2026 (2 weeks)
**Token Budget:** 500K tokens (Founder-approved)
**Supersedes:** sprint_5_kickoff_plan_021426_v1.md

---

## 0. What Changed from v1

### Florentino Gate Decisions (Binding)

| Decision | Ticket(s) | Rationale |
|----------|-----------|-----------|
| **KILLED** | TKT-213 (Team Pages Migration) | Defer to Sprint 6. Non-critical for Sprint 5 goals. |
| **KILLED** | TKT-214 (Research Desk Migration) | Defer to Sprint 6. Non-critical for Sprint 5 goals. |
| **DEFERRED** | TKT-219 (Shareable Links + PNG Export) | Defer to Sprint 6+. Nice-to-have, not core. |
| **CONDITIONED** | EPIC-018 (Win Probability) | Experimental/analytics only. Historical replay tool. Never forward prediction. |

**Root Cause:** v1 was ~40% over-scoped. Kevin de Bruyne was assigned 9 of 15 tickets -- an unsustainable bottleneck. Florentino's cuts remove 3 KdB tickets (TKT-213, 214, 219) from Sprint 5.

### Founder Additions

| Addition | Description |
|----------|-------------|
| **EPIC-021** | Player Rankings System (Lindy's Style) -- Signature feature. New Rankings tab in The Lab. |
| **EPIC-022** | Sprint 4 Close-Out & Editorial Polish -- P0 bug fixes and quality pass. |
| **EPIC-023** | Infrastructure & Pipeline Hardening -- CI/CD fixes, model registry, data freshness. |
| **EPIC-024** | UI/UX & Accessibility Improvements -- Font sizes, mobile nav, WCAG 2.1 AA basics. |

### Net Result

| Metric | v1 | v2 |
|--------|----|----|
| EPICs | 3 | 7 (3 original + 4 new) |
| Active tickets | 15 | 31 (12 original active + 19 new) |
| Killed/deferred | 0 | 3 (TKT-213, 214, 219) |
| KdB ticket count | 9 | 7 (net reduction of 2) |

---

## 1. Sprint Goals

Sprint 5.0 has two pillars: (1) advance Cricket Playbook toward an interactive intelligence platform, and (2) establish the Player Rankings System as the sprint's signature editorial feature.

### Pillar 1: Interactive Intelligence (EPICs 018, 019, 020)
Build the win probability historical replay tool, lay React dashboard foundations, and deliver the player comparison tool. All under Florentino's conditions: win probability is experimental/analytics only, never forward prediction.

### Pillar 2: Player Rankings (EPIC-021) -- Signature Feature
Build a comprehensive Lindy's-style player ranking system as a new Rankings tab in The Lab. Seven ranking categories covering phase-wise performance, matchup dominance, and overall composite rankings. This is the feature that transforms Cricket Playbook from "analytics dashboard" to "authoritative reference."

### Supporting Workstreams
- **EPIC-022:** Close out Sprint 4 editorial debt (stat pack quality, SUPER SELECTOR fixes, data integrity).
- **EPIC-023:** Harden the pipeline (fix ingestion, fresh data, model registry, automation).
- **EPIC-024:** UI/UX polish and accessibility foundations.

---

## 2. Epic Breakdown with Tickets

### EPIC-018: Win Probability Model (5 tickets, Owner: Jose Mourinho)

> **FLORENTINO CONDITION:** Experimental/analytics only. Historical replay tool. Never forward prediction. All marketing/display must label as "Historical Win Probability Replay." No live match inference.

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-205 | Research & define win probability model architecture | P0 | Jose Mourinho | Deep Work | BACKLOG |
| TKT-206 | Feature engineering from fact_ball data | P0 | Stephen Curry | Deep Work | BACKLOG |
| TKT-207 | Train & validate win probability model | P0 | Ime Udoka | Marathon | BACKLOG |
| TKT-208 | Integrate win probability into The Lab dashboard | P1 | Kevin de Bruyne | Deep Work | BACKLOG |
| TKT-209 | Model monitoring & drift detection setup | P1 | Ime Udoka | Hustle | BACKLOG |

**Critical Path:** TKT-205 -> TKT-206 -> TKT-207 -> TKT-208 (sequential dependency)
**Parallel Track:** TKT-209 can start after TKT-207

---

### EPIC-019: Interactive React Dashboard (4 active tickets, Owner: Kevin de Bruyne)

> **2 tickets KILLED by Florentino:** TKT-213 and TKT-214 deferred to Sprint 6 (SPRINT-003).

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-210 | React project setup + build pipeline | P0 | Brad Stevens | Deep Work | BACKLOG |
| TKT-211 | Design system -- component library + theme tokens | P0 | Kevin de Bruyne | Deep Work | BACKLOG |
| TKT-212 | Data layer -- DuckDB-WASM integration + React hooks | P0 | Brad Stevens | Marathon | BACKLOG |
| ~~TKT-213~~ | ~~Team pages migration~~ | ~~P1~~ | ~~Kevin de Bruyne~~ | ~~Marathon~~ | **DEFERRED** |
| ~~TKT-214~~ | ~~Research Desk migration~~ | ~~P1~~ | ~~Kevin de Bruyne~~ | ~~Deep Work~~ | **DEFERRED** |
| TKT-215 | Testing + CI integration for React dashboard | P1 | Brad Stevens | Hustle | BACKLOG |

**Critical Path (revised):** TKT-210 -> TKT-211 + TKT-212 (parallel) -> TKT-215
**Note:** Migration tickets deferred. Sprint 5 scope is foundation only: setup, design system, data layer, testing.

---

### EPIC-020: Player Comparison Tool (3 active tickets, Owner: Stephen Curry)

> **1 ticket DEFERRED by Florentino:** TKT-219 deferred to Sprint 6+.

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-216 | Head-to-head comparison data pipeline | P0 | Stephen Curry | Deep Work | BACKLOG |
| TKT-217 | Comparison UI -- radar charts + side-by-side stats | P0 | Kevin de Bruyne | Deep Work | BACKLOG |
| TKT-218 | Multi-player comparison (3+ players) | P1 | Stephen Curry | Hustle | BACKLOG |
| ~~TKT-219~~ | ~~Shareable comparison links + PNG export~~ | ~~P2~~ | ~~Kevin de Bruyne~~ | ~~Hustle~~ | **DEFERRED** |

**Critical Path (revised):** TKT-216 -> TKT-217 -> TKT-218 (sequential)

---

### EPIC-021: Player Rankings System -- Lindy's Style (5 tickets, Owner: Stephen Curry) -- NEW, SIGNATURE

This is the sprint's marquee feature. A comprehensive player ranking system displayed as a new "Rankings" tab in The Lab. Inspired by Lindy's Sports Annual rankings.

**Rankings to build (all since 2023 IPL unless stated):**

1. **Phase-wise Batter Rankings** -- Rank batters in each phase (powerplay, middle, death) by composite score using SR, average, boundary%, dot%. Separate leaderboards per phase.
2. **Phase-wise Bowler Rankings** -- Rank bowlers in each phase (powerplay, middle, death) by composite score using economy, SR, dot%, wickets. Separate leaderboards per phase.
3. **Batter vs Bowling Type Rankings** -- Rank batters by performance against each bowling type (pace, off-spin, leg-spin, left-arm orthodox, left-arm wrist spin).
4. **Bowler vs LHB/RHB Rankings** -- Rank bowlers by performance against left-hand and right-hand batters separately. Also include all-time IPL version.
5. **Best Player-vs-Player Matchups** -- All-time IPL head-to-head rankings from both batting and bowling perspective. Uses existing `analytics_ipl_player_matchup_matrix` view.
6. **Overall Batter Rankings** -- Composite ranking using career stats, phase performance, consistency, and match impact. Since 2023.
7. **Overall Bowler Rankings** -- Composite ranking using career stats, phase performance, economy, strike rate. Since 2023.

**Existing infrastructure to leverage:**
- `analytics_ipl_batting_percentiles` / `analytics_ipl_bowling_percentiles`
- `analytics_ipl_batter_phase_percentiles` / `analytics_ipl_bowler_phase_percentiles`
- `analytics_ipl_batter_vs_bowler_type` / `analytics_ipl_batter_vs_bowler_type_phase`
- `analytics_ipl_bowler_vs_batter_handedness`
- `analytics_ipl_player_matchup_matrix`
- All dual-scope views (`_alltime` and `_since2023`)
- Thresholds from `config/thresholds.yaml`

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-235 | Create ranking composite views in analytics_ipl.py | P0 | Stephen Curry | Marathon | BACKLOG |
| TKT-236 | Build ranking generator script -- generate_rankings.py | P0 | Stephen Curry | Deep Work | BACKLOG |
| TKT-237 | Build Rankings tab UI in The Lab dashboard | P0 | Kevin de Bruyne | Deep Work | BACKLOG |
| TKT-238 | Domain validation of rankings | P1 | Andy Flower | Hustle | BACKLOG |
| TKT-239 | QA validation of ranking data integrity | P1 | N'Golo Kante | Hustle | BACKLOG |

**Critical Path:** TKT-235 -> TKT-236 -> TKT-237 (sequential)
**Parallel Validation:** TKT-238 + TKT-239 can start once TKT-236 produces output

---

### EPIC-022: Sprint 4 Close-Out & Editorial Polish (5 tickets, Owner: Tom Brady) -- NEW

Consolidates all review-driven P0 bug fixes and editorial improvements from the Sprint 4 review cycle.

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-240 | Stat Pack Editorial Pass -- review all 10 stat packs | P0 | Virat Kohli | Marathon | BACKLOG |
| TKT-241 | Fix PRD section numbering, player/view/agent counts | P1 | Virat Kohli | Deep Work | BACKLOG |
| TKT-242 | Fix SUPER SELECTOR positional diversity constraints | P0 | Stephen Curry | Deep Work | BACKLOG |
| TKT-243 | Fix MI and RR salary cap overruns | P1 | Stephen Curry | Hustle | BACKLOG |
| TKT-244 | Fix 9 predicted XII players missing from depth charts | P1 | Stephen Curry | Deep Work | BACKLOG |

**Critical Path:** TKT-242 and TKT-244 should complete before TKT-240 (stat packs depend on correct data)
**Parallel:** TKT-241 and TKT-243 are independent

---

### EPIC-023: Infrastructure & Pipeline Hardening (5 tickets, Owner: Brad Stevens) -- NEW

CI/CD fixes, model registry, and pipeline improvements to close known system health gaps.

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-245 | Fix ingest.yml script path and download URL format mismatch | P0 | Brock Purdy | Hustle | BACKLOG |
| TKT-246 | Run fresh data ingestion -- data 30 days stale | P0 | Brock Purdy | Deep Work | BACKLOG |
| TKT-247 | Implement lightweight model registry | P1 | Ime Udoka | Deep Work | BACKLOG |
| TKT-248 | Add Lab data generators to generate-outputs.yml | P1 | Brad Stevens | Hustle | BACKLOG |
| TKT-249 | Add data freshness indicator to The Lab | P2 | Kevin de Bruyne | Hustle | BACKLOG |

**Critical Path:** TKT-245 -> TKT-246 (must fix ingest before running it)
**Parallel:** TKT-247 and TKT-248 are independent

---

### EPIC-024: UI/UX & Accessibility Improvements (4 tickets, Owner: Kevin de Bruyne) -- NEW

UI/UX polish and accessibility foundations.

| Ticket | Title | Priority | Assignee | Effort | Status |
|--------|-------|----------|----------|--------|--------|
| TKT-250 | Fix min font sizes, Film Room mobile overlap, smooth scroll | P1 | Kevin de Bruyne | Deep Work | BACKLOG |
| TKT-251 | Add Mission Control nav link + standardize mobile nav | P0 | Kevin de Bruyne | Hustle | BACKLOG |
| TKT-252 | Remove stale Ctrl+Space hint, fix typewriter delay, dead CSS | P1 | Jayson Tatum | Hustle | BACKLOG |
| TKT-253 | Add WCAG 2.1 AA accessibility basics | P1 | Kevin de Bruyne | Deep Work | BACKLOG |

**Parallel:** All tickets are independent (TKT-252 owned by Jayson Tatum, not KdB)

---

## 3. Killed & Deferred Tickets Summary

| Ticket | Original Epic | Decision | Reason | Deferred To |
|--------|--------------|----------|--------|-------------|
| TKT-213 | EPIC-019 | **KILLED** | KdB bottleneck. Team pages migration non-critical. | SPRINT-003 |
| TKT-214 | EPIC-019 | **KILLED** | KdB bottleneck. Research Desk migration non-critical. | SPRINT-003 |
| TKT-219 | EPIC-020 | **DEFERRED** | Nice-to-have. Social/export can wait. | SPRINT-003 |

All three tickets have been updated in Mission Control with `state: "DEFERRED"`, `deferred_reason`, and `deferred_to: "SPRINT-003"`.

---

## 4. Agent Workload Analysis (Post-Florentino Mitigation)

### Kevin de Bruyne -- The Bottleneck (Mitigated)

| Metric | v1 | v2 | Change |
|--------|----|----|--------|
| Total tickets | 9 | 7 | -2 (killed TKT-213, 214, 219; added TKT-237, 249, 250, 251, 253) |
| P0 tickets | 4 | 4 | Same |
| Marathon tickets | 1 | 0 | -1 (TKT-213 killed) |
| Deep Work tickets | 4 | 4 | Same |
| Hustle tickets | 1 | 2 | +1 |

**v2 KdB tickets:** TKT-208, TKT-211, TKT-217, TKT-237, TKT-249, TKT-250, TKT-251, TKT-253
**Wait -- that is 8 tickets.** Let me recount: TKT-208 (EPIC-018), TKT-211 (EPIC-019), TKT-217 (EPIC-020), TKT-237 (EPIC-021), TKT-249 (EPIC-023), TKT-250, TKT-251, TKT-253 (EPIC-024) = **8 tickets**.

**Mitigation strategy:**
- TKT-249 (data freshness indicator) is P2 Hustle -- can slip to Sprint 6 if needed
- TKT-208 (win prob integration) is blocked until Week 2 at earliest
- TKT-237 (Rankings UI) is blocked until TKT-236 completes
- Week 1 focus: TKT-211 (design system) + TKT-251 (nav) + TKT-250 (font fixes)
- Week 2 focus: TKT-217 (comparison UI) + TKT-237 (rankings UI) + TKT-208 (win prob) + TKT-253 (a11y)

### Full Agent Allocation

| Agent | Tickets | Count | Risk Level |
|-------|---------|-------|------------|
| **Stephen Curry** | TKT-206, TKT-216, TKT-218, TKT-235, TKT-236, TKT-242, TKT-243, TKT-244 | 8 | **HIGH** -- heaviest analytical workload |
| **Kevin de Bruyne** | TKT-208, TKT-211, TKT-217, TKT-237, TKT-249, TKT-250, TKT-251, TKT-253 | 8 | **HIGH** -- front-end bottleneck (mitigated from 9) |
| **Ime Udoka** | TKT-207, TKT-209, TKT-247 | 3 | LOW |
| **Brad Stevens** | TKT-210, TKT-212, TKT-215, TKT-248 | 4 | MEDIUM |
| **Jose Mourinho** | TKT-205 | 1 | LOW |
| **Brock Purdy** | TKT-245, TKT-246 | 2 | LOW |
| **Virat Kohli** | TKT-240, TKT-241 | 2 | LOW |
| **Andy Flower** | TKT-238 | 1 | LOW |
| **N'Golo Kante** | TKT-239 | 1 | LOW |
| **Jayson Tatum** | TKT-252 | 1 | LOW |

**Key risk:** Stephen Curry now carries 8 tickets (analytics lead for rankings + comparison + close-out fixes). Mitigation: TKT-243 (salary cap) is Hustle, TKT-218 (multi-player) is Hustle, and several tickets are sequential (TKT-235 -> TKT-236).

---

## 5. Key Dependencies

### Cross-Epic Dependencies

- **EPIC-021 -> EPIC-019:** TKT-237 (Rankings UI) may leverage the design system (TKT-211) and React hooks (TKT-212) if React dashboard is ready; otherwise builds as a standalone Lab tab.
- **EPIC-018 -> EPIC-019:** TKT-208 (win prob dashboard integration) depends on at least TKT-210 (React setup) and TKT-211 (design system).
- **EPIC-023 -> EPIC-021:** TKT-248 (automation chain) should include generate_rankings.py from TKT-236.
- **EPIC-022 -> EPIC-021:** TKT-242 (SUPER SELECTOR fix) and TKT-244 (depth chart fix) affect data that rankings consume.
- **EPIC-023 -> all:** TKT-246 (fresh data ingestion) affects all downstream analytics. Should complete early in Week 1.

### Sequencing Constraints

```
Week 1 Critical Starts:
  TKT-245 -> TKT-246 (fix ingest, then run it)
  TKT-205 -> TKT-206 (research, then feature eng)
  TKT-210 (React setup -- unblocks all EPIC-019)
  TKT-235 (ranking views -- unblocks TKT-236, TKT-237)
  TKT-242, TKT-244 (data fixes -- unblock editorial pass)

Week 2 Dependent Work:
  TKT-207 (train model -- needs TKT-206)
  TKT-236 (ranking generator -- needs TKT-235)
  TKT-237 (rankings UI -- needs TKT-236)
  TKT-208 (win prob UI -- needs TKT-207)
  TKT-217 (comparison UI -- needs TKT-216)
```

---

## 6. Token Budget

| Allocation | Tokens | Notes |
|-----------|--------|-------|
| **Total Budget** | 500,000 | Founder-approved 2026-02-14 |
| EPIC-018 (Win Prob) | ~120,000 | Reduced from 180K; conditioned scope, no forward prediction |
| EPIC-019 (React) | ~80,000 | Reduced from 200K; 2 migration tickets killed |
| EPIC-020 (Comparison) | ~60,000 | Reduced from 80K; export ticket deferred |
| **EPIC-021 (Rankings)** | **~120,000** | **Signature feature. 7 ranking categories, composite views, generator, UI.** |
| EPIC-022 (Close-Out) | ~50,000 | Editorial pass + data fixes |
| EPIC-023 (Pipeline) | ~35,000 | Infrastructure and CI/CD |
| EPIC-024 (UI/UX) | ~20,000 | Polish and accessibility |
| Buffer | ~15,000 | For rework and unplanned scope |

---

## 7. Week-by-Week Plan

### Week 1 (Feb 15-21): Foundation & Data

**Priority:** Get data fresh, lay foundations, start signature feature.

| Epic | Tickets | Goal |
|------|---------|------|
| EPIC-023 | TKT-245 (fix ingest), TKT-246 (run ingest) | Fresh data by Feb 17 |
| EPIC-018 | TKT-205 (research), TKT-206 (feature eng) | Model architecture defined, features ready |
| EPIC-019 | TKT-210 (React setup) | React project compiling, CI passing |
| EPIC-020 | TKT-216 (comparison pipeline) | H2H data pipeline producing output |
| EPIC-021 | TKT-235 (ranking views) | All 7 ranking composite views created in analytics_ipl.py |
| EPIC-022 | TKT-242 (SUPER SELECTOR fix), TKT-244 (depth chart fix), TKT-243 (salary cap) | Data integrity fixed before editorial pass |
| EPIC-024 | TKT-251 (nav link), TKT-252 (UX cleanup) | Quick wins shipped |

**KdB Week 1 focus:** TKT-211 (design system) + TKT-251 (nav link) -- 2 tickets, manageable.
**Curry Week 1 focus:** TKT-206 (feature eng) + TKT-235 (ranking views) + TKT-242, TKT-243, TKT-244 -- heavy but most are Hustle/fixes.

### Week 2 (Feb 22-28): Build, Integrate, Validate

**Priority:** Train model, build UIs, validate everything.

| Epic | Tickets | Goal |
|------|---------|------|
| EPIC-018 | TKT-207 (train model), TKT-208 (dashboard integration), TKT-209 (monitoring) | Trained model, integrated, monitoring active |
| EPIC-019 | TKT-211 (design system, cont.), TKT-212 (DuckDB-WASM), TKT-215 (testing) | Design system + data layer complete, tests passing |
| EPIC-020 | TKT-217 (comparison UI), TKT-218 (multi-player) | Comparison tool working end-to-end |
| EPIC-021 | TKT-236 (generator), TKT-237 (rankings UI), TKT-238 (domain validation), TKT-239 (QA) | Rankings tab live in The Lab with validated data |
| EPIC-022 | TKT-240 (editorial pass), TKT-241 (doc fixes) | All 10 stat packs reviewed, docs cleaned |
| EPIC-023 | TKT-247 (model registry), TKT-248 (automation chain), TKT-249 (freshness indicator) | Pipeline hardened, model registry operational |
| EPIC-024 | TKT-250 (font/mobile fixes), TKT-253 (WCAG a11y) | Accessibility basics in place |

**KdB Week 2 focus:** TKT-217 (comparison UI) + TKT-237 (rankings UI) + TKT-208 (win prob integration) + TKT-250 (fonts) + TKT-253 (a11y) + TKT-249 (freshness) -- 6 tickets. TKT-249 is P2 Hustle, can slip if needed.

---

## 8. Success Criteria

### Sprint-Level Success
- [ ] All 31 active Sprint 5.0 tickets reach at least REVIEW state by Feb 28
- [ ] At least 24/31 tickets marked DONE (>75% completion)
- [ ] System health score remains >= 85/100
- [ ] Rankings tab live in The Lab with all 7 ranking categories
- [ ] Win probability model trained with documented accuracy (historical replay only)

### Epic-Level Success

| Epic | Success Criteria |
|------|-----------------|
| EPIC-018 | Trained model, documented accuracy, integrated as historical replay, monitoring active. **No forward prediction.** |
| EPIC-019 | React app building, design system documented, DuckDB-WASM data layer working. Migration deferred. |
| EPIC-020 | 2-player comparison working end-to-end, radar charts rendering, multi-player extension. |
| **EPIC-021** | **All 7 ranking categories live in Rankings tab. Domain-validated by Andy Flower. QA-validated by Kante.** |
| EPIC-022 | All 10 stat packs editorially reviewed. SUPER SELECTOR and depth chart issues resolved. |
| EPIC-023 | Ingestion fixed and run. Model registry operational. Automation chain updated. |
| EPIC-024 | Nav standardized. Font/mobile issues fixed. WCAG 2.1 AA basics in place. |

### Quality Gates (from Task Integrity Loop)
- All P0 tickets must pass Florentino Gate before execution
- All ML tickets (TKT-205, 206, 207) must pass Domain Sanity review (Andy Flower + Jose Mourinho)
- EPIC-021 rankings must pass both Domain Sanity (Andy Flower, TKT-238) and QA validation (Kante, TKT-239)
- Win probability model must be labeled "Historical Win Probability Replay" everywhere -- Florentino condition
- Founder validation required for EPIC-021 (Rankings) before marking DONE

---

## 9. Risks & Mitigations

| # | Risk | Probability | Impact | Mitigation |
|---|------|------------|--------|------------|
| 1 | Stephen Curry overload (8 tickets) | High | High | Sequence work: ranking views (Week 1) before generator (Week 2). Close-out fixes are mostly Hustle. |
| 2 | Kevin de Bruyne overload (8 tickets) | Medium | High | Florentino already cut 3 tickets. TKT-249 is P2 safety valve. Week 1 limited to 2 tickets. |
| 3 | DuckDB-WASM performance issues | Medium | High | Early prototype in Week 1 (TKT-212). Fallback to static JSON. |
| 4 | Win prob model accuracy < 70% | Medium | Medium | Fallback to simpler logistic regression. Historical replay only (lower stakes). |
| 5 | Ranking composite scores produce nonsensical leaderboards | Medium | High | Andy Flower domain validation (TKT-238) + Kante QA (TKT-239) catch issues before UI. |
| 6 | Data ingestion failure (TKT-245/246) | Low | High | Manual Cricsheet download as fallback. Brock Purdy dedicated to this in Week 1. |
| 7 | React migration breaks existing Lab | Low | High | Feature branch + staging deploy before merge. Migration tickets already deferred. |
| 8 | 31 tickets in 2 weeks is still aggressive | Medium | Medium | Clear P0/P1/P2 prioritization. P2 tickets (TKT-249) are explicit slip candidates. |

---

## 10. P0 Ticket Checklist (Must Complete)

These 12 P0 tickets are non-negotiable for sprint success:

| # | Ticket | Title | Assignee |
|---|--------|-------|----------|
| 1 | TKT-205 | Win prob model architecture | Jose Mourinho |
| 2 | TKT-206 | Feature engineering from fact_ball | Stephen Curry |
| 3 | TKT-207 | Train & validate win prob model | Ime Udoka |
| 4 | TKT-210 | React project setup + build pipeline | Brad Stevens |
| 5 | TKT-211 | Design system -- component library | Kevin de Bruyne |
| 6 | TKT-212 | DuckDB-WASM integration + React hooks | Brad Stevens |
| 7 | TKT-216 | H2H comparison data pipeline | Stephen Curry |
| 8 | TKT-217 | Comparison UI -- radar charts | Kevin de Bruyne |
| 9 | TKT-235 | Ranking composite views | Stephen Curry |
| 10 | TKT-236 | Ranking generator script | Stephen Curry |
| 11 | TKT-237 | Rankings tab UI | Kevin de Bruyne |
| 12 | TKT-240 | Stat pack editorial pass | Virat Kohli |
| 13 | TKT-242 | SUPER SELECTOR fix | Stephen Curry |
| 14 | TKT-245 | Fix ingest.yml | Brock Purdy |
| 15 | TKT-246 | Run fresh data ingestion | Brock Purdy |
| 16 | TKT-251 | Mission Control nav link | Kevin de Bruyne |

**16 P0 tickets.** If all 16 reach DONE, Sprint 5 is a success regardless of P1/P2 status.

---

## 11. EPIC-018 Florentino Condition -- Detailed Compliance

Per Florentino's binding decision, EPIC-018 (Win Probability Model) operates under strict conditions:

1. **Scope:** Experimental analytics only. Historical match replay. Never forward prediction.
2. **Labeling:** All UI elements must display "Historical Win Probability Replay" -- not "Win Probability Predictor" or similar.
3. **No live inference:** The model processes completed match data. No real-time or pre-match predictions.
4. **Documentation:** Model card must explicitly state experimental status and historical-only scope.
5. **Review gate:** Jose Mourinho and Andy Flower must co-sign the model card before TKT-208 (dashboard integration) begins.

---

*Sprint 5.0 v2: Leaner scope from Florentino. Richer product from Founder. Rankings as the signature feature.*

*Prepared by Tom Brady, PO & Editor-in-Chief*
*Cricket Playbook v5.0.0*
*February 14, 2026*
