"""Unit tests for DPLL SAT Solver (TV1).

Covers:
  - Trivial SAT / UNSAT
  - Unit propagation
  - Pure literal elimination
  - Backtracking
  - Assumptions
  - Metrics correctness
  - Edge cases (empty formula, single clause, contradictory assumptions)
  - Griductive-style scenario (3×3 board variables)
"""

import sys
import os

try:
    import pytest
except ImportError:
    pytest = None

# Ensure Source/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

try:
    from core.dpll import DPLLSolver
    from core.solver_metrics import SolverMetrics
except ImportError:
    from Source.core.dpll import DPLLSolver
    from Source.core.solver_metrics import SolverMetrics


# ======================================================================== #
#  Upstream Baseline TDD Tests                                              #
# ======================================================================== #

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

    is_sat_a, model_a, _ = solver.solve(clauses, assumptions=[1])
    assert is_sat_a is True
    assert model_a[1] is True
    assert model_a[3] is True

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
    assert metrics.runtime >= 0.0


# ======================================================================== #
#  Helper                                                                   #
# ======================================================================== #

def _make_solver() -> DPLLSolver:
    return DPLLSolver()


# ======================================================================== #
#  1. Basic SAT / UNSAT                                                     #
# ======================================================================== #

class TestBasicSatUnsat:
    """Fundamental satisfiability checks."""

    def test_single_positive_literal(self):
        """[[1]] is trivially SAT with x1 = True."""
        solver = _make_solver()
        sat, model, m = solver.solve([[1]])
        assert sat is True
        assert model is not None
        assert model[1] is True

    def test_single_negative_literal(self):
        """[[-1]] is SAT with x1 = False."""
        solver = _make_solver()
        sat, model, m = solver.solve([[-1]])
        assert sat is True
        assert model[1] is False

    def test_two_unit_clauses_consistent(self):
        """[[1], [2]] => x1=True, x2=True."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1], [2]])
        assert sat is True
        assert model[1] is True
        assert model[2] is True

    def test_two_unit_clauses_contradictory(self):
        """[[1], [-1]] is UNSAT."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1], [-1]])
        assert sat is False
        assert model is None

    def test_simple_satisfiable(self):
        """(x1 ∨ x2) ∧ (¬x1 ∨ x2) => SAT with x2=True."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, 2], [-1, 2]])
        assert sat is True
        assert model[2] is True

    def test_simple_unsatisfiable(self):
        """(x1) ∧ (¬x1) ∧ (x2) ∧ (¬x2) is UNSAT."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1], [-1], [2], [-2]])
        assert sat is False
        assert model is None

    def test_empty_formula_is_sat(self):
        """An empty CNF (no clauses) is trivially SAT."""
        solver = _make_solver()
        sat, model, _ = solver.solve([])
        assert sat is True
        assert model is not None  # empty dict

    def test_single_empty_clause_is_unsat(self):
        """A formula containing an empty clause [[]] is UNSAT."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[]])
        assert sat is False
        assert model is None


# ======================================================================== #
#  2. Unit Propagation                                                      #
# ======================================================================== #

class TestUnitPropagation:
    """Verify that BCP correctly forces values and simplifies."""

    def test_chain_propagation(self):
        """Unit clauses trigger a chain: [1], [-1,2], [-2,3] => x1=T, x2=T, x3=T."""
        solver = _make_solver()
        sat, model, m = solver.solve([[1], [-1, 2], [-2, 3]])
        assert sat is True
        assert model[1] is True
        assert model[2] is True
        assert model[3] is True
        # At least 1 propagation for the initial unit clause
        assert m.propagations >= 1

    def test_unit_prop_conflict(self):
        """[1], [-1,2], [-2] forces x1=T -> x2=T -> conflict with [-2]? No.
        Actually [-2] forces x2=F and [-1,2] with x1=T forces x2=T -> conflict."""
        solver = _make_solver()
        sat, model, m = solver.solve([[1], [-1, 2], [-2]])
        # x1=T (from [1]), [-2] forces x2=F, then [-1,2] becomes [2] but x2=F -> conflict
        assert sat is False
        assert m.conflicts >= 1

    def test_multiple_unit_clauses(self):
        """[1],[2],[3] => all True, formula collapses immediately."""
        solver = _make_solver()
        sat, model, m = solver.solve([[1], [2], [3]])
        assert sat is True
        assert model == {1: True, 2: True, 3: True}


# ======================================================================== #
#  3. Backtracking                                                          #
# ======================================================================== #

class TestBacktracking:
    """Ensure the solver can recover from wrong branches."""

    def test_requires_backtracking(self):
        """(x1 ∨ x2) ∧ (¬x1 ∨ x2) ∧ (x1 ∨ ¬x2) ∧ (¬x1 ∨ ¬x3) ∧ (x2 ∨ x3)
        Has solutions but may require backtracking."""
        solver = _make_solver()
        clauses = [[1, 2], [-1, 2], [1, -2], [-1, -3], [2, 3]]
        sat, model, m = solver.solve(clauses)
        assert sat is True
        # Verify model satisfies all clauses
        for clause in clauses:
            assert any(
                (model[abs(l)] if l > 0 else not model[abs(l)]) for l in clause
            ), f"Clause {clause} not satisfied by model {model}"

    def test_backtracking_unsat(self):
        """All 4 combinations of 2 variables: no unit clauses initially,
        forces solver to make a decision and backtrack."""
        solver = _make_solver()
        clauses = [[1, 2], [-1, 2], [1, -2], [-1, -2]]
        sat, model, m = solver.solve(clauses)
        assert sat is False
        assert m.backtracks >= 1


# ======================================================================== #
#  4. Assumptions                                                           #
# ======================================================================== #

class TestAssumptions:
    """Test that assumptions are injected as unit clauses correctly."""

    def test_assumption_forces_value(self):
        """Assume x1=True on formula (x1 ∨ x2)."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, 2]], assumptions=[1])
        assert sat is True
        assert model[1] is True

    def test_assumption_causes_unsat(self):
        """(x1 ∨ x2) is SAT, but with assumptions [1, -1] it's UNSAT."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, 2]], assumptions=[1, -1])
        assert sat is False

    def test_assumption_negative_literal(self):
        """Assume ¬x2 on (x1 ∨ x2) ∧ (¬x1 ∨ x2).
        x2=False -> clause2 becomes [¬x1] -> x1=False -> clause1 becomes [] -> UNSAT."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, 2], [-1, 2]], assumptions=[-2])
        assert sat is False

    def test_assumption_propagation_chain(self):
        """Assume x1=True on (¬x1 ∨ x2) ∧ (¬x2 ∨ x3) => x2=T, x3=T."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[-1, 2], [-2, 3]], assumptions=[1])
        assert sat is True
        assert model[1] is True
        assert model[2] is True
        assert model[3] is True

    def test_multiple_assumptions(self):
        """Multiple assumptions all applied."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, 2, 3]], assumptions=[1, 2])
        assert sat is True
        assert model[1] is True
        assert model[2] is True

    def test_assumption_no_side_effect_on_original(self):
        """Calling solve() with assumptions should not mutate the original clauses list."""
        solver = _make_solver()
        original = [[1, 2], [-1, 3]]
        clauses_copy = [list(c) for c in original]
        solver.solve(original, assumptions=[-2])
        assert original == clauses_copy


