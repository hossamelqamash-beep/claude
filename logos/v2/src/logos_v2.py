"""Logo set v2 — all 17 workshops on the brand palette.
Concept mix: wordmarks (text only), marks embedded in the lettering, and
combination marks (symbol + text).
Run: python3 logos_v2.py <kit_dir> <out_dir> [only_number]"""
import math
import sys

sys.path.insert(0, sys.argv[1])
from logokit import (  # noqa: E402
    cap_height, circle_d, export, g, glyph_bounds, knockout, lockup_h, lockup_v, mono,
    preview_sheet, rich, rrect, stem, text_block, text_path, x_height,
)

OUT = sys.argv[2]
ONLY = sys.argv[3] if len(sys.argv) > 3 else None

# Brand palette (slightly tuned: deeper tints where a colour sits on white)
NAVY = "#2A3649"
CYAN, CYAN_D = "#20E0E0", "#12BFC4"
BLUE = "#00A2EA"
ORANGE = "#F85E35"
YELLOW, YELLOW_D = "#FBB414", "#E29A00"
GREEN, GREEN_D = "#00CC99", "#00A882"
SKY = "#80DBFF"
INDIGO = "#3F37C9"
VIOLET = "#8164FF"
PURPLE = "#672496"
PINK = "#ED1E6C"
DARK_BG = NAVY
WHITE = "#FFFFFF"

LOGOS = []


def logo(num, slug, kind, light, dark, builders):
    light = {"bg": WHITE, **light}
    dark = {"bg": DARK_BG, **dark}
    LOGOS.append((num, slug, kind, light, dark, builders))


def icon_only(fn):
    return lambda p: (fn(p, 0, 0, 1), 100, 100)


def place(body, dx, dy):
    return f'<g transform="translate({dx:.2f} {dy:.2f})">{body}</g>'


# =========================================================== 01 Doing the Right Thing  [embedded]
# the dot of the "i" in "right" becomes a check mark
F01, F01s = "PoppinsSemi.ttf", "PoppinsMed.ttf"


