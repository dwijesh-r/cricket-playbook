# Predicted XII Algorithm Specification - Version 2.0

**Authors:** Andy Flower (Cricket Domain Expert), Stephen Curry (Analytics Lead)
**Version:** 2.0
**Last Updated:** 2026-02-04
**Status:** FORMAL SPECIFICATION
**Binding Input:** Sprint 4 Check-In (Founder)

---

## 1. Algorithm Overview

### 1.1 Purpose

The Predicted XII Algorithm generates an optimal Playing XI plus one Impact Player for each IPL 2026 team. The algorithm balances statistical evidence with cricket-specific constraints to produce tactically sound team selections.

### 1.2 Design Philosophy

> **Founder Mandate:** "Competency over variety - favor proven performers while maintaining tactical balance."

The algorithm prioritizes:
1. **Competency (65%)** - Selection weighted toward players with proven performance metrics
2. **Variety (35%)** - Team composition balance (LHB/RHB, pace/spin distribution)

### 1.3 Cricket Context (Andy Flower Notes)

In T20 cricket, the best XI is rarely the eleven most talented individuals. Success requires:
- **Role clarity**: Each player must understand their function
- **Phase coverage**: Batting depth across powerplay, middle, and death overs
- **Bowling completeness**: The ability to bowl 20 overs without a weakness
- **Matchup flexibility**: Balance of left/right batters to disrupt bowling plans

This algorithm encodes these principles mathematically while respecting IPL-specific rules.

---

## 2. Selection Weight Formula

### 2.1 Primary Formula

```
SELECTION_SCORE = (COMPETENCY_SCORE * 0.65) + (VARIETY_SCORE * 0.35)
```

### 2.2 Competency Score Components

The competency score evaluates proven performance:

```
COMPETENCY_SCORE = BASE_SCORE + CLASSIFICATION_BONUS + TAG_BONUS + PRICE_MODIFIER

Where:
- BASE_SCORE = 50 (batters) or 40 (bowlers)
- CLASSIFICATION_BONUS = Archetype-based modifier (0-30 points)
- TAG_BONUS = Phase-specific tag bonuses (cumulative)
- PRICE_MODIFIER = (1 + AUCTION_TIER_BONUS) multiplier
```

#### 2.2.1 Classification Bonus Table (Batters)

| Classification | Bonus | Cricket Rationale |
|---------------|-------|-------------------|
| Elite Top-Order | +30 | Proven ability to set platform and accelerate |
| Power Finisher | +25 | Death-overs execution is the hardest skill in T20 |
| Aggressive Opener | +25 | Powerplay exploitation creates match-winning momentum |
| All-Round Finisher | +20 | Dual utility in death overs (bat + bowl) |
| Anchor | +15 | Stability value, though less critical in modern T20 |

#### 2.2.2 Classification Bonus Table (Bowlers)

| Classification | Bonus | Cricket Rationale |
|---------------|-------|-------------------|
| Powerplay Assassin | +25 | New ball wickets set the tone for the innings |
| Middle-Overs Spinner | +25 | Overs 7-15 control is the cheapest economy zone |
| Workhorse Seamer | +20 | Versatility across phases has immense squad value |
| Holding Spinner | +15 | Useful but not match-winning in isolation |
| Expensive Option | +5 | Fifth bowler necessity, not choice |

#### 2.2.3 Tag Bonus System

| Tag Category | Tag | Bonus | Cricket Context |
|--------------|-----|-------|-----------------|
| **Batter - Powerplay** | EXPLOSIVE_OPENER | +10 | Sub-20 SR in PP1 is elite |
| | PP_DOMINATOR | +8 | Consistent PP scoring above 140 SR |
| **Batter - Death** | FINISHER | +12 | SR 160+ in overs 16-20 is rare |
| | DEATH_SPECIALIST | +10 | Proven closing ability under pressure |
| | SIX_HITTER | +8 | Boundary % above 15% at death |
| **Batter - Middle** | MIDDLE_OVERS_ACCELERATOR | +7 | SR 130+ in overs 7-15 |
| | ANCHOR | +5 | Dot ball % below 30% with SR 120+ |
| **Bowler - Powerplay** | PP_ELITE | +12 | Economy below 7.0 in PP |
| | PP_STRIKE | +12 | Wickets per innings above 0.8 in PP |
| | NEW_BALL_SPECIALIST | +10 | Historical new ball success |
| | PP_LIABILITY | -8 | Economy above 9.0 in PP |
| **Bowler - Middle** | MIDDLE_STRANGLER | +10 | Economy below 6.5 in overs 7-15 |
| | MID_OVERS_ELITE | +10 | Dot ball % above 45% |
| | MIDDLE_WICKET_TAKER | +8 | Strike rate below 20 in middle |
| | MIDDLE_LIABILITY | -5 | Economy above 8.5 in middle |
| **Bowler - Death** | DEATH_ELITE | +15 | Economy below 9.0 at death is exceptional |
| | DEATH_STRIKE | +12 | Death wicket-taking ability |
| | DEATH_CONTAINER | +8 | Economy below 10.0 at death |
| | DEATH_COMPLETE | +12 | Both strike and contain at death |
| | DEATH_LIABILITY | -8 | Economy above 11.0 at death |
| **Bowler - Matchup** | RHB_SPECIALIST | +3 | Demonstrated handedness advantage |
| | LHB_SPECIALIST | +3 | Demonstrated handedness advantage |
| | RHB_WICKET_TAKER | +5 | High wicket rate vs RHB |
| | LHB_WICKET_TAKER | +5 | High wicket rate vs LHB |

