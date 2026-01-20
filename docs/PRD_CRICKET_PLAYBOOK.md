# Cricket Playbook - Product Requirements Document

**Version:** 2.0.0
**Last Updated:** 2026-01-20
**Authors:** Tom Brady (Product Owner), Stephen Curry (Analytics Lead), Andy Flower (Cricket Domain Expert)

---

## 1. Executive Summary

Cricket Playbook is a comprehensive T20 cricket analytics platform built on ball-by-ball data from Cricsheet. The platform provides deep analytical insights for IPL 2026 squad planning, player evaluation, and match preparation through 43 analytics views spanning batting, bowling, matchups, and team performance.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total Matches | 9,357 |
| IPL Matches | 1,169 |
| Total Players | 7,864 |
| Ball-by-Ball Records | 2,137,915 |
| Venues Covered | 531 |
| Tournaments | 426 |
| Analytics Views | 43 |
| IPL 2026 Players Tracked | 231 |

---

## 2. Data Architecture

### 2.1 Star Schema Design

The database follows a star schema with fact tables at the center and dimension tables providing context.

```
                    ┌─────────────────┐
                    │  dim_tournament │
                    └────────┬────────┘
                             │
┌──────────────┐    ┌────────┴────────┐    ┌─────────────┐
│  dim_venue   │────│    dim_match    │────│  dim_team   │
└──────────────┘    └────────┬────────┘    └─────────────┘
                             │
                    ┌────────┴────────┐
                    │    fact_ball    │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │   dim_player    │
                    └─────────────────┘
```

---

## 3. Base Tables Schema

### 3.1 Dimension Tables

#### dim_match
Match-level metadata for all T20 matches.

| Column | Type | Description |
|--------|------|-------------|
| match_id | VARCHAR | Primary key - unique match identifier |
| tournament_id | VARCHAR | FK to dim_tournament |
| match_number | DOUBLE | Match sequence within tournament |
| stage | VARCHAR | Tournament stage (Group, Qualifier, Final, etc.) |
| season | VARCHAR | Season/year identifier |
| match_date | VARCHAR | Date of match (YYYY-MM-DD) |
| venue_id | VARCHAR | FK to dim_venue |
| team1_id | VARCHAR | FK to dim_team - first team |
| team2_id | VARCHAR | FK to dim_team - second team |
| toss_winner_id | VARCHAR | FK to dim_team - toss winner |
| toss_decision | VARCHAR | 'bat' or 'field' |
| winner_id | VARCHAR | FK to dim_team - match winner |
| outcome_type | VARCHAR | 'runs', 'wickets', 'tie', 'no result' |
| outcome_margin | DOUBLE | Margin of victory |
| player_of_match_id | VARCHAR | FK to dim_player |
| balls_per_over | BIGINT | Balls per over (typically 6) |
| data_version | VARCHAR | Cricsheet data version |
| is_active | BOOLEAN | Record active flag |
| ingested_at | VARCHAR | Ingestion timestamp |
| source_file | VARCHAR | Source JSON file |

#### dim_player
Player master data with derived attributes.

| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | Primary key - 8-char hex ID from Cricsheet |
| current_name | VARCHAR | Current display name (e.g., "V Kohli") |
| first_seen_date | VARCHAR | First match date |
| last_seen_date | VARCHAR | Most recent match date |
| matches_played | BIGINT | Total matches in database |
| is_wicketkeeper | BOOLEAN | Derived from keeping duties |
| primary_role | VARCHAR | Derived: 'Batter', 'Bowler', 'All-rounder' |

#### dim_team
Team master data.

| Column | Type | Description |
|--------|------|-------------|
| team_id | VARCHAR | Primary key |
| team_name | VARCHAR | Full team name |
| short_name | VARCHAR | Abbreviated name |

#### dim_venue
Venue/ground information.

| Column | Type | Description |
|--------|------|-------------|
| venue_id | VARCHAR | Primary key |
| venue_name | VARCHAR | Full venue name |
| city | VARCHAR | City location |

#### dim_tournament
Tournament/competition metadata.

