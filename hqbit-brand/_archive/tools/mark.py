"""HQbit marks.

The HQ monogram is an H and a square Q that share one stem, drawn on a pixel grid
(1 unit = 1 grid square, strokes are 2 units). The Q's tail is a 3x3 square overlapping
the Q's bottom-right corner: in the HQbit logo it is the "bit" and takes its own colour;
in the personal HQ logo it is the same colour as the letters.
"""

GRID_W, GRID_H = 14, 12

# (x, y, w, h) in grid units
LETTERS = [
    (0, 0, 2, 10),    # H left stem
    (2, 4, 2, 2),     # H crossbar
    (4, 0, 2, 10),    # shared stem (H right / Q left)
    (6, 0, 6, 2),     # Q top
    (10, 2, 2, 8),    # Q right
    (6, 8, 4, 2),     # Q bottom
]
BIT = (10, 8, 4, 4)   # Q tail = the bit


def svg(fill="#B9A3FF", bit_fill=None, u=50, pad=0, bg=None, size=None):
    """bit_fill=None draws the tail in the letter colour (personal HQ logo)."""
    w, h = GRID_W * u + 2 * pad, GRID_H * u + 2 * pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"'
           + (f' width="{size}"' if size else "") + ' shape-rendering="crispEdges">']
    if bg:
        out.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')
    d = "".join(f"M{x*u+pad} {y*u+pad}h{ww*u}v{hh*u}h-{ww*u}z" for x, y, ww, hh in LETTERS)
    out.append(f'<path d="{d}" fill="{fill}"/>')
    x, y, ww, hh = BIT
    out.append(f'<rect x="{x*u+pad}" y="{y*u+pad}" width="{ww*u}" height="{hh*u}" fill="{bit_fill or fill}"/>')
    out.append("</svg>")
    return "".join(out)
