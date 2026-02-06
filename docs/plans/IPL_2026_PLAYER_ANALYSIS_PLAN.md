# IPL 2026 Player Analysis Plan

**Author:** Stephen Curry (Analytics Lead)
**Date:** 2026-02-06
**Version:** 1.0
**Status:** PENDING FOUNDER APPROVAL

---

## Executive Summary

This plan consolidates and expands upon the preliminary work outlined in `~/.claude/plans/misty-honking-clarke.md` to create a comprehensive IPL 2026 Player Analysis framework. The goal is to deliver actionable, data-driven insights for all 10 IPL 2026 squads with phase-wise breakdowns, bowler matchups, and advanced metrics.

**This document requires Founder approval before implementation begins.**

---

## 1. Overview

### 1.1 What is IPL 2026 Player Analysis?

The IPL 2026 Player Analysis is a comprehensive analytics initiative that:

1. **Connects Historical Performance to 2026 Squads**: Links player career statistics (IPL and All T20) to current team rosters
2. **Provides Phase-Wise Breakdowns**: Analyzes performance across powerplay (1-6), middle (7-15), and death (16-20) overs
3. **Enables Matchup Intelligence**: Batter vs bowler type matchups, bowler vs batting handedness matchups
4. **Generates Strategic Outputs**: Stat packs, depth charts, and predicted XIs for each franchise

### 1.2 Why Do We Need It?

| Reason | Description |
|--------|-------------|
| **New Season Preparation** | IPL 2026 starts soon; teams need current insights |
| **Squad Changes** | Mega auction completed; significant squad turnover across franchises |
| **Retention/Trade Updates** | Players like Sanju Samson (CSK), Ravindra Jadeja (RR) moved between teams |
| **New Player Acquisitions** | Auction brought in new talents requiring baseline analysis |
| **Overseas Player Updates** | International T20 data needs integration for overseas signings |
| **Competitive Intelligence** | Coaches, analysts, and fans need structured, actionable data |

### 1.3 Current State Assessment

| Component | Status | Location |
|-----------|--------|----------|
| 2026 Squad Data | COMPLETE | `data/ipl_2026_squads.csv` (all 10 teams, ~200+ players) |
| 2026 Contract Data | COMPLETE | `data/ipl_2026_player_contracts.csv` |
| Bowler Classifications | COMPLETE | `data/bowler_classifications_v3.csv` |
| DuckDB Database | COMPLETE | `data/cricket_playbook.duckdb` |
| Stat Pack Generator | COMPLETE | `scripts/generators/generate_stat_packs.py` |
| Depth Chart Generator | COMPLETE | `scripts/generators/generate_depth_charts.py` |
| Predicted XII Generator | COMPLETE | `scripts/generators/generate_predicted_xii.py` |

---

## 2. Data Collection Phase

### 2.1 Data Already Available

#### 2.1.1 IPL 2026 Squad Data (`data/ipl_2026_squads.csv`)

| Field | Description | Status |
|-------|-------------|--------|
| `team_name` | Franchise name | Complete |
| `player_name` | Player full name | Complete |
| `player_id` | Cricsheet ID | Complete |
| `nationality` | Country code | Complete |
| `age` | Player age | Complete |
| `role` | Batter/Bowler/All-rounder/Wicketkeeper | Complete |
| `bowling_arm` | Right-arm/Left-arm | Complete |
| `bowling_type` | Fast/Medium/Off-spin/Leg-spin/Left-arm orthodox/Left-arm wrist spin | Complete |
| `batting_hand` | Right-hand/Left-hand | Complete |
| `batter_classification` | K-means cluster archetype | Complete |
| `bowler_classification` | K-means cluster archetype | Complete |
| `batter_tags` | Performance tags | Complete |
| `bowler_tags` | Performance tags | Complete |
| `is_captain` | Captain flag | Complete |

**Teams Covered:** CSK, MI, RCB, KKR, DC, PBKS, RR, SRH, GT, LSG (all 10)

#### 2.1.2 Contract Data (`data/ipl_2026_player_contracts.csv`)

