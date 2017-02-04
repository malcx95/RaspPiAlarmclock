#!/bin/bash

scp -r ./* pi@rpi:/home/pi/RaspPiAlarmclock/src

if [ $? -ne 0 ]; then
    echo "Upload failed"
    exit 1
fi
