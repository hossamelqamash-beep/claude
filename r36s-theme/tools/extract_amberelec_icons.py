#!/usr/bin/env python3
"""Extract the console icons of the AmberELEC "8bit" theme and rename them to the R36S
(ArkOS / dArkOS) EmulationStation theme folder names.

usage: extract_amberelec_icons.py <extracted amberelec-8bit-master dir> <out dir>

Writes <out>/original/<system>.png (byte-identical copies) and
<out>/scaled/<system>.png (nearest-neighbour, integer scale, longest side <= 512 px).
"""
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from systems import SYSTEMS  # noqa: E402

# R36S theme name -> AmberELEC folder (when the names differ)
ALIAS = {
    "tic80": "tic-80", "pcenginecd": "pce-cd", "tg-cd": "tg16cd", "turbografx": "tg16",
    "fbneo": "fbn", "fba": "fbn", "pokemonmini": "pokemini", "wolf": "ecwolf", "vhs": "mplayer",
    "pico8": "pico-8", "mame2003": "mame", "mame2003plus": "mame", "mame2010": "mame", "mame2000": "mame",
    "gb-hacks": "gbh", "gbc-hacks": "gbch", "gba-hacks": "gbah", "nes-hacks": "nesh", "snes-hacks": "snesh",
    "genesis-hacks": "genh", "favorites": "auto-favorites", "all": "auto-allgames", "recent": "auto-lastplayed",
    "collections": "custom-collections", "dos": "msdos", "options": "tools", "retropie": "tools",
    "coleco": "colecovision", "msx1": "msx", "msumd": "megadrive", "gb2players": "gb", "gbc2players": "gbc",
}
TARGET = 512


def console_path(root, folder):
    t = os.path.join(root, folder, "theme.xml")
    if not os.path.isfile(t):
        return None
    x = open(t, encoding="utf-8", errors="ignore").read()
    m = re.search(r'name="console_overlay"[^>]*>.*?<path>(.*?)</path>', x, re.S)
    if not m:
        return None
    p = os.path.normpath(os.path.join(root, folder, m.group(1).strip()))
    return p if os.path.isfile(p) else None


def native_block(a):
    """Size of the pixel blocks if the art is already upscaled (k x k identical pixels)."""
    for k in (8, 6, 5, 4, 3, 2):
        h, w = a.shape[:2]
        if h % k == 0 and w % k == 0:
            b = a[::k, ::k]
            if np.array_equal(np.repeat(np.repeat(b, k, 0), k, 1), a):
                return k
    return 1


def scaled(path):
    img = Image.open(path).convert("RGBA")
    a = np.asarray(img)
    k = native_block(a)
    if k > 1:
        img = Image.fromarray(a[::k, ::k].copy(), "RGBA")
    f = max(1, TARGET // max(img.size))
    return img.resize((img.width * f, img.height * f), Image.NEAREST), f, k


def main():
    root, out = sys.argv[1], sys.argv[2]
    od, sd = os.path.join(out, "original"), os.path.join(out, "scaled")
    os.makedirs(od, exist_ok=True)
    os.makedirs(sd, exist_ok=True)
    used, missing, rows = set(), [], []
    for name in sorted(SYSTEMS):
        folder = ALIAS.get(name, name)
        src = console_path(root, folder)
        if not src:
            missing.append(name)
            continue
        used.add(folder)
        shutil.copyfile(src, os.path.join(od, name + ".png"))
        img, f, k = scaled(src)
        img.save(os.path.join(sd, name + ".png"), optimize=True)
        rows.append((name, folder, Image.open(src).size, img.size, f, k))
    unmapped = sorted(d for d in os.listdir(root) if console_path(root, d) and d not in used)
    for r in rows:
        print(f"{r[0]:<18} <- {r[1]:<18} {r[2]} -> {r[3]} x{r[4]}" + (f" (native /{r[5]})" if r[5] > 1 else ""))
    print(f"\n{len(rows)} icons; R36S systems without an icon in this theme: {len(missing)}")
    print(" ".join(missing))
    print("AmberELEC icons with no R36S system:", " ".join(unmapped))


if __name__ == "__main__":
    main()
