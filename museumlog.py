"""
museumlog.py - Main Program for CS361 Milestone #1
A CLI app to track museums you've visited and museums you want to visit.
"""

import sys 
from typing import List, Optional
import data
import display
from dataclasses import dataclass, field
from typing import Optional

#  Museum data model

@dataclass
class Museum:
    name: str
    location: str
    status: str          # "visited" or "wishlist"
    ticket_cost: str = ""
    museum_type: str = ""
    num_exhibits: str = ""
    notes: str = ""

    def to_dict(self) -> dict: # convert museum to dict for JSON
        return {
            "name": self.name,
            "location": self.location,
            "status": self.status,
            "ticket_cost": self.ticket_cost,
            "museum_type": self.museum_type,
            "num_exhibits": self.num_exhibits,
            "notes": self.notes,
        }

    @staticmethod  # method to create a museum from a dict, with defaults for missing fields
    def from_dict(d: dict) -> "Museum":
        return Museum(
            name=d.get("name", ""),
            location=d.get("location", ""),
            status=d.get("status", "visited"),
            ticket_cost=d.get("ticket_cost", ""),
            museum_type=d.get("museum_type", ""),
            num_exhibits=d.get("num_exhibits", ""),
            notes=d.get("notes", ""),
        )


#  Museum Database for auto-populate

AUTO_POPULATE_DB = {
    "metropolitan museum of art": {
        "name": "The Metropolitan Museum of Art",
        "location": "New York City, New York",
        "ticket_cost": "$30",
        "museum_type": "Art",
        "num_exhibits": "~30 permanent galleries",
    },
    "american museum of natural history": {
        "name": "American Museum of Natural History",
        "location": "New York City, New York",
        "ticket_cost": "$28",
        "museum_type": "Natural History",
        "num_exhibits": "~45 permanent halls",
    },
    "louvre": {
        "name": "Louvre Museum",
        "location": "Paris, France",
        "ticket_cost": "€22",
        "museum_type": "Art / History",
        "num_exhibits": "~35,000 works on display",
    },
    "moma": {
        "name": "Museum of Modern Art (MoMA)",
        "location": "New York City, New York",
        "ticket_cost": "$30",
        "museum_type": "Modern Art",
        "num_exhibits": "~200,000 works in collection",
    },
    "california science center": {
        "name": "California Science Center",
        "location": "Los Angeles, California",
        "ticket_cost": "Free",
        "museum_type": "Science",
        "num_exhibits": "Multiple permanent exhibits",
    },
    "getty center": {
        "name": "The Getty Center",
        "location": "Los Angeles, California",
        "ticket_cost": "Free (parking $20)",
        "museum_type": "Art",
        "num_exhibits": "Multiple permanent collections",
    },
}


def _auto_populate_lookup(search_term: str) -> Optional[dict]:
    """
    look up the search term setting to lower in the auto-populate database and return the info if found. 
    """
    term = search_term.lower().strip()
    for key, info in AUTO_POPULATE_DB.items():
        if term in key or key in term:
            return info
    return None


#  HOME SCREEN

def screen_home():
    """
    home screen with benefits explanation and clear nav
    """
    display.clear()
    display.header("HOME")

    print("""
  Welcome to museumlog!

  museumlog lets you:
    ♥  Keep a record of every museum you've visited
    ★  Build a wish-list of museums you want to explore
    ✎  Store ratings, notes, ticket cost, and more
    ⊞  View and sort your full collection any time

  Your data is saved automatically — it will be here
  every time you open the app.
""")

    visited = data.get_visited()
    wishlist = data.get_wishlist()
    print(f"  Your collection: {len(visited)} visited  |  {len(wishlist)} on wishlist")

    display.nav_bar([
        ("1", "My Museums (all)"),
        ("2", "Wishlist"),
        ("3", "Add a Museum"),
        ("H", "Help"),
        ("Q", "Quit"),
    ])

    choice = display.prompt("Choose an option").upper()
    return choice


#  MY MUSEUMS (all)

