#!/usr/bin/env python3
"""
Win Probability Model — Training & Validation Pipeline
========================================================
Trains LightGBM + Logistic Regression models for ball-by-ball
**Historical Win Probability Replay** using the feature-engineered
parquet from TKT-206.

Two models are trained (per the architecture doc TKT-205):
    - Model A: First innings  (no target / required run rate)
    - Model B: Second innings (with target and required run rate)

Both models are calibrated with Platt scaling, evaluated on Brier score,
and analysed with SHAP feature importance.

**CRITICAL FLORENTINO CONDITION:**
    This is HISTORICAL REPLAY ONLY — never forward prediction.
    All labeling and metadata must say "Historical Win Probability Replay".
    Models are registered as ``experimental`` with tag ``historical-replay-only``.

Owner: Ime Udoka (ML Ops Engineer)
Ticket: TKT-207  |  EPIC-018: Win Probability Model
"""

from __future__ import annotations

import json
import logging
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Lazy imports (heavy libraries)
# ---------------------------------------------------------------------------
lgb = None  # lightgbm
shap_lib = None  # shap


def _ensure_lightgbm() -> None:
    global lgb
    if lgb is None:
        import lightgbm

        lgb = lightgbm


def _ensure_shap() -> None:
    global shap_lib
    if shap_lib is None:
        import shap

        shap_lib = shap


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ml"
PARQUET_PATH = DATA_DIR / "win_prob_features.parquet"
METADATA_PATH = DATA_DIR / "win_prob_metadata.json"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "ml"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("train_win_prob")

# ---------------------------------------------------------------------------
# Feature definitions (from TKT-206 parquet schema)
# ---------------------------------------------------------------------------
# Shared features for both innings
SHARED_FEATURES: List[str] = [
    "over_number",
    "ball_in_over",
    "current_score",
    "wickets_fallen",
    "balls_remaining",
    "current_run_rate",
    "phase_progress",
    "last_3ov_run_rate",
    "last_3ov_wickets",
    "last_3ov_dot_pct",
    "last_3ov_boundary_pct",
    "batting_team_strength",
    "bowling_team_strength",
]

# Additional features for 2nd innings only
INNINGS2_EXTRA_FEATURES: List[str] = [
    "required_run_rate",
    "target_score",
]

CATEGORICAL_FEATURES: List[str] = ["phase"]

LABEL_COL = "batting_team_won"

# Phase encoding for LightGBM
PHASE_ENCODING = {"powerplay": 0, "middle": 1, "death": 2}

# ---------------------------------------------------------------------------
# Season grouping for temporal CV
# ---------------------------------------------------------------------------
# The parquet has match_id which contains season info.  We extract
# season from the match_id or from the date range metadata.
# We assign each row a "season_group" for cross-validation folds.

FOLD_SEASON_GROUPS: Dict[int, List[str]] = {
    # Fold -> validation season prefixes
    # Based on architecture doc Section 7.2
    0: ["2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011"],
    1: ["2012", "2013", "2014", "2015"],
    2: ["2016", "2017", "2018", "2019"],
    3: ["2020", "2021", "2022"],
    4: ["2023"],
}

# Holdout test set: most recent full season
HOLDOUT_SEASONS: List[str] = ["2024", "2025", "2026"]


