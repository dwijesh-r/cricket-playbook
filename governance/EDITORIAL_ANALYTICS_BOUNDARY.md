# Editorial vs Analytics Boundary

**Version:** 1.0.0
**Owner:** Brad Stevens
**Date:** 2026-02-01
**Reference:** Constitution v2.0, Mega Review #1

---

## Purpose

This document defines the clear separation between Editorial and Analytical work to prevent:
- Scope creep between teams
- Analytics writing final prose
- Editorial making data methodology decisions
- Confusion about ownership

---

## Team Definitions

### Editorial Team
| Agent | Primary Role |
|-------|--------------|
| **Virat Kohli** | Editor-in-Chief, final prose, stat pack presentation |
| **Kevin de Bruyne** | Data visualization, charts, diagrams |
| **LeBron James** | Cross-team coordination, reader perspective |

**Mission:** Transform analytical outputs into magazine-style content with confidence, narrative clarity, and authority.

### Analytical Team
| Agent | Primary Role |
|-------|--------------|
| **Stephen Curry** | Analytics Lead, SQL, algorithms, data generation |
| **Brock Purdy** | QA Engineer, data quality, validation |
| **Ime Udoka** | Infrastructure, ML Ops, model documentation |

**Mission:** Generate accurate, validated data outputs that power editorial content.

### Domain Team (Bridge)
| Agent | Primary Role |
|-------|--------------|
| **Andy Flower** | Cricket Domain Expert, cricket truth validation |
| **Jose Mourinho** | Data Robustness Guardian, baseline clarity |
| **Pep Guardiola** | System Architect, structural coherence |

**Mission:** Ensure analytical outputs are cricket-valid and editorial content is defensible.

---

## What Each Team Does

### Analytics Team DOES:
- Write SQL queries and Python scripts
- Generate CSV/JSON output files
- Define thresholds with EDA evidence
- Calculate metrics and statistics
- Build algorithms (Predicted XI, clustering)
- Document data methodology
- Create technical READMEs for outputs

### Analytics Team DOES NOT:
- Write prose for stat packs
- Make editorial decisions about emphasis
- Choose which insights to highlight
- Write reader-facing documentation
- Determine visual presentation
- Make final calls on player narratives

### Editorial Team DOES:
- Write all reader-facing prose
- Decide section structure and flow
- Choose which data points to emphasize
- Create narrative framing
- Ensure voice consistency
- Write tactical insights section
- Review reader experience

### Editorial Team DOES NOT:
- Write SQL or Python code
- Modify data generation logic
- Change threshold definitions
- Create new metrics
- Run data validation
- Modify output schemas

---

## Handoff Process

### Analytics → Editorial (Graduation)

