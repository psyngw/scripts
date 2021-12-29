#!/bin/bash

result=$(ps ax|grep -v grep|grep trayer)
if [ "$result" == "" ]; then
        # eval "trayer --transparent true --expand false --align right --width 20 --SetDockType false --tint 0x88888888 &"
        eval "trayer --edge top --widthtype pixel --height 23 --transparent 33 --tint 10 --expand false --SetDockType false"
else
        eval "killall trayer"
fi
