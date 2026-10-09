#!/bin/bash
# NeonGlow theme installer for the R36S (ArkOS / dArkOS)
#
#   sudo ./install.sh                     copy the theme to the themes folder (that's all)
#   sudo ./install.sh --restore-originals restore the boot logo / ES loading screen / launch
#                                         screen that the FIRST NeonGlow release replaced
#   sudo ./install.sh --uninstall         remove the theme (and restore those originals)
#
# This installer never touches the boot partition, never edits es_settings.cfg and never
# stops or restarts EmulationStation. After installing, pick the theme in
# Start > UI Settings > Theme.

set -u
SRC="$(cd "$(dirname "$0")" && pwd)"
ARGS=("$@")
MODE="install"
BAK=".neonglow-bak"

for a in "$@"; do
  case "$a" in
    --restore-originals) MODE="restore" ;;
    --uninstall) MODE="uninstall" ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown option: $a"; exit 1 ;;
  esac
done

say() { echo "[NeonGlow] $*"; }

if [ "$(id -u)" != "0" ]; then
  if command -v sudo >/dev/null 2>&1; then exec sudo "$0" "${ARGS[@]}"; fi
  say "please run as root (sudo)"; exit 1
fi

ES_USER="ark"
id "$ES_USER" >/dev/null 2>&1 || ES_USER="$(stat -c %U "$SRC" 2>/dev/null || echo root)"
ES_HOME="$(getent passwd "$ES_USER" | cut -d: -f6)"
[ -z "$ES_HOME" ] && ES_HOME="$HOME"
ES_DIR="$ES_HOME/.emulationstation"

THEME_DIRS=()
for d in /roms/themes /roms2/themes; do [ -d "$d" ] && THEME_DIRS+=("$d"); done
if [ ${#THEME_DIRS[@]} -eq 0 ]; then
  if [ -d /etc/emulationstation/themes ]; then THEME_DIRS+=(/etc/emulationstation/themes)
  else mkdir -p "$ES_DIR/themes"; THEME_DIRS+=("$ES_DIR/themes"); fi
fi

# Put back every file the first release replaced (it saved them as *.neonglow-bak).
restore_originals() {
  local found=0 f
  # ES loading screen: the original release added this file; remove it (or restore a backup)
  f="$ES_DIR/resources/splash.svg"
  if [ -f "$f$BAK" ]; then mv -f "$f$BAK" "$f"; say "restored $f"; found=1
  elif [ -f "$f" ] && grep -q "NEONGLOW\|fill=\"url(#b)\"" "$f" 2>/dev/null; then rm -f "$f"; say "removed $f"; found=1; fi
  for f in /roms/launchimages/loading.jpg /roms2/launchimages/loading.jpg; do
    if [ -f "$f$BAK" ]; then mv -f "$f$BAK" "$f"; say "restored $f"; found=1; fi
  done
  for d in /boot /flash /media/boot; do
    for f in "$d/logo.bmp" "$d/logo_kernel.bmp"; do
      if [ -f "$f$BAK" ]; then
        touch "$d/.ng" 2>/dev/null || mount -o remount,rw "$d" 2>/dev/null
        rm -f "$d/.ng"
        mv -f "$f$BAK" "$f" && say "restored $f"; found=1
      fi
    done
  done
  sync
  if [ $found -eq 0 ]; then say "nothing to restore (no NeonGlow backups found)"; fi
  return 0
}

case "$MODE" in
  restore)
    restore_originals ;;
  uninstall)
    for d in "${THEME_DIRS[@]}"; do [ -d "$d/neonglow" ] && rm -rf "$d/neonglow" && say "removed $d/neonglow"; done
    restore_originals
    say "done. Pick another theme in Start > UI Settings > Theme." ;;
  install)
    for d in "${THEME_DIRS[@]}"; do
      rm -rf "$d/neonglow"
      cp -r "$SRC/neonglow" "$d/neonglow"
      chown -R "$ES_USER": "$d/neonglow" 2>/dev/null
      say "theme installed to $d/neonglow"
    done
    sync
    say "done. Select it in Start > UI Settings > Theme > NEONGLOW." ;;
esac
exit 0
