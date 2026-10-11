#!/usr/bin/env python3
"""HQbit pixel wordmark, v2.

Combines two directions:
* chunky pixel letters with a thick dark outline and a stepped 3D extrusion;
* a "wing" perspective (left half tilts up-left, right half up-right), neon dash highlights
  inside the letters, a lightning bolt behind and a slanted tagline with a dashed underline.

All glyphs are drawn here on a pixel grid (original). The Q's tail is the bit (3x3 cells).
usage: python3 tools/pixel_logo.py   -> logo/hqbit-pixel-logo-*.svg + logo/png/*.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wordmark  # noqa: E402
from build_brand import BUILD, C, ROOT, render, w  # noqa: E402

GLYPHS = {
    "H": ["##....##", "##....##", "##....##", "##....##", "########", "########", "##....##", "##....##", "##....##",
          "##....##"],
    "Q": [".######.", "########", "##....##", "##....##", "##....##", "##....##", "##..####", "##...###", "########",
          ".######."],
    "b": ["##......", "##......", "##......", "######..", "#######.", "##...###", "##....##", "##...###", "#######.",
          "######.."],
    "i": ["##", "##", "..", "##", "##", "##", "##", "##", "##", "##"],
    "t": [".##..", ".##..", "#####", "#####", ".##..", ".##..", ".##..", ".##..", ".####", "..###"],
}
WORD = "HQbit"
GAP = 2           # cells between letters
OUTLINE = 1       # cells
DEPTH = 3         # extrusion cells (down-right)
BIT = 3           # bit size, cells


def layout():
    face, bit = set(), set()
    x = 0
    q_box = None
    split = None
    spans = []
    for ch in WORD:
        g = GLYPHS[ch]
        for y, row in enumerate(g):
            for cx, v in enumerate(row):
                if v == "#":
                    face.add((x + cx, y))
        if ch == "Q":
            q_box = (x, len(g[0]))
        if ch == "b":
            split = x - 0.5
        spans.append((x, x + len(g[0]) + (GAP + 1 if ch == "Q" else 0)))
        x += len(g[0]) + GAP + (1 if ch == "Q" else 0)
    # bit: 3x3 overlapping the Q's bottom-right corner
    qx, qw = q_box
    for by in range(9, 9 + BIT):
        for bx in range(qx + qw - 1, qx + qw - 1 + BIT):
            bit.add((bx, by))
    face -= bit
    return face, bit, x - GAP, split, spans


def dilate(cells, r):
    out = set(cells)
    for x, y in cells:
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                out.add((x + dx, y + dy))
    return out


def rects(cells, u, fill):
    """Merge horizontal runs into rects."""
    rows = {}
    for x, y in cells:
        rows.setdefault(y, []).append(x)
    out = []
    for y, xs in rows.items():
        xs.sort()
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            out.append(f"M{start*u} {y*u}h{(prev-start+1)*u}v{u}h{-(prev-start+1)*u}z")
            if x is not None:
                start = prev = x
    return f'<path fill="{fill}" d="{"".join(out)}"/>'


def highlights(face, u, color, lift):
    """Neon dashes inset along the left edge of each stem and the top edge of wide parts.
    Drawn per column so they follow the pixel wing steps."""
    t = 0.26
    pieces = []                                   # (x0, x1, y0, y1) in cells, unshifted
    left = sorted(((x, y) for x, y in face if (x - 1, y) not in face and (x + 1, y) in face))
    runs, cur = [], []
    for x, y in left:
        if cur and (x != cur[-1][0] or y != cur[-1][1] + 1):
            runs.append(cur)
            cur = []
        cur.append((x, y))
    if cur:
        runs.append(cur)
    for run in runs:
        if len(run) >= 5:
            x0, y0 = run[0]
            pieces.append((x0 + 0.42, x0 + 0.42 + t, y0 + 1.2, y0 + 1.2 + (len(run) - 2) * 0.55))
    top = sorted(((x, y) for x, y in face if (x, y - 1) not in face and (x, y + 1) in face), key=lambda p: (p[1], p[0]))
    runs, cur = [], []
    for x, y in top:
        if cur and (y != cur[-1][1] or x != cur[-1][0] + 1):
            runs.append(cur)
            cur = []
        cur.append((x, y))
    if cur:
        runs.append(cur)
    for run in runs:
        if len(run) >= 5:
            x0, y0 = run[0]
            pieces.append((x0 + 1.2, x0 + 1.2 + (len(run) - 2) * 0.5, y0 + 0.42, y0 + 0.42 + t))
    out = []
    for x0, x1, y0, y1 in pieces:                 # split horizontal pieces per column, then lift
        xs = [x0]
        k = int(x0) + 1
        while k < x1:
            xs.append(k)
            k += 1
        xs.append(x1)
        for a, b in zip(xs, xs[1:]):
            dy = lift(int(a))
            out.append(f"M{a*u:.1f} {(y0+dy)*u:.1f}h{(b-a)*u:.1f}v{(y1-y0)*u:.1f}h{-(b-a)*u:.1f}z")
    return f'<path fill="{color}" d="{"".join(out)}"/>'


def bolt_cells(ox, oy, s=1):
    """Pixel lightning bolt: upper stroke leaning left, a jag, lower stroke ending in a point."""
    cells = set()
    for y in range(0, 14):                       # upper stroke, 5 wide
        x0 = 16 - y * 0.62
        for x in range(round(x0), round(x0) + 5):
            cells.add((x, y))
    for y in (14, 15, 16):                       # the jag
        for x in range(4, 17):
            cells.add((x, y))
    for y in range(17, 34):                      # lower stroke, tapering
        x0 = 12 - (y - 17) * 0.62
        width = max(1, 5 - (y - 17) // 4)
        for x in range(round(x0), round(x0) + width):
            cells.add((x, y))
    return {(ox + x * s + dx, oy + y * s + dy) for x, y in cells for dx in range(s) for dy in range(s)}


STEP = 6          # wing: each letter rises one cell per STEP columns its centre is away from the middle


def logo(scheme, tagline=True, bolt=True, u=20):
    face, bit, width, split, spans = layout()
    centre = split

    def lift(x):
        for a, b in spans:
            if a <= x < b:
                return -round(abs((a + b) / 2 - centre) / STEP)
        return 0

    face = {(x, y + lift(x)) for x, y in face}
    bit = {(x, y + lift(x)) for x, y in bit}
    letters = face | bit
    out_cells = dilate(letters, OUTLINE)
    ext = set()
    for k in range(1, DEPTH + 1):
        ext |= {(x + k, y + k) for x, y in out_cells}
    dark = out_cells | ext
    rise = -min(lift(0), lift(width))
    pad = 6
    gw, gh = width + 2 * OUTLINE + DEPTH, 10 + 2 * OUTLINE + DEPTH + rise
    W = (gw + 2 * pad) * u
    H = (gh + 2 * pad + (3 if tagline else 0)) * u
    ox, oy = pad + OUTLINE, pad + OUTLINE + rise

    def shift(cells):
        return {(x + ox, y + oy) for x, y in cells}

    s = scheme
    unshifted = {(x, y - lift(x)) for x, y in face}
    parts = []
    if s.get("bg"):
        parts.append(f'<rect width="{W}" height="{H}" fill="{s["bg"]}"/>')
    if bolt:
        bc = bolt_cells(0, 0, 1)
        bx, by = (pad + 1) * u, (pad - 2) * u
        parts.append(f'<g transform="translate({bx} {by}) scale(0.8)">{rects(bc, u, s["bolt"])}</g>')
    parts += [rects(shift(dark), u, s["outline"]), rects(shift(face), u, s["face"]), rects(shift(bit), u, s["bit"]),
              f'<g transform="translate({ox*u} {oy*u})">{highlights(unshifted, u, s["dash"], lift)}</g>']
    if tagline:
        frag, tw, asc, desc, cap = wordmark.text_paths([("PIXEL / AI / UI", s["tag"])], 1.8 * u, tracking=0.0,
                                                       fontname="Silkscreen-Bold.ttf", wght=700)
        tx = (ox + width + OUTLINE + DEPTH) * u - tw
        ty = (oy + 10 + DEPTH + 2.2) * u
        dash = "".join(f'<rect x="{tx + i * 1.6 * u:.1f}" y="{ty + cap + 0.9*u:.1f}" width="{(0.9 if i % 4 else 2.4) * u:.1f}" height="{0.4*u:.1f}" fill="{s["tag2"]}"/>'
                       for i in range(int(tw / (1.6 * u))) if i % 4 != 1)
        parts.append(f'<g transform="translate({tx} {ty - (asc - cap)})">{frag}</g>{dash}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">'
            f'<title>HQbit</title>{"".join(parts)}</svg>'), W, H


SCHEMES = {
    # name: colours                                                  (bg only used for the preview PNG)
    "on-violet": dict(bg=C["violet"], outline=C["night"], face=C["mist"], bit=C["lilac"], dash=C["violet"],
                      bolt=C["lilac"], tag=C["mist"], tag2=C["night"]),
    "on-dark": dict(bg=C["night"], outline=C["void"], face=C["lilac"], bit=C["violet"], dash=C["mist"],
                    bolt=C["royal"], tag=C["lilac"], tag2=C["violet"]),
    "on-light": dict(bg=C["mist"], outline=C["night"], face=C["violet"], bit=C["lilac"], dash=C["mist"],
                     bolt=C["lilac"], tag=C["night"], tag2=C["violet"]),
}


def build():
    L = os.path.join(ROOT, "logo")
    previews = []
    for name, s in SCHEMES.items():
        transparent = dict(s, bg=None)
        svg, W, H = logo(transparent)
        w(f"{L}/hqbit-pixel-logo-{name}.svg", svg)
        svg_bg, W, H = logo(s)
        html = f"{BUILD}/pixel-{name}.html"
        pw = 2000
        ph = round(pw * H / W)
        w(html, f'<html><body style="margin:0">{svg_bg.replace("<svg ", f"<svg width={pw} height={ph} ", 1)}</body></html>')
        render(html, f"{L}/png/hqbit-pixel-logo-{name}-preview.png", pw, ph)
        html = f"{BUILD}/pixel-{name}-t.html"
        w(html, f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={pw} height={ph} ", 1)}</body></html>')
        render(html, f"{L}/png/hqbit-pixel-logo-{name}.png", pw, ph, transparent=True)
        previews.append(f"{L}/png/hqbit-pixel-logo-{name}-preview.png")
        # compact version (no bolt, no tagline) for small uses
        svg_c, W, H = logo(transparent, tagline=False, bolt=False)
        w(f"{L}/hqbit-pixel-wordmark-{name}.svg", svg_c)
    return previews


if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    for p in build():
        print(p)
