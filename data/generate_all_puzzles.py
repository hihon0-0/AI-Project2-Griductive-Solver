"""Generates, verifies with DPLL, and saves all 6 standardized Griductive puzzles.
Author: Member 3 (Game Engine & Data Lead)
"""
import os
import sys
import json
import jsonschema

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.dpll_verifier import verify_puzzle_with_dpll
from Source.engine.puzzle_io import save_puzzle, load_puzzle

def get_puzzle_3x3_01() -> dict:
    return {
        "puzzle_id": "puzzle_3x3_01",
        "name": "The Town Hall Mystery",
        "size": 3,
        "initial_revealed": ["A1"],
        "grid": [
            {
                "id": "A1", "row": 1, "col": "A",
                "character": {"name": "Abel", "occupation": "Baker"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A1", "type": "SAME",
                    "params": {"target1": "A1", "target2": "B1"},
                    "description": "Abel and Bea have the same status."
                }
            },
            {
                "id": "B1", "row": 1, "col": "B",
                "character": {"name": "Bea", "occupation": "Cook"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
                    "description": "Exactly 1 person in Row 1 is a Criminal."
                }
            },
            {
                "id": "C1", "row": 1, "col": "C",
                "character": {"name": "Clara", "occupation": "Guard"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C1", "type": "SAME",
                    "params": {"target1": "C1", "target2": "C2"},
                    "description": "Clara and Franz have the same status."
                }
            },
            {
                "id": "A2", "row": 2, "col": "A",
                "character": {"name": "David", "occupation": "Detective"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A2", "type": "AT_MOST",
                    "params": {"count": 1, "region": {"type": "EXPLICIT", "cells": ["A2", "A3"]}},
                    "description": "At most 1 person among David and Grant is a Criminal."
                }
            },
            {
                "id": "B2", "row": 2, "col": "B",
                "character": {"name": "Eliza", "occupation": "Judge"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B2", "type": "PARITY",
                    "params": {"parity": "EVEN", "region": {"type": "ROW", "row": 2}},
                    "description": "An even number of people in Row 2 are Criminals."
                }
            },
            {
                "id": "C2", "row": 2, "col": "C",
                "character": {"name": "Franz", "occupation": "Clerk"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C2", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "C"}},
                    "description": "Exactly 2 people in Column C are Criminals."
                }
            },
            {
                "id": "A3", "row": 3, "col": "A",
                "character": {"name": "Grant", "occupation": "Artist"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A3", "type": "COUNT_COMPARE",
                    "params": {
                        "operator": "GT",
                        "region1": {"type": "COLUMN", "col": "A"},
                        "region2": {"type": "ROW", "row": 3}
                    },
                    "description": "Column A has more Criminals than Row 3."
                }
            },
            {
                "id": "B3", "row": 3, "col": "B",
                "character": {"name": "Hannah", "occupation": "Doctor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B3", "type": "EXACTLY",
                    "params": {"count": 0, "region": {"type": "ROW", "row": 3}},
                    "description": "Nobody in Row 3 is a Criminal."
                }
            },
            {
                "id": "C3", "row": 3, "col": "C",
                "character": {"name": "Ian", "occupation": "Sailor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C3", "type": "SAME",
                    "params": {"target1": "C3", "target2": "B2"},
                    "description": "Ian and Eliza have the same status."
                }
            }
        ]
    }

