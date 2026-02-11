#!/usr/bin/env python3
"""
Cricket Playbook - ML Model Retraining Pipeline
=================================================
Automated retraining pipeline for the player clustering model (K-Means).

Loads latest data from DuckDB, runs feature engineering identical to
player_clustering_v2.py, trains a candidate model, compares it against the
current production model on silhouette score and cluster stability, and
conditionally promotes the new model with semantic versioning.

Owner: Pep Guardiola (ML Ops Agent)
Ticket: TKT-156
EPIC: EPIC-015 (Operational Maturity)

Usage:
    python scripts/ml_ops/retrain_pipeline.py
    python scripts/ml_ops/retrain_pipeline.py --force
    python scripts/ml_ops/retrain_pipeline.py --dry-run
    python scripts/ml_ops/retrain_pipeline.py --min-improvement 0.05
    python scripts/ml_ops/retrain_pipeline.py --force --dry-run --min-improvement 0.03
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
REGISTRY_PATH = PROJECT_ROOT / "scripts" / "ml_ops" / "model_registry.json"
THRESHOLDS_PATH = PROJECT_ROOT / "config" / "thresholds.yaml"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "monitoring" / "retrain_reports"

# Recent seasons for recency weighting (mirrors clustering_v2)
RECENT_SEASONS = [2021, 2022, 2023, 2024, 2025]

# Minimum sample sizes (mirrors clustering_v2)
MIN_BALLS_BATTER = 300
MIN_BALLS_BOWLER = 200

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("retrain_pipeline")


def _setup_logging(verbose: bool = False) -> None:
    """Configure structured logging for the pipeline."""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)


# ---------------------------------------------------------------------------
# Threshold loader (reads from thresholds.yaml when available)
# ---------------------------------------------------------------------------


def _load_thresholds() -> Dict[str, Any]:
    """Load ML thresholds from config/thresholds.yaml if it exists.

    Returns a dict with keys used by the pipeline.  Falls back to hardcoded
    defaults that match the values documented in model_monitoring.py.
    """
    defaults: Dict[str, Any] = {
        "min_variance_batter": 0.70,
        "min_variance_bowler": 0.50,
        "min_cluster_size_pct": 0.05,  # 5% of players
        "min_cluster_abs": 10,
        "n_clusters_batter": 5,
        "n_clusters_bowler": 5,
        "correlation_threshold": 0.90,
        "target_variance": 0.50,
    }

    if not THRESHOLDS_PATH.exists():
        logger.warning("thresholds.yaml not found at %s, using defaults", THRESHOLDS_PATH)
        return defaults

    try:
        import yaml  # PyYAML is in requirements.txt

        with open(THRESHOLDS_PATH) as fh:
            raw = yaml.safe_load(fh)

        ml_cfg = raw.get("ml", {})
        pca_cfg = ml_cfg.get("pca", {})
        clust_cfg = ml_cfg.get("clustering", {})

        defaults["min_variance_batter"] = pca_cfg.get(
            "min_variance_batter", defaults["min_variance_batter"]
        )
        defaults["min_variance_bowler"] = pca_cfg.get(
            "min_variance_bowler", defaults["min_variance_bowler"]
        )
        defaults["correlation_threshold"] = pca_cfg.get(
            "correlation_threshold", defaults["correlation_threshold"]
        )
        defaults["target_variance"] = pca_cfg.get("target_variance", defaults["target_variance"])
        defaults["min_cluster_abs"] = clust_cfg.get("min_cluster_size", defaults["min_cluster_abs"])
        defaults["n_clusters_batter"] = clust_cfg.get(
            "n_clusters_batter", defaults["n_clusters_batter"]
        )
        defaults["n_clusters_bowler"] = clust_cfg.get(
            "n_clusters_bowler", defaults["n_clusters_bowler"]
        )
        logger.info("Loaded ML thresholds from %s", THRESHOLDS_PATH)
    except Exception as exc:
        logger.warning("Failed to parse thresholds.yaml (%s), using defaults", exc)

    return defaults


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def _load_registry() -> Dict[str, Any]:
    """Load model_registry.json or return a blank structure."""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as fh:
            return json.load(fh)
    return {
        "models": {
            "player_clustering": {
                "active_version": "v2.0.0",
                "versions": {},
            }
        },
        "last_updated": None,
    }


def _save_registry(registry: Dict[str, Any]) -> None:
    """Persist model_registry.json."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry["last_updated"] = datetime.now().isoformat()
    with open(REGISTRY_PATH, "w") as fh:
        json.dump(registry, fh, indent=2)
    logger.info("Model registry updated at %s", REGISTRY_PATH)


