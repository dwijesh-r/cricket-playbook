#!/usr/bin/env python3
"""
TKT-092: CI/CD Artifact Comparison
Compares output artifacts between runs to detect drift and regressions.

Scans output directories for JSON artifacts, snapshots their metadata
(size, hash, schema, key counts), and compares against previous snapshots
to detect:
  1. Player count drift
  2. Statistical drift (>20% change in key metrics)
  3. Coverage checks (all 10 IPL teams represented)
  4. Schema validation (expected top-level keys present)

Author: Cricket Playbook ML Ops
Ticket: TKT-092
Sprint: 4.0 - Foundation & Editorial Excellence
"""

import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
SNAPSHOT_DIR = OUTPUT_DIR / "artifact_snapshots"

# Directories to scan for JSON artifacts
ARTIFACT_DIRS: List[Tuple[str, Path]] = [
    ("depth_charts", OUTPUT_DIR / "depth_charts"),
    ("player_profiles", OUTPUT_DIR / "player_profiles" / "by_team"),
    ("tags", OUTPUT_DIR / "tags"),
    ("stat_packs", OUTPUT_DIR / "stat_packs"),
]

# All 10 IPL 2026 team abbreviations
IPL_TEAMS = {"MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"}

# Size change threshold (fraction) — flag if file size changes by more than this
SIZE_DRIFT_THRESHOLD = 0.20

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class FileSnapshot:
    """Metadata snapshot for a single JSON artifact."""

    relative_path: str
    file_size: int
    md5_hash: str
    top_level_key_count: int
    top_level_keys: List[str]
    extracted_stats: Dict[str, Any]


