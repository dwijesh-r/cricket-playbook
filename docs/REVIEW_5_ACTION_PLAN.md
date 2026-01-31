# Founder Review #5 - Action Plan

**Document Owner:** Tom Brady (Product Owner)
**Review Date:** 2026-01-31
**Binding Document:** Mega Review #1
**Status:** PLANNING

---

## Overview

Review 5 provides tactical feedback on specific repo areas. All items are evaluated against Mega Review #1's strategic direction: **magazine-style preview generator with ruthless editorial compression**.

---

## Section 1: Repo README

### 1.1 Happy Path for Viewers

**Request:** Add a happy path for people viewing the repo to get the best possible experience.

**Status:** ✅ PARTIALLY DONE - "New Here? Start Here" section added in previous sprint.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Add hyperlinks throughout README | Tom Brady | P1 | To Do |
| Review happy path completeness | Tom Brady | P1 | To Do |

---

## Section 2: GitHub Workflows

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `.github/workflows/README.md` with idea, outcome, flow | Brad Stevens | P1 | To Do |
| Investigate CI/CD error emails | Brad Stevens | P2 | To Do |

---

## Section 3: Analysis

### 3.1 Threshold Justification

**Request:** Mention why and how thresholds have been set - justification needed, can be direct.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Add threshold justification to `analysis/threshold_eda_2023.md` | Stephen Curry | P0 | To Do |
| Link to EDA evidence for each threshold | Stephen Curry | P0 | To Do |

---

## Section 4: Data

### 4.1 Archive Folder

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `data/archive/` folder | Brock Purdy | P1 | To Do |
| Move deprecated files to archive | Brock Purdy | P1 | To Do |

### 4.2 IPL_2026_Squads Issues

#### 4.2.1 Workhorse Seamers Over-Classification

**Problem:** A lot of bowlers classified as "Workhorse Seamers" - review needed.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit bowler_classification distribution | Andy Flower | P0 | To Do |
| Review Workhorse Seamer criteria | Andy Flower | P0 | To Do |
| Rebalance classifications if needed | Stephen Curry | P0 | To Do |

#### 4.2.2 Player ID Mappings

**Status:** ✅ FIXED in commit `e386035`
- Aman Khan → Fixed (was mapping to Avesh Khan)
- Mohammed Izhar → Fixed (was mapping to Mohammed Siraj)

#### 4.2.3 Bowler Tags Standardization (CRITICAL)

**Problem:** Tags seem vague and incorrect. Example: Bumrah is elite across all phases but tagged only as "Powerplay Assassin".

**Request:** Andy Flower to standardize all tags and clusters across repo. One nomenclature only. Use 2023+ data only.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit all tag systems across repo | Andy Flower | P0 | To Do |
| Create unified tag nomenclature document | Andy Flower | P0 | To Do |
| Review Bumrah and similar elite players | Andy Flower | P0 | To Do |
| Implement single tag system | Stephen Curry | P0 | To Do |
| Update all outputs with standardized tags | Stephen Curry | P1 | To Do |
| Verify 2023+ data only for tagging | Stephen Curry | P0 | To Do |

### 4.3 IPL_2026_Player_Contracts

**Problem:** Some retained players show as "Auction" (Romario Shepherd, Nitish Rana was traded).

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit contract categories | Brock Purdy | P2 | To Do |
| Fix incorrect categories | Brock Purdy | P2 | To Do |

---

## Section 5: ML Ops

### 5.1 Product Description Document

**Request:** Detailed document with goal, desired outcome, process, final outcome. Not a black box - transparent. Visualizations needed.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `ml_ops/PRODUCT_DESCRIPTION.md` | Ime Udoka | P0 | To Do |
| Add goal and desired outcome | Ime Udoka | P0 | To Do |
| Document full process with steps | Ime Udoka | P0 | To Do |
| Add visualizations | Kevin de Bruyne | P1 | To Do |
| Include interpretation guide | Andy Flower | P1 | To Do |

---

## Section 6: Notebooks

### 6.1 User Guide

**Clarification:** Notebooks are for external users to run custom queries.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create `notebooks/USER_GUIDE.md` | Stephen Curry | P1 | To Do |
| Document how to use notebooks | Stephen Curry | P1 | To Do |
| Add efficient query examples | Stephen Curry | P1 | To Do |
| Document available columns | Stephen Curry | P1 | To Do |

