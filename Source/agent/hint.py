"""Hint generator identifying forced cells (Member 4)."""
from typing import Optional

from ..engine.models import PublicState
from .agent import DeductiveAgent


def get_hint(public_state: PublicState, agent: Optional[DeductiveAgent] = None) -> Optional[tuple[str, str]]:
    """Identifies the next provable cell and verdict without looking at hidden state.
    Returns (cell_id, forced_verdict) or None. The GUI can highlight the related clues
    with agent.clues_mentioning(public_state, cell_id)."""
    agent = agent or DeductiveAgent()
    found = agent.find_forced(public_state)
    return found[:2] if found else None
