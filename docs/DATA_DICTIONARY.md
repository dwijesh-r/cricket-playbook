# Data Dictionary

**Owner:** Brock Purdy (Data Pipeline Lead)
**Version:** 1.0.0
**Last Updated:** 2026-02-06
**Status:** REVIEW (TKT-032)

---

## Overview

This document provides a comprehensive reference for all data structures in Cricket Playbook, including:
- Database tables and views in `data/cricket_playbook.duckdb`
- Reference CSV files
- Key relationships and data types
- Sample values for enumerated fields

---

## Database Schema

### Star Schema Architecture

```
                    +------------------+
                    |  dim_tournament  |
                    +--------+---------+
                             |
+-------------+    +---------+---------+    +------------+
|  dim_venue  |----+     dim_match     +----+  dim_team  |
+-------------+    +---------+---------+    +------------+
                             |
                    +--------+---------+
                    |    fact_ball     |
                    +--------+---------+
                             |
                    +--------+---------+
                    |   dim_player     |
                    +-----------------+
```

The database uses a star schema with `fact_ball` as the central fact table, containing 2.1M+ ball-by-ball delivery records from T20 matches worldwide.

---

## Dimension Tables

### dim_match

**Description:** Match-level metadata for all T20 matches.
**Row Count:** 9,357

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| match_id | VARCHAR | NO | Primary key - Cricsheet match identifier |
| tournament_id | VARCHAR | YES | FK to dim_tournament |
| match_number | DOUBLE | YES | Match sequence within tournament |
| stage | VARCHAR | YES | Tournament stage (Group, Qualifier, Final) |
| season | VARCHAR | YES | Season/year identifier |
| match_date | VARCHAR | YES | Date played (YYYY-MM-DD format) |
| venue_id | VARCHAR | YES | FK to dim_venue |
| team1_id | VARCHAR | YES | FK to dim_team (first team) |
| team2_id | VARCHAR | YES | FK to dim_team (second team) |
| toss_winner_id | VARCHAR | YES | FK to dim_team |
| toss_decision | VARCHAR | YES | `bat` or `field` |
| winner_id | VARCHAR | YES | FK to dim_team |
| outcome_type | VARCHAR | YES | `runs`, `wickets`, `tie`, `no result` |
| outcome_margin | DOUBLE | YES | Margin of victory |
| player_of_match_id | VARCHAR | YES | FK to dim_player |
| balls_per_over | BIGINT | YES | Typically 6 |
| data_version | VARCHAR | YES | Cricsheet data version |
| is_active | BOOLEAN | YES | Record active flag (soft delete) |
| ingested_at | VARCHAR | YES | ISO timestamp of ingestion |
| source_file | VARCHAR | YES | Source JSON file path |

---

### dim_player

**Description:** Player dimension containing all T20 players.
**Row Count:** 7,864

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | NO | Primary key - 8-char hex Cricsheet ID |
| current_name | VARCHAR | YES | Current display name |
| first_seen_date | VARCHAR | YES | First match appearance date |
| last_seen_date | VARCHAR | YES | Most recent match date |
| matches_played | BIGINT | YES | Total matches in database |
| is_wicketkeeper | BOOLEAN | YES | Derived from keeping duties |
| primary_role | VARCHAR | YES | Derived: `Batter`, `Bowler`, `All-rounder`, `Unknown` |

**Sample Values - primary_role:**
- `Batter`
- `Bowler`
- `All-rounder`
- `Unknown`

---

### dim_team

**Description:** Team/franchise dimension.
**Row Count:** 285

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_id | VARCHAR | NO | Primary key (hash) |
| team_name | VARCHAR | YES | Full team name |
| short_name | VARCHAR | YES | Abbreviated name |

**Sample Values - team_name:**
- `Chennai Super Kings`
- `Mumbai Indians`
- `Royal Challengers Bangalore`
- `Rajasthan Royals`

---

### dim_venue

**Description:** Stadium/venue dimension.
**Row Count:** 531

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| venue_id | VARCHAR | NO | Primary key (hash) |
| venue_name | VARCHAR | YES | Full stadium name |
| city | VARCHAR | YES | City location |

---

### dim_tournament

**Description:** Tournament/competition dimension.
**Row Count:** 426

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| tournament_id | VARCHAR | NO | Primary key |
| tournament_name | VARCHAR | YES | Full tournament name |
| country | VARCHAR | YES | Primary host country |
| format | VARCHAR | YES | Match format (T20) |
| gender | VARCHAR | YES | `male` or `female` |

