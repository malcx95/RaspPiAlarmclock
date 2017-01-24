cmake_minimum_required (VERSION 3.3)
project (RaspberryPiAlarmClock)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -lwiringPi")

set(CMAKE_INCLUDE_CURRENT_DIR ON)
file(GLOB RaspberryPiAlarmClock_SRC
    "*.cpp"
    "*.hpp"
    "*.c"
    "*.h"
    )

add_executable(rpiclock ${RaspberryPiAlarmClock_SRC})

# target_link_libraries (rpiclock)

