#!/usr/bin/env python3
"""
Cricket Playbook - Neon Sync Pipeline
=====================================
Syncs DuckDB tables to Neon Serverless Postgres.

Keeps DuckDB as the analytical engine while mirroring data to Neon
for browser-side queries (dashboard) and application features (bug reports).

Usage:
    python scripts/core/neon_sync.py                    # Sync all tables
    python scripts/core/neon_sync.py --tables dim_only  # Dimension tables only
    python scripts/core/neon_sync.py --dry-run           # Show what would sync

Owner: Brock Purdy (Data Pipeline)
"""

import io
import os
import sys
import time
from pathlib import Path

import duckdb
import psycopg2

from scripts.utils.logging_config import setup_logger

logger = setup_logger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
ENV_PATH = PROJECT_ROOT / ".env"

# Tables to sync, in dependency order
# Dimension tables first, then facts
SYNC_TABLE_NAMES = [
    "dim_tournament",
    "dim_team",
    "dim_venue",
    "dim_player",
    "dim_match",
    "dim_franchise_alias",
    "dim_bowler_classification",
    "fact_ball",
    "fact_player_match_performance",
]

DIM_TABLES = [t for t in SYNC_TABLE_NAMES if t.startswith("dim_")]

# Indexes to create after sync (table -> list of index SQL)
NEON_INDEXES = {
    "fact_ball": [
        "CREATE INDEX IF NOT EXISTS idx_fb_match ON fact_ball(match_id)",
        "CREATE INDEX IF NOT EXISTS idx_fb_batter ON fact_ball(batter_id)",
        "CREATE INDEX IF NOT EXISTS idx_fb_bowler ON fact_ball(bowler_id)",
        "CREATE INDEX IF NOT EXISTS idx_fb_phase ON fact_ball(match_phase)",
    ],
    "fact_player_match_performance": [
        "CREATE INDEX IF NOT EXISTS idx_fpmp_match ON fact_player_match_performance(match_id)",
        "CREATE INDEX IF NOT EXISTS idx_fpmp_player ON fact_player_match_performance(player_id)",
        "CREATE INDEX IF NOT EXISTS idx_fpmp_team ON fact_player_match_performance(team_id)",
    ],
}

# DuckDB type -> Postgres type mapping
DUCKDB_TO_PG_TYPE = {
    "VARCHAR": "TEXT",
    "BIGINT": "BIGINT",
    "INTEGER": "INTEGER",
    "SMALLINT": "SMALLINT",
    "DOUBLE": "DOUBLE PRECISION",
    "FLOAT": "REAL",
    "BOOLEAN": "BOOLEAN",
    "DATE": "DATE",
    "TIMESTAMP": "TIMESTAMP",
    "TIMESTAMP WITH TIME ZONE": "TIMESTAMPTZ",
    "HUGEINT": "NUMERIC",
}


def get_neon_url() -> str:
    """Get Neon connection URL from environment or .env file."""
    url = os.environ.get("NEON_DATABASE_URL")
    if url:
        return url

    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith("NEON_DATABASE_URL="):
                    return line.split("=", 1)[1]

    raise RuntimeError("NEON_DATABASE_URL not set. Add it to .env or export it.")


def get_pg_type(duckdb_type: str) -> str:
    """Map DuckDB column type to Postgres type."""
    duckdb_type = duckdb_type.upper()
    return DUCKDB_TO_PG_TYPE.get(duckdb_type, "TEXT")


