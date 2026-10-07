import { Composition, Folder } from "remotion";
import { ImpactLogo, impactLogoSchema } from "./compositions/ImpactLogo";
import { Showcase, showcaseSchema } from "./compositions/Showcase";
import {
  getShowcaseDurationInFrames,
  IMPACT_LOGO_SECONDS,
  SHOWCASE_SCENES,
  toFrames,
  VIDEO,
} from "./config/video";
import { FeaturesScene, IntroScene, OutroScene, ShapesScene } from "./scenes";

/**
 * Registers every renderable composition.
 * Resolution, fps and durations come from src/config/video.ts.
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ImpactLogo"
        component={ImpactLogo}
        schema={impactLogoSchema}
        width={VIDEO.width}
        height={VIDEO.height}
        fps={VIDEO.fps}
        durationInFrames={toFrames(IMPACT_LOGO_SECONDS, VIDEO.fps)}
        defaultProps={{
          line1: "Every drop makes an impact.",
          line2: "Every ripple moves us forward.",
          wordmarkColor: "#FFFFFF",
          taglineColor: "#BDEBFF",
          withAudio: true,
        }}
      />
      <Composition
        id="Showcase"
        component={Showcase}
        schema={showcaseSchema}
        width={VIDEO.width}
        height={VIDEO.height}
        fps={VIDEO.fps}
        durationInFrames={getShowcaseDurationInFrames(VIDEO.fps)}
        defaultProps={{
          title: "Motion, made with code.",
          subtitle:
            "Programmatic motion graphics with React, rendered frame by frame.",
          cta: "npm run dev",
          accentColor: "#7C5CFF",
          secondaryColor: "#22D3EE",
          withAudio: true,
        }}
      />

      {/* Each scene on its own, for focused previewing and iteration. */}
      <Folder name="Scenes">
        <Composition
          id="Intro"
          component={IntroScene}
          width={VIDEO.width}
          height={VIDEO.height}
          fps={VIDEO.fps}
          durationInFrames={toFrames(SHOWCASE_SCENES.intro, VIDEO.fps)}
          defaultProps={{
            title: "Motion, made with code.",
            subtitle:
              "Programmatic motion graphics with React, rendered frame by frame.",
            accentColor: "#7C5CFF",
            secondaryColor: "#22D3EE",
          }}
        />
        <Composition
          id="Shapes"
          component={ShapesScene}
          width={VIDEO.width}
          height={VIDEO.height}
          fps={VIDEO.fps}
          durationInFrames={toFrames(SHOWCASE_SCENES.shapes, VIDEO.fps)}
          defaultProps={{ accentColor: "#7C5CFF", secondaryColor: "#22D3EE" }}
        />
        <Composition
          id="Features"
          component={FeaturesScene}
          width={VIDEO.width}
          height={VIDEO.height}
          fps={VIDEO.fps}
          durationInFrames={toFrames(SHOWCASE_SCENES.features, VIDEO.fps)}
          defaultProps={{ accentColor: "#7C5CFF", secondaryColor: "#22D3EE" }}
        />
        <Composition
          id="Outro"
          component={OutroScene}
          width={VIDEO.width}
          height={VIDEO.height}
          fps={VIDEO.fps}
          durationInFrames={toFrames(SHOWCASE_SCENES.outro, VIDEO.fps)}
          defaultProps={{
            cta: "npm run dev",
            accentColor: "#7C5CFF",
            secondaryColor: "#22D3EE",
          }}
        />
      </Folder>
    </>
  );
};
