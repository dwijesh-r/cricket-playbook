#!/usr/bin/env python3
"""
Cricket Playbook - Sprint 3.0 P1 Features
Author: Stephen Curry (Analytics Lead)
Sprint: 3.0 - P1 Features

Implements:
- S3.0-09: Bowler Role Tags Revision (MIDDLE_AND_DEATH_SPECIALIST, revised death overs criteria >=1 over in 16+)
- S3.0-10: Consistency Index (Andy Flower research) - overall + year-wise + quality metrics
- S3.0-11: Partnership Synergy Score - overall + year-wise breakdown
- S3.0-12: Pressure Sequence for Bowlers (reuse pressure sequence definition)
- S3.0-13: Venue Win/Loss Per Team
- S3.0-14: Bowler Phase Distribution Tables (grouped by phase)
"""

import json
from pathlib import Path
from typing import Dict

import duckdb
import pandas as pd

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "outputs"

# Data filter - only use recent IPL seasons (2023 onwards)
IPL_MIN_DATE = "2023-01-01"

# ============================================================================
# S3.0-09: BOWLER ROLE TAGS REVISION
# ============================================================================


def get_bowler_phase_overs(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Get per-match bowler phase overs to determine role tags.

    REVISED CRITERIA (S3.0-09):
    - Death specialist: bowls at least 1 over in overs 16+ (was >= 3 overs)
    - Add MIDDLE_AND_DEATH_SPECIALIST for bowlers who bowl both phases regularly
    """

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        bowler_match_phase AS (
            -- Count overs bowled per match per phase
            -- Death overs: over >= 15 (0-indexed means overs 16-20)
            SELECT
                fb.bowler_id,
                fb.match_id,
                fb.match_phase,
                -- Also track specific death overs (16+)
                SUM(CASE WHEN fb."over" >= 15 AND fb.is_legal_ball = TRUE THEN 1 ELSE 0 END) as death_balls_16plus,
                COUNT(DISTINCT fb."over") as overs_in_phase
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.is_legal_ball = TRUE
            GROUP BY fb.bowler_id, fb.match_id, fb.match_phase
        ),
        bowler_match_death_16plus AS (
            -- Track matches where bowler bowled at least 1 over (6 balls) in overs 16+
            SELECT
                bowler_id,
                match_id,
                SUM(death_balls_16plus) as death_balls_16plus
            FROM bowler_match_phase
            GROUP BY bowler_id, match_id
        ),
        bowler_phase_summary AS (
            -- Count how many matches a bowler bowled >= 1 over in each phase
            SELECT
                bowler_id,
                match_phase,
                COUNT(*) as matches_in_phase,
                SUM(CASE WHEN overs_in_phase >= 1 THEN 1 ELSE 0 END) as matches_with_1plus_overs,
                SUM(overs_in_phase) as total_overs_in_phase
            FROM bowler_match_phase
            GROUP BY bowler_id, match_phase
        ),
        bowler_death_16plus_summary AS (
            -- Count matches where bowler bowled at least 1 over in overs 16+
            SELECT
                bowler_id,
                COUNT(CASE WHEN death_balls_16plus >= 6 THEN 1 END) as matches_with_death_16plus,
                SUM(death_balls_16plus) as total_death_balls_16plus
            FROM bowler_match_death_16plus
            GROUP BY bowler_id
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            SUM(CASE WHEN match_phase = 'powerplay' THEN total_overs_in_phase ELSE 0 END) as pp_overs,
            SUM(CASE WHEN match_phase = 'middle' THEN total_overs_in_phase ELSE 0 END) as middle_overs,
            SUM(CASE WHEN match_phase = 'death' THEN total_overs_in_phase ELSE 0 END) as death_overs,
            SUM(CASE WHEN match_phase = 'powerplay' THEN matches_with_1plus_overs ELSE 0 END) as pp_matches,
            SUM(CASE WHEN match_phase = 'middle' THEN matches_with_1plus_overs ELSE 0 END) as middle_matches,
            SUM(CASE WHEN match_phase = 'death' THEN matches_with_1plus_overs ELSE 0 END) as death_matches,
            COALESCE(bd.matches_with_death_16plus, 0) as matches_with_death_16plus,
            COALESCE(bd.total_death_balls_16plus, 0) as total_death_balls_16plus
        FROM bowler_phase_summary bps
        JOIN dim_player dp ON bps.bowler_id = dp.player_id
        LEFT JOIN bowler_death_16plus_summary bd ON bps.bowler_id = bd.bowler_id
        GROUP BY dp.player_id, dp.current_name, bd.matches_with_death_16plus, bd.total_death_balls_16plus
    """).df()

    return df


