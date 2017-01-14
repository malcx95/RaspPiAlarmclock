import menu_node
from dialog import QuestionDialog, YES_OPTION
import threading
import buttons
import display
import alarm
try:
    import RPi.GPIO as GPIO
except ImportError:
    from simulator.gpio import GPIO
from datetime import datetime
from menu import Menu


class AlarmApplication(menu_node.MenuNode):
    """The menu option that manages the alarms"""

    # TODO I think you need to use the disable back option
    # TODO and handle the back button manually
    def __init__(self, display, lock, led_control, alarm_list):
        super(self.__class__, self).__init__(display, 'Alarms', lock,
                                             disable_back=True)
        self._led_control = led_control
        self.alarm_list = alarm_list
        self._selected = 0
        self.menu = None
        self.alarm_editors = []

    def _show(self):
        self.children = []
        if self.alarm_list.is_empty():
            # TODO remove this branch
            self.display.message('No alarms.\nPress {} to add.'\
                                 .format(display.ENTER))
            self._listen_to_input()
            self.lock.acquire()
            if not self._back_pressed:
                self._add_placeholder_alarm()
                return 0
            self.lock.release()
        else:
            self._refresh_menu()
            self._listen_to_input()
            self.menu.stop()
        self.back_pressed = True
        return None

    def _get_options(self):
        return [str(al) + ' - ON' if on else str(al) + ' - OFF'
                        for al, on in self.alarm_list]
    
    def _listen_to_input(self):
        while not self._stop_flag.wait(0.1):
            if GPIO.input(buttons.ENTER):
                self._enter_pressed()
                if self._back_pressed:
                    self._stop_flag = threading.Event()
                    self._back_pressed = False
            if GPIO.input(buttons.RIGHT):
                self.menu.move_selection_right()
                self._selected = (self._selected + 1) % len(self.alarm_editors)
            if GPIO.input(buttons.LEFT):
                self.menu.move_selection_left()
                self._selected = (self._selected - 1) % len(self.alarm_editors)
            if GPIO.input(buttons.SET):
                self.lock.acquire()
                self._set_pressed()
                self.lock.release()
            if GPIO.input(buttons.DELETE):
                self.lock.acquire()
                self._delete_pressed()
                self.lock.release()
            if GPIO.input(buttons.BACK):
                self.stop()
    
    def _refresh_menu(self):
        self.alarm_editors = [AlarmEditor(self.display,
                                     self.lock, 
                                     self._led_control,
                                     alarm,
                                     self._stop_flag)
                        for alarm, _ in self.alarm_list]

        icons = [display.ON if on else display.OFF
                 for _, on in self.alarm_list]
        options = self._get_options()
        self._selected = 0
        self.menu = Menu(options, self.display, 
                    'Alarms', 
                    led_control=self._led_control,
                    icons=icons, 
                    blinking_leds=[self._led_control.ENTER,
                                    self._led_control.SET,
                                    self._led_control.DELETE])
        self.menu.display_menu()

    def _enter_pressed(self):
        self.menu.stop()
        changed_alarm = self.alarm_editors[self._selected].show()
        if changed_alarm is not None:
            print changed_alarm
        else:
            print "Alarm not changed"
        self._refresh_menu()

    def _delete_pressed(self):
        self.menu.stop()
        alarm, activated = self.alarm_list[self._selected]
        self.alarm_list.delete_alarm(alarm, activated)
        self._refresh_menu()

    def _set_pressed(self):
        alarm, activated = self.alarm_list[self._selected]
        self.alarm_list.set_alarm_activated(alarm, not activated, activated)
        icon = display.ON if not activated else display.OFF
        self.menu.set_icon_at(icon, self._selected)
        self.menu.update_options(self._get_options())

    def _add_placeholder_alarm(self):
        today = datetime.now()
        alarm = alarm.Alarm(7, 0, today.weekday(), 0)
        alarm.increment_day()
        editor = AlarmEditor(self.display, self.lock, self._led_control, alarm)
        self.alarm_editors.append(editor)
        self.alarm_list.add_alarm(alarm, False)
    
    def _free_used_buttons(self):
        pass
    

# TODO redesign so editors aren't menu nodes
class AlarmEditor(object):

    PAGE0_FORMAT = '{hour}:{minute} {day}'
    SELECTIONS = ('hour', 'min', 'day', 'repeat')
    HOUR_POS = 0
    MINUTE_POS = 3
    DAY_POS = 6
    REPEAT_POS = 8
    BOTTOM_ROW = 'Edit:{}{}, Done:{}'.format(display.UP_ARROW, 
                                             display.DOWN_ARROW,
                                             display.ENTER)

    def __init__(self, display, lock, led_control, alarm, stop_flag):
        self.display = display
        self.lock = lock
        self.alarm = alarm
        self.stop_flag = stop_flag
        self._led_control = led_control
        self._weekday = datetime.now().weekday()
        self._selected_day = self._get_weekday_text()
        self._current_selection = 0
        # Page 0 contains hour, minute and day, page 1 contains repeat
        self._current_page = 0
        self._alarm_changed = False

    def show(self):
        self.display.clear()
        self._listen_to_input()
        # TODO return new alarm, if any
        if self._alarm_changed:
            self._alarm_changed = False
            return self.alarm
        else:
            return None

    def _listen_to_input(self):
        self._update()
        while not self.stop_flag.wait(0.1):
            if GPIO.input(buttons.BACK):
                break
            if GPIO.input(buttons.UP):
                pass

    def _update(self):
        top_row = ''
        if self._current_page == 0:
            top_row = self.PAGE0_FORMAT.format(hour=self.alarm.hour,
                                               minute=self.alarm.minute 
                                                if self.alarm.minute > 9 else
                                                '0' + str(self.alarm.minute),
                                               day=self._get_weekday_text())
        else:
            top_row = 'Repeat: {}'.format(self.alarm.get_repeat_string())
        self.display.change_row(top_row, display.TOP_ROW)
        self.display.change_row(self.BOTTOM_ROW, display.BOTTOM_ROW)

    def _get_weekday_text(self):
        today = datetime.now().weekday()
        if self.alarm.weekday == today:
            return 'Today'
        elif self.alarm.weekday == (today + 1) % 7:
            return 'Tomorrow'
        else:
            return alarm.DAYS[self.alarm.weekday]

    def _stop(self):
        self.stop_flag.set()

    def __repr__(self):
        return "AlarmEditor editing alarm {}".format(str(self.alarm))
        
