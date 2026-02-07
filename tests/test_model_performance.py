"""
Model Performance Tests for Cricket Playbook
TKT-071: Create model performance tests

Owner: Ime Udoka (MLOps Lead)
Tests: Clustering accuracy, model stability, domain validation

Run with: pytest tests/test_model_performance.py -v
"""

import pytest
import json
from pathlib import Path


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(scope="module")
def model_registry():
    """Load model registry for validation."""
    registry_path = Path("ml_ops/model_registry.json")
    if not registry_path.exists():
        pytest.skip("Model registry not found")
    with open(registry_path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def clustering_config(model_registry):
    """Extract clustering v2.0.0 configuration from registry."""
    return (
        model_registry.get("models", {})
        .get("player_clustering", {})
        .get("versions", {})
        .get("2.0.0", {})
    )


# =============================================================================
# 1. CLUSTERING ACCURACY TESTS
# =============================================================================


class TestClusteringAccuracy:
    """Tests for clustering accuracy metrics."""

    def test_batter_pca_variance_threshold(self, clustering_config):
        """Batter PCA variance (3 components) should exceed 70%."""
        pca = (
            clustering_config.get("model_performance", {})
            .get("pca_variance", {})
            .get("batters", {})
        )
        pca_variance = pca.get("variance_3pc", 0)
        assert pca_variance > 0.70, f"Batter PCA variance {pca_variance:.1%} below 70% threshold"

    def test_bowler_pca_variance_threshold(self, clustering_config):
        """Bowler PCA variance (3 components) should exceed 50%."""
        pca = (
            clustering_config.get("model_performance", {})
            .get("pca_variance", {})
            .get("bowlers", {})
        )
        pca_variance = pca.get("variance_3pc", 0)
        assert pca_variance > 0.50, f"Bowler PCA variance {pca_variance:.1%} below 50% threshold"

    def test_cluster_count_is_five(self, clustering_config):
        """Should have exactly 5 clusters for both batters and bowlers."""
        hyperparams = clustering_config.get("hyperparameters", {})
        n_clusters = hyperparams.get("n_clusters", 0)
        assert n_clusters == 5, f"Expected 5 clusters, got {n_clusters}"

    def test_batter_cluster_labels_defined(self, clustering_config):
        """All 5 batter cluster labels should be defined."""
        labels = clustering_config.get("cluster_labels", {}).get("batters", {})
        assert len(labels) == 5, f"Expected 5 batter labels, got {len(labels)}"


# =============================================================================
# 2. CLUSTER DISTRIBUTION TESTS
# =============================================================================


class TestClusterDistribution:
    """Tests for cluster size distribution."""

    def test_batter_sample_size(self, clustering_config):
        """Batter clustering should have sufficient sample size."""
        outputs = clustering_config.get("outputs", {})
        n_players = outputs.get("batters_clustered", 0)
        assert n_players >= 100, f"Only {n_players} batters clustered (min: 100)"

    def test_bowler_sample_size(self, clustering_config):
        """Bowler clustering should have sufficient sample size."""
        outputs = clustering_config.get("outputs", {})
        n_players = outputs.get("bowlers_clustered", 0)
        assert n_players >= 100, f"Only {n_players} bowlers clustered (min: 100)"


# =============================================================================
# 3. MODEL STABILITY TESTS
# =============================================================================


class TestModelStability:
    """Tests for model reproducibility."""

    def test_random_state_fixed(self, clustering_config):
        """Model should use fixed random_state for reproducibility."""
        hyperparams = clustering_config.get("hyperparameters", {})
        random_state = hyperparams.get("random_state")
        assert random_state == 42, f"random_state should be 42, got {random_state}"

    def test_model_lifecycle_is_production(self, clustering_config):
        """Model lifecycle_stage should be 'production'."""
        lifecycle = clustering_config.get("lifecycle_stage", "")
        assert lifecycle == "production", f"Lifecycle is '{lifecycle}', expected 'production'"

    def test_model_status_is_active(self, clustering_config):
        """Model status should be 'active'."""
        status = clustering_config.get("status", "")
        assert status == "active", f"Status is '{status}', expected 'active'"

    def test_algorithm_is_kmeans(self, clustering_config):
        """Should use K-Means algorithm."""
        hyperparams = clustering_config.get("hyperparameters", {})
        algorithm = hyperparams.get("algorithm", "")
        assert algorithm == "lloyd", f"Algorithm should be 'lloyd' (K-Means), got '{algorithm}'"


# =============================================================================
# 4. FEATURE VALIDATION TESTS
# =============================================================================


class TestFeatureValidation:
    """Tests for feature engineering compliance."""

    def test_batter_features_count(self, clustering_config):
        """Batter clustering should use 8 features (after correlation cleanup)."""
        features = clustering_config.get("features", {}).get("batters", {})
        n_features = features.get("count", 0)
        assert n_features == 8, f"Expected 8 batter features, got {n_features}"

    def test_bowler_features_count(self, clustering_config):
        """Bowler clustering should use 16 features."""
        features = clustering_config.get("features", {}).get("bowlers", {})
        n_features = features.get("count", 0)
        assert n_features == 16, f"Expected 16 bowler features, got {n_features}"

    def test_batter_features_include_position(self, clustering_config):
        """Batter features should include avg_batting_position (v2 addition)."""
        features = clustering_config.get("features", {}).get("batters", {})
        feature_names = features.get("names", [])
        assert "avg_batting_position" in feature_names, "Missing avg_batting_position feature"

    def test_bowler_features_include_wickets(self, clustering_config):
        """Bowler features should include phase wickets (v2 addition)."""
        features = clustering_config.get("features", {}).get("bowlers", {})
        feature_names = features.get("names", [])
        assert "pp_wickets" in feature_names, "Missing pp_wickets feature"
        assert "death_wickets" in feature_names, "Missing death_wickets feature"


# =============================================================================
# 5. REGISTRY SCHEMA TESTS
# =============================================================================


class TestRegistrySchema:
    """Tests for model registry schema compliance."""

    def test_registry_has_schema_version(self, model_registry):
        """Registry should have schema version."""
        meta = model_registry.get("registry_meta", {})
        schema_version = meta.get("schema_version", "")
        assert schema_version, "Missing schema_version in registry"

    def test_registry_schema_is_2_0(self, model_registry):
        """Registry schema should be version 2.0.0."""
        meta = model_registry.get("registry_meta", {})
        schema_version = meta.get("schema_version", "")
        assert schema_version == "2.0.0", f"Expected schema 2.0.0, got {schema_version}"

    def test_registry_has_models(self, model_registry):
        """Registry should have models section."""
        models = model_registry.get("models", {})
        assert models, "Missing models section in registry"

    def test_player_clustering_model_exists(self, model_registry):
        """Player clustering model should exist in registry."""
        models = model_registry.get("models", {})
        assert "player_clustering" in models, "player_clustering model not in registry"

    def test_versioning_policy_exists(self, model_registry):
        """Registry should have versioning policy."""
        policy = model_registry.get("versioning_policy", {})
        assert policy.get("semantic_versioning") is True, "Semantic versioning not enabled"


# =============================================================================
# 6. CLUSTER LABEL VALIDATION
# =============================================================================


class TestClusterLabels:
    """Tests for cluster label definitions."""

    def test_batter_labels_are_meaningful(self, clustering_config):
        """Batter cluster labels should be cricket-meaningful."""
        labels = clustering_config.get("cluster_labels", {}).get("batters", {})
        values = list(labels.values())
        # Check for meaningful names (not just "Cluster 0", etc.)
        assert all("CLUSTER" not in v.upper() or "_" in v for v in values), (
            "Labels should be meaningful"
        )

    def test_bowler_labels_are_meaningful(self, clustering_config):
        """Bowler cluster labels should be cricket-meaningful."""
        labels = clustering_config.get("cluster_labels", {}).get("bowlers", {})
        values = list(labels.values())
        assert all("CLUSTER" not in v.upper() or "_" in v for v in values), (
            "Labels should be meaningful"
        )

    def test_batter_has_finisher_archetype(self, clustering_config):
        """Batter clusters should include a finisher archetype."""
        labels = clustering_config.get("cluster_labels", {}).get("batters", {})
        values = [v.upper() for v in labels.values()]
        assert any("FINISHER" in v or "DEATH" in v for v in values), "Missing finisher archetype"

    def test_bowler_has_death_specialist(self, clustering_config):
        """Bowler clusters should include a death specialist."""
        labels = clustering_config.get("cluster_labels", {}).get("bowlers", {})
        values = [v.upper() for v in labels.values()]
        assert any("DEATH" in v for v in values), "Missing death specialist archetype"
