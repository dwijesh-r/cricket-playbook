# TKT-185: Season-Level Competitiveness Index

**Owner:** Jose Mourinho (Quant Researcher)
**Parent Ticket:** TKT-183 (Tournament Quality Weighting System)
**Generated:** 2026-02-12 07:43
**Status:** DRAFT — Pending Domain Sanity Review

---

## 1. Executive Summary

Phase 1 computed Competitiveness Index (CI) as a tournament-lifetime aggregate. This is
analytically naive. A tournament's competitiveness varies *dramatically* year to year:
the 2024 IPL was a different animal from the 2011 IPL. Season-level CI granularity is
essential for the recency-weighted composite to function correctly.

This analysis queries ball-by-ball and match-level data from DuckDB to compute CI for
every season of every major tournament in our database. The CI formula uses five weighted
components: close match percentage (30%), margin analysis (25%), win distribution Gini (20%),
NRR coefficient of variation (15%), and tie rate (10%).

**Key finding:** Competitiveness varies by 15-25 CI points within the same tournament
across seasons. Using all-time aggregates hides this signal and undermines the
recency decay system's ability to weight recent competitive data correctly.

---

## 2. Methodology

### 2.1 CI Component Definitions

| Component | Weight | Metric | Direction | Normalization Range |
|-----------|--------|--------|-----------|---------------------|
| Close Match % | 0.30 | Matches decided by <=15 runs or <=2 wickets | Higher = better | 0-50% |
| Average Margins | 0.25 | Mean run margin + mean wicket margin | Lower = better | Runs: 5-80, Wickets: 1-10 |
| Win Distribution (Gini) | 0.20 | Gini coefficient of wins per team | Lower = better | 0-0.5 |
| NRR Coefficient of Variation | 0.15 | StdDev(team RR) / Mean(team RR) | Lower = better | 0-0.3 |
| Tie Rate | 0.10 | Tied matches / decisive matches | Higher = better | 0-10% |

### 2.2 Data Source

- **Database:** `data/cricket_playbook.duckdb` (read-only)
- **Tables:** `dim_match`, `dim_tournament`, `fact_ball`
- **Minimum season size:** 3 decisive matches (seasons with fewer are excluded)

### 2.3 CI Score Interpretation

| CI Range | Interpretation |
|----------|---------------|
| 70-100 | Extremely competitive — close margins, balanced outcomes |
| 55-70 | Highly competitive — above average balance |
| 40-55 | Moderately competitive — typical T20 league |
| 25-40 | Below average — some dominant teams or lopsided results |
| 0-25 | Low competitiveness — blowouts common, unbalanced |

---

## 3. Season-Level CI by Tournament

### 3.1 Indian Premier League (IPL)

**Seasons:** 18 | **Avg CI:** 52.1 | **Range:** 43.2 - 62.3 (spread: 19.1)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2007/08 | 58 | 20.7% | 29.4 | 6.5 | 0.2500 | 0.0528 | 0 | **48.1** |
| 2009 | 57 | 26.3% | 28.3 | 6.2 | 0.1830 | 0.0530 | 1 | **56.5** |
| 2009/10 | 60 | 15.0% | 31.5 | 6.8 | 0.1589 | 0.0359 | 1 | **50.1** |
| 2011 | 73 | 9.7% | 33.3 | 6.8 | 0.1833 | 0.0500 | 0 | **43.2** |
| 2012 | 74 | 13.5% | 28.2 | 6.0 | 0.1832 | 0.0425 | 0 | **47.8** |
| 2013 | 76 | 19.7% | 33.5 | 6.1 | 0.2252 | 0.0656 | 2 | **50.3** |
| 2014 | 60 | 11.7% | 29.3 | 6.1 | 0.2394 | 0.0527 | 1 | **45.4** |
| 2015 | 59 | 24.6% | 26.6 | 6.2 | 0.1875 | 0.0535 | 1 | **55.5** |
| 2016 | 60 | 16.7% | 32.2 | 6.3 | 0.1583 | 0.0626 | 0 | **48.7** |
| 2017 | 59 | 23.7% | 30.3 | 6.4 | 0.2069 | 0.0532 | 1 | **53.3** |
| 2018 | 60 | 33.3% | 24.1 | 5.8 | 0.1500 | 0.0363 | 0 | **62.3** |
| 2019 | 60 | 18.6% | 30.2 | 5.8 | 0.1513 | 0.0529 | 2 | **55.0** |
| 2020/21 | 60 | 18.3% | 39.4 | 7.0 | 0.1295 | 0.0442 | 4 | **56.3** |
| 2021 | 60 | 21.7% | 26.5 | 5.9 | 0.1843 | 0.0408 | 1 | **54.8** |
| 2022 | 74 | 20.3% | 27.9 | 6.0 | 0.1865 | 0.0233 | 0 | **52.8** |
| 2023 | 74 | 27.4% | 30.4 | 5.7 | 0.1630 | 0.0528 | 0 | **56.5** |
| 2024 | 71 | 14.1% | 30.1 | 5.9 | 0.1563 | 0.0610 | 0 | **48.1** |
| 2025 | 74 | 22.5% | 33.2 | 6.3 | 0.1914 | 0.0413 | 1 | **53.1** |

