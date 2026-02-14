# Season Preview — Editorial Plan v1.1

**Cricket Playbook | IPL 2026 Season Preview Series**
*Agent: Virat Kohli (Tone & Narrative Guard)*
*Status: Updated per Founder Review (12 Suggestions Incorporated)*
*Revision Date: 2026-02-14*

---

## 1. Format Per Team

Each team preview follows a **17-section structure** inspired by Lindy's Football Annual and Phil Steele's College Football Preview. The Founder's 12 suggestions have been integrated as dedicated sections, replacing the original 7-section format.

| # | Section | Length | Purpose | Data Sources |
|---|---------|--------|---------|-------------|
| 1 | **The Headline** | 1-2 sentences | Bold thesis — the single most important storyline | Depth chart + tactical insights |
| 2 | **The Story** | 400-500 words | Narrative: what changed, who's new, what to watch | Squad composition + recent form |
| 3 | **Off-Season Changes** | 200-300 words | Trades, coaching changes, captaincy, what's different from 2025 | `ipl_2026_contracts`, `founder_squads_2026.json`, public reporting |
| 4 | **New Additions** | 150-250 words | Each new signing: who they replace, what gap they fill, style fit | `ipl_2026_contracts` (acquisition_type='Auction'), batting/bowling career views |
| 5 | **Full Squad Table** | Table | Entire squad with Name, Role, Price, Nationality, Key Stat, Founder Notes | `ipl_2026_squads`, `ipl_2026_contracts`, batting/bowling career views |
| 6 | **Team Style Analysis** | 300-400 words | How the franchise manages on/off the field — evolution over last 3 IPL seasons | `team_phase_batting_since2023`, `team_phase_bowling_since2023` by season |
| 7 | **Category Ratings** | Table + 150 words | Batting, Bowling, Fielding, Overall ratings with quantified breakdown | Phase batting/bowling aggregates, depth chart ratings, composite rankings |
| 8 | **Venue Analysis** | 200-300 words | Home ground profile, historical data, how team strengths interact with venue | `venue_profile_since2023`, cross-referenced with team phase data |
| 9 | **Schedule Analysis** | Placeholder (100 words) | Home/away split, cluster analysis, rest days — populated when schedule releases | TBD — schedule not yet released |
| 10 | **Players to Watch** | 3-4 profiles, ~100 words each | Data-backed individual storylines | Career stats + phase analysis + recent form |
| 11 | **Players Who Need to Step Up** | 200-300 words | Identify weaknesses and which players can address them | Depth chart gaps, phase stats, bowling type matchups |
| 12 | **Recent Form** | Table + 150 words | Last 10/20 innings performance, format crossover where relevant | `batter_recent_form`, `bowler_phase_since2023` |
| 13 | **Interesting Data Insights** | 3-5 insights, ~250 words | Non-obvious findings from 164+ analytics views | All analytics views — mined per team |
| 14 | **The Bold Take** | 150-200 words | One contrarian opinion supported by evidence | Percentile rankings + matchup data |
| 15 | **By the Numbers** | 5 key stats | The numbers that tell the season story | Cross-referenced from all sources |
| 16 | **Keys to Victory** | 200-300 words | What must go right, what weaknesses will surface, historical patterns | Squad structure analysis, phase data, depth chart |
| 17 | **Andy Flower's Scouting Report** | 200-300 words | Tactical overview: identity, strengths, vulnerabilities, opposition blueprint | Tactical insights + opposition data |
| 18 | **Verdict** | 1-3 sentences | Projected finish range, ceiling/floor | Composite rankings + depth chart |

**Total per team:** ~3,000-4,000 words
**Total series:** ~30,000-40,000 words across 10 teams

---

## 2. Tone Guidelines

### The Phil Steele Rule
Every section must teach the reader something they didn't know. If a paragraph could appear in any generic cricket preview, it doesn't belong here.

### Voice
- **Sharp, not flashy.** Write with authority, not hype.
- **Restrained, not cold.** Passion is allowed; breathlessness is not.
- **Credible, not hedging.** Make claims. Back them with data. Don't say "could potentially maybe."
- **Specific, not vague.** "Bhuvneshwar's 8.26 powerplay economy" not "strong bowling."

### Contextual Accuracy Rule (Founder Directive)
Every insight must be contextually accurate. If a stat appears surprising, explain WHY it exists. Example: if an opener has death-overs stats, clarify whether he bats through or enters at the death. Never present a number without its operational context.

### What We Are Not
- Not a prediction site. No "we guarantee top 4."
- Not a betting guide. No odds, no implied wagering.
- Not a hot-take factory. Every bold claim has a data citation.
- Not a fan blog. Equal rigor for every franchise.

