# Configuration

This directory contains project configuration, agent definitions, and templates.

## Structure

```
config/
├── agents/          # Agent persona definitions (12 agents)
├── templates/       # Output templates for stat packs, reports
└── CONSTITUTION.md  # Agent framework and guidelines
```

## Agents

| Agent | Role | Responsibilities |
|-------|------|------------------|
| Tom Brady | Product Owner | Sprint planning, PRD, stakeholder coordination |
| Stephen Curry | Analytics Lead | SQL views, clustering models, tag generation |
| Andy Flower | Cricket Domain Expert | Cluster validation, tactical insights, label review |
| Brock Purdy | Data Pipeline | Ingestion, schema validation, data quality |
| N'Golo Kanté | QA Engineer | Test suite, smoke tests, regression testing |
| Brad Stevens | Requirements & Architecture | CI/CD, code quality, best practices |
| Ime Udoka | ML Ops Engineer | Model registry, deployment, versioning |
| Kevin de Bruyne | Visualization Editor | Charts, dashboards, visual outputs |
| Virat Kohli | Editorial Agent | Stat pack content, narrative insights |
| Pep Guardiola | Strategy | Tactical analysis, team composition |
| LeBron James | Leadership | Cross-team coordination |
| Jayson Tatum | Development | Feature implementation |

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

---

*Cricket Playbook v2.7.0*
