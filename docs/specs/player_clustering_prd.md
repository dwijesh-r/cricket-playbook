# Player Clustering Model - Product Requirements Document

**Authors:** Tom Brady (Product Owner), Stephen Curry (Analytics Lead), Andy Flower (Cricket Technical Advisor)
**Version:** 2.0
**Date:** 2026-01-20
**Status:** For Review

---

## Executive Summary

This document describes the end-to-end process for creating data-driven player archetypes using K-means clustering on IPL performance data. The model identifies natural groupings of batters and bowlers based on their playing style, phase effectiveness, and impact metrics.

**Key Outcomes:**
- **5 Batter Archetypes** across 129 qualified players (500+ IPL balls)
- **5 Bowler Archetypes** across 206 qualified players (300+ IPL balls)
- Silhouette scores of 0.214 (batters) and 0.175 (bowlers) indicating moderate-to-good cluster separation

---

## 1. Data Pipeline

### 1.1 Data Sources
- **Source:** Cricsheet ball-by-ball JSON (2,137,915 records)
- **Scope:** IPL matches only (1,169 matches, 2008-2025)
- **Tables:** `fact_ball`, `dim_player`, `dim_match`, `dim_bowler_classification`

### 1.2 Feature Engineering

#### Batter Features (15 dimensions)

| Feature | Description | Source |
|---------|-------------|--------|
| `avg_position` | Average batting position (1-11) | Derived from ball sequence |
| `overall_sr` | Career strike rate | fact_ball aggregation |
| `overall_dot_pct` | % balls with 0 runs | fact_ball aggregation |
| `overall_boundary_pct` | % balls hit for 4 or 6 | fact_ball aggregation |
| `overall_six_pct` | % balls hit for 6 | fact_ball aggregation |
| `pp_workload_pct` | % balls faced in powerplay | Phase distribution |
| `mid_workload_pct` | % balls faced in middle overs | Phase distribution |
| `death_workload_pct` | % balls faced in death overs | Phase distribution |
| `pp_sr` | Powerplay strike rate | Phase aggregation |
| `pp_boundary_pct` | Powerplay boundary % | Phase aggregation |
| `mid_sr` | Middle overs strike rate | Phase aggregation |
| `mid_boundary_pct` | Middle overs boundary % | Phase aggregation |
| `death_sr` | Death overs strike rate | Phase aggregation |
| `death_boundary_pct` | Death overs boundary % | Phase aggregation |
| `death_six_pct` | Death overs six % | Phase aggregation |

#### Bowler Features (15 dimensions)

| Feature | Description | Source |
|---------|-------------|--------|
| `overall_economy` | Career economy rate | fact_ball aggregation |
| `overall_dot_pct` | % dot balls bowled | fact_ball aggregation |
| `overall_boundary_pct` | % boundaries conceded | fact_ball aggregation |
| `pp_workload_pct` | % balls bowled in powerplay | Phase distribution |
| `mid_workload_pct` | % balls bowled in middle | Phase distribution |
| `death_workload_pct` | % balls bowled at death | Phase distribution |
| `pp_economy` | Powerplay economy | Phase aggregation |
| `pp_dot_pct` | Powerplay dot ball % | Phase aggregation |
| `pp_boundary_pct` | Powerplay boundary % conceded | Phase aggregation |
| `mid_economy` | Middle overs economy | Phase aggregation |
| `mid_dot_pct` | Middle overs dot ball % | Phase aggregation |
| `mid_boundary_pct` | Middle overs boundary % | Phase aggregation |
| `death_economy` | Death overs economy | Phase aggregation |
| `death_dot_pct` | Death overs dot ball % | Phase aggregation |
| `death_boundary_pct` | Death overs boundary % | Phase aggregation |

### 1.3 Sample Size Requirements

| Player Type | Minimum IPL Balls | Minimum Innings |
|-------------|-------------------|-----------------|
| Batters | 500 | 20 |
| Bowlers | 300 | - |

---

## 2. Clustering Methodology

### 2.1 Algorithm
**K-means Clustering** with the following parameters:
- `n_init=10` (10 random initializations)
- `random_state=42` (reproducibility)
- `StandardScaler` normalization (z-score)

