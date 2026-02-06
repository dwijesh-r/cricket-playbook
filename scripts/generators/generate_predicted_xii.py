#!/usr/bin/env python3
"""
Cricket Playbook - Predicted XII Generator
Author: Stephen Curry (Analytics Lead)
Sprint: V1 - Predicted XII Algorithm

Generates optimal XII (XI + Impact Player) for each IPL 2026 team using:
1. Constraint-satisfaction with weighted scoring
2. Role-based selection logic
3. Balance optimization (pace/spin, LHB/RHB, phase coverage)

Per approved PRD: /governance/tasks/PREDICTED_XI_PRD.md
"""

import json
import csv
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
PREDICTED_XII_DIR = OUTPUT_DIR / "predicted_xii"

# IPL 2026 Teams
IPL_TEAMS = [
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

# Team abbreviations for output
TEAM_ABBREV = {
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

# Home venues (for spin/pace bias)
HOME_VENUES = {
    "Chennai Super Kings": {"venue": "MA Chidambaram Stadium", "bias": "spin"},
    "Mumbai Indians": {"venue": "Wankhede Stadium", "bias": "pace"},
    "Royal Challengers Bengaluru": {"venue": "M Chinnaswamy Stadium", "bias": "pace"},
    "Kolkata Knight Riders": {"venue": "Eden Gardens", "bias": "spin"},
    "Delhi Capitals": {"venue": "Arun Jaitley Stadium", "bias": "neutral"},
    "Punjab Kings": {"venue": "Punjab Cricket Association Stadium", "bias": "neutral"},
    "Rajasthan Royals": {"venue": "Sawai Mansingh Stadium", "bias": "neutral"},
    "Sunrisers Hyderabad": {"venue": "Rajiv Gandhi Intl Stadium", "bias": "pace"},
    "Gujarat Titans": {"venue": "Narendra Modi Stadium", "bias": "neutral"},
    "Lucknow Super Giants": {"venue": "Ekana Cricket Stadium", "bias": "neutral"},
}


# =============================================================================
# DATA CLASSES
# =============================================================================


class Role(Enum):
    """Player roles in T20 XI"""

    OPENER = "opener"
    TOP_ORDER = "top_order"
    MIDDLE_ORDER = "middle_order"
    FINISHER = "finisher"
    WICKETKEEPER = "wicketkeeper"
    ALL_ROUNDER_BAT = "all_rounder_batting"
    ALL_ROUNDER_BOWL = "all_rounder_bowling"
    SPINNER = "spinner"
    PACE_BOWLER = "pace_bowler"
    SPECIALIST_BOWLER = "specialist_bowler"


class BowlingType(Enum):
    """Bowling classification"""

    PACE = "pace"
    SPIN = "spin"
    MEDIUM = "medium"


@dataclass
class Player:
    """Player data model"""

    player_id: str
    player_name: str
    team: str
    role: str  # From squad data: Batter/Bowler/All-rounder/Wicketkeeper
    batting_hand: str
    bowling_arm: Optional[str] = None
    bowling_type: Optional[str] = None
    price_cr: float = 0.0
    is_overseas: bool = False
    is_wicketkeeper: bool = False
    batter_classification: Optional[str] = None
    bowler_classification: Optional[str] = None
    batter_tags: list = field(default_factory=list)
    bowler_tags: list = field(default_factory=list)

    # Computed properties
    can_bowl: bool = False
    bowling_overs_capability: int = 0  # 0, 2, or 4 overs
    is_spinner: bool = False
    is_pacer: bool = False

    # Scoring (computed later)
    batting_score: float = 0.0
    bowling_score: float = 0.0
    overall_score: float = 0.0

    def __post_init__(self):
        """Compute derived properties"""
        self.is_wicketkeeper = self.role == "Wicketkeeper"

        # Determine bowling capability
        if self.bowling_type:
            bowling_type_lower = self.bowling_type.lower()
            if "spin" in bowling_type_lower or "orthodox" in bowling_type_lower:
                self.is_spinner = True
                self.can_bowl = True
                self.bowling_overs_capability = 4
            elif "fast" in bowling_type_lower or "pace" in bowling_type_lower:
                self.is_pacer = True
                self.can_bowl = True
                self.bowling_overs_capability = 4
            elif "medium" in bowling_type_lower:
                self.can_bowl = True
                self.is_pacer = True  # Classify medium as pace
                self.bowling_overs_capability = 2  # Part-timer

        # All-rounders can bowl
        if self.role == "All-rounder":
            self.can_bowl = True
            if not self.bowling_overs_capability:
                self.bowling_overs_capability = 4

        # Bowlers definitely can bowl 4 overs
        if self.role == "Bowler":
            self.can_bowl = True
            self.bowling_overs_capability = 4


@dataclass
class SelectedPlayer:
    """Player selected in the XII"""

    player: Player
    batting_position: int
    role_in_xi: str
    rationale: str
    is_impact_player: bool = False


@dataclass
class PredictedXII:
    """Complete predicted XII for a team"""

    team_name: str
    team_abbrev: str
    home_venue: str
    venue_bias: str
    xi: list  # List of SelectedPlayer
    impact_player: Optional[SelectedPlayer]
    captain: str
    wicketkeeper: str
    overseas_count: int
    bowling_options: int
    spinners_count: int
    pacers_count: int
    left_handers_top6: int
    constraints_satisfied: bool
    constraint_violations: list
    generation_notes: list


# =============================================================================
# DATA LOADING
# =============================================================================


def load_squads() -> Tuple[Dict[str, List[Dict[str, str]]], Dict[str, str]]:
    """
    Load IPL 2026 squad data.

    Returns:
        tuple: (squads dict, captains dict)
        - squads: {team_name: [player_rows]}
        - captains: {team_name: captain_player_name} from is_captain=TRUE field
    """
    squads = {}
    captains = {}
    squad_file = DATA_DIR / "ipl_2026_squads.csv"

    logger.debug("Loading squads from %s", squad_file)

    with open(squad_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row["team_name"]
            if team not in squads:
                squads[team] = []
            squads[team].append(row)

            # Extract captain from is_captain field
            is_cap = (row.get("is_captain") or "").strip().upper()
            if is_cap == "TRUE":
                captains[team] = row["player_name"]

    logger.info("Loaded %d teams from squad data", len(squads))
    return squads, captains


def load_contracts() -> Dict[str, Dict[str, Any]]:
    """Load player contract/auction prices"""
    contracts = {}
    contract_file = DATA_DIR / "ipl_2026_player_contracts.csv"

    with open(contract_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['team_name']}|{row['player_name']}"
            contracts[key] = {
                "price_cr": float(row["price_cr"]),
                "acquisition_type": row["acquisition_type"],
                "year_joined": int(row["year_joined"]),
            }

    return contracts


def load_player_tags() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Load player tags from 2023+ analysis"""
    tags = {"batters": {}, "bowlers": {}}
    tags_file = OUTPUT_DIR / "player_tags_2023.json"

    if tags_file.exists():
        logger.debug("Loading player tags from %s", tags_file)
        with open(tags_file, "r") as f:
            data = json.load(f)

            # Index batters by player_id
            for batter in data.get("batters", []):
                tags["batters"][batter["player_id"]] = batter

            # Index bowlers by player_id
            for bowler in data.get("bowlers", []):
                tags["bowlers"][bowler["player_id"]] = bowler

        logger.debug(
            "Loaded tags for %d batters, %d bowlers", len(tags["batters"]), len(tags["bowlers"])
        )
    else:
        logger.warning("Player tags file not found: %s", tags_file)

    return tags


def load_bowler_phase_performance() -> Dict[str, Dict[str, str]]:
    """Load bowler phase performance metrics"""
    metrics = {}
    metrics_file = OUTPUT_DIR / "metrics" / "bowler_phase_performance.csv"

    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metrics[row["bowler_id"]] = row

    return metrics


def load_batting_entry_points() -> Dict[str, Dict[str, Any]]:
    """
    Load 2023 batting entry points data for position assignment.
    This data contains mean/median entry positions for batters.
    """
    entry_points = {}
    entry_file = OUTPUT_DIR / "matchups" / "batter_entry_points_2023.csv"

    if entry_file.exists():
        with open(entry_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry_points[row["player_id"]] = {
                    "player_name": row["player_name"],
                    "avg_entry_ball": float(row["avg_entry_ball"])
                    if row.get("avg_entry_ball")
                    else None,
                    "median_entry_ball": float(row["median_entry_ball"])
                    if row.get("median_entry_ball")
                    else None,
                    "classification": row.get("entry_point_classification", ""),
                    "innings": int(row["innings"]) if row.get("innings") else 0,
                }

    return entry_points


def load_batter_metrics() -> Dict[str, Dict[str, float]]:
    """
    Load batter consistency metrics for SUPER SELECTOR v3.0 scoring.
    Includes boundary_pct and consistency_index.
    """
    metrics = {}
    metrics_file = OUTPUT_DIR / "metrics" / "batter_consistency_index.csv"

    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metrics[row["batter_id"]] = {
                    "boundary_pct": float(row["boundary_pct"]) if row.get("boundary_pct") else 0.0,
                    "consistency_index": float(row["consistency_index"])
                    if row.get("consistency_index")
                    else 0.0,
                    "high_impact_pct": float(row["high_impact_pct"])
                    if row.get("high_impact_pct")
                    else 0.0,
                    "strike_rate": float(row["overall_sr"]) if row.get("overall_sr") else 0.0,
                }

    return metrics


def load_bowler_metrics() -> Dict[str, Dict[str, float]]:
    """
    Load bowler pressure metrics for SUPER SELECTOR v3.0 scoring.
    Includes death_dot_pct and death bowling economy.
    """
    metrics = {}
    metrics_file = OUTPUT_DIR / "metrics" / "bowler_pressure_sequences.csv"

    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bowler_id = row["bowler_id"]
                pressure_type = row.get("pressure_type", "")

                # Store death pressure metrics specifically
                if pressure_type == "death_pressure":
                    metrics[bowler_id] = {
                        "death_dot_pct": float(row["pressure_dot_pct"])
                        if row.get("pressure_dot_pct")
                        else 0.0,
                        "death_economy": float(row["pressure_economy"])
                        if row.get("pressure_economy")
                        else 0.0,
                        "death_strike_rate": float(row["pressure_strike_rate"])
                        if row.get("pressure_strike_rate")
                        else 0.0,
                    }

    return metrics


# Global metrics storage (loaded once, used by scoring functions)
BATTER_METRICS = {}
BOWLER_METRICS = {}


def is_overseas_player(player_name: str) -> bool:
    """Determine if player is overseas based on name heuristics and known lists"""
    # Normalize player name for matching (strip whitespace)
    player_name = player_name.strip()

    # Known overseas players list (can be expanded)
    OVERSEAS_PLAYERS = {
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
        # Pakistani/Afghan
        "Rashid Khan",
        "Noor Ahmad",
        "Azmatullah Omarzai",
        "AM Ghazanfar",
        # Bangladesh
        "Raqibul Hasan",
        # Zimbabwe
        "Sikandar Raza",
        # Others
        "Pathum Nissanka",
        "Kyle Jamieson",
        "Dushmantha Chameera",
        "Brydon Carse",
        "Jack Edwards",
        "Zak Foulkes",
    }

    return player_name in OVERSEAS_PLAYERS


def build_players(
    squads: Dict[str, List[Dict[str, str]]],
    contracts: Dict[str, Dict[str, Any]],
    tags: Dict[str, Dict[str, Dict[str, Any]]],
) -> Dict[str, List[Player]]:
    """Build Player objects for all teams"""
    team_players = {}

    for team, squad in squads.items():
        players = []

        for row in squad:
            player_name = row["player_name"]
            player_id = row["player_id"]

            # Get contract info
            contract_key = f"{team}|{player_name}"
            contract = contracts.get(contract_key, {"price_cr": 0.0})

            # Get tags
            batter_info = tags["batters"].get(player_id, {})
            bowler_info = tags["bowlers"].get(player_id, {})

            # Parse batter/bowler tags from squad data
            batter_tags = row.get("batter_tags", "").split("|") if row.get("batter_tags") else []
            bowler_tags = row.get("bowler_tags", "").split("|") if row.get("bowler_tags") else []

            # Merge with tags from player_tags_2023.json for enhanced scoring
            # Add batter tags from analysis (phase-specific tags)
            for tag in batter_info.get("tags", []):
                if tag not in batter_tags:
                    batter_tags.append(tag)

            # Add bowler tags from analysis (phase-specific tags)
            for tag in bowler_info.get("tags", []):
                if tag not in bowler_tags:
                    bowler_tags.append(tag)

            player = Player(
                player_id=player_id,
                player_name=player_name,
                team=team,
                role=row["role"],
                batting_hand=row.get("batting_hand", "Right-hand"),
                bowling_arm=row.get("bowling_arm"),
                bowling_type=row.get("bowling_type"),
                price_cr=contract.get("price_cr", 0.0),
                is_overseas=is_overseas_player(player_name),
                batter_classification=row.get("batter_classification"),
                bowler_classification=row.get("bowler_classification"),
                batter_tags=batter_tags,
                bowler_tags=bowler_tags,
            )

            players.append(player)

        team_players[team] = players

    return team_players


# =============================================================================
# SCORING FUNCTIONS
# =============================================================================

# Auction price tier bonuses (from PRD)
AUCTION_PRICE_BONUS = {
    15.0: 0.15,  # 15+ Cr: +15%
    10.0: 0.10,  # 10-15 Cr: +10%
    5.0: 0.05,  # 5-10 Cr: +5%
    0.0: 0.0,  # < 5 Cr: no bonus
}


def get_auction_bonus(price_cr: float) -> float:
    """Get auction price bonus multiplier"""
    if price_cr >= 15.0:
        return 0.15
    elif price_cr >= 10.0:
        return 0.10
    elif price_cr >= 5.0:
        return 0.05
    return 0.0


def score_batter(player: Player) -> float:
    """
    Score a player for batting capability.
    SUPER SELECTOR v3.0: Includes metrics-based scoring.
    """
    base_score = 50.0

    # Classification bonuses (SUPER SELECTOR v3.0)
    classification_scores = {
        "Elite Top-Order": 30,
        "Power Finisher": 25,
        "Aggressive Opener": 25,
        "All-Round Finisher": 20,
        "Anchor": 15,
        "ACCUMULATOR": 12,  # NEW: Added for players like Shivam Dube
    }
    base_score += classification_scores.get(player.batter_classification, 0)

    # Tag bonuses (SUPER SELECTOR v3.0)
    tag_bonuses = {
        "EXPLOSIVE_OPENER": 10,
        "PP_DOMINATOR": 8,
        "DEATH_SPECIALIST": 10,
        "SIX_HITTER": 8,
        "FINISHER": 12,
        "CONSISTENT": 8,
        "MIDDLE_ORDER": 5,
        "PLAYMAKER": 8,
        "MIDDLE_OVERS_ACCELERATOR": 7,
        "SPIN_SPECIALIST": 5,
        "PACE_SPECIALIST": 5,
        "ANCHOR": 5,
        "ACCUMULATOR": 8,  # NEW: Reliable run-scorers get bonus
    }

    for tag in player.batter_tags:
        base_score += tag_bonuses.get(tag, 0)

    # =========================================================================
    # SUPER SELECTOR v3.0: Metrics-Based Scoring
    # =========================================================================
    metrics = BATTER_METRICS.get(player.player_id, {})

    # Batting Efficiency (boundary percentage)
    boundary_pct = metrics.get("boundary_pct", 0.0)
    if boundary_pct >= 28:
        base_score += 15
    elif boundary_pct >= 24:
        base_score += 10
    elif boundary_pct >= 20:
        base_score += 5

    # Consistency Bonus
    consistency_index = metrics.get("consistency_index", 0.0)
    if consistency_index >= 55:
        base_score += 8
    elif consistency_index >= 45:
        base_score += 4

    # High Impact Innings Bonus
    high_impact_pct = metrics.get("high_impact_pct", 0.0)
    if high_impact_pct >= 50:
        base_score += 6
    elif high_impact_pct >= 35:
        base_score += 3
    # =========================================================================

    # Auction price bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    return min(base_score, 100.0)


def score_bowler(player: Player) -> float:
    """
    Score a player for bowling capability.
    SUPER SELECTOR v3.0: Includes metrics-based scoring.
    """
    if not player.can_bowl:
        return 0.0

    base_score = 40.0

    # Classification bonuses
    classification_scores = {
        "Powerplay Assassin": 25,
        "Middle-Overs Spinner": 25,
        "Workhorse Seamer": 20,
        "Holding Spinner": 15,
        "Expensive Option": 5,
    }
    base_score += classification_scores.get(player.bowler_classification, 0)

    # Tag bonuses from squad data (bowler_tags column)
    tag_bonuses = {
        "DEATH_SPECIALIST": 12,
        "DEATH_ELITE": 15,
        "PP_ELITE": 12,
        "NEW_BALL_SPECIALIST": 10,
        "PROVEN_WICKET_TAKER": 10,
        "PRESSURE_BUILDER": 8,
        "MID_OVERS_ELITE": 10,
        "MIDDLE_OVERS_CONTROLLER": 8,
        "WORKHORSE": 5,
        "PART_TIMER": -5,
        # Additional tags from player_tags_2023.json (bowlers section)
        "PP_STRIKE": 12,  # Powerplay strike bowler
        "PP_CONTAINER": 8,  # Powerplay container
        "PP_LIABILITY": -8,  # Weak in powerplay
        "MIDDLE_STRANGLER": 10,  # Middle overs specialist
        "MIDDLE_WICKET_TAKER": 8,
        "MIDDLE_LIABILITY": -5,
        "DEATH_STRIKE": 12,  # Death over strike bowler
        "DEATH_CONTAINER": 8,  # Death over container
        "DEATH_COMPLETE": 12,  # Can both strike and contain at death
        "DEATH_LIABILITY": -8,
        "RHB_SPECIALIST": 3,  # Matchup bonuses
        "LHB_SPECIALIST": 3,
        "RHB_WICKET_TAKER": 5,
        "LHB_WICKET_TAKER": 5,
        "RHB_VULNERABLE": -3,
        "LHB_VULNERABLE": -3,
    }

    for tag in player.bowler_tags:
        base_score += tag_bonuses.get(tag, 0)

    # =========================================================================
    # SUPER SELECTOR v3.0: Metrics-Based Scoring
    # =========================================================================
    metrics = BOWLER_METRICS.get(player.player_id, {})

    # Bowling Pressure (death overs dot ball percentage)
    death_dot_pct = metrics.get("death_dot_pct", 0.0)
    if death_dot_pct >= 35:
        base_score += 15
    elif death_dot_pct >= 30:
        base_score += 10
    elif death_dot_pct >= 25:
        base_score += 5

    # Death Overs Economy Bonus
    death_economy = metrics.get("death_economy", 0.0)
    if death_economy > 0:  # Only if data exists
        if death_economy <= 7.0:
            base_score += 12
        elif death_economy <= 8.5:
            base_score += 6
        elif death_economy >= 10.5:
            base_score -= 5  # Penalty for expensive death bowling
    # =========================================================================

    # Auction price bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    return min(base_score, 100.0)


def score_player(player: Player) -> None:
    """Calculate overall player score."""
    player.batting_score = score_batter(player)
    player.bowling_score = score_bowler(player)

    # Compute overall based on role
    if player.role == "Bowler":
        player.overall_score = player.bowling_score * 0.85 + player.batting_score * 0.15
    elif player.role == "All-rounder":
        # Check if batting or bowling all-rounder based on tags/classification
        if player.batter_classification in ["All-Round Finisher", "Power Finisher"]:
            # Batting all-rounder: 60% bat / 40% bowl
            player.overall_score = player.batting_score * 0.60 + player.bowling_score * 0.40
        elif player.bowler_classification in [
            "Middle-Overs Spinner",
            "Powerplay Assassin",
        ]:
            # Bowling all-rounder: 40% bat / 60% bowl
            player.overall_score = player.batting_score * 0.40 + player.bowling_score * 0.60
        else:
            # True all-rounder: 50/50
            player.overall_score = player.batting_score * 0.50 + player.bowling_score * 0.50
    elif player.role == "Wicketkeeper":
        player.overall_score = player.batting_score * 0.90 + 10  # Keeper bonus
    else:  # Batter
        player.overall_score = player.batting_score


# =============================================================================
# CONSTRAINT CHECKING
# =============================================================================


def check_constraints(xi: List[SelectedPlayer]) -> Tuple[bool, List[str]]:
    """
    Check hard constraints from PRD:
    C1: Maximum 4 overseas players
    C2: Minimum 5 bowling options (20 overs coverage)
    C3: At least 1 wicketkeeper
    C4: Minimum 4 primary bowling options (bowlers + bowling all-rounders)
    C5: At least 1 spinner
    """
    violations = []
    players = [sp.player for sp in xi]

    # C1: Overseas limit
    overseas_count = sum(1 for p in players if p.is_overseas)
    if overseas_count > 4:
        violations.append(f"C1: Overseas limit exceeded ({overseas_count}/4)")

    # C2: Bowling coverage (need 20 overs from 5+ options)
    bowling_overs = sum(p.bowling_overs_capability for p in players if p.can_bowl)
    bowling_options = sum(1 for p in players if p.can_bowl and p.bowling_overs_capability >= 4)
    if bowling_overs < 20:
        violations.append(f"C2: Insufficient bowling coverage ({bowling_overs}/20 overs)")
    if bowling_options < 5:
        violations.append(f"C2: Insufficient bowling options ({bowling_options}/5 required)")

    # C3: Wicketkeeper
    keepers = sum(1 for p in players if p.is_wicketkeeper)
    if keepers < 1:
        violations.append("C3: No wicketkeeper in XI")

    # C4: Primary bowling options - bowlers OR bowling all-rounders who can bowl 4 overs
    # In T20, all-rounders like Jadeja, Axar, Hardik count as bowling options
    # Bowlers always count, all-rounders with classification or can_bowl count
    primary_bowlers = sum(
        1
        for p in players
        if p.bowling_overs_capability >= 4
        and (
            p.role == "Bowler"
            or (p.role == "All-rounder" and (p.bowler_classification or p.can_bowl))
        )
    )
    if primary_bowlers < 4:
        violations.append(f"C4: Insufficient primary bowling options ({primary_bowlers}/4)")

    # C5: Spinner
    spinners = sum(1 for p in players if p.is_spinner)
    if spinners < 1:
        violations.append("C5: No spinner in XI")

    return len(violations) == 0, violations


def get_balance_metrics(xi: List[SelectedPlayer]) -> Dict[str, int]:
    """Calculate balance metrics for the XI"""
    players = [sp.player for sp in xi]

    return {
        "overseas_count": sum(1 for p in players if p.is_overseas),
        "bowling_options": sum(
            1 for p in players if p.can_bowl and p.bowling_overs_capability >= 4
        ),
        "total_bowling_overs": sum(p.bowling_overs_capability for p in players if p.can_bowl),
        "spinners": sum(1 for p in players if p.is_spinner),
        "pacers": sum(1 for p in players if p.is_pacer),
        "wicketkeepers": sum(1 for p in players if p.is_wicketkeeper),
        "left_handers_top6": sum(1 for sp in xi[:6] if sp.player.batting_hand == "Left-hand"),
        "left_handers_total": sum(1 for p in players if p.batting_hand == "Left-hand"),
    }


# =============================================================================
# SELECTION ALGORITHM
# =============================================================================


def get_role_candidates(players: List[Player], role: str) -> List[Player]:
    """Get candidates for a specific role"""
    candidates = []

    if role == "opener":
        # Aggressive openers, top-order batters
        for p in players:
            if any(
                tag in p.batter_tags for tag in ["EXPLOSIVE_OPENER", "PP_DOMINATOR", "PLAYMAKER"]
            ):
                candidates.append(p)
            elif p.batter_classification in ["Aggressive Opener", "Elite Top-Order"]:
                candidates.append(p)

    elif role == "anchor":
        # Middle-order anchors
        for p in players:
            if p.batter_classification in [
                "Elite Top-Order",
                "Anchor",
                "All-Round Finisher",
            ]:
                candidates.append(p)
            elif "MIDDLE_ORDER" in p.batter_tags or "ANCHOR" in p.batter_tags:
                candidates.append(p)

    elif role == "finisher":
        # Death-overs finishers
        for p in players:
            if any(tag in p.batter_tags for tag in ["FINISHER", "DEATH_SPECIALIST", "SIX_HITTER"]):
                candidates.append(p)
            elif p.batter_classification in ["Power Finisher", "All-Round Finisher"]:
                candidates.append(p)

    elif role == "wicketkeeper":
        candidates = [p for p in players if p.is_wicketkeeper]

    elif role == "spinner":
        candidates = [p for p in players if p.is_spinner and p.bowling_overs_capability >= 4]

    elif role == "pacer":
        candidates = [p for p in players if p.is_pacer and p.bowling_overs_capability >= 4]

    elif role == "all_rounder":
        candidates = [p for p in players if p.role == "All-rounder" and p.can_bowl]

    elif role == "bowling_all_rounder":
        # All-rounders who are primarily bowlers (have bowler classification)
        candidates = [
            p
            for p in players
            if p.role == "All-rounder"
            and p.bowler_classification
            and p.bowling_overs_capability >= 4
        ]

    elif role == "primary_bowler":
        # Any player who can reliably bowl 4 overs (bowlers + bowling all-rounders)
        candidates = [
            p
            for p in players
            if p.bowling_overs_capability >= 4 and (p.role == "Bowler" or p.bowler_classification)
        ]

    return sorted(candidates, key=lambda x: x.overall_score, reverse=True)


def generate_rationale(player: Player, role_in_xi: str) -> str:
    """Generate selection rationale for a player"""
    rationales = []

    # Price-based
    if player.price_cr >= 15:
        rationales.append(f"Franchise cornerstone at Rs {player.price_cr:.1f} Cr")
    elif player.price_cr >= 10:
        rationales.append(f"Key player investment ({player.price_cr:.1f} Cr)")

    # Classification-based
    if player.batter_classification:
        if player.batter_classification == "Elite Top-Order":
            rationales.append("Elite top-order anchor")
        elif player.batter_classification == "Power Finisher":
            rationales.append("Explosive death-overs finisher")
        elif player.batter_classification == "Aggressive Opener":
            rationales.append("Powerplay aggressor")

    if player.bowler_classification:
        if player.bowler_classification == "Powerplay Assassin":
            rationales.append("New ball specialist")
        elif player.bowler_classification == "Middle-Overs Spinner":
            rationales.append("Spin bowling strength in middle overs")

    # Tag-based
    key_tags = []
    for tag in player.batter_tags + player.bowler_tags:
        if tag in ["DEATH_ELITE", "PP_ELITE", "PROVEN_WICKET_TAKER"]:
            key_tags.append(tag.replace("_", " ").lower())

    if key_tags:
        rationales.append(f"Tagged: {', '.join(key_tags[:2])}")

    # Default
    if not rationales:
        if player.role == "All-rounder":
            rationales.append("Provides batting depth and bowling option")
        elif player.role == "Bowler":
            rationales.append(f"{'Spin' if player.is_spinner else 'Pace'} bowling depth")
        elif player.is_wicketkeeper:
            rationales.append("Primary wicketkeeper")
        else:
            rationales.append("Batting value")

    return ". ".join(rationales[:2])


def select_xi(
    team: str,
    players: List[Player],
    venue_bias: str,
    entry_points: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Tuple[List[SelectedPlayer], List[str]]:
    """
    Select optimal XI using constraint-satisfaction algorithm

    Algorithm:
    1. First pass: Filter candidates by role eligibility
    2. Second pass: Apply metric-based scoring within each role
    3. Third pass: Optimize for balance
    4. Final pass: Verify constraints
    """
    notes = []

    # Score all players
    for p in players:
        score_player(p)

    # Track selected players and remaining pool
    selected = []
    remaining = players.copy()

    def select_player(player: Player, position: int, role: str) -> None:
        """Add player to selection"""
        sp = SelectedPlayer(
            player=player,
            batting_position=position,
            role_in_xi=role,
            rationale=generate_rationale(player, role),
        )
        selected.append(sp)
        if player in remaining:
            remaining.remove(player)

    def count_overseas() -> int:
        return sum(1 for sp in selected if sp.player.is_overseas)

    def can_add_overseas() -> bool:
        return count_overseas() < 4

    def get_available(candidates: list) -> list:
        """Filter candidates that are still available and respect overseas limit"""
        available = [p for p in candidates if p in remaining]
        # If we're at overseas limit, filter out overseas players
        if count_overseas() >= 4:
            available = [p for p in available if not p.is_overseas]
        return available

    # ==========================================================================
    # SELECTION ORDER (Role-based)
    # ==========================================================================

    # 1. Select wicketkeeper (MUST have one)
    keepers = get_available(get_role_candidates(remaining, "wicketkeeper"))
    if keepers:
        select_player(keepers[0], 1, "Wicketkeeper")
        notes.append(f"Selected {keepers[0].player_name} as keeper")
    else:
        notes.append("WARNING: No wicketkeeper available!")

    # 2. Select openers (need aggressive opener)
    openers = get_available(get_role_candidates(remaining, "opener"))
    opener_positions = []

    # If keeper is an opener type, they open
    if selected and selected[0].player.batter_classification == "Aggressive Opener":
        opener_positions.append(1)
        notes.append(f"{selected[0].player.player_name} to open (keeper)")

    # Select 1-2 more openers
    for opener in openers[:2]:
        if len(opener_positions) < 2:
            pos = 1 if not opener_positions else 2
            select_player(opener, pos, "Opener")
            opener_positions.append(pos)

    # 3. Select anchors for positions 3-4
    anchors = get_available(get_role_candidates(remaining, "anchor"))
    for i, anchor in enumerate(anchors[:2]):
        select_player(anchor, 3 + i, "Middle Order")

    # 4. Select finishers for positions 5-6
    finishers = get_available(get_role_candidates(remaining, "finisher"))
    for i, finisher in enumerate(finishers[:2]):
        select_player(finisher, 5 + i, "Finisher")

    # 5. Select all-rounders (if not enough batting already)
    if len(selected) < 7:
        all_rounders = get_available(get_role_candidates(remaining, "all_rounder"))
        for ar in all_rounders:
            if len(selected) < 7:
                select_player(ar, len(selected) + 1, "All-rounder")

    # 6. Select spinners
    # Adjust based on venue bias
    min_spinners = 1
    if venue_bias == "spin":
        min_spinners = 2

    spinners = get_available(get_role_candidates(remaining, "spinner"))
    spinners_selected = sum(1 for sp in selected if sp.player.is_spinner)

    while spinners_selected < min_spinners and spinners:
        spinner = spinners.pop(0)
        select_player(spinner, len(selected) + 1, "Spinner")
        spinners_selected += 1

    # 7. Select pace bowlers
    pacers = get_available(get_role_candidates(remaining, "pacer"))
    pacers_selected = sum(1 for sp in selected if sp.player.is_pacer and sp.player.role == "Bowler")

    # Need at least 3 pacers typically
    while pacers_selected < 3 and pacers and len(selected) < 11:
        pacer = pacers.pop(0)
        select_player(pacer, len(selected) + 1, "Pace Bowler")
        pacers_selected += 1

    # 8. Fill remaining slots with best available
    while len(selected) < 11:
        available = get_available(remaining)
        if not available:
            notes.append("WARNING: Not enough players to complete XI!")
            break

        # Sort by overall score and pick best
        available.sort(key=lambda x: x.overall_score, reverse=True)
        best = available[0]

        # Determine role
        if best.role == "Bowler":
            role = "Spinner" if best.is_spinner else "Pace Bowler"
        elif best.role == "All-rounder":
            role = "All-rounder"
        else:
            role = "Batter"

        select_player(best, len(selected) + 1, role)

    # 9. OVERSEAS OPTIMIZATION: Target exactly 4 overseas players
    # Per algorithm spec v2: Teams should maximize overseas slots (up to 4)
    current_overseas = sum(1 for sp in selected if sp.player.is_overseas)
    if current_overseas < 4:
        # Find available overseas players not in XI
        available_overseas = [p for p in remaining if p.is_overseas]
        available_overseas.sort(key=lambda x: x.overall_score, reverse=True)

        # Find Indian players in XI that can be swapped (not keeper, not highest-value)
        swappable_indians = []
        for sp in selected:
            if not sp.player.is_overseas and not sp.player.is_wicketkeeper:
                # Don't swap very high-value players unless necessary
                swappable_indians.append(sp)

        # Sort swappable by score (lowest first - swap worst Indian players)
        swappable_indians.sort(key=lambda x: x.player.overall_score)

        # Perform swaps
        swaps_made = 0
        max_swaps = 4 - current_overseas
        for overseas_player in available_overseas:
            if swaps_made >= max_swaps:
                break
            if not swappable_indians:
                break

            # Find a suitable Indian to swap - prefer same role category
            swap_target = None
            for indian_sp in swappable_indians:
                # Check role compatibility (bowling capability matters most)
                indian_can_bowl = indian_sp.player.can_bowl
                overseas_can_bowl = overseas_player.can_bowl

                # Ensure we don't break bowling constraints
                if indian_can_bowl and not overseas_can_bowl:
                    # Would lose a bowling option - check if we have enough
                    bowling_options = sum(
                        1
                        for sp in selected
                        if sp.player.can_bowl and sp.player.bowling_overs_capability >= 4
                    )
                    if bowling_options <= 5:
                        continue  # Skip this swap

                swap_target = indian_sp
                break

            if swap_target:
                # Perform the swap
                selected.remove(swap_target)
                remaining.append(swap_target.player)
                remaining.remove(overseas_player)
                swappable_indians.remove(swap_target)

                new_sp = SelectedPlayer(
                    player=overseas_player,
                    batting_position=swap_target.batting_position,
                    role_in_xi=swap_target.role_in_xi,
                    rationale=generate_rationale(overseas_player, swap_target.role_in_xi),
                )
                selected.append(new_sp)
                swaps_made += 1
                notes.append(
                    f"Overseas optimization: Swapped {swap_target.player.player_name} "
                    f"for {overseas_player.player_name}"
                )

    # 10. Reorder batting positions based on role/classification and historical data
    selected = reorder_batting_positions(selected, entry_points)

    # Check constraints
    constraints_ok, violations = check_constraints(selected)
    if not constraints_ok:
        notes.append(f"Constraint violations: {violations}")
        # Attempt backtracking fixes
        selected, violations = fix_constraint_violations(selected, remaining, violations)
        constraints_ok = len(violations) == 0

    return selected, remaining, constraints_ok, violations, notes


def _get_batting_tier(player: SelectedPlayer, entry_points: Dict[str, Dict[str, Any]]) -> int:
    """
    Determine batting tier (1-5) based on ENTRY POINT DATA as primary signal.

    SUPER SELECTOR v3.0: Entry points are the PRIMARY position validator.

    Tiers based on avg_entry_ball:
    1 = Opener (0-15 balls / overs 1-2.5)
    2 = Top Order (16-40 balls / overs 3-7)  -> Positions 3-4
    3 = Middle Order (41-70 balls / overs 7-12) -> Positions 5-6
    4 = Finisher (71-100 balls / overs 12-17) -> Positions 7-8
    5 = Bowler (100+ balls or no batting data) -> Positions 9-11

    Args:
        player: SelectedPlayer to evaluate
        entry_points: Dictionary of player entry point data

    Returns:
        int: Batting tier (1-5)
    """
    p = player.player
    pid = p.player_id

    # Get historical entry point - THIS IS THE PRIMARY SIGNAL
    entry_data = entry_points.get(pid, {})
    avg_entry = entry_data.get("avg_entry_ball")
    entry_class = entry_data.get("classification", "")

    # PRIORITY 1: BOWLERS ALWAYS BAT 9-11 (regardless of entry point)
    # Exception: All-rounders with batting classification
    if p.role == "Bowler":
        # Only exception: if they have significant batting classification
        if p.batter_classification in [
            "Power Finisher",
            "All-Round Finisher",
            "Aggressive Opener",
        ]:
            pass  # Let them be placed by entry point
        else:
            return 5  # Bowlers bat last

    # PRIORITY 2: Spinners who are primarily bowlers bat 9-11
    if p.is_spinner and p.role == "Bowler":
        return 5

    # PRIORITY 3: Entry Point Data (PRIMARY POSITION VALIDATOR)
    if avg_entry is not None:
        if avg_entry <= 12:
            return 1
        elif avg_entry <= 45:
            return 2
        elif avg_entry <= 75:
            return 3
        elif avg_entry <= 105:
            return 4
        else:
            return 5

    # PRIORITY 4: Entry classification from CSV
    if entry_class == "TOP_ORDER":
        return 2
    if entry_class == "MIDDLE_ORDER":
        return 3
    if entry_class == "LOWER_ORDER":
        return 4

    # PRIORITY 5: Classification-based (fallback when no entry data)
    if p.batter_classification == "Aggressive Opener":
        return 1
    if p.batter_classification == "Elite Top-Order":
        return 2
    if p.batter_classification == "Anchor":
        return 3
    if p.batter_classification in ["Power Finisher", "All-Round Finisher"]:
        return 3

    # PRIORITY 6: Tag-based fallback
    opener_tags = ["EXPLOSIVE_OPENER", "PP_DOMINATOR"]
    middle_tags = ["ANCHOR", "ACCUMULATOR", "MIDDLE_ORDER"]
    finisher_tags = ["FINISHER", "DEATH_SPECIALIST", "SIX_HITTER"]

    if any(tag in p.batter_tags for tag in opener_tags):
        return 1
    if any(tag in p.batter_tags for tag in middle_tags):
        return 3
    if any(tag in p.batter_tags for tag in finisher_tags):
        return 4

    # PRIORITY 7: Role-based fallback
    if p.role == "All-rounder":
        if p.batter_classification:
            return 3
        return 4
    if p.role in ["Batter", "Wicketkeeper"]:
        return 2

    return 4


def _get_tier_score(player: SelectedPlayer, tier: int) -> float:
    """
    Get sorting score within a tier (higher = better).

    Args:
        player: SelectedPlayer to score
        tier: The batting tier (1-5)

    Returns:
        float: Score for sorting within the tier
    """
    p = player.player
    base_score = p.batting_score

    # Wicketkeepers get bonus to keep together with other batters
    if p.is_wicketkeeper:
        base_score += 5

    # Price bonus
    if p.price_cr >= 15:
        base_score += 15
    elif p.price_cr >= 10:
        base_score += 10
    elif p.price_cr >= 5:
        base_score += 5

    # Tier-specific bonuses
    if tier == 1:
        if "EXPLOSIVE_OPENER" in p.batter_tags:
            base_score += 10
        if "PP_DOMINATOR" in p.batter_tags:
            base_score += 8

    if tier in [2, 3]:
        if "ANCHOR" in p.batter_tags:
            base_score += 5
        if "CONSISTENT" in p.batter_tags:
            base_score += 5

    if tier == 4:
        if "FINISHER" in p.batter_tags:
            base_score += 10
        if "DEATH_SPECIALIST" in p.batter_tags:
            base_score += 8
        if "SIX_HITTER" in p.batter_tags:
            base_score += 5

    return base_score


def _assign_positions_by_tier(
    tiers: Dict[int, List[SelectedPlayer]], entry_points: Dict[str, Dict[str, Any]]
) -> Tuple[List[SelectedPlayer], int]:
    """
    Assign batting positions based on tier categorization.

    SUPER SELECTOR v3.0: Strict entry-point based position assignment.
    Tiers stay in their designated positions with minimal pulling up/down.

    Args:
        tiers: Dictionary mapping tier number to list of players
        entry_points: Player entry point data for flex placement

    Returns:
        Tuple of (batting_order list, next position number)
    """
    batting_order = []
    position = 1

    def add_to_order(sp, pos):
        sp.batting_position = pos
        batting_order.append(sp)

    # Positions 1-2: Openers (tier 1 ONLY)
    for sp in tiers[1][:2]:
        add_to_order(sp, position)
        position += 1

    # Fill from tier 2 if needed
    tier2_used = 0
    while position <= 2 and tier2_used < len(tiers[2]):
        add_to_order(tiers[2][tier2_used], position)
        position += 1
        tier2_used += 1

    # Positions 3-4: Top Order (tier 2 + extra tier 1)
    tier1_remaining = tiers[1][2:]
    for sp in tier1_remaining:
        if position <= 4:
            add_to_order(sp, position)
            position += 1

    for sp in tiers[2][tier2_used:]:
        if position <= 4:
            add_to_order(sp, position)
            position += 1

    # Flexible tier 3 placement
    tier3_sorted = sorted(
        tiers[3],
        key=lambda x: entry_points.get(x.player.player_id, {}).get("avg_entry_ball", 999),
    )

    if position == 4 and tier3_sorted:
        flex_player = tier3_sorted.pop(0)
        add_to_order(flex_player, 4)
        position = 5

    position = max(position, 5)

    # Positions 5-6: Middle Order
    for sp in tier3_sorted:
        if position <= 6:
            add_to_order(sp, position)
            position += 1

    # Flexible tier 4 placement
    tier4_sorted = sorted(
        tiers[4],
        key=lambda x: entry_points.get(x.player.player_id, {}).get("avg_entry_ball", 999),
    )

    while position <= 6 and tier4_sorted:
        flex_player = tier4_sorted.pop(0)
        add_to_order(flex_player, position)
        position += 1

    position = max(position, 7)

    # Positions 7-8: Finishers
    for sp in tier4_sorted:
        if position <= 8:
            add_to_order(sp, position)
            position += 1

    position = max(position, 9)

    # Positions 9-11: Bowlers
    for sp in tiers[5]:
        if sp not in batting_order and position <= 11:
            add_to_order(sp, position)
            position += 1

    return batting_order, position


def _fill_remaining_positions(
    batting_order: List[SelectedPlayer], tiers: Dict[int, List[SelectedPlayer]]
) -> List[SelectedPlayer]:
    """
    Fill any empty batting positions with remaining players.

    Priority: Keep batters/all-rounders in TOP 6, bowlers in 7-11.

    Args:
        batting_order: Current batting order
        tiers: Dictionary of tiered players

    Returns:
        Complete batting order with all positions filled
    """
    filled_positions = {sp.batting_position for sp in batting_order}

    # Collect remaining players
    remaining_batters = []
    remaining_bowlers = []

    for tier_num in [1, 2, 3, 4, 5]:
        for sp in tiers[tier_num]:
            if sp not in batting_order:
                if sp.player.role in ["Batter", "Wicketkeeper"]:
                    remaining_batters.append(sp)
                elif sp.player.role == "All-rounder":
                    if sp.player.batter_classification or sp.player.batting_score > 50:
                        remaining_batters.append(sp)
                    else:
                        remaining_bowlers.append(sp)
                else:
                    remaining_bowlers.append(sp)

    remaining_batters.sort(key=lambda x: x.player.batting_score, reverse=True)
    remaining_bowlers.sort(key=lambda x: x.player.overall_score, reverse=True)

    # Fill TOP 6 with batters
    for pos in range(1, 7):
        if pos not in filled_positions and remaining_batters:
            player_to_add = remaining_batters.pop(0)
            player_to_add.batting_position = pos
            batting_order.append(player_to_add)
            filled_positions.add(pos)

    # Fill 7-11 with remaining (bowlers first)
    all_remaining = remaining_bowlers + remaining_batters
    for pos in range(7, 12):
        if pos not in filled_positions and all_remaining:
            player_to_add = all_remaining.pop(0)
            player_to_add.batting_position = pos
            batting_order.append(player_to_add)
            filled_positions.add(pos)

    # Final fallback for top 6
    all_remaining = remaining_batters + remaining_bowlers
    for pos in range(1, 7):
        if pos not in filled_positions and all_remaining:
            player_to_add = all_remaining.pop(0)
            player_to_add.batting_position = pos
            batting_order.append(player_to_add)
            filled_positions.add(pos)

    return batting_order


def reorder_batting_positions(
    selected: List[SelectedPlayer], entry_points: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[SelectedPlayer]:
    """
    Reorder players into proper batting positions.

    Uses hierarchical priority system:
    1. Historical 2023 batting entry point data (mean/median position)
    2. Player batter tags (PP_DOMINATOR, EXPLOSIVE_OPENER, FINISHER, etc.)
    3. Role-based classification

    Position assignment logic:
    - Positions 1-2 (Openers): Low avg_entry_ball (<20) OR EXPLOSIVE_OPENER/PP_DOMINATOR tags
    - Positions 3-4 (Top Order): Mid entry (20-40) OR ANCHOR/MIDDLE_ORDER tags
    - Positions 5-6 (Middle Order): Mid-high entry (40-70) OR MIDDLE_OVERS_ACCELERATOR tags
    - Positions 7-8 (Finisher/All-rounders): High entry (70+) OR FINISHER/DEATH_SPECIALIST tags
    - Positions 9-11 (Bowlers): Purely based on bowling role

    Args:
        selected: List of SelectedPlayer objects to reorder
        entry_points: Optional dictionary of batting entry point data

    Returns:
        List[SelectedPlayer]: Reordered batting lineup
    """
    if entry_points is None:
        entry_points = {}

    # Categorize players into tiers
    tiers: Dict[int, List[SelectedPlayer]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for sp in selected:
        tier = _get_batting_tier(sp, entry_points)
        tiers[tier].append(sp)

    # Sort each tier by score
    for tier_num in tiers:
        tiers[tier_num].sort(key=lambda x: _get_tier_score(x, tier_num), reverse=True)

    # Assign positions by tier
    batting_order, position = _assign_positions_by_tier(tiers, entry_points)

    # Fill remaining positions
    batting_order = _fill_remaining_positions(batting_order, tiers)

    # Ensure exactly 11 players
    batting_order = batting_order[:11]

    # Sort by position
    batting_order.sort(key=lambda x: x.batting_position)

    # Handle any overflow
    for tier_num in [2, 3, 4]:
        for sp in tiers[tier_num]:
            if sp not in batting_order:
                sp.batting_position = position
                batting_order.append(sp)
                position += 1

    return batting_order


def fix_constraint_violations(
    selected: List[SelectedPlayer], remaining: List[Player], violations: List[str]
) -> Tuple[List[SelectedPlayer], List[str]]:
    """Attempt to fix constraint violations via substitution"""
    # This is a simplified backtracking - for V1, we just note violations
    # A more sophisticated version would swap players

    return selected, violations


def select_impact_player(
    xi: List[SelectedPlayer], remaining: List[Player], captain_name: Optional[str] = None
) -> Optional[SelectedPlayer]:
    """
    Select the Impact Player (12th man).

    Per IPL rules and algorithm spec v2 constraint C1:
    The designated team captain is EXCLUDED from impact player selection.
    """
    # Score remaining players
    for p in remaining:
        score_player(p)

    # Get XI composition
    xi_players = [sp.player for sp in xi]
    has_spinner = any(p.is_spinner for p in xi_players)
    batting_depth = sum(1 for p in xi_players if p.batting_score > 50)

    # Find best complement
    candidates = remaining.copy()

    # CONSTRAINT C1: Captain CANNOT be Impact Player (IPL rule)
    if captain_name:
        candidates = [p for p in candidates if p.player_name != captain_name]

    # Filter out overseas if XI has 4
    overseas_in_xi = sum(1 for p in xi_players if p.is_overseas)
    if overseas_in_xi >= 4:
        candidates = [p for p in candidates if not p.is_overseas]

    if not candidates:
        return None

    # Sort by overall score
    candidates.sort(key=lambda x: x.overall_score, reverse=True)

    # Pick based on XI needs
    impact = None

    # If XI lacks spinner, prioritize spinner as impact
    if not has_spinner:
        spinner_candidates = [p for p in candidates if p.is_spinner]
        if spinner_candidates:
            impact = spinner_candidates[0]

    # If XI needs batting depth, pick batter/all-rounder
    if not impact and batting_depth < 7:
        batting_candidates = [
            p for p in candidates if p.role in ["Batter", "All-rounder", "Wicketkeeper"]
        ]
        if batting_candidates:
            impact = batting_candidates[0]

    # If not found, pick best overall
    if not impact:
        impact = candidates[0]

    return SelectedPlayer(
        player=impact,
        batting_position=12,
        role_in_xi="Impact Player",
        rationale=f"Provides {'batting depth' if impact.batting_score > impact.bowling_score else 'bowling option'} as Impact substitute",
        is_impact_player=True,
    )


def identify_captain(
    xi: List[SelectedPlayer], team: str, squad_captains: Optional[Dict[str, str]] = None
) -> str:
    """
    Identify captain from CSV is_captain field first, then fall back to known list.

    Per algorithm spec v2: Captain is read from ipl_2026_squads.csv is_captain=TRUE field.
    """
    # PRIORITY 1: Use captain from squad CSV data (is_captain=TRUE)
    if squad_captains and team in squad_captains:
        csv_captain = squad_captains[team]
        # Verify captain is in XI
        for sp in xi:
            if sp.player.player_name == csv_captain:
                return csv_captain
        # If CSV captain not in XI, still return them (they should be selected)
        return csv_captain

    # PRIORITY 2: Fallback to known captains (legacy)
    KNOWN_CAPTAINS = {
        "Chennai Super Kings": "Ruturaj Gaikwad",
        "Mumbai Indians": "Hardik Pandya",
        "Royal Challengers Bengaluru": "Rajat Patidar",
        "Kolkata Knight Riders": "Ajinkya Rahane",
        "Delhi Capitals": "Axar Patel",
        "Punjab Kings": "Shreyas Iyer",
        "Rajasthan Royals": "Riyan Parag",
        "Sunrisers Hyderabad": "Pat Cummins",
        "Gujarat Titans": "Shubman Gill",
        "Lucknow Super Giants": "Rishabh Pant",
    }

    # Check if known captain is in XI
    known = KNOWN_CAPTAINS.get(team)
    for sp in xi:
        if sp.player.player_name == known:
            return known

    # Otherwise pick highest priced player
    xi_sorted = sorted(xi, key=lambda x: x.player.price_cr, reverse=True)
    return xi_sorted[0].player.player_name


def identify_keeper(xi: List[SelectedPlayer]) -> str:
    """Identify wicketkeeper in XI"""
    for sp in xi:
        if sp.player.is_wicketkeeper:
            return sp.player.player_name
    return "None designated"


# =============================================================================
# MAIN GENERATION
# =============================================================================


def generate_predicted_xii(
    team: str,
    players: List[Player],
    entry_points: Optional[Dict[str, Dict[str, Any]]] = None,
    squad_captains: Optional[Dict[str, str]] = None,
) -> PredictedXII:
    """Generate Predicted XII for a team"""
    logger.info("Generating predicted XII for %s", team)
    venue_info = HOME_VENUES.get(team, {"venue": "Unknown", "bias": "neutral"})
    logger.debug("Venue info: %s (bias: %s)", venue_info["venue"], venue_info["bias"])

    # Select XI
    xi, remaining, constraints_ok, violations, notes = select_xi(
        team, players, venue_info["bias"], entry_points
    )

    # Get balance metrics
    balance = get_balance_metrics(xi)

    # Identify captain and keeper
    captain = identify_captain(xi, team, squad_captains)
    keeper = identify_keeper(xi)

    # Select Impact Player (captain excluded per IPL rules - Constraint C1)
    impact = select_impact_player(xi, remaining, captain_name=captain)

    return PredictedXII(
        team_name=team,
        team_abbrev=TEAM_ABBREV[team],
        home_venue=venue_info["venue"],
        venue_bias=venue_info["bias"],
        xi=xi,
        impact_player=impact,
        captain=captain,
        wicketkeeper=keeper,
        overseas_count=balance["overseas_count"],
        bowling_options=balance["bowling_options"],
        spinners_count=balance["spinners"],
        pacers_count=balance["pacers"],
        left_handers_top6=balance["left_handers_top6"],
        constraints_satisfied=constraints_ok,
        constraint_violations=violations,
        generation_notes=notes,
    )


def predicted_xii_to_dict(pxii: PredictedXII) -> Dict[str, Any]:
    """Convert PredictedXII to JSON-serializable dict"""
    return {
        "team_name": pxii.team_name,
        "team_abbrev": pxii.team_abbrev,
        "home_venue": pxii.home_venue,
        "venue_bias": pxii.venue_bias,
        "captain": pxii.captain,
        "wicketkeeper": pxii.wicketkeeper,
        "xi": [
            {
                "batting_position": sp.batting_position,
                "player_id": sp.player.player_id,
                "player_name": sp.player.player_name,
                "role": sp.role_in_xi,
                "batting_hand": sp.player.batting_hand,
                "is_overseas": sp.player.is_overseas,
                "price_cr": sp.player.price_cr,
                "rationale": sp.rationale,
            }
            for sp in pxii.xi
        ],
        "impact_player": {
            "player_id": pxii.impact_player.player.player_id,
            "player_name": pxii.impact_player.player.player_name,
            "role": pxii.impact_player.role_in_xi,
            "batting_hand": pxii.impact_player.player.batting_hand,
            "is_overseas": pxii.impact_player.player.is_overseas,
            "price_cr": pxii.impact_player.player.price_cr,
            "rationale": pxii.impact_player.rationale,
        }
        if pxii.impact_player
        else None,
        "balance": {
            "overseas_count": pxii.overseas_count,
            "bowling_options": pxii.bowling_options,
            "spinners": pxii.spinners_count,
            "pacers": pxii.pacers_count,
            "left_handers_top6": pxii.left_handers_top6,
        },
        "constraints_satisfied": pxii.constraints_satisfied,
        "constraint_violations": pxii.constraint_violations,
        "generation_notes": pxii.generation_notes,
    }


def main() -> int:
    """Main entry point"""
    global BATTER_METRICS, BOWLER_METRICS

    logger.info("=" * 70)
    logger.info("CRICKET PLAYBOOK - SUPER SELECTOR v3.0")
    logger.info("Statistical Unified Player Evaluation and Ranking SELECTOR")
    logger.info("=" * 70)
    logger.info("Algorithm: Competency + Variety + Metrics-Based Scoring")

    # Load data
    logger.info("[1/4] Loading data...")
    squads, squad_captains = load_squads()
    contracts = load_contracts()
    tags = load_player_tags()
    entry_points = load_batting_entry_points()

    # SUPER SELECTOR v3.0: Load metrics
    BATTER_METRICS = load_batter_metrics()
    BOWLER_METRICS = load_bowler_metrics()

    logger.info("Loaded %d teams", len(squads))
    logger.info("Loaded %d player contracts", len(contracts))
    logger.info("Loaded %d batting entry point records", len(entry_points))
    logger.info("Loaded %d team captains from CSV", len(squad_captains))
    logger.info("Loaded %d batter metrics (boundary%%, consistency)", len(BATTER_METRICS))
    logger.info("Loaded %d bowler metrics (death dot%%)", len(BOWLER_METRICS))

    # Build player objects
    logger.info("[2/4] Building player database...")
    team_players = build_players(squads, contracts, tags)

    total_players = sum(len(p) for p in team_players.values())
    logger.info("Built %d player profiles", total_players)

    # Generate predictions
    logger.info("[3/4] Generating Predicted XIIs...")
    all_predictions = {}

    for team in IPL_TEAMS:
        logger.debug("Processing team: %s", team)
        players = team_players.get(team, [])

        if not players:
            logger.warning("No players found for %s", team)
            continue

        prediction = generate_predicted_xii(team, players, entry_points, squad_captains)
        all_predictions[team] = prediction

        # Log summary
        xi_names = [sp.player.player_name for sp in prediction.xi]
        logger.debug("XI for %s: %s...", team, ", ".join(xi_names[:6]))
        logger.debug(
            "Overseas: %d/4, Bowling options: %d",
            prediction.overseas_count,
            prediction.bowling_options,
        )
        if not prediction.constraints_satisfied:
            logger.warning(
                "Constraint violations for %s: %s", team, prediction.constraint_violations
            )

    # Save outputs
    logger.info("[4/4] Saving outputs...")

    # Ensure output directory exists
    PREDICTED_XII_DIR.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory: %s", PREDICTED_XII_DIR)

    # Save consolidated JSON
    output_data = {
        "generated_at": "2026-02-04",
        "version": "3.0",
        "algorithm_name": "SUPER SELECTOR",
        "algorithm_full_name": "Statistical Unified Player Evaluation and Ranking SELECTOR",
        "methodology": "Competency + Variety + Metrics-Based Scoring",
        "scoring_components": {
            "base": "Classification bonuses (0-30 pts)",
            "tags": "Phase-specific performance tags",
            "metrics": "boundary%, consistency_index, death_dot_pct",
            "price": "Auction price tier bonuses (5-15%)",
            "variety": "LHB, spinner/pacer balance optimization",
        },
        "constraints": {
            "C1": "Captain cannot be Impact Player",
            "C2": "Maximum 4 overseas players",
            "C3": "Minimum 20 overs bowling coverage",
            "C4": "At least 1 wicketkeeper",
            "C5": "At least 1 spinner",
        },
        "teams": {},
    }

    for team, prediction in all_predictions.items():
        output_data["teams"][TEAM_ABBREV[team]] = predicted_xii_to_dict(prediction)

    output_file = PREDICTED_XII_DIR / "predicted_xii_2026.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    logger.info("Saved consolidated output: %s", output_file)

    # Save per-team files
    for team, prediction in all_predictions.items():
        team_file = PREDICTED_XII_DIR / f"{TEAM_ABBREV[team].lower()}_predicted_xii.json"
        with open(team_file, "w") as f:
            json.dump(predicted_xii_to_dict(prediction), f, indent=2)

    logger.info("Saved %d team files", len(all_predictions))

    # Log summary
    logger.info("=" * 60)
    logger.info("GENERATION SUMMARY")
    logger.info("=" * 60)

    satisfied = sum(1 for p in all_predictions.values() if p.constraints_satisfied)
    logger.info("Teams with all constraints satisfied: %d/%d", satisfied, len(all_predictions))

    # List any violations
    for team, prediction in all_predictions.items():
        if not prediction.constraints_satisfied:
            logger.warning("%s has constraint violations:", team)
            for v in prediction.constraint_violations:
                logger.warning("  - %s", v)

    logger.info("=" * 70)
    logger.info("SUPER SELECTOR v3.0 - Generation complete")
    logger.info("Algorithm Name: SUPER SELECTOR")
    logger.info("Full Name: Statistical Unified Player Evaluation and Ranking SELECTOR")
    logger.info("Ready for Domain Sanity review.")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
