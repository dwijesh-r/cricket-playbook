#!/usr/bin/env python3
"""
Win Probability Model — Feature Engineering Pipeline
=====================================================
Extracts match-state features from fact_ball for training a ball-by-ball
win probability model. Outputs a parquet training dataset and metadata JSON.

Features:
    - Match state (score, wickets, balls remaining, run rates)
    - Phase context (powerplay/middle/death, phase progress)
    - Momentum (last-3-over rolling window)
    - Team strength indices (historical batting SR / bowling economy by phase)
    - Target label (batting_team_won)

Edge-case handling:
    - DLS/reduced-overs matches excluded (innings < 20 overs, < 10 wickets)
    - No-result / tie matches excluded
    - Super-over innings excluded (only innings 1 & 2)
    - First-ball momentum features default to 0

Owner: Ime Udoka (ML Ops Engineer)
Ticket: TKT-206  |  EPIC-018: Win Probability Model
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "data" / "ml"
PARQUET_PATH = OUTPUT_DIR / "win_prob_features.parquet"
METADATA_PATH = OUTPUT_DIR / "win_prob_metadata.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("feature_engineering")

# ---------------------------------------------------------------------------
# Phase boundaries (0-indexed overs)
# ---------------------------------------------------------------------------
PHASE_MAP = {
    "powerplay": (0, 5),  # overs 1-6
    "middle": (6, 14),  # overs 7-15
    "death": (15, 19),  # overs 16-20
}
MAX_LEGAL_BALLS = 120  # 20 overs * 6 balls


def connect_db() -> duckdb.DuckDBPyConnection:
    """Open DuckDB in read-only mode."""
    if not DB_PATH.exists():
        log.error("Database not found at %s", DB_PATH)
        sys.exit(1)
    return duckdb.connect(str(DB_PATH), read_only=True)


# ====================================================================
# Step 1 — Identify valid matches (exclude DLS, no-result, ties)
# ====================================================================
def get_valid_match_ids(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Return a DataFrame of valid match_ids with winner metadata.

    Exclusions:
    - outcome_type NOT IN ('runs', 'wickets') -> excludes ties, no-result, NULL
    - winner_id IS NULL
    - DLS/reduced-overs matches, detected as:
      - First innings: < 20 overs completed AND < 10 wickets (always abnormal)
      - Second innings: < 20 overs AND < 10 wickets AND match NOT won by wickets
        (because won-by-wickets normally ends before 20 overs when target is reached)
    """
    log.info("Identifying valid matches...")

    df = con.execute("""
        WITH innings_stats AS (
            SELECT
                fb.match_id,
                fb.innings,
                COUNT(CASE WHEN fb.is_legal_ball THEN 1 END) AS legal_balls,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets,
                MAX(fb.over) + 1 AS overs_completed
            FROM fact_ball fb
            WHERE fb.innings IN (1, 2)
            GROUP BY fb.match_id, fb.innings
        ),
        dls_inn1 AS (
            -- First innings cut short is always DLS/reduced
            SELECT DISTINCT match_id
            FROM innings_stats
            WHERE innings = 1
              AND overs_completed < 20
              AND wickets < 10
        ),
        dls_inn2 AS (
            -- Second innings cut short is DLS only if NOT won by wickets
            -- (won-by-wickets naturally ends early when target is reached)
            SELECT DISTINCT i.match_id
            FROM innings_stats i
            JOIN dim_match dm ON i.match_id = dm.match_id
            WHERE i.innings = 2
              AND i.overs_completed < 20
              AND i.wickets < 10
              AND dm.outcome_type != 'wickets'
        ),
        dls_matches AS (
            SELECT match_id FROM dls_inn1
            UNION
            SELECT match_id FROM dls_inn2
        ),
        valid AS (
            SELECT
                dm.match_id,
                dm.winner_id,
                dm.match_date,
                dm.team1_id,
                dm.team2_id,
                dm.outcome_type
            FROM dim_match dm
            WHERE dm.outcome_type IN ('runs', 'wickets')
              AND dm.winner_id IS NOT NULL
              AND dm.match_id NOT IN (SELECT match_id FROM dls_matches)
        )
        SELECT * FROM valid
        ORDER BY match_date
    """).fetchdf()

    log.info("Valid matches: %d (excluded DLS/reduced, ties, no-result)", len(df))
    return df


