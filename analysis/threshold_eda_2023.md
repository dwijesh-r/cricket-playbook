# EDA for Tag Thresholds (IPL 2023+)

**Author:** Stephen Curry (Analytics Lead)
**Date:** 2026-01-26
**Data Scope:** IPL 2023, 2024, 2025

---

## 1. Batter Entry Point Thresholds

### Percentile Analysis (ball_seq when batter arrives)

| Percentile | Value (balls) | Interpretation |
|------------|---------------|----------------|
| P10 | 4.1 | Clear openers |
| P25 | 21.7 | Top order cutoff |
| P50 | 67.8 | Middle order median |
| P75 | 95.6 | Lower order cutoff |
| P90 | 111.4 | Deep finishers |

### Recommended Thresholds

| Position | Ball Range | Rationale |
|----------|------------|-----------|
| **TOP_ORDER** | 1-30 | Below P25, covers overs 1-5 |
| **MIDDLE_ORDER** | 30-72 | P25 to ~P50, covers overs 5-12 |
| **LOWER_ORDER** | 72+ | Above P50, covers overs 12+ |

### Founder's Proposed Thresholds (Comparison)

| Position | Founder Proposal | EDA Recommendation | Status |
|----------|-----------------|-------------------|--------|
| Top Order | 7-72 balls | 1-30 balls | **Narrower range** |
| Middle Order | 60-90 balls | 30-72 balls | **Adjusted** |
| Lower Order | 90+ balls | 72+ balls | **Adjusted** |

**Note:** Founder's ranges allow overlap. EDA suggests distinct cutoffs for clarity.

---

## 2. Batter Specialist Tags

### Strike Rate Thresholds

Based on IPL 2023+ career batting data:

| Percentile | Strike Rate | Tag |
|------------|-------------|-----|
| P90+ | > 165 | POWER_HITTER |
| P75-90 | 145-165 | AGGRESSIVE |
| P25-75 | 125-145 | BALANCED |
| P10-25 | 110-125 | ACCUMULATOR |
| < P10 | < 110 | SLOW_STARTER |

### Average Thresholds

| Percentile | Average | Tag |
|------------|---------|-----|
| P90+ | > 45 | ELITE |
| P75-90 | 35-45 | RELIABLE |
| P25-75 | 22-35 | AVERAGE |
| < P25 | < 22 | INCONSISTENT |

### Boundary Percentage Thresholds

| Percentile | BPD | Tag |
|------------|-----|-----|
| P90+ | > 22% | BOUNDARY_HITTER |
| P75-90 | 18-22% | AGGRESSIVE |
| P25-75 | 12-18% | BALANCED |
| < P25 | < 12% | ROTATOR |

---

## 3. Batter Vulnerability Tags

### Current Criteria
- SR < 100 against bowling type
- Average < 15 against bowling type
- Minimum 30 balls faced

### Recommended Enhancement
Include dismissal rate:
- Dismissal rate > 8% (dismissed more than 1 in 12 balls)
- SR < 110 OR Average < 18
- Minimum 30 balls faced

---

## 4. Bowler Phase Tags

### Death Phase (Overs 16-20) Thresholds

| Metric | Percentile | Value | Tag |
|--------|------------|-------|-----|
| Economy | P25 | < 9.0 | DEATH_BEAST |
| Economy | P75 | > 12.0 | DEATH_LIABILITY |
| Strike Rate | P50 | 12.3 | Median |
| Strike Rate | P75 | > 18.0 | Poor |

**DEATH_LIABILITY requires BOTH:**
- Economy ≥ 12.0 (above P75)
- Strike Rate ≥ 18.0 (poor wicket-taking)

### Powerplay Phase (Overs 1-6) Thresholds

| Metric | Value | Tag |
|--------|-------|-----|
| Economy | < 7.0 | PP_BEAST |
| Economy | > 9.5 | PP_LIABILITY |

### Middle Overs Phase (Overs 7-15) Thresholds

| Metric | Value | Tag |
|--------|-------|-----|
| Economy | < 7.0 | MIDDLE_OVERS_BEAST |
| Economy | > 8.5 | MIDDLE_OVERS_LIABILITY |

---

## 5. Bowler Role Tags (Revised)

### Death Specialist Criteria
**Current:** ≥3 overs in overs 16+
**Revised:** ≥1 over in overs 16+ per match (more inclusive)

### New Tag: MIDDLE_AND_DEATH_SPECIALIST
Bowlers who regularly bowl both phases:
- ≥1 over in middle overs AND ≥1 over in death overs
- Bowled in 50%+ of matches in both phases

---

## 6. Bowler Handedness Tags

### Current Issue
"3+ wickets" threshold is too lenient - doesn't account for balls bowled.

### Revised Criteria
Use **wickets per ball ratio**:

| Metric | Threshold | Tag |
|--------|-----------|-----|
| WPB vs LHB > WPB vs RHB + 0.02 | AND LHB_WPB ≥ 0.03 | LHB_SPECIALIST |
| WPB vs RHB > WPB vs LHB + 0.02 | AND RHB_WPB ≥ 0.03 | RHB_SPECIALIST |
| Diff < 0.01 | Either direction | BALANCED |

---

## 7. Summary of Threshold Changes

| Category | Old Threshold | New Threshold | Rationale |
|----------|---------------|---------------|-----------|
| Entry: Top Order | ≤6 balls | ≤30 balls | EDA shows P25 = 21.7 |
| Entry: Middle Order | 7-24 balls | 30-72 balls | P25 to P50 |
| Entry: Lower Order | >24 balls | >72 balls | Above P50 |
| Death Economy Beast | 8.5 | 9.0 | Raised to be achievable |
| Death Economy Liability | 10.5 | 12.0 | Was below median, too harsh |
| Death SR Liability | N/A | 18.0 | New dual criterion |
| Death Specialist Overs | ≥3 overs | ≥1 over | More inclusive |
| Bowler Handedness | 3+ wickets | WPB ratio | Accounts for sample size |

---

## 8. Implementation Notes

1. All thresholds use IPL 2023+ data only
2. Minimum sample sizes apply (30 balls for batting, 1 over for bowling phases)
3. Dual criteria for liability tags prevent false positives
4. Percentile-based approach ensures thresholds adapt to T20 evolution

---

*Stephen Curry - Analytics Lead*
*Cricket Playbook Sprint 3.0*
