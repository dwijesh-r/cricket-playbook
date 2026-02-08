# Cricket Playbook Incident Response

**Ticket:** TKT-158
**EPIC:** EPIC-015 (Operational Maturity)
**Owner:** Tom Brady (Product Owner)
**Last Updated:** 2026-02-08

How we handle incidents when the Cricket Playbook system breaks. Read this when something is on fire. Skim it before something is on fire so you're not reading it for the first time at 2am.

---

## Table of Contents

1. [Severity Levels](#1-severity-levels)
2. [Response Procedures](#2-response-procedures)
3. [Communication Templates](#3-communication-templates)
4. [Post-Mortem Template](#4-post-mortem-template)
5. [Escalation Paths](#5-escalation-paths)

---

## 1. Severity Levels

### SEV1 - Critical

**Definition:** The system is producing wrong data that has been or could be delivered to stakeholders. Data corruption. Wrong numbers in stat packs or predicted XIs that someone is using to make decisions.

**Examples:**
- Database corruption after failed ingestion (no auto-rollback happened)
- GE validation shows failures in `fact_ball` or `dim_match` but outputs were already generated with the bad data
- Player clustering model assigned clearly wrong archetypes and stat packs shipped with those labels
- Dashboard is live with stale/incorrect data and stakeholders are actively viewing it

**Response time:** Immediately. Drop what you're doing.

**Target resolution:** 2 hours.

### SEV2 - High

**Definition:** A core pipeline component is broken but bad data hasn't shipped yet. The system can't produce outputs. CI/CD is completely blocked.

**Examples:**
- Ingestion pipeline fails (Cricsheet data changed format, DuckDB connection issues)
- All output generators are failing (missing analytics views, missing database)
- ML health check returns CRITICAL and blocks stat pack generation
- GitHub Actions workflows are all failing (broken config, expired secrets)
- Pre-commit hooks are blocking all commits on main

**Response time:** Within 4 hours during business hours.

**Target resolution:** 8 hours.

### SEV3 - Low

**Definition:** Something is degraded but the system still works. Outputs are still generated correctly, but with warnings or reduced quality.

**Examples:**
- One out of 10 team stat packs fails to generate
- ML health check returns DEGRADED (warning, not blocking)
- System health score dropped below 70 but above 50
- One CI workflow is flaky (passes on retry)
- A non-critical dashboard page is broken
- Some GE validations are failing on non-critical tables

**Response time:** Next business day.

**Target resolution:** 3 business days.

---

## 2. Response Procedures

### SEV1 Response

1. **Assess the blast radius.** What data was shipped? Who has seen it? Check recent GitHub Actions runs for the generate-outputs and deploy-dashboard workflows.

2. **Stop the bleeding.** If the dashboard is showing wrong data:

```bash
# Take down the dashboard data by pushing empty data files
# (or revert to last known good commit)
git log --oneline -- scripts/the_lab/dashboard/data/
git checkout <last-good-commit> -- scripts/the_lab/dashboard/data/
git commit -m "hotfix: revert dashboard to last known good state"
git push origin main
```

3. **Restore the database if corrupted:**

```bash
python scripts/core/backup_recovery.py list
python scripts/core/backup_recovery.py restore
python scripts/core/backup_recovery.py verify
```

4. **Validate the restored state:**

```bash
python scripts/core/ge_validation.py
```

5. **Re-generate outputs from clean data:**

```bash
python scripts/core/analytics_ipl.py
python scripts/generators/generate_outputs.py
```

6. **Verify outputs look correct.** Spot-check a couple of stat packs. Look at key player stats (Virat Kohli, Jasprit Bumrah) to see if the numbers pass a smell test.

7. **Notify stakeholders.** Use the SEV1 communication template below.

8. **Schedule a post-mortem** within 48 hours.

### SEV2 Response

1. **Identify which component is broken.** Check the failing GitHub Actions run or the local error output.

2. **Check recent changes.** What was the last commit before things broke?

```bash
git log --oneline -10
```

3. **Follow the troubleshooting section in the RUNBOOK.** Most SEV2 issues fall into one of:
   - DuckDB locked/corrupt -> See RUNBOOK 5.1
   - GE validation failures -> See RUNBOOK 5.2
   - CI/CD pipeline failures -> See RUNBOOK 5.4

4. **If it's a code issue, fix and push.** The Quality Gates workflow will validate.

5. **If it's an infrastructure issue (Cricsheet down, GitHub Actions broken):** wait and retry. Document the outage.

6. **Notify the team** using the SEV2 template.

### SEV3 Response

1. **File a ticket** if one doesn't exist already. Link it to the failing component.

2. **Check if it's intermittent.** Retry the failing operation once:

```bash
# Re-run the specific generator that failed
python scripts/generators/generate_stat_packs.py
```

3. **If it's a flaky test or CI issue**, check if a retry fixes it. If the workflow passes on retry, add a note to the existing flaky-test tracking issue.

4. **Fix during normal work hours.** No rush.

---

## 3. Communication Templates

### SEV1 - Stakeholder Notification

```
Subject: [SEV1] Cricket Playbook - Data Issue Detected and Resolved

Team,

We identified an issue with Cricket Playbook data outputs at [TIME].

What happened:
[Brief description - e.g., "The database was corrupted during ingestion,
causing stat packs to contain incorrect player statistics."]

Impact:
[What was affected - e.g., "Stat packs generated between [TIME1] and [TIME2]
contained incorrect batting averages for all teams."]

Resolution:
[What was done - e.g., "We restored the database from backup taken at [TIME],
re-validated all data, and regenerated all outputs."]

Current status:
[e.g., "All outputs have been regenerated and verified. The dashboard has been
updated with correct data."]

Post-mortem scheduled for: [DATE/TIME]

Questions? Reach out to [OWNER].
```

### SEV2 - Team Notification

```
Subject: [SEV2] Cricket Playbook - Pipeline Issue

Heads up:

[Component] is currently broken. [Brief description of what's failing.]

Impact: [e.g., "Output generation is blocked. No new stat packs or depth
charts can be produced until this is fixed."]

ETA for fix: [estimate]

Workaround: [if any - e.g., "Last generated outputs from [DATE] are still
valid and available."]

I'm on it. Will update when resolved.

- [Your name]
```

### SEV3 - Team Note

```
Subject: [SEV3] Cricket Playbook - Minor Issue Noted

FYI:

[Component] has a non-critical issue: [description].

Impact: Minimal. [e.g., "Gujarat Titans stat pack failed to generate
but the other 9 teams are fine."]

Will fix during normal hours. Tracked in [TICKET].

- [Your name]
```

---

## 4. Post-Mortem Template

Use this template after every SEV1 and for SEV2 incidents that had significant impact. Save the completed post-mortem in `docs/ops/post-mortems/`.

```markdown
# Post-Mortem: [Incident Title]

**Date:** YYYY-MM-DD
**Severity:** SEV1 / SEV2
**Duration:** [start time] to [end time] ([X] hours)
**Author:** [your name]
**Ticket:** [TKT-XXX]

## Summary

[2-3 sentences describing what happened and the impact.]

## Timeline

| Time (UTC) | Event |
|---|---|
| HH:MM | [First sign of trouble] |
| HH:MM | [Issue detected by / reported by] |
| HH:MM | [Investigation started] |
| HH:MM | [Root cause identified] |
| HH:MM | [Fix applied] |
| HH:MM | [Verified resolution] |

## Root Cause

[What actually caused the problem. Be specific. "The ingestion script
crashed" is not a root cause. "The ingestion script crashed because
Cricsheet added a new field 'super_sub' to match JSON that our parser
didn't handle, causing a KeyError in process_match()" is a root cause.]

## Impact

- **Data affected:** [what data was wrong/missing]
- **Duration of bad data:** [how long was bad data live]
- **Users affected:** [who saw bad data, if anyone]
- **Downstream effects:** [what outputs were generated from bad data]

## Resolution

[What was done to fix it, step by step.]

## What Went Well

- [e.g., "Backup system worked correctly, restore took 30 seconds"]
- [e.g., "GE validation caught the issue before stat packs shipped"]

## What Went Wrong

- [e.g., "No alerting on ingestion failures - we found out manually"]
- [e.g., "Backup was 3 days old because scheduled backups weren't running"]

## Action Items

| Action | Owner | Ticket | Due |
|---|---|---|---|
| [e.g., Add error handling for unknown JSON fields] | Brock Purdy | TKT-XXX | YYYY-MM-DD |
| [e.g., Set up Slack alerts on CI failures] | Brad Stevens | TKT-XXX | YYYY-MM-DD |
| [e.g., Increase backup frequency to daily] | Ime Udoka | TKT-XXX | YYYY-MM-DD |

## Lessons Learned

[What should we do differently? What assumptions were wrong?]
```

---

## 5. Escalation Paths

Each agent in the Cricket Playbook project owns specific components. When something breaks, go to the right person.

### Data Pipeline Issues

**Primary:** Brock Purdy (Data Pipeline Agent)
- Owns: `scripts/core/ingest.py`, `scripts/core/ge_validation.py`, `scripts/core/domain_constraints.py`
- Handles: Ingestion failures, data quality issues, Cricsheet format changes, GE validation failures

### Infrastructure & CI/CD Issues

**Primary:** Ime Udoka (MLOps & Infrastructure Lead)
- Owns: `scripts/core/backup_recovery.py`, `scripts/ml_ops/`, `.github/workflows/ingest.yml`
- Handles: Database backup/recovery, ML health monitoring, infrastructure failures

**Secondary:** Brad Stevens (Architecture & Performance)
- Owns: `.github/workflows/ci.yml`, `.github/workflows/gate-check.yml`, `.github/workflows/generate-outputs.yml`, `.github/workflows/deploy-dashboard.yml`
- Handles: CI/CD pipeline configuration, quality gates, workflow automation, performance issues

### Analytics & Model Issues

**Primary:** Stephen Curry (Analytics Lead)
- Owns: `scripts/analysis/player_clustering_v2.py`, `scripts/generators/generate_stat_packs.py`, `scripts/generators/generate_depth_charts.py`, `scripts/generators/generate_predicted_xii.py`
- Handles: Model retraining, clustering issues, output generation bugs, algorithm correctness

### Dashboard & Visualization Issues

**Primary:** Kevin de Bruyne (Visualization)
- Owns: `scripts/the_lab/dashboard/`, `scripts/mission_control/dashboard/`
- Handles: Dashboard bugs, GitHub Pages deployment, data file format issues

### Domain / Cricket Knowledge Issues

**Primary:** Andy Flower (Cricket Domain Expert)
- Handles: Player classification validation, threshold sanity checks, domain constraint definitions, "does this stat make cricket sense?" questions

### Product & Prioritization

**Primary:** Tom Brady (Product Owner)
- Handles: Severity classification, stakeholder communication, post-mortem scheduling, deciding what gets fixed first

### Escalation Order

For any incident:

1. **First responder:** Whoever notices it first. Check the component owner above and ping them.
2. **If the owner is unavailable:** Escalate to Brad Stevens (Architecture) or Ime Udoka (Infrastructure) -- they can triage most issues across components.
3. **If it's a SEV1 and nobody is responding:** Escalate to Tom Brady (Product Owner) who will get the right people involved.

---

## Quick Decision Tree

```
Something broke. What now?

Is wrong data live in front of stakeholders?
  YES -> SEV1. Stop the dashboard. Restore backup. Fix. Notify.
  NO  -> Continue...

Can we produce outputs at all?
  NO  -> SEV2. Pipeline is down. Follow troubleshooting in RUNBOOK.
  YES -> Continue...

Is the issue blocking other work?
  YES -> SEV2. Fix it now.
  NO  -> SEV3. File a ticket. Fix during normal hours.
```

---

*This document is part of TKT-158 (EPIC-015: Operational Maturity). If you're reading this during an incident, skip the table of contents and go straight to the severity level that matches your situation.*
