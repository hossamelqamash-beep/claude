"""The official HQbit logo (logo/official/hqbit-logo-original.svg, supplied by Hossam) and the
versions derived from its exact paths: horizontal, stacked (HQ over BIT), personal HQ, in colour,
white, purple and black.

The lime chip inside the B's upper bowl is "the bit". On a transparent background the purple ring
around it is dropped (it only paints the B's counter, which is already a hole).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "logo", "official", "hqbit-logo-original.svg")

PURPLE = "#612BFE"   # brand purple (from the logo)
LIME = "#E0FE3B"     # the bit (from the logo)
WHITE = "#FFFFFF"

_src = open(SRC, encoding="utf-8").read()
_paths = re.findall(r'<path class="(\w)" d="([^"]+)"', _src)
H, Q, B, CHIP, RING, I, T = (d for _, d in _paths)

TOP, BOTTOM = 249.84, 342.57          # letter bounds (all letters share them)
HQ_X = (162.0, 424.37)
BIT_X = (433.08, 678.33)
LH = BOTTOM - TOP                     # letter height


def _letters(fill, chip, ring=None):
    out = f'<g fill="{fill}"><path d="{H}"/><path d="{Q}"/><path d="{B}"/><path d="{I}"/><path d="{T}"/></g>'
    out += f'<path fill="{chip}" d="{CHIP}"/>'
    if ring:
        out += f'<path fill="{ring}" d="{RING}"/>'
    return out


def _hq(fill):
    return f'<g fill="{fill}"><path d="{H}"/><path d="{Q}"/></g>'


def _bit(fill, chip, ring=None):
    out = f'<g fill="{fill}"><path d="{B}"/><path d="{I}"/><path d="{T}"/></g><path fill="{chip}" d="{CHIP}"/>'
    if ring:
        out += f'<path fill="{ring}" d="{RING}"/>'
    return out


def svg(layout="horizontal", fill=WHITE, chip=LIME, bg=None, pad=None, square=False):
    """layout: horizontal | stacked | hq. pad is in logo units (letter height = 92.7)."""
    ring = bg if bg else None
    if layout == "horizontal":
        pad = LH * 0.5 if pad is None else pad
        x0, x1, y0, y1 = HQ_X[0], BIT_X[1], TOP, BOTTOM
        body = _letters(fill, chip, ring)
    elif layout == "hq":
        pad = LH * 0.35 if pad is None else pad
        x0, x1, y0, y1 = HQ_X[0], HQ_X[1], TOP, BOTTOM
        body = _hq(fill)
    else:  # stacked: HQ on top, BIT under it, both centred
        pad = LH * 0.35 if pad is None else pad
        gap = LH * 0.32
        wh, wb = HQ_X[1] - HQ_X[0], BIT_X[1] - BIT_X[0]
        width = max(wh, wb)
        x0, y0 = 0.0, 0.0
        x1, y1 = width, 2 * LH + gap
        body = (f'<g transform="translate({(width - wh) / 2 - HQ_X[0]:.2f} {-TOP:.2f})">{_hq(fill)}</g>'
                f'<g transform="translate({(width - wb) / 2 - BIT_X[0]:.2f} {LH + gap - TOP:.2f})">{_bit(fill, chip, ring)}</g>')
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    vx, vy = x0 - pad, y0 - pad
    if square:
        side = max(w, h)
        vx -= (side - w) / 2
        vy -= (side - h) / 2
        w = h = side
    bg_rect = f'<rect x="{vx:.2f}" y="{vy:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.2f} {vy:.2f} {w:.2f} {h:.2f}">'
            f'<title>HQbit</title>{bg_rect}{body}</svg>')


# file name -> (layout, fill, chip, bg)
VARIANTS = {
    "hqbit-logo-on-purple": ("horizontal", WHITE, LIME, PURPLE),
    "hqbit-logo-white": ("horizontal", WHITE, LIME, None),
    "hqbit-logo-purple": ("horizontal", PURPLE, PURPLE, None),
    "hqbit-logo-black": ("horizontal", "#0D0619", "#0D0619", None),
    "hqbit-logo-white-mono": ("horizontal", WHITE, WHITE, None),
    "hqbit-logo-stacked-on-purple": ("stacked", WHITE, LIME, PURPLE),
    "hqbit-logo-stacked-white": ("stacked", WHITE, LIME, None),
    "hqbit-logo-stacked-purple": ("stacked", PURPLE, PURPLE, None),
    "hq-logo-on-purple": ("hq", WHITE, None, PURPLE),
    "hq-logo-white": ("hq", WHITE, None, None),
    "hq-logo-purple": ("hq", PURPLE, None, None),
    "hq-logo-black": ("hq", "#0D0619", None, None),
}