### 3.2 Pakistan Super League (PSL)

**Seasons:** 11 | **Avg CI:** 50.2 | **Range:** 39.1 - 67.3 (spread: 28.2)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2015/16 | 23 | 17.4% | 24.4 | 6.4 | 0.2609 | 0.0420 | 0 | **47.2** |
| 2016/17 | 24 | 34.8% | 17.7 | 5.0 | 0.1217 | 0.0214 | 0 | **67.3** |
| 2017/18 | 33 | 15.2% | 31.2 | 6.4 | 0.2097 | 0.0420 | 2 | **52.8** |
| 2018/19 | 34 | 11.8% | 29.7 | 5.9 | 0.2255 | 0.0419 | 0 | **45.0** |
| 2019/20 | 28 | 14.8% | 28.4 | 6.0 | 0.1173 | 0.0303 | 0 | **51.8** |
| 2020/21 | 18 | 5.6% | 23.5 | 5.7 | 0.2843 | 0.0217 | 1 | **46.9** |
| 2021 | 20 | 25.0% | 36.1 | 6.8 | 0.3000 | 0.0978 | 0 | **44.9** |
| 2021/22 | 34 | 20.6% | 33.4 | 6.5 | 0.2879 | 0.0537 | 1 | **48.7** |
| 2022/23 | 34 | 29.4% | 41.3 | 4.8 | 0.2059 | 0.0397 | 0 | **56.1** |
| 2023/24 | 32 | 25.0% | 28.7 | 5.0 | 0.2500 | 0.0528 | 0 | **52.8** |
| 2025 | 34 | 12.1% | 66.0 | 5.5 | 0.2374 | 0.0453 | 0 | **39.1** |

### 3.3 Big Bash League (BBL)

