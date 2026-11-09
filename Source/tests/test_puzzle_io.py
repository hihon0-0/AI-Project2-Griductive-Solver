"""Unit tests for puzzle_io (TV3)."""
import os
import pytest
from Source.engine.puzzle_io import load_puzzle, parse_puzzle_cells

SAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "sample_3x3.json"
)

def test_load_sample_puzzle():
    puzzle = load_puzzle(SAMPLE_PATH)
    assert puzzle["puzzle_id"] == "puzzle_3x3_01"
    assert puzzle["size"] == 3
    assert len(puzzle["grid"]) == 9
    assert "A1" in puzzle["initial_revealed"]

def test_parse_puzzle_cells():
    puzzle = load_puzzle(SAMPLE_PATH)
    cells = parse_puzzle_cells(puzzle)
    assert len(cells) == 9
    assert "A1" in cells
    cell_a1 = cells["A1"]
    assert cell_a1.character.name == "Abel"
    assert cell_a1.hidden_status == "INNOCENT"
    assert cell_a1.clue.type == "SAME"

def test_invalid_puzzle_grid_size():
    puzzle = load_puzzle(SAMPLE_PATH)
    puzzle_corrupt = dict(puzzle)
    puzzle_corrupt["grid"] = puzzle["grid"][:8] # Only 8 cells for 3x3
    import tempfile, json
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(puzzle_corrupt, tmp)
        tmp_name = tmp.name

    try:
        with pytest.raises(ValueError, match="Grid size mismatch"):
            load_puzzle(tmp_name)
    finally:
        os.remove(tmp_name)
