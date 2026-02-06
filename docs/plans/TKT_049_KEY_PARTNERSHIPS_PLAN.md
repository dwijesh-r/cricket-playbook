# TKT-049: Key Partnerships Analysis - Implementation Plan

**Ticket:** TKT-049
**Status:** RUNNING (40%) - Paused for Founder Approval
**Author:** Stephen Curry (Analytics Lead)
**Date:** 2026-02-06
**Version:** 1.0

---

## Executive Summary

This document outlines the implementation plan for adding a **Key Partnerships** section to IPL 2026 stat packs. The feature will identify and analyze batting partnerships that significantly contributed to team performance, providing actionable insights for cricket strategists.

**Pending:** Founder approval before implementation continues.

---

## 1. What is Key Partnerships Analysis?

### 1.1 Definition

A **batting partnership** is the period during an innings when two specific batters are at the crease together. A partnership begins when a batter comes to the crease and ends when either batter is dismissed, retires, or the innings concludes.

A **key partnership** is one that meets specific threshold criteria indicating significant impact on the match outcome. Key partnerships typically:
- Stabilize an innings after early wickets
- Accelerate scoring during middle/death overs
- Build match-winning totals
- Rescue teams from precarious positions

### 1.2 Core Metrics

| Metric | Description | Calculation |
|--------|-------------|-------------|
| **Partnership Runs** | Total runs scored during the partnership | SUM(total_runs) while both batters at crease |
| **Partnership Balls** | Legal deliveries faced during partnership | COUNT(is_legal_ball) while both batters at crease |
| **Partnership Run Rate** | Scoring rate during partnership | (Partnership Runs / Partnership Balls) * 6 |
| **Partnership Strike Rate** | Batting strike rate | (Partnership Runs / Partnership Balls) * 100 |
| **Contribution Split** | % runs scored by each batter | (Batter1 Runs / Partnership Runs) * 100 |
| **Boundary %** | Proportion of runs from boundaries | (4s + 6s runs) / Partnership Runs * 100 |
| **Dot Ball %** | Proportion of dots faced | Dot Balls / Partnership Balls * 100 |

### 1.3 Derived Insights

- **Frequency:** How often a batter pair bats together
- **Average Partnership:** Mean runs when batting together
- **Peak Partnership:** Highest partnership between the pair
- **Phase Distribution:** Partnership performance by phase (PP/middle/death)
- **Situational Performance:** Performance at different entry points (e.g., after early wickets)

---

## 2. Data Sources

### 2.1 Available Data (DuckDB)

We have complete ball-by-ball data in `fact_ball` with the following relevant fields:

| Field | Description | Usage |
|-------|-------------|-------|
| `match_id` | Match identifier | Group by match |
| `innings` | Innings number (1/2) | Filter by innings |
| `batter_id` | On-strike batter | Partner 1 |
| `non_striker_id` | Non-strike batter | Partner 2 |
| `batting_team_id` | Batting team | Filter by team |
| `total_runs` | Runs scored on delivery | Sum for partnership |
| `batter_runs` | Runs credited to batter | Attribution |
| `is_legal_ball` | Valid delivery flag | Ball count |
| `is_wicket` | Wicket fell | Partnership end trigger |
| `player_out_id` | Dismissed player | Identify which partner out |
| `match_phase` | powerplay/middle/death | Phase analysis |

**Supporting Tables:**
- `dim_player`: Player names and IDs
- `dim_match`: Match metadata (date, season, venue)
- `dim_team`: Team names
- `ipl_2026_squads`: Current squad rosters

### 2.2 Data We Need to Calculate

Partnership data is not pre-aggregated, so we must derive it from ball-by-ball records:

1. **Partnership Identification**
   - Group consecutive balls by unique (batter_id, non_striker_id) pair
   - Handle striker rotation (A-B same as B-A)
   - Detect partnership boundaries (wickets, innings end)

2. **Partnership Aggregation**
   - Sum runs, count balls within each partnership
   - Track contribution by each batter
   - Calculate run rate and other metrics

3. **Squad Filtering**
   - Filter to partnerships involving current IPL 2026 squad players
   - Cross-reference with `ipl_2026_squads` table

---

## 3. Methodology

### 3.1 Identifying Key Partnerships

**Threshold Criteria (Proposed):**