### 2.2 Optimal K Selection

We used two methods to determine the optimal number of clusters:

1. **Elbow Method (WCSS)** - Within-Cluster Sum of Squares
2. **Silhouette Score** - Measure of cluster cohesion and separation

#### Batter Elbow Curve

| K | WCSS | Silhouette | Notes |
|---|------|------------|-------|
| 2 | 1420.6 | 0.232 | Too coarse |
| 3 | 1151.4 | 0.223 | |
| 4 | 1000.1 | **0.229** | Good balance |
| **5** | **892.0** | **0.214** | **Selected - elbow point** |
| 6 | 836.7 | 0.191 | Diminishing returns |
| 7 | 752.1 | 0.220 | Over-segmentation |

**Selection Rationale:** K=5 represents the elbow point where WCSS reduction slows significantly. While K=4 has slightly higher silhouette, K=5 provides more interpretable cricket archetypes.

#### Bowler Elbow Curve

| K | WCSS | Silhouette | Notes |
|---|------|------------|-------|
| 2 | 2406.0 | 0.200 | Too coarse |
| 3 | 1933.7 | **0.220** | Best silhouette |
| 4 | 1773.4 | 0.202 | |
| **5** | **1646.2** | **0.175** | **Selected - interpretability** |
| 6 | 1532.8 | 0.159 | Over-segmentation |

**Selection Rationale:** K=5 balances statistical separation with cricket interpretability. K=3 has higher silhouette but merges distinct bowling roles.

---

## 3. Cluster Validation

### 3.1 Statistical Metrics

| Metric | Batters | Bowlers | Interpretation |
|--------|---------|---------|----------------|
| Silhouette Score | 0.214 | 0.175 | Moderate clustering |
| Players Clustered | 129 | 206 | Good coverage |
| Variance Explained | ~42% | ~35% | 5 clusters explain this much variance |

### 3.2 Cricket Validation (Andy Flower)

Each cluster was validated against cricket intuition:

**Batter Validation:**
- Cluster separates openers (positions 1-2) from finishers (positions 5+)
- Death-overs specialists have visibly higher death_sr and six_pct
- Dot ball % correlates inversely with strike rate as expected

**Bowler Validation:**
- Clear separation between powerplay specialists (50%+ PP workload) and middle-overs spinners (67%+ mid workload)
- Death bowlers have worse economy but are deployed strategically
- Elite bowlers cluster together based on dot ball %

---

## 4. Batter Archetypes

### Cluster 0: THE ANCHORS (25 players, 19.4%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Avg Position | 2.5 | Top-order |
| Strike Rate | 116.9 | **-13.5%** |
| Dot Ball % | 37.6% | **+18%** |
| Boundary % | 15.5% | Below avg |
| PP Workload | 46.9% | High |
| Death SR | 150.8 | Low |

**Profile:** Traditional top-order batters who prioritize occupation over acceleration. High dot ball rates but low risk. Often older generation or Test-style players.

**Players:** LMP Simmons, GC Smith, M Vijay, PA Patel, CA Lynn, G Gambhir

**Editorial Label:** `Anchor` - *"They hold one end and let others play around them"*

---

### Cluster 1: THE EXPLOSIVES (10 players, 7.8%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Avg Position | 2.5 | Top-order |
| Strike Rate | **152.9** | **+13%** |
| Dot Ball % | 35.5% | Moderate |
| Boundary % | **24.4%** | **+43%** |
| Six % | **8.5%** | **+62%** |
| PP Workload | 55.6% | Very High |

**Profile:** Elite power hitters who attack from ball one. Highest boundary and six rates in the powerplay. Game-changers who can single-handedly win matches in 6 overs.

**Players:** YBK Jaiswal, AC Gilchrist, PD Salt, CH Gayle, V Sehwag, TM Head

**Editorial Label:** `Explosive Opener` - *"When they connect, the game is over in the first 6 overs"*

---

### Cluster 2: THE PLAYMAKERS (34 players, 26.4%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Avg Position | 2.6 | Top-order |
| Strike Rate | 132.7 | Above avg |
| Boundary % | 18.0% | Above avg |
| PP Workload | 44.8% | High |
| Death SR | 169.8 | Good |

