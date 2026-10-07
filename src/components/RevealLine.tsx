import type React from "react";
import { useCurrentFrame } from "remotion";
import { progress } from "../animation";
import { GRADIENTS } from "../theme";

type RevealLineProps = {
  readonly delay?: number;
  readonly duration?: number;
  readonly width?: number;
  readonly thickness?: number;
  readonly background?: string;
};

/** Accent bar that wipes in from the left. */
export const RevealLine: React.FC<RevealLineProps> = ({
  delay = 0,
  duration = 24,
  width = 360,
  thickness = 8,
  background = GRADIENTS.brand,
}) => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        width,
        height: thickness,
        borderRadius: thickness,
        background,
        transformOrigin: "left center",
        scale: `${progress(frame, delay, duration)} 1`,
      }}
    />
  );
};
