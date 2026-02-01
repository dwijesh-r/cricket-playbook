# Task PRD: Predicted XI Algorithm

**Author**: Andy Flower (Cricket Domain Expert)
**Status**: FLORENTINO GATE APPROVED - Ready for Build
**Created**: 2026-02-01
**Founder Review**: 2026-02-01

---

## Gate Approvals

```
FLORENTINO GATE: APPROVED
Reason: Predicted XII directly removes substantial reader preparation burden with methodology
that differentiates from free punditry, and is a non-negotiable section for any credible IPL
preview publication.
Date: 2026-02-01
```

---

## Problem Statement

Readers want to know which XI each IPL team is likely to field—and why. Currently, predicted XIs are either:
1. **Pundit guesswork** - subjective, inconsistent, often wrong
2. **Fantasy-focused** - optimized for fantasy points, not match strategy
3. **Missing entirely** - leaving readers to speculate

A credible, data-driven Predicted XI adds significant editorial value to our tournament preview and establishes Cricket Playbook as analytically rigorous.

---

## Proposed Solution

Build an algorithm that:
1. Ingests each team's full squad with player attributes and metrics
2. Applies role-based selection logic (who fits which slot?)
3. Enforces hard constraints (overseas limit, bowling overs coverage)
4. Weights recent form, career baseline, and role-specific metrics
5. Outputs a ranked XI with batting order and bowling roles explained

**Methodology**: Constraint-satisfaction with weighted scoring
- First pass: Filter candidates by role eligibility
- Second pass: Apply metric-based scoring within each role
- Third pass: Optimize for balance (pace/spin, LHB/RHB, phase coverage)
- Final pass: Verify all constraints satisfied; if not, backtrack

---

## Success Criteria

| Criteria | Measurement |
|----------|-------------|
| Credibility | XI looks reasonable to cricket experts (no glaring omissions) |
| Explainability | Each selection has 1-2 sentence rationale |
| Constraint compliance | 100% adherence to overseas limit, bowling coverage |
| Coverage | Predicted XII generated for all 10 IPL teams |
| Accuracy target | **Aim for highest possible match rate to actual XIs** |

---

## Selection Philosophy

Real teams select XIs through a layered decision process:

### 1. Core Players (Non-negotiable)
- Franchise icons (Kohli at RCB, Rohit at MI, Dhoni legacy at CSK)
- High-value auction buys (teams protect investment)
- Match-winners with proven IPL records

### 2. Role Filling
- Teams don't pick "best 11 players" - they pick "best player for each role"
- A world-class No.3 doesn't solve a death bowling problem
- Specialists trump all-rounders for primary roles; all-rounders provide flexibility

### 3. Combination Optimization
- "This XI" vs "These 11 individuals"
- Bowling attack must cover 20 overs with variety
- Batting order must handle all game phases

### 4. Conditions & Opposition
- **FOUNDER DECISION**: Default XI + venue-specific pointers
- Show one primary Predicted XII per team
- Include section below with venue-specific adjustment recommendations
- Home venue analysis informs default selection (e.g., spin-friendly Chennai = consider extra spinner)

---

## Role Framework

A T20 XI requires these 11 slots filled. Players may qualify for multiple roles.

| # | Role | Primary Requirement | Secondary Requirements |
|---|------|---------------------|------------------------|
| 1 | Opener (Aggressor) | SR > 140 in powerplay | Boundary % > 60% |
| 2 | Opener (Anchor/Aggressor) | PP average > 30 | Can rotate strike |
| 3 | No.3 (Versatile) | Plays pace AND spin well | Recovers innings or accelerates |
| 4 | Middle-Order (Anchor) | Average > 35 in overs 7-15 | Can bat through |
| 5 | Middle-Order (Finisher) | SR > 150 in death overs | Handles pressure |
| 6 | Finisher/All-rounder | SR > 160 in death + bowling utility | 2+ overs capability |
| 7 | All-rounder (Bowling) | Economy < 8.5 + batting utility | Can bat 7-8 credibly |
| 8 | Specialist Spinner | Economy < 7.5 in middle overs | Wicket-taking ability |
| 9 | Pace Bowler (Variety) | Either: death specialist OR powerplay OR swing | Complements other pacers |
| 10 | Pace Bowler (Death) | Economy < 9 in overs 16-20 | Yorker/slower ball arsenal |
| 11 | Pace Bowler (Wicket-taker) | Strike rate < 20 | Powerplay impact |

