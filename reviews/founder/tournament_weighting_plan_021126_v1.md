# Tournament Quality Weighting System — Founder Review Plan

**Date:** 2026-02-11
**Owner:** Jose Mourinho (Quant Researcher)
**Collaborators:** Stephen Curry (Analytics Lead), Brock Purdy (Data Pipeline), Andy Flower (Domain Expert)
**Document:** tournament_weighting_plan_021126_v1.md
**Status:** FOUNDER APPROVED — Phase 1 In Progress
**TIL Step:** 0 (PRD)

---

## Executive Summary

Jose Mourinho's research into tournament quality weighting addresses a fundamental analytical question: how should non-IPL T20 performance data be weighted when informing our internal analytical models? With 426 tournaments and 9,357 matches in our DuckDB database, we have extensive cross-tournament data — but not all tournaments are created equal.

The Founder has reviewed the methodology and rendered five binding decisions that shape the system's scope, governance, and integration path. The core principle: **weights are an internal analytical tool that must be data-derived, Founder-approved, and kept invisible to the paid artifact for now.** Non-IPL data supplements but does not compete with IPL data as the primary analytical source.

This document serves as the PRD (Step 0 of the Task Integrity Loop) for the implementation of the Tournament Quality Weighting System.

---

## Founder Decisions (Binding)

The following five questions were presented to the Founder. Each answer is a binding directive that governs all downstream implementation.

| # | Question | Founder Decision |
|---|----------|-----------------|
| 1 | Should tournament weights be exposed in the paid artifact? | **NO.** Weights are an INTERNAL analytical tool for now — not exposed in the paid artifact. They may inform outputs, but the weighting mechanism itself stays behind the curtain. |
| 2 | What is the status of non-IPL data? | **SUPPLEMENTARY.** Non-IPL data is supplementary, not first-class. IPL remains the primary analytical source per Constitution Section 8.1. Non-IPL data adds context and depth but does not carry equal standing. |
| 3 | Can weights be used editorially? | **NOT YET.** No editorial use at this time — purely internal analytical purposes. Weights may eventually inform editorial judgments, but that decision is deferred. |
| 4 | Who determines the final weight values? | **DATA-DERIVED, FOUNDER-APPROVED.** The system must use data to derive weights, but the Founder retains final sign-off authority on all weight values before they are integrated into any analytical pipeline. |
| 5 | How should temporal decay rates be determined? | **DATA-DERIVED, FOUNDER-DECIDED.** Use data to determine candidate temporal decay rates — present findings for Founder decision. The Founder will select the final decay parameters from the data-supported options. |
| 6 | What IPL baseline should be used for conditions comparison? | **IPL 2023-2025 ONLY.** All Factor 4 (Conditions Similarity) calculations must use IPL 2023-2025 as the baseline. The data shows a structural break at 2023 (see Appendix A). Using all-time IPL averages would dilute the signal with a fundamentally different era. **Locked in by Founder.** |

**Authority chain:** These decisions sit at Level 1 (Founder) per Constitution Section 2.1 and cannot be overridden by any agent.

---

## Data Inventory

Our DuckDB instance contains comprehensive T20 data that forms the foundation for weight derivation.

### Database Summary

| Metric | Value |
|--------|-------|
| Total tournaments | 426 |
| Total matches | 9,357 |
| Players appearing in 2+ tournaments | 3,698 |

### Key Franchise Leagues

| Tournament | Matches | Notes |
|------------|---------|-------|
| IPL | 1,169 | Primary data source (Constitution 8.1) |
| Vitality Blast | 967 | Largest county-level T20 dataset |
| BBL | 654 | Established franchise league |
| CPL | 407 | Caribbean Premier League |
| PSL | 314 | Pakistan Super League |
| T20 World Cup | 231 | ICC flagship event |
| The Hundred | 167 | 100-ball format (conditions mapping required) |
| ILT20 | 134 | UAE-based franchise league |
| SA20 | 121 | South Africa franchise league |
| MLC | 75 | Major League Cricket (USA) |

### Cross-Tournament Player Mobility

