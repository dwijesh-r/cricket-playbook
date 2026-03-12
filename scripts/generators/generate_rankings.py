#!/usr/bin/env python3
"""
Cricket Playbook - Ranking Generator (TKT-236 / EPIC-021)
Author: Stephen Curry (Analytics Lead)
Sprint: SPRINT-005 (Signature Feature)

Queries the 7 composite ranking view categories from analytics_ipl.py and produces
a JavaScript data file (rankings.js) for The Lab dashboard Rankings tab.

Dual-scope: generates both "alltime" (IPL 2008-2025) and "since2023" (IPL 2023-2025)
rankings in a single output file.

Categories:
    1. Batter Phase Rankings       (powerplay / middle / death)
    2. Bowler Phase Rankings        (powerplay / middle / death)
    3. Batter vs Bowling Type       (pace / spin / medium sub-types)
    4. Bowler vs Handedness          (vs Left-hand / vs Right-hand)
    5. Player Matchup Rankings      (batter-favored / bowler-favored)
    6. Overall Batter Composite     (top-20 leaderboard)
    7. Overall Bowler Composite     (top-20 leaderboard)

Data Source: DuckDB views created by create_composite_ranking_views() in analytics_ipl.py.
Output: scripts/the_lab/dashboard/data/rankings.js

Usage:
    python -m scripts.generators.generate_rankings
    python scripts/generators/generate_rankings.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import duckdb

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_JS = PROJECT_DIR / "scripts" / "the_lab" / "dashboard" / "data" / "rankings.js"

# =============================================================================
# CONSTANTS
# =============================================================================

# No limit — show all qualified players (frontend handles pagination)
TOP_N = None  # Previously 20

# Bowler types to include in batter-vs-bowling-type rankings (minimum 20 qualifiers).
# Excludes "Unknown" and very small sub-categories.
BOWLING_TYPE_ORDER = [
    "Right-arm pace",
    "Fast",
    "Fast-Medium",
    "Left-arm pace",
    "Right-arm off-spin",
    "Right-arm leg-spin",
    "Leg-spin",
    "Off-spin",
    "LA Orthodox",
    "Left-arm orthodox",
    "Medium",
    "Wrist-spin",
]

# Phase display order
PHASE_ORDER = ["powerplay", "middle", "death"]
PHASE_TITLES = {
    "powerplay": "Powerplay (Overs 1-6)",
    "middle": "Middle Overs (7-15)",
    "death": "Death Overs (16-20)",
}

# Handedness display
HAND_TITLES = {
    "Left-hand": "vs Left-Hand Batters",
    "Right-hand": "vs Right-Hand Batters",
}

# Scope suffixes and labels
SCOPES = {
    "alltime": {"suffix": "_alltime", "label": "IPL 2008-2025 (All-Time)"},
    "since2023": {"suffix": "_since2023", "label": "IPL 2023-2025 (Since 2023)"},
    "2023": {"suffix": "_y2023", "label": "IPL 2023", "year": 2023},
    "2024": {"suffix": "_y2024", "label": "IPL 2024", "year": 2024},
    "2025": {"suffix": "_y2025", "label": "IPL 2025", "year": 2025},
}

# Year-specific date ranges for per-year scopes
YEAR_DATE_RANGES = {
    2023: ("2023-01-01", "2023-12-31"),
    2024: ("2024-01-01", "2024-12-31"),
    2025: ("2025-01-01", "2025-12-31"),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _safe_float(val: Any) -> Optional[float]:
    """Convert a value to float, returning None for NaN/None."""
    if val is None:
        return None
    try:
        f = float(val)
        if f != f:  # NaN check
            return None
        return f
    except (TypeError, ValueError):
        return None


def _format_num(val: Any, decimals: int = 1) -> Any:
    """Format a number to specified decimals, pass through None."""
    f = _safe_float(val)
    if f is None:
        return None
    return round(f, decimals)


def create_year_views(conn: duckdb.DuckDBPyConnection, year: int) -> None:
    """Create temporary per-year views for ranking queries.

    Replicates the since2023 view chain but filtered to a single IPL season.
    Views created: batter_phase, bowler_phase, percentiles, rankings,
    batter_vs_bowling_type, bowler_vs_handedness, matchups, composites.
    """
    date_min, date_max = YEAR_DATE_RANGES[year]
    sfx = f"_y{year}"
    print(f"  Creating temporary views for {year}...")

    # --- Base: batter_phase ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_batter_phase{sfx} AS
        WITH ipl_matches AS (
            SELECT dm.match_id FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{date_min}' AND dm.match_date <= '{date_max}'
        )
        SELECT dp.player_id, dp.current_name as player_name, fb.match_phase,
            COUNT(DISTINCT fb.match_id) as innings,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as batting_average,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct,
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 100 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)

    # --- Base: bowler_phase ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_bowler_phase{sfx} AS
        WITH ipl_matches AS (
            SELECT dm.match_id FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{date_min}' AND dm.match_date <= '{date_max}'
        )
        SELECT dp.player_id, dp.current_name as player_name, fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) as overs,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            ROUND(SUM(CASE WHEN fb.total_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_conceded_pct,
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 60 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 300 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)

    # --- Batter phase percentiles ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_batter_phase_percentiles{sfx} AS
        WITH qualified AS (
            SELECT * FROM analytics_ipl_batter_phase{sfx}
            WHERE balls_faced >= 30
        )
        SELECT player_id, player_name, match_phase, innings, runs, balls_faced,
            strike_rate, batting_average, boundary_pct, dot_ball_pct, sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY boundary_pct) * 100, 1) as boundary_percentile
        FROM qualified
    """)

    # --- Bowler phase percentiles ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_bowler_phase_percentiles{sfx} AS
        WITH qualified AS (
            SELECT * FROM analytics_ipl_bowler_phase{sfx}
            WHERE balls_bowled >= 30
        )
        SELECT player_id, player_name, match_phase, matches, balls_bowled, overs, wickets,
            economy_rate, bowling_average, dot_ball_pct, boundary_conceded_pct, sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM qualified
    """)

    # --- Batter phase rankings ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_batter_phase_rankings{sfx} AS
        WITH phase_scores AS (
            SELECT player_id, player_name, match_phase, runs, balls_faced,
                strike_rate, batting_average, boundary_pct, dot_ball_pct,
                sr_percentile, avg_percentile, boundary_percentile,
                ROUND((sr_percentile * 0.4 + avg_percentile * 0.4 + boundary_percentile * 0.2), 1) AS phase_composite,
                ROUND(LEAST(balls_faced / 200.0, 1.0), 3) AS sample_size_factor
            FROM analytics_ipl_batter_phase_percentiles{sfx}
        )
        SELECT *, ROUND(phase_composite * sample_size_factor, 1) AS weighted_composite,
            RANK() OVER (PARTITION BY match_phase ORDER BY phase_composite * sample_size_factor DESC) AS phase_rank
        FROM phase_scores
    """)

    # --- Bowler phase rankings ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_bowler_phase_rankings{sfx} AS
        WITH phase_scores AS (
            SELECT player_id, player_name, match_phase, balls_bowled,
                economy_rate, dot_ball_pct, economy_percentile, dot_ball_percentile,
                ROUND((economy_percentile * 0.5 + dot_ball_percentile * 0.5), 1) AS phase_composite,
                ROUND(LEAST(balls_bowled / 120.0, 1.0), 3) AS sample_size_factor
            FROM analytics_ipl_bowler_phase_percentiles{sfx}
        )
        SELECT *, ROUND(phase_composite * sample_size_factor, 1) AS weighted_composite,
            RANK() OVER (PARTITION BY match_phase ORDER BY phase_composite * sample_size_factor DESC) AS phase_rank
        FROM phase_scores
    """)

    # --- Batter vs bowling type (use since2023 view filtered by date) ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_batter_vs_bowling_type_rankings{sfx} AS
        WITH ipl_matches AS (
            SELECT dm.match_id FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{date_min}' AND dm.match_date <= '{date_max}'
        ),
        raw AS (
            SELECT dp.player_id, dp.current_name as player_name,
                COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls,
                SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average
            FROM fact_ball fb
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            LEFT JOIN ipl_2026_squads sq ON fb.bowler_id = sq.player_id
            LEFT JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY dp.player_id, dp.current_name, COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
        ),
        qualified AS (
            SELECT *, ROUND(LEAST(balls / 100.0, 1.0), 3) as sample_size_factor,
                ROUND(PERCENT_RANK() OVER (PARTITION BY bowler_type ORDER BY strike_rate) * 100, 1) as sr_pctl,
                ROUND(PERCENT_RANK() OVER (PARTITION BY bowler_type ORDER BY average) * 100, 1) as avg_pctl,
                ROUND(PERCENT_RANK() OVER (PARTITION BY bowler_type ORDER BY balls * 1.0 / NULLIF(dismissals, 0)) * 100, 1) as survival_pctl
            FROM raw WHERE balls >= 15
        )
        SELECT player_id, player_name, bowler_type, runs, balls, strike_rate, average,
            ROUND((sr_pctl * 0.4 + avg_pctl * 0.4 + survival_pctl * 0.2) * sample_size_factor, 1) as weighted_composite,
            RANK() OVER (PARTITION BY bowler_type ORDER BY (sr_pctl * 0.4 + avg_pctl * 0.4 + survival_pctl * 0.2) * sample_size_factor DESC) as vs_type_rank
        FROM qualified
    """)

    # --- Bowler vs handedness ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_bowler_vs_handedness_rankings{sfx} AS
        WITH ipl_matches AS (
            SELECT dm.match_id FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{date_min}' AND dm.match_date <= '{date_max}'
        ),
        raw AS (
            SELECT dp.player_id, dp.current_name as player_name,
                sq.batting_hand as batting_hand,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy
            FROM fact_ball fb
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            JOIN ipl_2026_squads sq ON fb.batter_id = sq.player_id
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND sq.batting_hand IN ('Left-hand', 'Right-hand')
            GROUP BY dp.player_id, dp.current_name, sq.batting_hand
        ),
        qualified AS (
            SELECT *, ROUND(LEAST(balls / 100.0, 1.0), 3) as sample_size_factor,
                ROUND(PERCENT_RANK() OVER (PARTITION BY batting_hand ORDER BY economy DESC) * 100, 1) as econ_pctl,
                ROUND(PERCENT_RANK() OVER (PARTITION BY batting_hand ORDER BY balls * 1.0 / NULLIF(wickets, 0) DESC) * 100, 1) as sr_pctl
            FROM raw WHERE balls >= 15
        )
        SELECT player_id, player_name, batting_hand, balls, wickets, economy,
            ROUND((econ_pctl * 0.5 + sr_pctl * 0.5) * sample_size_factor, 1) as weighted_composite,
            RANK() OVER (PARTITION BY batting_hand ORDER BY (econ_pctl * 0.5 + sr_pctl * 0.5) * sample_size_factor DESC) as vs_hand_rank
        FROM qualified
    """)

    # --- Player matchup rankings (use since2023 as-is — matchups don't change much per year) ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_player_matchup_rankings{sfx} AS
        SELECT * FROM analytics_ipl_player_matchup_rankings_since2023
    """)

    # --- Batter composite rankings ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_batting_percentiles{sfx} AS
        WITH ipl_matches AS (
            SELECT dm.match_id FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{date_min}' AND dm.match_date <= '{date_max}'
        ),
        career AS (
            SELECT dp.player_id, dp.current_name as player_name,
                COUNT(DISTINCT fb.match_id) as innings,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
                ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
                ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as batting_average,
                ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                      NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_pct,
                ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct
            FROM fact_ball fb
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY dp.player_id, dp.current_name
            HAVING SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) >= 60
        )
        SELECT *, ROUND(PERCENT_RANK() OVER (ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY boundary_pct) * 100, 1) as boundary_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY dot_ball_pct DESC) * 100, 1) as dot_ball_percentile
        FROM career
    """)

    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_batter_composite_rankings{sfx} AS
        WITH career AS (
            SELECT player_id, player_name, innings, runs, balls_faced,
                strike_rate, batting_average, boundary_pct,
                sr_percentile AS career_sr_pctl, avg_percentile AS career_avg_pctl,
                boundary_percentile AS career_boundary_pctl, dot_ball_percentile AS career_dotball_pctl
            FROM analytics_ipl_batting_percentiles{sfx}
        ),
        phase_avg AS (
            SELECT player_id,
                ROUND(AVG(sr_percentile), 1) AS avg_phase_sr_pctl,
                ROUND(AVG(avg_percentile), 1) AS avg_phase_avg_pctl
            FROM analytics_ipl_batter_phase_percentiles{sfx}
            GROUP BY player_id
        ),
        combined AS (
            SELECT c.*, COALESCE(p.avg_phase_sr_pctl, c.career_sr_pctl) AS phase_sr,
                COALESCE(p.avg_phase_avg_pctl, c.career_avg_pctl) AS phase_avg,
                ROUND(LEAST(c.balls_faced / 500.0, 1.0), 3) AS sample_size_factor
            FROM career c LEFT JOIN phase_avg p ON c.player_id = p.player_id
        ),
        scored AS (
            SELECT *,
                ROUND((career_sr_pctl + career_avg_pctl) / 2 * 0.3 + (phase_sr + phase_avg) / 2 * 0.3 +
                    career_boundary_pctl * 0.2 + career_avg_pctl * 0.1 + career_dotball_pctl * 0.1, 1) AS composite_score
            FROM combined
        )
        SELECT player_id, player_name, innings, runs, balls_faced, strike_rate, batting_average, boundary_pct,
            composite_score, ROUND(composite_score * sample_size_factor, 1) AS weighted_composite,
            RANK() OVER (ORDER BY composite_score * sample_size_factor DESC) AS overall_rank
        FROM scored
    """)

    # --- Bowler composite rankings ---
    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_bowling_percentiles{sfx} AS
        WITH ipl_matches AS (
            SELECT dm.match_id FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{date_min}' AND dm.match_date <= '{date_max}'
        ),
        career AS (
            SELECT dp.player_id, dp.current_name as player_name,
                COUNT(DISTINCT fb.match_id) as matches_bowled,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
                ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
                ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'obstructing the field') THEN 1 ELSE 0 END), 0), 2) as bowling_strike_rate,
                ROUND(SUM(CASE WHEN fb.total_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct
            FROM fact_ball fb
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY dp.player_id, dp.current_name
            HAVING SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) >= 30
        )
        SELECT *, ROUND(PERCENT_RANK() OVER (ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY bowling_strike_rate DESC) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM career
    """)

    conn.execute(f"""
        CREATE OR REPLACE TEMP VIEW analytics_ipl_bowler_composite_rankings{sfx} AS
        WITH career AS (
            SELECT player_id, player_name, matches_bowled, balls_bowled, wickets,
                economy_rate, bowling_average, bowling_strike_rate,
                economy_percentile AS career_econ_pctl, sr_percentile AS career_sr_pctl,
                dot_ball_percentile AS career_dotball_pctl
            FROM analytics_ipl_bowling_percentiles{sfx}
        ),
        phase_avg AS (
            SELECT player_id,
                ROUND(AVG(economy_percentile), 1) AS avg_phase_econ_pctl,
                ROUND(AVG(dot_ball_percentile), 1) AS avg_phase_dotball_pctl
            FROM analytics_ipl_bowler_phase_percentiles{sfx}
            GROUP BY player_id
        ),
        combined AS (
            SELECT c.*, COALESCE(p.avg_phase_econ_pctl, c.career_econ_pctl) AS phase_econ,
                COALESCE(p.avg_phase_dotball_pctl, c.career_dotball_pctl) AS phase_dotball,
                ROUND(LEAST(c.balls_bowled / 300.0, 1.0), 3) AS sample_size_factor
            FROM career c LEFT JOIN phase_avg p ON c.player_id = p.player_id
        ),
        scored AS (
            SELECT *,
                ROUND((career_econ_pctl + career_sr_pctl) / 2 * 0.3 + (phase_econ + phase_dotball) / 2 * 0.3 +
                    career_econ_pctl * 0.2 + career_sr_pctl * 0.1 + career_dotball_pctl * 0.1, 1) AS composite_score
            FROM combined
        )
        SELECT player_id, player_name, matches_bowled, balls_bowled, wickets,
            economy_rate, bowling_average, bowling_strike_rate,
            composite_score, ROUND(composite_score * sample_size_factor, 1) AS weighted_composite,
            RANK() OVER (ORDER BY composite_score * sample_size_factor DESC) AS overall_rank
        FROM scored
    """)

    print(f"  Year {year} views created.")


# =============================================================================
# QUERY FUNCTIONS — one per ranking category, parameterized by scope suffix
# =============================================================================


def query_batter_phase_rankings(conn: duckdb.DuckDBPyConnection, suffix: str = "") -> List[Dict]:
    """Category 1: Batter phase rankings (powerplay/middle/death)."""
    view = f"analytics_ipl_batter_phase_rankings{suffix}"
    subcategories = []
    for phase in PHASE_ORDER:
        rows = conn.execute(
            f"""
            SELECT
                phase_rank, player_name, runs, balls_faced, strike_rate,
                batting_average, boundary_pct, dot_ball_pct
            FROM {view}
            WHERE match_phase = ?
            ORDER BY phase_rank
            """,
            [phase],
        ).fetchall()

        subcategories.append(
            {
                "id": phase,
                "title": PHASE_TITLES[phase],
                "headers": [
                    "Rank",
                    "Player",
                    "Runs",
                    "Balls",
                    "SR",
                    "Avg",
                    "Boundary%",
                    "Dot%",
                ],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]) if r[2] is not None else 0,
                        int(r[3]),
                        _format_num(r[4]),
                        _format_num(r[5]),
                        _format_num(r[6]),
                        _format_num(r[7]),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    f"SELECT COUNT(*) FROM {view} WHERE match_phase = ?",
                    [phase],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_bowler_phase_rankings(conn: duckdb.DuckDBPyConnection, suffix: str = "") -> List[Dict]:
    """Category 2: Bowler phase rankings (powerplay/middle/death)."""
    view = f"analytics_ipl_bowler_phase_rankings{suffix}"
    subcategories = []
    for phase in PHASE_ORDER:
        rows = conn.execute(
            f"""
            SELECT
                phase_rank, player_name, balls_bowled, economy_rate,
                dot_ball_pct
            FROM {view}
            WHERE match_phase = ?
            ORDER BY phase_rank
            """,
            [phase],
        ).fetchall()

        subcategories.append(
            {
                "id": phase,
                "title": PHASE_TITLES[phase],
                "headers": ["Rank", "Player", "Balls", "Econ", "Dot%"],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]),
                        _format_num(r[3], 2),
                        _format_num(r[4]),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    f"SELECT COUNT(*) FROM {view} WHERE match_phase = ?",
                    [phase],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_batter_vs_bowling_type(conn: duckdb.DuckDBPyConnection, suffix: str = "") -> List[Dict]:
    """Category 3: Batter vs bowling type rankings."""
    view = f"analytics_ipl_batter_vs_bowling_type_rankings{suffix}"
    subcategories = []

    # Only include types present in the data
    available_types = [
        r[0]
        for r in conn.execute(
            f"SELECT DISTINCT bowler_type FROM {view} ORDER BY bowler_type"
        ).fetchall()
    ]

    # Use ordered list, filtered to available
    ordered_types = [t for t in BOWLING_TYPE_ORDER if t in available_types]
    # Add any types in data but not in our order list (safety net)
    ordered_types += [t for t in available_types if t not in ordered_types and t != "Unknown"]

    for btype in ordered_types:
        rows = conn.execute(
            f"""
            SELECT
                vs_type_rank, player_name, runs, balls, strike_rate,
                average
            FROM {view}
            WHERE bowler_type = ?
            ORDER BY vs_type_rank
            """,
            [btype],
        ).fetchall()

        if not rows:
            continue

        subcategories.append(
            {
                "id": btype.lower().replace(" ", "_").replace("-", "_"),
                "title": f"vs {btype}",
                "headers": ["Rank", "Player", "Runs", "Balls", "SR", "Avg"],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]),
                        int(r[3]),
                        _format_num(r[4]),
                        _format_num(r[5]),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    f"SELECT COUNT(*) FROM {view} WHERE bowler_type = ?",
                    [btype],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_bowler_vs_handedness(conn: duckdb.DuckDBPyConnection, suffix: str = "") -> List[Dict]:
    """Category 4: Bowler vs batter handedness rankings."""
    view = f"analytics_ipl_bowler_vs_handedness_rankings{suffix}"
    subcategories = []
    for hand in ["Left-hand", "Right-hand"]:
        rows = conn.execute(
            f"""
            SELECT
                vs_hand_rank, player_name, balls, wickets,
                economy
            FROM {view}
            WHERE batting_hand = ?
            ORDER BY vs_hand_rank
            """,
            [hand],
        ).fetchall()

        subcategories.append(
            {
                "id": hand.lower().replace("-", "_"),
                "title": HAND_TITLES[hand],
                "headers": [
                    "Rank",
                    "Player",
                    "Balls",
                    "Wkts",
                    "Econ",
                ],
                "rows": [
                    [
                        int(r[0]),
                        r[1],
                        int(r[2]),
                        int(r[3]),
                        _format_num(r[4], 2),
                    ]
                    for r in rows
                ],
                "qualifiedCount": conn.execute(
                    f"SELECT COUNT(*) FROM {view} WHERE batting_hand = ?",
                    [hand],
                ).fetchone()[0],
            }
        )

    return subcategories


def query_player_matchup_rankings(conn: duckdb.DuckDBPyConnection, suffix: str = "") -> List[Dict]:
    """Category 5: Player matchup rankings (batter-favored + bowler-favored)."""
    view = f"analytics_ipl_player_matchup_rankings{suffix}"
    # Batter-favored matchups (highest weighted dominance)
    batter_rows = conn.execute(
        f"""
        SELECT
            batter_name, bowler_name, balls, runs, dismissals,
            strike_rate, dominance_index, weighted_dominance
        FROM {view}
        ORDER BY weighted_dominance DESC
        """,
    ).fetchall()

    # Bowler-favored matchups (lowest weighted dominance)
    bowler_rows = conn.execute(
        f"""
        SELECT
            batter_name, bowler_name, balls, runs, dismissals,
            strike_rate, dominance_index, weighted_dominance
        FROM {view}
        ORDER BY weighted_dominance ASC
        """,
    ).fetchall()

    total_matchups = conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]

    return [
        {
            "id": "batter_favored",
            "title": "Batter-Favored Matchups",
            "description": "Matchups where the batter dominates (high SR, high avg, low dismissal rate)",
            "headers": [
                "Rank",
                "Batter",
                "Bowler",
                "Balls",
                "Runs",
                "Outs",
                "SR",
            ],
            "rows": [
                [
                    i + 1,
                    r[0],
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5]),
                ]
                for i, r in enumerate(batter_rows)
            ],
            "qualifiedCount": total_matchups,
        },
        {
            "id": "bowler_favored",
            "title": "Bowler-Favored Matchups",
            "description": "Matchups where the bowler dominates (low SR, frequent dismissals)",
            "headers": [
                "Rank",
                "Batter",
                "Bowler",
                "Balls",
                "Runs",
                "Outs",
                "SR",
            ],
            "rows": [
                [
                    i + 1,
                    r[0],
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5]),
                ]
                for i, r in enumerate(bowler_rows)
            ],
            "qualifiedCount": total_matchups,
        },
    ]


def query_batter_composite_rankings(
    conn: duckdb.DuckDBPyConnection, suffix: str = ""
) -> List[Dict]:
    """Category 6: Overall batter composite rankings."""
    view = f"analytics_ipl_batter_composite_rankings{suffix}"
    rows = conn.execute(
        f"""
        SELECT
            overall_rank, player_name, innings, runs, balls_faced,
            strike_rate, batting_average, boundary_pct
        FROM {view}
        ORDER BY overall_rank
        """,
    ).fetchall()

    total = conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]

    return [
        {
            "id": "overall",
            "title": "Overall Batter Rankings",
            "description": (
                "Composite score: Career SR+Avg (30%) + Phase Performance (30%) "
                "+ Boundary% (20%) + Average (10%) + Dot Ball Discipline (10%). "
                "Sample-size weighted. Min 500 balls."
            ),
            "headers": [
                "Rank",
                "Player",
                "Inn",
                "Runs",
                "Balls",
                "SR",
                "Avg",
                "Boundary%",
            ],
            "rows": [
                [
                    int(r[0]),
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5]),
                    _format_num(r[6]),
                    _format_num(r[7]),
                ]
                for r in rows
            ],
            "qualifiedCount": total,
        }
    ]


def query_bowler_composite_rankings(
    conn: duckdb.DuckDBPyConnection, suffix: str = ""
) -> List[Dict]:
    """Category 7: Overall bowler composite rankings."""
    view = f"analytics_ipl_bowler_composite_rankings{suffix}"
    rows = conn.execute(
        f"""
        SELECT
            overall_rank, player_name, balls_bowled, matches_bowled,
            wickets, economy_rate, bowling_average, bowling_strike_rate
        FROM {view}
        ORDER BY overall_rank
        """,
    ).fetchall()

    total = conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]

    return [
        {
            "id": "overall",
            "title": "Overall Bowler Rankings",
            "description": (
                "Composite score: Career Econ+Avg (30%) + Phase Performance (30%) "
                "+ Economy (20%) + Wicket-taking (10%) + Dot Ball% (10%). "
                "Sample-size weighted. Min 300 balls."
            ),
            "headers": [
                "Rank",
                "Player",
                "Balls",
                "Matches",
                "Wkts",
                "Econ",
                "Avg",
                "Bowl SR",
            ],
            "rows": [
                [
                    int(r[0]),
                    r[1],
                    int(r[2]),
                    int(r[3]),
                    int(r[4]),
                    _format_num(r[5], 2),
                    _format_num(r[6]),
                    _format_num(r[7]),
                ]
                for r in rows
            ],
            "qualifiedCount": total,
        }
    ]


# =============================================================================
# SCOPE BUILDER — queries all 7 categories for one scope
# =============================================================================

CATEGORY_DEFS = [
    {
        "id": "batter_phase",
        "title": "Batter Phase Rankings",
        "description": (
            "Phase-specific batter composites. Combines SR percentile (40%), "
            "Avg percentile (40%), and Boundary% percentile (20%). "
            "Sample-size weighted (target: 200 balls per phase)."
        ),
        "query_fn": "query_batter_phase_rankings",
        "stat_key": "batter_phase",
        "stat_mode": "sum",
    },
    {
        "id": "bowler_phase",
        "title": "Bowler Phase Rankings",
        "description": (
            "Phase-specific bowler composites. Combines Economy percentile (50%) "
            "and Dot Ball% percentile (50%). "
            "Sample-size weighted (target: 120 balls per phase)."
        ),
        "query_fn": "query_bowler_phase_rankings",
        "stat_key": "bowler_phase",
        "stat_mode": "sum",
    },
    {
        "id": "batter_vs_bowling_type",
        "title": "Batter vs Bowling Type",
        "description": (
            "How batters perform against each bowling classification. "
            "Composite: SR (40%) + Avg (40%) + Survival Rate (20%). "
            "Min 50 balls. Sample-size weighted (target: 100 balls)."
        ),
        "query_fn": "query_batter_vs_bowling_type",
        "stat_key": "batter_vs_bowling_type",
        "stat_mode": "sum",
    },
    {
        "id": "bowler_vs_handedness",
        "title": "Bowler vs Batter Handedness",
        "description": (
            "Bowler effectiveness against left-hand and right-hand batters. "
            "Composite: Economy percentile (50%) + SR percentile (50%). "
            "Min 50 balls. Sample-size weighted (target: 100 balls)."
        ),
        "query_fn": "query_bowler_vs_handedness",
        "stat_key": "bowler_vs_handedness",
        "stat_mode": "sum",
    },
    {
        "id": "player_matchups",
        "title": "Player Matchup Rankings",
        "description": (
            "Head-to-head dominance index. Positive = batter-favored, "
            "negative = bowler-favored. Factors: SR deviation (50%), "
            "Avg deviation (30%), Boundary% deviation (20%). "
            "Min 12 balls. Sample-size weighted (target: 50 balls)."
        ),
        "query_fn": "query_player_matchup_rankings",
        "stat_key": "player_matchups",
        "stat_mode": "first",
    },
    {
        "id": "batter_composite",
        "title": "Overall Batter Rankings",
        "description_from_sub": True,
        "query_fn": "query_batter_composite_rankings",
        "stat_key": "batter_composite",
        "stat_mode": "first",
    },
    {
        "id": "bowler_composite",
        "title": "Overall Bowler Rankings",
        "description_from_sub": True,
        "query_fn": "query_bowler_composite_rankings",
        "stat_key": "bowler_composite",
        "stat_mode": "first",
    },
]

# Map query function names to actual functions
QUERY_FNS = {
    "query_batter_phase_rankings": query_batter_phase_rankings,
    "query_bowler_phase_rankings": query_bowler_phase_rankings,
    "query_batter_vs_bowling_type": query_batter_vs_bowling_type,
    "query_bowler_vs_handedness": query_bowler_vs_handedness,
    "query_player_matchup_rankings": query_player_matchup_rankings,
    "query_batter_composite_rankings": query_batter_composite_rankings,
    "query_bowler_composite_rankings": query_bowler_composite_rankings,
}


def build_scope_data(conn: duckdb.DuckDBPyConnection, scope_key: str) -> Dict[str, Any]:
    """Query all 7 categories for a given scope and return categories + stats."""
    suffix = SCOPES[scope_key]["suffix"]
    label = SCOPES[scope_key]["label"]

    categories = []
    stats: Dict[str, int] = {}

    for i, cat_def in enumerate(CATEGORY_DEFS, 1):
        print(f"  [{i}/7] {cat_def['title']}...")
        query_fn = QUERY_FNS[cat_def["query_fn"]]
        subs = query_fn(conn, suffix)

        # Compute stat
        if cat_def["stat_mode"] == "sum":
            stat_val = sum(s["qualifiedCount"] for s in subs)
        else:
            stat_val = subs[0]["qualifiedCount"] if subs else 0

        # Build category entry
        description = (
            subs[0].get("description", cat_def.get("title", ""))
            if cat_def.get("description_from_sub")
            else cat_def.get("description", "")
        )

        categories.append(
            {
                "id": cat_def["id"],
                "title": cat_def["title"],
                "description": description,
                "subcategories": subs,
            }
        )
        stats[cat_def["stat_key"]] = stat_val
        print(f"    {stat_val} qualified entries")

    return {
        "categories": categories,
        "stats": stats,
        "dataWindow": label,
    }


# =============================================================================
# MAIN GENERATOR
# =============================================================================


def generate_rankings() -> Dict[str, Any]:
    """Query all 7 ranking categories for both scopes and build the full data structure."""
    print("=" * 60)
    print("  RANKING GENERATOR (TKT-236 / EPIC-021)")
    print("  Dual-scope: alltime + since2023")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    # Open read-write to support TEMP VIEW creation for per-year scopes
    conn = duckdb.connect(str(DB_PATH), read_only=False)

    try:
        # Build alltime scope
        print("\n--- SCOPE: All-Time (IPL 2008-2025) ---")
        alltime_data = build_scope_data(conn, "alltime")

        # Build since2023 scope
        print("\n--- SCOPE: Since 2023 (IPL 2023-2025) ---")
        since2023_data = build_scope_data(conn, "since2023")

        # Build per-year scopes
        year_data = {}
        for year in [2023, 2024, 2025]:
            year_key = str(year)
            print(f"\n--- SCOPE: IPL {year} ---")
            create_year_views(conn, year)
            year_data[year_key] = build_scope_data(conn, year_key)

        # Build final data structure
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        scope_labels = {k: v["label"] for k, v in SCOPES.items()}
        rankings_data = {
            "alltime": {
                "categories": alltime_data["categories"],
                "stats": alltime_data["stats"],
            },
            "since2023": {
                "categories": since2023_data["categories"],
                "stats": since2023_data["stats"],
            },
        }
        for year_key, yd in year_data.items():
            rankings_data[year_key] = {
                "categories": yd["categories"],
                "stats": yd["stats"],
            }

        rankings_data["metadata"] = {
            "generated": now,
            "scopes": scope_labels,
            "defaultScope": "since2023",
            "categoriesPerScope": len(CATEGORY_DEFS),
            "ticket": "TKT-236",
            "epic": "EPIC-021",
        }

        return rankings_data

    finally:
        conn.close()


def write_js_output(data: Dict[str, Any]) -> None:
    """Write the rankings data as a JavaScript file for The Lab dashboard."""
    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)

    # Serialize to JSON with readable formatting
    json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)

    js_content = (
        "/**\n"
        " * The Lab - Player Rankings Data (Dual-Scope)\n"
        " * IPL Pre-Season Analytics (EPIC-021 Signature Feature)\n"
        f" * Auto-generated: {data['metadata']['generated']}\n"
        " * Generator: scripts/generators/generate_rankings.py (TKT-236)\n"
        " *\n"
        f" * Categories per scope: {data['metadata']['categoriesPerScope']}\n"
        " * Scopes: alltime (2008-2025), since2023 (2023-2025)\n"
        " * Composite methodology: see config/thresholds.yaml > rankings\n"
        " */\n"
        "\n"
        f"const RANKINGS_DATA = {json_str};\n"
    )

    OUTPUT_JS.write_text(js_content, encoding="utf-8")
    size_kb = OUTPUT_JS.stat().st_size / 1024
    print(f"\nOutput written to: {OUTPUT_JS}")
    print(f"  Size: {size_kb:.1f} KB")


def print_summary(data: Dict[str, Any]) -> None:
    """Print a summary of generated rankings for verification."""
    print("\n" + "=" * 60)
    print("  RANKINGS SUMMARY")
    print("=" * 60)

    for scope_key in ["alltime", "since2023"]:
        scope_data = data[scope_key]
        label = data["metadata"]["scopes"][scope_key]
        print(f"\n{'=' * 40}")
        print(f"  SCOPE: {label}")
        print(f"{'=' * 40}")

        for cat in scope_data["categories"]:
            print(f"\n--- {cat['title']} ---")
            for sub in cat["subcategories"]:
                rows = sub["rows"]
                qualified = sub.get("qualifiedCount", len(rows))
                top3 = ", ".join(str(r[1]) if len(r) > 1 else "?" for r in rows[:3])
                print(f"  {sub['title']}: {qualified} qualified | Top 3: {top3}")

    print("\n" + "=" * 60)
    print(f"  Categories per scope: {data['metadata']['categoriesPerScope']}")
    print(f"  Generated: {data['metadata']['generated']}")
    print("=" * 60)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    rankings = generate_rankings()
    write_js_output(rankings)
    print_summary(rankings)
    print("\nDone.")
