# StatSledge Infrastructure Upgrade Proposal

**Prepared by:** Brad Stevens (Architecture), Brock Purdy (Data Pipeline)
**Date:** March 9, 2026
**Status:** Ready for Review

---

## The Problem

StatSledge currently delivers all analytical data by embedding it directly into the website files. This worked well during development, but we're hitting real limits as the platform matures:

**1. Heavy page loads**
Every visitor downloads ~7.8 MB of data upfront, even if they only want to look at one team or one matchup. On mobile, this means slow load times and wasted bandwidth.

**2. Bug reports are limited**
Our current reporting tool (Web3Forms) caps us at 250 submissions per month, doesn't store reports in a searchable format, and provides no way to track whether issues were resolved.

**3. No interactive querying**
The SQL Lab feature loads a 31 MB file into the browser to simulate database queries. It's slow, limited to a subset of data, and crashes on some devices.

**4. Every update requires a full rebuild**
Even a small data correction triggers a complete regeneration of all data files and a full site redeploy.

---

## The Solution

Add a lightweight cloud database (Neon Serverless Postgres) alongside our existing setup. StatSledge stays on GitHub Pages — the site itself doesn't move. We're adding a data layer that lets the dashboard pull specific data on demand instead of loading everything at once.

**Think of it like this:**
- **Today:** The entire encyclopedia ships to your doorstep every time you want to look up one article.
- **After:** You search for the article you need and only that article loads.

---

## What Changes for Users

| Today | After Upgrade |
|-------|--------------|
| ~8 seconds to load dashboard (mobile) | ~2 seconds — loads only what's needed |
| Bug reports limited to 250/month | Unlimited reports, tracked with status updates |
| SQL Lab crashes on some devices | Runs real queries against the full dataset |
| No way to check if a reported bug was fixed | Reports show open/reviewed/resolved status |

---

## Phased Rollout

We're splitting this into three independent phases. Each phase delivers value on its own, and we can pause between phases if needed.

### Phase 1: Bug Reports (1-2 hours)

Replace the current bug report form backend with our own database. This gives us:
- Unlimited submissions (no monthly cap)
- Every report stored and searchable
- Status tracking: open → reviewed → resolved
- Foundation for all future database work

**Risk:** Near zero. If anything goes wrong, we revert to the current system in minutes.

---

### Phase 2: Data Offload (3-5 hours)

Move the largest data files out of the site and into on-demand database queries:

| What Moves | Current Size | After |
|------------|-------------|-------|
| Head-to-Head matchup data | 6.0 MB (always loaded) | Fetched per matchup (~2 KB each) |
| Player comparison data | 741 KB (always loaded) | Fetched per comparison (~1 KB each) |
| Player profiles | 509 KB (always loaded) | Fetched per player (~1 KB each) |
| Team rankings | 177 KB (always loaded) | Fetched on page load (~5 KB) |
| Squad rosters | 107 KB (always loaded) | Fetched per team (~2 KB each) |

**Result:** Browser goes from loading ~7.8 MB upfront to ~370 KB. Everything else loads on demand.

**What stays as-is:** Team configurations (4 KB), predicted XIs (20 KB), depth charts (85 KB), and season previews (156 KB) — these are small enough that moving them adds complexity without meaningful benefit.

---

### Phase 3: SQL Lab Upgrade (2-3 hours)

Replace the browser-based query simulator with real database queries. Users get:
- Full dataset access (not a limited export)
- Fast query execution (server-side, not in-browser)
- Ability to save and share queries
- No more 31 MB download or browser crashes

---

## What Stays the Same

- **The website stays on GitHub Pages** — no hosting migration
- **The daily data pipeline continues** — same Cricsheet source, same processing
- **All existing pages and features work identically** — this is invisible to users unless they notice faster load times
- **No user accounts or authentication** — StatSledge remains open and public

---

## Cost

| | Today | After |
|--|-------|-------|
| Hosting | Free (GitHub Pages) | Free (GitHub Pages) |
| Database | None | Free (Neon free tier: 0.5 GB) |
| Bug reports | Free (Web3Forms, 250/mo limit) | Free (unlimited, stored in database) |
| **Total** | **$0/month** | **$0/month** |

Our data footprint is approximately 160 MB, well within Neon's free tier of 500 MB. If usage grows significantly (unlikely for IPL-only data), the paid tier is $19/month.

---

## Timeline

| Phase | Effort | Can Ship By |
|-------|--------|-------------|
| Phase 1: Bug Reports | 1-2 hours | Same day |
| Phase 2: Data Offload | 3-5 hours | Within a week |
| Phase 3: SQL Lab | 2-3 hours | Within two weeks |

Total engineering effort: ~8-10 hours across all three phases.

---

## Why Neon?

We evaluated several options. Neon was chosen because:

1. **Works with static sites** — Its serverless driver communicates over standard web requests, meaning our GitHub Pages site can query it directly without needing a backend server.
2. **Generous free tier** — 500 MB storage and 191 compute hours/month, more than enough for our use case.
3. **Zero maintenance** — Automatically scales down when not in use, scales up when queries come in. No servers to manage.
4. **Database branching** — We can test schema changes on a branch without touching production data, similar to how we use Git branches for code.

---

## Decision Needed

Approve phased rollout starting with Phase 1 (bug reports). This is a low-risk, high-value starting point that also validates the infrastructure for later phases.

---

*Questions? Reach out to Brad Stevens (Architecture) or Brock Purdy (Data Pipeline).*
