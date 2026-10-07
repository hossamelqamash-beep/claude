/**
 * Single source of truth for output format and timing.
 *
 * Change WIDTH / HEIGHT / FPS here and every composition follows.
 * Scene lengths are in SECONDS, so changing FPS keeps the same pacing.
 */
export const VIDEO = {
  width: 1920,
  height: 1080,
  fps: 30,
} as const;

/** Length of each scene of the Showcase composition, in seconds. */
export const SHOWCASE_SCENES = {
  intro: 4,
  shapes: 4.5,
  features: 5,
  outro: 4.5,
} as const;

/** Length of each transition between scenes, in seconds. */
export const SHOWCASE_TRANSITION_SECONDS = 0.7;

/** Converts seconds to a whole number of frames. */
export const toFrames = (seconds: number, fps: number) =>
  Math.round(seconds * fps);

/**
 * Total Showcase length in frames.
 * Transitions overlap neighbouring scenes, so they are subtracted.
 */
export const getShowcaseDurationInFrames = (fps: number) => {
  const scenes = Object.values(SHOWCASE_SCENES);
  const sceneFrames = scenes.reduce((sum, s) => sum + toFrames(s, fps), 0);
  const transitionFrames =
    (scenes.length - 1) * toFrames(SHOWCASE_TRANSITION_SECONDS, fps);
  return sceneFrames - transitionFrames;
};

/** Length of the Impact logo animation, in seconds. */
export const IMPACT_LOGO_SECONDS = 30;

/**
 * Key moments of the Impact logo animation, in seconds.
 * Most land on beats of the 120 BPM soundtrack (every 0.5 s).
 */
export const IMPACT_CUES = {
  dropStart: 0.6,
  impact: 2,
  line1In: 2.5,
  line1Out: 4,
  tunnelIn: 4.5,
  line2In: 5.5,
  line2Out: 9.4,
  collapse: 10,
  pillar: 11,
  arches: 11.5,
  arcs: 12.25,
  lockup: 15,
  letters: 15.75,
  tagline: 16.6,
  sheen: 17.5,
  lens: 19.5,
  echo: 24,
  sheen2: 26.5,
} as const;
