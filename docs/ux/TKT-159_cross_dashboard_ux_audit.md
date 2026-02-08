# TKT-159: Cross-Dashboard UX Audit

**Owner:** Jayson Tatum (UX & Reader Flow)
**Created:** 2026-02-08
**Priority:** P0
**Status:** RUNNING

---

## What This Ticket Is About

A comprehensive UX audit of all three Cricket Playbook dashboard surfaces:

1. **The Boardroom** — Executive-facing analytics dashboard
2. **The Lab** — Deep-dive player analysis and exploration tool
3. **Mission Control Panel** — Internal project/ticket management dashboard

No formal UX audit has been conducted across all three surfaces. Each was built incrementally by different agents across different EPICs. This ticket produces a single source-of-truth UX scorecard.

---

## Process

### Phase 1: Individual Dashboard Audit
For each dashboard (Boardroom, The Lab, Mission Control), evaluate:

| Category | What to Assess |
|----------|---------------|
| **Navigation & Information Architecture** | Can a user find what they need? Is the hierarchy clear? Are labels intuitive? |
| **Visual Design & Consistency** | Color usage, typography, spacing, brand alignment across surfaces |
| **Responsive Design** | Mobile, tablet, desktop behavior. Breakpoint transitions. Touch targets. |
| **Data Visualization** | Chart clarity, appropriate chart types, labels, legends, tooltips |
| **Interaction Design** | Hover states, click targets, feedback loops, loading states, animations |
| **Accessibility** | Color contrast, keyboard navigation, screen reader friendliness, font sizes |
| **Performance & Load** | Perceived load time, render blocking, asset sizes, animation jank |
| **Content & Copy** | Clarity of labels, error messages, empty states, help text |

### Phase 2: Cross-Dashboard Consistency
- Are the three surfaces consistent in design language?
- Shared components (headers, footers, nav) — do they look/behave the same?
- Color system alignment across dashboards
- Typography and spacing consistency

### Phase 3: Scoring & Rating
- Score each category 0–100 (decimals included) per dashboard
- Apply weights to categories based on user impact
- Compute per-dashboard composite score
- Compute overall product UX score (weighted average across dashboards)

### Phase 4: Recommendations
- For each finding, provide:
  - **What:** The specific issue
  - **Where:** Dashboard + location
  - **Why it matters:** User impact
  - **Suggestion:** How to fix it
  - **Priority:** P0 / P1 / P2 based on impact vs effort

---

## End Goal

### Deliverables

1. **Composite UX Rating** — A single 0–100 score (decimals included) for the entire product
2. **Per-Dashboard Scores** — Individual 0–100 ratings for Boardroom, The Lab, Mission Control
3. **Category Breakdown** — Weighted scores for each assessment category
4. **Findings Report** — Specific issues found, organized by severity
5. **Improvement Suggestions** — Prioritized list of fixes with rationale and expected impact
6. **Cross-Dashboard Consistency Score** — How well the three surfaces align

### Success Criteria
- All three dashboards audited with documented findings
- Every suggestion includes a "why" (not just "what to fix")
- Scores are defensible with specific evidence from the dashboards
- Recommendations are actionable (an agent can pick one up and implement it)

---

## Dashboards to Audit

| Dashboard | Primary File | Purpose |
|-----------|-------------|---------|
| **The Boardroom** | `scripts/the_lab/dashboard/index.html` | Executive analytics |
| **The Lab** | `scripts/the_lab/dashboard/about.html` + data views | Player deep-dives |
| **Mission Control** | `scripts/mission_control/dashboard/index.html` | Project management |
| **Mission Control About** | `scripts/mission_control/dashboard/about.html` | Team roster |

---

## Task Integrity Loop Gates

| Gate | Owner | Status |
|------|-------|--------|
| `florentino_gate` | Florentino Perez | APPROVED |
| `domain_sanity` | Brad Stevens | PENDING |
| `enforcement_check` | N'Golo Kante | PENDING |
| `system_check` | Ime Udoka | PENDING |
| `founder_validation` | Florentino Perez | PENDING |
