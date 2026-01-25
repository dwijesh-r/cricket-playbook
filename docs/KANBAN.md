# Cricket Playbook - Kanban Board

**Product Owner:** Tom Brady
**Version:** 2.9.0
**Last Updated:** 2026-01-25

---

## Board Overview

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│    BACKLOG      │    TO DO        │   IN PROGRESS   │    REVIEW       │     DONE        │
│    (Icebox)     │  (Sprint 3.0)   │                 │                 │   (Sprint 2.9)  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

---

## ✅ DONE (Sprint 2.9 - Completed)

### Bug Fixes & Data Quality

| ID | Task | Owner | Completed | Commit |
|----|------|-------|-----------|--------|
| S2.9-01 | Entry point bug fix (ball_seq > 120) | Andy Flower + Stephen Curry | 2026-01-25 | `d320501` |
| S2.9-02 | Output validation script | Andy Flower | 2026-01-25 | `d320501` |
| S2.9-03 | Matchup missing data fix (use analytics table) | Stephen Curry | 2026-01-25 | `e085a58` |
| S2.9-04 | Matchup tag criteria (add BPD check) | Stephen Curry | 2026-01-25 | `e085a58` |
| S2.9-05 | Player clustering ball_seq fix | Stephen Curry | 2026-01-25 | `ef3effd` |

### CI/CD & Infrastructure

| ID | Task | Owner | Completed | Commit |
|----|------|-------|-----------|--------|
| S2.9-06 | GitHub Actions CI workflow | Ime Udoka | 2026-01-25 | `d320501` |
| S2.9-07 | Pre-commit hooks (Ruff linter/formatter) | Ime Udoka | 2026-01-25 | `d320501` |

---

## 🔍 REVIEW (Awaiting Founder Approval)

| ID | Task | Owner | Reviewer | Status |
|----|------|-------|----------|--------|
| **FR-4** | **Founder Review #4** | Tom Brady | Founder | **READY FOR REVIEW** |

### Founder Review #4 Checklist

**Data Quality & Accuracy:**
- [x] 2023+ data filter implementation (219 IPL matches)
- [x] Entry point bug fixed (max_entry_ball ≤ 120)
- [x] Matchup data complete (422 batters, was 125)
- [x] ball_seq bugs fixed across codebase

**Cluster Labels & Tags:**
- [x] Standardized 6 batter roles + 7 bowler roles
- [x] Tag criteria documented with thresholds
- [x] BPD (balls per dismissal) added to matchup tags

**Documentation:**
- [x] CSV schema documentation in outputs/README.md
- [x] Glossary with phases, metrics, tag criteria
- [x] All README files updated to v2.9.0

**Infrastructure:**
- [x] GitHub Actions CI workflow
- [x] Pre-commit hooks (Ruff)
- [x] Output validation script

---

## 🚧 IN PROGRESS

| ID | Task | Owner | Priority | Notes |
|----|------|-------|----------|-------|
| - | *Awaiting Founder Review #4* | - | - | - |

---

## 📋 TO DO (Sprint 3.0 - Post-Founder Review)

### P0 - Critical (Must Have)

---

#### S3.0-01: Founder Review #4 Response
**Owner:** Tom Brady | **Estimate:** 2h | **Dependencies:** FR-4

**What:** Process and document all feedback from Founder Review #4, create action items.

**Why Important:** Founder reviews are our quality gates. Addressing feedback promptly ensures we're building what stakeholders need and catches issues early before they compound.

**What It Involves:**
- Consolidate all Founder feedback into actionable tickets
- Prioritize based on severity (blockers vs nice-to-haves)
- Update Kanban with new tasks if needed
- Communicate timeline for fixes to stakeholders

---

#### S3.0-02: Address Founder Feedback
**Owner:** Stephen Curry | **Estimate:** 4h | **Dependencies:** S3.0-01

**What:** Implement all required changes identified in Founder Review #4.

**Why Important:** The Founder Review is our final quality gate before production use. Any issues identified must be resolved to maintain data accuracy and stakeholder confidence.

**What It Involves:**
- Fix any data quality issues flagged
- Update documentation if unclear
- Regenerate outputs if calculations change
- Re-run validation to confirm fixes

---

### P1 - High (Should Have)

---

#### S3.0-03: Model Serialization (joblib)
**Owner:** Ime Udoka | **Estimate:** 3h | **Dependencies:** None

**What:** Save trained K-means clustering models to disk using joblib, enabling reuse without retraining.

**Why Important:** Currently we retrain models every run, which is slow and can produce slightly different clusters each time. Serialization ensures consistency and enables deployment.

