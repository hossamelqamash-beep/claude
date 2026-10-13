"""Logo set v4 — refined concepts: negative space, letter-marks and precise geometry.
Run: python3 logos_v4.py <kit_dir> <out_dir> [only_number]"""
import math
import sys

sys.path.insert(0, sys.argv[1])
from logokit import (  # noqa: E402
    cap_height, circle_d, export, g, glyph_bounds, knockout, mono, preview_sheet, rrect, stem,
    text_path, x_height,
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


# ------------------------------------------------------------------ helpers
def G(*colors, angle=0):
    return ("grad", colors, angle)


def resolve(p):
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


def place(body, dx, dy):
    return f'<g transform="translate({dx:.2f} {dy:.2f})">{body}</g>'


def gk(x, y, k, inner):
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.4f})">{inner}</g>'


def poly(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def pline(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def fill(d, col, evenodd=False):
    rule = ' fill-rule="evenodd"' if evenodd else ""
    return f'<path d="{d}" fill="{col}"{rule}/>'


def pt(cx, cy, r, a):
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


def arc_pts(cx, cy, r, a0, a1, n=48):
    return [pt(cx, cy, r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def capsule(P, Q, w, n=16):
    (px, py), (qx, qy) = P, Q
    ang = math.degrees(math.atan2(qy - py, qx - px))
    return poly(arc_pts(qx, qy, w / 2, ang - 90, ang + 90, n) + arc_pts(px, py, w / 2, ang + 90, ang + 270, n))


def arc_band(cx, cy, r, w, a0, a1, n=72):
    """Thick arc with round ends, as a filled outline."""
    c0, c1 = pt(cx, cy, r, a0), pt(cx, cy, r, a1)
    return poly(arc_pts(cx, cy, r + w / 2, a0, a1, n) + arc_pts(*c1, w / 2, a1, a1 + 180, 16)
                + arc_pts(cx, cy, r - w / 2, a1, a0, n) + arc_pts(*c0, w / 2, a0 + 180, a0 + 360, 16))


def ribbon(center, widths):
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


def bez(p0, p1, p2, p3, n=60):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def spark(cx, cy, r, k=0.22):
    return (f"M{cx} {cy - r} C{cx + k * r} {cy - k * r} {cx + k * r} {cy - k * r} {cx + r} {cy} "
            f"C{cx + k * r} {cy + k * r} {cx + k * r} {cy + k * r} {cx} {cy + r} "
            f"C{cx - k * r} {cy + k * r} {cx - k * r} {cy + k * r} {cx - r} {cy} "
            f"C{cx - k * r} {cy - k * r} {cx - k * r} {cy - k * r} {cx} {cy - r}Z")


def seg_line(p, parts, x=0, y=0):
    """parts: (text, font, size, colorkey, tracking) — one baseline, mixed fonts."""
    out, cx = [], x
    for text, font, size, ck, tr in parts:
        d, w = text_path(text, font, size, cx, y, tracking=tr)
        out.append(fill(d, p[ck]))
        cx += w
    return "".join(out), cx - x


def text_lines(p, lines, align="left"):
    """lines: dicts {parts:[(t,f,s,c,tr)], gap}; origin = top of first caps."""
    meas = []
    for ln in lines:
        _, w = seg_line(p, ln["parts"])
        capm = max(cap_height(f, s) for _, f, s, _, _ in ln["parts"])
        meas.append((w, capm))
    W = max(w for w, _ in meas)
    y, out = 0, []
    for i, (ln, (w, capm)) in enumerate(zip(lines, meas)):
        y += (ln.get("gap", 0) if i else 0) + capm
        x = 0 if align == "left" else (W - w) / 2
        body, _ = seg_line(p, ln["parts"], x, y)
        out.append(body)
    return "".join(out), W, y


def lock_h(p, icon, lines, ratio=1.3, space=0.24, shift=0.0):
    body, W, H = text_lines(p, lines)
    isz = H * ratio
    tx = isz * (1 + space)
    return icon(p, 0, 0, isz / 100) + place(body, tx, (isz - H) / 2 + shift * H), round(tx + W), round(isz)


def lock_v(p, icon, lines, isz=200, space=52):
    body, W, H = text_lines(p, lines, align="center")
    WW = max(W, isz)
    return icon(p, (WW - isz) / 2, 0, isz / 100) + place(body, (WW - W) / 2, isz + space), round(WW), \
        round(isz + space + H)


def icon_only(fn):
    return lambda p: (fn(p, 0, 0, 1), 100, 100)


# =========================================================== 1 Doing the Right Thing
# A circle split down the middle: an open left half and a solid right half —
# choosing the right side.
def icon01(p, x, y, k):
    left = poly(arc_pts(46, 50, 46, 90, 270) + arc_pts(46, 50, 36, 270, 90))
    right = poly(arc_pts(54, 50, 46, -90, 90) + [(54, 96)])
    return gk(x, y, k, fill(left, p["main"]) + fill(right, p["accent"]))


L01 = [dict(parts=[("DOING THE", "JakartaMed.ttf", 32, "sub", 0.42)]),
       dict(parts=[("Right", "Jakarta.ttf", 104, "accent_t", 0), (" Thing", "Jakarta.ttf", 104, "main", 0)], gap=24)]
logo(1, "Doing-the-Right-Thing", "Symbol + text",
     {"main": NAVY, "accent": G(GREEN, CYAN_D, angle=90), "accent_t": G(GREEN_D, CYAN_D), "sub": GREEN_D},
     {"main": WHITE, "accent": G(GREEN, CYAN, angle=90), "accent_t": G(GREEN, CYAN), "sub": GREEN},
     {"primary": lambda p: lock_h(p, icon01, L01, ratio=1.3),
      "stacked": lambda p: lock_v(p, icon01, L01, isz=190),
      "icon": icon_only(icon01)})


# =========================================================== 2 The Political Savvy Leader
# A crown drawn as an influence network: the three points are connected nodes.
def icon02(p, x, y, k):
    crown = pline([(20, 70), (15, 30), (33, 52), (50, 14), (67, 52), (85, 30), (80, 70)])
    return gk(x, y, k,
              f'<path d="{crown}" fill="none" stroke="{p["accent"]}" stroke-width="7.5" stroke-linecap="round" '
              f'stroke-linejoin="round"/>'
              + fill(rrect(12, 78, 76, 13, 6.5), p["accent"])
              + "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{p["node"]}"/>'
                        for cx, cy, r in [(15, 30, 8), (50, 14, 9.5), (85, 30, 8)]))


L02 = [dict(parts=[("THE POLITICAL", "SoraReg.ttf", 32, "sub", 0.3)]),
       dict(parts=[("Savvy Leader", "Sora.ttf", 100, "main", -0.01)], gap=26)]
logo(2, "The-Political-Savvy-Leader", "Symbol + text",
     {"main": NAVY, "accent": G(VIOLET, INDIGO, angle=90), "node": G(PINK, VIOLET, angle=90), "sub": INDIGO},
     {"main": WHITE, "accent": G(SKY, VIOLET, angle=90), "node": G(PINK, VIOLET, angle=90), "sub": "#B3A4FF"},
     {"primary": lambda p: lock_h(p, icon02, L02, ratio=1.4),
      "stacked": lambda p: lock_v(p, icon02, L02, isz=200),
      "icon": icon_only(icon02)})


# =========================================================== 3 The Catalyst Within
# The "C" of Catalyst is an open ring with a spark inside it.
F03, F03L = "OutfitBold.ttf", "OutfitLight.ttf"


def c_mark(p, x, base, S):
    x0, y0, x1, y1, adv = glyph_bounds("C", F03, S)
    w = stem(F03, S, "l") * 1.05
    cx, cy = x + (x0 + x1) / 2 + S * 0.02, base - (y0 + y1) / 2
    r = (y1 - y0) / 2 - w / 2
    return (fill(arc_band(cx, cy, r, w, 58, 302), p["accent"])
            + f'<g transform="rotate(45 {cx + r * 0.1:.2f} {cy:.2f})">' + fill(spark(cx + r * 0.1, cy, r * 0.62, 0.2), p["spark"]) + "</g>"), adv


def word03(p, small=True):
    S = 140
    _, adv = c_mark(p, 0, 0, S)
    mark, _ = c_mark(p, 0, S, S)
    rest, w = seg_line(p, [("atalyst", F03, S, "main", 0), (" within", F03L, S, "sub", 0)], adv + S * 0.02, S)
    W = adv + S * 0.02 + w
    body = mark + rest
    if small:
        d, ws = text_path("THE", "JakartaMed.ttf", 30, 0, 0, tracking=0.6)
        d, _ = text_path("THE", "JakartaMed.ttf", 30, adv + S * 0.04, S - cap_height(F03, S) - 34, tracking=0.6)
        body += fill(d, p["sub"])
    return body, round(W), round(1.3 * S)


def icon03(p, x, y, k):
    cx, cy, r, w = 50, 50, 38, 15
    return gk(x, y, k, fill(arc_band(cx, cy, r, w, 58, 302), p["accent"]) + '<g transform="rotate(45 54 50)">' + fill(spark(54, 50, 22, 0.2), p["spark"]) + "</g>")


logo(3, "The-Catalyst-Within", "Letter mark (embedded)",
     {"main": NAVY, "sub": ORANGE, "accent": G(YELLOW, ORANGE, PINK, angle=90), "spark": G(ORANGE, PINK, angle=90)},
     {"main": WHITE, "sub": YELLOW, "accent": G(YELLOW, ORANGE, PINK, angle=90), "spark": G(YELLOW, ORANGE, angle=90)},
     {"primary": word03, "icon": icon_only(icon03)})


# =========================================================== 4 The Visionary Path
# The "V" carries a rising sun in its opening; "PATH" is spaced to the full width.
F04, F04s = "MontserratXB.ttf", "Montserrat.ttf"


def word04(p):
    S = 130
    x0, y0, x1, y1, adv = glyph_bounds("V", F04, S)
    dv, wv = text_path("V", F04, S, 0, S)
    rest, wr = seg_line(p, [("ISIONARY", F04, S, "main", 0)], wv, S)
    W = wv + wr
    sw = stem(F04, S, "I")
    sun = f'<circle cx="{(x0 + x1) / 2:.1f}" cy="{S - y1 * 0.80:.1f}" r="{sw * 0.42:.1f}" fill="{p["sun"]}"/>'
    s = 40
    tr = 0.6
    plain = text_path("PATH", F04s, s, 0, 0, tracking=tr)[1]
    d2, _ = text_path("PATH", F04s, s, W - plain, S + 32 + cap_height(F04s, s), tracking=tr)
    d1, _ = text_path("THE", F04s, s, 0, S - cap_height(F04, S) - 30, tracking=0.5)
    return (fill(dv, p["accent"]) + sun + rest + fill(d2, p["sub"]) + fill(d1, p["sub"])), round(W), round(S + 90)


def icon04(p, x, y, k):
    d, w = text_path("V", F04, 128, 0, 0)
    x0, y0, x1, y1, _ = glyph_bounds("V", F04, 128)
    ox = 50 - (x0 + x1) / 2
    sw = stem(F04, 128, "I")
    return gk(x, y, k, fill(text_path("V", F04, 128, ox, 95)[0], p["accent"])
              + f'<circle cx="50" cy="{95 - y1 * 0.80:.1f}" r="{sw * 0.42:.1f}" fill="{p["sun"]}"/>')


logo(4, "The-Visionary-Path", "Letter mark (embedded)",
     {"main": NAVY, "accent": G(BLUE, INDIGO, angle=90), "sun": G(YELLOW, ORANGE, angle=90), "sub": BLUE},
     {"main": WHITE, "accent": G(CYAN, BLUE, angle=90), "sun": G(YELLOW, ORANGE, angle=90), "sub": SKY},
     {"primary": word04, "icon": icon_only(icon04)})


# =========================================================== 5 The Modern Leader Blueprint
# A folded plan: three panels, alternating tilt, like an unfolded blueprint.
def icon05(p, x, y, k):
    panels = [([(6, 24), (34, 12), (34, 78), (6, 90)], "c1"), ([(37, 12), (63, 24), (63, 90), (37, 78)], "c2"),
              ([(66, 24), (94, 12), (94, 78), (66, 90)], "c3")]
    out = ""
    for pts, ck in panels:
        out += f'<path d="{poly(pts)}" fill="{p[ck]}" stroke="{p[ck]}" stroke-width="3" stroke-linejoin="round"/>'
    return gk(x, y, k, out)


L05 = [dict(parts=[("THE MODERN LEADER", "JetBrainsMono.ttf", 30, "sub", 0.1)]),
       dict(parts=[("Blueprint", "SpaceGrotesk.ttf", 118, "main", -0.01)], gap=26)]
logo(5, "The-Modern-Leader-Blueprint", "Symbol + text",
     {"main": NAVY, "sub": BLUE, "c1": G(CYAN_D, BLUE, angle=90), "c2": G(BLUE, INDIGO, angle=90),
      "c3": G(CYAN_D, BLUE, angle=90)},
     {"main": WHITE, "sub": SKY, "c1": G(CYAN, BLUE, angle=90), "c2": G(SKY, BLUE, angle=90),
      "c3": G(CYAN, BLUE, angle=90)},
     {"primary": lambda p: lock_h(p, icon05, L05, ratio=1.3),
      "stacked": lambda p: lock_v(p, icon05, L05, isz=190),
      "icon": icon_only(icon05)})


# =========================================================== 6 The Team Advantage
# The first "A" of ADVANTAGE is a triangle of three capsules — three people, one shape.
F06 = "Figtree.ttf"


def tri_capsules(p, A, B, C, w):
    def short(P, Q, cut):
        L = math.hypot(Q[0] - P[0], Q[1] - P[1])
        t = (L - cut) / L
        return P, (P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t)
    out = ""
    for (P, Q), ck in zip([(A, B), (B, C), (C, A)], ["c1", "c2", "c3"]):
        P2, Q2 = short(P, Q, w * 1.25)
        out += fill(capsule(P2, Q2, w), p[ck])
    return out


def a_mark(p, x, base, S):
    x0, y0, x1, y1, adv = glyph_bounds("A", F06, S)
    w = stem(F06, S, "I") * 0.95
    A = (x + (x0 + x1) / 2, base - y1 + w / 2)
    B = (x + x1 - w / 2, base - w / 2)
    C = (x + x0 + w / 2, base - w / 2)
    return tri_capsules(p, A, B, C, w), adv


def word06(p):
    S = 120
    _, adv = a_mark(p, 0, 0, S)
    mark, _ = a_mark(p, 0, S, S)
    rest, w = seg_line(p, [("DVANTAGE", F06, S, "main", 0.02)], adv + S * 0.03, S)
    W = adv + S * 0.03 + w
    d, _ = text_path("THE TEAM", "FigtreeMed.ttf", 32, 4, S - cap_height(F06, S) - 30, tracking=0.55)
    return mark + rest + fill(d, p["sub"]), round(W), round(1.3 * S)


def icon06(p, x, y, k):
    return gk(x, y, k, tri_capsules(p, (50, 12), (90, 84), (10, 84), 15))


logo(6, "The-Team-Advantage", "Letter mark (embedded)",
     {"main": NAVY, "sub": GREEN_D, "c1": G(GREEN, CYAN_D, angle=60), "c2": G(CYAN_D, BLUE), "c3": G(BLUE, INDIGO, angle=60)},
     {"main": WHITE, "sub": GREEN, "c1": G(GREEN, CYAN, angle=60), "c2": G(CYAN, BLUE), "c3": G(BLUE, VIOLET, angle=60)},
     {"primary": word06, "icon": icon_only(icon06)})


# =========================================================== 7 Leading Beyond Borders
# A globe of latitude bands; the middle band breaks out of the circle as an arrow.
def icon07(p, x, y, k):
    cx, cy, R = 44, 50, 42
    bands, out = [(9, 21), (25, 38), (42, 58), (62, 75), (79, 91)], ""

    def side(y0, y1, sgn, n=16):
        pts = []
        for i in range(n + 1):
            yy = y0 + (y1 - y0) * i / n
            dx = math.sqrt(max(R * R - (yy - cy) ** 2, 0))
            pts.append((cx + sgn * dx, yy))
        return pts
    for i, (a, b) in enumerate(bands):
        if i == 2:
            m = (a + b) / 2
            left = side(b, a, -1)
            d = poly(left + [(78, a), (78, a - 8), (98, m), (78, b + 8), (78, b)])
            out += fill(d, p["arrow"])
        else:
            out += fill(poly(side(a, b, 1) + side(b, a, -1)), p["accent"])
    return gk(x, y, k, out)


L07 = [dict(parts=[("LEADING", "JakartaMed.ttf", 32, "sub", 0.6)]),
       dict(parts=[("Beyond Borders", "ManropeXB.ttf", 100, "main", -0.01)], gap=24)]
logo(7, "Leading-Beyond-Borders", "Symbol + text",
     {"main": NAVY, "accent": G(CYAN_D, BLUE, angle=90), "arrow": G(ORANGE, PINK), "sub": BLUE},
     {"main": WHITE, "accent": G(CYAN, BLUE, angle=90), "arrow": G(YELLOW, ORANGE), "sub": CYAN},
     {"primary": lambda p: lock_h(p, icon07, L07, ratio=1.65, space=0.2),
      "stacked": lambda p: lock_v(p, icon07, L07, isz=200),
      "icon": icon_only(icon07)})


# =========================================================== 8 The Business Case Lab
# A flask whose liquid line is a rising chart.
def icon08(p, x, y, k):
    flask = "M36 7 H64 M42 7 V36 L17 80 Q12 92 26 92 H74 Q88 92 83 80 L58 36 V7"

    def xl(yy):
        return 42 - (yy - 36) * 25 / 44 + 7.5

    def xr(yy):
        return 58 + (yy - 36) * 25 / 44 - 7.5
    liquid = poly([(xl(84), 84), (xl(70), 70), (36, 72), (47, 60), (57, 65), (xr(50), 50), (xr(84), 84)])
    return gk(x, y, k, f'<path d="{flask}" fill="none" stroke="{p["main"]}" stroke-width="6.5" stroke-linecap="round" '
                       f'stroke-linejoin="round"/>'
              + f'<path d="{liquid}" fill="{p["accent"]}" stroke="{p["accent"]}" stroke-width="3" '
                f'stroke-linejoin="round"/>')


L08 = [dict(parts=[("Business Case", "Archivo.ttf", 100, "main", -0.01)]),
       dict(parts=[("LAB", "Archivo.ttf", 44, "sub", 0.5)], gap=28)]
logo(8, "The-Business-Case-Lab", "Symbol + text",
     {"main": NAVY, "accent": G(GREEN, CYAN_D, BLUE), "sub": GREEN_D},
     {"main": WHITE, "accent": G(GREEN, CYAN, BLUE), "sub": CYAN},
     {"primary": lambda p: lock_h(p, icon08, L08, ratio=1.45, space=0.18),
      "stacked": lambda p: lock_v(p, icon08, L08, isz=200),
      "icon": icon_only(icon08)})


# =========================================================== 9 Driving High Performance
# Sporty two-tier wordmark: outline italic over a solid gradient italic.
F09 = "BarlowCondIt.ttf"


def word09(p):
    s1, s2 = 96, 150
    c1, c2 = cap_height(F09, s1), cap_height(F09, s2)
    d1, w1 = text_path("DRIVING HIGH", F09, s1, 14, c1, tracking=0.04)
    d2, w2 = text_path("PERFORMANCE", F09, s2, 0, c1 + 20 + c2, tracking=0.0)
    return (f'<path d="{d1}" fill="none" stroke="{p["main"]}" stroke-width="3.2" stroke-linejoin="round"/>'
            + fill(d2, p["accent"])), round(max(w1 + 14, w2)), round(c1 + 20 + c2)


def icon09(p, x, y, k):
    d, w = text_path("HP", F09, 110, 0, 0)
    ch = cap_height(F09, 110)
    d, _ = text_path("HP", F09, 110, 50 - w / 2 + 2, 50 + ch / 2)
    return gk(x, y, k, fill(f"{rrect(0, 0, 100, 100, 24)} {d}", p["accent"], True))


logo(9, "Driving-High-Performance", "Wordmark",
     {"main": NAVY, "accent": G(YELLOW, ORANGE, PINK)},
     {"main": WHITE, "accent": G(YELLOW, ORANGE, PINK)},
     {"primary": word09, "icon": icon_only(icon09)})


# =========================================================== 10 Strategy That Delivers
# A dotted route that ends at a location pin — the plan, delivered.
def icon10(p, x, y, k):
    cx, cy, r = 70, 30, 22
    a0, a1 = 140, 400
    pin = poly(arc_pts(cx, cy, r, a0, a1) + [(cx, 74)])
    dots = ""
    for i in range(5):
        t = i / 5
        qx = (1 - t) ** 2 * 8 + 2 * (1 - t) * t * 34 + t * t * 58
        qy = (1 - t) ** 2 * 92 + 2 * (1 - t) * t * 96 + t * t * 76
        dots += f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="{3.2 + i * 0.5:.1f}" fill="{p["main"]}"/>'
    return gk(x, y, k, dots + fill(f"{pin} {circle_d(cx, cy, 8.5)}", p["accent"], True))


L10 = [dict(parts=[("Strategy", "Urbanist.ttf", 124, "main", -0.01)]),
       dict(parts=[("THAT DELIVERS", "UrbanistSemi.ttf", 38, "sub", 0.45)], gap=60)]
logo(10, "Strategy-That-Delivers", "Symbol + text",
     {"main": NAVY, "accent": G(YELLOW, ORANGE, angle=90), "sub": ORANGE},
     {"main": WHITE, "accent": G(YELLOW, ORANGE, angle=90), "sub": YELLOW},
     {"primary": lambda p: lock_h(p, icon10, L10, ratio=1.25, space=0.2),
      "stacked": lambda p: lock_v(p, icon10, L10, isz=200),
      "icon": icon_only(icon10)})


# =========================================================== 11 Beyond the Deal
# Serif wordmark; the tail of the "y" becomes a long tapered swash that runs beyond the words.
F11 = "DMSerif.ttf"


def word11(p):
    S = 136
    dB, wB = text_path("Be", F11, S, 0, S)
    x0, y0, x1, y1, advy = glyph_bounds("y", F11, S)
    dy, wy = text_path("y", F11, S, wB, S)
    dr, wr = text_path("ond the Deal", F11, S, wB + wy, S)
    W = wB + wy + wr
    start = (wB + x0 + S * 0.035, S - y0 - S * 0.012)
    pts = bez(start, (start[0] + S * 0.35, start[1] + S * 0.3), (W * 0.62, start[1] + S * 0.2),
              (W + S * 0.14, start[1] - S * 0.3), 120)
    n = len(pts) - 1
    widths = [S * 0.085 * math.sin(math.pi * min(1, 0.15 + i / n * 0.85)) ** 0.7 + 1.5 for i in range(n + 1)]
    return (fill(f"{dB} {dy} {dr}", p["main"]) + fill(ribbon(pts, widths), p["accent"])), round(W + S * 0.12), \
        round(S * 1.45)


def icon11(p, x, y, k):
    d, w = text_path("B", F11, 100, 0, 0)
    ch = cap_height(F11, 100)
    pts = bez((14, 84), (40, 92), (70, 90), (92, 70), 50)
    widths = [5.5 * (1 - i / 50) + 1.2 for i in range(51)]
    return gk(x, y, k, fill(text_path("B", F11, 100, 50 - w / 2, 12 + ch)[0], p["main"])
              + fill(ribbon(pts, widths), p["accent"]))


logo(11, "Beyond-the-Deal", "Wordmark (swash)",
     {"main": NAVY, "accent": G(PURPLE, PINK)},
     {"main": WHITE, "accent": G(VIOLET, PINK)},
     {"primary": word11, "icon": icon_only(icon11)})


# =========================================================== 12 Wealth Advisory Mastery
# A faceted gem — value, clarity and craft.
def icon12(p, x, y, k):
    facets = [([(8, 38), (28, 14), (37, 38)], "c1"), ([(28, 14), (72, 14), (63, 38), (37, 38)], "c2"),
              ([(63, 38), (72, 14), (92, 38)], "c1"), ([(8, 38), (37, 38), (50, 92)], "c2"),
              ([(37, 38), (63, 38), (50, 92)], "c1"), ([(63, 38), (92, 38), (50, 92)], "c2")]
    out = ""
    for pts, ck in facets:
        cxm = sum(a for a, _ in pts) / len(pts)
        cym = sum(b for _, b in pts) / len(pts)
        sh = [(cxm + (a - cxm) * 0.9, cym + (b - cym) * 0.9) for a, b in pts]
        out += f'<path d="{poly(sh)}" fill="{p[ck]}" stroke="{p[ck]}" stroke-width="2" stroke-linejoin="round"/>'
    return gk(x, y, k, out)


L12 = [dict(parts=[("WEALTH ADVISORY", "CormorantSemi.ttf", 78, "main", 0.08)]),
       dict(parts=[("MASTERY", "Jost.ttf", 30, "sub", 0.95)], gap=30)]
logo(12, "Wealth-Advisory-Mastery", "Emblem (stacked)",
     {"main": NAVY, "c1": G(YELLOW, "#FFD978", angle=90), "c2": G(ORANGE, "#D9871A", angle=90), "sub": "#D98E00"},
     {"main": WHITE, "c1": G("#FFE29A", YELLOW, angle=90), "c2": G(YELLOW, ORANGE, angle=90), "sub": YELLOW},
     {"primary": lambda p: lock_v(p, icon12, L12, isz=190, space=56),
      "horizontal": lambda p: lock_h(p, icon12, L12, ratio=1.5, space=0.2),
      "icon": icon_only(icon12)})


# =========================================================== 13 Seal the Deal
# An envelope whose flap is a check mark — the deal, sealed and approved.
def icon13(p, x, y, k):
    env = (f'<path d="{rrect(5, 28, 90, 62, 10)}" fill="none" stroke="{p["main"]}" stroke-width="7"/>'
           '')
    chk = poly([(14, 40), (22, 32), (47, 56), (88, 6), (97, 14), (47, 72)])
    return gk(x, y, k, env + f'<path d="{chk}" fill="{p["accent"]}" stroke="{p["accent"]}" stroke-width="3" '
                             f'stroke-linejoin="round"/>')


L13 = [dict(parts=[("Seal the Deal", "PoppinsBold.ttf", 104, "main", -0.01)])]
logo(13, "Seal-the-Deal", "Symbol + text",
     {"main": NAVY, "accent": G(PINK, ORANGE, angle=-30)},
     {"main": WHITE, "accent": G(PINK, ORANGE, angle=-30)},
     {"primary": lambda p: lock_h(p, icon13, L13, ratio=1.7, space=0.2, shift=-0.05),
      "stacked": lambda p: lock_v(p, icon13, L13, isz=210, space=44),
      "icon": icon_only(icon13)})


# =========================================================== 14 Build the Bond
# Two interlocking pieces that complete one square around a shared centre.
def icon14(p, x, y, k):
    u, o, gp, r = 28, 8, 2.6, 7

    def R(c0, r0, c1, r1):
        return rrect(o + c0 * u + gp, o + r0 * u + gp, (c1 - c0) * u - 2 * gp, (r1 - r0) * u - 2 * gp, r)
    a = fill(R(0, 0, 3, 1), p["c1"]) + fill(R(0, 0, 1, 2), p["c1"])
    b = fill(R(0, 2, 3, 3), p["c2"]) + fill(R(2, 1, 3, 3), p["c2"])
    return gk(x, y, k, a + b)


L14 = [dict(parts=[("Build the Bond", "FrauncesSoft.ttf", 106, "main", -0.01)])]
logo(14, "Build-the-Bond", "Symbol + text",
     {"main": NAVY, "c1": G(GREEN, CYAN_D, angle=0), "c2": G(BLUE, INDIGO, angle=0)},
     {"main": WHITE, "c1": G(GREEN, CYAN, angle=0), "c2": G(SKY, BLUE, angle=0)},
     {"primary": lambda p: lock_v(p, icon14, L14, isz=200, space=44),
      "horizontal": lambda p: lock_h(p, icon14, L14, ratio=1.6, space=0.2),
      "icon": icon_only(icon14)})


# =========================================================== 15 Contact to Contract
# A chat bubble that carries a signature — conversation becomes commitment.
def icon15(p, x, y, k):
    bubble = rrect(4, 8, 92, 66, 20)
    n = 70
    pts = []
    for i in range(n + 1):
        t = i / n
        xx = 18 + 64 * t
        yy = 42 - 9 * math.sin(t * 2 * math.pi) * (1 - 0.3 * t)
        pts.append((xx, yy))
    widths = [3 + 3.5 * math.sin(math.pi * i / n) for i in range(n + 1)]
    sig = ribbon(pts, widths)
    line = rrect(18, 58, 64, 4.5, 2.25)
    tail = poly([(20, 72), (16, 94), (44, 72)])
    return gk(x, y, k, fill(f"{bubble} {sig} {line}", p["accent"], True) + fill(tail, p["accent"]))


def lock15(p, vertical=False):
    parts = [("Contact ", "Lexend.ttf", 96, "main", -0.01), ("to", "LexendLight.ttf", 96, "sub", 0),
             (" Contract", "Lexend.ttf", 96, "main", -0.01)]
    L = [dict(parts=parts)]
    return lock_v(p, icon15, L, isz=200, space=46) if vertical else lock_h(p, icon15, L, ratio=2.2, space=0.18,
                                                                             shift=-0.06)


logo(15, "Contact-to-Contract", "Symbol + text",
     {"main": NAVY, "accent": G(CYAN_D, BLUE, INDIGO, angle=45), "sub": BLUE},
     {"main": WHITE, "accent": G(CYAN, BLUE, angle=45), "sub": CYAN},
     {"primary": lock15, "stacked": lambda p: lock15(p, True), "icon": icon_only(icon15)})


# =========================================================== 16 The Learning Architect
# An open book whose pages rise to a peak, like a roofline.
def icon16(p, x, y, k):
    left = [(4, 34), (47, 16), (47, 92), (4, 80)]
    right = [(53, 16), (96, 34), (96, 80), (53, 92)]

    def lines(x0, x1, sgn):
        out = []
        for off in (24, 40):
            def yy(xx):
                return (34 + (16 - 34) * (xx - 4) / 43 if sgn < 0 else 16 + (34 - 16) * (xx - 53) / 43) + off
            out.append(poly([(x0, yy(x0)), (x1, yy(x1)), (x1, yy(x1) + 4.5), (x0, yy(x0) + 4.5)]))
        return " ".join(out)
    return gk(x, y, k, fill(f"{poly(left)} {lines(13, 39, -1)}", p["c1"], True)
              + fill(f"{poly(right)} {lines(61, 87, 1)}", p["c2"], True))


L16 = [dict(parts=[("THE LEARNING", "Josefin.ttf", 34, "sub", 0.42)]),
       dict(parts=[("ARCHITECT", "Josefin.ttf", 104, "main", 0.1)], gap=26)]
logo(16, "The-Learning-Architect", "Symbol + text",
     {"main": NAVY, "c1": G(YELLOW, ORANGE, angle=90), "c2": NAVY, "sub": ORANGE},
     {"main": WHITE, "c1": G(YELLOW, ORANGE, angle=90), "c2": WHITE, "sub": YELLOW},
     {"primary": lambda p: lock_h(p, icon16, L16, ratio=1.6, space=0.18),
      "stacked": lambda p: lock_v(p, icon16, L16, isz=190),
      "icon": icon_only(icon16)})


# =========================================================== 17 The Leader DNA
# A double helix drawn in dots; dot size follows depth, so it turns in 3D.
def icon17(p, x, y, k):
    # double helix: two strands of dots crossing twice, joined by rungs
    out, n = [], 10
    for i in range(n):
        t = i / (n - 1)
        yy = 8 + 84 * t
        sn = math.sin(t * 2 * math.pi * 0.9 + 0.5)
        xa, xb = 50 + 24 * sn, 50 - 24 * sn
        if abs(sn) > 0.4:
            out.append(fill(capsule((min(xa, xb) + 6, yy), (max(xa, xb) - 6, yy), 3), p["rung"]))
        out.append(f'<circle cx="{xa:.2f}" cy="{yy:.2f}" r="4.8" fill="{p["c1"]}"/>'
                   f'<circle cx="{xb:.2f}" cy="{yy:.2f}" r="4.8" fill="{p["c2"]}"/>')
    return gk(x, y, k, "".join(out))


L17 = [dict(parts=[("THE LEADER", "RedHatBold.ttf", 36, "main", 0.32)]),
       dict(parts=[("DNA", "RedHat.ttf", 148, "accent", 0.02)], gap=22)]
logo(17, "The-Leader-DNA", "Symbol + text",
     {"main": NAVY, "accent": G(VIOLET, PINK), "c1": VIOLET, "c2": PINK, "rung": G(VIOLET, PINK)},
     {"main": WHITE, "accent": G(VIOLET, PINK), "c1": "#A592FF", "c2": PINK, "rung": G(VIOLET, PINK)},
     {"primary": lambda p: lock_h(p, icon17, L17, ratio=1.15, space=0.06),
      "stacked": lambda p: lock_v(p, icon17, L17, isz=190),
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
