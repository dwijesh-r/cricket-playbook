#!/usr/bin/env python3
"""
Generate momentum_insights.js for The Lab dashboard.

Queries DuckDB pressure dot/boundary sequence data per team, derives
Andy Flower-style tactical insights, and outputs a self-contained
JavaScript data file for the momentum/pressure sequence dashboard card.

Views used:
  - analytics_ipl_pressure_dot_sequences_since2023  (bowling pressure)
  - analytics_ipl_pressure_boundary_sequences_since2023  (batting counter-attack)
  - analytics_ipl_pressure_deltas_since2023  (clutch vs choke)
  - ipl_2026_squads  (team membership)

Usage:
    python scripts/the_lab/generate_momentum_data.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_PATH = ROOT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "momentum_insights.js"

# ---------------------------------------------------------------------------
# Team name -> abbreviation (matches teams.js / teams.html)
# ---------------------------------------------------------------------------
TEAM_ABBREV = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
}

TEAM_ORDER = ["MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"]

# Minimum pressure balls for clutch/choke qualification
MIN_PRESSURE_BALLS = 20

# ---------------------------------------------------------------------------
# Rating thresholds
# ---------------------------------------------------------------------------
BOWLING_PRESSURE_THRESHOLDS = {
    "Elite": 4.0,
    "Strong": 3.5,
    "Average": 3.0,
}  # below 3.0 = "Weak"

BATTING_RESILIENCE_THRESHOLDS = {
    "Explosive": 3.5,
    "Strong": 3.0,
    "Average": 2.5,
}  # below 2.5 = "Limited"


# ===================================================================
# Query functions
# ===================================================================


def query_dot_sequences(conn):
    """Query A: Team-level dot ball sequence pressure (bowlers).

    Returns dict keyed by team abbreviation, each containing a list of
    bowler dicts sorted by avg_dot_seq_length descending.
    """
    rows = conn.execute("""
        SELECT
            sq.team_name,
            ds.bowler_name,
            ds.dot_sequences,
            ds.avg_dot_seq_length,
            ds.max_dot_seq,
            ds.total_dots_in_sequences
        FROM analytics_ipl_pressure_dot_sequences_since2023 ds
        JOIN ipl_2026_squads sq ON ds.bowler_id = sq.player_id
        ORDER BY sq.team_name, ds.avg_dot_seq_length DESC
    """).fetchall()

    teams = {}
    for team_name, bowler_name, dot_seq, avg_len, max_seq, total_dots in rows:
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in teams:
            teams[abbrev] = []
        teams[abbrev].append(
            {
                "name": bowler_name,
                "dot_sequences": int(dot_seq) if dot_seq else 0,
                "avg_length": round(float(avg_len), 1) if avg_len else 0.0,
                "max_length": int(max_seq) if max_seq else 0,
                "total_dots": int(total_dots) if total_dots else 0,
            }
        )
    return teams


def query_boundary_sequences(conn):
    """Query B: Team-level boundary sequence pressure (batters).

    Returns dict keyed by team abbreviation, each containing a list of
    batter dicts sorted by avg_boundary_seq_length descending.
    """
    rows = conn.execute("""
        SELECT
            sq.team_name,
            bs.batter_name,
            bs.boundary_sequences,
            bs.avg_boundary_seq_length,
            bs.max_boundary_seq,
            bs.total_boundaries_in_sequences
        FROM analytics_ipl_pressure_boundary_sequences_since2023 bs
        JOIN ipl_2026_squads sq ON bs.batter_id = sq.player_id
        ORDER BY sq.team_name, bs.avg_boundary_seq_length DESC
    """).fetchall()

    teams = {}
    for team_name, batter_name, bdry_seq, avg_len, max_seq, total_bdry in rows:
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in teams:
            teams[abbrev] = []
        teams[abbrev].append(
            {
                "name": batter_name,
                "boundary_sequences": int(bdry_seq) if bdry_seq else 0,
                "avg_length": round(float(avg_len), 1) if avg_len else 0.0,
                "max_length": int(max_seq) if max_seq else 0,
                "total_boundaries": int(total_bdry) if total_bdry else 0,
            }
        )
    return teams


def query_pressure_deltas(conn):
    """Query C: Pressure deltas per player (clutch vs choke).

    Returns dict keyed by team abbreviation, each containing a list of
    player dicts sorted by sr_delta_pct descending (most clutch first).
    """
    rows = conn.execute(f"""
        SELECT
            sq.team_name,
            pd.player_name,
            pd.overall_sr,
            pd.pressure_sr,
            pd.sr_delta_pct,
            pd.pressure_balls
        FROM analytics_ipl_pressure_deltas_since2023 pd
        JOIN ipl_2026_squads sq ON pd.player_id = sq.player_id
        WHERE pd.pressure_balls >= {MIN_PRESSURE_BALLS}
        ORDER BY sq.team_name, pd.sr_delta_pct DESC
    """).fetchall()

    teams = {}
    for team_name, player_name, overall_sr, pressure_sr, sr_delta, p_balls in rows:
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in teams:
            teams[abbrev] = []
        teams[abbrev].append(
            {
                "name": player_name,
                "normal_sr": round(float(overall_sr), 1) if overall_sr is not None else 0.0,
                "pressure_sr": round(float(pressure_sr), 1) if pressure_sr is not None else 0.0,
                "delta": round(float(sr_delta), 1) if sr_delta is not None else 0.0,
                "pressure_balls": int(p_balls) if p_balls else 0,
            }
        )
    return teams


# ===================================================================
# Insight derivation
# ===================================================================


def classify_bowling_pressure(avg_dot_seq_length):
    """Classify bowling pressure rating based on top bowler's avg dot seq length."""
    if avg_dot_seq_length >= BOWLING_PRESSURE_THRESHOLDS["Elite"]:
        return "Elite"
    if avg_dot_seq_length >= BOWLING_PRESSURE_THRESHOLDS["Strong"]:
        return "Strong"
    if avg_dot_seq_length >= BOWLING_PRESSURE_THRESHOLDS["Average"]:
        return "Average"
    return "Weak"


