# CI/CD and Codebase Maintenance Best Practices

**Author:** Brad Stevens (Requirements & Architecture Reviewer)
**Requested by:** Tom Brady (Product Owner)
**Date:** 2026-01-24
**Project:** Cricket Playbook - IPL 2026 Analytics Platform

---

## Executive Summary

This document provides comprehensive CI/CD and codebase maintenance recommendations for the Cricket Playbook project. After reviewing the current project structure, existing workflows, and industry best practices for data/analytics projects, I present prioritized recommendations with implementation guidance.

**Key Findings:**
- Current CI/CD is minimal (single manual ingest workflow)
- No automated testing in CI pipeline
- No code quality tools configured
- ML model versioning partially implemented but not integrated into CI
- Strong existing test suite (65 tests) not leveraged in automation

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [CI/CD Pipeline Recommendations](#2-cicd-pipeline-recommendations)
3. [Code Quality Tools](#3-code-quality-tools)
4. [Testing Strategy](#4-testing-strategy)
5. [Documentation Standards](#5-documentation-standards)
6. [Version Control Practices](#6-version-control-practices)
7. [Data Validation Pipelines](#7-data-validation-pipelines)
8. [Model Versioning and MLOps](#8-model-versioning-and-mlops)
9. [Sample GitHub Actions Workflows](#9-sample-github-actions-workflows)
10. [Implementation Priority & Effort](#10-implementation-priority--effort)

---

## 1. Current State Assessment

### Project Overview

| Attribute | Current State |
|-----------|---------------|
| **Language** | Python 3.12 |
| **Database** | DuckDB (embedded OLAP) |
| **Data Source** | Cricsheet (ball-by-ball JSON) |
| **Total Scripts** | 16 Python scripts |
| **Test Coverage** | 65 pytest tests (single file) |
| **Analytics Views** | 34 DuckDB views |
| **ML Models** | 1 active (K-means clustering v2) |

### Current CI/CD Configuration

**File:** `.github/workflows/ingest.yml`

| Aspect | Assessment |
|--------|------------|
| **Trigger** | Manual only (`workflow_dispatch`) |
| **Testing** | None in pipeline |
| **Linting** | None |
| **Type Checking** | None |
| **Artifacts** | Database + manifest uploaded |
| **Caching** | pip dependencies cached |

**Strengths:**
- Clean workflow structure
- Proper artifact management
- Good use of GitHub Step Summary

**Gaps:**
- No automated triggers (push/PR)
- No test execution
- No code quality gates
- No dependency vulnerability scanning
- No multi-stage pipeline

---

## 2. CI/CD Pipeline Recommendations

### 2.1 Multi-Stage Pipeline Architecture

```
Stage 1: Lint & Format (< 1 min)
    |
Stage 2: Type Check (< 2 min)
    |
Stage 3: Unit Tests (< 3 min)
    |
Stage 4: Integration Tests (< 5 min)
    |
Stage 5: Data Validation (< 5 min)
    |
Stage 6: Build Artifacts (conditional)
```

### 2.2 Trigger Strategy

| Event | Pipeline Stages | Notes |
|-------|-----------------|-------|
| `push` to feature branches | 1-4 | Fast feedback |
| `pull_request` to main | 1-5 | Full validation |
| `push` to main | 1-6 | Deploy artifacts |
| `workflow_dispatch` | Full ingest | Manual data refresh |
| `schedule` (weekly) | Full ingest | Keep data current |

### 2.3 Branch Protection Rules

Configure the following for `main` branch:

- Require pull request reviews (1 reviewer)
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Required status checks: `lint`, `typecheck`, `test`

---

## 3. Code Quality Tools

### 3.1 Recommended Tool Stack

| Tool | Purpose | Configuration File |
|------|---------|-------------------|
| **Ruff** | Linting + Formatting | `pyproject.toml` |
| **mypy** | Static type checking | `pyproject.toml` |
| **pre-commit** | Git hooks | `.pre-commit-config.yaml` |
| **bandit** | Security linting | `pyproject.toml` |

### 3.2 Ruff Configuration

```toml
[tool.ruff]
target-version = "py312"
line-length = 100
src = ["scripts", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 3.3 Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

---

## 4. Testing Strategy

### 4.1 Test Pyramid

```
              /\
             /  \  E2E Tests (Stat Pack Generation)
            /    \
           /------\
          /        \
         /  Integra-\  Integration Tests (Database)
        /    tion    \
       /--------------\
      /                \
     /    Unit Tests    \
    /--------------------\
```

### 4.2 Recommended Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_transformations.py
│   └── test_clustering.py
├── integration/
│   ├── test_database.py
│   └── test_views.py
└── e2e/
    └── test_stat_pack_generation.py
```

### 4.3 Test Markers

```toml
[tool.pytest.ini_options]
markers = [
    "unit: fast tests without I/O",
    "integration: database required",
    "e2e: full pipeline tests",
]
```

---

## 5. Version Control Practices

### 5.1 Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `data/` - Data updates
- `docs/` - Documentation

### 5.2 Commit Message Standards (Conventional Commits)

```
feat(clustering): add batting position feature
fix(stats): correct Kohli career runs calculation
data(squads): add missing RCB players
docs(readme): update analytics views section
```

### 5.3 Semantic Versioning

- **MAJOR (X.0.0)**: Breaking schema changes
- **MINOR (0.X.0)**: New features, views, models
- **PATCH (0.0.X)**: Bug fixes, data corrections

---

## 6. Model Versioning and MLOps

### 6.1 Model Serialization

```python
import joblib
from pathlib import Path

def save_model(model, model_name: str, version: str):
    models_dir = Path("ml_ops/models")
    models_dir.mkdir(exist_ok=True)

    filepath = models_dir / f"{model_name}_v{version}.joblib"
    joblib.dump({
        "model": model,
        "version": version,
        "features": getattr(model, 'feature_names_in_', None),
    }, filepath)
    return filepath
```

### 6.2 Enhanced Model Registry

```json
{
  "models": {
    "player_clustering_v2": {
      "version": "2.0.0",
      "status": "active",
      "metrics": {
        "silhouette_score": 0.42,
        "pca_variance": 0.836
      },
      "validation": {
        "andy_flower_approved": true
      }
    }
  }
}
```

---

## 7. Sample CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff
      - run: ruff check scripts/ tests/
      - run: ruff format --check scripts/ tests/

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements.txt pytest
      - run: pytest tests/ -v --tb=short
```

---

## 8. Implementation Priority

| Priority | Item | Effort |
|----------|------|--------|
| **P0** | Add CI workflow with linting | Low |
| **P0** | Add tests to CI pipeline | Low |
| **P1** | Configure Ruff + pre-commit | Medium |
| **P1** | Restructure test directory | Low |
| **P2** | Add mypy to CI | Low |
| **P2** | Enable branch protection | Low |
| **P2** | Add model serialization | Medium |
| **P3** | Add Great Expectations | High |
| **P3** | Create release workflow | Low |

### 30-Day Roadmap

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | CI Foundation | `ci.yml`, Ruff, pre-commit |
| 2 | Testing | Test restructure, markers, coverage |
| 3 | Quality Gates | mypy, branch protection, PR template |
| 4 | MLOps | Model serialization, enhanced registry |

**Estimated Total Effort:** 40-50 developer hours over 4 weeks

---

*Brad Stevens*
*Requirements & Architecture Reviewer*
*Cricket Playbook - IPL 2026 Analytics Platform*
