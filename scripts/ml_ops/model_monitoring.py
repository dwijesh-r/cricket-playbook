#!/usr/bin/env python3
"""
Cricket Playbook - Model Monitoring Module
==========================================
Real-time monitoring for ML model health, drift detection, and performance metrics.

Author: Ime Udoka (MLOps Lead)
Version: 1.0.0
Ticket: TKT-073

Features:
- Cluster distribution tracking over time
- Feature drift detection using KS statistic
- PCA variance validation against thresholds
- Prediction metrics logging (counts, latency)
- Health report generation

Alert Thresholds:
- PCA variance: batters < 70%, bowlers < 50%
- Cluster size: < 10 players
- Feature drift: KS statistic > 0.1
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# Attempt relative import for logging, fall back to direct import
try:
    from scripts.utils.logging_config import setup_logger
except ImportError:
    try:
        from utils.logging_config import setup_logger
    except ImportError:
        import logging

        def setup_logger(name: str, **kwargs) -> logging.Logger:
            """Fallback logger setup if logging_config is not available."""
            logger = logging.getLogger(name)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(
                    logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
                )
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            return logger


# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
MONITORING_DIR = PROJECT_DIR / "outputs" / "monitoring"
METRICS_FILE = MONITORING_DIR / "model_metrics.json"
HEALTH_REPORT_DIR = MONITORING_DIR / "health_reports"


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertThresholds:
    """
    Configurable alert thresholds for model monitoring.

    IPL-Specific Threshold Justification:
    -------------------------------------
    These thresholds are calibrated for IPL T20 cricket data (2008-2025):

    - PCA Variance: Batter features are more standardized (SR, avg, boundary%)
      achieving 83%+ variance easily. Bowler features are more complex
      (phase-specific, matchup-dependent) so 50% is acceptable.

    - Feature Drift (KS=0.1): IPL data shows natural season-to-season variation
      of ~0.05-0.08 KS. Threshold of 0.1 catches meaningful shifts while
      tolerating normal variation. Rule changes (Impact Player 2023) can
      trigger 0.12-0.15 drift - these should be investigated.

    - Multivariate Drift (Mahalanobis > 3.0): Based on chi-squared distribution
      with p < 0.01 for typical feature dimensions (8 batter, 16 bowler features).
      Catches correlated feature shifts that univariate KS would miss.

    - Cluster Size (10+): Ensures each archetype has statistical validity.
      With ~170 batters and ~270 bowlers, 5 clusters should average 34-54 each.
      Clusters < 10 suggest overfitting or data issues.
    """

    # PCA variance thresholds (minimum acceptable)
    pca_variance_batter: float = 0.70  # 70% for batters (typically achieve 83%+)
    pca_variance_bowler: float = 0.50  # 50% for bowlers (more complex features)

    # Cluster size threshold (minimum players per cluster)
    min_cluster_size: int = 10

    # Univariate feature drift threshold (KS statistic)
    # 0.1 = ~10% distribution shift, catches meaningful changes
    feature_drift_ks: float = 0.1

    # Multivariate drift threshold (Mahalanobis distance)
    # 3.0 corresponds to p < 0.01 for chi-squared test
    multivariate_drift_mahal: float = 3.0

    # Latency thresholds (seconds)
    prediction_latency_warning: float = 1.0
    prediction_latency_critical: float = 5.0


@dataclass
class Alert:
    """Represents a monitoring alert."""

    level: AlertLevel
    metric: str
    message: str
    value: Any
    threshold: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for serialization."""
        return {
            "level": self.level.value,
            "metric": self.metric,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
        }


@dataclass
class ClusterDistribution:
    """Tracks cluster distribution over time."""

    timestamp: str
    player_type: str  # 'batter' or 'bowler'
    cluster_sizes: Dict[int, int]  # cluster_id -> count
    total_players: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "player_type": self.player_type,
            "cluster_sizes": self.cluster_sizes,
            "total_players": self.total_players,
        }