---

## Section 7: Outputs

### 7.1 README Standardization

**Request:** Tag Categories - Andy Flower to review and standardize across all docs. One standard system only. Add purpose and qualitative description.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Standardize tag categories in outputs/README | Andy Flower | P0 | To Do |
| Add purpose/qualitative help description | Andy Flower | P1 | To Do |

### 7.2 Matchups Data Issues (CRITICAL)

#### 7.2.1 batter_bowling_type_detail_2023.csv

**Problem:** Aiden Markram only shows stats against right arm off spin and right arm pace. File seems incomplete.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit Aiden Markram data completeness | Stephen Curry | P0 | To Do |
| Reconcile with overall career numbers | Stephen Curry | P0 | To Do |
| Fix data generation if incomplete | Stephen Curry | P0 | To Do |

#### 7.2.2 batter_bowling_type_matchup_2023.csv

**Problems:**
1. Devdutt Padikkal and Cameron Green have no pace_balls and pace_strike although they've played against pace since 2023
2. Only 64 players - need to include everyone

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit Devdutt Padikkal pace data | Stephen Curry | P0 | To Do |
| Audit Cameron Green pace data | Stephen Curry | P0 | To Do |
| Verify player count (should include all squad players) | Stephen Curry | P0 | To Do |
| Reconcile with overall numbers | Stephen Curry | P0 | To Do |
| Fix data generation script | Stephen Curry | P0 | To Do |

### 7.3 Subdirectory READMEs

**Request:** README for each subdirectory with metadata for each CSV and how to interpret them.

| Subdirectory | Action | Owner | Priority |
|--------------|--------|-------|----------|
| `outputs/matchups/` | Create README with classifications and basis | Stephen Curry | P0 |
| `outputs/tags/` | Create README with approach and interpretation | Andy Flower | P0 |
| `outputs/metrics/` | Create README (if not exists) | Stephen Curry | P1 |
| `outputs/team/` | Create README with description | Stephen Curry | P1 |
| `outputs/run-logs/` | Create README with purpose | Brock Purdy | P1 |

---

## Section 8: Reviews

### 8.1 Sprint Subfolders

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create subfolders by sprint in `reviews/sprint/` | Brad Stevens | P2 | To Do |
| Reorganize existing sprint files | Brad Stevens | P2 | To Do |

---

## Section 9: Domain Research (Andy Flower)

### 9.1 Approved Ideas - Scope Out

| Idea | Description | Owner | Priority |
|------|-------------|-------|----------|
| Match Phase Index (Historical) | Adapt for past matches - how teams react in pressure situations | Andy Flower + Stephen Curry | P1 |
| Match Turning Point (Historical) | Identify turning points in past matches | Andy Flower + Stephen Curry | P1 |
| Clutch Performance Measurement | For batters and bowlers - define "expected" component | Andy Flower + Ime Udoka | P1 |
| Tactical Pattern Recognition | Analyze which bowler types in certain situations | Andy Flower + Stephen Curry | P2 |
| Toss Advantage Index | Scope and implement | Andy Flower + Stephen Curry | P1 |
| Novel Composite Metrics | Per KenPom research | Stephen Curry + Ime Udoka | P2 |

### 9.2 On Hold

| Idea | Reason |
|------|--------|
| Batting Intent Classification | Vague - four may not be attacking, single may not be rotation |
| Fielding Metrics | Not of great importance right now |

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create scoping doc for Match Phase Index (historical) | Andy Flower | P1 | To Do |
| Create scoping doc for Clutch Performance | Andy Flower | P1 | To Do |
| Create scoping doc for Toss Advantage Index | Andy Flower | P1 | To Do |

---

## Section 10: Scripts

### 10.1 Code Quality

**Request:** Each script well-written, good standards, enough metadata and comments for anyone to understand.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Audit all scripts for documentation | Brad Stevens | P1 | To Do |
| Add docstrings to all functions | Stephen Curry + Brock Purdy | P1 | To Do |
| Add script header comments | Stephen Curry + Brock Purdy | P1 | To Do |
| Create script documentation template | Brad Stevens | P1 | To Do |

---

## Section 11: Stat Packs (CRITICAL - Core Product)