**Sample Values - tournament_name:**
- `Indian Premier League`
- `ICC Men's T20 World Cup`
- `Big Bash League`
- `Caribbean Premier League`
- `Pakistan Super League`

---

### dim_player_name_history

**Description:** Tracks player name changes over time.
**Row Count:** 7,888

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player |
| player_name | VARCHAR | YES | Name used in this period |
| valid_from | VARCHAR | YES | Start date of name usage |
| valid_to | VARCHAR | YES | End date (NULL if current) |
| source_file | VARCHAR | YES | Source file for name |

---

### dim_bowler_classification

**Description:** Manual bowling style classifications for bowlers.
**Row Count:** 430

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player (Cricsheet ID) |
| player_name | VARCHAR | YES | Player display name |
| bowling_style | VARCHAR | YES | Standardized bowling style |

**Sample Values - bowling_style:**
- `Right-arm pace`
- `Left-arm pace`
- `Right-arm off-spin`
- `Right-arm leg-spin`
- `Left-arm orthodox`
- `Left-arm wrist spin`

---

### dim_franchise_alias

**Description:** Maps team name variations to canonical names.
**Row Count:** 19

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_name | VARCHAR | YES | Team name variant |
| canonical_name | VARCHAR | YES | Standardized team name |

---

## Fact Tables

### fact_ball

**Description:** Core fact table - one row per delivery in T20 matches.
**Row Count:** 2,137,915

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ball_id | VARCHAR | NO | Primary key - unique ball identifier |
| match_id | VARCHAR | YES | FK to dim_match |
| innings | BIGINT | YES | Innings number (1 or 2) |
| over | BIGINT | YES | Over number (0-19) |
| ball | BIGINT | YES | Ball within over (1-6+) |
| ball_seq | BIGINT | YES | Sequential ball number in innings |
| batting_team_id | VARCHAR | YES | FK to dim_team |
| bowling_team_id | VARCHAR | YES | FK to dim_team |
| batter_id | VARCHAR | YES | FK to dim_player (striker) |
| bowler_id | VARCHAR | YES | FK to dim_player |
| non_striker_id | VARCHAR | YES | FK to dim_player |
| batter_runs | BIGINT | YES | Runs scored off bat (0-6) |
| extra_runs | BIGINT | YES | Extras (wides, noballs, etc.) |
| total_runs | BIGINT | YES | batter_runs + extra_runs |
| extra_type | VARCHAR | YES | Type of extra (if applicable) |
| is_wicket | BOOLEAN | YES | Whether wicket fell on this ball |
| wicket_type | VARCHAR | YES | Type of dismissal (if applicable) |
| player_out_id | VARCHAR | YES | FK to dim_player (dismissed batter) |
| fielder_id | VARCHAR | YES | FK to dim_player (fielder involved) |
| is_legal_ball | BOOLEAN | YES | FALSE for wides/noballs |
| match_phase | VARCHAR | YES | Derived phase of match |
| data_version | VARCHAR | YES | Cricsheet data version |
| ingested_at | VARCHAR | YES | Ingestion timestamp |
| source_file | VARCHAR | YES | Source file path |

**Sample Values - match_phase:**
- `powerplay` (overs 0-5)
- `middle` (overs 6-14)
- `death` (overs 15-19)

**Sample Values - wicket_type:**
- `bowled`
- `caught`
- `caught and bowled`
- `lbw`
- `run out`
- `stumped`
- `hit wicket`
- `retired hurt`
- `retired out`
- `obstructing the field`

**Sample Values - extra_type:**
- `wides`
- `noballs`
- `byes`
- `legbyes`
- `penalty`

**Match Phase Derivation Logic:**
```sql
CASE
  WHEN over < 6 THEN 'powerplay'
  WHEN over < 15 THEN 'middle'
  ELSE 'death'
END
```

---

### fact_player_match_performance

**Description:** Player participation and role per match.
**Row Count:** 195,510

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player |
| match_id | VARCHAR | YES | FK to dim_match |
| team_id | VARCHAR | YES | FK to dim_team |
| batting_position | DOUBLE | YES | Position in batting order (1-11) |
| did_bat | BOOLEAN | YES | Whether player batted |
| did_bowl | BOOLEAN | YES | Whether player bowled |
| did_keep_wicket | BOOLEAN | YES | Whether player kept wicket |

