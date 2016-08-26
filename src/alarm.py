import threading
import buttons
import time
import display
import RPi.GPIO as GPIO
from ledcontrol import LEDControl
from datetime import datetime

TIME_FORMAT = "%Y%m%d%H%M"

class Alarm(object):

    def __init__(self, hour, minute, day, month):
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month

    def get_alarm_string(self):
        return '{y}{m}{d}{h}{M}'.format(y=self.year, m=self.month, 
                                        d=self.day, h=self.hour, M=self.minute)
    
    def __str__(self):
        return '{}:{}'.format(self.hour, 
                              self.minute if self.minute >= 10 else 
                              '0' + str(self.minute))


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
        print self.alarms
                

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


