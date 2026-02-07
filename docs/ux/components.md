# UX Component Library

**Owner:** Kevin de Bruyne (UX/Frontend Lead)
**Last Updated:** 2026-02-07
**Status:** Living Document

---

## Overview

This document describes reusable UX patterns implemented across Cricket Playbook dashboards. All patterns are CSS-only (no JavaScript frameworks) for portability.

---

## 1. Tooltip System (TKT-109)

### Purpose
Provide contextual explanations for cricket metrics without cluttering the UI.

### CSS (Copy to any dashboard)
```css
/* ==================== TOOLTIP SYSTEM ==================== */
.has-tooltip {
    position: relative;
    cursor: help;
}
.has-tooltip::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: calc(100% + 8px);
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
    pointer-events: none;
    box-shadow: 0 4px 12px var(--shadow);
}
.has-tooltip:hover::after {
    opacity: 1;
    visibility: visible;
}
.help-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    font-size: 10px;
    color: var(--text-tertiary);
    cursor: help;
    margin-left: 4px;
    vertical-align: middle;
}
.help-icon:hover { color: var(--accent); }

/* Mobile-safe adjustments */
@media (max-width: 768px) {
    .has-tooltip::after {
        white-space: normal;
        max-width: 200px;
        left: 0;
        transform: none;
        font-size: 11px;
    }
}
@media (max-width: 480px) {
    .has-tooltip::after {
        max-width: 160px;
        padding: 6px 10px;
        font-size: 10px;
    }
}
```

### Usage
```html
<!-- On any element -->
<th class="has-tooltip" data-tooltip="Strike Rate: Runs per 100 balls">SR</th>

<!-- With help icon -->
<span class="stat-label">
    Economy
    <span class="help-icon has-tooltip" data-tooltip="Runs conceded per over">ⓘ</span>
</span>
```

### Cricket Glossary
| Metric | Tooltip Text |
|--------|-------------|
| SR | Strike Rate: Runs scored per 100 balls faced |
| Avg | Batting Average: Runs per dismissal |
| Econ | Economy Rate: Runs conceded per over |
| PP | Powerplay: Overs 1-6 with fielding restrictions |
| Death | Death Overs: Overs 16-20, highest pressure phase |
| Overseas | Non-Indian players (max 4 can play in XI) |
| Archetype | Player archetype from clustering analysis |

---

## 2. Progressive Disclosure (TKT-110)

### Purpose
Reduce cognitive load by showing essential content first, with option to expand.

### CSS
```css
/* ==================== PROGRESSIVE DISCLOSURE ==================== */
/* Extended rows (hidden by default) */
.extended-squad-row {
    display: none;
}
.extended-squad-row.show {
    display: table-row;
}

/* Show More button container */
.show-more-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 20px;
    border-top: 1px dashed var(--border);
    margin-top: 8px;
}

.show-more-btn {
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
    border: 1px solid var(--border);
    color: var(--accent);
    padding: 12px 24px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s ease;
    font-family: inherit;
}

.show-more-btn:hover {
    background: linear-gradient(135deg, rgba(10, 132, 255, 0.15) 0%, rgba(191, 90, 242, 0.15) 100%);
    border-color: var(--accent);
    transform: translateY(-2px);
}

.show-more-hint {
    font-size: 12px;
    color: var(--text-tertiary);
}

/* Toggle state */
.squad-expanded .extended-squad-row {
    display: table-row;
}
.squad-expanded .show-more-text {
    display: none !important;
}
.squad-expanded .show-less-text {
    display: inline !important;
}
.squad-expanded .show-more-hint {
    display: none;
}
```

### JavaScript
```javascript
function toggleExtendedSquad() {
    const squadContent = document.getElementById('squad-content');
    squadContent.classList.toggle('squad-expanded');
}
```

### Usage Pattern
```html
<!-- Row with conditional class -->
<tr class="${idx >= 11 ? 'extended-squad-row' : ''}">...</tr>

<!-- Show More button (only if more than 11 items) -->
${items.length > 11 ? `
<div class="show-more-container">
    <button class="show-more-btn" onclick="toggleExtendedSquad()">
        <span class="show-more-text">Show More (+${items.length - 11})</span>
        <span class="show-less-text" style="display: none;">Show Less</span>
    </button>
    <span class="show-more-hint">Currently showing top 11</span>
</div>
` : ''}
```

### Best Practices
- Show the most important items first (e.g., Predicted XI)
- Include count of hidden items in button text
- Provide context hint explaining what's shown

---

## 3. Phase Indicators (TKT-111)

