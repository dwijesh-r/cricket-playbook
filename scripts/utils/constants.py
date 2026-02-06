#!/usr/bin/env python3
"""
Cricket Playbook - Shared Constants Module
Author: Brad Stevens (Code Quality)
Sprint: Optimization Audit TKT-096

Consolidates commonly used constants across the codebase to:
1. Avoid duplication and maintain single source of truth
2. Make threshold updates easier (change in one place)
3. Improve consistency across scripts
"""

from pathlib import Path
from typing import Dict, List

# =============================================================================
# PATH CONSTANTS
# =============================================================================

# Base paths - scripts should import these instead of computing them
SCRIPTS_DIR = Path(__file__).parent.parent
PROJECT_DIR = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
DB_PATH = DATA_DIR / "cricket_playbook.duckdb"

# Output subdirectories
MATCHUPS_DIR = OUTPUT_DIR / "matchups"
METRICS_DIR = OUTPUT_DIR / "metrics"
PREDICTED_XII_DIR = OUTPUT_DIR / "predicted_xii"
DEPTH_CHARTS_DIR = OUTPUT_DIR / "depth_charts"


# =============================================================================
# DATE FILTERS
# =============================================================================

# Minimum date for recent data analysis (2023+ for recency)
IPL_MIN_DATE = "2023-01-01"


# =============================================================================
# SAMPLE SIZE THRESHOLDS
# =============================================================================

# Minimum balls faced/bowled for various analyses
MIN_BALLS_VS_TYPE = 50  # Updated per Andy Flower review - Sprint 4.0
MIN_BALLS_VS_HAND = 60  # ~10 overs for handedness analysis

# Phase-specific minimum overs for tagging
MIN_PP_OVERS = 30
MIN_MIDDLE_OVERS = 50
MIN_DEATH_OVERS = 30


# =============================================================================
# BOWLING TYPE CATEGORIES
# =============================================================================

# Must match dim_bowler_classification.bowling_style values exactly
PACE_TYPES: List[str] = ["Right-arm pace", "Left-arm pace"]
SPIN_TYPES: List[str] = [
    "Right-arm off-spin",
    "Right-arm leg-spin",
    "Left-arm orthodox",
    "Left-arm wrist spin",
]


# =============================================================================
# TAG THRESHOLDS - BATTING
# =============================================================================

# SPECIALIST thresholds (ALL must be true):
#   - SR >= threshold (scores fast)
#   - avg >= threshold (quality runs)
#   - bpd >= threshold (survives long enough)
SPECIALIST_SR_THRESHOLD = 130
SPECIALIST_AVG_THRESHOLD = 20
SPECIALIST_BPD_THRESHOLD = 15

# VULNERABLE thresholds (ANY can be true):
#   - SR < threshold (scores slowly)
#   - avg < threshold (poor quality)
#   - bpd < threshold with 3+ dismissals (gets out too often)
VULNERABLE_SR_THRESHOLD = 110
VULNERABLE_AVG_THRESHOLD = 12
VULNERABLE_BPD_THRESHOLD = 12


# =============================================================================
# TAG THRESHOLDS - BOWLING PHASE
# =============================================================================

# Powerplay thresholds
PP_BEAST_ECO = 7.0
PP_LIABILITY_ECO = 9.5

# Middle overs thresholds
MIDDLE_BEAST_ECO = 7.0
MIDDLE_LIABILITY_ECO = 8.5

# Death overs thresholds (adjusted based on percentile analysis)
DEATH_BEAST_ECO = 9.0
DEATH_LIABILITY_ECO = 12.0
DEATH_LIABILITY_SR = 18.0  # Strike rate threshold for death liability


# =============================================================================
# TAG THRESHOLDS - HANDEDNESS
# =============================================================================

# Economy differential for specialist/vulnerable tags
HANDEDNESS_ECO_THRESHOLD = 1.0

# Wickets per ball differential for wicket-taker tags
HANDEDNESS_WPB_THRESHOLD = 0.02  # 2% more wickets per ball

# Minimum wickets/ball ratio to qualify for wicket-taker tag
MIN_WICKETS_PER_BALL = 0.03  # ~1 wicket per 33 balls


# =============================================================================
# IPL 2026 TEAMS
# =============================================================================

IPL_TEAMS: List[str] = [
    "Chennai Super Kings",
    "Mumbai Indians",
    "Royal Challengers Bengaluru",
    "Kolkata Knight Riders",
    "Delhi Capitals",
    "Punjab Kings",
    "Rajasthan Royals",
    "Sunrisers Hyderabad",
    "Gujarat Titans",
    "Lucknow Super Giants",
]

TEAM_ABBREV: Dict[str, str] = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Rajasthan Royals": "RR",
    "Sunrisers Hyderabad": "SRH",
    "Gujarat Titans": "GT",
    "Lucknow Super Giants": "LSG",
}


# =============================================================================
# OVERSEAS PLAYERS LIST
# =============================================================================

# Comprehensive list of overseas players for constraint checking
OVERSEAS_PLAYERS: set = {
    # Australian
    "Mitchell Marsh",
    "Travis Head",
    "Pat Cummins",
    "Josh Hazlewood",
    "Mitchell Starc",
    "Glenn Maxwell",
    "Marcus Stoinis",
    "Josh Inglis",
    "Adam Zampa",
    "Nathan Ellis",
    "Matthew Short",
    "Spencer Johnson",
    "Xavier Bartlett",
    "Ben Dwarshuis",
    "Tim David",
    "Glenn Phillips",
    "Cameron Green",
    "Finn Allen",
    "Cooper Connolly",
    "Matthew Breetzke",
    # English
    "Jos Buttler",
    "Phil Salt",
    "Liam Livingstone",
    "Sam Curran",
    "Ben Duckett",
    "Jacob Bethell",
    "Will Jacks",
    "Jofra Archer",
    "Jamie Overton",
    "Romario Shepherd",
    "Jordan Cox",
    "Jacob Duffy",
    "Brydon Carse",
    "Jack Edwards",
    # South African
    "Quinton de Kock",
    "Heinrich Klaasen",
    "David Miller",
    "Kagiso Rabada",
    "Anrich Nortje",
    "Lungi Ngidi",
    "Gerald Coetzee",
    "Tristan Stubbs",
    "Dewald Brevis",
    "Marco Jansen",
    "Aiden Markram",
    "Donovan Ferreira",
    "Nandre Burger",
    "Kwena Maphaka",
    "Lhuan-dre Pretorius",
    "Corbin Bosch",
    "Ryan Rickelton",
    # West Indian
    "Nicholas Pooran",
    "Shimron Hetmyer",
    "Rovman Powell",
    "Sherfane Rutherford",
    "Sunil Narine",
    # New Zealand
    "Trent Boult",
    "Lockie Ferguson",
    "Mitchell Santner",
    "Rachin Ravindra",
    "Tim Seifert",
    "Adam Milne",
    "Matt Henry",
    # Sri Lankan
    "Wanindu Hasaranga",
    "Matheesha Pathirana",
    "Kamindu Mendis",
    "Akeal Hosein",
    # Afghan
    "Rashid Khan",
    "Noor Ahmad",
    "Azmatullah Omarzai",
    "AM Ghazanfar",
    # Others
    "Pathum Nissanka",
    "Kyle Jamieson",
    "Dushmantha Chameera",
    "Zak Foulkes",
    "Sikandar Raza",
    "Raqibul Hasan",
}


def is_overseas_player(player_name: str) -> bool:
    """Check if a player is overseas based on the known list."""
    return player_name.strip() in OVERSEAS_PLAYERS
