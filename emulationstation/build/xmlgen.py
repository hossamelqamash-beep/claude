"""Theme XML for Volta, structured like a theme known to work on the R36S.

Layout of the generated files (same structure as es-theme-vcr-osd):

  <system>/theme.xml   per-system <variables>, then <include> of _inc/main.xml,
                       then the option <subset>s at the top level
  _inc/main.xml        every view with literal default values
                       (Volta Dark, Medium font, Horizontal carousel)
  _inc/color-*.xml     colour scheme: only the properties it changes
  _inc/font-*.xml      font size: only the properties it changes
  _inc/system-*.xml    carousel layout: only the properties it changes

No values come from variables set inside option files, so if an option file
does not load (or a stale setting matches nothing) the theme still renders
completely with its defaults. The only variables are the per-system ones set
at the top of each system's theme.xml (logo name, names, maker, year).

The option files are computed as differences from the defaults, and the
build asserts that default + colour diff + font diff + layout diff equals the
fully specified theme for every combination.
"""
import itertools
from collections import OrderedDict

import build as b
from palettes import PALETTES

W, H = b.W, b.H
nx, ny, pair = b.nx, b.ny, b.pair_x
fsz, eff_px, glyph_height, xml_hex = b.fsz, b.eff_px, b.glyph_height, b.xml_hex

FONT_MED = "./../_fonts/Urbanist-Medium.ttf"
FONT_SEMI = "./../_fonts/Urbanist-SemiBold.ttf"
FONT_DOT = "./../_fonts/Doto-Black.ttf"
OFF = "2 2"  # off-screen, how ES themes hide elements (works on every fork)

MODES = ("horizontal", "vertical", "wheel")
MODE_NAMES = {"horizontal": "Horizontal", "vertical": "Vertical list", "wheel": "Wheel"}
FONT_ORDER = ("medium", "small", "large")


def hexa(v, alpha="FF"):
    v = xml_hex(v)
    return v if len(v) == 8 else v + alpha


def sys_tokens(p):
    """Colours for the system view (cards are cream in Citrine Pop)."""
    if p["name"] == "citrine-pop":
        return dict(sysLogo="111111", sysCardText="111111", sysCardDim="111111A8", sysInfo="111111")
    light = p["mode"] == "light"
    return dict(sysLogo=xml_hex(p["logoCard"]), sysCardText=xml_hex(p["cardText"]),
                sysCardDim=xml_hex(p["cardDim"]),
                sysInfo=xml_hex(p["text"]) if light else xml_hex(p["cardText"]))


def font_metrics(f):
    lst = f["list"]
    px = eff_px(lst)
    glyph = glyph_height(px)
    row = max(glyph, px) * f["spacing"]
    offset = 0.75 * glyph - row / 2
    desc_line = glyph_height(eff_px(f["desc"])) * b.DESC_SPACING
    return row, offset, desc_line * f["descLines"]


class Theme:
    """view -> element key -> (tag, name, attrs, props)"""

    def __init__(self):
        self.views = OrderedDict()

    def el(self, view, tag, name, extra=False, **props):
        v = self.views.setdefault(view, OrderedDict())
        key = (tag, name)
        if key not in v:
            v[key] = dict(extra=extra, props=OrderedDict())
        for k, val in props.items():
            if val is not None:
                v[key]["props"][k] = str(val)