def screen_my_museums():
    """
    show all museums
    """
    while True:
        display.clear()
        display.header("MY MUSEUMS")
        print("  See all your favorite visited or wishlist museums in one place.")
        print()

        museums = data.load_museums()

        if not museums:
            print("  You haven't added any museums yet.")
            print("  Go to [A]dd a Museum to get started!")
        else:
            visited = [m for m in museums if m.status == "visited"]
            wishlist = [m for m in museums if m.status == "wishlist"]

            if visited:
                display.section("VISITED  ♥")
                for i, m in enumerate(museums):
                    if m.status == "visited":
                        display.print_museum_card(museums.index(m), m)

            if wishlist:
                display.section("WISHLIST  ★")
                for i, m in enumerate(museums):
                    if m.status == "wishlist":
                        display.print_museum_card(museums.index(m), m)

            print()
            print("  Enter a number to view full details, or use the menu below.")

        display.nav_bar([
            ("A", "Add a Museum"),
            ("S", "Sort by name"),
            ("B", "Back to Home"),
        ])
        if museums:
            print("  Or enter a museum number [1-{}] to view details.".format(len(museums)))
            print()

        choice = display.prompt("Choose an option").upper()

        if choice == "B":
            return
        elif choice == "A":
            screen_add_museum()
        elif choice == "S":
            museums.sort(key=lambda m: m.name.lower())
            data.save_museums(museums)
            display.success("Museums sorted alphabetically!")
            display.pause()
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(museums):
                screen_view_museum(idx)
            else:
                display.error("Invalid number. Please try again.")
                display.pause()
        else:
            display.error("Unrecognized option. Please try again.")
            display.pause()


#  VIEW A SINGLE MUSEUM SCREEN

def screen_view_museum(index: int):
    """
    edit or delete the museum
    """
    while True:
        display.clear()
        display.header("VIEW MUSEUM")

        museums = data.load_museums()
        if index >= len(museums):
            display.error("Museum no longer exists.")
            display.pause()
            return

        museum = museums[index]
        display.print_museum_detail(museum, index)

        display.nav_bar([
            ("E", "Edit this museum"),
            ("D", "Delete this museum"),
            ("B", "Back"),
        ])

        choice = display.prompt("Choose an option").upper()

        if choice == "B":
            return
        elif choice == "E":
            screen_edit_museum(index)
            return
        elif choice == "D":
            _delete_with_confirmation(index)
            return
        else:
            display.error("Unrecognized option.")
            display.pause()


def _delete_with_confirmation(index: int): 
    """
    delete a museum with a clear warning about data loss and a confirmation step
    """
    museums = data.load_museums()
    if index >= len(museums):
        return

    museum = museums[index]
    display.clear()
    display.header("DELETE MUSEUM")
    print(f"""
  Are you sure you want to delete:

    "{museum.name}"

  ** WARNING: Removing a museum permanently deletes all of
     its data — location, notes, ticket cost, etc.
     You will need to re-enter everything if you change
     your mind.

  This action CANNOT be undone.
""")

    display.nav_bar([
        ("Y", "Yes, delete permanently"),
        ("N", "No, keep this museum (go back)"),
    ])

    choice = display.prompt("Delete? [Y / N]").upper()
    if choice == "Y":
        removed = data.delete_museum(index)
        if removed:
            display.success(f'"{removed.name}" has been removed from your museumlog.')
        display.pause()
    else:
        display.success("Deletion cancelled. No data lost!")
        display.pause()


#  EDIT A MUSEUM SCREEN

def screen_edit_museum(index: int):
    """allow the user to correct any field. pressing Enter keeps the old value."""
    display.clear()
    display.header("EDIT MUSEUM")

    museums = data.load_museums()
    if index >= len(museums):
        display.error("Museum not found.")
        display.pause()
        return

    m = museums[index]
    print(f"\n  Editing: {m.name}")
    print("  (Press Enter to keep the current value)\n")

    def ask(label, current):
        val = display.prompt(f"{label} [{current}]")
        return val if val else current

    m.name = ask("Name", m.name)
    m.location = ask("Location", m.location)

    print(f"\n  Current status: {'Visited ♥' if m.status == 'visited' else 'Wishlist ★'}")
    status_in = display.prompt("Change status? [V=Visited / W=Wishlist / Enter=keep]").upper()
    if status_in == "V":
        m.status = "visited"
    elif status_in == "W":
        m.status = "wishlist"

    m.ticket_cost = ask("Ticket cost", m.ticket_cost)
    m.museum_type = ask("Type", m.museum_type)
    m.num_exhibits = ask("Number of exhibits", m.num_exhibits)

    m.notes = ask("Notes", m.notes)

    data.update_museum(index, m)
    display.success(f'"{m.name}" has been updated.')
    display.pause()


#  WISHLIST SCREEN

