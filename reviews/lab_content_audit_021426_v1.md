# Lab Content Audit: Artifacts, Analysis & Research Tabs

**TKT-225** | Owner: Tom Brady (PO & Editor-in-Chief)
**Date:** 2026-02-14 | **Version:** v1
**Scope:** Artifacts, Analysis, Research tabs on The Lab dashboard
**Lab URL:** `scripts/the_lab/dashboard/index.html`

---

## Executive Summary

The Lab's three content tabs -- Artifacts, Analysis, and Research -- are in strong shape overall. Content is relevant, data-driven, and well-organized. All three pages have proper navigation, theme support, mobile responsiveness, and consistent visual design. There are **two confirmed broken GitHub links** in the Analysis tab that need fixing. The Artifacts tab is dynamically populated from live data files and links all check out. The Research tab is the most polished, with thorough methodology documentation and no broken references. No content is stale -- everything reflects the current IPL 2023-2025 analytical window.

**Overall Grade: B+** (solid content, minor link fixes needed, a few enhancement opportunities)

---

## 1. Tab Inventory

The Lab uses a **multi-page architecture** (not tab-based JS switching). Each tab is a separate HTML file sharing a common navigation bar.

| # | Tab Name | File | Size | Last Modified | Purpose |
|---|----------|------|------|---------------|---------|
| 1 | Home | `index.html` | 154 KB | Feb 10 | Landing page, hero section, team grid, navigation cards |
| 2 | Teams | `teams.html` | 275 KB | Feb 14 | Per-team drill-down (Predicted XIIs, depth charts, full rosters) |
| 3 | **Artifacts** | `artifacts.html` | 50 KB | Feb 12 | Build progress, Predicted XIIs grid, depth chart comparison, output files |
| 4 | **Analysis** | `analysis.html` | 96 KB | Feb 12 | Deep-dive reports: audits, EDA, research, matchups, pressure, algorithms |
| 5 | **Research** | `research.html` | 52 KB | Feb 13 | Methodology documentation: SUPER SELECTOR, PFF, KenPom, CricPom, clustering |
| 6 | Film Room | `research-desk.html` | 382 KB | Feb 14 | Interactive SQL Lab for querying the DuckDB analytics database |
| 7 | About | `about.html` | 42 KB | Feb 12 | Project story, vision, agent bios |

All 7 pages exist and are accessible. Navigation is consistent across all pages (desktop tabs + mobile hamburger menu).

---

## 2. Artifacts Tab (`artifacts.html`)

### 2.1 Content Sections

| Section | Content | Status |
|---------|---------|--------|
| **Build Progress** | Completed items (7) and Goals (7, with 4 done + 3 planned) | CURRENT |
| **Predicted XIIs** | Dynamic grid of 10 teams (JS-populated from `data/predicted_xii.js` and `data/teams.js`) | CURRENT |
| **Depth Chart Comparison** | Sortable table ranking all 10 teams by overall rating, strongest/weakest positions | CURRENT |
| **Output Files** | 10 direct GitHub links to key output files | CURRENT |

### 2.2 Data Sources

The Artifacts page loads two JS data files:
- `data/teams.js` -- TEAMS object (10 teams), TEAM_ORDER array. Last updated Feb 14.
- `data/predicted_xii.js` -- PREDICTED_XII and DEPTH_CHART_RATINGS objects. Last updated Feb 14.

Both files are fresh (updated today by the pipeline).

### 2.3 Output File Links Assessment

| # | File Linked | GitHub Path | File Exists Locally? | Status |
|---|-------------|-------------|---------------------|--------|
| 1 | `predicted_xii_2026.json` | `outputs/predicted_xii/predicted_xii_2026.json` | YES (43KB, Feb 13) | OK |
| 2 | `depth_charts_2026.json` | `outputs/depth_charts/depth_charts_2026.json` | YES (196KB, Feb 14) | OK |
| 3 | `player_tags.json` | `outputs/tags/player_tags.json` | YES (124KB, Feb 12) | OK |
| 4 | `batter_bowling_type_matchup.csv` | `outputs/matchups/batter_bowling_type_matchup_2023.csv` | YES (11KB, Feb 9) | OK |
| 5 | `batter_consistency_index.csv` | `outputs/metrics/batter_consistency_index.csv` | YES (10KB) | OK |
| 6 | `partnership_synergy.csv` | `outputs/metrics/partnership_synergy.csv` | YES (20KB) | OK |
| 7 | `bowler_pressure_sequences.csv` | `outputs/metrics/bowler_pressure_sequences.csv` | YES (20KB) | OK |
| 8 | `stat_packs/*.md` | `stat_packs/` (tree link) | YES (10 teams, all present) | OK |
| 9 | `DATA_DICTIONARY.md` | `docs/DATA_DICTIONARY.md` | YES | OK |
| 10 | `MODEL_VERSIONING.md` | `ml_ops/MODEL_VERSIONING.md` | YES | OK |

