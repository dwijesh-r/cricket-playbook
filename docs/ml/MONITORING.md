# Model Monitoring Documentation

**Owner:** Ime Udoka (MLOps Lead)
**Last Updated:** February 7, 2026
**Version:** 1.0.0
**Ticket:** TKT-073

---

## Overview

The Model Monitoring module provides real-time observability for Cricket Playbook's machine learning models. It tracks model health, detects feature drift, validates statistical assumptions, and generates comprehensive health reports.

### Key Capabilities

- **Cluster Distribution Tracking** - Monitor cluster sizes over time to detect population shifts
- **Feature Drift Detection** - Compare current feature distributions against baselines using KS tests
- **PCA Variance Validation** - Ensure dimensionality reduction meets quality thresholds
- **Prediction Metrics Logging** - Track prediction counts, latency, and success rates
- **Health Report Generation** - Create summary reports for operational monitoring

---

## Architecture

```
scripts/ml_ops/
├── __init__.py              # Package initialization
└── model_monitoring.py      # Core ModelMonitor class

outputs/monitoring/
├── model_metrics.json       # Exported metrics
└── health_reports/          # Generated health reports
    └── health_report_YYYYMMDD_HHMMSS.json
```

---

## Metrics Tracked

### 1. Cluster Distribution

Tracks the distribution of players across clusters for both batter and bowler models.

| Metric | Description | Update Frequency |
|--------|-------------|------------------|
| `cluster_sizes` | Count of players per cluster | Per model run |
| `total_players` | Total players in clustering | Per model run |
| `player_type` | 'batter' or 'bowler' | Per model run |

### 2. Feature Drift

Monitors statistical drift in input features compared to baseline distributions.

| Metric | Description | Method |
|--------|-------------|--------|
| `ks_statistic` | Kolmogorov-Smirnov test statistic | Two-sample KS test |
| `p_value` | Statistical significance | KS test p-value |
| `is_drifted` | Boolean drift flag | KS > threshold |
| `baseline_mean/std` | Baseline distribution stats | Historical data |
| `current_mean/std` | Current distribution stats | Recent data |

### 3. PCA Variance

Validates that principal component analysis meets variance thresholds.

| Metric | Description | Source |
|--------|-------------|--------|
| `variance_explained` | Cumulative variance ratio | sklearn PCA |
| `player_type` | Model type for threshold selection | Input parameter |

### 4. Prediction Metrics

Tracks prediction performance and latency.

| Metric | Description | Unit |
|--------|-------------|------|
| `prediction_count` | Number of predictions | Count |
| `latency_ms` | Prediction time | Milliseconds |
| `success` | Prediction success flag | Boolean |
| `error_message` | Error details if failed | String |

---

## Alert Thresholds and SLAs

### Threshold Configuration

| Metric | Threshold | Alert Level | Rationale |
|--------|-----------|-------------|-----------|
| **PCA Variance (Batters)** | < 70% | CRITICAL | Per ML PRD requirement; ensures features capture sufficient variance |
| **PCA Variance (Bowlers)** | < 50% | CRITICAL | Per ML PRD requirement; bowler features inherently more variable |
| **Cluster Size** | < 10 players | WARNING | Ensures statistical validity of cluster characteristics |
| **Feature Drift (KS)** | > 0.1 | WARNING | Standard drift threshold; indicates distribution shift |
| **Prediction Latency** | > 1000ms | WARNING | Performance degradation indicator |
| **Prediction Latency** | > 5000ms | CRITICAL | Unacceptable user experience |

### Alert Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| `INFO` | Informational event | No action needed |
| `WARNING` | Potential issue detected | Investigate within 24 hours |
| `CRITICAL` | Service degradation or model failure | Immediate investigation required |

### SLA Targets

| Metric | Target | Measurement Period |
|--------|--------|-------------------|
| Model Health | > 99% uptime | Weekly |
| Prediction Latency (P95) | < 1000ms | Daily |
| Feature Drift Alerts | < 2 per week | Weekly |
| PCA Variance Violations | 0 per deployment | Per deployment |

---

## Usage Examples

### Basic Usage

```python
from scripts.ml_ops.model_monitoring import ModelMonitor

# Initialize monitor
monitor = ModelMonitor()

# Track cluster distribution
distribution, alerts = monitor.track_cluster_distribution(
    clustered_df=batter_clusters,
    player_type='batter'
)

# Check PCA variance
pca_alerts = monitor.check_pca_variance(
    variance_explained=0.836,  # 83.6%
    player_type='batter'
)

# Generate health report
report = monitor.generate_health_report()
print(f"Health Status: {report['health_status']}")
```

### Feature Drift Detection

