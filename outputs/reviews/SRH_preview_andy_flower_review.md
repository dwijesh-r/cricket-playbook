# SRH Season Preview -- Andy Flower Domain Review

**Reviewer:** Andy Flower (Cricket Domain Expert)
**Date:** 2026-02-22
**Document Reviewed:** `outputs/season_previews/SRH_season_preview.md` (v1.0)
**Cross-Referenced Against:** `stat_packs/SRH/SRH_stat_pack.md`, DuckDB raw queries on `fact_ball`, `dim_match`, `dim_player`, `dim_team`, and analytics views
**Data Window:** IPL 2023-2025 (match_date >= '2023-01-01')

---

## Rating

| Criterion | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Cricket Accuracy | 30% | 7.5/10 | 2.25 |
| Tactical Credibility | 25% | 8.5/10 | 2.13 |
| Sample Size Honesty | 20% | 9.0/10 | 1.80 |
| Domain Nuance | 25% | 8.5/10 | 2.13 |
| **Overall** | **100%** | - | **8.30** |

**Verdict: DOES NOT PASS (threshold 9.0). Fixes required.**

---

## Verification Log: Stats Checked Against DuckDB

I verified 15 stats from the preview directly against the DuckDB fact tables and analytics views. Below is the full audit trail.

### Stats That MATCH the Database

| # | Claim (Preview) | DB Value | Source | Verdict |
|---|----------------|----------|--------|---------|
| 1 | Klaasen: 175.2 SR, 807 balls, 1,414 runs (since 2023) | 175.22 SR, 807 balls, 1,414 runs | `fact_ball` aggregate | EXACT MATCH |
| 2 | Abhishek Sharma: 186.5 SR, 616 balls, 1,149 runs | 186.53 SR, 616 balls, 1,149 runs | `fact_ball` aggregate | EXACT MATCH |
| 3 | Head overall: 181.0 SR (520 balls) | 180.96 SR, 520 balls | `analytics_ipl_batting_career_since2023` | MATCH (rounded) |
| 4 | SRH PP batting SR since 2023: 152.3 | 152.26 | `fact_ball` phase aggregate | MATCH (rounded) |
| 5 | SRH middle batting SR since 2023: 144.1 | 144.06 | `fact_ball` phase aggregate | MATCH (rounded) |
| 6 | SRH death batting SR since 2023: 164.4 | 164.44 | `fact_ball` phase aggregate | MATCH (rounded) |
| 7 | SRH PP bowling economy since 2023: 9.68 | 9.68 | `fact_ball` phase aggregate | EXACT MATCH |
| 8 | SRH middle bowling economy since 2023: 9.09 | 9.09 | `fact_ball` phase aggregate | EXACT MATCH |
| 9 | SRH death bowling economy since 2023: 11.13 | 11.13 | `fact_ball` phase aggregate | EXACT MATCH |
| 10 | Cummins: 9.32 economy, 110.7 overs, 34 wickets | 9.32, 110.7 overs, 34 wickets | `fact_ball` aggregate | EXACT MATCH |
| 11 | Harshal: 9.91 economy, 140 overs, 54 wickets | 9.91, 140 overs, 54 bowling wickets | `analytics_ipl_bowler_phase_since2023` | MATCH (bowling wkts) |
| 12 | Zeeshan Ansari: 9.87 economy, 33.8 overs, 6 wickets | 9.87, 33.8 overs, 8 wickets | `fact_ball` aggregate | PARTIAL -- economy and overs match, wicket count is 8 in DB, not 6 |
| 13 | NKR: 133.2 SR, 364 balls (since 2023) | 133.24 SR, 364 balls | `analytics_ipl_batting_career_since2023` | MATCH (rounded) |
| 14 | SRH 2024 PP SR: 177.6 | 177.60 | `fact_ball` phase+season aggregate | EXACT MATCH |
| 15 | SRH home record: 8-10 (42.1%), 19 matches at Uppal | 8 wins, 19 matches at Rajiv Gandhi International Stadium | `dim_match` + `dim_venue` aggregate | EXACT MATCH |

### Stats With DISCREPANCIES

