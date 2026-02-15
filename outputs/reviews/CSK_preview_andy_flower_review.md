# CSK Season Preview -- Andy Flower Domain Review

**Reviewer:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-15
**Document Reviewed:** `outputs/season_previews/CSK_season_preview.md` (v1.0)
**Cross-Referenced Against:** `stat_packs/CSK/CSK_stat_pack.md`, `outputs/depth_charts/CSK_depth_chart.md`, `config/thresholds.yaml`

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Cricket Accuracy | 40% | 7.0/10 | 2.80 |
| Tactical Credibility | 30% | 8.0/10 | 2.40 |
| Sample Size Honesty | 20% | 8.0/10 | 1.60 |
| Domain Nuance | 10% | 7.5/10 | 0.75 |
| **Overall** | **100%** | | **7.55/10** |

---

## Factual Errors

### 1. Chepauk Venue Classification: "Spin Paradise" vs. Data's BALANCED Classification (MAJOR)

The preview describes Chepauk as a venue whose "reputation as a spin paradise is well earned" (Venue Analysis section) and later states Noor Ahmad's wrist-spin is amplified by the venue: "lower bounce, more grip, less boundary access for batters." The scouting report states Chepauk's conditions "amplify the bowling attack's effectiveness" in a spin context.

However, the stat pack's own pitch characteristics table (Section 4) classifies MA Chidambaram Stadium as **BALANCED** (Pace SR: 17.7, Spin SR: 20.1). A lower bowling strike rate for pace (17.7) than spin (20.1) actually means pace bowlers take wickets more frequently at Chepauk than spinners do. The venue is not spin-dominant by the data's own classification system.

The preview acknowledges "the data reveals a more nuanced picture" but then proceeds to build its entire venue thesis around spin advantage. This is a material inconsistency between the editorial narrative and the underlying data.

### 2. Khaleel Ahmed's Bowling Type: Left-Arm vs. Right-Arm

The preview (Keys to Victory, section 4) refers to Khaleel as the beneficiary of a role where Ellis takes death duty, giving "Khaleel Ahmed the freedom to focus on powerplay aggression." The scouting report labels him under "new-ball aggression." However, the depth chart classifies Khaleel as "Left-arm seam" while the stat pack lists his bowling type as "Fast-Medium" with batting hand "Right-hand." These are consistent. But the preview never once mentions that Khaleel is a **left-arm** seamer, which is a significant tactical detail, particularly when discussing matchups against right-handed batters in the powerplay. A professional coaching staff would immediately want to know the handedness of every bowler.

### 3. Noor Ahmad Middle-Overs Economy: 7.90 vs. 7.96 vs. 8.12 vs. 8.2 vs. 8.24

The preview cites multiple economy figures for Noor Ahmad that are inconsistently sourced:

- "7.90 economy across 102 overs" (Players to Watch, Scouting Report, repeated four times)
- The stat pack Section 6.2 shows: middle overs 7.9 econ, 101.8 overs (rounds to 7.90, consistent)
- The stat pack Section 10.3 (Spin Attack) shows Noor Ahmad at **8.2 middle-overs econ** (inconsistent with 7.90)
- The stat pack "Key Phase Players" table shows Noor Ahmad at **8.12 econ** in the middle, 204 balls (inconsistent again)
- The Venue Specialists table shows Noor Ahmad at Chepauk at **7.96 economy** (used correctly in the preview)
- Career economy listed in the preview as **8.24** across 132 overs matches the stat pack (8.24, 132.0 overs)

The discrepancy between 7.90 and 8.12/8.2 for the same phase needs resolution. These likely reflect different scoping (IPL career vs. since 2023, or different phase definitions). The preview must specify which scope produces which number. As it stands, the reader encounters 7.90 in the narrative and 8.12 in the Keys to Victory section's stat pack reference without explanation.

### 4. Noor Ahmad Death-Overs Economy: 7.65 vs. 8.54

The preview cites Noor Ahmad's death economy at **7.65** across 21.2 overs (Players to Watch, By the Numbers, Bold Take, Keys to Victory). However, the stat pack Section 10.4 (Death Bowling) shows Noor Ahmad at **8.4 death economy** (21.2 overs, 13 wickets), and the Key Phase Players table shows **8.54 death economy** (78 balls). The Section 6.2 phase distribution shows 7.65 economy at the death.

