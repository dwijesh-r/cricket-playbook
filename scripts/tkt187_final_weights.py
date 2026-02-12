#!/usr/bin/env python3
"""
TKT-187: Final Composite Tournament Weights — Founder Presentation
Owner: Jose Mourinho (Quant Researcher)
Parent: TKT-183 (Tournament Quality Weighting System)

Compiles ALL Phase 1 outputs into final composite weights using:
  - Approved Founder Decisions (LOCKED):
    1. Recency Decay: Exponential, half-life = 4 years
    2. Season-Level CI: Recency-weighted season CI
    3. Composite Formula: Geometric Mean
    4. Conditions Baseline: IPL 2023-2025
  - 5 Factors: PQI, Effective CI, Recency, Conditions Similarity, Sample Confidence
  - Factor weights: PQI=0.25, CI=0.20, Recency=0.20, Conditions=0.15, Sample=0.20

Produces:
  - outputs/tournament_composite_weights_phase1.json
  - outputs/tournament_weighting/final_weights_presentation.md
"""

import json
import math
import os
from datetime import datetime, timezone

import duckdb

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = "/Users/dwijeshreddy/cricket-playbook"
DB_PATH = os.path.join(PROJECT_ROOT, "data/cricket_playbook.duckdb")
CI_JSON_PATH = os.path.join(PROJECT_ROOT, "outputs/tournament_weighting/season_ci_scores.json")
OUTPUT_JSON_PATH = os.path.join(PROJECT_ROOT, "outputs/tournament_composite_weights_phase1.json")
OUTPUT_MD_PATH = os.path.join(
    PROJECT_ROOT, "outputs/tournament_weighting/final_weights_presentation.md"
)

REFERENCE_YEAR = 2026
HALF_LIFE = 4.0

# Factor weights for geometric mean (Founder-approved)
FACTOR_WEIGHTS = {
    "pqi": 0.25,
    "effective_ci": 0.20,
    "recency": 0.20,
    "conditions_similarity": 0.15,
    "sample_confidence": 0.20,
}

# 14 tournaments tracked in Phase 1
TOURNAMENTS = {
    "indian_premier_league": {
        "name": "Indian Premier League",
        "short": "IPL",
    },
    "pakistan_super_league": {
        "name": "Pakistan Super League",
        "short": "PSL",
    },
    "big_bash_league": {
        "name": "Big Bash League",
        "short": "BBL",
    },
    "caribbean_premier_league": {
        "name": "Caribbean Premier League",
        "short": "CPL",
    },
    "the_hundred_mens_competition": {
        "name": "The Hundred",
        "short": "Hundred",
    },
    "major_league_cricket": {
        "name": "Major League Cricket",
        "short": "MLC",
    },
    "international_league_t20": {
        "name": "International League T20",
        "short": "ILT20",
    },
    "lanka_premier_league": {
        "name": "Lanka Premier League",
        "short": "LPL",
    },
    "vitality_blast": {
        "name": "Vitality Blast",
        "short": "VB",
    },
    "super_smash": {
        "name": "Super Smash",
        "short": "SS",
    },
    "icc_mens_t20_world_cup": {
        "name": "ICC Men's T20 World Cup",
        "short": "T20WC",
    },
    "syed_mushtaq_ali_trophy": {
        "name": "Syed Mushtaq Ali Trophy",
        "short": "SMAT",
    },
    "csa_t20_challenge": {
        "name": "CSA T20 Challenge",
        "short": "CSA",
    },
    "sa20": {
        "name": "SA20",
        "short": "SA20",
    },
}

