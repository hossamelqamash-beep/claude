"""Logo 01 — Doing the Right Thing (ethics programme).
Concept: a ring (integrity, wholeness) with a check mark that breaks out of it
toward the upper right (choosing the right path). Serif + sans lockup."""
import math
import sys

sys.path.insert(0, sys.argv[1])
from logokit import cap_height, export, preview_sheet, text_path  # noqa: E402

OUT = sys.argv[2]

VARIANTS = {
    "color-light": {"bg": "#FFFFFF", "main": "#0F4D3F", "accent": "#C9962C", "sub": "#0F4D3F"},
    "color-dark": {"bg": "#0B2A23", "main": "#F5EFE2", "accent": "#E4B651", "sub": "#F5EFE2"},
    "black": {"bg": "#FFFFFF", "main": "#000000", "accent": "#000000", "sub": "#000000"},
    "white": {"bg": "#111111", "main": "#FFFFFF", "accent": "#FFFFFF", "sub": "#FFFFFF"},
}

R, SW = 40.0, 9.0  # ring radius / stroke in the 100-unit icon box
CHECK = [(29, 53), (44, 68), (90, 14)]


def icon(p, ox=0, oy=0, k=1.0):
    cx, cy = 50, 50
    # gap in the ring where the long stroke of the check exits
    (x1, y1), (x2, y2) = CHECK[1], CHECK[2]
    dx, dy = x2 - x1, y2 - y1
    fx, fy = x1 - cx, y1 - cy
    a, b, c = dx * dx + dy * dy, 2 * (fx * dx + fy * dy), fx * fx + fy * fy - R * R
    t = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    ix, iy = x1 + t * dx, y1 + t * dy
    ang = math.atan2(iy - cy, ix - cx)
    gap = math.radians(19)
    a0, a1 = ang + gap, ang - gap + 2 * math.pi
    sx, sy = cx + R * math.cos(a0), cy + R * math.sin(a0)
    ex, ey = cx + R * math.cos(a1), cy + R * math.sin(a1)
    ring = f"M{sx:.2f} {sy:.2f} A{R} {R} 0 1 1 {ex:.2f} {ey:.2f}"
    pts = " ".join(f"{x},{y}" for x, y in CHECK)
    return (
        f'<g transform="translate({ox} {oy}) scale({k})">'
        f'<path d="{ring}" fill="none" stroke="{p["main"]}" stroke-width="{SW}" stroke-linecap="round"/>'
        f'<polyline points="{pts}" fill="none" stroke="{p["accent"]}" stroke-width="{SW + 1}" '
        f'stroke-linecap="round" stroke-linejoin="round"/></g>'
    )


def primary(p):
    big, small = 112, 34
    capb = cap_height("Fraunces.ttf", big)
    caps = cap_height("Manrope.ttf", small)
    gap = 22
    block_h = caps + gap + capb
    icon_size = block_h * 1.32
    tx = icon_size + 44
    top = (icon_size - block_h) / 2
    d1, w1 = text_path("DOING THE", "Manrope.ttf", small, tx + 4, top + caps, tracking=0.32)
    d2, w2 = text_path("Right Thing", "Fraunces.ttf", big, tx, top + block_h)
    body = icon(p, 0, 0, icon_size / 100) + (
        f'<path d="{d1}" fill="{p["sub"]}"/><path d="{d2}" fill="{p["main"]}"/>'
    )
    return body, round(tx + max(w1, w2)), round(icon_size)


def stacked(p):
    big, small = 112, 34
    d2, w2 = text_path("Right Thing", "Fraunces.ttf", big, 0, 0)
    _, w1 = text_path("DOING THE", "Manrope.ttf", small, 0, 0, tracking=0.32)
    W = max(w2, 200)
    isz = 190
    y_small = isz + 52 + cap_height("Manrope.ttf", small)
    y_big = y_small + 26 + cap_height("Fraunces.ttf", big)
    d1, _ = text_path("DOING THE", "Manrope.ttf", small, (W - w1) / 2, y_small, tracking=0.32)
    d2, _ = text_path("Right Thing", "Fraunces.ttf", big, (W - w2) / 2, y_big)
    body = icon(p, (W - isz) / 2, 0, isz / 100) + (
        f'<path d="{d1}" fill="{p["sub"]}"/><path d="{d2}" fill="{p["main"]}"/>'
    )
    return body, round(W), round(y_big + 6)


def mark(p):
    return icon(p, 0, 0, 1), 100, 100


zpath, prev = export(
    "01_Doing-the-Right-Thing", "Doing the Right Thing",
    {"primary": primary, "stacked": stacked, "icon": mark}, VARIANTS, OUT,
)
preview_sheet("Doing the Right Thing", prev, OUT + "/01_preview.png")
print(zpath)
