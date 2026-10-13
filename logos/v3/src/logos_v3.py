"""Logo set v3 — new concepts and styles, brand palette with gradients.
Run: python3 logos_v3.py <kit_dir> <out_dir> [only_number]"""
import math
import sys

sys.path.insert(0, sys.argv[1])
from logokit import (  # noqa: E402
    cap_height, circle_d, export, g, glyph_bounds, knockout, lockup_h, lockup_v, mono,
    preview_sheet, rich, rrect, stem, text_block, text_path, x_height,
)

OUT = sys.argv[2]
ONLY = sys.argv[3] if len(sys.argv) > 3 else None

NAVY = "#2A3649"
CYAN, CYAN_D = "#20E0E0", "#12BFC4"
BLUE = "#00A2EA"
ORANGE = "#F85E35"
YELLOW = "#FBB414"
GREEN, GREEN_D = "#00CC99", "#00A882"
SKY = "#80DBFF"
INDIGO = "#3F37C9"
VIOLET = "#8164FF"
PURPLE = "#672496"
PINK = "#ED1E6C"
WHITE = "#FFFFFF"
DARK_BG = NAVY


def G(*colors, angle=0):
    """Linear gradient spec; angle 0 = left→right, 90 = top→bottom."""
    return ("grad", colors, angle)


