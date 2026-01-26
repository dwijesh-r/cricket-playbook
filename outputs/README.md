# Outputs

Generated data artifacts from analytics scripts.

---

## Data Range

**IMPORTANT:** All outputs now use **recent IPL seasons (2023-2025)** to account for stat drift due to evolution of the game.

| Output File | Data Range | Notes |
|-------------|------------|-------|
| `player_tags.json` | 2023-2025 | Recent 3 IPL seasons (219 matches) |
| `player_tags_2023.json` | 2023-2025 | **NEW** Explicit 2023+ version |
| `bowler_handedness_matchup.csv` | 2023-2025 | Recent 3 IPL seasons |
| `bowler_handedness_matchup_2023.csv` | 2023-2025 | **NEW** Explicit 2023+ version |
| `batter_bowling_type_matchup.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_bowling_type_matchup_2023.csv` | 2023-2025 | **NEW** Explicit 2023+ version |
| `batter_bowling_type_detail.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_bowling_type_detail_2023.csv` | 2023-2025 | **NEW** Explicit 2023+ version |
| `bowler_phase_performance.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_entry_points.csv` | 2023-2025 | Recent 3 IPL seasons |
| `batter_entry_points_2023.csv` | 2023-2025 | **NEW** 197 batters classified |
| `bowler_over_timing.csv` | 2023-2025 | Recent 3 IPL seasons |
| `ipl_2026_squad_experience.csv` | 2023-2025 | Recent 3 IPL seasons |
| `player_clustering_2023.csv` | 2023-2025 | **NEW** Clustering output |
| `batter_consistency_index.csv` | 2023-2025 | **NEW** Consistency metrics |
| `batter_consistency_by_year.csv` | 2023-2025 | **NEW** Yearly breakdown |
| `partnership_synergy.csv` | 2023-2025 | **NEW** Partnership scores |
| `partnership_synergy_by_year.csv` | 2023-2025 | **NEW** Yearly breakdown |
| `bowler_pressure_sequences.csv` | 2023-2025 | **NEW** Pressure performance |
| `bowler_pressure_by_year.csv` | 2023-2025 | **NEW** Yearly breakdown |
| `bowler_role_tags.csv` | 2023-2025 | **NEW** Role classifications |
| `team_venue_records.csv` | 2023-2025 | **NEW** Venue win/loss |
| `team_venue_records_by_year.csv` | 2023-2025 | **NEW** Yearly breakdown |
| `bowler_phase_distribution_grouped.csv` | 2023-2025 | **NEW** Phase tables |
| `player_id_audit_report.md` | N/A | **NEW** 15 mismatches documented |

**Founder Review Note:** Per Review #4, all outputs now have explicit 2023+ versions for Founder review.

**Last Updated:** 2026-01-26

---

## Glossary & Definitions

### Match Phase Definitions

| Phase | Overs | Ball Range | Description |
|-------|-------|------------|-------------|
| **Powerplay** | 1-6 | Balls 1-36 | Only 2 fielders outside 30-yard circle. Batting-friendly phase. |
| **Middle Overs** | 7-15 | Balls 37-90 | 4-5 fielders allowed outside circle. Consolidation phase. |
| **Death Overs** | 16-20 | Balls 91-120 | Final acceleration phase. High-risk, high-reward batting. |

### Core Batting Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Strike Rate (SR)** | `(Runs / Balls) × 100` | Runs scored per 100 balls faced. Higher = more aggressive. |
| **Batting Average (Avg)** | `Runs / Dismissals` | Runs per dismissal. Higher = more consistent. |
| **Balls Per Dismissal (BPD)** | `Balls / Dismissals` | How many balls a batter survives per out. Higher = harder to dismiss. |
| **Dot Ball %** | `(Dot Balls / Total Balls) × 100` | Percentage of balls with zero runs. Lower = better rotation. |
| **Boundary %** | `((Fours + Sixes) / Total Balls) × 100` | Percentage of balls hit for boundaries. Higher = more power. |

### Core Bowling Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Economy Rate (Econ)** | `(Runs Conceded / Balls) × 6` | Runs conceded per over. Lower = more restrictive. |
| **Bowling Strike Rate (SR)** | `Balls / Wickets` | Balls bowled per wicket taken. Lower = takes wickets faster. |
| **Dot Ball %** | `(Dot Balls / Total Balls) × 100` | Percentage of balls with zero runs. Higher = more pressure. |
| **Wickets Per Over** | `Wickets / Overs` | Average wickets taken per over bowled. |

