# TKT-181: Film Room SQL Views Overhaul — Founder Review

**Date:** 2026-02-11
**Owner:** Stephen Curry (Analytics Lead)
**Reviewers:** Andy Flower (Domain QA), Tom Brady (Enforcement)
**Branch:** `feature/TKT-181-film-room-views-overhaul`
**Commit:** `e18b3de`

---

## Summary

Overhauled the Film Room analytics layer to address three problems:
1. **No scope clarity** — existing IPL views mixed all-time and 2023+ data with no way to tell which
2. **Missing tactical views** — key analytical questions (entry points, match context, innings progression) had no SQL views
3. **No standardized naming** — consumers had to read source code to understand what data range a view covered

## What Changed

### File Modified
`scripts/core/analytics_ipl.py` (+1,833 lines, now 3,292 total)

### Two New Functions Added

**`create_standardized_ipl_views(conn)`** — 54 views (27 pairs)
- For every existing IPL view, creates `_alltime` and `_since2023` variants
- Pattern A views (already all-time): alias as `_alltime`, new SQL with date filter for `_since2023`
- Pattern B views (already 2023+): alias as `_since2023`, new SQL without date filter for `_alltime`
- 6 initial bugs found by Andy Flower QA and fixed before commit

**`create_film_room_views(conn)`** — 26 views (13 pairs)
- 13 new tactical views, each with `_alltime` and `_since2023` variants
- Uses `_dual_view()` helper with `{DATE_FILTER}` placeholder

### View Inventory After Change

| Category | Count | Notes |
|----------|-------|-------|
| Original base views | 35 | Unchanged, backward-compatible |
| Dual-scope standardized | 54 | 27 existing x 2 scope variants |
| Film Room (new) | 26 | 13 new x 2 scope variants |
| **Total** | **115** | Up from 35 |

### 13 New Film Room Views

| # | View Name | What It Answers |
|---|-----------|-----------------|
| 1 | `batter_entry_point` | When/where do batters enter during chases? What's the team situation? |
| 2 | `match_context` | Full match summary — both innings totals, chase result, margin |
| 3 | `innings_progression` | Over-by-over cumulative runs, wickets, run rate, required rate |
| 4 | `batting_order_flexibility` | Do teams push batters down when early wickets fall? |
| 5 | `bowler_over_breakdown` | Per-over (1-20) economy, dot%, boundary% for each bowler |
| 6 | `new_batter_vulnerability` | First 10 balls vs settled performance — SR gap, dismissal rate |
| 7 | `partnership_analysis` | Batting pair combos — runs, balls, boundary%, appearances |
| 8 | `dot_ball_pressure` | Consecutive dots and their correlation with wickets |
| 9 | `wicket_clusters` | 2+ wickets within 12-ball windows — collapse detection |
| 10 | `team_phase_scoring` | Team-level run rates by phase (powerplay/middle/death) |
| 11 | `required_rate_performance` | Batter SR at required run rates >8, >10, >12 |
| 12 | `venue_profile` | Venue aggregate run rates, boundary%, avg scores |
| 13 | `bowling_change_impact` | First over of bowling spell vs continuation overs |

## QA Validation (Andy Flower)

### Comprehensive Report
- **132 total views** in database (includes non-analytics)
- **0 empty views**, **0 SQL errors**, **0 quoting issues**
- **34/40 dual-scope pairs** initially correct
- **6 bugs found and fixed** before commit:
  - 5 `_since2023` views were aliasing unfiltered all-time data
  - 1 `_alltime` view was aliasing 2023-filtered data
- **Date range verified**: since2023 starts 2023-03-31, alltime goes back to 2008-04-18
- **Row count sanity**: alltime >= since2023 for all pairs (e.g., batting_career: 702 vs 271)

### Downstream Impact Assessment
- Existing scripts (clustering, stat packs, The Lab) use **base view names only**
- No existing analysis was affected by the 6 bugs
- Bugs were fixed proactively for naming convention integrity

## Naming Convention

Every IPL analytics view now follows: `analytics_ipl_{topic}_{scope}`

| Scope Suffix | Data Range | IPL Matches |
|-------------|------------|-------------|
| `_alltime` | 2008-2025 | ~1,169 |
| `_since2023` | 2023-2025 | ~219 |

Base views (without suffix) remain for backward compatibility.

## Governance

| TIL Step | Status | Notes |
|----------|--------|-------|
| 0. PRD | Done | Founder requested Film Room overhaul |
| 1. Florentino Gate | APPROVED | Scope validated |
| 2. Build | DONE | 80 new views created |
| 3. Domain Sanity | DONE | Andy Flower validation (132 views, 6 bugs found + fixed) |
| 4. Enforcement | Pending | Tom Brady review |
| 5. Commit & Ship | DONE | Branch `feature/TKT-181-film-room-views-overhaul`, commit `e18b3de` |
| 6. Post Note | This document |
| 7. System Check | Pending | Kante QA |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| File grew large (3,292 lines) | Well-structured with separate functions per category |
| Views not in DuckDB until script runs | Script is idempotent, runs in analytics pipeline |
| Backward compatibility | Base views unchanged, new views are additive only |

## Founder Decision Needed

- **Approve** to merge to main and proceed with TIL Steps 4 + 7
- **Request changes** if scope or implementation needs adjustment
