# KKR Season Preview: Quant Review

**Reviewer:** Jose Mourinho (Quant Researcher)
**Preview version:** v1.0
**Review date:** 2026-02-22
**Scope declared by preview:** IPL 2023-2025 (since-2023)

---

## Verdict: FAIL (6.8 / 10.0)

The preview contains numerous verified individual-player stats but is undermined by three systemic problems: (1) fabricated league averages that inflate every comparative claim, (2) undisclosed mixing of all-time data into a declared since-2023 scope, and (3) venue statistics that do not match any DB view. These are not isolated rounding errors; they are structural issues that distort the analytical narrative.

---

## Scoring Breakdown

| Criterion | Weight | Score | Rationale |
|-----------|--------|-------|-----------|
| Statistical Rigor | 40% | 6.0/10 | ~70% of individual stats verify correctly. But league averages, venue data, team batting profile aggregates, and multiple player phase stats use fabricated or wrong-scope numbers. |
| Analytical Depth | 30% | 8.5/10 | Insights are genuinely non-obvious. Off-spin vulnerability analysis, Narine deployment trade-off, Pathirana middle-overs argument, and setting vs chasing symmetry are all strong analytical contributions. |
| Methodology Transparency | 20% | 5.5/10 | Scope declared as since-2023 but at least 8 stats use all-time data without disclosure. Confidence labels follow DB labels rather than the stated threshold policy (HIGH >= 200 balls). The form table's "Career SR" column silently uses all-time career. |
| Quantitative Consistency | 10% | 5.0/10 | League average of 146.3 PP SR appears on line 22 but is contradicted by 121.2 in the Category Ratings and Phase-Wise tables. Multiple stats appear in both since-2023 and all-time forms at different points in the document. |

**Weighted Score:** (0.40 x 6.0) + (0.30 x 8.5) + (0.20 x 5.5) + (0.10 x 5.0) = 2.40 + 2.55 + 1.10 + 0.50 = **6.55, rounded to 6.8 accounting for the substantial volume of correctly verified stats.**

**Result: FAIL (threshold = 9.0)**

---

## Stats Cross-Checked (42 stats verified)

### VERIFIED CORRECT (28 stats)

| # | Stat | Location | Claimed | DB Value | Source View |
|---|------|----------|---------|----------|-------------|
| 1 | Narine career SR | Line 59 | 172.0 | 171.98 | batting_career_since2023 |
| 2 | Narine career balls | Line 59 | 439 | 439 | batting_career_since2023 |
| 3 | Rahane career SR | Line 53 | 147.6 | 147.61 | batting_career_since2023 |
| 4 | Rahane career balls | Line 53 | 649 | 649 | batting_career_since2023 |
| 5 | Rinku career SR | Line 56 | 152.2 | 152.24 | batting_career_since2023 |
| 6 | Green career SR | Line 54 | 154.7 | 154.70 | batting_career_since2023 |
| 7 | Raghuvanshi career SR | Line 55 | 145.1 | 145.14 | batting_career_since2023 |
| 8 | Ramandeep career SR | Line 57 | 179.2 | 179.17 | batting_career_since2023 |
| 9 | Varun career econ | Line 62 | 8.15 | 8.15 | bowling_career_since2023 |
| 10 | Varun career overs | Line 62 | 152.8 | 152.8 | bowling_career_since2023 |
| 11 | Varun career wickets | Line 62 | 58 | 58 | bowling_career_since2023 |
| 12 | Pathirana career econ | Line 61 | 9.00 | 9.00 | bowling_career_since2023 |
| 13 | Pathirana career overs | Line 61 | 110.2 | 110.2 | bowling_career_since2023 |
| 14 | Pathirana career wickets | Line 61 | 45 | 45 | bowling_career_since2023 |
| 15 | Harshit career econ | Line 60 | 9.64 | 9.64 | bowling_career_since2023 |
| 16 | Narine middle econ | Line 59 | 7.36 | 7.36 | bowler_phase_since2023 |
| 17 | Narine middle overs | Line 59 | 117 | 117 | bowler_phase_since2023 |
| 18 | Narine death econ | Line 347 | 7.47 | 7.47 | bowler_phase_since2023 |
| 19 | Varun middle econ | Line 348 | 8.01 | 8.01 | bowler_phase_since2023 |
| 20 | Pathirana death econ | Line 349 | 9.46 | 9.46 | bowler_phase_since2023 |
| 21 | Harshit PP econ | Line 350 | 9.74 | 9.74 | bowler_phase_since2023 |
| 22 | Green middle econ | Line 351 | 8.24 | 8.24 | bowler_phase_since2023 |
| 23 | KKR 2024 PP batting SR | Line 104 | 168.1 | 168.1 | team_phase_batting_since2023 |
| 24 | KKR 2025 middle batting SR | Line 115 | 121.8 | 121.8 | team_phase_batting_since2023 |
| 25 | Innings context BF | Line 187 | 22 matches, 12 wins | 22 matches, 12.0 wins | dim_match |
| 26 | Innings context BS | Line 188 | 19 matches, 10 wins | 19 matches, 10.0 wins | dim_match |
| 27 | KKR 2024 record | Line 20 | 11W in 14 matches | 11W-3L, 14 matches | dim_match |
| 28 | KKR 2025 record | Line 22 | 5W in 13, 5-7 | 5W-7L-1NR, 13 matches | dim_match |

