"""Test doubles so TV4's agent can be tested before TV1 (DPLL) and TV2 (encoder) are done.
shortcut: brute-force solver + truth-table encoder only scale to 3x3, switch the agent tests
to the real DPLLSolver/CNFEncoder once they land."""
from itertools import product

from Source.core.solver_metrics import SolverMetrics
from Source.engine.region_helper import RegionHelper


def clue_cells(clue: dict, n: int) -> list[str]:
    p = clue["params"]
    if clue["type"] == "FACT":
        return [p["target"]]
    if clue["type"] in ("SAME", "DIFFERENT"):
        return [p["target1"], p["target2"]]
    if clue["type"] == "COUNT_COMPARE":
        return RegionHelper.sort_cells(RegionHelper.resolve_region(p["region1"], n)
                                       + RegionHelper.resolve_region(p["region2"], n))
    return RegionHelper.resolve_region(p["region"], n)


def holds(clue: dict, a: dict[str, bool], n: int) -> bool:
    p, t = clue["params"], clue["type"]
    count = lambda reg: sum(a[c] for c in RegionHelper.resolve_region(reg, n))
    if t == "FACT":
        return a[p["target"]] == (p["status"] == "CRIMINAL")
    if t == "SAME":
        return a[p["target1"]] == a[p["target2"]]
    if t == "DIFFERENT":
        return a[p["target1"]] != a[p["target2"]]
    if t == "EXACTLY":
        return count(p["region"]) == p["count"]
    if t == "AT_LEAST":
        return count(p["region"]) >= p["count"]
    if t == "AT_MOST":
        return count(p["region"]) <= p["count"]
    if t == "PARITY":
        return count(p["region"]) % 2 == (p["parity"] == "ODD")
    x, y = count(p["region1"]), count(p["region2"])
    return {"GT": x > y, "GTE": x >= y, "LT": x < y, "LTE": x <= y, "EQ": x == y}[p["operator"]]


class FakeMapper:
    def __init__(self):
        self.cell_to_var: dict[str, int] = {}

    def get_var(self, cell_id: str) -> int:
        return self.cell_to_var.setdefault(cell_id, len(self.cell_to_var) + 1)


class FakeEncoder:
    """Truth-table CNF: one clause blocking each falsifying assignment of the clue's cells."""
    def __init__(self):
        self.mapper = FakeMapper()

    def encode_clue(self, clue: dict, grid_size: int = 3) -> list[list[int]]:
        cells = clue_cells(clue, grid_size)
        out = []
        for bits in product([False, True], repeat=len(cells)):
            a = dict(zip(cells, bits))
            if not holds(clue, a, grid_size):
                out.append([-self.mapper.get_var(c) if b else self.mapper.get_var(c) for c, b in a.items()])
        return out


class BruteSolver:
    def solve(self, clauses, assumptions=None):
        cl = clauses + [[lit] for lit in (assumptions or [])]
        vs = sorted({abs(l) for c in cl for l in c})
        for bits in product([False, True], repeat=len(vs)):
            m = dict(zip(vs, bits))
            if all(any(m[abs(l)] == (l > 0) for l in c) for c in cl):
                return True, m, SolverMetrics()
        return False, None, SolverMetrics()
