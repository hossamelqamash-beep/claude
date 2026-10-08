"""1-bit pixel-art hardware illustrations, one function per machine.

Each function draws on a 160x104 logical canvas (shown at 2x = 320x208 px).
INK = dark, PAPER = light; dithers give the in-between greys.
"""
from __future__ import annotations

from pix import CLEAR, INK, PAPER, Canvas, body_font, label_font, title_font

W, H = 160, 104


# ---------------------------------------------------------------- helpers
def new() -> Canvas:
    return Canvas(W, H)


def shadow(c: Canvas, x, y, w, h=2):
    c.rect(x + 2, y, w - 1, h, INK, "checker")


def tiny(c: Canvas, x, y, s, col=INK, anchor="la", plate=True):
    """3x5-ish micro label (Tiny5 at 8px has a 5px cap height).

    With `plate` the text sits on a 1px knock-out plate so it stays legible
    on top of dithered surfaces."""
    if plate:
        x0, y0, x1, y1 = c.text_box(x, y, s, body_font(8), anchor)
        c.rect(x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2, PAPER if col == INK else INK)
    c.text(x, y, s, body_font(8), col, anchor)


def dpad(c: Canvas, cx, cy, s=3, col=INK, hole=PAPER):
    """Cross d-pad centred at cx,cy. s = arm width."""
    a = s * 3
    c.rect(cx - s // 2 - s, cy - s // 2, a, s, col)
    c.rect(cx - s // 2, cy - s // 2 - s, s, a, col)
    if hole is not None and s >= 3:
        c.px(cx, cy, hole)


def btn(c: Canvas, cx, cy, r=2, fill=INK, line=INK):
    if r <= 1:
        c.rect(cx - 1, cy - 1, 2, 2, fill)
        return
    c.circle(cx, cy, r, fill=fill, line=line)


def pill(c: Canvas, x, y, w=5, h=2, col=INK):
    c.rrect(x, y, w, h, col, r=1 if h > 2 else 0)


def grille(c: Canvas, x, y, w, h, step=2, col=INK):
    for i in range(0, h, step):
        c.hline(x, y + i, w, col)


def vgrille(c: Canvas, x, y, w, h, step=2, col=INK):
    for i in range(0, w, step):
        c.vline(x + i, y, h, col)


def scene(c: Canvas, x, y, w, h, style="platform"):
    """A tiny generic 'game' running on a screen. Paper background."""
    c.rect(x, y, w, h, PAPER)
    if style == "dark":
        c.rect(x, y, w, h, INK)
        return
    if style == "lines":
        c.rect(x, y, w, h, INK, "hlines")
        return
    if style == "tetris":
        c.rect(x, y, w, h, PAPER)
        c.rect(x, y + h - 3, w, 3, INK, "checker")
        c.rect(x + w // 2 - 2, y + h - 7, 4, 4, INK)
        c.rect(x + w // 2 - 4, y + h - 5, 2, 2, INK)
        c.rect(x + w // 2 - 1, y + 3, 4, 2, INK)
        c.rect(x + w // 2 + 1, y + 1, 2, 2, INK)
        return
    if style == "space":
        c.rect(x, y, w, h, INK)
        for i in range(0, w, 7):
            c.px(x + i + 2, y + (i * 5) % max(1, h - 2) + 1, PAPER)
        cx = x + w // 2
        c.rect(cx - 1, y + h - 5, 3, 2, PAPER)
        c.rect(cx - 2, y + h - 3, 5, 1, PAPER)
        c.px(cx, y + h - 7, PAPER)
        c.px(cx, y + h - 9, PAPER)
        c.rect(x + 3, y + 2, 3, 2, PAPER)
        c.rect(x + w - 7, y + 3, 3, 2, PAPER)
        return
    # platformer: sky, sun, ground, hero, block
    gy = y + h - max(3, h // 5)
    c.rect(x, gy, w, y + h - gy, INK, "checker")
    c.hline(x, gy, w, INK)
    if w > 18:
        c.rect(x + w - 8, y + 2, 4, 3, INK, "d25")
        c.rect(x + 3, y + 3, 6, 1, INK)
        c.rect(x + 4, y + 2, 3, 1, INK)
    hx = x + max(2, w // 4)
    if h >= 12:
        c.rect(hx, gy - 5, 3, 2, INK)
        c.rect(hx - 1, gy - 3, 5, 2, INK)
        c.px(hx, gy - 1, INK)
        c.px(hx + 2, gy - 1, INK)
        bx = x + w // 2 + 2
        c.rect(bx, gy - 9, 4, 4, INK)
        c.px(bx + 1, gy - 8, PAPER)
        c.px(bx + 2, gy - 7, PAPER)
    else:
        c.rect(hx, gy - 3, 2, 3, INK)


def cart(c: Canvas, x, y, w, h, label=True, ridges=True, fill=PAPER, notch=False):
    c.box(x, y, w, h, fill=fill, line=INK, r=1)
    if ridges:
        for i in range(x + 3, x + w - 3, 2):
            c.vline(i, y + 2, 3, INK if fill == PAPER else PAPER)
    if label:
        c.box(x + 3, y + 6, w - 6, h - 9, fill=PAPER, line=INK, r=0)
        c.rect(x + 5, y + 8, w - 10, 2, INK)
        c.rect(x + 5, y + 12, w - 14, 1, INK, "checker")
    if notch:
        c.rect(x + w // 2 - 2, y + h - 1, 4, 1, PAPER)


def disc(c: Canvas, cx, cy, r):
    c.circle(cx, cy, r, fill=PAPER, line=INK)
    c.ellipse(cx - r + 2, cy - r + 2, r, r, INK, "d25")
    c.circle(cx, cy, max(2, r // 4), fill=PAPER, line=INK)
    c.px(cx, cy, INK)


# ------------------------------------------------------------- controllers
def pad_nes(c: Canvas, x, y, w=40, h=17):
    c.box(x, y, w, h, fill=PAPER, line=INK, r=1)
    c.rect(x + 2, y + 3, w - 4, h - 5, INK)
    c.rect(x + 13, y + 3, 14, h - 5, PAPER, "d25", alt=PAPER)
    c.rect(x + 14, y + 6, 12, 1, INK)
    c.rect(x + 14, y + 9, 12, 1, INK)
    pill(c, x + 15, y + 11, 4, 2, INK)
    pill(c, x + 21, y + 11, 4, 2, INK)
    dpad(c, x + 7, y + 8, 3, PAPER, INK)
    c.circle(x + 31, y + 10, 2, fill=PAPER, line=PAPER)
    c.circle(x + 36, y + 9, 2, fill=PAPER, line=PAPER)
    c.line([(x + w // 2, y), (x + w // 2 - 6, y - 8)], INK)


def pad_snes(c: Canvas, x, y, w=46, h=19):
    c.box(x + 2, y, w - 4, h, fill=PAPER, line=INK, r=3)
    c.oval(x, y, 18, h, fill=PAPER, line=INK)
    c.oval(x + w - 18, y, 18, h, fill=PAPER, line=INK)
    c.rect(x + 9, y + 1, w - 18, h - 2, PAPER)
    dpad(c, x + 9, y + 9, 3)
    c.ellipse(x + w - 17, y + 2, 16, 15, INK, "d25")
    c.circle(x + w - 9, y + 4, 2, fill=PAPER, line=INK)
    c.circle(x + w - 9, y + 14, 2, fill=INK, line=INK)
    c.circle(x + w - 14, y + 9, 2, fill=PAPER, line=INK)
    c.circle(x + w - 4, y + 9, 2, fill=INK, line=INK)
    pill(c, x + 18, y + 11, 4, 2)
    pill(c, x + 24, y + 11, 4, 2)
    c.line([(x + w // 2, y), (x + w // 2 + 4, y - 6)], INK)


def pad_md(c: Canvas, x, y, w=44, h=22):
    c.polybox([(x + 4, y), (x + w - 4, y), (x + w, y + 6), (x + w - 3, y + h - 2),
               (x + w - 10, y + h), (x + w // 2 + 4, y + h - 5), (x + w // 2 - 4, y + h - 5),
               (x + 10, y + h), (x + 3, y + h - 2), (x, y + 6)], fill=INK, line=INK)
    c.circle(x + 10, y + 9, 5, fill=INK, line=PAPER)
    dpad(c, x + 10, y + 9, 3, PAPER, INK)
    for i in range(3):
        c.circle(x + 25 + i * 6, y + 11 - i * 2, 2, fill=PAPER, line=PAPER)
    pill(c, x + w // 2 - 3, y + 4, 5, 1, PAPER)


def pad_psx(c: Canvas, x, y, w=48, h=24):
    c.polybox([(x + 6, y), (x + w - 6, y), (x + w, y + 8), (x + w - 2, y + h - 1),
               (x + w - 9, y + h), (x + w - 14, y + 12), (x + 14, y + 12), (x + 9, y + h),
               (x + 2, y + h - 1), (x, y + 8)], fill=PAPER, line=INK)
    c.circle(x + 10, y + 8, 5, fill=PAPER, line=INK)
    dpad(c, x + 10, y + 8, 2)
    c.circle(x + w - 10, y + 8, 5, fill=PAPER, line=INK)
    c.px(x + w - 10, y + 5, INK)
    c.px(x + w - 7, y + 8, INK)
    c.px(x + w - 13, y + 8, INK)
    c.px(x + w - 10, y + 11, INK)
    pill(c, x + 19, y + 7, 3, 1)
    pill(c, x + 26, y + 7, 3, 1)
    c.circle(x + 18, y + 12, 3, fill=INK, line=INK)
    c.circle(x + w - 18, y + 12, 3, fill=INK, line=INK)


def pad_n64(c: Canvas, x, y):
    c.polybox([(x + 2, y + 3), (x + 46, y + 3), (x + 50, y + 9), (x + 48, y + 26),
               (x + 41, y + 28), (x + 36, y + 14), (x + 30, y + 14), (x + 28, y + 30),
               (x + 22, y + 30), (x + 20, y + 14), (x + 14, y + 14), (x + 9, y + 28),
               (x + 2, y + 26), (x, y + 9)], fill=PAPER, line=INK, pat="d25", alt=PAPER)
    dpad(c, x + 9, y + 10, 3)
    c.circle(x + 25, y + 18, 3, fill=INK, line=INK)
    c.px(x + 25, y + 18, PAPER)
    c.circle(x + 42, y + 13, 2, fill=INK, line=INK)
    c.circle(x + 38, y + 16, 2, fill=PAPER, line=INK)
    for dx, dy in ((40, 6), (44, 8), (37, 9), (43, 3)):
        c.rect(x + dx, y + dy, 2, 2, INK)
    pill(c, x + 23, y + 8, 4, 2)


def joystick(c: Canvas, x, y):
    """Atari CX40 style."""
    c.box(x, y + 10, 22, 18, fill=INK, line=INK, r=1)
    c.rect(x + 2, y + 12, 18, 14, INK, "checker")
    c.circle(x + 11, y + 19, 5, fill=INK, line=PAPER)
    c.rect(x + 10, y, 3, 18, INK)
    c.rect(x + 9, y - 1, 5, 3, INK)
    c.circle(x + 4, y + 13, 2, fill=PAPER, line=INK)


# ------------------------------------------------------------- Nintendo
def nes():
    c = new()
    x, y, w, h = 6, 18, 112, 56
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, 6, INK, "d25")       # top ridges
    for i in range(y + 2, y + 7, 2):
        c.hline(x + 30, i, w - 32, INK)
    c.hline(x + 1, y + 30, w - 2, INK)               # split line
    c.rect(x + 1, y + 31, w - 2, h - 32, INK, "checker")
    c.box(x + 20, y + 12, 70, 16, fill=INK, line=INK, r=0)  # cart door
    for i in range(y + 14, y + 27, 3):
        c.hline(x + 22, i, 66, PAPER, "checker")
    c.box(x + 4, y + 12, 13, 14, fill=PAPER, line=INK, r=0)
    tiny(c, x + 5, y + 14, "N", INK)
    c.box(x + 4, y + 36, 22, 12, fill=PAPER, line=INK, r=0)  # power/reset
    c.rect(x + 7, y + 40, 6, 4, INK)
    c.rect(x + 16, y + 40, 6, 4, INK)
    c.box(x + w - 30, y + 38, 9, 8, fill=INK, line=INK, r=0)   # ports
    c.box(x + w - 18, y + 38, 9, 8, fill=INK, line=INK, r=0)
    c.box(x + 32, y + 36, 40, 12, fill=PAPER, line=INK, r=0)
    tiny(c, x + 52, y + 38, "PUSH", INK, "ma")
    pad_nes(c, 104, 80)
    return c


def famicom():
    c = new()
    x, y, w, h = 14, 34, 104, 40
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=2)
    c.rect(x + 1, y + h - 12, w - 2, 11, INK, "checker")
    c.hline(x + 1, y + h - 13, w - 2, INK)
    c.box(x + 26, y - 6, 52, 10, fill=INK, line=INK, r=1)   # slot
    c.hline(x + 30, y - 2, 44, PAPER)
    cart(c, x + 32, y - 22, 40, 20, label=True)
    c.box(x + 4, y + 6, 14, 18, fill=INK, line=INK, r=1)    # pad cradles
    c.box(x + w - 18, y + 6, 14, 18, fill=INK, line=INK, r=1)
    c.rect(x + 34, y + 12, 8, 4, INK)
    c.rect(x + 62, y + 12, 8, 4, INK)
    c.hline(x + 30, y + 8, 44, INK, "checker")
    # wired pads
    for px_, flip in ((4, False), (112, True)):
        c.box(px_, 80, 40, 16, fill=PAPER, line=INK, r=1)
        c.rect(px_ + 2, 82, 36, 12, INK)
        dpad(c, px_ + 8, 88, 3, PAPER, INK)
        c.circle(px_ + 29, 88, 2, fill=PAPER, line=PAPER)
        c.circle(px_ + 34, 88, 2, fill=PAPER, line=PAPER)
    c.line([(24, 80), (24, 66)], INK)
    c.line([(132, 80), (132, 66), (118, 66)], INK)
    return c


def fds():
    c = famicom()
    c.rect(0, 0, W, 34, CLEAR)
    c.box(14, 2, 104, 30, fill=PAPER, line=INK, r=1)   # RAM adapter + drive
    c.rect(15, 3, 102, 6, INK, "checker")
    c.box(30, 14, 70, 6, fill=INK, line=INK, r=0)
    c.hline(32, 16, 66, PAPER)
    c.box(102, 13, 10, 8, fill=PAPER, line=INK, r=0)
    c.rect(104, 15, 6, 4, INK)
    c.box(124, 6, 30, 32, fill=INK, line=INK, r=1)     # the disk card
    c.box(128, 10, 22, 10, fill=PAPER, line=INK, r=0)
    c.rect(130, 12, 18, 2, INK)
    c.rect(130, 16, 12, 1, INK, "checker")
    c.rect(134, 26, 10, 10, PAPER, "checker", alt=INK)
    return c


def snes():
    c = new()
    # US "breadbox" model
    x, y, w, h = 6, 28, 118, 50
    shadow(c, x, y + h, w)
    c.polybox([(x + 6, y), (x + w - 6, y), (x + w, y + 10), (x + w, y + h),
               (x, y + h), (x, y + 10)], fill=PAPER, line=INK)
    c.rect(x + 1, y + 30, w - 2, h - 31, INK, "d25")
    c.hline(x + 1, y + 30, w - 2, INK)
    c.polybox([(x + 22, y + 4), (x + 96, y + 4), (x + 100, y + 18), (x + 18, y + 18)],
              fill=INK, line=INK)                      # purple cart deck
    c.box(x + 34, y + 8, 50, 6, fill=PAPER, line=INK, r=0)
    c.hline(x + 36, y + 10, 46, INK)
    for i in range(4):                                 # vents
        c.hline(x + 4, y + 6 + i * 3, 12, INK)
        c.hline(x + w - 16, y + 6 + i * 3, 12, INK)
    c.box(x + 10, y + 22, 18, 6, fill=INK, line=INK, r=1)     # power
    c.box(x + w - 28, y + 22, 18, 6, fill=INK, line=INK, r=1) # reset
    c.box(x + 40, y + 21, 38, 7, fill=PAPER, line=INK, r=0)
    c.rect(x + 42, y + 23, 34, 3, INK, "checker")
    c.box(x + 20, y + 36, 10, 8, fill=PAPER, line=INK, r=1)   # ports
    c.box(x + 34, y + 36, 10, 8, fill=PAPER, line=INK, r=1)
    c.rect(x + 22, y + 38, 6, 4, INK)
    c.rect(x + 36, y + 38, 6, 4, INK)
    cart(c, x + 40, y - 20, 38, 22)
    pad_snes(c, 108, 78)
    return c


def sfc():
    c = new()
    # rounded Super Famicom / PAL model
    x, y, w, h = 6, 30, 118, 46
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=3)
    c.rect(x + 1, y + 28, w - 2, h - 29, INK, "d25")
    c.hline(x + 1, y + 28, w - 2, INK)
    c.box(x + 28, y + 4, 62, 14, fill=INK, line=INK, r=2)
    c.box(x + 36, y + 8, 46, 5, fill=PAPER, line=INK, r=0)
    for i, cx in enumerate((x + 14, x + w - 14)):      # coloured slider caps
        c.box(cx - 8, y + 18, 16, 7, fill=PAPER, line=INK, r=2)
        c.rect(cx - 6, y + 20, 12, 3, INK, "checker" if i else "solid")
    c.circle(x + 59, y + 22, 4, fill=PAPER, line=INK)
    c.ellipse(x + 56, y + 19, 7, 7, INK, "checker")
    c.box(x + 20, y + 33, 10, 8, fill=PAPER, line=INK, r=1)
    c.box(x + 34, y + 33, 10, 8, fill=PAPER, line=INK, r=1)
    cart(c, x + 40, y - 20, 38, 24)
    pad_snes(c, 108, 78)
    return c


def n64():
    c = new()
    x, y, w, h = 8, 32, 112, 44
    shadow(c, x, y + h, w)
    c.polybox([(x + 18, y), (x + w - 18, y), (x + w, y + 14), (x + w, y + h),
               (x, y + h), (x, y + 14)], fill=INK, line=INK)
    c.polybox([(x + 22, y + 3), (x + w - 22, y + 3), (x + w - 8, y + 14), (x + 8, y + 14)],
              fill=INK, line=PAPER, pat="checker", alt=INK)
    c.box(x + 34, y - 3, 44, 8, fill=INK, line=PAPER, r=1)      # cart slot
    cart(c, x + 38, y - 22, 36, 22, ridges=False, fill=INK)
    c.box(x + 41, y - 16, 30, 10, fill=PAPER, line=INK, r=0)
    c.rect(x + 43, y - 14, 26, 2, INK)
    c.rect(x + 20, y + 8, 10, 4, PAPER)                          # power / reset
    c.rect(x + w - 30, y + 8, 10, 4, PAPER)
    c.hline(x + 1, y + 18, w - 2, PAPER, "checker")
    for i in range(4):                                           # ports
        c.box(x + 18 + i * 21, y + 26, 13, 9, fill=PAPER, line=PAPER, r=1)
        c.rect(x + 21 + i * 21, y + 29, 7, 3, INK)
    tiny(c, x + w // 2, y + 37, "64", PAPER, "ma")
    pad_n64(c, 104, 70)
    return c


def gameboy():
    c = new()
    x, y, w, h = 48, 4, 60, 96
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=2)
    c.polybox([(x + w - 2, y + h - 18), (x + w - 2, y + h - 2), (x + w - 18, y + h - 2)],
              fill=PAPER, line=None)
    c.rect(x + 1, y + 1, w - 2, 2, INK, "d25")
    c.box(x + 5, y + 6, w - 10, 44, fill=INK, line=INK, r=1)    # bezel
    c.rect(x + 5, y + 6, w - 10, 44, INK, "d75", alt=INK)
    c.rect(x + 7, y + 8, w - 32, 1, PAPER, "checker")
    c.px(x + 9, y + 24, PAPER)                                  # power LED
    scene(c, x + 14, y + 12, w - 24, 32, "tetris")
    c.frame(x + 13, y + 11, w - 22, 34, INK)
    tiny(c, x + 6, y + 52, "DOT MATRIX", INK)
    dpad(c, x + 14, y + 68, 4)
    c.circle(x + w - 9, y + 64, 4, fill=INK, line=INK)
    c.circle(x + w - 20, y + 69, 4, fill=INK, line=INK)
    c.line([(x + 22, y + 84), (x + 26, y + 81)], INK, 2)
    c.line([(x + 30, y + 84), (x + 34, y + 81)], INK, 2)
    for i in range(6):                                          # speaker
        c.line([(x + w - 22 + i * 3, y + h - 4), (x + w - 14 + i * 3, y + h - 12)], INK)
    return c


def gbc():
    c = new()
    x, y, w, h = 50, 6, 56, 92
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=3)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "d12", alt=PAPER)   # translucent shell
    c.box(x + 4, y + 6, w - 8, 40, fill=INK, line=INK, r=2)
    scene(c, x + 10, y + 10, w - 20, 30, "platform")
    c.frame(x + 9, y + 9, w - 18, 32, PAPER)
    c.rect(x + 6, y + 18, 2, 2, PAPER)
    tiny(c, x + w // 2, y + 48, "COLOR", INK, "ma")
    dpad(c, x + 13, y + 64, 4)
    c.circle(x + w - 9, y + 60, 4, fill=INK, line=INK)
    c.circle(x + w - 19, y + 66, 4, fill=INK, line=INK)
    c.line([(x + 20, y + 80), (x + 24, y + 77)], INK, 2)
    c.line([(x + 28, y + 80), (x + 32, y + 77)], INK, 2)
    for i in range(3):
        c.circle(x + w - 16 + i * 5, y + h - 8, 1, fill=INK, line=INK)
    return c


def gba():
    c = new()
    x, y, w, h = 14, 30, 132, 58
    shadow(c, x + 8, y + h, w - 16)
    c.ellipse(x, y, 40, h, INK)
    c.ellipse(x + w - 40, y, 40, h, INK)
    c.rect(x + 20, y, w - 40, h, INK)
    c.ellipse(x + 1, y + 1, 38, h - 2, PAPER)
    c.ellipse(x + w - 39, y + 1, 38, h - 2, PAPER)
    c.rect(x + 20, y + 1, w - 40, h - 2, PAPER)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "d25")
    c.ellipse(x + 1, y + 1, 38, h - 2, INK, "d25")
    c.box(x + 34, y + 6, 64, 44, fill=INK, line=INK, r=2)
    scene(c, x + 40, y + 10, 52, 34, "platform")
    c.frame(x + 39, y + 9, 54, 36, PAPER)
    dpad(c, x + 18, y + 26, 4)
    c.circle(x + w - 13, y + 22, 4, fill=INK, line=INK)
    c.circle(x + w - 23, y + 30, 4, fill=INK, line=INK)
    c.rect(x + w - 12, y + 44, 2, 2, INK)
    c.rect(x + w - 8, y + 42, 2, 2, INK)
    c.rect(x + 20, y + 42, 3, 2, INK)
    c.rect(x + 20, y + 46, 3, 2, INK)
    c.polybox([(x + 6, y - 3), (x + 30, y - 3), (x + 34, y + 2), (x + 2, y + 2)], fill=INK, line=INK)
    c.polybox([(x + w - 30, y - 3), (x + w - 6, y - 3), (x + w - 2, y + 2), (x + w - 34, y + 2)],
              fill=INK, line=INK)
    return c


def nds():
    c = new()
    # DS Lite, open at an angle
    x, y, w = 30, 2, 100
    c.box(x, y, w, 46, fill=PAPER, line=INK, r=3)
    c.box(x + 18, y + 5, 64, 38, fill=INK, line=INK, r=1)
    scene(c, x + 21, y + 8, 58, 32, "platform")
    c.rect(x + 6, y + 18, 6, 2, INK)
    c.rect(x + w - 12, y + 18, 6, 2, INK)
    c.rect(x + 2, y + 46, w - 4, 4, INK, "checker")              # hinge
    y2 = y + 50
    shadow(c, x, y2 + 48, w)
    c.box(x, y2, w, 48, fill=PAPER, line=INK, r=3)
    c.box(x + 18, y2 + 5, 64, 38, fill=INK, line=INK, r=1)
    scene(c, x + 21, y2 + 8, 58, 32, "lines")
    c.rect(x + 23, y2 + 10, 20, 8, PAPER)
    c.rect(x + 25, y2 + 12, 16, 4, INK, "checker")
    dpad(c, x + 9, y2 + 20, 3)
    for dx, dy in ((0, -5), (5, 0), (-5, 0), (0, 5)):
        c.circle(x + w - 9 + dx, y2 + 20 + dy, 1, fill=INK, line=INK)
    c.rect(x + w - 11, y2 + 34, 4, 2, INK)
    c.rect(x + w - 11, y2 + 38, 4, 2, INK)
    c.line([(x + 82, y2 + 24), (x + 98, y2 + 8)], INK)            # stylus
    return c


def virtualboy():
    c = new()
    # visor on a bipod stand
    c.polybox([(22, 18), (138, 18), (146, 30), (140, 52), (104, 56), (92, 46), (68, 46),
               (56, 56), (20, 52), (14, 30)], fill=INK, line=INK)
    c.polybox([(26, 22), (134, 22), (140, 31), (135, 48), (106, 51), (96, 42), (64, 42),
               (54, 51), (25, 48), (20, 31)], fill=INK, line=PAPER, pat="checker", alt=INK)
    c.box(52, 10, 56, 10, fill=INK, line=PAPER, r=2)              # eyeshade
    c.rect(56, 13, 48, 4, PAPER, "hlines")
    c.ellipse(38, 28, 30, 14, PAPER)
    c.ellipse(92, 28, 30, 14, PAPER)
    c.ellipse(41, 30, 24, 10, INK, "checker")
    c.ellipse(95, 30, 24, 10, INK, "checker")
    c.rect(76, 56, 8, 30, INK)
    c.line([(80, 84), (52, 98)], INK, 3)
    c.line([(80, 84), (108, 98)], INK, 3)
    shadow(c, 46, 99, 68)
    return c


def pokemini():
    c = new()
    x, y, w, h = 52, 14, 56, 74
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=3)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "d25")
    c.box(x + 6, y + 6, w - 12, 34, fill=INK, line=INK, r=2)
    scene(c, x + 10, y + 10, w - 20, 26, "platform")
    c.circle(x + w // 2, y + 56, 7, fill=PAPER, line=INK)     # big A
    c.rect(x + w // 2 - 1, y + 53, 2, 6, INK)
    dpad(c, x + 12, y + 56, 3)
    c.circle(x + w - 11, y + 52, 3, fill=INK, line=INK)
    c.circle(x + w - 11, y + 62, 3, fill=INK, line=INK)
    c.rect(x + w // 2 - 6, y + h - 6, 12, 2, INK)
    return c


def gameandwatch():
    c = new()
    # dual-screen clamshell open
    x, y, w = 24, 6, 112
    c.box(x, y, w, 44, fill=PAPER, line=INK, r=2)
    c.rect(x + 2, y + 2, w - 4, 40, INK, "d25")
    c.box(x + 22, y + 6, 68, 34, fill=PAPER, line=INK, r=0)
    c.rect(x + 24, y + 30, 64, 2, INK, "checker")
    for i in range(4):
        c.rect(x + 30 + i * 14, y + 14, 6, 4, INK)
    c.rect(x + 2, y + 44, w - 4, 4, INK)
    c.box(x, y + 48, w, 44, fill=PAPER, line=INK, r=2)
    c.rect(x + 2, y + 50, w - 4, 40, INK, "d25")
    c.box(x + 22, y + 52, 68, 34, fill=PAPER, line=INK, r=0)
    c.rect(x + 50, y + 70, 8, 8, INK)
    c.rect(x + 26, y + 78, 60, 2, INK, "checker")
    dpad(c, x + 10, y + 70, 3)
    c.circle(x + w - 10, y + 70, 4, fill=INK, line=INK)
    shadow(c, x, y + 92, w)
    return c


# ------------------------------------------------------------------ Sega
def sg1000():
    c = new()
    x, y, w, h = 10, 36, 108, 38
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, 12, PAPER, "d25", alt=INK)
    c.box(x + 34, y + 3, 40, 6, fill=INK, line=PAPER, r=0)
    cart(c, x + 38, y - 18, 32, 22, fill=INK)
    c.rect(x + 41, y - 13, 26, 10, PAPER)
    c.rect(x + 43, y - 11, 22, 2, INK)
    c.hline(x + 1, y + 16, w - 2, PAPER)
    c.rect(x + 6, y + 22, 18, 6, PAPER)
    tiny(c, x + w - 6, y + 22, "SG-1000", PAPER, "ra")
    joystick(c, 128, 66)
    return c


def mastersystem():
    c = new()
    x, y, w, h = 6, 30, 120, 46
    shadow(c, x, y + h, w)
    c.polybox([(x, y + 6), (x + 10, y), (x + w, y), (x + w, y + h), (x, y + h)], fill=INK, line=INK)
    c.rect(x + 1, y + 7, w - 2, 1, PAPER)
    for i in range(6):                                           # red grid lines
        c.hline(x + 52, y + 12 + i * 4, w - 56, PAPER, "checker")
        c.vline(x + 56 + i * 11, y + 10, 24, PAPER, "checker")
    c.box(x + 6, y + 12, 40, 8, fill=INK, line=PAPER, r=0)
    c.hline(x + 8, y + 16, 36, PAPER)
    c.rect(x + 6, y + 26, 8, 4, PAPER)
    c.rect(x + 18, y + 26, 8, 4, PAPER)
    c.box(x + 2, y + 36, w - 4, 8, fill=PAPER, line=PAPER, r=0)
    tiny(c, x + 6, y + 37, "MASTER SYSTEM", INK)
    cart(c, x + 8, y - 20, 36, 22, fill=PAPER)
    pad_rect(c, 108, 78)
    return c


def pad_rect(c, x, y):
    c.box(x, y, 46, 20, fill=INK, line=INK, r=2)
    c.rect(x + 2, y + 2, 42, 16, INK, "checker")
    c.circle(x + 10, y + 10, 6, fill=INK, line=PAPER)
    dpad(c, x + 10, y + 10, 3, PAPER, INK)
    c.circle(x + 30, y + 11, 3, fill=PAPER, line=PAPER)
    c.circle(x + 38, y + 11, 3, fill=PAPER, line=PAPER)


def genesis():
    c = new()
    x, y, w, h = 4, 30, 120, 42
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=3)
    c.circle(x + 44, y + 18, 15, fill=INK, line=PAPER)            # the big ring
    c.circle(x + 44, y + 18, 11, fill=INK, line=PAPER)
    c.circle(x + 44, y + 18, 9, fill=INK, line=PAPER, pat=None)
    c.box(x + 30, y + 14, 28, 8, fill=INK, line=PAPER, r=1)       # slot
    c.hline(x + 32, y + 18, 24, PAPER)
    cart(c, x + 30, y - 18, 28, 32, fill=INK)
    c.rect(x + 33, y - 12, 22, 12, PAPER)
    c.rect(x + 35, y - 10, 18, 2, INK)
    c.rect(x + 35, y - 6, 12, 1, INK, "checker")
    for i in range(5):
        c.hline(x + 66, y + 6 + i * 3, 46, PAPER, "checker")
    c.box(x + 66, y + 24, 14, 6, fill=PAPER, line=PAPER, r=1)     # volume / reset
    c.box(x + 84, y + 24, 14, 6, fill=INK, line=PAPER, r=1)
    tiny(c, x + 6, y + 30, "16-BIT", PAPER)
    c.rect(x + 1, y + 36, w - 2, 1, PAPER, "checker")
    pad_md(c, 112, 78)
    return c


def segacd():
    c = genesis()
    c.rect(0, 74, 112, 30, CLEAR)
    c.rect(0, 72, 160, 32, CLEAR)
    c.blit(_shift(c, 0, -12), 0, 0)
    x, y, w = 4, 61, 120
    c.box(x, y, w, 36, fill=INK, line=PAPER, r=2)                 # CD unit beneath
    c.rect(x + 1, y + 1, w - 2, 34, INK, "checker")
    c.box(x + 8, y + 4, 70, 28, fill=INK, line=PAPER, r=1)        # tray lid
    disc(c, x + 43, y + 18, 11)
    c.box(x + 86, y + 8, 26, 6, fill=PAPER, line=PAPER, r=1)
    c.box(x + 86, y + 18, 12, 5, fill=INK, line=PAPER, r=1)
    shadow(c, x, y + 36, w)
    pad_md(c, 114, 80)
    return c


def _shift(c: Canvas, dx, dy) -> Canvas:
    n = Canvas(c.w, c.h)
    n.blit(c, dx, dy)
    c.a[:] = 0
    return n


def sega32x():
    c = genesis()
    # the mushroom on top
    c.rect(28, 0, 40, 30, CLEAR)
    c.polybox([(30, 18), (64, 18), (70, 28), (24, 28)], fill=INK, line=INK)
    c.polybox([(22, 4), (72, 4), (78, 18), (16, 18)], fill=INK, line=PAPER)
    c.rect(24, 6, 46, 10, PAPER, "checker", alt=INK)
    c.box(32, 8, 30, 6, fill=INK, line=PAPER, r=0)
    tiny(c, 47, 20, "32X", PAPER, "ma")
    return c


def saturn():
    c = new()
    x, y, w, h = 6, 24, 120, 54
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=4)
    c.rect(x + 1, y + h - 14, w - 2, 13, INK, "checker")
    c.hline(x + 2, y + h - 15, w - 4, PAPER)
    c.oval(x + 22, y + 4, 76, 34, fill=INK, line=PAPER)           # disc lid
    c.oval(x + 30, y + 8, 60, 26, fill=INK, line=PAPER, pat="d12", alt=INK)
    c.oval(x + 50, y + 16, 20, 10, fill=INK, line=PAPER)
    c.rect(x + 6, y + 10, 10, 4, PAPER)
    c.rect(x + w - 16, y + 10, 10, 4, PAPER)
    c.box(x + 4, y + 18, 14, 8, fill=INK, line=PAPER, r=1)
    c.box(x + w - 18, y + 18, 14, 8, fill=INK, line=PAPER, r=1)
    c.box(x + 18, y + h - 11, 10, 7, fill=PAPER, line=PAPER, r=1)
    c.box(x + 32, y + h - 11, 10, 7, fill=PAPER, line=PAPER, r=1)
    tiny(c, x + w - 8, y + h - 11, "SATURN", PAPER, "ra")
    # 3D-ish pad
    pad_saturn(c, 104, 78)
    return c


def pad_saturn(c, x, y):
    c.polybox([(x + 4, y), (x + 46, y), (x + 52, y + 8), (x + 48, y + 20), (x + 40, y + 22),
               (x + 34, y + 16), (x + 18, y + 16), (x + 12, y + 22), (x + 4, y + 20), (x, y + 8)],
              fill=INK, line=INK)
    c.circle(x + 11, y + 9, 5, fill=INK, line=PAPER)
    dpad(c, x + 11, y + 9, 3, PAPER, INK)
    for i in range(3):
        c.circle(x + 30 + i * 6, y + 12 - i, 2, fill=PAPER, line=PAPER)
        c.circle(x + 31 + i * 6, y + 5 - i, 1, fill=PAPER, line=PAPER)


def dreamcast():
    c = new()
    x, y, w, h = 18, 30, 92, 50
    shadow(c, x, y + h, w)
    c.polybox([(x + 4, y), (x + w - 4, y), (x + w, y + 6), (x + w, y + h), (x, y + h), (x, y + 6)],
              fill=PAPER, line=INK)
    c.rect(x + 1, y + h - 12, w - 2, 11, INK, "d25")
    c.hline(x + 1, y + h - 13, w - 2, INK)
    c.circle(x + w // 2, y + 18, 16, fill=PAPER, line=INK)
    c.circle(x + w // 2, y + 18, 12, fill=PAPER, line=INK, pat="d25")
    # swirl
    c.line([(x + 40, y + 12), (x + 44, y + 10), (x + 50, y + 12), (x + 52, y + 18), (x + 48, y + 23),
            (x + 43, y + 22), (x + 42, y + 18), (x + 46, y + 16)], INK)
    c.circle(x + 8, y + 8, 3, fill=PAPER, line=INK)
    c.circle(x + w - 9, y + 8, 3, fill=PAPER, line=INK)
    c.rect(x + w - 11, y + 16, 5, 2, INK)
    for i in range(4):
        c.box(x + 6 + i * 21, y + h - 10, 14, 7, fill=PAPER, line=INK, r=1)
    # controller with VMU
    px, py = 112, 62
    c.polybox([(px + 2, py), (px + 42, py), (px + 46, py + 10), (px + 42, py + 34),
               (px + 34, py + 36), (px + 30, py + 22), (px + 14, py + 22), (px + 10, py + 36),
               (px + 2, py + 34), (px - 2, py + 10)], fill=PAPER, line=INK)
    c.box(px + 13, py + 3, 18, 18, fill=PAPER, line=INK, r=1)
    c.rect(px + 15, py + 5, 14, 8, INK, "checker")
    c.circle(px + 6, py + 6, 3, fill=PAPER, line=INK)
    dpad(c, px + 7, py + 16, 2)
    for dx, dy in ((0, -3), (3, 0), (-3, 0), (0, 3)):
        c.circle(px + 38 + dx, py + 12 + dy, 1, fill=INK, line=INK)
    return c


def gamegear():
    c = new()
    x, y, w, h = 10, 24, 140, 62
    shadow(c, x + 10, y + h, w - 20)
    c.ellipse(x, y, 44, h, INK)
    c.ellipse(x + w - 44, y, 44, h, INK)
    c.rect(x + 22, y, w - 44, h, INK)
    c.rect(x + 2, y + 2, w - 4, h - 4, INK, "d12", alt=INK)
    c.box(x + 36, y + 4, 68, 50, fill=INK, line=PAPER, r=2)
    scene(c, x + 44, y + 9, 52, 38, "platform")
    c.frame(x + 43, y + 8, 54, 40, PAPER)
    c.rect(x + 38, y + 26, 2, 2, PAPER)
    tiny(c, x + 70, y + 49, "GAME GEAR", PAPER, "ma")
    c.circle(x + 18, y + 31, 9, fill=INK, line=PAPER)
    dpad(c, x + 18, y + 31, 4, PAPER, INK)
    c.circle(x + w - 24, y + 35, 4, fill=PAPER, line=PAPER)
    c.circle(x + w - 13, y + 29, 4, fill=PAPER, line=PAPER)
    c.rect(x + w - 22, y + 14, 6, 2, PAPER)
    for i in range(4):
        c.px(x + 12 + i * 3, y + 48, PAPER)
        c.px(x + 12 + i * 3, y + 51, PAPER)
    return c


# ------------------------------------------------------------------ Sony
def psx():
    c = new()
    x, y, w, h = 8, 30, 108, 46
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=2)
    c.rect(x + 1, y + h - 10, w - 2, 9, INK, "d25")
    c.hline(x + 1, y + h - 11, w - 2, INK)
    c.circle(x + 40, y + 18, 16, fill=PAPER, line=INK)            # lid
    c.circle(x + 40, y + 18, 13, fill=PAPER, line=INK, pat="d25")
    c.circle(x + 40, y + 18, 3, fill=PAPER, line=INK)
    c.ellipse(x + 30, y + 8, 8, 5, PAPER)
    for i in range(3):                                            # open/power/reset
        c.circle(x + 72 + i * 11, y + 12, 3, fill=PAPER, line=INK)
    c.rect(x + 72, y + 22, 26, 2, INK, "checker")
    c.box(x + 6, y + h - 9, 16, 6, fill=PAPER, line=INK, r=0)
    c.box(x + 26, y + h - 9, 16, 6, fill=PAPER, line=INK, r=0)
    c.box(x + 60, y + h - 9, 10, 6, fill=INK, line=INK, r=0)
    c.box(x + 74, y + h - 9, 10, 6, fill=INK, line=INK, r=0)
    disc(c, 22, 84, 13)
    pad_psx(c, 108, 72)
    return c


def psp():
    c = new()
    x, y, w, h = 4, 28, 152, 58
    shadow(c, x + 10, y + h, w - 20)
    c.ellipse(x, y, 40, h, INK)
    c.ellipse(x + w - 40, y, 40, h, INK)
    c.rect(x + 20, y, w - 40, h, INK)
    c.ellipse(x + 2, y + 2, 36, h - 4, INK, "d12", alt=INK)
    c.ellipse(x + w - 38, y + 2, 36, h - 4, INK, "d12", alt=INK)
    c.box(x + 32, y + 5, 88, 46, fill=INK, line=PAPER, r=1)
    scene(c, x + 34, y + 7, 84, 42, "platform")
    dpad(c, x + 15, y + 22, 3, PAPER, INK)
    c.circle(x + 15, y + 40, 4, fill=INK, line=PAPER)              # analog nub
    sx, sy = x + w - 16, y + 24
    c.circle(sx, sy - 7, 2, fill=INK, line=PAPER)
    c.circle(sx + 7, sy, 2, fill=INK, line=PAPER)
    c.circle(sx - 7, sy, 2, fill=INK, line=PAPER)
    c.circle(sx, sy + 7, 2, fill=INK, line=PAPER)
    for i in range(4):
        c.rect(x + 46 + i * 16, y + 53, 8, 2, PAPER)
    return c


# ------------------------------------------------------------------- NEC
def pcengine():
    c = new()
    x, y = 34, 22
    shadow(c, x, y + 64, 70)
    c.box(x, y, 70, 64, fill=PAPER, line=INK, r=1)
    c.rect(x + 1, y + 1, 68, 62, INK, "d12", alt=PAPER)
    c.rect(x + 1, y + 1, 6, 62, INK, "checker")
    c.rect(x + 63, y + 1, 6, 62, INK, "checker")
    c.box(x + 14, y + 6, 42, 8, fill=INK, line=INK, r=0)          # HuCard slot
    c.rect(x + 18, y + 4, 34, 6, PAPER)
    c.box(x + 18, y - 2, 34, 9, fill=PAPER, line=INK, r=1)          # HuCard
    c.rect(x + 20, y, 30, 3, INK, "checker")
    c.rect(x + 14, y + 22, 42, 4, INK)
    c.rect(x + 8, y + 50, 54, 10, INK)
    c.rect(x + 12, y + 53, 30, 4, PAPER, "checker", alt=INK)
    c.box(x + 48, y + 52, 10, 6, fill=PAPER, line=PAPER, r=0)
    # pad
    px, py = 108, 74
    c.box(px, py, 44, 18, fill=INK, line=INK, r=2)
    c.rect(px + 2, py + 2, 40, 14, PAPER, "d25", alt=INK)
    dpad(c, px + 8, py + 9, 3, INK, PAPER)
    c.circle(px + 31, py + 10, 3, fill=INK, line=INK)
    c.circle(px + 38, py + 10, 3, fill=INK, line=INK)
    pill(c, px + 16, py + 12, 4, 2)
    pill(c, px + 22, py + 12, 4, 2)
    c.line([(px + 22, py), (px + 10, py - 10), (x + 70, y + 40)], INK)
    return c


def tg16():
    c = new()
    x, y, w, h = 6, 32, 112, 40
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, 10, PAPER, "checker", alt=INK)
    c.box(x + 30, y + 3, 52, 6, fill=INK, line=PAPER, r=0)
    c.box(x + 38, y - 8, 36, 10, fill=PAPER, line=INK, r=1)
    c.rect(x + 40, y - 6, 32, 3, INK, "checker")
    c.rect(x + 6, y + 14, w - 12, 1, PAPER)
    tiny(c, x + 6, y + 18, "TURBOGRAFX", PAPER)
    c.box(x + w - 30, y + 18, 24, 8, fill=INK, line=PAPER, r=0)
    c.rect(x + 1, y + 30, w - 2, 9, INK, "checker")
    c.box(x + 6, y + 31, 14, 6, fill=PAPER, line=PAPER, r=0)
    pad_rect(c, 110, 74)
    return c


def pcenginecd():
    c = new()
    # CD-ROM2 base with the PC Engine docked
    x, y = 6, 50
    shadow(c, x, y + 36, 124)
    c.box(x, y, 124, 36, fill=PAPER, line=INK, r=1)
    c.rect(x + 1, y + 26, 122, 9, INK, "checker")
    c.box(x + 52, y + 4, 66, 20, fill=PAPER, line=INK, r=1)
    disc(c, x + 85, y + 14, 8)
    c.box(x + 4, y + 4, 44, 18, fill=PAPER, line=INK, r=1)
    c.blit(_mini_pce(), x + 8, y - 30)
    return c


def _mini_pce():
    c = Canvas(40, 40)
    c.box(0, 0, 36, 36, fill=PAPER, line=INK, r=1)
    c.rect(1, 1, 34, 34, INK, "d12", alt=PAPER)
    c.rect(1, 1, 4, 34, INK, "checker")
    c.rect(31, 1, 4, 34, INK, "checker")
    c.box(8, 4, 20, 5, fill=INK, line=INK, r=0)
    c.rect(4, 28, 28, 5, INK)
    return c


def supergrafx():
    c = new()
    x, y, w, h = 14, 26, 112, 50
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=2)
    c.rect(x + 1, y + 1, w - 2, h - 2, PAPER, "d12", alt=INK)
    c.box(x + 34, y + 6, 44, 8, fill=PAPER, line=PAPER, r=0)
    c.rect(x + 38, y + 8, 36, 4, INK)
    c.rect(x + 8, y + 22, w - 16, 3, PAPER, "checker")
    tiny(c, x + w // 2, y + 30, "SuperGrafx", PAPER, "ma")
    c.box(x + 8, y + 38, 18, 7, fill=PAPER, line=PAPER, r=1)
    c.box(x + w - 26, y + 38, 18, 7, fill=PAPER, line=PAPER, r=1)
    pad_rect(c, 110, 80)
    return c


def pcfx():
    c = new()
    # upright tower
    x, y, w, h = 44, 4, 52, 92
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=2)
    c.rect(x + w - 10, y + 1, 9, h - 2, INK, "checker")
    c.box(x + 6, y + 8, 34, 26, fill=PAPER, line=INK, r=1)
    disc(c, x + 23, y + 21, 10)
    for i in range(8):
        c.hline(x + 6, y + 44 + i * 3, 34, INK)
    c.box(x + 6, y + 74, 14, 8, fill=INK, line=INK, r=1)
    c.box(x + 24, y + 74, 14, 8, fill=PAPER, line=INK, r=1)
    tiny(c, x + 22, y + 84, "PC-FX", INK, "ma")
    return c


# ------------------------------------------------------------------- SNK
def neogeo():
    c = new()
    x, y, w, h = 4, 34, 112, 38
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, 8, PAPER, "d12", alt=INK)
    cart(c, x + 20, y - 26, 70, 30, fill=INK)                     # huge MVS-size cart
    c.rect(x + 24, y - 20, 62, 16, PAPER)
    c.rect(x + 27, y - 17, 40, 3, INK)
    c.rect(x + 27, y - 11, 52, 2, INK, "checker")
    c.rect(x + 1, y + 12, w - 2, 1, PAPER)
    tiny(c, x + 6, y + 16, "NEO-GEO", PAPER)
    c.box(x + 66, y + 16, 14, 6, fill=PAPER, line=PAPER, r=0)
    c.box(x + 84, y + 16, 14, 6, fill=INK, line=PAPER, r=0)
    c.rect(x + 1, y + 27, w - 2, 10, INK, "checker")
    # the arcade stick
    px, py = 106, 64
    c.polybox([(px, py + 12), (px + 50, py + 12), (px + 52, py + 30), (px - 2, py + 30)], fill=INK, line=INK)
    c.rect(px + 1, py + 14, 49, 4, PAPER, "checker", alt=INK)
    c.rect(px + 9, py, 3, 14, INK)
    c.circle(px + 10, py - 1, 4, fill=INK, line=INK)
    c.px(px + 9, py - 3, PAPER)
    for i in range(4):
        c.circle(px + 22 + i * 7, py + 22 - (i % 2) * 2, 2, fill=PAPER, line=PAPER)
    return c


def ngp(color=False):
    c = new()
    x, y, w, h = 18, 26, 124, 58
    shadow(c, x + 6, y + h, w - 12)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=4)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "d12" if color else "d25")
    c.box(x + 34, y + 4, 56, 46, fill=INK, line=INK, r=2)
    scene(c, x + 39, y + 9, 46, 34, "platform")
    c.frame(x + 38, y + 8, 48, 36, PAPER)
    c.circle(x + 16, y + 26, 9, fill=INK, line=INK)               # clicky stick
    c.circle(x + 16, y + 26, 6, fill=PAPER, line=INK, pat="checker")
    c.circle(x + w - 22, y + 30, 4, fill=INK, line=INK)
    c.circle(x + w - 11, y + 22, 4, fill=INK, line=INK)
    return c


def ngpc():
    return ngp(True)


# ----------------------------------------------------------------- Atari
def atari2600():
    c = new()
    x, y, w, h = 6, 40, 116, 34
    shadow(c, x, y + h, w)
    c.polybox([(x + 8, y), (x + w - 8, y), (x + w, y + 14), (x + w, y + h), (x, y + h), (x, y + 14)],
              fill=INK, line=INK)
    c.polybox([(x + 8, y + 1), (x + w - 8, y + 1), (x + w - 2, y + 12), (x + 2, y + 12)],
              fill=INK, line=None, pat="vlines", alt=PAPER)        # ribbed top
    c.rect(x + 1, y + 16, w - 2, h - 17, PAPER, "hlines3", alt=INK)  # woodgrain front
    c.rect(x + 1, y + 16, w - 2, 2, INK)
    c.box(x + 36, y + 3, 44, 9, fill=INK, line=INK, r=0)
    cart(c, x + 42, y - 18, 32, 22, fill=INK)
    c.rect(x + 45, y - 12, 26, 10, PAPER)
    c.rect(x + 47, y - 10, 22, 2, INK)
    for i in range(4):                                             # silver switches
        sx = x + 10 + i * 9 if i < 2 else x + w - 28 + (i - 2) * 9
        c.rect(sx, y + 4, 5, 7, PAPER)
        c.rect(sx + 1, y + 5, 3, 2, INK)
    joystick(c, 130, 66)
    return c


def atari5200():
    c = new()
    x, y, w, h = 4, 34, 120, 44
    shadow(c, x, y + h, w)
    c.polybox([(x + 10, y), (x + w - 10, y), (x + w, y + 12), (x + w, y + h), (x, y + h), (x, y + 12)],
              fill=INK, line=INK)
    c.rect(x + 2, y + 16, w - 4, 6, PAPER, "hlines", alt=INK)
    c.box(x + 18, y + 3, 50, 10, fill=INK, line=PAPER, r=0)
    c.box(x + 76, y + 4, 34, 8, fill=PAPER, line=PAPER, r=0)
    c.rect(x + 78, y + 6, 30, 4, INK, "checker")
    c.rect(x + 2, y + 28, w - 4, 14, INK, "checker")
    # keypad controller
    px, py = 120, 46
    c.box(px, py, 34, 50, fill=INK, line=INK, r=2)
    c.circle(px + 17, py + 10, 7, fill=INK, line=PAPER)
    c.rect(px + 16, py + 4, 3, 6, PAPER)
    for r in range(4):
        for k in range(3):
            c.rect(px + 7 + k * 8, py + 22 + r * 6, 5, 4, PAPER)
    return c


def atari7800():
    c = new()
    x, y, w, h = 6, 34, 114, 40
    shadow(c, x, y + h, w)
    c.polybox([(x + 6, y), (x + w - 6, y), (x + w, y + 10), (x + w, y + h), (x, y + h), (x, y + 10)],
              fill=INK, line=INK)
    c.rect(x + 1, y + 1, w - 2, 9, PAPER, "vlines", alt=INK)
    c.polybox([(x + 18, y + 14), (x + w - 18, y + 14), (x + w - 22, y + 24), (x + 22, y + 24)],
              fill=PAPER, line=PAPER, pat="d25", alt=PAPER)
    c.box(x + 38, y + 15, 38, 7, fill=INK, line=INK, r=0)
    c.rect(x + 1, y + 28, w - 2, 2, PAPER)
    for i in range(4):
        c.rect(x + 6 + i * 6, y + 31, 3, 6, PAPER)
    tiny(c, x + w - 6, y + 31, "7800", PAPER, "ra")
    # pro-line stick
    px, py = 126, 66
    c.box(px, py + 8, 26, 20, fill=INK, line=INK, r=2)
    c.rect(px + 11, py - 6, 4, 16, INK)
    c.oval(px + 8, py - 9, 10, 6, fill=INK, line=INK)
    c.rect(px + 2, py + 12, 4, 4, PAPER)
    c.rect(px + 20, py + 12, 4, 4, PAPER)
    return c


def atari800():
    return _computer("ATARI 800", keys_dark=False, slot=True)


def atarilynx():
    c = new()
    x, y, w, h = 4, 28, 152, 58
    shadow(c, x + 8, y + h, w - 16)
    c.box(x, y, w, h, fill=INK, line=INK, r=6)
    c.rect(x + 2, y + 2, w - 4, h - 4, INK, "d12", alt=INK)
    c.box(x + 40, y + 5, 74, 46, fill=INK, line=PAPER, r=1)
    scene(c, x + 44, y + 9, 66, 38, "space")
    c.circle(x + 20, y + 29, 11, fill=INK, line=PAPER)
    dpad(c, x + 20, y + 29, 4, PAPER, INK)
    for i, (bx, by) in enumerate(((x + 128, y + 22), (x + 140, y + 32), (x + 128, y + 40), (x + 140, y + 14))):
        c.circle(bx, by, 3, fill=PAPER, line=PAPER)
    for i in range(5):
        c.hline(x + 6, y + 47 + i * 2, 18, PAPER, "checker")
    c.rect(x + 46, y + 53, 60, 1, PAPER)
    return c


def atarist():
    return _computer("ATARI ST", keys_dark=False, floppy=True, wedge=True)


def atarijaguar():
    c = new()
    x, y, w, h = 6, 30, 118, 46
    shadow(c, x, y + h, w)
    c.ellipse(x, y + 4, w, h - 4, INK)
    c.rect(x + 10, y + h // 2, w - 20, h // 2, INK)
    c.ellipse(x + 6, y + 8, w - 12, h - 16, INK, "d12", alt=INK)
    c.box(x + 36, y + 6, 46, 10, fill=INK, line=PAPER, r=2)
    cart(c, x + 40, y - 18, 38, 26, fill=INK)
    c.rect(x + 43, y - 12, 32, 10, PAPER)
    c.rect(x + 45, y - 10, 28, 2, INK)
    c.circle(x + 18, y + 26, 5, fill=INK, line=PAPER)
    c.rect(x + 50, y + 30, 20, 2, PAPER)
    # keypad pad
    px, py = 114, 58
    c.ellipse(px, py, 44, 26, INK)
    c.rect(px + 12, py + 12, 20, 26, INK)
    dpad(c, px + 9, py + 11, 3, PAPER, INK)
    for i in range(3):
        c.circle(px + 25 + i * 6, py + 12 - i * 2, 2, fill=PAPER, line=PAPER)
    for r in range(3):
        for k in range(3):
            c.rect(px + 15 + k * 5, py + 20 + r * 5, 3, 3, PAPER)
    return c


# ---------------------------------------------------------------- Bandai
def wonderswan(color=False):
    c = new()
    x, y, w, h = 14, 28, 132, 54
    shadow(c, x + 4, y + h, w - 8)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=5)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "d12" if color else "d25")
    c.box(x + 32, y + 5, 72, 44, fill=INK, line=INK, r=2)
    scene(c, x + 37, y + 9, 62, 36, "platform")
    c.frame(x + 36, y + 8, 64, 38, PAPER)
    for i, (dx, dy) in enumerate(((0, -5), (5, 0), (-5, 0), (0, 5))):   # X pad
        c.rect(x + 14 + dx - 2, y + 18 + dy - 1, 5, 3, INK)
    for i, (dx, dy) in enumerate(((0, -5), (5, 0), (-5, 0), (0, 5))):   # Y pad
        c.rect(x + 14 + dx - 2, y + 38 + dy - 1, 5, 3, INK, "checker")
    c.circle(x + w - 18, y + 28, 4, fill=INK, line=INK)
    c.circle(x + w - 10, y + 36, 4, fill=INK, line=INK)
    return c


def wonderswancolor():
    return wonderswan(True)


# ----------------------------------------------------- other consoles
def colecovision():
    c = new()
    x, y, w, h = 4, 34, 116, 40
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, 12, PAPER, "vlines", alt=INK)
    c.box(x + 6, y + 16, 44, 8, fill=INK, line=PAPER, r=0)
    c.rect(x + 54, y + 16, 56, 2, PAPER)
    c.rect(x + 54, y + 22, 56, 2, PAPER)
    c.box(x + 24, y + 26, 22, 12, fill=INK, line=PAPER, r=0)       # pad docks
    c.box(x + 70, y + 26, 22, 12, fill=INK, line=PAPER, r=0)
    _keypad_ctrl(c, 122, 40)
    return c


def _keypad_ctrl(c, px, py, w=30, h=56):
    c.box(px, py, w, h, fill=INK, line=INK, r=2)
    c.circle(px + w // 2, py + 10, 6, fill=PAPER, line=PAPER)
    c.rect(px + w // 2 - 1, py + 6, 3, 8, INK)
    for r in range(4):
        for k in range(3):
            c.rect(px + 5 + k * 8, py + 24 + r * 7, 5, 4, PAPER)
    c.rect(px - 1, py + 18, 2, 4, PAPER)
    c.rect(px + w - 1, py + 18, 2, 4, PAPER)


def intellivision():
    c = new()
    x, y, w, h = 4, 36, 120, 36
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "hlines3", alt=PAPER)    # woodgrain
    c.box(x + 34, y + 6, 52, 22, fill=PAPER, line=INK, r=0)
    c.rect(x + 36, y + 8, 48, 18, INK, "d25")
    c.rect(x + 2, y + h - 6, w - 4, 4, INK)
    for k, px in enumerate((126, 4)):
        if k:
            continue
        c.box(px, 44, 28, 52, fill=PAPER, line=INK, r=1)
        c.rect(px + 2, 46, 24, 30, INK, "d25")
        for r in range(4):
            for q in range(3):
                c.rect(px + 4 + q * 8, 48 + r * 7, 5, 4, INK)
        c.circle(px + 14, 86, 7, fill=PAPER, line=INK)
        c.circle(px + 14, 86, 4, fill=INK, line=INK, pat="checker")
    return c


def vectrex():
    c = new()
    x, y, w, h = 30, 2, 76, 98
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=2)
    c.box(x + 6, y + 6, w - 12, 70, fill=INK, line=PAPER, r=1)
    # vector graphics: a wireframe ship + stars
    c.line([(x + 24, y + 54), (x + 38, y + 26), (x + 52, y + 54), (x + 38, y + 46), (x + 24, y + 54)], PAPER)
    c.line([(x + 14, y + 20), (x + 22, y + 16), (x + 26, y + 24), (x + 14, y + 20)], PAPER)
    c.line([(x + 50, y + 14), (x + 60, y + 20), (x + 54, y + 28), (x + 50, y + 14)], PAPER)
    c.px(x + 30, y + 12, PAPER)
    c.px(x + 58, y + 40, PAPER)
    c.px(x + 16, y + 62, PAPER)
    c.rect(x + 6, y + 80, w - 12, 12, PAPER, "hlines", alt=INK)
    # control panel
    px, py = 108, 76
    c.box(px, py, 48, 18, fill=INK, line=INK, r=1)
    c.circle(px + 10, py + 9, 4, fill=INK, line=PAPER)
    c.rect(px + 9, py + 3, 3, 6, PAPER)
    for i in range(4):
        c.circle(px + 22 + i * 7, py + 10, 2, fill=PAPER, line=PAPER)
    return c


def odyssey2():
    c = new()
    x, y, w, h = 4, 30, 122, 50
    shadow(c, x, y + h, w)
    c.polybox([(x, y + 10), (x + w, y), (x + w, y + h), (x, y + h)], fill=INK, line=INK)
    c.polybox([(x + 4, y + 14), (x + w - 4, y + 5), (x + w - 4, y + 18), (x + 4, y + 26)],
              fill=PAPER, line=PAPER, pat="d25", alt=PAPER)
    for r in range(4):                                             # membrane keyboard
        for k in range(10):
            c.rect(x + 8 + k * 11, y + 28 + r * 5, 8, 3, PAPER)
    joystick(c, 130, 64)
    return c


def channelf():
    c = new()
    x, y, w, h = 4, 34, 122, 40
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, 14, PAPER, "hlines3", alt=INK)
    for i in range(4):
        c.box(x + 10 + i * 16, y + 20, 12, 8, fill=PAPER, line=PAPER, r=1)
    c.box(x + 80, y + 18, 34, 14, fill=INK, line=PAPER, r=0)
    c.box(x + 86, y + 6, 22, 14, fill=PAPER, line=INK, r=0)        # yellow cart
    # plunger stick
    px, py = 134, 44
    c.rect(px + 4, py + 10, 10, 40, INK)
    c.polybox([(px, py), (px + 18, py), (px + 14, py + 12), (px + 4, py + 12)], fill=INK, line=INK)
    c.rect(px + 6, py + 2, 6, 3, PAPER)
    return c


def supervision():
    c = new()
    x, y, w, h = 18, 26, 124, 58
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=3)
    c.rect(x + 2, y + 2, w - 4, h - 4, INK, "d12", alt=INK)
    c.box(x + 36, y + 6, 52, 46, fill=PAPER, line=INK, r=0)
    scene(c, x + 40, y + 10, 44, 38, "tetris")
    c.circle(x + 18, y + 28, 9, fill=INK, line=PAPER)
    dpad(c, x + 18, y + 28, 4, PAPER, INK)
    c.circle(x + w - 22, y + 32, 4, fill=PAPER, line=PAPER)
    c.circle(x + w - 11, y + 24, 4, fill=PAPER, line=PAPER)
    c.rect(x + 4, y - 2, 24, 4, INK)                               # hinge clips
    c.rect(x + w - 28, y - 2, 24, 4, INK)
    return c


def arduboy():
    c = new()
    x, y, w, h = 42, 6, 76, 92
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=PAPER, line=INK, r=2)
    c.rect(x + 1, y + 1, w - 2, h - 2, INK, "d25")
    c.box(x + 6, y + 6, w - 12, 40, fill=INK, line=INK, r=1)
    scene(c, x + 10, y + 10, w - 20, 32, "space")
    c.rect(x + 6, y + 50, w - 12, 2, INK)
    for dx, dy in ((0, -7), (7, 0), (-7, 0), (0, 7)):
        c.rect(x + 18 + dx - 2, y + 68 + dy - 2, 5, 5, INK)
    c.circle(x + w - 22, y + 72, 4, fill=INK, line=INK)
    c.circle(x + w - 11, y + 66, 4, fill=INK, line=INK)
    return c


def uzebox():
    c = new()
    x, y, w, h = 14, 40, 104, 34
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    c.rect(x + 1, y + 1, w - 2, h - 2, PAPER, "grid4", alt=INK)    # bare PCB
    c.box(x + 10, y + 6, 26, 14, fill=INK, line=PAPER, r=0)
    for i in range(6):
        c.px(x + 12 + i * 4, y + 5, PAPER)
        c.px(x + 12 + i * 4, y + 21, PAPER)
    c.box(x + 46, y + 8, 40, 10, fill=INK, line=PAPER, r=0)
    c.box(x + 10, y + 24, 12, 6, fill=PAPER, line=PAPER, r=0)
    c.box(x + 26, y + 24, 12, 6, fill=PAPER, line=PAPER, r=0)
    pad_snes(c, 108, 78)
    return c


def threedo():
    c = new()
    x, y, w, h = 6, 32, 120, 42
    shadow(c, x, y + h, w)
    c.polybox([(x + 4, y), (x + w - 4, y), (x + w, y + 8), (x + w, y + h), (x, y + h), (x, y + 8)],
              fill=INK, line=INK)
    c.box(x + 6, y + 6, 70, 18, fill=INK, line=PAPER, r=1)
    c.rect(x + 8, y + 8, 66, 14, PAPER, "d12", alt=INK)
    c.rect(x + 8, y + 26, 60, 2, PAPER)
    c.box(x + 84, y + 8, 26, 6, fill=PAPER, line=PAPER, r=1)
    c.box(x + 84, y + 18, 12, 6, fill=INK, line=PAPER, r=1)
    c.box(x + 98, y + 18, 12, 6, fill=INK, line=PAPER, r=1)
    c.rect(x + 1, y + 32, w - 2, 9, INK, "checker")
    disc(c, 24, 88, 12)
    pad_rect(c, 108, 80)
    return c


# ------------------------------------------------------------- computers
def _computer(name, keys_dark=False, floppy=False, slot=False, wedge=True, dark=False, monitor=False, tape=False):
    c = new()
    x, y, w, h = 4, 46, 132, 46
    body_fill = INK if dark else PAPER
    key_fill = PAPER if dark else INK
    shadow(c, x, y + h, w)
    if wedge:
        c.polybox([(x + 4, y), (x + w - 4, y), (x + w, y + h), (x, y + h)], fill=body_fill, line=INK)
    else:
        c.box(x, y, w, h, fill=body_fill, line=INK, r=2)
    if not dark:
        c.rect(x + 2, y + h - 8, w - 4, 6, INK, "d25")
    c.hline(x + 2, y + h - 9, w - 4, INK if not dark else PAPER, "checker")
    # keyboard
    ky = y + 8
    rows = (13, 12, 12, 11)
    for r, n in enumerate(rows):
        off = x + 10 + r * 3
        for k in range(n):
            kx = off + k * 8
            col = key_fill if not keys_dark else INK
            c.rect(kx, ky + r * 6, 6, 4, col)
            if not dark:
                c.px(kx + 1, ky + r * 6, PAPER)
    c.rect(x + 34, ky + 24, 60, 4, key_fill)                       # space bar
    if floppy:
        c.box(x + w - 30, y + 30, 22, 6, fill=INK, line=INK, r=0)
        c.hline(x + w - 28, y + 32, 18, PAPER)
    if slot:
        c.box(x + 34, y - 4, 50, 6, fill=INK, line=INK, r=0)
    tiny(c, x + 8, y + h - 7, name, INK if not dark else PAPER)
    if monitor:
        _monitor(c, 26, 0, 88, 46)
    return c


def _monitor(c, x, y, w, h, scene_style="platform"):
    c.box(x, y, w, h, fill=PAPER, line=INK, r=2)
    c.rect(x + 1, y + h - 6, w - 2, 5, INK, "d25")
    c.box(x + 6, y + 4, w - 12, h - 12, fill=INK, line=INK, r=2)
    scene(c, x + 9, y + 7, w - 18, h - 18, scene_style)


def c64():
    c = new()
    x, y, w, h = 4, 40, 140, 44
    shadow(c, x, y + h, w)
    c.polybox([(x + 6, y), (x + w - 6, y), (x + w, y + h), (x, y + h)], fill=PAPER, line=INK)
    c.rect(x + 2, y + 1, w - 4, h - 2, INK, "d25")                 # breadbin beige-brown
    c.polybox([(x + 6, y), (x + w - 6, y), (x + w - 4, y + 6), (x + 4, y + 6)], fill=PAPER, line=INK)
    for r, n in enumerate((16, 15, 15, 14)):
        for k in range(n):
            kx = x + 10 + r * 3 + k * 7
            c.rect(kx, y + 10 + r * 6, 5, 4, INK)
            c.px(kx + 1, y + 10 + r * 6, PAPER)
    c.rect(x + 40, y + 34, 54, 4, INK)
    for i in range(4):                                              # F-keys
        c.rect(x + w - 16, y + 10 + i * 6, 8, 4, INK)
    c.rect(x + w - 12, y + 3, 6, 2, INK)                           # power LED strip
    c.rect(x + 1, y + h - 4, w - 2, 3, INK)
    tiny(c, x + 6, y + 1, "commodore 64", INK)
    # 1541 drive
    c.box(4, 8, 54, 28, fill=PAPER, line=INK, r=1)
    c.rect(5, 9, 52, 26, INK, "d25")
    c.box(10, 16, 40, 6, fill=INK, line=INK, r=0)
    c.rect(28, 22, 6, 4, INK)
    # datasette
    c.box(66, 14, 40, 22, fill=INK, line=INK, r=1)
    c.box(70, 17, 32, 10, fill=PAPER, line=PAPER, r=0)
    c.circle(78, 22, 2, fill=INK, line=INK)
    c.circle(94, 22, 2, fill=INK, line=INK)
    for i in range(5):
        c.rect(70 + i * 7, 30, 5, 3, PAPER)
    joystick(c, 132, 2)
    return c


def amiga():
    c = new()
    # A500 with the boing ball
    x, y, w, h = 2, 50, 144, 42
    shadow(c, x, y + h, w)
    c.polybox([(x + 4, y), (x + w - 4, y), (x + w, y + h), (x, y + h)], fill=PAPER, line=INK)
    c.rect(x + 2, y + h - 8, w - 4, 6, INK, "d25")
    for r, n in enumerate((14, 13, 13, 12)):
        for k in range(n):
            kx = x + 8 + r * 3 + k * 8
            c.rect(kx, y + 6 + r * 6, 6, 4, INK, "checker" if r == 0 else None)
            c.rect(kx + 1, y + 6 + r * 6 + 1, 4, 2, PAPER) if r == 0 else None
    c.rect(x + 36, y + 30, 56, 4, INK)
    c.box(x + w - 24, y + 14, 16, 6, fill=INK, line=INK, r=0)
    tiny(c, x + 8, y + h - 8, "AMIGA", PAPER)
    # boing ball
    cx, cy, r = 112, 22, 18
    c.circle(cx, cy, r, fill=PAPER, line=INK)
    for i in range(-r, r + 1):
        for j in range(-r, r + 1):
            if i * i + j * j < (r - 1) ** 2:
                u = (i + r + (j // 3)) // 6
                v = (j + r) // 6
                if (u + v) % 2 == 0:
                    c.px(cx + i, cy + j, INK)
    c.ellipse(cx - r + 6, cy + r + 4, 2 * r - 4, 6, INK, "checker")
    # mouse
    c.box(14, 22, 18, 24, fill=PAPER, line=INK, r=3)
    c.vline(23, 22, 8, INK)
    c.hline(14, 30, 18, INK)
    c.line([(23, 22), (30, 10), (44, 10)], INK)
    return c


def amstradcpc():
    c = new()
    # CPC 464: keyboard with integrated tape deck + green monitor
    _monitor(c, 36, 0, 88, 52, "platform")
    x, y, w, h = 4, 56, 152, 40
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    for r, n in enumerate((12, 11, 11, 10)):
        for k in range(n):
            kx = x + 6 + r * 3 + k * 7
            c.rect(kx, y + 6 + r * 6, 5, 4, PAPER if r else PAPER)
    c.rect(x + 28, y + 30, 40, 4, PAPER)
    c.box(x + 96, y + 4, 34, 22, fill=INK, line=PAPER, r=0)        # tape deck
    c.rect(x + 100, y + 8, 26, 10, PAPER, "checker", alt=INK)
    for i in range(4):
        c.rect(x + 98 + i * 8, y + 28, 6, 3, PAPER)
    for i in range(3):                                              # coloured F keys
        for j in range(3):
            c.rect(x + 134 + j * 5, y + 6 + i * 6, 4, 4, PAPER, "checker" if (i + j) % 2 else None)
    return c


def msx(version="MSX"):
    c = _computer(version, dark=True, wedge=False, slot=True)
    cart(c, 42, 20, 38, 30, fill=INK)
    c.rect(45, 26, 32, 14, PAPER)
    c.rect(47, 28, 28, 3, INK)
    c.rect(47, 34, 20, 2, INK, "checker")
    joystick(c, 132, 10)
    return c


def msx2():
    c = msx("MSX2")
    return c


def zxspectrum():
    c = new()
    x, y, w, h = 14, 34, 120, 52
    shadow(c, x, y + h, w)
    c.box(x, y, w, h, fill=INK, line=INK, r=1)
    for r, n in enumerate((10, 10, 10, 10)):                        # rubber keys
        for k in range(n):
            kx = x + 8 + r * 2 + k * 10
            c.box(kx, y + 8 + r * 9, 8, 6, fill=PAPER, line=PAPER, r=1)
            c.rect(kx + 1, y + 9 + r * 9, 6, 2, INK, "checker")
    # rainbow flash (as diagonal stripes)
    for i in range(4):
        c.line([(x + w - 26 + i * 4, y + h - 2), (x + w - 14 + i * 4, y + h - 12)], PAPER, 2)
    tiny(c, x + 6, y + h - 8, "ZX Spectrum", PAPER)
    c.rect(x + 2, y + 2, w - 4, 2, PAPER, "checker")
    return c


def x68000():
    c = new()
    # the twin-tower
    for i, tx in enumerate((20, 50)):
        c.box(tx, 4, 28, 90, fill=INK if i == 0 else INK, line=INK, r=1)
        c.rect(tx + 2, 6, 24, 86, PAPER, "vlines" if i == 0 else "d12", alt=INK)
    c.rect(48, 4, 2, 90, PAPER)
    c.box(28, 26, 44, 8, fill=INK, line=PAPER, r=0)                 # floppies
    c.box(28, 38, 44, 8, fill=INK, line=PAPER, r=0)
    c.hline(30, 30, 40, PAPER)
    c.hline(30, 42, 40, PAPER)
    c.rect(44, 0, 12, 6, INK)                                       # handle
    c.rect(46, 1, 8, 2, PAPER)
    shadow(c, 20, 94, 58)
    _monitor(c, 90, 30, 66, 52, "space")
    return c


def apple2():
    c = new()
    _monitor(c, 30, 0, 80, 46, "lines")
    c.rect(41, 9, 30, 4, PAPER)
    x, y, w, h = 14, 50, 112, 42
    shadow(c, x, y + h, w)
    c.polybox([(x + 4, y), (x + w - 4, y), (x + w, y + h), (x, y + h)], fill=PAPER, line=INK)
    c.rect(x + 2, y + 1, w - 4, 12, INK, "d25")
    for r, n in enumerate((11, 11, 10, 9)):
        for k in range(n):
            c.rect(x + 10 + r * 3 + k * 8, y + 16 + r * 5, 6, 3, INK)
    c.rect(x + 34, y + 36, 40, 3, INK)
    # disk II drive
    c.box(126, 56, 30, 22, fill=PAPER, line=INK, r=1)
    c.rect(130, 64, 22, 3, INK)
    c.rect(134, 70, 4, 4, INK)
    return c


def dos():
    c = new()
    # beige PC tower + CRT
    _monitor(c, 4, 4, 96, 72, "platform")
    c.box(30, 76, 44, 10, fill=PAPER, line=INK, r=1)                 # monitor stand
    c.rect(31, 77, 42, 8, INK, "d25")
    c.box(108, 4, 46, 92, fill=PAPER, line=INK, r=1)
    c.rect(109, 5, 44, 90, INK, "d12", alt=PAPER)
    c.box(114, 12, 34, 8, fill=PAPER, line=INK, r=0)                 # 5.25 drive
    c.hline(116, 16, 30, INK)
    c.box(114, 24, 34, 8, fill=PAPER, line=INK, r=0)                 # 3.5 drive
    c.rect(122, 27, 18, 2, INK)
    c.box(114, 40, 14, 6, fill=PAPER, line=INK, r=0)
    tiny(c, 118, 40, "486", INK)
    c.rect(132, 42, 3, 2, INK)
    c.rect(138, 42, 3, 2, INK, "checker")
    for i in range(8):
        c.hline(114, 60 + i * 3, 34, INK)
    c.box(4, 88, 98, 12, fill=PAPER, line=INK, r=1)                  # keyboard
    for k in range(15):
        c.rect(8 + k * 6, 91, 4, 2, INK)
        c.rect(10 + k * 6, 95, 4, 2, INK)
    shadow(c, 108, 96, 46)
    return c


# ------------------------------------------------------------- arcade
def arcade(marquee="ARCADE", style="cab"):
    c = new()
    # side-profile upright cabinet seen 3/4 front
    x = 44
    c.polybox([(x, 2), (x + 70, 2), (x + 70, 100), (x, 100)], fill=INK, line=INK)
    c.box(x + 4, 4, 62, 14, fill=PAPER, line=INK, r=0)               # marquee
    c.rect(x + 5, 5, 60, 12, INK, "d12", alt=PAPER)
    c.text(x + 35, 7, marquee, title_font(8), INK, "ma")
    c.polybox([(x + 4, 22), (x + 66, 22), (x + 62, 60), (x + 8, 60)], fill=INK, line=PAPER)   # bezel
    scene(c, x + 12, 26, 46, 30, "space")
    c.polybox([(x + 2, 62), (x + 68, 62), (x + 70, 74), (x, 74)], fill=PAPER, line=INK)        # panel
    c.rect(x + 14, 63, 3, 6, INK)
    c.circle(x + 15, 63, 3, fill=INK, line=INK)
    for i in range(3):
        c.circle(x + 32 + i * 8, 68, 2, fill=INK, line=INK)
        c.circle(x + 32 + i * 8, 64 + 0, 1, fill=INK, line=INK)
    c.rect(x + 24, 80, 22, 12, PAPER, "checker", alt=INK)             # coin door
    c.rect(x + 28, 83, 4, 6, PAPER)
    c.rect(x + 38, 83, 4, 6, PAPER)
    shadow(c, x, 100, 70)
    # side art
    c.polybox([(x + 70, 2), (x + 84, 8), (x + 84, 98), (x + 70, 100)], fill=INK, line=INK, pat="checker", alt=INK)
    return c


def mame():
    return arcade("MAME")


def fbneo():
    return arcade("FBNEO")


def cps():
    return arcade("CPS")


def _cps_boards():
    c = new()
    # a CPS-style "A/B board" stack
    for i in range(2):
        bx, by = 20 + i * 8, 20 + i * 18
        c.polybox([(bx, by + 20), (bx + 70, by), (bx + 120, by + 20), (bx + 50, by + 40)],
                  fill=INK, line=PAPER, pat="grid4", alt=INK)
    for k in range(6):
        cx = 60 + k * 10
        c.rect(cx, 52 - (k % 3) * 4, 8, 5, PAPER)
        c.rect(cx + 1, 53 - (k % 3) * 4, 6, 3, INK)
    c.line([(28, 78), (78, 98), (130, 78)], INK)
    shadow(c, 30, 98, 100)
    return c


def naomi():
    c = arcade("NAOMI")
    return c


# ---------------------------------------------------------- engines & misc
def scummvm():
    c = new()
    # point & click scene: verb panel + cursor
    c.box(8, 4, 144, 60, fill=PAPER, line=INK, r=1)
    c.rect(9, 44, 142, 19, INK, "d25")
    c.hline(9, 44, 142, INK)
    c.polybox([(20, 44), (40, 20), (60, 44)], fill=INK, line=INK, pat="checker", alt=PAPER)
    c.box(90, 18, 26, 26, fill=PAPER, line=INK, r=0)                  # door
    c.circle(110, 32, 1, fill=INK, line=INK)
    c.rect(126, 30, 6, 14, INK)                                       # pirate-ish hero
    c.rect(125, 26, 8, 5, INK)
    c.rect(127, 27, 4, 2, PAPER)
    c.box(8, 68, 144, 30, fill=INK, line=INK, r=1)
    verbs = ("OPEN", "CLOSE", "PUSH", "TALK", "LOOK", "USE")
    for i, v in enumerate(verbs):
        tiny(c, 16 + (i % 3) * 44, 72 + (i // 3) * 12, v, PAPER)
    # cursor crosshair
    for dx in (-6, -5, -4, 4, 5, 6):
        c.px(70 + dx, 30, INK)
        c.px(70, 30 + dx, INK)
    shadow(c, 8, 98, 144)
    return c


def easyrpg():
    c = new()
    # an RPG battle window: hero, slime, menu
    c.box(6, 4, 148, 58, fill=PAPER, line=INK, r=1)
    c.rect(7, 40, 146, 21, INK, "d12", alt=PAPER)
    c.rect(118, 24, 8, 12, INK)                                       # hero
    c.rect(116, 18, 12, 7, INK)
    c.rect(119, 20, 6, 3, PAPER)
    c.line([(126, 26), (136, 16)], INK, 2)                            # sword
    c.ellipse(30, 26, 24, 16, INK)                                    # slime
    c.rect(36, 30, 3, 3, PAPER)
    c.rect(45, 30, 3, 3, PAPER)
    c.ellipse(36, 28, 6, 3, PAPER, "checker")
    c.box(6, 66, 148, 32, fill=PAPER, line=INK, r=1)
    c.frame(8, 68, 144, 28, INK)
    tiny(c, 18, 72, "FIGHT", INK)
    tiny(c, 18, 82, "MAGIC", INK)
    tiny(c, 70, 72, "ITEM", INK)
    tiny(c, 70, 82, "RUN", INK)
    c.poly([(12, 73), (15, 75), (12, 77)], INK)
    tiny(c, 112, 72, "HP 42", INK)
    c.rect(112, 84, 34, 4, INK, "checker")
    c.rect(112, 84, 22, 4, INK)
    return c


def pico8():
    c = new()
    # a fantasy-console cartridge + tiny screen
    c.box(16, 14, 60, 80, fill=PAPER, line=INK, r=2)
    c.rect(17, 15, 58, 6, INK, "checker")
    c.box(22, 24, 48, 48, fill=INK, line=INK, r=0)
    scene(c, 24, 26, 44, 44, "platform")
    c.rect(22, 78, 48, 4, INK)
    c.rect(22, 85, 30, 2, INK, "checker")
    shadow(c, 16, 94, 60)
    c.box(88, 20, 64, 52, fill=INK, line=INK, r=2)
    c.text(120, 26, "PICO", title_font(8), PAPER, "ma")
    c.text(120, 38, "-8", title_font(16), PAPER, "ma")
    for i in range(8):
        c.rect(92 + i * 7, 62, 5, 5, PAPER, None if i % 2 else "checker", alt=INK)
    return c


def tic80():
    c = pico8()
    c.rect(89, 21, 62, 50, INK)
    c.text(120, 26, "TIC", title_font(8), PAPER, "ma")
    c.text(120, 38, "-80", title_font(16), PAPER, "ma")
    return c


def openbor():
    c = new()
    # side-scrolling beat'em up: two brawlers on a street
    c.rect(4, 4, 152, 64, INK, "d12", alt=PAPER)
    c.rect(4, 68, 152, 30, INK, "checker")
    c.hline(4, 68, 152, INK)
    for i, bx in enumerate((20, 70, 120)):
        c.box(bx, 14, 24, 54, fill=PAPER, line=INK, r=0)
        for wy in range(20, 60, 10):
            c.rect(bx + 4, wy, 6, 6, INK)
            c.rect(bx + 14, wy, 6, 6, INK, "checker")
    # hero
    c.rect(56, 56, 8, 16, INK)
    c.rect(55, 50, 8, 7, INK)
    c.rect(64, 58, 10, 3, INK)                                        # punch
    c.rect(72, 56, 5, 6, INK)
    c.rect(56, 72, 3, 10, INK)
    c.rect(61, 72, 3, 10, INK)
    # thug
    c.rect(88, 58, 9, 16, INK)
    c.rect(89, 51, 7, 7, INK)
    c.rect(90, 53, 2, 2, PAPER)
    c.rect(88, 74, 3, 8, INK)
    c.rect(94, 74, 3, 8, INK)
    # POW burst
    c.poly([(80, 46), (84, 52), (90, 48), (86, 54), (92, 58), (84, 57), (82, 63), (79, 56), (73, 57), (78, 52)], PAPER)
    c.poly([(80, 49), (83, 53), (86, 52), (84, 55), (87, 57), (83, 56), (82, 59), (80, 55), (77, 55), (79, 53)], INK)
    c.frame(4, 4, 152, 94, INK)
    return c


def ports():
    c = new()
    # a folder bursting with games
    c.polybox([(20, 24), (60, 24), (66, 32), (140, 32), (140, 96), (20, 96)], fill=PAPER, line=INK)
    c.rect(21, 33, 118, 2, INK)
    for i, (gx, gy) in enumerate(((34, 8), (62, 2), (92, 10))):
        cart(c, gx, gy, 30, 36, label=True)
    c.polybox([(16, 44), (144, 44), (138, 98), (22, 98)], fill=PAPER, line=INK)
    c.rect(17, 45, 126, 52, INK, "d25")
    c.box(54, 56, 52, 24, fill=PAPER, line=INK, r=2)
    tiny(c, 80, 63, "PORTS", INK, "ma")
    shadow(c, 22, 98, 118)
    return c


def doom():
    c = new()
    # first-person corridor + shotgun
    c.rect(4, 4, 152, 92, INK)
    c.poly([(4, 4), (52, 30), (52, 66), (4, 96)], PAPER, "d25", alt=INK)
    c.poly([(156, 4), (108, 30), (108, 66), (156, 96)], PAPER, "d25", alt=INK)
    c.poly([(52, 66), (108, 66), (156, 96), (4, 96)], PAPER, "checker", alt=INK)
    c.rect(52, 30, 56, 36, PAPER, "d12", alt=INK)
    c.rect(72, 40, 16, 26, INK)                                      # demon silhouette
    c.rect(70, 34, 20, 8, INK)
    c.px(75, 37, PAPER)
    c.px(84, 37, PAPER)
    c.poly([(70, 34), (66, 28), (72, 32)], INK)
    c.poly([(90, 34), (94, 28), (88, 32)], INK)
    c.rect(72, 72, 16, 24, PAPER)                                    # gun
    c.rect(75, 66, 10, 8, PAPER)
    c.rect(77, 66, 6, 30, INK, "vlines", alt=PAPER)
    c.rect(4, 86, 152, 10, PAPER)
    c.rect(6, 88, 148, 6, INK, "checker")
    c.frame(4, 4, 152, 92, INK)
    return c


def solarus():
    c = easyrpg()
    return c


def wasm4():
    c = new()
    c.box(40, 4, 80, 92, fill=PAPER, line=INK, r=3)
    c.box(48, 12, 64, 64, fill=INK, line=INK, r=0)
    scene(c, 50, 14, 60, 60, "platform")
    c.text(80, 82, "WASM-4", body_font(8), INK, "ma")
    shadow(c, 40, 96, 80)
    return c


def tools():
    c = new()
    # system preferences: gear + wrench + floppy
    c.circle(54, 50, 30, fill=PAPER, line=INK)
    import math
    for k in range(8):
        a = k * math.pi / 4
        cx, cy = 54 + int(round(math.cos(a) * 32)), 50 + int(round(math.sin(a) * 32))
        c.rect(cx - 4, cy - 4, 9, 9, INK)
    c.circle(54, 50, 26, fill=PAPER, line=INK, pat="d25")
    c.circle(54, 50, 10, fill=PAPER, line=INK)
    c.circle(54, 50, 5, fill=INK, line=INK)
    c.line([(96, 92), (136, 40)], INK, 7)
    c.line([(96, 92), (136, 40)], PAPER, 3)
    c.circle(138, 36, 8, fill=INK, line=INK)
    c.rect(136, 26, 5, 8, CLEAR)
    c.rect(134, 26, 9, 8, PAPER)
    c.box(100, 4, 40, 28, fill=INK, line=INK, r=1)                    # floppy
    c.rect(108, 4, 22, 10, PAPER)
    c.rect(122, 6, 5, 6, INK)
    c.rect(106, 18, 28, 12, PAPER)
    return c


def favorites():
    c = new()
    import math
    pts = []
    for k in range(10):
        r = 42 if k % 2 == 0 else 18
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((80 + int(round(math.cos(a) * r)), 54 + int(round(math.sin(a) * r))))
    c.polybox(pts, fill=PAPER, line=INK, pat="d25", alt=PAPER)
    inner = [(80 + (px_ - 80) * 2 // 3, 54 + (py_ - 54) * 2 // 3) for px_, py_ in pts]
    c.polybox(inner, fill=PAPER, line=INK)
    c.rect(70, 46, 3, 3, INK)
    c.rect(87, 46, 3, 3, INK)
    c.line([(72, 58), (76, 61), (84, 61), (88, 58)], INK)
    for sx, sy in ((24, 20), (134, 24), (30, 84), (130, 86)):
        c.rect(sx - 3, sy, 7, 1, INK)
        c.rect(sx, sy - 3, 1, 7, INK)
    return c


def lastplayed():
    c = new()
    c.circle(80, 52, 42, fill=PAPER, line=INK)
    c.circle(80, 52, 38, fill=PAPER, line=INK, pat="d12")
    c.circle(80, 52, 34, fill=PAPER, line=INK)
    import math
    for k in range(12):
        a = k * math.pi / 6
        x0, y0 = 80 + math.cos(a) * 30, 52 + math.sin(a) * 30
        c.rect(int(x0) - 1, int(y0) - 1, 3 if k % 3 == 0 else 2, 3 if k % 3 == 0 else 2, INK)
    c.line([(80, 52), (80, 28)], INK, 3)
    c.line([(80, 52), (96, 60)], INK, 3)
    c.circle(80, 52, 3, fill=INK, line=INK)
    c.poly([(116, 14), (132, 10), (126, 26)], INK)                     # rewind arrow
    return c


def allgames():
    c = new()
    for i in range(5):
        cart(c, 10 + i * 28, 20 + (i % 2) * 10, 30, 40)
    c.rect(4, 78, 152, 3, INK)
    for i in range(4):
        disc(c, 22 + i * 38, 90, 9)
    return c


def default():
    c = new()
    _monitor(c, 30, 4, 100, 70, "platform")
    c.box(60, 74, 40, 8, fill=PAPER, line=INK, r=1)
    c.box(20, 84, 120, 14, fill=PAPER, line=INK, r=1)
    for k in range(18):
        c.rect(24 + k * 6, 87, 4, 2, INK)
        c.rect(26 + k * 6, 92, 4, 2, INK)
    return c


ART = {
    "nes": nes, "famicom": famicom, "fds": fds, "snes": snes, "sfc": sfc, "n64": n64,
    "gb": gameboy, "gbc": gbc, "gba": gba, "nds": nds, "virtualboy": virtualboy,
    "pokemini": pokemini, "gameandwatch": gameandwatch,
    "sg1000": sg1000, "mastersystem": mastersystem, "genesis": genesis, "segacd": segacd,
    "sega32x": sega32x, "saturn": saturn, "dreamcast": dreamcast, "gamegear": gamegear,
    "psx": psx, "psp": psp,
    "pcengine": pcengine, "tg16": tg16, "pcenginecd": pcenginecd, "supergrafx": supergrafx, "pcfx": pcfx,
    "neogeo": neogeo, "ngp": ngp, "ngpc": ngpc,
    "atari2600": atari2600, "atari5200": atari5200, "atari7800": atari7800, "atari800": atari800,
    "atarilynx": atarilynx, "atarist": atarist, "atarijaguar": atarijaguar,
    "wonderswan": wonderswan, "wonderswancolor": wonderswancolor,
    "coleco": colecovision, "intellivision": intellivision, "vectrex": vectrex,
    "odyssey2": odyssey2, "channelf": channelf, "supervision": supervision, "arduboy": arduboy,
    "uzebox": uzebox, "3do": threedo,
    "c64": c64, "amiga": amiga, "amstradcpc": amstradcpc, "msx": msx, "msx2": msx2,
    "zxspectrum": zxspectrum, "x68000": x68000, "apple2": apple2, "dos": dos,
    "arcade": arcade, "mame": mame, "fbneo": fbneo, "cps": cps, "naomi": naomi,
    "scummvm": scummvm, "easyrpg": easyrpg, "pico8": pico8, "tic80": tic80, "openbor": openbor,
    "ports": ports, "doom": doom, "solarus": solarus, "wasm4": wasm4,
    "tools": tools, "favorites": favorites, "lastplayed": lastplayed, "allgames": allgames,
    "default": default,
}
