# Neon Migration Plan

**Status:** Planning
**Owner:** Brad Stevens (Architecture), Brock Purdy (Data Pipeline)
**Created:** 2026-03-09

## Overview

Migration from fully static JS data delivery (GitHub Pages) to a hybrid architecture using Neon serverless Postgres as the data and application layer. StatSledge remains on GitHub Pages; Neon handles structured data queries, bug reports, and future interactive features.

## Documents

| Document | Purpose |
|----------|---------|
| [Architecture](ARCHITECTURE.md) | Current vs. target architecture, system diagrams |
| [Phase 1: Bug Reports](PHASE_1_BUG_REPORTS.md) | Replace Web3Forms with Neon (quick win) |
| [Phase 2: Data Offload](PHASE_2_DATA_OFFLOAD.md) | Move heavy JS files to on-demand Neon queries |
| [Phase 3: SQL Lab](PHASE_3_SQL_LAB.md) | Interactive SQL Lab powered by Neon |
| [Schema Design](SCHEMA_DESIGN.md) | Full Postgres schema (reports, cricket, app) |
| [Security](SECURITY.md) | Role-based access, row-level security, connection strategy |
| [Migration Runbook](MIGRATION_RUNBOOK.md) | Step-by-step execution checklist |

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-09 | Neon over Supabase/PlanetScale | Serverless HTTP driver works from static sites, generous free tier (0.5GB), branching |
| 2026-03-09 | Phased migration, not big-bang | Minimize risk, validate each layer before proceeding |
| 2026-03-09 | Keep small static JS files | teams.js (4KB), predicted_xii.js (20KB) are fast enough as static; not worth query overhead |
