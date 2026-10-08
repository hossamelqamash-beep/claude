"""Build the OSD Tape pixel fonts (Regular + Chunky) as TrueType files.

One font pixel is 100 font units and the em is 800 units, so the font is
pixel-perfect at 8, 16, 24 and 32 px. The theme uses exactly those sizes.
"Chunky" widens every pixel run by half a pixel to the right, the way VCR
on-screen-display characters have heavy verticals and thin horizontals.
"""
import sys

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from glyphs import ADVANCE, CAP, GLYPHS, pixels

PX = 100
UPM = 8 * PX
ASC = 9 * PX
DESC = 2 * PX


def rects_for(ch, bold):
    rows = {}
    for c, r in pixels(ch):
        rows.setdefault(r, set()).add(c)
    spans = []
    for r, cols in rows.items():
        cols = sorted(cols)
        start = prev = cols[0]
        for c in cols[1:] + [None]:
            if c is not None and c == prev + 1:
                prev = c
                continue
            spans.append((r, start, prev))
            if c is not None:
                start = prev = c
    # merge identical spans on consecutive rows into taller rectangles
    spans.sort(key=lambda s: (s[1], s[2], s[0]))
    rects = []
    for r, c0, c1 in spans:
        if rects and rects[-1][1] == c0 and rects[-1][2] == c1 and rects[-1][3] == r - 1:
            rects[-1][3] = r
        else:
            rects.append([r, c0, c1, r])
    out = []
    for r0, c0, c1, r1 in rects:
        x0 = c0 * PX
        x1 = (c1 + 1) * PX + (PX // 2 if bold else 0)
        # row r spans from (CAP - r) * PX at the top down to (CAP - r - 1) * PX
        ytop = (CAP - r0) * PX
        ybot = (CAP - r1 - 1) * PX
        out.append((x0, ybot, x1, ytop))
    return out


def draw_glyph(rects):
    pen = TTGlyphPen(None)
    for x0, y0, x1, y1 in rects:
        pen.moveTo((x0, y0))
        pen.lineTo((x0, y1))
        pen.lineTo((x1, y1))
        pen.lineTo((x1, y0))
        pen.closePath()
    return pen.glyph()


def notdef():
    pen = TTGlyphPen(None)
    for (x0, y0, x1, y1), cw in [((0, 0, 500, 700), True), ((100, 100, 400, 600), False)]:
        pts = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
        if not cw:
            pts.reverse()
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def build(path, bold):
    style = "Chunky" if bold else "Regular"
    chars = sorted(GLYPHS)
    names = [".notdef"] + ["uni%04X" % ord(c) for c in chars]
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap({ord(c): "uni%04X" % ord(c) for c in chars})
    glyf = {".notdef": notdef()}
    metrics = {".notdef": (ADVANCE * PX, 0)}
    for c in chars:
        rects = rects_for(c, bold)
        glyf["uni%04X" % ord(c)] = draw_glyph(rects)
        lsb = min((r[0] for r in rects), default=0)
        metrics["uni%04X" % ord(c)] = (ADVANCE * PX, lsb)
    # nbsp shares the space glyph
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASC, descent=-DESC, lineGap=0)
    fb.setupNameTable({
        "familyName": "OSD Tape " + style,
        "styleName": "Regular",
        "uniqueFontIdentifier": "OSDTape-" + style,
        "fullName": "OSD Tape " + style,
        "psName": "OSDTape-" + style,
        "version": "Version 1.000",
        "copyright": "OSD Tape pixel font, made for the VCR OSD EmulationStation theme",
        "licenseDescription": "SIL Open Font License 1.1",
    })
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=-DESC, sTypoLineGap=0,
                usWinAscent=ASC, usWinDescent=DESC, sxHeight=5 * PX,
                sCapHeight=CAP * PX, achVendID="OSDT", fsType=0)
    fb.setupPost(isFixedPitch=1)
    fb.save(path)


if __name__ == "__main__":
    out = sys.argv[1]
    build(f"{out}/OSDTape-Chunky.ttf", True)
    build(f"{out}/OSDTape-Regular.ttf", False)
    print("fonts written to", out)
