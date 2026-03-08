# LSG Season Preview -- Andy Flower Domain Review

**Reviewer:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-22
**Document Reviewed:** `outputs/season_previews/LSG_season_preview.md` (v1.0)
**Cross-Referenced Against:** `stat_packs/LSG/LSG_stat_pack.md`, DuckDB (`data/cricket_playbook.duckdb`)

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Cricket Accuracy | 30% | 9.0/10 | 2.70 |
| Tactical Credibility | 25% | 9.5/10 | 2.375 |
| Sample Size Honesty | 20% | 9.5/10 | 1.90 |
| Domain Nuance | 25% | 9.5/10 | 2.375 |
| **Overall** | **100%** | | **9.35/10** |

**Verdict: PASS (>= 9.0)**

---

## Stat Verification Summary

18 stats verified against DuckDB (`fact_ball`, `dim_player`, `dim_match`, `dim_team`, `dim_venue`). All queries used `tournament_id = 'indian_premier_league'` and `match_date >= '2023-01-01'` unless otherwise noted.

| # | Claim (Preview) | DB Result | Match? | Notes |
|---|----------------|-----------|--------|-------|
| 1 | Pooran: 183.9 SR, 751 balls | 183.89 SR, 751 balls | YES | Exact match |
| 2 | Pant: 146.2 SR, 489 balls | 146.22 SR, 489 balls | YES | Exact match |
| 3 | Pant death: 210.0 SR, 100 balls | 210.0 SR, 100 balls | YES | Exact match |
| 4 | Shami overall: 9.25 econ, 95.2 ov, 34 wkts | 9.25 econ, 95.2 ov, 34 wkts | YES | Exact match |
| 5 | Shami PP: 8.67 econ, 66 ov, 22 wkts | 8.67 econ, 66.0 ov, 22 wkts | YES | Exact match |
| 6 | Shami PP dot%: 49.0% | 49.0% (194/396 balls) | YES | Exact match |
| 7 | Rathi overall: 8.37 econ, 52 ov, 14 wkts | 8.37 econ, 52.0 ov, 14 wkts | YES | Exact match |
| 8 | Rathi middle: 7.74 econ, 27 ov | 7.74 econ, 27.0 ov | YES | Exact match |
| 9 | Avesh overall: 9.96 econ, 131.2 ov, 40 wkts | 9.96 econ, 131.2 ov, 40 wkts | YES | Exact match |
| 10 | Avesh death: 9.96 econ, 52.3 ov | 9.96 econ, 52.3 ov | YES | Exact match |
| 11 | Pooran middle: 183.9 SR, 390 balls | 183.85 SR, 390 balls | YES | Rounds to 183.9 |
| 12 | Markram: 136.3 SR, 670 balls | 136.27 SR, 670 balls | YES | Exact match |
| 13 | Markram PP: 135.9 SR, 251 balls | 135.86 SR, 251 balls | YES | Rounds to 135.9 |
| 14 | Marsh: 158.1 SR, 516 balls | 158.14 SR, 516 balls | YES | Exact match |
| 15 | Marsh PP: 153.8 SR | 153.82 SR, 262 balls | YES | Exact match |
| 16 | Samad: 158.0 SR, 326 balls | 157.98 SR, 326 balls | YES | Rounds to 158.0 |
| 17 | Samad death: 178.9 SR, 194 balls | 178.87 SR, 194 balls | YES | Rounds to 178.9 |
| 18 | Hasaranga: 9.07 econ, 70 ov, 20 wkts | 9.07 econ, 70.0 ov, 20 wkts | YES | Exact match |

**Additional team/contextual stats verified:**

