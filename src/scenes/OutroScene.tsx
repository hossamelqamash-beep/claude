import type React from "react";
import { Circle, Triangle } from "@remotion/shapes";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { beatPulse, progress, SPRING, springIn } from "../animation";
import { AnimatedText, Background, Counter } from "../components";
import { COLORS, FONTS } from "../theme";

/** Tempo of public/audio/soundtrack.mp3 — keep in sync if you swap the track. */
export const SOUNDTRACK_BPM = 120;

export type OutroSceneProps = {
  readonly cta: string;
  readonly accentColor: string;
  readonly secondaryColor: string;
};

/** Closing card: beat-synced logo, headline, live spec counters and CTA. */
export const OutroScene: React.FC<OutroSceneProps> = ({
  cta,
  accentColor,
  secondaryColor,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();

  const logoIn = springIn({
    frame,
    fps,
    delay: 0.1 * fps,
    config: SPRING.bouncy,
  });
  const pulse = beatPulse(frame, SOUNDTRACK_BPM, fps);
  const ctaIn = springIn({
    frame,
    fps,
    delay: 1.8 * fps,
    config: SPRING.snappy,
  });
  const fadeOut = 1 - progress(frame, durationInFrames - 0.6 * fps, 0.6 * fps);

  const stat: React.CSSProperties = {
    fontFamily: FONTS.display,
    fontWeight: 700,
    fontSize: 56,
    color: COLORS.text,
  };
  const statLabel: React.CSSProperties = {
    fontSize: 22,
    letterSpacing: "0.14em",
    textTransform: "uppercase",
    color: COLORS.textMuted,
  };

  return (
    <AbsoluteFill style={{ fontFamily: FONTS.body, opacity: fadeOut }}>
      <Background accentColor={accentColor} secondaryColor={secondaryColor} />
      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          gap: 48,
        }}
      >
        {/* Logo: ring pulses on every beat of the soundtrack. */}
        <div
          style={{
            position: "relative",
            width: 220,
            height: 220,
            scale: String(logoIn),
            rotate: `${interpolate(logoIn, [0, 1], [-120, 0])}deg`,
          }}
        >
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              scale: String(1 + 0.08 * pulse),
              filter: `drop-shadow(0 0 ${20 + 30 * pulse}px ${accentColor})`,
            }}
          >
            <Circle
              radius={104}
              fill="transparent"
              stroke={accentColor}
              strokeWidth={10}
            />
          </div>
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              paddingLeft: 14,
            }}
          >
            <Triangle
              length={96}
              direction="right"
              cornerRadius={10}
              fill={secondaryColor}
            />
          </div>
        </div>

        <AnimatedText
          text="Now make something moving."
          delay={0.5 * fps}
          stagger={3}
          style={{
            justifyContent: "center",
            fontFamily: FONTS.display,
            fontWeight: 700,
            fontSize: 104,
            letterSpacing: "-0.02em",
            color: COLORS.text,
          }}
        />

        {/* Live specs read from useVideoConfig(), so they follow config/video.ts. */}
        <div
          style={{
            display: "flex",
            gap: 90,
            opacity: progress(frame, 1.1 * fps, 0.5 * fps),
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 6,
            }}
          >
            <span style={stat}>
              <Counter to={width} delay={1.1 * fps} duration={fps} />×
              <Counter to={height} delay={1.1 * fps} duration={fps} />
            </span>
            <span style={statLabel}>Resolution</span>
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 6,
            }}
          >
            <Counter to={fps} delay={1.2 * fps} duration={fps} style={stat} />
            <span style={statLabel}>Frames / sec</span>
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 6,
            }}
          >
            <Counter
              to={SOUNDTRACK_BPM}
              delay={1.3 * fps}
              duration={fps}
              style={stat}
            />
            <span style={statLabel}>BPM sync</span>
          </div>
        </div>

        <div
          style={{
            marginTop: 12,
            padding: "22px 44px",
            borderRadius: 999,
            background: `linear-gradient(100deg, ${accentColor}, ${secondaryColor})`,
            color: COLORS.background,
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            fontWeight: 700,
            fontSize: 36,
            opacity: Math.min(1, ctaIn * 1.4),
            scale: String(interpolate(ctaIn, [0, 1], [0.7, 1])),
          }}
        >
          {cta}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
