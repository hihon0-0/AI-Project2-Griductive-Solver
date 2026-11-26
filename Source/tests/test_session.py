"""GameSession metrics must describe the same work as tools/benchmark.py."""
from pathlib import Path

from Source.agent.agent import DeductiveAgent
from Source.engine.engine import GameEngine
from Source.engine.puzzle_io import load_puzzle
from Source.gui.session import GameSession

PUZZLE = str(Path(__file__).parents[2] / "data" / "puzzle_3x3_01.json")


def test_step_metrics_match_benchmark():
    session = GameSession()
    session.load(PUZZLE)
    while not session.is_solved():
        assert session.next_step().kind in ("OK", "SOLVED")
    agent = DeductiveAgent()
    agent.solve(GameEngine(load_puzzle(PUZZLE)))
    metrics = session.metrics()
    assert metrics["SAT calls"] == agent.sat_calls
    assert metrics["Propagations"] == agent.metrics.propagations


def test_manual_play_reports_cnf_size_without_solver_counts():
    session = GameSession()
    session.load(PUZZLE)
    assert session.submit("B1", "INNOCENT").accepted
    metrics = session.metrics()
    assert metrics["CNF clauses"] > 0
    assert metrics["SAT calls"] == 0
