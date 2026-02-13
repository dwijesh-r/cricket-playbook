#!/usr/bin/env python3
"""
Cricket Playbook - Depth Charts Generator
Author: Stephen Curry (Analytics Lead)
Sprint: V1 - Depth Charts Algorithm

Generates position-by-position depth charts for all 10 IPL 2026 teams.
Per approved PRD: /governance/tasks/DEPTH_CHARTS_PRD.md

Positions:
1. Opener (Top 3) - PP SR 30%, PP Boundary% 20%, Career Avg 15%, Last 2 seasons 20%, Experience 15%
2. #3 Batter (Top 3) - Versatility focus, adaptability score
3. Middle Order #4-5 (Top 3) - Spin performance 25%, Avg in 7-15 25%
4. Finisher #6-7 (Top 3) - Death SR 35%, Boundary% at death 20%
5. Wicketkeeper (Primary + Backup) - Keeping 30%, Batting at slot 50%
6. Right-arm Pace (Top 3) - Uses lead_pacer scoring, filtered by bowling arm/type
7. Left-arm Pace (Top 3) - Uses lead_pacer scoring, filtered by bowling arm/type
8. Off Spin (Top 3) - Uses lead_spinner scoring, filtered by bowling type
9. Leg Spin (Top 3) - Uses lead_spinner scoring, filtered by bowling type
10. Left-arm Spin (Top 3) - Uses lead_spinner scoring, filtered by bowling arm/type
11. Middle Overs Specialist (Top 3) - Middle eco 40%, Middle wkts 20%, Overall eco 20%, Exp 20%
12. All-rounder - Batting-first (65/35) + Bowling-first (35/65)

Note: All-rounders compete in batting positions with NO penalty — evaluated purely on
the batting skill being tested. Founder XII players receive a +10 scoring bonus.
"""

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.utils.logging_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
DEPTH_CHARTS_DIR = OUTPUT_DIR / "depth_charts"

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


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class Player:
    """Player data model for depth chart analysis"""

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
    batter_tags: List[str] = field(default_factory=list)
    bowler_tags: List[str] = field(default_factory=list)

    # Computed properties
    can_bowl: bool = False
    bowling_overs_capability: int = 0
    is_spinner: bool = False
    is_pacer: bool = False

    # Entry point data (batting position)
    avg_entry_ball: Optional[float] = None
    entry_classification: Optional[str] = None
    mode_batting_position: Optional[int] = None
    mean_batting_position: Optional[float] = None

    # Phase performance data (bowlers)
    pp_economy: Optional[float] = None
    pp_wickets: Optional[int] = None
    pp_overs: Optional[float] = None
    middle_economy: Optional[float] = None
    middle_wickets: Optional[int] = None
    middle_overs: Optional[float] = None
    death_economy: Optional[float] = None
    death_wickets: Optional[int] = None
    death_overs: Optional[float] = None
    bowler_phase_tags: Optional[str] = None

    # Tags from player_tags_2023.json
    overall_sr: Optional[float] = None
    overall_economy: Optional[float] = None

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
                self.is_pacer = True
                self.bowling_overs_capability = 2

        if self.role == "All-rounder":
            self.can_bowl = True
            if not self.bowling_overs_capability:
                self.bowling_overs_capability = 4

        if self.role == "Bowler":
            self.can_bowl = True
            self.bowling_overs_capability = 4


@dataclass
class PositionPlayer:
    """Player ranked at a specific position"""

    rank: int
    player: Player
    score: float
    rationale: str
    secondary_positions: List[str] = field(default_factory=list)


@dataclass
class Position:
    """Position in depth chart"""

    name: str
    rating: float
    what_works: str
    what_doesnt: str
    players: List[PositionPlayer]
    overseas_count: int = 0


@dataclass
class DepthChart:
    """Complete depth chart for a team"""

    team_name: str
    team_abbrev: str
    positions: Dict[str, Position]
    overall_rating: float
    strongest_position: str
    weakest_position: str
    vulnerabilities: List[str]


# =============================================================================
# KNOWN OPENERS - Established franchise openers get priority boost
# =============================================================================

# Known openers - players who historically open for their teams/national sides
# These players should be ranked higher than algorithm-only would suggest
KNOWN_OPENERS = {
    "Rohit Sharma",  # MI captain, opens for India
    "Shubman Gill",  # GT captain, opens for India
    "Virat Kohli",  # RCB, opens in IPL
    "Yashasvi Jaiswal",  # RR, India opener
    "Ruturaj Gaikwad",  # CSK captain, franchise opener
    "Travis Head",  # SRH, Australian opener
    "Abhishek Sharma",  # SRH opener
    "Sunil Narine",  # KKR opener
    "Phil Salt",  # KKR opener
    "Jos Buttler",  # RR, England captain
    "Quinton de Kock",  # LSG/MI, SA opener
    "KL Rahul",  # LSG/DC, India
    "Sai Sudharsan",  # GT, emerging opener
    "Prabhsimran Singh",  # PBKS opener
    "Faf du Plessis",  # RCB opener
    "David Warner",  # DC opener (if on roster)
}

# Franchise captains who open - get additional priority
FRANCHISE_OPENING_CAPTAINS = {
    "Rohit Sharma": "Mumbai Indians",
    "Shubman Gill": "Gujarat Titans",
    "Ruturaj Gaikwad": "Chennai Super Kings",
}

# Opener priority bonus points
KNOWN_OPENER_BONUS = 25.0
FRANCHISE_CAPTAIN_OPENER_BONUS = 10.0

# Founder XII bonus - players in Founder's predicted XII get a boost
FOUNDER_XII_BONUS = 10.0
FOUNDER_SQUADS_FILE = PROJECT_DIR / "outputs" / "founder_review" / "founder_squads_2026.json"


# =============================================================================
# OVERSEAS PLAYER DETECTION
# =============================================================================

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
    # Afghan
    "Rashid Khan",
    "Noor Ahmad",
    "Azmatullah Omarzai",
    "AM Ghazanfar",
    # Others
    "Pathum Nissanka",
    "Kyle Jamieson",
    "Dushmantha Chameera",
    "Brydon Carse",
    "Jack Edwards",
    "Zak Foulkes",
}


def is_overseas_player(player_name: str) -> bool:
    """Determine if player is overseas"""
    return player_name.strip() in OVERSEAS_PLAYERS


# =============================================================================
# DATA LOADING
# =============================================================================