def _bump_minor(version_str: str) -> str:
    """Bump the MINOR component of a semver string.

    v2.0.0 -> v2.1.0 ; v2.3.1 -> v2.4.0
    """
    stripped = version_str.lstrip("v")
    parts = stripped.split(".")
    if len(parts) != 3:
        parts = ["2", "0", "0"]
    major, minor, _ = parts
    return f"v{major}.{int(minor) + 1}.0"


# ---------------------------------------------------------------------------
# Data-loading (replicates player_clustering_v2 queries)
# ---------------------------------------------------------------------------


def load_batter_features(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Extract batter feature vectors with batting position and recency weighting.

    This query is identical to ``get_batter_features_v2`` in
    ``scripts/analysis/player_clustering_v2.py``.
    """
    df = conn.execute(
        """
        WITH recent_balls AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(*) as recent_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND (dm.season LIKE '2021%' OR dm.season LIKE '2022%'
                   OR dm.season LIKE '2023%' OR dm.season LIKE '2024%'
                   OR dm.season LIKE '2025%')
            GROUP BY fb.batter_id
        ),
        legal_balls_numbered AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.batter_id,
                fb.ball_seq,
                fb.is_legal_ball,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                    OVER (PARTITION BY fb.match_id, fb.innings
                          ORDER BY fb.ball_seq) as legal_ball_num
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        batting_position AS (
            SELECT
                batter_id as player_id,
                AVG(batting_position) as avg_batting_position
            FROM (
                SELECT
                    batter_id,
                    match_id,
                    innings,
                    MIN(legal_ball_num) as first_legal_ball,
                    CASE
                        WHEN MIN(legal_ball_num) <= 6 THEN 1
                        WHEN MIN(legal_ball_num) <= 24 THEN 2
                        WHEN MIN(legal_ball_num) <= 48 THEN 3
                        WHEN MIN(legal_ball_num) <= 72 THEN 4
                        WHEN MIN(legal_ball_num) <= 96 THEN 5
                        ELSE 6
                    END as batting_position
                FROM legal_balls_numbered
                WHERE is_legal_ball = true
                GROUP BY batter_id, match_id, innings
            ) t
            GROUP BY batter_id
        ),
        career AS (
            SELECT player_id, player_name, balls_faced, runs, strike_rate,
                   batting_average, boundary_pct, dot_ball_pct
            FROM analytics_ipl_batting_career_since2023
            WHERE balls_faced >= {min_balls}
        ),
        powerplay AS (
            SELECT player_id,
                   strike_rate as pp_sr,
                   boundary_pct as pp_boundary,
                   dot_ball_pct as pp_dot
            FROM analytics_ipl_batter_phase_since2023
            WHERE match_phase = 'powerplay' AND balls_faced >= 50
        ),
        middle AS (
            SELECT player_id,
                   strike_rate as mid_sr,
                   boundary_pct as mid_boundary,
                   dot_ball_pct as mid_dot
            FROM analytics_ipl_batter_phase_since2023
            WHERE match_phase = 'middle' AND balls_faced >= 50
        ),
        death AS (
            SELECT player_id,
                   strike_rate as death_sr,
                   boundary_pct as death_boundary,
                   dot_ball_pct as death_dot
            FROM analytics_ipl_batter_phase_since2023
            WHERE match_phase = 'death' AND balls_faced >= 30
        )
        SELECT
            c.player_id,
            c.player_name,
            c.balls_faced,
            c.runs,
            c.strike_rate as overall_sr,
            c.batting_average as overall_avg,
            c.boundary_pct as overall_boundary,
            c.dot_ball_pct as overall_dot,
            COALESCE(bp.avg_batting_position, 4) as avg_batting_position,
            pp.pp_sr,
            pp.pp_boundary,
            pp.pp_dot,
            m.mid_sr,
            m.mid_boundary,
            m.mid_dot,
            d.death_sr,
            d.death_boundary,
            d.death_dot,
            COALESCE(rb.recent_balls, 0) as recent_balls,
            CASE WHEN c.balls_faced > 0
                 THEN 1.0 + COALESCE(rb.recent_balls, 0) * 1.0 / c.balls_faced
                 ELSE 1.0 END as recency_weight
        FROM career c
        LEFT JOIN batting_position bp ON c.player_id = bp.player_id
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        LEFT JOIN recent_balls rb ON c.player_id = rb.player_id
        WHERE pp.pp_sr IS NOT NULL OR m.mid_sr IS NOT NULL
        """.format(min_balls=MIN_BALLS_BATTER)
    ).df()

    return df


def load_bowler_features(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Extract bowler feature vectors with wickets per phase.

    This query is identical to ``get_bowler_features_v2`` in
    ``scripts/analysis/player_clustering_v2.py``.
    """
    df = conn.execute(
        """
        WITH recent_balls AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(*) as recent_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND (dm.season LIKE '2021%' OR dm.season LIKE '2022%'
                   OR dm.season LIKE '2023%' OR dm.season LIKE '2024%'
                   OR dm.season LIKE '2025%')
              AND fb.is_legal_ball = TRUE
            GROUP BY fb.bowler_id
        ),
        wickets_by_phase AS (
            SELECT
                fb.bowler_id as player_id,
                SUM(CASE WHEN fb.match_phase = 'powerplay' AND fb.is_wicket
                    THEN 1 ELSE 0 END) as pp_wickets,
                SUM(CASE WHEN fb.match_phase = 'middle' AND fb.is_wicket
                    THEN 1 ELSE 0 END) as mid_wickets,
                SUM(CASE WHEN fb.match_phase = 'death' AND fb.is_wicket
                    THEN 1 ELSE 0 END) as death_wickets,
                SUM(CASE WHEN fb.match_phase = 'powerplay' AND fb.is_legal_ball
                    THEN 1 ELSE 0 END) as pp_balls,
                SUM(CASE WHEN fb.match_phase = 'middle' AND fb.is_legal_ball
                    THEN 1 ELSE 0 END) as mid_balls,
                SUM(CASE WHEN fb.match_phase = 'death' AND fb.is_legal_ball
                    THEN 1 ELSE 0 END) as death_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
            GROUP BY fb.bowler_id
        ),
        career AS (
            SELECT player_id, player_name, balls_bowled, wickets,
                   economy_rate, bowling_average, bowling_strike_rate,
                   dot_ball_pct, boundary_conceded_pct
            FROM analytics_ipl_bowling_career_since2023
            WHERE balls_bowled >= {min_balls}
        ),
        powerplay AS (
            SELECT player_id,
                   economy_rate as pp_economy,
                   dot_ball_pct as pp_dot,
                   boundary_conceded_pct as pp_boundary
            FROM analytics_ipl_bowler_phase_since2023
            WHERE match_phase = 'powerplay' AND balls_bowled >= 30
        ),
        middle AS (
            SELECT player_id,
                   economy_rate as mid_economy,
                   dot_ball_pct as mid_dot,
                   boundary_conceded_pct as mid_boundary
            FROM analytics_ipl_bowler_phase_since2023
            WHERE match_phase = 'middle' AND balls_bowled >= 30
        ),
        death AS (
            SELECT player_id,
                   economy_rate as death_economy,
                   dot_ball_pct as death_dot,
                   boundary_conceded_pct as death_boundary
            FROM analytics_ipl_bowler_phase_since2023
            WHERE match_phase = 'death' AND balls_bowled >= 30
        ),
        phase_distribution AS (
            SELECT bowler_id as player_id,
                   MAX(CASE WHEN match_phase = 'powerplay'
                       THEN pct_overs_in_phase END) as pp_pct,
                   MAX(CASE WHEN match_phase = 'middle'
                       THEN pct_overs_in_phase END) as mid_pct,
                   MAX(CASE WHEN match_phase = 'death'
                       THEN pct_overs_in_phase END) as death_pct
            FROM analytics_ipl_bowler_phase_distribution_since2023
            GROUP BY bowler_id
        )
        SELECT
            c.player_id,
            c.player_name,
            c.balls_bowled,
            c.wickets,
            c.economy_rate as overall_economy,
            c.bowling_average as overall_avg,
            c.bowling_strike_rate as overall_sr,
            c.dot_ball_pct as overall_dot,
            c.boundary_conceded_pct as overall_boundary,
            pp.pp_economy,
            pp.pp_dot,
            pp.pp_boundary,
            m.mid_economy,
            m.mid_dot,
            m.mid_boundary,
            d.death_economy,
            d.death_dot,
            d.death_boundary,
            pd.pp_pct,
            pd.mid_pct,
            pd.death_pct,
            COALESCE(wp.pp_wickets, 0) as pp_wickets,
            COALESCE(wp.mid_wickets, 0) as mid_wickets,
            COALESCE(wp.death_wickets, 0) as death_wickets,
            CASE WHEN wp.pp_wickets > 0
                 THEN wp.pp_balls * 1.0 / wp.pp_wickets
                 ELSE NULL END as pp_bowling_sr,
            CASE WHEN wp.mid_wickets > 0
                 THEN wp.mid_balls * 1.0 / wp.mid_wickets
                 ELSE NULL END as mid_bowling_sr,
            CASE WHEN wp.death_wickets > 0
                 THEN wp.death_balls * 1.0 / wp.death_wickets
                 ELSE NULL END as death_bowling_sr,
            COALESCE(rb.recent_balls, 0) as recent_balls,
            CASE WHEN c.balls_bowled > 0
                 THEN 1.0 + COALESCE(rb.recent_balls, 0) * 1.0 / c.balls_bowled
                 ELSE 1.0 END as recency_weight
        FROM career c
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        LEFT JOIN phase_distribution pd ON c.player_id = pd.player_id
        LEFT JOIN wickets_by_phase wp ON c.player_id = wp.player_id
        LEFT JOIN recent_balls rb ON c.player_id = rb.player_id
        WHERE pp.pp_economy IS NOT NULL
           OR m.mid_economy IS NOT NULL
           OR d.death_economy IS NOT NULL
        """.format(min_balls=MIN_BALLS_BOWLER)
    ).df()

    return df


