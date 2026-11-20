"""Hint generator identifying forced cells (Member 4)."""
from typing import Optional
from ..engine.models import PublicState

def get_hint(public_state: PublicState) -> Optional[tuple[str, str]]:
    """Identifies the next provable cell and verdict without looking at hidden state.
    Returns (cell_id, forced_verdict) or None.
    """
    # TODO [TV4]: Implement hint search using DeductiveAgent
    raise NotImplementedError("TODO [TV4]: Implement get_hint in Source/agent/hint.py")
