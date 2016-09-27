OUT = 0
IN = 1
RISING = 0
FALLING = 1
BCM = None
PUD_DOWN = None

def setup(port, inout, **kwargs):
    pass

def output(port, value):
    pass

def add_event_detect(port, rise_fall, callback=None, bouncetime=400):
    pass

def remove_event_detect(port):
    pass

def cleanup():
    pass

def setmode(mode):
    pass