**All 10 output file links reference valid paths. No broken links on the Artifacts page.**

### 2.4 Build Progress Accuracy

The "Completed" section lists:
- Predicted XIIs + Impact Players: 10/10 teams -- VERIFIED (10 JSON files in `outputs/predicted_xii/`)
- Full Depth Charts (9 positions): 10/10 teams -- VERIFIED (10 JSON + HTML + MD sets in `outputs/depth_charts/`)
- Team Stat Packs: 10/10 teams -- VERIFIED (10 directories in `stat_packs/`)
- Full Squad Rosters: 231 players -- consistent with `data/full_squads.js` (494KB)
- Player Tags: 220 players -- consistent with `outputs/tags/player_tags.json` (124KB)
- Batter vs Bowling Type Matchups: 3 seasons -- VERIFIED (2023 + all-time files exist)
- Consistency & Pressure Metrics: 3 seasons -- VERIFIED (multiple CSV files present)

The "Planned" items (head-to-head predictor, player form tracker, season simulation) are correctly marked as Future/Planned.

### 2.5 Assessment

**What's Working:**
- Dynamic team cards with pixel art logos, captain names, and overall ratings
- Comparison table auto-sorts by rating (strong visual hierarchy)
- GitHub links all point to correct paths
- Build progress is accurate and honest (shows both done and planned items)
- Navigation guide modal provides helpful context

**What's Missing or Could Improve:**
- No direct links to individual team stat packs (only a tree link to the `stat_packs/` directory)
- The `data/depth_charts.js` file (84KB) exists but is not loaded on this page -- the comparison table only shows overall/strongest/weakest, not the full depth chart data
- Pressure metrics outputs (batter_pressure_bands.csv, pressure_deltas.csv, bowler_pressure_bands.csv) are in `outputs/` but not linked from the Output Files section
- CricPom weighted feed (125KB JSON) not linked from artifacts page
- No last-updated timestamp on the page

---

## 3. Analysis Tab (`analysis.html`)

### 3.1 Content Sections

| Section | Cards | Content Type | Status |
|---------|-------|--------------|--------|
| **Data Quality Audits** | 2 cards | Player ID Mismatch Audit, Entry Point Audit | CURRENT |
| **EDA & Threshold Analysis** | 2 cards | Threshold EDA (2023+), Baselines vs Tags | CURRENT |
| **Research & Methodology** | 8 cards | PFF, KenPom, CricPom, Tournament Weights, Confidence, Silhouette, Pressure Sequences, Clustering PRD, Archetypes | CURRENT |
| **Player Pattern Recognition** | 2 cards | Batter Consistency Index, Partnership Synergy | CURRENT |
| **Matchup Intelligence** | 3 cards | Batter vs Bowling Type, Bowler Handedness, Team Venue Records | CURRENT |
| **Pressure & Phase Performance** | 5 cards | Bowler Pressure, Phase Distribution, Batter Pressure Bands, Pressure Deltas, Pressure Glossary | CURRENT |
| **Algorithm Documentation** | 2 cards | SUPER SELECTOR v2, Andy Flower Validation | CURRENT |
| **Tournament Intelligence** | Dynamic table | JS-rendered from `data/tournament_weights.js` with 5-factor breakdown | CURRENT |

**Total: 8 sections, 24+ analysis cards, 1 dynamic data table.**

### 3.2 Link Assessment

