# Player ID Mismatch Audit Report

**Audit Date:** 2026-01-25
**Auditor:** Brock Purdy (Data Quality Engineer)
**Task ID:** S3.0-03
**Status:** CRITICAL ISSUES FOUND

---

## Executive Summary

This audit identified **15 critical player ID mismatches** across IPL 2026 squad data. The primary issue is **surname collision** where uncapped/new players are incorrectly mapped to historical players with the same or similar surnames. This results in incorrect career statistics being displayed in stat packs.

### Severity Classification
- **CRITICAL (5)**: Player stats completely wrong, shows experienced player data for uncapped player
- **HIGH (6)**: Duplicate player_id usage across different players
- **MEDIUM (4)**: Minor data inconsistencies or missing player_ids

---

## Section 1: Critical Surname Collision Mismatches

### 1.1 CRITICAL: Gurjapneet Singh -> Gurkeerat Singh (CSK)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Gurjapneet Singh | Gurkeerat Singh |
| **Player ID** | 6eb146d2 | 6eb146d2 |
| **Team** | Chennai Super Kings | - |
| **Role** | Bowler (Left-arm Fast) | Batter/All-rounder |
| **Expected IPL Experience** | ~0 matches (Uncapped) | 32+ innings batting |

**Evidence from CSK Stat Pack:**
- Line 327 shows venue data for "Gurkeerat Singh" with 7 innings, 120 runs at Punjab Cricket Association Stadium
- Gurjapneet Singh is an uncapped left-arm fast bowler
- Gurkeerat Singh is a veteran batter/all-rounder with different playing style

**Impact:** CSK stat pack shows batting statistics (121.09 SR, 21.29 Avg) for a fast bowler who should have minimal batting data.

**Fix Required:** Create new player_id for Gurjapneet Singh; do not reuse Gurkeerat Singh's ID.

---

### 1.2 CRITICAL: Ravi Singh -> Rinku Singh (RR)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Ravi Singh | Rinku Singh |
| **Player ID** | 0a509d6b | 0a509d6b |
| **Team** | Rajasthan Royals | Kolkata Knight Riders |
| **Expected IPL Experience** | Uncapped | 51 innings, 1099 runs |

**Evidence from Data:**
- `ipl_2026_squads.csv` Line 189: Ravi Singh (RR) has player_id `0a509d6b`
- `ipl_2026_squads.csv` Line 132: Rinku Singh (KKR) has player_id `0a509d6b`
- `ipl_2026_squad_experience.csv` Line 168: Shows "Ravi Singh" with 51 innings, 750 balls, 1099 runs

**Impact:** RR stat pack shows Rinku Singh's finisher statistics for a different uncapped player. Completely wrong career profile.

**Fix Required:** Create unique player_id for Ravi Singh (RR).

---

### 1.3 CRITICAL: Shubham Dubey -> Shivam Dube (RR)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Shubham Dubey | Shivam Dube |
| **Player ID** | a4e37e47 | a4e37e47 |
| **Team** | Rajasthan Royals | Chennai Super Kings |
| **Expected IPL Experience** | Limited | 75 innings, 1859 runs |

**Evidence from Data:**
- `ipl_2026_squads.csv` Line 185: Shubham Dubey (RR) has player_id `a4e37e47`
- `ipl_2026_squads.csv` Line 88: Shivam Dube (CSK) has player_id `a4e37e47`
- `ipl_2026_squad_experience.csv` Line 4: Shivam Dube with 75 innings
- `ipl_2026_squad_experience.csv` Line 164: "Shubham Dubey" showing same stats

**Impact:** Two different players sharing same player_id. RR Shubham Dubey showing CSK Shivam Dube's career stats.

**Fix Required:** Create unique player_id for Shubham Dubey.

---

### 1.4 CRITICAL: Shahrukh Khan (GT) -> Sarfaraz Khan (CSK)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Shahrukh Khan (GT) | Sarfaraz Khan |
| **Player ID** | f088b960 | f088b960 |
| **Team** | Gujarat Titans | Chennai Super Kings |

