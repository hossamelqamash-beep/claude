# HQbit brand kit

Identity for HQbit (Hossam el Qamash): EmulationStation themes, pixel icon packs and UI for the R36S.
Built around the official logo `logo/official/hqbit-logo-original.svg`.

| Folder | What |
|---|---|
| `logo/official/` | The original logo file, unchanged |
| `logo/` | SVG versions from the same paths: horizontal, stacked (HQ over BIT), personal HQ logo; on purple, white (for dark/purple backgrounds), purple and black (for light backgrounds); app icon |
| `logo/png/` | PNG exports (transparent unless "on-purple") and app icon 1024/512/192/32 |
| `profile/` | Profile pictures (1024×1024, circle-safe): HQbit flat, HQbit keycap, personal HQ |
| `boards/` | Brand guide boards: cover, logo system, colour, typography, elements, applications |
| `_archive/` | Earlier logo explorations (monogram v1, pixel v2) and accent studies, superseded |

## Colours
HQ Purple `#612BFE` (primary) · Bit Lime `#E0FE3B` (the bit only) · White `#FFFFFF` ·
Void `#0D0619` · Night `#160A2E` · Plum `#2A1250` · Lilac `#B9A3FF`

## Fonts (all SIL Open Font License)
Unbounded (headlines) · Inter (body) · Silkscreen (pixel accents) · JetBrains Mono (tech details)

## Rebuild
`python3 tools/build_brand.py` (needs Pillow and Playwright's Chromium headless shell).

## Logo mark and 3D photos
* `logo/hqbit-mark-*.svg` / `logo/png/hqbit-mark-*.png`: the logo mark, the B with the lime chip.
* `photos/`: 3D product shots with the B mark (glass tiles, glowing glass keycap, purple keycap), rendered with three.js.
  Rebuild: `cd tools/render3d && npm install three@0.170.0 playwright-core@1.56.1`, then from `hqbit-brand/`
  run `python3 -m http.server 8765` and `node tools/render3d/render.mjs`.
