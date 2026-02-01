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
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

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


def load_squads() -> dict:
    """Load IPL 2026 squad data"""
    squads = {}
    squad_file = DATA_DIR / "ipl_2026_squads.csv"

    with open(squad_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row["team_name"]
            if team not in squads:
                squads[team] = []
            squads[team].append(row)

    return squads


def load_contracts() -> dict:
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


def load_player_tags() -> dict:
    """Load player tags from 2023+ analysis"""
    tags = {"batters": {}, "bowlers": {}}
    tags_file = OUTPUT_DIR / "player_tags_2023.json"

    if tags_file.exists():
        with open(tags_file, "r") as f:
            data = json.load(f)

            # Index batters by player_id
            for batter in data.get("batters", []):
                tags["batters"][batter["player_id"]] = batter

            # Index bowlers by player_id
            for bowler in data.get("bowlers", []):
                tags["bowlers"][bowler["player_id"]] = bowler

    return tags


def load_bowler_phase_performance() -> dict:
    """Load bowler phase performance metrics"""
    metrics = {}
    metrics_file = OUTPUT_DIR / "metrics" / "bowler_phase_performance.csv"

    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metrics[row["bowler_id"]] = row

    return metrics


def load_batting_entry_points() -> dict:
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


def build_players(squads: dict, contracts: dict, tags: dict) -> dict:
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
            batter_tags = (
                row.get("batter_tags", "").split("|") if row.get("batter_tags") else []
            )
            bowler_tags = (
                row.get("bowler_tags", "").split("|") if row.get("bowler_tags") else []
            )

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
    """Score a player for batting capability"""
    base_score = 50.0

    # Classification bonuses
    classification_scores = {
        "Elite Top-Order": 30,
        "Power Finisher": 25,
        "Aggressive Opener": 25,
        "All-Round Finisher": 20,
        "Anchor": 15,
    }
    base_score += classification_scores.get(player.batter_classification, 0)

    # Tag bonuses
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
    }

    for tag in player.batter_tags:
        base_score += tag_bonuses.get(tag, 0)

    # Auction price bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    return min(base_score, 100.0)


def score_bowler(player: Player) -> float:
    """Score a player for bowling capability"""
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

    # Auction price bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    return min(base_score, 100.0)


def score_player(player: Player) -> None:
    """Calculate overall player score"""
    player.batting_score = score_batter(player)
    player.bowling_score = score_bowler(player)

    # Compute overall based on role
    if player.role == "Bowler":
        player.overall_score = player.bowling_score * 0.85 + player.batting_score * 0.15
    elif player.role == "All-rounder":
        # Check if batting or bowling all-rounder based on tags/classification
        if player.batter_classification in ["All-Round Finisher", "Power Finisher"]:
            # Batting all-rounder: 60% bat / 40% bowl
            player.overall_score = (
                player.batting_score * 0.60 + player.bowling_score * 0.40
            )
        elif player.bowler_classification in [
            "Middle-Overs Spinner",
            "Powerplay Assassin",
        ]:
            # Bowling all-rounder: 40% bat / 60% bowl
            player.overall_score = (
                player.batting_score * 0.40 + player.bowling_score * 0.60
            )
        else:
            # True all-rounder: 50/50
            player.overall_score = (
                player.batting_score * 0.50 + player.bowling_score * 0.50
            )
    elif player.role == "Wicketkeeper":
        player.overall_score = player.batting_score * 0.90 + 10  # Keeper bonus
    else:  # Batter
        player.overall_score = player.batting_score


# =============================================================================
# CONSTRAINT CHECKING
# =============================================================================


def check_constraints(xi: list) -> tuple:
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
    bowling_options = sum(
        1 for p in players if p.can_bowl and p.bowling_overs_capability >= 4
    )
    if bowling_overs < 20:
        violations.append(
            f"C2: Insufficient bowling coverage ({bowling_overs}/20 overs)"
        )
    if bowling_options < 5:
        violations.append(
            f"C2: Insufficient bowling options ({bowling_options}/5 required)"
        )

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
        violations.append(
            f"C4: Insufficient primary bowling options ({primary_bowlers}/4)"
        )

    # C5: Spinner
    spinners = sum(1 for p in players if p.is_spinner)
    if spinners < 1:
        violations.append("C5: No spinner in XI")

    return len(violations) == 0, violations


