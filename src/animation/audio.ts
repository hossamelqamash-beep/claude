/**
 * Helpers for syncing visuals to music with a known tempo.
 * For arbitrary audio, use `useAudioData()` + `visualizeAudio()` from
 * `@remotion/media-utils` instead (see AGENTS.md).
 */

/** Number of frames per musical beat. */
export const framesPerBeat = (bpm: number, fps: number) => (60 / bpm) * fps;

/** Frame on which beat number `beat` (0-based) lands. */
export const beatToFrame = (beat: number, bpm: number, fps: number) =>
  Math.round(beat * framesPerBeat(bpm, fps));

/**
 * 1 on every beat, decaying to 0 before the next one.
 * Multiply it into scale/glow to make elements "pulse" with the music.
 */
export const beatPulse = (
  frame: number,
  bpm: number,
  fps: number,
  decay = 6,
) => {
  const fpb = framesPerBeat(bpm, fps);
  const sinceBeat = (frame % fpb) / fpb;
  return Math.exp(-decay * sinceBeat);
};