# ======================================================================== #
#  5. Metrics                                                               #
# ======================================================================== #

class TestMetrics:
    """Verify that SolverMetrics tracks correct values."""

    def test_metrics_reset_between_calls(self):
        """Each solve() call resets metrics."""
        solver = _make_solver()
        solver.solve([[1], [-1]])  # UNSAT
        m1_conflicts = solver.metrics.conflicts

        solver.solve([[1]])  # SAT — should reset
        assert solver.metrics.conflicts == 0  # no conflicts this time

    def test_runtime_is_positive(self):
        solver = _make_solver()
        _, _, m = solver.solve([[1, 2], [-1, 2], [1, -2]])
        assert m.runtime > 0

    def test_propagation_counted(self):
        """Unit clause [1] should produce at least 1 propagation."""
        solver = _make_solver()
        _, _, m = solver.solve([[1], [-1, 2]])
        assert m.propagations >= 1

    def test_no_decisions_for_pure_unit(self):
        """Formula solvable entirely by unit propagation needs 0 decisions."""
        solver = _make_solver()
        _, _, m = solver.solve([[1], [2], [3]])
        assert m.decisions == 0

    def test_solver_metrics_summary(self):
        """SolverMetrics.summary() returns a readable string."""
        m = SolverMetrics()
        m.decisions = 5
        m.propagations = 12
        m.backtracks = 2
        m.conflicts = 1
        m.runtime = 0.001234
        s = m.summary()
        assert "decisions" in s
        assert "5" in s
        assert "propagations" in s
        assert "12" in s

    def test_solver_metrics_reset(self):
        m = SolverMetrics()
        m.decisions = 10
        m.propagations = 20
        m.backtracks = 5
        m.conflicts = 3
        m.runtime = 1.0
        m.reset()
        assert m.decisions == 0
        assert m.propagations == 0
        assert m.backtracks == 0
        assert m.conflicts == 0
        assert m.runtime == 0.0