| Column | Type | Description |
|--------|------|-------------|
| tournament_id | VARCHAR | Primary key |
| tournament_name | VARCHAR | e.g., "Indian Premier League" |
| country | VARCHAR | Host country |
| format | VARCHAR | Match format (T20) |
| gender | VARCHAR | 'male' or 'female' |

#### dim_player_name_history
Tracks player name changes over time.

| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | FK to dim_player |
| player_name | VARCHAR | Name used in this period |
| valid_from | VARCHAR | Start date |
| valid_to | VARCHAR | End date |
| source_file | VARCHAR | Source of name |

### 3.2 Fact Tables

#### fact_ball
Core fact table - one row per legal delivery.

| Column | Type | Description |
|--------|------|-------------|
| ball_id | VARCHAR | Primary key - unique ball identifier |
| match_id | VARCHAR | FK to dim_match |
| innings | BIGINT | Innings number (1 or 2) |
| over | BIGINT | Over number (0-19) |
| ball | BIGINT | Ball within over (1-6+) |
| ball_seq | BIGINT | Sequential ball number in innings |
| batting_team_id | VARCHAR | FK to dim_team |
| bowling_team_id | VARCHAR | FK to dim_team |
| batter_id | VARCHAR | FK to dim_player - striker |
| bowler_id | VARCHAR | FK to dim_player |
| non_striker_id | VARCHAR | FK to dim_player |
| batter_runs | BIGINT | Runs scored off bat (0-6) |
| extra_runs | BIGINT | Extra runs (wides, noballs, etc.) |
| total_runs | BIGINT | batter_runs + extra_runs |
| extra_type | VARCHAR | 'wides', 'noballs', 'byes', 'legbyes', NULL |
| is_wicket | BOOLEAN | Whether wicket fell |
| wicket_type | VARCHAR | 'bowled', 'caught', 'lbw', 'run out', etc. |
| player_out_id | VARCHAR | FK to dim_player - dismissed player |
| fielder_id | VARCHAR | FK to dim_player - fielder involved |
| is_legal_ball | BOOLEAN | FALSE for wides/noballs |
| match_phase | VARCHAR | **Derived**: 'powerplay', 'middle', 'death' |
| data_version | VARCHAR | Cricsheet version |
| ingested_at | VARCHAR | Ingestion timestamp |
| source_file | VARCHAR | Source file |

**Match Phase Logic:**
- `powerplay`: Overs 0-5 (balls 1-36)
- `middle`: Overs 6-14 (balls 37-90)
- `death`: Overs 15-19 (balls 91-120)

#### fact_player_match_performance
Player participation per match.

| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | FK to dim_player |
| match_id | VARCHAR | FK to dim_match |
| team_id | VARCHAR | FK to dim_team |
| batting_position | DOUBLE | Position in batting order |
| did_bat | BOOLEAN | Whether player batted |
| did_bowl | BOOLEAN | Whether player bowled |
| did_keep_wicket | BOOLEAN | Whether player kept wicket |

#### fact_powerplay
Powerplay definitions per innings.

| Column | Type | Description |
|--------|------|-------------|
| powerplay_id | VARCHAR | Primary key |
| match_id | VARCHAR | FK to dim_match |
| innings | BIGINT | Innings number |
| powerplay_seq | BIGINT | Powerplay sequence |
| powerplay_type | VARCHAR | 'mandatory', 'batting', 'bowling' |
| from_over | DOUBLE | Start over |
| to_over | DOUBLE | End over |

### 3.3 IPL 2026 Squad Tables

#### ipl_2026_squads
IPL 2026 squad composition with player classifications.

| Column | Type | Description |
|--------|------|-------------|
| team_name | VARCHAR | IPL franchise name |
| player_name | VARCHAR | Full player name |
| player_id | VARCHAR | FK to dim_player (95.7% mapped) |
| role | VARCHAR | 'Batter', 'Bowler', 'All-rounder', 'Wicketkeeper' |
| bowling_arm | VARCHAR | 'Right-arm', 'Left-arm', NULL |
| bowling_type | VARCHAR | 'Fast', 'Medium', 'Off-spin', 'Leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin' |
| batting_hand | VARCHAR | 'Right-hand', 'Left-hand' |