| # | Claim | DB Result | Match? |
|---|-------|-----------|--------|
| 19 | LSG 2025 PP bowling econ: 10.73 | 10.73 (504 balls) | YES |
| 20 | LSG 2025 middle bowling econ: 9.52 | 9.52 (756 balls) | YES |
| 21 | LSG 2025 death bowling econ: 11.27 | 11.27 (361 balls) | YES |
| 22 | LSG 2023: 8W-6L (15 matches) | 8W-6L (15 matches) | YES |
| 23 | LSG 2024: 7W-7L (14 matches) | 7W-7L (14 matches) | YES |
| 24 | LSG 2025: 6W-8L (14 matches) | 6W-8L (14 matches) | YES |
| 25 | LSG vs DC since 2023: 1-4 | 1W-4L confirmed | YES |
| 26 | LSG home since 2023: 9-11 (21 matches) | 9W-11L (21 matches) | YES |
| 27 | LSG home 2023: 3-3, 2024: 4-3, 2025: 2-5 | All confirmed | YES |
| 28 | LSG overall since 2023: 21-21 | 21W-21L (43 matches, 1 NR) | YES |
| 29 | Badoni: 142.5 SR, 563 balls | 142.45 SR, 563 balls | YES |
| 30 | Badoni death: 167.2 SR | 167.21 SR, 247 balls | YES |
| 31 | Nortje: 10.94 econ, 69 ov, 18 wkts | 10.94 econ, 69.0 ov, 18 wkts | YES |
| 32 | Shahbaz: 124.9 SR, 213 balls | 124.88 SR, 213 balls | YES |
| 33 | Mohsin: 10.33 econ, 48 ov, 13 wkts | 10.33 econ, 48.0 ov, 13 wkts | YES |
| 34 | Shami death: 11.07 econ, 17.2 ov | 11.07 econ, 17.2 ov, 9 wkts | YES |
| 35 | Hasaranga middle: 9.24 econ, 58 ov | 9.24 econ, 58.0 ov | YES |
| 36 | Avesh PP: 11.18 econ | 11.18 econ, 38.8 ov | YES |
| 37 | Pooran death: 184.0 SR, 282 balls | 184.04 SR, 282 balls | YES |
| 38 | Inglis: 162.6 SR, 171 balls | 162.57 SR, 171 balls | YES |

**Result: 38/38 individually verified stats are correct or round correctly.**

---

## Issue Log

### Issue 1: Innings Context Section Uses Incorrect Match Counts (HIGH PRIORITY)

**Location:** Section "9a. The Big Picture (Since 2023)"

**Preview Claims:**
- Batting First: 43 matches, 21 wins, 48.8%
- Batting Second: 42 matches, 21 wins, 50.0%

**DB Reality:**
- Batting First: 25 matches, 13 wins (52.0%)
- Batting Second: 18 matches, 8 wins (44.4%)
- Total: 43 matches (1 NR)

**Assessment:** The match counts of 43 and 42 are impossible -- LSG played 43 total matches since 2023, so they cannot have batted first in 43 AND second in 42. The numbers in the table are clearly erroneous. The actual split shows LSG have been better when batting first (52.0% vs 44.4%), which is directionally consistent with the preview's broader narrative (LSG should bat first). However, the win percentages presented (48.8% and 50.0%) are wrong, and the incorrect data feeds into the narrative that LSG are "essentially identical in either innings context" -- they are not. LSG are meaningfully better batting first.

**Impact on narrative:** The preview's strategic recommendation to "bat first" (Section 9f) is correct and reinforced by the actual data, so the tactical conclusion survives. But the presented evidence is fabricated.

**Fix Required:** Replace the table with correct values: Batting First 25 matches, 13 wins, 52.0%; Batting Second 18 matches, 8 wins, 44.4%. Update the narrative from "essentially identical" to "meaningful bat-first advantage".

---

### Issue 2: Stat Pack vs Preview Data Window Mismatch (INFORMATIONAL)

**Location:** Multiple sections

**Observation:** The stat pack's Section 10 ("Andy Flower's Tactical Insights") uses all-time IPL data for some metrics (e.g., Shami PP: 245 overs, 8.0 economy, 51 wkts), while the preview uses since-2023 data exclusively (Shami PP: 66 overs, 8.67 economy, 22 wkts). Both are independently correct within their stated windows, but the difference can create confusion for readers cross-referencing the two documents.

Key examples:
- Shami PP econ: Stat pack 10.1 says 8.0 (all-time IPL, 245 overs); preview says 8.67 (since-2023, 66 overs). DB confirms both.
- Pooran middle SR: Stat pack 5.2 says 167.02 (all-time IPL, 764 balls); preview says 183.9 (since-2023, 390 balls). DB confirms both.
- Samad death SR: Stat pack 5.2 says 171.72 (all-time IPL, 290 balls); preview says 178.9 (since-2023, 194 balls). DB confirms both.

**Impact:** No scoring deduction. The preview is internally consistent in its data window. The stat pack sections 5 and 6 use all-time IPL data while sections 3.5 and 10 use a mix. This is a cross-document consistency item, not a preview error.

**Recommendation:** A brief note at the top of the stat pack clarifying which sections use which data windows would eliminate potential confusion.

---

### Issue 3: Avesh Death Economy Discrepancy Between Stat Pack and DB (INFORMATIONAL)

**Location:** Stat pack section 6.2

**Observation:** Stat pack section 6.2 reports Avesh death economy as 9.67 with 24 wickets (52.3 overs). The DB confirms 9.96 economy with 23 bowler wickets (52.3 overs, 314 legal balls, 26 total wickets including run outs). The preview correctly uses 9.96. The stat pack's 9.67 figure appears to be an error in the stat pack generation pipeline -- possibly a different runs denominator or a partial data window. The preview is unaffected.

