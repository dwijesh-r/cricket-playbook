# Cricket Playbook — Metric Pack (v2)

## Philosophy
Impact > quantity. If a metric doesn’t change how a reader watches cricket, it doesn’t ship.
No predictions/projections/betting/fantasy.

## Data scope
- T20 only
- Every metric computed in **two contexts**:
  1) Tournament‑specific window (primary)
  2) All‑T20 baseline (context)
- Minimum sample thresholds required; always display sample sizes.

## Tier 1 — Core / Must‑Have
### 1) Phase & over‑window performance (team + player)
- SR/dot%/boundary% by phase (PP/Middle/Death)
- Over windows: 1–6, 7–10, 11–15, 16–20
- Entry‑over bucket performance (0–2, 3–6, 7–10, 11–15, 16–20)

### 2) Boundary & dot profile
- Boundary rate (4+6 per ball), six rate, dot%
- Bowling: boundary conceded%, dot%, suppression index

### 3) Roster construction
- Batting depth (% balls 1–4 vs 5–7)
- Bowling depth (count of bowlers with ≥2 overs)
- Overs concentration (top 3 share)
- All‑rounder usage

### 4) Squad change impact (structural)
- % runs replaced, % overs replaced, phase impact of losses/gains

### 5) Partnerships
- Top partnerships by runs/balls/RR
- Partnership by wicket number
- Stability vs acceleration pairs

## Tier 2 — High‑impact behavior (optional)
### 6) Post‑wicket response
- Next 6–12 balls: SR/dot% deltas, dismissal rate
- Indices: shock absorption, counter‑punch

### 7) Start‑of‑innings tendencies
- Overs 1–2 and 1–4 vs 3–6; classify starter/builder/delayed hitter

### 8) Collapse & recovery
- After early 2 wickets: overs 7–12 RR, boundary%, wicket preservation

### 9) Consistency & volatility
- Phase variance (RR, boundaries, wickets)

## Tier 2 — Experimental ML (gated)
### 10) Archetype clustering (k‑means)
- Interpretable features only; neutral labels; no “elite/trash” language.
Publication requires Flower + Brady + Kanté gates.

## Forbidden
Win probabilities, title odds, projections, points‑table forecasts, betting/fantasy metrics, black‑box ML.

## Traceability
Every published stat must record: metric name, context, data window, query path, data_version, run timestamp.