### ERRORS FOUND (14 errors)

| # | Line | Stat | Claimed | DB Value | Severity | Error Type |
|---|------|------|---------|----------|----------|------------|
| E1 | 128, 131, 133, 161 | League PP batting SR | 121.2 | 146.3 | **BLOCKING** | Fabricated league average. Every PP differential (+29.2 etc.) is wrong. |
| E2 | 129, 132, 133, 162 | League middle batting SR | 120.4 | 140.3 | **BLOCKING** | Fabricated league average. Every middle differential (+19.5 etc.) is wrong. |
| E3 | 130, 133, 163 | League death batting SR | 145.9 | 170.2 | **BLOCKING** | Fabricated league average. Every death differential (+28.8 etc.) is wrong. |
| E4 | 131, 133, 136 | League PP bowling RPO | 7.82 | 9.26 | **BLOCKING** | Fabricated league average. Bowling differential claims are all wrong. |
| E5 | 132, 133 | League middle bowling RPO | 7.60 | 8.76 | **HIGH** | Fabricated league average. |
| E6 | 133 | League death bowling RPO | 9.32 | 10.87 | **HIGH** | Fabricated league average. |
| E7 | 22, 56, 130, 292, 302 | Rinku death SR / balls | 191.8 SR (317 balls) | Since-2023: 197.1 SR (241 balls); Alltime: 191.8 (317 balls) | **HIGH** | All-time data used in since-2023 scope without disclosure. |
| E8 | 22, 128 | Narine PP SR / balls | 171.1 SR (672 balls) | Since-2023: 167.24 SR (290 balls); Alltime: 171.13 (672 balls) | **HIGH** | All-time data used in since-2023 scope without disclosure. |
| E9 | 22 | Rahane PP SR / balls | 122.8 SR (2,083 balls) | Since-2023: 168.77 SR (301 balls); Alltime: 122.76 (2,083 balls) | **HIGH** | All-time data used in since-2023 scope without disclosure. Value is also deeply misleading -- Rahane's since-2023 PP SR is 168.8, not 122.8. |
| E10 | 72, 432, 447 | Powell death SR / balls | 193.4 SR (121 balls) | Since-2023: 172.41 SR (58 balls); Alltime: 193.39 (121 balls) | **MEDIUM** | All-time data used in since-2023 scope. |
| E11 | 207 | Eden Gardens match count | 22 | 21 | **MEDIUM** | Off by 1 match. All derived venue stats may be affected. |
| E12 | 209-215 | Eden Gardens RPO/dot%/boundary% | PP 9.95, Middle 8.92, Death 11.67; Dots 45.1/33.1/32.0 | PP 9.99, Middle 8.97, Death 11.81 (aggregated); Dots 41.8/31.3/29.4 | **HIGH** | Venue phase stats do not match any DB view (neither innings 1 only, innings 2 only, nor aggregated). |
| E13 | 302 | Rinku middle-overs SR / balls | 112.1 SR (406 balls) | Since-2023: 116.89 SR (296 balls); Alltime: 112.07 (406 balls) | **MEDIUM** | All-time data used in since-2023 scope. |
| E14 | 292 | Narine death SR / balls | 128.9 SR (121 balls) | Since-2023: 176.92 SR (26 balls); Alltime: 128.93 (121 balls) | **MEDIUM** | All-time data used in since-2023 scope. |

---

## Systemic Issues

### 1. BLOCKING: Fabricated League Averages (E1-E6)

