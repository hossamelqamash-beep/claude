"""Shared helpers: shape text into outlined SVG paths and export logo variants."""
import io
import os
import zipfile

import cairosvg
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_cache = {}


def _font(name):
    if name not in _cache:
        path = os.path.join(FONT_DIR, name)
        blob = hb.Blob.from_file_path(path)
        _cache[name] = (TTFont(path), hb.Font(hb.Face(blob)))
    return _cache[name]


def text_path(text, font, size, x=0, y=0, tracking=0.0):
    """Return (svg path d, advance width) for text with baseline at y."""
    tt, hbfont = _font(font)
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    s = size / upem
    pen = SVGPathPen(gs)
    cx = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        tp = TransformPen(pen, (s, 0, 0, -s, x + (cx + pos.x_offset) * s, y - pos.y_offset * s))
        gs[g].draw(tp)
        cx += pos.x_advance + tracking * upem
    width = (cx - tracking * upem) * s
    return pen.getCommands(), width


def cap_height(font, size):
    tt, _ = _font(font)
    return tt["OS/2"].sCapHeight * size / tt["head"].unitsPerEm


def svg_doc(body, w, h, pad=0):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}" '
        f'width="{w + 2 * pad}" height="{h + 2 * pad}">\n{body}\n</svg>\n'
    )


def export(slug, title, builders, variants, out_dir, png_width=2400):
    """builders: {layout: fn(palette)->(body,w,h)}; variants: {name: palette}."""
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, f"{slug}.zip")
    previews = []
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for layout, fn in builders.items():
            for vname, pal in variants.items():
                body, w, h = fn(pal)
                pad = round(max(w, h) * 0.04)
                svg = svg_doc(body, w, h, pad)
                base = f"{slug}_{layout}_{vname}"
                z.writestr(f"{slug}/SVG/{base}.svg", svg)
                scale = png_width / (w + 2 * pad) if layout != "icon" else 1600 / (w + 2 * pad)
                png = cairosvg.svg2png(bytestring=svg.encode(), scale=scale)
                z.writestr(f"{slug}/PNG/{base}.png", png)
                previews.append((layout, vname, pal, png))
    return zpath, previews


def preview_sheet(title, previews, path):
    """Contact sheet with each variant on a fitting background (PNG via cairosvg)."""
    import base64

    cols, cw, ch = 4, 560, 300
    layouts = sorted({p[0] for p in previews}, key=lambda l: l != "primary")
    rows = len(layouts)
    parts = []
    for r, layout in enumerate(layouts):
        items = [p for p in previews if p[0] == layout]
        for c, (_, vname, pal, png) in enumerate(items):
            x, y = c * cw, r * ch
            bg = pal["bg"]
            parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{bg}"/>')
            from PIL import Image

            im = Image.open(io.BytesIO(png))
            iw, ih = im.size
            k = min((cw - 80) / iw, (ch - 80) / ih)
            dw, dh = iw * k, ih * k
            b64 = base64.b64encode(png).decode()
            parts.append(
                f'<image x="{x + (cw - dw) / 2}" y="{y + (ch - dh) / 2}" width="{dw}" height="{dh}" '
                f'href="data:image/png;base64,{b64}"/>'
            )
    svg = svg_doc("\n".join(parts), cols * cw, rows * ch)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=path)