---

### fact_powerplay

**Description:** Powerplay rules and timing per match.
**Row Count:** 19,167

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| powerplay_id | VARCHAR | NO | Primary key |
| match_id | VARCHAR | YES | FK to dim_match |
| innings | BIGINT | YES | Innings number |
| powerplay_seq | BIGINT | YES | Powerplay sequence number |
| powerplay_type | VARCHAR | YES | `mandatory`, `batting`, `bowling` |
| from_over | DOUBLE | YES | Start over |
| to_over | DOUBLE | YES | End over |

---

## IPL 2026 Tables

### ipl_2026_squads

**Description:** IPL 2026 team rosters with player classifications.
**Row Count:** 231

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_name | VARCHAR | YES | IPL franchise name |
| player_name | VARCHAR | YES | Full player name |
| player_id | VARCHAR | YES | FK to dim_player (Cricsheet ID) |
| nationality | VARCHAR | YES | Player nationality code (IND, AUS, etc.) |
| age | BIGINT | YES | Player age |
| role | VARCHAR | YES | Player role |
| bowling_arm | VARCHAR | YES | Bowling arm |
| bowling_type | VARCHAR | YES | Bowling style |
| batting_hand | VARCHAR | YES | Batting hand |
| batter_classification | VARCHAR | YES | Cluster-based batter archetype |
| bowler_classification | VARCHAR | YES | Cluster-based bowler archetype |
| batter_tags | VARCHAR | YES | Pipe-separated batter performance tags |
| bowler_tags | VARCHAR | YES | Pipe-separated bowler performance tags |
| is_captain | BOOLEAN | YES | TRUE if team captain |
| bowling_style | VARCHAR | YES | Detailed bowling style |

**Sample Values - role:**
- `Batter`
- `Bowler`
- `All-rounder`
- `Wicketkeeper`

**Sample Values - bowling_type:**
- `Fast`
- `Medium`
- `Off-spin`
- `Leg-spin`
- `Left-arm orthodox`
- `Left-arm wrist spin`

**Sample Values - bowling_arm:**
- `Right-arm`
- `Left-arm`

**Sample Values - batting_hand:**
- `Right-hand`
- `Left-hand`

**Sample Values - batter_classification:**
- `Aggressive Opener` - High strike rate powerplay specialists
- `Anchor` - Low-risk accumulators who build innings
- `Elite Top-Order` - Premium batters who excel across phases
- `Power Finisher` - Death-over specialists with high boundary %
- `All-Round Finisher` - Batting all-rounders effective at death

**Sample Values - bowler_classification:**
- `Workhorse Seamer` - Reliable pacers across all phases
- `Powerplay Assassin` - New ball specialists with high wicket rates
- `Middle-Overs Spinner` - Economy-focused spinners for middle overs
- `Holding Spinner` - Defensive spinners who control run rate
- `Expensive Option` - High-risk, high-reward bowlers

**Sample Batter Tags:**
- `PP_DOMINATOR` - Powerplay strike rate elite
- `MIDDLE_ORDER` - Middle-order specialist
- `ACCUMULATOR` - Low dot-ball percentage
- `PACE_SPECIALIST` - Performs well vs pace
- `SPIN_SPECIALIST` - Performs well vs spin
- `VULNERABLE_VS_SPIN` - Weakness against spin

**Sample Bowler Tags:**
- `WORKHORSE` - High workload, consistent performer
- `NEW_BALL_SPECIALIST` - Excels in first 3 overs
- `DEATH_SPECIALIST` - Effective in overs 16-20
- `DEATH_ELITE` - Top-tier death bowling
- `PP_ELITE` - Powerplay wicket-taker
- `PRESSURE_BUILDER` - High dot-ball percentage
- `PROVEN_WICKET_TAKER` - Career wicket rate above average

---

### ipl_2026_contracts

**Description:** IPL 2026 player contract details.
**Row Count:** 231

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_name | VARCHAR | YES | IPL franchise name |
| player_name | VARCHAR | YES | Full player name |
| price_cr | DOUBLE | YES | Contract price in INR crores |
| acquisition_type | VARCHAR | YES | How player was acquired |
| year_joined | BIGINT | YES | Year player joined franchise |

**Sample Values - acquisition_type:**
- `Retained` - Retained before auction
- `Auction` - Purchased at auction
- `Traded` - Acquired via trade

---

## Clustering Tables

### player_clusters_batters

