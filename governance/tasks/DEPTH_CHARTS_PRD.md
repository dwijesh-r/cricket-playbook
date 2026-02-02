# Task PRD: Depth Charts

**Author**: Andy Flower (Cricket Domain Expert)
**Status**: APPROVED - Founder Input Incorporated
**Created**: 2026-02-02
**Founder Review**: 2026-02-02

---

## Problem Statement

Readers viewing a Predicted XII see ONE combination - but real cricket management thinks in OPTIONS. When a player gets injured mid-tournament, when conditions change, when match-ups matter, teams draw from their squad depth.

Current cricket preview content fails to show:
1. **Backup options** - Who steps in if Bumrah is rested?
2. **Positional flexibility** - Can this opener bat #3 if needed?
3. **Squad depth quality** - Is this team one injury away from crisis?
4. **Selection dilemmas** - Why X over Y at a position?

Depth Charts solve this by showing position-by-position rankings - like NFL depth charts showing 1st string, 2nd string, 3rd string at each position. This gives readers the **coach's view** of squad options.

---

## Proposed Solution

Create **Depth Charts for all 10 IPL teams** showing ranked player options at each of 9 defined positions. Each position shows:
- Primary option (starter)
- Backup options (ranked)
- Brief rationale for ranking

**Relationship to Predicted XII**: Depth Charts show all OPTIONS; Predicted XII shows the SELECTED combination. A player ranked #1 at their position in the Depth Chart should appear in the Predicted XII (unless balance constraints force otherwise).

---

## Success Criteria

| Criteria | Measurement |
|----------|-------------|
| Position Coverage | All 9 positions defined for all 10 teams |
| Depth Visibility | Minimum 2 options shown per position |
| Ranking Credibility | Rankings defensible to cricket experts |
| Consistency | Depth Chart #1s align with Predicted XII selections |
| Reader Value | Reader understands "If X is unavailable, Y is next" |

---

## Position Definitions

### Position 1: Opener (2 slots in XI, show Top 3 options)

**What defines an opener:**
- Faces the new ball under fielding restrictions
- Must handle pace, swing, seam movement
- Benefits from powerplay field (only 2 fielders outside circle)
- Sets the tone - either aggressive (exploiting PP field) or anchoring (protecting wickets)

**Distinguishing characteristics:**
- **Powerplay strike rate** - Their PP SR matters more than overall SR
- **Boundary percentage in PP** - Openers should find boundaries against spread fields
- **Average against pace in first 6** - New ball survival/scoring
- **Balls faced per dismissal** - Ability to occupy crease when needed

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| Powerplay SR | 30% | Primary role requirement |
| PP Boundary % | 20% | Exploiting field restrictions |
| Career T20 Average | 15% | Overall reliability |
| Last 2 seasons IPL PP performance | 20% | Recent form in context |
| IPL experience (matches) | 15% | Proven at this level |

**Depth meaning**: Opener depth = "If both first-choice openers unavailable, who opens?" Critical because openers face most different bowling (new ball specialist, death over specialist may never bowl at them).

---

### Position 2: #3 Batter (1 slot in XI, show Top 3 options)

**What defines a #3:**
The #3 is the most versatile batting position in T20. They must handle two completely different situations:
1. **Early wicket** (1-2 down in PP): Face the new ball, rebuild, survive swing
2. **Platform set** (150/1 in 15 overs): Come in and immediately accelerate

**Distinguishing from openers:**
- Openers are SELECTED to open; #3 RESPONDS to situations
- #3 needs spin competence (may face middle overs spin)
- #3 needs pace competence (may enter against new ball)
- #3 needs acceleration gear (may enter with platform set)

