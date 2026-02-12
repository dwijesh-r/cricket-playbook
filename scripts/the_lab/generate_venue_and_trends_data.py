#!/usr/bin/env python3
"""
Generate venue_data.js and historic_trends.js for The Lab dashboard.

Queries DuckDB views for venue profiles, team venue records, match context,
and team phase batting/bowling data. Exports two self-contained JavaScript
data files for the dashboard.

Usage:
    python scripts/the_lab/generate_venue_and_trends_data.py
"""

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import duckdb

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "cricket_playbook.duckdb"
VENUE_CSV = ROOT_DIR / "outputs" / "team_venue_records.csv"
VENUE_OUTPUT = ROOT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "venue_data.js"
TRENDS_OUTPUT = ROOT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "historic_trends.js"

# Team name to abbreviation mapping
TEAM_ABBREV = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bengaluru": "RCB",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
}

TEAM_ORDER = ["MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"]

# Team home venue mapping — matched to actual DB venue names
TEAM_HOME_VENUES = {
    "MI": "Wankhede Stadium, Mumbai",
    "CSK": "MA Chidambaram Stadium, Chepauk, Chennai",
    "RCB": "M Chinnaswamy Stadium, Bengaluru",
    "KKR": "Eden Gardens, Kolkata",
    "SRH": "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
    "RR": "Sawai Mansingh Stadium, Jaipur",
    "DC": "Arun Jaitley Stadium, Delhi",
    "LSG": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow",
    "PBKS": "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
    "GT": "Narendra Modi Stadium, Ahmedabad",
}

# IPL season final standings (2023-2025, manually curated)
SEASON_POSITIONS = {
    2023: {
        "GT": "1st",
        "CSK": "2nd",
        "MI": "5th",
        "LSG": "3rd",
        "RCB": "7th",
        "KKR": "7th",
        "RR": "5th",
        "PBKS": "8th",
        "DC": "9th",
        "SRH": "10th",
    },
    2024: {
        "KKR": "1st",
        "SRH": "2nd",
        "RR": "3rd",
        "RCB": "4th",
        "CSK": "5th",
        "DC": "6th",
        "LSG": "7th",
        "GT": "8th",
        "PBKS": "9th",
        "MI": "10th",
    },
    2025: {
        "RCB": "1st",
        "PBKS": "2nd",
        "GT": "3rd",
        "MI": "4th",
        "DC": "5th",
        "KKR": "6th",
        "SRH": "7th",
        "LSG": "8th",
        "RR": "9th",
        "CSK": "10th",
    },
}

PHASE_ORDER = ["powerplay", "middle", "death"]


def safe_round(val, decimals=2):
    """Round a value safely, returning None for NaN/None."""
    if val is None:
        return None
    try:
        fval = float(val)
        if math.isnan(fval) or math.isinf(fval):
            return None
        return round(fval, decimals)
    except (TypeError, ValueError):
        return None


