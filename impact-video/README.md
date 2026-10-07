# IMPACT — "Learning that goes beyond learning." (motion graphic)

A 90-second, 1920×1080 / 30 fps brand motion piece built from the script, the IMPACT logo and the brand colour guide. The style follows the reference video: dark canvas, soft blurred gradient glows, mixed sans and italic-serif type that blurs in word by word, thin grid layouts, white cards, and a logo draw-on at the end.

**Output:** `out/impact_motion_1080p.mp4` (final, with soundtrack)

## Brand mapping
| Use | Colour |
|---|---|
| Primary accents, gradients, logo icon | `#20e0e0` cyan → `#00a2ea` blue |
| Text on light scenes, logo wordmark | `#2a3649` navy |
| Chips, tokens, dominos, culture-shift wave | Secondary palette: `#f85a35` `#fbb414` `#00cc99` `#80dbff` `#3f37c9` `#8164ff` `#672496` `#ed1e6c` |
| Background field (Introducing IMPACT) | Matches the supplied indigo/blue/cyan gradient artwork |

Type: **Montserrat** (brand sans) + **Instrument Serif Italic** (the editorial italic from the reference).
The fingerprint arches in the logo are reused as the "ripple" motif (logo reveal, *Progress*, closing).

## Timeline (follows the script)
| Time | Scene |
|---|---|
| 0:00–0:08 | Opening: "Every business wants to move forward… **People do.**" |
| 0:08–0:20 | The Challenge: grid, workplace chips, "New challenges / technologies / expectations", then a white card for the question |
| 0:20–0:32 | Introducing IMPACT: icon ripple reveal, "Learning should leave an impact", think / decide / lead / perform timeline |
| 0:32–0:50 | What IMPACT does: Real people / challenges / business needs cards, Learning → Practice → Action, capability pills, "FORWARD" |
| 0:50–1:04 | The Difference: crossed-out vanity metrics, "after.", domino chain Insight → Action → Behavior → Results |
| 1:04–1:17 | The IMPACT Effect: person → team → leader → organisation network, colour wave, "Progress." |
| 1:17–1:30 | Closing: stay / spread / change something, "IMPACT", logo reveal + tagline |

## Audio
`soundtrack.py` generates an original ambient score (pad, sub, soft 100 BPM pulse, plucks, whooshes and hits on the cuts). There is **no voiceover**: the VO lines appear on screen as kinetic type, timed to the script's sections, so a recorded VO can be laid over the same timings.

## Re-rendering
Requirements: Node + Playwright (Chromium), Python 3 + numpy, ffmpeg.
```bash
node render.mjs video out/impact_silent.mp4 30        # frames → H.264
python3 soundtrack.py out/soundtrack.wav              # score
ffmpeg -i out/impact_silent.mp4 -i out/soundtrack.wav -c:v copy -c:a aac -b:a 256k -shortest out/impact_motion_1080p.mp4
node render.mjs stills /tmp/stills 12.5 47.9          # preview single frames
```
Open `index.html` in a browser for a live preview (`index.html?t=40` seeks). All timings live in `anim.js`, one function per scene.