# ---------------------------------------------------------------------------
# Data loading & preparation
# ---------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    """Load the feature-engineered parquet and add season information.

    Season information is sourced from ``dim_match`` in the main DuckDB
    (``cricket_playbook.duckdb``) since the parquet ``match_id`` values are
    ESPNCricinfo numeric IDs, not year-prefixed strings.
    """
    if not PARQUET_PATH.exists():
        log.error("Feature parquet not found at %s. Run TKT-206 first.", PARQUET_PATH)
        sys.exit(1)

    df = pd.read_parquet(PARQUET_PATH)
    log.info("Loaded %d rows x %d cols from %s", len(df), len(df.columns), PARQUET_PATH)

    # Load season mapping from DuckDB dim_match
    duckdb_path = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
    if duckdb_path.exists():
        import duckdb

        con = duckdb.connect(str(duckdb_path), read_only=True)
        season_map = con.execute("SELECT match_id, season FROM dim_match").fetchdf()
        con.close()

        # Merge season onto the feature dataframe (deduplicate dim_match first)
        df["match_id"] = df["match_id"].astype(str)
        season_map["match_id"] = season_map["match_id"].astype(str)
        season_map = season_map.drop_duplicates(subset="match_id", keep="first")
        df = df.merge(season_map, on="match_id", how="left")

        # Normalise season to a 4-digit year (e.g. "2019/20" -> "2019")
        df["season"] = (
            df["season"].astype(str).str.extract(r"(\d{4})", expand=False).fillna("unknown")
        )
        log.info(
            "Season mapping: matched %d / %d rows from dim_match",
            (df["season"] != "unknown").sum(),
            len(df),
        )
    else:
        log.warning("DuckDB not found at %s — falling back to match_id regex", duckdb_path)
        df["season"] = df["match_id"].astype(str).str.extract(r"(\d{4})", expand=False)
        df["season"] = df["season"].fillna("unknown")

    return df


def assign_fold_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Assign each row a CV fold group based on season."""
    # Map season to fold group; holdout gets fold -1
    season_to_fold: Dict[str, int] = {}
    for fold_id, seasons in FOLD_SEASON_GROUPS.items():
        for s in seasons:
            season_to_fold[s] = fold_id
    for s in HOLDOUT_SEASONS:
        season_to_fold[s] = -1  # holdout

    df["fold_group"] = df["season"].map(season_to_fold).fillna(-1).astype(int)
    return df


def prepare_innings_data(
    df: pd.DataFrame,
    innings: int,
) -> Tuple[pd.DataFrame, List[str]]:
    """Filter to a specific innings and select appropriate features.

    Parameters
    ----------
    df : pd.DataFrame
        Full dataset with all innings.
    innings : int
        1 or 2.

    Returns
    -------
    df_innings : pd.DataFrame
        Filtered data with selected features.
    feature_cols : list[str]
        Feature column names for modelling.
    """
    df_inn = df[df["innings"] == innings].copy()

    # Encode phase as integer for LightGBM
    df_inn["phase_encoded"] = df_inn["phase"].map(PHASE_ENCODING).fillna(1).astype(int)

    # Select feature columns
    feature_cols = list(SHARED_FEATURES) + ["phase_encoded"]
    if innings == 2:
        feature_cols += INNINGS2_EXTRA_FEATURES

    # Drop rows with NaN in features (should be minimal)
    initial_len = len(df_inn)
    df_inn = df_inn.dropna(subset=feature_cols + [LABEL_COL])
    dropped = initial_len - len(df_inn)
    if dropped > 0:
        log.info("Innings %d: dropped %d rows with NaN features", innings, dropped)

    log.info(
        "Innings %d: %d rows, %d features",
        innings,
        len(df_inn),
        len(feature_cols),
    )
    return df_inn, feature_cols


# ---------------------------------------------------------------------------
# Evaluation metrics
# ---------------------------------------------------------------------------
def compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    prefix: str = "",
) -> Dict[str, float]:
    """Compute Brier score, log loss, and AUC-ROC.

    Parameters
    ----------
    y_true : array-like
        Binary labels (0 or 1).
    y_prob : array-like
        Predicted probabilities of class 1.
    prefix : str
        Optional prefix for metric keys.

    Returns
    -------
    dict
        Metrics dictionary.
    """
    # Clip probabilities for numerical stability
    y_prob = np.clip(y_prob, 1e-6, 1 - 1e-6)

    metrics: Dict[str, float] = {}
    p = f"{prefix}_" if prefix else ""

    metrics[f"{p}brier_score"] = float(brier_score_loss(y_true, y_prob))
    metrics[f"{p}log_loss"] = float(log_loss(y_true, y_prob))

    # AUC requires both classes present
    if len(np.unique(y_true)) == 2:
        metrics[f"{p}auc_roc"] = float(roc_auc_score(y_true, y_prob))
    else:
        metrics[f"{p}auc_roc"] = float("nan")

    return metrics


