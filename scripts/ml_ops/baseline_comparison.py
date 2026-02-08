#!/usr/bin/env python3
"""
TKT-137: Model Baselines Comparison for K-means Clustering

This module implements a comparison framework for evaluating the K-means
clustering approach used in player clustering against multiple baseline
methods. The comparison uses standard clustering evaluation metrics to
quantify how well K-means performs relative to alternatives.

Clustering Methods Compared:
1. Random Clustering (baseline) - Random cluster assignments
2. K-means (current method) - Centroid-based partitioning
3. Hierarchical Clustering - Agglomerative bottom-up approach
4. DBSCAN - Density-based spatial clustering

Evaluation Metrics:
- Silhouette Score: Measures cluster cohesion vs separation [-1, 1]
- Davies-Bouldin Index: Average similarity ratio (lower is better)
- Calinski-Harabasz Index: Variance ratio criterion (higher is better)

Author: Cricket Playbook ML Ops
Sprint: 2.10 - ML Ops Infrastructure
"""

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Minimum sample sizes (matching player_clustering_v2.py)
MIN_BALLS_BATTER = 300
MIN_BALLS_BOWLER = 200


@dataclass
class ClusteringResult:
    """Container for clustering results and metadata."""

    method_name: str
    labels: np.ndarray
    n_clusters: int
    silhouette: Optional[float]
    davies_bouldin: Optional[float]
    calinski_harabasz: Optional[float]
    parameters: Dict[str, Any]


@dataclass
class ComparisonReport:
    """Container for the full comparison report."""

    player_type: str
    n_samples: int
    n_features: int
    results: List[ClusteringResult]
    best_method: str
    summary: str