Again, this appears to be a scoping discrepancy (career vs. since-2023 vs. a different aggregation window), but it is material. The difference between 7.65 and 8.54 is almost a full run per over. A death economy of 7.65 for a wrist spinner is "genuinely rare" as the preview claims. A death economy of 8.54 is merely good. The claim built around this number ("the rarest skill in T20 cricket") may be overstated depending on which figure is correct.

### 5. Rahul Chahar's Career Overs: 82 vs. 239

The preview's depth buys table lists Rahul Chahar's middle-overs economy at "7.8 middle-overs econ across 239 overs (HIGH)." The stat pack Section 10.3 confirms 239 overs and 7.8 economy for the middle overs, but Section 6.1 lists his career IPL bowling as 81.7 overs total. The 239 overs figure includes **career data beyond the 2023-2025 window**, which is inconsistent with the preview's stated data window of "IPL 2023-2025." The stat pack's tactical insights section (Section 10) appears to use career-length data. The preview must clarify which data window applies.

### 6. Predicted XII Discrepancy with Depth Chart

The preview places Samson at #1 (opener), Mhatre at #2, and Gaikwad at #3 (anchor). The algorithmically generated depth chart places Gaikwad at #1, Mhatre at #2, and Samson at #3. The preview also includes Shivam Dube and Prashant Veer in the XI but excludes Aman Khan. The depth chart includes Aman Khan at #6 and excludes Dube from the starting formation entirely (Dube appears as the 4th option in the middle order depth chart).

This is not necessarily an error: editorial judgment can override algorithmic selection. But the preview states "The Founder's XII" without acknowledging the divergence from the depth chart algorithm. A footnote or explicit callout would maintain transparency.

### 7. Samson's Death-Overs Stats: 407 vs. 48 Innings

The preview cites Samson's death SR as "191.7 SR at the death (407 balls, MEDIUM)" and later "(48 innings, MEDIUM)." The stat pack confirms: 48 innings, 780 runs, 407 balls, 191.65 SR at the death. This is internally consistent, but the preview uses both "407 balls" and "48 innings" in different places without clearly distinguishing between them. In one instance (The Headline, paragraph 1), the preview writes "191.7 SR at the death (48 innings, MEDIUM)" which incorrectly pairs the innings count with the confidence label that corresponds to the ball count. Confidence labels are tied to ball counts per the thresholds system, not innings counts. This should be corrected to "(407 balls, MEDIUM)" for consistency.

### 8. Dhoni Death SR: 176.5 Career vs. 183.0 at Chepauk vs. 170.1 Since 2023

The preview uses three different Dhoni death SR figures without clearly distinguishing their scopes:

- 176.5 (1,965 balls) -- described as "death-overs career SR"
- 183.0 (241 balls) -- described as "at Chepauk" or "for CSK specifically"
- 170.1 (271 balls) -- described as career SR since 2023

The stat pack confirms: career death SR 176.49 (1,965 balls, HIGH), death SR at Chepauk specifically 154.62 (119 balls), overall SR since 2023 170.11 (271 balls). The 183.0 figure appears in the stat pack's Key Phase Players table (241 balls) but covers death-overs batting across all venues for CSK in the data window, not Chepauk-specific. The preview's scouting report states "183.0 SR at the death across 241 balls (for CSK specifically)" and then the Keys to Victory says "death SR (176.5 career, 183.0 at Chepauk)," incorrectly labeling the 183.0 figure as Chepauk-specific when it is a CSK team-context death SR across all venues.

---

## Strengths

### 1. Exceptional Structural Analysis
The three-season trajectory table (2023-2025) showing phase-by-phase batting SR and bowling economy decline is outstanding editorial work. It tells a story through numbers in a way that a professional coaching staff would immediately recognize and value. The year-on-year deltas are the right way to present regression data.

### 2. Opposition Blueprint Is Genuinely Useful
The scouting report's opposition blueprint ("Attack the powerplay, bowl off-spin in the middle overs, do not bowl pace to Dhoni at the death, do not bowl leg-spin to Samson") reads like a professional coaching briefing. This is precisely the kind of content that differentiates Cricket Playbook from generic previews.