def compute_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> Tuple[float, List[Dict[str, float]]]:
    """Compute Expected Calibration Error (ECE) and per-bin calibration.

    Parameters
    ----------
    y_true : array-like
        Binary labels.
    y_prob : array-like
        Predicted probabilities.
    n_bins : int
        Number of calibration bins.

    Returns
    -------
    ece : float
        Expected Calibration Error.
    bins : list[dict]
        Per-bin calibration data.
    """
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bins_data: List[Dict[str, float]] = []
    ece = 0.0

    for i in range(n_bins):
        mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i + 1])
        if i == n_bins - 1:  # include right edge for last bin
            mask = mask | (y_prob == bin_edges[i + 1])
        count = mask.sum()

        if count > 0:
            mean_pred = float(y_prob[mask].mean())
            mean_true = float(y_true[mask].mean())
            ece += abs(mean_pred - mean_true) * (count / len(y_true))
            bins_data.append(
                {
                    "bin": f"{bin_edges[i]:.1f}-{bin_edges[i + 1]:.1f}",
                    "count": int(count),
                    "mean_predicted": round(mean_pred, 4),
                    "mean_observed": round(mean_true, 4),
                    "abs_error": round(abs(mean_pred - mean_true), 4),
                }
            )
        else:
            bins_data.append(
                {
                    "bin": f"{bin_edges[i]:.1f}-{bin_edges[i + 1]:.1f}",
                    "count": 0,
                    "mean_predicted": None,
                    "mean_observed": None,
                    "abs_error": None,
                }
            )

    return float(ece), bins_data


def compute_phase_metrics(
    df: pd.DataFrame,
    y_prob: np.ndarray,
    feature_cols: List[str],
) -> Dict[str, Dict[str, float]]:
    """Compute per-phase Brier scores.

    Parameters
    ----------
    df : pd.DataFrame
        Data with ``phase`` and ``LABEL_COL`` columns, aligned with ``y_prob``.
    y_prob : array-like
        Predicted probabilities.
    feature_cols : list[str]
        Not used directly but kept for interface consistency.

    Returns
    -------
    dict
        Phase -> metrics dict.
    """
    results: Dict[str, Dict[str, float]] = {}
    y_true = df[LABEL_COL].values

    for phase_name in ["powerplay", "middle", "death"]:
        mask = df["phase"].values == phase_name
        if mask.sum() > 0:
            results[phase_name] = compute_metrics(y_true[mask], y_prob[mask])

    return results


# ---------------------------------------------------------------------------
# Model training
# ---------------------------------------------------------------------------
def train_lightgbm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_names: List[str],
) -> Any:
    """Train a LightGBM model with early stopping.

    Parameters
    ----------
    X_train, y_train : array-like
        Training data.
    X_val, y_val : array-like
        Validation data for early stopping.
    feature_names : list[str]
        Feature column names.

    Returns
    -------
    lgb.Booster
        Trained LightGBM model.
    """
    _ensure_lightgbm()

    params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "boosting_type": "gbdt",
        "n_estimators": 800,
        "max_depth": 6,
        "learning_rate": 0.05,
        "num_leaves": 48,
        "min_child_samples": 50,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 2.0,
        "random_state": 42,
        "verbose": -1,
        "n_jobs": -1,
    }

    model = lgb.LGBMClassifier(**params)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="binary_logloss",
        callbacks=[
            lgb.early_stopping(stopping_rounds=50, verbose=False),
            lgb.log_evaluation(period=0),
        ],
    )

    log.info(
        "LightGBM trained: %d trees, best iteration=%d",
        model.n_estimators,
        model.best_iteration_,
    )
    return model


def train_logistic_regression(
    X_train: np.ndarray,
    y_train: np.ndarray,
) -> LogisticRegression:
    """Train a logistic regression baseline.

    Parameters
    ----------
    X_train, y_train : array-like
        Training data.

    Returns
    -------
    LogisticRegression
        Trained model.
    """
    model = LogisticRegression(
        max_iter=1000,
        solver="lbfgs",
        C=1.0,
        random_state=42,
    )
    model.fit(X_train, y_train)
    log.info("Logistic Regression trained: %d features", X_train.shape[1])
    return model


def calibrate_model(
    model: Any,
    X_cal: np.ndarray,
    y_cal: np.ndarray,
    method: str = "sigmoid",
) -> CalibratedClassifierCV:
    """Apply Platt scaling (sigmoid) calibration to a trained model.

    Parameters
    ----------
    model : estimator
        A fitted classifier with ``predict_proba``.
    X_cal : array-like
        Calibration data features.
    y_cal : array-like
        Calibration data labels.
    method : str
        ``"sigmoid"`` for Platt scaling, ``"isotonic"`` for isotonic regression.

    Returns
    -------
    CalibratedClassifierCV
        Calibrated model.
    """
    cal_model = CalibratedClassifierCV(
        estimator=model,
        cv="prefit",
        method=method,
    )
    cal_model.fit(X_cal, y_cal)
    log.info("Platt scaling calibration applied (method=%s)", method)
    return cal_model