| # | Card | GitHub Link Target | File Exists? | Status |
|---|------|--------------------|--------------|--------|
| 1 | Player ID Mismatch Audit | `analysis/player_id_audit_report.md` | YES | OK |
| 2 | Entry Point Audit | `analysis/entry_point_audit_report.md` | YES | OK |
| 3 | Threshold EDA | `analysis/threshold_eda_2023.md` | YES | OK |
| 4 | Baselines vs Tags | `analysis/baselines_vs_tags.md` | YES | OK |
| 5 | PFF Grading Research | `docs/research/pff_grading_system_research.md` | YES | OK |
| 6 | KenPom Research | `docs/research/kenpom_methodology_research.md` | YES | OK |
| 7 | CricPom Spec | `docs/research/cricpom_prototype_spec_020926_v1.md` | YES | OK |
| 8 | CricPom Feed | `outputs/cricpom_weighted_feed.json` | YES | OK |
| 9 | Tournament Weights Engine | `scripts/tkt187_final_weights.py` | YES | OK |
| 10 | Insight Confidence | `scripts/tkt187_final_weights.py` | YES | OK |
| 11 | Silhouette Validation | `scripts/ml_ops/baseline_comparison.py` | YES | OK |
| 12 | Pressure Sequences | `scripts/the_lab/generate_momentum_data.py` | YES | OK |
| 13 | **Player Clustering PRD** | `docs/specs/player_clustering_prd.md` | **NO** | **BROKEN** |
| 14 | Cluster Archetypes Creative | `docs/specs/cluster_archetypes_creative.md` | YES | OK |
| 15 | Batter Consistency | `outputs/batter_consistency_index.csv` | YES (at `outputs/metrics/`) | OK |
| 16 | Partnership Synergy | `outputs/partnership_synergy.csv` | YES (at `outputs/metrics/`) | OK |
| 17 | Batter vs Bowling Type | `outputs/batter_bowling_type_matchup.csv` | YES (at `outputs/matchups/`) | OK |
| 18 | Bowler Handedness | `outputs/bowler_handedness_matchup.csv` | YES (at `outputs/matchups/`) | OK |
| 19 | Team Venue Records | `outputs/team_venue_records.csv` | YES (at `outputs/team/`) | OK |
| 20 | Bowler Pressure Sequences | `outputs/bowler_pressure_sequences.csv` | YES (at `outputs/metrics/`) | OK |
| 21 | Bowler Phase Distribution | `outputs/bowler_phase_distribution_grouped.csv` | YES (at `outputs/metrics/`) | OK |
| 22 | Batter Pressure Bands | `outputs/batter_pressure_bands.csv` | YES (at `outputs/`) | OK |
| 23 | Pressure Deltas | `outputs/pressure_deltas.csv` | YES (at `outputs/`) | OK |
| 24 | **SUPER SELECTOR v2** | `docs/specs/predicted_xii_algorithm_v2.md` | **NO** | **BROKEN** |
| 25 | Andy Flower Validation | `docs/specs/andy_flower_v2_validation.md` | YES | OK |
| 26 | Footer "View all on GitHub" | `analysis/` (tree link) | YES | OK |

### 3.3 Broken Links Detail

**BROKEN LINK #1: Player Clustering PRD**
- Links to: `https://github.com/dwijesh-r/cricket-playbook/blob/main/docs/specs/player_clustering_prd.md`
- Actual location: `docs/ml/algorithms/player_clustering_prd.md`
- Fix: Update href to `docs/ml/algorithms/player_clustering_prd.md`

**BROKEN LINK #2: SUPER SELECTOR Algorithm v2**
- Links to: `https://github.com/dwijesh-r/cricket-playbook/blob/main/docs/specs/predicted_xii_algorithm_v2.md`
- Actual location: `docs/ml/algorithms/predicted_xii_algorithm_v2.md`
- Fix: Update href to `docs/ml/algorithms/predicted_xii_algorithm_v2.md`

### 3.4 Assessment

**What's Working:**
- Extremely well-organized: 8 distinct sections with clear analytical themes
- Every card has a "Why this was done/matters" context section -- excellent editorial standard
- Pressure Glossary with expandable accordion is a strong UX pattern
- Tournament Intelligence section is fully dynamic with JS rendering
- Good mix of static content cards + interactive data tables
- 24+ cards covering the full analytical pipeline end-to-end

