"""System catalogue: theme folder -> artwork, logo design and spec sheet.

Folder names follow the <theme> tags used by ArkOS / AmberELEC / ROCKNIX
es_systems.cfg on the R36S. Several folders share artwork (e.g. genesis and
megadrive) but keep their own regional logo.
"""

# key: (art, logo, info)
#   logo = dict(main, top=None, sub=None, style=[...])
#   info = (maker, year, kind, cpu, media, tagline)

S = {}


def add(folders, art, main, top=None, sub=None, style=("solid",), info=None, short=None):
    for f in folders.split():
        S[f] = dict(art=art, logo=dict(main=main, top=top, sub=sub, style=list(style)), info=info,
                    short=short or folders.split()[0].upper())


# ---------------------------------------------------------------- Nintendo
add("nes", "nes", "NES", top="NINTENDO", sub="ENTERTAINMENT SYSTEM", style=("box",),
    info=("Nintendo", "1985", "Home console", "8-bit Ricoh 2A03", "Cartridge", "Blow on the cartridge."))
add("famicom", "famicom", "FAMICOM", top="FAMILY COMPUTER", style=("shadow",),
    info=("Nintendo", "1983", "Home console", "8-bit Ricoh 2A03", "Cartridge", "Red & white since '83."))
add("fds", "fds", "DISK SYSTEM", top="FAMICOM", style=("stripes",),
    info=("Nintendo", "1986", "Console add-on", "8-bit Ricoh 2A03", "Quick Disk", "Flip to side B."))
add("snes", "snes", "SNES", top="SUPER NINTENDO", sub="ENTERTAINMENT SYSTEM", style=("italic", "shadow"),
    info=("Nintendo", "1991", "Home console", "16-bit 65C816", "Cartridge", "Mode 7 engaged."))
add("sfc superfamicom", "sfc", "SUPER FAMICOM", style=("italic", "shadow"),
    info=("Nintendo", "1990", "Home console", "16-bit 65C816", "Cartridge", "Four colourful buttons."))
add("satellaview", "sfc", "SATELLAVIEW", top="BS-X", style=("italic",),
    info=("Nintendo", "1995", "Satellite add-on", "16-bit 65C816", "Broadcast", "Live from orbit."))
add("sufami", "sfc", "SUFAMI TURBO", style=("italic",),
    info=("Bandai", "1996", "SFC add-on", "16-bit 65C816", "Mini cart", "Two carts, one turbo."))
add("n64 nintendo64", "n64", "N64", top="NINTENDO", style=("outline", "italic"),
    info=("Nintendo", "1996", "Home console", "64-bit NEC VR4300", "Cartridge", "Hold the middle grip."))
add("n64dd", "n64", "64DD", top="NINTENDO", style=("outline", "italic"),
    info=("Nintendo", "1999", "Console add-on", "64-bit NEC VR4300", "Magnetic disk", "Japan-only drive."))
add("gb", "gb", "GAME BOY", style=("italic",), sub="DOT MATRIX WITH STEREO SOUND",
    info=("Nintendo", "1989", "Handheld", "8-bit Sharp LR35902", "Cartridge", "Four shades of green."))
add("gbc", "gbc", "GAME BOY", sub="C O L O R", style=("italic", "shadow"),
    info=("Nintendo", "1998", "Handheld", "8-bit Sharp LR35902", "Cartridge", "Now in 56 colours."))
add("gba", "gba", "GAME BOY", sub="A D V A N C E", style=("italic", "outline"),
    info=("Nintendo", "2001", "Handheld", "32-bit ARM7TDMI", "Cartridge", "Wide and widescreen."))
add("nds", "nds", "DS", top="NINTENDO", sub="DUAL SCREEN", style=("box",),
    info=("Nintendo", "2004", "Handheld", "ARM9 + ARM7", "Game card", "Two screens, one stylus."))
add("virtualboy", "virtualboy", "VIRTUAL BOY", style=("stripes", "italic"),
    info=("Nintendo", "1995", "Stereoscopic", "32-bit NEC V810", "Cartridge", "Look into the red."))
