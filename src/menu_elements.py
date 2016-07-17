import threading
from datetime import datetime

class MenuNode(object):


    def __init__(self, display, title, children=[]):
        self.title = title
        self.children = children
        self._stop_flag = threading.Event()
        self.display = display


    def start(self):
        raise NotImplementedError("Start needs to be overridden!")
    

    def stop(self):
        self._stop_flag.set()


class ClockFace(MenuNode):


    def __init__(self, display):
        self.time = datetime.now().strftime('%H:%M:%S')
        super(self.__class__, self).__init__(display, "Clock")
        
    
    def start(self):
        self.display.clear()
        while not self._stop_flag.wait(0.5):
            self._update_time()


    def _update_time(self):
        old_time = self.time
        self.time = datetime.now().strftime('%H:%M:%S')
        if old_time != self.time:
            self.display.change_row(self.time, 0)

