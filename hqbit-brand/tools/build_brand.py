#!/usr/bin/env python3
"""Build the HQbit brand kit: logo SVG/PNGs, app icon, profile pictures and brand boards.

usage: python3 tools/build_brand.py            (from hqbit-brand/)
Needs Python 3 + fontTools + brotli + Pillow, and Chromium (Playwright's headless_shell) for PNGs.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mark  # noqa: E402
import wordmark  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
BUILD = os.path.join(TOOLS, ".build")
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell")

# purple-only palette
C = {
    "void": "#0D0619",
    "night": "#160A2E",
    "plum": "#2A1250",
    "royal": "#4B2496",
    "violet": "#7C4DFF",
    "lilac": "#B9A3FF",
    "mist": "#F2EDFF",
}
NAMES = [
    ("void", "Void", "Deepest background, near black"),
    ("night", "Night", "Main background"),
    ("plum", "Plum", "Panels, cards"),
    ("royal", "Royal", "Borders, dim pixels, gradients"),
    ("violet", "Electric Violet", "The bit, glows, buttons"),
    ("lilac", "Lilac", "Highlights, links, secondary text"),
    ("mist", "Mist", "Text and the logo on dark"),
]
GRAD = f"linear-gradient(135deg,{C['royal']} 0%,{C['violet']} 55%,{C['lilac']} 100%)"


def contrast(a, b):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def w(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def render(html, png, width, height, transparent=False):
    os.makedirs(os.path.dirname(png), exist_ok=True)
    cmd = [CHROME, "--no-sandbox", "--disable-gpu", "--hide-scrollbars", f"--window-size={width},{height}",
           "--virtual-time-budget=4000", f"--screenshot={png}"]
    if transparent:
        cmd.append("--default-background-color=00000000")
    subprocess.run(cmd + ["file://" + html], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------- logo SVGs

def monogram_group(u, x0, y0, fill, bit_fill):
    d = "".join(f"M{x0+x*u:.2f} {y0+y*u:.2f}h{ww*u:.2f}v{hh*u:.2f}h{-ww*u:.2f}z" for x, y, ww, hh in mark.LETTERS)
    bx, by, bw, bh = mark.BIT
    return (f'<path d="{d}" fill="{fill}"/>'
            f'<rect x="{x0+bx*u:.2f}" y="{y0+by*u:.2f}" width="{bw*u:.2f}" height="{bh*u:.2f}" fill="{bit_fill}"/>')


def lockup(kind, letters, bit, word_hq, word_bit, pad_units=0):
    """kind: horizontal | stacked. Clear space = the bit's size (4 grid units) on every side by default."""
    size = 100
    frag, ww, asc, desc, cap = wordmark.text_paths([("HQ", word_hq), ("bit", word_bit)], size)
    u = cap * 1.25 / 10                 # monogram letters are 10 units tall = 1.25 x cap height
    pad = pad_units * u
    if kind == "horizontal":
        gap = 3 * u
        mw = mark.GRID_W * u
        W = pad * 2 + mw + gap + ww
        H = pad * 2 + max(mark.GRID_H * u, 10 * u + 0.24 * size)   # room for the Q's tail
        base = pad + 10 * u              # wordmark baseline on the letters' bottom
        tx, ty = pad + mw + gap, base - asc
    else:
        mw = mark.GRID_W * u
        gap = 3 * u
        W = pad * 2 + max(mw, ww)
        H = pad * 2 + mark.GRID_H * u + gap + cap + 0.24 * size
        tx, ty = pad + (W - 2 * pad - ww) / 2, pad + mark.GRID_H * u + gap + cap - asc
    mx = pad if kind == "horizontal" else pad + (W - 2 * pad - mw) / 2
    g = monogram_group(u, mx, pad, letters, bit)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}">'
            f'<title>HQbit</title>{g}<g transform="translate({tx:.2f} {ty:.2f})">{frag}</g></svg>')


def symbol(letters, bit, pad_units=0):
    return mark.svg(letters, bit_fill=bit, u=50, pad=pad_units * 50)


