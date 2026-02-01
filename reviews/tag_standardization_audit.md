# TAG STANDARDIZATION AUDIT REPORT

**Author:** Stephen Curry, Analytics Lead
**Date:** 2026-01-31
**Sprint:** Tag Standardization Review
**For Review By:** Andy Flower (Cricket Accuracy), Jose Mourinho (Data Robustness)

---

## EXECUTIVE SUMMARY

This audit examines all player tags in the Cricket Playbook system across two datasets:
- `player_tags.json` (all-time IPL data)
- `player_tags_2023.json` (2023+ filtered data)

**Key Findings:**
- **47 unique tags** identified across batters and bowlers
- **Inconsistent thresholds** between legacy and 2023+ tag generation
- **Missing baselines** for several tag categories
- **Sample size requirements** vary significantly across tag types
- **Several tags lack clear definitions** in code documentation

---

## 1. TAG INVENTORY

### 1.1 Batter Tags (26 unique tags)

| Tag | Category | Source File |
|-----|----------|-------------|
| SPECIALIST_VS_PACE | Bowling Type Matchup | batter_bowling_type_matchup.py |
| SPECIALIST_VS_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| SPECIALIST_VS_OFF_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| SPECIALIST_VS_LEG_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| SPECIALIST_VS_LEFT_ARM_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| SPECIALIST_VS_LEFT_ARM_WRIST_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| VULNERABLE_VS_PACE | Bowling Type Matchup | batter_bowling_type_matchup.py |
| VULNERABLE_VS_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| VULNERABLE_VS_OFF_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| VULNERABLE_VS_LEG_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| VULNERABLE_VS_LEFT_ARM_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| VULNERABLE_VS_LEFT_ARM_WRIST_SPIN | Bowling Type Matchup | batter_bowling_type_matchup.py |
| PLAYMAKER | Role-Based | generate_all_2023_outputs.py |
| AGGRESSIVE | Role-Based | generate_all_2023_outputs.py |
| ANCHOR | Role-Based | generate_all_2023_outputs.py |
| SIX_HITTER | Role-Based | generate_all_2023_outputs.py |
| DEATH_SPECIALIST | Phase Performance | player_tags.json (legacy) |
| MIDDLE_ORDER | Position-Based | player_tags.json (legacy) |
| MIDDLE_OVERS_ACCELERATOR | Phase Performance | player_tags.json (legacy) |
| FINISHER | Role-Based | player_tags.json (legacy) |
| EXPLOSIVE_OPENER | Role-Based | player_tags.json (legacy) |
| PP_DOMINATOR | Phase Performance | player_tags.json (legacy) |
| ACCUMULATOR | Role-Based | player_tags.json (legacy) |
| INCONSISTENT | Consistency | player_tags.json (legacy) |
| CONSISTENT | Consistency | player_tags.json (legacy) |
| SPIN_SPECIALIST | Bowling Type | player_tags.json (legacy) |
| PACE_SPECIALIST | Bowling Type | player_tags.json (legacy) |

### 1.2 Bowler Tags (21 unique tags)

