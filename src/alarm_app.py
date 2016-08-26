import menu_node
from alarm import Alarm

DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

class AlarmApplication(MenuNode):

    def __init__(self, display, lock, led_control):
        self._children = []
        super(self.__class__, self).__init__(display, 'Alarms', self._children, lock)
        self._led_control = led_control

    # TODO implement
    

class AlarmEditor(MenuNode):

    def __init__(self, display, lock, led_control, alarm=None):
        super(self.__class__, self).__init__(display, str(alarm),
                                             self._children, lock)
        self._led_control = led_control
        if alarm is None:
            self.alarm = alarm
        else:
            self.alarm = None

    def _increment_hour(self, amount):
        new_hour = self.alarm.hour
        new_hour = (new_hour + amount) % 24
        self.alarm.hour = new_hour
        return new_hour

    def _incremement_minute(self, amount):
        new_min = self.alarm.minute
        new_min = (new_min + amount) % 60
        self.alarm.minute = new_min
        return new_min
        

