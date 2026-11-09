"""Data models for characters, cells, and public states (Member 3)."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any

class VerdictStatus(str, Enum):
    """Possible outcomes of a submitted verdict."""
    CORRECT = "CORRECT"
    NOT_PROVABLE = "NOT_PROVABLE"
    CONTRADICTED = "CONTRADICTED"
    ALREADY_SOLVED = "ALREADY_SOLVED"
    INVALID_CELL = "INVALID_CELL"

class CharacterStatus(str, Enum):
    """Character status."""
    CRIMINAL = "CRIMINAL"
    INNOCENT = "INNOCENT"

@dataclass
class Character:
    name: str
    occupation: str
    avatar: Optional[str] = None

@dataclass
class Clue:
    id: str
    type: str
    params: dict[str, Any]
    description: str

@dataclass
class Cell:
    id: str
    row: int
    col: str
    character: Character
    hidden_status: str
    clue: Clue

@dataclass
class VerdictResult:
    is_valid: bool
    status_code: VerdictStatus
    revealed_clue: Optional[dict[str, Any]] = None
    message: str = ""

@dataclass
class PublicState:
    """Contains ONLY public knowledge state. Safe to give to LogicAgent and GUI."""
    grid_size: int
    revealed_verdicts: dict[str, str] = field(default_factory=dict) # e.g. {'A1': 'INNOCENT'}
    revealed_clues: list[dict[str, Any]] = field(default_factory=list)
    unsolved_cells: list[str] = field(default_factory=list)

    @property
    def is_solved(self) -> bool:
        """Returns True if all cells on the board have been revealed."""
        return len(self.unsolved_cells) == 0

    @property
    def solved_count(self) -> int:
        return len(self.revealed_verdicts)
