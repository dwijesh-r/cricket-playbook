# Task Integrity Loop

**Version:** 1.0.0
**Owner:** Florentino Perez + Tom Brady
**Status:** Active

---

## Overview

The Task Integrity Loop is a mandatory 8-step quality process for every task in Cricket Playbook. No exceptions. This ensures every piece of work materially improves our paid artifact.

---

## The Loop

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Step 0        Step 1         Step 2        Step 3        Step 4      │
│   ┌─────┐      ┌─────┐        ┌─────┐       ┌─────┐       ┌─────┐      │
│   │ PRD │ ──── │GATE │ ────── │BUILD│ ───── │SANITY│ ──── │CHECK│      │
│   └─────┘      └─────┘        └─────┘       └─────┘       └─────┘      │
│                   │                            │              │         │
│               Approved?                    Yes/No/Fix    Process OK?    │
│                   │                            │              │         │
│              ┌────┴────┐                       │              │         │
│              │         │                       │              │         │
│           Approved  Rejected                   │              │         │
│              │         │                       │              │         │
│              ▼         ▼                       │              │         │
│           Continue   STOP                      │              │         │
│                                                │              │         │
│   Step 5        Step 6         Step 7          │              │         │
│   ┌─────┐      ┌─────┐        ┌─────┐          │              │         │
│   │SHIP │ ──── │NOTE │ ────── │SYSTEM│ ◄───────┴──────────────┘         │
│   └─────┘      └─────┘        └─────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step 0: Task Declaration

**Owner:** Requesting Agent
**Output:** Task PRD

### Required Content

```markdown
# Task PRD: [Task Name]

## Problem Statement
What problem does this solve?

## Proposed Solution
What will be built/changed?

## Success Criteria
How do we know it's done?

## Scope
- In scope: [list]
- Out of scope: [list]

## Dependencies
What must exist before this can start?

## Estimated Effort
[Small / Medium / Large]
```

### Template Location
`governance/templates/TASK_PRD_TEMPLATE.md`

---

## Step 1: Florentino Gate

**Owner:** Florentino Perez
**Question:** "Does this task materially improve the paid artifact or strategic decision?"

### Outcomes

| Outcome | Meaning | Next Step |
|---------|---------|-----------|
| ✅ **APPROVED** | Directly improves paid artifact | Proceed to Step 2 |
| 🔬 **ANALYTICS ONLY** | Research value, not for paid artifact | Proceed with label |
| ❌ **NOT APPROVED** | Does not add sufficient value | STOP |

### Evaluation Criteria

Florentino asks:
1. Who is the buyer?
2. Why would they pay instead of reading free content?
3. What preparation burden does this remove?
4. If this feature is removed, does anyone notice?

### Sign-off Format

```
FLORENTINO GATE: [APPROVED / ANALYTICS ONLY / NOT APPROVED]
Reason: [One sentence]
Date: [YYYY-MM-DD]
```

---

## Step 2: Build

**Owner:** Assigned Agent
**Rule:** Work ONLY within approved scope

### Build Rules

| Do | Don't |
|----|-------|
| Build exactly what was approved | Add "nice to have" features |
| Stay within scope boundaries | Expand scope without approval |
| Ask if unclear | Assume and proceed |
| Document as you build | Leave documentation for later |

### Scope Creep Response

If you identify additional work needed:
1. STOP building the additional item
2. Document it as a separate task
3. Submit for Florentino Gate (Step 1)
4. Continue with original scope

---

## Step 3: Domain Sanity Loop

**Owners:** Jose Mourinho, Andy Flower, Pep Guardiola
**Format:** Yes / No / Fix (no essays)

### Three Sign-offs Required

| Agent | Question | Focus |
|-------|----------|-------|
| **Jose Mourinho** | Is this robust with current data? Are baselines clear? Is this scalable? | Data & Robustness |
| **Andy Flower** | Would this make sense to a coach, analyst, or fan? | Cricket Truth |
| **Pep Guardiola** | Is this structurally coherent? Does it contradict the system? | System Integrity |

### Sign-off Format

```
DOMAIN SANITY:
- Jose Mourinho: [YES / NO / FIX: reason]
- Andy Flower: [YES / NO / FIX: reason]
- Pep Guardiola: [YES / NO / FIX: reason]
Date: [YYYY-MM-DD]
```

### If Any "FIX"

1. Address the specific issue
2. Return to that reviewer for re-sign-off
3. Do not proceed until all three are YES

---

## Step 4: Enforcement Check

**Owner:** Tom Brady
**Role:** Process guardian (not judging content quality)

### Checklist

| Check | Question |
|-------|----------|
| Loop followed | Did the task go through Steps 0-3? |
| Objections addressed | Were any "FIX" items resolved? |
| Scope respected | Was only the approved scope built? |
| Documentation ready | Are READMEs and notes prepared? |

### Outcomes

| Result | Action |
|--------|--------|
| ✅ **PASS** | Proceed to Step 5 |
| ❌ **FAIL** | Return to appropriate step |