# ---------------------------------------------------------------------------
# SHAP feature importance
# ---------------------------------------------------------------------------
def compute_shap_importance(
    model: Any,
    X: np.ndarray,
    feature_names: List[str],
    n_samples: int = 500,
) -> List[Dict[str, Any]]:
    """Compute SHAP feature importance for a LightGBM model.

    Parameters
    ----------
    model : LGBMClassifier
        Trained LightGBM model.
    X : array-like
        Data to explain (a sample will be taken).
    feature_names : list[str]
        Feature names.
    n_samples : int
        Number of samples for SHAP computation.

    Returns
    -------
    list[dict]
        Feature importance entries sorted by mean |SHAP|.
    """
    _ensure_shap()

    sample_size = min(n_samples, len(X))
    rng = np.random.RandomState(42)
    idx = rng.choice(len(X), sample_size, replace=False)
    X_sample = X[idx]

    explainer = shap_lib.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # For binary classification, shap_values may be a list of 2 arrays
    if isinstance(shap_values, list):
        # Use class-1 SHAP values
        sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
    else:
        sv = shap_values

    mean_abs_shap = np.mean(np.abs(sv), axis=0)
    sorted_idx = np.argsort(mean_abs_shap)[::-1]

    importance_list: List[Dict[str, Any]] = []
    for rank, fi in enumerate(sorted_idx, 1):
        importance_list.append(
            {
                "rank": rank,
                "feature": feature_names[fi],
                "mean_abs_shap": round(float(mean_abs_shap[fi]), 6),
            }
        )

    return importance_list


# ---------------------------------------------------------------------------
# Cross-validation pipeline
# ---------------------------------------------------------------------------
def run_temporal_cv(
    df: pd.DataFrame,
    feature_cols: List[str],
    innings: int,
    n_folds: int = 5,
) -> Dict[str, Any]:
    """Run temporal (season-grouped) cross-validation.

    For each fold, trains on all seasons EXCEPT the validation seasons,
    then evaluates on the held-out fold.

    Parameters
    ----------
    df : pd.DataFrame
        Innings-specific data with ``fold_group`` column.
    feature_cols : list[str]
        Feature column names.
    innings : int
        1 or 2 (for logging).
    n_folds : int
        Number of CV folds.

    Returns
    -------
    dict
        Cross-validation results including per-fold metrics.
    """
    log.info("=" * 50)
    log.info("Temporal %d-fold CV for innings %d", n_folds, innings)
    log.info("=" * 50)

    # Exclude holdout data (fold_group == -1)
    df_cv = df[df["fold_group"] >= 0].copy()

    X = df_cv[feature_cols].values
    y = df_cv[LABEL_COL].values
    groups = df_cv["fold_group"].values

    gkf = GroupKFold(n_splits=n_folds)

    lgb_fold_metrics: List[Dict[str, float]] = []
    lr_fold_metrics: List[Dict[str, float]] = []

    for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
        log.info("--- Fold %d/%d ---", fold_idx + 1, n_folds)

        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        log.info(
            "  Train: %d samples | Val: %d samples",
            len(X_train),
            len(X_val),
        )

        # -- LightGBM --
        lgb_model = train_lightgbm(X_train, y_train, X_val, y_val, feature_cols)
        lgb_probs = lgb_model.predict_proba(X_val)[:, 1]
        lgb_metrics = compute_metrics(y_val, lgb_probs, prefix="lgb")
        lgb_fold_metrics.append(lgb_metrics)
        log.info(
            "  LightGBM  — Brier: %.4f | AUC: %.4f | LogLoss: %.4f",
            lgb_metrics["lgb_brier_score"],
            lgb_metrics["lgb_auc_roc"],
            lgb_metrics["lgb_log_loss"],
        )

        # -- Logistic Regression (baseline) --
        lr_model = train_logistic_regression(X_train, y_train)
        lr_probs = lr_model.predict_proba(X_val)[:, 1]
        lr_metrics = compute_metrics(y_val, lr_probs, prefix="lr")
        lr_fold_metrics.append(lr_metrics)
        log.info(
            "  LogReg    — Brier: %.4f | AUC: %.4f | LogLoss: %.4f",
            lr_metrics["lr_brier_score"],
            lr_metrics["lr_auc_roc"],
            lr_metrics["lr_log_loss"],
        )

    # Aggregate fold metrics
    def _mean_metrics(fold_list: List[Dict[str, float]]) -> Dict[str, float]:
        keys = fold_list[0].keys()
        return {k: float(np.mean([f[k] for f in fold_list])) for k in keys}

    def _std_metrics(fold_list: List[Dict[str, float]]) -> Dict[str, float]:
        keys = fold_list[0].keys()
        return {k: float(np.std([f[k] for f in fold_list])) for k in keys}

    lgb_mean = _mean_metrics(lgb_fold_metrics)
    lgb_std = _std_metrics(lgb_fold_metrics)
    lr_mean = _mean_metrics(lr_fold_metrics)
    lr_std = _std_metrics(lr_fold_metrics)

    log.info("")
    log.info("CV SUMMARY (innings %d):", innings)
    log.info(
        "  LightGBM  mean Brier: %.4f (+/- %.4f)",
        lgb_mean["lgb_brier_score"],
        lgb_std["lgb_brier_score"],
    )
    log.info(
        "  LogReg    mean Brier: %.4f (+/- %.4f)",
        lr_mean["lr_brier_score"],
        lr_std["lr_brier_score"],
    )

    return {
        "innings": innings,
        "n_folds": n_folds,
        "lightgbm": {
            "mean": {k: round(v, 6) for k, v in lgb_mean.items()},
            "std": {k: round(v, 6) for k, v in lgb_std.items()},
            "per_fold": lgb_fold_metrics,
        },
        "logistic_regression": {
            "mean": {k: round(v, 6) for k, v in lr_mean.items()},
            "std": {k: round(v, 6) for k, v in lr_std.items()},
            "per_fold": lr_fold_metrics,
        },
    }


