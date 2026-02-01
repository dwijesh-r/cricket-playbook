# Phase Tag Criteria - Data-Validated Thresholds

**Sprint 4.0 | IPL 2023+ Data | Andy Flower Review**

---

## WHERE THESE TAGS ARE USED

### Primary Use Cases

1. **Pre-Tournament Magazine** - Player profiles with phase-specific strengths/weaknesses
2. **Matchup Analysis** - Identifying exploitable matchups (e.g., PP_LIABILITY batter vs PP_STRIKE bowler)
3. **Team Composition Analysis** - Ensuring balanced phase coverage across squad
4. **Tactical Recommendations** - Bowling changes, batting order decisions by phase

### Generator Script

**Source:** `scripts/generators/generate_all_2023_outputs.py`

Tags are generated using multi-metric criteria (4 metrics per phase) and written to `player_tags_2023.json`.

---

## OUTPUT FILES

### Primary Tag Outputs (2023+ Data)

| File | Description | Tags Used |
|------|-------------|-----------|
| `outputs/player_tags_2023.json` | Master player tag file | All phase profile tags |
| `outputs/tags/player_tags_2023.json` | Copy in tags directory | All phase profile tags |
| `outputs/player_clustering_2023.csv` | K-means clustering output | Cluster labels |
| `outputs/tags/player_clustering_2023.csv` | Copy in tags directory | Cluster labels |

### Matchup Outputs (2023+ Data)

| File | Description | Related Tags |
|------|-------------|--------------|
| `outputs/matchups/batter_bowling_type_matchup_2023.csv` | Batter vs pace/spin | SPECIALIST_VS_*, VULNERABLE_VS_* |
| `outputs/matchups/batter_bowling_type_detail_2023.csv` | Batter vs specific bowling types | Per-type matchup tags |
| `outputs/matchups/bowler_handedness_matchup_2023.csv` | Bowler vs LHB/RHB | LHB_SPECIALIST, RHB_SPECIALIST |
| `outputs/matchups/batter_entry_points_2023.csv` | Batter entry point analysis | Entry point tags |

### All-Time Outputs (Full Historical Data)

| File | Description |
|------|-------------|
| `outputs/matchups/batter_bowling_type_matchup.csv` | All-time batter vs pace/spin |
| `outputs/matchups/batter_bowling_type_detail.csv` | All-time batter vs bowling types |
| `outputs/matchups/bowler_handedness_matchup.csv` | All-time bowler vs handedness |
| `outputs/matchups/batter_entry_points.csv` | All-time entry points |
| `outputs/tags/player_tags.json` | All-time player tags |
| `outputs/tags/bowler_role_tags.csv` | Bowler role classifications |

### Metrics Outputs

| File | Description |
|------|-------------|
| `outputs/metrics/batter_consistency_index.csv` | Batter consistency metrics |
| `outputs/metrics/batter_consistency_by_year.csv` | Year-wise consistency |
| `outputs/metrics/bowler_phase_performance.csv` | Bowler phase breakdown |
| `outputs/metrics/bowler_phase_distribution_grouped.csv` | Phase distribution |
| `outputs/metrics/bowler_over_timing.csv` | Over-by-over analysis |
| `outputs/metrics/bowler_pressure_sequences.csv` | Pressure sequence metrics |
| `outputs/metrics/bowler_pressure_by_year.csv` | Year-wise pressure |
| `outputs/metrics/partnership_synergy.csv` | Partnership analysis |
| `outputs/metrics/partnership_synergy_by_year.csv` | Year-wise partnerships |

### Team Outputs

| File | Description |
|------|-------------|
| `outputs/team/ipl_2026_squad_experience.csv` | Squad experience levels |
| `outputs/team/team_venue_records.csv` | Venue performance |
| `outputs/team/team_venue_records_by_year.csv` | Year-wise venue records |

---

## BATTER PHASE METRICS

### Powerplay (Overs 1-6) | Sample: 71 batters with 50+ balls

