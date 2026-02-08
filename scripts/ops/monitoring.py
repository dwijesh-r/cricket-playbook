#!/usr/bin/env python3
"""
Cricket Playbook - Production Monitoring & Alerting
====================================================
Unified observability layer with structured logging, health endpoints,
and alert thresholds for the Cricket Playbook data analytics platform.

Owner: Jose Mourinho (Tech Strategy)
Ticket: TKT-157
EPIC: EPIC-015 (Operational Maturity)

Features:
    - Structured JSON logging with component tagging
    - Aggregated health checks (DB, rows, model freshness, outputs, disk)
    - Two-tier alert thresholds (WARNING / CRITICAL)
    - Alert persistence to outputs/monitoring/alerts.json
    - CLI interface: --check, --alerts, --json

Usage:
    python scripts/ops/monitoring.py --check            # run all health checks
    python scripts/ops/monitoring.py --alerts           # show active alerts
    python scripts/ops/monitoring.py --check --json     # machine-readable output
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "cricket_playbook.duckdb"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MONITORING_DIR = OUTPUTS_DIR / "monitoring"
ALERTS_FILE = MONITORING_DIR / "alerts.json"

# Row-count minimums imported from ge_validation.py definitions.
# Kept in sync manually to avoid importing GE at runtime.
ROW_MINIMUMS: Dict[str, int] = {
    "fact_ball": 100_000,
    "dim_player": 1_000,
    "dim_match": 500,
    "dim_team": 10,
    "dim_venue": 10,
}

# ---------------------------------------------------------------------------
# Alert severity
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    """Two-tier alert severity matching operational run-book conventions."""

    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Structured logging
# ---------------------------------------------------------------------------


class StructuredLogger:
    """Emit JSON-formatted log entries to stderr.

    Each entry contains:
        timestamp  - ISO-8601 UTC
        level      - DEBUG / INFO / WARNING / ERROR / CRITICAL
        component  - logical subsystem (e.g. "health_check", "alert_engine")
        message    - human-readable description
        metrics    - optional dict of numeric / string KPIs
    """

    def __init__(self, component: str, level: int = logging.INFO) -> None:
        self._component = component
        self._logger = logging.getLogger(f"monitoring.{component}")
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
        self._logger.setLevel(level)
        self._logger.propagate = False

    def _emit(
        self,
        level: str,
        message: str,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "component": self._component,
            "message": message,
        }
        if metrics:
            entry["metrics"] = metrics
        log_fn = getattr(self._logger, level.lower(), self._logger.info)
        log_fn(json.dumps(entry, default=str))
        return entry

    def info(self, message: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._emit("INFO", message, metrics)

    def warning(self, message: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._emit("WARNING", message, metrics)

    def error(self, message: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._emit("ERROR", message, metrics)

    def critical(self, message: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._emit("CRITICAL", message, metrics)

    def debug(self, message: str, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._emit("DEBUG", message, metrics)


# ---------------------------------------------------------------------------
# Alert dataclass-like container (stdlib only)
# ---------------------------------------------------------------------------


class Alert:
    """Immutable representation of a monitoring alert."""

    __slots__ = ("severity", "component", "message", "timestamp")

    def __init__(
        self,
        severity: Severity,
        component: str,
        message: str,
        timestamp: Optional[str] = None,
    ) -> None:
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "component", component)
        object.__setattr__(self, "message", message)
        object.__setattr__(
            self,
            "timestamp",
            timestamp or datetime.now(timezone.utc).isoformat(),
        )

    def __setattr__(self, _name: str, _value: Any) -> None:
        raise AttributeError("Alert instances are immutable")

    def to_dict(self) -> Dict[str, str]:
        return {
            "severity": self.severity.value,
            "component": self.component,
            "message": self.message,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Individual health checks
# ---------------------------------------------------------------------------

log = StructuredLogger("health_check")


def check_db_connectivity() -> Dict[str, Any]:
    """Verify the DuckDB database file exists and is readable.

    Returns a dict with keys: name, status, ok, detail, alerts.
    """
    alerts: List[Alert] = []
    if not DB_PATH.exists():
        alerts.append(Alert(Severity.CRITICAL, "database", f"Database not found at {DB_PATH}"))
        return {
            "name": "database_connectivity",
            "status": "CRITICAL",
            "ok": False,
            "detail": f"Database file missing: {DB_PATH}",
            "alerts": alerts,
        }

    try:
        import duckdb

        con = duckdb.connect(str(DB_PATH), read_only=True)
        tables = con.execute("SHOW TABLES").fetchdf()["name"].tolist()
        con.close()
        return {
            "name": "database_connectivity",
            "status": "OK",
            "ok": True,
            "detail": f"DuckDB readable, {len(tables)} tables found",
            "tables": tables,
            "alerts": alerts,
        }
    except Exception as exc:
        alerts.append(Alert(Severity.CRITICAL, "database", f"DB unreachable: {exc}"))
        return {
            "name": "database_connectivity",
            "status": "CRITICAL",
            "ok": False,
            "detail": str(exc),
            "alerts": alerts,
        }


def check_row_counts() -> Dict[str, Any]:
    """Verify each table has at least the minimum expected rows.

    Minimum thresholds are sourced from ge_validation.py ROW_MINIMUMS.
    """
    alerts: List[Alert] = []
    table_counts: Dict[str, int] = {}
    below_minimum: List[str] = []

    if not DB_PATH.exists():
        return {
            "name": "row_counts",
            "status": "SKIP",
            "ok": False,
            "detail": "Database not found, skipping row count check",
            "alerts": [],
        }

    try:
        import duckdb

        con = duckdb.connect(str(DB_PATH), read_only=True)
        available = con.execute("SHOW TABLES").fetchdf()["name"].tolist()

        for table, minimum in ROW_MINIMUMS.items():
            if table not in available:
                continue
            count = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # noqa: S608
            table_counts[table] = count
            if count < minimum:
                below_minimum.append(table)
                alerts.append(
                    Alert(
                        Severity.WARNING,
                        "row_counts",
                        f"{table}: {count:,} rows below minimum {minimum:,}",
                    )
                )
        con.close()
    except Exception as exc:
        return {
            "name": "row_counts",
            "status": "ERROR",
            "ok": False,
            "detail": str(exc),
            "alerts": alerts,
        }

    ok = len(below_minimum) == 0
    return {
        "name": "row_counts",
        "status": "OK" if ok else "WARNING",
        "ok": ok,
        "detail": f"{len(table_counts)} tables checked, {len(below_minimum)} below minimum",
        "table_counts": table_counts,
        "below_minimum": below_minimum,
        "alerts": alerts,
    }


def check_model_freshness(max_age_days: int = 30) -> Dict[str, Any]:
    """Check when clustering models were last produced.

    Scans outputs/monitoring/ and outputs/metrics/ for model artefacts.
    If the newest artefact is older than *max_age_days*, emit a WARNING.
    """
    alerts: List[Alert] = []

    newest_mtime: Optional[float] = None
    newest_path: Optional[Path] = None

    # Check clustering CSV files at outputs root
    for csv_file in OUTPUTS_DIR.glob("player_clustering*.csv"):
        mtime = csv_file.stat().st_mtime
        if newest_mtime is None or mtime > newest_mtime:
            newest_mtime = mtime
            newest_path = csv_file

    # Check model artefacts in monitoring/health_reports
    health_reports_dir = MONITORING_DIR / "health_reports"
    if health_reports_dir.exists():
        for report in health_reports_dir.glob("*.json"):
            mtime = report.stat().st_mtime
            if newest_mtime is None or mtime > newest_mtime:
                newest_mtime = mtime
                newest_path = report

    # Check metrics directory
    metrics_dir = OUTPUTS_DIR / "metrics"
    if metrics_dir.exists():
        for artefact in metrics_dir.glob("*"):
            if artefact.is_file():
                mtime = artefact.stat().st_mtime
                if newest_mtime is None or mtime > newest_mtime:
                    newest_mtime = mtime
                    newest_path = artefact

    if newest_mtime is None:
        alerts.append(
            Alert(
                Severity.WARNING,
                "model_freshness",
                "No model artefacts found -- clustering may never have run",
            )
        )
        return {
            "name": "model_freshness",
            "status": "WARNING",
            "ok": False,
            "detail": "No model artefacts found",
            "alerts": alerts,
        }

    last_modified = datetime.fromtimestamp(newest_mtime, tz=timezone.utc)
    age_days = (datetime.now(timezone.utc) - last_modified).days

    if age_days > max_age_days:
        alerts.append(
            Alert(
                Severity.WARNING,
                "model_freshness",
                f"Model artefacts are {age_days} days old (threshold: {max_age_days}d)",
            )
        )

    ok = age_days <= max_age_days
    return {
        "name": "model_freshness",
        "status": "OK" if ok else "WARNING",
        "ok": ok,
        "detail": f"Newest artefact: {newest_path.name if newest_path else 'N/A'}, age {age_days}d",
        "age_days": age_days,
        "max_age_days": max_age_days,
        "newest_artefact": str(newest_path) if newest_path else None,
        "alerts": alerts,
    }


def check_output_freshness(max_age_days: int = 7) -> Dict[str, Any]:
    """Check when stat-pack outputs were last generated.

    Scans outputs/stat_packs/ and outputs/depth_charts/ for recent files.
    """
    alerts: List[Alert] = []
    output_dirs = [
        OUTPUTS_DIR / "stat_packs",
        OUTPUTS_DIR / "depth_charts",
        OUTPUTS_DIR / "matchups",
    ]

    newest_mtime: Optional[float] = None
    newest_path: Optional[Path] = None

    for output_dir in output_dirs:
        if not output_dir.exists():
            continue
        for item in output_dir.rglob("*"):
            if item.is_file():
                mtime = item.stat().st_mtime
                if newest_mtime is None or mtime > newest_mtime:
                    newest_mtime = mtime
                    newest_path = item

    if newest_mtime is None:
        alerts.append(
            Alert(
                Severity.WARNING,
                "output_freshness",
                "No stat-pack outputs found",
            )
        )
        return {
            "name": "output_freshness",
            "status": "WARNING",
            "ok": False,
            "detail": "No output files found in stat_packs/depth_charts/matchups",
            "alerts": alerts,
        }

    last_modified = datetime.fromtimestamp(newest_mtime, tz=timezone.utc)
    age_days = (datetime.now(timezone.utc) - last_modified).days

    if age_days > max_age_days:
        alerts.append(
            Alert(
                Severity.WARNING,
                "output_freshness",
                f"Outputs are {age_days} days old (threshold: {max_age_days}d)",
            )
        )

    ok = age_days <= max_age_days
    return {
        "name": "output_freshness",
        "status": "OK" if ok else "WARNING",
        "ok": ok,
        "detail": f"Newest output: {newest_path.name if newest_path else 'N/A'}, age {age_days}d",
        "age_days": age_days,
        "max_age_days": max_age_days,
        "newest_output": str(newest_path) if newest_path else None,
        "alerts": alerts,
    }


def check_disk_space(threshold_gb: float = 5.0) -> Dict[str, Any]:
    """Check that the data/ directory is not consuming excessive disk space.

    Args:
        threshold_gb: Maximum acceptable size of data/ in gigabytes.
    """
    alerts: List[Alert] = []

    if not DATA_DIR.exists():
        return {
            "name": "disk_space",
            "status": "OK",
            "ok": True,
            "detail": "data/ directory does not exist yet",
            "alerts": alerts,
        }

    total_bytes = sum(f.stat().st_size for f in DATA_DIR.rglob("*") if f.is_file())
    size_gb = total_bytes / (1024**3)

    if size_gb > threshold_gb:
        alerts.append(
            Alert(
                Severity.WARNING,
                "disk_space",
                f"data/ directory is {size_gb:.2f} GB (threshold: {threshold_gb} GB)",
            )
        )

    ok = size_gb <= threshold_gb
    return {
        "name": "disk_space",
        "status": "OK" if ok else "WARNING",
        "ok": ok,
        "detail": f"data/ directory size: {size_gb:.2f} GB (limit {threshold_gb} GB)",
        "size_gb": round(size_gb, 2),
        "threshold_gb": threshold_gb,
        "alerts": alerts,
    }


def check_health_score() -> Dict[str, Any]:
    """Run the system_health_score calculator and evaluate the result.

    Thresholds:
        - score < 50 -> CRITICAL
        - score < 70 -> WARNING
        - score >= 70 -> OK
    """
    alerts: List[Alert] = []
    score: Optional[float] = None

    try:
        from scripts.ml_ops.system_health_score import calculate_health_score

        report = calculate_health_score()
        score = report.get("score")
    except Exception as exc:
        # If the health scorer is unavailable, degrade gracefully.
        return {
            "name": "health_score",
            "status": "SKIP",
            "ok": True,
            "detail": f"Could not run health score calculator: {exc}",
            "alerts": alerts,
        }

    if score is None:
        return {
            "name": "health_score",
            "status": "SKIP",
            "ok": True,
            "detail": "Health score returned None",
            "alerts": alerts,
        }

    if score < 50:
        alerts.append(
            Alert(
                Severity.CRITICAL,
                "health_score",
                f"System health score is {score}/100 (CRITICAL threshold: 50)",
            )
        )
        status = "CRITICAL"
    elif score < 70:
        alerts.append(
            Alert(
                Severity.WARNING,
                "health_score",
                f"System health score is {score}/100 (WARNING threshold: 70)",
            )
        )
        status = "WARNING"
    else:
        status = "OK"

    ok = score >= 70
    return {
        "name": "health_score",
        "status": status,
        "ok": ok,
        "detail": f"System health score: {score}/100",
        "score": score,
        "alerts": alerts,
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def run_all_checks() -> Dict[str, Any]:
    """Execute every health check and return an aggregate report.

    Returns a dict with:
        timestamp, overall_status, checks (list), alerts (list)
    """
    log.info("Starting health check sweep")
    checks: List[Dict[str, Any]] = []
    all_alerts: List[Alert] = []

    for check_fn in [
        check_db_connectivity,
        check_row_counts,
        check_model_freshness,
        check_output_freshness,
        check_disk_space,
        check_health_score,
    ]:
        result = check_fn()
        checks.append(result)
        all_alerts.extend(result.get("alerts", []))
        log.info(
            f"Check [{result['name']}]: {result['status']}",
            metrics={"check": result["name"], "status": result["status"]},
        )

    # Determine overall status
    has_critical = any(a.severity == Severity.CRITICAL for a in all_alerts)
    has_warning = any(a.severity == Severity.WARNING for a in all_alerts)

    if has_critical:
        overall = "CRITICAL"
    elif has_warning:
        overall = "WARNING"
    else:
        overall = "HEALTHY"

    passed = sum(1 for c in checks if c.get("ok"))
    total = len(checks)

    report: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall,
        "summary": f"{passed}/{total} checks passed",
        "checks": checks,
        "alerts": [a.to_dict() for a in all_alerts],
        "alert_counts": {
            "warning": sum(1 for a in all_alerts if a.severity == Severity.WARNING),
            "critical": sum(1 for a in all_alerts if a.severity == Severity.CRITICAL),
        },
    }

    log.info(
        f"Health check sweep complete: {overall}",
        metrics={
            "overall": overall,
            "passed": passed,
            "total": total,
            "warnings": report["alert_counts"]["warning"],
            "criticals": report["alert_counts"]["critical"],
        },
    )

    # Persist alerts
    _write_alerts(all_alerts)

    return report


# ---------------------------------------------------------------------------
# Alert persistence
# ---------------------------------------------------------------------------


def _write_alerts(alerts: List[Alert]) -> None:
    """Write active alerts to outputs/monitoring/alerts.json."""
    MONITORING_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(alerts),
        "alerts": [a.to_dict() for a in alerts],
    }
    with open(ALERTS_FILE, "w") as fh:
        json.dump(payload, fh, indent=2)
    log.info(f"Wrote {len(alerts)} alert(s) to {ALERTS_FILE}")


def load_alerts() -> Dict[str, Any]:
    """Read the most recent alerts from disk."""
    if not ALERTS_FILE.exists():
        return {"generated_at": None, "count": 0, "alerts": []}
    with open(ALERTS_FILE) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# CLI pretty-printers
# ---------------------------------------------------------------------------

_STATUS_LABELS = {
    "OK": "PASS",
    "WARNING": "WARN",
    "CRITICAL": "CRIT",
    "SKIP": "SKIP",
    "ERROR": "ERR ",
}


def _print_report_text(report: Dict[str, Any]) -> None:
    """Human-friendly summary to stdout."""
    print("=" * 65)
    print("Cricket Playbook - Production Monitoring Report")
    print("Owner: Jose Mourinho | Ticket: TKT-157 | EPIC: EPIC-015")
    print(f"Timestamp: {report['timestamp']}")
    print("=" * 65)
    print()

    for check in report["checks"]:
        label = _STATUS_LABELS.get(check["status"], check["status"])
        print(f"  [{label}] {check['name']}: {check.get('detail', '')}")

    print()
    print("-" * 65)
    print(f"  Overall: {report['overall_status']}  ({report['summary']})")
    alerts_w = report["alert_counts"]["warning"]
    alerts_c = report["alert_counts"]["critical"]
    print(f"  Alerts:  {alerts_w} WARNING, {alerts_c} CRITICAL")
    print("-" * 65)

    if report["alerts"]:
        print()
        print("  Active alerts:")
        for alert in report["alerts"]:
            sev = alert["severity"]
            print(f"    [{sev}] {alert['component']}: {alert['message']}")

    print()
    print(f"  Alert file: {ALERTS_FILE}")
    print("=" * 65)


def _print_alerts_text(data: Dict[str, Any]) -> None:
    """Human-friendly alert listing to stdout."""
    alerts = data.get("alerts", [])
    gen = data.get("generated_at", "unknown")

    print("=" * 65)
    print("Cricket Playbook - Active Alerts")
    print(f"Generated: {gen}")
    print("=" * 65)

    if not alerts:
        print()
        print("  No active alerts.")
    else:
        print()
        for alert in alerts:
            sev = alert["severity"]
            print(f"  [{sev}] {alert['component']}: {alert['message']}")
            print(f"         at {alert['timestamp']}")

    print()
    print("=" * 65)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry-point for monitoring.

    Returns 0 when all checks pass or when showing alerts;
    returns 1 when any CRITICAL alert fires, 2 on usage error.
    """
    parser = argparse.ArgumentParser(
        description="Cricket Playbook production monitoring & alerting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run all health checks and print summary",
    )
    parser.add_argument(
        "--alerts",
        action="store_true",
        help="Show active alerts from last run",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Machine-readable JSON output",
    )
    args = parser.parse_args(argv)

    if not args.check and not args.alerts:
        parser.print_help()
        return 2

    if args.check:
        report = run_all_checks()
        if args.json_output:
            # Strip alert objects (already serialised), remove non-serialisable
            # check sub-keys like "alerts" that contain Alert objects
            clean_checks = []
            for chk in report["checks"]:
                clean = {k: v for k, v in chk.items() if k != "alerts"}
                clean_checks.append(clean)
            output = {
                "timestamp": report["timestamp"],
                "overall_status": report["overall_status"],
                "summary": report["summary"],
                "checks": clean_checks,
                "alerts": report["alerts"],
                "alert_counts": report["alert_counts"],
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            _print_report_text(report)

        has_critical = report["alert_counts"]["critical"] > 0
        return 1 if has_critical else 0

    if args.alerts:
        data = load_alerts()
        if args.json_output:
            print(json.dumps(data, indent=2))
        else:
            _print_alerts_text(data)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
