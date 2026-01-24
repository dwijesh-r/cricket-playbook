# IPL 2026 Stat Packs

**Version:** 2.7.0
**Generated:** 2026-01-24
**Prepared by:** Cricket Playbook Analytics Team

---

## Overview

This directory contains comprehensive statistical analysis for all 10 IPL 2026 teams. Each stat pack provides detailed batting, bowling, and tactical insights for the team's squad.

## Files

| File | Team | Size |
|------|------|------|
| `CSK_stat_pack.md` | Chennai Super Kings | ~25KB |
| `DC_stat_pack.md` | Delhi Capitals | ~27KB |
| `GT_stat_pack.md` | Gujarat Titans | ~24KB |
| `KKR_stat_pack.md` | Kolkata Knight Riders | ~25KB |
| `LSG_stat_pack.md` | Lucknow Super Giants | ~23KB |
| `MI_stat_pack.md` | Mumbai Indians | ~28KB |
| `PBKS_stat_pack.md` | Punjab Kings | ~24KB |
| `RCB_stat_pack.md` | Royal Challengers Bengaluru | ~26KB |
| `RR_stat_pack.md` | Rajasthan Royals | ~26KB |
| `SRH_stat_pack.md` | Sunrisers Hyderabad | ~22KB |

## Stat Pack Structure

Each stat pack contains 9 sections:

### 1. Squad Overview
- Full roster with roles, bowling types, batting hands, contract prices
- Role breakdown summary

### 2. Historical Record vs Opposition
- Win/loss records against each IPL team
- Includes franchise alias history (e.g., Delhi Daredevils data included in Delhi Capitals)

### 3. Venue Performance
- Team batting/bowling stats by venue
- Home ground analysis

### 4. Key Batters - IPL Career
- Career statistics for all squad batters
- Phase-wise breakdown (powerplay, middle, death)
- Sample size indicators (LOW/MEDIUM/HIGH)

### 5. Batter vs Bowler Type
- Performance against different bowling styles:
  - Right-arm pace
  - Left-arm pace
  - Right-arm off-spin
  - Right-arm leg-spin
  - Left-arm orthodox
  - Left-arm wrist spin

### 6. Key Bowlers - IPL Career
- Career statistics for all squad bowlers
- Phase-wise economy, wickets, dot ball %
- Sample size indicators

### 7. Bowler vs Opposition
- Performance against each IPL team

### 8. Key Matchups
- Top batter vs bowler head-to-head records

### 9. Andy Flower's Tactical Insights
- Death bowling options
- Powerplay batting options
- Potential spin vulnerabilities

---

## Player Classification Model

Stat packs integrate with the **K-means Clustering V2** model for player archetypes.

### Batter Clusters
| Cluster | Label | Description |
|---------|-------|-------------|
| 0 | CLASSIC_OPENER | Traditional openers, platform builders |
| 1 | ACCUMULATOR | Middle-order stabilizers (#3-4) |
| 2 | DEATH_FINISHER | Lower-order finishers (#5-6) |
| 3 | ELITE_EXPLOSIVE | Match-winners with 158+ SR |
| 4 | POWER_OPENER | Aggressive openers with 163+ SR |

### Bowler Clusters
| Cluster | Label | Description |
|---------|-------|-------------|
| 0 | DEATH_SPECIALIST | Dual-phase premium seamers |
| 1 | DEVELOPING | Higher economy, mixed phases |
| 2 | SPIN_CONTROLLER | Elite middle-overs spinners |
| 3 | NEW_BALL_PACER | Opening bowlers |
| 4 | SECONDARY_OPTION | Backup bowlers, part-timers |

### Player Tags

Players receive multiple tags based on performance:

**Matchup Tags:**
- `SPECIALIST_VS_PACE/SPIN` - SR ≥130 AND Avg ≥25 AND BPD ≥20
- `VULNERABLE_VS_PACE/SPIN` - SR <105 OR Avg <15 OR BPD <15

**Phase Tags (Bowlers):**
- `PP_BEAST` - Economy <7.0 in powerplay (30+ overs)
- `DEATH_BEAST` - Economy <8.5 at death (30+ overs)
- `PP_LIABILITY` / `DEATH_LIABILITY` - High economy in phase

**Handedness Tags (Bowlers):**
- `LHB_SPECIALIST` / `RHB_SPECIALIST` - ≥5% better economy
- `LHB_WICKET_TAKER` / `RHB_WICKET_TAKER` - ≥3 wickets + SR <25

See `outputs/README.md` for complete tag documentation.

---

## Data Sources

| Source | Records | Coverage |
|--------|---------|----------|
| IPL Matches | 1,169 | 2008-2025 |
| Total T20 Matches | 9,357 | Global T20 cricket |
| Ball-by-ball records | 2,137,915 | All deliveries |
| Bowler Classifications | 280 | 98.8% of IPL balls |

## Franchise Aliases

Historical team names are combined under current franchise names:

| Current Name | Historical Name |
|--------------|-----------------|
| Delhi Capitals | Delhi Daredevils |
| Punjab Kings | Kings XI Punjab |
| Royal Challengers Bengaluru | Royal Challengers Bangalore |

---

## Sample Size Indicators

Stats include sample size indicators to help assess reliability:

| Indicator | Balls Faced/Bowled | Interpretation |
|-----------|-------------------|----------------|
| HIGH | 100+ | Reliable sample |
| MEDIUM | 30-99 | Moderate confidence |
| LOW | <30 | Use with caution |

For phase-wise analysis:
- HIGH: 36+ balls
- MEDIUM: 12-35 balls
- LOW: <12 balls

---

## Known Limitations

1. **Bowling Style Coverage:** 280 IPL bowlers are classified (98.8% ball coverage). Some historical bowlers may show as "Unknown".

2. **Uncapped Players:** 10 of 231 (4.3%) players have no historical data (recent domestic players without Cricsheet IDs).

3. **Venue Names:** Some venues have multiple name variants in historical data (e.g., "Arun Jaitley Stadium" vs "Feroz Shah Kotla").

4. **Contract Prices:** Based on IPL 2026 auction and retention data. Verify against official IPL sources for final figures.

---

## Regenerating Stat Packs

To regenerate all stat packs:

```bash
cd cricket-playbook
python scripts/generate_stat_packs.py
```

This requires:
- DuckDB database at `data/cricket_playbook.duckdb`
- Analytics views created by `scripts/analytics_ipl.py`

---

## Usage Guidelines

1. **For Editorial Use:** Verify key statistics against official IPL sources before publication.

2. **Sample Sizes Matter:** Prioritize HIGH sample size stats for analysis. LOW sample stats should be presented with caveats.

3. **Phase Analysis:** Use phase-wise breakdowns (powerplay/middle/death) for tactical insights rather than aggregate stats.

4. **Matchup Data:** Head-to-head batter vs bowler stats are valuable but can have small samples. Always check ball counts.

---

## Contact

For questions or issues:
- Product Owner: Tom Brady
- Analytics: Stephen Curry
- Cricket Domain: Andy Flower
- Data Pipeline: Brock Purdy

---

*Cricket Playbook Analytics Engine v2.7.0*