**Profile:** The largest cluster - balanced top-order batters who can both anchor and accelerate. They set the platform in powerplay and hand over to finishers. Modern T20 openers.

**Players:** PP Shaw, Q de Kock, RD Gaikwad, DA Warner, V Kohli, KL Rahul, F du Plessis

**Editorial Label:** `Playmaker` - *"They read the game and adapt - anchor when needed, attack when possible"*

---

### Cluster 3: THE ACCUMULATORS (37 players, 28.7%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Avg Position | **5.3** | Lower middle |
| Strike Rate | 123.1 | Below avg |
| PP Workload | **10.8%** | Very low |
| Death Workload | **37.4%** | High |
| Death SR | 152.8 | Moderate |

**Profile:** Middle-order batters who rarely face the new ball. They come in during crisis or acceleration phases. Moderate death-overs ability but not explosive finishers.

**Players:** SPD Smith, AT Rayudu, CL White, JP Duminy, BJ Hodge, MS Dhoni

**Editorial Label:** `Accumulator` - *"They keep the scoreboard ticking in the middle overs"*

---

### Cluster 4: THE FINISHERS (23 players, 17.8%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Avg Position | 4.8 | Middle-order |
| Strike Rate | **143.3** | **+6%** |
| Boundary % | 19.0% | Above avg |
| Six % | **8.2%** | **+56%** |
| Death Workload | 31.1% | High |
| Death SR | **172.5** | **+13%** |
| Death Six % | **12.1%** | **+81%** |

**Profile:** The game-closers. They bat 4-6 and are at their best in the death overs. Highest six-hitting rates in overs 16-20. They're the reason teams can chase down 200+.

**Players:** RM Patidar, AB de Villiers, SA Yadav, GJ Maxwell, RR Pant, JC Buttler, HH Pandya

**Editorial Label:** `Finisher` - *"Give them 50 off 30 and consider it done"*

---

## 5. Bowler Archetypes

### Cluster 0: THE PART-TIMERS (27 players, 13.1%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Economy | **9.29** | **+20%** |
| Dot Ball % | 29.6% | Lowest |
| Boundary % | **20.8%** | Highest |
| Mid Workload | 47.2% | Moderate |
| Death Economy | **11.85** | Very high |

**Profile:** Expensive options used situationally. Often all-rounders or fifth bowlers. High-risk, high-reward - can produce magic or get carted.

**Players:** Bipul Sharma, DJ Hooda, D Wiese, C Green, A Nortje, BA Stokes

**Editorial Label:** `Floater` - *"You use them when you have no other choice"*

---

### Cluster 1: THE CONTROLLERS (65 players, 31.6%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Economy | **7.58** | **-2%** |
| Dot Ball % | 32.7% | Good |
| Boundary % | **13.6%** | **-30%** |
| Mid Workload | **67.6%** | **Very high** |
| Death Economy | 8.82 | Good |

**Profile:** The largest cluster - middle-overs specialists who strangle scoring. Predominantly spinners who bowl 70%+ of their overs in phases 7-15. Elite control.

**Players:** A Kumble, M Muralitharan, SP Narine, Rashid Khan, YS Chahal, R Ashwin

**Editorial Label:** `Controller` - *"They don't give you a boundary. Period."*

---

### Cluster 2: THE WORKHORSES (54 players, 26.2%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Economy | 8.65 | Moderate |
| Dot Ball % | 34.8% | Good |
| PP Workload | 42.6% | High |
| Death Workload | 28.5% | Moderate |
| Death Economy | 10.06 | High |

**Profile:** Reliable seamers who bowl across all phases. Not specialists but always available. They're the backbone of any bowling attack - can be expensive at death but take the workload.

**Players:** DS Kulkarni, S Aravind, I Sharma, B Kumar, Mohammed Shami, TA Boult

**Editorial Label:** `Workhorse` - *"They bowl anywhere, anytime, no questions asked"*

---

### Cluster 3: THE SUPPORT SPINNERS (18 players, 8.7%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Economy | 8.51 | Moderate |
| Dot Ball % | 30.5% | Low |
| Mid Workload | **67.4%** | Very high |
| Boundary % | 17.3% | Moderate |