def get_puzzle_3x3_02() -> dict:
    return {
        "puzzle_id": "puzzle_3x3_02",
        "name": "The Market Heist",
        "size": 3,
        "initial_revealed": ["B1"],
        "grid": [
            {
                "id": "A1", "row": 1, "col": "A",
                "character": {"name": "Alice", "occupation": "Merchant"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A1", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "A"}},
                    "description": "Exactly 2 people in Column A are Criminals."
                }
            },
            {
                "id": "B1", "row": 1, "col": "B",
                "character": {"name": "Bob", "occupation": "Jeweler"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B1", "type": "DIFFERENT",
                    "params": {"target1": "B1", "target2": "B2"},
                    "description": "Bob and Edward have different statuses."
                }
            },
            {
                "id": "C1", "row": 1, "col": "C",
                "character": {"name": "Charles", "occupation": "Guard"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
                    "description": "Exactly 1 person in Row 1 is a Criminal."
                }
            },
            {
                "id": "A2", "row": 2, "col": "A",
                "character": {"name": "Diana", "occupation": "Detective"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A2", "type": "SAME",
                    "params": {"target1": "A2", "target2": "C1"},
                    "description": "Diana and Charles have the same status."
                }
            },
            {
                "id": "B2", "row": 2, "col": "B",
                "character": {"name": "Edward", "occupation": "Scholar"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_B2", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 2}},
                    "description": "Exactly 1 person in Row 2 is a Criminal."
                }
            },
            {
                "id": "C2", "row": 2, "col": "C",
                "character": {"name": "Fiona", "occupation": "Artist"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C2", "type": "AT_MOST",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "B"}},
                    "description": "Fiona's Sketch: At most 1 person in Column B is a Criminal. (Red Herring - Column B was already solved!)"
                }
            },
            {
                "id": "A3", "row": 3, "col": "A",
                "character": {"name": "George", "occupation": "Blacksmith"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A3", "type": "PARITY",
                    "params": {"parity": "EVEN", "region": {"type": "NEIGHBORS", "cell": "B2"}},
                    "description": "George's Clue: An even number of neighbors of Edward are Criminals."
                }
            },
            {
                "id": "B3", "row": 3, "col": "B",
                "character": {"name": "Helen", "occupation": "Tailor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B3", "type": "COUNT_COMPARE",
                    "params": {
                        "operator": "GT",
                        "region1": {"type": "COLUMN", "col": "A"},
                        "region2": {"type": "COLUMN", "col": "C"}
                    },
                    "description": "Helen's Ledger: Column A has more Criminals than Column C."
                }
            },
            {
                "id": "C3", "row": 3, "col": "C",
                "character": {"name": "Ian", "occupation": "Sailor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C3", "type": "DIFFERENT",
                    "params": {"target1": "C3", "target2": "B2"},
                    "description": "Ian whispers: Ian and Edward have different statuses."
                }
            }
        ]
    }

