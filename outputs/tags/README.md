# Player Tags

Player classification and clustering outputs.

**Last Updated:** 2026-02-02

---

## Files

| File | Records | Description |
|------|---------|-------------|
| `player_tags.json` | 155 players | Multi-tag classifications (all criteria) |
| `player_tags_2023.json` | 155 players | 2023+ filtered version |
| `player_clustering_2023.csv` | 175 players | K-means cluster assignments |
| `bowler_role_tags.csv` | 184 bowlers | Phase-based role tags |

---

## Batter Role Tags (6 Archetypes)

| Tag | Count | Description |
|-----|-------|-------------|
| EXPLOSIVE_OPENER | 15 | Aggressive openers, 163+ SR |
| PLAYMAKER | 24 | Creative stroke-makers, adaptable |
| ANCHOR | 21 | Stabilizers, build innings |
| ACCUMULATOR | 49 | Consistent run-scorers |
| MIDDLE_ORDER | 45 | Middle-order specialists (#3-5) |
| FINISHER | 21 | Death-overs specialists (#5-7) |

---

## Bowler Role Tags (7 Archetypes)

| Tag | Count | Description |
|-----|-------|-------------|
| PACER | 116 | Fast/medium-fast bowlers |
| SPINNER | 68 | Spin bowlers (all types) |
| WORKHORSE | 112 | High-volume, multi-phase bowlers |
| NEW_BALL_SPECIALIST | 43 | Opening bowlers, powerplay focus |
| MIDDLE_OVERS_CONTROLLER | 50 | Middle-phase specialists |
| DEATH_SPECIALIST | 19 | Death-overs specialists |
| PART_TIMER | 44 | Part-time bowling options |

---

## Matchup Tags

| Tag | Criteria |
|-----|----------|
| SPECIALIST_VS_PACE | SR ≥130 AND Avg ≥25 AND BPD ≥20 vs pace |
| SPECIALIST_VS_SPIN | SR ≥130 AND Avg ≥25 AND BPD ≥20 vs spin |
| VULNERABLE_VS_PACE | SR <105 OR Avg <15 OR BPD <15 vs pace |
| VULNERABLE_VS_SPIN | SR <105 OR Avg <15 OR BPD <15 vs spin |

---

## Phase Tags (Bowlers)

| Tag | Economy Threshold | Min Overs |
|-----|-------------------|-----------|
| PP_BEAST | < 7.0 | 30 |
| PP_LIABILITY | > 9.5 | 30 |
| DEATH_BEAST | < 9.0 | 30 |
| DEATH_LIABILITY | > 12.0 AND SR > 18.0 | 30 |

---

## JSON Schema (player_tags.json)

```json
{
  "player_id": "abc123",
  "player_name": "Player Name",
  "team": "MI",
  "role_tags": ["PACER", "WORKHORSE"],
  "matchup_tags": ["SPECIALIST_VS_SPIN"],
  "phase_tags": ["DEATH_BEAST"],
  "batting_cluster": "FINISHER",
  "bowling_cluster": "DEATH_SPECIALIST"
}
```

---

## Regenerating

```bash
python scripts/analysis/player_clustering_v2.py
```

---

*Cricket Playbook v4.0.0*
