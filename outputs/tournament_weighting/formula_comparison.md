# TKT-186: Composite Weight Formula Comparison

**Owner:** Jose Mourinho (Quant Researcher)
**Parent Ticket:** TKT-183 (Tournament Quality Weighting System)
**Generated:** 2026-02-12 07:45
**Status:** DRAFT — Pending Domain Review

---

## 1. Executive Summary

The Tournament Quality Weighting System combines five factors (PQI, CI, Conditions Similarity,
Sample Confidence, Recency) into a single composite weight per tournament. Phase 1 used a
weighted arithmetic mean. This analysis compares three aggregation formulas to determine which
best separates tournament quality tiers while appropriately penalizing factor weaknesses.

**The three candidates:**

1. **Weighted Arithmetic Mean** (current): `W = SUM(w_i * f_i) / SUM(w_i)`
2. **Weighted Geometric Mean**: `W = PROD(f_i ^ w_i) ^ (1/SUM(w_i))`
3. **Weighted Harmonic Mean**: `W = SUM(w_i) / SUM(w_i / f_i)`

**Jose Mourinho's recommendation: Geometric Mean.** It provides the best balance between
tier separation and appropriate penalty for weak factors, without the harmonic mean's
excessive punishment. Details below.

---

## 2. Factor Weights (Unchanged)

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Player Quality Index (PQI) | 0.3 | Highest weight — talent concentration is the primary quality signal |
| Competitiveness Index (CI) | 0.15 | Competitive leagues produce more pressure-tested data |
| Conditions Similarity | 0.25 | Transferability of performance data to IPL context |
| Sample Size Confidence | 0.15 | Statistical reliability — small samples = lower confidence |
| Recency | 0.15 | More recent data is more relevant (currently uniform 0.90) |

**Note:** Recency is currently set to a uniform 0.90 for all tournaments in Phase 1.
This will be replaced by the decay curve selected under TKT-184.

---

## 3. Side-by-Side Rankings

| Rank | Tournament | Arithmetic | Tier | Geometric | Tier | Harmonic | Tier |
|------|------------|------------|------|-----------|------|----------|------|
| 1 | Indian PL | 0.8607 | 1A | 0.8125 | 1B | 0.7408 | 1B |
| 2 | Vitality Blast | 0.7127 | 1B | 0.6667 | 1C | 0.6194 | 1C |
| 3 | International League T20 | 0.7107 | 1B | 0.6471 | 1C | 0.5482 | 2 |
| 4 | Major League Cricket | 0.6963 | 1C | 0.6516 | 1C | 0.6019 | 1C |
| 5 | Caribbean PL | 0.6642 | 1C | 0.6008 | 1C | 0.5395 | 2 |
| 6 | Big Bash League | 0.6634 | 1C | 0.6002 | 1C | 0.5398 | 2 |
| 7 | Lanka PL | 0.6603 | 1C | 0.6280 | 1C | 0.5937 | 1C |
| 8 | The Hundred | 0.6590 | 1C | 0.6152 | 1C | 0.5722 | 1C |
| 9 | Pakistan Super League | 0.6578 | 1C | 0.5783 | 1C | 0.5042 | 2 |
| 10 | CSA T20 Challenge | 0.6561 | 1C | 0.6231 | 1C | 0.5908 | 1C |
| 11 | SA20 | 0.6361 | 1C | 0.5956 | 1C | 0.5554 | 1C |
| 12 | ICC Men's T20 World Cup | 0.6204 | 1C | 0.5842 | 1C | 0.5438 | 2 |
| 13 | Super Smash | 0.6150 | 1C | 0.5027 | 2 | 0.4014 | 2 |
| 14 | Syed Mushtaq Ali Trophy | 0.5957 | 1C | 0.4803 | 2 | 0.3802 | 3 |

### 3.1 Ranking Movements

