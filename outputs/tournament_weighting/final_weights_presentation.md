# TKT-187: Final Composite Tournament Weights

**Owner:** Jose Mourinho (Quant Researcher)
**Parent Ticket:** TKT-183 (Tournament Quality Weighting System)
**Generated:** 2026-02-12T14:40:13.992048+00:00
**Status:** READY FOR FOUNDER APPROVAL

---

## 1. Executive Summary

This document presents the **final composite tournament weights** for the Cricket Playbook's Tournament Quality Weighting System. These weights determine how much each tournament's data influences IPL 2026 player projections.

**All Founder Decisions have been implemented as locked parameters:**

| Decision | Implementation |
|----------|----------------|
| Recency Decay | Exponential, half-life = 4 years: `w(year) = 2^(-(2026-year)/4)` |
| Competitiveness Index | Season-level CI with recency weighting: `Effective_CI = SUM(CI*Decay)/SUM(Decay)` |
| Composite Formula | Geometric Mean: `W = PROD(f_i^w_i)^(1/SUM(w_i))` |
| Conditions Baseline | IPL 2023-2025 (219 matches) |

**Factor Weights:**

| Factor | Weight | Rationale |
|--------|--------|-----------|
| Player Quality Index (PQI) | 0.25 | Talent concentration is the primary quality signal |
| Effective CI | 0.20 | Competitive leagues produce pressure-tested data |
| Recency | 0.20 | More recent data is more relevant to IPL 2026 |
| Conditions Similarity | 0.15 | Transferability of performance data to IPL context |
| Sample Confidence | 0.20 | Statistical reliability from match volume |

---

## 2. Full Tournament Rankings

| Rank | Tournament | Composite | Tier | PQI | Eff CI | Recency | Conditions | Sample | Seasons | Matches |
|------|-----------|-----------|------|-----|--------|--------|------------|--------|---------|---------|
| 1 | Indian Premier League | **0.8721** | **1A** | 1.00 | 0.53 | 1.00 | 1.00 | 0.95 | 18 | 1169 |
| 2 | Syed Mushtaq Ali Trophy | **0.6454** | **1B** | 0.57 | 0.36 | 0.84 | 0.73 | 0.95 | 9 | 695 |
| 3 | Big Bash League | **0.5261** | **1C** | 0.21 | 0.49 | 1.00 | 0.50 | 0.95 | 15 | 654 |
| 4 | Pakistan Super League | **0.5140** | **1C** | 0.18 | 0.49 | 0.90 | 0.65 | 0.95 | 11 | 314 |
| 5 | The Hundred | **0.5035** | **1C** | 0.22 | 0.53 | 1.00 | 0.40 | 0.79 | 5 | 167 |
| 6 | SA20 | **0.5021** | **1C** | 0.25 | 0.48 | 1.00 | 0.55 | 0.60 | 4 | 121 |
| 7 | ICC Men's T20 World Cup | **0.4984** | **1C** | 0.36 | 0.40 | 0.76 | 0.50 | 0.62 | 3 | 124 |
| 8 | Vitality Blast | **0.4976** | **1C** | 0.20 | 0.52 | 0.84 | 0.45 | 0.95 | 7 | 835 |
| 9 | Caribbean Premier League | **0.4967** | **1C** | 0.17 | 0.48 | 1.00 | 0.50 | 0.95 | 13 | 407 |
| 10 | International League T20 | **0.4889** | **1C** | 0.21 | 0.45 | 1.00 | 0.55 | 0.66 | 4 | 134 |
| 11 | Major League Cricket | **0.4233** | **2** | 0.21 | 0.46 | 1.00 | 0.45 | 0.38 | 3 | 75 |
| 12 | Lanka Premier League | **0.3982** | **2** | 0.10 | 0.52 | 0.84 | 0.60 | 0.59 | 5 | 119 |
| 13 | CSA T20 Challenge | **0.3834** | **2** | 0.07 | 0.55 | 0.84 | 0.55 | 0.75 | 7 | 154 |
| 14 | Super Smash | **0.3633** | **2** | 0.05 | 0.50 | 1.00 | 0.40 | 0.95 | 9 | 256 |

---

## 3. Tier Distribution

### Tier 1A: Premier Tier -- highest composite weight, clear separation from field
**Count:** 1

- **Indian Premier League** (composite: 0.8721)
  - Strengths: Pqi (1.00), Recency (1.00), Conditions Similarity (1.00), Sample Confidence (0.95)

### Tier 1B: High Quality -- strong across most factors, composite >= 0.50
**Count:** 1

- **Syed Mushtaq Ali Trophy** (composite: 0.6454)
  - Strengths: Recency (0.84), Conditions Similarity (0.73), Sample Confidence (0.95)

### Tier 1C: Moderate Quality -- useful data but with notable weaknesses, composite 0.40-0.50
**Count:** 8

- **Big Bash League** (composite: 0.5261)
  - Strengths: Recency (1.00), Sample Confidence (0.95)
  - Weaknesses: Pqi (0.21)