def check_i(p, x, y, S):
    x0, _, x1, _, _ = glyph_bounds("ı", F01, S)
    d, _ = text_path("ı", F01, S, x, y)
    sw = (x1 - x0) * 0.9
    vx, vy = x + (x0 + x1) / 2, y - x_height(F01, S) - 0.1 * S
    pts = f"{vx - 0.15 * S:.1f},{vy - 0.14 * S:.1f} {vx:.1f},{vy:.1f} {vx + 0.24 * S:.1f},{vy - 0.33 * S:.1f}"
    return (f'<path d="{d}" fill="{p["main"]}"/><polyline points="{pts}" fill="none" stroke="{p["accent"]}" '
            f'stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def word01(p):
    S = 130
    adv = glyph_bounds("ı", F01, S)[4]
    big, w = rich(p, [("r", "main"), ("@mark", adv, lambda p, x, y: check_i(p, x, y, S)),
                      ("ght thing", "main")], F01, S)
    d, ws = text_path("doing the", F01s, 46, 0, 0, tracking=0.02)
    small = place(f'<path d="{d}" fill="{p["sub"]}"/>', w - ws, -0.74 * S - 26)
    return place(big + small, 0, S), round(w), round(1.3 * S)


def icon01(p, x, y, k):
    return g(x, y, k, check_i(p, 18, 96, 128))


logo(1, "01_Doing-the-Right-Thing", "Embedded mark",
     {"main": NAVY, "accent": GREEN, "sub": GREEN_D},
     {"main": WHITE, "accent": GREEN, "sub": GREEN},
     {"primary": word01, "icon": icon_only(icon01)})


# =========================================================== 02 Political Savvy Leader  [combination]
def icon02(p, x, y, k):
    c = p["accent"]
    return g(x, y, k,
             f'<rect x="46.5" y="2" width="7" height="21" rx="2" fill="{p["accent2"]}"/>'
             f'<rect x="40" y="8" width="20" height="7" rx="2" fill="{p["accent2"]}"/>'
             f'<circle cx="50" cy="35" r="10" fill="{c}"/>'
             f'<rect x="31" y="47.5" width="38" height="8" rx="4" fill="{c}"/>'
             f'<path d="M37 59 H63 L69 80 H31 Z" fill="{c}"/>'
             f'<rect x="22" y="84" width="56" height="12" rx="4" fill="{c}"/>')


L02 = [dict(t="THE POLITICAL", f="SoraReg.ttf", s=34, c="sub", tr=0.2),
       dict(t="Savvy Leader", f="Sora.ttf", s=96, c="main", gap=24)]
logo(2, "02_The-Political-Savvy-Leader", "Symbol + text",
     {"main": NAVY, "accent": VIOLET, "accent2": PINK, "sub": "#6A4DF0"},
     {"main": WHITE, "accent": VIOLET, "accent2": PINK, "sub": "#A592FF"},
     {"primary": lambda p: lockup_h(p, icon02, L02, ratio=1.7, space=0.18),
      "stacked": lambda p: lockup_v(p, icon02, L02, isz=200),
      "icon": icon_only(icon02)})


# =========================================================== 03 The Catalyst Within  [wordmark]
def word03(p):
    S, s = 150, 66
    d, w = text_path("catalyst", "Syne.ttf", S, 0, 0)
    d1, w1 = text_path("the", "Syne.ttf", s, 4, -cap_height("Syne.ttf", S) - 30)
    d2, w2 = text_path("within", "Syne.ttf", s, 0, 0)
    d2, _ = text_path("within", "Syne.ttf", s, w - w2, 0.26 * S + 22 + cap_height("Syne.ttf", s))
    body = (f'<path d="{d}" fill="{p["main"]}"/><path d="{d1}" fill="{p["accent"]}"/>'
            f'<path d="{d2}" fill="{p["accent"]}"/>')
    return place(body, 0, 1.3 * S), round(w), round(2 * S)


def icon03(p, x, y, k):
    return g(x, y, k, knockout(circle_d(50, 50, 48), "c", "Syne.ttf", 104, 50, 44, p["accent"]))


logo(3, "03_The-Catalyst-Within", "Wordmark",
     {"main": NAVY, "accent": ORANGE},
     {"main": WHITE, "accent": ORANGE},
     {"primary": word03, "icon": icon_only(icon03)})


# =========================================================== 04 The Visionary Path  [wordmark]
F04, F04s = "MontserratXB.ttf", "Montserrat.ttf"


def word04(p):
    S, s = 130, 40
    ch, chs = cap_height(F04, S), cap_height(F04s, s)
    d, w = text_path("VISIONARY", F04, S, 0, 0)
    d1, _ = text_path("THE", F04s, s, 6, -ch - 26, tracking=0.4)
    yp = 30 + chs
    d2, w2 = text_path("PATH", F04s, s, 6, yp, tracking=0.5)
    ly = yp - chs / 2
    lx0, lx1 = w2 + 34, w - 8
    arrow = (f'<path d="M{lx0:.1f} {ly:.1f} H{lx1:.1f} M{lx1 - 18:.1f} {ly - 15:.1f} L{lx1:.1f} {ly:.1f} '
             f'L{lx1 - 18:.1f} {ly + 15:.1f}" fill="none" stroke="{p["accent"]}" stroke-width="7" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    body = (f'<path d="{d}" fill="{p["main"]}"/><path d="{d1}" fill="{p["accent"]}"/>'
            f'<path d="{d2}" fill="{p["accent"]}"/>{arrow}')
    return place(body, 0, ch + 80), round(w), round(ch + 160)


def icon04(p, x, y, k):
    return g(x, y, k, knockout(rrect(2, 2, 96, 96, 22), "V", F04, 66, 50, 48, p["accent"]))


logo(4, "04_The-Visionary-Path", "Wordmark",
     {"main": NAVY, "accent": BLUE},
     {"main": WHITE, "accent": BLUE},
     {"primary": word04, "icon": icon_only(icon04)})


# =========================================================== 05 Modern Leader Blueprint  [combination]
def icon05(p, x, y, k):
    T, UR, LR, B, LL, UL, C = (50, 6), (88, 28), (88, 72), (50, 94), (12, 72), (12, 28), (50, 50)

    def face(pts, col, s=0.86):
        cx = sum(q[0] for q in pts) / len(pts)
        cy = sum(q[1] for q in pts) / len(pts)
        pp = " ".join(f"{cx + (a - cx) * s:.2f},{cy + (b - cy) * s:.2f}" for a, b in pts)
        return f'<polygon points="{pp}" fill="{col}" stroke="{col}" stroke-width="3" stroke-linejoin="round"/>'
    return g(x, y, k, face([T, UR, C, UL], p["c1"]) + face([UL, C, B, LL], p["c2"]) + face([C, UR, LR, B], p["c3"]))


L05 = [dict(t="THE MODERN LEADER", f="JetBrainsMono.ttf", s=30, c="sub", tr=0.12),
       dict(t="Blueprint", f="SpaceGrotesk.ttf", s=118, c="main", gap=26)]
logo(5, "05_The-Modern-Leader-Blueprint", "Symbol + text",
     {"main": NAVY, "sub": BLUE, "c1": CYAN_D, "c2": BLUE, "c3": NAVY},
     {"main": WHITE, "sub": SKY, "c1": CYAN, "c2": BLUE, "c3": SKY},
     {"primary": lambda p: lockup_h(p, icon05, L05, ratio=1.3, space=0.22),
      "stacked": lambda p: lockup_v(p, icon05, L05, isz=200),
      "icon": icon_only(icon05)})


# =========================================================== 06 The Team Advantage  [wordmark]
def word06(p):
    S, s = 160, 44
    ch = cap_height("Anton.ttf", S)
    d, w = text_path("ADVANTAGE", "Anton.ttf", S, 0, 0, tracking=0.01)
    d1, w1 = text_path("THE TEAM", "OutfitBold.ttf", s, 0, 0, tracking=0.38)
    chs = cap_height("OutfitBold.ttf", s)
    yb = -ch - 26
    d1, _ = text_path("THE TEAM", "OutfitBold.ttf", s, 0, yb, tracking=0.38)
    bar = f'<rect x="{w1 + 26:.1f}" y="{yb - chs / 2 - 4:.1f}" width="{w - w1 - 26:.1f}" height="8" rx="4" fill="{p["accent"]}"/>'
    body = f'<path d="{d}" fill="{p["main"]}"/><path d="{d1}" fill="{p["sub"]}"/>{bar}'
    return place(body, 0, ch + 90), round(w), round(ch + 100)


def icon06(p, x, y, k):
    d, w = text_path("TA", "Anton.ttf", 92, 0, 0)
    ch = cap_height("Anton.ttf", 92)
    d, _ = text_path("TA", "Anton.ttf", 92, 50 - w / 2, 78)
    return g(x, y, k, f'<rect x="{50 - w / 2}" y="{78 - ch - 16}" width="{w}" height="8" rx="4" '
                      f'fill="{p["accent"]}"/><path d="{d}" fill="{p["main"]}"/>')


logo(6, "06_The-Team-Advantage", "Wordmark",
     {"main": NAVY, "accent": GREEN, "sub": GREEN_D},
     {"main": WHITE, "accent": GREEN, "sub": GREEN},
     {"primary": word06, "icon": icon_only(icon06)})


# =========================================================== 07 Leading Beyond Borders  [embedded]
F07, F07s = "Jakarta.ttf", "JakartaMed.ttf"


def globe(p, x, y, S, col):
    x0, y0, x1, y1, adv = glyph_bounds("O", F07, S)
    sw = stem(F07, S, "I")
    cx, cy = x + (x0 + x1) / 2, y - (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 - sw / 2, (y1 - y0) / 2 - sw / 2
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{col}" '
            f'stroke-width="{sw:.1f}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx * 0.42:.1f}" ry="{ry:.1f}" fill="none" stroke="{col}" '
            f'stroke-width="{sw * 0.55:.1f}"/>'
            f'<path d="M{cx - rx:.1f} {cy:.1f} H{cx + rx:.1f}" stroke="{col}" stroke-width="{sw * 0.55:.1f}"/>')


def word07(p):
    S = 112
    adv = glyph_bounds("O", F07, S)[4]
    big, w = rich(p, [("BEY", "main"), ("@mark", adv, lambda p, x, y: globe(p, x, y, S, p["accent"])),
                      ("ND BORDERS", "main")], F07, S)
    d, _ = text_path("LEADING", F07s, 38, 4, -cap_height(F07, S) - 30, tracking=0.5)
    return place(big + f'<path d="{d}" fill="{p["accent"]}"/>', 0, S + 40), round(w), round(S + 60)


def icon07(p, x, y, k):
    return g(x, y, k, globe(p, 2, 94, 120, p["accent"]))


logo(7, "07_Leading-Beyond-Borders", "Embedded mark",
     {"main": NAVY, "accent": BLUE},
     {"main": WHITE, "accent": BLUE},
     {"primary": word07, "icon": icon_only(icon07)})


# =========================================================== 08 Business Case Lab  [combination]
def icon08(p, x, y, k):
    bars = " ".join(rrect(bx, 76 - h, 12, h, 3) for bx, h in [(27, 14), (44, 24), (61, 34)])
    return g(x, y, k,
             f'<path d="M36 30 V20 Q36 12 44 12 H56 Q64 12 64 20 V30" fill="none" stroke="{p["accent"]}" '
             f'stroke-width="7"/>'
             f'<path d="{rrect(8, 28, 84, 60, 12)} {bars}" fill="{p["accent"]}" fill-rule="evenodd"/>')


def lab_pill(p, x, cap_top, cap_h):
    s = cap_h * 0.62 / cap_height("Archivo.ttf", 1)
    tw = text_path("LAB", "Archivo.ttf", s, 0, 0, tracking=0.12)[1]
    ph = cap_h * 1.05
    pw = tw + ph * 0.9
    py = cap_top + (cap_h - ph) / 2
    return knockout(rrect(x, py, pw, ph, ph * 0.28), "LAB", "Archivo.ttf", s, x + pw / 2 + s * 0.06,
                    py + ph / 2, p["accent2"], tracking=0.12), pw


def lockup08(p, vertical=False):
    S = 100
    ch = cap_height("Archivo.ttf", S)
    d, w = text_path("Business Case", "Archivo.ttf", S, 0, ch)
    word = f'<path d="{d}" fill="{p["main"]}"/>'
    if vertical:
        pill, pw = lab_pill(p, 0, 0, ch)
        isz = 200
        W = max(w, isz)
        body = (icon08(p, (W - isz) / 2, 0, isz / 100) + place(word, (W - w) / 2, isz + 50)
                + place(pill, (W - pw) / 2, isz + 50 + ch + 34))
        return body, round(W), round(isz + 50 + 2 * ch + 40)
    pill, pw = lab_pill(p, w + 26, 0, ch)
    isz = ch * 2.5
    tx = isz * 1.2
    return icon08(p, 0, 0, isz / 100) + place(word + pill, tx, (isz - ch) / 2 + isz * 0.08), \
        round(tx + w + 26 + pw), round(isz)


logo(8, "08_The-Business-Case-Lab", "Symbol + text",
     {"main": NAVY, "accent": INDIGO, "accent2": CYAN_D},
     {"main": WHITE, "accent": VIOLET, "accent2": CYAN},
     {"primary": lockup08, "stacked": lambda p: lockup08(p, True), "icon": icon_only(icon08)})


# =========================================================== 09 Driving High Performance  [wordmark]
def word09(p):
    s1, s2 = 64, 140
    tb = text_block(p, [dict(t="DRIVING HIGH", f="BarlowCondItMed.ttf", s=s1, c="sub", tr=0.06, dx=24),
                        dict(t="PERFORMANCE", f="BarlowCondIt.ttf", s=s2, c="main", gap=16)])
    c1 = cap_height("BarlowCondItMed.ttf", s1)
    sx, ex = tb["rows"][0]["w"] + 50, tb["w"]
    lines = "".join(
        f'<path d="M{sx + i * 30:.1f} {c1 * f:.1f} H{ex:.1f}" stroke="{p["accent"]}" '
        f'stroke-width="{c1 * 0.17:.1f}" stroke-linecap="round"/>'
        for i, f in enumerate([0.18, 0.5, 0.82]))
    return tb["body"] + lines, round(tb["w"]), round(tb["h"])


def icon09(p, x, y, k):
    def chev(ox, col):
        return (f'<path d="M{ox} 18 L{ox + 30} 50 L{ox} 82" fill="none" stroke="{col}" stroke-width="15" '
                f'stroke-linecap="round" stroke-linejoin="round" transform="skewX(-10)"/>')
    return g(x, y, k, f'<g transform="translate(14 0)">{chev(14, p["main"])}{chev(46, p["accent"])}</g>')


logo(9, "09_Driving-High-Performance", "Wordmark",
     {"main": NAVY, "accent": ORANGE, "sub": ORANGE},
     {"main": WHITE, "accent": ORANGE, "sub": ORANGE},
     {"primary": word09, "icon": icon_only(icon09)})


# =========================================================== 10 Strategy That Delivers  [combination]
def icon10(p, x, y, k):
    return g(x, y, k,
             f'<polygon points="6,48 94,10 46,60" fill="{p["accent"]}" stroke="{p["accent"]}" stroke-width="4" '
             f'stroke-linejoin="round"/>'
             f'<polygon points="52,64 96,16 70,90" fill="{p["accent2"]}" stroke="{p["accent2"]}" stroke-width="4" '
             f'stroke-linejoin="round"/>'
             f'<polygon points="40,66 48,70 42,90" fill="{p["accent2"]}" stroke="{p["accent2"]}" stroke-width="4" '
             f'stroke-linejoin="round"/>')


L10 = [dict(t="Strategy", f="Urbanist.ttf", s=124, c="main"),
       dict(t="THAT DELIVERS", f="UrbanistSemi.ttf", s=40, c="sub", tr=0.36, gap=58)]
logo(10, "10_Strategy-That-Delivers", "Symbol + text",
     {"main": NAVY, "accent": YELLOW, "accent2": ORANGE, "sub": NAVY},
     {"main": WHITE, "accent": YELLOW, "accent2": ORANGE, "sub": YELLOW},
     {"primary": lambda p: lockup_h(p, icon10, L10, ratio=1.3, space=0.22),
      "stacked": lambda p: lockup_v(p, icon10, L10, isz=190),
      "icon": icon_only(icon10)})


# =========================================================== 11 Beyond the Deal  [wordmark]
def word11(p):
    big, sm = 160, 34
    tb = text_block(p, [dict(t="Beyond", f="CormorantIt.ttf", s=big, c="main"),
                        dict(t="THE DEAL", f="Montserrat.ttf", s=sm, c="sub", tr=0.6, gap=54)],
                    align="center")
    r = tb["rows"][1]
    cy = r["y"] - cap_height("Montserrat.ttf", sm) / 2
    L = 90
    lines = (f'<path d="M{r["x"] - 30 - L} {cy} H{r["x"] - 30} M{r["x"] + r["w"] + 30} {cy} '
             f'H{r["x"] + r["w"] + 30 + L}" stroke="{p["accent"]}" stroke-width="3"/>')
    return tb["body"] + lines, round(tb["w"]), round(tb["h"])


def icon11(p, x, y, k):
    d, w = text_path("B", "CormorantIt.ttf", 92, 0, 0)
    ch = cap_height("CormorantIt.ttf", 92)
    return g(x, y, k,
             f'<circle cx="50" cy="50" r="45" fill="none" stroke="{p["accent"]}" stroke-width="3.5"/>'
             f'<path d="{d}" fill="{p["main"]}" transform="translate({(100 - w) / 2 + 2} {50 + ch / 2})"/>')


logo(11, "11_Beyond-the-Deal", "Wordmark",
     {"main": PURPLE, "accent": PINK, "sub": PURPLE},
     {"main": WHITE, "accent": PINK, "sub": "#F7B8D0"},
     {"primary": word11, "icon": icon_only(icon11)})


# =========================================================== 12 Wealth Advisory Mastery  [combination]
def icon12(p, x, y, k):
    return g(x, y, k,
             f'<circle cx="50" cy="50" r="46" fill="none" stroke="{p["accent"]}" stroke-width="3"/>'
             f'<path d="M22 34 L35 70 L50 42 L64 70" fill="none" stroke="{p["main"]}" stroke-width="8" '
             f'stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="M64 70 L80 26 M70 30 L80 24 L84 36" fill="none" stroke="{p["accent"]}" stroke-width="8" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')


L12 = [dict(t="Wealth Advisory", f="Playfair.ttf", s=100, c="main"),
       dict(t="MASTERY", f="Jost.ttf", s=36, c="sub", tr=0.75, gap=30)]
logo(12, "12_Wealth-Advisory-Mastery", "Symbol + text",
     {"main": NAVY, "accent": YELLOW_D, "sub": YELLOW_D},
     {"main": WHITE, "accent": YELLOW, "sub": YELLOW},
     {"primary": lambda p: lockup_h(p, icon12, L12, ratio=1.75, space=0.2),
      "stacked": lambda p: lockup_v(p, icon12, L12, isz=200, space=50),
      "icon": icon_only(icon12)})


# =========================================================== 13 Seal the Deal  [embedded]
F13 = "Bricolage.ttf"


def seal_d(cx, cy, R, bumps=14):
    pts = []
    for i in range(0, 361, 2):
        t = math.radians(i)
        r = R * (1 + 0.075 * math.cos(bumps * t))
        pts.append(f"{cx + r * math.cos(t):.2f} {cy + r * math.sin(t):.2f}")
    return "M" + " L".join(pts) + "Z"


def word13(p):
    S = 140
    xh = x_height(F13, S)
    R = xh * 0.56
    gap = 0.07 * S

    def dot(p, x, y):
        cx, cy = x + gap + R * 1.08, y - R * 1.08
        return (f'<path d="{seal_d(cx, cy, R)} {circle_d(cx, cy, R * 0.66)} {circle_d(cx, cy, R * 0.5)}" '
                f'fill="{p["accent"]}" fill-rule="evenodd"/>')
    body, w = rich(p, [("seal the deal", "main"), ("@mark", gap + 2.2 * R, dot)], F13, S)
    return place(body, 0, S), round(w), round(1.3 * S)


def icon13(p, x, y, k):
    return g(x, y, k, knockout(f"{seal_d(50, 50, 44)} {circle_d(50, 50, 33)} {circle_d(50, 50, 30)}",
                               "s", F13, 70, 50, 42, p["accent"]))


logo(13, "13_Seal-the-Deal", "Embedded mark",
     {"main": NAVY, "accent": PINK},
     {"main": WHITE, "accent": PINK},
     {"primary": word13, "icon": icon_only(icon13)})


# =========================================================== 14 Build the Bond  [combination]
def ring_arc(cx, cy, r, a0, a1):
    t0, t1 = math.radians(a0), math.radians(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f"M{cx + r * math.cos(t0):.2f} {cy + r * math.sin(t0):.2f} "
            f"A{r} {r} 0 {large} 1 {cx + r * math.cos(t1):.2f} {cy + r * math.sin(t1):.2f}")


def icon14(p, x, y, k):
    a = ring_arc(37, 50, 25, 60 + 17, 60 - 17 + 360)
    b = ring_arc(63, 50, 25, -120 + 17, -120 - 17 + 360)
    return g(x, y, k, f'<path d="{a}" fill="none" stroke="{p["accent"]}" stroke-width="10"/>'
                      f'<path d="{b}" fill="none" stroke="{p["accent2"]}" stroke-width="10"/>')


L14 = [dict(t="Build the Bond", f="Nunito.ttf", s=108, c="main")]
logo(14, "14_Build-the-Bond", "Symbol + text",
     {"main": NAVY, "accent": GREEN, "accent2": BLUE},
     {"main": WHITE, "accent": GREEN, "accent2": SKY},
     {"primary": lambda p: lockup_v(p, icon14, L14, isz=230, space=36),
      "horizontal": lambda p: lockup_h(p, icon14, L14, ratio=1.9, space=0.16),
      "icon": icon_only(icon14)})


# =========================================================== 15 Contact to Contract  [embedded]
# the "o" goes from an open ring (contact) to a solid dot (contract)
F15 = "Lexend.ttf"


def o_mark(S, filled):
    x0, y0, x1, y1, adv = glyph_bounds("o", F15, S)
    sw = stem(F15, S, "l")

    def fn(p, x, y):
        cx, cy, r = x + (x0 + x1) / 2, y - (y0 + y1) / 2, (x1 - x0) / 2
        if filled:
            return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{p["accent"]}"/>'
        return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r - sw / 2:.1f}" fill="none" stroke="{p["accent"]}" '
                f'stroke-width="{sw:.1f}"/>')
    return ("@mark", adv, fn)