#### 2.2.4 Auction Price Modifier

| Price Tier (Cr) | Modifier | Rationale |
|-----------------|----------|-----------|
| 15.0+ | +15% | Franchise cornerstone investment |
| 10.0 - 14.99 | +10% | Key player category |
| 5.0 - 9.99 | +5% | Squad core player |
| < 5.0 | 0% | No modifier |

**Cricket Context:** Auction price reflects franchise confidence and creates a "soft" experience proxy when other signals are weak.

### 2.3 Variety Score Components

The variety score ensures tactical balance:

```
VARIETY_SCORE = LHB_RHB_BALANCE + PACE_SPIN_BALANCE + PHASE_COVERAGE

Where:
- LHB_RHB_BALANCE: 0-40 points (optimal: 2-3 LHB in top 6)
- PACE_SPIN_BALANCE: 0-30 points (optimal: 2-3 spinners based on venue)
- PHASE_COVERAGE: 0-30 points (all three phases covered by bowlers)
```

#### 2.3.1 LHB/RHB Balance Scoring

| LHB in Top 6 | Score | Cricket Rationale |
|--------------|-------|-------------------|
| 0 | 10 | Predictable for RH bowlers, but not fatal |
| 1 | 25 | Minimal disruption |
| 2 | 40 | Optimal - forces bowling changes |
| 3 | 35 | Good balance |
| 4+ | 20 | Over-indexed on variety |

**Cricket Context:** Left-handers disrupt right-arm bowler angles and spin direction. Having 2-3 in the top 6 forces bowlers to constantly adjust, creating uncertainty in their plans.

#### 2.3.2 Pace/Spin Balance by Venue

| Venue Bias | Optimal Spinners | Rationale |
|------------|------------------|-----------|
| Spin (Chennai, Kolkata) | 2-3 | Surface assists turn, grip |
| Pace (Mumbai, Bengaluru, Hyderabad) | 1-2 | Bounce and pace assist seamers |
| Neutral | 2 | Balanced approach |

---

## 3. Hard Constraints (Enforcement Rules)

### 3.1 Constraint C1: Captains Cannot Be Impact Players

**Rule:** The designated team captain is EXCLUDED from impact player selection.

**Implementation:**
```python
if player.is_captain:
    player.impact_eligible = False
```

**IPL Rule Reference:** IPL 2025+ regulations prohibit the captain from being substituted mid-match as an Impact Player.

**Cricket Context:** The captain's tactical value extends beyond individual performance. Their on-field decision-making, bowler management, and field placement cannot be replicated by a substitute.

### 3.2 Constraint C2: Maximum 4 Overseas Players

**Rule:** The XI (not including Impact Player) must contain no more than 4 overseas players.

**Implementation:**
```python
overseas_count = sum(1 for p in xi if p.is_overseas)
if overseas_count > 4:
    CONSTRAINT_VIOLATED
```

**Exception for Impact Player:** An overseas Impact Player can be selected even if XI has 4 overseas, but the substitution must replace an overseas player.

**Cricket Context:** This is an IPL regulation designed to ensure Indian player development and representation.

### 3.3 Constraint C3: Maximum 2 Roles Per Player in Depth Charts

**Rule:** Any individual player should appear in no more than 2 positions across all depth charts.

**Rationale:** A player appearing in 5+ positions (e.g., Nicholas Pooran in Opener, Middle-Order, Finisher, Wicketkeeper, Impact Player) dilutes the utility of the depth chart.

