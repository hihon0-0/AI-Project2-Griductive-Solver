"""Uniqueness checker for full clue set (Member 4).

Offline puzzle validation (not part of the agent's game loop), so it may read the full puzzle.
"""
from .agent import CRIMINAL, cell_ids


def check_puzzle_uniqueness(puzzle_data: dict, encoder=None, solver=None) -> bool:
    """Verifies that the complete clue set (+ initially revealed statuses) has EXACTLY ONE model
    over the primary variables: find a model M, block it, and the second solve must be UNSAT."""
    if encoder is None:
        from ..core.encoder import CNFEncoder, VariableMapper
        encoder = CNFEncoder(VariableMapper())
    if solver is None:
        from ..core.dpll import DPLLSolver
        solver = DPLLSolver()
    mapper, n = encoder.mapper, puzzle_data["size"]

    primary = [mapper.get_var(c) for c in cell_ids(n)]
    cells = {c["id"]: c for c in puzzle_data["grid"]}
    kb = [cl for c in puzzle_data["grid"] for cl in encoder.encode_clue(c["clue"], n)]
    for cid in puzzle_data.get("initial_revealed", []):
        v = mapper.get_var(cid)
        kb.append([v] if cells[cid]["hidden_status"] == CRIMINAL else [-v])

    is_sat, model, _ = solver.solve(kb, [])
    if not is_sat:
        return False
    if any(v not in model for v in primary):   # a primary variable no clause constrains is free
        return False
    blocking = [-v if model[v] else v for v in primary]
    is_sat, _, _ = solver.solve(kb + [blocking], [])
    return not is_sat