#### ipl_2026_contracts
Contract and acquisition details.

| Column | Type | Description |
|--------|------|-------------|
| team_name | VARCHAR | IPL franchise name |
| player_name | VARCHAR | Full player name |
| price_cr | DOUBLE | Contract price in INR crores |
| acquisition_type | VARCHAR | 'Retained', 'RTM', 'Auction', 'Uncapped' |
| year_joined | BIGINT | Year player joined current franchise |

---

## 4. Analytics Views Catalog

### 4.1 Career Statistics Views

| View | Description | Key Metrics |
|------|-------------|-------------|
| `analytics_batting_career` | All-time batting stats | Runs, SR, Avg, 50s, 100s, boundary% |
| `analytics_bowling_career` | All-time bowling stats | Wickets, Economy, Avg, SR, dot% |
| `analytics_ipl_batting_career` | IPL-only batting | Same metrics, IPL filtered |
| `analytics_ipl_bowling_career` | IPL-only bowling | Same metrics, IPL filtered |

### 4.2 Phase-wise Breakdown Views

| View | Description | Phases |
|------|-------------|--------|
| `analytics_batting_by_phase` | Batting by match phase | PP/Middle/Death |
| `analytics_bowling_by_phase` | Bowling by match phase | PP/Middle/Death |
| `analytics_ipl_batter_phase` | IPL batting by phase | PP/Middle/Death |
| `analytics_ipl_bowler_phase` | IPL bowling by phase | PP/Middle/Death |
| `analytics_t20_batter_phase` | All T20 batting by phase | PP/Middle/Death |
| `analytics_t20_bowler_phase` | All T20 bowling by phase | PP/Middle/Death |

### 4.3 Matchup Views

| View | Description | Granularity |
|------|-------------|-------------|
| `analytics_batter_vs_bowler` | Head-to-head career | Batter x Bowler |
| `analytics_ipl_batter_vs_bowler` | IPL head-to-head | Batter x Bowler (IPL) |
| `analytics_ipl_batter_vs_bowler_phase` | IPL H2H by phase | Batter x Bowler x Phase |
| `analytics_ipl_batter_vs_bowler_type` | Batter vs bowling type | Batter x Bowling Type |
| `analytics_ipl_batter_vs_bowler_type_phase` | By type and phase | Batter x Type x Phase |
| `analytics_ipl_bowler_vs_batter_phase` | Bowler perspective | Bowler x Batter x Phase |
| `analytics_t20_batter_vs_bowler_type` | All T20 vs type | Batter x Bowling Type |

### 4.4 Opposition Analysis Views

| View | Description | Key Use Case |
|------|-------------|--------------|
| `analytics_batter_vs_team` | Batting vs each team | Opposition prep |
| `analytics_ipl_batter_vs_team` | IPL batting vs team | IPL matchup analysis |
| `analytics_ipl_batter_vs_team_phase` | By team and phase | Phase-specific prep |
| `analytics_ipl_bowler_vs_team` | Bowling vs each team | Bowler matchup analysis |
| `analytics_ipl_bowler_vs_team_phase` | By team and phase | Phase-specific prep |

### 4.5 Venue Analysis Views

| View | Description | Key Use Case |
|------|-------------|--------------|
| `analytics_ipl_batter_venue` | Batting at each venue | Ground-specific form |
| `analytics_ipl_batter_venue_phase` | Venue by phase | Phase-specific venue |
| `analytics_ipl_bowler_venue` | Bowling at each venue | Ground conditions |
| `analytics_ipl_bowler_venue_phase` | Venue by phase | Phase-specific venue |

### 4.6 Distribution & Specialist Views

| View | Description | Key Insight |
|------|-------------|-------------|
| `analytics_ipl_bowler_phase_distribution` | % overs and wickets by phase | Role identification |
| `analytics_powerplay_hitters` | PP batting specialists | PP impact players |
| `analytics_death_over_specialists` | Death bowling specialists | Death over options |
| `analytics_best_strike_rates` | Qualified high SR batters | Impact batters |
| `analytics_best_economy` | Qualified low economy bowlers | Economical options |

### 4.7 Squad Integration Views

