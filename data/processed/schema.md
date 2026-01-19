# Cricket Playbook Schema

## Overview

This database contains ball-by-ball T20 cricket data from Cricsheet.

## Tables

### Dimension Tables

#### dim_tournament
| Column | Type | Description |
|--------|------|-------------|
| tournament_id | VARCHAR | Primary key |
| tournament_name | VARCHAR | Full name |
| country | VARCHAR | Primary country |
| format | VARCHAR | T20, Hundred |
| gender | VARCHAR | male/female |

#### dim_team
| Column | Type | Description |
|--------|------|-------------|
| team_id | VARCHAR | Primary key (hash) |
| team_name | VARCHAR | Full name |
| short_name | VARCHAR | Abbreviation |

#### dim_venue
| Column | Type | Description |
|--------|------|-------------|
| venue_id | VARCHAR | Primary key (hash) |
| venue_name | VARCHAR | Stadium name |
| city | VARCHAR | City |

#### dim_player
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | Primary key (Cricsheet ID) |
| current_name | VARCHAR | Latest known name |
| first_seen_date | DATE | First appearance |
| last_seen_date | DATE | Last appearance |
| matches_played | INT | Total matches |
| primary_role | VARCHAR | Batter/Bowler/All-rounder |

#### dim_player_name_history
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | FK to dim_player |
| player_name | VARCHAR | Name used |
| valid_from | DATE | First seen |
| valid_to | DATE | Last seen (NULL if current) |
| source_file | VARCHAR | Source |

#### dim_match
| Column | Type | Description |
|--------|------|-------------|
| match_id | VARCHAR | Primary key (Cricsheet ID) |
| tournament_id | VARCHAR | FK to dim_tournament |
| match_number | INT | Match # in tournament |
| stage | VARCHAR | Group/Final/etc |
| season | VARCHAR | Season |
| match_date | DATE | Date played |
| venue_id | VARCHAR | FK to dim_venue |
| team1_id | VARCHAR | FK to dim_team |
| team2_id | VARCHAR | FK to dim_team |
| toss_winner_id | VARCHAR | FK to dim_team |
| toss_decision | VARCHAR | bat/field |
| winner_id | VARCHAR | FK to dim_team |
| outcome_type | VARCHAR | runs/wickets/tie |
| outcome_margin | INT | Margin |
| player_of_match_id | VARCHAR | FK to dim_player |
| balls_per_over | INT | Usually 6 |

### Fact Tables

#### fact_ball
| Column | Type | Description |
|--------|------|-------------|
| ball_id | VARCHAR | Primary key |
| match_id | VARCHAR | FK to dim_match |
| innings | INT | 1 or 2 |
| over | INT | 0-19 |
| ball | INT | Ball in over |
| ball_seq | INT | Sequential # |
| batting_team_id | VARCHAR | FK to dim_team |
| bowling_team_id | VARCHAR | FK to dim_team |
| batter_id | VARCHAR | FK to dim_player |
| bowler_id | VARCHAR | FK to dim_player |
| non_striker_id | VARCHAR | FK to dim_player |
| batter_runs | INT | Runs by batter |
| extra_runs | INT | Extra runs |
| total_runs | INT | Total |
| extra_type | VARCHAR | wides/noballs/byes/legbyes |
| is_wicket | BOOLEAN | Wicket fell |
| wicket_type | VARCHAR | caught/bowled/etc |
| player_out_id | VARCHAR | FK to dim_player |
| fielder_id | VARCHAR | FK to dim_player |
| is_legal_ball | BOOLEAN | Not wide/noball |

#### fact_powerplay
| Column | Type | Description |
|--------|------|-------------|
| powerplay_id | VARCHAR | Primary key |
| match_id | VARCHAR | FK to dim_match |
| innings | INT | 1 or 2 |
| powerplay_seq | INT | Sequence |
| powerplay_type | VARCHAR | mandatory/batting/bowling |
| from_over | DECIMAL | Start |
| to_over | DECIMAL | End |

#### fact_player_match_performance
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | FK to dim_player |
| match_id | VARCHAR | FK to dim_match |
| team_id | VARCHAR | FK to dim_team |
| batting_position | INT | 1-11 |
| did_bat | BOOLEAN | Batted |
| did_bowl | BOOLEAN | Bowled |
| did_keep_wicket | BOOLEAN | Kept wicket |

## Generated

Generated: 2026-01-19T12:46:12.415720
Data Version: 1.1.0
