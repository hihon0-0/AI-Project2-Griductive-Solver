"""Benchmark the deductive agent on the 6 standard puzzles (Project 2, section 4.5).

Run from the repo root:  python tools/benchmark.py
Writes benchmark_results.csv and prints a Markdown table.
"""
import csv
import glob
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from Source.agent.agent import DeductiveAgent
from Source.agent.uniqueness import check_puzzle_uniqueness
from Source.engine.engine import GameEngine
from Source.engine.puzzle_io import load_puzzle

FIELDS = ["puzzle", "size", "primary_vars", "aux_vars", "clauses", "sat_calls", "decisions",
          "propagations", "backtracks", "steps", "runtime_ms", "solver_ms", "unique", "status"]


def run(path: str) -> dict:
    puzzle = load_puzzle(path)
    engine = GameEngine(puzzle)
    agent = DeductiveAgent()
    t0 = time.perf_counter()
    try:
        steps = agent.solve(engine)
        status = agent.status or "ERROR"
    except Exception as exc:  # report failures instead of dropping the puzzle
        steps, status = agent.trace, f"ERROR: {exc}"
    wall = (time.perf_counter() - t0) * 1000
    n = puzzle["size"]
    m = agent.metrics
    try:
        unique = check_puzzle_uniqueness(puzzle)
    except Exception as exc:
        unique = f"ERROR: {exc}"
    return {
        "puzzle": os.path.splitext(os.path.basename(path))[0], "size": f"{n}x{n}",
        "primary_vars": agent.mapper.main_variable_count,
        "aux_vars": agent.mapper.auxiliary_variable_count,
        "clauses": sum(len(v) for v in agent._clue_cache.values()),
        "sat_calls": agent.sat_calls, "decisions": m.decisions, "propagations": m.propagations,
        "backtracks": m.backtracks, "steps": len(steps), "runtime_ms": round(wall, 2),
        "solver_ms": round(m.runtime * 1000, 2), "unique": unique, "status": status,
    }


def main() -> None:
    files = sorted(glob.glob(os.path.join(ROOT, "data", "puzzle_*.json")))
    rows = [run(f) for f in files]
    out = os.path.join(ROOT, "benchmark_results.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print("| " + " | ".join(FIELDS) + " |")
    print("|" + "---|" * len(FIELDS))
    for r in rows:
        print("| " + " | ".join(str(r[k]) for k in FIELDS) + " |")
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
