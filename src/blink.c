#include <wiringPi.h>

int main(void) {
    wiringPiSetup();
    pinMode(16, OUTPUT);

    while (1) {
        digitalWrite(16, HIGH);
        delay(100);
        digitalWrite(16, LOW);
        delay(500);
    }
    return 0;
}
