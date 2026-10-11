#!/usr/bin/env python3
"""Build the HQbit brand kit around the official logo (logo/official/hqbit-logo-original.svg):
logo variants (SVG + PNG), app icon, profile pictures and brand boards.

usage: python3 tools/build_brand.py            (from hqbit-brand/)
Needs Python 3 + Pillow, and Chromium (Playwright's headless_shell) for PNGs.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import official_logo as OL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
BUILD = os.path.join(TOOLS, ".build")
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell")

C = {
    "void": "#0D0619",
    "night": "#160A2E",
    "plum": "#2A1250",
    "royal": "#4120B0",
    "purple": OL.PURPLE,      # HQ Purple, from the logo
    "lilac": "#B9A3FF",
    "mist": "#F2EDFF",
    "white": "#FFFFFF",
    "lime": OL.LIME,          # the bit, from the logo
}
NAMES = [
    ("void", "Void", "Deepest background"),
    ("night", "Night", "Dark background"),
    ("plum", "Plum", "Panels and cards on dark"),
    ("purple", "HQ Purple", "Primary brand colour"),
    ("lilac", "Lilac", "Secondary text, links on dark"),
    ("white", "White", "Logo and text on purple"),
    ("lime", "Bit Lime", "The bit only: one small highlight"),
]


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


def svg_png(svg, png, width, transparent=True):
    vb = [float(x) for x in svg.split('viewBox="')[1].split('"')[0].split()]
    height = round(width * vb[3] / vb[2])
    html = f"{BUILD}/{os.path.basename(png)}.html"
    w(html, f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={width} height={height} ", 1)}</body></html>')
    render(html, png, width, height, transparent)


# ---------------------------------------------------------------- logos

def build_logos():
    L = os.path.join(ROOT, "logo")
    for name, (layout, fill, chip, bg) in OL.VARIANTS.items():
        s = OL.svg(layout, fill, chip, bg)
        w(f"{L}/{name}.svg", s)
        svg_png(s, f"{L}/png/{name}.png", 2400 if layout == "horizontal" else 1200, transparent=bg is None)
    icon = app_icon_svg()
    w(f"{L}/hqbit-app-icon.svg", icon)
    for size in (1024, 512, 192, 32):
        svg_png(icon, f"{L}/png/hqbit-app-icon-{size}.png", size)


def app_icon_svg(size=1024):
    inner = OL.svg("stacked", C["white"], C["lime"], None, pad=0)
    vb = inner.split('viewBox="')[1].split('"')[0]
    iw = size * 0.62
    vbw, vbh = [float(x) for x in vb.split()][2:]
    ih = iw * vbh / vbw
    body = inner.split(">", 1)[1].rsplit("</svg>", 1)[0]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
            f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7A4BFF"/>'
            f'<stop offset="1" stop-color="{C["purple"]}"/></linearGradient></defs>'
            f'<rect width="{size}" height="{size}" rx="{size*0.22}" fill="url(#g)"/>'
            f'<svg x="{(size-iw)/2}" y="{(size-ih)/2}" width="{iw}" height="{ih}" viewBox="{vb}">{body}</svg></svg>')


# ---------------------------------------------------------------- HTML helpers

def fonts_css():
    f = "file://" + os.path.join(TOOLS, "fonts")
    return f"""
