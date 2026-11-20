"""DPLL SAT Solver implementation (Member 1).
Must implement pure Python DPLL with:
1. Unit propagation
2. Conflict detection
3. Deterministic variable selection
4. Recursive branching and backtracking
5. Recording decisions, propagations, backtracks, and runtime
"""
from typing import Optional
import time
from .solver_metrics import SolverMetrics

class DPLLSolver:
    """Davis-Putnam-Logemann-Loveland (DPLL) SAT Solver."""

    def __init__(self):
        self.metrics = SolverMetrics()

    def solve(self, clauses: list[list[int]], assumptions: Optional[list[int]] = None) -> tuple[bool, Optional[dict[int, bool]], SolverMetrics]:
        """Solves the CNF formula with optional assumptions.
        
        Args:
            clauses: List of clauses, where each clause is a list of non-zero integer literals (DIMACS format).
                     Example: [[1, 2], [-1, 2]] means (x1 OR x2) AND (NOT x1 OR x2)
            assumptions: Optional list of temporary unit literals that must hold True.
                         Example: [-1] means assume x1 is False.

        Returns:
            tuple (is_sat: bool, model: Optional[dict[int, bool]], metrics: SolverMetrics)
            - If SAT: (True, {1: False, 2: True, ...}, metrics)
            - If UNSAT: (False, None, metrics)
        """
        self.metrics.reset()
        start_time = time.time()
        
        # TODO [TV1]:
        # 1. Combine clauses with unit clauses from assumptions
        # 2. Call recursive DPLL solver: is_sat, model = self._dpll(clauses, {})
        # 3. Record runtime into self.metrics.runtime
        # 4. Return (is_sat, model, self.metrics)
        raise NotImplementedError("TODO [TV1]: Implement DPLL logic in Source/core/dpll.py")

    def _unit_propagate(self, clauses: list[list[int]], assignment: dict[int, bool]) -> tuple[list[list[int]], dict[int, bool], bool]:
        """Helper for Unit Propagation (TV1):
        Finds unit clauses (clauses with 1 unassigned literal), assigns it to True,
        simplifies clauses, and repeats until no unit clauses remain or conflict occurs.
        """
        # TODO [TV1]: Implement unit propagation
        pass

    def _pick_variable(self, clauses: list[list[int]], assignment: dict[int, bool]) -> Optional[int]:
        """Deterministic variable selection (TV1):
        Picks the next unassigned variable with the smallest variable ID.
        """
        # TODO [TV1]: Implement deterministic branching variable selection
        pass
