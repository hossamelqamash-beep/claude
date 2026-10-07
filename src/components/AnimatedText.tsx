import type React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { SPRING, springIn } from "../animation";

type AnimatedTextProps = {
  readonly text: string;
  /** Animate word by word, or character by character. */
  readonly by?: "word" | "char";
  /** Frames before the first piece starts. */
  readonly delay?: number;
  /** Frames between consecutive pieces. */
  readonly stagger?: number;
  /** Vertical travel of each piece, in em. */
  readonly rise?: number;
  /** Max blur at the start of each piece, in px. */
  readonly blur?: number;
  readonly style?: React.CSSProperties;
  /** Style applied to every animated piece (e.g. a gradient fill). */
  readonly pieceStyle?: React.CSSProperties;
};

/**
 * Staggered text reveal: each word/character rises, un-blurs and fades in
 * with a spring. Works for titles, subtitles and captions.
 */
export const AnimatedText: React.FC<AnimatedTextProps> = ({
  text,
  by = "word",
  delay = 0,
  stagger = by === "char" ? 2 : 4,
  rise = 0.5,
  blur = 10,
  style,
  pieceStyle,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");

  let pieceIndex = 0;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", ...style }}>
      {words.map((word, w) => {
        const pieces = by === "char" ? Array.from(word) : [word];
        return (
          <span
            key={`${word}-${w}`}
            style={{
              display: "inline-flex",
              whiteSpace: "pre",
              marginRight: w < words.length - 1 ? "0.25em" : 0,
            }}
          >
            {pieces.map((piece, p) => {
              const t = springIn({
                frame,
                fps,
                delay: delay + pieceIndex++ * stagger,
                config: SPRING.smooth,
                durationInFrames: Math.round(0.8 * fps),
              });
              return (
                <span
                  key={`${piece}-${p}`}
                  style={{
                    display: "inline-block",
                    opacity: t,
                    translate: `0 ${interpolate(t, [0, 1], [rise, 0])}em`,
                    filter: `blur(${interpolate(t, [0, 1], [blur, 0])}px)`,
                    ...pieceStyle,
                  }}
                >
                  {piece}
                </span>
              );
            })}
          </span>
        );
      })}
    </div>
  );
};
