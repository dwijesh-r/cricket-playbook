# Predicted XII - IPL 2026

**Version:** 4.1.0 | **Last Updated:** 2026-02-05

## Overview

This directory contains the predicted playing XI + Impact Player (XII) for all 10 IPL 2026 teams. The predictions are generated using a constraint-satisfaction algorithm with weighted scoring.

## Files

| File | Description |
|------|-------------|
| `predicted_xii_2026.json` | Consolidated predictions for all 10 teams |
| `{team}_predicted_xii.json` | Individual team prediction files (e.g., `mi_predicted_xii.json`) |

## Methodology

### Algorithm Overview

The Predicted XII generator uses a multi-step selection process:

1. **Player Scoring**: Each player receives batting and bowling scores based on:
   - Batter/Bowler classifications (Elite Top-Order, Power Finisher, etc.)
   - Player tags (PP_ELITE, DEATH_SPECIALIST, PROVEN_WICKET_TAKER, etc.)
   - Auction price tier bonuses (15+ Cr: +15%, 10-15 Cr: +10%, 5-10 Cr: +5%)

2. **Constraint Satisfaction**: Hard constraints that must be satisfied:
   - C1: Maximum 4 overseas players
   - C2: Minimum 20 overs bowling coverage
   - C3: At least 1 wicketkeeper
   - C4: Minimum 4 primary bowling options
   - C5: At least 1 spinner

3. **Role-Based Selection**: Players are selected to fill specific roles:
   - Openers (2)
   - Middle Order / Anchors (2-3)
   - Finishers (1-2)
   - All-rounders (2-3)
   - Specialist Bowlers (3-4)

4. **Batting Position Assignment**: Uses historical entry point data from 2023 IPL:
   - Positions 1-2: Openers (avg_entry_ball < 20)
   - Positions 3-4: Top Order (avg_entry_ball 20-40)
   - Positions 5-6: Middle Order (avg_entry_ball 40-70)
   - Positions 7-8: Finishers/All-rounders (avg_entry_ball 70+)
   - Positions 9-11: Specialist Bowlers

### Data Sources

- **Squad Data**: `/data/ipl_2026_squads.csv`
- **Contract Prices**: `/data/ipl_2026_player_contracts.csv`
- **Player Tags**: `/outputs/player_tags_2023.json`
- **Entry Points**: `/outputs/matchups/batter_entry_points_2023.csv`

## Output Schema

```json
{
  "team_name": "Mumbai Indians",
  "team_abbrev": "MI",
  "home_venue": "Wankhede Stadium",
  "venue_bias": "pace",
  "captain": "Hardik Pandya",
  "wicketkeeper": "Quinton de Kock",
  "xi": [
    {
      "batting_position": 1,
      "player_id": "...",
      "player_name": "...",
      "role": "Opener",
      "batting_hand": "Right-hand",
      "is_overseas": false,
      "price_cr": 16.35,
      "rationale": "..."
    }
  ],
  "impact_player": { ... },
  "balance": {
    "overseas_count": 4,
    "bowling_options": 5,
    "spinners": 2,
    "pacers": 3,
    "left_handers_top6": 2
  },
  "constraints_satisfied": true,
  "constraint_violations": [],
  "generation_notes": []
}
```

## Known Players Mappings

### Openers (Positions 1-2)
Based on historical avg_entry_ball data:
- Rohit Sharma (3.3)
- Shubman Gill (4.2)
- Virat Kohli (2.6)
- Yashasvi Jaiswal (1.0)
- Ruturaj Gaikwad (4.7)
- Travis Head (2.5)
- Abhishek Sharma (opens for SRH)
- Sunil Narine (opens for KKR)
- Phil Salt (5.9)
- Quinton de Kock (1.9)

### Middle Order (Positions 5-6)
- Shivam Dube (61.8)
- Suryakumar Yadav (40.7)
- Tilak Varma (51.8)
- Heinrich Klaasen (57.8)
- Nicholas Pooran (61.4)
- Hardik Pandya (66.4)

### Finishers (Positions 7-8)
- MS Dhoni (105.6)
- Rinku Singh (72.2)
- Tim David (91.7)
- Rashid Khan (108.5)
- Andre Russell (84.6)

## Venue Bias

Home venue characteristics influence team composition:

| Team | Venue | Bias |
|------|-------|------|
| CSK | MA Chidambaram Stadium | Spin |
| MI | Wankhede Stadium | Pace |
| RCB | M Chinnaswamy Stadium | Pace |
| KKR | Eden Gardens | Spin |
| DC | Arun Jaitley Stadium | Neutral |
| PBKS | Punjab Cricket Association Stadium | Neutral |
| RR | Sawai Mansingh Stadium | Neutral |
| SRH | Rajiv Gandhi Intl Stadium | Pace |
| GT | Narendra Modi Stadium | Neutral |
| LSG | Ekana Cricket Stadium | Neutral |

## Regenerating Predictions

```bash
python scripts/generators/generate_predicted_xii.py
```

## UI Wireframes

See `docs/specs/WIREFRAMES_V1.md` for the V6 wireframe specification for Predicted XII views.

**Wireframe Features:**
- Mobile-first design (393px × 852px)
- Tabular format for XI display
- Balance box with overseas count
- Archetype breakdown with phase coverage
- Rest of Squad section
- Algorithm confidence notes

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-01 | Initial generation with constraint-satisfaction algorithm |
| 1.1 | 2026-02-02 | Fixed overseas detection, improved batting position logic |
| 1.2 | 2026-02-04 | Added nationality/age data, wireframes V6 reference |

## Author

Stephen Curry - Analytics Lead, Cricket Playbook

---

## Post Task Note: TKT-066 Archive Completion

**Date:** 2026-02-05
**Owner:** Tom Brady

### What Changed
- All 10 IPL 2026 Predicted XII files archived with JSON format
- Consolidated file includes full methodology and constraint documentation
- README complete with algorithm overview, known mappings, and venue bias table

### Assumption Tested
- **Hypothesis:** A constraint-satisfaction algorithm can generate realistic playing XIs
- **Validated:** Yes - the 5 constraints (overseas cap, bowling overs, keeper, bowling options, spinner) produce balanced teams

### Risk Introduced
- Impact player selection depends on squad depth which may vary by match context
- Batting position assignment uses 2023 entry point data - may shift with new roles

### USP of This Change
- **Buyer Value:** Pre-season XI predictions with rationale reduce pre-match prep time
- **Preparation Burden Removed:** No manual lineup construction needed - algorithm handles constraints
