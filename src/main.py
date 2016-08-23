#!/usr/bin/python
# coding=utf-8
import time
import sys
import threading
import RPi.GPIO as GPIO
from menu import Menu
from display import Display
from ledcontrol import LEDControl
from clock_face import ClockFace
import buttons
from menu_node import *
from alarm import AlarmSupervisorThread


def main():

    display = Display()
    led_control = LEDControl()

    menu_lock = threading.Lock()

    # setup buttons
    for button in buttons.BUTTONS.values():
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # setup menu
    test_menu1_children = [PlaceHolderNode(display, menu_lock, "test1"),
                           PlaceHolderNode(display, menu_lock, "test2"),
                           PlaceHolderNode(display, menu_lock, "test3"),
                           PlaceHolderNode(display, menu_lock, "test4"),
                           PlaceHolderNode(display, menu_lock, "test5"),
                           PlaceHolderNode(display, menu_lock, "tesss"),
                           PlaceHolderNode(display, menu_lock, "tess"),
                           PlaceHolderNode(display, menu_lock, "tessd"),
                           PlaceHolderNode(display, menu_lock, "tersw"),
                           PlaceHolderNode(display, menu_lock, "tehws"),
                           PlaceHolderNode(display, menu_lock, "test6")]

    test_menu1 = SelectionMenu(display, "HEJHEJ", 
                               test_menu1_children, menu_lock,
                               led_control=led_control)

    clock_face = ClockFace(display, menu_lock)

    main_children = [clock_face, test_menu1]

    main_menu = SelectionMenu(display, "Main menu", main_children,
                              menu_lock, disable_back=True,
                              led_control=led_control)
    
    # list of indices tracing the path to the current node
    current_menu_selection = []

    alarm_thread = AlarmSupervisorThread(display, led_control)
    alarm_thread.start()

    def exit():
        main_menu.get_node(current_menu_selection).stop()
        display.clear()
        display.message("Have a nice\nkebab!")
        GPIO.cleanup()
        sys.exit(1)

    alarm_thread.set_alarm('2205')

    try:
        while True:
            led_control.clear()
            selected_node = main_menu.get_node(current_menu_selection)
            alarm_thread.set_selected_menu_node(selected_node)
            back_pressed, child_selected = selected_node.start()
            menu_lock.acquire()
            if alarm_thread.alarm_gone_off:
                alarm_thread.permission_to_start.set()
                alarm_thread.alarm_dismissed.wait()
            else:
                if child_selected is not None and (not back_pressed):
                    current_menu_selection.append(child_selected)
                elif back_pressed:
                    if current_menu_selection:
                        current_menu_selection.pop()
            child_selected = None
            menu_lock.release()
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':
    main()
