# Outputs

Generated data artifacts from analytics scripts.

---

## Data Range

**IMPORTANT:** All outputs now use **recent IPL seasons (2023-2025)** to account for stat drift due to evolution of the game.

| Output File | Data Range | Notes |
|-------------|------------|-------|
| `player_tags.json` | 2023-2025 | Recent 3 IPL seasons (219 matches) |
| `bowler_handedness_matchup.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_bowling_type_matchup.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_bowling_type_detail.csv` | 2023-2025 | Recent 3 IPL seasons |
| `bowler_phase_performance.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_entry_points.csv` | 2023-2025 | Recent 3 IPL seasons |
| `bowler_over_timing.csv` | 2023-2025 | Recent 3 IPL seasons |
| `ipl_2026_squad_experience.csv` | 2023-2025 | Recent 3 IPL seasons |

**Founder Review Note:** Per Review #3, data is now filtered to 2023+ instead of using recency weighting. This ensures stats reflect current player form and game evolution.

**Last Updated:** 2026-01-24

---

## Contents

| File | Description | Script |
|------|-------------|--------|
| `player_tags.json` | Multi-tag classification for 377 players | `player_clustering_v2.py` |
| `bowler_handedness_matchup.csv` | LHB/RHB matchup analysis (140 bowlers) | `bowler_handedness_matchup.py` |
| `batter_bowling_type_matchup.csv` | Batter vs pace/spin matchup | `batter_bowling_type_matchup.py` |
| `batter_bowling_type_detail.csv` | Detailed bowling type breakdown | `batter_bowling_type_matchup.py` |
| `bowler_phase_performance.csv` | Phase-wise bowler economy | `bowler_phase_tags.py` |
| `batter_entry_points.csv` | Batter entry positions (median/mode) | `entry_point_analysis.py` |
| `bowler_over_timing.csv` | Bowler over distribution | `entry_point_analysis.py` |
| `ipl_2026_squad_experience.csv` | Squad experience metrics (234 players) | `generate_experience_csv.py` |
| `manifest.json` | Data generation manifest | Various |
| `schema.md` | Schema documentation | `ingest.py` |

---

## CSV File Schemas

### batter_bowling_type_matchup.csv

**Description:** Aggregated batter performance against pace vs spin bowling (125 batters).

| Column | Type | Description |
|--------|------|-------------|
| `batter_id` | string | Unique player identifier |
| `batter_name` | string | Player display name |
| `pace_balls` | int | Total balls faced vs pace bowlers |
| `pace_sr` | float | Strike rate vs pace (runs per 100 balls) |
| `pace_avg` | float | Batting average vs pace (runs per dismissal) |
| `pace_dismissals` | int | Times dismissed by pace bowlers |
| `spin_balls` | int | Total balls faced vs spin bowlers |
| `spin_sr` | float | Strike rate vs spin |
| `spin_avg` | float | Batting average vs spin |
| `spin_dismissals` | int | Times dismissed by spin bowlers |
| `bowling_type_tags` | string | Comma-separated tags (e.g., "SPECIALIST_VS_PACE, VULNERABLE_VS_SPIN") |

---

### batter_bowling_type_detail.csv

**Description:** Granular batter performance broken down by specific bowling type (289 records).

| Column | Type | Description |
|--------|------|-------------|
| `batter_id` | string | Unique player identifier |
| `batter_name` | string | Player display name |
| `bowling_type` | string | Bowling style (e.g., "Right-arm fast", "Leg-spin", "Left-arm orthodox") |
| `balls` | int | Balls faced vs this bowling type |
| `runs` | int | Runs scored vs this bowling type |
| `dismissals` | int | Times dismissed by this bowling type |
| `fours` | int | Boundaries (4s) hit |
| `sixes` | int | Sixes hit |
| `dots` | int | Dot balls faced |
| `strike_rate` | float | Strike rate vs this bowling type |
| `average` | float | Batting average vs this bowling type |
| `dot_pct` | float | Dot ball percentage |
| `boundary_pct` | float | Boundary percentage (4s + 6s) |

---

### batter_entry_points.csv

**Description:** When batters typically come to bat in an innings (89 batters).

