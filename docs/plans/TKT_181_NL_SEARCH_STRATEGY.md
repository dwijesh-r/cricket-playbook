# TKT-181: Intelligent Natural Language Search Strategy

**Version:** 1.0
**Date:** 2026-02-11
**Authors:** Andy Flower (Cricket Domain Expert) + Jose Mourinho (Quant Researcher)
**Status:** PLAN (Research Only)
**Ticket:** TKT-181

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Andy Flower: Cricket Intelligence Layer](#2-andy-flower-cricket-intelligence-layer)
   - 2.1 Query Intent Categories
   - 2.2 Entity Recognition Requirements
   - 2.3 Complex Query Examples (30+)
3. [Jose Mourinho: Technical Architecture](#3-jose-mourinho-technical-architecture)
   - 3.1 Current Limitations Analysis
   - 3.2 Dynamic Query Builder Architecture
   - 3.3 Schema Graph (Join Relationships)
   - 3.4 Win/Loss Context Resolution
   - 3.5 Composable Filter System
   - 3.6 Fallback Strategy
4. [Joint Section: Implementation Plan](#4-joint-section-implementation-plan)
   - 4.1 Implementation Phases
   - 4.2 Example Query-to-SQL Mappings (10 Complex Cases)
   - 4.3 Performance Considerations (WASM DuckDB)
5. [Risk Register](#5-risk-register)
6. [Success Metrics](#6-success-metrics)

---

## 1. Executive Summary

The current `naturalLanguageToSQL()` function in `research-desk.html` is a rigid, pattern-matching engine with 11 hardcoded regex patterns. It maps queries to **pre-built views** using string matching and cannot compose multi-dimensional queries. The Founder's example -- "How does Suryakumar Yadav perform in the middle overs in wins vs losses" -- requires dynamically joining `fact_ball` with `dim_match`, filtering by `match_phase`, resolving win/loss from `dim_match.winner_id` against `batting_team_id`, and aggregating batting metrics. This is fundamentally impossible with the current architecture.

This document lays out a comprehensive strategy to transform NL search from a **pattern-to-view lookup** into a **dynamic query planner** that understands cricket semantics, the schema graph, and can compose arbitrary filter combinations.

---

## 2. Andy Flower: Cricket Intelligence Layer

### 2.1 Query Intent Categories

Cricket analysts ask questions that fall into **12 distinct intent categories**. The NL engine must detect each:

| # | Intent Category | Description | Example |
|---|----------------|-------------|---------|
| 1 | **Player Career Lookup** | Overall stats for a named player | "Kohli stats" |
| 2 | **Phase Analysis** | Performance split by powerplay / middle / death | "Bumrah in death overs" |
| 3 | **Win/Loss Context** | Performance bifurcated by match outcome | "SKY in wins vs losses" |
| 4 | **Head-to-Head Matchup** | Batter vs specific bowler | "Kohli vs Rashid Khan" |
| 5 | **Bowler Type Matchup** | Batter against spin/pace classification | "Pant against spin" |
| 6 | **Team Split** | Performance against specific opposition | "Warner vs CSK" |
| 7 | **Venue Split** | Performance at a specific ground | "Gill at Wankhede" |
| 8 | **Season/Trend** | Year-by-year progression | "Hardik Pandya season wise" |
| 9 | **Leaderboard/Ranking** | Top N by a metric | "Top 10 death bowlers by economy" |
| 10 | **Pressure/Clutch** | Performance under RRR-based pressure bands | "Best finishers under extreme pressure" |
| 11 | **Composite Multi-Filter** | Combination of 2+ filters | "Bumrah economy in powerplay at Wankhede in 2024" |
| 12 | **Team Aggregate** | Team-level phase/venue/matchup analysis | "CSK bowling in death overs" |

**Critical gap in current system:** Categories 3, 11, and most of 12 are entirely unsupported. Category 9 is only partially supported (batting leaderboards exist, but composite leaderboards like "best death bowlers in wins" do not).

### 2.2 Entity Recognition Requirements

The NL engine must detect and resolve these **8 cricket entity types**:

#### 2.2.1 Player Names (Critical)

- Full names: "Suryakumar Yadav", "Jasprit Bumrah"
- Nicknames / abbreviations: "SKY", "Kohli", "Pant", "ABD", "Bravo"
- Fuzzy matching: "surya kumar" -> "Suryakumar Yadav"
- **Implementation:** Maintain a lookup table derived from `dim_player.current_name` + `ipl_2026_squads.player_name`. Add a `player_aliases` map for common nicknames (SKY, MSD, ABD, Gayle, etc.).

#### 2.2.2 Team Names/Aliases (Existing, needs expansion)

Current `TEAM_ALIASES` map covers 10 IPL teams with abbreviations. Needs:
- Historical aliases: "Delhi Daredevils" -> "Delhi Capitals", "Deccan Chargers" -> "Sunrisers Hyderabad"
- Full canonical resolution via `dim_franchise_alias` table
- Handling of "vs" context: "MI vs CSK" should resolve to head-to-head, not player lookup

#### 2.2.3 Match Phases

| Keyword(s) | Phase Value |
|-------------|------------|
| powerplay, pp, power play, first 6, opening | `powerplay` |
| middle, middle overs, overs 7-15, consolidation | `middle` |
| death, death overs, slog, last 5, overs 16-20 | `death` |

#### 2.2.4 Bowling Types

| Keyword(s) | Classification |
|-------------|---------------|
| spin, spinner, spinners | All spin types |
| pace, fast, seam, quick | Right-arm pace, Left-arm pace |
| off-spin, off-spinner, offie | Right-arm off-spin |
| leg-spin, leggie, wrist spin | Right-arm leg-spin, Left-arm wrist spin |
| left-arm spin, left-arm orthodox, SLA | Left-arm orthodox |
| left-arm pace, left-arm quick | Left-arm pace |

Must map to values in `dim_bowler_classification.bowling_style` and `ipl_2026_squads.bowling_type`.

#### 2.2.5 Venue Names

- City names: "Mumbai" -> Wankhede Stadium; "Chennai" -> MA Chidambaram Stadium
- Ground names: "Wankhede", "Chinnaswamy", "Eden Gardens"
- Resolve via `dim_venue.venue_name` and `dim_venue.city`
- **Fuzzy match** needed: "chinnaswami" -> "M.Chinnaswamy Stadium"

#### 2.2.6 Seasons

- Year numbers: "2024", "2023"
- Relative: "last season", "this year", "recent"
- Ranges: "2023-2025", "since 2023"
- Resolve to `dim_match.season` values

#### 2.2.7 Metrics (Sort/Display targets)

| User Term(s) | SQL Column |
|-------------|-----------|
| strike rate, SR | `strike_rate` |
| average, avg | `batting_average` / `bowling_average` |
| economy, econ | `economy_rate` / `economy` |
| boundary %, boundaries | `boundary_pct` |
| dot ball % | `dot_ball_pct` |
| wickets | `wickets` |
| runs | `runs` |
| sixes, 6s | `sixes` |
| fours, 4s | `fours` |

#### 2.2.8 Context Modifiers

| Modifier | Meaning | SQL Impact |
|----------|---------|-----------|
| "in wins" / "when winning" | Match outcome = won | `JOIN dim_match dm ... WHERE dm.winner_id = fb.batting_team_id` |
| "in losses" / "when losing" | Match outcome = lost | `JOIN dim_match dm ... WHERE dm.winner_id != fb.batting_team_id AND dm.winner_id IS NOT NULL` |
| "wins vs losses" | Split comparison | Two aggregations with CASE WHEN or UNION |
| "batting first" / "setting" | Innings = 1 | `WHERE fb.innings = 1` |
| "chasing" / "batting second" | Innings = 2 | `WHERE fb.innings = 2` |
| "defending" | Bowling in innings 2 | `WHERE fb.innings = 2` (for bowler queries) |
| "above 180" / "high-scoring" | First innings total context | `JOIN` to innings total CTE |
| "playoffs" / "knockouts" | Tournament stage | `WHERE dm.stage IN ('playoff', 'final', 'qualifier', 'eliminator')` |

### 2.3 Complex Query Examples (30+)

Organized from simple to expert-level. Each includes the expected intent decomposition.

#### Tier 1: Simple (Single entity, single view)

| # | Query | Intent | View/Table |
|---|-------|--------|-----------|
| 1 | "Kohli stats" | Player career lookup | `analytics_ipl_batting_career` |
| 2 | "Bumrah bowling" | Player bowling career | `analytics_ipl_bowling_career` |
| 3 | "CSK squad" | Team roster | `ipl_2026_squads` |
| 4 | "Top 10 run scorers" | Batting leaderboard | `analytics_ipl_batting_career` |
| 5 | "Most expensive players" | Contract lookup | `ipl_2026_contracts` |
| 6 | "RCB overseas players" | Squad filter | `ipl_2026_squads` |

#### Tier 2: Medium (Two entities or one filter dimension)

| # | Query | Intent | Tables Needed |
|---|-------|--------|--------------|
| 7 | "Kohli vs Rashid Khan" | H2H matchup | `analytics_ipl_batter_vs_bowler` |
| 8 | "Pant against spin" | Bowler type matchup | `analytics_ipl_batter_vs_bowler_type` |
| 9 | "CSK bowling in death overs" | Team + phase | `analytics_ipl_squad_bowling_phase` |
| 10 | "Gill at Wankhede" | Player + venue | `analytics_ipl_batter_venue` |
| 11 | "Bumrah in powerplay" | Player + phase | `analytics_ipl_bowler_phase` |
| 12 | "Warner vs MI" | Player + team | `analytics_ipl_batter_vs_team` |
| 13 | "Best death bowlers" | Leaderboard + phase | `analytics_ipl_bowler_phase` |
| 14 | "Kohli season wise" | Player + trend | `fact_ball` + `dim_match` (dynamic) |
| 15 | "Finishers under pressure" | Pressure band query | `analytics_ipl_batter_pressure_bands_since2023` |

#### Tier 3: Complex (Multi-filter, requires joins)

| # | Query | Intent | Resolution |
|---|-------|--------|-----------|
| 16 | "SKY middle overs in wins vs losses" | Player + phase + win/loss split | `fact_ball` JOIN `dim_match` (winner_id), filter `match_phase='middle'` |
| 17 | "Kohli at Chinnaswamy in death overs" | Player + venue + phase | `analytics_ipl_batter_venue_phase` |
| 18 | "Bumrah economy vs MI in powerplay" | Player + team + phase + metric | `fact_ball` JOIN `dim_match` + `dim_team`, filter phase & team |
| 19 | "CSK batting in wins since 2023" | Team + win/loss + season range | `fact_ball` + `dim_match` + `ipl_2026_squads` |
| 20 | "Top 5 spinners in middle overs" | Leaderboard + role + phase | `analytics_ipl_bowler_phase` JOIN `dim_bowler_classification` |
| 21 | "Hardik Pandya batting vs pace in death" | Player + bowler type + phase | `analytics_ipl_batter_vs_bowler_type_phase` |
| 22 | "KKR bowling economy at Eden Gardens" | Team + venue + metric | `fact_ball` + `dim_venue` + team filter |
| 23 | "Best powerplay batters in 2024" | Leaderboard + phase + season | `fact_ball` + `dim_match`, dynamic aggregation |
| 24 | "Rashid Khan dot ball % in death when defending" | Player + phase + innings context | `fact_ball` filter `innings=2`, `match_phase='death'` |
| 25 | "Players with highest SR under extreme pressure" | Leaderboard + pressure band | `analytics_ipl_batter_pressure_bands_since2023` |

#### Tier 4: Expert (3+ filters, complex joins, computed context)

| # | Query | Intent | Resolution |
|---|-------|--------|-----------|
| 26 | "Bumrah economy in powerplay vs death when defending totals above 180" | Player + dual phase + innings + total context | `fact_ball` + first innings total CTE + phase split + innings 2 |
| 27 | "How does Kohli's SR change in wins vs losses in death overs at Chinnaswamy" | Player + win/loss + phase + venue | 4-way join: `fact_ball` + `dim_match` + `dim_venue`, phase filter, win/loss split |
| 28 | "Compare CSK vs MI bowling economy in powerplay since 2023" | Team comparison + phase + season | Two team aggregations from `fact_ball` |
| 29 | "Left-arm pacers' economy in death overs in playoff matches" | Role + phase + stage | `fact_ball` + `dim_bowler_classification` + `dim_match.stage` |
| 30 | "Batters who average above 40 in middle overs but below 25 in death" | Conditional leaderboard across phases | Self-join on `analytics_ipl_batter_phase` for middle vs death |
| 31 | "SKY vs spin in middle overs at Wankhede in wins" | 5 filters: player + bowler type + phase + venue + outcome | Full `fact_ball` join chain |
| 32 | "Which bowlers have the best economy under high/extreme pressure in 2024 playoffs" | Pressure + season + stage | `fact_ball` + pressure CTE + `dim_match` stage filter |
| 33 | "Batting average of top-order batters (1-3) in chasing innings" | Position + innings context | `fact_ball` + `fact_player_match_performance.batting_position` |
| 34 | "Uncapped Indian fast bowlers under 25 in IPL 2026" | Squad metadata composite | `ipl_2026_squads` multi-filter |
| 35 | "Kohli vs Bumrah in powerplay since 2023" | H2H + phase + season | `analytics_ipl_batter_vs_bowler_phase_since2023` |

---

## 3. Jose Mourinho: Technical Architecture

### 3.1 Current Limitations Analysis

The current `naturalLanguageToSQL()` implementation (lines 2748-3091 of `research-desk.html`) has these structural problems:

| Limitation | Impact | Example Failure |
|-----------|--------|----------------|
| **Fixed pattern order** | First matching pattern wins, later patterns never reached | "CSK batting in death" matches Pattern 6 (team batting), misses the phase dimension |
| **Single-view targeting** | Each pattern maps to exactly one pre-built view | Cannot combine venue + phase + win/loss because no single view has all three |
| **No join composition** | Cannot dynamically join `fact_ball` with context tables | "SKY in wins" is impossible -- no view has win/loss context for individual players |
| **No win/loss awareness** | `dim_match.winner_id` is never referenced | Entire class of outcome-based analysis is blocked |
| **No innings context** | Cannot filter by batting first/second, defending/chasing | "Bumrah when defending" cannot be expressed |
| **No stage filtering** | Cannot filter by playoffs/league stage | "Kohli in playoffs" unsupported |
| **No first-innings total context** | Cannot condition on the target being defended/chased | "Economy when defending 180+" impossible |
| **Brittle entity extraction** | Player name extracted by stripping known keywords, residual text assumed to be a name | "best death bowlers" partially matches as player name "best" |
| **No disambiguation** | Cannot distinguish "Pant stats" (batting) from "Pant bowling stats" reliably when query is ambiguous | Falls through to batting by default |
| **No multi-result queries** | Cannot do side-by-side comparison (wins vs losses) | Returns single result set only |
| **No alias/nickname support** | "SKY", "MSD", "ABD" not recognized | Returns null |
| **No score-context awareness** | Pressure bands exist as pre-built views but cannot be combined with other filters | "Pressure bowling at Wankhede" fails |

### 3.2 Dynamic Query Builder Architecture

The new system replaces the monolithic pattern-matcher with a **5-stage pipeline**:

```
User Query
    |
    v
[Stage 1: ENTITY EXTRACTION]
    Detect all entities: players, teams, phases, venues, seasons,
    bowler types, metrics, modifiers (win/loss, innings, stage)
    |
    v
[Stage 2: INTENT CLASSIFICATION]
    Determine query type: lookup, leaderboard, matchup, comparison, composite
    Determine primary subject: batting or bowling
    |
    v
[Stage 3: TABLE SELECTION + JOIN PLANNING]
    Given extracted entities, select optimal table path:
    - If existing view covers all dimensions -> use view directly
    - If not -> build from fact_ball with required joins
    Schema graph determines join path automatically
    |
    v
[Stage 4: SQL GENERATION]
    Build SQL with:
    - SELECT (metrics based on batting/bowling context)
    - FROM (selected table or fact_ball)
    - JOINs (from join planner)
    - WHERE (all extracted filters)
    - GROUP BY (entity groupings)
    - ORDER BY (detected metric or default)
    - LIMIT (extracted or default 20)
    |
    v
[Stage 5: VALIDATION + FALLBACK]
    Validate generated SQL is syntactically correct
    If confidence < threshold -> show suggestions instead
```

#### Stage 1: Entity Extraction (Detail)

```javascript
function extractEntities(query) {
    return {
        players: [],        // { name, id, confidence }
        teams: [],          // { name, canonical, confidence }
        phases: [],         // 'powerplay' | 'middle' | 'death'
        venues: [],         // { name, venueId }
        seasons: [],        // ['2024'] or { from: '2023', to: '2025' }
        bowlerTypes: [],    // 'spin' | 'pace' | 'off-spin' | ...
        metrics: [],        // { name: 'economy', direction: 'ASC' }
        modifiers: {
            winLoss: null,      // 'wins' | 'losses' | 'split'
            innings: null,      // 1 | 2
            stage: null,        // 'league' | 'playoff'
            limit: 20,
            totalContext: null,  // { operator: '>=', value: 180 }
        },
        role: null,         // 'batting' | 'bowling' | 'both'
    };
}
```

Entity extraction should use a **priority-ordered extraction pipeline**:
1. **Player names first** -- longest match against player dictionary (fuzzy, Levenshtein distance <= 2)
2. **Team names** -- match against TEAM_ALIASES (already exists)
3. **Phase keywords** -- match against PHASE_MAP (already exists)
4. **Venue names** -- match against venue dictionary (from `dim_venue`)
5. **Season numbers** -- regex for 4-digit years (2020-2026)
6. **Bowler type keywords** -- match against classification map
7. **Metric keywords** -- detect sort/display preferences
8. **Context modifiers** -- win/loss, innings, stage, total threshold

Each extractor **removes matched tokens** from the remaining query string so later extractors do not re-match the same text.

#### Stage 2: Intent Classification

```javascript
function classifyIntent(entities) {
    if (entities.players.length === 2 || hasVsToken)
        return 'MATCHUP';
    if (entities.players.length === 1 && noLeaderboardToken)
        return 'PLAYER_LOOKUP';
    if (hasLeaderboardToken)       // "top", "best", "worst", "most"
        return 'LEADERBOARD';
    if (entities.teams.length === 1 && !entities.players.length)
        return 'TEAM_ANALYSIS';
    if (entities.teams.length === 2)
        return 'TEAM_COMPARISON';
    if (hasComparisonToken)        // "vs", "compare", "wins vs losses"
        return 'COMPARISON';
    return 'EXPLORATORY';
}
```

#### Stage 3: Table Selection + Join Planning

This is the core innovation. The **Query Planner** decides:

1. **Can an existing view satisfy all required dimensions?**
   - Example: Player + phase + venue -> `analytics_ipl_batter_venue_phase` (exists!)
   - Example: Player + phase + win/loss -> NO existing view covers this

2. **If no view matches, build from `fact_ball`:**
   - Start from `fact_ball` as the anchor
   - Add joins based on required dimensions (see Schema Graph in 3.3)
   - Apply filters from entities

The planner maintains a **dimension coverage matrix**:

```javascript
const VIEW_COVERAGE = {
    'analytics_ipl_batting_career':        { dimensions: ['player'], role: 'batting' },
    'analytics_ipl_batter_phase':          { dimensions: ['player', 'phase'], role: 'batting' },
    'analytics_ipl_batter_venue':          { dimensions: ['player', 'venue'], role: 'batting' },
    'analytics_ipl_batter_venue_phase':    { dimensions: ['player', 'venue', 'phase'], role: 'batting' },
    'analytics_ipl_batter_vs_team':        { dimensions: ['player', 'team'], role: 'batting' },
    'analytics_ipl_batter_vs_team_phase':  { dimensions: ['player', 'team', 'phase'], role: 'batting' },
    'analytics_ipl_batter_vs_bowler':      { dimensions: ['player', 'player'], role: 'matchup' },
    'analytics_ipl_batter_vs_bowler_phase':{ dimensions: ['player', 'player', 'phase'], role: 'matchup' },
    'analytics_ipl_batter_vs_bowler_type': { dimensions: ['player', 'bowlerType'], role: 'batting' },
    'analytics_ipl_batter_vs_bowler_type_phase': { dimensions: ['player', 'bowlerType', 'phase'], role: 'batting' },
    'analytics_ipl_bowler_phase':          { dimensions: ['player', 'phase'], role: 'bowling' },
    'analytics_ipl_bowler_venue':          { dimensions: ['player', 'venue'], role: 'bowling' },
    'analytics_ipl_bowler_venue_phase':    { dimensions: ['player', 'venue', 'phase'], role: 'bowling' },
    'analytics_ipl_bowler_vs_team':        { dimensions: ['player', 'team'], role: 'bowling' },
    'analytics_ipl_bowler_vs_team_phase':  { dimensions: ['player', 'team', 'phase'], role: 'bowling' },
    'analytics_ipl_batter_pressure_bands_since2023': { dimensions: ['player', 'pressure'], role: 'batting' },
    'analytics_ipl_bowler_pressure_bands_since2023': { dimensions: ['player', 'pressure'], role: 'bowling' },
    // ... all 152 views catalogued
};
```

**View selection algorithm:**
1. Compute the **required dimension set** from extracted entities
2. Find views whose dimensions are a **superset** of the required set
3. Pick the **most specific** view (fewest extra dimensions = fastest query)
4. If no view matches AND a context modifier (win/loss, innings, stage, total) is present -> fall through to `fact_ball`-based dynamic SQL

### 3.3 Schema Graph (Join Relationships)

The complete join graph for dynamic query building:

```
                    dim_tournament
                         |
                    tournament_id
                         |
                    dim_match ─── dim_venue
                    /    |    \      (venue_id)
              match_id   |   winner_id
                /        |        \
          fact_ball   winner_id   dim_team
          /  |  \                  (team_id)
         /   |   \
        /    |    \
  batter_id  |  bowler_id
      |      |      |
  dim_player |  dim_player
             |
      batting_team_id / bowling_team_id
             |
         dim_team
             |
      dim_franchise_alias
         (team_name -> canonical_name)

  Additional joins:
  ─ dim_bowler_classification (player_id) -- bowling style
  ─ ipl_2026_squads (player_id) -- squad membership, role, nationality
  ─ ipl_2026_contracts (team_name + player_name) -- price, acquisition
  ─ fact_player_match_performance (player_id + match_id) -- batting position
  ─ player_clusters_batters / player_clusters_bowlers (player_id) -- ML clusters
```

**Key join paths for common queries:**

| Dimension Needed | Join Path from `fact_ball` |
|-----------------|--------------------------|
| Player name | `JOIN dim_player dp ON fb.batter_id = dp.player_id` (or `bowler_id`) |
| Team name | `JOIN dim_team dt ON fb.batting_team_id = dt.team_id` (or `bowling_team_id`) |
| Venue | `JOIN dim_match dm ON fb.match_id = dm.match_id` then `JOIN dim_venue dv ON dm.venue_id = dv.venue_id` |
| Season | `JOIN dim_match dm ON fb.match_id = dm.match_id` -> `dm.season` |
| IPL-only filter | `JOIN dim_match dm ON fb.match_id = dm.match_id JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id WHERE dt.tournament_name = 'Indian Premier League'` |
| Win/Loss | `JOIN dim_match dm ON fb.match_id = dm.match_id` -> compare `dm.winner_id` against `fb.batting_team_id` |
| Bowler type | `LEFT JOIN ipl_2026_squads sq ON fb.bowler_id = sq.player_id LEFT JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id` |
| Match phase | Already on `fact_ball.match_phase` |
| Tournament stage | `JOIN dim_match dm ON fb.match_id = dm.match_id` -> `dm.stage` |
| Franchise alias | `LEFT JOIN dim_franchise_alias fa ON dt.team_name = fa.team_name` |
| Batting position | `JOIN fact_player_match_performance fpmp ON fb.batter_id = fpmp.player_id AND fb.match_id = fpmp.match_id` |

### 3.4 Win/Loss Context Resolution

This is the single most requested missing feature. Implementation:

**For batting queries ("SKY in wins"):**
```sql
-- Win context: batting_team_id = winner_id
SELECT
    dp.current_name AS player_name,
    CASE WHEN dm.winner_id = fb.batting_team_id THEN 'WON' ELSE 'LOST' END AS match_result,
    -- standard batting aggregations ...
FROM fact_ball fb
JOIN dim_player dp ON fb.batter_id = dp.player_id
JOIN dim_match dm ON fb.match_id = dm.match_id
JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
WHERE dt.tournament_name = 'Indian Premier League'
  AND dp.current_name ILIKE '%Suryakumar Yadav%'
  AND dm.winner_id IS NOT NULL          -- exclude no-results / ties
GROUP BY dp.current_name,
         CASE WHEN dm.winner_id = fb.batting_team_id THEN 'WON' ELSE 'LOST' END
```

**For bowling queries ("Bumrah in wins"):**
```sql
-- Bowler's team won: bowling_team_id = winner_id
CASE WHEN dm.winner_id = fb.bowling_team_id THEN 'WON' ELSE 'LOST' END AS match_result
```

**For "wins vs losses" split comparison:**
Include `match_result` in the GROUP BY so the result set contains both rows side by side.

**Innings context (batting first / chasing):**
```sql
-- Batting first
WHERE fb.innings = 1

-- Chasing
WHERE fb.innings = 2
```

**Defending a total above 180:**
```sql
WITH innings1_total AS (
    SELECT match_id, SUM(total_runs) AS first_innings_total
    FROM fact_ball WHERE innings = 1
    GROUP BY match_id
)
-- Then join and filter:
WHERE i1.first_innings_total >= 180 AND fb.innings = 2
```

### 3.5 Composable Filter System

The dynamic SQL generator builds queries by stacking **composable filter modules**. Each filter is independent and can be combined with any other:

```javascript
class QueryBuilder {
    constructor() {
        this.selects = [];
        this.from = 'fact_ball fb';
        this.joins = new Set();     // de-duplicated
        this.wheres = [];
        this.groupBys = [];
        this.orderBy = null;
        this.limit = 20;
    }

    // Each filter method adds its required joins + where clauses
    addIPLFilter()         { /* joins dim_match + dim_tournament, adds WHERE */ }
    addPlayerFilter(name, role)  { /* joins dim_player, adds ILIKE WHERE */ }
    addTeamFilter(team)    { /* joins dim_team, adds WHERE */ }
    addPhaseFilter(phase)  { /* adds WHERE fb.match_phase = ... */ }
    addVenueFilter(venue)  { /* joins dim_match + dim_venue, adds WHERE */ }
    addSeasonFilter(season){ /* joins dim_match, adds WHERE dm.season = ... */ }
    addWinLossFilter(mode) { /* joins dim_match, adds winner_id comparison */ }
    addInningsFilter(inn)  { /* adds WHERE fb.innings = ... */ }
    addStageFilter(stage)  { /* joins dim_match, adds WHERE dm.stage */ }
    addBowlerTypeFilter(type) { /* joins bowler classification tables */ }
    addTotalContextFilter(op, val) { /* adds innings1_total CTE */ }
    addPressureFilter()    { /* adds pressure band CTE (RRR calculation) */ }

    // Aggregation templates
    setBattingAggregation() { /* standard batting metrics */ }
    setBowlingAggregation() { /* standard bowling metrics */ }

    // Build final SQL
    build() { /* compose all parts into valid SQL string */ }
}
```

**Filter stacking example** for "Bumrah economy in powerplay when defending totals above 180 since 2023":

```
Filters applied:
1. addIPLFilter()              -> JOIN dim_match + dim_tournament
2. addPlayerFilter('bumrah', 'bowling') -> JOIN dim_player on bowler_id
3. addPhaseFilter('powerplay') -> WHERE fb.match_phase = 'powerplay'
4. addInningsFilter(2)         -> WHERE fb.innings = 2 (bowling in 2nd innings = defending)
5. addTotalContextFilter('>=', 180)  -> CTE innings1_total + WHERE filter
6. addSeasonFilter('>=2023')   -> WHERE dm.match_date >= '2023-01-01'
7. setBowlingAggregation()     -> SELECT economy, wickets, dot_ball_pct, ...
```

### 3.6 Fallback Strategy

When the engine cannot confidently determine intent (confidence < 0.6):

**Tier 1: Suggest similar queries**
```
"I'm not sure I understand that query. Did you mean one of these?"
- "Suryakumar Yadav batting stats"
- "Suryakumar Yadav in middle overs"
- "Suryakumar Yadav vs [team name]"
```

**Tier 2: Show schema hints**
```
"I found a player match but couldn't determine the analysis type.
Available analysis for Suryakumar Yadav:
- Career stats (batting / bowling)
- Phase breakdown (powerplay / middle / death)
- vs Team (CSK, MI, RCB, ...)
- vs Bowler Type (pace / spin)
- Venue splits
- Pressure performance
- Season trend"
```

**Tier 3: Partial execution + explanation**
If the engine extracts some entities but not all, execute what it can and explain what was ignored:
```
"Showing Bumrah's powerplay stats. I couldn't determine the win/loss context
from your query. Try: 'Bumrah powerplay in wins vs losses'"
```

**Tier 4: Pass through to SQL editor**
If the query looks like raw SQL (contains SELECT, FROM, WHERE), pass it directly to the SQL editor without NL processing.

---

## 4. Joint Section: Implementation Plan

### 4.1 Implementation Phases

#### Phase 1: Foundation (Sprint 5, ~3 tickets)

**Goal:** Replace pattern-matching with entity extraction + view routing.

1. **TKT-182: Entity Extraction Engine**
   - Build `extractEntities()` function with player dictionary, team aliases, phase map, venue map
   - Player name dictionary loaded from `table_metadata.json` or a lightweight player list JSON
   - Fuzzy matching using Levenshtein distance (simple JS implementation, no dependencies)
   - Add player nickname/alias map (30-50 common nicknames)

2. **TKT-183: Intent Classifier**
   - Build `classifyIntent()` function
   - Map intents to query strategies (view lookup vs dynamic SQL)

3. **TKT-184: View Coverage Matrix**
   - Catalogue all 152 views with their dimension coverage
   - Build `findBestView()` function that matches required dimensions to available views
   - This alone will fix many queries that currently fail (e.g., venue + phase)

#### Phase 2: Dynamic SQL (Sprint 5-6, ~4 tickets)

**Goal:** Handle queries that no existing view can satisfy.

4. **TKT-185: QueryBuilder Class**
   - Implement composable SQL builder with filter stacking
   - Standard batting/bowling aggregation templates
   - IPL-only CTE as a reusable base

5. **TKT-186: Win/Loss Context Module**
   - Add `winner_id` join logic for batting and bowling
   - Support "in wins", "in losses", "wins vs losses" (split)
   - This directly addresses the Founder's example query

6. **TKT-187: Innings & Total Context Module**
   - Support "batting first", "chasing", "defending"
   - Support "totals above/below X" with first-innings total CTE
   - Support "playoff" / "league stage" filtering

7. **TKT-188: Season & Temporal Filters**
   - Support specific years, ranges ("since 2023"), "last N seasons"
   - Choose `_since2023` or `_alltime` view variants automatically

#### Phase 3: Intelligence (Sprint 6, ~3 tickets)

**Goal:** Make the system genuinely smart about cricket queries.

8. **TKT-189: Comparison Query Support**
   - Handle "Player A vs Player B stats" (side-by-side)
   - Handle "Team A vs Team B" comparison
   - Handle "wins vs losses" split output formatting

9. **TKT-190: Auto-Suggest & Disambiguation**
   - When query is ambiguous, show ranked suggestions
   - When multiple players match (e.g., "Pandya"), show disambiguation
   - Schema-aware hints ("You asked about bowling, available metrics: economy, wickets, ...")

10. **TKT-191: Composite Leaderboard Queries**
    - Support "best X by Y in Z" patterns with arbitrary filter stacking
    - Example: "Top 5 left-arm pacers by economy in death overs in 2024"

#### Phase 4: Polish (Sprint 7, ~2 tickets)

11. **TKT-192: Query Explanation Panel**
    - Show users what the engine understood: "Player: Bumrah | Phase: death | Context: wins"
    - Show the generated SQL for transparency
    - Allow users to edit/refine

12. **TKT-193: Query History & Autocomplete**
    - Cache successful queries for autocomplete
    - Show popular/trending queries
    - Learn from usage patterns

### 4.2 Example Query-to-SQL Mappings (10 Complex Cases)

#### Case 1: "SKY middle overs in wins vs losses"

**Entities:** player=Suryakumar Yadav, phase=middle, modifier=wins_vs_losses
**Strategy:** Dynamic SQL (no view has win/loss context)

```sql
WITH ipl AS (
  SELECT dm.match_id, dm.winner_id
  FROM dim_match dm
  JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
  WHERE dt.tournament_name = 'Indian Premier League'
    AND dm.match_date >= '2023-01-01'
    AND dm.winner_id IS NOT NULL
)
SELECT
  dp.current_name AS player_name,
  CASE WHEN ipl.winner_id = fb.batting_team_id THEN 'WON' ELSE 'LOST' END AS result,
  COUNT(DISTINCT fb.match_id) AS innings,
  SUM(fb.batter_runs) AS runs,
  SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS balls,
  ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS strike_rate,
  ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) AS average,
  ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
        NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS boundary_pct
FROM fact_ball fb
JOIN dim_player dp ON fb.batter_id = dp.player_id
JOIN ipl ON fb.match_id = ipl.match_id
WHERE dp.current_name ILIKE '%Suryakumar Yadav%'
  AND fb.match_phase = 'middle'
GROUP BY dp.current_name,
  CASE WHEN ipl.winner_id = fb.batting_team_id THEN 'WON' ELSE 'LOST' END
ORDER BY result;
```

#### Case 2: "Bumrah economy in powerplay vs death when defending totals above 180"

**Entities:** player=Bumrah, phases=[powerplay, death], innings=2, total_threshold>=180
**Strategy:** Dynamic SQL with first-innings total CTE

```sql
WITH ipl AS (
  SELECT dm.match_id
  FROM dim_match dm
  JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
  WHERE dt.tournament_name = 'Indian Premier League'
    AND dm.match_date >= '2023-01-01'
),
inn1_total AS (
  SELECT match_id, SUM(total_runs) AS first_inn_total
  FROM fact_ball
  WHERE innings = 1 AND match_id IN (SELECT match_id FROM ipl)
  GROUP BY match_id
  HAVING SUM(total_runs) >= 180
)
SELECT
  dp.current_name AS player_name,
  fb.match_phase,
  ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) AS overs,
  SUM(fb.total_runs) AS runs_conceded,
  ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS economy,
  SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out','retired hurt','retired out') THEN 1 ELSE 0 END) AS wickets,
  ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct
FROM fact_ball fb
JOIN dim_player dp ON fb.bowler_id = dp.player_id
JOIN inn1_total i1 ON fb.match_id = i1.match_id
WHERE dp.current_name ILIKE '%Bumrah%'
  AND fb.innings = 2
  AND fb.match_phase IN ('powerplay', 'death')
  AND fb.match_id IN (SELECT match_id FROM ipl)
GROUP BY dp.current_name, fb.match_phase
ORDER BY CASE fb.match_phase WHEN 'powerplay' THEN 1 WHEN 'death' THEN 2 END;
```

#### Case 3: "CSK bowling in death overs"

**Entities:** team=Chennai Super Kings, role=bowling, phase=death
**Strategy:** View lookup -> `analytics_ipl_squad_bowling_phase`

```sql
SELECT player_name, role, bowling_type, price_cr,
  matches, overs, wickets, economy_rate, dot_ball_pct, boundary_conceded_pct
FROM analytics_ipl_squad_bowling_phase
WHERE team_name ILIKE '%Chennai Super Kings%'
  AND match_phase = 'death'
ORDER BY economy_rate ASC;
```

#### Case 4: "Kohli at Chinnaswamy in death overs"

**Entities:** player=Kohli, venue=Chinnaswamy, phase=death
**Strategy:** View lookup -> `analytics_ipl_batter_venue_phase`

```sql
SELECT batter_name, venue, match_phase, innings, balls, runs,
  strike_rate, average, boundary_pct
FROM analytics_ipl_batter_venue_phase
WHERE batter_name ILIKE '%Kohli%'
  AND venue ILIKE '%Chinnaswamy%'
  AND match_phase = 'death';
```

#### Case 5: "Top 5 spinners in middle overs by economy"

**Entities:** bowlerType=spin, phase=middle, limit=5, metric=economy
**Strategy:** Dynamic SQL joining bowler phase with classification

```sql
SELECT
  bp.player_name,
  bc.bowling_style,
  bp.matches, bp.overs, bp.runs_conceded, bp.wickets,
  bp.economy_rate, bp.dot_ball_pct
FROM analytics_ipl_bowler_phase bp
JOIN dim_bowler_classification bc ON bp.player_id = bc.player_id
WHERE bp.match_phase = 'middle'
  AND bc.bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin')
  AND bp.balls_bowled >= 120
ORDER BY bp.economy_rate ASC
LIMIT 5;
```

#### Case 6: "Hardik Pandya batting vs pace in death overs"

**Entities:** player=Hardik Pandya, bowlerType=pace, phase=death
**Strategy:** View lookup -> `analytics_ipl_batter_vs_bowler_type_phase`

```sql
SELECT batter_name, bowler_type, match_phase, balls, runs,
  strike_rate, average, boundary_pct, dot_ball_pct
FROM analytics_ipl_batter_vs_bowler_type_phase
WHERE batter_name ILIKE '%Hardik Pandya%'
  AND bowler_type IN ('Fast', 'Medium', 'Right-arm pace', 'Left-arm pace')
  AND match_phase = 'death';
```

#### Case 7: "Left-arm pacers economy in death overs in playoff matches"

**Entities:** bowlerType=left-arm pace, phase=death, stage=playoff
**Strategy:** Dynamic SQL (no view has stage filter)

```sql
WITH ipl AS (
  SELECT dm.match_id
  FROM dim_match dm
  JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
  WHERE dt.tournament_name = 'Indian Premier League'
    AND dm.stage IN ('playoff', 'final', 'qualifier 1', 'qualifier 2', 'eliminator')
)
SELECT
  dp.current_name AS player_name,
  SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS balls,
  ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) AS overs,
  SUM(fb.total_runs) AS runs_conceded,
  ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS economy,
  SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out','retired hurt','retired out') THEN 1 ELSE 0 END) AS wickets
FROM fact_ball fb
JOIN dim_player dp ON fb.bowler_id = dp.player_id
JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
WHERE fb.match_id IN (SELECT match_id FROM ipl)
  AND fb.match_phase = 'death'
  AND bc.bowling_style = 'Left-arm pace'
  AND fb.is_legal_ball = TRUE
GROUP BY dp.current_name
HAVING SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) >= 30
ORDER BY economy ASC;
```

#### Case 8: "Compare CSK vs MI bowling economy in powerplay since 2023"

**Entities:** teams=[CSK, MI], role=bowling, phase=powerplay, season>=2023
**Strategy:** Dynamic SQL with team comparison

```sql
WITH ipl AS (
  SELECT dm.match_id
  FROM dim_match dm
  JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
  WHERE dt.tournament_name = 'Indian Premier League'
    AND dm.match_date >= '2023-01-01'
)
SELECT
  dt_bowl.team_name AS team,
  ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) AS overs,
  SUM(fb.total_runs) AS runs_conceded,
  ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS economy,
  SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out','retired hurt','retired out') THEN 1 ELSE 0 END) AS wickets,
  ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct
FROM fact_ball fb
JOIN dim_team dt_bowl ON fb.bowling_team_id = dt_bowl.team_id
LEFT JOIN dim_franchise_alias fa ON dt_bowl.team_name = fa.team_name
WHERE fb.match_id IN (SELECT match_id FROM ipl)
  AND fb.match_phase = 'powerplay'
  AND COALESCE(fa.canonical_name, dt_bowl.team_name) IN ('Chennai Super Kings', 'Mumbai Indians')
GROUP BY dt_bowl.team_name
ORDER BY economy ASC;
```

#### Case 9: "Batters who average above 40 in middle but below 25 in death"

**Entities:** role=batting, metric_condition=[middle avg > 40, death avg < 25]
**Strategy:** Self-join on phase view

```sql
SELECT
  mid.player_name,
  mid.innings AS mid_innings, mid.batting_average AS mid_avg, mid.strike_rate AS mid_sr,
  dth.innings AS death_innings, dth.batting_average AS death_avg, dth.strike_rate AS death_sr
FROM analytics_ipl_batter_phase mid
JOIN analytics_ipl_batter_phase dth
  ON mid.player_id = dth.player_id
WHERE mid.match_phase = 'middle'
  AND dth.match_phase = 'death'
  AND mid.batting_average > 40
  AND dth.batting_average < 25
  AND mid.balls_faced >= 200
  AND dth.balls_faced >= 100
ORDER BY mid.batting_average DESC;
```

#### Case 10: "Kohli vs Bumrah in powerplay since 2023"

**Entities:** player1=Kohli, player2=Bumrah, phase=powerplay, season>=2023
**Strategy:** View lookup -> `analytics_ipl_batter_vs_bowler_phase_since2023`

```sql
SELECT batter_name, bowler_name, match_phase,
  balls, runs, dismissals, strike_rate, average,
  dot_ball_pct, boundary_pct
FROM analytics_ipl_batter_vs_bowler_phase_since2023
WHERE batter_name ILIKE '%Kohli%'
  AND bowler_name ILIKE '%Bumrah%'
  AND match_phase = 'powerplay';
```

### 4.3 Performance Considerations (WASM DuckDB)

The Research Desk runs DuckDB-WASM in the browser. Key constraints and mitigations:

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| **Memory limit (~1GB in browser)** | Large `fact_ball` (2.1M rows) scans can be slow | Prefer pre-aggregated views over raw `fact_ball` queries. Only fall to `fact_ball` when views cannot satisfy the query. |
| **No parallelism** | Single-threaded execution in WASM | Keep CTEs minimal (1-2 levels). Avoid correlated subqueries where possible. |
| **Cold start latency** | First query after page load is slow (~2-3s) | Pre-warm DuckDB with a lightweight `SELECT 1` query on page load. Cache the connection object. |
| **No indexes on views** | Full scans on large views | Filter early in CTEs. Use `match_id IN (SELECT ...)` pattern to narrow fact_ball before aggregation. |
| **String matching overhead** | `ILIKE '%name%'` is O(n) on dim_player (7,864 rows) | For player lookups, resolve player_id first from a lightweight JS dictionary, then filter by ID instead of name. |
| **Dynamic SQL compilation** | Each new query must be parsed/planned | Limit SQL complexity to 3 CTEs max. Reuse CTE patterns (IPL filter, innings total). |

**Performance budget:**
- Simple view lookups: < 500ms
- Phase/venue view queries: < 1s
- Dynamic `fact_ball` queries with 2-3 joins: < 3s
- Complex pressure band queries: < 5s

**Optimization strategy:**
1. **View-first routing:** Always check if an existing view satisfies the query before building dynamic SQL. The 152 pre-computed views are the performance backbone.
2. **Player ID pre-resolution:** Resolve player names to `player_id` in JavaScript before embedding in SQL. Use `WHERE player_id = 'p123'` instead of `WHERE player_name ILIKE '%...'`.
3. **Dual-scope awareness:** Use `_since2023` views by default (smaller dataset = faster). Only use `_alltime` when user explicitly asks for "all time" or historical analysis.
4. **Progressive loading:** For complex queries, show a loading indicator and estimated time. If a query is expected to take > 3s, warn the user.

---

## 5. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Entity extraction misidentifies player names (common English words match) | HIGH | Queries return wrong data | Priority-based extraction: players first, check against dictionary. Require min 2-char match. |
| Complex dynamic SQL exceeds WASM memory on very large aggregations | MEDIUM | Browser tab crashes | Enforce max query scope (e.g., always filter to IPL). Add memory monitoring. Graceful error handling. |
| Ambiguous queries produce unexpected SQL | HIGH | User confusion | Always show "understood as" panel explaining extracted entities. Let user correct. |
| Performance regression on popular simple queries | LOW | UX degradation | Phase 1 must preserve current simple-query speed. View routing stays as fast path. |
| Nickname/alias dictionary maintenance | MEDIUM | "SKY" stops working if not maintained | Store aliases in a JSON config file, not hardcoded. Document maintenance process. |
| SQL injection via crafted NL queries | LOW | Security issue | Already mitigated by `escapeSql()` function. Dynamic SQL builder should parameterize all user input. |

---

## 6. Success Metrics

| Metric | Current | Target (Phase 2) | Target (Phase 4) |
|--------|---------|-------------------|-------------------|
| Query types supported | 11 patterns | 30+ intent combinations | 50+ |
| Win/loss context queries | 0 | Full support | Full support |
| Composite filter queries (3+ dimensions) | 0 | 10+ patterns | Arbitrary combinations |
| Entity extraction accuracy | ~70% (regex only) | 90%+ | 95%+ |
| Average query latency (simple) | <500ms | <500ms | <500ms |
| Average query latency (complex) | N/A (not supported) | <3s | <2s |
| Fallback rate (unresolvable queries) | ~40% | <15% | <10% |
| User satisfaction (manual review of top 50 queries) | Not measured | 80%+ correct | 90%+ correct |

---

*This document is a RESEARCH deliverable. No code modifications have been made. Implementation should follow the phased approach in Section 4.1, with Phase 1 targeted for Sprint 5.*

*Reviewed by: Andy Flower (Cricket Domain Expert) + Jose Mourinho (Quant Researcher)*
*Approved for planning by: Tom Brady (PO & Editor-in-Chief)*
