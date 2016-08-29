import time
from ledcontrol import LEDControl
import threading
import Adafruit_CharLCD as LCD
import RPi.GPIO as GPIO
import display

MENU_DELAY_TIME = 0.1
BLINK_INTERVAL = 0.7
MAX_NUM_OPTIONS_THAT_FIT = 5

class Menu:

    # deal with it
    NUMBERS = '123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __init__(self, options, display, 
                 title="", initial_selection=0, led_control=None,
                 icons=None, blinking_leds=[]):
        """ 
        Class for representing a menu on the display.
        Takes in a list of options in the format
        ["Option1", "Option2", ...] as well as a
        instance of a Adafruit_CharLCDPlate (display). 
        
        You can set the title of the menu in the optional
        title parameter, and which menu option should be 
        initially selected. If you supply a list of characters
        to the argument icons that is as long as the options list,
        each option will have those icons in the same order.
        
        You can also supply a led_control instance, and a list 
        of LED:s that should blink together with the cursor.
        """
        if not options:
            raise ValueError("No options were given!")
        elif not isinstance(options, list):
            raise ValueError("Incompatible options type - must be list!")

        if icons is None:
            self._icons = self.NUMBERS
        else:
            if len(icons) != len(options):
                raise ValueError("Icons must have the same length as options!")
            else:
                self._icons = icons

        self._led_control = led_control

        # List of options [OPT1, OPT2, ...]
        self.options = options

        # Title of menu
        self.title = title

        # The LCD-display
        self.display = display

        # Number of options
        if len(options) > self._icons:
            raise ValueError("List of options can't be longer than " 
                             + str(len(options)))
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

        # The number of options that don't fit on the display
        self.scroll_amount = max(0, self.options_count - MAX_NUM_OPTIONS_THAT_FIT)
        # The current scroll offset
        self.scroll_offset = 0

        # Lock for synchronizing changes of the selection
        self._selection_lock = threading.Lock()

        # list of LEDs that should blink as the cursor does
        self._blinking_leds = blinking_leds

    def display_menu(self):

        self.display.clear()

        options_row = self._get_options_row()

        # Display menu title, if there is any
        if self.title:
            self.display.change_row(self.title, display.TOP_ROW)
            self.display.change_row(options_row, display.BOTTOM_ROW)
            self._led_control.set(True, LEDControl.BACK)
            self._led_control.set(True, LEDControl.LEFT)
            self._led_control.set(True, LEDControl.RIGHT)
            time.sleep(0.5)
            self._led_control.set(False, LEDControl.BACK)
            self._led_control.set(False, LEDControl.LEFT)
            self._led_control.set(False, LEDControl.RIGHT)

        self._display_option()
        self._blink_thread.start()

    def stop(self):
        self._blink_stop_flag.set()

    def move_selection_left(self):
        self._move_selection('l')

    def move_selection_right(self):
        self._move_selection('r')

    def get_selected_index(self):
        return self._selected

    def _move_selection(self, direction):
        self._selection_lock.acquire()
        if direction == 'l':
            self._selected -= 1
        else:
            self._selected += 1

        if self._selected == -1:
            self._selected = self.options_count - 1
        elif self._selected == self.options_count:
            self._selected = 0

        self.scroll_offset = max(MAX_NUM_OPTIONS_THAT_FIT, 
                                 self._selected + 1) - \
                                 MAX_NUM_OPTIONS_THAT_FIT
        
        self._display_option()
        self.display.change_row(self._get_options_row(), display.BOTTOM_ROW)
        self._selection_lock.release()

    def _get_options_row(self):
        options_row = ""
        for i in range(min(self.options_count, MAX_NUM_OPTIONS_THAT_FIT)):
            number = self._icons[i + self.scroll_offset]
            if i + self.scroll_offset == self._selected:
                options_row += "[{}]".format(number)
            else:
                options_row += " {} ".format(number)

        while len(options_row) < display.LCD_COLS - 1:
            options_row += ' '

        if self.scroll_offset != self.scroll_amount:
            options_row += '>'
        else:
            options_row += ' '

        return options_row

    def _display_option(self):
        # Display option
        self.display.change_row(self.options[self._selected], display.TOP_ROW)
        
    def _blink(self):
        self._selection_lock.acquire()
        if self._current_blink:
            self.display.write_char(1, self._get_option_position(), ' ')
        else:
            self.display.write_char(1,
                                    self._get_option_position(),
                                    self._icons[self._selected])

        if self._led_control is not None:
            for led in self._blinking_leds:
                self._led_control.set(not self._current_blink, led)

        self._selection_lock.release()
        self._current_blink = not self._current_blink

    def _get_option_position(self):
        return (self._selected - self.scroll_offset) * 3 + 1

    def __str__(self):
        return "Menu \"{}\" with options {}".format(self.title, self.options)


class BlinkThread(threading.Thread):

    def __init__(self, display):
        super(BlinkThread, self).__init__()
        self.display = display

    def run(self):
        while not self.display._blink_stop_flag.wait(BLINK_INTERVAL):
            self.display._blink()
        
