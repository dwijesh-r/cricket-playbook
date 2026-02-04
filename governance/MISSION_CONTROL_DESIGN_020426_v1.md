# Mission Control Design Specification

**Document:** MISSION_CONTROL_DESIGN_020426_v1.md
**Authors:** Tom Brady (Delivery Owner), Brad Stevens (Architecture Lead)
**Date:** 2026-02-04
**Version:** 1.1
**Status:** FOUNDER APPROVED - Pilot (v0.1)

---

## Executive Summary

Mission Control is a local-only, JIRA-style task board for Cricket Playbook agents. It provides visibility into work progress, enforces governance gates, and ensures no work happens without explicit tracking and approval.

**Core Principle:** "If it's not on the board, it didn't happen."

### Design Highlights

| Component | Decision |
|-----------|----------|
| Data Storage | JSON files in `.mission-control/` directory |
| Hierarchy | EPIC → Ticket → Subtask |
| States | 8 states with role-aware transitions (incl. VALIDATION) |
| Integration | Full Task Integrity Loop mapping |
| CLI | `mc <entity> <action> [options]` |

---

## 1. Data Model (Tom Brady)

### 1.1 Three-Tier Hierarchy

```
EPIC (Project)
 └─ Ticket (Deliverable)
     └─ Subtask (Executable step)
```

**Progress Roll-up:**
- Subtask completion → Ticket % complete
- Ticket completion → EPIC % complete
- EPIC completion → Sprint velocity

### 1.2 Entity Relationships

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    EPIC     │────▶│   TICKET    │────▶│   SUBTASK   │
│             │ 1:N │             │ 1:N │             │
│ - id        │     │ - id        │     │ - id        │
│ - title     │     │ - epic_id   │     │ - ticket_id │
│ - owner     │     │ - title     │     │ - title     │
│ - sprint    │     │ - owner     │     │ - status    │
│ - progress  │     │ - state     │     │ - assignee  │
└─────────────┘     │ - priority  │     └─────────────┘
                    │ - llm_required│
                    │ - progress   │
                    └─────────────┘
```

---

## 2. Workflow States (Tom Brady)

### 2.1 State Diagram

```
                    ┌─────────┐
                    │  IDEA   │
                    └────┬────┘
                         │ Product Owner prioritizes
                         ▼
                    ┌─────────┐
                    │ BACKLOG │
                    └────┬────┘
                         │ Sprint planning assigns
                         ▼
                    ┌─────────┐
              ┌────▶│  READY  │◀────┐
              │     └────┬────┘     │
              │          │ Agent picks up
              │          ▼          │
              │     ┌─────────┐     │
              │     │ RUNNING │─────┤
              │     └────┬────┘     │
              │          │          │
              │   ┌──────┴──────┐   │
              │   ▼             ▼   │
         ┌─────────┐      ┌─────────┐
         │ BLOCKED │      │ REVIEW  │
         └─────────┘      └────┬────┘
                               │ Technical gates pass
                               ▼
                        ┌────────────┐
                        │ VALIDATION │ ◀─── Founder Review
                        └─────┬──────┘
                              │ Founder approves
                              ▼
                          ┌─────────┐
                          │  DONE   │
                          └─────────┘
