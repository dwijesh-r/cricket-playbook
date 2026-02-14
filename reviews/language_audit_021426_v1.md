# Language, Readability & Detail Audit Report

**Ticket:** TKT-227
**Auditor:** Virat Kohli (Tone & Narrative Guard)
**Date:** 2026-02-14
**Version:** v1
**Scope:** All dashboards (The Lab, Mission Control), stat packs (MI, CSK sampled), key documents (PRD, Constitution, README)

---

## Executive Summary

**Total Issues Found:** 31
**Severity Breakdown:**

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 5 | Violates Constitution, contradicts product identity |
| HIGH | 9 | Factual inconsistencies, broken numbering, empty sections |
| MEDIUM | 11 | Terminology inconsistencies, unclear jargon, minor inaccuracies |
| LOW | 6 | Style nits, capitalization, minor wording |

**Overall Readability Grade: B+**

The dashboards are polished and visually professional. Tooltip coverage on analytics terms is strong (TKT-109 well executed). The stat packs are data-rich and well-structured. However, there are five critical issues where the language directly contradicts the Constitution's mandate that this is NOT a prediction product. Additionally, the PRD has severe section numbering corruption, and several numeric claims (player counts, view counts, agent counts) are inconsistent across documents.

---

## Category 1: CRITICAL -- Constitution Violations (Tone)

These issues directly contradict Section 1.2 of the Constitution: "We are NOT a prediction product."

### C-1. Hero subtitle uses "predictions" language
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3396)
- **Current:** `"Your all-access pass to the analytics that power IPL 2026 predictions."`
- **Problem:** The word "predictions" frames the entire product as a prediction engine. The Constitution explicitly states we are NOT a prediction product.
- **Recommended fix:** `"Your all-access pass to the analytics behind IPL 2026. Where strategy meets execution."`

### C-2. Navigation card uses "AI-powered team predictions"
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3460)
- **Current:** `"Everything you need to stay ahead of IPL 2026. From AI-powered team predictions to research-backed methodologies, pick your starting point below."`
- **Problem:** "AI-powered team predictions" is prediction/betting language. This is a preview magazine, not a prediction engine.
- **Recommended fix:** `"Everything you need to understand IPL 2026. From data-driven team analysis to research-backed methodologies, pick your starting point below."`

### C-3. Navigation card references "algorithms behind our predictions"
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3481)
- **Current:** `"Learn how we built our analytics. See our PFF-inspired grading system, KenPom efficiency metrics, and the algorithms behind our predictions."`
- **Problem:** "algorithms behind our predictions" is prediction framing.
- **Recommended fix:** `"...and the algorithms behind our player evaluations."`

### C-4. Fantasy cricket reference in Artifacts description
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3471)
- **Current:** `"Compare all 10 teams at once. View depth charts, matchup matrices, and player tags in sortable tables. Great for fantasy cricket and head-to-head analysis."`
- **Problem:** "Great for fantasy cricket" directly associates the product with fantasy/betting use cases. The Constitution says we are NOT "Betting or fantasy advice."
- **Recommended fix:** `"Great for scouting reports and head-to-head analysis."`

### C-5. "stay ahead of" implies prediction/edge
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3460)
- **Current:** `"Everything you need to stay ahead of IPL 2026."`
- **Problem:** "Stay ahead" implies getting a predictive edge, which is betting/fantasy language.
- **Recommended fix:** `"Everything you need to understand IPL 2026."`

---

## Category 2: HIGH -- Factual Inconsistencies & Structural Issues

### H-1. PRD section numbering is severely corrupted
- **File:** `/Users/dwijeshreddy/cricket-playbook/docs/PRD_CRICKET_PLAYBOOK.md`
- **Problem:** Section 6 ("Analytics Views Catalog") uses subsection numbers 4.1-4.9. Section 7 ("Key Metrics Definitions") uses 5.1-5.4. Section 9 ("Sample Queries") uses 7.1-7.4. Section 11 uses 8.x. Section 12 uses 9.x.
- **Expected:** Subsections should match their parent: 6.1, 6.2, ... 7.1, 7.2, etc.
- **Impact:** Confusing for any new reader or contributor referencing the PRD.

### H-2. PRD has duplicated "Key Metrics" table
- **File:** `/Users/dwijeshreddy/cricket-playbook/docs/PRD_CRICKET_PLAYBOOK.md` (lines 70-92)
- **Problem:** The "Data Scale" table under Section 3.1 is immediately followed by a nearly identical "Key Metrics" table with the exact same data. This is a copy-paste artifact.
- **Recommended fix:** Remove the duplicate "### Key Metrics" block (lines 81-92).