| Column | Type | Description |
|--------|------|-------------|
| `batter_id` | string | Unique player identifier |
| `batter_name` | string | Player display name |
| `innings_count` | int | Number of innings analyzed |
| `mean_entry_ball` | float | Average ball number when batter arrives |
| `median_entry_ball` | float | Median ball number (more robust to outliers) |
| `mode_entry_ball` | int | Most common entry ball (binned to 6-ball overs) |
| `mean_entry_over` | float | Mean entry converted to overs |
| `median_entry_over` | float | Median entry converted to overs |
| `mode_entry_over` | float | Mode entry converted to overs |
| `position_category` | string | Classification: OPENER (≤6), TOP_ORDER (≤24), MIDDLE_ORDER (≤60), LOWER_ORDER (>60) |
| `min_entry_ball` | int | Earliest entry ball across all innings |
| `max_entry_ball` | int | Latest entry ball across all innings |

---

### bowler_handedness_matchup.csv

**Description:** Bowler performance split by batter handedness - LHB vs RHB (78 bowlers).

| Column | Type | Description |
|--------|------|-------------|
| `bowler_id` | string | Unique player identifier |
| `bowler_name` | string | Player display name |
| `lhb_balls` | int | Balls bowled to left-handed batters |
| `lhb_economy` | float | Economy rate vs LHB (runs per over) |
| `lhb_strike_rate` | float | Bowling strike rate vs LHB (balls per wicket) |
| `lhb_wickets` | int | Wickets taken vs LHB |
| `rhb_balls` | int | Balls bowled to right-handed batters |
| `rhb_economy` | float | Economy rate vs RHB |
| `rhb_strike_rate` | float | Bowling strike rate vs RHB |
| `rhb_wickets` | int | Wickets taken vs RHB |
| `economy_diff` | float | LHB economy minus RHB economy (negative = better vs LHB) |
| `strike_rate_diff` | float | LHB SR minus RHB SR (negative = takes wickets faster vs LHB) |
| `handedness_tags` | string | Comma-separated tags (e.g., "LHB_SPECIALIST, RHB_VULNERABLE") |

---

### bowler_over_timing.csv

**Description:** When bowlers typically bowl their overs in a match (67 bowlers).

| Column | Type | Description |
|--------|------|-------------|
| `bowler_id` | string | Unique player identifier |
| `bowler_name` | string | Player display name |
| `match_count` | int | Number of matches analyzed |
| `over1_median` | int | Median match over for bowler's 1st over |
| `over1_mode` | int | Most common match over for 1st over |
| `over1_count` | int | Sample size for 1st over |
| `over2_median` | int | Median match over for bowler's 2nd over |
| `over2_mode` | int | Most common match over for 2nd over |
| `over2_count` | int | Sample size for 2nd over |
| `over3_median` | int | Median match over for bowler's 3rd over |
| `over3_mode` | int | Most common match over for 3rd over |
| `over3_count` | int | Sample size for 3rd over |
| `over4_median` | int | Median match over for bowler's 4th over |
| `over4_mode` | int | Most common match over for 4th over |
| `over4_count` | int | Sample size for 4th over |
| `role_category` | string | POWERPLAY_BOWLER, DEATH_BOWLER, PP_AND_DEATH_SPECIALIST, or MIDDLE_OVERS_BOWLER |

---

### bowler_phase_performance.csv

**Description:** Bowler economy and wickets by match phase (208 bowlers).

| Column | Type | Description |
|--------|------|-------------|
| `bowler_id` | string | Unique player identifier |
| `bowler_name` | string | Player display name |
| `powerplay_overs` | float | Overs bowled in powerplay (overs 1-6) |
| `powerplay_economy` | float | Economy rate in powerplay |
| `powerplay_wickets` | int | Wickets taken in powerplay |
| `middle_overs` | float | Overs bowled in middle phase (overs 7-15) |
| `middle_economy` | float | Economy rate in middle overs |
| `middle_wickets` | int | Wickets taken in middle overs |
| `death_overs` | float | Overs bowled at death (overs 16-20) |
| `death_economy` | float | Economy rate at death |
| `death_wickets` | int | Wickets taken at death |
| `phase_tags` | string | Comma-separated tags (e.g., "PP_BEAST, DEATH_LIABILITY") |