```

### 2.2 State Definitions

| State | Description | Entry Condition | Exit Condition |
|-------|-------------|-----------------|----------------|
| IDEA | Proposed work, not yet evaluated | Created by anyone | Florentino Gate decision |
| BACKLOG | Approved but not scheduled | Florentino APPROVED | Assigned to sprint |
| READY | Scheduled, ready to start | Sprint assigned | Agent starts work |
| RUNNING | Active work in progress | Agent picks up | Work complete or blocked |
| BLOCKED | Cannot proceed | Dependency or issue | Blocker resolved |
| REVIEW | Awaiting technical validation | Work submitted | Domain Sanity + QA pass |
| VALIDATION | Awaiting Founder approval | Technical gates pass | Founder approves |
| DONE | Complete and shipped | Founder approved | N/A (terminal) |

### 2.3 State Transitions

| From | To | Trigger | Required By |
|------|-----|---------|-------------|
| IDEA | BACKLOG | `florentino_gate: APPROVED` | Florentino Perez |
| IDEA | (deleted) | `florentino_gate: NOT_APPROVED` | Florentino Perez |
| BACKLOG | READY | `sprint_id` assigned | Tom Brady |
| READY | RUNNING | Agent starts | Assigned Agent |
| RUNNING | REVIEW | Work submitted | Assigned Agent |
| RUNNING | BLOCKED | Blocker identified | Anyone |
| BLOCKED | READY | Blocker resolved | Tom Brady |
| REVIEW | VALIDATION | All technical gates YES | N'Golo Kanté |
| REVIEW | RUNNING | Gate FIX required | Reviewer |
| VALIDATION | DONE | `founder_validation: APPROVED` | Founder |
| VALIDATION | RUNNING | Founder requests changes | Founder |

---

## 3. Role-Permission Matrix (Tom Brady)

### 3.1 Roles

| Role | Agent(s) | Primary Responsibility |
|------|----------|----------------------|
| **Founder** | (Human) | Final validation & override authority |
| Product Owner | Florentino Perez | Scope & priority |
| Delivery Owner | Tom Brady | Workflow & execution |
| Executor | Stephen Curry, Virat Kohli, Kevin de Bruyne | Build deliverables |
| Validator | Jose Mourinho, Andy Flower, Pep Guardiola | Domain sanity |
| QA | N'Golo Kanté | System check |
| Architect | Brad Stevens | Governance review |
| ML Ops | Ime Udoka | Model & deployment |

### 3.2 Permission Matrix

| Action | Founder | Product Owner | Delivery Owner | Executor | Validator | QA |
|--------|:-------:|:-------------:|:--------------:|:--------:|:---------:|:--:|
| Create EPIC | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Create Ticket | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Approve (Gate 1) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Assign to Sprint | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Pick Up Ticket | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Submit for Review | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Domain Sanity | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| System Check | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Final Validation** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Mark DONE | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Override Any | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Note:** Only the Founder can move tickets from VALIDATION → DONE. This is the final approval gate.

---

## 4. File Structure (Brad Stevens)

### 4.1 Directory Layout

```
.mission-control/
├── config/
│   ├── settings.json          # Global settings
│   ├── schemas/               # JSON schemas
│   │   ├── epic.schema.json
│   │   ├── ticket.schema.json
│   │   └── sprint.schema.json
│   └── roles.json             # Role definitions
│
├── data/
│   ├── epics/                 # One JSON file per EPIC
│   │   ├── EPIC-001.json
│   │   └── EPIC-002.json
│   ├── tickets/               # One JSON file per ticket
│   │   ├── TKT-001.json
│   │   └── TKT-002.json
│   ├── sprints/               # One JSON file per sprint
│   │   ├── SPRINT-4.json
│   │   └── SPRINT-5.json
│   └── agents/                # Agent activity tracking
│       └── agent_status.json
│
├── indexes/                   # Auto-generated lookups
│   ├── by_state.json
│   ├── by_owner.json
│   ├── by_sprint.json
│   └── by_epic.json
│
├── views/                     # Pre-computed views
│   ├── kanban.json
│   ├── scoreboard.json
│   └── cockpit.json
│
└── logs/                      # Audit trail
    └── audit.jsonl            # Append-only log
```

### 4.2 Design Rationale

| Decision | Rationale |
|----------|-----------|
| JSON files | Human-readable, git-friendly, no database required |
| One file per entity | Easy to review changes in PRs |
| Indexes separate | Rebuild-able from source data |
| Append-only logs | Audit trail cannot be modified |

---

## 5. JSON Schemas (Brad Stevens)

### 5.1 Ticket Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "title", "state", "created_at"],
  "properties": {
    "id": { "type": "string", "pattern": "^TKT-\\d{3,}$" },
    "epic_id": { "type": "string", "pattern": "^EPIC-\\d{3,}$" },
    "title": { "type": "string", "maxLength": 100 },
    "description": { "type": "string" },
    "state": {
      "type": "string",
      "enum": ["IDEA", "BACKLOG", "READY", "RUNNING", "BLOCKED", "REVIEW", "VALIDATION", "DONE"]
    },
    "priority": {
      "type": "string",
      "enum": ["P0", "P1", "P2", "P3"]
    },
    "owner": { "type": "string" },
    "assignee": { "type": "string" },
    "sprint_id": { "type": "string" },
    "llm_required": { "type": "boolean", "default": false },
    "llm_budget_tokens": { "type": "integer" },
    "llm_approved_by": { "type": "string" },
    "subtasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "title": { "type": "string" },
          "status": { "enum": ["pending", "in_progress", "done"] },
          "assignee": { "type": "string" }
        }
      }
    },
    "gates": {
      "type": "object",
      "properties": {
        "florentino_gate": {
          "type": "object",
          "properties": {
            "status": { "enum": ["PENDING", "APPROVED", "ANALYTICS_ONLY", "NOT_APPROVED"] },
            "reason": { "type": "string" },
            "date": { "type": "string", "format": "date" }
          }
        },
        "domain_sanity": {
          "type": "object",
          "properties": {
            "jose_mourinho": { "enum": ["PENDING", "YES", "NO", "FIX"] },
            "andy_flower": { "enum": ["PENDING", "YES", "NO", "FIX"] },
            "pep_guardiola": { "enum": ["PENDING", "YES", "NO", "FIX"] },
            "date": { "type": "string", "format": "date" }
          }
        },
        "enforcement_check": {
          "type": "object",
          "properties": {
            "status": { "enum": ["PENDING", "PASS", "FAIL"] },
            "issues": { "type": "array", "items": { "type": "string" } },
            "date": { "type": "string", "format": "date" }
          }
        },
        "system_check": {
          "type": "object",
          "properties": {
            "status": { "enum": ["PENDING", "PASS", "FAIL"] },
            "tests_passed": { "type": "integer" },
            "tests_total": { "type": "integer" },
            "date": { "type": "string", "format": "date" }
          }
        },
        "founder_validation": {
          "type": "object",
          "properties": {
            "status": { "enum": ["PENDING", "APPROVED", "CHANGES_REQUESTED"] },
            "feedback": { "type": "string" },
            "validated_by": { "type": "string", "const": "Founder" },
            "date": { "type": "string", "format": "date" }
          }
        }
      }
    },
    "progress_pct": { "type": "integer", "minimum": 0, "maximum": 100 },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "completed_at": { "type": "string", "format": "date-time" }
  }
}
```

