#!/usr/bin/python
# coding=utf-8
import time
import sys
import threading
import os
from menu import Menu
from display import Display, TOP_ROW
from ledcontrol import LEDControl
from clock_face import ClockFace
from datetime import datetime
import buttons
from menu_node import *
from alarm import Alarm, AlarmList
from alarm_app import AlarmApplication
try:
    import RPi.GPIO as GPIO
except ImportError:
    from simulator.gpio import GPIOSimulator

SAVE_DIR = os.path.expanduser('~/.local/share/AlarmClockFiles')
ALARMS_FILE = os.path.join(SAVE_DIR, 'alarms.json')


def sound_alarm_if_neccessary(alarm_list, button_control, display, time):
    """
    Sounds the alarm given by the alarm list, unless it's None.
    Also deactivates it if necessary.

    Alarm -> AlarmList -> None
    """
    gone_off_alarm = alarm_list.get_gone_off_alarm(time)
    if gone_off_alarm is None:
        return
    alarm_list.delete_alarm(gone_off_alarm, True)
    display.clear()
    display.show_cursor(False)
    iteration = False
    while not button_control.wait_for_press(buttons.ENTER, 500):
        if iteration:
            display.change_row('WAKE UP!!', TOP_ROW)
        else:
            display.clear()

        iteration = not iteration

    alarm_list.add_alarm(gone_off_alarm,
                         gone_off_alarm.repeat != Alarm.NO_REPEAT)
    display.show_cursor(True)


def main():

    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    if not os.path.isdir(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    display = Display()

    led_control = LEDControl()

    alarm_list = AlarmList(ALARMS_FILE)

    # setup buttons
    button_control = buttons.ButtonControl()

    clock_face = ClockFace(display, button_control)

    main_children = [clock_face,
                     AlarmApplication(display, led_control,
                                      alarm_list, button_control)]

    main_menu = SelectionMenu(display, "Main menu",
                              button_control, main_children,
                              disable_back=True, led_control=led_control)
    
    # list of indices tracing the path to the current node
    current_menu_selection = []

    # alarm_thread = alarm.AlarmSupervisorThread(display, led_control)
    # alarm_thread.start()

    def exit():
        # main_menu.get_node(current_menu_selection).stop()
        # display.clear()
        # display.message("Have a nice\nkebab!")
        GPIO.cleanup()
        sys.exit(1)

    time.sleep(0.1)

    try:
        led_control.clear()
        while True:
            selected_node = main_menu.get_node(current_menu_selection)
            selected_node.setup()

            while True:
                button_control.update()
                navigation, child = selected_node.update()
                if navigation != MenuNode.NO_NAVIGATION:
                    if navigation == MenuNode.BACK and \
                       len(current_menu_selection) > 0:
                        current_menu_selection.pop()
                    elif navigation == MenuNode.ENTER:
                        current_menu_selection.append(child)
                    selected_node.stop()
                    break
                sound_alarm_if_neccessary(alarm_list, button_control,
                                          display, datetime.now())
                time.sleep(0.1)
            # alarm_thread.set_selected_menu_node(selected_node)
            # back_pressed, child_selected = selected_node.start()
            # if alarm_thread.alarm_gone_off:
            #     alarm_thread.permission_to_start.set()
            #     alarm_thread.alarm_dismissed.wait()
            # else:
            #     if child_selected is not None and (not back_pressed):
            #         current_menu_selection.append(child_selected)
            #     elif back_pressed:
            #         if current_menu_selection:
            #             current_menu_selection.pop()
            # child_selected = None
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    main()
