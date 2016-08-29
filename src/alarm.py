import threading
import buttons
import time
import display
import os
import json
import RPi.GPIO as GPIO
from ledcontrol import LEDControl
from datetime import datetime
from calendar import monthrange
from main import SAVE_DIR


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

    def increment_repeat(self, amount):
        """
        Increments the repeat option by amount (-1 or 1).
        """
        new_repeat = self.repeat
        new_repeat = (new_repeat + amount) % 3
        self.repeat = repeat
        return repeat

    def increment_hour(self, amount):
        """
        Increments the hour by amount and returns the new hour.
        Amount must be -1 or 1.
        """
        new_hour = self.hour
        new_hour = (new_hour + amount) % 24
        self.hour = new_hour
        return new_hour

    def incremement_minute(self, amount):
        """
        Increments the minute by amount and returns the new minute.
        Amount must be -1 or 1.
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
            
    def __str__(self):
        return '{}:{}'.format(self.hour, 
                              self.minute if self.minute >= 10 else 
                              '0' + str(self.minute))
    
    def get_json_representation(self):
        return [self.hour, self.minute, self.weekday, self.repeat]


def _alarm_list_compare(x1, x2):
    if x1[1] and not x2[1]:
        return 1
    elif not x1[1] and x2[1]:
        return -1
    else:
        return cmp(str(x1[0]), str(x2[0]))


class AlarmList(object):
    """An intelligent iterable list of alarms"""

    SAVE_FILE = os.path.join(SAVE_DIR, 'alarms.json')

    def __init__(self):
        self._alarms = self.load_alarms()

    def __iter__(self):
        return iter(self._alarms)

    def load_alarms(self):
        alarms = []
        if os.path.isfile(self.SAVE_FILE):
            with open(self.SAVE_FILE) as file_:
                alarms_string = file_.read()
            alarm_array = json.loads(alarms_string)
            for alarm, activated in alarm_array:
                alarms.append((Alarm(*alarm), activated))
            alarms.sort(_alarm_list_compare)
            return alarms
        else:
            return []

    def add_alarm(self, alarm, activated):
        self._alarms.append((alarm, activated))
        self._alarms.sort(_alarm_list_compare)
        self._save()

    def is_empty(self):
        return not self._alarms

    def _save(self):
        with open(self.SAVE_FILE, 'w') as file_:
            file_.write(json.dumps(
                [[al.get_json_representation(), act] 
                 for al, act in self._alarms]))

    def delete_alarm(self, alarm):
        for i in range(len(self._alarms)):
            if self._alarms[i] == alarm:
                self._alarms.pop(i)
        raise KeyError('Alarm {} is not in the list'.format(alarm))


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


