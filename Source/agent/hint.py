"""Hint generator identifying forced cells (Member 4)."""
from typing import Optional

from ..engine.models import PublicState
from .agent import DeductiveAgent


def get_hint(public_state: PublicState,
             agent: Optional[DeductiveAgent] = None) -> Optional[tuple[str, str, list[str]]]:
    """The cell Step would solve next, without looking at hidden state: (cell_id, forced_verdict, clue_ids),
    or None with agent.status set to STUCK / INCONSISTENT."""
    agent = agent or DeductiveAgent()
    found = agent.find_forced(public_state)
    return (found[0], found[1], found[3]) if found else None
