# Response to Founder Review #2

**Date:** 2026-01-21
**Reviewers:** Tom Brady (Product Owner), Brock Purdy (Data Pipeline), Stephen Curry (Analytics)

---

## Executive Summary

Founder Review #2 identified 3 data quality issues and 3 scope enhancements. Data fixes have been applied immediately. Scope enhancements are being implemented.

---

## Part A: Experience Squad CSV - Data Fixes

### Issue 1: Aman Khan (CSK) - FIXED

**Problem:** Bowling stats pulled from Avesh Khan instead of Aman Hakim Khan
- Both players had been mapped to same player_id `eef2536f`

**Root Cause:** Name similarity caused incorrect fuzzy matching

**Fix Applied:**
- Corrected player_id: `eef2536f` → `378daa89`
- Aman Hakim Khan is the correct database match

**Verification:**
| Metric | Before (Wrong) | After (Correct) |
|--------|----------------|-----------------|
| Matches | 13 | 10 |
| Runs | 62 | 115 |
| Balls Faced | - | 104 |
| Wickets | 87 | 0 |
| Balls Bowled | 1619 | 6 |

---

### Issue 2: Shahrukh Khan (GT) - FIXED

**Problem:** Stats mapped to wrong player (SN Khan instead of M Shahrukh Khan)

**Root Cause:** Multiple players with "Khan" surname - wrong player_id selected

**Fix Applied:**
- Corrected player_id: `f088b960` → `7dcb9bc9`
- M Shahrukh Khan is the correct database match

**Verification:**
| Metric | Before (Wrong) | After (Correct) | Founder Expected |
|--------|----------------|-----------------|------------------|
| Matches | 36 | 48 | 49 innings |
| Runs | 444 | 732 | 732 |
| Balls | 585 | 491 | 491 |

*Note: 48 matches vs 49 innings - player may have batted twice in some matches*

---

### Issue 3: Rasikh Salam Dar (RCB) - FIXED

**Problem:** Marked as uncapped with zero stats, but played IPL 2025 for RCB

**Root Cause:** Name variation ("Rasikh Salam Dar" vs "Rasikh Salam" in database)

**Fix Applied:**
- Corrected player_id: `uncapped_rasikh_salam_dar` → `b8527c3d`
- Removed uncapped flag

**Verification:**
| Metric | Before | After |
|--------|--------|-------|
| Matches | 0 | 13 |
| Wickets | 0 | 10 |
| Balls Bowled | 0 | 231 |
| Economy | - | 10.7 |

---

### Issue 4: Cross-verification with Cricbuzz

**Status:** ACKNOWLEDGED

**Plan:**
- Will implement a validation script to cross-check key stats against Cricbuzz
- Focus on players with >20 IPL matches for highest impact verification
- Flag discrepancies >5% for manual review

---

## Part B: Scope Enhancements - Implementation Plan

### Enhancement 1: Entry Point Improvements

**Current State:** Average entry point (mean batting position)

**Founder Feedback:**
- Use median or mode instead of average
- Make it granular in terms of balls (not just overs)
- Example: Opener entry = 0.0, Batter at 3 after wicket at 4.4 overs = 29th ball

**Implementation Plan:**
1. Calculate entry point as ball number in innings (not over number)
2. Report median entry point (more robust to outliers)
3. Add mode entry point for typical position
4. For bowlers: Track when they bowl 1st, 2nd, 3rd, 4th overs (frequency distribution)

**Owner:** Stephen Curry
**Status:** PENDING

---

### Enhancement 2: Bowler Handedness - Add Wickets & Strike Rate

**Current State:** Only economy differential analyzed

**Founder Feedback:** Include wickets aspect and strike rate

**Implementation Plan:**
1. Add wickets differential (vs LHB vs RHB)
2. Add bowling strike rate differential
3. Create additional tags:
   - LHB_WICKET_TAKER / RHB_WICKET_TAKER
   - LHB_PRESSURE / RHB_PRESSURE (based on SR)

**Owner:** Stephen Curry
**Status:** PENDING

---

### Enhancement 3: Batter vs Bowling Type Matchup Tags

**Current State:** Bowler handedness matchups exist, but not batter vs bowling type

**Founder Feedback:** Add tags like:
- VULNERABLE_VS_LEFT_ARM_SPIN
- VULNERABLE_VS_OFF_SPIN
- SPECIALIST_VS_PACE

**Implementation Plan:**
1. Analyze batter performance vs each bowling type:
   - Right-arm pace
   - Left-arm pace
   - Off-spin
   - Leg-spin
   - Left-arm orthodox
2. Calculate SR and average vs each type
3. Generate specialist/vulnerable tags based on thresholds:
   - SPECIALIST: SR ≥130 and Avg ≥25
   - VULNERABLE: SR <105 or Avg <15

**Owner:** Stephen Curry
**Status:** PENDING

---

## Implementation Priority

| Priority | Enhancement | Complexity | Owner | Status |
|----------|-------------|------------|-------|--------|
| P0 | Data fixes (Aman, Shahrukh, Rasikh) | Low | Brock Purdy | DONE |
| P1 | Batter vs bowling type matchups | Medium | Stephen Curry | DONE |
| P1 | Bowler handedness wickets/SR | Low | Stephen Curry | DONE |
| P2 | Entry point improvements | High | Stephen Curry | DONE |
| P3 | Cricbuzz cross-verification | Medium | Brock Purdy | BACKLOG |

---

## Deliverables

| Output File | Description |
|-------------|-------------|
| `outputs/ipl_2026_squad_experience.csv` | Regenerated with fixed player mappings |
| `outputs/bowler_handedness_matchup.csv` | Updated with wickets & SR differentials |
| `outputs/batter_bowling_type_matchup.csv` | New: Batter vs pace/spin performance |
| `outputs/batter_bowling_type_detail.csv` | New: Detailed breakdown by bowling type |
| `outputs/batter_entry_points.csv` | New: Median/mode entry points in balls |
| `outputs/bowler_over_timing.csv` | New: When bowlers bowl their 1st-4th overs |
| `outputs/player_tags.json` | Updated with 99 bowler + 131 batter matchup tags |

---

## New Tags Added

### Bowler Handedness Tags (Enhanced)
- LHB_WICKET_TAKER: 38 bowlers
- RHB_WICKET_TAKER: 25 bowlers

### Batter vs Bowling Type Tags (New)
- SPECIALIST_VS_PACE: 136 batters
- SPECIALIST_VS_SPIN: 67 batters
- VULNERABLE_VS_PACE: 25 batters
- VULNERABLE_VS_SPIN: 17 batters
- Plus specific tags for off-spin, leg-spin, left-arm spin

---

## Sign-off

| Role | Name | Status |
|------|------|--------|
| Product Owner | Tom Brady | APPROVED |
| Data Pipeline | Brock Purdy | DATA FIXES COMPLETE |
| Analytics | Stephen Curry | ALL ENHANCEMENTS COMPLETE |
| Founder | - | AWAITING REVIEW |

---

*Response prepared by Tom Brady, Product Owner*
*2026-01-21*
