#!/usr/bin/env python3
"""HQbit showcase images: each theme on an R36S, with the project name and logo, plus a collection poster.

usage: python3 tools/build_showcase.py   (from hqbit-brand/; screenshots in showcase/screens/)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_brand import BUILD, C, ROOT, fonts_css, logo, pix, render, w, SPARKLE  # noqa: E402

SCREENS = os.path.join(ROOT, "showcase", "screens")
OUT = os.path.join(ROOT, "showcase")

THEMES = [
    dict(key="volta", name="Volta", version="v1.1", file="es-theme-volta-v1.1.zip",
         line="A dark and light dashboard theme with glossy cards, tick-ring gauges and dot-matrix numbers.",
         chips=["13 colour schemes", "3 carousel layouts", "163 system logos", "Tested on the R36S"],
         hero="volta/system-horizontal-dark.png",
         thumbs=["volta/system-wheel-citrine.png", "volta/gamelist-dark.png", "volta/system-vertical-light.png"]),
    dict(key="neonglow", name="NeonGlow", version="v1.2", file="neonglow-r36s-v1.2.zip",
         line="Deep-glow glass tiles that light up in each system's own colour, on a dark or light canvas.",
         chips=["13 colour schemes", "4 system layouts", "194 systems", "Light + dark"],
         hero="neonglow/system-vertical.png",
         thumbs=["neonglow/system-wheel.png", "neonglow/gamelist-dark.png", "neonglow/system-light-horizontal.png"]),
    dict(key="vcr", name="VCR OSD", version="v1", file="es-theme-vcr-osd.zip",
         line="A blue-screen VHS on-screen display: hand-drawn pixel hardware, a custom pixel font and a tape-counter timeline.",
         chips=["153 pixel-art systems", "Custom pixel font", "3 colour sets", "CRT scanlines"],
         hero="vcr/system-snes.png",
         thumbs=["vcr/gamelist-snes.png", "vcr/system-gba-navy.png", "vcr/loading.png"]),
    dict(key="deskos", name="DeskOS", version="v2", file="deskos-r36s-theme-v2.zip",
         line="A retro desktop for your handheld: system windows with full-colour pixel consoles and 14 schemes.",
         chips=["14 colour schemes", "7 new dark schemes", "Pixel-perfect consoles", "640×464 native art"],
         hero="deskos/system-classic.png",
         thumbs=["deskos/system-amber-night.png", "deskos/gamelist-ice-night.png", "deskos/system-phosphor-night.png"]),
]


def img(rel):
    return "file://" + os.path.join(SCREENS, rel)


def device(screen, width=760):
    """R36S-style handheld with a 4:3 screen."""
    sw = width * 0.84
    sh = sw * 0.75
    pad = (width - sw) / 2
    return f"""<div style="position:relative;width:{width}px;padding:{pad}px {pad}px {sw*0.62}px;background:linear-gradient(160deg,#F4F2F8,#D9D5E3);
 border-radius:{width*0.07}px {width*0.07}px {width*0.2}px {width*0.07}px;box-shadow:0 40px 80px #0009,inset 0 2px 0 #fff,inset 0 -6px 14px #0002">
