"""Metrics tracking for DPLL solver (Section 4.3 & 4.5).

Records quantitative performance indicators for every solver invocation:
  - decisions   : Number of branching choices (variable picked + polarity)
  - propagations: Number of literals forced by unit propagation
  - backtracks  : Number of times the solver undid a decision
  - conflicts   : Number of empty-clause conflicts encountered
  - runtime     : Wall-clock time (seconds) of the last solve() call

Usage:
    metrics = SolverMetrics()
    metrics.record_decision()
    ...
    print(metrics.summary())
"""

from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class SolverMetrics:
    """Accumulates DPLL solver performance counters."""

    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    conflicts: int = 0
    runtime: float = 0.0
    sat_calls: int = 0

    # ---- Internal timing helpers (not part of public API) ----
    _start_time: float = field(default=0.0, repr=False)

    # ------------------------------------------------------------------ #
    #  Recording helpers                                                   #
    # ------------------------------------------------------------------ #

    def record_decision(self) -> None:
        """Call each time the solver makes a branching choice."""
        self.decisions += 1

    def record_propagation(self, count: int = 1) -> None:
        """Call for each literal forced by unit propagation."""
        self.propagations += count

    def record_backtrack(self) -> None:
        """Call each time the solver backtracks from a failed branch."""
        self.backtracks += 1

    def record_conflict(self) -> None:
        """Call when an empty clause (conflict) is detected."""
        self.conflicts += 1

    def add(self, other: SolverMetrics) -> None:
        """Accumulate metrics from another run."""
        self.decisions += other.decisions
        self.propagations += other.propagations
        self.backtracks += other.backtracks
        self.conflicts += other.conflicts
        self.runtime += other.runtime
        self.sat_calls += other.sat_calls if other.sat_calls > 0 else 1

    # ------------------------------------------------------------------ #
    #  Timer                                                               #
    # ------------------------------------------------------------------ #

    def start_timer(self) -> None:
        """Begin timing a solve call."""
        self._start_time = time.perf_counter()

    def stop_timer(self) -> None:
        """Stop the timer and accumulate elapsed time into *runtime*."""
        if self._start_time > 0:
            self.runtime = time.perf_counter() - self._start_time
            self._start_time = 0.0

    # ------------------------------------------------------------------ #
    #  Reset / display                                                     #
    # ------------------------------------------------------------------ #

    def reset(self) -> None:
        """Reset all counters and runtime to zero."""
        self.decisions = 0
        self.propagations = 0
        self.backtracks = 0
        self.conflicts = 0
        self.runtime = 0.0
        self.sat_calls = 0
        self._start_time = 0.0

    def summary(self) -> str:
        """Return a human-readable multi-line summary."""
        return (
            f"SolverMetrics(\n"
            f"  sat_calls    = {self.sat_calls}\n"
            f"  decisions    = {self.decisions}\n"
            f"  propagations = {self.propagations}\n"
            f"  backtracks   = {self.backtracks}\n"
            f"  conflicts    = {self.conflicts}\n"
            f"  runtime      = {self.runtime:.6f} s\n"
            f")"
        )

    def __str__(self) -> str:
        return self.summary()