add("pokemini", "pokemini", "POKeMON MINI", style=("box",),
    info=("Nintendo", "2001", "Handheld", "8-bit S1C88", "Cartridge", "Shake to play."))
add("gameandwatch gw", "gameandwatch", "GAME & WATCH", style=("outline",),
    info=("Nintendo", "1980", "LCD handheld", "4-bit Sharp SM5", "Built-in", "Tells the time, too."))

# --------------------------------------------------------------------- Sega
add("sg-1000 sg1000", "sg1000", "SG-1000", top="SEGA", style=("stripes",),
    info=("Sega", "1983", "Home console", "8-bit Z80", "Cartridge", "Where it all started."))
add("mastersystem sms", "mastersystem", "MASTER SYSTEM", style=("stripes",),
    info=("Sega", "1986", "Home console", "8-bit Z80", "Card / Cart", "The power base."))
add("megadrive", "genesis", "MEGA DRIVE", sub="16-BIT", style=("outline", "italic"),
    info=("Sega", "1988", "Home console", "16-bit 68000", "Cartridge", "Blast processing!"))
add("genesis", "genesis", "GENESIS", sub="16-BIT", style=("outline", "italic"),
    info=("Sega", "1989", "Home console", "16-bit 68000", "Cartridge", "Genesis does what..."))
add("segacd", "segacd", "SEGA CD", style=("outline", "italic"),
    info=("Sega", "1992", "Console add-on", "68000 @ 12.5MHz", "CD-ROM", "Full motion video!"))
add("megacd", "segacd", "MEGA-CD", style=("outline", "italic"),
    info=("Sega", "1991", "Console add-on", "68000 @ 12.5MHz", "CD-ROM", "Spin that disc."))
add("sega32x 32x", "sega32x", "32X", top="SEGA", style=("outline", "italic"),
    info=("Sega", "1994", "Console add-on", "2x SH-2", "Cartridge", "The mushroom of power."))
add("saturn", "saturn", "SATURN", top="SEGA", style=("stripes",),
    info=("Sega", "1994", "Home console", "2x SH-2", "CD-ROM", "Six buttons. Pure arcade."))
add("dreamcast dc", "dreamcast", "DREAMCAST", style=("italic",),
    info=("Sega", "1998", "Home console", "Hitachi SH-4", "GD-ROM", "It's thinking."))
add("gamegear gg", "gamegear", "GAME GEAR", top="SEGA", style=("box",),
    info=("Sega", "1990", "Handheld", "8-bit Z80", "Cartridge", "Six AAs of colour."))

# --------------------------------------------------------------------- Sony
add("psx ps1 playstation", "psx", "PLAYSTATION", style=("shadow",),
    info=("Sony", "1994", "Home console", "32-bit R3000A", "CD-ROM", "Insert disc 2."))
add("psp", "psp", "PSP", style=("outline",), sub="PORTABLE",
    info=("Sony", "2004", "Handheld", "MIPS R4000 x2", "UMD", "Console in your pocket."))
add("pspminis", "psp", "PSP minis", style=("outline",),
    info=("Sony", "2009", "Digital titles", "MIPS R4000 x2", "Download", "Small games, big fun."))

# ---------------------------------------------------------------------- NEC
add("pcengine pce", "pcengine", "PC ENGINE", style=("stripes",),
    info=("NEC / Hudson", "1987", "Home console", "8-bit HuC6280", "HuCard", "Tiny box, big sprites."))
add("tg16 turbografx turbografx16", "tg16", "TURBOGRAFX-16", style=("stripes", "italic"),
    info=("NEC", "1989", "Home console", "8-bit HuC6280", "TurboChip", "Turbo-charged."))
add("pcenginecd pcecd", "pcenginecd", "CD-ROM2", top="PC ENGINE", style=("stripes",),
    info=("NEC / Hudson", "1988", "Console add-on", "8-bit HuC6280", "CD-ROM", "The first CD console."))
