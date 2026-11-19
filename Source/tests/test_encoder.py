"""Unit tests for CNF Encoder and Semantics (TV2)."""

import itertools

import pytest

from Source.core.encoder import CNFEncoder, VariableMapper
from Source.core.semantics import evaluate_clue_semantic


def enumerate_solutions(clue: dict, ids: list[str], grid_size: int = 3) -> list[dict[str, bool]]:
    mapper = VariableMapper(grid_size)
    encoder = CNFEncoder(mapper, grid_size)
    clauses = encoder.encode_clue(clue)
    solutions = []
    auxiliary_count = mapper.auxiliary_variable_count

    for values in itertools.product((False, True), repeat=len(ids)):
        assignment = dict(zip(ids, values))
        cnf_main = {mapper.get_var(cell): value for cell, value in assignment.items()}
        cnf_satisfied = False

        auxiliary_values = itertools.product((False, True), repeat=auxiliary_count)
        for auxiliaries in auxiliary_values:
            cnf_assignment = dict(cnf_main)
            cnf_assignment.update({
                1000 + index: value
                for index, value in enumerate(auxiliaries)
            })
            if all(
                any(
                    cnf_assignment[abs(literal)] == (literal > 0)
                    for literal in clause
                )
                for clause in clauses
            ):
                cnf_satisfied = True
                break

        if cnf_satisfied:
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
            {"type": "EXACTLY", "params": {"count": 1, "region": {"type": "ROW", "row": 1}}},
            ["A1", "B1", "C1"],
            3,
        ),
        (
            {"type": "AT_LEAST", "params": {"count": 2, "region": {"type": "ROW", "row": 1}}},
            ["A1", "B1", "C1"],
            4,
        ),
        (
            {"type": "AT_MOST", "params": {"count": 1, "region": {"type": "ROW", "row": 1}}},
            ["A1", "B1", "C1"],
            4,
        ),
        (
            {"type": "PARITY", "params": {"parity": "EVEN", "region": {"type": "ROW", "row": 1}}},
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
    solutions = enumerate_solutions(clue, ids)
    assert len(solutions) == expected_count
    for assignment in solutions:
        assert evaluate_clue_semantic(clue, assignment, ids)