def app_icon_svg(size=1024):
    """Flat app icon (rounded tile + gradient + monogram): crisp at any size, used for favicons."""
    u = size * 0.052
    mw, mh = mark.GRID_W * u, mark.GRID_H * u
    x0, y0 = (size - mw) / 2 + u * 0.6, (size - mh) / 2 + u * 0.6
    r = size * 0.22
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{C["violet"]}"/><stop offset=".55" stop-color="{C["royal"]}"/>'
            f'<stop offset="1" stop-color="{C["plum"]}"/></linearGradient>'
            f'<linearGradient id="h" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
            f'<rect width="{size}" height="{size}" rx="{r}" fill="url(#g)"/>'
            f'<rect width="{size}" height="{size}" rx="{r}" fill="url(#h)"/>'
            f'{monogram_group(u, x0, y0, C["mist"], C["lilac"])}</svg>')


def build_logos():
    L = os.path.join(ROOT, "logo")
    v = {
        "dark": (C["mist"], C["violet"], C["mist"], C["lilac"]),       # for dark backgrounds
        "light": (C["night"], C["violet"], C["night"], C["violet"]),   # for light backgrounds
        "white": ("#FFFFFF",) * 4,
        "night": (C["night"],) * 4,
    }
    for name, (a, b, c, d) in v.items():
        w(f"{L}/hqbit-logo-horizontal-{name}.svg", lockup("horizontal", a, b, c, d))
        w(f"{L}/hqbit-logo-stacked-{name}.svg", lockup("stacked", a, b, c, d))
        w(f"{L}/hqbit-symbol-{name}.svg", symbol(a, b))
    for name, col in (("lilac", C["lilac"]), ("mist", C["mist"]), ("violet", C["violet"]), ("night", C["night"]),
                      ("white", "#FFFFFF")):
        w(f"{L}/hq-personal-logo-{name}.svg", mark.svg(col))
    w(f"{L}/hqbit-app-icon.svg", app_icon_svg())
    # PNG exports
    pngs = [
        ("hqbit-logo-horizontal-dark", 2400), ("hqbit-logo-horizontal-light", 2400),
        ("hqbit-logo-stacked-dark", 1600), ("hqbit-logo-stacked-light", 1600),
        ("hqbit-symbol-dark", 1024), ("hqbit-symbol-light", 1024),
        ("hq-personal-logo-lilac", 1024), ("hq-personal-logo-mist", 1024), ("hq-personal-logo-night", 1024),
    ]
    for name, width in pngs:
        svg = open(f"{L}/{name}.svg").read()
        vb = [float(x) for x in svg.split('viewBox="')[1].split('"')[0].split()]
        height = round(width * vb[3] / vb[2])
        html = f"{BUILD}/{name}.html"
        w(html, f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={width} height={height} ", 1)}</body></html>')
        render(html, f"{L}/png/{name}.png", width, height, transparent=True)
    svg = app_icon_svg()
    for s in (1024, 512, 192, 32):
        html = f"{BUILD}/icon{s}.html"
        w(html, f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={s} height={s} ", 1)}</body></html>')
        render(html, f"{L}/png/hqbit-app-icon-{s}.png", s, s, transparent=True)


# ---------------------------------------------------------------- HTML helpers

def fonts_css():
    f = "file://" + os.path.join(TOOLS, "fonts")
    return f"""
@font-face{{font-family:SG;src:url({f}/SpaceGrotesk-Variable.woff2);font-weight:300 700}}
@font-face{{font-family:IN;src:url({f}/Inter-Variable.woff2);font-weight:100 900}}
@font-face{{font-family:PX;src:url({f}/Silkscreen-Regular.ttf)}}
@font-face{{font-family:PX;src:url({f}/Silkscreen-Bold.ttf);font-weight:700}}
@font-face{{font-family:JB;src:url({f}/JetBrainsMono-Medium.ttf);font-weight:500}}
@font-face{{font-family:JB;src:url({f}/JetBrainsMono-Bold.ttf);font-weight:700}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{C['void']};color:{C['mist']};font-family:IN;overflow:hidden;position:relative}}
.grid{{position:absolute;inset:0;background-image:linear-gradient({C['plum']}66 1px,transparent 1px),linear-gradient(90deg,{C['plum']}66 1px,transparent 1px);background-size:48px 48px;
 -webkit-mask-image:radial-gradient(circle at 50% 45%,#000 0%,transparent 75%)}}
.eyebrow{{font-family:JB;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:{C['lilac']}}}
.h1{{font-family:SG;font-weight:700;letter-spacing:-.03em}}
.foot{{position:absolute;left:72px;right:72px;bottom:40px;display:flex;justify-content:space-between;font-family:JB;font-size:15px;color:{C['lilac']}99}}
"""


def keycap(size, bit_color=None, personal=False):
    """Glossy 3D keycap with the monogram (art direction: glass/keycap app icons)."""
    u = size * 0.042
    bit = C["mist"] if personal else (bit_color or C["night"])
    m = mark.svg(C["mist"], bit_fill=bit)
    r = size * 0.24
    return f"""<div style="position:relative;width:{size}px;height:{size}px">
<div style="position:absolute;inset:{size*.06}px 0 -{size*.04}px;border-radius:{r}px;background:{C['plum']};filter:blur(0);
 box-shadow:0 {size*.07}px {size*.16}px {C['violet']}88"></div>
<div style="position:absolute;inset:0;border-radius:{r}px;background:linear-gradient(165deg,#A98EFF 0%,{C['violet']} 38%,{C['royal']} 100%);
 box-shadow:inset 0 {size*.012}px 0 #ffffff70,inset 0 -{size*.05}px {size*.08}px #1a083f88"></div>
<div style="position:absolute;inset:{size*.075}px {size*.075}px {size*.115}px;border-radius:{r*.78}px;
 background:linear-gradient(172deg,#9C7BFF 0%,#7446F4 55%,#5F31DE 100%);
 box-shadow:inset 0 {size*.006}px 0 #ffffff80,inset 0 -{size*.02}px {size*.05}px #2a0f7055"></div>
<div style="position:absolute;inset:{size*.075}px {size*.075}px {size*.115}px;border-radius:{r*.78}px;
 background:radial-gradient(120% 70% at 30% 0%,#ffffff40,transparent 55%)"></div>
<div style="position:absolute;left:50%;top:46%;width:{mark.GRID_W*u}px;transform:translate(-46%,-50%);
 filter:drop-shadow(0 {size*.012}px 0 #2a0f70aa) drop-shadow(0 {size*.03}px {size*.04}px #1a083f66)">{m}</div>
</div>"""


def page(body, width, height, extra_css=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css()}{extra_css}</style></head><body style="width:{width}px;height:{height}px">{body}</body></html>'


def logo_inline(name, height=None, width=None):
    svg = open(os.path.join(ROOT, "logo", name + ".svg")).read()
    attr = (f'height="{height}" ' if height else "") + (f'width="{width}" ' if width else "")
    return svg.replace("<svg ", f"<svg {attr}style='display:block' ", 1)


def foot(page_no):
    return f'<div class="foot"><span>HQbit · Brand guide</span><span>Pixel · Digital · AI · UI</span><span>{page_no:02d}</span></div>'


# ---------------------------------------------------------------- profile pictures

def build_profiles():
    P = os.path.join(ROOT, "profile")
    for name, personal in (("hqbit-profile-picture", False), ("hq-personal-profile-picture", True)):
        body = f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 42%,{C['royal']} 0%,{C['night']} 45%,{C['void']} 80%)"></div>
<div class="grid" style="background-size:64px 64px"></div>
<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-53%)">{keycap(660, personal=personal)}</div>"""
        html = f"{BUILD}/{name}.html"
        w(html, page(body, 1024, 1024))
        render(html, f"{P}/{name}-1024.png", 1024, 1024)
    # circle preview (how Reddit/IG crop it)
    body = f"""<div style="display:flex;gap:60px;align-items:center;justify-content:center;height:100%;background:{C['night']}">
<img src="file://{P}/hqbit-profile-picture-1024.png" style="width:360px;border-radius:50%">
<img src="file://{P}/hqbit-profile-picture-1024.png" style="width:120px;border-radius:50%">
<img src="file://{P}/hqbit-profile-picture-1024.png" style="width:48px;border-radius:50%">
<img src="file://{P}/hq-personal-profile-picture-1024.png" style="width:360px;border-radius:50%"></div>"""
    html = f"{BUILD}/profile-preview.html"
    w(html, page(body, 1200, 520))
    render(html, f"{P}/profile-picture-preview.png", 1200, 520)


