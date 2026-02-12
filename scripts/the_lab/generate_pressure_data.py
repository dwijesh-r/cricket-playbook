#!/usr/bin/env python3
"""
Generate pressure_metrics.js for The Lab dashboard.

Queries DuckDB pressure performance views (TKT-050) and exports
per-team pressure summaries as a self-contained JavaScript data file.

Enhanced: Per-RRR-band breakdowns, over-phase stats (15-17, 18-20),
entry context, and qualification criteria display.

Usage:
    python scripts/the_lab/generate_pressure_data.py
"""

import json
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

# Qualification thresholds (10 overs = 60 balls minimum)
MIN_BATTER_PRESSURE_BALLS = 60
MIN_BATTER_OVERALL_BALLS = 50
MIN_BOWLER_LEGAL_BALLS = 60  # 10 overs across HIGH+ bands
MIN_BOWLER_BAND_BALLS = 15  # Per-band minimum for band breakdown display

# RRR band ordering for display
BAND_ORDER = ["COMFORTABLE", "BUILDING", "HIGH", "EXTREME", "NEAR_IMPOSSIBLE"]


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
    """Get ALL qualifying batters per team (JS handles sort/limit by active filter)."""
    rows = conn.execute("""
        SELECT
            sq.team_name,
            pd.player_id,
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
            pd.avg_balls_before_pressure
        FROM analytics_ipl_pressure_deltas_since2023 pd
        JOIN ipl_2026_squads sq ON pd.player_id = sq.player_id
        ORDER BY sq.team_name, pd.pressure_score DESC
    """).fetchall()

    batters = {}
    for row in rows:
        (
            team_name,
            player_id,
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
            avg_balls_before,
        ) = row
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in batters:
            batters[abbrev] = []
        batters[abbrev].append(
            {
                "playerId": player_id,
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
                "avgBallsBefore": round(float(avg_balls_before), 1)
                if avg_balls_before is not None
                else 0.0,
            }
        )

    return batters


def get_top_pressure_bowlers(conn):
    """Get ALL qualifying bowlers under pressure per team (JS handles sort/limit).

    Uses stricter minimum (60 balls across HIGH+ bands) for credibility.
    Deduplicates bowlers across multiple bands by aggregating.
    """
    rows = conn.execute(f"""
        WITH band_priority AS (
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
              AND bwl.legal_balls >= {MIN_BOWLER_BAND_BALLS}
        ),
        aggregated AS (
            SELECT
                team_name,
                player_id,
                player_name,
                FIRST(pressure_band ORDER BY band_rank DESC) AS pressure_band,
                ROUND(SUM(economy * legal_balls) / SUM(legal_balls), 2) AS economy,
                SUM(legal_balls) AS legal_balls,
                SUM(wickets) AS wickets,
                ROUND(SUM(dot_ball_pct * legal_balls) / SUM(legal_balls), 2) AS dot_ball_pct
            FROM band_priority
            GROUP BY team_name, player_id, player_name
            HAVING SUM(legal_balls) >= {MIN_BOWLER_LEGAL_BALLS}
        )
        SELECT team_name, player_id, player_name, pressure_band, economy,
               legal_balls, wickets, dot_ball_pct
        FROM aggregated
        ORDER BY team_name, economy ASC
    """).fetchall()

    bowlers = {}
    for row in rows:
        team_name, player_id, name, band, econ, balls, wkts, dot_pct = row
        abbrev = TEAM_ABBREV.get(team_name)
        if not abbrev:
            continue
        if abbrev not in bowlers:
            bowlers[abbrev] = []

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
                "playerId": player_id,
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


