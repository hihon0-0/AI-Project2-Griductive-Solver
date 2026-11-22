"""Main GUI application for Griductive Solver (Clean Minimalist Layout + HowToPlay Popup)."""
from __future__ import annotations

import glob
import math
import os
import sys
import time
import pygame
from typing import Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(SOURCE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Source.gui.session import GameSession
from Source.gui.clue_utils import clue_roles
from Source.gui.theme import Theme
from Source.gui.components import (
    FontManager,
    Button,
    CardRenderer,
    GridRenderer,
    StatusBar,
    TabbedSidePanel,
    VerdictPopover,
    HowToPlayPopup,
    SolvedBanner,
    get_detective_logo,
    draw_flipping_card,
    draw_tooltip,
)


class GriductiveApp:
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 840
    FPS = 60

    @classmethod
    def _window_size(cls) -> tuple[int, int]:
        """Cửa sổ lớn để ô bài to, nhưng không vượt quá màn hình thực tế."""
        w, h = cls.WINDOW_WIDTH, cls.WINDOW_HEIGHT
        try:
            dw, dh = pygame.display.get_desktop_sizes()[0]
            w = min(w, max(960, dw - 40))
            h = min(h, max(680, dh - 110))
        except Exception:
            pass
        return w, h

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Griductive No-Guess Solver (CSC14003)")
        size = self._window_size()
        try:
            self.screen = pygame.display.set_mode(size, pygame.SCALED | pygame.RESIZABLE)
        except pygame.error:
            self.screen = pygame.display.set_mode(size)

        self.clock = pygame.time.Clock()
        self.running = True

        self.puzzle_files = self._scan_puzzle_files()
        self.current_puzzle_index = 0
        self.solved_indices: set[int] = set()

        self.session = GameSession()
        self.grid_renderer: Optional[GridRenderer] = None

        self.selected_cell: Optional[str] = None
        self.hovered_cell: Optional[str] = None
        self.cell_highlights: dict[str, str] = {}
        self.popover = VerdictPopover()
        self.htp_popup = HowToPlayPopup()

        self.card_feedback: dict[str, dict] = {}
        # U6: Hoạt cảnh lật thẻ, nháy clue khi Step/Auto và banner Solved
        # cell_id -> {"elapsed": float, "duration": float, "status": str, "clue": dict|None, "solved": bool}
        self.flip_anims: dict[str, dict] = {}
        # Nhịp chờ nháy viền clue trước khi lật thẻ lúc Step/Auto
        self.pending_step_anim: Optional[dict] = None
        self.clue_flash_timer: float = 0.0
        self.solved_banner: Optional[SolvedBanner] = None

        self.auto_solve_active = False
        self.auto_solve_last_time = 0.0
        self.auto_solve_delay = 1.25

        self._init_layout()
        if self.puzzle_files:
            self.load_level(0)
        else:
            self.status_bar.set_status("No puzzle files found in data/. Click Load to open a JSON file.", "warning")

    def _scan_puzzle_files(self) -> list[str]:
        candidates = [
            os.path.join(ROOT_DIR, "data"),
            os.path.join(SOURCE_DIR, "data"),
            os.path.join(os.getcwd(), "data"),
        ]
        found: list[str] = []
        for folder in candidates:
            if os.path.isdir(folder):
                for fp in sorted(glob.glob(os.path.join(folder, "*.json"))):
                    if "schema" not in os.path.basename(fp).lower() and fp not in found:
                        found.append(fp)
                if found:
                    break
        return found

    def _name_of(self, cell_id: str) -> str:
        ch = self.session.character(cell_id)
        return ch.get("name", cell_id) if ch else cell_id

    def _init_layout(self):
        w, h = self.screen.get_size()
        pad = 20

        # Viên thuốc chọn màn 1..6 trên thanh trên
        self.level_pills: list[tuple[int, pygame.Rect]] = []
        num_pills = min(6, max(1, len(self.puzzle_files)))
        pill_w, pill_h, pill_gap = 36, 28, 8
        total_pills_w = num_pills * pill_w + (num_pills - 1) * pill_gap
        pill_start_x = int(w * 0.44) - total_pills_w // 2
        for i in range(num_pills):
            r = pygame.Rect(pill_start_x + i * (pill_w + pill_gap), 18, pill_w, pill_h)
            self.level_pills.append((i, r))

        # Nút tròn '?' nhỏ ở góc trên phải để mở lại How to play
        self.btn_help = Button(
            pygame.Rect(w - pad - 32, 16, 32, 32),
            "?",
            color=Theme.BG_PANEL,
            hover_color=Theme.BG_SUBTLE,
            text_color=Theme.TEXT_PRIMARY,
            font=FontManager.get(15, bold=True),
            border_radius=16,
        )

        # Cột phải: Tabbed Side Panel (Clue / Trace / Metrics)
        right_w = max(270, int(w * 0.22))
        body_y = 64
        body_h = h - body_y - pad
        self.side_panel = TabbedSidePanel(pygame.Rect(w - pad - right_w, body_y, right_w, body_h))

        # Khu chính bên trái + giữa: Bàn cờ rộng rãi
        main_x = pad
        main_w = w - right_w - pad * 3
        action_h = 36
        status_h = 50
        # Chừa phần trên bên trái cho tiêu đề & thông tin màn chơi thoáng như game gốc
        grid_top = 80
        grid_h = h - grid_top - status_h - action_h - pad - 14
        self.grid_rect = pygame.Rect(main_x, grid_top, main_w, grid_h)

        # Căn thanh trạng thái và dãy nút hành động gọn gàng dưới lưới
        bar_w = min(main_w, 720)
        bar_x = main_x + (main_w - bar_w) // 2
        self.status_bar = StatusBar(pygame.Rect(bar_x, grid_top + grid_h + 6, bar_w, status_h))

        ay = grid_top + grid_h + status_h + 14
        gap = 10
        btn_specs = [
            ("Hint",    (215, 150, 35), (235, 172, 55)),
            ("Step",    (52,  118, 178), (72,  142, 204)),
            ("Auto",    (46,  148, 82),  (64,  172, 102)),
            ("Restart", (195, 72,  62),  (218, 92,  82)),
            ("Load",    (95,  105, 120), (118, 128, 145)),
        ]
        bw = (bar_w - gap * (len(btn_specs) - 1)) // len(btn_specs)
        self.btn_hint    = Button(pygame.Rect(bar_x, ay, bw, action_h), *btn_specs[0])
        self.btn_step    = Button(pygame.Rect(bar_x + (bw + gap), ay, bw, action_h), *btn_specs[1])
        self.btn_auto    = Button(pygame.Rect(bar_x + (bw + gap) * 2, ay, bw, action_h), *btn_specs[2])
        self.btn_restart = Button(pygame.Rect(bar_x + (bw + gap) * 3, ay, bw, action_h), *btn_specs[3])
        self.btn_load    = Button(pygame.Rect(bar_x + (bw + gap) * 4, ay, bw, action_h), *btn_specs[4])

        self.buttons = [self.btn_help, self.btn_hint, self.btn_step, self.btn_auto, self.btn_restart, self.btn_load]

    def _sync_ui_from_session(self):
        self.side_panel.set_entries(self.session.log)
        self.side_panel.set_metrics(self.session.metrics())

    def load_level(self, index: int):
        if not self.puzzle_files:
            return
        self.current_puzzle_index = index % len(self.puzzle_files)
        self._load_file(self.puzzle_files[self.current_puzzle_index])

    def _clear_animations(self):
        self.flip_anims.clear()
        self.pending_step_anim = None
        self.clue_flash_timer = 0.0
        self.solved_banner = None
        self.card_feedback.clear()

    def _load_file(self, path: str):
        try:
            self.session.load(path)
            self.grid_renderer = GridRenderer(self.grid_rect, self.session.size, self.session.size)
            self.selected_cell = None
            self.cell_highlights.clear()
            self._clear_animations()
            self.popover.close()
            self.side_panel.clear_clue()
            self._stop_auto()
            self._sync_ui_from_session()
            if self.session.warnings:
                self.status_bar.set_status("WARNING: " + "; ".join(self.session.warnings), "warning")
            else:
                self.status_bar.set_status(
                    f"Loaded '{self.session.name}' ({self.session.size}x{self.session.size}). Click a card to begin.",
                    "info",
                )
        except Exception as e:
            self.status_bar.set_status(f"Error loading puzzle: {e}", "contradicted")

    def open_file_dialog(self):
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            file_path = filedialog.askopenfilename(
                title="Select Griductive Puzzle JSON",
                initialdir=os.path.join(ROOT_DIR, "data"),
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            root.destroy()
            if file_path:
                norm_path = os.path.abspath(file_path)
                if norm_path not in [os.path.abspath(p) for p in self.puzzle_files]:
                    self.puzzle_files.append(norm_path)
                    self._init_layout()
                for idx, p in enumerate(self.puzzle_files):
                    if os.path.abspath(p) == norm_path:
                        self.current_puzzle_index = idx
                        break
                self._load_file(norm_path)
        except Exception as e:
            self.status_bar.set_status(f"File dialog error: {e}", "contradicted")

    def restart_level(self):
        self.session.restart()
        self.selected_cell = None
        self.cell_highlights.clear()
        self._clear_animations()
        self.popover.close()
        self.side_panel.clear_clue()
        self._stop_auto()
        self._sync_ui_from_session()
        self.status_bar.set_status("Level restarted.", "info")

    def select_cell(self, cell_id: str, open_popover_if_unrevealed: bool = False, highlight_clue: bool = True):
        self.selected_cell = cell_id
        self.cell_highlights.clear()
        revealed = self.session.statuses()

        if cell_id in revealed:
            self.popover.close()
            clue = self.session.clue_of(cell_id)
            if clue:
                self.side_panel.set_clue(cell_id, self._name_of(cell_id), clue)
                if highlight_clue:
                    roles = clue_roles(clue, self.session.size)
                    for c in roles.get("region2", []):
                        self.cell_highlights[c] = "region2"
                    for c in roles.get("region", []):
                        self.cell_highlights[c] = "region"
                    for c in roles.get("target", []):
                        self.cell_highlights[c] = "target"
            else:
                self.side_panel.clear_clue()
        else:
            if open_popover_if_unrevealed and self.grid_renderer and cell_id in self.grid_renderer.cell_rects:
                self.popover.open_for(
                    cell_id,
                    self.grid_renderer.cell_rects[cell_id],
                    self.screen.get_rect(),
                )
            char = self.session.character(cell_id)
            self.status_bar.set_status(
                f"Selected {cell_id}: {char.get('name', '?')} ({char.get('occupation', '')}) - Choose Criminal or Innocent.",
                "info",
            )
        self._sync_ui_from_session()

    def _start_card_flip(self, cell_id: str, status: Optional[str], clue: Optional[dict], is_solved: bool = False):
        self.flip_anims[cell_id] = {
            "elapsed": 0.0,
            "duration": 0.40,  # 0.20s thu vào + 0.20s mở ra
            "status": status,
            "clue": clue,
            "solved": is_solved,
        }

    def call_verdict(self, verdict: str):
        cid = self.popover.cell_id or self.selected_cell
        if not cid:
            return
        self.popover.close()
        outcome = self.session.submit(cid, verdict)

        if outcome.accepted:
            self.card_feedback.pop(cid, None)
            revealed_now = self.session.statuses()
            clue_now = self.session.clue_of(cid)
            is_solved_now = (self.session.terminal == "SOLVED")

            self.select_cell(cid, open_popover_if_unrevealed=False, highlight_clue=False)
            self._start_card_flip(cid, revealed_now.get(cid), clue_now, is_solved=is_solved_now)

            if is_solved_now:
                self.solved_indices.add(self.current_puzzle_index)
                self.status_bar.set_status(
                    f"SOLVED! All {self.session.size * self.session.size} characters identified.",
                    "correct",
                )
            else:
                self.status_bar.set_status(
                    f"CORRECT: {self._name_of(cid)} ({cid}) is {verdict}. Clue revealed!",
                    "correct",
                )
        elif outcome.code == "CONTRADICTED":
            self.card_feedback[cid] = {"start": time.time(), "duration": 1.6, "tag": "Contradicted", "kind": "contradicted"}
            self.status_bar.set_status(
                f"CONTRADICTED: {self._name_of(cid)} ({cid}) cannot be {verdict} (the opposite is logically forced).",
                "contradicted",
            )
        elif outcome.code == "NOT_PROVABLE":
            self.card_feedback[cid] = {"start": time.time(), "duration": 1.6, "tag": "Not provable", "kind": "not_provable"}
            self.status_bar.set_status(
                f"NOT PROVABLE: Neither verdict is logically forced for {self._name_of(cid)} ({cid}) yet.",
                "not_provable",
            )
        elif outcome.code == "ALREADY_REVEALED":
            self.status_bar.set_status(f"{cid} is already revealed.", "info")
        else:
            self.status_bar.set_status(
                f"Engine returned unexpected result: {outcome.message or outcome.code!r}",
                "contradicted",
            )
        self._sync_ui_from_session()

    def do_hint(self):
        self.popover.close()
        if self.session.is_solved():
            self.status_bar.set_status("Puzzle is already solved!", "correct")
            return
        hint_info = self.session.hint()
        if not hint_info:
            self.status_bar.set_status(
                "INCONSISTENT: revealed clues contradict each other."
                if self.session.terminal == "INCONSISTENT"
                else "STUCK: no verdict is logically forced from the current public clues.",
                "warning",
            )
            return
        # Gợi ý = tô sáng thẻ có thể suy ra (viền ngọc + quầng sáng) và các thẻ chứa clue liên quan (viền hồng).
        self.selected_cell = None
        self.cell_highlights.clear()
        self.cell_highlights[hint_info.cell] = "hint"
        for clue_id in hint_info.clue_ids:
            owner = self.session.clue_owner(clue_id)
            if owner and owner != hint_info.cell:
                self.cell_highlights[owner] = "hint_clue"
        self.status_bar.set_status("Hint: the glowing card can be proved. Pink cards hold the clues it follows from.", "not_provable")
        self._sync_ui_from_session()

    def do_step(self):
        self.popover.close()
        # Nếu còn step trước đang nháy chờ lật thì hoàn tất ngay để không chồng chéo
        if self.pending_step_anim:
            p = self.pending_step_anim
            self.pending_step_anim = None
            self._start_card_flip(p["cell"], p["verdict"], p["clue"], is_solved=p["solved"])

        step_out = self.session.next_step()
        if step_out.kind in ("OK", "SOLVED") and step_out.cell:
            cid = step_out.cell
            is_solved_now = (step_out.kind == "SOLVED")
            self.selected_cell = None
            self.cell_highlights.clear()
            self.cell_highlights[cid] = "hint"

            clue_labels = []
            for clue_id in step_out.clue_ids:
                owner = self.session.clue_owner(clue_id)
                if owner:
                    clue_labels.append(f"clue_{owner}")
                    if owner != cid:
                        self.cell_highlights[owner] = "hint_clue"
                else:
                    clue_labels.append(str(clue_id))

            # Cập nhật tab Clue bên phải nhưng chưa tô highlight vùng của clue mới
            clue_obj = self.session.clue_of(cid)
            if clue_obj:
                # focus=False: không giật tab đang xem (Trace/Metrics) khi Auto chạy
                self.side_panel.set_clue(cid, self._name_of(cid), clue_obj, focus=False)

            # Đặt nhịp nháy viền clue 0.35s trước khi lật thẻ
            self.clue_flash_timer = 0.35
            self.pending_step_anim = {
                "delay": 0.35,
                "cell": cid,
                "verdict": step_out.verdict,
                "clue": clue_obj,
                "solved": is_solved_now,
            }

            basis_txt = f", based on {', '.join(clue_labels)}" if clue_labels else ""
            if is_solved_now:
                self._stop_auto()
                self.solved_indices.add(self.current_puzzle_index)
                self.status_bar.set_status(
                    f"Step {self.session.steps}: {cid} = {step_out.verdict}{basis_txt}. SOLVED!",
                    "correct",
                )
            else:
                self.status_bar.set_status(
                    f"Step {self.session.steps}: {cid} = {step_out.verdict}{basis_txt}",
                    "correct",
                )
        elif step_out.kind == "STUCK":
            self._stop_auto()
            self.status_bar.set_status("STUCK: Solver reached fixpoint; no further verdict is entailed.", "warning")
        elif step_out.kind == "INCONSISTENT":
            self._stop_auto()
            self.status_bar.set_status("INCONSISTENT: Revealed clues contain a logical contradiction!", "contradicted")
        else:
            self._stop_auto()
            self.status_bar.set_status(f"Step failed: {step_out.message or 'unknown error'}", "contradicted")
        self._sync_ui_from_session()

    def _stop_auto(self):
        self.auto_solve_active = False
        self.btn_auto.text = "Auto"
        self.btn_auto.color = (46, 148, 82)

    def toggle_auto(self):
        self.popover.close()
        if self.session.terminal == "STUCK":
            self.session.terminal = None
        elif self.session.terminal is not None:
            self._safe(self.restart_level)
        self.auto_solve_active = not self.auto_solve_active
        if self.auto_solve_active:
            self.btn_auto.text = "Stop"
            self.btn_auto.color = Theme.WARNING_COLOR
            self.auto_solve_last_time = time.time()
        else:
            self._stop_auto()

    def _safe(self, fn, *args):
        try:
            return fn(*args)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            self._stop_auto()
            self.status_bar.set_status(f"Internal error: {type(exc).__name__}: {exc}", "contradicted")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # 1. Pop-up How to play ưu tiên xử lý khi đang mở
            if self.htp_popup.handle_event(event):
                continue

            # 2. Popover chọn Criminal / Innocent
            pop_res = self.popover.handle_event(event)
            if pop_res in ("CRIMINAL", "INNOCENT"):
                self._safe(self.call_verdict, pop_res)
                continue
            elif pop_res == "CLOSED":
                continue

            # 3. Nút '?' mở lại How to play
            if self.btn_help.handle_event(event):
                self.htp_popup.is_open = not self.htp_popup.is_open
                continue

            # 4. Viên thuốc chọn màn
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_pill = False
                for idx, pill_rect in self.level_pills:
                    if pill_rect.collidepoint(event.pos):
                        self.load_level(idx)
                        clicked_pill = True
                        break
                if clicked_pill:
                    continue

            # 5. Các nút hành động (đã xử lý thì KHÔNG để click rơi xuống bước click lưới,
            #    nếu không highlight của Hint/Step bị xoá ngay lập tức)
            button_clicked = True
            if self.btn_load.handle_event(event):
                self.open_file_dialog()
            elif self.btn_restart.handle_event(event):
                self._safe(self.restart_level)
            elif self.btn_hint.handle_event(event):
                self._safe(self.do_hint)
            elif self.btn_step.handle_event(event):
                self._safe(self.do_step)
            elif self.btn_auto.handle_event(event):
                self._safe(self.toggle_auto)
            else:
                button_clicked = False

            self.side_panel.handle_event(event)

            # 6. Click lưới thẻ (bỏ qua click trên nút / panel bên phải để không mất highlight đang xem)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not button_clicked:
                if self.grid_renderer and not self.side_panel.rect.collidepoint(event.pos):
                    clicked = self.grid_renderer.get_cell_at(event.pos)
                    if clicked:
                        self.select_cell(clicked, open_popover_if_unrevealed=True)
                    elif self.grid_rect.collidepoint(event.pos):
                        self.selected_cell = None
                        self.cell_highlights.clear()

            # 7. Phím tắt
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self._safe(self.call_verdict, "CRIMINAL")
                elif event.key == pygame.K_i:
                    self._safe(self.call_verdict, "INNOCENT")
                elif event.key == pygame.K_h:
                    self._safe(self.do_hint)
                elif event.key == pygame.K_SPACE:
                    self._safe(self.do_step)
                elif event.key == pygame.K_a:
                    self._safe(self.toggle_auto)
                elif event.key == pygame.K_r:
                    self._safe(self.restart_level)
                elif event.key == pygame.K_l:
                    self.open_file_dialog()
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    idx = event.key - pygame.K_1
                    if idx < len(self.puzzle_files):
                        self.load_level(idx)

        mpos = pygame.mouse.get_pos()
        self.hovered_cell = self.grid_renderer.get_cell_at(mpos) if self.grid_renderer else None
        self.popover.update_hover(mpos)
        self.htp_popup.update_hover(mpos)
        for btn in self.buttons:
            btn.update_hover(mpos)

    def update(self, dt: float):
        now = time.time()
        expired = [cid for cid, info in self.card_feedback.items() if now - info["start"] > info["duration"]]
        for cid in expired:
            del self.card_feedback[cid]

        # 1. Cập nhật nhịp nháy clue trước khi lật (Step / Auto)
        if self.clue_flash_timer > 0:
            self.clue_flash_timer = max(0.0, self.clue_flash_timer - dt)

        if self.pending_step_anim:
            self.pending_step_anim["delay"] -= dt
            if self.pending_step_anim["delay"] <= 0:
                p = self.pending_step_anim
                self.pending_step_anim = None
                self._start_card_flip(p["cell"], p["verdict"], p["clue"], is_solved=p["solved"])

        # 2. Cập nhật hoạt cảnh lật thẻ
        done_flips = []
        for cid, anim in self.flip_anims.items():
            anim["elapsed"] += dt
            if anim["elapsed"] >= anim["duration"]:
                done_flips.append(cid)
                if anim.get("solved"):
                    self.solved_banner = SolvedBanner(self.session.steps)
        for cid in done_flips:
            del self.flip_anims[cid]

        # 3. Cập nhật banner Solved mờ dần
        if self.solved_banner:
            self.solved_banner.update(dt)
            if self.solved_banner.is_finished:
                self.solved_banner = None

        # 4. Auto-solve
        if self.auto_solve_active and now - self.auto_solve_last_time >= self.auto_solve_delay:
            self.auto_solve_last_time = now
            self._safe(self.do_step)

    def _compute_shake_x(self, cell_id: str, now: float) -> int:
        fb = self.card_feedback.get(cell_id)
        if not fb:
            return 0
        elapsed = now - fb["start"]
        if elapsed > 0.32:
            return 0
        decay = 1.0 - (elapsed / 0.32)
        return int(math.sin(elapsed * 55.0) * 7.0 * decay)

    def draw(self):
        now = time.time()
        self.screen.fill(Theme.BG_MAIN)

        # 1. Logo thám tử + Tiêu đề Griductive + Thông tin màn không đóng khung
        logo = get_detective_logo(36)
        self.screen.blit(logo, (20, 12))
        title_surf = FontManager.title().render("Griductive", True, Theme.TEXT_PRIMARY)
        self.screen.blit(title_surf, (62, 13))

        # Dòng phụ dưới tiêu đề: Tên màn chơi + dãy chấm độ khó
        sub_y = 54
        name_surf = FontManager.get(14, bold=True).render(self.session.name or "Puzzle", True, Theme.TEXT_PRIMARY)
        self.screen.blit(name_surf, (22, sub_y))
        dot_x = 22 + name_surf.get_width() + 12
        for i in range(min(6, max(1, len(self.level_pills)))):
            col = Theme.CONTRADICTED_COLOR if i <= self.current_puzzle_index else Theme.BORDER_SUBTLE
            pygame.draw.circle(self.screen, col, (dot_x + i * 12, sub_y + 9), 4)

        # Viên thuốc chọn màn 1..6
        pill_font = FontManager.mono(12, bold=True)
        for idx, r in self.level_pills:
            is_cur = (idx == self.current_puzzle_index)
            is_done = (idx in self.solved_indices)
            bg = Theme.BORDER_DARK if is_cur else (Theme.INNOCENT_TINT if is_done else Theme.BG_PANEL)
            fg = Theme.WHITE if is_cur else Theme.TEXT_PRIMARY
            pygame.draw.rect(self.screen, bg, r, border_radius=14)
            pygame.draw.rect(self.screen, Theme.BORDER_DARK, r, width=2, border_radius=14)
            lbl = pill_font.render(str(idx + 1), True, fg)
            self.screen.blit(lbl, lbl.get_rect(center=r.center))

        # 2. Lưới thẻ bài ở giữa
        hovered_tooltip: Optional[str] = None
        if self.grid_renderer:
            self.grid_renderer.draw_labels(self.screen)
            revealed_map = self.session.statuses()
            has_active_hl = bool(self.cell_highlights)
            pulse = 0.5 + 0.5 * math.sin(now * 5.0)

            pending_cid = self.pending_step_anim["cell"] if self.pending_step_anim else None

            # Vẽ thẻ được Hint/Step chiếu sáng sau cùng để quầng sáng không bị thẻ kế bên đè lên
            draw_order = sorted(
                self.grid_renderer.cell_rects.items(),
                key=lambda kv: 1 if self.cell_highlights.get(kv[0]) == "hint" else 0,
            )
            for cell_id, rect in draw_order:
                is_rev = (cell_id in revealed_map) and (cell_id != pending_cid)
                hl_role = self.cell_highlights.get(cell_id)
                # Nháy viền clue khi đang ở nhịp suy luận Step/Auto
                if hl_role == "hint_clue" and self.clue_flash_timer > 0:
                    if int(self.clue_flash_timer * 18) % 2 == 1:
                        hl_role = None

                is_sel = (cell_id == self.selected_cell)
                # Chỉ làm mờ thẻ ĐÃ LẬT không liên quan. Thẻ còn úp luôn rõ nét để không bị nhầm là đã lật.
                is_dim = has_active_hl and (hl_role is None) and not is_sel and is_rev

                if cell_id in self.flip_anims:
                    anim = self.flip_anims[cell_id]
                    prog = min(1.0, anim["elapsed"] / anim["duration"])
                    draw_flipping_card(
                        surface=self.screen,
                        rect=rect,
                        progress=prog,
                        cell_id=cell_id,
                        character=self.session.character(cell_id),
                        target_status=anim["status"],
                        target_clue=anim["clue"],
                        is_selected=is_sel,
                        highlight_role=None if hl_role == "hint" else hl_role,
                        name_of=self._name_of,
                    )
                    continue

                fb = self.card_feedback.get(cell_id)
                fb_tag = (fb["tag"], fb["kind"]) if fb else None

                clipped = CardRenderer.draw_card(
                    surface=self.screen,
                    rect=rect,
                    cell_id=cell_id,
                    character=self.session.character(cell_id),
                    is_revealed=is_rev,
                    status=revealed_map.get(cell_id) if is_rev else None,
                    clue=self.session.clue_of(cell_id) if is_rev else None,
                    is_selected=is_sel,
                    highlight_role=hl_role,
                    is_hovered=(cell_id == self.hovered_cell),
                    name_of=self._name_of,
                    dimmed=is_dim,
                    shake_offset_x=self._compute_shake_x(cell_id, now),
                    feedback_tag=fb_tag,
                    pulse=pulse,
                )
                if cell_id == self.hovered_cell and clipped:
                    hovered_tooltip = clipped

        # 3. Thanh trạng thái, nút bấm & tab panel phải
        self.status_bar.draw(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)
        self.side_panel.draw(self.screen, self._name_of)

        # 4. Pop-up How to play (góc trái trên), Popover & Tooltip
        self.htp_popup.draw(self.screen)
        self.popover.draw(self.screen)
        if hovered_tooltip and not self.popover.visible and not self.htp_popup.is_open:
            draw_tooltip(self.screen, hovered_tooltip, pygame.mouse.get_pos())

        if self.solved_banner:
            self.solved_banner.draw(self.screen, self.grid_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(self.FPS) / 1000.0)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

def start_app():
    app = GriductiveApp()
    app.run()


if __name__ == "__main__":
    start_app()