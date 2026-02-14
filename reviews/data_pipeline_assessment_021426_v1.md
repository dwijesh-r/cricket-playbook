# Data Pipeline Assessment & Weekly Refresh Runbook

**TKT-229 | Owner: Brock Purdy (Data Pipeline)**
**Date: 2026-02-14 | Version: 1.0**

---

## 1. Current Data State

### 1.1 Database Overview

| Metric | Value |
|--------|-------|
| **Database file** | `data/cricket_playbook.duckdb` |
| **File size** | 154.0 MB |
| **Base tables** | 16 |
| **Analytics views** | 163 |
| **Total deliveries** | 2,137,915 |
| **Total matches** | 9,357 |
| **Unique players** | 7,864 |
| **Unique teams** | 285 |
| **Unique venues** | 531 |
| **Tournaments tracked** | 426 |
| **Data version** | 1.1.0 (manifest) / 1.2.0 (ingest script) |
| **Last ingestion** | 2026-01-19T12:46:12 |

### 1.2 Date Range

| Scope | Earliest | Latest |
|-------|----------|--------|
| **All data** | 2005-02-17 | 2026-01-15 |
| **IPL only** | 2008-04-18 | 2025-06-03 |

### 1.3 IPL Season Coverage (Complete)

| Season | Start | End | Matches |
|--------|-------|-----|---------|
| 2007/08 | 2008-04-18 | 2008-06-01 | 58 |
| 2009 | 2009-04-18 | 2009-05-24 | 57 |
| 2009/10 | 2010-03-12 | 2010-04-25 | 60 |
| 2011 | 2011-04-08 | 2011-05-28 | 73 |
| 2012 | 2012-04-04 | 2012-05-27 | 74 |
| 2013 | 2013-04-03 | 2013-05-26 | 76 |
| 2014 | 2014-04-16 | 2014-06-01 | 60 |
| 2015 | 2015-04-08 | 2015-05-24 | 59 |
| 2016 | 2016-04-09 | 2016-05-29 | 60 |
| 2017 | 2017-04-05 | 2017-05-21 | 59 |
| 2018 | 2018-04-07 | 2018-05-27 | 60 |
| 2019 | 2019-03-23 | 2019-05-12 | 60 |
| 2020/21 | 2020-09-19 | 2020-11-10 | 60 |
| 2021 | 2021-04-09 | 2021-10-15 | 60 |
| 2022 | 2022-03-26 | 2022-05-29 | 74 |
| 2023 | 2023-03-31 | 2023-05-29 | 74 |
| 2024 | 2024-03-22 | 2024-05-26 | 71 |
| 2025 | 2025-03-22 | 2025-06-03 | 74 |
| **Total** | | | **1,169** |

**IPL 2025 data is COMPLETE** (final: RCB vs PBKS on 2025-06-03).

### 1.4 Cross-Tournament Freshness (Top 10 by Recency)

| Tournament | Latest Data | Matches |
|------------|-------------|---------|
| Super Smash | 2026-01-15 | 256 |
| SA20 | 2026-01-15 | 121 |
| Big Bash League | 2026-01-15 | 654 |
| Pakistan tour of Sri Lanka | 2026-01-11 | 2 |
| International League T20 | 2026-01-04 | 134 |
| Cambodia tour of Indonesia | 2025-12-29 | 23 |
| South Africa tour of India | 2025-12-19 | 14 |
| West Africa Trophy | 2025-12-14 | 39 |
| Nepal Premier League | 2025-12-13 | 64 |
| Ireland tour of Bangladesh | 2025-12-02 | 6 |

### 1.5 IPL 2026 Squad Coverage

| Team | Squad Size |
|------|-----------|
| Chennai Super Kings | 25 |
| Delhi Capitals | 25 |
| Gujarat Titans | 20 |
| Kolkata Knight Riders | 24 |
| Lucknow Super Giants | 20 |
| Mumbai Indians | 24 |
| Punjab Kings | 22 |
| Rajasthan Royals | 25 |
| Royal Challengers Bengaluru | 21 |
| Sunrisers Hyderabad | 25 |
| **Total** | **231** |

### 1.6 Data Gaps Identified

