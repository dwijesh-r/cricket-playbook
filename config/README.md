# Config

Agent definitions, templates, and framework guidelines.

**Version:** 3.1.0 | **Last Updated:** 2026-01-26

---

## Directory Structure

```
config/
├── README.md           # This file
├── CONSTITUTION.md     # Agent framework and guidelines
├── agents/             # Agent persona definitions (12 agents)
│   ├── tom-brady.agent.md
│   ├── stephen-curry.agent.md
│   ├── andy-flower.agent.md
│   ├── brock-purdy.agent.md
│   ├── n-golo-kante.agent.md
│   ├── brad-stevens.agent.md
│   ├── ime-udoka.agent.md
│   ├── kevin-de-bruyne.agent.md
│   ├── virat-kohli.agent.md
│   ├── pep-guardiola.agent.md
│   ├── lebron-james.agent.md
│   └── jayson-tatum.agent.md
└── templates/          # Output templates
    ├── MAGAZINE_TEMPLATE.md
    └── METRIC_PACK.md
```

---

## Agent Roster

### Core Team

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Tom Brady** | Product Owner | Sprint planning, PRD, stakeholder coordination, KANBAN |
| **Stephen Curry** | Analytics Lead | SQL views, clustering models, tag generation, EDA |
| **Andy Flower** | Cricket Domain Expert | Cluster validation, tactical insights, threshold review |
| **Brock Purdy** | Data Pipeline | Ingestion, schema validation, data quality, ETL |
| **N'Golo Kanté** | QA Engineer | Test suite, smoke tests, regression testing |
| **Brad Stevens** | Architecture | CI/CD, code quality, repo structure, best practices |

### Specialist Team

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Ime Udoka** | ML Ops Engineer | Model registry, deployment, versioning, research |
| **Kevin de Bruyne** | Visualization | Charts, dashboards, visual outputs |
| **Virat Kohli** | Editorial | Stat pack content, narrative insights |

### Extended Team

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Pep Guardiola** | Strategy | Tactical analysis, team composition |
| **LeBron James** | Leadership | Cross-team coordination |
| **Jayson Tatum** | Development | Feature implementation |

---

## Agent Workflows

### Model Development
```
Stephen Curry (builds model)
    → Andy Flower (validates labels)
    → N'Golo Kanté (writes tests)
    → Ime Udoka (registers in ml_ops)
```

### Data Pipeline
```
Brock Purdy (ingests data)
    → Stephen Curry (creates views)
    → N'Golo Kanté (validates schema)
    → Tom Brady (approves for production)
```

### Founder Reviews
```
Founder (submits review PDF)
    → Tom Brady (triages issues)
    → Stephen Curry (implements fixes)
    → N'Golo Kanté (writes regression tests)
    → Andy Flower (validates cricket accuracy)
```

### Sprint Management
```
Tom Brady (creates sprint plan)
    → Brad Stevens (reviews architecture)
    → Team (executes tasks)
    → Tom Brady (closes sprint, updates KANBAN)
```

---

## Templates

| Template | Description | Usage |
|----------|-------------|-------|
| `MAGAZINE_TEMPLATE.md` | IPL magazine article structure | Editorial content |
| `METRIC_PACK.md` | Stat pack section structure | Team reports |

---

## Constitution

The `CONSTITUTION.md` file defines:
- Agent interaction protocols
- Decision-making hierarchy
- Quality gates and approvals
- Communication guidelines

---

*Cricket Playbook v3.1.0*
