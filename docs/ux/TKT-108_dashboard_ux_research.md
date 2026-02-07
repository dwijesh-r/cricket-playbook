# TKT-108: Dashboard UX Research

**Owner:** Kevin de Bruyne (UX/Frontend Lead)
**Date:** 2026-02-07
**Status:** RESEARCH COMPLETE

---

## Executive Summary

After auditing all Cricket Playbook dashboards, I found a **solid foundation** with professional CSS architecture. The dashboards use proper CSS custom properties, theme systems, and modern patterns. Here are my top recommendations:

| Priority | Recommendation | Impact |
|----------|---------------|--------|
| P0 | Add progressive disclosure (expandable sections) | High - Reduce initial cognitive load |
| P1 | Add contextual tooltips for metrics | High - Improve understanding |
| P1 | Replace text blocks with visual indicators | Medium - Faster comprehension |
| P2 | Implement shared CSS file to reduce duplication | Medium - Maintenance improvement |

---

## 1. CSS/JS Architecture Audit

### Current State: ✅ GOOD

**The dashboards use REAL CSS**, not inline styles. Here's what I found:

| Dashboard | Style Type | Lines of CSS | Inline Styles |
|-----------|------------|--------------|---------------|
| The Lab (index.html) | Embedded `<style>` | ~2000+ | 10 (minimal) |
| Teams | Embedded `<style>` | ~800 | 34 (for dynamic colors) |
| Analysis | Embedded `<style>` | ~600 | 6 (minimal) |
| Mission Control | Embedded `<style>` | ~1500+ | 23 (for chart colors) |

### Architecture Strengths:
```css
/* CSS Custom Properties - Proper theming */
:root {
    --bg-primary: #000000;
    --accent: #0a84ff;
    --border: rgba(255, 255, 255, 0.1);
}

[data-theme="light"] {
    --bg-primary: #f5f5f7;
    /* Full light theme support */
}
```

- ✅ CSS custom properties (variables) for consistent theming
- ✅ Dark/light theme system via `[data-theme]` attribute
- ✅ Well-organized sections with comment headers
- ✅ Modern CSS: `backdrop-filter`, gradients, animations
- ✅ Inter font family with proper weight scale (300-800)

### Why Embedded CSS (Not External)?
**Intentional for portability.** Single-file HTML dashboards can be:
- Opened anywhere without a server
- Shared via email/Slack as standalone files
- Work offline without asset loading

### Recommendation: Shared Variables File
Create a `shared-theme.css` that can be embedded or linked:
```
docs/ux/shared-theme.css  (reference for copy-paste into dashboards)
```

---

## 2. Cognitive Load Reduction

### Current Issues Identified:

1. **Information Density**: Some sections show all data at once
2. **No Visual Breathing Room**: Cards packed tightly in grids
3. **Text-Heavy Sections**: Paragraphs where bullets would suffice

### Recommendations:

#### 2.1 Information Chunking
```
BEFORE: 10 metrics visible at once
AFTER:  3 key metrics visible, "Show More" expands to remaining 7
```

#### 2.2 Whitespace Guidelines
| Element | Current | Recommended |
|---------|---------|-------------|
| Card padding | 16px | 20-24px |
| Section gap | 24px | 32-40px |
| Grid gap | 16px | 20px |

#### 2.3 Visual Breathing Room Pattern
```css
/* Add to card components */
.stat-card {
    padding: 24px;
    margin-bottom: 8px;  /* Micro-gap between cards */
}

.section {
    padding: 40px 0;
    border-bottom: 1px solid var(--border);
}
```

---

## 3. Visual Hierarchy Enhancement

### Current Typography Scale (Good Foundation):
```css
/* Already in place - well designed */
.page-title     { font-size: 42px; font-weight: 800; }
.section-title  { font-size: 18px; font-weight: 700; }
.card-title     { font-size: 15px; font-weight: 600; }
.stat-value     { font-size: 28px; font-weight: 700; }
.stat-label     { font-size: 11px; font-weight: 600; }
```

### Recommendations:

#### 3.1 Color Hierarchy for Importance
```css
/* Priority-based coloring */
.metric-critical { color: var(--accent-red); }     /* P0 alerts */
.metric-warning  { color: var(--accent-yellow); }  /* P1 attention */
.metric-success  { color: var(--accent-green); }   /* Good state */
.metric-info     { color: var(--accent); }         /* Neutral info */
```

#### 3.2 Depth Through Elevation
```css
/* Card prominence levels */
.card-elevated   { background: var(--bg-elevated); }  /* Focus item */
.card-secondary  { background: var(--bg-secondary); } /* Normal */
.card-tertiary   { background: var(--bg-tertiary); }  /* De-emphasized */
```

---

## 4. Visuals Over Text

### Opportunities Identified:

| Location | Current | Recommended Visual |
|----------|---------|-------------------|
| Player archetypes | Text description | Icon + 1-line label |
| Batting position | "Opens for MI" | Position indicator bar |
| Phase performance | Paragraph | Sparkline mini-chart |
| Cluster membership | Text label | Colored dot + badge |
| Win/Loss record | "5W 3L" | Visual W/L streak bar |

### Implementation Examples:

#### 4.1 Sparkline for Trends
```html
<div class="sparkline">
    <svg viewBox="0 0 60 20">
        <polyline points="0,15 10,12 20,8 30,14 40,6 50,10 60,4" />
    </svg>
</div>
```

#### 4.2 Phase Performance Bars
```html
<div class="phase-bars">
    <div class="bar pp" style="--value: 85%"></div>   <!-- Powerplay -->
    <div class="bar mid" style="--value: 72%"></div>  <!-- Middle -->
    <div class="bar death" style="--value: 91%"></div><!-- Death -->
</div>
```