| # | Claim (Preview) | DB Value | Delta | Severity |
|---|----------------|----------|-------|----------|
| D1 | Head 2024 SR: 184.7 (stat pack) | 192.86 (567 runs / 294 balls) | +8.16 | HIGH -- per-season SR in stat pack appears computed differently from aggregate |
| D2 | Head 2025 SR: 150.8 (stat pack) | 165.49 (374 runs / 226 balls) | +14.69 | HIGH -- same methodology issue as D1 |
| D3 | NKR 2024 SR: 137.1 (stat pack) | 142.92 (303 runs / 212 balls) | +5.82 | HIGH -- same methodology issue |
| D4 | NKR 2025 SR: 113.0 (stat pack) | 119.74 (182 runs / 152 balls) | +6.74 | HIGH -- same methodology issue |
| D5 | Klaasen death SR: 199.6 (277 balls) -- preview body | 206.5 (246 balls) since 2023; 199.64 (277 balls) all-time | Mixed scopes | BLOCKING -- preview conflates all-time and since-2023 |
| D6 | Livingstone death SR: 227.8 (151 balls) -- preview body | 234.0 (100 balls) since 2023; 227.81 (151 balls) all-time | Mixed scopes | BLOCKING -- same all-time/since-2023 conflation |
| D7 | Harshal death economy: 9.78 (56.8 overs) -- preview body | 10.80 (56.8 overs) since 2023; 10.24 (140 overs) all-time | -1.02 | BLOCKING -- neither scope produces 9.78 |
| D8 | Harshal vs CSK: 6.57 economy (74 balls) -- preview body | 8.27 economy (74 balls, 102 total runs) from raw fact_ball; 6.57 from analytics view (81 runs) | Analytics pipeline issue | MEDIUM -- the analytics view undercounts runs (excludes extras from runs_conceded), preview inherits this |
| D9 | Cummins PP economy: 9.32 -- preview body line 32 | 9.52 since 2023; 8.77 all-time | Neither matches | HIGH -- the 9.32 is his overall economy, not his powerplay economy |
| D10 | Cummins middle economy: 7.50 (36 overs) -- preview body | 7.72 (36 overs) since 2023; 8.04 (79 overs) all-time | Neither matches | HIGH -- 7.50 not found in any scope |
| D11 | Cummins death economy: 10.63 (30.7 overs) -- preview body | 10.89 (30.7 overs) since 2023; 10.52 (74.5 overs) all-time | Neither matches | HIGH -- 10.63 not found in any scope |
| D12 | Cummins vs KKR economy: 10.60 (90 balls) -- preview body | 10.87 (90 balls) since 2023 | -0.27 | MEDIUM |
| D13 | Klaasen at Arun Jaitley: 236.1 SR (72 balls) -- preview body | 240.28 SR (72 balls, 173 runs) since 2023 | -4.18 | MEDIUM -- stat pack confirms 236.11 which also conflicts with raw query |
| D14 | Klaasen middle SR: 159.3 (526 balls) -- preview body | 161.48 (514 balls) since 2023; stat pack confirms 159.32 (526 balls) all-time | Mixed scopes | HIGH -- uses all-time data labeled as since-2023 |

---

## Blocking Issues (Must Fix Before Publication)

### BLOCK-1: Systematic All-Time / Since-2023 Data Conflation

**Severity:** BLOCKING
**Location:** Multiple sections throughout the preview

The preview declares its data window as "IPL 2023-2025" on line 5. However, numerous key stats are sourced from all-time IPL views rather than since-2023 views. This creates a fundamental data integrity problem: the reader is told they are seeing three-season data, but is actually seeing career numbers for several players.

**Specific instances:**

| Stat | Preview Claims (labeled "since 2023") | Since 2023 (DB) | All-Time (DB) | Preview Matches |
|------|---------------------------------------|-----------------|---------------|-----------------|
| Klaasen death SR | 199.6 (277 balls) | 206.5 (246 balls) | 199.64 (277 balls) | ALL-TIME |
| Klaasen middle SR | 159.3 (526 balls) | 161.48 (514 balls) | 159.32 (526 balls) | ALL-TIME |
| Livingstone death SR | 227.8 (151 balls) | 234.0 (100 balls) | 227.81 (151 balls) | ALL-TIME |
| Ishan Kishan PP SR | 134.1 (997 balls) | 146.88 (448 balls) | 134.1 (997 balls) | ALL-TIME |

