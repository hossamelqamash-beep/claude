"""Approximate EmulationStation renders of the theme (for README / sanity checks)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

import consoles
from build_theme import COLORSETS, FONT_SIZES, INK, PAPER, SH, SW
from pixelkit import Art, hexc
from pixeltext import draw_text, text_width
from systems import SYSTEMS

T = None


def font(px, style="Chunky"):
    return ImageFont.truetype(os.path.join(T, "_art", "fonts", f"OSDTape-{style}.ttf"), px)


def text(im, xy, s, px, col, style="Chunky", anchor="lm"):
    ImageDraw.Draw(im).text(xy, s, font=font(px, style), fill=hexc(col), anchor=anchor)


def battery(im):
    """Fake ArkOS status (battery + clock) to show the reserved corner stays clear."""
    d = ImageDraw.Draw(im)
    d.rectangle([590, 10, 621, 25], outline=(255, 255, 255, 255), width=2)
    d.rectangle([622, 14, 625, 21], fill=(255, 255, 255, 255))
    d.rectangle([594, 14, 610, 21], fill=(80, 255, 120, 255))
    text(im, (582, 18), "12:45", 16, "#ffffff", anchor="rm")


def help_line(im, items, bg):
    x = 16
    for icon, label in items:
        text(im, (x, 463), icon, 16, bg)
        x += font(16).getlength(icon) + 6
        text(im, (x, 463), label, 16, bg)
        x += font(16).getlength(label) + 18


def system_view(key, cs="VCR BLUE"):
    c = {"VCR BLUE": "blue", "DEEP NAVY": "navy", "MIDNIGHT": "midnight"}[cs]
    bg, _, dim = COLORSETS[cs]
    im = Image.open(os.path.join(T, "_art", "ui", f"bg_system_{c}.png")).convert("RGBA")
    im.alpha_composite(Image.open(os.path.join(T, "_art", "consoles", f"{key}.png")), (140, 46))
    im.alpha_composite(Image.open(os.path.join(T, "_art", "logos", f"{key}.png")), (80, 292))
    name, maker, year, kind, _ = SYSTEMS[key]
    text(im, (320, 371), f"{maker} · {year} · {kind}", 16, INK, anchor="mm")
    text(im, (320, 395), "42 GAMES AVAILABLE", 16, dim, anchor="mm")
    im.alpha_composite(Image.open(os.path.join(T, "_art", "timeline", f"{key}.png")), (120, 406))
    help_line(im, [("◀▶", "SYSTEM"), ("A", "SELECT"), ("START", "MENU")], bg)
    battery(im)
    return im


GAMES = ["Act Raiser", "Aero Fighters", "Breath of Fire II", "Chrono Trigger",
         "Contra III", "Donkey Kong Country", "EarthBound", "F-Zero", "Final Fight",
         "Kirby Super Star", "Mega Man X", "Secret of Mana", "Star Fox", "Super Metroid",
         "Super Mario World", "Tetris Attack", "Zelda: A Link to the Past"]
DESC = ("Kirby inhales foes, copies their powers and dashes through eight "
        "different adventures in one cartridge, with a second player able to "
        "join in as a helper at any time.")


def fake_cover(key):
    a = Art(56, 76)
    a.rect(0, 0, 55, 75, "#1a1a40")
    for y in range(0, 50):
        a.hl(0, 55, y, ["#ff7ab0", "#ff9ac8", "#ffbadc", "#ffd8ec"][min(3, y // 13)])
    a.rect(0, 50, 55, 75, "#40c060")
    a.ellipse(14, 22, 42, 50, "#ff9ad0", "#a03070")
    a.rect(22, 30, 23, 35, "#202040")
    a.rect(32, 30, 33, 35, "#202040")
    a.ellipse(10, 44, 22, 52, "#e02040")
    a.ellipse(34, 44, 46, 52, "#e02040")
    a.rect(0, 0, 55, 9, "#d02828")
    a.text(4, 2, "SUPER STAR", "#ffffff")
    a.rect(0, 66, 55, 75, "#202040")
    a.text(4, 68, "SNES", "#f0f0f0")
    return a.render(3, sticker=False)


def gamelist_view(key, size="MEDIUM", cs="VCR BLUE", upper=True, sel=9):
    c = {"VCR BLUE": "blue", "DEEP NAVY": "navy", "MIDNIGHT": "midnight"}[cs]
    bg, _, dim = COLORSETS[cs]
    im = Image.open(os.path.join(T, "_art", "ui", f"bg_gamelist_{c}.png")).convert("RGBA")
    d = ImageDraw.Draw(im)
    name = SYSTEMS[key][0]
    tag = "▶ " + name
    w = len(tag) * 12 + 18
    d.rectangle([16, 10, 16 + w - 1, 33], fill=hexc(PAPER))
    text(im, (16 + w // 2, 22), tag, 16, bg, anchor="mm")
    px = FONT_SIZES[size]
    spacing = {16: 1.6, 24: 1.5, 32: 1.4}[px]
    row = int(px * 9 / 8 * spacing)
    rows = 382 // row
    top = max(0, min(sel - rows // 2, len(GAMES) - rows))
    for i, g in enumerate(GAMES[top:top + rows]):
        y = 56 + i * row
        s = g.upper() if upper else g
        f = font(px)
        while f.getlength(s) > 298 and len(s) > 3:
            s = s[:-1]
        if top + i == sel:
            d.rectangle([16, y, 329, y + row - 1], fill=hexc(PAPER))
            text(im, (24, y + row // 2), s, px, bg)
        else:
            text(im, (24, y + row // 2), s, px, INK)
    cover = fake_cover(key)
    im.alpha_composite(cover, (486 - cover.width // 2, 186 - cover.height // 2))
    star_f = Image.open(os.path.join(T, "_art", "ui", "star_filled.png"))
    star_u = Image.open(os.path.join(T, "_art", "ui", "star_unfilled.png"))
    for i in range(5):
        im.alpha_composite(star_f if i < 4 else star_u, (446 + i * 24, 324))
    # description: wrap into the 262px box at 16px
    f = font(16)
    words, lines, cur = DESC.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if f.getlength(t) > 262:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    for i, ln in enumerate(lines[:4]):
        text(im, (356, 364 + i * 22), ln, 16, INK)
    help_line(im, [("▲▼", "CHOOSE"), ("A", "LAUNCH"), ("B", "BACK"), ("Y", "FAV")], bg)
    battery(im)
    return im


def menu_view(cs="VCR BLUE", size="MEDIUM"):
    bg, _, dim = COLORSETS[cs]
    base = gamelist_view("snes", size, cs)
    shade = Image.new("RGBA", (SW, SH), (0, 0, 20, 150))
    base.alpha_composite(shade)
    c = {"VCR BLUE": "blue", "DEEP NAVY": "navy", "MIDNIGHT": "midnight"}[cs]
    frame = Image.open(os.path.join(T, "_art", "ui", f"menu_frame_{c}.png"))
    x0, y0, x1, y1 = 56, 40, 584, 440
    # stretch the nine-patch
    k = 16
    im = Image.new("RGBA", (x1 - x0, y1 - y0))
    W_, H_ = im.size
    fw = frame.width
    for (sx, sw, dx, dw) in [(0, k, 0, k), (k, fw - 2 * k, k, W_ - 2 * k), (fw - k, k, W_ - k, k)]:
        for (sy, sh, dy, dh) in [(0, k, 0, k), (k, fw - 2 * k, k, H_ - 2 * k), (fw - k, k, H_ - k, k)]:
            im.paste(frame.crop((sx, sy, sx + sw, sy + sh)).resize((dw, dh), Image.NEAREST), (dx, dy))
    base.alpha_composite(im, (x0, y0))
    text(base, (320, 72), "MAIN MENU", 32, INK, anchor="mm")
    px = FONT_SIZES[size]
    items = ["GAME SETTINGS", "UI SETTINGS", "SOUND SETTINGS", "THEME CONFIGURATION",
             "SCRAPER", "QUIT"]
    row = int(px * 2)
    for i, it in enumerate(items):
        y = 104 + i * row
        if y + row > 430:
            break
        if i == 3:
            ImageDraw.Draw(base).rectangle([66, y, 573, y + row - 1], fill=hexc(PAPER))
            text(base, (80, y + row // 2), it, px, bg)
            text(base, (560, y + row // 2), "▶", px, bg, anchor="rm")
        else:
            text(base, (80, y + row // 2), it, px, INK)
            text(base, (560, y + row // 2), "▶", px, INK, anchor="rm")
        ImageDraw.Draw(base).line([(66, y + row), (573, y + row)], fill=hexc(dim))
    battery(base)
    return base


def theme_menu_view(cs="VCR BLUE"):
    bg, _, dim = COLORSETS[cs]
    base = system_view("snes", cs)
    base.alpha_composite(Image.new("RGBA", (SW, SH), (0, 0, 20, 150)))
    d = ImageDraw.Draw(base)
    d.rectangle([56, 52, 583, 436], fill=hexc(bg))
    d.rectangle([58, 54, 581, 434], outline=hexc(INK), width=2)
    d.rectangle([62, 58, 577, 430], outline=hexc(dim), width=1)
    text(base, (320, 82), "THEME CONFIGURATION", 24, INK, anchor="mm")
    opts = [("COLOR SET", "VCR BLUE"), ("FONT SIZE", "MEDIUM"), ("FONT STYLE", "CHUNKY VCR"),
            ("LETTER CASE", "ALL CAPS"), ("CRT SCANLINES", "OFF")]
    for i, (k, v) in enumerate(opts):
        y = 112 + i * 52
        if i == 1:
            d.rectangle([66, y, 573, y + 43], fill=hexc(PAPER))
            col = bg
        else:
            col = INK
        text(base, (80, y + 22), k, 24, col)
        text(base, (560, y + 22), "◀ " + v + " ▶", 16, col, anchor="rm")
    text(base, (320, 404), "SMALL · MEDIUM · BIG", 16, dim, anchor="mm")
    battery(base)
    return base


def main(theme, out):
    global T
    T = theme
    os.makedirs(out, exist_ok=True)
    system_view("snes").save(os.path.join(out, "system-snes.png"))
    system_view("genesis").save(os.path.join(out, "system-genesis.png"))
    system_view("gba", "DEEP NAVY").save(os.path.join(out, "system-gba-navy.png"))
    system_view("arcade").save(os.path.join(out, "system-arcade.png"))
    for s in FONT_SIZES:
        gamelist_view("snes", s).save(os.path.join(out, f"gamelist-{s.lower()}.png"))
    menu_view().save(os.path.join(out, "menu.png"))
    theme_menu_view().save(os.path.join(out, "theme-options.png"))
    Image.open(os.path.join(T, "_art", "loading", "loading_blue.png")).save(
        os.path.join(out, "loading.png"))
    # contact sheet of every hardware illustration
    keys = sorted(consoles.ART)
    cols = 8
    tw, th = 240, 160
    rows = (len(keys) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * tw, rows * (th + 18)), hexc("#000fc0"))
    for i, k in enumerate(keys):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.alpha_composite(Image.open(os.path.join(T, "_art", "consoles", "small", f"{k}.png")), (x, y))
        draw_text(sheet, x + 6, y + th + 4, k.upper()[:18], 1, hexc(INK))
    sheet.save(os.path.join(out, "all-systems.png"))
    print("previews written to", out)


if __name__ == "__main__":
    main(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]))