### Sign-off Format

```
ENFORCEMENT CHECK: [PASS / FAIL]
Issues (if any): [list]
Date: [YYYY-MM-DD]
```

---

## Step 5: Commit and Ship

**Owner:** Assigned Agent
**Action:** Merge to main branch

### Commit Requirements

- Descriptive commit message
- Reference to task/PRD
- Co-author attribution
- All tests passing

### Commit Message Format

```
[Category] Brief description

- Detail 1
- Detail 2

Task: [Task ID or PRD reference]
Florentino Gate: APPROVED
Domain Sanity: All YES

Co-Authored-By: [Agent Name]
```

---

## Step 6: Post Task Note

**Owner:** Assigned Agent
**Location:** Update relevant README or create task note

### Required Content

| Item | Description |
|------|-------------|
| What changed | Brief description of changes |
| Assumption tested | What hypothesis was validated |
| Risk introduced | Any new risks or limitations |
| USP of change | How this improves the product |

### Format

```markdown
## Post Task Note: [Task Name]

**Date:** [YYYY-MM-DD]
**Owner:** [Agent Name]

### What Changed
[Description]

### Assumption Tested
[What we believed, what we learned]

### Risk Introduced
[Any new risks or caveats]

### USP of This Change
[How this makes the product better]
```

---

## Step 7: System Check

**Owner:** N'Golo Kanté
**Focus:** Technical integrity

### Checklist

| Check | Verification |
|-------|--------------|
| Schema intact | No breaking changes to data structure |
| Manifests updated | Output manifests reflect current state |
| Tests passing | All pytest tests green |
| No regressions | Previous functionality still works |

### Sign-off Format

```
SYSTEM CHECK: [PASS / FAIL]
Tests: [X/Y passing]
Schema: [Intact / Changed (approved)]
Manifests: [Updated / N/A]
Date: [YYYY-MM-DD]
```

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                  TASK INTEGRITY LOOP                       │
├────────┬───────────────────────────────┬──────────────────┤
│ Step   │ Action                        │ Owner            │
├────────┼───────────────────────────────┼──────────────────┤
│ 0      │ Create PRD                    │ Requester        │
│ 1      │ Florentino Gate               │ Florentino Perez │
│ 2      │ Build (within scope)          │ Assigned Agent   │
│ 3      │ Domain Sanity (Yes/No/Fix)    │ JM + AF + PG     │
│ 4      │ Enforcement Check             │ Tom Brady        │
│ 5      │ Commit and Ship               │ Assigned Agent   │
│ 6      │ Post Task Note                │ Assigned Agent   │
│ 7      │ System Check                  │ N'Golo Kanté     │
└────────┴───────────────────────────────┴──────────────────┘
```

---

## Exception Handling

### Emergency Fixes

For critical bugs only:
1. Flag as EMERGENCY to Tom Brady
2. Abbreviated loop: Steps 2 → 5 → 7
3. Full loop documentation within 24 hours

### Founder Override

The Founder can override any step. Document with:
```
FOUNDER OVERRIDE: [Step skipped]
Reason: [Explanation]
Date: [YYYY-MM-DD]
```

### Founder Active Collaboration

The Founder is an **active collaborator**, not just an approval gate. Agents should:

1. **Seek Input Early:** On key decisions (methodology, feature scope, editorial direction), ask the Founder before finalizing
2. **Welcome Tuning:** Founder feedback mid-work is normal and expected, not a failure
3. **Iterate Quickly:** Founder input doesn't restart the full loop - incorporate and continue

#### When to Consult Founder

| Situation | Action |
|-----------|--------|
| Methodology choice (e.g., which metrics to use) | Ask before implementing |
| Feature scope unclear | Clarify with Founder |
| Editorial tone/framing decisions | Seek Founder preference |
| Trade-offs between options | Present options to Founder |
| Surprising data findings | Share with Founder for interpretation |

#### Founder Feedback Process

```
┌─────────────────────────────────────────────────────────────┐
│              FOUNDER FEEDBACK (Lightweight)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Agent presents work/question to Founder                 │
│         ↓                                                   │
│  2. Founder provides input/tuning                           │
│         ↓                                                   │
│  3. Agent incorporates feedback                             │
│         ↓                                                   │
│  4. Continue from current step (no restart)                 │
│                                                             │
│  Document with:                                             │
│  FOUNDER INPUT: [Summary of feedback]                       │
│  Action Taken: [How it was incorporated]                    │
│  Date: [YYYY-MM-DD]                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Key Principle

> "The Founder's vision drives the product. Active collaboration ensures we build what matters, not just what's technically correct."

---

## Tracking

All task loops are tracked in:
- Sprint KANBAN (`docs/KANBAN.md`)
- Task-specific PRD files (`governance/tasks/`)

---

*Task Integrity Loop v1.1.0*
*Cricket Playbook Governance*
*Updated: 2026-02-01 - Added Founder Active Collaboration*
