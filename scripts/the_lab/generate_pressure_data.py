#!/usr/bin/env python3
"""
Generate pressure_metrics.js for The Lab dashboard.

Queries DuckDB pressure performance views (TKT-050) and exports
per-team pressure summaries as a self-contained JavaScript data file.

Usage:
    python scripts/the_lab/generate_pressure_data.py
"""

from datetime import datetime
from pathlib import Path

import duckdb

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_PATH = ROOT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "pressure_metrics.js"

# Team name to abbreviation mapping (matches teams.js / teams.html)
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


def get_team_pressure_summary(conn):
    """Get CLUTCH/PRESSURE_PROOF/PRESSURE_SENSITIVE counts per team."""
    rows = conn.execute("""
        SELECT
            sq.team_name,
            pd.pressure_rating,
            COUNT(*) as cnt
        FROM analytics_ipl_pressure_deltas_since2023 pd
        JOIN ipl_2026_squads sq ON pd.player_id = sq.player_id
        GROUP BY sq.team_name, pd.pressure_rating
        ORDER BY sq.team_name, pd.pressure_rating
    """).fetchall()

    summary = {}
    for team_name, rating, cnt in rows:
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in summary:
            summary[abbrev] = {
                "CLUTCH": 0,
                "PRESSURE_PROOF": 0,
                "PRESSURE_SENSITIVE": 0,
                "MODERATE": 0,
            }
        summary[abbrev][rating] = cnt

    return summary


def get_top_clutch_batters(conn):
    """Get top 3 clutch batters per team by weighted pressure score."""
    rows = conn.execute("""
        WITH ranked AS (
            SELECT
                sq.team_name,
                pd.player_name,
                pd.sr_delta_pct,
                pd.pressure_sr,
                pd.overall_sr,
                pd.pressure_rating,
                pd.sample_confidence,
                pd.pressure_balls,
                pd.pressure_score,
                pd.death_pressure_balls,
                pd.entry_context,
                ROW_NUMBER() OVER (
                    PARTITION BY sq.team_name
                    ORDER BY pd.pressure_score DESC
                ) as rn
            FROM analytics_ipl_pressure_deltas_since2023 pd
            JOIN ipl_2026_squads sq ON pd.player_id = sq.player_id
        )
        SELECT team_name, player_name, sr_delta_pct, pressure_sr, overall_sr,
               pressure_rating, sample_confidence, pressure_balls,
               pressure_score, death_pressure_balls, entry_context
        FROM ranked
        WHERE rn <= 3
        ORDER BY team_name, rn
    """).fetchall()

    batters = {}
    for row in rows:
        (
            team_name,
            name,
            sr_delta,
            p_sr,
            o_sr,
            rating,
            confidence,
            balls,
            score,
            death_balls,
            entry_ctx,
        ) = row
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in batters:
            batters[abbrev] = []
        batters[abbrev].append(
            {
                "name": name,
                "srDelta": float(sr_delta) if sr_delta is not None else 0.0,
                "pressureSR": float(p_sr) if p_sr is not None else 0.0,
                "overallSR": float(o_sr) if o_sr is not None else 0.0,
                "rating": rating,
                "confidence": confidence,
                "pressureBalls": int(balls) if balls is not None else 0,
                "pressureScore": round(float(score), 2) if score is not None else 0.0,
                "deathPressureBalls": int(death_balls) if death_balls is not None else 0,
                "entryContext": entry_ctx if entry_ctx else "N/A",
            }
        )

    return batters


