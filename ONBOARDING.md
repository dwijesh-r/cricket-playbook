# ONBOARDING.md - Model Transition Context

**Read This First** | Last Updated: 2026-02-06 | Version: 1.0

---

## What Is This Project?

**Cricket Playbook** is an IPL 2026 pre-season analytics platform that provides:
- Team stat packs with performance breakdowns
- Predicted XIs using the SUPER SELECTOR algorithm
- Depth charts for all 10 IPL teams
- Player clustering and matchup analysis

**Live Dashboards:**
- [The Lab](https://dwijesh-r.github.io/cricket-playbook/scripts/the_lab/dashboard/) - Analytics views
- [The Boardroom](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/) - Project management

---

## Current State (Updated Each Session)

### Sprint Info
| Field | Value |
|-------|-------|
| Current Sprint | Sprint 4 |
| Sprint Dates | Jan 31 - Feb 14, 2026 |
| Primary Focus | Predicted XIIs, Depth Charts, UI/UX |

### Active Work
| Status | Count | Key Items |
|--------|-------|-----------|
| RUNNING | 5 | TKT-032 (data dictionary), TKT-049/050 (stat pack sections), TKT-070 (model versioning), TKT-082 (refactor) |
| VALIDATION | 7 | Awaiting Founder (🌹) review - depth charts, predicted XIIs, script quality |
| BLOCKED | 0 | None |

### Recent Commits
```
fc8ae29 [Tom Brady] Fix Andy Flower team in about.html
eb44f83 [Tom Brady] Roster improvements: Show all agents + running/blocked counts
2d34791 [Tom Brady + Kevin de Bruyne] Nav guides + Timer + Mission Control layout fixes
```

---

## The Agent System

This project uses **14 AI agents** with sports personas. Each has defined responsibilities:

### Leadership
| Agent | Role | Responsibility |
|-------|------|----------------|
| **Tom Brady** | Product Owner | Delivery, tickets, documentation, sprint planning |
| **Florentino Pérez** | Program Director | Governance, approvals, Florentino Gate |
| **Founder (🌹)** | You | Final approval on all VALIDATION tickets |

### Execution
| Agent | Role | Specialty |
|-------|------|-----------|
| **Stephen Curry** | Analytics Lead | Algorithms, metrics, SUPER SELECTOR |
| **Kevin de Bruyne** | Visualization | UI/UX, wireframes, dashboards |
| **Brock Purdy** | Data Pipeline | Data quality, ingestion, validation |
| **Brad Stevens** | Architecture | Code quality, refactoring, ops |
| **Ime Udoka** | DevOps | MLOps, CI/CD, model registry |

### Validation
| Agent | Role | Specialty |
|-------|------|-----------|
| **Andy Flower** | Cricket Domain | Validates cricket logic and realism |
| **José Mourinho** | Data Science | Critical review, bias detection |
| **N'Golo Kanté** | QA Lead | Data integrity, can BLOCK publication |
| **Virat Kohli** | Editorial | Tone, narrative, fan engagement |

### Advisory
| Agent | Role |
|-------|------|
| **LeBron James** | Social & Engagement |
| **Pep Guardiola** | Tactical Analysis |

---

## Key Documents to Read

### Must Read (Start Here)
1. **[CLAUDE.md](./CLAUDE.md)** - Operating principles and conventions
2. **[docs/INDEX.md](./docs/INDEX.md)** - Complete file index
3. **[config/CONSTITUTION.md](./config/CONSTITUTION.md)** - Governance framework

### For Current Work
4. **[governance/TASK_INTEGRITY_LOOP.md](./governance/TASK_INTEGRITY_LOOP.md)** - 8-step quality process
5. **[docs/sprints/SPRINT_4_STATUS_020426.md](./docs/sprints/SPRINT_4_STATUS_020426.md)** - Current sprint status

### For Analytics Work
6. **[docs/SUPER_SELECTOR.md](./docs/SUPER_SELECTOR.md)** - Predicted XI algorithm
7. **[docs/PRD_CRICKET_PLAYBOOK.md](./docs/PRD_CRICKET_PLAYBOOK.md)** - Product requirements

---

## Task Integrity Loop (Quick Reference)

All work follows this 8-step process:

```
1. IDEA        → Initial concept
2. BACKLOG     → Approved for sprint
3. READY       → Florentino Gate passed, ready to start
4. RUNNING     → Active development
5. BLOCKED     → Waiting on dependency
6. REVIEW      → Domain + System checks
7. VALIDATION  → 🌹 Founder Review required
8. DONE        → Shipped
```

**Gates:**
- **Florentino Gate** (Step 3): Scope approval before work begins
- **Domain Sanity** (Review): Andy Flower / José / Pep validates cricket logic
- **System Check** (Review): N'Golo Kanté validates data integrity
- **Founder Sign-off** (Step 7): You approve before DONE

---

## Repository Structure (Quick Reference)

```
cricket-playbook/
├── CLAUDE.md           # Operating principles
├── ONBOARDING.md       # THIS FILE - read first
├── config/agents/      # 14 agent configurations
├── docs/               # All documentation
├── governance/         # Task Integrity Loop, Constitution
├── outputs/            # Generated stat packs, depth charts, predicted XIIs
├── scripts/
│   ├── mission_control/dashboard/  # The Boardroom
│   └── the_lab/dashboard/          # The Lab
└── stat_packs/         # Team stat packs (10 teams)
```

---

## How to Continue Work

### If Resuming Active Work:
1. Check The Boardroom for ticket status: `scripts/mission_control/dashboard/index.html`
2. Look at RUNNING tickets - pick up where left off
3. Use `git log --oneline -10` to see recent changes

### If Starting Fresh:
1. Review VALIDATION tickets awaiting Founder approval
2. Check for any BLOCKED items
3. Ask the Founder for priorities

### For Any New Task:
1. Create a ticket in Mission Control (if doesn't exist)
2. Follow Task Integrity Loop
3. Get Florentino Gate approval before starting
4. Surface blockers early

---

## Active Plans (In Progress)

| Plan File | Description | Status |
|-----------|-------------|--------|
| `resilient-bouncing-jellyfish.md` | The Lab Intro Animation (attire, surfaces, floodlights) | Pending |
| `misty-honking-clarke.md` | IPL 2026 Player Analysis (SQL views, data collection) | Pending |

These are in `~/.claude/plans/` - can be resumed or archived.

---

## Quick Commands

```bash
# Check project status
git status
git log --oneline -10

# Run tests before committing
pytest

# Check linting
ruff check .

# View dashboards locally
open scripts/the_lab/dashboard/index.html
open scripts/mission_control/dashboard/index.html
```

---

## Contact Points

| Role | Agent | For |
|------|-------|-----|
| Project Lead | Tom Brady | Tickets, planning, delivery |
| Final Approval | Founder (🌹) | All VALIDATION items |
| Domain Questions | Andy Flower | Cricket logic |
| Data Issues | Brock Purdy | Pipeline, data quality |
| UI/UX | Kevin de Bruyne | Dashboard, visualizations |

---

## One-Line Summary

> **Cricket Playbook is an IPL analytics platform with 14 AI agents, currently in Sprint 4, with 7 tickets awaiting Founder review and 5 tickets actively running.**

---

*This document should be updated at the end of each significant work session to maintain accurate context for model transitions.*
