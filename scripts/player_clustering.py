#!/usr/bin/env python3
"""
Cricket Playbook - Player Clustering Model
Author: Stephen Curry (Analytics Lead)

Creates data-driven player clusters based on performance metrics.
Clusters are created first, then reviewed by Andy Flower for labeling.

Approach:
1. Extract normalized feature vectors for batters and bowlers
2. Apply K-means clustering to find natural groupings
3. Output cluster assignments for review
"""

import duckdb
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"


def get_batter_features(conn) -> pd.DataFrame:
    """Extract batter feature vectors for clustering."""

    # Get batters with sufficient sample size (500+ balls in IPL)
    df = conn.execute("""
        WITH career AS (
            SELECT player_id, player_name, balls_faced, runs, strike_rate,
                   batting_average, boundary_pct, dot_ball_pct
            FROM analytics_ipl_batting_career
            WHERE balls_faced >= 500
        ),
        powerplay AS (
            SELECT player_id,
                   strike_rate as pp_sr,
                   boundary_pct as pp_boundary,
                   dot_ball_pct as pp_dot
            FROM analytics_ipl_batter_phase
            WHERE match_phase = 'powerplay' AND balls_faced >= 100
        ),
        middle AS (
            SELECT player_id,
                   strike_rate as mid_sr,
                   boundary_pct as mid_boundary,
                   dot_ball_pct as mid_dot
            FROM analytics_ipl_batter_phase
            WHERE match_phase = 'middle' AND balls_faced >= 100
        ),
        death AS (
            SELECT player_id,
                   strike_rate as death_sr,
                   boundary_pct as death_boundary,
                   dot_ball_pct as death_dot
            FROM analytics_ipl_batter_phase
            WHERE match_phase = 'death' AND balls_faced >= 50
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
        WHERE pp.pp_sr IS NOT NULL
          AND m.mid_sr IS NOT NULL
    """).df()

    return df


def get_bowler_features(conn) -> pd.DataFrame:
    """Extract bowler feature vectors for clustering."""

    # Get bowlers with sufficient sample size (300+ balls in IPL)
    df = conn.execute("""
        WITH career AS (
            SELECT player_id, player_name, balls_bowled, wickets,
                   economy_rate, bowling_average, bowling_strike_rate,
                   dot_ball_pct, boundary_conceded_pct
            FROM analytics_ipl_bowling_career
            WHERE balls_bowled >= 300
        ),
        powerplay AS (
            SELECT player_id,
                   economy_rate as pp_economy,
                   dot_ball_pct as pp_dot,
                   boundary_conceded_pct as pp_boundary,
                   COALESCE(balls_bowled * 1.0 / NULLIF((SELECT SUM(balls_bowled) FROM analytics_ipl_bowler_phase bp2 WHERE bp2.player_id = bp.player_id), 0), 0) as pp_workload_pct
            FROM analytics_ipl_bowler_phase bp
            WHERE match_phase = 'powerplay' AND balls_bowled >= 60
        ),
        middle AS (
            SELECT player_id,
                   economy_rate as mid_economy,
                   dot_ball_pct as mid_dot,
                   boundary_conceded_pct as mid_boundary
            FROM analytics_ipl_bowler_phase
            WHERE match_phase = 'middle' AND balls_bowled >= 60
        ),
        death AS (
            SELECT player_id,
                   economy_rate as death_economy,
                   dot_ball_pct as death_dot,
                   boundary_conceded_pct as death_boundary
            FROM analytics_ipl_bowler_phase
            WHERE match_phase = 'death' AND balls_bowled >= 60
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
        WHERE pp.pp_economy IS NOT NULL
          AND m.mid_economy IS NOT NULL
          AND d.death_economy IS NOT NULL
    """).df()

    return df


def cluster_batters(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """Cluster batters based on their features."""

    # Features for clustering
    feature_cols = [
        "overall_sr",
        "overall_avg",
        "overall_boundary",
        "overall_dot",
        "pp_sr",
        "pp_boundary",
        "pp_dot",
        "mid_sr",
        "mid_boundary",
        "mid_dot",
        "death_sr",
        "death_boundary",
        "death_dot",
    ]

    # Filter to rows with all features
    df_clean = df.dropna(subset=feature_cols).copy()

    if len(df_clean) < n_clusters:
        print(f"  Warning: Only {len(df_clean)} batters with complete data")
        n_clusters = min(n_clusters, len(df_clean))

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[feature_cols])

    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean["cluster"] = kmeans.fit_predict(X)

    # Add cluster centers info
    centers = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_), columns=feature_cols
    )
    centers["cluster"] = range(n_clusters)

    return df_clean, centers


