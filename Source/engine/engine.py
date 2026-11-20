"""Game Engine holding complete puzzle, hidden solution, and unrevealed clues (Member 3).
Strictly enforces separation between private game state and public knowledge state.
"""
from typing import Optional, Callable, Any
from .models import PublicState, VerdictResult, VerdictStatus, Character
from .region_helper import RegionHelper

class GameEngine:
    """Manages the full puzzle game state, validates player/agent verdicts,
    and reveals cards progressively without leaking private information.
    """

    def __init__(self, puzzle_data: dict, entailment_verifier: Optional[Callable[[PublicState, str], str]] = None):
        """Initializes the GameEngine.
        
        Args:
            puzzle_data: Dictionary containing the validated puzzle JSON.
            entailment_verifier: Optional callback `(public_state, cell_id) -> status`
                                where status is 'CRIMINAL', 'INNOCENT', or 'UNKNOWN'.
                                When provided, enforces the strict No-Guess rule.
        """
        self.puzzle_data = puzzle_data
        self.puzzle_id = puzzle_data.get("puzzle_id", "unknown_puzzle")
        self.name = puzzle_data.get("name", "Untitled Puzzle")
        self.size = puzzle_data["size"]
        self.entailment_verifier = entailment_verifier

        # Private state: Hidden truth and unrevealed clues
        self._hidden_solution: dict[str, str] = {
            c["id"]: c["hidden_status"] for c in puzzle_data["grid"]
        }
        self._all_clues: dict[str, dict[str, Any]] = {
            c["id"]: c["clue"] for c in puzzle_data["grid"]
        }
        self._characters: dict[str, Character] = {
            c["id"]: Character(
                name=c["character"]["name"],
                occupation=c["character"]["occupation"],
                avatar=c["character"].get("avatar")
            )
            for c in puzzle_data["grid"]
        }

        # Public state: Visible to players and LogicAgent
        self.revealed_statuses: dict[str, str] = {}
        self.revealed_clues: dict[str, dict[str, Any]] = {}

        self.restart()

    def restart(self) -> None:
        """Resets the game state back to the initial revealed cards."""
        self.revealed_statuses.clear()
        self.revealed_clues.clear()

        # Reveal initial cards
        for cell_id in self.puzzle_data.get("initial_revealed", []):
            if cell_id in self._hidden_solution:
                self.revealed_statuses[cell_id] = self._hidden_solution[cell_id]
                self.revealed_clues[cell_id] = self._all_clues[cell_id]

    def get_public_state(self) -> PublicState:
        """Returns ONLY public knowledge state. Safe to give to LogicAgent and GUI."""
        all_cell_ids = [c["id"] for c in self.puzzle_data["grid"]]
        unsolved = [cid for cid in all_cell_ids if cid not in self.revealed_statuses]

        return PublicState(
            grid_size=self.size,
            revealed_verdicts=dict(self.revealed_statuses),
            revealed_clues=list(self.revealed_clues.values()),
            unsolved_cells=unsolved
        )

    def get_character_info(self, cell_id: str) -> Optional[Character]:
        """Returns character display info (name, occupation, avatar).
        Character identity is publicly visible on cards even when face-down.
        """
        return self._characters.get(cell_id)

    def is_solved(self) -> bool:
        """Returns True if all cells on the board have been proved and revealed."""
        return len(self.revealed_statuses) == len(self._hidden_solution)

    def submit_verdict(self, cell_id: str, verdict: str) -> VerdictResult:
        """Processes a submitted verdict for cell_id ('CRIMINAL' or 'INNOCENT').
        
        Rules:
        - If already revealed: reports ALREADY_SOLVED.
        - If entailment_verifier is attached:
          - If verdict is logically forced: accepts and reveals card.
          - If opposite verdict is forced: reports CONTRADICTED.
          - If neither is forced: reports NOT_PROVABLE (no guessing allowed).
        - If no verifier attached (standalone mode):
          - Verifies against hidden truth.
        """
        cell_id = cell_id.upper()
        verdict = verdict.upper()

        if cell_id not in self._hidden_solution:
            return VerdictResult(
                is_valid=False,
                status_code=VerdictStatus.INVALID_CELL,
                message=f"Cell '{cell_id}' does not exist on this {self.size}x{self.size} board."
            )

        if cell_id in self.revealed_statuses:
            return VerdictResult(
                is_valid=False,
                status_code=VerdictStatus.ALREADY_SOLVED,
                message=f"Cell '{cell_id}' has already been revealed as {self.revealed_statuses[cell_id]}."
            )

        if verdict not in ("CRIMINAL", "INNOCENT"):
            return VerdictResult(
                is_valid=False,
                status_code=VerdictStatus.NOT_PROVABLE,
                message=f"Verdict must be 'CRIMINAL' or 'INNOCENT', got '{verdict}'."
            )

        # Logic verification if verifier is connected
        if self.entailment_verifier is not None:
            public_state = self.get_public_state()
            forced_status = self.entailment_verifier(public_state, cell_id)
            
            if forced_status == verdict:
                # Entailed and correct!
                return self._accept_verdict(cell_id, verdict)
            elif forced_status in ("CRIMINAL", "INNOCENT") and forced_status != verdict:
                # Opposite is forced
                return VerdictResult(
                    is_valid=False,
                    status_code=VerdictStatus.CONTRADICTED,
                    message=f"Verdict {verdict} for cell {cell_id} is CONTRADICTED by available clues."
                )
            else:
                # Neither is forced -> Player is guessing!
                return VerdictResult(
                    is_valid=False,
                    status_code=VerdictStatus.NOT_PROVABLE,
                    message=f"Verdict {verdict} for cell {cell_id} is NOT_PROVABLE from current clues. Do not guess!"
                )
        else:
            # Standalone ground-truth verification mode
            true_status = self._hidden_solution[cell_id]
            if verdict == true_status:
                return self._accept_verdict(cell_id, verdict)
            else:
                return VerdictResult(
                    is_valid=False,
                    status_code=VerdictStatus.CONTRADICTED,
                    message=f"Verdict {verdict} for cell {cell_id} is CONTRADICTED."
                )

    def _accept_verdict(self, cell_id: str, verdict: str) -> VerdictResult:
        """Helper to record accepted verdict and reveal the card's clue."""
        self.revealed_statuses[cell_id] = verdict
        new_clue = self._all_clues[cell_id]
        self.revealed_clues[cell_id] = new_clue

        return VerdictResult(
            is_valid=True,
            status_code=VerdictStatus.CORRECT,
            revealed_clue=new_clue,
            message=f"Verdict {verdict} for {cell_id} accepted! Card flipped."
        )
