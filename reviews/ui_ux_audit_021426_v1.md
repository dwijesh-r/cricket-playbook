# UI/UX Audit Report - Cricket Playbook Dashboards

**Ticket:** TKT-228
**Auditor:** Kevin de Bruyne (Visualization Lead)
**Date:** 2026-02-14
**Version:** v1
**Scope:** The Lab (3 pages) + Mission Control (1 page)
**Type:** READ-ONLY audit -- no files modified

---

## Executive Summary

The Cricket Playbook dashboard suite demonstrates **professional-grade design** with a coherent Apple-inspired design system, a well-thought-out dark/light theme toggle, and genuinely impressive attention to detail. The CSS custom properties architecture is mature, the glassmorphism effects are tasteful, and the mobile responsive work is among the most thorough I have seen in a project of this scope.

**Overall Verdict:** This is already a top-tier product visually. The improvements below are refinements to push from "very good" to "world-class."

---

## 1. The Lab - File-by-File Visual Audit

### 1.1 `index.html` (Home Page) -- 4,167 lines

**Color Scheme: A**
- CSS custom properties system (lines 10-56) is perfectly consistent across dark/light themes.
- Apple SF-style color palette: `#0a84ff` (accent), `#30d158` (green), `#ffd60a` (yellow), `#ff453a` (red), `#bf5af2` (purple). These are the exact iOS system colors -- excellent choice.
- Dark mode gradient background (line 136) uses subtle deep blues (`#0a0a12`, `#0d1020`) -- premium feel.
- Light mode (lines 37-56) properly inverts all variables. No hardcoded dark-only values leaking.

**Typography: A-**
- Inter font family (line 7, 123) is the right choice for data-heavy dashboards.
- Weight range 300-800 loaded -- provides full hierarchy.
- Hero title at 56px/800wt (line 447) with gradient text fill is striking.
- ISSUE (line 2596-2600): At 380px breakpoint, font sizes drop as low as `4px` for trophy text and `6px` for names. These are illegible. Minimum readable font on mobile should be 10px.
- Anti-aliasing enabled (line 127) -- good.

**Spacing: A**
- Consistent 24px base padding on sections (line 2744).
- Hero section uses generous 80px top / 60px bottom padding (line 425).
- Card padding at 24px (line 2798) and 32px for nav cards (line 2899) is well-balanced.
- Gap system is consistent: 20px for grids (lines 2791, 2891), 60px for stats bar (line 2708).

**Card/Panel Design: A**
- Unified card pattern: `linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%)` with `1px solid var(--border)` and `16px border-radius`.
- Team cards (line 2794-2821) have a colored top accent bar, hover lift effect (`translateY(-4px)`), and blue glow on hover. Professional.
- Rating badges use gradient fills (line 2873-2880).

**Navigation: A**
- Fixed nav bar at 56px height (line 207) with frosted glass effect (`backdrop-filter: saturate(180%) blur(20px)`).
- Tab system in pill container (line 252-283) with gradient active state.
- Hamburger menu implemented for mobile (lines 286-356) with proper animation transitions.
- Mobile dropdown menu (lines 320-356) with `translateY` animation and pointer-events control.

**Intro Animation: B+ (currently disabled)**
- The trading card / jersey back intro system (lines 489-1893) is extraordinarily detailed -- CSS-only athlete figures, sport-specific stadium backgrounds, trophy lift animations, camera flashes, confetti.
- ISSUE: Currently disabled with `display: none !important` (line 492). The backlog note says "revisit later."
- The 14-agent card system with CSS variables for jersey colors is impressive engineering.

**Unique Standout Elements:**
1. Animated stats container with conic-gradient rotating border (lines 2626-2668).
2. Floating particle system in stats widget (lines 2674-2703).
3. Background watermark text "THE LAB" (lines 188-203).
4. Typewriter animation for hero text (lines 458-487).
5. Navigation guide FAB button with pulse animation (lines 3131-3258).

---

### 1.2 `teams.html` (Teams Page -- Main Product) -- 5,599 lines

**Color Scheme: A**
- Identical CSS variable system to index.html -- full consistency.
- Team-specific color accents via `--team-color` CSS variable on cards.

