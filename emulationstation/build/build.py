#!/usr/bin/env python3
"""Builds the Volta EmulationStation theme for the R36S (ArkOS, 640x480).

Renders all artwork with headless Chromium and writes every XML file from the
same layout constants, so art and element positions never drift apart.

usage:
  ABN_LOGOS=/path/to/art-book-next-es-de/_inc/systems/logos python3 build.py
"""
import html
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

from palettes import PALETTES
from systems import SYSTEMS

HERE = os.path.dirname(os.path.abspath(__file__))
THEME = os.path.normpath(os.path.join(HERE, "..", "es-theme-volta"))
FONTS = os.path.join(THEME, "_fonts")
ART = os.path.join(THEME, "_art")
INC = os.path.join(THEME, "_inc")
BOOT = os.path.join(THEME, "_boot")
ABN_LOGOS = os.environ.get("ABN_LOGOS", "")
ONLY = set(filter(None, os.environ.get("ONLY", "").split(",")))  # e.g. ONLY=xml,ui

W, H = 640, 480

# ---------------------------------------------------------------------------
# Layout (pixels on the 640x480 R36S screen)
# ---------------------------------------------------------------------------
# ArkOS draws the clock + battery inside our status capsule, top right.
STATUS = (474, 8, 154, 32)
BACK_BTN = (12, 8, 32, 32)
HEADER_LOGO = (54, 24, 200, 26)      # x, centre-y, max w, max h
HELP_Y = 456

# Game list: left half = list, right top 2/3 = art, right bottom 1/3 = info.
LIST = (12, 48, 306, 398)
ART_WELL = (326, 48, 302, 262)
INFO = (326, 318, 302, 128)
LIST_INNER = (LIST[0] + 6, LIST[1] + 10, LIST[2] - 12, LIST[3] - 20)
ART_PAD = 10

# System view
H_CARD = (196, 102, 248, 196)
V_COLUMN = (12, 48, 228, 398)
V_CARD = (248, 48, 380, 398)
W_CARD = (12, 48, 380, 398)
W_TRACK = (400, 48, 228, 398)
CAROUSEL_SLOTS_V = 7
DESC_SPACING = 1.25

FONT_SIZES = {
    # name: list font (px), list line spacing, description font (px), menu font (px)
    "small":  dict(list=16, spacing=1.75, desc=14, descLines=4, menu=17, menuTitle=24, menuSmall=13, sys=23),
    "medium": dict(list=19, spacing=1.6, desc=16, descLines=4, menu=20, menuTitle=27, menuSmall=15, sys=26),
    "large":  dict(list=23, spacing=1.5, desc=19, descLines=3, menu=23, menuTitle=30, menuSmall=17, sys=29),
}


# ArkOS' EmulationStation treats screens under 700px as "small" and enlarges
# every font by 1.31x (Font::Font). Sizes below are the pixel sizes we want on
# screen; fsz() pre-divides so the result lands on that size.
FONT_SCALE = 1.31


def fsz(px):
    n = max(1, round(px / FONT_SCALE))
    return f"{(n + 0.5) / H:.5f}"


def eff_px(px):
    """Pixel size ES actually renders for a design size."""
    return int(round(px / FONT_SCALE) * FONT_SCALE)


def glyph_height(px, font="Urbanist-Medium.ttf"):
    """Tallest bitmap among glyphs 32..127, as ES measures it (FreeType)."""
    try:
        import freetype
    except ImportError:
        return round(px * 0.97)
    face = freetype.Face(os.path.join(FONTS, font))
    face.set_pixel_sizes(0, px)
    best = 0
    for i in range(32, 128):
        face.load_char(chr(i), freetype.FT_LOAD_RENDER)
        best = max(best, face.glyph.bitmap.rows)
    return best


def nx(v):
    return f"{v / W:.5f}".rstrip("0").rstrip(".") if v else "0"


def ny(v):
    return f"{v / H:.5f}".rstrip("0").rstrip(".") if v else "0"


def pair_x(x, y):
    return f"{nx(x)} {ny(y)}"


def want(section):
    return not ONLY or section in ONLY


def css_hex(v):
    """'F4F4F6' or 'F4F4F6B0' -> CSS colour."""
    if v.startswith("#") or v.startswith("rgb"):
        return v
    if len(v) == 8:
        r, g, b, a = (int(v[i:i + 2], 16) for i in (0, 2, 4, 6))
        return f"rgba({r},{g},{b},{a / 255:.3f})"
    return "#" + v


def xml_hex(v):
    """CSS '#aabbcc' or 'AABBCC' -> ES 'AABBCC'."""
    return v.lstrip("#").upper()


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------
GRAIN = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
    "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 1.2 0'/></filter>"
    "<rect width='160' height='160' filter='url(%23n)'/></svg>"
)


def base_css(p, w, h):
    f = FONTS
    return f"""
@font-face {{ font-family: U; src: url('file://{f}/Urbanist-Medium.ttf'); font-weight: 500; }}
@font-face {{ font-family: U; src: url('file://{f}/Urbanist-SemiBold.ttf'); font-weight: 600; }}
@font-face {{ font-family: D; src: url('file://{f}/Doto-Black.ttf'); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {w}px; height: {h}px; overflow: hidden; background: transparent; }}
body {{ position: relative; font-family: U; font-weight: 500; -webkit-font-smoothing: antialiased; }}
.a {{ position: absolute; }}
.page {{ position: absolute; inset: 0;
  background:
    radial-gradient(70% 55% at 18% -5%, {p['glowA']}, transparent 70%),
    radial-gradient(60% 50% at 100% 105%, {p['glowB']}, transparent 70%),
    linear-gradient(180deg, {p['bg2']}, {p['bg']}); }}
.dots {{ position: absolute; inset: 0;
  background-image: radial-gradient(circle, {p['dot']} 0.9px, transparent 1.25px);
  background-size: 12px 12px; background-position: 4px 2px; }}
.grain {{ position: absolute; inset: 0; opacity: {0.10 if p['mode'] == 'dark' else 0.07};
  mix-blend-mode: overlay; background-image: url("{GRAIN}"); }}
.panel {{ position: absolute; border-radius: 24px;
  background: linear-gradient(165deg, {p['panelA']} 0%, {p['panelB']} 85%);
  box-shadow: 0 12px 26px {p['shadow']}, inset 0 1px 0 {p['panelLine']}, inset 0 0 0 1px {p['panelLine']}; }}
.panel::before {{ content: ''; position: absolute; inset: 0; border-radius: inherit;
  background: radial-gradient(80% 60% at 30% 0%, rgba(255,255,255,{p.get('panelGlow', 0.06 if p['mode'] == 'dark' else 0.5)}), transparent 70%); }}
.well {{ position: absolute; border-radius: 24px; overflow: hidden; background: {p['well']};
  box-shadow: inset 0 2px 14px rgba(0,0,0,{0.55 if p['mode'] == 'dark' else 0.10}), inset 0 0 0 1px {p['panelLine']}; }}
.card {{ position: absolute; overflow: hidden; border-radius: 34px;
  background:
    radial-gradient(75% 85% at 10% 8%, {p['cardA']} 0%, transparent 62%),
    radial-gradient(85% 95% at 98% 102%, {p['cardC']} 0%, transparent 70%),
    linear-gradient(140deg, {p['cardA']} 0%, {p['cardB']} 52%, {p['cardC']} 100%);
  box-shadow: 0 18px 38px {p['shadow']}, inset 0 0 30px 3px {p['cardEdge']},
              inset 0 1px 0 rgba(255,255,255,0.35); }}
.card::after {{ content: ''; position: absolute; inset: 0; opacity: 0.12; mix-blend-mode: overlay;
  background-image: url("{GRAIN}"); }}
.status {{ position: absolute; border-radius: 16px; background: {p['status']};
  box-shadow: 0 4px 12px {p['shadow']}, inset 0 0 0 1px {p['panelLine']}; }}
.rbtn {{ position: absolute; border-radius: 50%; background: {p['status']};
  box-shadow: 0 4px 12px {p['shadow']}, inset 0 0 0 1px {p['panelLine']};
  display: flex; align-items: center; justify-content: center; }}
.pill {{ position: absolute; border-radius: 999px; }}
"""


def page_html(p, body, w=W, h=H, extra_css=""):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{base_css(p, w, h)}{extra_css}"
            f"</style></head><body>{body}</body></html>")


def box(x, y, w, h):
    return f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;"