def get_puzzle_4x4_01() -> dict:
    return {
        "puzzle_id": "puzzle_4x4_01",
        "name": "The Royal Gala Intrigue",
        "size": 4,
        "initial_revealed": ["A1", "C2"],
        "grid": [
            # Row 1
            {
                "id": "A1", "row": 1, "col": "A",
                "character": {"name": "Abel", "occupation": "Ambassador"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A1", "type": "SAME",
                    "params": {"target1": "A1", "target2": "B1"},
                    "description": "Abel and Bea have the same status."
                }
            },
            {
                "id": "B1", "row": 1, "col": "B",
                "character": {"name": "Bea", "occupation": "Baroness"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B1", "type": "DIFFERENT",
                    "params": {"target1": "B1", "target2": "C1"},
                    "description": "Bea and Clara have different statuses."
                }
            },
            {
                "id": "C1", "row": 1, "col": "C",
                "character": {"name": "Clara", "occupation": "Countess"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
                    "description": "Exactly 1 person in Row 1 is a Criminal."
                }
            },
            {
                "id": "D1", "row": 1, "col": "D",
                "character": {"name": "Derek", "occupation": "Duke"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D1", "type": "SAME",
                    "params": {"target1": "D1", "target2": "A2"},
                    "description": "Derek and Eliza have the same status."
                }
            },
            # Row 2
            {
                "id": "A2", "row": 2, "col": "A",
                "character": {"name": "Eliza", "occupation": "Explorer"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A2", "type": "DIFFERENT",
                    "params": {"target1": "A2", "target2": "B2"},
                    "description": "Eliza and Franz have different statuses."
                }
            },
            {
                "id": "B2", "row": 2, "col": "B",
                "character": {"name": "Franz", "occupation": "Financier"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_B2", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "ROW", "row": 2}},
                    "description": "Exactly 2 people in Row 2 are Criminals."
                }
            },
            {
                "id": "C2", "row": 2, "col": "C",
                "character": {"name": "Grant", "occupation": "General"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C2", "type": "SAME",
                    "params": {"target1": "C2", "target2": "C3"},
                    "description": "Grant and Karl have the same status."
                }
            },
            {
                "id": "D2", "row": 2, "col": "D",
                "character": {"name": "Hannah", "occupation": "Historian"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_D2", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "D"}},
                    "description": "Exactly 1 person in Column D is a Criminal."
                }
            },
            # Row 3
            {
                "id": "A3", "row": 3, "col": "A",
                "character": {"name": "Ivy", "occupation": "Inspector"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A3", "type": "AT_MOST",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "A"}},
                    "description": "At most 1 person in Column A is a Criminal."
                }
            },
            {
                "id": "B3", "row": 3, "col": "B",
                "character": {"name": "Jonas", "occupation": "Judge"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B3", "type": "PARITY",
                    "params": {"parity": "ODD", "region": {"type": "ROW", "row": 4}},
                    "description": "An odd number of people in Row 4 are Criminals."
                }
            },
            {
                "id": "C3", "row": 3, "col": "C",
                "character": {"name": "Karl", "occupation": "Knight"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C3", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "C"}},
                    "description": "Exactly 1 person in Column C is a Criminal."
                }
            },
            {
                "id": "D3", "row": 3, "col": "D",
                "character": {"name": "Leo", "occupation": "Librarian"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D3", "type": "SAME",
                    "params": {"target1": "D3", "target2": "B3"},
                    "description": "Leo and Jonas have the same status."
                }
            },
            # Row 4
            {
                "id": "A4", "row": 4, "col": "A",
                "character": {"name": "Mara", "occupation": "Mayor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A4", "type": "DIFFERENT",
                    "params": {"target1": "A4", "target2": "B4"},
                    "description": "Mara and Noah have different statuses."
                }
            },
            {
                "id": "B4", "row": 4, "col": "B",
                "character": {"name": "Noah", "occupation": "Naval Officer"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_B4", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "B"}},
                    "description": "Exactly 2 people in Column B are Criminals."
                }
            },
            {
                "id": "C4", "row": 4, "col": "C",
                "character": {"name": "Owen", "occupation": "Officer"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C4", "type": "COUNT_COMPARE",
                    "params": {
                        "operator": "GT",
                        "region1": {"type": "COLUMN", "col": "B"},
                        "region2": {"type": "COLUMN", "col": "D"}
                    },
                    "description": "Column B has more Criminals than Column D."
                }
            },
            {
                "id": "D4", "row": 4, "col": "D",
                "character": {"name": "Priya", "occupation": "Physician"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D4", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 3}},
                    "description": "Exactly 1 person in Row 3 is a Criminal."
                }
            }
        ]
    }