**Impact:** Klaasen's death SR is overstated by labeling it as since-2023 (it's actually 206.5 since 2023, even better than the all-time 199.6 the preview quotes). Livingstone's death SR is also overstated as 227.8 when the since-2023 number is 234.0 (again, actually better). But the ball counts are wrong, and the confidence labels may shift. Ishan Kishan's powerplay SR is the most misleading: the preview says 134.1 (997 balls, HIGH) when the since-2023 figure is 146.88 (448 balls, MEDIUM). The 134.1 is his all-time PP SR -- 12 points lower -- and using it paints a more negative picture than warranted by recent form.

**Required Fix:** Audit every individual player stat in the preview. Use the `analytics_ipl_*_since2023` views exclusively. Update all SR values, ball counts, and sample size labels. The stats from the stat pack's Section 5.2 (Phase-wise Batting) and Section 6.2 (Bowler Phase Distribution) should be cross-checked against the since-2023 analytics views.

---

### BLOCK-2: Harshal Patel Death Economy Misquoted

**Severity:** BLOCKING
**Location:** Lines 26, 152, 405, 495

The preview states Harshal Patel's death economy is 9.78 across 56.8 overs (HIGH). The DuckDB since-2023 view shows 10.80 economy across 56.8 overs. The all-time view shows 10.24 across 140 overs. No scope produces the 9.78 figure.

The stat pack's Section 6.2 lists Harshal's death economy as 9.78 (56.8 overs), and Section 10.1 lists 10.2 for the same phase. These internal inconsistencies within the stat pack suggest a generation bug.

The correct since-2023 death economy for Harshal Patel is **10.80**. This is 1.02 runs higher than the quoted 9.78. This materially changes the narrative: at 10.80 death economy, Harshal is not "carrying the death bowling unit" -- he is performing at roughly the league average (10.87), not below it. The preview's claim that "Harshal Patel (9.78 econ, 56.8 death overs, HIGH) carries the unit" is factually misleading.

**Required Fix:** Replace all instances of 9.78 death economy with the correct figure. The stat pack's Section 6.2 (HV Patel death: 9.78) should also be flagged for correction upstream.

---

### BLOCK-3: Cummins Phase Economies Are Fabricated

**Severity:** BLOCKING
**Location:** Lines 32, 360, 406, 475

The preview cites specific phase economies for Cummins that do not exist in any database scope:

| Phase | Preview | Since 2023 | All-Time | Stat Pack Sec 6.2 |
|-------|---------|------------|----------|-------------------|
| PP | 9.32 | 9.52 | 8.77 | 9.32 |
| Middle | 7.50 | 7.72 | 8.04 | 7.72 (Sec 10.1) / 7.50 not found |
| Death | 10.63 | 10.89 | 10.52 | 10.63 not found |

The 9.32 PP economy is actually Cummins' **overall** economy, not his powerplay-specific number. The 7.50 middle economy is not found in any view. The 10.63 death economy is not found in any view. It appears the preview copied the overall economy (9.32) into the PP section, and the other phase figures may have been approximated or computed with an incorrect methodology.

**Required Fix:** Replace with the correct since-2023 phase economies: PP 9.52, Middle 7.72, Death 10.89.

---

## High-Priority Issues

### HIGH-1: Per-Season SR Figures in Narrative Do Not Match Database

**Severity:** HIGH
**Location:** Lines 22, 23, 127-137 (Story section year-by-year tables)

The preview's narrative cites per-season SRs that come from the stat pack's Historical Trends section. These figures do not match the aggregate SR computed from the raw data:

| Player | Season | Preview SR | DB SR (runs/balls) | Delta |
|--------|--------|-----------|-------------------|-------|
| Head | 2024 | 184.7 | 192.86 (567/294) | +8.16 |
| Head | 2025 | 150.8 | 165.49 (374/226) | +14.69 |
| NKR | 2024 | 137.1 | 142.92 (303/212) | +5.82 |
| NKR | 2025 | 113.0 | 119.74 (182/152) | +6.74 |

The stat pack appears to compute per-season SRs using a method that differs from the standard aggregate (total runs / total balls * 100). This may be an innings-average methodology or may include non-legal deliveries in the denominator. Regardless, the numbers cited in the preview do not match the canonical definition of strike rate.

**Required Fix:** Either recalculate these figures using aggregate SR (which is standard) or add a methodology note explaining the deviation. The Head 2024 discrepancy (184.7 vs 192.86) is material enough to change the reader's perception of the 2024-2025 regression narrative (the real SR drop is 192.86 to 165.49 = 27.4 points, not the 33.9 points the preview claims).

---

### HIGH-2: Zeeshan Ansari Wicket Count

