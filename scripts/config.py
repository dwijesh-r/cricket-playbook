#!/usr/bin/env python3
"""
Cricket Playbook - Externalized Configuration
=============================================
Scalable configuration system supporting environment variables, JSON config files,
and programmatic overrides.

Usage:
    from config import config

    # Basic usage
    min_date = config.IPL_MIN_DATE
    teams = config.get_teams()

    # Override at runtime
    config.set('TOURNAMENT', 'BBL')

Environment Variables:
    # Core Filters
    IPL_MIN_DATE - Minimum date for data analysis (default: 2023-01-01)
    IPL_MAX_DATE - Maximum date for data analysis (default: 2099-12-31)
    TOURNAMENT - Tournament filter: IPL, BBL, PSL, CPL, SA20, ILT20, ALL (default: IPL)
    MATCH_TYPE - Match format filter: T20, ODI, Test, ALL (default: T20)
    SEASON - Season year filter: 2023, 2024, 2025, 2026, ALL (default: ALL)

    # Team Filters
    TEAMS - Comma-separated team list or ALL (default: ALL)
    EXCLUDE_TEAMS - Comma-separated teams to exclude (default: none)

    # Output Configuration
    OUTPUT_FORMAT - json, markdown, html, all (default: markdown)
    OUTPUT_VERBOSE - Include detailed breakdowns (default: true)
    INCLUDE_SECTIONS - Comma-separated sections to include (default: all)
    EXCLUDE_SECTIONS - Comma-separated sections to exclude (default: none)

    # Sample Size Thresholds
    MIN_BALLS_VS_TYPE - Min balls for type matchup (default: 50)
    MIN_BALLS_VS_HAND - Min balls for handedness (default: 60)
    MIN_INNINGS - Min innings for player inclusion (default: 5)
    MIN_OVERS_BOWLED - Min overs for bowler inclusion (default: 10)

    # Performance & Caching
    CACHE_ENABLED - Enable query caching (default: true)
    CACHE_TTL_HOURS - Cache time-to-live in hours (default: 24)
    PARALLEL_WORKERS - Number of parallel workers (default: 4)
    BATCH_SIZE - Batch size for bulk operations (default: 10)

    # Debug & Logging
    LOG_LEVEL - quiet/normal/verbose/DEBUG (default: normal)
    DEBUG_MODE - Enable debug output (default: false)
    DRY_RUN - Simulate without writing files (default: false)

Author: Brad Stevens (Ops Lead)
Sprint: TKT-100 - Externalize Configuration
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class Config:
    """
    Comprehensive configuration manager for Cricket Playbook.

    Supports:
    - Environment variable overrides
    - JSON configuration files
    - Runtime programmatic changes
    - Team and tournament presets
    """

    # =======================================================================
    # TEAM REGISTRY - All supported teams with metadata
    # =======================================================================
    TEAM_REGISTRY: Dict[str, Dict[str, Any]] = {
        # IPL Teams
        "Chennai Super Kings": {
            "short": "CSK",
            "aliases": ["CSK", "Chennai", "Super Kings"],
            "tournament": "IPL",
            "home_venue": "MA Chidambaram Stadium",
            "primary_color": "#FFFF00",
        },
        "Mumbai Indians": {
            "short": "MI",
            "aliases": ["MI", "Mumbai"],
            "tournament": "IPL",
            "home_venue": "Wankhede Stadium",
            "primary_color": "#004BA0",
        },
        "Royal Challengers Bengaluru": {
            "short": "RCB",
            "aliases": ["RCB", "Bangalore", "Bengaluru", "Royal Challengers"],
            "tournament": "IPL",
            "home_venue": "M. Chinnaswamy Stadium",
            "primary_color": "#EC1C24",
        },
        "Kolkata Knight Riders": {
            "short": "KKR",
            "aliases": ["KKR", "Kolkata", "Knight Riders"],
            "tournament": "IPL",
            "home_venue": "Eden Gardens",
            "primary_color": "#3A225D",
        },
        "Rajasthan Royals": {
            "short": "RR",
            "aliases": ["RR", "Rajasthan", "Royals"],
            "tournament": "IPL",
            "home_venue": "Sawai Mansingh Stadium",
            "primary_color": "#EA1A85",
        },
        "Delhi Capitals": {
            "short": "DC",
            "aliases": ["DC", "Delhi", "Capitals"],
            "tournament": "IPL",
            "home_venue": "Arun Jaitley Stadium",
            "primary_color": "#00008B",
        },
        "Sunrisers Hyderabad": {
            "short": "SRH",
            "aliases": ["SRH", "Hyderabad", "Sunrisers"],
            "tournament": "IPL",
            "home_venue": "Rajiv Gandhi Intl Stadium",
            "primary_color": "#FF822A",
        },
        "Punjab Kings": {
            "short": "PBKS",
            "aliases": ["PBKS", "Punjab", "Kings XI"],
            "tournament": "IPL",
            "home_venue": "IS Bindra Stadium",
            "primary_color": "#ED1B24",
        },
        "Gujarat Titans": {
            "short": "GT",
            "aliases": ["GT", "Gujarat", "Titans"],
            "tournament": "IPL",
            "home_venue": "Narendra Modi Stadium",
            "primary_color": "#1C1C1C",
        },
        "Lucknow Super Giants": {
            "short": "LSG",
            "aliases": ["LSG", "Lucknow", "Super Giants"],
            "tournament": "IPL",
            "home_venue": "BRSABV Ekana Stadium",
            "primary_color": "#A72056",
        },
        # BBL Teams (for future expansion)
        "Melbourne Stars": {
            "short": "STA",
            "aliases": ["Stars", "Melbourne Stars"],
            "tournament": "BBL",
            "home_venue": "MCG",
            "primary_color": "#00B140",
        },
        "Sydney Sixers": {
            "short": "SIX",
            "aliases": ["Sixers", "Sydney Sixers"],
            "tournament": "BBL",
            "home_venue": "SCG",
            "primary_color": "#FF00FF",
        },
        # Add more BBL, PSL, CPL teams as needed
    }

    # =======================================================================
    # TOURNAMENT REGISTRY
    # =======================================================================
    TOURNAMENT_REGISTRY: Dict[str, Dict[str, Any]] = {
        "IPL": {
            "full_name": "Indian Premier League",
            "format": "T20",
            "teams_count": 10,
            "season_months": [3, 4, 5],  # March-May
        },
        "BBL": {
            "full_name": "Big Bash League",
            "format": "T20",
            "teams_count": 8,
            "season_months": [12, 1, 2],  # Dec-Feb
        },
        "PSL": {
            "full_name": "Pakistan Super League",
            "format": "T20",
            "teams_count": 6,
            "season_months": [2, 3],
        },
        "CPL": {
            "full_name": "Caribbean Premier League",
            "format": "T20",
            "teams_count": 6,
            "season_months": [8, 9],
        },
        "SA20": {
            "full_name": "SA20 League",
            "format": "T20",
            "teams_count": 6,
            "season_months": [1, 2],
        },
        "ILT20": {
            "full_name": "International League T20",
            "format": "T20",
            "teams_count": 6,
            "season_months": [1, 2],
        },
        "T20 World Cup": {
            "full_name": "ICC T20 World Cup",
            "format": "T20",
            "teams_count": 20,
            "season_months": [6, 7, 10, 11],  # Varies by year
        },
    }

    # =======================================================================
    # PLAYER ROLE CATEGORIES
    # =======================================================================
    PLAYER_ROLES: Dict[str, List[str]] = {
        "batting": [
            "Opener",
            "Top Order",
            "Middle Order",
            "Finisher",
            "Anchor",
            "Pinch Hitter",
        ],
        "bowling": [
            "Powerplay Specialist",
            "Middle Overs",
            "Death Specialist",
            "Wicket Taker",
            "Economy Bowler",
        ],
        "bowling_style": [
            "Right-arm Fast",
            "Right-arm Medium",
            "Left-arm Fast",
            "Left-arm Medium",
            "Right-arm Off Spin",
            "Right-arm Leg Spin",
            "Left-arm Orthodox",
            "Left-arm Chinaman",
        ],
        "fielding": [
            "Wicketkeeper",
            "Slip Fielder",
            "Boundary Rider",
            "Athletic Fielder",
        ],
    }

    # =======================================================================
    # OUTPUT SECTIONS
    # =======================================================================
    AVAILABLE_SECTIONS: List[str] = [
        "team_overview",
        "batting_depth",
        "bowling_depth",
        "matchup_matrix",
        "phase_analysis",
        "key_partnerships",
        "pressure_performance",
        "venue_analysis",
        "historical_trends",
        "player_profiles",
        "predictions",
    ]

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration with defaults, then load from environment and config file.

        Args:
            config_file: Optional path to JSON config file
        """
        # =======================================================================
        # PATH CONSTANTS
        # =======================================================================
        self._scripts_dir = Path(__file__).parent
        self._project_dir = self._scripts_dir.parent
        self._runtime_overrides: Dict[str, Any] = {}

        # Allow path overrides from environment
        self.DATA_DIR = Path(os.environ.get("DATA_DIR", str(self._project_dir / "data")))
        self.OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", str(self._project_dir / "outputs")))
        self.DB_PATH = Path(
            os.environ.get("DB_PATH", str(self.DATA_DIR / "cricket_playbook.duckdb"))
        )
        self.CONFIG_DIR = Path(os.environ.get("CONFIG_DIR", str(self._project_dir / "config")))

        # Output subdirectories (derived from OUTPUT_DIR)
        self.MATCHUPS_DIR = self.OUTPUT_DIR / "matchups"
        self.METRICS_DIR = self.OUTPUT_DIR / "metrics"
        self.PREDICTED_XII_DIR = self.OUTPUT_DIR / "predicted_xii"
        self.DEPTH_CHARTS_DIR = self.OUTPUT_DIR / "depth_charts"
        self.STAT_PACKS_DIR = self.OUTPUT_DIR / "stat_packs"

        # =======================================================================
        # DATE FILTERS
        # =======================================================================
        self.IPL_MIN_DATE = os.environ.get("IPL_MIN_DATE", "2023-01-01")
        self.IPL_MAX_DATE = os.environ.get("IPL_MAX_DATE", "2099-12-31")

        # =======================================================================
        # TOURNAMENT & MATCH TYPE FILTERS
        # =======================================================================
        self.TOURNAMENT = os.environ.get("TOURNAMENT", "IPL")
        self.MATCH_TYPE = os.environ.get("MATCH_TYPE", "T20")
        self.SEASON = os.environ.get("SEASON", "ALL")

        # =======================================================================
        # TEAM FILTERS
        # =======================================================================
        teams_env = os.environ.get("TEAMS", "ALL")
        self.TEAMS = teams_env if teams_env == "ALL" else [t.strip() for t in teams_env.split(",")]

        exclude_teams_env = os.environ.get("EXCLUDE_TEAMS", "")
        self.EXCLUDE_TEAMS = [t.strip() for t in exclude_teams_env.split(",") if t.strip()]

        # =======================================================================
        # PLAYER FILTERS
        # =======================================================================
        self.PLAYER_IDS = os.environ.get("PLAYER_IDS", "ALL")  # Comma-separated or ALL
        self.EXCLUDE_PLAYER_IDS = os.environ.get("EXCLUDE_PLAYER_IDS", "")

        # =======================================================================
        # OUTPUT CONFIGURATION
        # =======================================================================
        self.OUTPUT_FORMAT = os.environ.get(
            "OUTPUT_FORMAT", "markdown"
        )  # json, markdown, html, all
        self.OUTPUT_VERBOSE = os.environ.get("OUTPUT_VERBOSE", "true").lower() == "true"

        include_sections = os.environ.get("INCLUDE_SECTIONS", "all")
        self.INCLUDE_SECTIONS = (
            self.AVAILABLE_SECTIONS
            if include_sections == "all"
            else [s.strip() for s in include_sections.split(",")]
        )

        exclude_sections = os.environ.get("EXCLUDE_SECTIONS", "")
        self.EXCLUDE_SECTIONS = [s.strip() for s in exclude_sections.split(",") if s.strip()]

        # =======================================================================
        # SAMPLE SIZE THRESHOLDS
        # =======================================================================
        self.MIN_BALLS_VS_TYPE = int(os.environ.get("MIN_BALLS_VS_TYPE", "50"))
        self.MIN_BALLS_VS_HAND = int(os.environ.get("MIN_BALLS_VS_HAND", "60"))
        self.MIN_INNINGS = int(os.environ.get("MIN_INNINGS", "5"))
        self.MIN_OVERS_BOWLED = int(os.environ.get("MIN_OVERS_BOWLED", "10"))
        self.MIN_MATCHES_FOR_TREND = int(os.environ.get("MIN_MATCHES_FOR_TREND", "3"))

        # Phase-specific minimum overs for tagging
        self.MIN_PP_OVERS = int(os.environ.get("MIN_PP_OVERS", "30"))
        self.MIN_MIDDLE_OVERS = int(os.environ.get("MIN_MIDDLE_OVERS", "50"))
        self.MIN_DEATH_OVERS = int(os.environ.get("MIN_DEATH_OVERS", "30"))

        # Partnership thresholds
        self.MIN_PARTNERSHIP_BALLS = int(os.environ.get("MIN_PARTNERSHIP_BALLS", "12"))
        self.MIN_PARTNERSHIP_RUNS = int(os.environ.get("MIN_PARTNERSHIP_RUNS", "20"))
        self.KEY_PARTNERSHIP_THRESHOLD = int(os.environ.get("KEY_PARTNERSHIP_THRESHOLD", "50"))

        # =======================================================================
        # TAG THRESHOLDS - BATTING
        # =======================================================================
        self.SPECIALIST_SR_THRESHOLD = int(os.environ.get("SPECIALIST_SR_THRESHOLD", "130"))
        self.SPECIALIST_AVG_THRESHOLD = int(os.environ.get("SPECIALIST_AVG_THRESHOLD", "20"))
        self.SPECIALIST_BPD_THRESHOLD = int(os.environ.get("SPECIALIST_BPD_THRESHOLD", "15"))

        self.VULNERABLE_SR_THRESHOLD = int(os.environ.get("VULNERABLE_SR_THRESHOLD", "110"))
        self.VULNERABLE_AVG_THRESHOLD = int(os.environ.get("VULNERABLE_AVG_THRESHOLD", "12"))
        self.VULNERABLE_BPD_THRESHOLD = int(os.environ.get("VULNERABLE_BPD_THRESHOLD", "12"))

        # Pressure performance thresholds
        self.HIGH_RRR_THRESHOLD = float(os.environ.get("HIGH_RRR_THRESHOLD", "10.0"))
        self.CLUTCH_SR_THRESHOLD = float(os.environ.get("CLUTCH_SR_THRESHOLD", "140.0"))

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
        # PERFORMANCE & CACHING
        # =======================================================================
        self.CACHE_ENABLED = os.environ.get("CACHE_ENABLED", "true").lower() == "true"
        self.CACHE_TTL_HOURS = int(os.environ.get("CACHE_TTL_HOURS", "24"))
        self.PARALLEL_WORKERS = int(os.environ.get("PARALLEL_WORKERS", "4"))
        self.BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "10"))

        # =======================================================================
        # LOGGING & DEBUG
        # =======================================================================
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "normal")
        self.DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
        self.DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

        # =======================================================================
        # EDGE CASE HANDLING
        # =======================================================================
        self.FALLBACK_BATTING_HAND = os.environ.get("FALLBACK_BATTING_HAND", "Right")
        self.FALLBACK_BOWLING_STYLE = os.environ.get("FALLBACK_BOWLING_STYLE", "Unknown")
        self.MISSING_DATA_STRATEGY = os.environ.get(
            "MISSING_DATA_STRATEGY", "skip"
        )  # skip, default, error
        self.ALLOW_PARTIAL_DATA = os.environ.get("ALLOW_PARTIAL_DATA", "true").lower() == "true"

        # =======================================================================
        # LOAD JSON CONFIG FILE (if provided)
        # =======================================================================
        if config_file:
            self._load_config_file(config_file)
        elif (self.CONFIG_DIR / "config.json").exists():
            self._load_config_file(str(self.CONFIG_DIR / "config.json"))

    def _load_config_file(self, path: str) -> None:
        """Load configuration from a JSON file."""
        try:
            with open(path, "r") as f:
                file_config = json.load(f)
                for key, value in file_config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if self.DEBUG_MODE:
                print(f"Warning: Could not load config file {path}: {e}")

    # =======================================================================
    # HELPER METHODS
    # =======================================================================

    def get_teams(self, tournament: Optional[str] = None) -> List[str]:
        """
        Get list of teams for the specified tournament.

        Args:
            tournament: Tournament name (default: current TOURNAMENT setting)

        Returns:
            List of team names
        """
        tourney = tournament or self.TOURNAMENT

        if self.TEAMS != "ALL":
            return [t for t in self.TEAMS if t not in self.EXCLUDE_TEAMS]

        teams = [
            name
            for name, info in self.TEAM_REGISTRY.items()
            if tourney == "ALL" or info.get("tournament") == tourney
        ]
        return [t for t in teams if t not in self.EXCLUDE_TEAMS]

    def get_team_info(self, team_name: str) -> Optional[Dict[str, Any]]:
        """Get team metadata by name or alias."""
        # Direct match
        if team_name in self.TEAM_REGISTRY:
            return self.TEAM_REGISTRY[team_name]

        # Alias match
        for name, info in self.TEAM_REGISTRY.items():
            if team_name in info.get("aliases", []):
                return {**info, "full_name": name}

        return None

    def resolve_team_name(self, alias: str) -> Optional[str]:
        """Resolve a team alias to full name."""
        if alias in self.TEAM_REGISTRY:
            return alias

        for name, info in self.TEAM_REGISTRY.items():
            if alias in info.get("aliases", []):
                return name

        return None

    def get_active_sections(self) -> List[str]:
        """Get list of sections to include in output."""
        return [s for s in self.INCLUDE_SECTIONS if s not in self.EXCLUDE_SECTIONS]

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value at runtime."""
        self._runtime_overrides[key] = value
        setattr(self, key, value)

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get configuration value by key name."""
        return getattr(self, key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            key: getattr(self, key)
            for key in dir(self)
            if not key.startswith("_") and not callable(getattr(self, key))
        }

    def save(self, path: str) -> None:
        """Save current configuration to JSON file."""
        config_dict = {
            k: str(v) if isinstance(v, Path) else v
            for k, v in self.to_dict().items()
            if not isinstance(v, (dict, type))
        }
        with open(path, "w") as f:
            json.dump(config_dict, f, indent=2, default=str)

    @property
    def SCRIPTS_DIR(self) -> Path:
        """Get scripts directory path."""
        return self._scripts_dir

    @property
    def PROJECT_DIR(self) -> Path:
        """Get project root directory path."""
        return self._project_dir

    def __repr__(self) -> str:
        """Return string representation of config."""
        return (
            f"<Config TOURNAMENT={self.TOURNAMENT} SEASON={self.SEASON} "
            f"MATCH_TYPE={self.MATCH_TYPE} TEAMS={len(self.get_teams())} teams>"
        )


# Singleton instance - import this in other modules
config = Config()


# For backwards compatibility, also expose commonly used values at module level
IPL_MIN_DATE = config.IPL_MIN_DATE
IPL_MAX_DATE = config.IPL_MAX_DATE
TOURNAMENT = config.TOURNAMENT
MATCH_TYPE = config.MATCH_TYPE
SEASON = config.SEASON
DB_PATH = config.DB_PATH
OUTPUT_DIR = config.OUTPUT_DIR
DATA_DIR = config.DATA_DIR
