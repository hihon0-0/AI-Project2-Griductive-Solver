"""Deduction trace logger (Member 4)."""
from dataclasses import dataclass
from typing import Any

@dataclass
class DeductionStep:
    step_number: int
    cell_id: str
    verdict: str
    forced_by_clue_ids: list[str]
    new_clue: dict