def full_theme(p, fname, mode):
    """The complete theme for one combination of options."""
    f = b.FONT_SIZES[fname]
    st = sys_tokens(p)
    cs = p["name"]
    t = Theme()
    row, sel_off, desc_h = font_metrics(f)

    # ------------------------------------------------------------ system view
    sv = "system"
    for m in MODES:
        t.el(sv, "image", "bg" + m.capitalize(), extra=True,
             pos="0 0" if m == mode else OFF, size="1 1",
             path=f"./../_art/{cs}/system-{m}.png", zIndex=0)

    if mode == "horizontal":
        x, y, w, h = b.H_CARD
        car = dict(type="horizontal", pos=pair(0, y), size=pair(W, h), logoSize=pair(168, 74), logoScale="1.32",
                   maxLogoCount=3)
    elif mode == "vertical":
        x, y, w, h = b.V_COLUMN
        car = dict(type="vertical", pos=pair(x, y), size=pair(w, h), logoSize=pair(150, 34), logoScale="1.18",
                   maxLogoCount=b.CAROUSEL_SLOTS_V)
    else:
        x, y, w, h = b.W_TRACK
        car = dict(type="vertical_wheel", pos=pair(x, y), size=pair(w, h), logoSize=pair(170, 40),
                   logoScale="1.15", maxLogoCount=7)
    t.el(sv, "carousel", "systemcarousel", color="00000000", logoAlignment="center", logoRotation="9",
         logoRotationOrigin="3.2 0.5", systemInfoDelay="0", zIndex="40", **car)
    t.el(sv, "image", "logo", path="./../_art/logos/${sysLogo}.png", color=hexa(st["sysLogo"]))
    t.el(sv, "text", "logoText", fontPath=FONT_SEMI, fontSize=fsz(30 if mode == "horizontal" else 20),
         color=hexa(st["sysLogo"]))

    # horizontal: name + maker under the card
    on_h = mode == "horizontal"
    t.el(sv, "text", "hName", extra=True, text="${sysName}", pos=pair(40, 312) if on_h else OFF, size=pair(560, 34),
         fontPath=FONT_SEMI, fontSize=fsz(f["sys"]), color=hexa(p["bgText"]), alignment="center", zIndex=12)
    t.el(sv, "text", "hMaker", extra=True, text="${sysMakerYear}", pos=pair(40, 346) if on_h else OFF,
         size=pair(560, 22), fontPath=FONT_MED, fontSize=fsz(15), color=hexa(p["bgDim"]), alignment="center",
         zIndex=12)

    # vertical / wheel: details on the big card
    card = b.V_CARD if mode == "vertical" else b.W_CARD
    cx_, cy_, cw, ch = card
    on_c = mode != "horizontal"

    def cpos(dx, dy):
        return pair(cx_ + dx, cy_ + dy) if on_c else OFF

    t.el(sv, "text", "cName", extra=True, text="${sysName}", pos=cpos(24, 20), size=pair(cw - 48, 32),
         fontPath=FONT_SEMI, fontSize=fsz(f["sys"]), color=hexa(st["sysCardText"]), alignment="left", zIndex=12)
    t.el(sv, "text", "cMaker", extra=True, text="${sysMaker}", pos=cpos(24, 54), size=pair(cw - 48, 20),
         fontPath=FONT_MED, fontSize=fsz(15), color=hexa(st["sysCardDim"]), alignment="left", zIndex=12)
    t.el(sv, "image", "cLogo", extra=True, path="./../_art/logos/${sysLogo}.png", pos=cpos(cw / 2, 172),
         maxSize=pair(250, 96), origin="0.5 0.5", color=hexa(st["sysLogo"]), zIndex=12)
    t.el(sv, "text", "cYearLabel", extra=True, text="${sysYearLabel}", pos=cpos(24, ch - 92), size=pair(150, 18),
         fontPath=FONT_MED, fontSize=fsz(13), color=hexa(st["sysCardDim"]), alignment="left", zIndex=12)
    t.el(sv, "text", "cYear", extra=True, text="${sysYear}", pos=cpos(22, ch - 72), size=pair(170, 50),
         fontPath=FONT_DOT, fontSize=fsz(44), color=hexa(st["sysCardText"]), alignment="left", zIndex=12)

    if on_h:
        px, py, pw, ph = b.H_PILL
        info = (px + 18, py, pw - 26, ph)
    else:
        info = b.sys_info_pill(card)
    ix, iy, iw, ih = info
    t.el(sv, "text", "systemInfo", pos=pair(ix, iy), size=pair(iw, ih), fontPath=FONT_MED, fontSize=fsz(13),
         color=hexa(st["sysInfo"]), backgroundColor="00000000", alignment="center")
    help_el(t, sv, p)

    # --------------------------------------------------------- game list views
    gl = "basic,detailed,video,grid"
    t.el(gl, "image", "background", pos="0 0", size="1 1", path=f"./../_art/{cs}/gamelist.png", zIndex=0)
    hx, hy, hw, hh = b.HEADER_LOGO
    t.el(gl, "image", "logo", path="./../_art/logos/${sysLogo}.png", pos=pair(hx, hy), maxSize=pair(hw, hh),
         origin="0 0.5", color=hexa(p["logo"]), zIndex=50)
    lx, ly, lw, lh = b.LIST_INNER
    t.el(gl, "textlist", "gamelist", pos=pair(lx, ly), size=pair(lw, lh),
         selectorImagePath=f"./../_art/{cs}/selector.png", selectorImageTile="false",
         selectorColor="FFFFFFFF", selectorColorEnd="FFFFFFFF",
         selectorHeight=f"{row / H:.4f}", selectorOffsetY=f"{sel_off / H:.4f}",
         selectedColor=hexa(p["selText"]), primaryColor=hexa(p["text"]), secondaryColor=hexa(p["accent"]),
         fontPath=FONT_MED, fontSize=fsz(f["list"]), lineSpacing=str(f["spacing"]), alignment="left",
         horizontalMargin=f"{14 / W:.4f}", zIndex=20)
    help_el(t, gl, p)

    md = "detailed,video,grid"
    ax, ay, aw, ah = b.ART_WELL
    acx, acy = ax + aw / 2, ay + ah / 2
    art_max = pair(aw - 2 * b.ART_PAD, ah - 2 * b.ART_PAD)
    t.el(md, "image", "md_image", pos=pair(acx, acy), maxSize=art_max, origin="0.5 0.5",
         default=f"./../_art/{cs}/noart.png", zIndex=30)
    ix, iy, iw, ih = b.INFO
    t.el(md, "rating", "md_rating", pos=pair(ix + 18, iy + 11), size=pair(0, 15),
         filledPath="./../_art/ui/star-filled.png", unfilledPath="./../_art/ui/star-empty.png",
         color=hexa(p["star"]), unfilledColor=hexa(p["starOff"]), zIndex=40)
    t.el(md, "datetime", "md_releasedate", pos=pair(ix + iw - 18 - 120, iy + 6), size=pair(120, 24),
         fontPath=FONT_DOT, fontSize=fsz(20), color=hexa(p["cardText"]), alignment="right", format="%Y",
         zIndex=40)
    t.el(md, "text", "md_genre", pos=pair(ix + 104, iy + 9), size=pair(iw - 104 - 18 - 64, 18), fontPath=FONT_MED,
         fontSize=fsz(13), color=hexa(p["cardDim"]), alignment="left", zIndex=40)
    t.el(md, "text", "md_description", pos=pair(ix + 18, iy + 42), size=f"{nx(iw - 36)} {desc_h / H:.4f}",
         fontPath=FONT_MED, fontSize=fsz(f["desc"]), color=hexa(p["cardText"]), alignment="left",
         lineSpacing=str(b.DESC_SPACING), zIndex=40)
    for n in ("md_lbl_rating", "md_lbl_releasedate", "md_lbl_developer", "md_lbl_publisher", "md_lbl_genre",
              "md_lbl_players", "md_lbl_lastplayed", "md_lbl_playcount", "md_developer", "md_publisher",
              "md_players", "md_playcount", "md_name"):
        t.el(md, "text", n, pos=OFF, size="0.01 0.01")
    t.el(md, "datetime", "md_lastplayed", pos=OFF, size="0.01 0.01")

    t.el("video", "video", "md_video", pos=pair(acx, acy), maxSize=art_max, origin="0.5 0.5",
         default=f"./../_art/{cs}/noart.png", delay="1.2", showSnapshotNoVideo="true", showSnapshotDelay="true",
         zIndex=31)

    gx, gy, gw, gh = b.LIST
    t.el("grid", "imagegrid", "gamegrid", pos=pair(gx + 8, gy + 8), size=pair(gw - 16, gh - 16),
         margin=pair(6, 6), autoLayout="3 3", autoLayoutSelectedZoom="1", imageSource="image",
         gameImage=f"./../_art/{cs}/noart.png", folderImage=f"./../_art/{cs}/noart.png",
         scrollDirection="vertical", zIndex=20)
    t.el("grid", "gridtile", "default", padding="4 4", imageColor="FFFFFFFF",
         backgroundImage="./../_art/ui/tile.png", backgroundCornerSize="0.07 0.07",
         backgroundColor=hexa(p["text"], "10"))
    t.el("grid", "gridtile", "selected", backgroundColor=hexa(p["accent"]))

    t.el("basic", "image", "background", path=f"./../_art/{cs}/gamelist-basic.png")
    t.el("basic", "image", "basicLogo", extra=True, path="./../_art/logos/${sysLogo}.png",
         pos=pair(acx, acy - 14), maxSize=pair(220, 84), origin="0.5 0.5", color=hexa(p["dim"]), zIndex=30)
    t.el("basic", "text", "basicName", extra=True, text="${sysName}", pos=pair(ax + 16, acy + 46),
         size=pair(aw - 32, 24), fontPath=FONT_SEMI, fontSize=fsz(17), color=hexa(p["text"]),
         alignment="center", zIndex=30)
    t.el("basic", "text", "basicHint", extra=True,
         text="No game info yet. Open the menu with START and run the scraper to add box art, "
              "descriptions and ratings.",
         pos=pair(ix + 18, iy + 16), size=pair(iw - 36, ih - 32), fontPath=FONT_MED, fontSize=fsz(f["desc"]),
         color=hexa(p["cardText"]), alignment="left", lineSpacing="1.25", zIndex=30)

    # --------------------------------------------------------------------- menu
    mv = "menu"
    menu_text = "F4F4F6" if p["name"] == "citrine-pop" else xml_hex(p["text"])
    t.el(mv, "menuBackground", "menubg", path=f"./../_art/{cs}/menu.png", fadePath="./../_art/ui/fade.png",
         color="FFFFFFFF", centerColor="FFFFFFFF", cornerSize="32 32")
    t.el(mv, "menuText", "menutitle", fontPath=FONT_SEMI, fontSize=fsz(f["menuTitle"]), color=hexa(menu_text))
    t.el(mv, "menuText", "menutext", fontPath=FONT_MED, fontSize=fsz(f["menu"]), color=hexa(menu_text),
         separatorColor="FFFFFF14" if p["mode"] == "dark" or p["name"] == "citrine-pop" else "0000001A",
         selectorColor=hexa(p["sel2"]), selectedColor=hexa(p["selText"]))
    t.el(mv, "menuTextSmall", "menutextsmall", fontPath=FONT_MED, fontSize=fsz(f["menuSmall"]),
         color=hexa(p["dim"]))
    t.el(mv, "menuText", "menufooter", fontPath=FONT_MED, fontSize=fsz(f["menuSmall"]), color=hexa(p["dim"]))
    t.el(mv, "menuSwitch", "menuswitch", pathOn=f"./../_art/{cs}/switch-on.png",
         pathOff=f"./../_art/{cs}/switch-off.png")
    t.el(mv, "menuSlider", "menuslider", path=f"./../_art/{cs}/knob.png")
    t.el(mv, "menuButton", "menubutton", path=f"./../_art/{cs}/button.png",
         filledPath=f"./../_art/{cs}/button-filled.png")
    t.el(mv, "menuTextEdit", "menutextedit", inactive=f"./../_art/{cs}/textedit.png",
         active=f"./../_art/{cs}/textedit-active.png")

    # ------------------------------------------- splash (ES builds that support it)
    t.el("splash", "image", "background", pos="0 0", size="1 1", path="./../_art/splash.png")
    t.el("splash", "text", "label", pos=pair(16, 412), size=pair(W - 32, 24), alignment="center",
         fontPath=FONT_MED, fontSize=fsz(15), color="8D8D96FF")
    return t