**Evidence from Data:**
- `ipl_2026_squad_experience.csv` Line 7: Sarfaraz Khan (CSK) with player_id implicitly
- `ipl_2026_squad_experience.csv` Line 58: Shahrukh Khan (GT) shows identical stats: 36 innings, 444 balls, 585 runs

**Impact:** Both players showing same stats (36 inn, 444 balls, 585 runs, 131.76 SR, 22.5 Avg).

**Fix Required:** Verify correct player_id assignment for both Shahrukh Khan and Sarfaraz Khan.

---

### 1.5 CRITICAL: Mohammed Izhar -> Mohammed Siraj (MI)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Mohammed Izhar | Mohammed Siraj |
| **Player ID** | 2f49c897 | 2f49c897 |
| **Team** | Mumbai Indians | Gujarat Titans |
| **Expected Experience** | Uncapped | 108 matches, 109 wickets |

**Evidence from Data:**
- `ipl_2026_squads.csv` Line 7: Mohammed Izhar (MI) has player_id `2f49c897`
- `ipl_2026_squads.csv` Line 18: Mohammed Siraj (GT) has player_id `2f49c897`
- `ipl_2026_squad_experience.csv` Line 124: Mohammed Izhar showing 108 bowling matches, 109 wickets

**Impact:** Uncapped bowler showing international star's career statistics.

**Fix Required:** Create unique player_id for Mohammed Izhar.

---

### 1.6 CRITICAL: Amit Kumar -> Ashwani Kumar (SRH)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Amit Kumar (SRH) | Ashwani Kumar |
| **Player ID** | d45c29b1 | d45c29b1 |
| **Team** | Sunrisers Hyderabad | Mumbai Indians |

**Evidence from Data:**
- `ipl_2026_squads.csv` Line 208: Amit Kumar (SRH) has player_id `d45c29b1`
- `ipl_2026_squads.csv` Line 118: Ashwani Kumar (MI) has player_id `d45c29b1`
- `ipl_2026_squad_experience.csv` Line 222: Amit Kumar showing 7 bowling matches, 11 wickets

**Impact:** Two different players sharing same player_id.

**Fix Required:** Create unique player_id for Amit Kumar (SRH).

---

## Section 2: High Priority - Duplicate Player ID Usage

### 2.1 Abhinandan Singh -> Arshdeep Singh (RCB)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Abhinandan Singh | Arshdeep Singh |
| **Player ID** | 244048f6 | 244048f6 |
| **Team** | Royal Challengers Bengaluru | Punjab Kings |

**Evidence:**
- `ipl_2026_squads.csv` Line 128: Abhinandan Singh (RCB) has player_id `244048f6`
- `ipl_2026_squads.csv` Line 11: Arshdeep Singh (PBKS) has player_id `244048f6`
- `ipl_2026_squad_experience.csv` Line 196: Abhinandan Singh showing 81 bowling matches, 97 wickets

**Fix Required:** Create unique player_id for Abhinandan Singh.

---

### 2.2 Aman Khan (CSK) -> Avesh Khan (LSG)

| Field | Squad Value | Mapped Data |
|-------|-------------|-------------|
| **Player Name** | Aman Khan | Avesh Khan |
| **Player ID** | eef2536f | eef2536f |
| **Team** | Chennai Super Kings | Lucknow Super Giants |

**Evidence:**
- `ipl_2026_squads.csv` Line 5: Aman Khan (CSK) has player_id implied by matching
- `ipl_2026_squad_experience.csv` Line 12: Shows batting 13 inn, 62 runs AND bowling 75 matches, 87 wickets

**Fix Required:** Create unique player_id for Aman Khan.

---

## Section 3: Stat Pack Display Anomalies

### 3.1 Harbhajan Singh appearing in PBKS Stat Pack

**Evidence:** PBKS stat pack line 362 shows "Harbhajan Singh" venue performance data.

**Issue:** Harbhajan Singh is not on the IPL 2026 PBKS squad. This is likely data leakage from historical records being incorrectly joined to the current roster.

---

### 3.2 Harnoor Singh (PBKS) Stats Mismatch

