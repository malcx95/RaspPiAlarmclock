import threading
try:
    from Adafruit_CharLCD import Adafruit_CharLCDPlate
except ImportError:
    from simulator.display import SimulatorDisplay as Adafruit_CharLCDPlate

LCD_COLS = 16
LCD_ROWS = 2
TOP_ROW = 0
BOTTOM_ROW = 1

LEFT_ARROW = '\x01'
RIGHT_ARROW = '\x02'
ENTER = '\x03'
UP_ARROW = '\x04'
DOWN_ARROW = '\x05'
ON = '\x06'
OFF = '\x07'

class Display(Adafruit_CharLCDPlate):
    
    def __init__(self):
        """Initialize display with defaults"""

        # the current state of the display
        self.rows = ["                ","                "]

        super(Display, self).__init__()

        # create custom characters

        # left arrow
        self.create_char(1, [0,4,2,31,2,4,0,0])

        # right arrow
        self.create_char(2, [0,4,8,31,8,4,0,0])

        # enter
        self.create_char(3, [1,1,1,5,9,31,8,4])

        # up arrow
        self.create_char(4, [4,14,21,4,4,4,4,4])

        # down arrow
        self.create_char(5, [4,4,4,4,4,21,14,4])

        # on icon
        self.create_char(6, [0,14,31,31,31,31,14,0])
        
        # off icon
        self.create_char(7, [0,14,17,17,17,17,14,0])

        super(Display, self).clear()

        self.blink(False)
        self.show_cursor(False)

    def change_row(self, text, row):
        """Changes the top row of the display without clearing. Only changes
            different characters."""

        if row != 0 and row != 1:
            raise ValueError("Row must be either 0 or 1!")

        # only update if necessary
        if self._is_new_text(text, row):
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

    def _is_new_text(self, new_row, row_number):
        for i in range(LCD_COLS):
            if i > len(new_row) - 1:
                if new_row[i] != self.rows[row_number]:
                    return True
            else:
                if self.rows[row_number] != ' ':
                    return True
        return False


    def message(self, text):
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

    def write_char(self, row, col, char):
        if isinstance(char, int):
            char = str(char)
        if not isinstance(char, str) and len(char) != 1:
            raise TypeError(\
                    "Invalid character \'{}\', must be int or a single character"\
                    .format(char))
        self.set_cursor(col, row)
        self.write8(ord(char), True)
        # deal with it
        self.rows[row] = self.rows[row][:col] + char + self.rows[row][col + 1:]

    def clear(self):
        if not self._is_already_clear():
            super(Display, self).clear()
            self.rows = ["                ","                "]

    def _is_already_clear(self):
        return self.rows == ["                ","                "]
        