**Implementation:**
```python
for player in squad:
    role_count = count_depth_chart_appearances(player)
    if role_count > 2:
        reduce_to_primary_two_roles(player)
```

**Selection Priority for Multi-Role Players:**
1. Primary contracted role (Wicketkeeper > Batter > All-rounder)
2. Highest competency score position
3. Most frequently deployed position in 2023+ data

**Cricket Context:** While players like Nicholas Pooran can bat anywhere from 1-7, teams need clarity on their primary deployment. The depth chart should reflect realistic usage, not theoretical versatility.

### 3.4 Constraint C4: 20-Over Utilization

**Rule:** The XI must be able to bowl 20 overs using only players who can reliably deliver 4 overs.

**Implementation:**
```python
bowling_overs_capacity = sum(p.bowling_overs_capability for p in xi if p.can_bowl)
primary_bowlers = count(p for p in xi if p.bowling_overs_capability >= 4)

if bowling_overs_capacity < 20:
    CONSTRAINT_VIOLATED
if primary_bowlers < 5:
    CONSTRAINT_VIOLATED
```

**Bowling Capability Classification:**
| Player Type | Overs Capability | Rationale |
|-------------|------------------|-----------|
| Specialist Bowler | 4 | Full quota expected |
| Bowling All-rounder | 4 | Can complete quota if needed |
| Batting All-rounder | 2-4 | Part-time option |
| Part-timer | 0-2 | Emergency only |

**Cricket Context:** Running out of bowling options is a captain's nightmare. The algorithm ensures 5 players who can bowl 4 overs each, providing tactical flexibility and injury cover.

---

## 4. Optimization Metrics (In Order of Importance)

### 4.1 Metric M1: Strike Rate Optimization

**Priority:** HIGHEST

**Definition:** The XI should maximize expected strike rate across all three phases.

**Formula:**
```
PHASE_SR_SCORE = (PP_SR_CONTRIBUTION * 0.30) +
                 (MIDDLE_SR_CONTRIBUTION * 0.35) +
                 (DEATH_SR_CONTRIBUTION * 0.35)
```

**Benchmarks:**

| Phase | Elite SR | Good SR | Average SR | Below Average |
|-------|----------|---------|------------|---------------|
| Powerplay (1-6) | 150+ | 140-150 | 130-140 | <130 |
| Middle (7-15) | 140+ | 130-140 | 120-130 | <120 |
| Death (16-20) | 170+ | 160-170 | 150-160 | <150 |

**Cricket Context:** Strike rate is the currency of T20. A team striking at 145 overall will outscore a team at 135 by approximately 20 runs per innings, which is the difference between winning and losing most matches.

### 4.2 Metric M2: 20-Over Utilization Score

**Priority:** HIGH

**Definition:** Confidence that the XI can bowl 20 complete overs without a liability phase.

**Formula:**
```
BOWLING_UTILIZATION = (PP_COVERAGE * 0.25) +
                      (MIDDLE_COVERAGE * 0.40) +
                      (DEATH_COVERAGE * 0.35)

Where coverage = 1.0 if at least 2 bowlers can competently bowl that phase
```

**Phase Coverage Requirements:**

| Phase | Minimum Competent Bowlers | Optimal |
|-------|---------------------------|---------|
| Powerplay | 2 | 3 (2 seamers + 1 option) |
| Middle | 3 | 4 (2 spinners + 2 options) |
| Death | 2 | 3 (specialist + 2 options) |

**Cricket Context:** The middle overs (7-15) represent 9 overs - the largest phase. Teams need depth here because this is where spinners earn their keep and where batting all-rounders provide relief.

### 4.3 Metric M3: Dot Ball Percentage

**Priority:** MEDIUM-HIGH

**For Batters:** Lower is better
```
BATTER_DOT_PENALTY = max(0, (player.dot_pct - 30) * 0.5)
```

**For Bowlers:** Higher is better
```
BOWLER_DOT_BONUS = (player.dot_pct - 32) * 0.3  // 32% is T20 average
```

**Benchmarks:**

| Dot Ball % | Batters | Bowlers |
|------------|---------|---------|
| <25% | Elite | Liability |
| 25-30% | Good | Below Average |
| 30-35% | Average | Average |
| 35-40% | Below Average | Good |
| 40%+ | Liability | Elite |

**Cricket Context:** Dot balls create pressure. For batters, consecutive dots force risky shots. For bowlers, dots are wicket precursors. The elite bowlers (Bumrah, Rashid Khan) consistently achieve 38-42% dot ball rates.

