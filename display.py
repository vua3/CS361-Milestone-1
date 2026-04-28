"""
display.py - Display helpers for UI
"""

import os

# ── Terminal width ──────────────────────────────────────
WIDTH = 60

# clear the terminal screen for an empty start
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def divider(char="─"):
    print(char * WIDTH)

#top header with name & page title
def header(title: str):
    divider("═")
    print(f"  museumlog  │  {title}")
    divider("═")


def section(title: str):
    print()
    divider()
    print(f"  {title}")
    divider()


def print_museum_card(index: int, museum, show_index: bool = True):
    """print a minimal info for list views"""
    status_icon = "♥" if museum.status == "visited" else "★"
    idx_str = f"[{index + 1}] " if show_index else "    "
    loc = museum.location if museum.location else "Location unknown"
    print(f"  {idx_str}{status_icon}  {museum.name}")
    print(f"       📍 {loc}")


def print_museum_detail(museum, index: int = None):
    """print full detail view"""
    label = f"  [{index + 1}]  " if index is not None else "  "
    divider()
    print(f"{label}{museum.name.upper()}")
    divider()
    print(f"  Status  : {'✔ Visited' if museum.status == 'visited' else '★ Wishlist'}")
    print(f"  Location: {museum.location or '—'}")
    if museum.ticket_cost:
        print(f"  Ticket  : {museum.ticket_cost}")
    if museum.museum_type:
        print(f"  Type    : {museum.museum_type}")
    if museum.num_exhibits:
        print(f"  Exhibits: {museum.num_exhibits}")
    if museum.notes:
        print(f"  Notes   : {museum.notes}")


def nav_bar(options: list[tuple[str, str]]):
    """
    consistent nav bar with keyboard shortcuts and clear labels
    """
    print()
    for key, label in options:
        print(f"  [{key}] {label}")
    print()


def prompt(message: str) -> str:
    """input prompt for user input"""
    return input(f"\n  → {message}: ").strip()


def success(message: str):
    print(f"\n  ✔  {message}")


def warning(message: str):
    print(f"\n  ⚠  {message}")


def error(message: str):
    print(f"\n  ✖  {message}")


def pause():
    input("\n  Press Enter to continue...")