def tick_ring(cx, cy, r, n, length, color, major_every=0, major_len=0, accent=None,
              accent_color=None, width=1.4, start=0.0, sweep=360.0):
    """SVG tick ring like the 'Energy Status' gauge in the reference."""
    parts = []
    for i in range(n):
        ang = math.radians(start + sweep * i / n - 90)
        ln = major_len if major_every and i % major_every == 0 else length
        col = color
        sw = width
        if accent is not None and i in accent:
            col, ln, sw = accent_color, major_len or length * 1.8, width * 1.6
        x1, y1 = cx + math.cos(ang) * r, cy + math.sin(ang) * r
        x2, y2 = cx + math.cos(ang) * (r - ln), cy + math.sin(ang) * (r - ln)
        parts.append(f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' "
                     f"stroke='{col}' stroke-width='{sw}' stroke-linecap='round'/>")
    return "".join(parts)


def arc_path(cx, cy, r, a0, a1):
    a0r, a1r = math.radians(a0 - 90), math.radians(a1 - 90)
    x0, y0 = cx + r * math.cos(a0r), cy + r * math.sin(a0r)
    x1, y1 = cx + r * math.cos(a1r), cy + r * math.sin(a1r)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.2f},{y0:.2f} A{r},{r} 0 {large} 1 {x1:.2f},{y1:.2f}"


def svg_layer(inner, w=W, h=H):
    return (f"<svg class='a' style='left:0;top:0' width='{w}' height='{h}' "
            f"xmlns='http://www.w3.org/2000/svg'>{inner}</svg>")


def ink(p, alpha):
    """Neutral ink colour for decorations, works on dark and light pages."""
    base = "255,255,255" if p["mode"] == "dark" else "0,0,0"
    return f"rgba({base},{alpha})"


# --- shared chrome ---------------------------------------------------------
GRID_GLYPH = ("<svg width='14' height='14' viewBox='0 0 14 14'>"
              "<rect x='0.5' y='0.5' width='5.5' height='5.5' rx='1.6' fill='{c}'/>"
              "<rect x='8' y='0.5' width='5.5' height='5.5' rx='1.6' fill='{c}'/>"
              "<rect x='0.5' y='8' width='5.5' height='5.5' rx='1.6' fill='{c}'/>"
              "<rect x='8' y='8' width='5.5' height='5.5' rx='2.75' fill='{a}'/></svg>")
BACK_GLYPH = ("<svg width='16' height='16' viewBox='0 0 16 16'><path d='M13 8H3.5M7.5 3.5 3 8l4.5 4.5' "
              "fill='none' stroke='{c}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>")


def chrome(p, glyph):
    x, y, w, h = STATUS
    bx, by, bw, bh = BACK_BTN
    btn_ink = css_hex(p["text"]) if p.get("bgText") == p["text"] else css_hex(p["text"])
    return (
        "<div class='page'></div><div class='dots'></div>"
        f"<div class='rbtn' style='{box(bx, by, bw, bh)}'>"
        f"{glyph.format(c=btn_ink, a=css_hex(p['accent']))}</div>"
        f"<div class='status' style='{box(x, y, w, h)}'></div>"
        # thin divider between the clock and the battery inside the capsule
        f"<div class='a' style='{box(x + 82, y + 9, 1, h - 18)}background:{ink(p, 0.12) if p['status'] != '#111114' else 'rgba(255,255,255,0.12)'}'></div>"
    )


def page_end():
    return "<div class='grain'></div>"


# --- system views -----------------------------------------------------------
def sys_card_deco(p, card):
    """Decorations that live on the big per-system card (vertical / wheel)."""
    x, y, w, h = card
    cx, cy = x + w / 2, y + 172
    deco = tick_ring(cx, cy, 128, 96, 5, "rgba(255,255,255,0.20)" if p["mode"] == "dark" else "rgba(0,0,0,0.13)",
                     major_every=8, major_len=10)
    deco += (f"<path d='{arc_path(cx, cy, 138, 205, 320)}' fill='none' stroke='{css_hex(p['accent'])}' "
             f"stroke-width='3' stroke-linecap='round' opacity='0.9'/>")
    # count pill (systemInfo sits on top of it)
    px, py, pw, ph = sys_info_pill(card)
    pill = (f"<div class='pill' style='{box(px, py, pw, ph)}background:{ink(p, 0.16) if p['mode'] == 'dark' else 'rgba(255,255,255,0.65)'};"
            f"box-shadow: inset 0 0 0 1px {ink(p, 0.10)}'></div>")
    return svg_layer(deco), pill


def sys_info_pill(card):
    x, y, w, h = card
    return (x + w - 24 - 168, y + h - 24 - 30, 168, 30)


