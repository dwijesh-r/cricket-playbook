#!/usr/bin/env python3
"""
Cricket Playbook - Data Ingestion Pipeline
==========================================
Ingests Cricsheet T20 ball-by-ball data into DuckDB.

Usage:
    python scripts/ingest.py

Output:
    - data/cricket_playbook.duckdb (database)
    - data/manifests/manifest.json (ingestion log)
    - data/processed/schema.md (schema documentation)
"""

import hashlib
import json
import sys
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import duckdb
import pandas as pd

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging_config import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "cricket_playbook.duckdb"
MANIFEST_PATH = PROJECT_ROOT / "data" / "manifests" / "manifest.json"
SCHEMA_DOC_PATH = PROJECT_ROOT / "data" / "processed" / "schema.md"

DATA_VERSION = "1.1.0"  # Added WK detection + match_phase


def generate_id(text: str) -> str:
    """Generate a short hash ID from text."""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def slugify(text: str) -> str:
    """Convert text to slug format."""
    return text.lower().replace(" ", "_").replace("'", "").replace("-", "_")


def parse_over_ball(over_decimal: float) -> Tuple[int, int]:
    """Convert decimal over (e.g., 5.3) to (over, ball)."""
    over = int(over_decimal)
    ball = round((over_decimal - over) * 10)
    return over, ball


def get_match_phase(over: int, balls_per_over: int = 6) -> str:
    """
    Determine match phase based on over number.
    - Powerplay: overs 0-5 (1-6 in cricket terms)
    - Middle: overs 6-14 (7-15 in cricket terms)
    - Death: overs 15-19 (16-20 in cricket terms)

    For The Hundred (5-ball overs), adjusts accordingly.
    """
    if balls_per_over == 5:  # The Hundred
        if over < 5:
            return "powerplay"
        elif over < 15:
            return "middle"
        else:
            return "death"
    else:  # Standard T20
        if over < 6:
            return "powerplay"
        elif over < 15:
            return "middle"
        else:
            return "death"


