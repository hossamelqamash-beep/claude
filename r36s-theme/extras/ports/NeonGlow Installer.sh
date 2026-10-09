#!/bin/bash
# Run the NeonGlow installer from the EmulationStation "Ports" menu.
# Copy this file to /roms/ports/ and the whole r36s-theme folder to /roms/neonglow-install/
printf "\033c" > /dev/tty1
DIR=/roms/neonglow-install
[ -d "$DIR" ] || DIR=/roms2/neonglow-install
sudo "$DIR/install.sh" --set-theme 2>&1 | tee /dev/tty1
sleep 3
