#!/usr/bin/env python3
"""
Cricket Playbook - IPL 2026 Team Stat Pack Generator
Author: Tom Brady (Product Owner) & Stephen Curry (Analytics)
Domain Review: Andy Flower

Generates comprehensive stat packs for each IPL 2026 team including:
- Team overview and roster
- Historical records vs each opposition
- Venue performance breakdown
- Individual player statistics
- Phase-wise analysis
- Key matchups and insights
"""

import duckdb
import json
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # Go up two levels: generators -> scripts -> project root
DB_PATH = PROJECT_DIR / "data" / "cricket_playbook.duckdb"
OUTPUT_DIR = PROJECT_DIR / "stat_packs"
PLAYER_TAGS_PATH = PROJECT_DIR / "outputs" / "player_tags.json"


def load_player_tags() -> dict:
    """Load player tags from JSON file."""
    if not PLAYER_TAGS_PATH.exists():
        return {"batters": [], "bowlers": []}
    with open(PLAYER_TAGS_PATH) as f:
        return json.load(f)


def get_player_tags_lookup(tags_data: dict) -> dict:
    """Create lookup dict from player_id to tags."""
    # Role archetype tags (from clustering)
    BATTER_CLUSTERS = {
        "EXPLOSIVE_OPENER",
        "PLAYMAKER",
        "ANCHOR",
        "ACCUMULATOR",
        "MIDDLE_ORDER",
        "FINISHER",
    }
    BOWLER_CLUSTERS = {
        "PACER",
        "SPINNER",
        "WORKHORSE",
        "NEW_BALL_SPECIALIST",
        "MIDDLE_OVERS_CONTROLLER",
        "DEATH_SPECIALIST",
        "PART_TIMER",
    }

    lookup = {}
    for batter in tags_data.get("batters", []):
        tags = batter.get("tags", [])
        # Extract cluster from tags
        cluster = ""
        for tag in tags:
            if tag in BATTER_CLUSTERS:
                cluster = tag
                break
        lookup[batter["player_id"]] = {"cluster": cluster, "tags": tags}

    for bowler in tags_data.get("bowlers", []):
        pid = bowler["player_id"]
        tags = bowler.get("tags", [])
        # Extract cluster from tags
        cluster = ""
        for tag in tags:
            if tag in BOWLER_CLUSTERS:
                cluster = tag
                break

        if pid in lookup:
            # Merge bowler tags into existing entry
            lookup[pid]["tags"].extend(tags)
            if not lookup[pid]["cluster"] and cluster:
                lookup[pid]["bowler_cluster"] = cluster
        else:
            lookup[pid] = {"cluster": cluster, "tags": tags}
    return lookup


# Franchise name mappings for historical data
FRANCHISE_ALIASES = {
    "Delhi Capitals": ["Delhi Capitals", "Delhi Daredevils"],
    "Punjab Kings": ["Punjab Kings", "Kings XI Punjab"],
    "Royal Challengers Bengaluru": [
        "Royal Challengers Bengaluru",
        "Royal Challengers Bangalore",
    ],
    "Chennai Super Kings": ["Chennai Super Kings"],
    "Mumbai Indians": ["Mumbai Indians"],
    "Kolkata Knight Riders": ["Kolkata Knight Riders"],
    "Rajasthan Royals": ["Rajasthan Royals"],
    "Sunrisers Hyderabad": ["Sunrisers Hyderabad"],
    "Gujarat Titans": ["Gujarat Titans"],
    "Lucknow Super Giants": ["Lucknow Super Giants"],
}

# Team short codes
TEAM_CODES = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
}

# Home venue mappings for each IPL team
# Note: Some teams have moved venues over the years, these are current (2023+) home grounds
TEAM_HOME_VENUES = {
    "Chennai Super Kings": ["MA Chidambaram Stadium, Chepauk, Chennai"],
    "Mumbai Indians": ["Wankhede Stadium, Mumbai"],
    "Royal Challengers Bengaluru": ["M Chinnaswamy Stadium, Bengaluru"],
    "Kolkata Knight Riders": ["Eden Gardens, Kolkata"],
    "Delhi Capitals": ["Arun Jaitley Stadium, Delhi"],
    "Punjab Kings": [
        "Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur",
        "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
    ],
    "Rajasthan Royals": ["Sawai Mansingh Stadium, Jaipur"],
    "Sunrisers Hyderabad": ["Rajiv Gandhi International Stadium, Uppal, Hyderabad"],
    "Gujarat Titans": ["Narendra Modi Stadium, Ahmedabad"],
    "Lucknow Super Giants": [
        "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow"
    ],
}


def get_opposition_clause(team_name: str) -> str:
    """Generate SQL IN clause for opposition team names (handles aliases)."""
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    return ", ".join([f"'{a}'" for a in aliases])


