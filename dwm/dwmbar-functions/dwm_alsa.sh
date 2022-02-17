#!/bin/sh

# A dwm_bar function to show the master volume of ALSA
# Joe Standring <git@joestandring.com>
# GNU GPLv3

# Dependencies: alsa-utils

VOLUME_ICON_MUTE="🔇"
VOLUME_ICON1="🔈"
VOLUME_ICON2="🔉"
VOLUME_ICON3="🔊"
# VOLUME_ICON_MUTE="ﱝ "
# VOLUME_ICON1=""
# VOLUME_ICON2="墳"
# VOLUME_ICON3=""

dwm_alsa () {
    VOL=$(amixer get Master | tail -n1 | sed -r "s/.*\[(.*)%\].*/\1/")
    VOL_STATUS=$(amixer get Master | tail -n1 | sed -r "s/.*\[(.*)\].*/\1/")
    printf "%s" "$SEP1"
    if [ "$IDENTIFIER" = "unicode" ]; then
        if [ "$VOL" -eq 0 ] || [ "$VOL_STATUS" = "off" ]; then
            printf "$VOLUME_ICON_MUTE"
        elif [ "$VOL" -gt 0 ] && [ "$VOL" -le 33 ]; then
            printf "$VOLUME_ICON1 %s%%" "$VOL"
        elif [ "$VOL" -gt 33 ] && [ "$VOL" -le 66 ]; then
            printf "$VOLUME_ICON2 %s%%" "$VOL"
        else
            printf "$VOLUME_ICON3 %s%%" "$VOL"
        fi
    else
        if [ "$VOL" -eq 0 ] || [ "$VOL_STATUS" = "off" ]; then
            printf "MUTE"
        elif [ "$VOL" -gt 0 ] && [ "$VOL" -le 33 ]; then
            printf "VOL %s%%" "$VOL"
        elif [ "$VOL" -gt 33 ] && [ "$VOL" -le 66 ]; then
            printf "VOL %s%%" "$VOL"
        else
            printf "VOL %s%%" "$VOL"
        fi
    fi
    printf "%s\n" "$SEP2"
}