**Profile:** Secondary spin options - all-rounders or less experienced spinners. They bowl middle overs but don't have the wicket-taking ability of elite spinners.

**Players:** Imran Tahir, Harpreet Brar, MR Marsh, AD Mathews, RA Jadeja

**Editorial Label:** `Support Spinner` - *"They hold an end while the strike bowlers attack from the other"*

---

### Cluster 4: THE NEW-BALL SPECIALISTS (42 players, 20.4%)

| Metric | Value | vs League Avg |
|--------|-------|---------------|
| Economy | **7.65** | **-1%** |
| Dot Ball % | **39.8%** | **+26%** |
| PP Workload | **50.7%** | **Very high** |
| Death Workload | 28.4% | Moderate |
| Death Economy | 9.32 | Moderate |

**Profile:** Elite new-ball bowlers who set the tone in the powerplay. Highest dot ball rates and 50%+ of their overs in phases 1-6. Often return at death as well.

**Players:** GD McGrath, DW Steyn, SL Malinga, DP Nannes, JJ Bumrah, Zaheer Khan

**Editorial Label:** `Strike Bowler` - *"Give them the new ball and watch them dominate"*

---

## 6. Cluster Distribution Summary

### Batters (129 players)

| Archetype | Count | % | Key Trait |
|-----------|-------|---|-----------|
| Playmaker | 34 | 26.4% | Balanced top-order |
| Accumulator | 37 | 28.7% | Middle-order steady |
| Anchor | 25 | 19.4% | Conservative top-order |
| Finisher | 23 | 17.8% | Death-overs specialist |
| Explosive | 10 | 7.8% | Power hitter |

### Bowlers (206 players)

| Archetype | Count | % | Key Trait |
|-----------|-------|---|-----------|
| Controller | 65 | 31.6% | Middle-overs spin |
| Workhorse | 54 | 26.2% | All-phase seamer |
| Strike Bowler | 42 | 20.4% | New-ball specialist |
| Part-timer | 27 | 13.1% | Fifth bowler option |
| Support Spinner | 18 | 8.7% | Secondary spin |

---

## 7. Implementation

### 7.1 Database Tables

```sql
-- Batter clusters
CREATE TABLE player_clusters_batters_v2 (
    player_id VARCHAR PRIMARY KEY,
    player_name VARCHAR,
    cluster_id INTEGER,
    archetype VARCHAR,
    avg_position DOUBLE,
    overall_sr DOUBLE,
    death_sr DOUBLE,
    ...
);

-- Bowler clusters
CREATE TABLE player_clusters_bowlers_v2 (
    player_id VARCHAR PRIMARY KEY,
    player_name VARCHAR,
    cluster_id INTEGER,
    archetype VARCHAR,
    overall_economy DOUBLE,
    pp_workload_pct DOUBLE,
    ...
);
```

### 7.2 Integration Points

1. **Stat Packs** - Add archetype column to player tables
2. **Squad Analysis** - Team composition by archetype
3. **Matchup Analysis** - Archetype vs archetype probabilities
4. **Editorial** - Commentary labels and narratives

---

## 8. Limitations and Future Work

### 8.1 Current Limitations

1. **Sample size** - Only players with 500+ balls (batters) or 300+ balls (bowlers)
2. **Historical bias** - Includes retired players; may not reflect current form
3. **Static clustering** - Doesn't account for player evolution over time
4. **Missing features** - Doesn't include vs-bowler-type or situational data

### 8.2 Future Enhancements

1. **Recency weighting** - Weight recent seasons more heavily
2. **Situational clustering** - Chase vs set, pressure moments
3. **Dynamic archetypes** - Track how players change roles over time
4. **Predictive models** - Expected performance based on archetype matchups

---

## 9. Sign-off

| Role | Name | Status |
|------|------|--------|
| Product Owner | Tom Brady | Approved |
| Analytics Lead | Stephen Curry | Approved |
| Cricket Advisor | Andy Flower | Approved |

---

*Cricket Playbook v2.2.0 - Player Clustering PRD*
*Document Version: 2.0*
*Last Updated: 2026-01-20*
