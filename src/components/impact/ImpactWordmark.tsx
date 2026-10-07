import type React from "react";
import { useId } from "react";
import { LOGO_VIEWBOX, TAGLINE, WORDMARK } from "./logoPaths";

/** The wordmark lives right of the icon; this is where its slot starts. */
export const WORDMARK_X = 200;

type ImpactWordmarkProps = {
  /** Screen pixels per logo unit. */
  readonly unit: number;
  /** 0..1 per letter of "impact". Letters slide forward out of the slot. */
  readonly letters: readonly number[];
  /** 0..1 per glyph of the tagline. */
  readonly tagline: readonly number[];
  readonly color: string;
  readonly taglineColor: string;
  readonly style?: React.CSSProperties;
};

/**
 * "impact" + "learning and development" from the original logo paths.
 * Each letter travels left → right with a horizontal motion blur that
 * resolves to a sharp edge as it lands.
 */
export const ImpactWordmark: React.FC<ImpactWordmarkProps> = ({
  unit,
  letters,
  tagline,
  color,
  taglineColor,
  style,
}) => {
  const id = useId().replace(/[^a-zA-Z0-9]/g, "");
  const width = LOGO_VIEWBOX.width - WORDMARK_X;
  const slot = `slot-${id}`;

  return (
    <svg
      viewBox={`${WORDMARK_X} 0 ${width} ${LOGO_VIEWBOX.height}`}
      width={width * unit}
      height={LOGO_VIEWBOX.height * unit}
      style={{ overflow: "visible", ...style }}
    >
      <defs>
        <clipPath id={slot}>
          <rect x={WORDMARK_X + 8} y={-50} width={width + 100} height={300} />
        </clipPath>
        {letters.map((t, i) => (
          <filter
            key={i}
            id={`mb-${id}-${i}`}
            x="-50%"
            y="-10%"
            width="200%"
            height="120%"
          >
            <feGaussianBlur stdDeviation={`${(1 - t) * 9} 0`} />
          </filter>
        ))}
      </defs>
      <g clipPath={`url(#${slot})`}>
        {WORDMARK.map((paths, i) => {
          const t = letters[i] ?? 0;
          return (
            <g
              key={i}
              transform={`translate(${-(1 - t) * (70 + i * 16)} 0)`}
              opacity={Math.min(1, t * 1.8)}
              filter={t < 0.999 ? `url(#mb-${id}-${i})` : undefined}
            >
              {paths.map((d) => (
                <path key={d} d={d} fill={color} />
              ))}
            </g>
          );
        })}
        {TAGLINE.map((d, i) => {
          const t = tagline[i] ?? 0;
          return (
            <path
              key={d}
              d={d}
              fill={taglineColor}
              opacity={t}
              transform={`translate(${-(1 - t) * 14} 0)`}
            />
          );
        })}
      </g>
    </svg>
  );
};