3,698 players appear in 2+ tournaments, providing the foundation for the Player Quality Index. This cross-pollination is what makes tournament weighting analytically meaningful — we can observe how the same players perform across different competitive environments.

---

## Methodology: 5-Factor Composite Weight

Each tournament's quality weight is derived from a composite of five independently computed factors. No single factor dominates; the composite approach ensures robustness against any individual metric's weaknesses.

### Factor 1: Player Quality Index (PQI)

**Definition:** The percentage of players in a given tournament who also appear in Tier 1 leagues (IPL, PSL, SA20, BBL, The Hundred, CPL).

**Rationale:** Tournaments with higher concentrations of IPL-caliber talent produce more relevant performance data. A league where 35% of players also play IPL provides more transferable signal than one where 5% do.

**Computation:** For each tournament-season, calculate the ratio of unique players who have appeared in at least one Tier 1 league within the preceding 3 seasons.

### Factor 2: Competitiveness Index (CI)

**Definition:** Match margin analysis measuring how close contests are within a tournament.

**Metrics:**
- Close match percentage (margin <= 15 runs or <= 2 wickets)
- Average winning margin (runs and wickets separately)
- Super Over / tied match frequency

**Rationale:** Competitive leagues produce performance data under pressure. Blowout-heavy tournaments inflate stats and reduce signal quality.

### Factor 3: Recency Decay

**Definition:** Exponential decay function applied to historical tournament data, with more recent seasons carrying higher weight.

