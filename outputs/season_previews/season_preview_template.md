# Season Preview Template: Production Manual

**Cricket Playbook | IPL 2026 Season Preview Series**
*Owners: Virat Kohli (Tone & Narrative Guard), Tom Brady (PO & Editor-in-Chief)*
*Domain Accuracy: Andy Flower | Quant Validation: Jose Mourinho | QA: N'Golo Kante*
*Version: 1.0.0 | Date: 2026-02-14*

This document is the single source of truth for producing all 10 IPL 2026 season previews. It codifies the structure, tone, data requirements, Lab integration format, and quality gates established by the approved RCB sample (`RCB_season_preview_sample.md`). Every preview must conform to this template. No exceptions.

---

## A. Document Format Specification

### A.1 Section Order (14 Sections)

The RCB sample established a 14-section structure. The editorial plan v1.1 listed 18 conceptual sections; the actual approved output consolidates them into 14 distinct document sections. This is the binding order.

| # | Section | Word Target | Mandatory | Contains Tables |
|---|---------|-------------|-----------|-----------------|
| 1 | The Headline | 30-60 words | Yes | No |
| 2 | The Story | 400-500 words | Yes | No |
| 3 | Off-Season Changes | 300-450 words | Yes | No |
| 4 | New Additions | 150-350 words (varies by count) | Yes | No |
| 5 | Full Squad Table | Table + 1 line summary | Yes | Yes (2 tables) |
| 6 | Team Style Analysis | 300-450 words | Yes | Yes (2-3 tables) |
| 7 | Category Ratings | Table + 100-150 words | Yes | Yes (1 table) |
| 8 | Team Batting Profile | 600-900 words | Yes | Yes (3-4 tables) |
| 9 | Innings Context: Setting vs Chasing | 1000-1500 words | Yes | Yes (8-10 tables) |
| 10 | Venue Analysis | 200-350 words | Yes | Yes (2 tables) |
| 11 | Schedule Analysis | 50-100 words (placeholder) | Yes (placeholder) | No |
| 12 | Head-to-Head Record | 300-500 words | Yes | Yes (2 tables) |
| 13 | Players to Watch | 400-600 words (3-4 profiles) | Yes | No |
| 14 | Players Who Need to Step Up | 200-400 words (2-3 profiles) | Yes | No |
| 15 | Recent Form | Table + 200-300 words | Yes | Yes (2 tables) |
| 16 | Interesting Data Insights | 400-700 words (3-5 insights) | Yes | No |
| 17 | The Bold Take | 150-250 words | Yes | No |
| 18 | By the Numbers | Table (5 stats exactly) | Yes | Yes (1 table) |
| 19 | Keys to Victory | 300-500 words (3-4 keys) | Yes | No |
| 20 | Andy Flower's Scouting Report | 300-500 words | Yes | No |
| 21 | Verdict | 30-80 words | Yes | No |

**Total per team:** 3,500-5,500 words (the RCB sample came in at approximately 5,000 words including tables).

### A.2 Document Header Format

Every preview begins with this exact header structure:

```markdown
# {Team Full Name}: IPL 2026 Season Preview

**Cricket Playbook | Season Preview Series**
*Agent: Virat Kohli (Tone & Narrative) | Domain: Andy Flower (Scouting Report)*
*Data Window: IPL 2023-2025 | {match_count} matches / {ball_count} balls*
*Revision: v{X.Y} | {revision_notes}*
```

Fields:
- `{Team Full Name}`: Full franchise name (e.g., "Royal Challengers Bengaluru")
- `{match_count}`: Total IPL matches in the DuckDB dataset
- `{ball_count}`: Total balls in the dataset (formatted with M for millions, e.g., "2.14M")
- `{revision_notes}`: Latest revision context (e.g., "Jose Mourinho corrections applied; score target 9.0")

### A.3 Section-by-Section Requirements

---

#### Section 1: The Headline

**Purpose:** One-sentence thesis. The single most important storyline for this team in 2026.

**Format:**
```markdown
## The Headline

**{Headline text in bold.}**
```

Followed by a 2-4 sentence supporting paragraph that substantiates the headline with one or two key data points.

**Rules:**
- Must be a thesis, not a label. "The Bowling-First Revolution Is Real. Now Comes the Hard Part." not "RCB Preview 2026."
- Must provoke thought. The reader should want to know *why*.
- Draws from depth chart analysis, tactical insights, and the team's defining question for 2026.
- One paragraph max after the headline. This is the hook, not the story.

**Data Sources:** Depth chart ratings, team phase data, composite rankings.

---

#### Section 2: The Story

**Purpose:** Narrative context. What happened in 2025, what changed, and what the central question is for 2026.

**Format:** 3-5 paragraphs of continuous prose. No tables, no bullet points.

**Must Include:**
- 2025 season trajectory and outcome
- Key personnel changes (retentions, departures, auction buys) summarized at narrative level
- The central strategic question for 2026
- A closing paragraph framing what success and failure look like

**Rules:**
- Open with the franchise's 2025 trajectory
- Mention price (Cr) and acquisition type on first mention of any player
- Defer tactical specifics to later sections. This section is narrative-first.
- Must include at least 2 specific data points (e.g., economy, win rate, SR) to ground the narrative

**Data Sources:** `ipl_2026_contracts`, `ipl_2026_squads`, team phase data, recent form.

---

#### Section 3: Off-Season Changes

**Purpose:** Factual accounting of what changed between 2025 and 2026.

**Must Include (use subheadings):**
- **Captaincy:** Current captain, whether changed, batting position, context
- **Key Departures:** Names, destinations (if known), what they provided, what gap their exit creates. Use an analogy or comparison for the most significant departure.
- **Key Retentions:** Anchors of the squad with prices. Identify any retention that signals a strategic bet (e.g., retaining an uncapped player cheaply).
- **Auction Strategy:** Total spend, marquee buy, overall approach (e.g., "keep the band together" vs "rebuild").
- **What's Structurally Different from 2025:** One paragraph synthesizing the net effect of all changes.

**Data Sources:** `ipl_2026_contracts` (compare `year_joined` and `acquisition_type`), `founder_squads_2026.json`, public reporting.