1. **Staleness gap (30 days):** Data was last ingested on 2026-01-19, now 26 days stale. BBL/SA20/Super Smash seasons have advanced beyond Jan 15.
2. **IPL 2026 pre-season data:** No IPL 2026 matches exist yet (season starts ~Mar 2026). This is expected.
3. **Legacy database:** `data/ipl_ball_by_ball.duckdb` (12 KB) is empty -- appears to be a leftover from an earlier pipeline version. Safe to ignore or remove.
4. **Ingestion errors:** 20 match files had parsing errors (error code 3) in the last run. These are edge-case JSON structure issues in older matches. Non-blocking.
5. **Manifest version mismatch:** manifest.json reports data_version `1.1.0`, but the ingest script defines `1.2.0` (incremental ingestion added). The manifest was written during the initial full ingest before the version bump.

---

## 2. Pipeline Architecture

### 2.1 Architecture Diagram

```
+------------------+     +-------------------+     +---------------------------+
|   Cricsheet.org  |     |   data/raw/*.zip  |     |  data/cricket_playbook    |
|   (T20 JSON      | --> |   18 ZIP files    | --> |     .duckdb (154 MB)      |
|    archives)      |     |   ~29 MB total    |     |   16 tables, 163 views   |
+------------------+     +-------------------+     +---------------------------+
        |                         |                           |
   Manual/Weekly            ingest.py                  analytics_ipl.py
   Download (curl)     (scripts/core/)              (scripts/core/)
                                                          |
                       +----------------------------------+----------------------------------+
                       |                    |                    |                    |
               +--------------+    +----------------+   +----------------+   +--------------+
               | Clustering   |    | Stat Packs     |   | Depth Charts   |   | Predicted    |
               | (analysis/   |    | (generators/   |   | (generators/   |   |  XIIs        |
               | player_      |    | generate_stat  |   | generate_depth |   | (generators/ |
               | clustering   |    | _packs.py)     |   | _charts.py)    |   | generate_    |
               | _v2.py)      |    |                |   |                |   | predicted_   |
               +--------------+    +----------------+   +----------------+   | xii.py)      |
                       |                    |                    |            +--------------+
                       v                    v                    v                    |
               outputs/tags/        stat_packs/          outputs/                    v
               player_tags.json     {TEAM}/              depth_charts/         outputs/
               clustering_*.csv     *_stat_pack.md       *_depth_chart.*       predicted_xii/
                                                                               *_predicted_xii.json
                       |                    |                    |                    |
                       +---+----------------+--------------------+--------------------+
                           |
                    +------v------+        +--------------------+       +-----------------+
                    | update_     |        | generate_venue_    |       | generate_       |
                    | the_lab.py  |        | and_trends_data.py |       | pressure/       |
                    | (the_lab/)  |        | (the_lab/)         |       | momentum_data.py|
                    +------+------+        +--------+-----------+       +--------+--------+
                           |                        |                            |
                           v                        v                            v
                    dashboard/data/           dashboard/data/              dashboard/data/
                    teams.js                  venue_data.js                pressure_metrics.js
                    predicted_xii.js          historic_trends.js          momentum_insights.js
                    depth_charts.js
                    players.js
                           |
                           v
                    +-------------------+
                    | GitHub Pages      |
                    | (The Lab          |
                    |  Dashboard)       |
                    +-------------------+
```

### 2.2 Data Flow Summary

```
Cricsheet ZIPs --> ingest.py --> DuckDB (16 base tables)
                                    |
                              analytics_ipl.py --> 163 analytical views
                                    |
                              player_clustering_v2.py --> cluster tables + tags
                                    |
                    +---------------+---------------+
                    |               |               |
              generate_stat    generate_depth   generate_predicted
              _packs.py        _charts.py       _xii.py
                    |               |               |
                    v               v               v
              stat_packs/      outputs/         outputs/
              Markdown files   depth_charts/    predicted_xii/
                    |               |               |
                    +-------+-------+-------+-------+
                            |
                     update_the_lab.py + Lab data generators
                            |
                     Dashboard JS data files
                            |
                     GitHub Pages deploy
```

---

## 3. Script Inventory

### 3.1 Core Pipeline Scripts

