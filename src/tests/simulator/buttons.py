
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
    Simulator for the button control.
    """

    def __init__(self):
        # Dictionary of buttons mapped to sequences of outputs
        # is_pressed should have when called. Each call of is_pressed
        # pops the output from the list.
        self.sequences = {}

    def update(self):
        pass

    def set_sequence(self, seq, button):
        self.sequences[button] = seq

    def is_pressed(self, button):
        if self.sequences.get(button, None):
            output = self.sequences[button][0]
            self.sequences[button] = self.sequences[button][1:]
        else:
            return False

