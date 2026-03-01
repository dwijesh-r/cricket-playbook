#!/usr/bin/env python3
"""
Cricket Playbook - Automated ML Health Check Runner
====================================================
One-command runner for all ML monitoring checks.

Author: Ime Udoka (MLOps Lead) + Jose Mourinho (Robustness Review)
Version: 1.0.0
Ticket: TKT-073

Usage:
    python scripts/ml_ops/run_health_check.py
    python scripts/ml_ops/run_health_check.py --verbose
    python scripts/ml_ops/run_health_check.py --export

What It Checks:
    1. PCA variance thresholds (batters > 70%, bowlers > 50%)
    2. Cluster size distribution (min 10 per cluster)
    3. Feature drift detection (if baseline exists)
    4. Multivariate drift detection
    5. Win probability model health (artifacts, baselines)
    6. Generates comprehensive health report
    7. Win prob baseline readiness
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

import pandas as pd

from scripts.ml_ops.model_monitoring import (
    Alert,
    AlertLevel,
    create_monitor_with_defaults,
)
from scripts.ml_ops.model_registry import ModelRegistry

# Paths
DATA_DIR = PROJECT_DIR / "data"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
TAGS_DIR = OUTPUTS_DIR / "tags"
MONITORING_DIR = OUTPUTS_DIR / "monitoring"


def load_player_tags() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load batter and bowler tags from outputs."""
    tags_file = TAGS_DIR / "player_tags.json"

    if not tags_file.exists():
        raise FileNotFoundError(
            f"Player tags not found at {tags_file}. Run player_clustering_v2.py first."
        )

    with open(tags_file) as f:
        data = json.load(f)

    batters = pd.DataFrame(data.get("batters", []))
    bowlers = pd.DataFrame(data.get("bowlers", []))

    return batters, bowlers


def get_cluster_distribution(df: pd.DataFrame, cluster_col: str = "cluster") -> dict:
    """Get cluster size distribution from a DataFrame."""
    if cluster_col not in df.columns:
        # Try alternative column names
        for alt in ["archetype", "batter_archetype", "bowler_archetype", "cluster_label"]:
            if alt in df.columns:
                cluster_col = alt
                break
        else:
            return {}

    return df[cluster_col].value_counts().to_dict()