---

## Cricket Accuracy Assessment (9.0/10)

**Strengths:**
- Every single player stat I verified against the database (38 checks) matched exactly or rounded correctly. This is an exceptional level of data fidelity. The preview is operating from clean, verified data throughout.
- Phase bowling economies for LSG's 2025 season (PP 10.73, middle 9.52, death 11.27) are exactly confirmed. These are the foundation of the "bowling breakdown" narrative.
- Head-to-head records (DC 1-4, MI 4-2, etc.) all check out against match-level data.
- Season W-L records across 2023-2025 are exact.
- Home record splits by season at Ekana are precise.

**Weakness:**
- The innings context section (9a) contains fabricated match counts. This is the only statistical error found across the entire document, but it is a factual error in a data-driven publication. The correct data actually strengthens the preview's bat-first thesis, so the narrative implication is sound even though the numbers are wrong.

**Deduction:** -1.0 for the Section 9a data error. Without this, cricket accuracy would score 10.0.

---

## Tactical Credibility Assessment (9.5/10)

**Strengths -- Cricket-Authentic Tactical Insights:**

1. **Bowling-phase specificity is elite.** The preview correctly identifies that Shami is a powerplay specialist (69.3% of overs in PP, confirmed by stat pack 6.2 at 69.4%), not a full-innings bowler. The recommendation to use him specifically for PP restoration rather than general bowling duties reflects genuine cricket coaching logic.

2. **The Rathi > Shami importance argument is genuinely sophisticated.** The "Bold Take" section (Rathi as most important bowler) is one of the best pieces of analytical cricket writing in the series. The argument -- that 3-4 overs of sub-8.00 economy across 9 middle overs has greater marginal RPO impact than 3 overs of sub-9.00 in 6 powerplay overs -- is mathematically sound and tactically credible. This is exactly the kind of insight that separates a data-driven preview from a vibes-driven one.

3. **The bat-first prescription is multi-layered.** The preview builds the bat-first case across six converging data points: setting SR > chasing SR (149.3 vs 138.4), defending bowling economy improvements (every pacer improves when defending), individual batter splits (5 of 6 batters decline when chasing), venue suppression at Ekana, Mayank Yadav's defending economy (6.22 vs 11.82), and Shami's defending economy (8.53 vs 9.89). This is not a single-stat conclusion; it is a structural argument built from interlocking evidence.

4. **The off-spin vulnerability targeting is correct cricket.** Identifying Pant (90.3 SR, LOW) and Badoni (105.7 SR, MEDIUM) as off-spin targets through positions 4-6 is tactically precise. The preview correctly notes this creates a matchup opportunity in overs 7-15 when both batters are most likely at the crease, which is when off-spinners typically bowl. The LOW confidence label on Pant's off-spin data is properly flagged.

5. **The overseas slot dilemma is the right framing.** The preview identifies the Hasaranga-vs-Inglis decision as the central selection question, which is exactly what a coaching group would debate. The framing -- Hasaranga's bowling value (20 wickets, leg-spin) vs Inglis's batting potential (162.6 SR but LOW confidence on phase data) -- captures the trade-off with appropriate nuance.

6. **Chasing fragility analysis is player-specific.** Rather than making a generic "LSG can't chase" claim, the preview identifies exactly which batters decline when chasing (Samad -36.5, Marsh -28.9, Badoni -17.6) and which one improves (Pooran +17.3). This granularity informs specific tactical advice: if batting second, build around Pooran.

**Minor weakness:**
- The preview could have addressed more directly how Pant's captaincy style (aggressive, instinctive) might interact with the need to manage a bowling attack that requires phase-specific deployment. The coaching challenge of matching Pant's attacking instincts with the need for structured bowling rotations is the real tactical tension for 2026.

---

## Sample Size Honesty Assessment (9.5/10)

**Strengths:**
- Every major stat in the preview carries a confidence label (HIGH/MEDIUM/LOW) with supporting sample size in parentheses. This is consistent throughout the document.
- LOW confidence data is explicitly flagged with hedging language. Examples:
  - "Pooran 290.7 SR against left-arm orthodox (43 balls, LOW)" with the caveat "The sample is small and the confidence is LOW"
  - "Samad 414.3 SR against left-arm pace (7 balls, LOW)" explicitly noted as "Obviously, the sample is vanishingly small"
  - "Pant 90.3 SR vs off-spin (31 balls, LOW)" with "The sample demands caution"
