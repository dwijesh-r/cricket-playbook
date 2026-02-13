#!/usr/bin/env python3
"""
The Lab - Data Update Script
Regenerates JavaScript data files from source JSON/CSV outputs.

Usage:
    python scripts/the_lab/update_the_lab.py

This script reads from:
    - outputs/predicted_xii/*.json
    - outputs/depth_charts/*.json
    - outputs/tags/player_tags.json

And generates:
    - scripts/the_lab/dashboard/data/teams.js
    - scripts/the_lab/dashboard/data/predicted_xii.js
    - scripts/the_lab/dashboard/data/depth_charts.js
    - scripts/the_lab/dashboard/data/players.js
"""

import csv
import json
from datetime import datetime
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
DASHBOARD_DATA_DIR = ROOT_DIR / "scripts" / "the_lab" / "dashboard" / "data"

# Team metadata (static)
TEAMS_META = {
    "MI": {
        "name": "Mumbai Indians",
        "fullName": "Mumbai Indians",
        "homeVenue": "Wankhede Stadium",
        "venueBias": "pace",
        "primaryColor": "#004ba0",
        "secondaryColor": "#d4af37",
        "titles": 5,
        "captain": "Hardik Pandya",
        "coach": "Mahela Jayawardene",
        "icon": "🔵",
    },
    "CSK": {
        "name": "Chennai Super Kings",
        "fullName": "Chennai Super Kings",
        "homeVenue": "MA Chidambaram Stadium",
        "venueBias": "spin",
        "primaryColor": "#ffc20e",
        "secondaryColor": "#0081e9",
        "titles": 5,
        "captain": "Ruturaj Gaikwad",
        "coach": "Stephen Fleming",
        "icon": "🦁",
    },
    "RCB": {
        "name": "Royal Challengers",
        "fullName": "Royal Challengers Bengaluru",
        "homeVenue": "M Chinnaswamy Stadium",
        "venueBias": "pace",
        "primaryColor": "#d4213d",
        "secondaryColor": "#000000",
        "titles": 1,
        "captain": "Rajat Patidar",
        "coach": "Andy Flower",
        "icon": "🔴",
        "reigning": True,
    },
    "KKR": {
        "name": "Knight Riders",
        "fullName": "Kolkata Knight Riders",
        "homeVenue": "Eden Gardens",
        "venueBias": "spin",
        "primaryColor": "#3a225d",
        "secondaryColor": "#d4af37",
        "titles": 3,
        "captain": "Ajinkya Rahane",
        "coach": "Abhishek Nayar",
        "icon": "💜",
    },
    "DC": {
        "name": "Delhi Capitals",
        "fullName": "Delhi Capitals",
        "homeVenue": "Arun Jaitley Stadium",
        "venueBias": "neutral",
        "primaryColor": "#0078bc",
        "secondaryColor": "#ef1b23",
        "titles": 0,
        "captain": "Axar Patel",
        "coach": "Hemang Badani",
        "icon": "🔷",
    },
    "PBKS": {
        "name": "Punjab Kings",
        "fullName": "Punjab Kings",
        "homeVenue": "PCA Stadium, Mohali",
        "venueBias": "neutral",
        "primaryColor": "#ed1b24",
        "secondaryColor": "#a7a9ac",
        "titles": 0,
        "captain": "Shreyas Iyer",
        "coach": "Ricky Ponting",
        "icon": "🦁",
    },
    "RR": {
        "name": "Rajasthan Royals",
        "fullName": "Rajasthan Royals",
        "homeVenue": "Sawai Mansingh Stadium",
        "venueBias": "neutral",
        "primaryColor": "#ea1a85",
        "secondaryColor": "#254aa5",
        "titles": 1,
        "captain": "Riyan Parag",
        "coach": "Kumar Sangakkara",
        "icon": "👑",
    },
    "SRH": {
        "name": "Sunrisers",
        "fullName": "Sunrisers Hyderabad",
        "homeVenue": "Rajiv Gandhi Intl Stadium",
        "venueBias": "pace",
        "primaryColor": "#f7a721",
        "secondaryColor": "#000000",
        "titles": 1,
        "captain": "Pat Cummins",
        "coach": "Daniel Vettori",
        "icon": "🌅",
    },
    "GT": {
        "name": "Gujarat Titans",
        "fullName": "Gujarat Titans",
        "homeVenue": "Narendra Modi Stadium",
        "venueBias": "neutral",
        "primaryColor": "#1c1c1c",
        "secondaryColor": "#d5a239",
        "titles": 1,
        "captain": "Shubman Gill",
        "coach": "Ashish Nehra",
        "icon": "🦁",
    },
    "LSG": {
        "name": "Lucknow Giants",
        "fullName": "Lucknow Super Giants",
        "homeVenue": "Ekana Cricket Stadium",
        "venueBias": "neutral",
        "primaryColor": "#a72056",
        "secondaryColor": "#ffcc00",
        "titles": 0,
        "captain": "Rishabh Pant",
        "coach": "Justin Langer",
        "icon": "🦸",
    },
}

