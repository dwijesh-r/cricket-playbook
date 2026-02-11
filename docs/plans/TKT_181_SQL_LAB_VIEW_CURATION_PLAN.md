# TKT-181: SQL Lab View Curation Plan

**Author:** Tom Brady (PO & Editor-in-Chief)
**Date:** 2026-02-11
**Status:** PLAN (pending Founder approval)
**Scope:** Film Room / Research Desk schema browser UX and view organization

---

## 1. Problem Statement

The SQL Lab (Film Room Research Desk) currently displays **all 152 analytics views** in a single flat "Analytics Views" group in the schema browser sidebar. This creates several problems:

- **Information overload** -- 152 views in one collapsed list is unusable. Users cannot quickly find what they need.
- **No curation hierarchy** -- A flagship view like `analytics_ipl_batting_career` sits alongside a niche deep-dive like `analytics_ipl_batter_vs_bowler_type_phase_alltime` with equal visual weight.
- **Cryptic names** -- View names like `analytics_ipl_batter_vs_bowler_type_phase_since2023` are technically accurate but hostile to casual users.
- **Duplicate scope variants clutter** -- Every base view has `_alltime` and `_since2023` siblings, tripling the list without adding discovery value.
- **No descriptions visible** -- The metadata has one-line descriptions, but they are auto-generated and generic (e.g., "IPL Batter phase since2023").

The Founder's direction is clear: **"We can't show all 152 views and dump information."** We need strategic presentation.

---

## 2. Current State Analysis

### 2.1 View Inventory Breakdown

| Category | Count | Notes |
|----------|-------|-------|
| All T20 (non-IPL) views | 15 | Legacy/comparison views (e.g., `analytics_batting_career`, `analytics_t20_batter_phase`) |
| IPL Base Views (no suffix) | 28 | Core analytical views without `_alltime` / `_since2023` suffix |
| IPL `_since2023` variants | 43 | Same logic filtered to IPL 2023+ |
| IPL `_alltime` variants | 43 | Same logic with no date filter |
| IPL Film Room views | 23 | Newer views from TKT-050 (pressure, context, partnership, etc.) |
| **Total** | **152** | |

### 2.2 Current Schema Browser Implementation

File: `scripts/the_lab/dashboard/research-desk.html`

The sidebar groups items into:
1. **Dimension Tables** (7) -- `dim_bowler_classification`, `dim_franchise_alias`, `dim_match`, `dim_player`, etc.
2. **Fact Tables** (3) -- `fact_ball`, `fact_player_match_performance`, `fact_powerplay`
3. **Reference Tables** (2) -- `ipl_2026_contracts`, `ipl_2026_squads`
4. **Analytics Tables** (2) -- `player_clusters_batters`, `player_clusters_bowlers`
5. **Analytics Views** (152) -- one flat, uncategorized list

Each group is collapsible. There is a text search box that filters by table/view name and column name. Clicking a view name expands its column list; a "SQL" button inserts `SELECT * FROM view LIMIT 100`.

### 2.3 Key Problems with Current UX

1. **One mega-group** -- 152 items in "Analytics Views" is a scroll-fest.
2. **No scope toggle** -- Users must manually choose between `_since2023` and `_alltime` suffixes.
3. **No favorites** -- Power users cannot pin frequently-used views.
4. **No descriptions in sidebar** -- Only visible via column tooltip on hover.
5. **No concept of "start here"** -- New users have no guidance on which views matter most.

---

## 3. View Tier System

### 3.1 Tier Definitions

| Tier | Label | Visibility | Count Target | Purpose |
|------|-------|------------|-------------|---------|
| **Featured** | Always visible, prominent | Default expanded, highlighted | 12-15 | "Start here" views. The most useful, self-contained views for editorial work. |
| **Standard** | Visible in categorized groups | Collapsed by default, searchable | 25-30 | Important views that support deeper analysis. Accessible but not front-and-center. |
| **Deep Dive** | Hidden behind "Show All" toggle | Not visible by default; requires expanding "Advanced" section or searching | 30-40 | Phase-specific breakdowns, venue-phase combos, niche matchups. |
| **Internal** | Excluded from SQL Lab sidebar | Not shown in browser at all | ~60-70 | Scope variants (`_alltime` / `_since2023`) handled via scope toggle, plus legacy All T20 views. |