# ---------------------------------------------------------------- pixel elements

SPARKLE = ["...X...", "...X...", "..XXX..", "XXXXXXX", "..XXX..", "...X...", "...X..."]
ARROW = ["..X..", "...X.", "XXXXX", "...X.", "..X.."]
HEART = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
CURSOR = ["X....", "XX...", "XXX..", "XXXX.", "XXXXX", "XX...", "X.X.."]
PAD = ["..XXX..", "..X.X..", "XXX.XXX", "X.....X", "XXX.XXX", "..X.X..", "..XXX.."]
PAD_SOLID = ["..XXX..", "..XXX..", "XXXXXXX", "XXXXXXX", "XXXXXXX", "..XXX..", "..XXX.."]


def pix(rows, u, fill):
    h, wd = len(rows), len(rows[0])
    rects = "".join(f'<rect x="{x*u}" y="{y*u}" width="{u}" height="{u}"/>' for y, r in enumerate(rows)
                    for x, ch in enumerate(r) if ch == "X")
    return f'<svg width="{wd*u}" height="{h*u}" viewBox="0 0 {wd*u} {h*u}" fill="{fill}" shape-rendering="crispEdges">{rects}</svg>'


# ---------------------------------------------------------------- boards

W_, H_ = 1920, 1200


def board_cover():
    body = f"""<div style="position:absolute;inset:0;background:radial-gradient(70% 80% at 30% 50%,{C['royal']}cc 0%,{C['night']} 45%,{C['void']} 80%)"></div>
<div class="grid"></div>
<div style="position:absolute;left:150px;top:50%;transform:translateY(-52%)">{keycap(620)}</div>
<div style="position:absolute;left:930px;top:340px">
 <div class="eyebrow">Brand identity · 2026</div>
 <div style="margin-top:40px">{logo_inline('hqbit-logo-horizontal-dark', height=210)}</div>
 <div style="font-family:SG;font-size:40px;font-weight:500;margin-top:44px;color:{C['mist']};letter-spacing:-.01em">Pixel art, digital art and AI-made UI<br>for retro handhelds.</div>
 <div style="display:flex;gap:14px;margin-top:40px">{''.join(f'<span style="font-family:PX;font-size:20px;color:{C["lilac"]};border:2px solid {C["royal"]};padding:10px 16px;border-radius:12px">{t}</span>' for t in ('PIXEL','DIGITAL','AI','UI','R36S'))}</div>
</div>
<div style="position:absolute;right:90px;top:80px">{pix(SPARKLE, 10, C['lilac'])}</div>
<div style="position:absolute;right:220px;top:200px;opacity:.6">{pix(SPARKLE, 6, C['violet'])}</div>
<div style="position:absolute;left:110px;top:90px;opacity:.8">{pix(SPARKLE, 7, C['violet'])}</div>
{foot(1)}"""
    return body


