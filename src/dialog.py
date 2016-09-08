import threading
import display
import time
import buttons
from ledcontrol import LEDControl
import RPi.GPIO as GPIO

OK_OPTION = 'OK'
YES_OPTION = 'Yes'
NO_OPTION = 'No'
CANCEL_OPTION = 'Cancel'

class Dialog(object):
    """
    Generic dialog class.
    """

    # TODO Currently not usable

    def __init__(self, message, options, display, 
                 led_control=None, initial_selection=None):
        self.options = options
        self.message = message
        self.display = display
        self.selected = options.index(initial_selection) \
                if initial_selection else 0
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._led_control = led_control
        self._buttons_leds = [
            (buttons.ENTER, LEDControl.ENTER),
            (buttons.LEFT, LEDControl.LEFT if len(options) > 1 else None),
            (buttons.RIGHT, LEDControl.RIGHT if len(options) > 1 else None)
        ]

    def show_dialog(self):
        """
        Shows the dialog and returns the selected option.
        """
        def button_pressed(channel):
            self._lock.acquire()
            if channel == buttons.ENTER:
                self.stop()
            elif channel == buttons.LEFT:
                self._move_left()
            else:
                self._move_right()

            self._lock.release()

        for button, led in self._buttons_leds:
            GPIO.add_event_detect(button,
                                  GPIO.RISING,
                                  callback=button_pressed,
                                  bouncetime=300)
            if led is not None:
                self._led_control.set(True, led)

        return self._show()
    
    def _move_left(self):
        self.selected = (self.selected - 1) % len(self.options)
        self._update_options()

    def _move_right(self):
        self.selected = (self.selected + 1) % len(self.options)
        self._update_options()

    def stop(self):
        time.sleep(0.1)
        for button, led in self._buttons_leds:
            GPIO.remove_event_detect(button)
            if led is not None:
                self._led_control.set(False, led)
        self._stop_flag.set()

    def _show(self):
        self._update_options()
        message_split = self.message.split(' ')
        scroll_offset = 0
        self.display.change_row(self.message, display.TOP_ROW)
        while not self._stop_flag.wait(1):
            self._lock.acquire()
            message_row = ''
            last_index_to_fit = len(message_split) - 1
            for i in range(len(message_split)):
                index = i + scroll_offset
                # TODO review
                if index == len(message_split):
                    last_index_to_fit = len(message_split) - 1
                    break
                elif len(message_row) + len(message_split[index]) + 1 <= \
                        display.LCD_COLS:
                    message_row += message_split[index] + ' '
                elif len(message_row) + len(message_split[index]) <= \
                        display.LCD_COLS:
                    message_row += message_split[index]
                    last_index_to_fit = index
                    break
                else:
                    last_index_to_fit = index
                    break
            if last_index_to_fit == len(message_split) - 1:
                scroll_offset = 0
            else:
                scroll_offset  += 1
            self.display.change_row(message_row, display.TOP_ROW)
            self._lock.release()
        return self.options[self.selected]

    def _update_options(self):
        top_row = ""
        for i in range(len(self.options)):
            option = self.options[i]
            top_row += '[{}]'.format(option) \
                if self.selected == i else ' ' + option + ' '
            top_row += ' '
        self.display.change_row(top_row[:-1], display.BOTTOM_ROW)


class MessageDialog(Dialog):
    
    def __init__(self, message, display, led_control=None):
        super(self.__class__, self).__init__(
            message, [OK_OPTION], display, led_control)


class QuestionDialog(Dialog):
    """
    Yes/No/Cancel type dialog
    """
    OK_CANCEL = 0
    YES_NO = 1
    YES_NO_CANCEL = 2

    def __init__(self, question, option_type, display, led_control=None):
        if option_type == self.OK_CANCEL:
            options = [OK_OPTION, CANCEL_OPTION]
        elif option_type == self.YES_NO:
            options = [YES_OPTION, NO_OPTION]
        elif option_type == self.YES_NO_CANCEL:
            options = [YES_OPTION, NO_OPTION, CANCEL_OPTION]
        else:
            raise ValueError('option_type must be a number from 0 to 2!')
        super(self.__class__, self).__init__(question, options,
                                             display, led_control=led_control)


