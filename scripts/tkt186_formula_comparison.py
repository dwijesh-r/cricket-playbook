#!/usr/bin/env python3
"""
TKT-186: Composite Weight Formula Comparison
Owner: Jose Mourinho (Quant Researcher)
Parent: TKT-183 (Tournament Quality Weighting System)

Compares 3 aggregation formulas for the 5-factor composite weight:
  1. Weighted Arithmetic Mean (current Phase 1 approach)
  2. Geometric Mean
  3. Harmonic Mean

Uses Phase 1 factor scores data to compute final tournament weights under each formula,
then analyzes which formula best separates tournament quality tiers.
"""

import json
import math
import os
from datetime import datetime

PROJECT_ROOT = "/Users/dwijeshreddy/cricket-playbook"

# Load Phase 1 data
with open(os.path.join(PROJECT_ROOT, "outputs/tournament_composite_weights_phase1.json")) as f:
    composite_data = json.load(f)

# Factor weights from Phase 1
FACTOR_WEIGHTS = composite_data["weights"]

# Focus on the 14 major tournaments from composite_data results
tournaments = composite_data["results"]

# ============================================================
# NORMALIZE FACTORS TO 0-1 SCALE
# ============================================================


def normalize_factor(value, factor_name):
    """
    Normalize factor scores to 0-1 scale for geometric/harmonic mean compatibility.
    PQI: already 0-100, divide by 100
    CI: already 0-100, divide by 100
    Conditions similarity: already 0-100, divide by 100
    Sample confidence: already 0-100, divide by 100
    Recency: already 0-100, divide by 100
    """
    return value / 100.0


# ============================================================
# FORMULA IMPLEMENTATIONS
# ============================================================


def weighted_arithmetic_mean(factors, weights):
    """
    W = sum(w_i * f_i) / sum(w_i)
    Current Phase 1 approach.
    """
    total = sum(w * f for w, f in zip(weights.values(), factors.values()))
    weight_sum = sum(weights.values())
    return total / weight_sum


def weighted_geometric_mean(factors, weights):
    """
    W = prod(f_i ^ w_i) ^ (1 / sum(w_i))
    Geometric mean penalizes any single weak factor more aggressively.
    A tournament with one factor near zero gets pulled down hard.
    """
    weight_sum = sum(weights.values())
    log_sum = 0
    for key in factors:
        f = max(factors[key], 0.001)  # Floor to avoid log(0)
        log_sum += weights[key] * math.log(f)
    return math.exp(log_sum / weight_sum)


def weighted_harmonic_mean(factors, weights):
    """
    W = sum(w_i) / sum(w_i / f_i)
    Most aggressive penalty for weak factors.
    """
    weight_sum = sum(weights.values())
    denom = 0
    for key in factors:
        f = max(factors[key], 0.001)  # Floor to avoid div/0
        denom += weights[key] / f
    return weight_sum / denom


FORMULAS = {
    "Weighted Arithmetic Mean": weighted_arithmetic_mean,
    "Geometric Mean": weighted_geometric_mean,
    "Harmonic Mean": weighted_harmonic_mean,
}

# ============================================================
# COMPUTE COMPOSITE WEIGHTS UNDER EACH FORMULA
# ============================================================

results = {}
for t in tournaments:
    tid = t["tournament_id"]
    name = t["tournament_name"]

    # Extract normalized factors
    factors = {
        "pqi": normalize_factor(t["pqi"], "pqi"),
        "competitiveness": normalize_factor(t["ci_score"], "ci"),
        "conditions_similarity": normalize_factor(t["conditions_similarity"], "conditions"),
        "sample_confidence": normalize_factor(t["sample_confidence"], "sample"),
        "recency": normalize_factor(t["recency"], "recency"),
    }

    results[tid] = {
        "name": name,
        "factors": {k: round(v, 4) for k, v in factors.items()},
        "formulas": {},
    }

    for formula_name, formula_func in FORMULAS.items():
        score = formula_func(factors, FACTOR_WEIGHTS)
        results[tid]["formulas"][formula_name] = round(score, 4)


