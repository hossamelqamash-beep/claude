import type React from "react";
import { Circle, Star, Triangle } from "@remotion/shapes";
import { AbsoluteFill, useVideoConfig } from "remotion";
import {
  AnimatedText,
  Background,
  Kicker,
  RevealLine,
  ShapePop,
} from "../components";
import { COLORS, FONTS } from "../theme";

export type IntroSceneProps = {
  readonly title: string;
  readonly subtitle: string;
  readonly accentColor: string;
  readonly secondaryColor: string;
};

/** Opening title card: kicker, character-by-character headline, subtitle. */
export const IntroScene: React.FC<IntroSceneProps> = ({
  title,
  subtitle,
  accentColor,
  secondaryColor,
}) => {
  const { fps, width, height } = useVideoConfig();

  return (
    <AbsoluteFill style={{ fontFamily: FONTS.body }}>
      <Background accentColor={accentColor} secondaryColor={secondaryColor} />

      <ShapePop x={width * 0.8} y={height * 0.28} delay={0.3 * fps} spin={12}>
        <Circle
          radius={130}
          fill="transparent"
          stroke={secondaryColor}
          strokeWidth={6}
        />
      </ShapePop>
      <ShapePop x={width * 0.88} y={height * 0.7} delay={0.5 * fps} spin={-25}>
        <Triangle
          length={150}
          direction="up"
          fill={COLORS.coral}
          cornerRadius={12}
        />
      </ShapePop>
      <ShapePop x={width * 0.7} y={height * 0.78} delay={0.7 * fps} spin={40}>
        <Star
          points={5}
          innerRadius={28}
          outerRadius={60}
          fill={COLORS.amber}
          cornerRadius={4}
        />
      </ShapePop>

      <AbsoluteFill
        style={{
          padding: "0 160px",
          justifyContent: "center",
          gap: 40,
        }}
      >
        <Kicker color={secondaryColor} delay={0.2 * fps}>
          Remotion · Motion Studio
        </Kicker>
        <AnimatedText
          text={title}
          by="char"
          delay={0.4 * fps}
          stagger={2}
          style={{
            maxWidth: width * 0.62,
            fontFamily: FONTS.display,
            fontWeight: 700,
            fontSize: 150,
            lineHeight: 1.02,
            letterSpacing: "-0.03em",
            color: COLORS.text,
          }}
        />
        <RevealLine
          delay={1.3 * fps}
          background={`linear-gradient(90deg, ${accentColor}, ${secondaryColor})`}
        />
        <AnimatedText
          text={subtitle}
          delay={1.5 * fps}
          stagger={3}
          rise={0.8}
          style={{
            maxWidth: width * 0.55,
            fontSize: 42,
            lineHeight: 1.35,
            color: COLORS.textMuted,
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
