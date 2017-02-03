#include <wiringPi.h>
#include "display.hpp"
#include <iostream>
#include "buttons.hpp"

int main(int argc, char *argv[])
{   
    wiringPiSetup();

    // buttons::buttons_init();

    // Display display;

    // display.set_cursor_enabled(true);
    // display.set_cursor_blink_enabled(true);
    // display.set_cursor_position(0, 4);
    // delay(1000);

    // display.message("hejhej");
    // delay(1000);
    
    pinMode(11, INPUT);
    pullUpDnControl(11, PUD_UP);

    while (1) {
        if (digitalRead(11) == HIGH) {
            std::cout << "hej" << std::endl;
        }
        delay(1000);
    }

    return EXIT_SUCCESS;
}
