# GitHub Workflows

CI/CD automation for Cricket Playbook.

---

## Workflows

### `ci.yml` - Continuous Integration

**Triggers:** Push to `main`, Pull Requests to `main`

**Jobs:**
1. **lint-and-test**
   - Checkout code
   - Setup Python 3.12
   - Cache pip dependencies
   - Install requirements
   - Run Ruff linter (`ruff check .`)
   - Run Ruff formatter check (`ruff format --check .`)
   - Run pytest (`pytest tests/ -v`)

**Status Badge:**
```markdown
![CI](https://github.com/dwijesh-r/cricket-playbook/actions/workflows/ci.yml/badge.svg)
```

---

### `ingest.yml` - Data Ingestion (Manual)

**Triggers:** Manual (`workflow_dispatch`)

**Purpose:** Run data ingestion pipeline to load new Cricsheet data.

**Note:** This workflow is typically run manually when new match data is available.

---

## Local Development

To run the same checks locally:

```bash
# Linting
ruff check .

# Format check
ruff format --check .

# Auto-fix formatting
ruff format .

# Run tests
pytest tests/ -v
```

---

## Pre-commit Hooks

The repository uses pre-commit hooks that mirror CI checks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
```

Install hooks:
```bash
pre-commit install
```

---

## Required Secrets

| Secret | Purpose |
|--------|---------|
| (none currently) | No secrets required for CI |

---

## Adding New Workflows

1. Create new `.yml` file in `.github/workflows/`
2. Follow existing patterns for Python setup and caching
3. Document in this README
4. Test with a PR before merging

---

*Cricket Playbook v4.0.0*
