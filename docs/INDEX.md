# Cricket Playbook Document Index

**Last Updated:** 2026-02-04

---

## Quick Navigation

### Governance Documents
- [Constitution v2.0](../config/CONSTITUTION.md) - Binding governance framework
- [CLAUDE.md](../CLAUDE.md) - AI assistant operating principles
- [Task Integrity Loop](../governance/TASK_INTEGRITY_LOOP.md) - Process enforcement
- [PRD](./PRD_CRICKET_PLAYBOOK.md) - Product requirements document

### Sprint Documentation
- [Sprint 4 Status](./sprints/SPRINT_4_STATUS_020426.md) - **Current status (2026-02-04)**
- [Sprint 4 Plan](./SPRINT_4_PLAN.md) - Sprint plan and task breakdown
- [Archived Kanban (Sprint 3)](./archive/KANBAN_sprint_3_012626_v1.md) - Historical reference

*Note: Review 5 and Mega Review 1 action plans have been incorporated into Sprint 4 and archived.*

### Founder Reviews
- [Sprint 4 Check-In Response](../reviews/founder/sprint_4_checkin_response_020426_v1.md) - Latest
- [Mission Control PRD](../reviews/founder/Mission%20Control%20PRD%20Draft.md) - Infrastructure PRD
- [Review 5](../reviews/founder/review_5.pdf)
- [Mega Review 1](../reviews/founder/mega_review_1.pdf)

### Analytics Documentation
- [Threshold EDA](../analysis/threshold_eda_2023.md) - Statistical thresholds analysis
- [Player ID Audit](../analysis/player_id_audit_report.md) - ID mismatch report
- [Entry Point Audit](../analysis/entry_point_audit_report.md) - Batter positions
- [Baselines vs Tags](../analysis/baselines_vs_tags.md) - Methodology explanation

### Specifications
- [Player Clustering PRD](./specs/player_clustering_prd.md) - Clustering methodology
- [Cluster Labels v1.0](./specs/cluster_labels_v1.0.md) - Label definitions

### Research
- [KenPom Methodology](./research/kenpom_methodology_research.md) - Rating system research
- [PFF Grading System](./research/pff_grading_system_research.md) - Grading research

### Agent Configurations
- [Agent Directory](../config/agents/) - All 14 agent personas

### Domain Reviews (Current)
- [Andy Flower Analytics Research](../reviews/domain/andy_flower_analytics_research.md) - Comprehensive analytics review
- [Andy Flower Tag Validation](../reviews/domain/andy_flower_tag_validation.md) - Tag system validation
- [Phase Metrics Review](../reviews/domain/phase_metrics_review.md) - Phase-based metrics analysis
- [Phase Tag Criteria](../reviews/domain/phase_tag_criteria.md) - Tag threshold definitions
- [Tag Standardization Audit](../reviews/domain/tag_standardization_audit.md) - Tag consistency audit

---

## Archive
- [Archive Directory](../archive/) - Historical files organized by date

---

## Output Directories

| Directory | Contents |
|-----------|----------|
| `outputs/tags/` | Player classification tags |
| `outputs/matchups/` | Head-to-head analysis |
| `outputs/metrics/` | Performance metrics |
| `outputs/predicted_xii/` | Algorithm-generated XIs |
| `outputs/depth_charts/` | Position rankings |
| `stat_packs/` | Team stat packs (10 teams) |

---

## Scripts

| Directory | Purpose |
|-----------|---------|
| `scripts/core/` | Data pipeline (ingest, analytics, validation) |
| `scripts/generators/` | Output file generators |
| `scripts/analysis/` | Player analysis scripts |
| `scripts/utils/` | Utility functions |
| `scripts/archive/` | Deprecated scripts |

---

## Data Directory

| File/Directory | Contents |
|----------------|----------|
| `data/cricket_playbook.duckdb` | Main analytics database (159MB) |
| `data/ipl_2026_squads.csv` | Current team rosters (231 players) |
| `data/ipl_2026_player_contracts.csv` | Contract information |
| `data/bowler_classifications_v3.csv` | Current bowler type classifications |
| `data/raw/` | Cricsheet source data (18 ZIP files) |
| `data/processed/` | Intermediate processed files |
| `data/archive/` | Old data versions |

---

*Cricket Playbook v4.0.0*
*Index reorganized: 2026-02-04*
