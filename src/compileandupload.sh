#!/bin/bash

if [ ! -d "build" ]; then
    echo "Creating build directory..."
    mkdir build
fi

cd build
echo "Running CMake..."
cmake -D CMAKE_TOOLCHAIN_FILE=$HOME/raspberrypi/pi.cmake ../

if [ $? -ne 0 ]; then
    echo "CMake failed"
    cd ..
    exit 1
fi

echo "Compiling..."
make

if [ $? -ne 0 ]; then
    echo "Compilation failed"
    cd ..
    exit 1
fi

echo "Uploading..."
scp clock pi@rpi:/home/pi/

cd ..

echo "Done."