### Derived Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Economy Differential** | `LHB_Econ - RHB_Econ` | Negative = better vs left-handers |
| **SR Differential** | `LHB_SR - RHB_SR` | Negative = takes wickets faster vs left-handers |
| **Phase Economy** | Economy calculated only for balls in that phase | Phase-specific performance |
| **Entry Ball** | Ball number when batter arrives at crease | Opener = ball 1, lower order = higher ball number |

### Tag Criteria Reference

#### Batter Specialist Tags (require ALL three conditions)

| Tag | Strike Rate | Average | Balls/Dismissal |
|-----|-------------|---------|-----------------|
| `SPECIALIST_VS_PACE` | ≥ 130 | ≥ 25 | ≥ 20 |
| `SPECIALIST_VS_SPIN` | ≥ 130 | ≥ 25 | ≥ 20 |
| `SPECIALIST_VS_OFF_SPIN` | ≥ 130 | ≥ 25 | ≥ 20 |
| `SPECIALIST_VS_LEG_SPIN` | ≥ 130 | ≥ 25 | ≥ 20 |
| `SPECIALIST_VS_LEFT_ARM_SPIN` | ≥ 130 | ≥ 25 | ≥ 20 |

#### Batter Vulnerable Tags (ANY one condition triggers)

| Tag | Strike Rate | OR Average | OR Balls/Dismissal |
|-----|-------------|------------|-------------------|
| `VULNERABLE_VS_PACE` | < 105 | < 15 | < 15 |
| `VULNERABLE_VS_SPIN` | < 105 | < 15 | < 15 |

**Why three conditions?** A player like Aiden Markram has SR 130+ vs left-arm spin but Average 18.0 and BPD 13.75 — he scores quickly but gets out too often. Three conditions prevent false "specialist" labels.

#### Batter Performance Tags

| Tag | Criteria | Minimum Sample |
|-----|----------|----------------|
| `PP_DOMINATOR` | Powerplay SR > 150 | 50 PP balls |
| `DEATH_SPECIALIST` | Death SR > 160 | 30 death balls |
| `SIX_HITTER` | Six % > 15% | 100 balls |
| `CONSISTENT` | 50+ innings | 100 balls |

#### Bowler Phase Tags

| Tag | Economy Threshold | Minimum Overs |
|-----|-------------------|---------------|
| `PP_BEAST` | < 7.0 | 30 overs |
| `PP_LIABILITY` | > 9.5 | 30 overs |
| `MIDDLE_OVERS_BEAST` | < 7.0 | 50 overs |
| `MIDDLE_OVERS_LIABILITY` | > 8.5 | 50 overs |
| `DEATH_BEAST` | < 9.0 | 30 overs |
| `DEATH_LIABILITY` | > 12.0 AND SR > 18.0 | 30 overs |
| `MIDDLE_AND_DEATH_SPECIALIST` | Bowls both phases | N/A |

**Note:** DEATH_LIABILITY requires BOTH high economy (>12.0) AND poor strike rate (>18.0) to prevent mislabeling aggressive wicket-takers.

#### Bowler Elite Tags (Top Performers)

| Tag | Criteria |
|-----|----------|
| `PP_ELITE` | Top 25% economy in powerplay |
| `MID_OVERS_ELITE` | Top 25% economy in middle overs |
| `DEATH_ELITE` | Top 25% economy at death |

#### Bowler Handedness Tags

| Tag | Criteria | Minimum Sample |
|-----|----------|----------------|
| `LHB_SPECIALIST` | Economy ≥ 1.0 better vs LHB than RHB | 60 balls vs each |
| `RHB_SPECIALIST` | Economy ≥ 1.0 better vs RHB than LHB | 60 balls vs each |
| `LHB_WICKET_TAKER` | Lower SR vs LHB (takes wickets faster) | 3+ wickets vs LHB |
| `RHB_WICKET_TAKER` | Lower SR vs RHB | 3+ wickets vs RHB |
| `LHB_PRESSURE` | Dot ball % ≥ 5% higher vs LHB | 60 balls vs each |
| `RHB_PRESSURE` | Dot ball % ≥ 5% higher vs RHB | 60 balls vs each |
| `LHB_VULNERABLE` | Economy ≥ 1.0 worse vs LHB | 60 balls vs each |
| `RHB_VULNERABLE` | Economy ≥ 1.0 worse vs RHB | 60 balls vs each |

#### Batter Entry Position Tags (Revised Sprint 3.0)