def system_page(p, mode):
    body = chrome(p, GRID_GLYPH)
    title_col = css_hex(p["bgText"])
    body += (f"<div class='a' style='left:54px;top:12px;font:600 19px U;color:{title_col};letter-spacing:0.2px'>"
             f"Systems</div>")
    if mode == "horizontal":
        x, y, w, h = H_CARD
        cx, cy = x + w / 2, y + h / 2
        ring = tick_ring(cx, cy, 212, 140, 6, ink(p, 0.10), major_every=10, major_len=12, width=1.3)
        body += svg_layer(ring)
        body += f"<div class='card' style='{box(x, y, w, h)}border-radius:46px'></div>"
        # count pill under the name
        px, py, pw, ph = H_PILL
        body += (f"<div class='pill' style='{box(px, py, pw, ph)}background:{p['status']};"
                 f"box-shadow:0 4px 12px {p['shadow']}, inset 0 0 0 1px {p['panelLine']}'></div>")
        # small accent dot either side of the pill
        body += (f"<div class='pill' style='{box(px + 14, py + ph / 2 - 3, 6, 6)}background:{css_hex(p['accent'])}'></div>")
    elif mode == "vertical":
        x, y, w, h = V_COLUMN
        body += f"<div class='panel' style='{box(x, y, w, h)}'></div>"
        slot = h / CAROUSEL_SLOTS_V
        sy = y + slot * (CAROUSEL_SLOTS_V // 2)
        body += (f"<div class='a' style='{box(x + 8, sy + 3, w - 16, slot - 6)}border-radius:18px;"
                 f"background:{ink(p, 0.08) if p['mode'] == 'dark' else 'rgba(0,0,0,0.05)'};"
                 f"box-shadow: inset 0 0 0 1px {ink(p, 0.10)}'></div>")
        body += (f"<div class='pill' style='{box(x + 14, sy + slot / 2 - 11, 4, 22)}background:{css_hex(p['accent'])};"
                 f"box-shadow:0 0 10px {css_hex(p['accent'])}'></div>")
        cx_, cy_, cw, ch = V_CARD
        body += f"<div class='card' style='{box(cx_, cy_, cw, ch)}'></div>"
        deco, pill = sys_card_deco(p, V_CARD)
        body += deco + pill
    elif mode == "wheel":
        cx_, cy_, cw, ch = W_CARD
        body += f"<div class='card' style='{box(cx_, cy_, cw, ch)}'></div>"
        deco, pill = sys_card_deco(p, W_CARD)
        body += deco + pill
        tx, ty, tw, th = W_TRACK
        # curved guide track for the wheel + selection notch
        cxw, cyw = tx + tw + 230, ty + th / 2
        track = (f"<path d='{arc_path(cxw, cyw, 290, 228, 312)}' fill='none' stroke='{ink(p, 0.10)}' stroke-width='1.2'/>"
                 + tick_ring(cxw, cyw, 300, 120, 5, ink(p, 0.10), start=230, sweep=80))
        body += svg_layer(track)
        body += (f"<div class='a' style='{box(tx + 6, ty + th / 2 - 30, tw - 6, 60)}border-radius:20px;"
                 f"background:{ink(p, 0.07) if p['mode'] == 'dark' else 'rgba(255,255,255,0.55)'};"
                 f"box-shadow: inset 0 0 0 1px {ink(p, 0.10)}'></div>")
        body += (f"<div class='pill' style='{box(tx + tw - 8, ty + th / 2 - 12, 4, 24)}background:{css_hex(p['accent'])};"
                 f"box-shadow:0 0 10px {css_hex(p['accent'])}'></div>")
    return page_html(p, body + page_end())


H_PILL = (200, 380, 240, 28)


# --- game list --------------------------------------------------------------
def gamelist_page(p, placeholder=True):
    body = chrome(p, BACK_GLYPH)
    x, y, w, h = LIST
    body += f"<div class='panel' style='{box(x, y, w, h)}'></div>"
    x, y, w, h = ART_WELL
    body += f"<div class='well' style='{box(x, y, w, h)}'><div class='dots' style='opacity:0.8'></div></div>"
    # corner ticks in the art well (viewfinder)
    t = []
    c = ink(p, 0.22)
    for (cx, cy, dx, dy) in ((x + 12, y + 12, 1, 1), (x + w - 12, y + 12, -1, 1),
                             (x + 12, y + h - 12, 1, -1), (x + w - 12, y + h - 12, -1, -1)):
        t.append(f"<path d='M{cx},{cy + dy * 10} L{cx},{cy} L{cx + dx * 10},{cy}' fill='none' stroke='{c}' "
                 f"stroke-width='1.5' stroke-linecap='round'/>")
    if placeholder:
        # shown when a game has no box art (ES skips the default image for the first game)
        t.append(cart_glyph(p, x + w / 2, y + h / 2 - 14, 6, 1.9, css_hex(p["text"]), 0.28))
    body += svg_layer("".join(t))
    if placeholder:
        body += (f"<div class='a' style='left:{x}px;width:{w}px;top:{y + h / 2 + 28}px;text-align:center;"
                 f"font:500 12px U;letter-spacing:0.4px;color:{css_hex(p['dim'])};opacity:0.8'>No artwork</div>")
    x, y, w, h = INFO
    body += f"<div class='card' style='{box(x, y, w, h)}border-radius:26px'></div>"
    # divider under the rating row
    body += (f"<div class='a' style='{box(x + 16, y + 34, w - 32, 1)}background:"
             f"{'rgba(255,255,255,0.18)' if p['mode'] == 'dark' or p['name'] == 'citrine-pop' else 'rgba(0,0,0,0.10)'}'></div>")
    return page_html(p, body + page_end())


CART = [
        "..#########..",
        ".###########.",
        "##.........##",
        "##.#######.##",
        "##.#.....#.##",
        "##.#.....#.##",
        "##.#######.##",
        "##.........##",
        "##..##..##.##",
        "##.........##",
        "#############",
        ".#.#.#.#.#.#.",
]


def cart_glyph(p, cx, cy, cell, dot, ink_c, alpha=0.55):
    """Dot-matrix cartridge icon centred on (cx, cy)."""
    gw, gh = len(CART[0]) * cell, len(CART) * cell
    ox, oy = cx - gw / 2, cy - gh / 2
    dots = ""
    for r, row in enumerate(CART):
        for c, ch in enumerate(row):
            if ch == "#":
                accent = r == 8 and c in (4, 5)
                col = css_hex(p["accent"]) if accent else ink_c
                dots += (f"<circle cx='{ox + c * cell + cell / 2:.1f}' cy='{oy + r * cell + cell / 2:.1f}' r='{dot}' "
                         f"fill='{col}' opacity='{1 if accent else alpha}'/>")
    return dots


def noart_page(p, w, h):
    ink_c = css_hex(p["text"])
    dots = cart_glyph(p, w / 2, h * 0.30 + 10, 12, 3.6, ink_c)
    body = (f"<div class='a' style='{box(0, 0, w, h)}border-radius:40px;"
            f"background:linear-gradient(165deg,{p['panelA']},{p['panelB']});"
            f"box-shadow: inset 0 0 0 2px {p['panelLine']}'></div>"
            f"<div class='dots' style='opacity:0.7;border-radius:40px;background-size:20px 20px'></div>"
            + svg_layer(dots, w, h) +
            f"<div class='a' style='left:0;width:{w}px;top:{h * 0.62:.0f}px;text-align:center;font:60px D;"
            f"color:{ink_c};letter-spacing:4px'>NO ART</div>"
            f"<div class='a' style='left:0;width:{w}px;top:{h * 0.80:.0f}px;text-align:center;font:500 26px U;"
            f"color:{css_hex(p['dim'])}'>Scrape your games to add box art</div>")
    return page_html(p, body, w, h)


def selector_page(p, w, h):
    body = (f"<div class='a' style='{box(0, 0, w, h)}border-radius:{min(14, h / 2):.0f}px;"
            f"background:linear-gradient(100deg,{p['sel1']},{p['sel2']});"
            f"box-shadow: inset 0 1px 0 rgba(255,255,255,0.45), inset 0 -1px 0 rgba(0,0,0,0.12)'></div>"
            f"<div class='a' style='{box(0, 0, w, h)}border-radius:{min(14, h / 2):.0f}px;opacity:0.18;"
            f"background-image:radial-gradient(circle, rgba(0,0,0,0.6) 0.9px, transparent 1.3px);"
            f"background-size:7px 7px;-webkit-mask-image:linear-gradient(90deg,transparent 45%,#000)'></div>")
    return page_html(p, body, w, h)


# --- menu pieces --------------------------------------------------------------
def menu_bg_page(p):
    # 96x96 nine-patch, corner 32: 14px of soft shadow, then an 18px radius panel
    glow = css_hex(p["accent"]) if p["name"] != "citrine-pop" else "#F2D21B"
    body = (f"<div class='a' style='{box(14, 14, 68, 68)}border-radius:18px;"
            f"background:linear-gradient(180deg, color-mix(in srgb, {glow} {14 if p['mode'] == 'dark' or p['name'] == 'citrine-pop' else 10}%, {p['menuBg']}) 0px, {p['menuBg']} 52px);"
            f"box-shadow: 0 0 12px rgba(0,0,0,{0.6 if p['mode'] == 'dark' else 0.22}), inset 0 0 0 1px {p['menuLine']}'></div>")
    return page_html(p, body, 96, 96)


def switch_page(p, on):
    # ES multiplies this image by the menu text colour; dark schemes keep colour,
    # light schemes get a neutral (white) image that becomes the text colour.
    colored = p["mode"] == "dark" and p["name"] != "citrine-pop" or p["name"] == "citrine-pop"
    track_on = f"linear-gradient(100deg,{p['sel1']},{p['sel2']})" if colored else "#ffffff"
    knob_on = "#111" if colored and p["selText"] == "111111" else ("#fff" if colored else "#ffffff")
    if on:
        body = (f"<div class='pill' style='{box(4, 14, 120, 68)}background:{track_on}'></div>"
                f"<div class='pill' style='{box(60, 20, 56, 56)}background:{knob_on};"
                f"{'' if colored else 'box-shadow: inset 0 0 0 0 #000; opacity:1;'}'></div>")
        if not colored:
            # light schemes: knob is a cut-out ring so it reads on the solid track
            body = (f"<svg width='128' height='96' xmlns='http://www.w3.org/2000/svg'>"
                    f"<defs><mask id='m'><rect x='4' y='14' width='120' height='68' rx='34' fill='#fff'/>"
                    f"<circle cx='88' cy='48' r='24' fill='#000'/></mask></defs>"
                    f"<rect x='4' y='14' width='120' height='68' rx='34' fill='#fff' mask='url(#m)'/>"
                    f"<circle cx='88' cy='48' r='14' fill='#fff'/></svg>")
    else:
        body = (f"<div class='pill' style='{box(6, 16, 116, 64)}border:5px solid rgba(255,255,255,0.55)'></div>"
                f"<div class='pill' style='{box(20, 28, 40, 40)}background:rgba(255,255,255,0.7)'></div>")
    return page_html(p, body, 128, 96)


def knob_page(p):
    body = (f"<div class='pill' style='{box(8, 8, 48, 48)}background:{css_hex(p['accent']) if p['mode'] == 'dark' else '#ffffff'};"
            f"box-shadow:0 0 0 6px rgba(255,255,255,0.18)'></div>")
    return page_html(p, body, 64, 64)


def button_page(p, filled):
    # 48x48 nine-patch, corner 8 (ES hard-codes the button corner size)
    if filled:
        body = (f"<div class='a' style='{box(2, 2, 44, 44)}border-radius:10px;"
                f"background:linear-gradient(100deg,{p['sel1']},{p['sel2']})'></div>")
    else:
        body = (f"<div class='a' style='{box(2, 2, 44, 44)}border-radius:10px;"
                f"background:{ink(p, 0.06)};box-shadow: inset 0 0 0 2px {ink(p, 0.22)}'></div>")
    return page_html(p, body, 48, 48)


def textedit_page(p, active):
    edge = css_hex(p["accent"]) if active else ink(p, 0.25)
    body = (f"<div class='a' style='{box(2, 2, 44, 44)}border-radius:10px;background:{ink(p, 0.05)};"
            f"box-shadow: inset 0 0 0 2px {edge}'></div>")
    return page_html(p, body, 48, 48)


# --- shared white UI icons (tinted in XML) ----------------------------------
def star_svg(filled):
    pts = []
    for i in range(10):
        r = 46 if i % 2 == 0 else 19
        a = math.radians(-90 + i * 36)
        pts.append(f"{50 + r * math.cos(a):.2f},{52 + r * math.sin(a):.2f}")
    if filled:
        return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' width='100' height='100'>"
                f"<polygon points='{' '.join(pts)}' fill='#ffffff' stroke='#ffffff' stroke-width='8' stroke-linejoin='round'/></svg>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' width='100' height='100'>"
            f"<polygon points='{' '.join(pts)}' fill='none' stroke='#ffffff' stroke-width='7' stroke-linejoin='round'/></svg>")


