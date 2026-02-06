#!/usr/bin/env python3
"""
Cricket Playbook - Externalized Configuration
=============================================
Loads configuration from environment variables with defaults from constants.py.

Usage:
    from config import config

    min_date = config.IPL_MIN_DATE
    db_path = config.DB_PATH
    threshold = config.MIN_BALLS_VS_TYPE

Environment Variables:
    IPL_MIN_DATE - Minimum date for data analysis (default: 2023-01-01)
    MIN_BALLS_VS_TYPE - Min balls for type matchup analysis (default: 50)
    MIN_BALLS_VS_HAND - Min balls for handedness analysis (default: 60)
    MIN_PP_OVERS - Min powerplay overs for phase tags (default: 30)
    MIN_MIDDLE_OVERS - Min middle overs for phase tags (default: 50)
    MIN_DEATH_OVERS - Min death overs for phase tags (default: 30)
    DATA_DIR - Override data directory path
    OUTPUT_DIR - Override output directory path
    DB_PATH - Override database path
    LOG_LEVEL - Logging level (quiet/normal/verbose/DEBUG/INFO/WARNING/ERROR)

Author: Brad Stevens (Ops Lead)
Sprint: TKT-100 - Externalize Configuration
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """
    Configuration manager that loads from environment variables with defaults.

    All configuration values are accessible as attributes on the config instance.
    Environment variables override the defaults from constants.py.
    """

    def __init__(self):
        """Initialize configuration with defaults, then load from environment."""
        # =======================================================================
        # PATH CONSTANTS
        # =======================================================================
        self._scripts_dir = Path(__file__).parent
        self._project_dir = self._scripts_dir.parent

        # Allow path overrides from environment
        self.DATA_DIR = Path(os.environ.get("DATA_DIR", str(self._project_dir / "data")))
        self.OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(self._project_dir / "outputs")))
        self.DB_PATH = Path(
            os.environ.get("DB_PATH", str(self.DATA_DIR / "cricket_playbook.duckdb"))
        )

        # Output subdirectories (derived from OUTPUT_DIR)
        self.MATCHUPS_DIR = self.OUTPUT_DIR / "matchups"
        self.METRICS_DIR = self.OUTPUT_DIR / "metrics"
        self.PREDICTED_XII_DIR = self.OUTPUT_DIR / "predicted_xii"
        self.DEPTH_CHARTS_DIR = self.OUTPUT_DIR / "depth_charts"

        # =======================================================================
        # DATE FILTERS
        # =======================================================================
        self.IPL_MIN_DATE = os.environ.get("IPL_MIN_DATE", "2023-01-01")

        # =======================================================================
        # SAMPLE SIZE THRESHOLDS
        # =======================================================================
        self.MIN_BALLS_VS_TYPE = int(os.environ.get("MIN_BALLS_VS_TYPE", "50"))
        self.MIN_BALLS_VS_HAND = int(os.environ.get("MIN_BALLS_VS_HAND", "60"))

        # Phase-specific minimum overs for tagging
        self.MIN_PP_OVERS = int(os.environ.get("MIN_PP_OVERS", "30"))
        self.MIN_MIDDLE_OVERS = int(os.environ.get("MIN_MIDDLE_OVERS", "50"))
        self.MIN_DEATH_OVERS = int(os.environ.get("MIN_DEATH_OVERS", "30"))

        # =======================================================================
        # TAG THRESHOLDS - BATTING
        # =======================================================================
        self.SPECIALIST_SR_THRESHOLD = int(os.environ.get("SPECIALIST_SR_THRESHOLD", "130"))
        self.SPECIALIST_AVG_THRESHOLD = int(os.environ.get("SPECIALIST_AVG_THRESHOLD", "20"))
        self.SPECIALIST_BPD_THRESHOLD = int(os.environ.get("SPECIALIST_BPD_THRESHOLD", "15"))

        self.VULNERABLE_SR_THRESHOLD = int(os.environ.get("VULNERABLE_SR_THRESHOLD", "110"))
        self.VULNERABLE_AVG_THRESHOLD = int(os.environ.get("VULNERABLE_AVG_THRESHOLD", "12"))
        self.VULNERABLE_BPD_THRESHOLD = int(os.environ.get("VULNERABLE_BPD_THRESHOLD", "12"))

        # =======================================================================
        # TAG THRESHOLDS - BOWLING PHASE
        # =======================================================================
        self.PP_BEAST_ECO = float(os.environ.get("PP_BEAST_ECO", "7.0"))
        self.PP_LIABILITY_ECO = float(os.environ.get("PP_LIABILITY_ECO", "9.5"))

        self.MIDDLE_BEAST_ECO = float(os.environ.get("MIDDLE_BEAST_ECO", "7.0"))
        self.MIDDLE_LIABILITY_ECO = float(os.environ.get("MIDDLE_LIABILITY_ECO", "8.5"))

        self.DEATH_BEAST_ECO = float(os.environ.get("DEATH_BEAST_ECO", "9.0"))
        self.DEATH_LIABILITY_ECO = float(os.environ.get("DEATH_LIABILITY_ECO", "12.0"))
        self.DEATH_LIABILITY_SR = float(os.environ.get("DEATH_LIABILITY_SR", "18.0"))

        # =======================================================================
        # TAG THRESHOLDS - HANDEDNESS
        # =======================================================================
        self.HANDEDNESS_ECO_THRESHOLD = float(os.environ.get("HANDEDNESS_ECO_THRESHOLD", "1.0"))
        self.HANDEDNESS_WPB_THRESHOLD = float(os.environ.get("HANDEDNESS_WPB_THRESHOLD", "0.02"))
        self.MIN_WICKETS_PER_BALL = float(os.environ.get("MIN_WICKETS_PER_BALL", "0.03"))

        # =======================================================================
        # LOGGING
        # =======================================================================
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "normal")

    @property
    def SCRIPTS_DIR(self) -> Path:
        """Get scripts directory path."""
        return self._scripts_dir

    @property
    def PROJECT_DIR(self) -> Path:
        """Get project root directory path."""
        return self._project_dir

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value by key name.

        Args:
            key: Configuration key name
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return getattr(self, key, default)

    def __repr__(self) -> str:
        """Return string representation of config."""
        return f"<Config IPL_MIN_DATE={self.IPL_MIN_DATE} DB_PATH={self.DB_PATH}>"


# Singleton instance - import this in other modules
config = Config()


# For backwards compatibility, also expose commonly used values at module level
IPL_MIN_DATE = config.IPL_MIN_DATE
DB_PATH = config.DB_PATH
OUTPUT_DIR = config.OUTPUT_DIR
DATA_DIR = config.DATA_DIR
