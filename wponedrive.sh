#!/bin/bash

result=$(ps ax|grep -v grep|grep 'rclone mount wponedrive')
if [ "$result" == "" ]; then
        eval "rclone mount wponedrive:/ /home/warren/onedrive --copy-links --no-gzip-encoding --no-check-certificate --allow-non-empty --vfs-cache-mode minimal --umask 000 &"
else
        eval "fusermount -qzu /home/warren/onedrive"
fi