def board_logo_system():
    def panel(inner, bg, label, span=1, light=False):
        col = C["night"] if light else C["lilac"]
        return (f'<div style="grid-column:span {span};background:{bg};border:1px solid {C["royal"]}66;border-radius:28px;'
                f'position:relative;display:flex;align-items:center;justify-content:center">{inner}'
                f'<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{col}">{label}</div></div>')
    # clear space diagram
    u = 14
    sym = mark.svg(C["mist"], bit_fill=C["violet"], u=u)
    cw, ch = mark.GRID_W * u, mark.GRID_H * u
    q = 4 * u
    cs = f"""<div style="position:relative;width:{cw+2*q}px;height:{ch+2*q}px;outline:2px dashed {C['lilac']}88">
<div style="position:absolute;left:{q}px;top:{q}px;width:{cw}px;height:{ch}px;outline:1px solid {C['lilac']}55">{sym.replace('<svg ', '<svg style="display:block" ', 1)}</div>
<div style="position:absolute;left:0;top:{q+ (ch-q)/2}px;width:{q}px;height:{q}px;background:{C['violet']}55"></div>
<div style="position:absolute;left:{q+(cw-q)/2}px;top:0;width:{q}px;height:{q}px;background:{C['violet']}55"></div>
<div style="position:absolute;right:0;top:{q+(ch-q)/2}px;width:{q}px;height:{q}px;background:{C['violet']}55"></div>
<div style="position:absolute;left:{q+(cw-q)/2}px;bottom:0;width:{q}px;height:{q}px;background:{C['violet']}55"></div></div>"""
    sizes = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:14px"><div style="width:{s}px">{mark.svg(C["mist"], bit_fill=C["violet"])}</div><span style="font-family:JB;font-size:14px;color:{C["lilac"]}">{s}px</span></div>' for s in (128, 64, 32, 16))
    body = f"""<div class="grid" style="opacity:.5"></div>
<div style="position:absolute;left:72px;top:64px"><div class="eyebrow">01 · Logo system</div>
<div class="h1" style="font-size:64px;margin-top:12px">One mark, every size.</div>
<div style="font-size:22px;color:{C['lilac']};margin-top:12px;max-width:1100px;line-height:1.45">An H and a square Q share one stem on a pixel grid. The Q's tail is a single square: the <b style="color:{C['mist']}">bit</b>. Take the bit's colour away and the mark becomes the personal HQ logo.</div></div>
<div style="position:absolute;left:72px;right:72px;top:330px;bottom:110px;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:1fr 1fr;gap:24px">
{panel(logo_inline('hqbit-logo-horizontal-dark', width=640), C['night'], 'Primary · horizontal', 2)}
{panel(logo_inline('hqbit-logo-horizontal-light', width=640), C['mist'], 'On light backgrounds', 2, True)}
{panel(logo_inline('hqbit-logo-stacked-dark', width=230), C['plum'], 'Stacked')}
{panel(f'<div style="width:220px">{mark.svg(C["mist"])}</div>', C['night'], 'HQ · personal logo')}
{panel(cs, C['night'], 'Clear space = 1 bit on every side')}
{panel(f'<div style="display:flex;gap:28px;align-items:flex-end">{sizes}</div>', C['night'], 'Stays sharp down to 16px')}
</div>{foot(2)}"""
    return body