---

#### Section 4: New Additions

**Purpose:** Mini-profile for each new signing (auction purchases, year_joined = 2026).

**Format:** Each player gets a subheading and 2-5 sentences.

**Per-Player Must Include:**
- Name, price (Cr), role, nationality
- Key IPL stat with sample size and confidence label
- What gap they fill or who they replace
- Style fit with the team
- One flag or concern (if applicable), including confidence label

**Rules:**
- Order by price descending (marquee buy first)
- Players with zero IPL data: state "Uncapped in IPL" and describe what they bring based on role/profile
- Always include confidence labels (HIGH/MEDIUM/LOW) for stats cited

**Data Sources:** `ipl_2026_contracts` filtered by `year_joined = 2026`, `analytics_ipl_batting_career_since2023`, `analytics_ipl_bowling_career_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_bowler_phase_since2023`.

---

#### Section 5: Full Squad Table

**Purpose:** Complete squad roster with predicted XII separated from bench.

**Format:** Two tables (Predicted XII, Bench) with one summary line below.

**Table Columns (both tables):**

| # | Name | Role | Price (Cr) | Nat | Key Stat (IPL since 2023) | Founder Notes |

**Rules:**
- Predicted XII numbered 1-11 or 1-12 (depending on whether the team plays 11 or 12)
- Bench numbered sequentially after the XII
- Captain marked with "(c)" after name
- Key Stat: Single most relevant number for the player's role:
  - Batters: SR with ball count and confidence label
  - Bowlers: Economy with over count, phase context, and confidence label
  - Keepers: SR or dual role stat
  - All-rounders: Primary contribution metric
  - Uncapped players: "Uncapped IPL, {role description}"
- Founder Notes column always present, always blank (reserved for Founder annotation)
- Summary line: `**Total squad salary:** {X} Cr | **Overseas slots in XII:** {Y} ({names})`

**Data Sources:** `ipl_2026_squads`, `ipl_2026_contracts`, `analytics_ipl_batting_career_since2023`, `analytics_ipl_bowling_career_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_bowler_phase_since2023`.

---

#### Section 6: Team Style Analysis

**Purpose:** Define the team's tactical identity and how it has evolved.

**Must Include:**
- Year-over-year comparison tables (at minimum 2024 vs 2025)
- Phase profile tables with Batting SR and Bowling Economy per phase
- A "Delta from Previous Year" column in the 2025 table
- Squad-building philosophy paragraph synthesizing what the numbers reveal
- Sub-headings with descriptive titles (e.g., "2024: Still Living in the Past", "2025: Somebody Read the Memo")

**Table Format (per-season):**

| Phase | Batting SR | Bowling Economy |

**Table Format (comparison year):**

| Phase | Batting SR | Bowling Economy | Delta from {Year} |

**Data Sources:** `analytics_ipl_team_phase_batting_since2023`, `analytics_ipl_team_phase_bowling_since2023` filtered by season.

---

#### Section 7: Category Ratings

**Purpose:** Quantified 1-10 ratings for batting and bowling by phase, plus an overall composite.

**Table Format:**

| Category | Rating | Key Metric (2025) | Context |

**Required Rows (7 exactly):**
1. Batting, Powerplay
2. Batting, Middle
3. Batting, Death
4. Bowling, Powerplay
5. Bowling, Middle
6. Bowling, Death
7. Overall

**Rules:**
- Ratings are X/10 format (one decimal allowed)
- Key Metric: the specific number that drives the rating (e.g., "154.1 SR", "8.73 econ")
- Context: one sentence explaining why the rating is what it is, referencing specific players
- Overall rating is a composite, not an average. Weight bowling slightly higher for bowling-first teams, batting slightly higher for batting-first teams.
- Follow the table with 2-3 sentences summarizing the profile (peaks and valleys)

**Data Sources:** `analytics_ipl_team_phase_batting_since2023`, `analytics_ipl_team_phase_bowling_since2023`, depth chart ratings, composite rankings.

**Derivation Method:**
- Compare team phase metrics to league averages
- Normalize: league-average performance = 5.0/10
- Each standard deviation above/below = roughly 1.0 point
- Cap at 1.0 and 10.0
- Cross-reference with depth chart ratings for validation

---

#### Section 8: Team Batting Profile

**Purpose:** Where the team scores freely and where they get stuck, analyzed by bowling type and by phase, culminating in a Phase x Bowling Type cross-reference.

**Must Include (3 sub-sections):**

**8a. vs. Bowling Types (Since 2023)**

| Bowling Type | Team SR | League Avg SR | Diff | Verdict |

Required bowling types (6 rows):
1. Right-arm pace
2. Left-arm pace
3. Leg-spin
4. Left-arm wrist-spin
5. Left-arm orthodox
6. Off-spin

Followed by 1-2 paragraphs interpreting the pattern (dominant types, vulnerabilities).

**8b. Phase-Wise Batting (Since 2023)**

| Phase | Team SR | League SR | Diff | Boundary % (Team / League) | Dot % (Team / League) |

3 rows: Powerplay, Middle, Death. Followed by per-phase interpretation.

**8c. Phase x Bowling Type Cross-Reference**

| Scenario | Team SR | Sample | Confidence | Context |

Select the 3-5 most revealing combinations (typically: strongest scenario, weakest scenario, and 1-2 that tell a tactical story). Each row needs sample size in balls and a confidence label.

Follow with 2-3 paragraphs of tactical interpretation. End with the specific tactical implication for opposition captains.

**How to Derive Phase x Bowling Type Data:**
1. Query `analytics_ipl_batter_vs_bowler_type_phase_since2023`
2. Filter to team's batters (join with `ipl_2026_squads`)
3. Aggregate SR across all team batters per (phase, bowling_type) combination
4. Compare to league-wide aggregates from the same view
5. Identify the 3-5 most extreme differentials (positive and negative)

**Data Sources:** `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_batter_vs_bowler_type_phase_since2023`, league benchmarks from `analytics_ipl_batting_benchmarks_since2023`.

---

#### Section 9: Innings Context: Setting vs Chasing

