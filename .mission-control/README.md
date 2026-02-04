# 🚀 Mission Control

> "If it's not on the board, it didn't happen."

Welcome to Mission Control — the nerve center of Cricket Playbook operations. This is where chaos becomes clarity, where tickets flow like water through an 8-stage gauntlet, and where no work ships without the Founder's blessing.

---

## 🎬 The 60-Second Pitch

You're running a team of AI agents. They're brilliant but chaotic. Work gets lost. Things ship without review. LLM tokens vanish into the void.

**Mission Control fixes that.**

Every piece of work is a ticket. Every ticket follows the same 8-step journey. Every gate has a gatekeeper. Nothing slips through.

```
💡 IDEA → 📝 BACKLOG → 🎯 READY → 🔄 RUNNING → 👀 REVIEW → ⏳ VALIDATION → ✅ DONE
                                        ↓
                                   🚫 BLOCKED
```

---

## 🏃 Quick Start (2 Minutes)

### Create Your First Ticket

```bash
# The journey begins with an idea
python scripts/mission_control/mc.py ticket create \
  --title "Build the next big thing" \
  --priority P0 \
  --owner "Tom Brady"
```

### Get It Approved (Florentino Gate)

```bash
# Florentino decides: Is this worth our time?
python scripts/mission_control/mc.py approve florentino TKT-001 \
  --status APPROVED \
  --reason "Directly impacts revenue"
```

### Assign to Sprint & Start Work

```bash
# Create a sprint
python scripts/mission_control/mc.py sprint create \
  --title "Sprint 5 - Ship It" \
  --start 2026-02-05 \
  --end 2026-02-19

# Activate it
python scripts/mission_control/mc.py sprint update SPRINT-001 --status ACTIVE

# Assign ticket and start
python scripts/mission_control/mc.py ticket update TKT-001 --sprint SPRINT-001
python scripts/mission_control/mc.py ticket update TKT-001 --state READY --assignee "Stephen Curry"
python scripts/mission_control/mc.py ticket update TKT-001 --state RUNNING
```

### Pass the Gates & Ship

```bash
# Domain expert validates
python scripts/mission_control/mc.py approve domain-sanity TKT-001 \
  --validator andy_flower --status YES

# QA runs the gauntlet
python scripts/mission_control/mc.py approve system-check TKT-001 \
  --status PASS --tests 42/42

# Move to validation
python scripts/mission_control/mc.py ticket update TKT-001 --state REVIEW
python scripts/mission_control/mc.py ticket update TKT-001 --state VALIDATION

# THE FOUNDER SPEAKS 🎤
python scripts/mission_control/mc.py approve founder TKT-001 \
  --status APPROVED \
  --feedback "Ship it. Now."

# 🎉 Auto-transitions to DONE
```

---

## 🗺️ The Task Integrity Loop

Every ticket walks the same path. No shortcuts. No exceptions.

| Step | What Happens | Who Decides | Command |
|------|--------------|-------------|---------|
| **0** | 💡 Idea is born | Anyone | `mc ticket create` |
| **1** | 🚪 Florentino Gate | Product Owner | `mc approve florentino` |
| **2** | 🔨 Build begins | Executor | `mc ticket update --state RUNNING` |
| **3** | 🧠 Domain Sanity | Validators | `mc approve domain-sanity` |
| **4** | 📏 Enforcement Check | Architect | `mc approve enforcement` |
| **5** | ✅ System Check | QA | `mc approve system-check` |
| **6** | 👑 **Founder Validation** | **FOUNDER ONLY** | `mc approve founder` |
| **7-8** | 🚀 Ship & Document | Auto | Happens on approval |

**The Golden Rule:** Only the Founder can move tickets from VALIDATION → DONE.

---

## 📊 Views: Your Mission Control Dashboard

### 🎯 Kanban Board
See where everything is at a glance.

```bash
python scripts/mission_control/mc.py board
python scripts/mission_control/mc.py board --compact      # Minimal view
python scripts/mission_control/mc.py board --sprint SPRINT-001  # Filter by sprint
```

### 🏆 Scoreboard
Who's crushing it? Who's blocked?

```bash
python scripts/mission_control/mc.py score
```

Shows:
- Sprint progress with visual bar
- Agent leaderboard
- EPIC completion status
- LLM budget burn rate

### 🎮 Agent Cockpit
What's on each agent's plate?

```bash
python scripts/mission_control/mc.py cockpit                    # All agents
python scripts/mission_control/mc.py cockpit --agent "Stephen Curry"  # Specific agent
```

---

## 🤖 LLM Budget Control

No silent LLM usage. Every token is tracked.

