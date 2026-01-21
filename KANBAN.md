# Cricket Playbook - Sprint Kanban

**Last Updated:** 2026-01-20
**Current Version:** v2.2.0
**Owner:** Tom Brady (Product Owner)

---

## DONE

### v1.0 - Foundation Sprint (2026-01-17)
| Task | Owner | Sign-off |
|------|-------|----------|
| Schema design | Brock Purdy | Tom Brady |
| Ingestion pipeline | Brock Purdy | Tom Brady |
| Data load (9,357 matches) | Brock Purdy | N'Golo Kanté |
| QA certification | N'Golo Kanté | PASS |
| Cricket domain review | Andy Flower | APPROVED |

### v2.0 - IPL 2026 Sprint (2026-01-19)
| Task | Owner | Sign-off |
|------|-------|----------|
| IPL 2026 squad data (231 players) | Andy Flower | Tom Brady |
| Bowler classifications (280 players) | Andy Flower | Tom Brady |
| IPL contract data | Andy Flower | Tom Brady |
| 26 core analytics views | Stephen Curry | Tom Brady |
| Stat pack generator (10 teams) | Stephen Curry | Tom Brady |
| Franchise alias handling | Stephen Curry | Andy Flower |

### v2.1 - Rework Sprint (2026-01-20)
| Task | Owner | Sign-off |
|------|-------|----------|
| Sample size indicators (all tables) | Stephen Curry | Andy Flower |
| Percentile ranking views (4) | Stephen Curry | Tom Brady |
| Benchmark views (4) | Stephen Curry | Tom Brady |
| CLI runner script | Brock Purdy | Tom Brady |
| Smoke tests (65 tests) | N'Golo Kanté | PASS |
| Schema validation (33 checks) | N'Golo Kanté | PASS |
| Jupyter notebook explorer | Stephen Curry | Tom Brady |
| README.md documentation | Tom Brady | Tom Brady |
| Andy Flower v2.1 review | Andy Flower | APPROVED |

### v2.2 - Player Clustering (2026-01-20)
| Task | Owner | Sign-off |
|------|-------|----------|
| K-means clustering model | Stephen Curry | Tom Brady |
| Batter clusters (5 archetypes, 87 players) | Stephen Curry | Andy Flower |
| Bowler clusters (5 archetypes, 152 players) | Stephen Curry | Andy Flower |
| Cluster label definitions | Andy Flower | Pending User Review |
| Squad CSV with classifications | Stephen Curry | Tom Brady |
| Player ID collision fix (Abhinandan/Arshdeep) | Brock Purdy | Tom Brady |
| Player experience export | Stephen Curry | Tom Brady |

---

## IN PROGRESS

| Task | Owner | Status |
|------|-------|--------|
| User review of cluster archetypes | Andy Flower | Awaiting feedback |

---

## BACKLOG

### High Priority (v2.3)
| Task | Owner | Description |
|------|-------|-------------|
| Integrate clusters into stat packs | Stephen Curry | Add archetype labels to player tables |
| Squad balance analysis | Andy Flower | Team composition by archetype |
| Venue normalization | Brock Purdy | "Arun Jaitley" vs "Feroz Shah Kotla" |

### Medium Priority (v2.4)
| Task | Owner | Description |
|------|-------|-------------|
| Situational analysis views | Stephen Curry | Chase vs set, pressure moments |
| Partnership analytics | Stephen Curry | Batting pair analysis |
| Recent form weighting | Stephen Curry | 2024/2025 season emphasis |
| Player comparison tool | Stephen Curry | Side-by-side output |

### Low Priority (Future)
| Task | Owner | Description |
|------|-------|-------------|
| Win probability model | Stephen Curry | Match state predictions |
| Broadcast graphics export | Brock Purdy | JSON/CSV for graphics |
| Dashboard UI | TBD | Web interface |
| API endpoint | Brock Purdy | REST API |

---

## Sprint Metrics

| Sprint | Tasks | Key Deliverables |
|--------|-------|------------------|
| v1.0 | 5 | Data pipeline, 9,357 matches |
| v2.0 | 6 | 231 players, 26 views, stat packs |
| v2.1 | 9 | 34 views, 65 tests, CLI |
| v2.2 | 7 | 10 archetypes, clustering model |
| **Total** | **27** | |

---

## Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Smoke Tests | 65/65 | PASS |
| Schema Validations | 33/33 | PASS |
| Bowling Coverage | 98.8% | PASS |
| Analytics Views | 34 | ACTIVE |
| Stat Packs | 10/10 | GENERATED |

---

## Next Steps (Tom Brady Recommendation)

### Immediate
1. **User Review** - Approve/modify Andy Flower's cluster archetypes
2. **Integrate Classifications** - Add archetypes to stat pack player tables
3. **Squad Balance** - Per-team archetype distribution analysis

### Short-term (v2.3)
4. Venue name normalization
5. Partnership analytics
6. Recent form weighting

### Medium-term (v2.4)
7. Situational analysis (chase/set, pressure)
8. Broadcast export formats

---

## Team Status

| Agent | Role | Availability |
|-------|------|--------------|
| Tom Brady | Product Owner | Available |
| Stephen Curry | Analytics Lead | Available |
| Andy Flower | Cricket Advisor | Awaiting feedback |
| Brock Purdy | Data Pipeline | Available |
| N'Golo Kanté | QA | Available |
| Brad Stevens | Performance | On standby |

---

*Cricket Playbook v2.2.0 - IPL 2026 Analytics Platform*
*Maintained by Tom Brady, Product Owner*