def get_top_pressure_bowlers(conn):
    """Get top 3 unique bowlers under pressure per team (lowest economy in HIGH+ bands).

    Deduplicates bowlers who appear in multiple pressure bands by keeping
    the highest band (most extreme pressure = most interesting) for display,
    while aggregating balls/wickets across all qualifying bands.
    """
    rows = conn.execute("""
        WITH band_priority AS (
            -- Assign numeric priority: higher = more extreme pressure
            SELECT
                sq.team_name,
                bwl.player_id,
                bwl.player_name,
                bwl.pressure_band,
                bwl.economy,
                bwl.legal_balls,
                bwl.wickets,
                bwl.dot_ball_pct,
                CASE bwl.pressure_band
                    WHEN 'NEAR_IMPOSSIBLE' THEN 3
                    WHEN 'EXTREME' THEN 2
                    WHEN 'HIGH' THEN 1
                    ELSE 0
                END AS band_rank
            FROM analytics_ipl_bowler_pressure_bands_since2023 bwl
            JOIN ipl_2026_squads sq ON bwl.player_id = sq.player_id
            WHERE bwl.pressure_band IN ('HIGH', 'EXTREME', 'NEAR_IMPOSSIBLE')
              AND bwl.legal_balls >= 15
        ),
        aggregated AS (
            -- Aggregate stats across bands per bowler, keep highest band for display
            SELECT
                team_name,
                player_name,
                -- Show the highest pressure band the bowler qualifies in
                FIRST(pressure_band ORDER BY band_rank DESC) AS pressure_band,
                -- Weighted economy across all qualifying bands
                ROUND(SUM(economy * legal_balls) / SUM(legal_balls), 2) AS economy,
                SUM(legal_balls) AS legal_balls,
                SUM(wickets) AS wickets,
                ROUND(SUM(dot_ball_pct * legal_balls) / SUM(legal_balls), 2) AS dot_ball_pct
            FROM band_priority
            GROUP BY team_name, player_name
        ),
        ranked AS (
            SELECT
                team_name,
                player_name,
                pressure_band,
                economy,
                legal_balls,
                wickets,
                dot_ball_pct,
                ROW_NUMBER() OVER (
                    PARTITION BY team_name
                    ORDER BY economy ASC
                ) as rn
            FROM aggregated
        )
        SELECT team_name, player_name, pressure_band, economy,
               legal_balls, wickets, dot_ball_pct
        FROM ranked
        WHERE rn <= 3
        ORDER BY team_name, rn
    """).fetchall()

    bowlers = {}
    for row in rows:
        team_name, name, band, econ, balls, wkts, dot_pct = row
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in bowlers:
            bowlers[abbrev] = []

        # Assign pressure rating based on economy
        if econ <= 6.0:
            rating = "ELITE"
        elif econ <= 7.5:
            rating = "STRONG"
        elif econ <= 9.0:
            rating = "AVERAGE"
        else:
            rating = "VULNERABLE"

        bowlers[abbrev].append(
            {
                "name": name,
                "pressureBand": band,
                "economy": float(econ) if econ is not None else 0.0,
                "legalBalls": int(balls) if balls is not None else 0,
                "wickets": int(wkts) if wkts is not None else 0,
                "dotBallPct": float(dot_pct) if dot_pct is not None else 0.0,
                "rating": rating,
            }
        )

    return bowlers


