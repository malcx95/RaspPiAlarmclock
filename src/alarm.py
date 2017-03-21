import threading
try:
    import buttons
except ImportError:
    import tests.simulator.buttons as buttons
import time
import display
import os
import json
from ledcontrol import LEDControl
from datetime import datetime
from calendar import monthrange


DAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday')


TIME_FORMAT = "%Y%m%d%H%M"

class Alarm(object):
    """
    Represents an alarm. Contains information about exactly when the
    alarm shall be sound as well as information for the user.
    """

    NO_REPEAT = 0
    EVERY_DAY = 1
    EVERY_WEEK = 2
    REPEAT_OPTIONS = ('None', 'Daily', 'Weekly')

    def __init__(self, hour, minute, weekday, repeat):
        """hour: int, minute: int, weekday: int, repeat: int"""
        self.hour = hour
        self.minute = minute
        self.repeat = repeat
        self.weekday = weekday

    def _update_date(self):
        today = datetime.now()
        self._day = today.day
        self._month = today.month
        self._year = today.year
        while datetime(self._year, self._month, self._day).weekday() != \
              self.weekday:
           self._increment_day()

    def get_alarm_string(self):
        self._update_date()
        return '{y}{m}{d}{h}{M}'.format(y=self._year,
                                        m=self._month, 
                                        d=self._day,
                                        h=self.hour,
                                        M=self.minute)

    def get_repeat_string(self):
        return self.REPEAT_OPTIONS[self.repeat]

    def increment_weekday(self, amount):
        """
        Increments the weekday number by amount and returns the new day.
        """
        self.weekday = (self.weekday + amount) % 7
        return self.weekday

    def increment_repeat(self, amount):
        """
        Increments the repeat option by amount and returns the new repeat.
        """
        self.repeat = (self.repeat + amount) % 3
        return self.repeat

    def increment_hour(self, amount):
        """
        Increments the hour by amount and returns the new hour.
        """
        new_hour = self.hour
        new_hour = (new_hour + amount) % 24
        self.hour = new_hour
        return new_hour

    def incremement_minute(self, amount):
        """
        Increments the minute by amount and returns the new minute.
        """
        new_min = self.minute
        new_min = (new_min + amount) % 60
        self.minute = new_min
        return new_min
        
    def _increment_day(self):
        num_days = monthrange(self._year, self._month)
        if self._day + 1 > num_days:
            if self._month + 1 > 12:
                self._year += 1
                self._month = 1
            else:
                self._month += 1
        else:
            self._day += 1

    def __eq__(self, other):
        return self.get_json_representation() == \
                other.get_json_representation() if other is not None else False
            
    def __str__(self):
        return '{}:{} {}'.format(self.hour, 
                              self.minute if self.minute >= 10 else 
                              '0' + str(self.minute),
                                 DAYS[self.weekday][:3])

    def __repr__(self):
        return str(self)
    
    def get_json_representation(self):
        return [self.hour, self.minute, self.weekday, self.repeat]


def _alarm_list_compare(x1, x2):
    return cmp(str(x1), str(x2))


