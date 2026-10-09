"""System catalog for the NeonGlow theme.

Every entry produces a `<theme folder>/theme.xml` in the built theme, so ES
finds a theme for that system.  Theme folder names come from the dArkOS /
ArkOS `es_systems.cfg` (<theme> tag) plus common aliases used by other
ArkOS builds and by ES-fcamod auto collections.

Fields:
  logo  - logo key in the Carbon logo pack (art/logos/<key>.svg|png),
          or None to draw a typographic wordmark instead
  mark  - wordmark text used when logo is None (and as fallback)
  color - glow color (hex) for the multicolor schemes; None = derive it
          from the logo's dominant saturated color
"""

S = {}


def add(theme, logo=None, mark=None, color=None):
    S[theme] = dict(logo=logo, mark=mark or theme.upper(), color=color)


# --- Nintendo -------------------------------------------------------------
add("nes", "nes", "NES", "E4282D")
add("famicom", "famicom", "FAMICOM", "D9283A")
add("fds", "fds", "FDS", "F2B91C")
add("nes-hacks", "nesh", "NES HACKS", "E4282D")
add("nesh", "nesh", "NES HACKS", "E4282D")
add("snes", "snes", "SNES", "6A5BFF")
add("sfc", "sfc", "SFC", "8E5BFF")
add("snes-hacks", "snesh", "SNES HACKS", "4CC36B")
add("snesh", "snesh", "SNES HACKS", "4CC36B")
add("snesmsu1", "snes-msu1", "MSU-1", "D63A3A")
add("satellaview", "satellaview", "BS-X", "3E8BFF")
add("sufami", "sufami", "SUFAMI", "E8B21E")
add("n64", "n64", "N64", "2FA84F")
add("n64dd", "n64dd", "64DD", "7B4DFF")
add("gb", "gb", "GAME BOY", "86B53A")
add("gbc", "gbc", "GBC", "1FB5C9")
add("gba", "gba", "GBA", "5B3FD9")
add("gb-hacks", "gbh", "GB HACKS", "3FB85A")
add("gbh", "gbh", "GB HACKS", "3FB85A")
add("gbc-hacks", "gbch", "GBC HACKS", "2BBF7A")
add("gbch", "gbch", "GBC HACKS", "2BBF7A")
add("gba-hacks", "gbah", "GBA HACKS", "7A4CFF")
add("gbah", "gbah", "GBA HACKS", "7A4CFF")
add("gb2players", "gb2players", "GB 2P", "1FB5C9")
add("gbc2players", "gbc2players", "GBC 2P", "C13BE0")
add("sgb", "sgb", "SGB", "E04B4B")
add("nds", "nds", "NDS", "18A5A0")
add("virtualboy", "virtualboy", "VIRTUAL BOY", "E0182D")
add("gameandwatch", "gameandwatch", "GAME & WATCH", "E8A31E")
add("pokemonmini", "pokemini", "POKÉMON MINI", "F2C21C")
add("pokemini", "pokemini", "POKÉMON MINI", "F2C21C")
add("gc", "gc", "GAMECUBE", "6A4CFF")

# --- Sega -----------------------------------------------------------------
add("genesis", "genesis", "GENESIS", "3F5BFF")
add("megadrive", "megadrive-japan", "MEGA DRIVE", "E02A35")
add("genh", "genh", "GEN HACKS", "2FB85A")
add("genesis-hacks", "genh", "GEN HACKS", "2FB85A")
add("msumd", "msu-md", "MSU-MD", "D9283A")
add("mastersystem", "mastersystem", "MASTER SYSTEM", "E32B2B")
add("gamegear", "gamegear", "GAME GEAR", "2F6BFF")
add("segacd", "segacd", "SEGA CD", "2F6BFF")
add("megacd", "megacd", "MEGA CD", "2F6BFF")
add("sega32x", "sega32x", "32X", "E8B21E")
add("saturn", "saturn", "SATURN", "4E7BFF")
add("dreamcast", "dreamcast", "DREAMCAST", "F26B1F")
add("vmu", None, "VMU", "F26B1F")
add("sg-1000", "sg-1000", "SG-1000", "3F7BFF")
add("pico", "pico", "PICO", "2FA8F2")
add("naomi", "naomi", "NAOMI", "E8A31E")
add("atomiswave", "atomiswave", "ATOMISWAVE", "2F8BFF")

# --- Sony -----------------------------------------------------------------
add("psx", "psx", "PLAYSTATION", "5C7CFF")
add("psp", "psp", "PSP", "2F8BFF")
add("pspminis", "pspminis", "PSP MINIS", "2FB5F2")
add("ps2", "ps2", "PS2", "3F5BFF")

