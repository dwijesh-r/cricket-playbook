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

The repository uses pre-commit hooks that mirror CI checks and enforce project standards.

### Standard Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff          # Linting with auto-fix
      - id: ruff-format   # Code formatting
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files  # Blocks files > 500KB
```

### Custom Hooks

#### Document Naming Convention (P3-01)

**Location:** `scripts/hooks/check_naming_convention.py`

**Purpose:** Validates document naming convention for files in monitored directories.

**Naming Convention:** `documentname_MMDDYY_v*.md/pdf`
- Pattern: `^[a-z0-9_]+_\d{6}_v\d+\.(md|pdf)$`
- All lowercase with underscores
- Date in MMDDYY format
- Version suffix (e.g., `_v1`, `_v2`)

**Monitored Directories:**
- `reviews/founder/`
- `reviews/sprint/`
- `docs/sprints/`

**Examples:**
| Filename | Status | Reason |
|----------|--------|--------|
| `sprint_4_checkin_response_020426_v1.md` | PASS | Correct format |
| `founder_review_013026_v1.pdf` | PASS | Correct format |
| `review_1.pdf` | FAIL | No date/version |
| `SPRINT_4_STATUS.md` | FAIL | Uppercase, no date |

**Exempt Files:**
- `README.md`
- `.gitkeep`
- Config files (starting with `.`)

**Behavior:** WARNING only (non-blocking) - commits proceed but warnings are displayed.

#### Large File Prevention (P3-03)

**Purpose:** Prevents accidental commits of large files (> 500KB).

**Blocked file types:**
- `*.csv` (data files)
- `*.duckdb` (database files)
- `*.pkl` (model files)

**Whitelisted file types:**
- `*.md` (documentation can be large)
- `*.pdf` (founder reviews)

**Behavior:** BLOCKING - commits are rejected for large files.

### Install Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files (optional)
pre-commit run --all-files

# Run specific hook
pre-commit run check-naming-convention --all-files
```

### Test Custom Hooks Manually

```bash
# Test naming convention hook
python scripts/hooks/check_naming_convention.py docs/sprints/test_file.md

# Test with multiple files
python scripts/hooks/check_naming_convention.py \
  docs/sprints/sprint_4_status_020426_v1.md \
  reviews/founder/founder_review_013026_v1.pdf
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