| Field | Description | Status |
|-------|-------------|--------|
| `team_name` | Franchise | Complete |
| `player_name` | Player name | Complete |
| `price_cr` | Contract value in crores | Complete |
| `acquisition_type` | Retained/Traded/Auction | Complete |
| `year_joined` | First year with current franchise | Complete |

#### 2.1.3 DuckDB Analytics Views (Existing)

| View | Description | IPL Filter |
|------|-------------|------------|
| `analytics_batting_career` | Career batting stats | All T20 |
| `analytics_bowling_career` | Career bowling stats | All T20 |
| `analytics_batting_by_phase` | Phase-wise batting | All T20 |
| `analytics_bowling_by_phase` | Phase-wise bowling | All T20 |
| `analytics_batter_vs_bowler_type` | Batter vs spin/pace | All T20 |
| `analytics_bowler_vs_batting_hand` | Bowler vs LHB/RHB | All T20 |

### 2.2 Additional Data Needed

| Data Gap | Description | Priority | Owner |
|----------|-------------|----------|-------|
| **IPL-Filtered Views** | Separate views for IPL-only data | HIGH | Stephen Curry |
| **2025-26 Overseas Data** | Recent international T20 stats for overseas players | MEDIUM | Andy Flower |
| **Venue-Specific Stats** | Home ground performance by player | MEDIUM | Stephen Curry |
| **Recent Form Data** | Last 10/20 match rolling averages | HIGH | Stephen Curry |
| **Partnership Data** | Key batting partnerships (TKT-049 in progress) | MEDIUM | Stephen Curry |

### 2.3 Data Validation Checklist

| Check | Description | Status |
|-------|-------------|--------|
| All 10 teams in squad CSV | Verify team count | Needs verification |
| Player IDs match DuckDB | Join validation | Needs verification |
| Bowling classifications complete | No null values | Needs verification |
| Contract data aligned | Squad/contract match | Needs verification |

---

## 3. Analytics Views Needed

### 3.1 IPL-Specific Base Views (NEW)

These views filter existing analytics to IPL data only:

| View Name | Description | Base View |
|-----------|-------------|-----------|
| `analytics_ipl_batting_career` | IPL career batting stats | `analytics_batting_career` |
| `analytics_ipl_bowling_career` | IPL career bowling stats | `analytics_bowling_career` |
| `analytics_ipl_batting_by_phase` | IPL phase-wise batting | `analytics_batting_by_phase` |
| `analytics_ipl_bowling_by_phase` | IPL phase-wise bowling | `analytics_bowling_by_phase` |

### 3.2 Batter Analytics Views

| View Name | Description | Key Metrics |
|-----------|-------------|-------------|
| `analytics_ipl_batter_phase` | Phase breakdown for batters | SR, avg, runs, balls by PP/middle/death |
| `analytics_ipl_batter_vs_bowler_type` | Batter vs bowling type | Performance vs fast/medium/spin |
| `analytics_ipl_batter_vs_bowler` | Head-to-head matchups | Direct batter vs bowler stats |
| `analytics_ipl_batter_recent_form` | Last 10/20 IPL matches | Rolling averages and form indicators |

**Key Metrics per View:**
- Runs, Balls, Dismissals
- Strike Rate, Average
- Dot Ball % = (Dots / Balls) * 100
- Boundary % = ((4s + 6s) / Balls) * 100
- Scoring zones (% runs by area)

### 3.3 Bowler Analytics Views

| View Name | Description | Key Metrics |
|-----------|-------------|-------------|
| `analytics_ipl_bowler_phase` | Phase breakdown for bowlers | Econ, wickets, SR by PP/middle/death |
| `analytics_ipl_bowler_vs_batting_hand` | Bowler vs LHB/RHB | Wickets, economy by hand |
| `analytics_ipl_bowler_vs_batter_type` | Bowler vs batter archetype | Performance vs aggressive/anchor types |
| `analytics_ipl_bowler_recent_form` | Last 10/20 IPL matches | Rolling averages and form indicators |

**Key Metrics per View:**
- Overs, Runs Conceded, Wickets
- Economy Rate, Strike Rate
- Dot Ball % = (Dots / Balls) * 100
- Boundary Conceded % = (Boundaries / Balls) * 100
- Average (Runs / Wickets)

### 3.4 All T20 Comparison Views

