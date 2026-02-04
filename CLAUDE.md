# CLAUDE.md

**Version:** 1.0
**Last Updated:** 2026-02-04

## Project Operating Principles

This repository uses a multi-agent workflow with explicit roles, task ownership, and validation loops.
Agents are expected to operate within defined responsibilities and surface uncertainty early.

**Binding Governance Document:** [Constitution v2.0](config/CONSTITUTION.md)

---

## Quick Links

| Item | Location |
|------|----------|
| Governance | `config/CONSTITUTION.md` |
| PRD | `docs/PRD_CRICKET_PLAYBOOK.md` |
| Task Integrity | `governance/TASK_INTEGRITY_LOOP.md` |
| Agent Configs | `config/agents/` |
| Sprint Response | `reviews/founder/sprint_4_checkin_response_020426_v1.md` |

---

## Mission Control (Guiding)

Mission Control is the primary **task integrity and coordination layer** for this project.
It functions like a lightweight, local JIRA-style system for agents, making work visible, auditable,
and governed without introducing autonomous decision-making.

All meaningful work is expected to flow through Mission Control tickets.

### What Mission Control Is Used For

- Tracking projects, tickets, and subtasks (EPIC → Ticket → Subtask)
- Enforcing clear ownership across scope, execution, and validation
- Making token-heavy (LLM-required) work explicit and manually approved
- Providing visibility into progress, blockers, and % completion
- Supporting sprint planning, reviews, and retrospectives

Mission Control does **not** think, plan, or decide — it coordinates.

---

## Schema Governance (Guiding)

The Mission Control schema (tasks, subtasks, approvals, agent status, execution logs) is
**designed and owned by Tom Brady**, with **review and feedback by Brad Stevens**.

Agents may propose schema changes when needed, but should avoid independently introducing
or modifying structural fields, relationships, or workflow-critical logic.

### Material Changes (Require Founder Sign-off)

Schema changes that materially affect:
- Workflow state transitions
- Approval or validation gates
- Progress metrics or reporting
- Role-permission mappings

are expected to receive **explicit Founder sign-off** before adoption.

### Non-Material Changes (Tom Brady Can Approve)

- Display formatting
- Optional metadata fields
- UI/UX improvements without workflow impact

### Intent

This guidance exists to prevent silent schema drift and ensure that Mission Control remains
robust, auditable, and aligned with long-term governance goals.

When in doubt, propose early rather than optimize locally.

---

## Repository Conventions

### File Locations

| Content Type | Location |
|--------------|----------|
| Analytics outputs | `outputs/` |
| Team stat packs | `stat_packs/` |
| Scripts | `scripts/` (with subdirectories by type) |
| Documentation | `docs/` |
| Founder reviews | `reviews/founder/` |

### Document Naming Convention

For formal deliverables: `documentname_MMDDYY_v*`

Examples:
- `sprint_4_checkin_response_020426_v1.md`
- `founder_review_013026_v1.pdf`

Exempt from convention: `README.md`, `CONSTITUTION.md`, config files

### Commit Messages

Format: `[scope]: brief description`

Examples:
- `[analytics]: add batter consistency index`
- `[stat_packs]: regenerate with 2023 data`
- `[docs]: update PRD with new views`

### Before Committing

1. Run `pytest` - all tests must pass
2. Run `ruff check .` - no linting errors
3. Update relevant README if adding new files

---

## One-Line Reminder

> **If a change affects how work is tracked, approved, or measured, surface it to Tom Brady and Brad Stevens before implementing.**

---

*Cricket Playbook v4.0.0*
