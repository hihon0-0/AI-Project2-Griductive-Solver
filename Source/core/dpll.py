"""DPLL SAT Solver — pure Python implementation (Member 1 / TV1).

Implements the classic Davis–Putnam–Logemann–Loveland algorithm with:
  1. **Unit Propagation (BCP)** — iteratively forces values of unit-clause
     literals until a fixpoint or a conflict is reached.
  2. **Pure Literal Elimination** — assigns truth values to literals that
     appear with only one polarity across all remaining clauses.
  3. **Deterministic variable selection** — picks the unassigned variable
     that appears in the most clauses (VSIDS-lite / DLIS heuristic), with
     a tie-break on ascending variable id for reproducibility.
  4. **Recursive backtracking** — tries both polarities and counts every
     backtrack and decision in SolverMetrics.
  5. **Assumptions** — allows the caller (e.g. DeductiveAgent) to pass a
     list of initial forced literals so that "KB ∧ ¬Ci" checks can be
     performed by a single solver instance.

Public API
----------
    solver = DPLLSolver()
    sat, model, metrics = solver.solve(clauses, assumptions=[1, -3])

Parameters
----------
clauses : list[list[int]]
    CNF formula as a list of clauses.  Each clause is a list of non-zero
    integers. Positive = True, negative = False.  Example:
        [[1, -2], [-1, 2, 3]]   ≡  (x1 ∨ ¬x2) ∧ (¬x1 ∨ x2 ∨ x3)

assumptions : list[int] | None
    Optional list of literals to assert as unit clauses before solving.

Returns
-------
(is_sat, model, metrics)
    is_sat : bool
        True iff the formula (with assumptions) is satisfiable.
    model : dict[int, bool] | None
        A satisfying assignment {var_id: True/False} if SAT, None if UNSAT.
    metrics : SolverMetrics
        Performance counters for this call.
"""

from __future__ import annotations

import copy
from typing import Iterable, Optional
import time

from .solver_metrics import SolverMetrics


# ======================================================================== #
#  Internal helpers                                                         #
# ======================================================================== #

def _collect_variables(clauses: list[list[int]]) -> set[int]:
    """Return the set of *positive* variable ids occurring in *clauses*."""
    return {abs(lit) for clause in clauses for lit in clause}


# ======================================================================== #
#  DPLLSolver                                                               #
# ======================================================================== #

