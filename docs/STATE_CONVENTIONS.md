# State Naming Conventions

**Author:** Tom Brady (Delivery Owner)
**Date:** February 6, 2026
**Ticket:** RETRO-001 Action Item

---

## Kanban Column States

The following states are valid for tickets in Mission Control:

| State | Column Name | Description | Valid Transitions |
|-------|-------------|-------------|-------------------|
| `IDEA` | Idea | Raw ideas not yet scoped | → BACKLOG |
| `BACKLOG` | Backlog | Scoped and approved for sprint | → READY, IDEA |
| `READY` | Ready | Ready to be picked up by an agent | → RUNNING, BACKLOG |
| `RUNNING` | Running | Actively being worked on | → REVIEW, BLOCKED, READY |
| `BLOCKED` | Blocked | Waiting on external dependency | → RUNNING, BACKLOG |
| `REVIEW` | Review | Code/work complete, awaiting Domain Sanity or System Check | → VALIDATION, RUNNING |
| `VALIDATION` | 🌹 Founder Review | Awaiting Founder sign-off | → DONE, REVIEW |
| `DONE` | Done | Completed and approved | Terminal state |

---

## State Naming Rules

### 1. Always Use UPPERCASE
- ✅ `RUNNING`
- ❌ `Running`, `running`

### 2. Use Underscores for Multi-word States
- ✅ `FOUNDER_REVIEW` (if needed)
- ❌ `FOUNDER-REVIEW`, `FounderReview`

### 3. Never Invent New States
All tickets must use one of the 8 defined states above. If a new state is needed, it must be:
1. Proposed via ticket
2. Approved by Florentino
3. Added to this document

---

## EPIC States

EPICs use the same states as tickets. An EPIC moves to:
- `VALIDATION` when all child tickets are in VALIDATION or DONE
- `DONE` when all child tickets are DONE and Founder has approved

---

## Common Mistakes

| Mistake | Correct Usage |
|---------|---------------|
| `FOUNDER_REVIEW` | Use `VALIDATION` - that IS the Founder Review column |
| `IN_PROGRESS` | Use `RUNNING` |
| `PENDING` | Use `BACKLOG` or `READY` depending on context |
| `COMPLETED` | Use `DONE` |
| `APPROVED` | Use `DONE` (approval is a gate, not a state) |

---

## Tag Conventions (Related)

Tags provide additional context without changing state:

| Tag | Meaning | Color |
|-----|---------|-------|
| `🌹 Awaiting Founder` | In VALIDATION, waiting for Founder | Rose/Pink |
| `🌹 Founder Review` | Ready for Founder review | Rose/Pink |
| `✅ Founder Approved` | Founder has approved | Green |
| `🔄 In Progress` | Actively being worked on | Blue |
| `🔶 Illini Plan Review` | Plan document awaiting Founder approval | Orange (Fighting Illini) |

---

*Tom Brady*
*Delivery Owner*
*Cricket Playbook v4.1.0*
