#!/usr/bin/python
import time
import sys
import threading
import RPi.GPIO as GPIO
from menu import Menu
from display import Display
from constants import *

def button_pressed(channel):
    button = BUTTONS[channel]
    if button == 'right':
        menu.move_selection_right()
    elif button == 'left':
        menu.move_selection_left()


if __name__ == '__main__':

    display_lock = threading.Lock()

    display = Display(display_lock)

    GPIO.setup(17, GPIO.OUT)

    for button in BUTTONS:
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(button, GPIO.RISING, callback=button_pressed, 
                bouncetime=200)

    try:
        menu = Menu(["Kebab", "Mysarna", "Mamma"], display, title="MAMMA GILLAR GLASS")
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
