# CSK Season Preview — Jose Mourinho Quant Review

**Reviewer:** Jose Mourinho (Quant Researcher)
**Date:** 2026-02-15
**Document Reviewed:** `outputs/season_previews/CSK_season_preview.md` (v1.0)
**Thresholds Reference:** `config/thresholds.yaml` (v1.2.0)
**Confidence System Reference:** `scripts/generators/generate_player_profiles.py` (_classify_sample: HIGH >= 200 balls, MEDIUM >= 50 balls, LOW < 50 balls)

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Statistical Rigor | 40% | 7.0/10 | 2.80 |
| Analytical Depth | 30% | 8.0/10 | 2.40 |
| Methodology Transparency | 20% | 7.0/10 | 1.40 |
| Quantitative Consistency | 10% | 6.0/10 | 0.60 |
| **Overall** | **100%** | | **7.2/10** |

---

## Statistical Errors / Inconsistencies

### ERROR-1: Dube's Middle-Overs Balls Exceed Career Balls (Arithmetically Impossible)

**Sections affected:** "Shivam Dube: The Middle-Overs Anchor" (line 306) and Squad Table (line 79)

The preview states:
- Career since 2023: "151.1 SR across **775 balls** since 2023 (HIGH)" (Squad Table, line 79; Players to Watch, line 306)
- Middle overs only: "136.3 SR across **873 balls** (HIGH) with 1,190 runs" (Players to Watch, line 306)

A player cannot have 873 balls in a single phase (middle overs) when their total balls across all phases is 775. One of these numbers is wrong. If 873 is the correct middle-overs figure, then 775 cannot be his total career balls. If 775 is correct, 873 must be inflated. This is a blocking arithmetic error.

**Severity:** BLOCKING. Must be corrected before publication.

### ERROR-2: Head-to-Head Losses Do Not Sum to Stated Total

**Section:** Head-to-Head Record (lines 268-280)

Individual opponent losses: SRH 7 + KKR 11 + DC 12 + RCB 13 + RR 15 + PBKS 15 + GT 4 + MI 21 + LSG 3 = **101 losses**.

The summary states: "All-Time: 131-**100** (56.7% win rate)."

131 wins is correct (sum of individual wins). But losses total 101, not 100. Either one H2H record has an off-by-one error, or the summary total is wrong.

Additionally: 131/(131+100) = 56.7%, but 131/(131+101) = 56.5%. The win percentage is calculated on the stated total, not the actual sum. Both the total and the percentage need correction.

**Severity:** BLOCKING. Arithmetic must be verified against source data.

### ERROR-3: PBKS Win Percentage Is Wrong

**Section:** Head-to-Head Record (line 275)

Stated: "16-15 | **50.0%**". Actual: 16/31 = **51.6%**. A 50.0% win rate would require an even split (e.g., 15-15 or 16-16). 16-15 is definitionally not 50.0%.

**Severity:** Minor but embarrassing for a quant publication.

### ERROR-4: Confidence Labels for Brevis and Mhatre Appear Incorrect

**Section:** Full Squad Table (lines 78, 76)

Using the project's primary classification system (`generate_player_profiles.py`: HIGH >= 200, MEDIUM >= 50, LOW < 50):
- Brevis: 159.8 SR (**184 balls**, labeled **LOW**). 184 >= 50 means this should be **MEDIUM**.
- Mhatre: 189.0 SR (**127 balls**, labeled **LOW**). 127 >= 50 means this should be **MEDIUM**.

Both players' confidence labels are one tier too low. If a different classification system was used (e.g., the InsightConfidence system where MEDIUM >= 100), Mhatre at 127 would still be MEDIUM and Brevis at 184 would still be MEDIUM.

The only system where 184 balls = LOW would require a LOW threshold above 184, which does not exist in any codebase classifier.

**Severity:** BLOCKING. Incorrect confidence labels mislead the reader about data reliability.

### ERROR-5: Contradictory Boundary Percentage in Scoring Profiles

**Section:** Scoring Profiles: Power vs Placement (line 388)

The text reads: "Samson's death-overs boundary percentage (**26.8%**) is **21.1%** against the league's 23.3%."

This sentence contains two different numbers for what appears to be the same metric. Is Samson's death boundary percentage 26.8% or 21.1%? The sentence structure implies 26.8% and 21.1% are the same thing, which is contradictory. Most likely, one number is a different metric (e.g., six percentage vs total boundary percentage) or there is a copy-paste error.