---

### ipl_2026_squad_experience.csv

**Description:** IPL 2026 squad players with their historical IPL statistics (231 players).

| Column | Type | Description |
|--------|------|-------------|
| `team_name` | string | IPL franchise name (e.g., "Mumbai Indians") |
| `player_name` | string | Player display name |
| `player_id` | string | Unique player identifier |
| `role` | string | Playing role (Batter, Bowler, All-rounder, Wicketkeeper) |
| `bowling_type` | string | Primary bowling style (e.g., "Right-arm fast", "Leg-spin") |
| `bowling_style` | string | Detailed bowling classification |
| `batting_hand` | string | Left-hand or Right-hand |
| `is_uncapped` | bool | True if player has no IPL 2023+ stats |
| `ipl_batting_innings` | int | IPL batting innings (2023-2025) |
| `ipl_batting_balls` | int | Balls faced in IPL |
| `ipl_batting_runs` | int | Runs scored in IPL |
| `ipl_batting_sr` | float | IPL batting strike rate |
| `ipl_bowling_matches` | int | IPL matches bowled in |
| `ipl_bowling_balls` | int | Balls bowled in IPL |
| `ipl_bowling_wickets` | int | IPL wickets taken |
| `ipl_bowling_economy` | float | IPL bowling economy rate |

---

## Regenerating Outputs

```bash
# Regenerate all analytics
python scripts/analytics_ipl.py

# Regenerate player clustering and tags
python scripts/player_clustering_v2.py

# Regenerate LHB/RHB matchup analysis (with wicket-taker tags)
python scripts/bowler_handedness_matchup.py

# Regenerate batter vs bowling type matchups
python scripts/batter_bowling_type_matchup.py

# Regenerate bowler phase tags (PP_BEAST, DEATH_LIABILITY)
python scripts/bowler_phase_tags.py

# Regenerate entry point analysis
python scripts/entry_point_analysis.py

# Regenerate experience CSV
python scripts/generate_experience_csv.py
```

---

## Tags System

The `player_tags.json` contains multi-dimensional tags for players.

### Batter Tags

**Cluster Archetypes (K-means v2):**
| Cluster | Label | Description |
|---------|-------|-------------|
| 0 | CLASSIC_OPENER | Traditional openers, platform builders (avg position 1.8) |
| 1 | ACCUMULATOR | Middle-order stabilizers at #3-4 |
| 2 | DEATH_FINISHER | Lower-order finishers at #5-6 |
| 3 | ELITE_EXPLOSIVE | Match-winners with 158+ SR across phases |
| 4 | POWER_OPENER | Aggressive openers with 163+ SR |

**Secondary Tags:**
- `PP_DOMINATOR` - Strike rate >150 in powerplay with 50+ PP balls
- `DEATH_SPECIALIST` - Strike rate >160 at death with 30+ death balls
- `SIX_HITTER` - Six percentage >15%
- `CONSISTENT` - Innings count >50 with >100 balls

**Bowling Type Matchup Tags:**
| Tag | Criteria |
|-----|----------|
| `SPECIALIST_VS_PACE` | SR ≥130 AND Avg ≥25 AND balls/dismissal ≥20 |
| `SPECIALIST_VS_SPIN` | SR ≥130 AND Avg ≥25 AND balls/dismissal ≥20 |
| `VULNERABLE_VS_PACE` | SR <105 OR Avg <15 OR balls/dismissal <15 |
| `VULNERABLE_VS_SPIN` | SR <105 OR Avg <15 OR balls/dismissal <15 |
| `SPECIALIST_VS_OFF_SPIN` | Same criteria vs off-spin only |
| `SPECIALIST_VS_LEG_SPIN` | Same criteria vs leg-spin only |
| `SPECIALIST_VS_LEFT_ARM_SPIN` | Same criteria vs left-arm spin only |
| `VULNERABLE_VS_*` | Converse criteria for each type |

**Why SR alone is not enough:** A player like Aiden Markram can have SR 130+ vs left-arm orthodox but:
- Average of 18.0 (below 25 threshold)
- Only 13.75 balls per dismissal (below 20 threshold)
- This indicates he gets out too often despite scoring quickly = NOT a specialist

