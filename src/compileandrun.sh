#!/bin/bash

if [ ! -d "$DIRECTORY" ]; then
    echo "Creating build directory..."
    mkdir build
fi

cd build
echo "Running cmake..."
cmake -D CMAKE_TOOLCHAIN_FILE=$HOME/raspberrypi/pi.cmake ../

echo "Compiling..."
make

echo "Uploading..."
scp clock pi@192.168.1.180:/home/pi/

cd ..
ssh pi@192.168.1.180 sudo ./clock
