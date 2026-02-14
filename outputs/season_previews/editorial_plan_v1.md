# Season Preview — Editorial Plan v1.2

**Cricket Playbook | IPL 2026 Season Preview Series**
*Agent: Virat Kohli (Tone & Narrative Guard)*
*Status: Founder-Approved (RCB sample at v1.8). Templatized for 10-team production.*
*Revision Date: 2026-02-14*

---

## 1. Format Per Team

Each team preview follows a **21-section structure** inspired by Lindy's Football Annual and Phil Steele's College Football Preview. The Founder's 12 suggestions have been integrated. The approved RCB sample (v1.8) is the canonical reference for format and tone.

| # | Section | JS `id` | Length | Purpose |
|---|---------|---------|--------|---------|
| 1 | **The Headline** | (hero) | 1-2 sentences | Bold thesis — the single most important storyline |
| 2 | **The Story** | `story` | 400-500 words | Narrative: what changed, who's new, what to watch |
| 3 | **Off-Season Changes** | `offseason` | 200-300 words | Trades, coaching, captaincy, structural differences from 2025 |
| 4 | **New Additions** | `newAdditions` | 150-250 words | Each new signing: gap filled, style fit, key stat |
| 5 | **Full Squad Table** | `squad` | Table | Predicted XII + Bench with Name, Role, Price, Nat, Key Stat, Founder Notes |
| 6 | **Team Style Analysis** | `teamStyle` | 300-400 words | Year-over-year evolution with phase SR/econ tables |
| 7 | **Category Ratings** | (ratings) | Table + 150 words | 7 categories (Bat PP/Mid/Death, Bowl PP/Mid/Death, Overall) rated 1-10 |
| 8 | **Team Batting Profile** | `battingProfile` | 300-400 words | vs bowling types table + phase-wise table + Phase x Bowling Type cross-reference |
| 9 | **Innings Context** | `inningsContext` | 400-500 words | Setting vs chasing splits (team + individual) + chase approach (target bands, collapse zones, early wickets, player scaling, year-over-year) |
| 10 | **Venue Analysis** | `venue` | 200-300 words | Home ground phase profile vs league averages + team fit |
| 11 | **Schedule Analysis** | `schedule` | Placeholder | Home/away, clusters, rest days — populated when schedule releases |
| 12 | **Head-to-Head Record** | `headToHead` | 200-300 words | Since-2023 + all-time tables with key patterns per opponent |
| 13 | **Players to Watch** | `playersToWatch` | 3-4 profiles, ~100 words each | Data-backed individual storylines |
| 14 | **Players Who Need to Step Up** | `playersStepUp` | 200-300 words | Weakness + specific player who can address it |
| 15 | **Recent Form** | `recentForm` | Table + 150 words | Last 10 innings SR + delta from career + bowler phase economies |
| 16 | **Interesting Data Insights** | `dataInsights` | 3-5 insights, ~250 words | Non-obvious findings from 172+ analytics views |
| 17 | **The Bold Take** | (boldTake) | 150-200 words | One contrarian opinion backed by 2+ data points |
| 18 | **By the Numbers** | (byTheNumbers) | 5 key stats | The numbers that tell the season story |
| 19 | **Keys to Victory** | (keysToVictory) | 200-300 words | 3-4 conditions that must be met to contend |
| 20 | **Andy Flower's Scouting Report** | (scoutingReport) | 200-300 words | Identity, strengths, vulnerabilities, opposition blueprint |
| 21 | **Verdict** | (verdict) | 1-3 sentences | Projected finish range, ceiling/floor |

**Total per team:** ~4,000-5,000 words (RCB sample: ~4,800 words)
**Total series:** ~40,000-50,000 words across 10 teams

