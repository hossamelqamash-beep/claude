import type React from "react";
import { random, useVideoConfig } from "remotion";
import { IMPACT } from "../../theme";

type ForwardTunnelProps = {
  /** Distance travelled through the tunnel, in ring spacings. */
  readonly travel: number;
  /** Current speed (ring spacings per frame) — stretches the light streaks. */
  readonly speed: number;
  /** 0..1 rings collapse into the vanishing point. */
  readonly collapse?: number;
  readonly opacity?: number;
};

const RINGS = 14;
const STREAKS = 90;
const NEAR = 0.32;
const FOCAL = 430;
const RING_COLORS = [IMPACT.cyan, IMPACT.blue, IMPACT.sky, IMPACT.violet];

const smooth = (a: number, b: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

/**
 * Flying forward through concentric ripples: rings travel toward the camera
 * in perspective while light streaks rush past.
 */
export const ForwardTunnel: React.FC<ForwardTunnelProps> = ({
  travel,
  speed,
  collapse = 0,
  opacity = 1,
}) => {
  const { width, height } = useVideoConfig();
  const cx = width / 2;
  const cy = height / 2;
  const shrink = 1 - collapse;

  const rings = Array.from({ length: RINGS }, (_, i) => {
    const z = ((((i - travel) % RINGS) + RINGS) % RINGS) + NEAR;
    const r = (FOCAL / z) * shrink;
    const alpha = smooth(RINGS + NEAR, RINGS - 3, z) * smooth(NEAR, NEAR + 0.9, z);
    const stroke = Math.min(26, 7 / z);
    const color = RING_COLORS[(i + RINGS * 100) % RING_COLORS.length];
    return { i, z, r, alpha, stroke, color };
  }).sort((a, b) => b.z - a.z);

  const streakLength = Math.min(2.2, 0.08 + speed * 9);
  const streaks = Array.from({ length: STREAKS }, (_, i) => {
    const angle = random(`streak-angle-${i}`) * Math.PI * 2;
    const spread = 0.55 + random(`streak-spread-${i}`) * 1.3;
    const span = 9;
    const z =
      ((((random(`streak-phase-${i}`) * span - travel * 1.7) % span) + span) %
        span) +
      0.25;
    const r1 = ((FOCAL * spread) / z) * shrink;
    const r2 = ((FOCAL * spread) / (z + streakLength)) * shrink;
    const alpha = smooth(span, span - 2.5, z) * smooth(0.25, 0.6, z);
    return { i, angle, r1, r2, alpha };
  });

  return (
    <svg
      width={width}
      height={height}
      style={{ position: "absolute", inset: 0, opacity }}
    >
      <defs>
        <filter id="tunnel-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="9" />
        </filter>
        <radialGradient id="tunnel-core">
          <stop offset="0" stopColor="#FFFFFF" stopOpacity={0.55 * shrink} />
          <stop offset="0.25" stopColor={IMPACT.cyan} stopOpacity={0.25 * shrink} />
          <stop offset="1" stopColor={IMPACT.blue} stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx={cx} cy={cy} r={260} fill="url(#tunnel-core)" />
      <g filter="url(#tunnel-glow)">
        {rings.map((ring) => (
          <circle
            key={`g-${ring.i}`}
            cx={cx}
            cy={cy}
            r={ring.r}
            fill="none"
            stroke={ring.color}
            strokeWidth={ring.stroke * 2.4}
            opacity={ring.alpha * 0.55}
          />
        ))}
      </g>
      {rings.map((ring) => (
        <g key={`r-${ring.i}`} opacity={ring.alpha}>
          <circle
            cx={cx}
            cy={cy}
            r={ring.r}
            fill="none"
            stroke={ring.color}
            strokeWidth={ring.stroke}
            opacity={0.8}
          />
          {/* Glass highlight riding on the ring */}
          <circle
            cx={cx}
            cy={cy}
            r={Math.max(0, ring.r - ring.stroke * 0.25)}
            fill="none"
            stroke="#FFFFFF"
            strokeWidth={Math.max(0.8, ring.stroke * 0.18)}
            opacity={0.85}
          />
        </g>
      ))}
      {streaks.map((s) => (
        <line
          key={`s-${s.i}`}
          x1={cx + Math.cos(s.angle) * s.r2}
          y1={cy + Math.sin(s.angle) * s.r2}
          x2={cx + Math.cos(s.angle) * s.r1}
          y2={cy + Math.sin(s.angle) * s.r1}
          stroke={s.i % 3 === 0 ? IMPACT.cyan : "#FFFFFF"}
          strokeWidth={s.i % 5 === 0 ? 2.4 : 1.3}
          strokeLinecap="round"
          opacity={s.alpha * 0.8}
        />
      ))}
    </svg>
  );
};