### 3.2 Scope Toggle (Key UX Decision)

Rather than showing both `_since2023` and `_alltime` variants as separate views, implement a **global scope toggle** in the sidebar header:

```
[ IPL 2023+ (Recent) | All-Time ]
```

When a user selects a view, the system automatically appends the correct suffix based on the toggle state. This **immediately eliminates ~86 views** from the sidebar (43 `_alltime` + 43 `_since2023` pairs become 43 single entries).

For the ~28 base views that have no suffix (they ARE the `_since2023` version), the toggle maps:
- "Recent" -> base view name (e.g., `analytics_ipl_batting_career`)
- "All-Time" -> `_alltime` variant (e.g., `analytics_ipl_batting_career_alltime`)

---

## 4. Full View Inventory with Tier Assignments

### 4.1 Featured Tier (14 views)

These are the views that answer the most common editorial questions. Always visible, with rich descriptions.

| # | View Base Name | Display Name | Description |
|---|---------------|-------------|-------------|
| 1 | `analytics_ipl_batting_career` | **Batting Career Stats** | Career batting stats (SR, avg, boundary%, dots) for all IPL batters |
| 2 | `analytics_ipl_bowling_career` | **Bowling Career Stats** | Career bowling stats (economy, avg, SR, dot%) for all IPL bowlers |
| 3 | `analytics_ipl_squad_batting` | **Squad Batting Overview** | IPL 2026 squad batting stats with contract prices and T20 comparison |
| 4 | `analytics_ipl_squad_bowling` | **Squad Bowling Overview** | IPL 2026 squad bowling stats with contract prices and T20 comparison |
| 5 | `analytics_ipl_batter_phase` | **Batting by Phase** | Batter performance split by powerplay, middle, and death overs |
| 6 | `analytics_ipl_bowler_phase` | **Bowling by Phase** | Bowler performance split by powerplay, middle, and death overs |
| 7 | `analytics_ipl_batter_vs_bowler_type` | **Batter vs Bowling Style** | How batters perform against pace, off-spin, leg-spin, and left-arm |
| 8 | `analytics_ipl_team_roster` | **Team Rosters (2026)** | Full IPL 2026 squad roster with roles, prices, and player profiles |
| 9 | `analytics_ipl_batting_percentiles` | **Batting Percentile Rankings** | Where each batter ranks in SR, avg, boundary% vs IPL peer group |
| 10 | `analytics_ipl_bowling_percentiles` | **Bowling Percentile Rankings** | Where each bowler ranks in economy, avg, dot% vs IPL peer group |
| 11 | `analytics_ipl_career_benchmarks` | **IPL Career Benchmarks** | League-wide averages and medians for batting and bowling (comparison baseline) |
| 12 | `analytics_ipl_bowler_phase_distribution` | **Bowler Workload Distribution** | % of overs and wickets each bowler delivers per phase, with efficiency score |
| 13 | `analytics_ipl_batter_pressure_bands` | **Batter Pressure Bands** | How batters perform under different pressure scenarios |
| 14 | `analytics_ipl_bowler_pressure_bands` | **Bowler Pressure Bands** | How bowlers perform under different pressure scenarios |

### 4.2 Standard Tier (26 views)

Visible in categorized groups, collapsed by default.

