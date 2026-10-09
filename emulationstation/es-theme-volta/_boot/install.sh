#!/bin/bash
# Volta boot & loading screen installer for ArkOS on the R36S (and other 640x480 RK3326 devices).
#
#   ./install.sh                 install loading screen + font + boot logo
#   ./install.sh --no-bootlogo   only the EmulationStation loading screen
#   ./install.sh --portrait-cw   force the 480x640 clockwise boot logo variant
#   ./install.sh --portrait-ccw  force the 480x640 counter-clockwise variant
#   ./install.sh --uninstall     restore everything that was backed up
#
# Can also be launched from the ArkOS "Ports" menu: copy this file to the ports folder.
#
# What it changes
#  1. ~/.emulationstation/resources/splash.svg
#     EmulationStation looks here before its built-in resources, so this replaces
#     the startup "Loading..." screen and the game-launch loading screen without
#     touching system files.
#  2. ~/.emulationstation/resources/opensans_hebrew_condensed_regular.ttf
#     ES's default font. Replaced with Urbanist so the loading text and the battery
#     percentage match the theme.
#  3. The u-boot boot logo (logo.bmp on the BOOT partition), only if the existing file
#     is a BMP we can match exactly (size + bit depth). The original is backed up.

set -u

SELF_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
BOOTLOGO=1
ROTATE=""
UNINSTALL=0
for a in "$@"; do
  case "$a" in
    --no-bootlogo) BOOTLOGO=0 ;;
    --portrait-cw) ROTATE=cw ;;
    --portrait-ccw) ROTATE=ccw ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown option: $a"; exit 1 ;;
  esac
done

say() { echo "[volta] $*"; }

# --- locate the theme's _boot folder (works from the theme or from ports) ----------
ASSETS=""
for d in "$SELF_DIR" \
         /roms/themes/es-theme-volta/_boot /roms2/themes/es-theme-volta/_boot \
         "$HOME/.emulationstation/themes/es-theme-volta/_boot" \
         /home/ark/.emulationstation/themes/es-theme-volta/_boot \
         /etc/emulationstation/themes/es-theme-volta/_boot; do
  if [ -f "$d/splash.svg" ]; then ASSETS="$d"; break; fi
done
if [ -z "$ASSETS" ]; then
  say "can't find es-theme-volta/_boot. Copy the theme to your themes folder first."
  exit 1
fi
FONTS="$(dirname "$ASSETS")/_fonts"

# --- ES home (ArkOS runs ES as 'ark') --------------------------------------------------
ES_HOME="$HOME/.emulationstation"
if [ "$(id -u)" = "0" ] && [ -d /home/ark/.emulationstation ]; then
  ES_HOME=/home/ark/.emulationstation
fi
RES="$ES_HOME/resources"
BACKUP="$ES_HOME/volta-backup"

SUDO=""
if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi

# --- boot partition ------------------------------------------------------------------
find_bootlogo() {
  for f in ${VOLTA_BOOTLOGO:-} /boot/logo.bmp /flash/logo.bmp /boot/firmware/logo.bmp; do
    [ -f "$f" ] && { echo "$f"; return; }
  done
}

bmp_info() { # prints "width height bpp" for a BMP, empty if not a BMP
  local f="$1"
  [ "$(head -c 2 "$f" 2>/dev/null)" = "BM" ] || return
  local w h b
  w=$(od -An -t d4 -j 18 -N 4 "$f" | tr -d ' ')
  h=$(od -An -t d4 -j 22 -N 4 "$f" | tr -d ' ')
  b=$(od -An -t u2 -j 28 -N 2 "$f" | tr -d ' ')
  [ "${h#-}" != "$h" ] && h="${h#-}"
  echo "$w $h $b"
}

# --- uninstall ---------------------------------------------------------------------------
if [ "$UNINSTALL" = 1 ]; then
  for n in splash.svg opensans_hebrew_condensed_regular.ttf; do
    if [ -f "$BACKUP/$n" ]; then cp -f "$BACKUP/$n" "$RES/$n"; say "restored $n"
    else rm -f "$RES/$n"; say "removed $n"; fi
    rm -f "$BACKUP/$n" "$BACKUP/$n.none"
  done
  LOGO="$(find_bootlogo)"
  if [ -n "$LOGO" ] && [ -f "$BACKUP/logo.bmp" ]; then
    $SUDO cp -f "$BACKUP/logo.bmp" "$LOGO" && sync && rm -f "$BACKUP/logo.bmp" && say "restored boot logo $LOGO"
  fi
  say "done. Restart EmulationStation (or reboot) to see the original screens."
  exit 0
fi

# --- install loading screen + font ---------------------------------------------------
mkdir -p "$RES" "$BACKUP"
# back up only the user's original files, once (".none" = there was nothing to back up)
for n in splash.svg opensans_hebrew_condensed_regular.ttf; do
  [ -f "$BACKUP/$n" ] || [ -f "$BACKUP/$n.none" ] && continue
  if [ -f "$RES/$n" ]; then cp -f "$RES/$n" "$BACKUP/$n"; else touch "$BACKUP/$n.none"; fi
done
cp -f "$ASSETS/splash.svg" "$RES/splash.svg" && say "loading screen installed ($RES/splash.svg)"
if [ -f "$FONTS/Urbanist-Medium.ttf" ]; then
  cp -f "$FONTS/Urbanist-Medium.ttf" "$RES/opensans_hebrew_condensed_regular.ttf" && say "default font set to Urbanist"
fi
[ "$(id -u)" = "0" ] && [ -d /home/ark ] && chown -R ark:ark "$RES" "$BACKUP" 2>/dev/null

# --- boot logo ------------------------------------------------------------------------------
if [ "$BOOTLOGO" = 1 ]; then
  LOGO="$(find_bootlogo)"
  if [ -z "$LOGO" ]; then
    say "no logo.bmp found on the boot partition; skipping the boot logo."
    say "(you can copy _boot/logo-640x480-24.bmp to the BOOT partition as logo.bmp from a PC)"
  else
    read -r W Hh B <<<"$(bmp_info "$LOGO")"
    if [ -z "${W:-}" ]; then
      say "$LOGO is not a plain BMP (maybe compressed); leaving it alone."
    else
      TAG=""
      if [ "$W" = 640 ] && [ "$Hh" = 480 ]; then TAG="640x480"
      elif [ "$W" = 480 ] && [ "$Hh" = 640 ]; then TAG="480x640-${ROTATE:-cw}"
      fi
      if [ -z "$TAG" ] || { [ "$B" != 24 ] && [ "$B" != 8 ]; }; then
        say "existing boot logo is ${W}x${Hh} ${B}-bit; no matching Volta variant, skipping."
      else
        SRC="$ASSETS/logo-$TAG-$B.bmp"
        if [ ! -f "$BACKUP/logo.bmp" ] && ! cmp -s "$LOGO" "$SRC"; then
          $SUDO cp -f "$LOGO" "$BACKUP/logo.bmp"
        fi
        if $SUDO cp -f "$SRC" "$LOGO"; then
          sync
          say "boot logo installed ($TAG, ${B}-bit) -> $LOGO"
          [ "$TAG" != 640x480 ] && say "if it shows sideways, run again with --portrait-ccw (or --portrait-cw)"
        else
          say "could not write $LOGO (read-only boot partition?)"
        fi
      fi
    fi
  fi
fi

say "done. Select Volta in Start > UI Settings > Theme, then restart EmulationStation."