def js_value(v):
    """Convert a Python value to a JS literal string."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, (int, float)):
        if math.isnan(v) or math.isinf(v):
            return "null"
        return str(v)
    return str(v)


# ---------------------------------------------------------------------------
# VENUE DATA GENERATION
# ---------------------------------------------------------------------------


def get_venue_profiles(conn):
    """
    Get phase-level venue profiles for each team's home venue.
    Aggregates across venue_ids if there are duplicates for the same venue_name.
    innings=1 → battingFirst, innings=2 → chasing
    """
    profiles = {}

    for abbrev in TEAM_ORDER:
        venue_name = TEAM_HOME_VENUES[abbrev]
        rows = conn.execute(
            """
            SELECT
                innings,
                match_phase,
                ROUND(SUM(total_runs) * 6.0 / NULLIF(SUM(total_balls), 0), 2) AS run_rate,
                ROUND(SUM(boundary_pct * total_balls) / NULLIF(SUM(total_balls), 0), 2) AS boundary_pct,
                ROUND(SUM(dot_ball_pct * total_balls) / NULLIF(SUM(total_balls), 0), 2) AS dot_pct,
                ROUND(SUM(wickets_per_match * matches) / NULLIF(SUM(matches), 0), 2) AS wickets_per_match,
                SUM(matches) AS total_matches
            FROM analytics_ipl_venue_profile_since2023
            WHERE venue_name = ?
            GROUP BY innings, match_phase
            ORDER BY innings, match_phase
        """,
            [venue_name],
        ).fetchall()

        phases = {}
        for innings, phase, rr, bdry, dot, wpm, matches in rows:
            context = "battingFirst" if innings == 1 else "chasing"
            if phase not in phases:
                phases[phase] = {}
            phases[phase][context] = {
                "runRate": safe_round(rr),
                "boundaryPct": safe_round(bdry),
                "dotPct": safe_round(dot),
                "wicketsPerMatch": safe_round(wpm),
            }

        profiles[abbrev] = {
            "venueName": venue_name,
            "phases": phases,
        }

    return profiles


def classify_venue_character(profiles, conn):
    """
    Classify each venue as 'pace', 'spin', or 'balanced' based on
    run_rate and boundary% patterns. Also compute avgFirstInningsScore
    and chaseFriendly.
    """
    for abbrev in TEAM_ORDER:
        venue_name = TEAM_HOME_VENUES[abbrev]
        p = profiles[abbrev]
        phases = p.get("phases", {})

        # Compute average first innings score from run_rate across phases
        # First innings: 6 overs PP + 8 overs middle + 6 overs death = 120 balls
        pp_bf = phases.get("powerplay", {}).get("battingFirst", {})
        mid_bf = phases.get("middle", {}).get("battingFirst", {})
        death_bf = phases.get("death", {}).get("battingFirst", {})

        pp_rr = pp_bf.get("runRate") or 0
        mid_rr = mid_bf.get("runRate") or 0
        death_rr = death_bf.get("runRate") or 0

        # PP = 6 overs, middle = 8 overs, death = 6 overs
        avg_first = safe_round(pp_rr * 6 + mid_rr * 8 + death_rr * 6)

        # Overall boundary% and run_rate across all phases (batting first)
        total_bdry = 0
        total_phases = 0
        total_rr = 0
        for phase_name in PHASE_ORDER:
            bf = phases.get(phase_name, {}).get("battingFirst", {})
            if bf.get("boundaryPct") is not None:
                total_bdry += bf["boundaryPct"]
                total_phases += 1
            if bf.get("runRate") is not None:
                total_rr += bf["runRate"]

        avg_bdry = total_bdry / total_phases if total_phases > 0 else 0
        avg_rr_overall = total_rr / total_phases if total_phases > 0 else 0

        # High boundary% and high run rate → pace-friendly
        # Low boundary%, lower run rate → spin-friendly
        # Middle ground → balanced
        if avg_bdry >= 21 and avg_rr_overall >= 9.5:
            char_type = "pace"
        elif avg_bdry < 18 or avg_rr_overall < 8.5:
            char_type = "spin"
        else:
            char_type = "balanced"

        # Chase friendliness from match results at this venue
        chase_rows = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN chase_result = 'Won' THEN 1 ELSE 0 END) AS chases_won
            FROM analytics_ipl_match_context_since2023
            WHERE venue_name = ?
              AND chase_result IN ('Won', 'Lost')
        """,
            [venue_name],
        ).fetchone()

        total_matches = chase_rows[0] if chase_rows else 0
        chases_won = chase_rows[1] if chase_rows else 0
        chase_pct = (chases_won / total_matches * 100) if total_matches > 0 else 50
        chase_friendly = chase_pct >= 50

        p["character"] = char_type
        p["avgFirstInningsScore"] = avg_first
        p["chaseFriendly"] = chase_friendly
        p["chaseWinPct"] = safe_round(chase_pct, 1)

    return profiles


