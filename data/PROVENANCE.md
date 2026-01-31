# Data Provenance

**Document Owner:** Brock Purdy
**Last Updated:** 2026-01-31

---

## Overview

This document traces the origin, processing, and quality characteristics of all data used in Cricket Playbook.

---

## Primary Data Sources

### 1. Ball-by-Ball Match Data

| Attribute | Value |
|-----------|-------|
| **Source** | Cricsheet (https://cricsheet.org) |
| **Format** | JSON (ball-by-ball) |
| **License** | Open Data Commons Attribution License |
| **Coverage** | All T20 matches globally |
| **Total Matches** | 9,357 |
| **IPL Matches** | 1,089 (2008-2025) |
| **Analysis Window** | IPL 2023-2025 (219 matches) |

**What's Included:**
- Ball-by-ball delivery data
- Batter and bowler identifiers
- Runs scored (batter runs, extras)
- Wickets and dismissal types
- Match metadata (venue, date, toss, result)

**What's NOT Included:**
- Ball speed/trajectory
- Field positions
- Commentary/qualitative assessment
- Hawkeye/tracking data

### 2. IPL 2026 Squad Data

| Attribute | Value |
|-----------|-------|
| **Source** | Official IPL announcements, ESPNcricinfo |
| **File** | `data/ipl_2026_squads.csv` |
| **Last Updated** | 2026-01-26 |
| **Players** | 231 across 10 teams |

**Columns:**
- `team_name` - Franchise name
- `player_name` - Player full name
- `player_id` - Cricsheet unique identifier
- `role` - BATTER, BOWLER, ALL-ROUNDER, WICKETKEEPER
- `bowling_arm` - Right-arm, Left-arm
- `bowling_type` - Fast, Off-spin, Leg-spin, etc.
- `batting_hand` - Right-hand, Left-hand
- `batter_classification` - Cluster assignment
- `bowler_classification` - Cluster assignment
- `batter_tags` - Multi-tag assignments
- `bowler_tags` - Multi-tag assignments

### 3. Player Contract Data

| Attribute | Value |
|-----------|-------|
| **Source** | Official IPL auction results, team announcements |
| **File** | `data/ipl_2026_player_contracts.csv` |
| **Last Updated** | 2026-01-20 |

**Columns:**
- `player_name` - Player full name
- `team` - Team abbreviation
- `price_inr` - Contract value in INR
- `price_usd` - Contract value in USD
- `category` - RETAINED, AUCTION, RTM

### 4. Bowler Classifications

| Attribute | Value |
|-----------|-------|
| **Source** | Manual curation from ESPNcricinfo profiles |
| **File** | `data/bowler_classifications_v2.csv` |
| **Coverage** | 280 bowlers (98.8% of IPL balls) |

**Bowling Styles:**
- Right-arm pace
- Left-arm pace
- Right-arm off-spin
- Right-arm leg-spin
- Left-arm orthodox
- Left-arm wrist spin

---

## Data Processing Pipeline

### Pipeline Flow

```
Cricsheet JSON ZIPs
        ↓
scripts/core/ingest.py
        ↓
data/cricket_playbook.duckdb (fact_ball, dim_player, dim_match, dim_team)
        ↓
scripts/core/analytics_ipl.py
        ↓
34 Analytics Views
        ↓
scripts/analysis/*.py
        ↓
outputs/ (tags, matchups, metrics)
        ↓
scripts/generators/generate_stat_packs.py
        ↓
stat_packs/*.md
```

### Database Schema

| Table | Rows | Description |
|-------|------|-------------|
| `fact_ball` | 2,137,915 | Ball-by-ball delivery records |
| `dim_player` | ~15,000 | Player dimension (all T20) |
| `dim_match` | 9,357 | Match dimension |
| `dim_team` | ~200 | Team dimension |

---

## Data Quality

### Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No ball speed data | Cannot assess pace/speed variations | Use bowling type classification |
| No field position data | Cannot assess fielding impact | Focus on batter/bowler only |
| Player ID collisions | 16 cases identified and fixed | Manual ID assignment for affected players |
| Sample size variation | Some players have limited data | Confidence indicators (HIGH/MEDIUM/LOW) |

### Quality Checks

| Check | Script | Count |
|-------|--------|-------|
| Schema validation | `scripts/core/validate_schema.py` | 33 checks |
| Smoke tests | `tests/test_stat_packs.py` | 76 tests |

### Player ID Audit

16 player ID issues were identified and fixed (commit `e386035`):
- 5 collision fixes (surname conflicts)
- 11 missing IDs for uncapped players

See `analysis/player_id_audit_report.md` for details.

---

## Data Refresh Schedule

| Data Type | Refresh Frequency | Trigger |
|-----------|-------------------|---------|
| Ball-by-ball | Post-season | New Cricsheet release |
| Squad data | Pre-season | IPL auction/retention |
| Contract data | Pre-season | IPL auction |
| Bowler classifications | As needed | New players |

---

## Licensing & Attribution

### Cricsheet Data

```
This data is provided under the Open Data Commons Attribution License.
Attribution: Cricsheet (https://cricsheet.org)
```

### Derived Data

All derived outputs (tags, clusters, stat packs) are based on Cricsheet data and inherit the same attribution requirements.

---

## Contact

| Question | Contact |
|----------|---------|
| Data quality issues | Brock Purdy |
| Squad/contract data | Brock Purdy |
| Analytics methodology | Stephen Curry |
| Cricket interpretation | Andy Flower |

---

*Data Provenance v1.0.0*
*Cricket Playbook*