# --- NEC / Hudson ---------------------------------------------------------
add("pcengine", "pcengine", "PC ENGINE", "E0242D")
add("pcenginecd", "pcenginecd", "PCE CD", "C13BE0")
add("tg16", "tg16", "TG-16", "F2771C")
add("turbografx", "tg16", "TG-16", "F2771C")
add("tg-cd", "tg-cd", "TG-CD", "F2771C")
add("supergrafx", "supergrafx", "SUPERGRAFX", "8E5BFF")
add("pcfx", "pcfx", "PC-FX", "E8A31E")
add("pc98", "pc98", "PC-98", "E02A35")
add("pc88", "pc88", "PC-88", "E0249A")

# --- SNK ------------------------------------------------------------------
add("neogeo", "neogeo", "NEO GEO", "D9A21E")
add("neogeocd", "neogeocd", "NEO GEO CD", "D9A21E")
add("ngp", "ngp", "NGP", "3F8BFF")
add("ngpc", "ngpc", "NGPC", "E0242D")

# --- Arcade ---------------------------------------------------------------
add("arcade", "arcade", "ARCADE", "F2B21C")
add("mame", "mame", "MAME", "2FA8F2")
add("mame2003", "mame", "MAME 2003", "2FA8F2")
add("mame2003plus", "mame", "MAME 2003+", "2FA8F2")
add("mame2010", "mame", "MAME 2010", "2F8BF2")
add("mame2000", "mame", "MAME 2000", "2FA8F2")
add("fbneo", "fbneo", "FBNEO", "E0502A")
add("fba", "fba", "FBA", "E0502A")
add("cps1", "cps1", "CPS-1", "2F6BFF")
add("cps2", "cps2", "CPS-2", "2F6BFF")
add("cps3", "cps3", "CPS-3", "2F6BFF")
add("daphne", "daphne", "DAPHNE", "E8B21E")
add("alg", "alg", "ALG", "E03A2A")
add("mess", "mess", "MESS", "F29E1C")

# --- Atari ----------------------------------------------------------------
add("atari2600", "atari2600", "ATARI 2600", "E0242D")
add("atari5200", "atari5200", "ATARI 5200", "2F6BFF")
add("atari7800", "atari7800", "ATARI 7800", "E05A1F")
add("atari800", "atari800", "ATARI 800", "E05A1F")
add("atarixegs", "xegs", "XEGS", "8E5BFF")
add("atarist", "atarist", "ATARI ST", "2FB85A")
add("atarijaguar", "atarijaguar", "JAGUAR", "E0242D")
add("atarilynx", "atarilynx", "LYNX", "E8C21E")

# --- Bandai / handhelds ---------------------------------------------------
add("wonderswan", "wonderswan", "WONDERSWAN", "E0242D")
add("wonderswancolor", "wonderswancolor", "WS COLOR", "2F8BFF")
add("megaduck", "megaduck", "MEGA DUCK", "1FC9C9")
add("supervision", "supervision", "SUPERVISION", "4CC36B")
add("advision", "advision", "ADVISION", "E0242D")
add("microvision", None, "MICROVISION", "8E5BFF")
add("gametank", None, "GAMETANK", "2FB85A")
add("arduboy", "arduboy", "ARDUBOY", "1FC9C9")
add("palm", "palm", "PALM", "2F8BFF")
add("piece", None, "P/ECE", "E8A31E")

# --- Consoles (misc) ------------------------------------------------------
add("3do", "3do", "3DO", "E8C21E")
add("intellivision", "intellivision", "INTV", "E8A31E")
add("colecovision", "colecovision", "COLECO", "2F6BFF")
add("coleco", "coleco", "COLECO", "2F6BFF")
add("vectrex", "vectrex", "VECTREX", "E0242D")
add("odyssey2", "odyssey2", "ODYSSEY²", "E05A1F")
add("videopac", "videopac", "VIDEOPAC", "2F8BFF")
add("channelf", "channelf", "CHANNEL F", "E8A31E")
add("astrocade", "astrocade", "ASTROCADE", "E05A1F")
add("scv", "scv", "SCV", "E0242D")
add("uzebox", "uzebox", "UZEBOX", "2FB85A")
add("vircon32", "vircon32", "VIRCON32", "1FC9C9")
add("cdi", "cdi", "CD-i", "8E5BFF")