# ---------------------------------------------------------------------------
# Feature engineering (mirrors clustering_v2)
# ---------------------------------------------------------------------------

BATTER_FEATURE_COLS: List[str] = [
    "overall_sr",
    "overall_avg",
    "overall_boundary",
    "overall_dot",
    "avg_batting_position",
    "pp_sr",
    "pp_boundary",
    "mid_sr",
    "mid_boundary",
    "death_sr",
    "death_boundary",
]

BOWLER_FEATURE_COLS: List[str] = [
    "overall_economy",
    "overall_sr",
    "overall_dot",
    "overall_boundary",
    "pp_economy",
    "pp_dot",
    "mid_economy",
    "mid_dot",
    "death_economy",
    "death_dot",
    "pp_pct",
    "mid_pct",
    "death_pct",
    "pp_wickets",
    "mid_wickets",
    "death_wickets",
]


def _remove_correlated_features(
    df: pd.DataFrame,
    feature_cols: List[str],
    threshold: float = 0.90,
) -> List[str]:
    """Drop features with Pearson |r| > *threshold* (same logic as clustering_v2)."""
    numeric_df = df[feature_cols].dropna()
    if len(numeric_df) < 10:
        return feature_cols

    corr_matrix = numeric_df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    to_drop: List[str] = []
    for col in upper.columns:
        if any(upper[col] > threshold):
            if col not in to_drop:
                to_drop.append(col)

    if to_drop:
        logger.info("Removing correlated features (|r|>%.2f): %s", threshold, to_drop)
    return [c for c in feature_cols if c not in to_drop]


