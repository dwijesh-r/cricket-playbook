# CLAUDE.md

## Project Operating Principles

This repository uses a multi-agent workflow with explicit roles, task ownership, and validation loops.
Agents are expected to operate within defined responsibilities and surface uncertainty early.

---

## Mission Control (Guiding)

Mission Control is the primary **task integrity and coordination layer** for this project.
It functions like a lightweight, local JIRA-style system for agents, making work visible, auditable,
and governed without introducing autonomous decision-making.

All meaningful work is expected to flow through Mission Control tickets.

### What Mission Control Is Used For

- Tracking projects, tickets, and subtasks (EPIC → Ticket → Subtask)
- Enforcing clear ownership across scope, execution, and validation
- Making token-heavy (LLM-required) work explicit and manually approved
- Providing visibility into progress, blockers, and % completion
- Supporting sprint planning, reviews, and retrospectives

Mission Control does **not** think, plan, or decide — it coordinates.

---

## Schema Governance (Guiding)

The Mission Control schema (tasks, subtasks, approvals, agent status, execution logs) is
**designed and owned by Tom Brady**, with **review and feedback by Brad Stevens**.

Agents may propose schema changes when needed, but should avoid independently introducing
or modifying structural fields, relationships, or workflow-critical logic.

Schema changes that materially affect:
- workflow integrity
- validation or approval gates
- metrics or reporting

are expected to receive **explicit Founder sign-off** before adoption.

### Intent

This guidance exists to prevent silent schema drift and ensure that Mission Control remains
robust, auditable, and aligned with long-term governance goals.

When in doubt, propose early rather than optimize locally.

---

## One-Line Reminder (Read This)

> **If a change affects how work is tracked, approved, or measured, surface it to Tom Brady and Brad Stevens before implementing.**
