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

import duckdb
from pathlib import Path
from datetime import datetime

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "cricket_playbook.duckdb"
SQUADS_CSV = DATA_DIR / "ipl_2026_squads.csv"
CONTRACTS_CSV = DATA_DIR / "ipl_2026_player_contracts.csv"


def create_squad_tables(conn: duckdb.DuckDBPyConnection):
    """Load IPL 2026 squad data into tables."""

    print("Loading IPL 2026 squad data...")

    # Load squads CSV
    if SQUADS_CSV.exists():
        conn.execute(f"""
            CREATE OR REPLACE TABLE ipl_2026_squads AS
            SELECT * FROM read_csv_auto('{SQUADS_CSV}')
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
            SELECT * FROM read_csv_auto('{CONTRACTS_CSV}')
        """)
        print("  - ipl_2026_contracts table created")
    else:
        print(f"  WARNING: {CONTRACTS_CSV} not found")


def create_ipl_batting_views(conn: duckdb.DuckDBPyConnection):
    """Create IPL-specific batting analytics views."""

    print("\nCreating IPL-specific batting views...")

    # IPL Career Batting Stats
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_batting_career AS
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
            COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown') as bowler_type,
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
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown')
    """)
    print("  - analytics_ipl_batter_vs_bowler_type")


def create_ipl_bowling_views(conn: duckdb.DuckDBPyConnection):
    """Create IPL-specific bowling analytics views."""

    print("\nCreating IPL-specific bowling views...")

    # IPL Career Bowling Stats
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowling_career AS
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


def create_phase_matchup_views(conn: duckdb.DuckDBPyConnection):
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
            COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown') as bowler_type,
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
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown'), fb.match_phase
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


def create_team_venue_views(conn: duckdb.DuckDBPyConnection):
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
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_ipl_bowler_phase_distribution AS
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


def create_t20_comparison_views(conn: duckdb.DuckDBPyConnection):
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
            COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown') as bowler_type,
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
        GROUP BY dp_bat.player_id, dp_bat.current_name, COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown')
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


def create_squad_integration_views(conn: duckdb.DuckDBPyConnection):
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


def create_percentile_views(conn: duckdb.DuckDBPyConnection):
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


def create_benchmark_views(conn: duckdb.DuckDBPyConnection):
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
            COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown') as bowler_type,
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
        GROUP BY COALESCE(sq.bowling_style, bc.bowling_style, 'Unknown')
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


def verify_views(conn: duckdb.DuckDBPyConnection):
    """Verify all views are working with sample queries."""

    print("\n" + "="*60)
    print("Verifying IPL 2026 Analytics Views...")
    print("="*60)

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
    print(f"{'Player':<25} {'Role':<12} {'Price':>8} {'Runs':>8} {'SR':>8} {'Avg':>8} {'Sample':>10}")
    print("-" * 80)
    for row in result:
        price_str = f"{row[2]:.2f}" if row[2] else "N/A"
        runs_str = f"{row[3]:,}" if row[3] else "N/A"
        sr_str = f"{row[4]:.2f}" if row[4] else "N/A"
        avg_str = f"{row[5]:.2f}" if row[5] else "N/A"
        sample_str = row[6] if row[6] else "N/A"
        print(f"{row[0]:<25} {row[1]:<12} {price_str:>8} {runs_str:>8} {sr_str:>8} {avg_str:>8} {sample_str:>10}")

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


def main():
    """Main entry point."""

    print("="*60)
    print("Cricket Playbook - IPL 2026 Analytics Layer")
    print("Author: Stephen Curry")
    print("Version: 2.1.0")
    print("="*60)
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
    print("="*60)
    print(f"IPL Analytics layer complete:")
    print(f"  - {tables[0]} squad data tables created")
    print(f"  - {result[0]} analytics views created")
    print("="*60)

    conn.close()
    return 0


if __name__ == "__main__":
    exit(main())
