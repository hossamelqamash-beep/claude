# AGENTS.md — Remotion motion graphics project

Guidance for AI coding agents (Claude Code, Codex, Cursor, …) working in this repo.
Remotion **4.0.534**, React 19, TypeScript, npm.

> Official Remotion Agent Skills are installed in `.agents/skills/` (symlinked into
> `.claude/skills/`). Load `remotion-best-practices` / `remotion-markup` before writing
> non-trivial Remotion code, and `remotion-docs` to look up APIs. They are the source of
> truth for current APIs; this file is the source of truth for **this project's** conventions.

## Commands

| Task | Command |
| --- | --- |
| Install | `npm ci` |
| Preview in Remotion Studio | `npm run dev` (opens http://localhost:3000) |
| List compositions | `npm run compositions` |
| Render the sample MP4 | `npm run render` → `out/showcase.mp4` |
| Render one frame (visual check) | `npx remotion still Showcase out/frame.png --frame=120` |
| Render any composition | `npx remotion render <CompositionId> out/<name>.mp4` |
| Lint + typecheck | `npm run lint` (run before every commit) |
| Add a Remotion package | `npx remotion add @remotion/<pkg>` (keeps versions aligned) |
| Upgrade Remotion | `npm run upgrade` |

Useful render flags: `--frames=0-89`, `--scale=0.5` (fast drafts), `--props='{"title":"Hi"}'`,
`--codec=prores` / `--codec=vp9`, `--crf=18`, `--muted`.
If Chrome can't be downloaded (CI, locked network) point Remotion at an existing one:
`REMOTION_BROWSER_EXECUTABLE=/path/to/chrome-headless-shell npm run render`.

## Project layout

```
src/
  index.ts              Entry point (registerRoot) — don't rename
  Root.tsx              Registers every <Composition>; scenes live in the "Scenes" folder
  config/video.ts       ⭐ WIDTH / HEIGHT / FPS and scene lengths (seconds)
  theme/                Colors, gradients, fonts (self-hosted, src/theme/fonts.ts)
  animation/            Easings, spring presets, progress/stagger helpers, beat-sync helpers
  components/           Reusable animated building blocks (AnimatedText, Kicker, ShapePop, …)
  scenes/               One file per scene; each is also a standalone composition
  compositions/         Full videos that sequence scenes (Showcase.tsx)
public/                 Static assets — reference with staticFile("…")
  audio/soundtrack.mp3  120 BPM sample track
  fonts/                Inter + Space Grotesk variable woff2
  images/               Put images here
out/                    Render output (git-ignored)
```

## Changing resolution, frame rate, duration

Everything lives in `src/config/video.ts`:

- `VIDEO.width`, `VIDEO.height`, `VIDEO.fps` apply to every composition in `Root.tsx`.
  For vertical video use 1080×1920; for square use 1080×1080.
- `SHOWCASE_SCENES` holds each scene's length **in seconds**. `SHOWCASE_TRANSITION_SECONDS`
  sets the transition length. The total duration is computed automatically
  (scenes − overlapping transitions), so it never goes out of sync.
- Because all timing is in seconds × `fps`, changing fps (24/30/60) keeps the same pacing.

## Rules for writing animation code (must follow)

1. **Everything is driven by `useCurrentFrame()`.** Never use CSS `transition`/`animation`,
   Tailwind `animate-*`, `setTimeout`, `requestAnimationFrame` or `Math.random()`. They
   don't render deterministically. For randomness, use `random("seed")` from `remotion`.
2. **Time in seconds × fps.** Get `fps` from `useVideoConfig()` and write `delay={0.5 * fps}`,
   never hard-code frame numbers that assume 30 fps.
3. **Clamp interpolations**: `extrapolateLeft: "clamp", extrapolateRight: "clamp"`
   (the `progress()` helper does this for you).
4. **Use the shared motion vocabulary** in `src/animation`:
   - `EASE.outExpo` (entrances), `EASE.inOut` (moves), `EASE.inQuart` (exits), `EASE.outBack` (pops)
   - `SPRING.smooth` / `SPRING.snappy` / `SPRING.bouncy`
   - `progress(frame, start, duration, easing?)` → clamped eased 0..1
   - `springIn({frame, fps, delay, config})` → 0..1 spring
   - `stagger(index, step, base)` → per-item delay
   - `mix(t, from, to)`, `fadeInOut(frame, duration, fadeFrames)`
5. Prefer the individual CSS transform properties `translate`, `scale`, `rotate` over a
   combined `transform` string.
6. Add `premountFor={fps}` to every `<Sequence>`, `<TransitionSeries.Sequence>`, `<Audio>`,
   `<Video>` so assets are loaded before they appear.
7. Fonts must be loaded via `@remotion/fonts` (local) or `@remotion/google-fonts` so rendering
   waits for them. Use `FONTS.display` / `FONTS.body` from `src/theme`.
8. Images: `<Img>` (or `<CanvasImage>`) from `remotion` with `staticFile()`, never plain `<img>`.
9. Keep every component pure and deterministic: the same frame must always render the same pixels.

## Recipes

### Create a new scene

1. Create `src/scenes/MyScene.tsx`:

   ```tsx
   import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
   import { progress } from "../animation";
   import { AnimatedText, Background } from "../components";
   import { COLORS, FONTS } from "../theme";

   export type MySceneProps = { readonly accentColor: string };

   export const MyScene: React.FC<MySceneProps> = ({ accentColor }) => {
     const frame = useCurrentFrame();
     const { fps } = useVideoConfig();
     return (
       <AbsoluteFill style={{ fontFamily: FONTS.body }}>
         <Background accentColor={accentColor} />
         <AbsoluteFill style={{ justifyContent: "center", alignItems: "center",
                                opacity: progress(frame, 0, 0.5 * fps) }}>
           <AnimatedText text="Hello" by="char" delay={0.2 * fps}
             style={{ fontFamily: FONTS.display, fontSize: 140, color: COLORS.text }} />
         </AbsoluteFill>
       </AbsoluteFill>
     );
   };
   ```
2. Export it from `src/scenes/index.ts`.
3. Register it in `Root.tsx` inside `<Folder name="Scenes">` (inline `defaultProps`) so it can be
   previewed alone.
4. Add a length to `SHOWCASE_SCENES` and a `<TransitionSeries.Sequence>` (plus a
   `<TransitionSeries.Transition>`) in the composition that uses it.

### Create a new video (composition)

Copy `src/compositions/Showcase.tsx`, change the scene list, define a Zod schema for the props
you want editable in Studio, and register it in `Root.tsx` with
`width/height/fps` from `VIDEO` and a duration helper like `getShowcaseDurationInFrames`.
Keep `defaultProps` as an inline object literal on `<Composition>` so Studio can save edits.

### Animate typography

- `<AnimatedText text by="char" | "word" delay stagger rise blur />` gives staggered rise + blur + fade.
- `<Kicker>` is a label pill. `<RevealLine>` is an accent underline wipe. `<Counter to={…} />`
  counts numbers up with tabular figures.
- Gradient text: add `pieceStyle={{ background: GRADIENTS.brand, WebkitBackgroundClip: "text", color: "transparent" }}`
  (use `by="word"`).
- For fitting text to a box, use `fitText()` / `measureText()` from `@remotion/layout-utils`
  (`npx remotion add @remotion/layout-utils`).

### Animate graphics and shapes

- `@remotion/shapes`: `<Circle>`, `<Rect>`, `<Triangle>`, `<Star>`, `<Polygon>`, `<Pie>`, `<Arrow>`, …
- Wrap any shape in `<ShapePop x y delay spin float>` for a spring pop-in, continuous spin and float.
- SVG line drawing: animate `strokeDashoffset` from the circumference to 0 (see `ShapesScene.tsx`).
- For path morphing / drawing along paths: `@remotion/paths` (`evolvePath`, `interpolatePath`).

### Transitions between scenes

Use `<TransitionSeries>` from `@remotion/transitions` with presentations `fade()`, `slide({direction})`,
`wipe({direction})`, `flip()`, `clockWipe()`, … and timing `linearTiming({durationInFrames, easing})`
or `springTiming({config, durationInFrames})`. Transitions **overlap** scenes, so the total
duration = Σ scenes − Σ transitions (already handled in `config/video.ts`).

### Synchronize audio

- Put audio in `public/audio/` and use `<Audio src={staticFile("audio/x.mp3")} premountFor={fps} />`
  from `@remotion/media`. Props: `volume` (number, or `interpolate(frame, …)` for fades),
  `trimBefore`, `trimAfter`, `from`, `playbackRate`, `loop`, `muted`.
- **Tempo-based sync** (known BPM): `beatToFrame(beat, bpm, fps)` gives the frame for a beat,
  `beatPulse(frame, bpm, fps)` gives 1 on each beat decaying to 0 (see the logo in `OutroScene.tsx`;
  the sample track is 120 BPM, `SOUNDTRACK_BPM`).
- **Cue-based sync**: write cue times in seconds (`const CUES = { drop: 6.2 }`) and start
  sequences at `CUES.drop * fps`.
- **Amplitude-reactive**: `npx remotion add @remotion/media-utils`, then
  `useWindowedAudioData()` / `visualizeAudio()`; read the `audio-visualization.md` skill rule.
- Voiceover / captions: see the `remotion-markup` → `voiceover.md` rule and the `remotion-captions` skill.
- Make total duration follow an audio file with `calculateMetadata` (see `calculate-metadata.md` skill rule).

### Preview and verify your work

1. `npm run lint` (ESLint with Remotion rules + `tsc`).
2. `npm run compositions` to confirm the composition registers with the expected size/fps/duration.
3. Render key frames to PNG and **look at them** before rendering video:
   `npx remotion still Showcase out/check.png --frame=150 --scale=0.5`
4. `npm run dev` for interactive preview: scrub the timeline, edit props in the right panel.
5. `npm run render` for the final MP4. Check it with
   `ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate out/showcase.mp4`.

## Gotchas

- `public/` files must be referenced via `staticFile()`, never with relative imports or `/public/...`.
- Don't add a tsconfig `paths` alias named `remotion` (it shadows the package).
- Keep all `@remotion/*` packages and `remotion` on the **exact same version**; use `npx remotion add`.
- Large outputs go to `out/`, which is git-ignored.
- Licensing: Remotion is free for individuals and companies of up to 3 people; larger companies need a
  company license (https://remotion.pro/license).
