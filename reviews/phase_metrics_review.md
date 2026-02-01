# Andy Flower - Phase Metrics Domain Review

**Reviewer:** Andy Flower (Cricket Domain Specialist)
**Subject:** Multi-Metric Phase Tagging Framework
**Date:** 2026-02-01
**Status:** Response to Stephen Curry's Tag Standardization Audit

---

## Executive Summary

The user's challenge is **CORRECT**. Using single metrics (SR for batters, Economy for bowlers) to tag phase performance is fundamentally inadequate. Cricket is a multi-dimensional contest where players can be elite in one aspect while exploitable in another.

A death bowler with 10.5 economy but 0.08 wickets/ball is **NOT** a liability - they're a wicket-taking option who creates chances. A powerplay batter with 160 SR but 40% dot balls may be **boom-or-bust**, not elite.

---

## Section 1: BATTER PHASE METRICS

### 1.1 Metrics Required for Each Phase

| Metric | Powerplay | Middle | Death | Rationale |
|--------|-----------|--------|-------|-----------|
| Strike Rate | PRIMARY | SECONDARY | PRIMARY | PP sets tone, death requires acceleration |
| Dot Ball % | PRIMARY | PRIMARY | SECONDARY | PP dots = wasted fielding restrictions; middle dots stall momentum |
| Dismissal Rate (balls/dismissal) | SECONDARY | PRIMARY | SECONDARY | Middle survival allows building; death dismissals expected |
| Boundary % | PRIMARY | SECONDARY | PRIMARY | PP boundaries exploit field; death boundaries essential |

**Status:** APPROVE - The four-metric framework is cricket-correct.

---

### 1.2 Powerplay Batter Thresholds (Overs 1-6)

**Context:** Fielding restrictions (max 2 outside 30-yard circle). Batters SHOULD be aggressive. Bowlers targeting stumps/edges. High-risk, high-reward phase.

| Metric | ELITE | AVERAGE | EXPLOITABLE | Cricket Rationale |
|--------|-------|---------|-------------|-------------------|
| Strike Rate | >= 150 | 130-149 | < 120 | PP SR below 120 is unacceptable; you're wasting the field |
| Dot Ball % | < 25% | 25-35% | > 40% | More than 40% dots = failing to rotate, pressure builds |
| Balls/Dismissal | >= 25 | 15-24 | < 12 | Getting out under 12 balls = failed to settle |
| Boundary % | >= 20% | 12-19% | < 10% | PP is FOR boundaries; <10% means bowler dominance |

**Status:** APPROVE with following CAVEATS:

**CAVEAT 1:** These thresholds assume OPENER role. A No.3 entering at 4/1 in over 2 has different context - they need to survive first, then accelerate.

**CAVEAT 2:** Batting first vs chasing changes expectations. Chasing in PP allows more measured approach if required run rate is low.

---

### 1.3 Middle Overs Batter Thresholds (Overs 7-15)

**Context:** No fielding restrictions. Spin typically dominant (2-3 spinners bowling). The phase where anchors earn their value and accelerators set up the death.

| Metric | ELITE | AVERAGE | EXPLOITABLE | Cricket Rationale |
|--------|-------|---------|-------------|-------------------|
| Strike Rate | >= 140 | 120-139 | < 110 | Middle SR <110 is too slow; you're eating balls needed later |
| Dot Ball % | < 30% | 30-38% | > 45% | Middle phase NEEDS rotation; 45%+ dots creates collapse risk |
| Balls/Dismissal | >= 30 | 18-29 | < 15 | Middle dismissals hurt most - you've invested but not cashed out |
| Boundary % | >= 15% | 10-14% | < 8% | Occasional boundary maintains pressure; <8% is pure survival |

**Status:** APPROVE with following CAVEATS:

**CAVEAT 1:** Role matters enormously. An anchor batting through to death with 115 SR but 35 balls/dismissal is VALUABLE. A designated accelerator at 115 SR is EXPLOITABLE.