### 3. The Bold Take Is Defensible and Well-Argued
The argument that Noor Ahmad is more important than Gaikwad is structurally sound. The logic (removing Gaikwad reshuffles the batting; removing Noor Ahmad collapses the bowling) is the kind of systems-level thinking a coaching staff would apply. The counterfactual reasoning is well-constructed.

### 4. Setting vs. Chasing Analysis
The innings-context analysis showing CSK bat 10.1 SR points better when setting is a genuinely useful insight that goes beyond surface-level statistics. The observation that they "struggle to find boundaries under chase pressure, not to rotate strike" shows someone has actually interrogated the dot ball data, not just the headline numbers.

### 5. Dhoni Pace-vs-Spin Split Analysis
The data insight on Dhoni's pace SR (198.8) versus leg-spin SR (112.8) is an excellent example of actionable intelligence. The editorial framing ("the slower the bowling, the more time he has to overthink") is both tactically sound and editorially compelling.

### 6. Sample Size Labels Are Mostly Well-Applied
The preview consistently uses HIGH/MEDIUM/LOW confidence labels with ball counts. The distinction between 780 balls (HIGH) and 93 balls (MEDIUM) is exactly how sample sizes should be communicated to readers. There are few instances of claims being made beyond what the data supports, with the exceptions noted in the errors section.

---

## Changes Required for 9.0+

### 1. Resolve the Chepauk Venue Classification Contradiction (BLOCKING)

**Section:** Venue Analysis, Scouting Report
**Current text:** "Chepauk's reputation as a spin paradise is well earned" / "lower bounce, more grip, less boundary access for batters"
**Problem:** The stat pack classifies Chepauk as BALANCED (Pace SR 17.7 vs. Spin SR 20.1). Pace bowlers actually take wickets more frequently than spinners at Chepauk since 2023.
**Required change:** Reframe the venue analysis to acknowledge the BALANCED classification. The low-scoring nature of Chepauk is well-supported by the RPO data (7.47 middle-overs RPO vs. 8.89 league). The venue suppresses scoring across both pace and spin, with pace arguably more effective by wicket-taking metrics. The editorial narrative should focus on Chepauk as a **low-scoring ground** rather than a **spin-friendly ground**. This is still favorable for CSK's bowling attack (Noor Ahmad, Khaleel) but for different reasons than currently stated. The claim about "lower bounce, more grip" should either be supported by pitch condition data or removed as speculative.

### 2. Reconcile Noor Ahmad Economy Figures Across the Preview (BLOCKING)

**Section:** Players to Watch, Keys to Victory, Bold Take, By the Numbers, Scouting Report
**Current text:** Death economy cited as 7.65 in narrative, 8.54 in stat pack Key Phase Players.
**Problem:** The reader encounters 7.65 in six different places, but the stat pack's tactical section shows 8.4/8.54 for the same phase. If 7.65 is the correct career figure and 8.54 is the IPL-since-2023 figure, both are valid but the preview must specify scope.
**Required change:** Add a parenthetical or footnote the first time 7.65 is used, clarifying the data window. Example: "7.65 economy in death overs (career, 21.2 overs)" versus "8.54 (IPL 2023-2025, 13 overs)." If the preview's stated data window is IPL 2023-2025, the 8.54 figure should be the primary citation and 7.65 should be framed as career context. The "rarest skill in T20 cricket" claim should be re-evaluated against the 8.54 figure.

### 3. Include Khaleel Ahmed's Bowling Hand Throughout (HIGH PRIORITY)

**Section:** All references to Khaleel Ahmed
**Current text:** "Khaleel Ahmed's new-ball aggression" / "Khaleel opens"
**Problem:** Khaleel is a left-arm seamer. This is a material tactical detail. The preview never mentions his bowling hand.
**Required change:** First reference should read "Khaleel Ahmed, left-arm seamer" or equivalent. Subsequent references to his tactical role should note the angle and matchup implications against right-handed batters. At a professional level, the left-arm angle in the powerplay is a specific tactical weapon, particularly at Chepauk where the pitch may offer seam movement. This is exactly the kind of detail a coaching staff would foreground.

### 4. Correct the 183.0 Chepauk Label for Dhoni (HIGH PRIORITY)

