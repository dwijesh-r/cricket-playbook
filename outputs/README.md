# Outputs

Generated data artifacts organized by category.

**Version:** 4.0.0 | **Data Range:** IPL 2023-2025 (219 matches) | **Last Updated:** 2026-02-04

---

## Directory Structure

```
outputs/
├── README.md               # This file
├── manifest.json           # Output manifest with metadata
├── schema.md               # Schema documentation
│
├── predicted_xii/          # NEW: Predicted playing XII per team
│   ├── predicted_xii_2026.json
│   ├── {team}_predicted_xii.json
│   └── README.md
│
├── depth_charts/           # NEW: Position-by-position rankings
│   ├── depth_charts_2026.json
│   ├── {team}_depth_chart.json
│   └── README.md
│
├── tags/                   # Player classification files
│   ├── player_tags.json
│   ├── player_tags_2023.json
│   ├── player_clustering_2023.csv
│   └── bowler_role_tags.csv
│
├── matchups/               # Head-to-head analysis
│   ├── batter_bowling_type_matchup.csv
│   ├── batter_bowling_type_matchup_2023.csv
│   ├── batter_bowling_type_detail.csv
│   ├── batter_bowling_type_detail_2023.csv
│   ├── bowler_handedness_matchup.csv
│   ├── bowler_handedness_matchup_2023.csv
│   ├── batter_entry_points.csv
│   └── batter_entry_points_2023.csv
│
├── metrics/                # Performance metrics
│   ├── batter_consistency_index.csv
│   ├── batter_consistency_by_year.csv
│   ├── partnership_synergy.csv
│   ├── partnership_synergy_by_year.csv
│   ├── bowler_pressure_sequences.csv
│   ├── bowler_pressure_by_year.csv
│   ├── bowler_phase_performance.csv
│   ├── bowler_phase_distribution_grouped.csv
│   └── bowler_over_timing.csv
│
└── team/                   # Team-level data
    ├── team_venue_records.csv
    ├── team_venue_records_by_year.csv
    └── ipl_2026_squad_experience.csv
```

---

## Predicted XII (`predicted_xii/`) - NEW in v4.0

Algorithm-generated optimal playing XI + Impact Player for all 10 IPL 2026 teams.

| File | Description |
|------|-------------|
| `predicted_xii_2026.json` | Consolidated predictions for all teams |
| `{team}_predicted_xii.json` | Individual team files (e.g., `mi_predicted_xii.json`) |

**Features:**
- Constraint-satisfaction algorithm (max 4 overseas, min 5 bowling options, at least 1 spinner)
- Role-based selection with batting position assignment
- Impact Player recommendation
- Balance metrics (overseas count, bowling options, left-handers in top 6)

See `predicted_xii/README.md` for full methodology.

---

## Depth Charts (`depth_charts/`) - NEW in v4.0

Position-by-position player rankings for all 10 IPL 2026 teams.

| File | Description |
|------|-------------|
| `depth_charts_2026.json` | Consolidated depth charts for all teams |
| `{team}_depth_chart.json` | Individual team files (e.g., `mi_depth_chart.json`) |

**9 Positions Ranked:**
1. Opener (Top 3)
2. #3 Batter (Top 3)
3. Middle Order #4-5 (Top 3)
4. Finisher #6-7 (Top 3)
5. Wicketkeeper (Primary + Backup)
6. Lead Pacer (Top 2)
7. Supporting Pacer - PP & Death Specialists (Top 3 each)
8. Lead Spinner (Top 2)
9. All-rounder - Batting & Bowling first (Top 3 each)

**Rating System:** 0-10 scale with decimals + "what works" / "what doesn't" descriptions.

See `depth_charts/README.md` for full methodology.

---

## Tags (`tags/`)

Player classification and clustering outputs.

| File | Records | Description |
|------|---------|-------------|
| `player_tags.json` | 155 players | Multi-tag classifications (all criteria) |
| `player_tags_2023.json` | 155 players | 2023+ filtered version |
| `player_clustering_2023.csv` | 175 players | K-means cluster assignments |
| `bowler_role_tags.csv` | 184 bowlers | Phase-based role tags |

### Tag Categories

**Batter Role Tags:** EXPLOSIVE_OPENER, PLAYMAKER, ANCHOR, ACCUMULATOR, MIDDLE_ORDER, FINISHER

**Bowler Role Tags:** PACER, SPINNER, WORKHORSE, NEW_BALL_SPECIALIST, MIDDLE_OVERS_CONTROLLER, DEATH_SPECIALIST, MIDDLE_AND_DEATH_SPECIALIST, PART_TIMER

**Matchup Tags:** SPECIALIST_VS_PACE, SPECIALIST_VS_SPIN, VULNERABLE_VS_PACE, VULNERABLE_VS_SPIN

**Phase Tags:** PP_BEAST, PP_LIABILITY, DEATH_BEAST, DEATH_LIABILITY