| Script | Location | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| **ingest.py** | `scripts/core/` | Ingest Cricsheet ZIP files into DuckDB | `data/raw/*.zip` | `data/cricket_playbook.duckdb` + manifest + schema doc |
| **analytics_ipl.py** | `scripts/core/` | Create 163 analytical views in DuckDB | DuckDB base tables + CSVs (`ipl_2026_squads.csv`, `ipl_2026_player_contracts.csv`) | 163 SQL views in DuckDB |
| **validate_schema.py** | `scripts/core/` | Validate database schema integrity | DuckDB | Pass/fail validation |
| **domain_constraints.py** | `scripts/core/` | Domain-level data validation (cricket rules) | DuckDB | Pass/fail checks |
| **ge_validation.py** | `scripts/core/` | Great Expectations data quality checks | DuckDB | Validation report |
| **data_lineage.py** | `scripts/core/` | Track data lineage through pipeline | DuckDB + manifests | Lineage graph |
| **backup_recovery.py** | `scripts/core/` | Database backup & restore utility | DuckDB | Backup files |
| **schema_constraints.py** | `scripts/core/` | Schema constraint enforcement | DuckDB | Constraint report |

### 3.2 Generator Scripts

| Script | Location | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| **generate_stat_packs.py** | `scripts/generators/` | Team stat packs (10 teams) | DuckDB views | `stat_packs/{TEAM}/{TEAM}_stat_pack.md` |
| **generate_depth_charts.py** | `scripts/generators/` | Position-by-position depth charts | DuckDB views + squads CSV | `outputs/depth_charts/*.json`, `*.md`, `*.html` |
| **generate_predicted_xii.py** | `scripts/generators/` | Optimal XI + Impact Player per team | DuckDB views + squads CSV | `outputs/predicted_xii/*.json` |
| **generate_all_2023_outputs.py** | `scripts/generators/` | 2023+ filtered matchup/tag/clustering outputs | DuckDB views | `outputs/*.csv`, `outputs/tags/*.json` |
| **generate_player_profiles.py** | `scripts/generators/` | Pre-computed JSON profiles for 231 players | DuckDB views + CSVs + tags | `outputs/player_profiles/by_team/*.json` |
| **generate_outputs.py** | `scripts/generators/` | Entry point: runs all generators in sequence | N/A | Calls other generators |
| **generate_2023_outputs.py** | `scripts/generators/` | Subset of 2023+ output generation | DuckDB views | Filtered outputs |
| **sprint_3_p1_features.py** | `scripts/generators/` | Sprint 3 Phase 1 feature outputs | DuckDB views | Sprint-specific outputs |
| **parse_founder_review.py** | `scripts/generators/` | Parse founder review documents | Review documents | Parsed review data |

### 3.3 Analysis Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| **player_clustering_v2.py** | `scripts/analysis/` | K-means clustering of batters and bowlers |
| **batter_bowling_type_matchup.py** | `scripts/analysis/` | Batter vs bowling type matchup analysis |
| **bowler_handedness_matchup.py** | `scripts/analysis/` | Bowler vs batter handedness matchup analysis |
| **bowler_phase_tags.py** | `scripts/analysis/` | Bowler phase role tagging (PP/Middle/Death) |
| **entry_point_analysis.py** | `scripts/analysis/` | Batter entry point analysis |
| **confidence_intervals.py** | `scripts/analysis/` | Statistical confidence intervals for metrics |
| **cross_tournament_enrichment.py** | `scripts/analysis/` | Cross-tournament player profile enrichment |
| **insight_confidence.py** | `scripts/analysis/` | Insight reliability scoring |
| **toss_advantage_index.py** | `scripts/analysis/` | Toss advantage index computation |

### 3.4 The Lab Dashboard Scripts

| Script | Location | Purpose | Output |
|--------|----------|---------|--------|
| **update_the_lab.py** | `scripts/the_lab/` | Refresh dashboard JS data files from JSON outputs | `dashboard/data/{teams,predicted_xii,depth_charts,players}.js` |
| **generate_venue_and_trends_data.py** | `scripts/the_lab/` | Venue profiles + historic trend data | `dashboard/data/venue_data.js`, `historic_trends.js` |
| **generate_momentum_data.py** | `scripts/the_lab/` | Momentum/pressure sequence insights | `dashboard/data/momentum_insights.js` |
| **generate_pressure_data.py** | `scripts/the_lab/` | Pressure performance metrics | `dashboard/data/pressure_metrics.js` |
| **generate_sql_lab_data.py** | `scripts/the_lab/` | Parquet export + view DDL for browser SQL Lab | Parquet files + `views.sql` + `table_metadata.json` |

