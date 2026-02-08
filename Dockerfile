# ============================================================
# Cricket Playbook - Dockerfile
# TKT-154: Containerized analytics environment
# ============================================================
# Build:  docker build -t cricket-playbook .
# Run:    docker run -v ./data:/app/data -v ./outputs:/app/outputs cricket-playbook
# ============================================================

FROM python:3.9-slim

# --- System dependencies ---
# gcc and python3-dev are needed for compiling native extensions
# (scipy, scikit-learn wheels may need them on slim images)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# --- Working directory ---
WORKDIR /app

# --- Install Python dependencies first (layer caching) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy project source ---
COPY pyproject.toml .
COPY scripts/ scripts/
COPY config/ config/
COPY stat_packs/ stat_packs/
COPY ml_ops/ ml_ops/
COPY tests/ tests/
COPY analysis/ analysis/

# --- Create mount-point directories ---
# These will be overlaid by volume mounts at runtime, but we
# create them so the container works even without mounts.
RUN mkdir -p /app/data /app/outputs

# --- Environment defaults ---
# Paths inside the container (align with config.py env-var support)
ENV DATA_DIR=/app/data \
    OUTPUT_DIR=/app/outputs \
    DB_PATH=/app/data/cricket_playbook.duckdb \
    CONFIG_DIR=/app/config \
    LOG_LEVEL=normal \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- Default entrypoint: run Great Expectations validation ---
CMD ["python", "scripts/core/ge_validation.py"]