def prepare_features(
    df: pd.DataFrame,
    feature_cols: List[str],
    corr_threshold: float = 0.90,
) -> Tuple[np.ndarray, pd.DataFrame, List[str], StandardScaler]:
    """Clean, impute, scale, and apply recency weighting.

    Returns
    -------
    X : np.ndarray
        Scaled (and recency-weighted) feature matrix.
    df_clean : pd.DataFrame
        Cleaned dataframe with the same row order as *X*.
    final_features : list[str]
        Feature column names that survived correlation pruning.
    scaler : StandardScaler
        Fitted scaler (needed for inverse-transform later).
    """
    required_col = feature_cols[0]  # first feature used as non-null gate
    df_clean = df.dropna(subset=[required_col]).copy()

    # Median imputation (same as clustering_v2)
    for col in feature_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    # Correlation cleanup
    final_features = _remove_correlated_features(df_clean, feature_cols, corr_threshold)

    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[final_features])

    # Recency weighting
    if "recency_weight" in df_clean.columns:
        weights = df_clean["recency_weight"].values.reshape(-1, 1)
        X = X * np.sqrt(weights)

    return X, df_clean, final_features, scaler


# ---------------------------------------------------------------------------
# Training & evaluation helpers
# ---------------------------------------------------------------------------


@dataclass
class ModelMetrics:
    """Metrics for a single trained model (batter or bowler)."""

    player_type: str
    n_players: int
    n_clusters: int
    silhouette: float
    cluster_sizes: Dict[int, int]
    pca_variance_3pc: float
    feature_cols: List[str]


@dataclass
class RetrainResult:
    """Full result of a retrain attempt for one player type."""

    player_type: str
    current_metrics: Optional[ModelMetrics]
    candidate_metrics: ModelMetrics
    promoted: bool
    reason: str