def generate_ddl(duck_conn: duckdb.DuckDBPyConnection, table_name: str) -> str:
    """Auto-generate Postgres CREATE TABLE DDL from DuckDB schema."""
    cols = duck_conn.execute(
        f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}' AND table_schema = 'main'
        ORDER BY ordinal_position
        """
    ).fetchall()

    if not cols:
        raise ValueError(f"Table {table_name} not found in DuckDB")

    col_defs = []
    for col_name, col_type in cols:
        pg_type = get_pg_type(col_type)
        col_defs.append(f"    {col_name} {pg_type}")

    columns_sql = ",\n".join(col_defs)
    return f"CREATE TABLE IF NOT EXISTS {table_name} (\n{columns_sql}\n)"


def sync_table(
    duck_conn: duckdb.DuckDBPyConnection,
    pg_conn,
    table_name: str,
    dry_run: bool = False,
) -> dict:
    """Sync a single table from DuckDB to Neon."""
    start = time.time()

    # Get DuckDB row count
    try:
        duck_count = duck_conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    except Exception as e:
        logger.warning("Table %s not found in DuckDB: %s", table_name, e)
        return {"table": table_name, "status": "skipped", "reason": str(e)}

    if dry_run:
        logger.info("[DRY RUN] Would sync %s: %d rows", table_name, duck_count)
        return {"table": table_name, "status": "dry_run", "duck_rows": duck_count}

    pg_cur = pg_conn.cursor()

    # Drop and recreate (clean slate each sync)
    pg_cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    ddl = generate_ddl(duck_conn, table_name)
    pg_cur.execute(ddl)

    if duck_count == 0:
        logger.info("  %s: 0 rows (empty table)", table_name)
        pg_conn.commit()
        return {"table": table_name, "status": "ok", "rows": 0, "time_s": 0}

    # Export from DuckDB to CSV in memory, then COPY into Postgres
    duck_df = duck_conn.execute(f"SELECT * FROM {table_name}").fetchdf()

    # Use COPY for bulk load
    buffer = io.StringIO()
    duck_df.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)

    columns = list(duck_df.columns)
    copy_sql = f"COPY {table_name} ({', '.join(columns)}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
    pg_cur.copy_expert(copy_sql, buffer)

    # Create indexes if defined
    for idx_sql in NEON_INDEXES.get(table_name, []):
        pg_cur.execute(idx_sql)

    pg_conn.commit()

    # Verify row count
    pg_cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    pg_count = pg_cur.fetchone()[0]

    elapsed = time.time() - start
    status = "ok" if pg_count == duck_count else "mismatch"

    if status == "mismatch":
        logger.warning(
            "  %s: ROW MISMATCH - DuckDB=%d, Neon=%d (%.1fs)",
            table_name,
            duck_count,
            pg_count,
            elapsed,
        )
    else:
        logger.info(
            "  %s: %d rows synced (%.1fs)",
            table_name,
            pg_count,
            elapsed,
        )

    return {
        "table": table_name,
        "status": status,
        "duck_rows": duck_count,
        "neon_rows": pg_count,
        "time_s": round(elapsed, 1),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync DuckDB to Neon")
    parser.add_argument(
        "--tables",
        choices=["all", "dim_only"],
        default="all",
        help="Which tables to sync",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would sync without executing",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Cricket Playbook - Neon Sync")
    logger.info("=" * 60)

    # Connect to DuckDB
    if not DB_PATH.exists():
        logger.error("DuckDB not found at %s. Run ingest.py first.", DB_PATH)
        sys.exit(1)

    duck_conn = duckdb.connect(str(DB_PATH), read_only=True)
    logger.info(
        "DuckDB: %s (%.0f MB)",
        DB_PATH.name,
        DB_PATH.stat().st_size / 1024 / 1024,
    )

    # Connect to Neon
    neon_url = get_neon_url()
    pg_conn = psycopg2.connect(neon_url)
    logger.info("Neon: connected")

    # Determine which tables to sync
    if args.tables == "dim_only":
        tables = DIM_TABLES
        logger.info("Mode: dimension tables only (%d tables)", len(tables))
    else:
        tables = SYNC_TABLE_NAMES
        logger.info("Mode: full sync (%d tables)", len(tables))

    # Sync each table
    results = []
    total_start = time.time()

    for table_name in tables:
        result = sync_table(duck_conn, pg_conn, table_name, dry_run=args.dry_run)
        results.append(result)

    total_elapsed = time.time() - total_start

    # Summary
    logger.info("=" * 60)
    logger.info("SYNC COMPLETE (%.1fs)", total_elapsed)
    logger.info("=" * 60)

    ok = sum(1 for r in results if r["status"] == "ok")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    mismatched = sum(1 for r in results if r["status"] == "mismatch")
    total_rows = sum(r.get("neon_rows", 0) for r in results)

    logger.info("  Synced: %d tables, %d rows", ok, total_rows)
    if skipped:
        logger.warning("  Skipped: %d tables", skipped)
    if mismatched:
        logger.error("  Mismatched: %d tables", mismatched)

    duck_conn.close()
    pg_conn.close()

    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
