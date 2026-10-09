"""Colour schemes ("colorsets") for the Volta theme.

Every scheme defines the same tokens. CSS values feed the rendered artwork,
hex values (no '#') feed the theme XML. Keep `dark`/`light` pairs visually
related so switching mode keeps the personality of the accent.

Tokens
  bg, bg2        page background (gradient from bg2 at the top to bg)
  glowA, glowB   large soft ambient blobs behind the panels
  dot            faint dot-grid colour (rgba)
  panelA/B       graphite tile gradient (Assist Limit card in the reference)
  well           darker inset behind box art
  cardA/B/C      glossy accent card (Strain / Sync cards in the reference)
  cardEdge       inner rim glow of the accent card
  text, dim      primary / secondary text on the background and panels
  cardText, cardDim  text on the accent card
  accent         highlight colour (the yellow tick/slider in the reference)
  sel1/sel2      list selector gradient, selText = text drawn on it
  logo           tint for the white system logos
  logoCard       tint for logos that sit on the accent card
  star/starOff   rating stars
"""

def _dark(**kw):
    base = dict(
        mode="dark",
        bg="#060607", bg2="#111114",
        glowA="rgba(255,255,255,0.05)", glowB="rgba(255,255,255,0.03)",
        dot="rgba(255,255,255,0.055)",
        panelA="#2c2c31", panelB="#18181b", panelLine="rgba(255,255,255,0.07)",
        well="#0d0d0f",
        text="F4F4F6", dim="8D8D96", faint="55555C",
        cardText="FFFFFF", cardDim="FFFFFFB0",
        logo="F4F4F6", logoCard="FFFFFF",
        shadow="rgba(0,0,0,0.55)",
        status="#1b1b1f",
        menuBg="#1c1c20", menuLine="rgba(255,255,255,0.08)",
    )
    base.update(kw)
    return base


def _light(**kw):
    base = dict(
        mode="light",
        bg="#e7e7eb", bg2="#f6f6f8",
        glowA="rgba(255,255,255,0.9)", glowB="rgba(255,255,255,0.6)",
        dot="rgba(0,0,0,0.06)",
        panelA="#ffffff", panelB="#f1f1f4", panelLine="rgba(0,0,0,0.06)",
        well="#e4e4e9",
        text="141417", dim="6B6B74", faint="A9A9B2",
        cardText="141417", cardDim="141417A8",
        logo="141417", logoCard="141417",
        shadow="rgba(40,40,60,0.18)",
        status="#ffffff",
        menuBg="#ffffff", menuLine="rgba(0,0,0,0.07)",
    )
    base.update(kw)
    return base