def battery_svg(level, charging=False):
    # square canvas: ES draws battery textures in a square slot
    fill_w = {0: 0, 25: 6, 50: 12, 75: 18, 100: 24}[level]
    s = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40' width='40' height='40'>"
         "<rect x='3' y='12' width='31' height='16' rx='5' fill='none' stroke='#ffffff' stroke-width='2.2'/>"
         "<rect x='35.2' y='17' width='2.6' height='6' rx='1.2' fill='#ffffff'/>")
    if fill_w:
        s += f"<rect x='6.5' y='15.5' width='{fill_w}' height='9' rx='2.4' fill='#ffffff'/>"
    if charging:
        s = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40' width='40' height='40'>"
             "<rect x='3' y='12' width='31' height='16' rx='5' fill='none' stroke='#ffffff' stroke-width='2.2'/>"
             "<rect x='35.2' y='17' width='2.6' height='6' rx='1.2' fill='#ffffff'/>"
             "<path d='M21 13.5 13 21.2h5.6l-2 5.3 8-7.7H19z' fill='#ffffff'/>")
    if level == 0 and not charging:
        s += "<rect x='6.5' y='15.5' width='3' height='9' rx='1.2' fill='#ffffff'/>"
    return s + "</svg>"


# ---------------------------------------------------------------------------
# Boot splash (pure vector: ES renders it with nanosvg, so text -> paths)
# ---------------------------------------------------------------------------
def text_to_path(font_path, text, size, x, y, tracking=0.0, anchor="middle"):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen

    font = TTFont(font_path)
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = size / upm
    names = [cmap.get(ord(ch)) for ch in text]
    total = 0
    for i, n in enumerate(names):
        total += gs[n].width * scale + (tracking if i < len(names) - 1 else 0)
    cx = x - total / 2 if anchor == "middle" else x
    out = []
    for n in names:
        pen = SVGPathPen(gs)
        tp = TransformPen(pen, (scale, 0, 0, -scale, cx, y))
        gs[n].draw(tp)
        d = pen.getCommands()
        if d:
            out.append(d)
        cx += gs[n].width * scale + tracking
    return " ".join(out)


def splash_svg():
    """Square emblem: tick-ring gauge + dot-matrix VOLTA wordmark."""
    S = 512
    cx = cy = S / 2
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{S}' height='{S}' viewBox='0 0 {S} {S}'>"]
    # absolute coordinates: nanosvg (ES's SVG renderer) flattens bounding-box gradients
    parts.append(f"<defs><linearGradient id='g' gradientUnits='userSpaceOnUse' x1='{cx - 128}' y1='{cy - 128}' "
                 f"x2='{cx + 128}' y2='{cy + 128}'>"
                 "<stop offset='0' stop-color='#d697e2'/><stop offset='0.55' stop-color='#8b3db5'/>"
                 "<stop offset='1' stop-color='#5b1a7a'/></linearGradient></defs>")
    # outer ticks
    for i in range(120):
        a = math.radians(i * 3 - 90)
        major = i % 10 == 0
        r1, r2 = 236, 236 - (22 if major else 12)
        col = "#ffffff"
        op = 0.85 if major else 0.38
        w = 3 if major else 2
        if i in (52, 53, 54):
            col, op, w, r2 = "#F2D21B", 1, 4, 236 - 28
        parts.append(f"<line x1='{cx + math.cos(a) * r1:.2f}' y1='{cy + math.sin(a) * r1:.2f}' "
                     f"x2='{cx + math.cos(a) * r2:.2f}' y2='{cy + math.sin(a) * r2:.2f}' stroke='{col}' "
                     f"stroke-opacity='{op}' stroke-width='{w}' stroke-linecap='round'/>")
    # glossy squircle
    parts.append(f"<rect x='{cx - 128}' y='{cy - 128}' width='256' height='256' rx='76' fill='url(#g)'/>")
    parts.append(f"<rect x='{cx - 124}' y='{cy - 124}' width='248' height='248' rx='72' fill='none' "
                 f"stroke='#ffffff' stroke-opacity='0.35' stroke-width='3'/>")
    # dot-matrix 'V' made of circles + accent dot
    vpat = ["#.....#", "#.....#", ".#...#.", ".#...#.", "..#.#..", "..#.#..", "...#..."]
    cell = 18
    ox, oy = cx - 3 * cell, cy - 92
    for r, row in enumerate(vpat):
        for c, ch in enumerate(row):
            if ch == "#":
                tip = r == len(vpat) - 1
                parts.append(f"<circle cx='{ox + c * cell:.1f}' cy='{oy + r * cell:.1f}' r='{7.5 if tip else 6.5}' "
                             f"fill='{'#F2D21B' if tip else '#ffffff'}'/>")
    # wordmark, well clear of the V
    d = text_to_path(os.path.join(FONTS, "Urbanist-SemiBold.ttf"), "VOLTA", 40, cx, cy + 84, tracking=9)
    parts.append(f"<path d='{d}' fill='#ffffff'/>")
    parts.append("</svg>")
    return "".join(parts)


def boot_logo_page():
    p = dict(PALETTES[0][2])
    p["name"] = "volta-dark"
    svg = splash_svg()
    body = ("<div class='a' style='inset:0;background:#000'></div>"
            "<div class='a' style='inset:0;background:radial-gradient(45% 45% at 50% 44%, rgba(139,61,181,0.35), transparent 70%)'></div>"
            "<div class='dots' style='opacity:0.6'></div>"
            f"<div class='a' style='left:{(W - 300) / 2}px;top:46px;width:300px;height:300px'>"
            f"{svg.replace('<svg ', '<svg style=\"width:300px;height:300px\" ', 1)}</div>"
            "<div class='a' style='left:0;width:640px;top:378px;text-align:center;font:30px D;color:#fff;letter-spacing:3px'>"
            "R36S</div>"
            "<div class='a' style='left:0;width:640px;top:424px;text-align:center;font:500 15px U;color:#8d8d96'>"
            "powering up&#8230;</div>")
    return page_html(p, body)


# ---------------------------------------------------------------------------
# Logos
# ---------------------------------------------------------------------------
LOGO_W, LOGO_H = 480, 180


def logo_page_svg(svg_path):
    p = dict(PALETTES[0][2])
    p["name"] = "x"
    body = (f"<div class='a' style='{box(0, 0, LOGO_W, LOGO_H)}display:flex;align-items:center;justify-content:center'>"
            f"<img src='file://{svg_path}' style='max-width:{LOGO_W}px;max-height:{LOGO_H}px;"
            f"width:{LOGO_W}px;height:{LOGO_H}px;object-fit:contain'></div>")
    return page_html(p, body, LOGO_W, LOGO_H)


def logo_page_text(name):
    p = dict(PALETTES[0][2])
    p["name"] = "x"
    from PIL import ImageFont
    size = 120
    while size > 30:
        font = ImageFont.truetype(os.path.join(FONTS, "Urbanist-SemiBold.ttf"), size)
        if font.getlength(name) - size * 0.02 * len(name) <= LOGO_W - 24:
            break
        size -= 4
    body = (f"<div class='a' style='{box(0, 0, LOGO_W, LOGO_H)}display:flex;align-items:center;justify-content:center;"
            f"font:600 {size}px U;color:#fff;letter-spacing:-1px;white-space:nowrap'>{html.escape(name)}</div>")
    return page_html(p, body, LOGO_W, LOGO_H)


def trim_alpha(path, pad=2):
    im = Image.open(path).convert("RGBA")
    bbox = im.getchannel("A").point(lambda v: 255 if v > 6 else 0).getbbox()
    if bbox:
        l, t, r, b = bbox
        im = im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))
    # force pure white so tinting in ES is exact
    white = Image.new("RGBA", im.size, (255, 255, 255, 0))
    white.putalpha(im.getchannel("A"))
    white.save(path, optimize=True)


# ---------------------------------------------------------------------------
# XML
# ---------------------------------------------------------------------------
def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def xml_escape(s):
    return html.escape(s, quote=False)


def colorset_xml(name, display, p):
    v = {
        "cs": name,
        "bgText": xml_hex(p["bgText"]), "bgDim": xml_hex(p["bgDim"]),
        "text": xml_hex(p["text"]), "dim": xml_hex(p["dim"]), "faint": xml_hex(p["faint"]),
        "cardText": xml_hex(p["cardText"]), "cardDim": xml_hex(p["cardDim"]),
        "accent": xml_hex(p["accent"]), "selText": xml_hex(p["selText"]),
        "logo": xml_hex(p["logo"]), "logoCard": xml_hex(p["logoCard"]),
        "star": xml_hex(p["star"]), "starOff": xml_hex(p["starOff"]),
        "menuText": xml_hex(p["text"]) if p["name"] != "citrine-pop" else "F4F4F6",
        "menuDim": xml_hex(p["dim"]),
        "menuSel": xml_hex(p["sel2"]),
        "menuSelText": xml_hex(p["selText"]),
        "menuLine": "FFFFFF14" if p["mode"] == "dark" or p["name"] == "citrine-pop" else "0000001A",
        "statusText": xml_hex(p["text"]) if p["name"] != "citrine-pop" else "F4F4F6",
    }
    lines = "\n".join(f"\t\t<{k}>{val}</{k}>" for k, val in v.items())
    return f"""<!-- {display} colour scheme (generated by build/build.py) -->
<theme>
\t<formatVersion>6</formatVersion>
\t<variables>
{lines}
\t</variables>
</theme>
"""


