"""Unit tests for GameEngine (TV3)."""
import os
import pytest
from Source.engine.puzzle_io import load_puzzle
from Source.engine.engine import GameEngine
from Source.engine.models import VerdictStatus

SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "sample_3x3.json"
)

def test_engine_initial_state():
    puzzle = load_puzzle(SAMPLE_PATH)
    engine = GameEngine(puzzle)

    assert engine.size == 3
    assert not engine.is_solved()

    pub = engine.get_public_state()
    # Initially only A1 is revealed
    assert len(pub.revealed_verdicts) == 1
    assert "A1" in pub.revealed_verdicts
    assert pub.revealed_verdicts["A1"] == "INNOCENT"
    assert len(pub.revealed_clues) == 1
    assert len(pub.unsolved_cells) == 8

    # Public character info is available
    char_a1 = engine.get_character_info("A1")
    assert char_a1.name == "Abel"

def test_engine_submit_verdict_standalone():
    puzzle = load_puzzle(SAMPLE_PATH)
    engine = GameEngine(puzzle)

    # In sample_3x3, B1 is INNOCENT
    # Attempt wrong verdict
    res_wrong = engine.submit_verdict("B1", "CRIMINAL")
    assert not res_wrong.is_valid
    assert res_wrong.status_code == VerdictStatus.CONTRADICTED

    # Attempt correct verdict
    res_correct = engine.submit_verdict("B1", "INNOCENT")
    assert res_correct.is_valid
    assert res_correct.status_code == VerdictStatus.CORRECT
    assert res_correct.revealed_clue is not None
    assert res_correct.revealed_clue["type"] == "EXACTLY"

    # Submitting B1 again
    res_dup = engine.submit_verdict("B1", "INNOCENT")
    assert not res_dup.is_valid
    assert res_dup.status_code == VerdictStatus.ALREADY_SOLVED

    # Submitting invalid cell
    res_inv = engine.submit_verdict("Z9", "INNOCENT")
    assert not res_inv.is_valid
    assert res_inv.status_code == VerdictStatus.INVALID_CELL

def test_engine_with_entailment_verifier():
    puzzle = load_puzzle(SAMPLE_PATH)

    # Mock verifier
    def mock_verifier(pub_state, cell_id):
        if cell_id == "B1":
            return "INNOCENT"  # B1 is forced to be INNOCENT
        elif cell_id == "C1":
            return "UNKNOWN"   # C1 is not yet forced
        return "UNKNOWN"

    engine = GameEngine(puzzle, entailment_verifier=mock_verifier)

    # Player submits C1 = CRIMINAL (which is true in hidden solution, but NOT provable yet)
    res_unprovable = engine.submit_verdict("C1", "CRIMINAL")
    assert not res_unprovable.is_valid
    assert res_unprovable.status_code == VerdictStatus.NOT_PROVABLE

    # Player submits B1 = INNOCENT (which is provable)
    res_provable = engine.submit_verdict("B1", "INNOCENT")
    assert res_provable.is_valid
    assert res_provable.status_code == VerdictStatus.CORRECT

def test_engine_restart():
    puzzle = load_puzzle(SAMPLE_PATH)
    engine = GameEngine(puzzle)

    engine.submit_verdict("B1", "INNOCENT")
    assert len(engine.get_public_state().revealed_verdicts) == 2

    engine.restart()
    pub = engine.get_public_state()
    assert len(pub.revealed_verdicts) == 1
    assert "A1" in pub.revealed_verdicts
    assert "B1" not in pub.revealed_verdicts
