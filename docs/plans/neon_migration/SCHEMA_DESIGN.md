# Neon Schema Design

**Database:** `statsledge`
**Provider:** Neon Serverless Postgres
**Region:** us-east-2 (closest to GitHub Actions runners)

---

## Schema Overview

```
statsledge (database)
├── reports      → User-submitted bug reports and feedback
├── cricket      → Analytical data (migrated from DuckDB)
└── app          → User features (Phase 3+)
```

---

## 1. `reports` Schema (Phase 1)

### `reports.issues`

Replaces Web3Forms. Stores all bug reports, data inconsistencies, and suggestions submitted from the dashboard.

```sql
CREATE SCHEMA IF NOT EXISTS reports;

CREATE TABLE reports.issues (
    id              SERIAL PRIMARY KEY,
    type            VARCHAR(50) NOT NULL
                        CHECK (type IN ('Bug', 'Data Inconsistency', 'Suggestion', 'Other')),
    context         VARCHAR(255),           -- Player name, team, or page section
    message         TEXT NOT NULL,
    expected_actual TEXT,                    -- "SR shows 145.2 but should be 152.3"
    email           VARCHAR(255) NOT NULL,
    page            VARCHAR(100),           -- Source page (index.html, teams.html, etc.)
    status          VARCHAR(20) NOT NULL DEFAULT 'open'
                        CHECK (status IN ('open', 'reviewed', 'resolved', 'wont_fix')),
    reviewer_notes  TEXT,                   -- Internal notes when reviewing
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_issues_status ON reports.issues(status);
CREATE INDEX idx_issues_created ON reports.issues(created_at DESC);
CREATE INDEX idx_issues_type ON reports.issues(type);
```

---

## 2. `cricket` Schema (Phase 2)

### Dimension Tables

```sql
CREATE SCHEMA IF NOT EXISTS cricket;

-- Teams
CREATE TABLE cricket.dim_team (
    team_id         VARCHAR(10) PRIMARY KEY,     -- MI, CSK, RCB, etc.
    team_name       VARCHAR(100) NOT NULL,
    short_name      VARCHAR(10) NOT NULL,
    home_venue      VARCHAR(100),
    primary_color   VARCHAR(7),                  -- Hex color
    titles          INTEGER DEFAULT 0,
    captain         VARCHAR(100),
    coach           VARCHAR(100)
);

-- Players
CREATE TABLE cricket.dim_player (
    player_id       VARCHAR(50) PRIMARY KEY,     -- Cricsheet player ID
    player_name     VARCHAR(100) NOT NULL,
    team_id         VARCHAR(10) REFERENCES cricket.dim_team(team_id),
    role            VARCHAR(30),                 -- Batter, Bowler, All-Rounder, WK-Batter
    batting_style   VARCHAR(30),                 -- Right-hand, Left-hand
    bowling_style   VARCHAR(50),                 -- Right-arm fast, Left-arm orthodox, etc.
    nationality     VARCHAR(50),
    is_overseas     BOOLEAN DEFAULT FALSE,
    auction_price   NUMERIC(10,2),               -- In crores
    acquisition     VARCHAR(30),                 -- Auction, Retained, RTM
    cluster_bat     VARCHAR(50),                 -- ML cluster label (batter)
    cluster_bowl    VARCHAR(50)                  -- ML cluster label (bowler)
);

-- Matches
CREATE TABLE cricket.dim_match (
    match_id        VARCHAR(50) PRIMARY KEY,
    season          INTEGER NOT NULL,
    tournament      VARCHAR(50) NOT NULL,        -- IPL, BBL, PSL, T20I, etc.
    date            DATE NOT NULL,
    venue           VARCHAR(100),
    team_1          VARCHAR(10),
    team_2          VARCHAR(10),
    winner          VARCHAR(10),
    toss_winner     VARCHAR(10),
    toss_decision   VARCHAR(10),                 -- bat, field
    result_type     VARCHAR(20)                  -- runs, wickets, tie, no result
);

-- Venues
CREATE TABLE cricket.dim_venue (
    venue_id        SERIAL PRIMARY KEY,
    venue_name      VARCHAR(100) NOT NULL UNIQUE,
    city            VARCHAR(50),
    country         VARCHAR(50),
    pace_bias       NUMERIC(4,2),                -- 0-1 scale (1 = full pace)
    avg_first_score INTEGER,
    avg_second_score INTEGER
);
```

