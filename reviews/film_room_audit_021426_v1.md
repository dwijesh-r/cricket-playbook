# Film Room (Research Desk) Audit & Sprint 5 NL Search Improvement Scope

**TKT-226 | Auditor: Jose Mourinho (Quant Researcher)**
**Date: 2026-02-14 | Version: 1.0**

---

## 1. Film Room Status Audit

### 1.1 Component Status Matrix

| Component | Status | Notes |
|-----------|--------|-------|
| SQL Editor | **PASS** | Textarea-based editor with syntax highlighting styles. CodeMirror 6 was removed (ESM CDN hangs on GitHub Pages); textarea fallback works reliably. Ctrl+Enter shortcut wired. |
| Execute Button | **PASS** | `#run-button` present, wired to `executeQueryWithInsights()`. Disabled until DB initializes. |
| Schema Browser | **PASS** | Interactive sidebar (`#schema-browser`, TKT-175). Tables and views shown with column types, descriptions, row counts. Click-to-expand columns, click-to-insert column names, SQL button for quick `SELECT * LIMIT 100`. Schema search filters by table/view/column/description. |
| View Catalog | **PASS** | 163 views loaded from `views.sql`. Views split into categorized groups by scope (alltime/since2023). View Coverage Matrix (`VIEW_COVERAGE`) maps 80+ views for NL routing. |
| NL Search Bar | **PASS** | Full NL-to-SQL pipeline with 5-stage architecture (TKT-185). Search bar with placeholder chips, typeahead, disambiguation. Auto-executes after translation. |
| Export Functionality | **PASS** | CSV export via `exportCSV()` function. Clipboard copy of SQL via navigator.clipboard API. Download generates timestamped CSV file. |
| DuckDB WASM | **PASS** | v1.29.0 loaded from jsdelivr CDN with 15-second timeout fallback. Progressive loading overlay with step indicators. |
| Data Loading | **PASS** | 16 tables registered in `TABLE_FILES` array. Parquet files loaded via HTTP range requests from `data/sql_lab/tables/`. Total: 2,380,107 data points per metadata. |
| Theme Support | **PASS** | Dark/light toggle with CSS custom properties. Mobile responsive with hamburger menu for schema sidebar. |
| Example Queries | **PASS** | Gallery of categorized example queries (TKT-176): leaderboard, batting, bowling, team, matchup, venue, advanced categories. Quick-start queries in schema sidebar. |
| Error Handling | **PASS** | `showError()` renders error panel with elapsed time. DB disconnect detection. CDN timeout handling. Dismiss button on initialization failure. |
| Query Explanation | **PASS** | After NL search, shows "Understood" panel with extracted entities, intent, view used, and result count. |
| Win/Loss Comparison | **PASS** | Side-by-side card layout for wins vs losses when `match_result` split is detected. Delta chips show performance differences. |
| Insights Panel | **PASS** | `updateFirstTakeInsight()` auto-generates analytical commentary after query execution. |

### 1.2 Data Completeness

| Artifact | Expected | Actual | Status |
|----------|----------|--------|--------|
| `views.sql` | 163 views | 163 `CREATE OR REPLACE VIEW` statements | **PASS** |
| Parquet files | 16 tables | 17 files on disk (16 in TABLE_FILES) | **MINOR GAP** |
| `table_metadata.json` | 16 tables + 163 views | 16 tables + 163 views documented | **PASS** |
| Total rows | 2,380,107 | 2,380,107 (per metadata) | **PASS** |
| Parquet size | ~15 MB | 15.27 MB | **PASS** |

**Minor Gap:** `dim_tournament_weights.parquet` exists on disk (17th file) but is NOT included in `TABLE_FILES` and therefore not loaded into DuckDB WASM. This table is used by the `analytics_weighted_composite_batting` and `analytics_weighted_composite_bowling` views, which will fail at runtime unless the view definitions handle the missing table gracefully. **Recommendation:** Add `dim_tournament_weights` to `TABLE_FILES` in Sprint 5.

---

## 2. NL Search Capabilities Assessment

### 2.1 Architecture Overview

The NL Search is a **client-side, rule-based 5-stage pipeline** (no LLM/API calls):

