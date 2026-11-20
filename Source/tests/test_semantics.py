"""Unit tests for Direct Semantic Evaluators (TV2).
Target module: Source.core.semantics.evaluate_clue_semantic

Tests that each clue template can evaluate a complete assignment directly to True/False
WITHOUT using CNF encoding.
"""
import pytest
from Source.core.semantics import evaluate_clue_semantic

def test_semantic_fact():
    clue = {"type": "FACT", "params": {"target": "A1", "status": "CRIMINAL"}}
    assert evaluate_clue_semantic(clue, {"A1": True}, grid_size=3) is True
    assert evaluate_clue_semantic(clue, {"A1": False}, grid_size=3) is False

def test_semantic_same_and_different():
    clue_same = {"type": "SAME", "params": {"target1": "A1", "target2": "B1"}}
    assert evaluate_clue_semantic(clue_same, {"A1": True, "B1": True}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_same, {"A1": False, "B1": False}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_same, {"A1": True, "B1": False}, grid_size=3) is False

    clue_diff = {"type": "DIFFERENT", "params": {"target1": "A1", "target2": "B1"}}
    assert evaluate_clue_semantic(clue_diff, {"A1": True, "B1": False}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_diff, {"A1": True, "B1": True}, grid_size=3) is False

def test_semantic_exactly_at_least_at_most():
    # Region: Row 1 (A1, B1, C1)
    clue_exact = {
        "type": "EXACTLY",
        "params": {"count": 1, "region": {"type": "ROW", "row": 1}}
    }
    assert evaluate_clue_semantic(clue_exact, {"A1": True, "B1": False, "C1": False}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_exact, {"A1": True, "B1": True, "C1": False}, grid_size=3) is False
    assert evaluate_clue_semantic(clue_exact, {"A1": False, "B1": False, "C1": False}, grid_size=3) is False

    clue_at_least = {
        "type": "AT_LEAST",
        "params": {"count": 2, "region": {"type": "ROW", "row": 1}}
    }
    assert evaluate_clue_semantic(clue_at_least, {"A1": True, "B1": True, "C1": False}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_at_least, {"A1": True, "B1": False, "C1": False}, grid_size=3) is False

    clue_at_most = {
        "type": "AT_MOST",
        "params": {"count": 1, "region": {"type": "ROW", "row": 1}}
    }
    assert evaluate_clue_semantic(clue_at_most, {"A1": False, "B1": False, "C1": False}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_at_most, {"A1": True, "B1": False, "C1": False}, grid_size=3) is True
    assert evaluate_clue_semantic(clue_at_most, {"A1": True, "B1": True, "C1": False}, grid_size=3) is False

def test_semantic_parity_and_count_compare():
    clue_parity = {
        "type": "PARITY",
        "params": {"parity": "EVEN", "region": {"type": "ROW", "row": 1}}
    }
    # 2 criminals -> EVEN -> True
    assert evaluate_clue_semantic(clue_parity, {"A1": True, "B1": True, "C1": False}, grid_size=3) is True
    # 1 criminal -> ODD -> False
    assert evaluate_clue_semantic(clue_parity, {"A1": True, "B1": False, "C1": False}, grid_size=3) is False

    clue_compare = {
        "type": "COUNT_COMPARE",
        "params": {
            "operator": "GT",
            "region1": {"type": "COLUMN", "col": "A"},
            "region2": {"type": "COLUMN", "col": "B"}
        }
    }
    # Col A: A1=T, A2=T, A3=F (count 2). Col B: B1=T, B2=F, B3=F (count 1) -> 2 > 1 -> True
    assignment = {
        "A1": True, "A2": True, "A3": False,
        "B1": True, "B2": False, "B3": False,
        "C1": False, "C2": False, "C3": False
    }
    assert evaluate_clue_semantic(clue_compare, assignment, grid_size=3) is True