**Rate:** To be determined from data analysis (per Founder Decision #5). Jose Mourinho will present candidate decay curves with supporting evidence; the Founder will select the final rate.

**Rationale:** Playing conditions, player abilities, and league quality evolve. A 2024 PSL season is more relevant than a 2018 PSL season for IPL 2026 projections.

### Factor 4: Conditions Similarity to IPL

**Definition:** Quantitative comparison of playing conditions between a tournament and the IPL.

**Baseline: IPL 2023-2025 only** (Founder Decision #6). The all-time IPL average (RR 7.86) blends fundamentally different eras; the modern IPL (RR 8.98) is the correct benchmark. See Appendix A for the full data justification.

**Metrics:**
- Run rate differential (tournament avg vs IPL 2023-2025 avg)
- Boundary percentage comparison (vs IPL 2023-2025 baseline of 19.7%)
- Wickets per over distance (absolute difference from IPL 2023-2025 baseline of 0.307)

**Rationale:** Tournaments played in similar conditions to the IPL produce more transferable performance data. A player's SA20 numbers in Johannesburg tell us more about their IPL potential than the same player's performance in a low-scoring Associate tournament.

### Factor 5: Sample Size Confidence

**Definition:** Threshold-based confidence factor that accounts for the statistical reliability of tournament data.

**Mechanics:**
- Below minimum match threshold: weight suppressed
- Scales linearly from threshold to confidence cap
- Capped at 1.0 (no bonus for excess data)

**Rationale:** A tournament with 15 matches cannot be weighted as confidently as one with 150. This factor prevents small-sample tournaments from receiving outsized influence.

### Composite Weight Formula

```
W(tournament) = f(PQI, CI, Recency, Conditions, SampleSize)
```

The exact aggregation function (weighted average, geometric mean, or other) will be determined during Phase 1 and presented for Founder approval alongside the raw factor scores.

---

## Key Analytical Findings

Jose Mourinho's preliminary research has surfaced the following findings that inform the weighting methodology.

### Strike Rate Differentials (vs IPL 2023-2025 baseline)

**Important correction:** Earlier preliminary analysis compared tournament strike rates against all-time IPL averages (RR 7.86). Per Founder Decision #6, all comparisons now use the **IPL 2023-2025 baseline (RR 8.98)**. This produces materially different — and more honest — differentials. The MLC comparison in particular was misleading when benchmarked against the all-time average.

| Tournament | SR Differential (vs 2023+ IPL) | Interpretation |
|------------|-------------------------------|----------------|
| Vitality Blast | TBD (Phase 1) | To be recalculated against 2023+ baseline |
| MLC | TBD (Phase 1) | Gap expected to widen significantly vs 2023+ baseline |
| T20 World Cup | TBD (Phase 1) | To be recalculated against 2023+ baseline |

*All differentials will be recomputed during Phase 1 using the Founder-approved IPL 2023-2025 baseline.*

### Wickets Per Over

IPL has the **lowest** wickets per over of any major league at **0.307** (2023-2025), indicating that IPL batting conditions are the most batting-friendly among top-tier T20 leagues. This has direct implications for how we interpret bowling statistics from other tournaments.

### Player Overlap with IPL

| Tournament | Approximate Player Overlap |
|------------|---------------------------|
| SA20 | 30-35% |
| MLC | 25-30% |
| The Hundred | 25-30% |
| PSL | 20-25% |
| BBL | 15-20% |
| CPL | 15-20% |

Higher overlap tournaments provide more direct comparables for IPL analytical models.

---

## Proposed Tournament Tiers

Based on the preliminary factor analysis, the following tier structure is proposed. **All base weights are provisional and require Founder approval before integration (per Founder Decision #4).**

| Tier | Tournaments | Base Weight Range | Rationale |
|------|-------------|-------------------|-----------|
| **1A** | IPL | 1.00 | Primary data source; all weights relative to this baseline |
| **1B** | PSL, SA20, The Hundred, MLC, BBL, CPL | 0.70 - 0.85 | Major franchise leagues with meaningful IPL player overlap and competitive depth |
| **1C** | ILT20, LPL, Super Smash, Vitality Blast | 0.50 - 0.70 | Established leagues with lower IPL overlap or significantly different conditions |
| **2** | T20 World Cup, Asia Cup | 0.60 - 0.80 | High-quality international cricket but different context (nation vs franchise, different pitch conditions) |
| **3** | SMAT | 0.40 - 0.50 | Domestic Indian T20 with direct IPL pipeline relevance but lower overall quality |
| **4** | ICC Qualifiers, bilateral T20Is | 0.10 - 0.30 | Limited relevance; small samples, variable opposition quality |
| **5** | Regional / Associate | 0.00 - 0.10 | Minimal analytical signal for IPL purposes |

**Note:** The ranges within each tier will be narrowed to specific values during Phase 1 based on the 5-factor composite scores. The Founder will approve final values.

---

## Implementation Phases

| Phase | Work | Owner | Effort | Dependencies |
|-------|------|-------|--------|--------------|
| **1** | Weight derivation — compute PQI, CI, conditions similarity, recency decay candidates, sample size confidence for all 426 tournaments | Jose Mourinho + Stephen Curry | 2-3 days | Data inventory complete (confirmed) |
| **2** | Implementation — build `dim_tournament_weights` table, create weighted views, update `thresholds.yaml` with weight parameters | Stephen Curry + Brock Purdy | 3-4 days | Phase 1 complete + Founder approval of derived weights |
| **3** | Validation — domain sanity review, statistical robustness checks, edge case analysis | Andy Flower + Jose Mourinho + Pep Guardiola | 1-2 days | Phase 2 complete |
| **4** | Integration — apply weights internally to clustering, player tags, and analytical models | Stephen Curry | 2-3 days | Phase 3 complete |

**Total estimated effort:** 8-12 days

**Critical gate:** Phase 2 cannot begin until the Founder has reviewed and approved the derived weights from Phase 1. This is a hard dependency per Founder Decision #4.

---

## Governance

### Task Integrity Loop Status

| Step | Name | Status | Notes |
|------|------|--------|-------|
| 0 | PRD | **APPROVED** | Founder reviewed and approved 2026-02-11. Decision #6 locked (IPL 2023+ baseline). |
| 1 | Florentino Gate | **APPROVED** | Classified ANALYTICS_ONLY. Approved for internal calibration use. |
| 2 | Build | **IN PROGRESS** | Phase 1 started — weight derivation for 426 tournaments |
| 3 | Domain Sanity | NOT STARTED | Andy Flower, Jose Mourinho, Pep Guardiola |
| 4 | Enforcement | NOT STARTED | Tom Brady sign-off |
| 5 | Commit & Ship | NOT STARTED | Feature branch merge |
| 6 | Post Note | NOT STARTED | Documentation update |
| 7 | System Check | NOT STARTED | N'Golo Kante integrity review |

### Constitutional Alignment

- **Section 8.1 (Data Scope):** IPL is the primary data source. Non-IPL T20 data is baseline context for sanity checks. This system formalizes the "sanity check" role of non-IPL data by making it quantitatively weighted rather than ad-hoc.
- **Section 2.1 (Authority):** Founder retains ultimate override on all weight values.
- **Section 2.2 (Veto Rights):** Jose Mourinho can block unrobust/unscalable solutions; Andy Flower can block cricket-untrue insights; N'Golo Kante can block data integrity issues.

### Key Governance Constraints

1. All derived weights must be Founder-approved before integration into any pipeline
2. No black-box outputs — all weights must be transparent, documented, and reproducible
3. Weights remain internal-only until Founder explicitly approves editorial or artifact exposure
4. Any weight modification post-approval requires a new Founder review cycle

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Over-engineering | Medium | High | Start with a 3-tier simplified system; refine iteratively. Resist the temptation to build a perfect system before proving the concept works. |
| Weight gaming | Low | High | Founder sign-off required on all final weights. No agent can unilaterally adjust weight values. |
| Data staleness | Medium | Medium | Recency decay factor directly addresses this. Decay rate itself will be data-derived and Founder-approved. |
| Small sample noise | Medium | Medium | Sample Size Confidence factor caps the influence of low-data tournaments. Tournaments below the minimum match threshold receive suppressed weights. |
| Scope creep into editorial | Medium | Medium | Founder Decision #3 explicitly prohibits editorial use at this time. Any future editorial integration requires a separate Founder approval. |
| Integration complexity | Low | Medium | Phased implementation ensures each layer is validated before the next begins. Phase 3 validation gate catches issues before integration. |

---

## Next Steps

1. **Create TKT-183** for implementation tracking in Mission Control (Owner: Tom Brady)
2. **Jose Mourinho:** Compute raw factor scores (PQI, CI, conditions similarity, recency decay candidates, sample size confidence) for all tournaments in DuckDB
3. **Stephen Curry:** Build `dim_tournament_weights` table schema and prepare weighted view templates
4. **Present derived weights** to Founder for approval before any integration work begins (hard gate)
5. **Florentino Gate (TIL Step 1):** Submit this PRD for scope/value review

---

## Appendix A: IPL Era Analysis — Why 2023 Is the Cutoff (Founder-Approved)

This analysis was produced from ball-by-ball DuckDB queries on 2026-02-11 and reviewed by the Founder. It provides the empirical basis for Founder Decision #6.

### IPL Metrics by Season (1,169 matches, 2008-2025)

| Season | Matches | Run Rate | Boundary% | Six% | Four% | W/Over | Dot% |
|--------|---------|----------|-----------|------|-------|--------|------|
| 2007/08 | 58 | 7.98 | 17.2 | 4.62 | 12.63 | 0.307 | 36.4 |
| 2009 | 57 | 7.20 | 13.4 | 3.72 | 9.69 | 0.308 | 37.6 |
| 2009/10 | 60 | 7.81 | 15.8 | 4.04 | 11.79 | 0.299 | 34.5 |
| 2011 | 73 | 7.46 | 15.0 | 3.76 | 11.26 | 0.287 | 36.9 |
| 2012 | 74 | 7.58 | 14.9 | 4.13 | 10.76 | 0.290 | 35.1 |
| 2013 | 76 | 7.45 | 15.0 | 3.72 | 11.30 | 0.301 | 37.2 |
| 2014 | 60 | 7.94 | 15.9 | 5.00 | 10.93 | 0.282 | 35.1 |
| 2015 | 59 | 8.06 | 16.9 | 5.07 | 11.78 | 0.302 | 35.0 |
| 2016 | 60 | 8.03 | 16.1 | 4.53 | 11.58 | 0.283 | 33.0 |
| 2017 | 59 | 8.13 | 16.7 | 5.09 | 11.63 | 0.307 | 32.8 |
| 2018 | 60 | 8.36 | 17.7 | 6.10 | 11.56 | 0.303 | 33.3 |
| 2019 | 60 | 8.14 | 17.1 | 5.49 | 11.57 | 0.286 | 34.5 |
| 2020/21 | 60 | 8.00 | 16.0 | 5.07 | 10.91 | 0.276 | 33.5 |
| 2021 | 60 | 7.75 | 15.5 | 4.77 | 10.75 | 0.298 | 34.8 |
| 2022 | 74 | 8.17 | 17.2 | 5.93 | 11.28 | 0.305 | 35.5 |
| **2023** | **74** | **8.63** | **18.5** | **6.29** | **12.18** | **0.308** | **32.6** |
| **2024** | **71** | **9.11** | **20.1** | **7.37** | **12.72** | **0.310** | **31.4** |
| **2025** | **74** | **9.21** | **20.6** | **7.53** | **13.08** | **0.303** | **30.9** |

### Era Aggregation — Where the Game Changed

| Era | Matches | Run Rate | Boundary% | Six% | Four% | W/Over | Dot% |
|-----|---------|----------|-----------|------|-------|--------|------|
| 2008-2012 | 322 | 7.60 | 15.2 | 4.04 | 11.20 | 0.297 | 36.1 |
| 2013-2017 | 314 | 7.90 | 16.1 | 4.63 | 11.44 | 0.295 | 34.8 |
| 2018-2020 | 180 | 8.17 | 16.9 | 5.55 | 11.34 | 0.288 | 33.8 |
| 2021-2022 | 134 | 7.98 | 16.5 | 5.41 | 11.04 | 0.302 | 35.2 |
| **2023-2025** | **219** | **8.98** | **19.7** | **7.06** | **12.65** | **0.307** | **31.6** |

### The Structural Break: Era-over-Era Deltas

| Transition | RR Change | Boundary Change | Six% Change |
|---|---|---|---|
| 2008-12 → 2013-17 | +0.30 | +0.9 | +0.59 |
| 2013-17 → 2018-20 | +0.27 | +0.8 | +0.92 |
| 2018-20 → 2021-22 | -0.19 | -0.4 | -0.14 |
| **2021-22 → 2023-25** | **+1.00** | **+3.2** | **+1.65** |

The jump from 2021-22 to 2023-25 is **3-4x larger** than any previous era transition across every metric simultaneously.

### Head-to-Head: IPL 2023-2025 vs IPL 2008-2022

| Metric | IPL 2008-2022 (950 matches) | IPL 2023-2025 (219 matches) | Delta | Relative Change |
|--------|----------------------------|----------------------------|-------|-----------------|
| Run Rate | 7.86 | 8.98 | +1.12 | **+14.2%** |
| Boundary% | 16.0 | 19.7 | +3.7 | **+23.1%** |
| Six% | 4.72 | 7.06 | +2.34 | **+49.6%** |
| Four% | 11.28 | 12.65 | +1.37 | +12.1% |
| Wickets/Over | 0.296 | 0.307 | +0.011 | +3.7% |
| Dot Ball% | 35.1 | 31.6 | -3.5 | **-10.0%** |

### Drivers of the 2023 Structural Break

1. **Impact Player rule** (introduced IPL 2023) — allows a substitute specialist, effectively giving teams 12 players. This directly inflates batting depth and scoring rates.
2. **Mega auction reset** (2022) — team compositions fundamentally reshuffled, rendering pre-2023 team-level context obsolete.
3. **Evolved batting intent** — six-hitting up 49.6%, dot ball% down 10%. Batters attack from ball one in the modern IPL.
4. **Pitch and ground changes** — newer venues and conditions favoring higher scoring.

### Founder Decision

Based on this data, the Founder has locked in **IPL 2023-2025 as the conditions baseline** for all Factor 4 calculations in the tournament weighting system. This is consistent with the `_since2023` analytical window used across all 80 dual-scope views in the analytics pipeline.

---

*Cricket Playbook v4.0.0 | Constitution v2.2.0 | Task Integrity Loop v1.0.0*