1. **Entity Extraction** (`extractEntities`): Regex + dictionary-based. Extracts players, teams, phases, venues, seasons, metrics, bowler types, and context modifiers (win/loss, innings, stage, total context).
2. **Intent Classification** (`classifyIntent`): Rule-based priority chain. Returns one of 12 intents: `PLAYER_LOOKUP`, `MATCHUP`, `LEADERBOARD`, `TEAM_ANALYSIS`, `TEAM_COMPARISON`, `COMPARISON`, `PRESSURE`, `SEASON_TREND`, `CONTRACTS`, `SQUAD`, `OVERSEAS`, `EXPLORATORY`.
3. **View Coverage** (fast path): Finds the best pre-built view matching the required dimensions. 80+ views mapped in `VIEW_COVERAGE` matrix with scope awareness (alltime/since2023).
4. **Dynamic SQL Generation** (fallback): `QueryBuilder` class generates SQL from `fact_ball` with JOINs when context modifiers are present (win/loss, innings, stage, total context) and no pre-built view suffices.
5. **Validation + Fallback**: Disambiguation for ambiguous player names. Fallback suggestions with "what I understood" panel.

### 2.2 What Works (Strengths)

| Capability | Quality | Details |
|------------|---------|---------|
| **Player name resolution** | **Excellent** | 150+ aliases mapped. Handles nicknames (e.g., "Virat" -> "V Kohli", "boom" -> "JJ Bumrah", "thala" -> "MS Dhoni", "sky" -> "SA Yadav"), full names, abbreviations. Fuzzy matching via Levenshtein distance for typos. |
| **Team alias resolution** | **Excellent** | All 10 IPL franchises with abbreviations, full names, historical names (e.g., "dd" -> Delhi Capitals, "kxip" -> Punjab Kings, "deccan" -> Sunrisers Hyderabad). |
| **Simple player lookups** | **Excellent** | "Kohli stats", "Bumrah bowling" -> routes to correct career view. |
| **Phase filtering** | **Excellent** | "death overs", "powerplay", "middle" recognized and filtered. Phase breakdown supported. |
| **Matchup queries** | **Excellent** | "Kohli vs Bumrah" -> routes to batter_vs_bowler view with correct filters. Phase-augmented matchups supported. |
| **Player vs team** | **Excellent** | "Kohli vs MI" -> correct view with opposition filter. |
| **Player vs bowler type** | **Very Good** | "Kohli vs spin" -> batter_vs_bowler_type view. |
| **Leaderboard queries** | **Very Good** | "top run scorers", "best death bowlers", "highest strike rates" -> correct view with minimum sample filters. |
| **Team analysis** | **Very Good** | "CSK squad", "MI batting", "RCB bowling in death" -> correct squad/analysis views. |
| **Venue filtering** | **Very Good** | "at Wankhede", "Chinnaswamy" recognized via venue alias map. |
| **Season filtering** | **Good** | "since 2023", "2024 season" -> correct time-scoped views or season filters. |
| **Context modifiers** | **Good** | Win/loss splits, batting first/chasing, playoff/final stage, total context (score > 180) -> routes to QueryBuilder. |
| **Pressure queries** | **Very Good** | "Kohli under pressure", "clutch batters" -> pressure band views. Dot sequences, pressure ratings supported. |
| **Contract queries** | **Good** | "most expensive", "cheapest players", "CSK auction spend" -> ipl_2026_contracts. |
| **Disambiguation** | **Good** | Ambiguous names (e.g., "Iyer" could be SS Iyer or VR Iyer) trigger a selection card. |
| **Error recovery** | **Good** | On no match: shows "what I understood" + related suggestions + available analyses for detected entities. |

### 2.3 What Does NOT Work (Gaps)

| Gap | Severity | Details |
|-----|----------|---------|
| **No autonomous reasoning** | **HIGH** | The system is 100% rule-based. It cannot reason about novel queries, infer intent from ambiguous phrasing, or compose queries it hasn't been programmed to handle. No LLM integration. |
| **No cross-table joins in NL** | **MEDIUM** | NL search can only route to pre-built views OR build dynamic SQL from `fact_ball` base table. It cannot compose arbitrary multi-table JOINs (e.g., "bowlers who played for CSK and now play for MI"). |
| **No complex aggregation patterns** | **MEDIUM** | GROUP BY and HAVING are used internally by the QueryBuilder, but users cannot express arbitrary aggregation patterns via NL (e.g., "average runs per over by phase per season" or "players with increasing strike rates over last 3 seasons"). |
| **No subquery support** | **MEDIUM** | Cannot handle nested logic (e.g., "batters who scored more than the team average", "bowlers with economy below the median"). |
| **No comparative analytics** | **MEDIUM** | "Compare Kohli and Rohit" with two batters is not fully supported (matchup assumes batter vs bowler pairing). Two-batter comparison requires manual SQL. |
| **No temporal reasoning** | **MEDIUM** | Cannot interpret "last 5 matches", "recent form vs career form", or "form trajectory". Recent form views exist but NL routing to them is limited. |
| **No statistical functions** | **LOW** | Cannot interpret "correlation between strike rate and boundaries", "percentile rank of X", "standard deviation". Percentile views exist but NL discovery is weak. |
| **No query composition** | **LOW** | Cannot chain queries (e.g., "who has the best record against top-5 bowlers at Wankhede in death overs"). |
| **Limited venue intelligence** | **LOW** | Venue aliases cover major grounds but may miss alternate spellings or colloquial names. |
| **No UNION/INTERSECT** | **LOW** | Cannot combine result sets (e.g., "batters who are good in powerplay AND death"). |
| **No query history** | **LOW** | No persistence of previous queries, no favorites, no recently-used tracking. |
| **No typeahead for view names** | **LOW** | NL search typeahead exists for example queries but not for direct view name completion. |

