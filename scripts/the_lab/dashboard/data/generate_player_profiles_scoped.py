#!/usr/bin/env python3
"""
Generate multi-scope player profiles JS file for the Statsledge dashboard.
Queries DuckDB analytics views across 4 scopes (IPL since2023, IPL alltime, T20 since2023, T20 alltime)
and outputs a JS constant PLAYER_PROFILES_SCOPED.
"""

import json
import duckdb
from collections import defaultdict

DB_PATH = "/Users/dwijeshreddy/cricket-playbook/data/cricket_playbook.duckdb"
OUTPUT_PATH = (
    "/Users/dwijeshreddy/cricket-playbook/scripts/the_lab/dashboard/data/player_profiles_scoped.js"
)

con = duckdb.connect(DB_PATH, read_only=True)

# ---------------------------------------------------------------------------
# 1. Load IPL 2026 squad player_ids and full names
# ---------------------------------------------------------------------------
squad_rows = con.execute("SELECT player_id, player_name FROM ipl_2026_squads").fetchall()
squad = {pid: pname for pid, pname in squad_rows}
squad_ids = set(squad.keys())
print(f"Loaded {len(squad)} squad players")

# ---------------------------------------------------------------------------
# 2. Build team-name -> abbreviation map from dim_team
# ---------------------------------------------------------------------------
team_abbr = {}
for row in con.execute("SELECT team_name, short_name FROM dim_team").fetchall():
    team_abbr[row[0]] = row[1]
# Special handling: both RCB names map to RCB
team_abbr.setdefault("Royal Challengers Bangalore", "RCB")
team_abbr.setdefault("Royal Challengers Bengaluru", "RCB")


# ---------------------------------------------------------------------------
# 3. Define view configs per scope
# ---------------------------------------------------------------------------
def r2(v):
    """Round to 2 decimals, handle None."""
    if v is None:
        return None
    return round(float(v), 2)


# Scope definitions: (scope_key, batter_phase_view, bowler_phase_view, batter_vs_type_view, batter_vs_team_view, bowler_vs_team_view)
SCOPES = [
    {
        "key": "ipl_since2023",
        "batter_phase": "analytics_ipl_batter_phase_since2023",
        "bowler_phase": "analytics_ipl_bowler_phase_since2023",
        "batter_vs_type": "analytics_ipl_batter_vs_bowler_type_since2023",
        "batter_vs_team": "analytics_ipl_batter_vs_team_since2023",
        "bowler_vs_team": "analytics_ipl_bowler_vs_team_since2023",
    },
    {
        "key": "ipl_alltime",
        "batter_phase": "analytics_ipl_batter_phase_alltime",
        "bowler_phase": "analytics_ipl_bowler_phase_alltime",
        "batter_vs_type": "analytics_ipl_batter_vs_bowler_type_alltime",
        "batter_vs_team": "analytics_ipl_batter_vs_team_alltime",
        "bowler_vs_team": "analytics_ipl_bowler_vs_team_alltime",
    },
    {
        "key": "all_t20_since2023",
        "batter_phase": "analytics_t20_batter_phase_since2023",
        "bowler_phase": "analytics_t20_bowler_phase_since2023",
        "batter_vs_type": "analytics_t20_batter_vs_bowler_type_since2023",
        "batter_vs_team": None,
        "bowler_vs_team": None,
    },
    {
        "key": "all_t20_alltime",
        "batter_phase": "analytics_t20_batter_phase_alltime",
        "bowler_phase": "analytics_t20_bowler_phase_alltime",
        "batter_vs_type": "analytics_t20_batter_vs_bowler_type_alltime",
        "batter_vs_team": None,
        "bowler_vs_team": None,
    },
]

# ---------------------------------------------------------------------------
# 4. Query helpers
# ---------------------------------------------------------------------------


def fetch_batter_phase(view):
    """Returns {player_id: {phase: {...}}}"""
    rows = con.execute(f"""
        SELECT player_id, match_phase, strike_rate, batting_average, boundary_pct, balls_faced, runs
        FROM {view}
    """).fetchall()
    result = defaultdict(dict)
    for pid, phase, sr, avg, bpct, balls, runs in rows:
        if pid not in squad_ids:
            continue
        result[pid][phase] = {
            "sr": r2(sr),
            "avg": r2(avg),
            "boundary_pct": r2(bpct),
            "balls": int(balls) if balls else 0,
            "runs": int(runs) if runs else 0,
        }
    return result


def fetch_bowler_phase(view):
    """Returns {player_id: {phase: {...}}}"""
    rows = con.execute(f"""
        SELECT player_id, match_phase, economy_rate, bowling_average, wickets, overs
        FROM {view}
    """).fetchall()
    result = defaultdict(dict)
    for pid, phase, econ, avg, wkts, overs in rows:
        if pid not in squad_ids:
            continue
        result[pid][phase] = {
            "economy": r2(econ),
            "avg": r2(avg),
            "wickets": int(wkts) if wkts else 0,
            "overs": r2(overs),
        }
    return result