| Tag | Category | Source File |
|-----|----------|-------------|
| LHB_SPECIALIST | Handedness Matchup | bowler_handedness_matchup.py |
| RHB_SPECIALIST | Handedness Matchup | bowler_handedness_matchup.py |
| LHB_VULNERABLE | Handedness Matchup | bowler_handedness_matchup.py |
| RHB_VULNERABLE | Handedness Matchup | bowler_handedness_matchup.py |
| LHB_WICKET_TAKER | Handedness Matchup | bowler_handedness_matchup.py |
| RHB_WICKET_TAKER | Handedness Matchup | bowler_handedness_matchup.py |
| LHB_PRESSURE | Handedness Matchup | bowler_handedness_matchup.py |
| RHB_PRESSURE | Handedness Matchup | bowler_handedness_matchup.py |
| ECONOMICAL | Economy-Based | generate_all_2023_outputs.py |
| EXPENSIVE | Economy-Based | generate_all_2023_outputs.py |
| DOT_BALL_KING | Pressure-Based | generate_all_2023_outputs.py |
| PP_BEAST | Phase Performance | bowler_phase_tags.py |
| PP_LIABILITY | Phase Performance | bowler_phase_tags.py |
| MIDDLE_OVERS_BEAST | Phase Performance | bowler_phase_tags.py |
| MIDDLE_OVERS_LIABILITY | Phase Performance | bowler_phase_tags.py |
| DEATH_BEAST | Phase Performance | bowler_phase_tags.py |
| DEATH_LIABILITY | Phase Performance | bowler_phase_tags.py |
| PROVEN_WICKET_TAKER | Career Milestone | player_tags.json (legacy) |
| WORKHORSE | Workload | player_tags.json (legacy) |
| NEW_BALL_SPECIALIST | Phase Specialist | player_tags.json (legacy) |
| PRESSURE_BUILDER | Pressure-Based | player_tags.json (legacy) |

---

## 2. TAG DEFINITIONS AND THRESHOLDS

### 2.1 Batter Bowling Type Matchup Tags

**Source:** `scripts/analysis/batter_bowling_type_matchup.py` and `scripts/generators/generate_all_2023_outputs.py`

| Tag | Definition | Threshold Criteria | Sample Size |
|-----|------------|-------------------|-------------|
| SPECIALIST_VS_PACE | Batter scores quickly vs pace with quality runs | SR >= 130 AND (avg >= 20 OR null) AND balls/dismissal >= 15 | Min 30 balls |
| SPECIALIST_VS_SPIN | Batter scores quickly vs spin with quality runs | SR >= 130 AND (avg >= 20 OR null) AND balls/dismissal >= 15 | Min 30 balls |
| SPECIALIST_VS_OFF_SPIN | Batter scores quickly vs off-spin | SR >= 130 AND (avg >= 20 OR null) AND balls/dismissal >= 15 | Min 30 balls |
| SPECIALIST_VS_LEG_SPIN | Batter scores quickly vs leg-spin | SR >= 130 AND (avg >= 20 OR null) AND balls/dismissal >= 15 | Min 30 balls |
| SPECIALIST_VS_LEFT_ARM_SPIN | Batter scores quickly vs left-arm orthodox | SR >= 130 AND (avg >= 20 OR null) AND balls/dismissal >= 15 | Min 30 balls |
| SPECIALIST_VS_LEFT_ARM_WRIST_SPIN | Batter scores quickly vs left-arm wrist spin | SR >= 130 AND (avg >= 20 OR null) AND balls/dismissal >= 15 | Min 30 balls |
| VULNERABLE_VS_PACE | Batter struggles vs pace | SR < 110 OR avg < 12 OR (dismissals >= 3 AND balls/dismissal < 12) | Min 30 balls |
| VULNERABLE_VS_SPIN | Batter struggles vs spin | SR < 110 OR avg < 12 OR (dismissals >= 3 AND balls/dismissal < 12) | Min 30 balls |
| VULNERABLE_VS_OFF_SPIN | Batter struggles vs off-spin | SR < 110 OR avg < 12 OR (dismissals >= 3 AND balls/dismissal < 12) | Min 30 balls |
| VULNERABLE_VS_LEG_SPIN | Batter struggles vs leg-spin | SR < 110 OR avg < 12 OR (dismissals >= 3 AND balls/dismissal < 12) | Min 30 balls |
| VULNERABLE_VS_LEFT_ARM_SPIN | Batter struggles vs left-arm orthodox | SR < 110 OR avg < 12 OR (dismissals >= 3 AND balls/dismissal < 12) | Min 30 balls |
| VULNERABLE_VS_LEFT_ARM_WRIST_SPIN | Batter struggles vs left-arm wrist spin | SR < 110 OR avg < 12 OR (dismissals >= 3 AND balls/dismissal < 12) | Min 30 balls |

### 2.2 Batter Role-Based Tags (2023+ Dataset)

**Source:** `scripts/generators/generate_all_2023_outputs.py`

