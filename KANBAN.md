# Cricket Playbook - Sprint Kanban

**Last Updated:** 2026-01-19
**Sprint:** IPL 2026 Analytics Sprint
**Owner:** Tom Brady (Product Owner)

---

## 📋 BACKLOG

| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| Visualization templates | Kevin De Bruyne | Medium | Analytics layer ready |
| Editorial templates | LeBron James | Low | Magazine structure |
| Player photo/headshot integration | Brock Purdy | Low | Requires image sourcing |

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
| **IPL 2026 squad data** (`ipl_2026_squads.csv`) | Andy Flower | 2026-01-19 | Tom Brady ✅ |
| **IPL 2026 contracts data** (`ipl_2026_player_contracts.csv`) | Andy Flower | 2026-01-19 | Tom Brady ✅ |
| **IPL-specific analytics** (`analytics_ipl.py`) | Stephen Curry | 2026-01-19 | Tom Brady ✅ |
| **IPL phase-wise views** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |
| **Batter vs bowler type analysis** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |
| **All T20 comparison views** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |
| **Squad integration views** | Stephen Curry | 2026-01-19 | Tom Brady ✅ |

---

## 🚫 BLOCKED

| Task | Owner | Blocker | Resolution Needed |
|------|-------|---------|-------------------|
| - | - | - | - |

---

## 📊 Sprint Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed | 21 |
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

### Analytics Sprint (Complete)
- [x] Core batting metrics
- [x] Core bowling metrics
- [x] Player comparison views
- [ ] Sample visualizations

### IPL 2026 Sprint (Complete)
- [x] IPL 2026 squad data collection (all 10 teams)
- [x] Player classification (role, bowling type, batting hand)
- [x] Contract data (prices, acquisition type, year joined)
- [x] IPL-specific analytics views
- [x] Phase-wise batting/bowling breakdown
- [x] Batter vs bowler type analysis
- [x] All T20 comparison views
- [x] Squad integration views

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

**Andy Flower's IPL 2026 Data Report (2026-01-19):**

> IPL 2026 squad data collected for all 10 teams after the December 2025 mini auction.
>
> **Data Files Created:**
> - `data/ipl_2026_squads.csv` - 200+ players with classifications
> - `data/ipl_2026_player_contracts.csv` - Prices, acquisition type, year joined
>
> **Player Classifications:**
> - Role: Batter, Bowler, All-rounder, Wicketkeeper
> - Bowling type: Fast, Medium, Off-spin, Leg-spin, Left-arm orthodox, Left-arm wrist spin
> - Bowling arm: Right-arm, Left-arm
> - Batting hand: Right-hand, Left-hand
>
> **Notable Auction Highlights:**
> - Cameron Green to KKR: ₹25.20 crore (most expensive overseas player ever)
> - Rishabh Pant retained by LSG: ₹27 crore (highest paid player)
> - Kartik Sharma & Prashant Veer to CSK: ₹14.20 crore each (joint-most expensive uncapped)

**Stephen Curry's IPL 2026 Analytics Report (2026-01-19):**

> IPL Analytics layer v2.0.0 is live with 14 new IPL-specific views.
>
> **IPL Batting Views (4):**
> - `analytics_ipl_batting_career` - IPL-only career stats
> - `analytics_ipl_batter_phase` - Powerplay/middle/death IPL splits
> - `analytics_ipl_batter_vs_bowler` - IPL head-to-head matchups
> - `analytics_ipl_batter_vs_bowler_type` - Performance vs fast/spin/medium
>
> **IPL Bowling Views (2):**
> - `analytics_ipl_bowling_career` - IPL-only career bowling stats
> - `analytics_ipl_bowler_phase` - Phase-wise economy, wickets, dot %
>
> **All T20 Comparison Views (3):**
> - `analytics_t20_batter_phase` - All T20 phase breakdown
> - `analytics_t20_batter_vs_bowler_type` - All T20 vs bowler types
> - `analytics_t20_bowler_phase` - All T20 bowler phase stats
>
> **Squad Integration Views (5):**
> - `analytics_ipl_squad_batting` - 2026 squad with IPL + All T20 batting stats
> - `analytics_ipl_squad_bowling` - 2026 squad with IPL + All T20 bowling stats
> - `analytics_ipl_squad_batting_phase` - Phase-wise batting by squad
> - `analytics_ipl_squad_bowling_phase` - Phase-wise bowling by squad
> - `analytics_ipl_team_roster` - Full roster with contract details
>
> **Sample Queries:**
> ```sql
> -- RCB 2026 squad batting analysis
> SELECT * FROM analytics_ipl_squad_batting
> WHERE team_name = 'Royal Challengers Bengaluru';
>
> -- Kohli IPL vs All T20 phase comparison
> SELECT 'IPL', * FROM analytics_ipl_batter_phase WHERE player_name LIKE '%Kohli%'
> UNION ALL
> SELECT 'All T20', * FROM analytics_t20_batter_phase WHERE player_name LIKE '%Kohli%';
> ```
>
> Total views now: 31 (17 original + 14 IPL-specific)

---

*Maintained by Tom Brady, Product Owner & Editor-in-Chief*