**Severity:** HIGH
**Location:** Lines 26, 376, 409

The preview says Ansari has 6 wickets across 33.8 overs. The database shows 8 wickets across 33.8 overs. The stat pack also says 6 wickets. This appears to be a stat pack generation issue -- possibly filtering out caught-and-bowled or a wicket type exclusion. The correct figure is 8 wickets. Understating wickets by 33% is non-trivial for a bowler with a small sample.

**Required Fix:** Verify the wicket count methodology and correct to 8 if the stat pack pipeline is miscounting.

---

## Medium-Priority Issues

### MED-1: Harshal vs CSK Economy Uses Runs That Exclude Extras

**Severity:** MEDIUM
**Location:** Line 427

The preview says Harshal has 6.57 economy against CSK. This figure comes from the `analytics_ipl_bowler_vs_team_since2023` view, which reports 81 runs from 74 balls. The raw `fact_ball` table shows 102 total runs (87 batter runs + 15 extras) from the same 74 balls, yielding 8.27 economy. The analytics view apparently undercounts runs conceded by excluding extras (wides, no-balls) from the runs figure but still counting legal balls only for the denominator. In cricket, economy rate is always calculated using total runs conceded (including all extras bowled by that bowler). The correct economy is 8.27.

However, this is a systemic pipeline issue that affects all bowler-vs-team stats, not just this one. The preview is using its own pipeline's output consistently. I flag this for Stephen Curry / Brock Purdy to investigate upstream.

**Required Fix (Preview):** Add a note that this figure comes from the analytics view and may differ from standard economy calculations.
**Required Fix (Pipeline):** Investigate the `runs_conceded` column in `analytics_ipl_bowler_vs_team_since2023` -- it should include all extras charged to the bowler.

---

### MED-2: Klaasen at Arun Jaitley SR

**Severity:** MEDIUM
**Location:** Line 423

The preview says 236.1 SR at Arun Jaitley (72 balls). The stat pack says 236.11 (72 balls, 170 runs). My raw query returns 240.28 SR (72 balls, 173 runs). The discrepancy is 3 runs -- the stat pack reports 170 runs, the raw table reports 173 runs. This is a minor pipeline inconsistency (possibly in how extras or run outs are counted at the batter level).

**Required Fix:** Verify the batter runs count at Arun Jaitley. The delta is small but exists.

---

### MED-3: "Six wins in 14 matches. A 46.2% win rate" -- Arithmetic Error

**Severity:** MEDIUM
**Location:** Line 22

Six wins in 14 matches is 42.9%, not 46.2%. The stat pack correctly says 42.9%. The database shows 6 wins, 7 losses, 1 no-result in 14 matches. If you count decided matches only (13), the win rate is 46.2%. The preview should either say "Six wins in 13 decided matches (46.2%)" or "Six wins in 14 matches (42.9%)." Mixing them is misleading.

**Required Fix:** Clarify the denominator.

---

### MED-4: Head-to-Head RCB Split

**Severity:** MEDIUM
**Location:** Lines 312, 320, 329

The database shows two RCB team entries (Royal Challengers Bengaluru and Royal Challengers Bangalore). The preview notes this on line 320: "RCB has a split alias; combining both RCB entries: 2-2, 50.0%." However, the head-to-head table on line 312 shows RCB as "2-1, 66.7%", and the combined record on line 320 says "2-2, 50.0%". This means there is 1 match against the old "RCB Bangalore" alias that SRH lost. This handling is acceptable but the table should show the combined record directly, not the partial record. Alternatively, the footnote should be placed inline with the table entry.

**Required Fix:** Either combine the records in the table itself (3 matches, 2-1 becomes 4 matches, 2-2 with the alias) or clarify the footnote more prominently.

---

## Strengths

### 1. Exceptional Narrative Architecture

The three-season arc (2023: before the revolution, 2024: the year everything changed, 2025: the hangover) is the strongest narrative framework I have seen in any Cricket Playbook preview. The phase tables for each season provide clear, comparable snapshots that allow the reader to track the franchise's evolution. The 52.4-point PP batting SR jump from 2023 to 2024 is correctly identified as the defining inflection point.

### 2. Bowling Weakness Analysis Is Thorough and Credible

The identification of the bowling as SRH's structural limitation is persistent, data-backed, and never over-simplified. The preview correctly notes that the middle-overs bowling (9.09 economy, 0.33 above league) is the weakest link, identifies the absence of a frontline spinner as the root cause, and names Eshan Malinga (7.38 middle-overs economy, 13 overs, MEDIUM) as the potential internal solution. This is the kind of analysis a professional coaching staff would value.