PALETTES = [
    # name, display, tokens
    ("volta-dark", "Volta Dark", _dark(
        cardA="#d697e2", cardB="#8b3db5", cardC="#6d1b86", cardEdge="rgba(255,214,255,0.45)",
        accent="F2D21B", sel1="#f6dc3a", sel2="#e2bf0c", selText="111111",
        star="F2D21B", starOff="FFFFFF40")),
    ("volta-light", "Volta Light", _light(
        cardA="#f3dcf7", cardB="#dcb6ec", cardC="#c99be0", cardEdge="rgba(255,255,255,0.9)",
        accent="C9A800", sel1="#f6dc3a", sel2="#ebc614", selText="111111",
        star="D4AE00", starOff="14141730")),

    ("violet-dark", "Violet Dark", _dark(
        bg="#08040c", bg2="#160a1f", glowA="rgba(170,70,210,0.20)", glowB="rgba(120,40,170,0.14)",
        panelA="#2a1c33", panelB="#160e1c", well="#0c0710", status="#1d1324", menuBg="#1e1426",
        cardA="#e3a4ec", cardB="#9445c0", cardC="#701c8c", cardEdge="rgba(255,210,255,0.5)",
        accent="E9A8FF", sel1="#c77dd6", sel2="#7f35a5", selText="FFFFFF",
        dim="9C8AA6", star="F2D21B", starOff="FFFFFF40")),
    ("violet-light", "Violet Light", _light(
        bg="#efe6f4", bg2="#faf6fc", glowA="rgba(214,151,226,0.35)", glowB="rgba(255,255,255,0.8)",
        well="#e6daee",
        cardA="#f6e3fa", cardB="#e2bdf0", cardC="#cf9fe4", cardEdge="rgba(255,255,255,0.9)",
        accent="8E3FB8", sel1="#b866d4", sel2="#8a3cb2", selText="FFFFFF",
        text="25122F", dim="76637F", logo="25122F", logoCard="25122F", cardText="25122F", cardDim="25122FA8",
        star="8E3FB8", starOff="25122F30")),

    ("indigo-dark", "Indigo Dark", _dark(
        bg="#03031a", bg2="#0b0b2c", glowA="rgba(110,98,210,0.22)", glowB="rgba(60,50,170,0.18)",
        panelA="#1b1b3d", panelB="#0d0d24", well="#06061a", status="#13132e", menuBg="#141432",
        cardA="#9f95ee", cardB="#2a2378", cardC="#07072a", cardEdge="rgba(150,140,255,0.75)",
        accent="A99BFF", sel1="#8c7ff0", sel2="#5146c4", selText="FFFFFF",
        dim="8C8AB6", star="F2D21B", starOff="FFFFFF40")),
    ("indigo-light", "Indigo Light", _light(
        bg="#e8e8f8", bg2="#f7f7fe", glowA="rgba(140,130,240,0.30)", glowB="rgba(255,255,255,0.8)",
        well="#dedef3",
        cardA="#eeedff", cardB="#d4d0fb", cardC="#bab3f3", cardEdge="rgba(255,255,255,0.95)",
        accent="4B3FCB", sel1="#6a5ff0", sel2="#4237c0", selText="FFFFFF",
        text="13123A", dim="65648E", logo="13123A", logoCard="13123A", cardText="13123A", cardDim="13123AA8",
        star="4B3FCB", starOff="13123A30")),

    ("aqua-dark", "Aqua Dark", _dark(
        bg="#020c0f", bg2="#06191e", glowA="rgba(40,200,210,0.16)", glowB="rgba(20,120,150,0.14)",
        panelA="#16292d", panelB="#0b171a", well="#050e10", status="#102125", menuBg="#10232a",
        cardA="#7ce6e6", cardB="#178a98", cardC="#0a4c63", cardEdge="rgba(180,255,250,0.5)",
        accent="3BE0D0", sel1="#56ecd9", sel2="#1fbcb8", selText="03181B",
        dim="7FA0A5", star="3BE0D0", starOff="FFFFFF40")),
    ("aqua-light", "Aqua Light", _light(
        bg="#e3f2f3", bg2="#f5fbfb", glowA="rgba(60,200,210,0.28)", glowB="rgba(255,255,255,0.8)",
        well="#d8eaec",
        cardA="#e6fbfa", cardB="#bfeeee", cardC="#98dde2", cardEdge="rgba(255,255,255,0.95)",
        accent="0E8A92", sel1="#22b4b4", sel2="#0b8790", selText="FFFFFF",
        text="0B2427", dim="5B7779", logo="0B2427", logoCard="0B2427", cardText="0B2427", cardDim="0B2427A8",
        star="0E8A92", starOff="0B242730")),

    ("ember-dark", "Ember Dark", _dark(
        bg="#0e0604", bg2="#1d0c07", glowA="rgba(255,110,50,0.18)", glowB="rgba(200,50,30,0.14)",
        panelA="#2f1d18", panelB="#180e0b", well="#0d0705", status="#22140f", menuBg="#24150f",
        cardA="#ffb37a", cardB="#e2512a", cardC="#981d1a", cardEdge="rgba(255,220,180,0.5)",
        accent="FF8A47", sel1="#ff9a52", sel2="#e9592a", selText="1A0904",
        dim="A88E86", star="FFB23E", starOff="FFFFFF40")),
    ("ember-light", "Ember Light", _light(
        bg="#f6ebe5", bg2="#fdf8f5", glowA="rgba(255,150,90,0.28)", glowB="rgba(255,255,255,0.8)",
        well="#efe0d7",
        cardA="#fff0e4", cardB="#ffd2b4", cardC="#f8ae8b", cardEdge="rgba(255,255,255,0.95)",
        accent="D9501E", sel1="#f47a3a", sel2="#d4461b", selText="FFFFFF",
        text="2A120A", dim="85665B", logo="2A120A", logoCard="2A120A", cardText="2A120A", cardDim="2A120AA8",
        star="D9501E", starOff="2A120A30")),

    ("mint-dark", "Mint Dark", _dark(
        bg="#030d08", bg2="#081a11", glowA="rgba(70,220,140,0.15)", glowB="rgba(20,140,90,0.14)",
        panelA="#182b21", panelB="#0c1712", well="#050e09", status="#11221a", menuBg="#12251b",
        cardA="#9af0bf", cardB="#23985d", cardC="#0d5a3a", cardEdge="rgba(200,255,220,0.5)",
        accent="5BE38F", sel1="#74eda2", sel2="#2fc270", selText="03140B",
        dim="80A190", star="5BE38F", starOff="FFFFFF40")),
    ("mint-light", "Mint Light", _light(
        bg="#e5f3eb", bg2="#f6fcf8", glowA="rgba(90,220,150,0.28)", glowB="rgba(255,255,255,0.8)",
        well="#d9ebe0",
        cardA="#eafbf1", cardB="#c3f0d5", cardC="#9bdfb8", cardEdge="rgba(255,255,255,0.95)",
        accent="1E9A5A", sel1="#33bf74", sel2="#178c50", selText="FFFFFF",
        text="0B2416", dim="5A7867", logo="0B2416", logoCard="0B2416", cardText="0B2416", cardDim="0B2416A8",
        star="1E9A5A", starOff="0B241630")),

    ("citrine-pop", "Citrine Pop", _light(
        bg="#f0cf17", bg2="#f7dc3c", glowA="rgba(255,255,255,0.35)", glowB="rgba(255,240,150,0.5)",
        dot="rgba(0,0,0,0.10)",
        panelA="#16161a", panelB="#0b0b0d", panelLine="rgba(255,255,255,0.07)", well="#050506",
        status="#111114", menuBg="#141417", menuLine="rgba(255,255,255,0.08)", panelGlow=0.05,
        cardA="#2b2b31", cardB="#151518", cardC="#0a0a0c", cardEdge="rgba(242,210,27,0.55)",
        accent="F2D21B", sel1="#f6dc3a", sel2="#e2bf0c", selText="111111",
        # text on the yellow background is dark, text inside the black panels is light
        text="F4F4F6", dim="8D8D96", faint="55555C",
        cardText="F4F4F6", cardDim="F4F4F6A8",
        logo="111111", logoCard="F2D21B",
        bgText="111111", bgDim="11111199",
        star="F2D21B", starOff="FFFFFF40", shadow="rgba(60,40,0,0.35)")),
]

for _name, _disp, _p in PALETTES:
    # text drawn straight on the page background (header, help bar, labels)
    _p.setdefault("bgText", _p["text"])
    _p.setdefault("bgDim", _p["dim"])