**Description:** K-means clustering results for batter archetypes.
**Row Count:** 87

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player |
| player_name | VARCHAR | YES | Player display name |
| cluster_id | INTEGER | YES | Cluster assignment (0-4) |
| overall_sr | DOUBLE | YES | Overall strike rate |
| overall_avg | DOUBLE | YES | Overall batting average |
| overall_boundary | DOUBLE | YES | Overall boundary percentage |
| pp_sr | DOUBLE | YES | Powerplay strike rate |
| mid_sr | DOUBLE | YES | Middle-overs strike rate |
| death_sr | DOUBLE | YES | Death-overs strike rate |
| death_boundary | DOUBLE | YES | Death-overs boundary percentage |

---

### player_clusters_bowlers

**Description:** K-means clustering results for bowler archetypes.
**Row Count:** 152

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player |
| player_name | VARCHAR | YES | Player display name |
| cluster_id | INTEGER | YES | Cluster assignment (0-4) |
| overall_economy | DOUBLE | YES | Overall economy rate |
| overall_avg | DOUBLE | YES | Overall bowling average |
| overall_dot | DOUBLE | YES | Overall dot-ball percentage |
| pp_economy | DOUBLE | YES | Powerplay economy rate |
| mid_economy | DOUBLE | YES | Middle-overs economy rate |
| death_economy | DOUBLE | YES | Death-overs economy rate |
| pp_pct | DOUBLE | YES | Percentage of overs in powerplay |
| mid_pct | DOUBLE | YES | Percentage of overs in middle |
| death_pct | DOUBLE | YES | Percentage of overs at death |

---

## Analytics Views

The database contains 51 pre-built analytics views. These are organized into categories:

### Career Statistics Views (IPL 2023-2025)

| View | Description |
|------|-------------|
| `analytics_ipl_batting_career` | Career batting stats (runs, SR, avg, boundaries) |
| `analytics_ipl_bowling_career` | Career bowling stats (wickets, economy, avg) |
| `analytics_batting_career` | All-T20 career batting stats |
| `analytics_bowling_career` | All-T20 career bowling stats |

### Phase Analysis Views

| View | Description |
|------|-------------|
| `analytics_ipl_batter_phase` | Batter performance by match phase |
| `analytics_ipl_bowler_phase` | Bowler performance by match phase |
| `analytics_ipl_batter_phase_percentiles` | Batter phase stats with percentile ranks |
| `analytics_ipl_bowler_phase_percentiles` | Bowler phase stats with percentile ranks |
| `analytics_ipl_bowler_phase_distribution` | Bowler workload distribution by phase |

### Matchup Views

| View | Description |
|------|-------------|
| `analytics_ipl_batter_vs_bowler` | Head-to-head batter vs specific bowler |
| `analytics_ipl_batter_vs_bowler_phase` | Matchups by phase |
| `analytics_ipl_batter_vs_bowler_type` | Batter vs bowling style (pace/spin) |
| `analytics_ipl_batter_vs_bowler_type_phase` | Batter vs bowling style by phase |
| `analytics_ipl_batter_vs_team` | Batter vs specific team |
| `analytics_ipl_bowler_vs_team` | Bowler vs specific team |
| `analytics_ipl_bowler_vs_batter_handedness` | Bowler vs left/right-hand batters |

### Venue Analysis Views

| View | Description |
|------|-------------|
| `analytics_ipl_batter_venue` | Batter performance by venue |
| `analytics_ipl_batter_venue_phase` | Batter venue performance by phase |
| `analytics_ipl_bowler_venue` | Bowler performance by venue |
| `analytics_ipl_bowler_venue_phase` | Bowler venue performance by phase |

### Benchmark Views

| View | Description |
|------|-------------|
| `analytics_ipl_batting_benchmarks` | League batting benchmarks |
| `analytics_ipl_bowling_benchmarks` | League bowling benchmarks |
| `analytics_ipl_career_benchmarks` | Career milestone thresholds |
| `analytics_ipl_vs_bowler_type_benchmarks` | Performance vs bowler type benchmarks |

### Percentile Views

| View | Description |
|------|-------------|
| `analytics_ipl_batting_percentiles` | Batter percentile rankings |
| `analytics_ipl_bowling_percentiles` | Bowler percentile rankings |

### Squad Analysis Views

