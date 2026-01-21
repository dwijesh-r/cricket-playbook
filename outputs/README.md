# Outputs

Generated data artifacts from analytics scripts.

## Contents

| File | Description | Script |
|------|-------------|--------|
| `player_tags.json` | Multi-tag classification for 155 players | `player_clustering_v2.py` |
| `bowler_handedness_matchup.csv` | LHB/RHB matchup analysis (140 bowlers) | `bowler_handedness_matchup.py` |
| `ipl_2026_squad_experience.csv` | Squad experience metrics (234 players) | `generate_experience_csv.py` |
| `manifest.json` | Data generation manifest | Various |
| `schema.md` | Schema documentation | `ingest.py` |

## Regenerating Outputs

```bash
# Regenerate experience CSV
python scripts/generate_experience_csv.py

# Regenerate player clustering and tags
python scripts/player_clustering_v2.py

# Regenerate LHB/RHB matchup analysis
python scripts/bowler_handedness_matchup.py
```

## Tags System

The `player_tags.json` contains:

**Batter Tags:**
- Primary archetypes: EXPLOSIVE_OPENER, PLAYMAKER, ANCHOR, FINISHER, ACCUMULATOR
- Secondary tags: PP_DOMINATOR, DEATH_SPECIALIST, SPIN_SPECIALIST, etc.

**Bowler Tags:**
- Primary archetypes: NEW_BALL_SPECIALIST, MIDDLE_OVERS_CONTROLLER, DEATH_SPECIALIST, etc.
- Handedness tags: LHB_SPECIALIST, RHB_SPECIALIST, LHB_VULNERABLE, RHB_VULNERABLE

---

*Cricket Playbook v2.5.0*
