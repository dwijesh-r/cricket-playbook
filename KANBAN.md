# Cricket Playbook - Sprint Kanban

**Last Updated:** 2026-01-19
**Sprint:** Analytics Sprint
**Owner:** Tom Brady (Product Owner)

---

## 📋 BACKLOG

| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| External player attributes (LHB/RHB, bowling style) | Brock Purdy | Low | Requires ESPNcricinfo enrichment |
| Visualization templates | Kevin De Bruyne | Medium | Analytics layer ready |
| Editorial templates | LeBron James | Low | Magazine structure |

---

## 🔄 IN PROGRESS

| Task | Owner | Started | Status |
|------|-------|---------|--------|
| - | - | - | - |

---

## ✅ DONE (This Sprint)

| Task | Owner | Completed | Sign-off |
|------|-------|-----------|----------|
| Schema design | Brock Purdy | 2026-01-19 | Tom Brady ✅ |
| Ingestion pipeline (`ingest.py`) | Brock Purdy | 2026-01-19 | Tom Brady ✅ |
| Data load (9,357 matches) | Brock Purdy | 2026-01-19 | N'Golo Kanté ✅ |
| QA certification | N'Golo Kanté | 2026-01-19 | PASS |
| Cricket domain review | Andy Flower | 2026-01-19 | APPROVE w/ caveats |
| Structure review | Tom Brady | 2026-01-19 | APPROVED |
| Git repo setup | - | 2026-01-19 | ✅ |
| Virtual environment + deps | - | 2026-01-19 | ✅ |
| **Add `is_wicketkeeper` flag** | Brock Purdy | 2026-01-19 | Andy Flower ✅ |
| **Add `match_phase` column** | Brock Purdy | 2026-01-19 | Andy Flower ✅ |
| **GitHub Actions workflow** | Brock Purdy | 2026-01-19 | Tom Brady ✅ |
| **Analytics layer - batting metrics** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |
| **Analytics layer - bowling metrics** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |
| **Player comparison views** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |

---

## 🚫 BLOCKED

| Task | Owner | Blocker | Resolution Needed |
|------|-------|---------|-------------------|
| - | - | - | - |

---

## 📊 Sprint Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed | 14 |
| Tasks In Progress | 0 |
| Tasks Blocked | 0 |
| Tasks in Backlog | 3 |

---

## 🎯 Sprint Goals

### Foundation Sprint (Complete)
- [x] Data ingestion pipeline
- [x] Schema design and implementation
- [x] QA certification
- [x] Domain review
- [x] GitHub Actions setup

### Analytics Sprint (Current)
- [x] Core batting metrics
- [x] Core bowling metrics
- [x] Player comparison views
- [ ] Sample visualizations

---

## 📝 Notes

**Stephen Curry's Analytics Report (2026-01-19):**

> Analytics layer v1.0.0 is live with 17 views.
>
> **Batting Views (6):**
> - `analytics_batting_career` - Career stats with SR, avg, boundaries
> - `analytics_batting_by_phase` - Powerplay/middle/death splits
> - `analytics_batting_by_tournament` - Per-tournament stats
> - `analytics_batting_by_season` - Yearly progression
> - `analytics_top_run_scorers` - Leaderboard (10+ innings)
> - `analytics_best_strike_rates` - Qualified batters (500+ balls)
> - `analytics_powerplay_hitters` - PP specialists (200+ balls)
>
> **Bowling Views (6):**
> - `analytics_bowling_career` - Career stats with economy, avg, SR
> - `analytics_bowling_by_phase` - Phase splits
> - `analytics_bowling_by_tournament` - Per-tournament stats
> - `analytics_top_wicket_takers` - Leaderboard (10+ matches)
> - `analytics_best_economy` - Qualified bowlers (500+ balls)
> - `analytics_death_over_specialists` - Death overs (200+ balls)
>
> **Matchup Views (2):**
> - `analytics_batter_vs_bowler` - Head-to-head
> - `analytics_batter_vs_team` - Batter vs opposition
>
> **Team Views (2):**
> - `analytics_team_batting` - Team batting aggregates
> - `analytics_team_bowling` - Team bowling aggregates
>
> All views include sample size indicators per Andy Flower's recommendation.

**Tom Brady's Assessment (2026-01-19):**

> Excellent progress on the foundation sprint. We've gone from zero to a fully operational data pipeline in one session. The schema is solid, QA-certified, and cricket-approved.
>
> Key wins:
> - 9,357 matches loaded with full ball-by-ball granularity
> - Derived player roles working (with noted caveats)
> - Clean separation of concerns across agents
>
> Analytics layer now complete - 17 views ready for visualization.

---

*Maintained by Tom Brady, Product Owner & Editor-in-Chief*