Mirror IPL views for all T20 competitions:

| IPL View | All T20 Equivalent |
|----------|-------------------|
| `analytics_ipl_batter_phase` | `analytics_t20_batter_phase` |
| `analytics_ipl_batter_vs_bowler_type` | `analytics_t20_batter_vs_bowler_type` |
| `analytics_ipl_bowler_phase` | `analytics_t20_bowler_phase` |
| `analytics_ipl_bowler_vs_batting_hand` | `analytics_t20_bowler_vs_batting_hand` |

**Purpose:** Compare IPL-specific performance vs global T20 baseline.

### 3.5 Squad-Integrated Views (NEW)

| View Name | Description |
|-----------|-------------|
| `analytics_ipl_squad_batting_2026` | IPL batting stats for all 2026 squad members |
| `analytics_ipl_squad_bowling_2026` | IPL bowling stats for all 2026 squad members |
| `analytics_ipl_squad_phase_2026` | Phase-wise breakdown for 2026 squads |
| `analytics_ipl_team_matchups_2026` | Team-level matchup aggregations |

---

## 4. Squad Integration

### 4.1 Connecting Historical Performance to 2026 Squads

**Primary Join Strategy:**

```sql
SELECT
    sq.team_name,
    sq.player_name,
    sq.role,
    sq.player_id,
    stats.*
FROM ipl_2026_squads sq
LEFT JOIN analytics_ipl_batting_career stats
    ON sq.player_id = stats.player_id
WHERE sq.role IN ('Batter', 'All-rounder', 'Wicketkeeper');
```

**Key Considerations:**

| Issue | Solution |
|-------|----------|
| Player ID mismatches | Manual mapping table for edge cases |
| Name variations | Fuzzy matching + manual override list |
| Multiple player IDs | Canonical ID mapping |

### 4.2 Handling New Players with Limited IPL Data

#### Category A: Players with <10 IPL Matches

| Approach | Description |
|----------|-------------|
| **All T20 Baseline** | Use `analytics_t20_*` views as primary reference |
| **Domestic Proxy** | Weight List A/domestic T20 data where available |
| **Flag as "Limited Data"** | Mark in outputs for context |
| **Projection Model** | (Future) ML-based projection from non-IPL data |

#### Category B: Players with 0 IPL Matches (Debutants)

| Approach | Description |
|----------|-------------|
| **International T20** | Use national team T20I stats |
| **Franchise League Data** | BBL, PSL, CPL, SA20, ILT20 data |
| **Manual Scouting Notes** | Qualitative input from Andy Flower |
| **"New to IPL" Tag** | Clear labeling in all outputs |

#### Data Availability Matrix:

| Player Type | IPL Data | All T20 Data | Action |
|-------------|----------|--------------|--------|
| IPL Veteran (50+ matches) | Full | Full | Use IPL primary |
| IPL Regular (10-49 matches) | Moderate | Full | Blend IPL + T20 |
| IPL Newcomer (1-9 matches) | Limited | Varies | Weight T20 heavily |
| IPL Debutant (0 matches) | None | Varies | Use T20 only + flag |

### 4.3 Handling Overseas Players

| Challenge | Solution |
|-----------|----------|
| **Different Competition Quality** | Apply competition weighting factor |
| **Limited IPL Exposure** | Prioritize franchise leagues over domestic |
| **Recent Form Overseas** | Include last 12 months international data |
| **Conditions Adjustment** | Note subcontinental vs non-subcontinent splits |

**Overseas Player Data Sources (Priority Order):**

1. IPL historical data (primary)
2. Other Indian franchise leagues (if any)
3. International T20Is
4. Top-tier franchise leagues (BBL, PSL, CPL, SA20, ILT20)
5. County/State T20 leagues

### 4.4 Squad Mapping Validation

Before generating outputs, validate:

```sql
-- Check for unmapped players
SELECT
    sq.player_name,
    sq.player_id,
    CASE WHEN stats.player_id IS NULL THEN 'NO MATCH' ELSE 'OK' END as status
FROM ipl_2026_squads sq
LEFT JOIN analytics_ipl_batting_career stats
    ON sq.player_id = stats.player_id;
```

---

