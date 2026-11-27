"""CNF Encoder for clue templates (Member 2).

Cell variables are positive integers. Auxiliary variables for cardinality
constraints use numbers starting at 1000.
"""

from itertools import combinations

from .clue_types import ClueType


class VariableMapper:
    """Manages deterministic bidirectional mapping between cells and variables."""

    def __init__(self, grid_size: int | None = None):
        self.cell_to_var: dict[str, int] = {}
        self.var_to_cell: dict[int, str] = {}
        self.grid_size = grid_size
        self._next_aux_var = 1000

    def get_var(self, cell_id: str) -> int:
        cell_id = cell_id.upper()
        if not cell_id:
            raise ValueError("cell_id cannot be empty")
        if cell_id not in self.cell_to_var:
            if len(cell_id) < 2 or not cell_id[0].isalpha() or not cell_id[1:].isdigit():
                raise ValueError("Invalid cell identifier: %s" % cell_id)

            col = ord(cell_id[0]) - ord("A")
            row = int(cell_id[1:])
            if col < 0 or row < 1:
                raise ValueError("Invalid cell identifier: %s" % cell_id)

            variable = col * 5 + row
            if variable in self.var_to_cell:
                existing = self.var_to_cell[variable]
                if existing != cell_id:
                    raise ValueError("Cell variable collision: %s and %s" % (existing, cell_id))
            self.cell_to_var[cell_id] = variable
            self.var_to_cell[variable] = cell_id
        return self.cell_to_var[cell_id]

    def get_cell(self, var_id: int) -> str:
        """Return the cell coordinate associated with a SAT variable."""
        return self.var_to_cell.get(var_id, "")

    def set_grid_size(self, grid_size: int) -> None:
        if grid_size < 1:
            raise ValueError("grid_size must be positive")
        self.grid_size = grid_size

    def get_aux_var(self) -> int:
        variable = self._next_aux_var
        self._next_aux_var += 1
        return variable

    def new_aux_var(self) -> int:
        """Compatibility alias for get_aux_var."""
        return self.get_aux_var()

    def register_grid(self, cell_ids: list[str]) -> None:
        for cell_id in cell_ids:
            self.get_var(cell_id)

    @property
    def main_variable_count(self) -> int:
        return len(self.cell_to_var)

    @property
    def auxiliary_variable_count(self) -> int:
        return self._next_aux_var - 1000


