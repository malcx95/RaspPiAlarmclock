try:
    import RPi.GPIO as GPIO
except ImportError:
    from simulator.gpio import GPIO
import threading
from leds import LEDS

class LEDControl:
    """
        Class for controlling the LEDS. Other modules 
        should not instantiate this class, use the LED_CONTROL 
        instance.
    """

    ENTER = 'LED_ENTER'
    LEFT  = 'LED_LEFT'
    RIGHT = 'LED_RIGHT'
    BACK = 'LED_BACK'
    SET = 'LED_KEY1'
    UP = 'LED_KEY2'
    DOWN = 'LED_KEY3'
    DELETE = 'LED_KEY4'
    FRONT_RED = 'LED_FRONT_RED'
    FRONT_GREEN = 'LED_FRONT_GREEN'
    FRONT_YELLOW = 'LED_FRONT_YELLOW'
    
    def __init__(self):
        for led in LEDS.values():
            GPIO.setup(led, GPIO.OUT)
        self._lock = threading.Lock()
        self._values = {
            'LED_ENTER': False,
            'LED_LEFT': False,
            'LED_RIGHT': False,
            'LED_BACK': False,
            'LED_KEY1': False,
            'LED_KEY2': False,
            'LED_KEY3': False,
            'LED_KEY4': False,
            'LED_FRONT_RED': False,
            'LED_FRONT_GREEN': False,
            'LED_FRONT_YELLOW': False,
        }

    def set(self, on, led):
        self._lock.acquire()
        self._values[led] = on
        GPIO.output(LEDS[led], on)
        self._lock.release()

    def toggle(self, led):
        self._lock.acquire()
        self._values[led] = not self._values[led]
        GPIO.output(LEDS[led], self._values[led])
        self._lock.release()

    def is_on(self, led):
        return self._values[led]

    def clear(self):
        for led in LEDS:
            self.set(False, led)

