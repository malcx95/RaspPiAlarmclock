import threading
from datetime import datetime

class MenuNode:


    def __init__(self, display, title="", children=[]):
        self.title = title
        self.children = children


    def start(self):
        raise NotImplementedError("Start needs to be overridden!")


class ClockFace(MenuNode):


    def __init__(self, display):
        super(ClockFace, self).__init__(display)
        self._update_time()
        
    
    def start(self):
        pass


    def _update_time(self):
        self.time = datetime.now().strftime('%H:%M:%S')



