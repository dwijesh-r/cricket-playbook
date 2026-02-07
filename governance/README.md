# Governance

Process documentation and task tracking for Cricket Playbook.

**Version:** 2.0.0 | **Last Updated:** 2026-02-05

---

## Mission Control Integration

**All sprint tasks MUST be tracked on Mission Control.**

**Live Dashboard:** [https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/)

**Owner:** Tom Brady is responsible for ensuring all sprint tasks:
1. Have corresponding Mission Control tickets
2. Follow the Task Integrity Loop
3. Are reflected accurately on the board

See `MISSION_CONTROL_DESIGN_020426_v1.md` for full design spec.

---

## Directory Structure

```
governance/
├── README.md                           # This file
├── TASK_INTEGRITY_LOOP.md              # 8-step quality process (v1.2.0)
├── MISSION_CONTROL_DESIGN_020426_v1.md # Mission Control design spec
├── templates/                          # Document templates
│   └── TASK_PRD_TEMPLATE.md            # Task PRD template
└── tasks/                              # Active task PRDs
```

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `TASK_INTEGRITY_LOOP.md` | Mandatory 8-step process for all tasks |
| `MISSION_CONTROL_DESIGN_020426_v1.md` | Mission Control design specification |
| `templates/TASK_PRD_TEMPLATE.md` | Template for task declarations |

---

## Quick Reference

### Task Integrity Loop Steps

| Step | Name | Owner | Mission Control |
|------|------|-------|-----------------|
| 0 | Task Declaration (PRD) | Requester | `mc ticket create` |
| 1 | Florentino Gate | Florentino Perez | `mc approve florentino` |
| 2 | Build | Assigned Agent | State → RUNNING |
| 3 | Domain Sanity Loop | Jose Mourinho, Andy Flower, Pep Guardiola | `mc approve domain-sanity` |
| 4 | Enforcement Check | Tom Brady | State → REVIEW |
| 5 | System Check | N'Golo Kanté | `mc approve system-check` |
| 6 | Founder Validation | Founder | `mc approve founder` |
| 7-8 | Commit and Ship | Assigned Agent | State → DONE |

### Golden Rule

> **If it's not on the board, it didn't happen.**

---

## Related Documents

- [Constitution](../config/CONSTITUTION.md) - Authority and rules
- [CLAUDE.md](../CLAUDE.md) - Project operating principles
- [Mission Control README](../.mission-control/README.md) - CLI documentation
- [Mission Control](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/index.html) - Sprint tracking

---

*Cricket Playbook Governance v2.0.0*
