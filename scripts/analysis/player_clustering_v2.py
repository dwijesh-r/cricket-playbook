#!/usr/bin/env python3
"""
Cricket Playbook - Player Clustering Model V2
Author: Stephen Curry (Analytics Lead)
Sprint: 2.9 - Entry Point Bug Fix

V2 Improvements (from Founder Review #1):
1. Recency weighting - 2x weight for 2021-2025 data
2. Batting position / entry point feature for batters
3. Wickets and strike rate per phase for bowlers
4. PCA variance analysis with 50% target
5. Feature correlation cleanup (remove r > 0.9)
6. Player classification validation

Changes from V1:
- Added avg_batting_position feature
- Added wickets_per_phase and bowling_sr_per_phase
- Implemented recency weighting
- Added PCA variance reporting
- Added correlation matrix analysis

Bug Fix (Sprint 2.9):
- Fixed avg_batting_position to use legal ball count, not ball_seq
- ball_seq includes wides/no-balls and can exceed 120 per innings
- Now uses cumulative legal ball count for accurate position estimation

Data Scope (TKT-181):
- Uses _since2023 views (IPL 2023-2025) for clustering to reflect current form
- All-time historical data available via _alltime view variants if needed
"""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Tuple

import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # analysis -> scripts -> project root
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Recent seasons for weighting (2x weight)
RECENT_SEASONS = [2021, 2022, 2023, 2024, 2025]

# Minimum sample sizes
MIN_BALLS_BATTER = 300  # Reduced from 500 to include more players
MIN_BALLS_BOWLER = 200  # Reduced from 300


