/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// MP4 (H.264) output with good quality/size balance.
Config.setCodec("h264");
Config.setCrf(18);

// Optional: use an already-installed Chrome / Chrome Headless Shell instead
// of letting Remotion download one (useful in CI or locked-down networks).
//   REMOTION_BROWSER_EXECUTABLE=/path/to/chrome-headless-shell npm run render
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