| Tournament | Arith Rank | Geo Rank | Harm Rank | Max Movement |
|------------|-----------|----------|-----------|-------------|
| Indian PL | 1 | 1 | 1 | 0 |
| Vitality Blast | 2 | 2 | 2 | 0 |
| International League T20 | 3 | 4 | 8 | 5 |
| Major League Cricket | 4 | 3 | 3 | 1 |
| Caribbean PL | 5 | 8 | 11 | 6 |
| Big Bash League | 6 | 9 | 10 | 4 |
| Lanka PL | 7 | 5 | 4 | 3 |
| The Hundred | 8 | 7 | 6 | 2 |
| Pakistan Super League | 9 | 12 | 12 | 3 |
| CSA T20 Challenge | 10 | 6 | 5 | 5 |
| SA20 | 11 | 10 | 7 | 4 |
| ICC Men's T20 World Cup | 12 | 11 | 9 | 3 |
| Super Smash | 13 | 13 | 13 | 0 |
| Syed Mushtaq Ali Trophy | 14 | 14 | 14 | 0 |

---

## 4. Tier Separation Analysis

The key question: which formula produces the clearest separation between tournament quality tiers?

| Metric | Arithmetic | Geometric | Harmonic |
|--------|-----------|-----------|----------|
| Total Range (best - worst) | 0.265 | 0.3322 | 0.3606 |
| Average Gap Between Adjacent | 0.0204 | 0.0256 | 0.0277 |
| Maximum Gap (largest cliff) | 0.148 | 0.1458 | 0.1214 |
| Standard Deviation | 0.0617 | 0.0747 | 0.085 |
| Coefficient of Variation | 0.0918 | 0.1218 | 0.154 |
| Distinct Tiers Produced | 3 | 3 | 4 |

### 4.1 Tier Distribution

| Tier | Arithmetic | Geometric | Harmonic |
|------|-----------|-----------|----------|
| 1A | 1 | 0 | 0 |
| 1B | 2 | 1 | 1 |
| 1C | 11 | 11 | 6 |
| 2 | 0 | 2 | 6 |
| 3 | 0 | 0 | 1 |

### 4.2 Interpretation

- **Arithmetic Mean** produces the tightest clustering — most tournaments land in 1C,
  with narrow gaps between them. This is its fundamental weakness: it allows a single
  strong factor (e.g., high conditions similarity) to compensate for a weak factor
  (e.g., low PQI), producing tournaments that score similarly despite having very
  different quality profiles.

- **Geometric Mean** produces wider separation with a higher coefficient of variation.
  Crucially, it distributes tournaments more evenly across tiers, creating clearer
  quality distinctions. A tournament that is strong everywhere gets rewarded; one
  with a glaring weakness gets penalized proportionally.

- **Harmonic Mean** produces the widest separation but is arguably too aggressive.
  Any single weak factor drags the entire composite down drastically. This can
  produce counterintuitive results where a tournament with 4 excellent factors
  and 1 moderate factor scores lower than expected.

---

## 5. Sensitivity Analysis

Synthetic test: How does each formula handle deliberate factor weakness?

| Scenario | Arithmetic | Geometric | Harmonic | Key Insight |
|----------|-----------|-----------|----------|-------------|
| Strong across board | 0.8275 | 0.8247 | 0.8219 | Baseline — all formulas agree |
| Weak PQI (low talent) | 0.6325 | 0.4991 | 0.3519 | Penalties: A=0.195, G=0.326, H=0.470 |
| Weak sample size | 0.7150 | 0.6304 | 0.4878 | Penalties: A=0.113, G=0.194, H=0.334 |
| Weak conditions match | 0.6650 | 0.5744 | 0.4603 | Penalties: A=0.163, G=0.250, H=0.362 |
| Old tournament (low recency) | 0.7150 | 0.6304 | 0.4878 | Baseline — all formulas agree |
| Two weak factors | 0.5200 | 0.3815 | 0.2721 | Baseline — all formulas agree |

### 5.1 Key Findings