def board_color():
    sw = ""
    for key, name, use in NAMES:
        hexv = C[key]
        dark_text = key in ("lilac", "mist")
        tc = C["night"] if dark_text else C["mist"]
        sw += f"""<div style="flex:1;background:{hexv};border-radius:26px;padding:28px;display:flex;flex-direction:column;justify-content:flex-end;color:{tc};
border:1px solid {C['royal']}88"><div style="font-family:SG;font-weight:700;font-size:30px">{name}</div>
<div style="font-family:JB;font-size:20px;margin-top:6px">{hexv.upper()}</div><div style="font-size:16px;margin-top:10px;opacity:.85;line-height:1.35">{use}</div></div>"""
    body = f"""<div class="grid" style="opacity:.5"></div>
<div style="position:absolute;left:72px;top:64px"><div class="eyebrow">02 · Colour</div>
<div class="h1" style="font-size:64px;margin-top:12px">All purple. No accent.</div>
<div style="font-size:22px;color:{C['lilac']};margin-top:12px;max-width:1150px;line-height:1.45">Seven steps from near-black to near-white. Contrast comes from lightness, not from a second hue: Mist and Lilac on Night read clearly at every size on the R36S's 640×480 screen.</div></div>
<div style="position:absolute;left:72px;right:72px;top:330px;height:470px;display:flex;gap:18px">{sw}</div>
<div style="position:absolute;left:72px;right:72px;top:830px;height:200px;display:grid;grid-template-columns:2fr 1fr 1fr;gap:18px">
<div style="border-radius:26px;background:{GRAD};padding:28px;display:flex;align-items:flex-end;font-family:JB;font-size:18px;color:{C['mist']}">Signature gradient · Royal → Electric Violet → Lilac</div>
<div style="border-radius:26px;background:radial-gradient(circle at 50% 30%,{C['royal']},{C['void']} 75%);padding:28px;display:flex;align-items:flex-end;font-family:JB;font-size:18px">Glow · backgrounds</div>
<div style="border-radius:26px;background:{C['night']};border:1px solid {C['royal']};padding:28px;display:flex;flex-direction:column;justify-content:flex-end;font-family:JB;font-size:16px;color:{C['lilac']};gap:6px">
<span><b style="color:{C['mist']}">Mist on Night</b> · {contrast(C['mist'], C['night']):.1f}:1</span><span><b style="color:{C['lilac']}">Lilac on Night</b> · {contrast(C['lilac'], C['night']):.1f}:1</span><span><b style="color:{C['violet']}">Violet on Night</b> · {contrast(C['violet'], C['night']):.1f}:1 (large text + graphics)</span></div>
</div>{foot(3)}"""
    return body