**Purpose:** The most data-intensive section. Reveals how the team differs between first and second innings across batting, bowling, and individual player splits, plus a detailed chase approach analysis.

**Must Include (8 sub-sections):**

**9a. The Big Picture**

| Scenario | Matches | Wins | Win % |

2 rows: Batting first (setting), Batting second (chasing). Include a sample-size caveat note.

**9b. Team Batting: Two Different Gears**

| Phase | Setting SR | Chasing SR | Delta | League Chase SR | Team vs League |

4 rows: Powerplay, Middle, Death, Overall.

**9c. Team Bowling: Better With Something to Defend (or not)**

| Phase | Bowl First Econ | Defend Econ | Delta | Defend Dot% | Defend Wkt Rate |

4 rows: Powerplay, Middle, Death, Overall.

**9d. Individual Player Splits: Batters**

| Player | Setting SR | Chasing SR | Delta | Sample (Balls) |

Include all predicted XII batters (top 6 typically). Mark confidence labels in the Sample column.

**9e. Individual Player Splits: Bowlers**

| Bowler | Bowl First Econ | Defend Econ | Delta | Sample (Overs) |

Include all frontline bowlers (4-5 typically).

**9f. Chase Results by Target Band**

| Target Band | Chases | Wins | Win% | League Win% | Team vs League |

Standard bands: <=140, 141-160, 161-180, 181-200, 200+. Identify the cliff point.

**9g. How the Approach Changes by Target Size**

| Target Band | PP RPO | PP Wkts/Match | Mid RPO | Mid Wkts/Match | Death RPO | Death Wkts/Match |

3 rows: <=160, 161-180, 180+. Identify distinct chase modes.

**9h. The Collapse Zone**

| Phase | 3+ Wkt Collapses | Total Chase Innings | Collapse Rate | Lost After Collapse |

3 rows: Powerplay, Middle, Death. A collapse = 3+ wickets in a single phase during a chase.

**9i. Early Wickets**

| PP Wickets Lost | Chases | Wins | Win% |

4 rows: 0, 1, 2, 3. Identify the optimal chase profile.

**9j. Who Scales and Who Doesn't**

| Batter | SR (<=160) | SR (161-180) | SR (180+) | Scales? |

Include top 3 batters. "Scales?" column answers whether the batter increases SR as targets increase.

**9k. Year-over-Year Chase Evolution**

Brief paragraph showing chase win % trend by year (e.g., 2023: X%, 2024: Y%, 2025: Z%).

**9l. What This Means for 2026**

2-3 paragraph synthesis. Should the team chase or set? What is the specific target threshold? What is the operational priority for preparation?

**Data Sources:** `analytics_ipl_team_batting_by_innings_since2023`, `analytics_ipl_team_bowling_by_innings_since2023`, `analytics_ipl_player_batting_by_innings_since2023`, `analytics_ipl_player_bowling_by_innings_since2023`, match result data from `dim_match`.

**How to Compute Chase Approach Analysis:**
1. Query match-level results filtered by team and innings = 2 (chasing)
2. Categorize targets into bands: <=140, 141-160, 161-180, 181-200, 200+
3. Compute win% per band, compare to league-wide chase win% per band
4. For phase-by-target: join ball-by-ball data with match targets, aggregate SR and wickets per phase per target band
5. Collapse zones: count innings where 3+ wickets fell in a single phase during a chase, then compute loss rate after collapse

---

#### Section 10: Venue Analysis

**Purpose:** Home ground profile and how the team's strengths interact with venue characteristics.

**Must Include:**

**Table 1: Venue Phase Profile**

| Phase | Run Rate | Boundary % | Dot Ball % | Wkts/Match |

3 rows: Powerplay, Middle, Death.

**Table 2: vs. League Averages**

| Phase | Venue RR | League RR | Delta |

3 rows: Powerplay, Middle, Death.

Followed by analysis of how the team's strengths/weaknesses interact with the venue. Include at least one surprising finding (e.g., Chinnaswamy is not actually a powerplay paradise).

**Data Sources:** `analytics_ipl_venue_profile_since2023`, `analytics_ipl_venue_profile_alltime`, `dim_venue`, cross-referenced with team phase data.

---

#### Section 11: Schedule Analysis

**Purpose:** Placeholder until IPL 2026 schedule releases.

**Format:**
```markdown
## Schedule Analysis

**Status: IPL 2026 schedule has not been released.**

When the schedule drops, this section will cover:
- **Home/away split:** ...
- **Cluster analysis:** ...
- **Rest days:** ...
- **Travel burden:** ...
- **Early vs. late difficulty:** ...

*This section will be populated upon schedule release. Placeholder retained per editorial plan.*
```

---

#### Section 12: Head-to-Head Record

**Purpose:** Team's record against all 9 opponents, both since 2023 and all-time.

**Must Include:**

**Table 1: Since 2023**

| Opponent | W-L | Win % | Key Pattern |

9 rows (one per opponent). Ordered by Win% descending. Key Pattern column: one-sentence tactical insight.

**Table 2: All-Time IPL**

| Opponent | W-L | Win % | Since-2023 W-L | Trend |

9 rows. Ordered by Win% descending. Trend column: one-sentence directional observation.

Summary lines: `**Since 2023: {W}-{L} ({win%} win rate)**` and `**All-Time: {W}-{L} ({win%} win rate)**`

Follow with 2-3 paragraphs analyzing the most significant matchup stories (best matchup, worst matchup, one that has meaningfully shifted).

**Data Sources:** `dim_match` joined with team results, filtered by IPL matches. Head-to-head computed by aggregating wins/losses per opponent.

---

#### Section 13: Players to Watch

**Purpose:** 3-4 individual spotlight profiles for the most compelling storylines.

**Format:** Each player gets a subheading ("`### {Name}: {Descriptive Title}`") and one paragraph (100-150 words).

**Per-Player Must Include:**
- Key stat with sample size and confidence label on the opening line
- The specific storyline: why this player matters for 2026
- At least one bowling-type matchup stat
- One concern or flag
- Mix of disciplines: at least 1 batter, 1 bowler, 1 all-rounder/keeper

