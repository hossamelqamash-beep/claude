import type React from "react";
import { Audio } from "@remotion/media";
import { zColor } from "@remotion/zod-types";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { EASE, mix, progress, springIn } from "../animation";
import {
  ForwardText,
  ForwardTunnel,
  GlassDrop,
  GlassRipple,
  ImpactBackground,
  ImpactIcon,
  ImpactWordmark,
  LiquidGlass,
  LOGO_VIEWBOX,
  RIPPLE_ORIGIN,
  WORDMARK_X,
} from "../components/impact";
import { IMPACT_CUES as C } from "../config/video";

/** Props editable in the Remotion Studio sidebar. */
export const impactLogoSchema = z.object({
  line1: z.string(),
  line2: z.string(),
  wordmarkColor: zColor(),
  taglineColor: zColor(),
  withAudio: z.boolean(),
});

export type ImpactLogoProps = z.infer<typeof impactLogoSchema>;

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ICON_CENTER_Y = LOGO_VIEWBOX.height / 2;
/** Liquid, slightly wobbly spring for glass and logo parts. */
const LIQUID = { damping: 12, stiffness: 120, mass: 0.75 } as const;

/**
 * 30 s Impact logo animation.
 *
 * 1. The drop (0–4 s): a glass droplet falls and hits — glass ripples spread.
 * 2. Forward (4–11 s): we fly forward through a tunnel of ripples.
 * 3. The mark (11–15 s): the icon forms ripple by ripple from its pillar.
 * 4. Lockup (15–24 s): the icon steps aside, a liquid-glass capsule stretches
 *    forward and "impact" streams out; a glass lens sweeps across.
 * 5. Echo (24–30 s): the mark echoes its ripples and a last wave rolls out.
 */
