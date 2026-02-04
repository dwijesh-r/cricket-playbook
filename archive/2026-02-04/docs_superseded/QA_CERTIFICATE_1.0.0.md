# QA Certificate - Data Version 1.0.0

**Auditor:** N'Golo Kanté (Stats Integrity / QA Gate)
**Audit Date:** 2026-01-19
**Result:** ⚠️ WARN (APPROVED TO PROCEED)

---

## Integrity Checks

| Check | Status | Details |
|-------|--------|---------|
| Duplicate ball_id | ✅ PASS | No duplicates |
| Referential integrity (batter → player) | ✅ PASS | All valid |
| Referential integrity (match_id → match) | ✅ PASS | All valid |
| Balls per innings sanity | ✅ PASS | All within bounds |
| Match dates sanity | ✅ PASS | All 2000-2030 |
| Batter runs sanity | ⚠️ WARN | 3 balls with 7 runs |
| Team consistency | ✅ PASS | All valid |
| Wicket data consistency | ✅ PASS | All types present |

---

## Warning Investigation

**3 balls with batter_runs = 7:**

These are legitimate all-run sevens (extremely rare cricket events):

| Match | Innings | Over.Ball | Batter | Runs |
|-------|---------|-----------|--------|------|
| 1068357 | 1 | 2.3 | SM Davies | 7 |
| 533272 | 2 | 17.2 | BV Vitori | 7 |
| 894293 | 1 | 14.2 | GH Worker | 7 |

**Verdict:** Valid data, not errors.

---

## Reconciliation Totals

| Metric | Value |
|--------|-------|
| Matches | 9,357 |
| Balls | 2,137,915 |
| Players | 7,864 |
| Teams | 285 |
| Venues | 531 |
| Total Runs | 2,737,639 |
| Total Wickets | 116,636 |

---

## Approval

**Status:** ✅ APPROVED FOR ACTIVATION

Data integrity verified. Minor warning does not impact data quality.

---

*Signed: N'Golo Kanté, Stats Integrity Gate*