| # | View Base Name | Display Name | Description |
|---|---------------|-------------|-------------|
| 1 | `analytics_ipl_batter_vs_bowler` | **Batter vs Bowler H2H** | Head-to-head batting stats for every batter-bowler pair |
| 2 | `analytics_ipl_batter_vs_team` | **Batter vs Opposition** | Batter performance against each IPL franchise |
| 3 | `analytics_ipl_bowler_vs_team` | **Bowler vs Opposition** | Bowler performance against each IPL franchise |
| 4 | `analytics_ipl_batter_venue` | **Batter by Venue** | Batter performance at each ground |
| 5 | `analytics_ipl_bowler_venue` | **Bowler by Venue** | Bowler performance at each ground |
| 6 | `analytics_ipl_bowler_vs_batter_handedness` | **Bowler vs Left/Right Hand** | Bowler stats split by batter handedness |
| 7 | `analytics_ipl_squad_batting_phase` | **Squad Batting by Phase** | IPL 2026 squad members' batting by phase |
| 8 | `analytics_ipl_squad_bowling_phase` | **Squad Bowling by Phase** | IPL 2026 squad members' bowling by phase |
| 9 | `analytics_ipl_batting_benchmarks` | **Phase Batting Benchmarks** | League-wide batting averages by phase (for contextual comparison) |
| 10 | `analytics_ipl_bowling_benchmarks` | **Phase Bowling Benchmarks** | League-wide bowling averages by phase (for contextual comparison) |
| 11 | `analytics_ipl_vs_bowler_type_benchmarks` | **Bowler Type Benchmarks** | League-wide batting stats vs each bowling style |
| 12 | `analytics_ipl_batter_phase_percentiles` | **Phase Batting Percentiles** | Phase-specific percentile rankings for batters |
| 13 | `analytics_ipl_bowler_phase_percentiles` | **Phase Bowling Percentiles** | Phase-specific percentile rankings for bowlers |
| 14 | `analytics_ipl_match_context` | **Match Context Summary** | Innings-level totals, targets, and outcomes for each match |
| 15 | `analytics_ipl_partnership_analysis` | **Partnership Analysis** | Batting partnership runs, balls, strike rates, and phase splits |
| 16 | `analytics_ipl_innings_progression` | **Innings Progression** | Over-by-over scoring trajectory for each innings |
| 17 | `analytics_ipl_batter_entry_point` | **Batter Entry Points** | When each batter comes in: position, over, team state, chase target |
| 18 | `analytics_ipl_venue_profile` | **Venue Profiles** | Ground-level scoring patterns, average totals, and phase tendencies |
| 19 | `analytics_ipl_team_phase_scoring` | **Team Phase Scoring** | How each team scores across powerplay, middle, and death overs |
| 20 | `analytics_ipl_dot_ball_pressure` | **Dot Ball Pressure Index** | Dot ball sequences and their impact on scoring and wickets |
| 21 | `analytics_ipl_new_batter_vulnerability` | **New Batter Vulnerability** | Performance in first N balls after arriving at crease |
| 22 | `analytics_ipl_wicket_clusters` | **Wicket Clusters** | Patterns of wicket-falling sequences in innings |
| 23 | `analytics_ipl_pressure_deltas` | **Pressure Momentum Deltas** | Scoring acceleration/deceleration under pressure |
| 24 | `analytics_ipl_required_rate_performance` | **Required Rate Performance** | How batters/bowlers perform at different required run rates |
| 25 | `analytics_ipl_batting_order_flexibility` | **Batting Order Flexibility** | Which batters can perform across multiple positions |
| 26 | `analytics_ipl_bowling_change_impact` | **Bowling Change Impact** | Impact of bringing on a new bowler mid-spell |

### 4.3 Deep Dive Tier (32 views)

Hidden behind "Show Advanced Views" toggle. These are multi-dimensional cross-cuts (phase x matchup x venue) for power users writing deep analytical pieces.

