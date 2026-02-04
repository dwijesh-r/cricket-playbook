# Response to Founder Review #3

**Date:** 2026-01-21
**Reviewers:** Tom Brady (Product Owner), Stephen Curry (Analytics)

---

## Executive Summary

Founder Review #3 identified 8 issues across tag definitions, classification logic, and data quality. Several classification bugs have been identified that need immediate fixes.

---

## Issue Analysis

### Issue 1: What does LHB Pressure, RHB Pressure mean?

**Answer:** These tags indicate bowlers who build pressure through dot balls against specific handedness:
- **LHB_PRESSURE**: Bowler has ≥5% higher dot ball percentage vs left-handers
- **RHB_PRESSURE**: Bowler has ≥5% higher dot ball percentage vs right-handers

**Action:** Add clear documentation to outputs/README.md explaining all tags.

---

### Issue 2: Phase-wise classification for bowlers

**Request:** Tags like "POWERPLAY_BEAST", "DEATH_OVERS_LIABILITY" etc.

**Proposed Tags:**
| Tag | Criteria |
|-----|----------|
| PP_BEAST | Economy <7.0 in PP with 30+ PP overs |
| PP_LIABILITY | Economy >9.5 in PP with 30+ PP overs |
| MIDDLE_OVERS_BEAST | Economy <7.0 in middle with 50+ middle overs |
| MIDDLE_OVERS_LIABILITY | Economy >8.5 in middle with 50+ middle overs |
| DEATH_BEAST | Economy <8.5 at death with 30+ death overs |
| DEATH_LIABILITY | Economy >10.5 at death with 30+ death overs |

**Status:** WILL IMPLEMENT

---

### Issue 3: Aiden Markram - Specialist vs Left-arm Spin

**Problem:** Markram labeled as SPECIALIST_VS_LEFT_ARM_SPIN but data shows:
- 110 balls vs left-arm orthodox
- 8 dismissals (1 dismissal every 13.75 balls - VERY HIGH)
- Average: 18.0 (LOW)
- SR: 130.91 (looks good but misleading)

**Root Cause:** Current logic only looks at strike rate. Need to factor in:
1. **Dismissal rate** (balls per dismissal)
2. **Average** (runs per dismissal)
3. **Comparison to global benchmarks**

**Fix:** Change specialist/vulnerable criteria to include average:
- SPECIALIST: SR ≥130 AND Average ≥25 AND balls per dismissal ≥20
- VULNERABLE: SR <105 OR Average <15 OR balls per dismissal <12

**Status:** WILL FIX

---

### Issue 4: Time frame for batter entry points and bowling type CSVs

**Answer:** All IPL data from 2008-2025 (full history).

**Action:** Add metadata to CSV outputs showing:
- Data range (seasons included)
- Last updated timestamp
- Minimum sample sizes used

---

### Issue 5: Bowler over timing - sample size filter

**Request:** Don't give tag if sample size too low.

**Current State:** MIN_INNINGS = 5 (too low)

**Fix:** Increase to MIN_INNINGS = 15 for role classification tags.

**Status:** WILL FIX

---

### Issue 6: Deepak Chahar misclassification

**Data:**
```
DL Chahar: over1_median=0, over1_mode=0, over1_count=95
```

He bowls his first over at over 0 (powerplay) in 95 matches, but classified as MIDDLE_OVERS_BOWLER.

**Root Cause:** BUG in classification logic. The median value 0 is being treated incorrectly.

**Status:** BUG - WILL FIX

---

### Issue 7: Trent Boult misclassification

**Data:**
```
TA Boult: over1_median=0, over1_mode=0, over2_median=2, over2_mode=2
```

Clearly bowls overs 0 and 2 (powerplay), but classified as MIDDLE_OVERS_BOWLER.

**Root Cause:** Same bug as Issue 6.

**Status:** BUG - WILL FIX

---

### Issue 8: Death overs specialist classification missing

**Problem:** No DEATH_BOWLER category showing up at all.

**Data Check - Malinga:**
```
SL Malinga: over1_median=1, over4_median=18
```

Malinga bowls PP (over 1) AND death (over 18). Current logic only looks at first over timing.

**Fix:** Improve classification to look at WHERE bowlers bowl most frequently:
1. Count overs bowled in PP (1-6), Middle (7-15), Death (16-20)
2. Classify based on majority phase
3. Add dual tags for bowlers like Malinga who bowl multiple phases

**Status:** WILL FIX

---

## Implementation Plan

| Priority | Fix | Owner | Complexity |
|----------|-----|-------|------------|
| P0 | Fix bowler timing classification bug (Issues 6, 7) | Stephen Curry | Low |
| P0 | Add death overs specialist detection (Issue 8) | Stephen Curry | Medium |
| P1 | Add dismissal rate to batter matchup tags (Issue 3) | Stephen Curry | Medium |
| P1 | Add phase-wise bowler tags (Issue 2) | Stephen Curry | Medium |
| P2 | Add sample size filter (Issue 5) | Stephen Curry | Low |
| P2 | Add metadata to CSV outputs (Issue 4) | Brock Purdy | Low |
| P2 | Document tag definitions (Issue 1) | Tom Brady | Low |

---

## Sign-off

| Role | Name | Status |
|------|------|--------|
| Product Owner | Tom Brady | ISSUES ACKNOWLEDGED |
| Analytics | Stephen Curry | FIXES PLANNED |
| Founder | - | AWAITING REVIEW |

---

*Response prepared by Tom Brady, Product Owner*
*2026-01-21*
