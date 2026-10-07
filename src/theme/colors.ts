export const COLORS = {
  background: "#0B1020",
  backgroundAlt: "#141B34",
  surface: "rgba(255, 255, 255, 0.06)",
  surfaceBorder: "rgba(255, 255, 255, 0.12)",
  text: "#F5F7FF",
  textMuted: "#9AA3C7",
  violet: "#7C5CFF",
  cyan: "#22D3EE",
  coral: "#FF6B6B",
  amber: "#FFC857",
} as const;

export const GRADIENTS = {
  brand: `linear-gradient(100deg, ${COLORS.violet} 0%, ${COLORS.cyan} 100%)`,
  warm: `linear-gradient(100deg, ${COLORS.coral} 0%, ${COLORS.amber} 100%)`,
} as const;
