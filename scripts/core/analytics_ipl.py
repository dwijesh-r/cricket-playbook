"""
Cricket Playbook - IPL 2026 Analytics Layer
============================================
Author: Stephen Curry (Analytics Specialist)
Version: 2.0.0

Creates IPL-specific analytical views with phase-wise breakdown,
bowler matchups, and comparison with All T20 data.

New Views Created:
- IPL-specific career views (filtered to IPL data only)
- Phase-wise batting/bowling breakdown
- Batter vs bowler type analysis
- All T20 comparison views
- Squad integration views for IPL 2026
"""

from pathlib import Path

import duckdb

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DATA_DIR / "cricket_playbook.duckdb"
SQUADS_CSV = DATA_DIR / "ipl_2026_squads.csv"
CONTRACTS_CSV = DATA_DIR / "ipl_2026_player_contracts.csv"

# Data filter - only use recent IPL seasons (2023 onwards)
# This accounts for drift in stats due to evolution of the game
IPL_MIN_DATE = "2023-01-01"  # IPL 2023, 2024, 2025


def create_squad_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Load IPL 2026 squad data into tables."""

    print("Loading IPL 2026 squad data...")

    # Load squads CSV
    if SQUADS_CSV.exists():
        conn.execute(f"""
            CREATE OR REPLACE TABLE ipl_2026_squads AS
            SELECT * FROM read_csv('{SQUADS_CSV}',
                header=true,
                strict_mode=false,
                ignore_errors=true,
                null_padding=true,
                delim=',')
        """)
        print("  - ipl_2026_squads table created")

        # Add bowling_style column with standardized categories
        conn.execute("""
            ALTER TABLE ipl_2026_squads ADD COLUMN IF NOT EXISTS bowling_style VARCHAR
        """)
        conn.execute("""
            UPDATE ipl_2026_squads
            SET bowling_style = CASE
                WHEN bowling_arm = 'Right-arm' AND bowling_type IN ('Fast', 'Medium') THEN 'Right-arm pace'
                WHEN bowling_arm = 'Left-arm' AND bowling_type IN ('Fast', 'Medium') THEN 'Left-arm pace'
                WHEN bowling_type = 'Off-spin' THEN 'Right-arm off-spin'
                WHEN bowling_type = 'Leg-spin' THEN 'Right-arm leg-spin'
                WHEN bowling_type = 'Left-arm orthodox' THEN 'Left-arm orthodox'
                WHEN bowling_type = 'Left-arm wrist spin' THEN 'Left-arm wrist spin'
                ELSE bowling_type
            END
        """)
        print("  - bowling_style column added")
    else:
        print(f"  WARNING: {SQUADS_CSV} not found")

    # Load contracts CSV
    if CONTRACTS_CSV.exists():
        conn.execute(f"""
            CREATE OR REPLACE TABLE ipl_2026_contracts AS
            SELECT * FROM read_csv('{CONTRACTS_CSV}',
                header=true,
                strict_mode=false,
                ignore_errors=true,
                null_padding=true,
                delim=',')
        """)
        print("  - ipl_2026_contracts table created")
    else:
        print(f"  WARNING: {CONTRACTS_CSV} not found")


def create_ipl_batting_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create IPL-specific batting analytics views."""

    print("\nCreating IPL-specific batting views...")

    # IPL Career Batting Stats
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batting_career AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        batting_stats AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(DISTINCT fb.match_id) as innings,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
                SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) as dot_balls
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.batter_id
        ),
        innings_scores AS (
            SELECT
                fb.batter_id as player_id,
                fb.match_id,
                SUM(fb.batter_runs) as innings_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.batter_id, fb.match_id
        ),
        high_scores AS (
            SELECT
                player_id,
                MAX(innings_runs) as highest_score,
                SUM(CASE WHEN innings_runs >= 50 THEN 1 ELSE 0 END) as fifties,
                SUM(CASE WHEN innings_runs >= 100 THEN 1 ELSE 0 END) as hundreds
            FROM innings_scores
            GROUP BY player_id
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dp.primary_role,
            bs.innings,
            bs.runs,
            bs.balls_faced,
            bs.dismissals,
            hs.highest_score,
            hs.fifties,
            hs.hundreds,
            bs.fours,
            bs.sixes,
            bs.dot_balls,
            ROUND(bs.runs * 100.0 / NULLIF(bs.balls_faced, 0), 2) as strike_rate,
            ROUND(bs.runs * 1.0 / NULLIF(bs.dismissals, 0), 2) as batting_average,
            ROUND((bs.fours + bs.sixes) * 100.0 / NULLIF(bs.balls_faced, 0), 2) as boundary_pct,
            ROUND(bs.dot_balls * 100.0 / NULLIF(bs.balls_faced, 0), 2) as dot_ball_pct,
            CASE WHEN bs.innings < 10 THEN 'LOW'
                 WHEN bs.innings < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM batting_stats bs
        JOIN dim_player dp ON bs.player_id = dp.player_id
        JOIN high_scores hs ON bs.player_id = hs.player_id
    """)
    print("  - analytics_ipl_batting_career")

    # IPL Batting by Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
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
    print("  - analytics_ipl_batter_phase")

    # IPL Batter vs Bowler (head-to-head)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 10 THEN 'LOW'
                 WHEN COUNT(*) < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, dp_bowl.player_id, dp_bowl.current_name
    """)
    print("  - analytics_ipl_batter_vs_bowler")

    # IPL Batter vs Bowler Type (using bowling_style from squads + dim_bowler_classification)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_type AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 50 THEN 'LOW'
                 WHEN COUNT(*) < 200 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
    """)
    print("  - analytics_ipl_batter_vs_bowler_type")


def create_ipl_bowling_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create IPL-specific bowling analytics views."""

    print("\nCreating IPL-specific bowling views...")

    # IPL Career Bowling Stats
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_career AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        bowling_stats AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(DISTINCT fb.match_id) as matches_bowled,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
                SUM(fb.total_runs) as runs_conceded,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.bowler_id
        ),
        best_figures AS (
            SELECT
                fb.bowler_id as player_id,
                fb.match_id,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as match_wickets,
                SUM(fb.total_runs) as match_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.bowler_id, fb.match_id
        ),
        best_bowling AS (
            SELECT
                player_id,
                MAX(match_wickets) as best_wickets,
                FIRST(match_runs ORDER BY match_wickets DESC, match_runs ASC) as best_runs
            FROM best_figures
            GROUP BY player_id
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dp.primary_role,
            bs.matches_bowled,
            bs.balls_bowled,
            ROUND(bs.balls_bowled / 6.0, 1) as overs_bowled,
            bs.runs_conceded,
            bs.wickets,
            bb.best_wickets,
            bb.best_runs,
            bs.dot_balls,
            bs.fours_conceded,
            bs.sixes_conceded,
            ROUND(bs.runs_conceded * 6.0 / NULLIF(bs.balls_bowled, 0), 2) as economy_rate,
            ROUND(bs.runs_conceded * 1.0 / NULLIF(bs.wickets, 0), 2) as bowling_average,
            ROUND(bs.balls_bowled * 1.0 / NULLIF(bs.wickets, 0), 2) as bowling_strike_rate,
            ROUND(bs.dot_balls * 100.0 / NULLIF(bs.balls_bowled, 0), 2) as dot_ball_pct,
            ROUND((bs.fours_conceded + bs.sixes_conceded) * 100.0 / NULLIF(bs.balls_bowled, 0), 2) as boundary_conceded_pct,
            CASE WHEN bs.matches_bowled < 10 THEN 'LOW'
                 WHEN bs.matches_bowled < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM bowling_stats bs
        JOIN dim_player dp ON bs.player_id = dp.player_id
        JOIN best_bowling bb ON bs.player_id = bb.player_id
    """)
    print("  - analytics_ipl_bowling_career")

    # IPL Bowling by Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) as overs,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_conceded_pct,
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 100 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)
    print("  - analytics_ipl_bowler_phase")

    # IPL Bowler vs Batter Handedness (uses ipl_2026_squads for batting_hand)
    # Note: This covers ~80% of balls in 2023+ IPL data
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_batter_handedness AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            sq.batting_hand,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
            SUM(fb.batter_runs + fb.extra_runs) as runs,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as economy,
            ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_pct,
            -- Wickets per ball ratio (used for wicket-taker tags instead of raw wicket count)
            ROUND(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 4) as wickets_per_ball,
            CASE WHEN COUNT(*) FILTER (WHERE fb.is_legal_ball) < 60 THEN 'LOW'
                 WHEN COUNT(*) FILTER (WHERE fb.is_legal_ball) < 200 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        JOIN ipl_2026_squads sq ON fb.batter_id = sq.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
          AND sq.batting_hand IS NOT NULL
        GROUP BY dp_bowl.player_id, dp_bowl.current_name, sq.batting_hand
    """)
    print("  - analytics_ipl_bowler_vs_batter_handedness")


def create_phase_matchup_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create phase-wise batter vs bowler matchup views."""

    print("\nCreating phase-wise matchup views...")

    # IPL Batter vs Bowler by Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            fb.match_phase,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 6 THEN 'LOW'
                 WHEN COUNT(*) < 20 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, dp_bowl.player_id, dp_bowl.current_name, fb.match_phase
    """)
    print("  - analytics_ipl_batter_vs_bowler_phase")

    # IPL Batter vs Bowler Type by Phase (using bowling_style)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_type_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            fb.match_phase,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown'), fb.match_phase
    """)
    print("  - analytics_ipl_batter_vs_bowler_type_phase")

    # IPL Bowler vs Batter by Phase (bowler's perspective)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_batter_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            fb.match_phase,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 6 THEN 'LOW'
                 WHEN COUNT(*) < 20 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bowl.player_id, dp_bowl.current_name, dp_bat.player_id, dp_bat.current_name, fb.match_phase
    """)
    print("  - analytics_ipl_bowler_vs_batter_phase")


def create_team_venue_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create batter/bowler vs team and venue breakdown views."""

    print("\nCreating team and venue breakdown views...")

    # =========================================================================
    # BATTER VS TEAM VIEWS
    # =========================================================================

    # IPL Batter vs Team (aggregate) - uses franchise aliases
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_team AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_team dt_opp ON fb.bowling_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name)
    """)
    print("  - analytics_ipl_batter_vs_team")

    # IPL Batter vs Team by Phase - uses franchise aliases
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_team_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_team dt_opp ON fb.bowling_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name), fb.match_phase
    """)
    print("  - analytics_ipl_batter_vs_team_phase")

    # =========================================================================
    # BATTER VENUE VIEWS
    # =========================================================================

    # IPL Batter by Venue
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_venue AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            im.venue,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue
    """)
    print("  - analytics_ipl_batter_venue")

    # IPL Batter by Venue by Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_venue_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            im.venue,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue, fb.match_phase
    """)
    print("  - analytics_ipl_batter_venue_phase")

    # =========================================================================
    # BOWLER VS TEAM VIEWS
    # =========================================================================

    # IPL Bowler vs Team (aggregate) - uses franchise aliases
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_team AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN dim_team dt_opp ON fb.batting_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name)
    """)
    print("  - analytics_ipl_bowler_vs_team")

    # IPL Bowler vs Team by Phase - uses franchise aliases
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_team_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN dim_team dt_opp ON fb.batting_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name), fb.match_phase
    """)
    print("  - analytics_ipl_bowler_vs_team_phase")

    # =========================================================================
    # BOWLER VENUE VIEWS
    # =========================================================================

    # IPL Bowler by Venue
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_venue AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            im.venue,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue
    """)
    print("  - analytics_ipl_bowler_venue")

    # IPL Bowler by Venue by Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_venue_phase AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            im.venue,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue, fb.match_phase
    """)
    print("  - analytics_ipl_bowler_venue_phase")

    # =========================================================================
    # BOWLER PHASE DISTRIBUTION
    # =========================================================================

    # IPL Bowler Phase Distribution - % of overs and wickets in each phase
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_distribution AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        ),
        bowler_phase_stats AS (
            SELECT
                dp.player_id as bowler_id,
                dp.current_name as bowler_name,
                fb.match_phase,
                COUNT(*) as balls,
                SUM(fb.total_runs) as runs_conceded,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls
            FROM fact_ball fb
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE fb.is_legal_ball = TRUE
              AND fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY dp.player_id, dp.current_name, fb.match_phase
        ),
        bowler_totals AS (
            SELECT
                bowler_id,
                bowler_name,
                SUM(balls) as total_balls,
                SUM(wickets) as total_wickets
            FROM bowler_phase_stats
            GROUP BY bowler_id, bowler_name
        )
        SELECT
            bps.bowler_id,
            bps.bowler_name,
            bps.match_phase,
            bps.balls,
            ROUND(bps.balls / 6.0, 1) as overs,
            bps.runs_conceded,
            bps.wickets,
            bps.dot_balls,
            ROUND(bps.runs_conceded * 6.0 / NULLIF(bps.balls, 0), 2) as economy,
            ROUND(bps.dot_balls * 100.0 / NULLIF(bps.balls, 0), 2) as dot_ball_pct,
            -- Distribution percentages
            ROUND(bps.balls * 100.0 / NULLIF(bt.total_balls, 0), 1) as pct_overs_in_phase,
            ROUND(bps.wickets * 100.0 / NULLIF(bt.total_wickets, 0), 1) as pct_wickets_in_phase,
            -- Wicket efficiency: if pct_wickets > pct_overs, bowler is more effective in this phase
            ROUND(
                (bps.wickets * 100.0 / NULLIF(bt.total_wickets, 0)) -
                (bps.balls * 100.0 / NULLIF(bt.total_balls, 0)), 1
            ) as wicket_efficiency,
            bt.total_balls,
            bt.total_wickets,
            CASE WHEN bt.total_balls < 120 THEN 'LOW'
                 WHEN bt.total_balls < 300 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM bowler_phase_stats bps
        JOIN bowler_totals bt ON bps.bowler_id = bt.bowler_id
        ORDER BY bps.bowler_name,
            CASE bps.match_phase
                WHEN 'powerplay' THEN 1
                WHEN 'middle' THEN 2
                WHEN 'death' THEN 3
            END
    """)
    print("  - analytics_ipl_bowler_phase_distribution")


def create_t20_comparison_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create All T20 comparison views (across all tournaments)."""

    print("\nCreating All T20 comparison views...")

    # All T20 Batter Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_t20_batter_phase AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
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
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)
    print("  - analytics_t20_batter_phase")

    # All T20 Batter vs Bowler Type (using bowling_style)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_t20_batter_vs_bowler_type AS
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 50 THEN 'LOW'
                 WHEN COUNT(*) < 200 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
    """)
    print("  - analytics_t20_batter_vs_bowler_type")

    # All T20 Bowler Phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_t20_bowler_phase AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) as overs,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_conceded_pct,
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 100 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)
    print("  - analytics_t20_bowler_phase")


