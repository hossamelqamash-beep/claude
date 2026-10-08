"""Tiny pixel-art toolkit: draw at low resolution, upscale with nearest-neighbour."""
import math

from PIL import Image, ImageDraw, ImageFilter

STICKER = (236, 236, 244, 255)
SHADOW = (0, 0, 40, 150)


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def C(c):
    return hexc(c) if isinstance(c, str) else c


def mixc(a, b, t):
    a, b = C(a), C(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (255,)


def lit(c, t=0.25):
    return mixc(c, (255, 255, 255, 255), t)


def drk(c, t=0.25):
    return mixc(c, (8, 8, 32, 255), t)


# 3x5 micro font for printed labels on hardware
MICRO = {
    "A": "010101111101101", "B": "110101110101110", "C": "011100100100011",
    "D": "110101101101110", "E": "111100110100111", "F": "111100110100100",
    "G": "011100101101011", "H": "101101111101101", "I": "111010010010111",
    "J": "001001001101010", "K": "101101110101101", "L": "100100100100111",
    "M": "101111111101101", "N": "110101101101101", "O": "010101101101010",
    "P": "110101110100100", "Q": "010101101110011", "R": "110101110101101",
    "S": "011100010001110", "T": "111010010010010", "U": "101101101101111",
    "V": "101101101101010", "W": "101101111111101", "X": "101101010101101",
    "Y": "101101010010010", "Z": "111001010100111", "0": "111101101101111",
    "1": "010110010010111", "2": "110001010100111", "3": "110001010001110",
    "4": "101101111001001", "5": "111100110001110", "6": "011100111101111",
    "7": "111001010010010", "8": "111101111101111", "9": "111101111001110",
    "-": "000000111000000", ".": "000000000000010", " ": "000000000000000",
    "/": "001001010100100", "+": "000010111010000", ":": "000010000010000",
    "!": "010010010000010", "?": "110001010000010", "&": "010101010101011",
    "'": "010010000000000", ">": "100010001010100", "<": "001010100010001",
}


class Art:
    def __init__(self, w=120, h=80):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    # ------------------------------------------------------------ primitives
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.im.putpixel((int(x), int(y)), C(c))

    def rect(self, x0, y0, x1, y1, c):
        if x1 >= x0 and y1 >= y0:
            self.d.rectangle([x0, y0, x1, y1], fill=C(c))

    def line(self, pts, c, w=1):
        self.d.line(pts, fill=C(c), width=w)

    def hl(self, x0, x1, y, c):
        self.rect(x0, y, x1, y, c)

    def vl(self, x, y0, y1, c):
        self.rect(x, y0, x, y1, c)

    def ellipse(self, x0, y0, x1, y1, c, ol=None):
        self.d.ellipse([x0, y0, x1, y1], fill=C(c), outline=C(ol) if ol else None)

    def poly(self, pts, c, ol=None):
        self.d.polygon(pts, fill=C(c), outline=C(ol) if ol else None)

    def blk(self, x0, y0, x1, y1, c, r=0, ol="auto", bevel=True, hi=0.3, sh=0.28):
        """Bevelled block with a darker outline. Coordinates are inclusive."""
        c = C(c)
        o = drk(c, 0.62) if ol == "auto" else (C(ol) if ol else None)
        if r:
            self.d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=c, outline=o)
        else:
            self.d.rectangle([x0, y0, x1, y1], fill=c, outline=o)
        if bevel and x1 - x0 >= 3 and y1 - y0 >= 3:
            k = max(r - 1, 0)
            b = 1 if o else 0
            self.hl(x0 + b + k, x1 - b - k, y0 + b, lit(c, hi))
            self.vl(x0 + b, y0 + b + k, y1 - b - k, lit(c, hi * 0.45))
            self.hl(x0 + b + k, x1 - b - k, y1 - b, drk(c, sh))
            self.vl(x1 - b, y0 + b + k, y1 - b - k, drk(c, sh * 0.55))

    def slab(self, x0, y0, x1, y1, top, front, depth=6, r=1):
        """Box seen slightly from above: lighter top face over a front face."""
        self.blk(x0, y0 + depth, x1, y1, front, r=r)
        self.blk(x0, y0, x1, y0 + depth, top, r=r, sh=0.1)

    def grille(self, x0, y0, x1, y1, c, step=2, vertical=False):
        if vertical:
            for x in range(x0, x1 + 1, step):
                self.vl(x, y0, y1, c)
        else:
            for y in range(y0, y1 + 1, step):
                self.hl(x0, x1, y, c)

    def dots(self, x0, y0, x1, y1, c, step=2):
        for y in range(y0, y1 + 1, step):
            for x in range(x0 + ((y - y0) // step) % 2, x1 + 1, step):
                self.px(x, y, c)

    def text(self, x, y, s, c, scale=1):
        cx = x
        for ch in s.upper():
            bits = MICRO.get(ch, MICRO[" "])
            for i, b in enumerate(bits):
                if b == "1":
                    self.rect(cx + (i % 3) * scale, y + (i // 3) * scale,
                              cx + (i % 3) * scale + scale - 1, y + (i // 3) * scale + scale - 1, c)
            cx += 4 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 4 * scale - scale

    def ctext(self, cx, y, s, c, scale=1):
        self.text(cx - self.text_w(s, scale) // 2, y, s, c, scale)

    # ------------------------------------------------------------ parts
    def button(self, cx, cy, c, r=1):
        c = C(c)
        if r <= 1:
            self.rect(cx - 1, cy - 1, cx + 1, cy + 1, drk(c, 0.55))
            self.rect(cx, cy - 1, cx, cy + 1, c)
            self.rect(cx - 1, cy, cx + 1, cy, c)
            self.px(cx, cy - 1, lit(c, 0.45))
            self.px(cx - 1, cy - 1, drk(c, 0.55))
        else:
            self.ellipse(cx - r, cy - r, cx + r, cy + r, c, drk(c, 0.55))
            self.px(cx - r + 1, cy - r + 1, lit(c, 0.55))
            self.px(cx - r + 2 if r > 2 else cx, cy - r + 1, lit(c, 0.35))

    def dpad(self, cx, cy, c="#222228", size=2):
        c = C(c)
        o = drk(c, 0.5)
        s = size
        self.rect(cx - s, cy - 1 - (s > 2), cx + s, cy + 1 + (s > 2), o)
        self.rect(cx - 1 - (s > 2), cy - s, cx + 1 + (s > 2), cy + s, o)
        t = s - 1
        self.rect(cx - t, cy - (s > 2), cx + t, cy + (s > 2), c)
        self.rect(cx - (s > 2), cy - t, cx + (s > 2), cy + t, c)
        self.px(cx - (s > 2), cy - t, lit(c, 0.4))

    def stick(self, cx, cy, c="#222228", ball="#c02020", h=6):
        self.blk(cx - 3, cy, cx + 3, cy + 2, drk(c, 0.2), bevel=False)
        self.rect(cx, cy - h + 2, cx, cy, drk(c, 0.1))
        self.ellipse(cx - 2, cy - h - 1, cx + 2, cy - h + 3, ball, drk(ball, 0.5))
        self.px(cx - 1, cy - h, lit(ball, 0.6))

    def screen(self, x0, y0, x1, y1, kind="color", bezel="#2a2a33", pad=2):
        if bezel:
            self.blk(x0, y0, x1, y1, bezel, r=1, bevel=False)
            x0, y0, x1, y1 = x0 + pad, y0 + pad, x1 - pad, y1 - pad
        scene(self, x0, y0, x1, y1, kind)

    def cable(self, pts, c="#1a1a22"):
        self.line(pts, c)

    def cart(self, x0, y0, x1, y1, c, label="#e8e0c8", accent=None, ridges=True):
        self.blk(x0, y0, x1, y1, c, r=1)
        lx0, lx1 = x0 + 2, x1 - 2
        ly0, ly1 = y0 + 2, y0 + max(3, (y1 - y0) * 2 // 3)
        self.rect(lx0, ly0, lx1, ly1, label)
        if accent:
            self.rect(lx0, ly0, lx1, ly0 + 1, accent)
            self.rect(lx0 + 1, ly0 + 3, lx0 + 3, ly1 - 1, mixc(accent, label, 0.4))
            for yy in range(ly0 + 3, ly1, 2):
                self.hl(lx0 + 5, lx1 - 1, yy, mixc(label, "#606070", 0.5))
        if ridges and y1 - ly1 > 3:
            for yy in range(ly1 + 2, y1 - 1, 2):
                self.hl(x0 + 2, x1 - 2, yy, drk(c, 0.2))

    def disc(self, cx, cy, r, c="#c8ccd8"):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, c, drk(c, 0.5))
        self.ellipse(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2, lit(c, 0.2))
        for i, col in enumerate(["#ff70c0", "#70e0ff", "#ffe070"]):
            a = -2.4 + i * 0.35
            self.px(int(cx + math.cos(a) * (r - 2)), int(cy + math.sin(a) * (r - 2)), col)
        self.ellipse(cx - 2, cy - 2, cx + 2, cy + 2, drk(c, 0.15), drk(c, 0.5))
        self.px(cx, cy, (0, 0, 0, 0))

    # ------------------------------------------------------------ output
    def render(self, scale=3, sticker=True):
        im = self.im
        w, h = im.size
        alpha = im.getchannel("A").point(lambda a: 255 if a > 0 else 0)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        if sticker:
            sh = Image.new("RGBA", (w, h), SHADOW)
            outline_mask = alpha.filter(ImageFilter.MaxFilter(3))
            sh_mask = Image.new("L", (w, h), 0)
            sh_mask.paste(outline_mask.crop((0, 0, w - 2, h - 2)), (2, 2))
            out.paste(sh, (0, 0), sh_mask)
            out.paste(Image.new("RGBA", (w, h), STICKER), (0, 0), outline_mask)
        out.alpha_composite(im)
        return out.resize((w * scale, h * scale), Image.NEAREST)


# ---------------------------------------------------------------- screens
SCREEN_PAL = {
    "color": dict(sky=["#3a6cf0", "#5a8cff", "#8ab4ff"], ground="#3aa040", g2="#2a7030",
                  brick="#c06030", hero="#e02828", sun="#ffe060", hill="#2a8a3a"),
    "gb": dict(sky=["#9bbc0f", "#9bbc0f", "#8bac0f"], ground="#306230", g2="#0f380f",
               brick="#306230", hero="#0f380f", sun="#8bac0f", hill="#8bac0f"),
    "gbc": dict(sky=["#58a8f8", "#78c0ff", "#a8d8ff"], ground="#f8b830", g2="#c87818",
                brick="#e05818", hero="#f83838", sun="#ffffff", hill="#38b838"),
    "vb": dict(sky=["#100000", "#100000", "#180000"], ground="#e00000", g2="#800000",
               brick="#a00000", hero="#ff2020", sun="#600000", hill="#500000"),
    "amber": dict(sky=["#1a0e00", "#1a0e00", "#1a0e00"], ground="#ffb000", g2="#a06000",
                  brick="#c07800", hero="#ffd060", sun="#603800", hill="#402400"),
    "green": dict(sky=["#001a06", "#001a06", "#001a06"], ground="#30ff70", g2="#18a040",
                  brick="#20c050", hero="#a0ffc0", sun="#0a4a1a", hill="#0a3a14"),
    "lcd": dict(sky=["#b8bca8", "#b8bca8", "#b0b4a0"], ground="#40443c", g2="#585c50",
                brick="#585c50", hero="#202418", sun="#a0a490", hill="#a8ac98"),
    "dusk": dict(sky=["#301860", "#a03070", "#f07040"], ground="#202048", g2="#101030",
                 brick="#402060", hero="#ffe040", sun="#ffd040", hill="#281850"),
    "space": dict(sky=["#000018", "#000020", "#00002a"], ground="#303060", g2="#202040",
                  brick="#404080", hero="#40e0ff", sun="#ffffff", hill="#101028"),
    "osd": dict(sky=["#000fc0", "#000fc0", "#000fc0"], ground="#000fc0", g2="#000fc0",
                brick="#000fc0", hero="#ffffff", sun="#ffffff", hill="#000fc0"),
}


def scene(a, x0, y0, x1, y1, kind):
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if w < 4 or h < 4:
        a.rect(x0, y0, x1, y1, "#3050c0")
        return
    if kind == "vector":
        a.rect(x0, y0, x1, y1, "#04040c")
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        glow = "#f0f4ff"
        a.line([(cx - w // 4, cy + h // 4), (cx, cy - h // 3), (cx + w // 4, cy + h // 4),
                (cx - w // 4, cy + h // 4)], glow)
        a.line([(x0 + 2, y1 - 3), (x1 - 2, y1 - 3)], "#7080ff")
        for i in range(3):
            a.px(x0 + 3 + i * (w // 3), y0 + 2 + (i % 2) * 3, glow)
        return
    if kind == "osd":
        a.rect(x0, y0, x1, y1, "#000fc0")
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        a.poly([(cx - 2, cy - 3), (cx - 2, cy + 3), (cx + 2, cy)], "#f0f0f8")
        if w > 14:
            a.text(x0 + 2, y0 + 2, "PLAY", "#f0f0f8")
        return
    if kind == "dos":
        a.rect(x0, y0, x1, y1, "#000000")
        a.text(x0 + 1, y0 + 1, "C:", "#c0c0c0")
        a.rect(x0 + 9, y0 + 5, x0 + 10, y0 + 5, "#c0c0c0")
        for i in range(min(3, (h - 8) // 3)):
            a.hl(x0 + 1, x0 + 1 + (w - 4) * (3 - i) // 4, y0 + 8 + i * 3, "#808080")
        return
    if kind == "basic":
        a.rect(x0, y0, x1, y1, "#4040e0")
        a.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, "#3030b0")
        a.text(x0 + 2, y0 + 2, "READY", "#a0a0ff")
        a.rect(x0 + 2, y0 + 8, x0 + 4, y0 + 12, "#a0a0ff")
        return
    if kind == "amiga":
        a.rect(x0, y0, x1, y1, "#e0e0e0")
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        a.blk(cx - 4, cy - 4, cx + 4, cy + 4, "#f0f0f0", r=1)
        a.rect(cx - 2, cy - 2, cx + 2, cy + 2, "#3060d0")
        return
    p = SCREEN_PAL.get(kind, SCREEN_PAL["color"])
    bands = p["sky"]
    for i in range(h):
        a.hl(x0, x1, y0 + i, bands[min(len(bands) - 1, i * len(bands) // h)])
    gy = y0 + h * 3 // 4
    if w > 10:
        a.ellipse(x1 - 5, y0 + 2, x1 - 3, y0 + 4, p["sun"])
        for x in range(x0, x1 + 1):
            hh = int(3 + 2 * math.sin((x - x0) / 3.0))
            a.vl(x, gy - hh, gy - 1, p["hill"])
    a.rect(x0, gy, x1, y1, p["ground"])
    for x in range(x0, x1 + 1, 3):
        a.px(x, gy, p["g2"])
    if h > 9 and w > 12:
        bx = x0 + w // 2
        a.rect(bx, gy - 7, bx + 4, gy - 6, p["brick"])
        a.px(bx + 2, gy - 9, p["sun"])
    hx = x0 + max(2, w // 5)
    a.rect(hx, gy - 3, hx + 1, gy - 1, p["hero"])
    a.px(hx, gy - 4, p["hero"])
    # glass glare
    a.px(x0, y0, lit(bands[0], 0.7))
    if w > 8:
        a.hl(x0 + 1, x0 + 2, y0, lit(bands[0], 0.45))