def get_batter_band_breakdown(conn, batter_ids):
    """Get per-RRR-band stats for specific batters."""
    if not batter_ids:
        return {}

    id_list = ", ".join(f"'{pid}'" for pid in batter_ids)
    rows = conn.execute(f"""
        SELECT
            player_id,
            pressure_band,
            balls_faced,
            strike_rate,
            boundary_pct,
            dot_ball_pct,
            six_pct,
            entry_context
        FROM analytics_ipl_batter_pressure_bands_since2023
        WHERE player_id IN ({id_list})
        ORDER BY player_id, pressure_band
    """).fetchall()

    breakdown = {}
    for pid, band, balls, sr, bdry, dot, six_pct, entry_ctx in rows:
        if pid not in breakdown:
            breakdown[pid] = []
        breakdown[pid].append(
            {
                "band": band,
                "balls": int(balls) if balls else 0,
                "sr": round(float(sr), 1) if sr else 0.0,
                "boundaryPct": round(float(bdry), 1) if bdry else 0.0,
                "dotPct": round(float(dot), 1) if dot else 0.0,
                "sixPct": round(float(six_pct), 1) if six_pct else 0.0,
            }
        )

    # Sort each player's bands in canonical order
    for pid in breakdown:
        breakdown[pid].sort(
            key=lambda x: BAND_ORDER.index(x["band"]) if x["band"] in BAND_ORDER else 99
        )

    return breakdown


def get_bowler_band_breakdown(conn, bowler_ids):
    """Get per-RRR-band stats for specific bowlers."""
    if not bowler_ids:
        return {}

    id_list = ", ".join(f"'{pid}'" for pid in bowler_ids)
    rows = conn.execute(f"""
        SELECT
            player_id,
            pressure_band,
            legal_balls,
            economy,
            dot_ball_pct,
            boundary_conceded_pct,
            wickets
        FROM analytics_ipl_bowler_pressure_bands_since2023
        WHERE player_id IN ({id_list})
        ORDER BY player_id, pressure_band
    """).fetchall()

    breakdown = {}
    for pid, band, balls, econ, dot, bdry_conceded, wkts in rows:
        if pid not in breakdown:
            breakdown[pid] = []
        breakdown[pid].append(
            {
                "band": band,
                "balls": int(balls) if balls else 0,
                "economy": round(float(econ), 2) if econ else 0.0,
                "dotPct": round(float(dot), 1) if dot else 0.0,
                "boundaryConcededPct": round(float(bdry_conceded), 1) if bdry_conceded else 0.0,
                "wickets": int(wkts) if wkts else 0,
            }
        )

    for pid in breakdown:
        breakdown[pid].sort(
            key=lambda x: BAND_ORDER.index(x["band"]) if x["band"] in BAND_ORDER else 99
        )

    return breakdown