class DPLLSolver:
    """Pure-Python DPLL SAT solver with assumption support and metrics."""

    def __init__(self) -> None:
        self.metrics = SolverMetrics()
        self.total_metrics = SolverMetrics()

    def reset_total_metrics(self) -> None:
        """Reset cumulative session metrics back to zero."""
        self.total_metrics.reset()

    # ------------------------------------------------------------------ #
    #  Public entry-point                                                   #
    # ------------------------------------------------------------------ #

    def solve(
        self,
        clauses: list[list[int]],
        assumptions: list[int] | None = None,
        required_vars: Iterable[int] | None = None,
    ) -> tuple[bool, Optional[dict[int, bool]], SolverMetrics]:
        """Solve the CNF *clauses* under optional *assumptions*.

        Args:
            clauses: List of clauses (DIMACS format).
            assumptions: Optional list of unit literals that must hold.
            required_vars: Optional iterable of variable IDs that must appear
                in the returned model even if unmentioned in clauses.

        Returns:
            (is_sat, model, metrics_snapshot)
        """
        # Reset metrics for this invocation
        self.metrics.reset()
        self.metrics.start_timer()

        # Deep-copy so we never mutate the caller's data
        working_clauses: list[list[int]] = [list(c) for c in clauses]

        # Inject assumptions as unit clauses
        if assumptions:
            for lit in assumptions:
                working_clauses.append([lit])

        # Collect all variable ids from clauses and required_vars
        all_vars = _collect_variables(working_clauses)
        if required_vars:
            all_vars |= {abs(v) for v in required_vars}

        # Start empty assignment
        assignment: dict[int, bool] = {}

        sat, model = self._dpll(working_clauses, assignment, all_vars)

        self.metrics.stop_timer()
        self.metrics.sat_calls = 1
        self.total_metrics.add(self.metrics)

        # Return a detached copy of metrics so subsequent solves don't mutate caller references
        return sat, model, copy.copy(self.metrics)

    # ------------------------------------------------------------------ #
    #  Core recursive DPLL                                                  #
    # ------------------------------------------------------------------ #

    def _dpll(
        self,
        clauses: list[list[int]],
        assignment: dict[int, bool],
        all_vars: set[int],
    ) -> tuple[bool, Optional[dict[int, bool]]]:
        """Recursive DPLL with BCP + pure-literal + branching."""

        # ---- 1. Unit propagation ----
        clauses, assignment, ok = self._unit_propagate(clauses, assignment)
        if not ok:
            # Conflict detected during propagation
            return False, None

        # ---- 2. Check termination conditions ----
        if len(clauses) == 0:
            # All clauses satisfied — build full model (default unset vars
            # to False for determinism)
            full_model = {v: assignment.get(v, False) for v in all_vars}
            return True, full_model

        # Empty clause would have been caught by BCP, but guard anyway
        if any(len(c) == 0 for c in clauses):
            self.metrics.record_conflict()
            return False, None

        # ---- 3. Pure literal elimination ----
        clauses, assignment = self._pure_literal_assign(clauses, assignment)
        if len(clauses) == 0:
            full_model = {v: assignment.get(v, False) for v in all_vars}
            return True, full_model

        # ---- 4. Choose branching variable ----
        var = self._choose_variable(clauses, assignment, all_vars)
        if var is None:
            # Every variable assigned — check if any clause is still alive
            # (should not happen if simplification was correct)
            full_model = {v: assignment.get(v, False) for v in all_vars}
            return True, full_model

        # ---- 5. Branch on var = True first, then False ----
        for value in (True, False):
            self.metrics.record_decision()

            lit = var if value else -var
            new_clauses = self._assign_literal(clauses, lit)
            new_assignment = dict(assignment)
            new_assignment[var] = value

            sat, model = self._dpll(new_clauses, new_assignment, all_vars)
            if sat:
                return True, model

            # This branch failed — backtrack
            self.metrics.record_backtrack()

        return False, None

    # ------------------------------------------------------------------ #
    #  Unit propagation (BCP)                                               #
    # ------------------------------------------------------------------ #

    def _unit_propagate(
        self,
        clauses: list[list[int]],
        assignment: dict[int, bool],
    ) -> tuple[list[list[int]], dict[int, bool], bool]:
        """Iterate BCP until fixpoint.

        Returns ``(simplified_clauses, assignment, success)``.
        ``success`` is False if a conflict (empty clause) is derived.
        """
        assignment = dict(assignment)  # local copy
        changed = True

        while changed:
            changed = False
            unit_lits: list[int] = []

            # Find all unit clauses
            for clause in clauses:
                if len(clause) == 1:
                    unit_lits.append(clause[0])

            if not unit_lits:
                break

            for lit in unit_lits:
                var = abs(lit)
                val = lit > 0

                # Check for contradicting assignment
                if var in assignment:
                    if assignment[var] != val:
                        self.metrics.record_conflict()
                        return clauses, assignment, False
                    # Already assigned consistently — skip
                    continue

                assignment[var] = val
                self.metrics.record_propagation()
                clauses = self._assign_literal(clauses, lit)
                changed = True

                # Conflict: empty clause produced?
                if any(len(c) == 0 for c in clauses):
                    self.metrics.record_conflict()
                    return clauses, assignment, False

        return clauses, assignment, True

    # ------------------------------------------------------------------ #
    #  Pure literal elimination                                             #
    # ------------------------------------------------------------------ #

    def _pure_literal_assign(
        self,
        clauses: list[list[int]],
        assignment: dict[int, bool],
    ) -> tuple[list[list[int]], dict[int, bool]]:
        """Assign literals that appear with only one polarity."""
        assignment = dict(assignment)

        # Collect polarity information
        pos: set[int] = set()
        neg: set[int] = set()
        for clause in clauses:
            for lit in clause:
                if lit > 0:
                    pos.add(lit)
                else:
                    neg.add(-lit)

        # Pure positives: appear positive but never negative
        pure_pos = pos - neg
        # Pure negatives: appear negative but never positive
        pure_neg = neg - pos

        for var in pure_pos:
            if var not in assignment:
                assignment[var] = True
                self.metrics.record_propagation()
                clauses = self._assign_literal(clauses, var)

        for var in pure_neg:
            if var not in assignment:
                assignment[var] = False
                self.metrics.record_propagation()
                clauses = self._assign_literal(clauses, -var)

        return clauses, assignment

    # ------------------------------------------------------------------ #
    #  Variable selection heuristic                                         #
    # ------------------------------------------------------------------ #

    def _choose_variable(
        self,
        clauses: list[list[int]],
        assignment: dict[int, bool],
        all_vars: set[int],
    ) -> Optional[int]:
        """Select the most active unassigned variable (DLIS-style).

        Ties are broken by smallest variable id for determinism.
        """
        # Count how many clauses each unassigned variable appears in
        counts: dict[int, int] = {}
        for clause in clauses:
            for lit in clause:
                var = abs(lit)
                if var not in assignment:
                    counts[var] = counts.get(var, 0) + 1

        if not counts:
            # All variables in remaining clauses are already assigned
            # Check if there are still globally unassigned variables
            unassigned = all_vars - set(assignment.keys())
            if unassigned:
                return min(unassigned)
            return None

        # Pick variable with highest count, break ties by smallest id
        best_var = max(counts.keys(), key=lambda v: (counts[v], -v))
        return best_var

    def _pick_variable(
        self,
        clauses: list[list[int]],
        assignment: dict[int, bool],
        all_vars: Optional[set[int]] = None,
    ) -> Optional[int]:
        """Alias for variable selection matching upstream template signature."""
        if all_vars is None:
            all_vars = _collect_variables(clauses)
        return self._choose_variable(clauses, assignment, all_vars)

    # ------------------------------------------------------------------ #
    #  Clause simplification                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _assign_literal(
        clauses: list[list[int]],
        lit: int,
    ) -> list[list[int]]:
        """Simplify *clauses* given that *lit* is True.

        - Remove every clause containing *lit*  (clause is satisfied).
        - Remove *-lit* from every remaining clause (literal is falsified).
        """
        neg_lit = -lit
        new_clauses: list[list[int]] = []
        for clause in clauses:
            if lit in clause:
                # Clause is satisfied — drop it entirely
                continue
            # Remove the negation of the literal if present
            new_clause = [l for l in clause if l != neg_lit]
            new_clauses.append(new_clause)
        return new_clauses