---

## Matchups (`matchups/`)

Head-to-head performance analysis.

| File | Records | Description |
|------|---------|-------------|
| `batter_bowling_type_matchup.csv` | ~800 | Batter vs pace/spin summary |
| `batter_bowling_type_matchup_2023.csv` | ~400 | 2023+ filtered version |
| `batter_bowling_type_detail.csv` | ~4,000 | Detailed by 6 bowling styles |
| `batter_bowling_type_detail_2023.csv` | ~2,000 | 2023+ filtered version |
| `bowler_handedness_matchup.csv` | ~400 | Bowler vs LHB/RHB performance |
| `bowler_handedness_matchup_2023.csv` | ~300 | 2023+ filtered version |
| `batter_entry_points.csv` | 150 batters | Entry position classification |
| `batter_entry_points_2023.csv` | 197 batters | 2023+ with thresholds |

### Entry Point Thresholds
| Classification | Average Entry Ball |
|----------------|-------------------|
| TOP_ORDER | < 30 |
| MIDDLE_ORDER | 30 - 72 |
| LOWER_ORDER | > 72 |

---

## Metrics (`metrics/`)

Performance metrics and derived statistics.

| File | Records | Description |
|------|---------|-------------|
| `batter_consistency_index.csv` | ~200 | Consistency scores (CV-based) |
| `batter_consistency_by_year.csv` | ~500 | Yearly breakdown |
| `partnership_synergy.csv` | ~300 | Partnership performance scores |
| `partnership_synergy_by_year.csv` | ~800 | Yearly partnership data |
| `bowler_pressure_sequences.csv` | ~250 | Dot ball sequence analysis |
| `bowler_pressure_by_year.csv` | ~600 | Yearly pressure data |
| `bowler_phase_performance.csv` | ~400 | PP/Middle/Death stats |
| `bowler_phase_distribution_grouped.csv` | ~300 | Phase distribution tables |
| `bowler_over_timing.csv` | ~200 | Over timing patterns |

---

## Team (`team/`)

Team-level aggregated data.

| File | Records | Description |
|------|---------|-------------|
| `team_venue_records.csv` | ~100 | Team win/loss by venue |
| `team_venue_records_by_year.csv` | ~250 | Yearly venue breakdown |
| `ipl_2026_squad_experience.csv` | 231 | Squad experience metrics |

---

## Key Metrics Reference

### Batting Metrics
| Metric | Formula | Good Value |
|--------|---------|------------|
| Strike Rate (SR) | (Runs / Balls) × 100 | >140 |
| Average (Avg) | Runs / Dismissals | >30 |
| Balls per Dismissal (BPD) | Balls / Dismissals | >20 |
| Dot Ball % | Dots / Balls × 100 | <30% |
| Boundary % | (4s + 6s) / Balls × 100 | >15% |

### Bowling Metrics
| Metric | Formula | Good Value |
|--------|---------|------------|
| Economy | (Runs / Balls) × 6 | <8.0 |
| Strike Rate | Balls / Wickets | <20 |
| Dot Ball % | Dots / Balls × 100 | >40% |

---

## Tag Criteria Reference

### Specialist Tags (require ALL three)
| Condition | Threshold |
|-----------|-----------|
| Strike Rate | ≥ 130 |
| Average | ≥ 25 |
| Balls/Dismissal | ≥ 20 |

### Vulnerable Tags (ANY one triggers)
| Condition | Threshold |
|-----------|-----------|
| Strike Rate | < 105 |
| Average | < 15 |
| Balls/Dismissal | < 15 |

### Phase Tags (Bowlers)
| Tag | Economy | Min Overs |
|-----|---------|-----------|
| PP_BEAST | < 7.0 | 30 |
| PP_LIABILITY | > 9.5 | 30 |
| DEATH_BEAST | < 9.0 | 30 |
| DEATH_LIABILITY | > 12.0 AND SR > 18.0 | 30 |

---

## Regenerating Outputs

```bash
# Generate all 2023+ outputs
python scripts/generators/generate_all_2023_outputs.py

# Generate specific outputs
python scripts/analysis/player_clustering_v2.py
python scripts/analysis/batter_bowling_type_matchup.py
python scripts/analysis/bowler_handedness_matchup.py
python scripts/generators/sprint_3_p1_features.py

# Generate new Sprint 4.0 outputs
python scripts/generators/generate_predicted_xii.py
python scripts/generators/generate_depth_charts.py
```

---

## Data Quality Notes

1. **2023+ Focus:** All outputs use 2023-2025 IPL data only
2. **Sample Size:** Files include sample size indicators (HIGH/MEDIUM/LOW)
3. **Player ID Audit:** 15 mismatches documented in `analysis/player_id_audit_report.md`
4. **Threshold EDA:** See `analysis/threshold_eda_2023.md` for percentile analysis

---

*Cricket Playbook v4.0.0*