**Typography: A**
- Consistent Inter usage.
- Progressive disclosure system (TKT-110, lines 117-247) uses good font hierarchy: 14px/600wt headers, 12px for labels.
- Phase bar labels at 8px (line 290) and phase tags at 9px (line 317) are borderline small but acceptable for data-dense tables.
- ISSUE: Phase label at 7px (line 338) is too small. Minimum should be 9px.

**Data Visualization Quality: A-**
- Phase performance bars (TKT-111, lines 249-345): Color-coded bar fills (elite=green, specialist=teal, average=grey). Compact and readable.
- Pressure Index system (lines 2801-2926): Full table with sortable columns, expandable detail rows, search/filter bar. Very thorough.
- Player profile modal (TKT-200, lines 2022-2099): Proper modal with backdrop blur, gradient background, max-height scrolling.
- ISSUE: Roster table forces horizontal scroll on mobile with `min-width: 600px` (line 1980). This is a known trade-off but worth noting.

**Mobile Responsiveness:**
- Hamburger menu (lines 1926-1967) implemented.
- `@media (max-width: 768px)` block (lines 1969-1990) handles table overflow, grid collapse, search bar stacking.
- Touch targets: `.mobile-nav a` has `min-height: 44px` (line 2932), `.theme-toggle` has `min-width: 44px; min-height: 44px` (line 2933). WCAG compliant.
- `overflow-x: hidden` (line 2929) prevents horizontal scrollbar.

**Information Density: A**
- Content tabs system (line 2990-2997) with 6 views: Predicted XI, Full Squad, Depth Chart, Strategy Outlook, Pressure, Compare.
- Progressive disclosure (expandable sections) prevents information overload.
- "Show More / Show Less" for extended squad (lines 199-247).

**Issues Found:**
1. (Line 338) `font-size: 7px` for `.phase-label` -- below readable threshold.
2. (Line 2922) Pressure table on mobile sets `min-width: 700px` -- wider than the 600px set for main roster table. Inconsistent.
3. (Line 2831) `.pressure-filtered-stat .pressure-stat-label` at `font-size: 9px` -- borderline.

---

### 1.3 `research-desk.html` (The Film Room) -- 7,028 lines

**Color Scheme: A**
- Identical CSS variable system.
- Additional monospace font: JetBrains Mono (line 8) for code/query content -- perfect choice for a SQL-oriented interface.

**Layout: A**
- Two-column layout: 280px sidebar + flexible workspace (line 273-280).
- Schema sidebar is sticky (line 289-291) with own scroll -- proper IDE-style layout.
- Status bar at bottom (lines 1103-1144) with connection indicator -- professional IDE feel.

**Schema Browser: A-**
- Interactive schema browser (TKT-175, lines 387-474): Expandable table/column tree, color-coded data types (varchar=blue, bigint=orange, double=green, boolean=purple).
- Column type badges (lines 462-468) are well-designed with subtle colored backgrounds.
- Category groups with collapsible sections (lines 476-500).
- ISSUE: Schema search input at `font-size: 16px` (line 319) -- this is actually correct since it prevents iOS auto-zoom on focus. Good practice.

**Query Explanation Panel: A**
- Colored tag system (lines 1214-1233): player=blue, team=green, phase=teal, venue=orange, season=yellow, bowler-type=purple, role=pink.
- Route visualization with arrow indicators (lines 1239-1248).

**Side-by-Side Comparison: B+**
- Comparison cards (lines 1250-1298) with wins/losses border-top accent.
- ISSUE: Collapses to single column at 600px (line 1257) -- this is correct behavior but comparison loses its value without side-by-side layout. Could use an alternative visualization on narrow screens.

**Mobile Responsiveness:**
- Schema sidebar collapses properly (lines 1157-1180) with toggle capability.
- Grid switches from 2-column to 1-column at 768px.
- Mobile nav with 44px minimum touch targets (line 1179).
- Editor toolbar wraps at 480px (line 1184).

**Issues Found:**
1. (Line 1116) Status bar font at 11px on mobile -- could be hard to read. Consider hiding on mobile or increasing size.
2. No explicit `@media` handling for the status bar position on mobile -- it may overlap with mobile nav.

---

## 2. Mission Control - Visual Audit

