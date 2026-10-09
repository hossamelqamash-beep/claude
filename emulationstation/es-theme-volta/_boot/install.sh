#!/bin/bash
# Optional extras for the Volta theme on ArkOS (R36S and other 640x480 RK3326 devices).
#
# The theme itself needs NONE of this. It works by just copying es-theme-volta into
# the themes folder; its loading screen is part of the theme (the "splash" view).
# Nothing is changed unless you pass an option.
#
#   ./install.sh --splash        use the Volta emblem for EmulationStation's built-in
#                                startup / game-launch loading screen
#   ./install.sh --bootlogo      replace the boot logo (logo.bmp on the BOOT partition)
#        [--portrait-cw | --portrait-ccw]   for 480x640 (portrait) logo files
#   ./install.sh --uninstall     undo everything this script (any version) installed
#
# Backups: ~/.emulationstation/volta-backup/ and, for the boot logo, also
# logo.bmp.volta-backup next to logo.bmp on the BOOT partition (readable from a PC).

set -u

SELF_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DO_SPLASH=0
DO_LOGO=0
ROTATE=""
UNINSTALL=0
for a in "$@"; do
  case "$a" in
    --splash) DO_SPLASH=1 ;;
    --bootlogo) DO_LOGO=1 ;;
    --portrait-cw) ROTATE=cw ;;
    --portrait-ccw) ROTATE=ccw ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown option: $a"; exit 1 ;;
  esac
done

say() { echo "[volta] $*"; }

if [ "$UNINSTALL" = 0 ] && [ "$DO_SPLASH" = 0 ] && [ "$DO_LOGO" = 0 ]; then
  sed -n '2,16p' "$0"
  say "nothing to do: pass --splash, --bootlogo or --uninstall."
  exit 0
fi

# --- locate the theme's _boot folder (works from the theme or from ports) ----------
ASSETS=""
for d in "$SELF_DIR" \
         /roms/themes/es-theme-volta/_boot /roms2/themes/es-theme-volta/_boot \
         "$HOME/.emulationstation/themes/es-theme-volta/_boot" \
         /home/ark/.emulationstation/themes/es-theme-volta/_boot \
         /etc/emulationstation/themes/es-theme-volta/_boot; do
  if [ -f "$d/splash.svg" ]; then ASSETS="$d"; break; fi
done
if [ -z "$ASSETS" ] && [ "$UNINSTALL" = 0 ]; then
  say "can't find es-theme-volta/_boot. Copy the theme to your themes folder first."
  exit 1
fi

# --- ES home (ArkOS runs ES as 'ark') --------------------------------------------------
ES_HOME="$HOME/.emulationstation"
if [ "$(id -u)" = "0" ] && [ -d /home/ark/.emulationstation ]; then
  ES_HOME=/home/ark/.emulationstation
fi
RES="$ES_HOME/resources"
BACKUP="$ES_HOME/volta-backup"
SUDO=""
if [ "$(id -u)" != "0" ] && command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi

find_bootlogo() {
  for f in ${VOLTA_BOOTLOGO:-} /boot/logo.bmp /flash/logo.bmp /boot/firmware/logo.bmp; do
    [ -f "$f" ] && { echo "$f"; return; }
  done
}

bmp_info() { # "width height bpp compression" for a BMP, empty if not a BMP
  local f="$1"
  [ "$(head -c 2 "$f" 2>/dev/null)" = "BM" ] || return
  local w h b c
  w=$(od -An -t d4 -j 18 -N 4 "$f" | tr -d ' ')
  h=$(od -An -t d4 -j 22 -N 4 "$f" | tr -d ' ')
  b=$(od -An -t u2 -j 28 -N 2 "$f" | tr -d ' ')
  c=$(od -An -t u4 -j 30 -N 4 "$f" | tr -d ' ')
  echo "$w ${h#-} $b $c"
}

# --- uninstall: also cleans up files from the first release ------------------------
if [ "$UNINSTALL" = 1 ]; then
  for n in splash.svg opensans_hebrew_condensed_regular.ttf; do
    if [ -f "$BACKUP/$n" ]; then
      cp -f "$BACKUP/$n" "$RES/$n" && say "restored $n"
    elif [ -f "$RES/$n" ]; then
      rm -f "$RES/$n" && say "removed $n"
    fi
    rm -f "$BACKUP/$n" "$BACKUP/$n.none"
  done
  LOGO="$(find_bootlogo)"
  if [ -n "$LOGO" ]; then
    ORIG=""
    [ -f "$LOGO.volta-backup" ] && ORIG="$LOGO.volta-backup"
    [ -z "$ORIG" ] && [ -f "$BACKUP/logo.bmp" ] && ORIG="$BACKUP/logo.bmp"
    if [ -n "$ORIG" ]; then
      $SUDO cp -f "$ORIG" "$LOGO" && sync && say "restored boot logo $LOGO"
      $SUDO rm -f "$LOGO.volta-backup"; rm -f "$BACKUP/logo.bmp"
    fi
  fi
  say "done. Restart EmulationStation (or reboot)."
  exit 0
fi

mkdir -p "$BACKUP"

# --- loading screen ------------------------------------------------------------------------
if [ "$DO_SPLASH" = 1 ]; then
  mkdir -p "$RES"
  if [ ! -f "$BACKUP/splash.svg" ] && [ ! -f "$BACKUP/splash.svg.none" ]; then
    if [ -f "$RES/splash.svg" ]; then cp -f "$RES/splash.svg" "$BACKUP/splash.svg"; else touch "$BACKUP/splash.svg.none"; fi
  fi
  cp -f "$ASSETS/splash.svg" "$RES/splash.svg" && say "loading screen installed ($RES/splash.svg)"
fi

# --- boot logo --------------------------------------------------------------------------------
if [ "$DO_LOGO" = 1 ]; then
  LOGO="$(find_bootlogo)"
  if [ -z "$LOGO" ]; then
    say "no logo.bmp found on the boot partition; nothing changed."
  else
    read -r W Hh B C <<<"$(bmp_info "$LOGO")"
    TAG=""
    if [ "${W:-}" = 640 ] && [ "${Hh:-}" = 480 ]; then TAG="640x480"
    elif [ "${W:-}" = 480 ] && [ "${Hh:-}" = 640 ]; then TAG="480x640-${ROTATE:-cw}"
    fi
    if [ -z "$TAG" ] || [ "${C:-1}" != 0 ] || { [ "$B" != 24 ] && [ "$B" != 8 ]; }; then
      say "existing boot logo is not a plain 640x480/480x640 8- or 24-bit BMP; nothing changed."
    else
      SRC="$ASSETS/logo-$TAG-$B.bmp"
      if [ ! -f "$LOGO.volta-backup" ] && ! cmp -s "$LOGO" "$SRC"; then
        $SUDO cp -f "$LOGO" "$LOGO.volta-backup"
        cp -f "$LOGO" "$BACKUP/logo.bmp"
      fi
      if $SUDO cp -f "$SRC" "$LOGO"; then
        sync
        say "boot logo installed ($TAG, ${B}-bit). Original kept as $LOGO.volta-backup"
      else
        say "could not write $LOGO; nothing changed."
      fi
    fi
  fi
fi

[ "$(id -u)" = "0" ] && [ -d /home/ark ] && chown -R ark:ark "$ES_HOME/resources" "$BACKUP" 2>/dev/null
say "done. Restart EmulationStation (or reboot) to see the change."
