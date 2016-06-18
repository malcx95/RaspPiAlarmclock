from Adafruit_CharLCD import Adafruit_CharLCDPlate
from constants import *

class Display(Adafruit_CharLCDPlate):

    
    def __init__(self, blink=False):
        """Initialize display with defaults"""

        # the current state of the display
        self.rows = ["                ","                "]
        self._blink = blink
        super(Display, self).__init__()


    def change_row(self, text, row):
        """Changes the top row of the display without clearing. Only changes
            different characters."""

        self.blink(False)

        if row != 0 and row != 1:
            raise ValueError("Row must be either 0 or 1!")
        
        text_length = len(text)

        # first generate new row
        new_row = ""
        for i in range(LCD_COLS):
            if i > text_length - 1:
                new_row += ' '
            else:
                new_row += text[i]

        for i in range(LCD_COLS):
            self.set_cursor(i, row)
            # only write if it's a new character
            if new_row[i] != self.rows[row][i]:
                self.write8(ord(new_row[i]), True)

        # save the new state
        self.rows[row] = new_row
        self.blink(self._blink)


    def set_blink(self, blink):
        if blink != self._blink:
            self._blink = blink
            self.blink(blink)

