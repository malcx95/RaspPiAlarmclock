import threading
import RPi.GPIO as GPIO
from constants import *
import buttons
from menu import Menu


class MenuNode(object):
    """
    Generic class for things that can be in menu items.
    """

    def __init__(self, display, title, lock, children=[], disable_back=False):
        if not isinstance(children, list):
            raise ValueError("Children must be list")
        self._stop_flag = threading.Event()
        self.title = title
        self.children = children
        self.display = display
        self.lock = lock
        self._back_pressed = False
        self._disable_back = disable_back

    def start(self):
        """
        Shows this MenuNode on the display. The thread invoking 
        this method is not released until another thread invokes 
        the stop() method.

        Returns (bool, MenuNode): whether the back button was pressed,
        the child node selected.
        """

        self._stop_flag = threading.Event()
        self._back_pressed = False
        if not self._disable_back:
            def back(channel):
                self.lock.acquire()
                self._back_pressed = True
                self.stop()
                self.lock.release()

            GPIO.add_event_detect(BACK_BUTTON, GPIO.RISING, 
                                  callback=back, bouncetime=400)

        child_selected = self._show()
        self.lock.acquire()
        back_pressed = self._back_pressed
        self.lock.release()
        return back_pressed, child_selected

    def _show(self):
        """
        Abstract method for showing this menu item on the display.
        Every subclass to MenuNode must implement this method,
        and use the self._stop_flag to determine when to quit.

        This method needs to be synchronized with the lock.

        Returns the selected MenuNode, if any.
        """
        raise NotImplementedError("Start needs to be overridden!")

    def stop(self):
        """
        Terminates the MenuNode, so other nodes can
        be shown on the display. In case a subclass uses buttons,
        this method needs to be overridden to remove used buttons.

        Do not use the lock here.
        """
        if not self._disable_back:
            GPIO.remove_event_detect(buttons.BACK_BUTTON)
        self._stop_flag.set()

    def get_node(self, path):
        """
        Gets the MenuNode with the given path. The path is a list
        of indices representing path the which children in the nodes to follow.
        For example, to access the node which is child 1 of a node which is 
        child 0 of the main menu, [0, 1] is sent as path.
        """
        if not path:
            return self
        elif len(self.children) >= path[0]:
            return self.children[path[0]].get_node(path[1:])
        else:
            raise IndexError("Node with path {} does not exist".format(path))

    def __str__(self):
        return self.title



class PlaceHolderNode(MenuNode):
    """
    Just a placeholder node
    """

    def __init__(self, display, lock, title="Example"):
        super(self.__class__, self).__init__(display, title, lock)

    def _show(self):
        self.lock.acquire()
        self.display.clear()
        self.display.change_row(self.title, 0)
        self.lock.release()
        self._stop_flag.wait()
        return None


class SelectionMenu(MenuNode):
    """
    MenuNode representing a regular menu. Start returns the 
    selected MenuNode when stopped or on the press of the enter button.
    """

    def __init__(self, display, title, children, lock,
                 disable_back=False, led_control=None):
        if not children:
            raise ValueError("Children can't be empty")
        super(self.__class__, self).__init__(display, title,
                                             lock, children, disable_back)
        self._led_control = led_control

    def _show(self):
        self.lock.acquire()
        menu = Menu([str(child) for child in self.children],
                    self.display, self.title, led_control=self._led_control)

        def button_pressed(channel):
            self.lock.acquire()
            if channel == buttons.LEFT_BUTTON:
                # move left
                menu.move_selection_left()
            elif channel == buttons.RIGHT_BUTTON:
                # move right
                menu.move_selection_right()
            elif channel == buttons.ENTER_BUTTON:
                # enter
                self._enter_pressed()
            self.lock.release()

        # set up buttons
        menu.display_menu()
        GPIO.add_event_detect(buttons.ENTER_BUTTON, GPIO.RISING,
                              callback=button_pressed,
                              bouncetime=300)
        GPIO.add_event_detect(buttons.LEFT_BUTTON, GPIO.RISING,
                              callback=button_pressed, 
                              bouncetime=300)
        GPIO.add_event_detect(buttons.RIGHT_BUTTON, GPIO.RISING, 
                              callback=button_pressed, 
                              bouncetime=300)
        
        self.lock.release()
        
        self._stop_flag.wait()

        selected = menu.get_selected_index()
        menu.stop()

        self.stop()

        return selected

    def stop(self):
        super(self.__class__, self).stop()
        GPIO.remove_event_detect(buttons.ENTER_BUTTON)
        GPIO.remove_event_detect(buttons.LEFT_BUTTON)
        GPIO.remove_event_detect(buttons.RIGHT_BUTTON)

    def _enter_pressed(self):
        self._stop_flag.set()
    
