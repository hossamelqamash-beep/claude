import type React from "react";
import { useId } from "react";

type LiquidGlassProps = {
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
  readonly radius: number;
  /** Depth of the bevel that bends the background, in px. */
  readonly bezel?: number;
  /** Strength of the edge refraction (feDisplacementMap scale). */
  readonly refraction?: number;
  /** Frost blur of what is seen through the glass, in px. */
  readonly blur?: number;
  /** -0.3..1.3 position of a diagonal specular sweep; outside 0..1 = hidden. */
  readonly sheen?: number;
  readonly opacity?: number;
  readonly children?: React.ReactNode;
  readonly style?: React.CSSProperties;
};

/**
 * Builds a displacement map for a rounded rectangle: neutral (no shift) in
 * the middle, ramping towards the edges so the backdrop bends like it does
 * through a thick glass bevel.
 */
const displacementMap = (w: number, h: number, r: number, bezel: number) => {
  const W = Math.max(1, Math.round(w));
  const H = Math.max(1, Math.round(h));
  const bx = Math.min(0.49, bezel / W);
  const by = Math.min(0.49, bezel / H);
  const inset = bezel * 0.85;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<defs>
<linearGradient id="x" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="rgb(0,0,0)"/><stop offset="${bx}" stop-color="rgb(128,0,0)"/>
<stop offset="${1 - bx}" stop-color="rgb(128,0,0)"/><stop offset="1" stop-color="rgb(255,0,0)"/>
</linearGradient>
<linearGradient id="y" x1="0" x2="0" y1="0" y2="1">
<stop offset="0" stop-color="rgb(0,0,0)"/><stop offset="${by}" stop-color="rgb(0,128,0)"/>
<stop offset="${1 - by}" stop-color="rgb(0,128,0)"/><stop offset="1" stop-color="rgb(0,255,0)"/>
</linearGradient>
<filter id="b"><feGaussianBlur stdDeviation="${bezel * 0.35}"/></filter>
</defs>
<rect width="${W}" height="${H}" fill="url(#x)"/>
<rect width="${W}" height="${H}" fill="url(#y)" style="mix-blend-mode:screen"/>
<rect x="${inset}" y="${inset}" width="${W - inset * 2}" height="${H - inset * 2}" rx="${Math.max(0, r - inset)}" fill="rgb(128,128,0)" filter="url(#b)"/>
</svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
};

/**
 * A liquid-glass surface: the backdrop is refracted at the rim, frosted and
 * saturated, with a bright rim light and an optional moving specular sheen.
 */
export const LiquidGlass: React.FC<LiquidGlassProps> = ({
  left,
  top,
  width,
  height,
  radius,
  bezel = 34,
  refraction = 70,
  blur = 10,
  sheen = -1,
  opacity = 1,
  children,
  style,
}) => {
  const id = `lg-${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const r = Math.min(radius, width / 2, height / 2);
  const W = Math.max(1, Math.round(width));
  const H = Math.max(1, Math.round(height));

  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width,
        height,
        borderRadius: r,
        opacity,
        backdropFilter: `url(#${id}) blur(${blur}px) saturate(1.7) brightness(1.12)`,
        background:
          "linear-gradient(160deg, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0.05) 45%, rgba(120,200,255,0.08) 100%)",
        boxShadow: [
          "inset 0 1.5px 0 rgba(255,255,255,0.65)",
          "inset 0 -1px 0 rgba(255,255,255,0.18)",
          `inset 0 0 ${Math.round(bezel * 0.9)}px rgba(255,255,255,0.10)`,
          "0 40px 90px rgba(3, 0, 30, 0.55)",
          "0 6px 18px rgba(3, 0, 30, 0.35)",
        ].join(", "),
        overflow: "hidden",
        ...style,
      }}
    >
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter
          id={id}
          x="0"
          y="0"
          width={W}
          height={H}
          filterUnits="userSpaceOnUse"
          colorInterpolationFilters="sRGB"
        >
          <feImage
            href={displacementMap(W, H, r, bezel)}
            x="0"
            y="0"
            width={W}
            height={H}
            result="map"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="map"
            scale={refraction}
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>
      </svg>
      {/* Rim light: a gradient hairline, brightest where the light hits. */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: r,
          padding: 1.6,
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.15) 30%, rgba(255,255,255,0.05) 55%, rgba(128,219,255,0.55) 100%)",
          WebkitMask:
            "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
          WebkitMaskComposite: "xor",
          maskComposite: "exclude",
        }}
      />
      {sheen > -0.3 && sheen < 1.3 ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(110deg, transparent ${(sheen - 0.18) * 100}%, rgba(255,255,255,0.22) ${sheen * 100}%, transparent ${(sheen + 0.18) * 100}%)`,
            mixBlendMode: "screen",
          }}
        />
      ) : null}
      {children}
    </div>
  );
};