**CAVEAT 2:** Must tag batting position/role first, then evaluate phase performance within that role context.

---

### 1.4 Death Overs Batter Thresholds (Overs 16-20)

**Context:** Slog overs. Bowlers bowling yorkers, slower balls, wide variations. Only boundaries truly matter. Dots are devastating. Survival is secondary to scoring.

| Metric | ELITE | AVERAGE | EXPLOITABLE | Cricket Rationale |
|--------|-------|---------|-------------|-------------------|
| Strike Rate | >= 170 | 145-169 | < 130 | Death SR under 130 is a failure - you should be swinging |
| Dot Ball % | < 25% | 25-35% | > 40% | Death dots = runs left on the table; 40%+ is a finisher failure |
| Balls/Dismissal | >= 12 | 8-11 | < 6 | Getting out too quickly is bad, but dismissals are accepted |
| Boundary % | >= 25% | 18-24% | < 15% | Death MUST have boundaries; running is inefficient |

**Status:** APPROVE with following CAVEAT:

**CAVEAT:** Wickets in hand changes context. If you're 8 down, even a good finisher may struggle to find strike or take risks. Death phase stats should ideally filter for >= 3 wickets in hand.

---

### 1.5 Recommended Composite Scoring for Batters

**Status:** CHALLENGE on using single composite score

**Recommendation:** Use SEPARATE ASPECT TAGS, not a single composite.

**Rationale:** A batter with 160 SR but 42% dots is NOT "average" - they are specifically **BOOM-OR-BUST**. This is tactically valuable information that gets lost in a composite.

**Proposed Batter Phase Tags:**

| Tag | Criteria | Example |
|-----|----------|---------|
| `PP_DOMINATOR` | Elite in 3+ of 4 metrics | Rohit Sharma in form |
| `PP_BOOM_OR_BUST` | Elite SR + Boundary% but Exploitable Dots | Prithvi Shaw pattern |
| `PP_ACCUMULATOR` | Good survival/dots but Average SR | KL Rahul as opener |
| `PP_LIABILITY` | Exploitable in 2+ metrics | Occasional opener struggling |
| `MIDDLE_ANCHOR` | Elite survival, Average+ SR, Good dots | Kohli stabilizing |
| `MIDDLE_ACCELERATOR` | Elite SR, Elite boundary%, Average survival | SKY pattern |
| `MIDDLE_LIABILITY` | Poor SR AND poor survival | Out of form No.4 |
| `DEATH_FINISHER` | Elite SR + Boundary%, Good survival | Hardik, Russell |
| `DEATH_HITTER` | Elite SR/Boundary but poor survival | Jadeja at death |
| `DEATH_LIABILITY` | Exploitable SR + Boundary% | Not a finisher |

---

## Section 2: BOWLER PHASE METRICS

### 2.1 Metrics Required for Each Phase

| Metric | Powerplay | Middle | Death | Rationale |
|--------|-----------|--------|-------|-----------|
| Economy | PRIMARY | PRIMARY | SECONDARY | PP/middle economy dictates match tempo |
| Dot Ball % | PRIMARY | PRIMARY | SECONDARY | PP dots = early pressure; middle dots stall batting |
| Wickets/Ball | SECONDARY | SECONDARY | PRIMARY | Death wickets change equations |
| Boundary Conceded % | PRIMARY | SECONDARY | PRIMARY | PP/death boundaries are game-defining |

**Status:** APPROVE - The four-metric framework captures what bowlers do differently.

---

### 2.2 Powerplay Bowler Thresholds (Overs 1-6)

**Context:** New ball, fielding restrictions against you (max 2 out), batters swinging freely. Your job: early wickets AND limiting damage. Both matter.

