#!/usr/bin/env python3
"""Reddit post images (1080x1350): hero, themes on devices, screenshot sheet."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_brand import BUILD, C, ROOT, logo, render, w  # noqa: E402
from build_showcase import BG, page  # noqa: E402

W, H = 1080, 1350
P = os.path.join(ROOT, "photos", "real")
S = os.path.join(ROOT, "showcase", "screens")
OUT = os.path.join(ROOT, "reddit")
FOOT = (f'<div style="position:absolute;left:0;right:0;bottom:44px;text-align:center;font-family:JB;font-size:17px;'
        f'letter-spacing:.12em;color:#ffffffcc">FREE · R36S &amp; CLONES · EMUELEC · ARKOS · dARKOS</div>')


def hero():
    return f"""<img src="file://{P}/hqbit-photo-collection-five.jpg" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 12%">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#0d0619ee 0%,#0d061900 30%,#0d061900 70%,#0d0619f2 100%)"></div>
<div style="position:absolute;left:0;right:0;top:56px;display:flex;flex-direction:column;align-items:center;gap:18px">
 {logo('horizontal', width=250)}
 <div style="font-family:UB;font-weight:800;font-size:56px;line-height:1.05;text-align:center;letter-spacing:-.02em">4 free themes<br>for the R36S</div></div>
<div style="position:absolute;left:0;right:0;bottom:92px;text-align:center;font-family:UB;font-weight:600;font-size:28px;color:{C['lime']}">VOLTA · NEONGLOW · VCR OSD · DESKOS</div>
{FOOT}"""


def grid():
    items = [("volta", "Volta"), ("neonglow", "NeonGlow"), ("vcr", "VCR OSD"), ("deskos", "DeskOS")]
    cells = "".join(f"""<div style="position:relative;border-radius:22px;overflow:hidden;border:1px solid #ffffff2a;box-shadow:0 20px 50px #0008">
<img src="file://{P}/hqbit-photo-{k}.jpg" style="width:100%;height:100%;object-fit:cover">
<div style="position:absolute;left:0;right:0;bottom:0;padding:40px 22px 18px;background:linear-gradient(0deg,#0d0619e6,#0d061900);font-family:UB;font-weight:800;font-size:34px">{n}</div></div>""" for k, n in items)
    return f"""{BG}
<div style="position:absolute;left:56px;top:56px">{logo('horizontal', width=180)}</div>
<div style="position:absolute;right:56px;top:62px;font-family:UB;font-weight:600;font-size:26px">The collection</div>
<div style="position:absolute;left:56px;right:56px;top:150px;bottom:110px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:20px">{cells}</div>
{FOOT}"""


def sheet():
    rows = [("Volta", ["volta/system-horizontal-dark", "volta/system-wheel-citrine", "volta/gamelist-dark"]),
            ("NeonGlow", ["neonglow/system-vertical", "neonglow/system-light-horizontal", "neonglow/gamelist-dark"]),
            ("VCR OSD", ["vcr/system-snes", "vcr/gamelist-snes", "vcr/system-psx-midnight"]),
            ("DeskOS", ["deskos/system-classic", "deskos/system-amber-night", "deskos/gamelist-ice-night"])]
    body = ""
    for name, shots in rows:
        imgs = "".join(f'<img src="file://{S}/{p}.png" style="width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:10px;border:1px solid #ffffff22;display:block">' for p in shots)
        body += f"""<div><div style="font-family:UB;font-weight:800;font-size:22px;margin-bottom:6px">{name}</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">{imgs}</div></div>"""
    return f"""{BG}
<div style="position:absolute;left:56px;top:50px">{logo('horizontal', width=170)}</div>
<div style="position:absolute;right:56px;top:56px;font-family:UB;font-weight:600;font-size:24px">On the 640×480 screen</div>
<div style="position:absolute;left:56px;right:56px;top:118px;display:flex;flex-direction:column;gap:14px">{body}</div>
{FOOT}"""


if __name__ == "__main__":
    os.makedirs(BUILD, exist_ok=True)
    for i, (n, fn) in enumerate((("hero", hero), ("themes", grid), ("screens", sheet)), 1):
        html = f"{BUILD}/reddit-{n}.html"
        w(html, page(fn(), W, H))
        render(html, f"{OUT}/hqbit-reddit-{i}-{n}.png", W, H)
    print("done")
