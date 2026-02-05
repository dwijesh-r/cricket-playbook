# Generator Scripts

Output file generators for Cricket Playbook analytics.

**Version:** 4.1.0 | **Last Updated:** 2026-02-05

---

## Overview

Generator scripts produce output files (JSON, CSV, Markdown) from the DuckDB analytics database. These outputs power the dashboard, stat packs, and external integrations.

```
generators/
├── README.md                      # This file
├── generate_stat_packs.py         # Team stat pack generator
├── generate_predicted_xii.py      # SUPER SELECTOR v3.0
├── generate_depth_charts.py       # Position depth charts
├── generate_2023_outputs.py       # 2023+ filtered outputs
├── generate_all_2023_outputs.py   # Batch 2023+ generation
└── sprint_3_p1_features.py        # P1 feature outputs
```

---

## Quick Start

```bash
# Generate all team stat packs
python scripts/generators/generate_stat_packs.py

# Generate predicted XIIs for all 10 teams
python scripts/generators/generate_predicted_xii.py

# Generate depth charts
python scripts/generators/generate_depth_charts.py

# Batch generate all 2023+ filtered outputs
python scripts/generators/generate_all_2023_outputs.py
```

---

## Script Reference

### `generate_stat_packs.py`

**Purpose:** Generates comprehensive markdown stat packs for each IPL 2026 team.

**Authors:** Tom Brady (Product Owner), Stephen Curry (Analytics), Andy Flower (Domain Review)

#### Usage
```bash
python scripts/generators/generate_stat_packs.py
```

#### Input
- `data/cricket_playbook.duckdb` - Analytics database
- `outputs/player_tags.json` - Player classification tags

#### Output
- `stat_packs/{TEAM}/{TEAM}_stat_pack.md` - One file per team (10 total)

#### Output Location
```
stat_packs/
├── CSK/CSK_stat_pack.md
├── MI/MI_stat_pack.md
├── RCB/RCB_stat_pack.md
├── KKR/KKR_stat_pack.md
├── DC/DC_stat_pack.md
├── PBKS/PBKS_stat_pack.md
├── RR/RR_stat_pack.md
├── SRH/SRH_stat_pack.md
├── GT/GT_stat_pack.md
└── LSG/LSG_stat_pack.md
```

#### Stat Pack Sections
1. **Squad Overview** - Full roster with prices, roles, player archetypes
2. **Player Archetypes** - K-means clustering results (batter/bowler clusters)
3. **Key Player Tags** - Phase analysis and matchup tags
4. **Historical Record vs Opposition** - Head-to-head records
5. **Venue Analysis** - Home/away performance, pitch characteristics
6. **Squad Batting Analysis** - Career stats, phase-wise breakdown
7. **Squad Bowling Analysis** - Career stats, phase distribution
8. **Key Batter vs Opposition** - Top 5 batters' team matchups
9. **Key Bowler vs Opposition** - Top 5 bowlers' team matchups
10. **Key Player Venue Performance** - Batter venue stats
11. **Andy Flower's Tactical Insights** - Death bowling, PP batting, spin vulnerabilities

#### Configuration
```python
# Team aliases for historical data
FRANCHISE_ALIASES = {
    "Delhi Capitals": ["Delhi Capitals", "Delhi Daredevils"],
    "Punjab Kings": ["Punjab Kings", "Kings XI Punjab"],
    ...
}

# Home venue mappings
TEAM_HOME_VENUES = {
    "Chennai Super Kings": ["MA Chidambaram Stadium, Chepauk, Chennai"],
    ...
}
```

---

### `generate_predicted_xii.py`

**Purpose:** Generates optimal XII (XI + Impact Player) for each IPL 2026 team using the SUPER SELECTOR v3.0 algorithm.

**Author:** Stephen Curry (Analytics Lead)

**Algorithm:** Statistical Unified Player Evaluation and Ranking SELECTOR (SUPER SELECTOR)

#### Usage
```bash
python scripts/generators/generate_predicted_xii.py
```

#### Input
- `data/ipl_2026_squads.csv` - Squad roster data
- `data/ipl_2026_player_contracts.csv` - Auction prices
- `outputs/player_tags_2023.json` - Player performance tags
- `outputs/matchups/batter_entry_points_2023.csv` - Batting positions
- `outputs/metrics/batter_consistency_index.csv` - Batter metrics
- `outputs/metrics/bowler_pressure_sequences.csv` - Bowler metrics

#### Output
- `outputs/predicted_xii/predicted_xii_2026.json` - Consolidated all teams
- `outputs/predicted_xii/{team}_predicted_xii.json` - Per-team files