export const ImpactLogo: React.FC<ImpactLogoProps> = ({
  line1,
  line2,
  wordmarkColor,
  taglineColor,
  withAudio,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const sec = (s: number) => s * fps;
  const cx = width / 2;
  const cy = height / 2;

  /** 1 at `at` seconds, decaying exponentially. */
  const pulse = (at: number, decay = 0.35) =>
    frame < sec(at) ? 0 : Math.exp(-(frame - sec(at)) / sec(decay));

  // ── Background ────────────────────────────────────────────────────────
  const reveal = progress(frame, 0, sec(1.2));
  const energy = Math.min(
    1,
    pulse(C.impact) + 0.7 * pulse(C.pillar, 0.5) + 0.45 * pulse(C.echo, 0.6),
  );

  // ── 1. The drop ───────────────────────────────────────────────────────
  const fall = progress(
    frame,
    sec(C.dropStart),
    sec(C.impact - C.dropStart),
    Easing.in(Easing.quad),
  );
  const splash = progress(frame, sec(C.impact), sec(0.22), EASE.outExpo);
  const dropY = mix(fall, -140, cy);

  // ── 2. Forward tunnel ─────────────────────────────────────────────────
  const travelAt = (f: number) =>
    interpolate(f, [sec(C.tunnelIn), sec(C.pillar)], [0, 30], {
      ...CLAMP,
      easing: EASE.inOut,
    });
  const travel = travelAt(frame);
  const speed = travel - travelAt(frame - 1);
  const collapse = progress(frame, sec(C.collapse), sec(1), EASE.inQuart);
  const tunnelOpacity =
    progress(frame, sec(C.tunnelIn), sec(1)) *
    (1 - progress(frame, sec(C.pillar - 0.25), sec(0.3)));
  const showTunnel =
    frame >= sec(C.tunnelIn) && frame <= sec(C.pillar + 0.1);

  // ── 3. The mark forms ─────────────────────────────────────────────────
  const pillar = progress(frame, sec(C.pillar), sec(0.8));
  const archAt = (i: number) => C.arches + i * 0.25;
  const arcAt = (i: number) => C.arcs + i * 0.25;
  const arches = [0, 1, 2].map((i) =>
    springIn({ frame, fps, delay: sec(archAt(i)), config: LIQUID }),
  ) as [number, number, number];
  const arcs = [0, 1, 2].map((i) =>
    springIn({ frame, fps, delay: sec(arcAt(i)), config: LIQUID }),
  ) as [number, number, number];
  // Each part arrives glowing white, then echoes again at the finale.
  const echo = [0, 1, 2, 3, 4, 5].map((i) => {
    const born = i < 3 ? archAt(i) : arcAt(i - 3);
    return Math.min(
      1,
      0.9 * pulse(born, 0.3) + pulse(C.echo + i * 0.12, 0.28),
    );
  });
  const light =
    0.5 - 0.48 * Math.cos(Math.max(0, frame / fps - C.pillar) * 0.55);

  // ── Layout: big centred icon → horizontal lockup ──────────────────────
  const push = interpolate(
    frame,
    [sec(C.lockup), durationInFrames],
    [1, 1.045],
    CLAMP,
  );
  const lockUnit = 2.1 * push;
  const bigUnit = 3.3 * (1 + 0.05 * progress(frame, sec(C.pillar), sec(4), EASE.inOut));
  const move = progress(frame, sec(C.lockup), sec(1.5), EASE.inOut);
  const x0 = cx - (LOGO_VIEWBOX.width * lockUnit) / 2;
  const y0 = cy - ICON_CENTER_Y * lockUnit;
  const unit = mix(move, bigUnit, lockUnit);
  const iconCx = mix(move, cx, x0 + RIPPLE_ORIGIN.x * lockUnit);
  const iconLeft = iconCx - RIPPLE_ORIGIN.x * unit;
  const iconTop = cy - ICON_CENTER_Y * unit;
  const originY = iconTop + RIPPLE_ORIGIN.y * unit;
  const lockOriginX = x0 + RIPPLE_ORIGIN.x * lockUnit;
  const lockOriginY = y0 + RIPPLE_ORIGIN.y * lockUnit;

  // ── 4. Liquid-glass capsule ───────────────────────────────────────────
  const capsule = LOGO_VIEWBOX.height * lockUnit + 2 * 77 * push;
  const grow = springIn({ frame, fps, delay: sec(C.lockup + 0.3), config: LIQUID });
  const stretch = springIn({
    frame,
    fps,
    delay: sec(C.lockup + 0.8),
    config: { damping: 14, stiffness: 70, mass: 1 },
  });
  const finalRight = x0 + LOGO_VIEWBOX.width * lockUnit + 70 * push;
  const pillLeft = iconCx - (capsule / 2) * grow;
  const pillRight =
    iconCx + (capsule / 2) * grow + stretch * (finalRight - (iconCx + capsule / 2));
  const pillHeight =
    capsule * grow * (1 - 0.08 * Math.sin(Math.PI * Math.min(1, stretch)));
  const sheenAt = (at: number) =>
    interpolate(frame, [sec(at), sec(at + 1.6)], [-0.3, 1.3], {
      ...CLAMP,
      easing: EASE.inOut,
    });
  const sheen = frame < sec(C.sheen2) ? sheenAt(C.sheen) : sheenAt(C.sheen2);

  const letters = Array.from({ length: 6 }, (_, i) =>
    progress(frame, sec(C.letters + i * 0.075), sec(0.9)),
  );
  const tagline = Array.from({ length: 23 }, (_, i) =>
    progress(frame, sec(C.tagline + i * 0.03), sec(0.7)),
  );

  const lensT = progress(frame, sec(C.lens), sec(3.6), EASE.inOut);
  const lensSize = 300 * push;

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <ImpactBackground energy={energy} reveal={reveal} />

      {/* Act 1: impact ripples */}
      {[0, 0.25, 0.5, 1, 1.6].map((offset, i) => (
        <GlassRipple
          key={`impact-${offset}`}
          x={cx}
          y={cy}
          from={sec(C.impact + offset)}
          seconds={2.8}
          endRadius={1250 - i * 90}
          thickness={64 - i * 9}
        />
      ))}

      {/* Act 3: the mark sends out ripples as it forms */}
      <GlassRipple x={cx} y={originY} from={sec(C.pillar)} endRadius={1100} thickness={56} />
      <GlassRipple x={cx} y={originY} from={sec(C.arcs + 0.5)} endRadius={1250} thickness={44} strength={0.8} />
      <GlassRipple x={cx} y={originY} from={sec(13.75)} seconds={2.6} endRadius={1300} thickness={40} strength={0.65} />

      {/* Act 4/5: ripples from the lockup */}
      <GlassRipple x={lockOriginX} y={lockOriginY} from={sec(18.25)} seconds={3} endRadius={1500} thickness={42} strength={0.55} />
      <GlassRipple x={lockOriginX} y={lockOriginY} from={sec(C.echo)} seconds={3.2} endRadius={1900} thickness={70} />
      <GlassRipple x={lockOriginX} y={lockOriginY} from={sec(C.echo + 0.3)} seconds={3.2} endRadius={1800} thickness={50} strength={0.8} />
      <GlassRipple x={lockOriginX} y={lockOriginY} from={sec(C.echo + 0.6)} seconds={3.2} endRadius={1700} thickness={36} strength={0.6} />
      <GlassRipple x={lockOriginX} y={lockOriginY} from={sec(27.75)} seconds={2.6} endRadius={1500} thickness={36} strength={0.45} />

      {/* Act 2: forward through the ripples */}
      {showTunnel ? (
        <ForwardTunnel
          travel={travel}
          speed={speed}
          collapse={collapse}
          opacity={tunnelOpacity}
        />
      ) : null}

      {/* Act 1: the droplet */}
      {frame >= sec(C.dropStart) && splash < 1 ? (
        <GlassDrop
          x={cx}
          y={dropY}
          size={84 * (1 - splash * 0.6)}
          stretch={1 + 0.35 * fall - 0.75 * splash}
          opacity={progress(frame, sec(C.dropStart), sec(0.3)) * (1 - splash)}
        />
      ) : null}

      <ForwardText
        text={line1}
        inFrame={sec(C.line1In)}
        outFrame={sec(C.line1Out)}
        style={{ top: cy - 48 }}
      />
      <ForwardText
        text={line2}
        inFrame={sec(C.line2In)}
        outFrame={sec(C.line2Out)}
        style={{ top: cy - 48 }}
      />

      {/* Act 4: the liquid-glass capsule the lockup sits in */}
      {grow > 0.001 ? (
        <LiquidGlass
          left={pillLeft}
          top={cy - pillHeight / 2}
          width={pillRight - pillLeft}
          height={pillHeight}
          radius={pillHeight / 2}
          bezel={42}
          refraction={80}
          blur={14}
          sheen={sheen}
        />
      ) : null}

      {frame >= sec(C.pillar) ? (
        <ImpactIcon
          unit={unit}
          pillar={pillar}
          arches={arches}
          arcs={arcs}
          echo={echo}
          light={light}
          style={{
            position: "absolute",
            left: iconLeft,
            top: iconTop,
            filter: "drop-shadow(0 18px 30px rgba(3, 0, 40, 0.45))",
          }}
        />
      ) : null}

      {frame >= sec(C.letters) ? (
        <ImpactWordmark
          unit={lockUnit}
          letters={letters}
          tagline={tagline}
          color={wordmarkColor}
          taglineColor={taglineColor}
          style={{ position: "absolute", left: x0 + WORDMARK_X * lockUnit, top: y0 }}
        />
      ) : null}

      {/* Act 4: a liquid-glass lens rolls forward across the lockup */}
      {lensT > 0 && lensT < 1 ? (
        <LiquidGlass
          left={mix(lensT, -lensSize * 1.2, width + lensSize * 0.2)}
          top={cy - lensSize / 2}
          width={lensSize}
          height={lensSize}
          radius={lensSize / 2}
          bezel={70}
          refraction={140}
          blur={0.6}
          style={{ background: "rgba(255,255,255,0.04)" }}
        />
      ) : null}

      {withAudio ? (
        <Audio
          name="Soundtrack"
          src={staticFile("audio/soundtrack.mp3")}
          loop
          premountFor={fps}
          volume={interpolate(
            frame,
            [0, sec(0.8), durationInFrames - sec(2), durationInFrames],
            [0, 0.8, 0.8, 0],
            CLAMP,
          )}
        />
      ) : null}
    </AbsoluteFill>
  );
};
