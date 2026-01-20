# Cricket Playbook - Rework Plan v2.1

**Owner:** Tom Brady (Product Owner)
**Contributors:** Stephen Curry (Analytics), Andy Flower (Cricket), Brock Purdy (Data)
**Date:** 2026-01-20
**Status:** APPROVED FOR EXECUTION

---

## Executive Summary

Following v2.0.0 release and user feedback review, this document captures all required fixes, enhancements, and infrastructure improvements for the next sprint.

---

## Critical Bugs (P0) - FIXED

### 1. Sarfaraz Khan Price Error
- **Issue:** Listed as 5.0 Cr, should be 0.50 Cr (50 lakhs)
- **Status:** FIXED
- **Files Updated:**
  - `data/ipl_2026_player_contracts.csv`
  - `stat_packs/CSK_stat_pack.md`
  - `ipl_2026_contracts` table in DuckDB

### 2. Kartik Sharma Classification
- **Issue:** Questioned if wicketkeeper role is correct
- **Status:** VERIFIED CORRECT
- **Evidence:** Multiple sources confirm Kartik Sharma is a wicketkeeper-batter, bought by CSK for Rs 14.2 Cr at IPL 2026 auction

---

## Critical Analytics Bug (P0) - REQUIRES REWORK

### 3. Bowler Type Analysis Defect

**Problem:**
The `analytics_ipl_batter_vs_bowler_type` view shows values like "Bowler", "All-rounder", "Batter" instead of proper bowling types ("Fast", "Off-spin", "Leg-spin", etc.).

**Root Cause:**
```sql
COALESCE(bt.bowling_type, dp_bowl.primary_role) AS bowler_type
```
Only 2026 squad players have `bowling_type` populated. Historical IPL bowlers (not in 2026 squads) fall back to `primary_role` which contains generic roles.

**Impact:**
- KL Rahul vs bowler type shows "Bowler", "All-rounder" instead of pace/spin breakdown
- Ishan Kishan and all other batters affected
- Renders this analysis meaningless for editorial use

**Solution Options:**

| Option | Effort | Quality | Recommended |
|--------|--------|---------|-------------|
| A. Web scrape bowling types for all IPL bowlers | High | Best | Yes |
| B. Manual classification of top 100 IPL bowlers | Medium | Good | Backup |
| C. Use heuristics from bowling patterns | Medium | Moderate | No |
| D. Remove view until data available | Low | N/A | Interim |

**Recommended Action:**
1. **Immediate:** Add warning disclaimer to stat packs for this view
2. **Sprint 2.1:** Create `dim_bowler_classification` table with comprehensive bowling types
3. **Data Source:** ESPNCricinfo player profiles, IPL official data

---

## High Priority (P1)

### 4. Sample Size Indicators Missing

**Issue:** Stats shown without confidence indicators
**Solution:** Add `sample_size_class` column to all player stat views

```sql
CASE
  WHEN balls_faced < 30 THEN 'LOW'
  WHEN balls_faced < 100 THEN 'MEDIUM'
  ELSE 'HIGH'
END AS sample_size_class
```

**Apply to:**
- All batter phase views
- All batter matchup views
- All bowler phase views

### 5. Franchise Alias Handling in Queries - COMPLETED

**Issue:** Delhi Capitals stats don't include Delhi Daredevils history
**Status:** FIXED (2026-01-20)

**Solution Implemented:**
1. Created `dim_franchise_alias` table with mappings:
   - Delhi Daredevils → Delhi Capitals
   - Kings XI Punjab → Punjab Kings
   - Royal Challengers Bangalore → Royal Challengers Bengaluru

2. Updated views with LEFT JOIN to alias table:
   - `analytics_ipl_batter_vs_team`
   - `analytics_ipl_batter_vs_team_phase`
   - `analytics_ipl_bowler_vs_team`
   - `analytics_ipl_bowler_vs_team_phase`

3. All stat packs regenerated with combined franchise history

### 6. Impact Metrics Missing

**Issue:** SR and averages alone don't show impact
**Solution:** Add to all batting views:
- `boundary_pct` = (fours + sixes) / balls * 100
- `dot_ball_pct` = dots / balls * 100
- `runs_per_boundary` = runs / (fours + sixes)

---

## Medium Priority (P2)

### 7. Percentile Rankings

**Issue:** No context for how stats compare globally
**Solution:** Add percentile columns using window functions

```sql
PERCENT_RANK() OVER (ORDER BY strike_rate) AS sr_percentile
```

### 8. IPL vs Global Average Comparison

**Issue:** No baseline for comparison
**Solution:** Create reference views with IPL-wide averages by phase/role

### 9. Unmapped Players (10 of 231)

**Issue:** 10 newer uncapped players without Cricsheet IDs
**Players:** Likely recent domestic performers without international/franchise data
**Solution:** Manual ID assignment or wait for Cricsheet updates

---

## Infrastructure (P3)

### 10. README.md for Stat Packs
**Deliverable:** `stat_packs/README.md` explaining:
- File structure
- Data freshness
- Usage guidelines
- Known limitations

### 11. CLI Runner Script
**Deliverable:** `scripts/run_stat_packs.sh`
- Regenerates all stat packs
- Validates output
- Reports errors

### 12. Stat Pack Contract/Schema
**Deliverable:** `docs/STAT_PACK_CONTRACT.md`
- Required sections
- Column definitions
- Validation rules

### 13. Smoke Tests
**Deliverable:** `tests/test_stat_packs.py`
- Table existence checks
- View query validation
- Sample data assertions

### 14. Schema Validation
**Deliverable:** `scripts/validate_schema.py`
- Foreign key integrity
- Required column presence
- Data type verification

---

## Sprint Allocation

### Sprint 2.1 (Immediate)
- [x] Fix Sarfaraz Khan price
- [x] Verify Kartik Sharma classification
- [x] Add disclaimers to bowler type analysis (DONE - 2026-01-20)
- [x] Sample size indicators in views (DONE - already in all phase/matchup views)

### Sprint 2.2 (Next)
- [x] Comprehensive bowler classification table (DONE - 280 bowlers classified)
- [x] Franchise alias handling (DONE - 2026-01-20)
- [x] Impact metrics (boundary%, dot%) - DONE (already in all views)
- [x] README and documentation (DONE - stat_packs/README.md created)

### Sprint 2.3 (Future)
- [ ] Percentile rankings
- [ ] IPL average comparisons
- [ ] CLI runner and tests
- [ ] Schema validation

---

## Sign-off

| Role | Agent | Status |
|------|-------|--------|
| Product Owner | Tom Brady | APPROVED |
| Analytics | Stephen Curry | ACKNOWLEDGED |
| Cricket Domain | Andy Flower | ACKNOWLEDGED |
| Data Pipeline | Brock Purdy | ACKNOWLEDGED |
| QA | N'Golo Kanté | PENDING REVIEW |

---

*Tom Brady*
*Product Owner - Cricket Playbook*
