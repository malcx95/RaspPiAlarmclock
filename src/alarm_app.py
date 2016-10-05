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

    def __init__(self, display, lock, led_control, alarm_list):
        super(self.__class__, self).__init__(display, 'Alarms', lock)
        self._led_control = led_control
        self.alarm_list = alarm_list
        self._selected = 0
        self.menu = None

    def _show(self):
        self.children = []
        if self.alarm_list.is_empty():
            self.display.message('No alarms.\nPress {} to add.'\
                                 .format(display.ENTER))
            self._stop_flag.wait()
            self.lock.acquire()
            if not self._back_pressed:
                self._add_placeholder_alarm()
                return 0
            self.lock.release()
            return None
        else:
            self._refresh_menu()
            self._stop_flag.wait()
            self.menu.stop()
            return self._selected

    def _get_options(self):
        return [str(al) + ' - ON' if on else str(al) + ' - OFF'
                        for al, on in self.alarm_list]
    
    def _refresh_menu(self):
        # for alarm, _ in self.alarm_list:
        #     editor = AlarmEditor(self.display, self.lock, 
        #                          self._led_control, alarm)
        #     self.children.append(editor)
        self.children = [AlarmEditor(self.display,
                                     self.lock, 
                                     self._led_control,
                                     alarm)
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
        self._set_up_buttons()
        self.menu.display_menu()

    def _set_up_buttons(self):

        def button_pressed(channel):
            self.lock.acquire()
            if channel == buttons.LEFT:
                self.menu.move_selection_left()
            elif channel == buttons.RIGHT:
                self.menu.move_selection_right()
            elif channel == buttons.ENTER:
                self._enter_pressed()
            elif channel == buttons.SET:
                self._set_pressed()
            elif channel == buttons.DELETE:
                self._delete_pressed()
            self._selected = self.menu.get_selected_index()
            self.lock.release()
        
        GPIO.add_event_detect(buttons.ENTER, GPIO.RISING,
                              callback=button_pressed, bouncetime=300)
        GPIO.add_event_detect(buttons.RIGHT, GPIO.RISING,
                              callback=button_pressed, bouncetime=300)
        GPIO.add_event_detect(buttons.LEFT, GPIO.RISING, 
                              callback=button_pressed, bouncetime=300)
        GPIO.add_event_detect(buttons.SET, GPIO.RISING, 
                              callback=button_pressed, bouncetime=300)
        GPIO.add_event_detect(buttons.DELETE, GPIO.RISING, 
                              callback=button_pressed, bouncetime=300)

    def _enter_pressed(self):
        self.stop()

    def _delete_pressed(self):
        self._free_used_buttons()
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

    def _free_used_buttons(self):
        GPIO.remove_event_detect(buttons.ENTER)
        GPIO.remove_event_detect(buttons.RIGHT)
        GPIO.remove_event_detect(buttons.LEFT)
        GPIO.remove_event_detect(buttons.SET)
        GPIO.remove_event_detect(buttons.DELETE)

    def _add_placeholder_alarm(self):
        today = datetime.now()
        alarm = alarm.Alarm(7, 0, today.weekday(), 0)
        alarm.increment_day()
        editor = AlarmEditor(self.display, self.lock, self._led_control, alarm)
        self.children.append(editor)
        self.alarm_list.add_alarm(alarm, False)
    

class AlarmEditor(menu_node.MenuNode):

    PAGE0_FORMAT = '{hour}:{minute} {day}'
    SELECTIONS = ('hour', 'min', 'day', 'repeat')
    HOUR_POS = 0
    MINUTE_POS = 3
    DAY_POS = 6
    REPEAT_POS = 8
    BOTTOM_ROW = 'Edit:{}{}, Done:{}'.format(display.UP_ARROW, 
                                             display.DOWN_ARROW,
                                             display.ENTER)

    def __init__(self, display, lock, led_control, alarm):
        super(self.__class__, self).__init__(display, str(alarm), lock)
        self.alarm = alarm
        self._led_control = led_control
        self._weekday = datetime.now().weekday()
        self._selected_day = self._get_weekday_text()
        self._current_selection = 0
        # Page 0 contains hour, minute and day, page 1 contains repeat
        self._current_page = 0
        # TODO use
        self._accept = False

    def _show(self):
        self.lock.acquire()
        self.display.clear()
        self._update()
        self._set_up_buttons()
        self.lock.release()
        self._stop_flag.wait()
        return None

    def _set_up_buttons(self):
        pass

    def _free_used_buttons(self):
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

    def __repr__(self):
        return "AlarmEditor editing alarm {}".format(str(self.alarm))
        
