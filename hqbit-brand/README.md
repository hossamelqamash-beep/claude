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
