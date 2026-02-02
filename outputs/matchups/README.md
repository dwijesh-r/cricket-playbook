# Matchups

Head-to-head performance analysis for batters vs bowling types and bowlers vs batting handedness.

**Last Updated:** 2026-02-02

---

## Files

| File | Records | Description |
|------|---------|-------------|
| `batter_bowling_type_matchup.csv` | ~800 | Batter performance vs pace/spin (all time) |
| `batter_bowling_type_matchup_2023.csv` | ~400 | 2023+ filtered version |
| `batter_bowling_type_detail.csv` | ~4,000 | Detailed by 6 bowling styles |
| `batter_bowling_type_detail_2023.csv` | ~2,000 | 2023+ filtered version |
| `bowler_handedness_matchup.csv` | ~400 | Bowler performance vs LHB/RHB |
| `bowler_handedness_matchup_2023.csv` | ~300 | 2023+ filtered version |
| `batter_entry_points.csv` | 150 | Batter entry position data |
| `batter_entry_points_2023.csv` | 197 | 2023+ with thresholds |

---

## Bowling Styles

The 6 bowling styles tracked:

| Style | Code | Coverage |
|-------|------|----------|
| Right-arm pace | `right_arm_pace` | 49.4% |
| Left-arm pace | `left_arm_pace` | 13.6% |
| Right-arm off-spin | `right_arm_offspin` | 12.4% |
| Right-arm leg-spin | `right_arm_legspin` | 11.8% |
| Left-arm orthodox | `left_arm_orthodox` | 10.4% |
| Left-arm wrist spin | `left_arm_wristspin` | 1.2% |

---

## Entry Point Thresholds

| Classification | Average Entry Ball |
|----------------|-------------------|
| TOP_ORDER | < 30 |
| MIDDLE_ORDER | 30 - 72 |
| LOWER_ORDER | > 72 |

---

## Key Metrics

| Metric | Description |
|--------|-------------|
| `runs` | Total runs scored |
| `balls` | Total balls faced |
| `dismissals` | Times dismissed |
| `strike_rate` | (Runs / Balls) × 100 |
| `average` | Runs / Dismissals |
| `balls_per_dismissal` | Balls / Dismissals |

---

## Specialist/Vulnerable Tags

**Specialist** (all three required):
- Strike Rate ≥ 130
- Average ≥ 25
- Balls per Dismissal ≥ 20

**Vulnerable** (any one triggers):
- Strike Rate < 105
- Average < 15
- Balls per Dismissal < 15

---

## Regenerating

```bash
python scripts/analysis/batter_bowling_type_matchup.py
python scripts/analysis/bowler_handedness_matchup.py
```

---

*Cricket Playbook v4.0.0*
