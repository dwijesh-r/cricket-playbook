# Data

Source data, database, and reference files.

**Version:** 4.0.0 | **Last Updated:** 2026-02-04

---

## Directory Structure

```
data/
├── README.md                       # This file
├── cricket_playbook.duckdb         # Main DuckDB database (159MB)
│
├── ipl_2026_squads.csv             # IPL 2026 team rosters
├── ipl_2026_player_contracts.csv   # Player contract prices
├── bowler_classifications_v2.csv   # Bowling style mappings (current)
├── bowler_classifications_v1_archived.csv  # Legacy (archived)
│
├── raw/                            # Source Cricsheet ZIP files
│   └── (18 T20 datasets)
│
├── processed/                      # Intermediate processed data
│   ├── schema.md
│   └── QA_CERTIFICATE_1.0.0.md
│
└── manifests/                      # Data manifest files
    └── manifest.json
```

---

## Database (DuckDB)

**File:** `cricket_playbook.duckdb` (159MB)

### Core Tables

| Table | Rows | Description |
|-------|------|-------------|
| `fact_ball` | 2,137,915 | Ball-by-ball delivery records |
| `dim_player` | ~15,000 | Player dimension (all T20 players) |
| `dim_match` | 9,357 | Match dimension |
| `dim_team` | ~200 | Team dimension |

### Key Columns in `fact_ball`

| Column | Type | Description |
|--------|------|-------------|
| `match_id` | INT | Foreign key to dim_match |
| `innings` | INT | 1 or 2 |
| `over_num` | INT | Over number (1-20) |
| `ball_num` | INT | Ball in over (1-6+) |
| `ball_seq` | INT | Sequential ball number (1-120) |
| `batter_id` | INT | Foreign key to dim_player |
| `bowler_id` | INT | Foreign key to dim_player |
| `batter_runs` | INT | Runs scored by batter |
| `extra_runs` | INT | Extra runs (wides, no-balls, etc.) |
| `total_runs` | INT | Total runs for delivery |
| `is_wicket` | BOOL | Dismissal on this ball |
| `dismissal_kind` | STR | Type of dismissal |

### Analytics Views

The database contains 35 analytics views created by `scripts/core/analytics_ipl.py`. Key views:

| View | Description |
|------|-------------|
| `analytics_ipl_batting_career` | Career batting stats |
| `analytics_ipl_bowling_career` | Career bowling stats |
| `analytics_ipl_batter_phase` | Phase-wise batting |
| `analytics_ipl_bowler_phase` | Phase-wise bowling |
| `analytics_ipl_batter_vs_bowler` | Head-to-head matchups |

---

## Squad Data

### `ipl_2026_squads.csv`

| Column | Description |
|--------|-------------|
| `team_name` | Full team name |
| `player_name` | Player name |
| `player_id` | Cricsheet player ID |
| `role` | Batter, Bowler, All-rounder, Wicketkeeper |
| `bowling_arm` | Right-arm, Left-arm |
| `bowling_type` | Fast, Off-spin, Leg-spin, etc. |
| `batting_hand` | Right-hand, Left-hand |
| `batter_classification` | Elite Top-Order, Power Finisher, etc. |
| `bowler_classification` | Workhorse Seamer, Middle-Overs Spinner, etc. |
| `batter_tags` | Pipe-separated batter tags |
| `bowler_tags` | Pipe-separated bowler tags |
| `is_captain` | TRUE if team captain (NEW in v4.0) |

**Records:** 231 players across 10 teams

**Captains (IPL 2026):**
| Team | Captain |
|------|---------|
| CSK | Ruturaj Gaikwad |
| MI | Hardik Pandya |
| RCB | Rajat Patidar |
| KKR | Ajinkya Rahane |
| RR | Riyan Parag* |
| PBKS | Shreyas Iyer |
| DC | Axar Patel |
| SRH | Pat Cummins |
| GT | Shubman Gill |
| LSG | Rishabh Pant |

*\* Subject to confirmation*

### `ipl_2026_player_contracts.csv`

| Column | Description |
|--------|-------------|
| `player_name` | Player name |
| `team` | Team abbreviation |
| `price_inr` | Contract price in INR |
| `price_usd` | Contract price in USD |
| `category` | RETAINED, AUCTION, RTM |

---

## Bowler Classifications

### `bowler_classifications_v2.csv` (Current)

| Column | Description |
|--------|-------------|
| `player_id` | Cricsheet player ID |
| `player_name` | Player name |
| `bowling_style` | Standardized bowling style |

**Coverage:** 280 bowlers (98.8% of IPL balls)

**Bowling Styles:**
- Right-arm pace
- Left-arm pace
- Right-arm off-spin
- Right-arm leg-spin
- Left-arm orthodox
- Left-arm wrist spin

---

## Raw Data (`raw/`)

Source Cricsheet ZIP files (18 T20 datasets):

| Dataset | Matches | Coverage |
|---------|---------|----------|
| IPL | 1,089 | 2008-2025 |
| T20 International | 1,500+ | All time |
| BBL | 500+ | All time |
| CPL | 400+ | All time |
| PSL | 300+ | All time |
| Other T20 leagues | 5,000+ | Various |

**Total:** 9,357 T20 matches

---

## Data Pipeline

```bash
# 1. Ingest raw data into DuckDB
python scripts/core/ingest.py

# 2. Create analytics views
python scripts/core/analytics_ipl.py

# 3. Validate schema
python scripts/core/validate_schema.py
```

---

## Data Quality

### Known Issues
- **15 player ID mismatches** documented in `analysis/player_id_audit_report.md`
- Root cause: Surname collisions (Singh, Sharma, Kumar, Khan)
- Fix planned for Sprint 3.1

### Validation
- Schema validation: 33 checks
- Smoke tests: 76 pytest tests
- See `data/processed/QA_CERTIFICATE_1.0.0.md`

---

## Important Notes

1. **2023+ Filter:** Analytics use only 2023-2025 IPL data (219 matches)
2. **Do Not Modify:** Never edit `cricket_playbook.duckdb` directly
3. **Regenerate Views:** Run `analytics_ipl.py` after schema changes

---

*Cricket Playbook v4.0.0*