## 5. Outputs to Generate

### 5.1 Updated Stat Packs for 2026 Squads

**Location:** `stat_packs/{TEAM}_stat_pack.md`

**Current Status:** All 10 teams generated (as of 2026-02-06)

**Enhancements for 2026:**

| Section | Current | Enhancement |
|---------|---------|-------------|
| Squad Overview | Basic roster | Add acquisition type, contract value |
| Player Archetypes | K-means V2 | Refresh clusters with 2025 data |
| Phase Performance | Present | Add IPL vs All T20 comparison |
| Matchup Tables | Present | Add bowler type breakdowns |
| Key Partnerships | Missing | Add (pending TKT-049) |
| Recent Form | Missing | Add last 10 match rolling stats |
| New Player Profiles | Missing | Dedicated section for debutants |

### 5.2 Updated Depth Charts for 2026

**Location:** `outputs/depth_charts/{TEAM}_depth_chart.md`

**Current Status:** All 10 teams generated

**Enhancements for 2026:**

| Aspect | Enhancement |
|--------|-------------|
| Player Rankings | Re-sort based on 2025 form + career |
| Role Flexibility | Note players who can cover multiple slots |
| Impact Ratings | Add impact score (IPL + All T20 weighted) |
| Injury Replacements | Suggest like-for-like replacement chains |

### 5.3 Updated Predicted XIIs for 2026

**Location:** `outputs/predicted_xii/{TEAM}_predicted_xii.md`

**Current Status:** All 10 teams generated

**Enhancements for 2026:**

| Feature | Description |
|---------|-------------|
| **Condition-Based XIs** | Home vs Away, Pace-friendly vs Spin-friendly |
| **Opposition-Specific** | Optimal XI vs each opponent |
| **Balance Score** | Batting/bowling/pace/spin balance rating |
| **Flex Positions** | Highlight interchangeable slots |

### 5.4 New Outputs for 2026

| Output | Description | Priority |
|--------|-------------|----------|
| **Matchup Matrices** | Team vs Team batter-bowler grids | HIGH |
| **Phase Specialists Report** | Best PP/middle/death players across IPL | MEDIUM |
| **Form Tracker Dashboard** | Rolling form for all 2026 players | MEDIUM |
| **Debutant Watch Report** | Analysis of all IPL debutants | MEDIUM |
| **Trade Impact Analysis** | Before/after for traded players | LOW |

---

## 6. Implementation Steps

### Phase 1: Data Validation (Days 1-2)

| Step | Description | Owner | Effort |
|------|-------------|-------|--------|
| 1.1 | Verify all 10 teams in `ipl_2026_squads.csv` | Andy Flower | 1 hr |
| 1.2 | Validate player_id join rates with DuckDB | Stephen Curry | 2 hrs |
| 1.3 | Create unmapped player resolution list | Stephen Curry | 2 hrs |
| 1.4 | Verify contract data alignment | Andy Flower | 1 hr |
| 1.5 | Update bowler classifications for new players | Andy Flower | 3 hrs |

**Exit Criteria:** >95% player_id match rate, all missing IDs documented

### Phase 2: IPL-Specific Views (Days 3-5)

| Step | Description | Owner | Effort |
|------|-------------|-------|--------|
| 2.1 | Create `analytics_ipl_batting_career` view | Stephen Curry | 2 hrs |
| 2.2 | Create `analytics_ipl_bowling_career` view | Stephen Curry | 2 hrs |
| 2.3 | Create `analytics_ipl_batter_phase` view | Stephen Curry | 3 hrs |
| 2.4 | Create `analytics_ipl_bowler_phase` view | Stephen Curry | 3 hrs |
| 2.5 | Create matchup views (batter vs type, bowler vs hand) | Stephen Curry | 4 hrs |
| 2.6 | Create recent form views (last 10/20) | Stephen Curry | 3 hrs |
| 2.7 | Validate all views with sample queries | Stephen Curry | 2 hrs |

**Exit Criteria:** All 17+ views created and validated

### Phase 3: Squad Integration Views (Days 6-7)

