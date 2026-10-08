"""Render OSD Tape glyphs straight onto PIL images (pixel-perfect, no TTF)."""
from PIL import ImageDraw

from glyphs import ADVANCE, ASCENT, CAP, pixels


def _runs(ch):
    rows = {}
    for c, r in pixels(ch):
        rows.setdefault(r, []).append(c)
    for r, cols in rows.items():
        cols.sort()
        start = prev = cols[0]
        for c in cols[1:] + [None]:
            if c is not None and c == prev + 1:
                prev = c
                continue
            yield r, start, prev
            if c is not None:
                start = prev = c


def text_width(text, scale=1, bold=True, tracking=0):
    if not text:
        return 0
    n = len(text)
    w = (n - 1) * (ADVANCE * scale + tracking) + 5 * scale
    return w + (scale // 2 if bold else 0)


def draw_text(img, x, y, text, scale=1, color=(255, 255, 255, 255), bold=True,
              tracking=0, shadow=None, shadow_off=(1, 1)):
    """Draw text; (x, y) is the top-left of the capital letters."""
    if shadow is not None:
        draw_text(img, x + shadow_off[0] * max(1, scale // 2),
                  y + shadow_off[1] * max(1, scale // 2), text, scale, shadow,
                  bold, tracking)
    d = ImageDraw.Draw(img)
    extra = scale // 2 if bold else 0
    cx = x
    for ch in text:
        for r, c0, c1 in _runs(ch):
            x0 = cx + c0 * scale
            x1 = cx + (c1 + 1) * scale + extra - 1
            y0 = y + r * scale
            d.rectangle([x0, y0, x1, y0 + scale - 1], fill=color)
        cx += ADVANCE * scale + tracking
    return cx


def text_height(scale=1):
    return CAP * scale


__all__ = ["draw_text", "text_width", "text_height", "ASCENT"]
