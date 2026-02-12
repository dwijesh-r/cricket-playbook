# Research

Cross-sport analytics research for Cricket Playbook methodology development.

---

## Contents

| Document | Author | Status | Description |
|----------|--------|--------|-------------|
| `pff_grading_system_research.md` | Ime Udoka | Research | PFF (Pro Football Focus) grading methodology |
| `kenpom_methodology_research.md` | Andy Flower | Research | KenPom basketball efficiency metrics |
| `cricpom_prototype_spec_020926_v1.md` | Jose Mourinho | **DELIVERED** | CricPom T20 efficiency rating system — full spec + implementation |

---

## CricPom (DELIVERED)

The flagship research output. An opponent-adjusted, venue-normalized, phase-aware efficiency rating system for T20 cricket, inspired by KenPom's college basketball analytics.

**Spec:** `cricpom_prototype_spec_020926_v1.md` (Jose Mourinho, 570+ lines)

**What was built:**
- 5-factor tournament weighting: PQI, Effective CI, Recency, Conditions Similarity, Sample Confidence
- Geometric mean composite formula (not simple average — penalizes weakness in any factor)
- Sigmoid-based confidence scoring: `1 / (1 + exp(-0.02 * (matches - 100)))`
- 14 T20 tournaments weighted and tiered (1A/1B/1C/2)
- 231 IPL 2026 players rated with weighted SR, avg, boundary%, economy, dot%, trust scores

**Implementation Artifacts:**
| Artifact | Location |
|----------|----------|
| Weights engine | `scripts/tkt187_final_weights.py` |
| Weighted composite views | `analytics_weighted_composite_batting`, `analytics_weighted_composite_bowling` |
| Player feed (231 players) | `outputs/cricpom_weighted_feed.json` |
| Tournament weights data | `scripts/the_lab/dashboard/data/tournament_weights.js` |
| Dashboard visualization | [The Lab → Analysis → Tournament Intelligence](https://dwijesh-r.github.io/cricket-playbook/scripts/the_lab/dashboard/analysis.html) |
| Stat pack integration | Section 13 "Cross-Tournament Intelligence" (all 10 teams) |

**Tickets:** TKT-167 (spec) → TKT-187 (weights formula) → TKT-190 (feed generation)

---

## PFF Grading Research

**Key Concepts:**
- Play-by-play grading (-2 to +2 scale)
- Process over outcome evaluation
- Context-aware adjustments
- Multi-grader quality control
- WAR (Wins Above Replacement)

**Cricket Applications:**
- Ball-by-ball grading system
- Isolating individual contribution
- Expected vs actual performance

**Status:** Research only. Ball-by-ball grading deferred to future sprint (IDEA-003).

---

## KenPom Research

**Key Concepts:**
- Adjusted efficiency (opponent-normalized)
- Tempo-free statistics (per-possession)
- Four Factors decomposition
- Iterative opponent strength calculation
- Venue park factors

**Cricket Applications (DELIVERED via CricPom):**
- Adjusted Run Rate (AdjRR) → Weighted SR/Economy composites
- Cricket's Four Factors (Boundary%, Dot%, Wicket%, Extras%) → Phase-aware metrics
- Opposition Strength Index (OSI) → PQI factor in tournament weights
- Cricket Efficiency Margin (CEM) → Composite weight formula
- Venue normalization → Conditions Similarity factor

---

## Implementation Status

| Metric | Editorial Value | Effort | Status |
|--------|-----------------|--------|--------|
| Four Factors | HIGH | LOW | **DONE** (phase views + stat packs) |
| Venue Park Factors | HIGH | LOW | **DONE** (venue_data.js + Strategy Outlook) |
| Opposition Strength Index | HIGH | MEDIUM | **DONE** (PQI in CricPom weights) |
| Adjusted Strike Rate | HIGH | MEDIUM | **DONE** (weighted_composite views) |
| Ball-by-Ball Grading | HIGH | HIGH | Deferred (IDEA-003) |

---

*Cricket Playbook v4.0.0*
