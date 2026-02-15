# Stat Pack Editorial Review — TKT-240

**Date:** 2026-02-15
**Reviewers:** Virat Kohli (Tone & Narrative Guard) + Andy Flower (Cricket Domain Expert)
**Scope:** All 10 IPL team stat packs at `stat_packs/{TEAM}/`
**Task Integrity Loop:** Step 3 (Domain Sanity)

---

## Executive Summary

All 10 stat packs follow a consistent 13-section structure and deliver substantial analytical depth. The data tables are well-formatted, phase-wise analysis is comprehensive, and newer sections (Pressure Performance, Cross-Tournament Intelligence, Uncapped Watch) add genuine insight beyond what fans can find elsewhere.

However, the review uncovered **systemic boilerplate contamination** that violates the Phil Steele Rule. Section 3.5 "Keys to Victory" and Section 10.6 "Tactical Summary" contain identical template text across all 10 teams. Additionally, cross-team player data contamination was found in 2 stat packs (RCB, LSG), and several cricket-domain inaccuracies exist where generic bowling phrases are applied to spinners.

**Overall Quality Verdict:** 6.8/10 — Solid analytical foundation with structural and data integrity, but the boilerplate problem significantly undermines the "pro team prep for public consumption" promise. These stat packs currently read like generated reports, not editorial products.

---

## Per-Team Scores

| Team | Tone (1-10) | Accuracy (1-10) | Presentation (1-10) | Avg | Notes |
|------|-------------|------------------|----------------------|-----|-------|
| **CSK** | 7 | 7 | 7 | 7.0 | Empty Economy Rate Evolution table (Section 3). Boilerplate Keys/Summary. |
| **MI** | 7 | 8 | 7 | 7.3 | Cleanest data. Bumrah stats are impressive and correctly highlighted. Boilerplate Keys/Summary. |
| **KKR** | 5 | 5 | 7 | 5.7 | **Worst accuracy.** Summary says "no glaring gaps" after listing under-par in ALL phases. Narine "yorker accuracy" is cricket-inaccurate. |
| **RR** | 7 | 7 | 7 | 7.0 | Solid. Sandeep Sharma described as "reliable" death bowler at 10.64 economy is generous. Boilerplate. |
| **DC** | 7 | 7 | 7 | 7.0 | Kuldeep Yadav "yorker accuracy" is cricket-inaccurate (he is a wrist spinner). No boilerplate closing (only team). |
| **SRH** | 7 | 7 | 7 | 7.0 | JD Unadkat "yorker accuracy" is appropriate (he is a left-arm seamer). Boilerplate closing. |
| **PBKS** | 7 | 7 | 7 | 7.0 | Arshdeep "yorker accuracy" is appropriate. Boilerplate Keys/Summary. |
| **GT** | 6 | 6 | 7 | 6.3 | Section 10.3 only lists 1 pacer (Arshad Khan) despite Rabada, Siraj, Prasidh in squad. Boilerplate. |
| **LSG** | 6 | 5 | 7 | 6.0 | **PWH de Silva** appears in bowling data and tactical analysis but is NOT in the LSG 2026 squad — cross-contamination. DS Rathi "yorker accuracy" is inaccurate (leg-spinner). |
| **RCB** | 6 | 5 | 7 | 6.0 | **MP Yadav** (Mayank Yadav, LSG player) appears in Phase Distribution and Tactical Analysis — cross-contamination. Hazlewood "yorker accuracy" is appropriate. |

**Cross-Team Average:** Tone 6.5 | Accuracy 6.4 | Presentation 7.0 | **Overall 6.6**

---

## Top Issues (Prioritized)

### CRITICAL — Cross-Team Player Data Contamination

**Issue C1: MP Yadav (Mayank Yadav) in RCB stat pack**
- **File:** `stat_packs/RCB/RCB_stat_pack.md`
- **Lines:** 377-379 (Phase Distribution), 616-619 (Tactical Insights Section 10.3)
- **Problem:** Mayank Yadav is an LSG squad player, not RCB. His bowling data (PP: 12.0 econ, Middle: 7.73, Death: 6.95) appears in RCB's phase distribution table AND Section 10.3 where he is called "the designated death option at 7.0 economy."
- **Impact:** A reader relying on this stat pack would believe RCB has a 150kph death bowling specialist they do not have. This is a factual error that undermines the entire stat pack's credibility.
- **Severity:** CRITICAL — DO NOT SHIP as-is
- **Fix:** Remove MP Yadav rows from Section 6.2 and rewrite Section 10.3 pace attack intelligence without him. Generator script bug in `scripts/generators/stat_pack_generator.py` likely filtering by bowling data rather than squad roster.

