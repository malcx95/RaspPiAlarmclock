import menu_node
import threading
import display
from datetime import datetime
from alarm import Alarm

DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday')

class AlarmApplication(menu_node.MenuNode):

    def __init__(self, display, lock, led_control):
        super(self.__class__, self).__init__(display, 'Alarms', lock)
        self._led_control = led_control

    def _show(self):
        if not self.children:
            self.display.message('No alarms. Press {} to add new alarm.'\
                                 .format(display.ENTER))
            self._stop_flag.wait()
            self.lock.acquire()
            if not self._back_pressed:
                self._add_placeholder_alarm()
                return self.children[0]
            return None
        else:
            pass
        # TODO implement

    def _add_placeholder_alarm(self):
        today = datetime.now()
        alarm = Alarm(7, 0, today.day, today.month, today.year, False)
        alarm.increment_day()
        editor = AlarmEditor(self.display, self.lock, self._led_control, alarm)
        self.children.append(editor)
    

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
        self._accept = False

    def _show(self):
        self.lock.acquire()
        self.display.clear()
        self._update()
        self.lock.release()
        self._stop_flag.wait()
        return None

    def _update(self):
        top_row = ''
        if self._current_page == 0:
            top_row = self.PAGE0_FORMAT.format(hour=self.alarm.hour,
                                               minute=self.alarm.minute,
                                               day=self._get_weekday_text())
        else:
            top_row = 'Repeat: {}'.format(self.alarm.get_repeat_string())
        self.display.change_row(display.TOP_ROW, top_row)
        self.display.change_row(display.BOTTOM_ROW, self.BOTTOM_ROW)

    def _get_weekday_text(self):
        today = datetime.now().weekday()
        if self.alarm.weekday == today:
            return 'Today'
        elif self.alarm.weekday == (today + 1) % 7:
            return 'Tomorrow'
        else:
            return DAYS[self.alarm.weekday]

        
class BlinkThread(threading.Thread):
    
    def __init__(self):
        super(self.__class__, self).__init__()
        pass

