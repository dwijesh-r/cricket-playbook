# Architecture: Current vs. Target

## Current Architecture (Fully Static)

```
Cricsheet T20 JSON (public, weekly)
        │
        ▼
┌──────────────────┐
│  ingest.py       │  ← GitHub Actions (weekly)
│  → DuckDB 159MB  │     .gitignored, CI artifact only
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ analytics_ipl.py │  ← 35+ DuckDB views
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  8 Generator Scripts (daily CI)      │
│  generate_stat_packs.py              │
│  generate_predicted_xii.py           │
│  generate_depth_charts.py            │
│  generate_rankings.py                │
│  generate_comparison_data.py         │
│  generate_h2h_data.py                │
│  generate_pressure_data.py           │
│  update_the_lab.py                   │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Static JS Data Files                │
│  scripts/the_lab/dashboard/data/     │
│                                      │
│  teams.js ............... 4 KB       │
│  predicted_xii.js ....... 20 KB      │
│  depth_charts.js ........ 85 KB      │
│  full_squads.js ......... 107 KB     │
│  player_profiles.js ..... 509 KB     │
│  season_previews.js ..... 156 KB     │
│  rankings.js ............ 177 KB     │
│  comparison_data.js ..... 741 KB     │
│  h2h_data.js ............ 6.0 MB    │
│  ─────────────────────────────────   │
│  TOTAL: ~7.8 MB loaded in browser    │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  GitHub Pages (statsledge.com)       │
│  100% client-side rendering          │
│  No API, no middleware, no auth      │
└──────────────────────────────────────┘
```

### Current Pain Points

| Issue | Impact |
|-------|--------|
| 7.8 MB of JS loaded upfront | Slow first paint on mobile, wasted bandwidth |
| No user interaction storage | Bug reports go to Web3Forms (250/mo limit, no file upload) |
| SQL Lab uses Parquet in browser | DuckDB-WASM is heavy (~25MB), limited to exported subset |
| No live data updates | Every change requires full rebuild + deploy cycle |
| No user features | Can't save queries, preferences, or track report status |

---

## Target Architecture (Hybrid: Static + Neon)

```
┌──────────────────────────────────────────────────────────┐
│                    GitHub Actions (CI/CD)                  │
│                                                          │
│  ingest.py → DuckDB → generators → static JS + Neon sync │
│                                                          │
│  New: neon_sync.py pushes fact/dim tables to Neon        │
│  New: Materialized views refreshed after data sync       │
└──────────┬──────────────────────────────┬────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐    ┌─────────────────────────────┐
│  Static JS (small)  │    │  Neon Serverless Postgres    │
│  GitHub Pages       │    │                             │
│                     │    │  reports.issues (bug reports) │
│  teams.js (4 KB)    │    │  cricket.fact_ball (2.14M)   │
│  predicted_xii.js   │    │  cricket.dim_* (dimensions)  │
│  depth_charts.js    │    │  cricket.mv_rankings         │
│  season_previews.js │    │  cricket.mv_h2h              │
│  freshness.js       │    │  cricket.mv_comparison       │
│                     │    │  app.saved_queries           │
│  (~370 KB total)    │    │                             │
└─────────┬───────────┘    └──────────┬──────────────────┘
          │                           │
          │    ┌──────────────────┐   │
          └───►│  StatSledge      │◄──┘
               │  Browser         │
               │                  │
               │  Static data:    │
               │    Team configs  │
               │    Predicted XIs │
               │    Season prose  │
               │                  │
               │  Neon queries:   │
               │    Rankings      │
               │    H2H data      │
               │    Comparisons   │
               │    Bug reports   │
               │    SQL Lab       │
               └──────────────────┘
```

### What Stays Static (GitHub Pages)

Files under ~200 KB that are loaded on every page or rarely change:

| File | Size | Reason to keep static |
|------|------|-----------------------|
| teams.js | 4 KB | Tiny, used everywhere |
| predicted_xii.js | 20 KB | Small, team configs |
| depth_charts.js | 85 KB | Moderate, used on teams page only |
| season_previews.js | 156 KB | Editorial content, not queryable |
| freshness.js | 1 KB | Metadata |

### What Moves to Neon

Files that are large, queryable, or user-generated:

| File | Size | Neon Replacement | Benefit |
|------|------|-----------------|---------|
| h2h_data.js | 6.0 MB | `cricket.mv_h2h` materialized view | Query specific matchups on demand |
| comparison_data.js | 741 KB | `cricket.mv_comparison` | Query specific team pairs |
| rankings.js | 177 KB | `cricket.mv_rankings` | Paginated, sortable |
| player_profiles.js | 509 KB | `cricket.mv_player_profiles` | Query per-player |
| full_squads.js | 107 KB | `cricket.dim_player` + joins | Already structured |
| (Web3Forms) | N/A | `reports.issues` table | No limits, queryable |
| (SQL Lab Parquet) | 31 MB | Direct Neon queries | Real SQL, no WASM |

**Savings:** Browser goes from loading ~7.8 MB to ~370 KB upfront. Heavy data fetched on demand.

---

## Connection Strategy

### Neon Serverless HTTP Driver

Neon provides `@neondatabase/serverless` which works over HTTP — no WebSocket, no TCP. This is critical because GitHub Pages is static hosting with no backend.

```javascript
// Browser-side (no backend needed)
import { neon } from '@neondatabase/serverless';

const sql = neon(NEON_CONNECTION_STRING);
const result = await sql`
    SELECT * FROM cricket.mv_rankings
    WHERE tier = ${selectedTier}
    ORDER BY overall_rank
`;
```

### Connection String

The connection string will be a **read-only pooled endpoint** exposed via a JS config file that's .gitignored locally but set as a GitHub Pages environment variable or embedded at deploy time.

```
postgresql://readonly_user:***@ep-xxx.us-east-2.aws.neon.tech/statsledge?sslmode=require
```

### Roles

| Role | Permissions | Used By |
|------|------------|---------|
| `readonly` | SELECT on `cricket.*` | Dashboard data queries |
| `reporter` | INSERT on `reports.issues` | Bug report form |
| `admin` | ALL on all schemas | CI/CD sync, migrations |
| `sql_lab` | SELECT on `cricket.*` (rate-limited) | SQL Lab page |

---

## Workflow Changes

### Current
```
Push → gate-check → generate-outputs → deploy-dashboard
```

### Target
```
Push → gate-check → generate-outputs → neon-sync → deploy-dashboard
                                           │
                                           ▼
                                    Refresh materialized views
                                    Update cricket.* tables
                                    Verify row counts
```

New workflow: `neon-sync.yml`
- Trigger: After `generate-outputs` completes
- Steps: Export DuckDB tables → bulk load to Neon → refresh materialized views
- Owner: Brock Purdy

---

## Cost Analysis

### Neon Free Tier
- 0.5 GB storage (our data: ~200 MB in Postgres)
- 191 compute hours/month (auto-scales to zero)
- 1 project, 10 branches
- Serverless HTTP driver included

### When We'd Need Pro ($19/mo)
- Storage exceeds 0.5 GB (unlikely for IPL data)
- Compute hours exceed 191/mo (depends on SQL Lab usage)
- Need more than 10 branches

### Verdict
Free tier is sufficient for Phase 1-3. Monitor compute hours once SQL Lab is live.
