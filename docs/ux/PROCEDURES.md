# UI/UX Development Procedures

**Owner:** Kevin de Bruyne (UX/Frontend Lead)
**Last Updated:** 2026-02-07
**Version:** 1.0.0
**Ticket:** TKT-131

---

## Overview

This document defines the standard procedures for building, testing, and reviewing UI/UX for Cricket Playbook dashboards (The Boardroom, The Lab). Following these procedures ensures consistency, accessibility, and mobile-friendliness across all interfaces.

---

## 1. Design Principles

### 1.1 Dark-First Design

All dashboards are designed for **dark mode as the primary experience**.

| Principle | Implementation |
|-----------|----------------|
| **Background Hierarchy** | `--bg-primary` (darkest) → `--bg-secondary` → `--bg-tertiary` → `--bg-elevated` |
| **Text Contrast** | Primary text: white (#fff), Secondary: `--text-secondary` (#8e8e93) |
| **Accents** | Use `--accent` (#0a84ff) for interactive elements, system colors for states |
| **Light Mode** | Supported via `[data-theme="light"]` but dark is default |

```css
/* Always use CSS variables, never hardcode colors */
✅ background: var(--bg-secondary);
❌ background: #1c1c1e;
```

### 1.2 Mobile-First Development

Design for mobile first, then enhance for desktop.

| Breakpoint | Target | Priority |
|------------|--------|----------|
| 380px | Small phones (iPhone SE) | P0 - Must work |
| 480px | Standard phones | P0 - Must work |
| 600px | Large phones/small tablets | P0 - Must work |
| 768px | Tablets | P1 - Should work |
| 1024px | Desktop | P1 - Primary design |
| 1440px+ | Large desktop | P2 - Nice to have |

```css
/* Mobile-first: Start with mobile styles, add media queries for larger */
.card {
    padding: 12px;           /* Mobile default */
    font-size: 14px;
}

@media (min-width: 768px) {
    .card {
        padding: 20px;       /* Tablet+ enhancement */
        font-size: 16px;
    }
}
```

### 1.3 Information Hierarchy

Present information in order of importance:

```
Level 1: Critical (always visible)
    └── Key metrics, primary actions, navigation
Level 2: Important (visible on scroll/expand)
    └── Supporting data, secondary actions
Level 3: Detailed (hidden behind "Show More")
    └── Extended lists, historical data, technical details
```

**Cricket Example:** A player card should show current form metrics (Level 1), recent match performances (Level 2), and full career statistics (Level 3).

**Founder Guidance:** "On visuals over paragraphs - find a fine balance. Ensure enough context is given. Don't just put visuals for the sake of it."

### 1.4 Progressive Disclosure

Don't overwhelm users. Show essential content first, with option to expand.

| Pattern | When to Use | Implementation |
|---------|-------------|----------------|
| **Expandable sections** | Content groups (Related Links, Details) | See `components.md` |
| **Show More buttons** | Lists > 11 items | See `components.md` |
| **Tabs/Filters** | Multiple data views | Click to switch, don't load all |
| **Tooltips** | Abbreviations, metrics | Hover to reveal definition |

**Cricket-Specific Tooltips:** Common abbreviations requiring tooltips include SR (Strike Rate), Econ (Economy Rate), Ave (Average), BBI (Best Bowling in Innings), HS (Highest Score), and 4s/6s (boundaries).

---

## 2. Development Workflow

### 2.1 Pre-Development Checklist

Before writing any code:

- [ ] Ticket has clear `context.ask`, `context.goal`, `context.reason`
- [ ] Checked `docs/ux/components.md` for existing patterns
- [ ] Identified which breakpoints need testing
- [ ] Confirmed dark mode as primary design
- [ ] Identified any new CSS variables needed

### 2.2 Development Steps

```
1. STRUCTURE FIRST
   └── Write semantic HTML structure
   └── Use appropriate elements (<nav>, <main>, <section>, <article>)
   └── Add ARIA labels for accessibility

2. MOBILE STYLES
   └── Start with smallest breakpoint (380px)
   └── Use CSS variables from theme
   └── Test in browser at 380px width

3. RESPONSIVE ENHANCEMENT
   └── Add media queries for larger screens
   └── Test each breakpoint (480px, 600px, 768px, 1024px)
   └── Ensure nothing breaks at intermediate sizes

4. INTERACTIVE STATES
   └── Add hover states for clickable elements
   └── Add focus states for keyboard navigation
   └── Add transitions (0.2s ease standard)

5. DARK/LIGHT THEME
   └── Test in dark mode (primary)
   └── Test in light mode (if supported)
   └── Ensure contrast ratios are acceptable
```

### 2.3 CSS Architecture Rules

| Rule | Reason |
|------|--------|
| **Use CSS variables** | Enables theming, prevents hardcoded colors |
| **Embedded `<style>`** | Single-file HTML for portability (no server needed) |
| **BEM-lite naming** | `.component-element--modifier` for clarity |
| **Comment sections** | `/* ===== SECTION NAME ===== */` headers |
| **No !important** | Unless overriding third-party styles |
| **No inline styles** | Except for truly dynamic values (colors from data) |

#### Naming Convention Examples

**Component Classes (BEM-lite):**
```css
/* ==================== CARD COMPONENT ==================== */
.card { }                    /* Block */
.card-header { }             /* Element */
.card-body { }               /* Element */
.card-footer { }             /* Element */
.card--highlighted { }       /* Modifier */
.card--compact { }           /* Modifier */
```

**State Classes (is-* prefix):**
```css
.is-active { }               /* Currently selected/open */
.is-loading { }              /* Loading state */
.is-disabled { }             /* Disabled state */
.is-hidden { }               /* Visually hidden but in DOM */
.is-expanded { }             /* Expanded state for accordions */
.is-error { }                /* Error state */
```

**Utility Classes:**
```css
.sr-only {                   /* Screen reader only (accessibility) */
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}
.text-center { text-align: center; }
.text-muted { color: var(--text-tertiary); }
.mt-1 { margin-top: 8px; }   /* Spacing utilities */
.mb-2 { margin-bottom: 16px; }
```

**Theme-Specific Classes:**
```css
.theme-accent { color: var(--accent); }
.theme-success { color: var(--accent-green); }
.theme-warning { color: var(--accent-yellow); }
.theme-error { color: var(--accent-red); }
```

### 2.4 JavaScript Guidelines

| Rule | Reason |
|------|--------|
| **Vanilla JS only** | No frameworks, keeps files portable |
| **Functions at bottom** | After HTML, before closing `</body>` |
| **Event delegation** | Attach to parent, not individual elements |
| **No global pollution** | Use IIFE or module pattern if complex |

```javascript
// Good: Event delegation
document.querySelector('.list').addEventListener('click', (e) => {
    if (e.target.matches('.list-item')) {
        handleItemClick(e.target);
    }
});

// Avoid: Individual listeners on many elements
document.querySelectorAll('.list-item').forEach(item => {
    item.addEventListener('click', handleItemClick);
});
```

---

## 3. First Dashboard Walkthrough

**New to Cricket Playbook UI?** Follow this step-by-step example.

### Scenario: Add a New "Stats Card" to The Lab

**Step 1: Check Existing Patterns**
```bash
# Read the component library first
cat docs/ux/components.md

# Look at existing cards in The Lab
grep -A 20 "class=\"card\"" scripts/the_lab/dashboard/index.html
```

**Step 2: Copy Base HTML Structure**
```html
<!-- Copy this starter structure -->
<div class="card">
    <div class="card-header">
        <h3>Card Title</h3>
        <span class="help-icon has-tooltip" data-tooltip="Explanation here">ⓘ</span>
    </div>
    <div class="card-body">
        <!-- Your content here -->
    </div>
</div>
```

**Step 3: Copy Required CSS from components.md**

Open `docs/ux/components.md` and **literally copy-paste** the CSS you need:

```css
/* COPY FROM components.md -> Tooltip System section */
.has-tooltip { /* ... full CSS ... */ }
.has-tooltip::after { /* ... full CSS ... */ }
.help-icon { /* ... full CSS ... */ }

/* ADD your card-specific styles */
.stats-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}
```

**Step 4: Test Mobile First (380px)**
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Set width to 380px
4. Verify: No horizontal scroll, text readable, buttons tappable

**Step 5: Add Responsive Enhancements**
```css
/* Mobile default */
.stats-card { padding: 12px; }

/* Tablet+ */
@media (min-width: 768px) {
    .stats-card { padding: 20px; }
}
```

**Step 6: Test All Breakpoints**
- 380px ✓
- 480px ✓
- 600px ✓
- 768px ✓
- 1024px ✓

**Step 7: Self-Review Checklist**
- [ ] Uses CSS variables (no hardcoded colors)
- [ ] Hover states on interactive elements
- [ ] Tooltips on abbreviations
- [ ] Works at 380px width
- [ ] No console errors

**Step 8: Submit for Review**
```bash
git add .
git commit -m "feat(lab): Add stats card component"
# Request Kevin de Bruyne peer review
```

---

## 4. Testing Checklist

### 4.0 Standard Timing Values

Use these standard values for consistency:

| Property | Value | Use Case |
|----------|-------|----------|
| **Transition (fast)** | `0.15s ease` | Hover states, color changes |
| **Transition (normal)** | `0.2s ease` | Most interactions |
| **Transition (slow)** | `0.3s ease` | Expand/collapse, modals |
| **Animation (intro)** | `0.5s ease-out` | Page load animations |

### 4.1 Breakpoint Testing

Test at these exact widths in browser DevTools:

| Width | Device | Must Pass |
|-------|--------|-----------|
| 375px | iPhone SE | All content readable, no horizontal scroll |
| 390px | iPhone 14 | All content readable, no horizontal scroll |
| 430px | iPhone 14 Pro Max | All content readable |
| 600px | Small tablet | Layout adjusts, more spacing |
| 768px | iPad Mini | Desktop-like layout begins |
| 1024px | iPad Pro / Laptop | Full desktop experience |
| 1440px | Desktop | No overly stretched content |

### 4.2 Functional Testing

- [ ] All links work (no 404s)
- [ ] All buttons have visible hover/focus states
- [ ] All expandable sections open/close correctly
- [ ] Theme toggle works (if present)
- [ ] Search/filter works correctly
- [ ] Data loads without errors
- [ ] Console shows no JavaScript errors

### 4.3 Visual Testing

- [ ] Text is readable (sufficient contrast)
- [ ] Icons are visible against background
- [ ] No text overflow or truncation issues
- [ ] Images/charts scale appropriately
- [ ] Borders and shadows are subtle, not harsh
- [ ] Animations are smooth (60fps)

### 4.4 Accessibility Testing

| Check | How to Test |
|-------|-------------|
| **Keyboard navigation** | Tab through all interactive elements |
| **Focus visibility** | Focus ring visible on all focusable elements |
| **Screen reader** | VoiceOver/NVDA can read main content |
| **Color contrast** | 4.5:1 for normal text, 3:1 for large text |
| **Reduced motion** | Respects `prefers-reduced-motion` |

```css
/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## 5. Review Process

### 5.1 Self-Review (Developer)

Before requesting review:

1. Run through Testing Checklist (Section 3)
2. Verify all CSS uses variables (no hardcoded colors)
3. Check mobile at 380px and 600px
4. Verify hover states exist for all clickable elements
5. Test in both dark and light mode (if applicable)

### 5.2 Peer Review (Kevin de Bruyne)

UX Lead reviews for:

| Aspect | Questions |
|--------|-----------|
| **Consistency** | Does it match existing dashboard patterns? |
| **Components** | Are reusable patterns from `components.md` used? |
| **Mobile** | Does it work on small screens? |
| **Accessibility** | Can keyboard users navigate? |
| **Performance** | No unnecessary animations or large assets? |

### 5.3 Domain Review (Andy Flower)

Cricket domain expert reviews for:

- Correct use of cricket terminology
- Appropriate metrics shown for context
- Logical information hierarchy for cricket users

### 5.4 Founder Review

Final approval focuses on:

- Overall user experience
- Information balance (not too sparse, not overwhelming)
- Alignment with product vision

---

## 6. File Structure

```
scripts/
├── mission_control/
│   └── dashboard/
│       ├── index.html       # The Boardroom (main dashboard)
│       ├── sprints.html     # Sprint history view
│       └── about.html       # About/help page
├── the_lab/
│   └── dashboard/
│       ├── index.html       # The Lab (analytics hub)
│       ├── teams.html       # Team explorer
│       ├── research.html    # Research hub
│       ├── analysis.html    # Analysis tools
│       └── artifacts.html   # Artifacts gallery

docs/ux/
├── PROCEDURES.md            # This document
├── components.md            # Reusable CSS patterns
└── TKT-108_dashboard_ux_research.md  # UX research findings
```

---

## 7. CSS Variables Reference

All dashboards must use these variables (defined in each HTML file):

```css
:root {
    /* Backgrounds (dark mode) */
    --bg-primary: #000000;
    --bg-secondary: #1c1c1e;
    --bg-tertiary: #2c2c2e;
    --bg-elevated: #3a3a3c;

    /* Text */
    --text-primary: #ffffff;
    --text-secondary: #8e8e93;
    --text-tertiary: #636366;

    /* Accents (Apple system colors) */
    --accent: #0a84ff;        /* Blue - primary actions */
    --accent-green: #30d158;  /* Success states */
    --accent-yellow: #ffd60a; /* Warnings, highlights */
    --accent-orange: #ff9f0a; /* Attention */
    --accent-red: #ff453a;    /* Errors, critical */
    --accent-purple: #bf5af2; /* Special features */
    --accent-teal: #64d2ff;   /* Info states */

    /* Effects */
    --border: rgba(255, 255, 255, 0.1);
    --shadow: rgba(0, 0, 0, 0.4);
    --blur: blur(20px);
}

/* Light mode overrides */
[data-theme="light"] {
    --bg-primary: #f5f5f7;
    --bg-secondary: #ffffff;
    --bg-tertiary: #e5e5e7;
    --bg-elevated: #ffffff;
    --text-primary: #1d1d1f;
    --text-secondary: #86868b;
    --text-tertiary: #aeaeb2;
    --border: rgba(0, 0, 0, 0.1);
    --shadow: rgba(0, 0, 0, 0.1);
}
```

---

## 8. Common Patterns Quick Reference

### Buttons
```css
.btn {
    background: var(--accent);
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.btn:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
}
```

### Cards
```css
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}
```

### Tables
```css
.table {
    width: 100%;
    border-collapse: collapse;
}
.table th, .table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.table th {
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}
```

---

## 9. Changelog

### v1.0.0 (2026-02-07)
- Initial release
- Design principles documented
- Development workflow defined
- Testing checklist created
- Review process established
- CSS variables reference added

---

*Kevin de Bruyne - UX/Frontend Lead*
*Cricket Playbook v4.1.0*