**Distinguishing from middle order:**
- #3 may face the new ball; middle order rarely does
- #3 needs powerplay skills; middle order needs middle/death skills
- #3 is often the "best batter" who can handle anything

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| Overall T20 Average | 25% | Must be reliable - often protects innings |
| SR in overs 1-10 | 20% | May enter early |
| SR in overs 11-20 | 20% | May enter late |
| Performance vs spin | 15% | Will face spin if entering mid-innings |
| Performance vs pace | 15% | Will face pace if entering early |
| Adaptability score | 5% | SR variance between situations (lower = more adaptable) |

**FOUNDER DECISION**: Yes - create adaptability score for #3s measuring consistency across different entry points.

**Depth meaning**: #3 depth = "Who's the best alternative if our specialist #3 is unavailable?" Often an opener who can drop down or a middle-order player who can come up.

---

### Position 3: Middle Order #4-5 (2 slots in XI, show Top 3 options)

**What defines middle order (#4-5):**
- Typically bat in overs 8-16
- Face spin primarily (middle overs are spin-heavy)
- Build or consolidate; set platform for death overs
- Must rotate strike AND find occasional boundaries

**Distinguishing from #3:**
- #4-5 rarely face new ball (only in collapse)
- #4-5 need strong spin game
- #4-5 focus on accumulation with acceleration potential

**Distinguishing from finishers:**
- #4-5 build innings; finishers explode at death
- #4-5 may bat 50+ balls; finishers typically bat 15-25 balls
- #4-5 average matters more; finishers SR matters more

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| Average in overs 7-15 | 25% | Primary operating window |
| SR in overs 7-15 | 20% | Scoring rate in middle |
| Performance vs spin | 25% | Spin dominates middle overs |
| Career T20 Average | 15% | Overall reliability |
| Last 2 seasons middle-order performance | 15% | Recent form |

**Depth meaning**: Middle order depth = "If our #4 and #5 are both unavailable, who slides in?" Could be a #3 dropping down or a finisher coming up.

---

### Position 4: Finisher #6-7 (2 slots in XI, show Top 3 options)

**What defines a finisher:**
- Bat in death overs (16-20) primarily
- Face death bowling specialists (yorkers, slower balls, bouncers)
- Must score at 160+ SR under extreme pressure
- Often bat with tail; can't rely on partner

**Distinguishing characteristics:**
- **Death overs SR** - THE defining metric
- **Boundary % at death** - Must clear the ropes
- **Not out percentage** - Staying till the end
- **Performance under pressure** - Chases, close games

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| SR in overs 16-20 | 35% | Primary role requirement |
| Boundary % at death | 20% | Must hit boundaries |
| Career T20 SR | 15% | Overall intent |
| Average at death | 15% | Reliability when exploding |
| Bowling utility | 15% | Finishers often bowl (all-rounder value) |

**Note on all-rounders**: Many finishers are batting all-rounders (Hardik, Stoinis, Russell). Bowling utility adds to their ranking as finishers because it means team can pick an extra specialist elsewhere.

**Depth meaning**: Finisher depth = "If Hardik is injured, who finishes?" Critical depth position - quality finishers are rare. Poor finisher depth exposes a team.

---

### Position 5: Wicketkeeper (1-2 slots in XI, show Primary + Backup)

**What defines a wicketkeeper:**
- Primary: Keeping skills (stumping, catches, agility)
- Secondary: Batting ability at their designated slot

**Wicketkeeper batting archetypes:**
1. **Keeper-opener** (KL Rahul, de Kock): Primary batters who keep
2. **Keeper-middle order** (Pant, Samson): Middle order hitters who keep
3. **Specialist keeper** (Saha, Kishan defensive): Keeping primary, batting secondary

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| Keeping quality (qualitative) | 30% | Primary role |
| Batting at designated position | 50% | Ranked as batter at their slot |
| IPL keeping experience | 20% | Proven at this level |

**Important**: Keepers are ranked WITHIN their batting slot. A keeper-opener competes with other openers; a keeper-finisher competes with other finishers. The Depth Chart shows:
- Primary keeper (and which batting slot)
- Backup keeper (and which batting slot)

**FOUNDER DECISION**: Yes - flag teams with no backup keeper as vulnerability.

**Depth meaning**: Keeper depth = "If our keeper is injured mid-tournament, who keeps?" Some teams have genuine backup keepers; others would need emergency solutions.

---

### Position 6: Lead Pacer (1 slot in XI, show Top 2 options)

**What defines a lead pacer:**
- Takes the new ball
- Bowls at the death
- Often the "strike bowler" - team's go-to wicket-taker
- Commands respect; batters are cautious against them
- Usually bowls overs 1, 17, 19 (high-pressure overs)

**Distinguishing from supporting pacer:**
- Lead pacer bowls BOTH new ball AND death
- Supporting pacer may be PP specialist OR death specialist OR middle overs economical
- Lead pacer is the "complete" fast bowler
- Lead pacer typically has lower strike rate (wicket-taking)

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| Wicket-taking ability (SR) | 25% | Primary weapon |
| Death overs economy | 25% | Must bowl at death |
| Powerplay economy | 20% | New ball duties |
| Career T20 economy | 15% | Overall control |
| IPL experience | 15% | Proven at this level |

**Elite lead pacers**: Bumrah, Archer, Rabada, Cummins, Starc. If a team has one of these, they're automatic #1.

**Depth meaning**: Lead pacer depth = "If Bumrah is rested, who leads the attack?" Critical because lead pacers are workhorses - 4 overs every game takes toll.

---

### Position 7: Supporting Pacer (1-2 slots in XI, show Top 3 options)

**What defines a supporting pacer:**
- Complements the lead pacer
- May specialize in one phase rather than all three
- Provides variety (left-arm, swing, bounce, cutters)

**Supporting pacer archetypes:**
1. **Powerplay specialist**: Swing, seam, new ball wizard (Boult, Shami)
2. **Death specialist**: Yorker king, slower ball expert (Arshdeep, Harshal)
3. **Middle overs economical**: Contains in overs 7-15 (Prasidh, Avesh)
4. **Wicket-taking X-factor**: Unpredictable, strike bowler (Nortje, Wood)

**Ranking criteria weights** (varies by archetype):

*For PP Specialist:*
| Metric | Weight |
|--------|--------|
| PP Economy | 35% |
| PP Strike Rate | 30% |
| Swing/seam movement | 20% |
| Overall economy | 15% |

*For Death Specialist:*
| Metric | Weight |
|--------|--------|
| Death Economy | 40% |
| Death Strike Rate | 25% |
| Yorker/variation execution | 20% |
| Overall economy | 15% |

**FOUNDER DECISION**: Split by archetype (PP specialists + Death specialists) - more informative.

**Depth meaning**: Supporting pacer depth = "What are our pace bowling options beyond the lead?" Teams need 3 reliable pacers minimum; 4 provides rotation comfort.

---

### Position 8: Lead Spinner (1-2 slots in XI, show Top 2 options)

**What defines a lead spinner:**
- Primary spin bowling option
- Bowls crucial middle overs (7-15)
- Controls run rate when batters looking to accelerate
- Often a wicket-taking threat too

**Spin bowling types:**
1. **Off-spinner** (R Ashwin, Washington): Control-focused, uses angle
2. **Leg-spinner** (Chahal, Rashid): Wicket-taking, harder to score off
3. **Left-arm orthodox** (Jadeja, Axar): Angle into RHB, control
4. **Left-arm wrist spin** (Kuldeep): Rare, turns away from RHB
5. **Mystery spinner** (Varun, Narine): Multiple variations

**Ranking criteria weights:**
| Metric | Weight | Rationale |
|--------|--------|-----------|
| Middle overs economy | 30% | Primary phase |
| Strike rate (wicket-taking) | 25% | Breakthrough ability |
| Career T20 economy | 15% | Overall control |
| Performance vs RHB/LHB | 15% | Versatility |
| IPL experience | 15% | Proven at this level |

**Depth meaning**: Lead spinner depth = "If Rashid is unavailable, who bowls the crucial middle overs?" Spin depth less critical than pace depth because middle overs are lower pressure than death.

---

### Position 9: All-rounder (2-3 slots in XI, show Batting-first + Bowling-first options)

**What defines an all-rounder:**
- Contributes meaningfully with BOTH bat and ball
- Provides team balance (extra bowling option or extra batting depth)
- NOT a "bits and pieces" player - must be selection-worthy for one skill, with bonus of other

**All-rounder archetypes:**

**A. Batting-first All-rounders (Bat > Bowl)**
- Primary value: Finisher/middle-order batting
- Secondary value: 2-4 overs of useful bowling
- Examples: Hardik Pandya, Stoinis, Russell, Miller (if bowling)
- Batting weight: 65% | Bowling weight: 35%

**B. Bowling-first All-rounders (Bowl > Bat)**
- Primary value: Frontline bowling (spinner or pacer)
- Secondary value: Can bat 7-8 credibly, useful 20-30 runs
- Examples: Jadeja, Axar, Shardul, Sundar
- Batting weight: 35% | Bowling weight: 65%

**C. True All-rounders (Bat = Bowl)** - Rare
- Would be selected for either skill alone
- Examples: (Historical: Kallis, Stokes in some periods)
- Batting weight: 50% | Bowling weight: 50%

**Ranking within archetypes:**

*Batting-first AR ranking:*
| Metric | Weight |
|--------|--------|
| Finisher metrics (death SR, etc) | 45% |
| Middle-order metrics | 20% |
| Bowling economy | 20% |
| Bowling overs capability | 15% |

*Bowling-first AR ranking:*
| Metric | Weight |
|--------|--------|
| Bowling metrics (eco, SR) | 50% |
| Batting average | 25% |
| Lower-order SR | 15% |
| IPL experience | 10% |

**FOUNDER DECISION**: BOTH - show all-rounders in their batting position AND in All-rounder section.

**Depth meaning**: All-rounder depth = "How many genuine dual-contributors does this team have?" All-rounder depth is TEAM BUILDING depth - more all-rounders = more XI flexibility.

---

## Overlap Rules

Players can legitimately fit multiple positions. Here's how to handle:

### Rule 1: Primary Position Assignment
Each player has ONE primary position based on where they MOST bat/bowl for their IPL team. This is their "home" in the depth chart.

### Rule 2: Secondary Position Flagging
Players who qualify for secondary positions get flagged with a tag:
- "(Also: Opener)" - for a #3 who can open
- "(Also: Finisher)" - for a middle-order player who can finish
- "(Also: PP Specialist)" - for a lead pacer who excels in PP

### Rule 3: All-rounder Double Listing
All-rounders appear TWICE:
1. In their batting position (ranked as batter)
2. In the All-rounder section (ranked as all-rounder)

Example: Hardik Pandya appears in:
- Finisher #6-7: Ranked based on finishing metrics
- All-rounder (Batting-first): Ranked based on AR value

### Rule 4: Wicketkeeper Integration
Keepers appear TWICE:
1. In their batting position (ranked as batter)
2. In Wicketkeeper section (ranked as keeper)

Example: Rishabh Pant appears in:
- Middle Order #4-5: Ranked as middle-order batter
- Wicketkeeper: Ranked as primary keeper

### Rule 5: Conflict Resolution
If a player could realistically play different positions (e.g., KL Rahul: opener OR #3):
- Show in BOTH positions with clear ranking
- Note which is their "likely role" for this team context
- Team context matters: KL at PBKS = opener; hypothetically at different team might = #3

---

## Output Format

### Per-Team Depth Chart Layout

```
## [TEAM NAME] Depth Chart

### Batting Depth

| Position | #1 (Starter) | #2 (Backup) | #3 (Backup) | Notes |
|----------|--------------|-------------|-------------|-------|
| Opener | [Name] | [Name] | [Name] | [Key note] |
| #3 | [Name] | [Name] | [Name] | |
| Middle #4-5 | [Name], [Name] | [Name] | - | |
| Finisher #6-7 | [Name], [Name] | [Name] | - | |
| Wicketkeeper | [Name] (slots X) | [Name] (slots Y) | - | |

### Bowling Depth

| Position | #1 (Starter) | #2 (Backup) | Notes |
|----------|--------------|-------------|-------|
| Lead Pacer | [Name] | [Name] | |
| Supporting Pacer | [Name], [Name] | [Name] | |
| Lead Spinner | [Name] | [Name] | |

### All-rounder Depth

| Type | #1 | #2 | Notes |
|------|----|----|-------|
| Batting-first AR | [Name] | [Name] | |
| Bowling-first AR | [Name] | [Name] | |

### Depth Assessment
- **Strongest depth**: [Position] - [Why]
- **Weakest depth**: [Position] - [Why]
- **Key vulnerability**: [Assessment]
- **Overseas flexibility**: [How many overseas compete for 4 slots]
```

### Summary Depth Chart (Cross-Team Comparison)

```
| Team | Opener | #3 | Middle | Finisher | Pace | Spin | AR | Overall |
|------|--------|-----|--------|----------|------|------|-----|---------|
| MI | 8.5 | 9.0 | 7.5 | 9.0 | 9.5 | 6.0 | 8.0 | 8.2 |
| CSK | 7.0 | 8.5 | 8.0 | 7.5 | 7.0 | 8.5 | 8.5 | 7.9 |
...
```

### Per-Position Rating Format

```
**Opener Depth: 8.5/10**
- What works: Elite opening pair in Rohit + de Kock, both proven IPL performers
- What doesn't: No proven third option if both unavailable; Tilak untested as opener
```

**FOUNDER DECISION**: Depth ratings out of 10 (with decimals, e.g., 7.5/10) plus description of what works and what doesn't work for each position.

---

## Ranking Methodology Summary

### For All Batters
1. Calculate position-specific metrics (PP SR for openers, death SR for finishers, etc.)
2. Apply position-specific weights from tables above
3. Add experience bonus (+5% for 50+ IPL matches, +10% for 100+ matches)
4. Apply recent form modifier (0.9x to 1.1x based on last 2 seasons vs career)
5. Rank within position

### For All Bowlers
1. Calculate role-specific metrics (death economy for death bowlers, PP SR for PP specialists)
2. Apply role-specific weights from tables above
3. Add experience bonus
4. Apply recent form modifier
5. Rank within position

### For All-rounders
1. Calculate batting score using relevant batting position metrics
2. Calculate bowling score using relevant bowling position metrics
3. Apply archetype weights (65/35 or 35/65 or 50/50)
4. Combine for all-rounder score
5. Rank within archetype

---

## Scope

### In Scope (V1)
- Depth Charts for all 10 IPL teams
- 9 positions defined with clear criteria
- Minimum 2 options per position (where squad allows)
- Brief rationale for #1 ranking at each position
- Overlap handling (players in multiple positions flagged)
- Depth assessment per team (strongest/weakest areas)
- Cross-team depth comparison table

### Out of Scope (V1)
- Historical depth chart changes (who moved up/down over seasons)
- Injury scenario modeling ("if X injured, new depth chart")
- Match-by-match optimal depth (varies by opponent)
- Detailed scouting reports on backup players
- Development trajectories (who might move up)

### Future Considerations (V2+)
- Interactive depth charts (click player to see full profile)
- "Injury impact" scores (how much does losing #1 hurt?)
- Historical accuracy tracking (did our depth charts prove accurate?)
- Auction recommendations based on depth gaps

---

## Dependencies

| Dependency | Status | Owner |
|------------|--------|-------|
| Squad data for all 10 teams | Required | Data Team |
| Player career T20 metrics | Required | Data Team |
| Phase-specific performance data | Required | Data Team |
| Position-specific metrics (PP SR, death SR, etc.) | Required | Data Team |
| Player role classification (opener/finisher/etc.) | Required | Algorithmic + Manual |
| Predicted XII output | Required | Predicted XII task |
| IPL match count per player | Required | Data Team |
| Wicketkeeper designation | Required | Data Team |

---

## Estimated Effort

**Medium-Large**

### Breakdown
| Component | Effort | Notes |
|-----------|--------|-------|
| Position criteria finalization | Small | This PRD defines; founder validates |
| Metric calculation per position | Medium | Phase-specific metrics needed |
| Ranking algorithm per position | Medium | 9 positions x weighted scoring |
| Overlap handling logic | Small | Clear rules defined |
| Per-team depth chart generation | Medium | 10 teams x 9 positions |
| Cross-team comparison | Small | Aggregation of per-team |
| Depth assessment writing | Medium | Qualitative analysis per team |
| Editorial review | Small | Cricket expert validation |

---

## Founder Decisions Summary

| Question | Decision |
|----------|----------|
| #3 adaptability metric | Yes - create adaptability score |
| Flag teams with no backup keeper | Yes - flag as vulnerability |
| Supporting pacer organization | Split by archetype (PP vs Death) |
| All-rounder organization | BOTH - show in position + AR section |
| Depth ratings format | **Rating out of 10 (with decimals) + what works/doesn't work** |
| Overseas competition tracking | Yes - show overseas count per position |

---

## Relationship to Other Features

### Predicted XII
- Depth Charts show OPTIONS; Predicted XII shows SELECTED combination
- #1 at each position should align with Predicted XII (unless balance constraints)
- Depth Charts explain "why X over Y" that Predicted XII selection implies

### Team Profiles
- Depth Charts feed into team strengths/weaknesses
- "Thin finisher depth" = team vulnerability in profile

### Match Previews (if applicable)
- Depth Charts inform "who might play" discussions
- Rotation/rest decisions reference depth

---

## Example: Mumbai Indians Depth Chart (Illustrative)

### Batting Depth

| Position | #1 | #2 | #3 | Notes |
|----------|----|----|-----|-------|
| Opener | Rohit Sharma | Ishan Kishan | Tilak Varma (emergency) | Rohit captain, Ishan backup opener |
| #3 | Suryakumar Yadav | Tilak Varma | Ishan Kishan | SKY elite #3, versatile |
| Middle #4-5 | Tilak Varma, N Tilak | Dewald Brevis | - | Tilak emerging star |
| Finisher #6-7 | Hardik Pandya, Tim David | Romario Shepherd | - | Elite finishing duo |
| Wicketkeeper | Ishan Kishan (opener) | - | - | Single keeper risk |

### Bowling Depth

| Position | #1 | #2 | Notes |
|----------|----|----|-------|
| Lead Pacer | Jasprit Bumrah | Jofra Archer | Elite options |
| Supporting Pacer | Archer/Shams, Arjun Tendulkar | Akash Madhwal | Archer can lead or support |
| Lead Spinner | Piyush Chawla | Hrithik Shokeen | Spin depth thin |

### Depth Assessment
- **Strongest depth**: Lead Pacer (Bumrah + Archer = elite)
- **Weakest depth**: Spin (after Chawla, options unproven)
- **Key vulnerability**: Only one wicketkeeper (Ishan injury = crisis)
- **Overseas flexibility**: Archer, David, Brevis compete for 2 slots (Bumrah Indian)

---

*PRD APPROVED - Founder Input Incorporated*
*Andy Flower, Cricket Domain Expert*
*2026-02-02*

---

## Gate Approvals

```
FLORENTINO GATE: APPROVED
Reason: Removes critical preparation burden (squad research + position-specific ranking)
while providing non-obvious strategic insights that justify reader value.
Date: 2026-02-02
```
