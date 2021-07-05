#!/bin/bash

/bin/bash ~/scripts/dwm/wp-autochange.sh &
/bin/bash ~/scripts/dwm/dwm-status.sh &
/bin/python3 ~/repo/pclip/pclip.py &
amixer set Master 30%
# rclone mount wponedrive:/ /home/warren/onedrive --copy-links --no-gzip-encoding --no-check-certificate --allow-non-empty --vfs-cache-mode minimal --umask 000 &
# picom -o 0.95 -i 0.88 --detect-rounded-corners --vsync --blur-background-fixed -f -D 5 -c -b
# picom -b
# /bin/bash ~/scripts/dwm/tap-to-click.sh &
# /bin/bash ~/scripts/dwm/inverse-scroll.sh &
# /bin/bash ~/scripts/dwm/setxmodmap-colemak.sh &
# nm-applet &
# xfce4-power-manager &
# xfce4-volumed-pulse &
# /bin/bash ~/scripts/dwm/run-mailsync.sh &
# ~/scripts/dwm/autostart_wait.sh &
