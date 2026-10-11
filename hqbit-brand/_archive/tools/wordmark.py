"""Outline text to SVG paths (so logo files need no fonts installed)."""
import os
from functools import lru_cache

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


@lru_cache(None)
def font(name="SpaceGrotesk-Variable.woff2", wght=700):
    f = TTFont(os.path.join(FONTS, name))
    if "fvar" in f:
        f = instantiateVariableFont(f, {"wght": wght})
    return f


def text_paths(runs, size=100, tracking=-0.04, fontname="SpaceGrotesk-Variable.woff2", wght=700):
    """runs: [(text, fill)]. Returns (svg_fragment, width, ascent, descent) at font size `size`,
    baseline at y=ascent."""
    f = font(fontname, wght)
    upm = f["head"].unitsPerEm
    s = size / upm
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    asc = f["hhea"].ascent * s
    desc = -f["hhea"].descent * s
    cap = getattr(f["OS/2"], "sCapHeight", 700) * s
    x = 0.0
    parts = []
    for text, fill in runs:
        for ch in text:
            g = cmap[ord(ch)]
            pen = SVGPathPen(gs)
            gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, asc)))
            parts.append(f'<path d="{pen.getCommands()}" fill="{fill}"/>')
            x += hmtx[g][0] * s + tracking * size
    x -= tracking * size
    return "".join(parts), x, asc, desc, cap
