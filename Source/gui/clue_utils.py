from __future__ import annotations

def parse_cell(cell_id: str) -> tuple[int, int]:
    """Chuyển 'C2' -> (row_idx=1, col_idx=2) (0-indexed)."""
    col = ord(cell_id[0].upper()) - ord('A')
    row = int(cell_id[1:]) - 1
    return row, col

def format_cell(row: int, col: int) -> str:
    """Chuyển (row_idx=1, col_idx=2) -> 'C2'."""
    return f"{chr(ord('A') + col)}{row + 1}"

def expand_region(region: dict | list, size: int) -> list[str]:
    """
    Trả về danh sách các ô trong vùng theo thứ tự hàng trước cột sau (row-major).
    Hỗ trợ: ROW, COLUMN, NEIGHBORS, EXPLICIT.
    """
    if isinstance(region, list):
        # Trường hợp EXPLICIT truyền thẳng list ô
        cells = set(region)
    else:
        rtype = region.get("type", "").upper()
        cells = set()

        if rtype == "ROW":
            r = int(region["row"]) - 1
            if 0 <= r < size:
                cells = {format_cell(r, c) for c in range(size)}

        elif rtype == "COLUMN":
            c = ord(str(region.get("col") or region.get("column")).upper()) - ord('A')
            if 0 <= c < size:
                cells = {format_cell(r, c) for r in range(size)}

        elif rtype == "NEIGHBORS":
            center = region.get("cell") or region.get("target")
            cr, cc = parse_cell(center)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        cells.add(format_cell(nr, nc))

        elif rtype == "EXPLICIT":
            cells = set(region.get("cells", []))

    # Sắp xếp hàng trước, cột sau
    return sorted(cells, key=lambda cid: parse_cell(cid))

def clue_roles(clue: dict, size: int) -> dict[str, list[str]]:
    """Phân vai các ô được nhắc tới trong clue để GUI tô màu highlight khác nhau."""
    roles: dict[str, list[str]] = {"target": [], "region": [], "region2": []}
    ctype = clue.get("type", "").upper()
    params = clue.get("params") or clue

    if ctype == "FACT":
        t = params.get("target") or params.get("cell")
        if t:
            roles["target"] = [t]
    elif ctype in ("SAME", "DIFFERENT"):
        targets = params.get("targets") or [
            params.get("target1") or params.get("cell1"),
            params.get("target2") or params.get("cell2"),
        ]
        roles["target"] = [t for t in targets if t]
    elif ctype in ("EXACTLY", "AT_LEAST", "AT_MOST", "PARITY"):
        reg = params.get("region", {})
        if isinstance(reg, dict) and reg.get("type", "").upper() == "NEIGHBORS":
            center = reg.get("cell") or reg.get("target")
            if center:
                roles["target"] = [center]
        roles["region"] = expand_region(reg, size)
    elif ctype == "COUNT_COMPARE":
        roles["region"] = expand_region(params.get("region1", {}), size)
        roles["region2"] = expand_region(params.get("region2", {}), size)

    return roles

def clue_cells(clue: dict, size: int) -> list[str]:
    """Hợp tất cả các ô liên quan đến clue."""
    roles = clue_roles(clue, size)
    all_c = set(roles["target"]) | set(roles["region"]) | set(roles["region2"])
    return sorted(all_c, key=lambda cid: parse_cell(cid))


def evaluate_clue(clue: dict, assign: dict[str, bool], size: int) -> bool:
    """
    Kiểm tra clue có đúng với phép gán `assign` (True = CRIMINAL, False = INNOCENT) không.
    Hỗ trợ cả định dạng bọc trong `params` của puzzle_schema.json.
    """
    ctype = clue.get("type", "").upper()
    params = clue.get("params") or clue

    if ctype == "FACT":
        target = params.get("target") or params.get("cell")
        status_str = str(params.get("status", params.get("verdict", "CRIMINAL"))).upper()
        expected_criminal = (status_str == "CRIMINAL")
        return assign[target] == expected_criminal

    if ctype == "SAME":
        c1, c2 = params.get("targets") or [
            params.get("target1") or params.get("cell1"),
            params.get("target2") or params.get("cell2"),
        ]
        return assign[c1] == assign[c2]

    if ctype == "DIFFERENT":
        c1, c2 = params.get("targets") or [
            params.get("target1") or params.get("cell1"),
            params.get("target2") or params.get("cell2"),
        ]
        return assign[c1] != assign[c2]

    if ctype in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        cells = expand_region(params["region"], size)
        count = sum(1 for c in cells if assign[c])
        k = int(params.get("count") if "count" in params else params["k"])
        if ctype == "EXACTLY":
            return count == k
        if ctype == "AT_LEAST":
            return count >= k
        if ctype == "AT_MOST":
            return count <= k

    if ctype == "PARITY":
        cells = expand_region(params["region"], size)
        count = sum(1 for c in cells if assign[c])
        parity = str(params.get("parity", "EVEN")).upper()
        return (count % 2 == 0) if parity == "EVEN" else (count % 2 == 1)

    if ctype == "COUNT_COMPARE":
        c1 = sum(1 for c in expand_region(params["region1"], size) if assign[c])
        c2 = sum(1 for c in expand_region(params["region2"], size) if assign[c])
        op = str(params.get("operator", params.get("relation", "EQ"))).upper()
        table = {
            "EQ": c1 == c2, "EQUAL": c1 == c2, "==": c1 == c2,
            "GT": c1 > c2, "GREATER": c1 > c2, ">": c1 > c2,
            "GTE": c1 >= c2, ">=": c1 >= c2,
            "LT": c1 < c2, "LESS": c1 < c2, "<": c1 < c2,
            "LTE": c1 <= c2, "<=": c1 <= c2,
        }
        if op not in table:
            raise ValueError(f"Unknown COUNT_COMPARE operator: {op!r}")
        return table[op]

    # Không được trả True âm thầm: clue lạ sẽ bị bỏ qua khỏi KB và làm kết quả suy diễn sai
    raise ValueError(f"Unsupported clue type: {ctype!r}")
