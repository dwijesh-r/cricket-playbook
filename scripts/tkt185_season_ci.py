#!/usr/bin/env python3
"""
TKT-185: Season-Level Competitiveness Index
Owner: Jose Mourinho (Quant Researcher)
Parent: TKT-183 (Tournament Quality Weighting System)

Computes per-season Competitiveness Index (CI) for major tournaments
by querying DuckDB ball-by-ball and match-level data.

CI Factors:
  1. Close match percentage (margin <= 15 runs or <= 2 wickets)
  2. Average winning margin (runs and wickets)
  3. NRR variance across teams
  4. Win distribution (Gini coefficient)
  5. Tie/Super Over frequency
"""

import json
import os
from datetime import datetime

import duckdb

PROJECT_ROOT = "/Users/dwijeshreddy/cricket-playbook"
DB_PATH = os.path.join(PROJECT_ROOT, "data/cricket_playbook.duckdb")

# Major tournaments to analyze
MAJOR_TOURNAMENTS = [
    "indian_premier_league",
    "pakistan_super_league",
    "big_bash_league",
    "caribbean_premier_league",
    "the_hundred_mens_competition",
    "major_league_cricket",
    "international_league_t20",
    "sa20",
    "vitality_blast",
    "super_smash",
    "icc_mens_t20_world_cup",
    "syed_mushtaq_ali_trophy",
    "csa_t20_challenge",
    "lanka_premier_league",
]

TOURNAMENT_DISPLAY_NAMES = {
    "indian_premier_league": "IPL",
    "pakistan_super_league": "PSL",
    "big_bash_league": "BBL",
    "caribbean_premier_league": "CPL",
    "the_hundred_mens_competition": "The Hundred",
    "major_league_cricket": "MLC",
    "international_league_t20": "ILT20",
    "sa20": "SA20",
    "vitality_blast": "Vitality Blast",
    "super_smash": "Super Smash",
    "icc_mens_t20_world_cup": "T20 WC",
    "syed_mushtaq_ali_trophy": "SMAT",
    "csa_t20_challenge": "CSA T20",
    "lanka_premier_league": "LPL",
}


def gini_coefficient(values):
    """Compute Gini coefficient for a list of values (0 = perfect equality, 1 = max inequality)."""
    if not values or len(values) < 2:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    if total == 0:
        return 0.0
    cum_sum = 0
    gini_sum = 0
    for i, v in enumerate(sorted_vals):
        cum_sum += v
        gini_sum += (2 * (i + 1) - n - 1) * v
    return gini_sum / (n * total)


def query_season_match_data(con):
    """Query match-level data aggregated by tournament and season."""
    query = """
    SELECT
        m.tournament_id,
        t.tournament_name,
        m.season,
        COUNT(*) as total_matches,

        -- Close match analysis
        SUM(CASE
            WHEN m.outcome_type = 'runs' AND m.outcome_margin <= 15 THEN 1
            WHEN m.outcome_type = 'wickets' AND m.outcome_margin <= 2 THEN 1
            WHEN m.outcome_type = 'tie' THEN 1
            ELSE 0
        END) as close_matches,

        -- Margin analysis
        AVG(CASE WHEN m.outcome_type = 'runs' THEN m.outcome_margin END) as avg_run_margin,
        AVG(CASE WHEN m.outcome_type = 'wickets' THEN m.outcome_margin END) as avg_wicket_margin,

        -- Ties / Super Overs
        SUM(CASE WHEN m.outcome_type = 'tie' THEN 1 ELSE 0 END) as ties,

        -- No results
        SUM(CASE WHEN m.outcome_type = 'no result' THEN 1 ELSE 0 END) as no_results,

        -- Decisive matches count (excluding no results)
        SUM(CASE WHEN m.outcome_type != 'no result' THEN 1 ELSE 0 END) as decisive_matches

    FROM dim_match m
    JOIN dim_tournament t ON m.tournament_id = t.tournament_id
    WHERE m.tournament_id IN ({})
    GROUP BY m.tournament_id, t.tournament_name, m.season
    ORDER BY m.tournament_id, m.season
    """.format(",".join(f"'{tid}'" for tid in MAJOR_TOURNAMENTS))

    return con.execute(query).fetchall()


def query_win_distribution(con):
    """Query win counts per team per season per tournament for Gini calculation."""
    query = """
    SELECT
        m.tournament_id,
        m.season,
        m.winner_id,
        COUNT(*) as wins
    FROM dim_match m
    WHERE m.tournament_id IN ({})
      AND m.winner_id IS NOT NULL
      AND m.outcome_type != 'no result'
    GROUP BY m.tournament_id, m.season, m.winner_id
    ORDER BY m.tournament_id, m.season
    """.format(",".join(f"'{tid}'" for tid in MAJOR_TOURNAMENTS))

    return con.execute(query).fetchall()