### Language Standards
- No exclamation marks in analytical sections (allowed in headlines only)
- Numbers over 10 are always numerals (not spelled out)
- Player names include full context on first mention: "Virat Kohli (21.00 Cr, retained)"
- Cricket jargon is assumed — no explaining what a powerplay is
- Statistics always include sample size context (HIGH/MEDIUM/LOW or exact balls/innings)

---

## 3. Section Structure — Detailed

### Section 1: The Headline
- Must be a thesis, not a label. "RCB's Bowling-First Revolution" not "RCB Preview 2026"
- Should provoke thought — the reader should want to know *why*
- Draws from depth chart and tactical analysis

### Section 2: The Story
- Opens with the franchise's 2025 trajectory — where they ended, what it means
- Introduces the central strategic question for 2026
- Closes with what success and failure look like
- Keep focused on narrative; defer specifics to dedicated sections below

### Section 3: Off-Season Changes
*Founder Suggestion #4*
- Trades in and out (with prices and context)
- Coaching personnel changes
- Captaincy changes
- Key retentions and what they signal about franchise strategy
- What is structurally different from 2025?
- **Data source:** `ipl_2026_contracts` (compare `year_joined` and `acquisition_type`), `founder_squads_2026.json` notes

### Section 4: New Additions
*Founder Suggestion #3 — "Like in Lindy's, mention new additions"*
- Each new signing gets a mini-profile (2-4 sentences)
- For each: who they replace or what gap they fill, how they fit the team's playing style
- Include key stat from career views
- Separate auction buys from retained players who are new to the squad
- **Data source:** `ipl_2026_contracts` filtered by `year_joined = 2026`, batting/bowling career views

### Section 5: Full Squad Table
*Founder Suggestion #2*
- Show the ENTIRE squad, not just the predicted XI
- Columns: **Name | Role | Price (Cr) | Nationality | Key Stat | Founder Notes**
- "Founder Notes" column is intentionally blank — reserved for the Founder to annotate
- Key Stat should be the single most relevant number for that player's role (SR for batters, economy for bowlers, etc.)
- Order: predicted XI first (numbered 1-11/12), then bench players
- **Data source:** `ipl_2026_squads`, `ipl_2026_contracts`, `batting_career_since2023`, `bowling_career_since2023`

### Section 6: Team Style Analysis
*Founder Suggestion #11 — "Define the style each team takes up"*
- Analyze the franchise's identity across the last 3 IPL seasons (or 2 if data allows)
- Cover: batting approach (aggressive/conservative by phase), bowling philosophy (attack/contain), squad-building philosophy (allrounder-heavy, top-heavy, youth-focused, etc.)
- Show evolution: How has their style changed year-over-year?
- Use team phase batting/bowling data by season to quantify claims
- Address match-up beliefs, variety preferences, and on-field management patterns
- **Data source:** `team_phase_batting_since2023`, `team_phase_bowling_since2023` grouped by season

### Section 7: Category Ratings
*Founder Suggestion #7*
- Quantified ratings table:

| Category | Rating (1-10) | Key Metric | League Rank |
|----------|--------------|------------|-------------|
| Batting — Powerplay | X | Team PP SR | X/10 |
| Batting — Middle | X | Team Middle SR | X/10 |
| Batting — Death | X | Team Death SR | X/10 |
| Bowling — Powerplay | X | Team PP Economy | X/10 |
| Bowling — Middle | X | Team Middle Economy | X/10 |
| Bowling — Death | X | Team Death Economy | X/10 |
| **Overall** | X | Composite | X/10 |

- Derive ratings from team phase data, normalized against league averages
- Include 1-2 sentences explaining the ratings and any notable gaps
- **Data source:** `team_phase_batting_since2023`, `team_phase_bowling_since2023`, depth chart ratings

### Section 8: Venue Analysis
*Founder Suggestion #5 — "A bit about the venue and how the team will be approaching it"*
- Home ground characteristics: run rates by phase, boundary percentage, dot ball %, wickets per match
- Compare venue profile to league averages
- How do the team's strengths/weaknesses interact with venue conditions?
- Historical home record (if available)
- Tactical implications: what should the team emphasize at home?
- **Data source:** `venue_profile_since2023`, `dim_venue`, cross-referenced with team phase data

### Section 9: Schedule Analysis
*Founder Suggestion #6 — Placeholder until schedule is released*
- **Current state:** IPL 2026 schedule has not been released
- **When available, analyze:** Home/away split, clusters of tough opponents, rest days between games, travel burden, early-season vs late-season difficulty
- Placeholder text acknowledges this and states what will be covered
- **Data source:** TBD — schedule release

