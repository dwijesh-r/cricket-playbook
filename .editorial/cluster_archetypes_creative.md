# Andy Flower - Player Archetypes: A Cricket Perspective

**Author:** Andy Flower (Cricket Technical Advisor)
**Date:** 2026-01-20
**Status:** For User Review

---

## Introduction

Stephen Curry's K-means clustering has surfaced natural groupings in the data. My job now is to give these clusters names that resonate with cricket intuition - names that a coach, commentator, or fan would immediately understand.

I've tried to be creative while staying true to what the data shows. These aren't just statistical buckets - they're recognizable archetypes that have existed in cricket for generations.

---

## Batter Archetypes

### THE CONDUCTORS (Cluster 3 - 18 players)

**The Data Says:** SR 135.3, Avg **39.2** (highest), consistent across all phases

**The Cricket Says:** These are the maestros who orchestrate innings. They don't just bat - they conduct the entire orchestra. They know when to attack, when to defend, when to rotate. Their high averages show they rarely give their wicket away cheaply.

**Prototype:** Virat Kohli, David Warner, Shubman Gill

**Commentary Line:** *"He's not just batting, he's conducting a masterclass."*

**Stat Pack Label:** `Conductor`

---

### THE HURRICANES (Cluster 4 - 6 players)

**The Data Says:** SR **162.4** (highest), Boundary% **24.7%**, maintains 160+ SR across ALL phases

**The Cricket Says:** These batters play one way only - attack. They're the ones who can take the game away in a single over. No rebuilding, no consolidation - just carnage. Extremely rare (only 6 players) because sustaining 160+ SR requires extraordinary talent.

**Prototype:** Travis Head, Sunil Narine, Glenn Maxwell

**Commentary Line:** *"When he walks in, the bowler's already lost the plot."*

**Stat Pack Label:** `Hurricane`

---

### THE ASSASSINS (Cluster 1 - 13 players)

**The Data Says:** SR 144.8, Death SR **199.9**, Death Boundary% **29.5%**

**The Cricket Says:** The death-overs specialists. They wait, they assess, and then they strike. A SR approaching 200 in the death overs means they're scoring almost a run per ball while hitting boundaries 30% of the time. They don't just finish games - they assassinate bowling attacks.

**Prototype:** AB de Villiers, Jos Buttler, Rishabh Pant, Suryakumar Yadav

**Commentary Line:** *"He's ice cold with a blade in his hand at the death."*

**Stat Pack Label:** `Assassin`

---

### THE WARRIORS (Cluster 0 - 22 players)

**The Data Says:** SR 133.2, Avg 27.7, Death SR 164.1, good all-round bowling credentials

**The Cricket Says:** The modern T20 demands players who can do a bit of everything. These warriors bat in the middle order, accelerate at the death, and then bowl crucial overs. They're the glue that holds a T20 team together - not flashy, but indispensable.

**Prototype:** Hardik Pandya, Marcus Stoinis, Sam Curran, Mitchell Marsh

**Commentary Line:** *"He'll give you 30 with the bat and 2 with the ball - that's a match-winning contribution."*

**Stat Pack Label:** `Warrior`

---

### THE ARCHITECTS (Cluster 2 - 28 players)

**The Data Says:** SR 123.5, Boundary% **14.9%** (lowest), PP SR 103.5

**The Cricket Says:** The builders, the accumulators, the ones who ensure the innings has a foundation. Low boundary rates but they rarely get out cheaply. They're often the senior player who guides the young hitters - the architect who designs the blueprint others execute.

**Prototype:** Dinesh Karthik (early career), Yuvraj Singh, Ambati Rayudu

**Commentary Line:** *"He's not here to hit sixes - he's here to make sure someone else can."*

**Stat Pack Label:** `Architect`

---

## Bowler Archetypes

### THE GENERALS (Cluster 1 - 29 players)

**The Data Says:** Economy 7.97, PP Economy **7.28**, Dot Ball% **41.8%** (highest), **50% workload in powerplay**

**The Cricket Says:** The new-ball generals who set the tone. They attack the stumps, extract movement, build pressure with dots, and often return at the death. These are your leaders - the bowlers captains trust with the most critical overs.

**Prototype:** Jasprit Bumrah, Dale Steyn, Lasith Malinga, Deepak Chahar

**Commentary Line:** *"Give him the new ball and watch him take control of the game."*

