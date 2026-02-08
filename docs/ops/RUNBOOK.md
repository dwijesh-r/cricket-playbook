# Cricket Playbook Operational Runbook

**Ticket:** TKT-158
**EPIC:** EPIC-015 (Operational Maturity)
**Owner:** Tom Brady (Product Owner)
**Last Updated:** 2026-02-08

This is the operational runbook for the Cricket Playbook data pipeline, analytics engine, and output generation system. Keep it next to your coffee when you're on call.

---

## Table of Contents

1. [Data Pipeline Operations](#1-data-pipeline-operations)
2. [Output Generation](#2-output-generation)
3. [Model Operations](#3-model-operations)
4. [Dashboard Operations](#4-dashboard-operations)
5. [Common Troubleshooting](#5-common-troubleshooting)

---

## 1. Data Pipeline Operations

### 1.1 Full Data Ingestion

A full ingestion drops the existing DuckDB database, re-downloads all Cricsheet zip files, and rebuilds everything from scratch. Takes ~10-15 minutes depending on the number of leagues.

**When to use:** First setup, data corruption, or when you need a clean slate.

**Run locally:**

```bash
# From project root
python scripts/core/ingest.py
```

This will:
- Read all `.zip` files from `data/raw/`
- Parse every JSON match file inside them
- Build dimension tables (tournament, team, venue, player) and fact tables (ball, powerplay, player_match_performance)
- Derive player roles (Batter/Bowler/All-rounder) from match data
- Load everything into `data/cricket_playbook.duckdb` inside a single transaction
- Generate `data/manifests/manifest.json` (ingestion stats)
- Generate `data/processed/schema.md` (schema documentation)

**Run via GitHub Actions:**

Go to Actions > "Data Ingestion Pipeline" > Run workflow. Set `full_refresh` to `true` to download all T20 leagues, or leave it `false` for IPL-only.

The workflow downloads zips from Cricsheet, runs ingestion, and uploads the database as an artifact.

**What to check after:**

```bash
# Verify the database exists and has data
python scripts/core/backup_recovery.py verify
```

Look for:
- All 9 tables present (dim_tournament, dim_team, dim_venue, dim_player, dim_player_name_history, dim_match, fact_ball, fact_powerplay, fact_player_match_performance)
- No empty tables
- fact_ball should have 100k+ rows for IPL-only, 1M+ for full refresh

### 1.2 Incremental Ingestion

Incremental mode only processes new or changed match files by comparing SHA-256 checksums against `data/manifests/incremental_manifest.json`. Much faster if you only added a few new zip files.

**When to use:** New data dropped into `data/raw/`, and you don't want to re-process everything.

```bash
python scripts/core/ingest.py --incremental
```

This skips files whose checksums match the previous run. The incremental manifest at `data/manifests/incremental_manifest.json` tracks all known file checksums and saves checkpoints every 1000 matches.

**Heads up:** Incremental mode still creates a fresh database. It skips *parsing* unchanged files but rebuilds the DuckDB from scratch with all data. The time savings come from skipping JSON parsing, not from appending to the DB.

### 1.3 Validate Data After Ingestion (Great Expectations)

After any ingestion, run GE validation to catch data quality issues before they flow downstream into stat packs and models.

**Run all table validations:**

```bash
python scripts/core/ge_validation.py
```

**Validate a single table:**

```bash
python scripts/core/ge_validation.py --table fact_ball
```

**Point at a different database:**

```bash
python scripts/core/ge_validation.py --db path/to/other.duckdb
```

**Get JSON output (useful for CI):**

```bash
python scripts/core/ge_validation.py --json
```

**What it checks:**
- `fact_ball`: not-null match_id/innings, over range 0-19, ball range 0-20, batter_runs 0-7, extra_runs 0-15, total_runs 0-20, valid match_phase values, 100k+ row minimum
- `dim_player`: unique and not-null player_id, not-null current_name, matches_played >= 0, 1000+ row minimum
- `dim_match`: unique and not-null match_id, not-null match_date and venue_id, 500+ row minimum
- `dim_team`: unique and not-null team_id, not-null team_name, 10+ row minimum
- `dim_venue`: unique and not-null venue_id, not-null venue_name, 10+ row minimum

Exit code 0 = all pass, exit code 1 = failures detected.

### 1.4 Rollback a Bad Ingestion

If ingestion produced garbage data or failed mid-way, use the backup/recovery system.

**The ingest script auto-backs up:** Before overwriting, `ingest.py` copies the existing database to `data/cricket_playbook.duckdb.bak`. If the transaction fails, it auto-restores from this backup. If the transaction succeeds, it deletes the `.bak` file.

**Manual backup before risky operations:**

```bash
python scripts/core/backup_recovery.py backup --reason "pre-experiment"
```

Backups go to `data/backups/` with timestamped filenames like `cricket_playbook_20260208_143000.duckdb`. The system keeps the last 5 backups (configurable via `MAX_BACKUPS` in the script).

**List available backups:**

```bash
python scripts/core/backup_recovery.py list
```

**Restore from latest backup:**

```bash
python scripts/core/backup_recovery.py restore
```

**Restore from a specific timestamp:**

```bash
python scripts/core/backup_recovery.py restore --timestamp 2026-02-08T14:30:00
```

Before restoring, the script saves the current (bad) database as `cricket_playbook.duckdb.pre_restore` in case you need it for debugging. After restore, it verifies row counts match the backup.

**Verify database health anytime:**

```bash
python scripts/core/backup_recovery.py verify
```

---

## 2. Output Generation

### 2.1 Regenerate All Outputs at Once

The generate_outputs.py script runs stat packs, depth charts, predicted XIs, and 2023+ analytics in sequence.

```bash
python scripts/generators/generate_outputs.py
```

Skip the 2023+ analytics if you only need the main outputs:

```bash
python scripts/generators/generate_outputs.py --skip-2023
```

Each sub-generator has a 5-minute timeout. The script prints a summary showing which generators passed, failed, or timed out.

**Via GitHub Actions:** Actions > "Generate Outputs" > Run workflow. Set `regenerate_all` to `true` to force regeneration even if outputs look current. Set `skip_clustering` to `true` if you don't need fresh ML clusters.

### 2.2 Regenerate Stat Packs Only

Generates markdown stat packs for all 10 IPL 2026 teams.

```bash
python scripts/generators/generate_stat_packs.py
```

**Requires:**
- `data/cricket_playbook.duckdb` with analytics views already created (run `python scripts/core/analytics_ipl.py` first if views are missing)
- `outputs/player_tags.json` for player archetypes (optional but recommended)

**Output:** `stat_packs/` directory with one `{TEAM_CODE}_stat_pack.md` per team (e.g., `CSK_stat_pack.md`).

**Pre-execution hook:** The stat pack generator runs an ML health check before starting. If the health check returns CRITICAL, generation aborts. If DEGRADED, it logs a warning and continues.

### 2.3 Regenerate Depth Charts

Position-by-position depth charts for all 10 teams. Scores players against 9 positions (Opener, #3, Middle Order, Finisher, Wicketkeeper, Lead Pacer, Supporting Pacer, Lead Spinner, All-rounder).

```bash
python scripts/generators/generate_depth_charts.py
```

**Requires:**
- `data/ipl_2026_squads.csv`
- `data/ipl_2026_player_contracts.csv`
- `outputs/player_tags_2023.json`
- `outputs/matchups/batter_entry_points_2023.csv`
- `outputs/metrics/bowler_phase_performance.csv`

**Output:** `outputs/depth_charts/` directory with:
- `depth_charts_2026.json` (consolidated)
- `{team}_depth_chart.json` per team (e.g., `csk_depth_chart.json`)
- `README.md` with cross-team comparison table

### 2.4 Regenerate Predicted XIs

The SUPER SELECTOR v3.0 algorithm generates optimal XII (XI + Impact Player) for each team.

```bash
python scripts/generators/generate_predicted_xii.py
```

**Requires:** Same data files as depth charts plus `outputs/metrics/batter_consistency_index.csv` and `outputs/metrics/bowler_pressure_sequences.csv`.

**Output:** `outputs/predicted_xii/` directory with:
- `predicted_xii_2026.json` (consolidated)
- `{team}_predicted_xii.json` per team

---

## 3. Model Operations

### 3.1 Retrain the Clustering Model

The K-Means player clustering model (V2) classifies batters and bowlers into archetypes using career and phase-wise performance data.

```bash
python scripts/analysis/player_clustering_v2.py
```

**What it does:**
1. Extracts batter features (SR, average, boundary%, dot%, batting position, per-phase stats) with 2x recency weight for 2021-2025 data
2. Extracts bowler features (economy, SR, dots, per-phase stats, wickets per phase, phase distribution)
3. Removes features with correlation > 0.9
4. Runs PCA variance analysis (target: 50%)
5. Runs K-Means with 5 clusters each for batters and bowlers
6. Validates specific players (Dhoni, Buttler, Nortje, etc.) against expected classifications
7. Saves cluster explanations to `outputs/tags/cluster_explanations.json`

**Minimum data thresholds:** 300 balls faced for batters, 200 balls bowled for bowlers.

**Requires:** `data/cricket_playbook.duckdb` with analytics views (`analytics_ipl_batting_career`, `analytics_ipl_batter_phase`, `analytics_ipl_bowling_career`, `analytics_ipl_bowler_phase`, etc.)

**Via GitHub Actions:** The generate-outputs workflow includes an optional clustering step. Trigger it manually with `skip_clustering` set to `false`.

### 3.2 Check Model Health

The system health score evaluates the overall project across 6 categories: Governance (15%), Code Quality (20%), Data Robustness (20%), ML Rigor (20%), Testing (15%), Documentation (10%).

```bash
# Human-readable report
python scripts/ml_ops/system_health_score.py

# JSON output
python scripts/ml_ops/system_health_score.py --json
```

Target score is 85/100. Baseline was 67.4 when the health check was introduced.

The ML health check workflow also runs:

```bash
python scripts/ml_ops/run_health_check.py --verbose --export
```

Flags:
- `--verbose`: detailed output
- `--export`: save metrics to `outputs/monitoring/`
- `--json`: JSON output for CI parsing

**Via GitHub Actions:** Actions > "ML Health Check" > Run workflow. Also runs automatically on push to `scripts/ml_ops/**` or `scripts/analysis/player_clustering*.py`, and weekly on Monday 9 AM UTC.

Exit codes: 0 = healthy, 1 = degraded (warning, build passes), 2 = critical (build fails).

### 3.3 Rollback a Bad Model Version

There's no formal model registry with automated rollback yet. Here's the manual process:

1. **Check git history for the last known good clustering output:**

```bash
git log --oneline -- outputs/tags/player_tags.json
git log --oneline -- outputs/tags/cluster_explanations.json
```

2. **Restore from a specific commit:**

```bash
git checkout <commit-sha> -- outputs/tags/player_tags.json
git checkout <commit-sha> -- outputs/tags/cluster_explanations.json
```

3. **Re-run downstream generators** (stat packs and depth charts consume player tags):

```bash
python scripts/generators/generate_outputs.py --skip-2023
```

4. **Verify the restored model health:**

```bash
python scripts/ml_ops/run_health_check.py --verbose
```

---

## 4. Dashboard Operations

### 4.1 Deploy Dashboards to GitHub Pages

Dashboards are static HTML served via GitHub Pages. The deploy-dashboard workflow handles this automatically after output generation.

**Automatic deployment:** Whenever the "Generate Outputs" workflow completes successfully, the deploy-dashboard workflow:
1. Runs `python scripts/the_lab/update_the_lab.py` to update data files
2. Commits updated `.js` data files in `scripts/the_lab/dashboard/data/`
3. Pushes to main, which triggers GitHub Pages rebuild

**Manual deployment:**

```bash
# Update dashboard data files locally
python scripts/the_lab/update_the_lab.py

# Commit and push to trigger GitHub Pages
git add scripts/the_lab/dashboard/data/
git commit -m "chore(dashboard): update dashboard data"
git push origin main
```

**Via GitHub Actions:** Actions > "Deploy Dashboard" > Run workflow. Set `force_update` to `true` to update even if no data changed.

**Dashboard URL:** `https://dwijesh-r.github.io/cricket-playbook/scripts/the_lab/dashboard/`

### 4.2 Test Dashboard Changes Locally

The dashboards are plain HTML + JavaScript files. Open them directly in a browser:

```bash
# Open The Lab dashboard
open scripts/the_lab/dashboard/index.html

# Or use Python's built-in HTTP server for proper asset loading
cd scripts/the_lab/dashboard
python -m http.server 8000
# Then visit http://localhost:8000
```

Data files live in `scripts/the_lab/dashboard/data/` as `.js` files (teams.js, predicted_xii.js, depth_charts.js, player_tags.js). These get committed to the repo and served directly by GitHub Pages.

The Mission Control dashboard follows the same pattern under `scripts/mission_control/dashboard/`. The system health score script writes to `scripts/mission_control/dashboard/data/health_score.json`.

---

## 5. Common Troubleshooting

### 5.1 DuckDB Locked / Corrupt

**Symptoms:** `IOError: Could not open database`, `duckdb.IOException`, or queries returning nonsense.

**Fix 1 - Kill stale connections:**

Check if another Python process has the database open:

```bash
# macOS
lsof | grep cricket_playbook.duckdb

# Kill the offending process
kill -9 <PID>
```

**Fix 2 - Delete WAL/lock files:**

DuckDB creates `.wal` files during writes. If a process crashed mid-write, stale WAL files can cause lock issues.

```bash
rm -f data/cricket_playbook.duckdb.wal
```

**Fix 3 - Restore from backup:**

If the database is actually corrupt (queries crash or return wrong data):

```bash
# Check what backups exist
python scripts/core/backup_recovery.py list

# Restore the latest good backup
python scripts/core/backup_recovery.py restore

# Verify the restored database
python scripts/core/backup_recovery.py verify
```

**Fix 4 - Full re-ingestion:**

Nuclear option. Back up first, then re-ingest from raw data:

```bash
python scripts/core/backup_recovery.py backup --reason "pre-reingest"
python scripts/core/ingest.py
python scripts/core/ge_validation.py
```

### 5.2 GE Validation Failures

**Symptom:** `ge_validation.py` exits with code 1 and reports FAIL for one or more tables.

**Step 1 - Read the failure details:**

```bash
python scripts/core/ge_validation.py
```

Look at the FAIL lines. They tell you which expectation failed and on which column. Common causes:

- **Row count below minimum:** The database doesn't have enough data. Did ingestion complete? Check `data/manifests/manifest.json` for error counts.
- **Values out of range (e.g., batter_runs > 7):** Bad source data from Cricsheet, or a parsing bug in `ingest.py`. Check the `source_file` column of the offending rows.
- **Null values where not expected:** Dimension join failure during ingestion. Check that the registry mapping in the JSON source files is complete.

**Step 2 - Validate a single table to isolate:**

```bash
python scripts/core/ge_validation.py --table fact_ball --json
```

**Step 3 - Check the raw data:**

```bash
python3 -c "
import duckdb
conn = duckdb.connect('data/cricket_playbook.duckdb', read_only=True)
# Example: find rows with batter_runs > 7
print(conn.execute('SELECT * FROM fact_ball WHERE batter_runs > 7 LIMIT 10').fetchdf())
conn.close()
"
```

### 5.3 Pre-commit Hook Failures

**Symptom:** `git commit` gets rejected with ruff errors or other hook failures.

**Ruff linter errors:**

```bash
# See what ruff is complaining about
ruff check .

# Auto-fix what it can
ruff check --fix .
```

**Ruff formatter errors:**

```bash
# See diffs
ruff format --diff .

# Auto-format
ruff format .
```

**Trailing whitespace / end-of-file-fixer:**

These fix themselves. Just re-stage the modified files:

```bash
git add -u
git commit -m "your message"
```

**check-yaml failures:**

You have a malformed YAML file. The error message points to the file and line. Fix the YAML syntax.

**check-added-large-files (>500KB):**

You're trying to commit a file larger than 500KB. This is intentional to prevent accidentally committing the DuckDB file or large CSVs. If you really need to commit a large file, add it to `.gitignore` or adjust the threshold in `.pre-commit-config.yaml`.

**Naming convention hook warnings:**

The `check-naming-convention` hook is warning-only (does not block commits). It checks that documents in `reviews/` and `docs/sprints/` follow the `documentname_MMDDYY_v*.md` naming pattern.

**Bypass hooks in emergencies (use sparingly):**

```bash
git commit --no-verify -m "hotfix: description"
```

### 5.4 CI/CD Pipeline Failures

**Which workflow failed?** Check the GitHub Actions tab. Here's what each one does and common failure causes:

**CI (ci.yml):**
- Runs on push/PR to main
- Steps: ruff lint, ruff format check, mypy type check (non-blocking), pytest with coverage
- Common failures: lint errors (run `ruff check --fix .` locally), test failures (run `pytest tests/ -v --tb=short` locally)

**Quality Gates (gate-check.yml):**
- Runs on push/PR to main
- 5 gates: lint, tests, threshold config validation, schema validation, domain constraints
- Gate 1 (lint) and Gate 3 (thresholds) are blocking. Gate 2 (tests) is warning-only.
- If Gate 3 fails: check that `config/thresholds.yaml` exists and is valid YAML, then check `scripts/utils/threshold_loader.py`

**Generate Outputs (generate-outputs.yml):**
- Triggers after Quality Gates pass, on a daily schedule (2 AM UTC), or manually
- Requires the database file to exist (skip gracefully if missing)
- Runs analytics views, then clustering, then stat packs / depth charts / predicted XIs
- If it fails on "Create Analytics Views": the database is missing or corrupt
- If it fails on "Generate stat packs": check that analytics views exist by running `python scripts/core/analytics_ipl.py` locally

**Data Ingestion (ingest.yml):**
- Weekly (Sunday 3 AM UTC) or manual
- Downloads from Cricsheet then runs ingestion
- If download fails: Cricsheet might be down. Check https://cricsheet.org manually.
- If ingestion fails: check the manifest at `data/manifests/manifest.json` for error details

**Deploy Dashboard (deploy-dashboard.yml):**
- Triggers after Generate Outputs completes, or manually
- If commit/push fails: likely a permission issue with GITHUB_TOKEN
- If verification fails (HTTP status != 200): GitHub Pages might need a few minutes to rebuild. Check the Pages settings in repo Settings > Pages.

**ML Health Check (ml-health-check.yml):**
- Weekly (Monday 9 AM), on push to ML files, or manually
- Exit code 2 (critical) fails the build; exit code 1 (degraded) is a warning
- If it fails: run `python scripts/ml_ops/run_health_check.py --verbose` locally to see what's degraded

---

## Quick Reference

| What you want to do | Command |
|---|---|
| Full ingestion | `python scripts/core/ingest.py` |
| Incremental ingestion | `python scripts/core/ingest.py --incremental` |
| Validate data | `python scripts/core/ge_validation.py` |
| Create backup | `python scripts/core/backup_recovery.py backup` |
| Restore latest backup | `python scripts/core/backup_recovery.py restore` |
| List backups | `python scripts/core/backup_recovery.py list` |
| Verify database health | `python scripts/core/backup_recovery.py verify` |
| Generate all outputs | `python scripts/generators/generate_outputs.py` |
| Generate stat packs only | `python scripts/generators/generate_stat_packs.py` |
| Generate depth charts only | `python scripts/generators/generate_depth_charts.py` |
| Generate predicted XIs only | `python scripts/generators/generate_predicted_xii.py` |
| Retrain clustering model | `python scripts/analysis/player_clustering_v2.py` |
| System health score | `python scripts/ml_ops/system_health_score.py` |
| ML health check | `python scripts/ml_ops/run_health_check.py --verbose` |
| Lint check | `ruff check .` |
| Auto-fix lint | `ruff check --fix .` |
| Format check | `ruff format --check .` |
| Auto-format | `ruff format .` |
| Run tests | `pytest tests/ -v --tb=short` |

---

*This runbook was written for the Cricket Playbook project (TKT-158, EPIC-015). If something in here is wrong or outdated, fix it and commit. Runbooks that lie are worse than no runbook at all.*