# ======================================================================== #
#  6. Pure Literal Elimination                                              #
# ======================================================================== #

class TestPureLiteral:
    """Test pure literal elimination specifically."""

    def test_pure_positive(self):
        """x1 appears only positive => assigned True, clauses with x1 removed."""
        solver = _make_solver()
        # x1 only positive, x2 both polarities
        sat, model, _ = solver.solve([[1, 2], [1, -2]])
        assert sat is True
        assert model[1] is True

    def test_pure_negative(self):
        """x1 appears only negative => assigned False."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[-1, 2], [-1, -2]])
        assert sat is True
        assert model[1] is False


# ======================================================================== #
#  7. Edge Cases                                                            #
# ======================================================================== #

class TestEdgeCases:
    """Edge cases and stress scenarios."""

    def test_large_clause(self):
        """Single clause with 20 literals."""
        solver = _make_solver()
        clause = list(range(1, 21))  # [1,2,...,20]
        sat, model, _ = solver.solve([clause])
        assert sat is True
        # At least one of the 20 vars should be True
        assert any(model[v] for v in range(1, 21))

    def test_all_negative_unit_clauses(self):
        """[[-1],[-2],[-3]] => all False."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[-1], [-2], [-3]])
        assert sat is True
        assert all(model[v] is False for v in [1, 2, 3])

    def test_tautological_clause_ignored(self):
        """[1,-1] is a tautology — always satisfied."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, -1]])
        assert sat is True

    def test_duplicate_literals_in_clause(self):
        """[1,1,2] should behave like [1,2]."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[1, 1, 2], [-1]])
        assert sat is True
        assert model[1] is False
        assert model[2] is True

    def test_repeated_solve_calls(self):
        """Solver instance can be reused for multiple calls."""
        solver = _make_solver()
        s1, m1, _ = solver.solve([[1], [-1]])
        s2, m2, _ = solver.solve([[1, 2]])
        assert s1 is False
        assert s2 is True

    def test_non_contiguous_variable_ids(self):
        """Variables 10, 20, 30 (not 1,2,3)."""
        solver = _make_solver()
        sat, model, _ = solver.solve([[10, 20], [-10, 30], [-20, -30]])
        assert sat is True
        # Verify all clauses satisfied
        for clause in [[10, 20], [-10, 30], [-20, -30]]:
            assert any(
                (model[abs(l)] if l > 0 else not model[abs(l)]) for l in clause
            )


# ======================================================================== #
#  8. Model verification helper                                             #
# ======================================================================== #

def _verify_model(clauses, model):
    """Assert that every clause has at least one true literal under model."""
    for clause in clauses:
        satisfied = False
        for lit in clause:
            var = abs(lit)
            val = model.get(var, False)
            if (lit > 0 and val) or (lit < 0 and not val):
                satisfied = True
                break
        assert satisfied, f"Clause {clause} not satisfied by {model}"


# ======================================================================== #
#  9. Griductive-style scenario                                             #
# ======================================================================== #

