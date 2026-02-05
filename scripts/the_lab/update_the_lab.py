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

import json
from pathlib import Path
from datetime import datetime

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
        "titles": 5,
        "icon": "🔵",
    },
    "CSK": {
        "name": "Chennai Super Kings",
        "fullName": "Chennai Super Kings",
        "homeVenue": "MA Chidambaram Stadium",
        "venueBias": "spin",
        "primaryColor": "#ffc20e",
        "titles": 5,
        "icon": "🦁",
    },
    "RCB": {
        "name": "Royal Challengers",
        "fullName": "Royal Challengers Bengaluru",
        "homeVenue": "M Chinnaswamy Stadium",
        "venueBias": "pace",
        "primaryColor": "#d4213d",
        "titles": 0,
        "icon": "🔴",
    },
    "KKR": {
        "name": "Knight Riders",
        "fullName": "Kolkata Knight Riders",
        "homeVenue": "Eden Gardens",
        "venueBias": "spin",
        "primaryColor": "#3a225d",
        "titles": 3,
        "icon": "💜",
    },
    "DC": {
        "name": "Delhi Capitals",
        "fullName": "Delhi Capitals",
        "homeVenue": "Arun Jaitley Stadium",
        "venueBias": "neutral",
        "primaryColor": "#0078bc",
        "titles": 0,
        "icon": "🔷",
    },
    "PBKS": {
        "name": "Punjab Kings",
        "fullName": "Punjab Kings",
        "homeVenue": "PCA Stadium, Mohali",
        "venueBias": "neutral",
        "primaryColor": "#ed1b24",
        "titles": 0,
        "icon": "🦁",
    },
    "RR": {
        "name": "Rajasthan Royals",
        "fullName": "Rajasthan Royals",
        "homeVenue": "Sawai Mansingh Stadium",
        "venueBias": "neutral",
        "primaryColor": "#ea1a85",
        "titles": 1,
        "icon": "👑",
    },
    "SRH": {
        "name": "Sunrisers",
        "fullName": "Sunrisers Hyderabad",
        "homeVenue": "Rajiv Gandhi Intl Stadium",
        "venueBias": "pace",
        "primaryColor": "#f7a721",
        "titles": 1,
        "icon": "🌅",
    },
    "GT": {
        "name": "Gujarat Titans",
        "fullName": "Gujarat Titans",
        "homeVenue": "Narendra Modi Stadium",
        "venueBias": "neutral",
        "primaryColor": "#1c1c1c",
        "titles": 1,
        "icon": "🦁",
    },
    "LSG": {
        "name": "Lucknow Giants",
        "fullName": "Lucknow Super Giants",
        "homeVenue": "Ekana Cricket Stadium",
        "venueBias": "neutral",
        "primaryColor": "#a72056",
        "titles": 0,
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
    js_content = """/**
 * The Lab - Team Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 */

const TEAMS = {{
"""
    for abbrev, meta in TEAMS_META.items():
        js_content += f"""    {abbrev}: {{
        abbrev: "{abbrev}",
        name: "{meta['name']}",
        fullName: "{meta['fullName']}",
        homeVenue: "{meta['homeVenue']}",
        venueBias: "{meta['venueBias']}",
        primaryColor: "{meta['primaryColor']}",
        titles: {meta['titles']},
        icon: "{meta['icon']}"
    }},
"""

    js_content += """};

const TEAM_ORDER = ["MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"];

const QUICK_STATS = {
    totalTeams: 10,
    totalPlayers: 231,
    matchesAnalyzed: 219,
    totalReports: 86,
    dataRange: "2023-2025"
};
"""

    return js_content.format(timestamp=datetime.now().isoformat())


def generate_predicted_xii_js(data):
    """Generate predicted_xii.js from source data."""
    if not data:
        return "// No predicted XII data found\nconst PREDICTED_XII = {};\nconst DEPTH_CHART_RATINGS = {};"

    js_content = """/**
 * The Lab - Predicted XII Data
 * IPL 2026 Pre-Season Analytics
 * Auto-generated: {timestamp}
 * Algorithm: {algorithm}
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

        js_content += f"""    {abbrev}: {{
        teamName: "{team.get("team_name", "")}",
        teamAbbrev: "{abbrev}",
        homeVenue: "{team.get("home_venue", "")}",
        venueBias: "{team.get("venue_bias", "")}",
        captain: "{team.get("captain", "")}",
        wicketkeeper: "{team.get("wicketkeeper", "")}",
        xi: [
{",\\n".join(xi_players)}
        ],
        impactPlayer: {{ name: "{impact.get("player_name", "")}", role: "{impact.get("role", "")}", price: {impact.get("price_cr", 0)} }},
        balance: {{ overseas: {balance.get("overseas_count", 0)}, bowlingOptions: {balance.get("bowling_options", 0)}, spinners: {balance.get("spinners", 0)}, pacers: {balance.get("pacers", 0)}, leftHandersTop6: {balance.get("left_handers_top6", 0)} }},
        constraintsSatisfied: {"true" if team.get("constraints_satisfied") else "false"}
    }},
"""

    js_content += "};\n"

    return js_content.format(
        timestamp=datetime.now().isoformat(),
        generated_at=data.get("generated_at", ""),
        version=data.get("version", ""),
        algorithm=data.get("algorithm_name", ""),
        algorithm_name=data.get("algorithm_name", "SUPER SELECTOR"),
    )


def generate_depth_charts_js(depth_charts):
    """Generate depth_charts.js with ratings summary."""
    js_content = """/**
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
    return js_content.format(timestamp=datetime.now().isoformat())


def main():
    print("🏏 The Lab - Data Update Script")
    print("=" * 50)

    # Ensure output directory exists
    DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load source data
    print("\n📂 Loading source data...")
    predicted_xii = load_predicted_xii()
    depth_charts = load_depth_charts()
    player_tags = load_player_tags()

    print(f"  ✓ Predicted XII: {'Loaded' if predicted_xii else 'Not found'}")
    print(f"  ✓ Depth Charts: {len(depth_charts)} teams loaded")
    print(f"  ✓ Player Tags: {'Loaded' if player_tags else 'Not found'}")

    # Generate JS files
    print("\n📝 Generating JavaScript data files...")

    # teams.js
    teams_js = generate_teams_js()
    teams_path = DASHBOARD_DATA_DIR / "teams.js"
    with open(teams_path, "w") as f:
        f.write(teams_js)
    print(f"  ✓ {teams_path.name}")

    # predicted_xii.js
    predicted_js = generate_predicted_xii_js(predicted_xii)
    depth_ratings_js = generate_depth_charts_js(depth_charts)

    # Combine into one file
    combined_path = DASHBOARD_DATA_DIR / "predicted_xii.js"
    with open(combined_path, "w") as f:
        f.write(predicted_js)
        f.write("\n")
        f.write(depth_ratings_js)
    print(f"  ✓ {combined_path.name}")

    print("\n✅ Data update complete!")
    print(f"   Files written to: {DASHBOARD_DATA_DIR}")


if __name__ == "__main__":
    main()