def board_type():
    def spec(fam, name, role, sample, style, size):
        return f"""<div style="background:{C['night']};border:1px solid {C['royal']}66;border-radius:28px;padding:40px;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;justify-content:space-between;font-family:JB;font-size:16px;color:{C['lilac']}"><span>{role}</span><span>{name} · free (SIL OFL)</span></div>
<div style="font-family:{fam};font-size:{size}px;line-height:1.05;{style}">{sample}</div>
<div style="font-family:{fam};font-size:22px;color:{C['lilac']};{style}">ABCDEFGHIJKLM abcdefghijklm 0123456789</div></div>"""
    body = f"""<div class="grid" style="opacity:.5"></div>
<div style="position:absolute;left:72px;top:64px"><div class="eyebrow">03 · Typography</div>
<div class="h1" style="font-size:64px;margin-top:12px">Modern type, pixel accents.</div></div>
<div style="position:absolute;left:72px;right:72px;top:230px;bottom:110px;display:grid;grid-template-columns:1.3fr 1fr;grid-template-rows:1fr 1fr;gap:24px">
{spec('SG', 'Space Grotesk', 'Headlines + wordmark', 'Themes for<br>tiny screens.', 'font-weight:700;letter-spacing:-.03em', 92)}
{spec('IN', 'Inter', 'Body + UI text', 'Unzip, copy the folder into <i>themes</i>, then pick it under UI Settings.', 'font-weight:400', 40)}
{spec('PX', 'Silkscreen', 'Pixel accents, labels', 'PRESS START', 'font-weight:700', 84)}
{spec('JB', 'JetBrains Mono', 'Tech details, versions, file names', 'es-theme-volta-v1.1.zip', 'font-weight:500', 40)}
</div>{foot(4)}"""
    return body


