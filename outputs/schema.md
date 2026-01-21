# Cricket Playbook - Data Schema

**Owner:** Brock Purdy (Data Ingestion & Pipeline)
**Version:** 2.0.0
**Last Updated:** 2026-01-20

---

## Overview

Star schema design with fact tables at center, dimension tables providing context.

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

## Dimension Tables

### dim_match

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| match_id | VARCHAR | NO | PK - Unique match identifier |
| tournament_id | VARCHAR | YES | FK to dim_tournament |
| match_number | DOUBLE | YES | Match sequence within tournament |
| stage | VARCHAR | YES | Tournament stage (Group, Qualifier, Final) |
| season | VARCHAR | YES | Season/year identifier |
| match_date | VARCHAR | YES | Date (YYYY-MM-DD) |
| venue_id | VARCHAR | YES | FK to dim_venue |
| team1_id | VARCHAR | YES | FK to dim_team |
| team2_id | VARCHAR | YES | FK to dim_team |
| toss_winner_id | VARCHAR | YES | FK to dim_team |
| toss_decision | VARCHAR | YES | 'bat' or 'field' |
| winner_id | VARCHAR | YES | FK to dim_team |
| outcome_type | VARCHAR | YES | 'runs', 'wickets', 'tie', 'no result' |
| outcome_margin | DOUBLE | YES | Margin of victory |
| player_of_match_id | VARCHAR | YES | FK to dim_player |
| balls_per_over | BIGINT | YES | Typically 6 |
| data_version | VARCHAR | YES | Cricsheet data version |
| is_active | BOOLEAN | YES | Record active flag |
| ingested_at | VARCHAR | YES | Ingestion timestamp |
| source_file | VARCHAR | YES | Source JSON file |

### dim_player

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | NO | PK - 8-char hex ID from Cricsheet |
| current_name | VARCHAR | YES | Current display name |
| first_seen_date | VARCHAR | YES | First match date |
| last_seen_date | VARCHAR | YES | Most recent match date |
| matches_played | BIGINT | YES | Total matches in database |
| is_wicketkeeper | BOOLEAN | YES | **Derived** from keeping duties |
| primary_role | VARCHAR | YES | **Derived**: Batter/Bowler/All-rounder |

### dim_team

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_id | VARCHAR | NO | PK |
| team_name | VARCHAR | YES | Full team name |
| short_name | VARCHAR | YES | Abbreviated name |

### dim_venue

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| venue_id | VARCHAR | NO | PK |
| venue_name | VARCHAR | YES | Full venue name |
| city | VARCHAR | YES | City location |

### dim_tournament

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| tournament_id | VARCHAR | NO | PK |
| tournament_name | VARCHAR | YES | e.g., "Indian Premier League" |
| country | VARCHAR | YES | Host country |
| format | VARCHAR | YES | Match format (T20) |
| gender | VARCHAR | YES | 'male' or 'female' |

### dim_player_name_history

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player |
| player_name | VARCHAR | YES | Name used in this period |
| valid_from | VARCHAR | YES | Start date |
| valid_to | VARCHAR | YES | End date |
| source_file | VARCHAR | YES | Source of name |

---

## Fact Tables

### fact_ball

Core fact table - one row per legal delivery.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| ball_id | VARCHAR | NO | PK - Unique ball identifier |
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
| batter_runs | BIGINT | YES | Runs off bat (0-6) |
| extra_runs | BIGINT | YES | Wides, noballs, etc. |
| total_runs | BIGINT | YES | batter_runs + extra_runs |
| extra_type | VARCHAR | YES | 'wides', 'noballs', 'byes', 'legbyes', NULL |
| is_wicket | BOOLEAN | YES | Whether wicket fell |
| wicket_type | VARCHAR | YES | 'bowled', 'caught', 'lbw', 'run out', etc. |
| player_out_id | VARCHAR | YES | FK to dim_player (dismissed) |
| fielder_id | VARCHAR | YES | FK to dim_player (fielder) |
| is_legal_ball | BOOLEAN | YES | FALSE for wides/noballs |
| match_phase | VARCHAR | YES | **Derived**: 'powerplay', 'middle', 'death' |
| data_version | VARCHAR | YES | Cricsheet version |
| ingested_at | VARCHAR | YES | Ingestion timestamp |
| source_file | VARCHAR | YES | Source file |

**Match Phase Derivation:**
```sql
CASE
  WHEN over < 6 THEN 'powerplay'
  WHEN over < 15 THEN 'middle'
  ELSE 'death'
END
```

### fact_player_match_performance

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| player_id | VARCHAR | YES | FK to dim_player |
| match_id | VARCHAR | YES | FK to dim_match |
| team_id | VARCHAR | YES | FK to dim_team |
| batting_position | DOUBLE | YES | Position in batting order |
| did_bat | BOOLEAN | YES | Whether player batted |
| did_bowl | BOOLEAN | YES | Whether player bowled |
| did_keep_wicket | BOOLEAN | YES | Whether player kept wicket |

### fact_powerplay

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| powerplay_id | VARCHAR | NO | PK |
| match_id | VARCHAR | YES | FK to dim_match |
| innings | BIGINT | YES | Innings number |
| powerplay_seq | BIGINT | YES | Powerplay sequence |
| powerplay_type | VARCHAR | YES | 'mandatory', 'batting', 'bowling' |
| from_over | DOUBLE | YES | Start over |
| to_over | DOUBLE | YES | End over |

---

## IPL 2026 Squad Tables

### ipl_2026_squads

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_name | VARCHAR | YES | IPL franchise name |
| player_name | VARCHAR | YES | Full player name |
| player_id | VARCHAR | YES | FK to dim_player (95.7% mapped) |
| role | VARCHAR | YES | Batter/Bowler/All-rounder/Wicketkeeper |
| bowling_arm | VARCHAR | YES | Right-arm, Left-arm, NULL |
| bowling_type | VARCHAR | YES | Fast, Medium, Off-spin, Leg-spin, etc. |
| batting_hand | VARCHAR | YES | Right-hand, Left-hand |

### ipl_2026_contracts

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| team_name | VARCHAR | YES | IPL franchise name |
| player_name | VARCHAR | YES | Full player name |
| price_cr | DOUBLE | YES | Contract price in INR crores |
| acquisition_type | VARCHAR | YES | Retained, RTM, Auction, Uncapped |
| year_joined | BIGINT | YES | Year player joined franchise |

---

## Versioning Columns

All tables include these audit columns:

| Column | Purpose |
|--------|---------|
| data_version | Cricsheet data version identifier |
| is_active | Soft delete flag (TRUE = active) |
| ingested_at | ISO timestamp of ingestion |
| source_file | Original source file path |

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
```

---

*Brock Purdy*
*Data Ingestion & Pipeline Owner*