class CricketIngester:
    """Main ingestion class for Cricsheet data."""

    def __init__(self):
        self.tournaments = {}
        self.teams = {}
        self.players = {}
        self.player_names = []  # For name history tracking
        self.venues = {}
        self.matches = []
        self.powerplays = []
        self.balls = []
        self.player_match_perf = []

        # Track wicketkeeper candidates (fielders in stumping dismissals)
        self.stumping_fielders = defaultdict(int)  # player_id -> stumping count

        self.stats = {
            "zip_files": 0,
            "matches_processed": 0,
            "balls_processed": 0,
            "players_found": 0,
            "errors": [],
        }

    def extract_tournament_info(self, info: Dict[str, Any], source_file: str) -> str:
        """Extract or create tournament dimension."""
        event = info.get("event", {})
        event_name = event.get("name", "Unknown") if isinstance(event, dict) else str(event)

        # Generate tournament ID
        tournament_id = slugify(event_name)

        if tournament_id not in self.tournaments:
            self.tournaments[tournament_id] = {
                "tournament_id": tournament_id,
                "tournament_name": event_name,
                "country": self._infer_country(event_name),
                "format": info.get("match_type", "T20"),
                "gender": info.get("gender", "male"),
            }

        return tournament_id

    def _infer_country(self, event_name: str) -> str:
        """Infer country from tournament name."""
        mapping = {
            "Indian Premier League": "India",
            "Big Bash League": "Australia",
            "Pakistan Super League": "Pakistan",
            "Caribbean Premier League": "West Indies",
            "T20 Blast": "England",
            "The Hundred": "England",
            "SA20": "South Africa",
            "International": "International",
        }
        for key, country in mapping.items():
            if key.lower() in event_name.lower():
                return country
        return "Unknown"

    def extract_team(self, team_name: str) -> str:
        """Extract or create team dimension."""
        team_id = generate_id(team_name)

        if team_id not in self.teams:
            # Generate short name (first letters of each word)
            words = team_name.split()
            short_name = "".join(w[0].upper() for w in words if w[0].isalpha())[:4]

            self.teams[team_id] = {
                "team_id": team_id,
                "team_name": team_name,
                "short_name": short_name,
            }

        return team_id

    def extract_player(
        self,
        player_name: str,
        player_cricsheet_id: str,
        match_date: str,
        source_file: str,
    ) -> str:
        """Extract or create player dimension with name tracking."""
        player_id = player_cricsheet_id or generate_id(player_name)

        if player_id not in self.players:
            self.players[player_id] = {
                "player_id": player_id,
                "current_name": player_name,
                "first_seen_date": match_date,
                "last_seen_date": match_date,
                "matches_played": 0,
            }
            # Track initial name
            self.player_names.append(
                {
                    "player_id": player_id,
                    "player_name": player_name,
                    "valid_from": match_date,
                    "valid_to": None,
                    "source_file": source_file,
                }
            )
        else:
            # Update last seen
            if match_date > self.players[player_id]["last_seen_date"]:
                self.players[player_id]["last_seen_date"] = match_date
                # Check for name change
                if self.players[player_id]["current_name"] != player_name:
                    # Close previous name record
                    for record in reversed(self.player_names):
                        if record["player_id"] == player_id and record["valid_to"] is None:
                            record["valid_to"] = match_date
                            break
                    # Add new name
                    self.player_names.append(
                        {
                            "player_id": player_id,
                            "player_name": player_name,
                            "valid_from": match_date,
                            "valid_to": None,
                            "source_file": source_file,
                        }
                    )
                    self.players[player_id]["current_name"] = player_name

        return player_id

    def extract_venue(self, info: Dict[str, Any]) -> str:
        """Extract or create venue dimension."""
        venue_name = info.get("venue", "Unknown")
        city = info.get("city", "Unknown")

        venue_id = generate_id(f"{venue_name}_{city}")

        if venue_id not in self.venues:
            self.venues[venue_id] = {
                "venue_id": venue_id,
                "venue_name": venue_name,
                "city": city,
            }

        return venue_id

    def process_match(self, match_data: Dict[str, Any], source_file: str) -> None:
        """Process a single match JSON."""
        info = match_data.get("info", {})
        innings_data = match_data.get("innings", [])

        # Extract match date
        dates = info.get("dates", [])
        match_date = dates[0] if dates else "1900-01-01"

        # Extract match ID
        match_id = Path(source_file).stem

        # Extract dimensions
        tournament_id = self.extract_tournament_info(info, source_file)
        venue_id = self.extract_venue(info)

        teams = info.get("teams", [])
        team1_id = self.extract_team(teams[0]) if len(teams) > 0 else None
        team2_id = self.extract_team(teams[1]) if len(teams) > 1 else None

        # Extract player registry
        registry = info.get("registry", {}).get("people", {})

        # Process players from team lists
        players_by_team = info.get("players", {})
        for team_name, player_list in players_by_team.items():
            for player_name in player_list:
                cricsheet_id = registry.get(player_name)
                self.extract_player(player_name, cricsheet_id, match_date, source_file)

        # Toss info
        toss = info.get("toss", {})
        toss_winner = toss.get("winner")
        toss_winner_id = self.extract_team(toss_winner) if toss_winner else None
        toss_decision = toss.get("decision")

        # Outcome
        outcome = info.get("outcome", {})
        winner = outcome.get("winner")
        winner_id = self.extract_team(winner) if winner else None

        outcome_by = outcome.get("by", {})
        if "runs" in outcome_by:
            outcome_type = "runs"
            outcome_margin = outcome_by["runs"]
        elif "wickets" in outcome_by:
            outcome_type = "wickets"
            outcome_margin = outcome_by["wickets"]
        elif "result" in outcome:
            outcome_type = outcome["result"]  # "tie", "no result"
            outcome_margin = None
        else:
            outcome_type = None
            outcome_margin = None

        # Player of match
        pom_list = info.get("player_of_match", [])
        pom_name = pom_list[0] if pom_list else None
        pom_id = None
        if pom_name:
            pom_cricsheet_id = registry.get(pom_name)
            pom_id = self.extract_player(pom_name, pom_cricsheet_id, match_date, source_file)

        # Event info
        event = info.get("event", {})
        match_number = event.get("match_number") if isinstance(event, dict) else None
        stage = event.get("stage") if isinstance(event, dict) else None

        # Create match record
        match_record = {
            "match_id": match_id,
            "tournament_id": tournament_id,
            "match_number": match_number,
            "stage": stage,
            "season": info.get("season"),
            "match_date": match_date,
            "venue_id": venue_id,
            "team1_id": team1_id,
            "team2_id": team2_id,
            "toss_winner_id": toss_winner_id,
            "toss_decision": toss_decision,
            "winner_id": winner_id,
            "outcome_type": outcome_type,
            "outcome_margin": outcome_margin,
            "player_of_match_id": pom_id,
            "balls_per_over": info.get("balls_per_over", 6),
            "data_version": DATA_VERSION,
            "is_active": True,
            "ingested_at": datetime.now().isoformat(),
            "source_file": source_file,
        }
        self.matches.append(match_record)

        # Track player performances per match
        player_perf_tracker = defaultdict(
            lambda: {
                "batting_position": None,
                "did_bat": False,
                "did_bowl": False,
                "did_keep_wicket": False,
            }
        )
        batting_position_counter = {1: 0, 2: 0}  # Per innings

        # Process innings
        for innings_idx, innings in enumerate(innings_data, start=1):
            batting_team_name = innings.get("team")
            batting_team_id = self.extract_team(batting_team_name) if batting_team_name else None
            bowling_team_id = team2_id if batting_team_id == team1_id else team1_id

            # Process powerplays
            powerplays = innings.get("powerplays", [])
            for pp_idx, pp in enumerate(powerplays, start=1):
                self.powerplays.append(
                    {
                        "powerplay_id": f"{match_id}_{innings_idx}_{pp_idx}",
                        "match_id": match_id,
                        "innings": innings_idx,
                        "powerplay_seq": pp_idx,
                        "powerplay_type": pp.get("type"),
                        "from_over": pp.get("from"),
                        "to_over": pp.get("to"),
                    }
                )

            # Process overs and deliveries
            overs = innings.get("overs", [])
            ball_seq = 0
            batters_seen = set()

            for over_data in overs:
                over_num = over_data.get("over", 0)
                deliveries = over_data.get("deliveries", [])

                for ball_idx, delivery in enumerate(deliveries, start=1):
                    ball_seq += 1

                    batter_name = delivery.get("batter")
                    bowler_name = delivery.get("bowler")
                    non_striker_name = delivery.get("non_striker")

                    # Get player IDs
                    batter_id = None
                    bowler_id = None
                    non_striker_id = None

                    if batter_name:
                        batter_cricsheet_id = registry.get(batter_name)
                        batter_id = self.extract_player(
                            batter_name, batter_cricsheet_id, match_date, source_file
                        )
                        player_perf_tracker[(batter_id, batting_team_id)]["did_bat"] = True

                        # Track batting position
                        if batter_id not in batters_seen:
                            batters_seen.add(batter_id)
                            batting_position_counter[innings_idx] += 1
                            player_perf_tracker[(batter_id, batting_team_id)][
                                "batting_position"
                            ] = batting_position_counter[innings_idx]

                    if bowler_name:
                        bowler_cricsheet_id = registry.get(bowler_name)
                        bowler_id = self.extract_player(
                            bowler_name, bowler_cricsheet_id, match_date, source_file
                        )
                        player_perf_tracker[(bowler_id, bowling_team_id)]["did_bowl"] = True

                    if non_striker_name:
                        non_striker_cricsheet_id = registry.get(non_striker_name)
                        non_striker_id = self.extract_player(
                            non_striker_name,
                            non_striker_cricsheet_id,
                            match_date,
                            source_file,
                        )

                        if non_striker_id not in batters_seen:
                            batters_seen.add(non_striker_id)
                            batting_position_counter[innings_idx] += 1
                            player_perf_tracker[(non_striker_id, batting_team_id)][
                                "batting_position"
                            ] = batting_position_counter[innings_idx]

                    # Runs
                    runs = delivery.get("runs", {})
                    batter_runs = runs.get("batter", 0)
                    extra_runs = runs.get("extras", 0)
                    total_runs = runs.get("total", 0)

                    # Extras
                    extras = delivery.get("extras", {})
                    extra_type = None
                    if extras:
                        extra_type = list(extras.keys())[0]  # wides, noballs, byes, legbyes

                    # Wickets
                    wickets = delivery.get("wickets", [])
                    is_wicket = len(wickets) > 0
                    wicket_type = None
                    player_out_id = None
                    fielder_id = None

                    if wickets:
                        wicket = wickets[0]  # Take first wicket
                        wicket_type = wicket.get("kind")

                        player_out_name = wicket.get("player_out")
                        if player_out_name:
                            player_out_cricsheet_id = registry.get(player_out_name)
                            player_out_id = self.extract_player(
                                player_out_name,
                                player_out_cricsheet_id,
                                match_date,
                                source_file,
                            )

                        fielders = wicket.get("fielders", [])
                        if fielders:
                            fielder_name = fielders[0].get("name")
                            if fielder_name:
                                fielder_cricsheet_id = registry.get(fielder_name)
                                fielder_id = self.extract_player(
                                    fielder_name,
                                    fielder_cricsheet_id,
                                    match_date,
                                    source_file,
                                )

                        # Detect wicket keeper (stumped dismissals)
                        if wicket_type == "stumped" and fielder_id:
                            player_perf_tracker[(fielder_id, bowling_team_id)][
                                "did_keep_wicket"
                            ] = True
                            self.stumping_fielders[fielder_id] += 1  # Track for WK detection

                    # Is legal ball?
                    is_legal = extra_type not in ("wides", "noballs")

                    # Determine match phase
                    balls_per_over = info.get("balls_per_over", 6)
                    match_phase = get_match_phase(over_num, balls_per_over)

                    # Create ball record
                    ball_id = f"{match_id}_{innings_idx}_{over_num}_{ball_idx}"

                    self.balls.append(
                        {
                            "ball_id": ball_id,
                            "match_id": match_id,
                            "innings": innings_idx,
                            "over": over_num,
                            "ball": ball_idx,
                            "ball_seq": ball_seq,
                            "batting_team_id": batting_team_id,
                            "bowling_team_id": bowling_team_id,
                            "batter_id": batter_id,
                            "bowler_id": bowler_id,
                            "non_striker_id": non_striker_id,
                            "batter_runs": batter_runs,
                            "extra_runs": extra_runs,
                            "total_runs": total_runs,
                            "extra_type": extra_type,
                            "is_wicket": is_wicket,
                            "wicket_type": wicket_type,
                            "player_out_id": player_out_id,
                            "fielder_id": fielder_id,
                            "is_legal_ball": is_legal,
                            "match_phase": match_phase,
                            "data_version": DATA_VERSION,
                            "ingested_at": datetime.now().isoformat(),
                            "source_file": source_file,
                        }
                    )

                    self.stats["balls_processed"] += 1

        # Save player match performances
        for (player_id, team_id), perf in player_perf_tracker.items():
            self.player_match_perf.append(
                {
                    "player_id": player_id,
                    "match_id": match_id,
                    "team_id": team_id,
                    "batting_position": perf["batting_position"],
                    "did_bat": perf["did_bat"],
                    "did_bowl": perf["did_bowl"],
                    "did_keep_wicket": perf["did_keep_wicket"],
                }
            )

            # Increment matches played
            self.players[player_id]["matches_played"] += 1

        self.stats["matches_processed"] += 1

    def process_zip_file(self, zip_path: Path) -> None:
        """Process all JSON files in a zip archive."""
        logger.info("Processing: %s", zip_path.name)
        self.stats["zip_files"] += 1

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                json_files = [f for f in zf.namelist() if f.endswith(".json")]
                logger.debug("Found %d JSON files in %s", len(json_files), zip_path.name)

                for json_file in json_files:
                    try:
                        with zf.open(json_file) as f:
                            match_data = json.load(f)
                            source_file = f"{zip_path.stem}/{json_file}"
                            self.process_match(match_data, source_file)
                    except Exception as e:
                        logger.error("Error processing %s/%s: %s", zip_path.name, json_file, str(e))
                        self.stats["errors"].append(f"{zip_path.name}/{json_file}: {str(e)}")
        except Exception as e:
            logger.error("Error opening zip file %s: %s", zip_path.name, str(e))
            self.stats["errors"].append(f"{zip_path.name}: {str(e)}")

    def derive_player_roles(self) -> None:
        """Derive primary role and wicketkeeper status for each player based on match data."""
        player_batting = defaultdict(int)
        player_bowling = defaultdict(int)
        player_top6_batting = defaultdict(int)
        player_keeping = defaultdict(int)  # Matches where they kept wicket

        for perf in self.player_match_perf:
            pid = perf["player_id"]
            if perf["did_bat"]:
                player_batting[pid] += 1
                if perf["batting_position"] and perf["batting_position"] <= 6:
                    player_top6_batting[pid] += 1
            if perf["did_bowl"]:
                player_bowling[pid] += 1
            if perf["did_keep_wicket"]:
                player_keeping[pid] += 1

        for player_id, player in self.players.items():
            matches = player["matches_played"]
            if matches == 0:
                player["primary_role"] = "Unknown"
                player["is_wicketkeeper"] = False
                continue

            bat_pct = player_batting[player_id] / matches
            bowl_pct = player_bowling[player_id] / matches
            top6_pct = (
                player_top6_batting[player_id] / matches if player_batting[player_id] > 0 else 0
            )

            # Wicketkeeper detection:
            # - Has at least 3 stumpings as fielder, OR
            # - Kept wicket in >30% of matches played
            stumpings = self.stumping_fielders.get(player_id, 0)
            keep_pct = player_keeping[player_id] / matches
            player["is_wicketkeeper"] = stumpings >= 3 or keep_pct > 0.3

            # Primary role determination
            if bowl_pct > 0.5 and top6_pct < 0.3:
                player["primary_role"] = "Bowler"
            elif top6_pct > 0.5 and bowl_pct < 0.2:
                player["primary_role"] = "Batter"
            elif bat_pct > 0.3 and bowl_pct > 0.3:
                player["primary_role"] = "All-rounder"
            elif bat_pct > bowl_pct:
                player["primary_role"] = "Batter"
            else:
                player["primary_role"] = "Bowler"

        self.stats["players_found"] = len(self.players)
        self.stats["wicketkeepers_found"] = sum(
            1 for p in self.players.values() if p.get("is_wicketkeeper")
        )

    def load_to_duckdb(self) -> None:
        """Load all data into DuckDB."""
        logger.info("Loading to DuckDB: %s", DB_PATH)

        # Remove existing database to start fresh
        if DB_PATH.exists():
            logger.debug("Removing existing database")
            DB_PATH.unlink()

        conn = duckdb.connect(str(DB_PATH))

        # Create and load dimension tables
        logger.info("Loading dim_tournament (%d records)...", len(self.tournaments))
        df_tournaments = pd.DataFrame(list(self.tournaments.values()))  # noqa: F841
        conn.execute("CREATE TABLE dim_tournament AS SELECT * FROM df_tournaments")

        logger.info("Loading dim_team (%d records)...", len(self.teams))
        df_teams = pd.DataFrame(list(self.teams.values()))  # noqa: F841
        conn.execute("CREATE TABLE dim_team AS SELECT * FROM df_teams")

        logger.info("Loading dim_venue (%d records)...", len(self.venues))
        df_venues = pd.DataFrame(list(self.venues.values()))  # noqa: F841
        conn.execute("CREATE TABLE dim_venue AS SELECT * FROM df_venues")

        logger.info("Loading dim_player (%d records)...", len(self.players))
        df_players = pd.DataFrame(list(self.players.values()))  # noqa: F841
        conn.execute("CREATE TABLE dim_player AS SELECT * FROM df_players")

        logger.info("Loading dim_player_name_history (%d records)...", len(self.player_names))
        df_player_names = pd.DataFrame(self.player_names)  # noqa: F841
        conn.execute("CREATE TABLE dim_player_name_history AS SELECT * FROM df_player_names")

        logger.info("Loading dim_match (%d records)...", len(self.matches))
        df_matches = pd.DataFrame(self.matches)  # noqa: F841
        conn.execute("CREATE TABLE dim_match AS SELECT * FROM df_matches")

        logger.info("Loading fact_powerplay (%d records)...", len(self.powerplays))
        df_powerplays = pd.DataFrame(self.powerplays)  # noqa: F841
        conn.execute("CREATE TABLE fact_powerplay AS SELECT * FROM df_powerplays")

        logger.info("Loading fact_ball (%d records)...", len(self.balls))
        df_balls = pd.DataFrame(self.balls)  # noqa: F841
        conn.execute("CREATE TABLE fact_ball AS SELECT * FROM df_balls")

        logger.info(
            "Loading fact_player_match_performance (%d records)...", len(self.player_match_perf)
        )
        df_perf = pd.DataFrame(self.player_match_perf)  # noqa: F841
        conn.execute("CREATE TABLE fact_player_match_performance AS SELECT * FROM df_perf")

        # Create indexes for common queries
        logger.info("Creating indexes...")
        conn.execute("CREATE INDEX idx_ball_match ON fact_ball(match_id)")
        conn.execute("CREATE INDEX idx_ball_batter ON fact_ball(batter_id)")
        conn.execute("CREATE INDEX idx_ball_bowler ON fact_ball(bowler_id)")
        conn.execute("CREATE INDEX idx_match_tournament ON dim_match(tournament_id)")
        conn.execute("CREATE INDEX idx_match_date ON dim_match(match_date)")

        conn.close()
        db_size_mb = DB_PATH.stat().st_size / 1024 / 1024
        logger.info("Database size: %.1f MB", db_size_mb)

    def generate_manifest(self) -> None:
        """Generate ingestion manifest."""
        logger.info("Generating ingestion manifest...")
        manifest = {
            "data_version": DATA_VERSION,
            "ingested_at": datetime.now().isoformat(),
            "stats": {
                "zip_files_processed": self.stats["zip_files"],
                "matches_processed": self.stats["matches_processed"],
                "balls_processed": self.stats["balls_processed"],
                "players_found": self.stats["players_found"],
                "teams_found": len(self.teams),
                "venues_found": len(self.venues),
                "tournaments_found": len(self.tournaments),
            },
            "errors": self.stats["errors"][:20],  # First 20 errors only
        }

        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info("Manifest saved: %s", MANIFEST_PATH)

    def generate_schema_doc(self) -> None:
        """Generate schema documentation."""
        doc = """# Cricket Playbook Schema

## Overview

This database contains ball-by-ball T20 cricket data from Cricsheet.

## Tables

### Dimension Tables

#### dim_tournament
| Column | Type | Description |
|--------|------|-------------|
| tournament_id | VARCHAR | Primary key |
| tournament_name | VARCHAR | Full name |
| country | VARCHAR | Primary country |
| format | VARCHAR | T20, Hundred |
| gender | VARCHAR | male/female |

#### dim_team
| Column | Type | Description |
|--------|------|-------------|
| team_id | VARCHAR | Primary key (hash) |
| team_name | VARCHAR | Full name |
| short_name | VARCHAR | Abbreviation |

#### dim_venue
| Column | Type | Description |
|--------|------|-------------|
| venue_id | VARCHAR | Primary key (hash) |
| venue_name | VARCHAR | Stadium name |
| city | VARCHAR | City |

#### dim_player
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | Primary key (Cricsheet ID) |
| current_name | VARCHAR | Latest known name |
| first_seen_date | DATE | First appearance |
| last_seen_date | DATE | Last appearance |
| matches_played | INT | Total matches |
| primary_role | VARCHAR | Batter/Bowler/All-rounder |

#### dim_player_name_history
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | FK to dim_player |
| player_name | VARCHAR | Name used |
| valid_from | DATE | First seen |
| valid_to | DATE | Last seen (NULL if current) |
| source_file | VARCHAR | Source |

#### dim_match
| Column | Type | Description |
|--------|------|-------------|
| match_id | VARCHAR | Primary key (Cricsheet ID) |
| tournament_id | VARCHAR | FK to dim_tournament |
| match_number | INT | Match # in tournament |
| stage | VARCHAR | Group/Final/etc |
| season | VARCHAR | Season |
| match_date | DATE | Date played |
| venue_id | VARCHAR | FK to dim_venue |
| team1_id | VARCHAR | FK to dim_team |
| team2_id | VARCHAR | FK to dim_team |
| toss_winner_id | VARCHAR | FK to dim_team |
| toss_decision | VARCHAR | bat/field |
| winner_id | VARCHAR | FK to dim_team |
| outcome_type | VARCHAR | runs/wickets/tie |
| outcome_margin | INT | Margin |
| player_of_match_id | VARCHAR | FK to dim_player |
| balls_per_over | INT | Usually 6 |

### Fact Tables

#### fact_ball
| Column | Type | Description |
|--------|------|-------------|
| ball_id | VARCHAR | Primary key |
| match_id | VARCHAR | FK to dim_match |
| innings | INT | 1 or 2 |
| over | INT | 0-19 |
| ball | INT | Ball in over |
| ball_seq | INT | Sequential # |
| batting_team_id | VARCHAR | FK to dim_team |
| bowling_team_id | VARCHAR | FK to dim_team |
| batter_id | VARCHAR | FK to dim_player |
| bowler_id | VARCHAR | FK to dim_player |
| non_striker_id | VARCHAR | FK to dim_player |
| batter_runs | INT | Runs by batter |
| extra_runs | INT | Extra runs |
| total_runs | INT | Total |
| extra_type | VARCHAR | wides/noballs/byes/legbyes |
| is_wicket | BOOLEAN | Wicket fell |
| wicket_type | VARCHAR | caught/bowled/etc |
| player_out_id | VARCHAR | FK to dim_player |
| fielder_id | VARCHAR | FK to dim_player |
| is_legal_ball | BOOLEAN | Not wide/noball |

#### fact_powerplay
| Column | Type | Description |
|--------|------|-------------|
| powerplay_id | VARCHAR | Primary key |
| match_id | VARCHAR | FK to dim_match |
| innings | INT | 1 or 2 |
| powerplay_seq | INT | Sequence |
| powerplay_type | VARCHAR | mandatory/batting/bowling |
| from_over | DECIMAL | Start |
| to_over | DECIMAL | End |

#### fact_player_match_performance
| Column | Type | Description |
|--------|------|-------------|
| player_id | VARCHAR | FK to dim_player |
| match_id | VARCHAR | FK to dim_match |
| team_id | VARCHAR | FK to dim_team |
| batting_position | INT | 1-11 |
| did_bat | BOOLEAN | Batted |
| did_bowl | BOOLEAN | Bowled |
| did_keep_wicket | BOOLEAN | Kept wicket |

## Generated
"""
        doc += f"\nGenerated: {datetime.now().isoformat()}\n"
        doc += f"Data Version: {DATA_VERSION}\n"

        SCHEMA_DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SCHEMA_DOC_PATH, "w") as f:
            f.write(doc)

        print(f"Schema doc saved: {SCHEMA_DOC_PATH}")

    def run(self) -> None:
        """Run the full ingestion pipeline."""
        logger.info("=" * 60)
        logger.info("Cricket Playbook - Data Ingestion Pipeline")
        logger.info("=" * 60)

        # Find all zip files
        zip_files = sorted(RAW_DIR.glob("*.zip"))
        zip_files = [z for z in zip_files if z.stem != "cricket_playbook_files"]

        logger.info("Found %d zip files to process", len(zip_files))

        # Process each zip file
        for zip_path in zip_files:
            self.process_zip_file(zip_path)

        # Derive player roles
        logger.info("Deriving player roles...")
        self.derive_player_roles()

        # Load to DuckDB
        self.load_to_duckdb()

        # Generate artifacts
        self.generate_manifest()
        self.generate_schema_doc()

        # Log summary
        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info("Matches: %s", f"{self.stats['matches_processed']:,}")
        logger.info("Balls: %s", f"{self.stats['balls_processed']:,}")
        logger.info("Players: %s", f"{self.stats['players_found']:,}")
        logger.info("Wicketkeepers: %s", f"{self.stats.get('wicketkeepers_found', 0):,}")
        logger.info("Teams: %s", f"{len(self.teams):,}")
        logger.info("Venues: %s", f"{len(self.venues):,}")
        logger.info("Errors: %d", len(self.stats["errors"]))

        if self.stats["errors"]:
            logger.warning("First 5 errors:")
            for err in self.stats["errors"][:5]:
                logger.warning("  - %s", err)


if __name__ == "__main__":
    ingester = CricketIngester()
    ingester.run()