TEAM_ORDER = ["MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"]


def load_predicted_xii():
    """Load consolidated predicted XII data."""
    path = OUTPUTS_DIR / "predicted_xii" / "predicted_xii_2026.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def load_depth_charts():
    """Load depth chart data for each team."""
    depth_charts = {}
    for team in TEAM_ORDER:
        path = OUTPUTS_DIR / "depth_charts" / f"{team.lower()}_depth_chart.json"
        if path.exists():
            with open(path) as f:
                depth_charts[team] = json.load(f)
    return depth_charts


def load_player_tags():
    """Load player tags data."""
    path = OUTPUTS_DIR / "tags" / "player_tags.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def generate_teams_js():
    """Generate teams.js with team metadata."""
    timestamp = datetime.now().isoformat()
    js_content = f"""/**
 * The Lab - Team Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 */

const TEAMS = {{
"""
    for abbrev, meta in TEAMS_META.items():
        reigning_line = ""
        if meta.get("reigning"):
            reigning_line = ",\n        reigning: true"
        js_content += f"""    {abbrev}: {{
        abbrev: "{abbrev}",
        name: "{meta["name"]}",
        fullName: "{meta["fullName"]}",
        homeVenue: "{meta["homeVenue"]}",
        venueBias: "{meta["venueBias"]}",
        primaryColor: "{meta["primaryColor"]}",
        secondaryColor: "{meta.get("secondaryColor", meta["primaryColor"])}",
        titles: {meta["titles"]},
        captain: "{meta.get("captain", "")}",
        coach: "{meta.get("coach", "")}",
        icon: "{meta["icon"]}"{reigning_line}
    }},
"""

    js_content += """};

const TEAM_ORDER = ["MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"];

const QUICK_STATS = {
    totalTeams: 10,
    totalPlayers: 231,
    matchesAnalyzed: 219,
    totalReports: 142,
    dataRange: "2023-2025"
};
"""

    return js_content