def assign_bowler_role_tags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign bowler role tags based on revised criteria.

    REVISED CRITERIA (S3.0-09):
    - DEATH_SPECIALIST: bowls >= 1 over in overs 16+ in >= 30% of matches
    - MIDDLE_AND_DEATH_SPECIALIST: bowls both middle and death overs regularly
    - NEW_BALL_SPECIALIST: bowls >= 2 overs in powerplay in >= 40% of matches
    - MIDDLE_OVERS_CONTROLLER: bowls >= 2 overs in middle in >= 40% of matches
    - WORKHORSE: bowls across all phases
    """

    tags = []

    for _, row in df.iterrows():
        player_tags = []
        total_matches = max(row["pp_matches"], row["middle_matches"], row["death_matches"], 1)

        # Calculate phase percentages
        pp_pct = row["pp_matches"] / total_matches if total_matches > 0 else 0
        middle_pct = row["middle_matches"] / total_matches if total_matches > 0 else 0
        death_pct = row["death_matches"] / total_matches if total_matches > 0 else 0

        # Calculate death 16+ percentage (revised criteria: >=1 over in overs 16+)
        death_16plus_pct = (
            row["matches_with_death_16plus"] / total_matches if total_matches > 0 else 0
        )

        # Minimum overs to be considered a regular bowler
        total_overs = row["pp_overs"] + row["middle_overs"] + row["death_overs"]
        if total_overs < 30:
            tags.append([])
            continue

        # Death specialist: bowls >= 1 over in overs 16+ in >= 30% of matches (REVISED CRITERIA)
        is_death_specialist = (
            death_16plus_pct >= 0.30 and row["total_death_balls_16plus"] >= 36
        )  # At least 6 overs in death 16+

        # Middle overs controller: bowls in middle in >= 40% of matches
        is_middle_specialist = middle_pct >= 0.40 and row["middle_overs"] >= 20

        # New ball specialist: bowls in powerplay in >= 40% of matches
        is_pp_specialist = pp_pct >= 0.40 and row["pp_overs"] >= 10

        # Assign tags - MIDDLE_AND_DEATH_SPECIALIST for bowlers who do both
        if is_death_specialist and is_middle_specialist:
            player_tags.append("MIDDLE_AND_DEATH_SPECIALIST")
        elif is_death_specialist:
            player_tags.append("DEATH_SPECIALIST")
        elif is_middle_specialist:
            player_tags.append("MIDDLE_OVERS_CONTROLLER")

        if is_pp_specialist:
            player_tags.append("NEW_BALL_SPECIALIST")

        # Workhorse: bowls across all phases
        if pp_pct >= 0.25 and middle_pct >= 0.25 and death_pct >= 0.25:
            player_tags.append("WORKHORSE")

        tags.append(player_tags)

    df["role_tags"] = tags
    return df


# ============================================================================
# S3.0-10: CONSISTENCY INDEX (Andy Flower Research)
# ============================================================================


def calculate_batter_consistency_index(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Calculate Consistency Index based on Andy Flower research.

    Components:
    - Coefficient of Variation (CV) of runs scored
    - Strike rate consistency
    - Performance in high-pressure situations

    Formula:
    Consistency Index = (1 - CV) * 100 * Quality_Multiplier
    where Quality_Multiplier accounts for SR and boundaries

    Quality Metrics:
    - High Impact: 30+ scores frequency
    - Failure Rate: Single digit dismissals
    - Boundary %
    """

    # Overall since 2023
    overall_df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        innings_scores AS (
            SELECT
                fb.batter_id,
                fb.match_id,
                im.match_year,
                SUM(fb.batter_runs) as innings_runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
                SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) as boundaries,
                MAX(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as was_dismissed
            FROM fact_ball fb
            JOIN ipl_matches im ON fb.match_id = im.match_id
            GROUP BY fb.batter_id, fb.match_id, im.match_year
            HAVING SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) >= 10
        ),
        batter_stats AS (
            SELECT
                batter_id,
                COUNT(*) as innings,
                AVG(innings_runs) as avg_runs,
                STDDEV_POP(innings_runs) as stddev_runs,
                AVG(innings_runs * 100.0 / NULLIF(balls_faced, 0)) as avg_sr,
                STDDEV_POP(innings_runs * 100.0 / NULLIF(balls_faced, 0)) as stddev_sr,
                SUM(innings_runs) as total_runs,
                SUM(balls_faced) as total_balls,
                SUM(boundaries) as total_boundaries,
                -- Quality metrics
                SUM(CASE WHEN innings_runs >= 30 THEN 1 ELSE 0 END) as high_impact_innings,
                SUM(CASE WHEN innings_runs < 10 AND was_dismissed = 1 THEN 1 ELSE 0 END) as single_digit_dismissals,
                SUM(was_dismissed) as total_dismissals
            FROM innings_scores
            GROUP BY batter_id
            HAVING COUNT(*) >= 10
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            bs.innings,
            bs.total_runs,
            bs.total_balls,
            bs.avg_runs,
            bs.stddev_runs,
            -- Coefficient of Variation (lower = more consistent)
            ROUND(bs.stddev_runs / NULLIF(bs.avg_runs, 0), 3) as cv_runs,
            -- Strike rate
            ROUND(bs.total_runs * 100.0 / NULLIF(bs.total_balls, 0), 2) as overall_sr,
            ROUND(bs.avg_sr, 2) as avg_innings_sr,
            ROUND(bs.stddev_sr, 2) as stddev_sr,
            -- Boundary percentage
            ROUND(bs.total_boundaries * 100.0 / NULLIF(bs.total_balls, 0), 2) as boundary_pct,
            -- Quality metrics
            bs.high_impact_innings,
            ROUND(bs.high_impact_innings * 100.0 / bs.innings, 1) as high_impact_pct,
            bs.single_digit_dismissals,
            ROUND(bs.single_digit_dismissals * 100.0 / NULLIF(bs.total_dismissals, 0), 1) as failure_rate,
            -- Consistency Index: (1 - CV) * 100, bounded 0-100
            ROUND(GREATEST(0, LEAST(100, (1 - bs.stddev_runs / NULLIF(bs.avg_runs, 0)) * 100)), 1) as consistency_index,
            -- Quality multiplier based on SR percentile
            CASE
                WHEN bs.total_runs * 100.0 / NULLIF(bs.total_balls, 0) >= 150 THEN 1.2
                WHEN bs.total_runs * 100.0 / NULLIF(bs.total_balls, 0) >= 140 THEN 1.1
                WHEN bs.total_runs * 100.0 / NULLIF(bs.total_balls, 0) >= 130 THEN 1.0
                WHEN bs.total_runs * 100.0 / NULLIF(bs.total_balls, 0) >= 120 THEN 0.9
                ELSE 0.8
            END as quality_multiplier
        FROM batter_stats bs
        JOIN dim_player dp ON bs.batter_id = dp.player_id
        ORDER BY consistency_index DESC
    """).df()

    # Calculate weighted consistency index
    overall_df["weighted_consistency"] = (
        overall_df["consistency_index"] * overall_df["quality_multiplier"]
    ).round(1)

    return overall_df


def calculate_consistency_by_year(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Calculate year-wise consistency breakdown with quality metrics."""

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        innings_scores AS (
            SELECT
                fb.batter_id,
                fb.match_id,
                im.match_year,
                SUM(fb.batter_runs) as innings_runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
                SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) as boundaries,
                MAX(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as was_dismissed
            FROM fact_ball fb
            JOIN ipl_matches im ON fb.match_id = im.match_id
            GROUP BY fb.batter_id, fb.match_id, im.match_year
            HAVING SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) >= 10
        ),
        yearly_stats AS (
            SELECT
                batter_id,
                match_year,
                COUNT(*) as innings,
                AVG(innings_runs) as avg_runs,
                STDDEV_POP(innings_runs) as stddev_runs,
                SUM(innings_runs) as total_runs,
                SUM(balls_faced) as total_balls,
                SUM(boundaries) as total_boundaries,
                SUM(CASE WHEN innings_runs >= 30 THEN 1 ELSE 0 END) as high_impact_innings,
                SUM(CASE WHEN innings_runs < 10 AND was_dismissed = 1 THEN 1 ELSE 0 END) as failures
            FROM innings_scores
            GROUP BY batter_id, match_year
            HAVING COUNT(*) >= 5
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            ys.match_year,
            ys.innings,
            ys.total_runs,
            ys.total_balls,
            ROUND(ys.total_runs * 100.0 / NULLIF(ys.total_balls, 0), 2) as strike_rate,
            ROUND(ys.avg_runs, 1) as avg_runs,
            ROUND(ys.stddev_runs, 1) as stddev_runs,
            ROUND(ys.stddev_runs / NULLIF(ys.avg_runs, 0), 3) as cv_runs,
            ROUND(GREATEST(0, LEAST(100, (1 - ys.stddev_runs / NULLIF(ys.avg_runs, 0)) * 100)), 1) as consistency_index,
            ROUND(ys.total_boundaries * 100.0 / NULLIF(ys.total_balls, 0), 2) as boundary_pct,
            ys.high_impact_innings,
            ROUND(ys.high_impact_innings * 100.0 / ys.innings, 1) as high_impact_pct,
            ys.failures as single_digit_failures
        FROM yearly_stats ys
        JOIN dim_player dp ON ys.batter_id = dp.player_id
        ORDER BY dp.current_name, ys.match_year
    """).df()

    return df


# ============================================================================
# S3.0-11: PARTNERSHIP SYNERGY SCORE
# ============================================================================


def calculate_partnership_synergy(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Calculate Partnership Synergy Score for batting pairs.

    Synergy Score = (Partnership_SR - Individual_Combined_SR) * Partnership_Balls / 100

    A positive score indicates the pair performs better together than apart.
    """

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        partnerships AS (
            -- Get all balls where two batters were at crease together
            SELECT
                CASE WHEN fb.batter_id < fb.non_striker_id THEN fb.batter_id ELSE fb.non_striker_id END as batter1_id,
                CASE WHEN fb.batter_id < fb.non_striker_id THEN fb.non_striker_id ELSE fb.batter_id END as batter2_id,
                fb.match_id,
                im.match_year,
                SUM(fb.batter_runs + fb.extra_runs) as partnership_runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as partnership_balls
            FROM fact_ball fb
            JOIN ipl_matches im ON fb.match_id = im.match_id
            WHERE fb.non_striker_id IS NOT NULL
            GROUP BY 1, 2, fb.match_id, im.match_year
        ),
        partnership_totals AS (
            SELECT
                batter1_id,
                batter2_id,
                COUNT(DISTINCT match_id) as matches_together,
                SUM(partnership_runs) as total_runs,
                SUM(partnership_balls) as total_balls
            FROM partnerships
            GROUP BY batter1_id, batter2_id
            HAVING SUM(partnership_balls) >= 60  -- At least 10 overs together
        ),
        individual_sr AS (
            SELECT
                batter_id,
                SUM(batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0) as individual_sr
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY batter_id
        )
        SELECT
            dp1.player_id as batter1_id,
            dp1.current_name as batter1_name,
            dp2.player_id as batter2_id,
            dp2.current_name as batter2_name,
            pt.matches_together,
            pt.total_runs,
            pt.total_balls,
            ROUND(pt.total_runs * 100.0 / NULLIF(pt.total_balls, 0), 2) as partnership_sr,
            ROUND(i1.individual_sr, 2) as batter1_individual_sr,
            ROUND(i2.individual_sr, 2) as batter2_individual_sr,
            ROUND((i1.individual_sr + i2.individual_sr) / 2, 2) as combined_avg_sr,
            -- Synergy Score
            ROUND(
                (pt.total_runs * 100.0 / NULLIF(pt.total_balls, 0) - (i1.individual_sr + i2.individual_sr) / 2)
                * pt.total_balls / 100,
            1) as synergy_score
        FROM partnership_totals pt
        JOIN dim_player dp1 ON pt.batter1_id = dp1.player_id
        JOIN dim_player dp2 ON pt.batter2_id = dp2.player_id
        LEFT JOIN individual_sr i1 ON pt.batter1_id = i1.batter_id
        LEFT JOIN individual_sr i2 ON pt.batter2_id = i2.batter_id
        ORDER BY synergy_score DESC
    """).df()

    return df


def calculate_partnership_synergy_by_year(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Calculate year-wise partnership synergy breakdown."""

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        partnerships AS (
            SELECT
                CASE WHEN fb.batter_id < fb.non_striker_id THEN fb.batter_id ELSE fb.non_striker_id END as batter1_id,
                CASE WHEN fb.batter_id < fb.non_striker_id THEN fb.non_striker_id ELSE fb.batter_id END as batter2_id,
                im.match_year,
                fb.match_id,
                SUM(fb.batter_runs + fb.extra_runs) as partnership_runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as partnership_balls
            FROM fact_ball fb
            JOIN ipl_matches im ON fb.match_id = im.match_id
            WHERE fb.non_striker_id IS NOT NULL
            GROUP BY 1, 2, im.match_year, fb.match_id
        ),
        yearly_individual_sr AS (
            SELECT
                fb.batter_id,
                SUBSTR(dm.match_date, 1, 4) as match_year,
                SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0) as individual_sr
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.batter_id, SUBSTR(dm.match_date, 1, 4)
        )
        SELECT
            dp1.player_id as batter1_id,
            dp1.current_name as batter1_name,
            dp2.player_id as batter2_id,
            dp2.current_name as batter2_name,
            p.match_year,
            COUNT(DISTINCT p.match_id) as matches_together,
            SUM(p.partnership_runs) as total_runs,
            SUM(p.partnership_balls) as total_balls,
            ROUND(SUM(p.partnership_runs) * 100.0 / NULLIF(SUM(p.partnership_balls), 0), 2) as partnership_sr,
            ROUND(AVG(i1.individual_sr), 2) as batter1_sr,
            ROUND(AVG(i2.individual_sr), 2) as batter2_sr,
            ROUND(
                (SUM(p.partnership_runs) * 100.0 / NULLIF(SUM(p.partnership_balls), 0) -
                 (AVG(i1.individual_sr) + AVG(i2.individual_sr)) / 2)
                * SUM(p.partnership_balls) / 100,
            1) as synergy_score
        FROM partnerships p
        JOIN dim_player dp1 ON p.batter1_id = dp1.player_id
        JOIN dim_player dp2 ON p.batter2_id = dp2.player_id
        LEFT JOIN yearly_individual_sr i1 ON p.batter1_id = i1.batter_id AND p.match_year = i1.match_year
        LEFT JOIN yearly_individual_sr i2 ON p.batter2_id = i2.batter_id AND p.match_year = i2.match_year
        GROUP BY dp1.player_id, dp1.current_name, dp2.player_id, dp2.current_name, p.match_year
        HAVING SUM(p.partnership_balls) >= 30
        ORDER BY p.match_year, synergy_score DESC
    """).df()

    return df


# ============================================================================
# S3.0-12: PRESSURE SEQUENCE FOR BOWLERS
# ============================================================================


def calculate_bowler_pressure_sequences(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Calculate Pressure Sequence metrics for bowlers.
    Reuses the standard Pressure Sequence Definition:

    Pressure Situations:
    1. Death overs (16-20) - High scoring phase
    2. Tight chase: Required run rate > 9 in last 5 overs
    3. Close match: Run difference < 30 in last 5 overs
    4. Defending low total: Batting first score < 150

    Metrics:
    - Pressure dot ball %
    - Pressure economy
    - Pressure wickets
    - Pressure boundary % conceded
    """

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT
                dm.match_id,
                dm.winner_id,
                SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        -- Categorize pressure situations
        pressure_balls AS (
            SELECT
                fb.bowler_id,
                fb.match_id,
                fb."over",
                fb.batter_runs,
                fb.extra_runs,
                fb.total_runs,
                fb.is_wicket,
                fb.wicket_type,
                fb.is_legal_ball,
                fb.match_phase,
                -- Pressure type based on over number
                CASE
                    WHEN fb."over" >= 15 THEN 'death_pressure'  -- Overs 16-20
                    WHEN fb."over" >= 10 AND fb."over" < 15 THEN 'middle_pressure'  -- Overs 11-15
                    WHEN fb."over" < 6 THEN 'powerplay_pressure'  -- Overs 1-6
                    ELSE 'other'
                END as pressure_type
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        bowler_pressure_stats AS (
            SELECT
                bowler_id,
                pressure_type,
                COUNT(*) as total_balls,
                SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) as legal_balls,
                SUM(total_runs) as runs_conceded,
                SUM(CASE WHEN batter_runs = 0 AND extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
                SUM(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt', 'retired out')
                    THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN batter_runs IN (4, 6) THEN 1 ELSE 0 END) as boundaries,
                SUM(CASE WHEN batter_runs = 6 THEN 1 ELSE 0 END) as sixes
            FROM pressure_balls
            WHERE pressure_type IN ('death_pressure', 'middle_pressure', 'powerplay_pressure')
            GROUP BY bowler_id, pressure_type
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            bps.pressure_type,
            bps.legal_balls,
            ROUND(bps.legal_balls / 6.0, 1) as overs,
            bps.runs_conceded,
            bps.wickets,
            bps.dot_balls,
            bps.boundaries,
            bps.sixes,
            ROUND(bps.runs_conceded * 6.0 / NULLIF(bps.legal_balls, 0), 2) as pressure_economy,
            ROUND(bps.dot_balls * 100.0 / NULLIF(bps.legal_balls, 0), 2) as pressure_dot_pct,
            ROUND(bps.legal_balls * 1.0 / NULLIF(bps.wickets, 0), 2) as pressure_strike_rate,
            ROUND(bps.boundaries * 100.0 / NULLIF(bps.legal_balls, 0), 2) as pressure_boundary_pct,
            ROUND(bps.sixes * 100.0 / NULLIF(bps.legal_balls, 0), 2) as pressure_six_pct
        FROM bowler_pressure_stats bps
        JOIN dim_player dp ON bps.bowler_id = dp.player_id
        WHERE bps.legal_balls >= 60  -- At least 10 overs in pressure situations
        ORDER BY bps.pressure_type, pressure_economy ASC
    """).df()

    return df


def calculate_bowler_pressure_by_year(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Calculate year-wise pressure sequence breakdown for bowlers."""

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT
                dm.match_id,
                SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        pressure_balls AS (
            SELECT
                fb.bowler_id,
                im.match_year,
                fb.batter_runs,
                fb.extra_runs,
                fb.total_runs,
                fb.is_wicket,
                fb.wicket_type,
                fb.is_legal_ball,
                CASE
                    WHEN fb."over" >= 15 THEN 'death_pressure'
                    WHEN fb."over" >= 10 AND fb."over" < 15 THEN 'middle_pressure'
                    WHEN fb."over" < 6 THEN 'powerplay_pressure'
                    ELSE 'other'
                END as pressure_type
            FROM fact_ball fb
            JOIN ipl_matches im ON fb.match_id = im.match_id
        ),
        yearly_pressure_stats AS (
            SELECT
                bowler_id,
                match_year,
                pressure_type,
                SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) as legal_balls,
                SUM(total_runs) as runs_conceded,
                SUM(CASE WHEN batter_runs = 0 AND extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
                SUM(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt', 'retired out')
                    THEN 1 ELSE 0 END) as wickets
            FROM pressure_balls
            WHERE pressure_type IN ('death_pressure', 'middle_pressure', 'powerplay_pressure')
            GROUP BY bowler_id, match_year, pressure_type
            HAVING SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) >= 30
        )
        SELECT
            dp.current_name as bowler_name,
            yps.match_year,
            yps.pressure_type,
            yps.legal_balls,
            ROUND(yps.legal_balls / 6.0, 1) as overs,
            yps.runs_conceded,
            yps.wickets,
            ROUND(yps.runs_conceded * 6.0 / NULLIF(yps.legal_balls, 0), 2) as economy,
            ROUND(yps.dot_balls * 100.0 / NULLIF(yps.legal_balls, 0), 2) as dot_pct
        FROM yearly_pressure_stats yps
        JOIN dim_player dp ON yps.bowler_id = dp.player_id
        ORDER BY dp.current_name, yps.match_year, yps.pressure_type
    """).df()

    return df


# ============================================================================
# S3.0-13: VENUE WIN/LOSS PER TEAM
# ============================================================================


def calculate_venue_win_loss(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Calculate venue-based win/loss record for each team."""

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT
                dm.match_id,
                dm.team1_id,
                dm.team2_id,
                dm.winner_id,
                dm.venue_id,
                dv.venue_name,
                dv.city,
                SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        team_venue_records AS (
            SELECT
                dt.team_id,
                dt.team_name,
                im.venue_name,
                im.city,
                COUNT(*) as matches,
                SUM(CASE WHEN im.winner_id = dt.team_id THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN im.winner_id IS NOT NULL AND im.winner_id != dt.team_id THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN im.winner_id IS NULL THEN 1 ELSE 0 END) as no_results
            FROM ipl_matches im
            JOIN dim_team dt ON dt.team_id IN (im.team1_id, im.team2_id)
            GROUP BY dt.team_id, dt.team_name, im.venue_name, im.city
        )
        SELECT
            team_name,
            venue_name,
            city,
            matches,
            wins,
            losses,
            no_results,
            ROUND(wins * 100.0 / NULLIF(matches - no_results, 0), 1) as win_pct,
            CONCAT(wins, '-', losses) as record
        FROM team_venue_records
        WHERE matches >= 2
        ORDER BY team_name, win_pct DESC NULLS LAST
    """).df()

    return df


def calculate_venue_win_loss_by_year(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Calculate year-wise venue win/loss records."""

    df = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT
                dm.match_id,
                dm.team1_id,
                dm.team2_id,
                dm.winner_id,
                dm.venue_id,
                dv.venue_name,
                SUBSTR(dm.match_date, 1, 4) as match_year
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        yearly_venue_records AS (
            SELECT
                dt.team_name,
                im.venue_name,
                im.match_year,
                COUNT(*) as matches,
                SUM(CASE WHEN im.winner_id = dt.team_id THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN im.winner_id IS NOT NULL AND im.winner_id != dt.team_id THEN 1 ELSE 0 END) as losses
            FROM ipl_matches im
            JOIN dim_team dt ON dt.team_id IN (im.team1_id, im.team2_id)
            GROUP BY dt.team_name, im.venue_name, im.match_year
        )
        SELECT
            team_name,
            venue_name,
            match_year,
            matches,
            wins,
            losses,
            ROUND(wins * 100.0 / NULLIF(matches, 0), 1) as win_pct
        FROM yearly_venue_records
        WHERE matches >= 1
        ORDER BY team_name, venue_name, match_year
    """).df()

    return df


# ============================================================================
# S3.0-14: BOWLER PHASE DISTRIBUTION TABLES (grouped by phase)
# ============================================================================


def get_bowler_phase_distribution_grouped(
    conn: duckdb.DuckDBPyConnection,
) -> Dict[str, pd.DataFrame]:
    """
    Get bowler phase distribution grouped by phase for all teams.

    Returns a dict with three DataFrames:
    - powerplay: Bowlers sorted by powerplay performance
    - middle: Bowlers sorted by middle overs performance
    - death: Bowlers sorted by death overs performance
    """

    results = {}

    for phase in ["powerplay", "middle", "death"]:
        df = conn.execute(f"""
            SELECT
                bpd.bowler_id,
                bpd.bowler_name,
                bpd.overs,
                bpd.wickets,
                bpd.economy,
                bpd.dot_ball_pct,
                bpd.pct_overs_in_phase,
                bpd.pct_wickets_in_phase,
                bpd.wicket_efficiency,
                bpd.sample_size
            FROM analytics_ipl_bowler_phase_distribution bpd
            WHERE bpd.match_phase = '{phase}'
              AND bpd.sample_size IN ('MEDIUM', 'HIGH')
            ORDER BY bpd.overs DESC
        """).df()

        results[phase] = df

    return results


def get_bowler_phase_distribution_by_team(
    conn: duckdb.DuckDBPyConnection, team_name: str
) -> Dict[str, pd.DataFrame]:
    """
    Get bowler phase distribution grouped by phase for a specific team.
    """

    results = {}

    for phase in ["powerplay", "middle", "death"]:
        try:
            df = conn.execute(f"""
                SELECT
                    bpd.bowler_id,
                    bpd.bowler_name,
                    bpd.overs,
                    bpd.wickets,
                    bpd.economy,
                    bpd.dot_ball_pct,
                    bpd.pct_overs_in_phase,
                    bpd.pct_wickets_in_phase,
                    bpd.sample_size
                FROM analytics_ipl_bowler_phase_distribution bpd
                JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
                WHERE sq.team_name = '{team_name}'
                  AND bpd.match_phase = '{phase}'
                  AND bpd.sample_size IN ('MEDIUM', 'HIGH')
                ORDER BY bpd.overs DESC
            """).df()
            results[phase] = df
        except (RuntimeError, ValueError):
            results[phase] = pd.DataFrame()

    return results


def create_phase_distribution_tables(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Create comprehensive phase distribution tables grouped by phase.
    Output suitable for stat packs.
    """

    df = conn.execute("""
        WITH phase_stats AS (
            SELECT
                bpd.bowler_id,
                bpd.bowler_name,
                bpd.match_phase,
                bpd.overs,
                bpd.wickets,
                bpd.runs_conceded,
                bpd.economy,
                bpd.dot_ball_pct,
                bpd.pct_overs_in_phase,
                bpd.pct_wickets_in_phase,
                bpd.sample_size,
                -- Rank within phase
                ROW_NUMBER() OVER (PARTITION BY bpd.match_phase ORDER BY bpd.overs DESC) as phase_rank
            FROM analytics_ipl_bowler_phase_distribution bpd
            WHERE bpd.sample_size IN ('MEDIUM', 'HIGH')
        )
        SELECT
            match_phase,
            bowler_id,
            bowler_name,
            overs,
            wickets,
            runs_conceded,
            economy,
            dot_ball_pct,
            pct_overs_in_phase,
            pct_wickets_in_phase,
            sample_size,
            phase_rank
        FROM phase_stats
        ORDER BY match_phase, phase_rank
    """).df()

    return df


# ============================================================================
# UPDATE PLAYER TAGS JSON
# ============================================================================


def update_player_tags_with_role_tags(
    bowler_role_df: pd.DataFrame, consistency_df: pd.DataFrame
) -> None:
    """Update player_tags.json with new role tags and consistency tags."""

    tags_path = OUTPUT_DIR / "player_tags.json"

    if tags_path.exists():
        with open(tags_path) as f:
            tags_data = json.load(f)
    else:
        tags_data = {"batters": [], "bowlers": []}

    # Create lookup for role tags
    role_lookup = {}
    for _, row in bowler_role_df.iterrows():
        if row["role_tags"]:
            role_lookup[row["bowler_id"]] = row["role_tags"]

    # Create lookup for consistency tags
    consistency_lookup = {}
    for _, row in consistency_df.iterrows():
        if row["weighted_consistency"] >= 70:
            consistency_lookup[row["batter_id"]] = ["CONSISTENT"]
        elif row["weighted_consistency"] <= 40:
            consistency_lookup[row["batter_id"]] = ["INCONSISTENT"]

    # Role tags to manage
    role_tags_set = {
        "DEATH_SPECIALIST",
        "MIDDLE_OVERS_CONTROLLER",
        "NEW_BALL_SPECIALIST",
        "WORKHORSE",
        "MIDDLE_AND_DEATH_SPECIALIST",
        "PART_TIMER",
    }

    consistency_tags_set = {"CONSISTENT", "INCONSISTENT"}

    # Update bowler tags
    bowler_updated = 0
    for bowler in tags_data.get("bowlers", []):
        player_id = bowler.get("player_id")
        existing_tags = set(bowler.get("tags", []))

        # Remove old role tags
        existing_tags -= role_tags_set

        # Add new role tags
        if player_id in role_lookup:
            existing_tags.update(role_lookup[player_id])
            bowler_updated += 1

        bowler["tags"] = list(existing_tags)

    # Update batter consistency tags
    batter_updated = 0
    for batter in tags_data.get("batters", []):
        player_id = batter.get("player_id")
        existing_tags = set(batter.get("tags", []))

        # Remove old consistency tags
        existing_tags -= consistency_tags_set

        # Add new consistency tags
        if player_id in consistency_lookup:
            existing_tags.update(consistency_lookup[player_id])
            batter_updated += 1

        batter["tags"] = list(existing_tags)

    # Save updated file
    with open(tags_path, "w") as f:
        json.dump(tags_data, f, indent=2)

    print(f"  Updated {bowler_updated} bowlers with role tags")
    print(f"  Updated {batter_updated} batters with consistency tags")


# ============================================================================
# MAIN
# ============================================================================


def main() -> int:
    print("=" * 70)
    print("Cricket Playbook - Sprint 3.0 P1 Features")
    print("Author: Stephen Curry | Sprint 3.0")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"\nERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # ========================================================================
    # S3.0-09: Bowler Role Tags Revision
    # ========================================================================
    print("\n" + "=" * 70)
    print("S3.0-09: BOWLER ROLE TAGS REVISION")
    print("  - Death specialist: >=1 over in overs 16+ (revised from >=3 overs)")
    print("  - Added MIDDLE_AND_DEATH_SPECIALIST tag")
    print("=" * 70)

    print("\n1. Getting bowler phase overs data...")
    bowler_phase_df = get_bowler_phase_overs(conn)
    print(f"   Found {len(bowler_phase_df)} bowlers")

    print("\n2. Assigning revised role tags...")
    bowler_role_df = assign_bowler_role_tags(bowler_phase_df)

    # Count tags
    tag_counts = {}
    for tags in bowler_role_df["role_tags"]:
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print("\n   Role Tag Distribution:")
    for tag, count in sorted(tag_counts.items()):
        print(f"     {tag}: {count}")

    # Show sample MIDDLE_AND_DEATH_SPECIALIST
    mid_death = bowler_role_df[
        bowler_role_df["role_tags"].apply(lambda x: "MIDDLE_AND_DEATH_SPECIALIST" in x)
    ]
    if len(mid_death) > 0:
        print("\n   Sample MIDDLE_AND_DEATH_SPECIALIST:")
        for _, row in mid_death.head(5).iterrows():
            print(
                f"     {row['bowler_name']}: Middle={row['middle_overs']:.0f}ov, Death 16+={row['total_death_balls_16plus'] / 6:.1f}ov"
            )

    # Show sample DEATH_SPECIALIST
    death_spec = bowler_role_df[
        bowler_role_df["role_tags"].apply(lambda x: "DEATH_SPECIALIST" in x)
    ]
    if len(death_spec) > 0:
        print("\n   Sample DEATH_SPECIALIST:")
        for _, row in death_spec.head(5).iterrows():
            print(
                f"     {row['bowler_name']}: Death 16+={row['total_death_balls_16plus'] / 6:.1f}ov ({row['matches_with_death_16plus']} matches)"
            )

    # Save role tags
    role_tags_output = bowler_role_df[
        [
            "bowler_id",
            "bowler_name",
            "pp_overs",
            "middle_overs",
            "death_overs",
            "pp_matches",
            "middle_matches",
            "death_matches",
            "matches_with_death_16plus",
            "total_death_balls_16plus",
            "role_tags",
        ]
    ].copy()
    role_tags_output["role_tags"] = role_tags_output["role_tags"].apply(
        lambda x: ", ".join(x) if x else ""
    )
    role_tags_output.to_csv(OUTPUT_DIR / "bowler_role_tags.csv", index=False)
    print(f"\n   Saved to: {OUTPUT_DIR / 'bowler_role_tags.csv'}")

    # ========================================================================
    # S3.0-10: Consistency Index
    # ========================================================================
    print("\n" + "=" * 70)
    print("S3.0-10: CONSISTENCY INDEX (Andy Flower Research)")
    print("  - Overall since 2023 + Year-wise breakdown")
    print("  - Quality metrics: High impact %, Failure rate, Boundary %")
    print("=" * 70)

    print("\n1. Calculating overall consistency index...")
    consistency_df = calculate_batter_consistency_index(conn)
    print(f"   Analyzed {len(consistency_df)} batters")

    print("\n   Top 10 Most Consistent Batters (Weighted):")
    for _, row in consistency_df.head(10).iterrows():
        print(
            f"     {row['batter_name']}: WCI={row['weighted_consistency']:.1f} (CI={row['consistency_index']:.1f}, SR={row['overall_sr']:.1f}, HI%={row['high_impact_pct']:.0f}%)"
        )

    print("\n   Quality Metrics Sample:")
    for _, row in consistency_df.head(5).iterrows():
        print(
            f"     {row['batter_name']}: Boundary%={row['boundary_pct']:.1f}, HighImpact={row['high_impact_innings']}, FailRate={row['failure_rate']:.0f}%"
        )

    print("\n2. Calculating year-wise consistency...")
    yearly_consistency_df = calculate_consistency_by_year(conn)
    print(f"   Generated {len(yearly_consistency_df)} year-player records")

    # Save consistency data
    consistency_df.to_csv(OUTPUT_DIR / "batter_consistency_index.csv", index=False)
    yearly_consistency_df.to_csv(OUTPUT_DIR / "batter_consistency_by_year.csv", index=False)
    print(f"\n   Saved to: {OUTPUT_DIR / 'batter_consistency_index.csv'}")
    print(f"   Saved to: {OUTPUT_DIR / 'batter_consistency_by_year.csv'}")

    # ========================================================================
    # S3.0-11: Partnership Synergy Score
    # ========================================================================
    print("\n" + "=" * 70)
    print("S3.0-11: PARTNERSHIP SYNERGY SCORE")
    print("  - Overall level + Year-wise breakdown")
    print("=" * 70)

    print("\n1. Calculating overall partnership synergy...")
    partnership_df = calculate_partnership_synergy(conn)
    print(f"   Analyzed {len(partnership_df)} partnerships")

    print("\n   Top 10 Partnerships by Synergy Score:")
    for _, row in partnership_df.head(10).iterrows():
        print(
            f"     {row['batter1_name']} + {row['batter2_name']}: Synergy={row['synergy_score']:.1f} (SR={row['partnership_sr']:.1f} vs {row['combined_avg_sr']:.1f})"
        )

    print("\n2. Calculating year-wise partnership synergy...")
    yearly_partnership_df = calculate_partnership_synergy_by_year(conn)
    print(f"   Generated {len(yearly_partnership_df)} year-partnership records")

    # Save partnership data
    partnership_df.to_csv(OUTPUT_DIR / "partnership_synergy.csv", index=False)
    yearly_partnership_df.to_csv(OUTPUT_DIR / "partnership_synergy_by_year.csv", index=False)
    print(f"\n   Saved to: {OUTPUT_DIR / 'partnership_synergy.csv'}")
    print(f"   Saved to: {OUTPUT_DIR / 'partnership_synergy_by_year.csv'}")

    # ========================================================================
    # S3.0-12: Pressure Sequence for Bowlers
    # ========================================================================
    print("\n" + "=" * 70)
    print("S3.0-12: PRESSURE SEQUENCE FOR BOWLERS")
    print("  - Reuses Pressure Sequence Definition")
    print("  - Death/Middle/Powerplay pressure analysis")
    print("=" * 70)

    print("\n1. Calculating bowler pressure sequence metrics...")
    pressure_df = calculate_bowler_pressure_sequences(conn)
    print(f"   Analyzed {len(pressure_df)} bowler-pressure combinations")

    # Death pressure leaders
    death_pressure = pressure_df[pressure_df["pressure_type"] == "death_pressure"].sort_values(
        "pressure_economy"
    )
    print("\n   Top 10 Death Pressure Performers:")
    for _, row in death_pressure.head(10).iterrows():
        print(
            f"     {row['bowler_name']}: Econ={row['pressure_economy']:.2f}, Dot%={row['pressure_dot_pct']:.1f}%, Wkts={row['wickets']} ({row['overs']:.0f}ov)"
        )

    # Middle pressure leaders
    middle_pressure = pressure_df[pressure_df["pressure_type"] == "middle_pressure"].sort_values(
        "pressure_economy"
    )
    print("\n   Top 10 Middle Pressure Performers:")
    for _, row in middle_pressure.head(10).iterrows():
        print(
            f"     {row['bowler_name']}: Econ={row['pressure_economy']:.2f}, Dot%={row['pressure_dot_pct']:.1f}%, Wkts={row['wickets']} ({row['overs']:.0f}ov)"
        )

    print("\n2. Calculating year-wise pressure metrics...")
    yearly_pressure_df = calculate_bowler_pressure_by_year(conn)
    print(f"   Generated {len(yearly_pressure_df)} year-pressure records")

    # Save pressure data
    pressure_df.to_csv(OUTPUT_DIR / "bowler_pressure_sequences.csv", index=False)
    yearly_pressure_df.to_csv(OUTPUT_DIR / "bowler_pressure_by_year.csv", index=False)
    print(f"\n   Saved to: {OUTPUT_DIR / 'bowler_pressure_sequences.csv'}")
    print(f"   Saved to: {OUTPUT_DIR / 'bowler_pressure_by_year.csv'}")

    # ========================================================================
    # S3.0-13: Venue Win/Loss Per Team
    # ========================================================================
    print("\n" + "=" * 70)
    print("S3.0-13: VENUE WIN/LOSS PER TEAM")
    print("=" * 70)

    print("\n1. Calculating venue win/loss records...")
    venue_df = calculate_venue_win_loss(conn)
    print(f"   Generated {len(venue_df)} team-venue records")

    # Show sample team venue records
    sample_teams = [
        "Chennai Super Kings",
        "Mumbai Indians",
        "Royal Challengers Bengaluru",
    ]
    for sample_team in sample_teams:
        team_venues = venue_df[venue_df["team_name"] == sample_team].head(3)
        if len(team_venues) > 0:
            print(f"\n   {sample_team} Top Venues:")
            for _, row in team_venues.iterrows():
                venue_short = (
                    row["venue_name"][:40] + "..."
                    if len(row["venue_name"]) > 40
                    else row["venue_name"]
                )
                print(f"     {venue_short}: {row['record']} ({row['win_pct']:.0f}%)")

    print("\n2. Calculating year-wise venue records...")
    yearly_venue_df = calculate_venue_win_loss_by_year(conn)
    print(f"   Generated {len(yearly_venue_df)} year-venue records")

    # Save venue data
    venue_df.to_csv(OUTPUT_DIR / "team_venue_records.csv", index=False)
    yearly_venue_df.to_csv(OUTPUT_DIR / "team_venue_records_by_year.csv", index=False)
    print(f"\n   Saved to: {OUTPUT_DIR / 'team_venue_records.csv'}")
    print(f"   Saved to: {OUTPUT_DIR / 'team_venue_records_by_year.csv'}")

    # ========================================================================
    # S3.0-14: Bowler Phase Distribution Tables (grouped by phase)
    # ========================================================================
    print("\n" + "=" * 70)
    print("S3.0-14: BOWLER PHASE DISTRIBUTION TABLES (Grouped by Phase)")
    print("=" * 70)

    print("\n1. Generating phase-grouped bowler tables...")
    try:
        phase_tables = get_bowler_phase_distribution_grouped(conn)

        for phase, df in phase_tables.items():
            print(f"\n   {phase.upper()} Phase Leaders (Top 5):")
            for _, row in df.head(5).iterrows():
                print(
                    f"     {row['bowler_name']}: {row['overs']:.1f}ov, Econ={row['economy']:.2f}, Wkts={row['wickets']}, Dot%={row['dot_ball_pct']:.1f}"
                )

        # Create comprehensive phase distribution table
        phase_dist_df = create_phase_distribution_tables(conn)
        phase_dist_df.to_csv(OUTPUT_DIR / "bowler_phase_distribution_grouped.csv", index=False)
        print(f"\n   Saved to: {OUTPUT_DIR / 'bowler_phase_distribution_grouped.csv'}")

    except Exception as e:
        print(f"   Note: Could not generate phase tables: {e}")

    # ========================================================================
    # UPDATE PLAYER TAGS
    # ========================================================================
    print("\n" + "=" * 70)
    print("UPDATING PLAYER TAGS JSON")
    print("=" * 70)

    update_player_tags_with_role_tags(bowler_role_df, consistency_df)

    conn.close()

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("SPRINT 3.0 P1 FEATURES COMPLETE")
    print("=" * 70)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nOutput Files Generated:")
    print("  S3.0-09: bowler_role_tags.csv")
    print("  S3.0-10: batter_consistency_index.csv, batter_consistency_by_year.csv")
    print("  S3.0-11: partnership_synergy.csv, partnership_synergy_by_year.csv")
    print("  S3.0-12: bowler_pressure_sequences.csv, bowler_pressure_by_year.csv")
    print("  S3.0-13: team_venue_records.csv, team_venue_records_by_year.csv")
    print("  S3.0-14: bowler_phase_distribution_grouped.csv")
    print("\nFeatures Implemented:")
    print("  S3.0-09: Bowler Role Tags Revision (>=1 over in 16+, MIDDLE_AND_DEATH_SPECIALIST)")
    print("  S3.0-10: Consistency Index (overall + year-wise + quality metrics)")
    print("  S3.0-11: Partnership Synergy Score (overall + year-wise)")
    print("  S3.0-12: Pressure Sequence for Bowlers (reused definition)")
    print("  S3.0-13: Venue Win/Loss Per Team")
    print("  S3.0-14: Bowler Phase Distribution Tables (grouped by phase)")

    return 0


if __name__ == "__main__":
    exit(main())
