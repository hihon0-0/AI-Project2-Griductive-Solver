"""Deduction trace logger (Member 4)."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DeductionStep:
    step_number: int
    cell_id: str
    verdict: str                      # 'CRIMINAL' | 'INNOCENT'
    forced_by_clue_ids: list[str]     # revealed clues that mention this cell
    new_clue: Optional[dict]          # clue returned by the engine after the reveal
    active_clue_ids: list[str] = field(default_factory=list)  # every clue in KB_t
    sat_queries: int = 0              # SAT calls spent to find this step

    def __str__(self) -> str:
        new_id = self.new_clue["id"] if self.new_clue else "-"
        return (f"Step {self.step_number}: {self.cell_id} = {self.verdict} | "
                f"forced by {self.forced_by_clue_ids} | SAT queries {self.sat_queries} | "
                f"KB clues {len(self.active_clue_ids)} | new clue {new_id}")
