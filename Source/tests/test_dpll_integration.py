"""Test tích hợp DPLLSolver (TV1) với VariableMapper & CNFEncoder (TV2)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.dpll import DPLLSolver
from core.encoder import CNFEncoder, VariableMapper


def test_metrics_reference_and_accumulation():
    """Kiểm tra lỗi 1: metrics từng bước không bị ghi đè và total_metrics cộng dồn đúng."""
    solver = DPLLSolver()
    clauses = [[1, 2], [-1, 2]]  # Ép biến 2 = True

    sat1, _, m1 = solver.solve(clauses, assumptions=[1])
    sat2, _, m2 = solver.solve(clauses, assumptions=[-1])

    assert sat1 is True and sat2 is True
    # Đảm bảo m1 và m2 là 2 object độc lập, không trỏ chung vào self.metrics
    assert m1 is not m2
    assert m1.propagations > 0
    assert m2.propagations > 0
    # Đảm bảo total_metrics cộng dồn cả 2 lần gọi
    assert solver.total_metrics.sat_calls == 2
    assert solver.total_metrics.propagations == m1.propagations + m2.propagations
    print("[PASS] test_metrics_reference_and_accumulation")


def test_required_vars_completeness():
    """Kiểm tra lỗi 2: model trả về đủ toàn bộ biến trên bàn cờ kể cả ô chưa có clue."""
    mapper = VariableMapper(grid_size=3)
    all_cells = [f"{col}{row}" for row in range(1, 4) for col in ("A", "B", "C")]
    mapper.register_grid(all_cells)

    # Chỉ có 1 clue duy nhất nhắc tới A1 -> 8 ô còn lại không xuất hiện trong clauses
    encoder = CNFEncoder(mapper, grid_size=3)
    clauses = encoder.encode_clue({
        "type": "FACT",
        "params": {"target": "A1", "status": "CRIMINAL"},
    })

    solver = DPLLSolver()
    sat, model, _ = solver.solve(clauses, required_vars=mapper.var_to_cell.keys())

    assert sat is True
    assert model is not None
    # Phải đủ cả 9 ô (A1..C3)
    assert set(model.keys()) == set(mapper.var_to_cell.keys())
    assert model[mapper.get_var("A1")] is True
    print("[PASS] test_required_vars_completeness")


def test_griductive_deduction_integration():
    """Test giải một tình huống suy luận Griductive thực tế từ encoder của TV2."""
    mapper = VariableMapper(grid_size=3)
    all_cells = [f"{col}{row}" for row in range(1, 4) for col in ("A", "B", "C")]
    mapper.register_grid(all_cells)
    encoder = CNFEncoder(mapper, grid_size=3)

    # Giả sử:
    # 1. A1 là CRIMINAL
    # 2. A1 và B1 khác phe (DIFFERENT) -> B1 phải là INNOCENT
    # 3. Hàng 1 (A1, B1, C1) có đúng 2 CRIMINAL (EXACTLY 2) -> C1 buộc phải là CRIMINAL
    clues = [
        {"type": "FACT", "params": {"target": "A1", "status": "CRIMINAL"}},
        {"type": "DIFFERENT", "params": {"target1": "A1", "target2": "B1"}},
        {"type": "EXACTLY", "params": {"region": {"type": "ROW", "row": 1}, "count": 2}},
    ]

    kb_clauses = []
    for clue in clues:
        kb_clauses.extend(encoder.encode_clue(clue))

    solver = DPLLSolver()
    c1_var = mapper.get_var("C1")

    # Kiểm tra C1:
    # Nếu giả định C1 = False (INNOCENT) -> phải ra UNSAT
    sat_if_innocent, _, _ = solver.solve(kb_clauses, assumptions=[-c1_var])
    # Nếu giả định C1 = True (CRIMINAL) -> phải ra SAT
    sat_if_criminal, _, _ = solver.solve(kb_clauses, assumptions=[c1_var])

    assert sat_if_innocent is False, "C1=False phải mâu thuẫn (UNSAT)"
    assert sat_if_criminal is True, "C1=True phải thỏa mãn (SAT)"
    print("[PASS] test_griductive_deduction_integration")


if __name__ == "__main__":
    test_metrics_reference_and_accumulation()
    test_required_vars_completeness()
    test_griductive_deduction_integration()
    print("\nTất cả test đều PASS!")