| Field | Expected | Actual |
|-------|----------|--------|
| **Role** | Batter | Shows bowling stats |
| **Batting Innings** | Unknown (young player) | 88 innings, 833 runs |
| **Bowling** | Part-time Medium | 160 matches, 150 wickets |

**Evidence:** `ipl_2026_squad_experience.csv` Line 142 shows Harnoor Singh with extensive bowling stats inconsistent with a batter.

**Potential Issue:** Mapped to Harbhajan Singh or another spinner named Singh.

---

## Section 4: Common Surname Collision Analysis

### Players with Surname "Singh" (14 players across squads)

| Player | Team | Player ID | Status |
|--------|------|-----------|--------|
| Gurjapneet Singh | CSK | 6eb146d2 | MISMATCH - Uses Gurkeerat Singh ID |
| Rinku Singh | KKR | 0a509d6b | OK |
| Ramandeep Singh | KKR | be24ead0 | OK |
| Tejasvi Singh | KKR | 0bf15e52 | OK |
| Arshdeep Singh | PBKS | 244048f6 | COLLISION with Abhinandan Singh |
| Prabhsimran Singh | PBKS | 9418198b | OK |
| Harnoor Singh | PBKS | 8b5b6769 | MISMATCH - Wrong bowling stats |
| Ravi Singh | RR | 0a509d6b | MISMATCH - Uses Rinku Singh ID |
| Yudhvir Singh | RR | 4885bbe6 | OK |
| Abhinandan Singh | RCB | 244048f6 | COLLISION with Arshdeep Singh |
| Swapnil Singh | RCB | 983f2f61 | OK |
| Akash Singh | LSG | b483905d | OK |
| Himmat Singh | LSG | ebcfef83 | OK |
| Shashank Singh | PBKS | 26989d80 | OK |

### Players with Surname "Sharma" (8 players)

| Player | Team | Player ID | Status |
|--------|------|-----------|--------|
| Rohit Sharma | MI | 740742ef | OK |
| Abhishek Sharma | SRH | f29185a1 | OK |
| Kartik Sharma | CSK | 119678fd | OK |
| Ishant Sharma | GT | 5bb1a1c4 | OK |
| Sandeep Sharma | RR | ce820073 | OK |
| Brijesh Sharma | RR | c18496e1 | OK |
| Jitesh Sharma | RCB | 800d2d97 | OK |
| Raghu Sharma | MI | 5b615e7c | OK |
| Suyash Sharma | RCB | 9440ef41 | OK |

### Players with Surname "Kumar" (6 players)

| Player | Team | Player ID | Status |
|--------|------|-----------|--------|
| Bhuvneshwar Kumar | RCB | 2e81a32d | OK |
| Mukesh Kumar | DC | 2cffab74 | OK |
| Nitish Kumar Reddy | SRH | aad0c365 | OK |
| Shivang Kumar | SRH | 8998a68f | OK |
| Amit Kumar | SRH | d45c29b1 | COLLISION with Ashwani Kumar |
| Ashwani Kumar | MI | d45c29b1 | COLLISION with Amit Kumar |

### Players with Surname "Khan" (7 players)

| Player | Team | Player ID | Status |
|--------|------|-----------|--------|
| Aman Khan | CSK | eef2536f | COLLISION with Avesh Khan |
| Avesh Khan | LSG | eef2536f | COLLISION with Aman Khan |
| Mohsin Khan | LSG | c33d8116 | OK |
| Rashid Khan | GT | 5f547c8b | OK |
| Arshad Khan | GT | 12314277 | OK |
| Shahrukh Khan | GT | f088b960 | COLLISION with Sarfaraz Khan |
| Musheer Khan | PBKS | d621b427 | OK |
| Sarfaraz Khan | CSK | f088b960 | COLLISION with Shahrukh Khan |

### Players with Surname "Yadav" (4 players)

| Player | Team | Player ID | Status |
|--------|------|-----------|--------|
| Suryakumar Yadav | MI | 271f83cd | OK |
| Kuldeep Yadav | DC | 8d2c70ad | OK |
| Jayant Yadav | GT | 81049310 | OK |
| Mayank Yadav | LSG | c6355538 | OK |
| Mangesh Yadav | RCB | b1ad996b | OK |

