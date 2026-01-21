# Cricket Playbook - Sprint Kanban

**Last Updated:** 2026-01-21
**Current Version:** v2.3.0
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
| Batter clusters (5 archetypes, 129 players) | Stephen Curry | Andy Flower |
| Bowler clusters (5 archetypes, 206 players) | Stephen Curry | Andy Flower |
| Player Clustering PRD | Tom Brady | APPROVED |
| Squad CSV with classifications | Stephen Curry | Tom Brady |
| Player ID collision fix | Brock Purdy | Tom Brady |
| Elbow curve analysis | Stephen Curry | Tom Brady |

### v2.3 - Multi-Tag Classification (2026-01-21)
| Task | Owner | Sign-off |
|------|-------|----------|
| Player experience CSV (231 players) | Stephen Curry | Tom Brady |
| Enhanced feature extraction (15 dimensions) | Stephen Curry | Andy Flower |
| Batter archetype tags (5 primary) | Andy Flower | Tom Brady |
| Batter secondary tags (9 types) | Andy Flower | Tom Brady |
| Bowler archetype tags (5 primary) | Andy Flower | Tom Brady |
| Bowler secondary tags (6 types) | Andy Flower | Tom Brady |
| Phase specialist detection (PP/Mid/Death) | Stephen Curry | Andy Flower |
| Spin vs Pace matchup analysis | Stephen Curry | Andy Flower |
| Vulnerability tagging | Andy Flower | Tom Brady |
| player_tags.json export | Stephen Curry | Tom Brady |
| Squad CSV with tags (69 batters, 86 bowlers) | Stephen Curry | Tom Brady |

---

## IN PROGRESS

| Task | Owner | Status |
|------|-------|--------|
| Bowler vs LHB/RHB matchup tags | Stephen Curry | In development |

---

## BACKLOG

### High Priority (v2.4)
| Task | Owner | Description |
|------|-------|-------------|
| Integrate tags into stat packs | Stephen Curry | Add archetype + tags to player tables |
| Squad balance analysis | Andy Flower | Team composition by archetype/tags |
| Venue normalization | Brock Purdy | "Arun Jaitley" vs "Feroz Shah Kotla" |
| Recent form weighting | Stephen Curry | 2024/2025 season emphasis |

### Medium Priority (v2.5)
| Task | Owner | Description |
|------|-------|-------------|
| Situational analysis views | Stephen Curry | Chase vs set, pressure moments |
| Partnership analytics | Stephen Curry | Batting pair analysis |
| Player comparison tool | Stephen Curry | Side-by-side output |
| Matchup probability matrix | Stephen Curry | Archetype vs archetype expected performance |

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
| v2.2 | 7 | 10 archetypes, clustering PRD |
| v2.3 | 11 | Multi-tag system, phase specialists |
| **Total** | **38** | |

---

## Quality Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Smoke Tests | 65/65 | PASS |
| Schema Validations | 33/33 | PASS |
| Bowling Coverage | 98.8% | PASS |
| Analytics Views | 34 | ACTIVE |
| Stat Packs | 10/10 | GENERATED |
| Players Tagged | 155 | ACTIVE |

---

## Tagging System Summary (v2.3)

### Batter Tags
| Tag Category | Count | Examples |
|--------------|-------|----------|
| EXPLOSIVE_OPENER | 15 | Jaiswal, Salt, Narine |
| PLAYMAKER | 24 | Kohli, Rahul, Warner |
| ANCHOR | 21 | Dhoni, Dube, Samson |
| FINISHER | 21 | Pandya, Miller, Russell |
| ACCUMULATOR | 49 | Various middle-order |
| PP_DOMINATOR | 12 | High powerplay SR |
| DEATH_SPECIALIST | 8 | High death SR |
| SPIN_SPECIALIST | 15 | SR >130 vs spin |
| PACE_SPECIALIST | 11 | SR >130 vs pace |
| VULNERABLE_VS_SPIN | 6 | SR <105 vs spin |
| VULNERABLE_VS_PACE | 4 | SR <105 vs pace |
| SIX_HITTER | 14 | Six% >8% |

### Bowler Tags
| Tag Category | Count | Examples |
|--------------|-------|----------|
| NEW_BALL_SPECIALIST | 43 | Bumrah, Boult, Starc |
| MIDDLE_OVERS_CONTROLLER | 50 | Rashid, Ashwin, Narine |
| DEATH_SPECIALIST | 19 | Malinga, Bumrah, Archer |
| WORKHORSE | 112 | Shami, Siraj, Chahar |
| PART_TIMER | 44 | All-rounders |
| PP_ELITE | 18 | Top PP economy |
| MID_OVERS_ELITE | 23 | Top mid economy |
| DEATH_ELITE | 14 | Top death economy |
| PRESSURE_BUILDER | 38 | Dot ball% >38% |
| PROVEN_WICKET_TAKER | 12 | 100+ IPL wickets |

---

*Cricket Playbook v2.3.0 - IPL 2026 Analytics Platform*
*Maintained by Tom Brady, Product Owner*
