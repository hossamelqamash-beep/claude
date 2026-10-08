#!/usr/bin/env python3
"""Builds the DeskOS EmulationStation theme for the R36S (640x480).

    python3 emulationstation/tools/build.py

Everything (artwork, XML, previews, splash) is generated from code so the
theme can be re-tuned and rebuilt in seconds.
"""
from __future__ import annotations

import math
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from consoles import ART  # noqa: E402
from pix import (CLEAR, INK, PAPER, Canvas, body_font, font, hex2rgb,  # noqa: E402
                 title_font)
from systems import DEFAULT, S  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
OUT = os.path.join(ROOT, "es-theme-deskos")
PREVIEW = os.path.join(ROOT, "preview")
SCALE = 2
LW, LH = 320, 240           # logical screen
SW, SH = LW * SCALE, LH * SCALE

THEME_NAME = "DeskOS"

PALETTES = {
    # id: (display name, ink, paper)
    "classic": ("Classic Cream", "#2A2C33", "#E9E2C9"),
    "amber": ("Amber CRT", "#1B1308", "#FFB547"),
    "phosphor": ("Green Phosphor", "#0A1910", "#86F29A"),
    "pocket": ("Pocket Pea", "#1E2A1C", "#C4D08C"),
    "ice": ("Ice Blue", "#111A2C", "#CFE2FF"),
    "bubblegum": ("Bubblegum", "#2A1426", "#FFC9E0"),
    "paperwhite": ("Paper White", "#1A1A1A", "#F4F4F0"),
}

WALLPAPERS = {
    "bevel": "Dither Bevel",
    "dots": "Dot Grid",
    "weave": "Weave",
    "scanlines": "Scanlines",
    "plain": "Plain",
}

# font size presets: px sizes at 640x480
FONT_SIZES = {
    #          list (font, px)       desc             meta            menu             title
    "medium": (("Jersey20", 20), ("Jersey15", 15), ("Jersey15", 15), ("Jersey20", 20), ("Jersey15", 15)),
    "small": (("Jersey15", 15), ("Jersey10", 10), ("Jersey10", 10), ("Jersey15", 15), ("Jersey10", 10)),
    "big": (("Jersey25", 25), ("Jersey20", 20), ("Jersey15", 15), ("Jersey25", 25), ("Jersey15", 15)),
}
FONT_SIZE_NAMES = {"medium": "Medium", "small": "Small", "big": "Big"}


# ===========================================================================
# helpers
# ===========================================================================
def P(*parts):
    return os.path.join(OUT, *parts)


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def npair(x, y, w=SW, h=SH):
    return f"{x / w:.6f} {y / h:.6f}"


def fsz(px):
    return f"{px / SH:.6f}"


def hexa(h, a="FF"):
    return h.lstrip("#").upper() + a


# ---------------------------------------------------------------- sprites
ICONS = {
    "mail": [
        "................",
        ".##############.",
        ".#oooooooooooo#.",
        ".##oooooooooo##.",
        ".#o##oooooo##o#.",
        ".#ooo##oo##ooo#.",
        ".#ooooo##ooooo#.",
        ".#oooooooooooo#.",
        ".#oooooooooooo#.",
        ".##############.",
    ],
    "gear": [
        "......####......",
        "......#oo#......",
        "..##..#oo#..##..",
        "..#o###oo###o#..",
        "..##oooooooo##..",
        "....oo####oo....",
        "####oo#..#oo####",
        "#ooooo#..#ooooo#",
        "#ooooo#..#ooooo#",
        "####oo#..#oo####",
        "....oo####oo....",
        "..##oooooooo##..",
        "..#o###oo###o#..",
        "..##..#oo#..##..",
        "......#oo#......",
        "......####......",
    ],
    "card": [
        "......####......",
        "......#oo#......",
        "################",
        "#oooooooooooooo#",
        "#o#####ooooooo##",
        "#o#ooo#o#####oo#",
        "#o#o#o#ooooooo##",
        "#o#ooo#o####ooo#",
        "#o#o#o#ooooooo##",
        "#o#####o#####oo#",
        "#oooooooooooooo#",
        "################",
    ],
    "disk": [
        "##############..",
        "#oo#oooooo#oo##.",
        "#oo#oo##oo#ooo##",
        "#oo#oo##oo#oooo#",
        "#oo#oooooo#oooo#",
        "#ooo######ooooo#",
        "#oooooooooooooo#",
        "#oo##########oo#",
        "#oo#oooooooo#oo#",
        "#oo#o######o#oo#",
        "#oo#oooooooo#oo#",
        "#oo#o######o#oo#",
        "#oo#oooooooo#oo#",
        "################",
    ],
    "trash": [
        ".....######.....",
        "..############..",
        "..#oooooooooo#..",
        "..############..",
        "...#oooooooo#...",
        "...#o#o##o#o#...",
        "...#o#o##o#o#...",
        "...#o#o##o#o#...",
        "...#o#o##o#o#...",
        "...#o#o##o#o#...",
        "...#oooooooo#...",
        "...##########...",
    ],
    "joy": [
        "......####......",
        ".....#oooo#.....",
        ".....#oooo#.....",
        "......####......",
        ".......##.......",
        ".......##.......",
        "..############..",
        ".#oooooooooooo#.",
        ".#o##oooooo##o#.",
        ".#oooooooooooo#.",
        "..############..",
    ],
}

# 7x7 info icons
MINI = {
    "maker": ["#######", "#o#o#o#", "#######", "#ooooo#", "#o#o#o#", "#ooooo#", "#######"],
    "year": ["#.#.#.#", "#######", "#ooooo#", "#o#o#o#", "#ooooo#", "#o#o#o#", "#######"],
    "kind": ["..###..", ".#ooo#.", "#######", "#o#o#o#", "#######", "#ooooo#", "#######"],
    "cpu": [".#.#.#.", "#######", "##ooo##", "##o#o##", "##ooo##", "#######", ".#.#.#."],
    "media": [".#####.", "#ooooo#", "#o###o#", "#o#o#o#", "#o###o#", "#ooooo#", ".#####."],
}


def ink_sprite(c: Canvas, rows, x, y, ink=INK, paper=PAPER):
    c.sprite(rows, x, y, {"#": ink, "o": paper, ".": None, " ": None})


# ===========================================================================
# UI chrome
# ===========================================================================
def window(c: Canvas, x, y, w, h, title, shadow=True, close=True, icon=None):
    """Classic 1-bit desktop window like the reference art."""
    if shadow:
        c.rect(x + 4, y + 4, w, h, PAPER, "checker")
    c.rrect(x, y, w, h, PAPER, r=2)
    c.box(x + 1, y + 1, w - 2, h - 2, fill=PAPER, line=INK, r=1)
    # title bar
    tx = x + 5
    if icon:
        ink_sprite(c, icon, tx, y + 4)
        tx += len(icon[0]) + 3
    tw = c.text(tx, y + 3, title, title_font(8), INK)
    cx0 = tx + tw + 4
    cx1 = x + w - (17 if close else 5)
    if cx1 - cx0 > 4:
        c.rect(cx0, y + 4, cx1 - cx0, 8, INK, "checker")
    if close:
        bx = x + w - 14
        c.box(bx, y + 3, 10, 10, fill=PAPER, line=INK, r=0)
        c.line([(bx + 2, y + 5), (bx + 7, y + 10)], INK)
        c.line([(bx + 7, y + 5), (bx + 2, y + 10)], INK)
    c.hline(x + 2, y + 15, w - 4, INK)
    return (x + 2, y + 16, w - 4, h - 18)   # content rect


def dialog(c: Canvas, x, y, w, h):
    """Dark rounded dialog with a light double outline."""
    c.rrect(x, y, w, h, PAPER, r=3)
    c.rrect(x + 1, y + 1, w - 2, h - 2, INK, r=2)
    c.box(x + 2, y + 2, w - 4, h - 4, fill=INK, line=PAPER, r=2)


def menubar(c: Canvas, x, y, w, items, start_icon=True):
    c.box(x, y, w, 13, fill=PAPER, line=PAPER, r=2)
    c.rect(x + 1, y + 12, w - 2, 1, INK, "checker")
    tx = x + 4
    if start_icon:
        ink_sprite(c, ["..###..", ".#ooo#.", "#o#o#o#", "#ooooo#", "#o###o#", ".#ooo#.", "..###.."], tx, y + 3)
        tx += 12
    for it in items:
        tx += c.text(tx, y + 3, it, body_font(8), INK) + 9
    return tx


