import threading
try:
    import RPi.GPIO as GPIO
except ImportError:
    from simulator.gpio import GPIO
import buttons
import time
from menu import Menu


class MenuNode(object):
    """
    Generic class for things that can be in menu items.
    """

    # Constants returned from the update method
    ENTER = 0
    BACK = 1
    NO_NAVIGATION = 2

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

    def setup(self):
        """
        Sets this menu node up for viewing.
        """
        raise NotImplementedError('Update needs to be overridden!')

    def update(self):
        """
        Runs an iteration of this MenuNode. 

        Returns a tuple:
            (MenuNode.NO_NAVIGATION, None) if no navigation was done.
            (MenuNode.BACK, None) if a back navigation should be done.
            (MenuNode.ENTER, MenuNode) if a child (second) is to be entered.
        """
        raise NotImplementedError('Update needs to be overridden!')

    def stop(self):
        """
        Terminates the MenuNode, freeing up resources used by it.

        Returns the index of the selected MenuNode, if any. Returns
        None otherwise.
        """
        raise NotImplementedError('Update needs to be overridden!')

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
    Just a placeholder node.
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
    
    def _free_used_buttons(self):
        pass


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
                    self.display, self.title, led_control=self._led_control,
                    blinking_leds=[self._led_control.ENTER])

        def button_pressed(channel):
            self.lock.acquire()
            if channel == buttons.LEFT:
                # move left
                menu.move_selection_left()
            elif channel == buttons.RIGHT:
                # move right
                menu.move_selection_right()
            elif channel == buttons.ENTER:
                # enter
                self._enter_pressed()
            self.lock.release()

        # set up buttons
        menu.display_menu()
        GPIO.add_event_detect(buttons.ENTER, GPIO.RISING,
                              callback=button_pressed,
                              bouncetime=300)
        GPIO.add_event_detect(buttons.LEFT, GPIO.RISING,
                              callback=button_pressed, 
                              bouncetime=300)
        GPIO.add_event_detect(buttons.RIGHT, GPIO.RISING, 
                              callback=button_pressed, 
                              bouncetime=300)
        
        self.lock.release()
        
        self._stop_flag.wait()

        selected = menu.get_selected_index()
        menu.stop()

        self.stop()

        return selected

    def _free_used_buttons(self):
        GPIO.remove_event_detect(buttons.ENTER)
        GPIO.remove_event_detect(buttons.LEFT)
        GPIO.remove_event_detect(buttons.RIGHT)

    def _enter_pressed(self):
        self.stop()
    