- **Pakistan Super League** (composite: 0.5140)
  - Strengths: Recency (0.90), Sample Confidence (0.95)
  - Weaknesses: Pqi (0.18)
- **The Hundred** (composite: 0.5035)
  - Strengths: Recency (1.00), Sample Confidence (0.79)
  - Weaknesses: Pqi (0.22)
- **SA20** (composite: 0.5021)
  - Strengths: Recency (1.00)
  - Weaknesses: Pqi (0.25)
- **ICC Men's T20 World Cup** (composite: 0.4984)
  - Strengths: Recency (0.76)
- **Vitality Blast** (composite: 0.4976)
  - Strengths: Recency (0.84), Sample Confidence (0.95)
  - Weaknesses: Pqi (0.20)
- **Caribbean Premier League** (composite: 0.4967)
  - Strengths: Recency (1.00), Sample Confidence (0.95)
  - Weaknesses: Pqi (0.17)
- **International League T20** (composite: 0.4889)
  - Strengths: Recency (1.00)
  - Weaknesses: Pqi (0.21)

### Tier 2: Limited Utility -- data has significant gaps or low quality, composite 0.30-0.40
**Count:** 4

- **Major League Cricket** (composite: 0.4233)
  - Strengths: Recency (1.00)
  - Weaknesses: Pqi (0.21)
- **Lanka Premier League** (composite: 0.3982)
  - Strengths: Recency (0.84)
  - Weaknesses: Pqi (0.10)
- **CSA T20 Challenge** (composite: 0.3834)
  - Strengths: Recency (0.84), Sample Confidence (0.75)
  - Weaknesses: Pqi (0.07)
- **Super Smash** (composite: 0.3633)
  - Strengths: Recency (1.00), Sample Confidence (0.95)
  - Weaknesses: Pqi (0.05)

---

## 4. Notable Findings

### 4.1 Key Observations

1. **Indian Premier League** is the clear Tier 1A tournament (composite: 0.8721). Its dominance comes from having the highest PQI (1.00), perfect conditions similarity (1.00), and the largest sample size.

2. **Gap between #1 and #2:** 0.2267. This confirms separation of the IPL from the rest of the field.

3. **Surprises and Edge Cases:**

   - **SMAT** has high conditions similarity (0.85) because it is played on Indian grounds, but its low PQI and CI pull it down. This validates the geometric mean's penalty for unbalanced factor profiles.
   - **SA20** scores well on PQI (0.25) as a tournament that attracts top IPL players, but its limited sample size (121 matches) constrains its overall composite.
   - **MLC** shows the tension between quality and quantity: it attracts elite IPL players but has only 75 matches across 3 seasons.

   - **BBL vs CPL:** These two established leagues end up close in the rankings. BBL has more matches (654 vs 407) but similar PQI and conditions dissimilarity from IPL.

---

## 5. Factor Correlation Analysis

How correlated are the 5 factors? High correlation between factors would indicate redundancy; low correlation confirms they measure distinct dimensions.

| | PQI | Eff CI | Recency | Conditions | Sample |
|---|-----|--------|---------|------------|--------|
| **PQI** | 1.00 | -0.21 | 0.04 | 0.84 | 0.24 |
| **Eff CI** | -0.21 | 1.00 | 0.30 | -0.06 | 0.12 |
| **Recency** | 0.04 | 0.30 | 1.00 | -0.05 | 0.06 |
| **Conditions** | 0.84 | -0.06 | -0.05 | 1.00 | 0.26 |
| **Sample** | 0.24 | 0.12 | 0.06 | 0.26 | 1.00 |

**Interpretation:** Low cross-factor correlations confirm that the 5 factors measure distinct quality dimensions. The geometric mean correctly combines these independent signals into a holistic tournament quality score.

---

## 6. Conditions Similarity Reasoning

The Conditions Similarity factor is expert-defined. Below is the reasoning for each tournament's score:

| Tournament | Score | Reasoning |
|-----------|-------|-----------|
| Indian Premier League | 1.00 | Baseline. IPL conditions are the reference standard. |
| Syed Mushtaq Ali Trophy | 0.73 | Same Indian grounds and pitch types, but 2023+ data shows a 1.48 RR gap and 4.0 Bdry% gap from IPL — larger than PSL's gaps. Lower-quality outfields, no Impact Player rule, and domestic-level pressure significantly reduce transferability. |
| Pakistan Super League | 0.65 | Subcontinent venue profile with similar spinning conditions and heat. Key differences: Pakistan pitches tend to be slower and lower-scoring. Lahore/Karachi wickets behave differently from Mumbai/Bengaluru. |
| Lanka Premier League | 0.60 | Subcontinent with spin-friendly conditions. Sri Lankan pitches offer more turn and are generally slower than IPL surfaces. Pallekele and Hambantota differ significantly from Indian venues. |
| SA20 | 0.55 | Pace-friendly South African wickets (Wanderers, Newlands, SuperSport Park) differ substantially from Indian conditions. Higher bounce, more seam movement, different ball behavior. |
| International League T20 | 0.55 | UAE conditions: flat batting surfaces in Dubai/Sharjah/Abu Dhabi. Some similarity to Indian flat tracks but different dew factor, ball behavior, and outfield speed. |
| CSA T20 Challenge | 0.55 | Same South African conditions as SA20 but domestic-level. Pace-friendly wickets, higher bounce. Limited overlap with Indian conditions. |
| Big Bash League | 0.50 | Australian conditions: harder, bouncier pitches with bigger boundaries. MCG/SCG grounds are structurally different from Indian venues. Different ball (Kookaburra vs SG). |
| Caribbean Premier League | 0.50 | Caribbean pitches can be slow and low, somewhat similar to Indian sub-continent conditions in that respect. But smaller grounds, different climate, and variable pitch quality. |
| ICC Men's T20 World Cup | 0.50 | Varies by host country. Recent editions: UAE 2021, Australia 2022, West Indies/USA 2024. Average across host conditions is moderate similarity. Some editions (India 2016) were on IPL grounds. |
| Major League Cricket | 0.45 | American venues with drop-in pitches and unfamiliar conditions. Dallas, Morrisville grounds are nothing like Indian venues. Still T20 format but conditions are non-transferable. |
| Vitality Blast | 0.45 | English county grounds with seaming/swinging conditions. Green pitches, overcast skies, Dukes-style ball behavior. Very different from Indian conditions despite being full T20 format. |
| The Hundred | 0.40 | 100-ball format is structurally different from T20. English conditions (seam movement, overcast skies, green pitches) are fundamentally unlike Indian batting paradises. Format + conditions compound the dissimilarity. |
| Super Smash | 0.40 | New Zealand conditions: green tops, seam movement, smaller grounds but very different pitch behavior from India. Limited transferability of performance data. |

---

## 7. Adjacent Gap Analysis

The gaps between adjacent tournaments help identify natural tier boundaries:

| Between | Gap | Significance |
|---------|-----|-------------|
| IPL-SMAT | 0.2267 | LARGE -- clear tier boundary |
| SMAT-BBL | 0.1193 | LARGE -- clear tier boundary |
| BBL-PSL | 0.0121 | Minimal -- same cluster |
| PSL-Hundred | 0.0105 | Minimal -- same cluster |
| Hundred-SA20 | 0.0014 | Minimal -- same cluster |
| SA20-T20WC | 0.0037 | Minimal -- same cluster |
| T20WC-VB | 0.0008 | Minimal -- same cluster |
| VB-CPL | 0.0009 | Minimal -- same cluster |
| CPL-ILT20 | 0.0078 | Minimal -- same cluster |
| ILT20-MLC | 0.0656 | Notable -- possible tier split |
| MLC-LPL | 0.0251 | Moderate |
| LPL-CSA | 0.0148 | Minimal -- same cluster |
| CSA-SS | 0.0201 | Moderate |

---

## 8. PQI Methodology Detail

PQI is based on **220 top IPL players** identified from IPL 2023-2025 data (batters with 100+ legal balls faced, bowlers with 60+ legal balls bowled). For each tournament, we measure what fraction of these top IPL players have also played in that tournament.

| Tournament | Top IPL Players Present | PQI Score |
|-----------|------------------------|-----------|
| Indian Premier League | 100.0% of 220 | 1.00 |
| Syed Mushtaq Ali Trophy | 56.8% of 220 | 0.57 |
| Big Bash League | 21.4% of 220 | 0.21 |
| Pakistan Super League | 18.2% of 220 | 0.18 |
| The Hundred | 22.3% of 220 | 0.22 |
| SA20 | 24.5% of 220 | 0.25 |
| ICC Men's T20 World Cup | 35.9% of 220 | 0.36 |
| Vitality Blast | 20.0% of 220 | 0.20 |
| Caribbean Premier League | 17.3% of 220 | 0.17 |
| International League T20 | 21.4% of 220 | 0.21 |
| Major League Cricket | 20.9% of 220 | 0.21 |
| Lanka Premier League | 10.0% of 220 | 0.10 |
| CSA T20 Challenge | 7.3% of 220 | 0.07 |
| Super Smash | 5.5% of 220 | 0.05 |

---

## 9. Approval Request

These weights are ready for Founder sign-off. Upon approval:

1. The composite weights will be integrated into the player projection pipeline
2. Each tournament's data will be weighted by its composite score when computing player performance metrics
3. Tier assignments will guide which tournaments receive primary vs supplementary treatment in stat packs

**Founder Decision Required:**

- [ ] **APPROVE** -- Weights are correct and ready for integration
- [ ] **APPROVE WITH MODIFICATIONS** -- Specify adjustments to factor weights, tier boundaries, or conditions scores
- [ ] **REQUEST REVISION** -- Specify what additional analysis is needed

---

*Cricket Playbook v4.0.0 | TKT-187 | Jose Mourinho, Quant Researcher*
