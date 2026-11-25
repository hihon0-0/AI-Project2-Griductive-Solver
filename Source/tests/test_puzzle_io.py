"""Unit tests for puzzle_io (TV3)."""
import os
import glob
import json
import tempfile
import pytest
import jsonschema
from Source.engine.puzzle_io import load_puzzle, save_puzzle, parse_puzzle_cells

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data"
)
SAMPLE_PATH = os.path.join(DATA_DIR, "sample_3x3.json")

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
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(puzzle_corrupt, tmp)
        tmp_name = tmp.name

    try:
        with pytest.raises(ValueError, match="Grid size mismatch"):
            load_puzzle(tmp_name)
    finally:
        os.remove(tmp_name)

def test_save_puzzle_and_reload():
    puzzle = load_puzzle(SAMPLE_PATH)
    with tempfile.TemporaryDirectory() as tmp_dir:
        save_path = os.path.join(tmp_dir, "saved_puzzle.json")
        save_puzzle(puzzle, save_path)
        assert os.path.exists(save_path)

        reloaded = load_puzzle(save_path)
        assert reloaded["puzzle_id"] == puzzle["puzzle_id"]
        assert reloaded["size"] == puzzle["size"]
        assert len(reloaded["grid"]) == len(puzzle["grid"])

def test_save_puzzle_invalid_schema_fails():
    invalid_puzzle = {"title": "Bad Puzzle"}
    with tempfile.TemporaryDirectory() as tmp_dir:
        save_path = os.path.join(tmp_dir, "bad.json")
        with pytest.raises(jsonschema.ValidationError):
            save_puzzle(invalid_puzzle, save_path)

def test_all_standard_datasets_valid():
    """Verify all 6 official benchmark puzzles strictly validate against schema and semantics."""
    puzzle_files = glob.glob(os.path.join(DATA_DIR, "puzzle_*.json"))
    assert len(puzzle_files) >= 6, f"Expected at least 6 standard puzzle files, found {len(puzzle_files)}"

    for file_path in puzzle_files:
        data = load_puzzle(file_path)
        assert "puzzle_id" in data
        assert data["size"] in (3, 4, 5)
        assert len(data["grid"]) == data["size"] * data["size"]
        assert len(data["initial_revealed"]) >= 1

def test_duplicate_cell_id_raises():
    puzzle = load_puzzle(SAMPLE_PATH)
    puzzle_corrupt = dict(puzzle)
    grid_copy = [dict(c) for c in puzzle["grid"]]
    grid_copy[1]["id"] = grid_copy[0]["id"] # Duplicate id
    puzzle_corrupt["grid"] = grid_copy

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(puzzle_corrupt, tmp)
        tmp_name = tmp.name

    try:
        with pytest.raises(ValueError, match="Duplicate cell id found"):
            load_puzzle(tmp_name)
    finally:
        os.remove(tmp_name)

def test_out_of_bounds_coordinate_raises():
    puzzle = load_puzzle(SAMPLE_PATH)
    puzzle_corrupt = dict(puzzle)
    grid_copy = [dict(c) for c in puzzle["grid"]]
    # D1 matches schema regex ^[A-E][1-5]$ but is out of bounds for a 3x3 grid
    grid_copy[0]["id"] = "D1"
    puzzle_corrupt["grid"] = grid_copy

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(puzzle_corrupt, tmp)
        tmp_name = tmp.name

    try:
        with pytest.raises(ValueError, match="is out of bounds"):
            load_puzzle(tmp_name)
    finally:
        os.remove(tmp_name)

def test_missing_initial_revealed_raises():
    puzzle = load_puzzle(SAMPLE_PATH)
    puzzle_corrupt = dict(puzzle)
    # D1 passes regex ^[A-E][1-5]$ but does not exist in 3x3 grid cells
    puzzle_corrupt["initial_revealed"] = ["D1"]

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(puzzle_corrupt, tmp)
        tmp_name = tmp.name

    try:
        with pytest.raises(ValueError, match="does not exist in grid"):
            load_puzzle(tmp_name)
    finally:
        os.remove(tmp_name)