def get_puzzle_4x4_02() -> dict:
    return {
        "puzzle_id": "puzzle_4x4_02",
        "name": "The Harbour Syndicate",
        "size": 4,
        "initial_revealed": ["A1", "D2"],
        "grid": [
            # Row 1
            {
                "id": "A1", "row": 1, "col": "A",
                "character": {"name": "Arthur", "occupation": "Admiral"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A1", "type": "SAME",
                    "params": {"target1": "A1", "target2": "A2"},
                    "description": "Arthur and Edwin have the same status."
                }
            },
            {
                "id": "B1", "row": 1, "col": "B",
                "character": {"name": "Beatrice", "occupation": "Boatswain"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_B1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
                    "description": "Exactly 1 person in Row 1 is a Criminal."
                }
            },
            {
                "id": "C1", "row": 1, "col": "C",
                "character": {"name": "Cedric", "occupation": "Captain"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C1", "type": "DIFFERENT",
                    "params": {"target1": "C1", "target2": "B1"},
                    "description": "Cedric and Beatrice have different statuses."
                }
            },
            {
                "id": "D1", "row": 1, "col": "D",
                "character": {"name": "Diana", "occupation": "Diver"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D1", "type": "SAME",
                    "params": {"target1": "D1", "target2": "C1"},
                    "description": "Diana and Cedric have the same status."
                }
            },
            # Row 2
            {
                "id": "A2", "row": 2, "col": "A",
                "character": {"name": "Edwin", "occupation": "Engineer"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A2", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 2}},
                    "description": "Exactly 1 person in Row 2 is a Criminal."
                }
            },
            {
                "id": "B2", "row": 2, "col": "B",
                "character": {"name": "Flora", "occupation": "Fisherman"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B2", "type": "SAME",
                    "params": {"target1": "B2", "target2": "B3"},
                    "description": "Flora and Julia have the same status."
                }
            },
            {
                "id": "C2", "row": 2, "col": "C",
                "character": {"name": "George", "occupation": "Guard"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C2", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "C"}},
                    "description": "Exactly 1 person in Column C is a Criminal."
                }
            },
            {
                "id": "D2", "row": 2, "col": "D",
                "character": {"name": "Hester", "occupation": "Harbourmaster"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D2", "type": "DIFFERENT",
                    "params": {"target1": "D2", "target2": "D3"},
                    "description": "Hester and Laura have different statuses."
                }
            },
            # Row 3
            {
                "id": "A3", "row": 3, "col": "A",
                "character": {"name": "Isaac", "occupation": "Inspector"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A3", "type": "COUNT_COMPARE",
                    "params": {
                        "operator": "GT",
                        "region1": {"type": "COLUMN", "col": "B"},
                        "region2": {"type": "COLUMN", "col": "A"}
                    },
                    "description": "Column B has more Criminals than Column A."
                }
            },
            {
                "id": "B3", "row": 3, "col": "B",
                "character": {"name": "Julia", "occupation": "Judge"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B3", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "ROW", "row": 3}},
                    "description": "Exactly 2 people in Row 3 are Criminals."
                }
            },
            {
                "id": "C3", "row": 3, "col": "C",
                "character": {"name": "Kenneth", "occupation": "Knight"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C3", "type": "SAME",
                    "params": {"target1": "C3", "target2": "C4"},
                    "description": "Kenneth and Oliver have the same status."
                }
            },
            {
                "id": "D3", "row": 3, "col": "D",
                "character": {"name": "Laura", "occupation": "Locksmith"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_D3", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "D"}},
                    "description": "Exactly 1 person in Column D is a Criminal."
                }
            },
            # Row 4
            {
                "id": "A4", "row": 4, "col": "A",
                "character": {"name": "Martin", "occupation": "Merchant"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A4", "type": "PARITY",
                    "params": {"parity": "EVEN", "region": {"type": "COLUMN", "col": "B"}},
                    "description": "An even number of people in Column B are Criminals."
                }
            },
            {
                "id": "B4", "row": 4, "col": "B",
                "character": {"name": "Nora", "occupation": "Navigator"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_B4", "type": "AT_LEAST",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 4}},
                    "description": "At least 1 person in Row 4 is a Criminal."
                }
            },
            {
                "id": "C4", "row": 4, "col": "C",
                "character": {"name": "Oliver", "occupation": "Officer"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C4", "type": "PARITY",
                    "params": {"parity": "ODD", "region": {"type": "ROW", "row": 4}},
                    "description": "An odd number of people in Row 4 are Criminals."
                }
            },
            {
                "id": "D4", "row": 4, "col": "D",
                "character": {"name": "Penelope", "occupation": "Pilot"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D4", "type": "SAME",
                    "params": {"target1": "D4", "target2": "B2"},
                    "description": "Penelope and Flora have the same status."
                }
            }
        ]
    }

