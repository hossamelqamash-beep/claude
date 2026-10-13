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


def tight_svg(body, w, h, margin=0.035):
    """Measure real ink bounds by rendering, then return an SVG cropped to them."""
    from PIL import Image

    big = max(w, h)
    pad = big * 0.3
    probe = svg_doc(body, w, h, pad)
    k = 1500 / (big + 2 * pad)
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=probe.encode(), scale=k)))
    x0, y0, x1, y1 = im.getchannel("A").getbbox()
    x0, y0, x1, y1 = (v / k - pad for v in (x0, y0, x1, y1))
    m = max(x1 - x0, y1 - y0) * margin
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    W, H = x1 - x0, y1 - y0
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {W:.2f} {H:.2f}" '
        f'width="{W:.0f}" height="{H:.0f}">\n{body}\n</svg>\n'
    )
    return svg, W, H


def export(slug, title, builders, variants, out_dir, png_width=2400):
    """builders: {layout: fn(palette)->(body,w,h)}; variants: {name: palette}."""
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, f"{slug}.zip")
    previews = []
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for layout, fn in builders.items():
            for vname, pal in variants.items():
                body, w, h = fn(pal)
                svg, w, h = tight_svg(body, w, h)
                pad = 0
                base = f"{slug}_{layout}_{vname}"
                z.writestr(f"{slug}/SVG/{base}.svg", svg)
                scale = (1600 if layout == "icon" else png_width) / max(w, h if layout == "icon" else 0)
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


# ---------------------------------------------------------------- layouts
def text_block(p, lines, align="left"):
    """lines: dicts {t, f, s, c(palette key), tr(tracking em), gap(px before)}.
    Origin = top of first line's caps. Returns dict(body, w, h, rows)."""
    rows = []
    for l in lines:
        _, w = text_path(l["t"], l["f"], l["s"], tracking=l.get("tr", 0))
        rows.append([l, w])
    W = max(w for _, w in rows)
    y, parts, out = 0.0, [], []
    for i, (l, w) in enumerate(rows):
        y += (l.get("gap", 0.3 * l["s"]) if i else 0) + cap_height(l["f"], l["s"])
        x = 0 if align == "left" else (W - w) / 2
        d, _ = text_path(l["t"], l["f"], l["s"], x + l.get("dx", 0), y, tracking=l.get("tr", 0))
        parts.append(f'<path d="{d}" fill="{p[l["c"]]}"/>')
        out.append({"x": x, "y": y, "w": w})
    return {"body": "".join(parts), "w": W, "h": y, "rows": out}


def lockup_h(p, icon_fn, lines, ratio=1.3, space=0.38):
    tb = text_block(p, lines)
    isz = tb["h"] * ratio
    tx = isz * (1 + space)
    ty = (isz - tb["h"]) / 2
    body = icon_fn(p, 0, 0, isz / 100) + f'<g transform="translate({tx} {ty})">{tb["body"]}</g>'
    return body, round(tx + tb["w"]), round(isz)


def lockup_v(p, icon_fn, lines, isz=190, space=56):
    tb = text_block(p, lines, align="center")
    W = max(tb["w"], isz)
    body = icon_fn(p, (W - isz) / 2, 0, isz / 100) + (
        f'<g transform="translate({(W - tb["w"]) / 2} {isz + space})">{tb["body"]}</g>'
    )
    return body, round(W), round(isz + space + tb["h"] + 8)


def g(ox, oy, k, inner):
    return f'<g transform="translate({ox} {oy}) scale({k})">{inner}</g>'


def mono(light):
    """Return the standard 4 variants from light/dark palettes."""
    blk = {k: "#000000" for k in light}
    wht = {k: "#FFFFFF" for k in light}
    blk["bg"], wht["bg"] = "#FFFFFF", "#111111"
    return blk, wht
