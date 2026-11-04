"""Data models for characters, cells, and public states (Member 3)."""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Character:
    name: str
    occupation: str
    avatar: Optional[str] = None

@dataclass
class PublicState:
    grid_size: int
    revealed_verdicts: dict[str, str] = field(default_factory=dict) # e.g. {'A1': 'CRIMINAL'}
    revealed_clues: list[dict] = field(default_factory=list)
    unsolved_cells: list[str] = field(default_factory=list)