@dataclass
class FeatureDriftResult:
    """Result of feature drift detection."""

    feature_name: str
    ks_statistic: float
    p_value: float
    is_drifted: bool
    baseline_mean: float
    current_mean: float
    baseline_std: float
    current_std: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "feature_name": self.feature_name,
            "ks_statistic": round(self.ks_statistic, 4),
            "p_value": round(self.p_value, 4),
            "is_drifted": self.is_drifted,
            "baseline_mean": round(self.baseline_mean, 4),
            "current_mean": round(self.current_mean, 4),
            "baseline_std": round(self.baseline_std, 4),
            "current_std": round(self.current_std, 4),
        }


@dataclass
class MultivariateDriftResult:
    """Result of multivariate drift detection using Mahalanobis distance."""

    model_name: str
    mahalanobis_distance: float
    is_drifted: bool
    n_features: int
    n_baseline_samples: int
    n_current_samples: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_name": self.model_name,
            "mahalanobis_distance": round(self.mahalanobis_distance, 4),
            "is_drifted": self.is_drifted,
            "n_features": self.n_features,
            "n_baseline_samples": self.n_baseline_samples,
            "n_current_samples": self.n_current_samples,
            "timestamp": self.timestamp,
        }


@dataclass
class BaselineMetadata:
    """
    Metadata for baseline feature distributions.

    Baseline Lifecycle Policy:
    --------------------------
    - CREATION: Set after initial model training or retraining
    - REFRESH: Update after each model retraining cycle
    - OWNER: Ime Udoka (MLOps Lead) or Stephen Curry (Analytics Lead)
    - RETENTION: Keep previous baseline for 30 days for comparison
    - VALIDATION: Baseline must have 100+ samples per player type

    When to Refresh:
    - After model retraining with new season data
    - After feature engineering changes
    - After major data pipeline updates
    - Recommended: Start of each IPL season
    """

    model_name: str
    created_at: str
    created_by: str
    n_samples: int
    feature_names: List[str]
    season_range: str  # e.g., "2021-2025"
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_name": self.model_name,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "n_samples": self.n_samples,
            "feature_names": self.feature_names,
            "season_range": self.season_range,
            "notes": self.notes,
        }


@dataclass
class PredictionMetrics:
    """Metrics for prediction logging."""

    timestamp: str
    model_type: str
    prediction_count: int
    latency_ms: float
    success: bool
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "model_type": self.model_type,
            "prediction_count": self.prediction_count,
            "latency_ms": round(self.latency_ms, 2),
            "success": self.success,
            "error_message": self.error_message,
        }


