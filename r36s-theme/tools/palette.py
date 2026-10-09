"""Color schemes. Each scheme becomes one entry of the "COLOR SCHEME" theme option."""

# Accent swatches (also used to bake per-accent switches, boot logos, launch screens)
ACCENTS = {
    "red": "FF2E43",
    "blue": "2F7BFF",
    "amber": "FFB020",
    "green": "2EDB78",
    "violet": "9B5CFF",
    "pink": "FF3EA5",
    "cyan": "1FCFEA",
    "red-deep": "DC1E35",
    "blue-deep": "1F5FE0",
    "violet-deep": "7438EE",
    "teal-deep": "0E9C8E",
}

DARK = dict(
    bg="07070A", pattern="FFFFFF14", radial="40", vignette="000000D0",
    text="F3F3F7", list="D2D2DA", dim="8E8E9C", muted="55555F",
    panel="12121AF0", panelEdge="FFFFFF14", helpBar="0B0B10F5", helpText="A9A9B6",
    selText="FFFFFF", menuBg="111118", menuSep="FFFFFF14", off="dark",
)
LIGHT = dict(
    bg="E9EAEF", pattern="20203018", radial="30", vignette="00000026",
    text="15151C", list="2A2A34", dim="5E5E6C", muted="9A9AA8",
    panel="FFFFFFF0", panelEdge="0000001A", helpBar="FFFFFFF5", helpText="4A4A57",
    selText="FFFFFF", menuBg="FBFBFD", menuSep="00000014", off="light",
)


def _cs(name, display, base, accent_key, multi=False):
    d = dict(base)
    d.update(name=name, display=display, dark=base is DARK, multi=multi,
             accentKey=accent_key, accent=ACCENTS[accent_key])
    return d


COLORSETS = [
    _cs("dark-red", "DARK · NEON RED", DARK, "red"),
    _cs("dark-blue", "DARK · ELECTRIC BLUE", DARK, "blue"),
    _cs("dark-amber", "DARK · AMBER GOLD", DARK, "amber"),
    _cs("dark-green", "DARK · TOXIC GREEN", DARK, "green"),
    _cs("dark-violet", "DARK · ULTRA VIOLET", DARK, "violet"),
    _cs("dark-pink", "DARK · HOT PINK", DARK, "pink"),
    _cs("dark-cyan", "DARK · ICE CYAN", DARK, "cyan"),
    _cs("dark-multi", "DARK · MULTICOLOR (PER SYSTEM)", DARK, "red", multi=True),
    _cs("light-red", "LIGHT · CRIMSON", LIGHT, "red-deep"),
    _cs("light-blue", "LIGHT · COBALT", LIGHT, "blue-deep"),
    _cs("light-violet", "LIGHT · GRAPE", LIGHT, "violet-deep"),
    _cs("light-teal", "LIGHT · TEAL", LIGHT, "teal-deep"),
    _cs("light-multi", "LIGHT · MULTICOLOR (PER SYSTEM)", LIGHT, "red-deep", multi=True),
]