| Threshold | Value | Rationale |
|-----------|-------|-----------|
| **Minimum Runs** | 30+ runs | ~2 overs of good batting, meaningful contribution |
| **OR Minimum Run Rate** | 10+ RPO (for 15+ run partnerships) | High-impact acceleration |
| **OR Situational** | 25+ runs after 2+ wickets down in PP | Rescue partnership |

**Key Partnership Tiers:**

| Tier | Criteria | Label |
|------|----------|-------|
| **Elite** | 75+ runs | "Match-defining" |
| **Major** | 50-74 runs | "Significant" |
| **Useful** | 30-49 runs | "Key contribution" |
| **Accelerator** | 20-29 runs at 12+ RPO | "Impact partnership" |

### 3.2 Partnership Effectiveness Metrics

**Partnership Quality Index (PQI):**
```
PQI = (Partnership Runs * Run Rate) / League Average Partnership Score
```

Where League Average Partnership Score accounts for:
- Average partnership runs in IPL (2023-2025)
- Phase-adjusted expectations (PP: ~8.5 RPO, Middle: ~8.0 RPO, Death: ~10.5 RPO)

**Phase-Adjusted Rating:**
- Powerplay partnerships: Higher value for boundary %
- Middle overs: Higher value for rotation (lower dot %)
- Death overs: Higher value for strike rate

### 3.3 "Key" vs "Ordinary" Partnership

| Attribute | Key Partnership | Ordinary Partnership |
|-----------|-----------------|---------------------|
| Runs | 30+ (or 20+ with 12+ RPO) | < 30 runs, sub-10 RPO |
| Context | Builds innings or accelerates | Maintains without impact |
| Frequency | Notable (top 10-15% by runs) | Routine |
| Match Impact | Often correlates with wins | Minimal correlation |

**Example Thresholds from IPL 2023-2025 Data:**
- Top 10% partnerships: 35+ runs
- Top 5% partnerships: 50+ runs
- Top 1% partnerships: 80+ runs

---

## 4. Output Format

### 4.1 Stat Pack Section Structure

The Key Partnerships section will be added as **Section 11** in each team's stat pack, following Andy Flower's Tactical Insights.

```markdown
---

## 11. Key Partnerships

*Batting partnerships of 30+ runs involving current squad players (IPL 2023-2025)*

### 11.1 Top Partnership Combinations

| Partners | Innings | Avg Runs | Best | Avg RR | Avg Balls |
|----------|---------|----------|------|--------|-----------|
| Player A & Player B | 12 | 45.3 | 87 | 9.2 | 29.5 |
| Player C & Player D | 8 | 38.7 | 62 | 8.8 | 26.4 |
...

### 11.2 Phase-wise Partnership Analysis

| Phase | Top Pair | Avg Runs | Avg RR | Key Insight |
|-------|----------|----------|--------|-------------|
| Powerplay | A & B | 42.1 | 8.5 | Aggressive openers |
| Middle | C & D | 38.4 | 7.9 | Consolidation pair |
| Death | E & F | 35.2 | 11.8 | Finisher combo |

### 11.3 Notable Partnerships (2023-2025)

**Match-Defining (75+ runs):**
- **Player A & Player B**: 92 off 54 balls (10.2 RPO) vs MI, IPL 2024
- **Player C & Player D**: 87 off 48 balls (10.9 RPO) vs RCB, IPL 2025

**Rescue Partnerships (25+ after 2-down in PP):**
- **Player E & Player F**: 48 off 38 balls after 8/2 vs SRH, IPL 2024

---
```

### 4.2 Example Output: Chennai Super Kings

```markdown
## 11. Key Partnerships

*Batting partnerships of 30+ runs involving current squad players (IPL 2023-2025)*

### 11.1 Top Partnership Combinations

| Partners | Innings | Avg Runs | Best | Avg RR | Avg Balls |
|----------|---------|----------|------|--------|-----------|
| RD Gaikwad & S Dube | 15 | 52.3 | 87 | 8.9 | 35.2 |
| SV Samson & RD Gaikwad | 8 | 41.5 | 68 | 9.1 | 27.4 |
| MS Dhoni & S Dube | 12 | 38.7 | 54 | 10.8 | 21.5 |
| D Brevis & MS Dhoni | 4 | 35.2 | 48 | 11.2 | 18.8 |

### 11.2 Phase-wise Partnership Analysis

| Phase | Top Pair | Avg Runs | Avg RR | Key Insight |
|-------|----------|----------|--------|-------------|
| Powerplay | Gaikwad & Samson | 38.4 | 8.2 | Steady accumulation |
| Middle | Gaikwad & Dube | 45.1 | 8.6 | Key consolidation |
| Death | Dhoni & Dube | 42.3 | 11.4 | Finisher synergy |

### 11.3 Notable Partnerships (2023-2025)

**Match-Defining (75+ runs):**
- **RD Gaikwad & S Dube**: 87 off 52 balls (10.0 RPO) vs MI, IPL 2024

**Key Death Overs (30+ at 10+ RPO):**
- **MS Dhoni & S Dube**: 54 off 30 balls (10.8 RPO) vs KKR, IPL 2023

---
```