def taskbar(c: Canvas, y=222, pill_w=150):
    c.box(4, y, 312, 15, fill=PAPER, line=PAPER, r=2)
    c.rect(5, y, 310, 1, INK, "checker")
    # game-count pill like the "MAX" pill in the reference
    if pill_w:
        c.rrect(7, y + 2, pill_w, 11, INK, r=2)
        ink_sprite(c, ["#######", "#ooooo#", "#o###o#", "#o###o#", "#ooooo#", "#######"], 10, y + 4, PAPER, INK)
        c.vline(7 + pill_w - 7, y + 3, 9, PAPER, "checker")
    # clock well on the right
    c.box(268, y + 2, 46, 11, fill=PAPER, line=INK, r=1)


def wallpaper(kind: str) -> Canvas:
    c = Canvas(LW, LH, INK)
    if kind == "bevel":
        # like the reference: dithered bevel band inside the screen edge
        c.rect(0, 0, LW, 4, PAPER, "checker")
        c.rect(0, 0, 4, LH, PAPER, "checker")
        c.rect(0, LH - 2, LW, 2, PAPER, "d25")
        c.rect(LW - 2, 0, 2, LH, PAPER, "d25")
        c.rect(6, 6, LW - 10, LH - 10, PAPER, "d6")
    elif kind == "dots":
        c.rect(0, 0, LW, LH, PAPER, "d6")
        c.rect(0, 0, LW, 2, PAPER, "checker")
    elif kind == "weave":
        m = np.zeros((LH, LW), dtype=bool)
        yy, xx = np.mgrid[0:LH, 0:LW]
        m |= ((xx % 8 == 0) & (yy % 8 < 4)) | ((yy % 8 == 4) & (xx % 8 >= 4))
        c.a[m] = PAPER
    elif kind == "scanlines":
        c.rect(0, 0, LW, LH, PAPER, "hlines3")
        c.a[(np.mgrid[0:LH, 0:LW][1] % 2 == 1) & (c.a == PAPER)] = INK
    return c


# ===========================================================================
# logos
# ===========================================================================
LOGO_W, LOGO_H = 200, 28
HDR_W, HDR_H = 130, 10


def _text_mask(s, fnt, w, h, x=None, y=0, anchor="la"):
    t = Canvas(w, h)
    t.text(x if x is not None else 0, y, s, fnt, PAPER, anchor)
    return t.a == PAPER


def _dilate(m, r=1):
    o = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o


def _shear(m, k=0.25):
    h, w = m.shape
    o = np.zeros_like(m)
    for y in range(h):
        s = int(round((h - y) * k)) - int(round(h * k / 2))
        o[y] = np.roll(m[y], s)
    return o


def _fit_main(s, maxw):
    for fname, size in (("Silkscreen-Bold.ttf", 16), ("Tiny5-Regular.ttf", 16), ("Silkscreen-Bold.ttf", 8)):
        f = font(fname, size)
        if f.getlength(s) <= maxw:
            return f
    return font("Tiny5-Regular.ttf", 8)