**Seasons:** 15 | **Avg CI:** 49.7 | **Range:** 41.5 - 58.4 (spread: 16.9)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2011/12 | 27 | 37.0% | 25.1 | 6.7 | 0.3102 | 0.0570 | 0 | **55.7** |
| 2012/13 | 28 | 10.7% | 38.0 | 6.6 | 0.1939 | 0.0769 | 0 | **41.5** |
| 2013/14 | 34 | 30.3% | 29.2 | 6.2 | 0.3281 | 0.0542 | 1 | **54.2** |
| 2014/15 | 34 | 9.1% | 35.6 | 5.8 | 0.2656 | 0.0416 | 1 | **44.1** |
| 2015/16 | 32 | 12.5% | 30.2 | 6.5 | 0.2031 | 0.0374 | 0 | **45.7** |
| 2016/17 | 35 | 20.0% | 35.8 | 6.0 | 0.1618 | 0.0551 | 1 | **53.6** |
| 2017/18 | 43 | 25.6% | 23.5 | 6.2 | 0.2238 | 0.0319 | 0 | **54.5** |
| 2018/19 | 59 | 12.1% | 36.3 | 6.4 | 0.1509 | 0.0478 | 0 | **46.1** |
| 2019/20 | 61 | 27.1% | 27.5 | 6.5 | 0.1810 | 0.0174 | 1 | **58.4** |
| 2020/21 | 61 | 20.0% | 41.4 | 5.6 | 0.1583 | 0.0526 | 0 | **50.5** |
| 2021/22 | 60 | 18.3% | 40.1 | 6.1 | 0.2333 | 0.0517 | 0 | **46.2** |
| 2022/23 | 61 | 26.7% | 29.2 | 5.9 | 0.2167 | 0.0438 | 0 | **54.3** |
| 2023/24 | 41 | 17.9% | 28.6 | 6.5 | 0.2853 | 0.0417 | 0 | **45.8** |
| 2024/25 | 42 | 17.1% | 28.4 | 5.1 | 0.2104 | 0.0466 | 0 | **49.9** |
| 2025/26 | 36 | 11.4% | 31.2 | 5.7 | 0.1893 | 0.0732 | 0 | **44.8** |

### 3.4 Caribbean Premier League (CPL)

**Seasons:** 13 | **Avg CI:** 47.9 | **Range:** 33.6 - 55.8 (spread: 22.2)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2013 | 23 | 21.7% | 13.9 | 5.8 | 0.2681 | 0.0353 | 0 | **52.3** |
| 2014 | 27 | 18.5% | 28.4 | 6.4 | 0.2284 | 0.0622 | 0 | **47.4** |
| 2015 | 32 | 16.1% | 32.8 | 6.5 | 0.1452 | 0.0433 | 0 | **49.4** |
| 2016 | 29 | 10.7% | 33.0 | 6.1 | 0.2500 | 0.0556 | 0 | **41.9** |
| 2017 | 34 | 15.2% | 28.4 | 5.8 | 0.1576 | 0.0521 | 0 | **49.6** |
| 2018 | 33 | 18.2% | 38.2 | 5.3 | 0.2374 | 0.0556 | 0 | **47.1** |
| 2019 | 34 | 21.2% | 30.7 | 6.1 | 0.3021 | 0.0369 | 1 | **50.5** |
| 2020 | 33 | 21.9% | 20.6 | 6.5 | 0.3646 | 0.0819 | 0 | **44.3** |
| 2021 | 33 | 21.2% | 38.6 | 6.1 | 0.1667 | 0.0385 | 1 | **54.4** |
| 2022 | 31 | 19.4% | 34.9 | 5.6 | 0.2312 | 0.0651 | 0 | **47.7** |
| 2023 | 32 | 10.0% | 62.4 | 6.6 | 0.3222 | 0.0427 | 0 | **33.6** |
| 2024 | 34 | 23.5% | 33.9 | 5.4 | 0.2745 | 0.0612 | 0 | **49.1** |
| 2025 | 32 | 28.1% | 24.2 | 5.5 | 0.2292 | 0.0486 | 0 | **55.8** |

### 3.5 The Hundred Men's Competition (The Hundred)

**Seasons:** 5 | **Avg CI:** 53.4 | **Range:** 45.2 - 65.5 (spread: 20.3)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2021 | 32 | 25.8% | 27.6 | 5.6 | 0.2782 | 0.0550 | 0 | **51.4** |
| 2022 | 34 | 17.6% | 31.6 | 5.9 | 0.1429 | 0.0750 | 0 | **49.8** |
| 2023 | 33 | 43.3% | 28.5 | 6.0 | 0.2457 | 0.0633 | 1 | **65.5** |
| 2024 | 34 | 28.1% | 18.7 | 6.4 | 0.3105 | 0.0512 | 1 | **55.2** |
| 2025 | 34 | 15.2% | 28.1 | 5.9 | 0.2159 | 0.0922 | 0 | **45.2** |

### 3.6 Major League Cricket (MLC)