def get_phase_stats(conn, player_ids, role="batter"):
    """Get per-phase (overs 15-17 vs 18-20) pressure stats.

    Joins fact_ball with innings_progression to identify high-pressure
    balls (RRR >= 10) in specific over ranges.

    Over indexing: 0-based in DB (over 14 = human over 15).
    - Phase 'setup': overs 14-16 (human 15-17)
    - Phase 'death': overs 17-19 (human 18-20)
    """
    if not player_ids:
        return {}

    id_list = ", ".join(f"'{pid}'" for pid in player_ids)

    if role == "batter":
        query = f"""
            WITH pressure_balls AS (
                SELECT
                    fb.batter_id AS player_id,
                    fb.over,
                    fb.batter_runs,
                    fb.is_legal_ball,
                    fb.is_wicket,
                    fb.total_runs,
                    CASE
                        WHEN fb.over BETWEEN 14 AND 16 THEN 'setup'
                        WHEN fb.over BETWEEN 17 AND 19 THEN 'death'
                    END AS phase
                FROM fact_ball fb
                JOIN analytics_ipl_innings_progression_since2023 ip
                    ON fb.match_id = ip.match_id
                    AND fb.innings = ip.innings
                    AND fb.over = ip.over_number
                WHERE fb.batter_id IN ({id_list})
                  AND fb.innings = 2
                  AND ip.required_run_rate >= 10
                  AND fb.over >= 14
            )
            SELECT
                player_id,
                phase,
                COUNT(CASE WHEN is_legal_ball THEN 1 END) AS legal_balls,
                ROUND(SUM(batter_runs) * 100.0
                    / NULLIF(COUNT(CASE WHEN is_legal_ball THEN 1 END), 0), 1) AS sr,
                ROUND(SUM(CASE WHEN batter_runs IN (4, 6) THEN 1.0 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(CASE WHEN is_legal_ball THEN 1 END), 0), 1) AS boundary_pct,
                ROUND(SUM(CASE WHEN is_legal_ball AND batter_runs = 0 THEN 1.0 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(CASE WHEN is_legal_ball THEN 1 END), 0), 1) AS dot_pct
            FROM pressure_balls
            WHERE phase IS NOT NULL
            GROUP BY player_id, phase
            ORDER BY player_id, phase
        """
    else:
        query = f"""
            WITH pressure_balls AS (
                SELECT
                    fb.bowler_id AS player_id,
                    fb.over,
                    fb.total_runs,
                    fb.is_legal_ball,
                    fb.is_wicket,
                    fb.batter_runs,
                    CASE
                        WHEN fb.over BETWEEN 14 AND 16 THEN 'setup'
                        WHEN fb.over BETWEEN 17 AND 19 THEN 'death'
                    END AS phase
                FROM fact_ball fb
                JOIN analytics_ipl_innings_progression_since2023 ip
                    ON fb.match_id = ip.match_id
                    AND fb.innings = ip.innings
                    AND fb.over = ip.over_number
                WHERE fb.bowler_id IN ({id_list})
                  AND fb.innings = 2
                  AND ip.required_run_rate >= 10
                  AND fb.over >= 14
            )
            SELECT
                player_id,
                phase,
                COUNT(CASE WHEN is_legal_ball THEN 1 END) AS legal_balls,
                ROUND(SUM(total_runs) * 6.0
                    / NULLIF(COUNT(CASE WHEN is_legal_ball THEN 1 END), 0), 2) AS economy,
                ROUND(SUM(CASE WHEN is_legal_ball AND total_runs = 0 THEN 1.0 ELSE 0 END) * 100.0
                    / NULLIF(COUNT(CASE WHEN is_legal_ball THEN 1 END), 0), 1) AS dot_pct,
                SUM(CASE WHEN is_wicket THEN 1 ELSE 0 END) AS wickets
            FROM pressure_balls
            WHERE phase IS NOT NULL
            GROUP BY player_id, phase
            ORDER BY player_id, phase
        """

    rows = conn.execute(query).fetchall()

    stats = {}
    for row in rows:
        if role == "batter":
            pid, phase, balls, sr, bdry_pct, dot_pct = row
            if pid not in stats:
                stats[pid] = {}
            stats[pid][phase] = {
                "balls": int(balls) if balls else 0,
                "sr": float(sr) if sr else 0.0,
                "boundaryPct": float(bdry_pct) if bdry_pct else 0.0,
                "dotPct": float(dot_pct) if dot_pct else 0.0,
            }
        else:
            pid, phase, balls, econ, dot_pct, wkts = row
            if pid not in stats:
                stats[pid] = {}
            stats[pid][phase] = {
                "balls": int(balls) if balls else 0,
                "economy": float(econ) if econ else 0.0,
                "dotPct": float(dot_pct) if dot_pct else 0.0,
                "wickets": int(wkts) if wkts else 0,
            }

    return stats


def _js_val(v):
    """Convert a Python value to JS literal."""
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if v is None:
        return "null"
    return str(v)