| View | Description |
|------|-------------|
| `analytics_ipl_squad_batting` | Team batting depth analysis |
| `analytics_ipl_squad_batting_phase` | Team batting by phase |
| `analytics_ipl_squad_bowling` | Team bowling depth analysis |
| `analytics_ipl_squad_bowling_phase` | Team bowling by phase |
| `analytics_ipl_team_roster` | Full team roster view |

### All-T20 Views

| View | Description |
|------|-------------|
| `analytics_t20_batter_phase` | All-T20 batter phase performance |
| `analytics_t20_batter_vs_bowler_type` | All-T20 batter vs bowler type |
| `analytics_t20_bowler_phase` | All-T20 bowler phase performance |

### Leaderboard Views

| View | Description |
|------|-------------|
| `analytics_top_run_scorers` | Top run scorers |
| `analytics_top_wicket_takers` | Top wicket takers |
| `analytics_best_strike_rates` | Highest strike rates |
| `analytics_best_economy` | Best economy rates |
| `analytics_powerplay_hitters` | Powerplay specialists |
| `analytics_death_over_specialists` | Death-over specialists |

---

## Key Relationships

```
dim_tournament 1──M dim_match
dim_venue      1──M dim_match
dim_team       1──M dim_match (team1, team2, winner, toss_winner)
dim_match      1──M fact_ball
dim_player     1──M fact_ball (batter, bowler, non_striker, player_out, fielder)
dim_team       1──M fact_ball (batting_team, bowling_team)
dim_player     1──M ipl_2026_squads
dim_player     1──M dim_bowler_classification
dim_player     1──M player_clusters_batters
dim_player     1──M player_clusters_bowlers
```

---

## CSV Reference Files

### data/ipl_2026_squads.csv

**Description:** IPL 2026 team rosters (source file for ipl_2026_squads table).
**Records:** 231 players across 10 teams

| Column | Description |
|--------|-------------|
| team_name | IPL franchise name |
| player_name | Full player name |
| player_id | Cricsheet player ID |
| nationality | Country code (IND, AUS, ENG, etc.) |
| age | Player age |
| role | Batter, Bowler, All-rounder, Wicketkeeper |
| bowling_arm | Right-arm, Left-arm |
| bowling_type | Fast, Medium, Off-spin, Leg-spin, etc. |
| batting_hand | Right-hand, Left-hand |
| batter_classification | Cluster-based archetype |
| bowler_classification | Cluster-based archetype |
| batter_tags | Pipe-separated performance tags |
| bowler_tags | Pipe-separated performance tags |
| is_captain | TRUE if team captain |

---

### data/bowler_classifications_v3.csv

**Description:** Manually curated bowling style classifications.
**Records:** 430 bowlers (covers 98.8% of IPL balls)

| Column | Description |
|--------|-------------|
| player_id | Cricsheet player ID |
| player_name | Player display name |
| bowling_style | Standardized bowling style |

**Bowling Style Values:**
- `Right-arm pace`
- `Left-arm pace`
- `Right-arm off-spin`
- `Right-arm leg-spin`
- `Left-arm orthodox`
- `Left-arm wrist spin`

---

### data/ipl_2026_player_contracts.csv

**Description:** IPL 2026 player contract prices and acquisition details.
**Records:** 231 players

| Column | Description |
|--------|-------------|
| team_name | IPL franchise name |
| player_name | Full player name |
| price_cr | Contract value in INR crores |
| acquisition_type | Retained, Auction, Traded |
| year_joined | Year player joined franchise |

---

## Data Quality Notes

### Coverage
- **Matches:** 9,357 T20 matches globally
- **IPL Matches:** 1,089 (2008-2025)
- **Analysis Window:** IPL 2023-2025 (219 matches) for analytics views
- **Ball Records:** 2,137,915

### Known Limitations
1. **No ball speed/trajectory data** - Cannot assess pace variations
2. **No field position data** - Cannot analyze fielding impact
3. **Player ID collisions** - 16 cases fixed via manual curation
4. **Sample size variation** - Confidence indicators (HIGH/MEDIUM/LOW) in views

### Data Refresh
| Data Type | Frequency | Trigger |
|-----------|-----------|---------|
| Ball-by-ball | Post-season | New Cricsheet release |
| Squad data | Pre-season | IPL auction/retention |
| Contract data | Pre-season | IPL auction |
| Bowler classifications | As needed | New players |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-06 | Initial data dictionary (TKT-032) |

---

*Cricket Playbook v4.1.0*
*Owner: Brock Purdy (Data Pipeline Lead)*
