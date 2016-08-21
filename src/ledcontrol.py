import RPi.GPIO as GPIO
import threading

class LEDControl:
    """
        Class for controlling the LEDS. Other modules 
        should not instantiate this class, use the LED_CONTROL 
        instance.
    """

    LEDS = {
        'LED_ENTER': 12,
        'LED_LEFT': 7,
        'LED_RIGHT': 8,
        'LED_BACK': 25,
        'LED_KEY1': 24,
        'LED_KEY2': 23,
        'LED_KEY3': 18,
        'LED_KEY4': 15,
        'LED_FRONT_RED': 16,
        'LED_FRONT_GREEN': 21,
        'LED_FRONT_YELLOW': 20,
    }

    ENTER = 'LED_ENTER'
    LEFT  = 'LED_LEFT'
    RIGHT = 'LED_RIGHT'
    BACK = 'LED_BACK'
    KEY1 = 'LED_KEY1'
    KEY2 = 'LED_KEY2'
    KEY3 = 'LED_KEY3'
    KEY4 = 'LED_KEY4'
    FRONT_RED = 'LED_FRONT_RED'
    FRONT_GREEN = 'LED_FRONT_GREEN'
    FRONT_YELLOW = 'LED_FRONT_YELLOW'

    
    def __init__(self):
        for led in self.LEDS.values():
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
        GPIO.output(self.LEDS[led], on)
        self._lock.release()

    def toggle(self, led):
        self._lock.acquire()
        self._values[led] = not self._values[led]
        GPIO.output(self.LEDS[led], self._values[led])
        self._lock.release()

    def is_on(self, led):
        return self._values[led]

    def clear(self):
        for led in self.LEDS:
            self.set(False, led)

