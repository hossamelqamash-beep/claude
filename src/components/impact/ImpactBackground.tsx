import type React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { IMPACT } from "../../theme";

type ImpactBackgroundProps = {
  /** 0..1 extra light, used to flash the scene on impacts. */
  readonly energy?: number;
  /** 0..1 fade from black at the very start. */
  readonly reveal?: number;
};

/**
 * The brand's deep-blue fluid gradient (indigo → royal blue → aqua),
 * rebuilt from soft glows that drift slowly so the frame always breathes.
 */
export const ImpactBackground: React.FC<ImpactBackgroundProps> = ({
  energy = 0,
  reveal = 1,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const glow = (
    color: string,
    x: number,
    y: number,
    w: number,
    h: number,
    opacity: number,
  ) => (
    <div
      style={{
        position: "absolute",
        left: `${x - w / 2}%`,
        top: `${y - h / 2}%`,
        width: `${w}%`,
        height: `${h}%`,
        borderRadius: "50%",
        background: `radial-gradient(closest-side, ${color} 0%, transparent 100%)`,
        opacity,
      }}
    />
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          opacity: reveal,
          background: `linear-gradient(200deg, ${IMPACT.royal} 0%, ${IMPACT.midnight} 45%, ${IMPACT.abyss} 100%)`,
        }}
      >
        {glow(IMPACT.glow, 52 + 5 * Math.sin(t * 0.35), 4 + 3 * Math.cos(t * 0.3), 80, 90, 0.85)}
        {glow(IMPACT.royal, 92 + 3 * Math.cos(t * 0.27), 12, 70, 80, 0.8)}
        {glow(IMPACT.aqua, 98 + 2 * Math.sin(t * 0.4), 100 + 4 * Math.sin(t * 0.33), 70, 90, 0.95)}
        {glow(IMPACT.indigo, 30 + 6 * Math.cos(t * 0.25), 60, 70, 70, 0.35)}
        {glow(IMPACT.abyss, 76 + 4 * Math.sin(t * 0.3), 52 + 4 * Math.cos(t * 0.38), 38, 50, 0.9)}
        {/* Impact light */}
        <AbsoluteFill
          style={{
            background: `radial-gradient(circle at 50% 50%, rgba(120,220,255,${0.55 * energy}) 0%, rgba(32,224,224,${0.18 * energy}) 30%, transparent 65%)`,
          }}
        />
        {/* Fine grain keeps the gradients free of banding in H.264 */}
        <AbsoluteFill style={{ opacity: 0.07, mixBlendMode: "overlay" }}>
          <svg width="100%" height="100%">
            <filter id="impact-grain">
              <feTurbulence
                type="fractalNoise"
                baseFrequency="0.9"
                numOctaves="2"
                seed={7}
                stitchTiles="stitch"
              />
            </filter>
            <rect width="100%" height="100%" filter="url(#impact-grain)" />
          </svg>
        </AbsoluteFill>
        <AbsoluteFill
          style={{
            background:
              "radial-gradient(ellipse at 50% 50%, transparent 50%, rgba(2,0,20,0.6) 100%)",
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