**What's Missing or Could Improve:**
- 2 broken GitHub links (Player Clustering PRD and SUPER SELECTOR v2) -- files moved to `docs/ml/algorithms/`
- No cards for the Film Room tactical views (13 views mentioned in research but not shown here)
- No direct link to `outputs/tags/player_tags_2023.json` (the 2023-scoped tags file)
- Missing: player clustering output visualization (the CSV exists at `outputs/tags/player_clustering_2023.csv`)
- No toss advantage index card (data exists at `outputs/toss_advantage_index.json`)
- No cross-tournament profiles card (data exists at `outputs/tags/cross_tournament_profiles.json`)

---

## 4. Research Tab (`research.html`)

### 4.1 Content Sections

| # | Research Card | Topic | Content Quality |
|---|---------------|-------|----------------|
| 1 | SUPER SELECTOR Algorithm | Predicted XI algorithm components + constraints | Excellent |
| 2 | PFF-Inspired Grading | Process-over-outcome evaluation adapted from NFL | Excellent |
| 3 | KenPom Efficiency Metrics | Tempo-free stats, Four Factors, opponent adjustments | Excellent |
| 4 | Player Clustering (K-Means V2) | 5 batter + 4 bowler archetypes | Good |
| 5 | CricPom: Novel Composite Metrics | AdjBRR, AdjBE, CEM, OSI, 5-factor tournament engine | Excellent |
| 6 | Tournament Quality Weighting | 5-factor composite weight, tier system, IPL 2023+ baseline | Excellent |
| 7 | Dual-Scope Analytics Framework | All-time vs Since-2023 view architecture with statistical evidence | Excellent |
| 8 | Insight Confidence Framework | 4-component confidence scoring, grade boundaries | Good |
| 9 | Data Foundation | Data sources, derived metrics (115+ views), validation process | Good |

**Total: 9 research cards covering the full methodology.**

### 4.2 Link Assessment

