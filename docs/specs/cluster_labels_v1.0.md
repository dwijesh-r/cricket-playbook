# Andy Flower - Player Cluster Labels v1.0

**Reviewer:** Andy Flower (Cricket Technical Advisor)
**Review Date:** 2026-01-20
**Model:** K-means Clustering (Stephen Curry)
**Status:** APPROVED

---

## Executive Summary

Following Stephen Curry's data-driven clustering analysis, I have reviewed the player groupings and assigned cricket-meaningful labels to each cluster. The K-means algorithm has identified natural groupings that align well with established cricket archetypes.

**Batters:** 5 clusters, 87 players total
**Bowlers:** 5 clusters, 152 players total

---

## Batter Cluster Labels

### Cluster 0: ALL-ROUND FINISHERS (22 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Overall SR | 133.2 | Above average |
| Overall Avg | 27.7 | Solid |
| Death SR | 164.1 | Strong finishing |
| Death Boundary % | 22.5% | Good power |

**Label Rationale:** These are batting all-rounders who contribute across phases but excel at the death. They provide balance and can accelerate when needed.

**Representative Players:**
- Hardik Pandya, Marcus Stoinis, Mitchell Marsh
- Moeen Ali, Sam Curran, Yusuf Pathan
- Venkatesh Iyer, Rahul Tripathi

**Editorial Usage:** "All-round finisher who can accelerate in death overs"

---

### Cluster 1: POWER FINISHERS (13 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Overall SR | 144.8 | Elite |
| Overall Avg | 33.0 | Excellent |
| Death SR | **199.9** | Exceptional |
| Death Boundary % | **29.5%** | Highest |

**Label Rationale:** The most explosive finishers in T20 cricket. Their death-overs SR approaches 200 - nearly a run per ball with exceptional boundary-hitting.

**Representative Players:**
- AB de Villiers, Jos Buttler, Chris Gayle
- Suryakumar Yadav, Rishabh Pant, Sanju Samson
- Liam Livingstone, Rajat Patidar

**Editorial Usage:** "Elite power finisher capable of 200+ SR in death overs"

---

### Cluster 2: ANCHORS (28 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Overall SR | 123.5 | Conservative |
| Overall Avg | 28.3 | Solid |
| PP SR | 103.5 | Slow starter |
| Boundary % | 14.9% | Lowest |

**Label Rationale:** Traditional anchors who prioritize building innings. Lower boundary rates but steady accumulation. Often bat through phases.

**Representative Players:**
- David Miller, Dinesh Karthik, DJ Bravo
- Yuvraj Singh, Ambati Rayudu, DJ Hooda
- Vijay Shankar, Moises Henriques

**Editorial Usage:** "Anchor who builds innings and rotates strike"

---

### Cluster 3: ELITE TOP-ORDER (18 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Overall SR | 135.3 | Very good |
| Overall Avg | **39.2** | Highest |
| Mid SR | 133.5 | Consistent |
| Death SR | 175.2 | Strong |

**Label Rationale:** The cream of IPL batting - highest averages with excellent strike rates. These are franchise cornerstones who anchor AND accelerate.

**Representative Players:**
- David Warner, Shubman Gill, KL Rahul
- Suresh Raina, Ruturaj Gaikwad, Devon Conway
- B Sai Sudharsan, Tilak Varma

**Editorial Usage:** "Elite top-order batter with exceptional consistency and acceleration"

---

### Cluster 4: AGGRESSIVE OPENERS (6 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Overall SR | **162.4** | Highest |
| Overall Avg | 29.7 | Good |
| PP SR | **161.3** | Explosive |
| Boundary % | **24.7%** | Very high |

**Label Rationale:** Maximum aggression from ball one. These batters maintain 160+ SR across ALL phases - rare in cricket. High-risk, high-reward.

**Representative Players:**
- Travis Head, Nicholas Pooran, Sunil Narine
- Glenn Maxwell, Jonny Bairstow, Abhishek Sharma

**Editorial Usage:** "Ultra-aggressive opener with 160+ SR from the powerplay"

---

## Bowler Cluster Labels

### Cluster 0: EXPENSIVE OPTIONS (31 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Economy | **9.61** | Highest |
| Average | 36.1 | Expensive wickets |
| Dot Ball % | 34.3% | Low pressure |
| Phase Split | 37% PP / 36% Mid / 27% Death | Balanced |

**Label Rationale:** Part-time bowlers or those who leak runs. Used situationally rather than as primary options.

**Representative Players:**
- Ben Stokes, Cameron Green, Navdeep Saini
- Varun Aaron, Ankit Rajpoot