| # | View Base Name | Display Name | Description |
|---|---------------|-------------|-------------|
| 1 | `analytics_ipl_batter_vs_bowler_phase` | Batter vs Bowler by Phase | H2H batting with phase split |
| 2 | `analytics_ipl_batter_vs_bowler_type_phase` | Batter vs Bowling Style by Phase | Batting vs bowling types with phase split |
| 3 | `analytics_ipl_bowler_vs_batter_phase` | Bowler vs Batter by Phase | H2H from bowler's perspective with phase split |
| 4 | `analytics_ipl_batter_vs_team_phase` | Batter vs Opposition by Phase | Batting vs franchise with phase split |
| 5 | `analytics_ipl_bowler_vs_team_phase` | Bowler vs Opposition by Phase | Bowling vs franchise with phase split |
| 6 | `analytics_ipl_batter_venue_phase` | Batter at Venue by Phase | Batting at each ground with phase split |
| 7 | `analytics_ipl_bowler_venue_phase` | Bowler at Venue by Phase | Bowling at each ground with phase split |
| 8 | `analytics_ipl_bowler_over_breakdown` | Bowler Over-by-Over | Granular over-level bowling breakdown |
| 9 | `analytics_ipl_pressure_boundary_sequences` | Pressure Boundary Sequences | Boundary clusters and their game context |
| 10 | `analytics_ipl_pressure_dot_sequences` | Pressure Dot Sequences | Dot ball clusters and their game context |
| 11 | `analytics_ipl_squad_batting_alltime` | Squad Batting (All-Time) | Squad batting stats using full IPL history |
| 12 | `analytics_ipl_squad_bowling_alltime` | Squad Bowling (All-Time) | Squad bowling stats using full IPL history |
| 13 | `analytics_ipl_squad_batting_phase_alltime` | Squad Batting Phase (All-Time) | Squad batting by phase using full IPL history |
| 14 | `analytics_ipl_squad_bowling_phase_alltime` | Squad Bowling Phase (All-Time) | Squad bowling by phase using full IPL history |
| 15 | `analytics_ipl_bowler_phase_distribution_alltime` | Bowler Workload (All-Time) | Phase workload distribution for full IPL history |
| 16 | `analytics_t20_batter_phase` | All T20: Batting by Phase | Cross-tournament batting by phase (not IPL-specific) |
| 17 | `analytics_t20_batter_vs_bowler_type` | All T20: Batter vs Bowling Style | Cross-tournament matchup data |
| 18 | `analytics_t20_bowler_phase` | All T20: Bowling by Phase | Cross-tournament bowling by phase |

**Note:** The remaining ~14 views in Deep Dive tier are the `_since2023` / `_alltime` explicit aliases for squad views and non-standard scope variants that don't fit the toggle pattern cleanly. These will be accessible via search or the advanced panel.

### 4.4 Internal Tier (Excluded from SQL Lab -- ~66 views)

These are **not displayed** in the schema browser at all. They remain queryable via the SQL editor (users can type `SELECT * FROM view_name`), but are excluded from the sidebar.

| Category | View Pattern | Count | Reason |
|----------|-------------|-------|--------|
| Scope variants (since2023) | `analytics_ipl_*_since2023` | ~27 | Handled by scope toggle; base view is the default |
| Scope variants (alltime) | `analytics_ipl_*_alltime` | ~27 | Handled by scope toggle |
| Redundant squad scope aliases | `analytics_ipl_squad_*_since2023`, `analytics_ipl_team_roster_since2023/alltime` | ~6 | Base squad views already use 2023+ data; aliases are redundant |
| Legacy All T20 base views | `analytics_batting_career`, `analytics_bowling_career`, etc. | ~12 | Global T20 views not relevant to IPL 2026 editorial focus |

**Guiding principle:** If a view is strictly a scope variant of another view AND the scope toggle handles it, exclude it from the sidebar. The user can always type the full name in the SQL editor.

---

## 5. Naming Strategy

### 5.1 Display Name Convention

All views get human-readable display names in `table_metadata.json`. The convention:

```
[Subject] [Analysis Type] ([Scope/Qualifier])
```

Examples:
| Technical Name | Display Name |
|---------------|-------------|
| `analytics_ipl_batting_career` | Batting Career Stats |
| `analytics_ipl_batter_phase` | Batting by Phase |
| `analytics_ipl_batter_vs_bowler_type` | Batter vs Bowling Style |
| `analytics_ipl_batter_vs_bowler_type_phase` | Batter vs Bowling Style by Phase |
| `analytics_ipl_squad_batting` | Squad Batting Overview |
| `analytics_ipl_batting_percentiles` | Batting Percentile Rankings |
| `analytics_ipl_bowler_phase_distribution` | Bowler Workload Distribution |
| `analytics_ipl_batter_pressure_bands` | Batter Pressure Bands |
| `analytics_ipl_dot_ball_pressure` | Dot Ball Pressure Index |
| `analytics_ipl_new_batter_vulnerability` | New Batter Vulnerability |
| `analytics_ipl_venue_profile` | Venue Profiles |

### 5.2 Rules

1. **Drop prefixes** -- Never show `analytics_ipl_` in the display name. It is noise.
2. **Drop scope suffixes** -- Never show `_since2023` or `_alltime` in the display name. The scope toggle handles this.
3. **Use natural language** -- "Batter vs Bowling Style" not "batter_vs_bowler_type".
4. **Keep it under 35 characters** -- The sidebar is 280px wide; names must fit.
5. **Add parenthetical context sparingly** -- Only when genuinely clarifying, e.g., "(All T20)" for cross-tournament views.
6. **Tooltip shows full technical name** -- On hover, show the actual SQL view name for copy-paste.

