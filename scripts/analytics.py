"""
Cricket Playbook - Analytics Layer
===================================
Author: Stephen Curry (Analytics Specialist)
Version: 1.0.0

Creates analytical views for batting and bowling metrics.
Follows Andy Flower's recommendations:
- Sample size warnings (<10 innings, <100 balls)
- Phase-based analysis (powerplay/middle/death)
- Strike rate always shown with balls faced context
"""

import duckdb
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "cricket_playbook.duckdb"


def create_batting_views(conn: duckdb.DuckDBPyConnection):
    """Create batting analytics views."""

    print("Creating batting analytics views...")

    # Player career batting stats
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_batting_career AS
        WITH batting_stats AS (
            SELECT
                fb.batter_id as player_id,
                COUNT(DISTINCT fb.match_id) as innings,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
                SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.is_legal_ball THEN 1 ELSE 0 END) as dot_balls,
                MAX(fb.batter_runs) as highest_ball_runs
            FROM fact_ball fb
            GROUP BY fb.batter_id
        ),
        innings_scores AS (
            SELECT
                batter_id as player_id,
                match_id,
                SUM(batter_runs) as innings_runs,
                SUM(CASE WHEN is_wicket AND player_out_id = batter_id THEN 1 ELSE 0 END) as got_out
            FROM fact_ball
            GROUP BY batter_id, match_id
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
            dp.is_wicketkeeper,
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
            -- Calculated metrics
            ROUND(bs.runs * 100.0 / NULLIF(bs.balls_faced, 0), 2) as strike_rate,
            ROUND(bs.runs * 1.0 / NULLIF(bs.dismissals, 0), 2) as batting_average,
            ROUND((bs.fours + bs.sixes) * 100.0 / NULLIF(bs.balls_faced, 0), 2) as boundary_pct,
            ROUND(bs.dot_balls * 100.0 / NULLIF(bs.balls_faced, 0), 2) as dot_ball_pct,
            -- Sample size indicators (per Andy Flower)
            CASE WHEN bs.innings < 10 THEN 'LOW'
                 WHEN bs.innings < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size_innings,
            CASE WHEN bs.balls_faced < 100 THEN 'LOW'
                 WHEN bs.balls_faced < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size_balls
        FROM batting_stats bs
        JOIN dim_player dp ON bs.player_id = dp.player_id
        JOIN high_scores hs ON bs.player_id = hs.player_id
    """)
    print("  - analytics_batting_career")

    # Batting by match phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_batting_by_phase AS
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
            -- Metrics
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as batting_average,
            ROUND((SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) + SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END)) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as boundary_pct,
            -- Sample size
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 100 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)
    print("  - analytics_batting_by_phase")

    # Batting by tournament
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_batting_by_tournament AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dt.tournament_id,
            dt.tournament_name,
            COUNT(DISTINCT fb.match_id) as innings,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as batting_average,
            CASE WHEN COUNT(DISTINCT fb.match_id) < 10 THEN 'LOW'
                 WHEN COUNT(DISTINCT fb.match_id) < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        GROUP BY dp.player_id, dp.current_name, dt.tournament_id, dt.tournament_name
    """)
    print("  - analytics_batting_by_tournament")

    # Batting by season
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_batting_by_season AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dm.season,
            COUNT(DISTINCT fb.match_id) as innings,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as batting_average,
            CASE WHEN COUNT(DISTINCT fb.match_id) < 5 THEN 'LOW'
                 WHEN COUNT(DISTINCT fb.match_id) < 15 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_match dm ON fb.match_id = dm.match_id
        GROUP BY dp.player_id, dp.current_name, dm.season
    """)
    print("  - analytics_batting_by_season")


def create_bowling_views(conn: duckdb.DuckDBPyConnection):
    """Create bowling analytics views."""

    print("Creating bowling analytics views...")

    # Player career bowling stats
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_bowling_career AS
        WITH bowling_stats AS (
            SELECT
                fb.bowler_id as player_id,
                COUNT(DISTINCT fb.match_id) as matches_bowled,
                SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
                SUM(fb.total_runs) as runs_conceded,
                SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
                SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
                SUM(CASE WHEN fb.extra_type = 'wides' THEN 1 ELSE 0 END) as wides,
                SUM(CASE WHEN fb.extra_type = 'noballs' THEN 1 ELSE 0 END) as noballs,
                SUM(CASE WHEN fb.batter_runs = 4 THEN 1 ELSE 0 END) as fours_conceded,
                SUM(CASE WHEN fb.batter_runs = 6 THEN 1 ELSE 0 END) as sixes_conceded
            FROM fact_ball fb
            GROUP BY fb.bowler_id
        ),
        best_figures AS (
            SELECT
                bowler_id as player_id,
                match_id,
                SUM(CASE WHEN is_wicket AND wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as match_wickets,
                SUM(total_runs) as match_runs
            FROM fact_ball
            GROUP BY bowler_id, match_id
        ),
        best_bowling AS (
            SELECT
                player_id,
                MAX(match_wickets) as best_wickets,
                -- Get runs for best wicket haul
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
            bs.wides,
            bs.noballs,
            bs.fours_conceded,
            bs.sixes_conceded,
            -- Calculated metrics
            ROUND(bs.runs_conceded * 6.0 / NULLIF(bs.balls_bowled, 0), 2) as economy_rate,
            ROUND(bs.runs_conceded * 1.0 / NULLIF(bs.wickets, 0), 2) as bowling_average,
            ROUND(bs.balls_bowled * 1.0 / NULLIF(bs.wickets, 0), 2) as bowling_strike_rate,
            ROUND(bs.dot_balls * 100.0 / NULLIF(bs.balls_bowled, 0), 2) as dot_ball_pct,
            -- Sample size indicators
            CASE WHEN bs.matches_bowled < 10 THEN 'LOW'
                 WHEN bs.matches_bowled < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size_matches,
            CASE WHEN bs.balls_bowled < 100 THEN 'LOW'
                 WHEN bs.balls_bowled < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size_balls
        FROM bowling_stats bs
        JOIN dim_player dp ON bs.player_id = dp.player_id
        JOIN best_bowling bb ON bs.player_id = bb.player_id
    """)
    print("  - analytics_bowling_career")

    # Bowling by match phase
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_bowling_by_phase AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            fb.match_phase,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            ROUND(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) / 6.0, 1) as overs,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
            SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) as dot_balls,
            -- Metrics
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            ROUND(SUM(CASE WHEN fb.batter_runs = 0 AND fb.extra_runs = 0 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as dot_ball_pct,
            -- Sample size
            CASE WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 100 THEN 'LOW'
                 WHEN SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) < 500 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        GROUP BY dp.player_id, dp.current_name, fb.match_phase
    """)
    print("  - analytics_bowling_by_phase")

    # Bowling by tournament
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_bowling_by_tournament AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dt.tournament_id,
            dt.tournament_name,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) as wickets,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END), 0), 2) as bowling_average,
            CASE WHEN COUNT(DISTINCT fb.match_id) < 10 THEN 'LOW'
                 WHEN COUNT(DISTINCT fb.match_id) < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.bowler_id = dp.player_id
        JOIN dim_match dm ON fb.match_id = dm.match_id
        JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
        GROUP BY dp.player_id, dp.current_name, dt.tournament_id, dt.tournament_name
    """)
    print("  - analytics_bowling_by_tournament")


