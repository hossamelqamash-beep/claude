"""Tiny 1-bit pixel-art toolkit used to generate the DeskOS theme.

Every drawing is done on a *logical* canvas holding palette indices:

    0 = transparent, 1 = INK (dark), 2 = PAPER (light)

and is exported as two white alpha masks (ink / paper) upscaled with
nearest-neighbour. EmulationStation tints those masks with the colours of the
selected colorset, so one set of artwork serves every palette and every pixel
stays perfectly sharp on the R36S 640x480 screen.
"""
from __future__ import annotations

import os
from typing import Callable, Iterable, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CLEAR, INK, PAPER = 0, 1, 2
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")

_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _font_cache[key]


# Fonts at logical (1x) scale. They are drawn without anti-aliasing.
def title_font(size: int = 8):
    return font("Silkscreen-Bold.ttf", size)


def label_font(size: int = 8):
    return font("Silkscreen-Regular.ttf", size)


def body_font(size: int = 8):
    return font("Tiny5-Regular.ttf", size)


# --------------------------------------------------------------------------
# Dither patterns (absolute coordinates so neighbouring fills line up)
# --------------------------------------------------------------------------
PATTERNS: dict[str, Callable[[np.ndarray, np.ndarray], np.ndarray]] = {
    "solid": lambda x, y: np.ones_like(x, dtype=bool),
    "checker": lambda x, y: (x + y) % 2 == 0,
    "checker2": lambda x, y: ((x // 2) + (y // 2)) % 2 == 0,
    "d25": lambda x, y: (x % 2 == 0) & (y % 2 == 0),
    "d12": lambda x, y: ((x % 4 == 0) & (y % 4 == 0)) | ((x % 4 == 2) & (y % 4 == 2)),
    "d6": lambda x, y: ((x % 4 == 0) & (y % 4 == 0)),
    "d75": lambda x, y: ~((x % 2 == 0) & (y % 2 == 0)),
    "hlines": lambda x, y: y % 2 == 0,
    "vlines": lambda x, y: x % 2 == 0,
    "hlines3": lambda x, y: y % 3 == 0,
    "diag": lambda x, y: (x + y) % 4 == 0,
    "diag2": lambda x, y: (x - y) % 4 == 0,
    "grid4": lambda x, y: (x % 4 == 0) | (y % 4 == 0),
    "bricks": lambda x, y: (y % 4 == 0) | ((x + (y // 4) * 4) % 8 == 0),
}


class Canvas:
    def __init__(self, w: int, h: int, fill: int = CLEAR):
        self.w, self.h = w, h
        self.a = np.full((h, w), fill, dtype=np.uint8)
        self._yy, self._xx = np.mgrid[0:h, 0:w]

    # ---------------------------------------------------------------- core
    def _mask(self, fn: Callable[[ImageDraw.ImageDraw], None]) -> np.ndarray:
        im = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        fn(d)
        return np.asarray(im) > 127

    def paint(self, mask: np.ndarray, col: int, pat: str | None = None, alt: int | None = None):
        if pat and pat != "solid":
            p = PATTERNS[pat](self._xx, self._yy)
            self.a[mask & p] = col
            if alt is not None:
                self.a[mask & ~p] = alt
        else:
            self.a[mask] = col

    # ---------------------------------------------------------- primitives
    def px(self, x: int, y: int, col: int):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = col

    def rect(self, x, y, w, h, col, pat=None, alt=None):
        if w <= 0 or h <= 0:
            return
        m = np.zeros_like(self.a, dtype=bool)
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        m[y0:y1, x0:x1] = True
        self.paint(m, col, pat, alt)

    def frame(self, x, y, w, h, col, t=1):
        self.rect(x, y, w, t, col)
        self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col)
        self.rect(x + w - t, y, t, h, col)

    def hline(self, x, y, w, col, pat=None):
        self.rect(x, y, w, 1, col, pat)

    def vline(self, x, y, h, col, pat=None):
        self.rect(x, y, 1, h, col, pat)

    def _round_mask(self, x, y, w, h, r):
        m = np.zeros_like(self.a, dtype=bool)
        m[max(0, y):max(0, min(self.h, y + h)), max(0, x):max(0, min(self.w, x + w))] = True
        if r > 0:
            # staircase corners: r=1 removes 1px, r=2 removes 3px, r=3 removes 6px
            for i in range(r):
                for j in range(r - i):
                    for cx, cy in ((x + j, y + i), (x + w - 1 - j, y + i),
                                   (x + j, y + h - 1 - i), (x + w - 1 - j, y + h - 1 - i)):
                        if 0 <= cx < self.w and 0 <= cy < self.h:
                            m[cy, cx] = False
        return m

    def rrect(self, x, y, w, h, col, r=1, pat=None, alt=None):
        self.paint(self._round_mask(x, y, w, h, r), col, pat, alt)

    def box(self, x, y, w, h, fill=PAPER, line=INK, r=1, t=1, pat=None, alt=None):
        """Rounded filled rectangle with a pixel outline."""
        outer = self._round_mask(x, y, w, h, r)
        inner = self._round_mask(x + t, y + t, w - 2 * t, h - 2 * t, max(0, r - 1))
        if fill is not None:
            self.paint(inner, fill, pat, alt)
        if line is not None:
            self.paint(outer & ~inner, line)

    def ellipse(self, x, y, w, h, col, pat=None, alt=None):
        self.paint(self._mask(lambda d: d.ellipse([x, y, x + w - 1, y + h - 1], fill=255)), col, pat, alt)

    def oval(self, x, y, w, h, fill=PAPER, line=INK, pat=None, alt=None):
        outer = self._mask(lambda d: d.ellipse([x, y, x + w - 1, y + h - 1], fill=255))
        inner = self._mask(lambda d: d.ellipse([x + 1, y + 1, x + w - 2, y + h - 2], fill=255))
        if fill is not None:
            self.paint(inner, fill, pat, alt)
        if line is not None:
            self.paint(outer & ~inner, line)

    def circle(self, cx, cy, r, fill=PAPER, line=INK, pat=None):
        self.oval(cx - r, cy - r, 2 * r + 1, 2 * r + 1, fill, line, pat)

    def disc(self, cx, cy, r, col, pat=None):
        self.ellipse(cx - r, cy - r, 2 * r + 1, 2 * r + 1, col, pat)

    def poly(self, pts: Sequence[tuple[int, int]], col, pat=None, alt=None):
        self.paint(self._mask(lambda d: d.polygon(list(pts), fill=255)), col, pat, alt)

    def polybox(self, pts, fill=PAPER, line=INK, pat=None, alt=None):
        m = self._mask(lambda d: d.polygon(list(pts), fill=255))
        o = self._mask(lambda d: d.polygon(list(pts), outline=255))
        if fill is not None:
            self.paint(m & ~o, fill, pat, alt)
        if line is not None:
            self.paint(o, line)

    def line(self, pts: Sequence[tuple[int, int]], col, width=1):
        self.paint(self._mask(lambda d: d.line(list(pts), fill=255, width=width)), col)

    # ----------------------------------------------------------------- text
    def text(self, x, y, s, fnt, col, anchor="la", pat=None) -> int:
        self.paint(self._mask(lambda d: d.text((x, y), s, font=fnt, fill=255, anchor=anchor)), col, pat)
        return int(round(fnt.getlength(s)))

    def text_box(self, x, y, s, fnt, anchor="la"):
        """Returns the bounding box of the drawn text (for layout)."""
        im = Image.new("L", (1, 1))
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        return d.textbbox((x, y), s, font=fnt, anchor=anchor)

    # -------------------------------------------------------------- sprites
    def sprite(self, rows: Iterable[str], x: int, y: int, mapping=None):
        mapping = mapping or {"#": INK, "o": PAPER, ".": None, " ": None, "+": "checker"}
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                v = mapping.get(ch)
                if v is None:
                    continue
                if v == "checker":
                    if (x + i + y + j) % 2 == 0:
                        self.px(x + i, y + j, INK)
                    else:
                        self.px(x + i, y + j, PAPER)
                    continue
                self.px(x + i, y + j, v)

    def blit(self, other: "Canvas", x: int, y: int):
        h, w = other.a.shape
        sx0, sy0 = max(0, -x), max(0, -y)
        dx0, dy0 = max(0, x), max(0, y)
        dx1, dy1 = min(self.w, x + w), min(self.h, y + h)
        if dx1 <= dx0 or dy1 <= dy0:
            return
        src = other.a[sy0:sy0 + (dy1 - dy0), sx0:sx0 + (dx1 - dx0)]
        dst = self.a[dy0:dy1, dx0:dx1]
        dst[src != CLEAR] = src[src != CLEAR]

    def fill_where(self, col_from: int, col_to: int, pat: str):
        """Recolour every `col_from` pixel to `col_to` where the pattern is on."""
        p = PATTERNS[pat](self._xx, self._yy)
        self.a[(self.a == col_from) & p] = col_to

    def bbox(self):
        ys, xs = np.nonzero(self.a)
        if len(xs) == 0:
            return (0, 0, 0, 0)
        return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)

    # --------------------------------------------------------------- export
    def layer(self, col: int, scale: int = 2) -> Image.Image:
        m = (self.a == col).astype(np.uint8) * 255
        rgba = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        rgba[..., :3] = 255
        rgba[..., 3] = m
        im = Image.fromarray(rgba, "RGBA")
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return im

    def save_layers(self, ink_path: str | None, paper_path: str | None, scale=2):
        for col, path in ((INK, ink_path), (PAPER, paper_path)):
            if path:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                self.layer(col, scale).save(path, optimize=True)

    def colored(self, ink_rgb, paper_rgb, scale=2, bg=None) -> Image.Image:
        rgba = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        if bg is not None:
            rgba[..., :3] = bg
            rgba[..., 3] = 255
        rgba[self.a == INK] = (*ink_rgb, 255)
        rgba[self.a == PAPER] = (*paper_rgb, 255)
        im = Image.fromarray(rgba, "RGBA")
        if scale != 1:
            im = im.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return im


def hex2rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
