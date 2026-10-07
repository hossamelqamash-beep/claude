import type React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

type GlassRippleProps = {
  /** Origin of the ripple, in px. */
  readonly x: number;
  readonly y: number;
  /** Start time in frames. */
  readonly from: number;
  /** Life time in seconds. */
  readonly seconds?: number;
  readonly startRadius?: number;
  readonly endRadius: number;
  /** Ring thickness at birth, in px. Thins out as it spreads. */
  readonly thickness?: number;
  readonly strength?: number;
};

// Water-like: fast push off the impact point, long glide outward.
const SPREAD = Easing.bezier(0.1, 0.75, 0.25, 1);

/**
 * An expanding ring of liquid glass. The ring frosts and brightens what is
 * behind it and catches a rim light from the top-left.
 */
export const GlassRipple: React.FC<GlassRippleProps> = ({
  x,
  y,
  from,
  seconds = 2.2,
  startRadius = 10,
  endRadius,
  thickness = 46,
  strength = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const life = seconds * fps;
  const t = (frame - from) / life;
  if (t <= 0 || t >= 1) {
    return null;
  }

  const spread = SPREAD(t);
  const r = interpolate(spread, [0, 1], [startRadius, endRadius]);
  const th = Math.min(r, interpolate(t, [0, 1], [thickness, thickness * 0.25]));
  const opacity =
    strength *
    interpolate(t, [0, 0.06, 0.55, 1], [0, 1, 0.75, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  const inner = Math.max(0, r - th);
  const ring = `radial-gradient(circle closest-side, transparent ${inner - 1}px, #000 ${inner + 1}px, #000 ${r - 1.5}px, transparent ${r}px)`;

  return (
    <div
      style={{
        position: "absolute",
        left: x - r,
        top: y - r,
        width: r * 2,
        height: r * 2,
        borderRadius: "50%",
        opacity,
        pointerEvents: "none",
      }}
    >
      {/* Glass body: refracted, frosted and lifted backdrop */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          backdropFilter: "blur(5px) saturate(1.9) brightness(1.35)",
          background:
            "conic-gradient(from 210deg, rgba(255,255,255,0.42), rgba(255,255,255,0.03) 22%, rgba(32,224,224,0.22) 48%, rgba(255,255,255,0.03) 72%, rgba(255,255,255,0.42))",
          WebkitMaskImage: ring,
          maskImage: ring,
        }}
      />
      {/* Outer rim light */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          border: "1.5px solid transparent",
          background:
            "conic-gradient(from 200deg, rgba(255,255,255,0.95), rgba(255,255,255,0.1) 30%, rgba(128,219,255,0.6) 55%, rgba(255,255,255,0.1) 80%, rgba(255,255,255,0.95)) border-box",
          WebkitMask:
            "linear-gradient(#000 0 0) padding-box, linear-gradient(#000 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
        }}
      />
      {/* Inner rim, fainter: the back face of the ring */}
      <div
        style={{
          position: "absolute",
          left: th,
          top: th,
          width: inner * 2,
          height: inner * 2,
          borderRadius: "50%",
          boxShadow:
            "0 0 0 1px rgba(255,255,255,0.35), 0 0 24px rgba(32,224,224,0.25)",
        }}
      />
    </div>
  );
};
