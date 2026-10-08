"""Build the complete "VCR OSD" EmulationStation theme for 640x480 handhelds (R36S).

    python3 build_theme.py ../es-theme-vcr-osd

Generates fonts, hardware art, logos, timelines, UI images, the loading
screen and every theme XML file. Everything is pixel art drawn at an exact
integer scale, so nothing is resampled on a 640x480 screen.
"""
import math
import os
import shutil
import sys

from PIL import Image, ImageDraw

import build_font
import consoles
from pixelkit import Art, drk, hexc, lit, mixc
from pixeltext import draw_text, text_width
from systems import DEFAULT, SYSTEMS

SW, SH = 640, 480
OUT = None

# ----------------------------------------------------------------- palette
COLORSETS = {
    # name: (background, vignette edge, accent/dim text)
    "VCR BLUE": ("#000fc0", "#000a8c", "#8c9cff"),
    "DEEP NAVY": ("#00087c", "#000552", "#7c88e8"),
    "MIDNIGHT": ("#05053c", "#020222", "#6a6ad0"),
}
COLOR_FILES = {"VCR BLUE": "blue", "DEEP NAVY": "navy", "MIDNIGHT": "midnight"}
INK = "#f0f0f8"       # OSD white text
PAPER = "#e4e4ec"     # inverse highlight boxes
RESERVED_X = 448      # top-right corner kept clear for battery / clock
RESERVED_Y = 40

# Font sizes in px. The pixel font is pixel-perfect at multiples of 8.
FONT_SIZES = {"MEDIUM": 24, "SMALL": 16, "BIG": 32}
DESC_PX = 16
HELP_PX = 16


def fs(px):
    """ES fontSize is relative to screen height; nudge up so int() lands on px."""
    return f"{(px + 0.03) / SH:.5f}"


def nx(x):
    return f"{x / SW:.6f}".rstrip("0").rstrip(".") if x else "0"


def ny(y):
    return f"{y / SH:.6f}".rstrip("0").rstrip(".") if y else "0"


def xy(x, y):
    return f"{nx(x)} {ny(y)}"


def es_col(h, a="FF"):
    return h.lstrip("#").upper() + a


def P(*parts):
    return os.path.join(OUT, *parts)


def save(im, *parts):
    path = P(*parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, optimize=True)


# ============================================================ backgrounds
def base_bg(cs):
    bg, edge, _ = COLORSETS[cs]
    im = Image.new("RGBA", (SW, SH), hexc(bg))
    px = im.load()
    b, e = hexc(bg), hexc(edge)
    for y in range(SH):
        for x in range(SW):
            dx, dy = (x - SW / 2) / (SW / 2), (y - SH / 2) / (SH / 2)
            t = max(0.0, (dx * dx + dy * dy) ** 0.5 - 0.75) / 0.7
            t = min(1.0, t)
            # ordered dither keeps the vignette in clean pixel steps
            thr = ((x % 4) * 4 + (y % 4)) / 16.0
            q = math.floor(t * 4 + thr) / 4
            px[x, y] = tuple(int(b[i] + (e[i] - b[i]) * q) for i in range(3)) + (255,)
    return im


def dashed(d, x0, x1, y, col, dash=8, gap=6, h=2):
    x = x0
    while x < x1:
        d.rectangle([x, y, min(x + dash - 1, x1), y + h - 1], fill=col)
        x += dash + gap


