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

    alarms = [(Alarm(10, 0, 28, 8, 2016, False), False)]

    # setup buttons
    for button in buttons.BUTTONS.values():
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    clock_face = ClockFace(display, menu_lock)

    main_children = [clock_face,
                     AlarmApplication(display, menu_lock, led_control, alarms)]

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

    time.sleep(1)

    alarm_thread.set_alarm('201608232300')

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
