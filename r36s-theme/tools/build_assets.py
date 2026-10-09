#!/usr/bin/env python3
"""Generate every raster/vector asset of the NeonGlow theme.

Inputs : tools/.cache/carbon (Carbon logo pack, fetched automatically)
         tools/fonts (Barlow / Barlow Condensed, OFL)
Outputs: neonglow/art/**  and  extras/**
"""
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import gfx  # noqa: E402
from palette import COLORSETS, ACCENTS  # noqa: E402
from systems import SYSTEMS  # noqa: E402
from svgtext import text_path  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
THEME = os.path.join(ROOT, "neonglow")
ART = os.path.join(THEME, "art")
EXTRAS = os.path.join(ROOT, "extras")
CACHE = os.path.join(TOOLS, ".cache")
CARBON = os.path.join(CACHE, "carbon")
FONTS = os.path.join(TOOLS, "fonts")
F_DISPLAY = os.path.join(FONTS, "BarlowCondensed-Bold.ttf")
F_SEMI = os.path.join(FONTS, "BarlowCondensed-SemiBold.ttf")
F_BODY = os.path.join(FONTS, "Barlow-Medium.ttf")

TILE = 320
BODY = (42, 42, 278, 278)


def mk(*p):
    path = os.path.join(*p)
    os.makedirs(path, exist_ok=True)
    return path


def fetch_carbon():
    if os.path.isdir(os.path.join(CARBON, "art", "logos")):
        return
    os.makedirs(CACHE, exist_ok=True)
    subprocess.check_call(["git", "clone", "--depth", "1",
                           "https://github.com/fabricecaruso/es-theme-carbon.git", CARBON])


# --------------------------------------------------------------------------
# Glow tile
# --------------------------------------------------------------------------
def inset(box, d):
    return (box[0] + d, box[1] + d, box[2] - d, box[3] - d)


def tile_layers():
    size = (TILE, TILE)
    body_m = gfx.arr(gfx.superellipse_mask(size, BODY))
    outer = gfx.arr(gfx.blur(gfx.superellipse_mask(size, inset(BODY, -6)), 15))
    outer2 = gfx.arr(gfx.blur(gfx.superellipse_mask(size, inset(BODY, -2)), 5))
    rim_in = gfx.arr(gfx.superellipse_mask(size, inset(BODY, 4)))
    rim = gfx.arr(gfx.blur(gfx.to_img(np.clip(body_m - rim_in, 0, 1)), 1.2))
    deep = gfx.arr(gfx.blur(gfx.superellipse_mask(size, inset(BODY, 26)), 12))
    inner = np.clip(body_m - deep, 0, 1) * body_m

    glow_a = np.clip(outer * 0.85 * (1 - body_m) + outer2 * 0.6 * (1 - body_m)
                     + rim * 0.95 + inner * 0.62, 0, 1)
    glow = gfx.white_alpha(glow_a)

    # dark glass body with vertical gradient, top sheen and grain
    h = TILE
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None] * np.ones((1, TILE), np.float32)
    top, bot = np.array([27, 27, 35]) / 255.0, np.array([10, 10, 14]) / 255.0
    rgb = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    sheen = np.clip(1 - (y - 0.13) / 0.32, 0, 1) * 0.045
    rgb = rgb + sheen[..., None] + gfx.noise((TILE, TILE), 0.012, 7)[..., None]
    body = np.concatenate([np.clip(rgb, 0, 1), body_m[..., None]], -1)
    return gfx.to_img(body, "RGBA"), glow


def render_logo(key):
    svg = os.path.join(CARBON, "art", "logos", key + ".svg")
    png = os.path.join(CARBON, "art", "logos", key + ".png")
    tmp = os.path.join(CACHE, "render.png")
    if os.path.exists(svg):
        subprocess.check_call(["rsvg-convert", "-w", "1100", "-a", svg, "-o", tmp])
        img = Image.open(tmp).convert("RGBA")
    elif os.path.exists(png):
        img = Image.open(png).convert("RGBA")
    else:
        return None
    return gfx.lift_dark(gfx.trim(img))


