#!/usr/bin/env python3
"""Place theme screenshots onto the R36S screens in product photos.

usage: composite_photos.py <collage.png> <out dir>

For each screen:
1. Find the glass panel: the non-white region inside the device's white frame, grown from a seed quad
   (for clear/purple shells, the lit display itself). Fit a straight line to each side of its outline and
   intersect them, which gives the panel's corners without the rounding.
2. The active display sits inside the glass with a thin black border; its corners are found through the
   panel's homography, so the inset follows the perspective.
3. Warp the screenshot (with rounded corners) into the active area at 4x, tone it to the photo (lifted
   blacks, softer contrast, a tint from the scene), darken its edges slightly, and add a faint glass sheen.
   The photo's own bezel and rim reflections stay untouched.
"""
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(ROOT, "showcase", "screens")
UP = 4

# seed quads (TL, TR, BR, BL) measured on the collage; mode "glass" = white frame, "lit" = transparent shell
PANELS = {
    "volta": ((0, 0, 752, 574), [("glass", [(336, 69), (577, 71), (581, 257), (338, 258)], "volta/system-horizontal-dark.png")]),
    "vcr": ((767, 310, 1254, 623), [("glass", [(916, 342), (1075, 330), (1079, 463), (913, 467)], "vcr/system-snes.png")]),
    "neonglow": ((817, 922, 1254, 1254), [("glass", [(969, 967), (1128, 966), (1129, 1077), (969, 1079)], "neonglow/system-vertical.png")]),
    "deskos": ((627, 632, 1254, 910), [("glass", [(859, 689), (991, 657), (1012, 747), (881, 778)], "deskos/system-classic.png")]),
    "collection": ((0, 922, 515, 1254), [
        ("glass", [(77, 946), (208, 947), (217, 1030), (88, 1034)], "volta/system-wheel-citrine.png"),
        ("lit", [(245, 963), (344, 962), (351, 1033), (248, 1036)], "neonglow/system-wheel.png"),
        ("lit", [(384, 971), (458, 970), (468, 1037), (390, 1039)], "vcr/system-gba-navy.png"),
    ]),
}
INSET = (0.027, 0.034)        # active display inside the glass panel (fraction of width, height)


def region_hull(img, seed, mode):
    q = np.array(seed, np.float32)
    x0, y0 = (q.min(0) - 30).astype(int)
    x1, y1 = (q.max(0) + 30).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0)
    roi = img[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(int)
    seedm = np.zeros(roi.shape[:2], np.uint8)
    cv2.fillPoly(seedm, [(q - [x0, y0]).astype(np.int32)], 1)
    if mode == "glass":
        cand = ~((hsv[..., 2] > 150) & (hsv[..., 1] < 90))
        grow = cv2.dilate(seedm, np.ones((15, 15), np.uint8))
    else:  # lit display on a transparent shell: brighter than the dark bezel around it
        cand = hsv[..., 2] > 55
        grow = cv2.dilate(seedm, np.ones((7, 7), np.uint8))
    cand = (cand & (grow > 0)).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand)
    best = max(range(1, n), key=lambda i: ((lab == i) & (seedm == 1)).sum())
    m = (lab == best).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hull = cv2.convexHull(max(cs, key=cv2.contourArea)).reshape(-1, 2).astype(np.float32) + [x0, y0]
    dense = []                                   # resample the hull every 0.5 px so straight sides have points
    for p0, p1 in zip(hull, np.roll(hull, -1, 0)):
        n = max(2, int(np.linalg.norm(p1 - p0) * 2))
        dense.append(p0 + (p1 - p0) * np.linspace(0, 1, n, endpoint=False)[:, None])
    return np.concatenate(dense).astype(np.float32)