### 4.4 Metric M4: Experience Factor

**Priority:** LOW (Minor Weight)

**Definition:** A small bonus for IPL experience, especially in high-pressure situations.

**Formula:**
```
EXPERIENCE_BONUS = min(5, IPL_MATCHES / 20)  // Max 5 points at 100+ matches
```

**Cricket Context:** Experience matters less in T20 than other formats, but captaincy candidates and death-over finishers benefit from pressure exposure. This is weighted low (~5% of total score) to avoid over-selecting aging players.

---

## 5. Data Source Hierarchy

### 5.1 Primary Source: IPL Data (2021-2025)

**Scope:** All IPL matches from 2021-2025 (5 seasons)
**Use For:** Primary competency scoring, tag generation, matchup analysis

**Qualification Thresholds:**
- Batters: Minimum 300 balls faced in IPL
- Bowlers: Minimum 200 balls bowled in IPL

### 5.2 Secondary Source: Non-IPL T20 Data (2023+)

**Trigger:** Player does not meet IPL qualification thresholds

**Data Sources (in priority order):**
1. **T20 International data** (2023+)
2. **Other T20 franchise leagues** (BBL, PSL, CPL, The Hundred - 2023+)
3. **Domestic T20** (SMAT, Vitality Blast - 2023+)

**Application Rules:**
```python
if player.ipl_balls < QUALIFICATION_THRESHOLD:
    # Use non-IPL T20 data with 0.9 confidence modifier
    player.score = calculate_score(non_ipl_data) * 0.90
    player.data_source = "NON_IPL_T20"
    player.confidence = "MEDIUM"
else:
    player.score = calculate_score(ipl_data)
    player.data_source = "IPL"
    player.confidence = "HIGH"
```

**Cricket Context:** New signings (e.g., Rachin Ravindra, Kwena Maphaka) may have limited IPL data but strong international/franchise records. The 0.9 modifier accounts for IPL's uniquely competitive environment.

### 5.3 Tertiary Source: Entry Point Analysis

**Definition:** Historical batting entry position data indicating where players typically bat.

**Classifications:**
| Entry Classification | Avg Entry Ball | Typical Positions |
|---------------------|----------------|-------------------|
| TOP_ORDER | 0-25 | 1-3 |
| MIDDLE_ORDER | 26-60 | 4-6 |
| LOWER_ORDER | 61+ | 7-11 |

**Usage:**
```python
if player.entry_classification == "TOP_ORDER":
    eligible_positions = [1, 2, 3]
elif player.entry_classification == "MIDDLE_ORDER":
    eligible_positions = [4, 5, 6]
else:
    eligible_positions = [7, 8, 9, 10, 11]
```

**Cricket Context:** Entry point analysis prevents misplacements like batting Rashid Khan at #4 or dropping Virat Kohli to #6. Historical entry patterns reflect both capability and team trust.

---

## 6. Override Mechanism Design

### 6.1 Founder Override System

**Purpose:** Allow explicit human intervention in algorithm-generated selections.

**Override Types:**

| Type | Scope | Persistence | Example |
|------|-------|-------------|---------|
| **PLAYER_INCLUDE** | Force player into XI | Per regeneration | "Include Noor Ahmad in CSK XI" |
| **PLAYER_EXCLUDE** | Remove player from XI | Per regeneration | "Exclude injured player X" |
| **POSITION_LOCK** | Lock player to specific position | Per regeneration | "Lock Kohli at #1" |
| **CAPTAIN_DESIGNATE** | Override algorithm captain | Permanent | "Axar Patel is DC captain" |
| **IMPACT_LOCK** | Lock specific impact player | Per regeneration | "Impact must be spinner" |

### 6.2 JSON Output Schema with Override

```json
{
  "team_name": "Delhi Capitals",
  "team_abbrev": "DC",
  "xi": [...],
  "impact_player": {...},
  "overrides_applied": [
    {
      "override_id": "OVR-DC-001",
      "type": "CAPTAIN_DESIGNATE",
      "player_name": "Axar Patel",
      "source": "Founder Sprint 4 Check-In",
      "applied_at": "2026-02-04",
      "original_value": "KL Rahul",
      "new_value": "Axar Patel"
    }
  ],
  "founder_override": true,
  "algorithm_confidence": 0.85,
  "override_notes": "Captain corrected per Founder input. Axar Patel removed from impact eligibility."
}
```

### 6.3 Override Validation Rules

1. **Override cannot violate hard constraints** (e.g., cannot force 5 overseas)
2. **Override must be logged** with source, date, and rationale
3. **Override persists** until explicitly removed or contradicted by newer override
4. **Algorithm recalculates** remaining slots after override applied