def get_batter_features_v2(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Extract batter feature vectors with batting position and recency weighting."""

    df = conn.execute(
        """
        WITH recent_balls AS (
            -- Get balls from recent seasons (2021+) for recency weighting
            SELECT
                fb.batter_id as player_id,
                COUNT(*) as recent_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND (dm.season LIKE '2021%' OR dm.season LIKE '2022%' OR dm.season LIKE '2023%' OR dm.season LIKE '2024%' OR dm.season LIKE '2025%')
            GROUP BY fb.batter_id
        ),
        legal_balls_numbered AS (
            -- Number only legal balls within each innings (not wides/no-balls)
            SELECT
                fb.match_id,
                fb.innings,
                fb.batter_id,
                fb.ball_seq,
                fb.is_legal_ball,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) as legal_ball_num
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        batting_position AS (
            -- Calculate average batting position using LEGAL ball count
            SELECT
                batter_id as player_id,
                AVG(batting_position) as avg_batting_position
            FROM (
                SELECT
                    batter_id,
                    match_id,
                    innings,
                    MIN(legal_ball_num) as first_legal_ball,
                    -- Estimate batting position based on when they first face a LEGAL ball
                    CASE
                        WHEN MIN(legal_ball_num) <= 6 THEN 1  -- Opener
                        WHEN MIN(legal_ball_num) <= 24 THEN 2  -- #3
                        WHEN MIN(legal_ball_num) <= 48 THEN 3  -- #4
                        WHEN MIN(legal_ball_num) <= 72 THEN 4  -- #5
                        WHEN MIN(legal_ball_num) <= 96 THEN 5  -- #6
                        ELSE 6  -- Lower order
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
            -- Recency weight: 1.0 for old players, up to 2.0 for recent players
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


def get_bowler_features_v2(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Extract bowler feature vectors with wickets per phase."""

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
              AND (dm.season LIKE '2021%' OR dm.season LIKE '2022%' OR dm.season LIKE '2023%' OR dm.season LIKE '2024%' OR dm.season LIKE '2025%')
              AND fb.is_legal_ball = TRUE
            GROUP BY fb.bowler_id
        ),
        wickets_by_phase AS (
            -- Calculate wickets per phase
            SELECT
                fb.bowler_id as player_id,
                SUM(CASE WHEN fb.match_phase = 'powerplay' AND fb.is_wicket THEN 1 ELSE 0 END) as pp_wickets,
                SUM(CASE WHEN fb.match_phase = 'middle' AND fb.is_wicket THEN 1 ELSE 0 END) as mid_wickets,
                SUM(CASE WHEN fb.match_phase = 'death' AND fb.is_wicket THEN 1 ELSE 0 END) as death_wickets,
                SUM(CASE WHEN fb.match_phase = 'powerplay' AND fb.is_legal_ball THEN 1 ELSE 0 END) as pp_balls,
                SUM(CASE WHEN fb.match_phase = 'middle' AND fb.is_legal_ball THEN 1 ELSE 0 END) as mid_balls,
                SUM(CASE WHEN fb.match_phase = 'death' AND fb.is_legal_ball THEN 1 ELSE 0 END) as death_balls
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
                   MAX(CASE WHEN match_phase = 'powerplay' THEN pct_overs_in_phase END) as pp_pct,
                   MAX(CASE WHEN match_phase = 'middle' THEN pct_overs_in_phase END) as mid_pct,
                   MAX(CASE WHEN match_phase = 'death' THEN pct_overs_in_phase END) as death_pct
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
            -- Wickets per phase
            COALESCE(wp.pp_wickets, 0) as pp_wickets,
            COALESCE(wp.mid_wickets, 0) as mid_wickets,
            COALESCE(wp.death_wickets, 0) as death_wickets,
            -- Bowling strike rate per phase (balls per wicket)
            CASE WHEN wp.pp_wickets > 0 THEN wp.pp_balls * 1.0 / wp.pp_wickets ELSE NULL END as pp_bowling_sr,
            CASE WHEN wp.mid_wickets > 0 THEN wp.mid_balls * 1.0 / wp.mid_wickets ELSE NULL END as mid_bowling_sr,
            CASE WHEN wp.death_wickets > 0 THEN wp.death_balls * 1.0 / wp.death_wickets ELSE NULL END as death_bowling_sr,
            -- Recency weight
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
        WHERE pp.pp_economy IS NOT NULL OR m.mid_economy IS NOT NULL OR d.death_economy IS NOT NULL
    """.format(min_balls=MIN_BALLS_BOWLER)
    ).df()

    return df


def analyze_correlations(
    df: pd.DataFrame, feature_cols: List[str], threshold: float = 0.9
) -> List[str]:
    """Analyze feature correlations and return columns to drop."""

    numeric_df = df[feature_cols].dropna()
    if len(numeric_df) < 10:
        return []

    corr_matrix = numeric_df.corr().abs()

    # Find highly correlated pairs
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    to_drop = []
    for col in upper.columns:
        if any(upper[col] > threshold):
            correlated_with = upper.index[upper[col] > threshold].tolist()
            print(f"    {col} highly correlated with: {correlated_with}")
            # Drop the one that appears later in the list
            if col not in to_drop:
                to_drop.append(col)

    return to_drop


def pca_variance_analysis(
    X: np.ndarray, feature_cols: List[str], target_variance: float = 0.5
) -> Dict[str, Any]:
    """Perform PCA and analyze variance explained."""

    pca = PCA()
    pca.fit(X)

    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)

    # Find number of components for target variance
    n_components_target = np.argmax(cumulative_variance >= target_variance) + 1

    result = {
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "cumulative_variance": cumulative_variance,
        "n_components_for_target": n_components_target,
        "variance_at_target": cumulative_variance[n_components_target - 1]
        if n_components_target <= len(cumulative_variance)
        else cumulative_variance[-1],
        "total_components": len(feature_cols),
    }

    return result


def cluster_batters_v2(df: pd.DataFrame, n_clusters: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Cluster batters with V2 improvements."""

    # V2 features including batting position
    feature_cols = [
        "overall_sr",
        "overall_avg",
        "overall_boundary",
        "overall_dot",
        "avg_batting_position",  # NEW: batting entry point
        "pp_sr",
        "pp_boundary",
        "mid_sr",
        "mid_boundary",
        "death_sr",
        "death_boundary",
    ]

    # Filter to rows with key features
    df_clean = df.dropna(subset=["overall_sr", "overall_avg"]).copy()

    # Fill missing phase data with career averages
    for col in feature_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    print("\n  Correlation Analysis:")
    cols_to_drop = analyze_correlations(df_clean, feature_cols)
    if cols_to_drop:
        print(f"    Removing highly correlated: {cols_to_drop}")
        feature_cols = [c for c in feature_cols if c not in cols_to_drop]
    else:
        print("    No features exceed r=0.9 threshold")

    if len(df_clean) < n_clusters:
        print(f"  Warning: Only {len(df_clean)} batters with complete data")
        n_clusters = min(n_clusters, len(df_clean))

    # Normalize features with recency weighting
    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[feature_cols])

    # Apply recency weighting
    if "recency_weight" in df_clean.columns:
        weights = df_clean["recency_weight"].values.reshape(-1, 1)
        X = X * np.sqrt(weights)  # Square root to moderate the effect

    # PCA variance analysis
    print("\n  PCA Variance Analysis:")
    pca_result = pca_variance_analysis(X, feature_cols)
    print(
        f"    Components for 50% variance: {pca_result['n_components_for_target']} of {pca_result['total_components']}"
    )
    print(
        f"    Variance explained by first 3 PCs: {pca_result['cumulative_variance'][2] * 100:.1f}%"
    )

    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean["cluster"] = kmeans.fit_predict(X)

    # Cluster centers
    centers = pd.DataFrame(
        scaler.inverse_transform(
            kmeans.cluster_centers_ / np.sqrt(weights.mean())
            if "recency_weight" in df_clean.columns
            else kmeans.cluster_centers_
        ),
        columns=feature_cols,
    )
    centers["cluster"] = range(n_clusters)

    return df_clean, centers, pca_result


def cluster_bowlers_v2(df: pd.DataFrame, n_clusters: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Cluster bowlers with V2 improvements including wickets per phase."""

    # V2 features including wickets per phase
    feature_cols = [
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
        "death_wickets",  # NEW: wickets per phase
    ]

    df_clean = df.dropna(subset=["overall_economy"]).copy()

    # Fill missing data
    for col in feature_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())

    print("\n  Correlation Analysis:")
    cols_to_drop = analyze_correlations(df_clean, feature_cols)
    if cols_to_drop:
        print(f"    Removing highly correlated: {cols_to_drop}")
        feature_cols = [c for c in feature_cols if c not in cols_to_drop]
    else:
        print("    No features exceed r=0.9 threshold")

    if len(df_clean) < n_clusters:
        print(f"  Warning: Only {len(df_clean)} bowlers with complete data")
        n_clusters = min(n_clusters, len(df_clean))

    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[feature_cols])

    # Apply recency weighting
    if "recency_weight" in df_clean.columns:
        weights = df_clean["recency_weight"].values.reshape(-1, 1)
        X = X * np.sqrt(weights)

    # PCA variance analysis
    print("\n  PCA Variance Analysis:")
    pca_result = pca_variance_analysis(X, feature_cols)
    print(
        f"    Components for 50% variance: {pca_result['n_components_for_target']} of {pca_result['total_components']}"
    )
    print(
        f"    Variance explained by first 3 PCs: {pca_result['cumulative_variance'][2] * 100:.1f}%"
    )

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean["cluster"] = kmeans.fit_predict(X)

    centers = pd.DataFrame(
        scaler.inverse_transform(
            kmeans.cluster_centers_ / np.sqrt(weights.mean())
            if "recency_weight" in df_clean.columns
            else kmeans.cluster_centers_
        ),
        columns=feature_cols,
    )
    centers["cluster"] = range(n_clusters)

    return df_clean, centers, pca_result


def validate_specific_players(batter_df: pd.DataFrame, bowler_df: pd.DataFrame) -> None:
    """Validate classifications for players mentioned in Founder Review."""

    print("\n" + "=" * 70)
    print("PLAYER CLASSIFICATION VALIDATION (Founder Review Items)")
    print("=" * 70)

    # Players to validate
    batter_checks = [
        ("MS Dhoni", "Should be FINISHER, good in death overs"),
        ("Jos Buttler", "Bats at top order (1-4) in recent years"),
        ("Rajat Patidar", "Bats at 1-4, explosive"),
        ("Rishabh Pant", "Bats at 1-4, aggressive"),
        ("Suryakumar Yadav", "Bats at 1-4, goes berzerk"),
    ]

    bowler_checks = [
        ("Anrich Nortje", "Should NOT be part-timer - specialist fast bowler"),
    ]

    print("\n  BATTER VALIDATIONS:")
    for player_name, note in batter_checks:
        matches = batter_df[
            batter_df["player_name"].str.contains(player_name.split()[0], case=False, na=False)
        ]
        if len(matches) > 0:
            row = matches.iloc[0]
            print(f"\n  {row['player_name']}:")
            print(f"    Cluster: {row['cluster']}")
            print(
                f"    Avg Batting Position: {row.get('avg_batting_position', 'N/A'):.1f}"
                if pd.notna(row.get("avg_batting_position"))
                else "    Avg Batting Position: N/A"
            )
            print(
                f"    Death SR: {row.get('death_sr', 'N/A'):.1f}"
                if pd.notna(row.get("death_sr"))
                else "    Death SR: N/A"
            )
            print(f"    Overall SR: {row['overall_sr']:.1f}")
            print(f"    Note: {note}")
        else:
            print(f"\n  {player_name}: NOT FOUND in dataset")

    print("\n  BOWLER VALIDATIONS:")
    for player_name, note in bowler_checks:
        matches = bowler_df[
            bowler_df["player_name"].str.contains(player_name.split()[0], case=False, na=False)
        ]
        if len(matches) > 0:
            row = matches.iloc[0]
            print(f"\n  {row['player_name']}:")
            print(f"    Cluster: {row['cluster']}")
            print(f"    Balls Bowled: {row['balls_bowled']}")
            print(f"    Wickets: {row['wickets']}")
            print(f"    Economy: {row['overall_economy']:.2f}")
            print(f"    Note: {note}")
        else:
            print(f"\n  {player_name}: NOT FOUND in dataset")


def analyze_clusters_v2(df: pd.DataFrame, centers: pd.DataFrame, player_type: str) -> None:
    """Print cluster analysis with V2 features."""

    print(f"\n{'=' * 70}")
    print(f"{player_type.upper()} CLUSTER ANALYSIS (V2)")
    print(f"{'=' * 70}")

    for cluster_id in sorted(df["cluster"].unique()):
        cluster_players = df[df["cluster"] == cluster_id]
        center = centers[centers["cluster"] == cluster_id].iloc[0]

        print(f"\n--- CLUSTER {cluster_id} ({len(cluster_players)} players) ---")

        if player_type == "batter":
            print(
                f"  Avg Batting Position: {center.get('avg_batting_position', 'N/A'):.1f}"
                if "avg_batting_position" in center
                else ""
            )
            print(f"  Overall SR: {center['overall_sr']:.1f} | Avg: {center['overall_avg']:.1f}")
            print(f"  Boundary%: {center['overall_boundary']:.1f}%")
            print(
                f"  PP SR: {center.get('pp_sr', 0):.1f} | Mid SR: {center.get('mid_sr', 0):.1f} | Death SR: {center.get('death_sr', 0):.1f}"
            )
        else:
            print(
                f"  Overall Economy: {center['overall_economy']:.2f} | SR: {center.get('overall_sr', 0):.1f}"
            )
            print(f"  Dot Ball%: {center['overall_dot']:.1f}%")
            print(
                f"  PP Econ: {center.get('pp_economy', 0):.2f} | Mid: {center.get('mid_economy', 0):.2f} | Death: {center.get('death_economy', 0):.2f}"
            )
            print(
                f"  Wickets - PP: {center.get('pp_wickets', 0):.0f} | Mid: {center.get('mid_wickets', 0):.0f} | Death: {center.get('death_wickets', 0):.0f}"
            )
            print(
                f"  Phase%: PP {center.get('pp_pct', 0):.1f}% | Mid {center.get('mid_pct', 0):.1f}% | Death {center.get('death_pct', 0):.1f}%"
            )

        # Show top players
        print("\n  Players:")
        for _, player in cluster_players.head(8).iterrows():
            if player_type == "batter":
                pos = (
                    f", Pos:{player.get('avg_batting_position', 0):.1f}"
                    if pd.notna(player.get("avg_batting_position"))
                    else ""
                )
                print(f"    - {player['player_name']} (SR: {player['overall_sr']:.1f}{pos})")
            else:
                print(
                    f"    - {player['player_name']} (Econ: {player['overall_economy']:.2f}, Wkts: {int(player['wickets'])})"
                )

        if len(cluster_players) > 8:
            print(f"    ... and {len(cluster_players) - 8} more")


def compute_feature_importance(centers: pd.DataFrame, feature_cols: List[str]) -> Dict[str, Any]:
    """Compute feature importance for clustering using centroid variance analysis (TKT-142).

    For each feature, measures how much the cluster centroids differ from
    the global mean — features with high inter-cluster variance are important
    for distinguishing clusters.

    This approach doesn't require SHAP/LIME and works purely from the
    K-Means centroids, making it fast and dependency-free.
    """
    importance = {}
    for col in feature_cols:
        if col in centers.columns:
            # Inter-cluster variance (how spread the centroids are)
            col_values = centers[col].values
            variance = np.var(col_values)
            # Normalize by range to make comparable
            col_range = np.ptp(col_values) if np.ptp(col_values) > 0 else 1.0
            importance[col] = {
                "variance": float(variance),
                "range": float(col_range),
                "normalized_importance": float(variance / (col_range**2)) if col_range > 0 else 0,
            }

    # Rank by normalized importance
    sorted_features = sorted(
        importance.items(), key=lambda x: x[1]["normalized_importance"], reverse=True
    )
    for rank, (feat, data) in enumerate(sorted_features, 1):
        data["rank"] = rank

    return importance


def save_cluster_explanations(
    batter_df: pd.DataFrame,
    bowler_df: pd.DataFrame,
    batter_centers: pd.DataFrame,
    bowler_centers: pd.DataFrame,
    batter_features: List[str],
    bowler_features: List[str],
) -> None:
    """Save cluster explanations to JSON output (TKT-142)."""
    import json
    from datetime import datetime

    output_path = OUTPUT_DIR / "tags" / "cluster_explanations.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    batter_importance = compute_feature_importance(batter_centers, batter_features)
    bowler_importance = compute_feature_importance(bowler_centers, bowler_features)

    explanations = {
        "generated_at": datetime.now().isoformat(),
        "model_version": "2.0.0",
        "ticket": "TKT-142",
        "batter_clusters": {
            "n_clusters": len(batter_centers),
            "n_players": len(batter_df),
            "feature_importance": batter_importance,
            "cluster_profiles": {},
        },
        "bowler_clusters": {
            "n_clusters": len(bowler_centers),
            "n_players": len(bowler_df),
            "feature_importance": bowler_importance,
            "cluster_profiles": {},
        },
    }

    # Add cluster profiles with top players
    for cluster_id in sorted(batter_df["cluster"].unique()):
        players = batter_df[batter_df["cluster"] == cluster_id]
        center = batter_centers[batter_centers["cluster"] == cluster_id].iloc[0]
        explanations["batter_clusters"]["cluster_profiles"][str(cluster_id)] = {
            "size": len(players),
            "avg_sr": round(float(center.get("overall_sr", 0)), 1),
            "avg_position": round(float(center.get("avg_batting_position", 0)), 1),
            "top_players": players.head(5)["player_name"].tolist(),
            "distinguishing_features": [
                f
                for f, d in sorted(
                    batter_importance.items(),
                    key=lambda x: x[1]["rank"],
                )[:3]
            ],
        }

    for cluster_id in sorted(bowler_df["cluster"].unique()):
        players = bowler_df[bowler_df["cluster"] == cluster_id]
        center = bowler_centers[bowler_centers["cluster"] == cluster_id].iloc[0]
        explanations["bowler_clusters"]["cluster_profiles"][str(cluster_id)] = {
            "size": len(players),
            "avg_economy": round(float(center.get("overall_economy", 0)), 2),
            "top_players": players.head(5)["player_name"].tolist(),
            "distinguishing_features": [
                f
                for f, d in sorted(
                    bowler_importance.items(),
                    key=lambda x: x[1]["rank"],
                )[:3]
            ],
        }

    with open(output_path, "w") as f:
        json.dump(explanations, f, indent=2)

    print(f"\n  Cluster explanations saved: {output_path}")


def main() -> int:
    """Main entry point for V2 clustering."""

    print("=" * 70)
    print("Cricket Playbook - Player Clustering Model V2")
    print("Author: Stephen Curry | Sprint 2.5")
    print("=" * 70)
    print("\nV2 Improvements:")
    print("  - Batting position / entry point feature")
    print("  - Wickets per phase for bowlers")
    print("  - Recency weighting (2021-2025)")
    print("  - PCA variance analysis")
    print("  - Correlation cleanup")
    print("  - Cluster explainability (TKT-142)")

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH))

    # Extract features
    print("\n" + "=" * 70)
    print("1. EXTRACTING PLAYER FEATURES (V2)")
    print("=" * 70)

    batter_df = get_batter_features_v2(conn)
    bowler_df = get_bowler_features_v2(conn)

    print(f"\n  Batters with data: {len(batter_df)}")
    print(f"  Bowlers with data: {len(bowler_df)}")

    # Cluster batters
    print("\n" + "=" * 70)
    print("2. CLUSTERING BATTERS (V2)")
    print("=" * 70)
    batter_clusters, batter_centers, batter_pca = cluster_batters_v2(batter_df, n_clusters=5)

    # Cluster bowlers
    print("\n" + "=" * 70)
    print("3. CLUSTERING BOWLERS (V2)")
    print("=" * 70)
    bowler_clusters, bowler_centers, bowler_pca = cluster_bowlers_v2(bowler_df, n_clusters=5)

    # Analyze clusters
    analyze_clusters_v2(batter_clusters, batter_centers, "batter")
    analyze_clusters_v2(bowler_clusters, bowler_centers, "bowler")

    # Validate specific players
    validate_specific_players(batter_clusters, bowler_clusters)

    # Generate cluster explanations (TKT-142)
    print("\n" + "=" * 70)
    print("4. GENERATING CLUSTER EXPLANATIONS (TKT-142)")
    print("=" * 70)
    batter_feature_cols = [c for c in batter_centers.columns if c != "cluster"]
    bowler_feature_cols = [c for c in bowler_centers.columns if c != "cluster"]
    save_cluster_explanations(
        batter_clusters,
        bowler_clusters,
        batter_centers,
        bowler_centers,
        batter_feature_cols,
        bowler_feature_cols,
    )

    # Summary
    print("\n" + "=" * 70)
    print("V2 CLUSTERING SUMMARY")
    print("=" * 70)
    print(f"\n  Batters clustered: {len(batter_clusters)}")
    print(f"  Bowlers clustered: {len(bowler_clusters)}")
    print("\n  PCA Variance (Batters):")
    print(
        f"    Components for 50%: {batter_pca['n_components_for_target']}/{batter_pca['total_components']}"
    )
    print(f"    First 3 PCs explain: {batter_pca['cumulative_variance'][2] * 100:.1f}%")
    print("\n  PCA Variance (Bowlers):")
    print(
        f"    Components for 50%: {bowler_pca['n_components_for_target']}/{bowler_pca['total_components']}"
    )
    print(f"    First 3 PCs explain: {bowler_pca['cumulative_variance'][2] * 100:.1f}%")

    conn.close()

    print("\n" + "=" * 70)
    print("NEXT: Andy Flower to review V2 clusters and validate labels")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
