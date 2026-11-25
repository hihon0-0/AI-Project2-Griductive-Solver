"""Natural-language clue sentence builder with flexible JSON key support (U2)."""
from __future__ import annotations
from typing import Callable, Optional

Segment = tuple[str, Optional[str]]


def _extract_pair(params: dict) -> tuple[str, str]:
    if "cells" in params and isinstance(params["cells"], list) and len(params["cells"]) >= 2:
        return params["cells"][0], params["cells"][1]
    for k1, k2 in [("target1", "target2"), ("a", "b"), ("cell1", "cell2"), ("cell_a", "cell_b"), ("first", "second")]:
        if k1 in params and k2 in params:
            return params[k1], params[k2]
    return "", ""


def _extract_region(params: dict) -> dict:
    if isinstance(params.get("region"), dict):
        return params["region"]
    if "row" in params:
        return {"kind": "ROW", "row": params["row"]}
    if "col" in params or "column" in params:
        return {"kind": "COLUMN", "col": params.get("col", params.get("column"))}
    if "neighbors_of" in params or "center" in params:
        return {"kind": "NEIGHBORS", "cell": params.get("neighbors_of", params.get("center"))}
    if "cells" in params:
        return {"kind": "EXPLICIT", "cells": params["cells"]}
    return {}


def _format_name_list(cells: list[str], name_of: Callable[[str], str]) -> str:
    names = [name_of(c) for c in cells if c]
    if not names:
        return "no one"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _region_phrase(region_spec: dict, name_of: Callable[[str], str]) -> str:
    if not isinstance(region_spec, dict) or not region_spec:
        return ""
    kind = str(region_spec.get("kind", region_spec.get("type", ""))).upper()
    if kind == "ROW":
        r = region_spec.get("row", region_spec.get("index", "?"))
        row_num = (r + 1) if isinstance(r, int) and region_spec.get("zero_based") else r
        return f"row {row_num}"
    if kind == "COLUMN":
        col = region_spec.get("col", region_spec.get("column", "?"))
        if isinstance(col, int):
            col = chr(ord("A") + col)
        return f"column {col}"
    if kind == "NEIGHBORS":
        center = region_spec.get("cell", region_spec.get("center", ""))
        return f"the neighbors of {name_of(center)}"
    if kind == "EXPLICIT":
        return _format_name_list(region_spec.get("cells", []), name_of)
    return str(region_spec)


def clue_segments(clue: dict, name_of: Callable[[str], str]) -> list[Segment]:
    if not clue:
        return []
    ctype = str(clue.get("type", "")).upper()
    params = clue.get("params") or {}

    try:
        if ctype == "FACT":
            cell = params.get("cell") or params.get("target") or params.get("subject") or ""
            if cell:
                status = str(params.get("status", params.get("verdict", "INNOCENT"))).upper()
                st_word = "Criminal" if status == "CRIMINAL" else "Innocent"
                return [(name_of(cell), "target"), (f" is {st_word}.", None)]

        if ctype in ("SAME", "DIFFERENT"):
            c1, c2 = _extract_pair(params)
            if c1 and c2:
                rel = "the same role" if ctype == "SAME" else "different roles"
                return [
                    (name_of(c1), "target"),
                    (" and ", None),
                    (name_of(c2), "target"),
                    (f" have {rel}.", None),
                ]

        if ctype in ("EXACTLY", "AT_LEAST", "AT_MOST"):
            count = params.get("count", 0)
            reg_txt = _region_phrase(_extract_region(params), name_of)
            if reg_txt:
                prefix_map = {"EXACTLY": "Exactly", "AT_LEAST": "At least", "AT_MOST": "At most"}
                noun = "person" if count == 1 else "people"
                verb = "is a criminal" if count == 1 else "are criminals"
                return [
                    (f"{prefix_map[ctype]} {count} {noun} in ", None),
                    (reg_txt, "region"),
                    (f" {verb}.", None),
                ]

        if ctype == "PARITY":
            reg_txt = _region_phrase(_extract_region(params), name_of)
            if reg_txt:
                parity = str(params.get("parity", "EVEN")).lower()
                return [
                    ("There is an ", None),
                    (f"{parity} number", "target"),
                    (" of criminals in ", None),
                    (reg_txt, "region"),
                    (".", None),
                ]

        if ctype == "COUNT_COMPARE":
            r1 = _region_phrase(params.get("region1", {}), name_of)
            r2 = _region_phrase(params.get("region2", {}), name_of)
            if r1 and r2:
                op = str(params.get("operator", params.get("op", params.get("relation", "EQUAL")))).upper()
                op_map = {
                    "MORE": "more criminals than", "GREATER": "more criminals than", "GT": "more criminals than",
                    "FEWER": "fewer criminals than", "LESS": "fewer criminals than", "LT": "fewer criminals than",
                    "EQUAL": "the same number of criminals as", "EQ": "the same number of criminals as",
                    "GTE": "at least as many criminals as", "LTE": "at most as many criminals as",
                }
                comp_txt = op_map.get(op, "as many criminals as")
                return [
                    (r1[0].upper() + r1[1:], "region"),
                    (f" has {comp_txt} ", None),
                    (r2, "region2"),
                    (".", None),
                ]
    except Exception:
        pass

    desc = clue.get("description", str(clue))
    return [(desc, None)]


def clue_plain_text(clue: dict, name_of: Callable[[str], str]) -> str:
    return "".join(seg[0] for seg in clue_segments(clue, name_of))