### 3.5 Validation & QA Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| **validate_all_views.py** | `scripts/` | Validate all 163 analytics views execute correctly |
| **system_health_score.py** | `scripts/ml_ops/` | Compute system health score across 6 categories |

---

## 4. Database Schema

### 4.1 Base Tables (16)

| Table | Rows | Description |
|-------|------|-------------|
| **dim_match** | 9,357 | One row per match (date, venue, teams, outcome) |
| **dim_player** | 7,864 | Player dimension (ID, name, role, keeper flag) |
| **dim_player_name_history** | 7,888 | Player name changes over time |
| **dim_team** | 285 | Team dimension (name, short code) |
| **dim_tournament** | 426 | Tournament dimension (name, country, format) |
| **dim_tournament_weights** | 14 | Tournament weighting factors for composite scores |
| **dim_venue** | 531 | Venue dimension (name, city) |
| **dim_bowler_classification** | 430 | Bowler type classification data |
| **dim_franchise_alias** | 19 | Franchise name aliases (e.g., RCB name changes) |
| **fact_ball** | 2,137,915 | Ball-by-ball delivery data (core fact table) |
| **fact_player_match_performance** | 195,510 | Player-level match participation (bat/bowl/keep) |
| **fact_powerplay** | 19,167 | Powerplay overs metadata |
| **ipl_2026_squads** | 231 | IPL 2026 squad members with roles and classifications |
| **ipl_2026_contracts** | 231 | IPL 2026 player contract details |
| **player_clusters_batters** | 87 | Batter clustering results (K-means) |
| **player_clusters_bowlers** | 152 | Bowler clustering results (K-means) |

### 4.2 Analytics Views (163)

Views are organized into families:

- **Career aggregates:** `analytics_ipl_batting_career_*`, `analytics_ipl_bowling_career_*`
- **Phase breakdowns:** `analytics_ipl_batter_phase_*`, `analytics_ipl_bowler_phase_*`
- **Matchup views:** `analytics_ipl_batter_vs_bowler_*`, `analytics_ipl_batter_vs_bowler_type_*`, `analytics_ipl_batter_vs_team_*`
- **Venue analysis:** `analytics_ipl_batter_venue_*`, `analytics_ipl_bowler_venue_*`, `analytics_ipl_venue_profile_*`
- **Pressure metrics:** `analytics_ipl_pressure_*`, `analytics_ipl_dot_ball_pressure_*`
- **Squad integration:** `analytics_ipl_squad_batting_*`, `analytics_ipl_squad_bowling_*`, `analytics_ipl_team_roster_*`
- **Benchmarks:** `analytics_ipl_batting_benchmarks_*`, `analytics_ipl_bowling_benchmarks_*`, `analytics_ipl_career_benchmarks_*`
- **Percentiles:** `analytics_ipl_batting_percentiles_*`, `analytics_ipl_bowling_percentiles_*`
- **Time windows:** Views with `_alltime` (full IPL history) and `_since2023` (IPL 2023+) suffixes
- **Cross-tournament:** `analytics_t20_*` views for all T20 data comparison
- **Composite scores:** `analytics_weighted_composite_batting`, `analytics_weighted_composite_bowling`

---

## 5. CI/CD Automation

### 5.1 Workflow Inventory

| Workflow | File | Trigger | Schedule | Owner |
|----------|------|---------|----------|-------|
| **CI** | `ci.yml` | Push/PR to main | - | Brad Stevens |
| **Quality Gates** | `gate-check.yml` | Push/PR to main | - | Brad Stevens |
| **Data Ingestion** | `ingest.yml` | Weekly + manual | Sun 3 AM UTC | Brock Purdy |
| **Generate Outputs** | `generate-outputs.yml` | Post gate-check + daily + manual | Daily 2 AM UTC | Brad Stevens |
| **Deploy Dashboard** | `deploy-dashboard.yml` | Post generate-outputs + push + manual | - | Brad Stevens |
| **ML Health Check** | `ml-health-check.yml` | Weekly + push to ML files + manual | Mon 9 AM UTC | Ime Udoka |
| **Notify on Push** | `notify-on-push.yml` | Push to main | - | - |

