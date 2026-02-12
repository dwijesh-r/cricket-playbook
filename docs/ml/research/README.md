# ML Research

**Owner:** Various (Cross-sport methodology research)

---

## Contents

This directory contains research on analytics methodologies from other sports that inform Cricket Playbook's approach.

| Document | Sport | Key Concepts | Status |
|----------|-------|--------------|--------|
| [PFF Grading System](../../research/pff_grading_system_research.md) | NFL | Play-by-play grading, context-aware adjustments | Research |
| [KenPom Methodology](../../research/kenpom_methodology_research.md) | NCAA Basketball | Adjusted efficiency, tempo-free stats | **DELIVERED** (via CricPom) |
| [CricPom Prototype Spec](../../research/cricpom_prototype_spec_020926_v1.md) | T20 Cricket | Tournament-weighted efficiency ratings | **DELIVERED** |

---

## Cricket Adaptations

### From PFF (Pro Football Focus)
- **Concept:** Play-by-play grading (-2 to +2)
- **Cricket Application:** Ball-by-ball impact scoring
- **Status:** Research phase (IDEA-003)

### From KenPom → CricPom (DELIVERED)
- **Concept:** Adjusted efficiency metrics
- **Cricket Application:** Opponent-adjusted, venue-normalized, phase-aware T20 ratings
- **Status:** Delivered in Sprint 4.0 (TKT-167 spec → TKT-187 weights → TKT-190 feed)
- **Outputs:**
  - `outputs/cricpom_weighted_feed.json` — 231 IPL 2026 players with weighted composites
  - `scripts/tkt187_final_weights.py` — 5-factor geometric mean tournament weighting engine
  - `analytics_weighted_composite_batting/bowling` — DuckDB views
  - The Lab → Analysis → Tournament Intelligence (dashboard visualization)
  - Stat packs Section 13 "Cross-Tournament Intelligence" (all 10 teams)

---

## Related Ideas

- **IDEA-002:** CricPom — **DELIVERED** (see `docs/research/cricpom_prototype_spec_020926_v1.md`)
- **IDEA-003:** Win Probability model — Future sprint candidate

---

*Research compiled by Ime Udoka, Andy Flower, and Jose Mourinho*