# --- Computers ------------------------------------------------------------
add("amiga", "amiga", "AMIGA", "E05A1F")
add("amigacd32", "amigacd32", "CD32", "E0242D")
add("amstradcpc", "amstradcpc", "CPC", "2FB85A")
add("gx4000", "gx4000", "GX4000", "E8C21E")
add("apple2", "apple2", "APPLE II", "4CC36B")
add("vmac", "macintosh", "MACINTOSH", "8E9BB0")
add("macintosh", "macintosh", "MACINTOSH", "8E9BB0")
add("bbcmicro", "bbcmicro", "BBC MICRO", "E0242D")
add("c16", "c16", "C16", "2F8BFF")
add("c64", "c64", "C64", "6A5BFF")
add("c128", "c128", "C128", "2F6BFF")
add("vic20", "vic20", "VIC-20", "E05A1F")
add("msx", "msx", "MSX", "2F6BFF")
add("msx1", "msx1", "MSX", "2F6BFF")
add("msx2", "msx2", "MSX2", "2F6BFF")
add("zx81", "zx81", "ZX81", "E0242D")
add("zxspectrum", "zxspectrum", "ZX SPECTRUM", "E0242D")
add("x1", "x1", "SHARP X1", "E0242D")
add("x68000", "x68000", "X68000", "8E9BB0")
add("msdos", None, "MS-DOS", "2FB85A")
add("dos", None, "MS-DOS", "2FB85A")
add("pc", "pc", "PC", "2FB85A")
add("ti99", "ti99", "TI-99", "E0242D")
add("thomson", "thomson", "THOMSON", "2F8BFF")
add("dragon32", "dragon32", "DRAGON 32", "E0242D")
add("coco", "coco", "COCO", "4CC36B")
add("e128", "enterprise", "ENTERPRISE", "E8A31E")
add("tvc", None, "TVC", "E05A1F")

# --- Engines / ports / fantasy consoles ------------------------------------
add("ports", "ports", "PORTS", "F2771C")
add("openbor", "openbor", "OPENBOR", "E0242D")
add("scummvm", "scummvm", "SCUMMVM", "6CC21E")
add("doom", "prboom", "DOOM", "E0242D")
add("wolf", "ecwolf", "WOLF3D", "8E9BB0")
add("cavestory", "cavestory", "CAVE STORY", "E0242D")
add("easyrpg", "easyrpg", "EASYRPG", "4CC36B")
add("solarus", "solarus", "SOLARUS", "E8A31E")
add("love2d", "love", "LÖVE", "E0249A")
add("lutro", "lutro", "LUTRO", "E8A31E")
add("pico-8", "pico8", "PICO-8", "FF2E7A")
add("pico8", "pico8", "PICO-8", "FF2E7A")
add("tic80", "tic80", "TIC-80", "2FB85A")
add("wasm4", "wasm4", "WASM-4", "8E5BFF")
add("lowresnx", "lowresnx", "LOWRES NX", "E0249A")
add("puzzlescript", None, "PUZZLE SCRIPT", "8E5BFF")
add("onscripter", None, "ONS", "E0242D")
add("j2me", "j2me", "J2ME", "E05A1F")
add("vhs", None, "VIDEOS", "8E9BB0")
add("retroarch", None, "RETROARCH", "8E9BB0")

# --- Tools / collections ---------------------------------------------------
add("options", None, "OPTIONS", "8E9BB0")
add("tools", None, "TOOLS", "8E9BB0")
add("retropie", None, "OPTIONS", "8E9BB0")
add("setup", "setup", "SETUP", "8E9BB0")
add("auto-favorites", "auto-favorites", "FAVORITES", "F2B21C")
add("favorites", "auto-favorites", "FAVORITES", "F2B21C")
add("auto-lastplayed", "auto-lastplayed", "RECENT", "1FC9C9")
add("recent", "auto-lastplayed", "RECENT", "1FC9C9")
add("auto-allgames", "auto-allgames", "ALL GAMES", "6A5BFF")
add("all", "auto-allgames", "ALL GAMES", "6A5BFF")
add("auto-at2players", "auto-at2players", "2 PLAYERS", "2FB85A")
add("auto-at4players", "auto-at4players", "4 PLAYERS", "E05A1F")
add("auto-neverplayed", "auto-neverplayed", "NEVER PLAYED", "8E9BB0")
add("custom-collections", "custom-collections", "COLLECTIONS", "E0249A")
add("collections", "custom-collections", "COLLECTIONS", "E0249A")

# --- Arcade manufacturer collections (ES-fcamod "arcade systems") ----------
for _m, _c in (("acclaim", "2F8BFF"), ("atari", "E0242D"), ("atlus", "E8A31E"), ("banpresto", "E8C21E"),
               ("capcom", "2F6BFF"), ("cave", "E0242D"), ("irem", "E0242D"), ("jaleco", "2F8BFF"),
               ("kaneko", "E05A1F"), ("konami", "E0242D"), ("midway", "8E9BB0"), ("namco", "E0242D"),
               ("nintendo", "E0242D"), ("sammy", "2F8BFF"), ("sega", "2F6BFF"), ("snk", "2F8BFF"),
               ("taito", "2F8BFF"), ("tecmo", "2F8BFF")):
    add(_m, _m, _m.upper(), _c)
add("psiko", "psikyo", "PSIKYO", "E8A31E")
add("psikyo", "psikyo", "PSIKYO", "E8A31E")

SYSTEMS = S
