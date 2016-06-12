import time
import Adafruit_CharLCD as LCD

class Menu:

    LCD_COLS = 16
    LCD_ROWS = 2

    def __init__(self, options, display, title="", initial_selection=0):
        """ Class for representing a menu on the display.
             Takes in a list of options in the format
             ["Option1", "Option2", ...] as well as a
             instance of a Adafruit_CharLCDPlate (display). 
             
             You can set the title of the menu in the optional
             title parameter, and which menu option should be 
             initially selected """
        if not options:
            raise ValueError("No options were given!")
        elif not isinstance(options, list):
            raise ValueError("Incompatible options type - must be list!")
        self.options = options
        self.title = title
        self.display = display
        self.options_count = len(options)
        if initial_selection >= self.options_count or initial_selection < 0:
            raise ValueError("Invalid initial selection \"{}\"!".format( \
                    initial_selection))
        self.selected = initial_selection

    def _change_top_row(self, string, delay=False):
        """ Changes the top row of the display without clearing """
        for i in range(self.LCD_COLS):
            self.display.set_cursor(i, 0)
            self.display.write8(ord(string[i]), True)
            if delay:
                time.sleep(0.1)

    def display_menu(self, delay=False):
        self.display.clear()
        options_row = ""
        for i in range(min(self.options_count, 4)):
            options_row += "[{}] ".format(i)
        # Display menu title
        self.display.message("{}\n{}".format(self.title, options_row))
        time.sleep(1)
        print self.selected
        # Display option
        self._change_top_row(self.options[self.selected], delay=delay)

    def __str__(self):
        return "Menu \"{}\" with options {}".format(self.title, self.options)