def get_balance_metrics(xi: list) -> dict:
    """Calculate balance metrics for the XI"""
    players = [sp.player for sp in xi]

    return {
        "overseas_count": sum(1 for p in players if p.is_overseas),
        "bowling_options": sum(
            1 for p in players if p.can_bowl and p.bowling_overs_capability >= 4
        ),
        "total_bowling_overs": sum(
            p.bowling_overs_capability for p in players if p.can_bowl
        ),
        "spinners": sum(1 for p in players if p.is_spinner),
        "pacers": sum(1 for p in players if p.is_pacer),
        "wicketkeepers": sum(1 for p in players if p.is_wicketkeeper),
        "left_handers_top6": sum(
            1 for sp in xi[:6] if sp.player.batting_hand == "Left-hand"
        ),
        "left_handers_total": sum(1 for p in players if p.batting_hand == "Left-hand"),
    }


# =============================================================================
# SELECTION ALGORITHM
# =============================================================================


def get_role_candidates(players: list, role: str) -> list:
    """Get candidates for a specific role"""
    candidates = []

    if role == "opener":
        # Aggressive openers, top-order batters
        for p in players:
            if any(
                tag in p.batter_tags
                for tag in ["EXPLOSIVE_OPENER", "PP_DOMINATOR", "PLAYMAKER"]
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
            if any(
                tag in p.batter_tags
                for tag in ["FINISHER", "DEATH_SPECIALIST", "SIX_HITTER"]
            ):
                candidates.append(p)
            elif p.batter_classification in ["Power Finisher", "All-Round Finisher"]:
                candidates.append(p)

    elif role == "wicketkeeper":
        candidates = [p for p in players if p.is_wicketkeeper]

    elif role == "spinner":
        candidates = [
            p for p in players if p.is_spinner and p.bowling_overs_capability >= 4
        ]

    elif role == "pacer":
        candidates = [
            p for p in players if p.is_pacer and p.bowling_overs_capability >= 4
        ]

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
            if p.bowling_overs_capability >= 4
            and (p.role == "Bowler" or p.bowler_classification)
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
            rationales.append(
                f"{"Spin" if player.is_spinner else "Pace"} bowling depth"
            )
        elif player.is_wicketkeeper:
            rationales.append("Primary wicketkeeper")
        else:
            rationales.append("Batting value")

    return ". ".join(rationales[:2])


def select_xi(
    team: str, players: list, venue_bias: str, entry_points: dict = None
) -> tuple:
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
    pacers_selected = sum(
        1 for sp in selected if sp.player.is_pacer and sp.player.role == "Bowler"
    )

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

    # 9. Reorder batting positions based on role/classification and historical data
    selected = reorder_batting_positions(selected, entry_points)

    # Check constraints
    constraints_ok, violations = check_constraints(selected)
    if not constraints_ok:
        notes.append(f"Constraint violations: {violations}")
        # Attempt backtracking fixes
        selected, violations = fix_constraint_violations(
            selected, remaining, violations
        )
        constraints_ok = len(violations) == 0

    return selected, remaining, constraints_ok, violations, notes


def reorder_batting_positions(selected: list, entry_points: dict = None) -> list:
    """
    Reorder players into proper batting positions using:
    1. Historical 2023 batting entry point data (mean/median position)
    2. Player batter tags (PP_DOMINATOR, EXPLOSIVE_OPENER, FINISHER, etc.)
    3. Role-based classification

    Position assignment logic:
    - Positions 1-2 (Openers): Low avg_entry_ball (<20) OR EXPLOSIVE_OPENER/PP_DOMINATOR tags
    - Positions 3-4 (Top Order): Mid entry (20-40) OR ANCHOR/MIDDLE_ORDER tags
    - Positions 5-6 (Middle Order): Mid-high entry (40-70) OR MIDDLE_OVERS_ACCELERATOR tags
    - Positions 7-8 (Finisher/All-rounders): High entry (70+) OR FINISHER/DEATH_SPECIALIST tags
    - Positions 9-11 (Bowlers): Purely based on bowling role
    """
    if entry_points is None:
        entry_points = {}

    # Known openers - players who historically open for their teams/national sides
    # Based on avg_entry_ball <= 5 from historical data
    KNOWN_OPENERS = {
        "Rohit Sharma",  # avg_entry_ball: 3.3
        "Shubman Gill",  # avg_entry_ball: 4.2
        "Virat Kohli",  # avg_entry_ball: 2.6
        "Yashasvi Jaiswal",  # avg_entry_ball: 1.0
        "Ruturaj Gaikwad",  # avg_entry_ball: 4.7
        "Travis Head",  # avg_entry_ball: 2.5
        "Abhishek Sharma",  # avg_entry_ball: 9.5 but opens for SRH
        "Sunil Narine",  # Opens for KKR
        "Phil Salt",  # avg_entry_ball: 5.9
        "Jos Buttler",  # avg_entry_ball: 16.4 but can open
        "Quinton de Kock",  # avg_entry_ball: 1.9
        "KL Rahul",  # avg_entry_ball: 13.8 but can open
        "Sai Sudharsan",  # avg_entry_ball: 11.5 but can open
        "Prabhsimran Singh",  # avg_entry_ball: 6.0
    }

    # Known middle-order players (positions 4-6) - avg_entry_ball 40-80
    KNOWN_MIDDLE_ORDER = {
        "Shivam Dube",  # avg_entry_ball: 61.8
        "Ravindra Jadeja",  # avg_entry_ball: 75.5 (but bats 5-7)
        "Suryakumar Yadav",  # avg_entry_ball: 40.7
        "Tilak Varma",  # avg_entry_ball: 51.8
        "Heinrich Klaasen",  # avg_entry_ball: 57.8
        "Nicholas Pooran",  # avg_entry_ball: 61.4
        "Glenn Maxwell",  # avg_entry_ball: 60.5
        "Liam Livingstone",  # avg_entry_ball: 51.8
        "Marcus Stoinis",  # avg_entry_ball: 53.7
        "Hardik Pandya",  # avg_entry_ball: 66.4
        "Axar Patel",  # avg_entry_ball: 67.1
    }

    # Known finishers (positions 6-8) - batting all-rounders, not pure bowlers
    KNOWN_FINISHERS = {
        "MS Dhoni",  # avg_entry_ball: 105.6
        "Rinku Singh",  # avg_entry_ball: 72.2
        "Tim David",  # avg_entry_ball: 91.7
        "Rahul Tewatia",  # avg_entry_ball: 99.5
        "Shimron Hetmyer",  # avg_entry_ball: 85.8
        "Andre Russell",  # avg_entry_ball: 84.6
        # Note: Rashid Khan removed - spinners should bat 8-11, handled by role logic
    }

    def get_batting_tier(player) -> int:
        """
        Determine batting tier (1-5) based on historical data and tags.
        1 = Opener, 2 = Top Order (3-4), 3 = Middle (5-6), 4 = Finisher (7-8), 5 = Bowler (9-11)
        """
        p = player.player
        pid = p.player_id
        player_name = p.player_name.strip()

        # Get historical entry point if available
        entry_data = entry_points.get(pid, {})
        avg_entry = entry_data.get("avg_entry_ball")
        entry_class = entry_data.get("classification", "")

        # Tag-based opener detection
        opener_tags = ["EXPLOSIVE_OPENER", "PP_DOMINATOR"]
        has_opener_tag = any(tag in p.batter_tags for tag in opener_tags)

        # Tag-based middle order detection
        middle_tags = ["ANCHOR", "ACCUMULATOR", "MIDDLE_ORDER"]
        has_middle_tag = any(tag in p.batter_tags for tag in middle_tags)

        # Tag-based finisher detection
        finisher_tags = ["FINISHER", "DEATH_SPECIALIST", "SIX_HITTER"]
        has_finisher_tag = any(tag in p.batter_tags for tag in finisher_tags)

        # PRIORITY 1: Known role mappings (overrides everything else)
        if player_name in KNOWN_OPENERS:
            return 1
        if player_name in KNOWN_MIDDLE_ORDER:
            return 3

        # PRIORITY 2: Spinners (role == "Bowler" and is_spinner) should bat 8-11
        # This prevents spinners like Rashid Khan from batting in top order
        if p.is_spinner and p.role == "Bowler":
            return 5

        # Known finishers (batting all-rounders, not pure bowlers)
        if player_name in KNOWN_FINISHERS and p.role != "Bowler":
            return 4

        # Bowlers always at the end
        if p.role == "Bowler" and not p.batter_classification:
            return 5

        # Classification-based
        if p.batter_classification == "Aggressive Opener":
            return 1
        if p.batter_classification == "Elite Top-Order":
            # Check if historically opens (low entry ball)
            if avg_entry and avg_entry <= 20:
                return 1
            return 2
        if p.batter_classification == "Anchor":
            return 3
        if p.batter_classification in ["Power Finisher", "All-Round Finisher"]:
            # Check historical position
            if avg_entry and avg_entry <= 30:
                return 2  # Actually plays top order
            if avg_entry and avg_entry <= 60:
                return 3  # Actually plays middle
            return 4  # True finisher

        # Historical data based (most reliable)
        if avg_entry is not None:
            if avg_entry <= 15:  # Typically opens (enters by over 2.5)
                return 1
            elif avg_entry <= 35:  # Top order (enters by over 6)
                return 2
            elif avg_entry <= 60:  # Middle order (enters by over 10)
                return 3
            elif avg_entry <= 90:  # Lower middle/finisher (enters by over 15)
                return 4
            else:  # Very late order
                return 5

        # Entry classification based
        if entry_class == "TOP_ORDER":
            if has_opener_tag:
                return 1
            return 2
        if entry_class == "MIDDLE_ORDER":
            return 3
        if entry_class == "LOWER_ORDER":
            if has_finisher_tag:
                return 4
            return 5

        # Tag-based fallback
        if has_opener_tag:
            return 1
        if has_middle_tag:
            return 3
        if has_finisher_tag:
            return 4

        # Role-based fallback
        if p.role == "All-rounder":
            # Batting all-rounders higher, bowling all-rounders lower
            if p.batter_classification:
                return 3
            return 4
        if p.role in ["Batter", "Wicketkeeper"]:
            return 2

        return 4  # Default to lower-middle

    # Score players for sorting within tiers
    def get_tier_score(player, tier):
        """Get sorting score within a tier (higher = better)"""
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

        # For openers, prioritize aggressive tags
        if tier == 1:
            if "EXPLOSIVE_OPENER" in p.batter_tags:
                base_score += 10
            if "PP_DOMINATOR" in p.batter_tags:
                base_score += 8

        # For middle order, prioritize anchor/accumulator
        if tier in [2, 3]:
            if "ANCHOR" in p.batter_tags:
                base_score += 5
            if "CONSISTENT" in p.batter_tags:
                base_score += 5

        # For finishers, prioritize death specialists
        if tier == 4:
            if "FINISHER" in p.batter_tags:
                base_score += 10
            if "DEATH_SPECIALIST" in p.batter_tags:
                base_score += 8
            if "SIX_HITTER" in p.batter_tags:
                base_score += 5

        return base_score

    # Categorize into tiers
    tiers = {1: [], 2: [], 3: [], 4: [], 5: []}

    for sp in selected:
        tier = get_batting_tier(sp)
        tiers[tier].append(sp)

    # Sort each tier by score
    for tier_num in tiers:
        tiers[tier_num].sort(key=lambda x: get_tier_score(x, tier_num), reverse=True)

    # Build batting order
    batting_order = []
    position = 1

    def add_to_order(sp, pos):
        sp.batting_position = pos
        batting_order.append(sp)

    # Positions 1-2: Openers (tier 1)
    for sp in tiers[1][:2]:
        add_to_order(sp, position)
        position += 1

    # Fill opener slots from tier 2 if needed
    tier2_used = 0
    while position <= 2 and tier2_used < len(tiers[2]):
        add_to_order(tiers[2][tier2_used], position)
        position += 1
        tier2_used += 1

    # Positions 3-4: Top order
    # First use any remaining tier 1 players (extra openers bat at 3)
    tier1_remaining = tiers[1][2:]  # Openers beyond positions 1-2
    tier1_extra_used = 0
    while position <= 4 and tier1_extra_used < len(tier1_remaining):
        add_to_order(tier1_remaining[tier1_extra_used], position)
        position += 1
        tier1_extra_used += 1

    # Then remaining tier 2
    for sp in tiers[2][tier2_used:]:
        if position <= 4:
            add_to_order(sp, position)
            position += 1

    # Fill from tier 3 if needed
    tier3_used = 0
    while position <= 4 and tier3_used < len(tiers[3]):
        add_to_order(tiers[3][tier3_used], position)
        position += 1
        tier3_used += 1

    # Positions 5-6: Middle order (tier 3)
    for sp in tiers[3][tier3_used:]:
        if position <= 6:
            add_to_order(sp, position)
            position += 1

    # Positions 7-8: Finishers/All-rounders (tier 4)
    tier4_used = 0
    for sp in tiers[4]:
        if position <= 8:
            add_to_order(sp, position)
            position += 1
            tier4_used += 1

    # Positions 9-11: Bowlers (tier 5)
    for sp in tiers[5]:
        if sp not in batting_order:
            add_to_order(sp, position)
            position += 1

    # Any remaining players (should be rare - only if tiers overflow)
    for tier_num in [2, 3, 4]:  # Skip tier 1 - extra openers already handled above
        for sp in tiers[tier_num]:
            if sp not in batting_order:
                add_to_order(sp, position)
                position += 1

    return batting_order


def fix_constraint_violations(
    selected: list, remaining: list, violations: list
) -> tuple:
    """Attempt to fix constraint violations via substitution"""
    # This is a simplified backtracking - for V1, we just note violations
    # A more sophisticated version would swap players

    return selected, violations


def select_impact_player(xi: list, remaining: list) -> Optional[SelectedPlayer]:
    """Select the Impact Player (12th man)"""
    # Score remaining players
    for p in remaining:
        score_player(p)

    # Get XI composition
    xi_players = [sp.player for sp in xi]
    has_spinner = any(p.is_spinner for p in xi_players)
    batting_depth = sum(1 for p in xi_players if p.batting_score > 50)

    # Find best complement
    candidates = remaining.copy()

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
        rationale=f"Provides {"batting depth" if impact.batting_score > impact.bowling_score else "bowling option"} as Impact substitute",
        is_impact_player=True,
    )


