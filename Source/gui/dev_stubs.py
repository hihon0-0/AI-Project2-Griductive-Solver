from __future__ import annotations
import importlib
import itertools
import sys
import time
import types
from dataclasses import dataclass
from Source.gui.clue_utils import clue_cells, evaluate_clue


# =========================================================================
# 1. STUB CHO TV1 (solver_metrics & dpll) & TV2 (encoder)
# =========================================================================

@dataclass
class StubSolverMetrics:
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime: float = 0.0


class StubVariableMapper:
    def __init__(self, grid_size: int = 3):
        self.grid_size = grid_size
        self._cell_to_var: dict[str, int] = {}
        self._var_to_cell: dict[int, str] = {}
        idx = 1
        for r in range(grid_size):
            for c in range(grid_size):
                cid = f"{chr(ord('A') + c)}{r + 1}"
                self._cell_to_var[cid] = idx
                self._var_to_cell[idx] = cid
                idx += 1

    def get_var(self, cell_id: str) -> int:
        if cell_id not in self._cell_to_var:
            new_id = len(self._cell_to_var) + 1
            self._cell_to_var[cell_id] = new_id
            self._var_to_cell[new_id] = cell_id
        return self._cell_to_var[cell_id]


class StubCNFEncoder:
    def __init__(self, mapper: StubVariableMapper | None = None, grid_size: int = 3):
        self.mapper = mapper or StubVariableMapper(grid_size)
        self.grid_size = grid_size

    def encode_clue(self, clue: dict, grid_size: int | None = None) -> list[list[int]]:
        """Mã hóa bằng bảng chân trị thu nhỏ: cấm mọi tổ hợp giá trị làm clue sai."""
        sz = grid_size or self.grid_size
        cells = clue_cells(clue, sz)
        if not cells:
            return []
        clauses: list[list[int]] = []
        for bits in itertools.product([False, True], repeat=len(cells)):
            assign = dict(zip(cells, bits))
            if not evaluate_clue(clue, assign, sz):
                # Mệnh đề cấm tổ hợp sai: nếu x=True thì thêm -var, nếu x=False thì thêm +var
                clause = [
                    -self.mapper.get_var(c) if val else self.mapper.get_var(c)
                    for c, val in assign.items()
                ]
                clauses.append(clause)
        return clauses


class StubDPLLSolver:
    def __init__(self):
        self.metrics = StubSolverMetrics()

    def solve(
        self, clauses: list[list[int]], assumptions: list[int] | None = None
    ) -> tuple[bool, dict[int, bool] | None, StubSolverMetrics]:
        t0 = time.perf_counter()
        metrics = StubSolverMetrics()
        all_clauses = [list(c) for c in clauses]
        if assumptions:
            all_clauses.extend([[lit] for lit in assumptions])

        variables = sorted({abs(lit) for c in all_clauses for lit in c})

        def dpll(cnf: list[list[int]], model: dict[int, bool]) -> dict[int, bool] | None:
            # 1. Unit propagation
            changed = True
            while changed:
                changed = False
                for clause in cnf:
                    if len(clause) == 0:
                        return None  # Conflict
                    if len(clause) == 1:
                        lit = clause[0]
                        var, val = abs(lit), (lit > 0)
                        if var in model:
                            if model[var] != val:
                                return None
                        else:
                            model[var] = val
                            metrics.propagations += 1
                            cnf = self._simplify(cnf, lit)
                            changed = True
                            break

            if not cnf:
                return model

            # 2. Branching (chọn biến nhỏ nhất chưa gán)
            unassigned = [v for v in variables if v not in model]
            if not unassigned:
                return model
            var = unassigned[0]
            metrics.decisions += 1

            for val in (True, False):
                lit = var if val else -var
                new_model = dict(model)
                new_model[var] = val
                res = dpll(self._simplify(cnf, lit), new_model)
                if res is not None:
                    return res
                metrics.backtracks += 1
            return None

        result_model = dpll(all_clauses, {})
        metrics.runtime = time.perf_counter() - t0
        self.metrics = metrics
        return (result_model is not None), result_model, metrics

    @staticmethod
    def _simplify(cnf: list[list[int]], lit: int) -> list[list[int]]:
        new_cnf = []
        for clause in cnf:
            if lit in clause:
                continue  # Mệnh đề đã thỏa
            if -lit in clause:
                new_cnf.append([x for x in clause if x != -lit])
            else:
                new_cnf.append(clause)
        return new_cnf


