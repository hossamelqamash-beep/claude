import { interpolate, spring } from "remotion";
import { EASE } from "./easings";

type SpringConfig = Parameters<typeof spring>[0]["config"];

const CLAMP = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

/**
 * 0 → 1 progress between `start` and `start + duration` (in frames),
 * clamped and eased. The building block for most animations.
 */
export const progress = (
  frame: number,
  start: number,
  duration: number,
  easing: (t: number) => number = EASE.outExpo,
) =>
  interpolate(frame, [start, start + duration], [0, 1], { ...CLAMP, easing });

/** Maps a 0 → 1 progress value onto any numeric range. */
export const mix = (t: number, from: number, to: number) =>
  from + (to - from) * t;

/** 0 → 1 spring that starts at `delay` frames. */
export const springIn = ({
  frame,
  fps,
  delay = 0,
  config,
  durationInFrames,
}: {
  frame: number;
  fps: number;
  delay?: number;
  config?: SpringConfig;
  durationInFrames?: number;
}) => spring({ frame: frame - delay, fps, config, durationInFrames });

/** Delay (in frames) for the n-th item of a staggered group. */
export const stagger = (index: number, step: number, base = 0) =>
  base + index * step;

/**
 * Fades an element in at the start and out at the end of a window.
 * Handy for elements that must leave before a scene cut.
 */
export const fadeInOut = (
  frame: number,
  durationInFrames: number,
  fadeFrames: number,
) =>
  interpolate(
    frame,
    [0, fadeFrames, durationInFrames - fadeFrames, durationInFrames],
    [0, 1, 1, 0],
    CLAMP,
  );