def create_squad_integration_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create views that integrate IPL 2026 squad data with analytics."""

    print("\nCreating squad integration views...")

    # Squad Batting Analysis
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_batting AS
        SELECT
            sq.team_name,
            sq.player_name,
            sq.role,
            sq.batting_hand,
            ct.price_cr,
            ct.acquisition_type,
            ct.year_joined,
            ipl.innings as ipl_innings,
            ipl.runs as ipl_runs,
            ipl.balls_faced as ipl_balls,
            ipl.strike_rate as ipl_sr,
            ipl.batting_average as ipl_avg,
            ipl.boundary_pct as ipl_boundary_pct,
            ipl.dot_ball_pct as ipl_dot_pct,
            ipl.fifties as ipl_fifties,
            ipl.hundreds as ipl_hundreds,
            ipl.sample_size as ipl_sample_size,
            t20.innings as t20_innings,
            t20.runs as t20_runs,
            t20.strike_rate as t20_sr,
            t20.batting_average as t20_avg,
            t20.sample_size_innings as t20_sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_batting_career ipl ON sq.player_id = ipl.player_id
        LEFT JOIN analytics_batting_career t20 ON sq.player_id = t20.player_id
        WHERE sq.role IN ('Batter', 'Wicketkeeper', 'All-rounder')
        ORDER BY sq.team_name, COALESCE(ct.price_cr, 0) DESC
    """)
    print("  - analytics_ipl_squad_batting")

    # Squad Bowling Analysis
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_bowling AS
        SELECT
            sq.team_name,
            sq.player_name,
            sq.role,
            sq.bowling_arm,
            sq.bowling_type,
            ct.price_cr,
            ct.acquisition_type,
            ct.year_joined,
            ipl.matches_bowled as ipl_matches,
            ipl.overs_bowled as ipl_overs,
            ipl.wickets as ipl_wickets,
            ipl.economy_rate as ipl_economy,
            ipl.bowling_average as ipl_avg,
            ipl.bowling_strike_rate as ipl_sr,
            ipl.dot_ball_pct as ipl_dot_pct,
            ipl.boundary_conceded_pct as ipl_boundary_pct,
            ipl.sample_size as ipl_sample_size,
            t20.matches_bowled as t20_matches,
            t20.wickets as t20_wickets,
            t20.economy_rate as t20_economy,
            t20.bowling_average as t20_avg,
            t20.sample_size_matches as t20_sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_bowling_career ipl ON sq.player_id = ipl.player_id
        LEFT JOIN analytics_bowling_career t20 ON sq.player_id = t20.player_id
        WHERE sq.role IN ('Bowler', 'All-rounder')
        ORDER BY sq.team_name, COALESCE(ct.price_cr, 0) DESC
    """)
    print("  - analytics_ipl_squad_bowling")

    # Squad Phase-wise Batting
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_batting_phase AS
        SELECT
            sq.team_name,
            sq.player_name,
            sq.role,
            ct.price_cr,
            bp.match_phase,
            bp.innings,
            bp.runs,
            bp.balls_faced,
            bp.strike_rate,
            bp.batting_average,
            bp.boundary_pct,
            bp.dot_ball_pct,
            bp.sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_batter_phase bp ON sq.player_id = bp.player_id
        WHERE sq.role IN ('Batter', 'Wicketkeeper', 'All-rounder')
        ORDER BY sq.team_name, sq.player_name, bp.match_phase
    """)
    print("  - analytics_ipl_squad_batting_phase")

    # Squad Phase-wise Bowling
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_bowling_phase AS
        SELECT
            sq.team_name,
            sq.player_name,
            sq.role,
            sq.bowling_type,
            ct.price_cr,
            bp.match_phase,
            bp.matches,
            bp.overs,
            bp.wickets,
            bp.economy_rate,
            bp.bowling_average,
            bp.dot_ball_pct,
            bp.boundary_conceded_pct,
            bp.sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_bowler_phase bp ON sq.player_id = bp.player_id
        WHERE sq.role IN ('Bowler', 'All-rounder')
        ORDER BY sq.team_name, sq.player_name, bp.match_phase
    """)
    print("  - analytics_ipl_squad_bowling_phase")

    # Team comparison view with contracts
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_team_roster AS
        SELECT
            sq.team_name,
            sq.player_name,
            sq.role,
            sq.bowling_type,
            sq.batting_hand,
            ct.price_cr,
            ct.acquisition_type,
            ct.year_joined,
            CASE
                WHEN sq.role = 'Batter' THEN 'Batting'
                WHEN sq.role = 'Bowler' THEN 'Bowling'
                WHEN sq.role = 'All-rounder' THEN 'All-round'
                WHEN sq.role = 'Wicketkeeper' THEN 'Batting'
                ELSE 'Other'
            END as primary_skill
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        ORDER BY sq.team_name, COALESCE(ct.price_cr, 0) DESC
    """)
    print("  - analytics_ipl_team_roster")

    # ── Dual-scope variants for squad views (TKT-181) ────────────────
    # Base views already use 2023+ career stats. Create explicit _since2023
    # aliases and _alltime variants joining against alltime career views.

    # _since2023 aliases (base views are already 2023+)
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_squad_batting_since2023 AS SELECT * FROM analytics_ipl_squad_batting"
    )
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_squad_bowling_since2023 AS SELECT * FROM analytics_ipl_squad_bowling"
    )
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_squad_batting_phase_since2023 AS SELECT * FROM analytics_ipl_squad_batting_phase"
    )
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_squad_bowling_phase_since2023 AS SELECT * FROM analytics_ipl_squad_bowling_phase"
    )
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_team_roster_since2023 AS SELECT * FROM analytics_ipl_team_roster"
    )

    # _alltime variants (join against alltime career views)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_batting_alltime AS
        SELECT
            sq.team_name, sq.player_name, sq.role, sq.batting_hand,
            ct.price_cr, ct.acquisition_type, ct.year_joined,
            ipl.innings as ipl_innings, ipl.runs as ipl_runs,
            ipl.balls_faced as ipl_balls, ipl.strike_rate as ipl_sr,
            ipl.batting_average as ipl_avg, ipl.boundary_pct as ipl_boundary_pct,
            ipl.dot_ball_pct as ipl_dot_pct, ipl.fifties as ipl_fifties,
            ipl.hundreds as ipl_hundreds, ipl.sample_size as ipl_sample_size,
            t20.innings as t20_innings, t20.runs as t20_runs,
            t20.strike_rate as t20_sr, t20.batting_average as t20_avg,
            t20.sample_size_innings as t20_sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_batting_career_alltime ipl ON sq.player_id = ipl.player_id
        LEFT JOIN analytics_batting_career t20 ON sq.player_id = t20.player_id
        WHERE sq.role IN ('Batter', 'Wicketkeeper', 'All-rounder')
        ORDER BY sq.team_name, COALESCE(ct.price_cr, 0) DESC
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_bowling_alltime AS
        SELECT
            sq.team_name, sq.player_name, sq.role, sq.bowling_arm, sq.bowling_type,
            ct.price_cr, ct.acquisition_type, ct.year_joined,
            ipl.matches_bowled as ipl_matches, ipl.overs_bowled as ipl_overs,
            ipl.wickets as ipl_wickets, ipl.economy_rate as ipl_economy,
            ipl.bowling_average as ipl_avg, ipl.bowling_strike_rate as ipl_sr,
            ipl.dot_ball_pct as ipl_dot_pct, ipl.boundary_conceded_pct as ipl_boundary_pct,
            ipl.sample_size as ipl_sample_size,
            t20.matches_bowled as t20_matches, t20.wickets as t20_wickets,
            t20.economy_rate as t20_economy, t20.bowling_average as t20_avg,
            t20.sample_size_matches as t20_sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_bowling_career_alltime ipl ON sq.player_id = ipl.player_id
        LEFT JOIN analytics_bowling_career t20 ON sq.player_id = t20.player_id
        WHERE sq.role IN ('Bowler', 'All-rounder')
        ORDER BY sq.team_name, COALESCE(ct.price_cr, 0) DESC
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_batting_phase_alltime AS
        SELECT
            sq.team_name, sq.player_name, sq.role, ct.price_cr,
            bp.match_phase, bp.innings, bp.runs, bp.balls_faced,
            bp.strike_rate, bp.batting_average, bp.boundary_pct,
            bp.dot_ball_pct, bp.sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_batter_phase_alltime bp ON sq.player_id = bp.player_id
        WHERE sq.role IN ('Batter', 'Wicketkeeper', 'All-rounder')
        ORDER BY sq.team_name, sq.player_name, bp.match_phase
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_squad_bowling_phase_alltime AS
        SELECT
            sq.team_name, sq.player_name, sq.role, sq.bowling_type, ct.price_cr,
            bp.match_phase, bp.matches, bp.overs, bp.wickets,
            bp.economy_rate, bp.bowling_average, bp.dot_ball_pct,
            bp.boundary_conceded_pct, bp.sample_size
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_2026_contracts ct ON sq.team_name = ct.team_name AND sq.player_name = ct.player_name
        LEFT JOIN analytics_ipl_bowler_phase_alltime bp ON sq.player_id = bp.player_id
        WHERE sq.role IN ('Bowler', 'All-rounder')
        ORDER BY sq.team_name, sq.player_name, bp.match_phase
    """)
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_team_roster_alltime AS SELECT * FROM analytics_ipl_team_roster"
    )
    print("  - squad views: 5 x 2 dual-scope variants (10 views)")


def create_percentile_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create views with percentile rankings for key metrics."""

    print("\nCreating percentile ranking views...")

    # IPL Batting Career with Percentiles (minimum 500 balls for ranking)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batting_percentiles AS
        WITH qualified_batters AS (
            SELECT *
            FROM analytics_ipl_batting_career
            WHERE balls_faced >= 500
        )
        SELECT
            player_id,
            player_name,
            innings,
            runs,
            balls_faced,
            strike_rate,
            batting_average,
            boundary_pct,
            dot_ball_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY boundary_pct) * 100, 1) as boundary_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY dot_ball_pct DESC) * 100, 1) as dot_ball_percentile
        FROM qualified_batters
    """)
    print("  - analytics_ipl_batting_percentiles")

    # IPL Bowling Career with Percentiles (minimum 300 balls for ranking)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_percentiles AS
        WITH qualified_bowlers AS (
            SELECT *
            FROM analytics_ipl_bowling_career
            WHERE balls_bowled >= 300
        )
        SELECT
            player_id,
            player_name,
            matches_bowled,
            balls_bowled,
            overs_bowled,
            wickets,
            economy_rate,
            bowling_average,
            bowling_strike_rate,
            dot_ball_pct,
            boundary_conceded_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY bowling_average DESC) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY bowling_strike_rate DESC) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM qualified_bowlers
    """)
    print("  - analytics_ipl_bowling_percentiles")

    # Phase-wise batting percentiles
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_phase_percentiles AS
        WITH qualified AS (
            SELECT *
            FROM analytics_ipl_batter_phase
            WHERE balls_faced >= 100
        )
        SELECT
            player_id,
            player_name,
            match_phase,
            innings,
            runs,
            balls_faced,
            strike_rate,
            batting_average,
            boundary_pct,
            dot_ball_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY boundary_pct) * 100, 1) as boundary_percentile
        FROM qualified
    """)
    print("  - analytics_ipl_batter_phase_percentiles")

    # Phase-wise bowling percentiles
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_percentiles AS
        WITH qualified AS (
            SELECT *
            FROM analytics_ipl_bowler_phase
            WHERE balls_bowled >= 60
        )
        SELECT
            player_id,
            player_name,
            match_phase,
            matches,
            balls_bowled,
            overs,
            wickets,
            economy_rate,
            bowling_average,
            dot_ball_pct,
            boundary_conceded_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM qualified
    """)
    print("  - analytics_ipl_bowler_phase_percentiles")


