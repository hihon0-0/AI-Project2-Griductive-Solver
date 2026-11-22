"""Direct semantic evaluators (Member 2)."""


def _cells_in_region(region: dict, all_cells: list[str]) -> list[str]:
    region_type = str(region.get("type", "")).upper()
    all_cells = [cell.upper() for cell in all_cells]

    if region_type == "EXPLICIT":
        return [str(cell).upper() for cell in region.get("cells", [])]
    if region_type == "ROW":
        row = int(region["row"])
        return [cell for cell in all_cells if int(cell[1:]) == row]
    if region_type == "COLUMN":
        col = str(region["col"]).upper()
        return [cell for cell in all_cells if cell.startswith(col)]
    if region_type == "NEIGHBORS":
        target = str(region["cell"]).upper()
        target_col = ord(target[0]) - ord("A")
        target_row = int(target[1:])
        return [
            cell for cell in all_cells
            if cell != target
            and abs(ord(cell[0]) - ord("A") - target_col) <= 1
            and abs(int(cell[1:]) - target_row) <= 1
        ]
    raise ValueError("Unknown region type: %s" % region.get("type"))


def evaluate_clue_semantic(
    clue_dict: dict,
    assignment: dict[str, bool],
    grid_size: int | list[str] = 3,
) -> bool:
    """Evaluate a clue directly against a complete assignment."""
    if isinstance(grid_size, int):
        if grid_size < 1:
            raise ValueError("grid_size must be positive")
        region_cells = [
            f"{chr(ord('A') + col)}{row}"
            for row in range(1, grid_size + 1)
            for col in range(grid_size)
        ]
    else:
        region_cells = [cell.upper() for cell in grid_size]

    clue_type = str(clue_dict.get("type", "")).upper()
    params = clue_dict.get("params", {})

    if clue_type == "FACT":
        target = str(params["target"]).upper()
        criminal = str(params["status"]).upper() == "CRIMINAL"
        return assignment[target] == criminal
    if clue_type == "SAME":
        target1 = str(params["target1"]).upper()
        target2 = str(params["target2"]).upper()
        return assignment[target1] == assignment[target2]
    if clue_type == "DIFFERENT":
        target1 = str(params["target1"]).upper()
        target2 = str(params["target2"]).upper()
        return assignment[target1] != assignment[target2]

    if clue_type in ("EXACTLY", "AT_LEAST", "AT_MOST", "PARITY"):
        cells = _cells_in_region(params["region"], region_cells)
        count = sum(bool(assignment[cell.upper()]) for cell in cells)
        if clue_type == "EXACTLY":
            return count == int(params["count"])
        if clue_type == "AT_LEAST":
            return count >= int(params["count"])
        if clue_type == "AT_MOST":
            return count <= int(params["count"])
        if str(params["parity"]).upper() == "EVEN":
            return count % 2 == 0
        if str(params["parity"]).upper() == "ODD":
            return count % 2 == 1
        raise ValueError("Unknown PARITY value: %s" % params["parity"])

    if clue_type == "COUNT_COMPARE":
        cells1 = _cells_in_region(params["region1"], region_cells)
        cells2 = _cells_in_region(params["region2"], region_cells)
        count1 = sum(bool(assignment[cell.upper()]) for cell in cells1)
        count2 = sum(bool(assignment[cell.upper()]) for cell in cells2)
        operator = str(params["operator"]).upper()
        comparisons = {
            "GT": count1 > count2,
            "GTE": count1 >= count2,
            "LT": count1 < count2,
            "LTE": count1 <= count2,
            "EQ": count1 == count2,
        }
        if operator not in comparisons:
            raise ValueError("Unknown COUNT_COMPARE operator: %s" % operator)
        return comparisons[operator]

    raise ValueError("Unknown clue type: %s" % clue_dict.get("type"))