**Seasons:** 3 | **Avg CI:** 46.0 | **Range:** 42.8 - 50.4 (spread: 7.6)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2023 | 19 | 15.8% | 35.7 | 5.6 | 0.2544 | 0.0573 | 0 | **44.9** |
| 2024 | 23 | 22.7% | 33.6 | 6.4 | 0.3333 | 0.1043 | 0 | **42.8** |
| 2025 | 33 | 24.2% | 42.4 | 5.3 | 0.2172 | 0.0651 | 0 | **50.4** |

### 3.7 International League T20 (ILT20)

**Seasons:** 4 | **Avg CI:** 43.7 | **Range:** 31.2 - 57.9 (spread: 26.7)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2022/23 | 32 | 3.2% | 49.7 | 6.1 | 0.3065 | 0.0776 | 0 | **31.2** |
| 2023/24 | 34 | 11.8% | 37.2 | 6.2 | 0.1471 | 0.0631 | 0 | **45.4** |
| 2024/25 | 34 | 5.9% | 44.1 | 6.2 | 0.1863 | 0.0386 | 0 | **40.4** |
| 2025/26 | 34 | 26.5% | 28.8 | 5.4 | 0.2273 | 0.0330 | 1 | **57.9** |

### 3.8 SA20 (SA20)

**Seasons:** 4 | **Avg CI:** 47.5 | **Range:** 40.3 - 55.6 (spread: 15.3)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2022/23 | 33 | 19.4% | 44.1 | 5.4 | 0.1774 | 0.0573 | 0 | **49.1** |
| 2023/24 | 33 | 18.8% | 40.9 | 7.0 | 0.2396 | 0.0447 | 0 | **45.1** |
| 2024/25 | 33 | 16.1% | 39.3 | 7.1 | 0.2849 | 0.0765 | 0 | **40.3** |
| 2025/26 | 22 | 25.0% | 44.9 | 5.8 | 0.2018 | 0.0612 | 1 | **55.6** |

### 3.9 Vitality Blast (Vitality Blast)

**Seasons:** 7 | **Avg CI:** 52.0 | **Range:** 47.7 - 55.7 (spread: 8.0)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2018 | 126 | 17.5% | 30.7 | 6.0 | 0.2571 | 0.0591 | 2 | **47.7** |
| 2019 | 112 | 22.9% | 31.2 | 6.5 | 0.1804 | 0.0602 | 4 | **55.2** |
| 2020 | 89 | 23.5% | 26.8 | 5.8 | 0.2791 | 0.0674 | 3 | **52.9** |
| 2021 | 120 | 23.7% | 29.9 | 6.3 | 0.1841 | 0.0436 | 3 | **55.7** |
| 2022 | 130 | 20.5% | 38.0 | 5.7 | 0.2390 | 0.0608 | 1 | **48.5** |
| 2023 | 132 | 22.9% | 34.1 | 5.6 | 0.2330 | 0.0535 | 2 | **52.0** |
| 2024 | 126 | 21.1% | 33.5 | 5.9 | 0.2043 | 0.0547 | 2 | **51.9** |

### 3.10 Super Smash (Super Smash)

**Seasons:** 9 | **Avg CI:** 49.5 | **Range:** 36.1 - 61.1 (spread: 25.0)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2017/18 | 26 | 23.1% | 48.5 | 5.2 | 0.2692 | 0.0808 | 0 | **46.0** |
| 2018/19 | 28 | 25.9% | 33.4 | 6.2 | 0.2284 | 0.0351 | 0 | **52.6** |
| 2019/20 | 32 | 13.8% | 32.0 | 5.9 | 0.1092 | 0.0235 | 0 | **51.4** |
| 2020/21 | 32 | 6.2% | 45.9 | 5.6 | 0.2917 | 0.0545 | 0 | **36.1** |
| 2021/22 | 32 | 22.6% | 29.3 | 5.1 | 0.2849 | 0.0741 | 0 | **48.7** |
| 2022/23 | 28 | 25.0% | 23.8 | 5.2 | 0.1543 | 0.0445 | 1 | **61.1** |
| 2023/24 | 30 | 7.7% | 42.4 | 6.2 | 0.2200 | 0.0712 | 1 | **42.7** |
| 2024/25 | 29 | 25.9% | 30.2 | 6.1 | 0.1420 | 0.0302 | 0 | **57.1** |
| 2025/26 | 19 | 16.7% | 39.8 | 6.4 | 0.2059 | 0.0808 | 1 | **50.0** |