### 5.3 Metadata Schema Extension

Add these fields to each view entry in `table_metadata.json`:

```json
{
  "display_name": "Batting Career Stats",
  "description": "Career batting stats (SR, avg, boundary%, dots) for all IPL batters",
  "tier": "featured",
  "category": "batting",
  "scope_base": "analytics_ipl_batting_career",
  "scope_variants": {
    "recent": "analytics_ipl_batting_career",
    "alltime": "analytics_ipl_batting_career_alltime"
  }
}
```

---

## 6. Category Organization

### 6.1 Category Definitions

| Category | Icon | Color | Description | Featured Count |
|----------|------|-------|-------------|---------------|
| **Batting** | bat icon | `--accent-teal` | Individual batter career, phase, percentile, and benchmark views | 5 |
| **Bowling** | ball icon | `--accent-orange` | Individual bowler career, phase, percentile, distribution, and benchmark views | 5 |
| **Matchups** | crosshairs | `--accent-purple` | Batter vs bowler (H2H), batter vs bowling type, bowler vs handedness | 1 |
| **Team & Squad** | shield icon | `--accent-green` | Squad overviews, team rosters, team phase scoring | 3 |
| **Venue & Context** | stadium | `--accent-yellow` | Venue profiles, batter/bowler at venue, match context | 0 (Standard tier) |
| **Pressure & Situational** | gauge | `--accent-red` | Pressure bands, dot ball pressure, required rate, wicket clusters, new batter vulnerability | 2 |
| **Benchmarks** | ruler | `--accent` (blue) | League-wide batting/bowling averages, vs-type benchmarks, career benchmarks | 0 (Standard tier) |
| **Progression & Partnerships** | chart | `--accent-pink` | Innings progression, partnership analysis, batting order flexibility | 0 (Standard tier) |

### 6.2 Category Mapping (Full)

| Category | Featured Views | Standard Views | Deep Dive Views |
|----------|---------------|----------------|-----------------|
| **Batting** | Batting Career Stats, Batting by Phase, Batter vs Bowling Style, Batting Percentile Rankings, Batter Pressure Bands | Batter vs Opposition, Batter by Venue, Phase Batting Percentiles | Batter vs Bowler Type by Phase, Batter vs Opposition by Phase, Batter at Venue by Phase |
| **Bowling** | Bowling Career Stats, Bowling by Phase, Bowling Percentile Rankings, Bowler Workload Distribution, Bowler Pressure Bands | Bowler vs Opposition, Bowler by Venue, Bowler vs Left/Right Hand, Phase Bowling Percentiles | Bowler vs Batter by Phase, Bowler vs Opposition by Phase, Bowler at Venue by Phase, Bowler Over-by-Over |
| **Matchups** | -- | Batter vs Bowler H2H | Batter vs Bowler by Phase, Bowler vs Batter by Phase |
| **Team & Squad** | Squad Batting Overview, Squad Bowling Overview, Team Rosters (2026) | Squad Batting by Phase, Squad Bowling by Phase, Team Phase Scoring | Squad All-Time variants |
| **Venue & Context** | -- | Venue Profiles, Match Context Summary | -- |
| **Pressure & Situational** | -- | Dot Ball Pressure Index, New Batter Vulnerability, Wicket Clusters, Pressure Momentum Deltas, Required Rate Performance | Pressure Boundary Sequences, Pressure Dot Sequences |
| **Benchmarks** | IPL Career Benchmarks | Phase Batting Benchmarks, Phase Bowling Benchmarks, Bowler Type Benchmarks | -- |
| **Progression & Partnerships** | -- | Innings Progression, Partnership Analysis, Batter Entry Points, Batting Order Flexibility, Bowling Change Impact | -- |

---

## 7. Schema Browser UX Redesign

### 7.1 Sidebar Layout (Top to Bottom)