**Severity:** BLOCKING. The sentence is unintelligible as written.

### ERROR-6: Inconsistent Noor Ahmad Death-Overs Sample Size Label

**Section:** Bowlers Individual Phase Economies Table (line 360) and Players to Watch (line 294)

Noor Ahmad's death overs: "7.65 (21.2 ov, **HIGH**)". 21.2 overs = 127 balls. Under the player profile classification system, 127 balls = MEDIUM (not HIGH). Under the bowling phase threshold in `thresholds.yaml`, the minimum for death overs qualification is 30 overs -- he has only 21.2.

However, his middle-overs label of HIGH at 102 overs (612 balls) is clearly correct.

**Severity:** Moderate. The death-overs sample is substantial enough to be meaningful, but the label should be MEDIUM by the project's own classification. At minimum, it fails the `min_death_overs: 30` threshold in `thresholds.yaml`.

### ERROR-7: Samson Death-Overs Reference Uses Innings Instead of Balls

**Section:** The Story (line 26)

States: "191.7 SR at the death (**48 innings**, MEDIUM)."

The confidence label system classifies based on **balls**, not innings. Elsewhere in the same preview, the same stat is cited as "191.7 SR (407 balls, MEDIUM)" (line 202). The 48 innings is additional context but should not replace the balls-based denominator. This creates confusion about what the confidence label is based on.

**Severity:** Minor. The correct ball count appears elsewhere, but the inconsistency in denominator units undermines methodology transparency.

### ERROR-8: Rahul Chahar Data Window Mismatch Between Sections

**Section:** Auction Strategy Depth Buys Table (line 58) vs Bench Table (line 93)

- Depth buy table: "7.8 middle-overs econ across **239 overs** (HIGH)"
- Bench table: "8.29 econ / 18 wkts (**82 overs**, MEDIUM)"

The 239 overs figure likely reflects all-time career data, while 82 overs is "since 2023" per the data window stated in the header. Neither entry specifies its time window inline. For a reader, seeing 7.8 economy (239 overs) in one table and 8.29 economy (82 overs) in another for the same player creates confusion. The depth buy table must state its time window.

**Severity:** Moderate. Inconsistent time windows without labels violate methodology transparency.

---

## Strengths

1. **Delta calculations are flawless.** Every year-over-year delta in the Team Style Analysis section (2023 to 2024, 2024 to 2025) checks out to the decimal. This is the hallmark of pipeline-generated data, not manual entry, and it inspires confidence in the underlying analytics.

2. **Phase-level granularity is exceptional.** The preview does not treat CSK as a monolithic entity. It breaks performance into powerplay, middle, and death across batting and bowling, then cross-references with individual player profiles. This is the level of disaggregation that separates serious analysis from surface-level commentary.

3. **Sample sizes are shown for almost every claim.** Balls faced, overs bowled, and innings counts accompany nearly every metric. This is rare in cricket writing and allows the reader to independently assess reliability. The discipline is commendable even where the confidence labels themselves have errors.

4. **The venue analysis uses RPO correctly.** Chepauk phase profiles correctly use runs per over (RPO) for bowling/venue analysis, and strike rate (SR, per 100 balls) for batting. The SR/RPO distinction is maintained cleanly throughout the document. I found zero instances of SR being used where RPO should be, or vice versa.

5. **The Setting vs Chasing analysis is genuine insight.** The 10.1-point SR differential between setting and chasing is not a commonly discussed metric. The follow-up analysis that dot ball rates are similar (29.2% vs 29.4%) while boundary rates differ is exactly the kind of second-order thinking that elevates analysis.

6. **Bowling deployment phase tables are well-structured.** The individual phase economies table with primary/secondary phase designation, combined with the tactical deployment percentages, gives a complete picture of how the bowling attack functions as a unit.

