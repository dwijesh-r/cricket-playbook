#!/usr/bin/env python3
"""
Cricket Playbook - Win Probability Model Monitoring
=====================================================
Monitoring framework for win probability models (innings 1 & innings 2).
Extends the existing ModelMonitor with win-prob-specific checks:

1. Prediction calibration drift (Brier score over time windows)
2. Feature distribution drift (KS test against training baseline)
3. Calibration bin monitoring (expected vs observed in 10 bins)
4. Performance by match phase (powerplay / middle / death)
5. JSON report generation

Author: Ime Udoka (MLOps Lead)
Version: 1.0.0
Ticket: TKT-209  |  EPIC-015: Operational Maturity

Model Status: EXPERIMENTAL (historical replay only)
- Models are NOT deployed for live prediction
- Monitoring validates framework readiness for future deployment
- Baselines are template snapshots from training distributions

Alert Thresholds:
- Brier score: > 0.22 (degraded), > 0.25 (critical)
- Feature drift: KS statistic > 0.1
- Calibration bin deviation: > 15% from expected
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

from scripts.ml_ops.model_monitoring import (
    Alert,
    AlertLevel,
    AlertThresholds,
    FeatureDriftResult,
    ModelMonitor,
)

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


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
MONITORING_DIR = PROJECT_DIR / "outputs" / "monitoring"
WIN_PROB_HEALTH_DIR = MONITORING_DIR / "win_prob_health"
WIN_PROB_BASELINE_DIR = MONITORING_DIR / "win_prob_baseline"
MODELS_DIR = PROJECT_DIR / "models"

# ---------------------------------------------------------------------------
# Win Probability Feature List
# ---------------------------------------------------------------------------
WIN_PROB_FEATURES: List[str] = [
    "over_number",
    "ball_number",
    "wickets_fallen",
    "current_score",
    "run_rate",
    "required_run_rate",
    "scoring_rate_last5",
    "wickets_last5",
    "innings_progress",
    "runs_remaining",
    "balls_remaining",
    "partnership_runs",
    "partnership_balls",
]

# Phase boundaries (T20 overs)
PHASE_POWERPLAY = (1, 6)  # Overs 1-6
PHASE_MIDDLE = (7, 15)  # Overs 7-15
PHASE_DEATH = (16, 20)  # Overs 16-20


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class WinProbThresholds:
    """
    Alert thresholds specific to win probability models.

    Threshold Justification (IPL T20):
    -----------------------------------
    - Brier 0.22 (degraded): Baseline well-calibrated models achieve ~0.18-0.20
      on IPL data. A shift to 0.22 suggests mild miscalibration, possibly
      from meta-shifts (new Impact Player rules, pitch changes).

    - Brier 0.25 (critical): At this point the model is worse than a
      naive run-rate-based estimator. Retrain is likely required.

    - KS 0.1 for features: Matches the existing ModelMonitor threshold.
      IPL season-to-season natural variation is ~0.05-0.08.

    - Calibration bin 15%: In a 10-bin calibration, 15% absolute deviation
      means the model says "60% win chance" but reality is 45% or 75%.
      This is actionable miscalibration.
    """

    # Brier score thresholds
    brier_degraded: float = 0.22
    brier_critical: float = 0.25

    # Feature drift (KS statistic)
    feature_drift_ks: float = 0.1

    # Calibration bin max deviation (absolute)
    calibration_bin_max_deviation: float = 0.15

    # Phase-specific Brier thresholds (slightly relaxed for sparser phases)
    phase_brier_degraded: float = 0.24
    phase_brier_critical: float = 0.28


@dataclass
class CalibrationBin:
    """A single calibration bin tracking expected vs observed probability."""

    bin_lower: float
    bin_upper: float
    bin_midpoint: float
    expected_prob: float  # Mean predicted probability in this bin
    observed_freq: float  # Actual win fraction in this bin
    count: int  # Number of predictions in this bin
    deviation: float  # |expected - observed|
    is_deviated: bool  # deviation > threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bin_range": f"{self.bin_lower:.1f}-{self.bin_upper:.1f}",
            "bin_midpoint": round(self.bin_midpoint, 2),
            "expected_prob": round(self.expected_prob, 4),
            "observed_freq": round(self.observed_freq, 4),
            "count": self.count,
            "deviation": round(self.deviation, 4),
            "is_deviated": self.is_deviated,
        }


@dataclass
class PhasePerformance:
    """Performance metrics for a specific match phase."""

    phase_name: str  # "powerplay", "middle", "death"
    over_range: Tuple[int, int]
    brier_score: float
    n_predictions: int
    accuracy: float  # Binary accuracy (>0.5 threshold)
    mean_predicted: float
    mean_observed: float
    status: str  # "healthy", "degraded", "critical"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phase_name": self.phase_name,
            "over_range": f"{self.over_range[0]}-{self.over_range[1]}",
            "brier_score": round(self.brier_score, 4),
            "n_predictions": self.n_predictions,
            "accuracy": round(self.accuracy, 4),
            "mean_predicted": round(self.mean_predicted, 4),
            "mean_observed": round(self.mean_observed, 4),
            "status": self.status,
        }


@dataclass
class WinProbHealthReport:
    """Complete health report for win probability models."""

    generated_at: str
    model_status: str  # "EXPERIMENTAL"
    innings: str  # "innings1" or "innings2"
    overall_health: str  # "HEALTHY", "DEGRADED", "CRITICAL"
    brier_score: Optional[float]
    calibration_bins: List[Dict[str, Any]]
    phase_performance: List[Dict[str, Any]]
    feature_drift: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]
    baseline_metadata: Optional[Dict[str, Any]]
    thresholds: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "generated_at": self.generated_at,
            "model_status": self.model_status,
            "innings": self.innings,
            "overall_health": self.overall_health,
            "brier_score": (round(self.brier_score, 4) if self.brier_score is not None else None),
            "calibration_bins": self.calibration_bins,
            "phase_performance": self.phase_performance,
            "feature_drift": self.feature_drift,
            "alerts": self.alerts,
            "baseline_metadata": self.baseline_metadata,
            "thresholds": self.thresholds,
        }


# ---------------------------------------------------------------------------
# Win Probability Monitor
# ---------------------------------------------------------------------------
class WinProbMonitor:
    """
    Monitoring framework for win probability models.

    Extends the existing ModelMonitor patterns with win-prob-specific checks.
    Designed for EXPERIMENTAL models (historical replay only).

    Example:
        >>> monitor = WinProbMonitor()
        >>> # Check Brier score
        >>> alerts = monitor.check_brier_score(0.21, "innings1")
        >>> # Check calibration bins
        >>> bins, alerts = monitor.check_calibration_bins(
        ...     predicted_probs, actual_outcomes, "innings1"
        ... )
        >>> # Generate report
        >>> report = monitor.generate_health_report("innings1")
    """

    def __init__(
        self,
        thresholds: Optional[WinProbThresholds] = None,
        log_to_file: bool = True,
    ):
        """
        Initialize the WinProbMonitor.

        Args:
            thresholds: Custom thresholds (uses defaults if None)
            log_to_file: Whether to log to file in addition to console
        """
        self.thresholds = thresholds or WinProbThresholds()
        self.logger = setup_logger("win_prob_monitor", log_to_file=log_to_file)

        # Ensure output directories exist
        WIN_PROB_HEALTH_DIR.mkdir(parents=True, exist_ok=True)
        WIN_PROB_BASELINE_DIR.mkdir(parents=True, exist_ok=True)

        # In-memory state
        self._alerts: List[Alert] = []
        self._brier_history: Dict[str, List[Dict[str, Any]]] = {
            "innings1": [],
            "innings2": [],
        }
        self._calibration_results: Dict[str, List[CalibrationBin]] = {
            "innings1": [],
            "innings2": [],
        }
        self._phase_results: Dict[str, List[PhasePerformance]] = {
            "innings1": [],
            "innings2": [],
        }
        self._drift_results: Dict[str, List[FeatureDriftResult]] = {
            "innings1": [],
            "innings2": [],
        }

        # Underlying ModelMonitor for feature drift (reuses KS logic)
        self._base_monitor = ModelMonitor(
            thresholds=AlertThresholds(feature_drift_ks=self.thresholds.feature_drift_ks),
            log_to_file=log_to_file,
        )

        self.logger.info(
            "WinProbMonitor initialized (model_status=EXPERIMENTAL, "
            "brier_degraded=%.2f, brier_critical=%.2f, ks=%.2f, "
            "cal_bin_deviation=%.2f)",
            self.thresholds.brier_degraded,
            self.thresholds.brier_critical,
            self.thresholds.feature_drift_ks,
            self.thresholds.calibration_bin_max_deviation,
        )

    # ------------------------------------------------------------------
    # 1. Brier Score Monitoring
    # ------------------------------------------------------------------
    def check_brier_score(
        self,
        brier_score: float,
        innings: str,
        window_label: Optional[str] = None,
    ) -> List[Alert]:
        """
        Check Brier score against thresholds.

        The Brier score measures calibration quality: lower is better.
        - < 0.22: healthy
        - 0.22 - 0.25: degraded (WARNING)
        - > 0.25: critical (CRITICAL)

        Args:
            brier_score: Computed Brier score for the evaluation window
            innings: "innings1" or "innings2"
            window_label: Optional label for the evaluation window
                          (e.g., "2025_season", "last_50_matches")

        Returns:
            List of alerts raised
        """
        if innings not in ("innings1", "innings2"):
            raise ValueError(f"innings must be 'innings1' or 'innings2', got '{innings}'")

        alerts: List[Alert] = []
        now = datetime.now().isoformat()

        # Record history
        self._brier_history[innings].append(
            {
                "timestamp": now,
                "brier_score": round(brier_score, 4),
                "window_label": window_label or "default",
            }
        )

        if brier_score > self.thresholds.brier_critical:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                metric="brier_score",
                message=(
                    f"Win prob {innings} Brier score {brier_score:.4f} "
                    f"exceeds critical threshold {self.thresholds.brier_critical}"
                ),
                value=round(brier_score, 4),
                threshold=self.thresholds.brier_critical,
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self.logger.critical(
                "Brier CRITICAL: %s = %.4f > %.2f",
                innings,
                brier_score,
                self.thresholds.brier_critical,
            )
        elif brier_score > self.thresholds.brier_degraded:
            alert = Alert(
                level=AlertLevel.WARNING,
                metric="brier_score",
                message=(
                    f"Win prob {innings} Brier score {brier_score:.4f} "
                    f"exceeds degraded threshold {self.thresholds.brier_degraded}"
                ),
                value=round(brier_score, 4),
                threshold=self.thresholds.brier_degraded,
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self.logger.warning(
                "Brier DEGRADED: %s = %.4f > %.2f",
                innings,
                brier_score,
                self.thresholds.brier_degraded,
            )
        else:
            self.logger.info(
                "Brier HEALTHY: %s = %.4f (thresholds: %.2f / %.2f)",
                innings,
                brier_score,
                self.thresholds.brier_degraded,
                self.thresholds.brier_critical,
            )

        return alerts

    # ------------------------------------------------------------------
    # 2. Feature Distribution Drift
    # ------------------------------------------------------------------
    def check_feature_drift(
        self,
        current_features: np.ndarray,
        baseline_features: np.ndarray,
        feature_names: List[str],
        innings: str,
    ) -> Tuple[List[FeatureDriftResult], List[Alert]]:
        """
        Detect feature distribution drift via KS test.

        Compares current feature distributions against a training baseline
        for each feature independently. Uses the same KS threshold as the
        parent ModelMonitor (default 0.1).

        Args:
            current_features: Array of shape (n_samples, n_features) with
                              current evaluation data
            baseline_features: Array of shape (n_baseline, n_features) with
                               training baseline data
            feature_names: List of feature names matching column order
            innings: "innings1" or "innings2"

        Returns:
            Tuple of (drift results per feature, alerts for drifted features)
        """
        if innings not in ("innings1", "innings2"):
            raise ValueError(f"innings must be 'innings1' or 'innings2', got '{innings}'")

        if current_features.shape[1] != len(feature_names):
            raise ValueError(
                f"Feature count mismatch: data has {current_features.shape[1]} cols, "
                f"but {len(feature_names)} names provided"
            )

        results: List[FeatureDriftResult] = []
        alerts: List[Alert] = []
        ks_threshold = self.thresholds.feature_drift_ks

        for i, feat_name in enumerate(feature_names):
            baseline_vals = baseline_features[:, i]
            current_vals = current_features[:, i]

            # Drop NaN
            baseline_vals = baseline_vals[~np.isnan(baseline_vals)]
            current_vals = current_vals[~np.isnan(current_vals)]

            if len(baseline_vals) < 10 or len(current_vals) < 10:
                self.logger.warning(
                    "Skipping KS test for %s: insufficient samples (baseline=%d, current=%d)",
                    feat_name,
                    len(baseline_vals),
                    len(current_vals),
                )
                continue

            ks_stat, p_value = stats.ks_2samp(baseline_vals, current_vals)
            is_drifted = ks_stat > ks_threshold

            result = FeatureDriftResult(
                feature_name=feat_name,
                ks_statistic=ks_stat,
                p_value=p_value,
                is_drifted=is_drifted,
                baseline_mean=float(np.mean(baseline_vals)),
                current_mean=float(np.mean(current_vals)),
                baseline_std=float(np.std(baseline_vals)),
                current_std=float(np.std(current_vals)),
            )
            results.append(result)

            if is_drifted:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="win_prob_feature_drift",
                    message=(
                        f"Feature drift in {innings}/{feat_name}: KS={ks_stat:.3f} > {ks_threshold}"
                    ),
                    value=round(ks_stat, 4),
                    threshold=ks_threshold,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.warning(
                    "Feature drift: %s/%s KS=%.3f > %.2f",
                    innings,
                    feat_name,
                    ks_stat,
                    ks_threshold,
                )

        self._drift_results[innings] = results
        self.logger.info(
            "Feature drift check for %s: %d features, %d drifted",
            innings,
            len(results),
            sum(1 for r in results if r.is_drifted),
        )
        return results, alerts

    # ------------------------------------------------------------------
    # 3. Calibration Bin Monitoring
    # ------------------------------------------------------------------
    def check_calibration_bins(
        self,
        predicted_probs: np.ndarray,
        actual_outcomes: np.ndarray,
        innings: str,
        n_bins: int = 10,
    ) -> Tuple[List[CalibrationBin], List[Alert]]:
        """
        Monitor calibration across probability bins.

        Divides the [0, 1] probability range into n_bins equal bins and
        compares mean predicted probability to observed win frequency.
        Alerts if any bin deviates more than the configured threshold.

        Args:
            predicted_probs: Array of predicted win probabilities [0, 1]
            actual_outcomes: Array of actual outcomes (1=win, 0=loss)
            innings: "innings1" or "innings2"
            n_bins: Number of calibration bins (default 10)

        Returns:
            Tuple of (list of CalibrationBin, list of alerts)
        """
        if innings not in ("innings1", "innings2"):
            raise ValueError(f"innings must be 'innings1' or 'innings2', got '{innings}'")

        if len(predicted_probs) != len(actual_outcomes):
            raise ValueError(
                f"Length mismatch: predicted={len(predicted_probs)}, actual={len(actual_outcomes)}"
            )

        bins: List[CalibrationBin] = []
        alerts: List[Alert] = []
        max_dev = self.thresholds.calibration_bin_max_deviation
        bin_edges = np.linspace(0.0, 1.0, n_bins + 1)

        for b in range(n_bins):
            lower = bin_edges[b]
            upper = bin_edges[b + 1]
            midpoint = (lower + upper) / 2.0

            # Select predictions in this bin
            if b < n_bins - 1:
                mask = (predicted_probs >= lower) & (predicted_probs < upper)
            else:
                # Last bin is inclusive on the right
                mask = (predicted_probs >= lower) & (predicted_probs <= upper)

            count = int(np.sum(mask))
            if count == 0:
                # Empty bin: no deviation computable
                cal_bin = CalibrationBin(
                    bin_lower=lower,
                    bin_upper=upper,
                    bin_midpoint=midpoint,
                    expected_prob=midpoint,
                    observed_freq=0.0,
                    count=0,
                    deviation=0.0,
                    is_deviated=False,
                )
                bins.append(cal_bin)
                continue

            expected = float(np.mean(predicted_probs[mask]))
            observed = float(np.mean(actual_outcomes[mask]))
            deviation = abs(expected - observed)
            is_deviated = deviation > max_dev

            cal_bin = CalibrationBin(
                bin_lower=lower,
                bin_upper=upper,
                bin_midpoint=midpoint,
                expected_prob=expected,
                observed_freq=observed,
                count=count,
                deviation=deviation,
                is_deviated=is_deviated,
            )
            bins.append(cal_bin)

            if is_deviated:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="calibration_bin_deviation",
                    message=(
                        f"Calibration drift in {innings} bin "
                        f"[{lower:.1f}-{upper:.1f}]: "
                        f"expected={expected:.3f}, observed={observed:.3f}, "
                        f"deviation={deviation:.3f} > {max_dev}"
                    ),
                    value=round(deviation, 4),
                    threshold=max_dev,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.warning(
                    "Calibration bin [%.1f-%.1f] deviated: exp=%.3f obs=%.3f dev=%.3f",
                    lower,
                    upper,
                    expected,
                    observed,
                    deviation,
                )

        self._calibration_results[innings] = bins
        deviated_count = sum(1 for b in bins if b.is_deviated)
        self.logger.info(
            "Calibration bin check for %s: %d bins, %d deviated",
            innings,
            n_bins,
            deviated_count,
        )
        return bins, alerts

    # ------------------------------------------------------------------
    # 4. Phase Performance Monitoring
    # ------------------------------------------------------------------
    def check_phase_performance(
        self,
        predicted_probs: np.ndarray,
        actual_outcomes: np.ndarray,
        over_numbers: np.ndarray,
        innings: str,
    ) -> Tuple[List[PhasePerformance], List[Alert]]:
        """
        Monitor model accuracy across match phases.

        Splits data into powerplay (1-6), middle (7-15), and death (16-20)
        and computes Brier score and accuracy for each phase independently.

        Args:
            predicted_probs: Array of predicted win probabilities
            actual_outcomes: Array of actual outcomes (1=win, 0=loss)
            over_numbers: Array of over numbers (1-20) for each prediction
            innings: "innings1" or "innings2"

        Returns:
            Tuple of (list of PhasePerformance, list of alerts)
        """
        if innings not in ("innings1", "innings2"):
            raise ValueError(f"innings must be 'innings1' or 'innings2', got '{innings}'")

        phases = [
            ("powerplay", PHASE_POWERPLAY),
            ("middle", PHASE_MIDDLE),
            ("death", PHASE_DEATH),
        ]

        results: List[PhasePerformance] = []
        alerts: List[Alert] = []

        for phase_name, (start_over, end_over) in phases:
            mask = (over_numbers >= start_over) & (over_numbers <= end_over)
            n = int(np.sum(mask))

            if n < 10:
                self.logger.warning(
                    "Skipping phase %s for %s: only %d samples",
                    phase_name,
                    innings,
                    n,
                )
                continue

            phase_preds = predicted_probs[mask]
            phase_actuals = actual_outcomes[mask]

            # Brier score: mean((predicted - actual)^2)
            brier = float(np.mean((phase_preds - phase_actuals) ** 2))

            # Binary accuracy at 0.5 threshold
            binary_preds = (phase_preds >= 0.5).astype(int)
            accuracy = float(np.mean(binary_preds == phase_actuals))

            # Determine status
            if brier > self.thresholds.phase_brier_critical:
                status = "critical"
            elif brier > self.thresholds.phase_brier_degraded:
                status = "degraded"
            else:
                status = "healthy"

            perf = PhasePerformance(
                phase_name=phase_name,
                over_range=(start_over, end_over),
                brier_score=brier,
                n_predictions=n,
                accuracy=accuracy,
                mean_predicted=float(np.mean(phase_preds)),
                mean_observed=float(np.mean(phase_actuals)),
                status=status,
            )
            results.append(perf)

            if status == "critical":
                alert = Alert(
                    level=AlertLevel.CRITICAL,
                    metric="phase_brier_score",
                    message=(
                        f"Win prob {innings} {phase_name} phase Brier={brier:.4f} "
                        f"exceeds critical threshold "
                        f"{self.thresholds.phase_brier_critical}"
                    ),
                    value=round(brier, 4),
                    threshold=self.thresholds.phase_brier_critical,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.critical(
                    "Phase CRITICAL: %s/%s Brier=%.4f",
                    innings,
                    phase_name,
                    brier,
                )
            elif status == "degraded":
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="phase_brier_score",
                    message=(
                        f"Win prob {innings} {phase_name} phase Brier={brier:.4f} "
                        f"exceeds degraded threshold "
                        f"{self.thresholds.phase_brier_degraded}"
                    ),
                    value=round(brier, 4),
                    threshold=self.thresholds.phase_brier_degraded,
                )
                alerts.append(alert)
                self._alerts.append(alert)
                self.logger.warning(
                    "Phase DEGRADED: %s/%s Brier=%.4f",
                    innings,
                    phase_name,
                    brier,
                )
            else:
                self.logger.info(
                    "Phase HEALTHY: %s/%s Brier=%.4f, accuracy=%.3f",
                    innings,
                    phase_name,
                    brier,
                    accuracy,
                )

        self._phase_results[innings] = results
        return results, alerts

    # ------------------------------------------------------------------
    # 5. Report Generation
    # ------------------------------------------------------------------
    def generate_health_report(
        self,
        innings: str,
        save_to_file: bool = True,
    ) -> WinProbHealthReport:
        """
        Generate a comprehensive health report for a win probability model.

        Aggregates all check results (Brier, calibration, phase, drift)
        into a single JSON-serializable report.

        Args:
            innings: "innings1" or "innings2"
            save_to_file: Save report JSON to WIN_PROB_HEALTH_DIR

        Returns:
            WinProbHealthReport instance
        """
        if innings not in ("innings1", "innings2"):
            raise ValueError(f"innings must be 'innings1' or 'innings2', got '{innings}'")

        now = datetime.now()

        # Latest Brier score
        brier_history = self._brier_history.get(innings, [])
        latest_brier = brier_history[-1]["brier_score"] if brier_history else None

        # Calibration bins
        cal_bins = self._calibration_results.get(innings, [])
        cal_dicts = [b.to_dict() for b in cal_bins]

        # Phase performance
        phase_results = self._phase_results.get(innings, [])
        phase_dicts = [p.to_dict() for p in phase_results]

        # Feature drift
        drift_results = self._drift_results.get(innings, [])
        drift_dicts = [r.to_dict() for r in drift_results]

        # Alerts for this innings
        innings_alerts = [a for a in self._alerts if innings in a.message]
        alert_dicts = [a.to_dict() for a in innings_alerts]

        # Determine overall health
        critical_count = sum(1 for a in innings_alerts if a.level == AlertLevel.CRITICAL)
        warning_count = sum(1 for a in innings_alerts if a.level == AlertLevel.WARNING)

        if critical_count > 0:
            overall_health = "CRITICAL"
        elif warning_count > 0:
            overall_health = "DEGRADED"
        else:
            overall_health = "HEALTHY"

        # Baseline metadata (check on-disk)
        baseline_meta = self._load_baseline_metadata(innings)

        report = WinProbHealthReport(
            generated_at=now.isoformat(),
            model_status="EXPERIMENTAL",
            innings=innings,
            overall_health=overall_health,
            brier_score=latest_brier,
            calibration_bins=cal_dicts,
            phase_performance=phase_dicts,
            feature_drift=drift_dicts,
            alerts=alert_dicts,
            baseline_metadata=baseline_meta,
            thresholds={
                "brier_degraded": self.thresholds.brier_degraded,
                "brier_critical": self.thresholds.brier_critical,
                "feature_drift_ks": self.thresholds.feature_drift_ks,
                "calibration_bin_max_deviation": (self.thresholds.calibration_bin_max_deviation),
                "phase_brier_degraded": self.thresholds.phase_brier_degraded,
                "phase_brier_critical": self.thresholds.phase_brier_critical,
            },
        )

        if save_to_file:
            filename = f"win_prob_{innings}_health_{now.strftime('%Y%m%d_%H%M%S')}.json"
            report_path = WIN_PROB_HEALTH_DIR / filename
            with open(report_path, "w") as f:
                json.dump(report.to_dict(), f, indent=2)
            self.logger.info("Health report saved to: %s", report_path)

        self.logger.info(
            "Win prob %s health report: status=%s, brier=%s, "
            "%d calibration bins, %d phase checks, %d drift checks, "
            "%d alerts (%d critical, %d warning)",
            innings,
            overall_health,
            f"{latest_brier:.4f}" if latest_brier is not None else "N/A",
            len(cal_bins),
            len(phase_results),
            len(drift_results),
            len(innings_alerts),
            critical_count,
            warning_count,
        )

        return report

    # ------------------------------------------------------------------
    # Baseline Management
    # ------------------------------------------------------------------
    def save_baseline(
        self,
        feature_stats: Dict[str, Dict[str, float]],
        innings: str,
        n_samples: int,
        season_range: str = "2008-2025",
        created_by: str = "Ime Udoka",
        notes: Optional[str] = None,
    ) -> Path:
        """
        Save a baseline feature distribution snapshot to disk.

        The baseline is a JSON file containing per-feature summary statistics
        (mean, std, min, max, median, q25, q75). It does NOT store raw data.

        Args:
            feature_stats: Dict mapping feature name to stat dict
                           e.g. {"run_rate": {"mean": 7.5, "std": 2.1, ...}}
            innings: "innings1" or "innings2"
            n_samples: Number of training samples used
            season_range: IPL season range covered
            created_by: Agent/person creating baseline
            notes: Optional notes

        Returns:
            Path to saved baseline file
        """
        now = datetime.now()
        baseline = {
            "metadata": {
                "innings": innings,
                "created_at": now.isoformat(),
                "created_by": created_by,
                "n_samples": n_samples,
                "season_range": season_range,
                "model_status": "EXPERIMENTAL",
                "notes": notes,
                "feature_count": len(feature_stats),
            },
            "feature_distributions": feature_stats,
        }

        filename = f"win_prob_{innings}_baseline.json"
        baseline_path = WIN_PROB_BASELINE_DIR / filename
        with open(baseline_path, "w") as f:
            json.dump(baseline, f, indent=2)

        self.logger.info(
            "Baseline saved: %s (%d features, %d samples, %s)",
            baseline_path,
            len(feature_stats),
            n_samples,
            season_range,
        )
        return baseline_path

    def _load_baseline_metadata(self, innings: str) -> Optional[Dict[str, Any]]:
        """Load baseline metadata from disk if it exists."""
        filename = f"win_prob_{innings}_baseline.json"
        baseline_path = WIN_PROB_BASELINE_DIR / filename
        if not baseline_path.exists():
            return None
        try:
            with open(baseline_path) as f:
                data = json.load(f)
            return data.get("metadata")
        except (json.JSONDecodeError, KeyError):
            self.logger.warning("Failed to load baseline metadata from %s", baseline_path)
            return None

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        innings: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts, optionally filtered.

        Args:
            level: Filter by alert level
            innings: Filter by innings ("innings1" or "innings2")
            limit: Maximum alerts to return

        Returns:
            List of alert dictionaries
        """
        filtered = self._alerts
        if level:
            filtered = [a for a in filtered if a.level == level]
        if innings:
            filtered = [a for a in filtered if innings in a.message]
        return [a.to_dict() for a in filtered[-limit:]]

    def clear(self) -> None:
        """Clear all in-memory state."""
        self._alerts.clear()
        for key in self._brier_history:
            self._brier_history[key].clear()
        for key in self._calibration_results:
            self._calibration_results[key].clear()
        for key in self._phase_results:
            self._phase_results[key].clear()
        for key in self._drift_results:
            self._drift_results[key].clear()
        self.logger.info("WinProbMonitor state cleared")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