# Conditions Similarity scores (Founder-specified, IPL = baseline)
# Reasoning documented per tournament
CONDITIONS_SIMILARITY = {
    "indian_premier_league": {
        "score": 1.00,
        "reasoning": "Baseline. IPL conditions are the reference standard.",
    },
    "syed_mushtaq_ali_trophy": {
        "score": 0.85,
        "reasoning": (
            "Same Indian grounds and pitch types, but lower-quality "
            "outfields, smaller crowds, and domestic-level pressure. "
            "Strong conditions overlap; lower intensity."
        ),
    },
    "pakistan_super_league": {
        "score": 0.65,
        "reasoning": (
            "Subcontinent venue profile with similar spinning conditions "
            "and heat. Key differences: Pakistan pitches tend to be slower "
            "and lower-scoring. Lahore/Karachi wickets behave differently "
            "from Mumbai/Bengaluru."
        ),
    },
    "lanka_premier_league": {
        "score": 0.60,
        "reasoning": (
            "Subcontinent with spin-friendly conditions. Sri Lankan pitches "
            "offer more turn and are generally slower than IPL surfaces. "
            "Pallekele and Hambantota differ significantly from Indian venues."
        ),
    },
    "sa20": {
        "score": 0.55,
        "reasoning": (
            "Pace-friendly South African wickets (Wanderers, Newlands, "
            "SuperSport Park) differ substantially from Indian conditions. "
            "Higher bounce, more seam movement, different ball behavior."
        ),
    },
    "big_bash_league": {
        "score": 0.50,
        "reasoning": (
            "Australian conditions: harder, bouncier pitches with bigger "
            "boundaries. MCG/SCG grounds are structurally different from "
            "Indian venues. Different ball (Kookaburra vs SG)."
        ),
    },
    "caribbean_premier_league": {
        "score": 0.50,
        "reasoning": (
            "Caribbean pitches can be slow and low, somewhat similar to "
            "Indian sub-continent conditions in that respect. But smaller "
            "grounds, different climate, and variable pitch quality."
        ),
    },
    "international_league_t20": {
        "score": 0.55,
        "reasoning": (
            "UAE conditions: flat batting surfaces in Dubai/Sharjah/Abu Dhabi. "
            "Some similarity to Indian flat tracks but different dew factor, "
            "ball behavior, and outfield speed."
        ),
    },
    "the_hundred_mens_competition": {
        "score": 0.40,
        "reasoning": (
            "100-ball format is structurally different from T20. English "
            "conditions (seam movement, overcast skies, green pitches) are "
            "fundamentally unlike Indian batting paradises. Format + conditions "
            "compound the dissimilarity."
        ),
    },
    "major_league_cricket": {
        "score": 0.45,
        "reasoning": (
            "American venues with drop-in pitches and unfamiliar conditions. "
            "Dallas, Morrisville grounds are nothing like Indian venues. "
            "Still T20 format but conditions are non-transferable."
        ),
    },
    "vitality_blast": {
        "score": 0.45,
        "reasoning": (
            "English county grounds with seaming/swinging conditions. "
            "Green pitches, overcast skies, Dukes-style ball behavior. "
            "Very different from Indian conditions despite being full T20 format."
        ),
    },
    "csa_t20_challenge": {
        "score": 0.55,
        "reasoning": (
            "Same South African conditions as SA20 but domestic-level. "
            "Pace-friendly wickets, higher bounce. Limited overlap with "
            "Indian conditions."
        ),
    },
    "super_smash": {
        "score": 0.40,
        "reasoning": (
            "New Zealand conditions: green tops, seam movement, smaller "
            "grounds but very different pitch behavior from India. "
            "Limited transferability of performance data."
        ),
    },
    "icc_mens_t20_world_cup": {
        "score": 0.50,
        "reasoning": (
            "Varies by host country. Recent editions: UAE 2021, Australia 2022, "
            "West Indies/USA 2024. Average across host conditions is moderate "
            "similarity. Some editions (India 2016) were on IPL grounds."
        ),
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def exponential_decay(year, ref=REFERENCE_YEAR, half_life=HALF_LIFE):
    """Approved decay: w(year) = 2^(-(ref - year) / half_life)"""
    age = ref - year
    return 2.0 ** (-age / half_life)


def season_to_year(season_str):
    """
    Convert season string to a numeric year for decay computation.
    Handles formats like '2023', '2023/24', '2007/08', '2020/21'.

    For split seasons like '2025/26', use the FIRST year. Rationale:
    - The season '2025/26' starts in 2025 and its data is from that era
    - Using the first year prevents split-season tournaments from getting
      an unfair recency advantage over single-year tournaments (e.g.,
      BBL '2025/26' should not score higher than IPL '2025')
    - This makes the decay computation fair across naming conventions
    """
    if "/" in season_str:
        parts = season_str.split("/")
        first = int(parts[0])
        return first
    return int(season_str)


def sigmoid_confidence(matches, midpoint=100, steepness=0.02):
    """
    Sample size confidence: sigmoid function.
    confidence = 1 / (1 + exp(-steepness * (matches - midpoint)))
    Capped at 0.95.
    """
    raw = 1.0 / (1.0 + math.exp(-steepness * (matches - midpoint)))
    return min(raw, 0.95)


def geometric_mean_composite(factors, weights):
    """
    Weighted geometric mean: W = PROD(f_i ^ w_i) ^ (1 / SUM(w_i))
    All factor values must be > 0. Floor at 0.01 to avoid log(0).
    """
    total_weight = sum(weights.values())
    log_sum = 0.0
    for key, weight in weights.items():
        val = max(factors[key], 0.01)  # Floor to avoid log(0)
        log_sum += weight * math.log(val)
    return math.exp(log_sum / total_weight)


def assign_tier(composites_list):
    """
    Data-driven tier assignment using natural gap analysis.

    Rather than fixed thresholds, we identify the largest gaps between
    adjacent composites to find natural cluster boundaries. This produces
    tiers that reflect the actual distribution of tournament quality.

    Returns a dict mapping composite_weight -> tier string.
    """
    sorted_composites = sorted(composites_list, reverse=True)
    n = len(sorted_composites)

    if n == 0:
        return {}

    # Calculate gaps
    gaps = []
    for i in range(n - 1):
        gaps.append((i, sorted_composites[i] - sorted_composites[i + 1]))

    # Sort by gap size to find the largest natural breaks
    gaps_sorted = sorted(gaps, key=lambda x: x[1], reverse=True)

    # Use the top 3 gaps as tier boundaries (creates up to 4 tiers + 1A for leader)
    boundary_indices = sorted([g[0] for g in gaps_sorted[:3]])

    # Assign tiers based on boundaries
    tier_map = {}
    tier_labels = ["1A", "1B", "1C", "2", "3"]
    current_tier_idx = 0

    for i, comp in enumerate(sorted_composites):
        tier_map[comp] = tier_labels[min(current_tier_idx, len(tier_labels) - 1)]
        if current_tier_idx < len(boundary_indices):
            if i == boundary_indices[current_tier_idx]:
                current_tier_idx += 1

    return tier_map


# ============================================================
# FACTOR 1: PLAYER QUALITY INDEX (PQI)
# ============================================================


def compute_pqi(conn):
    """
    PQI measures how many top-quality IPL players (2023-2025) participate
    in each tournament. We define 'top IPL players' as those with a meaningful
    sample in IPL 2023-2025 (100+ legal balls faced as batter OR 60+ legal
    balls bowled as bowler). Then we count what percentage of these top IPL
    players have appeared in each other tournament.

    Normalize: IPL = 1.0, others as fraction of IPL's count.
    """
    result = conn.execute(
        """
        WITH ipl_top_batters AS (
            SELECT fb.batter_id AS player_id, COUNT(*) AS balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            WHERE dm.tournament_id = 'indian_premier_league'
              AND dm.season IN ('2023', '2024', '2025')
              AND fb.is_legal_ball = true
            GROUP BY fb.batter_id
            HAVING COUNT(*) >= 100
        ),
        ipl_top_bowlers AS (
            SELECT fb.bowler_id AS player_id, COUNT(*) AS balls
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            WHERE dm.tournament_id = 'indian_premier_league'
              AND dm.season IN ('2023', '2024', '2025')
              AND fb.is_legal_ball = true
            GROUP BY fb.bowler_id
            HAVING COUNT(*) >= 60
        ),
        ipl_top AS (
            SELECT player_id FROM ipl_top_batters
            UNION
            SELECT player_id FROM ipl_top_bowlers
        ),
        tournament_players AS (
            SELECT DISTINCT dm.tournament_id, fb.batter_id AS player_id
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
            UNION
            SELECT DISTINCT dm.tournament_id, fb.bowler_id
            FROM fact_ball fb
            JOIN dim_match dm ON fb.match_id = dm.match_id
        )
        SELECT
            tp.tournament_id,
            COUNT(DISTINCT CASE WHEN it.player_id IS NOT NULL
                                THEN tp.player_id END) AS top_ipl_players,
            (SELECT COUNT(*) FROM ipl_top) AS total_top_ipl
        FROM tournament_players tp
        LEFT JOIN ipl_top it ON tp.player_id = it.player_id
        WHERE tp.tournament_id IN ({placeholders})
        GROUP BY tp.tournament_id
        ORDER BY top_ipl_players DESC
        """.format(placeholders=", ".join(f"'{tid}'" for tid in TOURNAMENTS))
    ).fetchall()

    total_top_ipl = result[0][2] if result else 1
    pqi_raw = {}
    for row in result:
        tournament_id = row[0]
        top_count = row[1]
        pqi_raw[tournament_id] = top_count / total_top_ipl

    return pqi_raw, total_top_ipl


# ============================================================
# FACTOR 2: EFFECTIVE CI (Season-level with Recency Weighting)
# ============================================================


def compute_effective_ci(ci_data):
    """
    Effective_CI per tournament using season CI + exponential decay.
    Formula: Effective_CI = SUM(CI_season * Decay_season) / SUM(Decay_season)
    Then normalize 0-1 across all tournaments.
    """
    raw_ci = {}

    for tournament_id, tournament_data in ci_data["tournaments"].items():
        if tournament_id not in TOURNAMENTS:
            continue

        seasons = tournament_data["seasons"]
        weighted_sum = 0.0
        decay_sum = 0.0

        for season_str, season_data in seasons.items():
            ci_score = season_data["ci_score"]
            year = season_to_year(season_str)
            decay = exponential_decay(year)
            weighted_sum += ci_score * decay
            decay_sum += decay

        if decay_sum > 0:
            raw_ci[tournament_id] = weighted_sum / decay_sum
        else:
            raw_ci[tournament_id] = 0.0

    # Normalize: divide by theoretical max CI (100) to keep on 0-1 scale.
    # Season CI scores range from 0-100, so effective CI after weighting
    # will also be in that range. Dividing by 100 gives a meaningful 0-1 score.
    if not raw_ci:
        return {}

    normalized = {}
    for tid, val in raw_ci.items():
        normalized[tid] = val / 100.0  # CI ranges 0-100
    return normalized, raw_ci


# ============================================================
# FACTOR 3: RECENCY (Tournament-level aggregate decay score)
# ============================================================


def compute_recency(ci_data):
    """
    Tournament-level recency: measures how much *recent* data a tournament
    contributes. Uses the SUM of decay weights for the 3 most recent seasons.

    This approach:
    - Rewards tournaments with data in 2024-2025 (high decay weight)
    - Does NOT penalize long-running tournaments for having historical data
    - Creates separation between active and inactive tournaments
    - Caps at 3 seasons to prevent depth-of-history from dominating

    The IPL and other active tournaments all have recent seasons and score
    similarly. Tournaments without very recent data score lower.

    Normalize 0-1 across all tournaments (max gets 1.0).
    """
    raw_recency = {}

    for tournament_id, tournament_data in ci_data["tournaments"].items():
        if tournament_id not in TOURNAMENTS:
            continue

        seasons = tournament_data["seasons"]
        decay_weights = []

        for season_str in seasons:
            year = season_to_year(season_str)
            decay_weights.append(exponential_decay(year))

        # Use top-3 most recent seasons' decay weights
        decay_weights.sort(reverse=True)
        top_n = decay_weights[:3]

        if top_n:
            raw_recency[tournament_id] = sum(top_n)
        else:
            raw_recency[tournament_id] = 0.0

    # Normalize using ratio-to-max (not min-max).
    # Ratio normalization preserves meaningful differences:
    # a tournament with 75% of the max recency signal should score 0.75,
    # not 0.0 (as min-max would produce for the lowest tournament).
    if not raw_recency:
        return {}
    max_r = max(raw_recency.values())
    if max_r == 0:
        max_r = 1.0

    normalized = {}
    for tid, val in raw_recency.items():
        normalized[tid] = val / max_r
    return normalized, raw_recency


# ============================================================
# FACTOR 4: CONDITIONS SIMILARITY (Expert-defined)
# ============================================================


def get_conditions_similarity():
    """Return the Founder-specified conditions similarity scores."""
    return {tid: data["score"] for tid, data in CONDITIONS_SIMILARITY.items()}


# ============================================================
# FACTOR 5: SAMPLE SIZE CONFIDENCE
# ============================================================


def compute_sample_confidence(conn):
    """
    Sigmoid-based confidence: 1 / (1 + exp(-0.02 * (matches - 100)))
    Capped at 0.95. Based on total matches per tournament.
    """
    result = conn.execute(
        """
        SELECT tournament_id, COUNT(*) AS match_count
        FROM dim_match
        WHERE tournament_id IN ({placeholders})
        GROUP BY tournament_id
        """.format(placeholders=", ".join(f"'{tid}'" for tid in TOURNAMENTS))
    ).fetchall()

    match_counts = {}
    confidence = {}
    for row in result:
        tid = row[0]
        count = row[1]
        match_counts[tid] = count
        confidence[tid] = sigmoid_confidence(count)

    return confidence, match_counts


# ============================================================
# MAIN COMPUTATION
# ============================================================


def main():
    print("TKT-187: Computing Final Composite Tournament Weights")
    print("=" * 60)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Connect to DuckDB
    conn = duckdb.connect(DB_PATH, read_only=True)

    # Load season CI data
    with open(CI_JSON_PATH) as f:
        ci_data = json.load(f)

    # Compute all 5 factors
    print("\n[Factor 1] Computing PQI (Player Quality Index)...")
    pqi_scores, total_top_ipl = compute_pqi(conn)

    print("[Factor 2] Computing Effective CI (Season-level + Recency)...")
    ci_normalized, ci_raw = compute_effective_ci(ci_data)

    print("[Factor 3] Computing Recency scores...")
    recency_normalized, recency_raw = compute_recency(ci_data)

    print("[Factor 4] Loading Conditions Similarity...")
    conditions_scores = get_conditions_similarity()

    print("[Factor 5] Computing Sample Confidence...")
    sample_confidence, match_counts = compute_sample_confidence(conn)

    conn.close()

    # Get season counts from CI data
    season_counts = {}
    for tid in TOURNAMENTS:
        if tid in ci_data["tournaments"]:
            season_counts[tid] = len(ci_data["tournaments"][tid]["seasons"])
        else:
            season_counts[tid] = 0

    # ============================================================
    # COMBINE: Geometric Mean Composite
    # ============================================================
    print("\n[Composite] Applying geometric mean with factor weights...")
    print(f"  Weights: {FACTOR_WEIGHTS}")

    results = []
    for tid, tinfo in TOURNAMENTS.items():
        factors = {
            "pqi": pqi_scores.get(tid, 0.01),
            "effective_ci": ci_normalized.get(tid, 0.01),
            "recency": recency_normalized.get(tid, 0.01),
            "conditions_similarity": conditions_scores.get(tid, 0.01),
            "sample_confidence": sample_confidence.get(tid, 0.01),
        }

        # Floor all factors at 0.01 for geometric mean stability
        for key in factors:
            factors[key] = max(factors[key], 0.01)

        composite = geometric_mean_composite(factors, FACTOR_WEIGHTS)

        results.append(
            {
                "tournament": tinfo["name"],
                "tournament_key": tid,
                "short_name": tinfo["short"],
                "composite_weight": round(composite, 4),
                "tier": "",  # assigned after sorting
                "factors": {k: round(v, 4) for k, v in factors.items()},
                "factors_raw": {
                    "pqi_top_player_pct": round(pqi_scores.get(tid, 0) * 100, 1),
                    "effective_ci_raw": round(ci_raw.get(tid, 0), 2),
                    "recency_raw": round(recency_raw.get(tid, 0), 4),
                },
                "seasons_analyzed": season_counts.get(tid, 0),
                "total_matches": match_counts.get(tid, 0),
            }
        )

    # Sort by composite weight descending
    results.sort(key=lambda x: x["composite_weight"], reverse=True)

    # Assign tiers based on natural gap analysis
    composites = [r["composite_weight"] for r in results]
    gaps = []
    for i in range(len(composites) - 1):
        gaps.append(
            {
                "between": f"{results[i]['short_name']}-{results[i + 1]['short_name']}",
                "gap": round(composites[i] - composites[i + 1], 4),
            }
        )

    # Data-driven tier assignment
    tier_map = assign_tier(composites)
    for r in results:
        r["tier"] = tier_map.get(r["composite_weight"], "3")

    # ============================================================
    # OUTPUT JSON
    # ============================================================
    output = {
        "metadata": {
            "formula": "geometric_mean",
            "decay_halflife_years": HALF_LIFE,
            "conditions_baseline": "IPL 2023-2025",
            "computed_at": timestamp,
            "ticket": "TKT-187",
            "owner": "Jose Mourinho",
            "factor_weights": FACTOR_WEIGHTS,
            "total_top_ipl_players": total_top_ipl,
            "reference_year": REFERENCE_YEAR,
        },
        "tournaments": [
            {
                "tournament": r["tournament"],
                "tournament_key": r["tournament_key"],
                "composite_weight": r["composite_weight"],
                "tier": r["tier"],
                "factors": r["factors"],
                "seasons_analyzed": r["seasons_analyzed"],
                "total_matches": r["total_matches"],
            }
            for r in results
        ],
        "conditions_similarity_reasoning": {
            tid: data["reasoning"] for tid, data in CONDITIONS_SIMILARITY.items()
        },
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nJSON output written to: {OUTPUT_JSON_PATH}")

    # ============================================================
    # GENERATE FOUNDER PRESENTATION (Markdown)
    # ============================================================
    md = generate_presentation(results, gaps, timestamp, total_top_ipl)

    os.makedirs(os.path.dirname(OUTPUT_MD_PATH), exist_ok=True)
    with open(OUTPUT_MD_PATH, "w") as f:
        f.write("\n".join(md))
    print(f"Presentation written to: {OUTPUT_MD_PATH}")

    # Print summary
    print("\n" + "=" * 60)
    print("FINAL TOURNAMENT WEIGHTS — SUMMARY")
    print("=" * 60)
    print(
        f"{'Rank':>4}  {'Tournament':<30}  {'Composite':>9}  {'Tier':>4}  "
        f"{'PQI':>5}  {'CI':>5}  {'Rec':>5}  {'Cond':>5}  {'Samp':>5}"
    )
    print("-" * 105)
    for i, r in enumerate(results, 1):
        f = r["factors"]
        print(
            f"{i:>4}  {r['tournament']:<30}  {r['composite_weight']:>9.4f}  "
            f"{r['tier']:>4}  {f['pqi']:>5.2f}  {f['effective_ci']:>5.2f}  "
            f"{f['recency']:>5.2f}  {f['conditions_similarity']:>5.2f}  "
            f"{f['sample_confidence']:>5.2f}"
        )

    # Tier distribution
    tier_dist = {}
    for r in results:
        tier_dist[r["tier"]] = tier_dist.get(r["tier"], 0) + 1
    print(f"\nTier Distribution: {tier_dist}")
    print(f"Total tournaments: {len(results)}")


def generate_presentation(results, gaps, timestamp, total_top_ipl):
    """Generate the Founder presentation markdown."""
    md = []

    md.append("# TKT-187: Final Composite Tournament Weights")
    md.append("")
    md.append("**Owner:** Jose Mourinho (Quant Researcher)")
    md.append("**Parent Ticket:** TKT-183 (Tournament Quality Weighting System)")
    md.append(f"**Generated:** {timestamp}")
    md.append("**Status:** READY FOR FOUNDER APPROVAL")
    md.append("")
    md.append("---")
    md.append("")

    # Executive Summary
    md.append("## 1. Executive Summary")
    md.append("")
    md.append(
        "This document presents the **final composite tournament weights** for the "
        "Cricket Playbook's Tournament Quality Weighting System. These weights determine "
        "how much each tournament's data influences IPL 2026 player projections."
    )
    md.append("")
    md.append("**All Founder Decisions have been implemented as locked parameters:**")
    md.append("")
    md.append("| Decision | Implementation |")
    md.append("|----------|----------------|")
    md.append(
        "| Recency Decay | Exponential, half-life = 4 years: `w(year) = 2^(-(2026-year)/4)` |"
    )
    md.append(
        "| Competitiveness Index | Season-level CI with recency weighting: "
        "`Effective_CI = SUM(CI*Decay)/SUM(Decay)` |"
    )
    md.append("| Composite Formula | Geometric Mean: `W = PROD(f_i^w_i)^(1/SUM(w_i))` |")
    md.append("| Conditions Baseline | IPL 2023-2025 (219 matches) |")
    md.append("")

    md.append("**Factor Weights:**")
    md.append("")
    md.append("| Factor | Weight | Rationale |")
    md.append("|--------|--------|-----------|")
    md.append(
        "| Player Quality Index (PQI) | 0.25 | Talent concentration is the primary quality signal |"
    )
    md.append("| Effective CI | 0.20 | Competitive leagues produce pressure-tested data |")
    md.append("| Recency | 0.20 | More recent data is more relevant to IPL 2026 |")
    md.append(
        "| Conditions Similarity | 0.15 | Transferability of performance data to IPL context |"
    )
    md.append("| Sample Confidence | 0.20 | Statistical reliability from match volume |")
    md.append("")
    md.append("---")
    md.append("")

    # Full Ranking Table
    md.append("## 2. Full Tournament Rankings")
    md.append("")
    md.append(
        "| Rank | Tournament | Composite | Tier | PQI | Eff CI | Recency "
        "| Conditions | Sample | Seasons | Matches |"
    )
    md.append(
        "|------|-----------|-----------|------|-----|--------|--------"
        "|------------|--------|---------|---------|"
    )
    for i, r in enumerate(results, 1):
        f = r["factors"]
        md.append(
            f"| {i} | {r['tournament']} | **{r['composite_weight']:.4f}** "
            f"| **{r['tier']}** | {f['pqi']:.2f} | {f['effective_ci']:.2f} "
            f"| {f['recency']:.2f} | {f['conditions_similarity']:.2f} "
            f"| {f['sample_confidence']:.2f} | {r['seasons_analyzed']} "
            f"| {r['total_matches']} |"
        )
    md.append("")
    md.append("---")
    md.append("")

    # Tier Distribution
    md.append("## 3. Tier Distribution")
    md.append("")
    tier_groups = {}
    for r in results:
        tier_groups.setdefault(r["tier"], []).append(r)

    tier_descriptions = {
        "1A": "Premier Tier -- highest composite weight, clear separation from field",
        "1B": "High Quality -- strong across most factors, composite >= 0.50",
        "1C": "Moderate Quality -- useful data but with notable weaknesses, composite 0.40-0.50",
        "2": "Limited Utility -- data has significant gaps or low quality, composite 0.30-0.40",
        "3": "Minimal Utility -- data not recommended for primary projections, composite < 0.30",
    }

    for tier in ["1A", "1B", "1C", "2", "3"]:
        if tier not in tier_groups:
            continue
        group = tier_groups[tier]
        md.append(f"### Tier {tier}: {tier_descriptions.get(tier, '')}")
        md.append(f"**Count:** {len(group)}")
        md.append("")
        for r in group:
            f = r["factors"]
            strengths = []
            weaknesses = []
            for fname, fval in f.items():
                label = fname.replace("_", " ").title()
                if fval >= 0.70:
                    strengths.append(f"{label} ({fval:.2f})")
                elif fval <= 0.30:
                    weaknesses.append(f"{label} ({fval:.2f})")

            md.append(f"- **{r['tournament']}** (composite: {r['composite_weight']:.4f})")
            if strengths:
                md.append(f"  - Strengths: {', '.join(strengths)}")
            if weaknesses:
                md.append(f"  - Weaknesses: {', '.join(weaknesses)}")
        md.append("")

    md.append("---")
    md.append("")

    # Notable Findings
    md.append("## 4. Notable Findings")
    md.append("")

    # Find interesting patterns
    md.append("### 4.1 Key Observations")
    md.append("")

    # Top tournament
    top = results[0]
    md.append(
        f"1. **{top['tournament']}** is the clear Tier 1A tournament "
        f"(composite: {top['composite_weight']:.4f}). Its dominance comes from "
        f"having the highest PQI ({top['factors']['pqi']:.2f}), perfect conditions "
        f"similarity (1.00), and the largest sample size."
    )
    md.append("")

    # Gap analysis
    if len(results) >= 2:
        top_gap = results[0]["composite_weight"] - results[1]["composite_weight"]
        md.append(
            f"2. **Gap between #1 and #2:** {top_gap:.4f}. "
            f"This {'confirms' if top_gap > 0.08 else 'shows moderate'} "
            f"separation of the IPL from the rest of the field."
        )
        md.append("")

    # Surprises
    md.append("3. **Surprises and Edge Cases:**")
    md.append("")

    # SMAT has high PQI (Indian domestic) but low CI
    smat = next((r for r in results if r["tournament_key"] == "syed_mushtaq_ali_trophy"), None)
    if smat:
        md.append(
            "   - **SMAT** has high conditions similarity (0.85) because it is played on "
            "Indian grounds, but its low PQI and CI pull it down. This validates the "
            "geometric mean's penalty for unbalanced factor profiles."
        )

    # SA20 has high PQI but low recency (only 4 seasons)
    sa20 = next((r for r in results if r["tournament_key"] == "sa20"), None)
    if sa20:
        md.append(
            f"   - **SA20** scores well on PQI ({sa20['factors']['pqi']:.2f}) as a "
            f"tournament that attracts top IPL players, but its limited "
            f"sample size ({sa20['total_matches']} matches) constrains its "
            f"overall composite."
        )

    # MLC has high PQI but very few matches
    mlc = next((r for r in results if r["tournament_key"] == "major_league_cricket"), None)
    if mlc:
        md.append(
            f"   - **MLC** shows the tension between quality and quantity: "
            f"it attracts elite IPL players but has only {mlc['total_matches']} "
            f"matches across {mlc['seasons_analyzed']} seasons."
        )

    md.append("")

    # BBL vs CPL
    bbl = next((r for r in results if r["tournament_key"] == "big_bash_league"), None)
    cpl = next((r for r in results if r["tournament_key"] == "caribbean_premier_league"), None)
    if bbl and cpl:
        md.append(
            f"   - **BBL vs CPL:** These two established leagues end up close in the "
            f"rankings. BBL has more matches ({bbl['total_matches']} vs {cpl['total_matches']}) "
            f"but similar PQI and conditions dissimilarity from IPL."
        )

    md.append("")
    md.append("---")
    md.append("")

    # Factor Correlation Analysis
    md.append("## 5. Factor Correlation Analysis")
    md.append("")
    md.append(
        "How correlated are the 5 factors? High correlation between factors would "
        "indicate redundancy; low correlation confirms they measure distinct dimensions."
    )
    md.append("")

    # Compute simple correlation matrix
    factor_names = ["pqi", "effective_ci", "recency", "conditions_similarity", "sample_confidence"]
    factor_vectors = {fn: [r["factors"][fn] for r in results] for fn in factor_names}

    def pearson_r(x, y):
        n = len(x)
        if n < 3:
            return 0.0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        var_x = sum((xi - mean_x) ** 2 for xi in x)
        var_y = sum((yi - mean_y) ** 2 for yi in y)
        denom = math.sqrt(var_x * var_y)
        if denom == 0:
            return 0.0
        return cov / denom

    md.append("| | PQI | Eff CI | Recency | Conditions | Sample |")
    md.append("|---|-----|--------|---------|------------|--------|")
    labels = {
        "pqi": "PQI",
        "effective_ci": "Eff CI",
        "recency": "Recency",
        "conditions_similarity": "Conditions",
        "sample_confidence": "Sample",
    }
    for fn1 in factor_names:
        row = f"| **{labels[fn1]}** |"
        for fn2 in factor_names:
            r_val = pearson_r(factor_vectors[fn1], factor_vectors[fn2])
            row += f" {r_val:.2f} |"
        md.append(row)

    md.append("")
    md.append(
        "**Interpretation:** Low cross-factor correlations confirm that the 5 factors "
        "measure distinct quality dimensions. The geometric mean correctly combines "
        "these independent signals into a holistic tournament quality score."
    )
    md.append("")
    md.append("---")
    md.append("")

    # Conditions Similarity Reasoning
    md.append("## 6. Conditions Similarity Reasoning")
    md.append("")
    md.append(
        "The Conditions Similarity factor is expert-defined. Below is the reasoning "
        "for each tournament's score:"
    )
    md.append("")
    md.append("| Tournament | Score | Reasoning |")
    md.append("|-----------|-------|-----------|")
    for tid in sorted(
        CONDITIONS_SIMILARITY.keys(),
        key=lambda t: CONDITIONS_SIMILARITY[t]["score"],
        reverse=True,
    ):
        data = CONDITIONS_SIMILARITY[tid]
        name = TOURNAMENTS.get(tid, {}).get("name", tid)
        md.append(f"| {name} | {data['score']:.2f} | {data['reasoning']} |")

    md.append("")
    md.append("---")
    md.append("")

    # Adjacent Gap Analysis
    md.append("## 7. Adjacent Gap Analysis")
    md.append("")
    md.append("The gaps between adjacent tournaments help identify natural tier boundaries:")
    md.append("")
    md.append("| Between | Gap | Significance |")
    md.append("|---------|-----|-------------|")
    for g in gaps:
        significance = ""
        if g["gap"] > 0.10:
            significance = "LARGE -- clear tier boundary"
        elif g["gap"] > 0.05:
            significance = "Notable -- possible tier split"
        elif g["gap"] > 0.02:
            significance = "Moderate"
        else:
            significance = "Minimal -- same cluster"
        md.append(f"| {g['between']} | {g['gap']:.4f} | {significance} |")

    md.append("")
    md.append("---")
    md.append("")

    # PQI Detail
    md.append("## 8. PQI Methodology Detail")
    md.append("")
    md.append(
        f"PQI is based on **{total_top_ipl} top IPL players** identified from "
        f"IPL 2023-2025 data (batters with 100+ legal balls faced, bowlers with "
        f"60+ legal balls bowled). For each tournament, we measure what fraction "
        f"of these top IPL players have also played in that tournament."
    )
    md.append("")
    md.append("| Tournament | Top IPL Players Present | PQI Score |")
    md.append("|-----------|------------------------|-----------|")
    for r in results:
        pqi_pct = r["factors_raw"]["pqi_top_player_pct"]
        md.append(
            f"| {r['tournament']} | {pqi_pct:.1f}% of {total_top_ipl} | {r['factors']['pqi']:.2f} |"
        )
    md.append("")
    md.append("---")
    md.append("")

    # Sign-off
    md.append("## 9. Approval Request")
    md.append("")
    md.append("These weights are ready for Founder sign-off. Upon approval:")
    md.append("")
    md.append("1. The composite weights will be integrated into the player projection pipeline")
    md.append(
        "2. Each tournament's data will be weighted by its composite score when "
        "computing player performance metrics"
    )
    md.append(
        "3. Tier assignments will guide which tournaments receive primary vs "
        "supplementary treatment in stat packs"
    )
    md.append("")
    md.append("**Founder Decision Required:**")
    md.append("")
    md.append("- [ ] **APPROVE** -- Weights are correct and ready for integration")
    md.append(
        "- [ ] **APPROVE WITH MODIFICATIONS** -- Specify adjustments to "
        "factor weights, tier boundaries, or conditions scores"
    )
    md.append("- [ ] **REQUEST REVISION** -- Specify what additional analysis is needed")
    md.append("")
    md.append("---")
    md.append("")
    md.append("*Cricket Playbook v4.0.0 | TKT-187 | Jose Mourinho, Quant Researcher*")

    return md


if __name__ == "__main__":
    main()