def board_elements():
    def tile(inner, label):
        return (f'<div style="background:{C["night"]};border:1px solid {C["royal"]}66;border-radius:28px;position:relative;'
                f'display:flex;align-items:center;justify-content:center;gap:30px">{inner}'
                f'<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C["lilac"]}">{label}</div></div>')
    icons = "".join(pix(p, 12, C["lilac"]) for p in (SPARKLE, ARROW, HEART, CURSOR, PAD))
    btn = (f'<div style="display:flex;flex-direction:column;gap:18px">'
           f'<div style="font-family:SG;font-weight:700;font-size:26px;background:{C["lilac"]};color:{C["night"]};padding:18px 34px;border-radius:16px;box-shadow:0 6px 0 {C["royal"]}">Download theme</div>'
           f'<div style="font-family:SG;font-weight:600;font-size:26px;border:2px solid {C["lilac"]};color:{C["lilac"]};padding:16px 32px;border-radius:16px">View showcase</div></div>')
    tags = "".join(f'<span style="font-family:JB;font-size:18px;color:{C["lilac"]};background:{C["plum"]};border:1px solid {C["royal"]};padding:8px 14px;border-radius:999px">{t}</span>' for t in ("v1.2", "194 systems", "640×480", "ArkOS"))
    bullets = "".join(f'<div style="display:flex;gap:14px;align-items:center;font-size:22px"><span style="width:14px;height:14px;background:{C["violet"]};display:inline-block"></span>{t}</div>' for t in ("13 colour schemes", "Pixel-perfect icons", "Tested on device"))
    pattern = f'<div style="width:100%;height:100%;border-radius:28px;background-color:{C["night"]};background-image:radial-gradient({C["royal"]} 2px,transparent 2.5px);background-size:24px 24px;-webkit-mask-image:linear-gradient(135deg,#000,transparent 85%)"></div>'
    stair = "".join(f'<div style="position:absolute;left:{40+i*44}px;bottom:{50+i*44}px;width:44px;height:44px;background:{C["violet"]};opacity:{1-i*0.14}"></div>' for i in range(6))
    body = f"""<div class="grid" style="opacity:.5"></div>
<div style="position:absolute;left:72px;top:64px"><div class="eyebrow">04 · Brand elements</div>
<div class="h1" style="font-size:64px;margin-top:12px">Built from bits.</div></div>
<div style="position:absolute;left:72px;right:72px;top:230px;bottom:110px;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:24px">
{tile(keycap(250), 'Keycap icon · hero + profile')}
{tile(icons, 'Pixel icon set · 7×7 grid')}
{tile(btn, 'Buttons')}
{tile(f'<div style="display:flex;flex-direction:column;gap:22px"><div style="display:flex;gap:10px;flex-wrap:wrap;max-width:420px">{tags}</div>{bullets}</div>', 'Tags + bit bullets')}
<div style="position:relative">{pattern}<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center"><div style="width:200px;opacity:.95">{mark.svg(C['mist'], bit_fill=C['violet'])}</div></div><div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C['lilac']}">Dot-grid pattern</div></div>
<div style="background:{C['night']};border:1px solid {C['royal']}66;border-radius:28px;position:relative;overflow:hidden">{stair}
<div style="position:absolute;right:36px;top:40px;font-family:PX;font-weight:700;font-size:44px;text-align:right;line-height:1.1;color:{C['mist']}">LEVEL<br>UP</div>
<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C['lilac']}">Bit stairs · motion + dividers</div></div>
</div>{foot(5)}"""
    return body