### Fact Tables

```sql
-- Ball-by-ball (largest table: ~2.14M rows)
CREATE TABLE cricket.fact_ball (
    id              BIGSERIAL PRIMARY KEY,
    match_id        VARCHAR(50) NOT NULL REFERENCES cricket.dim_match(match_id),
    innings         SMALLINT NOT NULL,
    over_num        SMALLINT NOT NULL,
    ball_num        SMALLINT NOT NULL,
    batter_id       VARCHAR(50),
    bowler_id       VARCHAR(50),
    non_striker_id  VARCHAR(50),
    runs_batter     SMALLINT DEFAULT 0,
    runs_extras     SMALLINT DEFAULT 0,
    runs_total      SMALLINT DEFAULT 0,
    is_wicket       BOOLEAN DEFAULT FALSE,
    wicket_type     VARCHAR(30),
    player_out_id   VARCHAR(50),
    extra_type      VARCHAR(20),                 -- wide, noball, bye, legbye
    phase           VARCHAR(10)                  -- powerplay, middle, death
        GENERATED ALWAYS AS (
            CASE
                WHEN over_num < 6 THEN 'powerplay'
                WHEN over_num < 16 THEN 'middle'
                ELSE 'death'
            END
        ) STORED
);

-- Indexes for common query patterns
CREATE INDEX idx_fact_ball_match ON cricket.fact_ball(match_id);
CREATE INDEX idx_fact_ball_batter ON cricket.fact_ball(batter_id);
CREATE INDEX idx_fact_ball_bowler ON cricket.fact_ball(bowler_id);
CREATE INDEX idx_fact_ball_phase ON cricket.fact_ball(phase);
CREATE INDEX idx_fact_ball_innings ON cricket.fact_ball(match_id, innings);

-- Player match performance (pre-aggregated)
CREATE TABLE cricket.fact_player_match (
    id              BIGSERIAL PRIMARY KEY,
    match_id        VARCHAR(50) NOT NULL,
    player_id       VARCHAR(50) NOT NULL,
    team_id         VARCHAR(10),
    runs_scored     INTEGER DEFAULT 0,
    balls_faced     INTEGER DEFAULT 0,
    fours           INTEGER DEFAULT 0,
    sixes           INTEGER DEFAULT 0,
    strike_rate     NUMERIC(6,2),
    overs_bowled    NUMERIC(4,1) DEFAULT 0,
    runs_conceded   INTEGER DEFAULT 0,
    wickets         INTEGER DEFAULT 0,
    economy         NUMERIC(5,2),
    dots_bowled     INTEGER DEFAULT 0,
    catches         INTEGER DEFAULT 0,
    UNIQUE(match_id, player_id)
);

CREATE INDEX idx_fpm_player ON cricket.fact_player_match(player_id);
CREATE INDEX idx_fpm_team ON cricket.fact_player_match(team_id);
```

### Materialized Views

These replace the large static JS files. Refreshed after each data sync.