def classify_batting_resilience(avg_boundary_seq_length):
    """Classify batting resilience / counter-attack rating."""
    if avg_boundary_seq_length >= BATTING_RESILIENCE_THRESHOLDS["Explosive"]:
        return "Explosive"
    if avg_boundary_seq_length >= BATTING_RESILIENCE_THRESHOLDS["Strong"]:
        return "Strong"
    if avg_boundary_seq_length >= BATTING_RESILIENCE_THRESHOLDS["Average"]:
        return "Average"
    return "Limited"


def build_team_data(abbrev, dot_data, boundary_data, delta_data):
    """Derive all momentum insights for a single team."""
    bowlers = dot_data.get(abbrev, [])
    batters = boundary_data.get(abbrev, [])
    deltas = delta_data.get(abbrev, [])

    # --- Bowling Pressure ---
    top_bowlers = bowlers[:3]
    team_total_dot_seq = sum(b["dot_sequences"] for b in bowlers)
    best_max_dot = max((b["max_length"] for b in bowlers), default=0)
    # Rating based on top bowler's avg dot seq length
    top_avg = top_bowlers[0]["avg_length"] if top_bowlers else 0.0
    bowling_rating = classify_bowling_pressure(top_avg)

    bowling_pressure = {
        "rating": bowling_rating,
        "topBowlers": [
            {
                "name": b["name"],
                "dotSequences": b["dot_sequences"],
                "avgLength": b["avg_length"],
                "maxLength": b["max_length"],
            }
            for b in top_bowlers
        ],
        "teamTotalSequences": team_total_dot_seq,
        "bestMaxStreak": best_max_dot,
    }

    # --- Batting Resilience ---
    top_batters = batters[:3]
    team_total_bdry_seq = sum(b["boundary_sequences"] for b in batters)
    best_max_bdry = max((b["max_length"] for b in batters), default=0)
    top_bdry_avg = top_batters[0]["avg_length"] if top_batters else 0.0
    batting_rating = classify_batting_resilience(top_bdry_avg)

    batting_resilience = {
        "rating": batting_rating,
        "topBatters": [
            {
                "name": b["name"],
                "boundarySequences": b["boundary_sequences"],
                "avgLength": b["avg_length"],
                "maxLength": b["max_length"],
            }
            for b in top_batters
        ],
        "teamTotalSequences": team_total_bdry_seq,
        "bestMaxStreak": best_max_bdry,
    }

    # --- Clutch vs Choke ---
    # deltas are already sorted by sr_delta_pct DESC (most clutch first)
    clutch_players = [p for p in deltas if p["delta"] > 0][:3]
    choke_players = sorted([p for p in deltas if p["delta"] < 0], key=lambda x: x["delta"])[:3]
    team_avg_delta = round(sum(p["delta"] for p in deltas) / len(deltas), 1) if deltas else 0.0

    clutch_performers = {
        "topClutch": [
            {
                "name": p["name"],
                "normalSR": p["normal_sr"],
                "pressureSR": p["pressure_sr"],
                "delta": f"+{p['delta']:.1f}" if p["delta"] > 0 else f"{p['delta']:.1f}",
            }
            for p in clutch_players
        ],
        "chokeRisks": [
            {
                "name": p["name"],
                "normalSR": p["normal_sr"],
                "pressureSR": p["pressure_sr"],
                "delta": f"{p['delta']:.1f}",
            }
            for p in choke_players
        ],
        "teamAvgDelta": team_avg_delta,
    }

    # --- Andy Flower Insight ---
    insight = build_insight(
        abbrev,
        bowling_pressure,
        batting_resilience,
        clutch_performers,
        top_bowlers,
        top_batters,
        choke_players,
    )

    return {
        "bowlingPressure": bowling_pressure,
        "battingResilience": batting_resilience,
        "clutchPerformers": clutch_performers,
        "andyFlowerInsight": insight,
    }


