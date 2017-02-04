#include <wiringPi.h>
#include "buttons.hpp"
#include <iostream>

void buttons::buttons_init() {
    for (Button b : ALL_BUTTONS) {
        std::cout << b << std::endl;
        pinMode((int)b, INPUT);
        pullUpDnControl((int)b, PUD_UP);
    }
}

bool buttons::is_pressed(const Button b) {
    return digitalRead((int)b) != 0;
}