class TestGriductiveScenario:
    """Simulate a small Griductive-like SAT problem.

    3×3 board: cells A1..C3.  Variable mapping:
        A1=1, B1=2, C1=3, A2=4, B2=5, C2=6, A3=7, B3=8, C3=9
    True = CRIMINAL, False = INNOCENT.

    Ground truth (from sample_3x3.json):
        A1=I, B1=I, C1=C, A2=C, B2=I, C2=I, A3=I, B3=I, C3=C
    Model: {1:F, 2:F, 3:T, 4:T, 5:F, 6:F, 7:F, 8:F, 9:T}

    Encoded clues (selected):
        SAME(A1,B1):       (A1 ↔ B1) = (¬1∨2)∧(1∨¬2)
        EXACTLY(1, row1):  Exactly 1 of {1,2,3} is True
        DIFFERENT(C1,C2):  (C1 ⊕ C2) = (3∨6)∧(¬3∨¬6)
        AT_MOST(1, colA):  At most 1 of {1,4,7}
        EXACTLY(2, colC):  Exactly 2 of {3,6,9}
    """

    def _build_clauses(self):
        clauses = []

        # SAME(A1, B1): (¬1∨2) ∧ (1∨¬2)
        clauses.append([-1, 2])
        clauses.append([1, -2])

        # EXACTLY(1, {1,2,3}):
        #   At least 1: (1∨2∨3)
        #   At most 1:  (¬1∨¬2) ∧ (¬1∨¬3) ∧ (¬2∨¬3)
        clauses.append([1, 2, 3])
        clauses.append([-1, -2])
        clauses.append([-1, -3])
        clauses.append([-2, -3])

        # DIFFERENT(C1, C2): (3∨6) ∧ (¬3∨¬6)
        clauses.append([3, 6])
        clauses.append([-3, -6])

        # AT_MOST(1, {1,4,7}): (¬1∨¬4) ∧ (¬1∨¬7) ∧ (¬4∨¬7)
        clauses.append([-1, -4])
        clauses.append([-1, -7])
        clauses.append([-4, -7])

        # EXACTLY(2, {3,6,9}):
        #   At least 2: (3∨6)∧(3∨9)∧(6∨9)
        #   At most 2:  (¬3∨¬6∨¬9)  [at most 2 = not all 3]
        #   Correction — proper encoding:
        #   At least 2:  (6∨9) ∧ (3∨9) ∧ (3∨6)   — every pair has ≥1
        #   At most 2:   (¬3∨¬6∨¬9)
        clauses.append([6, 9])
        clauses.append([3, 9])
        clauses.append([3, 6])
        clauses.append([-3, -6, -9])

        return clauses

    def test_full_board_sat(self):
        """The clue set should be satisfiable."""
        solver = _make_solver()
        clauses = self._build_clauses()
        sat, model, m = solver.solve(clauses)
        assert sat is True
        _verify_model(clauses, model)

    def test_entailment_via_refutation_criminal(self):
        """KB ∧ ¬C1 (assume C1=Innocent i.e. x3=False) should be UNSAT
        IF C1 is forced to be CRIMINAL by the clues.

        With the partial clue set above, let's check with an assumption
        that is consistent with ground truth.
        """
        solver = _make_solver()
        clauses = self._build_clauses()

        # Test: Assume A1 = CRIMINAL (x1=True)
        # SAME(A1,B1) forces B1=True, but EXACTLY(1,row1) allows at most 1
        # of {1,2,3}, and both 1,2 true violates at-most-1. => UNSAT
        sat, model, m = solver.solve(clauses, assumptions=[1])
        assert sat is False, "A1=CRIMINAL should be refuted"

    def test_entailment_via_refutation_innocent(self):
        """KB ∧ C1 (assume C1=Criminal i.e. x3=True) should be SAT."""
        solver = _make_solver()
        clauses = self._build_clauses()
        sat, model, m = solver.solve(clauses, assumptions=[3])
        assert sat is True, "C1=CRIMINAL should be consistent"
        assert model[3] is True

    def test_metrics_recorded_for_griductive(self):
        """Metrics should have non-trivial values for the board."""
        solver = _make_solver()
        clauses = self._build_clauses()
        _, _, m = solver.solve(clauses)
        assert m.runtime > 0
        assert (m.decisions + m.propagations) > 0


