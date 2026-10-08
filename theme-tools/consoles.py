"""Pixel-art hardware illustrations for every system (120x80 logical px, x3)."""
import math

from pixelkit import Art, drk, lit, mixc

W, H = 120, 80
BASE = 72  # floor line


# ================================================================ controllers
def pad_nes(a, x, y, body="#c8c8cc", face="#202024", btn="#d02020"):
    a.blk(x, y, x + 21, y + 9, body, r=1)
    a.rect(x + 2, y + 2, x + 19, y + 7, face)
    a.dpad(x + 5, y + 5, "#5a5a62", 2)
    a.hl(x + 9, x + 10, y + 6, "#8a8a90")
    a.hl(x + 12, x + 13, y + 6, "#8a8a90")
    a.hl(x + 9, x + 13, y + 3, btn)
    a.button(x + 15, y + 5, btn)
    a.button(x + 18, y + 5, btn)


def b2(a, x, y, c):
    a.rect(x, y, x + 1, y + 1, c)
    a.px(x, y, lit(c, 0.45))
    a.px(x + 1, y + 1, drk(c, 0.35))


def pad_snes(a, x, y, body="#c4c4cc", cols=("#5a4aa0", "#5a4aa0", "#b4aadc", "#b4aadc")):
    a.blk(x, y, x + 25, y + 10, body, r=4)
    a.dpad(x + 6, y + 5, "#2a2a30", 2)
    a.hl(x + 11, x + 12, y + 6, "#707078")
    a.hl(x + 14, x + 15, y + 6, "#707078")
    a.ellipse(x + 16, y + 1, x + 24, y + 9, drk(body, 0.12))
    b2(a, x + 19, y + 2, cols[0])  # X
    b2(a, x + 17, y + 4, cols[2])  # Y
    b2(a, x + 21, y + 4, cols[1])  # A
    b2(a, x + 19, y + 6, cols[3])  # B


def pad_genesis(a, x, y, body="#26262c", btn="#3a3a44"):
    a.d.rounded_rectangle([x, y, x + 25, y + 11], radius=5, fill=body, outline=drk(body, 0.6))
    a.hl(x + 5, x + 20, y + 1, lit(body, 0.2))
    a.ellipse(x + 3, y + 3, x + 9, y + 9, "#3c3c46", "#101016")
    a.dpad(x + 6, y + 6, "#1a1a20", 2)
    for i in range(3):
        b2(a, x + 15 + i * 3, y + 6 - i, btn)
        a.px(x + 15 + i * 3, y + 6 - i, "#9090a0")
    a.hl(x + 11, x + 13, y + 4, "#c03030")


def pad_n64(a, x, y, body="#8c8c96"):
    o = drk(body, 0.6)
    for (x0, y0, x1, y1) in [(x, y + 3, x + 6, y + 13), (x + 10, y + 4, x + 15, y + 14),
                             (x + 19, y + 3, x + 25, y + 13)]:
        a.d.rounded_rectangle([x0, y0, x1, y1], radius=2, fill=body, outline=o)
    a.blk(x, y, x + 25, y + 7, body, r=3)
    a.dpad(x + 4, y + 4, "#2a2a30", 2)
    a.px(x + 12, y + 4, "#505058")
    a.rect(x + 12, y + 5, x + 13, y + 6, "#3a3a42")
    b2(a, x + 17, y + 4, "#2050d0")
    b2(a, x + 15, y + 2, "#20a040")
    for dx, dy in [(21, 1), (23, 3), (21, 5), (19, 3)]:
        a.px(x + dx, y + dy, "#f0c020")
    a.px(x + 12, y + 2, "#d02020")


def pad_psx(a, x, y, body="#b8b8c0"):
    o = drk(body, 0.6)
    a.d.rounded_rectangle([x, y + 3, x + 7, y + 13], radius=3, fill=body, outline=o)
    a.d.rounded_rectangle([x + 18, y + 3, x + 25, y + 13], radius=3, fill=body, outline=o)
    a.blk(x + 1, y, x + 24, y + 8, body, r=3)
    a.dpad(x + 5, y + 4, "#5a5a64", 2)
    a.px(x + 20, y + 2, "#20b060")
    a.px(x + 22, y + 4, "#e03040")
    a.px(x + 20, y + 6, "#4070e0")
    a.px(x + 18, y + 4, "#e070c0")
    a.rect(x + 9, y + 6, x + 10, y + 7, "#303038")
    a.rect(x + 15, y + 6, x + 16, y + 7, "#303038")
    a.hl(x + 11, x + 14, y + 3, "#707078")