| Metric | ELITE | AVERAGE | EXPLOITABLE | Cricket Rationale |
|--------|-------|---------|-------------|-------------------|
| Economy | <= 7.0 | 7.1-8.5 | >= 9.5 | PP eco >=9.5 with field up = hemorrhaging runs |
| Dot Ball % | >= 45% | 35-44% | < 30% | PP dots with new ball should be high; <30% is concerning |
| Wickets/Ball | >= 0.05 | 0.03-0.049 | < 0.02 | 1 wicket per 20 balls is solid; 1 per 50 is non-threatening |
| Boundary % Conceded | < 12% | 12-18% | > 22% | Conceding >22% boundaries in PP = being targeted |

**Status:** APPROVE with CAVEAT:

**CAVEAT:** Powerplay bowling roles differ. Opening bowlers (overs 1-3) face more aggressive openers than first-change bowlers (overs 4-6). Consider splitting if data allows.

---

### 2.3 Middle Overs Bowler Thresholds (Overs 7-15)

**Context:** Field spread. Spinners dominate (favorable conditions, less hitting intent). Pace bowlers often rested. This is where you BUILD pressure or let batters settle.

| Metric | ELITE | AVERAGE | EXPLOITABLE | Cricket Rationale |
|--------|-------|---------|-------------|-------------------|
| Economy | <= 7.0 | 7.1-8.0 | >= 8.5 | Middle eco 8.5+ means batters are ticking along too easily |
| Dot Ball % | >= 50% | 40-49% | < 35% | Middle overs SHOULD be dot-heavy; <35% = no pressure |
| Wickets/Ball | >= 0.04 | 0.025-0.039 | < 0.02 | Middle wickets trigger collapses; low rate = just containing |
| Boundary % Conceded | < 10% | 10-15% | > 18% | Middle boundaries should be rare; >18% = being attacked |

**Status:** APPROVE with CAVEAT:

**CAVEAT:** Spin vs pace expectations differ. A spinner at 7.5 eco in middle overs is underperforming; a pacer at 7.5 is doing their job. Consider bowling type context.

---

### 2.4 Death Overs Bowler Thresholds (Overs 16-20)

**Context:** The hardest phase. Batters swinging for everything. Set batters cashing in. Yorkers, slower balls, wide yorkers are your weapons. WICKETS matter more than economy here.

| Metric | ELITE | AVERAGE | EXPLOITABLE | Cricket Rationale |
|--------|-------|---------|-------------|-------------------|
| Economy | <= 9.0 | 9.1-11.0 | >= 12.0 | Death eco is naturally high; 12+ is still exploitable |
| Dot Ball % | >= 35% | 25-34% | < 22% | Death dots are hard but valuable; <22% = every ball scored |
| Wickets/Ball | >= 0.06 | 0.04-0.059 | < 0.03 | Death wickets WIN matches; <0.03 = no threat |
| Boundary % Conceded | < 20% | 20-28% | > 32% | Death boundaries expected; >32% = being demolished |

**Status:** APPROVE - These reflect the reality that death bowling is about wickets AND containment.

---

### 2.5 Critical Decision: Death Bowler Classification

**The User's Example:** "Is a death bowler with 10.5 economy but 0.08 wickets/ball elite or exploitable?"

**MY ASSESSMENT:** This bowler is **ELITE AS A WICKET-TAKING OPTION**.

**Analysis:**
- Economy 10.5 = AVERAGE for death (between 9.1-11.0)
- Wickets/ball 0.08 = ELITE (well above 0.06 threshold)
- This is a Jasprit Bumrah/Jofra Archer profile

**Cricket Logic:** You don't bowl this bowler to save runs - you bowl them to take wickets when batters are set. The 10.5 economy includes the wickets they take (which count as runs saved in context). A death bowler who takes 0.08 wickets/ball is REMOVING batters who would otherwise accelerate.

**Recommendation:** This bowler should receive:
- `DEATH_WICKET_TAKER` (elite)
- NOT `DEATH_LIABILITY` (current economy-only logic would wrongly tag this)

**The Inverse Case:** A death bowler with 8.5 economy but 0.02 wickets/ball is:
- Economy 8.5 = ELITE
- Wickets/ball 0.02 = EXPLOITABLE

