import menu_node
import threading
import display
from datetime import datetime
from alarm import Alarm

DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday')

class AlarmApplication(MenuNode):

    def __init__(self, display, lock, led_control):
        self._children = []
        super(self.__class__, self).__init__(display, 'Alarms', self._children, lock)
        self._led_control = led_control

    # TODO implement
    

class AlarmEditor(MenuNode):

    top_row_format = '{hour}:{min} {day}'

    def __init__(self, display, lock, led_control, alarm=None):
        super(self.__class__, self).__init__(display, str(alarm),
                                             self._children, lock)
        self._led_control = led_control
        if alarm is None:
            self.alarm = alarm
        else:
            today = datetime.now()
            self.alarm = Alarm(7, 0, today.day, today.month, today.year, False)
        self._weekday = datetime.now().weekday()

    def _show(self):
        pass

    def _update(self):
        # TODO you are here, use the top_row_format
        self.display.change_row(display.TOP_ROW, top_row)

        
class BlinkThread(threading.Thread):
    
    def __init__(self):
        super(self.__class__, self).__init__()
        pass