def get_puzzle_5x5_01() -> dict:
    return {
        "puzzle_id": "puzzle_5x5_01",
        "name": "The Grand Academy Conspiracy",
        "size": 5,
        "initial_revealed": ["A1", "C3", "E5"],
        "grid": [
            # Row 1
            {
                "id": "A1", "row": 1, "col": "A",
                "character": {"name": "Adrian", "occupation": "Alchemist"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A1", "type": "SAME",
                    "params": {"target1": "A1", "target2": "A2"},
                    "description": "Adrian and Fabian have the same status."
                }
            },
            {
                "id": "B1", "row": 1, "col": "B",
                "character": {"name": "Beatrice", "occupation": "Botanist"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_B1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "B"}},
                    "description": "Exactly 1 person in Column B is a Criminal."
                }
            },
            {
                "id": "C1", "row": 1, "col": "C",
                "character": {"name": "Cedric", "occupation": "Chirurgeon"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C1", "type": "DIFFERENT",
                    "params": {"target1": "C1", "target2": "B1"},
                    "description": "Cedric and Beatrice have different statuses."
                }
            },
            {
                "id": "D1", "row": 1, "col": "D",
                "character": {"name": "Dorothea", "occupation": "Dean"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D1", "type": "SAME",
                    "params": {"target1": "D1", "target2": "C1"},
                    "description": "Dorothea and Cedric have the same status."
                }
            },
            {
                "id": "E1", "row": 1, "col": "E",
                "character": {"name": "Edmund", "occupation": "Enchanter"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_E1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
                    "description": "Exactly 1 person in Row 1 is a Criminal."
                }
            },
            # Row 2
            {
                "id": "A2", "row": 2, "col": "A",
                "character": {"name": "Fabian", "occupation": "Faculty Head"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A2", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 2}},
                    "description": "Exactly 1 person in Row 2 is a Criminal."
                }
            },
            {
                "id": "B2", "row": 2, "col": "B",
                "character": {"name": "Genevieve", "occupation": "Geologist"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B2", "type": "SAME",
                    "params": {"target1": "B2", "target2": "A2"},
                    "description": "Genevieve and Fabian have the same status."
                }
            },
            {
                "id": "C2", "row": 2, "col": "C",
                "character": {"name": "Harold", "occupation": "Historian"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C2", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "C"}},
                    "description": "Exactly 2 people in Column C are Criminals."
                }
            },
            {
                "id": "D2", "row": 2, "col": "D",
                "character": {"name": "Isolde", "occupation": "Illusionist"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D2", "type": "SAME",
                    "params": {"target1": "D2", "target2": "D1"},
                    "description": "Isolde and Dorothea have the same status."
                }
            },
            {
                "id": "E2", "row": 2, "col": "E",
                "character": {"name": "Julian", "occupation": "Jurist"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_E2", "type": "DIFFERENT",
                    "params": {"target1": "E2", "target2": "E4"},
                    "description": "Julian and Thaddeus have different statuses."
                }
            },
            # Row 3
            {
                "id": "A3", "row": 3, "col": "A",
                "character": {"name": "Kaelen", "occupation": "Knight"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A3", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "A"}},
                    "description": "Exactly 2 people in Column A are Criminals."
                }
            },
            {
                "id": "B3", "row": 3, "col": "B",
                "character": {"name": "Lysandra", "occupation": "Librarian"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B3", "type": "SAME",
                    "params": {"target1": "B3", "target2": "B2"},
                    "description": "Lysandra and Genevieve have the same status."
                }
            },
            {
                "id": "C3", "row": 3, "col": "C",
                "character": {"name": "Magnus", "occupation": "Magister"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C3", "type": "DIFFERENT",
                    "params": {"target1": "C3", "target2": "C2"},
                    "description": "Magnus and Harold have different statuses."
                }
            },
            {
                "id": "D3", "row": 3, "col": "D",
                "character": {"name": "Nerissa", "occupation": "Necromancer"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_D3", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "COLUMN", "col": "D"}},
                    "description": "Exactly 1 person in Column D is a Criminal."
                }
            },
            {
                "id": "E3", "row": 3, "col": "E",
                "character": {"name": "Octavius", "occupation": "Oracle"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_E3", "type": "SAME",
                    "params": {"target1": "E3", "target2": "E1"},
                    "description": "Octavius and Edmund have the same status."
                }
            },
            # Row 4
            {
                "id": "A4", "row": 4, "col": "A",
                "character": {"name": "Percival", "occupation": "Philosopher"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A4", "type": "SAME",
                    "params": {"target1": "A4", "target2": "A1"},
                    "description": "Percival and Adrian have the same status."
                }
            },
            {
                "id": "B4", "row": 4, "col": "B",
                "character": {"name": "Quinn", "occupation": "Quartermaster"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B4", "type": "SAME",
                    "params": {"target1": "B4", "target2": "B3"},
                    "description": "Quinn and Lysandra have the same status."
                }
            },
            {
                "id": "C4", "row": 4, "col": "C",
                "character": {"name": "Roland", "occupation": "Researcher"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C4", "type": "SAME",
                    "params": {"target1": "C4", "target2": "C3"},
                    "description": "Roland and Magnus have the same status."
                }
            },
            {
                "id": "D4", "row": 4, "col": "D",
                "character": {"name": "Seraphina", "occupation": "Scribe"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D4", "type": "DIFFERENT",
                    "params": {"target1": "D4", "target2": "D3"},
                    "description": "Seraphina and Nerissa have different statuses."
                }
            },
            {
                "id": "E4", "row": 4, "col": "E",
                "character": {"name": "Thaddeus", "occupation": "Theologian"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_E4", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 4}},
                    "description": "Exactly 1 person in Row 4 is a Criminal."
                }
            },
            # Row 5
            {
                "id": "A5", "row": 5, "col": "A",
                "character": {"name": "Ursula", "occupation": "Undergraduate"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A5", "type": "COUNT_COMPARE",
                    "params": {
                        "operator": "GT",
                        "region1": {"type": "COLUMN", "col": "A"},
                        "region2": {"type": "COLUMN", "col": "B"}
                    },
                    "description": "Column A has more Criminals than Column B."
                }
            },
            {
                "id": "B5", "row": 5, "col": "B",
                "character": {"name": "Victor", "occupation": "Vice-Chancellor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B5", "type": "PARITY",
                    "params": {"parity": "ODD", "region": {"type": "ROW", "row": 5}},
                    "description": "An odd number of people in Row 5 are Criminals."
                }
            },
            {
                "id": "C5", "row": 5, "col": "C",
                "character": {"name": "Winifred", "occupation": "Warden"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C5", "type": "EXACTLY",
                    "params": {"count": 3, "region": {"type": "ROW", "row": 5}},
                    "description": "Exactly 3 people in Row 5 are Criminals."
                }
            },
            {
                "id": "D5", "row": 5, "col": "D",
                "character": {"name": "Xander", "occupation": "Xylographer"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D5", "type": "SAME",
                    "params": {"target1": "D5", "target2": "D4"},
                    "description": "Xander and Seraphina have the same status."
                }
            },
            {
                "id": "E5", "row": 5, "col": "E",
                "character": {"name": "Yvaine", "occupation": "Yearling Scholar"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_E5", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "E"}},
                    "description": "Exactly 2 people in Column E are Criminals."
                }
            }
        ]
    }