@font-face{{font-family:UB;src:url({f}/Unbounded-400.ttf);font-weight:400}}
@font-face{{font-family:UB;src:url({f}/Unbounded-600.ttf);font-weight:600}}
@font-face{{font-family:UB;src:url({f}/Unbounded-800.ttf);font-weight:800}}
@font-face{{font-family:IN;src:url({f}/Inter-Variable.woff2);font-weight:100 900}}
@font-face{{font-family:PX;src:url({f}/Silkscreen-Regular.ttf)}}
@font-face{{font-family:PX;src:url({f}/Silkscreen-Bold.ttf);font-weight:700}}
@font-face{{font-family:JB;src:url({f}/JetBrainsMono-Medium.ttf);font-weight:500}}
@font-face{{font-family:JB;src:url({f}/JetBrainsMono-Bold.ttf);font-weight:700}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{C['void']};color:{C['white']};font-family:IN;overflow:hidden;position:relative}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(#ffffff0d 1px,transparent 1px),linear-gradient(90deg,#ffffff0d 1px,transparent 1px);background-size:48px 48px;
 -webkit-mask-image:radial-gradient(circle at 50% 45%,#000 0%,transparent 75%)}}
.eyebrow{{font-family:JB;font-size:18px;letter-spacing:.16em;text-transform:uppercase;color:{C['lilac']}}}
.h1{{font-family:UB;font-weight:600;letter-spacing:-.02em}}
.foot{{position:absolute;left:72px;right:72px;bottom:40px;display:flex;justify-content:space-between;font-family:JB;font-size:15px;color:{C['lilac']}99}}
.chip{{display:inline-block;width:.9em;height:.42em;border-radius:.06em .2em .2em .06em;background:{C['lime']};vertical-align:.12em}}
"""


def logo(layout="horizontal", fill=None, chip=None, bg=None, width=None, height=None, pad=0):
    s = OL.svg(layout, fill or C["white"], chip or C["lime"], bg, pad=pad)
    attr = (f'width="{width}" ' if width else "") + (f'height="{height}" ' if height else "")
    return s.replace("<svg ", f"<svg {attr}style='display:block' ", 1)


def keycap(size, layout="stacked"):
    """Glossy 3D keycap in HQ Purple with the logo on top (art direction: glass/keycap icons)."""
    r = size * 0.24
    lw = size * 0.56
    return f"""<div style="position:relative;width:{size}px;height:{size}px">
<div style="position:absolute;inset:{size*.06}px 0 -{size*.045}px;border-radius:{r}px;background:#2B0E8F;
 box-shadow:0 {size*.07}px {size*.16}px {C['purple']}99"></div>
<div style="position:absolute;inset:0;border-radius:{r}px;background:linear-gradient(165deg,#9A78FF 0%,{C['purple']} 40%,#4116C9 100%);
 box-shadow:inset 0 {size*.012}px 0 #ffffff80,inset 0 -{size*.05}px {size*.08}px #1a083f88"></div>
<div style="position:absolute;inset:{size*.075}px {size*.075}px {size*.115}px;border-radius:{r*.78}px;
 background:linear-gradient(172deg,#8D66FF 0%,#6A36FF 50%,#5521F2 100%);
 box-shadow:inset 0 {size*.006}px 0 #ffffff90,inset 0 -{size*.02}px {size*.05}px #2a0f7055"></div>
<div style="position:absolute;inset:{size*.075}px {size*.075}px {size*.115}px;border-radius:{r*.78}px;
 background:radial-gradient(120% 70% at 30% 0%,#ffffff45,transparent 55%)"></div>
<div style="position:absolute;left:50%;top:45%;transform:translate(-50%,-50%);
 filter:drop-shadow(0 {size*.012}px 0 #2a0f70bb) drop-shadow(0 {size*.03}px {size*.04}px #1a083f66)">{logo(layout, width=lw)}</div>
</div>"""


def page(body, width, height):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css()}</style></head>'
            f'<body style="width:{width}px;height:{height}px">{body}</body></html>')


def foot(n):
    return f'<div class="foot"><span>HQbit · Brand guide</span><span>Pixel · Digital · AI · UI</span><span>{n:02d}</span></div>'


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


# ---------------------------------------------------------------- profile pictures

def build_profiles():
    P = os.path.join(ROOT, "profile")
    flat = f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,#7448FF 0%,{C['purple']} 55%,#4E1EE0 100%)"></div>
<div class="grid" style="background-size:64px 64px"></div>
<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)">{logo('stacked', width=600)}</div>"""
    personal = f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 40%,#7448FF 0%,{C['purple']} 55%,#4E1EE0 100%)"></div>
<div class="grid" style="background-size:64px 64px"></div>
<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)">{logo('hq', width=640)}</div>"""
    key = f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 42%,#3A16A8 0%,{C['night']} 50%,{C['void']} 80%)"></div>
<div class="grid" style="background-size:64px 64px"></div>
<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-53%)">{keycap(660)}</div>"""
    for name, body in (("hqbit-profile-picture", flat), ("hqbit-profile-picture-keycap", key),
                       ("hq-personal-profile-picture", personal)):
        html = f"{BUILD}/{name}.html"
        w(html, page(body, 1024, 1024))
        render(html, f"{P}/{name}-1024.png", 1024, 1024)
    imgs = "".join(f'<img src="file://{P}/{n}-1024.png" style="width:{s}px;border-radius:50%">' for n, s in
                   (("hqbit-profile-picture", 300), ("hqbit-profile-picture", 110), ("hqbit-profile-picture", 44),
                    ("hqbit-profile-picture-keycap", 300), ("hq-personal-profile-picture", 300)))
    html = f"{BUILD}/profile-preview.html"
    w(html, page(f'<div style="display:flex;gap:46px;align-items:center;justify-content:center;height:100%;background:{C["night"]}">{imgs}</div>', 1400, 460))
    render(html, f"{P}/profile-picture-preview.png", 1400, 460)


# ---------------------------------------------------------------- boards

W_, H_ = 1920, 1200


def panel(inner, bg, label, span=1, dark_label=False, extra=""):
    col = C["night"] if dark_label else C["lilac"]
    return (f'<div style="grid-column:span {span};background:{bg};border:1px solid #ffffff14;border-radius:28px;'
            f'position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;{extra}">{inner}'
            f'<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{col}">{label}</div></div>')


def header(n, eyebrow, title, sub=""):
    s = (f'<div style="position:absolute;left:72px;top:64px"><div class="eyebrow">{n:02d} · {eyebrow}</div>'
         f'<div class="h1" style="font-size:56px;margin-top:14px">{title}</div>')
    if sub:
        s += f'<div style="font-size:22px;color:{C["lilac"]};margin-top:14px;max-width:1180px;line-height:1.45">{sub}</div>'
    return s + "</div>"


def board_cover():
    tags = "".join(f'<span style="font-family:PX;font-size:20px;color:{C["white"]};border:2px solid #ffffff55;padding:10px 16px;border-radius:12px">{t}</span>'
                   for t in ("PIXEL", "DIGITAL", "AI", "UI", "R36S"))
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(80% 90% at 28% 50%,#7448FF 0%,{C['purple']} 40%,#3A14B8 80%,{C['night']} 100%)"></div>
<div class="grid"></div>
<div style="position:absolute;left:140px;top:50%;transform:translateY(-52%)">{keycap(600)}</div>
<div style="position:absolute;left:900px;top:330px">
 <div class="eyebrow" style="color:#ffffffcc">Brand identity · 2026</div>
 <div style="margin-top:44px">{logo('horizontal', width=860)}</div>
 <div style="font-family:UB;font-weight:400;font-size:34px;line-height:1.4;margin-top:50px">Pixel art, digital art and AI-made UI<br>for retro handhelds.</div>
 <div style="display:flex;gap:14px;margin-top:40px">{tags}</div></div>
<div style="position:absolute;right:90px;top:80px">{pix(SPARKLE, 10, C['white'])}</div>
<div style="position:absolute;right:220px;top:200px;opacity:.6">{pix(SPARKLE, 6, C['lilac'])}</div>
<div style="position:absolute;left:110px;top:90px;opacity:.8">{pix(SPARKLE, 7, C['lime'])}</div>
<div class="foot" style="color:#ffffffaa"><span>HQbit · Brand guide</span><span>Pixel · Digital · AI · UI</span><span>01</span></div>"""


def board_logo_system():
    LH = OL.LH
    cw = 230
    sc = cw / (OL.BIT_X[1] - OL.HQ_X[0])
    q = LH * 0.5 * sc
    cs = f"""<div style="position:relative;padding:{q}px;outline:2px dashed {C['lilac']}88">
<div style="outline:1px solid {C['lilac']}55">{logo('horizontal', width=cw)}</div>
<div style="position:absolute;left:0;top:50%;width:{q}px;height:{q}px;margin-top:{-q/2}px;background:{C['purple']}88"></div>
<div style="position:absolute;right:0;top:50%;width:{q}px;height:{q}px;margin-top:{-q/2}px;background:{C['purple']}88"></div>
<div style="position:absolute;top:0;left:50%;width:{q}px;height:{q}px;margin-left:{-q/2}px;background:{C['purple']}88"></div>
<div style="position:absolute;bottom:0;left:50%;width:{q}px;height:{q}px;margin-left:{-q/2}px;background:{C['purple']}88"></div></div>"""
    sizes = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:12px">{logo("horizontal", width=s)}'
                    f'<span style="font-family:JB;font-size:14px;color:{C["lilac"]}">{s}px</span></div>' for s in (150, 96, 72))
    body = f"""<div class="grid" style="opacity:.5"></div>
{header(1, 'Logo system', 'One logo, every surface.', 'A wide geometric wordmark. The lime chip inside the B is <b style="color:#fff">the bit</b>: the one spot of colour that is not purple. Split into HQ over BIT for square spaces; HQ alone is the personal logo.')}
<div style="position:absolute;left:72px;right:72px;top:330px;bottom:110px;display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:1fr 1fr;gap:24px">
{panel(logo('horizontal', width=700), C['purple'], 'Primary · on HQ Purple', 2, extra='')}
{panel(logo('horizontal', width=700), C['night'], 'On dark', 2)}
{panel(logo('horizontal', fill=C['purple'], chip=C['purple'], width=330), C['white'], 'On light · mono purple', dark_label=True)}
{panel(logo('stacked', width=230), C['purple'], 'Stacked · square spaces')}
{panel(logo('hq', width=250), C['night'], 'HQ · personal logo')}
{panel(f'<div style="display:flex;flex-direction:column;gap:30px;align-items:center;margin-bottom:30px">{cs}<div style="display:flex;gap:26px;align-items:flex-end">{sizes}</div></div>', C['night'], 'Clear space ½ letter height · min. 72px')}
</div>{foot(2)}"""
    return body


def board_color():
    sw = ""
    for key, name, use in NAMES:
        hexv = C[key]
        tc = C["night"] if key in ("lilac", "white", "lime") else C["white"]
        flex = "1.6" if key == "purple" else ("0.8" if key == "lime" else "1")
        sw += f"""<div style="flex:{flex};background:{hexv};border-radius:26px;padding:28px;display:flex;flex-direction:column;justify-content:flex-end;color:{tc};
border:1px solid #ffffff18"><div style="font-family:UB;font-weight:600;font-size:24px;line-height:1.2">{name}</div>
<div style="font-family:JB;font-size:19px;margin-top:8px">{hexv.upper()}</div><div style="font-size:16px;margin-top:10px;opacity:.85;line-height:1.35;min-height:44px">{use}</div></div>"""
    ratios = [("White on HQ Purple", C["white"], C["purple"]), ("White on Night", C["white"], C["night"]),
              ("Lilac on Night", C["lilac"], C["night"]), ("Bit Lime on HQ Purple", C["lime"], C["purple"])]
    rt = "".join(f'<span><b style="color:{a}">{n}</b> · {contrast(a, b):.1f}:1</span>' for n, a, b in ratios)
    return f"""<div class="grid" style="opacity:.5"></div>
{header(2, 'Colour', 'Purple, with one lime bit.', 'HQ Purple carries the brand. Darker purples hold the dark screens; white and lilac carry text. Bit Lime appears only as the bit: one small chip, never large areas or body text.')}
<div style="position:absolute;left:72px;right:72px;top:330px;height:470px;display:flex;gap:18px">{sw}</div>
<div style="position:absolute;left:72px;right:72px;top:830px;height:200px;display:grid;grid-template-columns:2fr 1fr 1.2fr;gap:18px">
<div style="border-radius:26px;background:linear-gradient(120deg,{C['night']} 0%,#3A14B8 45%,{C['purple']} 75%,#8A63FF 100%);padding:28px;display:flex;align-items:flex-end;font-family:JB;font-size:18px">Signature gradient · Night → HQ Purple</div>
<div style="border-radius:26px;background:{C['purple']};padding:28px;display:flex;align-items:center;justify-content:center"><span style="display:inline-block;width:120px;height:56px;border-radius:8px 26px 26px 8px;background:{C['lime']}"></span></div>
<div style="border-radius:26px;background:{C['night']};border:1px solid #ffffff18;padding:28px;display:flex;flex-direction:column;justify-content:flex-end;font-family:JB;font-size:16px;color:{C['lilac']};gap:6px">{rt}</div>
</div>{foot(3)}"""


def board_type():
    def spec(fam, name, role, sample, style, size):
        return f"""<div style="background:{C['night']};border:1px solid #ffffff14;border-radius:28px;padding:40px;display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;justify-content:space-between;font-family:JB;font-size:16px;color:{C['lilac']}"><span>{role}</span><span>{name} · free (SIL OFL)</span></div>
<div style="font-family:{fam};font-size:{size}px;line-height:1.1;{style}">{sample}</div>
<div style="font-family:{fam};font-size:21px;color:{C['lilac']};{style}">ABCDEFGHIJKLM abcdefghijklm 0123456789</div></div>"""
    return f"""<div class="grid" style="opacity:.5"></div>
{header(3, 'Typography', 'Wide and geometric, like the logo.')}
<div style="position:absolute;left:72px;right:72px;top:230px;bottom:110px;display:grid;grid-template-columns:1.3fr 1fr;grid-template-rows:1fr 1fr;gap:24px">
{spec('UB', 'Unbounded', 'Headlines', 'Themes for<br>tiny screens.', 'font-weight:600;letter-spacing:-.02em', 76)}
{spec('IN', 'Inter', 'Body + UI text', 'Unzip, copy the folder into <i>themes</i>, then pick it under UI Settings.', 'font-weight:400', 38)}
{spec('PX', 'Silkscreen', 'Pixel accents, labels', 'PRESS START', 'font-weight:700', 84)}
{spec('JB', 'JetBrains Mono', 'Tech details, versions, file names', 'es-theme-volta-v1.1.zip', 'font-weight:500', 40)}
</div>{foot(4)}"""


def board_elements():
    def tile(inner, label, bg=None):
        return panel(f'<div style="display:flex;align-items:center;justify-content:center;gap:30px">{inner}</div>', bg or C["night"], label)
    icons = "".join(pix(p, 12, C["white"]) for p in (SPARKLE, ARROW, HEART, CURSOR, PAD))
    btn = (f'<div style="display:flex;flex-direction:column;gap:18px">'
           f'<div style="font-family:UB;font-weight:600;font-size:22px;background:{C["white"]};color:{C["purple"]};padding:18px 34px;border-radius:16px;box-shadow:0 6px 0 #3A14B8">Download theme</div>'
           f'<div style="font-family:UB;font-weight:600;font-size:22px;border:2px solid {C["white"]};color:{C["white"]};padding:16px 32px;border-radius:16px">View showcase</div></div>')
    tags = "".join(f'<span style="font-family:JB;font-size:18px;color:{C["white"]};background:#ffffff1a;border:1px solid #ffffff33;padding:8px 14px;border-radius:999px">{t}</span>' for t in ("v1.2", "194 systems", "640×480", "ArkOS"))
    bullets = "".join(f'<div style="display:flex;gap:14px;align-items:center;font-size:22px"><span style="width:26px;height:12px;border-radius:2px 6px 6px 2px;background:{C["lime"]};display:inline-block"></span>{t}</div>' for t in ("13 colour schemes", "Pixel-perfect icons", "Tested on device"))
    pattern = (f'<div style="position:absolute;inset:0;background-color:{C["purple"]};background-image:radial-gradient(#ffffff55 2px,transparent 2.5px);'
               f'background-size:24px 24px;-webkit-mask-image:linear-gradient(135deg,#000,transparent 90%)"></div>')
    stair = "".join(f'<div style="position:absolute;left:{40+i*44}px;bottom:{50+i*44}px;width:44px;height:44px;background:{C["purple"]};opacity:{1-i*0.14}"></div>' for i in range(6))
    return f"""<div class="grid" style="opacity:.5"></div>
{header(4, 'Brand elements', 'Built from bits.')}
<div style="position:absolute;left:72px;right:72px;top:230px;bottom:110px;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:24px">
{tile(keycap(250), 'Keycap icon · hero + profile')}
{tile(icons, 'Pixel icon set · 7×7 grid', C['purple'])}
{tile(btn, 'Buttons', C['purple'])}
{tile(f'<div style="display:flex;flex-direction:column;gap:22px"><div style="display:flex;gap:10px;flex-wrap:wrap;max-width:420px">{tags}</div>{bullets}</div>', 'Tags + bit bullets')}
{panel(pattern + f'<div style="position:relative">{logo("stacked", width=220)}</div>', C['purple'], 'Dot-grid pattern')}
{panel(stair + f'<div style="position:absolute;right:36px;top:40px;font-family:PX;font-weight:700;font-size:44px;text-align:right;line-height:1.1">LEVEL<br>UP</div>', C['night'], 'Bit stairs · motion + dividers')}
</div>{foot(5)}"""


def board_applications():
    prof = f"file://{ROOT}/profile/hqbit-profile-picture-1024.png"
    reddit = f"""<div style="background:{C['night']};border:1px solid #ffffff14;border-radius:28px;overflow:hidden;position:relative">
<div style="height:200px;background:linear-gradient(110deg,#3A14B8,{C['purple']} 60%,#7A4BFF);position:relative;overflow:hidden">
<div class="grid" style="background-size:32px 32px"></div>
<div style="position:absolute;right:60px;top:50%;transform:translateY(-50%)">{logo('horizontal', width=420)}</div>
<div style="position:absolute;left:300px;top:40px;opacity:.8">{pix(SPARKLE, 8, C['white'])}</div></div>
<img src="{prof}" style="position:absolute;left:48px;top:140px;width:150px;border-radius:50%;border:6px solid {C['night']}">
<div style="padding:24px 48px 0 220px"><div style="font-family:UB;font-weight:600;font-size:30px">r/HQbit</div>
<div style="font-size:19px;color:{C['lilac']};margin-top:6px">EmulationStation themes, pixel icon packs and UI for the R36S</div></div>
<div style="position:absolute;left:28px;bottom:22px;font-family:JB;font-size:15px;color:{C['lilac']}">Reddit · banner + avatar</div></div>"""
    insta = panel(f"""<div style="width:310px;height:310px;border-radius:18px;overflow:hidden;position:relative;background:{C['purple']};margin-bottom:30px">
<div class="grid" style="background-size:24px 24px"></div>
<div style="position:absolute;left:28px;top:26px;font-family:PX;font-size:15px">NEW THEME DROP</div>
<div style="position:absolute;left:28px;top:60px;font-family:UB;font-weight:800;font-size:40px;line-height:1">NeonGlow<br>v1.2 <span class="chip"></span></div>
<div style="position:absolute;left:28px;bottom:28px">{logo('horizontal', width=150)}</div>
<div style="position:absolute;left:28px;bottom:66px;font-family:JB;font-size:14px">194 systems · free</div></div>""", C['night'], 'Instagram · post template')
    boot = panel(f"""<div style="background:#E9E6EF;border-radius:28px 28px 70px 28px;padding:18px 18px 84px;box-shadow:0 20px 50px #0008;position:relative;margin-bottom:30px">
<div style="width:300px;height:225px;border:8px solid #15121b;border-radius:6px;background:{C['purple']};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px">
{logo('horizontal', width=200)}
<div style="width:150px;height:8px;background:#ffffff33"><div style="width:62%;height:100%;background:{C['white']}"></div></div>
<div style="font-family:PX;font-size:12px">LOADING…</div></div>
<div style="position:absolute;left:30px;bottom:14px">{pix(PAD_SOLID, 9, '#2a2730')}</div>
<div style="position:absolute;right:34px;bottom:26px;display:flex;gap:10px"><i style="width:26px;height:26px;border-radius:50%;background:#2a2730;display:block"></i><i style="width:26px;height:26px;border-radius:50%;background:{C['purple']};display:block"></i></div></div>""",
                 C['night'], 'R36S · boot / loading screen')
    web = f"""<div style="background:{C['night']};border:1px solid #ffffff14;border-radius:28px;position:relative;overflow:hidden;padding:30px">
<div style="border-radius:16px;border:1px solid #ffffff22;overflow:hidden;height:calc(100% - 40px);background:{C['purple']}">
<div style="height:36px;background:#3A14B8;display:flex;align-items:center;gap:8px;padding:0 14px">{''.join('<i style="width:11px;height:11px;border-radius:50%;background:#ffffff44;display:block"></i>' for _ in range(3))}
<span style="margin-left:14px;font-family:JB;font-size:13px;color:#ffffffcc">hqbit · themes for the R36S</span></div>
<div style="padding:24px 30px;display:flex;justify-content:space-between;align-items:center">{logo('horizontal', width=150)}
<span style="font-size:15px;color:#ffffffcc">Themes · Icons · Downloads</span></div>
<div style="padding:10px 30px"><div style="font-family:UB;font-weight:800;font-size:40px;line-height:1.05">Themes built<br>from bits<span style="color:{C['lime']}">.</span></div>
<div style="display:flex;gap:12px;margin-top:22px"><span style="font-family:UB;font-weight:600;font-size:15px;background:{C['white']};color:{C['purple']};padding:12px 20px;border-radius:12px">Download all</span>
<span style="font-family:UB;font-weight:600;font-size:15px;border:2px solid {C['white']};padding:10px 18px;border-radius:12px">See showcase</span></div></div></div>
<div style="position:absolute;left:28px;bottom:14px;font-family:JB;font-size:15px;color:{C['lilac']}">Website · landing hero</div></div>"""
    return f"""<div class="grid" style="opacity:.5"></div>
{header(5, 'Applications', 'Out in the wild.')}
<div style="position:absolute;left:72px;right:72px;top:230px;bottom:110px;display:grid;grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:24px">
{reddit}{insta}{web}{boot}</div>{foot(6)}"""


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