def generate_predicted_xii_js(data):
    """Generate predicted_xii.js from source data."""
    if not data:
        return "// No predicted XII data found\nconst PREDICTED_XII = {};\nconst DEPTH_CHART_RATINGS = {};"

    timestamp = datetime.now().isoformat()
    generated_at = data.get("generated_at", "")
    version = data.get("version", "")
    algorithm_name = data.get("algorithm_name", "SUPER SELECTOR")

    js_content = f"""/**
 * The Lab - Predicted XII Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 * Algorithm: {algorithm_name}
 */

const PREDICTED_XII_META = {{
    generatedAt: "{generated_at}",
    version: "{version}",
    algorithmName: "{algorithm_name}"
}};

const PREDICTED_XII = {{
"""

    teams_data = data.get("teams", {})

    for abbrev in TEAM_ORDER:
        if abbrev not in teams_data:
            continue

        team = teams_data[abbrev]
        xi_players = []

        for player in team.get("xi", []):
            xi_players.append(
                f"""            {{ position: {player.get("batting_position", 0)}, name: "{player.get("player_name", "")}", role: "{player.get("role", "")}", batting: "{player.get("batting_hand", "")}", overseas: {"true" if player.get("is_overseas") else "false"}, price: {player.get("price_cr", 0)} }}"""
            )

        impact = team.get("impact_player", {})
        balance = team.get("balance", {})

        # Join xi_players outside f-string for Python 3.9 compatibility
        xi_joined = ",\n".join(xi_players)

        js_content += f"""    {abbrev}: {{
        teamName: "{team.get("team_name", "")}",
        teamAbbrev: "{abbrev}",
        homeVenue: "{team.get("home_venue", "")}",
        venueBias: "{team.get("venue_bias", "")}",
        captain: "{team.get("captain", "")}",
        wicketkeeper: "{team.get("wicketkeeper", "")}",
        xi: [
{xi_joined}
        ],
        impactPlayer: {{ name: "{impact.get("player_name", "")}", role: "{impact.get("role", "")}", price: {impact.get("price_cr", 0)} }},
        balance: {{ overseas: {balance.get("overseas_count", 0)}, bowlingOptions: {balance.get("bowling_options", 0)}, spinners: {balance.get("spinners", 0)}, pacers: {balance.get("pacers", 0)}, leftHandersTop6: {balance.get("left_handers_top6", 0)} }},
        constraintsSatisfied: {"true" if team.get("constraints_satisfied") else "false"}
    }},
"""

    js_content += "};\n"
    return js_content


def generate_depth_charts_js(depth_charts):
    """Generate depth_charts.js with ratings summary."""
    timestamp = datetime.now().isoformat()
    js_content = f"""/**
 * The Lab - Depth Chart Ratings
 * Auto-generated: {timestamp}
 */

const DEPTH_CHART_RATINGS = {{
"""

    for abbrev in TEAM_ORDER:
        if abbrev not in depth_charts:
            js_content += f'    {abbrev}: {{ overall: 0, strongest: "N/A", weakest: "N/A" }},\n'
            continue

        chart = depth_charts[abbrev]
        js_content += f"""    {abbrev}: {{ overall: {chart.get("overall_rating", 0)}, strongest: "{chart.get("strongest_position", "")}", weakest: "{chart.get("weakest_position", "")}" }},
"""

    js_content += "};\n"
    return js_content


def load_consolidated_depth_charts():
    """Load the consolidated depth charts file with all position details."""
    path = OUTPUTS_DIR / "depth_charts" / "depth_charts_2026.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def generate_full_depth_charts_js(consolidated_data):
    """Generate full inline depth charts with all positions and players."""
    if not consolidated_data:
        return "// No depth chart data found\nconst FULL_DEPTH_CHARTS = {};"

    timestamp = datetime.now().isoformat()
    js_content = f"""/**
 * The Lab - Full Depth Charts Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 */

const FULL_DEPTH_CHARTS = {{
"""

    teams_data = consolidated_data.get("teams", {})

    for abbrev in TEAM_ORDER:
        if abbrev not in teams_data:
            js_content += f"    {abbrev}: {{ positions: [] }},\n"
            continue

        team = teams_data[abbrev]
        positions_data = team.get("positions", {})

        # Position order for display
        position_order = [
            "opener",
            "number_3",
            "middle_order",
            "finisher",
            "wicketkeeper",
            "allrounder_batting",
            "allrounder_bowling",
            "right_arm_pace",
            "left_arm_pace",
            "off_spin",
            "leg_spin",
            "left_arm_spin",
            "middle_overs_specialist",
        ]

        positions_js = []
        for pos_key in position_order:
            if pos_key not in positions_data:
                continue
            pos = positions_data[pos_key]
            players_js = []
            for player in pos.get("players", [])[:4]:  # Top 4 players per position
                overseas_str = "true" if player.get("is_overseas") else "false"
                rationale = player.get("rationale", "").replace('"', "'")
                bowl_type = player.get("bowling_type", "").replace('"', "'")
                bowl_arm = player.get("bowling_arm", "").replace('"', "'")
                players_js.append(
                    f'{{ rank: {player.get("rank", 0)}, name: "{player.get("name", "")}", '
                    f"score: {player.get('score', 0)}, overseas: {overseas_str}, "
                    f"price: {player.get('price_cr', 0)}, "
                    f'bowlingType: "{bowl_type}", bowlingArm: "{bowl_arm}", '
                    f'rationale: "{rationale}" }}'
                )

            what_works = pos.get("what_works", "").replace('"', "'")
            what_doesnt = pos.get("what_doesnt", "").replace('"', "'")
            positions_js.append(
                f'{{ key: "{pos_key}", name: "{pos.get("name", "")}", rating: {pos.get("rating", 0)}, '
                f"overseas: {pos.get('overseas_count', 0)}, "
                f'whatWorks: "{what_works}", '
                f'whatDoesnt: "{what_doesnt}", '
                f"players: [{', '.join(players_js)}] }}"
            )

        vulnerabilities = team.get("vulnerabilities", [])
        vulnerabilities_str = ", ".join(
            [f'"{v.replace(chr(34), chr(39))}"' for v in vulnerabilities[:3]]
        )

        js_content += f"""    {abbrev}: {{
        overall: {team.get("overall_rating", 0)},
        strongest: "{team.get("strongest_position", "")}",
        weakest: "{team.get("weakest_position", "")}",
        vulnerabilities: [{vulnerabilities_str}],
        positions: [
            {",".join(positions_js)}
        ]
    }},
"""

    js_content += "};\n"
    return js_content


