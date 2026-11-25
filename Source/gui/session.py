"""Lớp giao tiếp DUY NHẤT giữa GUI và logic (Engine + Agent).

GUI chỉ nói chuyện với `GameSession`; mọi thứ của backend (GameEngine, DeductiveAgent, get_hint,
load_puzzle) đều được gọi trực tiếp ở đây, không còn module giả (dev_stubs) nào.

Hợp đồng với backend (những gì file này giả định):

  Source.engine.engine.GameEngine(data, entailment_verifier=fn)
      .get_public_state() -> PublicState(grid_size, revealed_verdicts: dict[str,str],
                                         revealed_clues: list[dict], unsolved_cells: list[str])
      .submit_verdict(cell, verdict) -> object có is_valid / status_code / message / revealed_clue
      .get_character(cell) -> dict(name, occupation)           (tuỳ chọn, thiếu thì đọc từ JSON)
  Source.agent.agent.DeductiveAgent()
      .classify_cell(public_state, cell) -> CRIMINAL | INNOCENT | UNKNOWN | INCONSISTENT
      .get_solution_stream(engine) -> iterator các step(cell_id, verdict, forced_by_clue_ids,
                                                         sat_queries, new_clue)
      .metrics (decisions, propagations, backtracks, runtime), .sat_calls, ._clue_cache, .status
  Source.agent.hint.get_hint(public_state, agent) -> (cell, verdict[, clue_ids]) | None
  Source.engine.puzzle_io.load_puzzle(path, schema_path) -> dict   (tuỳ chọn)
"""
from __future__ import annotations

import copy
import inspect
import json
import os
import traceback
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional

from Source.engine.engine import GameEngine
from Source.agent.agent import DeductiveAgent

try:
    from Source.engine.puzzle_io import load_puzzle as _backend_load_puzzle
except ImportError:  # thiếu jsonschema -> đọc JSON thuần
    _backend_load_puzzle = None

try:
    from Source.agent.hint import get_hint as _backend_get_hint
except ImportError:
    _backend_get_hint = None


# =========================================================================
# Kiểu dữ liệu trả về cho GUI
# =========================================================================

@dataclass
class VerdictResult:
    is_valid: bool
    message: str
    revealed_clue: Optional[dict] = None
    code: str = ""   # CORRECT | NOT_PROVABLE | CONTRADICTED | ALREADY_REVEALED | ERROR


@dataclass
class VerdictOutcome:
    accepted: bool
    code: str  # CORRECT | NOT_PROVABLE | CONTRADICTED | ALREADY_REVEALED | ERROR
    new_clue: Optional[dict] = None
    message: str = ""   # nguyên văn thông điệp engine trả về


@dataclass
class HintInfo:
    cell: str
    verdict: str
    clue_ids: list[str] = field(default_factory=list)


@dataclass
class StepOutcome:
    kind: str  # OK | SOLVED | STUCK | INCONSISTENT | ERROR
    cell: Optional[str] = None
    verdict: Optional[str] = None
    clue_ids: list[str] = field(default_factory=list)
    new_clue: Optional[dict] = None
    message: str = ""


_KNOWN_CODES = ("NOT_PROVABLE", "CONTRADICTED", "ALREADY_REVEALED")


def _code_of(raw_code: Any) -> str:
    """Đưa status_code của engine (Enum hoặc str) về mã chuẩn của GUI."""
    if raw_code is None:
        return ""
    name = (getattr(raw_code, "name", None) or str(raw_code)).split(".")[-1].upper()
    if name == "ALREADY_SOLVED":
        name = "ALREADY_REVEALED"
    return name if name in ("CORRECT", *_KNOWN_CODES) else "ERROR"