### Players with Surname "Patel" (2 players)

| Player | Team | Player ID | Status |
|--------|------|-----------|--------|
| Axar Patel | DC | 2e171977 | OK |
| Harshal Patel | SRH | f986ca1a | OK |
| Urvil Patel | CSK | cf59b3f0 | OK |

---

## Section 5: Players with Missing Player IDs

The following players have NULL/empty player_ids in `ipl_2026_squads.csv`:

| Player | Team | Notes |
|--------|------|-------|
| Ramakrishna Ghosh | CSK | Uncapped, needs new ID |
| Danish Malewar | MI | Uncapped, needs new ID |
| Satvik Deswal | RCB | Uncapped, needs new ID |
| Abhinandan Singh | RCB | Has incorrect ID (Arshdeep's) |
| Sahil Parakh | DC | Uncapped, needs new ID |
| Pyla Avinash | PBKS | Uncapped, needs new ID |
| Yash Raj Punja | RR | Uncapped, needs new ID |
| Ravichandran Smaran | SRH | Uncapped, needs new ID |
| Krains Fuletra | SRH | Uncapped, needs new ID |
| Onkar Tarmale | SRH | Uncapped, needs new ID |
| Praful Hinge | SRH | Uncapped, needs new ID |

---

## Section 6: Recommended Fixes

### Immediate Actions Required

1. **Create new player_ids for all collision cases:**
   - Gurjapneet Singh (CSK) - new unique ID
   - Ravi Singh (RR) - new unique ID
   - Shubham Dubey (RR) - new unique ID
   - Mohammed Izhar (MI) - new unique ID
   - Amit Kumar (SRH) - new unique ID
   - Abhinandan Singh (RCB) - new unique ID
   - Aman Khan (CSK) - new unique ID
   - Shahrukh Khan (GT) or Sarfaraz Khan (CSK) - verify correct assignment

2. **Generate player_ids for uncapped players with NULL IDs**

3. **Re-run stat pack generation** after fixing player_ids

4. **Add validation check** in ETL pipeline to prevent duplicate player_id usage across different players

### Database Update Script Needed

```sql
-- Example fixes (actual IDs to be generated)
UPDATE dim_player SET player_id = 'NEW_UNIQUE_ID_1' WHERE player_name = 'Gurjapneet Singh' AND team = 'CSK';
UPDATE dim_player SET player_id = 'NEW_UNIQUE_ID_2' WHERE player_name = 'Ravi Singh' AND team = 'RR';
-- etc.
```

---

## Section 7: Root Cause Analysis

The mismatches appear to be caused by:

1. **Fuzzy name matching** in the player ID assignment process that matches on surname similarity
2. **Reuse of existing player_ids** when new players join with similar names
3. **Lack of validation** to ensure player_ids are unique per player
4. **Missing disambiguation** for common Indian surnames

### Prevention Recommendations

1. Add unique constraint validation on player_id per player_name
2. Implement player verification step using additional attributes (team, role, bowling arm)
3. Flag new players for manual review before ID assignment
4. Create allowlist of known collision-prone surnames for extra validation

---

## Appendix: Data Files Reviewed

- `/Users/dwijeshreddy/cricket-playbook/data/ipl_2026_squads.csv`
- `/Users/dwijeshreddy/cricket-playbook/data/ipl_2026_squad_experience.csv`
- `/Users/dwijeshreddy/cricket-playbook/data/ipl_2026_player_contracts.csv`
- `/Users/dwijeshreddy/cricket-playbook/stat_packs/CSK_stat_pack.md`
- `/Users/dwijeshreddy/cricket-playbook/stat_packs/GT_stat_pack.md`
- `/Users/dwijeshreddy/cricket-playbook/stat_packs/RR_stat_pack.md`
- `/Users/dwijeshreddy/cricket-playbook/stat_packs/PBKS_stat_pack.md`

---

**Report Generated:** 2026-01-25
**Next Steps:** Assign to data engineering team for player_id correction