```
+----------------------------------+
| SCHEMA BROWSER         [scope]   |
| [Recent 2023+] [All-Time]        |
+----------------------------------+
| [  Search views...            ]  |
+----------------------------------+
| * FEATURED (14)            star  |
|   > Batting Career Stats         |
|   > Bowling Career Stats         |
|   > Squad Batting Overview       |
|   > ...                          |
+----------------------------------+
| v BATTING (8)                    |
|   > Batter vs Opposition         |
|   > Batter by Venue              |
|   > ...                          |
+----------------------------------+
| v BOWLING (9)                    |
| v MATCHUPS (3)                   |
| v TEAM & SQUAD (5)              |
| v VENUE & CONTEXT (2)           |
| v PRESSURE & SITUATIONAL (7)    |
| v BENCHMARKS (4)                |
| v PROGRESSION (5)               |
+----------------------------------+
| [Show Advanced Views (32)]       |
+----------------------------------+
| DATA TABLES                      |
| v Dimension Tables (7)          |
| v Fact Tables (3)               |
| v Reference Tables (2)          |
| v Analytics Tables (2)          |
+----------------------------------+
```

### 7.2 Interaction Patterns

| Feature | Behavior |
|---------|----------|
| **Featured section** | Always expanded by default. Highlighted with a star icon. Items shown with display names. |
| **Category sections** | Collapsed by default. Click to expand. Show count badge. |
| **Scope toggle** | Two buttons at sidebar top: "Recent (2023+)" and "All-Time". Default: Recent. When user clicks a view, the SQL uses the correct suffixed variant. |
| **Search** | Searches across display names, technical names, AND descriptions. Results show across all tiers (including Deep Dive). |
| **View item hover** | Shows tooltip with: technical view name, one-line description, scope indicator. |
| **View item click** | Expands column list (existing behavior). |
| **SQL button** | Generates `SELECT * FROM <scoped_view_name> LIMIT 100`. Respects scope toggle. |
| **Show Advanced Views** | Toggle button at bottom of categorized sections. Reveals Deep Dive tier views in their categories. |
| **Favorites** | Phase 2 feature. Star icon on each view to pin it to a "My Favorites" section at top. Stored in localStorage. |

### 7.3 Visual Treatment

| Tier | Background | Font Weight | Icon |
|------|-----------|-------------|------|
| Featured | Subtle highlight (`rgba(10, 132, 255, 0.05)`) | 600 (semi-bold) | Star |
| Standard | Default | 400 (normal) | Category icon |
| Deep Dive | Slightly dimmed text | 400 | Dashed circle |

---

## 8. View Descriptions (Featured Tier)

These descriptions appear as tooltips and in search results.

| View | One-Line Description |
|------|---------------------|
| Batting Career Stats | IPL career batting: runs, strike rate, average, boundary%, dot ball% for all batters |
| Bowling Career Stats | IPL career bowling: wickets, economy, average, strike rate, dot% for all bowlers |
| Squad Batting Overview | 2026 squad batting stats with contract price, IPL + T20 career comparison |
| Squad Bowling Overview | 2026 squad bowling stats with contract price, IPL + T20 career comparison |
| Batting by Phase | Batter SR, avg, and boundary% split by powerplay, middle, and death overs |
| Bowling by Phase | Bowler economy, avg, and dot% split by powerplay, middle, and death overs |
| Batter vs Bowling Style | How each batter performs against pace, off-spin, leg-spin, left-arm spin |
| Team Rosters (2026) | Complete IPL 2026 squads: player names, roles, bowling styles, contract details |
| Batting Percentile Rankings | Each batter's percentile rank in SR, avg, boundary%, and dot ball% (min 500 balls) |
| Bowling Percentile Rankings | Each bowler's percentile rank in economy, avg, SR, and dot% (min 300 balls) |
| IPL Career Benchmarks | League-wide median and mean for batting SR/avg and bowling economy/avg |
| Bowler Workload Distribution | % of each bowler's overs and wickets in PP/middle/death with efficiency score |
| Batter Pressure Bands | Batting performance bucketed by game pressure situations |
| Bowler Pressure Bands | Bowling performance bucketed by game pressure situations |

---

## 9. Implementation Plan

### 9.1 Metadata Changes (`table_metadata.json`)