**What It Involves:**
- Modify `player_clustering_v2.py` to save models after training
- Add version tracking to model files
- Create model loading utility for inference
- Document model versioning strategy
- Test that loaded models produce identical results

---

#### S3.0-04: Recency Weighting Toggle
**Owner:** Stephen Curry | **Estimate:** 4h | **Dependencies:** None

**What:** Add configurable recency weighting to analytics, allowing users to choose between "all-time" and "recent form" analysis.

**Why Important:** Different use cases need different weightings. Auction analysis might want career stats; match predictions might want recent form. Currently hardcoded to 2x for 2021-2025.

**What It Involves:**
- Add `--recency-mode` CLI flag (none, moderate, aggressive)
- Modify analytics queries to apply configurable weights
- Update documentation with weight definitions
- Add validation that weighted stats sum correctly
- Test with different weighting profiles

---

#### S3.0-05: Unit Test Restructuring
**Owner:** N'Golo Kanté | **Estimate:** 4h | **Dependencies:** None

**What:** Reorganize test suite into logical modules with proper fixtures and improved coverage.

**Why Important:** Current tests are scattered and some rely on live database. Proper test structure enables CI to catch issues and gives confidence in refactoring.

**What It Involves:**
- Create `tests/unit/`, `tests/integration/` structure
- Add pytest fixtures for mock data
- Ensure tests can run without database (unit tests)
- Add coverage reporting to CI
- Target 80% coverage for core modules

---

#### S3.0-06: Andy Flower Analytics Implementation
**Owner:** Stephen Curry | **Estimate:** 8h | **Dependencies:** See research agenda

**What:** Implement Phase 1 metrics from Andy Flower's research: Momentum Index, Pressure Sequence Index, Clutch Factor, Death Overs Closer Rating.

**Why Important:** These metrics represent our competitive advantage - novel cricket analytics that go beyond traditional stats. Fans and broadcasters want to understand *why* matches unfold, not just *what* happened.

**What It Involves:**
- Implement Momentum Index (MI) calculation
- Build Pressure Sequence Index (PSI) detection
- Create Clutch Factor (CF) for batters
- Add Death Overs Closer Rating (DOCR)
- Generate new CSV outputs with these metrics
- Add to stat packs for team-level rollups

---

### P2 - Medium (Nice to Have)

---

#### S3.0-07: Interactive Dashboard (Streamlit)
**Owner:** Kevin de Bruyne | **Estimate:** 8h | **Dependencies:** None

**What:** Build a Streamlit web app for exploring player stats, matchups, and team comparisons interactively.

**Why Important:** CSVs and markdown files are hard to explore. A dashboard lets stakeholders ask ad-hoc questions without engineering support, reducing turnaround time.

**What It Involves:**
- Setup Streamlit project structure
- Create player search/comparison page
- Build team stat pack viewer
- Add matchup explorer (batter vs bowling type)
- Include phase-wise performance charts
- Deploy to Streamlit Cloud or internal server

---

#### S3.0-08: Great Expectations Validation
**Owner:** Brock Purdy | **Estimate:** 6h | **Dependencies:** None

**What:** Implement Great Expectations data validation framework for automated data quality checks.

**Why Important:** Manual validation doesn't scale. Great Expectations provides declarative rules that run automatically, catching data drift and quality issues before they reach outputs.

**What It Involves:**
- Install and configure Great Expectations
- Define expectations for each analytics table
- Create validation checkpoints
- Integrate with CI pipeline
- Build data docs for transparency
- Alert on validation failures

---

#### S3.0-09: Type Hints (mypy strict)
**Owner:** Brad Stevens | **Estimate:** 4h | **Dependencies:** None

**What:** Add comprehensive type hints to all Python modules and enable mypy strict mode in CI.

**Why Important:** Type hints catch bugs at development time, improve IDE support, and serve as documentation. Critical for maintainability as codebase grows.

**What It Involves:**
- Add type hints to all function signatures
- Define custom types for domain objects (PlayerId, MatchId, etc.)
- Configure mypy with strict settings
- Add mypy check to pre-commit and CI
- Fix all type errors surfaced

---

#### S3.0-10: Bowler Handedness Matchup Fixes
**Owner:** Stephen Curry | **Estimate:** 3h | **Dependencies:** None

**What:** Apply same fixes from batter matchup to bowler handedness matchup - use analytics table, aggregate properly, add BPD criteria.

**Why Important:** Consistency across all matchup outputs. Bowler handedness data likely has same issues as batter matchup (missing data, threshold applied too early).