# ---------------------------------------------------------------------------
# Final model training (on all non-holdout data)
# ---------------------------------------------------------------------------
def train_final_model(
    df: pd.DataFrame,
    feature_cols: List[str],
    innings: int,
) -> Tuple[Any, CalibratedClassifierCV, Dict[str, Any]]:
    """Train the final LightGBM model on all non-holdout data, calibrate,
    and evaluate on the holdout set.

    Parameters
    ----------
    df : pd.DataFrame
        Full innings-specific data.
    feature_cols : list[str]
        Feature columns.
    innings : int
        1 or 2.

    Returns
    -------
    raw_model : LGBMClassifier
        The uncalibrated trained model (for SHAP / saving).
    calibrated_model : CalibratedClassifierCV
        Platt-scaled calibrated model.
    results : dict
        Holdout metrics, calibration data, SHAP importance.
    """
    log.info("=" * 50)
    log.info("FINAL MODEL TRAINING — Innings %d", innings)
    log.info("=" * 50)

    # Split: train on fold_group >= 0, holdout on fold_group == -1
    df_train = df[df["fold_group"] >= 0].copy()
    df_holdout = df[df["fold_group"] == -1].copy()

    X_train = df_train[feature_cols].values
    y_train = df_train[LABEL_COL].values

    if len(df_holdout) == 0:
        log.warning("No holdout data found. Using last CV fold as holdout.")
        # Fallback: use last fold group as holdout
        max_fold = df_train["fold_group"].max()
        holdout_mask = df_train["fold_group"] == max_fold
        df_holdout = df_train[holdout_mask].copy()
        df_train = df_train[~holdout_mask].copy()
        X_train = df_train[feature_cols].values  # noqa: F841
        y_train = df_train[LABEL_COL].values  # noqa: F841

    X_holdout = df_holdout[feature_cols].values
    y_holdout = df_holdout[LABEL_COL].values

    log.info("Train: %d | Holdout: %d", len(X_train), len(X_holdout))

    # Split train further: 80% for model, 20% for calibration
    n_cal = max(int(len(X_train) * 0.2), 1000)  # noqa: F841
    # Use the most recent data (highest fold) for calibration
    cal_fold = df_train["fold_group"].max()
    cal_mask = df_train["fold_group"] == cal_fold
    X_cal = df_train.loc[cal_mask, feature_cols].values
    y_cal = df_train.loc[cal_mask, LABEL_COL].values
    X_model_train = df_train.loc[~cal_mask, feature_cols].values
    y_model_train = df_train.loc[~cal_mask, LABEL_COL].values

    log.info("Model train: %d | Calibration: %d", len(X_model_train), len(X_cal))

    # Train LightGBM
    raw_model = train_lightgbm(X_model_train, y_model_train, X_cal, y_cal, feature_cols)

    # Calibrate with Platt scaling
    calibrated_model = calibrate_model(raw_model, X_cal, y_cal, method="sigmoid")

    # Evaluate on holdout
    raw_probs = raw_model.predict_proba(X_holdout)[:, 1]
    cal_probs = calibrated_model.predict_proba(X_holdout)[:, 1]

    raw_metrics = compute_metrics(y_holdout, raw_probs, prefix="raw")
    cal_metrics = compute_metrics(y_holdout, cal_probs, prefix="calibrated")

    log.info("HOLDOUT RESULTS (innings %d):", innings)
    log.info(
        "  Raw      — Brier: %.4f | AUC: %.4f",
        raw_metrics["raw_brier_score"],
        raw_metrics["raw_auc_roc"],
    )
    log.info(
        "  Calibrated — Brier: %.4f | AUC: %.4f",
        cal_metrics["calibrated_brier_score"],
        cal_metrics["calibrated_auc_roc"],
    )

    # Calibration analysis
    ece, cal_bins = compute_calibration_error(y_holdout, cal_probs)
    log.info("  ECE: %.4f", ece)

    # Phase-specific metrics
    phase_metrics = compute_phase_metrics(df_holdout, cal_probs, feature_cols)
    for phase, pm in phase_metrics.items():
        brier_key = [k for k in pm if "brier" in k][0]
        log.info("  Phase %-10s Brier: %.4f", phase, pm[brier_key])

    # SHAP importance
    log.info("Computing SHAP feature importance...")
    try:
        shap_importance = compute_shap_importance(raw_model, X_train, feature_cols)
        log.info("  Top 5 features:")
        for fi in shap_importance[:5]:
            log.info("    %d. %s (%.4f)", fi["rank"], fi["feature"], fi["mean_abs_shap"])
    except Exception as exc:
        log.warning("SHAP computation failed: %s", exc)
        shap_importance = []

    # LightGBM native feature importance (gain)
    native_importance = []
    if hasattr(raw_model, "feature_importances_"):
        for i, imp in enumerate(raw_model.feature_importances_):
            native_importance.append({"feature": feature_cols[i], "importance_gain": int(imp)})
        native_importance.sort(key=lambda x: x["importance_gain"], reverse=True)

    results = {
        "innings": innings,
        "n_train": len(X_model_train),
        "n_calibration": len(X_cal),
        "n_holdout": len(X_holdout),
        "holdout_seasons": HOLDOUT_SEASONS,
        "raw_metrics": {k: round(v, 6) for k, v in raw_metrics.items()},
        "calibrated_metrics": {k: round(v, 6) for k, v in cal_metrics.items()},
        "expected_calibration_error": round(ece, 6),
        "calibration_bins": cal_bins,
        "phase_metrics": {
            k: {mk: round(mv, 6) for mk, mv in v.items()} for k, v in phase_metrics.items()
        },
        "shap_importance": shap_importance,
        "native_importance": native_importance[:10],
        "hyperparameters": raw_model.get_params(),
        "best_iteration": getattr(raw_model, "best_iteration_", None),
    }

    return raw_model, calibrated_model, results