**Note**: Wicketkeeper allocation is flexible—typically slots 1-6 include a keeper. Algorithm should flag if no keeper in XI.

---

## Balance Requirements

### Pace vs Spin Ratio
- **Standard balance**: 3 pace + 2 spin (or 3 pace + 1 spin + 1 pace-bowling all-rounder)
- **Home venue adjusted**:
  - Spin-friendly (Chennai, Kolkata): 2 pace + 3 spin
  - Pace-friendly (Mumbai, Bangalore): 4 pace + 1 spin acceptable
- **FOUNDER DECISION**: Home venue analysis influences default selection

### Left-Hand / Right-Hand Mix
- Ideal: 3-4 left-handers in top 7
- Minimum: 2 left-handers in XII
- Disrupts opposition bowling plans, forces line changes
- **Complementary focus**: Alternate LHB/RHB where possible in batting order

### Overseas Player Distribution
- **Hard limit**: Maximum 4 overseas in XI
- **Typical distribution**: 2 batters + 2 bowlers (or 1/3 or 3/1)
- Algorithm must handle teams with 8+ quality overseas options
- **Auction price signal**: High-value overseas players likely starters

### Phase Coverage Matrix

| Phase | Overs | Required Capabilities |
|-------|-------|----------------------|
| Powerplay | 1-6 | 2 new-ball bowlers, 2 aggressive openers |
| Middle | 7-15 | 1+ spinner mandatory, anchors batting |
| Death | 16-20 | 2 death-bowling specialists, finishers batting |

### Complementary Skills (Qualitative Overlay)
- **As a side**: Must be competent against both spin and pace
- **Bowling variety**: Different types (swing, pace, leg-spin, off-spin, left-arm)
- **Phase-wise solidity**: No gaps in any phase
- **Balance over talent**: If perfect balance unachievable, fit best available options

---

## Metric Weights

**FOUNDER DECISION**: Decent weight to recent form, but experience counts. Career baseline primary.

### Batters (by role)

| Metric | Opener | No.3-4 | Finisher (5-7) | Notes |
|--------|--------|--------|----------------|-------|
| Career T20 Average | 20% | 30% | 15% | Experience baseline |
| Career T20 SR | 30% | 20% | 25% | Role-appropriate |
| Last 2 season avg | 15% | 15% | 15% | Recent form |
| Last 2 season SR | 15% | 15% | 25% | Recent form |
| Phase-specific SR | 20% | 20% | 20% | Role fit |

### Bowlers (by role)

| Metric | Powerplay Spec | Middle Overs | Death Spec | Notes |
|--------|---------------|--------------|------------|-------|
| Career Economy | 25% | 35% | 30% | Experience baseline |
| Career Strike Rate | 30% | 20% | 20% | Role-appropriate |
| Last 2 season eco | 15% | 15% | 20% | Recent form |
| Last 2 season SR | 10% | 10% | 10% | Recent form |
| Phase-specific eco | 20% | 20% | 20% | Role fit |

### Experience Bonus
- Players with 50+ IPL matches: +5% to overall score
- Players with 100+ IPL matches: +10% to overall score
- Reflects "experience counts" principle

### All-rounders
- Weighted average of batting + bowling scores
- **FOUNDER DECISION**: Role-dependent weighting
  - Batting all-rounder (Hardik, Stoinis): 60% bat / 40% bowl
  - Bowling all-rounder (Jadeja, Axar): 40% bat / 60% bowl
  - True all-rounder (rare): 50% bat / 50% bowl