**What It Involves:**
- Audit bowler_handedness_matchup.py for similar bugs
- Update to use analytics tables
- Fix aggregation order (aggregate first, then threshold)
- Add dismissal rate to tag criteria
- Regenerate outputs and validate

---

## 📦 BACKLOG (Future Sprints)

### Sprint 3.1 - API & Integration

---

#### S3.1-01: REST API Endpoint (FastAPI)
**Owner:** Jayson Tatum | **Priority:** P2

**What:** Create a FastAPI-based REST API exposing player stats, matchups, and recommendations.

**Why Important:** Enables external systems (broadcast graphics, fantasy apps, editorial tools) to consume our analytics programmatically without file transfers.

**What It Involves:**
- Design API schema (OpenAPI spec)
- Implement endpoints: `/players`, `/matchups`, `/teams`
- Add authentication (API keys)
- Setup rate limiting
- Deploy with Docker
- Document with Swagger UI

---

#### S3.1-02: Real-time Match Simulation
**Owner:** Stephen Curry | **Priority:** P3

**What:** Build a match simulator that projects likely outcomes given current state (score, wickets, overs, batters).

**Why Important:** "What if" scenarios for broadcast ("If Kohli stays 10 more balls, win probability jumps to...") and pre-match analysis.

**What It Involves:**
- Build Monte Carlo simulation engine
- Use historical data for outcome probabilities
- Implement ball-by-ball projection
- Create visualization of probability distributions
- Validate against actual match outcomes

---

#### S3.1-03: Webhook for Live Data Feeds
**Owner:** Brock Purdy | **Priority:** P3

**What:** Implement webhook receiver for live match data, enabling real-time analytics updates.

**Why Important:** Currently all analysis is post-match. Live data enables real-time Momentum Index, win probability, and pressure alerts during matches.

**What It Involves:**
- Design webhook receiver endpoint
- Handle Cricsheet or provider format
- Update analytics incrementally (not full recompute)
- Build event queue for reliability
- Add monitoring for data freshness

---

### Sprint 3.2 - Advanced Analytics

---

#### S3.2-01: Win Probability Model
**Owner:** Stephen Curry | **Priority:** P2

**What:** Build a model that calculates win probability at any point in a match based on runs, wickets, overs, and required rate.

**Why Important:** The foundation for turning point detection and match narrative generation. Every broadcast wants "X team has 73% chance of winning."

**What It Involves:**
- Build historical outcome dataset by match state
- Train logistic regression or XGBoost model
- Validate with held-out matches
- Calculate WP after each ball
- Identify turning points (WP delta > 8%)
- Create visualization library

---

#### S3.2-02: Player Form Tracker (Rolling 10 Matches)
**Owner:** Stephen Curry | **Priority:** P2

**What:** Track player performance over rolling windows (last 5, 10, 15 matches) to identify form trends.

**Why Important:** Career stats hide recent trends. A player averaging 40 career but 22 in last 10 matches is in poor form - critical for team selection.

**What It Involves:**
- Build rolling window aggregation functions
- Track trend direction (improving/declining)
- Compare to career baseline
- Flag "form alerts" (significant deviation)
- Add to player profiles in stat packs

---

#### S3.2-03: Venue-Pitch Condition Analysis
**Owner:** Andy Flower | **Priority:** P2

**What:** Quantify venue characteristics: pace vs spin friendly, first vs second innings advantage, boundary dimensions effect.

**Why Important:** Team selection depends on venue. "Chepauk turns, play 3 spinners" is folklore - we need data-driven venue profiles.

**What It Involves:**
- Calculate pace vs spin economy by venue
- Track 1st vs 2nd innings scoring rates
- Analyze boundary rates by venue
- Build venue archetype classifications
- Integrate with pre-match team recommendations

---

#### S3.2-04: Opposition-Specific Tactics Engine
**Owner:** Pep Guardiola | **Priority:** P3

**What:** Generate tactical recommendations based on specific opponent lineup - who to bowl at which batter, optimal batting order.

**Why Important:** Generic stats don't win matches. Knowing "Bowler X has dismissed Batter Y 4 times in 12 balls" enables targeted tactics.

**What It Involves:**
- Build head-to-head matchup matrices
- Identify exploitable weaknesses
- Generate bowling assignment recommendations
- Suggest batting order changes vs specific bowlers
- Create tactical briefing documents

---

### Icebox (Unscheduled)

