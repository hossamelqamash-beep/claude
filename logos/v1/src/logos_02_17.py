"""Logos 02-17. Each entry: palettes (light/dark) + layout builders.
Run: python3 logos_02_17.py <kit_dir> <out_dir> [only_number]"""
import math
import sys

sys.path.insert(0, sys.argv[1])
from logokit import (  # noqa: E402
    cap_height, export, g, lockup_h, lockup_v, mono, preview_sheet, text_block, text_path,
)

OUT = sys.argv[2]
ONLY = sys.argv[3] if len(sys.argv) > 3 else None
LOGOS = []


def logo(num, slug, light, dark):
    def deco(builders):
        LOGOS.append((num, slug, light, dark, builders))
        return builders
    return deco


def ring_arc(cx, cy, r, a0, a1):
    """SVG arc from angle a0 to a1 (degrees, clockwise in screen space)."""
    t0, t1 = math.radians(a0), math.radians(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f"M{cx + r * math.cos(t0):.2f} {cy + r * math.sin(t0):.2f} "
            f"A{r} {r} 0 {large} 1 {cx + r * math.cos(t1):.2f} {cy + r * math.sin(t1):.2f}")


# ------------------------------------------------------------ 02 Political Savvy Leader
def icon02(p, x, y, k):
    a, b, c = (22, 76), (78, 76), (50, 26)
    lines = f"M{a[0]} {a[1]} L{c[0]} {c[1]} L{b[0]} {b[1]} Z"
    return g(x, y, k,
             f'<path d="{lines}" fill="none" stroke="{p["main"]}" stroke-width="6" stroke-linejoin="round"/>'
             f'<circle cx="{a[0]}" cy="{a[1]}" r="11" fill="{p["main"]}"/>'
             f'<circle cx="{b[0]}" cy="{b[1]}" r="11" fill="{p["main"]}"/>'
             f'<circle cx="{c[0]}" cy="{c[1]}" r="17" fill="{p["accent"]}"/>')


L02 = [dict(t="THE POLITICAL", f="SoraReg.ttf", s=34, c="sub", tr=0.18),
       dict(t="Savvy Leader", f="Sora.ttf", s=96, c="main", gap=24)]