def identify_captain(xi: list, team: str) -> str:
    """Identify likely captain based on price, experience, role"""
    # Known captains (can be updated)
    KNOWN_CAPTAINS = {
        "Chennai Super Kings": "Ruturaj Gaikwad",
        "Mumbai Indians": "Hardik Pandya",
        "Royal Challengers Bengaluru": "Virat Kohli",
        "Kolkata Knight Riders": "Ajinkya Rahane",
        "Delhi Capitals": "KL Rahul",
        "Punjab Kings": "Shreyas Iyer",
        "Rajasthan Royals": "Yashasvi Jaiswal",
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


def identify_keeper(xi: list) -> str:
    """Identify wicketkeeper in XI"""
    for sp in xi:
        if sp.player.is_wicketkeeper:
            return sp.player.player_name
    return "None designated"


# =============================================================================
# MAIN GENERATION
# =============================================================================


def generate_predicted_xii(
    team: str, players: list, entry_points: dict = None
) -> PredictedXII:
    """Generate Predicted XII for a team"""
    venue_info = HOME_VENUES.get(team, {"venue": "Unknown", "bias": "neutral"})

    # Select XI
    xi, remaining, constraints_ok, violations, notes = select_xi(
        team, players, venue_info["bias"], entry_points
    )

    # Select Impact Player
    impact = select_impact_player(xi, remaining)

    # Get balance metrics
    balance = get_balance_metrics(xi)

    # Identify captain and keeper
    captain = identify_captain(xi, team)
    keeper = identify_keeper(xi)

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


def predicted_xii_to_dict(pxii: PredictedXII) -> dict:
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


def main():
    """Main entry point"""
    print("=" * 60)
    print("CRICKET PLAYBOOK - PREDICTED XII GENERATOR")
    print("=" * 60)

    # Load data
    print("\n[1/4] Loading data...")
    squads = load_squads()
    contracts = load_contracts()
    tags = load_player_tags()
    entry_points = load_batting_entry_points()

    print(f"  - Loaded {len(squads)} teams")
    print(f"  - Loaded {len(contracts)} player contracts")
    print(f"  - Loaded {len(entry_points)} batting entry point records")

    # Build player objects
    print("\n[2/4] Building player database...")
    team_players = build_players(squads, contracts, tags)

    total_players = sum(len(p) for p in team_players.values())
    print(f"  - Built {total_players} player profiles")

    # Generate predictions
    print("\n[3/4] Generating Predicted XIIs...")
    all_predictions = {}

    for team in IPL_TEAMS:
        print(f"\n  {team}...")
        players = team_players.get(team, [])

        if not players:
            print(f"    WARNING: No players found for {team}")
            continue

        prediction = generate_predicted_xii(team, players, entry_points)
        all_predictions[team] = prediction

        # Print summary
        xi_names = [sp.player.player_name for sp in prediction.xi]
        print(f"    XI: {', '.join(xi_names[:6])}...")
        print(f"    Overseas: {prediction.overseas_count}/4")
        print(f"    Bowling: {prediction.bowling_options} options")
        print(
            f"    Constraints: {'OK' if prediction.constraints_satisfied else 'VIOLATIONS'}"
        )

    # Save outputs
    print("\n[4/4] Saving outputs...")

    # Ensure output directory exists
    PREDICTED_XII_DIR.mkdir(parents=True, exist_ok=True)

    # Save consolidated JSON
    output_data = {
        "generated_at": "2026-02-01",
        "version": "1.0",
        "methodology": "Constraint-satisfaction with weighted scoring",
        "teams": {},
    }

    for team, prediction in all_predictions.items():
        output_data["teams"][TEAM_ABBREV[team]] = predicted_xii_to_dict(prediction)

    output_file = PREDICTED_XII_DIR / "predicted_xii_2026.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"  - Saved: {output_file}")

    # Save per-team files
    for team, prediction in all_predictions.items():
        team_file = (
            PREDICTED_XII_DIR / f"{TEAM_ABBREV[team].lower()}_predicted_xii.json"
        )
        with open(team_file, "w") as f:
            json.dump(predicted_xii_to_dict(prediction), f, indent=2)

    print(f"  - Saved {len(all_predictions)} team files")

    # Print summary
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)

    satisfied = sum(1 for p in all_predictions.values() if p.constraints_satisfied)
    print(f"\nTeams with all constraints satisfied: {satisfied}/{len(all_predictions)}")

    # List any violations
    for team, prediction in all_predictions.items():
        if not prediction.constraints_satisfied:
            print(f"\n{team} VIOLATIONS:")
            for v in prediction.constraint_violations:
                print(f"  - {v}")

    print("\n" + "=" * 60)
    print("DATA GAPS & NOTES")
    print("=" * 60)
    print("""
The following data would improve predictions:

1. PLAYER METRICS (Missing):
   - Career T20 average and strike rate
   - Last 2 seasons performance data
   - Phase-specific batting metrics (PP/Middle/Death SR)
   - IPL match count for experience bonus

2. FORM DATA (Missing):
   - Recent 10-match form factor
   - Form slump detection

3. AVAILABILITY (Assumed all available):
   - Injury flags not implemented
   - Availability status not available

4. VENUE DATA (Partial):
   - Home venue bias applied (spin/pace)
   - Detailed pitch characteristics not available

NOTE: Algorithm uses squad classifications, bowler tags, and auction
prices as primary signals. Player metrics database integration would
significantly improve selection accuracy.
""")

    print("\nReady for Domain Sanity review.")
    print("=" * 60)


if __name__ == "__main__":
    main()
