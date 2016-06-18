import time
import Adafruit_CharLCD as LCD
from constants import *

# TODO MenuOption is not yet tested

class MenuOption:
    """Single menu item in the menu"""


    def __init__(self, name, selected=False):

        # The whole name of the option
        self.name = name

        # The scroll offset in case the name doesn't fit.
        self.scroll_offset = 0

        # number of characters that don't fit on display
        if LCD_COLS < len(name):
            self.scroll_amount = len(name) - LCD_COLS
        else:
            self.scroll_amount = 0

        # whether this option is selected
        self.selected = selected


    def __str__(self):
        return self.name[self.scroll_offset:16]


class Menu:


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

        # List of options [OPT1, OPT2, ...]
        self.options = []

        # Convert options to MenuOption objects
        for option in options:
            self.options.append(MenuOption(option))

        # Title of menu
        self.title = title

        # The LCD-display
        self.display = display

        # Number of options
        self.options_count = len(options)

        if initial_selection >= self.options_count or initial_selection < 0:
            raise ValueError("Invalid initial selection \"{}\"!".format( \
                    initial_selection))

        # The current selection (0-based
        self.selected = initial_selection
        self.options[self.selected].selected = True


    def display_menu(self):
        self.display.clear()
        self.display.set_blink(True)
        options_row = ""
        for i in range(min(self.options_count, 4)):
            if i == self.selected:
                options_row += "[{}]".format(i + 1)
                self.display.set_cursor(i*3 + 1, 1)
            else:
                options_row += " {} ".format(i + 1)

        # Display menu title, if there is any
        if self.title:
            self.display.change_row(self.title, TOP_ROW)
            self.display.change_row(options_row, BOTTOM_ROW)
            time.sleep(0.5)
        self._display_option()


    def _display_option(self):
        # Display option
        self.display.change_row(str(self.options[self.selected]), 0)
        

    def __str__(self):
        return "Menu \"{}\" with options {}".format(self.title, self.options)