def screen_wishlist():
    """view for wishlist museums only, with options to view details or add new ones directly to wishlist"""
    while True:
        display.clear()
        display.header("WISH LIST  ★")
        print("  See all your wishlist museums in one place.")
        print()

        museums = data.load_museums()
        wishlist_indices = [i for i, m in enumerate(museums) if m.status == "wishlist"]

        if not wishlist_indices:
            print("  Your wishlist is empty.")
            print("  Add a museum and mark it as 'Wishlist' to see it here.")
        else:
            for i in wishlist_indices:
                display.print_museum_card(i, museums[i])
            print()
            print("  Enter a number to view details.")

        display.nav_bar([
            ("A", "Add to Wishlist"),
            ("B", "Back to Home"),
        ])
        if wishlist_indices:
            print("  Or enter a museum number [1-{}] for full details.".format(len(museums)))
            print()

        choice = display.prompt("Choose an option").upper()

        if choice == "B":
            return
        elif choice == "A":
            screen_add_museum(default_status="wishlist")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(museums):
                screen_view_museum(idx)
            else:
                display.error("Invalid number.")
                display.pause()
        else:
            display.error("Unrecognized option.")
            display.pause()


#  ADD MUSEUM

def screen_add_museum(default_status: str = "visited"):
    """
    add a museum with two approaches with either auto-populate or manual entry
    """
    display.clear()
    display.header("ADD MUSEUM")

    print("""
  There are two ways to add a museum:

    [1] Auto-populate  —  type the museum name and we'll
                          try to fill in the details for you.

    [2] Manual Entry   —  fill in each field yourself.

    [B] Back
""")

    mode = display.prompt("Choose a method [1 / 2 / B]").upper()
    if mode == "B":
        return
    elif mode == "1":
        _add_auto_populate(default_status)
    elif mode == "2":
        _add_manual(default_status)
    else:
        display.error("Invalid choice.")
        display.pause()
        screen_add_museum(default_status)


def _add_auto_populate(default_status: str):
    """
    auto-populate approach. Required field name (if found in DB)
    """
    display.clear()
    display.header("ADD MUSEUM — Auto-Populate")
    print("\n  ** Correctly spelled Museum Name is required to auto-populate.\n")

    name = display.prompt("Museum name (required)")
    if not name:
        display.error("Name is required.")
        display.pause()
        return

    # check to find a match in the auto-populate database
    match = _auto_populate_lookup(name)

    if match:
        display.success(f"Found: {match['name']}  — details auto-filled!")
        print()
        m = Museum(
            name=match["name"],
            location=match["location"],
            status=default_status,
            ticket_cost=match.get("ticket_cost", ""),
            museum_type=match.get("museum_type", ""),
            num_exhibits=match.get("num_exhibits", ""),
        )
        
        # show user what was found
        display.print_museum_detail(m)
        print()
        print("  You can accept these details or override any field.")
        print("  Press Enter at any prompt to keep the auto-filled value.\n")

        m.name = display.prompt(f"Name [{m.name}]") or m.name
        m.location = display.prompt(f"Location [{m.location}]") or m.location
        m.ticket_cost = display.prompt(f"Ticket cost [{m.ticket_cost}]") or m.ticket_cost
        m.museum_type = display.prompt(f"Type [{m.museum_type}]") or m.museum_type
        m.num_exhibits = display.prompt(f"Exhibits [{m.num_exhibits}]") or m.num_exhibits
    else:
        display.warning(f'No auto-populate match found for "{name}".')
        print("  You can still add it manually, or switch to Manual Entry.")
        print()
        fallback = display.prompt("Switch to Manual Entry? [Y / N]").upper()
        if fallback == "Y":
            _add_manual(default_status)
            return
        
        # 
        m = Museum(name=name, location="", status=default_status)
        m.location = display.prompt("Location (required)")
        if not m.location:
            display.error("Location is required. Museum not saved.")
            display.pause()
            return
        m.ticket_cost = display.prompt("Ticket cost (optional, press Enter to skip)") or ""
        m.museum_type = display.prompt("Type (optional)") or ""
        m.num_exhibits = display.prompt("Number of exhibits (optional)") or ""

    m = _collect_status_and_notes(m, default_status)
    if m:
        _confirm_and_save(m)


