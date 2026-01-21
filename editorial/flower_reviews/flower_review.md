# Andy Flower - Cricket Domain Review

**Reviewer:** Andy Flower (Cricket Domain Specialist)
**Sprint:** IPL 2026 Analytics Sprint
**Date:** 2026-01-20

---

## Review Protocol

Each insight/metric is classified as:
- **APPROVE** - Cricket-true, ready for publication
- **CAVEAT** - Valid but requires context/disclaimer
- **CHALLENGE** - Misleading or incorrect, needs rework

---

## Schema & Derived Fields

### match_phase Derivation
**Status:** APPROVE

| Phase | Overs | Cricket Rationale |
|-------|-------|-------------------|
| Powerplay | 0-5 | Fielding restrictions, aggressive batting expected |
| Middle | 6-14 | Building phase, rotations + occasional boundaries |
| Death | 15-19 | Slog overs, high-risk batting, yorkers/variations |

**Notes:** Standard T20 phase definitions. Correctly implemented.

---

### is_wicketkeeper Derivation
**Status:** APPROVE

Derived from `did_keep_wicket = TRUE` in any match. Correctly identifies specialist keepers.

**Notes:** May miss part-time keepers who haven't kept in dataset period. Acceptable limitation.

---

### primary_role Derivation
**Status:** CAVEAT

Logic based on batting vs bowling volume ratios.

**Caveat Required:** "Role derived from historical data; may not reflect current team role or auction designation."

---

## Analytics Metrics

### Strike Rate (SR)
**Status:** APPROVE
**Formula:** `(Runs / Balls) × 100`

Standard cricket metric. Correctly implemented.

---

### Batting Average
**Status:** APPROVE
**Formula:** `Runs / Dismissals`

Correctly handles NOT OUT innings by counting only completed innings (dismissals).

---

### Boundary %
**Status:** APPROVE
**Formula:** `(4s + 6s) / Balls × 100`

**Cricket Insight:** High boundary% with moderate SR indicates clean hitting. Low boundary% with high SR indicates rotation skills.

---

### Dot Ball % (Batting)
**Status:** APPROVE
**Formula:** `Dots / Balls × 100`

**Cricket Insight:** <25% in powerplay = aggressive intent. >35% = anchor role or struggling.

---

### Economy Rate
**Status:** APPROVE
**Formula:** `(Runs / Balls) × 6`

Standard cricket metric. Per-over basis.

---

### Bowling Strike Rate
**Status:** APPROVE
**Formula:** `Balls / Wickets`

Correctly measures wicket-taking frequency.

---

### Wicket Efficiency (Phase Distribution)
**Status:** APPROVE

**Formula:** `% Wickets in Phase - % Overs in Phase`

**Cricket Insight:** This is an innovative metric. Positive values identify phase specialists who outperform their workload. Example:
- Bowler bowls 30% of overs in death
- Takes 45% of wickets in death
- Wicket Efficiency = +15 → Death over specialist

**Recommendation:** Feature prominently in bowler profiles.

---

## Sample Size Discipline

### Classification Thresholds
**Status:** APPROVE

| Level | Batting (balls) | Bowling (balls) | Matchups |
|-------|-----------------|-----------------|----------|
| LOW | <30 | <30 | <6 |
| MEDIUM | 30-99 | 30-99 | 6-19 |
| HIGH | 100+ | 100+ | 20+ |

**Cricket Insight:** Critical for credibility. LOW sample insights should be labeled "indicative only" or excluded from publication.

---

## IPL-Specific Views

### Batter vs Bowler Type
**Status:** APPROVE

Classifications used:
- Fast
- Medium
- Off-spin
- Leg-spin
- Left-arm orthodox
- Left-arm wrist spin

**Notes:** Comprehensive coverage of bowling types. Correctly sourced from squad data.

---

### Franchise Alias Handling
**Status:** APPROVE

| Current | Historical |
|---------|------------|
| Delhi Capitals | Delhi Daredevils |
| Punjab Kings | Kings XI Punjab |
| Royal Challengers Bengaluru | Royal Challengers Bangalore |

**Cricket Insight:** Essential for historical accuracy. Correctly combined in queries.

---

## Stat Pack Tactical Insights

### Death Bowling Options
**Status:** APPROVE

Correctly identifies bowlers by economy in death overs with workload context.

---

### Powerplay Batting Options
**Status:** APPROVE

Filters by SR ≥130 in powerplay with sample size gate.

---

### Spin Vulnerabilities
**Status:** CAVEAT

Identifies batters with SR <115 vs spin types.

**Caveat Required:** "Low sample sizes may skew results. Consider match context (chasing vs setting, pitch conditions)."

---

## Challenges

### No Challenges This Sprint

All insights reviewed are cricket-valid. No misleading metrics identified.

---

## Recommendations for Future Sprints

1. **Add pitch/conditions context** - Spin-friendly vs pace-friendly venues
2. **Batting position awareness** - Opener vs finisher role context
3. **Recent form weighting** - Last 2 seasons vs career (optional)
4. **Head-to-head context** - Venue/phase when matchup occurred

---

## Sign-off

All metrics and insights in v2.0.0 release are **APPROVED** for use, with noted caveats for:
- `primary_role` derivation
- Spin vulnerability analysis

**No predictions or projections included.** Data is historical/observational only.

---

*Andy Flower*
*Cricket Domain Specialist*
