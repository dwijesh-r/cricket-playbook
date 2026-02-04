# Product Requirements Document (PRD)
## Mission Control – Local Task Integrity & Agent Coordination

**Owner (Product):** Florentino Perez
**Delivery Owner:** Tom Brady
**Status:** Approved – Pilot (v0.1)

---

## 1. What Problem This Solves

As the number of agents, analytics pipelines, and editorial outputs grows, execution risk increases:

- work happens without clear ownership
- token-heavy tasks run accidentally
- validation is inconsistent
- progress is hard to measure

Mission Control exists to fix this by making work **explicit, visible, and governed**.

---

## 2. What Mission Control Is

Mission Control is a **local-only, JIRA-style task board for agents**.

It tracks:
- projects (EPICs)
- tickets
- subtasks
- approvals
- progress (% complete)

It enforces a simple integrity loop:
**scope → execute → validate → done**

---

## 3. What Mission Control Is Not

Mission Control does NOT:
- replace agents
- generate ideas
- auto-run LLMs
- make decisions
- run in the cloud (v0.1)

It is coordination infrastructure, not intelligence.

---

## 4. Core Use Cases

### Use Case 1: Sprint Planning
- Florentino prioritizes tickets
- Tom Brady commits execution scope
- Work is grouped by sprint and priority

### Use Case 2: Execution Tracking
- Agents pull only assigned tickets
- Subtasks drive % completion
- Artifacts and logs are attached per ticket

### Use Case 3: Token Control
- LLM-required tickets are clearly marked
- Editorial / synthesis work is manually triggered
- No silent token burn

### Use Case 4: Validation & QA
- QA agents can block incorrect outputs
- No agent approves their own work
- Blocked work must re-enter the loop

### Use Case 5: Visibility
- Board view (Kanban)
- Ticket list (audit)
- Sprint view (planning)
- Agent cockpit (who is doing what)
- Scoreboard (% complete, blockers, risk)

---

## 5. Task Structure

EPIC (Project)
 └─ Ticket (Deliverable)
     └─ Subtasks (Executable steps)

Progress rolls up from subtasks → ticket → epic.

---

## 6. States

IDEA → BACKLOG → READY → RUNNING → REVIEW → DONE
                 ↘ BLOCKED

State transitions are role-aware and intentional.

---

## 7. Roles (Summary)

- Florentino Perez – Product Owner (scope & priority)
- Tom Brady – Delivery Owner (workflow & execution discipline)
- Stephen Curry / Virat Kohli – Executors
- N’Golo Kanté / Ime Udoka – Validation gates
- Brad Stevens – System & governance reviewer

---

## 8. Schema Governance

The Mission Control schema is **designed by Tom Brady** and **reviewed by Brad Stevens**.

Any schema change impacting workflow integrity, metrics, or approvals requires
**explicit Founder approval**.

---

## 9. Success Criteria

Mission Control is successful when:

- no work runs without a ticket
- no LLM work runs without approval
- progress % is always visible
- validation gates are respected
- sprint planning uses the same board

---

## 10. Final Note

Mission Control is treated as **first-class product infrastructure**.
If it’s not on the board, it didn’t happen.
