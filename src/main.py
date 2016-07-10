#!/usr/bin/python
import time
import sys
import threading
import RPi.GPIO as GPIO
from menu import Menu
from display import Display
from constants import *

menu = None

def button_pressed(channel):
    if channel == M1_BUTTON:
        menu.move_selection_right()
    elif channel == M2_BUTTON:
        menu.move_selection_left()

def test():
    display_lock = threading.Lock()

    display = Display(display_lock)

    for LED in LEDS.values():
        GPIO.setup(LED, GPIO.OUT)

    for button in BUTTONS.values():
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(button, GPIO.RISING, callback=button_pressed, 
                bouncetime=250, )

    try:
        menu = Menu(["Kebab", "Mysarna", "Mamma", "ha", "majs"],
                display, title="MAMMA GILLAR GLASS")
        menu.display_menu()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        display.clear()
        display.message("Have a nice\nkebab!")
        GPIO.cleanup()
        menu.stop()
        sys.exit(1)

    menu.stop()
    display.clear()
    display.message("Exiting")
    sys.exit(0)


if __name__ == '__main__':
    test()