# CLAUDE.md

**Version:** 1.1
**Last Updated:** 2026-02-08

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
| Agent Playbook | `docs/AGENT_PLAYBOOK.md` |
| Thresholds | `config/thresholds.yaml` |
| System Health | `scripts/ml_ops/system_health_score.py` |
| Agent Configs | `config/agents/` |
| Sprint Response | `reviews/founder/sprint_4_checkin_response_020426_v1.md` |

---

## Mission Control (Guiding)

Mission Control is the primary **task integrity and coordination layer** for this project.
It functions like a lightweight, local JIRA-style system for agents, making work visible, auditable,
and governed without introducing autonomous decision-making.

**Live Dashboard:** [https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/)

All meaningful work is expected to flow through Mission Control tickets.

### What Mission Control Is Used For

- Tracking projects, tickets, and subtasks (EPIC → Ticket → Subtask)
- Enforcing clear ownership across scope, execution, and validation
- Making token-heavy (LLM-required) work explicit and manually approved
- Providing visibility into progress, blockers, and % completion
- Supporting sprint planning, reviews, and retrospectives

Mission Control does **not** think, plan, or decide — it coordinates.

### Sprint Tasks → Mission Control Board (MANDATORY)

**Owner: Tom Brady**

All sprint-related tasks **MUST**:

1. **Go through the Task Integrity Loop** - No exceptions. Every task follows the 8-step quality process (see `governance/TASK_INTEGRITY_LOOP.md`)
2. **Have a corresponding ticket created** - Before work begins, a ticket must exist in Mission Control
3. **Reflect on the board** - The dashboard must show current state at all times

| Responsibility | Owner | Action |
|----------------|-------|--------|
| Ticket creation for sprint tasks | **Tom Brady** | Create TKT-XXX before sprint begins |
| Board accuracy | **Tom Brady** | Ensure tickets reflect actual work state |
| Task Integrity enforcement | **Tom Brady** | Verify all gates passed before DONE |
| Sprint-to-board sync | **Tom Brady** | Every KANBAN item = Mission Control ticket |

**If it's not on the board, it doesn't exist.** This is non-negotiable for sprint work.

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

### Branching Strategy (Effective 2026-02-08)

**All non-trivial work MUST use feature branches.** Never commit multi-file or ticket work directly to `main`.

1. Create branch: `git checkout -b feature/TKT-xxx-description`
2. Do work, commit on branch
3. Push and open PR: `gh pr create --title "TKT-xxx: Description"`
4. CI runs automatically on PR
5. Merge after checks pass, delete branch

Branch naming: `feature/TKT-xxx-*`, `fix/TKT-xxx-*`, `data/*`, `docs/*`, `hotfix/*`

**Exceptions (direct to main):** Single-line typos, config-only changes, emergency workflow fixes.

See `docs/cicd_best_practices.md` Section 5.1 for full details.

### Commit Messages

Format: `[scope]: brief description`

Examples:
- `[analytics]: add batter consistency index`
- `[stat_packs]: regenerate with 2023 data`
- `[docs]: update PRD with new views`

### Before Committing

1. Run `pytest` - all tests must pass
2. Run `ruff check .` - no linting errors
3. Run `python scripts/ml_ops/system_health_score.py` - target 85+
4. Update relevant README if adding new files

---

## Automation Coverage (Brad Stevens)

All meaningful work is automated through GitHub Actions workflows:

| Workflow | Trigger | Purpose | Owner |
|----------|---------|---------|-------|
| `ci.yml` | Push/PR | Lint, format, tests | Brad Stevens |
| `gate-check.yml` | Push/PR | Quality gates enforcement | Brad Stevens |
| `generate-outputs.yml` | Daily + post-gate | Stat packs, depth charts, XIIs | Brad Stevens |
| `deploy-dashboard.yml` | Post-outputs | The Lab data update | Brad Stevens |
| `ingest.yml` | Weekly + manual | Data ingestion from Cricsheet | Brock Purdy |
| `ml-health-check.yml` | Weekly + push | ML model monitoring | Ime Udoka |

**Current Automation Coverage:** 82% (target: 90%)

**Workflow Chain:**
```
Push to main → gate-check → generate-outputs → deploy-dashboard
                   ↓
            Tests + Lint + Schema + Domain validation
```

---

## System Health Score (José Mourinho)

The system is measured across 6 categories with weighted scoring:

| Category | Weight | Current | Target |
|----------|--------|---------|--------|
| Governance | 15% | 100% | 100% |
| Code Quality | 20% | 90% | 80% |
| Data Robustness | 20% | 100% | 100% |
| ML Rigor | 20% | 80% | 90% |
| Testing | 15% | 100% | 80% |
| Documentation | 10% | 100% | 100% |

**Current Score:** 94.0/100 | **Target:** 85/100 (EXCEEDED)

Run: `python scripts/ml_ops/system_health_score.py`

---

## AI Coding Benchmark Compliance

Per José Mourinho's audit (2026-02-10):

| Standard | Compliance | Notes |
|----------|------------|-------|
| Anthropic AI Safety | 97% | World-class agent boundaries |
| Microsoft Responsible AI | 90% | Strong accountability |
| Google ML Best Practices | 82% | SHAP/LIME added (TKT-142 DONE) |

**Known Gaps:**
- Model registry missing (ML Rigor category)
- No token accounting per task

---

## One-Line Reminder

> **If a change affects how work is tracked, approved, or measured, surface it to Tom Brady and Brad Stevens before implementing.**

---

*Cricket Playbook v4.0.0*