def create_win_prob_monitor(log_to_file: bool = True) -> WinProbMonitor:
    """
    Factory function to create a WinProbMonitor with default settings.

    Returns:
        Configured WinProbMonitor instance
    """
    return WinProbMonitor(
        thresholds=WinProbThresholds(),
        log_to_file=log_to_file,
    )


# ---------------------------------------------------------------------------
# Baseline Template Generator
# ---------------------------------------------------------------------------
def generate_baseline_templates() -> None:
    """
    Generate baseline template files for both innings models.

    Creates template JSON files at outputs/monitoring/win_prob_baseline/
    with placeholder statistics. These templates document the expected
    schema and should be populated with actual training distribution
    data after model training.
    """
    WIN_PROB_BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    # Template feature stats (placeholder values based on typical IPL T20 ranges)
    template_stats: Dict[str, Dict[str, float]] = {
        "over_number": {
            "mean": 10.5,
            "std": 5.8,
            "min": 1.0,
            "max": 20.0,
            "median": 10.0,
            "q25": 5.0,
            "q75": 16.0,
        },
        "ball_number": {
            "mean": 3.5,
            "std": 1.7,
            "min": 1.0,
            "max": 6.0,
            "median": 3.0,
            "q25": 2.0,
            "q75": 5.0,
        },
        "wickets_fallen": {
            "mean": 3.2,
            "std": 2.5,
            "min": 0.0,
            "max": 10.0,
            "median": 3.0,
            "q25": 1.0,
            "q75": 5.0,
        },
        "current_score": {
            "mean": 85.0,
            "std": 55.0,
            "min": 0.0,
            "max": 260.0,
            "median": 78.0,
            "q25": 38.0,
            "q75": 130.0,
        },
        "run_rate": {
            "mean": 7.8,
            "std": 2.5,
            "min": 0.0,
            "max": 36.0,
            "median": 7.5,
            "q25": 6.0,
            "q75": 9.5,
        },
        "required_run_rate": {
            "mean": 8.5,
            "std": 4.0,
            "min": 0.0,
            "max": 54.0,
            "median": 7.8,
            "q25": 6.0,
            "q75": 10.5,
        },
        "scoring_rate_last5": {
            "mean": 8.0,
            "std": 3.5,
            "min": 0.0,
            "max": 30.0,
            "median": 7.5,
            "q25": 5.5,
            "q75": 10.0,
        },
        "wickets_last5": {
            "mean": 0.8,
            "std": 1.0,
            "min": 0.0,
            "max": 5.0,
            "median": 0.0,
            "q25": 0.0,
            "q75": 1.0,
        },
        "innings_progress": {
            "mean": 0.50,
            "std": 0.29,
            "min": 0.0,
            "max": 1.0,
            "median": 0.50,
            "q25": 0.25,
            "q75": 0.75,
        },
        "runs_remaining": {
            "mean": 80.0,
            "std": 50.0,
            "min": 0.0,
            "max": 260.0,
            "median": 75.0,
            "q25": 35.0,
            "q75": 120.0,
        },
        "balls_remaining": {
            "mean": 60.0,
            "std": 35.0,
            "min": 0.0,
            "max": 120.0,
            "median": 60.0,
            "q25": 30.0,
            "q75": 90.0,
        },
        "partnership_runs": {
            "mean": 25.0,
            "std": 28.0,
            "min": 0.0,
            "max": 200.0,
            "median": 15.0,
            "q25": 5.0,
            "q75": 35.0,
        },
        "partnership_balls": {
            "mean": 18.0,
            "std": 20.0,
            "min": 0.0,
            "max": 120.0,
            "median": 11.0,
            "q25": 3.0,
            "q75": 25.0,
        },
    }

    monitor = WinProbMonitor(log_to_file=False)

    for innings in ("innings1", "innings2"):
        notes = (
            f"TEMPLATE BASELINE for {innings}. "
            "Placeholder statistics based on typical IPL T20 ranges. "
            "Replace with actual training distribution data after "
            "model training (TKT-207 outputs)."
        )
        monitor.save_baseline(
            feature_stats=template_stats,
            innings=innings,
            n_samples=0,
            season_range="2008-2025",
            created_by="Ime Udoka (template)",
            notes=notes,
        )

    print(f"Baseline templates generated at: {WIN_PROB_BASELINE_DIR}")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------