# ====================================================================
# Step 2 — Extract raw ball-by-ball data for valid matches
# ====================================================================
def get_ball_data(con: duckdb.DuckDBPyConnection, valid_match_ids: list[str]) -> pd.DataFrame:
    """Fetch all legal + extra balls for valid matches, innings 1 & 2."""
    log.info("Fetching ball-by-ball data for %d matches...", len(valid_match_ids))

    # Register the list as a temp table for the IN clause
    con.execute(
        "CREATE OR REPLACE TEMP TABLE valid_ids AS SELECT UNNEST(?::VARCHAR[]) AS match_id",
        [valid_match_ids],
    )

    df = con.execute("""
        SELECT
            fb.match_id,
            fb.innings,
            fb.over AS over_number,
            fb.ball AS ball_in_over,
            fb.ball_seq,
            fb.batting_team_id,
            fb.bowling_team_id,
            fb.total_runs,
            fb.batter_runs,
            fb.extra_runs,
            fb.is_wicket,
            fb.is_legal_ball,
            fb.match_phase
        FROM fact_ball fb
        INNER JOIN valid_ids v ON fb.match_id = v.match_id
        WHERE fb.innings IN (1, 2)
        ORDER BY fb.match_id, fb.innings, fb.ball_seq
    """).fetchdf()

    log.info("Fetched %d ball rows", len(df))
    return df


# ====================================================================
# Step 3 — Compute per-innings first-innings totals (for target)
# ====================================================================
def compute_innings_totals(ball_df: pd.DataFrame) -> pd.DataFrame:
    """Compute first-innings total for each match (used as target in inn 2)."""
    inn1 = ball_df[ball_df["innings"] == 1]
    totals = (
        inn1.groupby("match_id")
        .agg(
            first_innings_total=("total_runs", "sum"),
            first_innings_balls=("is_legal_ball", "sum"),
        )
        .reset_index()
    )
    totals["target"] = totals["first_innings_total"] + 1  # chase target
    return totals[["match_id", "first_innings_total", "target"]]


# ====================================================================
# Step 4 — Build cumulative match-state features (vectorized)
# ====================================================================
def build_match_state_features(
    ball_df: pd.DataFrame,
    innings_totals: pd.DataFrame,
    match_meta: pd.DataFrame,
) -> pd.DataFrame:
    """
    For every ball, compute cumulative match state features.

    This is the core feature engineering step. We use pandas groupby + cumsum
    for vectorized computation rather than row-by-row iteration.
    """
    log.info("Computing match-state features...")

    df = ball_df.copy()

    # --- Merge match metadata ---
    df = df.merge(match_meta[["match_id", "winner_id"]], on="match_id", how="left")
    df = df.merge(innings_totals, on="match_id", how="left")

    # --- Group key for cumulative aggregation ---
    grp = df.groupby(["match_id", "innings"])

    # Cumulative score (running total of runs up to and including this ball)
    df["current_score"] = grp["total_runs"].cumsum()

    # Cumulative wickets
    df["is_wicket_int"] = df["is_wicket"].astype(int)
    df["wickets_fallen"] = grp["is_wicket_int"].cumsum()

    # Cumulative legal balls bowled
    df["is_legal_int"] = df["is_legal_ball"].astype(int)
    df["legal_balls_bowled"] = grp["is_legal_int"].cumsum()

    # Balls remaining (for first innings: 120 - legal_balls_bowled)
    # For second innings: same calculation (balls left in innings)
    df["balls_remaining"] = MAX_LEGAL_BALLS - df["legal_balls_bowled"]
    df["balls_remaining"] = df["balls_remaining"].clip(lower=0)

    # Overs bowled (as float)
    df["overs_bowled"] = df["legal_balls_bowled"] / 6.0

    # Current run rate
    df["current_run_rate"] = np.where(
        df["overs_bowled"] > 0,
        df["current_score"] / df["overs_bowled"],
        0.0,
    )

    # Required run rate (2nd innings only)
    df["runs_remaining"] = np.where(
        df["innings"] == 2,
        df["target"] - df["current_score"],
        np.nan,
    )
    df["overs_remaining"] = df["balls_remaining"] / 6.0
    df["required_run_rate"] = np.where(
        (df["innings"] == 2) & (df["overs_remaining"] > 0),
        df["runs_remaining"] / df["overs_remaining"],
        np.nan,
    )

    # Target (only for innings 2)
    df["target_score"] = np.where(df["innings"] == 2, df["target"], np.nan)

    # --- Phase context ---
    df["phase"] = df["match_phase"]  # already in fact_ball
    df["phase_start"] = df["over_number"].map(
        lambda o: (
            PHASE_MAP["powerplay"][0]
            if o <= 5
            else (PHASE_MAP["middle"][0] if o <= 14 else PHASE_MAP["death"][0])
        )
    )
    df["phase_end"] = df["over_number"].map(
        lambda o: (
            PHASE_MAP["powerplay"][1]
            if o <= 5
            else (PHASE_MAP["middle"][1] if o <= 14 else PHASE_MAP["death"][1])
        )
    )
    df["phase_length"] = df["phase_end"] - df["phase_start"] + 1
    df["overs_into_phase"] = df["over_number"] - df["phase_start"]
    df["phase_progress"] = np.where(
        df["phase_length"] > 0,
        (df["overs_into_phase"] + (df["ball_in_over"] / 6.0)) / df["phase_length"],
        0.0,
    )
    df["phase_progress"] = df["phase_progress"].clip(0.0, 1.0)

    # --- Label: batting_team_won ---
    df["batting_team_won"] = (df["batting_team_id"] == df["winner_id"]).astype(int)

    log.info("Match-state features computed.")
    return df


