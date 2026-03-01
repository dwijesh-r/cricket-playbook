#!/usr/bin/env python3
"""
Lightweight Model Registry
==========================
Provides structured model versioning, registration, promotion, and
lifecycle management for all ML models in Cricket Playbook.

Persists to a single JSON file at ``scripts/ml_ops/model_registry.json``.
Thread-safe via ``fcntl`` file locking on Unix.

Owner: Ime Udoka (ML Ops Engineer)
Ticket: TKT-247  |  EPIC-015: Operational Maturity
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import logging
import re
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = PROJECT_ROOT / "scripts" / "ml_ops" / "model_registry.json"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("model_registry")

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------
ModelStatus = Literal["production", "candidate", "archived", "experimental"]

VALID_STATUSES: set[str] = {"production", "candidate", "archived", "experimental"}

# Semantic version regex (e.g. "1.0.0", "2.3.1")
_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


# ---------------------------------------------------------------------------
# Dataclass: ModelEntry
# ---------------------------------------------------------------------------
@dataclass
class ModelEntry:
    """A single registered model entry in the registry."""

    id: str
    name: str
    version: str
    created_at: str
    created_by: str
    model_type: str
    path: str
    training_data_hash: str
    hyperparameters: Dict[str, Any]
    metrics: Dict[str, Any]
    status: ModelStatus
    tags: List[str] = field(default_factory=list)
    description: str = ""

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a JSON-safe dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelEntry":
        """Reconstruct a ModelEntry from a dict."""
        return cls(**data)


# ---------------------------------------------------------------------------
# Semver helpers
# ---------------------------------------------------------------------------
def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string into (major, minor, patch).

    Raises ValueError if the string is not valid semver.
    """
    m = _SEMVER_RE.match(version)
    if not m:
        raise ValueError(f"Invalid semver string: {version!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def bump_version(
    version: str,
    part: Literal["major", "minor", "patch"] = "patch",
) -> str:
    """Bump a semantic version string.

    Parameters
    ----------
    version : str
        Current version (e.g. ``"1.2.3"``).
    part : str
        Which component to bump: ``"major"``, ``"minor"``, or ``"patch"``.

    Returns
    -------
    str
        The bumped version string.
    """
    major, minor, patch = parse_semver(version)
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def compute_data_hash(path: Path | str) -> str:
    """Compute a SHA-256 hash of a file for training-data lineage.

    Returns the first 12 hex characters of the hash, or ``"unknown"`` if
    the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        return "unknown"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


# ---------------------------------------------------------------------------
# File-locking context manager
# ---------------------------------------------------------------------------
@contextmanager
def _locked_registry(path: Path) -> Iterator[Dict[str, Any]]:
    """Context manager that reads, yields, and writes the registry JSON
    under an exclusive file lock.

    On entry the full registry dict is yielded.  The caller mutates it
    in-place and the updated dict is written back on exit.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure file exists
    if not path.exists():
        path.write_text(json.dumps({"models": [], "last_updated": None}, indent=2))

    with open(path, "r+") as fh:
        # Acquire exclusive lock (blocks until available)
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.seek(0)
            data = json.load(fh)
            yield data
            # Write back
            fh.seek(0)
            fh.truncate()
            data["last_updated"] = datetime.now(timezone.utc).isoformat()
            json.dump(data, fh, indent=2)
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# ModelRegistry class
# ---------------------------------------------------------------------------
class ModelRegistry:
    """Lightweight JSON-backed model registry with file locking.

    Usage::

        registry = ModelRegistry()
        entry = registry.register(
            name="win_prob_innings1",
            version="1.0.0",
            created_by="Ime Udoka",
            model_type="lightgbm",
            path="models/win_prob_innings1_v1.lgbm",
            training_data_hash="abc123def456",
            hyperparameters={"n_estimators": 500},
            metrics={"brier_score": 0.189},
            status="experimental",
            tags=["historical-replay-only"],
            description="First innings win probability - LightGBM",
        )
    """

    def __init__(self, registry_path: Path | str | None = None) -> None:
        self.path = Path(registry_path) if registry_path else REGISTRY_PATH

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _next_id(self, models: List[Dict[str, Any]]) -> str:
        """Generate the next auto-incrementing model ID."""
        if not models:
            return "mdl-001"
        existing_ids = [m.get("id", "") for m in models]
        max_num = 0
        for mid in existing_ids:
            parts = mid.split("-")
            if len(parts) == 2 and parts[1].isdigit():
                max_num = max(max_num, int(parts[1]))
        return f"mdl-{max_num + 1:03d}"

    def _find_model(
        self,
        models: List[Dict[str, Any]],
        *,
        model_id: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find a model entry by id or by (name, version)."""
        for m in models:
            if model_id and m.get("id") == model_id:
                return m
            if name and version and m.get("name") == name and m.get("version") == version:
                return m
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register(
        self,
        name: str,
        version: str,
        created_by: str,
        model_type: str,
        path: str,
        training_data_hash: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        status: ModelStatus = "experimental",
        tags: Optional[List[str]] = None,
        description: str = "",
    ) -> ModelEntry:
        """Register a new model in the registry.

        Parameters
        ----------
        name : str
            Human-readable model name (e.g. ``"win_prob_innings1"``).
        version : str
            Semantic version (e.g. ``"1.0.0"``).
        created_by : str
            Agent or person who created the model.
        model_type : str
            Model framework/type (e.g. ``"lightgbm"``, ``"logistic_regression"``).
        path : str
            Path to the serialised model file, relative to project root.
        training_data_hash : str
            Hash of the training data for lineage tracking.
        hyperparameters : dict
            Model hyperparameters.
        metrics : dict
            Evaluation metrics (Brier score, AUC, etc.).
        status : ModelStatus
            One of ``"production"``, ``"candidate"``, ``"archived"``, ``"experimental"``.
        tags : list[str] or None
            Arbitrary tags (e.g. ``["historical-replay-only"]``).
        description : str
            Free-text description of the model.

        Returns
        -------
        ModelEntry
            The newly registered model entry.

        Raises
        ------
        ValueError
            If a model with the same name and version already exists.
        """
        # Validate version format
        parse_semver(version)

        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status {status!r}; must be one of {VALID_STATUSES}")

        with _locked_registry(self.path) as data:
            models: List[Dict[str, Any]] = data.setdefault("models", [])

            # Duplicate check
            if self._find_model(models, name=name, version=version):
                raise ValueError(f"Model {name!r} version {version!r} already exists in registry")

            entry = ModelEntry(
                id=self._next_id(models),
                name=name,
                version=version,
                created_at=datetime.now(timezone.utc).isoformat(),
                created_by=created_by,
                model_type=model_type,
                path=path,
                training_data_hash=training_data_hash,
                hyperparameters=hyperparameters,
                metrics=metrics,
                status=status,
                tags=tags or [],
                description=description,
            )

            models.append(entry.to_dict())
            logger.info(
                "Registered model %s (%s v%s) with status=%s",
                entry.id,
                name,
                version,
                status,
            )

        return entry

    def promote(self, model_id: str) -> ModelEntry:
        """Promote a model to ``"production"`` status.

        Any existing production model with the same *name* is automatically
        archived.

        Parameters
        ----------
        model_id : str
            The ID of the model to promote.

        Returns
        -------
        ModelEntry
            The promoted model entry.

        Raises
        ------
        KeyError
            If no model with the given ID exists.
        """
        with _locked_registry(self.path) as data:
            models: List[Dict[str, Any]] = data.get("models", [])
            target = self._find_model(models, model_id=model_id)
            if target is None:
                raise KeyError(f"Model {model_id!r} not found in registry")

            # Archive any existing production model with the same name
            for m in models:
                if (
                    m.get("name") == target["name"]
                    and m.get("status") == "production"
                    and m.get("id") != model_id
                ):
                    m["status"] = "archived"
                    logger.info(
                        "Archived previous production model %s (%s v%s)",
                        m["id"],
                        m["name"],
                        m["version"],
                    )

            target["status"] = "production"
            logger.info(
                "Promoted model %s (%s v%s) to production",
                model_id,
                target["name"],
                target["version"],
            )
            return ModelEntry.from_dict(target)

    def archive(self, model_id: str) -> ModelEntry:
        """Archive a model (set status to ``"archived"``).

        Parameters
        ----------
        model_id : str
            The ID of the model to archive.

        Returns
        -------
        ModelEntry
            The archived model entry.
        """
        with _locked_registry(self.path) as data:
            models: List[Dict[str, Any]] = data.get("models", [])
            target = self._find_model(models, model_id=model_id)
            if target is None:
                raise KeyError(f"Model {model_id!r} not found in registry")

            target["status"] = "archived"
            logger.info("Archived model %s", model_id)
            return ModelEntry.from_dict(target)

    def get_production(self, name: str) -> Optional[ModelEntry]:
        """Return the current production model for a given name, or None.

        Parameters
        ----------
        name : str
            The model name to look up.

        Returns
        -------
        ModelEntry or None
        """
        with _locked_registry(self.path) as data:
            for m in data.get("models", []):
                if m.get("name") == name and m.get("status") == "production":
                    return ModelEntry.from_dict(m)
        return None

    def get_model(self, model_id: str) -> Optional[ModelEntry]:
        """Retrieve a model entry by its ID.

        Parameters
        ----------
        model_id : str
            The model ID.

        Returns
        -------
        ModelEntry or None
        """
        with _locked_registry(self.path) as data:
            target = self._find_model(data.get("models", []), model_id=model_id)
            if target:
                return ModelEntry.from_dict(target)
        return None

    def list_models(
        self,
        name: Optional[str] = None,
        status: Optional[ModelStatus] = None,
    ) -> List[ModelEntry]:
        """List all models, optionally filtered by name and/or status.

        Parameters
        ----------
        name : str or None
            Filter by model name.
        status : ModelStatus or None
            Filter by status.

        Returns
        -------
        list[ModelEntry]
        """
        with _locked_registry(self.path) as data:
            results = []
            for m in data.get("models", []):
                if name and m.get("name") != name:
                    continue
                if status and m.get("status") != status:
                    continue
                results.append(ModelEntry.from_dict(m))
        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    """Print registry contents to stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    registry = ModelRegistry()
    models = registry.list_models()

    print("=" * 70)
    print("MODEL REGISTRY")
    print(f"Path: {registry.path}")
    print(f"Total models: {len(models)}")
    print("=" * 70)

    if not models:
        print("  (no models registered)")
    else:
        for entry in models:
            print(f"\n  [{entry.status.upper():12s}] {entry.id}  {entry.name} v{entry.version}")
            print(f"    Type       : {entry.model_type}")
            print(f"    Created    : {entry.created_at}")
            print(f"    Created by : {entry.created_by}")
            print(f"    Path       : {entry.path}")
            print(f"    Data hash  : {entry.training_data_hash}")
            print(f"    Tags       : {', '.join(entry.tags) or '(none)'}")
            if entry.metrics:
                metrics_str = ", ".join(
                    f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}"
                    for k, v in entry.metrics.items()
                )
                print(f"    Metrics    : {metrics_str}")
            if entry.description:
                print(f"    Description: {entry.description}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
