import time
import threading
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
from constants import *

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
        self.options = options

        # Title of menu
        self.title = title

        # The LCD-display
        self.display = display

        # Number of options
        self.options_count = len(options)

        if initial_selection >= self.options_count or initial_selection < 0:
            raise ValueError("Invalid initial selection \"{}\"!".format( \
                    initial_selection))

        # The current selection (0-based)
        self._selected = initial_selection

        # The current state of a blink
        self._current_blink = False
        # Thread enabling blinking
        self._blink_stop_flag = threading.Event()
        self._blink_thread = BlinkThread(self)

        # TODO maybe we shouldn't care that we can only have five options?
        # The number of options that don't fit on the display
        self.scroll_amount = max(0, self.options_count - MAX_NUM_OPTIONS_THAT_FIT)
        # The current scroll offset
        self.scroll_offset = 0


    def display_menu(self):

        self.display.clear()

        options_row = self._get_options_row()

        # Display menu title, if there is any
        if self.title:
            self.display.change_row(self.title, TOP_ROW)
            self.display.change_row(options_row, BOTTOM_ROW)
            time.sleep(0.5)
        self._display_option()
        self._blink_thread.start()


    def stop(self):
        self._blink_stop_flag.set()


    def move_selection_left(self):
        self._move_selection('l')


    def move_selection_right(self):
        self._move_selection('r')


    def _move_selection(self, direction):
        new_selection = self._selected
        if direction == 'l':
            new_selection -= 1
        else:
            new_selection += 1

        if new_selection == -1:
            new_selection = self.options_count - 1
        elif new_selection == self.options_count:
            new_selection = 0
        
        self._selected = new_selection
        self._display_option()
        self.display.change_row(self._get_options_row(), BOTTOM_ROW)


    def _get_options_row(self):
        options_row = ""
        for i in range(min(self.options_count, 5)):
            if i == self._selected:
                options_row += "[{}]".format(i + 1 + self.scroll_offset)
            else:
                options_row += " {} ".format(i + 1 + self.scroll_offset)

        while len(options_row) < LCD_COLS - 1:
            options_row += ' '

        if self.scroll_offset != self.scroll_amount:
            options_row += '>'
        else:
            options_row += ' '

        return options_row

    
    def _display_option(self):
        # Display option
        self.display.change_row(self.options[self._selected], TOP_ROW)
        
        
    def _blink(self):
        if self._current_blink:
            self.display.write_char(1, self._get_option_position(), ' ')
        else:
            self.display.write_char(1, \
                    self._get_option_position(), self._selected + 1)

        self._current_blink = not self._current_blink

        
    def _get_option_position(self):
        return self._selected * 3 + 1


    def __str__(self):
        return "Menu \"{}\" with options {}".format(self.title, self.options)


class BlinkThread(threading.Thread):


    def __init__(self, display):
        super(BlinkThread, self).__init__()
        self.display = display
        

    def run(self):
        while not self.display._blink_stop_flag.wait(BLINK_INTERVAL):
            self.display._blink()
            # TODO remove
            GPIO.output(GREEN_LED, self.display._current_blink)
            GPIO.output(YELLOW_LED, not self.display._current_blink)
            GPIO.output(RED_LED, self.display._current_blink)
        