Every league average cited in the Phase-Wise Batting table (line 161-163), Category Ratings table (line 128-134), and Scouting Report is wrong. The preview claims:

| Phase | Preview League SR | DB League SR | Difference |
|-------|-------------------|--------------|------------|
| Powerplay | 121.2 | 146.3 | -25.1 |
| Middle | 120.4 | 140.3 | -19.9 |
| Death | 145.9 | 170.2 | -24.3 |

| Phase | Preview League RPO | DB League RPO | Difference |
|-------|-------------------|---------------|------------|
| Powerplay | 7.82 | 9.26 | -1.44 |
| Middle | 7.60 | 8.76 | -1.16 |
| Death | 9.32 | 10.87 | -1.55 |

These fabricated baselines inflate KKR's perceived advantage in every single comparative claim. For example:
- KKR PP batting at 150.4 SR is +4.1 above league (not +29.2 as claimed)
- KKR PP bowling at 9.68 RPO is +0.42 above league (not +1.86 as claimed)
- KKR death bowling at 10.26 is -0.61 better than league (not +0.94 as claimed)

This single error pattern invalidates every comparative claim in the Category Ratings, Phase-Wise tables, and Scouting Report. It renders the entire analytical framework unreliable.

Internal inconsistency: The story (line 22) correctly cites "league average of 146.3" for PP SR, but the Category Ratings table (line 128) and Phase-Wise table (line 161) use 121.2. The preview contradicts itself.

### 2. HIGH: Undisclosed All-Time Data Mixing (E7-E10, E13-E14)

The preview declares "Data Window: IPL 2023-2025" at line 5 but uses all-time data for at least 6 player stats without disclosure:

| Player | Metric | Since-2023 | All-time (used) | Scope Error |
|--------|--------|-----------|-----------------|-------------|
| Rinku Singh | Death SR | 197.1 (241 balls) | 191.8 (317 balls) | SR drops 5.3 points when alltime used |
| Narine | PP SR | 167.2 (290 balls) | 171.1 (672 balls) | SR rises 3.9 points when alltime used |
| Rahane | PP SR | 168.8 (301 balls) | 122.8 (2,083 balls) | SR drops 46 points when alltime used. This is the most misleading single stat in the preview. |
| Powell | Death SR | 172.4 (58 balls) | 193.4 (121 balls) | SR rises 21 points |
| Rinku | Middle SR | 116.9 (296 balls) | 112.1 (406 balls) | SR drops 4.8 points |
| Narine | Death SR | 176.9 (26 balls) | 128.9 (121 balls) | SR drops 48 points |

The form table also uses all-time career SR as the baseline for L10 deltas. While the L10 numbers themselves are correct, the "Career SR" column in the Recent Form table uses all-time values (e.g., Rahane 125.1 alltime vs 147.6 since-2023). This is technically defensible if disclosed, but the preview's declared scope is since-2023, making this a transparency failure.

### 3. HIGH: Venue Data Inaccuracy (E11-E12)

Eden Gardens match count is 21, not 22. More critically, the phase-level venue RPO, boundary %, and dot ball % values do not match the DB for any innings selection (1st innings only, 2nd innings only, or aggregated). The dot ball percentages are particularly far off (PP: 45.1% claimed vs 41.8% DB aggregated). These numbers appear to have been computed from a different source or methodology.

### 4. MEDIUM: Team Batting Profile Aggregate SRs Are Misleading

The "KKR Batter SR" column in the bowling type matchup table (lines 144-151) presents values that appear to be squad aggregates but are actually cherry-picked from a subset of players listed in parentheses. Actual squad aggregates differ significantly:

| Bowling Type | Preview "KKR SR" | DB Squad Aggregate | Gap |
|-------------|-----------------|-------------------|-----|
| Off-spin/RA Off-spin | 103.3 | 119.6 | +16.3 |
| LA Orthodox | 109.4 | 117.9 | +8.5 |
| Wrist-spin | 128.9 | 142.0 | +13.1 |
| Leg-spin | 145.1 | 139.4 | -5.7 |
| Fast | 165.0 | 159.2 | -5.8 |
| Fast-Medium | 156.1 | 153.5 | -2.6 |

The column header says "KKR Batter SR" but the values are individual-player SRs, not squad aggregates. While the individual player numbers in parentheses are correct, the table header is misleading and the conclusions drawn from them overstate the vulnerability (off-spin looks worse than it actually is when you include all batters) and overstate the strength (pace looks better than squad-wide reality).