add("tg-cd tg16cd turbografxcd", "pcenginecd", "TURBOGRAFX-CD", style=("stripes", "italic"),
    info=("NEC", "1989", "Console add-on", "8-bit HuC6280", "CD-ROM", "Redbook rock."))
add("supergrafx sgfx", "supergrafx", "SUPERGRAFX", style=("stripes",),
    info=("NEC", "1989", "Home console", "8-bit HuC6280", "HuCard", "Double the video chips."))
add("pcfx pc-fx", "pcfx", "PC-FX", style=("box",),
    info=("NEC", "1994", "Home console", "32-bit V810", "CD-ROM", "Anime in a tower."))

# ---------------------------------------------------------------------- SNK
add("neogeo", "neogeo", "NEO-GEO", sub="MAX 330 MEGA", style=("outline", "italic"),
    info=("SNK", "1990", "Arcade at home", "68000 + Z80", "Cartridge", "Max 330 Mega. Pro gear."))
add("neocd neogeocd", "neogeo", "NEO-GEO CD", style=("outline", "italic"),
    info=("SNK", "1994", "Home console", "68000 + Z80", "CD-ROM", "Long loads, great games."))
add("ngp", "ngp", "NEOGEO POCKET", style=("italic",),
    info=("SNK", "1998", "Handheld", "16-bit TLCS-900H", "Cartridge", "Click that stick."))
add("ngpc", "ngpc", "NEOGEO POCKET", sub="C O L O R", style=("italic",),
    info=("SNK", "1999", "Handheld", "16-bit TLCS-900H", "Cartridge", "Clicky stick, in colour."))

# -------------------------------------------------------------------- Atari
add("atari2600", "atari2600", "ATARI 2600", style=("stripes",),
    info=("Atari", "1977", "Home console", "8-bit 6507", "Cartridge", "Woodgrain forever."))
add("atari5200", "atari5200", "ATARI 5200", style=("stripes",),
    info=("Atari", "1982", "Home console", "8-bit 6502C", "Cartridge", "SuperSystem."))
add("atari7800", "atari7800", "ATARI 7800", style=("stripes",),
    info=("Atari", "1986", "Home console", "8-bit 6502C", "Cartridge", "ProSystem."))
add("atari800 atarixe", "atari800", "ATARI 800", style=("stripes",),
    info=("Atari", "1979", "Home computer", "8-bit 6502B", "Cart / Disk", "READY"))
add("atarilynx lynx", "atarilynx", "LYNX", top="ATARI", style=("box", "italic"),
    info=("Atari", "1989", "Handheld", "8-bit 65C02", "Card", "First colour handheld."))
add("atarist", "atarist", "ATARI ST", style=("stripes",),
    info=("Atari", "1985", "Home computer", "16-bit 68000", "Floppy", "Power without the price."))
add("atarijaguar jaguar", "atarijaguar", "JAGUAR", top="ATARI", sub="64-BIT", style=("italic", "shadow"),
    info=("Atari", "1993", "Home console", "Tom & Jerry", "Cartridge", "Do the math."))

# ------------------------------------------------------------------- Bandai
add("wonderswan ws", "wonderswan", "WonderSwan", style=("italic",),
    info=("Bandai", "1999", "Handheld", "16-bit NEC V30MZ", "Cartridge", "Play it sideways."))
add("wonderswancolor wsc", "wonderswancolor", "WonderSwan", sub="C O L O R", style=("italic",),
    info=("Bandai", "2000", "Handheld", "16-bit NEC V30MZ", "Cartridge", "One AA. Many hours."))

# ------------------------------------------------------------- other gear
add("coleco colecovision", "coleco", "COLECOVISION", style=("shadow",),
    info=("Coleco", "1982", "Home console", "8-bit Z80A", "Cartridge", "Arcade quality, '82."))
add("intellivision", "intellivision", "INTELLIVISION", style=("shadow",),
    info=("Mattel", "1979", "Home console", "16-bit CP1610", "Cartridge", "Intelligent television."))
