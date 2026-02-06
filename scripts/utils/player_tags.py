#!/usr/bin/env python3
"""
Cricket Playbook - Player Tags Utility Module
Author: Brock Purdy (Data Engineer)
Sprint: Optimization Audit TKT-097

Consolidates player_tags.json update logic into a single source of truth.
Previously, the same 50+ line function was duplicated in 3 files:
- batter_bowling_type_matchup.py
- bowler_handedness_matchup.py
- bowler_phase_tags.py

This module provides:
- load_player_tags(): Load existing tags from JSON
- remove_tags_by_category(tags, category): Remove old tags by prefix/category
- add_tags(tags, new_tags): Add new tags to player entries
- save_player_tags(tags): Save with proper formatting (2-space indent)
- update_player_tags(category, new_tags, player_type): Main function combining all steps
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

from .constants import OUTPUT_DIR


# Path to the player_tags.json file
PLAYER_TAGS_PATH = OUTPUT_DIR / "tags" / "player_tags.json"

# Tag categories and their associated tags
# Used for removing old tags before adding new ones
TAG_CATEGORIES: Dict[str, Set[str]] = {
    "bowling_type": {
        "SPECIALIST_VS_PACE",
        "SPECIALIST_VS_SPIN",
        "VULNERABLE_VS_PACE",
        "VULNERABLE_VS_SPIN",
        "SPECIALIST_VS_OFF_SPIN",
        "SPECIALIST_VS_LEG_SPIN",
        "SPECIALIST_VS_LEFT_ARM_SPIN",
        "SPECIALIST_VS_LEFT_ARM_WRIST_SPIN",
        "VULNERABLE_VS_OFF_SPIN",
        "VULNERABLE_VS_LEG_SPIN",
        "VULNERABLE_VS_LEFT_ARM_SPIN",
        "VULNERABLE_VS_LEFT_ARM_WRIST_SPIN",
    },
    "handedness": {
        "LHB_SPECIALIST",
        "RHB_SPECIALIST",
        "LHB_VULNERABLE",
        "RHB_VULNERABLE",
        "LHB_PRESSURE",
        "RHB_PRESSURE",
        "LHB_WICKET_TAKER",
        "RHB_WICKET_TAKER",
    },
    "phase": {
        "PP_BEAST",
        "PP_LIABILITY",
        "MIDDLE_OVERS_BEAST",
        "MIDDLE_OVERS_LIABILITY",
        "DEATH_BEAST",
        "DEATH_LIABILITY",
    },
}


def load_player_tags(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load existing player tags from JSON file.

    Args:
        path: Optional path to tags file. Defaults to PLAYER_TAGS_PATH.

    Returns:
        Dictionary with "batters" and "bowlers" lists.
    """
    tags_path = path or PLAYER_TAGS_PATH

    if tags_path.exists():
        with open(tags_path) as f:
            return json.load(f)
    else:
        return {"batters": [], "bowlers": []}


def remove_tags_by_category(existing_tags: Set[str], category: str) -> Set[str]:
    """Remove tags belonging to a specific category.

    Args:
        existing_tags: Set of existing player tags.
        category: Category name (e.g., "bowling_type", "handedness", "phase").

    Returns:
        Set with category tags removed.
    """
    if category not in TAG_CATEGORIES:
        raise ValueError(
            f"Unknown category: {category}. Valid categories: {list(TAG_CATEGORIES.keys())}"
        )

    return existing_tags - TAG_CATEGORIES[category]


def add_tags(existing_tags: Set[str], new_tags: Set[str]) -> Set[str]:
    """Add new tags to existing tag set.

    Args:
        existing_tags: Set of existing player tags.
        new_tags: Set of new tags to add.

    Returns:
        Combined set of tags.
    """
    return existing_tags.union(new_tags)


def save_player_tags(tags_data: Dict[str, Any], path: Optional[Path] = None) -> None:
    """Save player tags to JSON file with proper formatting.

    Args:
        tags_data: Dictionary with "batters" and "bowlers" lists.
        path: Optional path to save to. Defaults to PLAYER_TAGS_PATH.
    """
    tags_path = path or PLAYER_TAGS_PATH

    # Ensure parent directory exists
    tags_path.parent.mkdir(parents=True, exist_ok=True)

    with open(tags_path, "w") as f:
        json.dump(tags_data, f, indent=2)


def update_player_tags(
    category: str,
    new_tags_lookup: Dict[str, List[str]],
    player_type: str = "batters",
    path: Optional[Path] = None,
) -> int:
    """Update player_tags.json with new tags for a specific category.

    This is the main function that combines all steps:
    1. Load existing tags
    2. Remove old tags from the specified category
    3. Add new tags
    4. Save with proper formatting

    Args:
        category: Tag category (e.g., "bowling_type", "handedness", "phase").
        new_tags_lookup: Dictionary mapping player_id to list of new tags.
        player_type: Either "batters" or "bowlers".
        path: Optional path to tags file. Defaults to PLAYER_TAGS_PATH.

    Returns:
        Number of players updated.

    Raises:
        ValueError: If category or player_type is invalid.
    """
    if category not in TAG_CATEGORIES:
        raise ValueError(
            f"Unknown category: {category}. Valid categories: {list(TAG_CATEGORIES.keys())}"
        )

    if player_type not in ("batters", "bowlers"):
        raise ValueError(f"Invalid player_type: {player_type}. Must be 'batters' or 'bowlers'.")

    # Load existing tags
    tags_data = load_player_tags(path)

    # Update player tags
    updated_count = 0
    for player in tags_data.get(player_type, []):
        player_id = player.get("player_id")
        if player_id in new_tags_lookup:
            # Get existing tags as a set
            existing_tags = set(player.get("tags", []))

            # Remove old category tags
            existing_tags = remove_tags_by_category(existing_tags, category)

            # Add new tags
            new_tags = set(new_tags_lookup[player_id])
            existing_tags = add_tags(existing_tags, new_tags)

            # Update player's tags (convert back to list)
            player["tags"] = list(existing_tags)
            updated_count += 1

    # Save updated tags
    save_player_tags(tags_data, path)

    return updated_count
