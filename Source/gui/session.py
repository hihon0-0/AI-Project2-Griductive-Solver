from __future__ import annotations

import copy
import inspect
import json
import os
import traceback
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional

# Luôn nạp stub core TRƯỚC KHI import agent/engine (agent import core.* ngay đầu file)
from Source.gui.dev_stubs import install_missing_core, make_stub_engine, StubClassifier

_CORE_STUBS = install_missing_core("Source")

from Source.engine.engine import GameEngine  # noqa: E402
from Source.agent.agent import DeductiveAgent  # noqa: E402

try:
    from Source.engine.puzzle_io import load_puzzle as _backend_load_puzzle
except ImportError:  # thiếu jsonschema
    _backend_load_puzzle = None

try:
    from Source.agent.hint import get_hint as _backend_get_hint
except ImportError:
    _backend_get_hint = None


# =========================================================================
# Kiểu dữ liệu trả về cho GUI (hợp đồng mục 5 của tài liệu phân việc)
# =========================================================================

@dataclass
class VerdictResult:
    is_valid: bool
    message: str
    revealed_clue: Optional[dict] = None
    code: str = ""   # CORRECT | NOT_PROVABLE | CONTRADICTED | ALREADY_REVEALED | ERROR (rỗng = chưa biết)


@dataclass
class VerdictOutcome:
    accepted: bool
    code: str  # CORRECT | NOT_PROVABLE | CONTRADICTED | ALREADY_REVEALED | ERROR
    new_clue: Optional[dict] = None
    message: str = ""   # nguyên văn thông điệp engine trả về (để báo lỗi cho đúng người)


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


class _EngineAdapterForAgent:
    """Mặt nạ để agent luôn nhận VerdictResult dạng object (agent dùng result.is_valid)."""

    def __init__(self, engine: Any):
        self._engine = engine

    def get_public_state(self):
        return self._engine.get_public_state()

    def submit_verdict(self, cell: str, verdict: str) -> VerdictResult:
        return GameSession._normalize_verdict(self._engine.submit_verdict(cell, verdict))


_KNOWN_CODES = ("NOT_PROVABLE", "CONTRADICTED", "ALREADY_REVEALED")


