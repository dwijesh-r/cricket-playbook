"""
Threshold Loader Utility
========================
Single source of truth for loading thresholds from config/thresholds.yaml

Owner: Stephen Curry (Analytics Lead)
Ticket: TKT-132 (EPIC-014: Foundation Fortification)
Version: 1.0.0

Usage:
    from scripts.utils.threshold_loader import get_threshold, get_thresholds

    # Get single threshold
    min_balls = get_threshold('sample_size.min_balls_batter')

    # Get threshold section
    batting = get_thresholds('batting')
    sr_threshold = batting['specialist']['strike_rate']
"""

from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache

import yaml


def _find_project_root() -> Path:
    """Find the project root directory (contains config/)."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "config" / "thresholds.yaml").exists():
            return parent
    raise FileNotFoundError(
        "Could not find project root with config/thresholds.yaml. "
        "Ensure you're running from within the cricket-playbook project."
    )


@lru_cache(maxsize=1)
def _load_thresholds() -> Dict[str, Any]:
    """Load and cache thresholds from YAML file."""
    project_root = _find_project_root()
    config_path = project_root / "config" / "thresholds.yaml"

    with open(config_path, "r") as f:
        thresholds = yaml.safe_load(f)

    return thresholds


def get_thresholds(section: Optional[str] = None) -> Dict[str, Any]:
    """
    Get thresholds from config.

    Args:
        section: Optional section name (e.g., 'batting', 'ml.pca')
                 If None, returns entire config.

    Returns:
        Dictionary of thresholds

    Examples:
        >>> get_thresholds()  # All thresholds
        >>> get_thresholds('batting')  # Batting section
        >>> get_thresholds('ml.pca')  # Nested section
    """
    thresholds = _load_thresholds()

    if section is None:
        return thresholds

    # Navigate nested keys
    result = thresholds
    for key in section.split("."):
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            raise KeyError(f"Threshold section '{section}' not found. Key '{key}' missing.")

    return result


def get_threshold(path: str, default: Any = None) -> Any:
    """
    Get a single threshold value by dot-notation path.

    Args:
        path: Dot-notation path (e.g., 'sample_size.min_balls_batter')
        default: Default value if path not found (None raises KeyError)

    Returns:
        Threshold value

    Examples:
        >>> get_threshold('sample_size.min_balls_batter')
        300
        >>> get_threshold('batting.specialist.strike_rate')
        130
        >>> get_threshold('ml.pca.min_variance_batter')
        0.70
    """
    thresholds = _load_thresholds()

    result = thresholds
    keys = path.split(".")

    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        elif default is not None:
            return default
        else:
            raise KeyError(f"Threshold '{path}' not found. Key '{key}' missing.")

    return result


def reload_thresholds() -> Dict[str, Any]:
    """
    Force reload thresholds from disk (clears cache).

    Use when thresholds.yaml has been modified at runtime.
    """
    _load_thresholds.cache_clear()
    return _load_thresholds()


# =============================================================================
# CONVENIENCE ACCESSORS
# Common thresholds accessed frequently
# =============================================================================


class SampleSize:
    """Sample size thresholds."""

    @staticmethod
    def min_balls_batter() -> int:
        return get_threshold("sample_size.min_balls_batter")

    @staticmethod
    def min_balls_bowler() -> int:
        return get_threshold("sample_size.min_balls_bowler")

    @staticmethod
    def min_balls_vs_type() -> int:
        return get_threshold("sample_size.min_balls_vs_type")

    @staticmethod
    def min_balls_vs_hand() -> int:
        return get_threshold("sample_size.min_balls_vs_hand")


class Batting:
    """Batting thresholds."""

    @staticmethod
    def specialist_sr() -> int:
        return get_threshold("batting.specialist.strike_rate")

    @staticmethod
    def specialist_avg() -> int:
        return get_threshold("batting.specialist.average")

    @staticmethod
    def vulnerable_sr() -> int:
        return get_threshold("batting.vulnerable.strike_rate")

    @staticmethod
    def vulnerable_avg() -> int:
        return get_threshold("batting.vulnerable.average")


class Bowling:
    """Bowling thresholds by phase."""

    @staticmethod
    def pp_beast_economy() -> float:
        return get_threshold("bowling.powerplay.beast_economy")

    @staticmethod
    def pp_liability_economy() -> float:
        return get_threshold("bowling.powerplay.liability_economy")

    @staticmethod
    def death_beast_economy() -> float:
        return get_threshold("bowling.death.beast_economy")

    @staticmethod
    def death_liability_economy() -> float:
        return get_threshold("bowling.death.liability_economy")


class ML:
    """ML and clustering thresholds."""

    @staticmethod
    def pca_min_variance_batter() -> float:
        return get_threshold("ml.pca.min_variance_batter")

    @staticmethod
    def pca_min_variance_bowler() -> float:
        return get_threshold("ml.pca.min_variance_bowler")

    @staticmethod
    def min_cluster_size() -> int:
        return get_threshold("ml.clustering.min_cluster_size")

    @staticmethod
    def drift_ks_threshold() -> float:
        return get_threshold("ml.drift.ks_statistic")


class Validation:
    """Domain validation thresholds."""

    @staticmethod
    def sr_max_warning() -> int:
        return get_threshold("validation.strike_rate.warning_max")

    @staticmethod
    def sr_max_error() -> int:
        return get_threshold("validation.strike_rate.error_max")

    @staticmethod
    def economy_max_warning() -> float:
        return get_threshold("validation.economy.warning_max")

    @staticmethod
    def economy_max_error() -> float:
        return get_threshold("validation.economy.error_max")


# =============================================================================
# VALIDATION
# =============================================================================


def validate_thresholds() -> bool:
    """
    Validate that thresholds.yaml has all required sections.

    Returns:
        True if valid, raises ValueError otherwise.
    """
    required_sections = [
        "sample_size",
        "batting",
        "bowling",
        "ml",
        "stat_packs",
        "validation",
        "metadata",
    ]

    thresholds = _load_thresholds()

    missing = [s for s in required_sections if s not in thresholds]
    if missing:
        raise ValueError(f"Missing required threshold sections: {missing}")

    # Validate metadata
    metadata = thresholds.get("metadata", {})
    if "version" not in metadata:
        raise ValueError("Thresholds metadata missing 'version' field")

    return True


if __name__ == "__main__":
    # Quick validation test
    print("Validating thresholds.yaml...")
    validate_thresholds()
    print("✅ All required sections present")

    print("\nSample thresholds:")
    print(f"  Min balls (batter): {SampleSize.min_balls_batter()}")
    print(f"  Specialist SR: {Batting.specialist_sr()}")
    print(f"  PP Beast Economy: {Bowling.pp_beast_economy()}")
    print(f"  PCA Min Variance (batter): {ML.pca_min_variance_batter()}")
    print(f"  SR Max (error): {Validation.sr_max_error()}")

    print(f"\nVersion: {get_threshold('metadata.version')}")
