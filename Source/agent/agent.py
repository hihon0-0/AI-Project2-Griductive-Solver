"""Deductive Logic Agent (Member 4).

Performs No-Guess reasoning via refutation on the public knowledge base only:
    KB ∧ ¬C_i UNSAT -> CRIMINAL
    KB ∧  C_i UNSAT -> INNOCENT
    both SAT        -> UNKNOWN
    KB itself UNSAT -> INCONSISTENT
"""
from typing import Iterator, Optional

from ..core.solver_metrics import SolverMetrics
from ..engine.models import PublicState
from .deduction_trace import DeductionStep

CRIMINAL, INNOCENT, UNKNOWN, INCONSISTENT = "CRIMINAL", "INNOCENT", "UNKNOWN", "INCONSISTENT"
SOLVED, STUCK = "SOLVED", "STUCK"


def cell_ids(grid_size: int) -> list[str]:
    """All cells in row-major order: A1, B1, C1, A2, ..."""
    return [f"{chr(ord('A') + c)}{r}" for r in range(1, grid_size + 1) for c in range(grid_size)]


def row_major_key(cell_id: str) -> tuple[int, str]:
    return int(cell_id[1:]), cell_id[0]


class DeductiveAgent:
    """Sees only PublicState. encoder/solver are injectable so the agent can be tested
    before TV1/TV2 finish; defaults are the team's CNFEncoder and DPLLSolver."""

    def __init__(self, encoder=None, solver=None):
        if encoder is None:
            from ..core.encoder import CNFEncoder, VariableMapper
            encoder = CNFEncoder(VariableMapper())
        if solver is None:
            from ..core.dpll import DPLLSolver
            solver = DPLLSolver()
        self.encoder, self.solver, self.mapper = encoder, solver, encoder.mapper
        self.grid_size = 3
        self._clue_cache: dict[str, list[list[int]]] = {}  # re-encoding would allocate new aux vars
        self.metrics = SolverMetrics()   # summed over all SAT calls
        self.sat_calls = 0
        self.status: Optional[str] = None
        self.trace: list[DeductionStep] = []

    # ---------- knowledge base ----------
    def encode_clue(self, clue: dict) -> list[list[int]]:
        if clue["id"] not in self._clue_cache:
            self._clue_cache[clue["id"]] = self.encoder.encode_clue(clue, self.grid_size)
        return self._clue_cache[clue["id"]]

    def build_kb(self, state: PublicState) -> list[list[int]]:
        """KB_t = CNF(revealed clues) ∧ unit clauses for proved verdicts."""
        self.grid_size = state.grid_size
        for cell in cell_ids(state.grid_size):   # fixes the deterministic variable order
            self.mapper.get_var(cell)
        kb = [cl for clue in state.revealed_clues for cl in self.encode_clue(clue)]
        for cell, verdict in state.revealed_verdicts.items():
            v = self.mapper.get_var(cell)
            kb.append([v] if verdict == CRIMINAL else [-v])
        return kb

    def _sat(self, kb: list[list[int]], assumptions: list[int]) -> bool:
        is_sat, _, m = self.solver.solve(kb, assumptions)
        self.sat_calls += 1
        self.metrics.decisions += m.decisions
        self.metrics.propagations += m.propagations
        self.metrics.backtracks += m.backtracks
        self.metrics.runtime += m.runtime
        return is_sat

    def _verdict(self, kb: list[list[int]], cell: str) -> str:
        v = self.mapper.get_var(cell)
        if not self._sat(kb, [-v]):
            return CRIMINAL
        if not self._sat(kb, [v]):
            return INNOCENT
        return UNKNOWN

    # ---------- classification ----------
    def classify(self, state: PublicState) -> dict[str, str]:
        """Verdict for every unresolved cell; every value is INCONSISTENT if KB_t is UNSAT."""
        kb = self.build_kb(state)
        cells = sorted(state.unsolved_cells, key=row_major_key)
        if not self._sat(kb, []):
            return {c: INCONSISTENT for c in cells}
        return {c: self._verdict(kb, c) for c in cells}

    def classify_cell(self, public_state: PublicState, cell_id: str) -> str:
        """CRIMINAL / INNOCENT / UNKNOWN for one cell, INCONSISTENT if KB_t is UNSAT.
        Signature matches GameEngine's entailment_verifier, so the engine can use it for manual play."""
        kb = self.build_kb(public_state)
        if not self._sat(kb, []):
            return INCONSISTENT
        return self._verdict(kb, cell_id.upper())

    def proof_clues(self, state: PublicState, cell: str, verdict: str) -> list[str]:
        """Minimal (not necessarily smallest) set of revealed clues that, with the proved verdicts,
        still forces `verdict`: drop one clue at a time while the refutation stays UNSAT."""
        v = self.mapper.get_var(cell)
        kb = self.build_kb(state)
        facts = kb[len(kb) - len(state.revealed_verdicts):]   # build_kb appends verdict units last
        refute = [-v] if verdict == CRIMINAL else [v]
        keep = list(state.revealed_clues)
        for clue in list(keep):
            rest = [c for c in keep if c is not clue]
            if not self._sat([cl for c in rest for cl in self.encode_clue(c)] + facts, refute):
                keep = rest
        return [c["id"] for c in keep]

    def find_forced(self, state: PublicState) -> Optional[tuple[str, str, int, list[str]]]:
        """The forced cell needing the fewest clues (ties: row-major): (cell_id, verdict, sat_queries, clue_ids).
        Hint, Step and Auto all use this. Returns None and sets self.status to STUCK / INCONSISTENT."""
        before = self.sat_calls
        kb = self.build_kb(state)
        if not self._sat(kb, []):
            self.status = INCONSISTENT
            return None
        best = None
        for cell in sorted(state.unsolved_cells, key=row_major_key):
            verdict = self._verdict(kb, cell)
            if verdict == UNKNOWN:
                continue
            clues = self.proof_clues(state, cell, verdict)
            if best is None or len(clues) < len(best[2]):
                best = (cell, verdict, clues)
            if len(clues) <= 1:   # nothing can need fewer
                break
        if best is None:
            self.status = STUCK
            return None
        return best[0], best[1], self.sat_calls - before, best[2]

    def solve_step(self, public_state: PublicState) -> Optional[tuple[str, str]]:
        """Finds next logically forced verdict. Returns (cell_id, verdict) or None."""
        found = self.find_forced(public_state)
        return found[:2] if found else None

    def clues_mentioning(self, state: PublicState, cell: str) -> list[str]:
        v = self.mapper.get_var(cell)
        return [clue["id"] for clue in state.revealed_clues
                if any(abs(lit) == v for cl in self.encode_clue(clue) for lit in cl)]

    # ---------- deduction loop ----------
    def get_solution_stream(self, engine) -> Iterator[DeductionStep]:
        """Yields one DeductionStep per accepted verdict until SOLVED, STUCK or INCONSISTENT.
        Talks to the engine only via get_public_state() and submit_verdict()."""
        self.status, self.trace = None, []
        while True:
            state = engine.get_public_state()
            if not state.unsolved_cells:
                self.status = SOLVED
                return
            found = self.find_forced(state)
            if found is None:
                return
            cell, verdict, queries, clue_ids = found
            result = engine.submit_verdict(cell, verdict)
            if not result.is_valid:  # an entailed verdict is only rejected if encoder/solver/puzzle is wrong
                raise RuntimeError(f"Engine rejected forced verdict {cell}={verdict}: {result.message}")
            step = DeductionStep(
                step_number=len(self.trace) + 1,
                cell_id=cell,
                verdict=verdict,
                forced_by_clue_ids=clue_ids,
                new_clue=result.revealed_clue,
                active_clue_ids=[c["id"] for c in state.revealed_clues],
                sat_queries=queries,
            )
            self.trace.append(step)
            yield step

    def solve(self, engine) -> list[DeductionStep]:
        """Runs the whole loop; check self.status afterwards."""
        return list(self.get_solution_stream(engine))
