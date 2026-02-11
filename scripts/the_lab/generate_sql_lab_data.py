#!/usr/bin/env python3
"""
TKT-172: Export Parquet + View DDL Pipeline
Owner: Brock Purdy (Data Pipeline Owner)

Exports the full DuckDB database to Parquet files for browser-based SQL Lab consumption.
Generates:
  - ZSTD-compressed Parquet files for all 15 base tables
  - views.sql with all 52 view DDL statements
  - table_metadata.json with schema info, row counts, and column descriptions

Usage:
    python scripts/the_lab/generate_sql_lab_data.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import duckdb
except ImportError:
    print("ERROR: duckdb not installed. Run: pip install duckdb")
    sys.exit(1)

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = ROOT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "sql_lab"
TABLES_DIR = OUTPUT_DIR / "tables"
VIEWS_SQL = OUTPUT_DIR / "views.sql"
METADATA_JSON = OUTPUT_DIR / "table_metadata.json"

# ── Expected Tables ──────────────────────────────────────────────────────────
EXPECTED_TABLES = [
    "dim_bowler_classification",
    "dim_franchise_alias",
    "dim_match",
    "dim_player",
    "dim_player_name_history",
    "dim_team",
    "dim_tournament",
    "dim_venue",
    "fact_ball",
    "fact_player_match_performance",
    "fact_powerplay",
    "ipl_2026_contracts",
    "ipl_2026_squads",
    "player_clusters_batters",
    "player_clusters_bowlers",
]

# ── Column Description Map ───────────────────────────────────────────────────
COLUMN_DESCRIPTIONS = {
    # Identifiers
    "match_id": "Unique match identifier",
    "player_id": "Unique player identifier",
    "team_id": "Unique team identifier",
    "venue_id": "Unique venue identifier",
    "tournament_id": "Unique tournament identifier",
    "ball_id": "Unique ball-level identifier",
    "powerplay_id": "Unique powerplay identifier",
    # Player fields
    "batter_id": "Batter player identifier",
    "bowler_id": "Bowler player identifier",
    "non_striker_id": "Non-striker player identifier",
    "player_out_id": "Player dismissed identifier",
    "fielder_id": "Fielder involved in dismissal",
    "player_of_match_id": "Player of the match identifier",
    "player_name": "Player name",
    "current_name": "Current player name",
    "batter": "Batter name",
    "striker": "Batter name",
    "bowler": "Bowler name",
    # Match fields
    "season": "IPL season year",
    "match_date": "Date of the match",
    "match_number": "Match number in the tournament",
    "stage": "Tournament stage (league, playoff, final)",
    "toss_winner_id": "Team that won the toss",
    "toss_decision": "Toss decision (bat/field)",
    "winner_id": "Winning team identifier",
    "outcome_type": "Type of match outcome",
    "outcome_margin": "Margin of victory",
    "balls_per_over": "Number of balls per over",
    # Ball-level fields
    "innings": "Innings number",
    "over": "Over number",
    "ball": "Ball number within the over",
    "ball_seq": "Sequential ball number in the innings",
    "batter_runs": "Runs scored off the bat",
    "runs_off_bat": "Runs scored off the bat",
    "extra_runs": "Extra runs conceded",
    "total_runs": "Total runs from the delivery",
    "extra_type": "Type of extra (wide, noball, bye, legbye)",
    "is_wicket": "Whether a wicket fell on this delivery",
    "wicket_type": "Type of dismissal",
    "is_legal_ball": "Whether this was a legal delivery",
    "match_phase": "Phase of play (powerplay, middle, death)",
    # Team fields
    "team_name": "Team name",
    "short_name": "Team short/abbreviated name",
    "batting_team_id": "Batting team identifier",
    "bowling_team_id": "Bowling team identifier",
    "team1_id": "First team identifier",
    "team2_id": "Second team identifier",
    "canonical_name": "Standardized franchise name",
    # Venue fields
    "venue": "Match venue name",
    "venue_name": "Match venue name",
    "city": "City where venue is located",
    # Tournament fields
    "tournament_name": "Tournament name",
    "country": "Country of the tournament",
    "format": "Match format (T20, ODI, Test)",
    "gender": "Gender category (male, female)",
    # Performance fields
    "batting_position": "Batting order position",
    "did_bat": "Whether the player batted",
    "did_bowl": "Whether the player bowled",
    "did_keep_wicket": "Whether the player kept wicket",
    # Powerplay fields
    "powerplay_seq": "Powerplay sequence number",
    "powerplay_type": "Type of powerplay",
    "from_over": "Starting over of powerplay",
    "to_over": "Ending over of powerplay",
    # Contract fields
    "price_cr": "Contract price in crores (INR)",
    "acquisition_type": "How the player was acquired (auction, retention, RTM)",
    "year_joined": "Year player joined the franchise",
    # Squad fields
    "nationality": "Player nationality",
    "age": "Player age",
    "role": "Player role (batter, bowler, all-rounder)",
    "bowling_arm": "Bowling arm (left, right)",
    "bowling_type": "Bowling type (pace, spin)",
    "batting_hand": "Batting hand (left, right)",
    "batter_classification": "Batter cluster classification",
    "bowler_classification": "Bowler cluster classification",
    "batter_tags": "Analytical tags for batting style",
    "bowler_tags": "Analytical tags for bowling style",
    "is_captain": "Whether the player is team captain",
    "bowling_style": "Detailed bowling style classification",
    # Cluster fields
    "cluster_id": "Cluster assignment identifier",
    "overall_sr": "Overall strike rate",
    "overall_avg": "Overall batting/bowling average",
    "overall_boundary": "Overall boundary percentage",
    "pp_sr": "Powerplay strike rate",
    "mid_sr": "Middle overs strike rate",
    "death_sr": "Death overs strike rate",
    "death_boundary": "Death overs boundary percentage",
    "overall_economy": "Overall economy rate",
    "overall_dot": "Overall dot ball percentage",
    "pp_economy": "Powerplay economy rate",
    "mid_economy": "Middle overs economy rate",
    "death_economy": "Death overs economy rate",
    "pp_pct": "Percentage of overs bowled in powerplay",
    "mid_pct": "Percentage of overs bowled in middle overs",
    "death_pct": "Percentage of overs bowled in death overs",
    # Player history fields
    "valid_from": "Start date of name validity",
    "valid_to": "End date of name validity",
    "first_seen_date": "First appearance date",
    "last_seen_date": "Most recent appearance date",
    "matches_played": "Total matches played",
    "is_wicketkeeper": "Whether the player is a wicketkeeper",
    "primary_role": "Primary playing role",
    # Metadata fields
    "data_version": "Data pipeline version",
    "is_active": "Whether the record is currently active",
    "ingested_at": "Timestamp of data ingestion",
    "source_file": "Source data file path",
}

# ── Table Descriptions ───────────────────────────────────────────────────────
TABLE_DESCRIPTIONS = {
    "dim_bowler_classification": "Bowler style classifications for all players",
    "dim_franchise_alias": "Franchise name aliases and canonical mappings",
    "dim_match": "Match-level metadata for all cricket matches",
    "dim_player": "Player dimension table with current names and roles",
    "dim_player_name_history": "Historical player name changes over time",
    "dim_team": "Team dimension table with names and abbreviations",
    "dim_tournament": "Tournament metadata (name, country, format)",
    "dim_venue": "Venue dimension table with city locations",
    "fact_ball": "Ball-by-ball delivery data for all matches",
    "fact_player_match_performance": "Per-player per-match performance flags",
    "fact_powerplay": "Powerplay period definitions for each match innings",
    "ipl_2026_contracts": "IPL 2026 player contract details and prices",
    "ipl_2026_squads": "IPL 2026 full squad rosters with player profiles",
    "player_clusters_batters": "K-means batter cluster assignments with phase metrics",
    "player_clusters_bowlers": "K-means bowler cluster assignments with phase metrics",
}

# ── View Category Mapping ────────────────────────────────────────────────────


def classify_view(view_name: str) -> str:
    """Map view name to category based on prefix patterns."""
    name = view_name.lower()
    if "pressure" in name:
        return "pressure"
    if "batter" in name or "batting" in name or "powerplay_hitter" in name:
        return "batting"
    if "bowler" in name or "bowling" in name or "death_over" in name:
        return "bowling"
    if "squad" in name or "team" in name or "roster" in name:
        return "team"
    if "top_" in name or "best_" in name:
        return "leaderboard"
    if "benchmark" in name or "percentile" in name:
        return "benchmarks"
    return "general"


def describe_view(view_name: str) -> str:
    """Generate a human-readable description from the view name."""
    # Remove common prefixes
    name = view_name
    for prefix in ["analytics_ipl_", "analytics_t20_", "analytics_"]:
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break
    # Convert underscores to spaces and title-case
    desc = name.replace("_", " ").strip()
    desc = desc[0].upper() + desc[1:] if desc else view_name
    # Add context
    if "ipl" in view_name.lower():
        desc = f"IPL {desc}" if not desc.lower().startswith("ipl") else desc
    return desc


def get_table_type(table_name: str) -> str:
    """Determine table type from naming convention."""
    if table_name.startswith("fact_"):
        return "fact"
    if table_name.startswith("dim_"):
        return "dimension"
    if table_name.startswith("player_clusters_"):
        return "analytics"
    if table_name.startswith("ipl_2026_"):
        return "reference"
    return "other"


def get_column_description(col_name: str) -> str:
    """Look up or generate a column description."""
    if col_name in COLUMN_DESCRIPTIONS:
        return COLUMN_DESCRIPTIONS[col_name]
    # Fallback: convert name to readable form
    return col_name.replace("_", " ").capitalize()


def export_tables(con) -> dict:
    """Export all base tables to ZSTD-compressed Parquet files."""
    print("\n--- Exporting Tables to Parquet ---")
    table_meta = {}
    total_rows = 0

    tables = con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='main' AND table_type='BASE TABLE' "
        "ORDER BY table_name"
    ).fetchall()

    actual_tables = [t[0] for t in tables]

    # Verify expected tables exist
    missing = set(EXPECTED_TABLES) - set(actual_tables)
    if missing:
        print(f"  WARNING: Missing expected tables: {missing}")

    extra = set(actual_tables) - set(EXPECTED_TABLES)
    if extra:
        print(f"  NOTE: Found additional tables: {extra}")

    for table_name in actual_tables:
        parquet_path = TABLES_DIR / f"{table_name}.parquet"

        # Get row count
        row_count = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
        total_rows += row_count

        # Get column info
        columns = con.execute(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_name='{table_name}' AND table_schema='main' "
            f"ORDER BY ordinal_position"
        ).fetchall()

        col_info = [
            {
                "name": col_name,
                "type": col_type,
                "description": get_column_description(col_name),
            }
            for col_name, col_type in columns
        ]

        # Export to Parquet with ZSTD compression
        con.execute(
            f"COPY (SELECT * FROM \"{table_name}\") TO '{parquet_path}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD)"
        )

        file_size = parquet_path.stat().st_size
        print(f"  {table_name}: {row_count:>10,} rows -> {file_size / 1024 / 1024:.2f} MB")

        table_meta[table_name] = {
            "type": get_table_type(table_name),
            "rows": row_count,
            "description": TABLE_DESCRIPTIONS.get(
                table_name, table_name.replace("_", " ").capitalize()
            ),
            "columns": col_info,
        }

    return table_meta, total_rows


def export_views(con) -> dict:
    """Extract all view DDL statements and write to views.sql."""
    print("\n--- Extracting View DDL ---")

    views = con.execute(
        "SELECT view_name, sql FROM duckdb_views() WHERE schema_name='main'"
    ).fetchall()

    # Filter out system views
    user_views = [
        (name, sql)
        for name, sql in views
        if not name.startswith("duckdb_")
        and not name.startswith("pragma_")
        and not name.startswith("sqlite_")
    ]

    user_views.sort(key=lambda x: x[0])

    # Write views.sql
    with open(VIEWS_SQL, "w") as f:
        f.write("-- =============================================================\n")
        f.write("-- Cricket Playbook - View DDL Definitions\n")
        f.write(f"-- Generated: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"-- Total views: {len(user_views)}\n")
        f.write("-- =============================================================\n\n")

        for view_name, view_sql in user_views:
            # The sql column from duckdb_views() already contains "CREATE VIEW ... AS ..."
            # Replace "CREATE VIEW" with "CREATE OR REPLACE VIEW"
            cleaned_sql = view_sql.strip()
            if cleaned_sql.upper().startswith("CREATE VIEW"):
                cleaned_sql = "CREATE OR REPLACE VIEW" + cleaned_sql[len("CREATE VIEW") :]
            else:
                cleaned_sql = f"CREATE OR REPLACE VIEW {view_name} AS\n{cleaned_sql}"
            # Remove trailing semicolons from DuckDB's stored SQL before adding our own
            cleaned_sql = cleaned_sql.rstrip(";")
            f.write(f"{cleaned_sql};\n\n")

    print(f"  Wrote {len(user_views)} view definitions to {VIEWS_SQL}")

    # Build view metadata
    view_meta = {}
    for view_name, view_sql in user_views:
        # Get column info for the view
        try:
            columns = con.execute(
                f"SELECT column_name, data_type FROM information_schema.columns "
                f"WHERE table_name='{view_name}' AND table_schema='main' "
                f"ORDER BY ordinal_position"
            ).fetchall()

            col_info = [
                {
                    "name": col_name,
                    "type": col_type,
                    "description": get_column_description(col_name),
                }
                for col_name, col_type in columns
            ]
        except Exception:
            col_info = []

        view_meta[view_name] = {
            "category": classify_view(view_name),
            "description": describe_view(view_name),
            "columns": col_info,
        }

    return view_meta, len(user_views)


def calculate_parquet_size() -> float:
    """Calculate total Parquet file size in MB."""
    total_bytes = sum(f.stat().st_size for f in TABLES_DIR.glob("*.parquet"))
    return total_bytes / 1024 / 1024


def generate_metadata(table_meta, view_meta, total_rows, total_views):
    """Generate the table_metadata.json file."""
    print("\n--- Generating Metadata ---")

    parquet_size = calculate_parquet_size()

    metadata = {
        "tables": table_meta,
        "views": view_meta,
        "stats": {
            "total_tables": len(table_meta),
            "total_views": total_views,
            "total_rows": total_rows,
            "parquet_size_mb": round(parquet_size, 2),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    with open(METADATA_JSON, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"  Wrote metadata to {METADATA_JSON}")
    return metadata


def main():
    print("=" * 60)
    print("  TKT-172: SQL Lab Data Pipeline")
    print("  Owner: Brock Purdy (Data Pipeline)")
    print("=" * 60)

    # Verify database exists
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    print(f"\nDatabase: {DB_PATH}")
    print(f"Output:   {OUTPUT_DIR}")

    # Create output directories
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Connect read-only
    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        # Export tables
        table_meta, total_rows = export_tables(con)

        # Export views
        view_meta, total_views = export_views(con)

        # Generate metadata
        metadata = generate_metadata(table_meta, view_meta, total_rows, total_views)

        # Summary
        parquet_size = metadata["stats"]["parquet_size_mb"]
        print("\n" + "=" * 60)
        print("  SUMMARY")
        print("=" * 60)
        print(f"  Tables exported:  {len(table_meta)}")
        print(f"  Views extracted:  {total_views}")
        print(f"  Total rows:       {total_rows:,}")
        print(f"  Parquet size:     {parquet_size:.2f} MB")
        print(f"  Output directory: {OUTPUT_DIR}")
        print("=" * 60)
        print("  Pipeline complete.")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        con.close()


if __name__ == "__main__":
    main()