add("vectrex", "vectrex", "VECTREX", style=("outline",),
    info=("GCE / MB", "1982", "Vector console", "8-bit 6809", "Cartridge", "Built-in vector screen."))
add("videopac odyssey2 o2em", "odyssey2", "ODYSSEY2", style=("stripes",),
    info=("Magnavox / Philips", "1978", "Home console", "8-bit 8048", "Cartridge", "Selectgame!"))
add("channelf", "channelf", "CHANNEL F", style=("stripes",),
    info=("Fairchild", "1976", "Home console", "8-bit F8", "Videocart", "The very first cart."))
add("supervision", "supervision", "SUPERVISION", style=("box",),
    info=("Watara", "1992", "Handheld", "8-bit 65SC02", "Cartridge", "Bendy neck, big screen."))
add("arduboy", "arduboy", "ARDUBOY", style=("box",),
    info=("Arduboy", "2016", "Credit-card handheld", "8-bit ATmega32u4", "Flash", "Open source fun."))
add("uzebox", "uzebox", "UZEBOX", style=("stripes",),
    info=("Belogic", "2008", "DIY console", "8-bit ATmega644", "SD card", "Solder it yourself."))
add("3do", "3do", "3DO", style=("outline", "italic"),
    info=("Panasonic / 3DO", "1993", "Home console", "32-bit ARM60", "CD-ROM", "Interactive multiplayer."))

# ---------------------------------------------------------------- computers
add("c64 commodore64", "c64", "COMMODORE 64", style=("stripes",),
    info=("Commodore", "1982", "Home computer", "8-bit 6510", "Tape / Disk", "LOAD\"*\",8,1"))
add("amiga amiga500 amiga1200", "amiga", "AMIGA", style=("italic", "shadow"),
    info=("Commodore", "1985", "Home computer", "16-bit 68000", "Floppy", "Insert Workbench disk."))
add("amigacd32 cd32", "amiga", "AMIGA CD32", style=("italic", "shadow"),
    info=("Commodore", "1993", "Home console", "32-bit 68EC020", "CD-ROM", "32 bits of Amiga."))
add("amstradcpc cpc", "amstradcpc", "AMSTRAD CPC", style=("stripes",),
    info=("Amstrad", "1984", "Home computer", "8-bit Z80A", "Tape / Disk", "Ready."))
add("msx msx1", "msx", "MSX", style=("box",),
    info=("Microsoft / ASCII", "1983", "Home computer", "8-bit Z80A", "Cart / Disk", "One standard, many brands."))
add("msx2 msx2plus", "msx2", "MSX2", style=("box",),
    info=("Microsoft / ASCII", "1985", "Home computer", "8-bit Z80A", "Cart / Disk", "More colours, more VRAM."))
add("zxspectrum zx", "zxspectrum", "ZX SPECTRUM", style=("stripes", "italic"),
    info=("Sinclair", "1982", "Home computer", "8-bit Z80A", "Tape", "Rubber keys, big heart."))
add("x68000", "x68000", "X68000", style=("outline",),
    info=("Sharp", "1987", "Home computer", "16-bit 68000", "Floppy", "The arcade at home."))
add("apple2 appleii", "apple2", "APPLE ][", style=("shadow",),
    info=("Apple", "1977", "Home computer", "8-bit 6502", "Floppy", "]RUN"))
add("dos pc msdos", "dos", "MS-DOS", style=("box",),
    info=("IBM PC compatible", "1981", "Personal computer", "x86", "Floppy / CD", "C:\\>_"))

# ------------------------------------------------------------------- arcade
add("arcade", "arcade", "ARCADE", style=("outline", "italic"),
    info=("Various", "1971+", "Coin-op", "Many", "PCB", "Insert coin."))
add("mame mame2003 mame2003plus mame2010 mame2003-plus advmame", "mame", "MAME", style=("outline", "italic"),
    info=("MAME team", "1997", "Arcade emulator", "Many", "ROM set", "Multiple Arcade Machine."))