class GameSession:
    """Giao diện DUY NHẤT giữa GUI và backend (Engine + Agent)."""

    def __init__(self):
        self.stubs: list[str] = list(_CORE_STUBS)
        self.size: int = 3
        self.name: str = ""
        self.terminal: Optional[str] = None  # None | SOLVED | STUCK | INCONSISTENT
        self.log: list[dict] = []

        self._puzzle_path: Optional[str] = None
        self._puzzle_data: dict = {}
        self._engine: Any = None
        self._agent: Optional[DeductiveAgent] = None
        self._stream: Optional[Iterator] = None
        self._step_num: int = 0
        self._use_fallback_loop: bool = False
        self._stub_classifier = StubClassifier()
        self._stub_classifier_used = False

    @property
    def steps(self) -> int:
        """Số verdict đã được chấp nhận (không tính thẻ mở sẵn và lượt bị từ chối)."""
        return self._step_num

    # ------------------------------------------------------------------
    @staticmethod
    def _code_of(raw_code: Any) -> str:
        """Đưa status_code của engine thật (Enum hoặc str) về mã chuẩn của GUI."""
        if raw_code is None:
            return ""
        name = getattr(raw_code, "name", None) or str(raw_code)
        name = name.split(".")[-1].upper()
        if name == "ALREADY_SOLVED":
            name = "ALREADY_REVEALED"
        return name if name in ("CORRECT", "NOT_PROVABLE", "CONTRADICTED", "ALREADY_REVEALED") else "ERROR"

    @staticmethod
    def _normalize_verdict(raw: Any) -> VerdictResult:
        """Chấp nhận tuple (ok, msg, clue) lẫn object có is_valid/status_code/message/revealed_clue."""
        if raw is None:
            raise NotImplementedError("submit_verdict chưa được cài đặt (trả về None)")
        if isinstance(raw, VerdictResult):
            return raw
        if isinstance(raw, tuple):
            ok = bool(raw[0]) if len(raw) > 0 else False
            msg = str(raw[1]) if len(raw) > 1 else "ERROR"
            clue = raw[2] if len(raw) > 2 else None
            return VerdictResult(ok, msg, clue, GameSession._code_of(msg))
        ok = getattr(raw, "is_valid", getattr(raw, "success", False))
        msg = str(getattr(raw, "message", "ERROR"))
        # Engine thật để mã ở status_code, còn message là câu dài -> phải đọc status_code
        code = GameSession._code_of(getattr(raw, "status_code", None)) or GameSession._code_of(msg)
        if bool(ok):
            code = "CORRECT"
        return VerdictResult(bool(ok), msg, getattr(raw, "revealed_clue", None), code)

    def _engine_submit_works(self) -> bool:
        """Gọi thử submit_verdict trên một engine TẠM; trả False nếu TV3 còn TODO."""
        try:
            probe = GameEngine(copy.deepcopy(self._puzzle_data))
            unsolved = probe.get_public_state().unsolved_cells
            if not unsolved:
                return True
            return probe.submit_verdict(unsolved[0], "INNOCENT") is not None
        except NotImplementedError:
            return False
        except Exception:
            return True  # engine thật nhưng báo lỗi: để lỗi lộ ra ở lần gọi thật

    def _classify(self, state, cell):
        """agent.classify_cell của TV4; nếu còn TODO (NotImplementedError) thì dùng StubClassifier
        và báo 'agent.classify_cell' vào session.stubs để GUI hiện cảnh báo DEV."""
        try:
            return self._agent.classify_cell(state, cell)
        except NotImplementedError:
            if not self._stub_classifier_used:
                self._stub_classifier_used = True
                if "agent.classify_cell" not in self.stubs:
                    self.stubs.append("agent.classify_cell")
            return self._stub_classifier(state, cell)

    def _make_real_engine(self, data: dict):
        """Dựng GameEngine thật VÀ gắn agent.classify_cell làm entailment_verifier.
        Thiếu verifier thì engine rơi về chế độ standalone: so với nghiệm ẩn, tức là cho phép ĐOÁN."""
        verifier = self._classify
        try:
            params = inspect.signature(GameEngine.__init__).parameters
        except (TypeError, ValueError):
            params = {}
        if "entailment_verifier" in params:
            engine = GameEngine(data, entailment_verifier=verifier)
        else:
            engine = GameEngine(data)
            if hasattr(engine, "entailment_verifier"):
                engine.entailment_verifier = verifier
            else:
                self.stubs.append("engine.NO_VERIFIER (game se chap nhan doan mo!)")
        return engine

    def _build_engine_and_agent(self):
        """Dựng mới engine + agent từ self._puzzle_data."""
        self.stubs = list(_CORE_STUBS)
        self._agent = DeductiveAgent()   # agent MỚI -> bộ đếm SAT/metrics về 0
        self._stub_classifier = StubClassifier()
        self._stub_classifier_used = False

        data = copy.deepcopy(self._puzzle_data)
        if self._engine_submit_works():
            engine = self._make_real_engine(data)
        else:
            engine = make_stub_engine(GameEngine, data, self._classify)
            self.stubs.append("engine.submit_verdict")
        self._engine = engine          # <<< dòng bị thiếu trong bản cũ

        self._stream = None
        self._use_fallback_loop = False
        self._step_num = 0
        self.terminal = "SOLVED" if self.is_solved() else None
        self.log.clear()
        for cid, v in self.statuses().items():
            self.log.append({"step": 0, "cell": cid, "verdict": v, "note": "(Initially revealed)"})

    # ------------------------------------------------------------------
    def load(self, path: str) -> None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schema_path = os.path.join(root_dir, "schemas", "puzzle_schema.json")

        data = None
        if _backend_load_puzzle and os.path.exists(schema_path):
            try:
                data = _backend_load_puzzle(path, schema_path)
            except TypeError:
                data = _backend_load_puzzle(path)
            except ImportError:
                data = None

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
    def character(self, cell: str) -> dict:
        """{name, occupation}. Tuyệt đối không đọc hidden_status."""
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
        rc = getattr(self._engine, "revealed_clues", None)
        if isinstance(rc, dict):
            return rc.get(cell)
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
    def submit(self, cell: str, verdict: str, _note: str = "Manual proof accepted") -> VerdictOutcome:
        if self._engine is None:
            return VerdictOutcome(False, "ERROR")
        cell, verdict = cell.upper(), verdict.upper()
        if cell in self.statuses():
            return VerdictOutcome(False, "ALREADY_REVEALED")

        try:
            res = self._normalize_verdict(self._engine.submit_verdict(cell, verdict))
        except Exception as exc:  # engine/agent lỗi -> báo lên GUI, không để chương trình sập
            self.log.append({"step": None, "cell": cell, "verdict": verdict, "note": f"Error: {exc}"})
            return VerdictOutcome(False, "ERROR", message=f"{type(exc).__name__}: {exc}")

        self._stream = None  # người chơi đi tay -> lần Auto sau dựng generator mới từ KB hiện tại
        if res.is_valid:
            self._step_num += 1
            if self.terminal == "STUCK":
                self.terminal = None       # KB vừa có thêm clue mới -> có thể suy diễn tiếp
            if hasattr(self._agent, "status") and str(self._agent.status).upper() == "STUCK":
                self._agent.status = "RUNNING"
            if self.is_solved():
                self.terminal = "SOLVED"
            self.log.append({"step": self._step_num, "cell": cell, "verdict": verdict,
                             "note": _note})
            return VerdictOutcome(True, "CORRECT", res.revealed_clue)

        code = res.code if res.code in _KNOWN_CODES else "ERROR"
        note = f"Rejected ({code})" if code != "ERROR" else f"Rejected: engine said {res.message!r}"
        self.log.append({"step": None, "cell": cell, "verdict": verdict, "note": note})
        return VerdictOutcome(False, code, message=res.message)

    def _find_forced(self, pub) -> Optional[tuple]:
        """(cell, verdict, ...) của ô đang bị ép, hoặc None. Thử lần lượt các API của agent;
        API nào chưa cài (NotImplementedError / sai chữ ký) thì bỏ qua sang API kế tiếp."""
        a = self._agent
        for name in ("find_forced", "solve_step"):
            fn = getattr(a, name, None)
            if fn is None:
                continue
            try:
                return fn(pub)          # None nghĩa là "không có ô nào bị ép"
            except NotImplementedError:
                continue
            except TypeError:
                # Có thể do sai chữ ký (thử API khác) nhưng cũng có thể là lỗi thật trong agent.
                traceback.print_exc()
                continue
        if hasattr(a, "classify_cell"):
            order = sorted(pub.unsolved_cells, key=lambda c: (int(c[1:]), c[0]))
            for cid in order:
                r = self._classify(pub, cid)
                if r == "INCONSISTENT":
                    if hasattr(a, "status"):
                        a.status = "INCONSISTENT"
                    return None
                if r in ("CRIMINAL", "INNOCENT"):
                    return (cid, r, 0)
            return None
        raise NotImplementedError("Agent chưa có find_forced / solve_step / classify_cell")

    def hint(self) -> Optional[HintInfo]:
        if self._engine is None or self._agent is None or self.is_solved():
            return None
        pub = self._engine.get_public_state()

        res, answered = None, False
        if _backend_get_hint:
            for args in ((pub, self._agent), (pub,)):
                try:
                    res, answered = _backend_get_hint(*args), True
                    break
                except (TypeError, NotImplementedError):
                    continue       # hint.py của TV4 chưa xong -> dùng thẳng agent bên dưới
        if not answered:
            res = self._find_forced(pub)

        if not res:
            st = str(getattr(self._agent, "status", "") or "").upper()
            self.terminal = "INCONSISTENT" if st == "INCONSISTENT" else "STUCK"
            return None

        cell, verdict = res[0], res[1]
        clue_ids = list(res[2]) if len(res) > 2 and isinstance(res[2], list) else []
        if not clue_ids and hasattr(self._agent, "clues_mentioning"):
            try:
                clue_ids = list(self._agent.clues_mentioning(pub, cell))
            except (NotImplementedError, TypeError):
                clue_ids = []
        return HintInfo(cell, verdict, clue_ids)

    def _end_state(self) -> StepOutcome:
        st = str(getattr(self._agent, "status", "") or "").upper()
        if self.is_solved() or st == "SOLVED":
            self.terminal = "SOLVED"
        else:
            self.terminal = "INCONSISTENT" if st == "INCONSISTENT" else "STUCK"
        return StepOutcome(self.terminal)

    def _next_step_fallback(self) -> StepOutcome:
        """Dùng khi agent.get_solution_stream chưa được TV4 cài: tự tìm ô bị ép rồi gửi qua engine."""
        pub = self._engine.get_public_state()
        try:
            found = self._find_forced(pub)
        except Exception as exc:
            traceback.print_exc()
            return StepOutcome("ERROR", message=f"{type(exc).__name__}: {exc}")
        if not found:
            return self._end_state()
        cell, verdict = found[0], found[1]
        clue_ids = []
        if hasattr(self._agent, "clues_mentioning"):
            try:
                clue_ids = list(self._agent.clues_mentioning(pub, cell))
            except (NotImplementedError, TypeError):
                pass
        out = self.submit(cell, verdict, _note="Auto step (fallback)")
        if not out.accepted:
            return StepOutcome("ERROR", message=f"Engine rejected forced verdict {cell}={verdict}: {out.code}")
        return StepOutcome("SOLVED" if self.terminal == "SOLVED" else "OK",
                           cell, verdict, clue_ids, out.new_clue)

    def next_step(self) -> StepOutcome:
        if self._engine is None or self._agent is None:
            return StepOutcome("ERROR", message="No puzzle loaded")
        if self.is_solved():
            self.terminal = "SOLVED"
            return StepOutcome("SOLVED")
        if self.terminal in ("STUCK", "INCONSISTENT"):
            return StepOutcome(self.terminal)

        if not self._use_fallback_loop:
            try:
                if self._stream is None:
                    self._stream = iter(self._agent.get_solution_stream(_EngineAdapterForAgent(self._engine)))
                step = next(self._stream)
            except StopIteration:
                self._stream = None
                return self._end_state()
            except NotImplementedError:
                self._stream, self._use_fallback_loop = None, True   # TV4 chưa cài stream
            except Exception as exc:
                # Mọi lỗi khác (kể cả AttributeError bên trong agent) phải lộ ra, không được nuốt thành "STUCK".
                traceback.print_exc()
                self._stream = None
                return StepOutcome("ERROR", message=f"{type(exc).__name__}: {exc}")
            else:
                self._step_num += 1
                cell = getattr(step, "cell_id", None)
                verdict = getattr(step, "verdict", None)
                clue_ids = list(getattr(step, "forced_by_clue_ids", []))
                sat_q = getattr(step, "sat_queries", 0)
                new_clue = getattr(step, "new_clue", None)
                if self.is_solved():
                    self.terminal = "SOLVED"
                note = f"SAT {sat_q}"
                if clue_ids:
                    note += f" | via {', '.join(clue_ids)}"
                if new_clue:
                    note += f" | +{new_clue.get('id', '?')}"
                self.log.append({"step": self._step_num, "cell": cell or "?",
                                 "verdict": verdict or "?", "note": note})
                return StepOutcome("SOLVED" if self.terminal == "SOLVED" else "OK",
                                   cell, verdict, clue_ids, new_clue)
        return self._next_step_fallback()

    # ------------------------------------------------------------------
    def metrics(self) -> dict[str, str | int]:
        a = self._agent
        m = getattr(a, "metrics", None)
        cache = getattr(a, "_clue_cache", {}) or {}
        clauses = sum(len(v) for v in cache.values())
        max_var = max((abs(l) for v in cache.values() for cl in v for l in cl), default=0)
        primary = self.size * self.size
        sc = self._stub_classifier if self._stub_classifier_used else None
        if sc is not None:   # agent chưa cài -> lấy số liệu từ verifier dự phòng (chỉ để dev nhìn, không dùng cho báo cáo)
            sat_calls, dec, prop, back, rt = sc.sat_calls, sc.decisions, sc.propagations, sc.backtracks, sc.runtime
        else:
            sat_calls = getattr(a, "sat_calls", 0)
            dec, prop, back = (getattr(m, k, 0) for k in ("decisions", "propagations", "backtracks"))
            rt = getattr(m, "runtime", 0.0)
        return {
            "Grid": f"{self.size}x{self.size}",
            "Solved": f"{len(self.statuses())}/{primary}",
            "Primary vars": primary,
            "Aux vars": max(0, max_var - primary),
            "CNF clauses": clauses,
            "SAT calls": sat_calls,
            "Decisions": dec,
            "Propagations": prop,
            "Backtracks": back,
            "Runtime": f"{rt * 1000.0:.2f} ms",
        }