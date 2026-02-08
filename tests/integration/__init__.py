"""
TKT-139: Integration Tests for Cricket Playbook Data Pipeline
==============================================================

This package contains integration tests that validate the complete data pipeline
from ingestion through analytics generation and output.

Test Categories:
- IngestFlow: Tests for data ingestion from JSON to DuckDB
- AnalyticsFlow: Tests for analytics view generation and metrics
- StatPackGeneration: Tests for stat pack output structure
- ClusteringPipeline: Tests for K-means clustering stability

Usage:
    pytest tests/integration/ -v -m integration

Author: Cricket Playbook Team
"""