### 2.1 `index.html` (The Boardroom) -- 10,097 lines

**Color Scheme: A**
- Identical CSS variable system with two additional variables: `--bg-sports` and `--text-sports` for background pattern opacity.
- Additional font: Cinzel (line 8) -- a serif display font for the "Boardroom" branding. Elegant choice for the administrative dashboard.

**Background Design: A+**
- Cricket-themed SVG pattern (lines 200-213) with ball, bat, stumps, six marker, trophy -- extremely clever.
- Corner accent brackets (lines 254-294) -- sports broadcast inspired.
- Floating cricket ball decorations (lines 297-345) with CSS-only design including seam detail.
- Diagonal accent stripes (lines 242-253).
- Dot pattern overlay with mask fade (lines 368-378).
- This is the most visually distinctive background in the entire product.

**Kanban Board: A**
- 8-column grid layout (line 1157) for full workflow: IDEA -> BACKLOG -> READY -> RUNNING -> BLOCKED -> REVIEW -> VALIDATION -> DONE.
- Each column has a unique top accent color (lines 1191-1199) -- properly color-coded for quick scanning.
- Column headers have dark background overlay (line 1207) for separation.
- FOUNDER_REVIEW column gets special crimson/gold styling (lines 1211-1225) -- excellent hierarchy distinction.

**Ticket Card Design: A**
- Glass-effect cards (line 1282) with gradient background.
- Left accent bar appears on hover (lines 1304-1315) color-coded by priority.
- Agent-specific team color borders (lines 1401-1424) -- Patriots Navy, Warriors Blue, Lakers Purple, Man City Sky Blue, etc. This is a standout design decision.
- Sport icons on tickets (lines 1394-1398): NFL, NBA, soccer, cricket.
- Retro tickets for Pep Guardiola get special sky blue styling (lines 1427-1439).
- Hover state with 3D lift effect (line 1320): `translateY(-3px) scale(1.01)`.

**Sprint View: A**
- Hero section with large sprint title (52px, line 619) and gradient text.
- Stats grid with rainbow gradient border (line 648) -- innovative.
- Color-coded stat values: green for done, yellow for running, red for blocked, blue for total (lines 705-708).

**Agent Modal: A-**
- 4-column grid of agent avatars (line 1023).
- Selection state with blue border and checkmark (lines 1045-1068).
- ISSUE: Agent grid switches to 3 columns at 600px (line 1139) which is fine, but the avatar size (44px) might be tight for 4 per row on tablets.

**Filter System: A**
- Search box with icon (lines 806-835).
- Filter buttons with gradient active state (lines 837-879).
- Priority and effort dropdowns (lines 881-927).
- On mobile (600px), filter layout switches to 2-column grid (lines 4321-4428). This is excellent mobile design work.

**Mobile Responsiveness:**
- Kanban: 8 cols -> 4 cols (1400px) -> 2 cols (900px) -> 1 col (600px). (Lines 4286-4302.)
- Mobile bottom navigation (mentioned in CSS at line 4484).
- Collapsible columns on mobile (lines 4377-4428) with tap-to-expand -- brilliant solution for mobile kanban.
- Touch targets enforced at 44px (lines 4513-4515).
- Stats grid wraps to 2 per row on smallest screens (line 4479).
- Table view hidden on mobile, replaced with card view (lines 4313-4314).

**Issues Found:**
1. (Line 4484) `.mobile-nav-tab` font-size drops to 8px at 480px -- illegible.
2. (Line 1157) 8-column kanban at full width means very narrow columns on 1400-1800px screens. Column content might feel cramped.
3. (Lines 5503-5520) Inline styles in HTML with `font-size: 8px` and `font-size: 9px` for the token dashboard decay visualization -- should be classes.
4. Some inline styles in the HTML body use hardcoded font sizes instead of CSS classes.

---

## 3. Mobile Responsiveness Score

