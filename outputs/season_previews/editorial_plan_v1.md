# Season Preview — Editorial Plan v1

**Cricket Playbook | IPL 2026 Season Preview Series**
*Agent: Virat Kohli (Tone & Narrative Guard)*
*Status: Awaiting Founder Approval*

---

## 1. Format Per Team

Each team preview follows a 7-section structure inspired by Lindy's Football Annual and Phil Steele's College Football Preview:

| Section | Length | Purpose |
|---------|--------|---------|
| **The Headline** | 1-2 sentences | Bold thesis — the single most important storyline |
| **The Story** | 400-600 words | Narrative: what changed, who's new, what to watch |
| **Players to Watch** | 3-4 profiles | Data-backed individual storylines, ~100 words each |
| **The Bold Take** | 150-200 words | One contrarian opinion supported by evidence |
| **By the Numbers** | 5 key stats | The numbers that tell the season story |
| **Andy Flower's Scouting Report** | 200-300 words | Tactical overview: identity, strengths, vulnerabilities, opposition blueprint |
| **Verdict** | 1-3 sentences | Projected finish range, ceiling/floor |

**Total per team:** ~1,500-2,000 words
**Total series:** ~15,000-20,000 words across 10 teams

---

## 2. Tone Guidelines

### The Phil Steele Rule
Every section must teach the reader something they didn't know. If a paragraph could appear in any generic cricket preview, it doesn't belong here.

### Voice
- **Sharp, not flashy.** Write with authority, not hype.
- **Restrained, not cold.** Passion is allowed; breathlessness is not.
- **Credible, not hedging.** Make claims. Back them with data. Don't say "could potentially maybe."
- **Specific, not vague.** "Bhuvneshwar's 6.70 powerplay economy" not "strong bowling."

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

### The Headline
- Must be a thesis, not a label. "RCB's Bowling-First Revolution" not "RCB Preview 2026"
- Should provoke thought — the reader should want to know *why*
- Draws from Section 10 (Andy Flower's Tactical Insights) of the stat pack

### The Story
- Opens with the franchise's 2025 trajectory — where they ended, what it means
- Introduces key acquisitions and departures
- Identifies the central strategic question for 2026
- Closes with what success and failure look like

### Players to Watch
- Each profile: name, price, one killer stat, the storyline
- Mix of stars (Kohli), unsung heroes (Bhuvneshwar), and X-factors (Bethell)
- At least 1 player from each discipline (bat, bowl, all-round)
- Bold stat first, narrative second

### The Bold Take
- Must be genuinely contrarian — something most fans would disagree with
- Must be supported by at least 2 data points from our analytics
- Should reframe how the reader thinks about the team
- Example: "Kohli is no longer RCB's most important player"

### By the Numbers
- 5 stats exactly. No more, no less.
- Each stat tells a story — not just a number, but what it means
- Format: stat | value | one-line context
- Mix of team-level and player-level stats

### Andy Flower's Scouting Report
- Written in Andy Flower's voice: cricket-first, tactically precise
- Structure: Identity -> Strengths -> Vulnerabilities -> Opposition Blueprint
- Identifies specific matchup vulnerabilities (e.g., "Kohli vs off-spin: 102 SR")
- Gives actionable scouting intel, as if preparing a coaching staff

### Verdict
- One sentence: projected finish range
- Ceiling and floor in parentheses
- No hedging — commit to a range

---

## 4. Data Sources Per Section

| Section | Primary Data Source | Stat Pack Section |
|---------|-------------------|-------------------|
| The Headline | Depth chart + tactical insights | Section 10 |
| The Story | Squad composition + recent form | Sections 1-3 |
| Players to Watch | Career stats + phase analysis | Sections 4-6 |
| The Bold Take | Percentile rankings + matchup data | Sections 7-9 |
| By the Numbers | All sources | Cross-referenced |
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
1. RCB (sample — DONE)
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
- [ ] Bold Take is genuinely contrarian (would surprise casual fans)
- [ ] No prediction language ("will", "guaranteed") — only projection ranges
- [ ] Andy Flower sign-off on scouting report
- [ ] Consistent with other team previews in format and depth
- [ ] Phil Steele Rule: every section teaches something new

### Series-Level Checklist
- [ ] All 10 teams covered with equal rigor
- [ ] No team's preview reads like fan content
- [ ] Cross-team references are consistent (e.g., RCB vs CSK record matches both previews)
- [ ] Verdict ranges don't overlap impossibly (can't have 6 teams projected 1st-2nd)
- [ ] Navigation and indexing for the full series

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

*This plan awaits Founder approval before full production begins.*
*Sample preview (RCB) is available at: `outputs/season_previews/RCB_season_preview_sample.md`*