def run_win_prob_health_check(verbose: bool = False) -> Dict[str, Any]:
    """
    Run win probability health checks and return combined report.

    This is the integration entrypoint called by run_health_check.py.
    Since models are EXPERIMENTAL (no live predictions), this check:
    - Verifies baseline files exist
    - Validates model artifacts are present
    - Reports model status and readiness
    - Does NOT load or execute models

    Args:
        verbose: Print detailed output

    Returns:
        Combined health status dict for both innings models
    """
    print("\n   --- Win Probability Model Health ---")
    print("   Model Status: EXPERIMENTAL (historical replay only)")

    results: Dict[str, Any] = {
        "model_status": "EXPERIMENTAL",
        "timestamp": datetime.now().isoformat(),
        "innings1": {},
        "innings2": {},
        "alerts": [],
    }

    alerts: List[Alert] = []

    for innings in ("innings1", "innings2"):
        innings_label = innings.replace("innings", "Innings ")

        # Check model artifacts
        lgbm_path = MODELS_DIR / f"win_prob_{innings}_v1.lgbm"
        calibrated_path = MODELS_DIR / f"win_prob_{innings}_v1_calibrated.joblib"

        lgbm_exists = lgbm_path.exists()
        calibrated_exists = calibrated_path.exists()

        if lgbm_exists and calibrated_exists:
            status_icon = "OK"
            print(f"   {innings_label}: model artifacts found")
        elif lgbm_exists or calibrated_exists:
            status_icon = "PARTIAL"
            print(f"   {innings_label}: partial model artifacts")
            alert = Alert(
                level=AlertLevel.WARNING,
                metric="model_artifact",
                message=f"Win prob {innings} has partial model artifacts",
                value="partial",
                threshold="both lgbm + calibrated",
            )
            alerts.append(alert)
        else:
            status_icon = "MISSING"
            print(f"   {innings_label}: model artifacts NOT found")
            alert = Alert(
                level=AlertLevel.INFO,
                metric="model_artifact",
                message=(
                    f"Win prob {innings} model artifacts not found at "
                    f"{MODELS_DIR}. Expected after TKT-207 completion."
                ),
                value="missing",
                threshold="present",
            )
            alerts.append(alert)

        # Check baseline
        baseline_path = WIN_PROB_BASELINE_DIR / f"win_prob_{innings}_baseline.json"
        baseline_exists = baseline_path.exists()
        baseline_meta = None

        if baseline_exists:
            try:
                with open(baseline_path) as f:
                    baseline_data = json.load(f)
                baseline_meta = baseline_data.get("metadata", {})
                n_features = baseline_meta.get("feature_count", 0)
                print(
                    f"   {innings_label} baseline: {n_features} features "
                    f"({baseline_meta.get('season_range', 'unknown')})"
                )
            except (json.JSONDecodeError, KeyError):
                print(f"   {innings_label} baseline: CORRUPT")
                alert = Alert(
                    level=AlertLevel.WARNING,
                    metric="baseline_integrity",
                    message=f"Win prob {innings} baseline file is corrupt",
                    value="corrupt",
                    threshold="valid JSON",
                )
                alerts.append(alert)
        else:
            print(f"   {innings_label} baseline: not yet created")

        results[innings] = {
            "model_artifact_status": status_icon,
            "lgbm_exists": lgbm_exists,
            "calibrated_exists": calibrated_exists,
            "baseline_exists": baseline_exists,
            "baseline_metadata": baseline_meta,
        }

    # Overall status
    critical_count = sum(1 for a in alerts if a.level == AlertLevel.CRITICAL)
    warning_count = sum(1 for a in alerts if a.level == AlertLevel.WARNING)

    if critical_count > 0:
        results["overall_health"] = "CRITICAL"
    elif warning_count > 0:
        results["overall_health"] = "DEGRADED"
    else:
        results["overall_health"] = "HEALTHY"

    results["alerts"] = [a.to_dict() for a in alerts]

    print(f"   Overall: {results['overall_health']}")

    if verbose and alerts:
        for a in alerts:
            print(f"      [{a.level.value.upper()}] {a.message}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if "--generate-baselines" in sys.argv:
        generate_baseline_templates()
    elif "--health-check" in sys.argv:
        verbose = "--verbose" in sys.argv or "-v" in sys.argv
        result = run_win_prob_health_check(verbose=verbose)
        print(json.dumps(result, indent=2))
    else:
        print("Win Probability Model Monitoring")
        print("=" * 50)
        print("Usage:")
        print("  --generate-baselines  Create baseline template files")
        print("  --health-check        Run health check")
        print("  --verbose / -v        Verbose output")
        print()
        print("Programmatic usage:")
        print("  from scripts.ml_ops.win_prob_monitoring import WinProbMonitor")
        print("  monitor = WinProbMonitor()")
        print("  monitor.check_brier_score(0.19, 'innings1')")
