"""JSON puzzle loader and validator (Member 3)."""
import json
import jsonschema

def load_puzzle(file_path: str, schema_path: str = "schemas/puzzle_schema.json") -> dict:
    """Loads and validates a puzzle JSON against schema."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # TODO [TV3]: Add validation
    return data