**Section:** Keys to Victory (point 3), Scouting Report
**Current text:** "death SR (176.5 career, 183.0 at Chepauk)"
**Problem:** 183.0 is Dhoni's death SR for CSK across all venues (241 balls), not Chepauk-specific. The stat pack shows his Chepauk SR as 154.62 across 119 balls.
**Required change:** Correct to "183.0 SR at the death (CSK career, all venues, 241 balls)" or cite the actual Chepauk figure (154.62 SR, 119 balls). If the 154.62 figure is used, the narrative about Dhoni's death-overs value at Chepauk specifically needs to be reconsidered, as it is materially lower than the all-venue figure.

### 5. Address the Predicted XII Discrepancy with the Depth Chart (MEDIUM PRIORITY)

**Section:** Full Squad Table, Tactical Blueprint
**Current text:** "The Founder's XII" with Samson opening, Gaikwad at #3, Dube at #5, Prashant Veer at #6
**Problem:** The algorithmically generated depth chart has Gaikwad opening, Samson at #3, Aman Khan at #6, and Dube outside the starting XI. These are significantly different selections.
**Required change:** Add a brief editorial note acknowledging the divergence. Example: "Note: The algorithmic depth chart (v2.0) produces a different XI with Gaikwad opening, Samson at #3, and Aman Khan at #6. The Founder's XII reflects editorial judgment on optimal deployment, particularly the decision to move Gaikwad to #3 where his middle-overs SR of 142.5 is better utilized." This maintains transparency without undermining editorial authority.

### 6. Strengthen the Off-Spin Vulnerability Analysis (MEDIUM PRIORITY)

**Section:** Team Batting Profile, Scouting Report
**Current text:** "Gaikwad at 125.0 (40 balls, LOW), Dube at 117.98 (89 balls, MEDIUM). It's a meaningful sample for Dube..."
**Problem:** Gaikwad's 40-ball sample against off-spin is labeled LOW and correctly so. But the preview then groups both figures together to declare "off-spin is the weapon" for opposition teams. A professional coaching staff would not build a bowling plan around a 40-ball sample from one batter. Dube's 89-ball MEDIUM sample is more defensible but still below the 100-ball threshold for full-weight vs-bowling-type analysis per the thresholds file (rankings.sample_size_targets.vs_bowling_type: 100).
**Required change:** Lead with Dube's MEDIUM-sample vulnerability as the primary evidence. Note Gaikwad's LOW-sample figure as directional but unconfirmed. The conclusion ("off-spin is the weapon") should be qualified: "Off-spin appears to be the matchup to target, primarily through Dube (117.98 SR, 89 balls, MEDIUM). Gaikwad's 125.0 SR against off-spin (40 balls, LOW) is suggestive but requires a larger sample to confirm."

### 7. Correct the Samson Innings/Balls Confidence Label Pairing (MINOR)

**Section:** The Headline (paragraph 1)
**Current text:** "191.7 SR at the death (48 innings, MEDIUM)"
**Problem:** Confidence labels correspond to ball counts, not innings counts. 48 innings = 407 balls = MEDIUM.
**Required change:** Change to "191.7 SR at the death (407 balls, MEDIUM)" for consistency with the thresholds system. The innings count can be provided separately if desired.

### 8. Clarify Rahul Chahar's Data Window (MINOR)

**Section:** Auction Strategy depth buys table
**Current text:** "7.8 middle-overs econ across 239 overs (HIGH)"
**Problem:** 239 overs appears to be career-length data, not the preview's stated 2023-2025 window. His IPL career since 2023 is only 81.7 overs total.
**Required change:** Either clarify the data window ("7.8 middle-overs economy, career, 239 overs, HIGH") or use the 2023-2025 figure from the stat pack (8.01 economy, 69 overs, HIGH) to maintain consistency with the rest of the preview.

### 9. Add Gurjapneet Singh to the Bowling Discussion (MINOR)

**Section:** Bowling Deployment
**Current text:** No mention of Gurjapneet Singh in the bowling deployment or bowler phase distribution.
**Problem:** Gurjapneet Singh is retained at 2.20 Cr (third-highest among bowlers after Noor Ahmad and Khaleel). He is described as "LF depth" in the Squad Table but is completely absent from the bowling deployment section. At 2.20 Cr, the franchise clearly values him as more than bench depth.
**Required change:** Add a brief mention in the bowling deployment section or the Players Who Need to Step Up section. Even if he is uncapped, the price tag warrants acknowledgment.