def fontsize_xml(name, f):
    lst = f["list"]
    spacing = f["spacing"]
    # ES row height = max(tallest glyph, size) * lineSpacing. With DEL patched out
    # of the fonts the tallest Urbanist glyph is ~0.95 x size, so rows = size x spacing.
    # Row text is drawn with a fixed 1.5 line spacing, putting its centre at
    # 0.75 x glyph height; shift the selector so it is centred on the text.
    px = eff_px(lst)
    glyph = glyph_height(px)
    row = max(glyph, px) * spacing
    offset = 0.75 * glyph - row / 2
    desc_line = glyph_height(eff_px(f["desc"])) * DESC_SPACING
    v = {
        "fs": name,
        "listFont": fsz(lst),
        "listSpacing": f"{spacing}",
        "selHeight": f"{row / H:.4f}",
        "selOffset": f"{offset / H:.4f}",
        "descHeight": f"{desc_line * f['descLines'] / H:.4f}",
        "descFont": fsz(f['desc']),
        "menuFont": fsz(f['menu']),
        "menuTitleFont": fsz(f['menuTitle']),
        "menuSmallFont": fsz(f['menuSmall']),
        "sysFont": fsz(f['sys']),
    }
    lines = "\n".join(f"\t\t<{k}>{val}</{k}>" for k, val in v.items())
    return f"""<!-- {name} font size (generated by build/build.py) -->
<theme>
\t<formatVersion>6</formatVersion>
\t<variables>
{lines}
\t</variables>
</theme>
"""


def img(name, path, pos, size=None, max_size=None, origin=None, color=None, extra=False, z=None, other=""):
    s = f'\t\t<image name="{name}"{" extra=\"true\"" if extra else ""}>\n'
    s += f"\t\t\t<path>{path}</path>\n"
    s += f"\t\t\t<pos>{pos}</pos>\n"
    if size:
        s += f"\t\t\t<size>{size}</size>\n"
    if max_size:
        s += f"\t\t\t<maxSize>{max_size}</maxSize>\n"
    if origin:
        s += f"\t\t\t<origin>{origin}</origin>\n"
    if color:
        s += f"\t\t\t<color>{color}</color>\n"
    if z is not None:
        s += f"\t\t\t<zIndex>{z}</zIndex>\n"
    s += other
    s += "\t\t</image>\n"
    return s


def txt(name, pos, size, text=None, font="${fontSemi}", font_size="0.05", color="${text}", align="left",
        valign=None, extra=False, z=None, upper=False, other=""):
    s = f'\t\t<text name="{name}"{" extra=\"true\"" if extra else ""}>\n'
    if text is not None:
        s += f"\t\t\t<text>{text}</text>\n"
    s += f"\t\t\t<pos>{pos}</pos>\n\t\t\t<size>{size}</size>\n"
    s += f"\t\t\t<fontPath>{font}</fontPath>\n\t\t\t<fontSize>{font_size}</fontSize>\n"
    s += f"\t\t\t<color>{color}</color>\n\t\t\t<alignment>{align}</alignment>\n"
    if valign:
        s += f"\t\t\t<verticalAlignment>{valign}</verticalAlignment>\n"
    if upper:
        s += "\t\t\t<forceUppercase>true</forceUppercase>\n"
    if z is not None:
        s += f"\t\t\t<zIndex>{z}</zIndex>\n"
    s += other
    s += "\t\t</text>\n"
    return s


def help_xml(color_var="bgText", dim_var="bgDim"):
    return f"""\t\t<helpsystem name="help">
\t\t\t<pos>{pair_x(14, HELP_Y)}</pos>
\t\t\t<textColor>${{{dim_var}}}</textColor>
\t\t\t<iconColor>${{{color_var}}}</iconColor>
\t\t\t<fontPath>${{fontMedium}}</fontPath>
\t\t\t<fontSize>{fsz(13)}</fontSize>
\t\t</helpsystem>
"""


def card_extras(card, logo_tint="${logoCard}"):
    """Per-system extras on the big system card (vertical / wheel layouts)."""
    x, y, w, h = card
    cx = x + w / 2
    s = ""
    s += txt("sysName", pair_x(x + 24, y + 20), pair_x(w - 48, 32), text="${system.fullName}",
             font="${fontSemi}", font_size="${sysFont}", color="${cardText}", extra=True, z=12)
    s += txt("sysMaker", pair_x(x + 24, y + 54), pair_x(w - 48, 20), text="${sysMaker}",
             font="${fontMedium}", font_size=fsz(15), color="${cardDim}", extra=True, z=12)
    s += img("sysLogoBig", "./../_art/logos/${system.theme}.png", pair_x(cx, y + 172),
             max_size=pair_x(250, 96), origin="0.5 0.5", color=logo_tint, extra=True, z=12)
    s += txt("sysYearLabel", pair_x(x + 24, y + h - 92), pair_x(150, 18), text="${sysYearLabel}",
             font="${fontMedium}", font_size=fsz(13), color="${cardDim}", extra=True, z=12, upper=True)
    s += txt("sysYear", pair_x(x + 22, y + h - 72), pair_x(170, 50), text="${sysYear}",
             font="${fontDot}", font_size=fsz(44), color="${cardText}", extra=True, z=12)
    return s


def system_info_xml(rect, color="${cardText}"):
    x, y, w, h = rect
    return txt("systemInfo", pair_x(x, y), pair_x(w, h), font="${fontMedium}", font_size=fsz(13),
               color=color, align="center", other="\t\t\t<backgroundColor>00000000</backgroundColor>\n")


def systemview_xml(mode):
    s = f"""<!-- System view: {mode} carousel (generated by build/build.py) -->
<theme>
\t<formatVersion>6</formatVersion>
\t<view name="system">
"""
    s += img("background", f"./../_art/${{cs}}/system-{mode}.jpg", "0 0", size="1 1", extra=True, z=0)
    if mode == "horizontal":
        x, y, w, h = H_CARD
        s += f"""\t\t<carousel name="systemcarousel">
\t\t\t<type>horizontal</type>
\t\t\t<pos>{pair_x(0, y)}</pos>
\t\t\t<size>{pair_x(W, h)}</size>
\t\t\t<color>00000000</color>
\t\t\t<logoSize>{pair_x(168, 74)}</logoSize>
\t\t\t<logoScale>1.32</logoScale>
\t\t\t<maxLogoCount>3</maxLogoCount>
\t\t\t<logoAlignment>center</logoAlignment>
\t\t\t<systemInfoDelay>0</systemInfoDelay>
\t\t\t<zIndex>40</zIndex>
\t\t</carousel>
"""
        s += img("logo", "./../_art/logos/${system.theme}.png", "0 0", color="${logoCard}", z=41)
        s += txt("logoText", "0 0", "0 0", font="${fontSemi}", font_size=fsz(30), color="${logoCard}")
        s += txt("sysName", pair_x(40, 312), pair_x(560, 34), text="${system.fullName}", font="${fontSemi}",
                 font_size="${sysFont}", color="${bgText}", align="center", extra=True, z=12)
        s += txt("sysMaker", pair_x(40, 346), pair_x(560, 22), text="${sysMakerYear}", font="${fontMedium}",
                 font_size=fsz(15), color="${bgDim}", align="center", extra=True, z=12)
        px, py, pw, ph = H_PILL
        s += system_info_xml((px + 18, py, pw - 26, ph), color="${statusText}")
    else:
        card = V_CARD if mode == "vertical" else W_CARD
        if mode == "vertical":
            x, y, w, h = V_COLUMN
            s += f"""\t\t<carousel name="systemcarousel">
\t\t\t<type>vertical</type>
\t\t\t<pos>{pair_x(x, y)}</pos>
\t\t\t<size>{pair_x(w, h)}</size>
\t\t\t<color>00000000</color>
\t\t\t<logoSize>{pair_x(150, 34)}</logoSize>
\t\t\t<logoScale>1.18</logoScale>
\t\t\t<maxLogoCount>{CAROUSEL_SLOTS_V}</maxLogoCount>
\t\t\t<logoAlignment>center</logoAlignment>
\t\t\t<systemInfoDelay>0</systemInfoDelay>
\t\t\t<zIndex>40</zIndex>
\t\t</carousel>
"""
        else:
            x, y, w, h = W_TRACK
            s += f"""\t\t<carousel name="systemcarousel">
\t\t\t<type>vertical_wheel</type>
\t\t\t<pos>{pair_x(x, y)}</pos>
\t\t\t<size>{pair_x(w, h)}</size>
\t\t\t<color>00000000</color>
\t\t\t<logoSize>{pair_x(170, 40)}</logoSize>
\t\t\t<logoScale>1.15</logoScale>
\t\t\t<logoRotation>9</logoRotation>
\t\t\t<logoRotationOrigin>3.2 0.5</logoRotationOrigin>
\t\t\t<maxLogoCount>7</maxLogoCount>
\t\t\t<logoAlignment>center</logoAlignment>
\t\t\t<systemInfoDelay>0</systemInfoDelay>
\t\t\t<zIndex>40</zIndex>
\t\t</carousel>
"""
        s += img("logo", "./../_art/logos/${system.theme}.png", "0 0", color="${logo}", z=41)
        s += txt("logoText", "0 0", "0 0", font="${fontSemi}", font_size=fsz(20), color="${logo}")
        s += card_extras(card)
        s += system_info_xml(sys_info_pill(card))
    s += help_xml()
    s += "\t</view>\n</theme>\n"
    return s


