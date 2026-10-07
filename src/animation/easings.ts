import { Easing } from "remotion";

/** Shared easing curves. Use these instead of ad-hoc curves for a consistent feel. */
export const EASE = {
  /** Fast start, long soft landing. Great default for entrances. */
  outExpo: Easing.bezier(0.16, 1, 0.3, 1),
  /** Symmetric, for moves between two resting states. */
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  /** Accelerating, for exits. */
  inQuart: Easing.bezier(0.5, 0, 0.75, 0),
  /** Slight overshoot, for playful pops. */
  outBack: Easing.bezier(0.34, 1.56, 0.64, 1),
} as const;

/** Spring presets for `spring()`. */
export const SPRING = {
  /** No bounce, smooth settle. */
  smooth: { damping: 200 },
  /** A little bounce. */
  snappy: { damping: 14, stiffness: 160, mass: 0.6 },
  /** Bouncy, for shapes and icons. */
  bouncy: { damping: 9, stiffness: 120, mass: 0.7 },
} as const;