| Tag | Definition | Threshold Criteria | Sample Size |
|-----|------------|-------------------|-------------|
| PLAYMAKER | Elite strike rate batter | Overall SR >= 150 | Min 100 balls |
| AGGRESSIVE | Above-average strike rate batter | Overall SR >= 140 (but < 150) | Min 100 balls |
| ANCHOR | Low strike rate accumulator | Overall SR < 120 | Min 300 balls |
| SIX_HITTER | Frequent boundary hitter | Boundary% >= 20% | Min 100 balls |

### 2.3 Bowler Handedness Matchup Tags

**Source:** `scripts/analysis/bowler_handedness_matchup.py`

| Tag | Definition | Threshold Criteria | Sample Size |
|-----|------------|-------------------|-------------|
| LHB_SPECIALIST | Better economy vs left-handers | Economy diff (LHB - RHB) <= -1.0 | Min 60 balls vs each hand |
| RHB_SPECIALIST | Better economy vs right-handers | Economy diff (LHB - RHB) >= 1.0 | Min 60 balls vs each hand |
| LHB_VULNERABLE | Struggles vs left-handers | Economy diff (LHB - RHB) >= 1.0 | Min 60 balls vs each hand |
| RHB_VULNERABLE | Struggles vs right-handers | Economy diff (LHB - RHB) <= -1.0 | Min 60 balls vs each hand |
| LHB_WICKET_TAKER | Takes wickets more efficiently vs LHB | Wickets/ball diff >= 0.02 AND LHB wickets/ball >= 0.03 | Min 60 balls vs each hand |
| RHB_WICKET_TAKER | Takes wickets more efficiently vs RHB | Wickets/ball diff <= -0.02 AND RHB wickets/ball >= 0.03 | Min 60 balls vs each hand |
| LHB_PRESSURE | Higher dot ball % vs LHB | Dot% diff >= 5% | Min 60 balls vs each hand |
| RHB_PRESSURE | Higher dot ball % vs RHB | Dot% diff <= -5% | Min 60 balls vs each hand |

### 2.4 Bowler Phase Performance Tags

**Source:** `scripts/analysis/bowler_phase_tags.py`

| Tag | Definition | Threshold Criteria | Sample Size |
|-----|------------|-------------------|-------------|
| PP_BEAST | Excellent powerplay economy | Economy <= 7.0 | Min 30 overs in powerplay |
| PP_LIABILITY | Poor powerplay economy | Economy >= 9.5 | Min 30 overs in powerplay |
| MIDDLE_OVERS_BEAST | Excellent middle overs economy | Economy <= 7.0 | Min 50 overs in middle |
| MIDDLE_OVERS_LIABILITY | Poor middle overs economy | Economy >= 8.5 | Min 50 overs in middle |
| DEATH_BEAST | Excellent death overs economy | Economy <= 9.0 | Min 30 overs in death |
| DEATH_LIABILITY | Poor death overs economy AND poor strike rate | Economy >= 12.0 AND balls/wicket >= 18 | Min 30 overs in death |

### 2.5 Bowler Economy-Based Tags (2023+ Dataset)

**Source:** `scripts/generators/generate_all_2023_outputs.py`

| Tag | Definition | Threshold Criteria | Sample Size |
|-----|------------|-------------------|-------------|
| ECONOMICAL | Very low economy rate | Economy <= 7.0 | Min 60 balls |
| EXPENSIVE | High economy rate | Economy >= 9.5 | Min 60 balls |
| DOT_BALL_KING | High dot ball percentage | Dot% >= 45% | Min 60 balls |

---

## 3. BASELINE ANALYSIS

### 3.1 Batter Strike Rate Distribution (2023+)

Based on `player_tags_2023.json` analysis:

| Percentile | Strike Rate | Tag Implication |
|------------|-------------|-----------------|
| 10th | ~120 | Below this = ANCHOR territory |
| 25th | ~135 | - |
| 50th (Median) | ~148 | League average |
| 75th | ~160 | - |
| 90th | ~175 | PLAYMAKER territory (SR >= 150) |