def _js_obj(d, indent=12):
    """Convert a dict to a JS object literal string."""
    pad = " " * indent
    parts = []
    for k, v in d.items():
        if isinstance(v, dict):
            parts.append(f"{pad}{k}: {_js_obj(v, indent + 4)}")
        elif isinstance(v, list):
            inner = ", ".join(
                _js_obj(item, 0) if isinstance(item, dict) else _js_val(item) for item in v
            )
            parts.append(f"{pad}{k}: [{inner}]")
        else:
            parts.append(f"{pad}{k}: {_js_val(v)}")
    if indent == 0:
        return (
            "{ "
            + ", ".join(
                f"{k}: {_js_val(v)}"
                if not isinstance(v, (dict, list))
                else f"{k}: {_js_obj(v, 0) if isinstance(v, dict) else '[...]'}"
                for k, v in d.items()
            )
            + " }"
        )
    return "{\n" + ",\n".join(parts) + "\n" + " " * (indent - 4) + "}"


def generate_js(
    summary, batters, bowlers, batter_bands, bowler_bands, batter_phases, bowler_phases
):
    """Generate the JavaScript data file content."""
    timestamp = datetime.now().isoformat()

    lines = [
        "/**",
        " * The Lab - Pressure Performance Metrics (Enhanced)",
        " * IPL 2026 Pre-Season Analytics (TKT-050)",
        f" * Auto-generated: {timestamp}",
        " * Source: analytics_ipl_pressure_deltas_since2023,",
        " *         analytics_ipl_batter_pressure_bands_since2023,",
        " *         analytics_ipl_bowler_pressure_bands_since2023,",
        " *         fact_ball + analytics_ipl_innings_progression_since2023",
        " *",
        f" * Qualification: Batters >= {MIN_BATTER_PRESSURE_BALLS} pressure balls,",
        f" *               Bowlers >= {MIN_BOWLER_LEGAL_BALLS} balls in HIGH+ bands",
        " */",
        "",
        "const PRESSURE_DATA = {",
        "    _meta: {",
        f'        generated: "{timestamp}",',
        f"        minBatterPressureBalls: {MIN_BATTER_PRESSURE_BALLS},",
        f"        minBatterOverallBalls: {MIN_BATTER_OVERALL_BALLS},",
        f"        minBowlerLegalBalls: {MIN_BOWLER_LEGAL_BALLS},",
        f"        minBowlerBandBalls: {MIN_BOWLER_BAND_BALLS},",
        '        bandOrder: ["COMFORTABLE", "BUILDING", "HIGH", "EXTREME", "NEAR_IMPOSSIBLE"],',
        '        phases: { setup: "Overs 15-17", death: "Overs 18-20" }',
        "    },",
    ]

    for abbrev in TEAM_ORDER:
        team_summary = summary.get(
            abbrev,
            {"CLUTCH": 0, "PRESSURE_PROOF": 0, "PRESSURE_SENSITIVE": 0, "MODERATE": 0},
        )
        team_batters = batters.get(abbrev, [])
        team_bowlers = bowlers.get(abbrev, [])

        total = sum(team_summary.values())
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
                / 3,
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

        # All qualifying batters with band breakdown and phase stats (JS sorts/limits)
        lines.append("        allBatters: [")
        for b in team_batters:
            pid = b["playerId"]
            ne = b["name"].replace('"', '\\"')

            # Band breakdown array
            bands = batter_bands.get(pid, [])
            bands_js = json.dumps(bands)

            # Phase stats
            phases = batter_phases.get(pid, {})
            setup = phases.get("setup", {"balls": 0, "sr": 0, "boundaryPct": 0, "dotPct": 0})
            death = phases.get("death", {"balls": 0, "sr": 0, "boundaryPct": 0, "dotPct": 0})

            lines.append(
                f'            {{ name: "{ne}", '
                f"srDelta: {b['srDelta']}, "
                f"pressureSR: {b['pressureSR']}, "
                f"overallSR: {b['overallSR']}, "
                f'rating: "{b["rating"]}", '
                f'confidence: "{b["confidence"]}", '
                f"pressureBalls: {b['pressureBalls']}, "
                f"pressureScore: {b['pressureScore']}, "
                f"deathPressureBalls: {b['deathPressureBalls']}, "
                f'entryContext: "{b["entryContext"]}", '
                f"avgBallsBefore: {b['avgBallsBefore']}, "
                f"bandBreakdown: {bands_js}, "
                f"phaseStats: {{ "
                f"setup: {{ balls: {setup['balls']}, sr: {setup['sr']}, boundaryPct: {setup['boundaryPct']}, dotPct: {setup['dotPct']} }}, "
                f"death: {{ balls: {death['balls']}, sr: {death['sr']}, boundaryPct: {death['boundaryPct']}, dotPct: {death['dotPct']} }} "
                f"}} }},"
            )
        lines.append("        ],")

        # All qualifying bowlers with band breakdown and phase stats (JS sorts/limits)
        lines.append("        allBowlers: [")
        for bw in team_bowlers:
            pid = bw["playerId"]
            ne = bw["name"].replace('"', '\\"')

            bands = bowler_bands.get(pid, [])
            bands_js = json.dumps(bands)

            phases = bowler_phases.get(pid, {})
            setup = phases.get("setup", {"balls": 0, "economy": 0, "dotPct": 0, "wickets": 0})
            death = phases.get("death", {"balls": 0, "economy": 0, "dotPct": 0, "wickets": 0})

            lines.append(
                f'            {{ name: "{ne}", '
                f'pressureBand: "{bw["pressureBand"]}", '
                f"economy: {bw['economy']}, "
                f"legalBalls: {bw['legalBalls']}, "
                f"wickets: {bw['wickets']}, "
                f"dotBallPct: {bw['dotBallPct']}, "
                f'rating: "{bw["rating"]}", '
                f"bandBreakdown: {bands_js}, "
                f"phaseStats: {{ "
                f"setup: {{ balls: {setup['balls']}, economy: {setup['economy']}, dotPct: {setup['dotPct']}, wickets: {setup['wickets']} }}, "
                f"death: {{ balls: {death['balls']}, economy: {death['economy']}, dotPct: {death['dotPct']}, wickets: {death['wickets']} }} "
                f"}} }},"
            )
        lines.append("        ]")
        lines.append("    },")

    lines.append("};")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Generating pressure_metrics.js for The Lab (Enhanced)...")
    print("=" * 60)

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

        # Collect all player IDs for enrichment queries
        all_batter_ids = set()
        for team_batters in batters.values():
            for b in team_batters:
                all_batter_ids.add(b["playerId"])

        all_bowler_ids = set()
        for team_bowlers in bowlers.values():
            for bw in team_bowlers:
                all_bowler_ids.add(bw["playerId"])

        print(f"\n  Querying per-band breakdown for {len(all_batter_ids)} batters...")
        batter_bands = get_batter_band_breakdown(conn, all_batter_ids)
        print(f"    {sum(len(v) for v in batter_bands.values())} band entries")

        print(f"  Querying per-band breakdown for {len(all_bowler_ids)} bowlers...")
        bowler_bands = get_bowler_band_breakdown(conn, all_bowler_ids)
        print(f"    {sum(len(v) for v in bowler_bands.values())} band entries")

        print("\n  Querying phase stats (overs 15-17 vs 18-20) for batters...")
        batter_phases = get_phase_stats(conn, all_batter_ids, role="batter")
        print(f"    {sum(len(v) for v in batter_phases.values())} phase entries")

        print("  Querying phase stats (overs 15-17 vs 18-20) for bowlers...")
        bowler_phases = get_phase_stats(conn, all_bowler_ids, role="bowler")
        print(f"    {sum(len(v) for v in bowler_phases.values())} phase entries")

        print("\n  Generating JavaScript...")
        js_content = generate_js(
            summary,
            batters,
            bowlers,
            batter_bands,
            bowler_bands,
            batter_phases,
            bowler_phases,
        )

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