### Section 10: Players to Watch
- Each profile: name, price, one killer stat, the storyline
- Mix of stars, unsung heroes, and X-factors
- At least 1 player from each discipline (bat, bowl, all-round)
- Bold stat first, narrative second
- **Contextual accuracy rule applies:** every stat must be operationally explained

### Section 11: Players Who Need to Step Up
*Founder Suggestion #8*
- Identify the team's 2-3 biggest structural weaknesses
- For each weakness, name the specific player(s) who have the profile to address it
- Use depth chart gaps, phase stats, and bowling type matchup data
- Frame as opportunity, not criticism — "If X can do Y, the team gains Z"
- **Data source:** Depth chart ratings, phase stats, `batter_vs_bowler_type`, bowling career data

### Section 12: Recent Form
*Founder Suggestion #10 — "Overall and across different formats too if needed"*
- Table showing last 10 and last 20 IPL innings for key batters
- Include SR delta (current form vs career) to flag who's trending up/down
- For bowlers: recent phase economy trends
- Cross-format context where relevant (e.g., T20 World Cup, domestic T20s)
- **Data source:** `batter_recent_form`, `bowler_phase_since2023`

### Section 13: Interesting Data Insights
*Founder Suggestion #9 — "Any interesting insights from our big barrage of views"*
- Mine the 164+ analytics views for 3-5 non-obvious findings about this team's players
- Types of insights: unusual matchup data, phase contradictions, hidden strengths, surprising vulnerabilities
- Each insight: stat + context + so-what (2-3 sentences)
- These should make the reader say "I didn't know that"
- **Data source:** All analytics views — `batter_vs_bowler_type`, `batter_phase`, `bowler_phase`, `batter_venue`, composite rankings, pressure bands, etc.

### Section 14: The Bold Take
- Must be genuinely contrarian — something most fans would disagree with
- Must be supported by at least 2 data points from our analytics
- Should reframe how the reader thinks about the team
- **Contextual accuracy rule applies**

### Section 15: By the Numbers
- 5 stats exactly. No more, no less.
- Each stat tells a story — not just a number, but what it means
- Format: stat | value | one-line context
- Mix of team-level and player-level stats

### Section 16: Keys to Victory
*Founder Suggestion #12 — "What must go right for each team to win"*
- 3-4 specific conditions that must be met for the team to contend
- Include analysis of squad structure risks (youth vs experience balance, overseas slot constraints)
- Reference historical patterns (e.g., "RCB reached the 2025 final on bowling; that core returns intact")
- Address the weaknesses on paper that will be tested during the season
- **Data source:** Squad structure, phase data, depth chart, historical team performance

### Section 17: Andy Flower's Scouting Report
- Written in Andy Flower's voice: cricket-first, tactically precise
- Structure: Identity -> Strengths -> Vulnerabilities -> Opposition Blueprint
- Identifies specific matchup vulnerabilities
- Gives actionable scouting intel, as if preparing a coaching staff

### Section 18: Verdict
- One sentence: projected finish range
- Ceiling and floor in parentheses
- No hedging — commit to a range

---

## 4. Data Sources Per Section

| Section | Primary Views / Tables | Stat Pack Reference |
|---------|----------------------|-------------------|
| The Headline | Depth chart + tactical insights | Section 10 |
| The Story | Squad composition + recent form | Sections 1-3 |
| Off-Season Changes | `ipl_2026_contracts`, `founder_squads_2026.json` | N/A |
| New Additions | `ipl_2026_contracts`, batting/bowling career views | Sections 1-3 |
| Full Squad Table | `ipl_2026_squads`, `ipl_2026_contracts`, career views | All |
| Team Style Analysis | `team_phase_batting_since2023`, `team_phase_bowling_since2023` | Section 10 |
| Category Ratings | Team phase data, depth chart ratings | Sections 7-9 |
| Venue Analysis | `venue_profile_since2023`, `dim_venue` | Section 10 |
| Schedule Analysis | TBD (schedule not released) | N/A |
| Players to Watch | Career stats + phase analysis + recent form | Sections 4-6 |
| Players Who Need to Step Up | Depth chart gaps, phase stats, matchup data | Sections 7-9 |
| Recent Form | `batter_recent_form`, bowler phase data | Section 3 |
| Interesting Data Insights | All 164+ analytics views | Cross-referenced |
| The Bold Take | Percentile rankings + matchup data | Sections 7-9 |
| By the Numbers | All sources | Cross-referenced |
| Keys to Victory | Squad structure, phase data, historical patterns | Section 10 |
| Scouting Report | Tactical insights + opposition data | Section 10 |
| Verdict | Composite rankings + depth chart | Sections 10-11 |

