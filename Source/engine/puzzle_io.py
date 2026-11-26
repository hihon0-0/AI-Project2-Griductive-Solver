"""JSON puzzle loader, saver, and schema validator (Member 3)."""
import json
import os
from typing import Optional
import jsonschema

from .region_helper import RegionHelper
from .models import Cell, Character, Clue

DEFAULT_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "schemas",
    "puzzle_schema.json"
)

def load_puzzle(file_path: str, schema_path: Optional[str] = None) -> dict:
    """Loads a puzzle JSON file and validates it against the schema.
    Also verifies grid dimensions and cell coordinates.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Puzzle file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        puzzle_data = json.load(f)

    # Use default schema path if not specified
    target_schema_path = schema_path or DEFAULT_SCHEMA_PATH
    if os.path.exists(target_schema_path):
        with open(target_schema_path, "r", encoding="utf-8") as sf:
            schema = json.load(sf)
        try:
            jsonschema.validate(instance=puzzle_data, schema=schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Schema validation error in {file_path}: {e.message}") from e

    # Additional semantic validation
    size = puzzle_data["size"]
    grid = puzzle_data["grid"]
    if len(grid) != size * size:
        raise ValueError(f"Grid size mismatch: expected {size * size} cells, got {len(grid)}")

    seen_ids = set()
    for cell_entry in grid:
        cid = cell_entry["id"]
        if cid in seen_ids:
            raise ValueError(f"Duplicate cell id found: '{cid}'")
        seen_ids.add(cid)

        if not RegionHelper.is_valid_coord(cid, size):
            raise ValueError(f"Cell '{cid}' is out of bounds for size {size}")

    for init_id in puzzle_data.get("initial_revealed", []):
        if init_id not in seen_ids:
            raise ValueError(f"Initial revealed cell '{init_id}' does not exist in grid")

    for cell_entry in grid:
        cid, clue = cell_entry["id"], cell_entry["clue"]
        # GUI tìm clue của thẻ và agent cache CNF theo id này, nên id khác dạng sẽ làm sai cả hai
        if clue["id"] != f"clue_{cid}":
            raise ValueError(f"Cell '{cid}': clue id must be 'clue_{cid}', got '{clue['id']}'")
        try:
            _check_clue_params(clue["type"], clue["params"], size)
        except KeyError as e:
            raise ValueError(f"{clue['id']}: missing parameter {e}") from e
        except ValueError as e:
            raise ValueError(f"{clue['id']}: {e}") from e

    return puzzle_data

def _check_clue_params(clue_type: str, params: dict, size: int) -> None:
    """Parameters and referenced regions of one clue. The schema only checks their format."""
    def check_cell(cell_id: str) -> None:
        if not RegionHelper.is_valid_coord(cell_id, size):
            raise ValueError(f"cell '{cell_id}' is not on the {size}x{size} board")

    def region_size(name: str) -> int:
        region = params[name]
        if region["type"] == "EXPLICIT" and len(set(region["cells"])) != len(region["cells"]):
            raise ValueError("EXPLICIT region has duplicate cells")
        return len(RegionHelper.resolve_region(region, size))

    if clue_type == "FACT":
        check_cell(params["target"])
        params["status"]
    elif clue_type in ("SAME", "DIFFERENT"):
        check_cell(params["target1"])
        check_cell(params["target2"])
    elif clue_type in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        cells, count = region_size("region"), params["count"]
        if not 0 <= count <= cells:
            raise ValueError(f"count {count} is outside 0..{cells}")
    elif clue_type == "PARITY":
        region_size("region")
        params["parity"]
    elif clue_type == "COUNT_COMPARE":
        region_size("region1")
        region_size("region2")
        params["operator"]

def save_puzzle(puzzle_data: dict, file_path: str, schema_path: Optional[str] = None) -> None:
    """Saves puzzle data to JSON after verifying schema."""
    target_schema_path = schema_path or DEFAULT_SCHEMA_PATH
    if os.path.exists(target_schema_path):
        with open(target_schema_path, "r", encoding="utf-8") as sf:
            schema = json.load(sf)
        jsonschema.validate(instance=puzzle_data, schema=schema)

    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(puzzle_data, f, indent=2, ensure_ascii=False)

def parse_puzzle_cells(puzzle_data: dict) -> dict[str, Cell]:
    """Converts puzzle grid entries into a dictionary mapping cell_id -> Cell model."""
    cells = {}
    for c in puzzle_data["grid"]:
        char_obj = Character(
            name=c["character"]["name"],
            occupation=c["character"]["occupation"],
            avatar=c["character"].get("avatar")
        )
        clue_obj = Clue(
            id=c["clue"]["id"],
            type=c["clue"]["type"],
            params=c["clue"]["params"],
            description=c["clue"]["description"]
        )
        cell_obj = Cell(
            id=c["id"],
            row=c["row"],
            col=c["col"],
            character=char_obj,
            hidden_status=c["hidden_status"],
            clue=clue_obj
        )
        cells[c["id"]] = cell_obj
    return cells