| Step | Description | Owner | Effort |
|------|-------------|-------|--------|
| 3.1 | Create `analytics_ipl_squad_batting_2026` | Stephen Curry | 2 hrs |
| 3.2 | Create `analytics_ipl_squad_bowling_2026` | Stephen Curry | 2 hrs |
| 3.3 | Create team-level aggregation views | Stephen Curry | 3 hrs |
| 3.4 | Handle limited-data players (flag + fallback) | Stephen Curry | 3 hrs |
| 3.5 | Create debutant profile view | Stephen Curry | 2 hrs |

**Exit Criteria:** All squad members have associated analytics

### Phase 4: Generator Updates (Days 8-10)

| Step | Description | Owner | Effort |
|------|-------------|-------|--------|
| 4.1 | Update `generate_stat_packs.py` for new sections | Stephen Curry | 4 hrs |
| 4.2 | Update `generate_depth_charts.py` with enhancements | Stephen Curry | 3 hrs |
| 4.3 | Update `generate_predicted_xii.py` with conditions | Stephen Curry | 4 hrs |
| 4.4 | Add IPL vs All T20 comparison sections | Stephen Curry | 3 hrs |
| 4.5 | Add new player/debutant handling | Stephen Curry | 2 hrs |

**Exit Criteria:** Generators produce enhanced outputs

### Phase 5: Output Generation (Days 11-12)

| Step | Description | Owner | Effort |
|------|-------------|-------|--------|
| 5.1 | Regenerate all 10 stat packs | Stephen Curry | 2 hrs |
| 5.2 | Regenerate all 10 depth charts | Stephen Curry | 1 hr |
| 5.3 | Regenerate all 10 predicted XIIs | Stephen Curry | 1 hr |
| 5.4 | Generate new outputs (matchup matrices, etc.) | Stephen Curry | 4 hrs |
| 5.5 | Quality review of all outputs | Andy Flower | 4 hrs |

**Exit Criteria:** All outputs generated and reviewed

### Phase 6: Documentation & Validation (Days 13-14)

| Step | Description | Owner | Effort |
|------|-------------|-------|--------|
| 6.1 | Update DATA_DICTIONARY.md with new views | Stephen Curry | 2 hrs |
| 6.2 | Update scripts/README.md | Stephen Curry | 1 hr |
| 6.3 | Domain Sanity review (Jose/Andy/Pep) | All | 3 hrs |
| 6.4 | Final Founder review | Founder | 2 hrs |
| 6.5 | Commit and ship | Stephen Curry | 1 hr |

**Exit Criteria:** All documentation updated, reviews complete

### Dependencies

```
Phase 1 (Data Validation)
    ↓
Phase 2 (IPL Views)
    ↓
Phase 3 (Squad Integration)
    ↓
Phase 4 (Generator Updates)
    ↓
Phase 5 (Output Generation)
    ↓
Phase 6 (Documentation)
```

### Total Estimated Effort

| Phase | Days | Hours |
|-------|------|-------|
| Phase 1: Data Validation | 2 | 9 |
| Phase 2: IPL-Specific Views | 3 | 19 |
| Phase 3: Squad Integration | 2 | 12 |
| Phase 4: Generator Updates | 3 | 16 |
| Phase 5: Output Generation | 2 | 12 |
| Phase 6: Documentation | 2 | 9 |
| **Total** | **14 days** | **77 hours** |

---

## 7. Questions for Founder

The following decisions require Founder input before implementation:

### 7.1 Scope Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Should we prioritize IPL-only views or also create All T20 comparison views? | IPL only / Both | Both (more comprehensive) |
| 2 | For players with <10 IPL matches, should we weight All T20 data or just flag them? | Weight / Flag only | Weight with flag |
| 3 | Should we generate opposition-specific predicted XIs (10x10 = 90 variants)? | Yes / No | No (too many, do on-demand) |

### 7.2 Output Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 4 | Should new outputs (matchup matrices, form tracker) be in stat packs or separate? | Integrated / Separate | Separate (keeps stat packs focused) |
| 5 | What's the minimum IPL match threshold to display individual stats? | 5 / 10 / 15 | 10 matches |
| 6 | Should debutant profiles include international T20I stats or just franchise leagues? | T20I + Franchise / T20I only / All | T20I + Franchise |