### 3. Phase x Bowling Type Cross-Reference Table

The cross-reference table (lines 186-193) showing SRH batting SR by phase AND bowling type is analytically excellent. The identification of "middle overs vs right-arm off-spin at 126.8 SR" as the specific matchup weakness is actionable intelligence. The 208.1 SR against fast bowling at the death is correctly flagged as the team's strongest hand. This table alone elevates the preview above surface-level analysis.

### 4. Sample Size Honesty Is Consistently Applied

Throughout the preview, sample sizes are labeled (HIGH/MEDIUM/LOW), ball counts are provided, and claims are qualified accordingly. Livingstone's 84.2 SR against left-arm orthodox is correctly flagged as LOW (38 balls). Abhishek's 251.0 SR against leg-spin is correctly flagged as LOW (49 balls). The preview consistently leads with MEDIUM/HIGH evidence and qualifies LOW-sample insights as "directional." This is textbook epistemic discipline.

### 5. Opposition Blueprint Is Genuinely Actionable

The scouting report (lines 483-504) provides a clear, data-backed plan for opposing teams: bowl off-spin in the middle overs, do not bowl fast at Klaasen in the death, use left-arm orthodox against Livingstone, test Head's form early. Each recommendation is tied to specific stats with sample sizes. A professional coaching staff could use this section directly in match preparation.

### 6. Bold Take Is Well-Argued (Despite Data Concerns)

The argument that SRH should chase more often is intellectually coherent and well-structured. The framework of comparing bowling-first economy vs defending economy is a novel analytical angle. The identification of Abhishek's 209.3 chasing SR as the engine of chase proficiency is insightful. The tactical recommendation ("bat as if chasing 190 from ball one") is both cricket-savvy and data-supported. However, the underlying bat-first/bat-second win rate figures need verification (see note below on the bat-first/second data).

---

## Notes on Bat-First/Second Win Rates

The preview cites 35.0% batting-first (20 matches, 7 wins) and 52.2% batting-second (23 matches, 12 wins). My raw dim_match query using toss_winner_id and toss_decision produces 44.0% batting-first (25 matches, 11 wins) and 44.4% batting-second (18 matches, 8 wins) -- a vastly different picture.

However, the `analytics_ipl_match_context_since2023` view reproduces the preview's figures exactly: 20 bat-first (7W, 35.0%) and 23 bat-second (12W, 52.2%). This means the analytics view and the raw toss logic disagree. The preview is internally consistent with the analytics pipeline, but there may be a bug in how the analytics view determines batting order (perhaps using innings data from fact_ball rather than toss_decision, which could handle edge cases like super overs or abandoned matches differently).

I do NOT flag this as a preview error because the preview correctly uses its own pipeline's output. However, I flag this for **Brad Stevens / Brock Purdy** to investigate: the `analytics_ipl_match_context_since2023` view's bat-first/bat-second logic should be reconciled with the raw `dim_match.toss_decision` field.

If the raw numbers are correct (44.0% vs 44.4%), the entire Bold Take section and multiple strategic recommendations ("win the toss and chase") become unsupported. This is a critical data integrity question that needs resolution before publication.

---

## Scoring Justification

### Cricket Accuracy: 7.5/10

**Positives:**
- Core team-level stats (PP/middle/death batting SR, bowling economies) are all verified exact against the database.
- Career-level batting stats for Klaasen, Abhishek, Head, and NKR are correct (since-2023 scope).
- Head-to-head records match the database exactly.
- Home venue record (8-10, 19 matches) is exact.

**Negatives:**
- Three blocking issues: all-time/since-2023 conflation for individual phase stats, Harshal death economy misquoted, Cummins phase economies fabricated.
- Per-season SR figures (Head 184.7/150.8, NKR 137.1/113.0) do not match database aggregates.
- Zeeshan Ansari wicket count wrong (6 vs 8).
- SRH 2025 win rate arithmetic error (46.2% stated for 6/14 = 42.9%).

The team-level accuracy is strong, but the individual-level phase stats contain enough errors to warrant a 7.5. The blocking issues are data-sourcing problems, not analytical failures.

---

### Tactical Credibility: 8.5/10

