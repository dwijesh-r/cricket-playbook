# The Agent Playbook
## How 12 AI Agents Run Cricket Playbook Like a Championship Team

**Owner:** Tom Brady (Product Owner)
**Ticket:** TKT-148 (EPIC-014: Foundation Fortification)
**Version:** 1.0.0

---

## The Setup: A Tale of Two Worlds

Imagine you're building a data analytics system, but instead of one developer grinding through code, you have 12 specialized agents working together like a championship roster. Some are star players who execute the gameplan. Others are coaches who set strategy. And a few are executives who make sure nobody goes off script.

This is the Agent Coding Stack: a structured approach where AI agents with distinct personas, responsibilities, and veto powers collaborate to build robust software. Think of it less like traditional development and more like managing a franchise where every player knows their role and the front office keeps everyone accountable.

---

## The Roster: Meet the 12 Agents

### The Athletes (The Ones Who Ship Code)

**Tom Brady (QB, Product Owner)**
The field general. Brady owns the product vision, writes tickets, and makes calls when requirements get fuzzy. When someone asks "what should this feature actually do?", Brady answers. He doesn't write much code himself, but nothing ships without his signoff on the PRD.

**Brock Purdy (QB, Data Pipeline)**
The young gun handling data flow. Purdy manages everything from raw CSVs to polished DuckDB schemas. Ball-by-ball cricket data? Match metadata? Player dimensions? That's all Purdy's territory. He makes sure data arrives clean, validated, and ready for analysis.

**Stephen Curry (Analytics Lead)**
The sharpshooter for all things analytical. Curry owns thresholds, scoring logic, and the math that turns raw numbers into insights. When you need to know if a strike rate of 145 is "elite" or just "good", Curry's already defined it in `thresholds.yaml`.

**Virat Kohli (Domain Expert)**
The cricket specialist. Kohli ensures every metric, every calculation, every insight actually makes sense in the context of T20 cricket. He's the one who catches when someone tries to calculate a batting average using balls instead of innings. Domain sanity is his beat.

**LeBron James (Visualization & BI)**
The triple threat for dashboards and visualizations. LeBron takes Curry's analytics and makes them consumable. Whether it's depth charts, form curves, or matchup matrices, if a human needs to understand the data, LeBron designs the visual.

**Kevin de Bruyne (Feature Engineering)**
The creative playmaker. KDB sees patterns others miss and engineers features that capture them. Phase-specific metrics, situational modifiers, handedness adjustments: the subtle signals that separate good analysis from great.

**N'Golo Kanté (Quality Assurance)**
The tireless defender. Kanté covers every inch of the codebase looking for bugs, edge cases, and validation gaps. Nothing gets past him. If there's a way for bad data to sneak through, Kanté finds it and patches the hole.

### The Coaches (Strategy and Architecture)

**Andy Flower (Cricket Coaching)**
The tactical mind for cricket methodology. Flower defines what "powerplay beast" means, how to evaluate death bowling, and which matchup patterns actually predict outcomes. He turns cricket intuition into rigorous definitions.

**José Mourinho (Quant Research & Benchmarking)**
The Special One for system evaluation. Mourinho audits the entire system, identifies weaknesses, and scores performance. That "67.4 out of 100" rating? That's Mourinho telling you where the gaps are, with the same directness he'd use in a post-match presser.

**Pep Guardiola (ML Architecture)**
The philosopher of the system. Pep designs the machine learning components: clustering algorithms, dimensionality reduction, drift detection. He thinks three moves ahead about how models will behave under distribution shift.

### The Front Office (Governance and Enforcement)

**Brad Stevens (Architecture & DevOps)**
The operations mastermind. Stevens owns CI/CD, testing infrastructure, and system architecture. He ensures that Pep's elegant algorithms actually run reliably in production. Quality gates? Pre-commit hooks? That's Stevens making sure nobody pushes broken code.

**Florentino Pérez (Governance)**
The president who holds veto power. Pérez doesn't write code. He reviews decisions for strategic alignment. If someone proposes a change that could destabilize the system or violate the Constitution, Pérez steps in. "An offer you can't refuse" works differently here: Florentino's veto means the change doesn't happen until concerns are addressed.