| Metric | 25th %ile | Median | 75th %ile | ELITE (Top 25%) | EXPLOITABLE (Bottom 25%) |
|--------|-----------|--------|-----------|-----------------|--------------------------|
| Strike Rate | 130.5 | 143.8 | 155.9 | >= 156 | <= 130 |
| Dot Ball % | 38.6% | 42.9% | 47.2% | <= 38% | >= 47% |
| Balls/Dismissal | 17.4 | 24.7 | 31.9 | >= 32 | <= 17 |
| Boundary % | 21.0% | 23.4% | 27.0% | >= 27% | <= 21% |

**Data Validation Examples:**
- ELITE: J Fraser-McGurk (SR 209.9, Boundary 40.1%), V Kohli (Dots 33.5%)
- EXPLOITABLE: T Kohler-Cadmore (SR 92.2, Dots 58.8%), DJ Hooda (SR 98.7)

---

### Middle Overs (7-15) | Sample: 100 batters with 50+ balls

| Metric | 25th %ile | Median | 75th %ile | ELITE (Top 25%) | EXPLOITABLE (Bottom 25%) |
|--------|-----------|--------|-----------|-----------------|--------------------------|
| Strike Rate | 125.0 | 139.4 | 156.7 | >= 157 | <= 125 |
| Dot Ball % | 25.4% | 29.7% | 33.1% | <= 25% | >= 33% |
| Balls/Dismissal | 15.4 | 20.6 | 28.4 | >= 28 | <= 15 |
| Boundary % | 13.7% | 16.6% | 20.1% | >= 20% | <= 14% |

**Data Validation Examples:**
- ELITE: Shubman Gill (Dots 18.3%), Abhishek Sharma (SR 199.0, Boundary 29.0%)
- EXPLOITABLE: Anuj Rawat (SR 78.6, Boundary 5.7%), A Manohar (SR 92.4, Dots 44.6%)

---

### Death Overs (16-20) | Sample: 94 batters with 30+ balls

| Metric | 25th %ile | Median | 75th %ile | ELITE (Top 25%) | EXPLOITABLE (Bottom 25%) |
|--------|-----------|--------|-----------|-----------------|--------------------------|
| Strike Rate | 149.2 | 175.2 | 191.8 | >= 192 | <= 149 |
| Dot Ball % | 22.4% | 28.0% | 32.7% | <= 22% | >= 33% |
| Balls/Dismissal | 9.0 | 11.5 | 14.5 | >= 15 | <= 9 |
| Boundary % | 18.0% | 24.3% | 28.0% | >= 28% | <= 18% |

**Data Validation Examples:**
- ELITE: R Shepherd (SR 288.6, Boundary 50.0%), C Green (Dots 12.8%)
- EXPLOITABLE: HV Patel (SR 67.7, Boundary 0%), Noor Ahmad (SR 59.4, Dots 65.6%)

---

## BOWLER PHASE METRICS

### Powerplay (Overs 1-6) | Sample: 47 bowlers with 100+ balls

| Metric | 25th %ile | Median | 75th %ile | ELITE (Top 25%) | EXPLOITABLE (Bottom 25%) |
|--------|-----------|--------|-----------|-----------------|--------------------------|
| Economy | 8.53 | 8.93 | 9.71 | <= 8.53 | >= 9.71 |
| Dot Ball % | 39.4% | 41.3% | 44.9% | >= 45% | <= 39% |
| Wickets/Ball | 0.034 | 0.042 | 0.049 | >= 0.049 | <= 0.034 |
| Boundary % | 21.6% | 23.6% | 26.4% | <= 21.6% | >= 26.4% |

**Data Validation Examples:**
- ELITE: JJ Bumrah (Eco 6.97, Dots 55.1%, Boundary 16.7%), JR Hazlewood (W/B 0.071)
- EXPLOITABLE: SN Thakur (Eco 11.29, Dots 28.1%, Boundary 32.0%)

