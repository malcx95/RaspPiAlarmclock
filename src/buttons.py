"""
Button constants
"""

import RPi.GPIO as GPIO

BUTTONS = {
    'ENTER': 17,
    'LEFT' : 27,
    'RIGHT': 22,
    'BACK' : 5,
    'KEY1' : 6,
    'KEY2' : 13,
    'KEY3' : 19,
    'KEY4' : 26,
        }

ENTER = BUTTONS['ENTER']
LEFT = BUTTONS['LEFT']
RIGHT = BUTTONS['RIGHT']
BACK = BUTTONS['BACK']
SET = BUTTONS['KEY1']
UP = BUTTONS['KEY2']
DOWN = BUTTONS['KEY3']
DELETE = BUTTONS['KEY4']

def is_pressed(button):
    return GPIO.input(button)