def word15(p):
    S = 112
    xh = x_height(F15, S)
    aw = 0.95 * S

    def arrow(p, x, y):
        x0, x1, cy = x + 0.22 * S, x + aw - 0.22 * S, y - xh / 2
        return (f'<path d="M{x0:.1f} {cy:.1f} H{x1:.1f} M{x1 - 20:.1f} {cy - 18:.1f} L{x1:.1f} {cy:.1f} '
                f'L{x1 - 20:.1f} {cy + 18:.1f}" fill="none" stroke="{p["sub"]}" stroke-width="{stem(F15, S) * 0.7:.1f}" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    body, w = rich(p, [("c", "main"), o_mark(S, False), ("ntact", "main"), ("@mark", aw, arrow),
                       ("c", "main"), o_mark(S, True), ("ntract", "main")], F15, S)
    return place(body, 0, S), round(w), round(1.3 * S)


def icon15(p, x, y, k):
    return g(x, y, k,
             f'<circle cx="24" cy="50" r="17" fill="none" stroke="{p["accent"]}" stroke-width="9"/>'
             f'<path d="M48 50 H56" stroke="{p["sub"]}" stroke-width="7" stroke-linecap="round"/>'
             f'<circle cx="78" cy="50" r="21" fill="{p["accent"]}"/>')