def build_insight(abbrev, bowling, batting, clutch, top_bowlers, top_batters, choke_players):
    """Build Andy Flower-style editorial insight string per team."""
    parts = []

    # Bowling pressure assessment
    if bowling["rating"] in ("Elite", "Strong") and top_bowlers:
        top = top_bowlers[0]
        parts.append(
            f"{abbrev}'s pressure game is anchored by {top['name']}'s "
            f"dot-ball sequences (avg {top['avg_length']:.1f} consecutive dots "
            f"under high RRR)"
        )
    elif top_bowlers:
        top = top_bowlers[0]
        parts.append(
            f"{abbrev} lacks a sustained dot-ball pressure weapon "
            f"-- longest avg sequence is just {top['avg_length']:.1f}"
        )
    else:
        parts.append(f"{abbrev} has no qualifying pressure bowlers in the sequence data")

    # Counter-attack capability
    if batting["rating"] in ("Explosive", "Strong") and top_batters:
        top = top_batters[0]
        parts.append(
            f"Counter-attack capability led by {top['name']} "
            f"({top['max_length']} consecutive boundaries under pressure)"
        )
    elif top_batters:
        top = top_batters[0]
        parts.append(
            f"Counter-attack capability is limited -- "
            f"{top['name']} leads with just {top['avg_length']:.1f} avg "
            f"boundary sequence length"
        )

    # Choke risks
    if choke_players:
        worst = choke_players[0]
        parts.append(
            f"Key vulnerability: {worst['name']}'s SR drops "
            f"{abs(worst['delta']):.0f}% under pressure "
            f"-- opposition will target this window"
        )

    return ". ".join(parts) + "."


# ===================================================================
# JavaScript output generation
# ===================================================================


def generate_js(all_team_data):
    """Generate the JavaScript data file content using json.dumps for safety."""
    timestamp = datetime.now(timezone.utc).isoformat()

    payload = {
        "metadata": {
            "computedAt": timestamp,
            "source": (
                "analytics_ipl_pressure_dot/boundary_sequences_since2023 "
                "+ pressure_deltas_since2023"
            ),
            "owner": "Andy Flower (Cricket Domain Expert)",
        },
        "teams": all_team_data,
    }

    # Use json.dumps with indent for readability, then wrap in var declaration
    json_str = json.dumps(payload, indent=4, ensure_ascii=False)

    lines = [
        "/**",
        " * The Lab - Momentum & Pressure Sequence Insights",
        " * IPL 2026 Pre-Season Analytics",
        f" * Auto-generated: {timestamp}",
        " * Source: analytics_ipl_pressure_dot_sequences_since2023,",
        " *         analytics_ipl_pressure_boundary_sequences_since2023,",
        " *         analytics_ipl_pressure_deltas_since2023",
        " * Owner: Andy Flower (Cricket Domain Expert)",
        " */",
        "",
        f"var MOMENTUM_INSIGHTS = {json_str};",
        "",
    ]

    return "\n".join(lines)


# ===================================================================
# Main
# ===================================================================


def main():
    print("Generating momentum_insights.js for The Lab...")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"  ERROR: DuckDB not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # Query all three data sources
        print("  Querying dot-ball pressure sequences...")
        dot_data = query_dot_sequences(conn)
        print(
            f"    {sum(len(v) for v in dot_data.values())} bowler entries "
            f"across {len(dot_data)} teams"
        )

        print("  Querying boundary sequences...")
        boundary_data = query_boundary_sequences(conn)
        print(
            f"    {sum(len(v) for v in boundary_data.values())} batter entries "
            f"across {len(boundary_data)} teams"
        )

        print("  Querying pressure deltas (clutch/choke)...")
        delta_data = query_pressure_deltas(conn)
        print(
            f"    {sum(len(v) for v in delta_data.values())} player entries "
            f"across {len(delta_data)} teams"
        )

        # Derive insights per team
        print("\n  Deriving insights per team...")
        all_team_data = {}
        for abbrev in TEAM_ORDER:
            team_result = build_team_data(abbrev, dot_data, boundary_data, delta_data)
            all_team_data[abbrev] = team_result

            bp = team_result["bowlingPressure"]
            br = team_result["battingResilience"]
            cp = team_result["clutchPerformers"]
            print(
                f"    {abbrev}: bowling={bp['rating']}, "
                f"batting={br['rating']}, "
                f"avgDelta={cp['teamAvgDelta']:+.1f}%"
            )

        # Generate JavaScript output
        print("\n  Generating JavaScript...")
        js_content = generate_js(all_team_data)

        # Validate basic JS structure
        if js_content.count("{") != js_content.count("}"):
            print("  WARNING: Brace mismatch detected in output!")
        if "var MOMENTUM_INSIGHTS" not in js_content:
            print("  WARNING: Missing var declaration!")

        # Write output
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(js_content)

        print(f"\n  Written to: {OUTPUT_PATH}")
        print(f"  File size: {OUTPUT_PATH.stat().st_size:,} bytes")

        # Summary
        team_count = len(all_team_data)
        missing = [t for t in TEAM_ORDER if t not in all_team_data]
        print(f"\n  Teams covered: {team_count}/10")
        if missing:
            print(f"  Missing teams: {', '.join(missing)}")

        print("\n  Done.")
        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