def get_puzzle_5x5_02() -> dict:
    return {
        "puzzle_id": "puzzle_5x5_02",
        "name": "The Metropolitan Heist",
        "size": 5,
        "initial_revealed": ["B2", "D4"],
        "grid": [
            # Row 1
            {
                "id": "A1", "row": 1, "col": "A",
                "character": {"name": "Alan", "occupation": "Architect"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A1", "type": "SAME",
                    "params": {"target1": "A1", "target2": "A2"},
                    "description": "Alan and Felix have the same status."
                }
            },
            {
                "id": "B1", "row": 1, "col": "B",
                "character": {"name": "Brenda", "occupation": "Broker"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B1", "type": "DIFFERENT",
                    "params": {"target1": "B1", "target2": "C1"},
                    "description": "Brenda and Conrad have different statuses."
                }
            },
            {
                "id": "C1", "row": 1, "col": "C",
                "character": {"name": "Conrad", "occupation": "Courier"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C1", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
                    "description": "Exactly 1 person in Row 1 is a Criminal."
                }
            },
            {
                "id": "D1", "row": 1, "col": "D",
                "character": {"name": "Damian", "occupation": "Dispatcher"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D1", "type": "SAME",
                    "params": {"target1": "D1", "target2": "E1"},
                    "description": "Damian and Elena have the same status."
                }
            },
            {
                "id": "E1", "row": 1, "col": "E",
                "character": {"name": "Elena", "occupation": "Electrician"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_E1", "type": "SAME",
                    "params": {"target1": "E1", "target2": "E2"},
                    "description": "Elena and Jack have the same status."
                }
            },
            # Row 2
            {
                "id": "A2", "row": 2, "col": "A",
                "character": {"name": "Felix", "occupation": "Foreman"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A2", "type": "DIFFERENT",
                    "params": {"target1": "A2", "target2": "A3"},
                    "description": "Felix and Kira have different statuses."
                }
            },
            {
                "id": "B2", "row": 2, "col": "B",
                "character": {"name": "Grace", "occupation": "Gunslinger"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B2", "type": "EXACTLY",
                    "params": {"count": 0, "region": {"type": "COLUMN", "col": "B"}},
                    "description": "Nobody in Column B is a Criminal."
                }
            },
            {
                "id": "C2", "row": 2, "col": "C",
                "character": {"name": "Henry", "occupation": "Hacker"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C2", "type": "EXACTLY",
                    "params": {"count": 1, "region": {"type": "ROW", "row": 2}},
                    "description": "Exactly 1 person in Row 2 is a Criminal."
                }
            },
            {
                "id": "D2", "row": 2, "col": "D",
                "character": {"name": "Iris", "occupation": "Informant"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D2", "type": "PARITY",
                    "params": {"parity": "ODD", "region": {"type": "ROW", "row": 2}},
                    "description": "An odd number of people in Row 2 are Criminals."
                }
            },
            {
                "id": "E2", "row": 2, "col": "E",
                "character": {"name": "Jack", "occupation": "Janitor"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_E2", "type": "DIFFERENT",
                    "params": {"target1": "E2", "target2": "E3"},
                    "description": "Jack and Oscar have different statuses."
                }
            },
            # Row 3
            {
                "id": "A3", "row": 3, "col": "A",
                "character": {"name": "Kira", "occupation": "Kingpin"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A3", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "A"}},
                    "description": "Exactly 2 people in Column A are Criminals."
                }
            },
            {
                "id": "B3", "row": 3, "col": "B",
                "character": {"name": "Leo", "occupation": "Lockpicker"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B3", "type": "COUNT_COMPARE",
                    "params": {
                        "operator": "GT",
                        "region1": {"type": "COLUMN", "col": "C"},
                        "region2": {"type": "COLUMN", "col": "A"}
                    },
                    "description": "Column C has more Criminals than Column A."
                }
            },
            {
                "id": "C3", "row": 3, "col": "C",
                "character": {"name": "Maya", "occupation": "Mastermind"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C3", "type": "EXACTLY",
                    "params": {"count": 3, "region": {"type": "COLUMN", "col": "C"}},
                    "description": "Exactly 3 people in Column C are Criminals."
                }
            },
            {
                "id": "D3", "row": 3, "col": "D",
                "character": {"name": "Nathan", "occupation": "Negotiator"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D3", "type": "SAME",
                    "params": {"target1": "D3", "target2": "C3"},
                    "description": "Nathan and Maya have the same status."
                }
            },
            {
                "id": "E3", "row": 3, "col": "E",
                "character": {"name": "Oscar", "occupation": "Operative"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_E3", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "E"}},
                    "description": "Exactly 2 people in Column E are Criminals."
                }
            },
            # Row 4
            {
                "id": "A4", "row": 4, "col": "A",
                "character": {"name": "Paige", "occupation": "Patrolman"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_A4", "type": "SAME",
                    "params": {"target1": "A4", "target2": "A1"},
                    "description": "Paige and Alan have the same status."
                }
            },
            {
                "id": "B4", "row": 4, "col": "B",
                "character": {"name": "Quincy", "occupation": "Quality Assayer"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B4", "type": "EXACTLY",
                    "params": {"count": 0, "region": {"type": "ROW", "row": 4}},
                    "description": "Nobody in Row 4 is a Criminal."
                }
            },
            {
                "id": "C4", "row": 4, "col": "C",
                "character": {"name": "Rachel", "occupation": "Rigger"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_C4", "type": "SAME",
                    "params": {"target1": "C4", "target2": "C3"},
                    "description": "Rachel and Maya have the same status."
                }
            },
            {
                "id": "D4", "row": 4, "col": "D",
                "character": {"name": "Sam", "occupation": "Safecracker"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D4", "type": "EXACTLY",
                    "params": {"count": 0, "region": {"type": "COLUMN", "col": "D"}},
                    "description": "Nobody in Column D is a Criminal."
                }
            },
            {
                "id": "E4", "row": 4, "col": "E",
                "character": {"name": "Tara", "occupation": "Tracker"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_E4", "type": "DIFFERENT",
                    "params": {"target1": "E4", "target2": "E5"},
                    "description": "Tara and Yuri have different statuses."
                }
            },
            # Row 5
            {
                "id": "A5", "row": 5, "col": "A",
                "character": {"name": "Uri", "occupation": "Undercover Agent"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_A5", "type": "EXACTLY",
                    "params": {"count": 3, "region": {"type": "ROW", "row": 5}},
                    "description": "Exactly 3 people in Row 5 are Criminals."
                }
            },
            {
                "id": "B5", "row": 5, "col": "B",
                "character": {"name": "Vance", "occupation": "Vault Guard"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_B5", "type": "PARITY",
                    "params": {"parity": "ODD", "region": {"type": "ROW", "row": 5}},
                    "description": "An odd number of people in Row 5 are Criminals."
                }
            },
            {
                "id": "C5", "row": 5, "col": "C",
                "character": {"name": "Wade", "occupation": "Watchman"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_C5", "type": "SAME",
                    "params": {"target1": "C5", "target2": "A5"},
                    "description": "Wade and Uri have the same status."
                }
            },
            {
                "id": "D5", "row": 5, "col": "D",
                "character": {"name": "Xena", "occupation": "X-Ray Tech"},
                "hidden_status": "INNOCENT",
                "clue": {
                    "id": "clue_D5", "type": "SAME",
                    "params": {"target1": "D5", "target2": "D1"},
                    "description": "Xena and Damian have the same status."
                }
            },
            {
                "id": "E5", "row": 5, "col": "E",
                "character": {"name": "Yuri", "occupation": "Yardmaster"},
                "hidden_status": "CRIMINAL",
                "clue": {
                    "id": "clue_E5", "type": "EXACTLY",
                    "params": {"count": 2, "region": {"type": "COLUMN", "col": "E"}},
                    "description": "Yuri admits: Exactly 2 people in Column E are Criminals."
                }
            }
        ]
    }

