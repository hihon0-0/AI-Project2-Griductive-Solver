"""Region calculation utilities (Member 3).
Handles geometric coordinates and cell regions on an N x N grid.
"""
from typing import Optional, Union

class RegionHelper:
    """Helper methods for calculating coordinates and regions on the grid."""

    COL_LETTERS = ["A", "B", "C", "D", "E"]

    @classmethod
    def parse_coord(cls, cell_id: str) -> tuple[int, int]:
        """Converts coordinate like 'C2' to 0-based (col_idx, row_idx).
        Example: 'A1' -> (0, 0), 'C2' -> (2, 1)
        """
        if not cell_id or len(cell_id) < 2:
            raise ValueError(f"Invalid cell coordinate format: '{cell_id}'")
        col_char = cell_id[0].upper()
        row_str = cell_id[1:]

        if col_char not in cls.COL_LETTERS:
            raise ValueError(f"Invalid column letter: '{col_char}' in '{cell_id}'")
        
        try:
            row_num = int(row_str)
        except ValueError:
            raise ValueError(f"Invalid row number: '{row_str}' in '{cell_id}'")

        col_idx = cls.COL_LETTERS.index(col_char)
        row_idx = row_num - 1 # 1-based to 0-based
        return col_idx, row_idx

    @classmethod
    def to_coord(cls, col_idx: int, row_idx: int) -> str:
        """Converts 0-based (col_idx, row_idx) back to coordinate string like 'C2'."""
        if not (0 <= col_idx < len(cls.COL_LETTERS)):
            raise ValueError(f"col_idx out of range: {col_idx}")
        if row_idx < 0:
            raise ValueError(f"row_idx must be non-negative: {row_idx}")
        return f"{cls.COL_LETTERS[col_idx]}{row_idx + 1}"

    @classmethod
    def is_valid_coord(cls, cell_id: str, size: int) -> bool:
        """Checks if cell_id is within the bounds of an N x N grid."""
        try:
            col_idx, row_idx = cls.parse_coord(cell_id)
            return 0 <= col_idx < size and 0 <= row_idx < size
        except ValueError:
            return False

    @classmethod
    def get_all_cells(cls, size: int) -> list[str]:
        """Returns all cells in row-major order: A1, B1, C1, A2, B2, ..."""
        cells = []
        for r in range(size):
            for c in range(size):
                cells.append(cls.to_coord(c, r))
        return cells

    @classmethod
    def get_row_cells(cls, row: int, size: int) -> list[str]:
        """Returns all cells in a given 1-based row number.
        Example: row=1, size=3 -> ['A1', 'B1', 'C1']
        """
        if not (1 <= row <= size):
            raise ValueError(f"Row {row} is out of bounds for size {size}")
        r_idx = row - 1
        return [cls.to_coord(c, r_idx) for c in range(size)]

    @classmethod
    def get_col_cells(cls, col: str, size: int) -> list[str]:
        """Returns all cells in a given column letter.
        Example: col='B', size=3 -> ['B1', 'B2', 'B3']
        """
        col_char = col.upper()
        if col_char not in cls.COL_LETTERS:
            raise ValueError(f"Invalid column letter: {col}")
        c_idx = cls.COL_LETTERS.index(col_char)
        if not (0 <= c_idx < size):
            raise ValueError(f"Column '{col}' is out of bounds for size {size}")
        return [cls.to_coord(c_idx, r) for r in range(size)]

    @classmethod
    def get_neighbors(cls, cell_id: str, size: int) -> list[str]:
        """Returns the 8 neighbors of cell_id (horizontal, vertical, diagonal),
        excluding cell_id itself, sorted in canonical row-major order.
        Interior cell has 8, edge has 5, corner has 3.
        """
        col_idx, row_idx = cls.parse_coord(cell_id)
        if not (0 <= col_idx < size and 0 <= row_idx < size):
            raise ValueError(f"Cell '{cell_id}' is out of bounds for size {size}")

        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = row_idx + dr
                nc = col_idx + dc
                if 0 <= nr < size and 0 <= nc < size:
                    neighbors.append(cls.to_coord(nc, nr))

        return cls.sort_cells(neighbors)

    @classmethod
    def sort_cells(cls, cells: list[str]) -> list[str]:
        """Sorts cell coordinates in canonical row-major order (A1, B1, ..., A2, B2, ...)."""
        def sort_key(c_id: str):
            c_idx, r_idx = cls.parse_coord(c_id)
            return (r_idx, c_idx)
        return sorted(list(set(cells)), key=sort_key)

    @classmethod
    def resolve_region(cls, region_dict: dict, size: int) -> list[str]:
        """Resolves a Region dictionary from JSON into a sorted list of cell IDs.
        Supported region types:
        - 'ROW': {'type': 'ROW', 'row': 1}
        - 'COLUMN': {'type': 'COLUMN', 'col': 'B'}
        - 'NEIGHBORS': {'type': 'NEIGHBORS', 'cell': 'B2'}
        - 'EXPLICIT': {'type': 'EXPLICIT', 'cells': ['A1', 'C2']}
        """
        if not isinstance(region_dict, dict) or "type" not in region_dict:
            raise ValueError(f"Invalid region definition: {region_dict}")

        rtype = region_dict["type"].upper()

        if rtype == "ROW":
            row = region_dict.get("row")
            if row is None:
                raise ValueError("Missing 'row' parameter in ROW region")
            return cls.get_row_cells(int(row), size)

        elif rtype == "COLUMN":
            col = region_dict.get("col")
            if not col:
                raise ValueError("Missing 'col' parameter in COLUMN region")
            return cls.get_col_cells(str(col), size)

        elif rtype == "NEIGHBORS":
            cell = region_dict.get("cell")
            if not cell:
                raise ValueError("Missing 'cell' parameter in NEIGHBORS region")
            return cls.get_neighbors(str(cell), size)

        elif rtype == "EXPLICIT":
            cells = region_dict.get("cells", [])
            if not isinstance(cells, list):
                raise ValueError("EXPLICIT region 'cells' must be a list")
            for c in cells:
                if not cls.is_valid_coord(c, size):
                    raise ValueError(f"Cell '{c}' in EXPLICIT region is out of bounds for size {size}")
            return cls.sort_cells(cells)

        else:
            raise ValueError(f"Unsupported region type: '{rtype}'")