def load_batter_features(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Load batter features for clustering comparison.

    Uses the same data extraction approach as player_clustering_v2.py
    to ensure consistency in the comparison.

    Args:
        conn: DuckDB database connection

    Returns:
        DataFrame with batter features including phase-specific stats
    """
    df = conn.execute(
        f"""
        WITH career AS (
            SELECT player_id, player_name, balls_faced, runs, strike_rate,
                   batting_average, boundary_pct, dot_ball_pct
            FROM analytics_ipl_batting_career
            WHERE balls_faced >= {MIN_BALLS_BATTER}
        ),
        powerplay AS (
            SELECT player_id,
                   strike_rate as pp_sr,
                   boundary_pct as pp_boundary,
                   dot_ball_pct as pp_dot
            FROM analytics_ipl_batter_phase
            WHERE match_phase = 'powerplay' AND balls_faced >= 50
        ),
        middle AS (
            SELECT player_id,
                   strike_rate as mid_sr,
                   boundary_pct as mid_boundary,
                   dot_ball_pct as mid_dot
            FROM analytics_ipl_batter_phase
            WHERE match_phase = 'middle' AND balls_faced >= 50
        ),
        death AS (
            SELECT player_id,
                   strike_rate as death_sr,
                   boundary_pct as death_boundary,
                   dot_ball_pct as death_dot
            FROM analytics_ipl_batter_phase
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
            pp.pp_sr,
            pp.pp_boundary,
            pp.pp_dot,
            m.mid_sr,
            m.mid_boundary,
            m.mid_dot,
            d.death_sr,
            d.death_boundary,
            d.death_dot
        FROM career c
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        WHERE pp.pp_sr IS NOT NULL OR m.mid_sr IS NOT NULL
        """
    ).df()

    return df


def load_bowler_features(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Load bowler features for clustering comparison.

    Uses the same data extraction approach as player_clustering_v2.py
    to ensure consistency in the comparison.

    Args:
        conn: DuckDB database connection

    Returns:
        DataFrame with bowler features including phase-specific stats
    """
    df = conn.execute(
        f"""
        WITH career AS (
            SELECT player_id, player_name, balls_bowled, wickets,
                   economy_rate, bowling_average, bowling_strike_rate,
                   dot_ball_pct, boundary_conceded_pct
            FROM analytics_ipl_bowling_career
            WHERE balls_bowled >= {MIN_BALLS_BOWLER}
        ),
        powerplay AS (
            SELECT player_id,
                   economy_rate as pp_economy,
                   dot_ball_pct as pp_dot,
                   boundary_conceded_pct as pp_boundary
            FROM analytics_ipl_bowler_phase
            WHERE match_phase = 'powerplay' AND balls_bowled >= 30
        ),
        middle AS (
            SELECT player_id,
                   economy_rate as mid_economy,
                   dot_ball_pct as mid_dot,
                   boundary_conceded_pct as mid_boundary
            FROM analytics_ipl_bowler_phase
            WHERE match_phase = 'middle' AND balls_bowled >= 30
        ),
        death AS (
            SELECT player_id,
                   economy_rate as death_economy,
                   dot_ball_pct as death_dot,
                   boundary_conceded_pct as death_boundary
            FROM analytics_ipl_bowler_phase
            WHERE match_phase = 'death' AND balls_bowled >= 30
        ),
        phase_distribution AS (
            SELECT bowler_id as player_id,
                   MAX(CASE WHEN match_phase = 'powerplay' THEN pct_overs_in_phase END) as pp_pct,
                   MAX(CASE WHEN match_phase = 'middle' THEN pct_overs_in_phase END) as mid_pct,
                   MAX(CASE WHEN match_phase = 'death' THEN pct_overs_in_phase END) as death_pct
            FROM analytics_ipl_bowler_phase_distribution
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
            pd.death_pct
        FROM career c
        LEFT JOIN powerplay pp ON c.player_id = pp.player_id
        LEFT JOIN middle m ON c.player_id = m.player_id
        LEFT JOIN death d ON c.player_id = d.player_id
        LEFT JOIN phase_distribution pd ON c.player_id = pd.player_id
        WHERE pp.pp_economy IS NOT NULL OR m.mid_economy IS NOT NULL OR d.death_economy IS NOT NULL
        """
    ).df()

    return df


def prepare_features(df: pd.DataFrame, feature_cols: List[str]) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Prepare and scale features for clustering.

    Args:
        df: Raw DataFrame with player data
        feature_cols: List of column names to use as features

    Returns:
        Tuple of (scaled feature array, cleaned DataFrame)
    """
    df_clean = df.copy()

    # Fill missing values with median
    for col in feature_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    # Drop rows with any remaining NaN in feature columns
    available_cols = [c for c in feature_cols if c in df_clean.columns]
    df_clean = df_clean.dropna(subset=available_cols)

    # Scale features
    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[available_cols])

    return X, df_clean


def compute_metrics(
    X: np.ndarray, labels: np.ndarray
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Compute clustering evaluation metrics.

    Args:
        X: Feature matrix
        labels: Cluster labels

    Returns:
        Tuple of (silhouette_score, davies_bouldin_index, calinski_harabasz_index)
        Returns None for metrics that cannot be computed (e.g., single cluster)
    """
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)

    # Metrics require at least 2 clusters and samples not all in one cluster
    if n_clusters < 2 or n_clusters >= len(X):
        return None, None, None

    # Filter out noise points for DBSCAN (label = -1)
    mask = labels != -1
    if mask.sum() < 2 or len(np.unique(labels[mask])) < 2:
        return None, None, None

    try:
        silhouette = silhouette_score(X[mask], labels[mask])
    except Exception:
        silhouette = None

    try:
        davies_bouldin = davies_bouldin_score(X[mask], labels[mask])
    except Exception:
        davies_bouldin = None

    try:
        calinski_harabasz = calinski_harabasz_score(X[mask], labels[mask])
    except Exception:
        calinski_harabasz = None

    return silhouette, davies_bouldin, calinski_harabasz


def random_clustering(X: np.ndarray, n_clusters: int, random_state: int = 42) -> ClusteringResult:
    """
    Perform random clustering as a baseline.

    Randomly assigns each sample to one of n_clusters.
    This provides a lower bound for what a clustering algorithm should achieve.

    Args:
        X: Feature matrix (n_samples, n_features)
        n_clusters: Number of clusters to create
        random_state: Random seed for reproducibility

    Returns:
        ClusteringResult with random assignments and metrics
    """
    np.random.seed(random_state)
    labels = np.random.randint(0, n_clusters, size=X.shape[0])

    silhouette, davies_bouldin, calinski_harabasz = compute_metrics(X, labels)

    return ClusteringResult(
        method_name="Random (Baseline)",
        labels=labels,
        n_clusters=n_clusters,
        silhouette=silhouette,
        davies_bouldin=davies_bouldin,
        calinski_harabasz=calinski_harabasz,
        parameters={"n_clusters": n_clusters, "random_state": random_state},
    )


def kmeans_clustering(X: np.ndarray, n_clusters: int, random_state: int = 42) -> ClusteringResult:
    """
    Perform K-means clustering (current production method).

    Uses sklearn's K-means implementation with the same parameters
    as player_clustering_v2.py for fair comparison.

    Args:
        X: Feature matrix (n_samples, n_features)
        n_clusters: Number of clusters
        random_state: Random seed for reproducibility

    Returns:
        ClusteringResult with K-means assignments and metrics
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)

    silhouette, davies_bouldin, calinski_harabasz = compute_metrics(X, labels)

    return ClusteringResult(
        method_name="K-means (Current)",
        labels=labels,
        n_clusters=n_clusters,
        silhouette=silhouette,
        davies_bouldin=davies_bouldin,
        calinski_harabasz=calinski_harabasz,
        parameters={
            "n_clusters": n_clusters,
            "n_init": 10,
            "random_state": random_state,
            "inertia": kmeans.inertia_,
        },
    )


def hierarchical_clustering(
    X: np.ndarray, n_clusters: int, linkage: str = "ward"
) -> ClusteringResult:
    """
    Perform hierarchical agglomerative clustering.

    Uses bottom-up agglomerative approach which can capture
    hierarchical structure in the data that K-means might miss.

    Args:
        X: Feature matrix (n_samples, n_features)
        n_clusters: Number of clusters
        linkage: Linkage criterion ('ward', 'complete', 'average', 'single')

    Returns:
        ClusteringResult with hierarchical assignments and metrics
    """
    model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
    labels = model.fit_predict(X)

    silhouette, davies_bouldin, calinski_harabasz = compute_metrics(X, labels)

    return ClusteringResult(
        method_name=f"Hierarchical ({linkage})",
        labels=labels,
        n_clusters=n_clusters,
        silhouette=silhouette,
        davies_bouldin=davies_bouldin,
        calinski_harabasz=calinski_harabasz,
        parameters={"n_clusters": n_clusters, "linkage": linkage},
    )


def dbscan_clustering(X: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> ClusteringResult:
    """
    Perform DBSCAN density-based clustering.

    DBSCAN can discover clusters of arbitrary shape and automatically
    determines the number of clusters. Points not belonging to any
    cluster are labeled as noise (-1).

    Args:
        X: Feature matrix (n_samples, n_features)
        eps: Maximum distance between samples for neighborhood
        min_samples: Minimum samples in neighborhood to form cluster

    Returns:
        ClusteringResult with DBSCAN assignments and metrics
    """
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X)

    # Count actual clusters (excluding noise label -1)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = (labels == -1).sum()

    silhouette, davies_bouldin, calinski_harabasz = compute_metrics(X, labels)

    return ClusteringResult(
        method_name="DBSCAN",
        labels=labels,
        n_clusters=n_clusters,
        silhouette=silhouette,
        davies_bouldin=davies_bouldin,
        calinski_harabasz=calinski_harabasz,
        parameters={
            "eps": eps,
            "min_samples": min_samples,
            "n_noise_points": n_noise,
        },
    )


def find_optimal_dbscan_eps(X: np.ndarray, min_samples: int = 5) -> float:
    """
    Find a reasonable eps value for DBSCAN using k-distance heuristic.

    Args:
        X: Feature matrix
        min_samples: min_samples parameter for DBSCAN

    Returns:
        Suggested eps value
    """
    from sklearn.neighbors import NearestNeighbors

    nn = NearestNeighbors(n_neighbors=min_samples)
    nn.fit(X)
    distances, _ = nn.kneighbors(X)

    # Use the knee point of the k-distance graph
    k_distances = np.sort(distances[:, min_samples - 1])
    knee_point = int(len(k_distances) * 0.9)  # 90th percentile

    return float(k_distances[knee_point])


def run_comparison(X: np.ndarray, n_clusters: int = 5) -> List[ClusteringResult]:
    """
    Run all clustering methods and collect results.

    Args:
        X: Feature matrix (n_samples, n_features)
        n_clusters: Target number of clusters for applicable methods

    Returns:
        List of ClusteringResult for each method
    """
    results = []

    # 1. Random baseline
    print("  Running Random clustering (baseline)...")
    results.append(random_clustering(X, n_clusters))

    # 2. K-means (current method)
    print("  Running K-means clustering...")
    results.append(kmeans_clustering(X, n_clusters))

    # 3. Hierarchical clustering
    print("  Running Hierarchical clustering (ward)...")
    results.append(hierarchical_clustering(X, n_clusters, linkage="ward"))

    # 4. DBSCAN with auto-tuned eps
    print("  Running DBSCAN clustering...")
    eps = find_optimal_dbscan_eps(X)
    results.append(dbscan_clustering(X, eps=eps, min_samples=5))

    return results


def generate_report(
    player_type: str,
    n_samples: int,
    n_features: int,
    results: List[ClusteringResult],
) -> ComparisonReport:
    """
    Generate a comparison report from clustering results.

    Args:
        player_type: 'batter' or 'bowler'
        n_samples: Number of samples clustered
        n_features: Number of features used
        results: List of ClusteringResult from each method

    Returns:
        ComparisonReport with analysis and recommendations
    """
    # Determine best method by silhouette score (higher is better)
    valid_results = [r for r in results if r.silhouette is not None]
    if valid_results:
        best = max(valid_results, key=lambda r: r.silhouette)
        best_method = best.method_name
    else:
        best_method = "Unable to determine"

    # Generate summary text
    summary_lines = [
        f"Comparison of {len(results)} clustering methods on {player_type} data:",
        f"  - Samples: {n_samples}",
        f"  - Features: {n_features}",
        "",
    ]

    # Add metric comparison
    kmeans_result = next((r for r in results if "K-means" in r.method_name), None)
    random_result = next((r for r in results if "Random" in r.method_name), None)

    if kmeans_result and random_result:
        if kmeans_result.silhouette and random_result.silhouette:
            improvement = (
                (kmeans_result.silhouette - random_result.silhouette)
                / abs(random_result.silhouette)
                * 100
                if random_result.silhouette != 0
                else float("inf")
            )
            summary_lines.append(
                f"K-means silhouette improvement over random baseline: {improvement:+.1f}%"
            )

    summary_lines.append(f"\nBest performing method: {best_method}")

    return ComparisonReport(
        player_type=player_type,
        n_samples=n_samples,
        n_features=n_features,
        results=results,
        best_method=best_method,
        summary="\n".join(summary_lines),
    )


def print_report(report: ComparisonReport) -> None:
    """
    Print a formatted comparison report to stdout.

    Args:
        report: ComparisonReport to display
    """
    print("\n" + "=" * 80)
    print(f"CLUSTERING COMPARISON REPORT: {report.player_type.upper()}S")
    print("=" * 80)
    print(f"\nDataset: {report.n_samples} samples, {report.n_features} features")

    # Results table header
    print("\n" + "-" * 80)
    print(
        f"{'Method':<25} {'Clusters':>10} {'Silhouette':>12} "
        f"{'Davies-Bouldin':>15} {'Calinski-H':>12}"
    )
    print("-" * 80)

    # Print each result
    for r in report.results:
        sil = f"{r.silhouette:.4f}" if r.silhouette is not None else "N/A"
        db = f"{r.davies_bouldin:.4f}" if r.davies_bouldin is not None else "N/A"
        ch = f"{r.calinski_harabasz:.1f}" if r.calinski_harabasz is not None else "N/A"

        print(f"{r.method_name:<25} {r.n_clusters:>10} {sil:>12} {db:>15} {ch:>12}")

    print("-" * 80)

    # Metric interpretation
    print("\nMetric Interpretation:")
    print("  - Silhouette Score: Higher is better (range: -1 to 1)")
    print("  - Davies-Bouldin Index: Lower is better (range: 0 to infinity)")
    print("  - Calinski-Harabasz Index: Higher is better")

    # K-means vs baseline analysis
    kmeans_result = next((r for r in report.results if "K-means" in r.method_name), None)
    random_result = next((r for r in report.results if "Random" in r.method_name), None)

    if kmeans_result and random_result:
        print("\n" + "-" * 80)
        print("K-MEANS VS BASELINE ANALYSIS")
        print("-" * 80)

        if kmeans_result.silhouette and random_result.silhouette:
            sil_diff = kmeans_result.silhouette - random_result.silhouette
            print(
                f"  Silhouette improvement: {sil_diff:+.4f} "
                f"({kmeans_result.silhouette:.4f} vs {random_result.silhouette:.4f})"
            )

        if kmeans_result.davies_bouldin and random_result.davies_bouldin:
            db_diff = random_result.davies_bouldin - kmeans_result.davies_bouldin
            print(
                f"  Davies-Bouldin improvement: {db_diff:+.4f} "
                f"({kmeans_result.davies_bouldin:.4f} vs {random_result.davies_bouldin:.4f})"
            )

        if kmeans_result.calinski_harabasz and random_result.calinski_harabasz:
            ch_diff = kmeans_result.calinski_harabasz - random_result.calinski_harabasz
            print(
                f"  Calinski-Harabasz improvement: {ch_diff:+.1f} "
                f"({kmeans_result.calinski_harabasz:.1f} vs {random_result.calinski_harabasz:.1f})"
            )

    # Best method summary
    print("\n" + "-" * 80)
    print(f"BEST METHOD: {report.best_method}")
    print("-" * 80)

    # Additional method details
    print("\nMethod Details:")
    for r in report.results:
        params = ", ".join(f"{k}={v}" for k, v in r.parameters.items())
        print(f"  {r.method_name}: {params}")


def main() -> int:
    """
    Main entry point for baseline comparison.

    Loads player data, runs all clustering methods, and outputs
    a comparison report showing K-means performance vs baselines.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    print("=" * 80)
    print("TKT-137: Model Baselines Comparison for K-means Clustering")
    print("=" * 80)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH))

    try:
        # === BATTER COMPARISON ===
        print("\n" + "=" * 80)
        print("LOADING BATTER DATA")
        print("=" * 80)

        batter_df = load_batter_features(conn)
        print(f"  Loaded {len(batter_df)} batters")

        batter_feature_cols = [
            "overall_sr",
            "overall_avg",
            "overall_boundary",
            "overall_dot",
            "pp_sr",
            "pp_boundary",
            "mid_sr",
            "mid_boundary",
            "death_sr",
            "death_boundary",
        ]

        X_batters, df_batters_clean = prepare_features(batter_df, batter_feature_cols)
        print(f"  Prepared {X_batters.shape[0]} samples with {X_batters.shape[1]} features")

        print("\nRunning clustering methods on batters...")
        batter_results = run_comparison(X_batters, n_clusters=5)
        batter_report = generate_report(
            "batter", X_batters.shape[0], X_batters.shape[1], batter_results
        )
        print_report(batter_report)

        # === BOWLER COMPARISON ===
        print("\n" + "=" * 80)
        print("LOADING BOWLER DATA")
        print("=" * 80)

        bowler_df = load_bowler_features(conn)
        print(f"  Loaded {len(bowler_df)} bowlers")

        bowler_feature_cols = [
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
        ]

        X_bowlers, df_bowlers_clean = prepare_features(bowler_df, bowler_feature_cols)
        print(f"  Prepared {X_bowlers.shape[0]} samples with {X_bowlers.shape[1]} features")

        print("\nRunning clustering methods on bowlers...")
        bowler_results = run_comparison(X_bowlers, n_clusters=5)
        bowler_report = generate_report(
            "bowler", X_bowlers.shape[0], X_bowlers.shape[1], bowler_results
        )
        print_report(bowler_report)

        # === FINAL SUMMARY ===
        print("\n" + "=" * 80)
        print("FINAL SUMMARY")
        print("=" * 80)
        print(f"\nBatters best method: {batter_report.best_method}")
        print(f"Bowlers best method: {bowler_report.best_method}")

        # Check if K-means is performing well
        batter_kmeans = next((r for r in batter_results if "K-means" in r.method_name), None)
        bowler_kmeans = next((r for r in bowler_results if "K-means" in r.method_name), None)

        print("\nK-means Performance Assessment:")
        if batter_kmeans and batter_kmeans.silhouette:
            if batter_kmeans.silhouette > 0.3:
                print("  Batters: Strong cluster structure (silhouette > 0.3)")
            elif batter_kmeans.silhouette > 0.1:
                print("  Batters: Moderate cluster structure (silhouette 0.1-0.3)")
            else:
                print("  Batters: Weak cluster structure (silhouette < 0.1)")

        if bowler_kmeans and bowler_kmeans.silhouette:
            if bowler_kmeans.silhouette > 0.3:
                print("  Bowlers: Strong cluster structure (silhouette > 0.3)")
            elif bowler_kmeans.silhouette > 0.1:
                print("  Bowlers: Moderate cluster structure (silhouette 0.1-0.3)")
            else:
                print("  Bowlers: Weak cluster structure (silhouette < 0.1)")

        print("\n" + "=" * 80)
        print("Comparison complete. K-means baseline comparison finished.")
        print("=" * 80)

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    exit(main())