def _add_manual(default_status: str):
    """
    manual entry approach. Required fields: name + location
    """
    display.clear()
    display.header("ADD MUSEUM — Manual Entry")
    print("\n  ** Name and Location are required to add a museum.\n")

    name = display.prompt("Museum name (required)")
    if not name:
        display.error("Name is required.")
        display.pause()
        return

    location = display.prompt("Location (required, e.g. 'New York City, NY')")
    if not location:
        display.error("Location is required.")
        display.pause()
        return

    ticket_cost = display.prompt("Ticket cost (optional, press Enter to skip)") or ""
    museum_type = display.prompt("Type (e.g. Art, History, Science — optional)") or ""
    num_exhibits = display.prompt("Number of exhibits (optional)") or ""

    m = Museum(
        name=name,
        location=location,
        status=default_status,
        ticket_cost=ticket_cost,
        museum_type=museum_type,
        num_exhibits=num_exhibits,
    )

    m = _collect_status_and_notes(m, default_status)
    if m:
        _confirm_and_save(m)


def _collect_status_and_notes(museum: Museum, default_status: str) -> Optional[Museum]:
    """collect status (visited/wishlist), rating, notes"""
    print()
    display.divider()
    print("  STEP 3 of 3 — Status & Notes")
    display.divider()

    # status: visited or wishlist
    print(f"\n  Add to which list?")
    print(f"    [V] Visited  ♥")
    print(f"    [W] Wishlist ★")
    status_in = display.prompt("Choose [V / W]").upper()
    if status_in == "W":
        museum.status = "wishlist"
    elif status_in == "V":
        museum.status = "visited"
    else:
        museum.status = default_status

    # notes (optional)
    notes = display.prompt("Notes (optional — memorable moments, tips, etc.)")
    museum.notes = notes or ""

    return museum


def _confirm_and_save(museum: Museum):
    """show a summary and ask for final confirmation before saving"""
    display.clear()
    display.header("CONFIRM ADD MUSEUM")
    display.print_museum_detail(museum)
    print()
    confirm = display.prompt("Save this museum? [Y / N]").upper()
    if confirm == "Y":
        data.add_museum(museum)
        display.success(f'"{museum.name}" has been added to your museumlog!')
    else:
        display.warning("Museum not saved. Returning to menu.")
    display.pause()


#  HELP PAGE 

def screen_help():
    """
    help screen with clear steps for how to accomplish different tasks
    """
    display.clear()
    display.header("HELP")
    print("""
  Here are steps to help you navigate museumlog!
  ══════════════════════════════════════════════

  HOW TO ADD A MUSEUM
  ────────────────────
  Step 1: From the Home screen, choose [3] Add a Museum.
  Step 2: Choose Auto-populate [1] or Manual Entry [2].
          • Auto-populate: type the museum name and the app
            will try to fill in the details automatically.
            If it can't find a match, you'll be offered
            Manual Entry as a fallback.
          • Manual Entry: fill in each field yourself.
  Step 3: Choose Visited ♥ or Wishlist ★, add optional
          notes/rating, then confirm with [Y].

  HOW TO VIEW YOUR MUSEUMS
  ────────────────────────
  • From Home, choose [1] My Museums to see all museums.
  • Or choose [2] Wishlist to see only wishlist museums.
  • Type a museum's number to see its full details.

  HOW TO EDIT A MUSEUM
  ────────────────────
  • Open a museum's detail view (choose its number).
  • Choose [E] Edit.
  • Press Enter at any field to keep the current value.

  HOW TO DELETE A MUSEUM
  ──────────────────────
  • Open a museum's detail view (choose its number).
  • Choose [D] Delete.
  • ⚠  You will see a warning about data loss.
  • Type [Y] to confirm deletion, [N] to cancel safely.

  HOW TO MOVE A WISHLIST MUSEUM TO VISITED
  ─────────────────────────────────────────
  • Open the museum's detail view.
  • Choose [E] Edit.
  • Change the status from Wishlist to Visited.

  NEED MORE HELP?
  ───────────────
  Contact: help@museumlog.com
""")

    display.nav_bar([("B", "Back to Home")])
    display.prompt("Press Enter or [B] to go back")


#  MAIN LOOP

def main():
    while True:
        choice = screen_home()

        if choice == "1":
            screen_my_museums()
        elif choice == "2":
            screen_wishlist()
        elif choice == "3":
            screen_add_museum()
        elif choice == "H":
            screen_help()
        elif choice == "Q":
            display.clear()
            print("\n  Thanks for using museumlog!\n")
            sys.exit(0)
        else:
            display.error("Unrecognized option. Please try again.")
            display.pause()


if __name__ == "__main__":
    main()