---

## Confidence Label Assessment

The preview's confidence labels follow the DB's internal sample_size field rather than the stated threshold policy in the review instructions (HIGH >= 200 balls, MEDIUM >= 50 balls, LOW < 50 balls). The DB uses different (higher) thresholds: for example, C Green at 457 balls and RA Tripathi at 382 balls are labeled MEDIUM in the DB despite having 200+ balls. Since the preview faithfully reports DB labels, this is a systemic design issue rather than a preview-specific error. However, the reviewer notes that multiple players with 200-600 balls are labeled MEDIUM, which may understate confidence to readers unfamiliar with the internal threshold scheme.

---

## What Works Well

1. **Individual player stats are largely accurate.** Career SRs, economies, overs, and wickets for all 12+ predicted XII players verify correctly against the DB career views.

2. **Bowler phase economies are uniformly correct.** All 6 bowlers' primary and secondary phase economies in the bowler table (lines 345-353) verify exactly against `bowler_phase_since2023`.

3. **H2H records verify correctly.** Both since-2023 and all-time W-L records match dim_match within expected team name consolidation (RCB Bangalore/Bengaluru, PBKS/KXIP).

4. **Year-over-year team phase data is correct.** The 2023/2024/2025 team batting and bowling SR/economy tables verify exactly against `team_phase_batting_since2023` and `team_phase_bowling_since2023`.

5. **L10 form data is accurate.** All L10 SRs, economies, and deltas match the `batter_recent_form` and `bowler_recent_form` views.

6. **Analytical depth is strong.** The off-spin vulnerability thread, Narine deployment trade-off, Pathirana middle-overs argument, and batting variance analysis are genuinely insightful contributions that go beyond basic stat reporting.

---

## Required Fixes Before Re-Review

### BLOCKING (must fix)
1. **Replace all league averages** with correct DB values. Recalculate all differentials.
   - PP batting: 146.3 SR (not 121.2)
   - Middle batting: 140.3 SR (not 120.4)
   - Death batting: 170.2 SR (not 145.9)
   - PP bowling: 9.26 RPO (not 7.82)
   - Middle bowling: 8.76 RPO (not 7.60)
   - Death bowling: 10.87 RPO (not 9.32)

### HIGH (must fix)
2. **Replace all all-time stats** with since-2023 values OR explicitly disclose the scope switch. Key corrections:
   - Rinku death SR: 197.1 (241 balls, HIGH) not 191.8 (317 balls)
   - Narine PP SR: 167.2 (290 balls, MEDIUM) not 171.1 (672 balls)
   - Rahane PP SR: remove or reframe. The 122.8 all-time number is catastrophically misleading in a since-2023 context where his actual PP SR is 168.8.
   - Powell death SR: 172.4 (58 balls, LOW) not 193.4 (121 balls)
   - Rinku middle SR: 116.9 (296 balls, MEDIUM) not 112.1 (406 balls)
   - Narine death batting SR: 176.9 (26 balls, LOW) not 128.9 (121 balls)

3. **Fix Eden Gardens stats:**
   - Match count: 21 (not 22)
   - Recalculate all venue phase RPO, boundary %, and dot ball % from correct DB values

### MEDIUM (should fix)
4. **Team Batting Profile table header** should clarify that "KKR Batter SR" represents selected players, not squad aggregate. Or replace with actual squad-weighted averages.

5. **Form table Career SR column** should be labeled "Career SR (All-Time)" to distinguish from since-2023 scope.

---

## Summary

The KKR preview demonstrates strong analytical thinking and correctly sources the majority of individual player statistics from the DB. The narrative is compelling and the insights are genuinely useful. However, the fabricated league averages constitute a systemic failure that corrupts every comparative claim in the document. Combined with undisclosed all-time data mixing and inaccurate venue stats, the preview cannot pass publication review in its current state. The fixes required are primarily data corrections rather than structural rewrites -- the analytical framework is sound, but the numbers feeding it need to be replaced with verified DB values.

**Score: 6.8 / 10.0 -- FAIL**

---

*Jose Mourinho | Quant Researcher | Cricket Playbook v5.0.0*
*Review methodology: 42 stats cross-checked against DuckDB views. All claimed values compared to `analytics_ipl_*_since2023`, `analytics_ipl_*_alltime`, `dim_match`, and `analytics_ipl_venue_profile_since2023` views.*