| File | Breakpoints | Touch Targets | Min Font | Overflow | Hamburger | Score |
|------|-------------|--------------|----------|----------|-----------|-------|
| **Lab index.html** | 768, 600, 500, 480, 380 (5) | 44px enforced | 6px (fail) | Protected | Yes | **8/10** |
| **Lab teams.html** | 768, 600, 480 (3) | 44px enforced | 7px (fail) | Protected | Yes | **8/10** |
| **Lab research-desk.html** | 768, 600, 480 (3) | 44px enforced | 10px (pass) | Protected | Yes | **9/10** |
| **MC index.html** | 1400, 900, 768, 600, 480, 380 (6) | 44px enforced | 8px (fail) | Protected | Yes | **9/10** |

**Aggregate Mobile Score: 8.5 / 10**

### Detailed Breakpoint Analysis

**The Lab - index.html:**
- 768px: Nav tabs hidden, hamburger shown, hero title 32px, stats wrap, grids collapse to 1-col.
- 600px: Stat values shrink, nav time hidden, nav guide button repositioned.
- 480px: Hero title 26px, nav button hidden, extra small stat text.
- 380px: Minimum sizes enforced (but 4-6px for intro card text).
- `overflow-x: hidden` on body (line 3122).

**The Lab - teams.html:**
- 768px: Nav hidden, table wrapper scrolls horizontally, XI grid collapses, filters stack vertically.
- Content tabs scroll horizontally with overflow-x: auto (line 1988).
- Touch target: All mobile nav links at 44px min-height.
- `overflow-x: hidden` on html,body (line 2929).

**The Lab - research-desk.html:**
- 768px: Sidebar collapses from left panel to stacked layout. Schema can be toggled.
- 480px: Toolbar wraps, editor margins tighten.
- Schema search input at 16px prevents iOS auto-zoom (line 319).
- `overflow-x: hidden` on html,body (line 122).

**MC index.html:**
- 1400px: Kanban drops from 8 to 4 columns.
- 900px: Kanban drops to 2 columns, mobile nav appears.
- 600px: Kanban drops to 1 column, table view hidden/card view shown, filter layout switches to 2-column grid, collapsible columns enabled.
- 480px: Extreme compaction -- stat values 20px, ticket padding 12px, avatar 36px.
- Touch targets enforced globally (line 4513-4515).
- Dynamic viewport height used: `min-height: 100dvh` (line 138).

---

## 4. Top 10 Quick Wins

These are specific CSS changes that would immediately improve quality:

### QW-1: Fix Minimum Font Sizes on Smallest Breakpoints
**Files:** `index.html` (lines 2596-2600), `teams.html` (line 338)
**Issue:** Font sizes drop to 4-7px at 380px breakpoint.
**Fix:** Set minimum `font-size: 10px` for all text elements at the 380px breakpoint. For intro card text, consider hiding labels entirely rather than rendering them at 4px.
```css
@media (max-width: 380px) {
    .trophy-ticker .trophy-text { font-size: 10px; }
    .label-group .name { font-size: 10px; }
    .phase-label { font-size: 9px; }
}
```

### QW-2: Fix Mobile Nav Tab Font Size
**File:** `MC index.html` (line 4484)
**Issue:** `.mobile-nav-tab` drops to `font-size: 8px` at 480px.
**Fix:** Minimum 10px, or use icon-only navigation at that breakpoint.
```css
.mobile-nav-tab { font-size: 10px; }
```

### QW-3: Add `scroll-behavior: smooth` Globally
**Files:** All 4 HTML files
**Issue:** Navigation between sections uses default instant scroll.
**Fix:** Add to `html` element:
```css
html { scroll-behavior: smooth; }
```

### QW-4: Add Focus Styles for Keyboard Navigation
**Files:** All 4 HTML files
**Issue:** No visible `:focus` styles on interactive elements beyond browser defaults.
**Fix:** Add focus-visible ring:
```css
:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}
```

### QW-5: Status Bar Overlap Fix on Mobile
**File:** `research-desk.html` (line 1104-1118)
**Issue:** Fixed status bar at bottom may overlap with mobile browser chrome or navigation.
**Fix:** Add `@media (max-width: 768px)` to hide status bar or make it position: static.
```css
@media (max-width: 768px) {
    .status-bar { position: static; }
}
```

### QW-6: Consistent Nav Height Across Lab Pages
**Files:** Lab `index.html` (line 207: 56px), MC `index.html` (line 399: 52px)
**Issue:** Nav height differs by 4px between The Lab and Mission Control.
**Fix:** Standardize to 56px across both dashboards for visual consistency.