def create_matchup_views(conn: duckdb.DuckDBPyConnection):
    """Create head-to-head matchup views."""

    print("Creating matchup analytics views...")

    # Batter vs Bowler matchups
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_batter_vs_bowler AS
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
            CASE WHEN COUNT(*) < 10 THEN 'LOW'
                 WHEN COUNT(*) < 30 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp_bat ON fb.batter_id = dp_bat.player_id
        JOIN dim_player dp_bowl ON fb.bowler_id = dp_bowl.player_id
        WHERE fb.is_legal_ball = TRUE
        GROUP BY dp_bat.player_id, dp_bat.current_name, dp_bowl.player_id, dp_bowl.current_name
    """)
    print("  - analytics_batter_vs_bowler")

    # Player vs Team
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_batter_vs_team AS
        SELECT
            dp.player_id,
            dp.current_name as player_name,
            dt.team_id as opponent_team_id,
            dt.team_name as opponent_team,
            COUNT(DISTINCT fb.match_id) as innings,
            SUM(fb.batter_runs) as runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
            SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as dismissals,
            ROUND(SUM(fb.batter_runs) * 100.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as strike_rate,
            ROUND(SUM(fb.batter_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END), 0), 2) as average,
            CASE WHEN COUNT(DISTINCT fb.match_id) < 5 THEN 'LOW'
                 WHEN COUNT(DISTINCT fb.match_id) < 15 THEN 'MEDIUM'
                 ELSE 'HIGH' END as sample_size
        FROM fact_ball fb
        JOIN dim_player dp ON fb.batter_id = dp.player_id
        JOIN dim_team dt ON fb.bowling_team_id = dt.team_id
        GROUP BY dp.player_id, dp.current_name, dt.team_id, dt.team_name
    """)
    print("  - analytics_batter_vs_team")


