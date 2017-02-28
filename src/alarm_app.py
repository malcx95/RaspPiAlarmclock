from menu_node import MenuNode
from dialog import QuestionDialog, YES_OPTION
import buttons
import display
import alarm
from datetime import datetime
from menu import Menu
import pdb

class AlarmApplication(MenuNode):
    """The menu option that manages the alarms"""

    # TODO redesign
    def __init__(self, display, led_control, alarm_list, button_control):
        super(self.__class__, self).__init__(display, 'Alarms', button_control)
        self._led_control = led_control
        self._button_control = button_control
        self.alarm_list = alarm_list
        self.menu = None

    def setup(self):
        if self.alarm_list.is_empty():
            self.alarm_list.append(self._get_placeholder_alarm())
        self.children = [AlarmEditor(self.display,
                                     self._led_control,
                                     alarm,
                                     self._button_control)
                        for alarm, _ in self.alarm_list]

        icons = [display.ON if on else display.OFF
                 for _, on in self.alarm_list]
        options = self._get_options()
        self.menu = Menu(options, self.display, 
                    'Alarms', 
                    led_control=self._led_control,
                    icons=icons, 
                    blinking_leds=[self._led_control.ENTER,
                                    self._led_control.SET,
                                    self._led_control.DELETE])
        self.menu.setup()

    def _update(self):
        self.menu.update()
        # TODO redo this
        if self._button_control.is_pressed(buttons.ENTER):
            return MenuNode.ENTER, self.menu.get_selected_index()
        elif self._button_control.is_pressed(buttons.RIGHT):
            self.menu.move_selection_right()
        elif self._button_control.is_pressed(buttons.LEFT):
            self.menu.move_selection_left()
        elif self._button_control.is_pressed(buttons.SET):
            self._set_pressed()
        elif self._button_control.is_pressed(buttons.DELETE):
            self._delete_pressed()
        return MenuNode.NO_NAVIGATION, None

    def _get_options(self):
        return [str(al) + ' - ON' if on else str(al) + ' - OFF'
                        for al, on in self.alarm_list]
    
    def _enter_pressed(self):
        self.menu.stop()
        changed_alarm = self.children[self._selected].show()
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
        self.menu.update(self._get_options())

    def _get_placeholder_alarm(self):
        today = datetime.now()
        alarm = alarm.Alarm(7, 0, today.weekday(), 0)
        alarm.increment_day()
        return (alarm, False)
    
    def stop(self):
        self.menu.stop()
    

class AlarmEditor(MenuNode):

    PAGE0_FORMAT = '{hour}:{minute} {day}'
    SELECTIONS = ('hour', 'min', 'day', 'repeat')
    HOUR_POS = 0
    MINUTE_POS = 3
    DAY_POS = 6
    REPEAT_POS = 8
    BOTTOM_ROW = 'Edit:{}{}, Done:{}'.format(display.UP_ARROW, 
                                             display.DOWN_ARROW,
                                             display.ENTER)

    def __init__(self, display, led_control, alarm, button_control):
        self.display = display
        self.alarm = alarm
        self._button_control = button_control
        self._led_control = led_control
        self._weekday = datetime.now().weekday()
        self._selected_day = self._get_weekday_text()
        self._current_selection = 0
        # Page 0 contains hour, minute and day, page 1 contains repeat
        self._current_page = 0
        self._alarm_changed = False

    # TODO implement these
    def setup(self):
        pass

    def _update(self):
        pass

    def stop(self):
        pass

    # def show(self):
    #     self.display.clear()
    #     # TODO return new alarm, if any
    #     if self._alarm_changed:
    #         self._alarm_changed = False
    #         return self.alarm
    #     else:
    #         return None

    def _listen_to_input(self):
        self._update()
        while not self.stop_flag.wait(0.1):
            if self._button_control.is_pressed(buttons.BACK):
                break
            if self._button_control.is_pressed(buttons.UP):
                pass

    # def _update(self):
    #     top_row = ''
    #     if self._current_page == 0:
    #         top_row = self.PAGE0_FORMAT.format(hour=self.alarm.hour,
    #                                            minute=self.alarm.minute 
    #                                             if self.alarm.minute > 9 else
    #                                             '0' + str(self.alarm.minute),
    #                                            day=self._get_weekday_text())
    #     else:
    #         top_row = 'Repeat: {}'.format(self.alarm.get_repeat_string())
    #     self.display.change_row(top_row, display.TOP_ROW)
    #     self.display.change_row(self.BOTTOM_ROW, display.BOTTOM_ROW)

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
        