---

### Middle Overs (7-15) | Sample: 71 bowlers with 100+ balls

| Metric | 25th %ile | Median | 75th %ile | ELITE (Top 25%) | EXPLOITABLE (Bottom 25%) |
|--------|-----------|--------|-----------|-----------------|--------------------------|
| Economy | 8.16 | 8.72 | 9.52 | <= 8.16 | >= 9.52 |
| Dot Ball % | 25.6% | 29.1% | 31.4% | >= 31% | <= 26% |
| Wickets/Ball | 0.037 | 0.044 | 0.055 | >= 0.055 | <= 0.037 |
| Boundary % | 14.2% | 16.3% | 19.4% | <= 14.2% | >= 19.4% |

**Data Validation Examples:**
- ELITE: JJ Bumrah (Eco 6.17, Dots 43.9%, Boundary 10.0%), AD Russell (W/B 0.092)
- EXPLOITABLE: R Shepherd (Eco 11.63, Boundary 27.2%), Sandeep Sharma (W/B 0.015)

---

### Death Overs (16-20) | Sample: 46 bowlers with 80+ balls

| Metric | 25th %ile | Median | 75th %ile | ELITE (Top 25%) | EXPLOITABLE (Bottom 25%) |
|--------|-----------|--------|-----------|-----------------|--------------------------|
| Economy | 10.14 | 10.75 | 11.42 | <= 10.14 | >= 11.42 |
| Dot Ball % | 25.9% | 28.6% | 31.9% | >= 32% | <= 26% |
| Wickets/Ball | 0.074 | 0.085 | 0.101 | >= 0.101 | <= 0.074 |
| Boundary % | 21.2% | 23.8% | 25.3% | <= 21.2% | >= 25.3% |

**Data Validation Examples:**
- ELITE: JJ Bumrah (Eco 6.84, Boundary 11.6%), MA Starc (W/B 0.151), Noor Ahmad (Dots 42.5%)
- EXPLOITABLE: Mukesh Kumar (Eco 12.90, Boundary 31.7%), PJ Cummins (W/B 0.049)

---

## PROPOSED PROFILE TAGS

### Batter Tags (Multi-Metric Criteria)

| Tag | Criteria | Example Players |
|-----|----------|-----------------|
| **PP_DOMINATOR** | Elite in 3+ metrics | J Fraser-McGurk |
| **PP_BOOM_OR_BUST** | Elite SR + Boundary BUT Exploitable Dots | PP Shaw (SR 12.7 b/d, high SR when in) |
| **PP_ACCUMULATOR** | Elite Survival + Dots BUT Average SR | RR Pant (72.0 b/d, 55.6% dots) |
| **PP_LIABILITY** | Exploitable in 2+ metrics | T Kohler-Cadmore |
| **MIDDLE_ANCHOR** | Elite Survival + Dots, Average+ SR | SS Iyer (58.8 b/d) |
| **MIDDLE_ACCELERATOR** | Elite SR + Boundary, Average Survival | SA Yadav |
| **MIDDLE_LIABILITY** | Poor SR AND poor Survival | Anuj Rawat |
| **DEATH_FINISHER** | Elite SR + Boundary, Good Survival | R Shepherd, MP Stoinis |
| **DEATH_HITTER** | Elite SR + Boundary, Poor Survival | High-risk power hitters |
| **DEATH_LIABILITY** | Exploitable SR + Boundary | HV Patel (SR 67.7) |

### Bowler Tags (Multi-Metric Criteria)