**Editorial Usage:** "Part-time option; use with caution against quality batting"

---

### Cluster 1: POWERPLAY ASSASSINS (29 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Economy | 7.97 | Very good |
| PP Economy | **7.28** | Elite |
| Dot Ball % | **41.8%** | Highest |
| Phase Split | **50% PP** / 21% Mid / 29% Death | New-ball heavy |

**Label Rationale:** Premium new-ball bowlers who dominate the powerplay. High dot-ball rates create pressure, and they often return for death overs.

**Representative Players:**
- Dale Steyn, Lasith Malinga, Jasprit Bumrah
- Zaheer Khan, Brett Lee, Deepak Chahar
- Munaf Patel, Dirk Nannes

**Editorial Usage:** "Powerplay specialist with elite new-ball control"

---

### Cluster 2: MIDDLE-OVERS SPINNERS (26 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Economy | **7.63** | Best |
| Mid Economy | 7.37 | Elite |
| Average | 28.1 | Good |
| Phase Split | 14% PP / **70% Mid** / 16% Death | Heavily middle |

**Label Rationale:** The elite spinners who strangle in middle overs. 70% of their workload in overs 7-15, with league-best economy rates.

**Representative Players:**
- Anil Kumble, Muttiah Muralitharan, Harbhajan Singh
- Sunil Narine, Rashid Khan, Daniel Vettori
- Johan Botha, R Ashwin

**Editorial Usage:** "Middle-overs spin specialist with elite control"

---

### Cluster 3: WORKHORSE SEAMERS (45 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Economy | 8.82 | Average |
| Average | 28.4 | Good |
| Dot Ball % | 36.3% | Average |
| Phase Split | 40% PP / 29% Mid / 30% Death | Balanced |

**Label Rationale:** The largest cluster - reliable seamers used across all phases. Not specialists but consistent contributors.

**Representative Players:**
- Trent Boult, Sandeep Sharma, Mustafizur Rahman
- Dwayne Bravo (as bowler), Jason Holder
- Mohit Sharma, Albie Morkel

**Editorial Usage:** "Workhorse seamer; reliable across all phases"

---

### Cluster 4: HOLDING SPINNERS (21 players)

**Characteristics:**
| Metric | Value | Context |
|--------|-------|---------|
| Economy | 8.03 | Good |
| Average | 35.2 | Higher |
| Mid Economy | 7.62 | Good |
| Phase Split | 22% PP / **63% Mid** / 14% Death | Middle heavy |

**Label Rationale:** Secondary spin options - often all-rounders who bowl in middle overs to hold an end. Less strike-power than Cluster 2.

**Representative Players:**
- Suresh Raina, Shakib Al Hasan, Washington Sundar
- Yusuf Pathan, Stuart Binny, Pravin Tambe
- Shahbaz Nadeem, Murali Kartik

**Editorial Usage:** "Holding spinner who can tie down in middle overs"

---

## Summary Table

### Batter Labels

| Cluster | Label | Players | Key Trait |
|---------|-------|---------|-----------|
| 0 | All-Round Finishers | 22 | Death-overs ability + all-round |
| 1 | Power Finishers | 13 | 200 SR in death, explosive |
| 2 | Anchors | 28 | Conservative, low boundary % |
| 3 | Elite Top-Order | 18 | Highest avg (39), consistent |
| 4 | Aggressive Openers | 6 | 162 SR, maximum intent |

### Bowler Labels

| Cluster | Label | Players | Key Trait |
|---------|-------|---------|-----------|
| 0 | Expensive Options | 31 | Economy 9.6, part-time |
| 1 | Powerplay Assassins | 29 | 50% PP, elite dot ball % |
| 2 | Middle-Overs Spinners | 26 | 70% middle, best economy |
| 3 | Workhorse Seamers | 45 | Balanced phase usage |
| 4 | Holding Spinners | 21 | 63% middle, tie-down role |

---

## Recommendations for Stat Packs

1. **Include cluster labels** in player profiles for quick archetype identification
2. **Use in tactical analysis** - e.g., "RCB has 3 Power Finishers but no Elite Top-Order anchor"
3. **Squad balance assessment** - teams need diversity across clusters
4. **Matchup context** - Aggressive Openers vs Powerplay Assassins is a key battle

---

## Sign-off

I approve these cluster labels for use in Cricket Playbook editorial content.

The K-means clustering has successfully identified meaningful cricket archetypes that align with established terminology and strategic concepts.

**Status: APPROVED FOR PRODUCTION**

---

*Andy Flower*
*Cricket Technical Advisor*
*2026-01-20*