### 5.2 Automation Chain

```
Weekly (Sun 3AM):                       Daily (2AM):
  ingest.yml                              generate-outputs.yml
    |                                       |
    v                                       v
  Download Cricsheet ZIPs            1. check-staleness
  Run ingest.py                      2. analytics_ipl.py (create views)
  Upload DB artifact                 3. player_clustering_v2.py
    |                                4. generate_stat_packs.py
    v                                5. generate_predicted_xii.py
  (triggers gate-check)             6. generate_depth_charts.py
    |                                7. matchup analysis scripts
    v                                8. validate outputs
  gate-check.yml                     9. commit outputs
    |                                   |
    v                                   v
  generate-outputs.yml              deploy-dashboard.yml
    |                                   |
    v                                   v
  deploy-dashboard.yml              GitHub Pages
```

### 5.3 Key CI/CD Notes

- The database file is in `.gitignore` -- CI runners download from Cricsheet fresh via `ingest.yml`.
- `generate-outputs.yml` has a `db_check` step that gracefully skips if no database is available (common for PR CI runs).
- The `ingest.yml` workflow references `scripts/ingest.py` (not `scripts/core/ingest.py`). This may need verification that the import path resolves correctly in CI.
- Dashboard deployment uses GitHub Actions Pages (not auto-build) to prevent cascading cancellation emails.
- Concurrency groups prevent parallel runs of generation and deployment.

---

## 6. Weekly Refresh Runbook

### 6.1 When to Refresh

- **Automated:** `ingest.yml` runs every Sunday at 3 AM UTC (8:30 AM IST).
- **Manual trigger:** Any time new Cricsheet data is available, via GitHub Actions UI.
- **Critical refresh:** Before any major editorial/analytics milestone (sprint review, magazine deadline).

### 6.2 Pre-Refresh Checklist

- [ ] Check Cricsheet data availability: https://cricsheet.org/downloads/
- [ ] Verify no active analytics jobs are running (check workflow runs)
- [ ] Confirm `data/raw/` directory structure is intact locally

### 6.3 Automated Refresh (Recommended)

**Option A: GitHub Actions (fully automated)**

1. Navigate to GitHub Actions > "Data Ingestion Pipeline"
2. Click "Run workflow"
3. Set `full_refresh: true` for all leagues, `false` for IPL-only test run
4. Monitor the workflow run
5. Download the database artifact if needed locally

**Option B: Local manual refresh**

```bash
# Step 1: Download latest Cricsheet data
cd data/raw
curl -sLO https://cricsheet.org/downloads/ipl_json.zip
curl -sLO https://cricsheet.org/downloads/bbl_json.zip
curl -sLO https://cricsheet.org/downloads/psl_json.zip
curl -sLO https://cricsheet.org/downloads/cpl_json.zip
curl -sLO https://cricsheet.org/downloads/ntb_json.zip
curl -sLO https://cricsheet.org/downloads/hnd_json.zip
curl -sLO https://cricsheet.org/downloads/sat_json.zip
curl -sLO https://cricsheet.org/downloads/ilt_json.zip
curl -sLO https://cricsheet.org/downloads/lpl_json.zip
curl -sLO https://cricsheet.org/downloads/mlc_json.zip
curl -sLO https://cricsheet.org/downloads/ssm_json.zip
curl -sLO https://cricsheet.org/downloads/sma_json.zip
curl -sLO https://cricsheet.org/downloads/cst_json.zip
curl -sLO https://cricsheet.org/downloads/t20s_json.zip
cd ../..

# Step 2: Run ingestion (full mode)
python scripts/core/ingest.py

# Step 3: Create analytics views
python scripts/core/analytics_ipl.py

# Step 4: Run clustering
python scripts/analysis/player_clustering_v2.py

# Step 5: Generate all outputs
python scripts/generators/generate_outputs.py

# Step 6: Generate Lab data
python scripts/the_lab/generate_venue_and_trends_data.py
python scripts/the_lab/generate_pressure_data.py
python scripts/the_lab/generate_momentum_data.py
python scripts/the_lab/generate_sql_lab_data.py
python scripts/the_lab/update_the_lab.py

# Step 7: Validate
python scripts/validate_all_views.py
python scripts/ml_ops/system_health_score.py
```

