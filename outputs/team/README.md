# Team Data

Team-level aggregated data including venue records and squad experience.

**Last Updated:** 2026-02-02

---

## Files

| File | Records | Description |
|------|---------|-------------|
| `team_venue_records.csv` | ~100 | Team win/loss by venue (all time) |
| `team_venue_records_by_year.csv` | ~250 | Yearly venue breakdown |
| `ipl_2026_squad_experience.csv` | 231 | Squad experience metrics |

---

## Venue Records Schema

| Column | Description |
|--------|-------------|
| `team` | Team abbreviation |
| `venue` | Venue name |
| `matches` | Total matches played |
| `wins` | Wins at venue |
| `losses` | Losses at venue |
| `win_pct` | Win percentage |
| `avg_score_batting_first` | Average score batting first |
| `avg_score_chasing` | Average score chasing |

---

## IPL 2026 Teams

| Abbreviation | Full Name |
|--------------|-----------|
| CSK | Chennai Super Kings |
| DC | Delhi Capitals |
| GT | Gujarat Titans |
| KKR | Kolkata Knight Riders |
| LSG | Lucknow Super Giants |
| MI | Mumbai Indians |
| PBKS | Punjab Kings |
| RCB | Royal Challengers Bengaluru |
| RR | Rajasthan Royals |
| SRH | Sunrisers Hyderabad |

---

## Squad Experience Metrics

| Metric | Description |
|--------|-------------|
| `ipl_matches` | Total IPL matches played |
| `ipl_runs` / `ipl_wickets` | Career IPL stats |
| `t20i_matches` | International T20 experience |
| `experience_tier` | HIGH / MEDIUM / LOW |

---

## Regenerating

```bash
python scripts/generators/sprint_3_p1_features.py
```

---

*Cricket Playbook v4.0.0*
