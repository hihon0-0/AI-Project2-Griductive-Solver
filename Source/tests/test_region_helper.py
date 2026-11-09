"""Unit tests for RegionHelper (TV3)."""
import pytest
from Source.engine.region_helper import RegionHelper

def test_parse_and_to_coord():
    assert RegionHelper.parse_coord("A1") == (0, 0)
    assert RegionHelper.parse_coord("C2") == (2, 1)
    assert RegionHelper.parse_coord("E5") == (4, 4)

    assert RegionHelper.to_coord(0, 0) == "A1"
    assert RegionHelper.to_coord(2, 1) == "C2"
    assert RegionHelper.to_coord(4, 4) == "E5"

def test_get_all_cells():
    cells_3 = RegionHelper.get_all_cells(3)
    assert len(cells_3) == 9
    assert cells_3[0] == "A1"
    assert cells_3[-1] == "C3"

def test_get_row_cells():
    assert RegionHelper.get_row_cells(1, 3) == ["A1", "B1", "C1"]
    assert RegionHelper.get_row_cells(2, 3) == ["A2", "B2", "C2"]
    with pytest.raises(ValueError):
        RegionHelper.get_row_cells(4, 3)

def test_get_col_cells():
    assert RegionHelper.get_col_cells("A", 3) == ["A1", "A2", "A3"]
    assert RegionHelper.get_col_cells("C", 3) == ["C1", "C2", "C3"]
    with pytest.raises(ValueError):
        RegionHelper.get_col_cells("D", 3)

def test_get_neighbors_3x3():
    # Center cell B2 in 3x3 has 8 neighbors
    b2_nbrs = RegionHelper.get_neighbors("B2", 3)
    assert len(b2_nbrs) == 8
    assert "B2" not in b2_nbrs
    assert b2_nbrs == ["A1", "B1", "C1", "A2", "C2", "A3", "B3", "C3"]

    # Corner cell A1 has 3 neighbors: B1, A2, B2
    a1_nbrs = RegionHelper.get_neighbors("A1", 3)
    assert len(a1_nbrs) == 3
    assert a1_nbrs == ["B1", "A2", "B2"]

    # Edge cell B1 has 5 neighbors: A1, C1, A2, B2, C2
    b1_nbrs = RegionHelper.get_neighbors("B1", 3)
    assert len(b1_nbrs) == 5
    assert b1_nbrs == ["A1", "C1", "A2", "B2", "C2"]

def test_resolve_region():
    # ROW
    assert RegionHelper.resolve_region({"type": "ROW", "row": 2}, 3) == ["A2", "B2", "C2"]

    # COLUMN
    assert RegionHelper.resolve_region({"type": "COLUMN", "col": "B"}, 3) == ["B1", "B2", "B3"]

    # NEIGHBORS
    assert RegionHelper.resolve_region({"type": "NEIGHBORS", "cell": "A1"}, 3) == ["B1", "A2", "B2"]

    # EXPLICIT
    assert RegionHelper.resolve_region({"type": "EXPLICIT", "cells": ["C3", "A1", "B2"]}, 3) == ["A1", "B2", "C3"]
