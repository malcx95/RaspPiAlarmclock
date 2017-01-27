#include <wiringPi.h>
#include "display.hpp"

int main(int argc, char *argv[])
{   
    wiringPiSetupGpio();

    Display display;

    return 0;
}