def load_squads() -> Dict[str, List[Dict[str, str]]]:
    """Load IPL 2026 squad data"""
    squads = {}
    squad_file = DATA_DIR / "ipl_2026_squads.csv"

    logger.debug("Loading squads from %s", squad_file)

    with open(squad_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            team = row["team_name"]
            if team not in squads:
                squads[team] = []
            squads[team].append(row)

    logger.info("Loaded %d teams from squad data", len(squads))
    return squads


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

            for batter in data.get("batters", []):
                tags["batters"][batter["player_id"]] = batter

            for bowler in data.get("bowlers", []):
                tags["bowlers"][bowler["player_id"]] = bowler

        logger.debug(
            "Loaded tags for %d batters, %d bowlers", len(tags["batters"]), len(tags["bowlers"])
        )
    else:
        logger.warning("Player tags file not found: %s", tags_file)

    return tags


def load_entry_points() -> Dict[str, Dict[str, Any]]:
    """Load batting entry points data"""
    entry_points = {}
    entry_file = OUTPUT_DIR / "matchups" / "batter_entry_points_2023.csv"

    if entry_file.exists():
        with open(entry_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry_points[row["player_id"]] = {
                    "avg_entry_ball": float(row["avg_entry_ball"])
                    if row.get("avg_entry_ball")
                    else None,
                    "classification": row.get("entry_point_classification", ""),
                    "mode_batting_position": int(row["mode_batting_position"])
                    if row.get("mode_batting_position")
                    else None,
                    "mean_batting_position": float(row["mean_batting_position"])
                    if row.get("mean_batting_position")
                    else None,
                    "avg_entry_over": float(row["avg_entry_over"])
                    if row.get("avg_entry_over")
                    else None,
                }

    return entry_points


def load_bowler_phase_performance() -> Dict[str, Dict[str, str]]:
    """Load bowler phase performance metrics"""
    metrics = {}
    metrics_file = OUTPUT_DIR / "metrics" / "bowler_phase_performance.csv"

    if metrics_file.exists():
        with open(metrics_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                metrics[row["bowler_id"]] = {
                    "pp_overs": float(row["powerplay_overs"]) if row.get("powerplay_overs") else 0,
                    "pp_economy": float(row["powerplay_economy"])
                    if row.get("powerplay_economy")
                    else None,
                    "pp_wickets": int(float(row["powerplay_wickets"]))
                    if row.get("powerplay_wickets")
                    else 0,
                    "middle_overs": float(row["middle_overs"]) if row.get("middle_overs") else 0,
                    "middle_economy": float(row["middle_economy"])
                    if row.get("middle_economy")
                    else None,
                    "middle_wickets": int(float(row["middle_wickets"]))
                    if row.get("middle_wickets")
                    else 0,
                    "death_overs": float(row["death_overs"]) if row.get("death_overs") else 0,
                    "death_economy": float(row["death_economy"])
                    if row.get("death_economy")
                    else None,
                    "death_wickets": int(float(row["death_wickets"]))
                    if row.get("death_wickets")
                    else 0,
                    "phase_tags": row.get("phase_tags", ""),
                }

    return metrics


def load_founder_xii() -> set:
    """
    Load Founder's predicted XII player IDs.
    Players in the Founder's XII receive a scoring bonus in all positions.

    Returns:
        Set of player_id strings that are in the Founder's XII
    """
    founder_xii = set()

    if FOUNDER_SQUADS_FILE.exists():
        logger.debug("Loading Founder XII from %s", FOUNDER_SQUADS_FILE)
        with open(FOUNDER_SQUADS_FILE, "r") as f:
            data = json.load(f)

        for team_abbrev, team_data in data.get("teams", {}).items():
            for player in team_data.get("players", []):
                if player.get("is_predicted_xii", False):
                    founder_xii.add(player["player_id"])

        logger.info("Loaded %d Founder XII players", len(founder_xii))
    else:
        logger.warning("Founder squads file not found: %s", FOUNDER_SQUADS_FILE)

    return founder_xii


# Global founder XII set — loaded once at module level or in main()
_FOUNDER_XII: set = set()


def is_founder_xii(player_id: str) -> bool:
    """Check if a player is in the Founder's XII"""
    return player_id in _FOUNDER_XII


def build_players(
    squads: Dict[str, List[Dict[str, str]]],
    contracts: Dict[str, Dict[str, Any]],
    tags: Dict[str, Dict[str, Dict[str, Any]]],
    entry_points: Dict[str, Dict[str, Any]],
    bowler_metrics: Dict[str, Dict[str, str]],
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

            # Merge with tags from player_tags_2023.json
            for tag in batter_info.get("tags", []):
                if tag not in batter_tags:
                    batter_tags.append(tag)

            for tag in bowler_info.get("tags", []):
                if tag not in bowler_tags:
                    bowler_tags.append(tag)

            # Get entry point data
            entry_data = entry_points.get(player_id, {})

            # Get bowler phase metrics
            bowler_data = bowler_metrics.get(player_id, {})

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
                avg_entry_ball=entry_data.get("avg_entry_ball"),
                entry_classification=entry_data.get("classification"),
                mode_batting_position=entry_data.get("mode_batting_position"),
                mean_batting_position=entry_data.get("mean_batting_position"),
                pp_economy=bowler_data.get("pp_economy"),
                pp_wickets=bowler_data.get("pp_wickets"),
                pp_overs=bowler_data.get("pp_overs"),
                middle_economy=bowler_data.get("middle_economy"),
                middle_wickets=bowler_data.get("middle_wickets"),
                middle_overs=bowler_data.get("middle_overs"),
                death_economy=bowler_data.get("death_economy"),
                death_wickets=bowler_data.get("death_wickets"),
                death_overs=bowler_data.get("death_overs"),
                bowler_phase_tags=bowler_data.get("phase_tags"),
                overall_sr=batter_info.get("overall_sr"),
                overall_economy=bowler_info.get("economy"),
            )

            players.append(player)

        team_players[team] = players

    return team_players


# =============================================================================
# POSITION SCORING ALGORITHMS
# =============================================================================


def get_auction_bonus(price_cr: float) -> float:
    """Get auction price bonus multiplier"""
    if price_cr >= 15.0:
        return 0.15
    elif price_cr >= 10.0:
        return 0.10
    elif price_cr >= 5.0:
        return 0.05
    return 0.0


def get_experience_bonus(price_cr: float, year_joined: int = 2026) -> float:
    """Estimate experience bonus based on price and tenure"""
    # Higher price typically correlates with more experience
    if price_cr >= 15:
        return 0.10  # 100+ matches equivalent
    elif price_cr >= 8:
        return 0.05  # 50+ matches equivalent
    return 0.0


def score_opener(player: Player) -> Tuple[float, str]:
    """
    Score player for Opener position.
    Criteria: PP SR 30%, PP Boundary% 20%, Career Avg 15%, Last 2 seasons 20%, Experience 15%

    KNOWN OPENERS PRIORITY: Established franchise openers get priority boost
    to ensure algorithm respects traditional batting positions.
    """
    base_score = 0.0
    rationale_parts = []

    # Check if player is a KNOWN OPENER (priority boost)
    player_name = player.player_name.strip()
    is_known_opener = player_name in KNOWN_OPENERS
    is_franchise_captain_opener = player_name in FRANCHISE_OPENING_CAPTAINS

    # Check if player can open
    opener_tags = ["EXPLOSIVE_OPENER", "PP_DOMINATOR", "PP_AGGRESSOR"]
    is_opener_type = any(tag in player.batter_tags for tag in opener_tags)
    is_aggressive = player.batter_classification in [
        "Aggressive Opener",
        "Elite Top-Order",
    ]
    opens_historically = player.avg_entry_ball is not None and player.avg_entry_ball <= 15

    # Known openers bypass the standard profile check
    if not (is_known_opener or is_opener_type or is_aggressive or opens_historically):
        return 0.0, "Not an opener profile"

    # PP SR component (30%)
    if player.overall_sr:
        if player.overall_sr >= 170:
            base_score += 30
            rationale_parts.append(f"Elite SR ({player.overall_sr:.1f})")
        elif player.overall_sr >= 150:
            base_score += 25
            rationale_parts.append(f"Good SR ({player.overall_sr:.1f})")
        elif player.overall_sr >= 140:
            base_score += 20
        else:
            base_score += 15

    # PP-specific tags (20%)
    if "PP_DOMINATOR" in player.batter_tags:
        base_score += 20
        rationale_parts.append("PP Dominator")
    elif "PP_AGGRESSOR" in player.batter_tags:
        base_score += 18
        rationale_parts.append("PP Aggressor")
    elif "EXPLOSIVE_OPENER" in player.batter_tags:
        base_score += 15
        rationale_parts.append("Explosive opener")
    elif "PP_ACCUMULATOR" in player.batter_tags:
        base_score += 10
    elif "PP_LIABILITY" in player.batter_tags:
        base_score += 2

    # Career reliability (15%)
    if player.batter_classification == "Elite Top-Order":
        base_score += 15
        rationale_parts.append("Elite top-order")
    elif player.batter_classification == "Aggressive Opener":
        base_score += 15
        rationale_parts.append("Aggressive opener")
    elif player.batter_classification in ["Power Finisher", "All-Round Finisher"]:
        base_score += 8

    # Recent form proxy using price (20%)
    base_score += min(player.price_cr, 20)  # Cap at 20 points

    # Experience (15%)
    base_score += get_experience_bonus(player.price_cr) * 100

    # Mode batting position penalty: non-openers penalised for opener slot
    if player.mode_batting_position is not None:
        if player.mode_batting_position > 3:
            base_score *= 0.50  # Middle-order/finisher: -50%
            rationale_parts.append("Pos penalty (mode > 3)")
        elif player.mode_batting_position == 3:
            base_score *= 0.80  # #3 batter: -20%
            rationale_parts.append("Pos penalty (mode 3)")

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    # KNOWN OPENER PRIORITY BOOST
    # Established franchise openers get priority to ensure algorithm respects
    # traditional batting positions (fixes Rohit Sharma > Tilak Varma for MI)
    if is_known_opener:
        base_score += KNOWN_OPENER_BONUS
        if "Franchise opener" not in rationale_parts:
            rationale_parts.insert(0, "Franchise opener")

    if is_franchise_captain_opener:
        # Additional boost for captains who open
        base_score += FRANCHISE_CAPTAIN_OPENER_BONUS
        if "Captain" not in " ".join(rationale_parts):
            rationale_parts.insert(0, "Captain")

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Opens for the team"
    return min(base_score, 100.0), rationale


def score_number_three(player: Player) -> Tuple[float, str]:
    """
    Score player for #3 position.
    Criteria: Versatility focus, adaptability score, can handle both PP and middle overs
    """
    base_score = 0.0
    rationale_parts = []

    # Check if player can bat #3
    middle_entry = player.avg_entry_ball is not None and 10 <= player.avg_entry_ball <= 50
    is_top_order = player.batter_classification in [
        "Elite Top-Order",
        "Anchor",
        "All-Round Finisher",
    ]
    has_versatility = (
        "PP_ACCUMULATOR" in player.batter_tags or "MIDDLE_ANCHOR" in player.batter_tags
    )

    if not (is_top_order or middle_entry or has_versatility):
        # Check if they can open (openers can bat #3)
        opener_tags = ["EXPLOSIVE_OPENER", "PP_DOMINATOR", "PP_AGGRESSOR"]
        if not any(tag in player.batter_tags for tag in opener_tags):
            return 0.0, "Not a #3 profile"

    # Overall T20 Average proxy (25%) - use SR and classification
    if player.overall_sr:
        if player.overall_sr >= 150:
            base_score += 20
        elif player.overall_sr >= 140:
            base_score += 15
        else:
            base_score += 10

    if player.batter_classification == "Elite Top-Order":
        base_score += 5
        rationale_parts.append("Elite top-order")

    # SR in overs 1-10 proxy (20%)
    if "PP_DOMINATOR" in player.batter_tags or "PP_AGGRESSOR" in player.batter_tags:
        base_score += 18
        rationale_parts.append("Strong in PP")
    elif "PP_ACCUMULATOR" in player.batter_tags:
        base_score += 12

    # SR in overs 11-20 proxy (20%)
    if "MIDDLE_ACCELERATOR" in player.batter_tags:
        base_score += 18
        rationale_parts.append("Middle overs accelerator")
    elif "MIDDLE_ANCHOR" in player.batter_tags:
        base_score += 14
    elif "DEATH_HITTER" in player.batter_tags or "DEATH_FINISHER" in player.batter_tags:
        base_score += 12

    # Performance vs spin (15%)
    if "SPECIALIST_VS_SPIN" in player.batter_tags:
        base_score += 15
        rationale_parts.append("Spin specialist")
    elif any("SPIN" in tag for tag in player.batter_tags):
        base_score += 10

    # Performance vs pace (15%)
    if "SPECIALIST_VS_PACE" in player.batter_tags:
        base_score += 15
    elif "PACE_SPECIALIST" in player.batter_tags:
        base_score += 12

    # Adaptability score (5%) - lower variance = more adaptable
    # Proxy: Elite classification + multiple phase tags
    phase_tags_count = sum(
        1 for tag in player.batter_tags if any(p in tag for p in ["PP_", "MIDDLE_", "DEATH_"])
    )
    if phase_tags_count >= 3:
        base_score += 5
        rationale_parts.append("Highly adaptable")
    elif phase_tags_count >= 2:
        base_score += 3

    # Price bonus
    base_score += min(player.price_cr * 0.5, 10)

    # Mode batting position penalty: deep lower-order/pure openers penalised for #3
    if player.mode_batting_position is not None:
        if player.mode_batting_position > 5:
            base_score *= 0.60  # Lower-order/tail: -40%
            rationale_parts.append("Pos penalty (mode > 5)")
        elif player.mode_batting_position == 1:
            base_score *= 0.90  # Pure opener: -10%
            rationale_parts.append("Pos penalty (mode 1)")

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Can bat #3"
    return min(base_score, 100.0), rationale


def score_middle_order(player: Player) -> Tuple[float, str]:
    """
    Score player for Middle Order #4-5 position.
    Criteria: Avg in 7-15 25%, SR in 7-15 20%, Performance vs spin 25%, Career Avg 15%, Recent 15%

    All-rounders compete in batting positions with NO penalty — evaluated purely
    on the batting skill being tested.
    """
    base_score = 0.0
    rationale_parts = []

    # Check if player can bat middle order
    # All-rounders with batting credentials are explicitly eligible
    middle_entry = player.avg_entry_ball is not None and 30 <= player.avg_entry_ball <= 80
    is_middle_order = player.batter_classification in [
        "All-Round Finisher",
        "Anchor",
        "Power Finisher",
    ]
    has_middle_tags = "MIDDLE_ORDER" in player.batter_tags or "MIDDLE_ANCHOR" in player.batter_tags
    is_allrounder_with_batting = (
        player.role == "All-rounder"
        and player.batter_classification is not None
        and player.batter_classification != ""
    )

    if not (is_middle_order or middle_entry or has_middle_tags or is_allrounder_with_batting):
        return 0.0, "Not a middle order profile"

    # Performance in overs 7-15 (45% combined)
    if "MIDDLE_ANCHOR" in player.batter_tags:
        base_score += 25
        rationale_parts.append("Middle overs anchor")
    elif "MIDDLE_ACCELERATOR" in player.batter_tags:
        base_score += 30
        rationale_parts.append("Middle overs accelerator")
    elif "MIDDLE_LIABILITY" in player.batter_tags:
        base_score += 5
    elif player.role == "All-rounder" and player.overall_sr:
        # All-rounders: use overall SR as a proxy for middle-overs ability
        # when specific middle-overs tags are missing
        if player.overall_sr >= 150:
            base_score += 22
            rationale_parts.append(f"AR middle-overs SR ({player.overall_sr:.0f})")
        elif player.overall_sr >= 140:
            base_score += 18
            rationale_parts.append(f"AR middle-overs SR ({player.overall_sr:.0f})")
        elif player.overall_sr >= 130:
            base_score += 12

    # Entry point classification from analytics (supplements batter_tags)
    if player.entry_classification == "MIDDLE_ORDER" and "MIDDLE_ORDER" not in player.batter_tags:
        base_score += 15
        if "Middle order entry" not in rationale_parts:
            rationale_parts.append("Middle order entry")
    elif "MIDDLE_ORDER" in player.batter_tags:
        base_score += 15

    # Performance vs spin (25%)
    spin_tags = [
        "SPECIALIST_VS_SPIN",
        "SPECIALIST_VS_LEG_SPIN",
        "SPECIALIST_VS_OFF_SPIN",
        "SPECIALIST_VS_LEFT_ARM_SPIN",
        "SPIN_SPECIALIST",
    ]
    spin_count = sum(1 for tag in player.batter_tags if tag in spin_tags)
    if spin_count >= 3:
        base_score += 25
        rationale_parts.append("Excellent vs spin")
    elif spin_count >= 2:
        base_score += 20
    elif spin_count >= 1:
        base_score += 15

    vulnerable_spin = "VULNERABLE_VS_SPIN" in player.batter_tags
    if vulnerable_spin:
        base_score -= 10

    # Career reliability (15%)
    if player.batter_classification == "Power Finisher":
        base_score += 15
    elif player.batter_classification in ["Anchor", "Elite Top-Order"]:
        base_score += 12
    elif player.batter_classification == "All-Round Finisher":
        base_score += 10

    # Recent form proxy (15%)
    base_score += min(player.price_cr * 0.75, 15)

    # Mode batting position penalty: openers and tail-enders penalised for middle order
    if player.mode_batting_position is not None:
        if player.mode_batting_position <= 2:
            base_score *= 0.60  # Openers: -40%
            rationale_parts.append("Pos penalty (opener)")
        elif player.mode_batting_position >= 8:
            base_score *= 0.70  # Tail-enders: -30%
            rationale_parts.append("Pos penalty (lower order)")

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Middle order batter"
    return min(base_score, 100.0), rationale


def score_finisher(player: Player) -> Tuple[float, str]:
    """
    Score player for Finisher #6-7 position.
    Criteria: Death SR 35%, Boundary% at death 20%, Career SR 15%, Avg at death 15%, Bowling utility 15%

    All-rounders compete in batting positions with NO penalty — evaluated purely
    on the batting skill being tested.
    """
    base_score = 0.0
    rationale_parts = []

    # Check if player is a finisher type
    # All-rounders with finisher credentials are explicitly eligible
    finisher_tags = [
        "FINISHER",
        "DEATH_SPECIALIST",
        "DEATH_HITTER",
        "DEATH_FINISHER",
        "SIX_HITTER",
    ]
    is_finisher_type = any(tag in player.batter_tags for tag in finisher_tags)
    late_entry = player.avg_entry_ball is not None and player.avg_entry_ball >= 60
    is_ar_finisher = player.batter_classification in [
        "All-Round Finisher",
        "Power Finisher",
    ]
    is_allrounder_with_batting = (
        player.role == "All-rounder"
        and player.batter_classification is not None
        and player.batter_classification != ""
    )

    if not (is_finisher_type or late_entry or is_ar_finisher or is_allrounder_with_batting):
        return 0.0, "Not a finisher profile"

    # Death overs SR (35%)
    if "DEATH_HITTER" in player.batter_tags:
        base_score += 35
        rationale_parts.append("Death overs hitter")
    elif "DEATH_FINISHER" in player.batter_tags:
        base_score += 32
        rationale_parts.append("Death overs finisher")
    elif "DEATH_SPECIALIST" in player.batter_tags:
        base_score += 28
        rationale_parts.append("Death specialist")
    elif "DEATH_LIABILITY" in player.batter_tags:
        base_score += 5
    elif player.role == "All-rounder" and player.overall_sr:
        # All-rounders: use overall SR as proxy for death-overs striking
        # when specific death-phase batter tags are missing
        if player.overall_sr >= 160:
            base_score += 28
            rationale_parts.append(f"AR death SR ({player.overall_sr:.0f})")
        elif player.overall_sr >= 145:
            base_score += 22
            rationale_parts.append(f"AR death SR ({player.overall_sr:.0f})")
        elif player.overall_sr >= 135:
            base_score += 16
            rationale_parts.append(f"AR death SR ({player.overall_sr:.0f})")
        elif player.overall_sr >= 125:
            base_score += 10

    # Boundary percentage (20%)
    if "SIX_HITTER" in player.batter_tags:
        base_score += 20
        rationale_parts.append("Six-hitting ability")
    elif "FINISHER" in player.batter_tags:
        base_score += 15

    # Career SR (15%)
    if player.overall_sr:
        if player.overall_sr >= 170:
            base_score += 15
        elif player.overall_sr >= 150:
            base_score += 12
        elif player.overall_sr >= 140:
            base_score += 8
        else:
            base_score += 5

    # Average at death (15%)
    if player.batter_classification == "Power Finisher":
        base_score += 15
        rationale_parts.append("Power finisher")
    elif player.batter_classification == "All-Round Finisher":
        base_score += 12
        rationale_parts.append("All-round finisher")

    # Bowling utility (15%)
    if player.can_bowl and player.bowling_overs_capability >= 4:
        base_score += 15
        rationale_parts.append("Bowling utility")
    elif player.can_bowl:
        base_score += 8

    # Mode batting position penalty: openers/top-order penalised for finisher slot
    # Critical fix: e.g. Rohit Sharma (mode_pos=1) should NOT rank as #1 finisher
    if player.mode_batting_position is not None:
        if player.mode_batting_position <= 2:
            base_score *= 0.30  # Opener: -70%
            rationale_parts.append("Pos penalty (opener)")
        elif player.mode_batting_position == 3:
            base_score *= 0.50  # #3 batter: -50%
            rationale_parts.append("Pos penalty (#3)")
        elif player.mode_batting_position in (4, 5):
            base_score *= 0.85  # Middle order: -15% (can finish sometimes)
            rationale_parts.append("Pos adj (mid-order)")
        elif player.mode_batting_position in (6, 7):
            base_score *= 1.10  # Natural finisher slot: +10% boost
            rationale_parts.append("Natural finisher slot")

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Finisher"
    return min(base_score, 100.0), rationale


def score_wicketkeeper(player: Player, batting_position_score: float) -> Tuple[float, str]:
    """
    Score player for Wicketkeeper position.
    Criteria: Keeping quality 30%, Batting at designated position 50%, IPL keeping experience 20%
    """
    if not player.is_wicketkeeper and player.role != "Wicketkeeper":
        return 0.0, "Not a wicketkeeper"

    base_score = 0.0
    rationale_parts = []

    # Keeping quality (30%) - proxy using price and classification
    if player.price_cr >= 15:
        base_score += 30
        rationale_parts.append("Primary keeper")
    elif player.price_cr >= 8:
        base_score += 25
    elif player.price_cr >= 4:
        base_score += 20
    else:
        base_score += 15

    # Batting at designated position (50%)
    base_score += batting_position_score * 0.5
    if batting_position_score >= 70:
        rationale_parts.append(f"Strong batter (score: {batting_position_score:.0f})")
    elif batting_position_score >= 50:
        rationale_parts.append(f"Capable batter (score: {batting_position_score:.0f})")

    # IPL keeping experience (20%) - proxy using price and tenure
    if player.price_cr >= 10:
        base_score += 20
        rationale_parts.append("Experienced keeper")
    elif player.price_cr >= 5:
        base_score += 15
    else:
        base_score += 10

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Wicketkeeper"
    return min(base_score, 100.0), rationale


def score_lead_pacer(player: Player) -> Tuple[float, str]:
    """
    Score player for Lead Pacer position.
    Criteria: Wicket-taking (SR) 25%, Death economy 25%, PP economy 20%, Career economy 15%, Experience 15%
    """
    if not player.is_pacer or player.role not in ["Bowler", "All-rounder"]:
        return 0.0, "Not a pacer"

    base_score = 0.0
    rationale_parts = []

    # Wicket-taking ability (25%)
    if "PROVEN_WICKET_TAKER" in player.bowler_tags:
        base_score += 25
        rationale_parts.append("Proven wicket-taker")
    elif "PRESSURE_BUILDER" in player.bowler_tags:
        base_score += 18
    elif player.death_wickets and player.death_wickets >= 20:
        base_score += 22
    elif player.pp_wickets and player.pp_wickets >= 15:
        base_score += 20

    # Death overs economy (25%)
    if player.death_economy:
        if player.death_economy <= 8:
            base_score += 25
            rationale_parts.append(f"Elite death eco ({player.death_economy:.1f})")
        elif player.death_economy <= 10:
            base_score += 20
        elif player.death_economy <= 11:
            base_score += 15
        elif player.death_economy <= 12:
            base_score += 10
        else:
            base_score += 5
    elif "DEATH_ELITE" in player.bowler_tags or "DEATH_COMPLETE" in player.bowler_tags:
        base_score += 22
        rationale_parts.append("Death overs specialist")
    elif "DEATH_SPECIALIST" in player.bowler_tags:
        base_score += 18

    # Powerplay economy (20%)
    if player.pp_economy:
        if player.pp_economy <= 7:
            base_score += 20
            rationale_parts.append(f"Elite PP eco ({player.pp_economy:.1f})")
        elif player.pp_economy <= 8:
            base_score += 16
        elif player.pp_economy <= 9:
            base_score += 12
        else:
            base_score += 6
    elif "PP_ELITE" in player.bowler_tags:
        base_score += 18
    elif "NEW_BALL_SPECIALIST" in player.bowler_tags:
        base_score += 15

    # Career economy (15%)
    if player.overall_economy:
        if player.overall_economy <= 7:
            base_score += 15
        elif player.overall_economy <= 8:
            base_score += 12
        elif player.overall_economy <= 9:
            base_score += 9
        else:
            base_score += 5
    elif player.bowler_classification == "Powerplay Assassin":
        base_score += 15
        rationale_parts.append("PP Assassin")
    elif player.bowler_classification == "Workhorse Seamer":
        base_score += 10

    # Experience (15%)
    if player.price_cr >= 15:
        base_score += 15
        rationale_parts.append(f"Franchise lead pacer ({player.price_cr:.1f} Cr)")
    elif player.price_cr >= 10:
        base_score += 12
    elif player.price_cr >= 5:
        base_score += 8
    else:
        base_score += 5

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Lead pacer"
    return min(base_score, 100.0), rationale


def score_supporting_pacer_pp(player: Player) -> Tuple[float, str]:
    """
    Score player for PP Specialist Supporting Pacer.
    Criteria: PP Economy 35%, PP SR 30%, Swing/seam 20%, Overall eco 15%
    """
    if not player.is_pacer or player.role not in ["Bowler", "All-rounder"]:
        return 0.0, "Not a pacer"

    base_score = 0.0
    rationale_parts = []

    # PP Economy (35%)
    if player.pp_economy:
        if player.pp_economy <= 7:
            base_score += 35
            rationale_parts.append(f"Elite PP economy ({player.pp_economy:.1f})")
        elif player.pp_economy <= 8:
            base_score += 30
        elif player.pp_economy <= 9:
            base_score += 22
        else:
            base_score += 12
    elif "PP_ELITE" in player.bowler_tags:
        base_score += 30
        rationale_parts.append("PP Elite")
    elif "NEW_BALL_SPECIALIST" in player.bowler_tags:
        base_score += 25

    # PP Strike Rate (30%)
    if player.pp_wickets and player.pp_overs:
        pp_sr = (player.pp_overs * 6) / player.pp_wickets if player.pp_wickets > 0 else 99
        if pp_sr <= 15:
            base_score += 30
            rationale_parts.append(f"PP wicket-taker (SR {pp_sr:.1f})")
        elif pp_sr <= 20:
            base_score += 24
        elif pp_sr <= 25:
            base_score += 18
        else:
            base_score += 10
    elif "PP_STRIKE" in player.bowler_tags:
        base_score += 25
        rationale_parts.append("PP strike bowler")

    # Swing/seam movement (20%) - proxy using classification
    if player.bowler_classification == "Powerplay Assassin":
        base_score += 20
    elif "NEW_BALL_SPECIALIST" in player.bowler_tags:
        base_score += 15
    elif player.bowling_arm == "Left-arm":
        base_score += 12  # Left-arm angle is valuable

    # Overall economy (15%)
    if player.overall_economy:
        if player.overall_economy <= 8:
            base_score += 15
        elif player.overall_economy <= 9:
            base_score += 10
        else:
            base_score += 5

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "PP specialist"
    return min(base_score, 100.0), rationale


def score_supporting_pacer_death(player: Player) -> Tuple[float, str]:
    """
    Score player for Death Specialist Supporting Pacer.
    Criteria: Death Economy 40%, Death SR 25%, Yorker/variation execution 20%, Overall eco 15%
    """
    if not player.is_pacer or player.role not in ["Bowler", "All-rounder"]:
        return 0.0, "Not a pacer"

    base_score = 0.0
    rationale_parts = []

    # Death Economy (40%)
    if player.death_economy:
        if player.death_economy <= 8:
            base_score += 40
            rationale_parts.append(f"Elite death economy ({player.death_economy:.1f})")
        elif player.death_economy <= 10:
            base_score += 32
        elif player.death_economy <= 11:
            base_score += 24
        elif player.death_economy <= 12:
            base_score += 16
        else:
            base_score += 8
    elif "DEATH_ELITE" in player.bowler_tags or "DEATH_COMPLETE" in player.bowler_tags:
        base_score += 35
        rationale_parts.append("Death specialist")
    elif "DEATH_SPECIALIST" in player.bowler_tags:
        base_score += 28

    # Death Strike Rate (25%)
    if player.death_wickets and player.death_overs:
        death_sr = (
            (player.death_overs * 6) / player.death_wickets if player.death_wickets > 0 else 99
        )
        if death_sr <= 12:
            base_score += 25
            rationale_parts.append(f"Death wicket-taker (SR {death_sr:.1f})")
        elif death_sr <= 15:
            base_score += 20
        elif death_sr <= 20:
            base_score += 14
        else:
            base_score += 8
    elif "DEATH_STRIKE" in player.bowler_tags:
        base_score += 22

    # Yorker/variation execution (20%) - proxy
    if "DEATH_COMPLETE" in player.bowler_tags:
        base_score += 20
    elif "DEATH_CONTAINER" in player.bowler_tags:
        base_score += 15
    elif player.death_overs and player.death_overs >= 30:
        base_score += 12  # Experience at death

    # Overall economy (15%)
    if player.overall_economy:
        if player.overall_economy <= 8:
            base_score += 15
        elif player.overall_economy <= 9:
            base_score += 10
        else:
            base_score += 5

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Death specialist"
    return min(base_score, 100.0), rationale


def score_lead_spinner(player: Player) -> Tuple[float, str]:
    """
    Score player for Lead Spinner position.
    Criteria: Middle overs economy 30%, Strike rate 25%, Career economy 15%, vs RHB/LHB 15%, Experience 15%
    """
    if not player.is_spinner or player.role not in ["Bowler", "All-rounder"]:
        return 0.0, "Not a spinner"

    base_score = 0.0
    rationale_parts = []

    # Middle overs economy (30%)
    if player.middle_economy:
        if player.middle_economy <= 7:
            base_score += 30
            rationale_parts.append(f"Elite middle eco ({player.middle_economy:.1f})")
        elif player.middle_economy <= 8:
            base_score += 25
        elif player.middle_economy <= 9:
            base_score += 18
        else:
            base_score += 10
    elif "MIDDLE_STRANGLER" in player.bowler_tags or "MID_OVERS_ELITE" in player.bowler_tags:
        base_score += 28
        rationale_parts.append("Middle overs specialist")
    elif "MIDDLE_OVERS_CONTROLLER" in player.bowler_tags:
        base_score += 22

    # Strike rate / wicket-taking (25%)
    if player.middle_wickets and player.middle_overs:
        middle_sr = (
            (player.middle_overs * 6) / player.middle_wickets if player.middle_wickets > 0 else 99
        )
        if middle_sr <= 15:
            base_score += 25
            rationale_parts.append(f"Wicket-taker (SR {middle_sr:.1f})")
        elif middle_sr <= 20:
            base_score += 20
        elif middle_sr <= 25:
            base_score += 15
        else:
            base_score += 8
    elif "PROVEN_WICKET_TAKER" in player.bowler_tags:
        base_score += 22

    # Career economy (15%)
    if player.overall_economy:
        if player.overall_economy <= 7:
            base_score += 15
        elif player.overall_economy <= 8:
            base_score += 12
        elif player.overall_economy <= 9:
            base_score += 8
        else:
            base_score += 5
    elif player.bowler_classification == "Middle-Overs Spinner":
        base_score += 12

    # vs RHB/LHB versatility (15%)
    if "RHB_SPECIALIST" in player.bowler_tags and "LHB_WICKET_TAKER" in player.bowler_tags:
        base_score += 15
        rationale_parts.append("Versatile vs both hands")
    elif "RHB_WICKET_TAKER" in player.bowler_tags or "LHB_WICKET_TAKER" in player.bowler_tags:
        base_score += 10
    elif not ("LHB_VULNERABLE" in player.bowler_tags or "RHB_VULNERABLE" in player.bowler_tags):
        base_score += 8

    # Experience (15%)
    if player.price_cr >= 15:
        base_score += 15
        rationale_parts.append(f"Lead spinner ({player.price_cr:.1f} Cr)")
    elif player.price_cr >= 10:
        base_score += 12
    elif player.price_cr >= 5:
        base_score += 8
    else:
        base_score += 5

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Lead spinner"
    return min(base_score, 100.0), rationale


def score_middle_overs_specialist(player: Player) -> Tuple[float, str]:
    """
    Score player for Middle Overs Specialist position.
    ALL bowling types eligible. Scored by middle-overs performance.
    Criteria: Middle overs economy (40%), Middle overs wickets (20%),
              Overall economy (20%), Experience (20%)
    """
    if not player.can_bowl or player.role not in ["Bowler", "All-rounder"]:
        return 0.0, "Not a bowler"

    base_score = 0.0
    rationale_parts = []

    # Middle overs economy (40%)
    if player.middle_economy:
        if player.middle_economy <= 6.5:
            base_score += 40
            rationale_parts.append(f"Elite middle eco ({player.middle_economy:.1f})")
        elif player.middle_economy <= 7.5:
            base_score += 34
            rationale_parts.append(f"Strong middle eco ({player.middle_economy:.1f})")
        elif player.middle_economy <= 8.5:
            base_score += 26
        elif player.middle_economy <= 9.5:
            base_score += 18
        else:
            base_score += 10
    elif "MIDDLE_STRANGLER" in player.bowler_tags or "MID_OVERS_ELITE" in player.bowler_tags:
        base_score += 34
        rationale_parts.append("Middle overs specialist tag")
    elif "MIDDLE_OVERS_CONTROLLER" in player.bowler_tags:
        base_score += 26

    # Middle overs wickets (20%)
    if player.middle_wickets and player.middle_overs:
        middle_sr = (
            (player.middle_overs * 6) / player.middle_wickets if player.middle_wickets > 0 else 99
        )
        if middle_sr <= 15:
            base_score += 20
            rationale_parts.append(f"Middle wkt-taker (SR {middle_sr:.1f})")
        elif middle_sr <= 20:
            base_score += 16
        elif middle_sr <= 25:
            base_score += 12
        else:
            base_score += 6
    elif "PROVEN_WICKET_TAKER" in player.bowler_tags:
        base_score += 16

    # Overall economy (20%)
    if player.overall_economy:
        if player.overall_economy <= 7:
            base_score += 20
        elif player.overall_economy <= 8:
            base_score += 16
        elif player.overall_economy <= 9:
            base_score += 12
        else:
            base_score += 6

    # Experience (20%)
    if player.price_cr >= 15:
        base_score += 20
        rationale_parts.append(f"Franchise bowler ({player.price_cr:.1f} Cr)")
    elif player.price_cr >= 10:
        base_score += 16
    elif player.price_cr >= 5:
        base_score += 12
    else:
        base_score += 6

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Middle overs specialist"
    return min(base_score, 100.0), rationale


def score_batting_allrounder(player: Player) -> Tuple[float, str]:
    """
    Score player for Batting-first All-rounder.
    Criteria: Finisher metrics 45%, Middle-order metrics 20%, Bowling economy 20%, Bowling capability 15%
    """
    if player.role != "All-rounder" or not player.can_bowl:
        return 0.0, "Not an all-rounder"

    base_score = 0.0
    rationale_parts = []

    # Finisher metrics (45%)
    finisher_score, _ = score_finisher(player)
    base_score += finisher_score * 0.45
    if finisher_score >= 60:
        rationale_parts.append(f"Strong finisher ({finisher_score:.0f})")

    # Middle-order metrics (20%)
    middle_score, _ = score_middle_order(player)
    base_score += middle_score * 0.20
    if middle_score >= 50:
        rationale_parts.append(f"Middle order capable ({middle_score:.0f})")

    # Bowling economy (20%)
    if player.overall_economy:
        if player.overall_economy <= 8:
            base_score += 20
        elif player.overall_economy <= 9:
            base_score += 14
        elif player.overall_economy <= 10:
            base_score += 10
        else:
            base_score += 5
    elif player.death_economy:
        if player.death_economy <= 10:
            base_score += 16
            rationale_parts.append("Useful death bowling")
        else:
            base_score += 8
    else:
        base_score += 10  # Can bowl

    # Bowling overs capability (15%)
    if player.bowling_overs_capability >= 4:
        base_score += 15
        rationale_parts.append("Bowls 4 overs")
    else:
        base_score += 8

    # Apply auction bonus
    base_score *= 1 + get_auction_bonus(player.price_cr)

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Batting all-rounder"
    return min(base_score, 100.0), rationale


def score_bowling_allrounder(player: Player) -> Tuple[float, str]:
    """
    Score player for Bowling-first All-rounder.
    Criteria: Bowling metrics 50%, Batting average 25%, Lower-order SR 15%, Experience 10%
    """
    if player.role != "All-rounder" or not player.can_bowl:
        return 0.0, "Not an all-rounder"

    base_score = 0.0
    rationale_parts = []

    # Bowling metrics (50%)
    if player.is_spinner:
        bowling_score, _ = score_lead_spinner(player)
    else:
        bowling_score, _ = score_lead_pacer(player)

    base_score += bowling_score * 0.50
    if bowling_score >= 60:
        rationale_parts.append(f"Primary bowler ({bowling_score:.0f})")

    # Proven bowling credentials bonus — rewards players with actual bowling tags
    # This ensures bowlers with elite tags (e.g. Santner with MIDDLE_OVERS_CONTROLLER,
    # economy 7.64, 15 wickets) clearly rank above players with sparse bowling stats
    proven_bowling_tags = [
        "MIDDLE_OVERS_CONTROLLER",
        "MID_OVERS_ELITE",
        "MIDDLE_STRANGLER",
        "PROVEN_WICKET_TAKER",
        "DEATH_ELITE",
        "DEATH_COMPLETE",
        "DEATH_SPECIALIST",
        "PP_ELITE",
        "NEW_BALL_SPECIALIST",
        "PRESSURE_BUILDER",
    ]
    proven_tag_count = sum(1 for tag in player.bowler_tags if tag in proven_bowling_tags)
    if proven_tag_count >= 2:
        base_score += 15
        rationale_parts.append("Proven bowling credentials")
    elif proven_tag_count == 1:
        base_score += 10
        rationale_parts.append("Bowling specialist tag")
    elif not player.bowler_tags:
        # No bowler tags at all — significantly reduce bowling credibility
        base_score -= 8
        rationale_parts.append("Unproven bowling")

    # Batting average/capability (25%)
    batting_score, _ = score_middle_order(player)
    if batting_score < 30:
        batting_score, _ = score_finisher(player)
    base_score += batting_score * 0.25
    if batting_score >= 40:
        rationale_parts.append(f"Handy bat ({batting_score:.0f})")

    # Lower-order SR proxy (15%)
    if player.overall_sr:
        if player.overall_sr >= 150:
            base_score += 15
            rationale_parts.append(f"SR {player.overall_sr:.0f}")
        elif player.overall_sr >= 140:
            base_score += 12
        elif player.overall_sr >= 130:
            base_score += 8
        else:
            base_score += 5
    else:
        base_score += 8  # Default

    # Experience (10%)
    if player.price_cr >= 10:
        base_score += 10
    elif player.price_cr >= 5:
        base_score += 7
    else:
        base_score += 4

    rationale = ". ".join(rationale_parts[:2]) if rationale_parts else "Bowling all-rounder"
    return min(base_score, 100.0), rationale


# =============================================================================
# POSITION RANKING
# =============================================================================


def rank_position(
    players: List[Player], scoring_func, position_name: str, limit: int = 3
) -> List[PositionPlayer]:
    """Rank players for a specific position.

    Applies Founder XII bonus (+10) after base scoring for players
    in the Founder's predicted XII.
    """
    scored = []

    for player in players:
        score, rationale = scoring_func(player)
        if score > 0:
            # Apply Founder XII bonus
            if is_founder_xii(player.player_id):
                score = min(score + FOUNDER_XII_BONUS, 100.0)
                rationale = f"Founder XII. {rationale}"
            scored.append((player, score, rationale))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Create PositionPlayer objects
    ranked = []
    for i, (player, score, rationale) in enumerate(scored[:limit]):
        ranked.append(
            PositionPlayer(
                rank=i + 1,
                player=player,
                score=score,
                rationale=rationale,
            )
        )

    return ranked


def calculate_position_rating(players: List[PositionPlayer], position_name: str) -> float:
    """Calculate position depth rating out of 10"""
    if not players:
        return 1.0

    # Weight scores: #1 = 50%, #2 = 30%, #3 = 20%
    weights = [0.50, 0.30, 0.20]
    total_score = 0.0
    total_weight = 0.0

    for i, player in enumerate(players[:3]):
        if i < len(weights):
            total_score += player.score * weights[i]
            total_weight += weights[i] * 100  # Max score is 100

    if total_weight == 0:
        return 1.0

    # Normalize to 10-point scale
    rating = (total_score / total_weight) * 10

    # Bonus for having multiple quality options
    if len(players) >= 3 and players[2].score >= 40:
        rating += 0.5  # Strong third option
    if len(players) >= 2 and players[1].score >= 50:
        rating += 0.5  # Strong backup

    return round(min(rating, 10.0), 1)


def generate_what_works(players: List[PositionPlayer], position_name: str) -> str:
    """Generate 'what works' description for a position"""
    if not players:
        return "No options available"

    parts = []

    # Highlight #1 player
    p1 = players[0]
    if p1.score >= 80:
        parts.append(f"Elite #1 in {p1.player.player_name}")
    elif p1.score >= 60:
        parts.append(f"Strong #1 with {p1.player.player_name}")
    else:
        parts.append(f"{p1.player.player_name} leads")

    # Mention backup quality
    if len(players) >= 2 and players[1].score >= 50:
        parts.append(f"quality backup in {players[1].player.player_name}")
    elif len(players) >= 2:
        parts.append(f"{players[1].player.player_name} as backup")

    # Note any special strengths
    overseas_count = sum(1 for p in players if p.player.is_overseas)
    if overseas_count == 0:
        parts.append("all Indian options")

    return ". ".join(parts[:2]).capitalize() if parts else "Adequate depth"


def generate_what_doesnt(players: List[PositionPlayer], position_name: str) -> str:
    """Generate 'what doesn't work' description for a position"""
    if not players:
        return "No options at this position"

    issues = []

    # Check depth
    if len(players) < 2:
        issues.append("Only one option")
    elif len(players) >= 2 and players[1].score < 40:
        issues.append("Weak backup option")

    # Check #1 quality
    if players[0].score < 50:
        issues.append("No standout performer")

    # Check overseas dependency (softened language)
    overseas = [p for p in players if p.player.is_overseas]
    if len(overseas) >= 2 and len(players) <= 3:
        issues.append(f"Overseas mix ({len(overseas)} of {len(players)})")

    # Check score drop-off
    if len(players) >= 2 and (players[0].score - players[1].score) > 30:
        issues.append("Big gap between #1 and #2")

    if not issues:
        if players[0].score < 70:
            issues.append("Room for improvement at the top")
        else:
            issues.append("Minimal concerns")

    return ". ".join(issues[:2]).capitalize()


# =============================================================================
# DEPTH CHART GENERATION
# =============================================================================


def _filter_right_arm_pace(players: List[Player]) -> List[Player]:
    """Filter players who are right-arm pace bowlers"""
    return [
        p
        for p in players
        if p.bowling_arm == "Right-arm"
        and p.bowling_type
        and p.bowling_type in ("Fast", "Fast-Medium", "Medium")
        and p.role in ("Bowler", "All-rounder")
    ]


def _filter_left_arm_pace(players: List[Player]) -> List[Player]:
    """Filter players who are left-arm pace bowlers"""
    return [
        p
        for p in players
        if p.bowling_arm == "Left-arm"
        and p.bowling_type
        and p.bowling_type in ("Fast", "Fast-Medium", "Medium")
        and p.role in ("Bowler", "All-rounder")
    ]


def _filter_off_spin(players: List[Player]) -> List[Player]:
    """Filter players who bowl off-spin (includes right-arm finger spin)"""
    result = []
    for p in players:
        if p.role not in ("Bowler", "All-rounder"):
            continue
        if not p.bowling_type:
            continue
        bt = p.bowling_type
        if bt in ("Off-spin", "Off-break"):
            result.append(p)
        elif p.bowling_arm == "Right-arm" and "spin" in bt.lower():
            result.append(p)
    return result


def _filter_leg_spin(players: List[Player]) -> List[Player]:
    """Filter players who bowl leg-spin (right-arm wrist spin)"""
    result = []
    for p in players:
        if p.role not in ("Bowler", "All-rounder"):
            continue
        if not p.bowling_type:
            continue
        bt = p.bowling_type
        if bt in ("Leg-spin", "Wrist-spin", "Leg-break") and p.bowling_arm != "Left-arm":
            result.append(p)
    return result


def _filter_left_arm_spin(players: List[Player]) -> List[Player]:
    """Filter players who are left-arm spinners (orthodox, slow left-arm)"""
    result = []
    for p in players:
        if p.role not in ("Bowler", "All-rounder"):
            continue
        if not p.bowling_type:
            continue
        if p.bowling_arm != "Left-arm":
            continue
        bt_lower = p.bowling_type.lower()
        if any(kw in bt_lower for kw in ("orthodox", "spin", "slow")):
            result.append(p)
    return result


def _create_typed_bowling_position(
    players: List[Player],
    filter_func,
    scoring_func,
    position_name: str,
    display_name: str,
    limit: int = 3,
) -> Position:
    """
    Create a bowling position filtered by bowling type.
    If no players match the filter, returns an empty position with rating 0.
    """
    filtered = filter_func(players)

    if not filtered:
        return Position(
            name=display_name,
            rating=0.0,
            what_works="No options available",
            what_doesnt="No options",
            players=[],
            overseas_count=0,
        )

    return _create_position(filtered, scoring_func, position_name, display_name, limit)


def _create_position(
    players: List[Player], scoring_func, position_name: str, display_name: str, limit: int = 3
) -> Position:
    """
    Create a Position object by ranking players with given scoring function.

    Args:
        players: List of all team players
        scoring_func: Function to score players for this position
        position_name: Internal position key name
        display_name: Human-readable position name
        limit: Max number of players to rank

    Returns:
        Position object with ranked players
    """
    ranked_players = rank_position(players, scoring_func, position_name, limit)
    return Position(
        name=display_name,
        rating=calculate_position_rating(ranked_players, position_name),
        what_works=generate_what_works(ranked_players, position_name),
        what_doesnt=generate_what_doesnt(ranked_players, position_name),
        players=ranked_players,
        overseas_count=sum(1 for p in ranked_players if p.player.is_overseas),
    )


def _create_wicketkeeper_position(players: List[Player]) -> Position:
    """
    Create the Wicketkeeper position with special scoring.

    Wicketkeepers require batting position-aware scoring.

    Args:
        players: List of all team players

    Returns:
        Position object for wicketkeeper role
    """
    keepers = [p for p in players if p.is_wicketkeeper or p.role == "Wicketkeeper"]
    keeper_scored = []

    for k in keepers:
        # Determine batting position score based on entry point
        if k.avg_entry_ball and k.avg_entry_ball <= 20:
            bat_score, _ = score_opener(k)
        elif k.avg_entry_ball and k.avg_entry_ball >= 60:
            bat_score, _ = score_finisher(k)
        else:
            bat_score, _ = score_middle_order(k)

        score, rationale = score_wicketkeeper(k, bat_score)
        if score > 0:
            keeper_scored.append(PositionPlayer(rank=0, player=k, score=score, rationale=rationale))

    # Sort and assign ranks
    keeper_scored.sort(key=lambda x: x.score, reverse=True)
    for i, kp in enumerate(keeper_scored):
        kp.rank = i + 1

    keeper_players = keeper_scored[:2]
    return Position(
        name="Wicketkeeper",
        rating=calculate_position_rating(keeper_players, "Wicketkeeper"),
        what_works=generate_what_works(keeper_players, "Wicketkeeper"),
        what_doesnt=generate_what_doesnt(keeper_players, "Wicketkeeper"),
        players=keeper_players,
        overseas_count=sum(1 for p in keeper_players if p.player.is_overseas),
    )


def _identify_vulnerabilities(positions: Dict[str, Position]) -> List[str]:
    """
    Identify team vulnerabilities based on position analysis.

    Args:
        positions: Dictionary of all positions

    Returns:
        List of vulnerability descriptions
    """
    vulnerabilities = []

    # Check keeper depth
    if len(positions["wicketkeeper"].players) < 2:
        vulnerabilities.append("Single keeper risk - no backup")

    # Check overseas dependency (softened: 3+ overseas in a single position)
    for pos_name, pos in positions.items():
        if pos.overseas_count >= 3 and len(pos.players) <= 3:
            vulnerabilities.append(f"{pos.name}: overseas dependent")

    # Check weak positions
    for pos_name, pos in positions.items():
        if pos.rating < 5.0:
            vulnerabilities.append(f"{pos.name}: thin depth (rating {pos.rating})")

    return vulnerabilities[:5]


def generate_team_depth_chart(team: str, players: List[Player]) -> DepthChart:
    """
    Generate complete depth chart for a team.

    Creates position-by-position rankings for all 9 defined positions
    with ratings, strengths, weaknesses, and vulnerability analysis.

    Args:
        team: Team name
        players: List of Player objects for the team

    Returns:
        DepthChart object with complete position analysis
    """
    logger.info("Generating depth chart for %s", team)
    logger.debug("Processing %d players for %s", len(players), team)
    positions = {}

    # Batting positions
    positions["opener"] = _create_position(players, score_opener, "Opener", "Opener", 3)
    positions["number_3"] = _create_position(
        players, score_number_three, "#3 Batter", "#3 Batter", 3
    )
    positions["middle_order"] = _create_position(
        players, score_middle_order, "Middle Order", "Middle Order #4-5", 3
    )
    positions["finisher"] = _create_position(
        players, score_finisher, "Finisher", "Finisher #6-7", 3
    )

    # Wicketkeeper (special handling)
    positions["wicketkeeper"] = _create_wicketkeeper_position(players)

    # Bowling positions — type-specific
    positions["right_arm_pace"] = _create_typed_bowling_position(
        players, _filter_right_arm_pace, score_lead_pacer, "Right-arm Pace", "Right-arm Pace", 3
    )
    positions["left_arm_pace"] = _create_typed_bowling_position(
        players, _filter_left_arm_pace, score_lead_pacer, "Left-arm Pace", "Left-arm Pace", 3
    )
    positions["off_spin"] = _create_typed_bowling_position(
        players, _filter_off_spin, score_lead_spinner, "Off Spin", "Off Spin", 3
    )
    positions["leg_spin"] = _create_typed_bowling_position(
        players, _filter_leg_spin, score_lead_spinner, "Leg Spin", "Leg Spin", 3
    )
    positions["left_arm_spin"] = _create_typed_bowling_position(
        players, _filter_left_arm_spin, score_lead_spinner, "Left-arm Spin", "Left-arm Spin", 3
    )
    positions["middle_overs_specialist"] = _create_position(
        players,
        score_middle_overs_specialist,
        "Middle Overs Specialist",
        "Middle Overs Specialist",
        3,
    )

    # All-rounder positions
    positions["allrounder_batting"] = _create_position(
        players, score_batting_allrounder, "Batting AR", "Allrounder", 3
    )
    positions["allrounder_bowling"] = _create_position(
        players, score_bowling_allrounder, "Bowling AR", "Allrounder", 3
    )

    # Calculate overall metrics
    ratings = {k: v.rating for k, v in positions.items()}
    avg_rating = sum(ratings.values()) / len(ratings) if ratings else 5.0
    strongest = max(ratings, key=ratings.get)
    weakest = min(ratings, key=ratings.get)

    # Identify vulnerabilities
    vulnerabilities = _identify_vulnerabilities(positions)

    return DepthChart(
        team_name=team,
        team_abbrev=TEAM_ABBREV[team],
        positions=positions,
        overall_rating=round(avg_rating, 1),
        strongest_position=positions[strongest].name,
        weakest_position=positions[weakest].name,
        vulnerabilities=vulnerabilities,
    )


# =============================================================================
# OUTPUT GENERATION
# =============================================================================


def depth_chart_to_dict(dc: DepthChart) -> Dict[str, Any]:
    """Convert DepthChart to JSON-serializable dict"""
    positions_dict = {}

    for key, pos in dc.positions.items():
        positions_dict[key] = {
            "name": pos.name,
            "rating": pos.rating,
            "what_works": pos.what_works,
            "what_doesnt": pos.what_doesnt,
            "overseas_count": pos.overseas_count,
            "players": [
                {
                    "rank": p.rank,
                    "name": p.player.player_name,
                    "player_id": p.player.player_id,
                    "score": round(p.score, 1),
                    "rationale": p.rationale,
                    "is_overseas": p.player.is_overseas,
                    "price_cr": p.player.price_cr,
                    "bowling_type": p.player.bowling_type,
                    "bowling_arm": p.player.bowling_arm,
                    "secondary_positions": p.secondary_positions,
                }
                for p in pos.players
            ],
        }

    return {
        "team": dc.team_abbrev,
        "team_name": dc.team_name,
        "overall_rating": dc.overall_rating,
        "strongest_position": dc.strongest_position,
        "weakest_position": dc.weakest_position,
        "vulnerabilities": dc.vulnerabilities,
        "positions": positions_dict,
    }


def generate_cross_team_comparison(
    all_charts: Dict[str, DepthChart],
) -> Dict[str, Dict[str, float]]:
    """Generate cross-team comparison table"""
    comparison = {}

    for team, dc in all_charts.items():
        # Compute average pace rating across right-arm and left-arm pace
        pace_ratings = [
            dc.positions[k].rating
            for k in ("right_arm_pace", "left_arm_pace")
            if k in dc.positions and dc.positions[k].rating > 0
        ]
        avg_pace = round(sum(pace_ratings) / len(pace_ratings), 1) if pace_ratings else 0.0

        # Compute average spin rating across off-spin, leg-spin, left-arm spin
        spin_ratings = [
            dc.positions[k].rating
            for k in ("off_spin", "leg_spin", "left_arm_spin")
            if k in dc.positions and dc.positions[k].rating > 0
        ]
        avg_spin = round(sum(spin_ratings) / len(spin_ratings), 1) if spin_ratings else 0.0

        comparison[dc.team_abbrev] = {
            "opener": dc.positions["opener"].rating,
            "number_3": dc.positions["number_3"].rating,
            "middle_order": dc.positions["middle_order"].rating,
            "finisher": dc.positions["finisher"].rating,
            "wicketkeeper": dc.positions["wicketkeeper"].rating,
            "pace": avg_pace,
            "spin": avg_spin,
            "middle_overs_specialist": dc.positions.get(
                "middle_overs_specialist",
                Position(name="", rating=0.0, what_works="", what_doesnt="", players=[]),
            ).rating,
            "allrounder": round(
                (
                    dc.positions["allrounder_batting"].rating
                    + dc.positions["allrounder_bowling"].rating
                )
                / 2,
                1,
            ),
            "overall": dc.overall_rating,
        }

    return comparison


def main() -> int:
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("CRICKET PLAYBOOK - DEPTH CHARTS GENERATOR")
    logger.info("=" * 60)

    # Load data
    logger.info("[1/5] Loading data...")
    squads = load_squads()
    contracts = load_contracts()
    tags = load_player_tags()
    entry_points = load_entry_points()
    bowler_metrics = load_bowler_phase_performance()

    # Load Founder XII data
    global _FOUNDER_XII
    _FOUNDER_XII = load_founder_xii()

    logger.info("Loaded %d teams", len(squads))
    logger.info("Loaded %d player contracts", len(contracts))
    logger.info("Loaded %d batting entry points", len(entry_points))
    logger.info("Loaded %d bowler phase records", len(bowler_metrics))
    logger.info("Loaded %d Founder XII players", len(_FOUNDER_XII))

    # Build player objects
    logger.info("[2/5] Building player database...")
    team_players = build_players(squads, contracts, tags, entry_points, bowler_metrics)

    total_players = sum(len(p) for p in team_players.values())
    logger.info("Built %d player profiles", total_players)

    # Generate depth charts
    logger.info("[3/5] Generating Depth Charts...")
    all_charts = {}

    for team in IPL_TEAMS:
        logger.debug("Processing team: %s", team)
        players = team_players.get(team, [])

        if not players:
            logger.warning("No players found for %s", team)
            continue

        depth_chart = generate_team_depth_chart(team, players)
        all_charts[team] = depth_chart

        # Log summary
        logger.debug(
            "%s - Rating: %.1f/10, Strongest: %s, Weakest: %s",
            team,
            depth_chart.overall_rating,
            depth_chart.strongest_position,
            depth_chart.weakest_position,
        )
        if depth_chart.vulnerabilities:
            logger.debug("%s vulnerabilities: %s", team, depth_chart.vulnerabilities[0])

    # Save outputs
    logger.info("[4/5] Saving outputs...")

    # Ensure output directory exists
    DEPTH_CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.debug("Output directory: %s", DEPTH_CHARTS_DIR)

    # Save consolidated JSON
    output_data = {
        "generated_at": "2026-02-02",
        "version": "1.0",
        "methodology": "Position-specific weighted scoring per PRD",
        "teams": {},
        "cross_team_comparison": generate_cross_team_comparison(all_charts),
    }

    for team, dc in all_charts.items():
        output_data["teams"][TEAM_ABBREV[team]] = depth_chart_to_dict(dc)

    output_file = DEPTH_CHARTS_DIR / "depth_charts_2026.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)
    logger.info("Saved consolidated output: %s", output_file)

    # Save per-team files
    for team, dc in all_charts.items():
        team_file = DEPTH_CHARTS_DIR / f"{TEAM_ABBREV[team].lower()}_depth_chart.json"
        with open(team_file, "w") as f:
            json.dump(depth_chart_to_dict(dc), f, indent=2)

    logger.info("Saved %d team files", len(all_charts))

    # Generate README
    readme_content = generate_readme(all_charts)
    readme_file = DEPTH_CHARTS_DIR / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)
    logger.info("Saved README: %s", readme_file)

    # Log summary
    logger.info("[5/5] Generation Summary")
    logger.info("=" * 60)

    comparison = generate_cross_team_comparison(all_charts)
    sorted_teams = sorted(comparison.items(), key=lambda x: x[1]["overall"], reverse=True)

    logger.info("CROSS-TEAM DEPTH COMPARISON")
    for abbrev, ratings in sorted_teams:
        logger.debug(
            "%s - Overall: %.1f, Opener: %.1f, Pace: %.1f, Spin: %.1f",
            abbrev,
            ratings["overall"],
            ratings["opener"],
            ratings["pace"],
            ratings["spin"],
        )

    logger.info("Ready for Domain Sanity review.")
    logger.info("=" * 60)


def generate_readme(all_charts: Dict[str, DepthChart]) -> str:
    """Generate README content for the depth charts output"""
    comparison = generate_cross_team_comparison(all_charts)
    sorted_teams = sorted(comparison.items(), key=lambda x: x[1]["overall"], reverse=True)

    readme = """# IPL 2026 Depth Charts

Generated: 2026-02-02
Version: 1.0

## Overview

This directory contains position-by-position depth charts for all 10 IPL 2026 teams.
Each team's depth chart shows ranked player options at defined positions:

**Batting:**
1. **Opener** - Top 3 options for opening the batting
2. **#3 Batter** - Top 3 versatile options for the crucial #3 slot
3. **Middle Order #4-5** - Top 3 middle order batters
4. **Finisher #6-7** - Top 3 death overs specialists
5. **Wicketkeeper** - Primary + Backup keepers

**Bowling (type-specific):**
6. **Right-arm Pace** - Right-arm fast/medium bowlers
7. **Left-arm Pace** - Left-arm fast/medium bowlers
8. **Off Spin** - Off-spinners and right-arm finger spinners
9. **Leg Spin** - Leg-spinners and wrist-spinners (non left-arm)
10. **Left-arm Spin** - Left-arm orthodox/slow spinners
11. **Middle Overs Specialist** - All bowling types, scored by overs 7-15

**Hybrid:**
12. **All-rounder (Batting)** - Batting-first ARs
13. **All-rounder (Bowling)** - Bowling-first ARs

All-rounders compete in batting positions with NO role penalty. Founder XII
players receive a +10 scoring bonus across all positions.

## Position Ratings

Ratings are out of 10 (with decimals) based on:
- Quality of #1 option (50% weight)
- Quality of backup (30% weight)
- Quality of third option (20% weight)
- Bonuses for strong depth

## Cross-Team Comparison

| Team | Opener | #3 | Middle | Finisher | Keeper | Pace | Spin | Mid-Ov | AR | Overall |
|------|--------|-----|--------|----------|--------|------|------|--------|-----|---------|
"""

    for abbrev, ratings in sorted_teams:
        readme += f"| {abbrev} | {ratings['opener']:.1f} | {ratings['number_3']:.1f} | "
        readme += f"{ratings['middle_order']:.1f} | {ratings['finisher']:.1f} | "
        readme += f"{ratings['wicketkeeper']:.1f} | {ratings['pace']:.1f} | "
        readme += f"{ratings['spin']:.1f} | {ratings['middle_overs_specialist']:.1f} | "
        readme += f"{ratings['allrounder']:.1f} | "
        readme += f"**{ratings['overall']:.1f}** |\n"

    readme += """
## Files

- `depth_charts_2026.json` - Consolidated depth charts for all teams
- `{team}_depth_chart.json` - Individual team depth charts
- `README.md` - This file

## Methodology

Scoring criteria per position as defined in PRD:

### Batting Positions
- **Opener**: PP SR (30%), PP Boundary% (20%), Career Avg (15%), Recent form (20%), Experience (15%)
- **#3 Batter**: Adaptability across phases, versatility score
- **Middle Order**: Middle overs performance (45%), Spin performance (25%), Reliability (30%)
- **Finisher**: Death SR (35%), Boundary% (20%), Career SR (15%), Death Avg (15%), Bowling (15%)

### Bowling Positions (type-specific)
- **Right-arm Pace / Left-arm Pace**: Wickets (25%), Death Eco (25%), PP Eco (20%), Career Eco (15%), Experience (15%)
- **Off Spin / Leg Spin / Left-arm Spin**: Middle Eco (30%), SR (25%), Career Eco (15%), Versatility (15%), Experience (15%)
- **Middle Overs Specialist**: Middle Eco (40%), Middle Wkts (20%), Overall Eco (20%), Experience (20%)

### Special Positions
- **Wicketkeeper**: Keeping quality (30%), Batting at slot (50%), Experience (20%)
- **All-rounder (Batting)**: Bat 65% / Bowl 35%
- **All-rounder (Bowling)**: Bowl 65% / Bat 35%

## Overlap Rules

- All-rounders appear in their batting position AND in All-rounder section
- Keepers appear in their batting position AND in Keeper section
- Secondary positions flagged with "(Also: X)"

---

*Generated by Cricket Playbook Depth Charts Algorithm*
*PRD: /governance/tasks/DEPTH_CHARTS_PRD.md*
"""

    return readme


if __name__ == "__main__":
    main()
