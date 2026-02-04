# SUPER SELECTOR v3.0

**Statistical Unified Player Evaluation and Ranking SELECTOR**

*Cricket Playbook's proprietary algorithm for predicting optimal IPL Playing XIIs*

---

## Algorithm Overview

SUPER SELECTOR is a constraint-satisfaction algorithm that combines player competency scores, variety optimization, and metrics-based evaluation to generate predicted Playing XIs for IPL teams.

Like FiveThirtyEight's PECOTA (baseball), CARMELO (basketball), and RAPTOR systems, SUPER SELECTOR provides a transparent, data-driven methodology for player evaluation.

---

## Scoring Formula

```
PLAYER_SCORE = BASE + CLASSIFICATION + TAGS + METRICS + (PRICE_BONUS × multiplier)
```

### Components

| Component | Weight | Description |
|-----------|--------|-------------|
| BASE | 50 pts (batters), 40 pts (bowlers) | Starting score |
| CLASSIFICATION | 0-30 pts | Player archetype bonus |
| TAGS | Variable | Phase-specific performance tags |
| METRICS | 0-40 pts | boundary%, consistency, dot_ball% |
| PRICE_BONUS | 5-15% multiplier | Auction investment signal |

---

## Classification Scoring

### Batter Classifications
| Classification | Bonus | Description |
|----------------|-------|-------------|
| Elite Top-Order | +30 | Franchise anchors (Kohli, Rohit) |
| Power Finisher | +25 | Death-overs specialists |
| Aggressive Opener | +25 | Powerplay dominators |
| All-Round Finisher | +20 | Batting all-rounders |
| Anchor | +15 | Middle-overs stabilizers |
| ACCUMULATOR | +12 | Reliable run-scorers |

### Bowler Classifications
| Classification | Bonus | Description |
|----------------|-------|-------------|
| Powerplay Assassin | +25 | New-ball wicket-takers |
| Middle-Overs Spinner | +25 | Economy-focused spin |
| Workhorse Seamer | +20 | Multi-phase workhorses |
| Holding Spinner | +15 | Defensive spinners |
| Expensive Option | +5 | High-risk options |

---

## Metrics-Based Scoring (NEW in v3.0)

### Batting Metrics
| Metric | Threshold | Bonus |
|--------|-----------|-------|
| **Boundary %** | ≥28% | +15 |
| | ≥24% | +10 |
| | ≥20% | +5 |
| **Consistency Index** | ≥55 | +8 |
| | ≥45 | +4 |
| **High Impact %** | ≥50% | +6 |
| | ≥35% | +3 |

### Bowling Metrics
| Metric | Threshold | Bonus |
|--------|-----------|-------|
| **Death Dot Ball %** | ≥35% | +15 |
| | ≥30% | +10 |
| | ≥25% | +5 |
| **Death Economy** | ≤7.0 | +12 |
| | ≤8.5 | +6 |
| | ≥10.5 | -5 |

---

## Entry Point Position Validation

SUPER SELECTOR v3.0 uses historical batting entry point data (`avg_entry_ball`) as the PRIMARY signal for batting position assignment:

| Tier | Entry Ball Range | Positions | Example Players |
|------|------------------|-----------|-----------------|
| 1 | 0-12 | 1-2 (Openers) | Rohit (3.3), Kohli (2.6) |
| 2 | 13-45 | 3-4 (Top Order) | Sanju (25.8), Brevis (41.8) |
| 3 | 46-75 | 5-6 (Middle Order) | Shivam Dube (61.8), Hardik (66.4) |
| 4 | 76-105 | 7-8 (Finishers) | MS Dhoni (105.6), Tim David (91.7) |
| 5 | 105+ or Bowlers | 9-11 (Tail) | Bowlers |

---

## Constraint Satisfaction

### Hard Constraints
| ID | Constraint | Enforcement |
|----|------------|-------------|
| C1 | Captain ≠ Impact Player | IPL rule |
| C2 | Maximum 4 overseas | IPL rule |
| C3 | Minimum 20 overs bowling | Team balance |
| C4 | At least 1 wicketkeeper | Required |
| C5 | At least 1 spinner | Variety |

### Soft Optimization
- Left-hand batter variety in top 6
- Spin/pace balance based on home venue
- Maximize overseas slots (up to 4)

---

## Selection Algorithm

```
1. LOAD DATA
   - Squad rosters
   - Player contracts
   - Batting entry points
   - Batter/bowler metrics

2. SCORE ALL PLAYERS
   - Calculate batting_score
   - Calculate bowling_score
   - Calculate overall_score (weighted by role)

3. SELECT XI
   a. Select wicketkeeper (MUST)
   b. Select openers (tier 1)
   c. Select anchors (tier 2)
   d. Select finishers (tier 3-4)
   e. Select spinners (venue-aware)
   f. Select pace bowlers
   g. Overseas optimization

4. VALIDATE POSITIONS
   - Reorder by entry point tiers
   - Ensure tier 3 stays at positions 5-6
   - Fill gaps with fallback logic

5. CHECK CONSTRAINTS
   - Verify all hard constraints
   - Backtrack if violations

6. SELECT IMPACT PLAYER
   - Best available (captain excluded)
   - Complement XI composition
```

---

## Data Sources

| File | Records | Usage |
|------|---------|-------|
| `ipl_2026_squads.csv` | 231 | Player rosters |
| `ipl_2026_player_contracts.csv` | 231 | Auction prices |
| `batter_entry_points_2023.csv` | 197 | Position validation |
| `batter_consistency_index.csv` | 76 | Batting metrics |
| `bowler_pressure_sequences.csv` | 59 | Bowling metrics |
| `player_tags_2023.json` | - | Phase-specific tags |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-01-15 | Initial algorithm |
| v2.0 | 2026-01-28 | Overseas optimization, captain from CSV |
| **v3.0** | 2026-02-04 | **SUPER SELECTOR**: Metrics scoring, entry point validation, ACCUMULATOR bonus |

---

## Output

SUPER SELECTOR generates:

1. **Consolidated JSON** (`predicted_xii_2026.json`)
   - All 10 teams
   - Full metadata and rationale

2. **Per-team JSON** (`{team}_predicted_xii.json`)
   - Detailed XI with positions
   - Balance metrics
   - Constraint status

3. **Depth Charts** (HTML/Markdown)
   - Visual representation
   - Position depth
   - Key insights

---

## Example Output: CSK

```
1. Ruturaj Gaikwad (Opener) - entry: 4.7
2. Sanju Samson (Wicketkeeper) - entry: 25.8
3. Dewald Brevis (Middle Order) - entry: 41.8
4. [Fallback from tier 4]
5. Shivam Dube (Middle Order) - entry: 61.8  ← Correctly placed!
6. [Fallback]
7. Aman Khan (All-rounder) - entry: 77.9
8. Jamie Overton (Pace Bowler)
9. MS Dhoni (Finisher) - entry: 105.6
10. Noor Ahmad (All-rounder)
11. Khaleel Ahmed (Pace Bowler)
```

---

## Credits

- **Algorithm Design**: Stephen Curry (Analytics Lead)
- **Metrics Integration**: Andy Flower (Domain Expert)
- **Data Engineering**: Brock Purdy (Data Quality)

---

*Generated by Cricket Playbook | IPL 2026 Season*