### 3.11 ICC Men's T20 World Cup (T20 WC)

**Seasons:** 3 | **Avg CI:** 39.3 | **Range:** 34.2 - 43.6 (spread: 9.4)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2021/22 | 40 | 7.5% | 34.4 | 7.0 | 0.2808 | 0.1167 | 0 | **34.2** |
| 2022/23 | 39 | 18.4% | 36.9 | 5.9 | 0.2526 | 0.1034 | 0 | **43.6** |
| 2024 | 44 | 23.3% | 32.5 | 6.3 | 0.3815 | 0.2263 | 2 | **40.1** |

### 3.12 Syed Mushtaq Ali Trophy (SMAT)

**Seasons:** 9 | **Avg CI:** 36.1 | **Range:** 21.3 - 44.3 (spread: 23.0)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2015/16 | 83 | 12.0% | 39.1 | 5.6 | 0.3422 | 0.1226 | 0 | **35.3** |
| 2017/18 | 79 | 16.5% | 27.5 | 6.5 | 0.3387 | 0.0924 | 2 | **42.8** |
| 2018/19 | 130 | 12.7% | 58.4 | 6.7 | 0.3150 | 0.1454 | 0 | **30.9** |
| 2019/20 | 131 | 12.2% | 38.8 | 7.0 | 0.2896 | 0.1555 | 0 | **34.0** |
| 2020/21 | 92 | 15.2% | 48.7 | 6.8 | 0.3306 | 0.1441 | 2 | **35.5** |
| 2021/22 | 89 | 20.2% | 41.1 | 6.6 | 0.3586 | 0.1270 | 1 | **38.7** |
| 2022/23 | 44 | 27.3% | 28.6 | 5.6 | 0.3134 | 0.1845 | 0 | **44.3** |
| 2023/24 | 39 | 5.1% | 60.3 | 7.0 | 0.3212 | 0.2266 | 0 | **21.3** |
| 2024/25 | 8 | 12.5% | 21.0 | 6.0 | 0.2500 | 0.1214 | 0 | **41.8** |

### 3.13 CSA T20 Challenge (CSA T20)

**Seasons:** 7 | **Avg CI:** 54.1 | **Range:** 45.6 - 70.0 (spread: 24.4)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2016/17 | 27 | 26.9% | 21.9 | 6.8 | 0.2949 | 0.0699 | 0 | **50.0** |
| 2018/19 | 22 | 28.6% | 13.9 | 6.2 | 0.1905 | 0.0905 | 0 | **56.3** |
| 2020/21 | 16 | 25.0% | 20.0 | 5.4 | 0.3333 | 0.0505 | 0 | **50.5** |
| 2021/22 | 31 | 29.0% | 24.2 | 6.4 | 0.2500 | 0.0625 | 1 | **56.8** |
| 2022/23 | 28 | 20.0% | 25.1 | 5.8 | 0.3250 | 0.0665 | 0 | **45.6** |
| 2023/24 | 4 | 50.0% | 24.0 | N/A | 0.0000 | 0.2124 | 0 | **70.0** |
| 2024/25 | 26 | 23.1% | 33.0 | 5.5 | 0.2404 | 0.0709 | 0 | **49.7** |

### 3.14 Lanka Premier League (LPL)

**Seasons:** 5 | **Avg CI:** 51.9 | **Range:** 43.1 - 57.3 (spread: 14.2)

