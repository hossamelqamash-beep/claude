#!/usr/bin/env python3
"""Put theme screenshots onto the R36S screens in product photos (perspective warp + glass sheen).

usage: composite_photos.py <collage.png> <out dir>
Screen quads are in collage pixel coordinates: top-left, top-right, bottom-right, bottom-left.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(ROOT, "showcase", "screens")
SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
UP = 3  # supersampling factor for the warp; output is saved at 2x the collage size

PANELS = {
    # name: (panel box in the collage, [(screen quad, screenshot)])
    "volta": ((0, 0, 752, 574), [([(335, 59), (581, 64), (586, 261), (339, 265)], "volta/system-horizontal-dark.png")]),
    "vcr": ((767, 310, 1254, 623), [([(920, 340), (1076, 331), (1089, 462), (918, 470)], "vcr/system-snes.png")]),
    "neonglow": ((817, 922, 1254, 1254), [([(972, 967), (1132, 966), (1136, 1082), (972, 1086)], "neonglow/system-vertical.png")]),
    "deskos": ((627, 632, 1254, 910), [([(857, 688), (998, 655), (1017, 753), (876, 786)], "deskos/system-classic.png")]),
    "collection": ((0, 922, 515, 1254), [
        ([(80, 952), (221, 948), (223, 1031), (86, 1034)], "volta/system-wheel-citrine.png"),
        ([(247, 966), (340, 966), (342, 1032), (247, 1035)], "neonglow/system-wheel.png"),
        ([(385, 972), (465, 975), (467, 1040), (384, 1040)], "vcr/system-gba-navy.png"),
    ]),
}


def coeffs(dst, src):
    """Perspective coefficients mapping output (dst) points to input (src) points, for Image.transform."""
    a = []
    b = []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return np.linalg.solve(np.array(a, float), np.array(b, float)).tolist()


def composite(name):
    box, screens = PANELS[name]
    col = Image.open(SRC).convert("RGB")
    panel = col.crop(box)
    big = panel.resize((panel.width * UP, panel.height * UP), Image.LANCZOS).convert("RGBA")
    for quad, shot in screens:
        q = [((x - box[0]) * UP, (y - box[1]) * UP) for x, y in quad]
        img = Image.open(os.path.join(SCR, shot)).convert("RGB")
        img = ImageEnhance.Color(img).enhance(1.08)
        img = ImageEnhance.Brightness(img).enhance(1.04)
        w, h = img.size
        warped = img.transform(big.size, Image.PERSPECTIVE, coeffs(q, [(0, 0), (w, 0), (w, h), (0, h)]), Image.BICUBIC)
        mask = Image.new("L", big.size, 0)
        ImageDraw.Draw(mask).polygon(q, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(UP * 0.6))
        warped = warped.filter(ImageFilter.GaussianBlur(UP * 0.35))       # match the photo's softness
        # glass: a soft diagonal sheen plus the original screen's brightest reflections
        xs, ys = zip(*q)
        sheen = Image.new("L", big.size, 0)
        sd = ImageDraw.Draw(sheen)
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        sd.polygon([(x0, y0), (x0 + (x1 - x0) * 0.55, y0), (x0, y0 + (y1 - y0) * 0.7)], fill=34)
        sheen = Image.composite(sheen.filter(ImageFilter.GaussianBlur(UP * 18)), Image.new("L", big.size, 0), mask)
        layer = Image.composite(warped.convert("RGBA"), big, mask)
        white = Image.new("RGBA", big.size, (255, 255, 255, 255))
        layer = Image.composite(white, layer, sheen)
        big = layer
    out = big.convert("RGB").resize((panel.width * 2, panel.height * 2), Image.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    out.save(os.path.join(OUT, f"hqbit-photo-{name}.jpg"), quality=92)
    return out


for n in PANELS:
    composite(n)
    print(n)
