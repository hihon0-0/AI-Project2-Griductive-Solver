"""Hint generator identifying forced cells (Member 4)."""
from typing import Optional

from ..engine.models import PublicState
from .agent import CRIMINAL, INCONSISTENT, INNOCENT, STUCK, DeductiveAgent, row_major_key


def proof_clues(agent: DeductiveAgent, state: PublicState, cell: str, verdict: str) -> list[str]:
    """Minimal set of revealed clues that, with the proved verdicts, still forces `verdict` on `cell`.
    Deletion-based: drop one clue at a time and keep the drop if the refutation stays UNSAT."""
    v = agent.mapper.get_var(cell)
    kb = agent.build_kb(state)
    facts = kb[len(kb) - len(state.revealed_verdicts):]   # build_kb appends verdict units last
    refute = [-v] if verdict == CRIMINAL else [v]
    keep = [clue for clue in state.revealed_clues]
    for clue in list(keep):
        rest = [c for c in keep if c is not clue]
        cnf = [cl for c in rest for cl in agent.encode_clue(c)] + facts
        if not agent.solver.solve(cnf, refute)[0]:   # not counted in the solve metrics
            keep = rest
    return [c["id"] for c in keep]


def get_hint(public_state: PublicState,
             agent: Optional[DeductiveAgent] = None) -> Optional[tuple[str, str, list[str]]]:
    """The provable cell that needs the fewest clues (ties: row-major), without looking at hidden state.
    Returns (cell_id, forced_verdict, clue_ids) or None, setting agent.status to STUCK / INCONSISTENT."""
    agent = agent or DeductiveAgent()
    verdicts = agent.classify(public_state)
    if INCONSISTENT in verdicts.values():
        agent.status = INCONSISTENT
        return None
    forced = [(c, v, proof_clues(agent, public_state, c, v))
              for c, v in verdicts.items() if v in (CRIMINAL, INNOCENT)]
    if not forced:
        agent.status = STUCK
        return None
    return min(forced, key=lambda f: (len(f[2]), row_major_key(f[0])))
