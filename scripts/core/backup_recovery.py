"""
Cricket Playbook - Backup & Recovery Module (TKT-146)
=====================================================
Owner: Ime Udoka (MLOps & Infrastructure Lead)
Epic: EPIC-014 (Foundation Fortification)

Provides automated backup of DuckDB database with:
- Timestamped backups with rotation (keep last N)
- Integrity verification via row count checksums
- Recovery from backup with validation
- Point-in-time backup selection

Usage:
    python scripts/core/backup_recovery.py backup
    python scripts/core/backup_recovery.py verify
    python scripts/core/backup_recovery.py restore --timestamp 2026-02-08T14:30:00
    python scripts/core/backup_recovery.py list
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

import duckdb

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
BACKUP_DIR = PROJECT_ROOT / "data" / "backups"
BACKUP_MANIFEST = BACKUP_DIR / "backup_manifest.json"
MAX_BACKUPS = 5  # Keep last N backups


def get_db_integrity_info(db_path: Path) -> dict:
    """Get row counts and table info for integrity verification."""
    if not db_path.exists():
        return {"exists": False, "tables": {}}

    conn = duckdb.connect(str(db_path), read_only=True)
    tables = {}
    try:
        table_list = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
        for (table_name,) in table_list:
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            tables[table_name] = count
    finally:
        conn.close()

    return {
        "exists": True,
        "size_mb": round(db_path.stat().st_size / 1024 / 1024, 2),
        "tables": tables,
        "total_rows": sum(tables.values()),
    }


def create_backup(reason: str = "manual") -> dict:
    """Create a timestamped backup of the DuckDB file.

    Args:
        reason: Why the backup was created (manual, pre-ingest, scheduled)

    Returns:
        Backup metadata dict
    """
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return {"success": False, "error": "Database not found"}

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now()
    ts_str = timestamp.strftime("%Y%m%d_%H%M%S")
    backup_filename = f"cricket_playbook_{ts_str}.duckdb"
    backup_path = BACKUP_DIR / backup_filename

    # Verify source integrity before backup
    print("Verifying source database integrity...")
    source_info = get_db_integrity_info(DB_PATH)
    if not source_info["exists"]:
        return {"success": False, "error": "Source database verification failed"}

    print(f"  Source: {source_info['size_mb']} MB, {source_info['total_rows']} total rows")

    # Copy database
    print(f"Creating backup: {backup_filename}")
    shutil.copy2(DB_PATH, backup_path)

    # Verify backup integrity
    print("Verifying backup integrity...")
    backup_info = get_db_integrity_info(backup_path)
    if backup_info["total_rows"] != source_info["total_rows"]:
        print("WARNING: Backup row count mismatch!")
        backup_path.unlink()
        return {"success": False, "error": "Integrity check failed"}

    print(f"  Backup verified: {backup_info['total_rows']} rows match")

    # Update manifest
    metadata = {
        "filename": backup_filename,
        "timestamp": timestamp.isoformat(),
        "reason": reason,
        "size_mb": backup_info["size_mb"],
        "total_rows": backup_info["total_rows"],
        "tables": backup_info["tables"],
    }

    manifest = _load_manifest()
    manifest["backups"].append(metadata)
    manifest["last_backup"] = timestamp.isoformat()

    # Rotate old backups
    if len(manifest["backups"]) > MAX_BACKUPS:
        old_backups = manifest["backups"][:-MAX_BACKUPS]
        manifest["backups"] = manifest["backups"][-MAX_BACKUPS:]
        for old in old_backups:
            old_path = BACKUP_DIR / old["filename"]
            if old_path.exists():
                old_path.unlink()
                print(f"  Rotated old backup: {old['filename']}")

    _save_manifest(manifest)
    print(f"Backup complete: {backup_filename}")

    return {"success": True, **metadata}


def restore_backup(timestamp: str | None = None) -> dict:
    """Restore database from a backup.

    Args:
        timestamp: ISO timestamp to restore from. If None, uses latest backup.

    Returns:
        Restore result dict
    """
    manifest = _load_manifest()
    if not manifest["backups"]:
        print("ERROR: No backups available")
        return {"success": False, "error": "No backups found"}

    if timestamp:
        # Find backup closest to requested timestamp
        backup = None
        for b in manifest["backups"]:
            if b["timestamp"].startswith(timestamp[:19]):
                backup = b
                break
        if not backup:
            print(f"ERROR: No backup found for timestamp {timestamp}")
            print("Available backups:")
            for b in manifest["backups"]:
                print(f"  - {b['timestamp']} ({b['filename']})")
            return {"success": False, "error": "Backup not found"}
    else:
        backup = manifest["backups"][-1]

    backup_path = BACKUP_DIR / backup["filename"]
    if not backup_path.exists():
        print(f"ERROR: Backup file missing: {backup['filename']}")
        return {"success": False, "error": "Backup file missing"}

    # Verify backup integrity before restore
    print(f"Restoring from: {backup['filename']}")
    backup_info = get_db_integrity_info(backup_path)
    print(f"  Backup: {backup_info['size_mb']} MB, {backup_info['total_rows']} rows")

    # Create safety backup of current DB before restore
    if DB_PATH.exists():
        safety_path = DB_PATH.with_suffix(".duckdb.pre_restore")
        shutil.copy2(DB_PATH, safety_path)
        print(f"  Safety backup saved: {safety_path.name}")

    # Restore
    shutil.copy2(backup_path, DB_PATH)

    # Verify restore
    restored_info = get_db_integrity_info(DB_PATH)
    if restored_info["total_rows"] != backup_info["total_rows"]:
        print("WARNING: Restore integrity check failed!")
        return {"success": False, "error": "Restore verification failed"}

    print(f"Restore complete: {restored_info['total_rows']} rows verified")
    return {"success": True, "restored_from": backup["filename"]}


def verify_database() -> dict:
    """Verify current database integrity."""
    print("Verifying database integrity...")
    info = get_db_integrity_info(DB_PATH)

    if not info["exists"]:
        print("ERROR: Database not found")
        return {"healthy": False, "error": "Database not found"}

    print(f"  Size: {info['size_mb']} MB")
    print(f"  Tables: {len(info['tables'])}")
    print(f"  Total rows: {info['total_rows']}")

    for table, count in sorted(info["tables"].items()):
        status = "OK" if count > 0 else "EMPTY"
        print(f"    {table}: {count:,} rows [{status}]")

    empty_tables = [t for t, c in info["tables"].items() if c == 0]
    healthy = len(empty_tables) == 0 and len(info["tables"]) >= 5

    print(f"\n  Health: {'HEALTHY' if healthy else 'ISSUES FOUND'}")
    return {"healthy": healthy, **info}


def list_backups() -> list[dict]:
    """List all available backups."""
    manifest = _load_manifest()
    backups = manifest.get("backups", [])

    if not backups:
        print("No backups found.")
        return []

    print(f"Available backups ({len(backups)}):")
    for i, b in enumerate(backups):
        age = datetime.now() - datetime.fromisoformat(b["timestamp"])
        print(
            f"  [{i + 1}] {b['timestamp']} | {b['size_mb']} MB | "
            f"{b['total_rows']:,} rows | {b['reason']} | {age.days}d ago"
        )

    return backups


def _load_manifest() -> dict:
    """Load backup manifest."""
    if BACKUP_MANIFEST.exists():
        with open(BACKUP_MANIFEST) as f:
            return json.load(f)
    return {"backups": [], "last_backup": None}


def _save_manifest(manifest: dict) -> None:
    """Save backup manifest."""
    BACKUP_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(BACKUP_MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cricket Playbook - Backup & Recovery")
    parser.add_argument(
        "action",
        choices=["backup", "restore", "verify", "list"],
        help="Action to perform",
    )
    parser.add_argument("--timestamp", help="Timestamp for restore (ISO format)")
    parser.add_argument("--reason", default="manual", help="Reason for backup (default: manual)")
    args = parser.parse_args()

    if args.action == "backup":
        create_backup(reason=args.reason)
    elif args.action == "restore":
        restore_backup(timestamp=args.timestamp)
    elif args.action == "verify":
        verify_database()
    elif args.action == "list":
        list_backups()