def run_health_check(verbose: bool = False, export: bool = False) -> dict:
    """
    Run comprehensive ML health check.

    Args:
        verbose: Print detailed output
        export: Export metrics to file

    Returns:
        Health report dictionary
    """
    print("\n" + "=" * 60)
    print("🏏 CRICKET PLAYBOOK - ML HEALTH CHECK")
    print("=" * 60)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    monitor = create_monitor_with_defaults()
    alerts = []

    # 1. Load player tags
    print("\n[1/7] Loading player tags...")
    try:
        batters, bowlers = load_player_tags()
        print(f"   ✅ Batters: {len(batters)} players")
        print(f"   ✅ Bowlers: {len(bowlers)} players")
    except FileNotFoundError as e:
        print(f"   ❌ FAILED: {e}")
        return {"status": "FAILED", "error": str(e)}

    # 2. Check cluster distribution
    print("\n[2/7] Checking cluster distribution...")

    batter_clusters = get_cluster_distribution(batters)
    bowler_clusters = get_cluster_distribution(bowlers)

    if batter_clusters:
        batter_dist, batter_alerts = monitor.track_cluster_sizes(
            cluster_sizes=list(batter_clusters.values()), player_type="batter"
        )
        alerts.extend(batter_alerts)
        print(f"   Batter clusters: {batter_clusters}")
        min_batter = min(batter_clusters.values()) if batter_clusters else 0
        status = "✅" if min_batter >= 10 else "⚠️"
        print(f"   {status} Min cluster size: {min_batter}")

    if bowler_clusters:
        bowler_dist, bowler_alerts = monitor.track_cluster_sizes(
            cluster_sizes=list(bowler_clusters.values()), player_type="bowler"
        )
        alerts.extend(bowler_alerts)
        print(f"   Bowler clusters: {bowler_clusters}")
        min_bowler = min(bowler_clusters.values()) if bowler_clusters else 0
        status = "✅" if min_bowler >= 10 else "⚠️"
        print(f"   {status} Min cluster size: {min_bowler}")

    # 3. Check PCA variance (from model registry if available)
    print("\n[3/7] Checking PCA variance...")

    # Use the ModelRegistry class for proper integration (TKT-247)
    model_registry = ModelRegistry()
    registry_path = model_registry.path

    if registry_path.exists():
        # Look for the production clustering model's PCA metrics
        production_model = model_registry.get_production("player_clustering")
        if production_model is None:
            # Fall back: try any model with PCA metrics
            all_models = model_registry.list_models(name="player_clustering")
            production_model = all_models[0] if all_models else None

        if production_model and production_model.metrics:
            batter_pca = production_model.metrics.get("batter_pca_variance")
            bowler_pca = production_model.metrics.get("bowler_pca_variance")

            if batter_pca:
                pca_alerts = monitor.check_pca_variance(batter_pca, "batter")
                alerts.extend(pca_alerts)
                status = "✅" if batter_pca >= 0.70 else "❌"
                print(f"   {status} Batter PCA: {batter_pca * 100:.1f}% (threshold: 70%)")

            if bowler_pca:
                pca_alerts = monitor.check_pca_variance(bowler_pca, "bowler")
                alerts.extend(pca_alerts)
                status = "✅" if bowler_pca >= 0.50 else "❌"
                print(f"   {status} Bowler PCA: {bowler_pca * 100:.1f}% (threshold: 50%)")

            if not batter_pca and not bowler_pca:
                print("   ⚠️ PCA metrics not found in production model")
        else:
            print("   ⚠️ No clustering model registered - skipping PCA check")

        # Print registry summary
        all_registered = model_registry.list_models()
        production_count = len(model_registry.list_models(status="production"))
        print(f"   ℹ️  Registry: {len(all_registered)} models, {production_count} in production")
    else:
        print("   ⚠️ Model registry not found - skipping PCA check")

    # 4. Check for baseline and drift detection
    print("\n[4/7] Checking drift detection...")

    batter_baseline = monitor.get_baseline_metadata("batter_clustering")
    bowler_baseline = monitor.get_baseline_metadata("bowler_clustering")

    # Check batter baseline
    if batter_baseline:
        print(f"   ✅ Batter baseline set: {batter_baseline.created_at[:10]}")
        print(f"      Created by: {batter_baseline.created_by}")
        print(f"      Samples: {batter_baseline.n_samples}")

        # Check if stale
        if monitor.is_baseline_stale("batter_clustering", max_age_days=90):
            print("   ⚠️ Batter baseline is stale (>90 days) - consider refreshing")
            stale_alert = Alert(
                level=AlertLevel.WARNING,
                metric="baseline_staleness",
                message="Batter clustering baseline is stale (>90 days old)",
                value="stale",
                threshold="90 days",
            )
            alerts.append(stale_alert)
    else:
        print("   ⚠️ No batter baseline - call set_baseline_features() to enable drift detection")

    # Check bowler baseline
    if bowler_baseline:
        print(f"   ✅ Bowler baseline set: {bowler_baseline.created_at[:10]}")

        if monitor.is_baseline_stale("bowler_clustering", max_age_days=90):
            print("   ⚠️ Bowler baseline is stale (>90 days) - consider refreshing")
    else:
        print("   ⚠️ No bowler baseline - drift detection not available")

    # Note: Actual drift detection requires current feature data
    # which would come from a retraining run. This health check
    # verifies readiness but doesn't run drift checks without data.
    print("\n   ℹ️  Drift detection ready when baselines exist.")
    print("   ℹ️  Multivariate drift (Mahalanobis) available via detect_multivariate_drift()")

    # 5. Win probability model health
    print("\n[5/7] Checking win probability models...")

    win_prob_result = None
    try:
        from scripts.ml_ops.win_prob_monitoring import run_win_prob_health_check

        win_prob_result = run_win_prob_health_check(verbose=verbose)
        win_prob_alerts_raw = win_prob_result.get("alerts", [])

        # Convert alert dicts back to Alert objects for unified counting
        for a_dict in win_prob_alerts_raw:
            level = AlertLevel(a_dict.get("level", "info"))
            alerts.append(
                Alert(
                    level=level,
                    metric=a_dict.get("metric", "win_prob"),
                    message=a_dict.get("message", ""),
                    value=a_dict.get("value"),
                    threshold=a_dict.get("threshold"),
                )
            )
    except ImportError:
        print("   Win prob monitoring not available (win_prob_monitoring.py missing)")
        win_prob_result = None
    except Exception as e:
        print(f"   Win prob check error: {e}")
        win_prob_result = None

    # 6. Generate health report
    print("\n[6/7] Generating health report...")

    _ = monitor.generate_health_report()  # Generates and saves report

    # Determine overall status
    critical_count = sum(1 for a in alerts if a.level == AlertLevel.CRITICAL)
    warning_count = sum(1 for a in alerts if a.level == AlertLevel.WARNING)

    if critical_count > 0:
        overall_status = "🔴 CRITICAL"
    elif warning_count > 0:
        overall_status = "🟡 DEGRADED"
    else:
        overall_status = "🟢 HEALTHY"

    print(f"\n   Status: {overall_status}")
    print(f"   Critical alerts: {critical_count}")
    print(f"   Warning alerts: {warning_count}")

    # Export if requested
    if export:
        export_path = monitor.export_metrics()
        print(f"\n   📁 Metrics exported to: {export_path}")

    # 7. Win prob baseline readiness
    print("\n[7/7] Checking win prob baseline readiness...")
    baseline_dir = MONITORING_DIR / "win_prob_baseline"
    for innings in ("innings1", "innings2"):
        baseline_file = baseline_dir / f"win_prob_{innings}_baseline.json"
        if baseline_file.exists():
            print(f"   Baseline {innings}: found")
        else:
            print(f"   Baseline {innings}: not yet created (run --generate-baselines)")

    # Summary
    print("\n" + "=" * 60)
    print(f"HEALTH CHECK COMPLETE: {overall_status}")
    print("=" * 60)

    if verbose and alerts:
        print("\n📋 ALERT DETAILS:")
        for alert in alerts:
            icon = "🔴" if alert.level == AlertLevel.CRITICAL else "🟡"
            print(f"   {icon} [{alert.level.value.upper()}] {alert.message}")

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "batter_count": len(batters),
        "bowler_count": len(bowlers),
        "batter_clusters": batter_clusters,
        "bowler_clusters": bowler_clusters,
        "critical_alerts": critical_count,
        "warning_alerts": warning_count,
        "alerts": [a.to_dict() for a in alerts],
        "win_prob_health": win_prob_result,
    }


def main():
    parser = argparse.ArgumentParser(description="Cricket Playbook ML Health Check Runner")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print detailed alert information"
    )
    parser.add_argument(
        "--export", "-e", action="store_true", help="Export metrics to outputs/monitoring/"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        result = run_health_check(verbose=args.verbose, export=args.export)

        if args.json:
            print(json.dumps(result, indent=2))

        # Exit with appropriate code
        if "CRITICAL" in result.get("status", ""):
            sys.exit(2)
        elif "DEGRADED" in result.get("status", ""):
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ HEALTH CHECK FAILED: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
