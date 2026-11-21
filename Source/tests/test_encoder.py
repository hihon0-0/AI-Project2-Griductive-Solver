"""Tests for CNF encoding and direct clue semantics."""

import itertools

import pytest

from Source.core.encoder import CNFEncoder, VariableMapper
from Source.core.semantics import evaluate_clue_semantic


def test_variable_mapper():
    mapper = VariableMapper()
    var_a1 = mapper.get_var("A1")
    var_b1 = mapper.get_var("B1")

    assert var_a1 > 0
    assert var_b1 > 0
    assert var_a1 != var_b1
    assert mapper.get_var("a1") == var_a1
    assert mapper.get_cell(var_a1) == "A1"
    assert mapper.get_cell(9999) == ""

    aux1 = mapper.new_aux_var()
    aux2 = mapper.get_aux_var()
    assert aux1 >= 1000
    assert aux2 > aux1
    assert aux1 != var_a1


def enumerate_solutions(
    clue: dict,
    ids: list[str],
    grid_size: int = 3,
) -> list[dict[str, bool]]:
    mapper = VariableMapper()
    encoder = CNFEncoder(mapper)
    clauses = encoder.encode_clue(clue, grid_size)
    solutions = []

    for values in itertools.product((False, True), repeat=len(ids)):
        assignment = dict(zip(ids, values))
        cnf_assignment = {
            mapper.get_var(cell): value for cell, value in assignment.items()
        }
        auxiliary_count = mapper.auxiliary_variable_count
        satisfies_cnf = False

        for auxiliary_values in itertools.product(
            (False, True), repeat=auxiliary_count
        ):
            candidate = cnf_assignment.copy()
            candidate.update({
                1000 + index: value
                for index, value in enumerate(auxiliary_values)
            })
            if all(
                any(candidate[abs(literal)] == (literal > 0) for literal in clause)
                for clause in clauses
            ):
                satisfies_cnf = True
                break

        if satisfies_cnf:
            solutions.append(assignment)

    return solutions


@pytest.mark.parametrize(
    ("clue", "ids", "expected_count"),
    [
        (
            {"type": "FACT", "params": {"target": "A1", "status": "CRIMINAL"}},
            ["A1"],
            1,
        ),
        (
            {"type": "FACT", "params": {"target": "A1", "status": "INNOCENT"}},
            ["A1"],
            1,
        ),
        (
            {"type": "SAME", "params": {"target1": "A1", "target2": "B1"}},
            ["A1", "B1"],
            2,
        ),
        (
            {"type": "DIFFERENT", "params": {"target1": "A1", "target2": "B1"}},
            ["A1", "B1"],
            2,
        ),
        (
            {
                "type": "EXACTLY",
                "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
            },
            ["A1", "B1", "C1"],
            3,
        ),
        (
            {
                "type": "AT_LEAST",
                "params": {"count": 2, "region": {"type": "ROW", "row": 1}},
            },
            ["A1", "B1", "C1"],
            4,
        ),
        (
            {
                "type": "AT_MOST",
                "params": {"count": 1, "region": {"type": "ROW", "row": 1}},
            },
            ["A1", "B1", "C1"],
            4,
        ),
        (
            {
                "type": "PARITY",
                "params": {"parity": "EVEN", "region": {"type": "ROW", "row": 1}},
            },
            ["A1", "B1", "C1"],
            4,
        ),
        (
            {
                "type": "PARITY",
                "params": {"parity": "ODD", "region": {"type": "ROW", "row": 1}},
            },
            ["A1", "B1", "C1"],
            4,
        ),
    ],
)
def test_encoder_matches_semantics(clue, ids, expected_count):
    solutions = enumerate_solutions(clue, ids)

    assert len(solutions) == expected_count
    for assignment in solutions:
        assert evaluate_clue_semantic(clue, assignment, ids)


@pytest.mark.parametrize(
    ("operator", "expected_count"),
    [
        ("GT", 5),
        ("GTE", 11),
        ("LT", 5),
        ("LTE", 11),
        ("EQ", 6),
    ],
)
def test_count_compare(operator, expected_count):
    ids = ["A1", "B1", "A2", "B2"]
    clue = {
        "type": "COUNT_COMPARE",
        "params": {
            "operator": operator,
            "region1": {"type": "COLUMN", "col": "A"},
            "region2": {"type": "COLUMN", "col": "B"},
        },
    }

    solutions = enumerate_solutions(clue, ids, grid_size=2)

    assert len(solutions) == expected_count
    for assignment in solutions:
        assert evaluate_clue_semantic(clue, assignment, ids)
