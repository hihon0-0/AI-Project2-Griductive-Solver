"""Polished UI rendering components for Griductive Solver."""
from __future__ import annotations
import pygame
import math
from typing import Callable, Optional

from Source.gui.theme import Theme, FontCatalog
from Source.gui.avatars import get_avatar
from Source.gui.clue_text import clue_segments, clue_plain_text


Colors = Theme

_LOGO_CACHE: dict[int, pygame.Surface] = {}


def get_detective_logo(size: int = 38) -> pygame.Surface:
    """Vẽ icon thám tử đội nón fedora tối giản sắc nét (supersample 3x)."""
    if size in _LOGO_CACHE:
        return _LOGO_CACHE[size]
    S = size * 3
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    col = Theme.BORDER_DARK

    # Thân áo choàng
    pygame.draw.polygon(surf, col, [
        (int(S * 0.16), int(S * 0.92)),
        (int(S * 0.84), int(S * 0.92)),
        (int(S * 0.72), int(S * 0.62)),
        (int(S * 0.28), int(S * 0.62)),
    ])
    # Cổ áo trắng chữ V
    pygame.draw.polygon(surf, Theme.BG_MAIN, [
        (int(S * 0.40), int(S * 0.62)),
        (int(S * 0.60), int(S * 0.62)),
        (int(S * 0.50), int(S * 0.78)),
    ])
    # Khuôn mặt (bóng tối giản)
    pygame.draw.ellipse(surf, col, pygame.Rect(int(S * 0.34), int(S * 0.34), int(S * 0.32), int(S * 0.30)))
    # Vành nón Fedora
    pygame.draw.ellipse(surf, col, pygame.Rect(int(S * 0.14), int(S * 0.30), int(S * 0.72), int(S * 0.12)))
    # Chóp nón Fedora
    pygame.draw.polygon(surf, col, [
        (int(S * 0.28), int(S * 0.34)),
        (int(S * 0.72), int(S * 0.34)),
        (int(S * 0.64), int(S * 0.12)),
        (int(S * 0.50), int(S * 0.16)),
        (int(S * 0.36), int(S * 0.12)),
    ])
    # Dải ruy băng nón màu kem
    pygame.draw.line(surf, Theme.BG_MAIN, (int(S * 0.29), int(S * 0.31)), (int(S * 0.71), int(S * 0.31)), max(2, S // 26))

    out = pygame.transform.smoothscale(surf, (size, size))
    _LOGO_CACHE[size] = out
    return out


class FontManager:
    @classmethod
    def get(cls, size: int, bold: bool = False, family: str = "sans") -> pygame.font.Font:
        return FontCatalog.get(family, size, bold)

    @classmethod
    def title(cls) -> pygame.font.Font:
        return FontCatalog.get("serif", 28, bold=True)

    @classmethod
    def heading(cls) -> pygame.font.Font:
        return FontCatalog.get("sans", 16, bold=True)

    @classmethod
    def body(cls) -> pygame.font.Font:
        return FontCatalog.get("sans", 14, bold=False)

    @classmethod
    def small(cls) -> pygame.font.Font:
        return FontCatalog.get("sans", 12, bold=False)

    @classmethod
    def mono(cls, size: int = 11, bold: bool = False) -> pygame.font.Font:
        return FontCatalog.get("mono", size, bold=bold)


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    if not text or max_width <= 10:
        return []
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            while font.size(word)[0] > max_width and len(word) > 1:
                cut = len(word) - 1
                while cut > 1 and font.size(word[:cut])[0] > max_width:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            current = word
    if current:
        lines.append(current)
    return lines


def truncate_text(text: str, font: pygame.font.Font, max_width: int) -> str:
    if max_width <= 8:
        return ""
    if font.size(text)[0] <= max_width:
        return text
    while len(text) > 1 and font.size(text + "...")[0] > max_width:
        text = text[:-1]
    return text + "..."


def layout_colored_segments(
    segments: list[tuple[str, Optional[str]]],
    font_regular: pygame.font.Font,
    font_bold: pygame.font.Font,
    max_width: int,
) -> list[list[tuple[str, Optional[str], int]]]:
    """Chia các đoạn thành dòng, trả về từng token (text, role, pixel_width) để căn giữa chính xác."""
    tokens: list[tuple[str, Optional[str]]] = []
    for text, role in segments:
        parts = text.split(" ")
        for idx, part in enumerate(parts):
            word = part + (" " if idx < len(parts) - 1 else "")
            if word:
                tokens.append((word, role))

    lines: list[list[tuple[str, Optional[str], int]]] = []
    cur_line: list[tuple[str, Optional[str], int]] = []
    cur_w = 0

    for tok_txt, role in tokens:
        f = font_bold if role else font_regular
        w = f.size(tok_txt)[0]
        if cur_w + w <= max_width or not cur_line:
            cur_line.append((tok_txt, role, w))
            cur_w += w
        else:
            if cur_line and cur_line[-1][0].endswith(" "):
                lt, lr, _ = cur_line[-1]
                trimmed = lt.rstrip(" ")
                lf = font_bold if lr else font_regular
                cur_line[-1] = (trimmed, lr, lf.size(trimmed)[0])
            lines.append(cur_line)
            stripped = tok_txt.lstrip(" ")
            sw = f.size(stripped)[0]
            cur_line = [(stripped, role, sw)] if stripped else []
            cur_w = sw

    if cur_line:
        if cur_line[-1][0].endswith(" "):
            lt, lr, _ = cur_line[-1]
            trimmed = lt.rstrip(" ")
            lf = font_bold if lr else font_regular
            cur_line[-1] = (trimmed, lr, lf.size(trimmed)[0])
        lines.append(cur_line)
    return lines


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        color: tuple = Theme.BG_BUTTON,
        hover_color: tuple = Theme.BG_BTN_HOVER,
        text_color: tuple = Theme.TEXT_ON_DARK,
        font: Optional[pygame.font.Font] = None,
        enabled: bool = True,
        border_radius: int = 10,
        outline_color: Optional[tuple] = None,
    ):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font or FontManager.get(13, bold=True)
        self.enabled = enabled
        self.border_radius = border_radius
        self.outline_color = outline_color or Theme.BORDER_DARK
        self._hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            self._hovered = False
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update_hover(self, mouse_pos: tuple[int, int]):
        self._hovered = self.rect.collidepoint(mouse_pos) if self.enabled else False

    def draw(self, surface: pygame.Surface):
        bg = Theme.BG_DISABLED if not self.enabled else (self.hover_color if self._hovered else self.color)
        tc = Theme.TEXT_MUTED if not self.enabled else self.text_color
        pygame.draw.rect(surface, bg, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.outline_color, self.rect, width=2, border_radius=self.border_radius)
        txt_surf = self.font.render(self.text, True, tc)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))