def generate_full_squads_js():
    """Generate full_squads.js from squad CSV + contracts + experience data."""
    data_dir = ROOT_DIR / "data"
    squad_file = data_dir / "ipl_2026_squads.csv"
    contracts_file = data_dir / "ipl_2026_player_contracts.csv"
    experience_file = ROOT_DIR / "outputs" / "team" / "ipl_2026_squad_experience.csv"

    # Load contracts
    contracts = {}
    if contracts_file.exists():
        with open(contracts_file) as f:
            for row in csv.DictReader(f):
                key = f"{row['team_name']}|{row['player_name']}"
                contracts[key] = {
                    "price_cr": float(row["price_cr"]),
                    "acquisition_type": row["acquisition_type"],
                }

    # Load experience
    experience = {}
    if experience_file.exists():
        with open(experience_file) as f:
            for row in csv.DictReader(f):
                key = f"{row['team_name']}|{row['player_name']}"
                bat_inn = float(row.get("ipl_batting_innings") or 0)
                bowl_m = float(row.get("ipl_bowling_matches") or 0)
                experience[key] = {
                    "ipl_matches": int(max(bat_inn, bowl_m)),
                    "ipl_runs": int(float(row.get("ipl_batting_runs") or 0)),
                    "ipl_sr": round(float(row.get("ipl_batting_sr") or 0), 1),
                    "ipl_wickets": int(float(row.get("ipl_bowling_wickets") or 0)),
                    "ipl_economy": round(float(row.get("ipl_bowling_economy") or 0), 2),
                }

    # Load founder data for predicted XII
    founder_xii = {}
    founder_file = ROOT_DIR / "outputs" / "founder_review" / "founder_squads_2026.json"
    if founder_file.exists():
        with open(founder_file) as f:
            fd = json.load(f)
            for team_data in fd.get("teams", {}).values():
                for p in team_data.get("players", []):
                    if p.get("player_id") and p.get("is_predicted_xii"):
                        founder_xii[p["player_id"]] = p["squad_number"]

    # Load squads
    squads = {}
    with open(squad_file) as f:
        for row in csv.DictReader(f):
            team = row["team_name"]
            if team not in squads:
                squads[team] = []
            key = f"{team}|{row['player_name']}"
            contract = contracts.get(key, {})
            exp = experience.get(key, {})
            founder_pos = founder_xii.get(row["player_id"])
            # Parse pipe-delimited tags into lists
            batter_tags_raw = row.get("batter_tags", "")
            bowler_tags_raw = row.get("bowler_tags", "")
            batter_tags = (
                [t.strip() for t in batter_tags_raw.split("|") if t.strip()]
                if batter_tags_raw
                else []
            )
            bowler_tags = (
                [t.strip() for t in bowler_tags_raw.split("|") if t.strip()]
                if bowler_tags_raw
                else []
            )

            squads[team].append(
                {
                    "name": row["player_name"],
                    "player_id": row["player_id"],
                    "role": row["role"],
                    "batting_hand": row.get("batting_hand", ""),
                    "bowling_arm": row.get("bowling_arm", ""),
                    "bowling_type": row.get("bowling_type", ""),
                    "nationality": row.get("nationality", "IND"),
                    "age": row.get("age", ""),
                    "batter_classification": row.get("batter_classification", ""),
                    "bowler_classification": row.get("bowler_classification", ""),
                    "batter_tags": batter_tags,
                    "bowler_tags": bowler_tags,
                    "is_captain": row.get("is_captain", "").strip().upper() == "TRUE",
                    "price_cr": contract.get("price_cr", 0),
                    "acquisition_type": contract.get("acquisition_type", ""),
                    "ipl_matches": exp.get("ipl_matches", 0),
                    "ipl_runs": exp.get("ipl_runs", 0),
                    "ipl_sr": exp.get("ipl_sr", 0),
                    "ipl_wickets": exp.get("ipl_wickets", 0),
                    "ipl_economy": exp.get("ipl_economy", 0),
                    "is_predicted_xii": founder_pos is not None,
                    "founder_position": founder_pos,
                }
            )

    timestamp = datetime.now().isoformat()
    js = f"""/**
 * The Lab - Full Squad Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 */

const FULL_SQUADS = {{
"""
    for abbrev in TEAM_ORDER:
        full_name = TEAMS_META[abbrev]["fullName"]
        team_players = squads.get(full_name, [])
        players_js = []
        for p in team_players:
            overseas = p["nationality"] not in ("IND", "India", "")
            is_uncapped = p["ipl_matches"] == 0
            name_esc = p["name"].replace("'", "\\'")
            role_esc = p["role"].replace("'", "\\'")
            bat_class_esc = p["batter_classification"].replace("'", "\\'")
            bwl_class_esc = p["bowler_classification"].replace("'", "\\'")
            bat_tags_js = json.dumps(p["batter_tags"])
            bwl_tags_js = json.dumps(p["bowler_tags"])
            acq_esc = p["acquisition_type"].replace("'", "\\'")
            fpos = p["founder_position"] if p["founder_position"] else "null"
            bowl_type_display = (
                p["bowling_type"].replace("LA Orthodox", "Orthodox") if p["bowling_type"] else ""
            )
            players_js.append(
                f"        {{ name: '{name_esc}', role: '{role_esc}', "
                f"battingHand: '{p['batting_hand']}', "
                f"bowlingArm: '{p['bowling_arm']}', "
                f"bowlingType: '{bowl_type_display}', "
                f"nationality: '{p['nationality']}', "
                f"age: {p['age'] if p['age'] else 0}, "
                f"price: {p['price_cr']}, "
                f"overseas: {'true' if overseas else 'false'}, "
                f"isCaptain: {'true' if p['is_captain'] else 'false'}, "
                f"batterClass: '{bat_class_esc}', "
                f"bowlerClass: '{bwl_class_esc}', "
                f"batterTags: {bat_tags_js}, "
                f"bowlerTags: {bwl_tags_js}, "
                f"isUncapped: {'true' if is_uncapped else 'false'}, "
                f"acquisition: '{acq_esc}', "
                f"predictedXII: {'true' if p['is_predicted_xii'] else 'false'}, "
                f"founderPos: {fpos}, "
                f"iplMatches: {p['ipl_matches']}, iplRuns: {p['ipl_runs']}, "
                f"iplSR: {p['ipl_sr']}, iplWickets: {p['ipl_wickets']}, "
                f"iplEconomy: {p['ipl_economy']} }}"
            )
        joined = ",\n".join(players_js)
        js += f"    {abbrev}: [\n{joined}\n    ],\n"

    js += "};\n"
    return js


