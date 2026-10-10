# HQbit brand kit

Purple-only identity for HQbit (Hossam el Qamash): EmulationStation themes, pixel icon packs and UI for the R36S.

| Folder | What |
|---|---|
| `logo/` | SVG logos (horizontal, stacked, symbol) in `dark` (for dark backgrounds), `light`, `white` and `night`; personal HQ logo; app icon |
| `logo/png/` | PNG exports (transparent) and app icon 1024/512/192/32 |
| `profile/` | Profile pictures (1024×1024, circle-safe) for Reddit and other platforms |
| `boards/` | Brand guide boards: cover, logo system, colour, typography, elements, applications |
| `color-studies/` | Earlier accent studies (superseded: the brand is purple only) |

## Colours
Void `#0D0619` · Night `#160A2E` · Plum `#2A1250` · Royal `#4B2496` · Electric Violet `#7C4DFF` · Lilac `#B9A3FF` · Mist `#F2EDFF`

## Fonts (all SIL Open Font License)
Space Grotesk (headlines, wordmark) · Inter (body) · Silkscreen (pixel accents) · JetBrains Mono (tech details)

## Rebuild
`python3 tools/build_brand.py` (needs fontTools, brotli, Pillow and Playwright's Chromium headless shell).