**This is a DIFFERENT profile:** Defensive, dot-ball focused, but batters know they can survive and score off them eventually. Useful in certain situations but NOT a strike bowler.

**Tag:** `DEATH_CONTAINER` - economical but non-threatening.

---

### 2.6 Recommended Composite Approach for Bowlers

**Status:** CHALLENGE on single economy-based tagging

**Recommendation:** Use PROFILE-BASED TAGS that combine metrics meaningfully.

**Proposed Bowler Phase Tags:**

| Tag | Criteria | Tactical Use |
|-----|----------|--------------|
| `PP_STRIKE_BOWLER` | Elite wickets/ball + Good dots | New ball with field up |
| `PP_CONTAINER` | Elite economy/dots but Average wickets | Restrict in PP |
| `PP_LIABILITY` | Exploitable economy AND low dots | Avoid in PP |
| `MIDDLE_STRANGLER` | Elite dots + Good economy | Build pressure |
| `MIDDLE_WICKET_TAKER` | Elite wickets but Average economy | Break partnerships |
| `MIDDLE_LIABILITY` | Poor dots AND poor economy | Avoid middle overs |
| `DEATH_STRIKE` | Elite wickets/ball, Average+ economy | When wickets needed |
| `DEATH_CONTAINER` | Elite economy but low wickets | Defend 15+ runs |
| `DEATH_COMPLETE` | Elite in economy AND wickets | True death specialist |
| `DEATH_LIABILITY` | Exploitable economy AND low wickets | Not a death option |

---

## Section 3: SPECIFIC THRESHOLD RECOMMENDATIONS

### 3.1 Dot Ball % by Phase

| Phase | Role | ELITE | PROBLEMATIC | Notes |
|-------|------|-------|-------------|-------|
| Powerplay | Batter | < 25% | > 40% | Wasted fielding restrictions |
| Powerplay | Bowler | >= 45% | < 30% | New ball should create dots |
| Middle | Batter | < 30% | > 45% | Rotation is essential |
| Middle | Bowler | >= 50% | < 35% | Spin should dominate |
| Death | Batter | < 25% | > 40% | Every dot hurts |
| Death | Bowler | >= 35% | < 22% | Hard to dot but valuable |

**Status:** APPROVE - These reflect genuine phase dynamics.

---

### 3.2 Wickets/Ball Rate by Phase (Bowlers)

| Phase | ELITE | AVERAGE | EXPLOITABLE | Context |
|-------|-------|---------|-------------|---------|
| Powerplay | >= 0.05 | 0.03-0.049 | < 0.02 | 1 wicket per 20 balls is solid |
| Middle | >= 0.04 | 0.025-0.039 | < 0.02 | Middle wickets trigger collapses |
| Death | >= 0.06 | 0.04-0.059 | < 0.03 | Death wickets are crucial |

**Status:** APPROVE

**Note:** Death wickets/ball SHOULD be higher than other phases because batters take more risks. A death bowler with same wickets/ball as their middle overs is actually UNDERPERFORMING at death.

---

### 3.3 Dismissal Rate by Phase (Batters)

| Phase | CONCERNING | ACCEPTABLE | ELITE | Context |
|-------|------------|------------|-------|---------|
| Powerplay | < 12 balls | 12-24 balls | >= 25 balls | Getting out under 2 overs is a failure |
| Middle | < 15 balls | 15-29 balls | >= 30 balls | Middle dismissals hurt partnership building |
| Death | < 6 balls | 6-11 balls | >= 12 balls | Death dismissals are acceptable risks |

**Status:** APPROVE with CAVEAT:

**CAVEAT:** Dismissal rate must be read alongside SR. A batter with 8 balls/dismissal at death but 180 SR and 30% boundaries is VALUABLE (aggressive risk-taking). One with 8 balls/dismissal and 120 SR is EXPLOITABLE (getting out without scoring).