def _round_floats(obj, precision=2):
    """Recursively round all floats in a nested dict/list structure."""
    if isinstance(obj, float):
        return round(obj, precision)
    if isinstance(obj, dict):
        return {k: _round_floats(v, precision) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(item, precision) for item in obj]
    return obj


def generate_player_profiles_js():
    """Generate player_profiles.js from per-team profile JSONs."""
    profiles_dir = OUTPUTS_DIR / "player_profiles" / "by_team"
    all_teams = {}

    for abbrev in TEAM_ORDER:
        team_file = profiles_dir / f"{abbrev}_profiles.json"
        if not team_file.exists():
            continue
        with open(team_file) as f:
            data = json.load(f)
        players = data.get("players", {})
        # Round all floats to 2 decimal places to save space
        all_teams[abbrev] = _round_floats(players)

    # Compact JSON (no indentation) to keep file small
    json_str = json.dumps(all_teams, separators=(",", ":"))
    timestamp = datetime.now().isoformat()
    js_content = f"""/**
 * The Lab - Player Profiles Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 */

const PLAYER_PROFILES = {json_str};
"""
    return js_content


def main():
    print("🏏 The Lab - Data Update Script")
    print("=" * 50)

    # Ensure output directory exists
    DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load source data
    print("\n📂 Loading source data...")
    predicted_xii = load_predicted_xii()
    depth_charts = load_depth_charts()
    consolidated_depth = load_consolidated_depth_charts()
    player_tags = load_player_tags()

    print(f"  ✓ Predicted XII: {'Loaded' if predicted_xii else 'Not found'}")
    print(f"  ✓ Depth Charts: {len(depth_charts)} teams loaded")
    print(f"  ✓ Consolidated Depth Charts: {'Loaded' if consolidated_depth else 'Not found'}")
    print(f"  ✓ Player Tags: {'Loaded' if player_tags else 'Not found'}")

    # Generate JS files
    print("\n📝 Generating JavaScript data files...")

    # teams.js
    teams_js = generate_teams_js()
    teams_path = DASHBOARD_DATA_DIR / "teams.js"
    with open(teams_path, "w") as f:
        f.write(teams_js)
    print(f"  ✓ {teams_path.name}")

    # predicted_xii.js (includes ratings summary)
    predicted_js = generate_predicted_xii_js(predicted_xii)
    depth_ratings_js = generate_depth_charts_js(depth_charts)

    # Combine into one file
    combined_path = DASHBOARD_DATA_DIR / "predicted_xii.js"
    with open(combined_path, "w") as f:
        f.write(predicted_js)
        f.write("\n")
        f.write(depth_ratings_js)
    print(f"  ✓ {combined_path.name}")

    # depth_charts.js (full inline depth charts)
    if consolidated_depth:
        full_depth_js = generate_full_depth_charts_js(consolidated_depth)
        depth_path = DASHBOARD_DATA_DIR / "depth_charts.js"
        with open(depth_path, "w") as f:
            f.write(full_depth_js)
        print(f"  ✓ {depth_path.name}")

    # full_squads.js
    full_squads_js = generate_full_squads_js()
    squads_path = DASHBOARD_DATA_DIR / "full_squads.js"
    with open(squads_path, "w") as f:
        f.write(full_squads_js)
    print(f"  ✓ {squads_path.name}")

    # player_profiles.js
    profiles_js = generate_player_profiles_js()
    profiles_path = DASHBOARD_DATA_DIR / "player_profiles.js"
    with open(profiles_path, "w") as f:
        f.write(profiles_js)
    print(f"  ✓ {profiles_path.name}")

    print("\n✅ Data update complete!")
    print(f"   Files written to: {DASHBOARD_DATA_DIR}")


if __name__ == "__main__":
    main()