**Contextual Accuracy Rule:** If a stat appears surprising, explain the operational context. (Example: Kohli's death-overs SR comes from batting through, not entering at the death.)

**Data Sources:** `analytics_ipl_batting_career_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_bowling_career_since2023`, `analytics_ipl_bowler_phase_since2023`, `analytics_ipl_batter_recent_form`.

---

#### Section 14: Players Who Need to Step Up

**Purpose:** Identify 2-3 structural weaknesses and the specific players who can address them.

**Format:** Each player gets a numbered subheading and one paragraph (80-120 words).

**Per-Player Must Include:**
- The structural weakness they can address (reference depth chart rating if applicable)
- Their price and retention status
- Key stat (with confidence label) showing potential
- One flag or developmental concern
- What it means for the team if they deliver (and if they don't)

**Framing:** Opportunity, not criticism. "If X can do Y, the team gains Z."

**Data Sources:** Depth chart ratings, `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_bowler_phase_since2023`, `analytics_ipl_batter_recent_form`.

---

#### Section 15: Recent Form

**Purpose:** Last-10-innings performance for batters and phase economies for bowlers.

**Table 1: Batters (IPL Recent Form)**

| Player | Last 10 Inn | L10 Runs | L10 SR | Since-2023 SR | SR Delta | Trend |

Include all predicted XII batters. Trend column: descriptive label (e.g., "Steep decline", "Stable-elite", "Career-best form").

**Table 2: Bowlers (Individual Phase Economies, Since 2023)**

| Player | Primary Phase | Econ (Primary) | Secondary Phase | Econ (Secondary) | Role |

Include all frontline bowlers. Economy values include sample size and confidence label in parentheses.

Follow with 1-2 paragraphs interpreting the form picture. Identify the biggest positive swing, the biggest concern, and any small-sample caveats.

**Data Sources:** `analytics_ipl_batter_recent_form`, `analytics_ipl_bowler_phase_since2023`, `analytics_ipl_bowler_recent_form`.

---

#### Section 16: Interesting Data Insights

**Purpose:** 3-5 non-obvious findings from the 164+ analytics views.

**Format:** Each insight gets a numbered subheading (descriptive title) and one paragraph (80-120 words).

**Requirements:**
- Each insight: stat + context + so-what
- Must satisfy the Phil Steele Rule (something the reader didn't know)
- Types: unusual matchup data, phase contradictions, hidden strengths, surprising vulnerabilities
- Every stat must include sample size and confidence label
- Contextual Accuracy Rule applies: if a stat seems surprising, explain why

**Data Sources:** All analytics views, particularly: `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_bowler_phase_since2023`, `analytics_ipl_batter_venue_since2023`, composite rankings, pressure bands.

---

#### Section 17: The Bold Take

**Purpose:** One genuinely contrarian opinion supported by evidence.

**Format:**
```markdown
## The Bold Take

**{Bold claim in bold.}**

{2-3 paragraphs of supporting argument with data citations.}
```

**Rules:**
- Must be genuinely contrarian (something most fans would disagree with)
- Must be supported by at least 2 data points from our analytics
- Should reframe how the reader thinks about the team
- Contextual Accuracy Rule applies
- No hedging. State the claim. Back it up. End definitively.

---

#### Section 18: By the Numbers

**Purpose:** Five stats that tell the season story.

**Table Format:**

| Stat | Value | Context |

**Rules:**
- Exactly 5 stats. No more, no less.
- Mix of team-level and player-level
- Each context line is one sentence explaining the significance
- Include confidence labels where applicable

---

#### Section 19: Keys to Victory

**Purpose:** 3-4 specific conditions that must be met for the team to contend.

**Format:** Each key gets a numbered bold subheading and one paragraph (80-120 words).

**Must Cover:**
- At least one player health/availability condition
- At least one tactical/performance threshold
- At least one structural vulnerability that must be managed
- At least one overseas slot or squad management consideration (where relevant)

**Data Sources:** Squad structure, phase data, depth chart, historical team performance.

---

#### Section 20: Andy Flower's Scouting Report

**Purpose:** Tactical overview written from a cricket coaching perspective.

**Structure (use bold labels):**
- **Tactical Identity:** One sentence defining how this team wins
- **Structural Strengths:** Bullet list (3-5 items), each with a specific stat
- **Structural Vulnerabilities:** Bullet list (4-6 items), each with a specific stat or depth chart rating
- **Opposition Blueprint:** One paragraph describing how to beat this team, with specific tactical instructions
- **Matchup Targets:** One paragraph identifying specific player vulnerabilities opponents should exploit, with stats and confidence labels

---

#### Section 21: Verdict

**Format:**
```markdown
## Verdict

{1-3 sentences synthesizing the preview. Conditional framing: "If X, then Y. If not, Z."}

**Projected Finish: {range}** | **Ceiling: {best case}** | **Floor: {worst case}**
```

**Rules:**
- No hedging. Commit to a range.
- Ceiling and floor must be realistic (not "1st" and "10th" for every team)
- The conditional framing should reference the 2-3 key variables identified throughout the preview

### A.4 Document Footer

```markdown
---

*Cricket Playbook v5.0.0 | Data: Cricsheet ({match_count} matches) | Analytics: 164+ views*
*Every claim above is backed by data. No vibes. No predictions. Just evidence.*
```

---

## B. Tone & Style Guide

### B.1 The Phil Steele Rule (Non-Negotiable)

Every section must teach the reader something they didn't know how to ask about yet. If a paragraph could appear in any generic cricket preview, it doesn't belong in Cricket Playbook.

This is a hard requirement inherited from the Constitution (Section 1.3). Content that fails this test is rejected at editorial review.

### B.2 Voice Calibration

| Attribute | Do This | Not This |
|-----------|---------|----------|
| Authority | "Bhuvneshwar's economy is elite" | "Bhuvneshwar's economy could be considered quite good" |
| Specificity | "8.26 powerplay economy across 99 overs" | "strong bowling" |
| Humor | "Krunal's 7.45 exists in its own postcode" | "Krunal is a pressure cooker on legs" |
| Emphasis | "This is no longer a competitive fixture" | "PBKS have become RCB's personal stress-relief exercise" |
| Surprise | "The only bowling type where RCB underperform" | "Let that sink in" |

### B.3 Writing Rules

1. **Dry and witty.** A senior analyst who happens to be funny, not a comedian trying to analyze cricket.
2. **Professional but engaging.** Authority first, personality second.
3. **Confident, not hedging.** Make claims. Back them with data. Do not say "could potentially maybe."
4. **Specific, not vague.** Every claim has a number attached.
5. **Short sentences for emphasis** after longer analytical paragraphs. "Full stop." / "That's the point."
6. **Vary sentence length.** Mix analytical depth with punchy observations.
7. **Headers tell stories.** "Somebody Read the Memo" not "2025 Analysis."

### B.4 Quantitative Limits

| Element | Limit | Reference |
|---------|-------|-----------|
| Puns | Max 1-2 per 1000 words | `content_language_guide.md` |
| Food metaphors | Max 1 per 2000 words | `content_language_guide.md` |
| Analogies | Max 1 per paragraph | `content_language_guide.md` |
| Em dashes | Zero. Not permitted. | `content_language_guide.md` |
| Exclamation marks | Headlines only, never in body text | `content_language_guide.md` |
| Emoji in body text | Zero. Data tables only. | `content_language_guide.md` |

### B.5 Banned Language

- No internet-speak: "let that sink in", "I'll wait", "say it louder"
- No cliche metaphors: "heat-seeking missile", "pressure cooker", "ticking time bomb"
- No "breaking", "shocking", "stunning" for analytical findings
- No forced alliteration
- No "imagine" / "picture this" / "think about it" openings
- No stacking metaphors (one analogy per paragraph maximum)

### B.6 Confidence Labels (Mandatory)

Every statistical claim in the preview must include a confidence label based on sample size.

**Batting (measured in balls faced):**

| Label | Threshold | Usage |
|-------|-----------|-------|
| HIGH | 500+ balls | Full confidence. Present as established fact. |
| MEDIUM | 100-499 balls | Reasonable confidence. Present as reliable indicator. |
| LOW | <100 balls | Limited data. Must acknowledge explicitly. |

**Bowling (measured in overs bowled):**

| Label | Threshold | Usage |
|-------|-----------|-------|
| HIGH | 80+ overs | Full confidence. |
| MEDIUM | 30-79 overs | Reasonable confidence. |
| LOW | <30 overs | Limited data. Must acknowledge. |

**How to Handle Small Samples:**
- Always disclose the exact sample size (e.g., "45 balls", "12 overs")
- LOW samples: use language like "limited data but directional", "small sample deserves caution", "small-sample roulette rather than any real trend"
- Never hide a small sample. Never present a LOW stat as if it were HIGH.
- If a LOW stat supports a critical argument, state the caveat in the same sentence

**Reference:** These thresholds derive from `config/thresholds.yaml` and the ranking qualification thresholds therein.

### B.7 Statistical Formatting

- Numbers over 10: always numerals, never spelled out
- Strike rates: one decimal (e.g., 146.6)
- Economies: two decimals (e.g., 8.26)
- Percentages: one decimal with % sign (e.g., 47.5%)
- Prices: X.XX Cr format (e.g., 11.50 Cr)
- Player first mention: include full context: "Virat Kohli (21.00 Cr, retained)"
- Cricket jargon assumed. Do not explain what a powerplay is.

### B.8 Contextual Accuracy Rule (Founder Directive)

Every insight must be contextually accurate. If a stat appears surprising, explain WHY it exists.

Example: Kohli's 183.3 death SR is real, but he entered in the powerplay in all 44 innings. His death numbers come from batting through (15/44 innings), not from entering as a pinch-hitter. Both approaches are valuable. They are not the same skill.

Never present a number without its operational context.

---

## C. Data Requirements

### C.1 Primary DuckDB Views Per Section

| Section | Required Views | Scope |
|---------|---------------|-------|
| The Headline | Depth chart, composite rankings | _since2023 |
| The Story | `ipl_2026_contracts`, `ipl_2026_squads`, team phase data | _since2023 |
| Off-Season Changes | `ipl_2026_contracts`, `founder_squads_2026.json` | N/A |
| New Additions | `ipl_2026_contracts`, `analytics_ipl_batting_career_since2023`, `analytics_ipl_bowling_career_since2023` | _since2023 |
| Full Squad Table | `ipl_2026_squads`, `ipl_2026_contracts`, `analytics_ipl_batting_career_since2023`, `analytics_ipl_bowling_career_since2023` | _since2023 |
| Team Style Analysis | `analytics_ipl_team_phase_batting_since2023`, `analytics_ipl_team_phase_bowling_since2023` | Both (filter by season) |
| Category Ratings | `analytics_ipl_team_phase_batting_since2023`, `analytics_ipl_team_phase_bowling_since2023`, depth chart | _since2023 |
| Team Batting Profile | `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_batter_vs_bowler_type_phase_since2023`, `analytics_ipl_batting_benchmarks_since2023` | _since2023 |
| Innings Context | `analytics_ipl_team_batting_by_innings_since2023`, `analytics_ipl_team_bowling_by_innings_since2023`, `analytics_ipl_player_batting_by_innings_since2023`, `analytics_ipl_player_bowling_by_innings_since2023` | _since2023 |
| Venue Analysis | `analytics_ipl_venue_profile_since2023`, `analytics_ipl_venue_profile_alltime`, `dim_venue` | Both |
| Head-to-Head | `dim_match`, team results | Both |
| Players to Watch | `analytics_ipl_batting_career_since2023`, `analytics_ipl_batter_phase_since2023`, `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_bowler_phase_since2023` | _since2023 |
| Players Who Need to Step Up | Depth chart ratings, `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_batter_phase_since2023` | _since2023 |
| Recent Form | `analytics_ipl_batter_recent_form`, `analytics_ipl_bowler_phase_since2023`, `analytics_ipl_bowler_recent_form` | _since2023 |
| Interesting Data Insights | All 164+ views (mined per team) | Both |
| The Bold Take | Composite rankings, matchup data | _since2023 |
| By the Numbers | Cross-referenced from all sources | _since2023 |
| Keys to Victory | Squad structure, phase data, depth chart | _since2023 |
| Scouting Report | Tactical insights, opposition data, matchup rankings | _since2023 |
| Verdict | Composite rankings, depth chart | _since2023 |

### C.2 Dual-Scope Convention

The analytics layer creates views in two scopes:
- `_alltime`: Full IPL history (all available seasons)
- `_since2023`: IPL 2023, 2024, 2025 only (recency-weighted for current relevance)

**Default scope for season previews: `_since2023`** unless explicitly noted otherwise.

Use `_alltime` only for:
- Head-to-head all-time records
- Venue historical context
- Career milestones or all-time rankings
- When contrasting current form against historical baseline

When both scopes appear in the same section, label them clearly (e.g., "Since 2023" vs "All-Time IPL (2008-2025)").

### C.3 Required Sample Size Thresholds

Reference: `config/thresholds.yaml`

| Context | Minimum for Inclusion | Source |
|---------|----------------------|--------|
| Batter career inclusion | 300 balls | `thresholds.yaml > sample_size > min_balls_batter` |
| Bowler career inclusion | 200 balls | `thresholds.yaml > sample_size > min_balls_bowler` |
| Batter vs bowling type | 50 balls per type | `thresholds.yaml > sample_size > min_balls_vs_type` |
| Individual bowling type tag | 20 balls | `thresholds.yaml > sample_size > min_balls_per_type` |
| Phase analysis (overs bowled) | PP: 30 / Mid: 50 / Death: 30 | `thresholds.yaml > sample_size` |
| Ranking qualification (batter) | 500 balls | `thresholds.yaml > rankings > qualification > min_balls_batter` |
| Ranking qualification (bowler) | 300 balls | `thresholds.yaml > rankings > qualification > min_balls_bowler` |
| Ranking phase-specific | 100 balls | `thresholds.yaml > rankings > qualification > min_balls_phase` |

Players below minimum thresholds may still appear in previews (especially new signings), but must be flagged with LOW confidence labels and explicit sample size disclosure.

### C.4 How to Derive Phase x Bowling Type Cross-References

This is the most analytically complex section in the preview. Follow this procedure:

1. **Query:** `analytics_ipl_batter_vs_bowler_type_phase_since2023`
2. **Filter:** Join with `ipl_2026_squads` to get only the team's current batters
3. **Aggregate:** For each (match_phase, bowling_type) combination, sum runs and balls across all team batters. Compute team SR = (total_runs / total_balls) * 100.
4. **Benchmark:** Compute the same aggregation across ALL batters in the league for the same (phase, bowling_type) combinations.
5. **Differential:** Team SR minus League SR per combination.
6. **Select:** Pick the 3-5 combinations with the most extreme differentials (both positive and negative), plus any that tell a compelling tactical story.
7. **Confidence:** Assign confidence labels based on total balls in each combination.

### C.5 How to Compute Chase Approach Analysis

The Innings Context section requires several derived datasets:

**Target Band Analysis:**
1. Query `dim_match` for all matches where the team batted second (chasing)
2. Extract the target (first innings total + 1)
3. Categorize into bands: <=140, 141-160, 161-180, 181-200, 200+
4. Compute win% per band
5. Compare to league-wide chase win% per band (all teams, same time window)

**Phase-by-Target Analysis:**
1. Join ball-by-ball data (`fact_ball`) with match targets
2. Categorize each chase into target bands
3. Aggregate per (target_band, match_phase): compute run rate and wickets per match
4. Present as SR values (run rate * 100 / 6 is approximate; use actual balls-based SR)

**Collapse Zone Analysis:**
1. For each chase innings, count wickets fallen per phase
2. A "collapse" = 3+ wickets falling in a single phase
3. Compute: collapse_rate = collapses / total_chase_innings
4. Compute: loss_after_collapse = losses_when_collapsed / collapses

**Who Scales Analysis:**
1. For each top-order batter, compute their SR in chases categorized by target band
2. A batter "scales" if their SR increases as the target band increases
3. Present the SR progression across bands

---

## D. The Lab Integration Spec

### D.1 Data File Location

`scripts/the_lab/dashboard/data/season_previews.js`

### D.2 Top-Level Structure

```javascript
const SEASON_PREVIEWS = {
  {TEAM_ABBR}: {
    available: true,
    meta: { ... },
    headline: { ... },
    verdict: { ... },
    byTheNumbers: [ ... ],
    categoryRatings: [ ... ],
    boldTake: { ... },
    keysToVictory: [ ... ],
    scoutingReport: { ... },
    sections: [ ... ]
  },
  // ... remaining teams
};
```

### D.3 Required Fields Per Team

**`meta` Object:**
```javascript
meta: {
  revision: 'v{X.Y}',                    // String
  dataWindow: 'IPL 2023-2025 | {matches} matches / {balls} balls',  // String
  agents: 'Virat Kohli (Tone & Narrative) | Andy Flower (Scouting Report)',  // String
  matches: '{match_count}'                // String
}
```

**`headline` Object:**
```javascript
headline: {
  title: '{Bold headline text}',          // String
  intro: '{Supporting paragraph text}'    // String
}
```

**`verdict` Object:**
```javascript
verdict: {
  text: '{Full verdict paragraph}',       // String
  projected: '{range}',                   // String, e.g., '3rd-4th'
  ceiling: '{best case}',                 // String, e.g., 'Champions'
  floor: '{worst case}'                   // String, e.g., '6th'
}
```

**`byTheNumbers` Array (5 items exactly):**
```javascript
byTheNumbers: [
  { value: '{stat}', label: '{description}', context: '{one-line explanation}' },
  // ... 4 more
]
```

**`categoryRatings` Array (7 items exactly):**
```javascript
categoryRatings: [
  { cat: '{category}', rating: {number}, metric: '{key metric}', note: '{context}' },
  // ... 6 more
]
```
Categories in order: Batting, Powerplay / Batting, Middle / Batting, Death / Bowling, Powerplay / Bowling, Middle / Bowling, Death / Overall.

**`boldTake` Object:**
```javascript
boldTake: {
  claim: '{Bold claim text}',             // String
  argument: '{Full supporting argument}'  // String (HTML entities escaped)
}
```

**`keysToVictory` Array (3-4 items):**
```javascript
keysToVictory: [
  { title: '{Key title}', text: '{Explanation paragraph}' },
  // ... 2-3 more
]
```

**`scoutingReport` Object:**
```javascript
scoutingReport: {
  identity: '{One sentence}',             // String
  strengths: ['{item}', ...],             // Array of strings (3-5 items)
  vulnerabilities: ['{item}', ...],       // Array of strings (4-6 items)
  oppositionBlueprint: '{Paragraph}',     // String
  matchupTargets: '{Paragraph}'           // String
}
```

### D.4 Sections Array: Block Types

The `sections` array contains section objects, each with `id`, `title`, `summary`, and `blocks`.

**Section Object:**
```javascript
{
  id: '{camelCase section ID}',           // String
  title: '{Section Title}',              // String
  summary: '{One-sentence summary}',     // String (used for navigation/preview)
  blocks: [ ... ]                        // Array of block objects
}
```

**Block Types:**

| Type | Properties | Usage |
|------|-----------|-------|
| `text` | `content` (HTML string) | Paragraph text. Use `<p>`, `<em>`, `<strong>` tags. |
| `table` | `headers` (string array), `rows` (array of string arrays), `caption` (optional string) | Data tables. |
| `subheading` | `content` (string) | Section sub-headers within a section. |
| `callout` | `content` (string) | Highlighted insight or key takeaway. |

**Section ID Mapping:**

| Section | ID |
|---------|-----|
| The Story | `story` |
| Off-Season Changes | `offseason` |
| New Additions | `newAdditions` |
| Full Squad | `squad` |
| Team Style Analysis | `teamStyle` |
| Team Batting Profile | `battingProfile` |
| Innings Context | `inningsContext` |
| Venue Analysis | `venue` |
| Schedule Analysis | `schedule` |
| Head-to-Head Record | `headToHead` |
| Players to Watch | `playersToWatch` |
| Players Who Need to Step Up | `playersStepUp` |
| Recent Form | `recentForm` |
| Interesting Data Insights | `dataInsights` |

**Note:** The Headline, Category Ratings, Bold Take, By the Numbers, Keys to Victory, Scouting Report, and Verdict are stored as top-level fields (not in the sections array) because they have dedicated rendering components in the Lab.

### D.5 HTML Escaping Rules

- Single quotes in content strings must be escaped: `\'`
- Use HTML entities for special characters within `content` fields
- Use `<em>` for italics, `<strong>` for bold
- Use `<br>` for line breaks within a single text block (sparingly)
- Unicode characters (e.g., <=) should use Unicode escapes: `\u2264`

### D.6 Teams Not Yet Available

For teams whose preview has not been produced:
```javascript
{TEAM_ABBR}: { available: false }
```

Team abbreviations: RCB, MI, CSK, KKR, DC, PBKS, RR, SRH, GT, LSG.

---

## E. Quality Gates

### E.1 Jose Mourinho Scoring Rubric (10-Point System)

Every preview is scored before publication. Minimum threshold to ship: **8.5/10.**

| Criterion | Weight | What It Measures |
|-----------|--------|-----------------|
| 1. Statistical Accuracy | 1.5 | All numbers traceable to specific views/queries. No rounding errors. |
| 2. Sample Size Disclosure | 1.0 | Every stat includes ball count/over count and confidence label. |
| 3. Contextual Accuracy | 1.5 | No stats presented without operational context. Surprising numbers explained. |
| 4. Phil Steele Rule Compliance | 1.0 | Every section teaches something new. No generic content. |
| 5. Tone Compliance | 1.0 | Matches `content_language_guide.md`. No em dashes, no internet-speak, pun limits respected. |
| 6. Structural Completeness | 1.0 | All sections present. All required tables included. Word counts within targets. |
| 7. Analytical Depth | 1.0 | Phase x Bowling Type cross-references present. Chase approach analysis complete. Innings splits computed. |
| 8. Bold Take Quality | 0.5 | Genuinely contrarian. Supported by 2+ data points. |
| 9. Scouting Report Precision | 0.5 | Actionable tactical intel. Specific matchup vulnerabilities. Would pass Andy Flower's scrutiny. |
| 10. Lab Integration Readiness | 1.0 | JS data structure complete and correctly formatted. All block types populated. |

**Scoring:**
- 9.0+: Publish-ready
- 8.5-8.9: Publish with minor revisions noted
- 7.0-8.4: Requires revision cycle. Do not publish.
- Below 7.0: Requires rewrite. Escalate to Tom Brady.

### E.2 Andy Flower Domain Sanity Checks

Andy Flower reviews every preview for cricket accuracy before publication.

**Checklist:**
- [ ] Tactical identity description matches actual on-field approach
- [ ] Player roles are correctly assigned (e.g., is this player actually a death bowler?)
- [ ] Phase allocations for bowlers reflect how they are actually used (not assumed)
- [ ] Opposition blueprint is tactically viable (not just "exploit their weakness")
- [ ] Matchup targets are based on genuine vulnerabilities, not statistical noise
- [ ] No cricket inaccuracies in narrative sections (e.g., confusing batting positions, wrong bowling styles)
- [ ] Captaincy and team management context is factually correct
- [ ] Scouting report would be credible if handed to an actual IPL coaching staff

### E.3 N'Golo Kante QA Checks

Kante performs the final statistical integrity pass.

**Checklist:**
- [ ] **Rounding:** All SRs rounded to one decimal. All economies to two decimals. All percentages to one decimal.
- [ ] **Sample sizes:** Every stat cites exact sample (balls for batting, overs for bowling)
- [ ] **Confidence labels:** Every stat has HIGH/MEDIUM/LOW label. Labels match the thresholds defined in Section B.6.
- [ ] **Consistency:** Same player's stat cited in multiple sections uses the same number everywhere
- [ ] **Table arithmetic:** Win-Loss records sum correctly. Win percentages match W/(W+L). Deltas are correctly computed.
- [ ] **Squad totals:** Total squad salary matches sum of individual prices. Overseas count is correct.
- [ ] **Cross-team consistency:** If RCB's H2H vs KKR says 1-4, then KKR's H2H vs RCB must say 4-1.
- [ ] **Data window disclaimer:** Header correctly states the data window.
- [ ] **No orphan stats:** Every number in the text can be traced to a table or a specific analytics view.

### E.4 Minimum Score Threshold

**8.5/10 is required to ship.** Previews scoring below 8.5 enter a revision loop:

1. Jose Mourinho identifies specific deficiencies with point deductions
2. Virat Kohli (or assigned writer) revises the flagged sections
3. Re-scored by Jose Mourinho
4. If still below 8.5, escalate to Tom Brady for editorial intervention
5. Maximum 2 revision cycles before Florentino Perez kill-switch review

---

## F. Production Checklist

### F.1 Step-by-Step Process to Produce a Preview

| Step | Action | Owner | Deliverable | Gate |
|------|--------|-------|-------------|------|
| 1 | Run data extraction queries for the team | Stephen Curry | Raw data tables per section | Data completeness check |
| 2 | Generate team stat pack (if not current) | Brock Purdy | Updated stat pack in `stat_packs/` | Pipeline validation |
| 3 | Draft full preview (all 21 sections) | Virat Kohli | Draft markdown file | Phil Steele Rule self-check |
| 4 | Domain sanity review | Andy Flower | Annotated draft with corrections | Andy Flower sign-off |
| 5 | Quant validation | Jose Mourinho | Scored rubric (must achieve 8.5+) | Score threshold |
| 6 | Tone review | Virat Kohli | Final tone pass against `content_language_guide.md` | Tone compliance |
| 7 | Statistical QA | N'Golo Kante | QA checklist completed | All checks pass |
| 8 | Lab integration | Kevin De Bruyne | JS data structure added to `season_previews.js` | Structure validation |
| 9 | Tom Brady editorial sign-off | Tom Brady | Final approval | Publish gate |
| 10 | Founder review (if required) | Founder | Approval or feedback | Final gate |

### F.2 Agent Assignments

| Role | Agent | Responsibility |
|------|-------|---------------|
| Primary Writer | Virat Kohli | Draft all narrative sections, tone compliance, revision cycles |
| Domain Reviewer | Andy Flower | Scouting report accuracy, tactical identity, cricket truth |
| Data Extraction | Stephen Curry | Query DuckDB views, prepare raw data tables per section |
| Pipeline Owner | Brock Purdy | Ensure stat packs and data are current |
| Quant Scorer | Jose Mourinho | Score rubric, identify statistical deficiencies |
| QA Enforcer | N'Golo Kante | Rounding, sample sizes, confidence labels, cross-team consistency |
| Lab Integration | Kevin De Bruyne | Convert markdown to JS data structure |
| Editor-in-Chief | Tom Brady | Editorial consistency across all 10 previews, final approval |
| Program Director | Florentino Perez | Kill-switch authority if revision cycles exceed threshold |

### F.3 Review Loop

```
Virat Kohli (Draft)
    |
    v
Andy Flower (Domain) --[corrections]--> Virat Kohli (Revise)
    |
    v
Jose Mourinho (Score) --[below 8.5]--> Virat Kohli (Revise) --> Jose Mourinho (Re-score)
    |                                                              |
    v [8.5+]                                              [still below 8.5]
    |                                                              |
N'Golo Kante (QA)                                     Tom Brady (Intervention)
    |
    v
Tom Brady (Final Sign-off)
    |
    v
Kevin De Bruyne (Lab Integration)
    |
    v
Founder Review (if flagged)
```

### F.4 Team Production Order

Per editorial plan, ordered by narrative richness:

| Order | Team | Status | Key Narrative |
|-------|------|--------|---------------|
| 1 | RCB | COMPLETE (sample approved) | Title defence, bowling-first revolution |
| 2 | CSK | Pending | Legacy franchise, Dhoni transition |
| 3 | MI | Pending | Rebuild season |
| 4 | KKR | Pending | Defending champions (note: verify current status) |
| 5 | RR | Pending | Analytical franchise |
| 6 | DC | Pending | Pant return narrative |
| 7 | SRH | Pending | Aggressive identity |
| 8 | PBKS | Pending | Perpetual rebuild |
| 9 | GT | Pending | Post-Hardik era |
| 10 | LSG | Pending | Stability play |

### F.5 File Naming Convention

- Individual preview: `outputs/season_previews/{TEAM}_season_preview.md` (e.g., `RCB_season_preview.md`)
- Sample/draft: `outputs/season_previews/{TEAM}_season_preview_sample.md`
- Combined: `outputs/season_previews/IPL_2026_season_preview_complete.md`
- Lab data: `scripts/the_lab/dashboard/data/season_previews.js`

### F.6 Conflict Resolution

- If Virat Kohli and Andy Flower disagree on a claim, the data decides.
- If data is ambiguous, both perspectives are presented.
- Founder has final call on tone disputes.
- Tom Brady has final call on structural/editorial disputes.
- Florentino Perez has kill-switch authority if a preview cannot reach 8.5 after 2 revision cycles.

---

## G. Reference Documents

| Document | Path | Purpose |
|----------|------|---------|
| Content Language Guide | `config/content_language_guide.md` | Tone rules, banned language, quantitative limits |
| Thresholds | `config/thresholds.yaml` | Sample size thresholds, ranking qualifications |
| Constitution | `config/CONSTITUTION.md` | Binding governance, Phil Steele Rule origin |
| Editorial Plan | `outputs/season_previews/editorial_plan_v1.md` | Original section breakdown and production timeline |
| RCB Sample | `outputs/season_previews/RCB_season_preview_sample.md` | Approved reference implementation |
| Lab Data | `scripts/the_lab/dashboard/data/season_previews.js` | JS integration reference |
| Task Integrity Loop | `governance/TASK_INTEGRITY_LOOP.md` | 8-step process for all work |

---

## H. Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-02-14 | Virat Kohli, Tom Brady | Initial production template based on approved RCB sample |

---

*Cricket Playbook Season Preview Template v1.0.0*
*This is an internal production manual. Not for public distribution.*
