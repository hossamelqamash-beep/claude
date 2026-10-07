import type React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../theme";

type BackgroundProps = {
  readonly accentColor?: string;
  readonly secondaryColor?: string;
};

/**
 * Dark backdrop with slowly drifting colour glows and a moving dot grid.
 * Purely frame-driven, so it loops seamlessly under any scene.
 */
export const Background: React.FC<BackgroundProps> = ({
  accentColor = COLORS.violet,
  secondaryColor = COLORS.cyan,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;

  const glow = (color: string, x: number, y: number, size: number) => (
    <div
      style={{
        position: "absolute",
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        borderRadius: "50%",
        background: `radial-gradient(circle, ${color} 0%, transparent 65%)`,
        opacity: 0.35,
      }}
    />
  );

  return (
    <AbsoluteFill
      style={{ backgroundColor: COLORS.background, overflow: "hidden" }}
    >
      {glow(
        accentColor,
        width * (0.25 + 0.06 * Math.sin(t * 0.6)),
        height * (0.3 + 0.08 * Math.cos(t * 0.5)),
        width * 0.7,
      )}
      {glow(
        secondaryColor,
        width * (0.78 + 0.05 * Math.cos(t * 0.45)),
        height * (0.72 + 0.07 * Math.sin(t * 0.55)),
        width * 0.6,
      )}
      <AbsoluteFill
        style={{
          backgroundImage:
            "radial-gradient(rgba(255,255,255,0.09) 1.5px, transparent 1.5px)",
          backgroundSize: "48px 48px",
          backgroundPosition: `${t * 8}px ${t * 4}px`,
        }}
      />
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.55) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