### 7.3 Priority Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 7 | Should we complete TKT-049 (Key Partnerships) before or after this work? | Before / After / Parallel | Parallel |
| 8 | Is 14 days timeline acceptable, or should we reduce scope for faster delivery? | 14 days / Reduce scope | 14 days (comprehensive) |
| 9 | Which teams should we pilot first (for faster feedback loop)? | All at once / Top 4 first | Top 4 first (MI, CSK, RCB, KKR) |

### 7.4 Technical Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 10 | Should new views be created as SQL files or in Python generators? | SQL files / Python | Python (consistent with current approach) |
| 11 | Should we version the analytics scripts (e.g., `analytics_ipl_v1.py`)? | Yes / No | Yes (cleaner iteration) |

---

## 8. Success Criteria

### 8.1 Quantitative

| Metric | Target |
|--------|--------|
| Player ID match rate | >95% |
| Views created | 17+ |
| Stat packs generated | 10/10 teams |
| Depth charts updated | 10/10 teams |
| Predicted XIIs updated | 10/10 teams |

### 8.2 Qualitative

| Criteria | Validation |
|----------|------------|
| Cricket accuracy | Andy Flower sign-off |
| Data robustness | Jose Mourinho sign-off |
| System integrity | Pep Guardiola sign-off |
| Business value | Florentino Perez approval |

---

## 9. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Player ID mismatches | Medium | Medium | Manual mapping table + validation |
| Limited data for debutants | Medium | High | All T20 fallback + clear flagging |
| View performance issues | Medium | Low | Indexing strategy + query optimization |
| Scope creep | High | Medium | Strict adherence to approved scope |
| Generator regressions | High | Low | Snapshot current outputs before changes |

---

## 10. Files to Create/Modify

| File | Action | Owner |
|------|--------|-------|
| `scripts/analytics_ipl.py` | CREATE | Stephen Curry |
| `scripts/generators/generate_stat_packs.py` | MODIFY | Stephen Curry |
| `scripts/generators/generate_depth_charts.py` | MODIFY | Stephen Curry |
| `scripts/generators/generate_predicted_xii.py` | MODIFY | Stephen Curry |
| `data/player_id_mapping.csv` | CREATE (if needed) | Andy Flower |
| `docs/DATA_DICTIONARY.md` | MODIFY | Stephen Curry |
| `stat_packs/*.md` | REGENERATE | Stephen Curry |
| `outputs/depth_charts/*.md` | REGENERATE | Stephen Curry |
| `outputs/predicted_xii/*.md` | REGENERATE | Stephen Curry |

---

## 11. Approval Section

### Task Integrity Loop Status

| Step | Status | Owner |
|------|--------|-------|
| Step 0: Task Declaration | COMPLETE | Stephen Curry |
| Step 1: Florentino Gate | **PENDING** | Florentino Perez |
| Step 2: Build | NOT STARTED | Stephen Curry |
| Step 3: Domain Sanity | NOT STARTED | Jose/Andy/Pep |
| Step 4: Enforcement Check | NOT STARTED | Tom Brady |
| Step 5: Commit and Ship | NOT STARTED | Stephen Curry |
| Step 6: Post Task Note | NOT STARTED | Stephen Curry |
| Step 7: System Check | NOT STARTED | N'Golo Kante |

### Founder Sign-off

```
FLORENTINO GATE: [PENDING]
Reason: [Awaiting Founder review]
Date: [YYYY-MM-DD]

FOUNDER DECISIONS:
Q1:
Q2:
Q3:
Q4:
Q5:
Q6:
Q7:
Q8:
Q9:
Q10:
Q11:

Notes:
```

---

## References

- Original Plan: `~/.claude/plans/misty-honking-clarke.md`
- Task Integrity Loop: `governance/TASK_INTEGRITY_LOOP.md`
- Data Dictionary: `docs/DATA_DICTIONARY.md`
- PRD: `docs/PRD_CRICKET_PLAYBOOK.md`
- TKT-049 Plan: `docs/plans/TKT_049_KEY_PARTNERSHIPS_PLAN.md`

---

*IPL 2026 Player Analysis Plan v1.0*
*Cricket Playbook - Analytics Division*
*Stephen Curry (Analytics Lead)*
