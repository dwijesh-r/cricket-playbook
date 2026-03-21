#!/usr/bin/env python3
"""
Generate bowler_usage.js from DuckDB for the IPL 2025 dashboard.
Produces a match-by-match heatmap: rows=bowlers, columns=overs 1-20.
"""

import json
import duckdb
from collections import defaultdict

DB_PATH = "data/cricket_playbook.duckdb"
OUT_PATH = "scripts/the_lab/dashboard/data/bowler_usage.js"

con = duckdb.connect(DB_PATH, read_only=True)

# ── 1. Team abbreviation map ────────────────────────────────────────
teams = {
    row[0]: {"name": row[1], "abbr": row[2]}
    for row in con.execute("""
        SELECT DISTINCT t.team_id, t.team_name, t.short_name
        FROM dim_match m
        JOIN dim_team t ON t.team_id IN (m.team1_id, m.team2_id)
        WHERE m.tournament_id = 'indian_premier_league' AND m.season = '2025'
    """).fetchall()
}

# ── 2. Match metadata ───────────────────────────────────────────────
matches_meta = {}
for row in con.execute("""
    SELECT m.match_id, m.match_date, m.team1_id, m.team2_id,
           v.venue_name, v.city
    FROM dim_match m
    LEFT JOIN dim_venue v ON m.venue_id = v.venue_id
    WHERE m.tournament_id = 'indian_premier_league' AND m.season = '2025'
    ORDER BY m.match_date
""").fetchall():
    matches_meta[row[0]] = {
        "match_id": row[0],
        "date": row[1],
        "team1_id": row[2],
        "team2_id": row[3],
        "venue": row[4] or "",
        "city": row[5] or "",
    }

# ── 3. Ball-level aggregation: bowler per over per match per innings ─
rows = con.execute("""
    SELECT
        fb.match_id,
        fb.innings,
        fb.bowling_team_id,
        fb.batting_team_id,
        fb.over,
        p.current_name AS bowler_name,
        COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) AS legal_balls,
        SUM(fb.total_runs) AS runs,
        SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets,
        SUM(CASE WHEN fb.total_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) AS dots
    FROM fact_ball fb
    JOIN dim_match m ON fb.match_id = m.match_id
    JOIN dim_player p ON fb.bowler_id = p.player_id
    WHERE m.tournament_id = 'indian_premier_league' AND m.season = '2025'
    GROUP BY 1, 2, 3, 4, 5, 6
    ORDER BY fb.match_id, fb.innings, fb.over
""").fetchall()

con.close()

# ── 4. Structure: team_abbr -> list of match-innings entries ────────
# Key = (team_abbr, match_id, innings)
team_data = defaultdict(list)  # team_abbr -> [match_entry, ...]

# Intermediate: (bowling_team_id, match_id, innings) -> {over_num: {...}}
match_innings = defaultdict(dict)
match_innings_meta = {}

for r in rows:
    match_id, innings, bowl_team_id, bat_team_id, over_0idx, bowler, legal, runs, wkts, dots = r
    over_num = over_0idx + 1  # 1-indexed

    key = (bowl_team_id, match_id, innings)
    match_innings[key][over_num] = {
        "bowler": bowler,
        "runs": int(runs),
        "wickets": int(wkts),
        "dots": int(dots),
        "legal_balls": int(legal),
    }
    match_innings_meta[key] = (match_id, bat_team_id)

# Build final structure
for (bowl_team_id, match_id, innings), overs_dict in match_innings.items():
    if bowl_team_id not in teams:
        continue
    abbr = teams[bowl_team_id]["abbr"]
    meta = matches_meta.get(match_id, {})
    bat_team_id = match_innings_meta[(bowl_team_id, match_id, innings)][1]
    opponent_abbr = teams.get(bat_team_id, {}).get("abbr", "???")

    entry = {
        "match_id": match_id,
        "date": meta.get("date", ""),
        "opponent": opponent_abbr,
        "venue": meta.get("venue", ""),
        "city": meta.get("city", ""),
        "innings": int(innings),
        "overs": {str(k): v for k, v in sorted(overs_dict.items())},
    }
    team_data[abbr].append(entry)

# Sort each team's matches by date then innings
for abbr in team_data:
    team_data[abbr].sort(key=lambda e: (e["date"], e["innings"]))

# Build final object with team metadata
output = {}
for abbr in sorted(team_data.keys()):
    # Find full name
    full_name = next((t["name"] for t in teams.values() if t["abbr"] == abbr), abbr)
    output[abbr] = {
        "team_name": full_name,
        "matches": team_data[abbr],
    }

# ── 5. Write JS file ───────────────────────────────────────────────
js_content = (
    "// Auto-generated: IPL 2025 bowler usage data (match-by-match, over-by-over)\n"
    "// Generated from cricket_playbook.duckdb\n"
    "// Rows = bowlers, Columns = overs 1-20, per match per team\n"
    "const BOWLER_USAGE = " + json.dumps(output, indent=2) + ";\n"
)

with open(OUT_PATH, "w") as f:
    f.write(js_content)

# Summary
total_matches = sum(len(v["matches"]) for v in output.values())
print(f"Written {OUT_PATH}")
print(f"Teams: {len(output)}")
print(f"Total match-innings entries: {total_matches}")
for abbr in sorted(output.keys()):
    print(f"  {abbr}: {len(output[abbr]['matches'])} match-innings")
