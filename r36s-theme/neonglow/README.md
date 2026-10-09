# NeonGlow: EmulationStation theme for the R36S

A dark "deep glow" theme for the **R36S** (and clones) running **ArkOS** or **dArkOS** (EmulationStation-fcamod, 640×480).

![showcase](https://github.com/hossamelqamash-beep/claude/blob/claude/emulationstation-r36s-theme-7xvpy8/r36s-theme/previews/showcase.jpg)

> **v1.2: fixes the EmulationStation restart loop.**
> Earlier versions kept their colours, font sizes and backgrounds in theme *variables* that only the colour/font/background options defined. ES stores those choices in settings it shares with other themes (`ThemeColorSet`, `subset.fontsize`, …). If they still held values from the previous theme (ArkOS ships with `es-theme-nes-box`), no option loaded, the variables stayed empty, and ES aborted (`std::out_of_range`) on opening a game list. systemd then restarted it in a loop.
> v1.2 is rebuilt like the Volta theme that already runs on your device:
> * every view has literal default values in `_inc/main.xml`;
> * each option is a small override listed after the include;
> * no `screen` view, no SVG, no JPEG, no rounded-corner stencil, no tiled textures;
> * nothing is installed outside the theme folder (no boot logo, no loading screen, no installer).

## Install

1. Unzip, then copy the **`neonglow`** folder into the **`themes`** folder of the SD card's **EASYROMS** partition. The result must be `EASYROMS/themes/neonglow/3do/theme.xml`. "Extract all…" sometimes creates `neonglow/neonglow/`; if so, move the inner folder up a level.
2. On the device: **Start → UI Settings → Theme → NEONGLOW**.

## Recovering from v1.0 / v1.1

1. **ES keeps restarting:** put the SD card in a PC and delete `EASYROMS/themes/neonglow` (ES falls back to another theme). Then copy in this version.
2. **v1.0 also replaced the boot logo, launch screen and ES loading screen** (originals saved as `*.neonglow-bak`). To restore them:
   * **Over SSH:** `sudo /roms/themes/neonglow/_scripts/restore-v1.0-files.sh`
   * **From a PC:** on the **BOOT** partition, if `logo.bmp.neonglow-bak` exists, delete `logo.bmp` and rename the backup to `logo.bmp` (same for `logo_kernel.bmp.neonglow-bak`). On EASYROMS, do the same for `launchimages/loading.jpg.neonglow-bak`.

## Theme options

**Start → UI Settings → Theme Configuration**

| Option | Values |
|---|---|
| System list layout | Vertical list + icon *(default)* · Horizontal carousel · Vertical carousel · Wheel |
| Color scheme | Dark: Neon Red *(default)*, Electric Blue, Amber Gold, Toxic Green, Ultra Violet, Hot Pink, Ice Cyan, Multicolor · Light: Crimson, Cobalt, Grape, Teal, Multicolor |
| Font size | Medium *(default)* · Small · Large |
| Background | Dotted *(default)* · Solid · Plus grid |

Each option only overrides a few properties. If ES remembers a setting from another theme, NeonGlow shows its default look instead of breaking.

## Features

* **194 system folders:** every dArkOS/ArkOS system plus aliases, auto collections and arcade-manufacturer collections. Each system has a glowing glass tile built from high-quality vector logos.
* **Multicolor schemes:** the accent follows each system's own glow colour.
* **Gamelist:** game list on the left half. On the right, box art fills the top two thirds and rating, year, genre and description fill the bottom third. Detailed, video, grid and basic views are all themed.
* **Missing box art:** "No artwork" placeholder in each scheme's accent.
* **Settings menu:** themed fonts, colours, selector, switches, slider, buttons and icons.
* **Corners kept clear for the battery:** ArkOS draws the battery and clock itself, so the theme keeps both top corners clear. Some builds put it top-right, the dArkOS 351v build puts it top-left.
* **Fonts:** Barlow Condensed and Barlow (SIL OFL).

## How it was tested

ArkOS's EmulationStation (`christianhaitian/EmulationStation-fcamod`, branch `351v`) was built for desktop with **both renderers**: desktop GL, and the **GLES 1.0** renderer the R36S uses. Each build ran at 640×480 with scraped and unscraped ROM folders.

* **Generator check:** `main.xml` plus the layout, colour, font and background overrides reproduces the full theme exactly for all **468 combinations** of options.
* **Stale settings from another theme** (`ThemeColorSet`, `ThemeSystemView`, `subset.fontsize`, `subset.background`), on GL and GLES 1.0: the default look loads, there are zero warnings, and every view style (detailed / video / grid / basic) opens. The old v1.1 aborted in the same test.
* **AddressSanitizer + UBSan:** 183 systems with stale settings, then live switching of every option from the menu. No memory errors and no crashes. The only UBSan notes are uninitialised flags inside ES itself, and they appear with any theme.
* **Clean log:** every combination logs zero theme warnings.

## Rebuilding / customising

```
python3 tools/build_assets.py   # logos, glow tiles, backgrounds, UI icons (PNG), no-art cards
python3 tools/build_xml.py      # main.xml + option overrides + 194 system folders, with the 468-combination check
```

* `tools/systems.py`: system → logo + glow colour
* `tools/palette.py`: colour schemes
* `tools/build_xml.py`: layouts, font sizes, gamelist geometry

Requirements: Python 3 with Pillow, numpy and fontTools; `rsvg-convert`; `git`. The logo pack is cloned into `tools/.cache/`.

## Credits & licenses

* **System logos:** vector logos from the *Carbon* theme family (Rookervik / RetroPie, Batocera and fcamod contributors, [fabricecaruso/es-theme-carbon](https://github.com/fabricecaruso/es-theme-carbon)), licensed **CC BY-NC-SA**. NeonGlow is therefore for **non-commercial use**. Console names and logos are trademarks of their respective owners.
* **Fonts:** Barlow / Barlow Condensed by Jeremy Tribby, SIL Open Font License.
* **Glow tiles, backgrounds, icons, placeholders and theme XML:** original work generated by `tools/`.