def wordmark(text, rgb):
    words = text.split(" ")
    lines = [text]
    if len(text) > 8 and len(words) > 1:
        mid = len(words) // 2 if len(words) > 2 else 1
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    imgs = [gfx.text_image(l, F_DISPLAY, 150, (255, 255, 255, 255), tracking=4) for l in lines]
    w = max(i.width for i in imgs)
    gap = 10
    h = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    yy = 0
    for i in imgs:
        out.alpha_composite(i, ((w - i.width) // 2, yy))
        yy += i.height + gap
    light = tuple(int(c + (255 - c) * 0.35) for c in rgb)
    return gfx.tint(out, light)


def logo_layer(img):
    layer = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    ar = img.width / img.height
    # wide wordmarks get more width, compact emblems more height
    bw, bh = (196, 124) if ar > 1.6 else (156, 142)
    f = gfx.fit(img, bw, bh)
    layer.alpha_composite(f, ((TILE - f.width) // 2, (TILE - f.height) // 2))
    return layer


def build_tiles():
    body, glow = tile_layers()
    d = mk(ART, "tile")
    body.save(os.path.join(d, "body.png"), optimize=True)
    glow.save(os.path.join(d, "glow.png"), optimize=True)
    # small glow tile used for the gamelist header + generic fallback
    logos_d, icons_d = mk(ART, "logos"), mk(ART, "icons")
    colors = {}
    for theme, s in sorted(SYSTEMS.items()):
        img = render_logo(s["logo"]) if s["logo"] else None
        if s["color"]:
            rgb = gfx.normalize_glow(gfx.hex_rgb(s["color"]))
        else:
            rgb = gfx.normalize_glow(gfx.dominant_color(img)) if img else (142, 155, 176)
        if img is None:
            img = wordmark(s["mark"], rgb)
        colors[theme] = "%02X%02X%02X" % rgb
        layer = logo_layer(img)
        layer.save(os.path.join(logos_d, theme + ".png"), optimize=True)
        comp = body.copy()
        comp.alpha_composite(gfx.tint(glow, rgb))
        comp.alpha_composite(layer)
        comp.save(os.path.join(icons_d, theme + ".png"), optimize=True)
    # generic fallback tile
    rgb = (142, 155, 176)
    layer = logo_layer(wordmark("GAMES", rgb))
    layer.save(os.path.join(logos_d, "_default.png"))
    comp = body.copy()
    comp.alpha_composite(gfx.tint(glow, rgb))
    comp.alpha_composite(layer)
    comp.save(os.path.join(icons_d, "_default.png"))
    return colors


# --------------------------------------------------------------------------
# Backgrounds
# --------------------------------------------------------------------------
def build_backgrounds():
    d = mk(ART, "bg")
    Image.new("RGBA", (8, 8), (255, 255, 255, 255)).save(os.path.join(d, "pixel.png"))
    Image.new("RGBA", (8, 8), (255, 255, 255, 0)).save(os.path.join(d, "none.png"))

    # dot grid, 16 px pitch
    t = 16
    m = Image.new("L", (t * gfx.SS, t * gfx.SS), 0)
    c = t * gfx.SS / 2
    r = 1.25 * gfx.SS
    ImageDraw.Draw(m).ellipse([c - r, c - r, c + r, c + r], fill=255)
    m = m.resize((t, t), Image.LANCZOS)
    gfx.white_alpha(gfx.arr(m)).save(os.path.join(d, "dots.png"))

    # plus grid, 32 px pitch
    t = 32
    m = Image.new("L", (t * gfx.SS, t * gfx.SS), 0)
    dr = ImageDraw.Draw(m)
    c, arm, th = t * gfx.SS / 2, 4.0 * gfx.SS, 0.75 * gfx.SS
    dr.rectangle([c - arm, c - th, c + arm, c + th], fill=255)
    dr.rectangle([c - th, c - arm, c + th, c + arm], fill=255)
    m = m.resize((t, t), Image.LANCZOS)
    gfx.white_alpha(gfx.arr(m)).save(os.path.join(d, "plus.png"))

    # soft radial light (tinted with the accent in the theme)
    n = 512
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    rr = np.hypot(xx - n / 2 + 0.5, yy - n / 2 + 0.5) / (n / 2)
    a = np.clip(np.exp(-(rr ** 2) * 3.2) - np.exp(-3.2), 0, 1) / (1 - np.exp(-3.2))
    gfx.white_alpha(a).save(os.path.join(d, "radial.png"))

    # vignette (multiply-dark at the edges)
    w, h = 640, 480
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2)
    v = np.clip((np.sqrt(nx ** 2 * 0.8 + ny ** 2) - 0.55) / 0.75, 0, 1) ** 1.6
    out = np.zeros((h, w, 4), np.float32)
    out[..., 3] = v
    gfx.to_img(out, "RGBA").save(os.path.join(d, "vignette.png"))

    # horizontal fade (accent rules, list selector sheen)
    w = 512
    a = np.linspace(1, 0, w, dtype=np.float32)[None, :] ** 1.3 * np.ones((4, 1), np.float32)
    gfx.white_alpha(a).save(os.path.join(d, "hfade.png"))
    # vertical fade for the help bar top edge
    a = np.linspace(0, 1, 64, dtype=np.float32)[:, None] * np.ones((1, 4), np.float32)
    gfx.white_alpha(a).save(os.path.join(d, "vfade.png"))


# --------------------------------------------------------------------------
# UI pieces (ninepatches, stars, battery, menu icons, switches)
# --------------------------------------------------------------------------
def ninepatch(path, size, radius, outline=None):
    m = gfx.rounded_mask((size, size), (0, 0, size, size), radius)
    a = gfx.arr(m)
    if outline:
        inner = gfx.arr(gfx.rounded_mask((size, size), (outline, outline, size - outline, size - outline),
                                         max(1, radius - outline)))
        a = np.clip(a - inner, 0, 1)
    gfx.white_alpha(a).save(path)


def svg(path, body, w=64, h=64):
    with open(path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                + body + "</svg>\n")


STAR = ("M32 4 L40.2 22.6 L60.4 24.6 L45.2 38.2 L49.6 58.2 L32 47.8 L14.4 58.2 L18.8 38.2 "
        "L3.6 24.6 L23.8 22.6 Z")


def build_ui():
    d = mk(ART, "ui")
    ninepatch(os.path.join(d, "panel.png"), 48, 14)
    ninepatch(os.path.join(d, "panel_edge.png"), 48, 14, outline=2)
    ninepatch(os.path.join(d, "menu.png"), 64, 20)
    ninepatch(os.path.join(d, "button.png"), 48, 12, outline=3)
    ninepatch(os.path.join(d, "button_filled.png"), 48, 12)
    ninepatch(os.path.join(d, "textinput.png"), 48, 10, outline=2)
    ninepatch(os.path.join(d, "textinput_active.png"), 48, 10, outline=4)

    svg(os.path.join(d, "star_filled.svg"), f'<path d="{STAR}" fill="#FFFFFF"/>')
    svg(os.path.join(d, "star_empty.svg"),
        f'<path d="{STAR}" fill="#FFFFFF" fill-opacity="0.18" stroke="#FFFFFF" stroke-opacity="0.55" '
        'stroke-width="3" stroke-linejoin="round"/>')

    # battery (white; tinted by the theme)
    b = mk(ART, "battery")
    shell = ('<rect x="3" y="9" width="50" height="30" rx="7" fill="none" stroke="#FFFFFF" stroke-width="4"/>'
             '<rect x="56" y="17" width="5" height="14" rx="2" fill="#FFFFFF"/>')
    for name, frac in (("full", 1.0), ("75", 0.75), ("50", 0.5), ("25", 0.25), ("empty", 0.0)):
        fill = "" if frac == 0 else f'<rect x="9" y="15" width="{38 * frac:.1f}" height="18" rx="3" fill="#FFFFFF"/>'
        if frac == 0:
            fill = '<rect x="9" y="15" width="5" height="18" rx="2" fill="#FF3B3B"/>'
        svg(os.path.join(b, name + ".svg"), shell + fill, 64, 48)
    svg(os.path.join(b, "incharge.svg"),
        shell + '<path d="M31 12 L19 26 H28 L24 37 L37 22 H28 Z" fill="#FFFFFF"/>', 64, 48)

    # menu icons (white, ES tints them with the menu text color)
    mi = mk(ART, "menu")
    S = 'fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
    icons = {
        "brightness": f'<circle cx="32" cy="32" r="10" {S}/>' + "".join(
            f'<line x1="{32 + 17 * np.cos(a):.1f}" y1="{32 + 17 * np.sin(a):.1f}" '
            f'x2="{32 + 25 * np.cos(a):.1f}" y2="{32 + 25 * np.sin(a):.1f}" {S}/>'
            for a in np.linspace(0, 2 * np.pi, 9)[:-1]),
        "ui": "".join(f'<rect x="{x}" y="{y}" width="21" height="21" rx="6" {S}/>'
                      for x in (8, 35) for y in (8, 35)),
        "sound": f'<path d="M8 24 H18 L32 12 V52 L18 40 H8 Z" {S}/>'
                 f'<path d="M42 24 Q48 32 42 40" {S}/><path d="M49 16 Q61 32 49 48" {S}/>',
        "games": f'<path d="M20 18 H44 Q58 18 60 34 L61 44 Q62 52 54 52 Q49 52 45 44 L43 40 H21 L19 44 Q15 52 10 52 '
                 f'Q2 52 3 44 L4 34 Q6 18 20 18 Z" {S}/>'
                 f'<line x1="18" y1="27" x2="18" y2="35" {S}/><line x1="14" y1="31" x2="22" y2="31" {S}/>'
                 '<circle cx="44" cy="28" r="3" fill="#FFFFFF"/><circle cx="50" cy="34" r="3" fill="#FFFFFF"/>',
        "system": f'<rect x="16" y="16" width="32" height="32" rx="5" {S}/><rect x="26" y="26" width="12" height="12" '
                  'rx="2" fill="#FFFFFF"/>' + "".join(
                      f'<line x1="{p}" y1="6" x2="{p}" y2="12" {S}/><line x1="{p}" y1="52" x2="{p}" y2="58" {S}/>'
                      f'<line x1="6" y1="{p}" x2="12" y2="{p}" {S}/><line x1="52" y1="{p}" x2="58" y2="{p}" {S}/>'
                      for p in (24, 40)),
        "scraper": f'<circle cx="27" cy="27" r="16" {S}/><line x1="39" y1="39" x2="56" y2="56" {S}/>',
        "updates": f'<path d="M52 30 A20 20 0 1 0 46 46" {S}/><path d="M53 14 V30 H37" {S}/>',
        "options": "".join(f'<line x1="8" y1="{y}" x2="56" y2="{y}" {S}/><circle cx="{x}" cy="{y}" r="6" '
                           'fill="#FFFFFF"/>' for x, y in ((22, 16), (42, 32), (28, 48))),
        "advanced": f'<circle cx="32" cy="32" r="9" {S}/>' + "".join(
            f'<line x1="{32 + 15 * np.cos(a):.1f}" y1="{32 + 15 * np.sin(a):.1f}" '
            f'x2="{32 + 24 * np.cos(a):.1f}" y2="{32 + 24 * np.sin(a):.1f}" fill="none" stroke="#FFFFFF" '
            'stroke-width="9" stroke-linecap="round"/>' for a in np.linspace(0, 2 * np.pi, 7)[:-1])
                    + f'<circle cx="32" cy="32" r="17" {S}/>',
        "quit": f'<path d="M20 16 A21 21 0 1 0 44 16" {S}/><line x1="32" y1="6" x2="32" y2="30" {S}/>',
        "network": f'<path d="M8 26 Q32 4 56 26" {S}/><path d="M16 35 Q32 20 48 35" {S}/>'
                   f'<path d="M24 44 Q32 36 40 44" {S}/><circle cx="32" cy="52" r="4" fill="#FFFFFF"/>',
        "search": f'<circle cx="27" cy="27" r="16" {S}/><line x1="39" y1="39" x2="56" y2="56" {S}/>',
    }
    for k, v in icons.items():
        svg(os.path.join(mi, k + ".svg"), v)

    # switches / slider knob per accent (menus cannot tint them)
    sw = mk(ART, "switch")
    for name, hexc in ACCENTS.items():
        svg(os.path.join(sw, f"on_{name}.svg"),
            f'<rect x="2" y="6" width="76" height="40" rx="20" fill="#{hexc}"/>'
            '<circle cx="58" cy="26" r="15" fill="#FFFFFF"/>', 80, 52)
        svg(os.path.join(sw, f"knob_{name}.svg"),
            f'<circle cx="32" cy="32" r="26" fill="#{hexc}"/><circle cx="32" cy="32" r="11" fill="#FFFFFF"/>')
    for name, col in (("dark", "#5A5A66"), ("light", "#B4B6C0")):
        svg(os.path.join(sw, f"off_{name}.svg"),
            f'<rect x="4" y="8" width="72" height="36" rx="18" fill="none" stroke="{col}" stroke-width="4"/>'
            f'<circle cx="24" cy="26" r="11" fill="{col}"/>', 80, 52)


# --------------------------------------------------------------------------
# Missing box art placeholder
# --------------------------------------------------------------------------
def cartridge(draw, cx, cy, s, fill, width):
    # stylised cartridge outline with label + contacts
    x0, y0, x1, y1 = cx - 0.42 * s, cy - 0.5 * s, cx + 0.42 * s, cy + 0.5 * s
    draw.rounded_rectangle([x0, y0, x1, y1], radius=0.08 * s, outline=fill, width=width)
    draw.rounded_rectangle([x0 + 0.12 * s, y0 + 0.12 * s, x1 - 0.12 * s, cy + 0.12 * s], radius=0.05 * s,
                           outline=fill, width=width)
    for i in range(5):
        x = cx - 0.24 * s + i * 0.12 * s
        draw.line([x, y1 - 0.2 * s, x, y1 - 0.06 * s], fill=fill, width=width)
    draw.polygon([(x1, y0 + 0.18 * s), (x1 - 0.1 * s, y0 + 0.18 * s), (x1, y0 + 0.08 * s)], fill=fill)


def noart(path, dark, accent_rgb):
    W, H = 600, 800
    k = gfx.SS // 2
    big = (W * k, H * k)
    y = np.linspace(0, 1, big[1], dtype=np.float32)[:, None] * np.ones((1, big[0]), np.float32)
    if dark:
        top, bot, ink = np.array([30, 30, 38]), np.array([12, 12, 16]), (92, 92, 104, 255)
    else:
        top, bot, ink = np.array([252, 252, 254]), np.array([226, 228, 234]), (150, 152, 164, 255)
    rgb = (top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]) / 255.0
    img = gfx.to_img(np.concatenate([rgb, np.ones_like(y)[..., None]], -1), "RGBA")

    # diagonal hairlines
    lines = Image.new("RGBA", big, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lines)
    lc = (255, 255, 255, 10) if dark else (0, 0, 0, 10)
    for x in range(-big[1], big[0], 26 * k):
        ld.line([x, big[1], x + big[1], 0], fill=lc, width=2 * k)
    img.alpha_composite(lines)

    # accent glow behind the cartridge
    if accent_rgb:
        n = big[0]
        yy, xx = np.mgrid[0:big[1], 0:big[0]].astype(np.float32)
        rr = np.hypot(xx - big[0] / 2, yy - big[1] * 0.42) / (n * 0.42)
        a = np.clip(np.exp(-(rr ** 2) * 2.6), 0, 1) * (0.32 if dark else 0.22)
        glow = np.zeros((big[1], big[0], 4), np.float32)
        glow[..., :3] = np.array(accent_rgb) / 255.0
        glow[..., 3] = a
        img.alpha_composite(gfx.to_img(glow, "RGBA"))

    d = ImageDraw.Draw(img)
    icon = ink if not accent_rgb else tuple(list(accent_rgb) + [255])
    cartridge(d, big[0] / 2, big[1] * 0.42, 250 * k, icon, 9 * k)
    t1 = gfx.text_image("NO ARTWORK", F_DISPLAY, 70 * k, ink, tracking=6 * k)
    img.alpha_composite(t1, ((big[0] - t1.width) // 2, int(big[1] * 0.7)))
    t2 = gfx.text_image("SCRAPE THIS GAME TO ADD BOX ART", F_SEMI, 28 * k, ink[:3] + (170,), tracking=3 * k)
    img.alpha_composite(t2, ((big[0] - t2.width) // 2, int(big[1] * 0.7) + t1.height + 22 * k))
    m = gfx.rounded_mask(big, (0, 0, big[0], big[1]), 36 * k)
    img.putalpha(m)
    img.resize((W, H), Image.LANCZOS).save(path, optimize=True)


def build_noart():
    d = mk(ART, "noart")
    for cs in COLORSETS:
        accent = None if cs["multi"] else gfx.hex_rgb(cs["accent"])
        noart(os.path.join(d, f"{cs['name']}.png"), cs["dark"], accent)


# --------------------------------------------------------------------------
# Boot logo, game launch screen, ES splash
# --------------------------------------------------------------------------
def glow_tile_image(size, rgb, inner_draw):
    body, glow = tile_layers()
    comp = body.copy()
    comp.alpha_composite(gfx.tint(glow, rgb))
    layer = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    inner_draw(layer)
    comp.alpha_composite(layer)
    return comp.resize((size, size), Image.LANCZOS)


def r36s_mark(layer, rgb=(255, 255, 255)):
    t = gfx.text_image("R36S", F_DISPLAY, 210, (255, 255, 255, 255), tracking=2)
    t = gfx.fit(t, 170, 120)
    layer.alpha_composite(t, ((TILE - t.width) // 2, (TILE - t.height) // 2 - 4))


def play_mark(layer):
    d = ImageDraw.Draw(layer)
    c = TILE / 2
    d.polygon([(c - 28, c - 40), (c - 28, c + 40), (c + 42, c)], fill=(255, 255, 255, 255))


def screen_bg(rgb, w=640, h=480, pattern="dots"):
    img = Image.new("RGBA", (w, h), (7, 7, 10, 255))
    if pattern:
        tile = Image.open(os.path.join(ART, "bg", f"{pattern}.png"))
        tile = gfx.tint(tile, (255, 255, 255))
        a = np.asarray(tile).astype(np.float32)
        a[..., 3] *= 0.07
        tile = Image.fromarray(a.astype(np.uint8), "RGBA")
        pat = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for x in range(0, w, tile.width):
            for y in range(0, h, tile.height):
                pat.paste(tile, (x, y))
        img.alpha_composite(pat)
    rad = Image.open(os.path.join(ART, "bg", "radial.png")).resize((560, 560), Image.LANCZOS)
    rad = gfx.tint(rad, rgb)
    a = np.asarray(rad).astype(np.float32)
    a[..., 3] *= 0.30
    rad = Image.fromarray(a.astype(np.uint8), "RGBA")
    img.alpha_composite(rad, ((w - 560) // 2, (h - 560) // 2 - 30))
    vig = Image.open(os.path.join(ART, "bg", "vignette.png")).resize((w, h))
    img.alpha_composite(vig)
    return img


def centered_text(img, text, font, size, y, fill, tracking=0):
    t = gfx.text_image(text, font, size, fill, tracking)
    img.alpha_composite(t, ((img.width - t.width) // 2, y))
    return t


def build_extras(colors_by_accent):
    boot_d, load_d = mk(EXTRAS, "boot"), mk(EXTRAS, "launchimages")
    for name, hexc in colors_by_accent.items():
        rgb = gfx.hex_rgb(hexc)
        # boot logo (u-boot needs a 24-bit uncompressed BMP)
        img = screen_bg(rgb, pattern="dots")
        tile = glow_tile_image(250, rgb, r36s_mark)
        img.alpha_composite(tile, ((640 - 250) // 2, 78))
        centered_text(img, "N E O N G L O W", F_SEMI, 26, 352, (235, 235, 240, 255), tracking=3)
        centered_text(img, "R36S  ·  ARKOS  ·  DARKOS", F_SEMI, 17, 392, rgb + (255,), tracking=2)
        rgb_img = img.convert("RGB")
        sub = mk(boot_d, name)
        rgb_img.save(os.path.join(sub, "logo.bmp"))

        # game launch screen (/roms/launchimages/loading.jpg)
        img = screen_bg(rgb, pattern="plus")
        tile = glow_tile_image(210, rgb, play_mark)
        img.alpha_composite(tile, ((640 - 210) // 2, 92))
        centered_text(img, "LOADING", F_DISPLAY, 46, 318, (240, 240, 245, 255), tracking=10)
        # progress capsule (static)
        bar = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(bar)
        d.rounded_rectangle([220, 386, 420, 392], 3, fill=(255, 255, 255, 34))
        d.rounded_rectangle([220, 386, 340, 392], 3, fill=rgb + (255,))
        img.alpha_composite(bar)
        centered_text(img, "GET READY", F_SEMI, 16, 406, (150, 150, 162, 255), tracking=4)
        sub = mk(load_d, name)
        img.convert("RGB").save(os.path.join(sub, "loading.jpg"), quality=93)

    # ES splash (used for the ES boot "loading" screen); ES draws it on black.
    # Pure vector: nanosvg has no filters/text, so the glow is layered strokes and
    # the lettering is converted to paths.
    es_d = mk(EXTRAS, "es-resources")
    for name, hexc in colors_by_accent.items():
        sub = mk(es_d, name)
        with open(os.path.join(sub, "splash.svg"), "w") as f:
            f.write(splash_svg(hexc))


def squircle_path(cx, cy, r, n=5.0, steps=160):
    pts = []
    for i in range(steps):
        t = 2 * np.pi * i / steps
        c, s = np.cos(t), np.sin(t)
        x = cx + r * np.sign(c) * abs(c) ** (2 / n)
        y = cy + r * np.sign(s) * abs(s) ** (2 / n)
        pts.append(f"{x:.2f} {y:.2f}")
    return "M" + " L".join(pts) + " Z"


def splash_svg(hexc):
    p = squircle_path(256, 210, 150)
    glow = "".join(
        f'<path d="{p}" fill="none" stroke="#{hexc}" stroke-opacity="{op}" stroke-width="{w}" '
        'stroke-linejoin="round"/>'
        for w, op in ((44, 0.05), (32, 0.08), (22, 0.12), (14, 0.2), (8, 0.35)))
    body = ('<defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#1D1D25"/><stop offset="1" stop-color="#0A0A0E"/></linearGradient></defs>')
    inner = "".join(
        f'<path d="{p}" fill="none" stroke="#{hexc}" stroke-opacity="{op}" stroke-width="{w}" '
        'stroke-linejoin="round"/>'
        for w, op in ((40, 0.10), (24, 0.14), (12, 0.22)))
    mark = text_path("R36S", os.path.join(FONTS, "BarlowCondensed-Bold.ttf"), 256, 252, 150, "#FFFFFF")
    word = text_path("NEONGLOW", os.path.join(FONTS, "BarlowCondensed-SemiBold.ttf"), 256, 455, 54,
                     "#EDEDF2", tracking=14)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">'
            + body + glow
            + f'<path d="{p}" fill="url(#b)"/>' + inner
            + f'<path d="{p}" fill="none" stroke="#{hexc}" stroke-width="4"/>'
            + mark + word + "</svg>\n")


def main():
    fetch_carbon()
    if os.path.isdir(ART):
        shutil.rmtree(ART)
    mk(ART)
    shutil.copytree(FONTS, os.path.join(ART, "fonts"))
    build_backgrounds()
    build_ui()
    colors = build_tiles()
    build_noart()
    build_extras({k: v for k, v in ACCENTS.items()})
    with open(os.path.join(CACHE, "syscolors.txt"), "w") as f:
        for k, v in sorted(colors.items()):
            f.write(f"{k} {v}\n")
    print(f"assets: {len(colors)} systems")
    return colors


if __name__ == "__main__":
    main()
