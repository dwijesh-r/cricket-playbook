#!/usr/bin/env python3
"""
Cricket Playbook - Toss Advantage Index (TKT-089)
==================================================
Owner: Stephen Curry (Analytics Lead)
Epic: EPIC-011

Computes a Toss Advantage Index (TAI) per IPL venue, measuring how much
the toss-decision matters at each ground.

Metrics:
- bat_first_win_rate:   Win% when toss winner elects to bat
- field_first_win_rate: Win% when toss winner elects to field
- toss_advantage:       Overall win% for the toss-winning team
- TAI = abs(field_first_win_rate - bat_first_win_rate)
  Higher TAI => the toss decision matters more at this venue.
- preferred_decision:   'bat' or 'field' (whichever gives higher win%)

Confidence bands:
- HIGH:   >= 15 matches at venue
- MEDIUM: >= 8 matches at venue
- LOW:    < 8 matches at venue

Data scope: IPL 2023-2025 (matches with decisive results only).

Usage:
    python scripts/analysis/toss_advantage_index.py
    python scripts/analysis/toss_advantage_index.py --create-view
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from scripts.config import config
from scripts.utils.logging_config import setup_logger

logger = setup_logger(__name__)

DB_PATH = config.DB_PATH
OUTPUT_DIR = config.OUTPUT_DIR
IPL_MIN_DATE = config.IPL_MIN_DATE

# Confidence thresholds (match count at venue)
HIGH_CONFIDENCE_MIN = 15
MEDIUM_CONFIDENCE_MIN = 8


def _confidence_label(matches: int) -> str:
    """Return confidence band based on venue match count."""
    if matches >= HIGH_CONFIDENCE_MIN:
        return "HIGH"
    if matches >= MEDIUM_CONFIDENCE_MIN:
        return "MEDIUM"
    return "LOW"


def compute_venue_toss_advantage(conn: duckdb.DuckDBPyConnection) -> list[dict]:
    """Compute per-venue toss advantage metrics.

    Returns a list of dicts, one per venue, sorted by TAI descending.
    """
    rows = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT
                dm.match_id,
                dm.venue_id,
                dm.toss_winner_id,
                dm.toss_decision,
                dm.winner_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND dm.winner_id IS NOT NULL
        ),
        venue_stats AS (
            SELECT
                im.venue_id,
                dv.venue_name,
                dv.city,
                COUNT(*) AS matches,
                -- Bat-first stats (toss winner chose to bat)
                COUNT(*) FILTER (WHERE im.toss_decision = 'bat') AS bat_first_total,
                COUNT(*) FILTER (WHERE im.toss_decision = 'bat'
                                   AND im.toss_winner_id = im.winner_id) AS bat_first_wins,
                -- Field-first stats (toss winner chose to field)
                COUNT(*) FILTER (WHERE im.toss_decision = 'field') AS field_first_total,
                COUNT(*) FILTER (WHERE im.toss_decision = 'field'
                                   AND im.toss_winner_id = im.winner_id) AS field_first_wins,
                -- Overall toss advantage
                COUNT(*) FILTER (WHERE im.toss_winner_id = im.winner_id) AS toss_wins
            FROM ipl_matches im
            JOIN dim_venue dv ON im.venue_id = dv.venue_id
            GROUP BY im.venue_id, dv.venue_name, dv.city
        )
        SELECT *
        FROM venue_stats
        ORDER BY matches DESC
    """).fetchall()

    columns = [
        "venue_id",
        "venue_name",
        "city",
        "matches",
        "bat_first_total",
        "bat_first_wins",
        "field_first_total",
        "field_first_wins",
        "toss_wins",
    ]

    venues = []
    for row in rows:
        d = dict(zip(columns, row))

        bat_rate = d["bat_first_wins"] / d["bat_first_total"] if d["bat_first_total"] > 0 else 0.0
        field_rate = (
            d["field_first_wins"] / d["field_first_total"] if d["field_first_total"] > 0 else 0.0
        )
        toss_adv = d["toss_wins"] / d["matches"] if d["matches"] > 0 else 0.0
        tai = abs(field_rate - bat_rate)

        venues.append(
            {
                "venue_id": d["venue_id"],
                "venue_name": d["venue_name"],
                "city": d["city"],
                "matches": d["matches"],
                "bat_first_wins": d["bat_first_wins"],
                "bat_first_total": d["bat_first_total"],
                "bat_first_win_rate": round(bat_rate, 4),
                "field_first_wins": d["field_first_wins"],
                "field_first_total": d["field_first_total"],
                "field_first_win_rate": round(field_rate, 4),
                "toss_advantage": round(toss_adv, 4),
                "tai": round(tai, 4),
                "preferred_decision": "bat" if bat_rate >= field_rate else "field",
                "confidence": _confidence_label(d["matches"]),
            }
        )

    # Sort by TAI descending (venues where decision matters most first)
    venues.sort(key=lambda v: v["tai"], reverse=True)
    return venues