### 6.4 Execution Order (Critical)

The pipeline MUST be executed in this order due to data dependencies:

```
1. ingest.py              (creates/updates base tables)
     |
2. analytics_ipl.py       (creates views over base tables)
     |
3. player_clustering_v2.py (requires analytics views)
     |
4. generate_stat_packs.py   \
5. generate_depth_charts.py   |-- Can run in parallel after step 3
6. generate_predicted_xii.py  |
7. generate_all_2023_outputs.py /
     |
8. generate_player_profiles.py  (requires tags from step 7)
     |
9. generate_venue_and_trends_data.py  \
10. generate_pressure_data.py           |-- Lab data (parallel)
11. generate_momentum_data.py           |
12. generate_sql_lab_data.py           /
     |
13. update_the_lab.py          (reads from outputs of steps 4-8)
     |
14. validate_all_views.py      (final validation)
15. system_health_score.py     (health check)
```

### 6.5 Post-Refresh Verification

After each refresh, verify:

1. **Manifest check:** `data/manifests/manifest.json` updated with new timestamp and stats
2. **Row count check:** `fact_ball` count should increase (or stay same if no new data)
3. **Date range check:** `SELECT MAX(match_date) FROM dim_match` reflects latest available data
4. **View validation:** `python scripts/validate_all_views.py` passes
5. **System health:** `python scripts/ml_ops/system_health_score.py` >= 85
6. **Output freshness:** Check file modification dates in `outputs/` and `stat_packs/`

### 6.6 Incremental Ingestion

The ingest script supports incremental mode (added in v1.2.0 / TKT-141):

```bash
python scripts/core/ingest.py --incremental
```

This uses SHA-256 checksums stored in `data/manifests/incremental_manifest.json` to skip unchanged match files. Recommended for regular weekly refreshes where most data is unchanged. Use full mode for initial setup or suspected data corruption.

### 6.7 Rollback Procedure

If ingestion fails:
1. The ingest script automatically restores from `data/cricket_playbook.duckdb.bak` on failure.
2. If manual rollback is needed: `cp data/archive/*.duckdb data/cricket_playbook.duckdb`
3. Re-run analytics views after any database restore: `python scripts/core/analytics_ipl.py`

---

## 7. Automation Recommendations

### 7.1 Immediate (This Sprint)

| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 1 | **Fix `ingest.yml` script path:** Workflow references `scripts/ingest.py` but script lives at `scripts/core/ingest.py`. Verify this resolves correctly or update the path. | S | HIGH |
| 2 | **Download URL format mismatch:** `ingest.yml` uses Cricsheet download format (`ipl_json.zip`) but `data/raw/` contains format like `IPL_Male.zip`. The download step and ingest script may expect different file naming. Needs alignment. | M | HIGH |
| 3 | **Run a fresh ingestion now:** Data is 30 days stale (last ingested Jan 19). BBL, SA20, Super Smash, and T20I data from Jan 15 onwards is missing. | S | HIGH |
| 4 | **Update manifest version:** Align manifest data_version (1.1.0) with ingest script (1.2.0) on next ingestion. | S | LOW |

### 7.2 Near-Term (Next Sprint)

| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 5 | **Add staleness alert:** Add a workflow or cron job that warns when data is > 7 days stale. Can be a simple GitHub Actions job that checks `MAX(match_date)` against current date. | M | MEDIUM |
| 6 | **Consolidate Lab data generation:** The 4 Lab data generator scripts (`generate_venue_and_trends_data.py`, `generate_pressure_data.py`, `generate_momentum_data.py`, `generate_sql_lab_data.py`) are not called in the `generate-outputs.yml` workflow. They should be added to the automation chain. | M | HIGH |
| 7 | **Add data freshness dashboard card:** Add a "Last Updated" indicator to The Lab dashboard showing data currency. | S | MEDIUM |
| 8 | **Clean up legacy database:** Remove or archive `data/ipl_ball_by_ball.duckdb` (12 KB, empty). | S | LOW |

### 7.3 Future (Post-IPL 2026 Launch)

| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 9 | **Cricsheet webhook/RSS monitoring:** Auto-detect when new data is published rather than polling weekly. | L | MEDIUM |
| 10 | **Database artifact caching:** Store the latest good DuckDB in GitHub releases or artifact cache so CI runners don't need full re-ingestion every time. | M | HIGH |
| 11 | **Incremental view refresh:** Only recreate views that depend on changed data, not all 163 views. | L | MEDIUM |
| 12 | **Data quality regression tests:** Add automated tests that compare key metrics (IPL total matches, player counts) against expected baselines after each ingestion. | M | HIGH |

---

## 8. Raw Data Inventory

### 8.1 Source ZIP Files (data/raw/)

| File | Size | Tournament |
|------|------|------------|
| `IPL_Male.zip` | 3.7 MB | Indian Premier League |
| `T20_Internationals_Male.zip` | 9.5 MB | T20 Internationals |
| `T20_Blast_Male.zip` | 4.3 MB | Vitality Blast (England) |
| `BBL_Male.zip` | 2.0 MB | Big Bash League |
| `SMAT_Male.zip` | 2.0 MB | Syed Mushtaq Ali Trophy |
| `CPL_Male.zip` | 1.3 MB | Caribbean Premier League |
| `PSL_Male.zip` | 1.0 MB | Pakistan Super League |
| `CSA_T20_Challenge_Male.zip` | 966 KB | CSA T20 Challenge |
| `Super_Smash_Male.zip` | 805 KB | Super Smash (NZ) |
| `T20_Internationals_Male_Unofficial.zip` | 729 KB | Unofficial T20Is |
| `Hundred_Male.zip` | 493 KB | The Hundred |
| `ILT20_Male.zip` | 452 KB | International League T20 |
| `LPL_Male.zip` | 391 KB | Lanka Premier League |
| `SA20_Male.zip` | 381 KB | SA20 |
| `MLC_Male.zip` | 245 KB | Major League Cricket |
| `NPL_Male.zip` | 206 KB | Nepal Premier League |
| `MSL_Male.zip` | 174 KB | Mzansi Super League |
| `cricket_playbook_files.zip` | 14 KB | (excluded from ingestion) |

**Total: 18 ZIP files, ~29 MB**

---

## 9. Key Contacts & Ownership

| Component | Primary Owner | Backup |
|-----------|--------------|--------|
| Data Ingestion Pipeline | **Brock Purdy** | Brad Stevens |
| Analytics Views | **Stephen Curry** | Andy Flower |
| Generator Scripts | **Stephen Curry** | Tom Brady |
| CI/CD Workflows | **Brad Stevens** | Ime Udoka |
| ML Clustering | **Ime Udoka** | Jose Mourinho |
| Data Quality | **N'Golo Kante** | Brock Purdy |
| The Lab Dashboard | **Kevin De Bruyne** | Brad Stevens |
| System Health | **Jose Mourinho** | Ime Udoka |

---

## 10. Assessment Summary

**Overall Pipeline Health: GOOD (with minor gaps)**

The Cricket Playbook data pipeline is well-architected with clear separation of concerns:
- Ingestion (Cricsheet JSON -> DuckDB) is robust with transaction safety, backup/restore, and incremental mode.
- The analytics layer (163 views) provides comprehensive IPL coverage across multiple time windows and analytical dimensions.
- Output generation is automated through GitHub Actions with daily regeneration.
- Dashboard deployment is fully automated via GitHub Pages.

**Key findings:**
1. IPL data coverage is COMPLETE through IPL 2025 (1,169 matches, 18 seasons).
2. Cross-tournament data is fresh through Jan 15, 2026 (30 days stale as of today).
3. All 231 IPL 2026 squad players are loaded with role classifications.
4. CI/CD automation coverage is strong (6 workflows) but has a gap: Lab data generators are not in the automation chain.
5. The incremental ingestion feature (TKT-141) is implemented but the CI workflow may not be using it.
6. File naming conventions between CI download step and local raw data need alignment.

**Recommended immediate action:** Run a fresh full ingestion to bring data up to date before IPL 2026 season starts.

---

*Assessment by Brock Purdy (Data Pipeline Owner) | TKT-229*
*Cricket Playbook v4.0.0 | Sprint 4.0*
