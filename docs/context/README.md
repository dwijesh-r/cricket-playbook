# Context Files for Model Transition

**Purpose:** Quick access to essential documents for any new Claude Code model.

---

## Read Order (Priority)

### 1. Start Here
| Order | File | Why |
|-------|------|-----|
| 1 | [ONBOARDING.md](../../ONBOARDING.md) | Current state, agents, priorities |
| 2 | [CLAUDE.md](../../CLAUDE.md) | Operating principles, conventions |
| 3 | [docs/INDEX.md](../INDEX.md) | Complete file index |

### 2. Governance
| File | Description |
|------|-------------|
| [CONSTITUTION.md](../../config/CONSTITUTION.md) | Binding governance framework |
| [TASK_INTEGRITY_LOOP.md](../../governance/TASK_INTEGRITY_LOOP.md) | 8-step quality process |

### 3. Current Sprint
| File | Description |
|------|-------------|
| [SPRINT_4_STATUS_020426.md](../sprints/SPRINT_4_STATUS_020426.md) | Sprint status |
| [Mission Control Dashboard](../../scripts/mission_control/dashboard/index.html) | Live ticket board |

### 4. Product
| File | Description |
|------|-------------|
| [PRD_CRICKET_PLAYBOOK.md](../PRD_CRICKET_PLAYBOOK.md) | Product requirements |
| [SUPER_SELECTOR.md](../SUPER_SELECTOR.md) | Predicted XI algorithm |

---

## Agent Configurations

All 14 agents are defined in `config/agents/`:

| Agent | File |
|-------|------|
| Tom Brady | [tom-brady.agent.md](../../config/agents/tom-brady.agent.md) |
| Stephen Curry | [stephen-curry.agent.md](../../config/agents/stephen-curry.agent.md) |
| Andy Flower | [andy-flower.agent.md](../../config/agents/andy-flower.agent.md) |
| Brad Stevens | [brad-stevens.agent.md](../../config/agents/brad-stevens.agent.md) |
| Brock Purdy | [brock-purdy.agent.md](../../config/agents/brock-purdy.agent.md) |
| Kevin de Bruyne | [kevin-de-bruyne.agent.md](../../config/agents/kevin-de-bruyne.agent.md) |
| José Mourinho | [jose-mourinho.agent.md](../../config/agents/jose-mourinho.agent.md) |
| N'Golo Kanté | [n-golo-kante.agent.md](../../config/agents/n-golo-kante.agent.md) |
| Virat Kohli | [virat-kohli.agent.md](../../config/agents/virat-kohli.agent.md) |
| Ime Udoka | [ime-udoka.agent.md](../../config/agents/ime-udoka.agent.md) |
| LeBron James | [lebron-james.agent.md](../../config/agents/lebron-james.agent.md) |
| Pep Guardiola | [pep-guardiola.agent.md](../../config/agents/pep-guardiola.agent.md) |
| Florentino Pérez | [florentino-perez.agent.md](../../config/agents/florentino-perez.agent.md) |

---

## One Command to Get Context

After switching models, run this in Claude Code:

```
Please read ONBOARDING.md to understand the current project state, then read CLAUDE.md for operating principles.
```

Or simply:

```
Read ONBOARDING.md and tell me what you understand about the project.
```

---

*This folder exists to make model transitions seamless. Update ONBOARDING.md at the end of each session.*
