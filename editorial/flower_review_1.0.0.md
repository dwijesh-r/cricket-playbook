# Andy Flower - Cricket Domain Review

**Data Version:** 1.0.0
**Review Date:** 2026-01-19
**Status:** ✅ APPROVE with CAVEATS

---

## Schema Review

### Player Role Derivation

**Current Logic:**
```
- Bowled >50% matches + rarely batted top 7 → Bowler
- Batted top 6 frequently + rarely bowled → Batter
- Both batted and bowled regularly → All-rounder
```

**Cricket Assessment:** ⚠️ CAVEAT

The logic is reasonable but has blind spots:

| Issue | Example | Impact |
|-------|---------|--------|
| Wicket-keepers not identified | MS Dhoni classified as "Batter" | Misses WK role entirely |
| Part-time bowlers | V Kohli bowls occasionally | May incorrectly flag as all-rounder |
| Batting position ≠ role | Jadeja bats 7 but is an all-rounder | Position-based logic can mislead |

**Recommendation:**
- Add `is_wicketkeeper` flag (can derive from stumping dismissals as fielder)
- Consider bowling frequency thresholds more carefully
- Cross-reference with known player archetypes for validation

---

### Batting Position Tracking

**Current Implementation:** Derived from order of appearance at crease

**Cricket Assessment:** ✅ APPROVE

This is correct. In cricket, batting position is determined by when you walk out to bat, not a pre-assigned number. The implementation captures this accurately.

**Note:** Position can vary match-to-match (openers getting rested, night watchmen, etc.) - the per-match tracking handles this well.

---

### Powerplay Tracking

**Current Implementation:** Captures mandatory + batting powerplays from JSON

**Cricket Assessment:** ✅ APPROVE

Good coverage of:
- Standard T20 powerplays (overs 1-6)
- BBL Power Surge (batting team chooses 2 overs)
- The Hundred (25-ball powerplay)

**Note:** Death overs (16-20) are not a "powerplay" but are analytically important. Consider adding a derived `phase` column:
- Powerplay: overs 1-6
- Middle: overs 7-15
- Death: overs 16-20

---

### Wicket Types

**Current Coverage:**
- caught, bowled, lbw, run out, stumped ✅
- caught and bowled ✅
- hit wicket, retired hurt ✅
- obstructing the field, handled the ball ✅

**Cricket Assessment:** ✅ APPROVE

Comprehensive coverage of all dismissal types.

---

## Data Quality Observations

### All-Run 7s (flagged by Kanté)

**Cricket Assessment:** ✅ LEGITIMATE

These are rare but valid:
- Ball hit to outfield, batters run 3
- Fielder overthrows, ball goes to boundary (4 more)
- Total: 7 runs credited to batter

This is correct cricket scoring. Not an error.

---

### Player Name Variations

**Observation:** Same player may appear with different names across sources

**Examples:**
- "V Kohli" vs "Virat Kohli"
- "KL Rahul" vs "Lokesh Rahul"
- "CH Gayle" vs "Chris Gayle"

**Cricket Assessment:** ⚠️ CAVEAT

The Cricsheet player_id handles this well, but display names may confuse users. Consider:
- Standardizing to most common display name
- Adding `full_name` column for formal references

---

## Recommendations for Analytics Layer

1. **Strike Rate Context:** Always show balls faced alongside strike rate (SR of 200 on 5 balls ≠ SR of 200 on 50 balls)

2. **Match Situation:** Consider adding derived columns:
   - `required_run_rate` at each ball
   - `match_phase` (powerplay/middle/death)
   - `innings_position` (chasing vs setting)

3. **Opposition Quality:** Bowling averages without opponent context can mislead

4. **Sample Size Warnings:** Flag any stat with <10 innings or <100 balls

---

## Final Verdict

**Status:** ✅ APPROVED FOR USE

The schema is cricket-sound with minor caveats noted above. Data quality is high. Recommended enhancements are additive, not blockers.

Good foundation for the analytics layer.

---

*Signed: Andy Flower, Cricket Domain Specialist*
