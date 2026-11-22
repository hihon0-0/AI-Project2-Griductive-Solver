"""Design tokens, light/dark themes, and cross-platform font loader (U0)."""
from __future__ import annotations
import os
import pygame

ASSETS_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")


class Theme:
    # Spacing & Radii
    RADIUS_CARD = 12
    RADIUS_PANEL = 10
    RADIUS_BTN = 8
    RADIUS_PILL = 16
    PAD_SM = 8
    PAD_MD = 16
    PAD_LG = 24

    # Light Palette (Game gốc: nền kem, thẻ trắng ngà, viền đen dày)
    BG_MAIN       = (245, 238, 224)
    BG_PANEL      = (252, 249, 242)
    BG_SUBTLE     = (235, 226, 210)
    BG_CARD_DOWN  = (252, 249, 242)
    BG_CARD_HOVER = (255, 253, 248)
    BG_CARD_UP    = (248, 244, 235)

    # Trạng thái thẻ đã lật (tint nhẹ + viền đậm phân biệt màu & hình)
    INNOCENT_TINT   = (214, 234, 214)
    INNOCENT_BORDER = (46,  138, 78)
    CRIMINAL_TINT   = (242, 208, 204)
    CRIMINAL_BORDER = (195, 58,  52)
    HINT_TINT       = (219, 242, 234)   # nền thẻ đang được Hint / Step chiếu sáng

    # Nút bấm
    BG_BUTTON     = (52,  112, 168)
    BG_BTN_HOVER  = (72,  135, 194)
    BG_DISABLED   = (215, 208, 196)

    # Chữ
    TEXT_PRIMARY  = (36,  32,  30)
    TEXT_MUTED    = (120, 112, 104)
    TEXT_ON_DARK  = (252, 249, 242)
    TEXT_CRIMINAL = (185, 45,  42)
    TEXT_INNOCENT = (38,  125, 68)
    TEXT_UNKNOWN  = (185, 130, 20)

    # Viền & 5 màu vai trò (tăng độ đậm để nổi bật trên nền sáng)
    BORDER_DARK      = (40,  36,  34)
    BORDER_SUBTLE    = (205, 196, 182)
    BORDER_ACTIVE    = (230, 165, 20)     # Vàng đậm: ô đang chọn
    ROLE_TARGET      = (225, 115, 20)     # Cam đậm: ô target / tâm NEIGHBORS
    ROLE_REGION      = (35,  125, 215)    # Xanh dương: vùng region 1
    ROLE_REGION2     = (145, 65,  210)    # Tím: vùng region 2
    ROLE_HINT        = (20,  165, 130)    # Xanh ngọc: ô Hint gợi ý
    ROLE_HINT_CLUE   = (215, 55,  125)    # Hồng đậm: ô chứa clue gợi ý

    # Phản hồi & Status Bar
    CORRECT_COLOR      = (46,  148, 82)
    NOT_PROVABLE_COLOR = (210, 145, 20)
    CONTRADICTED_COLOR = (205, 52,  52)
    WARNING_COLOR      = (215, 110, 25)

    WHITE = (255, 255, 255)
    GOLD  = (205, 145, 20)


class FontCatalog:
    _cache: dict[tuple[str, int, bool], pygame.font.Font] = {}

    @classmethod
    def get(cls, family: str, size: int, bold: bool = False) -> pygame.font.Font:
        """family in {'serif', 'sans', 'mono'}"""
        key = (family, size, bold)
        if key not in cls._cache:
            if not pygame.font.get_init():
                pygame.font.init()
            # Ưu tiên font đóng gói trong assets/fonts/
            file_map = {
                ("serif", True):  "Merriweather-Bold.ttf",
                ("serif", False): "Merriweather-Regular.ttf",
                ("sans", True):   "Inter-Bold.ttf",
                ("sans", False):  "Inter-Regular.ttf",
                ("mono", True):   "JetBrainsMono-Bold.ttf",
                ("mono", False):  "JetBrainsMono-Regular.ttf",
            }
            ttf_path = os.path.join(ASSETS_FONT_DIR, file_map.get((family, bold), ""))
            if os.path.isfile(ttf_path):
                font = pygame.font.Font(ttf_path, size)
            else:
                fallback_map = {
                    "serif": "georgia,timesnewroman,dejavuserif,serif",
                    "sans":  "arial,dejavusans,helvetica,segoeui,sans",
                    "mono":  "consolas,dejavusansmono,couriernew,monospace",
                }
                matched = pygame.font.match_font(fallback_map.get(family, "sans"), bold=bold)
                font = pygame.font.Font(matched, size) if matched else pygame.font.SysFont("arial", size, bold=bold)
                if bold and not matched:
                    font.set_bold(True)
            cls._cache[key] = font
        return cls._cache[key]