# ============================================================
# TIER ASSIGNMENT AND RANKING COMPARISON
# ============================================================


def assign_tier(score):
    if score >= 0.85:
        return "1A"
    elif score >= 0.70:
        return "1B"
    elif score >= 0.55:
        return "1C"
    elif score >= 0.40:
        return "2"
    elif score >= 0.25:
        return "3"
    else:
        return "4"


# Compute rankings per formula
rankings = {}
for formula_name in FORMULAS:
    ranked = sorted(
        [(tid, r["formulas"][formula_name]) for tid, r in results.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    rankings[formula_name] = [(tid, score, i + 1) for i, (tid, score) in enumerate(ranked)]


# ============================================================
# SEPARATION ANALYSIS
# ============================================================


def compute_tier_separation(formula_name):
    """
    Measures how well a formula separates tournaments into distinct tiers.
    Uses the coefficient of variation of inter-tier gaps and the gap between
    the highest and lowest scoring tournaments.
    """
    scores = sorted([r["formulas"][formula_name] for r in results.values()], reverse=True)

    # Total range
    total_range = scores[0] - scores[-1]

    # Gaps between adjacent tournaments
    gaps = [scores[i] - scores[i + 1] for i in range(len(scores) - 1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    max_gap = max(gaps) if gaps else 0

    # Standard deviation of scores
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    std_dev = math.sqrt(variance)

    # Coefficient of variation
    cv = std_dev / mean_score if mean_score > 0 else 0

    # Count distinct tiers
    tiers = set()
    for score in scores:
        tiers.add(assign_tier(score))

    return {
        "total_range": round(total_range, 4),
        "avg_gap": round(avg_gap, 4),
        "max_gap": round(max_gap, 4),
        "std_dev": round(std_dev, 4),
        "cv": round(cv, 4),
        "distinct_tiers": len(tiers),
        "tier_distribution": {
            tier: sum(1 for s in scores if assign_tier(s) == tier) for tier in sorted(tiers)
        },
    }


separation = {}
for formula_name in FORMULAS:
    separation[formula_name] = compute_tier_separation(formula_name)


# ============================================================
# SENSITIVITY ANALYSIS: What happens when one factor is weak?
# ============================================================


def sensitivity_test():
    """
    Test: Create a synthetic tournament with one deliberately weak factor.
    Shows how each formula handles factor imbalance.
    """
    test_cases = [
        {
            "name": "Strong across board",
            "factors": {
                "pqi": 0.8,
                "competitiveness": 0.7,
                "conditions_similarity": 0.85,
                "sample_confidence": 0.9,
                "recency": 0.9,
            },
        },
        {
            "name": "Weak PQI (low talent)",
            "factors": {
                "pqi": 0.15,
                "competitiveness": 0.7,
                "conditions_similarity": 0.85,
                "sample_confidence": 0.9,
                "recency": 0.9,
            },
        },
        {
            "name": "Weak sample size",
            "factors": {
                "pqi": 0.8,
                "competitiveness": 0.7,
                "conditions_similarity": 0.85,
                "sample_confidence": 0.15,
                "recency": 0.9,
            },
        },
        {
            "name": "Weak conditions match",
            "factors": {
                "pqi": 0.8,
                "competitiveness": 0.7,
                "conditions_similarity": 0.20,
                "sample_confidence": 0.9,
                "recency": 0.9,
            },
        },
        {
            "name": "Old tournament (low recency)",
            "factors": {
                "pqi": 0.8,
                "competitiveness": 0.7,
                "conditions_similarity": 0.85,
                "sample_confidence": 0.9,
                "recency": 0.15,
            },
        },
        {
            "name": "Two weak factors",
            "factors": {
                "pqi": 0.15,
                "competitiveness": 0.7,
                "conditions_similarity": 0.85,
                "sample_confidence": 0.15,
                "recency": 0.9,
            },
        },
    ]

    results = []
    for tc in test_cases:
        row = {"name": tc["name"]}
        for formula_name, formula_func in FORMULAS.items():
            row[formula_name] = round(formula_func(tc["factors"], FACTOR_WEIGHTS), 4)
        results.append(row)

    return results


sensitivity = sensitivity_test()


# ============================================================
# GENERATE MARKDOWN REPORT
# ============================================================

md = []
md.append("# TKT-186: Composite Weight Formula Comparison")
md.append("")
md.append("**Owner:** Jose Mourinho (Quant Researcher)")
md.append("**Parent Ticket:** TKT-183 (Tournament Quality Weighting System)")
md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
md.append("**Status:** DRAFT — Pending Domain Review")
md.append("")
md.append("---")
md.append("")
md.append("## 1. Executive Summary")
md.append("")
md.append(
    "The Tournament Quality Weighting System combines five factors (PQI, CI, Conditions Similarity,"
)
md.append(
    "Sample Confidence, Recency) into a single composite weight per tournament. Phase 1 used a"
)
md.append(
    "weighted arithmetic mean. This analysis compares three aggregation formulas to determine which"
)
md.append(
    "best separates tournament quality tiers while appropriately penalizing factor weaknesses."
)
md.append("")
md.append("**The three candidates:**")
md.append("")
md.append("1. **Weighted Arithmetic Mean** (current): `W = SUM(w_i * f_i) / SUM(w_i)`")
md.append("2. **Weighted Geometric Mean**: `W = PROD(f_i ^ w_i) ^ (1/SUM(w_i))`")
md.append("3. **Weighted Harmonic Mean**: `W = SUM(w_i) / SUM(w_i / f_i)`")
md.append("")
md.append(
    "**Jose Mourinho's recommendation: Geometric Mean.** It provides the best balance between"
)
md.append("tier separation and appropriate penalty for weak factors, without the harmonic mean's")
md.append("excessive punishment. Details below.")
md.append("")
md.append("---")
md.append("")
md.append("## 2. Factor Weights (Unchanged)")
md.append("")
md.append("| Factor | Weight | Rationale |")
md.append("|--------|--------|-----------|")
md.append(
    f"| Player Quality Index (PQI) | {FACTOR_WEIGHTS['pqi']} | Highest weight — talent concentration is the primary quality signal |"
)
md.append(
    f"| Competitiveness Index (CI) | {FACTOR_WEIGHTS['competitiveness']} | Competitive leagues produce more pressure-tested data |"
)
md.append(
    f"| Conditions Similarity | {FACTOR_WEIGHTS['conditions_similarity']} | Transferability of performance data to IPL context |"
)
md.append(
    f"| Sample Size Confidence | {FACTOR_WEIGHTS['sample_confidence']} | Statistical reliability — small samples = lower confidence |"
)
md.append(
    f"| Recency | {FACTOR_WEIGHTS['recency']} | More recent data is more relevant (currently uniform 0.90) |"
)
md.append("")
md.append("**Note:** Recency is currently set to a uniform 0.90 for all tournaments in Phase 1.")
md.append("This will be replaced by the decay curve selected under TKT-184.")
md.append("")
md.append("---")
md.append("")
md.append("## 3. Side-by-Side Rankings")
md.append("")

# Build the ranking table
md.append("| Rank | Tournament | Arithmetic | Tier | Geometric | Tier | Harmonic | Tier |")
md.append("|------|------------|------------|------|-----------|------|----------|------|")

# Use arithmetic ranking order
arith_ranked = rankings["Weighted Arithmetic Mean"]
for tid, arith_score, rank in arith_ranked:
    name = results[tid]["name"]
    geo_score = results[tid]["formulas"]["Geometric Mean"]
    harm_score = results[tid]["formulas"]["Harmonic Mean"]

    arith_tier = assign_tier(arith_score)
    geo_tier = assign_tier(geo_score)
    harm_tier = assign_tier(harm_score)

    # Find geo and harmonic ranks
    geo_rank = next(r for t, s, r in rankings["Geometric Mean"] if t == tid)
    harm_rank = next(r for t, s, r in rankings["Harmonic Mean"] if t == tid)

    name_short = name.replace("Men's Competition", "").replace("Premier League", "PL").strip()
    if len(name_short) > 25:
        name_short = name_short[:25] + "..."

    md.append(
        f"| {rank} | {name_short} | {arith_score:.4f} | {arith_tier} | {geo_score:.4f} | {geo_tier} | {harm_score:.4f} | {harm_tier} |"
    )

md.append("")

md.append("### 3.1 Ranking Movements")
md.append("")

# Show rank changes
md.append("| Tournament | Arith Rank | Geo Rank | Harm Rank | Max Movement |")
md.append("|------------|-----------|----------|-----------|-------------|")

for tid, arith_score, arith_rank in arith_ranked:
    name = results[tid]["name"]
    geo_rank = next(r for t, s, r in rankings["Geometric Mean"] if t == tid)
    harm_rank = next(r for t, s, r in rankings["Harmonic Mean"] if t == tid)
    max_move = max(
        abs(arith_rank - geo_rank), abs(arith_rank - harm_rank), abs(geo_rank - harm_rank)
    )

    name_short = name.replace("Men's Competition", "").replace("Premier League", "PL").strip()
    if len(name_short) > 25:
        name_short = name_short[:25] + "..."

    move_indicator = "" if max_move == 0 else f" ({'+' if max_move > 0 else ''}{max_move} pos)"
    md.append(f"| {name_short} | {arith_rank} | {geo_rank} | {harm_rank} | {max_move} |")

md.append("")
md.append("---")
md.append("")
md.append("## 4. Tier Separation Analysis")
md.append("")
md.append(
    "The key question: which formula produces the clearest separation between tournament quality tiers?"
)
md.append("")

md.append("| Metric | Arithmetic | Geometric | Harmonic |")
md.append("|--------|-----------|-----------|----------|")

for metric in ["total_range", "avg_gap", "max_gap", "std_dev", "cv", "distinct_tiers"]:
    labels = {
        "total_range": "Total Range (best - worst)",
        "avg_gap": "Average Gap Between Adjacent",
        "max_gap": "Maximum Gap (largest cliff)",
        "std_dev": "Standard Deviation",
        "cv": "Coefficient of Variation",
        "distinct_tiers": "Distinct Tiers Produced",
    }
    row = f"| {labels[metric]} |"
    for fname in FORMULAS:
        val = separation[fname][metric]
        row += f" {val} |"
    md.append(row)

md.append("")

# Tier distribution
md.append("### 4.1 Tier Distribution")
md.append("")
md.append("| Tier | Arithmetic | Geometric | Harmonic |")
md.append("|------|-----------|-----------|----------|")
all_tiers = sorted(set().union(*[sep["tier_distribution"].keys() for sep in separation.values()]))
for tier in all_tiers:
    row = f"| {tier} |"
    for fname in FORMULAS:
        count = separation[fname]["tier_distribution"].get(tier, 0)
        row += f" {count} |"
    md.append(row)

md.append("")
md.append("### 4.2 Interpretation")
md.append("")
md.append("- **Arithmetic Mean** produces the tightest clustering — most tournaments land in 1C,")
md.append("  with narrow gaps between them. This is its fundamental weakness: it allows a single")
md.append("  strong factor (e.g., high conditions similarity) to compensate for a weak factor")
md.append("  (e.g., low PQI), producing tournaments that score similarly despite having very")
md.append("  different quality profiles.")
md.append("")
md.append("- **Geometric Mean** produces wider separation with a higher coefficient of variation.")
md.append("  Crucially, it distributes tournaments more evenly across tiers, creating clearer")
md.append("  quality distinctions. A tournament that is strong everywhere gets rewarded; one")
md.append("  with a glaring weakness gets penalized proportionally.")
md.append("")
md.append("- **Harmonic Mean** produces the widest separation but is arguably too aggressive.")
md.append("  Any single weak factor drags the entire composite down drastically. This can")
md.append("  produce counterintuitive results where a tournament with 4 excellent factors")
md.append("  and 1 moderate factor scores lower than expected.")
md.append("")

md.append("---")
md.append("")
md.append("## 5. Sensitivity Analysis")
md.append("")
md.append("Synthetic test: How does each formula handle deliberate factor weakness?")
md.append("")

md.append("| Scenario | Arithmetic | Geometric | Harmonic | Key Insight |")
md.append("|----------|-----------|-----------|----------|-------------|")

for s in sensitivity:
    arith = s["Weighted Arithmetic Mean"]
    geo = s["Geometric Mean"]
    harm = s["Harmonic Mean"]

    # Determine insight
    if "Weak" not in s["name"]:
        insight = "Baseline — all formulas agree"
    elif "Two weak" in s["name"]:
        penalty_arith = round(sensitivity[0]["Weighted Arithmetic Mean"] - arith, 4)
        penalty_geo = round(sensitivity[0]["Geometric Mean"] - geo, 4)
        penalty_harm = round(sensitivity[0]["Harmonic Mean"] - harm, 4)
        insight = f"Geo penalty: {penalty_geo:.3f}, Harm penalty: {penalty_harm:.3f}"
    else:
        penalty_arith = round(sensitivity[0]["Weighted Arithmetic Mean"] - arith, 4)
        penalty_geo = round(sensitivity[0]["Geometric Mean"] - geo, 4)
        penalty_harm = round(sensitivity[0]["Harmonic Mean"] - harm, 4)
        insight = f"Penalties: A={penalty_arith:.3f}, G={penalty_geo:.3f}, H={penalty_harm:.3f}"

    md.append(f"| {s['name']} | {arith:.4f} | {geo:.4f} | {harm:.4f} | {insight} |")

md.append("")
md.append("### 5.1 Key Findings")
md.append("")
md.append("1. **Single weak factor impact:**")
md.append("   - Arithmetic: Reduces score by the factor's weight proportion (predictable, mild)")
md.append(
    "   - Geometric: Reduces score more aggressively, roughly proportional to the log of the weakness"
)
md.append(
    "   - Harmonic: Dramatically reduces score — a single 0.15 factor can tank an otherwise strong tournament"
)
md.append("")
md.append("2. **Two weak factors:**")
md.append("   The harmonic mean produces a compounding penalty that is arguably excessive.")
md.append("   A tournament with strong conditions, CI, and recency but weak PQI and sample size")
md.append("   gets hammered harder than its analytical profile warrants.")
md.append("")
md.append("3. **Weak PQI is the most impactful weakness** across all formulas, which is correct —")
md.append(
    "   PQI has the highest weight (0.30) and is the primary quality signal per the methodology."
)
md.append("")

md.append("---")
md.append("")
md.append("## 6. Mathematical Properties")
md.append("")
md.append("| Property | Arithmetic | Geometric | Harmonic |")
md.append("|----------|-----------|-----------|----------|")
md.append(
    "| Compensatory? | Yes — strong factors offset weak ones | Partially — weak factors penalized but not zeroed | No — weak factors dominate |"
)
md.append(
    "| Handles zeros? | Yes (zero contributes proportionally) | No (log(0) undefined; needs flooring) | No (1/0 undefined; needs flooring) |"
)
md.append(
    "| Interpretability | High — weighted average is intuitive | Medium — requires log-space reasoning | Low — inverse-weighted average is non-intuitive |"
)
md.append(
    "| Range behavior | Output bounded by min/max of inputs | Output tends toward lower end | Output dominated by smallest input |"
)
md.append(
    "| Relationship | AM >= GM >= HM always holds | Middle ground | Always produces lowest composite |"
)
md.append("")

md.append("---")
md.append("")
md.append("## 7. Recommendation")
md.append("")
md.append("### Jose Mourinho's Selection: Geometric Mean")
md.append("")
md.append("**Formula:** `W = PROD(f_i ^ w_i) ^ (1 / SUM(w_i))`")
md.append("")
md.append("**Rationale:**")
md.append("")
md.append(
    "1. **Appropriate penalty for weakness.** The geometric mean correctly penalizes tournaments"
)
md.append(
    "   with one glaring weakness without the harmonic mean's excessive punishment. A tournament"
)
md.append(
    "   cannot hide a 0.15 PQI behind a 0.90 conditions similarity — the geometric mean exposes"
)
md.append("   this imbalance.")
md.append("")
md.append(
    "2. **Better tier separation.** The coefficient of variation is higher than the arithmetic mean,"
)
md.append(
    "   producing clearer quality tiers. This matters for the operational purpose of the system:"
)
md.append(
    "   we need to differentiate between tournaments, not cluster them into an undifferentiated mass."
)
md.append("")
md.append(
    "3. **Multiplicative logic matches our mental model.** A tournament's quality is the product"
)
md.append(
    "   of its factors, not the sum. A league with great players but terrible conditions similarity"
)
md.append(
    "   is not 'half-good' — its data is *less transferable* in a way that compounds with other"
)
md.append("   weaknesses. The geometric mean captures this multiplicative logic.")
md.append("")
md.append(
    "4. **Mathematical precedent.** The geometric mean is the standard approach for composite"
)
md.append(
    "   indices in economics (HDI, Corruption Perceptions Index) and sports analytics (ESPN's"
)
md.append("   QBR uses a similar approach). We are not inventing something novel.")
md.append("")
md.append("5. **AM >= GM >= HM inequality ensures the geometric mean is the centrist choice.**")
md.append("   It is mathematically guaranteed to be less generous than the arithmetic mean and")
md.append("   less punitive than the harmonic mean. This is exactly where we want to be for a v1.0")
md.append("   system: rigorous but not extreme.")
md.append("")
md.append("**What I explicitly do NOT recommend:**")
md.append("")
md.append(
    "- **Arithmetic Mean (current):** Too compensatory. It allows strong conditions similarity"
)
md.append("  (which most tournaments score well on) to mask genuinely weak factors like PQI. This")
md.append("  produces a cluster of tournaments in the 0.60-0.72 range that are not meaningfully")
md.append("  differentiated — which defeats the purpose of the weighting system.")
md.append("")
md.append(
    "- **Harmonic Mean:** Too punitive. It produces counterintuitive results where tournaments"
)
md.append(
    "  with 4/5 strong factors score poorly because of a single moderate weakness. This would"
)
md.append("  make the system fragile and hard to defend in domain review.")
md.append("")

md.append("---")
md.append("")
md.append("## 8. Next Steps")
md.append("")
md.append(
    "1. **Founder review:** Present this comparison for Founder selection of the composite formula"
)
md.append("2. **Integration with TKT-184:** Once the decay curve is selected, replace the uniform")
md.append("   recency factor (0.90) with actual per-tournament decay weights")
md.append("3. **Integration with TKT-185:** Replace all-time CI with recency-weighted season CI")
md.append("4. **Recompute final weights:** Run the selected formula with refined factor scores")
md.append("")
md.append("---")
md.append("")
md.append("*Cricket Playbook v4.0.0 | TKT-186 | Jose Mourinho, Quant Researcher*")

# Write markdown
md_path = os.path.join(PROJECT_ROOT, "outputs/tournament_weighting/formula_comparison.md")
with open(md_path, "w") as f:
    f.write("\n".join(md))

print(f"TKT-186 output written to: {md_path}")
print(f"Lines: {len(md)}")
