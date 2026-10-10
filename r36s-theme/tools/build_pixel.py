#!/usr/bin/env python3
"""Pixel-art packs for every R36S system, named like the EmulationStation theme folders.

  pixel/logos/<system>.png     pixel-art version of each system's logo
  pixel/consoles/<system>.png  pixel-art version of each real console / computer / arcade board

The pixel art is made by sampling the original artwork onto a coarse pixel grid
(area average), reducing it to a limited palette without dithering, hard-edging the
alpha and scaling up with nearest-neighbour. Nothing is redrawn or recoloured, so
the shapes, proportions, markings and colours of the originals are preserved.
"""
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import gfx  # noqa: E402
from systems import SYSTEMS  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
OUT = os.path.join(ROOT, "pixel")
CACHE = os.path.join(TOOLS, ".cache")
CARBON = os.path.join(CACHE, "carbon", "art")
ABN = os.path.join(CACHE, "art-book-next")  # extra official logos (DOS, Tools)
F_DISPLAY = os.path.join(TOOLS, "fonts", "BarlowCondensed-Bold.ttf")

SCALE = 4                     # nearest-neighbour upscale of the final pixel grid
LOGO_GRID = (176, 64)         # max pixel-grid size of a logo
CONSOLE_GRID = (160, 112)     # max pixel-grid size of a console
LOGO_COLORS = 24
CONSOLE_COLORS = 32

# logos missing from Carbon that Art Book Next ships officially
EXTRA_LOGOS = {"msdos": "dos", "dos": "dos", "tools": "tools", "options": "tools", "retropie": "tools"}

# console image aliases (theme folder -> Carbon console image)
CONSOLE_ALIAS = {"coleco": "colecovision", "msdos": "dos", "megadrive": "megadrive", "gb-hacks": "gbh",
                 "gbc-hacks": "gbch", "gba-hacks": "gbah", "nes-hacks": "nesh", "snes-hacks": "snesh",
                 "genesis-hacks": "genh", "atarixegs": "xegs", "pokemonmini": "pokemini"}

# entries that are not a physical console (collections, menus, engines, ports, fantasy consoles)
NOT_HARDWARE = {
    "auto-favorites", "favorites", "auto-lastplayed", "recent", "auto-allgames", "all", "auto-at2players",
    "auto-at4players", "auto-neverplayed", "custom-collections", "collections", "options", "tools", "retropie",
    "setup", "retroarch", "ports", "scummvm", "openbor", "doom", "wolf", "cavestory", "easyrpg", "solarus",
    "love2d", "lutro", "onscripter", "puzzlescript", "vhs", "mess", "pico-8", "pico8", "tic80", "wasm4",
    "lowresnx", "vircon32", "j2me",
}


def render_svg(path, width=1600):
    tmp = os.path.join(CACHE, "pixel_render.png")
    subprocess.check_call(["rsvg-convert", "-w", str(width), "-a", path, "-o", tmp])
    return Image.open(tmp).convert("RGBA")


def area_downscale(img, grid):
    """Fit img into grid (w, h) using a premultiplied box filter (true area average)."""
    s = min(grid[0] / img.width, grid[1] / img.height)
    w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
    a = np.asarray(img).astype(np.float32) / 255.0
    pm = a.copy()
    pm[..., :3] *= pm[..., 3:4]
    pm_img = [Image.fromarray(pm[..., i]) for i in range(4)]
    out = np.stack([np.asarray(c.resize((w, h), Image.BOX)) for c in pm_img], -1)
    alpha = out[..., 3:4]
    rgb = np.where(alpha > 1e-4, out[..., :3] / np.maximum(alpha, 1e-4), 0)
    return np.concatenate([np.clip(rgb, 0, 1), alpha], -1)


def pixelate(img, grid, colors, alpha_cut=0.5):
    a = area_downscale(gfx.trim(img), grid)
    opaque = a[..., 3] >= alpha_cut
    rgb = Image.fromarray((a[..., :3] * 255 + 0.5).astype(np.uint8), "RGB")
    # palette from the opaque pixels only, no dithering (clean pixel-art clusters)
    pal_src = np.asarray(rgb)[opaque]
    if len(pal_src) == 0:
        raise ValueError("empty image")
    strip = Image.fromarray(pal_src.reshape(1, -1, 3), "RGB")
    pal = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = rgb.quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB")
    out = np.concatenate([np.asarray(q), (opaque * 255).astype(np.uint8)[..., None]], -1)
    small = Image.fromarray(out, "RGBA")
    big = small.resize((small.width * SCALE, small.height * SCALE), Image.NEAREST)
    return small, big


def save(img, path):
    # indexed PNG keeps files small and the palette exact
    img.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(path, optimize=True)


def logo_source(theme, s):
    if theme in EXTRA_LOGOS:
        p = os.path.join(ABN, "logos", EXTRA_LOGOS[theme] + ".svg")
        if os.path.exists(p):
            return render_svg(p), "Art Book Next"
    key = s["logo"]
    if key:
        svg = os.path.join(CARBON, "logos", key + ".svg")
        png = os.path.join(CARBON, "logos", key + ".png")
        if os.path.exists(svg):
            return render_svg(svg), "Carbon"
        if os.path.exists(png):
            return Image.open(png).convert("RGBA"), "Carbon"
    # no official logo exists in the packs: plain wordmark in the system's colour
    return gfx.tint(gfx.text_image(s["mark"], F_DISPLAY, 220, (255, 255, 255, 255), 6),
                    gfx.hex_rgb(s["color"] or "D0D0D8")), "wordmark"


def console_source(theme, s):
    if theme in NOT_HARDWARE:
        return None
    for key in (CONSOLE_ALIAS.get(theme, theme), s["logo"]):
        if key:
            p = os.path.join(CARBON, "consoles", key + ".png")
            if os.path.exists(p):
                return Image.open(p).convert("RGBA")
    return None


def main():
    ld, cd = os.path.join(OUT, "logos"), os.path.join(OUT, "consoles")
    for d in (ld, cd):   # keep pixel/README.md
        if os.path.isdir(d):
            shutil.rmtree(d)
    os.makedirs(ld)
    os.makedirs(cd)
    report = {"wordmark": [], "no_console": []}
    for theme, s in sorted(SYSTEMS.items()):
        img, src = logo_source(theme, s)
        if src == "wordmark":
            report["wordmark"].append(theme)
        _, big = pixelate(img, LOGO_GRID, LOGO_COLORS, alpha_cut=0.42)
        save(big, os.path.join(ld, theme + ".png"))
        c = console_source(theme, s)
        if c is None:
            report["no_console"].append(theme)
            continue
        _, big = pixelate(c, CONSOLE_GRID, CONSOLE_COLORS)
        save(big, os.path.join(cd, theme + ".png"))
    # collection logos are original hand-built pixel art, not conversions
    import build_pixel_collections
    build_pixel_collections.main()
    n_logo, n_con = len(os.listdir(ld)), len(os.listdir(cd))
    print(f"logos: {n_logo}  consoles: {n_con}")
    print("wordmark logos (no official logo in the packs):", " ".join(report["wordmark"]))
    print("no console:", " ".join(report["no_console"]))


if __name__ == "__main__":
    main()
