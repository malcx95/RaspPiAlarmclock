#!/usr/bin/python
# coding=utf-8
import time
import sys
import threading
import RPi.GPIO as GPIO
from menu import Menu
from display import Display
from ledcontrol import LEDControl
from constants import *
from menu_elements import *


# def test():
#     display_lock = threading.Lock()
# 
#     display = Display(display_lock)
# 
#     menu = Menu(["Kebab", "Mysarna", "Mamma", "ha", "majs"],
#                 display, title="MAMMA GILLAR GLASS")
# 
#     def button_pressed(channel):
#         if channel == ENTER_BUTTON:
#             menu.move_selection_left()
#         elif channel == LEFT_BUTTON:
#             menu.move_selection_right()
# 
#     for button in BUTTONS.values():
#         GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#         GPIO.add_event_detect(button, GPIO.RISING, callback=button_pressed, 
#                 bouncetime=300)
# 
#     try:
#         clock = ClockFace(display)
#         clock.start()
#         while True:
#             time.sleep(10)
#     except KeyboardInterrupt:
#         display.clear()
#         display.message("Have a nice\nkebab!")
#         GPIO.cleanup()
#         clock.stop()
#         sys.exit(1)
# 
#     menu.stop()
#     display.clear()
#     display.message("Exiting")
#     sys.exit(0)


def main():

    display = Display()
    menu_lock = threading.Lock()

    # setup buttons
    for button in BUTTONS.values():
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # setup menu
    test_menu1_children = [PlaceHolderNode(display, menu_lock, "test1"),
                           PlaceHolderNode(display, menu_lock, "test2"),
                           PlaceHolderNode(display, menu_lock, "test3")]

    test_menu2_children = [PlaceHolderNode(display, menu_lock, "test4"),
                           PlaceHolderNode(display, menu_lock, "test5"),
                           PlaceHolderNode(display, menu_lock, "test6")]

    test_menu1 = SelectionMenu(display, "HEJHEJ", test_menu1_children, menu_lock)
    test_menu2 = SelectionMenu(display, "KEBAB", test_menu2_children, menu_lock)

    clock_face = ClockFace(display, menu_lock)

    main_children = [clock_face, test_menu1, test_menu2]

    main_menu = SelectionMenu(display, "Main menu", main_children,
                              menu_lock, disable_back=True)
    
    # list of indices tracing the path to the current node
    current_menu_selection = []

    def exit():
        menu_lock.acquire()
        main_menu.get_node(current_menu_selection).stop()
        menu_lock.release()

        display.clear()
        display.message("Have a nice\nkebab!")
        GPIO.cleanup()
        sys.exit(1)

    try:
        while True:
            back_pressed, child_selected = main_menu.get_node(
                current_menu_selection).start()
            menu_lock.acquire()
            if child_selected is not None and (not back_pressed):
                current_menu_selection.append(child_selected)
            elif back_pressed:
                if current_menu_selection:
                    current_menu_selection.pop()
            child_selected = None
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':
    main()
