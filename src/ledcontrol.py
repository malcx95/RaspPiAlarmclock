import RPi.GPIO as GPIO
import threading

"""
    Class for controlling the LEDS. Other modules 
    should not instantiate this class, use the LED_CONTROL 
    instance.
"""
class LEDControl:

    GREEN = 'green'
    RED = 'red'
    YELLOW = 'yellow'
    
    LED_PORTS = {
            'green' : 16,
            'yellow' : 20,
            'red' : 21
            }

    VALUES = {
            'green' : False,
            'yellow' : False,
            'red' : False,
    }

    for led in LED_PORTS.values():
        GPIO.setup(led, GPIO.OUT)

    _lock = threading.Lock()

    def set(self, on, led):
        self._lock.aqcuire()
        self.value = on
        GPIO.output(LED_PORTS[led], self.value)
        self._lock.release()

    def toggle(self, led):
        self._lock.aqcuire()
        self.value = not self.value
        GPIO.output(LED_PORTS[led], self.value)
        self._lock.release()