def fit_quad(hull, seed):
    """Fit a line to each side of the outline (ignoring the rounded corners) and intersect them."""
    s = np.array(seed, np.float32)
    lines = []
    for i in range(4):
        a, b = s[i], s[(i + 1) % 4]
        d = b - a
        L = np.linalg.norm(d)
        t = ((hull - a) @ d) / (L * L)
        nrm = np.array([-d[1], d[0]]) / L
        dist = np.abs((hull - a) @ nrm)
        sel = hull[(t > 0.18) & (t < 0.82) & (dist < 0.12 * L)]
        vx, vy, x, y = cv2.fitLine(sel, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        lines.append((np.array([x, y]), np.array([vx, vy])))
    pts = []
    for i in range(4):                       # corner i lies between side i-1 and side i
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        t = np.linalg.solve(np.array([d1, -d2]).T, p2 - p1)
        pts.append(p1 + t[0] * d1)
    return np.array(pts, np.float32)


def inset_quad(quad, fx, fy):
    H = cv2.getPerspectiveTransform(np.float32([[0, 0], [1, 0], [1, 1], [0, 1]]), quad)
    unit = np.float32([[fx, fy], [1 - fx, fy], [1 - fx, 1 - fy], [fx, 1 - fy]]).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(unit, H).reshape(-1, 2)


def tone(shot, tint):
    s = shot.astype(np.float32) / 255
    s = 0.035 + s * 0.93                                   # lifted blacks, softer whites, like a lit LCD in a photo
    s = np.clip((s - 0.5) * 0.96 + 0.5, 0, 1)
    return s * 0.94 + tint * 0.06                          # a hint of the room's colour


def rounded_mask(w, h, r):
    m = np.zeros((h, w), np.uint8)
    cv2.rectangle(m, (r, 0), (w - r, h), 255, -1)
    cv2.rectangle(m, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r, r), (w - r, h - r), (r, h - r)):
        cv2.circle(m, (cx, cy), r, 255, -1, lineType=cv2.LINE_AA)
    return m


def composite(src, out_dir, name):
    box, screens = PANELS[name]
    col = cv2.imread(src)
    panel = col[box[1]:box[3], box[0]:box[2]]
    big = cv2.resize(panel, None, fx=UP, fy=UP, interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    out = big.copy()
    size = (big.shape[1], big.shape[0])
    quads = []
    for mode, seed, shot_path in screens:
        if mode == "glass":
            active = inset_quad(fit_quad(region_hull(col, seed, mode), seed), *INSET)
        else:                                    # transparent shells: edges too faint to detect, use the measured quad
            active = np.array(seed, np.float32)
        quads.append(active)
        act = ((active - [box[0], box[1]]) * UP + (UP - 1) / 2).astype(np.float32)
        shot = cv2.imread(os.path.join(SCR, shot_path))
        sh, sw = shot.shape[:2]
        shot = cv2.resize(shot, (sw * 3, sh * 3), interpolation=cv2.INTER_CUBIC)
        sh, sw = shot.shape[:2]
        tint = cv2.GaussianBlur(big, (0, 0), 40)[int(act[:, 1].mean()), int(act[:, 0].mean())]
        s = tone(shot, tint)
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        edge = np.minimum(np.minimum(xx, sw - 1 - xx) / sw, np.minimum(yy, sh - 1 - yy) / sh)
        s *= (0.9 + 0.1 * np.clip(edge / 0.06, 0, 1))[..., None]           # slight falloff at the edges
        rm = rounded_mask(sw, sh, int(0.025 * sw)).astype(np.float32) / 255
        H = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), act)
        ws = cv2.warpPerspective(s, H, size, flags=cv2.INTER_AREA)
        wm = cv2.warpPerspective(rm, H, size, flags=cv2.INTER_LINEAR)
        ws = cv2.GaussianBlur(ws, (0, 0), UP * 0.45)                         # match the photo's softness
        wm = cv2.GaussianBlur(wm, (0, 0), UP * 0.5)[..., None]
        tl, tr, br, bl = act
        band = np.float32([tl, tl + (tr - tl) * 0.62, tl + (tr - tl) * 0.18 + (bl - tl) * 0.55, tl + (bl - tl) * 0.75])
        g = np.zeros(size[::-1], np.float32)
        cv2.fillPoly(g, [band.astype(np.int32)], 0.07)
        g = cv2.GaussianBlur(g, (0, 0), UP * 14)[..., None] * wm             # soft diagonal glass sheen
        layer = ws * wm + out * (1 - wm)
        out = layer + g * (1 - layer)
    res = cv2.resize(np.clip(out * 255, 0, 255).astype(np.uint8), (panel.shape[1] * 2, panel.shape[0] * 2), interpolation=cv2.INTER_AREA)
    res = cv2.addWeighted(res, 1.35, cv2.GaussianBlur(res, (0, 0), 1.2), -0.35, 0)
    cv2.imwrite(os.path.join(out_dir, f"hqbit-photo-{name}.jpg"), res, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return quads


if __name__ == "__main__":
    SRC, OUT = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    for n in PANELS:
        print(n, [[(round(float(x), 1), round(float(y), 1)) for x, y in q] for q in composite(SRC, OUT, n)])
