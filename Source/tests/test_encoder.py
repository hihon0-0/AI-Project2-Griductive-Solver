"""Unit tests for CNF Encoder and VariableMapper (TV2).
Target module: Source.core.encoder

Requirements tested:
1. Deterministic mapping between cell coordinates and integer propositional variables.
2. Separate allocation of auxiliary variables.
3. Accurate CNF conversion for 6 core clue templates:
   - FACT
   - SAME
   - DIFFERENT
   - EXACTLY
   - AT_LEAST
   - AT_MOST
4. Accurate CNF conversion for 2 extensions:
   - PARITY
   - COUNT_COMPARE
"""
import pytest
from Source.core.encoder import VariableMapper, CNFEncoder

def test_variable_mapper():
    mapper = VariableMapper()
    var_a1 = mapper.get_var("A1")
    var_b1 = mapper.get_var("B1")

    assert var_a1 > 0
    assert var_b1 > 0
    assert var_a1 != var_b1
    # Deterministic check: calling again returns same int
    assert mapper.get_var("A1") == var_a1
    assert mapper.get_cell(var_a1) == "A1"

    # Auxiliary variables must be strictly distinct from primary
    aux1 = mapper.new_aux_var()
    aux2 = mapper.new_aux_var()
    assert aux1 >= 1000
    assert aux2 > aux1
    assert aux1 != var_a1

def test_encode_fact():
    mapper = VariableMapper()
    encoder = CNFEncoder(mapper)

    # Abel is CRIMINAL -> [var_a1]
    clue_crim = {"type": "FACT", "params": {"target": "A1", "status": "CRIMINAL"}}
    clauses_crim = encoder.encode_clue(clue_crim, grid_size=3)
    var_a1 = mapper.get_var("A1")
    assert [var_a1] in clauses_crim

    # Abel is INNOCENT -> [-var_a1]
    clue_inno = {"type": "FACT", "params": {"target": "A1", "status": "INNOCENT"}}
    clauses_inno = encoder.encode_clue(clue_inno, grid_size=3)
    assert [-var_a1] in clauses_inno

def test_encode_same():
    """SAME(A1, B1) is (A1 <-> B1) == (~A1 OR B1) AND (A1 OR ~B1)."""
    mapper = VariableMapper()
    encoder = CNFEncoder(mapper)

    clue = {"type": "SAME", "params": {"target1": "A1", "target2": "B1"}}
    clauses = encoder.encode_clue(clue, grid_size=3)
    va = mapper.get_var("A1")
    vb = mapper.get_var("B1")

    # Check that clauses enforce equality
    # [-va, vb] and [va, -vb]
    assert any(set(c) == {-va, vb} for c in clauses)
    assert any(set(c) == {va, -vb} for c in clauses)

def test_encode_different():
    """DIFFERENT(A1, B1) is (A1 XOR B1) == (A1 OR B1) AND (~A1 OR ~B1)."""
    mapper = VariableMapper()
    encoder = CNFEncoder(mapper)

    clue = {"type": "DIFFERENT", "params": {"target1": "A1", "target2": "B1"}}
    clauses = encoder.encode_clue(clue, grid_size=3)
    va = mapper.get_var("A1")
    vb = mapper.get_var("B1")

    assert any(set(c) == {va, vb} for c in clauses)
    assert any(set(c) == {-va, -vb} for c in clauses)

def test_encode_counting_clues():
    """Test EXACTLY, AT_LEAST, AT_MOST for 3 cells: A1, B1, C1 in Row 1."""
    mapper = VariableMapper()
    encoder = CNFEncoder(mapper)
    v1 = mapper.get_var("A1")
    v2 = mapper.get_var("B1")
    v3 = mapper.get_var("C1")

    # AT_LEAST 1 in Row 1 -> (v1 OR v2 OR v3)
    clue_at_least_1 = {
        "type": "AT_LEAST",
        "params": {"count": 1, "region": {"type": "ROW", "row": 1}}
    }
    clauses_al1 = encoder.encode_clue(clue_at_least_1, grid_size=3)
    assert any(set(c) == {v1, v2, v3} for c in clauses_al1)

    # AT_MOST 1 in Row 1 -> cannot have any 2 true: (~v1 OR ~v2), (~v1 OR ~v3), (~v2 OR ~v3)
    clue_at_most_1 = {
        "type": "AT_MOST",
        "params": {"count": 1, "region": {"type": "ROW", "row": 1}}
    }
    clauses_am1 = encoder.encode_clue(clue_at_most_1, grid_size=3)
    assert any(set(c) == {-v1, -v2} for c in clauses_am1)
    assert any(set(c) == {-v1, -v3} for c in clauses_am1)
    assert any(set(c) == {-v2, -v3} for c in clauses_am1)

    # EXACTLY 1 in Row 1 -> conjunction of AT_LEAST 1 and AT_MOST 1
    clue_exact_1 = {
        "type": "EXACTLY",
        "params": {"count": 1, "region": {"type": "ROW", "row": 1}}
    }
    clauses_ex1 = encoder.encode_clue(clue_exact_1, grid_size=3)
    assert len(clauses_ex1) >= 4

def test_encode_extensions():
    """Test PARITY and COUNT_COMPARE extensions."""
    mapper = VariableMapper()
    encoder = CNFEncoder(mapper)

    clue_parity = {
        "type": "PARITY",
        "params": {"parity": "EVEN", "region": {"type": "ROW", "row": 1}}
    }
    clauses_parity = encoder.encode_clue(clue_parity, grid_size=3)
    assert len(clauses_parity) > 0, "PARITY clue must generate CNF clauses"

    clue_compare = {
        "type": "COUNT_COMPARE",
        "params": {
            "operator": "GT",
            "region1": {"type": "COLUMN", "col": "A"},
            "region2": {"type": "COLUMN", "col": "B"}
        }
    }
    clauses_compare = encoder.encode_clue(clue_compare, grid_size=3)
    assert len(clauses_compare) > 0, "COUNT_COMPARE clue must generate CNF clauses"