add("fbneo fba finalburn", "fbneo", "FINALBURN NEO", style=("outline", "italic"),
    info=("FBNeo team", "2019", "Arcade emulator", "Many", "ROM set", "Burning since 2000."))
add("cps1 cps2 cps3 cps", "cps", "CAPCOM CPS", style=("outline", "italic"),
    info=("Capcom", "1988", "Arcade board", "68000 + Z80", "PCB", "Hadouken optional."))
add("naomi atomiswave", "naomi", "NAOMI", style=("outline", "italic"),
    info=("Sega / Sammy", "1998", "Arcade board", "Hitachi SH-4", "PCB", "Dreamcast in a cab."))

# ------------------------------------------------------------ engines etc.
add("scummvm", "scummvm", "SCUMMVM", style=("box",),
    info=("ScummVM team", "2001", "Game engine", "-", "Data files", "Use key on door."))
add("easyrpg", "easyrpg", "EASYRPG", style=("shadow",),
    info=("EasyRPG team", "2007", "RPG engine", "-", "Project", "A slime draws near!"))
add("pico-8 pico8", "pico8", "PICO-8", style=("box",),
    info=("Lexaloffle", "2015", "Fantasy console", "Lua", "PNG cart", "128x128, 16 colours."))
add("tic80 tic-80", "tic80", "TIC-80", style=("box",),
    info=("Nesbox", "2017", "Fantasy console", "Lua", "Cart", "240x136 tiny computer."))
add("openbor", "openbor", "OPENBOR", style=("outline", "italic"),
    info=("OpenBOR team", "2005", "Beat 'em up engine", "-", "PAK", "Streets of pixels."))
add("ports", "ports", "PORTS", style=("box",),
    info=("Community", "-", "Native ports", "ARM64", "Folder", "Native, no emulation."))
add("doom prboom", "doom", "DOOM", style=("outline",),
    info=("id Software", "1993", "FPS engine", "-", "WAD", "Rip and tear."))
add("quake", "doom", "QUAKE", style=("outline",),
    info=("id Software", "1996", "FPS engine", "-", "PAK", "Into the slipgate."))
add("solarus", "solarus", "SOLARUS", style=("shadow",),
    info=("Solarus team", "2006", "Action-RPG engine", "-", "Quest", "It's dangerous to go alone."))
add("wasm4", "wasm4", "WASM-4", style=("box",),
    info=("Aduros", "2021", "Fantasy console", "WebAssembly", "Cart", "160x160, 4 colours."))
add("love lovegames lowresnx", "default", "LOVE2D", style=("box",),
    info=("Community", "-", "Lua games", "-", "Folder", "Made with love."))

# -------------------------------------------------------------- collections
add("retropie tools options settings system", "tools", "OPTIONS", style=("box",),
    info=("DeskOS", "-", "Control panel", "-", "-", "Tweak all the things."), short="OPTIONS")
add("favorites auto-favorites", "favorites", "FAVORITES", style=("shadow",),
    info=("You", "-", "Collection", "-", "-", "Your all-time best."), short="FAVES")
add("lastplayed auto-lastplayed recent", "lastplayed", "LAST PLAYED", style=("shadow",),
    info=("You", "-", "Collection", "-", "-", "Pick up where you left."), short="RECENT")
add("all auto-allgames allgames", "allgames", "ALL GAMES", style=("shadow",),
    info=("You", "-", "Collection", "-", "-", "Everything, everywhere."), short="ALL")
add("custom-collections collections", "allgames", "COLLECTIONS", style=("shadow",),
    info=("You", "-", "Collection", "-", "-", "Curated by you."), short="COLLECT")

DEFAULT = dict(art="default", logo=dict(main="DESKOS", top=None, sub="GAME SYSTEM", style=["box"]),
               info=("Unknown", "-", "Game system", "-", "-", "New disk detected."), short="SYSTEM")
