# theme-tools

Generators for `../es-theme-vcr-osd` (EmulationStation VCR OSD theme for the R36S).

| File | Purpose |
| --- | --- |
| `glyphs.py` | Bitmap glyph data for the OSD Tape pixel font |
| `build_font.py` | Builds `OSDTape-Chunky.ttf` / `OSDTape-Regular.ttf` with fontTools |
| `pixeltext.py` | Draws the same glyphs directly onto images (logos, backgrounds) |
| `pixelkit.py` | Small pixel-art toolkit (bevelled blocks, screens, buttons, sticker outline) |
| `consoles.py` | Hardware illustrations for every system (`python3 consoles.py sheet.png [keys…]`) |
| `systems.py` | System names, makers, years, types and brand colours |
| `build_theme.py` | Builds the whole theme: fonts, art, UI, loading screen, XML |
| `preview.py` | Renders approximate screenshots into `_preview/` |

```bash
pip install pillow fonttools
python3 build_theme.py ../es-theme-vcr-osd
python3 preview.py ../es-theme-vcr-osd ../es-theme-vcr-osd/_preview
```