def get_team_venue_records_from_csv():
    """Read team venue records from CSV, return top 5 venues per team by matches."""
    records = {}

    if not VENUE_CSV.exists():
        print(f"  WARNING: {VENUE_CSV} not found, will derive from DB")
        return None

    with open(VENUE_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_name = row["team_name"]
            abbrev = TEAM_ABBREV.get(team_name)
            if not abbrev:
                continue

            if abbrev not in records:
                records[abbrev] = []

            # Extract short venue name (before the comma) and city
            full_venue = row["venue_name"]
            city = row["city"]
            # Use full venue name as-is for consistency
            venue_short = full_venue.split(",")[0].strip()

            records[abbrev].append(
                {
                    "venue": venue_short,
                    "fullVenue": full_venue,
                    "city": city,
                    "matches": int(float(row["matches"])),
                    "wins": int(float(row["wins"])),
                    "losses": int(float(row["losses"])),
                    "winPct": safe_round(float(row["win_pct"]), 1),
                    "record": row["record"],
                }
            )

    # Merge RCB variants (Bangalore + Bengaluru)
    if "RCB" in records:
        # Deduplicate by venue — merge records for same venue
        merged = {}
        for rec in records["RCB"]:
            key = rec["fullVenue"]
            if key in merged:
                merged[key]["matches"] += rec["matches"]
                merged[key]["wins"] += rec["wins"]
                merged[key]["losses"] += rec["losses"]
                total = merged[key]["wins"] + merged[key]["losses"]
                merged[key]["winPct"] = (
                    safe_round(merged[key]["wins"] / total * 100, 1) if total > 0 else 0
                )
                merged[key]["record"] = f"{merged[key]['wins']}-{merged[key]['losses']}"
            else:
                merged[key] = rec.copy()
        records["RCB"] = list(merged.values())

    # Sort each team's records by matches desc, take top 5
    for abbrev in records:
        records[abbrev].sort(key=lambda x: x["matches"], reverse=True)
        records[abbrev] = records[abbrev][:5]

    return records


def get_team_venue_records_from_db(conn):
    """Derive team venue records from match context if CSV unavailable."""
    rows = conn.execute("""
        WITH team_matches AS (
            SELECT venue_name, city, team1_name AS team, winner_name
            FROM analytics_ipl_match_context_since2023
            UNION ALL
            SELECT venue_name, city, team2_name AS team, winner_name
            FROM analytics_ipl_match_context_since2023
        )
        SELECT team, venue_name, city,
            COUNT(*) AS matches,
            SUM(CASE WHEN winner_name = team THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN winner_name != team AND winner_name IS NOT NULL THEN 1 ELSE 0 END) AS losses
        FROM team_matches
        GROUP BY team, venue_name, city
        ORDER BY team, matches DESC
    """).fetchall()

    records = {}
    for team, venue, city, matches, wins, losses in rows:
        abbrev = TEAM_ABBREV.get(team)
        if not abbrev:
            continue
        if abbrev not in records:
            records[abbrev] = []

        venue_short = venue.split(",")[0].strip()
        total = wins + losses
        win_pct = safe_round(wins / total * 100, 1) if total > 0 else None

        records[abbrev].append(
            {
                "venue": venue_short,
                "fullVenue": venue,
                "city": city,
                "matches": int(matches),
                "wins": int(wins),
                "losses": int(losses),
                "winPct": win_pct,
                "record": f"{int(wins)}-{int(losses)}",
            }
        )

    # Merge RCB variants
    if "RCB" in records:
        merged = {}
        for rec in records["RCB"]:
            key = rec["fullVenue"]
            if key in merged:
                merged[key]["matches"] += rec["matches"]
                merged[key]["wins"] += rec["wins"]
                merged[key]["losses"] += rec["losses"]
                total = merged[key]["wins"] + merged[key]["losses"]
                merged[key]["winPct"] = (
                    safe_round(merged[key]["wins"] / total * 100, 1) if total > 0 else 0
                )
                merged[key]["record"] = f"{merged[key]['wins']}-{merged[key]['losses']}"
            else:
                merged[key] = rec.copy()
        records["RCB"] = list(merged.values())

    for abbrev in records:
        records[abbrev].sort(key=lambda x: x["matches"], reverse=True)
        records[abbrev] = records[abbrev][:5]

    return records


def generate_venue_js(profiles, venue_records):
    """Generate venue_data.js content."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "/**",
        " * The Lab - Venue Analysis Data",
        " * IPL 2026 Pre-Season Analytics",
        f" * Auto-generated: {timestamp}",
        " * Source: analytics_ipl_venue_profile_since2023,",
        " *         analytics_ipl_match_context_since2023,",
        " *         outputs/team_venue_records.csv",
        " */",
        "",
        "var VENUE_DATA = {",
        "    venueProfiles: {",
    ]

    for abbrev in TEAM_ORDER:
        p = profiles[abbrev]
        lines.append(f'        "{abbrev}": {{')
        lines.append(f"            venueName: {js_value(p['venueName'])},")
        lines.append(f"            character: {js_value(p['character'])},")
        lines.append(f"            avgFirstInningsScore: {js_value(p['avgFirstInningsScore'])},")
        lines.append(f"            chaseFriendly: {js_value(p['chaseFriendly'])},")
        lines.append(f"            chaseWinPct: {js_value(p['chaseWinPct'])},")
        lines.append("            phases: {")

        for phase in PHASE_ORDER:
            phase_data = p["phases"].get(phase, {})
            lines.append(f"                {phase}: {{")
            for context in ["battingFirst", "chasing"]:
                ctx_data = phase_data.get(context, {})
                rr = js_value(ctx_data.get("runRate"))
                bdry = js_value(ctx_data.get("boundaryPct"))
                dot = js_value(ctx_data.get("dotPct"))
                wpm = js_value(ctx_data.get("wicketsPerMatch"))
                comma = "," if context == "battingFirst" else ""
                lines.append(
                    f"                    {context}: {{ runRate: {rr}, boundaryPct: {bdry}, "
                    f"dotPct: {dot}, wicketsPerMatch: {wpm} }}{comma}"
                )
            comma = "," if phase != "death" else ""
            lines.append(f"                }}{comma}")

        lines.append("            }")
        comma = "," if abbrev != TEAM_ORDER[-1] else ""
        lines.append(f"        }}{comma}")

    lines.append("    },")
    lines.append("    teamVenueRecords: {")

    for abbrev in TEAM_ORDER:
        team_recs = venue_records.get(abbrev, [])
        lines.append(f'        "{abbrev}": [')
        for i, rec in enumerate(team_recs):
            comma = "," if i < len(team_recs) - 1 else ""
            lines.append(
                f"            {{ venue: {js_value(rec['venue'])}, "
                f"city: {js_value(rec['city'])}, "
                f"matches: {rec['matches']}, "
                f"wins: {rec['wins']}, "
                f"losses: {rec['losses']}, "
                f"winPct: {js_value(rec['winPct'])}, "
                f"record: {js_value(rec['record'])} }}{comma}"
            )
        comma = "," if abbrev != TEAM_ORDER[-1] else ""
        lines.append(f"        ]{comma}")

    lines.append("    }")
    lines.append("};")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HISTORIC TRENDS GENERATION
# ---------------------------------------------------------------------------


def get_season_records(conn):
    """Derive season-by-season W-L records for all teams."""
    rows = conn.execute("""
        WITH team_matches AS (
            SELECT season, team1_name AS team, winner_name
            FROM analytics_ipl_match_context_since2023
            UNION ALL
            SELECT season, team2_name AS team, winner_name
            FROM analytics_ipl_match_context_since2023
        )
        SELECT team, season,
            COUNT(*) AS matches,
            SUM(CASE WHEN winner_name = team THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN winner_name != team AND winner_name IS NOT NULL THEN 1 ELSE 0 END) AS losses
        FROM team_matches
        GROUP BY team, season
        ORDER BY team, season
    """).fetchall()

    records = {}
    for team, season, matches, wins, losses in rows:
        abbrev = TEAM_ABBREV.get(team)
        if not abbrev:
            continue

        season_int = int(season)
        total = wins + losses
        win_pct = safe_round(wins / total * 100, 1) if total > 0 else None
        position = SEASON_POSITIONS.get(season_int, {}).get(abbrev, "N/A")

        entry = {
            "season": season_int,
            "matches": int(matches),
            "wins": int(wins),
            "losses": int(losses),
            "winPct": win_pct,
            "position": position,
        }

        if abbrev not in records:
            records[abbrev] = []
        records[abbrev].append(entry)

    # Merge RCB across name changes (Bangalore 2023 → Bengaluru 2024+)
    if "RCB" in records:
        # Season records should already be separate seasons, no overlap
        # Sort by season
        records["RCB"].sort(key=lambda x: x["season"])

    return records


def get_phase_trends(conn):
    """Get season-over-season batting and bowling phase performance per team."""
    # Batting
    bat_rows = conn.execute("""
        SELECT batting_team, season, match_phase,
            strike_rate, run_rate, boundary_pct, dot_ball_pct
        FROM analytics_ipl_team_phase_batting_since2023
        ORDER BY batting_team, season, match_phase
    """).fetchall()

    batting = {}
    for team, season, phase, sr, rr, bdry, dot in bat_rows:
        abbrev = TEAM_ABBREV.get(team)
        if not abbrev:
            continue
        season_int = int(season)
        if abbrev not in batting:
            batting[abbrev] = {}
        if season_int not in batting[abbrev]:
            batting[abbrev][season_int] = {"season": season_int}

        if phase == "powerplay":
            batting[abbrev][season_int]["powerplaySR"] = safe_round(sr, 1)
            batting[abbrev][season_int]["powerplayRR"] = safe_round(rr)
        elif phase == "middle":
            batting[abbrev][season_int]["middleSR"] = safe_round(sr, 1)
            batting[abbrev][season_int]["middleRR"] = safe_round(rr)
        elif phase == "death":
            batting[abbrev][season_int]["deathSR"] = safe_round(sr, 1)
            batting[abbrev][season_int]["deathRR"] = safe_round(rr)

    # Bowling
    bowl_rows = conn.execute("""
        SELECT bowling_team, season, match_phase,
            economy, wickets_taken, dot_ball_pct
        FROM analytics_ipl_team_phase_bowling_since2023
        ORDER BY bowling_team, season, match_phase
    """).fetchall()

    bowling = {}
    for team, season, phase, econ, wkts, dot in bowl_rows:
        abbrev = TEAM_ABBREV.get(team)
        if not abbrev:
            continue
        season_int = int(season)
        if abbrev not in bowling:
            bowling[abbrev] = {}
        if season_int not in bowling[abbrev]:
            bowling[abbrev][season_int] = {"season": season_int}

        if phase == "powerplay":
            bowling[abbrev][season_int]["powerplayEcon"] = safe_round(econ)
            bowling[abbrev][season_int]["powerplayWickets"] = int(wkts) if wkts else 0
        elif phase == "middle":
            bowling[abbrev][season_int]["middleEcon"] = safe_round(econ)
            bowling[abbrev][season_int]["middleWickets"] = int(wkts) if wkts else 0
        elif phase == "death":
            bowling[abbrev][season_int]["deathEcon"] = safe_round(econ)
            bowling[abbrev][season_int]["deathWickets"] = int(wkts) if wkts else 0

    # Convert dicts to sorted lists
    batting_out = {}
    for abbrev in batting:
        batting_out[abbrev] = [batting[abbrev][s] for s in sorted(batting[abbrev].keys())]

    bowling_out = {}
    for abbrev in bowling:
        bowling_out[abbrev] = [bowling[abbrev][s] for s in sorted(bowling[abbrev].keys())]

    return batting_out, bowling_out


def generate_trends_js(season_records, batting_trends, bowling_trends):
    """Generate historic_trends.js content."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "/**",
        " * The Lab - Historic Season Trends",
        " * IPL 2026 Pre-Season Analytics",
        f" * Auto-generated: {timestamp}",
        " * Source: analytics_ipl_match_context_since2023,",
        " *         analytics_ipl_team_phase_batting_since2023,",
        " *         analytics_ipl_team_phase_bowling_since2023",
        " */",
        "",
        "var HISTORIC_TRENDS = {",
        "    seasonRecords: {",
    ]

    for abbrev in TEAM_ORDER:
        recs = season_records.get(abbrev, [])
        lines.append(f'        "{abbrev}": [')
        for i, rec in enumerate(recs):
            comma = "," if i < len(recs) - 1 else ""
            lines.append(
                f"            {{ season: {rec['season']}, "
                f"matches: {rec['matches']}, "
                f"wins: {rec['wins']}, "
                f"losses: {rec['losses']}, "
                f"winPct: {js_value(rec['winPct'])}, "
                f"position: {js_value(rec['position'])} }}{comma}"
            )
        comma = "," if abbrev != TEAM_ORDER[-1] else ""
        lines.append(f"        ]{comma}")

    lines.append("    },")
    lines.append("    phaseTrends: {")

    for abbrev in TEAM_ORDER:
        bat = batting_trends.get(abbrev, [])
        bowl = bowling_trends.get(abbrev, [])

        lines.append(f'        "{abbrev}": {{')
        lines.append("            batting: [")
        for i, entry in enumerate(bat):
            comma = "," if i < len(bat) - 1 else ""
            parts = [f"season: {entry['season']}"]
            for key in ["powerplaySR", "middleSR", "deathSR", "powerplayRR", "middleRR", "deathRR"]:
                parts.append(f"{key}: {js_value(entry.get(key))}")
            lines.append(f"                {{ {', '.join(parts)} }}{comma}")
        lines.append("            ],")

        lines.append("            bowling: [")
        for i, entry in enumerate(bowl):
            comma = "," if i < len(bowl) - 1 else ""
            parts = [f"season: {entry['season']}"]
            for key in [
                "powerplayEcon",
                "middleEcon",
                "deathEcon",
                "powerplayWickets",
                "middleWickets",
                "deathWickets",
            ]:
                parts.append(f"{key}: {js_value(entry.get(key))}")
            lines.append(f"                {{ {', '.join(parts)} }}{comma}")
        lines.append("            ]")

        comma = "," if abbrev != TEAM_ORDER[-1] else ""
        lines.append(f"        }}{comma}")

    lines.append("    }")
    lines.append("};")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------


