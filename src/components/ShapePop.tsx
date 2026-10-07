import type React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SPRING, springIn } from "../animation";

type ShapePopProps = {
  readonly children: React.ReactNode;
  /** Centre position, in px. */
  readonly x: number;
  readonly y: number;
  /** Frame at which the shape pops in. */
  readonly delay?: number;
  /** Continuous rotation speed, in degrees per second. */
  readonly spin?: number;
  /** Vertical float amplitude, in px. */
  readonly float?: number;
};

/**
 * Positions any shape, pops it in with a bouncy spring, then keeps it
 * gently floating and rotating. Wrap `@remotion/shapes` components with it.
 */
export const ShapePop: React.FC<ShapePopProps> = ({
  children,
  x,
  y,
  delay = 0,
  spin = 20,
  float = 14,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = springIn({ frame, fps, delay, config: SPRING.bouncy });
  const seconds = Math.max(0, frame - delay) / fps;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        translate: `-50% calc(-50% + ${Math.sin(seconds * 1.6 + delay) * float}px)`,
        scale: String(t),
        rotate: `${interpolate(t, [0, 1], [-90, 0]) + seconds * spin}deg`,
        opacity: Math.min(1, t * 1.5),
      }}
    >
      {children}
    </div>
  );
};
