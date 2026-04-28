"""
data.py - saves user added museums to museums.json
"""

import json
import os
from typing import List, Optional
from museumlog import Museum

DATA_FILE = "museums.json"


def load_museums() -> List[Museum]:
    """load all museums from the JSON data file
        return empty list if file doesn't exist or is corrupted
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Museum.from_dict(d) for d in raw]
    except (json.JSONDecodeError, KeyError):
        # corrupted file — return empty list so it still runs
        return []


def save_museums(museums: List[Museum]) -> None:
    """persist the full museum list to the JSON data file"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([m.to_dict() for m in museums], f, indent=2)


def add_museum(museum: Museum) -> List[Museum]:
    """add a museum and save. returns updated list"""
    museums = load_museums()
    museums.append(museum)
    save_museums(museums)
    return museums


def delete_museum(index: int) -> Optional[Museum]:
    """
    delete museum at the given index (0-based)
    returns the deleted museum, or None if index was invalid
    """
    museums = load_museums()
    if 0 <= index < len(museums):
        removed = museums.pop(index)
        save_museums(museums)
        return removed
    return None


def update_museum(index: int, updated: Museum) -> bool:
    """replace the museum at index with an updated version"""
    museums = load_museums()
    if 0 <= index < len(museums):
        museums[index] = updated
        save_museums(museums)
        return True
    return False


def get_visited() -> List[Museum]:
    return [m for m in load_museums() if m.status == "visited"]


def get_wishlist() -> List[Museum]:
    return [m for m in load_museums() if m.status == "wishlist"]