def create_benchmark_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create IPL-wide benchmark/average views for comparison."""

    print("\nCreating IPL benchmark views...")

    # IPL-wide batting averages by phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batting_benchmarks AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.batter_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as total_balls,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as total_wickets,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_batting_avg,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_dot_ball_pct
        FROM fact_ball fb
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.match_phase
    """)
    print("  - analytics_ipl_batting_benchmarks")

    # IPL-wide bowling averages by phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_benchmarks AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.total_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as total_balls,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as total_wickets,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_economy,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_bowling_avg,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_bowling_sr,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_dot_ball_pct
        FROM fact_ball fb
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.match_phase
    """)
    print("  - analytics_ipl_bowling_benchmarks")

    # Batting vs Bowler Type benchmarks
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_vs_bowler_type_benchmarks AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            COUNT(*) as total_balls,
            SUM(fb.batter_runs) as total_runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as total_dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as avg_strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as avg_batting_avg,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as avg_boundary_pct
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
          AND fb.is_legal_ball = TRUE
        GROUP BY COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
    """)
    print("  - analytics_ipl_vs_bowler_type_benchmarks")

    # Overall IPL career benchmarks (qualified players only)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_career_benchmarks AS
        SELECT
            'batting' as category,
            COUNT(*) as qualified_players,
            ROUND(AVG(strike_rate), 2) as avg_strike_rate,
            ROUND(AVG(batting_average), 2) as avg_batting_avg,
            ROUND(AVG(boundary_pct), 2) as avg_boundary_pct,
            ROUND(AVG(dot_ball_pct), 2) as avg_dot_ball_pct,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY strike_rate), 2) as median_strike_rate,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY batting_average), 2) as median_batting_avg
        FROM analytics_ipl_batting_career
        WHERE balls_faced >= 500
        UNION ALL
        SELECT
            'bowling' as category,
            COUNT(*) as qualified_players,
            ROUND(AVG(economy_rate), 2) as avg_economy,
            ROUND(AVG(bowling_average), 2) as avg_bowling_avg,
            ROUND(AVG(dot_ball_pct), 2) as avg_dot_ball_pct,
            ROUND(AVG(boundary_conceded_pct), 2) as avg_boundary_pct,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY economy_rate), 2) as median_economy,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bowling_average), 2) as median_bowling_avg
        FROM analytics_ipl_bowling_career
        WHERE balls_bowled >= 300
    """)
    print("  - analytics_ipl_career_benchmarks")


def create_standardized_ipl_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create standardized dual-scope views for the Film Room.

    For every existing IPL analytics view (prefix analytics_ipl_), create:
      - VIEWNAME_alltime  -- all IPL history (no date filter)
      - VIEWNAME_since2023 -- IPL 2023+ only

    Squad views and T20 comparison views are excluded.
    """

    print("\nCreating standardized dual-scope views...")

    # =========================================================================
    # PATTERN A: Existing views are ALL-TIME (no date filter)
    #   -> _alltime = alias to existing view
    #   -> _since2023 = new SQL with date filter added to CTE
    # =========================================================================

    # --- batter_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_phase_alltime AS SELECT * FROM analytics_ipl_batter_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
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
    print("  - analytics_ipl_batter_phase_alltime / _since2023")

    # --- batter_vs_bowler ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_alltime AS SELECT * FROM analytics_ipl_batter_vs_bowler"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 10 THEN 'LOW'
                 WHEN COUNT(*) < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, dp_bowl.player_id, dp_bowl.current_name
    """)
    print("  - analytics_ipl_batter_vs_bowler_alltime / _since2023")

    # --- batter_vs_bowler_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_phase_alltime AS SELECT * FROM analytics_ipl_batter_vs_bowler_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            fb.match_phase,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 6 THEN 'LOW'
                 WHEN COUNT(*) < 20 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, dp_bowl.player_id, dp_bowl.current_name, fb.match_phase
    """)
    print("  - analytics_ipl_batter_vs_bowler_phase_alltime / _since2023")

    # --- batter_vs_bowler_type ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_type_alltime AS SELECT * FROM analytics_ipl_batter_vs_bowler_type"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_type_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 50 THEN 'LOW'
                 WHEN COUNT(*) < 200 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
    """)
    print("  - analytics_ipl_batter_vs_bowler_type_alltime / _since2023")

    # --- batter_vs_bowler_type_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_type_phase_alltime AS SELECT * FROM analytics_ipl_batter_vs_bowler_type_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_bowler_type_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            fb.match_phase,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown'), fb.match_phase
    """)
    print("  - analytics_ipl_batter_vs_bowler_type_phase_alltime / _since2023")

    # --- batter_vs_team ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_vs_team_alltime AS SELECT * FROM analytics_ipl_batter_vs_team"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_team_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_team dt_opp ON fb.bowling_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name)
    """)
    print("  - analytics_ipl_batter_vs_team_alltime / _since2023")

    # --- batter_vs_team_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_vs_team_phase_alltime AS SELECT * FROM analytics_ipl_batter_vs_team_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_vs_team_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_team dt_opp ON fb.bowling_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name), fb.match_phase
    """)
    print("  - analytics_ipl_batter_vs_team_phase_alltime / _since2023")

    # --- batter_venue ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_venue_alltime AS SELECT * FROM analytics_ipl_batter_venue"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_venue_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            im.venue,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue
    """)
    print("  - analytics_ipl_batter_venue_alltime / _since2023")

    # --- batter_venue_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batter_venue_phase_alltime AS SELECT * FROM analytics_ipl_batter_venue_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batter_venue_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as batter_id,
            dp.current_name as batter_name,
            im.venue,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as innings,
            COUNT(*) as balls,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue, fb.match_phase
    """)
    print("  - analytics_ipl_batter_venue_phase_alltime / _since2023")

    # --- bowler_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_alltime AS SELECT * FROM analytics_ipl_bowler_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) as overs,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_conceded_pct,
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 100 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)
    print("  - analytics_ipl_bowler_phase_alltime / _since2023")

    # --- bowler_venue ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_venue_alltime AS SELECT * FROM analytics_ipl_bowler_venue"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_venue_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            im.venue,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue
    """)
    print("  - analytics_ipl_bowler_venue_alltime / _since2023")

    # --- bowler_venue_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_venue_phase_alltime AS SELECT * FROM analytics_ipl_bowler_venue_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_venue_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            im.venue,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN ipl_matches im ON fb.match_id = im.match_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp.player_id, dp.current_name, im.venue, fb.match_phase
    """)
    print("  - analytics_ipl_bowler_venue_phase_alltime / _since2023")

    # --- bowler_vs_batter_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_batter_phase_alltime AS SELECT * FROM analytics_ipl_bowler_vs_batter_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_batter_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            dp_bat.player_id as batter_id,
            dp_bat.current_name as batter_name,
            fb.match_phase,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 6 THEN 'LOW'
                 WHEN COUNT(*) < 20 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp_bowl.player_id, dp_bowl.current_name, dp_bat.player_id, dp_bat.current_name, fb.match_phase
    """)
    print("  - analytics_ipl_bowler_vs_batter_phase_alltime / _since2023")

    # --- bowler_vs_team ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_team_alltime AS SELECT * FROM analytics_ipl_bowler_vs_team"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_team_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 30 THEN 'LOW'
                 WHEN COUNT(*) < 100 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN dim_team dt_opp ON fb.batting_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name)
    """)
    print("  - analytics_ipl_bowler_vs_team_alltime / _since2023")

    # --- bowler_vs_team_phase ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_team_phase_alltime AS SELECT * FROM analytics_ipl_bowler_vs_team_phase"
    )
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_team_phase_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            dp.player_id as bowler_id,
            dp.current_name as bowler_name,
            COALESCE(fa.canonical_name, dt_opp.team_name) as opposition,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            COUNT(*) as balls,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(COUNT(*), 0), 2) as economy,
            ROUND(COUNT(*) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as boundary_conceded_pct,
            CASE WHEN COUNT(*) < 12 THEN 'LOW'
                 WHEN COUNT(*) < 36 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN dim_team dt_opp ON fb.batting_team_id = dt_opp.team_id
        LEFT JOIN dim_franchise_alias fa ON dt_opp.team_name = fa.team_name
        WHERE fb.is_legal_ball = TRUE
          AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY dp.player_id, dp.current_name, COALESCE(fa.canonical_name, dt_opp.team_name), fb.match_phase
    """)
    print("  - analytics_ipl_bowler_vs_team_phase_alltime / _since2023")

    # --- bowler_phase_distribution ---
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_distribution_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        bowler_phase_stats AS (
            SELECT
                dp.player_id as bowler_id,
                dp.current_name as bowler_name,
                fb.match_phase,
                COUNT(*) as balls,
                SUM(fb.total_runs) as runs_conceded,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls
            FROM fact_ball fb
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE fb.is_legal_ball = TRUE
              AND fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY dp.player_id, dp.current_name, fb.match_phase
        ),
        bowler_totals AS (
            SELECT
                bowler_id,
                bowler_name,
                SUM(balls) as total_balls,
                SUM(wickets) as total_wickets
            FROM bowler_phase_stats
            GROUP BY bowler_id, bowler_name
        )
        SELECT
            bps.bowler_id,
            bps.bowler_name,
            bps.match_phase,
            bps.balls,
            ROUND(bps.balls / 6.0, 1) as overs,
            bps.runs_conceded,
            bps.wickets,
            bps.dot_balls,
            ROUND(bps.runs_conceded * 6.0 / NULLIF(bps.balls, 0), 2) as economy,
            ROUND(bps.dot_balls * 100.0 / NULLIF(bps.balls, 0), 2) as dot_ball_pct,
            ROUND(bps.balls * 100.0 / NULLIF(bt.total_balls, 0), 1) as pct_overs_in_phase,
            ROUND(bps.wickets * 100.0 / NULLIF(bt.total_wickets, 0), 1) as pct_wickets_in_phase,
            ROUND(
                (bps.wickets * 100.0 / NULLIF(bt.total_wickets, 0)) -
                (bps.balls * 100.0 / NULLIF(bt.total_balls, 0)), 1
            ) as wicket_efficiency,
            bt.total_balls,
            bt.total_wickets,
            CASE WHEN bt.total_balls < 120 THEN 'LOW'
                 WHEN bt.total_balls < 300 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM bowler_phase_stats bps
        JOIN bowler_totals bt ON bps.bowler_id = bt.bowler_id
        ORDER BY bps.bowler_name,
            CASE bps.match_phase
                WHEN 'powerplay' THEN 1
                WHEN 'middle' THEN 2
                WHEN 'death' THEN 3
            END
    """)
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_distribution_since2023 AS SELECT * FROM analytics_ipl_bowler_phase_distribution"
    )
    print("  - analytics_ipl_bowler_phase_distribution_alltime / _since2023")

    # =========================================================================
    # PATTERN B: Existing views are 2023+ filtered
    #   -> _since2023 = alias to existing view
    #   -> _alltime = new SQL with date filter removed from CTE
    # =========================================================================

    # --- batting_career ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batting_career_since2023 AS SELECT * FROM analytics_ipl_batting_career"
    )
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batting_career_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        batting_stats AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(DISTINCT fb.match_id) as innings,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
                SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) as dot_balls
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.batter_id
        ),
        innings_scores AS (
            SELECT
                fb.batter_id as player_id,
                fb.match_id,
                SUM(fb.batter_runs) as innings_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.batter_id, fb.match_id
        ),
        high_scores AS (
            SELECT
                player_id,
                MAX(innings_runs) as highest_score,
                SUM(CASE WHEN innings_runs >= 50 THEN 1 ELSE 0 END) as fifties,
                SUM(CASE WHEN innings_runs >= 100 THEN 1 ELSE 0 END) as hundreds
            FROM innings_scores
            GROUP BY player_id
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dp.primary_role,
            bs.innings,
            bs.runs,
            bs.balls_faced,
            bs.dismissals,
            hs.highest_score,
            hs.fifties,
            hs.hundreds,
            bs.fours,
            bs.sixes,
            bs.dot_balls,
            ROUND(bs.runs * 100.0 / NULLIF(bs.balls_faced, 0), 2) as strike_rate,
            ROUND(bs.runs * 1.0 / NULLIF(bs.dismissals, 0), 2) as batting_average,
            ROUND((bs.fours + bs.sixes) * 100.0 / NULLIF(bs.balls_faced, 0), 2) as boundary_pct,
            ROUND(bs.dot_balls * 100.0 / NULLIF(bs.balls_faced, 0), 2) as dot_ball_pct,
            CASE WHEN bs.innings < 10 THEN 'LOW'
                 WHEN bs.innings < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM batting_stats bs
        JOIN dim_player dp ON bs.player_id = dp.player_id
        JOIN high_scores hs ON bs.player_id = hs.player_id
    """)
    print("  - analytics_ipl_batting_career_since2023 / _alltime")

    # --- bowling_career ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowling_career_since2023 AS SELECT * FROM analytics_ipl_bowling_career"
    )
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_career_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        bowling_stats AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(DISTINCT fb.match_id) as matches_bowled,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
                SUM(fb.total_runs) as runs_conceded,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.bowler_id
        ),
        best_figures AS (
            SELECT
                fb.bowler_id as player_id,
                fb.match_id,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as match_wickets,
                SUM(fb.total_runs) as match_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.bowler_id, fb.match_id
        ),
        best_bowling AS (
            SELECT
                player_id,
                MAX(match_wickets) as best_wickets,
                FIRST(match_runs ORDER BY match_wickets DESC, match_runs ASC) as best_runs
            FROM best_figures
            GROUP BY player_id
        )
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dp.primary_role,
            bs.matches_bowled,
            bs.balls_bowled,
            ROUND(bs.balls_bowled / 6.0, 1) as overs_bowled,
            bs.runs_conceded,
            bs.wickets,
            bb.best_wickets,
            bb.best_runs,
            bs.dot_balls,
            bs.fours_conceded,
            bs.sixes_conceded,
            ROUND(bs.runs_conceded * 6.0 / NULLIF(bs.balls_bowled, 0), 2) as economy_rate,
            ROUND(bs.runs_conceded * 1.0 / NULLIF(bs.wickets, 0), 2) as bowling_average,
            ROUND(bs.balls_bowled * 1.0 / NULLIF(bs.wickets, 0), 2) as bowling_strike_rate,
            ROUND(bs.dot_balls * 100.0 / NULLIF(bs.balls_bowled, 0), 2) as dot_ball_pct,
            ROUND((bs.fours_conceded + bs.sixes_conceded) * 100.0 / NULLIF(bs.balls_bowled, 0), 2) as boundary_conceded_pct,
            CASE WHEN bs.matches_bowled < 10 THEN 'LOW'
                 WHEN bs.matches_bowled < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM bowling_stats bs
        JOIN dim_player dp ON bs.player_id = dp.player_id
        JOIN best_bowling bb ON bs.player_id = bb.player_id
    """)
    print("  - analytics_ipl_bowling_career_since2023 / _alltime")

    # --- batting_percentiles ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_batting_percentiles_since2023 AS SELECT * FROM analytics_ipl_batting_percentiles"
    )
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batting_percentiles_alltime AS
        WITH qualified_batters AS (
            SELECT *
            FROM analytics_ipl_batting_career_alltime
            WHERE balls_faced >= 500
        )
        SELECT
            player_id,
            player_name,
            innings,
            runs,
            balls_faced,
            strike_rate,
            batting_average,
            boundary_pct,
            dot_ball_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY boundary_pct) * 100, 1) as boundary_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY dot_ball_pct DESC) * 100, 1) as dot_ball_percentile
        FROM qualified_batters
    """)
    print("  - analytics_ipl_batting_percentiles_since2023 / _alltime")

    # --- bowling_percentiles ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowling_percentiles_since2023 AS SELECT * FROM analytics_ipl_bowling_percentiles"
    )
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_percentiles_alltime AS
        WITH qualified_bowlers AS (
            SELECT *
            FROM analytics_ipl_bowling_career_alltime
            WHERE balls_bowled >= 300
        )
        SELECT
            player_id,
            player_name,
            matches_bowled,
            balls_bowled,
            overs_bowled,
            wickets,
            economy_rate,
            bowling_average,
            bowling_strike_rate,
            dot_ball_pct,
            boundary_conceded_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY bowling_average DESC) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY bowling_strike_rate DESC) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM qualified_bowlers
    """)
    print("  - analytics_ipl_bowling_percentiles_since2023 / _alltime")

    # --- batter_phase_percentiles ---
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_phase_percentiles_since2023 AS
        WITH qualified AS (
            SELECT *
            FROM analytics_ipl_batter_phase_since2023
            WHERE balls_faced >= 100
        )
        SELECT
            player_id,
            player_name,
            match_phase,
            innings,
            runs,
            balls_faced,
            strike_rate,
            batting_average,
            boundary_pct,
            dot_ball_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY boundary_pct) * 100, 1) as boundary_percentile
        FROM qualified
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_phase_percentiles_alltime AS
        WITH qualified AS (
            SELECT *
            FROM analytics_ipl_batter_phase_alltime
            WHERE balls_faced >= 100
        )
        SELECT
            player_id,
            player_name,
            match_phase,
            innings,
            runs,
            balls_faced,
            strike_rate,
            batting_average,
            boundary_pct,
            dot_ball_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY strike_rate) * 100, 1) as sr_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY batting_average) * 100, 1) as avg_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY boundary_pct) * 100, 1) as boundary_percentile
        FROM qualified
    """)
    print("  - analytics_ipl_batter_phase_percentiles_since2023 / _alltime")

    # --- bowler_phase_percentiles ---
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_percentiles_since2023 AS
        WITH qualified AS (
            SELECT *
            FROM analytics_ipl_bowler_phase_since2023
            WHERE balls_bowled >= 60
        )
        SELECT
            player_id,
            player_name,
            match_phase,
            matches,
            balls_bowled,
            overs,
            wickets,
            economy_rate,
            bowling_average,
            dot_ball_pct,
            boundary_conceded_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM qualified
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_percentiles_alltime AS
        WITH qualified AS (
            SELECT *
            FROM analytics_ipl_bowler_phase_alltime
            WHERE balls_bowled >= 60
        )
        SELECT
            player_id,
            player_name,
            match_phase,
            matches,
            balls_bowled,
            overs,
            wickets,
            economy_rate,
            bowling_average,
            dot_ball_pct,
            boundary_conceded_pct,
            sample_size,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY economy_rate DESC) * 100, 1) as economy_percentile,
            ROUND(PERCENT_RANK() OVER (PARTITION BY match_phase ORDER BY dot_ball_pct) * 100, 1) as dot_ball_percentile
        FROM qualified
    """)
    print("  - analytics_ipl_bowler_phase_percentiles_since2023 / _alltime")

    # --- bowler_vs_batter_handedness ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_batter_handedness_since2023 AS SELECT * FROM analytics_ipl_bowler_vs_batter_handedness"
    )
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_vs_batter_handedness_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            dp_bowl.player_id as bowler_id,
            dp_bowl.current_name as bowler_name,
            sq.batting_hand,
            COUNT(*) FILTER (WHERE fb.is_legal_ball) as balls,
            SUM(fb.batter_runs + fb.extra_runs) as runs,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
            SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
            ROUND(SUM(fb.batter_runs + fb.extra_runs) * 6.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as economy,
            ROUND(COUNT(*) FILTER (WHERE fb.is_legal_ball) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as dot_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 2) as boundary_pct,
            ROUND(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*) FILTER (WHERE fb.is_legal_ball), 0), 4) as wickets_per_ball,
            CASE WHEN COUNT(*) FILTER (WHERE fb.is_legal_ball) < 60 THEN 'LOW'
                 WHEN COUNT(*) FILTER (WHERE fb.is_legal_ball) < 200 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        JOIN ipl_2026_squads sq ON fb.batter_id = sq.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
          AND sq.batting_hand IS NOT NULL
        GROUP BY dp_bowl.player_id, dp_bowl.current_name, sq.batting_hand
    """)
    print("  - analytics_ipl_bowler_vs_batter_handedness_since2023 / _alltime")

    # --- batting_benchmarks ---
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_batting_benchmarks_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.batter_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as total_balls,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as total_wickets,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_batting_avg,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_dot_ball_pct
        FROM fact_ball fb
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.match_phase
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batting_benchmarks_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.batter_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as total_balls,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as total_wickets,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_batting_avg,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_dot_ball_pct
        FROM fact_ball fb
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.match_phase
    """)
    print("  - analytics_ipl_batting_benchmarks_since2023 / _alltime")

    # --- bowling_benchmarks ---
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_benchmarks_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.total_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as total_balls,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as total_wickets,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_economy,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_bowling_avg,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_bowling_sr,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_dot_ball_pct
        FROM fact_ball fb
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.match_phase
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_benchmarks_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.total_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as total_balls,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as total_wickets,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_economy,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_bowling_avg,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) as avg_bowling_sr,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as avg_dot_ball_pct
        FROM fact_ball fb
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.match_phase
    """)
    print("  - analytics_ipl_bowling_benchmarks_since2023 / _alltime")

    # --- vs_bowler_type_benchmarks ---
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_vs_bowler_type_benchmarks_since2023 AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
        )
        SELECT
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            COUNT(*) as total_balls,
            SUM(fb.batter_runs) as total_runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as total_dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as avg_strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as avg_batting_avg,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as avg_boundary_pct
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
          AND fb.is_legal_ball = TRUE
        GROUP BY COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
    """)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_vs_bowler_type_benchmarks_alltime AS
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        )
        SELECT
            COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown') as bowler_type,
            COUNT(*) as total_balls,
            SUM(fb.batter_runs) as total_runs,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as total_dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) as avg_strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as avg_batting_avg,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(COUNT(*), 0), 2) as avg_boundary_pct
        FROM fact_ball fb
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        LEFT JOIN ipl_2026_squads sq ON dp_bowl.player_id = sq.player_id
        LEFT JOIN dim_bowler_classification bc ON dp_bowl.player_id = bc.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
          AND fb.is_legal_ball = TRUE
        GROUP BY COALESCE(sq.bowling_type, bc.bowling_style, 'Unknown')
    """)
    print("  - analytics_ipl_vs_bowler_type_benchmarks_since2023 / _alltime")

    # --- career_benchmarks ---
    conn.execute(
        "CREATE OR REPLACE VIEW analytics_ipl_career_benchmarks_since2023 AS SELECT * FROM analytics_ipl_career_benchmarks"
    )
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_career_benchmarks_alltime AS
        SELECT
            'batting' as category,
            COUNT(*) as qualified_players,
            ROUND(AVG(strike_rate), 2) as avg_strike_rate,
            ROUND(AVG(batting_average), 2) as avg_batting_avg,
            ROUND(AVG(boundary_pct), 2) as avg_boundary_pct,
            ROUND(AVG(dot_ball_pct), 2) as avg_dot_ball_pct,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY strike_rate), 2) as median_strike_rate,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY batting_average), 2) as median_batting_avg
        FROM analytics_ipl_batting_career_alltime
        WHERE balls_faced >= 500
        UNION ALL
        SELECT
            'bowling' as category,
            COUNT(*) as qualified_players,
            ROUND(AVG(economy_rate), 2) as avg_economy,
            ROUND(AVG(bowling_average), 2) as avg_bowling_avg,
            ROUND(AVG(dot_ball_pct), 2) as avg_dot_ball_pct,
            ROUND(AVG(boundary_conceded_pct), 2) as avg_boundary_pct,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY economy_rate), 2) as median_economy,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY bowling_average), 2) as median_bowling_avg
        FROM analytics_ipl_bowling_career_alltime
        WHERE balls_bowled >= 300
    """)
    print("  - analytics_ipl_career_benchmarks_since2023 / _alltime")

    print("\n  Standardized dual-scope views created: 27 pairs (54 views total)")


