import threading
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
        self.selection = options.index(initial_selection) \
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
        pass

    def _move_right(self):
        pass

    def stop(self):
        time.sleep(0.1)
        for button, led in self._buttons_leds:
            GPIO.remove_event_detect(button)
            if led is not None:
                self._led_control.set(False, led)
        self._stop_flag.set()

    def _show(self):
        # TODO refresh options
        while not self._stop_flag.wait(1):
            self._lock.acquire()
                # TODO scroll message
            self._lock.release()


class MessageDialog(Dialog):
    
    def __init__(self, message, display, led_control=none):
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
        if option_type == OK_CANCEL:
            options = [OK_OPTION, CANCEL_OPTION]
        elif option_type == YES_NO:
            options = [YES_OPTION, NO_OPTION]
        elif option_type == YES_NO_CANCEL:
            options = [YES_OPTION, NO_OPTION, CANCEL_OPTION]
        else:
            raise ValueError('option_type must be a number from 0 to 2!')
        super(self.__class__, self).__init__(question, options,
                                             display, led_control=ledcontrol)