def help_el(t, view, p):
    t.el(view, "helpsystem", "help", pos=pair(14, b.HELP_Y), textColor=hexa(p["bgDim"]),
         iconColor=hexa(p["bgText"]), fontPath=FONT_MED, fontSize=fsz(13))


# ---------------------------------------------------------------------------
def diff(base, other):
    """Properties of `other` that differ from `base` (same element set)."""
    out = Theme()
    for view, els in other.views.items():
        for key, e in els.items():
            be = base.views[view][key]
            for k, v in e["props"].items():
                if be["props"].get(k) != v:
                    out.el(view, key[0], key[1], extra=e["extra"], **{k: v})
    return out


def merge(*themes):
    out = Theme()
    for t in themes:
        for view, els in t.views.items():
            for key, e in els.items():
                out.el(view, key[0], key[1], extra=e["extra"], **e["props"])
    return out


def render(t, comment, with_extra=True):
    lines = [f"<!-- {comment} (generated by build/xmlgen.py) -->", "<theme>", "\t<formatVersion>7</formatVersion>"]
    for view, els in t.views.items():
        lines.append(f'\t<view name="{view}">')
        for (tag, name), e in els.items():
            extra = ' extra="true"' if (e["extra"] and with_extra) else ""
            lines.append(f'\t\t<{tag} name="{name}"{extra}>')
            for k, v in e["props"].items():
                lines.append(f"\t\t\t<{k}>{b.xml_escape(v)}</{k}>")
            lines.append(f"\t\t</{tag}>")
        lines.append("\t</view>")
    lines.append("</theme>")
    return "\n".join(lines) + "\n"


