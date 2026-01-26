# Batter Entry Point Audit Report

**Author:** Stephen Curry (Analytics Lead)
**Date:** 2026-01-26
**Data Scope:** IPL 2023+ (minimum 5 innings)

---

## Executive Summary

Comprehensive audit of ALL batters' entry point classifications based on IPL 2023+ data. Entry point is measured as `ball_seq` (ball number in innings when batter arrives at the crease).

**Total batters analyzed:** 158

---

## Entry Point Thresholds (Revised)

Based on EDA percentile analysis:

| Position | Ball Range | Over Range | Rationale |
|----------|------------|------------|-----------|
| **TOP_ORDER** | 1-30 balls | Overs 1-5 | P25 = 21.7 balls |
| **MIDDLE_ORDER** | 30-72 balls | Overs 5-12 | P50 = 67.8 balls |
| **LOWER_ORDER** | 72+ balls | Overs 12+ | P75 = 95.6 balls |

### Percentile Distribution
- P10: 4.1 balls
- P25: 21.7 balls
- P50: 67.8 balls
- P75: 95.6 balls
- P90: 111.4 balls

---

## Key Player Validation

| Player | Avg Entry (balls) | Classification | Correct? |
|--------|-------------------|----------------|----------|
| **SV Samson** | 25.8 | TOP_ORDER | ✅ YES |
| DA Warner | 2.7 | TOP_ORDER | ✅ YES |
| RG Sharma | 3.3 | TOP_ORDER | ✅ YES |
| V Kohli | 2.6 | TOP_ORDER | ✅ YES |
| Shubman Gill | 4.2 | TOP_ORDER | ✅ YES |
| HH Pandya | 66.4 | MIDDLE_ORDER | ✅ YES |
| KD Karthik | 91.0 | LOWER_ORDER | ✅ YES |
| MS Dhoni | 105.6 | LOWER_ORDER | ✅ YES |
| AD Russell | 84.6 | LOWER_ORDER | ✅ YES |
| SO Hetmyer | 85.8 | LOWER_ORDER | ✅ YES |

**Sanju Samson Status:** ✅ CORRECTLY CLASSIFIED as TOP_ORDER (avg 25.8 balls)

---

## Top Order Players (Entry < 30 balls)

| Player | Innings | Avg Entry | Median Entry |
|--------|---------|-----------|--------------|
| Priyansh Arya | 18 | 1.0 | 1.0 |
| WP Saha | 26 | 1.0 | 1.0 |
| YBK Jaiswal | 43 | 1.0 | 1.0 |
| Q de Kock | 23 | 1.9 | 1.0 |
| V Kohli | 44 | 2.6 | 1.0 |
| DA Warner | 22 | 2.7 | 1.0 |
| RG Sharma | 45 | 3.3 | 2.0 |
| Shubman Gill | 44 | 4.2 | 4.0 |
| F du Plessis | 38 | 4.1 | 3.5 |
| SV Samson | 38 | 25.8 | 21.5 |

---

## Middle Order Players (Entry 30-72 balls)

| Player | Innings | Avg Entry | Median Entry |
|--------|---------|-----------|--------------|
| D Padikkal | 28 | 31.5 | 25.5 |
| VR Iyer | 34 | 37.9 | 27.5 |
| SS Iyer | 31 | 40.0 | 32.0 |
| SA Yadav | 43 | 40.7 | 39.0 |
| RM Patidar | 27 | 45.1 | 42.0 |
| R Parag | 35 | 48.9 | 46.0 |
| RR Pant | 26 | 50.0 | 49.0 |
| HH Pandya | 40 | 66.4 | 64.0 |

---

## Lower Order Players (Entry 72+ balls)

| Player | Innings | Avg Entry | Median Entry |
|--------|---------|-----------|--------------|
| RK Singh | 36 | 72.2 | 73.5 |
| DA Miller | 32 | 76.2 | 78.5 |
| RA Jadeja | 37 | 75.5 | 83.0 |
| Dhruv Jurel | 35 | 80.5 | 84.0 |
| AD Russell | 33 | 84.6 | 83.0 |
| SO Hetmyer | 35 | 85.8 | 90.0 |
| KD Karthik | 26 | 91.0 | 92.5 |
| MS Dhoni | 36 | 105.6 | 108.0 |

---

## Audit Conclusion

**No systematic misclassifications found.**

The entry point logic correctly classifies batters based on 2023+ IPL data:
- All known openers are TOP_ORDER
- All known finishers are LOWER_ORDER
- Sanju Samson IS correctly classified as TOP_ORDER (avg 25.8 balls)

### Original Issue Resolution
The reported issue that "Sanju Samson classified as middle order when he bats 1-3" appears to have been resolved or was based on older data. Current 2023+ analysis shows Samson correctly as TOP_ORDER.

---

*Stephen Curry - Analytics Lead*