### Sections Added Since v1.1 (Validated in RCB Sample)
- **Section 8 (Team Batting Profile):** vs bowling types, phase-wise batting with boundary/dot%, Phase x Bowling Type cross-reference with ball counts and confidence labels
- **Section 9 (Innings Context):** Setting vs chasing team splits, individual player splits, chase approach analysis (target bands, collapse zones, early wickets, player scaling by target, year-over-year trends)
- **Section 12 (Head-to-Head Record):** Since-2023 + all-time tables with key pattern callouts per opponent

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

## 9. The Lab Integration Spec

### JS Data Structure (`scripts/the_lab/dashboard/data/season_previews.js`)

Each team entry in `SEASON_PREVIEWS` follows this schema:

```javascript
const SEASON_PREVIEWS = {
  TEAM_ABBREV: {
    available: true|false,    // false = "Coming Soon" placeholder
    meta: {
      revision: 'v1.x',
      dataWindow: 'IPL 2023-2025 | 9,289 matches / 2.14M balls',
      agents: 'Virat Kohli (Tone & Narrative) | Andy Flower (Scouting Report)',
      matches: '9,289'
    },
    headline: { title: '...', intro: '...' },
    verdict: { text: '...', projected: '3rd-4th', ceiling: 'Champions', floor: '6th' },
    byTheNumbers: [
      { value: '8.73', label: 'RCB\'s 2025 PP econ', context: 'Down from 9.77...' }
      // exactly 5 entries
    ],
    categoryRatings: [
      { cat: 'Batting, Powerplay', rating: 6.5, metric: '154.1 SR', note: 'Above average...' }
      // 7 entries: Bat PP/Mid/Death, Bowl PP/Mid/Death, Overall
    ],
    boldTake: { claim: '...', argument: '...' },
    keysToVictory: [
      { title: '...', text: '...' }
      // 3-4 entries
    ],
    scoutingReport: {
      identity: '...',
      strengths: ['...', '...'],       // array of strings
      vulnerabilities: ['...', '...'],  // array of strings
      blueprint: '...'
    },
    sections: [
      {
        id: 'story',           // matches the JS id column in section table
        title: 'The Story',
        summary: '1-2 sentence summary shown in collapsed header',
        blocks: [
          { type: 'text', content: '<p>HTML paragraph...</p>' },
          { type: 'subheading', content: 'Subheading Text' },
          { type: 'table', headers: ['Col1', 'Col2'], rows: [['val', 'val']] },
          { type: 'callout', content: 'Highlighted insight text' }
        ]
      }
      // 14 collapsible sections (sections 2-6, 8-16 from the master list)
    ]
  }
};
```

### Block Types
| Type | Renders As | Notes |
|------|-----------|-------|
| `text` | `<p>` paragraph | HTML allowed. Use `<strong>` for emphasis, `<em>` for accent color |
| `subheading` | Section sub-header | Used within a collapsible section for internal structure |
| `table` | Magazine-quality table | `headers` array + `rows` array of arrays. Last column wraps. |
| `callout` | Accent-bordered highlight box | For tactical prescriptions or key insights |

### Rendering
- Sections 1, 7, 17-21 render as **fixed components** (hero, ratings, bold take, by the numbers, keys, scouting report, verdict)
- Sections 2-6, 8-16 render as **collapsible sections** via the `sections` array
- Category ratings are collapsible cards with loader bars (click to expand note)
- All text is justified. Tables allow last-column wrapping.

---

## 10. Jose Mourinho Quality Scoring Rubric

Each preview is scored on a 10-point scale across 5 dimensions. Target: **8.5+ to ship**.

| Dimension | Weight | Criteria | Score Range |
|-----------|--------|----------|-------------|
| **Statistical Accuracy** | 25% | All stats traceable, correct rounding, no calculation errors | 0-10 |
| **Sample Size Integrity** | 20% | HIGH/MEDIUM/LOW labels present, ball counts for cross-references, caveats for small samples | 0-10 |
| **Contextual Accuracy** | 20% | No stats presented without operational context (e.g., death SR from batting through vs entering at death) | 0-10 |
| **Analytical Depth** | 20% | Phase x bowling type cross-references, innings context splits, non-obvious insights | 0-10 |
| **Consistency** | 15% | No internal contradictions, totals add up, dual-scope used correctly | 0-10 |