def _dual_view(conn, base_name, sql_template):
    """Create both _alltime and _since2023 versions of an IPL view."""
    for suffix, date_filter in [
        ("_alltime", ""),
        ("_since2023", f"AND dm.match_date >= '{IPL_MIN_DATE}'"),
    ]:
        full_sql = sql_template.replace("{DATE_FILTER}", date_filter)
        conn.execute(f"CREATE OR REPLACE VIEW {base_name}{suffix} AS {full_sql}")
    print(f"  - {base_name}_alltime + _since2023")


def create_film_room_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create Film Room analytical views (13 views x 2 variants = 26 views)."""

    print("\nCreating Film Room views...")

    # ── 1. Batter Entry Point ─────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_batter_entry_point",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        first_appearance AS (
            SELECT
                fb.batter_id,
                fb.match_id,
                fb.innings,
                fb.batting_team_id,
                fb.bowling_team_id,
                MIN(fb.ball_seq) AS entry_ball_seq,
                MIN(fb.over) AS entry_over
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.batter_id, fb.match_id, fb.innings, fb.batting_team_id, fb.bowling_team_id
        ),
        with_position AS (
            SELECT
                fa.*,
                ROW_NUMBER() OVER (PARTITION BY fa.match_id, fa.innings ORDER BY fa.entry_ball_seq) AS batting_position
            FROM first_appearance fa
        ),
        team_state AS (
            SELECT
                wp.*,
                COALESCE((
                    SELECT SUM(fb2.total_runs)
                    FROM fact_ball fb2
                    WHERE fb2.match_id = wp.match_id
                      AND fb2.innings = wp.innings
                      AND fb2.ball_seq < wp.entry_ball_seq
                ), 0) AS team_score_at_entry,
                COALESCE((
                    SELECT SUM(CASE WHEN fb2.is_wicket THEN 1 ELSE 0 END)
                    FROM fact_ball fb2
                    WHERE fb2.match_id = wp.match_id
                      AND fb2.innings = wp.innings
                      AND fb2.ball_seq < wp.entry_ball_seq
                ), 0) AS team_wickets_at_entry
            FROM with_position wp
        ),
        innings1_total AS (
            SELECT
                fb.match_id,
                SUM(fb.total_runs) + 1 AS chase_target
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.innings = 1
            GROUP BY fb.match_id
        )
        SELECT
            ts.batter_id,
            dp.current_name AS batter_name,
            ts.match_id,
            ts.innings,
            ts.batting_position,
            ts.entry_over,
            ts.entry_ball_seq,
            ts.team_score_at_entry,
            ts.team_wickets_at_entry,
            CASE WHEN ts.innings = 1 THEN NULL ELSE i1.chase_target END AS chase_target,
            dt_bat.team_name AS team_name,
            dt_bowl.team_name AS opposition
        FROM team_state ts
        JOIN dim_player dp ON ts.batter_id = dp.player_id
        JOIN dim_team dt_bat ON ts.batting_team_id = dt_bat.team_id
        JOIN dim_team dt_bowl ON ts.bowling_team_id = dt_bowl.team_id
        LEFT JOIN innings1_total i1 ON ts.match_id = i1.match_id
    """,
    )

    # ── 2. Match Context ──────────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_match_context",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        innings_agg AS (
            SELECT
                fb.match_id,
                fb.innings,
                SUM(fb.total_runs) AS runs,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets,
                ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) AS overs,
                MIN(fb.batting_team_id) AS batting_team_id
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.match_id, fb.innings
        )
        SELECT
            dm.match_id,
            dm.season,
            dm.match_date,
            dv.venue_name,
            dv.city,
            dt1.team_name AS team1_name,
            dt2.team_name AS team2_name,
            dm.toss_decision,
            dtw.team_name AS winner_name,
            i1.runs AS innings1_runs,
            i1.wickets AS innings1_wickets,
            i1.overs AS innings1_overs,
            i2.runs AS innings2_runs,
            i2.wickets AS innings2_wickets,
            i2.overs AS innings2_overs,
            i1.runs + 1 AS chase_target,
            CASE
                WHEN dm.winner_id = i2.batting_team_id THEN 'Won'
                WHEN dm.winner_id IS NULL THEN 'No Result'
                ELSE 'Lost'
            END AS chase_result
        FROM dim_match dm
        JOIN dim_tournament dtt ON dm.tournament_id = dtt.tournament_id
        JOIN dim_venue dv ON dm.venue_id = dv.venue_id
        JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
        JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
        LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
        LEFT JOIN innings_agg i1 ON dm.match_id = i1.match_id AND i1.innings = 1
        LEFT JOIN innings_agg i2 ON dm.match_id = i2.match_id AND i2.innings = 2
        WHERE dm.match_id IN (SELECT match_id FROM ipl_matches)
    """,
    )

    # ── 3. Innings Progression ────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_innings_progression",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        over_agg AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.over AS over_number,
                SUM(fb.total_runs) AS runs_this_over,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets_this_over,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS legal_balls_this_over
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.match_id, fb.innings, fb.over
        ),
        with_cumulative AS (
            SELECT
                oa.*,
                SUM(oa.runs_this_over) OVER (PARTITION BY oa.match_id, oa.innings ORDER BY oa.over_number) AS cumulative_runs,
                SUM(oa.wickets_this_over) OVER (PARTITION BY oa.match_id, oa.innings ORDER BY oa.over_number) AS cumulative_wickets,
                SUM(oa.legal_balls_this_over) OVER (PARTITION BY oa.match_id, oa.innings ORDER BY oa.over_number) AS cumulative_legal_balls
            FROM over_agg oa
        ),
        innings1_total AS (
            SELECT
                match_id,
                SUM(runs_this_over) + 1 AS chase_target
            FROM over_agg
            WHERE innings = 1
            GROUP BY match_id
        )
        SELECT
            wc.match_id,
            wc.innings,
            wc.over_number,
            wc.runs_this_over,
            wc.wickets_this_over,
            wc.cumulative_runs,
            wc.cumulative_wickets,
            ROUND(wc.cumulative_runs * 6.0 / NULLIF(wc.cumulative_legal_balls, 0), 2) AS run_rate,
            CASE WHEN wc.innings = 2 THEN i1t.chase_target ELSE NULL END AS chase_target,
            CASE WHEN wc.innings = 2 THEN i1t.chase_target - wc.cumulative_runs ELSE NULL END AS runs_remaining,
            CASE WHEN wc.innings = 2
                THEN ROUND((i1t.chase_target - wc.cumulative_runs) * 6.0 / NULLIF(120 - wc.cumulative_legal_balls, 0), 2)
                ELSE NULL
            END AS required_run_rate
        FROM with_cumulative wc
        LEFT JOIN innings1_total i1t ON wc.match_id = i1t.match_id
    """,
    )

    # ── 4. Batting Order Flexibility ──────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_batting_order_flexibility",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        first_appearance AS (
            SELECT
                fb.batter_id,
                fb.match_id,
                fb.innings,
                fb.batting_team_id,
                MIN(fb.ball_seq) AS entry_ball_seq
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.batter_id, fb.match_id, fb.innings, fb.batting_team_id
        ),
        with_position AS (
            SELECT
                fa.*,
                ROW_NUMBER() OVER (PARTITION BY fa.match_id, fa.innings ORDER BY fa.entry_ball_seq) AS batting_position
            FROM first_appearance fa
        ),
        with_wickets AS (
            SELECT
                wp.*,
                COALESCE((
                    SELECT SUM(CASE WHEN fb2.is_wicket THEN 1 ELSE 0 END)
                    FROM fact_ball fb2
                    WHERE fb2.match_id = wp.match_id
                      AND fb2.innings = wp.innings
                      AND fb2.ball_seq < wp.entry_ball_seq
                ), 0) AS team_wickets_at_entry
            FROM with_position wp
        )
        SELECT
            ww.batter_id,
            dp.current_name AS batter_name,
            dtt.team_name,
            COUNT(*) AS innings_count,
            ROUND(AVG(ww.batting_position), 2) AS avg_batting_position,
            ROUND(AVG(CASE WHEN ww.team_wickets_at_entry = 0 THEN ww.batting_position END), 2) AS avg_position_0_wickets,
            ROUND(AVG(CASE WHEN ww.team_wickets_at_entry = 1 THEN ww.batting_position END), 2) AS avg_position_1_wicket,
            ROUND(AVG(CASE WHEN ww.team_wickets_at_entry >= 2 THEN ww.batting_position END), 2) AS avg_position_2plus_wickets,
            ROUND(
                AVG(CASE WHEN ww.team_wickets_at_entry >= 2 THEN ww.batting_position END)
                - AVG(CASE WHEN ww.team_wickets_at_entry = 0 THEN ww.batting_position END)
            , 2) AS position_shift
        FROM with_wickets ww
        JOIN dim_player dp ON ww.batter_id = dp.player_id
        JOIN dim_team dtt ON ww.batting_team_id = dtt.team_id
        GROUP BY ww.batter_id, dp.current_name, dtt.team_name
        HAVING COUNT(*) >= 5
    """,
    )

    # ── 5. Bowler Over Breakdown ──────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_bowler_over_breakdown",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        )
        SELECT
            fb.bowler_id,
            dp.current_name AS bowler_name,
            fb.over + 1 AS over_number,
            COUNT(DISTINCT fb.match_id) AS times_bowled,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS balls_bowled,
            SUM(fb.total_runs) AS runs_conceded,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS economy,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0
                / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0
                / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS boundary_conceded_pct
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.bowler_id, dp.current_name, fb.over
    """,
    )

    # ── 6. New Batter Vulnerability ───────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_new_batter_vulnerability",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        numbered_balls AS (
            SELECT
                fb.*,
                ROW_NUMBER() OVER (PARTITION BY fb.match_id, fb.innings, fb.batter_id ORDER BY fb.ball_seq) AS batter_ball_num
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.is_legal_ball
        )
        SELECT
            nb.batter_id,
            dp.current_name AS batter_name,
            CASE WHEN nb.batter_ball_num <= 10 THEN 'first_10' ELSE 'settled' END AS ball_phase,
            COUNT(*) AS balls,
            SUM(nb.batter_runs) AS runs,
            SUM(CASE WHEN nb.is_wicket AND nb.player_out_id = nb.batter_id THEN 1 ELSE 0 END) AS dismissals,
            ROUND(SUM(nb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) AS strike_rate,
            ROUND(SUM(CASE WHEN nb.batter_runs = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS dot_ball_pct,
            ROUND((SUM(CASE WHEN nb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN nb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0
                / NULLIF(COUNT(*), 0), 2) AS boundary_pct
        FROM numbered_balls nb
        JOIN dim_player dp ON nb.batter_id = dp.player_id
        GROUP BY nb.batter_id, dp.current_name, CASE WHEN nb.batter_ball_num <= 10 THEN 'first_10' ELSE 'settled' END
    """,
    )

    # ── 7. Partnership Analysis ───────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_partnership_analysis",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        )
        SELECT
            LEAST(fb.batter_id, fb.non_striker_id) AS player_a_id,
            dp_a.current_name AS player_a_name,
            GREATEST(fb.batter_id, fb.non_striker_id) AS player_b_id,
            dp_b.current_name AS player_b_name,
            COUNT(DISTINCT CONCAT(CAST(fb.match_id AS VARCHAR), '-', CAST(fb.innings AS VARCHAR))) AS partnerships,
            SUM(fb.total_runs) AS total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS balls,
            SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) AS boundaries,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS run_rate
        FROM fact_ball fb
        JOIN dim_player dp_a ON LEAST(fb.batter_id, fb.non_striker_id) = dp_a.player_id
        JOIN dim_player dp_b ON GREATEST(fb.batter_id, fb.non_striker_id) = dp_b.player_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY LEAST(fb.batter_id, fb.non_striker_id), dp_a.current_name,
                 GREATEST(fb.batter_id, fb.non_striker_id), dp_b.current_name
    """,
    )

    # ── 8. Dot Ball Pressure ──────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_dot_ball_pressure",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        numbered AS (
            SELECT fb.*,
                   CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 0 ELSE 1 END AS is_scoring,
                   SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 0 ELSE 1 END)
                       OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS scoring_group
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        dot_runs AS (
            SELECT match_id, innings, scoring_group,
                   COUNT(*) AS dots_in_sequence,
                   MAX(ball_seq) AS last_dot_seq
            FROM numbered WHERE is_scoring = 0
            GROUP BY match_id, innings, scoring_group
        ),
        next_ball AS (
            SELECT dr.*,
                   fb_next.is_wicket AS next_is_wicket
            FROM dot_runs dr
            LEFT JOIN fact_ball fb_next ON dr.match_id = fb_next.match_id
                AND dr.innings = fb_next.innings
                AND fb_next.ball_seq = dr.last_dot_seq + 1
            WHERE dr.dots_in_sequence >= 2
        )
        SELECT
            CASE WHEN dots_in_sequence >= 6 THEN '6+' ELSE CAST(dots_in_sequence AS VARCHAR) END AS consecutive_dots,
            COUNT(*) AS occurrences,
            ROUND(SUM(CASE WHEN next_is_wicket THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS next_ball_wicket_pct
        FROM next_ball
        GROUP BY CASE WHEN dots_in_sequence >= 6 THEN '6+' ELSE CAST(dots_in_sequence AS VARCHAR) END
    """,
    )

    # ── 9. Wicket Clusters ────────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_wicket_clusters",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        wicket_balls AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.batting_team_id,
                fb.bowling_team_id,
                fb.ball_seq,
                LAG(fb.ball_seq) OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS prev_wicket_seq
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.is_wicket
        ),
        cluster_flags AS (
            SELECT
                wb.*,
                CASE WHEN wb.ball_seq - wb.prev_wicket_seq <= 12 THEN 1 ELSE 0 END AS in_cluster
            FROM wicket_balls wb
            WHERE wb.prev_wicket_seq IS NOT NULL
        )
        SELECT
            cf.batting_team_id,
            dt_bat.team_name AS batting_team_name,
            cf.bowling_team_id,
            dt_bowl.team_name AS bowling_team_name,
            SUM(cf.in_cluster) AS cluster_events,
            SUM(cf.in_cluster) * 2 AS total_cluster_wickets,
            COUNT(DISTINCT CASE WHEN cf.in_cluster = 1 THEN cf.match_id END) AS matches_with_clusters
        FROM cluster_flags cf
        JOIN dim_team dt_bat ON cf.batting_team_id = dt_bat.team_id
        JOIN dim_team dt_bowl ON cf.bowling_team_id = dt_bowl.team_id
        GROUP BY cf.batting_team_id, dt_bat.team_name, cf.bowling_team_id, dt_bowl.team_name
    """,
    )

    # ── 10. Team Phase Scoring ────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_team_phase_scoring",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        )
        SELECT
            fb.batting_team_id,
            dtt.team_name,
            fb.innings,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) AS matches,
            SUM(fb.total_runs) AS runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS run_rate,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets_lost,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0
                / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0
                / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct
        FROM fact_ball fb
        JOIN dim_team dtt ON fb.batting_team_id = dtt.team_id
        WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        GROUP BY fb.batting_team_id, dtt.team_name, fb.innings, fb.match_phase
    """,
    )

    # ── 11. Required Rate Performance ─────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_required_rate_performance",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        innings1_total AS (
            SELECT
                fb.match_id,
                SUM(fb.total_runs) + 1 AS chase_target
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.innings = 1
            GROUP BY fb.match_id
        ),
        chase_balls AS (
            SELECT
                fb.batter_id,
                fb.match_id,
                fb.ball_seq,
                fb.batter_runs,
                fb.is_wicket,
                fb.player_out_id,
                fb.is_legal_ball,
                i1t.chase_target,
                COALESCE(SUM(fb2.total_runs), 0) AS cumulative_runs_before,
                120 - SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS legal_balls_remaining
            FROM fact_ball fb
            JOIN innings1_total i1t ON fb.match_id = i1t.match_id
            LEFT JOIN fact_ball fb2 ON fb.match_id = fb2.match_id
                AND fb2.innings = 2
                AND fb2.ball_seq < fb.ball_seq
                AND fb2.is_legal_ball
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.innings = 2
              AND fb.is_legal_ball
            GROUP BY fb.batter_id, fb.match_id, fb.ball_seq, fb.batter_runs,
                     fb.is_wicket, fb.player_out_id, fb.is_legal_ball, fb.innings,
                     i1t.chase_target
        ),
        with_rrr AS (
            SELECT
                cb.*,
                ROUND((cb.chase_target - cb.cumulative_runs_before) * 6.0 / NULLIF(cb.legal_balls_remaining + 1, 0), 2) AS required_run_rate
            FROM chase_balls cb
            WHERE cb.legal_balls_remaining >= 0
        ),
        with_band AS (
            SELECT
                wr.*,
                CASE
                    WHEN wr.required_run_rate < 8 THEN 'RRR_under_8'
                    WHEN wr.required_run_rate < 10 THEN 'RRR_8_10'
                    WHEN wr.required_run_rate < 12 THEN 'RRR_10_12'
                    ELSE 'RRR_12_plus'
                END AS pressure_band
            FROM with_rrr wr
        )
        SELECT
            wb.batter_id,
            dp.current_name AS batter_name,
            wb.pressure_band,
            COUNT(*) AS balls_faced,
            SUM(wb.batter_runs) AS runs,
            ROUND(SUM(wb.batter_runs) * 100.0 / NULLIF(COUNT(*), 0), 2) AS strike_rate,
            SUM(CASE WHEN wb.is_wicket AND wb.player_out_id = wb.batter_id THEN 1 ELSE 0 END) AS dismissals,
            ROUND((SUM(CASE WHEN wb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN wb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0
                / NULLIF(COUNT(*), 0), 2) AS boundary_pct
        FROM with_band wb
        JOIN dim_player dp ON wb.batter_id = dp.player_id
        GROUP BY wb.batter_id, dp.current_name, wb.pressure_band
    """,
    )

    # ── 12. Venue Profile ─────────────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_venue_profile",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id, dm.venue_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        )
        SELECT
            im.venue_id,
            dv.venue_name,
            dv.city,
            fb.innings,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) AS matches,
            SUM(fb.total_runs) AS total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS total_balls,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS run_rate,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0
                / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS boundary_pct,
            ROUND(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(DISTINCT fb.match_id), 0), 2) AS wickets_per_match,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0
                / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct
        FROM fact_ball fb
        JOIN ipl_matches im ON fb.match_id = im.match_id
        JOIN dim_venue dv ON im.venue_id = dv.venue_id
        GROUP BY im.venue_id, dv.venue_name, dv.city, fb.innings, fb.match_phase
    """,
    )

    # ── 13. Bowling Change Impact ─────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_bowling_change_impact",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        bowler_overs AS (
            SELECT DISTINCT
                fb.match_id,
                fb.innings,
                fb.bowler_id,
                fb.over
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        with_prev AS (
            SELECT
                bo.*,
                LAG(bo.over) OVER (PARTITION BY bo.match_id, bo.innings, bo.bowler_id ORDER BY bo.over) AS prev_over
            FROM bowler_overs bo
        ),
        spell_marked AS (
            SELECT
                wp.*,
                CASE WHEN wp.prev_over IS NULL OR wp.over - wp.prev_over > 1 THEN 'first_over' ELSE 'continuation' END AS spell_position
            FROM with_prev wp
        )
        SELECT
            sm.bowler_id,
            dp.current_name AS bowler_name,
            sm.spell_position,
            COUNT(*) AS overs_bowled,
            SUM(fb_agg.over_runs) AS runs_conceded,
            SUM(fb_agg.over_wickets) AS wickets,
            ROUND(SUM(fb_agg.over_runs) * 6.0 / NULLIF(SUM(fb_agg.over_legal_balls), 0), 2) AS economy,
            ROUND(SUM(fb_agg.over_dots) * 100.0 / NULLIF(SUM(fb_agg.over_legal_balls), 0), 2) AS dot_ball_pct
        FROM spell_marked sm
        JOIN (
            SELECT
                fb.match_id,
                fb.innings,
                fb.bowler_id,
                fb.over,
                SUM(fb.total_runs) AS over_runs,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS over_wickets,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS over_legal_balls,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) AS over_dots
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
            GROUP BY fb.match_id, fb.innings, fb.bowler_id, fb.over
        ) fb_agg ON sm.match_id = fb_agg.match_id
            AND sm.innings = fb_agg.innings
            AND sm.bowler_id = fb_agg.bowler_id
            AND sm.over = fb_agg.over
        JOIN dim_player dp ON sm.bowler_id = dp.player_id
        GROUP BY sm.bowler_id, dp.current_name, sm.spell_position
    """,
    )

    print("\n  Film Room: 13 views x 2 variants = 26 views created.")