def compute_league_average(conn: duckdb.DuckDBPyConnection) -> dict:
    """Compute league-wide toss advantage averages as a reference baseline."""
    row = conn.execute(f"""
        SELECT
            COUNT(*) AS matches,
            COUNT(*) FILTER (WHERE dm.toss_decision = 'bat') AS bat_total,
            COUNT(*) FILTER (WHERE dm.toss_decision = 'bat'
                               AND dm.toss_winner_id = dm.winner_id) AS bat_wins,
            COUNT(*) FILTER (WHERE dm.toss_decision = 'field') AS field_total,
            COUNT(*) FILTER (WHERE dm.toss_decision = 'field'
                               AND dm.toss_winner_id = dm.winner_id) AS field_wins,
            COUNT(*) FILTER (WHERE dm.toss_winner_id = dm.winner_id) AS toss_wins
        FROM dim_match dm
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
          AND dm.winner_id IS NOT NULL
    """).fetchone()

    matches, bat_total, bat_wins, field_total, field_wins, toss_wins = row

    bat_rate = bat_wins / bat_total if bat_total > 0 else 0.0
    field_rate = field_wins / field_total if field_total > 0 else 0.0
    toss_adv = toss_wins / matches if matches > 0 else 0.0

    return {
        "matches": matches,
        "bat_first_win_rate": round(bat_rate, 4),
        "field_first_win_rate": round(field_rate, 4),
        "toss_advantage": round(toss_adv, 4),
    }


def save_results(venues: list[dict], league_avg: dict, output_path: Path) -> None:
    """Save toss advantage index results to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_scope": "IPL 2023-2025",
        "matches_analyzed": league_avg["matches"],
        "league_average": {
            "bat_first_win_rate": league_avg["bat_first_win_rate"],
            "field_first_win_rate": league_avg["field_first_win_rate"],
            "toss_advantage": league_avg["toss_advantage"],
        },
        "venues": venues,
    }

    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)

    logger.info("Results saved to %s", output_path)


def create_toss_advantage_view(conn: duckdb.DuckDBPyConnection) -> None:
    """Create (or replace) analytics_ipl_toss_advantage view in DuckDB."""
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_toss_advantage AS
        WITH ipl_matches AS (
            SELECT
                dm.match_id,
                dm.venue_id,
                dm.toss_winner_id,
                dm.toss_decision,
                dm.winner_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND dm.winner_id IS NOT NULL
        ),
        venue_stats AS (
            SELECT
                im.venue_id,
                dv.venue_name,
                dv.city,
                COUNT(*) AS matches,
                COUNT(*) FILTER (WHERE im.toss_decision = 'bat') AS bat_first_total,
                COUNT(*) FILTER (WHERE im.toss_decision = 'bat'
                                   AND im.toss_winner_id = im.winner_id) AS bat_first_wins,
                COUNT(*) FILTER (WHERE im.toss_decision = 'field') AS field_first_total,
                COUNT(*) FILTER (WHERE im.toss_decision = 'field'
                                   AND im.toss_winner_id = im.winner_id) AS field_first_wins,
                COUNT(*) FILTER (WHERE im.toss_winner_id = im.winner_id) AS toss_wins
            FROM ipl_matches im
            JOIN dim_venue dv ON im.venue_id = dv.venue_id
            GROUP BY im.venue_id, dv.venue_name, dv.city
        )
        SELECT
            venue_id,
            venue_name,
            city,
            matches,
            bat_first_wins,
            bat_first_total,
            ROUND(COALESCE(bat_first_wins * 1.0 / NULLIF(bat_first_total, 0), 0), 4) AS bat_first_win_rate,
            field_first_wins,
            field_first_total,
            ROUND(COALESCE(field_first_wins * 1.0 / NULLIF(field_first_total, 0), 0), 4) AS field_first_win_rate,
            ROUND(toss_wins * 1.0 / matches, 4) AS toss_advantage,
            ROUND(ABS(
                COALESCE(field_first_wins * 1.0 / NULLIF(field_first_total, 0), 0)
                - COALESCE(bat_first_wins * 1.0 / NULLIF(bat_first_total, 0), 0)
            ), 4) AS tai,
            CASE
                WHEN COALESCE(bat_first_wins * 1.0 / NULLIF(bat_first_total, 0), 0)
                     >= COALESCE(field_first_wins * 1.0 / NULLIF(field_first_total, 0), 0)
                THEN 'bat'
                ELSE 'field'
            END AS preferred_decision,
            CASE
                WHEN matches >= {HIGH_CONFIDENCE_MIN} THEN 'HIGH'
                WHEN matches >= {MEDIUM_CONFIDENCE_MIN} THEN 'MEDIUM'
                ELSE 'LOW'
            END AS confidence
        FROM venue_stats
        ORDER BY tai DESC
    """)
    logger.info("Created DuckDB view: analytics_ipl_toss_advantage")


