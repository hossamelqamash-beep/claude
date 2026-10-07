import type React from "react";

type GlassDropProps = {
  readonly x: number;
  readonly y: number;
  readonly size: number;
  /** Vertical stretch while falling (>1) or squash on impact (<1). */
  readonly stretch?: number;
  readonly opacity?: number;
};

/** A falling droplet of liquid glass. */
export const GlassDrop: React.FC<GlassDropProps> = ({
  x,
  y,
  size,
  stretch = 1,
  opacity = 1,
}) => {
  const w = size / Math.sqrt(stretch);
  const h = size * stretch;
  return (
    <div
      style={{
        position: "absolute",
        left: x - w / 2,
        top: y - h / 2,
        width: w,
        height: h,
        borderRadius: "50% 50% 50% 50% / 58% 58% 42% 42%",
        opacity,
        backdropFilter: "blur(3px) saturate(2) brightness(1.4)",
        background: [
          "radial-gradient(circle at 34% 26%, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.35) 9%, transparent 22%)",
          "radial-gradient(circle at 62% 78%, rgba(32,224,224,0.65) 0%, transparent 45%)",
          "radial-gradient(circle at 50% 50%, rgba(0,162,234,0.08) 40%, rgba(128,219,255,0.45) 100%)",
        ].join(", "),
        boxShadow: [
          "inset 0 2px 1px rgba(255,255,255,0.7)",
          "inset 0 -6px 14px rgba(32,224,224,0.45)",
          "0 0 40px rgba(32,224,224,0.45)",
          "0 18px 30px rgba(3,0,30,0.4)",
        ].join(", "),
      }}
    />
  );
};
