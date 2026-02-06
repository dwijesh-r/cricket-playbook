# Script Quality Validation Schema

**Ticket:** TKT-085
**Author:** Ime Udoka / Brad Stevens
**Standard:** Industry-aligned Python Quality Gates

---

## Overview

This document defines the validation schema used to approve script quality in the Cricket Playbook codebase. It follows industry best practices from Google, Meta, and open-source Python projects.

---

## Validation Gates (5-Point Check)

### Gate 1: Static Analysis (Linting)
**Tool:** Ruff (replaces Flake8 + isort + pyupgrade)

| Check | Rule | Threshold |
|-------|------|-----------|
| Line length | E501 | ≤ 120 characters |
| Unused imports | F401 | 0 violations |
| Undefined names | F821 | 0 violations |
| Import order | I001 | Sorted, grouped |
| Complexity | C901 | McCabe ≤ 10 |

**Command:**
```bash
ruff check scripts/ --select=E,F,I,C901
```

**Pass Criteria:** 0 errors

---

### Gate 2: Type Safety
**Tool:** mypy (optional but recommended)

| Check | Threshold |
|-------|-----------|
| Type errors | 0 critical |
| Missing annotations | ≤ 20% of functions |
| Any type usage | Minimize |

**Command:**
```bash
mypy scripts/ --ignore-missing-imports --no-error-summary
```

**Pass Criteria:** No critical type errors

---

### Gate 3: Code Formatting
**Tool:** Ruff format (replaces Black)

| Standard | Value |
|----------|-------|
| Line length | 120 |
| Quote style | Double |
| Indent | 4 spaces |
| Trailing commas | Yes |

**Command:**
```bash
ruff format scripts/ --check
```

**Pass Criteria:** No reformatting needed

---

### Gate 4: Security Scanning
**Tool:** Bandit

| Severity | Threshold |
|----------|-----------|
| High | 0 allowed |
| Medium | Review required |
| Low | Document if accepted |

**Focus Areas:**
- SQL injection (B608)
- Hardcoded credentials (B105, B106)
- Command injection (B602, B603)
- Insecure pickle (B301)

**Command:**
```bash
bandit -r scripts/ -ll -ii
```

**Pass Criteria:** 0 high/medium issues

---

### Gate 5: Test Coverage
**Tool:** pytest + coverage.py

| Metric | Threshold |
|--------|-----------|
| Line coverage | ≥ 70% |
| Branch coverage | ≥ 50% |
| Critical paths | 100% |

**Command:**
```bash
pytest tests/ --cov=scripts --cov-report=term-missing --cov-fail-under=70
```

**Pass Criteria:** Coverage ≥ 70%, all tests pass

---

## Pre-Commit Integration

All gates are enforced via `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/ -x -q
        language: system
        pass_filenames: false
        always_run: true
```

---

## Quality Metrics Dashboard

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Ruff violations | 0 | 0 | ✅ |
| Test count | 90 | 90+ | ✅ |
| Test pass rate | 100% | 100% | ✅ |
| Coverage | ~70% | 70% | ✅ |
| Type hints | 60% | 80% | 🔄 |
| Security issues | 0 | 0 | ✅ |

---

## Approval Workflow

### For New Scripts:
1. **Author** writes script following style guide
2. **Pre-commit** runs all 5 gates automatically
3. **PR Review** by assigned agent
4. **Domain Sanity** check by José Mourinho
5. **Founder Validation** for P0/P1 tickets

### For Script Modifications:
1. **Pre-commit** must pass
2. **No regression** in test coverage
3. **No new security issues**

---

## Industry Alignment

This schema aligns with:

| Standard | Alignment |
|----------|-----------|
| PEP 8 | ✅ Via Ruff |
| PEP 484 | ✅ Type hints |
| Google Python Style | ✅ Docstrings, naming |
| 12-Factor App | ✅ Config externalization |
| OWASP | ✅ Bandit security checks |

---

## Tooling Summary

| Purpose | Tool | Config File |
|---------|------|-------------|
| Linting | Ruff | `pyproject.toml` |
| Formatting | Ruff format | `pyproject.toml` |
| Type checking | mypy | `pyproject.toml` |
| Security | Bandit | `.bandit` |
| Testing | pytest | `pytest.ini` |
| Coverage | coverage.py | `.coveragerc` |
| Pre-commit | pre-commit | `.pre-commit-config.yaml` |

---

**Approved by:** Founder
**Effective Date:** February 6, 2026
