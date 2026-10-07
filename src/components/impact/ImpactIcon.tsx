import type React from "react";
import { useId } from "react";
import { IMPACT } from "../../theme";
import {
  ARCHES,
  ARCS,
  ICON_WIDTH,
  LOGO_VIEWBOX,
  PILLAR,
  RIPPLE_ORIGIN,
} from "./logoPaths";

type ImpactIconProps = {
  /** Screen pixels per logo unit. The SVG is sized directly, so it stays crisp. */
  readonly unit: number;
  /** 0..1 rise of the pillar out of the ground. */
  readonly pillar: number;
  /** 0..1 ripple-out of the three arches, inner → outer. */
  readonly arches: readonly [number, number, number];
  /** 0..1 ripple-out of the three upper arcs, inner → outer. */
  readonly arcs: readonly [number, number, number];
  /** 0..1 white "echo" flash per part: [arch1-3, arc1-3]. */
  readonly echo?: readonly number[];
  /** 0..1 horizontal position of the specular light sweeping the glass. */
  readonly light: number;
  readonly style?: React.CSSProperties;
};

const { x: OX, y: OY } = RIPPLE_ORIGIN;

/** Scales a part out of the shared ripple origin. */
const rippleTransform = (t: number) => {
  const s = 0.35 + 0.65 * t;
  return `translate(${OX} ${OY}) scale(${s}) translate(${-OX} ${-OY})`;
};

/**
 * The Impact mark rendered as glossy liquid glass: brand gradient fill,
 * a moving specular highlight (feSpecularLighting) and a refracted rim.
 */
export const ImpactIcon: React.FC<ImpactIconProps> = ({
  unit,
  pillar,
  arches,
  arcs,
  echo = [0, 0, 0, 0, 0, 0],
  light,
  style,
}) => {
  const id = useId().replace(/[^a-zA-Z0-9]/g, "");
  const gradient = `grad-${id}`;
  const glass = `glass-${id}`;
  const ground = `ground-${id}`;

  const part = (d: string, t: number, flash: number, key: string) => (
    <g
      key={key}
      transform={rippleTransform(t)}
      opacity={Math.min(1, t * 1.6)}
    >
      <path d={d} fill={`url(#${gradient})`} />
      {flash > 0.001 ? (
        <path d={d} fill="#FFFFFF" opacity={flash * 0.85} />
      ) : null}
    </g>
  );

  return (
    <svg
      viewBox={`0 0 ${ICON_WIDTH} ${LOGO_VIEWBOX.height}`}
      width={ICON_WIDTH * unit}
      height={LOGO_VIEWBOX.height * unit}
      style={{ overflow: "visible", ...style }}
    >
      <defs>
        <linearGradient
          id={gradient}
          x1="86.35"
          y1="-1.18"
          x2="86.35"
          y2="161.68"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0" stopColor={IMPACT.logoTop} />
          <stop offset="0.55" stopColor={IMPACT.blue} />
          <stop offset="1" stopColor={IMPACT.logoBottom} />
        </linearGradient>
        <clipPath id={ground}>
          <rect x={-200} y={-200} width={600} height={365.03} />
        </clipPath>
        <filter
          id={glass}
          x="-20%"
          y="-20%"
          width="140%"
          height="140%"
          colorInterpolationFilters="sRGB"
        >
          {/* Rounded height map of the shapes → glossy bevel highlight */}
          <feGaussianBlur in="SourceAlpha" stdDeviation="1.6" result="height" />
          <feSpecularLighting
            in="height"
            surfaceScale="3.2"
            specularConstant="1.25"
            specularExponent="22"
            lightingColor="#FFFFFF"
            result="spec"
          >
            <fePointLight x={-60 + light * 300} y={-70} z={110} />
          </feSpecularLighting>
          <feComposite in="spec" in2="SourceAlpha" operator="in" result="specIn" />
          {/* Inner rim: a thin bright edge, like light caught in glass */}
          <feMorphology in="SourceAlpha" operator="erode" radius="0.9" result="eroded" />
          <feComposite in="SourceAlpha" in2="eroded" operator="out" result="rim" />
          <feFlood floodColor="#FFFFFF" floodOpacity="0.55" />
          <feComposite in2="rim" operator="in" result="rimLight" />
          <feMerge>
            <feMergeNode in="SourceGraphic" />
            <feMergeNode in="rimLight" />
            <feMergeNode in="specIn" />
          </feMerge>
        </filter>
      </defs>
      <g filter={`url(#${glass})`}>
        <g clipPath={`url(#${ground})`}>
          <g
            transform={`translate(0 ${(1 - pillar) * 60})`}
            opacity={Math.min(1, pillar * 3)}
          >
            <path d={PILLAR} fill={`url(#${gradient})`} />
          </g>
          {ARCHES.map((d, i) => part(d, arches[i], echo[i] ?? 0, `arch-${i}`))}
        </g>
        {ARCS.map((d, i) => part(d, arcs[i], echo[i + 3] ?? 0, `arc-${i}`))}
      </g>
    </svg>
  );
};
