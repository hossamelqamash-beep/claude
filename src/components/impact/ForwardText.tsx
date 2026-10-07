import type React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { EASE, progress } from "../../animation";
import { FONTS, IMPACT } from "../../theme";

type ForwardTextProps = {
  readonly text: string;
  /** Frame the first word starts entering. */
  readonly inFrame: number;
  /** Frame the first word starts leaving. */
  readonly outFrame: number;
  readonly fontSize?: number;
  readonly style?: React.CSSProperties;
};

/**
 * A line that always travels forward: words arrive from the left out of a
 * motion blur, settle sharp, then keep moving right as they leave.
 * The last word carries the brand gradient.
 */
export const ForwardText: React.FC<ForwardTextProps> = ({
  text,
  inFrame,
  outFrame,
  fontSize = 78,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: `0 ${fontSize * 0.28}px`,
        fontFamily: FONTS.display,
        fontWeight: 500,
        fontSize,
        letterSpacing: "-0.02em",
        color: "#FFFFFF",
        textShadow: "0 6px 34px rgba(3, 0, 40, 0.85)",
        ...style,
      }}
    >
      {words.map((word, i) => {
        const enter = progress(frame, inFrame + i * 0.09 * fps, 0.8 * fps);
        const exit = progress(
          frame,
          outFrame + i * 0.06 * fps,
          0.55 * fps,
          EASE.inQuart,
        );
        const last = i === words.length - 1;
        return (
          <span
            key={`${word}-${i}`}
            style={{
              display: "inline-block",
              opacity: enter * (1 - exit),
              translate: `${-70 * (1 - enter) + 110 * exit}px 0px`,
              filter: `blur(${14 * (1 - enter) + 12 * exit}px)`,
              ...(last
                ? {
                    background: `linear-gradient(100deg, ${IMPACT.cyan} 0%, ${IMPACT.sky} 50%, ${IMPACT.blue} 100%)`,
                    WebkitBackgroundClip: "text",
                    backgroundClip: "text",
                    color: "transparent",
                  }
                : null),
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