---

## 7. Domain-Specific Notes (Cricket Expert)

### 7.1 Why Competency > Variety (65/35)

The 65/35 split reflects a fundamental T20 truth: **proven performers win tournaments**.

**Historical Evidence:**
- CSK (4 titles): Consistently backs experienced players (Dhoni, Jadeja, Bravo)
- MI (5 titles): Core of Rohit, Bumrah, Pollard across multiple seasons
- GT (2022 winner): Rashid Khan, Shubman Gill as anchors

**The Variety Trap:** Teams that over-optimize for balance often field untested combinations. A perfectly balanced XI with 2 LHB, 2 spinners, and 3 pacers means nothing if those players are unproven at IPL level.

### 7.2 Why Strike Rate is Metric #1

In modern T20 cricket (2020+), **first innings scores above 180 are now routine**. The algorithm must:
- Select batters who can score at 140+ SR across phases
- Avoid "anchors" who score at 110-120 SR regardless of match situation

**The Math:**
- Team A: 8 batters averaging 125 SR = 150 runs in 120 balls
- Team B: 8 batters averaging 140 SR = 168 runs in 120 balls
- Difference: 18 runs per innings, or ~36 runs per match

### 7.3 Why Experience is Weighted Low

T20 cricket rewards:
- **Speed** (physical and mental)
- **Fearlessness** (youth advantage)
- **Adaptability** (match-up awareness)

Experience provides marginal gains in death-over finishing and captaincy, but the algorithm should not penalize talented young players (Jaiswal, Stubbs, Tilak Varma) in favor of declining veterans.

### 7.4 Critical Errors to Avoid

| Error | Example | Prevention |
|-------|---------|------------|
| **Spinner as WK** | Digvesh Rathi classified as keeper | Validate role against bowling_type |
| **Captain as Impact** | Axar Patel in DC impact slot | Hard constraint C1 |
| **Under-using overseas** | CSK with 1 overseas | Target exactly 4 overseas |
| **Position inflation** | Pooran in 6 depth chart slots | Max 2 roles per player |
| **Ignoring entry points** | Finisher batting at #3 | Use entry classification data |

### 7.5 Phase-Specific Selection Priorities

| Phase | Priority | Reasoning |
|-------|----------|-----------|
| **Death Bowling** | CRITICAL | Hardest phase to defend; need 2+ specialists |
| **Powerplay Batting** | HIGH | Sets the tone; poor PP = chasing all innings |
| **Middle Overs Spin** | HIGH | Cheapest economy zone; accumulator phase |
| **Death Batting** | HIGH | Finisher quality separates good from great |
| **Powerplay Bowling** | MEDIUM | Wickets valuable but economy manageable |
| **Middle Batting** | MEDIUM | Rotators acceptable if depth exists |

---

## 8. Algorithm Execution Flow

```
INPUT: Squad (25 players), Venue Bias, Captain Flag, Entry Points

STEP 1: Score all players (Competency Score)
STEP 2: Apply variety adjustments per team composition
STEP 3: Check hard constraints (C1-C4)
STEP 4: Optimize for metrics (M1-M4)
STEP 5: Apply Founder overrides (if any)
STEP 6: Generate final XI + Impact Player
STEP 7: Output JSON with confidence scores and notes

OUTPUT:
- xi[11]: Selected players with positions and rationales
- impact_player: 12th man selection
- overrides_applied[]: List of founder interventions
- founder_override: boolean flag
- constraint_violations[]: Any remaining issues
- algorithm_confidence: 0.0-1.0 score
```

---

## 9. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-01 | Stephen Curry | Initial algorithm implementation |
| 2.0 | 2026-02-04 | Andy Flower | Founder inputs incorporated (Sprint 4 Check-In): 65/35 weights, optimization metrics, hard constraints, override mechanism |

---

## 10. Sign-off

| Role | Name | Status | Date |
|------|------|--------|------|
| Cricket Domain Expert | Andy Flower | AUTHORED | 2026-02-04 |
| Analytics Lead | Stephen Curry | FOR IMPLEMENTATION | 2026-02-04 |
| Product Owner | Tom Brady | PENDING REVIEW | - |
| Founder | Florentino Perez | PENDING APPROVAL | - |

---

*Cricket Playbook - Predicted XII Algorithm Specification v2.0*
*Document: `docs/specs/predicted_xii_algorithm_v2.md`*
*This is a living spec document - updates tracked via version history*
