# Remotion Motion Studio

Programmatic motion graphics videos with [Remotion](https://www.remotion.dev) 4.0.534 and React,
set up for building with AI coding agents.

**AI agents:** read [AGENTS.md](AGENTS.md). Official Remotion Agent Skills are installed in `.agents/skills`.

## Quick start

```console
npm ci            # install dependencies (Node 18+)
npm run dev       # open Remotion Studio for a live preview
npm run render    # render the sample to out/showcase.mp4
```

The first render downloads Chrome Headless Shell automatically.

## The sample: `Showcase`

1920×1080 · 30 fps · ~16 s · four scenes (Intro → Shapes → Features → Outro) with animated
typography, `@remotion/shapes` graphics, slide/wipe/fade transitions and a 120 BPM soundtrack that
the outro logo pulses to. Title, subtitle, CTA, colors and audio can be edited in the Studio sidebar.

Each scene is also registered on its own under **Scenes** for focused previewing.

## Change format and timing

Edit [`src/config/video.ts`](src/config/video.ts):

```ts
export const VIDEO = { width: 1920, height: 1080, fps: 30 };
export const SHOWCASE_SCENES = { intro: 4, shapes: 4.5, features: 5, outro: 4.5 }; // seconds
export const SHOWCASE_TRANSITION_SECONDS = 0.7;
```

Total duration is computed from these. All animations are written in seconds × fps, so changing
the frame rate keeps the same pacing.

## Scripts

| Script | What it does |
| --- | --- |
| `npm run dev` / `npm run studio` | Remotion Studio preview |
| `npm run render` | Render `Showcase` to `out/showcase.mp4` (H.264, CRF 18) |
| `npm run render:still` | Render frame 60 to `out/showcase.png` |
| `npm run render:all` | Render the full video and every scene |
| `npm run compositions` | List compositions with size, fps and duration |
| `npm run lint` | ESLint + TypeScript |
| `npm run upgrade` | Upgrade all Remotion packages together |

## Structure

```
src/config/        resolution, fps, durations
src/theme/         colors, fonts
src/animation/     easings, springs, progress/stagger and beat-sync helpers
src/components/    AnimatedText, Background, Kicker, RevealLine, ShapePop, FeatureCard, Counter
src/scenes/        Intro, Shapes, Features, Outro
src/compositions/  Showcase (TransitionSeries + audio)
public/            audio, fonts, images (use staticFile())
```

## License

Remotion requires a company license for organizations with more than 3 people. See
[remotion.pro/license](https://www.remotion.pro/license). Bundled fonts (Inter, Space Grotesk) are
SIL Open Font License 1.1.