def main():
    puzzles = [
        get_puzzle_3x3_01(),
        get_puzzle_3x3_02(),
        get_puzzle_4x4_01(),
        get_puzzle_4x4_02(),
        get_puzzle_5x5_01(),
        get_puzzle_5x5_02()
    ]

    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schemas", "puzzle_schema.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    data_dir = os.path.dirname(os.path.abspath(__file__))

    print("=================================================================")
    print("STARTING DPLL VERIFICATION & JSON EXPORT FOR ALL 6 PUZZLES")
    print("=================================================================")

    for p in puzzles:
        pid = p["puzzle_id"]
        # 1. JSON Schema validation
        jsonschema.validate(instance=p, schema=schema)
        print(f"[{pid}] JSON Schema validation: PASSED")

        # 2. DPLL Logic Verification (Consistency, Uniqueness, No-Guess Solvability)
        ok = verify_puzzle_with_dpll(p)
        if not ok:
            print(f"FAILED VERIFICATION FOR {pid}")
            sys.exit(1)

        # 3. Save JSON file
        out_path = os.path.join(data_dir, f"{pid}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2, ensure_ascii=False)
        print(f"Saved: {out_path}")

    # Also update sample_3x3.json with validated puzzle_3x3_01
    sample_path = os.path.join(data_dir, "sample_3x3.json")
    with open(sample_path, "w", encoding="utf-8") as f:
        json.dump(puzzles[0], f, indent=2, ensure_ascii=False)
    print(f"Updated sample_3x3.json with validated puzzle_3x3_01.")

    print("\n=================================================================")
    print("ALL 6 PUZZLES SUCCESSFULLY VERIFIED AND GENERATED!")
    print("=================================================================")

if __name__ == "__main__":
    main()
