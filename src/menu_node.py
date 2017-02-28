import threading
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

    def __init__(self, display, title, button_control,
                 children=[], disable_back=False):
        if not isinstance(children, list):
            raise ValueError("Children must be list")
        self._button_control = button_control
        self.title = title
        self.children = children
        self.display = display
        self._disable_back = disable_back

    def setup(self):
        """
        Sets this menu node up for viewing.
        Returns nothing.
        """
        raise NotImplementedError('Update needs to be overridden!')

    def update(self):
        """
        Runs an iteration of this MenuNode. 

        Returns a tuple:
            (MenuNode.NO_NAVIGATION, None) if no navigation was done.
            (MenuNode.BACK, None) if a back navigation should be done.
            (MenuNode.ENTER, MenuNode-index) if a child (second) is to be entered.
        """
        if not self._disable_back:
            if self._button_control.is_pressed(buttons.BACK):
                return MenuNode.BACK, None
        res = self._update()
        assert isinstance(res, tuple)
        status, child = res
        assert status in (MenuNode.BACK, MenuNode.ENTER, MenuNode.NO_NAVIGATION)
        assert child is None or isinstance(child, int)
        return res

    def _update(self):
        """
        Internal update, override this and return:
            (MenuNode.NO_NAVIGATION, None) if no navigation was done.
            (MenuNode.BACK, None) if a back navigation should be done.
            (MenuNode.ENTER, MenuNode-index) if a child (second) is to be entered.

        Whether back-button is pressed doesn't need to be checked here.
        """
        raise NotImplementedError('Update needs to be overridden!')

    def stop(self):
        """
        Terminates the MenuNode, freeing up resources used by it.
        """
        raise NotImplementedError('Stop needs to be overridden!')

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

    def __init__(self, display, button_control, title="Example"):
        super(self.__class__, self).__init__(display, title, button_control)

    def setup(self):
        self.display.clear()
        self.display.change_row(self.title, 0)

    def _update(self):
        return MenuNode.NO_NAVIGATION, None


class SelectionMenu(MenuNode):
    """
    MenuNode representing a regular menu. Start returns the 
    selected MenuNode when stopped or on the press of the enter button.
    """

    def __init__(self, display, title, button_control, children,
                 disable_back=False, led_control=None):
        if not children:
            raise ValueError("Children can't be empty")
        super(self.__class__, self).__init__(display, title, button_control,
                                             children, disable_back)
        self._led_control = led_control
        self.menu = None

    def setup(self):
        self.menu = Menu([str(child) for child in self.children],
                    self.display, self.title, led_control=self._led_control,
                    blinking_leds=[self._led_control.ENTER])
        self.menu.setup()
    
    def _update(self):
        self.menu.update()
        if self._button_control.is_pressed(buttons.ENTER):
            return MenuNode.ENTER, self.menu.get_selected_index()
        elif self._button_control.is_pressed(buttons.LEFT):
            self.menu.move_selection_left()
        elif self._button_control.is_pressed(buttons.RIGHT):
            self.menu.move_selection_right()
        return MenuNode.NO_NAVIGATION, None

    def stop(self):
        self.menu.stop()

    # def _show(self):
    #     self.lock.acquire()
    #     menu = 

    #     def button_pressed(channel):
    #         self.lock.acquire()
    #         if channel == buttons.LEFT:
    #             # move left
    #             menu.move_selection_left()
    #         elif channel == buttons.RIGHT:
    #             # move right
    #             menu.move_selection_right()
    #         elif channel == buttons.ENTER:
    #             # enter
    #             self._enter_pressed()
    #         self.lock.release()

    #     # set up buttons
    #     menu.display_menu()
    #     GPIO.add_event_detect(buttons.ENTER, GPIO.RISING,
    #                           callback=button_pressed,
    #                           bouncetime=300)
    #     GPIO.add_event_detect(buttons.LEFT, GPIO.RISING,
    #                           callback=button_pressed, 
    #                           bouncetime=300)
    #     GPIO.add_event_detect(buttons.RIGHT, GPIO.RISING, 
    #                           callback=button_pressed, 
    #                           bouncetime=300)
    #     
    #     self.lock.release()
    #     
    #     self._stop_flag.wait()

    #     selected = menu.get_selected_index()
    #     menu.stop()

    #     self.stop()

    #     return selected

    # def _enter_pressed(self):
    #     self.stop()
    