# ====================================================================
# Step 5 — Momentum features (last 3 overs rolling window)
# ====================================================================
def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute rolling 3-over momentum features per innings.

    For each ball, we look back at legal deliveries in the previous 3 completed
    overs (not including the current over) plus the current over's balls so far.
    To keep it tractable and accurate, we define "last 18 legal balls" as the
    window (3 overs = 18 balls).
    """
    log.info("Computing momentum features (last 3 overs)...")

    WINDOW = 18  # 3 overs * 6 balls

    # We only consider legal balls for momentum calculations
    # but we need to track runs from extras too
    # Approach: for each ball, compute rolling stats over the last 18 legal balls

    # Sort properly
    df = df.sort_values(["match_id", "innings", "ball_seq"]).reset_index(drop=True)

    # Pre-compute per-ball metrics we need for rolling
    df["is_dot"] = ((df["total_runs"] == 0) & df["is_legal_ball"]).astype(int)
    df["is_boundary"] = ((df["batter_runs"].isin([4, 6])) & df["is_legal_ball"]).astype(int)

    # For rolling we need legal-ball indexed data
    # Strategy: use expanding window on legal balls only, then map back

    results = []
    for (mid, inn), group in df.groupby(["match_id", "innings"]):
        legal_mask = group["is_legal_ball"]
        legal_idx = group.index[legal_mask]

        # Build legal-ball-only series
        legal_runs = group.loc[legal_idx, "total_runs"]
        legal_wickets = group.loc[legal_idx, "is_wicket_int"]
        legal_dots = group.loc[legal_idx, "is_dot"]
        legal_boundaries = group.loc[legal_idx, "is_boundary"]

        # Rolling sums over last WINDOW legal balls
        roll_runs = legal_runs.rolling(window=WINDOW, min_periods=1).sum()
        roll_wickets = legal_wickets.rolling(window=WINDOW, min_periods=1).sum()
        roll_dots = legal_dots.rolling(window=WINDOW, min_periods=1).sum()
        roll_boundaries = legal_boundaries.rolling(window=WINDOW, min_periods=1).sum()
        roll_count = legal_runs.rolling(window=WINDOW, min_periods=1).count()

        # Run rate over the window (per 6 balls = per over)
        roll_rr = np.where(roll_count > 0, roll_runs * 6.0 / roll_count, 0.0)
        roll_dot_pct = np.where(roll_count > 0, roll_dots / roll_count, 0.0)
        roll_boundary_pct = np.where(roll_count > 0, roll_boundaries / roll_count, 0.0)

        # Create a mapping from legal ball index to momentum values
        momentum_df = pd.DataFrame(
            {
                "last_3ov_run_rate": roll_rr,
                "last_3ov_wickets": roll_wickets.values,
                "last_3ov_dot_pct": roll_dot_pct,
                "last_3ov_boundary_pct": roll_boundary_pct,
            },
            index=legal_idx,
        )

        # Forward-fill to non-legal balls (extras get same momentum as preceding legal ball)
        full_momentum = momentum_df.reindex(group.index).ffill().fillna(0.0)
        results.append(full_momentum)

    momentum_all = pd.concat(results)
    for col in [
        "last_3ov_run_rate",
        "last_3ov_wickets",
        "last_3ov_dot_pct",
        "last_3ov_boundary_pct",
    ]:
        df[col] = momentum_all[col].values

    log.info("Momentum features computed.")
    return df


# ====================================================================
# Step 6 — Team strength indices (historical phase-level performance)
# ====================================================================
def add_team_strength_indices(df: pd.DataFrame, con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Compute batting_team_strength and bowling_team_strength.

    batting_team_strength = team's historical SR in this phase (min-max normalized 0-1)
    bowling_team_strength = team's historical economy in this phase (inverted, normalized 0-1)

    We compute these from the full fact_ball table (all T20 data) as aggregate
    team-level stats per phase. Then normalize across all teams.
    """
    log.info("Computing team strength indices...")

    # Historical batting SR per team per phase
    team_bat = con.execute("""
        SELECT
            batting_team_id AS team_id,
            match_phase AS phase,
            SUM(batter_runs) * 100.0
                / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0) AS strike_rate
        FROM fact_ball
        WHERE innings IN (1, 2) AND match_phase IS NOT NULL
        GROUP BY batting_team_id, match_phase
        HAVING SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) >= 120
    """).fetchdf()

    # Historical bowling economy per team per phase
    team_bowl = con.execute("""
        SELECT
            bowling_team_id AS team_id,
            match_phase AS phase,
            SUM(total_runs) * 6.0
                / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0) AS economy
        FROM fact_ball
        WHERE innings IN (1, 2) AND match_phase IS NOT NULL
        GROUP BY bowling_team_id, match_phase
        HAVING SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) >= 120
    """).fetchdf()

    # Min-max normalize batting SR per phase (higher SR = stronger = closer to 1)
    for phase in team_bat["phase"].unique():
        mask = team_bat["phase"] == phase
        sr_vals = team_bat.loc[mask, "strike_rate"]
        sr_min, sr_max = sr_vals.min(), sr_vals.max()
        if sr_max > sr_min:
            team_bat.loc[mask, "bat_strength"] = (sr_vals - sr_min) / (sr_max - sr_min)
        else:
            team_bat.loc[mask, "bat_strength"] = 0.5

    # Min-max normalize bowling economy per phase (LOWER economy = stronger = closer to 1)
    for phase in team_bowl["phase"].unique():
        mask = team_bowl["phase"] == phase
        eco_vals = team_bowl.loc[mask, "economy"]
        eco_min, eco_max = eco_vals.min(), eco_vals.max()
        if eco_max > eco_min:
            team_bowl.loc[mask, "bowl_strength"] = 1.0 - (
                (eco_vals - eco_min) / (eco_max - eco_min)
            )
        else:
            team_bowl.loc[mask, "bowl_strength"] = 0.5

    # Create lookup dicts: (team_id, phase) -> strength
    bat_lookup = dict(
        zip(
            zip(team_bat["team_id"], team_bat["phase"]),
            team_bat["bat_strength"],
        )
    )
    bowl_lookup = dict(
        zip(
            zip(team_bowl["team_id"], team_bowl["phase"]),
            team_bowl["bowl_strength"],
        )
    )

    # Map to main DataFrame
    df["batting_team_strength"] = [
        bat_lookup.get((bt, ph), 0.5) for bt, ph in zip(df["batting_team_id"], df["phase"])
    ]
    df["bowling_team_strength"] = [
        bowl_lookup.get((bw, ph), 0.5) for bw, ph in zip(df["bowling_team_id"], df["phase"])
    ]

    log.info(
        "Team strength indices computed. Batting lookup: %d entries, Bowling: %d",
        len(bat_lookup),
        len(bowl_lookup),
    )
    return df


