#!/bin/bash
# NeonGlow installer for the R36S (ArkOS / dArkOS and their R36S clone builds)
#
#   sudo ./install.sh                     install theme + splash + launch screen + boot logo (red)
#   sudo ./install.sh --accent cyan       pick the accent of the boot / loading screens
#   sudo ./install.sh --set-theme         also switch ES to NeonGlow and restart it
#   sudo ./install.sh --no-boot --no-splash --no-launch   install only the theme
#   sudo ./install.sh --uninstall         remove the theme and restore every backup
#
# Accents: red blue amber green violet pink cyan red-deep blue-deep violet-deep teal-deep

set -u
SRC="$(cd "$(dirname "$0")" && pwd)"
ARGS=("$@")
ACCENT="red"
DO_BOOT=1; DO_SPLASH=1; DO_LAUNCH=1; SET_THEME=0; UNINSTALL=0
BAK=".neonglow-bak"

while [ $# -gt 0 ]; do
  case "$1" in
    --accent) ACCENT="$2"; shift ;;
    --no-boot) DO_BOOT=0 ;;
    --no-splash) DO_SPLASH=0 ;;
    --no-launch) DO_LAUNCH=0 ;;
    --set-theme) SET_THEME=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

say() { echo "[NeonGlow] $*"; }

if [ "$(id -u)" != "0" ]; then
  if command -v sudo >/dev/null 2>&1; then exec sudo "$0" "${ARGS[@]}"; fi
  say "please run as root (sudo)"; exit 1
fi

if [ ! -d "$SRC/extras/boot/$ACCENT" ]; then
  say "unknown accent '$ACCENT'. Available: $(ls "$SRC/extras/boot" | tr '\n' ' ')"; exit 1
fi

# --- locations ---------------------------------------------------------------
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

LAUNCH_DIRS=()
for d in /roms /roms2; do [ -d "$d" ] && LAUNCH_DIRS+=("$d/launchimages"); done

BOOT_DIR=""
for d in /boot /flash /media/boot; do
  if [ -f "$d/logo.bmp" ] || [ -f "$d/uInitrd" ] || [ -f "$d/Image" ]; then BOOT_DIR="$d"; break; fi
done

backup() { [ -f "$1" ] && [ ! -f "$1$BAK" ] && cp -p "$1" "$1$BAK"; }
restore() {
  if [ -f "$1$BAK" ]; then mv -f "$1$BAK" "$1"; say "restored $1"
  elif [ -n "${2:-}" ] && [ -f "$1" ]; then rm -f "$1"; say "removed $1"; fi
}

remount_boot() {
  # the BOOT partition is FAT and sometimes mounted read-only
  if ! touch "$BOOT_DIR/.neonglow-test" 2>/dev/null; then mount -o remount,rw "$BOOT_DIR" 2>/dev/null; fi
  rm -f "$BOOT_DIR/.neonglow-test"
}

# --- uninstall ---------------------------------------------------------------
if [ $UNINSTALL -eq 1 ]; then
  for d in "${THEME_DIRS[@]}"; do [ -d "$d/neonglow" ] && rm -rf "$d/neonglow" && say "removed $d/neonglow"; done
  restore "$ES_DIR/resources/splash.svg" new
  for d in "${LAUNCH_DIRS[@]}"; do restore "$d/loading.jpg" new; done
  if [ -n "$BOOT_DIR" ]; then
    remount_boot
    restore "$BOOT_DIR/logo.bmp"; restore "$BOOT_DIR/logo_kernel.bmp"; sync
  fi
  say "done. Pick another theme in Start > UI Settings > Theme."
  exit 0
fi

# --- theme -------------------------------------------------------------------
for d in "${THEME_DIRS[@]}"; do
  rm -rf "$d/neonglow"
  cp -r "$SRC/neonglow" "$d/neonglow"
  chown -R "$ES_USER": "$d/neonglow" 2>/dev/null
  say "theme installed to $d/neonglow"
done

# --- ES loading screen (overrides the built-in splash) -------------------------
if [ $DO_SPLASH -eq 1 ]; then
  mkdir -p "$ES_DIR/resources"
  backup "$ES_DIR/resources/splash.svg"
  cp "$SRC/extras/es-resources/$ACCENT/splash.svg" "$ES_DIR/resources/splash.svg"
  chown -R "$ES_USER": "$ES_DIR/resources" 2>/dev/null
  say "ES loading screen installed ($ES_DIR/resources/splash.svg)"
fi

# --- game launch screen ------------------------------------------------------
if [ $DO_LAUNCH -eq 1 ]; then
  for d in "${LAUNCH_DIRS[@]}"; do
    mkdir -p "$d"
    backup "$d/loading.jpg"
    cp "$SRC/extras/launchimages/$ACCENT/loading.jpg" "$d/loading.jpg"
    say "game launch screen installed ($d/loading.jpg)"
  done
fi

# --- boot logo ---------------------------------------------------------------
if [ $DO_BOOT -eq 1 ]; then
  if [ -n "$BOOT_DIR" ]; then
    remount_boot
    for f in logo.bmp logo_kernel.bmp; do
      if [ -f "$BOOT_DIR/$f" ] || [ "$f" = "logo.bmp" ]; then
        backup "$BOOT_DIR/$f"
        cp "$SRC/extras/boot/$ACCENT/logo.bmp" "$BOOT_DIR/$f"
        say "boot logo installed ($BOOT_DIR/$f)"
      fi
    done
    sync
  else
    say "BOOT partition not found - skipped the boot logo (copy extras/boot/$ACCENT/logo.bmp to the BOOT partition manually)"
  fi
fi

# --- select the theme --------------------------------------------------------
if [ $SET_THEME -eq 1 ]; then
  CFG="$ES_DIR/es_settings.cfg"
  systemctl stop emulationstation 2>/dev/null
  sleep 1
  if [ -f "$CFG" ]; then
    backup "$CFG"
    if grep -q 'name="ThemeSet"' "$CFG"; then
      sed -i 's|<string name="ThemeSet" value="[^"]*" */>|<string name="ThemeSet" value="neonglow" />|' "$CFG"
    else
      sed -i 's|</config>|<string name="ThemeSet" value="neonglow" />\n</config>|' "$CFG"
    fi
  fi
  systemctl start emulationstation 2>/dev/null
  say "EmulationStation switched to NeonGlow"
fi

say "all done. Theme options: Start > UI Settings > Theme Configuration."