**Issue C2: PWH de Silva in LSG stat pack**
- **File:** `stat_packs/LSG/LSG_stat_pack.md`
- **Lines:** 296-297 (Venue Specialists), 402-404 (Phase Distribution), 644 (Tactical Insights), 758-761 (Pressure bowling)
- **Problem:** Wanindu Hasaranga de Silva (PWH de Silva) is listed extensively in LSG bowling analysis. He played for RCB previously and is listed in LSG's 2026 squad. *However*, the data volume (70 overs, 20 wickets in Phase Distribution) suggests this includes non-LSG historical data bleeding into the LSG pack.
- **Impact:** Statistical data may be inflated with matches played for other franchises.
- **Severity:** CRITICAL — needs investigation. If de Silva IS in the LSG squad, the data still may include non-LSG matches incorrectly attributed.

### MAJOR — Systemic Boilerplate Violations

**Issue M1: Identical Section 10.6 Tactical Summary across 9/10 teams**
- **Files:** All stat packs except DC
- **Text:** *"The data suggests a well-rounded squad with no glaring tactical gaps. The coaching priority should be maintaining peak performance levels across phases and ensuring tactical flexibility for different match situations. Roster management and workload planning across the tournament will be the real differentiator."*
- **Problem:** This identical closing paragraph appears in 9 of 10 stat packs. It is generic boilerplate that says nothing team-specific. Worse, for KKR, it directly contradicts the analysis in Section 10.6 that flags "under-par" performance in ALL three batting phases.
- **Impact:** Violates the Phil Steele Rule ("Every section must answer at least one question the average fan doesn't know how to ask yet"). A reader who opens two team packs will immediately notice they have the same closing paragraph. Destroys editorial credibility.
- **Severity:** MAJOR — requires rewrite by Virat Kohli or Tom Brady for each team with team-specific tactical conclusions.

**Issue M2: Identical "Keys to Victory" template (Section 3.5)**
- **Files:** All 10 stat packs
- **Pattern:** All 7 keys follow the same template:
  1. "Powerplay aggression from [PLAYER] — [stat] sets the tone; need early intent without reckless wicket loss."
  2. "[BOWLER] must control the new ball — [stat]; early breakthroughs are non-negotiable."
  3. "Middle-overs accumulation through [PLAYER1] and [PLAYER2] — building partnerships in overs 7-15..."
  4. "[BOWLER] must squeeze in the middle — [stat]; choking run flow here builds scoreboard pressure."
  5. "Death hitting from [PLAYER] — [SR] in overs 16-20; maximizing the last 5 overs is the difference between 170 and 190+."
  6. "[BOWLER]'s [adjective] death bowling — [economy] at the death; **defending totals requires yorker accuracy and nerve under pressure.**"
  7. "Reduce top-order dependency — top 3 contributed [X]% of runs in 2025; middle order must step up..."
- **Problem:** Mad-libs-style templating. The structure is identical; only player names and numbers change. The phrase "yorker accuracy" is applied to every death bowler including leg-spinners (DS Rathi, Kuldeep Yadav) and off-spinners (SP Narine, Noor Ahmad). No team has unique strategic keys.
- **Severity:** MAJOR — requires rewrite. Each team should have genuinely different strategic priorities based on their data DNA.

**Issue M3: KKR Contradictory Tactical Summary**
- **File:** `stat_packs/KKR/KKR_stat_pack.md`
- **Lines:** ~686-690
- **Problem:** Section 10.6 analysis correctly identifies "under-par powerplay batting (SR 141.8 vs league 146.3), under-par middle-overs batting (SR 136.9 vs league 140.3), under-par death batting (SR 163.1 vs league 175.5)." Then immediately concludes with the boilerplate: "well-rounded squad with no glaring tactical gaps."
- **Impact:** Reader sees a direct contradiction between evidence and conclusion. Destroys analytical credibility.
- **Severity:** MAJOR

### MODERATE — Cricket Domain Inaccuracies

**Issue Mo1: "Yorker accuracy" applied to spinners**
- **Teams affected:** KKR (Narine — off-spinner), CSK (Noor Ahmad — left-arm wrist spinner), DC (Kuldeep Yadav — left-arm wrist spinner), LSG (DS Rathi — leg-spinner), GT (Prasidh Krishna — pacer, but labeled "reliable" at 10.39 economy)
- **Problem:** The template phrase "defending totals requires yorker accuracy and nerve under pressure" is applied to every death bowler in Key #6. Spinners do not bowl yorkers. Their death bowling skill is about varying pace, using wider lines, and bowling to plans against slog-sweeps.
- **Fix:** Generator should produce bowling-type-specific language: pace bowlers get "yorker accuracy," spinners get "variation and nerve under pressure."

