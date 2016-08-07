import threading
import RPi.GPIO as GPIO
from constants import *
from menu import Menu
from datetime import datetime

"""
Generic class for things that can be in menu items.
Every subclass must override the start(self) method.
"""
class MenuNode(object):

    def __init__(self, display, title, lock, children=[]):
        if not isinstance(children, list):
            raise ValueError("Children must be list")
        self._stop_flag = threading.Event()
        self.title = title
        self.children = children
        self.display = display
        self.lock = lock

    """
    Method for "starting" the menu node, that is 
    showing it on the display. Every subclass to MenuNode
    must implement this method, and use the self._stop_flag
    to determine when to quit.

    This method needs to be synchronized with the lock.
    """
    def start(self):
        raise NotImplementedError("Start needs to be overridden!")

    """
    Terminates the MenuNode, so other nodes can
    be shown on the display. In case a subclass uses buttons,
    this method needs to be overridden to remove used buttons.

    Every subclass should override this, to add synchronization for the flag
    using the lock, make sure to encapsulate a call to the base method within 
    a synchronized block.
    """
    def stop(self):
        self._stop_flag.set()
        self._stop_flag = threading.Event()

    """
    Gets the MenuNode with the given path. The path is a list
    of indices representing the which children in the nodes to follow.
    For example, to access the node which is child 1 of a node which is 
    child 0 of the main menu, [0, 1] is sent as path.
    """
    def get_node(self, path):
        if not path:
            return self
        elif len(self.children) >= path[0]:
            return self.children[path[0]].get_node(path[1:])
        else:
            raise IndexError("Node with path {} does not exist".format(path))

    def __str__(self):
        return self.title


class ClockFace(MenuNode):

    def __init__(self, display, lock):
        super(self.__class__, self).__init__(display, "Clock", lock)
    
    def start(self):
        self.lock.acquire()
        self.time = datetime.now().strftime('%H:%M')
        self._stop_flag = threading.Event()
        self.lock.release()

        self.display.clear()
        self.display.change_row(self.time, 0)
        while not self._stop_flag.wait(1):
            self._update_time()

    def _update_time(self):
        old_time = self.time
        self.time = datetime.now().strftime('%H:%M')
        if old_time != self.time:
            self.display.change_row(self.time, 0)

    def stop(self):
        self.lock.acquire()
        super(self,__class__, self).stop()
        self.lock.release()


"""
Just a placeholder node
"""
class PlaceHolderNode(MenuNode):

    def __init__(self, display, lock, title="Example"):
        super(self.__class__, self).__init__(display, title, lock)

    def start(self):
        self.lock.acquire()
        self.lock.release()
        self.display.clear()
        self.display.change_row(self.title, 0)
        self._stop_flag.wait()

    def stop(self):
        self.lock.acquire()
        super(self,__class__, self).stop()
        self.lock.release()


"""
MenuNode representing a regular menu. Start returns the 
selected MenuNode when stopped or on the press of the enter button.
"""
class SelectionMenu(MenuNode):

    def __init__(self, display, title, children, lock):
        if not children:
            raise ValueError("Children can't be empty")
        super(self.__class__, self).__init__(display, title, lock, children)

    def start(self):
        self.lock.acquire()
        menu = Menu([str(child) for child in self.children],
                    self.display, self.title)

        def button_pressed(channel):
            self.lock.aqcuire()
            if channel == M1_BUTTON:
                # move left
                menu.move_selection_left()
            elif channel == M2_BUTTON:
                # move right
                menu.move_selection_right()
            elif channel == M3_BUTTON:
                # enter
                print "Entering..."
                self._enter_pressed()
            self.lock.release()

        # set up buttons
        GPIO.add_event_detect(M1_BUTTON, GPIO.RISING, callback=button_pressed,
                              bouncetime=300)
        GPIO.add_event_detect(M2_BUTTON, GPIO.RISING, callback=button_pressed, 
                              bouncetime=300)
        GPIO.add_event_detect(M3_BUTTON, GPIO.RISING, callback=button_pressed, 
                              bouncetime=300)
        
        menu.display_menu()
        self.lock.release()
        
        self._stop_flag.wait()

        selected = menu.get_selected_index()
        menu.stop()

        self.stop()

        return selected

    def stop(self):
        self.lock.acquire()
        super(self.__class__, self).stop()
        GPIO.remove_event_detect(M1_BUTTON)
        GPIO.remove_event_detect(M2_BUTTON)
        GPIO.remove_event_detect(M3_BUTTON)
        self.lock.release()

    def _enter_pressed(self):
        self.lock.acquire()
        self._stop_flag.set()
        self.lock.release()
    