### H-3. Player count inconsistency: 231 vs 233
- **Files:** Multiple locations
  - README.md line 127: "233 players"
  - README.md line 192: "231 players"
  - PRD line 79: "231"
  - `docs/specs/WIREFRAMES_V1.md` line 47: "233 players"
  - `docs/INDEX.md` line 64: "233 players"
  - Analysis reports, QA certificates: "231 players"
- **Recommended fix:** Standardize to the verified count (231 per QA certificate) across all documents.

### H-4. Analytics view count inconsistency: 34 vs 35 vs 43
- **Files:**
  - README.md line 128: "35 views"
  - README.md line 158: "34 views" (in code comment)
  - PRD line 78: "43" (Analytics Views)
  - CLAUDE.md: "35 views"
- **Recommended fix:** Run a count of actual views and standardize across all documents.

### H-5. Agent count inconsistency: 12 vs 14
- **Files:**
  - README.md line 71: "12 specialized AI agents"
  - README.md line 186: "12 agents"
  - `config/README.md`: "14 agents"
  - Sprint reviews: "14 agents"
  - CLAUDE.md MEMORY: "14 Agent Personas"
- **Problem:** The roster expanded from 12 to 14 but README was not updated.
- **Recommended fix:** Update README to "14 agents" everywhere.

### H-6. Stat pack "Key Player Tags" section is empty
- **Files:** `/Users/dwijeshreddy/cricket-playbook/stat_packs/MI/MI_stat_pack.md` (lines 53-55), CSK stat pack (lines 54-55)
- **Problem:** Section 1.3 "Key Player Tags" has a table header but zero rows. This is a visible gap in the paid artifact.
- **Recommended fix:** Either populate with actual tag data or remove the empty section.