| Season | Matches | Close% | Avg Run Margin | Avg Wkt Margin | Gini | NRR CV | Ties | **CI** |
|--------|---------|--------|----------------|----------------|------|--------|------|--------|
| 2020/21 | 23 | 22.7% | 31.6 | 6.0 | 0.1905 | 0.0384 | 1 | **57.3** |
| 2021/22 | 24 | 13.0% | 38.6 | 5.8 | 0.2261 | 0.0698 | 0 | **43.1** |
| 2022/23 | 24 | 25.0% | 34.6 | 5.8 | 0.2833 | 0.0548 | 0 | **49.3** |
| 2023 | 24 | 20.8% | 35.1 | 7.0 | 0.2087 | 0.0384 | 1 | **53.1** |
| 2024 | 24 | 20.8% | 24.8 | 6.3 | 0.1565 | 0.0645 | 1 | **56.6** |

---

## 4. Cross-Tournament Comparison

### 4.1 Average CI Rankings

| Rank | Tournament | Seasons | All-Time Avg CI | Recent Avg CI (2022+) | CI Range |
|------|------------|---------|-----------------|----------------------|----------|
| 1 | CSA T20 | 7 | 54.1 | 55.1 | 24.4 |
| 2 | The Hundred | 5 | 53.4 | 53.9 | 20.3 |
| 3 | IPL | 18 | 52.1 | 52.6 | 19.1 |
| 4 | Vitality Blast | 7 | 52.0 | 50.8 | 8.0 |
| 5 | LPL | 5 | 51.9 | 53.0 | 14.2 |
| 6 | PSL | 11 | 50.2 | 49.3 | 28.2 |
| 7 | BBL | 15 | 49.7 | 48.7 | 16.9 |
| 8 | Super Smash | 9 | 49.5 | 52.7 | 25.0 |
| 9 | CPL | 13 | 47.9 | 46.5 | 22.2 |
| 10 | SA20 | 4 | 47.5 | 47.5 | 15.3 |
| 11 | MLC | 3 | 46.0 | 46.0 | 7.6 |
| 12 | ILT20 | 4 | 43.7 | 43.7 | 26.7 |
| 13 | T20 WC | 3 | 39.3 | 41.9 | 9.4 |
| 14 | SMAT | 9 | 36.1 | 35.8 | 23.0 |

### 4.2 Implications for Tournament Weighting

1. **Season-level CI reveals instability** that all-time aggregates mask. A tournament's
   CI can swing 15-25 points between seasons, meaning that a single aggregate CI
   number is a misleading summary statistic.

2. **The Hundred and CSA T20 Challenge** consistently show high CI scores. These are
   genuinely competitive tournaments where margins are tight and outcomes unpredictable.
   Their CI scores may partially offset their lower PQI scores in the composite.

3. **IPL's CI is moderate, not exceptional.** The IPL is the best T20 league in the world
   by player quality, but its competitiveness is average relative to smaller leagues.
   This is expected: more matches and larger squads create more lopsided results.
   This finding validates using CI as a *complement* to PQI, not a replacement.

4. **Recency decay must interact with season CI.** When we apply Factor 3 (Recency)
   to Factor 2 (CI), the effective competitiveness weight becomes:
   `Effective_CI = CI(season) * Decay(season)`. This means a highly competitive
   2024 PSL season gets full CI credit, while a competitive 2016 PSL season gets
   heavily discounted — which is the correct analytical behavior.

---

## 5. Recommendation

### Replace All-Time CI with Season-Level CI in the Composite

The Phase 1 composite used a single CI number per tournament (e.g., IPL CI = 32.8).
This should be replaced with a **recency-weighted season CI average**:

```
Effective_CI(tournament) = SUM(CI(season) * Decay(season)) / SUM(Decay(season))
```

This formula naturally emphasizes recent competitive conditions while still
incorporating historical context, weighted by the Founder-approved decay curve.

**Impact on tournament rankings:** Minimal at the top (IPL remains dominant via PQI),
but significant in the 1B/1C tier separation where CI is the swing factor.
Tournaments with improving competitiveness trends (e.g., SA20's growth) will see
their effective CI increase relative to the all-time aggregate.

---

*Cricket Playbook v4.0.0 | TKT-185 | Jose Mourinho, Quant Researcher*
