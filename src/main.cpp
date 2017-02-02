#include <wiringPi.h>
#include "display.hpp"
#include <iostream>

int main(int argc, char *argv[])
{   
    wiringPiSetup();

    Display display;

    display.message("hejhej");
    delay(1000);

    display.message("kebab\nhej");
    delay(1000);

    display.message("eeeeeeeeeeeeeeeeeeee");
    delay(1000);

    display.message("nope\nnope\nnope\n");
    delay(1000);

    display.set_cursor_enabled(true);
    display.set_cursor_blink_enabled(true);
    display.set_cursor_position(0, 4);
    delay(1000);

    display.message("adfieuwhiuwehdiulwehfilwehfluewhflewsuifhlisef");
    delay(1000);

    return EXIT_SUCCESS;
}