# ======================================================================== #
#  10. Solver correctness stress test                                       #
# ======================================================================== #

class TestCorrectnessStress:
    """Randomly-structured but deterministic formulas."""

    def test_3sat_satisfiable_instance(self):
        """Hand-crafted 3-SAT instance known to be satisfiable."""
        clauses = [
            [1, 2, 3],
            [-1, 2, 4],
            [1, -3, 4],
            [-2, 3, -4],
            [1, -2, -4],
        ]
        solver = _make_solver()
        sat, model, _ = solver.solve(clauses)
        assert sat is True
        _verify_model(clauses, model)

    def test_3sat_unsatisfiable_instance(self):
        """All 8 sign combinations of {1,2,3} — UNSAT by resolution."""
        clauses = [
            [1, 2, 3],
            [1, 2, -3],
            [1, -2, 3],
            [1, -2, -3],
            [-1, 2, 3],
            [-1, 2, -3],
            [-1, -2, 3],
            [-1, -2, -3],
        ]
        solver = _make_solver()
        sat, model, m = solver.solve(clauses)
        assert sat is False
        assert m.conflicts >= 1


# ======================================================================== #
#  11. Enhancements: required_vars, metrics copy, and total_metrics         #
# ======================================================================== #

class TestEnhancements:
    """Tests for required_vars inclusion and metrics history/accumulation."""

    def test_required_vars_included_in_model(self):
        """Unrevealed/unreferenced variables in required_vars must appear in model."""
        solver = _make_solver()
        # Formula only refers to var 1 and 2
        clauses = [[1, 2]]
        # Required vars includes 3, 4, 9 (e.g., unopened board cells)
        sat, model, _ = solver.solve(clauses, required_vars=[1, 2, 3, 4, 9])
        assert sat is True
        assert model is not None
        for v in [1, 2, 3, 4, 9]:
            assert v in model, f"Variable {v} missing from satisfying model"

    def test_metrics_immutability_in_history(self):
        """Each solve call returns an independent copy so history lists are not mutated."""
        solver = _make_solver()
        history = []

        _, _, m1 = solver.solve([[1, 2], [-1, 2], [1, -2], [-1, -2]]) # requires backtrack
        history.append(m1)
        prev_backtracks = m1.backtracks
        assert prev_backtracks >= 1

        # Next call that requires 0 backtracks
        _, _, m2 = solver.solve([[1]])
        history.append(m2)

        # Ensure previous metrics snapshot in history was NOT reset to 0
        assert history[0].backtracks == prev_backtracks
        assert history[1].sat_calls == 1

    def test_total_metrics_accumulation_and_reset(self):
        """Total metrics correctly accumulates calls and resets on demand."""
        solver = _make_solver()
        solver.reset_total_metrics()

        solver.solve([[1]])
        solver.solve([[1, 2]])
        solver.solve([[1], [-1]])

        assert solver.total_metrics.sat_calls == 3
        assert solver.total_metrics.runtime > 0

        solver.reset_total_metrics()
        assert solver.total_metrics.sat_calls == 0
        assert solver.total_metrics.runtime == 0.0


if __name__ == '__main__':
    # 1. Run baseline tests
    baseline_tests = [
        test_dpll_simple_sat,
        test_dpll_simple_unsat,
        test_dpll_unsat_4clauses,
        test_dpll_unit_propagation_chain,
        test_dpll_with_assumptions,
        test_dpll_metrics_tracking,
    ]
    for fn in baseline_tests:
        fn()

    # 2. Run comprehensive suite
    test_classes = [
        TestBasicSatUnsat,
        TestUnitPropagation,
        TestBacktracking,
        TestAssumptions,
        TestMetrics,
        TestPureLiteral,
        TestEdgeCases,
        TestGriductiveScenario,
        TestCorrectnessStress,
        TestEnhancements,
    ]
    total = len(baseline_tests)
    passed = len(baseline_tests)
    for cls in test_classes:
        instance = cls()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total += 1
                getattr(instance, method_name)()
                passed += 1
    print(f"All {passed}/{total} DPLL tests passed successfully!")
