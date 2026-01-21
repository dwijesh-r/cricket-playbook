# Founder Review #1 - Validation Checklist

**Date:** 2026-01-21
**Sprint:** 2.4 - Data Fix Sprint
**Status:** READY FOR FOUNDER VALIDATION

---

## Instructions

Please verify each fix below against your original observations. Mark as PASS or FAIL.

---

## A. Player ID Mismatches (Uncapped Players)

All these players now have:
- `is_ipl_uncapped = TRUE`
- New unique player_id (not colliding with historical players)
- Stats set to 0 in experience CSV

| # | Player | Team | Original Issue | Status |
|---|--------|------|----------------|--------|
| 1 | Kartik Sharma | CSK | Mapped to Karn Sharma | Fixed - uncapped, 0 stats |
| 2 | Gurjapneet Singh | CSK | Mapped to Gurkeerat Singh Mann | Fixed - uncapped, 0 stats |
| 6 | Mohammed Izhar | MI | Mapped to unknown | Fixed - uncapped, 0 stats |
| 7 | Harnoor Singh | PBKS | Mapped to Harbhajan Singh | Fixed - uncapped, 0 stats |
| 8 | Ravi Singh | RR | Mapped to Rinku Singh | Fixed - uncapped, 0 stats |
| 9 | Brijesh Sharma | RR | Uncapped | Fixed - uncapped, 0 stats |
| 10 | Abhinandan Singh | RCB | Mapped to Arshdeep Singh | Fixed - uncapped, 0 stats |
| 35 | Shivang Kumar | SRH | Uncapped, bowls left-arm wrist spin | Fixed - uncapped, bowling: Left-arm wrist spin |
| 36 | Amit Kumar | SRH | Uncapped, bowls right-arm leg spin | Fixed - uncapped, bowling: Leg-spin |

**Founder Validation:** [ ] PASS  [ ] FAIL

---

## B. Bowling Type Corrections

| # | Player | Team | Was | Now | Your Note |
|---|--------|------|-----|-----|-----------|
| 3 | Aman Khan | CSK | Off-spin | Medium | Medium pacer |
| 5 | Ayush Badoni | LSG | Leg-spin | Off-spin | Off-spin bowler |
| 11 | Prashant Veer | CSK | Off-spin | Left-arm orthodox | Left arm orthodox |
| 12 | Nitish Rana | DC | Left-arm orthodox | Off-spin | Right arm off spin |
| 13 | Tristan Stubbs | DC | Medium | Off-spin | Right arm off spin |
| 14 | Vipraj Nigam | DC | Medium | Leg-spin | Leg spinner right arm |
| 15 | Shahrukh Khan | GT | Medium | Off-spin | Right arm off spinner |
| 16 | Gurnoor Brar | GT | Left-arm orthodox | Fast | Right arm fast bowler |
| 17 | Rinku Singh | KKR | Medium | Off-spin | Right arm off spinner |
| 18 | Prashant Solanki | KKR | Left-arm orthodox | Leg-spin | Right arm leg spinner |
| 19 | Daksh Kamra | KKR | Medium | Leg-spin | Leg spinner right arm |
| 20 | Digvesh Rathi | LSG | Medium | Leg-spin | Leg spinner right arm |
| 21 | Naman Dhir | MI | Left-arm orthodox | Off-spin | Right arm off spinner |
| 22 | Suryansh Shedge | PBKS | Off-spin | Medium | Medium pacer |
| 23 | Riyan Parag | RR | Off-spin | Leg-spin | Right arm leg spin |
| 24 | Yashasvi Jaiswal | RR | Left-arm orthodox | Leg-spin | Right arm leg spin |
| 25 | Ravi Singh | RR | Medium | Leg-spin | Right arm leg spin |
| 26 | Vaibhav Suryavanshi | RR | Medium | Left-arm orthodox | Left arm orthodox |
| 27 | Vignesh Puthur | RR | Leg-spin | Left-arm wrist spin | Left arm leg spin (chinaman) |
| 28 | Lhuan-dre Pretorius | RR | Fast | NULL | Doesn't bowl |
| 31 | Travis Head | SRH | Left-arm orthodox | Off-spin | Right arm off spin |
| 33 | Nitish Kumar Reddy | SRH | Fast | Medium | Medium pacer |
| 37 | Harsh Dubey | SRH | Off-spin | Left-arm orthodox | Left arm orthodox |

**Founder Validation:** [ ] PASS  [ ] FAIL

---

## C. Dual-Type Bowlers

New schema supports players who bowl multiple styles:

| Player | Team | Primary | Secondary | Your Note |
|--------|------|---------|-----------|-----------|
| Liam Livingstone | SRH | Leg-spin | Off-spin | Bowls both leg spin and off spin |
| Kamindu Mendis | SRH | Off-spin | Left-arm orthodox | Bowls both RA off spin and LA orthodox |

**Founder Validation:** [ ] PASS  [ ] FAIL

---

## D. RCB Squad Composition

| Change | Details |
|--------|---------|
| REMOVED | Raqibul Hasan |
| ADDED | Rasikh Salam Dar (Bowler, Fast) |
| ADDED | Vicky Ostwal (Bowler, Left-arm orthodox) |
| ADDED | Vihaan Malhotra (Batter) |
| ADDED | Kanishk Chouhan (Bowler, Leg-spin) |

**RCB Squad Size:** 24 players (was 21)

**Founder Validation:** [ ] PASS  [ ] FAIL

---

## E. Items NOT YET ADDRESSED (Deferred to Sprint 2.5)

These clustering methodology items are planned for the next sprint:

| # | Item | Status |
|---|------|--------|
| 1 | Time window - use data since 2021 only | Planned for Sprint 2.5 |
| 2 | Batting position / entry point analysis | Planned for Sprint 2.5 |
| 3 | Wickets across phases for bowlers | Planned for Sprint 2.5 |
| 4 | Sample size requirements review | Planned for Sprint 2.5 |
| 5 | 50% variance explanation target | Planned for Sprint 2.5 |
| 6 | Feature correlation analysis | Planned for Sprint 2.5 |
| 7 | MS Dhoni finisher classification | To verify |
| 8 | Jos Buttler / Patidar / Pant / Surya classification | Planned for Sprint 2.5 |
| 9 | Nortje not a part-timer | To verify |

---

## F. Summary Statistics

| Metric | Before | After |
|--------|--------|-------|
| Total players | 231 | 234 |
| Uncapped players identified | 0 | 13 |
| Bowling types corrected | - | 24 |
| Dual-type bowlers | 0 | 2 |
| RCB squad size | 21 | 24 |

---

## Sign-off

| Role | Name | Validation | Date |
|------|------|------------|------|
| Founder | - | [ ] APPROVED  [ ] REQUIRES CHANGES | |

**Notes/Additional Issues Found:**

_________________________________________________________________________________________

_________________________________________________________________________________________

_________________________________________________________________________________________

---

*Please return this checklist with your validation marks.*