def normalize_verdict(raw: Any) -> VerdictResult:
    """Kết quả submit_verdict của engine -> VerdictResult."""
    if raw is None:
        raise RuntimeError("engine.submit_verdict trả về None")
    if isinstance(raw, VerdictResult):
        return raw
    ok = bool(getattr(raw, "is_valid", getattr(raw, "success", False)))
    msg = str(getattr(raw, "message", ""))
    code = "CORRECT" if ok else (_code_of(getattr(raw, "status_code", None)) or _code_of(msg))
    return VerdictResult(ok, msg, getattr(raw, "revealed_clue", None), code)


class _EngineAdapterForAgent:
    """Agent đọc `result.is_valid`; adapter đảm bảo submit_verdict luôn trả VerdictResult."""

    def __init__(self, engine: Any):
        self._engine = engine

    def get_public_state(self):
        return self._engine.get_public_state()

    def submit_verdict(self, cell: str, verdict: str) -> VerdictResult:
        return normalize_verdict(self._engine.submit_verdict(cell, verdict))


class GameSession:
    """Giao diện duy nhất giữa GUI và backend."""

    def __init__(self):
        self.size: int = 3
        self.name: str = ""
        self.terminal: Optional[str] = None  # None | SOLVED | STUCK | INCONSISTENT
        self.log: list[dict] = []
        self.warnings: list[str] = []        # cảnh báo cấu hình backend (hiện lên thanh trạng thái)

        self._puzzle_path: Optional[str] = None
        self._puzzle_data: dict = {}
        self._engine: Any = None
        self._agent: Optional[DeductiveAgent] = None
        self._stream: Optional[Iterator] = None
        self._step_num: int = 0

    @property
    def steps(self) -> int:
        """Số verdict đã được chấp nhận (không tính thẻ mở sẵn và lượt bị từ chối)."""
        return self._step_num

    # ------------------------------------------------------------------
    # Dựng engine + agent
    # ------------------------------------------------------------------
    def _make_engine(self, data: dict):
        """GameEngine gắn agent.classify_cell làm entailment_verifier (để game KHÔNG cho đoán mò)."""
        verifier = self._agent.classify_cell
        try:
            params = inspect.signature(GameEngine.__init__).parameters
        except (TypeError, ValueError):
            params = {}
        if "entailment_verifier" in params:
            return GameEngine(data, entailment_verifier=verifier)
        engine = GameEngine(data)
        if hasattr(engine, "entailment_verifier"):
            engine.entailment_verifier = verifier
        else:
            self.warnings.append("GameEngine không nhận entailment_verifier: game sẽ chấp nhận đoán mò!")
        return engine

    def _build_engine_and_agent(self):
        self.warnings = []
        self._agent = DeductiveAgent()   # agent MỚI -> bộ đếm SAT/metrics về 0
        self._engine = self._make_engine(copy.deepcopy(self._puzzle_data))
        self._stream = None
        self._step_num = 0
        self.terminal = "SOLVED" if self.is_solved() else None
        self.log.clear()
        for cid, v in self.statuses().items():
            self.log.append({"step": 0, "cell": cid, "verdict": v, "note": "(Initially revealed)"})

    def load(self, path: str) -> None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schema_path = os.path.join(root_dir, "schemas", "puzzle_schema.json")

        data = None
        if _backend_load_puzzle and os.path.exists(schema_path):
            try:
                data = _backend_load_puzzle(path, schema_path)
            except TypeError:
                data = _backend_load_puzzle(path)
        if data is None:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        if not isinstance(data, dict) or "grid" not in data:
            raise ValueError("Invalid puzzle JSON format: missing 'grid'")

        self._puzzle_path = path
        self._puzzle_data = data
        self.size = int(data.get("size", 3))
        self.name = str(data.get("name", os.path.basename(path)))
        self._build_engine_and_agent()

    def restart(self) -> None:
        if self._puzzle_data:
            self._build_engine_and_agent()

    # ------------------------------------------------------------------
    # Truy vấn trạng thái công khai (không bao giờ đọc nghiệm ẩn)
    # ------------------------------------------------------------------
    def character(self, cell: str) -> dict:
        """{name, occupation}."""
        if self._engine is not None and hasattr(self._engine, "get_character"):
            info = self._engine.get_character(cell)
            if isinstance(info, dict):
                return {"name": info.get("name", "?"), "occupation": info.get("occupation", "")}
        for item in self._puzzle_data.get("grid", []):
            if item.get("id") == cell:
                ch = item.get("character", {})
                return {"name": ch.get("name", "?"), "occupation": ch.get("occupation", "")}
        return {"name": "?", "occupation": ""}

    def statuses(self) -> dict[str, str]:
        if self._engine is None:
            return {}
        return dict(self._engine.get_public_state().revealed_verdicts)

    def clue_of(self, cell: str) -> Optional[dict]:
        if self._engine is None:
            return None
        for clue in self._engine.get_public_state().revealed_clues:
            if clue.get("id") == f"clue_{cell}" or clue.get("cell") == cell or clue.get("owner") == cell:
                return clue
        return None

    def clue_owner(self, clue_id: str) -> Optional[str]:
        for cell_id in self.statuses():
            clue = self.clue_of(cell_id)
            if clue and clue.get("id") == clue_id:
                return cell_id
        return None

    def is_solved(self) -> bool:
        if self._engine is None:
            return False
        return not self._engine.get_public_state().unsolved_cells

    # ------------------------------------------------------------------
    # Người chơi đi tay
    # ------------------------------------------------------------------
    def submit(self, cell: str, verdict: str, _note: str = "Manual proof accepted") -> VerdictOutcome:
        if self._engine is None:
            return VerdictOutcome(False, "ERROR")
        cell, verdict = cell.upper(), verdict.upper()
        if cell in self.statuses():
            return VerdictOutcome(False, "ALREADY_REVEALED")

        try:
            res = normalize_verdict(self._engine.submit_verdict(cell, verdict))
        except Exception as exc:  # lỗi backend -> báo lên GUI, không để chương trình sập
            traceback.print_exc()
            self.log.append({"step": None, "cell": cell, "verdict": verdict, "note": f"Error: {exc}"})
            return VerdictOutcome(False, "ERROR", message=f"{type(exc).__name__}: {exc}")

        self._stream = None  # đi tay -> lần Auto sau dựng generator mới từ KB hiện tại
        if res.is_valid:
            self._step_num += 1
            if self.terminal == "STUCK":
                self.terminal = None       # KB vừa có thêm clue mới -> có thể suy diễn tiếp
            if str(getattr(self._agent, "status", "")).upper() == "STUCK":
                self._agent.status = "RUNNING"
            if self.is_solved():
                self.terminal = "SOLVED"
            self.log.append({"step": self._step_num, "cell": cell, "verdict": verdict, "note": _note})
            return VerdictOutcome(True, "CORRECT", res.revealed_clue)

        code = res.code if res.code in _KNOWN_CODES else "ERROR"
        note = f"Rejected ({code})" if code != "ERROR" else f"Rejected: engine said {res.message!r}"
        self.log.append({"step": None, "cell": cell, "verdict": verdict, "note": note})
        return VerdictOutcome(False, code, message=res.message)

    # ------------------------------------------------------------------
    # Hint
    # ------------------------------------------------------------------
    def _hint_from_backend(self, pub) -> Optional[tuple]:
        """Gọi Source.agent.hint.get_hint; nếu module không có thì tự quét bằng agent.classify_cell."""
        if _backend_get_hint is not None:
            try:
                n_params = len(inspect.signature(_backend_get_hint).parameters)
            except (TypeError, ValueError):
                n_params = 2
            res = _backend_get_hint(pub, self._agent) if n_params >= 2 else _backend_get_hint(pub)
            if res is None:
                return None
            if hasattr(res, "cell"):   # get_hint trả object thay vì tuple
                return (res.cell, res.verdict, list(getattr(res, "clue_ids", []) or []))
            return tuple(res)

        for cid in sorted(pub.unsolved_cells, key=lambda c: (int(c[1:]), c[0])):
            r = self._agent.classify_cell(pub, cid)
            if r == "INCONSISTENT":
                self._agent.status = "INCONSISTENT"
                return None
            if r in ("CRIMINAL", "INNOCENT"):
                return (cid, r, [])
        return None

    def hint(self) -> Optional[HintInfo]:
        if self._engine is None or self._agent is None or self.is_solved():
            return None
        pub = self._engine.get_public_state()
        res = self._hint_from_backend(pub)

        if not res:
            self._set_terminal_from_agent()
            return None

        cell, verdict = res[0], res[1]
        clue_ids = list(res[2]) if len(res) > 2 and isinstance(res[2], (list, tuple)) else []
        if not clue_ids and hasattr(self._agent, "clues_mentioning"):
            clue_ids = list(self._agent.clues_mentioning(pub, cell))
        return HintInfo(cell, verdict, clue_ids)

    # ------------------------------------------------------------------
    # Step / Auto
    # ------------------------------------------------------------------
    def _set_terminal_from_agent(self) -> StepOutcome:
        st = str(getattr(self._agent, "status", "") or "").upper()
        if self.is_solved() or st == "SOLVED":
            self.terminal = "SOLVED"
        else:
            self.terminal = "INCONSISTENT" if st == "INCONSISTENT" else "STUCK"
        return StepOutcome(self.terminal)

    def next_step(self) -> StepOutcome:
        if self._engine is None or self._agent is None:
            return StepOutcome("ERROR", message="No puzzle loaded")
        if self.is_solved():
            self.terminal = "SOLVED"
            return StepOutcome("SOLVED")
        if self.terminal in ("STUCK", "INCONSISTENT"):
            return StepOutcome(self.terminal)

        try:
            if self._stream is None:
                self._stream = iter(self._agent.get_solution_stream(_EngineAdapterForAgent(self._engine)))
            step = next(self._stream)
        except StopIteration:
            self._stream = None
            return self._set_terminal_from_agent()
        except Exception as exc:
            traceback.print_exc()
            self._stream = None
            return StepOutcome("ERROR", message=f"{type(exc).__name__}: {exc}")

        self._step_num += 1
        cell = getattr(step, "cell_id", None)
        verdict = getattr(step, "verdict", None)
        clue_ids = list(getattr(step, "forced_by_clue_ids", []) or [])
        sat_q = getattr(step, "sat_queries", 0)
        new_clue = getattr(step, "new_clue", None)
        if self.is_solved():
            self.terminal = "SOLVED"

        note = f"SAT {sat_q}"
        if clue_ids:
            note += f" | via {', '.join(clue_ids)}"
        if new_clue:
            note += f" | +{new_clue.get('id', '?')}"
        self.log.append({"step": self._step_num, "cell": cell or "?", "verdict": verdict or "?", "note": note})
        return StepOutcome("SOLVED" if self.terminal == "SOLVED" else "OK", cell, verdict, clue_ids, new_clue)

    # ------------------------------------------------------------------
    # Metrics (đọc thẳng từ agent)
    # ------------------------------------------------------------------
    def metrics(self) -> dict[str, str | int]:
        a = self._agent
        m = getattr(a, "metrics", None)
        cache = getattr(a, "_clue_cache", {}) or {}
        clauses = sum(len(v) for v in cache.values())
        mapper = getattr(getattr(a, "encoder", None), "mapper", None)
        aux = mapper.auxiliary_variable_count if mapper else 0
        primary = self.size * self.size
        rt = getattr(m, "runtime", 0.0)
        return {
            "Grid": f"{self.size}x{self.size}",
            "Solved": f"{len(self.statuses())}/{primary}",
            "Primary vars": primary,
            "Aux vars": aux,                    
            "CNF clauses": clauses,
            "SAT calls": getattr(a, "sat_calls", 0),
            "Steps": self._step_num,
            "Decisions": getattr(m, "decisions", 0),
            "Propagations": getattr(m, "propagations", 0),
            "Backtracks": getattr(m, "backtracks", 0),
            "Runtime": f"{rt * 1000.0:.2f} ms",
        }