| ID | Task | Owner | Priority | Description |
|----|------|-------|----------|-------------|
| ICE-01 | Historical trend analysis | Stephen Curry | P3 | Year-over-year stat evolution (is T20 getting faster?) |
| ICE-02 | Injury/availability tracking | Tom Brady | P3 | Track player availability, injury history for squad planning |
| ICE-03 | Player valuation model | Stephen Curry | P3 | Predict auction prices based on stats, age, market dynamics |
| ICE-04 | Commentary auto-generation | Virat Kohli | P3 | Generate narrative text from stats ("Kohli's SR drops 30 points vs left-arm spin") |
| ICE-05 | Video highlight tagging | Kevin de Bruyne | P4 | Link stats to video timestamps for automated highlight reels |

---

## 🔬 Andy Flower Research Agenda

### Comprehensive Analytics Research Document

**Location:** `editorial/andy_flower_analytics_research.md`

**Document Contents:**
- 17 novel metrics with full calculations
- Data requirements mapped to our schema
- Feasibility ratings (Easy/Medium/Hard)
- Implementation priority recommendations
- **NEW: Fan's Perspective section** with 6 fan-focused metrics

### Fan-Focused Metrics (NEW)

| Metric | Fan Question It Answers |
|--------|------------------------|
| **Death Overs Closer Rating (DOCR)** | "Who should bat when we need 20 off 10?" |
| **Consistency Index (CI)** | "Is he reliable or a one-match wonder?" |
| **Entertainment Value Score (EVS)** | "Who's exciting to watch?" |
| **Big Match Factor (BMF)** | "Does he show up in finals?" |
| **Value-for-Money Index (VMI)** | "Was the auction price justified?" |
| **Team Impact Score (TIS)** | "Does he make the team better?" |

### Implementation Phases

| Phase | Metrics | Complexity | Timeline |
|-------|---------|------------|----------|
| 1 | Momentum Index, PSI, DOCR, BMF | Easy | Sprint 3.0 |
| 2 | Match Control Index, Clutch Factor, EVS | Medium | Sprint 3.1 |
| 3 | Win Probability, Partnership Synergy | Medium | Sprint 3.2 |
| 4 | Full Fielding Impact, Bowling Patterns | Hard | Future |

---

## Sprint 2.9 Summary

### Key Achievements

| Category | Metric | Before | After |
|----------|--------|--------|-------|
| Batter matchup data | Total batters | 125 | 422 |
| Entry point validation | max_entry_ball | 136 | 120 |
| CI/CD | Automated checks | None | Ruff + pre-commit |
| Documentation | Glossary | Missing | Complete |

### Bug Fixes Summary

| Bug | Root Cause | Fix |
|-----|------------|-----|
| Entry point > 120 | `ball_seq` includes extras | Use legal ball count |
| Missing matchup data | Joined only 2026 squad bowlers | Use analytics table |
| Wrong tag criteria | Only checked SR | Added BPD check |
| Clustering position | `ball_seq` for batting position | Use legal ball count |

### Commits This Sprint

1. `d320501` - Entry point fix + validation + CI/CD
2. `e085a58` - Matchup data fixes + tag criteria
3. `ef3effd` - Player clustering ball_seq fix
4. `9d2e6de` - Kanban update

---

## Agent Role Clarification

| Agent | Primary Role | Expertise |
|-------|--------------|-----------|
| **Andy Flower** | Cricket Analytics QA | Domain expertise, metric design, fan perspective |
| **Stephen Curry** | Analytics Lead | Implementation, SQL, Python, data pipelines |
| **Ime Udoka** | ML Ops Engineer | CI/CD, deployment, model serialization |
| **Tom Brady** | Product Owner | Roadmap, stakeholder management, documentation |
| **Brad Stevens** | Architecture | Code quality, type safety, best practices |
| **N'Golo Kanté** | QA Engineer | Testing, coverage, edge cases |
| **Kevin de Bruyne** | Frontend/UX | Dashboards, visualizations |
| **Brock Purdy** | Data Pipeline | Ingestion, validation, Great Expectations |
| **Pep Guardiola** | Tactical Analysis | Opposition analysis, recommendations |

---

## Definition of Done

- [x] Code passes all tests (pytest)
- [x] Code passes linting (Ruff)
- [x] Pre-commit hooks pass
- [x] Documentation updated
- [x] README reflects changes
- [x] Committed to main branch
- [ ] **Founder Review #4 approved**

---

## Blockers & Risks

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Founder Review delays | High | Comprehensive documentation prepared | Ready |
| Small sample size (2023+ only) | Medium | Add optional full-history mode (S3.0-04) | Backlog |
| ball_seq bugs in other scripts | High | Grep audit completed | ✅ Fixed |
| Missing fan engagement metrics | Medium | Andy Flower research expanded | ✅ Done |

---

*Cricket Playbook v2.9.0 - Ready for Founder Review #4*