def palette(name):
    for n, d, p in PALETTES:
        if n == name:
            return dict(p, name=n)
    raise KeyError(name)


def subsets_xml(prefix):
    cs = "\n".join(f'\t\t<include name="{n}" displayName="{d}">{prefix}color-{n}.xml</include>'
                   for n, d, _ in PALETTES)
    fs = "\n".join(f'\t\t<include name="{n}" displayName="{n.capitalize()}">{prefix}font-{n}.xml</include>'
                   for n in FONT_ORDER)
    sv = "\n".join(f'\t\t<include name="{m}" displayName="{MODE_NAMES[m]}">{prefix}system-{m}.xml</include>'
                   for m in MODES)
    return (f'\t<subset name="colorset" displayName="Color scheme">\n{cs}\n\t</subset>\n'
            f'\t<subset name="fontsize" displayName="Font size">\n{fs}\n\t</subset>\n'
            f'\t<subset name="systemview" displayName="System carousel">\n{sv}\n\t</subset>\n')


def system_theme(vars_, prefix):
    v = "\n".join(f"\t\t<{k}>{b.xml_escape(val)}</{k}>" for k, val in vars_.items())
    return (f"<theme>\n\t<formatVersion>7</formatVersion>\n\t<variables>\n{v}\n\t</variables>\n"
            f"\t<include>{prefix}main.xml</include>\n{subsets_xml(prefix)}</theme>\n")


