# Cricket Playbook - Sprint Kanban

**Last Updated:** 2026-01-19
**Sprint:** Foundation Sprint
**Owner:** Tom Brady (Product Owner)

---

## 📋 BACKLOG

| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| External player attributes (LHB/RHB, bowling style) | Brock Purdy | Low | Requires ESPNcricinfo enrichment |
| GitHub Actions for automated ingestion | Brock Purdy | High | `workflow_dispatch` trigger |
| Analytics layer - batting metrics | Stephen Curry | High | SR, average, boundaries |
| Analytics layer - bowling metrics | Stephen Curry | High | Economy, wickets, dot ball % |
| Visualization templates | Kevin De Bruyne | Medium | After analytics ready |
| Editorial templates | LeBron James | Low | Magazine structure |

---

## 🔄 IN PROGRESS

| Task | Owner | Started | Status |
|------|-------|---------|--------|
| - | - | - | - |

---

## ✅ DONE (This Sprint)

| Task | Owner | Completed | Sign-off |
|------|-------|-----------|----------|
| Schema design | Brock Purdy | 2026-01-19 | Tom Brady ✅ |
| Ingestion pipeline (`ingest.py`) | Brock Purdy | 2026-01-19 | Tom Brady ✅ |
| Data load (9,357 matches) | Brock Purdy | 2026-01-19 | N'Golo Kanté ✅ |
| QA certification | N'Golo Kanté | 2026-01-19 | PASS |
| Cricket domain review | Andy Flower | 2026-01-19 | APPROVE w/ caveats |
| Structure review | Tom Brady | 2026-01-19 | APPROVED |
| Git repo setup | - | 2026-01-19 | ✅ |
| Virtual environment + deps | - | 2026-01-19 | ✅ |
| **Add `is_wicketkeeper` flag** | Brock Purdy | 2026-01-19 | Andy Flower ✅ |
| **Add `match_phase` column** | Brock Purdy | 2026-01-19 | Andy Flower ✅ |

---

## 🚫 BLOCKED

| Task | Owner | Blocker | Resolution Needed |
|------|-------|---------|-------------------|
| - | - | - | - |

---

## 📊 Sprint Metrics

| Metric | Value |
|--------|-------|
| Tasks Completed | 8 |
| Tasks In Progress | 0 |
| Tasks Blocked | 0 |
| Tasks in Backlog | 8 |

---

## 🎯 Sprint Goals

### Foundation Sprint (Current)
- [x] Data ingestion pipeline
- [x] Schema design and implementation
- [x] QA certification
- [x] Domain review
- [ ] GitHub Actions setup

### Next Sprint: Analytics
- [ ] Core batting metrics
- [ ] Core bowling metrics
- [ ] Player comparison views
- [ ] Sample visualizations

---

## 📝 Notes

**Tom Brady's Assessment (2026-01-19):**

> Excellent progress on the foundation sprint. We've gone from zero to a fully operational data pipeline in one session. The schema is solid, QA-certified, and cricket-approved.
>
> Key wins:
> - 9,357 matches loaded with full ball-by-ball granularity
> - Derived player roles working (with noted caveats)
> - Clean separation of concerns across agents
>
> Concerns:
> - 68 JSON parse errors need investigation (low priority)
> - External enrichment (batting style, etc.) deferred - acceptable for now
>
> Next priority: GitHub Actions for reproducible, automated ingestion. Then hand off to Stephen Curry for analytics layer.

---

*Maintained by Tom Brady, Product Owner & Editor-in-Chief*
