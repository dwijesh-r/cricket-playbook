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
PROJECT_DIR = SCRIPT_DIR.parent
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


def get_opposition_clause(team_name: str) -> str:
    """Generate SQL IN clause for opposition team names (handles aliases)."""
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    return ", ".join([f"'{a}'" for a in aliases])


def generate_team_stat_pack(conn, team_name: str, tags_lookup: dict) -> str:
    """Generate comprehensive stat pack for a team."""

    team_code = TEAM_CODES.get(team_name, team_name[:3].upper())
    aliases = FRANCHISE_ALIASES.get(team_name, [team_name])
    alias_clause = ", ".join([f"'{a}'" for a in aliases])

    md = []
    md.append(f"# {team_name} ({team_code}) - IPL 2026 Stat Pack")
    md.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("**Data Source:** Cricket Playbook Analytics Engine")
    md.append(
        "**Prepared by:** Tom Brady (PO), Stephen Curry (Analytics), Andy Flower (Cricket)"
    )
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
        "\n**Role Breakdown:** "
        + ", ".join([f"{k}: {v}" for k, v in sorted(role_counts.items())])
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
    md.append(
        "*Performance tags based on phase analysis, matchups, and specializations*\n"
    )

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
    # SECTION 3: VENUE PERFORMANCE
    # ==========================================================================
    md.append("\n---\n")
    md.append("## 3. Venue Performance\n")

    # Team batting at venues
    md.append("### 3.1 Team Batting by Venue (Top 10 by matches)\n")

    venue_batting = conn.execute(f"""
        WITH ipl_matches AS (
            SELECT dm.match_id, dv.venue_name as venue
            FROM dim_match dm
            JOIN dim_tournament dt ON dm.tournament_id = dt.tournament_id
            JOIN dim_venue dv ON dm.venue_id = dv.venue_id
            WHERE dt.tournament_name = 'Indian Premier League'
        ),
        team_balls AS (
            SELECT
                im.venue,
                COUNT(DISTINCT fb.match_id) as matches,
                COUNT(*) as balls,
                SUM(fb.batter_runs) as runs,
                SUM(CASE WHEN fb.is_wicket AND fb.player_out_id = fb.batter_id THEN 1 ELSE 0 END) as wickets
            FROM fact_ball fb
            JOIN dim_team dt ON fb.batting_team_id = dt.team_id
            JOIN ipl_matches im ON fb.match_id = im.match_id
            WHERE dt.team_name IN ({alias_clause})
              AND fb.is_legal_ball = TRUE
            GROUP BY im.venue
        )
        SELECT venue, matches, runs, balls, wickets,
               ROUND(runs * 100.0 / NULLIF(balls, 0), 2) as sr,
               ROUND(runs * 1.0 / NULLIF(wickets, 0), 2) as avg
        FROM team_balls
        WHERE matches >= 3
        ORDER BY matches DESC
        LIMIT 10
    """).fetchall()

    md.append("| Venue | Matches | Runs | Balls | SR | Avg |")
    md.append("|-------|---------|------|-------|-----|-----|")
    for row in venue_batting:
        venue, matches, runs, balls, wkts, sr, avg = row
        venue_short = venue[:40] + "..." if len(venue) > 40 else venue
        md.append(
            f"| {venue_short} | {matches} | {runs} | {balls} | {sr or '-'} | {avg or '-'} |"
        )

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

    md.append(
        "| Player | Phase | Inn | Runs | Balls | SR | Avg | Bound% | Dot% | Sample |"
    )
    md.append(
        "|--------|-------|-----|------|-------|-----|-----|--------|------|--------|"
    )
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
        md.append(
            "| Player | Venue | Inn | Runs | Balls | SR | Avg | Bound% | Sample |"
        )
        md.append(
            "|--------|-------|-----|------|-------|-----|-----|--------|--------|"
        )
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

    # Left-arm spin vulnerability check
    vs_spin = conn.execute(f"""
        SELECT batter_name, bowler_type, balls, runs, strike_rate, dismissals, average
        FROM analytics_ipl_batter_vs_bowler_type
        WHERE batter_id IN (SELECT player_id FROM ipl_2026_squads WHERE team_name = '{team_name}')
          AND bowler_type IN ('Off-spin', 'Leg-spin', 'Left-arm orthodox', 'Left-arm wrist spin')
          AND sample_size IN ('MEDIUM', 'HIGH')
          AND strike_rate < 115
        ORDER BY strike_rate ASC
        LIMIT 5
    """).fetchall()

    md.append("\n### 9.3 Potential Spin Vulnerabilities\n")
    md.append(
        "*Note: Bowling style analysis covers 280 classified IPL bowlers (98.8% of balls). Some historical data may be excluded.*\n"
    )
    if vs_spin:
        for name, btype, balls, runs, sr, outs, avg in vs_spin:
            md.append(
                f"- **{name}** vs {btype}: SR {sr}, Avg {avg or 'N/A'} ({balls} balls)"
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