@dataclass
class ComparisonReport:
    """Result of comparing two artifact snapshots."""

    timestamp: str
    files_compared: int
    files_added: List[str]
    files_removed: List[str]
    drift_warnings: List[str]
    coverage_ok: bool
    schema_ok: bool
    passed: bool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _md5_of_file(path: Path) -> str:
    """Compute the MD5 hex digest of a file."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_stats(data: Any, rel_path: str) -> Dict[str, Any]:
    """
    Extract key statistics from a parsed JSON artifact.

    Looks for common patterns across stat packs, depth charts,
    player profiles, and tag files.
    """
    stats: Dict[str, Any] = {}

    if not isinstance(data, dict):
        stats["root_type"] = type(data).__name__
        if isinstance(data, list):
            stats["item_count"] = len(data)
        return stats

    # Team identifier (various key names used across artifacts)
    for key in ("team", "team_abbr", "team_code"):
        if key in data:
            stats["team"] = str(data[key]).upper()
            break

    # Player count — direct key or length of players list/dict
    if "total_players" in data:
        stats["player_count"] = data["total_players"]
    elif "players" in data:
        players = data["players"]
        stats["player_count"] = len(players) if isinstance(players, (list, dict)) else 0
    elif "squad" in data:
        squad = data["squad"]
        stats["player_count"] = len(squad) if isinstance(squad, (list, dict)) else 0

    # Batter / bowler counts (tags files)
    if "batters" in data and isinstance(data["batters"], list):
        stats["batter_count"] = len(data["batters"])
    if "bowlers" in data and isinstance(data["bowlers"], list):
        stats["bowler_count"] = len(data["bowlers"])

    # Cluster info
    if "batter_clusters" in data:
        bc = data["batter_clusters"]
        stats["batter_cluster_count"] = len(bc) if isinstance(bc, (list, dict)) else 0
    if "bowler_clusters" in data:
        bc = data["bowler_clusters"]
        stats["bowler_cluster_count"] = len(bc) if isinstance(bc, (list, dict)) else 0

    # Depth chart positions
    if "positions" in data:
        pos = data["positions"]
        stats["position_count"] = len(pos) if isinstance(pos, (list, dict)) else 0

    # Overall rating (depth charts)
    if "overall_rating" in data:
        stats["overall_rating"] = data["overall_rating"]

    return stats


def _detect_team_in_path(rel_path: str) -> Optional[str]:
    """Attempt to infer team abbreviation from a file path."""
    upper = rel_path.upper()
    for team in IPL_TEAMS:
        if team in upper:
            return team
    return None


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def snapshot_artifacts(
    output_dir: Path = OUTPUT_DIR,
    snapshot_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Create a snapshot of current JSON artifacts across all output directories.

    For each JSON file found in the configured artifact directories, records:
    - file_size, md5_hash, top-level key count, extracted stats

    Args:
        output_dir: Root output directory (default: ``outputs/``).
        snapshot_path: Where to write the snapshot JSON.  If ``None``,
            auto-generates a timestamped path inside ``artifact_snapshots/``.

    Returns:
        The snapshot dict that was written to disk.
    """
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    files: Dict[str, Dict[str, Any]] = {}
    teams_found: set = set()

    for label, dir_path in ARTIFACT_DIRS:
        if not dir_path.exists():
            print(f"  [WARN] Directory not found, skipping: {dir_path.relative_to(PROJECT_DIR)}")
            continue

        json_files = sorted(dir_path.glob("*.json"))
        if not json_files:
            print(f"  [WARN] No JSON files in: {dir_path.relative_to(PROJECT_DIR)}")
            continue

        for jf in json_files:
            rel = str(jf.relative_to(PROJECT_DIR))
            md5 = _md5_of_file(jf)
            size = jf.stat().st_size

            try:
                with open(jf, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                print(f"  [WARN] Could not parse {rel}: {exc}")
                files[rel] = {
                    "relative_path": rel,
                    "file_size": size,
                    "md5_hash": md5,
                    "top_level_key_count": 0,
                    "top_level_keys": [],
                    "extracted_stats": {"parse_error": str(exc)},
                }
                continue

            if isinstance(data, dict):
                top_keys = sorted(data.keys())
                top_key_count = len(top_keys)
            else:
                top_keys = []
                top_key_count = 0

            extracted = _extract_stats(data, rel)

            # Track team coverage
            team = extracted.get("team") or _detect_team_in_path(rel)
            if team and team in IPL_TEAMS:
                teams_found.add(team)

            files[rel] = {
                "relative_path": rel,
                "file_size": size,
                "md5_hash": md5,
                "top_level_key_count": top_key_count,
                "top_level_keys": top_keys,
                "extracted_stats": extracted,
            }

    snapshot = {
        "timestamp": now.isoformat(),
        "timestamp_label": timestamp,
        "project_dir": str(PROJECT_DIR),
        "files_count": len(files),
        "teams_found": sorted(teams_found),
        "teams_missing": sorted(IPL_TEAMS - teams_found),
        "files": files,
    }

    # Write snapshot to disk
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    if snapshot_path is None:
        snapshot_path = SNAPSHOT_DIR / f"snapshot_{timestamp}.json"

    with open(snapshot_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)

    print(f"  Snapshot saved: {snapshot_path.relative_to(PROJECT_DIR)}")
    return snapshot


def _find_latest_snapshot(exclude: Optional[Path] = None) -> Optional[Path]:
    """Return the most recent snapshot file, excluding *exclude* if given."""
    if not SNAPSHOT_DIR.exists():
        return None
    candidates = sorted(SNAPSHOT_DIR.glob("snapshot_*.json"))
    for c in reversed(candidates):
        if exclude and c.resolve() == exclude.resolve():
            continue
        return c
    return None


def compare_snapshots(
    current: Dict[str, Any],
    previous: Dict[str, Any],
) -> ComparisonReport:
    """
    Compare two artifact snapshots and produce a ComparisonReport.

    Checks performed:
    - File additions / removals
    - Size changes > 20%
    - Schema changes (missing / new top-level keys)
    - Player count drifts
    - Team coverage (all 10 IPL teams)

    Args:
        current: The newer snapshot dict.
        previous: The older snapshot dict.

    Returns:
        A populated ``ComparisonReport``.
    """
    cur_files = current.get("files", {})
    prev_files = previous.get("files", {})

    cur_keys = set(cur_files.keys())
    prev_keys = set(prev_files.keys())

    files_added = sorted(cur_keys - prev_keys)
    files_removed = sorted(prev_keys - cur_keys)
    common_files = sorted(cur_keys & prev_keys)

    drift_warnings: List[str] = []
    schema_issues: List[str] = []

    # --- file additions / removals ---
    if files_added:
        drift_warnings.append(f"Files added ({len(files_added)}): {', '.join(files_added)}")
    if files_removed:
        drift_warnings.append(f"Files removed ({len(files_removed)}): {', '.join(files_removed)}")

    # --- per-file comparison ---
    for rel in common_files:
        cur = cur_files[rel]
        prev = prev_files[rel]

        # Size drift
        prev_size = prev.get("file_size", 0)
        cur_size = cur.get("file_size", 0)
        if prev_size > 0:
            size_change = abs(cur_size - prev_size) / prev_size
            if size_change > SIZE_DRIFT_THRESHOLD:
                direction = "increased" if cur_size > prev_size else "decreased"
                drift_warnings.append(
                    f"Size drift in {rel}: {direction} by {size_change:.0%} "
                    f"({prev_size} -> {cur_size} bytes)"
                )

        # Schema changes (top-level keys)
        prev_tl = set(prev.get("top_level_keys", []))
        cur_tl = set(cur.get("top_level_keys", []))
        missing_keys = prev_tl - cur_tl
        new_keys = cur_tl - prev_tl
        if missing_keys:
            schema_issues.append(f"Missing keys in {rel}: {sorted(missing_keys)}")
        if new_keys:
            # New keys are informational, not necessarily issues
            drift_warnings.append(f"New keys in {rel}: {sorted(new_keys)}")

        # Player count drift
        prev_stats = prev.get("extracted_stats", {})
        cur_stats = cur.get("extracted_stats", {})

        for count_key in ("player_count", "batter_count", "bowler_count"):
            prev_val = prev_stats.get(count_key)
            cur_val = cur_stats.get(count_key)
            if prev_val is not None and cur_val is not None:
                if prev_val > 0:
                    pct_change = abs(cur_val - prev_val) / prev_val
                    if pct_change > SIZE_DRIFT_THRESHOLD:
                        drift_warnings.append(
                            f"{count_key} drift in {rel}: "
                            f"{prev_val} -> {cur_val} ({pct_change:+.0%})"
                        )
                elif cur_val != prev_val:
                    drift_warnings.append(f"{count_key} changed in {rel}: {prev_val} -> {cur_val}")

        # Statistical drift — numeric extracted stats
        for stat_key in (
            "overall_rating",
            "position_count",
            "batter_cluster_count",
            "bowler_cluster_count",
        ):
            prev_val = prev_stats.get(stat_key)
            cur_val = cur_stats.get(stat_key)
            if (
                prev_val is not None
                and cur_val is not None
                and isinstance(prev_val, (int, float))
                and isinstance(cur_val, (int, float))
            ):
                if prev_val != 0:
                    pct_change = abs(cur_val - prev_val) / abs(prev_val)
                    if pct_change > SIZE_DRIFT_THRESHOLD:
                        drift_warnings.append(
                            f"{stat_key} drift in {rel}: "
                            f"{prev_val} -> {cur_val} ({pct_change:+.0%})"
                        )

    # Add schema issues to drift warnings
    drift_warnings.extend(schema_issues)

    # Coverage check
    teams_found = set(current.get("teams_found", []))
    coverage_ok = IPL_TEAMS.issubset(teams_found)
    if not coverage_ok:
        missing = sorted(IPL_TEAMS - teams_found)
        drift_warnings.append(f"Team coverage gap: missing {missing}")

    # Schema check — any missing keys is a schema failure
    schema_ok = len(schema_issues) == 0

    # Overall pass/fail — passes if no critical issues
    # Critical issues: files removed, schema issues, coverage gap
    has_critical = bool(files_removed) or not schema_ok or not coverage_ok
    passed = not has_critical

    return ComparisonReport(
        timestamp=current.get("timestamp", datetime.now().isoformat()),
        files_compared=len(common_files),
        files_added=files_added,
        files_removed=files_removed,
        drift_warnings=drift_warnings,
        coverage_ok=coverage_ok,
        schema_ok=schema_ok,
        passed=passed,
    )


def print_report(report: ComparisonReport) -> None:
    """Print a formatted comparison report to stdout."""
    print("\n" + "=" * 72)
    print("ARTIFACT COMPARISON REPORT")
    print("=" * 72)
    print(f"  Timestamp      : {report.timestamp}")
    print(f"  Files compared : {report.files_compared}")
    print(f"  Files added    : {len(report.files_added)}")
    print(f"  Files removed  : {len(report.files_removed)}")
    print(f"  Coverage OK    : {report.coverage_ok}")
    print(f"  Schema OK      : {report.schema_ok}")

    if report.drift_warnings:
        print("\n" + "-" * 72)
        print(f"DRIFT WARNINGS ({len(report.drift_warnings)})")
        print("-" * 72)
        for i, w in enumerate(report.drift_warnings, 1):
            print(f"  {i}. {w}")

    print("\n" + "-" * 72)
    status = "PASSED" if report.passed else "FAILED"
    print(f"RESULT: {status}")
    print("-" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """
    Entry point.

    1. Snapshot current artifacts.
    2. If a previous snapshot exists, compare and report.
    3. Return 0 if passed (or first run), 1 if issues detected.
    """
    print("=" * 72)
    print("TKT-092: CI/CD Artifact Comparison")
    print("=" * 72)

    # --- Step 1: Snapshot current state ---
    print("\n[1/3] Creating artifact snapshot ...")
    snapshot = snapshot_artifacts()
    print(f"       Files captured: {snapshot['files_count']}")
    print(f"       Teams found  : {', '.join(snapshot['teams_found']) or '(none)'}")
    if snapshot["teams_missing"]:
        print(f"       Teams missing : {', '.join(snapshot['teams_missing'])}")

    # --- Step 2: Find previous snapshot ---
    current_path = SNAPSHOT_DIR / f"snapshot_{snapshot['timestamp_label']}.json"
    previous_path = _find_latest_snapshot(exclude=current_path)

    if previous_path is None:
        print("\n[2/3] No previous snapshot found — first run, nothing to compare.")
        print("\n[3/3] Snapshot stored for future comparisons.")

        # Still check coverage on first run
        teams_found = set(snapshot.get("teams_found", []))
        coverage_ok = IPL_TEAMS.issubset(teams_found)
        if not coverage_ok:
            missing = sorted(IPL_TEAMS - teams_found)
            print(f"\n  [WARN] Team coverage gap on first run: missing {missing}")

        print("\n" + "=" * 72)
        print("RESULT: PASSED (first run — baseline snapshot created)")
        print("=" * 72)
        return 0

    # --- Step 3: Compare ---
    print(f"\n[2/3] Loading previous snapshot: {previous_path.name}")
    with open(previous_path, "r", encoding="utf-8") as fh:
        previous = json.load(fh)

    print(f"       Previous timestamp: {previous.get('timestamp', 'unknown')}")
    print(f"       Previous files    : {previous.get('files_count', '?')}")

    print("\n[3/3] Comparing snapshots ...")
    report = compare_snapshots(snapshot, previous)

    # Print formatted report
    print_report(report)

    # Save comparison report alongside snapshot
    report_path = SNAPSHOT_DIR / f"comparison_{snapshot['timestamp_label']}.json"
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(asdict(report), fh, indent=2)
    print(f"\n  Comparison report saved: {report_path.relative_to(PROJECT_DIR)}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
