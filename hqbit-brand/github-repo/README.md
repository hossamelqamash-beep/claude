<p align="center"><img src="images/showcase-collection.jpg" alt="HQbit: the R36S theme collection" width="100%"></p>

# HQbit R36S Themes

Four free EmulationStation themes for the **R36S and its clones** running **EmuELEC, ArkOS or dArkOS**, and firmware variants based on them. Everything is drawn for the 640×480 screen, so pixel art stays sharp and the battery and clock corner stays clear.

**Website:** https://hossamelqamash-beep.github.io/hqbit-r36s-themes/

## Download

| Theme | What it looks like | Download |
|---|---|---|
| **Volta** v1.1 | Dark and light dashboard look: glossy cards, tick-ring gauges, dot-matrix numbers. 13 colour schemes, 3 carousel layouts. | [es-theme-volta-v1.1.zip](https://github.com/hossamelqamash-beep/hqbit-r36s-themes/raw/main/downloads/es-theme-volta-v1.1.zip) (19 MB) |
| **NeonGlow** v1.2 | Glass tiles that glow in each system's own colour. 13 colour schemes, 4 layouts, 194 systems. | [neonglow-r36s-v1.2.zip](https://github.com/hossamelqamash-beep/hqbit-r36s-themes/raw/main/downloads/neonglow-r36s-v1.2.zip) (22 MB) |
| **VCR OSD** v1 | The blue screen of an old VCR, with full-colour pixel consoles and a custom pixel font. 153 systems, 3 colour sets, CRT scanlines. | [es-theme-vcr-osd.zip](https://github.com/hossamelqamash-beep/hqbit-r36s-themes/raw/main/downloads/es-theme-vcr-osd.zip) (2 MB) |
| **DeskOS** v2 | A retro desktop where every system opens as a window. 14 colour schemes (7 light, 7 dark). | [es-theme-deskos.zip](https://github.com/hossamelqamash-beep/hqbit-r36s-themes/raw/main/downloads/es-theme-deskos.zip) (2 MB) |

You can also browse everything in the [`downloads`](downloads) folder.

## Install

1. Download a theme and unzip it on your computer. If you get a folder inside a folder with the same name, use the inner one.
2. Copy the theme folder to the SD card:
   - **ArkOS / dArkOS:** `EASYROMS/themes/`
   - **EmuELEC:** EmulationStation's themes folder, `/storage/.config/emulationstation/themes/` (over the network share or SSH)
3. On the device press **Start → UI Settings → Theme Set** and pick the theme. Colours, layouts and font sizes are under **Theme Configuration**. Restart EmulationStation if it doesn't switch right away.

| Theme | Folder to copy | Ends up as |
|---|---|---|
| Volta | `es-theme-volta` | `themes/es-theme-volta/theme.xml` |
| NeonGlow | `neonglow` | `themes/neonglow/3do/theme.xml` |
| VCR OSD | `es-theme-vcr-osd` | `themes/es-theme-vcr-osd/theme.xml` |
| DeskOS | `es-theme-deskos` | `themes/es-theme-deskos/snes/theme.xml` |

### Boot loop after applying a theme?

1. Turn the device off and take out the SD card.
2. Put the SD card into your computer and delete the theme folder you just selected from the `themes` folder.
3. Put the SD card back into your R36S and turn it on. It will start with your default system theme.

## Showcase

| | |
|---|---|
| ![Volta](images/showcase-volta.jpg) | ![NeonGlow](images/showcase-neonglow.jpg) |
| ![VCR OSD](images/showcase-vcr.jpg) | ![DeskOS](images/showcase-deskos.jpg) |

![Screenshots of all four themes on the 640×480 screen](images/screens.jpg)

## About

HQbit is the pixel art and UI project of Hossam el Qamash. This is my first project of this kind, so there's plenty of room to improve, and it's the start of more projects for the R36S and other popular handhelds. Bug reports and ideas are welcome in [Issues](../../issues): what breaks on your clone or firmware, what's hard to read, what you'd like next.

Made with a mix of AI and traditional design tools. Device photos are AI mock-ups; the screenshots are real.

## Credits and licence

Free for personal, non-commercial use; see [LICENSE.md](LICENSE.md).

- Volta's system logos come from [Art Book Next](https://github.com/anthonycaccese/art-book-next-es-de) by Anthony Caccese and NeonGlow's from the [Carbon](https://github.com/fabricecaruso/es-theme-carbon) theme family, both CC BY-NC-SA, so those themes are shared under CC BY-NC-SA too.
- The full-colour console art in DeskOS and VCR OSD is from the AmberELEC 8bit theme (based on Rookervik's Carbon, edited by bebeidon).
- VCR OSD's interface art and its OSD Tape font are original; the font is under the SIL Open Font License.
- Console names, designs and logos are trademarks of their owners. HQbit is a fan project and isn't affiliated with them.
