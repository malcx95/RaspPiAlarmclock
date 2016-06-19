import threading
from Adafruit_CharLCD import Adafruit_CharLCDPlate
from constants import *


class Display(Adafruit_CharLCDPlate):

    
    def __init__(self, lock):
        """Initialize display with defaults"""

        # the current state of the display
        self.rows = ["                ","                "]

        # the display lock
        self.lock = lock

        super(Display, self).__init__()

        self.blink(False)
        self.show_cursor(False)


    def change_row(self, text, row):
        """Changes the top row of the display without clearing. Only changes
            different characters."""

        if row != 0 and row != 1:
            raise ValueError("Row must be either 0 or 1!")

        self.lock.acquire()

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

        self.lock.release()


    def message(self, text):
        self.lock.acquire()
        row = 0
        col = 0
        new_rows = ["",""]
        for char in text:
            if char == '\n' and row == TOP_ROW:
                row = BOTTOM_ROW
            elif col == LCD_COLS and row == TOP_ROW:
                row = BOTTOM_ROW
                new_rows[row] += char
            elif char != '\n':
                new_rows[row] += char

        # fill out with spaces
        for row in range(LCD_ROWS):
            while len(new_rows[row]) < 16:
                new_rows[row] += ' '

        self.change_row(new_rows[TOP_ROW], TOP_ROW)
        self.change_row(new_rows[BOTTOM_ROW], BOTTOM_ROW)
        self.lock.release()

    def write_char(self, row, col, char):
        if isinstance(char, int):
            char = str(char)
        if not isinstance(char, str) and len(char) != 1:
            raise TypeError(\
                    "Invalid character \'{}\', must be int or a single character"\
                    .format(char))
        self.lock.acquire()
        self.set_cursor(col, row)
        self.write8(ord(char), True)
        self.rows[row][col] = char
        self.lock.release()

    def clear(self):
        self.lock.acquire()
        super(Display, self).clear()
        self.rows = ["                ","                "]
        self.lock.release()
        