def create_pressure_performance_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create pressure performance views for TKT-050 (IPL 2023+ only).

    5 RRR bands: COMFORTABLE (<8), BUILDING (8-10), HIGH (10-12),
    EXTREME (12-15), NEAR_IMPOSSIBLE (15+).
    Covers both batters and bowlers with sequence analysis.
    """

    print("\nCreating Pressure Performance views (TKT-050)...")

    # ── 1. Batter Pressure Bands ─────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_batter_pressure_bands",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        first_innings_total AS (
            SELECT fb.match_id, SUM(fb.total_runs) AS target_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches) AND fb.innings = 1
            GROUP BY fb.match_id
        ),
        running_context AS (
            SELECT fb.match_id, fb.innings, fb.ball_seq,
                fb.batter_id, fb.bowler_id,
                fb.batter_runs, fb.extra_runs, fb.total_runs,
                fb.is_wicket, fb.is_legal_ball,
                SUM(fb.total_runs) OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS cumulative_runs,
                fit.target_runs + 1 AS target,
                (120 - fb.ball_seq) AS balls_remaining,
                -- Balls faced by this batter in this innings before this ball
                COALESCE(
                    SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) OVER (
                        PARTITION BY fb.match_id, fb.innings, fb.batter_id
                        ORDER BY fb.ball_seq
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ), 0
                ) AS batter_balls_before
            FROM fact_ball fb
            JOIN first_innings_total fit ON fb.match_id = fit.match_id
            WHERE fb.innings = 2 AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        with_bands AS (
            SELECT *,
                CASE
                    WHEN balls_remaining <= 0 THEN NULL
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 15 THEN 'NEAR_IMPOSSIBLE'
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 12 THEN 'EXTREME'
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 10 THEN 'HIGH'
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 8  THEN 'BUILDING'
                    ELSE 'COMFORTABLE'
                END AS pressure_band
            FROM running_context
            WHERE balls_remaining > 0
        ),
        -- Find the first ball each batter faces in each pressure band per innings
        band_entry AS (
            SELECT batter_id, match_id, innings, pressure_band,
                MIN(batter_balls_before) AS entry_balls_before
            FROM with_bands
            WHERE pressure_band IS NOT NULL
            GROUP BY batter_id, match_id, innings, pressure_band
        )
        SELECT
            wb.batter_id AS player_id,
            dp.current_name AS player_name,
            wb.pressure_band,
            COUNT(DISTINCT wb.match_id) AS innings,
            SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) AS balls_faced,
            SUM(wb.batter_runs) AS runs,
            ROUND(SUM(wb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS strike_rate,
            ROUND(SUM(wb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN wb.is_wicket THEN 1 ELSE 0 END), 0), 2) AS batting_average,
            ROUND(SUM(CASE WHEN wb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS boundary_pct,
            ROUND(SUM(CASE WHEN wb.batter_runs = 0 AND wb.extra_runs = 0 AND wb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct,
            ROUND(SUM(CASE WHEN wb.batter_runs = 6 THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS six_pct,
            SUM(CASE WHEN wb.is_wicket THEN 1 ELSE 0 END) AS dismissals,
            -- Entry context: avg balls faced before entering this pressure band
            ROUND(AVG(be.entry_balls_before), 1) AS avg_balls_before_entry,
            CASE
                WHEN AVG(be.entry_balls_before) > 40 THEN 'DEEP_SET'
                WHEN AVG(be.entry_balls_before) > 25 THEN 'SET'
                WHEN AVG(be.entry_balls_before) >= 10 THEN 'BUILDING'
                ELSE 'FRESH'
            END AS entry_context
        FROM with_bands wb
        JOIN dim_player dp ON wb.batter_id = dp.player_id
        JOIN band_entry be ON wb.batter_id = be.batter_id
            AND wb.match_id = be.match_id
            AND wb.innings = be.innings
            AND wb.pressure_band = be.pressure_band
        WHERE wb.pressure_band IS NOT NULL
        GROUP BY wb.batter_id, dp.current_name, wb.pressure_band
        HAVING SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) >= 15
    """,
    )

    # ── 2. Bowler Pressure Bands ─────────────────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_bowler_pressure_bands",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        first_innings_total AS (
            SELECT fb.match_id, SUM(fb.total_runs) AS target_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches) AND fb.innings = 1
            GROUP BY fb.match_id
        ),
        running_context AS (
            SELECT fb.match_id, fb.innings, fb.ball_seq,
                fb.batter_id, fb.bowler_id,
                fb.batter_runs, fb.extra_runs, fb.total_runs,
                fb.is_wicket, fb.wicket_type, fb.is_legal_ball,
                SUM(fb.total_runs) OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS cumulative_runs,
                fit.target_runs + 1 AS target,
                (120 - fb.ball_seq) AS balls_remaining
            FROM fact_ball fb
            JOIN first_innings_total fit ON fb.match_id = fit.match_id
            WHERE fb.innings = 2 AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        with_bands AS (
            SELECT *,
                CASE
                    WHEN balls_remaining <= 0 THEN NULL
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 15 THEN 'NEAR_IMPOSSIBLE'
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 12 THEN 'EXTREME'
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 10 THEN 'HIGH'
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 8  THEN 'BUILDING'
                    ELSE 'COMFORTABLE'
                END AS pressure_band
            FROM running_context
            WHERE balls_remaining > 0
        )
        SELECT
            wb.bowler_id AS player_id,
            dp.current_name AS player_name,
            wb.pressure_band,
            SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) AS legal_balls,
            ROUND(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) AS overs,
            SUM(wb.total_runs) AS runs_conceded,
            ROUND(SUM(wb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS economy,
            ROUND(SUM(CASE WHEN wb.batter_runs = 0 AND wb.extra_runs = 0 AND wb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS dot_ball_pct,
            ROUND(SUM(CASE WHEN wb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS boundary_conceded_pct,
            ROUND(SUM(CASE WHEN wb.batter_runs = 6 THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS six_conceded_pct,
            SUM(CASE WHEN wb.is_wicket AND wb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) AS wickets,
            ROUND(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) * 1.0 / NULLIF(SUM(CASE WHEN wb.is_wicket AND wb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END), 0), 2) AS bowling_strike_rate
        FROM with_bands wb
        JOIN dim_player dp ON wb.bowler_id = dp.player_id
        WHERE wb.pressure_band IS NOT NULL
        GROUP BY wb.bowler_id, dp.current_name, wb.pressure_band
        HAVING SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) >= 15
    """,
    )

    # ── 3. Dot Ball Sequences Under Pressure ─────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_pressure_dot_sequences",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        first_innings_total AS (
            SELECT fb.match_id, SUM(fb.total_runs) AS target_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches) AND fb.innings = 1
            GROUP BY fb.match_id
        ),
        running_context AS (
            SELECT fb.match_id, fb.innings, fb.ball_seq,
                fb.bowler_id, fb.batter_id,
                fb.batter_runs, fb.extra_runs, fb.total_runs,
                fb.is_legal_ball,
                SUM(fb.total_runs) OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS cumulative_runs,
                fit.target_runs + 1 AS target,
                (120 - fb.ball_seq) AS balls_remaining,
                CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 0 ELSE 1 END AS is_scoring,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 AND fb.is_legal_ball THEN 0 ELSE 1 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS scoring_group
            FROM fact_ball fb
            JOIN first_innings_total fit ON fb.match_id = fit.match_id
            WHERE fb.innings = 2 AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        pressure_balls AS (
            SELECT *,
                CASE WHEN balls_remaining > 0
                    THEN (target - cumulative_runs) * 6.0 / balls_remaining ELSE NULL END AS rrr
            FROM running_context
            WHERE balls_remaining > 0
              AND (target - cumulative_runs) * 6.0 / balls_remaining >= 10
        ),
        dot_runs AS (
            SELECT bowler_id, match_id, innings, scoring_group,
                COUNT(*) AS dots_in_sequence
            FROM pressure_balls WHERE is_scoring = 0
            GROUP BY bowler_id, match_id, innings, scoring_group
            HAVING COUNT(*) >= 2
        )
        SELECT
            dp.current_name AS bowler_name,
            dr.bowler_id,
            COUNT(*) AS dot_sequences,
            ROUND(AVG(dr.dots_in_sequence), 1) AS avg_dot_seq_length,
            MAX(dr.dots_in_sequence) AS max_dot_seq,
            SUM(dr.dots_in_sequence) AS total_dots_in_sequences
        FROM dot_runs dr
        JOIN dim_player dp ON dr.bowler_id = dp.player_id
        GROUP BY dr.bowler_id, dp.current_name
        HAVING COUNT(*) >= 3
        ORDER BY avg_dot_seq_length DESC
    """,
    )

    # ── 4. Boundary Sequences Under Pressure ─────────────────────────
    _dual_view(
        conn,
        "analytics_ipl_pressure_boundary_sequences",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        first_innings_total AS (
            SELECT fb.match_id, SUM(fb.total_runs) AS target_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches) AND fb.innings = 1
            GROUP BY fb.match_id
        ),
        running_context AS (
            SELECT fb.match_id, fb.innings, fb.ball_seq,
                fb.batter_id,
                fb.batter_runs, fb.extra_runs, fb.total_runs,
                fb.is_legal_ball,
                SUM(fb.total_runs) OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS cumulative_runs,
                fit.target_runs + 1 AS target,
                (120 - fb.ball_seq) AS balls_remaining,
                CASE WHEN fb.batter_runs IN (4, 6) THEN 0 ELSE 1 END AS is_non_boundary,
                SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 0 ELSE 1 END)
                    OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS non_boundary_group
            FROM fact_ball fb
            JOIN first_innings_total fit ON fb.match_id = fit.match_id
            WHERE fb.innings = 2 AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        pressure_balls AS (
            SELECT *,
                CASE WHEN balls_remaining > 0
                    THEN (target - cumulative_runs) * 6.0 / balls_remaining ELSE NULL END AS rrr
            FROM running_context
            WHERE balls_remaining > 0
              AND (target - cumulative_runs) * 6.0 / balls_remaining >= 10
        ),
        boundary_runs AS (
            SELECT batter_id, match_id, innings, non_boundary_group,
                COUNT(*) AS boundaries_in_sequence
            FROM pressure_balls WHERE is_non_boundary = 0
            GROUP BY batter_id, match_id, innings, non_boundary_group
            HAVING COUNT(*) >= 2
        )
        SELECT
            dp.current_name AS batter_name,
            br.batter_id,
            COUNT(*) AS boundary_sequences,
            ROUND(AVG(br.boundaries_in_sequence), 1) AS avg_boundary_seq_length,
            MAX(br.boundaries_in_sequence) AS max_boundary_seq,
            SUM(br.boundaries_in_sequence) AS total_boundaries_in_sequences
        FROM boundary_runs br
        JOIN dim_player dp ON br.batter_id = dp.player_id
        GROUP BY br.batter_id, dp.current_name
        HAVING COUNT(*) >= 2
        ORDER BY avg_boundary_seq_length DESC
    """,
    )

    # ── 5. Pressure Performance Deltas ───────────────────────────────
    # TKT-050 v2: Added sample-size weighting, death-overs bonus,
    # composite pressure_score, and IPL innings filter (>= 10).
    _dual_view(
        conn,
        "analytics_ipl_pressure_deltas",
        """
        WITH ipl_matches AS (
            SELECT dm.match_id
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League' {DATE_FILTER}
        ),
        -- IPL innings filter: only batters with >= 10 IPL innings
        ipl_innings_count AS (
            SELECT fb.batter_id, COUNT(DISTINCT fb.match_id) AS ipl_innings
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches)
              AND fb.is_legal_ball
            GROUP BY fb.batter_id
            HAVING COUNT(DISTINCT fb.match_id) >= 10
        ),
        first_innings_total AS (
            SELECT fb.match_id, SUM(fb.total_runs) AS target_runs
            FROM fact_ball fb
            WHERE fb.match_id IN (SELECT match_id FROM ipl_matches) AND fb.innings = 1
            GROUP BY fb.match_id
        ),
        running_context AS (
            SELECT fb.match_id, fb.innings, fb.ball_seq, fb.over,
                fb.batter_id, fb.bowler_id,
                fb.batter_runs, fb.extra_runs, fb.total_runs,
                fb.is_wicket, fb.wicket_type, fb.is_legal_ball,
                SUM(fb.total_runs) OVER (PARTITION BY fb.match_id, fb.innings ORDER BY fb.ball_seq) AS cumulative_runs,
                fit.target_runs + 1 AS target,
                (120 - fb.ball_seq) AS balls_remaining,
                -- Balls faced by this batter in this innings before this ball
                COALESCE(
                    SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) OVER (
                        PARTITION BY fb.match_id, fb.innings, fb.batter_id
                        ORDER BY fb.ball_seq
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ), 0
                ) AS batter_balls_before
            FROM fact_ball fb
            JOIN first_innings_total fit ON fb.match_id = fit.match_id
            WHERE fb.innings = 2 AND fb.match_id IN (SELECT match_id FROM ipl_matches)
        ),
        with_bands AS (
            SELECT *,
                CASE
                    WHEN balls_remaining <= 0 THEN NULL
                    WHEN (target - cumulative_runs) * 6.0 / balls_remaining >= 10 THEN 'HIGH_PRESSURE'
                    ELSE 'NORMAL'
                END AS pressure_group
            FROM running_context
            WHERE balls_remaining > 0
        ),
        -- Average balls faced before each pressure ball across all innings.
        -- Uses AVG across ALL pressure deliveries (not just the first entry
        -- point per innings) to better reflect how settled the batter typically
        -- is during high-pressure situations.
        batter_entry_context AS (
            SELECT batter_id,
                ROUND(AVG(batter_balls_before), 1) AS avg_balls_before_pressure,
                CASE
                    WHEN AVG(batter_balls_before) > 40 THEN 'DEEP_SET'
                    WHEN AVG(batter_balls_before) > 25 THEN 'SET'
                    WHEN AVG(batter_balls_before) >= 10 THEN 'BUILDING'
                    ELSE 'FRESH'
                END AS entry_context
            FROM with_bands
            WHERE pressure_group = 'HIGH_PRESSURE'
            GROUP BY batter_id
        ),
        batter_overall AS (
            SELECT wb.batter_id,
                SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) AS overall_balls,
                ROUND(SUM(wb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS overall_sr,
                ROUND(SUM(CASE WHEN wb.batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS overall_boundary_pct,
                ROUND(SUM(CASE WHEN wb.batter_runs = 0 AND wb.extra_runs = 0 AND wb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS overall_dot_pct
            FROM with_bands wb
            JOIN ipl_innings_count ic ON wb.batter_id = ic.batter_id
            GROUP BY wb.batter_id
            HAVING SUM(CASE WHEN wb.is_legal_ball THEN 1 ELSE 0 END) >= 50
        ),
        batter_pressure AS (
            SELECT batter_id,
                SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) AS pressure_balls,
                ROUND(SUM(batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS pressure_sr,
                ROUND(SUM(CASE WHEN batter_runs IN (4,6) THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS pressure_boundary_pct,
                ROUND(SUM(CASE WHEN batter_runs = 0 AND extra_runs = 0 AND is_legal_ball THEN 1 ELSE 0 END) * 100.0 / NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS pressure_dot_pct,
                -- Death overs (16-20 = over index 15-19) under pressure
                SUM(CASE WHEN is_legal_ball AND over >= 15 THEN 1 ELSE 0 END) AS death_pressure_balls,
                ROUND(SUM(CASE WHEN over >= 15 THEN batter_runs ELSE 0 END) * 100.0
                    / NULLIF(SUM(CASE WHEN is_legal_ball AND over >= 15 THEN 1 ELSE 0 END), 0), 2) AS death_pressure_sr
            FROM with_bands
            WHERE pressure_group = 'HIGH_PRESSURE'
            GROUP BY batter_id
            HAVING SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) >= 30
        )
        SELECT
            dp.current_name AS player_name,
            bo.batter_id AS player_id,
            'BATTER' AS role,
            bo.overall_balls,
            bp.pressure_balls,
            bp.death_pressure_balls,
            bp.death_pressure_sr,
            bo.overall_sr, bp.pressure_sr,
            ROUND((bp.pressure_sr - bo.overall_sr) / NULLIF(bo.overall_sr, 0) * 100, 1) AS sr_delta_pct,
            bo.overall_boundary_pct, bp.pressure_boundary_pct,
            ROUND((bp.pressure_boundary_pct - bo.overall_boundary_pct) / NULLIF(bo.overall_boundary_pct, 0) * 100, 1) AS boundary_delta_pct,
            bo.overall_dot_pct, bp.pressure_dot_pct,
            ROUND((bp.pressure_dot_pct - bo.overall_dot_pct) / NULLIF(bo.overall_dot_pct, 0) * 100, 1) AS dot_delta_pct,
            CASE
                WHEN bp.pressure_balls >= 100 THEN 'HIGH'
                WHEN bp.pressure_balls >= 50 THEN 'MEDIUM'
                ELSE 'LOW'
            END AS sample_confidence,
            CASE
                WHEN (bp.pressure_sr - bo.overall_sr) / NULLIF(bo.overall_sr, 0) * 100 >= 10 THEN 'CLUTCH'
                WHEN ABS((bp.pressure_sr - bo.overall_sr) / NULLIF(bo.overall_sr, 0) * 100) <= 5 THEN 'PRESSURE_PROOF'
                WHEN (bp.pressure_sr - bo.overall_sr) / NULLIF(bo.overall_sr, 0) * 100 <= -10 THEN 'PRESSURE_SENSITIVE'
                ELSE 'MODERATE'
            END AS pressure_rating,
            -- Composite weighted pressure score:
            -- sr_delta_pct * (1 + log2(pressure_balls/30)) * (1 + 0.3 * death_ratio)
            ROUND(
                ((bp.pressure_sr - bo.overall_sr) / NULLIF(bo.overall_sr, 0) * 100)
                * (1.0 + LOG2(bp.pressure_balls / 30.0))
                * (1.0 + 0.3 * (bp.death_pressure_balls * 1.0 / NULLIF(bp.pressure_balls, 0))),
                2
            ) AS pressure_score,
            -- Entry context: how set was the batter when entering pressure
            bec.avg_balls_before_pressure,
            bec.entry_context
        FROM batter_overall bo
        JOIN batter_pressure bp ON bo.batter_id = bp.batter_id
        JOIN dim_player dp ON bo.batter_id = dp.player_id
        LEFT JOIN batter_entry_context bec ON bo.batter_id = bec.batter_id
        ORDER BY pressure_score DESC
    """,
    )

    print("\n  Pressure Performance: 5 views x 2 variants = 10 views created.")


def verify_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Verify all views are working with sample queries."""

    print("\n" + "=" * 60)
    print("Verifying IPL 2026 Analytics Views...")
    print("=" * 60)

    # Test IPL career batting
    print("\nTop 5 IPL Run Scorers (Career):")
    print("-" * 70)
    result = conn.execute("""
        SELECT player_name, runs, innings, strike_rate, batting_average, sample_size
        FROM analytics_ipl_batting_career
        ORDER BY runs DESC
        LIMIT 5
    """).fetchall()
    print(f"{'Player':<25} {'Runs':>8} {'Inn':>6} {'SR':>8} {'Avg':>8} {'Sample':>10}")
    print("-" * 70)
    for row in result:
        avg_str = f"{row[4]:.2f}" if row[4] else "N/A"
        print(f"{row[0]:<25} {row[1]:>8,} {row[2]:>6} {row[3]:>8.2f} {avg_str:>8} {row[5]:>10}")

    # Test phase-wise batting for a known player
    print("\n\nKohli's IPL Phase-wise Batting:")
    print("-" * 70)
    result = conn.execute("""
        SELECT match_phase, innings, runs, balls_faced, strike_rate, boundary_pct
        FROM analytics_ipl_batter_phase
        WHERE player_name LIKE '%Kohli%'
        ORDER BY match_phase
    """).fetchall()
    print(f"{'Phase':<15} {'Inn':>6} {'Runs':>8} {'Balls':>8} {'SR':>8} {'Bound%':>10}")
    print("-" * 70)
    for row in result:
        print(f"{row[0]:<15} {row[1]:>6} {row[2]:>8} {row[3]:>8} {row[4]:>8.2f} {row[5]:>10.1f}")

    # Test squad batting view
    print("\n\nRCB 2026 Squad Batting (Top 5 by Price):")
    print("-" * 80)
    result = conn.execute("""
        SELECT player_name, role, price_cr, ipl_runs, ipl_sr, ipl_avg, ipl_sample_size
        FROM analytics_ipl_squad_batting
        WHERE team_name = 'Royal Challengers Bengaluru'
        ORDER BY price_cr DESC NULLS LAST
        LIMIT 5
    """).fetchall()
    print(
        f"{'Player':<25} {'Role':<12} {'Price':>8} {'Runs':>8} {'SR':>8} {'Avg':>8} {'Sample':>10}"
    )
    print("-" * 80)
    for row in result:
        price_str = f"{row[2]:.2f}" if row[2] else "N/A"
        runs_str = f"{row[3]:,}" if row[3] else "N/A"
        sr_str = f"{row[4]:.2f}" if row[4] else "N/A"
        avg_str = f"{row[5]:.2f}" if row[5] else "N/A"
        sample_str = row[6] if row[6] else "N/A"
        print(
            f"{row[0]:<25} {row[1]:<12} {price_str:>8} {runs_str:>8} {sr_str:>8} {avg_str:>8} {sample_str:>10}"
        )

    # Compare IPL vs All T20 for a player
    print("\n\nKohli: IPL vs All T20 (Phase-wise):")
    print("-" * 90)
    result = conn.execute("""
        SELECT
            'IPL' as scope,
            match_phase,
            innings,
            runs,
            strike_rate,
            boundary_pct
        FROM analytics_ipl_batter_phase
        WHERE player_name LIKE '%Kohli%'
        UNION ALL
        SELECT
            'All T20' as scope,
            match_phase,
            innings,
            runs,
            strike_rate,
            boundary_pct
        FROM analytics_t20_batter_phase
        WHERE player_name LIKE '%Kohli%'
        ORDER BY match_phase, scope
    """).fetchall()
    print(f"{'Scope':<10} {'Phase':<15} {'Inn':>6} {'Runs':>8} {'SR':>8} {'Bound%':>10}")
    print("-" * 90)
    for row in result:
        print(f"{row[0]:<10} {row[1]:<15} {row[2]:>6} {row[3]:>8} {row[4]:>8.2f} {row[5]:>10.1f}")

    return True


def create_tournament_weights_table(conn: duckdb.DuckDBPyConnection) -> None:
    """Create dim_tournament_weights table with Founder-approved weights (TKT-188).

    Materializes Jose Mourinho's 5-factor composite weights for all tracked
    tournaments. Geometric mean composite: W = PROD(f_i^w_i)^(1/SUM(w_i)).
    """

    print("\nCreating Tournament Weights table (TKT-188)...")

    conn.execute("""
        CREATE OR REPLACE TABLE dim_tournament_weights (
            tournament_name VARCHAR PRIMARY KEY,
            tier VARCHAR,
            composite_weight FLOAT,
            pqi_score FLOAT,
            competitiveness_score FLOAT,
            recency_score FLOAT,
            conditions_similarity FLOAT,
            sample_confidence FLOAT,
            seasons_count INTEGER,
            match_count INTEGER
        )
    """)

    # Founder-approved weights from TKT-187 final_weights_presentation.md
    conn.execute("""
        INSERT INTO dim_tournament_weights VALUES
        ('Indian Premier League',           '1A', 0.8721, 1.00, 0.53, 1.00, 1.00, 0.95, 18, 1169),
        ('Syed Mushtaq Ali Trophy',         '1B', 0.6454, 0.57, 0.36, 0.84, 0.73, 0.95,  9,  695),
        ('Big Bash League',                 '1C', 0.5261, 0.21, 0.49, 1.00, 0.50, 0.95, 15,  654),
        ('Pakistan Super League',           '1C', 0.5140, 0.18, 0.49, 0.90, 0.65, 0.95, 11,  314),
        ('The Hundred Men''s Competition',  '1C', 0.5035, 0.22, 0.53, 1.00, 0.40, 0.79,  5,  167),
        ('SA20',                            '1C', 0.5021, 0.25, 0.48, 1.00, 0.55, 0.60,  4,  121),
        ('ICC Men''s T20 World Cup',        '1C', 0.4984, 0.36, 0.40, 0.76, 0.50, 0.62,  3,  124),
        ('Vitality Blast',                  '1C', 0.4976, 0.20, 0.52, 0.84, 0.45, 0.95,  7,  835),
        ('Caribbean Premier League',        '1C', 0.4967, 0.17, 0.48, 1.00, 0.50, 0.95, 13,  407),
        ('International League T20',        '1C', 0.4889, 0.21, 0.45, 1.00, 0.55, 0.66,  4,  134),
        ('Major League Cricket',            '2',  0.4233, 0.21, 0.46, 1.00, 0.45, 0.38,  3,   75),
        ('Lanka Premier League',            '2',  0.3982, 0.10, 0.52, 0.84, 0.60, 0.59,  5,  119),
        ('CSA T20 Challenge',               '2',  0.3834, 0.07, 0.55, 0.84, 0.55, 0.75,  7,  154),
        ('Super Smash',                     '2',  0.3633, 0.05, 0.50, 1.00, 0.40, 0.95,  9,  256)
    """)

    # Verify
    count = conn.execute("SELECT COUNT(*) FROM dim_tournament_weights").fetchone()[0]
    print(f"  - dim_tournament_weights: {count} tournaments loaded")


def create_weighted_composite_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create weighted cross-tournament composite views (TKT-190).

    Joins per-tournament player stats with dim_tournament_weights to produce
    weighted composite batting/bowling profiles. Used for:
    - Small-sample IPL player enrichment (<300 bat balls, <200 bowl balls)
    - Uncapped player confidence scoring
    - CricPom feed data layer
    """

    print("\nCreating Weighted Composite views (TKT-190)...")

    # Weighted composite batting: per player, aggregated across tournaments
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_weighted_composite_batting AS
        WITH per_tournament AS (
            SELECT
                fb.batter_id AS player_id,
                dp.current_name AS player_name,
                dt.tournament_name,
                dtw.composite_weight,
                dtw.tier,
                COUNT(DISTINCT fb.match_id) AS matches,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS balls_faced,
                SUM(fb.batter_runs) AS runs,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN
                    ('run out', 'retired hurt', 'retired out', 'obstructing the field')
                    THEN 1 ELSE 0 END) AS dismissals,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) AS fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) AS sixes
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_tournament_weights dtw ON dt.tournament_name = dtw.tournament_name
            JOIN dim_player dp ON fb.batter_id = dp.player_id
            WHERE fb.is_legal_ball = true
            GROUP BY fb.batter_id, dp.current_name, dt.tournament_name,
                     dtw.composite_weight, dtw.tier
            HAVING balls_faced >= 20
        )
        SELECT
            player_id,
            player_name,
            COUNT(DISTINCT tournament_name) AS tournaments_played,
            SUM(matches) AS total_matches,
            SUM(balls_faced) AS total_balls,
            SUM(runs) AS total_runs,
            -- Weighted strike rate: SUM(runs * weight) / SUM(balls * weight) * 100
            ROUND(SUM(runs * composite_weight) * 100.0
                / NULLIF(SUM(balls_faced * composite_weight), 0), 2) AS weighted_sr,
            -- Weighted average: SUM(runs * weight) / SUM(dismissals * weight)
            ROUND(SUM(runs * composite_weight)
                / NULLIF(SUM(dismissals * composite_weight), 0), 2) AS weighted_avg,
            -- Raw (unweighted) SR for comparison
            ROUND(SUM(runs) * 100.0 / NULLIF(SUM(balls_faced), 0), 2) AS raw_sr,
            -- Weighted boundary %
            ROUND(SUM((fours + sixes) * composite_weight) * 100.0
                / NULLIF(SUM(balls_faced * composite_weight), 0), 2) AS weighted_boundary_pct,
            -- Confidence score: weighted sum of balls / max possible
            ROUND(SUM(balls_faced * composite_weight)
                / NULLIF(SUM(balls_faced), 0), 4) AS avg_weight,
            -- Top 3 tournaments by balls faced
            LIST(STRUCT_PACK(
                t := tournament_name,
                w := composite_weight,
                b := balls_faced,
                sr := ROUND(runs * 100.0 / NULLIF(balls_faced, 0), 1)
            ) ORDER BY balls_faced DESC)[:3] AS top_tournaments
        FROM per_tournament
        GROUP BY player_id, player_name
    """)
    print("  - analytics_weighted_composite_batting created")

    # Weighted composite bowling
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_weighted_composite_bowling AS
        WITH per_tournament AS (
            SELECT
                fb.bowler_id AS player_id,
                dp.current_name AS player_name,
                dt.tournament_name,
                dtw.composite_weight,
                dtw.tier,
                COUNT(DISTINCT fb.match_id) AS matches,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS legal_balls,
                SUM(fb.total_runs) AS runs_conceded,
                SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball
                    THEN 1 ELSE 0 END) AS dot_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_tournament_weights dtw ON dt.tournament_name = dtw.tournament_name
            JOIN dim_player dp ON fb.bowler_id = dp.player_id
            WHERE fb.is_legal_ball = true
            GROUP BY fb.bowler_id, dp.current_name, dt.tournament_name,
                     dtw.composite_weight, dtw.tier
            HAVING legal_balls >= 12
        )
        SELECT
            player_id,
            player_name,
            COUNT(DISTINCT tournament_name) AS tournaments_played,
            SUM(matches) AS total_matches,
            SUM(legal_balls) AS total_balls,
            SUM(wickets) AS total_wickets,
            -- Weighted economy: SUM(runs * weight) / SUM(overs * weight) * 6
            ROUND(SUM(runs_conceded * composite_weight) * 6.0
                / NULLIF(SUM(legal_balls * composite_weight), 0), 2) AS weighted_economy,
            -- Weighted SR: SUM(balls * weight) / SUM(wickets * weight)
            ROUND(SUM(legal_balls * composite_weight)
                / NULLIF(SUM(wickets * composite_weight), 0), 2) AS weighted_bowling_sr,
            -- Raw economy for comparison
            ROUND(SUM(runs_conceded) * 6.0 / NULLIF(SUM(legal_balls), 0), 2) AS raw_economy,
            -- Weighted dot ball %
            ROUND(SUM(dot_balls * composite_weight) * 100.0
                / NULLIF(SUM(legal_balls * composite_weight), 0), 2) AS weighted_dot_pct,
            -- Avg weight
            ROUND(SUM(legal_balls * composite_weight)
                / NULLIF(SUM(legal_balls), 0), 4) AS avg_weight,
            -- Top 3 tournaments
            LIST(STRUCT_PACK(
                t := tournament_name,
                w := composite_weight,
                b := legal_balls,
                econ := ROUND(runs_conceded * 6.0 / NULLIF(legal_balls, 0), 1)
            ) ORDER BY legal_balls DESC)[:3] AS top_tournaments
        FROM per_tournament
        GROUP BY player_id, player_name
    """)
    print("  - analytics_weighted_composite_bowling created")

    # Small-sample IPL player enrichment view (players with <300 bat / <200 bowl balls in IPL 2023+)
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_small_sample_enrichment AS
        WITH ipl_bat AS (
            SELECT
                fb.batter_id AS player_id,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS ipl_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            WHERE dm.tournament_id = 'indian_premier_league'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.batter_id
        ),
        ipl_bowl AS (
            SELECT
                fb.bowler_id AS player_id,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS ipl_balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            WHERE dm.tournament_id = 'indian_premier_league'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.bowler_id
        )
        SELECT
            sq.player_id,
            sq.player_name,
            sq.team_name,
            sq.role,
            COALESCE(ib.ipl_balls, 0) AS ipl_bat_balls,
            COALESCE(ibl.ipl_balls, 0) AS ipl_bowl_balls,
            CASE WHEN COALESCE(ib.ipl_balls, 0) < 300 THEN true ELSE false END AS bat_small_sample,
            CASE WHEN COALESCE(ibl.ipl_balls, 0) < 200 THEN true ELSE false END AS bowl_small_sample,
            wcb.weighted_sr AS cross_tournament_bat_sr,
            wcb.weighted_avg AS cross_tournament_bat_avg,
            wcb.weighted_boundary_pct AS cross_tournament_boundary_pct,
            wcb.tournaments_played AS bat_tournaments,
            wcb.total_balls AS bat_total_t20_balls,
            wcbl.weighted_economy AS cross_tournament_bowl_econ,
            wcbl.weighted_bowling_sr AS cross_tournament_bowl_sr,
            wcbl.weighted_dot_pct AS cross_tournament_dot_pct,
            wcbl.tournaments_played AS bowl_tournaments,
            wcbl.total_balls AS bowl_total_t20_balls
        FROM ipl_2026_squads sq
        LEFT JOIN ipl_bat ib ON sq.player_id = ib.player_id
        LEFT JOIN ipl_bowl ibl ON sq.player_id = ibl.player_id
        LEFT JOIN analytics_weighted_composite_batting wcb ON sq.player_id = wcb.player_id
        LEFT JOIN analytics_weighted_composite_bowling wcbl ON sq.player_id = wcbl.player_id
        WHERE COALESCE(ib.ipl_balls, 0) < 300 OR COALESCE(ibl.ipl_balls, 0) < 200
    """)
    print("  - analytics_ipl_small_sample_enrichment created")


def create_team_phase_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create team-level phase approach views (Item 3 / TKT-052).

    Aggregated team batting and bowling by phase and season (2023+),
    plus batting order balance analysis.
    """

    print("\nCreating Team Phase Approach views (TKT-052)...")

    # Team Phase Batting (per season)
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_team_phase_batting_since2023 AS
        SELECT
            dtt.team_name AS batting_team,
            dm.season,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) AS matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS legal_balls,
            SUM(fb.batter_runs) AS runs,
            ROUND(SUM(fb.batter_runs) * 100.0 /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 1) AS strike_rate,
            ROUND(SUM(fb.batter_runs) * 6.0 /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS run_rate,
            ROUND(SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0 /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 1) AS boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 1) AS dot_ball_pct,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets_lost
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
        JOIN dim_team dtt ON fb.batting_team_id = dtt.team_id
        WHERE dtr.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
        GROUP BY dtt.team_name, dm.season, fb.match_phase
    """)

    # Team Phase Bowling (per season)
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_team_phase_bowling_since2023 AS
        SELECT
            dtt.team_name AS bowling_team,
            dm.season,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) AS matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) AS legal_balls,
            SUM(fb.batter_runs + fb.extra_runs) AS runs_conceded,
            ROUND((SUM(fb.batter_runs + fb.extra_runs) * 6.0) /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) AS economy,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) AS wickets_taken,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) * 100.0 /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 1) AS dot_ball_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0 /
                NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 1) AS boundary_conceded_pct
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
        JOIN dim_team dtt ON fb.bowling_team_id = dtt.team_id
        WHERE dtr.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
        GROUP BY dtt.team_name, dm.season, fb.match_phase
    """)

    # Batting Order Balance (top 3 / middle / lower order contribution)
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_team_batting_order_since2023 AS
        WITH first_ball AS (
            SELECT
                fb.match_id,
                fb.innings,
                fb.batter_id,
                fb.batting_team_id,
                dm.season,
                MIN(fb.ball_seq) AS first_ball_seq
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
            GROUP BY fb.match_id, fb.innings, fb.batter_id, fb.batting_team_id, dm.season
        ),
        batter_order AS (
            SELECT
                match_id, innings, batter_id, batting_team_id, season,
                ROW_NUMBER() OVER (
                    PARTITION BY match_id, innings, batting_team_id
                    ORDER BY first_ball_seq
                ) AS batting_position
            FROM first_ball
        ),
        classified AS (
            SELECT
                dtt.team_name AS batting_team,
                bo.season,
                CASE
                    WHEN bo.batting_position <= 3 THEN 'top_order'
                    WHEN bo.batting_position <= 5 THEN 'middle_order'
                    ELSE 'lower_order'
                END AS order_segment,
                fb.batter_runs,
                fb.is_legal_ball
            FROM fact_ball fb
            JOIN batter_order bo ON fb.match_id = bo.match_id
                AND fb.innings = bo.innings
                AND fb.batter_id = bo.batter_id
            JOIN dim_team dtt ON fb.batting_team_id = dtt.team_id
        )
        SELECT
            batting_team,
            season,
            order_segment,
            SUM(batter_runs) AS runs,
            SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) AS balls,
            ROUND(SUM(batter_runs) * 100.0 /
                NULLIF(SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END), 0), 1) AS strike_rate
        FROM classified
        GROUP BY batting_team, season, order_segment
    """)

    # Verify
    for vw in [
        "analytics_ipl_team_phase_batting_since2023",
        "analytics_ipl_team_phase_bowling_since2023",
        "analytics_ipl_team_batting_order_since2023",
    ]:
        count = conn.execute(f"SELECT COUNT(*) FROM {vw}").fetchone()[0]
        print(f"  - {vw}: {count} rows")