- Classification based on primary role in team context

---

## Constraints (Hard Rules)

These constraints MUST be satisfied. If violated, the XI is invalid.

| # | Constraint | Rule |
|---|-----------|------|
| C1 | Overseas limit | Maximum 4 overseas players |
| C2 | Bowling coverage | Minimum 5 players capable of bowling 4 overs each (20 total) |
| C3 | Wicketkeeper | At least 1 designated keeper in XI |
| C4 | Specialist bowlers | Minimum 4 players whose primary role is bowling |
| C5 | Spin minimum | **At least 1 spinner required** (2-3 for spin-friendly home venues) |

### Soft Constraints (Penalized but not fatal)

| # | Constraint | Penalty |
|---|-----------|---------|
| S1 | No left-handers in top 6 | -10% overall score |
| S2 | Only 1 death bowling option | -15% overall score |
| S3 | Captain not in XI | Flag for manual review |

---

## Edge Cases

### Injured/Unavailable Players
- **Input requirement**: Squad must have availability flags
- If flagged unavailable, player excluded from selection pool
- **FOUNDER DECISION**: No separate "fully fit" XI - show predicted XII based on available players only

### Debutants / Uncapped Players
- Limited data problem
- **Proposal**: Use domestic T20 data with 0.85x weight multiplier (domestic competition weaker)
- If no data: Exclude from algorithmic selection, flag for editorial override

### Form Slumps
- Player with poor last 10 matches but strong career
- **FOUNDER DECISION**: Decent weightage to recent form, but experience counts
- Apply "form factor" multiplier (0.85x - 1.15x based on recent vs career delta)
- Career baseline remains primary; recent form adjusts at margins
- Experienced players (50+ IPL matches) get stability bonus

### New Auction Signings
- Player in new team environment
- No team-specific data
- **Proposal**: Use overall career data, note "new signing - no team chemistry data"

### Impact Player Rule (IPL-specific)
- Teams can substitute a player mid-match
- **FOUNDER DECISION**: Predict 12-man squad (XI + Impact Player)
- Optimization criteria:
  - 5 solid bowling options minimum
  - 7-8 good batting options
  - Impact Player should complement starting XI (e.g., extra batting depth or bowling specialist)

---

## Scope

### In Scope (V1)
- **Predicted XII** for all 10 IPL teams (XI + Impact Player)
- Default XII with venue-specific adjustment pointers
- Batting order (1-11 + Impact)
- Bowling role assignments (who bowls when)
- Brief rationale for each selection
- Overseas player identification
- Captain/keeper designation
- Auction price consideration for selection priority
- Home venue analysis influence on selection

### Out of Scope (V1)
- Opposition-specific adjustments
- Match-by-match predictions
- Fantasy points optimization
- Confidence intervals on predictions
- "Best XI if fully fit" hypotheticals

### Future Considerations (V2+)
- Opposition-specific XI recommendations
- "If X is injured, who replaces?" scenarios
- Historical accuracy tracking (predicted vs actual)

---

## Dependencies

| Dependency | Status | Owner |
|------------|--------|-------|
| Squad data for all 10 teams | Required | Data Team |
| Player career T20 metrics | Required | Data Team |
| Phase-specific performance data | Required | Data Team |
| Last 2 seasons performance data | Required | Data Team |
| Player availability/injury flags | Required | Editorial Team |
| Overseas/domestic classification | Required | Data Team |
| Primary role classification | Required | **Algorithmic derivation + manual validation** |
| Auction price data | Required | Data Team (new) |
| Home venue characteristics | Required | Data Team (new) |

---

## Estimated Effort

**Large**

