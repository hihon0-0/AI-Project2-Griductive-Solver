"""Game Engine holding complete puzzle and ground truth (Member 3)."""
from typing import Optional
from .models import PublicState

class GameEngine:
    def __init__(self, puzzle_data: dict):
        self.puzzle_data = puzzle_data
        self.size = puzzle_data["size"]
        self._hidden_solution = {c["id"]: c["hidden_status"] for c in puzzle_data["grid"]}
        self._unrevealed_clues = {c["id"]: c["clue"] for c in puzzle_data["grid"]}
        self.revealed_statuses: dict[str, str] = {}
        self.revealed_clues: dict[str, dict] = {}
        self._init_game()

    def _init_game(self):
        for cell_id in self.puzzle_data.get("initial_revealed", []):
            self.revealed_statuses[cell_id] = self._hidden_solution[cell_id]
            self.revealed_clues[cell_id] = self._unrevealed_clues[cell_id]

    def get_public_state(self) -> PublicState:
        """Returns ONLY public knowledge state. Safe to give to Agent."""
        unsolved = [c["id"] for c in self.puzzle_data["grid"] if c["id"] not in self.revealed_statuses]
        return PublicState(
            grid_size=self.size,
            revealed_verdicts=dict(self.revealed_statuses),
            revealed_clues=list(self.revealed_clues.values()),
            unsolved_cells=unsolved
        )

    def submit_verdict(self, cell_id: str, verdict: str) -> tuple[bool, str, Optional[dict]]:
        """Validates verdict against ground truth and public proofs.
        Returns: (success, message, new_clue)
        Possible messages: 'CORRECT', 'NOT_PROVABLE', 'CONTRADICTED'
        """
        # TODO [TV3]: Implement verdict processing
        pass
