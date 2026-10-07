import type React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SPRING, springIn } from "../animation";
import { COLORS, FONTS } from "../theme";

type FeatureCardProps = {
  readonly icon: React.ReactNode;
  readonly title: string;
  readonly body: string;
  readonly accentColor: string;
  /** Frame at which the card slides in. */
  readonly delay?: number;
};

/** Glassy card that springs up into place. */
export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  body,
  accentColor,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = springIn({ frame, fps, delay, config: SPRING.snappy });

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        gap: 28,
        padding: 48,
        borderRadius: 32,
        backgroundColor: COLORS.surface,
        border: `1.5px solid ${COLORS.surfaceBorder}`,
        boxShadow: `0 30px 80px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08)`,
        opacity: interpolate(t, [0, 0.6], [0, 1], {
          extrapolateRight: "clamp",
        }),
        translate: `0 ${interpolate(t, [0, 1], [120, 0])}px`,
      }}
    >
      <div
        style={{
          width: 96,
          height: 96,
          borderRadius: 24,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: `${accentColor}22`,
          border: `1.5px solid ${accentColor}55`,
        }}
      >
        {icon}
      </div>
      <div
        style={{
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 48,
          color: COLORS.text,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontFamily: FONTS.body,
          fontSize: 28,
          lineHeight: 1.45,
          color: COLORS.textMuted,
        }}
      >
        {body}
      </div>
    </div>
  );
};