---

## 5. Implementation Steps

### 5.1 Phase 1: Analytics View Creation (Est: 2 hours)

**Step 1.1:** Create partnership identification query
```sql
-- Create view: analytics_ipl_partnerships_raw
-- Groups consecutive balls by (batter_id, non_striker_id) pair
-- Handles striker rotation (normalizes pair order)
-- Calculates partnership boundaries
```

**Step 1.2:** Create aggregated partnership view
```sql
-- Create view: analytics_ipl_partnerships
-- Aggregates partnership metrics
-- Joins with player names and team info
-- Adds sample_size classification
```

**Step 1.3:** Create squad-filtered partnership view
```sql
-- Create view: analytics_ipl_squad_partnerships
-- Filters to current IPL 2026 squad members
-- Adds phase breakdown
-- Calculates partnership quality metrics
```

**Deliverable:** Three new views in `scripts/core/analytics_ipl.py`

### 5.2 Phase 2: Stat Pack Generator Update (Est: 1.5 hours)

**Step 2.1:** Add `generate_key_partnerships()` function
- Query partnership views for team
- Format top combinations table
- Generate phase-wise analysis
- Identify notable partnerships

**Step 2.2:** Integrate into `generate_team_stat_pack()`
- Add Section 11 call after Section 10
- Update section numbering if needed

**Deliverable:** Updated `scripts/generators/generate_stat_packs.py`

### 5.3 Phase 3: Validation & Testing (Est: 1 hour)

**Step 3.1:** Manual validation
- Verify partnership counts against known matches
- Cross-check run totals
- Validate phase classifications

**Step 3.2:** Regenerate all stat packs
- Run full generation pipeline
- Review output for all 10 teams

**Step 3.3:** Sample comparison
- Compare 2-3 notable partnerships against Cricinfo/ESPNcricinfo
- Document any discrepancies

**Deliverable:** Validated stat packs with Key Partnerships section

### 5.4 Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| DuckDB database | Available | `data/cricket_playbook.duckdb` |
| IPL 2026 squads | Available | `ipl_2026_squads` table |
| Ball-by-ball data | Available | `fact_ball` with `non_striker_id` |
| Stat pack generator | Available | `generate_stat_packs.py` |

### 5.5 Estimated Effort

| Phase | Task | Hours |
|-------|------|-------|
| 1 | Analytics views | 2.0 |
| 2 | Generator update | 1.5 |
| 3 | Validation | 1.0 |
| **Total** | | **4.5 hours** |

---

## 6. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Partnership identification edge cases (retired hurt, substitutes) | Minor data gaps | Document limitations, exclude edge cases |
| Large output volume (many partnerships) | Cluttered stat packs | Apply 30+ run threshold, limit to top N |
| Performance impact on generation | Slower generation | Optimize queries, add indexes if needed |
| Squad players with limited IPL history | Missing partnerships | Show available data, note sample size |

---

## 7. Success Criteria

1. **Accuracy:** Partnership totals match manual verification within 1%
2. **Coverage:** All 10 team stat packs include Key Partnerships section
3. **Usefulness:** Section provides actionable batting order insights
4. **Performance:** Stat pack generation completes in < 60 seconds

---

## 8. Open Questions for Founder

1. **Threshold:** Is 30+ runs the right minimum, or should we use 25+?
2. **Historical Range:** Should we include all IPL history or limit to 2023-2025?
3. **Notable Partnerships:** How many "notable" examples to show per team (currently 3-5)?
4. **Phase Priority:** Should we weight any phase higher (e.g., death overs)?

---

## Approval

| Role | Name | Status |
|------|------|--------|
| Analytics Lead | Stephen Curry | Proposed |
| Product Owner | Tom Brady | Pending |
| Domain Expert | Andy Flower | Pending |
| **Founder** | | **AWAITING APPROVAL** |

---

*Plan Version: 1.0 | Created: 2026-02-06*