```python
from scripts.ml_ops.model_monitoring import ModelMonitor

monitor = ModelMonitor()

# Set baseline from production data
monitor.set_baseline_features(
    baseline_df=production_features,
    feature_cols=['strike_rate', 'boundary_pct', 'avg_batting_position'],
    model_name='batter_clustering'
)

# Check for drift with new data
drift_results, alerts = monitor.detect_feature_drift(
    current_df=new_features,
    feature_cols=['strike_rate', 'boundary_pct', 'avg_batting_position'],
    model_name='batter_clustering'
)

for result in drift_results:
    if result.is_drifted:
        print(f"DRIFT: {result.feature_name} (KS={result.ks_statistic:.3f})")
```

### Prediction Timing

```python
from scripts.ml_ops.model_monitoring import ModelMonitor, PredictionTimer

monitor = ModelMonitor()

# Time predictions with automatic logging
with PredictionTimer(monitor, 'batter_clustering', len(X)):
    predictions = model.predict(X)

# Metrics are automatically logged when context exits
```

### Custom Thresholds

```python
from scripts.ml_ops.model_monitoring import ModelMonitor, AlertThresholds

# Define custom thresholds
custom_thresholds = AlertThresholds(
    pca_variance_batter=0.75,      # Stricter: 75%
    pca_variance_bowler=0.55,      # Stricter: 55%
    min_cluster_size=15,           # Larger minimum
    feature_drift_ks=0.08,         # More sensitive
    prediction_latency_warning=0.5 # 500ms warning
)

monitor = ModelMonitor(thresholds=custom_thresholds)
```

### Exporting Metrics

```python
from scripts.ml_ops.model_monitoring import ModelMonitor

monitor = ModelMonitor()

# ... perform monitoring activities ...

# Export all metrics to JSON
export_path = monitor.export_metrics()
print(f"Metrics exported to: {export_path}")

# Get recent alerts
critical_alerts = monitor.get_alerts(level=AlertLevel.CRITICAL)
```

---

## Integration with Existing Systems

### Logging Integration

The module integrates with `scripts/utils/logging_config.py` for consistent logging:

```python
from scripts.utils.logging_config import setup_logger

# ModelMonitor uses the shared logging configuration
# All log messages follow the standard format:
# 2026-02-07 10:30:45 | INFO | model_monitoring | Message here
```

### Player Clustering Integration

```python
from scripts.analysis.player_clustering_v2 import cluster_batters_v2
from scripts.ml_ops.model_monitoring import ModelMonitor

# Run clustering
batter_clusters, centers, pca_result = cluster_batters_v2(batter_df, n_clusters=5)

# Monitor results
monitor = ModelMonitor()
monitor.track_cluster_distribution(batter_clusters, 'batter')
monitor.check_pca_variance(
    pca_result['cumulative_variance'][2],  # Variance at 3 components
    'batter'
)
```

---

## Dashboard Integration (Future)

### Planned Dashboard Metrics

| Panel | Metrics | Refresh Rate |
|-------|---------|--------------|
| Health Overview | Status, Alert counts, Uptime | Real-time |
| Cluster Distribution | Cluster sizes, Trends | Hourly |
| Feature Drift | KS statistics, Drift timeline | Daily |
| Prediction Performance | Latency P50/P95/P99, Error rate | Real-time |

### API Endpoints (Planned)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Current health status |
| `/api/v1/metrics/clusters` | GET | Cluster distribution history |
| `/api/v1/metrics/drift` | GET | Feature drift results |
| `/api/v1/alerts` | GET | Recent alerts |

### Integration Options

1. **Grafana** - JSON metrics export compatible
2. **Prometheus** - Planned metrics exporter
3. **DataDog** - Future integration via API
4. **Custom Dashboard** - React/Streamlit integration

---

## Troubleshooting

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| No baseline set | `set_baseline_features()` not called | Set baseline before drift detection |
| Empty cluster history | No tracking calls made | Call `track_cluster_distribution()` |
| Import error | Path not in PYTHONPATH | Add project root to path |

### Debug Mode

```python
import logging
from scripts.ml_ops.model_monitoring import ModelMonitor

# Enable debug logging
monitor = ModelMonitor()
monitor.logger.setLevel(logging.DEBUG)
```

---

## Related Documentation

- [Model Versioning](models/MODEL_VERSIONING.md) - Semantic versioning and lifecycle
- [Quality Gates](validation/quality_gates.md) - Validation requirements
- [Player Clustering PRD](algorithms/player_clustering_prd.md) - Algorithm specification
- [Logging Configuration](../../scripts/utils/logging_config.py) - Shared logging setup

---

## Changelog

### v1.0.0 (2026-02-07)
- Initial release
- Cluster distribution tracking
- Feature drift detection with KS test
- PCA variance validation
- Prediction metrics logging
- Health report generation
- Logging integration with logging_config.py

---

*Ime Udoka - MLOps Lead*
*Cricket Playbook v4.1.0*