**Threshold Assessment:**
- SPECIALIST threshold (SR >= 130) represents approximately **35th percentile** - relatively inclusive
- VULNERABLE threshold (SR < 110) represents approximately **10th percentile** - appropriately strict
- PLAYMAKER threshold (SR >= 150) represents approximately **60th percentile** - elite but achievable

### 3.2 Bowler Economy Distribution (2023+)

Based on `player_tags_2023.json` analysis:

| Percentile | Economy | Tag Implication |
|------------|---------|-----------------|
| 10th | ~7.8 | Elite ECONOMICAL |
| 25th | ~8.5 | - |
| 50th (Median) | ~9.3 | League average |
| 75th | ~10.0 | - |
| 90th | ~10.8 | EXPENSIVE territory |

**Threshold Assessment:**
- ECONOMICAL threshold (Eco <= 7.0) represents approximately **5th percentile** - very strict
- EXPENSIVE threshold (Eco >= 9.5) represents approximately **60th percentile** - appropriately tags lower performers

### 3.3 Bowler Phase Economy Baselines

From `bowler_phase_tags.py` comments:

| Phase | Median Economy | 75th Percentile | Tag Threshold |
|-------|---------------|-----------------|---------------|
| Powerplay | ~7.5 | ~8.5 | Beast: <= 7.0, Liability: >= 9.5 |
| Middle | ~7.5 | ~8.0 | Beast: <= 7.0, Liability: >= 8.5 |
| Death | ~10.8 | ~11.5 | Beast: <= 9.0, Liability: >= 12.0 |

---

## 4. CONSISTENCY CHECK

### 4.1 Consistent Tag Pairs

**GOOD: Symmetric specialist/vulnerable tags**
- SPECIALIST_VS_PACE <-> VULNERABLE_VS_PACE (same thresholds)
- LHB_SPECIALIST <-> RHB_SPECIALIST (same economy diff threshold: 1.0)
- PP_BEAST <-> PP_LIABILITY (reasonable economy thresholds)

### 4.2 Inconsistencies Found

#### Issue 1: Asymmetric Bowler Economy Thresholds
```
ECONOMICAL: Economy <= 7.0 (2023+ dataset)
EXPENSIVE:  Economy >= 9.5 (2023+ dataset)

Gap: 7.0 - 9.5 = 2.5 point gap with no tag
```
**Impact:** Bowlers with economy between 7.0-9.5 receive no economy tag.
**Recommendation:** Consider adding "AVERAGE" tag or adjusting thresholds.

#### Issue 2: Death Phase Inconsistency
```
DEATH_BEAST:     Economy <= 9.0
DEATH_LIABILITY: Economy >= 12.0 AND balls/wicket >= 18

Gap: 9.0 - 12.0 = 3.0 point gap with no tag
```
**Impact:** Bowlers with death economy 9.0-12.0 are not tagged either way.
**Note:** The DEATH_LIABILITY has a dual condition (economy + strike rate) which is intentionally more strict.

#### Issue 3: Legacy vs 2023+ Tag Differences
The following tags appear in `player_tags.json` but NOT in `player_tags_2023.json`:
- DEATH_SPECIALIST (batter)
- MIDDLE_ORDER (batter)
- MIDDLE_OVERS_ACCELERATOR (batter)
- FINISHER (batter)
- EXPLOSIVE_OPENER (batter)
- PP_DOMINATOR (batter)
- ACCUMULATOR (batter)
- INCONSISTENT / CONSISTENT (batter)
- PROVEN_WICKET_TAKER (bowler)
- WORKHORSE (bowler)
- NEW_BALL_SPECIALIST (bowler)

**Impact:** 2023+ dataset has significantly fewer tag types, losing some nuanced player classifications.
**Recommendation:** Consider adding these tags to the 2023+ generation script.

### 4.3 Overlapping Tags

#### Potential Conflict: Handedness Tags
A bowler can receive both:
- `LHB_SPECIALIST` (economy better vs LHB)
- `RHB_WICKET_TAKER` (takes more wickets vs RHB)