def create_aggregate_views(conn: duckdb.DuckDBPyConnection):
    """Create aggregate leaderboard views."""

    print("Creating aggregate analytics views...")

    # Top run scorers (with minimum innings filter)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_top_run_scorers AS
        SELECT
            player_id,
            player_name,
            primary_role,
            innings,
            runs,
            balls_faced,
            highest_score,
            fifties,
            hundreds,
            strike_rate,
            batting_average,
            boundary_pct,
            sample_size_innings
        FROM analytics_batting_career
        WHERE innings >= 10
        ORDER BY runs DESC
    """)
    print("  - analytics_top_run_scorers")

    # Top wicket takers
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_top_wicket_takers AS
        SELECT
            player_id,
            player_name,
            primary_role,
            matches_bowled,
            overs_bowled,
            wickets,
            best_wickets,
            best_runs,
            economy_rate,
            bowling_average,
            bowling_strike_rate,
            dot_ball_pct,
            sample_size_matches
        FROM analytics_bowling_career
        WHERE matches_bowled >= 10
        ORDER BY wickets DESC
    """)
    print("  - analytics_top_wicket_takers")

    # Best strike rates (qualified batters)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_best_strike_rates AS
        SELECT
            player_id,
            player_name,
            primary_role,
            innings,
            runs,
            balls_faced,
            strike_rate,
            batting_average,
            boundary_pct,
            sample_size_balls
        FROM analytics_batting_career
        WHERE balls_faced >= 500  -- Minimum qualification
        ORDER BY strike_rate DESC
    """)
    print("  - analytics_best_strike_rates")

    # Best economy rates (qualified bowlers)
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_best_economy AS
        SELECT
            player_id,
            player_name,
            primary_role,
            matches_bowled,
            overs_bowled,
            runs_conceded,
            wickets,
            economy_rate,
            dot_ball_pct,
            sample_size_balls
        FROM analytics_bowling_career
        WHERE balls_bowled >= 500  -- Minimum qualification
        ORDER BY economy_rate ASC
    """)
    print("  - analytics_best_economy")

    # Death over specialists
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_death_over_specialists AS
        SELECT
            player_id,
            player_name,
            balls_bowled,
            overs,
            runs_conceded,
            wickets,
            economy_rate,
            dot_ball_pct,
            sample_size
        FROM analytics_bowling_by_phase
        WHERE match_phase = 'death'
          AND balls_bowled >= 200
        ORDER BY economy_rate ASC
    """)
    print("  - analytics_death_over_specialists")

    # Powerplay hitters
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_powerplay_hitters AS
        SELECT
            player_id,
            player_name,
            innings,
            runs,
            balls_faced,
            strike_rate,
            boundary_pct,
            sample_size
        FROM analytics_batting_by_phase
        WHERE match_phase = 'powerplay'
          AND balls_faced >= 200
        ORDER BY strike_rate DESC
    """)
    print("  - analytics_powerplay_hitters")