| View | Description | Key Use Case |
|------|-------------|--------------|
| `analytics_ipl_squad_batting` | 2026 squad batting | Squad evaluation |
| `analytics_ipl_squad_bowling` | 2026 squad bowling | Squad evaluation |
| `analytics_ipl_squad_batting_phase` | Squad batting by phase | Role assessment |
| `analytics_ipl_squad_bowling_phase` | Squad bowling by phase | Role assessment |
| `analytics_ipl_team_roster` | Full roster with contracts | Squad overview |

### 4.8 Leaderboard Views

| View | Description | Qualification |
|------|-------------|---------------|
| `analytics_top_run_scorers` | Run scoring leaders | 10+ innings |
| `analytics_top_wicket_takers` | Wicket taking leaders | 10+ matches |

### 4.9 Team Aggregate Views

| View | Description |
|------|-------------|
| `analytics_team_batting` | Team batting aggregates |
| `analytics_team_bowling` | Team bowling aggregates |

---

## 5. Key Metrics Definitions

### 5.1 Batting Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Strike Rate (SR) | (Runs / Balls) × 100 | Scoring rate per 100 balls |
| Batting Average | Runs / Dismissals | Runs per dismissal |
| Boundary % | (4s + 6s) / Balls × 100 | % of balls hit for boundary |
| Dot Ball % | Dot Balls / Balls × 100 | % of balls with no runs |

### 5.2 Bowling Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| Economy Rate | (Runs / Balls) × 6 | Runs conceded per over |
| Bowling Average | Runs / Wickets | Runs per wicket |
| Bowling Strike Rate | Balls / Wickets | Balls per wicket |
| Dot Ball % | Dots / Balls × 100 | % dot balls bowled |
| Boundary Conceded % | (4s + 6s) / Balls × 100 | % balls hit for boundary |

### 5.3 Distribution Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| % Overs in Phase | Phase Balls / Total Balls × 100 | Workload distribution |
| % Wickets in Phase | Phase Wickets / Total Wickets × 100 | Wicket distribution |
| Wicket Efficiency | % Wickets - % Overs | Over/under-performance in phase |

### 5.4 Sample Size Indicators

All views include sample size classification:

| Classification | Batting (balls) | Bowling (balls) | Matchups |
|----------------|-----------------|-----------------|----------|
| LOW | < 30 | < 30 | < 6 |
| MEDIUM | 30-99 | 30-99 | 6-19 |
| HIGH | 100+ | 100+ | 20+ |

---

## 6. IPL 2026 Squad Coverage

| Team | Players | ID Mapped | Coverage |
|------|---------|-----------|----------|
| Chennai Super Kings | 25 | 24 | 96% |
| Delhi Capitals | 25 | 24 | 96% |
| Gujarat Titans | 20 | 19 | 95% |
| Kolkata Knight Riders | 24 | 23 | 96% |
| Lucknow Super Giants | 20 | 19 | 95% |
| Mumbai Indians | 24 | 23 | 96% |
| Punjab Kings | 22 | 21 | 95% |
| Rajasthan Royals | 25 | 24 | 96% |
| Royal Challengers Bengaluru | 21 | 20 | 95% |
| Sunrisers Hyderabad | 25 | 24 | 96% |
| **Total** | **231** | **221** | **95.7%** |

---

## 7. Sample Queries

### 7.1 Player Analysis

```sql
-- Virat Kohli's IPL career summary
SELECT * FROM analytics_ipl_batting_career
WHERE player_name LIKE '%Kohli%';

-- Kohli's phase-wise breakdown
SELECT * FROM analytics_ipl_batter_phase
WHERE player_name LIKE '%Kohli%';

-- Kohli vs spin bowlers
SELECT * FROM analytics_ipl_batter_vs_bowler_type
WHERE batter_name LIKE '%Kohli%' AND bowler_type IN ('Off-spin', 'Leg-spin');
```

### 7.2 Head-to-Head

```sql
-- Kohli vs Bumrah by phase
SELECT * FROM analytics_ipl_batter_vs_bowler_phase
WHERE batter_name LIKE '%Kohli%' AND bowler_name LIKE '%Bumrah%';
```

