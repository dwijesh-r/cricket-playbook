# Mega Review #1 - Comprehensive Action Plan

**Document Owner:** Tom Brady (Product Owner)
**Review Date:** 2026-01-31
**Status:** PLANNING - AWAITING FOUNDER APPROVAL

---

## Executive Summary

The Founder Mega Review establishes the strategic direction for Cricket Playbook as a **magazine-style preview generator** - scouting-style cricket editorial similar to Lindy's and Phil Steele's publications. This document captures every action item, assigns ownership, and prioritizes execution.

**Core Philosophy (from Founder):**
> "Cricket fans don't pay for analytics, they pay for confidence, narrative clarity and authority. What will make money is ruthless editorial compression, strong opinions based on transparent data and zero temptation to be only analytical heavy."

---

## Part 1: Product Vision & Identity

### 1.1 Product Clarity

**What We Are Building:**
- Magazine-style preview generator powered by analytics warehouse
- Structured, opinionated cricket analysis (like pro team's internal prep for public consumption)
- Scouting-style editorial: roles, depth charts, matchups, possible Playing XI, structures, skill-gaps, strengths, tendencies
- Using only freely available ball-by-ball data

**Reference Models:** Lindy's Sports Annual, Phil Steele's College Football Preview

**USP:** Pro team internal prep packaged for public consumption

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Update PRD to reflect magazine-style focus | Tom Brady | P0 | To Do |
| Create product positioning document | Tom Brady + Virat Kohli | P0 | To Do |
| Define "Editorial vs Analytics" boundary clearly | Brad Stevens | P0 | To Do |

---

## Part 2: Task Integrity Loop (New Process)

### 2.1 New Agent: Florentino Perez

**Role:** Strategic Gatekeeper - ensures every task materially improves the paid artifact or strategic decision.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `config/agents/florentino-perez.agent.md` | Brad Stevens | P0 | To Do |
| Define Florentino Gate criteria | Florentino Perez + Tom Brady | P0 | To Do |

### 2.2 Task Integrity Loop - 8 Steps

**Create folder:** `governance/task_integrity_loop/`

| Step | Name | Description | Owner |
|------|------|-------------|-------|
| 0 | Task Declaration | Create PRD for task | Requesting Agent |
| 1 | Florentino Gate | "Does this materially improve paid artifact or strategic decision?" Outcomes: Approved / Analytics Only / Not Approved | Florentino Perez |
| 2 | Build | Work within scope only, no opportunistic additions | Assigned Agent |
| 3 | Domain Sanity Loop | Three sign-offs (Yes/No/Fix): Jose Mourinho (robust? baselines? scalable?), Andy Flower (makes sense to coach/analyst/fan?), Pep Guardiola (structurally coherent?) | Jose Mourinho, Andy Flower, Pep Guardiola |
| 4 | Enforcement Check | Was loop followed? Objections addressed? Scope respected? | Tom Brady |
| 5 | Commit and Ship | Merge to main | Assigned Agent |
| 6 | Post Task Note | README updates, what changed, assumptions tested, risks introduced, USP of change | Assigned Agent |
| 7 | System Check | Schema structure intact, manifests updated | N'Golo Kanté |

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `governance/` folder structure | Brad Stevens | P0 | To Do |
| Create `governance/TASK_INTEGRITY_LOOP.md` | Florentino Perez + Tom Brady | P0 | To Do |
| Create task PRD template | Tom Brady | P0 | To Do |
| Create domain sanity checklist template | Andy Flower | P1 | To Do |

### 2.3 New Agent: Jose Mourinho

**Role:** Data Robustness & Scalability Guardian - ensures baselines are clear, data is robust, and solutions are scalable.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `config/agents/jose-mourinho.agent.md` | Brad Stevens | P0 | To Do |
| Define Jose Mourinho's review criteria | Jose Mourinho | P0 | To Do |
| Jose Mourinho ecosystem analysis (Review 5 request) | Jose Mourinho | P1 | To Do |

---

## Part 3: Constitution Document

### 3.1 Requirements (DO NOT COMMIT BEFORE FOUNDER APPROVAL)

The Constitution must define:

| Section | Content | Owner |
|---------|---------|-------|
| Authority | Decision rights hierarchy | Brad Stevens |
| Agent Roles | Formalized responsibilities, no overlap | Brad Stevens |
| Loops | Task Integrity Loop enforcement | Florentino Perez |
| Scope & Boundaries | What's in/out of scope | Tom Brady |
| Editorial vs Analytical Teams | Clear separation | Tom Brady |
| Definition of Done | Formal criteria | N'Golo Kanté |
| Graduation Rules | Analytics → Editorial pathway | Andy Flower |
| Product Vision | Clear USP and direction | Tom Brady |

**Team Classification:**

| Team | Agents | Focus |
|------|--------|-------|
| **Editorial** | Virat Kohli, Kevin de Bruyne, LeBron James | Magazine content, narrative, presentation |
| **Analytical** | Stephen Curry, Ime Udoka, Brock Purdy | Data, models, pipelines |
| **Governance** | Tom Brady, Brad Stevens, Florentino Perez, N'Golo Kanté | Process, quality, architecture |
| **Domain** | Andy Flower, Jose Mourinho, Pep Guardiola | Cricket expertise, validation, coherence |

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Draft CONSTITUTION.md v2.0 | Brad Stevens + Florentino Perez + Tom Brady | P0 | To Do |
| Submit for Founder approval BEFORE commit | Tom Brady | P0 | Blocked |

---

## Part 4: Documentation Overhaul

### 4.1 Single Source of Truth

**Problem:** README says 34 views, manifest says 43, .py file has 35 CREATE OR REPLACE statements.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit all view counts across docs | Stephen Curry | P0 | To Do |
| Create auto-updating manifest system | Brock Purdy | P0 | To Do |
| Archive outdated documents | Brad Stevens | P1 | To Do |
| Implement manifest generation on script run | Brock Purdy | P1 | To Do |

### 4.2 "How Does This All Work" Document

**Requirement:** One-page markdown for outsiders explaining:

1. What agents do
2. What reviews mean
3. What the approval chain is
4. Where published artifacts are
5. Flow of work
6. Who is responsible for each step
7. Review and Approval Gates (Stage, Owner, What must be solved)
8. Each metric has a baseline, no silent assumptions

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `docs/HOW_IT_WORKS.md` | Tom Brady + Brad Stevens | P0 | To Do |

---

## Part 5: Repo Structure & Hygiene

### 5.1 Immediate Fixes

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Add .DS_Store to .gitignore | Brad Stevens | P0 | To Do |
| Remove committed .DS_Store files | Brad Stevens | P0 | To Do |
| Create `data/archive/` folder | Brock Purdy | P1 | To Do |

---

## Part 6: Data Strategy & Credibility

### 6.1 Data Provenance

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `data/PROVENANCE.md` | Brock Purdy | P0 | To Do |
| Document squad data sources | Brock Purdy | P0 | To Do |
| Document contract data sources | Brock Purdy | P0 | To Do |
| Document Cricsheet data details | Brock Purdy | P0 | To Do |

### 6.2 DuckDB Scalability

**Problem:** Committing full 159MB DuckDB may be inefficient.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Research DuckDB alternatives (parquet, delta lake) | Brock Purdy + Ime Udoka | P2 | To Do |
| Evaluate git-lfs for large files | Brad Stevens | P2 | To Do |
| Document decision in ADR | Brad Stevens | P2 | To Do |

---

## Part 7: Pipeline & Engineering Execution

### 7.1 Schema Contracts

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Define expected schema per output file | N'Golo Kanté | P0 | To Do |
| Create column definitions document | N'Golo Kanté | P0 | To Do |
| Define stable naming conventions | Pep Guardiola | P0 | To Do |
| Implement schema contract tests | N'Golo Kanté | P1 | To Do |

---

## Part 8: Outputs Quality

### 8.1 Outputs Changelog

**Requirement:** For each run, generate changelog with:
- Number of rows changes
- New columns
- New files
- Hash of each file

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create outputs changelog generator | Brock Purdy | P1 | To Do |
| Add hash validation to outputs | Brock Purdy | P1 | To Do |

### 8.2 Limitations Section

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Add "Limitations" section to outputs/README.md | Andy Flower | P1 | To Do |
| Document known data gaps | Andy Flower | P1 | To Do |

---

## Part 9: Analytics Methodology & Model Rigor

### 9.1 Clustering Verification

**Problem:** ML Ops says K-Means/PCA with variance numbers and cluster counts, but they don't align with role lists. Different archetype counts in different places.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit cluster counts across all docs | Stephen Curry | P0 | To Do |
| Verify PCA variance alignment | Ime Udoka | P0 | To Do |
| Reconcile archetype counts | Stephen Curry + Andy Flower | P0 | To Do |

### 9.2 Model Validation

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Add silhouette score validation | Ime Udoka | P1 | To Do |
| Add inertia trends analysis | Ime Udoka | P1 | To Do |
| Create sanity check examples | Andy Flower | P1 | To Do |
| Validate clustering stability across seasons | Ime Udoka | P1 | To Do |

### 9.3 Baselines vs Tags (Critical)

**Requirement:** For each tag/archetype, show:
- Baseline metric (simple heuristic, e.g., 135 SR)
- Tagged metric (actual value for tagged players)
- Delta (tagged - baseline)

**Purpose:** Defense against "isn't this just obvious cricket knowledge?"

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Define baseline heuristics for each tag | Andy Flower | P0 | To Do |
| Create baseline vs tag comparison table | Stephen Curry | P0 | To Do |
| Calculate deltas for all archetypes | Stephen Curry | P0 | To Do |
| Document in `analysis/baselines_vs_tags.md` | Stephen Curry | P0 | To Do |

---

## Part 10: Testing

### 10.1 Required Tests

| Test Type | Description | Owner | Priority |
|-----------|-------------|-------|----------|
| Schema tests | Validate output schemas | N'Golo Kanté | P0 |
| Output file existence | All expected files exist | N'Golo Kanté | P0 |
| Column set tests | Required columns present | N'Golo Kanté | P0 |
| No null in key IDs | Player IDs, match IDs not null | N'Golo Kanté | P0 |
| Manifest update tests | Manifests reflect current state | N'Golo Kanté | P1 |

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Implement schema validation tests | N'Golo Kanté | P0 | To Do |
| Implement output existence tests | N'Golo Kanté | P0 | To Do |
| Implement null check tests | N'Golo Kanté | P0 | To Do |
| Update tests/README.md with purpose/plan | N'Golo Kanté | P1 | To Do |

---

## Part 11: CI/CD & Automation

### 11.1 CI/CD Pipeline Requirements

| Stage | Description | Owner |
|-------|-------------|-------|
| Lint/Pre-commit | Ruff, trailing whitespace, EOF | Brad Stevens |
| Unit Tests | pytest suite | N'Golo Kanté |
| Output Validation | Schema contracts, file existence | N'Golo Kanté |
| Artifact Generation | Generate sample artifacts | Stephen Curry |
| Artifact Comparison | Compare with baseline | Brock Purdy |

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Fix CI/CD error emails (low priority per Review 5) | Brad Stevens | P2 | To Do |
| Create .github/workflows/README.md | Brad Stevens | P1 | To Do |
| Implement artifact comparison in CI | Brock Purdy | P2 | To Do |

---

## Part 12: Governance/Review System

### 12.1 Review Gates

| Stage | Owner | What Must Be Solved |
|-------|-------|---------------------|
| Florentino Gate | Florentino Perez | Value to paid artifact? |
| Domain Sanity | Jose Mourinho | Robust? Baselines clear? Scalable? |
| Domain Sanity | Andy Flower | Makes sense to coach/analyst/fan? |
| Domain Sanity | Pep Guardiola | Structurally coherent? |
| Enforcement | Tom Brady | Process followed? |
| QA | N'Golo Kanté | Tests pass? Schema intact? |

---

## Part 13: Risk Management

### 13.1 Over-Interpretation Risk

**Responsibility:** Andy Flower + Jose Mourinho

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create "Insight Confidence Framework" | Andy Flower + Jose Mourinho | P1 | To Do |
| Prioritize stable/foolproof insights over flashy | All Agents | Ongoing | - |
| Flag sample-size limited insights | Stephen Curry | P1 | To Do |

### 13.2 Editorial Discipline

**Rule:** Editorial team (Virat Kohli, Kevin de Bruyne, LeBron James) must stay separate from Analytical lab (Ime Udoka, Stephen Curry, Brock Purdy).

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Define Editorial/Analytical handoff process | Tom Brady | P1 | To Do |
| Create graduation criteria (Analytics → Editorial) | Andy Flower | P1 | To Do |

---

## Summary: Mega Review Action Items by Priority

### P0 - Critical (Do First)

| # | Action Item | Owner |
|---|-------------|-------|
| 1 | Create Florentino Perez agent | Brad Stevens |
| 2 | Create Jose Mourinho agent | Brad Stevens |
| 3 | Create `governance/TASK_INTEGRITY_LOOP.md` | Florentino Perez + Tom Brady |
| 4 | Draft CONSTITUTION.md v2.0 (await approval) | Brad Stevens + Florentino Perez + Tom Brady |
| 5 | Create `docs/HOW_IT_WORKS.md` | Tom Brady + Brad Stevens |
| 6 | Add .DS_Store to .gitignore | Brad Stevens |
| 7 | Create `data/PROVENANCE.md` | Brock Purdy |
| 8 | Audit view/archetype counts for consistency | Stephen Curry |
| 9 | Define baselines vs tags with deltas | Andy Flower + Stephen Curry |
| 10 | Implement schema validation tests | N'Golo Kanté |
| 11 | Define expected schemas per output | N'Golo Kanté |
| 12 | Update PRD for magazine-style focus | Tom Brady |

### P1 - High Priority

| # | Action Item | Owner |
|---|-------------|-------|
| 1 | Auto-updating manifest system | Brock Purdy |
| 2 | Outputs changelog generator | Brock Purdy |
| 3 | Silhouette score / inertia validation | Ime Udoka |
| 4 | Limitations section in outputs | Andy Flower |
| 5 | Archive outdated documents | Brad Stevens |
| 6 | Create .github/workflows/README.md | Brad Stevens |
| 7 | Insight Confidence Framework | Andy Flower + Jose Mourinho |
| 8 | Editorial/Analytical handoff process | Tom Brady |

### P2 - Medium Priority

| # | Action Item | Owner |
|---|-------------|-------|
| 1 | DuckDB scalability research | Brock Purdy + Ime Udoka |
| 2 | Fix CI/CD error emails | Brad Stevens |
| 3 | Artifact comparison in CI | Brock Purdy |

---

## New Agents Required

| Agent | Role | Created By |
|-------|------|------------|
| **Florentino Perez** | Strategic Gatekeeper - value validation | Brad Stevens |
| **Jose Mourinho** | Data Robustness Guardian - baselines, scalability | Brad Stevens |

---

## Documents to Create

| Document | Location | Owner |
|----------|----------|-------|
| TASK_INTEGRITY_LOOP.md | `governance/` | Florentino Perez + Tom Brady |
| CONSTITUTION.md v2.0 | `config/` | Brad Stevens + Florentino Perez + Tom Brady |
| HOW_IT_WORKS.md | `docs/` | Tom Brady + Brad Stevens |
| PROVENANCE.md | `data/` | Brock Purdy |
| baselines_vs_tags.md | `analysis/` | Stephen Curry + Andy Flower |

---

**IMPORTANT:** Constitution document requires Founder approval before commit.

---

*Cricket Playbook - Mega Review #1 Action Plan*
*Tom Brady, Product Owner*
*2026-01-31*