def print_summary(venues: list[dict], league_avg: dict) -> None:
    """Print a formatted summary table to stdout."""
    print()
    print("=" * 100)
    print("TOSS ADVANTAGE INDEX  |  IPL 2023-2025")
    print("=" * 100)
    print()

    # League averages
    print("LEAGUE AVERAGES ({} matches)".format(league_avg["matches"]))
    print("  Bat-first win rate  : {:.1%}".format(league_avg["bat_first_win_rate"]))
    print("  Field-first win rate: {:.1%}".format(league_avg["field_first_win_rate"]))
    print("  Toss advantage      : {:.1%}".format(league_avg["toss_advantage"]))
    print()

    # Venue table header
    hdr = "{:<45s} {:>5s} {:>6s} {:>6s}  {:>6s} {:>6s}  {:>5s}  {:>5s} {:>6s}".format(
        "Venue",
        "M",
        "BatW%",
        "FldW%",
        "TAI",
        "TossA",
        "Pref",
        "Conf",
        "City",
    )
    print(hdr)
    print("-" * 100)

    for v in venues:
        line = "{:<45s} {:>5d} {:>5.1%} {:>6.1%}  {:>5.1%} {:>6.1%}  {:>5s} {:>6s} {:>6s}".format(
            v["venue_name"][:45],
            v["matches"],
            v["bat_first_win_rate"],
            v["field_first_win_rate"],
            v["tai"],
            v["toss_advantage"],
            v["preferred_decision"],
            v["confidence"],
            v["city"],
        )
        print(line)

    print("-" * 100)
    print(f"Total venues: {len(venues)}")
    print()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Toss Advantage Index (TKT-089)")
    parser.add_argument(
        "--create-view",
        action="store_true",
        help="Create analytics_ipl_toss_advantage view in DuckDB",
    )
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("Cricket Playbook - Toss Advantage Index (TKT-089)")
    logger.info("=" * 70)

    if not DB_PATH.exists():
        logger.error("Database not found at %s", DB_PATH)
        return 1

    read_only = not args.create_view
    conn = duckdb.connect(str(DB_PATH), read_only=read_only)

    try:
        logger.info("[1/3] Computing per-venue toss advantage...")
        venues = compute_venue_toss_advantage(conn)
        logger.info("Venues analyzed: %d", len(venues))

        logger.info("[2/3] Computing league-wide averages...")
        league_avg = compute_league_average(conn)
        logger.info(
            "League avg — Bat: %.1f%%, Field: %.1f%%, Toss advantage: %.1f%%",
            league_avg["bat_first_win_rate"] * 100,
            league_avg["field_first_win_rate"] * 100,
            league_avg["toss_advantage"] * 100,
        )

        logger.info("[3/3] Saving results...")
        output_path = OUTPUT_DIR / "toss_advantage_index.json"
        save_results(venues, league_avg, output_path)

        if args.create_view:
            create_toss_advantage_view(conn)

        print_summary(venues, league_avg)

    finally:
        conn.close()

    logger.info("Toss Advantage Index complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