**Positives:**
- The three-season arc narrative is strategically sound and supported by verified phase data.
- The opposition blueprint is actionable and tied to specific, credible stats.
- The identification of middle-overs off-spin as SRH's batting vulnerability is a genuine insight.
- The phase x bowling type cross-reference is analytically elite.
- The Eshan Malinga middle-overs potential is correctly identified as the internal solution to the bowling weakness.

**Negatives:**
- The "win the toss and chase" recommendation may be built on questionable bat-first/second data (see note above). If the raw numbers are correct, this key strategic recommendation collapses.
- Cummins' phase economies are wrong, which undermines the bowling deployment analysis.
- Harshal's death economy is significantly overstated, which changes the assessment of who "carries" the death bowling.

The tactical framework is excellent. The specific numbers supporting it need correction.

---

### Sample Size Honesty: 9.0/10

**Positives:**
- Every major claim includes ball counts and confidence labels (HIGH/MEDIUM/LOW).
- LOW-sample stats (Livingstone vs left-arm orthodox 38 balls, Abhishek vs leg-spin 49 balls) are explicitly qualified.
- The preview consistently leads with MEDIUM/HIGH evidence and treats LOW-sample data as directional.
- Phase data uses appropriate confidence thresholds.

**Negatives:**
- The all-time/since-2023 conflation means some ball counts are wrong (e.g., Klaasen death: 277 balls labeled since-2023 is actually all-time; since-2023 is 246 balls). This affects the confidence labels: 277 balls might be HIGH while 246 balls might be MEDIUM, depending on thresholds.
- No explicit acknowledgment of the methodological difference in per-season SR computation.

The intent is excellent. The execution is undermined by the scope confusion, but the practice of qualifying claims is consistently strong.

---

### Domain Nuance: 8.5/10

**Positives:**
- The distinction between "outscore, don't outbowl" philosophy and its structural consequences is professionally framed.
- Livingstone's dual-spin capability (off-spin to left-handers, leg-spin to right-handers) is correctly noted as a tactical feature.
- The Uppal venue analysis correctly identifies the pace-friendly nature (Pace SR 19.4, Spin SR 26.5) and links it to SRH's squad composition.
- The Klaasen vs CSK vulnerability (96.4 SR, 56 balls) is correctly identified as a matchup issue driven by Chennai's spin + slow conditions combination.
- The pressure ratings (PRESSURE_PROOF for Klaasen, PRESSURE_SENSITIVE for Kishan) are correctly deployed in tactical recommendations.
- The death-overs chasing SR collapse (152.4 vs 171.4 when setting) is a genuine insight that reflects deep tactical understanding.

**Negatives:**
- Unadkat is described as a "Pace Bowler" in the squad table but his bowling is classified as "Fast" in the stat pack. His actual style is left-arm medium-fast. The distinction matters: he provides a left-arm angle that is tactically different from the right-arm pace of Cummins and Harshal. This left-arm angle is never discussed.
- Eshan Malinga is listed as "Pace Bowler" but his bowling type is "Fast-Medium" and he is left-handed. His left-arm angle is also never mentioned.
- SRH's bowling attack has gone from three left-arm options (Bhuvneshwar is right-arm, correction: Natarajan was left-arm, Jansen was left-arm) to fewer left-arm options (Unadkat, Malinga). The preview mentions the "less left-arm heavy" shift (line 40) but does not explore the tactical consequence: the loss of left-arm variety reduces the angles of attack against right-handed batters in the powerplay.
- The preview does not discuss Abhishek Sharma's left-arm orthodox spin as a tactical option in the middle overs (8.5 economy, 20 overs in middle from stat pack Section 6.2). For a team starved of spin, this is an underexplored option.

---

## Required Fixes (Ordered by Priority)

### Fix 1: Resolve All-Time / Since-2023 Conflation (BLOCKING)

Audit all individual player phase stats. Replace any stat that matches the `analytics_ipl_*_alltime` views with the corresponding `analytics_ipl_*_since2023` figure. Key corrections:

| Stat | Current (All-Time) | Correct (Since 2023) |
|------|-------------------|---------------------|
| Klaasen death SR | 199.6 (277 balls) | 206.5 (246 balls, MEDIUM) |
| Klaasen middle SR | 159.3 (526 balls) | 161.48 (514 balls, HIGH) |
| Livingstone death SR | 227.8 (151 balls) | 234.0 (100 balls, MEDIUM) |
| Ishan Kishan PP SR | 134.1 (997 balls, HIGH) | 146.88 (448 balls, MEDIUM) |