### Breakdown
| Component | Effort | Notes |
|-----------|--------|-------|
| Data schema design | Small | Define player attributes needed |
| Data collection/cleaning | Medium | 10 teams x 25 players x multiple metrics |
| Algorithm development | Medium | Constraint satisfaction + scoring |
| Balance optimization | Medium | Tricky edge cases |
| Rationale generation | Small | Template-based text |
| Editorial review workflow | Small | Human-in-the-loop for validation |
| Testing & validation | Medium | Compare to real team selections |

---

## Founder Decisions Summary

| Question | Decision |
|----------|----------|
| Accuracy target | Aim for highest possible |
| Venue specificity | Default XII + venue-specific pointers |
| All-rounder weighting | Role-dependent (batting AR: 60/40, bowling AR: 40/60) |
| Spin minimum | At least 1 spinner required |
| Form vs career | Decent weight to recent form, experience counts |
| Impact Player | Yes - 12-man squad (5 bowling, 7-8 batting options) |
| Role classification | Algorithmic + manual validation |
| Injured "best XI" | No - show available players only |

---

## Founder Additional Insights

### 1. Auction Price Signal
- **Principle**: Auction prices indicate franchise priorities
- Use auction price as directional signal for "core player" identification
- High auction value = likely starter (unless major form concerns)
- Helps identify first-choice 12 before optimization

### 2. Complementary Skills Focus
- **Principle**: Build team, not collection of stars
- Prioritize variety throughout the side:
  - LHB/RHB combinations in batting order
  - Competence against both spin and pace as a side
  - Bowling variety (pace variations, spin options)
  - Phase-wise solidity (not leaving gaps)
- This is a qualitative overlay on quantitative selection

### 3. Balance Over Talent
- **Principle**: If perfect balance isn't achievable, fit best available options
- Don't force suboptimal players to fill theoretical balance requirements
- A slightly unbalanced XI with better players > perfectly balanced XI with weaker players

### 4. Home Venue Influence
- **Principle**: Teams build squads for home conditions
- Analyze how team's home venue plays:
  - Spin-friendly (Chennai, Kolkata) → consider 2-3 spinners
  - Pace-friendly (Mumbai, Bangalore) → lean pace-heavy
  - Batting paradise → prioritize batting depth
- Home venue analysis should influence default XII selection

---

## Appendix: Example Role Fit Scoring

**Player**: Hardik Pandya
**Evaluating for**: Slot 6 (Finisher/All-rounder)

| Metric | Value | Weight | Weighted Score |
|--------|-------|--------|----------------|
| Death overs SR | 162 | 25% | 40.5 |
| Career batting SR | 147 | 20% | 29.4 |
| Last 2 season SR | 151 | 20% | 30.2 |
| Bowling economy | 8.9 | 20% | 17.8 (inverted) |
| Bowling capability | 4 overs | 15% | 15.0 |
| **Total Role Fit** | | | **82.9/100** |

This scoring approach ensures we're matching players to roles, not just picking highest overall ratings.

### Auction Price Influence

| Auction Price Tier | Selection Weight Bonus |
|--------------------|------------------------|
| ₹15+ Cr | +15% (franchise cornerstone) |
| ₹10-15 Cr | +10% (key player) |
| ₹5-10 Cr | +5% (important signing) |
| ₹2-5 Cr | No bonus |
| < ₹2 Cr | No bonus |

Auction price serves as directional signal for "first-choice 12" identification. High-value players are likely starters unless significant form/fitness concerns.

---

## Next Steps

1. **Florentino Gate**: Submit for commercial value validation
2. **Stephen Curry + Pep Guardiola**: Algorithm implementation
3. **Andy Flower**: Manual validation of algorithmic role classifications
4. **Domain Sanity Loop**: Jose Mourinho (robustness), Andy Flower (cricket truth), Pep Guardiola (coherence)
5. **Virat Kohli**: Editorial integration into stat packs

---

*PRD APPROVED - Founder Input Incorporated 2026-02-01*
*Ready for Florentino Gate (Step 1)*
