import type React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { progress } from "../animation";
import { COLORS, FONTS } from "../theme";

type KickerProps = {
  readonly children: string;
  readonly color?: string;
  /** Frame at which the pill starts animating in. */
  readonly delay?: number;
};

/** Small uppercase label pill that sits above a headline. */
export const Kicker: React.FC<KickerProps> = ({
  children,
  color = COLORS.cyan,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const t = progress(frame, delay, 20);

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 14,
        alignSelf: "flex-start",
        padding: "12px 24px",
        borderRadius: 999,
        border: `1.5px solid ${COLORS.surfaceBorder}`,
        backgroundColor: COLORS.surface,
        color: COLORS.text,
        fontFamily: FONTS.body,
        fontWeight: 600,
        fontSize: 24,
        letterSpacing: "0.16em",
        textTransform: "uppercase",
        opacity: t,
        translate: `${interpolate(t, [0, 1], [-30, 0])}px 0`,
      }}
    >
      <div
        style={{
          width: 12,
          height: 12,
          borderRadius: "50%",
          backgroundColor: color,
          boxShadow: `0 0 18px ${color}`,
        }}
      />
      {children}
    </div>
  );
};
