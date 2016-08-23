import threading


class AlarmSupervisorThread(threading.Thread):

    def __init__(self):
        self._selected_menu = None
        self._added_menu = threading.Event()
        self._added_alarm = threading.Event()
        self.lock = threading.Lock()
        self.alarms = []

    def set_selected_menu(self, menu):
        self.lock.acquire()
        self._selected_menu = menu
        self._added_menu.set()
        self.lock.release()

    def set_alarm(self, alarm):
        self.lock.acquire()
        self.alarms.append(alarm)
        if len(alarms) == 1:
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

