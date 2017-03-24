
import RPi.GPIO as GPIO
import time

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

class ButtonControl:
    """
    Interface for controlling the buttons.
    """

    def __init__(self):
        # buttons mapped to (Is currently pressed, was pressed before)
        self.buttons = {}
        for button in BUTTONS.values():
            self.buttons[button] = (False, False)
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def update(self):
        for button in self.buttons:
            old_pressed, _ = self.buttons[button]
            new_before_pressed = old_pressed
            self.buttons[button] = (bool(GPIO.input(button)), new_before_pressed)
    
    def is_pressed(self, button):
        pressed, before_pressed = self.buttons[button]
        return pressed and not before_pressed

    def wait_for_press(self, button, timeout):
        """
        Waits for a button to be pressed. Returns True when the button is pressed
        or False when the given timeout in milliseconds expires.
        """
        while True:
            if GPIO.input(button):
                return True
            if timeout <= 0:
                return False
            timeout -= 1
            time.sleep(0.001)

