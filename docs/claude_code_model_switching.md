# Claude Code Model Switching Guide

**Owner:** Tom Brady (Product Owner)
**Created:** February 6, 2026
**Purpose:** Ensure smooth model transitions without data loss or configuration breaks

---

## Overview

When switching Claude Code models (e.g., from `claude-opus-4-5` to another model), this guide ensures all project context, configurations, and progress are preserved.

---

## 1. Pre-Switch Checklist

### 1.1 Commit All Work
```bash
# Check for uncommitted changes
git status

# Stage and commit everything
git add . && git commit -m "[Pre-Model-Switch] Save all work before model transition"
git push origin main
```

### 1.2 Export Current Session Context
The current conversation context is stored in:
- **Session transcript:** `~/.claude/projects/-Users-dwijeshreddy-cricket-playbook/*.jsonl`
- **History:** `~/.claude/history.jsonl`
- **Plans:** `~/.claude/plans/`
- **Todos:** `~/.claude/todos/`

### 1.3 Document Current State
Before switching, record:
- [ ] Current sprint (Sprint 4)
- [ ] In-progress tickets (check The Boardroom)
- [ ] Any pending Founder approvals
- [ ] Recent architectural decisions

---

## 2. Files That Will Persist (Safe)

These are version-controlled and will be retained:

| Category | Location | Notes |
|----------|----------|-------|
| **Agent Configs** | `config/agents/*.agent.md` | 14 agent definitions with roles, tools, models |
| **Documentation** | `docs/` | PRD, Constitution, Task Integrity Loop |
| **Dashboards** | `scripts/*/dashboard/*.html` | The Lab, The Boardroom |
| **Python Scripts** | `scripts/*.py` | All analytics code |
| **Outputs** | `outputs/` | Generated stat packs, depth charts |
| **Workflows** | `.github/workflows/` | CI/CD configurations |
| **Reviews** | `reviews/` | Sprint review documents |

---

## 3. Files That May Need Re-Sync

These are Claude Code session-specific and may need attention:

| File/Directory | Location | Risk | Mitigation |
|----------------|----------|------|------------|
| **Session history** | `~/.claude/history.jsonl` | Context loss | Export key decisions to `docs/` |
| **Active plans** | `~/.claude/plans/*.md` | Plan state | Complete or document plans before switch |
| **Todos** | `~/.claude/todos/` | Lost progress | Mark all as complete or document remaining |
| **Stats cache** | `~/.claude/stats-cache.json` | Resets | Non-critical, will rebuild |
| **Project settings** | `~/.claude/projects/` | May reset | Document custom settings |

---

## 4. Agent Configuration Compatibility

All 14 agents specify their model in the frontmatter:

```yaml
---
name: Andy Flower
model: claude-3-5-sonnet
temperature: 0.25
---
```

**Current Agent Models:**
| Agent | Model |
|-------|-------|
| All 14 agents | `claude-3-5-sonnet` |

### 4.1 If Model Changes Require Agent Updates
If the new Claude Code model uses different model identifiers:
1. Update each `config/agents/*.agent.md` file
2. Verify tool compatibility
3. Test one agent before bulk update

---

## 5. Switch Procedure

### Step 1: Pre-Switch
```bash
# Navigate to project
cd ~/cricket-playbook

# Commit all work
git status
git add . && git commit -m "[Pre-Model-Switch] Save all work"
git push

# Export todos (if any active)
cat ~/.claude/todos/* > docs/pre_switch_todos.txt 2>/dev/null

# Document active plans
cp ~/.claude/plans/*.md docs/pre_switch_plans/ 2>/dev/null
```

### Step 2: Switch Model
In Claude Code:
```
/model <new-model-name>
```

Or via settings if using IDE integration.

### Step 3: Post-Switch Verification
```bash
# Verify project loads correctly
cd ~/cricket-playbook

# Check git status
git status

# Verify agent configs are readable
ls -la config/agents/

# Test a simple operation
ls outputs/
```

### Step 4: Context Re-Establishment (Automated)

Simply ask the new model to read the onboarding file:

```
Please read ONBOARDING.md to understand the current project state.
```

The **ONBOARDING.md** file (at project root) contains:
- Current sprint and status
- Active/blocked/validation tickets
- Agent roster with roles
- Key documents to read
- How to continue work

**Alternative (Quick Start):**
```
Read ONBOARDING.md and CLAUDE.md, then tell me what you understand about this project.
```

**Context Files Location:** `docs/context/README.md` has a complete reading list.

> **Note:** Update ONBOARDING.md at the end of each session to keep context fresh.

---

## 6. Post-Switch Checklist

- [ ] Project loads without errors
- [ ] Git repository accessible
- [ ] Agent configs parse correctly
- [ ] Dashboards render (The Lab, The Boardroom)
- [ ] Previous context understood (test by asking about recent work)
- [ ] Tools work (Read, Write, Bash, etc.)
- [ ] Todo list restored or re-created

---

## 7. Rollback Plan

If the new model has issues:

1. **Revert settings** if model was changed via config
2. **Check Claude Code version:** `claude --version`
3. **Clear cache if needed:** `rm -rf ~/.claude/cache/`
4. **Contact support** if persistent issues

---

## 8. Known Model Differences

| Aspect | claude-opus-4-5 | claude-sonnet | Notes |
|--------|-----------------|---------------|-------|
| Context window | 200K | 200K | Same |
| Tool use | Full | Full | Compatible |
| Cost | Higher | Lower | Consider for high-volume work |
| Speed | Slower | Faster | Sonnet is faster |
| Reasoning | Deeper | Good | Opus better for complex planning |

---

## 9. Emergency Recovery

If all else fails:

```bash
# Clone fresh copy
git clone https://github.com/dwijesh-r/cricket-playbook.git cricket-playbook-recovery
cd cricket-playbook-recovery

# Copy any local-only files from original
cp -r ~/cricket-playbook/outputs/* outputs/
cp -r ~/cricket-playbook/.editorial/* .editorial/ 2>/dev/null
```

The git repository contains all critical project state.

---

## Appendix: File Inventory

### Critical Files (Must Preserve)
- `docs/prd_v2.md` - Product Requirements Document
- `docs/constitution.md` - Project governance
- `config/agents/*.agent.md` - 14 agent configurations
- `scripts/mission_control/dashboard/index.html` - The Boardroom (tickets)
- `scripts/the_lab/dashboard/` - The Lab dashboards

### Generated Files (Recreatable)
- `outputs/stat_packs/` - Can regenerate from scripts
- `outputs/depth_charts/` - Can regenerate from scripts
- `.editorial/` - Review documents (version controlled)

### Local-Only Files (Document Before Switch)
- `~/.claude/todos/` - Active todo items
- `~/.claude/plans/` - In-progress plans
- Any uncommitted changes

---

*Document created by Tom Brady (Product Owner) to ensure smooth Claude Code model transitions.*
