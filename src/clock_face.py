from menu_node import MenuNode
from datetime import datetime

class ClockFace(MenuNode):

    def __init__(self, display, lock):
        super(self.__class__, self).__init__(display, "Clock", lock)
        self.time = None
    
    def _show(self):
        self.lock.acquire()
        self.time = datetime.now().strftime('%H:%M')

        self.display.clear()
        self.display.change_row(self.time, 0)
        self.lock.release()
        while not self._stop_flag.wait(1):
            self.lock.acquire()
            self._update_time()
            self.lock.release()
        return None

    def _update_time(self):
        old_time = self.time
        self.time = datetime.now().strftime('%H:%M')
        if old_time != self.time:
            self.display.change_row(self.time, 0)
    
    def _free_used_buttons(self):
        pass