logo(15, "15_Contact-to-Contract", "Embedded mark",
     {"main": NAVY, "accent": BLUE, "sub": CYAN_D},
     {"main": WHITE, "accent": BLUE, "sub": CYAN},
     {"primary": word15, "icon": icon_only(icon15)})


# =========================================================== 16 The Learning Architect  [embedded]
# the first "A" of ARCHITECT is a drafting compass
F16 = "Josefin.ttf"


def compass(p, x, y, S):
    x0, _, x1, y1, adv = glyph_bounds("A", F16, S)
    sw = stem(F16, S, "I")
    ax, top = x + (x0 + x1) / 2, y - y1 + sw * 0.6
    lx, rx = x + x0 + sw * 0.5, x + x1 - sw * 0.5
    ty = y - 0.36 * y1

    def on_leg(xx, t):
        return xx + (ax - xx) * t
    t = 0.36
    return (f'<path d="M{ax:.1f} {top:.1f} L{lx:.1f} {y:.1f} M{ax:.1f} {top:.1f} L{rx:.1f} {y:.1f}" fill="none" '
            f'stroke="{p["main"]}" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
            f'<path d="M{on_leg(lx, t):.1f} {ty:.1f} Q{ax:.1f} {ty + 0.2 * y1:.1f} {on_leg(rx, t):.1f} {ty:.1f}" '
            f'fill="none" stroke="{p["accent"]}" stroke-width="{sw * 0.8:.1f}" stroke-linecap="round"/>'
            f'<circle cx="{ax:.1f}" cy="{top - sw * 0.2:.1f}" r="{sw * 1.05:.1f}" fill="{p["accent"]}"/>')