def cluster_bowlers(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """Cluster bowlers based on their features."""

    # Features for clustering
    feature_cols = [
        "overall_economy",
        "overall_avg",
        "overall_sr",
        "overall_dot",
        "overall_boundary",
        "pp_economy",
        "pp_dot",
        "pp_boundary",
        "mid_economy",
        "mid_dot",
        "mid_boundary",
        "death_economy",
        "death_dot",
        "death_boundary",
        "pp_pct",
        "mid_pct",
        "death_pct",
    ]

    # Filter to rows with all features
    df_clean = df.dropna(subset=feature_cols).copy()

    if len(df_clean) < n_clusters:
        print(f"  Warning: Only {len(df_clean)} bowlers with complete data")
        n_clusters = min(n_clusters, len(df_clean))

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(df_clean[feature_cols])

    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_clean["cluster"] = kmeans.fit_predict(X)

    # Add cluster centers info
    centers = pd.DataFrame(
        scaler.inverse_transform(kmeans.cluster_centers_), columns=feature_cols
    )
    centers["cluster"] = range(n_clusters)

    return df_clean, centers


def analyze_clusters(df: pd.DataFrame, centers: pd.DataFrame, player_type: str):
    """Print cluster analysis for review."""

    print(f"\n{'='*70}")
    print(f"{player_type.upper()} CLUSTER ANALYSIS")
    print(f"{'='*70}")

    for cluster_id in sorted(df["cluster"].unique()):
        cluster_players = df[df["cluster"] == cluster_id]
        center = centers[centers["cluster"] == cluster_id].iloc[0]

        print(f"\n--- CLUSTER {cluster_id} ({len(cluster_players)} players) ---")

        # Show key characteristics
        if player_type == "batter":
            print(f"  Overall SR: {center['overall_sr']:.1f}")
            print(f"  Overall Avg: {center['overall_avg']:.1f}")
            print(f"  Boundary%: {center['overall_boundary']:.1f}%")
            print(
                f"  PP SR: {center['pp_sr']:.1f} | Mid SR: {center['mid_sr']:.1f} | Death SR: {center['death_sr']:.1f}"
            )
            print(f"  Death Boundary%: {center['death_boundary']:.1f}%")
        else:
            print(f"  Overall Economy: {center['overall_economy']:.2f}")
            print(f"  Overall Avg: {center['overall_avg']:.1f}")
            print(f"  Dot Ball%: {center['overall_dot']:.1f}%")
            print(
                f"  PP Econ: {center['pp_economy']:.2f} | Mid Econ: {center['mid_economy']:.2f} | Death Econ: {center['death_economy']:.2f}"
            )
            print(
                f"  Phase Split: PP {center['pp_pct']:.1f}% | Mid {center['mid_pct']:.1f}% | Death {center['death_pct']:.1f}%"
            )

        # Show players in cluster
        print("\n  Players:")
        for _, player in cluster_players.head(10).iterrows():
            if player_type == "batter":
                print(
                    f"    - {player['player_name']} (SR: {player['overall_sr']:.1f}, Avg: {player['overall_avg']:.1f})"
                )
            else:
                print(
                    f"    - {player['player_name']} (Econ: {player['overall_economy']:.2f}, Wkts: {player['wickets']})"
                )

        if len(cluster_players) > 10:
            print(f"    ... and {len(cluster_players) - 10} more")


def save_clusters_to_db(conn, batter_df: pd.DataFrame, bowler_df: pd.DataFrame):
    """Save cluster assignments to database."""

    # Create batter clusters table
    conn.execute("DROP TABLE IF EXISTS player_clusters_batters")
    conn.execute("""
        CREATE TABLE player_clusters_batters (
            player_id VARCHAR,
            player_name VARCHAR,
            cluster_id INTEGER,
            overall_sr DOUBLE,
            overall_avg DOUBLE,
            overall_boundary DOUBLE,
            pp_sr DOUBLE,
            mid_sr DOUBLE,
            death_sr DOUBLE,
            death_boundary DOUBLE
        )
    """)

    for _, row in batter_df.iterrows():
        conn.execute(
            """
            INSERT INTO player_clusters_batters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                row["player_id"],
                row["player_name"],
                int(row["cluster"]),
                row["overall_sr"],
                row["overall_avg"],
                row["overall_boundary"],
                row.get("pp_sr"),
                row.get("mid_sr"),
                row.get("death_sr"),
                row.get("death_boundary"),
            ],
        )

    # Create bowler clusters table
    conn.execute("DROP TABLE IF EXISTS player_clusters_bowlers")
    conn.execute("""
        CREATE TABLE player_clusters_bowlers (
            player_id VARCHAR,
            player_name VARCHAR,
            cluster_id INTEGER,
            overall_economy DOUBLE,
            overall_avg DOUBLE,
            overall_dot DOUBLE,
            pp_economy DOUBLE,
            mid_economy DOUBLE,
            death_economy DOUBLE,
            pp_pct DOUBLE,
            mid_pct DOUBLE,
            death_pct DOUBLE
        )
    """)

    for _, row in bowler_df.iterrows():
        conn.execute(
            """
            INSERT INTO player_clusters_bowlers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                row["player_id"],
                row["player_name"],
                int(row["cluster"]),
                row["overall_economy"],
                row["overall_avg"],
                row["overall_dot"],
                row.get("pp_economy"),
                row.get("mid_economy"),
                row.get("death_economy"),
                row.get("pp_pct"),
                row.get("mid_pct"),
                row.get("death_pct"),
            ],
        )

    print("\n  Cluster tables saved to database:")
    print("    - player_clusters_batters")
    print("    - player_clusters_bowlers")


def main():
    """Main entry point."""

    print("=" * 70)
    print("Cricket Playbook - Player Clustering Model")
    print("Author: Stephen Curry")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH))

    # Extract features
    print("\n1. Extracting player features...")
    batter_df = get_batter_features(conn)
    bowler_df = get_bowler_features(conn)
    print(f"   Batters with complete data: {len(batter_df)}")
    print(f"   Bowlers with complete data: {len(bowler_df)}")

    # Cluster batters
    print("\n2. Clustering batters (K=5)...")
    batter_clusters, batter_centers = cluster_batters(batter_df, n_clusters=5)

    # Cluster bowlers
    print("\n3. Clustering bowlers (K=5)...")
    bowler_clusters, bowler_centers = cluster_bowlers(bowler_df, n_clusters=5)

    # Analyze and print results
    analyze_clusters(batter_clusters, batter_centers, "batter")
    analyze_clusters(bowler_clusters, bowler_centers, "bowler")

    # Save to database
    print("\n4. Saving clusters to database...")
    save_clusters_to_db(conn, batter_clusters, bowler_clusters)

    conn.close()

    print("\n" + "=" * 70)
    print("NEXT STEP: Andy Flower to review clusters and assign labels")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(main())
