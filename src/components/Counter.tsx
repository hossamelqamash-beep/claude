import type React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { EASE } from "../animation";

type CounterProps = {
  readonly to: number;
  readonly from?: number;
  readonly delay?: number;
  readonly duration?: number;
  readonly decimals?: number;
  readonly prefix?: string;
  readonly suffix?: string;
  readonly style?: React.CSSProperties;
};

/** Number that counts up. Uses tabular figures so it doesn't jitter. */
export const Counter: React.FC<CounterProps> = ({
  to,
  from = 0,
  delay = 0,
  duration = 40,
  decimals = 0,
  prefix = "",
  suffix = "",
  style,
}) => {
  const frame = useCurrentFrame();
  const value = interpolate(frame, [delay, delay + duration], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE.outExpo,
  });
  return (
    <span style={{ fontVariantNumeric: "tabular-nums", ...style }}>
      {prefix}
      {value.toFixed(decimals)}
      {suffix}
    </span>
  );
};