**Issue Mo2: "Reliable" death bowling at 10.39+ economy**
- **Teams:** GT (Prasidh Krishna: 10.39), RR (Sandeep Sharma: 10.64), PBKS (Arshdeep: 10.5), SRH (Unadkat: 10.09), RCB (Hazlewood: 10.65)
- **Problem:** An economy rate above 10 in the death overs is above league average (~10.9) but not elite. Calling it "reliable" at 10.39-10.65 is generous. The template assigns "elite" (<8.0), "strong" (<9.5), and "reliable" for everyone else regardless of whether it is actually reliable.
- **Fix:** The adjective should be data-driven using thresholds from `config/thresholds.yaml`: beast (<9.0), good (9.0-12.0), liability (>12.0).

### MODERATE — Empty/Placeholder Sections

**Issue Mo3: Empty Section 1.2 (Player Archetypes) and Section 1.3 (Key Player Tags)**
- **Teams affected:** All 10
- **Problem:** Section 1.2 exists as a header with no content below it. Section 1.3 has a `| Player | Tags |` table header with no data rows.
- **Impact:** Reader sees empty sections. Feels like an incomplete product.
- **Fix:** Either populate from K-means clustering data (archetypes exist in the analytics pipeline) or remove the sections entirely.

**Issue Mo4: Empty Economy Rate Evolution table in CSK Section 3**
- **File:** `stat_packs/CSK/CSK_stat_pack.md`, line 138-140
- **Problem:** The "Economy Rate Evolution (Key Bowlers):" label exists but no table follows. All other teams have data here.
- **Impact:** CSK appears to have no bowler trends when they do (Deepak Chahar, Tushar Deshpande were key bowlers).
- **Fix:** Generator bug — likely no bowlers met the multi-season threshold for CSK. Lower threshold or add a "no qualifying bowlers" note.

### MINOR — Presentation Issues

**Issue Mi1: Truncated venue names in tables**
- **Teams affected:** All 10
- **Examples:** "Bharat Ratna Shri Atal Bihari Vajpa" (truncated), "Maharaja Yadavindra Singh Inte" (truncated), "Rajiv Gandhi International Sta" (truncated), "Himachal Pradesh Cricket Associatio" (truncated)
- **Problem:** Table column width causes venue names to be cut off without indication (no "...").
- **Fix:** Use abbreviated venue names in tables (e.g., "Ekana, Lucknow" instead of full name) or add "..." suffix when truncated.

**Issue Mi2: Venue name truncation in Venue Specialists (Section 4)**
- **Teams affected:** All 10
- **Problem:** Same as Mi1 but also affects the Venue Specialists section where player venue combinations get truncated.
- **Fix:** Same as Mi1.

**Issue Mi3: Inconsistent Pitch Characteristics table (identical across all teams)**
- **Problem:** The "Pitch Characteristics (All IPL Venues 2023+)" table in Section 4 is identical across all 10 teams. This is correct behavior (it is league-wide data) but it is redundant — readers comparing teams see the same table 10 times.
- **Fix:** Move to a standalone league reference document or append only to the first occurrence.

---

## Cross-Team Consistency Assessment

### Structural Consistency: PASS (10/10)
All 10 teams follow the identical 13-section structure:
1. Squad Overview (1.1 Roster, 1.2 Archetypes*, 1.3 Tags*)
2. Historical Record vs Opposition
3. Historical Trends (2023-2025)
3.5 Team Phase Approach (2023-2025)
4. Venue Analysis
5. Squad Batting Analysis (5.1 Career, 5.2 Phase-wise)
6. Squad Bowling Analysis (6.1 Career, 6.2 Phase Distribution)
7. Key Batter vs Opposition
8. Key Bowler vs Opposition
9. Key Player Venue Performance
10. Andy Flower's Tactical Insights (10.1-10.6)
11. Pressure Performance (11.1-11.4)
12. Uncapped Watch (12.1-12.3)
13. Cross-Tournament Intelligence (13.1-13.3)

*Sections 1.2 and 1.3 are empty across all teams.

### Metric Consistency: PASS
- SR = runs per 100 balls (batting) — correctly used throughout all 10 packs
- Economy = runs per over (bowling) — correctly used throughout
- Bowling SR = balls per wicket — correctly used
- No SR/RPO confusion detected anywhere
- Phase boundaries consistent: Powerplay (1-6), Middle (7-15), Death (16-20)

### Sample Size Indicators: PASS
All tables include "Sample" column with HIGH/MEDIUM/LOW indicators. Methodology section (13.3) is present in all 10 packs.

### Pressure Section: PASS
All 10 teams have Section 11 with consistent glossary, band definitions, and pressure rating methodology. Bands match `config/thresholds.yaml` definitions.