---

## 5. Production Timeline

| Phase | Timeline | Owner | Deliverable |
|-------|----------|-------|-------------|
| **Sample** | Sprint 5, Wave 1 | Virat Kohli | RCB preview (this document) |
| **Founder Gate** | Post-Wave 1 | Founder | Approve/reject sample |
| **Full Production** | Sprint 5, Wave 2-3 | Virat Kohli | Remaining 9 teams |
| **Andy Flower Review** | Per-team, within 24h | Andy Flower | Scouting report accuracy |
| **Tom Brady QA** | Post-production | Tom Brady | Editorial consistency |
| **Final Polish** | Sprint 5 close | Virat Kohli | Cross-team consistency pass |

### Team Order (by narrative richness)
1. RCB (sample — revised per Founder feedback)
2. Chennai Super Kings (legacy franchise, Dhoni transition)
3. Mumbai Indians (rebuild season?)
4. Kolkata Knight Riders (defending champions)
5. Rajasthan Royals (analytical franchise)
6. Delhi Capitals (Pant return narrative)
7. Sunrisers Hyderabad (aggressive identity)
8. Punjab Kings (perpetual rebuild)
9. Gujarat Titans (post-Hardik era)
10. Lucknow Super Giants (stability play)

---

## 6. Andy Flower Collaboration Model

### Per-Team Process
1. Virat Kohli drafts full preview using stat pack data
2. Andy Flower reviews scouting report section for cricket accuracy
3. Andy Flower flags any claims that don't survive domain scrutiny
4. Virat Kohli revises based on Andy's feedback
5. Final version goes to Tom Brady for editorial consistency

### Escalation
- If Virat and Andy disagree on a claim, the data decides
- If data is ambiguous, both perspectives are presented
- Founder has final call on tone disputes

---

## 7. Quality Gates

### Per-Team Checklist
- [ ] Every stat cited is traceable to a specific view/query
- [ ] Sample sizes noted for all statistical claims
- [ ] Contextual accuracy verified — no stats presented without operational context
- [ ] Bold Take is genuinely contrarian (would surprise casual fans)
- [ ] No prediction language ("will", "guaranteed") — only projection ranges
- [ ] Full squad table includes all players and blank Founder Notes column
- [ ] New additions section covers every auction buy
- [ ] Off-season changes are factually verified
- [ ] Team style analysis shows year-over-year evolution with data
- [ ] Category ratings are quantified and league-ranked
- [ ] Venue analysis uses actual venue profile data
- [ ] Schedule section is present (placeholder if schedule unreleased)
- [ ] Recent form includes SR delta trends
- [ ] Data insights are genuinely non-obvious
- [ ] Keys to Victory addresses both upside conditions and structural risks
- [ ] Andy Flower sign-off on scouting report
- [ ] Consistent with other team previews in format and depth
- [ ] Phil Steele Rule: every section teaches something new

### Series-Level Checklist
- [ ] All 10 teams covered with equal rigor
- [ ] No team's preview reads like fan content
- [ ] Cross-team references are consistent (e.g., RCB vs CSK record matches both previews)
- [ ] Verdict ranges don't overlap impossibly (can't have 6 teams projected 1st-2nd)
- [ ] Navigation and indexing for the full series
- [ ] Category ratings allow cross-team comparison

---

## 8. Distribution

### Output Files
- Individual: `outputs/season_previews/{TEAM}_season_preview.md`
- Combined: `outputs/season_previews/IPL_2026_season_preview_complete.md`
- The Lab integration: Add previews as a new section in the Lab dashboard

### Format Options (Post-Founder Approval)
- Markdown (primary — for The Lab)
- PDF export (for distribution)
- Social atomization (LeBron James — pull quotes, stats, graphics briefs)

---

## 9. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-02-13 | Initial 7-section format |
| v1.1 | 2026-02-14 | Incorporated Founder's 12 suggestions: added Off-Season Changes, New Additions, Full Squad Table, Team Style Analysis, Category Ratings, Venue Analysis, Schedule Analysis (placeholder), Players Who Need to Step Up, Recent Form, Interesting Data Insights, Keys to Victory sections. Added Contextual Accuracy Rule. Expanded from 7 to 18 sections. Target word count increased to 3,000-4,000 per team. |

---

*This plan is updated per Founder review. RCB sample has been revised accordingly.*
*Sample preview (RCB) is available at: `outputs/season_previews/RCB_season_preview_sample.md`*