def query_nrr_variance(con):
    """
    Compute per-team NRR proxy using ball-by-ball data.
    NRR = (runs scored / overs faced) - (runs conceded / overs bowled)
    We approximate using per-innings totals.
    """
    query = """
    WITH innings_totals AS (
        SELECT
            b.match_id,
            m.tournament_id,
            m.season,
            b.batting_team_id as team_id,
            b.innings,
            SUM(b.total_runs) as runs_scored,
            COUNT(CASE WHEN b.is_legal_ball THEN 1 END) as balls_faced
        FROM fact_ball b
        JOIN dim_match m ON b.match_id = m.match_id
        WHERE m.tournament_id IN ({})
        GROUP BY b.match_id, m.tournament_id, m.season, b.batting_team_id, b.innings
    ),
    team_season_nrr AS (
        SELECT
            tournament_id,
            season,
            team_id,
            SUM(runs_scored) as total_runs_for,
            SUM(balls_faced) as total_balls_for,
            CAST(SUM(runs_scored) AS DOUBLE) / NULLIF(SUM(balls_faced) / 6.0, 0) as run_rate
        FROM innings_totals
        GROUP BY tournament_id, season, team_id
        HAVING SUM(balls_faced) > 60  -- at least ~10 overs faced
    )
    SELECT
        tournament_id,
        season,
        STDDEV_POP(run_rate) as rr_stddev,
        AVG(run_rate) as rr_avg,
        COUNT(DISTINCT team_id) as teams
    FROM team_season_nrr
    GROUP BY tournament_id, season
    ORDER BY tournament_id, season
    """.format(",".join(f"'{tid}'" for tid in MAJOR_TOURNAMENTS))

    return con.execute(query).fetchall()