class StubClassifier:
    """Verifier DỰ PHÒNG khi agent.classify_cell của TV4 còn TODO (raise NotImplementedError).
    Dùng bộ mã hóa + DPLL giả ở trên, độc lập với Source.core nên chạy được kể cả khi core cũng chưa xong.
    Chữ ký khớp entailment_verifier của engine: (public_state, cell_id) -> CRIMINAL|INNOCENT|UNKNOWN|INCONSISTENT.
    Chỉ đọc PublicState, KHÔNG đọc nghiệm ẩn."""

    def __init__(self):
        self.sat_calls = 0
        self.decisions = self.propagations = self.backtracks = 0
        self.runtime = 0.0
        self._cache: dict[tuple, list[list[int]]] = {}

    def _sat(self, clauses, lit) -> bool:
        ok, _model, m = StubDPLLSolver().solve(clauses, [lit])
        self.sat_calls += 1
        self.decisions += m.decisions
        self.propagations += m.propagations
        self.backtracks += m.backtracks
        self.runtime += m.runtime
        return ok

    def __call__(self, state, cell_id: str) -> str:
        size = state.grid_size
        mapper = StubVariableMapper(size)
        enc = StubCNFEncoder(mapper, size)
        clauses: list[list[int]] = []
        for clue in state.revealed_clues:
            key = (clue.get("id"), size)
            if key not in self._cache:
                self._cache[key] = enc.encode_clue(clue, size)
            clauses.extend(self._cache[key])
        for cid, verdict in state.revealed_verdicts.items():
            v = mapper.get_var(cid)
            clauses.append([v] if verdict == "CRIMINAL" else [-v])
        v = mapper.get_var(cell_id)
        can_be_criminal = self._sat(clauses, v)
        can_be_innocent = self._sat(clauses, -v)
        if not can_be_criminal and not can_be_innocent:
            return "INCONSISTENT"
        if not can_be_innocent:
            return "CRIMINAL"
        if not can_be_criminal:
            return "INNOCENT"
        return "UNKNOWN"


def install_missing_core(base: str = "Source") -> list[str]:
    """Tự động nạp module giả nếu TV1/TV2 chưa push code thật."""
    used_stubs: list[str] = []
    core_pkg = importlib.import_module(f"{base}.core")

    stub_specs = {
        "core.solver_metrics": {"SolverMetrics": StubSolverMetrics},
        "core.encoder": {
            "VariableMapper": StubVariableMapper,
            "CNFEncoder": StubCNFEncoder,
        },
        "core.dpll": {"DPLLSolver": StubDPLLSolver},
    }

    for mod_suffix, attrs in stub_specs.items():
        full_name = f"{base}.{mod_suffix}"
        try:
            mod = importlib.import_module(full_name)
            # Kiểm tra xem module thật đã có đủ class chưa
            if not all(hasattr(mod, attr_name) for attr_name in attrs):
                raise ImportError("Module chưa viết xong các class cần thiết")
        except ImportError:
            fake_mod = types.ModuleType(full_name)
            for attr_name, attr_val in attrs.items():
                setattr(fake_mod, attr_name, attr_val)
            sys.modules[full_name] = fake_mod
            setattr(core_pkg, mod_suffix.split(".")[1], fake_mod)
            used_stubs.append(mod_suffix)

    return used_stubs


# =========================================================================
# 2. STUB CHO TV3 (GameEngine.submit_verdict & các hàm phụ trợ)
# =========================================================================

def make_stub_engine(GameEngineCls, puzzle_data: dict, verifier):
    """
    Kế thừa GameEngine thật của TV3, giữ nguyên các ô đã mở sẵn từ GameEngine
    và chỉ bổ sung hàm submit_verdict còn thiếu.
    """

    class StubGameEngine(GameEngineCls):
        def __init__(self, data: dict):
            self._raw_puzzle = data
            try:
                super().__init__(data)
            except TypeError:
                super().__init__(data, entailment_verifier=verifier)

            # Lấy dữ liệu ô mở sẵn từ GameEngine thật của TV3
            pub = super().get_public_state()
            self.size = getattr(pub, "grid_size", data.get("size", 3))
            self.revealed_statuses = dict(getattr(pub, "revealed_verdicts", {}))
            self.revealed_clues = {}
            for clue in getattr(pub, "revealed_clues", []):
                cid = clue.get("id", "").replace("clue_", "")
                if cid:
                    self.revealed_clues[cid] = clue

            self._all_cells = {c["id"]: c for c in data.get("grid", [])}

        def get_public_state(self):
            pub = super().get_public_state()
            pub.revealed_verdicts = dict(self.revealed_statuses)
            pub.revealed_clues = list(self.revealed_clues.values())
            pub.unsolved_cells = [
                f"{chr(ord('A') + c)}{r + 1}"
                for r in range(self.size)
                for c in range(self.size)
                if f"{chr(ord('A') + c)}{r + 1}" not in self.revealed_statuses
            ]
            return pub

        def submit_verdict(self, cell: str, verdict: str):
            verdict = verdict.upper()
            if cell in self.revealed_statuses:
                return (False, "ALREADY_REVEALED", None)

            pub_state = self.get_public_state()
            forced = verifier(pub_state, cell)

            if forced == "UNKNOWN" or forced is None:
                return (False, "NOT_PROVABLE", None)
            if forced != verdict:
                return (False, "CONTRADICTED", None)

            self.revealed_statuses[cell] = verdict
            clue = self._all_cells.get(cell, {}).get("clue")
            if clue:
                self.revealed_clues[cell] = clue
            return (True, "CORRECT", clue)

        def restart(self):
            if hasattr(super(), "restart"):
                super().restart()
            pub = super().get_public_state()
            self.revealed_statuses = dict(getattr(pub, "revealed_verdicts", {}))
            self.revealed_clues = {}
            for clue in getattr(pub, "revealed_clues", []):
                cid = clue.get("id", "").replace("clue_", "")
                if cid:
                    self.revealed_clues[cid] = clue

        def is_solved(self) -> bool:
            return len(self.revealed_statuses) == (self.size * self.size)

    return StubGameEngine(puzzle_data)