def make_logo(spec, w=LOGO_W, h=LOGO_H) -> np.ndarray:
    """Returns a bool mask of the logo, centred on a w x h canvas."""
    style = spec["style"]
    main = spec["main"]
    pad = 4 if ("outline" in style or "box" in style) else 2
    fmain = _fit_main(main, w - 2 * pad - (8 if "italic" in style else 0) - 4)
    small = body_font(8)
    # measure
    bx = Canvas(1, 1).text_box(0, 0, main, fmain)
    mh = bx[3] - bx[1]
    mw = bx[2] - bx[0]
    lines_h = mh + (8 if spec.get("top") else 0) + (8 if spec.get("sub") else 0)
    y0 = (h - lines_h) // 2
    m = np.zeros((h, w), dtype=bool)
    yy = y0
    if spec.get("top"):
        m |= _text_mask(spec["top"], small, w, h, w // 2, yy - 2, "ma")
        yy += 8
    main_mask = _text_mask(main, fmain, w, h, w // 2 - mw // 2 - bx[0], yy - bx[1])
    main_top, main_bot = yy, yy + mh
    yy += mh
    sub_mask = None
    if spec.get("sub"):
        sub_mask = _text_mask(spec["sub"], small, w, h, w // 2, yy + 1, "ma")
    if "italic" in style:
        main_mask = _shear(main_mask, 0.3)
    deco = np.zeros_like(m)
    if "stripes" in style:
        rows = np.arange(h)[:, None]
        cut = ((rows - main_top) % 3 == 2) & (rows > main_top + 2)
        main_mask = main_mask & ~np.broadcast_to(cut, main_mask.shape)
    if "outline" in style:
        ring = _dilate(main_mask, 2) & ~_dilate(main_mask, 1)
        deco |= ring
    if "shadow" in style:
        # hard 3D extrude, separated from the letters by a 1px gap
        sh = np.roll(np.roll(main_mask, 2, 0), 2, 1) | np.roll(np.roll(main_mask, 1, 0), 1, 1)
        deco |= sh & ~_dilate(main_mask, 1)
    m |= main_mask | deco
    if sub_mask is not None:
        m |= sub_mask
    if "box" in style:
        ys, xs = np.nonzero(main_mask | deco)
        x0, x1 = xs.min() - 4, xs.max() + 5
        y0b, y1b = ys.min() - 3, ys.max() + 4
        b = Canvas(w, h)
        b.rrect(x0, y0b, x1 - x0, y1b - y0b, PAPER, r=2)
        box = b.a == PAPER
        m = (m & ~box) | (box & ~(main_mask | deco))
        # keep a 1px inner keyline so the box reads as a badge
    return m


def make_header_logo(spec) -> np.ndarray:
    s = spec["main"]
    f = title_font(8)
    if f.getlength(s) > HDR_W - 8:
        f = body_font(8)
    m = _text_mask(s, f, HDR_W, HDR_H, 2, 1)
    if "italic" in spec["style"]:
        m = _shear(m, 0.3)
    if "box" in spec["style"]:
        ys, xs = np.nonzero(m)
        b = np.zeros_like(m)
        b[0:HDR_H, 0:xs.max() + 4] = True
        b[0, 0] = b[0, xs.max() + 3] = b[HDR_H - 1, 0] = b[HDR_H - 1, xs.max() + 3] = False
        m = b & ~m
    return m


def mask_png(m: np.ndarray, path, scale=SCALE):
    h, w = m.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = m.astype(np.uint8) * 255
    Image.fromarray(rgba, "RGBA").resize((w * scale, h * scale), Image.NEAREST).save(ensure(path), optimize=True)


# ===========================================================================
# screens
# ===========================================================================
SYS_CONSOLE_WIN = (40, 28, 172, 132)
SYS_INFO_WIN = (196, 52, 118, 102)
SYS_DIALOG = (14, 164, 292, 54)
CAROUSEL = (30, 168, 260, 28)       # logical box for the logo carousel


def system_screen(key, data) -> Canvas:
    c = Canvas(LW, LH)
    menubar(c, 4, 6 + 4, 244, ["File", "Edit", "View", "Games", "Help"])
    # desktop icons
    for i, (ic, lbl) in enumerate((("mail", "Inbox"), ("card", "Profile"), ("disk", "Saves"), ("trash", "Trash"))):
        iy = 34 + i * 30
        ink_sprite(c, ICONS[ic], 10, iy, PAPER, INK)
        bx = c.text_box(18, iy + len(ICONS[ic]) + 3, lbl, body_font(8), "ma")
        c.rect(bx[0] - 1, bx[1] - 1, bx[2] - bx[0] + 2, bx[3] - bx[1] + 2, PAPER)
        c.text(18, iy + len(ICONS[ic]) + 3, lbl, body_font(8), INK, "ma")

    x, y, w, h = SYS_CONSOLE_WIN
    cx, cy, cw, ch = window(c, x, y, w, h, data["short"][:12] + ".SYS", icon=None)
    art = ART[data["art"]]()
    ax = cx + (cw - art.w) // 2
    ay = cy + (ch - art.h) // 2
    c.blit(art, ax, ay)

    x, y, w, h = SYS_INFO_WIN
    ix, iy, iw, ih = window(c, x, y, w, h, "INFO")
    maker, year, kind, cpu, media, tagline = data["info"]
    for i, (k, v) in enumerate((("maker", maker), ("year", year), ("kind", kind), ("cpu", cpu), ("media", media))):
        ry = iy + 4 + i * 11
        ink_sprite(c, MINI[k], ix + 4, ry)
        f = body_font(8)
        while f.getlength(v) > iw - 18 and len(v) > 3:
            v = v[:-2] + "."
        c.text(ix + 15, ry, v, f, INK)
        c.hline(ix + 4, ry + 9, iw - 8, INK, "d6") if i < 4 else None
    # two buttons at the bottom like the reference
    by = y + h - 17
    c.box(x + w - 46, by, 40, 12, fill=PAPER, line=INK, r=1)
    c.text(x + w - 26, by + 3, "PLAY", body_font(8), INK, "ma")
    c.rect(x + w - 44, by + 12, 38, 1, INK)
    c.box(x + 6, by, 30, 12, fill=INK, line=INK, r=1)
    c.text(x + 21, by + 3, "OK", body_font(8), PAPER, "ma")

    x, y, w, h = SYS_DIALOG
    dialog(c, x, y, w, h)
    # carousel arrows
    c.poly([(x + 10, y + 17), (x + 15, y + 12), (x + 15, y + 22)], PAPER)
    c.poly([(x + w - 10, y + 17), (x + w - 15, y + 12), (x + w - 15, y + 22)], PAPER)
    c.text(x + w // 2, y + 39, tagline, body_font(8), PAPER, "ma")
    c.hline(x + 20, y + 35, w - 40, PAPER, "d6")

    taskbar(c)
    return c


GL_LIST_WIN = (4, 26, 152, 194)
GL_ART_WIN = (162, 26, 154, 128)
GL_INFO_WIN = (162, 158, 154, 62)


def gamelist_screen(placeholders=False) -> Canvas:
    c = Canvas(LW, LH)
    menubar(c, 4, 10, 244, [])
    x0 = 16 + 12 + HDR_W + 2
    c.text(244, 13, "View  Sort  Help", body_font(8), INK, "ra")
    window(c, *GL_LIST_WIN, "GAMES", icon=["#####", "#ooo#", "#####", "#ooo#", "#####"])
    ax, ay, aw, ah = window(c, *GL_ART_WIN, "BOX ART")
    ix, iy, iw, ih = window(c, *GL_INFO_WIN, "ABOUT")
    # rating row baseline separator
    c.hline(ix + 3, iy + 13, iw - 6, INK, "d6")
    if placeholders:
        art = no_art_canvas()
        c.blit(art, ax + (aw - art.w) // 2, ay + (ah - art.h) // 2)
        c.text(ix + iw // 2, iy + 22, "No metadata scraped yet.", body_font(8), INK, "ma")
        c.text(ix + iw // 2, iy + 32, "Scrape to fill this window.", body_font(8), INK, "ma")
    taskbar(c, pill_w=0)
    return c


def no_art_canvas() -> Canvas:
    c = Canvas(148, 106)
    # a floppy with a sleepy face
    x, y = 44, 10
    c.box(x, y, 60, 64, fill=PAPER, line=INK, r=1)
    c.polybox([(x + 52, y), (x + 59, y + 7), (x + 59, y)], fill=PAPER, line=None)
    c.rect(x + 12, y, 34, 20, INK)
    c.rect(x + 34, y + 3, 8, 14, PAPER)
    c.box(x + 8, y + 30, 44, 30, fill=PAPER, line=INK, r=0)
    c.line([(x + 18, y + 40), (x + 24, y + 40)], INK, 1)
    c.line([(x + 36, y + 40), (x + 42, y + 40)], INK, 1)
    c.line([(x + 24, y + 50), (x + 28, y + 48), (x + 32, y + 50), (x + 36, y + 48)], INK)
    c.text(x + 58, y - 6, "z", body_font(8), INK)
    c.text(x + 64, y - 12, "Z", body_font(8), INK)
    c.rect(x + 2, y + 66, 60, 2, INK, "checker")
    c.text(74, 84, "NO BOX ART", title_font(8), INK, "ma")
    return c


# ===========================================================================
# per-palette coloured assets
# ===========================================================================
def colored(c: Canvas, pal, scale=SCALE, bg=None):
    _, ink, paper = PALETTES[pal]
    return c.colored(hex2rgb(ink), hex2rgb(paper), scale, bg)


def menu_frame() -> Canvas:
    c = Canvas(24, 24)
    c.rrect(0, 0, 24, 24, PAPER, r=2)
    c.box(1, 1, 22, 22, fill=PAPER, line=INK, r=1)
    c.rect(3, 3, 18, 1, INK, "checker")
    return c


def button_frame(filled=False) -> Canvas:
    c = Canvas(24, 24)
    c.box(0, 0, 24, 24, fill=INK if filled else PAPER, line=INK, r=2)
    if not filled:
        c.hline(2, 21, 20, INK)
    return c


def textedit_frame(active=False) -> Canvas:
    c = Canvas(24, 24)
    c.box(0, 0, 24, 24, fill=PAPER, line=INK, r=0)
    if active:
        c.frame(1, 1, 22, 22, INK)
        c.rect(2, 2, 20, 1, INK, "checker")
    return c


def switch(on: bool) -> Canvas:
    c = Canvas(22, 11)
    c.box(0, 0, 22, 11, fill=INK if on else PAPER, line=INK, r=2)
    if on:
        c.box(12, 2, 8, 7, fill=PAPER, line=PAPER, r=1)
        c.rect(4, 4, 2, 3, PAPER)
    else:
        c.box(2, 2, 8, 7, fill=INK, line=INK, r=1)
        c.frame(14, 4, 4, 3, INK)
    return c


def knob() -> Canvas:
    c = Canvas(9, 9)
    c.box(0, 0, 9, 9, fill=PAPER, line=INK, r=2)
    c.rect(3, 3, 3, 3, INK)
    return c


def fade() -> Canvas:
    c = Canvas(LW, LH)
    c.rect(0, 0, LW, LH, INK, "checker")
    return c


# ---------------------------------------------------------------- hourglass
def hourglass(sand_top: float, frame: int = 0) -> Canvas:
    """sand_top: 1.0 = all sand in the top bulb."""
    c = Canvas(40, 56)
    c.box(2, 0, 36, 5, fill=INK, line=INK, r=1)
    c.box(2, 51, 36, 5, fill=INK, line=INK, r=1)
    c.rect(5, 5, 2, 46, INK)
    c.rect(33, 5, 2, 46, INK)
    glass = [(9, 5), (31, 5), (31, 12), (22, 26), (22, 30), (31, 44), (31, 51), (9, 51), (9, 44), (18, 30), (18, 26), (9, 12)]
    c.polybox(glass, fill=PAPER, line=INK)
    m_top = Canvas(40, 56)
    m_top.poly([(10, 7), (30, 7), (30, 12), (21, 25), (19, 25), (10, 12)], PAPER)
    m_bot = Canvas(40, 56)
    m_bot.poly([(19, 31), (21, 31), (30, 44), (30, 49), (10, 49), (10, 44)], PAPER)
    top_rows = int(round(18 * sand_top))
    for y in range(7, 26):
        if y >= 26 - top_rows:
            c.a[y][(m_top.a[y] == PAPER)] = INK
    bot_rows = int(round(19 * (1 - sand_top)))
    for y in range(31, 50):
        if y >= 50 - bot_rows:
            c.a[y][(m_bot.a[y] == PAPER)] = INK
    if 0.02 < sand_top:
        for y in range(26, 50 - bot_rows):
            if (y + frame) % 3 != 0:
                c.px(20, y, INK)
    c.rect(11, 8, 1, 3, PAPER)
    c.rect(11, 45, 1, 3, PAPER)
    return c


def loading_screen(pal_wall="bevel", sand=0.6, frame=0, progress=0.6, with_text=True) -> Canvas:
    c = wallpaper(pal_wall)
    x, y, w, h = 70, 44, 180, 150
    cx, cy, cw, ch = window(c, x, y, w, h, "PLEASE WAIT", close=False)
    hg = hourglass(sand, frame)
    c.blit(hg, x + (w - hg.w) // 2, cy + 8)
    if with_text:
        tw = title_font(16).getlength("LOADING")
        tx = x + (w - tw - 12) // 2
        c.text(tx, cy + 72, "LOADING", title_font(16), INK)
        for k in range(1 + frame % 3):
            c.rect(int(tx + tw + 2 + k * 4), cy + 86, 2, 2, INK)
    bx, by = x + 16, cy + 96
    c.box(bx, by, w - 32, 12, fill=PAPER, line=INK, r=1)
    fillw = int((w - 36) * progress)
    c.rect(bx + 2, by + 2, fillw, 8, INK, "checker")
    c.rect(bx + 2, by + 2, fillw - (fillw % 4), 8, INK)
    for k in range(bx + 2, bx + 2 + fillw, 4):
        c.vline(k + 3, by + 2, 8, PAPER)
    return c


# ---------------------------------------------------------------- help icons
def help_icon(kind) -> Canvas:
    c = Canvas(8, 8)
    if kind in "ABXY":
        c.box(0, 0, 8, 8, fill=INK, line=INK, r=2)
        letter = {
            "A": [".##.", "#..#", "####", "#..#", "#..#"],
            "B": ["###.", "#..#", "###.", "#..#", "###."],
            "X": ["#..#", ".##.", ".##.", ".##.", "#..#"],
            "Y": ["#..#", "#..#", ".##.", ".##.", ".##."],
        }[kind]
        c.sprite(letter, 2, 1, {"#": CLEAR, ".": None})
        return c
    if kind in ("L", "R"):
        c.box(0, 1, 8, 6, fill=INK, line=INK, r=2)
        letter = {"L": ["#..", "#..", "#..", "###"], "R": ["##.", "#.#", "##.", "#.#"]}[kind]
        c.sprite(letter, 3 if kind == "R" else 3, 2, {"#": CLEAR, ".": None})
        return c
    if kind in ("start", "select"):
        c.box(0, 2, 8, 4, fill=INK, line=INK, r=1)
        if kind == "start":
            c.sprite(["#..", "##.", "#.."], 3, 2, {"#": CLEAR, ".": None})
        else:
            c.rect(2, 3, 4, 2, CLEAR)
        return c
    # d-pad variants
    c.rect(3, 0, 2, 8, INK)
    c.rect(0, 3, 8, 2, INK)
    if kind == "updown":
        c.rect(0, 3, 8, 2, INK, "checker")
        c.rect(3, 0, 2, 8, INK)
    elif kind == "leftright":
        c.rect(3, 0, 2, 8, INK, "checker")
        c.rect(0, 3, 8, 2, INK)
    return c


def star(filled) -> Canvas:
    c = Canvas(8, 8)
    rows = ["...#....", "..###...", "#######.", ".#####..", "..###...", ".##.##..", ".#...#..", "........"]
    if filled:
        c.sprite(rows, 0, 0, {"#": PAPER, ".": None})
    else:
        c.sprite(rows, 0, 0, {"#": PAPER, ".": None})
        inner = ["........", "...#....", "..###...", "..###...", "...#....", "........", "........", "........"]
        c.sprite(inner, 0, 0, {"#": CLEAR, ".": None})
    return c


# ===========================================================================
# XML
# ===========================================================================
def img(name, path, x=0, y=0, w=SW, h=SH, z=1, color=None, extra=True, origin=None, max_size=False, tile=False):
    parts = [f'    <image name="{name}"{" extra=\"true\"" if extra else ""}>']
    parts.append(f"      <pos>{npair(x, y)}</pos>")
    if origin:
        parts.append(f"      <origin>{origin}</origin>")
    parts.append(f"      <{'maxSize' if max_size else 'size'}>{npair(w, h)}</{'maxSize' if max_size else 'size'}>")
    if path:
        parts.append(f"      <path>{path}</path>")
    if color:
        parts.append(f"      <color>{color}</color>")
    if tile:
        parts.append("      <tile>true</tile>")
    parts.append(f"      <zIndex>{z}</zIndex>")
    parts.append("    </image>")
    return "\n".join(parts)


def L(x):
    return x * SCALE


HELP_ICONS = "".join(
    f"\n      <{tag}>../_art/help/{fn}.png</{tag}>" for tag, fn in (
        ("iconUpDown", "updown"), ("iconLeftRight", "leftright"), ("iconUpDownLeftRight", "dpad"),
        ("iconA", "a"), ("iconB", "b"), ("iconX", "x"), ("iconY", "y"), ("iconL", "l"), ("iconR", "r"),
        ("iconStart", "start"), ("iconSelect", "select")))


def main_xml():
    gl = "basic,detailed,video,grid"
    lx, ly, lw, lh = GL_LIST_WIN
    ax, ay, aw, ah = GL_ART_WIN
    ix, iy, iw, ih = GL_INFO_WIN
    # pixel rects (inside the window chrome)
    list_rect = (L(lx) + 10, L(ly) + 36, L(lw) - 20, L(lh) - 44)
    art_c = (L(ax) + L(aw) // 2, L(ay) + 32 + (L(ah) - 36) // 2)
    art_max = (L(aw) - 16, L(ah) - 44)
    info_x = L(ix) + 8
    info_w = L(iw) - 16
    rating = (info_x, L(iy) + 36, 80, 16)
    genre = (info_x + 88, L(iy) + 34, info_w - 88, 20)
    desc = (info_x, L(iy) + 62, info_w, L(ih) - 66)
    cx, cy, cw, chh = CAROUSEL

    x = []
    x.append('<?xml version="1.0" encoding="UTF-8"?>')
    x.append(f"<!-- {THEME_NAME} for EmulationStation (fcamod / ArkOS / AmberELEC / batocera-style) - generated by tools/build.py -->")
    x.append("<theme>")
    x.append("  <formatVersion>7</formatVersion>")
    x.append("")
    x.append("  <!-- ======================= THEME OPTIONS (Main menu > UI settings > Theme configuration) -->")
    x.append("  <!-- the first entry of every subset is the default -->")
    for i, (pid, (name, ink, paper)) in enumerate(PALETTES.items()):
        x.append(f'  <include subset="colorset" name="{pid}" displayName="{name}">./colors/{pid}.xml</include>')
    for fid, name in FONT_SIZE_NAMES.items():
        x.append(f'  <include subset="fontsize" subSetDisplayName="Font size" name="{fid}" displayName="{name}">./fontsize/{fid}.xml</include>')
    for wid, name in WALLPAPERS.items():
        x.append(f'  <include subset="wallpaper" subSetDisplayName="Wallpaper" name="{wid}" displayName="{name}">./wallpaper/{wid}.xml</include>')
    x.append('  <include subset="gamelistview" name="boxart" displayName="Box art (image tag)">./artsource/image.xml</include>')
    x.append('  <include subset="gamelistview" name="thumbnail" displayName="Box art (thumbnail tag)">./artsource/thumbnail.xml</include>')
    x.append('  <include subset="gamelistview" name="marquee" displayName="Logo / marquee tag">./artsource/marquee.xml</include>')
    x.append("")

    # ---------------------------------------------------------------- system
    x.append("  <!-- ======================= SYSTEM VIEW -->")
    x.append('  <view name="system">')
    x.append(img("staticBackground", "../_art/wallpaper/${palette}_${wallpaper}.png", z=0, extra=False))
    x.append(f"""    <carousel name="systemcarousel">
      <type>horizontal</type>
      <pos>{npair(L(cx), L(cy))}</pos>
      <size>{npair(L(cw), L(chh))}</size>
      <logoSize>{npair(L(LOGO_W), L(LOGO_H))}</logoSize>
      <logoScale>1</logoScale>
      <maxLogoCount>1</maxLogoCount>
      <color>00000000</color>
      <defaultTransition>slide</defaultTransition>
      <systemInfoDelay>0</systemInfoDelay>
      <zIndex>40</zIndex>
    </carousel>
    <text name="systemInfo">
      <pos>{npair(L(10) + 18, L(222) + 4)}</pos>
      <size>{npair(L(150) - 34, 22)}</size>
      <alignment>left</alignment>
      <verticalAlignment>center</verticalAlignment>
      <backgroundColor>00000000</backgroundColor>
      <forceUppercase>true</forceUppercase>
      <zIndex>50</zIndex>
    </text>
    <helpsystem name="help">
      <pos>{npair(L(160) + 6, L(222) + 7)}</pos>{HELP_ICONS}
    </helpsystem>""")
    x.append("  </view>")
    x.append("")

    # -------------------------------------------------------------- gamelist
    x.append("  <!-- ======================= GAME LIST: list left, box art top-right (2/3), info bottom-right (1/3) -->")
    x.append(f'  <view name="{gl}">')
    x.append(img("background", "../_art/wallpaper/${palette}_${wallpaper}.png", z=0, extra=False))
    x.append(img("chromePaper", "../_art/ui/gamelist_paper.png", z=2, color="${paperColor}"))
    x.append(img("chromeInk", "../_art/ui/gamelist_ink.png", z=3, color="${inkColor}"))
    x.append(f"""    <image name="logo">
      <pos>{npair(L(16) + 24, L(10) + 3)}</pos>
      <origin>0 0</origin>
      <size>{npair(L(HDR_W), L(HDR_H))}</size>
      <zIndex>10</zIndex>
    </image>
    <text name="logoText">
      <pos>{npair(L(16) + 24, L(10) + 2)}</pos>
      <size>{npair(L(HDR_W), 22)}</size>
      <alignment>left</alignment>
      <forceUppercase>true</forceUppercase>
      <zIndex>10</zIndex>
    </text>
    <textlist name="gamelist">
      <pos>{npair(list_rect[0], list_rect[1])}</pos>
      <size>{npair(list_rect[2], list_rect[3])}</size>
      <alignment>left</alignment>
      <horizontalMargin>0.008</horizontalMargin>
      <forceUppercase>false</forceUppercase>
      <zIndex>20</zIndex>
    </textlist>
    <image name="md_image">
      <origin>0.5 0.5</origin>
      <pos>{npair(*art_c)}</pos>
      <maxSize>{npair(*art_max)}</maxSize>
      <zIndex>20</zIndex>
    </image>
    <image name="md_thumbnail">
      <origin>0.5 0.5</origin>
      <pos>{npair(*art_c)}</pos>
      <maxSize>{npair(*art_max)}</maxSize>
      <visible>false</visible>
      <zIndex>21</zIndex>
    </image>
    <image name="md_marquee">
      <origin>0.5 0.5</origin>
      <pos>{npair(*art_c)}</pos>
      <maxSize>{npair(*art_max)}</maxSize>
      <visible>false</visible>
      <zIndex>21</zIndex>
    </image>
    <video name="md_video">
      <origin>0.5 0.5</origin>
      <pos>{npair(*art_c)}</pos>
      <maxSize>{npair(*art_max)}</maxSize>
      <delay>1.5</delay>
      <showSnapshotNoVideo>true</showSnapshotNoVideo>
      <zIndex>22</zIndex>
    </video>
    <rating name="md_rating">
      <pos>{npair(rating[0], rating[1])}</pos>
      <size>{npair(rating[2], rating[3])}</size>
      <filledPath>../_art/ui/star_filled.png</filledPath>
      <unfilledPath>../_art/ui/star_empty.png</unfilledPath>
      <zIndex>25</zIndex>
    </rating>
    <text name="md_genre">
      <pos>{npair(genre[0], genre[1])}</pos>
      <size>{npair(genre[2], genre[3])}</size>
      <alignment>right</alignment>
      <verticalAlignment>center</verticalAlignment>
      <zIndex>25</zIndex>
    </text>
    <text name="md_description">
      <pos>{npair(desc[0], desc[1])}</pos>
      <size>{npair(desc[2], desc[3])}</size>
      <alignment>left</alignment>
      <lineSpacing>1.1</lineSpacing>
      <zIndex>25</zIndex>
    </text>""")
    # everything else hidden (keeps the right panel clean)
    for n in ("md_name", "md_lbl_rating", "md_lbl_releasedate", "md_lbl_developer", "md_lbl_publisher",
              "md_lbl_genre", "md_lbl_players", "md_lbl_lastplayed", "md_lbl_playcount",
              "md_developer", "md_publisher", "md_players", "md_playcount"):
        x.append(f'    <text name="{n}"><visible>false</visible></text>')
    for n in ("md_releasedate", "md_lastplayed"):
        x.append(f'    <datetime name="{n}"><visible>false</visible></datetime>')
    x.append(f"""    <helpsystem name="help">
      <pos>{npair(L(8) + 4, L(222) + 7)}</pos>{HELP_ICONS}
    </helpsystem>""")
    x.append("  </view>")
    x.append('  <view name="basic">')
    x.append(img("chromeInk", "../_art/ui/gamelist_basic_ink.png", z=3, color="${inkColor}"))
    x.append(img("chromePaper", "../_art/ui/gamelist_basic_paper.png", z=2, color="${paperColor}"))
    x.append("  </view>")
    x.append("")

    # ---------------------------------------------------------------- screen
    x.append("  <!-- ======================= SCREEN: clock sits in the taskbar well (enable 'Show clock' in UI settings) -->")
    x.append(f"""  <view name="screen">
    <text name="clock">
      <pos>{npair(L(268), L(222) + 4)}</pos>
      <size>{npair(L(46), 22)}</size>
      <alignment>center</alignment>
    </text>
  </view>""")
    x.append("")
    x.append("  <!-- ======================= MENUS (same window style as the desktop) -->")
    x.append("""  <view name="menu">
    <menuBackground name="menubg">
      <path>../_art/palette/${palette}/menu_frame.png</path>
      <fadePath>../_art/palette/${palette}/menu_fade.png</fadePath>
      <color>FFFFFFFF</color>
      <cornerSize>16 16</cornerSize>
    </menuBackground>
    <menuSwitch name="menuswitch">
      <pathOn>../_art/palette/${palette}/switch_on.png</pathOn>
      <pathOff>../_art/palette/${palette}/switch_off.png</pathOff>
    </menuSwitch>
    <menuSlider name="menuslider">
      <path>../_art/palette/${palette}/slider_knob.png</path>
    </menuSlider>
    <menuButton name="menubutton">
      <path>../_art/palette/${palette}/button.png</path>
      <filledPath>../_art/palette/${palette}/button_filled.png</filledPath>
    </menuButton>
    <menuTextEdit name="menutextedit">
      <inactive>../_art/palette/${palette}/textedit.png</inactive>
      <active>../_art/palette/${palette}/textedit_active.png</active>
    </menuTextEdit>
  </view>""")
    x.append("</theme>")
    return "\n".join(x) + "\n"


def colors_xml(pid):
    name, ink, paper = PALETTES[pid]
    I, Pp = hexa(ink), hexa(paper)
    sep = hexa(ink, "40")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Colorset: {name} -->
<theme>
  <variables>
    <palette>{pid}</palette>
    <inkColor>{I}</inkColor>
    <paperColor>{Pp}</paperColor>
  </variables>
  <view name="system">
    <carousel name="systemcarousel"><color>00000000</color></carousel>
    <image name="logo"><color>{Pp}</color></image>
    <text name="systemInfo"><color>{Pp}</color></text>
    <helpsystem name="help"><textColor>{I}</textColor><iconColor>{I}</iconColor></helpsystem>
  </view>
  <view name="basic,detailed,video,grid">
    <image name="logo"><color>{I}</color></image>
    <text name="logoText"><color>{I}</color></text>
    <textlist name="gamelist">
      <selectorColor>{I}</selectorColor>
      <selectedColor>{Pp}</selectedColor>
      <primaryColor>{I}</primaryColor>
      <secondaryColor>{I}</secondaryColor>
    </textlist>
    <image name="md_image"><default>../../_art/palette/{pid}/noart.png</default></image>
    <rating name="md_rating"><color>{I}</color><unfilledColor>{I}</unfilledColor></rating>
    <text name="md_genre"><color>{I}</color></text>
    <text name="md_description"><color>{I}</color></text>
    <helpsystem name="help"><textColor>{I}</textColor><iconColor>{I}</iconColor></helpsystem>
  </view>
  <view name="screen">
    <text name="clock"><color>{I}</color></text>
  </view>
  <view name="menu">
    <menuText name="menutitle"><color>{I}</color></menuText>
    <menuText name="menufooter"><color>{I}</color></menuText>
    <menuText name="menutext">
      <color>{I}</color>
      <separatorColor>{sep}</separatorColor>
      <selectorColor>{I}</selectorColor>
      <selectedColor>{Pp}</selectedColor>
    </menuText>
    <menuTextSmall name="menutextsmall"><color>{I}</color></menuTextSmall>
    <menuGroup name="menugroup"><color>{I}</color></menuGroup>
  </view>
</theme>
"""


def fontsize_xml(fid):
    (lf, lp), (df, dp), (mf, mp), (nf, np_), (tf, tp) = FONT_SIZES[fid]
    fp = lambda f: f"../../_art/fonts/{f}-Regular.ttf"  # noqa: E731
    title = "../../_art/fonts/Silkscreen-Bold.ttf"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Font size: {FONT_SIZE_NAMES[fid]}  (list {lp}px, description {dp}px, menu {np_}px) -->
<theme>
  <view name="system">
    <text name="systemInfo"><fontPath>{fp(tf)}</fontPath><fontSize>{fsz(tp)}</fontSize></text>
    <helpsystem name="help"><fontPath>{fp(tf)}</fontPath><fontSize>{fsz(tp)}</fontSize></helpsystem>
  </view>
  <view name="basic,detailed,video,grid">
    <text name="logoText"><fontPath>{title}</fontPath><fontSize>{fsz(16)}</fontSize></text>
    <textlist name="gamelist">
      <fontPath>{fp(lf)}</fontPath>
      <fontSize>{fsz(lp)}</fontSize>
      <lineSpacing>1.35</lineSpacing>
    </textlist>
    <text name="md_genre"><fontPath>{fp(mf)}</fontPath><fontSize>{fsz(mp)}</fontSize></text>
    <text name="md_description"><fontPath>{fp(df)}</fontPath><fontSize>{fsz(dp)}</fontSize></text>
    <helpsystem name="help"><fontPath>{fp(tf)}</fontPath><fontSize>{fsz(tp)}</fontSize></helpsystem>
  </view>
  <view name="screen">
    <text name="clock"><fontPath>{fp(tf)}</fontPath><fontSize>{fsz(tp)}</fontSize></text>
  </view>
  <view name="menu">
    <menuText name="menutitle"><fontPath>{title}</fontPath><fontSize>{fsz(16 if fid != 'big' else 24)}</fontSize></menuText>
    <menuText name="menufooter"><fontPath>{fp(tf)}</fontPath><fontSize>{fsz(tp)}</fontSize></menuText>
    <menuText name="menutext"><fontPath>{fp(nf)}</fontPath><fontSize>{fsz(np_)}</fontSize></menuText>
    <menuTextSmall name="menutextsmall"><fontPath>{fp(df)}</fontPath><fontSize>{fsz(dp)}</fontSize></menuTextSmall>
    <menuGroup name="menugroup"><fontPath>{fp(tf)}</fontPath><fontSize>{fsz(tp)}</fontSize></menuGroup>
  </view>
</theme>
"""


def wallpaper_xml(wid):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Wallpaper: {WALLPAPERS[wid]} -->
<theme>
  <variables>
    <wallpaper>{wid}</wallpaper>
  </variables>
</theme>
"""


def artsource_xml(src):
    vis = {k: ("true" if k == src else "false") for k in ("image", "thumbnail", "marquee")}
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Which gamelist.xml tag fills the BOX ART window -->
<theme>
  <view name="detailed,video">
    <image name="md_image"><visible>{vis['image']}</visible></image>
    <image name="md_thumbnail"><visible>{vis['thumbnail']}</visible></image>
    <image name="md_marquee"><visible>{vis['marquee']}</visible></image>
  </view>
</theme>
"""


def system_xml(folder, key):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<theme>
  <formatVersion>7</formatVersion>
  <include>../_inc/main.xml</include>
  <view name="system">
{img("sysPaper", f"../_art/systems/{key}/screen_paper.png", z=2, color="${paperColor}")}
{img("sysInk", f"../_art/systems/{key}/screen_ink.png", z=3, color="${inkColor}")}
    <image name="logo">
      <path>../_art/systems/{key}/logo.png</path>
    </image>
  </view>
  <view name="basic,detailed,video,grid">
    <image name="logo">
      <path>../_art/systems/{key}/logo_header.png</path>
    </image>
  </view>
</theme>
"""


# ===========================================================================
# preview renderer (approximates what EmulationStation draws on the R36S)
# ===========================================================================
def jfont(name, px):
    return font(f"{name}-Regular.ttf", px)


def tint_mask(path, rgb):
    m = Image.open(path).convert("RGBA")
    a = np.asarray(m)[..., 3]
    out = np.zeros((*a.shape, 4), dtype=np.uint8)
    out[..., :3] = rgb
    out[..., 3] = a
    return Image.fromarray(out, "RGBA")


def preview_system(key, pal="classic", wall="bevel", fid="medium", count="254 games"):
    _, ink, paper = PALETTES[pal]
    ink, paper = hex2rgb(ink), hex2rgb(paper)
    base = Image.open(P("_art", "wallpaper", f"{pal}_{wall}.png")).convert("RGBA")
    base.alpha_composite(tint_mask(P("_art", "systems", key, "screen_paper.png"), paper))
    base.alpha_composite(tint_mask(P("_art", "systems", key, "screen_ink.png"), ink))
    logo = tint_mask(P("_art", "systems", key, "logo.png"), paper)
    cx, cy, cw, ch = CAROUSEL
    base.alpha_composite(logo, (L(cx) + (L(cw) - logo.width) // 2, L(cy)))
    d = ImageDraw.Draw(base)
    d.fontmode = "1"
    tf, tp = FONT_SIZES[fid][4]
    f = jfont(tf, tp)
    d.text((L(10) + 18, L(222) + 4 + 11), count.upper(), font=f, fill=paper, anchor="lm")
    _help(base, d, L(160) + 6, L(222) + 7, [("A", "LAUNCH"), ("B", "BACK"), ("start", "MENU")], ink, f)
    d.text((L(268) + L(46) // 2, L(222) + 4 + 11), "03:40", font=f, fill=ink, anchor="mm")
    return base.convert("RGB")


def _help(base, d, x, y, items, ink, f):
    for k, label in items:
        ic = help_icon(k)
        im = ic.colored(ink, ink, 2)
        base.alpha_composite(im, (x, y))
        x += 18
        d.text((x, y + 8), label, font=f, fill=ink, anchor="lm")
        x += int(f.getlength(label)) + 12


GAMES = ["Aero Fighter Ace", "Bubble Bobble Party", "Castle Crawler II", "Dino Dash", "Ever Quest Mini",
         "Final Lap '91", "Galaxy Raiders", "Hyper Blaster", "Isle of Pixels", "Jungle Jumper",
         "Knightfall", "Lunar Lander DX", "Mega Mech Arena", "Neon Drift", "Ocean Odyssey", "Pixel Pirates"]


def demo_boxart():
    c = Canvas(84, 108)
    c.box(0, 0, 84, 108, fill=PAPER, line=INK, r=1)
    c.rect(1, 1, 82, 14, INK)
    c.text(42, 4, "GALAXY", title_font(8), PAPER, "ma")
    c.rect(4, 18, 76, 66, INK)
    for i in range(0, 76, 6):
        c.px(6 + i, 22 + (i * 7) % 50, PAPER)
    c.poly([(42, 30), (58, 70), (42, 62), (26, 70)], PAPER)
    c.poly([(42, 38), (50, 62), (42, 58), (34, 62)], INK, "checker")
    c.disc(64, 32, 6, PAPER, "d25")
    c.text(42, 88, "RAIDERS", title_font(8), INK, "ma")
    c.rect(4, 98, 30, 6, INK)
    c.text(78, 98, "1P", body_font(8), INK, "ra")
    # pretend it is a real full-colour scan: render with its own colours
    return c.colored((26, 34, 80), (240, 200, 70), 2)


def preview_gamelist(key, pal="classic", wall="bevel", fid="medium", sel=6, basic=False):
    _, ink, paper = PALETTES[pal]
    ink, paper = hex2rgb(ink), hex2rgb(paper)
    base = Image.open(P("_art", "wallpaper", f"{pal}_{wall}.png")).convert("RGBA")
    pre = "gamelist_basic" if basic else "gamelist"
    base.alpha_composite(tint_mask(P("_art", "ui", f"{pre}_paper.png"), paper))
    base.alpha_composite(tint_mask(P("_art", "ui", f"{pre}_ink.png"), ink))
    base.alpha_composite(tint_mask(P("_art", "systems", key, "logo_header.png"), ink), (L(16) + 24, L(10) + 3))
    d = ImageDraw.Draw(base)
    d.fontmode = "1"
    (lf, lp), (df, dp), (mf, mp), _, (tf, tp) = FONT_SIZES[fid]
    lfont = jfont(lf, lp)
    lx, ly, lw, lh = GL_LIST_WIN
    x0, y0, w0, h0 = L(lx) + 10, L(ly) + 36, L(lw) - 20, L(lh) - 44
    rowh = int(round(lp * 1.35))
    nrows = h0 // rowh
    for i, g in enumerate(GAMES[:nrows]):
        yy = y0 + i * rowh
        if i == sel:
            d.rectangle([x0, yy, x0 + w0 - 1, yy + rowh - 1], fill=ink)
        d.text((x0 + 5, yy + rowh // 2), g, font=lfont, fill=paper if i == sel else ink, anchor="lm")
    if not basic:
        ax, ay, aw, ah = GL_ART_WIN
        box = demo_boxart()
        mx, my = L(aw) - 16, L(ah) - 44
        s = min(mx / box.width, my / box.height)
        box = box.resize((int(box.width * s), int(box.height * s)), Image.NEAREST)
        cxp, cyp = L(ax) + L(aw) // 2, L(ay) + 32 + (L(ah) - 36) // 2
        base.alpha_composite(box, (cxp - box.width // 2, cyp - box.height // 2))
        ix, iy, iw, ih = GL_INFO_WIN
        rx, ry = L(ix) + 8, L(iy) + 36
        for k in range(5):
            st = star(k < 4).colored(ink, ink, 2)
            base.alpha_composite(st, (rx + k * 16, ry))
        mfont = jfont(mf, mp)
        d.text((L(ix) + L(iw) - 8, L(iy) + 34 + 10), "Shoot 'em up", font=mfont, fill=ink, anchor="rm")
        dfont = jfont(df, dp)
        text = ("Pilot the last star-fighter of the Federation through 32 waves of "
                "alien raiders. Power up, chain combos and save the galaxy before the "
                "mothership reaches Earth.")
        _wrap(d, text, dfont, L(ix) + 8, L(iy) + 62, L(iw) - 16, L(ih) - 66, ink, 1.1)
    f = jfont(tf, tp)
    _help(base, d, L(8) + 4, L(222) + 7, [("updown", "CHOOSE"), ("A", "LAUNCH"), ("B", "BACK"), ("X", "FAV")], ink, f)
    d.text((L(268) + L(46) // 2, L(222) + 4 + 11), "03:40", font=f, fill=ink, anchor="mm")
    return base.convert("RGB")


def _wrap(d, text, f, x, y, w, h, col, ls=1.0):
    words = text.split()
    line = ""
    lh = int(f.size * ls * 1.05)
    yy = y
    for wd in words:
        t = (line + " " + wd).strip()
        if f.getlength(t) > w:
            if yy + lh > y + h:
                return
            d.text((x, yy), line, font=f, fill=col)
            yy += lh
            line = wd
        else:
            line = t
    if yy + lh <= y + h + 2:
        d.text((x, yy), line, font=f, fill=col)


def preview_menu(pal="classic", wall="bevel", fid="medium"):
    """Approximates the ES main menu drawn with the theme's ninepatch."""
    _, ink, paper = PALETTES[pal]
    inkc, paperc = hex2rgb(ink), hex2rgb(paper)
    base = preview_system("snes", pal, wall, fid).convert("RGBA")
    base.alpha_composite(Image.open(P("_art", "palette", pal, "menu_fade.png")))
    fr = Image.open(P("_art", "palette", pal, "menu_frame.png")).convert("RGBA")
    mx, my, mw, mh = 120, 40, 400, 410
    nine = _ninepatch(fr, mw, mh, 16)
    base.alpha_composite(nine, (mx, my))
    d = ImageDraw.Draw(base)
    d.fontmode = "1"
    (lf, lp), (df, dp), _, (nf, np_), (tf, tp) = FONT_SIZES[fid]
    tfont = font("Silkscreen-Bold.ttf", 16 if fid != "big" else 24)
    d.text((mx + mw // 2, my + 34), "MAIN MENU", font=tfont, fill=inkc, anchor="mm")
    # title bar checker like the windows
    nf_ = jfont(nf, np_)
    items = ["KODI MEDIA CENTER", "GAME SETTINGS", "UI SETTINGS", "SOUND SETTINGS", "NETWORK SETTINGS",
             "SCRAPER", "QUIT"]
    rowh = int(np_ * 2.0)
    yy = my + 62
    for i, it in enumerate(items):
        if yy + rowh > my + mh - 50:
            break
        if i == 2:
            d.rectangle([mx + 16, yy, mx + mw - 17, yy + rowh - 1], fill=inkc)
        d.text((mx + 30, yy + rowh // 2), it, font=nf_, fill=paperc if i == 2 else inkc, anchor="lm")
        d.text((mx + mw - 30, yy + rowh // 2), ">", font=nf_, fill=paperc if i == 2 else inkc, anchor="rm")
        if i != 2:
            d.line([(mx + 24, yy + rowh - 1), (mx + mw - 25, yy + rowh - 1)], fill=inkc + (64,))
        yy += rowh
    f = jfont(tf, tp)
    d.text((mx + mw // 2, my + mh - 30), "DeskOS  -  UI SETTINGS > THEME CONFIGURATION", font=f, fill=inkc, anchor="mm")
    return base.convert("RGB")


def preview_theme_options(pal="classic", wall="bevel", fid="medium"):
    _, ink, paper = PALETTES[pal]
    inkc, paperc = hex2rgb(ink), hex2rgb(paper)
    base = preview_gamelist("snes", pal, wall, fid).convert("RGBA")
    base.alpha_composite(Image.open(P("_art", "palette", pal, "menu_fade.png")))
    fr = Image.open(P("_art", "palette", pal, "menu_frame.png")).convert("RGBA")
    mx, my, mw, mh = 90, 50, 460, 380
    base.alpha_composite(_ninepatch(fr, mw, mh, 16), (mx, my))
    d = ImageDraw.Draw(base)
    d.fontmode = "1"
    (lf, lp), (df, dp), _, (nf, np_), (tf, tp) = FONT_SIZES[fid]
    tfont = font("Silkscreen-Bold.ttf", 16 if fid != "big" else 24)
    d.text((mx + mw // 2, my + 34), "THEME CONFIGURATION", font=tfont, fill=inkc, anchor="mm")
    nf_ = jfont(nf, np_)
    rows = [("THEME COLORSET", PALETTES[pal][0]), ("FONT SIZE", FONT_SIZE_NAMES[fid]),
            ("WALLPAPER", WALLPAPERS[wall]), ("THEME GAMELISTVIEW", "Box art (image tag)"),
            ("GAMELIST VIEW STYLE", "Detailed"), ("TRANSITION STYLE", "Slide")]
    rowh = int(np_ * 2.0)
    yy = my + 62
    for i, (k, v) in enumerate(rows):
        if yy + rowh > my + mh - 20:
            break
        sel = i == 1
        if sel:
            d.rectangle([mx + 16, yy, mx + mw - 17, yy + rowh - 1], fill=inkc)
        col = paperc if sel else inkc
        d.text((mx + 30, yy + rowh // 2), k, font=nf_, fill=col, anchor="lm")
        d.text((mx + mw - 30, yy + rowh // 2), f"<  {v}  >", font=nf_, fill=col, anchor="rm")
        yy += rowh
    return base.convert("RGB")


def _ninepatch(img, w, h, cs):
    out = Image.new("RGBA", (w, h))
    iw, ih = img.size
    xs = [(0, cs, 0, cs), (cs, iw - cs, cs, w - cs), (iw - cs, iw, w - cs, w)]
    ys = [(0, cs, 0, cs), (cs, ih - cs, cs, h - cs), (ih - cs, ih, h - cs, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            part = img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.NEAREST)
            out.paste(part, (dx0, dy0))
    return out


# ===========================================================================
# build
# ===========================================================================
def unique_systems():
    """Groups alias folders that share identical screens."""
    keys = {}
    for folder, data in S.items():
        sig = (data["art"], data["short"], tuple(data["info"]), str(data["logo"]))
        keys.setdefault(sig, []).append(folder)
    out = {}
    for sig, folders in keys.items():
        out[folders[0]] = (S[folders[0]], folders)
    return out


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    os.makedirs(PREVIEW, exist_ok=True)

    # fonts
    fdir = P("_art", "fonts")
    os.makedirs(fdir)
    for f in os.listdir(os.path.join(TOOLS, "fonts")):
        shutil.copy(os.path.join(TOOLS, "fonts", f), fdir)

    # wallpapers per palette
    for wid in WALLPAPERS:
        wc = wallpaper(wid)
        for pid in PALETTES:
            colored(wc, pid).save(ensure(P("_art", "wallpaper", f"{pid}_{wid}.png")), optimize=True)

    # gamelist chrome
    gamelist_screen().save_layers(P("_art", "ui", "gamelist_ink.png"), P("_art", "ui", "gamelist_paper.png"))
    gamelist_screen(True).save_layers(P("_art", "ui", "gamelist_basic_ink.png"), P("_art", "ui", "gamelist_basic_paper.png"))
    # stars & help icons (white masks, tinted by ES)
    star(True).save_layers(None, P("_art", "ui", "star_filled.png"))
    star(False).save_layers(None, P("_art", "ui", "star_empty.png"))
    for k in ("A", "B", "X", "Y", "L", "R", "start", "select", "updown", "leftright", "dpad"):
        help_icon(k).save_layers(P("_art", "help", f"{k.lower()}.png"), None)

    # per palette
    for pid in PALETTES:
        d = lambda n: ensure(P("_art", "palette", pid, n))  # noqa: E731
        colored(menu_frame(), pid).save(d("menu_frame.png"))
        fade_im = colored(fade(), pid)
        a = np.asarray(fade_im).copy()
        a[..., 3] = np.where(a[..., 3] > 0, 200, 0)
        Image.fromarray(a).save(d("menu_fade.png"), optimize=True)
        colored(button_frame(False), pid).save(d("button.png"))
        colored(button_frame(True), pid).save(d("button_filled.png"))
        colored(textedit_frame(False), pid).save(d("textedit.png"))
        colored(textedit_frame(True), pid).save(d("textedit_active.png"))
        colored(switch(True), pid).save(d("switch_on.png"))
        colored(switch(False), pid).save(d("switch_off.png"))
        colored(knob(), pid).save(d("slider_knob.png"))
        na = Canvas(148, 106, PAPER)
        na.blit(no_art_canvas(), 0, 0)
        colored(na, pid).save(d("noart.png"))
        colored(loading_screen("bevel"), pid).save(d("loading.png"), optimize=True)

    # systems
    groups = unique_systems()
    groups["default"] = (DEFAULT, [])
    for key, (data, folders) in groups.items():
        scr = system_screen(key, data)
        scr.save_layers(P("_art", "systems", key, "screen_ink.png"), P("_art", "systems", key, "screen_paper.png"))
        mask_png(make_logo(data["logo"]), P("_art", "systems", key, "logo.png"))
        mask_png(make_header_logo(data["logo"]), P("_art", "systems", key, "logo_header.png"))
        for folder in folders:
            with open(ensure(P(folder, "theme.xml")), "w") as fh:
                fh.write(system_xml(folder, key))
    with open(P("theme.xml"), "w") as fh:
        fh.write(system_xml("default", "default").replace("../_inc/main.xml", "./_inc/main.xml")
                 .replace("../_art/", "./_art/"))

    # XML includes
    with open(ensure(P("_inc", "main.xml")), "w") as fh:
        fh.write(main_xml())
    for pid in PALETTES:
        with open(ensure(P("_inc", "colors", f"{pid}.xml")), "w") as fh:
            fh.write(colors_xml(pid))
    for fid in FONT_SIZES:
        with open(ensure(P("_inc", "fontsize", f"{fid}.xml")), "w") as fh:
            fh.write(fontsize_xml(fid))
    for wid in WALLPAPERS:
        with open(ensure(P("_inc", "wallpaper", f"{wid}.xml")), "w") as fh:
            fh.write(wallpaper_xml(wid))
    for src in ("image", "thumbnail", "marquee"):
        with open(ensure(P("_inc", "artsource", f"{src}.xml")), "w") as fh:
            fh.write(artsource_xml(src))

    build_splash()
    build_previews(groups)
    print(f"built {len(groups)} system screens for {len(S)} folders -> {OUT}")


# ---------------------------------------------------------------- splash
def build_splash():
    sd = os.path.join(ROOT, "splash")
    os.makedirs(sd, exist_ok=True)
    for pid in PALETTES:
        frames = []
        n = 24
        for i in range(n):
            t = i / (n - 1)
            frames.append(colored(loading_screen("bevel", sand=1 - t, frame=i, progress=0.1 + 0.85 * t), pid).convert("P"))
        frames += [frames[-1]] * 4
        frames[0].save(os.path.join(sd, f"loading_{pid}.gif"), save_all=True, append_images=frames[1:],
                       duration=120, loop=0, optimize=True)
        colored(loading_screen("bevel", sand=0.55, frame=1, progress=0.55), pid).convert("RGB").save(
            os.path.join(sd, f"loading_{pid}.png"))
        colored(loading_screen("bevel", sand=0.55, frame=1, progress=0.55), pid).convert("RGB").save(
            os.path.join(sd, f"loading_{pid}.jpg"), quality=95)

    # splash.svg for EmulationStation's own start-up / "Loading..." screen:
    # a crisp hourglass + LOADING plate drawn with <rect>s.
    _, ink, paper = PALETTES["classic"]
    c = Canvas(100, 100)
    c.box(0, 0, 100, 100, fill=PAPER, line=INK, r=3)
    c.rect(3, 3, 94, 9, INK, "checker")
    c.rect(3, 13, 94, 1, INK)
    hg = hourglass(0.55, 1)
    c.blit(hg, 30, 18)
    c.text(50, 80, "LOADING", title_font(8), INK, "ma")
    rects = []
    for col, hexc in ((PAPER, paper), (INK, ink)):
        for y in range(c.h):
            x_ = 0
            while x_ < c.w:
                if c.a[y, x_] == col:
                    run = x_
                    while run < c.w and c.a[y, run] == col:
                        run += 1
                    rects.append(f'<rect x="{x_}" y="{y}" width="{run - x_}" height="1" fill="{hexc}"/>')
                    x_ = run
                else:
                    x_ += 1
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 100 100" '
           'shape-rendering="crispEdges">' + "".join(rects) + "</svg>\n")
    with open(os.path.join(sd, "splash.svg"), "w") as fh:
        fh.write(svg)


def build_previews(groups):
    pv = PREVIEW
    shots = {
        "01_system_snes.png": preview_system("snes"),
        "02_system_gba.png": preview_system("gba"),
        "03_system_psx_amber.png": preview_system("psx", "amber", "dots"),
        "04_gamelist_medium.png": preview_gamelist("snes"),
        "05_gamelist_small.png": preview_gamelist("snes", fid="small"),
        "06_gamelist_big.png": preview_gamelist("snes", fid="big"),
        "07_gamelist_phosphor.png": preview_gamelist("gba", "phosphor", "scanlines"),
        "08_menu.png": preview_menu(),
        "09_theme_options.png": preview_theme_options(),
        "10_system_md_pocket.png": preview_system("megadrive", "pocket", "weave"),
        "11_system_arcade_ice.png": preview_system("arcade", "ice"),
        "12_gamelist_bubblegum.png": preview_gamelist("nes", "bubblegum", "dots"),
    }
    for n, im in shots.items():
        im.save(os.path.join(pv, n))
    # contact sheet of every system screen
    keys = [k for k in groups if k != "default"]
    cols = 6
    tw, th = 320, 240
    rows = (len(keys) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (0, 0, 0))
    for i, k in enumerate(keys):
        im = preview_system(k).resize((tw, th), Image.LANCZOS)
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(os.path.join(pv, "all_systems.png"), optimize=True)
    # palettes strip
    strip = Image.new("RGB", (len(PALETTES) * 320, 240))
    for i, pid in enumerate(PALETTES):
        strip.paste(preview_gamelist("snes", pid).resize((320, 240), Image.LANCZOS), (i * 320, 0))
    strip.save(os.path.join(pv, "palettes.png"))
    Image.open(os.path.join(ROOT, "splash", "loading_classic.png")).save(os.path.join(pv, "13_loading.png"))


if __name__ == "__main__":
    build()
