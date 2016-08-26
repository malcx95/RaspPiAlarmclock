import threading
import buttons
import time
import display
import RPi.GPIO as GPIO
from ledcontrol import LEDControl
from datetime import datetime
from calendar import monthrange

TIME_FORMAT = "%Y%m%d%H%M"

class Alarm(object):
    """
    Represents an alarm. Contains information about exactly when the
    alarm shall be sound as well as information for the user.
    """

    def __init__(self, hour, minute, day, month, year, repeat):
        self._hour = hour
        self._minute = minute
        self._day = day
        self._month = month
        self._year = year
        self.repeat = repeat
        self._weekday = datetime(year, month, day).weekday()

    def get_alarm_string(self):
        return '{y}{m}{d}{h}{M}'.format(y=self._year,
                                        m=self._month, 
                                        d=self._day,
                                        h=self._hour,
                                        M=self._minute)

    def get_weekday(self):
        return self._weekday

    def increment_hour(self, amount):
        """
        Increments the hour by amount and returns the new hour.
        Amount must be -1 or 1.
        """
        new_hour = self._hour
        new_hour = (new_hour + amount) % 24
        self._hour = new_hour
        return new_hour

    def incremement_minute(self, amount):
        """
        Increments the minute by amount and returns the new minute.
        Amount must be -1 or 1.
        """
        new_min = self._minute
        new_min = (new_min + amount) % 60
        self._minute = new_min
        return new_min
        
    def increment_day(self, amount):
        """
        Increments the weekday by amount and returns the new weekday.
        This changes the actual date on which the alarm will sound.
        Amount must be -1 or 1.
        """
        num_days = monthrange(self._year, self._month)
        if amount + self._day > num_days:
            if self._month + 1 > 12:
                self._year += 1
                self._month = 1
            else:
                self._month += 1
        elif amount + self._day < 1:
            if self._month - 1 < 1:
                self._year -= 1
                self._month = 1
            else:
                self._month -= 1
        else:
            self._day += amount
        self._weekday = datetime(self._year, self._month, self._day).weekday()
        return self._weekday
            
    def __str__(self):
        return '{}:{}'.format(self._hour, 
                              self._minute if self._minute >= 10 else 
                              '0' + str(self._minute))


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


