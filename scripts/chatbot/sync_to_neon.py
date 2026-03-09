#!/usr/bin/env python3
"""
Sync chatbot analytics tables from DuckDB to Neon.
Only syncs the 11 small analytics tables Richmond needs (~44K rows).

Usage:
    python scripts/chatbot/sync_to_neon.py
"""

import io
import os
import time
from pathlib import Path

import duckdb
import psycopg2

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
ENV_PATH = PROJECT_ROOT / ".env"

TABLES = [
    "analytics_ipl_batting_career",
    "analytics_ipl_bowling_career",
    "analytics_ipl_batter_phase",
    "analytics_ipl_bowler_phase",
    "analytics_ipl_batter_vs_bowler",
    "analytics_ipl_batter_vs_bowler_type",
    "analytics_ipl_batter_vs_team",
    "analytics_ipl_bowler_vs_team",
    "analytics_ipl_squad_batting",
    "analytics_ipl_squad_bowling",
    "ipl_2026_squads",
]

DUCKDB_TO_PG = {
    "VARCHAR": "TEXT",
    "BIGINT": "BIGINT",
    "INTEGER": "INTEGER",
    "SMALLINT": "SMALLINT",
    "DOUBLE": "DOUBLE PRECISION",
    "FLOAT": "REAL",
    "BOOLEAN": "BOOLEAN",
    "DATE": "DATE",
    "HUGEINT": "NUMERIC",
}


def get_env(key):
    val = os.environ.get(key)
    if val:
        return val
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1]
    raise RuntimeError(f"{key} not set")


def sync():
    duck = duckdb.connect(str(DB_PATH), read_only=True)
    pg = psycopg2.connect(get_env("NEON_DATABASE_URL"))
    cur = pg.cursor()

    total_rows = 0
    start = time.time()

    for table in TABLES:
        t0 = time.time()

        # Get schema from DuckDB
        cols = duck.execute(
            f"SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_name = '{table}' AND table_schema = 'main' "
            f"ORDER BY ordinal_position"
        ).fetchall()

        col_defs = []
        for name, dtype in cols:
            pg_type = DUCKDB_TO_PG.get(dtype.upper(), "TEXT")
            col_defs.append(f"{name} {pg_type}")

        # Drop and recreate
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        cur.execute(f"CREATE TABLE {table} ({', '.join(col_defs)})")

        # Export data via CSV
        df = duck.execute(f"SELECT * FROM {table}").fetchdf()
        buf = io.StringIO()
        df.to_csv(buf, index=False, header=False, na_rep="\\N")
        buf.seek(0)

        columns = list(df.columns)
        copy_sql = f"COPY {table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
        cur.copy_expert(copy_sql, buf)
        pg.commit()

        # Verify
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        total_rows += count
        print(f"  {table}: {count} rows ({time.time() - t0:.1f}s)")

    elapsed = time.time() - start
    print(f"\nDone: {len(TABLES)} tables, {total_rows} rows in {elapsed:.1f}s")

    duck.close()
    pg.close()


if __name__ == "__main__":
    sync()
