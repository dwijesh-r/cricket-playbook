# Outputs

Generated data artifacts from analytics scripts.

## Contents

| File | Description | Script |
|------|-------------|--------|
| `player_tags.json` | Multi-tag classification for 155 players | `player_clustering_v2.py` |
| `bowler_handedness_matchup.csv` | LHB/RHB matchup analysis (140 bowlers) | `bowler_handedness_matchup.py` |
| `batter_bowling_type_matchup.csv` | Batter vs pace/spin matchup | `batter_bowling_type_matchup.py` |
| `batter_bowling_type_detail.csv` | Detailed bowling type breakdown | `batter_bowling_type_matchup.py` |
| `bowler_phase_performance.csv` | Phase-wise bowler economy | `bowler_phase_tags.py` |
| `batter_entry_points.csv` | Batter entry positions (median/mode) | `entry_point_analysis.py` |
| `bowler_over_timing.csv` | Bowler over distribution | `entry_point_analysis.py` |
| `ipl_2026_squad_experience.csv` | Squad experience metrics (234 players) | `generate_experience_csv.py` |
| `manifest.json` | Data generation manifest | Various |
| `schema.md` | Schema documentation | `ingest.py` |

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

**Data Source:** All IPL matches 2008-2025 (1,169 matches)

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