```sql
-- Rankings (replaces rankings.js, 177 KB)
CREATE MATERIALIZED VIEW cricket.mv_rankings AS
SELECT
    t.team_id,
    t.team_name,
    -- Aggregate metrics computed from fact tables
    COUNT(DISTINCT m.match_id) AS matches_played,
    SUM(CASE WHEN m.winner = t.team_id THEN 1 ELSE 0 END) AS wins,
    ROUND(AVG(fpm.strike_rate) FILTER (WHERE fpm.runs_scored > 0), 2) AS avg_bat_sr,
    ROUND(AVG(fpm.economy) FILTER (WHERE fpm.overs_bowled > 0), 2) AS avg_bowl_econ
FROM cricket.dim_team t
JOIN cricket.dim_match m ON m.team_1 = t.team_id OR m.team_2 = t.team_id
JOIN cricket.fact_player_match fpm ON fpm.match_id = m.match_id AND fpm.team_id = t.team_id
WHERE m.tournament = 'IPL' AND m.season >= 2023
GROUP BY t.team_id, t.team_name;

-- H2H (replaces h2h_data.js, 6 MB)
CREATE MATERIALIZED VIEW cricket.mv_h2h AS
SELECT
    m.team_1,
    m.team_2,
    m.season,
    m.date,
    m.venue,
    m.winner,
    m.toss_winner,
    m.toss_decision,
    m.result_type
FROM cricket.dim_match m
WHERE m.tournament = 'IPL'
ORDER BY m.date DESC;

-- Player profiles (replaces player_profiles.js, 509 KB)
CREATE MATERIALIZED VIEW cricket.mv_player_profiles AS
SELECT
    p.player_id,
    p.player_name,
    p.team_id,
    p.role,
    p.batting_style,
    p.bowling_style,
    p.is_overseas,
    p.auction_price,
    p.cluster_bat,
    p.cluster_bowl,
    COALESCE(SUM(fpm.runs_scored), 0) AS total_runs,
    COALESCE(SUM(fpm.balls_faced), 0) AS total_balls,
    COALESCE(SUM(fpm.wickets), 0) AS total_wickets,
    COUNT(DISTINCT fpm.match_id) AS matches
FROM cricket.dim_player p
LEFT JOIN cricket.fact_player_match fpm ON fpm.player_id = p.player_id
GROUP BY p.player_id, p.player_name, p.team_id, p.role,
         p.batting_style, p.bowling_style, p.is_overseas,
         p.auction_price, p.cluster_bat, p.cluster_bowl;

-- Refresh command (run after data sync)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY cricket.mv_rankings;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY cricket.mv_h2h;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY cricket.mv_player_profiles;
```

---

## 3. `app` Schema (Phase 3+)

```sql
CREATE SCHEMA IF NOT EXISTS app;

-- Saved SQL Lab queries
CREATE TABLE app.saved_queries (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    sql_text        TEXT NOT NULL,
    description     TEXT,
    author_email    VARCHAR(255),
    is_public       BOOLEAN DEFAULT FALSE,
    run_count       INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- User preferences (cookie-based, no auth)
CREATE TABLE app.user_preferences (
    session_id      VARCHAR(64) PRIMARY KEY,     -- Browser-generated UUID
    favorite_team   VARCHAR(10),
    theme           VARCHAR(20) DEFAULT 'dark',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Data Volume Estimates

| Table | Rows | Est. Size (Postgres) |
|-------|------|---------------------|
| cricket.fact_ball | 2,140,000 | ~150 MB |
| cricket.fact_player_match | ~45,000 | ~5 MB |
| cricket.dim_match | 9,357 | ~1 MB |
| cricket.dim_player | 431 | <1 MB |
| cricket.dim_team | 10 | <1 KB |
| cricket.dim_venue | ~20 | <1 KB |
| reports.issues | <1,000/year | <1 MB |
| **TOTAL** | | **~160 MB** |

Neon free tier: 0.5 GB. We fit comfortably with room for growth.

---

## Naming Conventions

- Schema names: lowercase, singular (`reports`, `cricket`, `app`)
- Table names: lowercase, snake_case, prefixed (`dim_`, `fact_`, `mv_`)
- Column names: lowercase, snake_case
- Indexes: `idx_{table}_{column}`
- Constraints: inline CHECKs preferred over named constraints
