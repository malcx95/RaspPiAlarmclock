import threading

class GPIOSimulator:

    OUT = 0
    IN = 1
    RISING = 0
    FALLING = 1
    BCM = None
    PUD_DOWN = None

    def __init__(self, window, lock):
        self.window = window
        self.lock = lock

    def setup(self, port, inout, **kwargs):
        pass

    def output(self, port, value):
        pass

    def add_event_detect(self, port, rise_fall, callback=None, bouncetime=400):
        pass

    def remove_event_detect(self, port):
        pass

    def cleanup(self):
        pass

    def setmode(self, mode):
        pass

# TODO initscr()
window_lock = threading.Lock()
GPIO = GPIOSimulator(None, window_lock)