class ModelMonitor:
    """
    Model monitoring class for Cricket Playbook ML models.

    Provides real-time monitoring for:
    - Cluster distribution tracking
    - Feature drift detection
    - PCA variance validation
    - Prediction metrics logging
    - Health report generation

    Example:
        >>> monitor = ModelMonitor()
        >>> monitor.track_cluster_distribution(batter_df, 'batter')
        >>> alerts = monitor.check_pca_variance(0.65, 'batter')
        >>> report = monitor.generate_health_report()
    """

    def __init__(
        self,
        thresholds: Optional[AlertThresholds] = None,
        log_to_file: bool = True,
    ):
        """
        Initialize the ModelMonitor.

        Args:
            thresholds: Custom alert thresholds (uses defaults if None)
            log_to_file: Whether to log to file in addition to console
        """
        self.thresholds = thresholds or AlertThresholds()
        self.logger = setup_logger(__name__, log_to_file=log_to_file)

        # Initialize storage directories
        MONITORING_DIR.mkdir(parents=True, exist_ok=True)
        HEALTH_REPORT_DIR.mkdir(parents=True, exist_ok=True)

        # In-memory metrics storage
        self._cluster_history: List[ClusterDistribution] = []
        self._drift_results: List[FeatureDriftResult] = []
        self._multivariate_drift_results: List[MultivariateDriftResult] = []
        self._prediction_metrics: List[PredictionMetrics] = []
        self._alerts: List[Alert] = []
        self._baseline_features: Dict[str, pd.DataFrame] = {}
        self._baseline_metadata: Dict[str, BaselineMetadata] = {}

        self.logger.info("ModelMonitor initialized with thresholds: %s", self.thresholds)

    def track_cluster_distribution(
        self,
        clustered_df: pd.DataFrame,
        player_type: str,
        cluster_col: str = "cluster",
    ) -> Tuple[ClusterDistribution, List[Alert]]:
        """
        Track cluster distribution and check for size anomalies.

        Args:
            clustered_df: DataFrame with cluster assignments
            player_type: 'batter' or 'bowler'
            cluster_col: Name of the cluster column

        Returns:
            Tuple of (ClusterDistribution, list of alerts)
        """
        if cluster_col not in clustered_df.columns:
            raise ValueError(f"Cluster column '{cluster_col}' not found in DataFrame")

        # Calculate cluster sizes
        cluster_counts = clustered_df[cluster_col].value_counts().to_dict()
        cluster_sizes = {int(k): int(v) for k, v in cluster_counts.items()}

        distribution = ClusterDistribution(
            timestamp=datetime.now().isoformat(),
            player_type=player_type,
            cluster_sizes=cluster_sizes,
            total_players=len(clustered_df),
        )

        self._cluster_history.append(distribution)

        # Check for undersized clusters
        alerts = []
        for cluster_id, size in cluster_sizes.items():
            if size < self.thresholds.min_cluster_size:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="cluster_size",
                    message=f"{player_type.capitalize()} cluster {cluster_id} has only {size} players",
                    value=size,
                    threshold=self.thresholds.min_cluster_size,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.warning(
                    "Undersized cluster detected: %s cluster %d has %d players (min: %d)",
                    player_type,
                    cluster_id,
                    size,
                    self.thresholds.min_cluster_size,
                )

        self.logger.info(
            "Tracked %s cluster distribution: %d clusters, %d total players",
            player_type,
            len(cluster_sizes),
            distribution.total_players,
        )

        return distribution, alerts

    def set_baseline_features(
        self,
        baseline_df: pd.DataFrame,
        feature_cols: List[str],
        model_name: str,
        created_by: str = "unknown",
        season_range: str = "unknown",
        notes: Optional[str] = None,
    ) -> None:
        """
        Set baseline feature distributions for drift detection.

        Baseline Lifecycle:
        - Must be called after model training/retraining
        - Should be refreshed at start of each IPL season
        - Owner: Ime Udoka (MLOps) or Stephen Curry (Analytics)

        Args:
            baseline_df: DataFrame containing baseline feature values
            feature_cols: List of feature column names
            model_name: Identifier for the model (e.g., 'batter_clustering')
            created_by: Name of person/agent setting baseline
            season_range: Data season range (e.g., "2021-2025")
            notes: Optional notes about the baseline

        Raises:
            ValueError: If baseline has fewer than 100 samples
        """
        if len(baseline_df) < 100:
            raise ValueError(
                f"Baseline must have at least 100 samples, got {len(baseline_df)}. "
                "Insufficient data for reliable drift detection."
            )

        self._baseline_features[model_name] = baseline_df[feature_cols].copy()
        self._baseline_metadata[model_name] = BaselineMetadata(
            model_name=model_name,
            created_at=datetime.now().isoformat(),
            created_by=created_by,
            n_samples=len(baseline_df),
            feature_names=feature_cols,
            season_range=season_range,
            notes=notes,
        )
        self.logger.info(
            "Set baseline features for %s: %d features, %d samples, created by %s",
            model_name,
            len(feature_cols),
            len(baseline_df),
            created_by,
        )

    def get_baseline_metadata(self, model_name: str) -> Optional[BaselineMetadata]:
        """Get metadata for a baseline, if set."""
        return self._baseline_metadata.get(model_name)

    def detect_feature_drift(
        self,
        current_df: pd.DataFrame,
        feature_cols: List[str],
        model_name: str,
        strict: bool = True,
    ) -> Tuple[List[FeatureDriftResult], List[Alert]]:
        """
        Detect univariate feature drift using Kolmogorov-Smirnov test.

        Compares current feature distributions against baseline independently
        for each feature. For correlated feature shifts, also use
        detect_multivariate_drift().

        Args:
            current_df: DataFrame with current feature values
            feature_cols: List of feature column names to check
            model_name: Identifier for the model
            strict: If True, raises error when no baseline exists (recommended)

        Returns:
            Tuple of (list of FeatureDriftResult, list of alerts)

        Raises:
            ValueError: If strict=True and no baseline exists
        """
        if model_name not in self._baseline_features:
            msg = (
                f"No baseline features set for {model_name}. "
                "Call set_baseline_features() first with valid baseline data."
            )
            if strict:
                raise ValueError(msg)
            self.logger.warning(msg)
            return [], []

        baseline_df = self._baseline_features[model_name]
        results = []
        alerts = []

        for feature in feature_cols:
            if feature not in baseline_df.columns or feature not in current_df.columns:
                self.logger.warning("Feature %s not found in baseline or current data", feature)
                continue

            baseline_values = baseline_df[feature].dropna().values
            current_values = current_df[feature].dropna().values

            if len(baseline_values) < 10 or len(current_values) < 10:
                self.logger.warning(
                    "Insufficient samples for KS test on feature %s (baseline: %d, current: %d)",
                    feature,
                    len(baseline_values),
                    len(current_values),
                )
                continue

            # Perform KS test
            ks_stat, p_value = stats.ks_2samp(baseline_values, current_values)
            is_drifted = ks_stat > self.thresholds.feature_drift_ks

            result = FeatureDriftResult(
                feature_name=feature,
                ks_statistic=ks_stat,
                p_value=p_value,
                is_drifted=is_drifted,
                baseline_mean=np.mean(baseline_values),
                current_mean=np.mean(current_values),
                baseline_std=np.std(baseline_values),
                current_std=np.std(current_values),
            )
            results.append(result)
            self._drift_results.append(result)

            if is_drifted:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="feature_drift",
                    message=f"Feature drift detected in {feature} (KS={ks_stat:.3f})",
                    value=ks_stat,
                    threshold=self.thresholds.feature_drift_ks,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.warning(
                    "Feature drift detected: %s (KS=%.3f > %.3f)",
                    feature,
                    ks_stat,
                    self.thresholds.feature_drift_ks,
                )

        self.logger.info(
            "Feature drift check completed for %s: %d features checked, %d drifted",
            model_name,
            len(results),
            sum(1 for r in results if r.is_drifted),
        )

        return results, alerts

    def detect_multivariate_drift(
        self,
        current_df: pd.DataFrame,
        feature_cols: List[str],
        model_name: str,
    ) -> Tuple[Optional[MultivariateDriftResult], List[Alert]]:
        """
        Detect multivariate drift using Mahalanobis distance.

        Catches correlated feature shifts that univariate KS tests miss.
        Compares the centroid of current data to baseline distribution.

        Why Mahalanobis? IPL features are correlated (strike_rate affects avg,
        phase stats interconnect). Univariate tests might miss "compensating
        drift" where two features shift in opposite directions.

        Args:
            current_df: DataFrame with current feature values
            feature_cols: List of feature column names
            model_name: Model identifier

        Returns:
            Tuple of (MultivariateDriftResult or None, list of alerts)

        Raises:
            ValueError: If no baseline exists
        """
        if model_name not in self._baseline_features:
            raise ValueError(f"No baseline for {model_name}. Call set_baseline_features() first.")

        baseline_df = self._baseline_features[model_name]
        alerts = []

        # Get common features
        common_features = [
            f for f in feature_cols if f in baseline_df.columns and f in current_df.columns
        ]

        if len(common_features) < 2:
            self.logger.warning("Need at least 2 features for multivariate drift")
            return None, []

        # Extract feature matrices
        baseline_matrix = baseline_df[common_features].dropna().values
        current_matrix = current_df[common_features].dropna().values

        if len(baseline_matrix) < 10 or len(current_matrix) < 10:
            self.logger.warning("Insufficient samples for multivariate drift detection")
            return None, []

        try:
            # Compute baseline statistics
            baseline_mean = np.mean(baseline_matrix, axis=0)
            baseline_cov = np.cov(baseline_matrix, rowvar=False)

            # Regularize covariance matrix for numerical stability
            baseline_cov += np.eye(len(common_features)) * 1e-6

            # Compute current centroid
            current_mean = np.mean(current_matrix, axis=0)

            # Compute Mahalanobis distance
            diff = current_mean - baseline_mean
            cov_inv = np.linalg.inv(baseline_cov)
            mahal_dist = np.sqrt(diff @ cov_inv @ diff)

            is_drifted = mahal_dist > self.thresholds.multivariate_drift_mahal

            result = MultivariateDriftResult(
                model_name=model_name,
                mahalanobis_distance=mahal_dist,
                is_drifted=is_drifted,
                n_features=len(common_features),
                n_baseline_samples=len(baseline_matrix),
                n_current_samples=len(current_matrix),
            )
            self._multivariate_drift_results.append(result)

            if is_drifted:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="multivariate_drift",
                    message=f"Multivariate drift detected for {model_name} (Mahal={mahal_dist:.2f})",
                    value=mahal_dist,
                    threshold=self.thresholds.multivariate_drift_mahal,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.warning(
                    "Multivariate drift detected: %s (Mahalanobis=%.2f > %.2f)",
                    model_name,
                    mahal_dist,
                    self.thresholds.multivariate_drift_mahal,
                )
            else:
                self.logger.info(
                    "Multivariate drift check passed: %s (Mahalanobis=%.2f)",
                    model_name,
                    mahal_dist,
                )

            return result, alerts

        except np.linalg.LinAlgError as e:
            self.logger.error("Failed to compute Mahalanobis distance: %s", e)
            return None, []

    def check_pca_variance(
        self,
        variance_explained: float,
        player_type: str,
    ) -> List[Alert]:
        """
        Validate PCA variance against thresholds.

        Args:
            variance_explained: Cumulative variance explained (0-1)
            player_type: 'batter' or 'bowler'

        Returns:
            List of alerts if threshold violated
        """
        if player_type.lower() == "batter":
            threshold = self.thresholds.pca_variance_batter
        elif player_type.lower() == "bowler":
            threshold = self.thresholds.pca_variance_bowler
        else:
            raise ValueError(f"Unknown player type: {player_type}")

        alerts = []

        if variance_explained < threshold:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                metric="pca_variance",
                message=f"{player_type.capitalize()} PCA variance {variance_explained:.1%} below threshold {threshold:.0%}",
                value=variance_explained,
                threshold=threshold,
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self.logger.critical(
                "PCA variance violation: %s variance %.1f%% < %.0f%%",
                player_type,
                variance_explained * 100,
                threshold * 100,
            )
        else:
            self.logger.info(
                "PCA variance check passed: %s variance %.1f%% >= %.0f%%",
                player_type,
                variance_explained * 100,
                threshold * 100,
            )

        return alerts

    def log_prediction_metrics(
        self,
        model_type: str,
        prediction_count: int,
        latency_seconds: float,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> List[Alert]:
        """
        Log prediction metrics and check latency thresholds.

        Args:
            model_type: Type of model (e.g., 'batter_clustering')
            prediction_count: Number of predictions made
            latency_seconds: Total prediction latency in seconds
            success: Whether prediction was successful
            error_message: Error message if prediction failed

        Returns:
            List of alerts for latency violations
        """
        latency_ms = latency_seconds * 1000

        metrics = PredictionMetrics(
            timestamp=datetime.now().isoformat(),
            model_type=model_type,
            prediction_count=prediction_count,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message,
        )

        self._prediction_metrics.append(metrics)

        alerts = []

        if not success:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                metric="prediction_error",
                message=f"Prediction failed for {model_type}: {error_message}",
                value=error_message,
                threshold=None,
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self.logger.error("Prediction failed: %s - %s", model_type, error_message)
        elif latency_seconds >= self.thresholds.prediction_latency_critical:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                metric="prediction_latency",
                message=f"Critical latency for {model_type}: {latency_ms:.0f}ms",
                value=latency_ms,
                threshold=self.thresholds.prediction_latency_critical * 1000,
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self.logger.critical(
                "Critical prediction latency: %s took %.0fms (threshold: %.0fms)",
                model_type,
                latency_ms,
                self.thresholds.prediction_latency_critical * 1000,
            )
        elif latency_seconds >= self.thresholds.prediction_latency_warning:
            alert = Alert(
                level=AlertLevel.WARNING,
                metric="prediction_latency",
                message=f"High latency for {model_type}: {latency_ms:.0f}ms",
                value=latency_ms,
                threshold=self.thresholds.prediction_latency_warning * 1000,
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self.logger.warning(
                "High prediction latency: %s took %.0fms (threshold: %.0fms)",
                model_type,
                latency_ms,
                self.thresholds.prediction_latency_warning * 1000,
            )
        else:
            self.logger.info(
                "Prediction completed: %s, %d predictions, %.0fms",
                model_type,
                prediction_count,
                latency_ms,
            )

        return alerts

    def generate_health_report(
        self,
        include_history: bool = True,
        save_to_file: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive health report.

        Args:
            include_history: Include full metric history in report
            save_to_file: Save report to JSON file

        Returns:
            Health report dictionary
        """
        now = datetime.now()

        # Calculate summary statistics
        total_predictions = sum(m.prediction_count for m in self._prediction_metrics)
        successful_predictions = sum(
            m.prediction_count for m in self._prediction_metrics if m.success
        )
        avg_latency = (
            np.mean([m.latency_ms for m in self._prediction_metrics])
            if self._prediction_metrics
            else 0
        )

        # Count alerts by level
        alert_counts = {
            "info": sum(1 for a in self._alerts if a.level == AlertLevel.INFO),
            "warning": sum(1 for a in self._alerts if a.level == AlertLevel.WARNING),
            "critical": sum(1 for a in self._alerts if a.level == AlertLevel.CRITICAL),
        }

        # Determine overall health status
        if alert_counts["critical"] > 0:
            health_status = "CRITICAL"
        elif alert_counts["warning"] > 0:
            health_status = "WARNING"
        else:
            health_status = "HEALTHY"

        # Get latest cluster distributions
        latest_clusters = {}
        for dist in reversed(self._cluster_history):
            if dist.player_type not in latest_clusters:
                latest_clusters[dist.player_type] = dist.to_dict()

        # Get drifted features
        drifted_features = [r.to_dict() for r in self._drift_results if r.is_drifted]

        report = {
            "generated_at": now.isoformat(),
            "health_status": health_status,
            "summary": {
                "total_predictions": total_predictions,
                "successful_predictions": successful_predictions,
                "success_rate": (
                    successful_predictions / total_predictions if total_predictions > 0 else 1.0
                ),
                "average_latency_ms": round(avg_latency, 2),
                "alert_counts": alert_counts,
            },
            "thresholds": {
                "pca_variance_batter": self.thresholds.pca_variance_batter,
                "pca_variance_bowler": self.thresholds.pca_variance_bowler,
                "min_cluster_size": self.thresholds.min_cluster_size,
                "feature_drift_ks": self.thresholds.feature_drift_ks,
                "latency_warning_ms": self.thresholds.prediction_latency_warning * 1000,
                "latency_critical_ms": self.thresholds.prediction_latency_critical * 1000,
            },
            "latest_cluster_distributions": latest_clusters,
            "drifted_features": drifted_features,
            "recent_alerts": [a.to_dict() for a in self._alerts[-10:]],
        }

        if include_history:
            report["history"] = {
                "cluster_distributions": [d.to_dict() for d in self._cluster_history],
                "drift_results": [r.to_dict() for r in self._drift_results],
                "prediction_metrics": [m.to_dict() for m in self._prediction_metrics[-100:]],
                "all_alerts": [a.to_dict() for a in self._alerts],
            }

        if save_to_file:
            report_filename = f"health_report_{now.strftime('%Y%m%d_%H%M%S')}.json"
            report_path = HEALTH_REPORT_DIR / report_filename
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            self.logger.info("Health report saved to: %s", report_path)

        self.logger.info(
            "Health report generated: status=%s, alerts=%d critical / %d warning",
            health_status,
            alert_counts["critical"],
            alert_counts["warning"],
        )

        return report

    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts, optionally filtered by level.

        Args:
            level: Filter by alert level (None for all)
            limit: Maximum number of alerts to return

        Returns:
            List of alert dictionaries
        """
        alerts = self._alerts
        if level:
            alerts = [a for a in alerts if a.level == level]
        return [a.to_dict() for a in alerts[-limit:]]

    def clear_metrics(self) -> None:
        """Clear all stored metrics and alerts."""
        self._cluster_history.clear()
        self._drift_results.clear()
        self._prediction_metrics.clear()
        self._alerts.clear()
        self.logger.info("All metrics cleared")

    def export_metrics(self, filepath: Optional[Path] = None) -> Path:
        """
        Export all metrics to a JSON file.

        Args:
            filepath: Optional custom path (defaults to METRICS_FILE)

        Returns:
            Path to the exported file
        """
        filepath = filepath or METRICS_FILE

        data = {
            "exported_at": datetime.now().isoformat(),
            "cluster_distributions": [d.to_dict() for d in self._cluster_history],
            "drift_results": [r.to_dict() for r in self._drift_results],
            "prediction_metrics": [m.to_dict() for m in self._prediction_metrics],
            "alerts": [a.to_dict() for a in self._alerts],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        self.logger.info("Metrics exported to: %s", filepath)
        return filepath


def create_monitor_with_defaults() -> ModelMonitor:
    """
    Factory function to create a ModelMonitor with default settings.

    Returns:
        Configured ModelMonitor instance
    """
    return ModelMonitor(
        thresholds=AlertThresholds(),
        log_to_file=True,
    )


# Context manager for timing predictions
class PredictionTimer:
    """
    Context manager for timing predictions and logging metrics.

    Example:
        >>> monitor = ModelMonitor()
        >>> with PredictionTimer(monitor, 'batter_clustering', 100) as timer:
        ...     predictions = model.predict(X)
        >>> # Metrics are automatically logged
    """

    def __init__(
        self,
        monitor: ModelMonitor,
        model_type: str,
        prediction_count: int,
    ):
        self.monitor = monitor
        self.model_type = model_type
        self.prediction_count = prediction_count
        self.start_time: float = 0
        self.error: Optional[str] = None

    def __enter__(self) -> "PredictionTimer":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        elapsed = time.time() - self.start_time
        success = exc_type is None
        error_msg = str(exc_val) if exc_val else None

        self.monitor.log_prediction_metrics(
            model_type=self.model_type,
            prediction_count=self.prediction_count,
            latency_seconds=elapsed,
            success=success,
            error_message=error_msg,
        )

        # Don't suppress exceptions
        return False


if __name__ == "__main__":
    # Example usage demonstration
    print("=" * 70)
    print("Cricket Playbook - Model Monitoring Demo")
    print("=" * 70)

    # Create monitor
    monitor = ModelMonitor(log_to_file=False)

    # Simulate cluster distribution tracking
    print("\n1. Tracking cluster distribution...")
    sample_clusters = pd.DataFrame(
        {
            "player_id": range(100),
            "player_name": [f"Player_{i}" for i in range(100)],
            "cluster": np.random.randint(0, 5, 100),
        }
    )

    distribution, alerts = monitor.track_cluster_distribution(sample_clusters, "batter")
    print(
        f"   Tracked {distribution.total_players} players across {len(distribution.cluster_sizes)} clusters"
    )

    # Simulate PCA variance check
    print("\n2. Checking PCA variance...")
    pca_alerts = monitor.check_pca_variance(0.836, "batter")  # From README: 83.6%
    print(f"   Batter variance check: {len(pca_alerts)} alerts")

    pca_alerts = monitor.check_pca_variance(0.45, "bowler")  # Below threshold for demo
    print(f"   Bowler variance check (simulated failure): {len(pca_alerts)} alerts")

    # Simulate feature drift detection
    print("\n3. Setting baseline and checking feature drift...")
    baseline = pd.DataFrame(
        {
            "strike_rate": np.random.normal(130, 20, 200),
            "boundary_pct": np.random.normal(15, 5, 200),
        }
    )
    current = pd.DataFrame(
        {
            "strike_rate": np.random.normal(135, 22, 180),  # Slight shift
            "boundary_pct": np.random.normal(15, 5, 180),
        }
    )

    monitor.set_baseline_features(baseline, ["strike_rate", "boundary_pct"], "batter_clustering")
    drift_results, drift_alerts = monitor.detect_feature_drift(
        current, ["strike_rate", "boundary_pct"], "batter_clustering"
    )
    print(f"   Checked {len(drift_results)} features, {len(drift_alerts)} drift alerts")

    # Simulate prediction logging
    print("\n4. Logging prediction metrics...")
    with PredictionTimer(monitor, "batter_clustering", 173):
        time.sleep(0.1)  # Simulate prediction time
    print("   Prediction logged successfully")

    # Generate health report
    print("\n5. Generating health report...")
    report = monitor.generate_health_report(include_history=False, save_to_file=False)
    print(f"   Health Status: {report['health_status']}")
    print(f"   Total Predictions: {report['summary']['total_predictions']}")
    print(f"   Alerts: {report['summary']['alert_counts']}")

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