class AlarmList(object):
    """An intelligent iterable list of alarms"""

    def __init__(self, save_file):
        self.save_file = save_file
        active, inactive = self.load_alarms()
        self._inactive_alarms = inactive
        self._active_alarms = active

    def get_all_alarms(self):
        return self._active_alarms + self._inactive_alarms

    def get_all_alarms_with_activated(self):
        """
        Just like get all alarms, but every alarm is paired with it's
        activated status.

        AlarmList -> [(Alarm, bool)]
        """
        return [(al, True) for al in self._active_alarms] + \
                [(al, False) for al in self._inactive_alarms]

    def num_active_alarms(self):
        return len(self._active_alarms)

    def num_inactive_alarms(self):
        return len(self._inactive_alarms)

    def num_alarms(self):
        return self.num_active_alarms() + self.num_inactive_alarms()

    def get_active_alarms(self):
        return self._active_alarms
    
    def get_inactive_alarms(self):
        return self._inactive_alarms

    def load_alarms(self):
        active = []
        inactive = []
        try:
            with open(self.save_file) as file_:
                alarms_string = file_.read()
            alarms = json.loads(alarms_string)
            for alarm in alarms['active']:
                active.append(Alarm(*alarm))
            active.sort(_alarm_list_compare)
            for alarm in alarms['inactive']:
                inactive.append(Alarm(*alarm))
            inactive.sort(_alarm_list_compare)
            return active, inactive
        except Exception:
            return [], []

    def add_alarm(self, alarm, activated):
        if activated:
            self._active_alarms.append(alarm)
            self._active_alarms.sort(_alarm_list_compare)
        else:
            self._inactive_alarms.append(alarm)
            self._inactive_alarms.sort(_alarm_list_compare)
        self.save()

    def is_empty(self):
        return not (self._inactive_alarms or self._active_alarms)

    def save(self):
        active = [al.get_json_representation() for al in self._active_alarms]
        inactive = [al.get_json_representation() for al in self._inactive_alarms]
        with open(self.save_file, 'w') as file_:
            file_.write(json.dumps({'active': active, 'inactive': inactive}))

    def delete_alarm(self, alarm, activated):
        if activated:
            for i in range(len(self._active_alarms)):
                if self._active_alarms[i] == alarm:
                    self._active_alarms.pop(i)
                    self.save()
                    return
        else:
            for i in range(len(self._inactive_alarms)):
                if self._inactive_alarms[i] == alarm:
                    self._inactive_alarms.pop(i)
                    self.save()
                    return
        raise KeyError('Alarm {} is not in the list'.format(alarm))

    def set_alarm_activated(self, alarm, activated, old_value):
        """
        Sets the given alarm in the list to activated. Raises
        KeyError if the given alarm is not contained in the list.
        """
        found_index = None
        alarm_list = []

        # we want to look either in the active or inactive
        # alarms depending on the old value
        if old_value:
            alarm_list = self._active_alarms
        else:
            alarm_list = self._inactive_alarms
        
        for i in range(len(alarm_list)):
            al = alarm_list[i]
            if alarm == al:
                found_index = i
                break

        if found_index is None:
            raise KeyError(
                'Alarm {} with old value {} not found'.format(
                    str(alarm), old_value))

        # move from active to inactive, or the other way around
        if old_value:
            self._active_alarms.pop(found_index)
            self._inactive_alarms.append(alarm)
            self._inactive_alarms.sort(_alarm_list_compare)
        else:
            self._inactive_alarms.pop(found_index)
            self._active_alarms.append(alarm)
            self._active_alarms.sort(_alarm_list_compare)

        self.save()

    def get_gone_off_alarm(self, time):
        """
        If an alarm is supposed to go off now, the alarm that should go off
        is returned, otherwise, None is returned. The given time
        should be generated using datetime.now().strftime(alarm.TIME_FORMAT).

        An alarm goes off if the current time equals the time of an activated
        alarm down to the minute.

        AlarmList -> String -> Alarm | None
        """
        # TODO implement
        pass


class AlarmSupervisorThread(threading.Thread):

    def __init__(self, display, led_control):
        super(self.__class__, self).__init__()
        self._selected_menu = None
        self._added_menu = threading.Event()
        self._added_alarm = None
        self.alarm_gone_off = False
        self.permission_to_start = None
        self.alarm_dismissed = None
        self.lock = threading.Lock()
        self.alarms = []
        self.display = display
        self.led_control = led_control

    def set_selected_menu_node(self, menu):
        self.lock.acquire()
        self._selected_menu = menu
        self._added_menu.set()
        self.lock.release()

    def set_alarm(self, alarm):
        self.lock.acquire()
        self.alarms.append(alarm)
        if len(self.alarms) == 1:
            while self._added_alarm is None:
                pass
            self._added_alarm.set()
        self.lock.release()

    def run(self):
        while True:
            self.lock.acquire()
            self._remove_passed_alarms()
            self._added_alarm = threading.Event()
            self.lock.release()
            if not self.alarms:
                self._added_alarm.wait()
            self._added_menu.wait()
            while True:
                current_time = datetime.now().strftime(TIME_FORMAT)
                self.lock.acquire()
                if current_time in self.alarms:
                    self.alarm_dismissed = threading.Event()
                    self.permission_to_start = threading.Event()
                    self.alarm_gone_off = True
                    self._sound_alarm()
                    self.alarms.remove(current_time)
                    self.lock.release()
                    self._added_menu = threading.Event()
                    self._selected_menu = None
                    self.alarm_dismissed.set()
                    break
                self.lock.release()
                time.sleep(1)
            self.alarm_gone_off = False

    def _remove_passed_alarms(self):
        alarms_to_remove = []
        for alarm in self.alarms:
            if int(alarm) < int(datetime.now().strftime(TIME_FORMAT)):
                alarms_to_remove.append(alarm)
        self.alarms = [a for a in self.alarms if a not in alarms_to_remove]

    def _sound_alarm(self):
        self._selected_menu.stop()
        self.permission_to_start.wait()
        iteration = False
        self.display.clear()
        while not GPIO.wait_for_edge(buttons.ENTER, 
                                     GPIO.RISING, timeout=500):
            if iteration:
                self.display.change_row('WAKE UP!!', display.TOP_ROW)
            else:
                self.display.clear()

            self.led_control.set(iteration, LEDControl.FRONT_RED)
            self.led_control.set(iteration, LEDControl.FRONT_YELLOW)
            self.led_control.set(iteration, LEDControl.FRONT_GREEN)

            iteration = not iteration

        GPIO.remove_event_detect(buttons.ENTER)

        self.display.clear()