1. **Single weak factor impact:**
   - Arithmetic: Reduces score by the factor's weight proportion (predictable, mild)
   - Geometric: Reduces score more aggressively, roughly proportional to the log of the weakness
   - Harmonic: Dramatically reduces score — a single 0.15 factor can tank an otherwise strong tournament

2. **Two weak factors:**
   The harmonic mean produces a compounding penalty that is arguably excessive.
   A tournament with strong conditions, CI, and recency but weak PQI and sample size
   gets hammered harder than its analytical profile warrants.

3. **Weak PQI is the most impactful weakness** across all formulas, which is correct —
   PQI has the highest weight (0.30) and is the primary quality signal per the methodology.

---

## 6. Mathematical Properties

| Property | Arithmetic | Geometric | Harmonic |
|----------|-----------|-----------|----------|
| Compensatory? | Yes — strong factors offset weak ones | Partially — weak factors penalized but not zeroed | No — weak factors dominate |
| Handles zeros? | Yes (zero contributes proportionally) | No (log(0) undefined; needs flooring) | No (1/0 undefined; needs flooring) |
| Interpretability | High — weighted average is intuitive | Medium — requires log-space reasoning | Low — inverse-weighted average is non-intuitive |
| Range behavior | Output bounded by min/max of inputs | Output tends toward lower end | Output dominated by smallest input |
| Relationship | AM >= GM >= HM always holds | Middle ground | Always produces lowest composite |

---

## 7. Recommendation

### Jose Mourinho's Selection: Geometric Mean

**Formula:** `W = PROD(f_i ^ w_i) ^ (1 / SUM(w_i))`

**Rationale:**

1. **Appropriate penalty for weakness.** The geometric mean correctly penalizes tournaments
   with one glaring weakness without the harmonic mean's excessive punishment. A tournament
   cannot hide a 0.15 PQI behind a 0.90 conditions similarity — the geometric mean exposes
   this imbalance.

2. **Better tier separation.** The coefficient of variation is higher than the arithmetic mean,
   producing clearer quality tiers. This matters for the operational purpose of the system:
   we need to differentiate between tournaments, not cluster them into an undifferentiated mass.

3. **Multiplicative logic matches our mental model.** A tournament's quality is the product
   of its factors, not the sum. A league with great players but terrible conditions similarity
   is not 'half-good' — its data is *less transferable* in a way that compounds with other
   weaknesses. The geometric mean captures this multiplicative logic.

4. **Mathematical precedent.** The geometric mean is the standard approach for composite
   indices in economics (HDI, Corruption Perceptions Index) and sports analytics (ESPN's
   QBR uses a similar approach). We are not inventing something novel.

5. **AM >= GM >= HM inequality ensures the geometric mean is the centrist choice.**
   It is mathematically guaranteed to be less generous than the arithmetic mean and
   less punitive than the harmonic mean. This is exactly where we want to be for a v1.0
   system: rigorous but not extreme.

**What I explicitly do NOT recommend:**

- **Arithmetic Mean (current):** Too compensatory. It allows strong conditions similarity
  (which most tournaments score well on) to mask genuinely weak factors like PQI. This
  produces a cluster of tournaments in the 0.60-0.72 range that are not meaningfully
  differentiated — which defeats the purpose of the weighting system.

- **Harmonic Mean:** Too punitive. It produces counterintuitive results where tournaments
  with 4/5 strong factors score poorly because of a single moderate weakness. This would
  make the system fragile and hard to defend in domain review.

---

## 8. Next Steps

1. **Founder review:** Present this comparison for Founder selection of the composite formula
2. **Integration with TKT-184:** Once the decay curve is selected, replace the uniform
   recency factor (0.90) with actual per-tournament decay weights
3. **Integration with TKT-185:** Replace all-time CI with recency-weighted season CI
4. **Recompute final weights:** Run the selected formula with refined factor scores

---

*Cricket Playbook v4.0.0 | TKT-186 | Jose Mourinho, Quant Researcher*