| Tag | Avg Entry Ball | Over Range | Notes |
|-----|----------------|------------|-------|
| `TOP_ORDER` | < 30 balls | Overs 1-5 | Openers + #3 |
| `MIDDLE_ORDER` | 30-72 balls | Overs 5-12 | #4-5 |
| `LOWER_ORDER` | > 72 balls | Overs 12+ | #6-7+ finishers |

**EDA Percentiles (2023+ IPL):**
- P25: 21.7 balls (Top Order cutoff)
- P50: 67.8 balls (Middle Order median)
- P75: 95.6 balls (Lower Order typical)

#### Bowler Role Tags

| Tag | Criteria |
|-----|----------|
| `POWERPLAY_BOWLER` | 1st over median in overs 0-5 |
| `DEATH_BOWLER` | 4th over median in overs 16+ |
| `PP_AND_DEATH_SPECIALIST` | Both PP and death criteria met |
| `MIDDLE_OVERS_BOWLER` | Neither PP nor death criteria |

### Bowling Style Categories

| Category | Examples |
|----------|----------|
| **Right-arm pace** | Fast, fast-medium, medium-fast |
| **Left-arm pace** | Left-arm fast, left-arm medium |
| **Right-arm off-spin** | Off-break, finger spin |
| **Right-arm leg-spin** | Leg-break, googly |
| **Left-arm orthodox** | Slow left-arm orthodox |
| **Left-arm wrist spin** | Chinaman, left-arm unorthodox |

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

**Role Archetypes:**
| Tag | Count | Description |
|-----|-------|-------------|
| `EXPLOSIVE_OPENER` | 15 | Aggressive openers with high SR in powerplay (163+ SR) |
| `PLAYMAKER` | 24 | Creative stroke-makers, adaptable across phases |
| `ANCHOR` | 21 | Stabilizers who build innings, lower SR but high consistency |
| `ACCUMULATOR` | 49 | Consistent run-scorers, reliable middle-order batters |
| `MIDDLE_ORDER` | 45 | Middle-order specialists batting at positions 3-5 |
| `FINISHER` | 21 | Death-overs specialists, high SR in final overs |

**Performance Tags:**
| Tag | Count | Criteria |
|-----|-------|----------|
| `PP_DOMINATOR` | 14 | Strike rate >150 in powerplay with 50+ PP balls |
| `DEATH_SPECIALIST` | 47 | Strike rate >160 at death with 30+ death balls |
| `MIDDLE_OVERS_ACCELERATOR` | 34 | Strong acceleration in middle overs (7-15) |
| `SIX_HITTER` | 47 | Six percentage >15% |
| `CONSISTENT` | 34 | Innings count >50 with >100 balls |
| `PACE_SPECIALIST` | 40 | Excels vs pace bowling (SR ≥130, Avg ≥25) |
| `SPIN_SPECIALIST` | 24 | Excels vs spin bowling (SR ≥130, Avg ≥25) |

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

**Type Tags:**
| Tag | Count | Description |
|-----|-------|-------------|
| `PACER` | 116 | Fast/medium-fast bowlers |
| `SPINNER` | 68 | Spin bowlers (off-spin, leg-spin, left-arm orthodox/wrist) |

**Role Tags:**
| Tag | Count | Description |
|-----|-------|-------------|
| `WORKHORSE` | 112 | High-volume bowlers, bowl multiple phases |
| `NEW_BALL_SPECIALIST` | 43 | Opening bowlers, excel with new ball in powerplay |
| `MIDDLE_OVERS_CONTROLLER` | 50 | Middle-phase specialists, economy-focused spinners |
| `DEATH_SPECIALIST` | 19 | Death-overs specialists, bowl overs 16-20 |
| `PART_TIMER` | 44 | Part-time bowlers, secondary bowling options |

**Performance Tags:**
| Tag | Count | Description |
|-----|-------|-------------|
| `PRESSURE_BUILDER` | 82 | High dot ball %, creates pressure |
| `PROVEN_WICKET_TAKER` | 29 | Consistent wicket-taking ability |

**Phase Elite Tags:**
| Tag | Count | Criteria |
|-----|-------|----------|
| `PP_ELITE` | 52 | Top performer in powerplay phase |
| `MID_OVERS_ELITE` | 38 | Top performer in middle overs |
| `DEATH_ELITE` | 21 | Top performer at death |

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

*Cricket Playbook v3.0.1 - Sprint 3.0 (Founder Review #4)*