def create_recent_form_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create recent form views (rolling last 10/20 matches) for batters and bowlers.

    EPIC-013: Provides form-vs-career deltas for IPL 2026 squad members.
    Uses DENSE_RANK on match_id (by match_date DESC) to identify each player's
    most recent N IPL matches, then aggregates batting/bowling stats.
    """

    print("\nCreating Recent Form views (EPIC-013)...")

    # ── View 1: Batter Recent Form ──────────────────────────────
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batter_recent_form AS
        WITH ipl_balls AS (
            SELECT
                fb.batter_id,
                fb.match_id,
                dm.match_date,
                fb.batter_runs,
                fb.is_legal_ball,
                fb.is_wicket,
                fb.player_out_id
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        match_ranked AS (
            SELECT
                batter_id,
                match_id,
                DENSE_RANK() OVER (
                    PARTITION BY batter_id
                    ORDER BY MAX(match_date) DESC, match_id DESC
                ) AS match_rank
            FROM ipl_balls
            GROUP BY batter_id, match_id
        ),
        tagged AS (
            SELECT
                ib.*,
                mr.match_rank
            FROM ipl_balls ib
            JOIN match_ranked mr
              ON ib.batter_id = mr.batter_id
             AND ib.match_id  = mr.match_id
        ),
        agg AS (
            SELECT
                batter_id,
                -- Last 10 matches
                COUNT(DISTINCT CASE WHEN match_rank <= 10 THEN match_id END)
                    AS last10_innings,
                SUM(CASE WHEN match_rank <= 10 THEN batter_runs ELSE 0 END)
                    AS last10_runs,
                SUM(CASE WHEN match_rank <= 10 AND is_legal_ball THEN 1 ELSE 0 END)
                    AS last10_balls,
                SUM(CASE WHEN match_rank <= 10 AND is_wicket
                         AND player_out_id = batter_id THEN 1 ELSE 0 END)
                    AS last10_dismissals,
                SUM(CASE WHEN match_rank <= 10 AND batter_runs IN (4, 6)
                         THEN 1 ELSE 0 END)
                    AS last10_boundaries,
                SUM(CASE WHEN match_rank <= 10 AND batter_runs = 0
                         AND is_legal_ball THEN 1 ELSE 0 END)
                    AS last10_dots,
                -- Last 20 matches
                COUNT(DISTINCT CASE WHEN match_rank <= 20 THEN match_id END)
                    AS last20_innings,
                SUM(CASE WHEN match_rank <= 20 THEN batter_runs ELSE 0 END)
                    AS last20_runs,
                SUM(CASE WHEN match_rank <= 20 AND is_legal_ball THEN 1 ELSE 0 END)
                    AS last20_balls,
                SUM(CASE WHEN match_rank <= 20 AND is_wicket
                         AND player_out_id = batter_id THEN 1 ELSE 0 END)
                    AS last20_dismissals,
                SUM(CASE WHEN match_rank <= 20 AND batter_runs IN (4, 6)
                         THEN 1 ELSE 0 END)
                    AS last20_boundaries,
                SUM(CASE WHEN match_rank <= 20 AND batter_runs = 0
                         AND is_legal_ball THEN 1 ELSE 0 END)
                    AS last20_dots,
                -- Career (all IPL)
                SUM(batter_runs) AS career_runs,
                SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) AS career_balls,
                SUM(CASE WHEN is_wicket AND player_out_id = batter_id
                         THEN 1 ELSE 0 END) AS career_dismissals
            FROM tagged
            GROUP BY batter_id
        )
        SELECT
            sq.team_name,
            dp.player_id   AS batter_id,
            dp.current_name AS batter_name,
            -- Last 10
            a.last10_innings,
            a.last10_runs,
            a.last10_balls,
            ROUND(a.last10_runs * 100.0
                  / NULLIF(a.last10_balls, 0), 2)          AS last10_sr,
            ROUND(a.last10_runs * 1.0
                  / NULLIF(a.last10_dismissals, 0), 2)     AS last10_avg,
            ROUND(a.last10_boundaries * 100.0
                  / NULLIF(a.last10_balls, 0), 2)           AS last10_boundary_pct,
            ROUND(a.last10_dots * 100.0
                  / NULLIF(a.last10_balls, 0), 2)           AS last10_dot_pct,
            -- Last 20
            a.last20_innings,
            a.last20_runs,
            a.last20_balls,
            ROUND(a.last20_runs * 100.0
                  / NULLIF(a.last20_balls, 0), 2)          AS last20_sr,
            ROUND(a.last20_runs * 1.0
                  / NULLIF(a.last20_dismissals, 0), 2)     AS last20_avg,
            ROUND(a.last20_boundaries * 100.0
                  / NULLIF(a.last20_balls, 0), 2)           AS last20_boundary_pct,
            ROUND(a.last20_dots * 100.0
                  / NULLIF(a.last20_balls, 0), 2)           AS last20_dot_pct,
            -- Career
            ROUND(a.career_runs * 100.0
                  / NULLIF(a.career_balls, 0), 2)           AS career_sr,
            ROUND(a.career_runs * 1.0
                  / NULLIF(a.career_dismissals, 0), 2)     AS career_avg,
            -- Form vs career deltas
            ROUND((a.last10_runs * 100.0 / NULLIF(a.last10_balls, 0))
                - (a.career_runs * 100.0 / NULLIF(a.career_balls, 0)), 2)
                                                            AS sr_delta_last10,
            ROUND((a.last20_runs * 100.0 / NULLIF(a.last20_balls, 0))
                - (a.career_runs * 100.0 / NULLIF(a.career_balls, 0)), 2)
                                                            AS sr_delta_last20
        FROM agg a
        JOIN dim_player dp ON a.batter_id = dp.player_id
        JOIN ipl_2026_squads sq ON dp.player_id = sq.player_id
    """)
    print("  - analytics_ipl_batter_recent_form")

    # ── View 2: Bowler Recent Form ──────────────────────────────
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_recent_form AS
        WITH ipl_balls AS (
            SELECT
                fb.bowler_id,
                fb.match_id,
                dm.match_date,
                fb.batter_runs,
                fb.extra_runs,
                fb.total_runs,
                fb.is_legal_ball,
                fb.is_wicket,
                fb.wicket_type
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        match_ranked AS (
            SELECT
                bowler_id,
                match_id,
                DENSE_RANK() OVER (
                    PARTITION BY bowler_id
                    ORDER BY MAX(match_date) DESC, match_id DESC
                ) AS match_rank
            FROM ipl_balls
            GROUP BY bowler_id, match_id
        ),
        tagged AS (
            SELECT
                ib.*,
                mr.match_rank
            FROM ipl_balls ib
            JOIN match_ranked mr
              ON ib.bowler_id = mr.bowler_id
             AND ib.match_id  = mr.match_id
        ),
        agg AS (
            SELECT
                bowler_id,
                -- Last 10 matches
                COUNT(DISTINCT CASE WHEN match_rank <= 10 THEN match_id END)
                    AS last10_matches,
                SUM(CASE WHEN match_rank <= 10 AND is_legal_ball THEN 1 ELSE 0 END)
                    AS last10_balls,
                SUM(CASE WHEN match_rank <= 10 THEN total_runs ELSE 0 END)
                    AS last10_runs_conceded,
                SUM(CASE WHEN match_rank <= 10 AND is_wicket
                         AND wicket_type NOT IN (
                             'run out', 'retired hurt',
                             'retired out', 'obstructing the field')
                         THEN 1 ELSE 0 END)
                    AS last10_wickets,
                SUM(CASE WHEN match_rank <= 10 AND batter_runs = 0
                         AND extra_runs = 0 THEN 1 ELSE 0 END)
                    AS last10_dots,
                -- Last 20 matches
                COUNT(DISTINCT CASE WHEN match_rank <= 20 THEN match_id END)
                    AS last20_matches,
                SUM(CASE WHEN match_rank <= 20 AND is_legal_ball THEN 1 ELSE 0 END)
                    AS last20_balls,
                SUM(CASE WHEN match_rank <= 20 THEN total_runs ELSE 0 END)
                    AS last20_runs_conceded,
                SUM(CASE WHEN match_rank <= 20 AND is_wicket
                         AND wicket_type NOT IN (
                             'run out', 'retired hurt',
                             'retired out', 'obstructing the field')
                         THEN 1 ELSE 0 END)
                    AS last20_wickets,
                SUM(CASE WHEN match_rank <= 20 AND batter_runs = 0
                         AND extra_runs = 0 THEN 1 ELSE 0 END)
                    AS last20_dots,
                -- Career (all IPL)
                SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END)
                    AS career_balls,
                SUM(total_runs) AS career_runs_conceded,
                SUM(CASE WHEN is_wicket
                         AND wicket_type NOT IN (
                             'run out', 'retired hurt',
                             'retired out', 'obstructing the field')
                         THEN 1 ELSE 0 END)
                    AS career_wickets
            FROM tagged
            GROUP BY bowler_id
        )
        SELECT
            sq.team_name,
            dp.player_id    AS bowler_id,
            dp.current_name AS bowler_name,
            -- Last 10
            a.last10_matches,
            ROUND(a.last10_balls / 6.0, 1)                 AS last10_overs,
            a.last10_wickets,
            ROUND(a.last10_runs_conceded * 6.0
                  / NULLIF(a.last10_balls, 0), 2)          AS last10_economy,
            ROUND(a.last10_balls * 1.0
                  / NULLIF(a.last10_wickets, 0), 2)        AS last10_sr,
            ROUND(a.last10_dots * 100.0
                  / NULLIF(a.last10_balls, 0), 2)          AS last10_dot_pct,
            -- Last 20
            a.last20_matches,
            ROUND(a.last20_balls / 6.0, 1)                 AS last20_overs,
            a.last20_wickets,
            ROUND(a.last20_runs_conceded * 6.0
                  / NULLIF(a.last20_balls, 0), 2)          AS last20_economy,
            ROUND(a.last20_balls * 1.0
                  / NULLIF(a.last20_wickets, 0), 2)        AS last20_sr,
            ROUND(a.last20_dots * 100.0
                  / NULLIF(a.last20_balls, 0), 2)          AS last20_dot_pct,
            -- Career
            ROUND(a.career_runs_conceded * 6.0
                  / NULLIF(a.career_balls, 0), 2)          AS career_economy,
            ROUND(a.career_balls * 1.0
                  / NULLIF(a.career_wickets, 0), 2)        AS career_sr,
            -- Form vs career deltas
            ROUND((a.last10_runs_conceded * 6.0 / NULLIF(a.last10_balls, 0))
                - (a.career_runs_conceded * 6.0 / NULLIF(a.career_balls, 0)), 2)
                                                            AS economy_delta_last10,
            ROUND((a.last20_runs_conceded * 6.0 / NULLIF(a.last20_balls, 0))
                - (a.career_runs_conceded * 6.0 / NULLIF(a.career_balls, 0)), 2)
                                                            AS economy_delta_last20
        FROM agg a
        JOIN dim_player dp ON a.bowler_id = dp.player_id
        JOIN ipl_2026_squads sq ON dp.player_id = sq.player_id
    """)
    print("  - analytics_ipl_bowler_recent_form")

    # Verify row counts
    for vw in [
        "analytics_ipl_batter_recent_form",
        "analytics_ipl_bowler_recent_form",
    ]:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {vw}").fetchone()[0]
            print(f"  - {vw}: {count} rows")
        except Exception as exc:
            print(f"  ERROR verifying {vw}: {exc}")


def create_matchup_matrix_views(conn: duckdb.DuckDBPyConnection) -> None:
    """Create team-level and player-level matchup matrix views.

    EPIC-013: Cross-team and head-to-head matchup analysis
    filtered to IPL 2026 squad members (since 2023).
    """

    print("\nCreating Matchup Matrix views (EPIC-013)...")

    # ── View 3: Team Matchup Batting ────────────────────────────
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_team_matchup_batting AS
        SELECT
            sq_bat.team_name                               AS batting_team,
            sq_bowl.team_name                              AS bowling_team,
            COUNT(DISTINCT fb.batter_id)                   AS batters_faced,
            COUNT(DISTINCT fb.bowler_id)                   AS bowlers_faced,
            COUNT(DISTINCT fb.match_id)                    AS matches,
            SUM(fb.batter_runs)                            AS total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END)
                                                           AS total_balls,
            ROUND(SUM(fb.batter_runs) * 100.0
                  / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2)
                                                           AS strike_rate,
            ROUND(SUM(fb.batter_runs) * 6.0
                  / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2)
                                                           AS run_rate,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id
                     THEN 1 ELSE 0 END)                    AS wickets,
            SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END)
                                                           AS boundaries,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball
                     THEN 1 ELSE 0 END)                    AS dot_balls,
            ROUND(SUM(CASE WHEN fb.batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0
                  / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2)
                                                           AS boundary_pct,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball
                           THEN 1 ELSE 0 END) * 100.0
                  / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2)
                                                           AS dot_ball_pct
        FROM fact_ball fb
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        JOIN ipl_2026_squads sq_bat  ON fb.batter_id = sq_bat.player_id
        JOIN ipl_2026_squads sq_bowl ON fb.bowler_id = sq_bowl.player_id
        WHERE dt.tournament_name = 'Indian Premier League'
          AND dm.match_date >= '{IPL_MIN_DATE}'
          AND sq_bat.team_name != sq_bowl.team_name
        GROUP BY sq_bat.team_name, sq_bowl.team_name
    """)
    print("  - analytics_ipl_team_matchup_batting")

    # ── View 4: Player Matchup Matrix ───────────────────────────
    conn.execute(f"""
        CREATE OR REPLACE VIEW analytics_ipl_player_matchup_matrix AS
        WITH raw AS (
            SELECT
                fb.batter_id,
                dp_bat.current_name  AS batter_name,
                sq_bat.team_name     AS batter_team,
                fb.bowler_id,
                dp_bowl.current_name AS bowler_name,
                sq_bowl.team_name    AS bowler_team,
                fb.batter_runs,
                fb.is_legal_ball,
                fb.is_wicket,
                fb.player_out_id
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_player dp_bat  ON fb.batter_id  = dp_bat.player_id
            JOIN dim_player dp_bowl ON fb.bowler_id   = dp_bowl.player_id
            JOIN ipl_2026_squads sq_bat  ON fb.batter_id = sq_bat.player_id
            JOIN ipl_2026_squads sq_bowl ON fb.bowler_id = sq_bowl.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '{IPL_MIN_DATE}'
              AND fb.is_legal_ball = TRUE
        )
        SELECT
            batter_id,
            batter_name,
            batter_team,
            bowler_id,
            bowler_name,
            bowler_team,
            COUNT(*)                                       AS balls,
            SUM(batter_runs)                               AS runs,
            SUM(CASE WHEN is_wicket AND player_out_id = batter_id
                     THEN 1 ELSE 0 END)                    AS dismissals,
            ROUND(SUM(batter_runs) * 100.0
                  / NULLIF(COUNT(*), 0), 2)                AS strike_rate,
            ROUND(SUM(batter_runs) * 1.0
                  / NULLIF(SUM(CASE WHEN is_wicket AND player_out_id = batter_id
                                    THEN 1 ELSE 0 END), 0), 2)
                                                           AS average,
            SUM(CASE WHEN batter_runs = 0 THEN 1 ELSE 0 END)
                                                           AS dots,
            SUM(CASE WHEN batter_runs IN (4, 6) THEN 1 ELSE 0 END)
                                                           AS boundaries,
            ROUND(SUM(CASE WHEN batter_runs = 0 THEN 1 ELSE 0 END) * 100.0
                  / NULLIF(COUNT(*), 0), 2)                AS dot_pct,
            ROUND(SUM(CASE WHEN batter_runs IN (4, 6) THEN 1 ELSE 0 END) * 100.0
                  / NULLIF(COUNT(*), 0), 2)                AS boundary_pct,
            CASE WHEN COUNT(*) < 10 THEN 'LOW'
                 WHEN COUNT(*) < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END                           AS sample_size
        FROM raw
        GROUP BY batter_id, batter_name, batter_team,
                 bowler_id, bowler_name, bowler_team
        HAVING COUNT(*) >= 10
    """)
    print("  - analytics_ipl_player_matchup_matrix")

    # Verify row counts
    for vw in [
        "analytics_ipl_team_matchup_batting",
        "analytics_ipl_player_matchup_matrix",
    ]:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {vw}").fetchone()[0]
            print(f"  - {vw}: {count} rows")
        except Exception as exc:
            print(f"  ERROR verifying {vw}: {exc}")


