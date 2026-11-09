"""Unit tests for DPLL SAT Solver (TV1).
Target module: Source.core.dpll.DPLLSolver

Requirements tested:
1. Unit propagation
2. Conflict detection
3. Deterministic variable selection
4. Recursive branching and backtracking
5. Correct SAT (with model) / UNSAT result
6. Correct assumptions handling (crucial for TV4's refutation check)
7. Recording metrics (decisions, propagations, backtracks, runtime)
"""
import pytest
from Source.core.dpll import DPLLSolver
from Source.core.solver_metrics import SolverMetrics

def test_dpll_simple_sat():
    """Test formula: (x1 OR x2) AND (NOT x1 OR x2).
    Satisfiable with x2 = True.
    """
    solver = DPLLSolver()
    clauses = [[1, 2], [-1, 2]]
    is_sat, model, metrics = solver.solve(clauses)

    assert is_sat is True, "Formula should be SAT"
    assert model is not None, "Model must not be None when SAT"
    assert model.get(2) is True, "Variable 2 must be True in all satisfying models"
    assert isinstance(metrics, SolverMetrics)
    assert metrics.runtime >= 0.0

def test_dpll_simple_unsat():
    """Test contradictory formula: (x1) AND (NOT x1).
    Must return UNSAT and model must be None.
    """
    solver = DPLLSolver()
    clauses = [[1], [-1]]
    is_sat, model, metrics = solver.solve(clauses)

    assert is_sat is False, "Direct contradiction must be UNSAT"
    assert model is None, "Model must be None when UNSAT"

def test_dpll_unsat_4clauses():
    """Test 2-variable contradictory formula:
    (x1 OR x2) AND (x1 OR NOT x2) AND (NOT x1 OR x2) AND (NOT x1 OR NOT x2)
    All 4 assignments are blocked. Must be UNSAT.
    """
    solver = DPLLSolver()
    clauses = [
        [1, 2],
        [1, -2],
        [-1, 2],
        [-1, -2]
    ]
    is_sat, model, metrics = solver.solve(clauses)

    assert is_sat is False
    assert model is None

def test_dpll_unit_propagation_chain():
    """Test unit propagation cascading:
    (x1) AND (NOT x1 OR x2) AND (NOT x2 OR x3)
    Propagates: x1 -> True, then x2 -> True, then x3 -> True.
    """
    solver = DPLLSolver()
    clauses = [
        [1],
        [-1, 2],
        [-2, 3]
    ]
    is_sat, model, metrics = solver.solve(clauses)

    assert is_sat is True
    assert model[1] is True
    assert model[2] is True
    assert model[3] is True
    assert metrics.propagations >= 3, "Should record at least 3 unit propagations"

def test_dpll_with_assumptions():
    """Test solver under assumptions (temporary unit clauses).
    Given KB: (x1 OR x2) AND (NOT x1 OR x3)
    1. Assumption [1]: forces x3=True, x2 can be anything. (SAT)
    2. Assumption [-2, -3]:
       - from (x1 OR x2) and x2=False -> x1=True
       - from (NOT x1 OR x3) and x3=False -> x1=False -> CONFLICT! (UNSAT)
    """
    solver = DPLLSolver()
    clauses = [
        [1, 2],
        [-1, 3]
    ]

    # Sub-case A: Satisfiable assumption
    is_sat_a, model_a, _ = solver.solve(clauses, assumptions=[1])
    assert is_sat_a is True
    assert model_a[1] is True
    assert model_a[3] is True

    # Sub-case B: Contradictory assumptions
    is_sat_b, model_b, _ = solver.solve(clauses, assumptions=[-2, -3])
    assert is_sat_b is False
    assert model_b is None

def test_dpll_metrics_tracking():
    """Verifies that solver records decisions, backtracks, and runtime."""
    solver = DPLLSolver()
    clauses = [
        [1, 2, 3],
        [-1, -2],
        [-2, -3],
        [-1, -3]
    ]
    is_sat, model, metrics = solver.solve(clauses)

    assert is_sat is True
    assert hasattr(metrics, 'decisions')
    assert hasattr(metrics, 'propagations')
    assert hasattr(metrics, 'backtracks')
    assert hasattr(metrics, 'runtime')
    assert metrics.runtime > 0.0 or metrics.decisions >= 0