logo(2, "02_The-Political-Savvy-Leader",
     {"bg": "#FFFFFF", "main": "#22223B", "accent": "#EE6C4D", "sub": "#EE6C4D"},
     {"bg": "#1A1A2E", "main": "#F2F2F7", "accent": "#FF8466", "sub": "#FF8466"})({
    "primary": lambda p: lockup_h(p, icon02, L02, ratio=1.5, space=0.3),
    "stacked": lambda p: lockup_v(p, icon02, L02),
    "icon": lambda p: (icon02(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 03 Catalyst Within
def icon03(p, x, y, k):
    hexagon = " ".join(f"{50 + 42 * math.cos(math.radians(a)):.2f},{50 + 42 * math.sin(math.radians(a)):.2f}"
                       for a in range(-90, 270, 60))
    spark = "M50 24 C52.5 43 57 47.5 76 50 C57 52.5 52.5 57 50 76 C47.5 57 43 52.5 24 50 C43 47.5 47.5 43 50 24Z"
    return g(x, y, k,
             f'<polygon points="{hexagon}" fill="none" stroke="{p["main"]}" stroke-width="7" stroke-linejoin="round"/>'
             f'<path d="{spark}" fill="{p["accent"]}"/>')


L03 = [dict(t="the catalyst", f="Syne.ttf", s=92, c="main"),
       dict(t="within", f="Syne.ttf", s=92, c="accent", gap=44)]
logo(3, "03_The-Catalyst-Within",
     {"bg": "#FFFFFF", "main": "#1B1B2F", "accent": "#FF5A1F"},
     {"bg": "#14141F", "main": "#FFFFFF", "accent": "#FF6B33"})({
    "primary": lambda p: lockup_h(p, icon03, L03, ratio=1.35, space=0.25),
    "stacked": lambda p: lockup_v(p, icon03, L03, isz=200),
    "icon": lambda p: (icon03(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 04 Visionary Path (wordmark)
def word04(p):
    big = 132
    d1, w1 = text_path("The Visionary", "DMSerif.ttf", big, 0, 0)
    ch = cap_height("DMSerif.ttf", big)
    sm = 40
    y2 = 0 + 34 + cap_height("DMSans.ttf", sm) + 18
    d2, w2 = text_path("PATH", "DMSans.ttf", sm, 4, y2, tracking=0.55)
    # rising path line from after "PATH" to the right edge, ending in a star-dot
    sx, ex = w2 + 34, w1 + 30
    sy, ey = y2 - cap_height("DMSans.ttf", sm) / 2, -ch * 0.45 - 40
    path = f"M{sx:.1f} {sy:.1f} C{w1 - 40:.1f} {sy:.1f} {w1 + 18:.1f} {sy - 8:.1f} {ex:.1f} {ey + 40:.1f}"
    body = (f'<path d="{d1}" fill="{p["main"]}"/><path d="{d2}" fill="{p["accent"]}"/>'
            f'<path d="{path}" fill="none" stroke="{p["accent"]}" stroke-width="6" stroke-linecap="round"/>'
            f'<circle cx="{ex:.1f}" cy="{ey + 40:.1f}" r="11" fill="{p["accent"]}"/>')
    return body, round(w1), round(y2)


def icon04(p, x, y, k):
    d, w = text_path("V", "DMSerif.ttf", 104, 0, 0)
    ch = cap_height("DMSerif.ttf", 104)
    return g(x, y, k,
             f'<path d="{d}" fill="{p["main"]}" transform="translate({(100 - w) / 2 - 4} {50 + ch / 2})"/>'
             f'<circle cx="86" cy="{50 - ch / 2 + 4}" r="8" fill="{p["accent"]}"/>')


logo(4, "04_The-Visionary-Path",
     {"bg": "#FFFFFF", "main": "#14213D", "accent": "#E8920C"},
     {"bg": "#0E1830", "main": "#F5F1E8", "accent": "#FCA311"})({
    "primary": word04,
    "icon": lambda p: (icon04(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 05 Modern Leader Blueprint
def icon05(p, x, y, k):
    return g(x, y, k,
             f'<rect x="8" y="8" width="84" height="84" rx="14" fill="none" stroke="{p["main"]}" stroke-width="7"/>'
             f'<path d="M50 14 V86 M14 50 H86" stroke="{p["main"]}" stroke-width="3" stroke-dasharray="5 5"/>'
             f'<rect x="56" y="20" width="24" height="24" rx="5" fill="{p["accent"]}"/>'
             f'<path d="M24 32 V76 H68" fill="none" stroke="{p["main"]}" stroke-width="9" stroke-linecap="round" '
             f'stroke-linejoin="round"/>')


L05 = [dict(t="THE MODERN LEADER", f="JetBrainsMono.ttf", s=30, c="sub", tr=0.12),
       dict(t="Blueprint", f="SpaceGrotesk.ttf", s=118, c="main", gap=26)]
logo(5, "05_The-Modern-Leader-Blueprint",
     {"bg": "#FFFFFF", "main": "#1D4ED8", "accent": "#38BDF8", "sub": "#0F2A6B"},
     {"bg": "#0A1A40", "main": "#FFFFFF", "accent": "#38BDF8", "sub": "#93C5FD"})({
    "primary": lambda p: lockup_h(p, icon05, L05, ratio=1.15, space=0.3),
    "stacked": lambda p: lockup_v(p, icon05, L05, isz=190),
    "icon": lambda p: (icon05(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 06 Team Advantage
def icon06(p, x, y, k):
    out = []
    for i, (bx, h) in enumerate([(12, 30), (41, 46), (70, 62)]):
        col = p["accent"] if i == 2 else p["main"]
        top = 92 - h
        out.append(f'<rect x="{bx}" y="{top}" width="18" height="{h}" rx="9" fill="{col}"/>'
                   f'<circle cx="{bx + 9}" cy="{top - 15}" r="9" fill="{col}"/>')
    return g(x, y, k, "".join(out))


L06 = [dict(t="The Team", f="OutfitLight.ttf", s=56, c="sub"),
       dict(t="Advantage", f="Outfit.ttf", s=104, c="main", gap=22)]
logo(6, "06_The-Team-Advantage",
     {"bg": "#FFFFFF", "main": "#10324A", "accent": "#0EA594", "sub": "#0E8A7C"},
     {"bg": "#0B2233", "main": "#FFFFFF", "accent": "#2DD4BF", "sub": "#5EEAD4"})({
    "primary": lambda p: lockup_h(p, icon06, L06, ratio=1.35, space=0.25),
    "stacked": lambda p: lockup_v(p, icon06, L06, isz=180),
    "icon": lambda p: (icon06(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 07 Leading Beyond Borders
def icon07(p, x, y, k):
    return g(x, y, k,
             f'<circle cx="46" cy="54" r="36" fill="none" stroke="{p["main"]}" stroke-width="7"/>'
             f'<ellipse cx="46" cy="54" rx="15" ry="36" fill="none" stroke="{p["main"]}" stroke-width="5"/>'
             f'<path d="M10 54 H82" stroke="{p["main"]}" stroke-width="5"/>'
             f'<path d="M62 22 L90 8 M76 6 L90 8 L88 22" fill="none" stroke="{p["accent"]}" stroke-width="7" '
             f'stroke-linecap="round" stroke-linejoin="round"/>'
             f'<circle cx="62" cy="22" r="7" fill="{p["accent"]}"/>')


L07 = [dict(t="LEADING", f="JakartaMed.ttf", s=34, c="sub", tr=0.42),
       dict(t="Beyond Borders", f="Jakarta.ttf", s=92, c="main", gap=24)]
logo(7, "07_Leading-Beyond-Borders",
     {"bg": "#FFFFFF", "main": "#344E41", "accent": "#D4893B", "sub": "#B86E22"},
     {"bg": "#1F2E26", "main": "#F1EDE4", "accent": "#E9A55C", "sub": "#E9A55C"})({
    "primary": lambda p: lockup_h(p, icon07, L07, ratio=1.55, space=0.25),
    "stacked": lambda p: lockup_v(p, icon07, L07, isz=190),
    "icon": lambda p: (icon07(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 08 Business Case Lab
def icon08(p, x, y, k):
    flask = "M36 10 H64 M43 10 V40 L22 80 Q19 88 28 88 H72 Q81 88 78 80 L57 40 V10"
    bars = "".join(f'<rect x="{bx}" y="{80 - h}" width="9" height="{h}" rx="2.5" fill="{p["accent"]}"/>'
                   for bx, h in [(33, 10), (45.5, 18), (58, 26)])
    return g(x, y, k,
             f'<path d="{flask}" fill="none" stroke="{p["main"]}" stroke-width="7" stroke-linecap="round" '
             f'stroke-linejoin="round"/>{bars}')


def lab_pill(p, x, cap_top, cap_h):
    """'LAB' tag, text knocked out of the pill (even-odd) so it works on any background."""
    s = cap_h * 0.62 / cap_height("Archivo.ttf", 1)
    tw = text_path("LAB", "Archivo.ttf", s, 0, 0, tracking=0.12)[1]
    ph = cap_h * 1.05
    pw = tw + ph * 0.9
    py = cap_top + (cap_h - ph) / 2
    r = ph * 0.28
    pill = (f"M{x + r} {py} H{x + pw - r} A{r} {r} 0 0 1 {x + pw} {py + r} V{py + ph - r} "
            f"A{r} {r} 0 0 1 {x + pw - r} {py + ph} H{x + r} A{r} {r} 0 0 1 {x} {py + ph - r} "
            f"V{py + r} A{r} {r} 0 0 1 {x + r} {py} Z")
    tch = cap_height("Archivo.ttf", s)
    d, _ = text_path("LAB", "Archivo.ttf", s, x + (pw - tw) / 2, py + (ph + tch) / 2, tracking=0.12)
    return f'<path d="{pill} {d}" fill="{p["accent"]}" fill-rule="evenodd"/>', pw


def lockup08(p, vertical=False):
    big = 100
    ch = cap_height("Archivo.ttf", big)
    d, w = text_path("Business Case", "Archivo.ttf", big, 0, ch)
    if vertical:
        pill, pw = lab_pill(p, 0, 0, ch)
        word = f'<path d="{d}" fill="{p["main"]}"/>'
        isz = 200
        W = max(w, isz)
        body = (icon08(p, (W - isz) / 2, 0, isz / 100)
                + f'<g transform="translate({(W - w) / 2} {isz + 50})">{word}</g>'
                + f'<g transform="translate({(W - pw) / 2} {isz + 50 + ch + 34})">{pill}</g>')
        return body, round(W), round(isz + 50 + 2 * ch + 40)
    pill, pw = lab_pill(p, w + 26, 0, ch)
    isz = ch * 2.3
    tx = isz * 1.22
    body = icon08(p, 0, 0, isz / 100) + (
        f'<g transform="translate({tx} {(isz - ch) / 2})"><path d="{d}" fill="{p["main"]}"/>{pill}</g>')
    return body, round(tx + w + 26 + pw), round(isz)


logo(8, "08_The-Business-Case-Lab",
     {"bg": "#FFFFFF", "main": "#3F2A9E", "accent": "#16B88A"},
     {"bg": "#1C1446", "main": "#FFFFFF", "accent": "#2FE0AE"})({
    "primary": lockup08,
    "stacked": lambda p: lockup08(p, True),
    "icon": lambda p: (icon08(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 09 Driving High Performance
def icon09(p, x, y, k):
    def chev(ox, col):
        return (f'<path d="M{ox} 18 L{ox + 30} 50 L{ox} 82" fill="none" stroke="{col}" stroke-width="15" '
                f'stroke-linecap="round" stroke-linejoin="round" transform="skewX(-10)"/>')
    return g(x, y, k, f'<g transform="translate(14 0)">{chev(14, p["main"])}{chev(46, p["accent"])}</g>')


def word09(p):
    s1, s2 = 64, 132
    tb = text_block(p, [dict(t="DRIVING HIGH", f="BarlowCondItMed.ttf", s=s1, c="sub", tr=0.06, dx=22),
                        dict(t="PERFORMANCE", f="BarlowCondIt.ttf", s=s2, c="main", gap=18)])
    c1 = cap_height("BarlowCondItMed.ttf", s1)
    # speed lines to the right of the first line
    sx = tb["rows"][0]["w"] + 44
    ex = tb["w"]
    lines = "".join(
        f'<path d="M{sx + i * 26:.1f} {c1 * f:.1f} H{ex - i * 0:.1f}" stroke="{p["accent"]}" '
        f'stroke-width="{c1 * 0.16:.1f}" stroke-linecap="round"/>'
        for i, f in enumerate([0.2, 0.5, 0.8]))
    return tb["body"] + lines, round(tb["w"]), round(tb["h"])


logo(9, "09_Driving-High-Performance",
     {"bg": "#FFFFFF", "main": "#111111", "accent": "#F2B705", "sub": "#111111"},
     {"bg": "#111111", "main": "#FFFFFF", "accent": "#FFD60A", "sub": "#FFFFFF"})({
    "primary": word09,
    "lockup": lambda p: (lambda b: (icon09(p, 0, 0, b[2] * 1.15 / 100) +
                                    f'<g transform="translate({b[2] * 1.3} {b[2] * 0.075})">{b[0]}</g>',
                                    round(b[2] * 1.3 + b[1]), round(b[2] * 1.15)))(word09(p)),
    "icon": lambda p: (icon09(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 10 Strategy That Delivers
def icon10(p, x, y, k):
    return g(x, y, k,
             f'<circle cx="46" cy="54" r="38" fill="none" stroke="{p["main"]}" stroke-width="7"/>'
             f'<circle cx="46" cy="54" r="21" fill="none" stroke="{p["main"]}" stroke-width="7"/>'
             f'<path d="M46 54 L86 14 M74 12 L88 12 L88 26" fill="none" stroke="{p["accent"]}" stroke-width="7" '
             f'stroke-linecap="round" stroke-linejoin="round"/>'
             f'<circle cx="46" cy="54" r="8" fill="{p["accent"]}"/>')


L10 = [dict(t="Strategy", f="Urbanist.ttf", s=120, c="main"),
       dict(t="THAT DELIVERS", f="UrbanistSemi.ttf", s=40, c="sub", tr=0.3, gap=26)]
logo(10, "10_Strategy-That-Delivers",
     {"bg": "#FFFFFF", "main": "#1B2A49", "accent": "#5DB12F", "sub": "#4A9A22"},
     {"bg": "#111C33", "main": "#FFFFFF", "accent": "#8AD95B", "sub": "#8AD95B"})({
    "primary": lambda p: lockup_h(p, icon10, L10, ratio=1.4, space=0.25),
    "stacked": lambda p: lockup_v(p, icon10, L10, isz=190),
    "icon": lambda p: (icon10(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 11 Beyond the Deal (wordmark)
def word11(p):
    big, sm = 150, 34
    tb = text_block(p, [dict(t="Beyond", f="CormorantIt.ttf", s=big, c="main"),
                        dict(t="THE DEAL", f="Montserrat.ttf", s=sm, c="sub", tr=0.6, gap=52)],
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
             f'<circle cx="50" cy="50" r="45" fill="none" stroke="{p["accent"]}" stroke-width="3"/>'
             f'<path d="{d}" fill="{p["main"]}" transform="translate({(100 - w) / 2 + 2} {50 + ch / 2})"/>')


logo(11, "11_Beyond-the-Deal",
     {"bg": "#FFFFFF", "main": "#6D1A36", "accent": "#C08B5C", "sub": "#6D1A36"},
     {"bg": "#2A0A16", "main": "#F6E7DC", "accent": "#D9A77A", "sub": "#F6E7DC"})({
    "primary": word11,
    "icon": lambda p: (icon11(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 12 Wealth Advisory Mastery
def icon12(p, x, y, k):
    d, w = text_path("W", "Playfair.ttf", 50, 0, 0)
    ch = cap_height("Playfair.ttf", 50)
    return g(x, y, k,
             f'<path d="M50 4 L96 50 L50 96 L4 50 Z" fill="none" stroke="{p["accent"]}" stroke-width="4" '
             f'stroke-linejoin="round"/>'
             f'<path d="M50 14 L86 50 L50 86 L14 50 Z" fill="none" stroke="{p["accent"]}" stroke-width="1.6" '
             f'stroke-linejoin="round"/>'
             f'<path d="{d}" fill="{p["main"]}" transform="translate({(100 - w) / 2} {50 + ch / 2})"/>')


L12 = [dict(t="Wealth Advisory", f="Playfair.ttf", s=100, c="main"),
       dict(t="MASTERY", f="Jost.ttf", s=36, c="sub", tr=0.7, gap=30)]
logo(12, "12_Wealth-Advisory-Mastery",
     {"bg": "#FFFFFF", "main": "#0A1F44", "accent": "#B8935A", "sub": "#9C7A45"},
     {"bg": "#081733", "main": "#FFFFFF", "accent": "#D6B47C", "sub": "#D6B47C"})({
    "primary": lambda p: lockup_h(p, icon12, L12, ratio=1.45, space=0.25),
    "stacked": lambda p: lockup_v(p, icon12, L12, isz=200, space=50),
    "icon": lambda p: (icon12(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 13 Seal the Deal
def icon13(p, x, y, k):
    pts = []
    for i in range(361):
        t = math.radians(i)
        r = 45 + 3.2 * math.cos(14 * t)
        pts.append(f"{50 + r * math.cos(t):.2f} {50 + r * math.sin(t):.2f}")
    seal = "M" + " L".join(pts) + "Z"

    def circ(r):
        return f"M{50 - r} 50 A{r} {r} 0 1 0 {50 + r} 50 A{r} {r} 0 1 0 {50 - r} 50Z"
    d, w = text_path("S", "Bricolage.ttf", 64, 0, 0)
    ch = cap_height("Bricolage.ttf", 64)
    d, _ = text_path("S", "Bricolage.ttf", 64, (100 - w) / 2, 50 + ch / 2)
    return g(x, y, k, f'<path d="{seal} {circ(35)} {circ(32)} {d}" fill="{p["accent"]}" fill-rule="evenodd"/>')


L13 = [dict(t="Seal the Deal", f="Bricolage.ttf", s=110, c="main")]
logo(13, "13_Seal-the-Deal",
     {"bg": "#FFFFFF", "main": "#2B2118", "accent": "#C0392B"},
     {"bg": "#1E1611", "main": "#FBF3EA", "accent": "#E0503F"})({
    "primary": lambda p: lockup_h(p, icon13, L13, ratio=1.6, space=0.22),
    "stacked": lambda p: lockup_v(p, icon13, L13, isz=210, space=46),
    "icon": lambda p: (icon13(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 14 Build the Bond
def icon14(p, x, y, k):
    # interlocking rings; gaps make the over/under readable in one colour too
    a = ring_arc(37, 50, 25, 60 + 17, 60 - 17 + 360)
    b = ring_arc(63, 50, 25, -120 + 17, -120 - 17 + 360)
    return g(x, y, k,
             f'<path d="{a}" fill="none" stroke="{p["main"]}" stroke-width="10"/>'
             f'<path d="{b}" fill="none" stroke="{p["accent"]}" stroke-width="10"/>')


L14 = [dict(t="Build the Bond", f="Nunito.ttf", s=108, c="main")]
logo(14, "14_Build-the-Bond",
     {"bg": "#FFFFFF", "main": "#1A535C", "accent": "#FF6B6B"},
     {"bg": "#0F3338", "main": "#F7FFF7", "accent": "#FF8585"})({
    "primary": lambda p: lockup_v(p, icon14, L14, isz=230, space=40),
    "horizontal": lambda p: lockup_h(p, icon14, L14, ratio=1.9, space=0.18),
    "icon": lambda p: (icon14(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 15 Contact to Contract (wordmark)
def word15(p):
    s = 104
    ch = cap_height("Lexend.ttf", s)
    d1, w1 = text_path("Contact", "Lexend.ttf", s, 0, ch)
    gap, aw = 34, 120
    ax0, ax1 = w1 + gap, w1 + gap + aw
    cy = ch * 0.55
    d2, w2 = text_path("Contract", "Lexend.ttf", s, ax1 + gap, ch)
    arrow = (f'<circle cx="{ax0 + 9}" cy="{cy}" r="9" fill="{p["accent"]}"/>'
             f'<path d="M{ax0 + 9} {cy} H{ax1 - 4} M{ax1 - 26} {cy - 22} L{ax1 - 4} {cy} L{ax1 - 26} {cy + 22}" '
             f'fill="none" stroke="{p["accent"]}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
    tsmall = 30
    return (f'<path d="{d1}" fill="{p["sub"]}"/>{arrow}<path d="{d2}" fill="{p["main"]}"/>',
            round(ax1 + gap + w2), round(ch))


def icon15(p, x, y, k):
    return g(x, y, k,
             f'<circle cx="26" cy="74" r="16" fill="none" stroke="{p["sub"]}" stroke-width="8"/>'
             f'<path d="M38 62 L60 40" stroke="{p["accent"]}" stroke-width="8" stroke-linecap="round" '
             f'stroke-dasharray="0.1 13"/>'
             f'<rect x="56" y="10" width="34" height="34" rx="8" fill="{p["main"]}"/>')


logo(15, "15_Contact-to-Contract",
     {"bg": "#FFFFFF", "main": "#2449E5", "accent": "#2449E5", "sub": "#0F172A"},
     {"bg": "#0B1224", "main": "#7C9BFF", "accent": "#7C9BFF", "sub": "#FFFFFF"})({
    "primary": word15,
    "icon": lambda p: (icon15(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 16 Learning Architect
def icon16(p, x, y, k):
    return g(x, y, k,
             f'<path d="M50 20 L24 90 M50 20 L76 90" fill="none" stroke="{p["main"]}" stroke-width="8" '
             f'stroke-linecap="round"/>'
             f'<path d="M30 70 Q50 82 70 70" fill="none" stroke="{p["accent"]}" stroke-width="7" stroke-linecap="round"/>'
             f'<circle cx="50" cy="16" r="9" fill="{p["accent"]}"/>')


L16 = [dict(t="THE LEARNING", f="Josefin.ttf", s=40, c="sub", tr=0.32),
       dict(t="ARCHITECT", f="Josefin.ttf", s=104, c="main", tr=0.08, gap=26)]
logo(16, "16_The-Learning-Architect",
     {"bg": "#FFFFFF", "main": "#2D3142", "accent": "#C8553D", "sub": "#C8553D"},
     {"bg": "#1F212E", "main": "#F4F1EC", "accent": "#E8775F", "sub": "#E8775F"})({
    "primary": lambda p: lockup_h(p, icon16, L16, ratio=1.5, space=0.2),
    "stacked": lambda p: lockup_v(p, icon16, L16, isz=190),
    "icon": lambda p: (icon16(p, 0, 0, 1), 100, 100),
})


# ------------------------------------------------------------ 17 Leader DNA
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
             f'<path d="{rungs}" stroke="{p["main"]}" stroke-width="4" stroke-linecap="round" opacity="1"/>'
             f'<path d="{strand(0)}" fill="none" stroke="{p["main"]}" stroke-width="8" stroke-linecap="round"/>'
             f'<path d="{strand(math.pi)}" fill="none" stroke="{p["accent"]}" stroke-width="8" stroke-linecap="round"/>')


L17 = [dict(t="THE LEADER", f="RedHatBold.ttf", s=40, c="main", tr=0.24),
       dict(t="DNA", f="RedHat.ttf", s=150, c="accent", gap=22, dx=-6)]
logo(17, "17_The-Leader-DNA",
     {"bg": "#FFFFFF", "main": "#23022E", "accent": "#D81E5B"},
     {"bg": "#1A0122", "main": "#FFFFFF", "accent": "#FF3D7F"})({
    "primary": lambda p: lockup_h(p, icon17, L17, ratio=1.05, space=0.22),
    "stacked": lambda p: lockup_v(p, icon17, L17, isz=180),
    "icon": lambda p: (icon17(p, 0, 0, 1), 100, 100),
})


for num, slug, light, dark, builders in LOGOS:
    if ONLY and int(ONLY) != num:
        continue
    blk, wht = mono(light)
    variants = {"color-light": light, "color-dark": dark, "black": blk, "white": wht}
    zpath, prev = export(slug, slug, builders, variants, OUT)
    preview_sheet(slug, prev, f"{OUT}/{num:02d}_preview.png")
    print(zpath)
