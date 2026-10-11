#!/usr/bin/env python3
"""Collection hero: five R36S handhelds (green screens + green floor reflections) -> theme screenshots.

usage: composite_five.py <green photo> <out.jpg>

* Screens: keyed by greenness; the visible part is fitted with four lines (see composite_photos.fit_quad).
  Screens partly hidden behind the front device get their hidden side extended to the front screen's
  aspect, so the screenshot continues underneath and the matte cuts it where the device in front starts.
  The photo's screens are taller than 4:3, so the 640x480 screenshot is letterboxed (black bars).
* Reflections: each green blob on the floor is filled with that device's screen, flipped, blurred and
  dimmed by the reflection's own brightness, then cut by its soft green matte.
"""
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from composite_photos import SCR, fit_quad, greenness  # noqa: E402

UP = 2
# (point inside the green screen, screenshot, hidden side or None, point inside its floor reflection or None)
SCREENS = [
    ((77, 629), "volta/system-wheel-citrine.png", "right", (72, 1137)),        # white
    ((190, 608), "vcr/system-snes.png", "right", (186, 1185)),                  # orange
    ((636, 590), "volta/system-horizontal-dark.png", "left", (639, 1189)),      # black
    ((757, 608), "deskos/system-classic.png", "left", (759, 1170)),             # red
    ((399, 454), "neonglow/system-vertical.png", None, None),                   # purple, in front (drawn last)
]


def component(img, pt):
    m = (greenness(img) > 40).astype(np.uint8)
    _, lab = cv2.connectedComponents(m)
    return (lab == lab[pt[1], pt[0]]).astype(np.uint8)


def extend(quad, side, aspect):
    tl, tr, br, bl = quad
    h = (np.linalg.norm(bl - tl) + np.linalg.norm(br - tr)) / 2
    w = h * aspect
    if side == "right":
        tr = tl + (tr - tl) / np.linalg.norm(tr - tl) * w
        br = bl + (br - bl) / np.linalg.norm(br - bl) * w
    elif side == "left":
        tl = tr + (tl - tr) / np.linalg.norm(tl - tr) * w
        bl = br + (bl - br) / np.linalg.norm(bl - br) * w
    return np.float32([tl, tr, br, bl])


def letterbox(shot, aspect):
    """Put the 4:3 screenshot full-width on a screen of the given width/height aspect."""
    h, w = shot.shape[:2]
    H = int(round(w / aspect))
    canvas = np.full((H, w, 3), 6, np.uint8)
    y = (H - h) // 2
    canvas[y:y + h] = shot
    return canvas


def warp(src, quad, size):
    h, w = src.shape[:2]
    H = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), quad)
    return cv2.warpPerspective(src, H, size, flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)


def main(src, dst):
    img = cv2.imread(src)
    big = cv2.resize(img, None, fx=UP, fy=UP, interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    size = (big.shape[1], big.shape[0])
    gr = cv2.resize(greenness(img), size, interpolation=cv2.INTER_CUBIC)
    gch = big[..., 1]
    front = fit_quad(component(img, SCREENS[-1][0]))
    aspect = (np.linalg.norm(front[1] - front[0]) + np.linalg.norm(front[2] - front[3])) / \
             (np.linalg.norm(front[3] - front[0]) + np.linalg.norm(front[2] - front[1]))
    out = big.copy()
    for inside, shot_path, hidden, refl in SCREENS:
        m = component(img, inside)
        quad = fit_quad(m)
        if hidden:
            quad = extend(quad, hidden, aspect)
        q = (quad * UP + (UP - 1) / 2).astype(np.float32)
        shot = cv2.imread(os.path.join(SCR, shot_path))
        shot = cv2.resize(shot, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        screen = letterbox(shot, aspect).astype(np.float32) / 255
        screen = 0.03 + screen * 0.94
        region = cv2.dilate(cv2.resize(m, size, interpolation=cv2.INTER_NEAREST), np.ones((7, 7), np.uint8)).astype(np.float32)
        matte = cv2.dilate(np.clip((gr - 8) / 50, 0, 1) * region, np.ones((3, 3), np.uint8))
        matte = cv2.GaussianBlur(matte, (0, 0), 0.6 * UP)[..., None]
        ws = cv2.GaussianBlur(warp(screen, q, size), (0, 0), 0.35 * UP)
        tl, tr, br, bl = q
        band = np.float32([tl, tl + (tr - tl) * 0.6, tl + (tr - tl) * 0.15 + (bl - tl) * 0.5, tl + (bl - tl) * 0.7])
        sheen = np.zeros(size[::-1], np.float32)
        cv2.fillPoly(sheen, [band.astype(np.int32)], 0.06)
        sheen = cv2.GaussianBlur(sheen, (0, 0), 12 * UP)[..., None] * matte
        layer = ws * matte + out * (1 - matte)
        out = layer + sheen * (1 - layer)
        if refl:
            rm = component(img, refl)
            x, y, w, h = cv2.boundingRect(rm)                                   # reflections are soft blobs: use their box
            rq = (np.float32([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]) * UP).astype(np.float32)
            flipped = np.ascontiguousarray(screen[::-1])                     # mirror image of the screen
            wr = cv2.GaussianBlur(warp(flipped, rq, size), (0, 0), 9 * UP)
            rreg = cv2.dilate(cv2.resize(rm, size, interpolation=cv2.INTER_NEAREST), np.ones((15, 15), np.uint8)).astype(np.float32)
            ra = np.clip((gr - 5) / 60, 0, 1) * rreg
            ra = cv2.GaussianBlur(ra, (0, 0), 6 * UP)[..., None]
            light = np.clip(gch / 0.85, 0, 1)[..., None]                      # how bright the reflection is here
            base = out * (1 - ra)
            out = base + ra * (0.05 + wr * light * 0.7)
    # despill the green glow on the shells and the floor
    ring = cv2.dilate((gr > 6).astype(np.uint8), np.ones((9 * UP, 9 * UP), np.uint8)).astype(bool)
    b, g, r = out[..., 0], out[..., 1], out[..., 2]
    lim = np.maximum(b, r)
    out[..., 1] = np.where(ring & (g > lim), lim + (g - lim) * 0.1, g)
    res = np.clip(out * 255, 0, 255).astype(np.uint8)
    res = cv2.addWeighted(res, 1.25, cv2.GaussianBlur(res, (0, 0), 1.2), -0.25, 0)
    cv2.imwrite(dst, res, [cv2.IMWRITE_JPEG_QUALITY, 93])
    print("aspect", round(float(aspect), 3))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
