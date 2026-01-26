# Research

Cross-sport analytics research for Cricket Playbook methodology development.

---

## Contents

| Document | Author | Description |
|----------|--------|-------------|
| `pff_grading_system_research.md` | Ime Udoka | PFF (Pro Football Focus) grading methodology |
| `kenpom_methodology_research.md` | Andy Flower | KenPom basketball efficiency metrics |

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

---

## KenPom Research

**Key Concepts:**
- Adjusted efficiency (opponent-normalized)
- Tempo-free statistics (per-possession)
- Four Factors decomposition
- Iterative opponent strength calculation
- Venue park factors

**Cricket Applications:**
- Adjusted Run Rate (AdjRR)
- Cricket's Four Factors (Boundary%, Dot%, Wicket%, Extras%)
- Opposition Strength Index (OSI)
- Cricket Efficiency Margin (CEM)
- Venue normalization

---

## Implementation Priority

| Metric | Editorial Value | Effort | Priority |
|--------|-----------------|--------|----------|
| Four Factors | HIGH | LOW | P0 |
| Venue Park Factors | HIGH | LOW | P0 |
| Opposition Strength Index | HIGH | MEDIUM | P1 |
| Adjusted Strike Rate | HIGH | MEDIUM | P1 |
| Ball-by-Ball Grading | HIGH | HIGH | P2 |

---

*Cricket Playbook v3.1.0*