<div style="background:#14111b;border-radius:{width*0.02}px;padding:{width*0.022}px;box-shadow:inset 0 0 0 2px #0006">
<img src="{screen}" style="display:block;width:{sw - width*0.044}px;height:{sh - width*0.033}px;object-fit:cover;border-radius:4px"></div>
<div style="position:absolute;left:{width*0.1}px;bottom:{width*0.2}px">{pix(["..XXX..", "..XXX..", "XXXXXXX", "XXXXXXX", "XXXXXXX", "..XXX..", "..XXX.."], width*0.024, '#2a2730')}</div>
<div style="position:absolute;right:{width*0.1}px;bottom:{width*0.19}px;width:{width*0.19}px;height:{width*0.19}px">
{''.join(f'<i style="position:absolute;left:{x*width*0.19}px;top:{y*width*0.19}px;width:{width*0.06}px;height:{width*0.06}px;margin:-{width*0.03}px;border-radius:50%;background:{c};display:block"></i>' for x, y, c in ((.5, .12, "#2a2730"), (.12, .5, "#2a2730"), (.88, .5, C["purple"]), (.5, .88, "#2a2730")))}</div>
<div style="position:absolute;left:{width*0.2}px;bottom:{width*0.05}px;width:{width*0.16}px;height:{width*0.16}px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#3a3542,#16131c);box-shadow:0 4px 10px #0005"></div>
<div style="position:absolute;right:{width*0.2}px;bottom:{width*0.05}px;width:{width*0.16}px;height:{width*0.16}px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#3a3542,#16131c);box-shadow:0 4px 10px #0005"></div>
<div style="position:absolute;left:50%;bottom:{width*0.24}px;transform:translateX(-50%);display:flex;gap:{width*0.03}px">
<i style="width:{width*0.06}px;height:{width*0.02}px;border-radius:9px;background:#2a2730;display:block"></i><i style="width:{width*0.06}px;height:{width*0.02}px;border-radius:9px;background:#2a2730;display:block"></i></div>
</div>"""


def page(body, W, H):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts_css()}</style></head>'
            f'<body style="width:{W}px;height:{H}px">{body}</body></html>')


BG = (f'<div style="position:absolute;inset:0;background:radial-gradient(70% 90% at 75% 45%,#7448FF 0%,{C["purple"]} 38%,#3A14B8 72%,{C["night"]} 100%)"></div>'
      '<div class="grid"></div>')


def theme_card(t):
    chips = "".join(f'<span style="font-family:JB;font-size:19px;background:#ffffff1f;border:1px solid #ffffff40;padding:9px 16px;border-radius:999px">{c}</span>' for c in t["chips"])
    thumbs = "".join(f'<img src="{img(p)}" style="width:250px;height:188px;object-fit:cover;border-radius:14px;border:3px solid #ffffff33;box-shadow:0 18px 40px #0007">' for p in t["thumbs"])
    return f"""{BG}
<div style="position:absolute;left:96px;top:84px">{logo('horizontal', width=230)}</div>
<div style="position:absolute;right:96px;top:92px;font-family:JB;font-size:18px;letter-spacing:.14em;color:#ffffffcc">EMULATIONSTATION THEME · R36S</div>
<div style="position:absolute;left:96px;top:300px;width:720px">
 <div style="font-family:PX;font-size:22px;color:{C['lime']}">{t['version'].upper()}</div>
 <div style="font-family:UB;font-weight:800;font-size:120px;line-height:1;letter-spacing:-.02em;margin-top:12px">{t['name']}</div>
 <div style="font-size:30px;line-height:1.45;margin-top:34px;color:#ffffffe6">{t['line']}</div>
 <div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:40px">{chips}</div>
 <div style="font-family:JB;font-size:18px;color:#ffffffaa;margin-top:44px">↓ {t['file']}</div></div>
<div style="position:absolute;right:130px;top:170px">{device(img(t['hero']), 680)}</div>
<div style="position:absolute;left:96px;bottom:96px;display:flex;gap:22px">{thumbs}</div>
<div style="position:absolute;right:980px;top:150px;opacity:.9">{pix(SPARKLE, 8, C['lime'])}</div>"""


def collection():
    devs = "".join(f"""<div style="display:flex;flex-direction:column;align-items:center;gap:34px">{device(img(t['hero']), 380)}
<div style="text-align:center"><div style="font-family:UB;font-weight:800;font-size:38px">{t['name']}</div>
<div style="font-family:JB;font-size:17px;color:#ffffffbb;margin-top:8px">{t['chips'][0]} · {t['chips'][1]}</div></div></div>""" for t in THEMES)
    return f"""{BG}
<div style="position:absolute;left:0;right:0;top:80px;display:flex;flex-direction:column;align-items:center;gap:22px">
{logo('horizontal', width=330)}
<div style="font-family:UB;font-weight:600;font-size:46px;margin-top:18px">The R36S theme collection</div>
<div style="font-family:JB;font-size:19px;letter-spacing:.14em;color:#ffffffcc">4 FREE EMULATIONSTATION THEMES · ARKOS / dARKOS · 640×480</div></div>
<div style="position:absolute;left:0;right:0;top:350px;display:flex;justify-content:center;gap:56px">{devs}</div>
<div style="position:absolute;left:96px;top:110px">{pix(SPARKLE, 8, C['lime'])}</div>
<div style="position:absolute;right:120px;top:200px;opacity:.6">{pix(SPARKLE, 6, '#ffffff')}</div>"""


if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    for t in THEMES:
        html = f"{BUILD}/showcase-{t['key']}.html"
        w(html, page(theme_card(t), 1920, 1200))
        render(html, f"{OUT}/hqbit-showcase-{t['key']}.png", 1920, 1200)
    html = f"{BUILD}/showcase-collection.html"
    w(html, page(collection(), 1920, 1080))
    render(html, f"{OUT}/hqbit-showcase-collection.png", 1920, 1080)
    print("done")