# ---------------------------------------------------------------------------
# Model persistence
# ---------------------------------------------------------------------------
def save_model(
    model: Any,
    path: Path,
) -> None:
    """Save a LightGBM model to disk.

    Parameters
    ----------
    model : LGBMClassifier
        Trained model.
    path : Path
        Output file path.
    """
    _ensure_lightgbm()
    path.parent.mkdir(parents=True, exist_ok=True)
    model.booster_.save_model(str(path))
    log.info("Model saved: %s", path)


def save_calibrated_model(
    calibrated_model: CalibratedClassifierCV,
    path: Path,
) -> None:
    """Save a calibrated model using joblib.

    Parameters
    ----------
    calibrated_model : CalibratedClassifierCV
        Platt-scaled model.
    path : Path
        Output file path.
    """
    import joblib

    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated_model, str(path))
    log.info("Calibrated model saved: %s", path)


# ---------------------------------------------------------------------------
# Registry integration (TKT-247)
# ---------------------------------------------------------------------------
def register_models(
    metrics_inn1: Dict[str, Any],
    metrics_inn2: Dict[str, Any],
    hyperparams_inn1: Dict[str, Any],
    hyperparams_inn2: Dict[str, Any],
) -> None:
    """Register trained models in the model registry as 'experimental'.

    Per Florentino's binding condition, win probability models MUST be
    registered with status ``"experimental"`` and tagged
    ``"historical-replay-only"``.
    """
    try:
        from scripts.ml_ops.model_registry import ModelRegistry, compute_data_hash
    except ImportError:
        # Fallback: direct import when running from project root
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.ml_ops.model_registry import ModelRegistry, compute_data_hash

    registry = ModelRegistry()
    data_hash = compute_data_hash(PARQUET_PATH)

    common_tags = ["historical-replay-only", "win-probability", "TKT-207"]
    common_desc_prefix = "Historical Win Probability Replay"

    # Register innings 1 model
    registry.register(
        name="win_prob_innings1",
        version="1.0.0",
        created_by="Ime Udoka (TKT-207)",
        model_type="lightgbm",
        path="models/win_prob_innings1_v1.lgbm",
        training_data_hash=data_hash,
        hyperparameters=hyperparams_inn1,
        metrics={
            k: v
            for k, v in metrics_inn1.get("calibrated_metrics", {}).items()
            if isinstance(v, (int, float))
        },
        status="experimental",
        tags=common_tags + ["innings-1"],
        description=f"{common_desc_prefix} — 1st Innings LightGBM",
    )
    log.info("Registered win_prob_innings1 v1.0.0 as experimental")

    # Register innings 2 model
    registry.register(
        name="win_prob_innings2",
        version="1.0.0",
        created_by="Ime Udoka (TKT-207)",
        model_type="lightgbm",
        path="models/win_prob_innings2_v1.lgbm",
        training_data_hash=data_hash,
        hyperparameters=hyperparams_inn2,
        metrics={
            k: v
            for k, v in metrics_inn2.get("calibrated_metrics", {}).items()
            if isinstance(v, (int, float))
        },
        status="experimental",
        tags=common_tags + ["innings-2"],
        description=f"{common_desc_prefix} — 2nd Innings LightGBM",
    )
    log.info("Registered win_prob_innings2 v1.0.0 as experimental")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main() -> Dict[str, Any]:
    """Run the full training pipeline.

    Returns
    -------
    dict
        Complete metrics report.
    """
    t0 = time.time()

    log.info("=" * 70)
    log.info("TKT-207: Historical Win Probability Replay — Training Pipeline")
    log.info("CRITICAL: This is HISTORICAL REPLAY ONLY — NOT forward prediction")
    log.info("=" * 70)

    # ------------------------------------------------------------------
    # 1. Load and prepare data
    # ------------------------------------------------------------------
    df = load_data()
    df = assign_fold_groups(df)

    log.info(
        "Season distribution:\n%s",
        df.groupby("season").size().to_string(),
    )
    log.info(
        "Fold group distribution:\n%s",
        df.groupby("fold_group").size().to_string(),
    )

    # ------------------------------------------------------------------
    # 2. Prepare innings-specific datasets
    # ------------------------------------------------------------------
    df_inn1, features_inn1 = prepare_innings_data(df, innings=1)
    df_inn2, features_inn2 = prepare_innings_data(df, innings=2)

    # ------------------------------------------------------------------
    # 3. Cross-validation (both innings, both model types)
    # ------------------------------------------------------------------
    cv_results_inn1 = run_temporal_cv(df_inn1, features_inn1, innings=1)
    cv_results_inn2 = run_temporal_cv(df_inn2, features_inn2, innings=2)

    # ------------------------------------------------------------------
    # 4. Final model training + calibration + holdout evaluation
    # ------------------------------------------------------------------
    raw_model_inn1, cal_model_inn1, final_inn1 = train_final_model(
        df_inn1, features_inn1, innings=1
    )
    raw_model_inn2, cal_model_inn2, final_inn2 = train_final_model(
        df_inn2, features_inn2, innings=2
    )

    # ------------------------------------------------------------------
    # 5. Save models
    # ------------------------------------------------------------------
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    save_model(raw_model_inn1, MODELS_DIR / "win_prob_innings1_v1.lgbm")
    save_model(raw_model_inn2, MODELS_DIR / "win_prob_innings2_v1.lgbm")
    save_calibrated_model(cal_model_inn1, MODELS_DIR / "win_prob_innings1_v1_calibrated.joblib")
    save_calibrated_model(cal_model_inn2, MODELS_DIR / "win_prob_innings2_v1_calibrated.joblib")

    # ------------------------------------------------------------------
    # 6. Assemble and save metrics report
    # ------------------------------------------------------------------
    elapsed = time.time() - t0

    report: Dict[str, Any] = {
        "ticket": "TKT-207",
        "epic": "EPIC-018",
        "title": "Historical Win Probability Replay — Model Training Report",
        "disclaimer": (
            "HISTORICAL REPLAY ONLY. This model is trained on completed match data "
            "and produces retrospective win probability curves. It is NOT a "
            "forward-looking prediction or betting tool."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "training_time_seconds": round(elapsed, 1),
        "data_source": str(PARQUET_PATH),
        "total_training_rows": len(df),
        "innings_1": {
            "features": features_inn1,
            "n_features": len(features_inn1),
            "cross_validation": cv_results_inn1,
            "final_model": final_inn1,
        },
        "innings_2": {
            "features": features_inn2,
            "n_features": len(features_inn2),
            "cross_validation": cv_results_inn2,
            "final_model": final_inn2,
        },
        "model_comparison": {
            "description": "LightGBM vs Logistic Regression baseline comparison",
            "innings_1_lgb_brier": cv_results_inn1["lightgbm"]["mean"].get("lgb_brier_score"),
            "innings_1_lr_brier": cv_results_inn1["logistic_regression"]["mean"].get(
                "lr_brier_score"
            ),
            "innings_2_lgb_brier": cv_results_inn2["lightgbm"]["mean"].get("lgb_brier_score"),
            "innings_2_lr_brier": cv_results_inn2["logistic_regression"]["mean"].get(
                "lr_brier_score"
            ),
        },
        "models_saved": [
            "models/win_prob_innings1_v1.lgbm",
            "models/win_prob_innings2_v1.lgbm",
            "models/win_prob_innings1_v1_calibrated.joblib",
            "models/win_prob_innings2_v1_calibrated.joblib",
        ],
    }

    # Write metrics JSON
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = OUTPUT_DIR / "win_prob_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    log.info("Metrics report saved: %s", metrics_path)

    # ------------------------------------------------------------------
    # 7. Register models in registry (TKT-247 integration)
    # ------------------------------------------------------------------
    try:
        register_models(
            metrics_inn1=final_inn1,
            metrics_inn2=final_inn2,
            hyperparams_inn1=final_inn1.get("hyperparameters", {}),
            hyperparams_inn2=final_inn2.get("hyperparameters", {}),
        )
    except Exception as exc:
        log.warning("Model registration failed (non-fatal): %s", exc)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    log.info("")
    log.info("=" * 70)
    log.info("TRAINING PIPELINE COMPLETE")
    log.info("=" * 70)
    log.info("  Time elapsed  : %.1f seconds", elapsed)
    log.info("  Total rows    : %d", len(df))
    log.info("")
    log.info("  INNINGS 1 (LightGBM final holdout):")
    log.info(
        "    Brier score : %.4f (target < 0.20)",
        final_inn1["calibrated_metrics"].get("calibrated_brier_score", float("nan")),
    )
    log.info(
        "    AUC-ROC     : %.4f (target > 0.80)",
        final_inn1["calibrated_metrics"].get("calibrated_auc_roc", float("nan")),
    )
    log.info(
        "    ECE         : %.4f (target < 0.05)",
        final_inn1.get("expected_calibration_error", float("nan")),
    )
    log.info("")
    log.info("  INNINGS 2 (LightGBM final holdout):")
    log.info(
        "    Brier score : %.4f (target < 0.20)",
        final_inn2["calibrated_metrics"].get("calibrated_brier_score", float("nan")),
    )
    log.info(
        "    AUC-ROC     : %.4f (target > 0.80)",
        final_inn2["calibrated_metrics"].get("calibrated_auc_roc", float("nan")),
    )
    log.info(
        "    ECE         : %.4f (target < 0.05)",
        final_inn2.get("expected_calibration_error", float("nan")),
    )
    log.info("")
    log.info("  DISCLAIMER: Historical Win Probability Replay — NOT forward prediction.")
    log.info("=" * 70)

    return report


if __name__ == "__main__":
    main()
