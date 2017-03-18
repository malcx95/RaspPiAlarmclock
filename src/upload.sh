#!/bin/bash

echo "Running tests..."

python -m unittest discover

if [ $? -ne 0 ]; then
    echo "Tests failed, not uploading."
    exit 1
fi

rm *.pyc
rm tests/*.pyc
rm tests/simulator/*.pyc

scp -r ./* pi@rpi:/home/pi/RaspPiAlarmclock/src

if [ $? -ne 0 ]; then
    echo "Upload failed"
    exit 1
fi