```
┌─────────────────────────────────────────────────────────────┐
│                    GRADUATION PROCESS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Stephen Curry: Creates output with evidence             │
│         ↓                                                   │
│  2. Andy Flower: Validates cricket truth                    │
│         ↓                                                   │
│  3. Virat Kohli: Confirms editorial value                   │
│         ↓                                                   │
│  4. Florentino Perez: Approves for paid artifact            │
│         ↓                                                   │
│  5. Tom Brady: Schedules for stat pack inclusion            │
│         ↓                                                   │
│  6. Virat Kohli: Writes editorial prose                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### What Gets Handed Off

| From Analytics | To Editorial |
|----------------|--------------|
| `outputs/player_tags_2023.json` | Tag labels to embed in tables |
| `outputs/matchups/*.csv` | Matchup data for head-to-head sections |
| `outputs/metrics/*.csv` | Performance numbers for all sections |
| Algorithm output (Predicted XI) | XI with reasoning to explain |
| Threshold documentation | Context for editorial claims |

### What Does NOT Get Handed Off

| Analytics Keeps | Editorial Cannot Modify |
|-----------------|------------------------|
| SQL query logic | Data generation code |
| Threshold values | Metric calculations |
| Schema definitions | Output file structure |
| Validation rules | Data quality tests |

---

## Boundary Rules

### Rule 1: Analytics Does Not Write Final Prose
> "Stephen Curry generates the Predicted XI algorithm output. Virat Kohli writes the explanation of why this XI makes sense."

**Bad:** Stephen Curry writes "This XI maximizes boundary% while maintaining bowling depth."
**Good:** Stephen Curry outputs `{xi: [...], metrics: {...}}`. Virat Kohli writes the prose.

### Rule 2: Editorial Does Not Change Data Logic
> "Virat Kohli cannot ask 'Can we make Kohli look better by changing the threshold?'"

If editorial disagrees with data:
1. Raise with Andy Flower (cricket truth)
2. If Andy agrees, raise with Stephen Curry
3. Stephen Curry evaluates with EDA
4. Data change follows full Task Integrity Loop

### Rule 3: Domain Team Is The Bridge
> "Andy Flower can say 'This data is correct but the editorial framing is misleading' AND 'This editorial claim cannot be supported by data.'"

Domain team has veto on:
- Cricket truth violations (Andy Flower)
- Data robustness issues (Jose Mourinho)
- System contradictions (Pep Guardiola)

### Rule 4: README Ownership
| README Type | Owner |
|-------------|-------|
| Technical output READMEs | Stephen Curry |
| User-facing documentation | Virat Kohli |
| Methodology documentation | Andy Flower |
| API/schema documentation | N'Golo Kanté |

### Rule 5: Visualization Ownership
| Visual Type | Creator | Reviewer |
|-------------|---------|----------|
| Data charts (matplotlib) | Kevin de Bruyne | Stephen Curry |
| Stat pack tables | Virat Kohli | Stephen Curry |
| Architecture diagrams | Kevin de Bruyne | Brad Stevens |
| Flow diagrams | Kevin de Bruyne | Pep Guardiola |

---

## Conflict Resolution

### When Analytics and Editorial Disagree

1. **First:** Andy Flower mediates (cricket expertise)
2. **Second:** Tom Brady arbitrates (process)
3. **Third:** Florentino Perez decides (value)
4. **Final:** Founder override (if needed)

### Common Conflicts

| Conflict | Resolution |
|----------|------------|
| "This insight isn't interesting" | Editorial decides what to emphasize, but cannot suppress accurate data |
| "This data seems wrong" | Analytics investigates, Domain validates |
| "We need a new metric" | Analytics scopes, Domain validates, Florentino gates |
| "The prose misrepresents the data" | Domain flags, Editorial revises |

---

## Checklist for Handoffs

### Analytics → Editorial Handoff
- [ ] Output files generated and validated
- [ ] Technical README complete
- [ ] Methodology documented
- [ ] Andy Flower cricket truth: YES
- [ ] Jose Mourinho robustness: YES
- [ ] Sample interpretations provided (not final prose)

### Editorial Acceptance
- [ ] Received output files
- [ ] Understood methodology
- [ ] Identified editorial angles
- [ ] Confirmed no data questions remain
- [ ] Ready to write prose

---

## Examples

### Good Collaboration

**Analytics:** "Here's the Predicted XI output with role fit scores, boundary%, and bowling depth metrics."

**Domain:** "The XI makes cricket sense. The algorithm correctly identified the need for a left-arm spinner."

**Editorial:** "I'll frame this as 'The algorithm reveals a hidden weakness: no left-arm spin option forces tactical compromise.'"

### Bad Collaboration

**Analytics:** "I wrote the tactical insights section because I had the data."
❌ Violates Rule 1

**Editorial:** "Can we change the death-overs threshold from 16 to 18 so more players qualify?"
❌ Violates Rule 2

**Analytics:** "The editorial made this sound too negative, can we change the numbers?"
❌ Both violate boundaries

---

*Editorial vs Analytics Boundary v1.0.0*
*Brad Stevens, Architecture Lead*
*2026-02-01*
