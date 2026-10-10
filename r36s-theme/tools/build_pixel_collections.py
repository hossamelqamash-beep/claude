#!/usr/bin/env python3
"""Hand-built pixel-art logos for the ES auto collections, in 8/16-bit title-screen style.

  favorites       -> auto-favorites.png, favorites.png   (gold star)
  all games       -> auto-allgames.png,  all.png         (game cartridge)
  recently played -> auto-lastplayed.png, recent.png     (clock)

Everything is drawn on a pixel grid with hard edges: a chunky 6x8 pixel font (doubled),
row-banded gradients, a 1-pixel dark outline and a drop shadow, then scaled up 4x with
nearest-neighbour like the rest of the pixel pack.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "pixel", "logos")
SCALE = 4

FONT = {
    "A": [".####.", "##..##", "##..##", "##..##", "######", "##..##", "##..##", "##..##"],
    "C": [".####.", "##..##", "##....", "##....", "##....", "##....", "##..##", ".####."],
    "D": ["#####.", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", "#####."],
    "E": ["######", "##....", "##....", "#####.", "##....", "##....", "##....", "######"],
    "F": ["######", "##....", "##....", "#####.", "##....", "##....", "##....", "##...."],
    "G": [".####.", "##..##", "##....", "##.###", "##..##", "##..##", "##..##", ".#####"],
    "I": ["####", ".##.", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    "L": ["##....", "##....", "##....", "##....", "##....", "##....", "##....", "######"],
    "M": ["##...##", "###.###", "#######", "##.#.##", "##...##", "##...##", "##...##", "##...##"],
    "N": ["##..##", "###.##", "######", "##.###", "##..##", "##..##", "##..##", "##..##"],
    "O": [".####.", "##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####."],
    "P": ["#####.", "##..##", "##..##", "##..##", "#####.", "##....", "##....", "##...."],
    "R": ["#####.", "##..##", "##..##", "##..##", "#####.", "##.##.", "##..##", "##..##"],
    "S": [".####.", "##..##", "##....", ".####.", "....##", "....##", "##..##", ".####."],
    "T": ["######", "..##..", "..##..", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "V": ["##..##", "##..##", "##..##", "##..##", "##..##", "##..##", ".####.", "..##.."],
    "Y": ["##..##", "##..##", "##..##", ".####.", "..##..", "..##..", "..##..", "..##.."],
    " ": ["...", "...", "...", "...", "...", "...", "...", "..."],
}


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)


def text_mask(text, px=2, spacing=1):
    cols = []
    for i, ch in enumerate(text):
        g = np.array([[c == "#" for c in row] for row in FONT[ch]], bool)
        g = np.kron(g, np.ones((px, px), bool))
        if i:
            cols.append(np.zeros((g.shape[0], spacing * px), bool))
        cols.append(g)
    return np.concatenate(cols, 1)


def dilate(m, r=1):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def banded(mask, bands, top=None, height=None):
    """Fill mask with horizontal colour bands (list of (fraction_end, hex))."""
    ys = np.nonzero(mask.any(1))[0]
    top = ys[0] if top is None else top
    height = (ys[-1] - ys[0] + 1) if height is None else height
    rgb = np.zeros(mask.shape + (3,), np.uint8)
    for y in range(mask.shape[0]):
        f = (y - top + 0.5) / height
        for end, col in bands:
            if f <= end:
                rgb[y] = hexc(col)
                break
        else:
            rgb[y] = hexc(bands[-1][1])
    return rgb


class Canvas:
    def __init__(self, w, h):
        self.rgb = np.zeros((h, w, 3), np.uint8)
        self.a = np.zeros((h, w), bool)

    def put(self, mask, rgb, x=0, y=0):
        h, w = mask.shape
        region = (slice(y, y + h), slice(x, x + w))
        m = mask
        self.rgb[region][m] = rgb[m] if rgb.ndim == 3 else rgb
        self.a[region] |= m

    def stamp(self, mask, fill_rgb, outline, shadow, x, y, shadow_off=(2, 2)):
        """Shape with 1px outline and a drop shadow, all on the pixel grid."""
        pad = 3
        m = np.pad(mask, pad)
        f = np.pad(fill_rgb, ((pad, pad), (pad, pad), (0, 0)))
        out = dilate(m, 1)
        sh = np.zeros_like(out)
        sh[shadow_off[1]:, shadow_off[0]:] = out[:out.shape[0] - shadow_off[1], :out.shape[1] - shadow_off[0]]
        self.put(sh & ~out, hexc(shadow), x - pad, y - pad)
        self.put(out & ~m, hexc(outline), x - pad, y - pad)
        self.put(m, f, x - pad, y - pad)

    def image(self):
        ys, xs = np.nonzero(self.a)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        out = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        out[..., :3] = self.rgb[y0:y1, x0:x1]
        out[..., 3] = self.a[y0:y1, x0:x1] * 255
        img = Image.fromarray(out, "RGBA")
        return img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST)


def raster(size, draw_fn):
    im = Image.new("1", size, 0)
    draw_fn(ImageDraw.Draw(im))
    return np.array(im, bool)


# --------------------------------------------------------------------------- icons (32x32 grid)
GOLD = [(0.12, "FFFBD0"), (0.42, "FFE14A"), (0.72, "FFB21C"), (1.0, "E2700E")]
CYAN = [(0.12, "E6FDFF"), (0.42, "7FE6FF"), (0.72, "33A6FF"), (1.0, "2459D9")]
ROSE = [(0.12, "FFE3EE"), (0.42, "FF8CB0"), (0.72, "FF3F6E"), (1.0, "C2123E")]


def star_icon(c, x, y):
    n = 30
    pts = []
    for i in range(10):
        r = 15 if i % 2 == 0 else 6.4
        a = -np.pi / 2 + i * np.pi / 5
        pts.append((15 + r * np.cos(a), 16 + r * np.sin(a)))
    m = raster((n, n), lambda d: d.polygon(pts, fill=1))
    rgb = banded(m, GOLD)
    # pixel highlight on the upper-left arm + face shine
    for (yy, xx) in ((8, 13), (9, 13), (10, 12), (13, 9), (13, 10)):
        if m[yy, xx]:
            rgb[yy, xx] = hexc("FFFFFF")
    c.stamp(m, rgb, "3A1A00", "140800", x, y)


def cartridge_icon(c, x, y):
    w, h = 24, 31
    body = raster((w, h), lambda d: d.polygon([(2, 0), (w - 3, 0), (w - 1, 2), (w - 1, h - 1), (0, h - 1),
                                                (0, 2)], fill=1))
    rgb = banded(body, [(0.1, "E8E8EE"), (0.6, "BDBDC8"), (1.0, "9696A4")])
    # sticker label with a tiny pixel title screen
    lab = np.zeros_like(body)
    lab[3:17, 3:w - 3] = True
    rgb[lab] = banded(lab, CYAN)[lab]
    rgb[5, 5:w - 5] = hexc("FFFFFF")                       # title bar
    rgb[7, 5:14] = hexc("FFFFFF")
    rgb[12:15, 6:9] = hexc("FFE14A")                       # little hero + ground
    rgb[15, 4:w - 4] = hexc("2459D9")
    # ridged grip on the lower half
    for yy in range(20, h - 2, 2):
        rgb[yy, 3:w - 3] = hexc("7A7A88")
    c.stamp(body, rgb, "141A33", "060814", x + 3, y)


def clock_icon(c, x, y):
    n = 30
    face = raster((n, n), lambda d: d.ellipse([0, 0, n - 1, n - 1], fill=1))
    rgb = banded(face, ROSE)
    inner = raster((n, n), lambda d: d.ellipse([4, 4, n - 5, n - 5], fill=1))
    rgb[inner] = banded(inner, [(0.3, "FFFFFF"), (0.8, "FFF4E6"), (1.0, "F2DCC6")])[inner]
    ink = hexc("2A0A14")
    for k in range(12):                                      # hour ticks
        a = k * np.pi / 6
        rgb[int(round(14.5 - 9 * np.cos(a))), int(round(14.5 + 9 * np.sin(a)))] = ink
    rgb[8:15, 14:16] = ink                                    # minute hand (12)
    rgb[14:16, 9:15] = ink                                    # hour hand (9) -> 9:00
    rgb[14:16, 14:16] = hexc("FF3F6E")
    c.stamp(face, rgb, "3A0614", "140208", x, y)


# --------------------------------------------------------------------------- logos
def logo(lines, bands, outline, shadow, icon):
    c = Canvas(260, 90)
    icon(c, 4, 6)
    tx = 4 + 34 + 6
    masks = [text_mask(t) for t in lines]
    gap = 4
    total_h = sum(m.shape[0] for m in masks) + gap * (len(masks) - 1)
    ty = 6 + (31 - total_h) // 2
    for m in masks:
        c.stamp(m, banded(m, bands), outline, shadow, tx, ty)
        ty += m.shape[0] + gap
    return c.image()


def main():
    os.makedirs(OUT, exist_ok=True)
    items = {
        ("auto-favorites", "favorites"): logo(["FAVORITES"], GOLD, "3A1A00", "140800", star_icon),
        ("auto-allgames", "all"): logo(["ALL GAMES"], CYAN, "141A33", "060814", cartridge_icon),
        ("auto-lastplayed", "recent"): logo(["RECENTLY", "PLAYED"], ROSE, "3A0614", "140208", clock_icon),
    }
    for names, img in items.items():
        for n in names:
            img.save(os.path.join(OUT, n + ".png"), optimize=True)
        print(names, img.size)


if __name__ == "__main__":
    main()
