#!/usr/bin/env python3
"""Compose 640x480 preview screens of the VCR OSD theme from its own art, fonts and layout
(positions from _inc/main.xml), since the downloadable zip has no _preview folder.

usage: vcr_previews.py <es-theme-vcr-osd dir> <out dir>
"""
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

T, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
WHITE, LILAC, BLUE, BOX = (240, 240, 248), (140, 156, 255), (0, 15, 192), (228, 228, 236)


def font(px, chunky=True):
    f = ImageFont.truetype(os.path.join(T, "_art/fonts", "OSDTape-Chunky.ttf" if chunky else "OSDTape-Regular.ttf"), px)
    return f


def text(d, xy, s, f, fill, anchor="la"):
    d.fontmode = "1"                      # pixel font: no anti-aliasing
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def var(system, name):
    x = open(os.path.join(T, system, "theme.xml"), encoding="utf-8").read()
    m = re.search(rf"<{name}>(.*?)</{name}>", x)
    return m.group(1) if m else ""


def help_bar(d, items):
    f = font(16)
    x = 16
    for k, label in items:
        text(d, (x, 463), f"{k} {label}", f, BLUE, "lm")
        x += d.textlength(f"{k} {label}", font=f) + 22


def system_view(sysname, colour="blue", games=18):
    im = Image.open(os.path.join(T, f"_art/ui/bg_system_{colour}.png")).convert("RGB")
    art = var(sysname, "sysArt") or sysname
    con = Image.open(os.path.join(T, f"_art/consoles/{art}.png")).convert("RGBA")
    im.paste(con, (140, 46), con)
    logo = Image.open(os.path.join(T, f"_art/logos/{art}.png")).convert("RGBA")
    im.paste(logo, ((640 - logo.width) // 2, 292 + (64 - logo.height) // 2), logo)
    d = ImageDraw.Draw(im)
    text(d, (320, 371), f"{var(sysname, 'sysMaker')} · {var(sysname, 'sysYear')} · {var(sysname, 'sysKind')}", font(16), WHITE, "mm")
    text(d, (320, 395), f"{games} GAMES AVAILABLE", font(16), LILAC, "mm")
    tl = Image.open(os.path.join(T, f"_art/timeline/{art}.png")).convert("RGBA")
    im.paste(tl, (120, 406), tl)
    help_bar(d, [("◀▶", "CHOOSE"), ("A", "SELECT"), ("Y", "RANDOM"), ("START", "MENU")])
    return im


GAMES = ["CHRONO TRIGGER", "DONKEY KONG COUNTRY", "EARTHBOUND", "F-ZERO", "FINAL FANTASY VI", "KIRBY SUPER STAR",
         "MEGA MAN X", "SECRET OF MANA", "STAR FOX", "SUPER METROID"]


def gamelist_view(sysname="snes", colour="blue", sel=0):
    im = Image.open(os.path.join(T, f"_art/ui/bg_gamelist_{colour}.png")).convert("RGB")
    d = ImageDraw.Draw(im)
    f16, f24 = font(16), font(24)
    tag = f"▶ {var(sysname, 'sysName')}"
    tw = round(float(var(sysname, "tagW") or 0.33) * 640)
    d.rectangle((16, 10, 16 + tw, 10 + 24), fill=BOX)
    text(d, (16 + tw / 2, 22), tag, f16, BLUE, "mm")
    y = 56
    for i, g in enumerate(GAMES):
        if y + 36 > 438:
            break
        if i == sel:
            d.rectangle((16, y, 330, y + 35), fill=BOX)
        while d.textlength(g, font=f24) > 300:
            g = g[:-1]
        text(d, (24, y + 18), g.rstrip(), f24, BLUE if i == sel else WHITE, "lm")
        y += 36
    ns = Image.open(os.path.join(T, "_art/ui/no_signal.png")).convert("RGBA")
    im.paste(ns, (486 - ns.width // 2, 186 - ns.height // 2), ns)
    star_f = Image.open(os.path.join(T, "_art/ui/star_filled.png")).convert("RGBA")
    star_u = Image.open(os.path.join(T, "_art/ui/star_unfilled.png")).convert("RGBA")
    for i in range(5):
        s = star_f if i < 4 else star_u
        im.paste(s, (446 + i * 24, 324), s)
    desc = ["A TIME-TRAVELLING RPG.", "SAVE THE FUTURE BY", "CHANGING THE PAST, ONE", "ERA AT A TIME."]
    for i, line in enumerate(desc):
        text(d, (356, 356 + i * 20), line, f16, WHITE)
    help_bar(d, [("▲▼", "CHOOSE"), ("A", "LAUNCH"), ("B", "BACK"), ("Y", "FAVORITE")])
    return im


system_view("snes").save(os.path.join(OUT, "system-snes.png"))
system_view("gba", "navy", 7).save(os.path.join(OUT, "system-gba-navy.png"))
system_view("psx", "midnight", 12).save(os.path.join(OUT, "system-psx-midnight.png"))
system_view("megadrive", "blue", 9).save(os.path.join(OUT, "system-megadrive.png"))
gamelist_view().save(os.path.join(OUT, "gamelist-snes.png"))
Image.open(os.path.join(T, "_art/loading/loading_blue.png")).convert("RGB").save(os.path.join(OUT, "loading.png"))
print("ok")