# ====================================================================
# Step 7 — Select final columns and write output
# ====================================================================
FEATURE_COLUMNS = [
    # Identifiers (not model features, but needed for traceability)
    "match_id",
    "innings",
    "ball_seq",
    # Match state
    "over_number",
    "ball_in_over",
    "current_score",
    "wickets_fallen",
    "balls_remaining",
    "current_run_rate",
    "required_run_rate",
    # Phase context
    "phase",
    "phase_progress",
    # Momentum (last 3 overs)
    "last_3ov_run_rate",
    "last_3ov_wickets",
    "last_3ov_dot_pct",
    "last_3ov_boundary_pct",
    # Team strength indices
    "batting_team_strength",
    "bowling_team_strength",
    # Target info
    "target_score",
    # Label
    "batting_team_won",
]

FEATURE_DTYPES = {
    "match_id": "string",
    "innings": "int8",
    "ball_seq": "int16",
    "over_number": "int8",
    "ball_in_over": "int8",
    "current_score": "int16",
    "wickets_fallen": "int8",
    "balls_remaining": "int16",
    "current_run_rate": "float32",
    "required_run_rate": "float32",
    "phase": "string",
    "phase_progress": "float32",
    "last_3ov_run_rate": "float32",
    "last_3ov_wickets": "int8",
    "last_3ov_dot_pct": "float32",
    "last_3ov_boundary_pct": "float32",
    "batting_team_strength": "float32",
    "bowling_team_strength": "float32",
    "target_score": "float32",
    "batting_team_won": "int8",
}