---

## The Task Integrity Loop: Eight Steps to Done

Nothing ships without running the full loop. This isn't bureaucracy for its own sake. It's how you build systems that don't collapse under real-world pressure. Every ticket, every feature, every bug fix follows the same ritual.

### Step 1: The PRD
Tom Brady drafts the Product Requirements Document. What are we building? Why does it matter? What does success look like? No code gets written until the PRD exists and answers these questions.

### Step 2: The Florentino Gate
Before work begins, Florentino reviews the PRD for strategic fit. Does this align with our goals? Does it create technical debt we'll regret? Could it break existing contracts? If Florentino has concerns, the ticket goes back for revision. No exceptions.

### Step 3: The Build
The assigned agent (or agents) write the code. This is where Curry builds thresholds, Purdy designs schemas, or LeBron creates visualizations. Each agent operates within their domain, following established patterns.

### Step 4: Domain Sanity
Virat Kohli reviews the output for cricket domain validity. Do the numbers make sense? Could a strike rate of 847 ever be real? Are we comparing apples to apples? Kohli catches the errors that only a domain expert would recognize.

### Step 5: The Kanté Sweep
N'Golo runs quality checks. Edge cases tested? Validation in place? Error handling correct? Kanté is thorough because production is unforgiving. If there's a bug, he finds it here, not after deployment.

### Step 6: The Commit
Brad Stevens' gates kick in. Pre-commit hooks run linting and formatting. CI pipeline validates thresholds and schemas. If any gate fails, the commit is rejected. The code doesn't merge until it passes every check.

### Step 7: Post Note
The work gets documented. What was built? What decisions were made? Any quirks future developers should know? This isn't optional housekeeping. It's how we maintain institutional memory as the system grows.

### Step 8: System Check
José Mourinho runs the health score. Did this change improve the system or introduce new debt? The score updates, and we see exactly where we stand. 81.5 today. 85 is the target. The gap shrinks with every good commit.

---

## The Playbook: Three Layers of the Stack

### Layer 1: Architect
This is where strategy lives. Pep Guardiola designs ML pipelines. Andy Flower defines cricket methodology. Brad Stevens maps system architecture. These aren't daily coding decisions. They're the foundational choices that shape everything else.

**Key artifacts:**
- `config/CONSTITUTION.md` (the rules of engagement)
- `config/thresholds.yaml` (the single source of truth for all thresholds)
- Architecture decision records in `docs/`

### Layer 2: Code
This is where execution happens. Curry writes analytics functions. KDB engineers features. Purdy builds data pipelines. LeBron designs dashboards. Each agent operates within boundaries set by the Architect layer.

**Key locations:**
- `scripts/core/` (foundational utilities)
- `scripts/analytics/` (statistical calculations)
- `scripts/ml_ops/` (machine learning operations)
- `scripts/viz/` (visualization components)

### Layer 3: Ops
This is where reliability lives. Brad Stevens maintains CI/CD. Kanté enforces testing standards. Mourinho runs audits and benchmarks. The code might be brilliant, but if it doesn't run reliably, it doesn't matter.

**Key infrastructure:**
- `.github/workflows/` (gate enforcement)
- `tests/` (automated testing)
- `scripts/ml_ops/system_health_score.py` (automated scoring)

---

## The Constitution: Laws of the Land

Every franchise needs rules. Ours are documented in `config/CONSTITUTION.md`. These aren't suggestions. They're binding constraints that every agent respects.

**Sample provisions:**

1. **No Magic Numbers.** Every threshold goes in `thresholds.yaml`. If you're typing `if strike_rate > 130`, you're doing it wrong. Use `get_threshold('batting.specialist.strike_rate')`.

2. **Domain Validation Required.** Every data pipeline validates inputs against realistic bounds. Cricket strike rates don't exceed 500. Batting positions stay between 1 and 11. If the data violates physics, we catch it.

3. **Gates Must Pass.** The CI pipeline isn't advisory. Lint errors block merges. Threshold validation blocks merges. Schema checks block merges. No workarounds.

4. **Every Ticket Has an Owner.** Orphan work is how technical debt accumulates. Every ticket names an agent who's accountable for completion.