def gamelist_xml():
    lx, ly, lw, lh = LIST_INNER
    ax, ay, aw, ah = ART_WELL
    ix, iy, iw, ih = INFO
    acx, acy = ax + aw / 2, ay + ah / 2
    s = """<!-- Game list views (generated by build/build.py) -->
<theme>
\t<formatVersion>6</formatVersion>
\t<view name="basic, detailed, video, grid">
"""
    s += img("background", "./../_art/${cs}/gamelist.jpg", "0 0", size="1 1", z=0)
    hx, hy, hw, hh = HEADER_LOGO
    s += img("logo", "./../_art/logos/${system.theme}.png", pair_x(hx, hy), max_size=pair_x(hw, hh),
             origin="0 0.5", color="${logo}", z=50)
    s += f"""\t\t<textlist name="gamelist">
\t\t\t<pos>{pair_x(lx, ly)}</pos>
\t\t\t<size>{pair_x(lw, lh)}</size>
\t\t\t<selectorImagePath>./../_art/${{cs}}/selector-${{fs}}.png</selectorImagePath>
\t\t\t<selectorImageTile>false</selectorImageTile>
\t\t\t<selectorColor>FFFFFFFF</selectorColor>
\t\t\t<selectorColorEnd>FFFFFFFF</selectorColorEnd>
\t\t\t<selectorHeight>${{selHeight}}</selectorHeight>
\t\t\t<selectorOffsetY>${{selOffset}}</selectorOffsetY>
\t\t\t<selectedColor>${{selText}}</selectedColor>
\t\t\t<primaryColor>${{text}}</primaryColor>
\t\t\t<secondaryColor>${{accent}}</secondaryColor>
\t\t\t<fontPath>${{fontMedium}}</fontPath>
\t\t\t<fontSize>${{listFont}}</fontSize>
\t\t\t<lineSpacing>${{listSpacing}}</lineSpacing>
\t\t\t<alignment>left</alignment>
\t\t\t<horizontalMargin>{14 / W:.4f}</horizontalMargin>
\t\t\t<zIndex>20</zIndex>
\t\t</textlist>
"""
    s += help_xml()
    s += "\t</view>\n"

    # --- detailed + video + grid: art + info ---------------------------------
    s += '\t<view name="detailed, video, grid">\n'
    art_max = pair_x(aw - 2 * ART_PAD, ah - 2 * ART_PAD)
    s += img("md_image", "", pair_x(acx, acy), max_size=art_max, origin="0.5 0.5", z=30,
             other=f"\t\t\t<default>./../_art/${{cs}}/noart.png</default>\n\t\t\t<roundCorners>0.025</roundCorners>\n"
             ).replace("\t\t\t<path></path>\n", "")
    s += f"""\t\t<rating name="md_rating">
\t\t\t<pos>{pair_x(ix + 18, iy + 11)}</pos>
\t\t\t<size>{pair_x(0, 15)}</size>
\t\t\t<filledPath>./../_art/ui/star-filled.png</filledPath>
\t\t\t<unfilledPath>./../_art/ui/star-empty.png</unfilledPath>
\t\t\t<color>${{star}}</color>
\t\t\t<unfilledColor>${{starOff}}</unfilledColor>
\t\t\t<zIndex>40</zIndex>
\t\t</rating>
\t\t<datetime name="md_releasedate">
\t\t\t<pos>{pair_x(ix + iw - 18 - 120, iy + 6)}</pos>
\t\t\t<size>{pair_x(120, 24)}</size>
\t\t\t<fontPath>${{fontDot}}</fontPath>
\t\t\t<fontSize>{fsz(20)}</fontSize>
\t\t\t<color>${{cardText}}</color>
\t\t\t<alignment>right</alignment>
\t\t\t<format>%Y</format>
\t\t\t<zIndex>40</zIndex>
\t\t</datetime>
\t\t<text name="md_genre">
\t\t\t<pos>{pair_x(ix + 104, iy + 9)}</pos>
\t\t\t<size>{pair_x(iw - 104 - 18 - 64, 18)}</size>
\t\t\t<fontPath>${{fontMedium}}</fontPath>
\t\t\t<fontSize>{fsz(13)}</fontSize>
\t\t\t<color>${{cardDim}}</color>
\t\t\t<alignment>left</alignment>
\t\t\t<singleLineScroll>false</singleLineScroll>
\t\t\t<zIndex>40</zIndex>
\t\t</text>
\t\t<text name="md_description">
\t\t\t<pos>{pair_x(ix + 18, iy + 42)}</pos>
\t\t\t<size>{nx(iw - 36)} ${{descHeight}}</size>
\t\t\t<fontPath>${{fontMedium}}</fontPath>
\t\t\t<fontSize>${{descFont}}</fontSize>
\t\t\t<color>${{cardText}}</color>
\t\t\t<alignment>left</alignment>
\t\t\t<lineSpacing>{DESC_SPACING}</lineSpacing>
\t\t\t<zIndex>40</zIndex>
\t\t</text>
"""
    # labels and fields we don't show
    for n in ("md_lbl_rating", "md_lbl_releasedate", "md_lbl_developer", "md_lbl_publisher", "md_lbl_genre",
              "md_lbl_players", "md_lbl_lastplayed", "md_lbl_playcount", "md_developer", "md_publisher",
              "md_players", "md_lastplayed", "md_playcount", "md_name"):
        tag = "datetime" if n == "md_lastplayed" else "text"
        s += f'\t\t<{tag} name="{n}">\n\t\t\t<visible>false</visible>\n\t\t\t<pos>2 2</pos>\n\t\t</{tag}>\n'
    s += "\t</view>\n"

    s += '\t<view name="video">\n'
    s += f"""\t\t<video name="md_video">
\t\t\t<pos>{pair_x(acx, acy)}</pos>
\t\t\t<maxSize>{art_max}</maxSize>
\t\t\t<origin>0.5 0.5</origin>
\t\t\t<default>./../_art/${{cs}}/noart.png</default>
\t\t\t<delay>1.2</delay>
\t\t\t<showSnapshotNoVideo>true</showSnapshotNoVideo>
\t\t\t<showSnapshotDelay>true</showSnapshotDelay>
\t\t\t<roundCorners>0.025</roundCorners>
\t\t\t<zIndex>31</zIndex>
\t\t</video>
"""
    s += "\t</view>\n"

    # --- grid: tiles in the left panel ---------------------------------------
    s += '\t<view name="grid">\n'
    gx, gy, gw, gh = LIST
    s += f"""\t\t<imagegrid name="gamegrid">
\t\t\t<pos>{pair_x(gx + 8, gy + 8)}</pos>
\t\t\t<size>{pair_x(gw - 16, gh - 16)}</size>
\t\t\t<margin>{pair_x(6, 6)}</margin>
\t\t\t<autoLayout>3 3</autoLayout>
\t\t\t<autoLayoutSelectedZoom>1</autoLayoutSelectedZoom>
\t\t\t<imageSource>image</imageSource>
\t\t\t<gameImage>./../_art/${{cs}}/noart.png</gameImage>
\t\t\t<folderImage>./../_art/${{cs}}/noart.png</folderImage>
\t\t\t<scrollDirection>vertical</scrollDirection>
\t\t\t<centerSelection>false</centerSelection>
\t\t\t<zIndex>20</zIndex>
\t\t</imagegrid>
\t\t<gridtile name="default">
\t\t\t<padding>4 4</padding>
\t\t\t<imageColor>FFFFFFFF</imageColor>
\t\t\t<backgroundColor>${{text}}10</backgroundColor>
\t\t\t<backgroundCenterColor>${{text}}10</backgroundCenterColor>
\t\t\t<backgroundEdgeColor>${{text}}10</backgroundEdgeColor>
\t\t\t<backgroundImage>./../_art/ui/tile.png</backgroundImage>
\t\t\t<backgroundCornerSize>0.07 0.07</backgroundCornerSize>
\t\t</gridtile>
\t\t<gridtile name="selected">
\t\t\t<backgroundColor>${{accent}}FF</backgroundColor>
\t\t\t<backgroundCenterColor>${{accent}}FF</backgroundCenterColor>
\t\t\t<backgroundEdgeColor>${{accent}}FF</backgroundEdgeColor>
\t\t</gridtile>
\t\t<text name="md_name">
\t\t\t<visible>false</visible>
\t\t\t<pos>2 2</pos>
\t\t</text>
\t</view>
"""

    # --- basic: no scraped data, show the system instead ---------------------
    s += '\t<view name="basic">\n'
    s += img("background", "./../_art/${cs}/gamelist-basic.jpg", "0 0", size="1 1", z=0)
    s += img("basicLogo", "./../_art/logos/${system.theme}.png", pair_x(acx, acy - 14), max_size=pair_x(220, 84),
             origin="0.5 0.5", color="${dim}", extra=True, z=30)
    s += txt("basicName", pair_x(ax + 16, acy + 46), pair_x(aw - 32, 24), text="${system.fullName}",
             font="${fontSemi}", font_size=fsz(17), color="${text}", align="center", extra=True, z=30)
    s += txt("basicHint", pair_x(ix + 18, iy + 16), pair_x(iw - 36, ih - 32),
             text="No game info yet. Open the menu with START and run the scraper to add box art, descriptions and ratings.",
             font="${fontMedium}", font_size="${descFont}", color="${cardText}", extra=True, z=30,
             other="\t\t\t<lineSpacing>1.25</lineSpacing>\n")
    s += "\t</view>\n</theme>\n"
    return s