**Assessment:** This is NOT a conflict - it represents a valid scenario where a bowler concedes fewer runs to LHB but takes more wickets against RHB. The dual-metric approach is correct.

#### Potential Conflict: Batter Matchup Tags
A batter could theoretically receive both:
- `SPECIALIST_VS_SPIN` (aggregated spin performance)
- `VULNERABLE_VS_OFF_SPIN` (specific type struggle)

**Assessment:** This CAN happen and is valid - a batter might be good vs leg-spin (boosting overall spin stats) but struggle vs off-spin specifically.

---

## 5. ISSUES AND RECOMMENDATIONS

### 5.1 Critical Issues

| Issue | Severity | Impact | Recommendation |
|-------|----------|--------|----------------|
| Missing tag definitions in 2023+ | HIGH | Reduced analytical depth | Add legacy tags to generate_all_2023_outputs.py |
| No baseline documentation | HIGH | Thresholds not data-driven | Add percentile calculations to scripts |
| Inconsistent sample sizes | MEDIUM | Different reliability levels | Standardize minimum balls to 60 for all matchup tags |

### 5.2 Tags Without Clear Definitions

The following legacy tags have **no documented threshold criteria** in the codebase:

1. **ACCUMULATOR** - No SR/avg threshold defined
2. **INCONSISTENT / CONSISTENT** - No variance metric defined
3. **FINISHER** - No death overs SR threshold defined
4. **MIDDLE_ORDER** - No position detection logic documented
5. **WORKHORSE** - No balls bowled threshold defined
6. **PROVEN_WICKET_TAKER** - No wicket count threshold defined
7. **PRESSURE_BUILDER** - No dot ball % threshold defined

**Recommendation:** These tags appear to be generated by a different (possibly older) script not in the current codebase. Need to locate or recreate the definition logic.

### 5.3 Sample Size Inconsistencies

| Tag Category | Current Min Sample | Recommended Min | Rationale |
|--------------|-------------------|-----------------|-----------|
| Batter vs Bowling Type | 30 balls | 50 balls | 30 balls is only ~5 overs - high variance |
| Bowler vs Handedness | 60 balls | 60 balls | Good - represents 10 overs |
| Bowler Phase (PP) | 30 overs | 30 overs | Good - represents 5 matches |
| Bowler Phase (Middle) | 50 overs | 40 overs | 50 overs may be too strict |
| Bowler Phase (Death) | 30 overs | 30 overs | Good |
| Overall Career (2023+) | 100 balls (batter) / 60 balls (bowler) | 150 balls / 90 balls | Current thresholds may include too many low-sample players |

### 5.4 Naming Convention Issues

| Current | Issue | Suggested |
|---------|-------|-----------|
| DEATH_BEAST / DEATH_LIABILITY | Inconsistent with batter phase tags | Keep for clarity |
| PP_BEAST | Abbreviation may be unclear | POWERPLAY_BEAST |
| DOT_BALL_KING | Gendered language | DOT_BALL_MASTER |
| SIX_HITTER | Doesn't account for fours | BOUNDARY_HITTER exists in clustering |

---

## 6. SUMMARY TABLES

### 6.1 All Tags with Status