def corner_brackets(d, x0, y0, x1, y1, col, L=12, t=2):
    for (cx, cy, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        d.rectangle(sorted_box(cx, cy, cx + sx * (L - 1), cy + sy * (t - 1)), fill=col)
        d.rectangle(sorted_box(cx, cy, cx + sx * (t - 1), cy + sy * (L - 1)), fill=col)


def sorted_box(x0, y0, x1, y1):
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def inverse_tag(im, x, y, text, bg, scale=2, padx=8, h=24):
    w = text_width(text, scale) + padx * 2
    ImageDraw.Draw(im).rectangle([x, y, x + w - 1, y + h - 1], fill=hexc(PAPER))
    draw_text(im, x + padx, y + (h - 7 * scale) // 2, text, scale, hexc(bg))
    return x + w


def help_bar(im, cs):
    d = ImageDraw.Draw(im)
    d.rectangle([8, 450, SW - 9, 475], fill=hexc(PAPER))


def bg_system(cs):
    bg, edge, dim = COLORSETS[cs]
    im = base_bg(cs)
    d = ImageDraw.Draw(im)
    inverse_tag(im, 16, 10, "▶ SELECT SYSTEM", bg)
    dashed(d, 16, SW - 17, 46, hexc(dim), 8, 6, 2)
    # stage floor under the hardware
    for x in range(60, SW - 60, 4):
        d.rectangle([x, 288, x + 1, 289], fill=hexc(dim))
    # navigation arrows either side of the logo
    draw_text(im, 20, 308, "◀", 4, hexc(INK))
    draw_text(im, SW - 20 - 20, 308, "▶", 4, hexc(INK))
    help_bar(im, cs)
    return im


def bg_gamelist(cs):
    bg, edge, dim = COLORSETS[cs]
    im = base_bg(cs)
    d = ImageDraw.Draw(im)
    dashed(d, 16, SW - 17, 44, hexc(dim), 8, 6, 2)
    corner_brackets(d, 10, 52, 336, 442, hexc(dim))
    # right panel: double OSD frame
    d.rectangle([344, 52, 627, 442], outline=hexc(INK), width=2)
    d.rectangle([348, 56, 623, 438], outline=hexc(dim), width=1)
    for x in range(352, 620, 4):
        d.rectangle([x, 318, x + 1, 319], fill=hexc(dim))
    draw_text(im, 356, 330, "RATING", 2, hexc(INK))
    draw_text(im, 586, 298, "SP", 2, hexc(dim))
    help_bar(im, cs)
    return im


def bg_plain(cs):
    im = base_bg(cs)
    dashed(ImageDraw.Draw(im), 16, SW - 17, 44, hexc(COLORSETS[cs][2]), 8, 6, 2)
    help_bar(im, cs)
    return im


def scanlines():
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(1, SH, 2):
        d.line([(0, y), (SW, y)], fill=(0, 0, 24, 46))
    return im


# ============================================================ small UI parts
def star(filled):
    pts = [".....##.....", ".....##.....", "....####....", "############",
           ".##########.", "..########..", "...######...", "...######...",
           "..###..###..", "..##....##..", ".##......##.", "............"]
    im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for r, row in enumerate(pts):
        for c, v in enumerate(row):
            if v == "#":
                edge = (r == 0 or c == 0 or pts[r - 1][c] != "#" or pts[r][c - 1] != "#"
                        or c == 11 or pts[r][c + 1] != "#" or r == 11 or pts[r + 1][c] != "#")
                if filled:
                    col = hexc("#ffe040") if not edge else hexc("#f0f0f8")
                else:
                    col = hexc("#f0f0f8") if edge else None
                if col:
                    d.rectangle([c * 2, r * 2, c * 2 + 1, r * 2 + 1], fill=col)
    return im


def no_signal():
    w, h = 262, 244
    im = Image.new("RGBA", (w, h), hexc("#000000"))
    d = ImageDraw.Draw(im)
    bars = ["#c0c0c0", "#c0c000", "#00c0c0", "#00c000", "#c000c0", "#c00000", "#0000c0"]
    bw = w / 7
    for i, c in enumerate(bars):
        d.rectangle([int(i * bw), 0, int((i + 1) * bw) - 1, int(h * 0.66)], fill=hexc(c))
    rev = ["#0000c0", "#131313", "#c000c0", "#131313", "#00c0c0", "#131313", "#c0c0c0"]
    for i, c in enumerate(rev):
        d.rectangle([int(i * bw), int(h * 0.66) + 1, int((i + 1) * bw) - 1, int(h * 0.75)], fill=hexc(c))
    for i, c in enumerate(["#00214c", "#ffffff", "#32006a", "#131313"]):
        d.rectangle([int(i * w / 5.5), int(h * 0.75) + 1, int((i + 1) * w / 5.5) - 1, h - 1], fill=hexc(c))
    tw = text_width("NO SIGNAL", 3)
    d.rectangle([(w - tw) // 2 - 8, h // 3 - 14, (w + tw) // 2 + 8, h // 3 + 22], fill=hexc("#000fc0"))
    draw_text(im, (w - tw) // 2, h // 3 - 3, "NO SIGNAL", 3, hexc(INK))
    return im


def nine_patch(bg, border=INK, inner=None, size=48, fill_alpha=255):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, size - 1, size - 1], fill=hexc(bg, fill_alpha))
    d.rectangle([2, 2, size - 3, size - 3], outline=hexc(border), width=2)
    if inner:
        d.rectangle([6, 6, size - 7, size - 7], outline=hexc(inner), width=1)
    return im


def switch_img(on, bg):
    label = "ON" if on else "OFF"
    w = text_width("OFF", 2) + 16
    im = Image.new("RGBA", (w, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if on:
        d.rectangle([0, 0, w - 1, 23], fill=hexc(PAPER))
        draw_text(im, (w - text_width(label, 2)) // 2, 5, label, 2, hexc(bg))
    else:
        d.rectangle([0, 0, w - 1, 23], outline=hexc(INK), width=2)
        draw_text(im, (w - text_width(label, 2)) // 2, 5, label, 2, hexc(INK))
    return im


def slider_knob():
    im = Image.new("RGBA", (12, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 11, 23], fill=hexc(PAPER))
    d.rectangle([4, 4, 7, 19], fill=hexc("#8c9cff"))
    return im


def osd_arrow(ch):
    im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    draw_text(im, 1, 3, ch, 3, hexc(INK))
    return im


# ============================================================ logos & timeline
def logo(key, scale_px=4):
    name, maker, year, kind, cols = SYSTEMS.get(key, DEFAULT)
    w, h = 480, 64
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    scale = scale_px
    while scale > 2 and text_width(name, scale) > w - 8:
        scale -= 1
    lines = [name]
    if text_width(name, scale) > w - 8:
        words = name.split()
        lines = [" ".join(words[: len(words) // 2]), " ".join(words[len(words) // 2:])]
    th = len(lines) * 7 * scale + (len(lines) - 1) * scale * 2
    y = (48 - th) // 2 + 2
    maxw = 0
    for line in lines:
        tw = text_width(line, scale)
        maxw = max(maxw, tw)
        draw_text(im, (w - tw) // 2, y, line, scale, hexc(INK), shadow=hexc("#000040", 200),
                  shadow_off=(1, 1))
        y += 7 * scale + scale * 2
    # brand stripe: four colour blocks under the name, OSD style
    seg = max(12, min(48, (maxw + 12) // 4))
    sx = (w - seg * 4) // 2
    for i, c in enumerate(cols):
        ImageDraw.Draw(im).rectangle([sx + i * seg, 54, sx + (i + 1) * seg - 3, 59], fill=hexc(c))
    return im


def timeline(key):
    name, maker, year, kind, cols = SYSTEMS.get(key, DEFAULT)
    w, h = 400, 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0, y1 = 12, 25
    bx0, bx1 = 70, w - 70
    lo, hi = 1975, 2025
    t = (min(max(year, lo), hi) - lo) / (hi - lo)
    mx = int(bx0 + 4 + t * (bx1 - bx0 - 8))
    d.rectangle([bx0, y0, bx1, y1], outline=hexc(INK), width=2)
    d.rectangle([bx0 + 4, y0 + 4, mx, y1 - 4], fill=hexc(PAPER))
    for i in range(1, 5):
        tx = bx0 + i * (bx1 - bx0) // 5
        d.rectangle([tx, y0 + 2, tx + 1, y0 + 4], fill=hexc(INK))
    draw_text(im, mx - 5, 1, "▼", 2, hexc(INK))
    draw_text(im, 0, y0 + 1, str(lo), 2, hexc(INK))
    draw_text(im, bx1 + 12, y0 + 1, str(hi), 2, hexc(INK))
    return im


# ============================================================ loading screen
HOURGLASS = [
    "################",
    "################",
    ".#............#.",
    ".#............#.",
    ".#............#.",
    "..#..........#..",
    "...#........#...",
    "....#......#....",
    ".....#....#.....",
    "......#..#......",
    "......#..#......",
    ".....#....#.....",
    "....#......#....",
    "...#........#...",
    "..#..........#..",
    ".#............#.",
    ".#............#.",
    ".#............#.",
    "################",
    "################",
]


def hourglass(frame=0, frames=8, scale=8, bg="#000fc0"):
    """Hourglass with the sand level set by frame/frames."""
    rows, cols = len(HOURGLASS), len(HOURGLASS[0])
    im = Image.new("RGBA", (cols * scale + 8, rows * scale + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    t = frame / max(1, frames - 1)
    sand = hexc("#ffd84a")
    sand_d = hexc("#e0a020")
    glass = hexc("#9cc8ff")
    frame_c = hexc(PAPER)

    def cell(c, r, col):
        d.rectangle([4 + c * scale, 4 + r * scale, 4 + c * scale + scale - 1,
                     4 + r * scale + scale - 1], fill=col)

    # inside extents per row
    inside = []
    for r, row in enumerate(HOURGLASS):
        idx = [i for i, v in enumerate(row) if v == "#"]
        if len(idx) == 2 and idx[1] - idx[0] > 1:
            inside.append((r, idx[0] + 1, idx[1] - 1))
    top = [x for x in inside if x[0] < 10]
    bot = [x for x in inside if x[0] >= 10]
    top_cells = sum(c1 - c0 + 1 for _, c0, c1 in top)
    bot_cells = sum(c1 - c0 + 1 for _, c0, c1 in bot)
    total = min(top_cells, bot_cells) * 0.8
    remaining = int(total * (1 - t))
    fallen = int(total * t)
    # glass tint
    for r, c0, c1 in inside:
        for c in range(c0, c1 + 1):
            cell(c, r, mixc(bg, glass, 0.18))
    # upper sand drains from the top down (fill from the neck upwards)
    left = remaining
    for r, c0, c1 in sorted(top, key=lambda x: -x[0]):
        for c in range(c0, c1 + 1):
            if left > 0:
                cell(c, r, sand if (r + c) % 3 else sand_d)
                left -= 1
    # lower sand piles up from the bottom
    left = fallen
    for r, c0, c1 in sorted(bot, key=lambda x: -x[0]):
        width = c1 - c0 + 1
        take = min(width, left)
        start = c0 + (width - take) // 2
        for c in range(start, start + take):
            cell(c, r, sand if (r + c) % 3 else sand_d)
        left -= take
        if left <= 0:
            break
    # falling stream through the neck
    if 0 < t < 1:
        for r in range(9, 17):
            if (r + frame) % 2 == 0:
                cell(7 + (r % 2 == 0), r, sand)
    for r, row in enumerate(HOURGLASS):
        for c, v in enumerate(row):
            if v == "#":
                cell(c, r, frame_c if r not in (0, 19) else hexc("#c8a060"))
    # glass highlights
    for r in (3, 4, 15, 16):
        cell(2, r, hexc("#ffffff"))
    # wooden caps detail
    for c in range(0, 16, 3):
        cell(c, 1, hexc("#a07a40"))
        cell(c, 18, hexc("#a07a40"))
    return im


def loading_screen(cs, frame=7, frames=8):
    bg, edge, dim = COLORSETS[cs]
    im = base_bg(cs)
    d = ImageDraw.Draw(im)
    inverse_tag(im, 16, 10, "▶ PLAY", bg)
    dashed(d, 16, SW - 17, 46, hexc(dim), 8, 6, 2)
    hg = hourglass(frame if frames > 1 else 0, frames, 8, bg)
    hx, hy = (SW - hg.width) // 2, 70
    shadow = Image.new("RGBA", hg.size, (0, 0, 40, 120))
    im.paste(shadow, (hx + 8, hy + 8), hg)
    im.alpha_composite(hg, (hx, hy))
    dots = "." * (frame % 4)
    word = "LOADING"
    tw = text_width(word + "...", 5)
    tx = (SW - tw) // 2
    draw_text(im, tx, 266, word + dots, 5, hexc(INK), shadow=hexc("#000040"), shadow_off=(1, 1))
    # segmented progress bar like a VCR tape counter
    segs = 24
    filled = int(round(segs * (frame + 1) / frames)) if frames > 1 else segs
    bx = (SW - segs * 18) // 2
    for i in range(segs):
        x = bx + i * 18
        if i < filled:
            d.rectangle([x, 330, x + 9, 349], fill=hexc(PAPER))
        else:
            d.rectangle([x, 339, x + 9, 340], fill=hexc(INK))
    counter = "0:%02d:%02d" % (frame // 2, (frame * 7) % 60)
    draw_text(im, SW - 16 - text_width(counter, 2), 372, counter, 2, hexc(INK))
    draw_text(im, SW - 16 - text_width("SP", 2), 392, "SP", 2, hexc(INK))
    draw_text(im, 16, 372, "PLEASE WAIT", 2, hexc(INK))
    draw_text(im, 16, 392, "▶ PLAY", 2, hexc(dim))
    d.rectangle([8, 450, SW - 9, 475], fill=hexc(PAPER))
    draw_text(im, 16, 456, "INSERTING TAPE  ▶▶", 2, hexc(bg))
    return im


# ============================================================ XML
FONT_FILES = {"CHUNKY VCR": "OSDTape-Chunky.ttf", "CLEAN OSD": "OSDTape-Regular.ttf"}


def font_path(style="CHUNKY VCR"):
    return f"./../_art/fonts/{FONT_FILES[style]}"


GL_VIEWS = "basic,detailed,video"
TEXT_ELEMS_SYSTEM = ["sysTag", "sysInfo", "systemInfo"]


def x_main():
    bg = COLORSETS["VCR BLUE"][0]
    dim = COLORSETS["VCR BLUE"][2]
    fp = font_path()
    hide = f"<pos>2 2</pos><size>0.01 0.01</size>"
    lbls = ["md_lbl_rating", "md_lbl_releasedate", "md_lbl_developer", "md_lbl_publisher",
            "md_lbl_genre", "md_lbl_players", "md_lbl_lastplayed", "md_lbl_playcount"]
    fields = ["md_releasedate", "md_developer", "md_publisher", "md_genre", "md_players",
              "md_lastplayed", "md_playcount", "md_name", "md_marquee"]
    hidden = "\n".join(f'    <text name="{n}">{hide}</text>' for n in lbls)
    hidden += "\n" + "\n".join(
        f'    <{"image" if n == "md_marquee" else ("datetime" if n in ("md_releasedate", "md_lastplayed") else "text")} name="{n}">{hide}</{"image" if n == "md_marquee" else ("datetime" if n in ("md_releasedate", "md_lastplayed") else "text")}>'
        for n in fields)
    return f"""<!--
  VCR OSD - EmulationStation theme for 640x480 handhelds (R36S / ArkOS / dArkOS)
  Shared layout. Every system folder sets its variables and includes this file.
  Positions are in screen fractions; the comments give the pixel value at 640x480.
  The top-right corner (x > {RESERVED_X}px, y < {RESERVED_Y}px) stays empty for the battery/clock.
-->
<theme>
  <formatVersion>7</formatVersion>

  <!-- ====================================================== SYSTEM VIEW -->
  <view name="system">
    <image name="background" extra="true">
      <pos>0 0</pos><size>1 1</size>
      <path>./../_art/ui/bg_system_blue.png</path>
      <zIndex>0</zIndex>
    </image>
    <image name="console" extra="true">
      <!-- 360x240 hardware art at (140,46): drawn at its native size, no blur -->
      <pos>{xy(140, 46)}</pos><size>{xy(360, 240)}</size>
      <path>./../_art/consoles/${{sysArt}}.png</path>
      <zIndex>10</zIndex>
    </image>
    <carousel name="systemcarousel">
      <type>horizontal</type>
      <pos>{xy(0, 292)}</pos>
      <size>{xy(640, 64)}</size>
      <logoSize>{xy(480, 64)}</logoSize>
      <logoScale>1.0</logoScale>
      <maxLogoCount>1</maxLogoCount>
      <logoAlignment>center</logoAlignment>
      <color>00000000</color>
      <zIndex>40</zIndex>
    </carousel>
    <image name="logo">
      <path>./../_art/logos/${{sysArt}}.png</path>
    </image>
    <text name="logoText">
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(32)}</fontSize>
      <color>{es_col(INK)}</color>
      <forceUppercase>true</forceUppercase>
    </text>
    <text name="sysInfo" extra="true">
      <!-- maker and release year, e.g. NINTENDO * 1990 * CONSOLE -->
      <text>${{sysMaker}} · ${{sysYear}} · ${{sysKind}}</text>
      <pos>{xy(16, 360)}</pos><size>{xy(608, 22)}</size>
      <alignment>center</alignment>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(16)}</fontSize>
      <color>{es_col(INK)}</color>
      <forceUppercase>true</forceUppercase>
      <zIndex>45</zIndex>
    </text>
    <text name="systemInfo">
      <pos>{xy(16, 384)}</pos><size>{xy(608, 22)}</size>
      <alignment>center</alignment>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(16)}</fontSize>
      <color>{es_col(dim)}</color>
      <backgroundColor>00000000</backgroundColor>
      <forceUppercase>true</forceUppercase>
      <zIndex>45</zIndex>
    </text>
    <image name="timeline" extra="true">
      <!-- BEGIN/END tape counter bar; the marker sits on the release year -->
      <pos>{xy(120, 406)}</pos><size>{xy(400, 40)}</size>
      <path>./../_art/timeline/${{sysArt}}.png</path>
      <zIndex>45</zIndex>
    </image>
    <helpsystem name="help">
      <pos>{xy(16, 463)}</pos>
      <origin>0 0.5</origin>
      <textColor>{es_col(bg)}</textColor>
      <iconColor>{es_col(bg)}</iconColor>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(HELP_PX)}</fontSize>
    </helpsystem>
  </view>

  <!-- ===================================================== GAMELIST VIEWS -->
  <view name="{GL_VIEWS}">
    <image name="background" extra="true">
      <pos>0 0</pos><size>1 1</size>
      <path>./../_art/ui/bg_gamelist_blue.png</path>
      <zIndex>0</zIndex>
    </image>
    <text name="sysTag" extra="true">
      <!-- inverse OSD tag with the system name, like the highlighted AUTO box -->
      <text>▶ ${{sysName}}</text>
      <pos>{xy(16, 10)}</pos><size>${{tagW}} {ny(24)}</size>
      <alignment>center</alignment>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(16)}</fontSize>
      <color>{es_col(bg)}</color>
      <backgroundColor>{es_col(PAPER)}</backgroundColor>
      <forceUppercase>true</forceUppercase>
      <zIndex>50</zIndex>
    </text>
    <textlist name="gamelist">
      <!-- left column: x 16..330, y 56..438 -->
      <pos>{xy(16, 56)}</pos><size>{xy(314, 382)}</size>
      <selectorColor>{es_col(PAPER)}</selectorColor>
      <selectedColor>{es_col(bg)}</selectedColor>
      <primaryColor>{es_col(INK)}</primaryColor>
      <secondaryColor>{es_col(dim)}</secondaryColor>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(24)}</fontSize>
      <lineSpacing>1.5</lineSpacing>
      <alignment>left</alignment>
      <horizontalMargin>{nx(8)}</horizontalMargin>
      <forceUppercase>true</forceUppercase>
      <zIndex>20</zIndex>
    </textlist>
    <image name="md_image">
      <!-- box art: top two thirds of the right panel (x 352..620, y 60..312) -->
      <pos>{xy(486, 186)}</pos>
      <origin>0.5 0.5</origin>
      <maxSize>{xy(262, 244)}</maxSize>
      <default>./../_art/ui/no_signal.png</default>
      <zIndex>30</zIndex>
    </image>
    <video name="md_video">
      <pos>{xy(486, 186)}</pos>
      <origin>0.5 0.5</origin>
      <maxSize>{xy(262, 244)}</maxSize>
      <delay>1.5</delay>
      <showSnapshotNoVideo>true</showSnapshotNoVideo>
      <showSnapshotDelay>true</showSnapshotDelay>
      <default>./../_art/ui/no_signal.png</default>
      <zIndex>31</zIndex>
    </video>
    <rating name="md_rating">
      <!-- bottom third: five 24px pixel stars next to the RATING label -->
      <pos>{xy(446, 324)}</pos><size>{xy(120, 24)}</size>
      <filledPath>./../_art/ui/star_filled.png</filledPath>
      <unfilledPath>./../_art/ui/star_unfilled.png</unfilledPath>
      <zIndex>40</zIndex>
    </rating>
    <text name="md_description">
      <!-- bottom third: small 16px text, scrolls automatically -->
      <pos>{xy(356, 354)}</pos><size>{xy(262, 82)}</size>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(DESC_PX)}</fontSize>
      <lineSpacing>1.25</lineSpacing>
      <color>{es_col(INK)}</color>
      <alignment>left</alignment>
      <zIndex>40</zIndex>
    </text>
{hidden}
    <helpsystem name="help">
      <pos>{xy(16, 463)}</pos>
      <origin>0 0.5</origin>
      <textColor>{es_col(bg)}</textColor>
      <iconColor>{es_col(bg)}</iconColor>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(HELP_PX)}</fontSize>
    </helpsystem>
  </view>

  <view name="basic">
    <!-- the basic view has no box art, so the console fills the art window -->
    <image name="consoleSmall" extra="true">
      <pos>{xy(486, 186)}</pos><origin>0.5 0.5</origin><size>{xy(240, 160)}</size>
      <path>./../_art/consoles/small/${{sysArt}}.png</path>
      <zIndex>30</zIndex>
    </image>
  </view>

  <view name="grid">
    <image name="background" extra="true">
      <pos>0 0</pos><size>1 1</size>
      <path>./../_art/ui/bg_plain_blue.png</path>
    </image>
    <imagegrid name="gamegrid">
      <pos>{xy(16, 56)}</pos><size>{xy(608, 382)}</size>
      <margin>{xy(12, 12)}</margin>
      <padding>{xy(12, 12)}</padding>
    </imagegrid>
    <gridtile name="default">
      <size>{xy(110, 120)}</size>
      <backgroundColor>00000000</backgroundColor>
    </gridtile>
    <gridtile name="selected">
      <backgroundColor>{es_col(PAPER)}</backgroundColor>
    </gridtile>
    <helpsystem name="help">
      <pos>{xy(16, 463)}</pos><origin>0 0.5</origin>
      <textColor>{es_col(bg)}</textColor><iconColor>{es_col(bg)}</iconColor>
      <fontPath>{fp}</fontPath><fontSize>{fs(HELP_PX)}</fontSize>
    </helpsystem>
  </view>

  <!-- ======================================== SETTINGS MENU = SAME OSD LOOK -->
  <view name="menu">
    <menuBackground name="menubg">
      <color>{es_col(bg)}</color>
      <path>./../_art/ui/menu_frame_blue.png</path>
      <cornerSize>16 16</cornerSize>
    </menuBackground>
    <menuText name="menutitle">
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(32)}</fontSize>
      <color>{es_col(INK)}</color>
    </menuText>
    <menuText name="menutext">
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(24)}</fontSize>
      <color>{es_col(INK)}</color>
      <separatorColor>{es_col(dim, "80")}</separatorColor>
      <selectedColor>{es_col(bg)}</selectedColor>
      <selectorColor>{es_col(PAPER)}</selectorColor>
    </menuText>
    <menuText name="menutextsmall">
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(16)}</fontSize>
      <color>{es_col(dim)}</color>
      <selectedColor>{es_col(bg)}</selectedColor>
    </menuText>
    <menuText name="menufooter">
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(16)}</fontSize>
      <color>{es_col(dim)}</color>
    </menuText>
    <menuSwitch name="menuswitch">
      <pathOn>./../_art/ui/switch_on_blue.png</pathOn>
      <pathOff>./../_art/ui/switch_off.png</pathOff>
    </menuSwitch>
    <menuSlider name="menuslider">
      <path>./../_art/ui/slider_knob.png</path>
    </menuSlider>
    <menuButton name="menubutton">
      <path>./../_art/ui/button_blue.png</path>
      <filledPath>./../_art/ui/button_filled.png</filledPath>
    </menuButton>
    <menuTextEdit name="menutextedit">
      <inactive>./../_art/ui/textinput_blue.png</inactive>
      <active>./../_art/ui/textinput_active_blue.png</active>
    </menuTextEdit>
    <menuIcons name="menuicons">
      <iconOptionListArrow>./../_art/ui/arrow_down.png</iconOptionListArrow>
      <iconArrow>./../_art/ui/arrow_right.png</iconArrow>
    </menuIcons>
  </view>

  <!-- ============================================ SPLASH / LOADING SCREEN -->
  <view name="splash">
    <image name="background">
      <pos>0 0</pos><size>1 1</size>
      <path>./../_art/loading/loading_blue.png</path>
    </image>
    <image name="logo">
      <pos>2 2</pos><size>0.01 0.01</size>
    </image>
    <text name="label">
      <pos>{xy(16, 406)}</pos><size>{xy(608, 22)}</size>
      <alignment>left</alignment>
      <fontPath>{fp}</fontPath>
      <fontSize>{fs(16)}</fontSize>
      <color>{es_col(INK)}</color>
    </text>
  </view>
</theme>
"""


def x_colorset(cs):
    bg, edge, dim = COLORSETS[cs]
    c = COLOR_FILES[cs]
    help_ = f"""    <helpsystem name="help">
      <textColor>{es_col(bg)}</textColor>
      <iconColor>{es_col(bg)}</iconColor>
    </helpsystem>"""
    return f"""<!-- Colour set: {cs} -->
<theme>
  <formatVersion>7</formatVersion>
  <view name="system">
    <image name="background"><path>./../_art/ui/bg_system_{c}.png</path></image>
    <text name="systemInfo"><color>{es_col(dim)}</color></text>
{help_}
  </view>
  <view name="{GL_VIEWS}">
    <image name="background"><path>./../_art/ui/bg_gamelist_{c}.png</path></image>
    <text name="sysTag"><color>{es_col(bg)}</color></text>
    <textlist name="gamelist">
      <selectedColor>{es_col(bg)}</selectedColor>
      <secondaryColor>{es_col(dim)}</secondaryColor>
    </textlist>
{help_}
  </view>
  <view name="grid">
    <image name="background"><path>./../_art/ui/bg_plain_{c}.png</path></image>
{help_}
  </view>
  <view name="menu">
    <menuBackground name="menubg">
      <color>{es_col(bg)}</color>
      <path>./../_art/ui/menu_frame_{c}.png</path>
    </menuBackground>
    <menuText name="menutext">
      <separatorColor>{es_col(dim, "80")}</separatorColor>
      <selectedColor>{es_col(bg)}</selectedColor>
    </menuText>
    <menuText name="menutextsmall">
      <color>{es_col(dim)}</color>
      <selectedColor>{es_col(bg)}</selectedColor>
    </menuText>
    <menuText name="menufooter"><color>{es_col(dim)}</color></menuText>
    <menuSwitch name="menuswitch">
      <pathOn>./../_art/ui/switch_on_{c}.png</pathOn>
    </menuSwitch>
    <menuButton name="menubutton"><path>./../_art/ui/button_{c}.png</path></menuButton>
    <menuTextEdit name="menutextedit">
      <inactive>./../_art/ui/textinput_{c}.png</inactive>
      <active>./../_art/ui/textinput_active_{c}.png</active>
    </menuTextEdit>
  </view>
  <view name="splash">
    <image name="background"><path>./../_art/loading/loading_{c}.png</path></image>
  </view>
</theme>
"""


def x_fontsize(name):
    px = FONT_SIZES[name]
    title = {16: 24, 24: 32, 32: 32}[px]
    spacing = {16: 1.6, 24: 1.5, 32: 1.4}[px]
    return f"""<!-- Font size: {name} ({px}px list and menu text; descriptions stay small at {DESC_PX}px) -->
<theme>
  <formatVersion>7</formatVersion>
  <view name="{GL_VIEWS}">
    <textlist name="gamelist">
      <fontSize>{fs(px)}</fontSize>
      <lineSpacing>{spacing}</lineSpacing>
    </textlist>
  </view>
  <view name="menu">
    <menuText name="menutitle"><fontSize>{fs(title)}</fontSize></menuText>
    <menuText name="menutext"><fontSize>{fs(px)}</fontSize></menuText>
  </view>
</theme>
"""


def x_fontstyle(style):
    fp = font_path(style)
    sysv = "\n".join(f'    <text name="{n}"><fontPath>{fp}</fontPath></text>'
                     for n in ["logoText", "sysInfo", "systemInfo"])
    help_ = f'    <helpsystem name="help"><fontPath>{fp}</fontPath></helpsystem>'
    menu = "\n".join(f'    <menuText name="{n}"><fontPath>{fp}</fontPath></menuText>'
                     for n in ["menutitle", "menutext", "menutextsmall", "menufooter"])
    return f"""<!-- Font style: {style} -->
<theme>
  <formatVersion>7</formatVersion>
  <view name="system">
{sysv}
{help_}
  </view>
  <view name="{GL_VIEWS}">
    <text name="sysTag"><fontPath>{fp}</fontPath></text>
    <textlist name="gamelist"><fontPath>{fp}</fontPath></textlist>
    <text name="md_description"><fontPath>{fp}</fontPath></text>
{help_}
  </view>
  <view name="grid">
{help_}
  </view>
  <view name="menu">
{menu}
  </view>
  <view name="splash">
    <text name="label"><fontPath>{fp}</fontPath></text>
  </view>
</theme>
"""


def x_textcase(upper):
    v = "true" if upper else "false"
    return f"""<!-- Game list letter case: {"ALL CAPS" if upper else "AS SCRAPED"} -->
<theme>
  <formatVersion>7</formatVersion>
  <view name="{GL_VIEWS}">
    <textlist name="gamelist"><forceUppercase>{v}</forceUppercase></textlist>
  </view>
</theme>
"""


def x_scanlines(on):
    if not on:
        return "<!-- CRT scanlines: OFF -->\n<theme>\n  <formatVersion>7</formatVersion>\n</theme>\n"
    el = """    <image name="scanlines" extra="true">
      <pos>0 0</pos><size>1 1</size>
      <path>./../_art/ui/scanlines.png</path>
      <zIndex>90</zIndex>
    </image>"""
    return f"""<!-- CRT scanlines: ON -->
<theme>
  <formatVersion>7</formatVersion>
  <view name="system">
{el}
  </view>
  <view name="{GL_VIEWS}">
{el}
  </view>
</theme>
"""


SUBSETS = [
    ("colorset", "COLOR SET", [(n, f"color-{COLOR_FILES[n]}.xml") for n in COLORSETS]),
    ("fontsize", "FONT SIZE", [(n, f"fontsize-{n.lower()}.xml") for n in FONT_SIZES]),
    ("fontstyle", "FONT STYLE", [("CHUNKY VCR", "fontstyle-chunky.xml"),
                                 ("CLEAN OSD", "fontstyle-clean.xml")]),
    ("textcase", "LETTER CASE", [("ALL CAPS", "case-upper.xml"), ("AS SCRAPED", "case-mixed.xml")]),
    ("scanlines", "CRT SCANLINES", [("OFF", "scanlines-off.xml"), ("ON", "scanlines-on.xml")]),
]


def x_system(key, rel="./.."):
    name, maker, year, kind, _ = SYSTEMS.get(key, DEFAULT)
    tag = "▶ " + name
    tag_w = (len(tag) * 12 + 18) / SW
    art = key if key in consoles.ART else "default"
    subsets = []
    for sid, disp, items in SUBSETS:
        inc = "\n".join(f'    <include name="{n}">{rel}/_inc/{f}</include>' for n, f in items)
        subsets.append(f'  <subset name="{sid}" displayName="{disp}">\n{inc}\n  </subset>')
    subs = "\n".join(subsets)
    esc = lambda s: s.replace("&", "&amp;")
    return f"""<!-- VCR OSD theme: {esc(name)} -->
<theme>
  <formatVersion>7</formatVersion>
  <variables>
    <sysArt>{art}</sysArt>
    <sysName>{esc(name)}</sysName>
    <sysMaker>{esc(maker)}</sysMaker>
    <sysYear>{year}</sysYear>
    <sysKind>{esc(kind)}</sysKind>
    <tagW>{tag_w:.5f}</tagW>
  </variables>
  <include>{rel}/_inc/main.xml</include>
{subs}
</theme>
"""


# ============================================================ build
def build(out):
    global OUT
    OUT = out
    for sub in ("_art", "_inc"):
        shutil.rmtree(P(sub), ignore_errors=True)
    os.makedirs(P("_art", "fonts"), exist_ok=True)
    build_font.build(P("_art", "fonts", "OSDTape-Chunky.ttf"), True)
    build_font.build(P("_art", "fonts", "OSDTape-Regular.ttf"), False)

    # UI per colour set
    for cs, c in COLOR_FILES.items():
        bg = COLORSETS[cs][0]
        save(bg_system(cs), "_art", "ui", f"bg_system_{c}.png")
        save(bg_gamelist(cs), "_art", "ui", f"bg_gamelist_{c}.png")
        save(bg_plain(cs), "_art", "ui", f"bg_plain_{c}.png")
        save(nine_patch(bg, INK, COLORSETS[cs][2]), "_art", "ui", f"menu_frame_{c}.png")
        save(nine_patch(bg, INK), "_art", "ui", f"button_{c}.png")
        save(nine_patch(bg, COLORSETS[cs][2]), "_art", "ui", f"textinput_{c}.png")
        save(nine_patch(bg, INK, PAPER), "_art", "ui", f"textinput_active_{c}.png")
        save(switch_img(True, bg), "_art", "ui", f"switch_on_{c}.png")
        save(loading_screen(cs, 4, 8), "_art", "loading", f"loading_{c}.png")
    save(nine_patch(PAPER, INK), "_art", "ui", "button_filled.png")
    save(switch_img(False, "#000fc0"), "_art", "ui", "switch_off.png")
    save(slider_knob(), "_art", "ui", "slider_knob.png")
    save(osd_arrow("▼"), "_art", "ui", "arrow_down.png")
    save(osd_arrow("▶"), "_art", "ui", "arrow_right.png")
    save(star(True), "_art", "ui", "star_filled.png")
    save(star(False), "_art", "ui", "star_unfilled.png")
    save(no_signal(), "_art", "ui", "no_signal.png")
    save(scanlines(), "_art", "ui", "scanlines.png")

    # animated loading screen (GIF) + still copy at the canonical name
    frames = [loading_screen("VCR BLUE", f, 8).convert("RGB") for f in range(8)]
    frames[0].save(P("_art", "loading", "loading.gif"), save_all=True,
                   append_images=frames[1:], duration=160, loop=0, optimize=True)
    shutil.copy(P("_art", "loading", "loading_blue.png"), P("_art", "loading", "loading.png"))

    # hardware art, logos and timelines
    keys = sorted(set(SYSTEMS) | {"default"})
    arts = sorted(set(consoles.ART))
    for k in arts:
        a = Art()
        consoles.ART[k](a)
        save(a.render(3), "_art", "consoles", f"{k}.png")
        save(a.render(2), "_art", "consoles", "small", f"{k}.png")
    for k in keys:
        save(logo(k), "_art", "logos", f"{k}.png")
        save(timeline(k), "_art", "timeline", f"{k}.png")
    for k in arts:  # art-only keys still need a logo/timeline for the default
        if k not in SYSTEMS:
            save(logo(k), "_art", "logos", f"{k}.png")
            save(timeline(k), "_art", "timeline", f"{k}.png")

    # XML
    os.makedirs(P("_inc"), exist_ok=True)

    def w(path, text):
        with open(P(*path), "w", encoding="utf-8") as f:
            f.write(text)

    w(("_inc", "main.xml"), x_main())
    for cs, c in COLOR_FILES.items():
        w(("_inc", f"color-{c}.xml"), x_colorset(cs))
    for n in FONT_SIZES:
        w(("_inc", f"fontsize-{n.lower()}.xml"), x_fontsize(n))
    w(("_inc", "fontstyle-chunky.xml"), x_fontstyle("CHUNKY VCR"))
    w(("_inc", "fontstyle-clean.xml"), x_fontstyle("CLEAN OSD"))
    w(("_inc", "case-upper.xml"), x_textcase(True))
    w(("_inc", "case-mixed.xml"), x_textcase(False))
    w(("_inc", "scanlines-on.xml"), x_scanlines(True))
    w(("_inc", "scanlines-off.xml"), x_scanlines(False))

    # remove old system folders, then write one per system
    for entry in os.listdir(out):
        p = P(entry, "theme.xml")
        if not entry.startswith("_") and os.path.isfile(p) and entry != "theme.xml":
            shutil.rmtree(P(entry))
    for k in sorted(SYSTEMS):
        os.makedirs(P(k), exist_ok=True)
        w((k, "theme.xml"), x_system(k))
    # root fallback for any system without its own folder
    w(("theme.xml",), x_system("default", rel="."))
    print(f"built {len(SYSTEMS)} systems, {len(arts)} hardware illustrations into {out}")


if __name__ == "__main__":
    build(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "../es-theme-vcr-osd"))
