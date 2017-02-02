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

printf "\nCompiling...\n"
make

if [ $? -ne 0 ]; then
    echo "Compilation failed"
    cd ..
    exit 1
fi

cd ..

printf "\nUploading compiled program...\n"
scp build/clock pi@rpi:/home/pi/

if [ $? -ne 0 ]; then
    echo "Upload failed"
    exit 1
fi


printf "\nUploading python scripts...\n"
scp python/* pi@rpi:/home/pi/

if [ $? -ne 0 ]; then
    echo "Upload failed"
    exit 1
else
    echo "Done."
fi


exit 0