| Tag | Criteria | Example Players |
|-----|----------|-----------------|
| **PP_STRIKE** | Elite W/B + Good Dots | JR Hazlewood (W/B 0.071) |
| **PP_CONTAINER** | Elite Economy + Dots BUT Average W/B | JJ Bumrah profile |
| **PP_LIABILITY** | Exploitable Economy + Dots | SN Thakur |
| **MIDDLE_STRANGLER** | Elite Dots + Economy | JJ Bumrah, M Prasidh Krishna |
| **MIDDLE_WICKET_TAKER** | Elite W/B, Average Economy | AD Russell (W/B 0.092) |
| **MIDDLE_LIABILITY** | Poor Dots AND Economy | R Shepherd (Eco 11.63) |
| **DEATH_STRIKE** | Elite W/B, Average+ Economy | MA Starc (W/B 0.151, Eco 10.94) |
| **DEATH_CONTAINER** | Elite Economy BUT Low W/B | SP Narine (Eco 7.47) |
| **DEATH_COMPLETE** | Elite in Economy AND W/B | JJ Bumrah |
| **DEATH_LIABILITY** | Exploitable Economy AND low W/B | PJ Cummins at death |

---

## ANDY FLOWER VS DATA COMPARISON

### Where Data Confirms Andy Flower's Thresholds

| Andy's Threshold | Data Finding | Status |
|------------------|--------------|--------|
| PP Batter SR Elite >= 150 | 75th %ile = 155.9 | CONFIRMED |
| PP Dots Exploitable > 40% | 75th %ile = 47.2% | CONFIRMED (even stricter) |
| Death SR Elite >= 170 | Median = 175.2, 75th = 191.8 | CONFIRMED |
| Death Bowler Eco Elite <= 9.0 | 25th %ile = 10.14 | DATA SUGGESTS 10.1 |
| Death W/B Elite >= 0.06 | 75th %ile = 0.101 | CONFIRMED (data stricter) |

### Where Data Refines Andy Flower's Thresholds

| Andy's Original | Data Finding | Proposed Adjustment |
|-----------------|--------------|---------------------|
| PP Bowler Eco Elite <= 7.0 | 25th %ile = 8.53 | Adjust to <= 8.5 |
| Middle Dots Elite >= 50% (bowler) | 75th %ile = 31.4% | Adjust to >= 31% |
| Death Bowler Eco Elite <= 9.0 | Only Bumrah/Narine below 9.0 | Adjust to <= 10.1 |

---

## KEY INSIGHT: User's Examples Validated

### Example 1: Death bowler with 10.5 economy + 0.08 wickets/ball

**Data Context:**
- Economy 10.5 = 49th percentile (exactly median)
- W/B 0.08 = 46th percentile (just below median)

**Verdict:** This is AVERAGE, not elite. But the 0.08 W/B is close to median (0.085), so this bowler is a viable death option - just not a specialist.

**Tag:** Could be `DEATH_BALANCED` rather than elite or liability.

### Example 2: PP batter with 160 SR + 40% dots

**Data Context:**
- SR 160 = 78th percentile (Elite)
- Dots 40% = 38th percentile (Average, close to median 42.9%)

**Verdict:** NOT boom-or-bust. 40% dots is actually average for PP. This batter is simply ELITE with normal dot rate.

**Revised Tag:** `PP_DOMINATOR` if other metrics strong, or `PP_AGGRESSIVE` if survival is average.

---

## SIGN-OFF

This document provides data-validated thresholds for all phase tags. Thresholds are based on:
- **25th percentile** = Elite threshold (top 25%)
- **75th percentile** = Exploitable threshold (bottom 25%)
- **Median** = Average benchmark

All thresholds derived from IPL 2023+ data with minimum sample sizes:
- Batters: 30 balls (PP/Middle), 20 balls (Death) - *Lowered in Sprint 4.0*
- Bowlers: 60 balls (PP/Middle), 50 balls (Death) - *Lowered in Sprint 4.0*

**Note on Empty Tags:** Players with empty phase tags have insufficient phase-specific sample size to meet the minimum threshold. This does NOT indicate neutral performance - it means we lack enough data to make a reliable assessment for that phase.

---

*Generated: 2026-02-01*
*Data Source: cricket_playbook.duckdb (IPL 2023+)*
*Review: Andy Flower (Cricket Domain) + Stephen Curry (Analytics)*
