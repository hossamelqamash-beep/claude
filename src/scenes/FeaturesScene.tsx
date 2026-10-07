import type React from "react";
import { Circle, Rect, Triangle } from "@remotion/shapes";
import { AbsoluteFill, useVideoConfig } from "remotion";
import { stagger } from "../animation";
import { AnimatedText, Background, FeatureCard, Kicker } from "../components";
import { COLORS, FONTS } from "../theme";

export type FeaturesSceneProps = {
  readonly accentColor: string;
  readonly secondaryColor: string;
};

/** Headline plus three staggered feature cards. */
export const FeaturesScene: React.FC<FeaturesSceneProps> = ({
  accentColor,
  secondaryColor,
}) => {
  const { fps } = useVideoConfig();
  const cardDelay = (i: number) => stagger(i, 0.2 * fps, 0.9 * fps);

  return (
    <AbsoluteFill style={{ fontFamily: FONTS.body }}>
      <Background accentColor={accentColor} secondaryColor={COLORS.coral} />
      <AbsoluteFill
        style={{
          padding: "120px 140px",
          gap: 36,
        }}
      >
        <Kicker color={accentColor} delay={0.1 * fps}>
          Built for AI agents
        </Kicker>
        <AnimatedText
          text="Every frame is a React component."
          delay={0.25 * fps}
          stagger={3}
          style={{
            fontFamily: FONTS.display,
            fontWeight: 700,
            fontSize: 96,
            letterSpacing: "-0.02em",
            color: COLORS.text,
          }}
        />
        <div style={{ display: "flex", gap: 40, marginTop: 40 }}>
          <FeatureCard
            delay={cardDelay(0)}
            accentColor={accentColor}
            icon={
              <Rect
                width={44}
                height={44}
                cornerRadius={10}
                fill={accentColor}
              />
            }
            title="Compositions"
            body="Scenes are components. Resolution, fps and duration live in one config file."
          />
          <FeatureCard
            delay={cardDelay(1)}
            accentColor={secondaryColor}
            icon={<Circle radius={24} fill={secondaryColor} />}
            title="Animation utilities"
            body="Shared easings, springs, staggers and beat-sync helpers keep motion consistent."
          />
          <FeatureCard
            delay={cardDelay(2)}
            accentColor={COLORS.coral}
            icon={
              <Triangle
                length={50}
                direction="right"
                cornerRadius={6}
                fill={COLORS.coral}
              />
            }
            title="Render anywhere"
            body="Preview live in Remotion Studio, then render a frame-perfect MP4 from the CLI."
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
