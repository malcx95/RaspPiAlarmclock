import threading
import buttons
import time
import display
from ledcontrol import LEDControl
from datetime import datetime

TIME_FORMAT = "%H%M"

class AlarmSupervisorThread(threading.Thread):

    def __init__(self, display, led_control):
        super(self.__class__, self).__init__()
        self._selected_menu = None
        self._added_menu = None
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
        while self._added_menu is None:
            pass
        self._added_menu.set()
        self.lock.release()

    def set_alarm(self, alarm):
        self.lock.acquire()
        self.alarms.append(alarm)
        if len(alarms) == 1:
            while self._added_alarm is None:
                pass
            self._added_alarm.set()
        self.lock.release()

    def run(self):
        while True:
            self.lock.acquire()
            self._added_menu = threading.Event()
            self._added_alarm = threading.Event()
            self.lock.release()
            self._added_alarm.wait()
            self._added_menu.wait()
            while True:
                current_time = datetime.now().strftime(TIME_FORMAT)
                self.lock.acquire()
                if current_time in self.alarms:
                    self.alarm_dismissed = threading.Event()
                    self.permission_to_start = threading.Event()
                    self.alarm_gone_off = True
                    sound_alarm()
                    self.alarms.remove(current_time)
                    self.lock.release()
                    self.alarm_dismissed.set()
                    break
                self.lock.release()
                time.sleep(1)
            self.alarm_gone_off = False

    def sound_alarm(self):
        print 'Stopping current menu...'
        self._selected_menu.stop()
        print 'Waiting to sound alarm...'
        self.permission_to_start.wait()
        iteration = False
        self.display.clear()
        print 'Starting alarm...'
        while not GPIO.wait_for_edge(buttons.ENTER_BUTTON, 
                                     GPIO.RISING, timeout=500):
            print 'ALARM GONE OFF'
            if iteration:
                self.display.change_row('WAKE UP!!', display.TOP_ROW)
            else:
                self.display.clear()

            self.led_control.set(iteration, LEDControl.FRONT_RED)
            self.led_control.set(iteration, LEDControl.FRONT_YELLOW)
            self.led_control.set(iteration, LEDControl.FRONT_GREEN)

            iteration = not iteration

        print 'Dismissing alarm...'

        self.display.clear()