### QW-7: Add `prefers-reduced-motion` Media Query
**Files:** All 4 HTML files
**Issue:** Multiple animations (pulse-glow, float-ball, confetti, rotating background) run continuously with no option to disable.
**Fix:**
```css
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### QW-8: Improve Pressure Table Mobile Experience
**File:** `teams.html` (line 2922)
**Issue:** Pressure table sets `min-width: 700px` on mobile, requiring significant horizontal scroll.
**Fix:** Either (a) reduce min-width to 500px by hiding non-critical columns, or (b) switch to card-based layout at 768px (similar to how MC handles tables with `.mobile-cards`).

### QW-9: Add Loading Skeleton States
**Files:** `teams.html`, `MC index.html`
**Issue:** Both pages load data via JavaScript. During loading, content areas are empty. The `teams.html` uses a simple spinner (line 1914-1924).
**Fix:** Add CSS skeleton shimmer for cards and tables:
```css
.skeleton {
    background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-elevated) 50%, var(--bg-tertiary) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

### QW-10: Replace Inline Styles in MC Token Dashboard
**File:** `MC index.html` (lines 5330-5520)
**Issue:** Token dashboard uses extensive inline styles with `font-size: 8px`, `font-size: 9px` directly in HTML.
**Fix:** Extract to CSS classes (`.token-label`, `.token-time-text`, `.decay-bar-label`) for maintainability and consistency.

---

## 5. Top 5 Standout Features (What Makes This Visually Unique)

### SF-1: Sports-Themed Background System (MC)
The Mission Control background (MC lines 146-391) is a masterclass in themed UI. The cricket SVG pattern, floating ball decorations with seam detail, corner accent brackets, and diagonal stripe accents create an immersive sports broadcast feel. The attention to detail -- cricket stumps, bat, ball, trophy, and "6" marker in the SVG pattern -- is exceptional and unlike anything I have seen in a dashboard product.

### SF-2: Agent Identity System
The team-color coding across tickets (MC lines 1401-1424), card backgrounds (Lab index lines 766-821), and sport-based icons creates a visual language that makes the multi-agent system immediately legible. Seeing a Lakers purple border on a LeBron James ticket or a Patriots navy on a Tom Brady ticket is both functional and delightful. This is the kind of design that makes users smile.

### SF-3: CSS-Only Trading Card Athletes (Lab index)
The intro animation system (Lab index lines 489-1893, currently disabled) is one of the most ambitious CSS-only designs I have ever encountered: jersey shapes, sleeve cuts, collar styles, coat lapels, beard shapes, hair styles, trophies (Lombardi, IPL, UCL, NBA, Premier League, World Cup, NFC Championship) -- all built purely in CSS with proper shadows, gradients, and clip-paths. When re-enabled, this will be a show-stopping introduction.

### SF-4: Interactive Film Room (research-desk.html)
The SQL query interface with schema browser, color-coded data types, query explanation tags, and comparison cards provides a genuine IDE-quality experience in the browser. The natural language search with entity extraction and route visualization is a feature typically found in enterprise BI tools. The status bar at the bottom completes the IDE metaphor.

### SF-5: Adaptive Kanban with Collapsible Columns
The mobile kanban implementation (MC lines 4377-4428) that collapses columns to tap-to-expand sections is a creative solution to a hard UX problem. Combined with the 2-column grid filter layout and the hidden-table/shown-cards approach, the mobile Mission Control experience is remarkably usable for what is inherently a wide-screen layout.

---

## 6. Top 5 Missing Features for World-Class UX

### MF-1: Keyboard Navigation / Accessibility Layer
**Impact: High**
Currently, there are no ARIA labels, role attributes, or skip-navigation links. Interactive elements lack `:focus-visible` styles. Screen reader support is absent. For a world-class product, WCAG 2.1 AA compliance is expected. Specific gaps:
- No `aria-label` on navigation buttons
- No `role="tablist"` / `role="tab"` on tab systems
- No skip-to-content link
- No screen reader announcements for dynamic content updates

