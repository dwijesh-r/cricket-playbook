# Progress Percentage Definitions

**Author:** Pep Guardiola (Process Excellence)
**Date:** February 6, 2026
**Ticket:** RETRO-001 Action Item

---

## Overview

Progress percentage indicates **work completion within the current state**, not overall ticket completion. This avoids confusion where a ticket at 95% in REVIEW state could mean different things.

---

## Progress by State

### IDEA (0-100%)
| Progress | Meaning |
|----------|---------|
| 0-25% | Raw idea captured, no details |
| 26-50% | Initial scope outlined |
| 51-75% | Acceptance criteria drafted |
| 76-100% | Ready for Florentino Gate review |

### BACKLOG (0-100%)
| Progress | Meaning |
|----------|---------|
| 0-25% | Florentino Gate passed, not yet refined |
| 26-50% | Technical approach discussed |
| 51-75% | Dependencies identified, effort estimated |
| 76-100% | Sprint-ready, can move to READY |

### READY (Always 0%)
Tickets in READY are waiting to be picked up. Progress resets to 0% when entering READY.

### RUNNING (0-100%)
| Progress | Meaning |
|----------|---------|
| 0-10% | Just started, environment setup |
| 11-30% | Core implementation in progress |
| 31-60% | Major functionality complete |
| 61-80% | Testing and edge cases |
| 81-95% | Documentation and cleanup |
| 96-100% | Ready for review, moving to REVIEW |

### BLOCKED (Frozen)
Progress freezes at the value when blocked. Does not change until unblocked.

### REVIEW (90-100%)
| Progress | Meaning |
|----------|---------|
| 90% | In Domain Sanity review |
| 92% | Domain Sanity passed, in System Check |
| 95% | All gates passed, awaiting Founder |
| 100% | Review complete, moving to VALIDATION |

### VALIDATION (95-100%)
| Progress | Meaning |
|----------|---------|
| 95% | Awaiting Founder review |
| 98% | Founder reviewing, feedback pending |
| 100% | Founder approved, moving to DONE |

### DONE (Always 100%)
Completed tickets are always at 100%.

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│              PROGRESS % GUIDE                   │
├─────────────────────────────────────────────────┤
│ IDEA      → Scoping completeness (0-100%)       │
│ BACKLOG   → Sprint-readiness (0-100%)           │
│ READY     → Always 0% (waiting pickup)          │
│ RUNNING   → Implementation progress (0-100%)    │
│ BLOCKED   → Frozen at block point               │
│ REVIEW    → Gate passage (90-100%)              │
│ VALIDATION→ Founder review status (95-100%)     │
│ DONE      → Always 100%                         │
└─────────────────────────────────────────────────┘
```

---

## Examples

| Ticket | State | Progress | Interpretation |
|--------|-------|----------|----------------|
| TKT-049 | RUNNING | 40% | Core implementation in progress |
| TKT-100 | RUNNING | 80% | Testing and documentation phase |
| TKT-051 | VALIDATION | 95% | Awaiting Founder review |
| TKT-042 | REVIEW | 95% | All gates passed, needs Founder |

---

*Pep Guardiola*
*Process Excellence Lead*
*Cricket Playbook v4.1.0*