### 2.4 Autonomy Assessment

**Verdict: Template-match with structured fallback, NOT autonomous.**

The system does NOT "think." It follows a deterministic decision tree:
1. Extract entities via regex/dictionary lookup.
2. Classify intent via keyword priority rules.
3. Route to the best-matching pre-built view OR build dynamic SQL from a fixed QueryBuilder template.
4. If no route matches, show fallback suggestions.

There is no inference, no reasoning, no probabilistic matching, and no API call to an LLM. The QueryBuilder (Phase 2, TKT-185) adds dynamic SQL generation from `fact_ball`, but only for a fixed set of filter dimensions (win/loss, innings, stage, total context, phase, venue, season, bowler type). It cannot compose novel queries outside its programmed patterns.

---

## 3. Sprint 5 Improvement Proposals

### P1: Claude API Integration for Autonomous Query Generation

**Objective:** Add an optional LLM-powered path for queries the rule-based system cannot handle.

| Attribute | Value |
|-----------|-------|
| Priority | **P0** |
| Effort | **L** (Large) |
| Dependencies | Claude API key, API proxy for CORS, token budget governance |

**Proposed Design:**
- When the rule-based pipeline returns `EXPLORATORY` (no match), offer a "Deep Analysis" button that sends the query + schema context to Claude API.
- Claude receives: table schemas, view catalog, and the user's natural language question.
- Claude returns: validated DuckDB-compatible SQL.
- Safety: SQL is displayed for user review before execution. Read-only queries only (block INSERT/UPDATE/DELETE/DROP).
- Token accounting: Track API calls per session, cap at configurable limit.
- Fallback: If API unavailable, current rule-based system continues to operate.

**Risk:** Adds external dependency, latency, and cost. Requires API key management in a client-side app (proxy needed).

### P2: Enhanced Aggregation Patterns (GROUP BY, HAVING, Window Functions)

**Objective:** Allow NL queries like "average runs per season", "players with increasing strike rate over 3 seasons", "top 5 by percentile rank".

| Attribute | Value |
|-----------|-------|
| Priority | **P1** |
| Effort | **M** (Medium) |
| Dependencies | None (extends existing QueryBuilder) |

**Proposed Design:**
- Add aggregation intent detection: "average X by Y", "X per Y", "grouped by Z".
- Extend QueryBuilder with window function templates: `RANK()`, `PERCENT_RANK()`, `LAG()`, `LEAD()`.
- Add "trend" intent: detect "increasing", "declining", "consistent" and generate season-over-season comparisons.
- Map to existing percentile views where applicable.

### P3: Cross-Table Join Support

**Objective:** Enable NL queries that require joining tables not covered by pre-built views.

| Attribute | Value |
|-----------|-------|
| Priority | **P1** |
| Effort | **M** (Medium) |
| Dependencies | Enhanced entity extraction |

**Proposed Design:**
- Build a JOIN graph that maps table relationships (foreign keys, common columns).
- When NL query requires dimensions from multiple tables, auto-compose JOIN chain.
- Priority joins: `fact_ball` -> `dim_player`, `dim_match`, `dim_team`, `dim_venue`, `dim_tournament`, `ipl_2026_squads`, `dim_bowler_classification`.
- Safety: Limit join depth to 4 tables max. Require at least one WHERE filter to prevent cartesian products.

### P4: Better Player Name Resolution

**Objective:** Handle players NOT in the alias dictionary, improve fuzzy matching, support team-contextualized lookups.

