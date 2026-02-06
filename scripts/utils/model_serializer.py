#!/usr/bin/env python3
"""
Cricket Playbook - Model Serialization Module
Author: Ime Udoka (DevOps Engineer)

Provides functionality to save and load trained ML models using joblib
for reproducibility and efficient inference without retraining.

Features:
- Save trained models with metadata (training date, parameters, version)
- Load models for inference without retraining
- Model versioning and registry integration
- Validation of loaded models
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
MODELS_DIR = PROJECT_DIR / "models"
ML_OPS_DIR = PROJECT_DIR / "ml_ops"
MODEL_REGISTRY_PATH = ML_OPS_DIR / "model_registry.json"


class ModelSerializer:
    """Handles serialization and deserialization of ML models with metadata."""

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize the ModelSerializer.

        Args:
            models_dir: Directory to store serialized models.
                       Defaults to PROJECT_DIR/models/
        """
        self.models_dir = models_dir or MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def save_model(
        self,
        model: Any,
        model_name: str,
        version: str,
        scaler: Optional[Any] = None,
        feature_names: Optional[list] = None,
        hyperparameters: Optional[dict] = None,
        metrics: Optional[dict] = None,
        additional_metadata: Optional[dict] = None,
    ) -> Path:
        """
        Save a trained model with metadata using joblib.

        Args:
            model: The trained model object (e.g., KMeans)
            model_name: Name identifier for the model (e.g., "batter_clustering")
            version: Semantic version string (e.g., "2.0.0")
            scaler: Optional StandardScaler or other preprocessing object
            feature_names: List of feature names used for training
            hyperparameters: Dictionary of hyperparameters used
            metrics: Dictionary of performance metrics
            additional_metadata: Any additional metadata to store

        Returns:
            Path to the saved model file
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Create model bundle with metadata
        model_bundle = {
            "model": model,
            "scaler": scaler,
            "metadata": {
                "model_name": model_name,
                "version": version,
                "created_at": timestamp,
                "feature_names": feature_names or [],
                "hyperparameters": hyperparameters or {},
                "metrics": metrics or {},
                "scikit_learn_version": self._get_sklearn_version(),
                "python_version": self._get_python_version(),
                **(additional_metadata or {}),
            },
        }

        # Generate filename with version
        filename = f"{model_name}_v{version.replace('.', '_')}.joblib"
        filepath = self.models_dir / filename

        # Save using joblib with compression
        joblib.dump(model_bundle, filepath, compress=3)

        # Also save a "latest" symlink/copy
        latest_path = self.models_dir / f"{model_name}_latest.joblib"
        joblib.dump(model_bundle, latest_path, compress=3)

        # Save metadata as JSON for quick inspection
        metadata_path = self.models_dir / f"{model_name}_v{version.replace('.', '_')}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(model_bundle["metadata"], f, indent=2, default=str)

        print(f"Model saved: {filepath}")
        print(f"Metadata saved: {metadata_path}")

        return filepath

    def load_model(
        self,
        model_name: str,
        version: Optional[str] = None,
        validate: bool = True,
    ) -> dict:
        """
        Load a saved model with its metadata.

        Args:
            model_name: Name identifier for the model
            version: Specific version to load. If None, loads latest.
            validate: Whether to validate the loaded model

        Returns:
            Dictionary containing 'model', 'scaler', and 'metadata'

        Raises:
            FileNotFoundError: If model file doesn't exist
            ValueError: If validation fails
        """
        if version:
            filename = f"{model_name}_v{version.replace('.', '_')}.joblib"
        else:
            filename = f"{model_name}_latest.joblib"

        filepath = self.models_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Model not found: {filepath}")

        model_bundle = joblib.load(filepath)

        if validate:
            self._validate_model_bundle(model_bundle)

        print(f"Model loaded: {filepath}")
        print(f"  Version: {model_bundle['metadata']['version']}")
        print(f"  Created: {model_bundle['metadata']['created_at']}")

        return model_bundle

    def predict(
        self,
        model_name: str,
        features: np.ndarray,
        version: Optional[str] = None,
    ) -> np.ndarray:
        """
        Load a model and make predictions without retraining.

        Args:
            model_name: Name of the model to use
            features: Feature array for prediction
            version: Specific version to use

        Returns:
            Predicted labels/values
        """
        bundle = self.load_model(model_name, version)

        # Apply scaler if present
        if bundle["scaler"] is not None:
            features = bundle["scaler"].transform(features)

        # Make prediction
        model = bundle["model"]
        if hasattr(model, "predict"):
            return model.predict(features)
        elif hasattr(model, "fit_predict"):
            # For clustering models, use predict if available
            if hasattr(model, "labels_"):
                # Model was already fit, use predict
                return model.predict(features)
            else:
                raise ValueError("Model has not been fitted")
        else:
            raise ValueError("Model does not support prediction")

    def list_models(self) -> list:
        """List all available models and their versions."""
        models = []
        for filepath in self.models_dir.glob("*.joblib"):
            if "_latest" not in filepath.name:
                try:
                    bundle = joblib.load(filepath)
                    models.append(
                        {
                            "file": filepath.name,
                            "name": bundle["metadata"]["model_name"],
                            "version": bundle["metadata"]["version"],
                            "created_at": bundle["metadata"]["created_at"],
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not load {filepath}: {e}")
        return sorted(models, key=lambda x: x["created_at"], reverse=True)

    def get_model_info(self, model_name: str, version: Optional[str] = None) -> dict:
        """Get metadata for a specific model without loading the full model."""
        if version:
            metadata_path = (
                self.models_dir / f"{model_name}_v{version.replace('.', '_')}_metadata.json"
            )
        else:
            # Load from latest model
            bundle = self.load_model(model_name, validate=False)
            return bundle["metadata"]

        if metadata_path.exists():
            with open(metadata_path) as f:
                return json.load(f)
        else:
            # Fall back to loading the full model
            bundle = self.load_model(model_name, version, validate=False)
            return bundle["metadata"]

    def _validate_model_bundle(self, bundle: dict) -> None:
        """Validate a loaded model bundle."""
        required_keys = ["model", "metadata"]
        for key in required_keys:
            if key not in bundle:
                raise ValueError(f"Invalid model bundle: missing '{key}'")

        required_metadata = ["model_name", "version", "created_at"]
        for key in required_metadata:
            if key not in bundle["metadata"]:
                raise ValueError(f"Invalid metadata: missing '{key}'")

    def _get_sklearn_version(self) -> str:
        """Get scikit-learn version."""
        try:
            import sklearn

            return sklearn.__version__
        except ImportError:
            return "unknown"

    def _get_python_version(self) -> str:
        """Get Python version."""
        import sys

        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def compute_model_hash(self, model_name: str, version: Optional[str] = None) -> str:
        """
        Compute a hash of the model file for integrity verification.

        Args:
            model_name: Name of the model
            version: Specific version (optional)

        Returns:
            SHA256 hash of the model file
        """
        if version:
            filename = f"{model_name}_v{version.replace('.', '_')}.joblib"
        else:
            filename = f"{model_name}_latest.joblib"

        filepath = self.models_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Model not found: {filepath}")

        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()


def save_clustering_models(
    batter_model,
    batter_scaler,
    batter_features: list,
    batter_centers: np.ndarray,
    bowler_model,
    bowler_scaler,
    bowler_features: list,
    bowler_centers: np.ndarray,
    version: str = "2.0.0",
    n_batters: int = 0,
    n_bowlers: int = 0,
) -> dict:
    """
    Convenience function to save both batter and bowler clustering models.

    Args:
        batter_model: Trained KMeans model for batters
        batter_scaler: StandardScaler for batter features
        batter_features: List of feature names for batters
        batter_centers: Cluster centers for batters
        bowler_model: Trained KMeans model for bowlers
        bowler_scaler: StandardScaler for bowler features
        bowler_features: List of feature names for bowlers
        bowler_centers: Cluster centers for bowlers
        version: Model version string
        n_batters: Number of batters in training set
        n_bowlers: Number of bowlers in training set

    Returns:
        Dictionary with paths to saved models
    """
    serializer = ModelSerializer()

    # Save batter model
    batter_path = serializer.save_model(
        model=batter_model,
        model_name="batter_clustering",
        version=version,
        scaler=batter_scaler,
        feature_names=batter_features,
        hyperparameters={
            "n_clusters": batter_model.n_clusters,
            "random_state": batter_model.random_state,
            "n_init": batter_model.n_init,
            "max_iter": batter_model.max_iter,
        },
        metrics={
            "inertia": float(batter_model.inertia_),
            "n_iter": batter_model.n_iter_,
            "n_samples": n_batters,
        },
        additional_metadata={
            "cluster_centers": batter_centers.tolist()
            if isinstance(batter_centers, np.ndarray)
            else batter_centers,
            "player_type": "batter",
        },
    )

    # Save bowler model
    bowler_path = serializer.save_model(
        model=bowler_model,
        model_name="bowler_clustering",
        version=version,
        scaler=bowler_scaler,
        feature_names=bowler_features,
        hyperparameters={
            "n_clusters": bowler_model.n_clusters,
            "random_state": bowler_model.random_state,
            "n_init": bowler_model.n_init,
            "max_iter": bowler_model.max_iter,
        },
        metrics={
            "inertia": float(bowler_model.inertia_),
            "n_iter": bowler_model.n_iter_,
            "n_samples": n_bowlers,
        },
        additional_metadata={
            "cluster_centers": bowler_centers.tolist()
            if isinstance(bowler_centers, np.ndarray)
            else bowler_centers,
            "player_type": "bowler",
        },
    )

    return {
        "batter_model_path": str(batter_path),
        "bowler_model_path": str(bowler_path),
        "version": version,
    }


def load_clustering_model_for_inference(player_type: str, version: Optional[str] = None) -> dict:
    """
    Load a clustering model ready for inference.

    Args:
        player_type: Either "batter" or "bowler"
        version: Specific version to load (optional)

    Returns:
        Model bundle with model, scaler, and metadata
    """
    if player_type not in ["batter", "bowler"]:
        raise ValueError("player_type must be 'batter' or 'bowler'")

    serializer = ModelSerializer()
    model_name = f"{player_type}_clustering"
    return serializer.load_model(model_name, version)


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Model Serialization Utility")
    parser.add_argument("action", choices=["list", "info", "hash"], help="Action to perform")
    parser.add_argument("--model", "-m", help="Model name")
    parser.add_argument("--version", "-v", help="Model version")

    args = parser.parse_args()

    serializer = ModelSerializer()

    if args.action == "list":
        print("\nAvailable Models:")
        print("-" * 60)
        for model in serializer.list_models():
            print(f"  {model['name']} v{model['version']} ({model['created_at'][:10]})")
        print()

    elif args.action == "info":
        if not args.model:
            print("Error: --model required for 'info' action")
            exit(1)
        info = serializer.get_model_info(args.model, args.version)
        print(f"\nModel: {info['model_name']} v{info['version']}")
        print("-" * 40)
        print(json.dumps(info, indent=2, default=str))

    elif args.action == "hash":
        if not args.model:
            print("Error: --model required for 'hash' action")
            exit(1)
        hash_value = serializer.compute_model_hash(args.model, args.version)
        print(f"SHA256: {hash_value}")
