# How Does This All Work?

**A One-Page Guide for Outsiders**

---

## What Is Cricket Playbook?

A **pre-tournament preview magazine** for IPL cricket. Think Lindy's Sports Annual or Phil Steele's College Football Preview, but for cricket.

We produce **stat packs** for all 10 IPL teams with:
- Squad analysis and depth charts
- Player roles and matchups
- Phase-by-phase breakdowns
- Tactical insights

**What we're NOT:** A prediction service, betting tool, or live commentary platform.

---

## The Team (Agents)

We operate with specialized AI agents, each with a defined role:

### Who Does What

| Agent | Role | What They Do |
|-------|------|--------------|
| **Florentino Perez** | Strategic Gatekeeper | Decides what gets built (value filter) |
| **Tom Brady** | Product Owner | Runs sprints, approves work, enforces process |
| **Andy Flower** | Cricket Expert | Validates cricket accuracy |
| **Stephen Curry** | Analytics Lead | Builds SQL views, clustering, tags |
| **Virat Kohli** | Editorial Lead | Writes stat pack content |
| **Brad Stevens** | Architecture | Code quality, agent performance |
| **Brock Purdy** | Data Pipeline | Data ingestion and quality |
| **N'Golo Kanté** | QA Engineer | Testing and validation |

---

## How Work Flows

```
Idea → Florentino Gate → Build → Domain Review → Ship → Document
```

### The Task Integrity Loop (8 Steps)

Every task must pass through:

| Step | What Happens | Who Decides |
|------|--------------|-------------|
| 0 | Write a PRD (what & why) | Requester |
| 1 | **Florentino Gate**: Does this improve the product? | Florentino Perez |
| 2 | Build it (within scope only) | Assigned agent |
| 3 | **Domain Sanity**: Is it robust? Cricket-true? Coherent? | Jose Mourinho, Andy Flower, Pep Guardiola |
| 4 | **Enforcement**: Was process followed? | Tom Brady |
| 5 | Commit to main | Assigned agent |
| 6 | Document what changed | Assigned agent |
| 7 | System check (tests pass?) | N'Golo Kanté |

**No shortcuts.** Every task goes through this loop.

---

## Where Things Live

| You Want | Go Here |
|----------|---------|
| Final product (stat packs) | `stat_packs/*.md` |
| Player tags and clusters | `outputs/tags/` |
| Matchup analysis | `outputs/matchups/` |
| Raw data and database | `data/` |
| Python scripts | `scripts/` |
| Process docs | `governance/` |
| Sprint planning | [Mission Control Dashboard](https://dwijesh-r.github.io/cricket-playbook/scripts/mission_control/dashboard/index.html) |

---

## Review System

### Types of Reviews

| Review | Purpose | Who |
|--------|---------|-----|
| **Florentino Gate** | Does this add value? | Florentino Perez |
| **Domain Sanity** | Is this correct and coherent? | Andy Flower, Jose Mourinho, Pep Guardiola |
| **Founder Review** | Strategic direction check | Founder |
| **Sprint Review** | What got done, what's next | Tom Brady |

### Approval Chain

```
Agent proposes → Florentino approves scope → Domain validates → Tom Brady enforces → Founder can override anything
```

---

## What Goes Into Stat Packs

| Section | What It Contains |
|---------|------------------|
| Squad Overview | Roster with roles, tags, contracts |
| Depth Charts | Best options per position |
| Predicted XI | Algorithm-recommended lineup |
| Key Batters | Stats, phase performance, matchups |
| Key Bowlers | Stats, phase performance, tendencies |
| Tactical Insights | Andy Flower's strategic analysis |

---

## Quality Rules

### Every Metric Must Have

1. **A baseline** - What's the league average?
2. **A sample size indicator** - HIGH / MEDIUM / LOW confidence
3. **Clear interpretation** - What does this mean for a fan?

### Content Rules

- ✅ Strong opinions backed by data
- ✅ Actionable insights
- ❌ No predictions or probabilities
- ❌ No hallucinated stats
- ❌ No black-box claims

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Data window | IPL 2023-2025 (219 matches) |
| Teams covered | 10 |
| Players in squads | 231 |
| Analytics views | 34 |
| Batter archetypes | 6 |
| Bowler archetypes | 7 |

---

## If You're Contributing

1. **Read the Constitution** (`config/CONSTITUTION.md`)
2. **Follow the Task Integrity Loop** (`governance/TASK_INTEGRITY_LOOP.md`)
3. **Get Florentino Gate approval** before building anything
4. **Document everything** - READMEs, post-task notes

---

## Who Owns What

| Area | Owner |
|------|-------|
| Overall product | Tom Brady |
| Scope decisions | Florentino Perez |
| Cricket accuracy | Andy Flower |
| Analytics | Stephen Curry |
| Editorial content | Virat Kohli |
| Code quality | Brad Stevens |
| Data pipeline | Brock Purdy |
| Testing | N'Golo Kanté |

---

## Quick Links

- [Main README](../README.md)
- [Constitution](../config/CONSTITUTION.md)
- [Task Integrity Loop](../governance/TASK_INTEGRITY_LOOP.md)
- [Sprint Board](KANBAN.md)
- [Stat Packs](../stat_packs/)

---

*Cricket Playbook - How It Works*