### 10. Address Noor Ahmad's Bowling Type Correctly (MEDIUM PRIORITY)

**Section:** The Headline, multiple references
**Current text:** "a 20-year-old Afghan left-arm wrist spinner"
**Problem:** The stat pack classifies Noor Ahmad as "Wrist-spin" with batting hand "Right-hand." Left-arm wrist spin is correct (he bowls chinaman/left-arm unorthodox). However, the term "wrist spinner" is used interchangeably with references to his operating in the middle overs alongside Rahul Chahar (leg-spin). A professional coaching staff would want the specific bowling type noted consistently: Noor Ahmad bowls left-arm wrist spin (chinaman), which means he turns the ball away from right-handers and into left-handers. This is tactically distinct from right-arm leg-spin (Chahar) and matters for matchup analysis. The preview never explains this distinction.
**Required change:** On first reference, specify "left-arm wrist spinner (chinaman)" and note the directional implications for matchups. When discussing Noor Ahmad alongside Chahar, note that their spin goes in opposite directions, which is tactically significant for the batting opposition.

---

## Minor Suggestions (Non-Blocking)

1. **Em-dash usage:** The preview uses em dashes extensively (e.g., "the death-overs enforcer" on line 36, "a batter who strikes at 151.0" on line 26). The Content Language Guide explicitly bans em dashes: "No em dashes. Do not use em dashes (---). Use commas, colons, or full stops instead." This is a tone compliance issue for Virat Kohli's review, but I flag it here because several em dashes appear within cricket-analytical sentences where they could distort reading flow. A full pass for em-dash removal is needed.

2. **Pathirana in the "experienced Indian all-rounders" parenthetical:** The Team Style Analysis section lists "Jadeja, Bravo, Pathirana" as "experienced Indian all-rounders." Matheesha Pathirana is Sri Lankan. Dwayne Bravo is Trinidadian. Only Jadeja is Indian. This is a factual error in categorization, though the broader point about experienced all-rounders is valid.

3. **Dhoni's age consistency:** The preview states Dhoni is 43. He was born July 7, 1981. At the time of IPL 2026 (likely April-June 2026), he would be 44. The preview was written in February 2026 when he would be 44 (having turned 44 in July 2025). This should be verified and corrected if necessary.

4. **"Five titles" claim:** The Headline states "Five titles." CSK have won the IPL in 2010, 2011, 2018, 2021, and 2023. This is correct.

5. **PBKS Win%:** The head-to-head table shows PBKS at "50.0%" but the record is 16W-15L-1NR, which is 51.6% wins out of decided matches or 50.0% out of total matches. The stat pack confirms 50.0% which is calculated as wins/total matches. This is consistent but worth noting that the calculation method differs from the other entries (which don't have NR matches).

6. **"Front office fire sale" analogy:** The Content Language Guide permits cross-sport analogies. This one works. However, a "fire sale" implies deliberate dumping for value, whereas Conway/Pathirana/Jadeja departures were retention-era decisions. The analogy could be more precise: "the cricketing equivalent of roster turnover forced by the retention window."

---

## Summary Assessment

This is a good season preview. The analytical depth is genuine, the phase-by-phase framework is rigorous, and the tactical recommendations would hold up in a professional coaching meeting. The writing is confident and data-anchored.

The primary concern is the Chepauk venue classification contradiction. The preview builds a significant portion of its tactical thesis ("CSK's bowling attack is built for it" at Chepauk) on the premise that Chepauk is spin-friendly, when the data classifies it as BALANCED with pace actually more effective by wicket-taking strike rate. This does not invalidate the broader argument (Chepauk is low-scoring, which benefits CSK's bowling), but it requires reframing.

The secondary concern is the inconsistent economy figures for Noor Ahmad across different sections, which undermines reader confidence in the data integrity even though the underlying stats are likely correct under different scoping assumptions.

At 7.55/10, this preview is solidly above average but needs the venue analysis correction, the Noor Ahmad figure reconciliation, and the Dhoni Chepauk label fix to reach 9.0+. Those three changes alone would push the Cricket Accuracy score from 7.0 to 8.5+, and the overall from 7.55 to approximately 8.4. The remaining items would bring it above 9.0.

---

*Review completed: 2026-02-15*
*Andy Flower, Cricket Domain Expert*
*Cricket Playbook v5.0.0*