def main():
    print("=" * 60)
    print("Generating venue_data.js and historic_trends.js for The Lab")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"  ERROR: DuckDB not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # --- VENUE DATA ---
        print("\n[1/5] Querying venue profiles...")
        profiles = get_venue_profiles(conn)
        print(f"       {len(profiles)} team home venue profiles loaded")

        print("[2/5] Classifying venue characters...")
        profiles = classify_venue_character(profiles, conn)
        for abbrev in TEAM_ORDER:
            p = profiles[abbrev]
            print(
                f"       {abbrev}: {p['character']} | "
                f"avg1stInnings={p['avgFirstInningsScore']} | "
                f"chaseFriendly={p['chaseFriendly']}"
            )

        print("[3/5] Loading team venue records...")
        venue_records = get_team_venue_records_from_csv()
        if venue_records is None:
            print("       CSV not found, deriving from database...")
            venue_records = get_team_venue_records_from_db(conn)
        total_recs = sum(len(v) for v in venue_records.values())
        print(f"       {total_recs} venue records across {len(venue_records)} teams")

        print("       Generating venue_data.js...")
        venue_js = generate_venue_js(profiles, venue_records)
        VENUE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(VENUE_OUTPUT, "w") as f:
            f.write(venue_js)
        print(f"       Written to: {VENUE_OUTPUT}")
        print(f"       File size: {VENUE_OUTPUT.stat().st_size:,} bytes")

        # --- HISTORIC TRENDS ---
        print("\n[4/5] Querying season records...")
        season_records = get_season_records(conn)
        total_seasons = sum(len(v) for v in season_records.values())
        print(f"       {total_seasons} season entries across {len(season_records)} teams")

        print("[5/5] Querying phase trends...")
        batting_trends, bowling_trends = get_phase_trends(conn)
        total_bat = sum(len(v) for v in batting_trends.values())
        total_bowl = sum(len(v) for v in bowling_trends.values())
        print(f"       {total_bat} batting trend entries, {total_bowl} bowling trend entries")

        print("       Generating historic_trends.js...")
        trends_js = generate_trends_js(season_records, batting_trends, bowling_trends)
        TRENDS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        with open(TRENDS_OUTPUT, "w") as f:
            f.write(trends_js)
        print(f"       Written to: {TRENDS_OUTPUT}")
        print(f"       File size: {TRENDS_OUTPUT.stat().st_size:,} bytes")

        print("\n" + "=" * 60)
        print("Done. Both files generated successfully.")
        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