class VerdictPopover:
    def __init__(self):
        self.visible: bool = False
        self.cell_id: Optional[str] = None
        self.rect = pygame.Rect(0, 0, 154, 88)
        self.btn_criminal = Button(
            pygame.Rect(0, 0, 136, 32), "Criminal (C)",
            color=Theme.CRIMINAL_BORDER, hover_color=(218, 72, 65),
            text_color=Theme.WHITE, font=FontManager.get(13, bold=True),
        )
        self.btn_innocent = Button(
            pygame.Rect(0, 0, 136, 32), "Innocent (I)",
            color=Theme.INNOCENT_BORDER, hover_color=(60, 165, 92),
            text_color=Theme.WHITE, font=FontManager.get(13, bold=True),
        )

    def open_for(self, cell_id: str, card_rect: pygame.Rect, bounds: pygame.Rect):
        self.cell_id = cell_id
        self.visible = True
        pw, ph = 154, 88
        x = card_rect.right + 6
        if x + pw > bounds.right - 8:
            x = card_rect.left - pw - 6
        x = max(bounds.left + 8, min(bounds.right - pw - 8, x))
        y = max(bounds.top + 8, min(bounds.bottom - ph - 8, card_rect.centery - ph // 2))
        self.rect = pygame.Rect(x, y, pw, ph)
        self.btn_criminal.rect = pygame.Rect(x + 9, y + 9, pw - 18, 32)
        self.btn_innocent.rect = pygame.Rect(x + 9, y + 47, pw - 18, 32)

    def close(self):
        self.visible = False
        self.cell_id = None

    def update_hover(self, mouse_pos: tuple[int, int]):
        if self.visible:
            self.btn_criminal.update_hover(mouse_pos)
            self.btn_innocent.update_hover(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if not self.visible:
            return None
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return "CLOSED"
        if self.btn_criminal.handle_event(event):
            return "CRIMINAL"
        if self.btn_innocent.handle_event(event):
            return "INNOCENT"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                self.close()
                return "CLOSED"
        return None

    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        pygame.draw.rect(surface, (205, 196, 180), self.rect.move(3, 4), border_radius=12)
        pygame.draw.rect(surface, Theme.BG_PANEL, self.rect, border_radius=12)
        pygame.draw.rect(surface, Theme.BORDER_DARK, self.rect, width=2, border_radius=12)
        self.btn_criminal.draw(surface)
        self.btn_innocent.draw(surface)


# ======================================================================== #
#  HowToPlay Pop-up Modal (Mở lúc mới vào, thu gọn thành nút ? ở góc)      #
# ======================================================================== #

class HowToPlayPopup:
    RULES = [
        ("Tap a suspect", "Click any face-down card to call Criminal or Innocent."),
        ("Flips & clues", "A right call flips the card and reveals a true clue."),
        ("Pure deduction", "Never guess - only call what the clues logically prove."),
        ("Need a nudge?", "Use Hint to spotlight the next provable character."),
    ]

    def __init__(self):
        self.is_open: bool = True
        self.rect = pygame.Rect(0, 0, 490, 365)
        self.btn_close = Button(
            pygame.Rect(0, 0, 140, 38),
            "Got it",
            color=Theme.BORDER_DARK,
            hover_color=(72, 66, 62),
            text_color=Theme.WHITE,
            font=FontManager.get(15, bold=True),
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_open:
            return False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
            self.is_open = False
            return True
        if self.btn_close.handle_event(event):
            self.is_open = False
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                self.is_open = False
                return True
        return True

    def update_hover(self, mouse_pos: tuple[int, int]):
        if self.is_open:
            self.btn_close.update_hover(mouse_pos)

    def draw(self, surface: pygame.Surface):
        if not self.is_open:
            return

        sw, sh = surface.get_size()
        backdrop = pygame.Surface((sw, sh), pygame.SRCALPHA)
        backdrop.fill((36, 32, 30, 95))
        surface.blit(backdrop, (0, 0))

        self.rect.center = (sw // 2, sh // 2)
        x, y = self.rect.topleft

        pygame.draw.rect(surface, (40, 36, 34, 70), self.rect.move(4, 6), border_radius=16)
        pygame.draw.rect(surface, Theme.BG_PANEL, self.rect, border_radius=16)
        pygame.draw.rect(surface, Theme.BORDER_DARK, self.rect, width=2, border_radius=16)

        px = x + 28
        py = y + 24
        title_f = FontManager.get(24, bold=True, family="serif")
        surface.blit(title_f.render("How to Play", True, Theme.TEXT_PRIMARY), (px, py))
        py += 34

        sub_f = FontManager.get(15, bold=True)
        body_f = FontManager.get(14)
        surface.blit(sub_f.render("Every person is Criminal or Innocent.", True, Theme.TEXT_PRIMARY), (px, py))
        py += 28
        pygame.draw.line(surface, Theme.BORDER_SUBTLE, (px, py), (self.rect.right - 28, py), 1)
        py += 16

        for idx, (lead, desc) in enumerate(self.RULES, 1):
            pygame.draw.circle(surface, Theme.BG_SUBTLE, (px + 11, py + 10), 11)
            num_s = FontManager.mono(12, bold=True).render(str(idx), True, Theme.TEXT_PRIMARY)
            surface.blit(num_s, num_s.get_rect(center=(px + 11, py + 10)))

            lines = wrap_text(f"{lead}: {desc}", body_f, self.rect.width - 80)
            for l in lines:
                surface.blit(body_f.render(l, True, (75, 68, 62)), (px + 32, py))
                py += 20
            py += 7

        self.btn_close.rect = pygame.Rect(0, 0, 140, 38)
        self.btn_close.rect.centerx = self.rect.centerx
        self.btn_close.rect.bottom = self.rect.bottom - 20
        self.btn_close.draw(surface)

# ======================================================================== #
#  Card Renderer (Giống game gốc: phẳng, thoáng, căn giữa clue)             #
# ======================================================================== #

ROLE_COLORS = {
    "target": Theme.ROLE_TARGET,
    "region": Theme.ROLE_REGION,
    "region2": Theme.ROLE_REGION2,
    "hint": Theme.ROLE_HINT,
    "hint_clue": Theme.ROLE_HINT_CLUE,
}


class CardRenderer:
    CARD_PADDING = 8

    @staticmethod
    def draw_card(
        surface: pygame.Surface,
        rect: pygame.Rect,
        cell_id: str,
        character: dict,
        is_revealed: bool,
        status: Optional[str],
        clue: Optional[dict],
        is_selected: bool = False,
        highlight_role: Optional[str] = None,
        is_hovered: bool = False,
        name_of: Optional[Callable[[str], str]] = None,
        dimmed: bool = False,
        shake_offset_x: int = 0,
        feedback_tag: Optional[tuple[str, str]] = None,
    ) -> Optional[str]:
        pad = CardRenderer.CARD_PADDING
        inner = rect.inflate(-pad, -pad)
        inner.x += shake_offset_x
        if is_hovered and not is_revealed and not is_selected:
            inner.y -= 2

        w, h = inner.width, inner.height
        radius = Theme.RADIUS_CARD
        clipped_clue_text: Optional[str] = None

        if is_revealed and status == "CRIMINAL":
            bg_color = Theme.CRIMINAL_TINT
            border_color = Theme.CRIMINAL_BORDER
        elif is_revealed and status == "INNOCENT":
            bg_color = Theme.INNOCENT_TINT
            border_color = Theme.INNOCENT_BORDER
        elif is_hovered and not is_revealed:
            bg_color = Theme.BG_CARD_HOVER
            border_color = Theme.BORDER_DARK
        else:
            bg_color = Theme.BG_CARD_DOWN
            border_color = Theme.BORDER_DARK

        pygame.draw.rect(surface, bg_color, inner, border_radius=radius)

        border_w = 2
        if highlight_role and highlight_role in ROLE_COLORS:
            border_color = ROLE_COLORS[highlight_role]
            border_w = 3
        if is_selected:
            border_color = Theme.BORDER_ACTIVE
            border_w = 3

        pygame.draw.rect(surface, border_color, inner, width=border_w, border_radius=radius)

        char_name = character.get("name", "?")
        char_occ = character.get("occupation", "")
        char_av_path = character.get("avatar")
        resolver = name_of or (lambda cid: cid)

        is_compact = (h < 132)
        id_font = FontManager.mono(10 if is_compact else 11, bold=True)
        name_font = FontManager.get(13 if is_compact else 16, bold=True)
        occ_font = FontManager.mono(9 if is_compact else 11, bold=False)

        # Mã ô góc trái trên
        id_surf = id_font.render(cell_id, True, Theme.TEXT_MUTED)
        surface.blit(id_surf, (inner.x + 9, inner.y + 7))

        if not is_revealed:
            # --- THẺ ÚP: Avatar không khung tròn ở giữa, Tên đậm, Nghề mono ---
            av_size = max(42, min(int(h * 0.48), int(w * 0.50), 78))
            av_surf = get_avatar(char_name, char_occ, av_size, char_av_path)
            av_y = inner.y + max(16, int(h * 0.13))
            av_rect = av_surf.get_rect(centerx=inner.centerx, top=av_y)
            surface.blit(av_surf, av_rect)

            ny = av_rect.bottom + (3 if is_compact else 6)
            n_str = truncate_text(char_name, name_font, w - 16)
            n_surf = name_font.render(n_str, True, Theme.TEXT_PRIMARY)
            surface.blit(n_surf, n_surf.get_rect(centerx=inner.centerx, top=ny))

            oy = ny + name_font.get_linesize() + 1
            if char_occ and oy + occ_font.get_linesize() <= inner.bottom - 5:
                o_str = truncate_text(char_occ, occ_font, w - 16)
                o_surf = occ_font.render(o_str, True, Theme.TEXT_MUTED)
                surface.blit(o_surf, o_surf.get_rect(centerx=inner.centerx, top=oy))
        else:
            # --- THẺ LẬT: Huy hiệu C/I góc phải + Cụm Avatar/Tên/Nghề căn giữa + Clue căn giữa ---
            badge_r = 8 if is_compact else 10
            badge_cx = inner.right - badge_r - 8
            badge_cy = inner.y + badge_r + 7
            if status in ("CRIMINAL", "INNOCENT"):
                b_col = Theme.CRIMINAL_BORDER if status == "CRIMINAL" else Theme.INNOCENT_BORDER
                b_char = "C" if status == "CRIMINAL" else "I"
                pygame.draw.circle(surface, b_col, (badge_cx, badge_cy), badge_r)
                bc_surf = FontManager.mono(9 if is_compact else 11, bold=True).render(b_char, True, Theme.WHITE)
                surface.blit(bc_surf, bc_surf.get_rect(center=(badge_cx, badge_cy)))

            # Cụm avatar nhỏ + tên + nghề căn giữa phía trên giống game gốc
            small_av = 26 if is_compact else 34
            av_surf = get_avatar(char_name, char_occ, small_av, char_av_path)
            max_txt_w = w - small_av - 44
            n_str = truncate_text(char_name, name_font, max_txt_w)
            o_str = truncate_text(char_occ, occ_font, max_txt_w) if char_occ else ""
            n_surf = name_font.render(n_str, True, Theme.TEXT_PRIMARY)
            o_surf = occ_font.render(o_str, True, Theme.TEXT_MUTED) if o_str else None

            block_w = small_av + 6 + max(n_surf.get_width(), o_surf.get_width() if o_surf else 0)
            start_hx = inner.centerx - block_w // 2
            top_hy = inner.y + (16 if is_compact else 20)

            surface.blit(av_surf, (start_hx, top_hy))
            surface.blit(n_surf, (start_hx + small_av + 6, top_hy))
            if o_surf:
                surface.blit(o_surf, (start_hx + small_av + 6, top_hy + name_font.get_linesize() - 2))

            clue_top = top_hy + max(small_av, name_font.get_linesize() + (occ_font.get_linesize() if o_surf else 0)) + 8

            if clue:
                segs = clue_segments(clue, resolver)
                plain_full = clue_plain_text(clue, resolver)
                avail_h = inner.bottom - clue_top - 8
                avail_w = w - 20

                base_sz = 12 if is_compact else 14
                chosen_sz = base_sz
                f_reg = FontManager.get(chosen_sz, bold=False)
                f_bld = FontManager.get(chosen_sz, bold=True)
                wrapped_lines = layout_colored_segments(segs, f_reg, f_bld, avail_w)

                for step_down in (1, 2):
                    if len(wrapped_lines) * f_reg.get_linesize() <= avail_h:
                        break
                    chosen_sz = max(9, base_sz - step_down)
                    f_reg = FontManager.get(chosen_sz, bold=False)
                    f_bld = FontManager.get(chosen_sz, bold=True)
                    wrapped_lines = layout_colored_segments(segs, f_reg, f_bld, avail_w)

                line_h = f_reg.get_linesize()
                max_lines = max(1, avail_h // line_h)
                if len(wrapped_lines) > max_lines:
                    clipped_clue_text = plain_full

                # Căn giữa theo chiều dọc trong phần không gian còn lại của thẻ
                total_txt_h = min(len(wrapped_lines), max_lines) * line_h
                cy = clue_top + max(0, (avail_h - total_txt_h) // 2)

                line_ascent = max(f_reg.get_ascent(), f_bld.get_ascent())
                for l_idx, line_tokens in enumerate(wrapped_lines[:max_lines]):
                    line_w = sum(tok[2] for tok in line_tokens)
                    cx = inner.centerx - line_w // 2
                    is_last_cut = (l_idx == max_lines - 1 and len(wrapped_lines) > max_lines)
                    for seg_txt, role, _ in line_tokens:
                        col = ROLE_COLORS.get(role, Theme.TEXT_PRIMARY) if role else Theme.TEXT_PRIMARY
                        f_use = f_bld if role else f_reg
                        if is_last_cut:
                            rem = (inner.right - 10) - cx
                            if rem <= 12:
                                break
                            seg_txt = truncate_text(seg_txt, f_use, rem)
                        s_surf = f_use.render(seg_txt, True, col)
                        baseline_y = cy + (line_ascent - f_use.get_ascent())
                        surface.blit(s_surf, (cx, baseline_y))
                        cx += s_surf.get_width()
                    cy += line_h

        if feedback_tag:
            tag_txt, tag_kind = feedback_tag
            tag_bg = Theme.CONTRADICTED_COLOR if tag_kind == "contradicted" else Theme.NOT_PROVABLE_COLOR
            t_font = FontManager.get(11, bold=True)
            t_surf = t_font.render(tag_txt, True, Theme.WHITE)
            pill = pygame.Rect(0, 0, t_surf.get_width() + 14, t_surf.get_height() + 6)
            pill.centerx = inner.centerx
            pill.bottom = inner.bottom - 6
            pygame.draw.rect(surface, tag_bg, pill, border_radius=8)
            pygame.draw.rect(surface, Theme.BORDER_DARK, pill, width=1, border_radius=8)
            surface.blit(t_surf, t_surf.get_rect(center=pill.center))

        if dimmed:
            dim_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            dim_surf.fill((*Theme.BG_MAIN, 145))
            surface.blit(dim_surf, inner.topleft)

        return clipped_clue_text


class GridRenderer:
    def __init__(self, grid_rect: pygame.Rect, rows: int, cols: Optional[int] = None):
        self.grid_rect = grid_rect
        self.rows = rows
        self.cols = cols if cols is not None else rows
        self.label_margin = 24
        self.cell_rects: dict[str, pygame.Rect] = {}
        self._compute_cells()

    def _compute_cells(self):
        area_x = self.grid_rect.x + self.label_margin
        area_y = self.grid_rect.y + self.label_margin
        area_w = self.grid_rect.width - self.label_margin
        area_h = self.grid_rect.height - self.label_margin

        cell_side = min(area_w // max(1, self.cols), area_h // max(1, self.rows))
        total_w = cell_side * self.cols
        total_h = cell_side * self.rows
        start_x = area_x + (area_w - total_w) // 2
        start_y = area_y + (area_h - total_h) // 2

        for r in range(self.rows):
            for c in range(self.cols):
                cell_id = f"{chr(ord('A') + c)}{r + 1}"
                self.cell_rects[cell_id] = pygame.Rect(
                    start_x + c * cell_side,
                    start_y + r * cell_side,
                    cell_side,
                    cell_side,
                )

    def draw_labels(self, surface: pygame.Surface):
        font = FontManager.mono(13, bold=True)
        for c in range(self.cols):
            col_char = chr(ord("A") + c)
            rect = self.cell_rects[f"{col_char}1"]
            lbl = font.render(col_char, True, Theme.TEXT_MUTED)
            surface.blit(lbl, lbl.get_rect(centerx=rect.centerx, bottom=rect.top - 4))

        for r in range(self.rows):
            rect = self.cell_rects[f"A{r + 1}"]
            lbl = font.render(str(r + 1), True, Theme.TEXT_MUTED)
            surface.blit(lbl, lbl.get_rect(right=rect.left - 8, centery=rect.centery))

    def get_cell_at(self, pos: tuple[int, int]) -> Optional[str]:
        for cell_id, rect in self.cell_rects.items():
            if rect.collidepoint(pos):
                return cell_id
        return None


class StatusBar:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.message: str = "Click any face-down card to call Criminal or Innocent."
        self.border_color: tuple = Theme.BORDER_SUBTLE
        self.bg_color: tuple = Theme.BG_PANEL
        self.text_color: tuple = Theme.TEXT_PRIMARY

    def set_status(self, message: str, kind: str = "info"):
        self.message = message
        styles = {
            "correct":      (Theme.CORRECT_COLOR,      (232, 246, 236), Theme.TEXT_INNOCENT),
            "not_provable": (Theme.NOT_PROVABLE_COLOR, (253, 246, 224), (155, 102, 10)),
            "contradicted": (Theme.CONTRADICTED_COLOR, (252, 234, 232), Theme.TEXT_CRIMINAL),
            "warning":      (Theme.WARNING_COLOR,      (253, 240, 225), (165, 80, 15)),
            "info":         (Theme.BORDER_SUBTLE,      Theme.BG_PANEL,    Theme.TEXT_PRIMARY),
        }
        self.border_color, self.bg_color, self.text_color = styles.get(kind, styles["info"])

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, self.border_color, self.rect, width=2, border_radius=10)

        font = FontManager.body()
        lines = wrap_text(self.message, font, self.rect.width - 24)[:2]
        if not lines:
            return
        line_h = font.get_linesize()
        total_h = len(lines) * line_h
        y = self.rect.y + (self.rect.height - total_h) // 2
        for line in lines:
            surface.blit(font.render(line, True, self.text_color), (self.rect.x + 12, y))
            y += line_h


def draw_tooltip(surface: pygame.Surface, text: str, mouse_pos: tuple[int, int]):
    if not text:
        return
    font = FontManager.get(15)
    lines = wrap_text(text, font, 280)
    if not lines:
        return
    line_h = font.get_linesize()
    w = max(font.size(l)[0] for l in lines) + 18
    h = len(lines) * line_h + 12

    sw, sh = surface.get_size()
    x = min(sw - w - 10, mouse_pos[0] + 14)
    y = min(sh - h - 10, mouse_pos[1] + 16)
    box = pygame.Rect(x, y, w, h)

    pygame.draw.rect(surface, Theme.BORDER_DARK, box, border_radius=8)
    pygame.draw.rect(surface, Theme.GOLD, box, width=1, border_radius=8)
    ty = y + 6
    for line in lines:
        surface.blit(font.render(line, True, Theme.WHITE), (x + 9, ty))
        ty += line_h


class TabbedSidePanel:
    TABS = ["Clue", "Trace", "Metrics"]

    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.active_tab: str = "Clue"
        self.tab_rects: dict[str, pygame.Rect] = {}
        self.clue: Optional[dict] = None
        self.cell_id: Optional[str] = None
        self.character_name: Optional[str] = None
        self.entries: list[dict] = []
        self.metrics_data: dict = {}
        self.scroll_offset = 0
        self._compute_tabs()

    def _compute_tabs(self):
        tw = self.rect.width // len(self.TABS)
        for i, name in enumerate(self.TABS):
            self.tab_rects[name] = pygame.Rect(self.rect.x + i * tw, self.rect.y, tw, 36)

    def set_clue(self, cell_id: str, character_name: str, clue: dict):
        self.cell_id = cell_id
        self.character_name = character_name
        self.clue = clue
        self.active_tab = "Clue"

    def clear_clue(self):
        self.clue = None
        self.cell_id = None
        self.character_name = None

    def set_entries(self, entries: list[dict]):
        old_len = len(self.entries)
        self.entries = list(entries)
        max_vis = max(1, (self.rect.height - 48) // 20)
        if len(self.entries) > old_len and len(self.entries) > max_vis:
            self.scroll_offset = len(self.entries) - max_vis

    def set_metrics(self, data: dict):
        self.metrics_data = data

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, r in self.tab_rects.items():
                if r.collidepoint(event.pos):
                    self.active_tab = name
                    return
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.active_tab == "Trace":
                max_vis = max(1, (self.rect.height - 48) // 20)
                max_scroll = max(0, len(self.entries) - max_vis)
                self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y))

    def draw(self, surface: pygame.Surface, name_of: Callable[[str], str]):
        pygame.draw.rect(surface, Theme.BG_PANEL, self.rect, border_radius=12)
        pygame.draw.rect(surface, Theme.BORDER_SUBTLE, self.rect, width=1, border_radius=12)

        tab_font = FontManager.get(13, bold=True)
        for name, r in self.tab_rects.items():
            is_act = (name == self.active_tab)
            bg = Theme.BG_PANEL if is_act else Theme.BG_SUBTLE
            pygame.draw.rect(surface, bg, r, border_top_left_radius=10, border_top_right_radius=10)
            if is_act:
                pygame.draw.line(surface, Theme.BORDER_DARK, (r.x + 10, r.bottom - 2), (r.right - 10, r.bottom - 2), 3)
            col = Theme.TEXT_PRIMARY if is_act else Theme.TEXT_MUTED
            lbl = tab_font.render(name, True, col)
            surface.blit(lbl, lbl.get_rect(center=r.center))

        pygame.draw.line(surface, Theme.BORDER_SUBTLE, (self.rect.x, self.rect.y + 36), (self.rect.right, self.rect.y + 36), 1)
        body_rect = pygame.Rect(self.rect.x + 14, self.rect.y + 46, self.rect.width - 28, self.rect.height - 54)

        if self.active_tab == "Clue":
            self._draw_clue_tab(surface, body_rect, name_of)
        elif self.active_tab == "Trace":
            self._draw_trace_tab(surface, body_rect)
        else:
            self._draw_metrics_tab(surface, body_rect)

    def _draw_clue_tab(self, surface: pygame.Surface, area: pygame.Rect, name_of: Callable[[str], str]):
        small_f = FontManager.small()
        if not self.clue:
            for i, line in enumerate(wrap_text("Click any revealed card to inspect its clue and role highlights.", small_f, area.width)):
                surface.blit(small_f.render(line, True, Theme.TEXT_MUTED), (area.x, area.y + i * 18))
            return

        y = area.y
        hdr = f"{self.cell_id} - {self.character_name}"
        surface.blit(FontManager.get(18, bold=True).render(hdr, True, Theme.TEXT_PRIMARY), (area.x, y))
        y += 26

        segs = clue_segments(self.clue, name_of)
        f_reg = FontManager.get(15, bold=False)
        f_bld = FontManager.get(15, bold=True)
        ## f_reg = FontManager.body()
        ## f_bld = FontManager.get(14, bold=True)
        for line_tokens in layout_colored_segments(segs, f_reg, f_bld, area.width):
            cx = area.x
            for txt, role, _ in line_tokens:
                col = ROLE_COLORS.get(role, Theme.TEXT_PRIMARY) if role else Theme.TEXT_PRIMARY
                f_use = f_bld if role else f_reg
                s = f_use.render(txt, True, col)
                surface.blit(s, (cx, y))
                cx += s.get_width()
            y += f_reg.get_linesize() + 3

        y = area.bottom - 44
        pygame.draw.line(surface, Theme.BORDER_SUBTLE, (area.x, y - 6), (area.right, y - 6), 1)
        legends = [("Target", Theme.ROLE_TARGET), ("Region 1", Theme.ROLE_REGION), ("Region 2", Theme.ROLE_REGION2)]
        lx = area.x
        for label, col in legends:
            pygame.draw.circle(surface, col, (lx + 5, y + 7), 5)
            t = small_f.render(label, True, Theme.TEXT_MUTED)
            surface.blit(t, (lx + 14, y))
            lx += t.get_width() + 24

    def _draw_trace_tab(self, surface: pygame.Surface, area: pygame.Rect):
        font = FontManager.mono(11)
        if not self.entries:
            surface.blit(FontManager.small().render("No steps recorded yet.", True, Theme.TEXT_MUTED), (area.x, area.y))
            return
        y = area.y
        for i in range(self.scroll_offset, len(self.entries)):
            if y + 20 > area.bottom:
                break
            entry = self.entries[i]
            verdict = str(entry.get("verdict", ""))
            v_col = Theme.TEXT_CRIMINAL if "CRIMINAL" in verdict else (
                Theme.TEXT_INNOCENT if "INNOCENT" in verdict else Theme.TEXT_UNKNOWN
            )
            step = entry.get("step")
            prefix = f"#{step:>2d} " if isinstance(step, int) else " x  "
            p_surf = font.render(f"{prefix}{entry.get('cell', '?')} ", True, Theme.TEXT_MUTED)
            v_surf = font.render(verdict, True, v_col)
            surface.blit(p_surf, (area.x, y))
            surface.blit(v_surf, (area.x + p_surf.get_width(), y))
            y += 20

    def _draw_metrics_tab(self, surface: pygame.Surface, area: pygame.Rect):
        font = FontManager.small()
        y = area.y
        for key, val in self.metrics_data.items():
            if y + 22 > area.bottom:
                break
            k_surf = font.render(f"{key}:", True, Theme.TEXT_MUTED)
            v_surf = FontManager.mono(12, bold=True).render(str(val), True, Theme.TEXT_PRIMARY)
            surface.blit(k_surf, (area.x, y))
            surface.blit(v_surf, (area.right - v_surf.get_width(), y))
            y += 22

# ======================================================================== #
# Card Flip Renderer & Fading Solved Banner                            #
# ======================================================================== #

def _ease_in_quad(t: float) -> float:
    return t * t


def _ease_out_quad(t: float) -> float:
    return 1.0 - (1.0 - t) * (1.0 - t)


def draw_flipping_card(
    surface: pygame.Surface,
    rect: pygame.Rect,
    progress: float,  # 0.0 -> 1.0 (0.0..0.5: mặt úp thu nhỏ, 0.5..1.0: mặt ngửa mở ra)
    cell_id: str,
    character: dict,
    target_status: Optional[str],
    target_clue: Optional[dict],
    is_selected: bool = False,
    highlight_role: Optional[str] = None,
    name_of: Optional[Callable[[str], str]] = None,
):
    """Vẽ thẻ đang lật bằng smoothscale theo bề ngang trên Surface tạm (U6)."""
    temp = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    local_rect = pygame.Rect(0, 0, rect.width, rect.height)

    if progress < 0.5:
        # Nửa đầu (0 -> 0.5): mặt úp thu bề ngang về 0
        t = progress / 0.5
        scale_x = max(0.02, 1.0 - _ease_in_quad(t))
        CardRenderer.draw_card(
            surface=temp,
            rect=local_rect,
            cell_id=cell_id,
            character=character,
            is_revealed=False,
            status=None,
            clue=None,
            is_selected=is_selected,
            highlight_role=highlight_role,
            name_of=name_of,
        )
    else:
        # Nửa sau (0.5 -> 1.0): mặt ngửa mở rộng từ 0 về 1
        t = (progress - 0.5) / 0.5
        scale_x = max(0.02, _ease_out_quad(t))
        CardRenderer.draw_card(
            surface=temp,
            rect=local_rect,
            cell_id=cell_id,
            character=character,
            is_revealed=True,
            status=target_status,
            clue=target_clue,
            is_selected=is_selected,
            highlight_role=highlight_role,
            name_of=name_of,
        )

    new_w = max(2, int(rect.width * scale_x))
    scaled = pygame.transform.smoothscale(temp, (new_w, rect.height))
    blit_rect = scaled.get_rect(center=rect.center)
    surface.blit(scaled, blit_rect)


class SolvedBanner:
    """Banner 'Solved in n steps' tự mờ dần, không chặn thao tác chuột (U6)."""

    def __init__(self, steps: int):
        self.text = f"Solved in {steps} step{'s' if steps != 1 else ''}!"
        self.elapsed = 0.0
        self.hold_duration = 2.2
        self.fade_duration = 0.8

    @property
    def is_finished(self) -> bool:
        return self.elapsed >= (self.hold_duration + self.fade_duration)

    def update(self, dt: float):
        self.elapsed += dt

    def draw(self, surface: pygame.Surface, anchor_rect: pygame.Rect):
        if self.is_finished:
            return
        if self.elapsed <= self.hold_duration:
            alpha = 245
        else:
            fade_t = (self.elapsed - self.hold_duration) / self.fade_duration
            alpha = int(245 * max(0.0, 1.0 - fade_t))

        font = FontManager.get(18, bold=True, family="serif")
        txt_surf = font.render(self.text, True, Theme.WHITE)
        bw = txt_surf.get_width() + 44
        bh = txt_surf.get_height() + 18

        banner_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        box = pygame.Rect(0, 0, bw, bh)
        pygame.draw.rect(banner_surf, (*Theme.INNOCENT_BORDER, alpha), box, border_radius=22)
        pygame.draw.rect(banner_surf, (*Theme.BORDER_DARK, alpha), box, width=2, border_radius=22)

        txt_alpha = txt_surf.copy()
        txt_alpha.set_alpha(alpha)
        banner_surf.blit(txt_alpha, txt_alpha.get_rect(center=box.center))

        dst_rect = banner_surf.get_rect(centerx=anchor_rect.centerx, top=anchor_rect.top + 12)
        surface.blit(banner_surf, dst_rect)