def fetch_batter_vs_type(view):
    """Returns {player_id: {bowling_type: {...}}}"""
    # Uses batter_id instead of player_id
    rows = con.execute(f"""
        SELECT batter_id, bowler_type, strike_rate, average, balls, runs
        FROM {view}
    """).fetchall()
    result = defaultdict(dict)
    for pid, btype, sr, avg, balls, runs in rows:
        if pid not in squad_ids:
            continue
        result[pid][btype] = {
            "sr": r2(sr),
            "avg": r2(avg),
            "balls": int(balls) if balls else 0,
            "runs": int(runs) if runs else 0,
        }
    return result


def fetch_batter_vs_team(view):
    """Returns {player_id: {best_3: [...], worst_3: [...]}}"""
    rows = con.execute(f"""
        SELECT batter_id, opposition, innings, balls, runs, strike_rate, average
        FROM {view}
        WHERE balls >= 10
    """).fetchall()
    # Group by player
    player_data = defaultdict(list)
    for pid, opp, inn, balls, runs, sr, avg in rows:
        if pid not in squad_ids:
            continue
        abbr = team_abbr.get(opp, opp)
        player_data[pid].append(
            {
                "team": abbr,
                "sr": r2(sr),
                "avg": r2(avg),
                "innings": int(inn) if inn else 0,
                "runs": int(runs) if runs else 0,
                "balls": int(balls) if balls else 0,
            }
        )
    result = {}
    for pid, entries in player_data.items():
        sorted_by_sr = sorted(entries, key=lambda x: x["sr"] if x["sr"] is not None else 0)
        best_3 = sorted_by_sr[-3:][::-1]  # highest SR
        worst_3 = sorted_by_sr[:3]  # lowest SR
        result[pid] = {"best_3": best_3, "worst_3": worst_3}
    return result


def fetch_bowler_vs_team(view):
    """Returns {player_id: {best_3: [...], worst_3: [...]}}"""
    rows = con.execute(f"""
        SELECT bowler_id, opposition, matches, balls, runs_conceded, wickets, economy, strike_rate, average
        FROM {view}
        WHERE balls >= 12
    """).fetchall()
    player_data = defaultdict(list)
    for pid, opp, matches, balls, rc, wkts, econ, sr, avg in rows:
        if pid not in squad_ids:
            continue
        abbr = team_abbr.get(opp, opp)
        player_data[pid].append(
            {
                "team": abbr,
                "economy": r2(econ),
                "sr": r2(sr),
                "avg": r2(avg),
                "wickets": int(wkts) if wkts else 0,
                "balls": int(balls) if balls else 0,
            }
        )
    result = {}
    for pid, entries in player_data.items():
        sorted_by_econ = sorted(
            entries, key=lambda x: x["economy"] if x["economy"] is not None else 999
        )
        best_3 = sorted_by_econ[:3]  # lowest economy
        worst_3 = sorted_by_econ[-3:][::-1]  # highest economy
        result[pid] = {"best_3": best_3, "worst_3": worst_3}
    return result


# ---------------------------------------------------------------------------
# 5. Build profiles
# ---------------------------------------------------------------------------
profiles = defaultdict(dict)

for scope in SCOPES:
    scope_key = scope["key"]
    print(f"\nProcessing scope: {scope_key}")

    bat_phase = fetch_batter_phase(scope["batter_phase"])
    bowl_phase = fetch_bowler_phase(scope["bowler_phase"])
    bat_vs_type = fetch_batter_vs_type(scope["batter_vs_type"])

    bat_vs_team = fetch_batter_vs_team(scope["batter_vs_team"]) if scope["batter_vs_team"] else {}
    bowl_vs_team = fetch_bowler_vs_team(scope["bowler_vs_team"]) if scope["bowler_vs_team"] else {}

    # Collect all player_ids that have data in this scope
    all_pids = set()
    all_pids.update(bat_phase.keys())
    all_pids.update(bowl_phase.keys())
    all_pids.update(bat_vs_type.keys())
    all_pids.update(bat_vs_team.keys())
    all_pids.update(bowl_vs_team.keys())

    count = 0
    for pid in all_pids:
        pname = squad.get(pid)
        if not pname:
            continue

        scope_data = {}

        # Batting
        batting = {}
        if pid in bat_phase:
            batting["phase"] = bat_phase[pid]
        if pid in bat_vs_type:
            batting["vs_bowling_type"] = bat_vs_type[pid]
        if pid in bat_vs_team:
            batting["vs_teams"] = bat_vs_team[pid]
        if batting:
            scope_data["batting"] = batting

        # Bowling
        bowling = {}
        if pid in bowl_phase:
            bowling["phase"] = bowl_phase[pid]
        if pid in bowl_vs_team:
            bowling["vs_teams"] = bowl_vs_team[pid]
        if bowling:
            scope_data["bowling"] = bowling

        if scope_data:
            profiles[pname][scope_key] = scope_data
            count += 1

    print(f"  -> {count} players with data")

con.close()

# ---------------------------------------------------------------------------
# 6. Write JS file
# ---------------------------------------------------------------------------
js_content = (
    "const PLAYER_PROFILES_SCOPED = "
    + json.dumps(dict(profiles), indent=2, ensure_ascii=False)
    + ";\n"
)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"\nWrote {len(profiles)} player profiles to {OUTPUT_PATH}")
print(f"File size: {len(js_content):,} bytes")
