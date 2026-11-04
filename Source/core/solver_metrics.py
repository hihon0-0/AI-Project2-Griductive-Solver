"""Metrics tracking for DPLL solver (Section 4.3 & 4.5)."""
from dataclasses import dataclass, field
import time

@dataclass
class SolverMetrics:
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime: float = 0.0

    def reset(self):
        self.decisions = 0
        self.propagations = 0
        self.backtracks = 0
        self.runtime = 0.0