class CNFEncoder:
    def __init__(self, var_mapper: VariableMapper, grid_size: int | None = None):
        self.mapper = var_mapper
        if grid_size is not None:
            self.mapper.set_grid_size(grid_size)

    def _region_cells(self, region: dict, clue_params: dict | None = None) -> list[str]:
        region_type = str(region.get("type", "")).upper()

        if region_type == "EXPLICIT":
            return [str(cell).upper() for cell in region.get("cells", [])]

        size = self.mapper.grid_size
        if size is None:
            known = list(self.mapper.cell_to_var)
            if clue_params:
                for key in ("target", "target1", "target2"):
                    value = clue_params.get(key)
                    if isinstance(value, str):
                        known.append(value.upper())
            if known:
                size = max(
                    max(ord(cell[0]) - ord("A") + 1, int(cell[1:]))
                    for cell in known
                    if len(cell) >= 2 and cell[0].isalpha() and cell[1:].isdigit()
                )
            else:
                size = 5

        if region_type == "ROW":
            row = int(region["row"])
            return ["%s%d" % (chr(ord("A") + col), row) for col in range(size)]

        if region_type == "COLUMN":
            col = str(region["col"]).upper()
            return ["%s%d" % (col, row) for row in range(1, size + 1)]

        if region_type == "NEIGHBORS":
            cell_id = str(region["cell"]).upper()
            col = ord(cell_id[0]) - ord("A")
            row = int(cell_id[1:]) - 1
            return [
                "%s%d" % (chr(ord("A") + other_col), other_row + 1)
                for other_row in range(max(0, row - 1), min(size, row + 2))
                for other_col in range(max(0, col - 1), min(size, col + 2))
                if not (other_row == row and other_col == col)
            ]

        raise ValueError("Unknown region type: %s" % region.get("type"))

    def _at_most(self, literals: list[int], limit: int) -> list[list[int]]:
        n = len(literals)
        if limit < 0:
            return [[]]
        if limit >= n:
            return []
        return [
            [-literal for literal in subset]
            for subset in combinations(literals, limit + 1)
        ]

    def _at_least(self, literals: list[int], limit: int) -> list[list[int]]:
        if limit <= 0:
            return []
        if limit > len(literals):
            return [[]]
        return [
            [literal for literal in subset]
            for subset in combinations(literals, len(literals) - limit + 1)
        ]

    def _exactly(self, literals: list[int], count: int) -> list[list[int]]:
        if count < 0 or count > len(literals):
            return [[]]
        clauses = self._at_most(literals, count)
        clauses.extend(self._at_least(literals, count))
        return clauses

    def _conditional(self, clauses: list[list[int]], selector: int) -> list[list[int]]:
        return [[-selector] + clause for clause in clauses]

    def encode_clue(
        self,
        clue_dict: dict,
        grid_size: int | None = None,
    ) -> list[list[int]]:
        """Convert one clue to CNF clauses."""
        if grid_size is not None:
            self.mapper.set_grid_size(grid_size)

        clue_type = str(clue_dict.get("type", "")).upper()
        params = clue_dict.get("params", {})
        clauses: list[list[int]] = []

        if clue_type == ClueType.FACT.value:
            target = str(params["target"]).upper()
            status = str(params["status"]).upper()
            value = status == "CRIMINAL"
            literal = self.mapper.get_var(target)
            clauses.append([literal if value else -literal])

        elif clue_type in (ClueType.SAME.value, ClueType.DIFFERENT.value):
            target1 = self.mapper.get_var(str(params["target1"]).upper())
            target2 = self.mapper.get_var(str(params["target2"]).upper())
            if clue_type == ClueType.SAME.value:
                clauses.extend([
                    [-target1, target2],
                    [target1, -target2],
                ])
            else:
                clauses.extend([
                    [target1, target2],
                    [-target1, -target2],
                ])

        elif clue_type in (
            ClueType.EXACTLY.value,
            ClueType.AT_LEAST.value,
            ClueType.AT_MOST.value,
            ClueType.PARITY.value,
        ):
            region = params["region"]
            literals = [
                self.mapper.get_var(cell)
                for cell in self._region_cells(region, params)
            ]

            if clue_type == ClueType.EXACTLY.value:
                clauses.extend(self._exactly(literals, int(params["count"])))
            elif clue_type == ClueType.AT_LEAST.value:
                clauses.extend(self._at_least(literals, int(params["count"])))
            elif clue_type == ClueType.AT_MOST.value:
                clauses.extend(self._at_most(literals, int(params["count"])))
            else:
                parity = str(params["parity"]).upper()
                valid_counts = [
                    count for count in range(len(literals) + 1)
                    if (count % 2 == 0) == (parity == "EVEN")
                ]
                choices = []
                for count in valid_counts:
                    choice = self.mapper.get_aux_var()
                    choices.append(choice)
                    clauses.extend(self._conditional(
                        self._exactly(literals, count), choice
                    ))
                if not choices:
                    clauses.append([])
                else:
                    clauses.append(choices)

        elif clue_type == ClueType.COUNT_COMPARE.value:
            region1 = params["region1"]
            region2 = params["region2"]
            literals1 = [
                self.mapper.get_var(cell)
                for cell in self._region_cells(region1, params)
            ]
            literals2 = [
                self.mapper.get_var(cell)
                for cell in self._region_cells(region2, params)
            ]

            operator = str(params["operator"]).upper()
            choices: list[int] = []
            for count1 in range(len(literals1) + 1):
                for count2 in range(len(literals2) + 1):
                    valid = {
                        "GT": count1 > count2,
                        "GTE": count1 >= count2,
                        "LT": count1 < count2,
                        "LTE": count1 <= count2,
                        "EQ": count1 == count2,
                    }.get(operator)
                    if valid is None:
                        raise ValueError("Unknown COUNT_COMPARE operator: %s" % operator)
                    if not valid:
                        continue

                    choice = self.mapper.get_aux_var()
                    choices.append(choice)
                    clauses.extend(self._conditional(
                        self._exactly(literals1, count1), choice
                    ))
                    clauses.extend(self._conditional(
                        self._exactly(literals2, count2), choice
                    ))

            if not choices:
                clauses.append([])
            else:
                clauses.append(choices)
        else:
            raise ValueError("Unknown clue type: %s" % clue_dict.get("type"))

        return clauses

    def encode_puzzle(self, puzzle_data: dict) -> list[list[int]]:
        grid = puzzle_data.get("grid", [])
        cell_ids = [str(cell["id"]).upper() for cell in grid]
        self.mapper.register_grid(cell_ids)
        if puzzle_data.get("size") is not None:
            self.mapper.set_grid_size(int(puzzle_data["size"]))

        clauses: list[list[int]] = []
        for cell in grid:
            if "clue" in cell:
                clauses.extend(self.encode_clue(cell["clue"]))
        return clauses