### 11.1 Embed Archetypes/Tags

**Problem:** Player Archetypes and Key Player Tags don't add value as standalone sections.

**Solution:** Embed them in other tables.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Embed archetypes in player tables | Virat Kohli + Stephen Curry | P0 | To Do |
| Embed tags in overview table | Virat Kohli + Stephen Curry | P0 | To Do |
| Remove standalone archetype section | Virat Kohli | P0 | To Do |

### 11.2 Historical Record vs Opposition

**Request:** Present in tabular format.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Convert to markdown table format | Virat Kohli | P0 | To Do |

### 11.3 Venue Performance

**Request:** Just give record only (W-L). Runs/balls don't matter at team level. Add dot ball % and boundary % for batting and bowling.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Simplify to W-L record only | Virat Kohli | P0 | To Do |
| Add batting dot ball % | Stephen Curry | P0 | To Do |
| Add batting boundary % | Stephen Curry | P0 | To Do |
| Add bowling dot ball % | Stephen Curry | P0 | To Do |
| Add bowling boundary % | Stephen Curry | P0 | To Do |

### 11.4 Tactical Insights (CRITICAL)

**Problem:** Seems really vague and not well thought of. Has to add enough value.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Review all tactical insights | Andy Flower + Virat Kohli | P0 | To Do |
| Make insights specific and data-backed | Virat Kohli | P0 | To Do |
| Add editorial narrative | Virat Kohli | P0 | To Do |
| Ensure each insight is actionable | Andy Flower | P0 | To Do |

### 11.5 NEW SECTIONS (Important - Scope Out)

#### 11.5.1 Predicted XI

**Requirements:**
- Based on: experience, fit, best possible outcome
- Optimize for: best SR, best economy, best boundary%, best dot ball%
- Consider: role fit, batting depth, bowling depth, variety
- Account for: matchups

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create Predicted XI algorithm | Stephen Curry + Pep Guardiola | P0 | To Do |
| Define optimization criteria | Andy Flower | P0 | To Do |
| Implement role fit scoring | Stephen Curry | P0 | To Do |
| Implement depth scoring | Stephen Curry | P0 | To Do |
| Account for variety (pace/spin, LHB/RHB) | Stephen Curry | P0 | To Do |
| Integrate matchup considerations | Stephen Curry | P1 | To Do |
| Create explanation narrative | Virat Kohli | P1 | To Do |

#### 11.5.2 Depth Charts

**Requirements:** Depth chart for each role and position.

