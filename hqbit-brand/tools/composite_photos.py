#!/usr/bin/env python3
"""Place theme screenshots onto the R36S screens in a green-screen product photo collage.

usage: composite_photos.py <green-screen collage> <out dir>

Each display in the collage is solid green. For each one:
1. Key out the green: a soft matte from how much green exceeds red/blue, so the screen's own edge and
   rounded corners stay exactly as photographed.
2. Fit a straight line to each side of the green area and intersect them for the four corners; the
   screenshot is perspective-warped (at 4x) onto that quad and cut by the matte.
3. Remove green spill from the bezel next to the screen, tone the screenshot to the photo (lifted
   blacks, a hint of the room colour, slight edge falloff), add a faint glass sheen.
"""
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(ROOT, "showcase", "screens")
UP = 4

# name: (panel box in the collage, [(point inside the green screen, screenshot[, quarter turns])])
PANELS = {
    "volta": ((0, 0, 757, 578), [((460, 150), "volta/system-horizontal-dark.png")]),
    "neonglow": ((767, 0, 1254, 300), [((1080, 90), "neonglow/system-vertical.png", 1)]),
    "vcr": ((767, 306, 1254, 620), [((1000, 395), "vcr/system-snes.png")]),
    "deskos": ((626, 629, 1254, 912), [((935, 715), "deskos/system-classic.png")]),
    "collection": ((0, 586, 616, 912), [((390, 695), "volta/system-wheel-citrine.png"),
                                        ((492, 700), "vcr/system-gba-navy.png")]),
}


def greenness(img):
    b, g, r = [img[..., i].astype(np.float32) for i in range(3)]
    return g - np.maximum(r, b)


def screen_mask(img, inside):
    m = (greenness(img) > 40).astype(np.uint8)
    n, lab = cv2.connectedComponents(m)
    return (lab == lab[inside[1], inside[0]]).astype(np.uint8)


def fit_quad(mask):
    cs, _ = cv2.findContours(mask * 255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cs, key=cv2.contourArea)
    pts = cnt.reshape(-1, 2).astype(np.float32)
    hull = cv2.convexHull(cnt)
    peri = cv2.arcLength(hull, True)
    eps = 0.02
    while True:
        ap = cv2.approxPolyDP(hull, eps * peri, True).reshape(-1, 2).astype(np.float32)
        if len(ap) <= 4:
            break
        eps += 0.005
    c = ap.mean(0)
    ap = ap[np.argsort(np.arctan2(ap[:, 1] - c[1], ap[:, 0] - c[0]))]
    ap = np.roll(ap, -int(np.argmin(ap.sum(1))), 0)          # TL, TR, BR, BL
    lines = []
    for i in range(4):
        a, b = ap[i], ap[(i + 1) % 4]
        d = b - a
        L = np.linalg.norm(d)
        t = ((pts - a) @ d) / (L * L)
        nrm = np.array([-d[1], d[0]]) / L
        sel = pts[(t > 0.15) & (t < 0.85) & (np.abs((pts - a) @ nrm) < 0.08 * L)]
        vx, vy, x, y = cv2.fitLine(sel, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        lines.append((np.array([x, y]), np.array([vx, vy])))
    out = []
    for i in range(4):                                       # corner i between side i-1 and side i
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        t = np.linalg.solve(np.array([d1, -d2]).T, p2 - p1)
        out.append(p1 + t[0] * d1)
    return np.array(out, np.float32)


def composite(src, out_dir, name):
    box, screens = PANELS[name]
    col = cv2.imread(src)
    x0, y0, x1, y1 = box
    panel = col[y0:y1, x0:x1]
    big = cv2.resize(panel, None, fx=UP, fy=UP, interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    size = (big.shape[1], big.shape[0])
    gr = cv2.resize(greenness(panel), size, interpolation=cv2.INTER_CUBIC)
    out = big.copy()
    quads = []
    for inside, shot_path, *rot in screens:
        m = screen_mask(col, inside)[y0:y1, x0:x1]
        quad = np.roll(fit_quad(m), -(rot[0] if rot else 0), 0)   # rot: device lying on its side
        quads.append((quad + [x0, y0]).tolist())
        q = (quad * UP + (UP - 1) / 2).astype(np.float32)
        region = cv2.dilate(cv2.resize(m, size, interpolation=cv2.INTER_NEAREST), np.ones((13, 13), np.uint8)).astype(np.float32)
        matte = np.clip((gr - 8) / 50, 0, 1) * region
        matte = cv2.dilate(matte, np.ones((5, 5), np.uint8))                 # cover the anti-aliased rim
        matte = cv2.GaussianBlur(matte, (0, 0), UP * 0.45)[..., None]
        shot = cv2.imread(os.path.join(SCR, shot_path))
        shot = cv2.resize(shot, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255
        sh, sw = shot.shape[:2]
        tint = cv2.GaussianBlur(big, (0, 0), 60)[int(q[:, 1].mean()), int(q[:, 0].mean())]
        s = (0.03 + shot * 0.94) * 0.95 + tint * 0.05
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        edge = np.minimum(np.minimum(xx, sw - 1 - xx) / sw, np.minimum(yy, sh - 1 - yy) / sh)
        s *= (0.92 + 0.08 * np.clip(edge / 0.05, 0, 1))[..., None]
        H = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), q)
        ws = cv2.warpPerspective(s, H, size, flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
        ws = cv2.GaussianBlur(ws, (0, 0), UP * 0.4)
        tl, tr, br, bl = q
        band = np.float32([tl, tl + (tr - tl) * 0.6, tl + (tr - tl) * 0.15 + (bl - tl) * 0.55, tl + (bl - tl) * 0.72])
        g = np.zeros(size[::-1], np.float32)
        cv2.fillPoly(g, [band.astype(np.int32)], 0.06)
        g = cv2.GaussianBlur(g, (0, 0), UP * 14)[..., None] * matte
        layer = ws * matte + out * (1 - matte)
        out = layer + g * (1 - layer)
    # despill: around the screens, pull green down towards max(red, blue)
    ring = cv2.dilate((gr > 10).astype(np.uint8), np.ones((5 * UP, 5 * UP), np.uint8)).astype(bool)
    bch, gch, rch = out[..., 0], out[..., 1], out[..., 2]
    lim = np.maximum(bch, rch)
    out[..., 1] = np.where(ring & (gch > lim), lim + (gch - lim) * 0.15, gch)
    res = cv2.resize(np.clip(out * 255, 0, 255).astype(np.uint8), (panel.shape[1] * 2, panel.shape[0] * 2), interpolation=cv2.INTER_AREA)
    res = cv2.addWeighted(res, 1.3, cv2.GaussianBlur(res, (0, 0), 1.2), -0.3, 0)
    cv2.imwrite(os.path.join(out_dir, f"hqbit-photo-{name}.jpg"), res, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return quads


if __name__ == "__main__":
    SRC, OUT = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    for n in PANELS:
        print(n, [[(round(float(x), 1), round(float(y), 1)) for x, y in q] for q in composite(SRC, OUT, n)])
