import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

/**
 * Fonts are self-hosted from public/fonts so renders work offline and are
 * deterministic. loadFont() delays rendering until each font is ready.
 *
 * To use any Google Font instead (needs network at render time):
 *   import { loadFont } from "@remotion/google-fonts/Montserrat";
 *   const { fontFamily } = loadFont("normal", { weights: ["400", "700"], subsets: ["latin"] });
 */
const DISPLAY_FAMILY = "Space Grotesk";
const BODY_FAMILY = "Inter";

loadFont({
  family: DISPLAY_FAMILY,
  url: staticFile("fonts/SpaceGrotesk-Variable.woff2"),
  weight: "400 700",
});
loadFont({
  family: BODY_FAMILY,
  url: staticFile("fonts/Inter-Variable.woff2"),
  weight: "400 700",
});

export const FONTS = {
  display: `"${DISPLAY_FAMILY}", system-ui, sans-serif`,
  body: `"${BODY_FAMILY}", system-ui, sans-serif`,
} as const;