### Severity Levels for Issues
| Level | Impact | Action |
|-------|--------|--------|
| **CRITICAL** | Factual error (wrong number, wrong player) | Must fix before any gate |
| **HIGH** | Missing context that changes interpretation | Must fix before domain sanity |
| **MEDIUM** | Improvement that strengthens a claim | Fix before enforcement |
| **LOW** | Polish item (rounding, label, small sample caveat) | Fix before ship |

### RCB Sample Scores (Reference)
- Initial draft: 7.2/10 (3 HIGH, 2 MEDIUM, 5 LOW)
- After HIGH/MEDIUM fixes: 8.4/10
- After LOW fixes (v1.8): 9.0/10

---

## 11. Production Checklist (Per Team)

### Phase 1: Data Assembly (~30 min)
- [ ] Run stat pack generator for team: `python scripts/generators/generate_stat_packs.py --team ABBREV`
- [ ] Run depth chart generator: `python scripts/generators/generate_depth_chart.py --team ABBREV`
- [ ] Run predicted XII generator: `python scripts/generators/generate_predicted_xii.py --team ABBREV`
- [ ] Query innings context views: `analytics_ipl_team_batting_by_innings_since2023`, `analytics_ipl_team_bowling_by_innings_since2023`
- [ ] Query batting profile views: `analytics_ipl_batter_vs_bowler_type_since2023`, `analytics_ipl_batter_phase_since2023`
- [ ] Query venue profile: `analytics_ipl_venue_profile_since2023`
- [ ] Query head-to-head: `analytics_ipl_team_matchup_matrix_since2023`
- [ ] Query recent form: `analytics_ipl_batter_recent_form`
- [ ] Compile chase approach data: target bands, collapse zones, player scaling by target

### Phase 2: Editorial Draft (~45 min)
- [ ] Virat Kohli writes all 21 sections following this template
- [ ] Every stat includes sample size + confidence label
- [ ] Phase x Bowling Type cross-reference includes ball counts
- [ ] Bold Take is genuinely contrarian (would surprise casual fans)
- [ ] Output: `outputs/season_previews/{ABBREV}_season_preview.md`

### Phase 3: Review Loop (~20 min)
- [ ] Andy Flower: cricket accuracy, scouting report sign-off
- [ ] Jose Mourinho: statistical accuracy score (target 8.5+)
- [ ] Apply corrections per severity level
- [ ] LeBron James: social proof (pull quotes, shareable stats)
- [ ] Tom Brady: editorial consistency with other previews

### Phase 4: Lab Integration (~15 min)
- [ ] Build JS data entry in `season_previews.js` matching the schema above
- [ ] Set `available: true` for the team
- [ ] Verify rendering in Preview tab (desktop + mobile)
- [ ] Commit + push

### Phase 5: Quality Gate
- [ ] Kante QA: rounding, sample sizes, confidence labels, internal consistency
- [ ] Jose score >= 8.5
- [ ] Andy Flower sign-off
- [ ] Tom Brady enforcement pass

---

## 12. Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-02-13 | Initial 7-section format |
| v1.1 | 2026-02-14 | Incorporated Founder's 12 suggestions. Expanded from 7 to 18 sections. |
| v1.2 | 2026-02-14 | Founder approved RCB sample (v1.8). Updated to 21-section structure reflecting approved sample (added Team Batting Profile, Innings Context, Head-to-Head). Added Lab JS integration spec with data schema. Added Jose Mourinho quality scoring rubric. Added per-team production checklist. Word count target updated to 4,000-5,000 per team. |

---

*Canonical reference: `outputs/season_previews/RCB_season_preview_sample.md` (v1.8, Founder-approved)*
*Content language rules: `config/content_language_guide.md`*
*Lab data schema: `scripts/the_lab/dashboard/data/season_previews.js`*
