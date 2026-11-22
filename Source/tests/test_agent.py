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


# ---------- Tests with fake solver/encoder (run before TV1/TV2 are done) ----------
import copy

from Source.agent.agent import CRIMINAL, INNOCENT, UNKNOWN, INCONSISTENT, SOLVED, STUCK
from Source.tests.fakes import BruteSolver, FakeEncoder


def _cell(cid, hidden, ctype, **params):
    return {"id": cid, "row": int(cid[1]), "col": cid[0],
            "character": {"name": cid, "occupation": "X"}, "hidden_status": hidden,
            "clue": {"id": f"clue_{cid}", "type": ctype, "params": params, "description": ""}}


# Criminals: B1, C2. Forced order: B1, C1, C2, C3, B2, A2, A3, B3. Uses all 8 clue types.
PUZZLE = {"puzzle_id": "t", "name": "t", "size": 3, "initial_revealed": ["A1"], "grid": [
    _cell("A1", "INNOCENT", "FACT", target="B1", status="CRIMINAL"),
    _cell("B1", "CRIMINAL", "EXACTLY", count=1, region={"type": "ROW", "row": 1}),
    _cell("C1", "INNOCENT", "DIFFERENT", target1="C1", target2="C2"),
    _cell("A2", "INNOCENT", "PARITY", parity="EVEN", region={"type": "ROW", "row": 3}),
    _cell("B2", "INNOCENT", "EXACTLY", count=2, region={"type": "NEIGHBORS", "cell": "B2"}),
    _cell("C2", "CRIMINAL", "AT_MOST", count=1, region={"type": "COLUMN", "col": "C"}),
    _cell("A3", "INNOCENT", "COUNT_COMPARE", operator="GT",
          region1={"type": "COLUMN", "col": "C"}, region2={"type": "COLUMN", "col": "A"}),
    _cell("B3", "INNOCENT", "AT_LEAST", count=1, region={"type": "EXPLICIT", "cells": ["B1", "C2"]}),
    _cell("C3", "INNOCENT", "SAME", target1="C3", target2="B2"),
]}


def _agent():
    return DeductiveAgent(FakeEncoder(), BruteSolver())


def _weak_puzzle():
    p = copy.deepcopy(PUZZLE)
    p["grid"][0]["clue"].update(type="AT_MOST", params={"count": 2, "region": {"type": "ROW", "row": 1}})
    return p


def test_fake_solves_without_guessing_in_row_major_order():
    agent = _agent()
    steps = agent.solve(GameEngine(PUZZLE))   # engine checks every verdict against the hidden truth
    assert agent.status == SOLVED
    assert [s.cell_id for s in steps] == ["B1", "C1", "C2", "C3", "B2", "A2", "A3", "B3"]
    assert steps[0].verdict == CRIMINAL and steps[0].forced_by_clue_ids == ["clue_A1"]
    assert steps[0].new_clue["id"] == "clue_B1" and steps[0].sat_queries > 0
    assert agent.sat_calls == sum(s.sat_queries for s in steps)


def test_fake_engine_strict_mode_uses_agent_as_verifier():
    engine = GameEngine(PUZZLE, entailment_verifier=_agent().classify_cell)
    assert engine.submit_verdict("C1", "INNOCENT").status_code == "NOT_PROVABLE"   # not forced yet
    assert engine.submit_verdict("B1", "INNOCENT").status_code == "CONTRADICTED"
    assert engine.submit_verdict("B1", "CRIMINAL").is_valid


def test_fake_stuck_returns_unknown_and_does_not_reveal():
    engine = GameEngine(_weak_puzzle())
    agent = _agent()
    assert agent.solve(engine) == [] and agent.status == STUCK
    assert set(agent.classify(engine.get_public_state()).values()) == {UNKNOWN}
    assert list(engine.revealed_statuses) == ["A1"]


def test_fake_inconsistent_kb():
    state = PublicState(grid_size=3, revealed_verdicts={"B1": INNOCENT},
                        revealed_clues=[PUZZLE["grid"][0]["clue"]], unsolved_cells=["A1"])
    agent = _agent()
    assert agent.classify_cell(state, "A1") == INCONSISTENT
    assert agent.solve_step(state) is None and agent.status == INCONSISTENT


def test_fake_uniqueness():
    assert check_puzzle_uniqueness(PUZZLE, FakeEncoder(), BruteSolver())
    loose = copy.deepcopy(PUZZLE)   # every clue only says A1 and B1 differ: many models
    for c in loose["grid"]:
        c["clue"].update(type="DIFFERENT", params={"target1": "A1", "target2": "B1"})
    assert not check_puzzle_uniqueness(loose, FakeEncoder(), BruteSolver())


def test_fake_hint():
    state = GameEngine(PUZZLE).get_public_state()
    assert get_hint(state, _agent()) == ("B1", CRIMINAL)
    assert get_hint(GameEngine(_weak_puzzle()).get_public_state(), _agent()) is None