```bash
# Check the budget
python scripts/mission_control/mc.py llm budget

# Approve LLM usage for a ticket
python scripts/mission_control/mc.py llm approve TKT-001 \
  --tokens 50000 \
  --reason "Complex analysis required"

# Record consumption
python scripts/mission_control/mc.py llm consume TKT-001 --tokens 12500

# See who's using what
python scripts/mission_control/mc.py llm status
```

---

## 🔍 Interpreting the Output

### Gate Status Display
```
✅ = Passed/Approved
⬜ = Pending
🔧 = Needs Fix
❌ = Failed/Rejected
```

### Priority Icons
```
🔴 P0 = Drop everything
🟠 P1 = This sprint
🟡 P2 = Soon
🟢 P3 = Nice to have
```

### State Icons
```
💡 IDEA      = Just born
📝 BACKLOG   = Approved, waiting
🎯 READY     = Sprint assigned
🔄 RUNNING   = In progress
🚫 BLOCKED   = Stuck
👀 REVIEW    = Technical gates
⏳ VALIDATION = Founder review
✅ DONE      = Shipped!
```

---

## ✅ Verify It's Working

Run this smoke test sequence:

```bash
# 1. Create a ticket
python scripts/mission_control/mc.py ticket create --title "Smoke Test" --priority P1

# 2. Check it exists
python scripts/mission_control/mc.py ticket list

# 3. View the board
python scripts/mission_control/mc.py board

# 4. Check status
python scripts/mission_control/mc.py status

# 5. Try an invalid transition (should fail gracefully)
python scripts/mission_control/mc.py ticket update TKT-001 --state DONE
# Expected: Will fail - gates not passed

# 6. Check the audit log
cat .mission-control/logs/audit.jsonl
```

### Run the Test Suite

```bash
# Full test suite (24 tests)
python -m pytest tests/test_mission_control.py -v

# Quick sanity check
python -m pytest tests/test_mission_control.py -v -k "test_create"
```

---

## 🔮 What's Next? (Phase 5+)

### Immediate Enhancements
- [ ] **Slack/Discord notifications** on state changes
- [ ] **Auto-assignment** based on agent capacity
- [ ] **Burndown charts** with matplotlib
- [ ] **PRD migration** from existing docs

### Future Features
- [ ] **Web dashboard** (Flask/FastAPI)
- [ ] **GitHub integration** for auto-linking PRs
- [ ] **Time tracking** for velocity prediction
- [ ] **Agent performance analytics**

### Integration Ideas
```bash
# Future: Auto-create ticket from PR
mc ticket create --from-pr 123

# Future: Link to GitHub issue
mc ticket link TKT-001 --github-issue 456

# Future: Generate sprint report
mc report --sprint SPRINT-001 --format pdf
```

---

## 📁 File Structure

```
.mission-control/
├── config/
│   ├── settings.json      # Global config
│   ├── roles.json         # Who can do what
│   └── schemas/           # Data validation
├── data/
│   ├── tickets/           # TKT-001.json, TKT-002.json...
│   ├── epics/             # EPIC-001.json...
│   ├── sprints/           # SPRINT-001.json...
│   └── agents/            # Agent status
├── indexes/               # Fast lookups (auto-generated)
├── views/                 # Cached view data
└── logs/
    └── audit.jsonl        # APPEND-ONLY audit trail 🔒
```

---

## 🎯 Pro Tips

1. **Always check gate status before transitioning:**
   ```bash
   python scripts/mission_control/mc.py approve show TKT-001
   ```

2. **Use compact board for quick standup:**
   ```bash
   python scripts/mission_control/mc.py board --compact
   ```

3. **Track agent workload before assigning:**
   ```bash
   python scripts/mission_control/mc.py cockpit
   ```

4. **The audit log is your friend:**
   ```bash
   tail -20 .mission-control/logs/audit.jsonl | jq .
   ```

5. **JSON output for automation:**
   ```bash
   python scripts/mission_control/mc.py board --json > kanban.json
   ```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ticket not found" | Check ID format: `TKT-001` not `TKT-1` |
| "Invalid transition" | Run `mc approve show` to see missing gates |
| "Gate Error" | Check you have the right role/permissions |
| "Sprint budget exceeded" | Request budget increase: `mc llm budget --set 200000` |

---

## 🏁 The Bottom Line

Mission Control is your single source of truth. If it's not tracked here, it doesn't exist. If it hasn't passed the gates, it doesn't ship.

**Three commands to live by:**

```bash
mc board      # What's happening?
mc status     # How are we doing?
mc approve show TKT-XXX  # What's blocking this?
```

Now go ship something. 🚀

---

*Built with ❤️ for Cricket Playbook | v0.1.0*
*Design Spec: governance/MISSION_CONTROL_DESIGN_020426_v1.md*
