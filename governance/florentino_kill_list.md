# Florentino Kill List

**Owner:** Florentino Perez (Program Director)
**Authority:** Constitution v2.0, Section 2.2 -- kill-switch on any task that does not improve the paid artifact.
**Ticket:** TKT-171
**Created:** 2026-02-09

---

## Purpose

This is the institutional memory for scope decisions. Every idea that gets killed, deferred, or quarantined to analytics-only is logged here with the reason. No idea returns from the dead without a row update and Florentino + Founder sign-off.

If it is not on this list, it was not formally rejected. If it is on this list, do not re-propose it without new evidence.

---

## Decision Log

| ID | Idea | Proposer | Date | Decision | Reason | Revisit? |
|----|------|----------|------|----------|--------|----------|
| -- | Copy Editor agent | Brad Stevens | 2026-02-09 | KILLED | Founder will handle copy editing personally. Adding agent headcount for this is unnecessary. (Founder validation on TKT-160) | No |
| IDEA-003 | Win Probability model | Ime Udoka | 2026-02-09 | DEFERRED | This is a prediction product. Constitution Section 1.2 explicitly states "We are NOT a prediction product." Violates core product identity. | Only if product definition changes |
| IDEA-005 | Interactive React dashboard | Kevin de Bruyne | 2026-02-09 | DEFERRED | Current HTML/JS output is adequate for MVP. React adds build complexity, maintenance burden, and zero incremental revenue at this stage. | Post-MVP if distribution requires it |
| IDEA-007 | Player comparison tool | Kevin de Bruyne | 2026-02-09 | DEFERRED | Not in MVP scope. Depth charts and Predicted XII already cover player evaluation. Comparison view is a nice-to-have, not a must-have. | Sprint 6+ if stat pack feedback demands it |
| IDEA-002 | CricPom (KenPom clone) | Jose Mourinho | 2026-02-09 | ANALYTICS_ONLY | Research value for internal calibration. Not for the paid artifact -- it is an analytics research product, not editorial content (Constitution Section 1.2). | Outputs may feed into stat pack metrics |
| -- | REST API (FastAPI) | Backlog | 2026-02-09 | DEFERRED | No customer-facing product requires an API. We ship a magazine, not a platform. Engineering effort with zero revenue justification at MVP. | Only if distribution model changes |
| -- | Real-time Match Simulation | Backlog (S3.2-02) | 2026-02-09 | KILLED | We are NOT live commentary or reactive content (Constitution Section 1.2). This is a fundamentally different product. | No |

---

## Decision Criteria

Every idea is evaluated against one question: **Does this directly improve the paid artifact?**

- **KILLED** -- No path to the paid artifact. Do not revisit without a product redefinition.
- **DEFERRED** -- Potentially valuable but not now. Revisit conditions noted.
- **ANALYTICS_ONLY** -- Has internal/research value but must not leak into paid artifact scope or consume editorial bandwidth.

---

## Process

1. Any agent can propose an idea (IDEA-XXX ticket in Mission Control).
2. Florentino evaluates against the paid artifact test.
3. Decision is logged here with reason.
4. Killed ideas require Founder + Florentino sign-off to reopen.
5. Deferred ideas are re-evaluated at sprint boundaries if conditions change.

---

*Florentino Kill List v1.0 -- 2026-02-09*
