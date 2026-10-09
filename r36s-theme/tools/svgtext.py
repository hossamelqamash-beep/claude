"""Convert a string to SVG path data (nanosvg in ES cannot render <text>)."""
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

_fonts = {}


def text_path(text, font_path, cx, baseline, size, fill, tracking=0):
    font = _fonts.setdefault(font_path, TTFont(font_path))
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    s = size / upm
    names = [cmap[ord(ch)] for ch in text]
    advances = [gs[n].width * s for n in names]
    total = sum(advances) + tracking * (len(text) - 1)
    x = cx - total / 2
    out = []
    for n, adv in zip(names, advances):
        pen = SVGPathPen(gs)
        gs[n].draw(TransformPen(pen, (s, 0, 0, -s, x, baseline)))
        d = pen.getCommands()
        if d:
            out.append(d)
        x += adv + tracking
    return f'<path d="{" ".join(out)}" fill="{fill}"/>'