def create_team_views(conn: duckdb.DuckDBPyConnection):
    """Create team-level analytics views."""

    print("Creating team analytics views...")

    # Team batting performance
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_team_batting AS
        SELECT
            dt.team_id,
            dt.team_name,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.total_runs) as total_runs,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_faced,
            SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END) as wickets_lost,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as run_rate,
            ROUND(SUM(fb.total_runs) * 1.0 / NULLIF(SUM(CASE WHEN fb.is_wicket THEN 1 ELSE 0 END), 0), 2) as runs_per_wicket
        FROM fact_ball fb
        JOIN dim_team dt ON fb.batting_team_id = dt.team_id
        GROUP BY dt.team_id, dt.team_name
        ORDER BY total_runs DESC
    """)
    print("  - analytics_team_batting")

    # Team bowling performance
    conn.execute("""
        CREATE OR REPLACE VIEW analytics_team_bowling AS
        SELECT
            dt.team_id,
            dt.team_name,
            COUNT(DISTINCT fb.match_id) as matches,
            SUM(fb.total_runs) as runs_conceded,
            SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END) as balls_bowled,
            SUM(CASE WHEN fb.is_wicket AND fb.wicket_type NOT IN ('run out', 'retired hurt', 'retired out') THEN 1 ELSE 0 END) as wickets_taken,
            ROUND(SUM(fb.total_runs) * 6.0 / NULLIF(SUM(CASE WHEN fb.is_legal_ball THEN 1 ELSE 0 END), 0), 2) as economy_rate
        FROM fact_ball fb
        JOIN dim_team dt ON fb.bowling_team_id = dt.team_id
        GROUP BY dt.team_id, dt.team_name
        ORDER BY wickets_taken DESC
    """)
    print("  - analytics_team_bowling")


def verify_views(conn: duckdb.DuckDBPyConnection):
    """Verify all views are working with sample queries."""

    print("\nVerifying analytics views...\n")

    # Test batting career
    result = conn.execute("""
        SELECT player_name, runs, strike_rate, batting_average, sample_size_innings
        FROM analytics_batting_career
        ORDER BY runs DESC
        LIMIT 5
    """).fetchall()

    print("Top 5 Run Scorers (Career):")
    print("-" * 70)
    print(f"{'Player':<25} {'Runs':>8} {'SR':>8} {'Avg':>8} {'Sample':>10}")
    print("-" * 70)
    for row in result:
        print(
            f"{row[0]:<25} {row[1]:>8,} {row[2]:>8.2f} {row[3] if row[3] else 'N/A':>8} {row[4]:>10}"
        )

    print()

    # Test bowling career
    result = conn.execute("""
        SELECT player_name, wickets, economy_rate, bowling_average, sample_size_matches
        FROM analytics_bowling_career
        ORDER BY wickets DESC
        LIMIT 5
    """).fetchall()

    print("Top 5 Wicket Takers (Career):")
    print("-" * 70)
    print(f"{'Player':<25} {'Wkts':>8} {'Econ':>8} {'Avg':>8} {'Sample':>10}")
    print("-" * 70)
    for row in result:
        print(
            f"{row[0]:<25} {row[1]:>8,} {row[2]:>8.2f} {row[3] if row[3] else 'N/A':>8} {row[4]:>10}"
        )

    print()

    # Test death over specialists
    result = conn.execute("""
        SELECT player_name, overs, wickets, economy_rate, dot_ball_pct
        FROM analytics_death_over_specialists
        LIMIT 5
    """).fetchall()

    print("Top 5 Death Over Specialists (by Economy):")
    print("-" * 70)
    print(f"{'Player':<25} {'Overs':>8} {'Wkts':>8} {'Econ':>8} {'Dot%':>10}")
    print("-" * 70)
    for row in result:
        print(f"{row[0]:<25} {row[1]:>8.1f} {row[2]:>8} {row[3]:>8.2f} {row[4]:>10.1f}")

    print()

    # Test powerplay hitters
    result = conn.execute("""
        SELECT player_name, innings, runs, strike_rate, boundary_pct
        FROM analytics_powerplay_hitters
        LIMIT 5
    """).fetchall()

    print("Top 5 Powerplay Hitters (by Strike Rate):")
    print("-" * 70)
    print(f"{'Player':<25} {'Inn':>8} {'Runs':>8} {'SR':>8} {'Bound%':>10}")
    print("-" * 70)
    for row in result:
        print(f"{row[0]:<25} {row[1]:>8} {row[2]:>8} {row[3]:>8.2f} {row[4]:>10.1f}")

    return True


def main():
    """Main entry point."""

    print("=" * 60)
    print("Cricket Playbook - Analytics Layer")
    print("Author: Stephen Curry")
    print("=" * 60)
    print()

    # Connect to database
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run ingest.py first to create the database.")
        return 1

    conn = duckdb.connect(str(DB_PATH))

    # Create all views
    create_batting_views(conn)
    create_bowling_views(conn)
    create_matchup_views(conn)
    create_aggregate_views(conn)
    create_team_views(conn)

    # Verify
    verify_views(conn)

    # Count views
    result = conn.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_type = 'VIEW' AND table_name LIKE 'analytics_%'
    """).fetchone()

    print()
    print("=" * 60)
    print(f"Analytics layer complete: {result[0]} views created")
    print("=" * 60)

    conn.close()
    return 0


if __name__ == "__main__":
    exit(main())