| Role | Players to Rank |
|------|-----------------|
| Opener | Top 3 options |
| #3 | Top 3 options |
| Middle Order (#4-5) | Top 3 options |
| Finisher (#6-7) | Top 3 options |
| Wicketkeeper | Primary + backup |
| Lead Pacer | Top 2 options |
| Supporting Pacer | Top 3 options |
| Lead Spinner | Top 2 options |
| All-rounder | Batting + Bowling options |

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Define depth chart positions | Andy Flower | P0 | To Do |
| Create ranking algorithm per position | Stephen Curry | P0 | To Do |
| Generate depth charts for all 10 teams | Stephen Curry | P0 | To Do |
| Add to stat pack template | Virat Kohli | P0 | To Do |

---

## Section 12: Tests

### 12.1 README Enhancement

**Request:** What is the purpose? What is the outcome? Plan?

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Update tests/README.md with purpose | N'Golo Kanté | P1 | To Do |
| Add outcome expectations | N'Golo Kanté | P1 | To Do |
| Add test plan and roadmap | N'Golo Kanté | P1 | To Do |

---

## Section 13: Brad Stevens Tasks

### 13.1 Agent Performance Review

**Request:** Review agent performance, look at repetitive issues, rate them, analyze improvement areas, determine if retraining needed or more agents needed.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Conduct agent performance audit | Brad Stevens | P1 | To Do |
| Identify repetitive issues | Brad Stevens | P1 | To Do |
| Create agent rating system | Brad Stevens | P1 | To Do |
| Document improvement recommendations | Brad Stevens | P1 | To Do |

### 13.2 Jose Mourinho Ecosystem Analysis

**Request:** Get Jose Mourinho in the loop, analyze whole ecosystem and progress, provide report and next steps.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Create Jose Mourinho agent file | Brad Stevens | P0 | To Do |
| Jose Mourinho ecosystem analysis | Jose Mourinho | P1 | To Do |
| Jose Mourinho progress report | Jose Mourinho | P1 | To Do |

---

## Section 14: Research

### 14.1 KenPom Research

**Founder Feedback:** Love the idea. For small season and pre-season focus, retain crux to:
- Players' individual performances since 2023
- Team's expected finishes in upcoming season

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Scope KenPom-style model for pre-season | Ime Udoka | P1 | To Do |
| Focus on 2023+ individual performance | Ime Udoka | P1 | To Do |
| Add team expected finish predictions | Ime Udoka | P2 | To Do |

### 14.2 PFF Research

**Founder Feedback:** Based on qualitative assessment - not feasible without commentary/tape access.

| Action Item | Owner | Priority | Status |
|-------------|-------|----------|--------|
| Deprioritize PFF implementation | Ime Udoka | - | Done |
| Archive for future reference | Ime Udoka | P2 | To Do |

---

## Summary: Review 5 Action Items by Priority

### P0 - Critical (Core Product Impact)

| # | Action Item | Owner |
|---|-------------|-------|
| 1 | Standardize all tags across repo (Andy Flower) | Andy Flower |
| 2 | Fix matchup data completeness (Aiden Markram, Devdutt, Cameron Green) | Stephen Curry |
| 3 | Ensure all 231 players in matchup files | Stephen Curry |
| 4 | Add threshold justification to analysis | Stephen Curry |
| 5 | Create ML Ops Product Description document | Ime Udoka |
| 6 | Audit Workhorse Seamer over-classification | Andy Flower |
| 7 | Embed archetypes/tags in stat pack tables | Virat Kohli + Stephen Curry |
| 8 | Improve tactical insights in stat packs | Andy Flower + Virat Kohli |
| 9 | Create Predicted XI feature | Stephen Curry + Pep Guardiola |
| 10 | Create Depth Charts feature | Stephen Curry + Andy Flower |
| 11 | Venue Performance: W-L only + dot%/boundary% | Stephen Curry + Virat Kohli |
| 12 | Create outputs/matchups/README.md | Stephen Curry |
| 13 | Create outputs/tags/README.md | Andy Flower |
| 14 | Create Jose Mourinho agent | Brad Stevens |

### P1 - High Priority

| # | Action Item | Owner |
|---|-------------|-------|
| 1 | Add hyperlinks to main README | Tom Brady |
| 2 | Create .github/workflows/README.md | Brad Stevens |
| 3 | Create data/archive/ folder | Brock Purdy |
| 4 | Add visualizations to ML Ops docs | Kevin de Bruyne |
| 5 | Create notebooks/USER_GUIDE.md | Stephen Curry |
| 6 | Scope Match Phase Index (historical) | Andy Flower |
| 7 | Scope Clutch Performance Measurement | Andy Flower |
| 8 | Scope Toss Advantage Index | Andy Flower |
| 9 | Script documentation audit | Brad Stevens |
| 10 | Agent performance review | Brad Stevens |
| 11 | Jose Mourinho ecosystem analysis | Jose Mourinho |
| 12 | KenPom pre-season model scoping | Ime Udoka |

### P2 - Medium Priority

| # | Action Item | Owner |
|---|-------------|-------|
| 1 | Fix CI/CD error emails | Brad Stevens |
| 2 | Fix contract categories (Romario Shepherd, etc.) | Brock Purdy |
| 3 | Sprint review subfolders | Brad Stevens |
| 4 | Tactical Pattern Recognition scoping | Andy Flower |

---

## Cross-Reference: Mega Review Alignment

| Review 5 Item | Mega Review Alignment |
|---------------|----------------------|
| Tag Standardization | Supports "single source of truth" principle |
| Matchup Data Completeness | Supports "baselines clear" requirement |
| Stat Pack Improvements | Aligns with "magazine-style" product vision |
| Predicted XI / Depth Charts | Core to "scouting-style editorial" USP |
| Tactical Insights | Supports "ruthless editorial compression" |
| ML Ops Documentation | Aligns with "no silent assumptions" |

---

*Cricket Playbook - Review 5 Action Plan*
*Tom Brady, Product Owner*
*2026-01-31*
