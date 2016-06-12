#!/usr/bin/python
import time
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
from menu import Menu

display = LCD.Adafruit_CharLCDPlate()

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

try:
    menu = Menu(["Kebab", "Mysarna", "Mamma"], display, title="hAIhai")
    menu.display_menu(delay=False)
except KeyboardInterrupt:
    display.message("Have a nice\nday!")
    GPIO.cleanup()