#### Output Structure
```json
{
  "generated_at": "2026-02-04",
  "version": "3.0",
  "algorithm_name": "SUPER SELECTOR",
  "teams": {
    "CSK": {
      "team_name": "Chennai Super Kings",
      "captain": "Ruturaj Gaikwad",
      "wicketkeeper": "MS Dhoni",
      "xi": [
        {
          "batting_position": 1,
          "player_name": "Ruturaj Gaikwad",
          "role": "Opener",
          "is_overseas": false,
          "rationale": "Elite top-order anchor"
        },
        ...
      ],
      "impact_player": {...},
      "balance": {
        "overseas_count": 4,
        "bowling_options": 6,
        "spinners": 2,
        "pacers": 3
      }
    }
  }
}
```

#### Algorithm Constraints
| Constraint | Description |
|------------|-------------|
| C1 | Captain cannot be Impact Player |
| C2 | Maximum 4 overseas players |
| C3 | Minimum 20 overs bowling coverage |
| C4 | At least 1 wicketkeeper |
| C5 | At least 1 spinner |

#### Scoring Formula
```
PLAYER_SCORE = BASE + CLASSIFICATION + TAGS + METRICS + PRICE_BONUS

Batter Metrics:
  - boundary_pct: +5/10/15 points for 20%/24%/28%+
  - consistency_index: +4/8 points for 45/55+
  - high_impact_pct: +3/6 points for 35%/50%+

Bowler Metrics:
  - death_dot_pct: +5/10/15 points for 25%/30%/35%+
  - death_economy: +6/12 points for 8.5/7.0 or lower

Price Tiers:
  - 15+ Cr: +15%
  - 10-15 Cr: +10%
  - 5-10 Cr: +5%
```