**Stat Pack Label:** `General`

---

### THE SURGEONS (Cluster 2 - 26 players)

**The Data Says:** Economy **7.63** (best), Mid Economy 7.37, **70% workload in middle overs**

**The Cricket Says:** Spinners who operate with surgical precision in the middle overs. They don't need pace or swing - just guile, variation, and the ability to land the ball on a coin. They're the reason teams can't accelerate in overs 7-15.

**Prototype:** Rashid Khan, Sunil Narine, Yuzvendra Chahal, Muttiah Muralitharan

**Commentary Line:** *"He's not bowling - he's performing surgery on the batting lineup."*

**Stat Pack Label:** `Surgeon`

---

### THE SENTRIES (Cluster 4 - 21 players)

**The Data Says:** Economy 8.03, Mid Economy 7.62, **63% workload in middle overs**

**The Cricket Says:** The holding bowlers who guard an end while the strike bowlers attack from the other. Often part-time spinners or all-rounders who can tie down batters without being expensive. Essential for maintaining pressure.

**Prototype:** Washington Sundar, Suresh Raina, Shakib Al Hasan

**Commentary Line:** *"He's holding fort while the others reload."*

**Stat Pack Label:** `Sentry`

---

### THE TROOPERS (Cluster 3 - 45 players)

**The Data Says:** Economy 8.82, balanced 40/29/30 phase split

**The Cricket Says:** The workhorses. The reliable seamers who bowl anywhere, anytime. They might not have the lowest economy or the most wickets, but they're always available, always willing, always putting in the hard yards. Every team needs troopers.

**Prototype:** Trent Boult, Sandeep Sharma, Mohit Sharma, Jason Holder

**Commentary Line:** *"He runs in all day, asks no questions, and does the job."*

**Stat Pack Label:** `Trooper`

---

### THE GAMBLERS (Cluster 0 - 31 players)

**The Data Says:** Economy **9.61** (highest), Avg 36.1

**The Cricket Says:** High risk, high reward. These are often fast bowlers with raw pace but inconsistent lines, or part-time options who occasionally produce magic. You use them when you need a wicket and are willing to concede runs. Sometimes they win you the game; sometimes they lose it.

**Prototype:** Ben Stokes (as bowler), Navdeep Saini, Varun Aaron

**Commentary Line:** *"He's a gamble, but when it comes off, it really comes off."*

**Stat Pack Label:** `Gambler`

---

## Summary Table

### Batter Archetypes

| Archetype | Players | Key Trait | Prototypes |
|-----------|---------|-----------|------------|
| **Conductor** | 18 | Highest average (39), orchestrates innings | Kohli, Warner, Gill |
| **Hurricane** | 6 | 162 SR, maximum attack all phases | Head, Narine, Maxwell |
| **Assassin** | 13 | 200 SR in death, ice-cold finisher | ABD, Buttler, Pant, SKY |
| **Warrior** | 22 | All-round contributor, death acceleration | Hardik, Stoinis, Marsh |
| **Architect** | 28 | Foundation builder, low risk | Karthik, Yuvraj, Rayudu |

### Bowler Archetypes

| Archetype | Players | Key Trait | Prototypes |
|-----------|---------|-----------|------------|
| **General** | 29 | New-ball leader, 50% PP workload | Bumrah, Steyn, Malinga |
| **Surgeon** | 26 | Best economy, 70% middle overs | Rashid, Narine, Chahal |
| **Sentry** | 21 | Holding role, ties down batters | Sundar, Raina, Shakib |
| **Trooper** | 45 | Reliable workhorse, bowls anywhere | Boult, Sandeep, Holder |
| **Gambler** | 31 | High risk/reward, expensive but can strike | Stokes, Saini, Aaron |

---

## Editorial Usage Guide

When writing about players, use the archetype to add color:

- *"Mumbai Indians have assembled three Assassins in their middle order..."*
- *"The Generals - Bumrah and Chahar - will share the new ball..."*
- *"With Narine opening, KKR are unleashing a Hurricane from ball one..."*
- *"He's not a flashy player, but every team needs an Architect..."*

---

## Sign-off

I believe these names capture both the statistical reality and the cricket romance. They should resonate with viewers and readers while remaining analytically defensible.

Happy to refine based on feedback.

---

*Andy Flower*
*Cricket Technical Advisor*
*2026-01-20*