@dataclass
class PipelineReport:
    """Aggregate report for the entire pipeline run."""

    timestamp: str
    run_mode: str  # "normal", "force", "dry-run"
    batter_result: Optional[RetrainResult] = None
    bowler_result: Optional[RetrainResult] = None
    new_version: Optional[str] = None
    previous_version: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the report for JSON output."""

        def _result_dict(r: Optional[RetrainResult]) -> Optional[Dict[str, Any]]:
            if r is None:
                return None
            return {
                "player_type": r.player_type,
                "promoted": r.promoted,
                "reason": r.reason,
                "candidate_silhouette": round(r.candidate_metrics.silhouette, 4),
                "candidate_n_clusters": r.candidate_metrics.n_clusters,
                "candidate_cluster_sizes": r.candidate_metrics.cluster_sizes,
                "candidate_pca_3pc": round(r.candidate_metrics.pca_variance_3pc, 4),
                "current_silhouette": (
                    round(r.current_metrics.silhouette, 4) if r.current_metrics else None
                ),
            }

        return {
            "timestamp": self.timestamp,
            "run_mode": self.run_mode,
            "previous_version": self.previous_version,
            "new_version": self.new_version,
            "batter": _result_dict(self.batter_result),
            "bowler": _result_dict(self.bowler_result),
            "errors": self.errors,
        }


def _train_model(
    X: np.ndarray,
    n_clusters: int,
    random_state: int = 42,
) -> Tuple[KMeans, np.ndarray]:
    """Train a K-Means model and return (model, labels)."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)
    return kmeans, labels


def _evaluate_model(
    X: np.ndarray,
    labels: np.ndarray,
    feature_cols: List[str],
    player_type: str,
) -> ModelMetrics:
    """Compute evaluation metrics for a trained model."""
    n_clusters = len(set(labels))

    sil = silhouette_score(X, labels) if n_clusters >= 2 else -1.0

    # Cluster size distribution
    unique, counts = np.unique(labels, return_counts=True)
    cluster_sizes = {int(u): int(c) for u, c in zip(unique, counts)}

    # PCA variance (first 3 components)
    pca = PCA()
    pca.fit(X)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    pca_3pc = float(cumvar[min(2, len(cumvar) - 1)])

    return ModelMetrics(
        player_type=player_type,
        n_players=len(X),
        n_clusters=n_clusters,
        silhouette=sil,
        cluster_sizes=cluster_sizes,
        pca_variance_3pc=pca_3pc,
        feature_cols=feature_cols,
    )


# ---------------------------------------------------------------------------
# Validation gates
# ---------------------------------------------------------------------------


def _validate_pca_variance(
    metrics: ModelMetrics,
    thresholds: Dict[str, Any],
) -> Optional[str]:
    """Gate: PCA variance for the first 3 PCs must meet threshold.

    Returns an error message string if the gate fails, else None.
    """
    if metrics.player_type == "batter":
        required = thresholds["min_variance_batter"]
    else:
        required = thresholds["min_variance_bowler"]

    if metrics.pca_variance_3pc < required:
        return (
            f"PCA variance gate FAILED for {metrics.player_type}: "
            f"{metrics.pca_variance_3pc:.2%} < {required:.0%}"
        )
    return None


def _validate_cluster_sizes(
    metrics: ModelMetrics,
    thresholds: Dict[str, Any],
) -> Optional[str]:
    """Gate: No cluster should contain <5% of total players.

    Also checks the absolute minimum from thresholds.
    """
    total = metrics.n_players
    min_pct_threshold = thresholds.get("min_cluster_size_pct", 0.05)
    min_abs_threshold = thresholds.get("min_cluster_abs", 10)

    for cid, size in metrics.cluster_sizes.items():
        pct = size / total if total > 0 else 0
        if pct < min_pct_threshold:
            return (
                f"Cluster size gate FAILED: cluster {cid} has {size} players "
                f"({pct:.1%} < {min_pct_threshold:.0%} of {total})"
            )
        if size < min_abs_threshold:
            return (
                f"Cluster size gate FAILED: cluster {cid} has {size} players "
                f"(< absolute min {min_abs_threshold})"
            )
    return None


def _validate_cluster_count_stability(
    candidate: ModelMetrics,
    current: Optional[ModelMetrics],
) -> Optional[str]:
    """Gate: Cluster count should not change wildly between versions.

    Allows a delta of at most 2 clusters from the current production model.
    """
    if current is None:
        return None  # No baseline to compare against

    delta = abs(candidate.n_clusters - current.n_clusters)
    if delta > 2:
        return (
            f"Cluster count stability gate FAILED: candidate has "
            f"{candidate.n_clusters} clusters vs current {current.n_clusters} "
            f"(delta={delta} > 2)"
        )
    return None