#### Batting Position Assignment
Positions are assigned based on historical entry point data:
- Tier 1 (Openers): avg_entry_ball 0-15
- Tier 2 (Top Order #3-4): avg_entry_ball 16-45
- Tier 3 (Middle Order #5-6): avg_entry_ball 46-75
- Tier 4 (Finisher #7-8): avg_entry_ball 76-105
- Tier 5 (Bowlers #9-11): 105+ or no batting data

---

### `generate_depth_charts.py`

**Purpose:** Generates position-by-position depth charts for all 10 IPL 2026 teams.

**Author:** Stephen Curry (Analytics Lead)

#### Usage
```bash
python scripts/generators/generate_depth_charts.py
```

#### Input
- `data/ipl_2026_squads.csv` - Squad roster
- `data/ipl_2026_player_contracts.csv` - Contract data
- `outputs/player_tags_2023.json` - Player tags
- `outputs/matchups/batter_entry_points_2023.csv` - Entry positions
- `outputs/metrics/bowler_phase_performance.csv` - Phase metrics

#### Output
- `outputs/depth_charts/depth_charts_2026.json` - Consolidated
- `outputs/depth_charts/{team}_depth_chart.json` - Per-team files
- `outputs/depth_charts/README.md` - Generated documentation

#### Positions Analyzed
| Position | Players Ranked | Key Criteria |
|----------|----------------|--------------|
| Opener | Top 3 | PP SR 30%, PP Boundary% 20%, Career Avg 15% |
| #3 Batter | Top 3 | Versatility, adaptability across phases |
| Middle Order #4-5 | Top 3 | Spin performance 25%, Middle overs 25% |
| Finisher #6-7 | Top 3 | Death SR 35%, Boundary% 20%, bowling utility |
| Wicketkeeper | Primary + Backup | Keeping 30%, Batting 50%, Experience 20% |
| Lead Pacer | Top 2 | Wickets 25%, Death eco 25%, PP eco 20% |
| PP Pacer | Top 3 | PP Economy 35%, PP SR 30%, Swing 20% |
| Death Pacer | Top 3 | Death Economy 40%, Death SR 25% |
| Lead Spinner | Top 2 | Middle overs eco 30%, SR 25% |
| Batting AR | Top 3 | Finisher 45%, Middle 20%, Bowling 35% |
| Bowling AR | Top 3 | Bowling 50%, Batting 25%, Lower-order SR 15% |

#### Rating Scale
Ratings are out of 10 based on weighted scores:
- #1 player: 50% weight
- #2 player: 30% weight
- #3 player: 20% weight
- Bonuses for strong depth across options

#### Output Structure
```json
{
  "team": "CSK",
  "overall_rating": 7.2,
  "strongest_position": "Lead Spinner",
  "weakest_position": "Finisher #6-7",
  "vulnerabilities": ["Finisher: thin depth (rating 5.2)"],
  "positions": {
    "opener": {
      "name": "Opener",
      "rating": 7.8,
      "what_works": "Elite #1 in Ruturaj Gaikwad",
      "what_doesnt": "Overseas heavy (2 of 3)",
      "players": [
        {"rank": 1, "name": "Ruturaj Gaikwad", "score": 85.2, ...},
        {"rank": 2, "name": "Devon Conway", "score": 72.1, ...}
      ]
    }
  }
}
```

---

### `generate_2023_outputs.py`

**Purpose:** Generates 2023+ filtered CSV outputs for matchup analysis.

#### Usage
```bash
python scripts/generators/generate_2023_outputs.py
```

#### Output Files
- `outputs/matchups/batter_bowling_type_2023.csv`
- `outputs/matchups/batter_entry_points_2023.csv`
- `outputs/matchups/bowler_handedness_2023.csv`
- `outputs/tags/player_tags_2023.json`
- `outputs/metrics/batter_consistency_index.csv`
- `outputs/metrics/bowler_phase_performance.csv`

---

### `generate_all_2023_outputs.py`

**Purpose:** Batch generates all 2023+ filtered outputs in one run.

#### Usage
```bash
python scripts/generators/generate_all_2023_outputs.py
```

#### Outputs Generated
1. Player tags (batters and bowlers)
2. Batter vs bowling type matchups
3. Batter entry point analysis
4. Bowler vs handedness matchups
5. Bowler phase performance metrics
6. Batter consistency index
7. Bowler pressure sequences

---

### `sprint_3_p1_features.py`

**Purpose:** Generates P1 feature outputs including consistency, synergy, and pressure metrics.

#### Usage
```bash
python scripts/generators/sprint_3_p1_features.py
```

#### Features Generated
- Batter consistency index
- Partnership synergy analysis
- Pressure situation performance
- Clutch player identification

---

## Common Usage Patterns

### Generate All Outputs
```bash
# Full generation pipeline
python scripts/generators/generate_all_2023_outputs.py
python scripts/generators/generate_predicted_xii.py
python scripts/generators/generate_depth_charts.py
python scripts/generators/generate_stat_packs.py
```

### Generate for Specific Team
Most generators process all teams by default. For single-team generation, modify the script or filter outputs.

### Regenerate After Data Update
```bash
# After running ingest.py and analytics_ipl.py
python scripts/generators/generate_all_2023_outputs.py
python scripts/generators/generate_predicted_xii.py
python scripts/generators/generate_depth_charts.py
python scripts/generators/generate_stat_packs.py
python scripts/the_lab/update_the_lab.py
```

---

## Dependencies

**Python Packages:**
```bash
pip install duckdb pandas numpy
```

**Database:**
- `data/cricket_playbook.duckdb` must exist
- Analytics views must be created via `core/analytics_ipl.py`

**Data Files:**
- `data/ipl_2026_squads.csv`
- `data/ipl_2026_player_contracts.csv`
- `outputs/player_tags_2023.json` (for predicted XII and depth charts)

---

## Output Locations Summary

| Generator | Output Directory |
|-----------|------------------|
| generate_stat_packs.py | `stat_packs/` |
| generate_predicted_xii.py | `outputs/predicted_xii/` |
| generate_depth_charts.py | `outputs/depth_charts/` |
| generate_2023_outputs.py | `outputs/matchups/`, `outputs/tags/`, `outputs/metrics/` |
| generate_all_2023_outputs.py | Multiple directories |
| sprint_3_p1_features.py | `outputs/metrics/` |

---

## Troubleshooting

### "Database not found"
```bash
# Ensure database exists
ls -la data/cricket_playbook.duckdb

# Run ingestion if missing
python scripts/core/ingest.py
python scripts/core/analytics_ipl.py
```

### "View does not exist"
```bash
# Recreate analytics views
python scripts/core/analytics_ipl.py
```

### "player_tags_2023.json not found"
```bash
# Generate tags first
python scripts/generators/generate_all_2023_outputs.py
```

### Empty output files
- Check database has IPL 2023+ data
- Verify squad CSV has correct player_id mappings
- Run validation: `python scripts/core/validate_schema.py`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2026-02-05 | SUPER SELECTOR v3.0 with metrics-based scoring |
| 2.0.0 | 2026-02-01 | Added depth charts generator |
| 1.0.0 | 2026-01-20 | Initial stat packs generator |

---

*Cricket Playbook Generators v4.1.0*