### 7.3 Team Preparation

```sql
-- RCB 2026 squad batting overview
SELECT * FROM analytics_ipl_squad_batting
WHERE team_name = 'Royal Challengers Bengaluru'
ORDER BY price_cr DESC;

-- RCB batters vs Mumbai Indians in death overs
SELECT * FROM analytics_ipl_batter_vs_team_phase
WHERE batter_id IN (SELECT player_id FROM ipl_2026_squads WHERE team_name = 'Royal Challengers Bengaluru')
AND opposition = 'Mumbai Indians' AND match_phase = 'death';
```

### 7.4 Bowler Role Analysis

```sql
-- Death over specialists in MI squad
SELECT * FROM analytics_ipl_bowler_phase_distribution
WHERE bowler_id IN (SELECT player_id FROM ipl_2026_squads WHERE team_name = 'Mumbai Indians')
AND match_phase = 'death'
ORDER BY pct_overs_in_phase DESC;
```

---

## 8. Franchise Name Mappings

**Important**: Some IPL franchises have undergone name changes. Historical data should be combined:

| Current Name | Previous Name(s) | Years |
|--------------|------------------|-------|
| Delhi Capitals | Delhi Daredevils | 2008-2018 |
| Punjab Kings | Kings XI Punjab | 2008-2020 |
| Royal Challengers Bengaluru | Royal Challengers Bangalore | 2008-2023 |

When querying historical records, use:
```sql
WHERE opposition IN ('Delhi Capitals', 'Delhi Daredevils')
```

---

## 9. Revolutionary Insights (Andy Flower's Cricket Notes)

### 8.1 Wicket Efficiency Metric
The `wicket_efficiency` column in `analytics_ipl_bowler_phase_distribution` identifies bowlers who take MORE wickets than their workload suggests:
- **Positive value**: Over-performs in that phase (specialist)
- **Negative value**: Under-performs relative to overs bowled

**Example**: A bowler with `pct_overs_in_phase = 30%` but `pct_wickets_in_phase = 45%` has `wicket_efficiency = +15` - they're a phase specialist.

### 8.2 Boundary % as Intent Indicator
High `boundary_pct` with moderate `strike_rate` suggests clean hitting. Low `boundary_pct` with high `strike_rate` suggests rotation and placement skills.

### 8.3 Dot Ball Pressure
`dot_ball_pct` > 40% for bowlers in death overs is exceptional. For batters, `dot_ball_pct` < 25% in powerplay indicates aggressive intent.

### 8.4 Sample Size Discipline
Always filter for `sample_size = 'HIGH'` for strategic decisions. Use `MEDIUM` for directional insights. Treat `LOW` as anecdotal only.

### 8.5 Phase Matchup Intelligence
The combination of:
- `analytics_ipl_batter_vs_bowler_type_phase`
- `analytics_ipl_bowler_phase_distribution`

...enables precise matchup planning: "Who should bowl to left-handers in death overs?"

---

## 9. Technical Notes

### 9.1 Database
- **Engine**: DuckDB (embedded OLAP)
- **File**: `data/cricket_playbook.duckdb`
- **Size**: ~500MB

### 9.2 Data Source
- **Provider**: Cricsheet (https://cricsheet.org)
- **Format**: JSON (ball-by-ball)
- **Coverage**: All major T20 leagues and internationals

### 9.3 Refresh Frequency
- Manual ingestion via `scripts/ingest.py`
- Squad data updated for IPL 2026 post-auction

---

## 10. Appendix: IPL 2026 Auction Highlights

| Player | Team | Price (Cr) | Type |
|--------|------|------------|------|
| Rishabh Pant | LSG | 27.00 | Retained |
| Cameron Green | KKR | 25.20 | Auction |
| Virat Kohli | RCB | 21.00 | Retained |
| Jos Buttler | GT | 15.75 | Auction |
| Kartik Sharma | CSK | 14.20 | Uncapped |

---

*Document maintained by Tom Brady, Product Owner & Editor-in-Chief*
*Analytics by Stephen Curry, Analytics Lead*
*Cricket expertise by Andy Flower, Domain Expert*