def generate_js(summary, batters, bowlers):
    """Generate the JavaScript data file content."""
    timestamp = datetime.now().isoformat()

    lines = [
        "/**",
        " * The Lab - Pressure Performance Metrics",
        " * IPL 2026 Pre-Season Analytics (TKT-050)",
        f" * Auto-generated: {timestamp}",
        " * Source: analytics_ipl_pressure_deltas_since2023,",
        " *         analytics_ipl_batter_pressure_bands_since2023,",
        " *         analytics_ipl_bowler_pressure_bands_since2023",
        " */",
        "",
        "const PRESSURE_DATA = {",
    ]

    for abbrev in TEAM_ORDER:
        team_summary = summary.get(
            abbrev,
            {
                "CLUTCH": 0,
                "PRESSURE_PROOF": 0,
                "PRESSURE_SENSITIVE": 0,
                "MODERATE": 0,
            },
        )
        team_batters = batters.get(abbrev, [])
        team_bowlers = bowlers.get(abbrev, [])

        # Compute a clutch factor score: (CLUTCH*3 + PP*2 + MOD*1 - SENS*2) / total
        total = (
            team_summary["CLUTCH"]
            + team_summary["PRESSURE_PROOF"]
            + team_summary["PRESSURE_SENSITIVE"]
            + team_summary["MODERATE"]
        )
        if total > 0:
            clutch_score = round(
                (
                    team_summary["CLUTCH"] * 3
                    + team_summary["PRESSURE_PROOF"] * 2
                    + team_summary["MODERATE"] * 1
                    - team_summary["PRESSURE_SENSITIVE"] * 2
                )
                / total
                * 10
                / 3,  # Normalize to ~0-10 scale
                1,
            )
            clutch_score = max(0, min(10, clutch_score))
        else:
            clutch_score = 0

        lines.append(f"    {abbrev}: {{")
        lines.append("        summary: {")
        lines.append(f"            clutch: {team_summary['CLUTCH']},")
        lines.append(f"            pressureProof: {team_summary['PRESSURE_PROOF']},")
        lines.append(f"            pressureSensitive: {team_summary['PRESSURE_SENSITIVE']},")
        lines.append(f"            moderate: {team_summary['MODERATE']},")
        lines.append(f"            total: {total},")
        lines.append(f"            clutchScore: {clutch_score}")
        lines.append("        },")

        # Clutch batters
        lines.append("        topBatters: [")
        for b in team_batters:
            name_escaped = b["name"].replace('"', '\\"')
            lines.append(
                f'            {{ name: "{name_escaped}", '
                f"srDelta: {b['srDelta']}, "
                f"pressureSR: {b['pressureSR']}, "
                f"overallSR: {b['overallSR']}, "
                f'rating: "{b["rating"]}", '
                f'confidence: "{b["confidence"]}", '
                f"pressureBalls: {b['pressureBalls']}, "
                f"pressureScore: {b['pressureScore']}, "
                f"deathPressureBalls: {b['deathPressureBalls']}, "
                f'entryContext: "{b["entryContext"]}" }},'
            )
        lines.append("        ],")

        # Pressure bowlers
        lines.append("        topBowlers: [")
        for bw in team_bowlers:
            name_escaped = bw["name"].replace('"', '\\"')
            lines.append(
                f'            {{ name: "{name_escaped}", '
                f'pressureBand: "{bw["pressureBand"]}", '
                f"economy: {bw['economy']}, "
                f"legalBalls: {bw['legalBalls']}, "
                f"wickets: {bw['wickets']}, "
                f"dotBallPct: {bw['dotBallPct']}, "
                f'rating: "{bw["rating"]}" }},'
            )
        lines.append("        ]")
        lines.append("    },")

    lines.append("};")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Generating pressure_metrics.js for The Lab...")
    print("=" * 50)

    if not DB_PATH.exists():
        print(f"  ERROR: DuckDB not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        print("  Querying pressure deltas (team summary)...")
        summary = get_team_pressure_summary(conn)
        print(f"    {len(summary)} teams with pressure data")

        print("  Querying top clutch batters per team...")
        batters = get_top_clutch_batters(conn)
        total_batters = sum(len(v) for v in batters.values())
        print(f"    {total_batters} batter entries across {len(batters)} teams")

        print("  Querying top pressure bowlers per team...")
        bowlers = get_top_pressure_bowlers(conn)
        total_bowlers = sum(len(v) for v in bowlers.values())
        print(f"    {total_bowlers} bowler entries across {len(bowlers)} teams")

        print("\n  Generating JavaScript...")
        js_content = generate_js(summary, batters, bowlers)

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w") as f:
            f.write(js_content)

        print(f"  Written to: {OUTPUT_PATH}")
        print(f"  File size: {OUTPUT_PATH.stat().st_size:,} bytes")
        print("\n  Done.")
        return 0

    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