def write_all(write):
    p0 = palette(PALETTES[0][0])
    f0, m0 = FONT_ORDER[0], MODES[0]
    base = full_theme(p0, f0, m0)
    cdiff = {n: diff(base, full_theme(palette(n), f0, m0)) for n, _, _ in PALETTES}
    fdiff = {n: diff(base, full_theme(p0, n, m0)) for n in FONT_ORDER}
    mdiff = {n: diff(base, full_theme(p0, f0, n)) for n in MODES}

    # every combination must be exactly reproducible from base + the three diffs
    for (pn, _, _), fn, mn in itertools.product(PALETTES, FONT_ORDER, MODES):
        want_t = full_theme(palette(pn), fn, mn)
        got = merge(base, cdiff[pn], fdiff[fn], mdiff[mn])
        for view, els in want_t.views.items():
            for key, e in els.items():
                assert got.views[view][key]["props"] == e["props"], (pn, fn, mn, view, key)

    write("_inc/main.xml", render(base, "Volta: every view with its default values"))
    for n, d, _ in PALETTES:
        write(f"_inc/color-{n}.xml", render(cdiff[n], f"Colour scheme {d}", with_extra=False))
    for n in FONT_ORDER:
        write(f"_inc/font-{n}.xml", render(fdiff[n], f"Font size {n}", with_extra=False))
    for n in MODES:
        write(f"_inc/system-{n}.xml", render(mdiff[n], f"System carousel {MODE_NAMES[n]}", with_extra=False))