| Attribute | Value |
|-----------|-------|
| Priority | **P2** |
| Effort | **S** (Small) |
| Dependencies | None |

**Proposed Design:**
- **Dynamic alias loading:** At init time, build alias map from `dim_player.current_name` and `dim_player_name_history` tables. Eliminates hardcoded dictionary maintenance.
- **Team-scoped disambiguation:** When a player name is ambiguous but a team is also mentioned, filter candidates by team roster.
- **Phonetic matching:** Add Soundex or Metaphone for names with common misspellings (e.g., "Chawla" vs "Chahal").
- **Partial match confidence:** Return confidence scores and show "Did you mean?" for low-confidence matches.

### P5: Query History & Favorites

**Objective:** Allow users to revisit previous queries, save favorites, and share queries via URL.

| Attribute | Value |
|-----------|-------|
| Priority | **P2** |
| Effort | **S** (Small) |
| Dependencies | localStorage |

**Proposed Design:**
- Store last 50 queries in `localStorage` with timestamp, SQL, NL text, and result count.
- "Favorites" star button on each query result.
- History panel in schema sidebar (new tab).
- URL hash encoding: `#q=base64(sql)` for shareable query links.
- Clear history button for privacy.

### P6: Two-Player Comparison (Non-Matchup)

**Objective:** Support "Compare Kohli and Rohit" as a side-by-side batting comparison (not batter-vs-bowler matchup).

| Attribute | Value |
|-----------|-------|
| Priority | **P2** |
| Effort | **S** (Small) |
| Dependencies | Extends existing comparison rendering |

**Proposed Design:**
- Detect two-player same-role queries: both batters or both bowlers.
- Generate UNION query: one row per player from career/phase views.
- Render side-by-side comparison cards (reuse win/loss comparison template).
- Support dimension stacking: "Compare Kohli and Rohit in death overs".

### P7: Load Missing `dim_tournament_weights` Table

**Objective:** Fix the gap where `dim_tournament_weights.parquet` exists but is not loaded.

| Attribute | Value |
|-----------|-------|
| Priority | **P1** |
| Effort | **XS** (Extra Small) |
| Dependencies | None |

**Proposed Design:**
- Add `'dim_tournament_weights'` to the `TABLE_FILES` array in `research-desk.html`.
- Verify that dependent views (`analytics_weighted_composite_batting`, `analytics_weighted_composite_bowling`) load successfully.

---

## 4. Recommended Priority Order

| Rank | Ticket | Title | Effort | Impact |
|------|--------|-------|--------|--------|
| 1 | P7 | Load missing `dim_tournament_weights` table | XS | Fixes broken views |
| 2 | P4 | Better player name resolution (dynamic aliases) | S | Reduces NL search failure rate |
| 3 | P5 | Query history & favorites | S | User experience improvement |
| 4 | P6 | Two-player comparison | S | Closes common query gap |
| 5 | P2 | Enhanced aggregation patterns | M | Enables new query classes |
| 6 | P3 | Cross-table join support | M | Enables complex research queries |
| 7 | P1 | Claude API integration | L | Transforms NL search from template-match to autonomous |

**Sprint 5 Recommended Scope (assuming 2-week sprint):**
- Commit to: P7 + P4 + P5 + P6 (all Small/XS, high-impact)
- Stretch: P2 (Medium, enables aggregation patterns)
- Backlog for Sprint 6: P3 + P1 (larger scope, higher risk)

---

## 5. Summary

The Film Room is **fully operational** with all core components passing audit. The NL Search system is remarkably capable for a client-side, rule-based implementation -- handling 12 distinct intent types, 150+ player aliases, 10 team aliases with historical names, and dynamic SQL generation via the QueryBuilder. The 5-stage pipeline architecture is well-structured and extensible.

The primary limitation is the absence of autonomous reasoning. The system cannot handle queries outside its programmed patterns. Adding Claude API integration (P1) would be transformative but carries implementation complexity. The near-term wins are in P7 (data fix), P4 (dynamic aliases), P5 (query history), and P6 (two-player comparison) -- all achievable within Sprint 5.

**Overall Film Room Grade: A-**
- Infrastructure: A+
- NL Search Coverage: B+
- NL Search Autonomy: D (by design -- rule-based)
- Data Completeness: A- (one missing table in loader)
- User Experience: A

---

*Filed by Jose Mourinho, Quant Researcher*
*Cricket Playbook v4.0.0 | Sprint 4.0 Close-Out*