5. **The Loop Completes.** Partial work doesn't count. A feature isn't done until it passes all eight steps, including documentation and system health check.

---

## The Scoring System: How We Keep Score

José Mourinho doesn't just complain. He quantifies. The system health score measures quality across six categories:

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Governance | 15% | Constitution completeness, gate enforcement, Task Loop documentation |
| Code Quality | 20% | Bare excepts, hardcoded thresholds, type hints, sys.path hacks |
| Data Robustness | 20% | CHECK constraints, domain validation, data lineage |
| ML Rigor | 20% | Baseline comparison, feature importance, model versioning |
| Testing | 15% | Test coverage, integration tests, edge case handling |
| Documentation | 10% | Threshold docs, methodology docs, API documentation |

**Current Score:** 81.5/100
**Target:** 85/100
**Baseline (before EPIC-014):** 67.4/100

The score runs automatically. Every commit either helps or hurts. There's no hiding from the numbers.

---

## The Family: Working Together

Like any good organization, whether it's a sports franchise or a Sicilian family, success depends on clear roles and mutual respect. Here's how conflicts get resolved:

**Domain Disputes:** Virat Kohli has final say on cricket logic. If Curry's threshold doesn't match cricket reality, Kohli's objection wins.

**Architecture Disputes:** Pep Guardiola owns ML design. Brad Stevens owns infrastructure. When they conflict, they negotiate, but neither can unilaterally override the other's domain.

**Strategic Disputes:** Florentino Pérez holds the veto. If a decision threatens system stability or violates the Constitution, Florentino can block it. His veto isn't a conversation ender. It's a signal that concerns must be addressed before proceeding.

**Quality Disputes:** Kanté's findings are facts, not opinions. If he identifies a bug or edge case, it gets fixed. There's no "we'll address it later" for quality issues.

---

## Getting Started: Your First Play

New to the system? Here's how to contribute:

1. **Read the Constitution.** Understand the rules before you try to play the game.

2. **Check the Health Score.** Run `python scripts/ml_ops/system_health_score.py` to see where we stand.

3. **Review Active Tickets.** Open Mission Control (`scripts/mission_control/dashboard/index.html`) to see current work.

4. **Follow the Loop.** Every contribution follows all eight steps. No shortcuts.

5. **Respect the Roster.** Know which agent owns what. Don't step on another agent's domain without coordination.

---

## The Philosophy: Why This Works

Traditional development treats AI as a tool. You prompt, it responds, you iterate. But that misses the opportunity for something more structured. By giving agents distinct personas, clear responsibilities, and genuine authority within their domains, we create something closer to a real team.

Tom Brady doesn't pretend to be a data engineer. Brock Purdy doesn't pretend to own product strategy. Each agent excels at their specialty because they're not trying to be everything. The Task Integrity Loop ensures nothing falls through the cracks. The Constitution prevents drift. The scoring system keeps everyone honest.

Is it more complex than just prompting an AI? Yes. Is it more reliable? Also yes. When you're building systems that matter, reliability wins.

---

## The Numbers Don't Lie

Since implementing EPIC-014 (Foundation Fortification):

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| System Health Score | 67.4 | 81.5 | +14.1 |
| Bare Except Handlers | 40+ | 2 | -95% |
| Hardcoded Thresholds | 50+ | 0 | -100% |
| CI Gates Enforced | No | Yes | New |
| Domain Validation | Partial | Full | Complete |

The work isn't done. Integration tests need expansion. Model registry needs implementation. But the trajectory is clear. Every sprint, the score goes up. Every ticket closed is another step toward the target.

---

## Final Thought

In the Godfather, Michael Corleone says "It's not personal. It's strictly business." In our system, quality isn't personal either. It's not about which agent wrote the code or who's feelings might be hurt by a failed gate. The system health score doesn't play favorites. The Task Integrity Loop doesn't care about convenience.

That's the point. When you build with rigor, when every agent knows their role, when governance is real and not just documented, you get systems that actually work. Not just today, but tomorrow, and the day after that.

Welcome to the team. Now let's get that score to 85.

---

*"Leave the gun. Take the thresholds.yaml."*