def menu_xml():
    return """<!-- Settings menu (generated by build/build.py) -->
<theme>
\t<formatVersion>6</formatVersion>
\t<view name="menu">
\t\t<menuBackground name="menubg">
\t\t\t<path>./../_art/${cs}/menu.png</path>
\t\t\t<fadePath>./../_art/ui/fade.png</fadePath>
\t\t\t<color>FFFFFFFF</color>
\t\t\t<centerColor>FFFFFFFF</centerColor>
\t\t\t<cornerSize>32 32</cornerSize>
\t\t</menuBackground>
\t\t<menuText name="menutitle">
\t\t\t<fontPath>${fontSemi}</fontPath>
\t\t\t<fontSize>${menuTitleFont}</fontSize>
\t\t\t<color>${menuText}</color>
\t\t</menuText>
\t\t<menuText name="menutext">
\t\t\t<fontPath>${fontMedium}</fontPath>
\t\t\t<fontSize>${menuFont}</fontSize>
\t\t\t<color>${menuText}</color>
\t\t\t<separatorColor>${menuLine}</separatorColor>
\t\t\t<selectorColor>${menuSel}</selectorColor>
\t\t\t<selectedColor>${menuSelText}</selectedColor>
\t\t</menuText>
\t\t<menuTextSmall name="menutextsmall">
\t\t\t<fontPath>${fontMedium}</fontPath>
\t\t\t<fontSize>${menuSmallFont}</fontSize>
\t\t\t<color>${menuDim}</color>
\t\t</menuTextSmall>
\t\t<menuText name="menufooter">
\t\t\t<fontPath>${fontMedium}</fontPath>
\t\t\t<fontSize>${menuSmallFont}</fontSize>
\t\t\t<color>${menuDim}</color>
\t\t</menuText>
\t\t<menuSwitch name="menuswitch">
\t\t\t<pathOn>./../_art/${cs}/switch-on.png</pathOn>
\t\t\t<pathOff>./../_art/${cs}/switch-off.png</pathOff>
\t\t</menuSwitch>
\t\t<menuSlider name="menuslider">
\t\t\t<path>./../_art/${cs}/knob.png</path>
\t\t</menuSlider>
\t\t<menuButton name="menubutton">
\t\t\t<path>./../_art/${cs}/button.png</path>
\t\t\t<filledPath>./../_art/${cs}/button-filled.png</filledPath>
\t\t</menuButton>
\t\t<menuTextEdit name="menutextedit">
\t\t\t<inactive>./../_art/${cs}/textedit.png</inactive>
\t\t\t<active>./../_art/${cs}/textedit-active.png</active>
\t\t</menuTextEdit>
\t</view>
</theme>
"""


def screen_xml():
    x, y, w, h = STATUS
    return f"""<!-- Always-on overlays: clock + battery inside the top-right status capsule -->
<theme>
\t<formatVersion>6</formatVersion>
\t<view name="screen">
\t\t<text name="clock">
\t\t\t<pos>{pair_x(x + 8, y)}</pos>
\t\t\t<size>{pair_x(70, h)}</size>
\t\t\t<fontPath>${{fontSemi}}</fontPath>
\t\t\t<fontSize>{fsz(16)}</fontSize>
\t\t\t<color>${{statusText}}</color>
\t\t\t<alignment>center</alignment>
\t\t\t<verticalAlignment>center</verticalAlignment>
\t\t</text>
\t\t<batteryIndicator name="batteryIndicator">
\t\t\t<pos>{pair_x(x + 88, y + 6)}</pos>
\t\t\t<size>{pair_x(w - 96, 20)}</size>
\t\t\t<itemSpacing>{3 / W:.4f}</itemSpacing>
\t\t\t<horizontalAlignment>center</horizontalAlignment>
\t\t\t<color>${{statusText}}</color>
\t\t\t<incharge>./../_art/ui/battery-charging.svg</incharge>
\t\t\t<full>./../_art/ui/battery-100.svg</full>
\t\t\t<at75>./../_art/ui/battery-75.svg</at75>
\t\t\t<at50>./../_art/ui/battery-50.svg</at50>
\t\t\t<at25>./../_art/ui/battery-25.svg</at25>
\t\t\t<empty>./../_art/ui/battery-0.svg</empty>
\t\t</batteryIndicator>
\t</view>
</theme>
"""


def main_xml():
    cs = "\n".join(f'\t\t<include name="{n}" displayName="{d}">./color-{n}.xml</include>' for n, d, _ in PALETTES)
    fs = "\n".join(f'\t\t<include name="{n}" displayName="{n.capitalize()}">./font-{n}.xml</include>'
                   for n in ("medium", "small", "large"))
    return f"""<!--
	Volta - EmulationStation theme for the R36S (ArkOS, 640x480)
	Generated by build/build.py - edit the generator, not this file.
-->
<theme>
\t<formatVersion>6</formatVersion>
\t<variables>
\t\t<fontMedium>./../_fonts/Urbanist-Medium.ttf</fontMedium>
\t\t<fontSemi>./../_fonts/Urbanist-SemiBold.ttf</fontSemi>
\t\t<fontDot>./../_fonts/Doto-Black.ttf</fontDot>
\t</variables>

\t<!--
\t\tDefaults first, so the theme still works if a subset setting holds a value
\t\tthis theme does not know. The subsets below override these variables.
\t-->
\t<include>./color-volta-dark.xml</include>
\t<include>./font-medium.xml</include>

\t<!--
\t\tOptions use Volta-specific setting keys (subset.voltacolor, ...). The shared
\t\tkeys (ThemeColorSet, ThemeSystemView) often hold names saved by the previous
\t\ttheme; no entry would match and ES would load no colours or carousel at all.
\t\tFirst entry of each subset is the default.
\t-->
\t<subset name="voltacolor" displayName="Color scheme">
{cs}
\t</subset>
\t<subset name="voltafont" displayName="Font size">
{fs}
\t</subset>
\t<subset name="voltacarousel" displayName="System carousel">
\t\t<include name="horizontal" displayName="Horizontal">./system-horizontal.xml</include>
\t\t<include name="vertical" displayName="Vertical list">./system-vertical.xml</include>
\t\t<include name="wheel" displayName="Wheel">./system-wheel.xml</include>
\t</subset>

\t<include>./gamelist.xml</include>
\t<include>./menu.xml</include>
\t<include>./screen.xml</include>
</theme>
"""


def system_theme_xml(folder, meta):
    _logo, name, maker, year = meta
    maker_year = " · ".join(x for x in (maker, year) if x)
    return f"""<theme>
\t<formatVersion>6</formatVersion>
\t<variables>
\t\t<sysMaker>{xml_escape(maker)}</sysMaker>
\t\t<sysYear>{year}</sysYear>
\t\t<sysYearLabel>{'Released' if year else ''}</sysYearLabel>
\t\t<sysMakerYear>{xml_escape(maker_year)}</sysMakerYear>
\t</variables>
\t<include>./../_inc/main.xml</include>
</theme>
"""


def root_theme_xml():
    return """<!-- Fallback for systems without their own folder -->
<theme>
\t<formatVersion>6</formatVersion>
\t<include>./_inc/main.xml</include>
</theme>
"""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def to_jpeg(png, jpg, q=93):
    Image.open(png).convert("RGB").save(jpg, quality=q, optimize=True, progressive=False, subsampling=0)
    os.remove(png)


