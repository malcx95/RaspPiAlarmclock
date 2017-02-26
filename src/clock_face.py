from menu_node import MenuNode
from datetime import datetime

class ClockFace(MenuNode):

    def __init__(self, display, button_control):
        super(self.__class__, self).__init__(display, "Clock", button_control)
        self.time = None
    
    def setup(self):
        self.time = datetime.now().strftime('%H:%M')

        self.display.clear()
        self.display.change_row(self.time, 0)

    def _update(self):
        self._update_time()
        return MenuNode.NO_NAVIGATION, None

    def _update_time(self):
        old_time = self.time
        self.time = datetime.now().strftime('%H:%M')
        if old_time != self.time:
            self.display.change_row(self.time, 0)
    
    def stop(self):
        pass

