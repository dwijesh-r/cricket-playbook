# Outputs

Generated data artifacts organized by category.

**Data Range:** IPL 2023-2025 (219 matches)

---

## Directory Structure

```
outputs/
├── tags/           # Player classification files
├── matchups/       # Head-to-head analysis
├── metrics/        # Performance metrics
├── team/           # Team-level data
├── manifest.json   # Output manifest
└── schema.md       # Schema documentation
```

---

## Tags (`tags/`)

Player classification and clustering outputs.

| File | Description |
|------|-------------|
| `player_tags.json` | Multi-tag player classifications |
| `player_tags_2023.json` | 2023+ filtered version |
| `player_clustering_2023.csv` | K-means cluster assignments |
| `bowler_role_tags.csv` | Bowler phase role tags |

---

## Matchups (`matchups/`)

Head-to-head performance analysis.

| File | Description |
|------|-------------|
| `batter_bowling_type_matchup.csv` | Batter vs pace/spin summary |
| `batter_bowling_type_matchup_2023.csv` | 2023+ filtered version |
| `batter_bowling_type_detail.csv` | Detailed breakdown by bowling style |
| `batter_bowling_type_detail_2023.csv` | 2023+ filtered version |
| `bowler_handedness_matchup.csv` | Bowler vs LHB/RHB performance |
| `bowler_handedness_matchup_2023.csv` | 2023+ filtered version |
| `batter_entry_points.csv` | Batter entry position analysis |
| `batter_entry_points_2023.csv` | 197 batters classified |

---

## Metrics (`metrics/`)

Performance metrics and derived statistics.

| File | Description |
|------|-------------|
| `batter_consistency_index.csv` | Batter consistency scores |
| `batter_consistency_by_year.csv` | Yearly consistency breakdown |
| `partnership_synergy.csv` | Partnership performance scores |
| `partnership_synergy_by_year.csv` | Yearly partnership data |
| `bowler_pressure_sequences.csv` | Bowler pressure performance |
| `bowler_pressure_by_year.csv` | Yearly pressure data |
| `bowler_phase_performance.csv` | Phase-wise bowling stats |
| `bowler_phase_distribution_grouped.csv` | Phase distribution tables |
| `bowler_over_timing.csv` | Bowler over timing patterns |

---

## Team (`team/`)

Team-level aggregated data.

| File | Description |
|------|-------------|
| `team_venue_records.csv` | Team win/loss by venue |
| `team_venue_records_by_year.csv` | Yearly venue breakdown |
| `ipl_2026_squad_experience.csv` | Squad experience metrics |

---

## Key Metrics

| Metric | Formula | Good Value |
|--------|---------|------------|
| Strike Rate | (Runs / Balls) × 100 | >140 |
| Economy | (Runs / Balls) × 6 | <8.0 |
| Average | Runs / Dismissals | >30 |

---

## Tag Criteria

**Specialist Tags** (require ALL three):
- Strike Rate ≥ 130
- Average ≥ 25
- Balls/Dismissal ≥ 20

**Vulnerable Tags** (ANY one triggers):
- Strike Rate < 105 OR Average < 15 OR BPD < 15

---

*Cricket Playbook v3.1.0*