def generate_venue_analysis(conn, team_name: str, alias_clause: str) -> list:
    """Generate comprehensive venue analysis section for a team.

    Includes:
    - Home venue performance (win rate, avg score, key stats)
    - Away venue performance breakdown
    - Venue-specific pitch characteristics (pace vs spin friendly)
    - Venue specialists (players who perform best at specific venues)
    """
    md = []
    md.append("## Venue Analysis\n")
    md.append("*Performance breakdown by venue (2023+ IPL data)*\n")

    home_venues = TEAM_HOME_VENUES.get(team_name, [])
    home_venue_clause = ", ".join([f"'{v}'" for v in home_venues]) if home_venues else "''"

    # ==========================================================================
    # HOME VENUE PERFORMANCE
    # ==========================================================================
    if home_venues:
        md.append(f"### Home Venue: {home_venues[0].split(',')[0]}\n")

        # Get home venue win rate and match stats
        home_stats = conn.execute(f"""
            WITH ipl_matches AS (
                SELECT dm.match_id, dv.venue_name, dt1.team_name as team1, dt2.team_name as team2,
                       dtw.team_name as winner
                FROM dim_match dm
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_venue dv ON dm.venue_id = dv.venue_id
                JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
                JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
                LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dv.venue_name IN ({home_venue_clause})
            )
            SELECT
                COUNT(*) as matches,
                SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN winner IS NOT NULL AND winner NOT IN ({alias_clause}) THEN 1 ELSE 0 END) as losses
            FROM ipl_matches
            WHERE team1 IN ({alias_clause}) OR team2 IN ({alias_clause})
        """).fetchone()

        if home_stats and home_stats[0] > 0:
            matches, wins, losses = home_stats
            win_pct = (wins / matches * 100) if matches > 0 else 0
            md.append(f"- **Matches:** {matches}")
            md.append(f"- **Win Rate:** {win_pct:.1f}% ({wins}W - {losses}L)")

        # Get average score at home venue
        home_avg_score = conn.execute(f"""
            WITH ipl_innings AS (
                SELECT fb.match_id, fb.innings, dv.venue_name, dt.team_name,
                       SUM(fb.total_runs) as innings_runs
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_venue dv ON dm.venue_id = dv.venue_id
                JOIN dim_team dt ON fb.batting_team_id = dt.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dv.venue_name IN ({home_venue_clause})
                GROUP BY fb.match_id, fb.innings, dv.venue_name, dt.team_name
            )
            SELECT
                COUNT(*) as innings,
                ROUND(AVG(innings_runs), 1) as avg_score,
                MAX(innings_runs) as highest,
                MIN(innings_runs) as lowest
            FROM ipl_innings
            WHERE team_name IN ({alias_clause})
        """).fetchone()

        if home_avg_score and home_avg_score[0] > 0:
            innings, avg_score, highest, lowest = home_avg_score
            md.append(f"- **Avg Score (batting):** {avg_score}")
            md.append(f"- **Highest/Lowest:** {highest}/{lowest}")

        # Get pitch characteristics at home venue
        home_pitch = conn.execute(f"""
            WITH ipl_balls AS (
                SELECT fb.*, dv.venue_name,
                       COALESCE(bc.bowling_style, 'Unknown') as bowling_style
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
                JOIN dim_venue dv ON dm.venue_id = dv.venue_id
                LEFT JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
                WHERE dt.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dv.venue_name IN ({home_venue_clause})
            )
            SELECT
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_wickets,
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_wickets,
                SUM(CASE WHEN bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_balls,
                SUM(CASE WHEN bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_balls
            FROM ipl_balls
        """).fetchone()

        if home_pitch and home_pitch[2] and home_pitch[3]:
            pace_wkts, spin_wkts, pace_balls, spin_balls = home_pitch
            pace_sr = round(pace_balls / pace_wkts, 1) if pace_wkts > 0 else 0
            spin_sr = round(spin_balls / spin_wkts, 1) if spin_wkts > 0 else 0

            # Determine pitch bias
            if pace_sr > 0 and spin_sr > 0:
                if pace_sr < spin_sr - 5:
                    pitch_type = "Pace-friendly"
                elif spin_sr < pace_sr - 5:
                    pitch_type = "Spin-friendly"
                else:
                    pitch_type = "Balanced"
            else:
                pitch_type = "Unknown"

            md.append(f"- **Pitch Type:** {pitch_type}")
            md.append(f"- **Pace SR:** {pace_sr} | **Spin SR:** {spin_sr}")

        md.append("")

    # ==========================================================================
    # AWAY PERFORMANCE BREAKDOWN
    # ==========================================================================
    md.append("### Away Performance\n")

    away_stats = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name, dt1.team_name as team1, dt2.team_name as team2,
                   dtw.team_name as winner
            FROM dim_match dm
            JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
            JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
            LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
            WHERE dtr.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '2023-01-01'
              AND dv.venue_name NOT IN ({home_venue_clause})
        ),
        venue_stats AS (
            SELECT
                venue_name,
                COUNT(*) as matches,
                SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins
            FROM ipl_matches
            WHERE team1 IN ({alias_clause}) OR team2 IN ({alias_clause})
            GROUP BY venue_name
            HAVING COUNT(*) >= 2
        ),
        venue_scores AS (
            SELECT dv.venue_name,
                   ROUND(AVG(innings_runs), 1) as avg_score
            FROM (
                SELECT fb.match_id, fb.innings, dm.venue_id,
                       SUM(fb.total_runs) as innings_runs
                FROM fact_ball fb
                JOIN dim_match dm ON fb.match_id = dm.match_id
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_team dt ON fb.batting_team_id = dt.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
                  AND dm.match_date >= '2023-01-01'
                  AND dt.team_name IN ({alias_clause})
                GROUP BY fb.match_id, fb.innings, dm.venue_id
            ) innings
            JOIN dim_venue dv ON innings.venue_id = dv.venue_id
            GROUP BY dv.venue_name
        )
        SELECT vs.venue_name, vs.matches, vs.wins,
               ROUND(vs.wins * 100.0 / vs.matches, 1) as win_pct,
               COALESCE(vsc.avg_score, 0) as avg_score
        FROM venue_stats vs
        LEFT JOIN venue_scores vsc ON vs.venue_name = vsc.venue_name
        ORDER BY vs.matches DESC
        LIMIT 10
    """).fetchall()

    if away_stats:
        md.append("| Venue | Matches | Wins | Win% | Avg Score |")
        md.append("|-------|---------|------|------|-----------|")
        for row in away_stats:
            venue, matches, wins, win_pct, avg_score = row
            venue_short = venue.split(",")[0][:35]
            md.append(f"| {venue_short} | {matches} | {wins} | {win_pct}% | {avg_score or '-'} |")
    else:
        md.append("*Insufficient away match data (2023+)*")

    md.append("")

    # ==========================================================================
    # PITCH BIAS INDICATORS
    # ==========================================================================
    md.append("### Pitch Characteristics (All IPL Venues 2023+)\n")
    md.append("*Based on bowling strike rates - lower SR = more effective*\n")

    pitch_bias = conn.execute("""
        WITH ipl_balls AS (
            SELECT fb.*, dv.venue_name,
                   COALESCE(bc.bowling_style, 'Unknown') as bowling_style
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            LEFT JOIN dim_bowler_classification bc ON fb.bowler_id = bc.player_id
            WHERE dt.tournament_name = 'Indian Premier League'
              AND dm.match_date >= '2023-01-01'
        ),
        venue_pitch AS (
            SELECT
                venue_name,
                COUNT(DISTINCT match_id) as matches,
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_wickets,
                SUM(CASE WHEN is_wicket AND bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_wickets,
                SUM(CASE WHEN bowling_style IN ('Right-arm pace', 'Left-arm pace') THEN 1 ELSE 0 END) as pace_balls,
                SUM(CASE WHEN bowling_style IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin') THEN 1 ELSE 0 END) as spin_balls
            FROM ipl_balls
            GROUP BY venue_name
            HAVING COUNT(DISTINCT match_id) >= 5
        )
        SELECT
            venue_name,
            matches,
            ROUND(pace_balls * 1.0 / NULLIF(pace_wickets, 0), 1) as pace_sr,
            ROUND(spin_balls * 1.0 / NULLIF(spin_wickets, 0), 1) as spin_sr,
            CASE
                WHEN pace_balls * 1.0 / NULLIF(pace_wickets, 0) < spin_balls * 1.0 / NULLIF(spin_wickets, 0) - 5 THEN 'PACE'
                WHEN spin_balls * 1.0 / NULLIF(spin_wickets, 0) < pace_balls * 1.0 / NULLIF(pace_wickets, 0) - 5 THEN 'SPIN'
                ELSE 'BALANCED'
            END as pitch_bias
        FROM venue_pitch
        ORDER BY matches DESC
        LIMIT 10
    """).fetchall()

    if pitch_bias:
        md.append("| Venue | Matches | Pace SR | Spin SR | Bias |")
        md.append("|-------|---------|---------|---------|------|")
        for row in pitch_bias:
            venue, matches, pace_sr, spin_sr, bias = row
            venue_short = venue.split(",")[0][:30]
            md.append(
                f"| {venue_short} | {matches} | {pace_sr or '-'} | {spin_sr or '-'} | {bias} |"
            )

    md.append("")

    # ==========================================================================
    # VENUE SPECIALISTS
    # ==========================================================================
    md.append("### Venue Specialists\n")
    md.append(
        "*Squad players with exceptional performance at specific venues (min 100 runs or 5 wickets)*\n"
    )

    # Batting specialists
    batter_specialists = conn.execute(f"""
        SELECT bv.batter_name, bv.venue, bv.innings, bv.runs, bv.strike_rate, bv.average
        FROM analytics_ipl_batter_venue bv
        JOIN ipl_2026_squads sq ON bv.batter_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bv.runs >= 100
          AND bv.sample_size IN ('MEDIUM', 'HIGH')
          AND (bv.strike_rate >= 150 OR bv.average >= 40)
        ORDER BY bv.runs DESC
        LIMIT 8
    """).fetchall()

    if batter_specialists:
        md.append("**Top Batting Performances:**\n")
        md.append("| Player | Venue | Inn | Runs | SR | Avg |")
        md.append("|--------|-------|-----|------|-----|-----|")
        for row in batter_specialists:
            name, venue, inn, runs, sr, avg = row
            venue_short = venue.split(",")[0][:25]
            md.append(f"| {name} | {venue_short} | {inn} | {runs} | {sr or '-'} | {avg or '-'} |")
        md.append("")

    # Bowling specialists
    bowler_specialists = conn.execute(f"""
        SELECT bv.bowler_name, bv.venue, bv.matches, bv.wickets, bv.economy, bv.strike_rate
        FROM analytics_ipl_bowler_venue bv
        JOIN ipl_2026_squads sq ON bv.bowler_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bv.wickets >= 5
          AND bv.sample_size IN ('MEDIUM', 'HIGH')
          AND (bv.economy <= 8.5 OR bv.strike_rate <= 18)
        ORDER BY bv.wickets DESC
        LIMIT 8
    """).fetchall()

    if bowler_specialists:
        md.append("**Top Bowling Performances:**\n")
        md.append("| Player | Venue | Matches | Wkts | Econ | SR |")
        md.append("|--------|-------|---------|------|------|-----|")
        for row in bowler_specialists:
            name, venue, matches, wkts, econ, sr = row
            venue_short = venue.split(",")[0][:25]
            md.append(
                f"| {name} | {venue_short} | {matches} | {wkts} | {econ or '-'} | {sr or '-'} |"
            )
        md.append("")

    if not batter_specialists and not bowler_specialists:
        md.append("*No venue specialists identified in current squad*\n")

    return md


def generate_team_stat_pack(conn, team_name: str, tags_lookup: dict) -> str:
    """Generate comprehensive stat pack for a team."""

    team_code = TEAM_CODES.get(team_name, team_name[:3].upper())
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    alias_clause = ", ".join([f"'{a}'" for a in aliases])

    md = []
    md.append(f"# {team_name} ({team_code}) - IPL 2026 Stat Pack")
    md.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("**Data Source:** Cricket Playbook Analytics Engine")
    md.append("**Prepared by:** Tom Brady (PO), Stephen Curry (Analytics), Andy Flower (Cricket)")
    md.append("\n---\n")

    # ==========================================================================
    # SECTION 1: TEAM ROSTER
    # ==========================================================================
    md.append("## 1. Squad Overview\n")

    roster = conn.execute(f"""
        SELECT player_name, role, bowling_type, batting_hand, price_cr, acquisition_type, year_joined
        FROM analytics_ipl_team_roster
        WHERE team_name = '{team_name}'
        ORDER BY price_cr DESC
    """).fetchall()

    md.append("### 1.1 Full Roster\n")
    md.append("| Player | Role | Bowling | Batting | Price (Cr) | Type | Joined |")
    md.append("|--------|------|---------|---------|------------|------|--------|")

    total_spend = 0
    role_counts = {}
    for row in roster:
        player, role, bowling, batting, price, acq, year = row
        price = price or 0
        total_spend += price
        role_counts[role] = role_counts.get(role, 0) + 1
        md.append(
            f"| {player} | {role} | {bowling or '-'} | {batting or '-'} | {price:.2f} | {acq or '-'} | {year or '-'} |"
        )

    md.append(f"\n**Total Squad Size:** {len(roster)} players")
    md.append(f"**Total Spend:** ₹{total_spend:.2f} Cr")
    md.append(
        "\n**Role Breakdown:** " + ", ".join([f"{k}: {v}" for k, v in sorted(role_counts.items())])
    )

    # ==========================================================================
    # SECTION 1.2: PLAYER ARCHETYPES AND TAGS
    # ==========================================================================
    md.append("\n### 1.2 Player Archetypes (K-means V2 Model)\n")
    md.append("*Based on clustering analysis of IPL career performance*\n")

    # Get player IDs for this team
    squad_players = conn.execute(f"""
        SELECT player_id, player_name, role
        FROM ipl_2026_squads
        WHERE team_name = '{team_name}'
        ORDER BY role, player_name
    """).fetchall()

    # Group by archetype - extract from tags
    BATTER_CLUSTERS = [
        "EXPLOSIVE_OPENER",
        "PLAYMAKER",
        "ANCHOR",
        "ACCUMULATOR",
        "MIDDLE_ORDER",
        "FINISHER",
    ]
    BOWLER_CLUSTERS = [
        "PACER",
        "SPINNER",
        "WORKHORSE",
        "NEW_BALL_SPECIALIST",
        "MIDDLE_OVERS_CONTROLLER",
        "DEATH_SPECIALIST",
        "PART_TIMER",
    ]

    batters_by_cluster = {}
    bowlers_by_cluster = {}

    for player_id, player_name, role in squad_players:
        if player_id in tags_lookup:
            tags = tags_lookup[player_id].get("tags", [])

            if role in ("Batter", "Wicketkeeper", "All-rounder"):
                # Find batter cluster tag
                for cluster in BATTER_CLUSTERS:
                    if cluster in tags:
                        if cluster not in batters_by_cluster:
                            batters_by_cluster[cluster] = []
                        batters_by_cluster[cluster].append((player_name, tags))
                        break

            if role in ("Bowler", "All-rounder"):
                # Find bowler cluster tag
                for cluster in BOWLER_CLUSTERS:
                    if cluster in tags:
                        if cluster not in bowlers_by_cluster:
                            bowlers_by_cluster[cluster] = []
                        bowlers_by_cluster[cluster].append((player_name, tags))
                        break

    if batters_by_cluster:
        md.append("**Batter Archetypes:**\n")
        for cluster in BATTER_CLUSTERS:
            if cluster in batters_by_cluster:
                players = batters_by_cluster[cluster]
                player_list = ", ".join([p[0] for p in players])
                md.append(f"- **{cluster}**: {player_list}")
        md.append("")

    if bowlers_by_cluster:
        md.append("**Bowler Archetypes:**\n")
        for cluster in BOWLER_CLUSTERS:
            if cluster in bowlers_by_cluster:
                players = bowlers_by_cluster[cluster]
                player_list = ", ".join([p[0] for p in players])
                md.append(f"- **{cluster}**: {player_list}")
        md.append("")

    # Show key player tags
    md.append("### 1.3 Key Player Tags\n")
    md.append("*Performance tags based on phase analysis, matchups, and specializations*\n")

    md.append("| Player | Tags |")
    md.append("|--------|------|")
    for player_id, player_name, role in squad_players:
        if player_id in tags_lookup:
            tags = tags_lookup[player_id].get("tags", [])
            if tags:
                # Show up to 5 most relevant tags
                display_tags = tags[:5]
                tags_str = ", ".join(display_tags)
                if len(tags) > 5:
                    tags_str += f" (+{len(tags) - 5} more)"
                md.append(f"| {player_name} | {tags_str} |")

    # ==========================================================================
    # SECTION 2: TEAM HISTORICAL RECORD VS OPPOSITION
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 2. Historical Record vs Opposition\n")
    md.append(
        "*Combined records for franchise aliases (e.g., Delhi Capitals + Delhi Daredevils)*\n"
    )

    # Get team vs team records
    for opp_name, opp_aliases in FRANCHISE_ALIASES.items():
        if opp_name == team_name:
            continue

        opp_clause = ", ".join([f"'{a}'" for a in opp_aliases])

        # Get head-to-head match results
        h2h = conn.execute(f"""
            WITH ipl_matches AS (
                SELECT dm.match_id, dm.winner_id, dt1.team_name as team1, dt2.team_name as team2,
                       dtw.team_name as winner, dm.venue_id
                FROM dim_match dm
                JOIN dim_tournament dtr ON dm.tournament_id = dtr.tournament_id
                JOIN dim_team dt1 ON dm.team1_id = dt1.team_id
                JOIN dim_team dt2 ON dm.team2_id = dt2.team_id
                LEFT JOIN dim_team dtw ON dm.winner_id = dtw.team_id
                WHERE dtr.tournament_name = 'Indian Premier League'
            )
            SELECT
                COUNT(*) as matches,
                SUM(CASE WHEN winner IN ({alias_clause}) THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN winner IN ({opp_clause}) THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN winner IS NULL THEN 1 ELSE 0 END) as no_result
            FROM ipl_matches
            WHERE (team1 IN ({alias_clause}) AND team2 IN ({opp_clause}))
               OR (team1 IN ({opp_clause}) AND team2 IN ({alias_clause}))
        """).fetchone()

        if h2h and h2h[0] > 0:
            matches, wins, losses, nr = h2h
            opp_code = TEAM_CODES.get(opp_name, opp_name[:3].upper())
            md.append(f"### vs {opp_name} ({opp_code})")
            md.append(f"**Record:** {wins}W - {losses}L - {nr}NR (Matches: {matches})")
            win_pct = (wins / matches * 100) if matches > 0 else 0
            md.append(f"**Win %:** {win_pct:.1f}%\n")

    # ==========================================================================
    # SECTION 3: VENUE ANALYSIS (NEW COMPREHENSIVE SECTION)
    # ==========================================================================
    md.append("\n---\n")
    venue_analysis = generate_venue_analysis(conn, team_name, alias_clause)
    md.extend(venue_analysis)

    # ==========================================================================
    # SECTION 4: SQUAD BATTING ANALYSIS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 4. Squad Batting Analysis\n")

    # Career batting stats
    md.append("### 4.1 IPL Career Batting\n")

    batting = conn.execute(f"""
        SELECT player_name, role, price_cr,
               ipl_innings, ipl_runs, ipl_balls, ipl_sr, ipl_avg,
               ipl_boundary_pct, ipl_dot_pct, ipl_fifties, ipl_hundreds, ipl_sample_size
        FROM analytics_ipl_squad_batting
        WHERE team_name = '{team_name}'
        ORDER BY ipl_runs DESC NULLS LAST
    """).fetchall()

    md.append(
        "| Player | Role | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | 50s | 100s | Sample |"
    )
    md.append(
        "|--------|------|-----|------|-------|-----|-----|--------|------|-----|------|--------|"
    )
    for row in batting:
        (
            name,
            role,
            price,
            inn,
            runs,
            balls,
            sr,
            avg,
            bound,
            dot,
            fifties,
            hundreds,
            sample,
        ) = row
        md.append(
            f"| {name} | {role} | {inn or 0} | {runs or 0} | {balls or 0} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {dot or '-'} | {fifties or 0} | {hundreds or 0} | {sample or '-'} |"
        )

    # Phase-wise batting
    md.append("\n### 4.2 Phase-wise Batting (Qualified players)\n")

    phase_batting = conn.execute(f"""
        SELECT player_name, match_phase, innings, runs, balls_faced, strike_rate,
               batting_average, boundary_pct, dot_ball_pct, sample_size
        FROM analytics_ipl_squad_batting_phase
        WHERE team_name = '{team_name}'
          AND sample_size IN ('MEDIUM', 'HIGH')
        ORDER BY player_name,
            CASE match_phase WHEN 'powerplay' THEN 1 WHEN 'middle' THEN 2 WHEN 'death' THEN 3 END
    """).fetchall()

    md.append("| Player | Phase | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | Sample |")
    md.append("|--------|-------|-----|------|-------|-----|-----|--------|------|--------|")
    for row in phase_batting:
        name, phase, inn, runs, balls, sr, avg, bound, dot, sample = row
        md.append(
            f"| {name} | {phase} | {inn or 0} | {runs or 0} | {balls or 0} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {dot or '-'} | {sample or '-'} |"
        )

    # ==========================================================================
    # SECTION 5: SQUAD BOWLING ANALYSIS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 5. Squad Bowling Analysis\n")

    # Career bowling stats
    md.append("### 5.1 IPL Career Bowling\n")

    bowling = conn.execute(f"""
        SELECT player_name, role, bowling_type, price_cr,
               ipl_matches, ipl_overs, ipl_wickets, ipl_economy, ipl_avg, ipl_sr,
               ipl_dot_pct, ipl_boundary_pct, ipl_sample_size
        FROM analytics_ipl_squad_bowling
        WHERE team_name = '{team_name}'
          AND ipl_matches > 0
        ORDER BY ipl_wickets DESC NULLS LAST
    """).fetchall()

    md.append(
        "| Player | Type | Matches | Overs | Wkts | Econ | Avg | SR | Dot% | Bound% | Sample |"
    )
    md.append(
        "|--------|------|---------|-------|------|------|-----|-----|------|--------|--------|"
    )
    for row in bowling:
        (
            name,
            role,
            btype,
            price,
            matches,
            overs,
            wkts,
            econ,
            avg,
            sr,
            dot,
            bound,
            sample,
        ) = row
        btype_short = (btype or "-")[:10]
        md.append(
            f"| {name} | {btype_short} | {matches or 0} | {overs or 0:.1f} | {wkts or 0} | {econ or '-'} | {avg or '-'} | {sr or '-'} | {dot or '-'} | {bound or '-'} | {sample or '-'} |"
        )

    # Phase distribution
    md.append("\n### 5.2 Bowler Phase Distribution\n")
    md.append("*Shows % of overs bowled and % of wickets taken in each phase*\n")

    phase_dist = conn.execute(f"""
        SELECT bpd.bowler_name, bpd.match_phase,
               bpd.overs, bpd.wickets, bpd.economy, bpd.dot_ball_pct,
               bpd.pct_overs_in_phase, bpd.pct_wickets_in_phase, bpd.wicket_efficiency,
               bpd.sample_size
        FROM analytics_ipl_bowler_phase_distribution bpd
        JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bpd.sample_size IN ('MEDIUM', 'HIGH')
        ORDER BY bpd.bowler_name,
            CASE bpd.match_phase WHEN 'powerplay' THEN 1 WHEN 'middle' THEN 2 WHEN 'death' THEN 3 END
    """).fetchall()

    md.append(
        "| Bowler | Phase | Overs | Wkts | Econ | Dot% | %Overs | %Wkts | Efficiency | Sample |"
    )
    md.append(
        "|--------|-------|-------|------|------|------|--------|-------|------------|--------|"
    )
    for row in phase_dist:
        name, phase, overs, wkts, econ, dot, pct_ov, pct_wk, eff, sample = row
        eff_str = f"+{eff}" if eff and eff > 0 else str(eff or "-")
        md.append(
            f"| {name} | {phase} | {overs or 0:.1f} | {wkts or 0} | {econ or '-'} | {dot or '-'} | {pct_ov or '-'}% | {pct_wk or '-'}% | {eff_str} | {sample or '-'} |"
        )

    # ==========================================================================
    # SECTION 6: KEY PLAYER VS OPPOSITION MATCHUPS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 6. Key Batter vs Opposition\n")
    md.append("*Top batters' performance against each IPL team*\n")

    # Get top 5 batters by runs
    top_batters = conn.execute(f"""
        SELECT DISTINCT sq.player_id, sq.player_name
        FROM ipl_2026_squads sq
        JOIN analytics_ipl_batting_career bc ON sq.player_id = bc.player_id
        WHERE sq.team_name = '{team_name}'
          AND bc.runs > 500
        ORDER BY bc.runs DESC
        LIMIT 5
    """).fetchall()

    for batter_id, batter_name in top_batters:
        md.append(f"\n### {batter_name}\n")

        vs_team = conn.execute(f"""
            SELECT opposition, innings, runs, balls, strike_rate, average,
                   boundary_pct, dot_ball_pct, dismissals, sample_size
            FROM analytics_ipl_batter_vs_team
            WHERE batter_id = '{batter_id}'
              AND sample_size IN ('MEDIUM', 'HIGH')
            ORDER BY runs DESC
        """).fetchall()

        if vs_team:
            md.append(
                "| Opposition | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | Outs | Sample |"
            )
            md.append(
                "|------------|-----|------|-------|-----|-----|--------|------|------|--------|"
            )
            for row in vs_team:
                opp, inn, runs, balls, sr, avg, bound, dot, outs, sample = row
                md.append(
                    f"| {opp} | {inn} | {runs} | {balls} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {dot or '-'} | {outs} | {sample or '-'} |"
                )

    # ==========================================================================
    # SECTION 7: KEY BOWLER VS OPPOSITION
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 7. Key Bowler vs Opposition\n")

    # Get top 5 bowlers by wickets
    top_bowlers = conn.execute(f"""
        SELECT DISTINCT sq.player_id, sq.player_name
        FROM ipl_2026_squads sq
        JOIN analytics_ipl_bowling_career bc ON sq.player_id = bc.player_id
        WHERE sq.team_name = '{team_name}'
          AND bc.wickets > 30
        ORDER BY bc.wickets DESC
        LIMIT 5
    """).fetchall()

    for bowler_id, bowler_name in top_bowlers:
        md.append(f"\n### {bowler_name}\n")

        vs_team = conn.execute(f"""
            SELECT opposition, matches, balls, runs_conceded, wickets, economy,
                   average, strike_rate, dot_ball_pct, boundary_conceded_pct, sample_size
            FROM analytics_ipl_bowler_vs_team
            WHERE bowler_id = '{bowler_id}'
              AND sample_size IN ('MEDIUM', 'HIGH')
            ORDER BY wickets DESC
        """).fetchall()

        if vs_team:
            md.append(
                "| Opposition | Matches | Balls | Runs | Wkts | Econ | Avg | SR | Dot% | Bound% | Sample |"
            )
            md.append(
                "|------------|---------|-------|------|------|------|-----|-----|------|--------|--------|"
            )
            for row in vs_team:
                opp, m, balls, runs, wkts, econ, avg, sr, dot, bound, sample = row
                md.append(
                    f"| {opp} | {m} | {balls} | {runs} | {wkts} | {econ or '-'} | {avg or '-'} | {sr or '-'} | {dot or '-'} | {bound or '-'} | {sample or '-'} |"
                )

    # ==========================================================================
    # SECTION 8: PLAYER VENUE PERFORMANCE
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 8. Key Player Venue Performance\n")

    # Top batter venue stats
    md.append("### 8.1 Top Batters by Venue\n")

    batter_venues = conn.execute(f"""
        SELECT bv.batter_name, bv.venue, bv.innings, bv.runs, bv.balls,
               bv.strike_rate, bv.average, bv.boundary_pct, bv.sample_size
        FROM analytics_ipl_batter_venue bv
        JOIN ipl_2026_squads sq ON bv.batter_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bv.sample_size IN ('MEDIUM', 'HIGH')
          AND bv.runs >= 100
        ORDER BY bv.batter_name, bv.runs DESC
    """).fetchall()

    if batter_venues:
        md.append("| Player | Venue | Inn | Runs | Balls | SR | Avg | Bound% | Sample |")
        md.append("|--------|-------|-----|------|-------|-----|-----|--------|--------|")
        for row in batter_venues:
            name, venue, inn, runs, balls, sr, avg, bound, sample = row
            venue_short = venue[:35] + "..." if len(venue) > 35 else venue
            md.append(
                f"| {name} | {venue_short} | {inn} | {runs} | {balls} | {sr or '-'} | {avg or '-'} | {bound or '-'} | {sample or '-'} |"
            )

    # ==========================================================================
    # SECTION 9: INSIGHTS & RECOMMENDATIONS
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 9. Andy Flower's Tactical Insights\n")

    # Identify death bowling options
    death_specialists = conn.execute(f"""
        SELECT bpd.bowler_name, bpd.overs, bpd.wickets, bpd.economy,
               bpd.pct_overs_in_phase, bpd.wicket_efficiency
        FROM analytics_ipl_bowler_phase_distribution bpd
        JOIN ipl_2026_squads sq ON bpd.bowler_id = sq.player_id
        WHERE sq.team_name = '{team_name}'
          AND bpd.match_phase = 'death'
          AND bpd.sample_size IN ('MEDIUM', 'HIGH')
          AND bpd.overs >= 10
        ORDER BY bpd.economy ASC
        LIMIT 3
    """).fetchall()

    md.append("\n### 9.1 Death Bowling Options\n")
    if death_specialists:
        for name, overs, wkts, econ, pct, eff in death_specialists:
            eff_note = "over-performs" if eff and eff > 0 else "workload matches output"
            md.append(
                f"- **{name}**: {overs:.1f} overs, {wkts} wickets, {econ} economy ({eff_note})"
            )
    else:
        md.append("*Insufficient data for death bowling analysis*")

    # Powerplay batting options
    pp_hitters = conn.execute(f"""
        SELECT player_name, innings, runs, strike_rate, boundary_pct
        FROM analytics_ipl_squad_batting_phase
        WHERE team_name = '{team_name}'
          AND match_phase = 'powerplay'
          AND sample_size IN ('MEDIUM', 'HIGH')
          AND strike_rate >= 130
        ORDER BY strike_rate DESC
        LIMIT 3
    """).fetchall()

    md.append("\n### 9.2 Powerplay Batting Options\n")
    if pp_hitters:
        for name, inn, runs, sr, bound in pp_hitters:
            md.append(f"- **{name}**: SR {sr}, Boundary% {bound}% ({inn} innings)")
    else:
        md.append("*Insufficient data for powerplay batting analysis*")

    # Spin vulnerability check - show ALL vulnerabilities per player
    # Uses correct bowling type names from dim_bowler_classification
    # Vulnerability criteria: SR < 110 OR avg < 12 OR (dismissals >= 3 AND bpd < 12)
    vs_spin = conn.execute(f"""
        SELECT
            batter_name,
            bowler_type,
            balls,
            runs,
            strike_rate,
            dismissals,
            average,
            ROUND(balls * 1.0 / NULLIF(dismissals, 0), 2) as balls_per_dismissal
        FROM analytics_ipl_batter_vs_bowler_type
        WHERE batter_id IN (SELECT player_id FROM ipl_2026_squads WHERE team_name = '{team_name}')
          AND bowler_type IN ('Right-arm off-spin', 'Right-arm leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin')
          AND sample_size IN ('MEDIUM', 'HIGH')
          AND (
              strike_rate < 110
              OR (average IS NOT NULL AND average < 12)
              OR (dismissals >= 3 AND balls * 1.0 / dismissals < 12)
          )
        ORDER BY batter_name, strike_rate ASC
    """).fetchall()

    md.append("\n### 9.3 Potential Spin Vulnerabilities\n")
    md.append(
        "*Note: Bowling style analysis covers 280 classified IPL bowlers (98.8% of balls). Some historical data may be excluded.*\n"
    )
    md.append("*Vulnerability criteria: SR < 110 OR Avg < 12 OR BPD < 12 (gets out too often)*\n")
    if vs_spin:
        for name, btype, balls, runs, sr, outs, avg, bpd in vs_spin:
            # Format bowling type for display (shorter names)
            btype_display = btype.replace("Right-arm ", "").replace("Left-arm ", "LA ")
            md.append(
                f"- **{name}** vs {btype_display}: SR {sr}, Avg {avg or 'N/A'}, BPD {bpd or 'N/A'} ({balls} balls)"
            )
    else:
        md.append("*No significant spin vulnerabilities identified*")

    md.append("\n---\n")
    md.append(f"*End of {team_name} Stat Pack*")

    return "\n".join(md)


def main():
    """Generate stat packs for all 10 IPL teams."""

    print("=" * 60)
    print("Cricket Playbook - IPL 2026 Stat Pack Generator")
    print("=" * 60)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Connect to database
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return 1

    conn = duckdb.connect(str(DB_PATH), read_only=True)

    # Load player tags
    print("Loading player tags...")
    tags_data = load_player_tags()
    tags_lookup = get_player_tags_lookup(tags_data)
    print(f"  Loaded tags for {len(tags_lookup)} players\n")

    # Get all teams
    teams = conn.execute("""
        SELECT DISTINCT team_name FROM ipl_2026_squads ORDER BY team_name
    """).fetchall()

    print(f"Generating stat packs for {len(teams)} teams...\n")

    for (team_name,) in teams:
        team_code = TEAM_CODES.get(team_name, team_name[:3].upper())
        print(f"  Generating {team_code} stat pack...")

        try:
            stat_pack = generate_team_stat_pack(conn, team_name, tags_lookup)

            # Write to file
            filename = f"{team_code}_stat_pack.md"
            filepath = OUTPUT_DIR / filename
            filepath.write_text(stat_pack)

            print(f"    -> {filepath}")
        except Exception as e:
            print(f"    ERROR: {e}")

    conn.close()

    print()
    print("=" * 60)
    print(f"Stat packs generated in: {OUTPUT_DIR}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
