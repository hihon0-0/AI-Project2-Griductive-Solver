"""Definitions of Clue and Region data classes (Member 2)."""
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional

class ClueType(str, Enum):
    # 6 Core templates
    FACT = "FACT"
    SAME = "SAME"
    DIFFERENT = "DIFFERENT"
    EXACTLY = "EXACTLY"
    AT_LEAST = "AT_LEAST"
    AT_MOST = "AT_MOST"
    # 2 Extension templates
    PARITY = "PARITY"
    COUNT_COMPARE = "COUNT_COMPARE"

class RegionType(str, Enum):
    ROW = "ROW"
    COLUMN = "COLUMN"
    NEIGHBORS = "NEIGHBORS"
    EXPLICIT = "EXPLICIT"
