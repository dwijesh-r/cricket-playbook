# Analysis

Exploratory data analysis reports and audits.

---

## Contents

| File | Description |
|------|-------------|
| `entry_point_audit_report.md` | Batter entry point classification audit (197 batters) |
| `threshold_eda_2023.md` | EDA-backed threshold analysis for player tags |
| `player_id_audit_report.md` | Player ID mismatch audit (15 issues documented) |

---

## Entry Point Audit

Classifies batters by average entry position:
- **TOP_ORDER**: Entry ball < 30
- **MIDDLE_ORDER**: Entry ball 30-72
- **LOWER_ORDER**: Entry ball > 72

---

## Threshold EDA

Percentile-based analysis for tag thresholds:
- Specialist tags: SR ≥ 130, Avg ≥ 25, BPD ≥ 20
- Vulnerable tags: SR < 105 OR Avg < 15 OR BPD < 15

---

## Player ID Audit

Documents 15 player ID mismatches in ETL:
- 6 critical (wrong stats entirely)
- Root cause: Surname collisions (Singh, Sharma, Kumar, Khan)

---

*Cricket Playbook v3.1.0*