def pad_saturn(a, x, y, body="#2a2a32"):
    a.d.rounded_rectangle([x, y, x + 25, y + 11], radius=5, fill=body, outline="#0c0c12")
    a.dpad(x + 6, y + 6, "#55555f", 2)
    cols = ["#d03030", "#e0c020", "#20a050", "#3060d0", "#30a0d0", "#a040c0"]
    for i, c in enumerate(cols):
        a.px(x + 15 + (i % 3) * 3, y + 4 + (i // 3) * 3 - (i % 3), c)
    a.hl(x + 3, x + 22, y, "#40404a")


def pad_dc(a, x, y, body="#e8e8ec"):
    o = drk(body, 0.55)
    a.d.rounded_rectangle([x, y, x + 25, y + 13], radius=5, fill=body, outline=o)
    a.rect(x + 9, y + 1, x + 16, y + 7, "#b8b8c0")
    a.rect(x + 10, y + 2, x + 15, y + 5, "#2a4040")
    a.px(x + 11, y + 3, "#80ffb0")
    a.dpad(x + 5, y + 9, "#606068", 2)
    a.px(x + 21, y + 5, "#d03030")
    a.px(x + 23, y + 7, "#3060d0")
    a.px(x + 19, y + 7, "#e0c020")
    a.px(x + 21, y + 9, "#20a050")
    a.ellipse(x + 3, y + 3, x + 6, y + 6, "#a0a0a8", "#606068")


def joystick(a, x, y, body="#1e1e24", btn="#d02020"):
    a.blk(x, y, x + 12, y + 9, body, r=1)
    a.hl(x + 1, x + 11, y + 1, "#3a3a44")
    a.blk(x + 1, y + 1, x + 4, y + 3, btn, r=0, bevel=False)
    a.rect(x + 5, y - 6, x + 7, y + 3, "#121216")
    a.vl(x + 5, y - 6, y + 2, "#3a3a44")
    a.blk(x + 4, y + 3, x + 8, y + 5, "#2c2c34", bevel=False)


def pad_generic(a, x, y, body, b1="#d03030", b2c="#3060d0", r=3, w=24, h=10):
    a.blk(x, y, x + w, y + h, body, r=r)
    a.dpad(x + 5, y + h // 2, "#26262c", 2)
    b2(a, x + w - 9, y + h // 2, b1)
    b2(a, x + w - 5, y + h // 2 - 2, b2c)


def keypad_pad(a, x, y, body="#2a2a30", keys="#c8c0a8", disc="#c0a050"):
    a.blk(x, y, x + 9, y + 18, body, r=1)
    for r in range(4):
        for c in range(3):
            a.px(x + 2 + c * 2, y + 2 + r * 2, keys)
    a.ellipse(x + 2, y + 11, x + 7, y + 16, disc, drk(disc, 0.5))


# ================================================================ Nintendo
def nes(a, label="NINTENDO"):
    LG, DG = "#c4c4ca", "#4a4a52"
    a.blk(10, 28, 84, 64, LG, r=1)
    a.rect(11, 29, 83, 31, lit(LG, 0.35))
    a.blk(10, 48, 84, 64, DG, r=1)
    for y in range(51, 63, 2):
        a.hl(46, 82, y, drk(DG, 0.3))
    a.blk(42, 33, 82, 46, LG, r=0)
    for y in range(36, 45, 3):
        a.hl(44, 80, y, drk(LG, 0.18))
    a.rect(14, 34, 37, 39, "#c02028")
    a.text(15, 35, "NES", "#f0f0f0")
    a.px(14, 51, "#ff3030")
    a.blk(17, 50, 26, 54, LG)
    a.blk(28, 50, 37, 54, LG)
    a.blk(17, 57, 22, 61, "#2a2a30")
    a.blk(25, 57, 30, 61, "#2a2a30")
    a.cart(48, 18, 74, 34, "#7a7a82", "#e8d8b8", "#d03030")
    a.cable([(88, 58), (92, 58), (94, 62)])
    pad_nes(a, 88, 60)


def famicom(a):
    W_, R = "#ece6d4", "#9c1c28"
    a.blk(8, 36, 88, 64, W_, r=2)
    a.blk(8, 52, 88, 64, R, r=1)
    a.text(12, 56, "FAMILY", "#e8c060")
    a.blk(36, 32, 60, 38, drk(W_, 0.25))
    a.cart(38, 18, 58, 35, "#d8c020", "#f8f0e0", "#e04030")
    a.blk(66, 40, 70, 46, R)
    a.blk(72, 40, 76, 46, R)
    a.blk(12, 40, 24, 48, R, r=1)
    a.dpad(16, 44, "#202020", 2)
    pad_generic(a, 92, 58, R, "#e8c060", "#e8c060", r=1, w=22, h=10)
    a.rect(94, 60, 112, 66, W_)
    a.dpad(98, 63, "#202020", 2)
    b2(a, 105, 63, R)
    b2(a, 109, 63, R)
    a.cable([(91, 62), (88, 60)], R)


def fds(a):
    R = "#a82024"
    a.blk(4, 40, 52, 66, "#ece6d4", r=2)
    a.blk(4, 56, 52, 66, "#9c1c28", r=1)
    a.blk(18, 36, 38, 42, "#3a3a40")
    a.cart(20, 26, 36, 39, "#3a3a42", "#d0d0d0", "#202020", ridges=False)
    a.slab(56, 32, 112, 68, lit(R, 0.15), R, depth=8, r=2)
    a.rect(62, 48, 106, 52, "#1a0808")
    a.blk(66, 30, 102, 50, "#f0c020", r=1)
    a.rect(70, 33, 98, 40, "#f8f0d0")
    a.text(72, 34, "DISK", "#c03020")
    a.ellipse(82, 42, 86, 46, "#806010")
    a.text(60, 58, "FAMICOM", "#f0e0c0")
    a.px(108, 58, "#40ff40")


def snes(a, jp=False, extra=None):
    G, P = "#c8c8d2", "#5b4a9c"
    if jp:
        P = "#7a7a86"
    a.blk(8, 30, 92, 64, G, r=4)
    a.rect(12, 31, 88, 33, lit(G, 0.4))
    a.blk(26, 26, 74, 34, drk(G, 0.12), r=2)
    a.blk(10, 52, 90, 64, drk(G, 0.1), r=3)
    a.blk(14, 38, 26, 46, P, r=2)
    a.blk(74, 38, 86, 46, P, r=2)
    a.blk(44, 40, 56, 46, drk(G, 0.3))
    a.blk(18, 55, 24, 60, "#3a3a44")
    a.blk(28, 55, 34, 60, "#3a3a44")
    a.px(16, 50, "#e02020")
    if jp:
        for i, c in enumerate(["#d02828", "#f0c020", "#20a040", "#3060d0"]):
            a.rect(64 + i * 5, 56, 67 + i * 5, 59, c)
    else:
        a.text(62, 56, "SNES", P)
    a.cart(34, 10, 66, 30, "#8a8a94" if not jp else "#7c7c88", "#f0e8d8", "#d04040")
    cols = ("#d02828", "#3060d0", "#20a040", "#f0c020") if jp else \
        ("#5a4aa0", "#5a4aa0", "#b4aadc", "#b4aadc")
    pad_snes(a, 90, 60, cols=cols)
    a.cable([(90, 64), (88, 60)])
    if extra:
        extra(a)


def satellaview(a):
    snes(a, jp=True)
    a.blk(6, 64, 94, 74, "#5a5a66", r=1)
    a.text(10, 67, "BS-X", "#f0d040")
    a.px(88, 67, "#40ff60")


def sufami(a):
    snes(a, jp=True)
    a.blk(30, 4, 70, 30, "#e8c840", r=2)
    a.text(36, 8, "SUFAMI", "#3a2a10")
    a.cart(34, 14, 48, 28, "#e85050", "#fff0e8", "#a02020", ridges=False)
    a.cart(52, 14, 66, 28, "#40a0e0", "#fff0e8", "#2060a0", ridges=False)


def snes_msu(a):
    snes(a)
    a.disc(104, 30, 9)
    a.text(96, 42, "MSU1", "#f0f0f0")


def n64(a):
    D = "#3a3a42"
    a.blk(8, 30, 92, 64, D, r=4)
    a.poly([(30, 34), (70, 34), (78, 64), (22, 64)], drk(D, 0.15))
    a.line([(30, 34), (22, 64)], lit(D, 0.25))
    a.blk(32, 36, 68, 46, lit(D, 0.08), r=2)
    for i, x in enumerate([34, 43, 52, 61]):
        a.blk(x, 52, x + 5, 58, "#202026")
    a.blk(12, 38, 20, 42, "#55555f")
    a.blk(80, 38, 88, 42, "#55555f")
    a.px(16, 46, "#ff3030")
    a.cart(36, 16, 64, 38, "#6a6a74", "#f0e8d8", "#2050c0")
    for i, c in enumerate(["#d02828", "#20a040", "#2050d0", "#f0c020"]):
        a.rect(12 + i * 2, 58, 12 + i * 2, 60, c)
    pad_n64(a, 92, 56)
    a.cable([(104, 56), (100, 52), (92, 52)])


def gb(a, body="#c8c4bc", btn="#a02860", scr="gb", cart=True, bezel="#5a5a6e", label="GAME BOY"):
    x0, y0, x1, y1 = 34, 4, 74, 72
    a.blk(x0, y0, x1, y1, body, r=2)
    a.rect(x1 - 6, y1 - 4, x1, y1, (0, 0, 0, 0))
    a.poly([(x1 - 7, y1), (x1, y1 - 7), (x1, y1)], (0, 0, 0, 0))
    a.line([(x1 - 7, y1), (x1, y1 - 7)], drk(body, 0.62))
    a.line([(x1 - 7, y1 - 1), (x1 - 1, y1 - 7)], drk(body, 0.3))
    a.blk(x0 + 4, y0 + 5, x1 - 4, y0 + 33, bezel, r=1, bevel=False)
    a.d.rounded_rectangle([x0 + 4, y0 + 5, x1 - 4, y0 + 33], radius=1, outline=drk(bezel, 0.5))
    a.rect(x1 - 8, y0 + 31, x1 - 5, y0 + 33, bezel)
    a.px(x0 + 6, y0 + 15, "#ff2020")
    scene(a, x0 + 10, y0 + 8, x1 - 10, y0 + 29, scr)
    a.text(x0 + 6, y0 + 36, label[:9], drk(body, 0.5))
    a.dpad(x0 + 8, y0 + 48, "#222228", 3)
    a.button(x1 - 7, y0 + 44, btn, 2)
    a.button(x1 - 13, y0 + 48, btn, 2)
    a.d.line([(x0 + 15, y0 + 57), (x0 + 17, y0 + 55)], fill=drk(body, 0.45))
    a.d.line([(x0 + 20, y0 + 57), (x0 + 22, y0 + 55)], fill=drk(body, 0.45))
    for i in range(5):
        a.line([(x1 - 13 + i * 2, y1 - 2), (x1 - 9 + i * 2, y1 - 7)], drk(body, 0.3))
    if cart:
        a.cart(80, 40, 102, 68, drk(body, 0.08), "#e8e0d0", btn)


def scene(a, x0, y0, x1, y1, kind):
    from pixelkit import scene as sc
    sc(a, x0, y0, x1, y1, kind)


def gbc(a):
    gb(a, body="#6c3cc0", btn="#383848", scr="gbc", bezel="#2a2a36", label="COLOR")


def megaduck(a):
    gb(a, body="#2e2e36", btn="#e0e0e0", scr="gb", bezel="#4a4a56", label="DUCK")


def pokemini(a):
    a.blk(30, 14, 90, 66, "#3070d0", r=8)
    a.blk(42, 20, 78, 44, "#202838", r=2)
    scene(a, 46, 23, 74, 41, "lcd")
    a.ellipse(54, 48, 66, 60, "#e0e0f0", "#203060")
    a.ellipse(57, 51, 63, 57, "#f0d020", "#806010")
    a.button(40, 54, "#e0e0f0", 2)
    a.button(80, 54, "#e0e0f0", 2)
    a.text(48, 61, "MINI", "#e0e8ff")


def landscape_handheld(a, body, scr="color", left="dpad", right=2, btncol="#3a3a44", w=92,
                       h=40, r=10, label=None, screen_w=36, bezel="#202028", shoulder=False,
                       labelcol=None, dark_bezel_pad=3):
    x0 = (W - w) // 2
    y0 = 20
    x1, y1 = x0 + w, y0 + h
    if shoulder:
        a.blk(x0 + 4, y0 - 3, x0 + 22, y0 + 4, drk(body, 0.2), r=2)
        a.blk(x1 - 22, y0 - 3, x1 - 4, y0 + 4, drk(body, 0.2), r=2)
    a.blk(x0, y0, x1, y1, body, r=r)
    cx = (x0 + x1) // 2
    sh = h - 12
    a.blk(cx - screen_w // 2, y0 + 5, cx + screen_w // 2, y0 + 5 + sh, bezel, r=1, bevel=False)
    p = dark_bezel_pad
    scene(a, cx - screen_w // 2 + p + 1, y0 + 5 + p, cx + screen_w // 2 - p - 1, y0 + 5 + sh - p, scr)
    lx = x0 + 11
    ly = y0 + h // 2
    if left == "dpad":
        a.dpad(lx, ly, "#26262c", 3)
    elif left == "stick":
        a.ellipse(lx - 4, ly - 4, lx + 4, ly + 4, drk(body, 0.3), drk(body, 0.6))
        a.ellipse(lx - 2, ly - 2, lx + 2, ly + 2, "#c8c8d0", "#606068")
    elif left == "cross":
        a.dpad(lx, ly - 4, "#26262c", 2)
        a.dpad(lx, ly + 5, "#26262c", 2)
    rx = x1 - 11
    if right == 2:
        a.button(rx - 3, ly + 2, btncol, 2)
        a.button(rx + 3, ly - 3, btncol, 2)
    elif right == 4:
        b2(a, rx - 1, ly - 5, "#20b060")
        b2(a, rx + 3, ly - 1, "#e03040")
        b2(a, rx - 1, ly + 3, "#4070e0")
        b2(a, rx - 5, ly - 1, "#e070c0")
    if label:
        a.ctext(cx, y1 - 5, label, labelcol or lit(body, 0.5))
    return x0, y0, x1, y1


def gba(a):
    x0, y0, x1, y1 = landscape_handheld(a, "#4a3ab0", "gbc", "dpad", 2, "#c8c8d8", w=96, h=42,
                                        r=12, label=None, screen_w=40, shoulder=True)
    a.hl(x0 + 30, x1 - 30, y1 - 4, lit("#4a3ab0", 0.35))
    a.cart(48, 64, 72, 76, "#3a3a44", "#e8e8f0", "#4a3ab0", ridges=False)


def gamegear(a):
    x0, y0, x1, y1 = landscape_handheld(a, "#26262e", "color", "dpad", 2, "#5a3a9a", w=100,
                                        h=44, r=8, screen_w=40, bezel="#121216")
    a.text(x0 + 5, y0 + 5, "GG", "#3070e0")
    a.hl(x0 + 30, x1 - 30, y1 - 3, "#3a3a46")


def lynx(a):
    x0, y0, x1, y1 = landscape_handheld(a, "#3a3a42", "dusk", "dpad", 2, "#5a5a66", w=110,
                                        h=40, r=6, screen_w=44, bezel="#18181e")
    a.rect(x0 + 2, y0 + 4, x0 + 4, y1 - 4, "#d03030")
    a.text(x1 - 20, y0 + 4, "LYNX", "#e8a040")


def ngp(a, color=False):
    body = "#3a8ad0" if color else "#2e2e36"
    x0, y0, x1, y1 = landscape_handheld(a, body, "color" if color else "lcd", "stick", 2,
                                        "#e0e0e8", w=84, h=42, r=10, screen_w=36)
    a.ctext((x0 + x1) // 2, y1 - 5, "NEOGEO", "#e8c050")


def wonderswan(a, color=False):
    body = "#d8dce4" if not color else "#3050c0"
    x0, y0, x1, y1 = landscape_handheld(a, body, "gbc" if color else "lcd", "cross", 2,
                                        "#5a5a66", w=96, h=42, r=6, screen_w=44)
    a.text(x0 + 4, y1 - 6, "WS", drk(body, 0.5) if not color else "#f0f0f0")


def psp(a):
    x0, y0, x1, y1 = landscape_handheld(a, "#1c1c22", "dusk", "dpad", 4, w=112, h=40, r=14,
                                        screen_w=56, bezel="#08080c", shoulder=False)
    a.hl(x0 + 14, x1 - 14, y0 + 1, "#4a4a56")
    a.ellipse(x0 + 9, y1 - 11, x0 + 13, y1 - 7, "#40404a", "#0a0a0e")
    a.ctext((x0 + x1) // 2, y1 - 5, "PSP", "#6a6a78")


def pspminis(a):
    psp(a)
    a.blk(92, 56, 112, 74, "#e0e0e8", r=1)
    a.text(94, 58, "MINI", "#2050c0")
    a.rect(94, 64, 110, 72, "#3060d0")


def nds(a):
    S = "#e4e4ea"
    a.blk(28, 2, 92, 36, S, r=4)
    a.blk(40, 6, 80, 32, "#1a1a20", r=1, bevel=False)
    scene(a, 43, 8, 77, 30, "color")
    a.blk(28, 38, 92, 76, S, r=4)
    a.rect(30, 35, 90, 38, drk(S, 0.35))
    a.blk(42, 42, 78, 68, "#1a1a20", r=1, bevel=False)
    scene(a, 45, 44, 75, 66, "dusk")
    a.dpad(35, 50, "#3a3a44", 2)
    for dx, dy, c in [(85, 47, "#5a5a66"), (88, 50, "#5a5a66"), (85, 53, "#5a5a66"), (82, 50, "#5a5a66")]:
        b2(a, dx, dy, c)
    a.line([(96, 30), (104, 72)], "#a0a0b0")
    a.px(104, 72, "#e0e0e8")


def gameandwatch(a):
    a.blk(10, 18, 110, 66, "#c8a050", r=3)
    a.blk(14, 22, 106, 62, "#d8d8dc", r=1)
    a.blk(36, 24, 84, 54, "#6a2a1a", r=1)
    scene(a, 39, 27, 81, 51, "lcd")
    a.ctext(60, 56, "GAME&WATCH", "#a03020")
    a.button(22, 50, "#e05020", 3)
    a.button(98, 50, "#e05020", 3)
    a.text(18, 27, "GAME", "#a03020")
    a.text(88, 27, "TIME", "#a03020")


def virtualboy(a):
    R, B = "#c01818", "#1a1a20"
    a.line([(40, 50), (30, 74)], B, 2)
    a.line([(80, 50), (90, 74)], B, 2)
    a.line([(60, 50), (60, 74)], B, 2)
    a.blk(18, 18, 102, 50, R, r=6)
    a.blk(26, 22, 94, 44, B, r=4)
    a.blk(34, 26, 56, 40, "#3a0808", r=2)
    a.blk(64, 26, 86, 40, "#3a0808", r=2)
    scene(a, 37, 29, 53, 37, "vb")
    scene(a, 67, 29, 83, 37, "vb")
    a.ctext(60, 45, "VIRTUAL BOY", "#f0e0e0")
    a.blk(48, 6, 72, 18, B, r=2)


def arduboy(a):
    a.blk(36, 8, 84, 72, "#e8e8ec", r=3)
    a.blk(40, 12, 80, 40, "#101014", r=1, bevel=False)
    a.rect(44, 16, 76, 36, "#000000")
    a.text(46, 18, "ARDU", "#ffffff")
    a.text(46, 25, "BOY", "#ffffff")
    a.hl(46, 72, 33, "#ffffff")
    a.dpad(48, 54, "#303038", 3)
    a.button(70, 56, "#303038", 2)
    a.button(76, 50, "#303038", 2)


def supervision(a):
    landscape_handheld(a, "#3a4a5a", "lcd", "dpad", 2, "#d03030", w=96, h=44, r=4, screen_w=40,
                       label="SUPERVISION")


def vmu(a):
    a.blk(36, 10, 84, 70, "#e8e8ec", r=8)
    a.blk(44, 16, 76, 38, "#3a5048", r=1)
    scene(a, 47, 19, 73, 35, "green")
    a.dpad(48, 52, "#7080a0", 3)
    a.button(68, 54, "#7080a0", 2)
    a.button(75, 49, "#7080a0", 2)


# ================================================================ Sega
def genesis(a, label="GENESIS", tag="16-BIT", lc="#e8e8f0"):
    B = "#22222a"
    a.blk(6, 34, 92, 64, B, r=3)
    a.hl(10, 88, 35, "#3c3c48")
    a.ellipse(28, 34, 66, 58, "#2c2c36", "#0c0c12")
    a.ellipse(36, 38, 58, 54, "#16161c", "#3a3a46")
    a.blk(36, 30, 58, 38, "#101016")
    a.cart(37, 12, 57, 34, "#202028", "#f0e8e0", "#3060d0")
    a.text(64, 40, tag, "#d03030")
    a.text(12, 58, label, lc)
    a.blk(10, 42, 22, 47, "#3a3a44")
    a.px(12, 50, "#ff3030")
    a.blk(70, 50, 86, 52, "#3a3a44")
    pad_genesis(a, 90, 58)
    a.cable([(90, 62), (86, 58)])


def megadrive(a):
    genesis(a, "MEGA DRIVE", "16-BIT", "#e8c060")


def sega32x(a):
    genesis(a)
    a.blk(28, 10, 66, 30, "#2c2c34", r=3)
    a.blk(32, 6, 62, 16, "#3a3a44", r=3)
    a.text(38, 20, "32X", "#d03030")
    a.blk(36, 26, 58, 34, "#16161c")


def segacd(a, label="SEGA CD"):
    B = "#26262e"
    a.slab(4, 50, 96, 76, "#34343e", B, depth=4, r=2)
    a.rect(10, 62, 60, 66, "#0c0c10")
    a.text(66, 62, label, "#d03030")
    a.px(90, 64, "#40ff40")
    # genesis sits on top, drawn smaller
    a.blk(14, 30, 86, 50, "#1e1e26", r=3)
    a.ellipse(30, 30, 62, 48, "#2c2c36", "#0c0c12")
    a.ellipse(38, 33, 54, 45, "#16161c", "#3a3a46")
    a.text(66, 36, "16-BIT", "#d03030")
    a.blk(36, 26, 56, 32, "#101016")
    a.cart(38, 12, 54, 30, "#202028", "#f0e8e0", "#3060d0")
    pad_genesis(a, 92, 62)


def megacd(a):
    segacd(a, "MEGA-CD")


def mastersystem(a):
    B = "#1c1c22"
    a.poly([(6, 64), (12, 34), (92, 34), (96, 64)], B, "#08080c")
    a.hl(13, 91, 35, "#3a3a46")
    for y in (42, 46, 50):
        a.hl(10, 94, y, "#c02020")
    a.blk(40, 30, 64, 36, "#0c0c10")
    a.cart(42, 14, 62, 33, "#1a1a20", "#f0f0f0", "#c02020")
    a.text(14, 56, "MASTER", "#e8e8f0")
    a.blk(70, 54, 78, 58, "#2c2c34")
    a.blk(82, 54, 90, 58, "#c02020")
    pad_generic(a, 96, 60, "#1c1c22", "#d0d0d8", "#d0d0d8", r=1, w=20, h=10)
    a.cable([(96, 64), (94, 60)])


def sg1000(a):
    B = "#2a2a32"
    a.blk(10, 34, 90, 64, B, r=2)
    a.blk(10, 52, 90, 64, "#c02028", r=1)
    a.text(14, 56, "SG-1000", "#f0f0f0")
    a.blk(36, 30, 64, 36, "#0c0c10")
    a.cart(38, 16, 62, 33, "#1a1a20", "#f0e8d8", "#c02028")
    joystick(a, 96, 58, "#2a2a32", "#c02028")


def gx4000(a):
    a.poly([(8, 66), (14, 40), (52, 32), (92, 40), (100, 66)], "#4a5a78", "#1c2030")
    a.poly([(20, 44), (52, 36), (84, 44), (84, 50), (20, 50)], "#2a3048")
    a.rect(20, 56, 86, 60, "#e04080")
    a.text(30, 58, "GX4000", "#f0f0f0")
    a.cart(40, 18, 64, 40, "#30303a", "#f8e8e0", "#e04080")
    pad_generic(a, 96, 60, "#4a5a78", "#e04080", "#e04080", r=2, w=20, h=10)


def saturn(a, jp=False):
    D = "#3c3c46" if not jp else "#c8c8d0"
    a.slab(8, 30, 92, 66, lit(D, 0.08), D, depth=22, r=3)
    a.ellipse(26, 33, 74, 49, drk(D, 0.12), drk(D, 0.5))
    a.ellipse(30, 35, 70, 47, lit(D, 0.1))
    a.text(36, 39, "SATURN", "#5080e0" if not jp else "#3a3a46")
    a.hl(12, 88, 56, "#2050c0")
    a.blk(14, 58, 22, 62, "#22222a")
    a.blk(78, 58, 86, 62, "#22222a")
    a.px(76, 32, "#40ff40")
    pad_saturn(a, 92, 60)
    a.cable([(92, 64), (90, 62)])


def dreamcast(a):
    Wt = "#ecece8"
    a.slab(12, 24, 88, 68, lit(Wt, 0.2), drk(Wt, 0.06), depth=28, r=4)
    a.ellipse(24, 26, 76, 48, drk(Wt, 0.12), drk(Wt, 0.4))
    cx, cy = 50, 37
    for t in range(0, 30):
        ang = t * 0.42
        r = 1 + t * 0.22
        a.px(int(cx + math.cos(ang) * r * 1.3), int(cy + math.sin(ang) * r * 0.8), "#f05a14")
    for i in range(4):
        a.blk(18 + i * 18, 58, 26 + i * 18, 63, "#b0b0b8")
    a.px(82, 54, "#f08020")
    pad_dc(a, 92, 58)


def naomi(a):
    arcade_cab(a, "#1a3a8a", "NAOMI", "#e8f0ff", "#f0b020")


def atomiswave(a):
    arcade_cab(a, "#20202a", "ATOMISWAVE", "#f08020", "#20c0f0")


# ================================================================ Sony / disc
def psx(a):
    G = "#c4c4cc"
    a.slab(8, 28, 92, 66, lit(G, 0.15), G, depth=26, r=2)
    a.ellipse(14, 30, 58, 52, drk(G, 0.1), drk(G, 0.45))
    a.ellipse(18, 32, 54, 50, lit(G, 0.22))
    a.ellipse(33, 38, 39, 44, drk(G, 0.2))
    for i, (x, c) in enumerate([(66, "#7a7a84"), (76, "#7a7a84"), (86, "#7a7a84")]):
        a.ellipse(x - 3, 36, x + 3, 42, lit(G, 0.1), drk(G, 0.5))
    a.rect(64, 44, 88, 48, drk(G, 0.25))
    for i, c in enumerate(["#e03040", "#f0c020", "#20b060", "#4070e0"]):
        a.px(66 + i * 2, 46, c)
    a.blk(14, 58, 24, 63, "#3a3a42")
    a.blk(76, 58, 86, 63, "#3a3a42")
    pad_psx(a, 92, 58)
    a.cable([(104, 58), (100, 56), (92, 56)])


def ps2(a):
    B = "#1c1c26"
    a.blk(14, 12, 82, 72, B, r=1)
    for y in range(16, 70, 4):
        a.hl(16, 80, y, "#2a2a38")
    a.rect(18, 30, 78, 33, "#0c0c10")
    a.rect(68, 20, 72, 24, "#3060e0")
    a.text(20, 62, "PS2", "#4070e0")
    pad_psx(a, 88, 58, "#26262e")


def threedo(a):
    B = "#1c1c22"
    a.slab(6, 34, 96, 66, "#2a2a32", B, depth=12, r=2)
    a.rect(20, 52, 70, 58, "#0c0c10")
    a.disc(46, 45, 10)
    a.blk(20, 52, 70, 56, "#2a2a34")
    a.text(76, 52, "3DO", "#e0b030")
    a.px(90, 60, "#ff4040")
    pad_generic(a, 96, 62, "#1c1c22", "#e0b030", "#e0b030", r=3, w=20, h=10)


def neogeocd(a):
    B = "#16161c"
    a.slab(8, 30, 92, 66, "#26262e", B, depth=22, r=3)
    a.ellipse(22, 32, 78, 50, "#1e1e26", "#0a0a0e")
    a.disc(50, 41, 7)
    a.text(12, 58, "NEOGEO CD", "#e8c050")
    pad_generic(a, 94, 58, "#16161c", "#e03030", "#f0c020", r=4, w=22, h=12)


def cdi(a):
    B = "#24242c"
    a.slab(6, 40, 104, 66, "#30303a", B, depth=6, r=1)
    a.rect(12, 50, 60, 53, "#0c0c10")
    a.rect(66, 49, 96, 56, "#081808")
    a.text(68, 50, "CD-I", "#40ff70")
    for i in range(4):
        a.blk(12 + i * 8, 57, 17 + i * 8, 61, "#4a4a56")
    a.disc(36, 30, 10)
    pad_generic(a, 92, 66, "#30303a", "#c0c0c8", "#c0c0c8", r=2, w=20, h=8)


def jaguar(a):
    B = "#16161c"
    a.d.rounded_rectangle([6, 38, 92, 66], radius=10, fill=B, outline="#060608")
    a.hl(14, 84, 39, "#30303a")
    a.blk(34, 32, 62, 40, "#0a0a0e")
    a.cart(36, 14, 60, 36, "#1c1c22", "#f0e8e0", "#d02020")
    a.text(14, 52, "JAGUAR", "#d02020")
    a.px(84, 50, "#d02020")
    pad_generic(a, 94, 56, B, "#d02020", "#d02020", r=4, w=22, h=14)
    for r in range(3):
        for c in range(3):
            a.px(103 + c * 2, 63 + r * 2 - 3, "#808090")


def cd32(a):
    B = "#30303a"
    a.slab(8, 30, 92, 66, "#3e3e48", B, depth=22, r=2)
    a.ellipse(20, 32, 60, 50, "#28282e", "#101014")
    a.text(64, 38, "CD32", "#e0e0e8")
    a.rect(64, 44, 88, 46, "#d02020")
    pad_generic(a, 94, 58, "#22222a", "#d02020", "#3060d0", r=4, w=22, h=10)


# ================================================================ NEC
def pcengine(a):
    Wt = "#ececf0"
    a.slab(22, 30, 78, 66, Wt, drk(Wt, 0.08), depth=20, r=2)
    a.rect(28, 34, 72, 40, "#3a3a44")
    a.rect(30, 30, 70, 36, "#d8d0b8")
    a.text(34, 31, "HUCARD", "#c02020")
    a.rect(24, 54, 76, 57, "#c02020")
    a.text(26, 59, "PC ENGINE", "#3a3a44")
    pad_generic(a, 86, 58, "#e8e8ec", "#3a3a44", "#3a3a44", r=2, w=24, h=10)
    a.cable([(86, 62), (78, 60)])


def tg16(a):
    B = "#1c1c22"
    a.slab(6, 36, 96, 66, "#26262e", B, depth=10, r=2)
    a.rect(6, 52, 96, 54, "#f07020")
    a.blk(10, 38, 34, 44, "#3a3a44")
    a.rect(12, 39, 32, 42, "#d8d0b8")
    a.text(40, 57, "TURBOGRAFX", "#f07020")
    for x in range(64, 92, 3):
        a.vl(x, 40, 48, "#30303a")
    pad_generic(a, 96, 62, B, "#f07020", "#f07020", r=2, w=20, h=10)


def supergrafx(a):
    G = "#6a6a74"
    a.slab(8, 26, 92, 66, lit(G, 0.2), G, depth=18, r=2)
    a.rect(14, 30, 50, 38, "#2a2a32")
    a.rect(16, 28, 48, 34, "#d8d0b8")
    a.text(14, 50, "SUPERGRAFX", "#f0f0f0")
    a.blk(60, 48, 86, 60, "#3a3a44", r=1)
    a.rect(14, 58, 50, 60, "#3060d0")
    pad_generic(a, 94, 60, "#3a3a44", "#f0f0f0", "#f0f0f0", r=2, w=22, h=10)


def pcenginecd(a):
    G = "#d8d8dc"
    a.slab(40, 18, 112, 66, lit(G, 0.2), G, depth=26, r=2)
    a.ellipse(54, 20, 98, 42, drk(G, 0.12), drk(G, 0.5))
    a.text(48, 54, "CD-ROM2", "#3a3a44")
    a.slab(6, 40, 46, 70, "#ececf0", "#d8d8e0", depth=14, r=2)
    a.rect(10, 44, 42, 48, "#3a3a44")
    a.rect(8, 62, 44, 64, "#c02020")


def tg16cd(a):
    B = "#1c1c22"
    a.slab(4, 50, 100, 74, "#26262e", B, depth=6, r=2)
    a.rect(4, 64, 100, 66, "#f07020")
    a.text(60, 58, "CD", "#f07020")
    a.slab(10, 22, 70, 50, "#2c2c34", "#202028", depth=16, r=2)
    a.ellipse(18, 24, 62, 36, "#1a1a20", "#08080c")
    a.disc(40, 30, 5)
    a.rect(74, 40, 96, 48, "#26262e")


def pcfx(a):
    B = "#2a2a36"
    a.blk(38, 6, 78, 72, B, r=2)
    a.hl(40, 76, 7, "#40404e")
    a.ellipse(44, 12, 72, 30, "#1c1c26", "#0a0a10")
    a.text(46, 36, "PC-FX", "#f0f0f0")
    a.rect(42, 46, 74, 48, "#d02050")
    for y in range(52, 68, 3):
        a.hl(42, 74, y, "#1c1c26")
    pad_generic(a, 88, 58, "#e0e0e8", "#3a3a44", "#3a3a44", r=3, w=24, h=12)


# ================================================================ Atari & co
def woodgrain(a, x0, y0, x1, y1, base="#7a4a22"):
    a.rect(x0, y0, x1, y1, base)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = math.sin(x * 0.35 + math.sin(y * 0.6) * 2.2)
            if v > 0.75:
                a.px(x, y, drk(base, 0.25))
            elif v < -0.85:
                a.px(x, y, lit(base, 0.15))


def atari2600(a):
    B = "#1c1a18"
    a.poly([(4, 66), (12, 34), (90, 34), (98, 66)], B, "#060606")
    for x in range(16, 88, 3):
        a.vl(x, 37, 44, "#2c2a26")
    a.blk(30, 30, 60, 38, "#0c0c0c")
    a.cart(34, 14, 56, 34, "#2a2622", "#f0e0c0", "#c02020")
    woodgrain(a, 6, 48, 96, 64)
    a.hl(6, 96, 48, "#3a2410")
    a.hl(6, 96, 64, "#3a2410")
    for i, x in enumerate([14, 26, 70, 82]):
        a.blk(x, 51, x + 6, 61, "#3a3634")
        a.blk(x + 2, 53, x + 4, 57, "#c8c8cc")
    a.text(38, 54, "ATARI", "#f0e0c0")
    joystick(a, 100, 58)
    a.cable([(106, 52), (104, 46), (96, 44)])


def atari7800(a):
    B = "#16161a"
    a.poly([(6, 66), (14, 38), (90, 38), (96, 66)], B, "#060606")
    a.rect(14, 40, 88, 44, "#c8c8d0")
    a.rect(10, 52, 92, 54, "#c02020")
    a.blk(36, 34, 64, 40, "#0a0a0c")
    a.cart(38, 16, 62, 37, "#202020", "#f0e8d0", "#3060d0")
    a.text(12, 58, "7800", "#c8c8d0")
    for x in (60, 70, 80):
        a.blk(x, 57, x + 6, 62, "#3a3a44")
    joystick(a, 100, 58, "#1e1e24", "#e0e0e0")


def atari5200(a):
    B = "#16161a"
    a.slab(4, 30, 96, 66, "#26262c", B, depth=16, r=2)
    a.rect(4, 46, 96, 50, "#c8c8d0")
    a.blk(30, 26, 60, 34, "#0a0a0c")
    a.cart(32, 10, 58, 30, "#262626", "#f0e8d0", "#3060d0")
    a.text(10, 56, "5200", "#c8c8d0")
    keypad_pad(a, 100, 50, "#1e1e24", "#c8c8d0", "#2a2a32")


def atari800(a):
    computer(a, "#d8ccb0", "#6a4a2a", label="ATARI 800", slot=True, keyrows=4)


def atarist(a):
    computer(a, "#d4d4d0", "#9a9a9a", label="ATARI ST", floppy=True, keyrows=5, mouse=True,
             accent="#3060d0")


def intellivision(a):
    a.slab(4, 34, 104, 66, "#c8a060", "#2c241c", depth=8, r=1)
    woodgrain(a, 6, 44, 70, 64, "#6a4422")
    a.rect(72, 44, 102, 64, "#c8a060")
    a.blk(74, 46, 86, 64, "#2a2a30")
    a.blk(88, 46, 100, 64, "#2a2a30")
    a.text(10, 37, "INTELLIVISION", "#3a2a10")
    keypad_pad(a, 106, 50, "#2a2a30", "#e8e0c8", "#c8a060")


def colecovision(a):
    B = "#16161a"
    a.slab(4, 34, 88, 66, "#26262c", B, depth=10, r=1)
    a.rect(8, 44, 50, 48, "#a0a0a8")
    a.text(10, 52, "COLECO", "#e0e0e8")
    a.blk(54, 46, 64, 62, "#2c2c34")
    a.blk(68, 46, 78, 62, "#2c2c34")
    a.blk(26, 28, 46, 36, "#0a0a0c")
    a.cart(28, 14, 44, 32, "#202020", "#f0e8d0", "#d02020", ridges=False)
    keypad_pad(a, 96, 48, "#16161a", "#c8c8d0", "#2a2a32")
    a.rect(99, 44, 102, 49, "#1e1e24")


def odyssey2(a):
    B = "#16161a"
    a.poly([(4, 66), (10, 34), (94, 34), (100, 66)], B, "#060606")
    a.rect(12, 38, 92, 40, "#c8c8d0")
    for r in range(4):
        for c in range(10):
            a.px(14 + c * 8 - r, 44 + r * 5, "#c8c8d0")
            a.px(15 + c * 8 - r, 44 + r * 5, "#c8c8d0")
    a.text(12, 61, "ODYSSEY2", "#e0b030")
    joystick(a, 100, 58, "#16161a", "#e04040")


def channelf(a):
    a.slab(6, 34, 92, 66, "#c8a060", "#2c241c", depth=8, r=1)
    woodgrain(a, 8, 44, 90, 64, "#6a4422")
    a.blk(12, 47, 42, 61, "#2a2a30")
    for i in range(4):
        a.blk(46 + i * 10, 50, 52 + i * 10, 56, "#e8e8e8")
    a.text(46, 59, "CHANNEL F", "#f0e0c0")
    a.blk(98, 46, 106, 70, "#1e1e24", r=2)
    a.blk(96, 38, 108, 46, "#e0e0e0", r=2)


def vectrex(a):
    B = "#16161a"
    a.blk(28, 2, 84, 66, B, r=2)
    a.hl(30, 82, 3, "#30303a")
    a.blk(33, 7, 79, 54, "#0a0a10", r=1, bevel=False)
    scene(a, 35, 9, 77, 52, "vector")
    a.text(36, 58, "VECTREX", "#e0e0e8")
    a.blk(20, 66, 92, 74, B, r=1)
    a.blk(30, 68, 40, 72, "#2a2a34")
    for i in range(4):
        a.button(62 + i * 7, 70, "#c02020", 2)
    a.stick(35, 68, B, "#2a2a34", h=5)


def thomson(a):
    computer(a, "#1e1e24", "#c8c8d0", label="THOMSON", keyrows=4, accent="#d02020",
             pen=True)


# ================================================================ computers
def computer(a, body, keys, label=None, slot=False, floppy=False, keyrows=4, mouse=False,
             accent=None, rainbow=False, monitor=None, keyalt=None, pen=False, flat=False,
             wedge=True, y0=30):
    x0, x1 = 6, 98
    if monitor:
        monitor_unit(a, 14, 2, 90, 40, monitor)
        y0 = 42
    if wedge:
        a.poly([(x0, 70), (x0 + 4, y0), (x1 - 4, y0), (x1, 70)], body, drk(body, 0.6))
        a.hl(x0 + 5, x1 - 5, y0 + 1, lit(body, 0.35))
        a.rect(x0 + 1, 66, x1 - 1, 69, drk(body, 0.15))
        a.hl(x0 + 1, x1 - 1, 70, drk(body, 0.6))
    else:
        a.blk(x0, y0, x1, 70, body, r=2)
    ky = y0 + 6
    kx0 = x0 + 8
    rows = keyrows
    for r in range(rows):
        off = (r % 2) * 2
        for c in range(13 - (r == rows - 1) * 0):
            x = kx0 + off + c * 6
            if x + 4 > x1 - 8:
                break
            col = keys
            if keyalt and (c in keyalt.get(r, ())):
                col = keyalt[r][c] if isinstance(keyalt[r], dict) else keyalt["c"]
            a.rect(x, ky + r * 5, x + 4, ky + r * 5 + 3, drk(col, 0.4))
            a.rect(x, ky + r * 5, x + 4, ky + r * 5 + 2, col)
            a.hl(x, x + 4, ky + r * 5, lit(col, 0.25))
    end = ky + rows * 5
    if end + 4 <= 64:
        a.rect(kx0 + 14, end, kx0 + 50, end + 3, drk(keys, 0.4))
        a.rect(kx0 + 14, end, kx0 + 50, end + 2, keys)
        end += 5
    if rainbow:
        for i, c in enumerate(["#e02020", "#f0c020", "#20b040", "#20b0e0"]):
            a.poly([(x1 - 22 + i * 3, 66), (x1 - 14 + i * 3, y0 + 2), (x1 - 12 + i * 3, y0 + 2),
                    (x1 - 20 + i * 3, 66)], c)
    if label:
        a.text(x0 + 6, min(end + 1, 64), label, accent or drk(body, 0.55))
    if slot:
        a.blk(30, y0 - 4, 60, y0 + 1, drk(body, 0.4))
        a.cart(34, y0 - 16, 56, y0, "#3a3a40", "#f0e8d8", "#d03030", ridges=False)
    if floppy:
        a.rect(x1 - 1, y0 + 14, x1, y0 + 22, "#2a2a30")
        a.blk(100, 52, 112, 64, "#2a2a34", r=0)
        a.rect(103, 52, 109, 56, "#c8c8d0")
        a.rect(104, 60, 108, 63, "#e8e0c0")
    if mouse:
        a.blk(102, 64, 110, 74, body, r=3)
        a.vl(106, 64, 68, drk(body, 0.4))
        a.line([(106, 64), (104, 58), (100, 56)], "#2a2a30")
    if pen:
        a.line([(104, 46), (110, 70)], "#d02020", 2)
    return y0


def monitor_unit(a, x0, y0, x1, y1, kind, body="#d8d0bc"):
    a.blk(x0, y0, x1, y1, body, r=2)
    a.blk(x0 + 4, y0 + 3, x1 - 4, y1 - 7, "#2a2a30", r=2, bevel=False)
    scene(a, x0 + 7, y0 + 5, x1 - 7, y1 - 9, kind)
    a.rect(x1 - 12, y1 - 5, x1 - 6, y1 - 4, drk(body, 0.3))
    a.px(x1 - 4, y1 - 4, "#40ff40")


def c64(a):
    computer(a, "#a89880", "#4e3c2c", label="COMMODORE 64", keyalt={3: {12: "#8a6a4a"}},
             accent="#3a2a1a")
    a.rect(84, 61, 92, 63, "#3060d0")
    a.rect(84, 63, 92, 64, "#d02020")
    joystick(a, 104, 56, "#1e1e24", "#e03030")


def vic20(a):
    computer(a, "#e4dcc8", "#5a4632", label="VIC-20", keyalt={0: {12: "#c0a060"}},
             accent="#5a4632")
    a.rect(84, 61, 92, 63, "#d02020")


def c16(a):
    computer(a, "#3a3a42", "#c8c8d0", label="C16", accent="#e0e0e8")
    joystick(a, 104, 56, "#1e1e24", "#e03030")


def c128(a):
    computer(a, "#d8d0bc", "#5a5248", label="C128", accent="#3a3226", keyrows=5)


def amiga(a):
    computer(a, "#e8e4d8", "#c4c0b4", label="AMIGA 500", floppy=False, keyrows=5,
             accent="#d02020", keyalt={0: {0: "#a8a4a0", 1: "#a8a4a0", 2: "#a8a4a0"}})
    a.rect(96, 50, 98, 54, "#2a2a30")
    # boing ball
    cx, cy, r = 108, 30, 9
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x * x + y * y <= r * r:
                half = math.sqrt(max(r * r - y * y, 0.01))
                u = int((math.asin(max(-1, min(1, x / half))) + 1.9) * 1.6)
                v = int((math.asin(y / r) + 1.6) * 1.9)
                c = "#e02020" if (u + v) % 2 else "#f4f4f4"
                if x + y > r * 0.9:
                    c = drk(c, 0.25)
                a.px(cx + x, cy + y, c)
    a.ellipse(100, 70, 116, 74, "#141436")


def amstradcpc(a):
    B = "#2c2c34"
    y0 = 36
    a.blk(4, y0, 100, 70, B, r=1)
    a.rect(6, y0 + 1, 98, y0 + 2, "#40404c")
    a.blk(70, y0 - 6, 98, y0 + 6, "#1c1c22", r=1)
    a.rect(74, y0 - 4, 94, y0 + 2, "#0a0a0c")
    a.rect(78, y0 - 3, 90, y0, "#606070")
    for r in range(4):
        for c in range(10):
            col = "#e8e8e8"
            if c >= 8:
                col = "#3070d0"
            if r == 3 and c < 2:
                col = "#30b040"
            a.rect(8 + c * 6 + (r % 2), y0 + 6 + r * 5, 12 + c * 6 + (r % 2), y0 + 9 + r * 5, col)
    a.rect(10, 64, 66, 66, "#e02020")
    a.text(76, 62, "CPC", "#e0e0e8")
    for i, c in enumerate(["#e02020", "#30b040", "#3070d0"]):
        a.rect(88 + i * 3, 62, 89 + i * 3, 66, c)


def zxspectrum(a):
    B = "#16161c"
    a.poly([(6, 70), (10, 36), (94, 36), (98, 70)], B, "#060608")
    a.hl(11, 93, 37, "#2c2c34")
    for r in range(4):
        for c in range(10):
            x = 14 + c * 7 + r
            a.rect(x, 42 + r * 5, x + 4, 44 + r * 5, "#8a8a96")
            a.hl(x, x + 4, 42 + r * 5, "#b0b0bc")
    a.text(12, 64, "ZX SPECTRUM", "#e0e0e8")
    for i, c in enumerate(["#e02020", "#f0c020", "#20b040", "#20b0e0"]):
        a.poly([(78 + i * 3, 70), (86 + i * 3, 58), (88 + i * 3, 58), (80 + i * 3, 70)], c)
    a.blk(102, 54, 116, 70, "#1e1e24", r=1)
    a.rect(105, 58, 113, 62, "#5a5a66")
    a.rect(104, 64, 114, 67, "#3a3a44")


def zx81(a):
    B = "#16161c"
    a.slab(10, 36, 90, 70, "#26262e", B, depth=4, r=1)
    a.rect(16, 44, 84, 62, "#101014")
    for r in range(4):
        for c in range(10):
            a.rect(18 + c * 7, 46 + r * 4, 21 + c * 7, 48 + r * 4, "#30303a")
            a.px(19 + c * 7, 47 + r * 4, "#e0e0e8")
    a.text(16, 64, "ZX81", "#d02020")
    a.blk(96, 44, 110, 70, "#e8e8e8", r=1)
    a.text(98, 48, "16K", "#2a2a30")


def msx(a, label="MSX", body="#26262e", keys="#9a9aa6", acc="#d02020"):
    computer(a, body, keys, label=label, slot=True, accent=lit(keys, 0.3),
             keyalt={4: {}, 0: {10: acc, 11: acc, 12: acc}}, keyrows=5)


def msx2(a):
    msx(a, "MSX2", "#c8c8d0", "#40404a", "#3060d0")


def msxturbor(a):
    msx(a, "TURBO R", "#2a2a32", "#d0d0d8", "#e0b020")


def apple2(a):
    B = "#d8ccae"
    monitor_unit(a, 22, 2, 82, 36, "green", "#c8c0a4")
    a.blk(10, 36, 94, 46, B, r=1)
    for i in range(2):
        a.blk(18 + i * 34, 38, 46 + i * 34, 45, "#cfc3a4", r=1)
        a.rect(22 + i * 34, 41, 42 + i * 34, 42, "#2a2a30")
    a.poly([(6, 72), (10, 48), (96, 48), (100, 72)], B, drk(B, 0.6))
    for r in range(4):
        for c in range(11):
            x = 16 + c * 6 + r
            a.rect(x, 52 + r * 5, x + 4, 55 + r * 5, "#3a3a3e")
            a.hl(x, x + 4, 52 + r * 5, "#5a5a60")
    a.text(16, 66, "APPLE II", "#3a3226")
    for i, c in enumerate(["#60b040", "#f0c020", "#f08020", "#e02020", "#a040a0", "#3080e0"]):
        a.hl(88, 91, 63 + i, c)


def dos(a):
    T = "#d8d0bc"
    a.blk(4, 6, 30, 72, T, r=1)
    a.rect(8, 12, 26, 15, drk(T, 0.3))
    a.rect(8, 18, 26, 21, drk(T, 0.3))
    a.rect(10, 13, 24, 13, "#2a2a30")
    a.rect(10, 19, 24, 19, "#2a2a30")
    a.px(8, 30, "#40ff40")
    a.px(8, 33, "#ffb000")
    for y in range(40, 68, 3):
        a.hl(8, 26, y, drk(T, 0.12))
    a.text(8, 24, "486", "#3a3226")
    monitor_unit(a, 36, 6, 104, 54, "dos", T)
    a.blk(60, 54, 80, 58, drk(T, 0.1))
    a.poly([(34, 74), (38, 62), (102, 62), (106, 74)], T, drk(T, 0.6))
    for r in range(2):
        for c in range(14):
            a.rect(40 + c * 4 + r, 64 + r * 4, 42 + c * 4 + r, 66 + r * 4, "#9a9488")


def pc98(a, label="PC-9801"):
    T = "#d8d4cc"
    monitor_unit(a, 22, 2, 86, 40, "dos", T)
    a.slab(6, 40, 102, 58, lit(T, 0.1), T, depth=4, r=1)
    a.rect(60, 48, 94, 50, "#3a3a40")
    a.rect(60, 53, 94, 55, "#3a3a40")
    a.text(12, 50, label, "#2050a0")
    a.poly([(8, 76), (12, 62), (96, 62), (100, 76)], T, drk(T, 0.6))
    for r in range(2):
        for c in range(20):
            a.rect(16 + c * 4 + r, 65 + r * 4, 18 + c * 4 + r, 67 + r * 4, "#8a8680")


def pc88(a):
    pc98(a, "PC-8801")


def x68000(a):
    D = "#30303a"
    for x in (10, 34):
        a.blk(x, 8, x + 20, 72, D, r=1)
        a.hl(x + 2, x + 18, 9, "#4a4a56")
        for y in range(40, 68, 3):
            a.hl(x + 3, x + 17, y, "#24242c")
    a.blk(10, 6, 54, 12, "#40404c", r=2)
    a.rect(13, 18, 27, 20, "#0a0a0c")
    a.rect(37, 18, 51, 20, "#0a0a0c")
    a.px(14, 26, "#40ff60")
    a.text(13, 30, "X68K", "#e0e0e8")
    monitor_unit(a, 58, 14, 116, 60, "dusk", "#3a3a44")
    a.blk(76, 60, 98, 66, "#3a3a44")


def x1(a):
    computer(a, "#c03030", "#f0f0f0", label="SHARP X1", monitor="dusk", accent="#f0f0f0",
             keyrows=3, wedge=False)


def coco(a):
    computer(a, "#b8bcc4", "#2a2a30", label="TRS-80 COCO", accent="#c02020", slot=True)


def ti99(a):
    computer(a, "#1e1e24", "#c8c8d0", label="TI-99/4A", accent="#c8c8d0", slot=False, keyrows=4)
    a.rect(6, 36, 98, 40, "#b0b4bc")
    a.blk(84, 26, 98, 38, "#2a2a30")
    a.cart(86, 14, 96, 30, "#3a3a40", "#f0e8d8", "#3060d0", ridges=False)


def bbcmicro(a):
    computer(a, "#d8ccae", "#3a2a1a", label="BBC MICRO", accent="#c02020",
             keyalt={0: {c: "#c02020" for c in range(10)}}, keyrows=4, wedge=False)


def samcoupe(a):
    computer(a, "#2a2a32", "#e8e8ec", label="SAM", accent="#e0b020", keyrows=4)


def oric(a):
    computer(a, "#e8e4dc", "#2a2a30", label="ORIC ATMOS", accent="#c02020", keyrows=4)


# ================================================================ arcade
def arcade_cab(a, side="#4a2a8a", marquee="ARCADE", mcol="#ffe040", trim="#e04080",
               scr="color"):
    x0, x1 = 34, 86
    a.poly([(x0, 2), (x0 + 6, 2), (x0 + 6, 76), (x0, 76)], drk(side, 0.25))
    a.blk(x0 + 4, 2, x1, 76, side, r=1)
    # marquee
    a.blk(x0 + 6, 4, x1 - 2, 15, "#101014", r=1, bevel=False)
    a.rect(x0 + 7, 5, x1 - 3, 14, "#18181e")
    a.ctext((x0 + 6 + x1 - 2) // 2, 7, marquee[:11], mcol)
    a.hl(x0 + 7, x1 - 3, 5, lit(mcol, 0.4))
    # screen
    a.blk(x0 + 7, 17, x1 - 3, 46, "#121216", r=1, bevel=False)
    scene(a, x0 + 10, 20, x1 - 6, 43, scr)
    # control panel
    a.poly([(x0 + 2, 52), (x0 + 6, 46), (x1 - 0, 46), (x1 + 4, 52)], lit(side, 0.25), drk(side, 0.6))
    a.blk(x0 + 2, 52, x1 + 4, 56, drk(side, 0.2))
    a.stick(x0 + 14, 50, "#16161a", "#e02020", h=5)
    for i, c in enumerate([trim, "#40a0ff", "#ffe040"]):
        a.px(x0 + 26 + i * 4, 49, c)
        a.px(x0 + 27 + i * 4, 49, drk(c, 0.3))
        a.px(x0 + 25 + i * 4 + 2, 51, c)
    # coin door
    a.blk(x0 + 18, 60, x1 - 12, 74, "#2a2a30", r=1)
    a.rect(x0 + 22, 63, x0 + 23, 66, "#ff4030")
    a.rect(x1 - 18, 63, x1 - 17, 66, "#ff4030")
    a.rect(x0 + 21, 69, x1 - 15, 70, "#121216")
    # side art stripe
    a.line([(x0 + 1, 60), (x0 + 5, 20)], trim, 1)
    a.line([(x0 + 3, 66), (x0 + 5, 40)], mcol, 1)


def arcade(a):
    arcade_cab(a)
    star(a, 16, 18, "#ffe040")
    star(a, 102, 28, "#e04080")
    star(a, 98, 60, "#40a0ff")


def star(a, cx, cy, c):
    a.hl(cx - 2, cx + 2, cy, c)
    a.vl(cx, cy - 2, cy + 2, c)
    a.px(cx, cy, "#ffffff")


def mame(a):
    arcade_cab(a, "#16305a", "MAME", "#40c0ff", "#f0f0f0")
    star(a, 18, 30, "#40c0ff")
    star(a, 102, 22, "#f0f0f0")


def fbneo(a):
    arcade_cab(a, "#1e5a30", "FBNEO", "#a0ff60", "#f0e040", scr="dusk")
    star(a, 102, 20, "#a0ff60")


def cps1(a):
    arcade_cab(a, "#8a1a1a", "CPS-1", "#ffe040", "#40a0ff")
    star(a, 16, 22, "#ffe040")


def cps2(a):
    arcade_cab(a, "#1a3a9a", "CPS-2", "#f0f0f0", "#e04040", scr="dusk")
    star(a, 104, 24, "#f0f0f0")


def cps3(a):
    arcade_cab(a, "#1a1a20", "CPS-3", "#ffd020", "#e04040", scr="space")
    star(a, 16, 50, "#ffd020")


def neogeo(a):
    arcade_cab(a, "#b01818", "NEO-GEO", "#f0c040", "#f0f0f0")
    star(a, 102, 30, "#f0c040")


def daphne(a):
    arcade_cab(a, "#2a1a4a", "LASERDISC", "#f0a0ff", "#40e0ff", scr="dusk")
    a.disc(102, 56, 10)


def model2(a):
    arcade_cab(a, "#2050b0", "MODEL 2", "#f0f0f0", "#f0c020", scr="color")


# ================================================================ VCR / tapes / CRT
def vcr_deck(a, display="0:22:37", led="#40ff70"):
    S = "#c8c8d0"
    a.slab(4, 34, 116, 66, lit(S, 0.15), "#2a2a32", depth=6, r=1)
    a.blk(10, 44, 54, 52, "#121216")
    a.hl(14, 50, 48, "#2a2a32")
    a.rect(60, 43, 96, 53, "#050a08")
    a.text(62, 46, display, led)
    for i in range(5):
        a.blk(60 + i * 8, 57, 65 + i * 8, 61, "#4a4a56")
    a.poly([(70, 58), (70, 60), (72, 59)], "#e0e0e8")
    a.px(102, 47, "#ff3030")
    a.blk(100, 54, 110, 62, "#3a3a44", r=3)
    a.text(10, 57, "VHS", "#e0e0e8")
    a.blk(26, 56, 50, 62, "#3a3a44")
    tape(a, 30, 8, 82, 36, title="E-180")


def tape(a, x0, y0, x1, y1, label="#f0f0f0", stripe="#e02060", title=None, tcol="#000fc0"):
    B = "#16161a"
    a.blk(x0, y0, x1, y1, B, r=1)
    a.rect(x0 + 6, y0 + 3, x1 - 6, y0 + (y1 - y0) // 2, label)
    a.rect(x0 + 6, y0 + 3, x1 - 6, y0 + 4, stripe)
    if title:
        a.ctext((x0 + x1) // 2, y0 + 6, title[:max(1, (x1 - x0 - 12) // 4)], tcol)
    wy = y0 + (y1 - y0) // 2 + 3
    a.rect(x0 + 12, wy, x1 - 12, wy + 5, "#0a0a0c")
    a.rect(x0 + 18, wy + 1, x1 - 18, wy + 4, "#3a3a44")
    for cx in (x0 + 16, x1 - 16):
        a.ellipse(cx - 3, wy - 1, cx + 3, wy + 5, "#d8d8e0", "#0a0a0c")
        a.px(cx, wy + 2, "#0a0a0c")
    a.rect(x0 + 2, y1 - 2, x1 - 2, y1 - 1, "#2a2a32")


def crt_tv(a, x0, y0, x1, y1, kind="osd", body="#5a4630"):
    a.blk(x0, y0, x1, y1, body, r=3)
    a.blk(x0 + 3, y0 + 3, x1 - 12, y1 - 3, "#16161c", r=3, bevel=False)
    scene(a, x0 + 6, y0 + 6, x1 - 15, y1 - 6, kind)
    for i in range(3):
        a.button(x1 - 6, y0 + 7 + i * 6, "#c8c0a8", 1)
    a.grille(x1 - 9, y1 - 14, x1 - 3, y1 - 5, drk(body, 0.3))
    a.line([(x0 + 18, y0), (x0 + 12, y0 - 8)], "#a0a0a8")
    a.line([(x0 + 22, y0), (x0 + 28, y0 - 9)], "#a0a0a8")


def software(a, title, stripe="#e02060", kind="osd", label="#f0f0f0", tcol="#000fc0",
             icon=None):
    crt_tv(a, 6, 14, 66, 66, kind)
    if icon:
        icon(a)
    tape(a, 62, 46, 116, 76, label, stripe, title, tcol)


def ic_pico(a):
    a.rect(12, 20, 51, 59, "#000000")
    for i, c in enumerate(["#ff004d", "#ffa300", "#ffec27", "#00e436", "#29adff", "#83769c",
                           "#ff77a8", "#ffccaa"]):
        a.rect(14 + i * 4 + 1, 48, 16 + i * 4 + 1, 52, c)
    a.text(16, 26, "PICO", "#ffec27")
    a.text(16, 34, "8", "#ff004d")
    a.rect(26, 40, 28, 42, "#29adff")


def ic_tic(a):
    a.rect(12, 20, 51, 59, "#1a1c2c")
    for i, c in enumerate(["#b13e53", "#ef7d57", "#ffcd75", "#a7f070", "#38b764", "#41a6f6",
                           "#5d275d", "#f4f4f4"]):
        a.rect(14 + i * 4 + 1, 50, 16 + i * 4 + 1, 54, c)
    a.text(16, 26, "TIC-80", "#f4f4f4")


def ic_doom(a):
    a.rect(12, 20, 51, 59, "#3a0a00")
    for y in range(36, 60):
        a.hl(12, 51, y, mixc("#8a2a10", "#200500", (y - 36) / 24))
    a.text(18, 26, "DOOM", "#f04010")
    a.rect(28, 44, 34, 58, "#5a5a5a")
    a.rect(30, 40, 32, 44, "#e0b080")


def ic_quake(a):
    a.rect(12, 20, 51, 59, "#2a1e14")
    a.ellipse(22, 26, 42, 46, "#6a5a40", "#1a1008")
    a.ellipse(26, 30, 38, 42, "#2a1e14")
    a.rect(31, 40, 33, 54, "#6a5a40")
    a.text(18, 52, "QUAKE", "#a08a60")


def ic_scumm(a):
    a.rect(12, 20, 51, 59, "#102040")
    a.ellipse(30, 22, 42, 32, "#f0f0c0")
    a.rect(12, 44, 51, 59, "#205030")
    a.rect(18, 36, 22, 44, "#0a0a10")
    a.text(14, 50, "SCUMM", "#f0e060")


def ic_openbor(a):
    a.rect(12, 20, 51, 59, "#301020")
    a.rect(12, 50, 51, 59, "#503040")
    a.rect(20, 36, 24, 50, "#f0c0a0")
    a.rect(34, 38, 38, 50, "#40a0ff")
    a.text(14, 24, "BEAT EM", "#ffe040")


def ic_rpg(a):
    a.rect(12, 20, 51, 59, "#103010")
    a.rect(12, 46, 51, 59, "#000fc0")
    a.d.rectangle([13, 47, 50, 58], outline="#f0f0f0")
    a.text(15, 49, "HP 99", "#f0f0f0")
    a.rect(28, 32, 32, 40, "#f0c040")
    a.rect(29, 30, 31, 32, "#f0d0b0")


def ic_ports(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    a.text(14, 24, "PORTS", "#f0f0f0")
    for i, c in enumerate(["#e02020", "#f0c020", "#20b040", "#20b0e0"]):
        a.rect(16 + i * 8, 36, 21 + i * 8, 41, c)
    a.text(14, 48, "LOAD", "#f0f0f0")


def ic_heart(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    pts = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
    for r, row in enumerate(pts):
        for c, v in enumerate(row):
            if v == "#":
                a.rect(18 + c * 4, 26 + r * 4, 21 + c * 4, 29 + r * 4, "#ff3060")


def ic_clock(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    a.ellipse(20, 24, 44, 48, "#f0f0f0", "#202040")
    a.ellipse(22, 26, 42, 46, "#000fc0")
    a.line([(32, 36), (32, 29)], "#f0f0f0")
    a.line([(32, 36), (37, 39)], "#f0f0f0")
    a.text(18, 51, "RECENT", "#f0f0f0")


def ic_all(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    for i in range(4):
        a.blk(16 + i * 2, 24 + i * 7, 46 - i * 2, 29 + i * 7, ["#e02020", "#f0c020", "#20b040", "#20b0e0"][i])
    a.text(22, 53, "ALL", "#f0f0f0")


def ic_star(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    pts = ["...#...", "...#...", "#######", ".#####.", "..###..", ".##.##.", "#.....#"]
    for r, row in enumerate(pts):
        for c, v in enumerate(row):
            if v == "#":
                a.rect(18 + c * 4, 24 + r * 4, 21 + c * 4, 27 + r * 4, "#ffe040")


def ic_music(a):
    a.rect(12, 20, 51, 59, "#200040")
    for i in range(8):
        hgt = [8, 14, 20, 12, 24, 16, 10, 18][i]
        a.rect(15 + i * 4, 56 - hgt, 17 + i * 4, 56, mixc("#40e0ff", "#ff40c0", i / 7))


def ic_gear(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    cx, cy = 32, 38
    for k in range(8):
        ang = k * math.pi / 4
        a.rect(int(cx + math.cos(ang) * 11) - 2, int(cy + math.sin(ang) * 11) - 2,
               int(cx + math.cos(ang) * 11) + 2, int(cy + math.sin(ang) * 11) + 2, "#f0f0f0")
    a.ellipse(cx - 10, cy - 10, cx + 10, cy + 10, "#f0f0f0")
    a.ellipse(cx - 4, cy - 4, cx + 4, cy + 4, "#000fc0")


def ic_solarus(a):
    a.rect(12, 20, 51, 59, "#205020")
    a.ellipse(24, 26, 40, 42, "#ffd040", "#c08010")
    a.text(16, 50, "SOLARUS", "#f0f0f0")


def ic_java(a):
    a.rect(12, 20, 51, 59, "#2a2a30")
    a.blk(24, 34, 40, 50, "#f0f0f0", r=2)
    a.blk(40, 38, 44, 44, "#f0f0f0", r=1)
    for i in range(3):
        a.line([(28 + i * 4, 30), (30 + i * 4, 24)], "#e08040")
    a.text(18, 52, "J2ME", "#e08040")


def ic_cave(a):
    a.rect(12, 20, 51, 59, "#1a1028")
    a.rect(12, 48, 51, 59, "#5a3a2a")
    a.rect(28, 38, 33, 47, "#f0f0f0")
    a.rect(28, 36, 33, 38, "#c02020")
    a.text(16, 24, "CAVE", "#f0f0f0")


def ic_vn(a):
    a.rect(12, 20, 51, 59, "#402060")
    a.ellipse(24, 24, 40, 40, "#f0d0c0")
    a.rect(14, 44, 49, 57, "#000fc0")
    a.text(16, 47, "TEXT..", "#f0f0f0")


def ic_wasm(a):
    a.rect(12, 20, 51, 59, "#071821")
    a.text(16, 26, "WASM4", "#86c06c")
    a.rect(24, 36, 40, 52, "#306850")
    a.rect(28, 40, 36, 48, "#e0f8cf")


def ic_retroarch(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    pts = ["..#...#..", "...#.#...", "..#####..", ".##.#.##.", "#########", "#.#####.#",
           "#.#...#.#", "...##.##."]
    for r, row in enumerate(pts):
        for c, v in enumerate(row):
            if v == "#":
                a.rect(14 + c * 4, 24 + r * 4, 17 + c * 4, 27 + r * 4, "#f0f0f0")


def ic_uzebox(a):
    a.rect(12, 20, 51, 59, "#100820")
    a.text(16, 26, "UZEBOX", "#f070ff")
    a.rect(24, 38, 40, 50, "#3060ff")


def ic_palm(a):
    a.rect(12, 20, 51, 59, "#9aa88a")
    a.text(16, 26, "PALM", "#202818")
    a.rect(18, 36, 46, 52, "#808c70")


def ic_easy(a):
    ic_rpg(a)


def ic_video(a):
    a.rect(12, 20, 51, 59, "#000fc0")
    a.poly([(26, 28), (26, 50), (42, 39)], "#f0f0f0")
    a.text(16, 53, "PLAY", "#f0f0f0")


def ic_love(a):
    a.rect(12, 20, 51, 59, "#e04080")
    a.ellipse(20, 26, 44, 50, "#40a0e0", "#202040")
    a.text(18, 34, "LOVE", "#f0f0f0")


def tools(a):
    vcr_deck(a, "SETUP", "#40ff70")


def videos(a):
    vcr_deck(a, "PLAY", "#ffd040")


def soft(title, stripe, icon, label="#f0f0f0", tcol="#000fc0"):
    return lambda a: software(a, title, stripe, "osd", label, tcol, icon)


ART = {
    # Nintendo
    "nes": nes, "famicom": famicom, "fds": fds, "snes": snes,
    "sfc": lambda a: snes(a, jp=True), "satellaview": satellaview, "sufami": sufami,
    "snesmsu1": snes_msu, "snes-msu1": snes_msu, "n64": n64, "gb": gb, "gbc": gbc,
    "sgb": lambda a: snes(a, jp=True, extra=lambda b: b.cart(98, 26, 114, 46, "#c8c4bc", "#e8e0d0", "#a02860", ridges=False)),
    "gba": gba, "nds": nds, "virtualboy": virtualboy, "vb": virtualboy,
    "gameandwatch": gameandwatch, "gw": gameandwatch, "pokemini": pokemini,
    "megaduck": megaduck, "arduboy": arduboy, "supervision": supervision,
    # Sega
    "genesis": genesis, "megadrive": megadrive, "megadrive-japan": megadrive,
    "sega32x": sega32x, "segacd": segacd, "megacd": megacd, "mastersystem": mastersystem,
    "sg-1000": sg1000, "sg1000": sg1000, "gamegear": gamegear, "saturn": saturn,
    "saturnjp": lambda a: saturn(a, jp=True), "dreamcast": dreamcast, "naomi": naomi,
    "atomiswave": atomiswave, "vmu": vmu, "model2": model2,
    # Sony
    "psx": psx, "psp": psp, "pspminis": pspminis, "ps2": ps2,
    # NEC
    "pcengine": pcengine, "tg16": tg16, "supergrafx": supergrafx, "pcenginecd": pcenginecd,
    "tg16cd": tg16cd, "tg-cd": tg16cd, "pcfx": pcfx,
    # SNK / arcade
    "neogeo": neogeo, "neogeocd": neogeocd, "ngp": ngp, "ngpc": lambda a: ngp(a, True),
    "arcade": arcade, "mame": mame, "mame2003": mame, "mame2010": mame, "mame-advmame": mame,
    "fbneo": fbneo, "fba": fbneo, "cps1": cps1, "cps2": cps2, "cps3": cps3, "daphne": daphne,
    # Atari & classic
    "atari2600": atari2600, "atari5200": atari5200, "atari7800": atari7800,
    "atari800": atari800, "atarist": atarist, "atarilynx": lynx, "lynx": lynx,
    "atarijaguar": jaguar, "jaguar": jaguar, "intellivision": intellivision,
    "colecovision": colecovision, "coleco": colecovision, "odyssey2": odyssey2,
    "videopac": odyssey2, "channelf": channelf, "vectrex": vectrex, "3do": threedo,
    "cdi": cdi, "amigacd32": cd32, "cd32": cd32, "wonderswan": wonderswan,
    "wonderswancolor": lambda a: wonderswan(a, True),
    # computers
    "c64": c64, "c16": c16, "c128": c128, "vic20": vic20, "amiga": amiga,
    "amstradcpc": amstradcpc, "gx4000": gx4000, "zxspectrum": zxspectrum, "zx81": zx81,
    "msx": msx, "msx1": msx, "msx2": msx2, "msxturbor": msxturbor, "apple2": apple2,
    "pc": dos, "dos": dos, "pc98": pc98, "pc88": pc88, "x68000": x68000, "x1": x1,
    "coco": coco, "trs-80": coco, "ti99": ti99, "thomson": thomson, "bbcmicro": bbcmicro,
    "samcoupe": samcoupe, "oric": oric,
    # engines & ports
    "pico8": soft("PICO-8", "#ff004d", ic_pico), "pico-8": soft("PICO-8", "#ff004d", ic_pico),
    "tic80": soft("TIC-80", "#41a6f6", ic_tic), "doom": soft("DOOM", "#c02010", ic_doom),
    "prboom": soft("DOOM", "#c02010", ic_doom), "quake": soft("QUAKE", "#6a5a40", ic_quake),
    "scummvm": soft("SCUMMVM", "#20a040", ic_scumm), "openbor": soft("OPENBOR", "#e04080", ic_openbor),
    "easyrpg": soft("EASYRPG", "#f0c040", ic_rpg), "ports": soft("PORTS", "#20b0e0", ic_ports),
    "solarus": soft("SOLARUS", "#ffd040", ic_solarus), "j2me": soft("J2ME", "#e08040", ic_java),
    "cavestory": soft("CAVE STORY", "#c02020", ic_cave), "onscripter": soft("ONSCRIPTER", "#a040c0", ic_vn),
    "wasm4": soft("WASM-4", "#86c06c", ic_wasm), "uzebox": soft("UZEBOX", "#f070ff", ic_uzebox),
    "palm": soft("PALM OS", "#808c70", ic_palm), "love": soft("LOVE", "#e04080", ic_love),
    "lowresnx": soft("LOWRES NX", "#40c0ff", ic_ports), "retroarch": soft("RETROARCH", "#808090", ic_retroarch),
    # collections & tools
    "auto-favorites": soft("FAVORITES", "#ff3060", ic_heart), "favorites": soft("FAVORITES", "#ff3060", ic_heart),
    "auto-lastplayed": soft("RECENT", "#40c0ff", ic_clock), "recent": soft("RECENT", "#40c0ff", ic_clock),
    "auto-allgames": soft("ALL GAMES", "#f0c020", ic_all), "all": soft("ALL GAMES", "#f0c020", ic_all),
    "custom-collections": soft("COLLECTION", "#ffe040", ic_star), "collections": soft("COLLECTION", "#ffe040", ic_star),
    "bgm": soft("MUSIC", "#a040ff", ic_music), "music": soft("MUSIC", "#a040ff", ic_music),
    "tools": tools, "options": tools, "settings": tools, "ark": tools,
    "videos": videos, "mplayer": videos, "movies": videos, "mvideos": videos,
    "default": soft("VHS TAPE", "#e02060", ic_video),
}


def render(key, scale=3):
    a = Art(W, H)
    ART.get(key, ART["default"])(a)
    return a.render(scale)


if __name__ == "__main__":
    import sys
    from PIL import Image
    keys = sys.argv[2:] or list(ART)
    cols = 6
    tiles = [render(k, 2) for k in keys]
    tw, th = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * tw, rows * (th + 14)), (0, 15, 192, 255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, (k, t) in enumerate(zip(keys, tiles)):
        x, y = (i % cols) * tw, (i // cols) * (th + 14)
        sheet.alpha_composite(t, (x, y))
        d.text((x + 4, y + th), k, fill=(255, 255, 255))
    sheet.save(sys.argv[1])
    print(len(keys), "systems")
