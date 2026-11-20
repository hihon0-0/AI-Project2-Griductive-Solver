"""Clean flat-vector procedural avatars matching the original Griductive style."""
from __future__ import annotations
import hashlib
import os
import pygame
from typing import Optional

_AVATAR_CACHE: dict[tuple[str, int, str], pygame.Surface] = {}

SKIN_PALETTE = [
    (246, 214, 188), (236, 194, 162), (218, 170, 134),
    (192, 140, 104), (156, 108, 76),  (118, 78,  54),
]
HAIR_PALETTE = [
    (46, 38, 34),    (88, 58, 42),    (138, 86, 48),
    (196, 152, 82),  (168, 72, 46),   (112, 118, 128),
]
SHIRT_PALETTE = [
    (68, 108, 162),  (192, 82, 76),   (56, 138, 88),
    (216, 132, 54),  (92, 96, 106),   (138, 92, 156),
    (64, 142, 148),  (212, 118, 142),
]


def _hash_bytes(name: str) -> bytes:
    return hashlib.sha256(name.strip().lower().encode("utf-8")).digest()


def get_avatar(
    name: str,
    occupation: str = "",
    size: int = 64,
    avatar_path: Optional[str] = None,
) -> pygame.Surface:
    cache_key = (name, size, avatar_path or "")
    if cache_key in _AVATAR_CACHE:
        return _AVATAR_CACHE[cache_key]

    if avatar_path and os.path.isfile(avatar_path):
        try:
            img = pygame.image.load(avatar_path).convert_alpha()
            surf = pygame.transform.smoothscale(img, (size, size))
            _AVATAR_CACHE[cache_key] = surf
            return surf
        except Exception:
            pass

    # Supersample 3x để nét vẽ cong cực mịn, không răng cưa
    scale = 3
    S = size * scale
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    h = _hash_bytes(name or "Unknown")

    skin = SKIN_PALETTE[h[0] % len(SKIN_PALETTE)]
    skin_shadow = (max(0, skin[0] - 22), max(0, skin[1] - 22), max(0, skin[2] - 22))
    hair = HAIR_PALETTE[h[1] % len(HAIR_PALETTE)]
    shirt = SHIRT_PALETTE[h[2] % len(SHIRT_PALETTE)]
    hair_style = h[3] % 5   # 0: ngắn vuốt, 1: tóc dài ôm vai, 2: búi cao, 3: xoăn bồng, 4: mái ngang
    has_glasses = (h[4] % 4 == 0)
    has_collar = (h[5] % 2 == 0)
    eye_col = (44, 38, 36)

    cx = S // 2

    # 1. Tóc sau (nếu tóc dài hoặc búi cao)
    if hair_style == 1:
        back = pygame.Rect(cx - int(S * 0.25), int(S * 0.20), int(S * 0.50), int(S * 0.48))
        pygame.draw.rect(surf, hair, back, border_radius=int(S * 0.18))
    elif hair_style == 2:
        pygame.draw.circle(surf, hair, (cx, int(S * 0.14)), int(S * 0.11))

    # 2. Vai áo bo tròn mềm mại (không viền đen)
    torso = pygame.Rect(cx - int(S * 0.30), int(S * 0.64), int(S * 0.60), int(S * 0.34))
    pygame.draw.rect(surf, shirt, torso, border_top_left_radius=int(S * 0.18), border_top_right_radius=int(S * 0.18),
                     border_bottom_left_radius=int(S * 0.06), border_bottom_right_radius=int(S * 0.06))

    # Cổ & bóng đổ dưới cằm
    neck = pygame.Rect(cx - int(S * 0.075), int(S * 0.52), int(S * 0.15), int(S * 0.16))
    pygame.draw.rect(surf, skin_shadow, neck, border_radius=int(S * 0.04))

    if has_collar:
        # Cổ áo chữ V trắng
        pygame.draw.polygon(surf, (248, 245, 240), [
            (cx - int(S * 0.10), int(S * 0.64)),
            (cx + int(S * 0.10), int(S * 0.64)),
            (cx, int(S * 0.76)),
        ])

    # 3. Tai & Khuôn mặt oval thanh thoát
    head_w = int(S * 0.40)
    head_h = int(S * 0.44)
    head_rect = pygame.Rect(cx - head_w // 2, int(S * 0.18), head_w, head_h)
    ear_y = head_rect.centery + int(S * 0.02)
    pygame.draw.circle(surf, skin_shadow, (head_rect.left, ear_y), int(S * 0.045))
    pygame.draw.circle(surf, skin_shadow, (head_rect.right, ear_y), int(S * 0.045))
    pygame.draw.ellipse(surf, skin, head_rect)

    # 4. Kiểu tóc phía trước
    if hair_style == 0:
        # Tóc ngắn rẽ ngôi gọn
        top_hair = pygame.Rect(head_rect.x - int(S * 0.01), head_rect.y - int(S * 0.04), head_w + int(S * 0.02), int(head_h * 0.42))
        pygame.draw.ellipse(surf, hair, top_hair)
    elif hair_style in (1, 2):
        # Mái rẽ hai bên dịu dàng
        pygame.draw.arc(surf, hair, head_rect.inflate(4, 4), 0.25, 2.89, width=int(S * 0.09))
    elif hair_style == 3:
        # Tóc xoăn phồng
        for dx, dy, r in [(-0.15, 0.20, 0.09), (-0.07, 0.15, 0.10), (0.04, 0.14, 0.10), (0.14, 0.19, 0.09)]:
            pygame.draw.circle(surf, hair, (cx + int(S * dx), int(S * dy)), int(S * r))
    else:
        # Mái bằng cá tính
        bangs = pygame.Rect(head_rect.x, head_rect.y - int(S * 0.02), head_w, int(head_h * 0.34))
        pygame.draw.rect(surf, hair, bangs, border_top_left_radius=int(S * 0.16), border_top_right_radius=int(S * 0.16))

    # 5. Mắt, lông mày, kính & nụ cười
    eye_dx = int(head_w * 0.22)
    eye_y = head_rect.centery + int(head_h * 0.02)
    eye_r = max(2, int(S * 0.024))
    pygame.draw.circle(surf, eye_col, (cx - eye_dx, eye_y), eye_r)
    pygame.draw.circle(surf, eye_col, (cx + eye_dx, eye_y), eye_r)

    # Lông mày mảnh
    brow_y = eye_y - int(S * 0.045)
    brow_w = int(S * 0.06)
    lw = max(2, S // 45)
    pygame.draw.line(surf, hair, (cx - eye_dx - brow_w // 2, brow_y), (cx - eye_dx + brow_w // 2, brow_y), lw)
    pygame.draw.line(surf, hair, (cx + eye_dx - brow_w // 2, brow_y), (cx + eye_dx + brow_w // 2, brow_y), lw)

    if has_glasses and size >= 32:
        gr = int(S * 0.065)
        glw = max(2, S // 48)
        pygame.draw.circle(surf, (60, 56, 54), (cx - eye_dx, eye_y), gr, width=glw)
        pygame.draw.circle(surf, (60, 56, 54), (cx + eye_dx, eye_y), gr, width=glw)
        pygame.draw.line(surf, (60, 56, 54), (cx - eye_dx + gr, eye_y), (cx + eye_dx - gr, eye_y), glw)

    # Miệng cười tự nhiên
    mouth_rect = pygame.Rect(cx - int(S * 0.055), eye_y + int(S * 0.065), int(S * 0.11), int(S * 0.055))
    pygame.draw.arc(surf, (155, 88, 78), mouth_rect, 3.3, 6.1, width=lw)

    final_surf = pygame.transform.smoothscale(surf, (size, size))
    _AVATAR_CACHE[cache_key] = final_surf
    return final_surf