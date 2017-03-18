from menu_node import MenuNode
from dialog import QuestionDialog, YES_OPTION
try:
    import buttons
except ImportError:
    import tests.simulator.buttons as buttons
import display
import alarm
from datetime import datetime
from menu import Menu
import pdb

class AlarmApplication(MenuNode):
    """The menu option that manages the alarms"""

    def __init__(self, display, led_control, alarm_list, button_control):
        super(self.__class__, self).__init__(display, 'Alarms', button_control)
        self._led_control = led_control
        self._button_control = button_control
        self.alarm_list = alarm_list
        self.menu = None

    def setup(self):
        # Save the alarm list since we might have just exited an editor.
        self.alarm_list.save()

        if self.alarm_list.is_empty():
            self.alarm_list.add_alarm(*self._get_placeholder_alarm())

        all_alarms = self.alarm_list.get_all_alarms_with_activated()
        self.children = [AlarmEditor(self.display,
                                     self._led_control,
                                     alarm,
                                     self._button_control)
                        for alarm, _ in all_alarms]

        icons = [display.ON if activated else display.OFF
                 for _, activated in all_alarms]
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
                for al, on in self.alarm_list.get_all_alarms_with_activated()]
    
    def _delete_pressed(self):
        self.menu.stop()
        all_alarms = self.alarm_list.get_all_alarms_with_activated()
        alarm, activated = all_alarms[self.menu.get_selected_index()]
        self.alarm_list.delete_alarm(alarm, activated)
        self.setup()

    def _set_pressed(self):
        all_alarms = self.alarm_list.get_all_alarms_with_activated()
        alarm, activated = all_alarms[self.menu.get_selected_index()]
        self.alarm_list.set_alarm_activated(alarm, not activated, activated)
        icon = display.ON if not activated else display.OFF
        self.menu.set_icon_at(icon, self.menu.get_selected_index())
        self.menu.update_options(self._get_options())

    def _get_placeholder_alarm(self):
        today = datetime.now()
        al = alarm.Alarm(7, 0, today.weekday(), 0)
        al.increment_weekday(1)
        return (al, False)
    
    def stop(self):
        self.menu.stop()
    

class AlarmEditor(MenuNode):

    PAGE0_FORMAT = '{hour}:{minute} {day}'
    PAGE1_FORMAT = 'Repeat: {repeat}'

    HOUR_INDEX = 0
    MINUTE_INDEX = 1
    DAY_INDEX = 2
    REPEAT_INDEX = 3

    # (Position on page, page number)
    HOUR_POS = (0, 0)
    MINUTE_POS = (3, 0)
    DAY_POS = (6, 0)
    REPEAT_POS = (8, 1)

    # Don't change this order without changing the index constants
    SELECTIONS = (HOUR_POS, MINUTE_POS, DAY_POS, REPEAT_POS)

    BOTTOM_ROW = 'Edit:{}{}'.format(display.UP_ARROW, display.DOWN_ARROW)

    def __init__(self, display, led_control, alarm, button_control):
        super(self.__class__, self).__init__(display, 'Alarm Editor',
                                             button_control)
        self.alarm = alarm
        self._led_control = led_control
        self._weekday = datetime.now().weekday()
        self._selected_day = self._get_weekday_text()
        self._current_selection = 0

    def setup(self):
        self.display.show_cursor(True)
        self.display.blink(True)
        self._update_display()

    def _update(self):
        changed = False
        if self._button_control.is_pressed(buttons.LEFT):
            self._move_selection(True)
            changed = True
        elif self._button_control.is_pressed(buttons.RIGHT):
            self._move_selection(False)
            changed = True
        elif self._button_control.is_pressed(buttons.UP):
            self._increment_selection(1)
            changed = True
        elif self._button_control.is_pressed(buttons.DOWN):
            self._increment_selection(-1)
            changed = True

        if changed:
            self._update_display()

        return MenuNode.NO_NAVIGATION, None

    def _increment_selection(self, amount):
        if self._current_selection == self.HOUR_INDEX:
            self.alarm.increment_hour(amount)
        elif self._current_selection == self.MINUTE_INDEX:
            self.alarm.incremement_minute(amount)
        elif self._current_selection == self.DAY_INDEX:
            self.alarm.increment_weekday(amount)
        elif self._current_selection == self.REPEAT_INDEX:
            self.alarm.increment_repeat(amount)

    def _update_display(self):
        index, page = self.SELECTIONS[self._current_selection]
        top_row = ""
        bottom_row = ""
        if page == 0:
            top_row = self.PAGE0_FORMAT.format(hour=self.alarm.hour
                                               if self.alarm.hour > 9 else
                                               '0' + str(self.alarm.hour),
                                               # add extra zero if singe digit
                                               minute=self.alarm.minute 
                                               if self.alarm.minute > 9 else
                                               '0' + str(self.alarm.minute),
                                               day=self._get_weekday_text())
        else:
            top_row = self.PAGE1_FORMAT.format(
                repeat=self.alarm.get_repeat_string())

        self.display.change_row(top_row, display.TOP_ROW)
        self.display.change_row(self.BOTTOM_ROW, display.BOTTOM_ROW)
        self.display.set_cursor(index, display.TOP_ROW)

    def _get_current_page(self):
        return self.SELECTIONS[self._current_selection][1]

    def _move_selection(self, move_left):
        """
        Move cursor, if move_left is True, move left, otherwise
        move right
        """
        movement = -1 if move_left else 1
        self._current_selection = (movement + 
                                   self._current_selection) % \
                                    len(self.SELECTIONS)

    def stop(self):
        self.display.show_cursor(False)
        self.display.blink(False)

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
        
