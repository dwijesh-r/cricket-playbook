# Ticket Context Template

**Author:** Tom Brady (Delivery Owner)
**Date:** February 6, 2026
**Ticket:** RETRO-001 Action Item

---

## Overview

Every ticket should have a `context` object that provides clarity on what needs to be done, why, and how. This ensures any agent or team member can pick up a ticket and understand the full scope.

---

## Context Structure

```javascript
context: {
    ask: 'The specific deliverable or outcome expected',
    goal: 'Measurable success criteria or acceptance conditions',
    reason: 'PRD reference or business justification',
    audible: ['Step 1', 'Step 2', 'Step 3']  // Execution steps
}
```

---

## Field Definitions

### `ask` (Required)
**What is the deliverable?**

A clear, actionable statement of what needs to be produced. Start with a verb.

**Examples:**
- "Run depth chart pipeline for all 10 IPL teams"
- "Add Key Partnerships section to stat pack"
- "Review and approve the 10 depth chart outputs"
- "Move hardcoded values to config file"

**Anti-patterns:**
- "Work on the feature" (too vague)
- "Improve performance" (not specific)

---

### `goal` (Required)
**How do we know it's done?**

Measurable success criteria. Should be verifiable.

**Examples:**
- "Produce 10 depth chart files in outputs/depth_charts/"
- "Display top partnerships by runs, balls faced, and efficiency"
- "Enable runtime configuration without code changes"
- "Confirm outputs meet quality bar and can be published"

**Anti-patterns:**
- "Make it work" (not measurable)
- "User is happy" (subjective)

---

### `reason` (Required)
**Why are we doing this?**

Reference to PRD, sprint goal, or business justification.

**Examples:**
- "PRD Requirement: Team depth visualization with positional rankings"
- "Task Integrity Loop: Founder validation required before DONE"
- "PRD: Partnership analysis identifies complementary batting pairs"
- "Sprint 4 Goal: Operational excellence through externalization"

**Anti-patterns:**
- "Because Tom said so" (not traceable)
- "It would be nice" (no business case)

---

### `audible` (Required)
**What are the execution steps?**

Array of ordered steps. Use short, imperative statements.

**Examples:**
```javascript
audible: [
    'Execute generate_depth_charts.py',
    'Validate all 10 teams have outputs',
    'Verify Andy Flower approved positions'
]

audible: [
    'Query partnership data from DuckDB',
    'Calculate partnership metrics',
    'Add to stat pack generator',
    'Test with MI, CSK'
]
```

**Anti-patterns:**
- Empty array (no guidance)
- Single step for complex work (under-specified)

---

## Context by Ticket Type

### Feature Tickets
```javascript
context: {
    ask: 'Add [feature name] section to [component]',
    goal: 'Display [specific data] with [format/visualization]',
    reason: 'PRD: [requirement reference]',
    audible: ['Query data', 'Transform/calculate', 'Add to generator', 'Test']
}
```

### Pipeline Tickets
```javascript
context: {
    ask: 'Run [pipeline] for [scope]',
    goal: 'Produce [N] files in [path] with [format]',
    reason: 'PRD Core Deliverable: [description]',
    audible: ['Execute script', 'Validate outputs', 'Domain review']
}
```

### Approval Tickets
```javascript
context: {
    ask: 'Review and approve [outputs] for [quality criteria]',
    goal: 'Confirm [outputs] meet quality bar',
    reason: 'Task Integrity Loop: [gate] required before DONE',
    audible: ['Review files', 'Check criteria', 'Approve or feedback']
}
```

### Config/Ops Tickets
```javascript
context: {
    ask: 'Move/externalize [thing] to [location/mechanism]',
    goal: 'Enable [capability] without [constraint]',
    reason: '[Sprint/Ops goal]',
    audible: ['Identify values', 'Create config', 'Update references', 'Test']
}
```

---

## Adding Context to Existing Tickets

For tickets in Mission Control (`index.html`), add context like this:

```javascript
// BEFORE
{ id: 'TKT-XXX', title: 'Some task', state: 'RUNNING', ... },

// AFTER
{ id: 'TKT-XXX', title: 'Some task', state: 'RUNNING', ...,
  context: {
    ask: 'The deliverable',
    goal: 'Success criteria',
    reason: 'Business justification',
    audible: ['Step 1', 'Step 2']
  }
},
```

---

## Context Quality Checklist

Before marking a ticket as ready:

- [ ] `ask` starts with a verb and is specific
- [ ] `goal` is measurable and verifiable
- [ ] `reason` references PRD or business case
- [ ] `audible` has 2-5 ordered steps
- [ ] Any agent could complete the ticket using only the context

---

*Tom Brady*
*Delivery Owner*
*Cricket Playbook v4.1.0*
