#!/usr/bin/env python3
"""Builds the static TTFs in es-theme-volta/_fonts from the Google Fonts variable fonts.

usage: python3 fonts.py /path/to/google-fonts/ofl

- Urbanist (UI) -> Medium 500 and SemiBold 600
- Doto (dot-matrix numerals) -> Black 900, rounded dots

EmulationStation pre-loads glyphs 32..127 and sizes every text line from the
tallest one. U+007F (DEL) falls back to the tall .notdef box, which makes all
lines ~25% taller than the type and pushes list text off-centre, so DEL is
mapped to the empty space glyph.
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "es-theme-volta", "_fonts")

JOBS = [
    ("urbanist/Urbanist[wght].ttf", "Urbanist-Medium.ttf", {"wght": 500}),
    ("urbanist/Urbanist[wght].ttf", "Urbanist-SemiBold.ttf", {"wght": 600}),
    ("doto/Doto[ROND,wght].ttf", "Doto-Black.ttf", {"wght": 900, "ROND": 100}),
]


def patch_del(font):
    for table in font["cmap"].tables:
        if table.isUnicode() and 0x20 in table.cmap:
            table.cmap[0x7F] = table.cmap[0x20]


def main(ofl):
    os.makedirs(OUT, exist_ok=True)
    for src, dst, loc in JOBS:
        font = TTFont(os.path.join(ofl, src))
        inst = instancer.instantiateVariableFont(font, loc)
        patch_del(inst)
        inst.save(os.path.join(OUT, dst))
        print("wrote", dst)


if __name__ == "__main__":
    main(sys.argv[1])