def word16(p):
    S, tr = 124, 0.08
    adv = glyph_bounds("A", F16, S)[4]
    big, w = rich(p, [("@mark", adv, lambda p, x, y: compass(p, x, y, S)), ("RCHITECT", "main")], F16, S,
                  tracking=tr)
    d, _ = text_path("THE LEARNING", F16, 42, 4, -cap_height(F16, S) - 40, tracking=0.36)
    return place(big + f'<path d="{d}" fill="{p["accent"]}"/>', 0, S + 40), round(w), round(S + 60)


def icon16(p, x, y, k):
    return g(x, y, k, compass(p, 12, 94, 120))


logo(16, "16_The-Learning-Architect", "Embedded mark",
     {"main": NAVY, "accent": ORANGE},
     {"main": WHITE, "accent": ORANGE},
     {"primary": word16, "icon": icon_only(icon16)})


# =========================================================== 17 The Leader DNA  [combination]
def icon17(p, x, y, k):
    def strand(phase):
        pts = [(50 + 28 * math.sin(t / 80 * 3 * math.pi + phase), 10 + t) for t in range(0, 81)]
        return "M" + " L".join(f"{a:.2f} {b:.2f}" for a, b in pts)
    rungs = ""
    for t in [8, 21, 34, 46, 59, 72]:
        s = math.sin(t / 80 * 3 * math.pi)
        if abs(s) > 0.35:
            rungs += f"M{50 - 28 * s:.2f} {10 + t} H{50 + 28 * s:.2f} "
    return g(x, y, k,
             f'<path d="{rungs}" stroke="{p["rung"]}" stroke-width="4" stroke-linecap="round"/>'
             f'<path d="{strand(0)}" fill="none" stroke="{p["accent2"]}" stroke-width="8" stroke-linecap="round"/>'
             f'<path d="{strand(math.pi)}" fill="none" stroke="{p["accent"]}" stroke-width="8" stroke-linecap="round"/>')


L17 = [dict(t="THE LEADER", f="RedHatBold.ttf", s=40, c="main", tr=0.26),
       dict(t="DNA", f="RedHat.ttf", s=150, c="accent", gap=22, dx=-6)]
logo(17, "17_The-Leader-DNA", "Symbol + text",
     {"main": NAVY, "accent": PINK, "accent2": VIOLET, "rung": NAVY},
     {"main": WHITE, "accent": PINK, "accent2": VIOLET, "rung": WHITE},
     {"primary": lambda p: lockup_h(p, icon17, L17, ratio=1.05, space=0.22),
      "stacked": lambda p: lockup_v(p, icon17, L17, isz=180),
      "icon": icon_only(icon17)})


if __name__ == "__main__":
    for num, slug, kind, light, dark, builders in LOGOS:
        if ONLY and int(ONLY) != num:
            continue
        blk, wht = mono(light)
        wht["bg"] = DARK_BG
        variants = {"color-light": light, "color-dark": dark, "black": blk, "white": wht}
        zpath, prev = export(slug, slug, builders, variants, OUT)
        preview_sheet(slug, prev, f"{OUT}/{num:02d}_preview.png")
        print(num, kind)