def write_outputs(df: pd.DataFrame, match_meta: pd.DataFrame) -> dict:
    """Write parquet and metadata JSON. Return metadata dict."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Select and cast columns
    out = df[FEATURE_COLUMNS].copy()
    for col, dtype in FEATURE_DTYPES.items():
        if col in out.columns:
            if dtype == "string":
                out[col] = out[col].astype(str)
            else:
                out[col] = pd.to_numeric(out[col], errors="coerce").astype(dtype)

    # Write parquet
    out.to_parquet(PARQUET_PATH, index=False, engine="pyarrow")
    log.info("Parquet written: %s (%d rows, %d cols)", PARQUET_PATH, len(out), len(out.columns))

    # Class balance
    won_counts = out["batting_team_won"].value_counts().to_dict()
    total = len(out)
    class_balance = {
        "batting_team_won_1": int(won_counts.get(1, 0)),
        "batting_team_won_0": int(won_counts.get(0, 0)),
        "ratio_won": round(won_counts.get(1, 0) / total, 4) if total > 0 else 0,
    }

    # Date range
    dates = match_meta["match_date"].dropna()
    date_min = str(dates.min()) if len(dates) > 0 else "unknown"
    date_max = str(dates.max()) if len(dates) > 0 else "unknown"

    # Feature names (exclude identifiers)
    model_features = [c for c in FEATURE_COLUMNS if c not in ("match_id", "innings", "ball_seq")]

    metadata = {
        "ticket": "TKT-206",
        "description": "Win probability training features from fact_ball",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_matches": int(match_meta["match_id"].nunique()),
        "total_balls": int(len(out)),
        "total_columns": int(len(out.columns)),
        "feature_count": len(model_features),
        "feature_names": model_features,
        "feature_types": {c: FEATURE_DTYPES.get(c, "unknown") for c in model_features},
        "date_range": {"min": date_min, "max": date_max},
        "class_balance": class_balance,
        "exclusions": [
            "DLS/reduced 1st innings (< 20 overs, < 10 wickets)",
            "DLS/reduced 2nd innings (< 20 overs, < 10 wickets, not won by wickets)",
            "No-result matches",
            "Ties (no clear winner)",
            "Super-over innings (only regulation innings 1 & 2)",
        ],
        "parquet_path": str(PARQUET_PATH),
        "parquet_size_mb": round(PARQUET_PATH.stat().st_size / (1024 * 1024), 2),
    }

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    log.info("Metadata written: %s", METADATA_PATH)

    return metadata


# ====================================================================
# Main pipeline
# ====================================================================
def main() -> dict:
    """Run the full feature engineering pipeline."""
    t0 = time.time()
    log.info("=" * 60)
    log.info("TKT-206: Feature Engineering Pipeline — START")
    log.info("=" * 60)

    con = connect_db()

    # Step 1: Valid matches
    match_meta = get_valid_match_ids(con)

    # Step 2: Ball data
    valid_ids = match_meta["match_id"].tolist()
    ball_df = get_ball_data(con, valid_ids)

    # Step 3: Innings totals (for 2nd innings target)
    innings_totals = compute_innings_totals(ball_df)

    # Step 4: Match-state features
    df = build_match_state_features(ball_df, innings_totals, match_meta)

    # Step 5: Momentum features
    df = add_momentum_features(df)

    # Step 6: Team strength indices
    df = add_team_strength_indices(df, con)

    # Step 7: Write outputs
    metadata = write_outputs(df, match_meta)

    con.close()

    elapsed = time.time() - t0
    log.info("-" * 60)
    log.info("Pipeline complete in %.1f seconds", elapsed)
    log.info(
        "Matches: %d | Balls: %d | Features: %d",
        metadata["total_matches"],
        metadata["total_balls"],
        metadata["feature_count"],
    )
    log.info(
        "Class balance: won=%.1f%% | lost=%.1f%%",
        metadata["class_balance"]["ratio_won"] * 100,
        (1 - metadata["class_balance"]["ratio_won"]) * 100,
    )
    log.info("Output: %s (%.1f MB)", PARQUET_PATH, metadata["parquet_size_mb"])
    log.info("=" * 60)

    return metadata


if __name__ == "__main__":
    main()