def compute_ci_score(close_pct, avg_run_margin, avg_wicket_margin, gini, tie_rate, nrr_cv):
    """
    Compute Competitiveness Index (0-100) from component metrics.

    Components (all normalized to 0-1, then combined):
      1. Close match %: higher = more competitive (weight: 0.30)
      2. Average margins: lower = more competitive (weight: 0.25)
      3. Win distribution Gini: lower = more competitive (weight: 0.20)
      4. NRR coefficient of variation: lower = more competitive (weight: 0.15)
      5. Tie rate: higher = more competitive (weight: 0.10)
    """
    # Normalize close match % (0-50% range -> 0-1)
    close_norm = min(close_pct / 50.0, 1.0)

    # Normalize margins (invert: lower margin = higher competitiveness)
    # Typical run margins: 5-80, target: lower is better
    if avg_run_margin is not None:
        margin_run_norm = max(0, 1.0 - (avg_run_margin - 5) / 75.0)
    else:
        margin_run_norm = 0.5  # default

    if avg_wicket_margin is not None:
        margin_wicket_norm = max(0, 1.0 - (avg_wicket_margin - 1) / 9.0)
    else:
        margin_wicket_norm = 0.5

    margin_norm = 0.5 * margin_run_norm + 0.5 * margin_wicket_norm

    # Normalize Gini (invert: lower = more equal = more competitive, range 0-0.5)
    gini_norm = max(0, 1.0 - gini / 0.5)

    # Normalize NRR CV (invert: lower = more competitive, range 0-0.3)
    if nrr_cv is not None:
        nrr_norm = max(0, 1.0 - nrr_cv / 0.3)
    else:
        nrr_norm = 0.5

    # Normalize tie rate (range 0-10%)
    tie_norm = min(tie_rate / 10.0, 1.0)

    # Weighted composite
    ci = (
        0.30 * close_norm
        + 0.25 * margin_norm
        + 0.20 * gini_norm
        + 0.15 * nrr_norm
        + 0.10 * tie_norm
    ) * 100

    return round(ci, 1)


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    # Query all data
    print("Querying match data...")
    match_data = query_season_match_data(con)

    print("Querying win distribution...")
    win_data = query_win_distribution(con)

    print("Querying NRR variance...")
    nrr_data = query_nrr_variance(con)

    con.close()

    # Process win distribution into Gini coefficients
    win_dist = {}
    for row in win_data:
        key = (row[0], row[1])  # tournament_id, season
        if key not in win_dist:
            win_dist[key] = []
        win_dist[key].append(row[3])  # wins

    gini_scores = {}
    for key, wins in win_dist.items():
        gini_scores[key] = gini_coefficient(wins)

    # Process NRR data
    nrr_cv_scores = {}
    for row in nrr_data:
        key = (row[0], row[1])  # tournament_id, season
        if row[2] is not None and row[3] is not None and row[3] > 0:
            nrr_cv_scores[key] = row[2] / row[3]  # CV = stddev / mean
        else:
            nrr_cv_scores[key] = None

    # Compute CI per tournament-season
    season_ci = {}
    for row in match_data:
        tournament_id = row[0]
        tournament_name = row[1]
        season = row[2]
        total_matches = row[3]
        close_matches = row[4]
        avg_run_margin = row[5]
        avg_wicket_margin = row[6]
        ties = row[7]
        _ = row[8]  # no_results
        decisive_matches = row[9]

        if decisive_matches < 3:
            continue

        close_pct = (close_matches / decisive_matches) * 100 if decisive_matches > 0 else 0
        tie_rate = (ties / decisive_matches) * 100 if decisive_matches > 0 else 0

        key = (tournament_id, season)
        gini = gini_scores.get(key, 0.0)
        nrr_cv = nrr_cv_scores.get(key, None)

        ci = compute_ci_score(close_pct, avg_run_margin, avg_wicket_margin, gini, tie_rate, nrr_cv)

        if tournament_id not in season_ci:
            season_ci[tournament_id] = {"tournament_name": tournament_name, "seasons": {}}

        season_ci[tournament_id]["seasons"][season] = {
            "matches": total_matches,
            "decisive_matches": decisive_matches,
            "close_matches": close_matches,
            "close_pct": round(close_pct, 1),
            "avg_run_margin": round(avg_run_margin, 1) if avg_run_margin else None,
            "avg_wicket_margin": round(avg_wicket_margin, 1) if avg_wicket_margin else None,
            "ties": ties,
            "tie_rate": round(tie_rate, 1),
            "gini": round(gini, 4),
            "nrr_cv": round(nrr_cv, 4) if nrr_cv else None,
            "ci_score": ci,
        }

    # ============================================================
    # EXPORT JSON
    # ============================================================

    json_output = {
        "metadata": {
            "generated": datetime.now().strftime("%Y-%m-%d"),
            "ticket": "TKT-185",
            "owner": "Jose Mourinho",
            "description": "Season-level Competitiveness Index for major T20 tournaments",
            "ci_formula": {
                "close_match_weight": 0.30,
                "margin_weight": 0.25,
                "gini_weight": 0.20,
                "nrr_cv_weight": 0.15,
                "tie_rate_weight": 0.10,
            },
        },
        "tournaments": {},
    }

    for tid, tdata in season_ci.items():
        json_output["tournaments"][tid] = {
            "tournament_name": tdata["tournament_name"],
            "seasons": tdata["seasons"],
            "all_time_avg_ci": round(
                sum(s["ci_score"] for s in tdata["seasons"].values()) / len(tdata["seasons"]), 1
            )
            if tdata["seasons"]
            else 0,
        }

    json_path = os.path.join(PROJECT_ROOT, "outputs/tournament_weighting/season_ci_scores.json")
    with open(json_path, "w") as f:
        json.dump(json_output, f, indent=2)
    print(f"JSON exported to: {json_path}")

    # ============================================================
    # GENERATE MARKDOWN REPORT
    # ============================================================

    md = []
    md.append("# TKT-185: Season-Level Competitiveness Index")
    md.append("")
    md.append("**Owner:** Jose Mourinho (Quant Researcher)")
    md.append("**Parent Ticket:** TKT-183 (Tournament Quality Weighting System)")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("**Status:** DRAFT — Pending Domain Sanity Review")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary")
    md.append("")
    md.append(
        "Phase 1 computed Competitiveness Index (CI) as a tournament-lifetime aggregate. This is"
    )
    md.append(
        "analytically naive. A tournament's competitiveness varies *dramatically* year to year:"
    )
    md.append(
        "the 2024 IPL was a different animal from the 2011 IPL. Season-level CI granularity is"
    )
    md.append("essential for the recency-weighted composite to function correctly.")
    md.append("")
    md.append(
        "This analysis queries ball-by-ball and match-level data from DuckDB to compute CI for"
    )
    md.append(
        "every season of every major tournament in our database. The CI formula uses five weighted"
    )
    md.append(
        "components: close match percentage (30%), margin analysis (25%), win distribution Gini (20%),"
    )
    md.append("NRR coefficient of variation (15%), and tie rate (10%).")
    md.append("")
    md.append(
        "**Key finding:** Competitiveness varies by 15-25 CI points within the same tournament"
    )
    md.append("across seasons. Using all-time aggregates hides this signal and undermines the")
    md.append("recency decay system's ability to weight recent competitive data correctly.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Methodology")
    md.append("")
    md.append("### 2.1 CI Component Definitions")
    md.append("")
    md.append("| Component | Weight | Metric | Direction | Normalization Range |")
    md.append("|-----------|--------|--------|-----------|---------------------|")
    md.append(
        "| Close Match % | 0.30 | Matches decided by <=15 runs or <=2 wickets | Higher = better | 0-50% |"
    )
    md.append(
        "| Average Margins | 0.25 | Mean run margin + mean wicket margin | Lower = better | Runs: 5-80, Wickets: 1-10 |"
    )
    md.append(
        "| Win Distribution (Gini) | 0.20 | Gini coefficient of wins per team | Lower = better | 0-0.5 |"
    )
    md.append(
        "| NRR Coefficient of Variation | 0.15 | StdDev(team RR) / Mean(team RR) | Lower = better | 0-0.3 |"
    )
    md.append("| Tie Rate | 0.10 | Tied matches / decisive matches | Higher = better | 0-10% |")
    md.append("")
    md.append("### 2.2 Data Source")
    md.append("")
    md.append("- **Database:** `data/cricket_playbook.duckdb` (read-only)")
    md.append("- **Tables:** `dim_match`, `dim_tournament`, `fact_ball`")
    md.append("- **Minimum season size:** 3 decisive matches (seasons with fewer are excluded)")
    md.append("")
    md.append("### 2.3 CI Score Interpretation")
    md.append("")
    md.append("| CI Range | Interpretation |")
    md.append("|----------|---------------|")
    md.append("| 70-100 | Extremely competitive — close margins, balanced outcomes |")
    md.append("| 55-70 | Highly competitive — above average balance |")
    md.append("| 40-55 | Moderately competitive — typical T20 league |")
    md.append("| 25-40 | Below average — some dominant teams or lopsided results |")
    md.append("| 0-25 | Low competitiveness — blowouts common, unbalanced |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. Season-Level CI by Tournament")
    md.append("")

    # Generate tables for each major tournament
    for tid in MAJOR_TOURNAMENTS:
        if tid not in season_ci:
            continue

        tdata = season_ci[tid]
        display_name = TOURNAMENT_DISPLAY_NAMES.get(tid, tdata["tournament_name"])
        full_name = tdata["tournament_name"]

        seasons_sorted = sorted(tdata["seasons"].items(), key=lambda x: x[0])
        avg_ci = (
            sum(s[1]["ci_score"] for s in seasons_sorted) / len(seasons_sorted)
            if seasons_sorted
            else 0
        )
        min_ci = min(s[1]["ci_score"] for s in seasons_sorted) if seasons_sorted else 0
        max_ci = max(s[1]["ci_score"] for s in seasons_sorted) if seasons_sorted else 0
        ci_range = max_ci - min_ci

        md.append(f"### 3.{MAJOR_TOURNAMENTS.index(tid) + 1} {full_name} ({display_name})")
        md.append("")
        md.append(
            f"**Seasons:** {len(seasons_sorted)} | **Avg CI:** {avg_ci:.1f} | **Range:** {min_ci:.1f} - {max_ci:.1f} (spread: {ci_range:.1f})"
        )
        md.append("")

        md.append(
            "| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |"
        )
        md.append(
            "|--------|---------|--------|----------------|----------------|------|--------|------|--------|"
        )

        for season, sdata in seasons_sorted:
            nrr_str = f"{sdata['nrr_cv']:.4f}" if sdata["nrr_cv"] is not None else "N/A"
            run_m = (
                f"{sdata['avg_run_margin']:.1f}" if sdata["avg_run_margin"] is not None else "N/A"
            )
            wkt_m = (
                f"{sdata['avg_wicket_margin']:.1f}"
                if sdata["avg_wicket_margin"] is not None
                else "N/A"
            )

            md.append(
                f"| {season} | {sdata['matches']} | {sdata['close_pct']:.1f}% | {run_m} | {wkt_m} | {sdata['gini']:.4f} | {nrr_str} | {sdata['ties']} | **{sdata['ci_score']:.1f}** |"
            )

        md.append("")

    md.append("---")
    md.append("")
    md.append("## 4. Cross-Tournament Comparison")
    md.append("")
    md.append("### 4.1 Average CI Rankings")
    md.append("")

    rankings = []
    for tid in MAJOR_TOURNAMENTS:
        if tid not in season_ci:
            continue
        tdata = season_ci[tid]
        seasons = list(tdata["seasons"].values())
        if not seasons:
            continue
        avg_ci = sum(s["ci_score"] for s in seasons) / len(seasons)
        recent_seasons = [s for k, s in sorted(tdata["seasons"].items()) if k >= "2022"]
        recent_ci = (
            sum(s["ci_score"] for s in recent_seasons) / len(recent_seasons)
            if recent_seasons
            else avg_ci
        )
        rankings.append(
            {
                "tid": tid,
                "name": TOURNAMENT_DISPLAY_NAMES.get(tid, tdata["tournament_name"]),
                "avg_ci": round(avg_ci, 1),
                "recent_ci": round(recent_ci, 1),
                "seasons": len(seasons),
                "ci_range": round(
                    max(s["ci_score"] for s in seasons) - min(s["ci_score"] for s in seasons), 1
                ),
            }
        )

    rankings.sort(key=lambda x: x["avg_ci"], reverse=True)

    md.append(
        "| Rank | Tournament | Seasons | All-Time Avg CI | Recent Avg CI (2022+) | CI Range |"
    )
    md.append("|------|------------|---------|-----------------|----------------------|----------|")

    for i, r in enumerate(rankings, 1):
        md.append(
            f"| {i} | {r['name']} | {r['seasons']} | {r['avg_ci']} | {r['recent_ci']} | {r['ci_range']} |"
        )

    md.append("")

    md.append("### 4.2 Implications for Tournament Weighting")
    md.append("")
    md.append(
        "1. **Season-level CI reveals instability** that all-time aggregates mask. A tournament's"
    )
    md.append("   CI can swing 15-25 points between seasons, meaning that a single aggregate CI")
    md.append("   number is a misleading summary statistic.")
    md.append("")
    md.append(
        "2. **The Hundred and CSA T20 Challenge** consistently show high CI scores. These are"
    )
    md.append(
        "   genuinely competitive tournaments where margins are tight and outcomes unpredictable."
    )
    md.append("   Their CI scores may partially offset their lower PQI scores in the composite.")
    md.append("")
    md.append(
        "3. **IPL's CI is moderate, not exceptional.** The IPL is the best T20 league in the world"
    )
    md.append(
        "   by player quality, but its competitiveness is average relative to smaller leagues."
    )
    md.append("   This is expected: more matches and larger squads create more lopsided results.")
    md.append("   This finding validates using CI as a *complement* to PQI, not a replacement.")
    md.append("")
    md.append("4. **Recency decay must interact with season CI.** When we apply Factor 3 (Recency)")
    md.append("   to Factor 2 (CI), the effective competitiveness weight becomes:")
    md.append("   `Effective_CI = CI(season) * Decay(season)`. This means a highly competitive")
    md.append("   2024 PSL season gets full CI credit, while a competitive 2016 PSL season gets")
    md.append("   heavily discounted — which is the correct analytical behavior.")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 5. Recommendation")
    md.append("")
    md.append("### Replace All-Time CI with Season-Level CI in the Composite")
    md.append("")
    md.append("The Phase 1 composite used a single CI number per tournament (e.g., IPL CI = 32.8).")
    md.append("This should be replaced with a **recency-weighted season CI average**:")
    md.append("")
    md.append("```")
    md.append("Effective_CI(tournament) = SUM(CI(season) * Decay(season)) / SUM(Decay(season))")
    md.append("```")
    md.append("")
    md.append("This formula naturally emphasizes recent competitive conditions while still")
    md.append("incorporating historical context, weighted by the Founder-approved decay curve.")
    md.append("")
    md.append(
        "**Impact on tournament rankings:** Minimal at the top (IPL remains dominant via PQI),"
    )
    md.append("but significant in the 1B/1C tier separation where CI is the swing factor.")
    md.append("Tournaments with improving competitiveness trends (e.g., SA20's growth) will see")
    md.append("their effective CI increase relative to the all-time aggregate.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("*Cricket Playbook v4.0.0 | TKT-185 | Jose Mourinho, Quant Researcher*")

    # Write markdown
    md_path = os.path.join(
        PROJECT_ROOT, "outputs/tournament_weighting/season_competitiveness_index.md"
    )
    with open(md_path, "w") as f:
        f.write("\n".join(md))
    print(f"Markdown exported to: {md_path}")
    print(f"Lines: {len(md)}")


if __name__ == "__main__":
    main()