#### 4.3 Archetype Icons
| Archetype | Icon | Color |
|-----------|------|-------|
| Power Hitter | ⚡ | var(--accent-yellow) |
| Anchor | ⚓ | var(--accent-teal) |
| Finisher | 🎯 | var(--accent-green) |
| All-Rounder | 🔄 | var(--accent-purple) |
| Specialist | 🎪 | var(--accent-orange) |

---

## 5. Progressive Disclosure

### Pattern Recommendations:

#### 5.1 Summary → Detail Flow
```
┌─────────────────────────────────────────┐
│ Player: Virat Kohli           SR: 142.5 │
│ Archetype: Anchor                       │
│ [▼ Show Details]                        │
└─────────────────────────────────────────┘

Expanded:
┌─────────────────────────────────────────┐
│ Player: Virat Kohli           SR: 142.5 │
│ Archetype: Anchor                       │
│ ─────────────────────────────────────── │
│ Phase Performance:                      │
│   PP: 128.4  │  Mid: 145.2  │  Death: 162│
│ Recent Form: ████████░░ (8/10 matches)  │
│ vs Pace: 148.2  │  vs Spin: 138.1       │
│ [▲ Hide Details]                        │
└─────────────────────────────────────────┘
```

#### 5.2 Tabbed Interface for Categories
```html
<div class="tab-group">
    <button class="tab active">Overview</button>
    <button class="tab">Phase Analysis</button>
    <button class="tab">Matchups</button>
    <button class="tab">History</button>
</div>
```

#### 5.3 Drill-Down Cards
```
Team Card (Collapsed) → Player List → Player Detail Modal
```

### CSS Pattern for Expandable Sections:
```css
.expandable-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.expandable.open .expandable-content {
    max-height: 500px;  /* Adjust per content */
}

.expand-toggle {
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
}

.expand-toggle::after {
    content: '▼';
    font-size: 10px;
    transition: transform 0.3s ease;
}

.expandable.open .expand-toggle::after {
    transform: rotate(180deg);
}
```

---

## 6. Contextual Tooltips

### Design System:

#### 6.1 Tooltip Styling
```css
.tooltip {
    position: relative;
    cursor: help;
}

.tooltip::before {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 8px 12px;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    z-index: 1000;
}

.tooltip:hover::before {
    opacity: 1;
    visibility: visible;
    bottom: calc(100% + 8px);
}
```

#### 6.2 Metric Glossary
| Metric | Tooltip Text |
|--------|--------------|
| SR | Strike Rate: Runs scored per 100 balls faced |
| Avg | Batting Average: Runs per dismissal |
| Econ | Economy Rate: Runs conceded per over |
| PP | Powerplay: Overs 1-6 with fielding restrictions |
| Death | Death Overs: Overs 16-20, highest pressure phase |

#### 6.3 Help Icon Pattern
```html
<span class="stat-label">
    Strike Rate
    <span class="help-icon tooltip" data-tooltip="Runs per 100 balls">ⓘ</span>
</span>
```

---

## Implementation Priority Matrix

| Recommendation | Effort | Impact | Priority | Owner |
|---------------|--------|--------|----------|-------|
| Add expandable sections | Medium | High | P0 | Kevin de Bruyne |
| Contextual tooltips | Low | High | P1 | Kevin de Bruyne |
| Phase performance bars | Low | Medium | P1 | Kevin de Bruyne |
| Sparklines for trends | Medium | Medium | P2 | Stephen Curry |
| Shared CSS variables file | Low | Low | P2 | Kevin de Bruyne |
| Tab interface for categories | Medium | Medium | P3 | Kevin de Bruyne |

---

## Quick Wins (Implement This Week)

### 1. Add Tooltips to Existing Metrics
```javascript
// Add to any dashboard
document.querySelectorAll('[data-metric]').forEach(el => {
    const glossary = {
        'sr': 'Runs per 100 balls faced',
        'avg': 'Runs per dismissal',
        'econ': 'Runs conceded per over',
        'pp': 'Powerplay: Overs 1-6',
        'death': 'Death overs: 16-20'
    };
    el.setAttribute('data-tooltip', glossary[el.dataset.metric]);
    el.classList.add('tooltip');
});
```

### 2. Progressive Disclosure Toggle
```javascript
document.querySelectorAll('.expand-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
        toggle.closest('.expandable').classList.toggle('open');
    });
});
```

---

## Appendix: Dashboard Inventory

| Dashboard | Path | Size | Purpose |
|-----------|------|------|---------|
| The Lab Main | `scripts/the_lab/dashboard/index.html` | 156KB | Main entry with intro animation |
| Teams | `scripts/the_lab/dashboard/teams.html` | 45KB | IPL team rosters |
| Analysis | `scripts/the_lab/dashboard/analysis.html` | 28KB | Deep dive analytics |
| Artifacts | `scripts/the_lab/dashboard/artifacts.html` | 22KB | Output files browser |
| Research | `scripts/the_lab/dashboard/research.html` | 18KB | Research docs |
| About | `scripts/the_lab/dashboard/about.html` | 12KB | Project info |
| Mission Control | `scripts/mission_control/dashboard/index.html` | 180KB | Sprint management |
| MC Sprints | `scripts/mission_control/dashboard/sprints.html` | 15KB | Sprint history |
| MC About | `scripts/mission_control/dashboard/about.html` | 10KB | Team info |

---

*Kevin de Bruyne - UX/Frontend Lead*