### Bowler Tags

**Cluster Archetypes:**
| Cluster | Label | Phase Focus |
|---------|-------|-------------|
| 0 | DEATH_SPECIALIST | PP 43.8%, Death 31.8% (dual-phase seamers) |
| 1 | DEVELOPING | Mixed phases, higher economy |
| 2 | SPIN_CONTROLLER | Middle 71.3% (elite middle-overs spinners) |
| 3 | NEW_BALL_PACER | PP 47.7% (opening bowlers) |
| 4 | SECONDARY_OPTION | Middle 61.9% (part-timers, backup options) |

**Handedness Matchup Tags:**
| Tag | Criteria |
|-----|----------|
| `LHB_SPECIALIST` | ≥5% better economy vs left-handers |
| `RHB_SPECIALIST` | ≥5% better economy vs right-handers |
| `LHB_WICKET_TAKER` | ≥3 wickets vs LHB + SR <25 |
| `RHB_WICKET_TAKER` | ≥3 wickets vs RHB + SR <25 |
| `LHB_PRESSURE` | ≥5% higher dot ball % vs left-handers |
| `RHB_PRESSURE` | ≥5% higher dot ball % vs right-handers |
| `LHB_VULNERABLE` | ≥5% worse economy vs left-handers |
| `RHB_VULNERABLE` | ≥5% worse economy vs right-handers |

**Phase Performance Tags:**
| Tag | Criteria |
|-----|----------|
| `PP_BEAST` | Economy <7.0 in powerplay with 30+ PP overs |
| `PP_LIABILITY` | Economy >9.5 in powerplay with 30+ PP overs |
| `MIDDLE_OVERS_BEAST` | Economy <7.0 in middle with 50+ middle overs |
| `MIDDLE_OVERS_LIABILITY` | Economy >8.5 in middle with 50+ middle overs |
| `DEATH_BEAST` | Economy <8.5 at death with 30+ death overs |
| `DEATH_LIABILITY` | Economy >10.5 at death with 30+ death overs |

**Role Categories (from over timing):**
| Role | Criteria |
|------|----------|
| `POWERPLAY_BOWLER` | 1st over median in overs 0-5 |
| `DEATH_BOWLER` | 4th over median in overs 16+ |
| `PP_AND_DEATH_SPECIALIST` | Both PP and death criteria met |
| `MIDDLE_OVERS_BOWLER` | Neither PP nor death criteria met |

---

## Model Details

### Player Clustering V2

**Algorithm:** K-means clustering (scikit-learn)

**Features for Batters:**
1. Strike rate (overall)
2. Average batting position (weighted by balls faced)
3. Powerplay strike rate
4. Death overs strike rate
5. Boundary percentage (4s + 6s)
6. Dot ball percentage

**Features for Bowlers:**
1. Economy rate
2. Strike rate (balls per wicket)
3. Powerplay wickets %
4. Middle overs wickets %
5. Death overs wickets %
6. Dot ball percentage

**Preprocessing:**
- StandardScaler normalization
- PCA dimensionality reduction (83.6% variance for batters, 63.8% for bowlers)

**Cluster Count:** 5 clusters each (determined by elbow method)

**Minimum Sample Size:** 100 balls (batters), 60 balls (bowlers)

### Matchup Analysis

**Minimum Sample Sizes:**
- Handedness matchup: 30 balls per handedness
- Bowling type matchup: 30 balls per type
- Phase tags: 30-50 overs depending on phase
- Entry point analysis: 15 innings minimum

**Data Source:** IPL matches 2023-2025 (219 matches: 74 in 2023, 71 in 2024, 74 in 2025)

---

## Sample Size Indicators

All outputs include confidence indicators:

| Indicator | Batting | Bowling |
|-----------|---------|---------|
| HIGH | 500+ balls | 300+ balls |
| MEDIUM | 100-499 balls | 60-299 balls |
| LOW | <100 balls | <60 balls |

---

*Cricket Playbook v2.7.0 - Sprint 2.7 (Founder Review #3)*
