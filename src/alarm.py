import threading
import buttons
import time
import display
import RPi.GPIO as GPIO
from ledcontrol import LEDControl
from datetime import datetime
from calendar import monthrange


TIME_FORMAT = "%Y%m%d%H%M"


def alarm_list_compare(x1, x2):
    if x1[1] and not x2[1]:
        return 1
    elif not x1[1] and x2[1]:
        return -1
    else:
        return cmp(x1, x2)


class Alarm(object):
    """
    Represents an alarm. Contains information about exactly when the
    alarm shall be sound as well as information for the user.
    """

    NO_REPEAT = 0
    EVERY_DAY = 1
    EVERY_WEEK = 2
    REPEAT_OPTIONS = ('None', 'Daily', 'Weekly')

    def __init__(self, hour, minute, day, month, year, repeat):
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.year = year
        self.repeat = repeat
        self.weekday = datetime(year, month, day).weekday()

    def get_alarm_string(self):
        return '{y}{m}{d}{h}{M}'.format(y=self.year,
                                        m=self.month, 
                                        d=self.day,
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
        
    def increment_day(self, amount):
        """
        Increments the weekday by amount and returns the new weekday.
        This changes the actual date on which the alarm will sound.
        Amount must be -1 or 1.
        """
        num_days = monthrange(self.year, self.month)
        if amount + self.day > num_days:
            if self.month + 1 > 12:
                self.year += 1
                self.month = 1
            else:
                self.month += 1
        elif amount + self.day < 1:
            if self.month - 1 < 1:
                self.year -= 1
                self.month = 1
            else:
                self.month -= 1
        else:
            self.day += amount
        self.weekday = datetime(self.year, self.month, self.day).weekday()
        return self.weekday
            
    def __str__(self):
        return '{}:{}'.format(self.hour, 
                              self.minute if self.minute >= 10 else 
                              '0' + str(self.minute))

    def __cmp__(self, other):
        return cmp(self.get_alarm_string(), other.get_alarm_string())


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