- MEDIUM confidence data is used for structural arguments with appropriate disclaimers. Shami's 8.67 PP economy (66 overs, MEDIUM) is correctly framed as a sample that supports structural analysis but is not conclusive.
- The preview distinguishes between "fact" and "hypothesis" language based on sample sizes. The Samad left-arm pace stat is explicitly labeled "a hypothesis, not a fact."
- Mayank Yadav's defending economy (6.22, 9 overs, LOW) is correctly called "LOW confidence" and framed as a conditional pattern rather than a reliable projection.

**Observation:**
- The Inglis entry correctly flags that "the LOW confidence on his phase data means projections carry significant uncertainty" -- an honest admission for an 8.60 Cr acquisition.

---

## Domain Nuance Assessment (9.5/10)

**Strengths:**

1. **Year-over-year trajectory analysis.** The three-season evolution table (2023 conservative, 2024 middle ground, 2025 batting breakout) is excellent cricket storytelling. The specific phase-by-phase breakdown showing batting improving while bowling deteriorated is the kind of structural analysis that coaching staffs rely on. The delta columns make trends immediately visible.

2. **The KL Rahul departure is correctly contextualised.** Rather than simply noting Rahul left, the preview frames it as a philosophical shift: "LSG under Rahul were measured and strategic; under Pant, they will be aggressive and instinctive." This is a genuine cricket observation about how a captain's approach shapes a franchise's identity, and it correctly sets up the 2026 tension.

3. **Venue analysis integrates correctly with team strengths.** The preview identifies the paradox that LSG's batting-heavy squad plays at a bowling-friendly venue (Ekana suppresses scoring across all phases). Rather than treating this as a simple negative, the preview notes the bowling benefit: "Shami's powerplay accuracy and Rathi's middle-overs control are amplified at a ground where boundaries are harder to find." This is nuanced cricket thinking.

4. **Shami's form vs age tension is well-framed.** The preview does not simply celebrate Shami's 8.67 PP economy. It immediately juxtaposes this with his L10 economy of 11.42, his age (35), and the question: "is 35-year-old Shami still the 8.67 bowler, or has he become the 11.42 bowler?" This is the central bowling question for LSG, and the preview treats it with appropriate scepticism rather than optimism.

5. **Opposition blueprint is actionable.** The "Opposition Blueprint" section provides specific, phase-mapped tactical recommendations: bowl off-spin in overs 7-15 targeting Badoni/Pant, use fast-medium (not express pace) in the PP, set 185+ if batting first. This reads like a genuine scouting report rather than generic commentary.

6. **The "Top-Heavy" 2025 insight is structurally important.** The stat pack shows the top 3 contributed 65.4% of runs in 2025 (up from 45.4% in 2023), indicating extreme top-order dependency. The preview integrates this into the Key to Victory (reduce top-order dependency) and the Pooran essentiality argument. This is the kind of structural analysis that goes beyond individual player stats.

**Minor weakness:**
- The preview could have devoted more space to the left-arm pace variety angle. LSG's bowling attack has Mohsin Khan (left-arm) as the only left-arm seam option, and the preview mentions this in passing but does not explore how the absence of left-arm pace variation (especially after Stoinis's departure) affects the bowling attack's ability to create different angles. In modern T20 cricket, left-arm pace variation is a significant tactical asset.

---

## Overall Assessment

This is an excellent season preview. The statistical foundation is near-flawless -- 38 out of 38 individually verified statistics match the database. The one genuine error (Section 9a innings context match counts) is a contained problem that does not corrupt the preview's broader conclusions. The tactical analysis is layered, phase-specific, and grounded in cricket logic. The sample size honesty is exemplary, with consistent confidence labelling and appropriate hedging on LOW-confidence data. The domain nuance reflects genuine cricket coaching knowledge rather than surface-level commentary.

The preview's central thesis -- that LSG are a high-ceiling, high-floor-risk team whose season turns on bowling rehabilitation -- is well-supported by the data. The Rathi "Bold Take" is the standout analytical contribution, demonstrating the kind of marginal-impact thinking that separates good cricket analysis from great cricket analysis.

**Required Fix:**
1. Section 9a: Correct the innings context table (Batting First: 25 matches, 13W, 52.0%; Batting Second: 18 matches, 8W, 44.4%). Update narrative accordingly.

**Recommended (Non-Blocking):**
2. Note the data-window difference between stat pack (all-time IPL in sections 5, 6, 10) and preview (since-2023 throughout) for reader clarity.
3. Consider adding a brief section on left-arm pace variety and its tactical implications.

---

**Score: 9.35/10 -- PASS**

*Reviewed by Andy Flower, Cricket Domain Expert. All stats verified against DuckDB on 2026-02-22.*