def board_applications():
    prof = f"file://{ROOT}/profile/hqbit-profile-picture-1024.png"
    reddit = f"""<div style="background:{C['night']};border:1px solid {C['royal']}66;border-radius:28px;overflow:hidden;position:relative">
<div style="height:200px;background:radial-gradient(60% 140% at 70% 50%,{C['royal']},{C['night']} 70%);position:relative;overflow:hidden">
<div class="grid" style="background-size:32px 32px"></div>
<div style="position:absolute;right:60px;top:50%;transform:translateY(-50%)">{logo_inline('hqbit-logo-horizontal-dark', height=90)}</div>
<div style="position:absolute;left:300px;top:40px;opacity:.7">{pix(SPARKLE, 8, C['lilac'])}</div></div>
<img src="{prof}" style="position:absolute;left:48px;top:140px;width:150px;border-radius:50%;border:6px solid {C['night']}">
<div style="padding:24px 48px 0 220px"><div style="font-family:SG;font-weight:700;font-size:34px">r/HQbit</div>
<div style="font-size:19px;color:{C['lilac']};margin-top:4px">EmulationStation themes, pixel icon packs and UI for the R36S</div></div>
<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C['lilac']}">Reddit · banner + avatar</div></div>"""
    insta = f"""<div style="background:{C['night']};border:1px solid {C['royal']}66;border-radius:28px;position:relative;display:flex;align-items:center;justify-content:center;padding-bottom:30px">
<div style="width:310px;height:310px;border-radius:18px;overflow:hidden;position:relative;background:radial-gradient(circle at 50% 35%,{C['royal']},{C['void']} 80%)">
<div class="grid" style="background-size:24px 24px"></div>
<div style="position:absolute;left:30px;top:28px;font-family:PX;font-size:16px;color:{C['lilac']}">NEW THEME DROP</div>
<div style="position:absolute;left:30px;top:66px;font-family:SG;font-weight:700;font-size:46px;line-height:.95;letter-spacing:-.03em">NeonGlow<br><span style="color:{C['lilac']}">v1.2</span></div>
<div style="position:absolute;right:26px;bottom:26px">{keycap(96)}</div>
<div style="position:absolute;left:30px;bottom:30px;font-family:JB;font-size:15px;color:{C['lilac']}">194 systems · free</div></div>
<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C['lilac']}">Instagram · post template</div></div>"""
    boot = f"""<div style="background:{C['night']};border:1px solid {C['royal']}66;border-radius:28px;position:relative;display:flex;align-items:center;justify-content:center;padding-bottom:30px">
<div style="background:#E9E6EF;border-radius:28px 28px 70px 28px;padding:18px 18px 84px;box-shadow:0 20px 50px #0008;position:relative">
<div style="width:300px;height:225px;border:8px solid #15121b;border-radius:6px;background:radial-gradient(circle at 50% 45%,{C['plum']},{C['void']} 80%);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px">
<div style="width:84px">{mark.svg(C['mist'], bit_fill=C['violet'])}</div>
<div style="width:150px;height:10px;background:{C['plum']};border:1px solid {C['royal']}"><div style="width:62%;height:100%;background:{C['lilac']}"></div></div>
<div style="font-family:PX;font-size:13px;color:{C['lilac']}">LOADING…</div></div>
<div style="position:absolute;left:30px;bottom:14px">{pix(PAD_SOLID, 9, '#2a2730')}</div>
<div style="position:absolute;right:34px;bottom:26px;display:flex;gap:10px"><i style="width:26px;height:26px;border-radius:50%;background:#2a2730;display:block"></i><i style="width:26px;height:26px;border-radius:50%;background:{C['violet']};display:block"></i></div></div>
<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C['lilac']}">R36S · boot / loading screen</div></div>"""
    web = f"""<div style="background:{C['night']};border:1px solid {C['royal']}66;border-radius:28px;position:relative;overflow:hidden;padding:30px">
<div style="border-radius:16px;border:1px solid {C['royal']};overflow:hidden;height:calc(100% - 40px);background:{C['void']}">
<div style="height:36px;background:{C['plum']};display:flex;align-items:center;gap:8px;padding:0 14px">{''.join(f'<i style="width:11px;height:11px;border-radius:50%;background:{C["royal"]};display:block"></i>' for _ in range(3))}
<span style="margin-left:14px;font-family:JB;font-size:13px;color:{C['lilac']}">hqbit · themes for the R36S</span></div>
<div style="padding:26px 30px;display:flex;justify-content:space-between;align-items:center">{logo_inline('hqbit-logo-horizontal-dark', height=40)}
<span style="font-family:IN;font-size:15px;color:{C['lilac']}">Themes · Icons · Downloads</span></div>
<div style="padding:16px 30px"><div style="font-family:SG;font-weight:700;font-size:48px;letter-spacing:-.03em;line-height:1">Themes built<br>from bits.</div>
<div style="display:flex;gap:12px;margin-top:22px"><span style="font-family:SG;font-weight:700;font-size:17px;background:{C['lilac']};color:{C['night']};padding:12px 20px;border-radius:12px">Download all</span>
<span style="font-family:SG;font-weight:600;font-size:17px;border:2px solid {C['lilac']};color:{C['lilac']};padding:10px 18px;border-radius:12px">See showcase</span></div></div></div>
<div style="position:absolute;left:28px;bottom:14px;font-family:JB;font-size:15px;color:{C['lilac']}">Website · landing hero</div></div>"""
    body = f"""<div class="grid" style="opacity:.5"></div>
<div style="position:absolute;left:72px;top:64px"><div class="eyebrow">05 · Applications</div>
<div class="h1" style="font-size:64px;margin-top:12px">Out in the wild.</div></div>
<div style="position:absolute;left:72px;right:72px;top:230px;bottom:110px;display:grid;grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:24px">
{reddit}{insta}{web}{boot}</div>{foot(6)}"""
    return body


def build_boards():
    B = os.path.join(ROOT, "boards")
    for i, (name, fn) in enumerate((("cover", board_cover), ("logo-system", board_logo_system), ("color", board_color),
                                    ("typography", board_type), ("elements", board_elements),
                                    ("applications", board_applications)), 1):
        html = f"{BUILD}/board-{name}.html"
        w(html, page(fn(), W_, H_))
        render(html, f"{B}/{i:02d}-hqbit-{name}.png", W_, H_)


if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    build_logos()
    build_profiles()
    build_boards()
    print("done")