### MF-2: Animation Performance Budget
**Impact: Medium**
Multiple continuous CSS animations run simultaneously: `pulse-glow` (8s loop), `float-ball` (20s loop), `rotate-bg` (20s loop), `pulse-guide` (2s loop), `founder-pulse` (2s loop), plus backdrop-filter on multiple elements. On lower-end mobile devices, this will cause frame drops. Needs:
- `will-change` property on animated elements
- `prefers-reduced-motion` query (mentioned in QW-7)
- Intersection Observer to pause off-screen animations

### MF-3: Data Visualization Charts (Beyond Tables)
**Impact: High**
The teams page uses tables and bar indicators but has no actual chart visualizations (no radar charts for player profiles, no line charts for form trends, no scatter plots for clustering results). For a data analytics product, this is the biggest gap. Consider:
- Radar/spider charts for player profiles
- Sparklines in table cells for form trends
- Heat maps for venue performance
- Distribution curves for pressure metrics

### MF-4: Micro-Interactions and State Transitions
**Impact: Medium**
While hover states are well-handled, there are no page transition animations, no tab-switch animations (content just appears/disappears with `display: none/block`), and no list reordering animations. Adding:
- CSS `view-transition-api` for page navigations
- `@starting-style` for element entry animations
- `transition` on opacity/transform for tab content switches
- Reflow animation for filter result changes

### MF-5: Print / Export Stylesheet
**Impact: Low-Medium**
For a pre-tournament preview magazine product, print styling is essential. Currently there are no `@media print` rules. Key needs:
- Hide navigation, background decorations, interactive elements
- Enforce white background with dark text
- Proper page break controls for team sections
- Stat pack formatting optimized for A4/Letter output

---

## 7. Overall Design Grade

| Dashboard | Visual Design | Typography | Color System | Mobile | Interaction | Overall |
|-----------|--------------|------------|-------------|--------|-------------|---------|
| **Lab - Home** | A | A- | A | B+ | B+ | **A-** |
| **Lab - Teams** | A | A | A | B+ | A- | **A** |
| **Lab - Film Room** | A | A | A | A- | A- | **A** |
| **MC - Boardroom** | A+ | A- | A | A- | A | **A** |

### Final Grades

| Dashboard | Grade |
|-----------|-------|
| **The Lab (aggregate)** | **A-** |
| **Mission Control** | **A** |

### Rationale
- **The Lab** loses points primarily for the minimum font size violations at extreme breakpoints and the lack of chart visualizations on a data analytics product. The home page intro animation being disabled also reduces the first-impression impact.
- **Mission Control** earns the higher grade for its innovative mobile kanban, the most thorough responsive design work, the best background theming, and the collapsible column system. The agent identity color system is a design innovation.

---

## Appendix: CSS Architecture Assessment

### Design System Consistency
- **CSS Variables:** 24 shared variables across all files. 100% consistent.
- **Font Stack:** Inter + system fallback. Consistent across all files.
- **Border Radius:** 8px (small), 10px (buttons), 12px (cards), 14px (columns), 16px (large cards), 20px (modals). Consistent scale.
- **Transition Timing:** `0.25s ease` standard. Some variations (0.15s, 0.3s) for specific components.
- **Shadow System:** `var(--shadow)` for consistent shadow opacity across themes.

### Code Quality
- Well-organized with section comment headers (e.g., `/* ==================== NAVIGATION ==================== */`).
- Ticket references in comments (TKT-109, TKT-110, TKT-111, TKT-175, TKT-200) -- excellent traceability.
- Tom Brady's UI/UX review notes are inline (e.g., "Tom Brady UI/UX Review - February 2026").
- No CSS specificity conflicts detected.
- Proper use of `backdrop-filter` with `-webkit-` prefix for Safari.

### Duplication Concerns
- The tooltip system (`.has-tooltip`) is duplicated identically across all 4 files (~30 lines each).
- The theme system (`:root` variables + `[data-theme="light"]`) is duplicated across all 4 files (~50 lines each).
- The navigation styles are duplicated with minor variations.
- **Recommendation:** If this product ever moves to a build system, extract shared CSS into a common stylesheet.

---

*This audit was conducted by reviewing all CSS and HTML source code across 26,891 total lines. No files were modified. All line references are accurate as of 2026-02-14.*

*Kevin de Bruyne -- Visualization Lead*