---

## Section 4: IMPLEMENTATION RECOMMENDATIONS

### 4.1 Data Requirements

**CHALLENGE:** Current `bowler_phase_tags.py` calculates wickets but doesn't use them for tagging.

**Required Changes:**
1. Add boundary tracking (4s and 6s conceded) to phase queries
2. Store wickets/ball and boundary % in output CSVs
3. Implement multi-metric tagging logic

### 4.2 Sample Size Recommendations by Phase

| Phase | Bowler Min | Batter Min | Rationale |
|-------|------------|------------|-----------|
| Powerplay | 30 overs (180 balls) | 100 balls | ~5 full PP stints, ~17 innings |
| Middle | 50 overs (300 balls) | 150 balls | ~5 full stints, ~15 innings |
| Death | 25 overs (150 balls) | 80 balls | Death overs are scarcer |

**Status:** APPROVE - Current minimums are reasonable but death could be lowered.

### 4.3 Tag Hierarchy Recommendation

When multiple tags could apply, use this hierarchy:

1. **Elite positive tags** (DOMINATOR, STRIKE, COMPLETE) - awarded if metrics qualify
2. **Profile tags** (ACCUMULATOR, CONTAINER, BOOM_OR_BUST) - describe style
3. **Liability tags** - only if multiple metrics are exploitable

**Rule:** A player cannot have both ELITE and LIABILITY tags for the same phase.

---

## Section 5: RESPONSE TO USER'S SPECIFIC EXAMPLES

### Example 1: "Is a death bowler with 10.5 economy but 0.08 wickets/ball elite or exploitable?"

**VERDICT:** ELITE as wicket-taking option.

**Tag Recommendation:** `DEATH_STRIKE` or `DEATH_WICKET_TAKER`

**Rationale:** 0.08 wickets/ball is exceptional (1 wicket every 12.5 balls). This is a Bumrah-tier wicket threat. The 10.5 economy is acceptable collateral for that strike rate. You bowl this player when you need wickets.

---

### Example 2: "Is a powerplay batter with 160 SR but 40% dot ball elite?"

**VERDICT:** NOT ELITE. This is **BOOM-OR-BUST**.

**Tag Recommendation:** `PP_BOOM_OR_BUST`

**Rationale:**
- 160 SR is elite
- 40% dots is exploitable

This player hits big when they connect but goes multiple balls without scoring. This is:
- Useful when chasing a big total (need boundaries, accept risk)
- Problematic when setting (40% dots means 20+ dot balls in a 50-ball PP stint)

**Tactical Note:** This is often a bowler-specific vulnerability - they may dominate pace but struggle with spin, or vice versa. Worth investigating matchup breakdown.

---

## Section 6: FINAL RECOMMENDATIONS

### APPROVE:
1. Four-metric framework for both batters and bowlers
2. Phase-specific thresholds (PP/Middle/Death have different expectations)
3. Profile-based tagging over single composite scores
4. Separate positive/negative tags for different aspects

### CAVEAT:
1. Role context matters - anchor vs accelerator should have different thresholds
2. Batting position affects phase interpretation (opener vs No.5)
3. Match situation (setting vs chasing) changes expectations
4. Bowling type (spin vs pace) affects middle overs benchmarks

### CHALLENGE:
1. Current economy-only tagging for bowler phases - MUST add wickets/ball
2. Single SR metric for batter phases - MUST add dots and boundaries
3. The `DEATH_LIABILITY` tag requiring BOTH high economy AND poor SR is correct logic - but should be applied to ALL phases with appropriate multi-metric criteria

---

## Sign-off

The proposed multi-metric framework is **CRICKET-CORRECT** and should be implemented. Single-metric phase tags are misleading and fail to capture the nuanced reality of T20 cricket.

Key message: **A player's VALUE in a phase depends on WHAT they contribute, not just HOW MUCH.**

---

*Andy Flower*
*Cricket Domain Specialist*
*2026-02-01*