### 5.2 EPIC Schema

```json
{
  "id": "EPIC-001",
  "title": "Sprint 4 - Foundation & Editorial Excellence",
  "description": "Establish governance and fix critical product issues",
  "owner": "Tom Brady",
  "sprint_id": "SPRINT-4",
  "tickets": ["TKT-001", "TKT-002", "TKT-003"],
  "progress_pct": 52,
  "created_at": "2026-01-31T00:00:00Z",
  "target_date": "2026-02-14"
}
```

### 5.3 Sprint Schema (with LLM Budget)

```json
{
  "id": "SPRINT-4",
  "title": "Sprint 4 - Foundation & Editorial Excellence",
  "duration_weeks": 2,
  "start_date": "2026-01-31",
  "end_date": "2026-02-14",
  "epics": ["EPIC-001"],
  "tickets": ["TKT-001", "TKT-002", "TKT-003"],
  "llm_budget": {
    "total_tokens": 1000000,
    "used_tokens": 0,
    "approved_by": "Founder",
    "approved_date": "2026-01-31"
  },
  "velocity": {
    "planned_points": 83,
    "completed_points": 43,
    "burndown": [31, 35, 40, 43]
  },
  "status": "ACTIVE",
  "created_at": "2026-01-31T00:00:00Z"
}
```

---

## 6. CLI Interface (Brad Stevens)

### 6.1 Command Structure

```bash
mc <entity> <action> [options]
```

### 6.2 Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `mc ticket create` | Create new ticket | `mc ticket create --title "Fix Digvesh Rathi" --priority P0` |
| `mc ticket list` | List tickets | `mc ticket list --state RUNNING --assignee "Stephen Curry"` |
| `mc ticket update` | Update ticket | `mc ticket update TKT-001 --state REVIEW` |
| `mc ticket assign` | Assign ticket | `mc ticket assign TKT-001 --to "Stephen Curry"` |
| `mc epic create` | Create EPIC | `mc epic create --title "Sprint 4"` |
| `mc sprint plan` | Plan sprint | `mc sprint plan SPRINT-4 --tickets TKT-001,TKT-002` |
| `mc board` | Show Kanban | `mc board --sprint SPRINT-4` |
| `mc cockpit` | Agent status | `mc cockpit` |
| `mc score` | Scoreboard | `mc score --sprint SPRINT-4` |
| `mc approve` | Gate approval | `mc approve TKT-001 --gate florentino --status APPROVED` |

### 6.3 Example Workflows

**Create and Approve Ticket:**
```bash
# 1. Create ticket
mc ticket create --title "Regenerate Predicted XIIs" --priority P0 --epic EPIC-001

# 2. Florentino Gate approval
mc approve TKT-001 --gate florentino --status APPROVED --reason "Directly improves paid artifact"

# 3. Assign to sprint and agent
mc ticket update TKT-001 --sprint SPRINT-4
mc ticket assign TKT-001 --to "Stephen Curry"

# 4. Agent starts work
mc ticket update TKT-001 --state RUNNING

# 5. Submit for review
mc ticket update TKT-001 --state REVIEW

# 6. Domain sanity
mc approve TKT-001 --gate domain_sanity --reviewer andy_flower --status YES

# 7. System check
mc approve TKT-001 --gate system_check --status PASS --tests 43/43

# 8. Move to Founder validation
mc ticket update TKT-001 --state VALIDATION

# 9. Founder validation (only Founder can execute)
mc approve TKT-001 --gate founder_validation --status APPROVED

# 10. Mark done (auto-transitions on Founder approval)
mc ticket update TKT-001 --state DONE
```

