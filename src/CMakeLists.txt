cmake_minimum_required (VERSION 3.3)
project (RaspberryPiAlarmClock)

set(CMAKE_CXX_FLAGS "-std=c++11 -Wall")

set(CMAKE_INCLUDE_CURRENT_DIR ON)
file(GLOB RaspberryPiAlarmClock_SRC
    "*.cpp"
    "*.hpp"
    "*.c"
    "*.h"
    )

include_directories("/home/malcolm/raspberrypi/rootfs/usr/local/include")

add_executable(clock ${RaspberryPiAlarmClock_SRC})

target_link_libraries(clock "-L/home/malcolm/raspberrypi/rootfs/usr/local/lib -lwiringPi")

