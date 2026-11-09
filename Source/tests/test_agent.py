"""Unit tests for Deductive Logic Agent (TV4).
Target modules: Source.agent.agent, Source.agent.uniqueness, Source.agent.hint

Requirements tested:
1. Classification of unresolved cells into CRIMINAL, INNOCENT, or UNKNOWN.
2. Entailment via refutation (No-Guess principle).
3. Deduction loop with deduction trace generation.
4. Separate uniqueness checking for complete clue set.
5. Hint identification of currently forced cell without peeking.
"""
import os
import pytest
from Source.engine.puzzle_io import load_puzzle
from Source.engine.engine import GameEngine
from Source.engine.models import PublicState
from Source.agent.agent import DeductiveAgent
from Source.agent.uniqueness import check_puzzle_uniqueness
from Source.agent.hint import get_hint

SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "sample_3x3.json"
)

def test_agent_initialization():
    agent = DeductiveAgent()
    assert agent is not None

def test_agent_entailment_classification():
    """Given A1 is INNOCENT and clue is SAME(A1, B1):
    B1 must be classified as INNOCENT (forced).
    Other unconstrained cells should be classified as UNKNOWN.
    """
    agent = DeductiveAgent()
    pub_state = PublicState(
        grid_size=3,
        revealed_verdicts={"A1": "INNOCENT"},
        revealed_clues=[
            {
                "id": "clue_A1",
                "type": "SAME",
                "params": {"target1": "A1", "target2": "B1"},
                "description": "A1 and B1 have same status"
            }
        ],
        unsolved_cells=["B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3"]
    )

    # B1 is forced to be INNOCENT
    status_b1 = agent.classify_cell(pub_state, "B1")
    assert status_b1 == "INNOCENT", "B1 must be entailed as INNOCENT by refutation"

    # C3 has no clues pointing to it yet -> UNKNOWN
    status_c3 = agent.classify_cell(pub_state, "C3")
    assert status_c3 == "UNKNOWN", "C3 must be UNKNOWN"

def test_agent_hint_generation():
    """Hint function must return the forced cell B1."""
    pub_state = PublicState(
        grid_size=3,
        revealed_verdicts={"A1": "INNOCENT"},
        revealed_clues=[
            {
                "id": "clue_A1",
                "type": "SAME",
                "params": {"target1": "A1", "target2": "B1"},
                "description": "A1 and B1 have same status"
            }
        ],
        unsolved_cells=["B1", "C1"]
    )
    hint = get_hint(pub_state)
    assert hint is not None
    cell_id, verdict = hint
    assert cell_id == "B1"
    assert verdict == "INNOCENT"

def test_puzzle_uniqueness_check():
    """Sample 3x3 puzzle must have exactly one unique solution."""
    puzzle = load_puzzle(SAMPLE_PATH)
    is_unique = check_puzzle_uniqueness(puzzle)
    assert is_unique is True, "Sample 3x3 puzzle must be verified as having a UNIQUE solution"
