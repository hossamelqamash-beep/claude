#!/bin/bash
# Undo the changes made by the FIRST NeonGlow release (v1.0): restores the original boot logo,
# game-launch screen and EmulationStation loading screen that v1.0 saved as *.neonglow-bak.
# Usage (SSH):  sudo /roms/themes/neonglow/_scripts/restore-v1.0-files.sh
set -u
BAK=".neonglow-bak"
say() { echo "[NeonGlow] $*"; }
if [ "$(id -u)" != "0" ]; then exec sudo "$0" "$@"; fi
ES_HOME="$(getent passwd ark | cut -d: -f6)"
[ -z "$ES_HOME" ] && ES_HOME="$HOME"
ES_DIR="$ES_HOME/.emulationstation"

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

restore_originals
exit 0