def resolve(p):
    """Turn gradient specs into <defs> + url() references."""
    defs, out = [], {}
    for k, v in p.items():
        if isinstance(v, tuple) and v[0] == "grad":
            _, cols, ang = v
            a = math.radians(ang)
            x1, y1 = 0.5 - 0.5 * math.cos(a), 0.5 - 0.5 * math.sin(a)
            x2, y2 = 0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)
            stops = "".join(f'<stop offset="{i / (len(cols) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(cols))
            defs.append(f'<linearGradient id="{k}" x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}">'
                        f'{stops}</linearGradient>')
            out[k] = f"url(#{k})"
        else:
            out[k] = v
    return out, (f"<defs>{''.join(defs)}</defs>" if defs else "")


LOGOS = []


def logo(num, slug, kind, light, dark, builders):
    light = {"bg": WHITE, **light}
    dark = {"bg": DARK_BG, **dark}

    def wrap(fn):
        def run(p):
            rp, defs = resolve(p)
            body, w, h = fn(rp)
            return defs + body, w, h
        return run
    LOGOS.append((num, slug, kind, light, dark, {k: wrap(f) for k, f in builders.items()}))


def icon_only(fn):
    return lambda p: (fn(p, 0, 0, 1), 100, 100)


def place(body, dx, dy):
    return f'<g transform="translate({dx:.2f} {dy:.2f})">{body}</g>'


def poly(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def arc_pts(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def ribbon(center, widths):
    """Filled outline of a variable-width centre line (for knock-outs)."""
    L, R = [], []
    for i, (x, y) in enumerate(center):
        a = center[max(i - 1, 0)]
        b = center[min(i + 1, len(center) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        w = widths[i] / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return poly(L + R[::-1])


def fill(d, col, evenodd=False):
    rule = ' fill-rule="evenodd"' if evenodd else ""
    return f'<path d="{d}" fill="{col}"{rule}/>'


# =========================================================== Doing the Right Thing — app-icon mark + text
def icon01(p, x, y, k):
    arrow = ([(30, 84), (30, 46)] + arc_pts(58, 46, 28, 180, 270) +
             [(64, 18), (64, 6), (88, 25), (64, 44), (64, 32)] + arc_pts(58, 46, 14, 270, 180) + [(44, 84)])
    return g(x, y, k, fill(f"{rrect(0, 0, 100, 100, 26)} {poly(arrow)}", p["accent"], True))


L01 = [dict(t="DOING THE", f="FigtreeMed.ttf", s=36, c="sub", tr=0.3),
       dict(t="Right Thing", f="Figtree.ttf", s=104, c="text", gap=22)]
logo(1, "Doing-the-Right-Thing", "Symbol + text (app icon)",
     {"accent": G(GREEN, CYAN_D, angle=45), "text": G(GREEN_D, BLUE), "sub": NAVY},
     {"accent": G(GREEN, CYAN, angle=45), "text": G(GREEN, CYAN), "sub": WHITE},
     {"primary": lambda p: lockup_h(p, icon01, L01, ratio=1.25, space=0.22),
      "stacked": lambda p: lockup_v(p, icon01, L01, isz=190),
      "icon": icon_only(icon01)})


# =========================================================== Political Savvy Leader — justified type block
def word02(p, W=720):
    F = "Unbounded.ttf"
    out, y = [], 0
    for i, (t, ck) in enumerate([("THE POLITICAL", "main"), ("SAVVY", "accent"), ("LEADER", "main")]):
        w1 = text_path(t, F, 100, 0, 0, tracking=0.02)[1]
        s = 100 * W / w1
        y += cap_height(F, s) + (0 if i == 0 else W * 0.035)
        d, _ = text_path(t, F, s, 0, y, tracking=0.02)
        out.append(fill(d, p[ck]))
    return "".join(out), W, round(y)


def icon02(p, x, y, k):
    return g(x, y, k, knockout(circle_d(50, 50, 48), "S", "Unbounded.ttf", 62, 51, 50, p["accent"]))


logo(2, "The-Political-Savvy-Leader", "Wordmark (type block)",
     {"main": NAVY, "accent": G(VIOLET, PINK)},
     {"main": WHITE, "accent": G(VIOLET, PINK)},
     {"primary": word02, "icon": icon_only(icon02)})


# =========================================================== The Catalyst Within — gradient orb with spark
def icon03(p, x, y, k):
    cx, cy, r = 50, 50, 15
    spark = (f"M{cx} {cy - 2.3 * r} C{cx + .25 * r} {cy - .5 * r} {cx + .5 * r} {cy - .25 * r} {cx + 2.3 * r} {cy} "
             f"C{cx + .5 * r} {cy + .25 * r} {cx + .25 * r} {cy + .5 * r} {cx} {cy + 2.3 * r} "
             f"C{cx - .25 * r} {cy + .5 * r} {cx - .5 * r} {cy + .25 * r} {cx - 2.3 * r} {cy} "
             f"C{cx - .5 * r} {cy - .25 * r} {cx - .25 * r} {cy - .5 * r} {cx} {cy - 2.3 * r}Z")
    return g(x, y, k, fill(f"{circle_d(50, 50, 48)} {spark}", p["accent"], True))


L03 = [dict(t="The Catalyst", f="DMSerif.ttf", s=110, c="main"),
       dict(t="WITHIN", f="DMSans.ttf", s=36, c="sub", tr=0.7, gap=30)]
logo(3, "The-Catalyst-Within", "Symbol + text (gradient orb)",
     {"main": NAVY, "accent": G(YELLOW, ORANGE, PINK, angle=60), "sub": ORANGE},
     {"main": WHITE, "accent": G(YELLOW, ORANGE, PINK, angle=60), "sub": YELLOW},
     {"primary": lambda p: lockup_h(p, icon03, L03, ratio=1.35, space=0.2),
      "stacked": lambda p: lockup_v(p, icon03, L03, isz=200),
      "icon": icon_only(icon03)})


# =========================================================== The Visionary Path — mountain with a road
def icon04(p, x, y, k):
    mountain = "M6 92 L44 22 Q50 12 56 22 L94 92 Z"
    n = 40
    centre = [(50 + 9 * math.sin(t / n * 2 * math.pi) * (1 - t / n * 0.5), 85 - 44 * t / n) for t in range(n + 1)]
    widths = [14 * (1 - t / n) ** 1.2 + 3 for t in range(n + 1)]
    return g(x, y, k, fill(f"{mountain} {ribbon(centre, widths)}", p["accent"], True)
             + f'<circle cx="80" cy="20" r="10" fill="{p["sun"]}"/>')


L04 = [dict(t="THE", f="RalewayMed.ttf", s=36, c="sub", tr=0.6),
       dict(t="VISIONARY PATH", f="Raleway.ttf", s=96, c="main", gap=24)]
logo(4, "The-Visionary-Path", "Symbol + text (landscape)",
     {"main": NAVY, "accent": G(BLUE, INDIGO, angle=90), "sun": G(YELLOW, ORANGE, angle=90), "sub": BLUE},
     {"main": WHITE, "accent": G(SKY, BLUE, angle=90), "sun": G(YELLOW, ORANGE, angle=90), "sub": SKY},
     {"primary": lambda p: lockup_h(p, icon04, L04, ratio=1.8, space=0.16),
      "stacked": lambda p: lockup_v(p, icon04, L04, isz=200),
      "icon": icon_only(icon04)})


# =========================================================== Modern Leader Blueprint — terminal wordmark
F05 = "JetBrainsMono.ttf"


def word05(p):
    S, s = 130, 38
    ch = cap_height(F05, S)
    d, w = text_path("blueprint", F05, S, 0, 0)
    cw = glyph_bounds("n", F05, S)[4]
    cur = f'<rect x="{w + cw * 0.18:.1f}" y="{-ch:.1f}" width="{cw * 0.62:.1f}" height="{ch:.1f}" rx="4" fill="{p["accent"]}"/>'
    d1, _ = text_path("// the modern leader", F05, s, 4, -ch - 0.42 * S, tracking=0.02)
    return place(fill(d, p["main"]) + cur + fill(d1, p["sub"]), 0, ch + 0.8 * S), round(w + cw), round(ch + S)


def icon05(p, x, y, k):
    d, w = text_path("b", F05, 70, 0, 0)
    ch = cap_height(F05, 70)
    d, _ = text_path("b", F05, 70, 22, 50 + ch / 2)
    cur = rrect(64, 50 + ch / 2 - 10, 16, 10, 2)
    return g(x, y, k, fill(f"{rrect(0, 0, 100, 100, 22)} {d} {cur}", p["accent"], True))


logo(5, "The-Modern-Leader-Blueprint", "Wordmark (monospace)",
     {"main": NAVY, "accent": G(CYAN_D, BLUE, angle=90), "sub": BLUE},
     {"main": WHITE, "accent": G(CYAN, BLUE, angle=90), "sub": SKY},
     {"primary": word05, "icon": icon_only(icon05)})


# =========================================================== The Team Advantage — rising chevrons
def icon06(p, x, y, k):
    def chev(Y):
        return poly([(18, Y + 30), (50, Y), (82, Y + 30), (82, Y + 46), (50, Y + 16), (18, Y + 46)])
    return g(x, y, k, fill(chev(4), p["accent"]) + fill(chev(30), p["mid"]) + fill(chev(56), p["low"]))


L06 = [dict(t="THE TEAM", f="Rubik.ttf", s=34, c="sub", tr=0.4),
       dict(t="Advantage", f="Rubik.ttf", s=108, c="main", gap=22)]
logo(6, "The-Team-Advantage", "Symbol + text (chevrons)",
     {"main": NAVY, "accent": G(GREEN, CYAN_D), "mid": G(BLUE, CYAN_D), "low": NAVY, "sub": GREEN_D},
     {"main": WHITE, "accent": G(GREEN, CYAN), "mid": G(BLUE, CYAN), "low": WHITE, "sub": GREEN},
     {"primary": lambda p: lockup_h(p, icon06, L06, ratio=1.4, space=0.2),
      "stacked": lambda p: lockup_v(p, icon06, L06, isz=190),
      "icon": icon_only(icon06)})


# =========================================================== Leading Beyond Borders — breaking the frame
def icon07(p, x, y, k):
    return g(x, y, k,
             f'<rect x="6" y="24" width="70" height="70" rx="8" fill="none" stroke="{p["main"]}" stroke-width="6" '
             f'stroke-dasharray="11 8"/>'
             f'<circle cx="70" cy="30" r="24" fill="{p["accent"]}"/>')


L07 = [dict(t="LEADING", f="ManropeXB.ttf", s=32, c="sub", tr=0.55),
       dict(t="Beyond Borders", f="ManropeXB.ttf", s=100, c="main", gap=22)]
logo(7, "Leading-Beyond-Borders", "Symbol + text (geometric)",
     {"main": NAVY, "accent": G(CYAN_D, BLUE, INDIGO, angle=45), "sub": BLUE},
     {"main": WHITE, "accent": G(CYAN, BLUE, VIOLET, angle=45), "sub": CYAN},
     {"primary": lambda p: lockup_h(p, icon07, L07, ratio=1.7, space=0.18),
      "stacked": lambda p: lockup_v(p, icon07, L07, isz=190),
      "icon": icon_only(icon07)})


# =========================================================== Business Case Lab — the "A" of LAB is a flask
F08 = "OutfitBold.ttf"


def flask(p, x, y, S):
    x0, _, x1, y1, adv = glyph_bounds("A", F08, S)
    cx, nw = x + (x0 + x1) / 2, S * 0.075
    top, shoulder = y - y1, y - y1 * 0.6
    body = poly([(cx - nw, top), (cx + nw, top), (cx + nw, shoulder), (x + x1, y - S * 0.05), (x + x1 - S * 0.04, y),
                 (x + x0 + S * 0.04, y), (x + x0, y - S * 0.05), (cx - nw, shoulder)])
    lip = rrect(cx - nw * 1.9, top - S * 0.02, nw * 3.8, S * 0.06, S * 0.02)
    bubbles = f"{circle_d(cx - S * 0.06, y - S * 0.17, S * 0.045)} {circle_d(cx + S * 0.08, y - S * 0.27, S * 0.03)}"
    return fill(f"{body} {bubbles}", p["accent"], True) + fill(lip, p["accent"])


def word08(p):
    S = 190
    adv = glyph_bounds("A", F08, S)[4]
    big, w = rich(p, [("L", "main"), ("@mark", adv, lambda p, x, y: flask(p, x, y, S)), ("B", "main")], F08, S,
                  tracking=0.04)
    d, ws = text_path("THE BUSINESS CASE", F08, 30, 0, 0, tracking=0.3)
    d, _ = text_path("THE BUSINESS CASE", F08, 30, (w - ws) / 2, -cap_height(F08, S) - 34, tracking=0.3)
    return place(big + fill(d, p["sub"]), 0, S + 40), round(w), round(S + 60)


def icon08(p, x, y, k):
    return g(x, y, k, flask(p, 6, 96, 140))


logo(8, "The-Business-Case-Lab", "Embedded mark",
     {"main": NAVY, "accent": G(INDIGO, VIOLET, angle=90), "sub": INDIGO},
     {"main": WHITE, "accent": G(VIOLET, SKY, angle=90), "sub": SKY},
     {"primary": word08, "icon": icon_only(icon08)})


# =========================================================== Driving High Performance — gauge emblem
def icon09(p, x, y, k):
    cx, cy = 50, 58
    band = poly(arc_pts(cx, cy, 44, 150, 390) + arc_pts(cx, cy, 31, 390, 150))
    a = math.radians(-40)
    tip = (cx + 36 * math.cos(a), cy + 36 * math.sin(a))
    nx, ny = -math.sin(a) * 6, math.cos(a) * 6
    needle = poly([tip, (cx + nx, cy + ny), (cx - nx, cy - ny)])
    return g(x, y, k, fill(band, p["accent"]) + fill(needle, p["main"]) + f'<circle cx="{cx}" cy="{cy}" r="9" '
             f'fill="{p["main"]}"/>')


L09 = [dict(t="DRIVING", f="BebasNeue.ttf", s=46, c="sub", tr=0.5),
       dict(t="HIGH PERFORMANCE", f="BebasNeue.ttf", s=120, c="main", gap=16)]
logo(9, "Driving-High-Performance", "Emblem (stacked)",
     {"main": NAVY, "accent": G(YELLOW, ORANGE, PINK), "sub": ORANGE},
     {"main": WHITE, "accent": G(YELLOW, ORANGE, PINK), "sub": YELLOW},
     {"primary": lambda p: lockup_v(p, icon09, L09, isz=270, space=30),
      "horizontal": lambda p: lockup_h(p, icon09, L09, ratio=1.25, space=0.15),
      "icon": icon_only(icon09)})


# =========================================================== Strategy That Delivers — "A" becomes a delta
F10 = "ArchivoBlack.ttf"


def delta(p, x, y, S):
    x0, _, x1, y1, _ = glyph_bounds("A", F10, S)
    r = S * 0.03
    tri = poly([(x + x0 + r, y), (x + (x0 + x1) / 2, y - y1), (x + x1 - r, y)])
    return (f'<path d="{tri}" fill="{p["accent"]}" stroke="{p["accent"]}" stroke-width="{2 * r:.1f}" '
            f'stroke-linejoin="round"/>')


def word10(p):
    S = 130
    adv = glyph_bounds("A", F10, S)[4]
    big, w = rich(p, [("STR", "main"), ("@mark", adv, lambda p, x, y: delta(p, x, y, S)), ("TEGY", "main")], F10, S,
                  tracking=0.02)
    d, ws = text_path("THAT DELIVERS", "Montserrat.ttf", 40, 0, 0, tracking=0.62)
    d, _ = text_path("THAT DELIVERS", "Montserrat.ttf", 40, (w - ws) / 2, 0.24 * S + 30 + 28, tracking=0.62)
    return place(big + fill(d, p["sub"]), 0, S), round(w), round(1.6 * S)


def icon10(p, x, y, k):
    return g(x, y, k, delta(p, 4, 92, 125))


logo(10, "Strategy-That-Delivers", "Embedded mark",
     {"main": NAVY, "accent": G(YELLOW, ORANGE, PINK, angle=90), "sub": ORANGE},
     {"main": WHITE, "accent": G(YELLOW, ORANGE, PINK, angle=90), "sub": YELLOW},
     {"primary": word10, "icon": icon_only(icon10)})


# =========================================================== Beyond the Deal — infinity loop
def icon11(p, x, y, k):
    pts = []
    for i in range(0, 361, 4):
        t = math.radians(i)
        s = 1 + math.sin(t) ** 2
        pts.append((50 + 44 * math.cos(t) / s, 50 + 44 * math.sin(t) * math.cos(t) / s))
    d = "M" + " L".join(f"{a:.2f} {b:.2f}" for a, b in pts) + "Z"
    return g(x, y, k, f'<path d="{d}" fill="none" stroke="{p["accent"]}" stroke-width="10" stroke-linejoin="round"/>')


def lock11(p, vertical=False):
    S = 120
    F, Fi = "InstrumentSerif.ttf", "InstrumentSerifIt.ttf"
    d1, w1 = text_path("Beyond ", F, S, 0, 0)
    d2, w2 = text_path("the", Fi, S, w1, 0)
    d3, w3 = text_path(" Deal", F, S, w1 + w2, 0)
    word = fill(d1, p["main"]) + fill(d2, p["sub"]) + fill(d3, p["main"])
    W = w1 + w2 + w3
    ch = cap_height(F, S)
    if vertical:
        isz = 220
        return place(icon11(p, (W - isz) / 2, -isz * 0.25, isz / 100), 0, 0) + place(word, 0, isz * 0.75 + 40 + ch), \
            round(W), round(isz + ch + 40)
    isz = ch * 2.0
    return icon11(p, 0, 0, isz / 100) + place(word, isz * 1.12, isz / 2 + ch / 2), round(isz * 1.12 + W), round(isz)


logo(11, "Beyond-the-Deal", "Symbol + text (elegant serif)",
     {"main": NAVY, "accent": G(PURPLE, PINK), "sub": PINK},
     {"main": WHITE, "accent": G(VIOLET, PINK), "sub": PINK},
     {"primary": lock11, "stacked": lambda p: lock11(p, True), "icon": icon_only(icon11)})


# =========================================================== Wealth Advisory Mastery — arch crest
def icon12(p, x, y, k):
    arch = "M12 98 V46 A38 38 0 0 1 88 46 V98 Z"
    return g(x, y, k, knockout(arch, "W", "CormorantSemi.ttf", 64, 50, 64, p["accent"])
             + f'<rect x="12" y="104" width="76" height="3" fill="{p["line"]}"/>')


L12 = [dict(t="WEALTH ADVISORY", f="CormorantSemi.ttf", s=76, c="main", tr=0.08),
       dict(t="MASTERY", f="JostSemi.ttf", s=30, c="sub", tr=0.9, gap=28)]
logo(12, "Wealth-Advisory-Mastery", "Crest (stacked)",
     {"main": NAVY, "accent": G(INDIGO, NAVY, angle=90), "line": G(YELLOW, ORANGE), "sub": "#D98E00"},
     {"main": WHITE, "accent": G(VIOLET, INDIGO, angle=90), "line": G(YELLOW, ORANGE), "sub": YELLOW},
     {"primary": lambda p: lockup_v(p, icon12, L12, isz=200, space=60),
      "horizontal": lambda p: lockup_h(p, icon12, L12, ratio=1.6, space=0.18),
      "icon": icon_only(icon12)})


# =========================================================== Seal the Deal — rubber stamp
F13 = "PoppinsBold.ttf"


def word13(p):
    S = 96
    ch = cap_height(F13, S)
    d, w = text_path("SEAL THE DEAL", F13, S, 0, 0, tracking=0.06)
    px, py = 0.42 * S, 0.42 * S
    W, H = w + 2 * px, ch + 2 * py
    inner = f'<rect x="{-px + 12}" y="{-ch - py + 12}" width="{W - 24}" height="{H - 24}" rx="10" fill="none" ' \
            f'stroke="{p["accent"]}" stroke-width="3"/>'
    outer = f'<rect x="{-px}" y="{-ch - py}" width="{W}" height="{H}" rx="18" fill="none" stroke="{p["accent"]}" ' \
            f'stroke-width="9"/>'
    body = f'<g transform="rotate(-5 {w / 2} {-ch / 2})">{outer}{inner}{fill(d, p["accent"])}</g>'
    return place(body, px + 20, ch + py + 40), round(W + 40), round(H + 80)


def icon13(p, x, y, k):
    d, w = text_path("S", F13, 62, 0, 0)
    ch = cap_height(F13, 62)
    d, _ = text_path("S", F13, 62, 50 - w / 2, 50 + ch / 2)
    return g(x, y, k, f'<g transform="rotate(-5 50 50)"><rect x="6" y="6" width="88" height="88" rx="18" fill="none" '
                      f'stroke="{p["accent"]}" stroke-width="7"/><rect x="15" y="15" width="70" height="70" rx="10" '
                      f'fill="none" stroke="{p["accent"]}" stroke-width="2.5"/>{fill(d, p["accent"])}</g>')


logo(13, "Seal-the-Deal", "Wordmark (stamp)",
     {"accent": G(PINK, ORANGE, angle=20)},
     {"accent": G(PINK, ORANGE, angle=20)},
     {"primary": word13, "icon": icon_only(icon13)})


# =========================================================== Build the Bond — building blocks
def icon14(p, x, y, k):
    return g(x, y, k, fill(rrect(27, 18, 46, 34, 9), p["top"]) + fill(rrect(4, 58, 44, 34, 9), p["left"])
             + fill(rrect(52, 58, 44, 34, 9), p["right"]))


L14 = [dict(t="Build the Bond", f="FrauncesSoft.ttf", s=108, c="main")]
logo(14, "Build-the-Bond", "Symbol + text (blocks)",
     {"main": NAVY, "top": G(GREEN, CYAN_D, angle=45), "left": G(CYAN_D, BLUE, angle=45),
      "right": G(BLUE, INDIGO, angle=45)},
     {"main": WHITE, "top": G(GREEN, CYAN, angle=45), "left": G(CYAN, BLUE, angle=45),
      "right": G(BLUE, VIOLET, angle=45)},
     {"primary": lambda p: lockup_v(p, icon14, L14, isz=210, space=40),
      "horizontal": lambda p: lockup_h(p, icon14, L14, ratio=1.7, space=0.18),
      "icon": icon_only(icon14)})


# =========================================================== Contact to Contract — chat bubble to document
def icon15(p, x, y, k):
    bubble = f"{rrect(2, 6, 60, 44, 14)} M16 48 L12 64 L32 48 Z"
    dots = " ".join(circle_d(cx, 28, 4.5) for cx in (18, 32, 46))
    doc = poly([(38, 34), (78, 34), (96, 52), (96, 96), (38, 96)])
    lines = " ".join(rrect(48, yy, ww, 6, 3) for yy, ww in [(58, 38), (70, 38), (82, 24)])
    fold = poly([(78, 34), (78, 52), (96, 52)])
    return g(x, y, k, fill(f"{bubble} {dots}", p["accent"], True) + fill(f"{doc} {lines}", p["main"], True)
             + fill(fold, p["accent2"]))


def lock15(p, vertical=False):
    S = 100
    body, w = rich(p, [("Contact ", "main")], "Urbanist.ttf", S)
    d2, w2 = text_path("to", "UrbanistLight.ttf", S, w, 0)
    d3, w3 = text_path(" Contract", "Urbanist.ttf", S, w + w2, 0)
    word = body + fill(d2, p["sub"]) + fill(d3, p["main"])
    W, ch = w + w2 + w3, cap_height("Urbanist.ttf", S)
    if vertical:
        isz = 200
        return icon15(p, (W - isz) / 2, 0, isz / 100) + place(word, 0, isz + 50 + ch), round(W), round(isz + 60 + ch)
    isz = ch * 2.4
    return icon15(p, 0, 0, isz / 100) + place(word, isz * 1.2, isz / 2 + ch / 2), round(isz * 1.2 + W), round(isz)


logo(15, "Contact-to-Contract", "Symbol + text (overlap)",
     {"main": NAVY, "accent": G(CYAN_D, BLUE, angle=45), "accent2": BLUE, "sub": BLUE},
     {"main": WHITE, "accent": G(CYAN, BLUE, angle=45), "accent2": CYAN, "sub": CYAN},
     {"primary": lock15, "stacked": lambda p: lock15(p, True), "icon": icon_only(icon15)})


# =========================================================== The Learning Architect — temple of learning
def icon16(p, x, y, k):
    roof = "M50 4 L96 32 H4 Z"
    cols = "".join(fill(rrect(cx, 40, 12, 40, 3), p["main"]) for cx in (14, 44, 74))
    return g(x, y, k, f'<path d="{roof}" fill="{p["accent"]}" stroke="{p["accent"]}" stroke-width="5" '
                      f'stroke-linejoin="round"/>{cols}{fill(rrect(4, 86, 92, 10, 3), p["main"])}')


L16 = [dict(t="THE LEARNING", f="JostSemi.ttf", s=34, c="sub", tr=0.45),
       dict(t="ARCHITECT", f="JostSemi.ttf", s=104, c="main", tr=0.12, gap=24)]
logo(16, "The-Learning-Architect", "Symbol + text (classical)",
     {"main": NAVY, "accent": G(ORANGE, YELLOW, angle=0), "sub": ORANGE},
     {"main": WHITE, "accent": G(ORANGE, YELLOW, angle=0), "sub": YELLOW},
     {"primary": lambda p: lockup_h(p, icon16, L16, ratio=1.6, space=0.18),
      "stacked": lambda p: lockup_v(p, icon16, L16, isz=190),
      "icon": icon_only(icon16)})


# =========================================================== The Leader DNA — fingerprint
def icon17(p, x, y, k):
    arcs = []
    spec = [(8, 200, 520), (17, 185, 470), (26, 175, 430), (35, 165, 400), (44, 175, 365)]
    for r, a0, a1 in spec:
        pts = arc_pts(50, 54, r, a0, a1, 60)
        d = "M" + " L".join(f"{a:.2f} {b:.2f}" for a, b in pts)
        arcs.append(f'<path d="{d}" fill="none" stroke="{p["accent"]}" stroke-width="6" stroke-linecap="round"/>')
    return g(x, y, k, "".join(arcs))


L17 = [dict(t="THE LEADER", f="SpaceGroteskMed.ttf", s=36, c="main", tr=0.35),
       dict(t="DNA", f="SpaceGrotesk.ttf", s=150, c="accent2", gap=22, dx=-6)]
logo(17, "The-Leader-DNA", "Symbol + text (fingerprint)",
     {"main": NAVY, "accent": G(VIOLET, PINK, angle=45), "accent2": G(VIOLET, PINK)},
     {"main": WHITE, "accent": G(VIOLET, PINK, angle=45), "accent2": G(VIOLET, PINK)},
     {"primary": lambda p: lockup_h(p, icon17, L17, ratio=1.15, space=0.2),
      "stacked": lambda p: lockup_v(p, icon17, L17, isz=190),
      "icon": icon_only(icon17)})


if __name__ == "__main__":
    for num, slug, kind, light, dark, builders in LOGOS:
        if ONLY and int(ONLY) != num:
            continue
        blk, wht = mono(light)
        wht["bg"] = DARK_BG
        variants = {"color-light": light, "color-dark": dark, "black": blk, "white": wht}
        zpath, prev = export(slug, slug, builders, variants, OUT)
        preview_sheet(slug, prev, f"{OUT}/{slug}_preview.png")
        print(num, slug, kind)