### Purpose
Visual representation of player phase specialization (Powerplay, Middle, Death).

### CSS
```css
/* ==================== PHASE INDICATORS ==================== */
.phase-bars {
    display: flex;
    gap: 4px;
    align-items: center;
}

.phase-tag {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.phase-tag.pp-elite {
    background: rgba(255, 214, 10, 0.2);
    color: var(--accent-yellow);
}
.phase-tag.mid-elite {
    background: rgba(10, 132, 255, 0.2);
    color: var(--accent);
}
.phase-tag.death-elite {
    background: rgba(255, 69, 58, 0.2);
    color: var(--accent-red);
}
.phase-tag.neutral {
    background: var(--bg-tertiary);
    color: var(--text-tertiary);
}
```

### Usage
```javascript
// Derive phase from player tags
const allTags = [...(player.batterTags || []), ...(player.bowlerTags || [])];
const isPP = allTags.some(t => t.includes('PP_') || t === 'NEW_BALL_SPECIALIST');
const isMid = allTags.some(t => t.includes('MIDDLE') || t.includes('MID_'));
const isDeath = allTags.some(t => t.includes('DEATH') || t === 'FINISHER');

// Render phase tags
const phaseHtml = `
    <div class="phase-bars">
        ${isPP ? '<span class="phase-tag pp-elite has-tooltip" data-tooltip="Powerplay specialist (Overs 1-6)">PP</span>' : ''}
        ${isMid ? '<span class="phase-tag mid-elite has-tooltip" data-tooltip="Middle overs specialist (Overs 7-15)">MID</span>' : ''}
        ${isDeath ? '<span class="phase-tag death-elite has-tooltip" data-tooltip="Death overs specialist (Overs 16-20)">DTH</span>' : ''}
    </div>
`;
```

### Phase Tag Mapping
| Tag Pattern | Phase | Color |
|-------------|-------|-------|
| PP_*, NEW_BALL_SPECIALIST, EXPLOSIVE_OPENER | PP (Powerplay) | Yellow |
| MIDDLE*, MID_*, ACCUMULATOR, ANCHOR | MID (Middle) | Blue |
| DEATH*, FINISHER | DTH (Death) | Red |

---

## 4. Expandable Sections (General Pattern)

### Purpose
Allow users to show/hide content sections.

### CSS
```css
.expandable {
    overflow: hidden;
}
.expandable-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    padding: 12px 16px;
    background: var(--bg-tertiary);
    border-radius: 8px;
    transition: all 0.2s ease;
    user-select: none;
}
.expandable-header:hover {
    background: var(--bg-elevated);
}
.expand-icon {
    font-size: 12px;
    color: var(--text-tertiary);
    transition: transform 0.3s ease;
}
.expandable.open .expand-icon {
    transform: rotate(180deg);
}
.expandable-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, padding 0.3s ease;
    padding: 0 16px;
}
.expandable.open .expandable-content {
    max-height: 500px;
    padding: 16px;
}
```

### Usage
```html
<div class="expandable" onclick="this.classList.toggle('open')">
    <div class="expandable-header">
        <h4>Section Title</h4>
        <span class="expand-icon">▼</span>
    </div>
    <div class="expandable-content">
        <!-- Content here -->
    </div>
</div>
```

---

## Theme Variables Reference

All components use these CSS custom properties:

```css
:root {
    /* Backgrounds */
    --bg-primary: #000000;
    --bg-secondary: #1c1c1e;
    --bg-tertiary: #2c2c2e;
    --bg-elevated: #3a3a3c;

    /* Text */
    --text-primary: #ffffff;
    --text-secondary: #8e8e93;
    --text-tertiary: #636366;

    /* Accents */
    --accent: #0a84ff;
    --accent-green: #30d158;
    --accent-yellow: #ffd60a;
    --accent-orange: #ff9f0a;
    --accent-red: #ff453a;
    --accent-purple: #bf5af2;
    --accent-teal: #64d2ff;

    /* Borders & Effects */
    --border: rgba(255, 255, 255, 0.1);
    --shadow: rgba(0, 0, 0, 0.4);
}
```

---

## Implementation Checklist

When adding a new component:

1. [ ] Uses existing CSS variables (no hardcoded colors)
2. [ ] Works in both dark and light themes
3. [ ] Has hover states for interactive elements
4. [ ] Includes tooltips for any abbreviations
5. [ ] Mobile responsive (tested at 600px, 380px)
6. [ ] No external dependencies (pure CSS/JS)
7. [ ] Documented in this file

---

*Kevin de Bruyne - UX/Frontend Lead*