### H-7. Stat pack section numbering: "3.5" instead of proper hierarchy
- **Files:** MI stat pack (line 161), CSK stat pack (line 156)
- **Problem:** "## 3.5 Team Phase Approach" uses a decimal subsection directly under Section 3 instead of proper Markdown hierarchy (### 3.1, ### 3.2, etc.). Sections jump from 3 to 3.5 with no 3.1-3.4.
- **Recommended fix:** Use `### 3.1 Team Phase Approach` or restructure to `## 4. Team Phase Approach` and renumber downstream sections.

### H-8. CSK stat pack has contradictory trend data for Gaikwad
- **File:** `/Users/dwijeshreddy/cricket-playbook/stat_packs/CSK/CSK_stat_pack.md` (lines 145-149)
- **Problem:** Gaikwad appears in BOTH "Trending UP" (SR +11.6) and "Trending DOWN" (runs -461) for the same 2024-2025 comparison. This is confusing and appears contradictory to the reader.
- **Recommended fix:** Consolidate into a single entry with nuance: "RD Gaikwad: Higher SR (+11.6) but significantly fewer runs (-461) due to limited innings."

### H-9. Venue name truncation in stat packs
- **Files:** MI stat pack (lines 260, 270, 275), CSK stat pack (line 262)
- **Problem:** "Bharat Ratna Shri Atal Bihari Vajpa" is truncated. "Rajiv Gandhi International Sta" is truncated. These appear in tables where column width limits cut off the names.
- **Recommended fix:** Use standardized short names (e.g., "BRSABV Stadium, Lucknow" or "RGICS, Hyderabad") consistently.

---

## Category 3: MEDIUM -- Terminology Inconsistencies

### M-1. "batsman/batsmen" vs "batter" inconsistency
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/mission_control/dashboard/about.html` (line 2051)
- **Current:** `"One of the greatest wicketkeeper-batsmen ever"`
- **Problem:** The ICC and modern cricket usage standardized on "batter" in 2021. The codebase correctly uses "batter" in data fields (`batterClass`, `batterTags`) and tooltips (`"Primary playing role: Batter, Bowler..."`), but about.html uses the legacy "batsmen."
- **Recommended fix:** Change to "wicketkeeper-batters" for consistency.

### M-2. "Bangalore" vs "Bengaluru" in tooltip
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3417)
- **Current:** `data-tooltip="Chennai, Mumbai, Bangalore, Kolkata, Delhi, Punjab, Rajasthan, Hyderabad, Gujarat, Lucknow"`
- **Problem:** Uses "Bangalore" while the franchise name is "Royal Challengers Bengaluru" everywhere else in the codebase (teams.js, venue_data.js, research-desk.html).
- **Recommended fix:** Change to "Bengaluru" to match the official franchise name.

### M-3. "Predicted XI" vs "Predicted XII" vs "Predicted XIs" vs "Predicted XIIs" inconsistency
- **Files:** Mixed usage across all dashboards:
  - teams.html: "Predicted XI" (lines 644, 2992, 4875, 4877)
  - index.html: "Predicted XIIs" (line 3442), "Predicted XIs" (line 3339)
  - artifacts.html: "Predicted XIIs" (lines 691, 775), "Predicted XI" (line 963)
  - analysis.html: "Predicted XIs" (line 1192)
  - about.html: "Predicted XIs" (lines 748, 954)
- **Problem:** The algorithm generates 11 + 1 Impact Player = XII, but terminology switches between XI, XII, XIs, and XIIs randomly.
- **Recommended fix:** Standardize on "Predicted XII" (singular) and "Predicted XIIs" (plural) since the product includes the Impact Player.

### M-4. Tooltip for "Matches Analyzed" says "200" but actual count is different
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (lines 3425-3427)
- **Current:** `"Over" + "200"` for Matches Analyzed
- **Problem:** README states "219 matches" (IPL 2023-2025), PRD says 1,169 IPL matches total. The dashboard says "Over 200" which is imprecise.
- **Recommended fix:** Use the specific count or clarify scope (e.g., "219" for IPL 2023-2025, or "1,169" for all IPL).

### M-5. "TBD" placeholders in about.html roadmap
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/mission_control/dashboard/about.html` (lines 1563, 1567, 1571, 1575)
- **Problem:** Four roadmap items have "TBD" as the owner. This is visible on the public dashboard.
- **Recommended fix:** Either assign owners or mark items as "Unassigned" with a more professional label.

### M-6. "Batters" used in analysis descriptions but "batter" in data fields
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/analysis.html` (multiple lines)
- **Problem:** Descriptions use both "batters" (plural) and "batter" (adjective, e.g., "batter averaging 45"). This is actually correct English usage, but in one location (line 1428) it uses "batters can play normally" in a table description while the formal rating names use underscore-separated technical terms (PRESSURE_SENSITIVE). This is fine but worth noting for consistency.
- **Status:** Acceptable -- no change needed.

### M-7. Cricket jargon without explanation in stat packs
- **Files:** MI and CSK stat packs
- **Problem:** Several terms used in stat packs lack context for the target "cricket-savvy but not expert" audience:
  - "Wicket Efficiency" (+23.2) -- what does the number mean?
  - "Bound%" -- abbreviation for Boundary Percentage not defined in stat pack header
  - "SR Delta" -- appears in tooltips but not in stat pack glossary
- **Recommended fix:** Add a brief glossary section to stat packs, or define abbreviations on first use.

### M-8. "Bowling arm" column header says "Bowling" in stat packs
- **Files:** MI stat pack line 13, CSK stat pack line 13
- **Current:** `| Player | Role | Bowling | Batting | Price (Cr) | Type | Joined |`
- **Problem:** "Bowling" and "Batting" as column headers are ambiguous -- they refer to bowling type and batting hand, not bowling/batting stats.
- **Recommended fix:** Use "Bowl Type" and "Bat Hand" for clarity.

### M-9. Missing "Bowling Trends" economy table in CSK stat pack
- **File:** `/Users/dwijeshreddy/cricket-playbook/stat_packs/CSK/CSK_stat_pack.md` (line 140)
- **Problem:** The "Economy Rate Evolution (Key Bowlers)" header exists but the table itself is empty (no rows). MI stat pack has this populated.
- **Recommended fix:** Populate with CSK bowler economy trends, or remove the empty header.

### M-10. "Left-arm o" truncation in stat pack bowling tables
- **File:** `/Users/dwijeshreddy/cricket-playbook/stat_packs/MI/MI_stat_pack.md` (lines 375, 380)
- **Problem:** "Left-arm o" appears instead of "Left-arm orthodox" due to column width limitations.
- **Recommended fix:** Use abbreviation "LA Orth" or "SLA" consistently and define in glossary.

### M-11. TODO comment visible in source code
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 490)
- **Current:** `/* TODO: Revisit intro animation design later */`
- **Problem:** While this is in CSS comments and not visible to users, it indicates unfinished work. Not user-facing, but noted for completeness.
- **Status:** Low priority -- comment-only, not visible.

---

## Category 4: LOW -- Style & Polish

### L-1. Inconsistent use of "overs 1-6" vs "overs 0-5" for Powerplay
- **File:** PRD line 238 uses "Overs 0-5" while README line 136 uses "overs 1-6"
- **Problem:** Technical schema uses 0-indexed overs, but fan-facing content should use 1-indexed.
- **Recommended fix:** Use "overs 1-6" in all user-facing text; keep 0-indexed only in schema documentation.

### L-2. Footer data claim: "Data: 2023-2025 (219 matches)"
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/index.html` (line 3504)
- **Problem:** The "219 matches" number should be verified as current. The PRD states 1,169 IPL matches total. If the footer refers specifically to the 2023-2025 analysis window, this may be correct, but it could confuse users who see "Over 200" in the stats bar above.
- **Recommended fix:** Make both references consistent.

### L-3. "Predicted XI (top 11)" phrasing
- **File:** `/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/teams.html` (line 4877)
- **Current:** `"Currently showing Predicted XI (top 11)"`
- **Problem:** If the product is "Predicted XII" (11 + Impact Player), showing only 11 and calling it XI is technically accurate but inconsistent with the section title "Predicted XIIs."
- **Recommended fix:** Clarify: "Currently showing Predicted XII (11 starters + Impact Player)"

### L-4. Constitution version mismatch
- **File:** Constitution header says "v2.0" in title but "Version: 2.2.0" in metadata
- **Recommended fix:** Update title to "Constitution v2.2.0"

### L-5. CLAUDE.md says "12 agents" in agent playbook reference
- **File:** `/Users/dwijeshreddy/cricket-playbook/docs/AGENT_PLAYBOOK.md` (line 12)
- **Current:** `"you have 12 specialized agents working together"`
- **Recommended fix:** Update to 14.

### L-6. README "Sprint: 5.0" but project memory says Sprint 4.0
- **File:** README.md line 5 says "Sprint: 5.0"
- **File:** CLAUDE.md MEMORY says "Sprint 4.0"
- **Problem:** Sprint number is inconsistent.
- **Recommended fix:** Align to the current sprint number.

---

## Readability Assessment

### Dashboard Text Quality

| Dashboard | Headers | Tooltips | Labels | Jargon Coverage | Grade |
|-----------|---------|----------|--------|-----------------|-------|
| The Lab (index.html) | Clear, engaging | Good coverage | Clean | Strong | A- |
| Teams (teams.html) | Professional | Excellent (20+ tooltips) | Consistent | Best in class | A |
| Analysis (analysis.html) | Well-structured | Good | Clean | Strong "Why" sections | A |
| Research Desk | Professional | Good | Clean | Schema well-documented | A- |
| Mission Control | Professional | Minimal (none found) | Clean | N/A (internal tool) | B+ |

### Stat Pack Quality

| Aspect | MI | CSK | Grade |
|--------|-----|-----|-------|
| Structure | Consistent, logical | Consistent, logical | A |
| Data completeness | Strong | Strong | A- |
| Empty sections | Tags table empty | Tags table + economy table empty | C |
| Analytical tone | Good -- no prediction language | Good -- no prediction language | A |
| Glossary/context | Missing | Missing | C |
| Trend narratives | Clear | Contradictory (Gaikwad) | B- |

### Key Documents Quality

| Document | Tone | Accuracy | Formatting | Grade |
|----------|------|----------|------------|-------|
| Constitution v2.2.0 | Authoritative, clear | Good | Title version mismatch | A- |
| PRD v3.0.0 | Professional | Duplicated table, wrong numbering | Broken section numbers | C+ |
| README v4.1.0 | Welcoming, well-structured | Multiple stale numbers | Good | B |
| CLAUDE.md | Clear, actionable | Sprint number stale | Good | B+ |

---

## Priority Fix List (Recommended Order)

1. **IMMEDIATE:** Fix all 5 "predictions" references on The Lab homepage (C-1 through C-5). These directly contradict the Constitution.
2. **THIS SPRINT:** Fix PRD section numbering and remove duplicated table (H-1, H-2).
3. **THIS SPRINT:** Standardize player count (231), view count, and agent count across all documents (H-3, H-4, H-5).
4. **THIS SPRINT:** Populate or remove empty stat pack sections (H-6, H-9).
5. **NEXT SPRINT:** Standardize "Predicted XII" terminology (M-3).
6. **NEXT SPRINT:** Fix "Bangalore" tooltip (M-2) and "batsmen" reference (M-1).
7. **BACKLOG:** Add glossary to stat packs (M-7), fix venue truncation (H-9), address remaining LOW items.

---

## Overall Readability Grade: B+

**Strengths:**
- Dashboard tooltip system (TKT-109) is excellent -- analytics terms are well-explained on hover
- Stat pack structure is consistent across teams
- Professional, confident editorial tone in analysis descriptions
- The "Why this was done" cards on analysis.html are outstanding for transparency
- No betting/prediction language in stat packs (only in dashboard homepage)

**Weaknesses:**
- Constitution-violating prediction language on the most visible page (The Lab homepage)
- PRD numbering corruption makes it unreliable as a reference document
- Numeric inconsistencies (231/233, 34/35/43, 12/14) undermine credibility
- Empty sections in stat packs (the paid artifact) are unprofessional
- No glossary for cricket analytics terms in stat packs

---

*Audit completed by Virat Kohli, Tone & Narrative Guard*
*Cricket Playbook v4.0.0 | Sprint 4.0*