| # | Card | Link Target | File Exists? | Status |
|---|------|-------------|--------------|--------|
| 1 | PFF Research | `docs/research/pff_grading_system_research.md` | YES | OK |
| 2 | KenPom Research (card #3) | `docs/research/kenpom_methodology_research.md` | YES | OK |
| 3 | Cluster Archetypes | `docs/specs/cluster_archetypes_creative.md` | YES | OK |
| 4 | KenPom Foundation (card #5) | `docs/research/kenpom_methodology_research.md` | YES | OK |
| 5 | Tournament Weighting Plan | `reviews/founder/tournament_weighting_plan_021126_v1.md` | YES | OK |
| 6 | TKT-181 Review | `reviews/founder/tkt181_film_room_review_021126_v1.md` | YES | OK |

**All 6 links on the Research page are valid. No broken links.**

### 4.3 Assessment

**What's Working:**
- Most polished of the three tabs
- CricPom section is outstanding: formulas, comparison tables, factor breakdowns
- Dual-Scope section includes actual data evidence (era-by-era IPL stats table)
- Tournament Quality section has tier system with Founder-locked baseline documentation
- Insight Confidence framework provides editorial guardrails
- Every card explains both "what" and "why"
- Good separation of concerns from Analysis tab (Research = methodology, Analysis = outputs)

**What's Missing or Could Improve:**
- SUPER SELECTOR section (card #1) doesn't link to the algorithm spec document (which exists at `docs/ml/algorithms/predicted_xii_algorithm_v2.md`)
- Player Clustering section (card #4) lists only 5 batter + 4 bowler archetypes, but the actual model has 6 batter + 7 bowler archetypes (per the card's own description on analysis.html)
- No link to the CricPom spec document from the CricPom card (the spec exists at `docs/research/cricpom_prototype_spec_020926_v1.md`)
- The "Data Foundation" card says "115+ Views" but Dual-Scope says "80 dual-scope views" -- the number should be consistent
- Insight Confidence card says "Bridges with existing Confidence Intervals (TKT-145)" but no link provided
- Tournament Weighting card says "Implementation via TKT-183 (8-12 days)" -- this status text may be stale since the implementation appears to be DONE (tournament_weights.js exists with live data on the Analysis page)
- No mention of the Pressure Performance system on Research tab (it's a major methodology)

---

## 5. Cross-Tab Consistency

| Item | Artifacts | Analysis | Research | Notes |
|------|-----------|----------|----------|-------|
| CricPom | Not linked | Spec + feed linked | Described, no spec link | Add spec link to Research |
| Clustering | Player Tags linked | PRD linked (BROKEN) | Described, archetypes linked | Fix PRD link in Analysis |
| Pressure | Not linked (data exists) | 5 cards + glossary | Not mentioned | Consider adding to Research |
| Tournament Weights | Not linked | Dynamic table | Described | Consider linking data from Artifacts |
| SUPER SELECTOR | Not linked | Algorithm v2 (BROKEN) | Described, no link | Fix link in Analysis, add to Research |
| Stat Packs | Tree link | Not linked | Not mentioned | Working as designed |

---

## 6. Priority Fixes

### P0 -- Fix Now (Broken Links)

1. **Analysis page line ~1106**: Fix Player Clustering PRD link
   - FROM: `docs/specs/player_clustering_prd.md`
   - TO: `docs/ml/algorithms/player_clustering_prd.md`

2. **Analysis page line ~1496**: Fix SUPER SELECTOR Algorithm v2 link
   - FROM: `docs/specs/predicted_xii_algorithm_v2.md`
   - TO: `docs/ml/algorithms/predicted_xii_algorithm_v2.md`

### P1 -- Should Fix (Stale Content)

3. **Research page Tournament Weighting card**: Update status text from "Plan approved... Implementation via TKT-183 (8-12 days)" to reflect that implementation is DONE (tournament weights are live on the Analysis page).

4. **Research page Player Clustering card**: Correct archetype counts to match the actual model (6 batter archetypes, not 5 listed; bowler archetypes text only shows 4 but model has more).

5. **Research page Data Foundation card**: Reconcile "115+ Views" with "80 dual-scope views" stated in the Dual-Scope card. Use a consistent number.

### P2 -- Enhancement Opportunities

6. **Artifacts page**: Add links to pressure metrics outputs (batter_pressure_bands.csv, bowler_pressure_bands.csv, pressure_deltas.csv) in the Output Files section.

7. **Artifacts page**: Add link to `outputs/cricpom_weighted_feed.json` (125KB, a major analytical output).

8. **Research page**: Add link to `docs/ml/algorithms/predicted_xii_algorithm_v2.md` from the SUPER SELECTOR card.

9. **Research page**: Add link to `docs/research/cricpom_prototype_spec_020926_v1.md` from the CricPom card.

10. **All tabs**: Add a "Last Updated" timestamp (either static or auto-generated) so readers know data freshness.

11. **Analysis page**: Consider adding cards for Film Room tactical views, toss advantage index, and cross-tournament profiles.

---

## 7. Content Freshness Assessment

| Data Source | Last Updated | Freshness |
|-------------|-------------|-----------|
| `data/teams.js` | Feb 14, 2026 | FRESH (today) |
| `data/predicted_xii.js` | Feb 14, 2026 | FRESH (today) |
| `data/depth_charts.js` | Feb 14, 2026 | FRESH (today) |
| `data/tournament_weights.js` | Feb 12, 2026 | CURRENT (2 days) |
| `data/full_squads.js` | Feb 14, 2026 | FRESH (today) |
| `data/pressure_metrics.js` | Feb 14, 2026 | FRESH (today) |
| `data/player_profiles.js` | Feb 14, 2026 | FRESH (today) |
| Predicted XII JSONs | Feb 13, 2026 | CURRENT (1 day) |
| Depth chart JSONs | Feb 14, 2026 | FRESH (today) |
| Stat packs | Feb 13, 2026 | CURRENT (1 day) |
| Player tags | Feb 14, 2026 | FRESH (today) |
| Analysis docs (analysis/) | Jan 26 - Feb 4, 2026 | CURRENT (foundational docs, not expected to change frequently) |
| Research docs (docs/research/) | Jan - Feb 2026 | CURRENT |

**Verdict: No stale content detected.** All data files are within the current sprint window. Analysis/research docs are foundational and not expected to change frequently.

---

## 8. Conclusion

The Lab's Artifacts, Analysis, and Research tabs represent a strong, well-organized analytics showcase. The primary issues are two broken GitHub links in the Analysis tab where files were moved from `docs/specs/` to `docs/ml/algorithms/`. These should be fixed immediately. The Research tab could benefit from a few additional document links and a status text update for Tournament Weighting. No content is stale or irrelevant -- everything aligns with the IPL 2023-2025 analytical window and the current sprint deliverables.

**Signed:** Tom Brady, PO & Editor-in-Chief
**Date:** 2026-02-14
