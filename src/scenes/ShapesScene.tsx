import type React from "react";
import { Circle, Polygon, Rect, Star, Triangle } from "@remotion/shapes";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { EASE, progress, stagger } from "../animation";
import { AnimatedText, Background, ShapePop } from "../components";
import { COLORS, FONTS } from "../theme";

export type ShapesSceneProps = {
  readonly accentColor: string;
  readonly secondaryColor: string;
};

/** Geometry showcase: a ring draws itself while shapes pop in around it. */
export const ShapesScene: React.FC<ShapesSceneProps> = ({
  accentColor,
  secondaryColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const cx = width / 2;
  const cy = height * 0.56;
  const ringRadius = 300;
  const circumference = 2 * Math.PI * ringRadius;
  const draw = progress(frame, 0.2 * fps, 1.4 * fps, EASE.inOut);
  const orbit = (frame / fps) * 24; // degrees per second

  // Five slots evenly spaced on the ring, rotating slowly as a group.
  const slot = (i: number) => {
    const angle = ((orbit + i * 72 - 90) * Math.PI) / 180;
    return {
      x: cx + Math.cos(angle) * ringRadius,
      y: cy + Math.sin(angle) * ringRadius,
    };
  };
  const delay = (i: number) => stagger(i, 0.15 * fps, 0.6 * fps);

  return (
    <AbsoluteFill style={{ fontFamily: FONTS.body }}>
      <Background accentColor={secondaryColor} secondaryColor={accentColor} />

      <AbsoluteFill style={{ alignItems: "center", paddingTop: 90 }}>
        <AnimatedText
          text="Shapes & geometry"
          delay={0.1 * fps}
          style={{
            fontFamily: FONTS.display,
            fontWeight: 700,
            fontSize: 88,
            letterSpacing: "-0.02em",
            color: COLORS.text,
          }}
        />
      </AbsoluteFill>

      <svg
        width={width}
        height={height}
        style={{ position: "absolute", inset: 0 }}
      >
        <circle
          cx={cx}
          cy={cy}
          r={ringRadius}
          fill="none"
          stroke={COLORS.surfaceBorder}
          strokeWidth={3}
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - draw)}
          transform={`rotate(-90 ${cx} ${cy})`}
        />
        <circle
          cx={cx}
          cy={cy}
          r={ringRadius - 70}
          fill="none"
          stroke={accentColor}
          strokeOpacity={0.35}
          strokeWidth={2}
          strokeDasharray="4 14"
          transform={`rotate(${orbit * -1.5} ${cx} ${cy})`}
          opacity={draw}
        />
      </svg>

      <ShapePop {...slot(0)} delay={delay(0)} spin={0}>
        <Circle radius={64} fill={accentColor} />
      </ShapePop>
      <ShapePop {...slot(1)} delay={delay(1)} spin={30}>
        <Rect
          width={120}
          height={120}
          cornerRadius={24}
          fill={secondaryColor}
        />
      </ShapePop>
      <ShapePop {...slot(2)} delay={delay(2)} spin={-20}>
        <Triangle
          length={140}
          direction="up"
          cornerRadius={14}
          fill={COLORS.coral}
        />
      </ShapePop>
      <ShapePop {...slot(3)} delay={delay(3)} spin={45}>
        <Star
          points={5}
          innerRadius={36}
          outerRadius={78}
          cornerRadius={6}
          fill={COLORS.amber}
        />
      </ShapePop>
      <ShapePop {...slot(4)} delay={delay(4)} spin={-35}>
        <Polygon points={6} radius={70} cornerRadius={10} fill={COLORS.text} />
      </ShapePop>

      <div
        style={{
          position: "absolute",
          left: cx,
          top: cy,
          translate: "-50% -50%",
          textAlign: "center",
          fontFamily: FONTS.display,
          fontWeight: 500,
          fontSize: 44,
          color: COLORS.textMuted,
          opacity: progress(frame, 1.6 * fps, 0.6 * fps),
          scale: String(
            interpolate(
              progress(frame, 1.6 * fps, 0.6 * fps),
              [0, 1],
              [0.85, 1],
            ),
          ),
        }}
      >
        @remotion/shapes
      </div>
    </AbsoluteFill>
  );
};
