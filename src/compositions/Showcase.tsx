import type React from "react";
import { Audio } from "@remotion/media";
import {
  linearTiming,
  springTiming,
  TransitionSeries,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { zColor } from "@remotion/zod-types";
import {
  AbsoluteFill,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { EASE } from "../animation";
import {
  SHOWCASE_SCENES,
  SHOWCASE_TRANSITION_SECONDS,
  toFrames,
} from "../config/video";
import { FeaturesScene, IntroScene, OutroScene, ShapesScene } from "../scenes";

/** Props editable in the Remotion Studio sidebar. */
export const showcaseSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  cta: z.string(),
  accentColor: zColor(),
  secondaryColor: zColor(),
  withAudio: z.boolean(),
});

export type ShowcaseProps = z.infer<typeof showcaseSchema>;

/**
 * Sample multi-scene video. Scene lengths come from config/video.ts in
 * seconds, so changing the fps keeps the pacing intact.
 */
export const Showcase: React.FC<ShowcaseProps> = ({
  title,
  subtitle,
  cta,
  accentColor,
  secondaryColor,
  withAudio,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const transitionFrames = toFrames(SHOWCASE_TRANSITION_SECONDS, fps);
  const colors = { accentColor, secondaryColor };

  return (
    <AbsoluteFill style={{ backgroundColor: "#0B1020" }}>
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="Intro"
          durationInFrames={toFrames(SHOWCASE_SCENES.intro, fps)}
          premountFor={fps}
        >
          <IntroScene title={title} subtitle={subtitle} {...colors} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={slide({ direction: "from-right" })}
          timing={springTiming({
            config: { damping: 200 },
            durationInFrames: transitionFrames,
          })}
        />
        <TransitionSeries.Sequence
          name="Shapes"
          durationInFrames={toFrames(SHOWCASE_SCENES.shapes, fps)}
          premountFor={fps}
        >
          <ShapesScene {...colors} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={wipe({ direction: "from-bottom-left" })}
          timing={linearTiming({
            durationInFrames: transitionFrames,
            easing: EASE.inOut,
          })}
        />
        <TransitionSeries.Sequence
          name="Features"
          durationInFrames={toFrames(SHOWCASE_SCENES.features, fps)}
          premountFor={fps}
        >
          <FeaturesScene {...colors} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({
            durationInFrames: transitionFrames,
            easing: EASE.inOut,
          })}
        />
        <TransitionSeries.Sequence
          name="Outro"
          durationInFrames={toFrames(SHOWCASE_SCENES.outro, fps)}
          premountFor={fps}
        >
          <OutroScene cta={cta} {...colors} />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      {withAudio ? (
        <Audio
          name="Soundtrack"
          src={staticFile("audio/soundtrack.mp3")}
          premountFor={fps}
          volume={interpolate(
            frame,
            [0, 0.5 * fps, durationInFrames - fps, durationInFrames],
            [0, 0.8, 0.8, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          )}
        />
      ) : null}
    </AbsoluteFill>
  );
};