| Step | Task | Effort |
|------|------|--------|
| 1 | Add `display_name`, `tier`, `category`, and `scope_variants` fields to every view entry | Medium |
| 2 | Write meaningful one-line descriptions for all Featured and Standard tier views | Medium |
| 3 | Mark Internal tier views with `"tier": "internal"` so the renderer can skip them | Small |
| 4 | Create a `generate_view_metadata.py` script to auto-populate scope variants and base mappings | Medium |

### 9.2 Frontend Changes (`research-desk.html`)

| Step | Task | Effort |
|------|------|--------|
| 5 | Add scope toggle UI (two buttons in schema header) | Small |
| 6 | Refactor `buildInteractiveSchema()` to group views by `category` instead of one flat list | Medium |
| 7 | Add Featured section rendering with star icon and always-expanded behavior | Small |
| 8 | Add "Show Advanced Views" toggle button at bottom of categories | Small |
| 9 | Update search to match against `display_name` and `description` in addition to technical name | Small |
| 10 | Update SQL button click handler to apply scope suffix based on toggle state | Small |
| 11 | Filter out Internal tier views from sidebar rendering | Small |
| 12 | Add display name rendering in sidebar items (with technical name in tooltip) | Small |

### 9.3 Phase 2 (Post-Sprint 4)

| Step | Task | Effort |
|------|------|--------|
| 13 | Add localStorage-based Favorites system | Medium |
| 14 | Add "Recently Used" section below Favorites | Small |
| 15 | Add view relationship hints (e.g., "Related: Phase Percentiles" when viewing Batting by Phase) | Medium |

### 9.4 Estimated Timeline

| Phase | Scope | Duration |
|-------|-------|----------|
| Phase 1 (metadata) | Steps 1-4 | 1 session |
| Phase 1 (frontend) | Steps 5-12 | 1-2 sessions |
| Phase 2 (polish) | Steps 13-15 | 1 session |

---

## 10. Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Views visible in sidebar (default state) | 152 | ~40 (14 Featured + ~26 Standard) |
| Time to find a specific view | Scroll + scan 152 items | Search by description or browse category |
| Scope switching | Manual suffix editing in SQL | One-click toggle |
| Views with meaningful descriptions | 0 (auto-generated only) | 40+ (all Featured + Standard) |
| Views with human-readable display names | 0 | All 72 non-internal views |

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Power users rely on current flat list and resist change | Medium | Search still finds everything; all views remain queryable by typing in editor |
| Scope toggle adds confusion for users who want a specific variant | Low | Tooltip always shows the resolved technical name; advanced users can type directly |
| Metadata maintenance burden as new views are added | Medium | `generate_view_metadata.py` script auto-detects views and applies naming rules |
| Internal-tier views become invisible and forgotten | Low | They are documented here and remain in the analytics layer; just hidden from casual browsing |

---

## 12. Appendix: Full View-to-Category Mapping Reference

This is the authoritative mapping for the metadata update.

### Batting Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_batting_career` | Batting Career Stats | Featured |
| `analytics_ipl_batter_phase` | Batting by Phase | Featured |
| `analytics_ipl_batter_vs_bowler_type` | Batter vs Bowling Style | Featured |
| `analytics_ipl_batting_percentiles` | Batting Percentile Rankings | Featured |
| `analytics_ipl_batter_pressure_bands` | Batter Pressure Bands | Featured |
| `analytics_ipl_batter_vs_team` | Batter vs Opposition | Standard |
| `analytics_ipl_batter_venue` | Batter by Venue | Standard |
| `analytics_ipl_batter_phase_percentiles` | Phase Batting Percentiles | Standard |
| `analytics_ipl_batter_vs_bowler_type_phase` | Batter vs Bowling Style by Phase | Deep Dive |
| `analytics_ipl_batter_vs_team_phase` | Batter vs Opposition by Phase | Deep Dive |
| `analytics_ipl_batter_venue_phase` | Batter at Venue by Phase | Deep Dive |