### Scoring Scale Consistency: PASS
The 1-10 scale used in this review is applied consistently. No team received scores outside the defined range.

---

## Detailed Team Notes

### CSK (7.0)
- Strong data depth: Ravindra Jadeja's dual-threat role well-captured
- Missing Economy Rate Evolution table is the only data gap
- Phase approach shows clear strategic DNA evolution
- Boilerplate closing undermines otherwise strong Section 10

### MI (7.3)
- Highest accuracy score: Bumrah stats (6.84 death economy) are genuinely elite and correctly positioned
- Suryakumar Yadav's middle-overs dominance well-captured
- Best-in-class bowling analysis section
- Boilerplate closing is the main weakness

### KKR (5.7)
- **Lowest score.** The contradiction between "under-par in ALL phases" and "no glaring gaps" is unacceptable
- Narine as "yorker accuracy" bowler is cricket-illiterate
- Otherwise good data on Starc and Russell's death bowling
- Phase approach data is actually very interesting — shows KKR's death batting is league-worst

### RR (7.0)
- Sanju Samson and Buttler data comprehensive
- Sandeep Sharma at 10.64 death economy labeled "reliable" is generous but not strictly wrong
- Trent Boult's PP dominance correctly highlighted

### DC (7.0)
- **Only team without the boilerplate closing** — has differentiated tactical summary mentioning "shore up pace-hitting deficiencies"
- Kuldeep Yadav "yorker accuracy" is cricket-inaccurate
- Otherwise solid; Rishabh Pant's phase data is well-presented

### SRH (7.0)
- Strong phase approach showing Abhishek Sharma's evolution
- Head and Klaasen data comprehensive
- Cummins dual-threat role well-captured
- Unadkat "yorker accuracy" is appropriate

### PBKS (7.0)
- P Simran Singh progression well-documented
- Arshdeep Singh's death bowling prowess correctly highlighted
- Shreyas Iyer acquisition adds middle-order depth
- Chahal's bowling data appears complete

### GT (6.3)
- Section 10.3 pace attack intelligence severely incomplete (only Arshad Khan listed despite having Rabada, Siraj, Prasidh Krishna)
- Shubman Gill's CLUTCH pressure rating is an interesting finding
- Sai Sudharsan's consistency well-documented

### LSG (6.0)
- PWH de Silva data contamination is the critical issue
- Pooran's pressure performance (PRESSURE_PROOF) is genuinely interesting
- Rishabh Pant and Mitchell Marsh data comprehensive
- DS Rathi "yorker accuracy" is cricket-inaccurate

### RCB (6.0)
- MP Yadav cross-contamination is the critical issue
- Virat Kohli's 208 powerplay innings (!) is an extraordinary sample size
- Phil Salt's arrival changes the team DNA significantly
- Devdutt Padikkal's PRESSURE_SENSITIVE rating is an interesting finding

---

## Recommendations

### Immediate (Before Ship)
1. **Remove MP Yadav data from RCB stat pack** — generator bug must be fixed
2. **Investigate PWH de Silva in LSG** — verify squad membership and data attribution
3. **Replace 9 boilerplate closing paragraphs** with team-specific tactical conclusions
4. **Fix "yorker accuracy" for spinners** — use bowling-type-aware language

### Short-Term (Next Sprint)
5. Populate Section 1.2 (Player Archetypes) from K-means clustering output
6. Populate Section 1.3 (Key Player Tags) from matchup tagging pipeline
7. Fix CSK Economy Rate Evolution empty table
8. Rewrite Section 3.5 Keys to Victory with team-differentiated strategic points
9. Use abbreviated venue names in tables

### Medium-Term
10. De-duplicate the Pitch Characteristics table (identical across all teams)
11. Add editorial commentary to Pressure Performance section (currently data-only)
12. Consider adding a "What to Watch For" opening paragraph per team

---

## Sign-Off

| Reviewer | Role | Assessment | Date |
|----------|------|------------|------|
| Virat Kohli | Tone & Narrative Guard | **CONDITIONAL PASS** — Boilerplate must be replaced before publication. Data quality is good but editorial voice is absent. | 2026-02-15 |
| Andy Flower | Cricket Domain Expert | **CONDITIONAL PASS** — Cross-team data contamination (C1, C2) must be fixed. Cricket-inaccurate language (Mo1) must be corrected. Underlying analytical framework is sound. | 2026-02-15 |

**Overall Status:** CONDITIONAL PASS — 4 blocking issues must be resolved before stat packs are publication-ready.

---

*Generated as part of TKT-240: Stat Pack Editorial Pass*
*Cricket Playbook v5.0.0*