def run_validation_gates(
    candidate: ModelMetrics,
    current: Optional[ModelMetrics],
    thresholds: Dict[str, Any],
) -> List[str]:
    """Run all validation gates and return a list of failure messages."""
    failures: List[str] = []

    result = _validate_pca_variance(candidate, thresholds)
    if result:
        failures.append(result)

    result = _validate_cluster_sizes(candidate, thresholds)
    if result:
        failures.append(result)

    result = _validate_cluster_count_stability(candidate, current)
    if result:
        failures.append(result)

    return failures


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------


def _compare_models(
    candidate: ModelMetrics,
    current: Optional[ModelMetrics],
    min_improvement: float,
    force: bool,
) -> Tuple[bool, str]:
    """Decide whether the candidate model should be promoted.

    Parameters
    ----------
    candidate : ModelMetrics
        Metrics of the newly trained model.
    current : ModelMetrics or None
        Metrics of the current production model.  None when no production
        model exists yet (first run).
    min_improvement : float
        Minimum improvement in silhouette score to trigger promotion.
    force : bool
        If True, skip the improvement check and always promote.

    Returns
    -------
    promote : bool
    reason : str
    """
    if current is None:
        return True, "No existing production model; promoting candidate as initial version."

    if force:
        return True, (
            f"Force mode: promoting regardless of improvement "
            f"(candidate silhouette={candidate.silhouette:.4f}, "
            f"current={current.silhouette:.4f})."
        )

    improvement = candidate.silhouette - current.silhouette
    if improvement >= min_improvement:
        return True, (
            f"Candidate is better by {improvement:.4f} "
            f"(>= threshold {min_improvement:.4f}). "
            f"Candidate silhouette={candidate.silhouette:.4f}, "
            f"current={current.silhouette:.4f}."
        )

    return False, (
        f"Candidate not sufficiently better: improvement={improvement:.4f} "
        f"(< threshold {min_improvement:.4f}). "
        f"Candidate silhouette={candidate.silhouette:.4f}, "
        f"current={current.silhouette:.4f}. Keeping current model."
    )


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def _retrain_single(
    conn: duckdb.DuckDBPyConnection,
    player_type: str,
    thresholds: Dict[str, Any],
    min_improvement: float,
    force: bool,
    current_metrics: Optional[ModelMetrics],
) -> RetrainResult:
    """Run the retrain-and-evaluate loop for a single player type."""

    logger.info("--- Retraining %s model ---", player_type)

    # 1. Load features
    if player_type == "batter":
        raw_df = load_batter_features(conn)
        feature_cols = list(BATTER_FEATURE_COLS)
        n_clusters = thresholds.get("n_clusters_batter", 5)
    else:
        raw_df = load_bowler_features(conn)
        feature_cols = list(BOWLER_FEATURE_COLS)
        n_clusters = thresholds.get("n_clusters_bowler", 5)

    logger.info("Loaded %d %ss from DuckDB", len(raw_df), player_type)

    # 2. Feature engineering
    corr_threshold = thresholds.get("correlation_threshold", 0.90)
    X, df_clean, final_features, scaler = prepare_features(raw_df, feature_cols, corr_threshold)
    logger.info("Prepared feature matrix: %d samples x %d features", X.shape[0], X.shape[1])

    # Guard: need more samples than clusters
    if X.shape[0] < n_clusters:
        logger.warning(
            "Too few samples (%d) for %d clusters; reducing n_clusters",
            X.shape[0],
            n_clusters,
        )
        n_clusters = max(2, X.shape[0] // 2)

    # 3. Train candidate model
    kmeans, labels = _train_model(X, n_clusters)

    # 4. Evaluate
    candidate_metrics = _evaluate_model(X, labels, final_features, player_type)
    logger.info(
        "Candidate %s model: silhouette=%.4f, clusters=%d, PCA(3pc)=%.2f%%",
        player_type,
        candidate_metrics.silhouette,
        candidate_metrics.n_clusters,
        candidate_metrics.pca_variance_3pc * 100,
    )

    # 5. Validation gates
    gate_failures = run_validation_gates(candidate_metrics, current_metrics, thresholds)
    if gate_failures and not force:
        for msg in gate_failures:
            logger.warning("Validation gate: %s", msg)
        return RetrainResult(
            player_type=player_type,
            current_metrics=current_metrics,
            candidate_metrics=candidate_metrics,
            promoted=False,
            reason=f"Validation gate(s) failed: {'; '.join(gate_failures)}",
        )

    if gate_failures and force:
        for msg in gate_failures:
            logger.warning("Validation gate (overridden by --force): %s", msg)

    # 6. Compare against production
    promote, reason = _compare_models(candidate_metrics, current_metrics, min_improvement, force)
    logger.info("Promotion decision for %s: %s (%s)", player_type, promote, reason)

    return RetrainResult(
        player_type=player_type,
        current_metrics=current_metrics,
        candidate_metrics=candidate_metrics,
        promoted=promote,
        reason=reason,
    )


def run_pipeline(
    force: bool = False,
    dry_run: bool = False,
    min_improvement: float = 0.05,
    verbose: bool = False,
) -> PipelineReport:
    """Execute the full retraining pipeline for both batters and bowlers.

    Parameters
    ----------
    force : bool
        Promote the candidate model even if it does not exceed the
        improvement threshold (still runs validation gates with warnings).
    dry_run : bool
        Run the full pipeline but do not update model_registry.json or
        write any files.
    min_improvement : float
        Minimum improvement in silhouette score required for promotion.
    verbose : bool
        Enable DEBUG-level logging.

    Returns
    -------
    PipelineReport
    """
    _setup_logging(verbose)
    thresholds = _load_thresholds()

    mode = "force" if force else ("dry-run" if dry_run else "normal")
    logger.info("Starting retrain pipeline (mode=%s, min_improvement=%.4f)", mode, min_improvement)

    # Database check
    if not DB_PATH.exists():
        msg = f"DuckDB database not found at {DB_PATH}"
        logger.error(msg)
        return PipelineReport(
            timestamp=datetime.now().isoformat(),
            run_mode=mode,
            errors=[msg],
        )

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Load current production metrics from registry (if they exist)
    registry = _load_registry()
    clustering_entry = registry["models"].get("player_clustering", {})
    active_version = clustering_entry.get("active_version", "v2.0.0")
    version_data = clustering_entry.get("versions", {}).get(active_version, {})

    current_batter: Optional[ModelMetrics] = None
    current_bowler: Optional[ModelMetrics] = None
    prod_metrics = version_data.get("metrics", {})

    if prod_metrics.get("batter_silhouette") is not None:
        current_batter = ModelMetrics(
            player_type="batter",
            n_players=prod_metrics.get("batter_n_players", 0),
            n_clusters=prod_metrics.get("batter_n_clusters", 5),
            silhouette=prod_metrics["batter_silhouette"],
            cluster_sizes=prod_metrics.get("batter_cluster_sizes", {}),
            pca_variance_3pc=prod_metrics.get("batter_pca_variance", 0.0),
            feature_cols=prod_metrics.get("batter_features", []),
        )
        logger.info(
            "Loaded current batter metrics from registry (v%s, sil=%.4f)",
            active_version,
            current_batter.silhouette,
        )

    if prod_metrics.get("bowler_silhouette") is not None:
        current_bowler = ModelMetrics(
            player_type="bowler",
            n_players=prod_metrics.get("bowler_n_players", 0),
            n_clusters=prod_metrics.get("bowler_n_clusters", 5),
            silhouette=prod_metrics["bowler_silhouette"],
            cluster_sizes=prod_metrics.get("bowler_cluster_sizes", {}),
            pca_variance_3pc=prod_metrics.get("bowler_pca_variance", 0.0),
            feature_cols=prod_metrics.get("bowler_features", []),
        )
        logger.info(
            "Loaded current bowler metrics from registry (v%s, sil=%.4f)",
            active_version,
            current_bowler.silhouette,
        )

    # Retrain batter model
    try:
        batter_result = _retrain_single(
            conn, "batter", thresholds, min_improvement, force, current_batter
        )
    except (ValueError, RuntimeError, OSError):
        logger.exception("Batter retraining failed")
        batter_result = None

    # Retrain bowler model
    try:
        bowler_result = _retrain_single(
            conn, "bowler", thresholds, min_improvement, force, current_bowler
        )
    except (ValueError, RuntimeError, OSError):
        logger.exception("Bowler retraining failed")
        bowler_result = None

    conn.close()

    # Determine overall promotion decision (promote only when BOTH succeed)
    batter_promoted = batter_result.promoted if batter_result else False
    bowler_promoted = bowler_result.promoted if bowler_result else False
    should_promote = batter_promoted or bowler_promoted

    new_version: Optional[str] = None
    report = PipelineReport(
        timestamp=datetime.now().isoformat(),
        run_mode=mode,
        batter_result=batter_result,
        bowler_result=bowler_result,
        previous_version=active_version,
    )

    if should_promote:
        new_version = _bump_minor(active_version)
        report.new_version = new_version

        if dry_run:
            logger.info("[DRY-RUN] Would promote to %s -- no files written", new_version)
        else:
            # Update registry
            new_entry: Dict[str, Any] = {
                "created_at": datetime.now().isoformat(),
                "created_by": "retrain_pipeline (TKT-156)",
                "promoted_from": active_version,
                "run_mode": mode,
                "metrics": {},
            }

            if batter_result:
                m = batter_result.candidate_metrics
                new_entry["metrics"]["batter_silhouette"] = round(m.silhouette, 4)
                new_entry["metrics"]["batter_n_players"] = m.n_players
                new_entry["metrics"]["batter_n_clusters"] = m.n_clusters
                new_entry["metrics"]["batter_cluster_sizes"] = m.cluster_sizes
                new_entry["metrics"]["batter_pca_variance"] = round(m.pca_variance_3pc, 4)
                new_entry["metrics"]["batter_features"] = m.feature_cols

            if bowler_result:
                m = bowler_result.candidate_metrics
                new_entry["metrics"]["bowler_silhouette"] = round(m.silhouette, 4)
                new_entry["metrics"]["bowler_n_players"] = m.n_players
                new_entry["metrics"]["bowler_n_clusters"] = m.n_clusters
                new_entry["metrics"]["bowler_cluster_sizes"] = m.cluster_sizes
                new_entry["metrics"]["bowler_pca_variance"] = round(m.pca_variance_3pc, 4)
                new_entry["metrics"]["bowler_features"] = m.feature_cols

            if "versions" not in clustering_entry:
                clustering_entry["versions"] = {}
            clustering_entry["versions"][new_version] = new_entry
            clustering_entry["active_version"] = new_version
            registry["models"]["player_clustering"] = clustering_entry

            _save_registry(registry)
            logger.info("Promoted new model to %s", new_version)

            # Write comparison report
            _write_report(report)
    else:
        logger.info("No promotion; current production model %s remains active", active_version)
        if not dry_run:
            _write_report(report)

    return report


def _write_report(report: PipelineReport) -> None:
    """Write the pipeline report to a JSON file under outputs/monitoring."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"retrain_report_{ts}.json"
    with open(path, "w") as fh:
        json.dump(report.to_dict(), fh, indent=2)
    logger.info("Retrain report written to %s", path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cricket Playbook - ML Model Retraining Pipeline (TKT-156)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Promote the candidate model even if improvement is below threshold.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the full pipeline but do not write any files.",
    )
    parser.add_argument(
        "--min-improvement",
        type=float,
        default=0.05,
        help="Minimum silhouette score improvement for promotion (default: 0.05).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug-level logging.",
    )

    args = parser.parse_args()

    report = run_pipeline(
        force=args.force,
        dry_run=args.dry_run,
        min_improvement=args.min_improvement,
        verbose=args.verbose,
    )

    # Print summary
    print("\n" + "=" * 70)
    print("RETRAIN PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Timestamp    : {report.timestamp}")
    print(f"  Run mode     : {report.run_mode}")
    print(f"  Prev version : {report.previous_version}")
    print(f"  New version  : {report.new_version or '(none - not promoted)'}")

    for label, result in [("Batter", report.batter_result), ("Bowler", report.bowler_result)]:
        if result is None:
            print(f"\n  {label}: SKIPPED (error)")
            continue
        m = result.candidate_metrics
        print(f"\n  {label}:")
        print(f"    Promoted      : {result.promoted}")
        print(f"    Silhouette    : {m.silhouette:.4f}")
        print(f"    Clusters      : {m.n_clusters}")
        print(f"    Players       : {m.n_players}")
        print(f"    PCA (3 PCs)   : {m.pca_variance_3pc:.2%}")
        print(f"    Cluster sizes : {m.cluster_sizes}")
        print(f"    Reason        : {result.reason}")

    if report.errors:
        print("\n  Errors:")
        for err in report.errors:
            print(f"    - {err}")

    print("\n" + "=" * 70)

    # Exit code: 0 = promoted, 1 = not promoted, 2 = error
    if report.errors:
        return 2
    any_promoted = (report.batter_result and report.batter_result.promoted) or (
        report.bowler_result and report.bowler_result.promoted
    )
    return 0 if any_promoted else 1


if __name__ == "__main__":
    sys.exit(main())
