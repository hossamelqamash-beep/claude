#!/bin/bash
# Install the NeonGlow theme from the EmulationStation "Ports" menu.
# Copy this file to /roms/ports/ and the unzipped NeonGlow folder to /roms/neonglow-install/
# It only copies the theme folder; it does not restart ES or touch the boot partition.
DIR=/roms/neonglow-install
[ -d "$DIR" ] || DIR=/roms2/neonglow-install
sudo "$DIR/install.sh" 2>&1 | sudo tee /dev/tty1 >/dev/null
sleep 3