---

## 7. Integration with Task Integrity Loop

### 7.1 Loop-to-State Mapping

| Task Integrity Step | Mission Control State | Gate Field |
|---------------------|----------------------|------------|
| Step 0: PRD Creation | IDEA → BACKLOG | (ticket created) |
| Step 1: Florentino Gate | BACKLOG | `gates.florentino_gate` |
| Step 2: Build | RUNNING | `assignee`, `progress_pct` |
| Step 3: Domain Sanity | REVIEW | `gates.domain_sanity` |
| Step 4: Enforcement Check | REVIEW | `gates.enforcement_check` |
| Step 5: System Check | REVIEW → VALIDATION | `gates.system_check` |
| Step 6: **Founder Validation** | VALIDATION → DONE | `gates.founder_validation` |
| Step 7: Commit and Ship | DONE | `completed_at` |
| Step 8: Post Task Note | DONE | (comment added) |

### 7.2 Validation Hooks

**Pre-transition hooks:**
- BACKLOG → READY: Verify `florentino_gate.status == APPROVED`
- REVIEW → VALIDATION: Verify all technical gates are YES/PASS
- VALIDATION → DONE: Verify `founder_validation.status == APPROVED`
- Any → RUNNING (if `llm_required`): Verify `llm_approved_by` set

**Post-transition hooks:**
- Any state change: Update `updated_at`, log to audit
- VALIDATION: Notify Founder for approval
- DONE: Calculate final progress, update EPIC progress

---

## 8. Implementation Phases

### Phase 0: Foundation (v0.1) - Week 1
- Create `.mission-control/` directory structure
- Implement JSON schemas
- Basic CRUD operations for tickets
- Manual state transitions

### Phase 1: Workflow (v0.2) - Week 2
- State machine with validation
- Pre/post transition hooks
- Progress calculation
- Audit logging

### Phase 2: Sprint Planning (v0.3) - Week 3
- Sprint lifecycle management
- Ticket-to-sprint assignment
- Velocity tracking
- Burndown calculation

### Phase 3: Approvals (v0.4) - Week 4
- Florentino Gate integration
- Domain Sanity integration
- LLM approval workflow
- Gate validation enforcement

### Phase 4: Views (v0.5) - Week 5
- Kanban board view
- Scoreboard view
- Agent cockpit view
- Sprint report generation

### Phase 5: Polish (v1.0) - Week 6
- Documentation
- Migration from existing PRDs
- Founder sign-off
- Production deployment

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Work Tracking | 100% tickets | All work has a ticket |
| LLM Control | 100% approved | No unauthorized LLM use |
| Gate Compliance | 0 bypasses | All gates enforced |
| Sprint Velocity | Improving trend | Points per sprint |
| Blocked Rate | < 10% | Blocked / Total tickets |
| Cycle Time | Decreasing | READY → DONE duration |

---

## 10. Founder Decisions (Resolved)

| Question | Founder Decision | Implementation |
|----------|-----------------|----------------|
| Sprint Duration | **2-week sprints** (standard) | `sprint.duration_weeks: 2` in config |
| Migration | **Yes** - migrate existing PRDs | Phase 5 includes PRD migration |
| Token Budget | **Per-sprint** LLM budgets | `sprint.llm_budget_tokens` field added |
| Archive Policy | **After 3-4 sprints** completed | Auto-archive trigger at sprint 4 |
| Workflow Gate | **VALIDATION state added** | Founder-only approval before DONE |

### Additional Governance Notes

- **VALIDATION State:** All work must pass through Founder validation before being marked DONE
- **Founder Override:** Founder can override any gate at any time
- **No Silent LLM Use:** All LLM work requires explicit approval and budget allocation

---

## Sign-off

| Role | Name | Status | Date |
|------|------|--------|------|
| Design Lead | Tom Brady | AUTHORED | 2026-02-04 |
| Architecture | Brad Stevens | AUTHORED | 2026-02-04 |
| Founder Review | Florentino Perez | **APPROVED** | 2026-02-04 |

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-04 | Initial design (7 states) |
| 1.1 | 2026-02-04 | Added VALIDATION state per Founder directive; resolved open questions |

---

*Mission Control Design v1.1*
*Cricket Playbook Governance*