Note: The Ishan Kishan correction is particularly impactful. The preview says his PP SR is "12.2 points below the league average of 146.3." Using the since-2023 figure (146.88), he is actually 0.6 points ABOVE the league average. This reverses the entire "step up" narrative for Kishan's powerplay.

### Fix 2: Correct Harshal Death Economy (BLOCKING)

Replace 9.78 with **10.80** (since 2023) across all instances: lines 26, 152, 405, 495. Update the Category Ratings bowling death entry and the Scouting Report accordingly. At 10.80, Harshal's death economy is essentially at the league average (10.87), not significantly below it.

### Fix 3: Correct Cummins Phase Economies (BLOCKING)

Replace across all instances:
- PP: 9.32 (this is overall, not PP) -> **9.52**
- Middle: 7.50 -> **7.72**
- Death: 10.63 -> **10.89**

### Fix 4: Correct Per-Season SRs or Add Methodology Note (HIGH)

Either:
(a) Recalculate Head 2024/2025 and NKR 2024/2025 SRs using aggregate method (total runs / total balls * 100), or
(b) Add a note explaining the alternative methodology.

If using aggregate: Head 2024 = 192.86, Head 2025 = 165.49, NKR 2024 = 142.92, NKR 2025 = 119.74.

### Fix 5: Correct Zeeshan Ansari Wicket Count (HIGH)

6 wickets -> 8 wickets across all instances.

### Fix 6: Fix 2025 Win Rate Arithmetic (MEDIUM)

"Six wins in 14 matches. A 46.2% win rate" -> "Six wins in 14 matches (42.9% overall; 46.2% in decided matches)"

### Fix 7: Investigate Bat-First/Second Pipeline Discrepancy (MEDIUM -- for Brad Stevens / Brock Purdy)

The analytics view and raw dim_match toss logic produce different bat-first/bat-second counts. This must be resolved before publication because it underpins the Bold Take and Key to Victory #1. If the raw numbers are correct (44.0% vs 44.4%, virtually identical), the "win the toss and chase" recommendation is unsupported.

### Fix 8: Mention Left-Arm Angle for Unadkat and Malinga (MEDIUM -- Domain Nuance)

First reference to each bowler should note their left-arm angle. The tactical discussion of bowling variety should explicitly note that SRH have two left-arm seam options (Unadkat, Malinga) who create angles against right-handed batters.

### Fix 9: Discuss Abhishek's Middle-Overs Spin Option (MEDIUM -- Domain Nuance)

Abhishek Sharma's left-arm orthodox bowling (8.5 economy in middle overs, 20 overs) is a meaningful tactical option for a team that lacks a quality frontline spinner. The preview should at least mention this as a supplementary option.

---

## Path to 9.0+

The preview's analytical framework and narrative quality are already at 9.0+ level. The issues are almost entirely data-sourcing problems that can be fixed mechanically:

1. Fix all three BLOCKING issues (all-time/since-2023 conflation, Harshal death economy, Cummins phase economies) -- this alone raises Cricket Accuracy from 7.5 to 9.0.
2. Correct per-season SRs and Ansari wickets -- raises Cricket Accuracy further to 9.5.
3. Resolve bat-first/second pipeline discrepancy -- either confirms the Bold Take or requires rewriting it.
4. Add left-arm bowling angle discussion -- raises Domain Nuance from 8.5 to 9.0.

**Projected post-fix score:**

| Criterion | Weight | Post-Fix Score | Weighted |
|-----------|--------|---------------|----------|
| Cricket Accuracy | 30% | 9.5/10 | 2.85 |
| Tactical Credibility | 25% | 9.0/10 | 2.25 |
| Sample Size Honesty | 20% | 9.5/10 | 1.90 |
| Domain Nuance | 25% | 9.0/10 | 2.25 |
| **Overall** | **100%** | - | **9.25** |

---

## Recommendation

**RETURN FOR FIXES.** The preview is analytically strong but the data integrity issues (three BLOCKING items) prevent publication. The fixes are mechanical -- replacing wrong numbers with correct ones from the database -- and should take approximately 60-90 minutes. The narrative quality, analytical framework, and editorial voice are all publication-ready. Once the stats are corrected, this will be a strong 9.0+ preview.

---

*Review completed: 2026-02-22*
*Andy Flower, Cricket Domain Expert*
*Cricket Playbook v5.0.0*