| Tag | Dataset | Has Definition | Has Baseline | Sample Size OK |
|-----|---------|---------------|--------------|----------------|
| SPECIALIST_VS_PACE | Both | YES | NO | REVIEW |
| SPECIALIST_VS_SPIN | Both | YES | NO | REVIEW |
| SPECIALIST_VS_OFF_SPIN | Both | YES | NO | REVIEW |
| SPECIALIST_VS_LEG_SPIN | Both | YES | NO | REVIEW |
| SPECIALIST_VS_LEFT_ARM_SPIN | Both | YES | NO | REVIEW |
| SPECIALIST_VS_LEFT_ARM_WRIST_SPIN | Both | YES | NO | REVIEW |
| VULNERABLE_VS_* | Both | YES | NO | REVIEW |
| PLAYMAKER | 2023+ | YES | NO | YES |
| AGGRESSIVE | 2023+ | YES | NO | YES |
| ANCHOR | 2023+ | YES | NO | YES |
| SIX_HITTER | 2023+ | YES | NO | YES |
| LHB_SPECIALIST | Both | YES | NO | YES |
| RHB_SPECIALIST | Both | YES | NO | YES |
| LHB_VULNERABLE | Both | YES | NO | YES |
| RHB_VULNERABLE | Both | YES | NO | YES |
| LHB_WICKET_TAKER | Both | YES | NO | YES |
| RHB_WICKET_TAKER | Both | YES | NO | YES |
| ECONOMICAL | 2023+ | YES | NO | YES |
| EXPENSIVE | 2023+ | YES | NO | YES |
| DOT_BALL_KING | 2023+ | YES | NO | YES |
| PP_BEAST | Both | YES | PARTIAL | YES |
| PP_LIABILITY | Both | YES | PARTIAL | YES |
| MIDDLE_OVERS_BEAST | Both | YES | PARTIAL | YES |
| MIDDLE_OVERS_LIABILITY | Both | YES | PARTIAL | YES |
| DEATH_BEAST | Both | YES | PARTIAL | YES |
| DEATH_LIABILITY | Both | YES | PARTIAL | YES |
| DEATH_SPECIALIST (batter) | Legacy | NO | NO | UNKNOWN |
| MIDDLE_ORDER | Legacy | NO | NO | UNKNOWN |
| FINISHER | Legacy | NO | NO | UNKNOWN |
| ACCUMULATOR | Legacy | NO | NO | UNKNOWN |
| INCONSISTENT | Legacy | NO | NO | UNKNOWN |
| PROVEN_WICKET_TAKER | Legacy | NO | NO | UNKNOWN |
| WORKHORSE | Legacy | NO | NO | UNKNOWN |

### 6.2 Recommended Priority Actions

| Priority | Action | Owner |
|----------|--------|-------|
| P0 | Document legacy tag generation logic | Stephen Curry |
| P1 | Add baseline percentile calculations to all scripts | Stephen Curry |
| P1 | Increase batter vs bowling type minimum to 50 balls | Stephen Curry |
| P2 | Port missing tags to 2023+ generation | Stephen Curry |
| P2 | Standardize naming conventions | Team Review |
| P3 | Add sample size indicators to output files | Stephen Curry |

---

## APPENDIX A: Source Code References

1. **Batter Bowling Type Matchup:** `/Users/dwijeshreddy/cricket-playbook/scripts/analysis/batter_bowling_type_matchup.py`
2. **Bowler Handedness Matchup:** `/Users/dwijeshreddy/cricket-playbook/scripts/analysis/bowler_handedness_matchup.py`
3. **Bowler Phase Tags:** `/Users/dwijeshreddy/cricket-playbook/scripts/analysis/bowler_phase_tags.py`
4. **2023+ Output Generator:** `/Users/dwijeshreddy/cricket-playbook/scripts/generators/generate_all_2023_outputs.py`
5. **Player Clustering V2:** `/Users/dwijeshreddy/cricket-playbook/scripts/analysis/player_clustering_v2.py`

## APPENDIX B: Output Files

1. **All-time Tags:** `/Users/dwijeshreddy/cricket-playbook/outputs/tags/player_tags.json`
2. **2023+ Tags:** `/Users/dwijeshreddy/cricket-playbook/outputs/tags/player_tags_2023.json`
3. **Batter Matchup (2023+):** `/Users/dwijeshreddy/cricket-playbook/outputs/matchups/batter_bowling_type_matchup_2023.csv`
4. **Bowler Matchup (2023+):** `/Users/dwijeshreddy/cricket-playbook/outputs/matchups/bowler_handedness_matchup_2023.csv`

---

**Report Generated:** 2026-01-31
**Next Review:** Pending Andy Flower (Cricket) and Jose Mourinho (Data) approval