def main() -> int:
    """Main entry point."""

    print("=" * 60)
    print("Cricket Playbook - IPL 2026 Analytics Layer")
    print("Author: Stephen Curry")
    print("Version: 2.2.0")
    print("=" * 60)
    print()

    # Connect to database
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run ingest.py first to create the database.")
        return 1

    conn = duckdb.connect(str(DB_PATH))

    # Create all views
    create_squad_tables(conn)
    create_ipl_batting_views(conn)
    create_ipl_bowling_views(conn)
    create_phase_matchup_views(conn)
    create_team_venue_views(conn)
    create_t20_comparison_views(conn)
    create_squad_integration_views(conn)
    create_percentile_views(conn)
    create_benchmark_views(conn)
    create_standardized_ipl_views(conn)
    create_film_room_views(conn)
    create_pressure_performance_views(conn)
    create_tournament_weights_table(conn)
    create_weighted_composite_views(conn)
    create_team_phase_views(conn)
    create_recent_form_views(conn)
    create_matchup_matrix_views(conn)

    # Verify
    verify_views(conn)

    # Count views
    result = conn.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_type = 'VIEW' AND (table_name LIKE 'analytics_ipl_%' OR table_name LIKE 'analytics_t20_%')
    """).fetchone()

    tables = conn.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_type = 'BASE TABLE' AND table_name LIKE 'ipl_2026_%'
    """).fetchone()

    print()
    print("=" * 60)
    print("IPL Analytics layer complete:")
    print(f"  - {tables[0]} squad data tables created")
    print(f"  - {result[0]} analytics views created")
    print("=" * 60)

    conn.close()
    return 0


if __name__ == "__main__":
    exit(main())