### Bowling Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_bowling_career` | Bowling Career Stats | Featured |
| `analytics_ipl_bowler_phase` | Bowling by Phase | Featured |
| `analytics_ipl_bowling_percentiles` | Bowling Percentile Rankings | Featured |
| `analytics_ipl_bowler_phase_distribution` | Bowler Workload Distribution | Featured |
| `analytics_ipl_bowler_pressure_bands` | Bowler Pressure Bands | Featured |
| `analytics_ipl_bowler_vs_team` | Bowler vs Opposition | Standard |
| `analytics_ipl_bowler_venue` | Bowler by Venue | Standard |
| `analytics_ipl_bowler_vs_batter_handedness` | Bowler vs Left/Right Hand | Standard |
| `analytics_ipl_bowler_phase_percentiles` | Phase Bowling Percentiles | Standard |
| `analytics_ipl_bowler_vs_batter_phase` | Bowler vs Batter by Phase | Deep Dive |
| `analytics_ipl_bowler_vs_team_phase` | Bowler vs Opposition by Phase | Deep Dive |
| `analytics_ipl_bowler_venue_phase` | Bowler at Venue by Phase | Deep Dive |
| `analytics_ipl_bowler_over_breakdown` | Bowler Over-by-Over Breakdown | Deep Dive |

### Matchups Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_batter_vs_bowler` | Batter vs Bowler H2H | Standard |
| `analytics_ipl_batter_vs_bowler_phase` | Batter vs Bowler by Phase | Deep Dive |
| `analytics_ipl_bowler_vs_batter_phase` | Bowler vs Batter by Phase | Deep Dive |

### Team & Squad Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_squad_batting` | Squad Batting Overview | Featured |
| `analytics_ipl_squad_bowling` | Squad Bowling Overview | Featured |
| `analytics_ipl_team_roster` | Team Rosters (2026) | Featured |
| `analytics_ipl_squad_batting_phase` | Squad Batting by Phase | Standard |
| `analytics_ipl_squad_bowling_phase` | Squad Bowling by Phase | Standard |
| `analytics_ipl_team_phase_scoring` | Team Phase Scoring | Standard |

### Venue & Context Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_venue_profile` | Venue Profiles | Standard |
| `analytics_ipl_match_context` | Match Context Summary | Standard |

### Pressure & Situational Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_dot_ball_pressure` | Dot Ball Pressure Index | Standard |
| `analytics_ipl_new_batter_vulnerability` | New Batter Vulnerability | Standard |
| `analytics_ipl_wicket_clusters` | Wicket Clusters | Standard |
| `analytics_ipl_pressure_deltas` | Pressure Momentum Deltas | Standard |
| `analytics_ipl_required_rate_performance` | Required Rate Performance | Standard |
| `analytics_ipl_pressure_boundary_sequences` | Pressure Boundary Sequences | Deep Dive |
| `analytics_ipl_pressure_dot_sequences` | Pressure Dot Sequences | Deep Dive |

### Benchmarks Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_career_benchmarks` | IPL Career Benchmarks | Featured |
| `analytics_ipl_batting_benchmarks` | Phase Batting Benchmarks | Standard |
| `analytics_ipl_bowling_benchmarks` | Phase Bowling Benchmarks | Standard |
| `analytics_ipl_vs_bowler_type_benchmarks` | Bowler Type Benchmarks | Standard |

### Progression & Partnerships Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_ipl_innings_progression` | Innings Progression | Standard |
| `analytics_ipl_partnership_analysis` | Partnership Analysis | Standard |
| `analytics_ipl_batter_entry_point` | Batter Entry Points | Standard |
| `analytics_ipl_batting_order_flexibility` | Batting Order Flexibility | Standard |
| `analytics_ipl_bowling_change_impact` | Bowling Change Impact | Standard |

### All T20 (Cross-Tournament) Category

| View Base Name | Display Name | Tier |
|---------------|-------------|------|
| `analytics_t20_batter_phase` | All T20: Batting by Phase | Deep Dive |
| `analytics_t20_batter_vs_bowler_type` | All T20: Batter vs Bowling Style | Deep Dive |
| `analytics_t20_bowler_phase` | All T20: Bowling by Phase | Deep Dive |

---

## 13. Sign-off

| Role | Agent | Status |
|------|-------|--------|
| PO & Editor-in-Chief | Tom Brady | AUTHORED |
| Founder | -- | PENDING |
| Analytics Lead | Stephen Curry | PENDING REVIEW |
| UX & Reader Flow | Jayson Tatum | PENDING REVIEW |
| Architecture | Brad Stevens | PENDING REVIEW |

---

*This plan reduces the SQL Lab sidebar from 152 undifferentiated views to ~40 curated, human-named, categorized views -- with zero loss of queryability for power users.*