def write_bmp_variants():
    src = os.path.join(BOOT, "bootlogo.png")
    im = Image.open(src).convert("RGB")
    variants = {"640x480": im, "480x640-cw": im.transpose(Image.ROTATE_270),
                "480x640-ccw": im.transpose(Image.ROTATE_90)}
    for old in os.listdir(BOOT):
        if old.endswith(".bmp"):
            os.remove(os.path.join(BOOT, old))
    for tag, v in variants.items():
        v.save(os.path.join(BOOT, f"logo-{tag}-24.bmp"))
        v.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(
            os.path.join(BOOT, f"logo-{tag}-8.bmp"))


def main():
    os.makedirs(ART, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="volta-")
    jobs = []
    post = []  # (callable)

    def job(name, html_text, w_, h_, out, transparent=False):
        hp = os.path.join(tmp, name + ".html")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(html_text)
        jobs.append(dict(html=hp, w=w_, h=h_, out=out, transparent=transparent))

    # --- per colour scheme ---------------------------------------------------
    if want("art"):
        for name, display, p in PALETTES:
            p = dict(p)
            p["name"] = name
            d = os.path.join(ART, name)
            os.makedirs(d, exist_ok=True)
            for mode in ("horizontal", "vertical", "wheel"):
                out = os.path.join(d, f"system-{mode}.png")
                job(f"{name}-sys-{mode}", system_page(p, mode), W, H, out)
                post.append(lambda o=out: to_jpeg(o, o[:-4] + ".jpg"))
            out = os.path.join(d, "gamelist.png")
            job(f"{name}-gl", gamelist_page(p), W, H, out)
            post.append(lambda o=out: to_jpeg(o, o[:-4] + ".jpg"))
            out = os.path.join(d, "gamelist-basic.png")
            job(f"{name}-glb", gamelist_page(p, placeholder=False), W, H, out)
            post.append(lambda o=out: to_jpeg(o, o[:-4] + ".jpg"))
            job(f"{name}-noart", noart_page(p, 564, 484), 564, 484, os.path.join(d, "noart.png"), True)
            lw = LIST_INNER[2]
            for fsn, f in FONT_SIZES.items():
                px = eff_px(f["list"])
                sh = round(max(glyph_height(px), px) * f["spacing"])
                job(f"{name}-sel-{fsn}", selector_page(p, lw, sh), lw, sh,
                    os.path.join(d, f"selector-{fsn}.png"), True)
            job(f"{name}-menu", menu_bg_page(p), 96, 96, os.path.join(d, "menu.png"), True)
            job(f"{name}-on", switch_page(p, True), 128, 96, os.path.join(d, "switch-on.png"), True)
            job(f"{name}-off", switch_page(p, False), 128, 96, os.path.join(d, "switch-off.png"), True)
            job(f"{name}-knob", knob_page(p), 64, 64, os.path.join(d, "knob.png"), True)
            job(f"{name}-btn", button_page(p, False), 48, 48, os.path.join(d, "button.png"), True)
            job(f"{name}-btnf", button_page(p, True), 48, 48, os.path.join(d, "button-filled.png"), True)
            job(f"{name}-te", textedit_page(p, False), 48, 48, os.path.join(d, "textedit.png"), True)
            job(f"{name}-tea", textedit_page(p, True), 48, 48, os.path.join(d, "textedit-active.png"), True)
            # preview swatch for docs
            job(f"{name}-swatch", page_html(p, f"<div class='card' style='{box(8, 8, 144, 84)}border-radius:26px'></div>"
                                               f"<div class='pill' style='{box(110, 64, 34, 14)}background:{css_hex(p['accent'])}'></div>",
                                            160, 100), 160, 100, os.path.join(tmp, f"swatch-{name}.png"), True)

    # --- shared UI -------------------------------------------------------------
    ui = os.path.join(ART, "ui")
    os.makedirs(ui, exist_ok=True)
    if want("ui"):
        p0 = dict(PALETTES[0][2], name="x")
        for filled in (True, False):
            sp = os.path.join(tmp, f"star-{filled}.svg")
            with open(sp, "w") as f:
                f.write(star_svg(filled))
            job(f"star-{filled}", page_html(p0, f"<img src='file://{sp}' style='width:96px;height:96px'>", 96, 96),
                96, 96, os.path.join(ui, "star-filled.png" if filled else "star-empty.png"), True)
        for lvl in (0, 25, 50, 75, 100):
            w(os.path.join(ui, f"battery-{lvl}.svg"), battery_svg(lvl))
        w(os.path.join(ui, "battery-charging.svg"), battery_svg(100, charging=True))
        # list scroll fade used behind menus: soft vertical gradient
        fade = Image.new("RGBA", (4, 256))
        for yy in range(256):
            a = int(255 * (yy / 255) ** 1.6 * 0.85)
            for xx in range(4):
                fade.putpixel((xx, yy), (0, 0, 0, a))
        fade.save(os.path.join(ui, "fade.png"))
        # plain texture for grid tiles (ES needs a texture, then draws a tinted round rect)
        Image.new("RGBA", (16, 16), (255, 255, 255, 255)).save(os.path.join(ui, "tile.png"))

    # --- logos -----------------------------------------------------------------
    if want("logos"):
        if not ABN_LOGOS or not os.path.isdir(ABN_LOGOS):
            sys.exit("set ABN_LOGOS to art-book-next-es-de/_inc/systems/logos")
        ld = os.path.join(ART, "logos")
        if os.path.isdir(ld):
            shutil.rmtree(ld)
        os.makedirs(ld)
        rendered = {}
        for folder, meta in sorted(SYSTEMS.items()):
            logo, name = meta[0], meta[1]
            key = logo or ("text:" + name)
            out = os.path.join(ld, folder + ".png")
            if key in rendered:
                post.append(lambda a=rendered[key], b=out: shutil.copyfile(a, b))
                continue
            rendered[key] = out
            if logo:
                svg = os.path.join(ABN_LOGOS, logo + ".svg")
                if not os.path.exists(svg):
                    sys.exit(f"missing logo {svg}")
                job(f"logo-{folder}", logo_page_svg(svg), LOGO_W, LOGO_H, out, True)
            else:
                job(f"logo-{folder}", logo_page_text(name), LOGO_W, LOGO_H, out, True)
            post.insert(0, lambda o=out: trim_alpha(o))

    # --- boot / splash -----------------------------------------------------------
    if want("boot"):
        os.makedirs(BOOT, exist_ok=True)
        w(os.path.join(BOOT, "splash.svg"), splash_svg())
        job("bootlogo", boot_logo_page(), W, H, os.path.join(BOOT, "bootlogo.png"))
        post.append(write_bmp_variants)

    if jobs:
        jp = os.path.join(tmp, "jobs.json")
        with open(jp, "w") as f:
            json.dump(jobs, f)
        subprocess.run(["node", os.path.join(HERE, "render.mjs"), jp], check=True)
    # trims must run before copies of the same logo
    for fn in post:
        fn()

    if want("art"):
        # contact sheet of all colour schemes for the README
        sw = [Image.open(os.path.join(tmp, f"swatch-{n}.png")) for n, _, _ in PALETTES]
        sheet = Image.new("RGBA", (160 * 7, 100 * 2), (0, 0, 0, 0))
        for i, im in enumerate(sw):
            sheet.paste(im, ((i % 7) * 160, (i // 7) * 100), im)
        os.makedirs(os.path.join(THEME, "_preview"), exist_ok=True)
        sheet.save(os.path.join(THEME, "_preview", "colorsets.png"))

    # --- XML ---------------------------------------------------------------------
    if want("xml"):
        os.makedirs(INC, exist_ok=True)
        for name, display, p in PALETTES:
            w(os.path.join(INC, f"color-{name}.xml"), colorset_xml(name, display, dict(p, name=name)))
        for name, f in FONT_SIZES.items():
            w(os.path.join(INC, f"font-{name}.xml"), fontsize_xml(name, f))
        for mode in ("horizontal", "vertical", "wheel"):
            w(os.path.join(INC, f"system-{mode}.xml"), systemview_xml(mode))
        w(os.path.join(INC, "gamelist.xml"), gamelist_xml())
        w(os.path.join(INC, "menu.xml"), menu_xml())
        w(os.path.join(INC, "screen.xml"), screen_xml())
        w(os.path.join(INC, "main.xml"), main_xml())
        w(os.path.join(THEME, "theme.xml"), root_theme_xml())
        for folder, meta in SYSTEMS.items():
            w(os.path.join(THEME, folder, "theme.xml"), system_theme_xml(folder, meta))

    shutil.rmtree(tmp, ignore_errors=True)
    print("theme written to", THEME)


if __name__ == "__main__":
    main()
