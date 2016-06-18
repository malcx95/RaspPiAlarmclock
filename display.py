from Adafruit_CharLCD import Adafruit_CharLCDPlate

class Display(Adafruit_CharLCDPlate):
    
    def __init__(self):
        """Initialize display with defaults"""

        # the current state of the display
        self.rows = ["                ","                "]
        super(Display, self).__init__()

    def change_row(self, text, row):
        """Changes the top row of the display without clearing. Only changes
            different characters."""
        if row != 0 or row != 1:
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
                self.write8(ord(text[i]), True)
            if delay:
                time.sleep(MENU_DELAY_TIME)

        # save the new state
        self.rows[row] = new_row