7. **The Bold Take is data-backed.** The argument that Noor Ahmad is more important than Gaikwad is supported by specific replacement analysis (Chahar's economy as fallback, the phase-specific impact of removal). It follows a proper counterfactual framework rather than relying on narrative assertion.

---

## Changes Required for 9.0+

### 1. Fix Dube's Ball Count Contradiction (ERROR-1)
**Section:** Players to Watch, "Shivam Dube: The Middle-Overs Anchor" (line 306) and Squad Table (line 79)
**Current:** 775 balls (career) and 873 balls (middle overs)
**Required:** Query DuckDB for both values. If 775 is wrong, update it across all references (Squad Table line 79, Players to Watch line 306). If 873 is wrong, correct the middle-overs reference. The correct pair must satisfy: middle_overs_balls < total_career_balls.

### 2. Fix Head-to-Head Arithmetic (ERROR-2)
**Section:** Head-to-Head Record (lines 268-280)
**Current:** Individual losses sum to 101; stated total is 100.
**Required:** Verify each H2H record against the stat pack. Either correct the individual record that is off by one, or change the total to 131-101 (56.5%). Update the win percentage accordingly.

### 3. Fix PBKS Win Percentage (ERROR-3)
**Section:** Head-to-Head Record (line 275)
**Current:** "16-15 | 50.0%"
**Required:** "16-15 | 51.6%"

### 4. Correct Brevis and Mhatre Confidence Labels (ERROR-4)
**Section:** Full Squad Table (lines 76, 78)
**Current:** Both labeled LOW
**Required:** Both should be labeled MEDIUM (Brevis 184 balls, Mhatre 127 balls -- both >= 50 threshold)

### 5. Rewrite the Samson Boundary Percentage Sentence (ERROR-5)
**Section:** Scoring Profiles (line 388)
**Current:** "Samson's death-overs boundary percentage (26.8%) is 21.1% against the league's 23.3%"
**Required:** Clarify which number is correct and what the other represents. If 26.8% is total boundary % and 21.1% is six %, say so. If one is wrong, remove it. The sentence as written is incoherent.

### 6. Downgrade Noor Ahmad Death-Overs Confidence Label (ERROR-6)
**Section:** Bowlers Individual Phase Economies (line 360), Players to Watch (line 294)
**Current:** "7.65 (21.2 ov, HIGH)"
**Required:** "7.65 (21.2 ov, MEDIUM)" -- 21.2 overs = 127 balls, which is below the 200-ball HIGH threshold. Additionally, 21.2 overs is below the `min_death_overs: 30` qualification threshold in `thresholds.yaml`. Add a note acknowledging the sub-threshold sample.

### 7. Standardize Denominator Units in Confidence Labels (ERROR-7)
**Section:** The Story (line 26)
**Current:** "191.7 SR at the death (48 innings, MEDIUM)"
**Required:** "191.7 SR at the death (407 balls / 48 inn, MEDIUM)" -- Show balls first (since the confidence system is balls-based), with innings as supplementary context.

### 8. Add Time Window Labels to Depth Buy Table (ERROR-8)
**Section:** Auction Strategy Depth Buys Table (lines 56-63)
**Current:** No time window specified; Chahar shows "239 overs" (appears to be all-time)
**Required:** Add "(since 2023)" or "(career)" label to each entry. Align with the "Since 2023" window used elsewhere, or explicitly mark exceptions.

### 9. Add Denominators to All Category Ratings
**Section:** Category Ratings (lines 148-176)
**Current:** Ratings like "4.5/10" with descriptive context but no explicit methodology.
**Required:** State the inputs to each rating. Example: "4.5/10 based on 2025 PP SR (137.2) being 9.1 points below league avg (146.3), weighted by wickets lost per innings (2.1, +1.5 above league)." Without showing the calculation, ratings appear subjective.

### 10. Add Confidence Intervals or Ranges to Key Claims
**Section:** Keys to Victory (lines 466-482), The Bold Take (lines 448-450)
**Current:** Point estimates only (e.g., "middle-overs bowling economy could regress by 0.5-1.0 RPO")
**Required:** The 0.5-1.0 range in Keys to Victory #1 is good practice. Apply the same approach to other predictive claims. For instance, the Bold Take claims Noor Ahmad is more important than Gaikwad but does not quantify the counterfactual impact range. State: "Without Noor Ahmad, middle-overs economy would regress from 7.90 to approximately 8.01-8.50 (Chahar's 8.01 as floor, blended with uncapped replacements)."

### 11. Show League Average Denominators
**Section:** Team Batting Profile vs Bowling Types (lines 183-191)
**Current:** "League Avg SR" values given without sample sizes
**Required:** Show the aggregate ball count behind each league average. Example: "League Avg SR 144.9 (based on X00,000 balls)." This lets the reader assess whether individual player samples are meaningful against the benchmark.

### 12. Add Regression-to-Mean Caveat for Extreme Values
**Sections:** Mhatre 257.6 SR against fast bowling (line 314), Urvil Patel 212.5 SR (line 100), Kamboj death economy 6.00 (line 362)
**Current:** Numbers stated without volatility context
**Required:** For any stat based on fewer than 100 balls (or 10 overs for bowlers), add an explicit regression-to-mean caveat. Mhatre's 257.6 SR against fast bowling from 59 balls will almost certainly regress. Kamboj's 6.00 death economy from 0.5 overs (3 balls!) should not appear in a phase analysis table at all -- it is statistically meaningless.

---

## Minor Suggestions (Non-Blocking)

1. **Dhoni's "197 innings" vs "1965 balls" for death SR (The Story, line 26):** The Story section says "death-overs career SR of 176.5 remains elite across 197 innings." The Squad Table says "death SR 176.5 (1965 balls, HIGH)." Both could be correct (197 innings, 1965 balls), but showing both in the same document with different denominators is mildly confusing. Standardize to show balls with innings in parentheses.

2. **CSK's 2025 win rate in The Headline (line 14):** "4 wins in 14 matches" in The Story (line 20) vs "28.6% win rate" in The Headline (line 14). 4/14 = 28.57%, rounds to 28.6%. Correct, but consider showing the fraction alongside the percentage for transparency.

3. **"62.5% win rate in 2023" (By the Numbers, line 458):** This should be sourced. If CSK won 10/16, that's 62.5%. If the data window is different, state it.

4. **The "9,496 matches / 2.14M balls" header (line 5):** This is the total database size, not the CSK-specific data window. Consider adding the CSK-specific match count (e.g., "CSK data: X matches, Y balls") alongside the total database size. The current framing could mislead a casual reader into thinking all 9,496 matches involved CSK.

5. **Gaikwad's powerplay SR discrepancy:** The Tactical Blueprint (line 406) says Gaikwad's PP SR is 128.7. The Category Ratings (line 154) says CSK's PP batting SR is 137.2 (2025). The Off-Season section (line 34) says Gaikwad's 2025 SR improved to 148.8. These are likely different contexts (PP-specific vs all-phases vs career), but the proximity creates confusion. Label each with its phase and time window explicitly.

6. **Samson's PRESSURE_PROOF label (line 298):** The raw token "PRESSURE_PROOF" appears as a variable name, not a reader-friendly label. Consider rendering it as "Pressure-Proof" with a brief definition (e.g., "positive SR delta under high-pressure conditions").

7. **The 11-10 home record (line 245):** "52.4% win rate" -- 11/21 = 52.38%, rounds to 52.4%. Correct. But consider that ties/NR could affect this. If there were 24 matches at the venue but only 21 decided (W/L), state the denominator explicitly.

8. **Kamboj's death economy of 6.00 from 0.5 overs (line 362):** This is 3 balls. It should either be removed from the table entirely or flagged with a "DISCARD" or "N/A" note. Including it alongside 31-over and 102-over samples creates a false equivalence.

---

## Summary

The CSK season preview is a strong piece of analytical writing. The phase-level granularity, sample size discipline, and second-order thinking (setting vs chasing analysis, counterfactual impact modeling in the Bold Take) demonstrate genuine analytical sophistication. The SR/RPO distinction is handled correctly throughout.

However, five blocking errors prevent a score above 7.5:

1. Dube's ball count contradiction (ERROR-1) is the most serious -- an arithmetic impossibility that undermines trust in the data pipeline.
2. The H2H arithmetic errors (ERROR-2, ERROR-3) are embarrassing for a publication that claims "every claim above is backed by data."
3. The confidence label errors (ERROR-4) suggest either a classification bug or manual overrides without documentation.
4. The incoherent boundary percentage sentence (ERROR-5) indicates incomplete editing.

Fix these five blocking errors, implement changes 6-12, and the score reaches 8.5+. To reach 9.0, the Category Ratings methodology (change #9) and regression-to-mean caveats (change #12) are essential -- they transform the preview from excellent journalism with data backing into a document that meets publication-grade quantitative standards.

**Bottom line:** 7.2/10. Good work with specific, fixable defects. Not yet at the standard where I would sign off without revisions.

---

*Jose Mourinho | Quant Researcher | Cricket Playbook v5.0.0*
*Review conducted against thresholds.yaml v1.2.0 and generate_player_profiles.py classification system*
