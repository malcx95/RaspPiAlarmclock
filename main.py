#!/usr/bin/python
import time
import sys
import threading
import RPi.GPIO as GPIO
from menu import Menu
from display import Display

display_lock = threading.Lock()

display = Display(display_lock)

DISPLAY_WIDTH = 16

def button_pressed(channel):
    display.clear()
    display.message("Oh shit you\n pressed pin {}".format(channel))
    GPIO.output(22, True)
    time.sleep(3)
    GPIO.output(22, False)

BUTTON_PIN = 22

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(17, GPIO.OUT)

GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_pressed)

menu = None

try:
    menu = Menu(["Kebab", "Mysarna", "Mamma"], display, title="MAMMA GILLAR GLASS")
    menu.display_menu()
    time.sleep(10)
except KeyboardInterrupt:
    display.clear()
    display.message("Have a nice\nday!")
    GPIO.cleanup()
    menu.stop()
    sys.exit(1)

display.clear()
display.message("Exiting")
sys.exit(0)
