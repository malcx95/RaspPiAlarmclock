import unittest
import simulator.buttons as buttons
from menu_node import MenuNode
import alarm_app
from datetime import datetime
import pdb
import display
import ledcontrol
import alarm
import os

ALARMS_TEST_FILE = 'tests/alarms_test.json'

TEST_ALARMS = [
    (alarm.Alarm(7, 30, 1, 0), True),
    (alarm.Alarm(8, 0, 1, 2), True),
    (alarm.Alarm(2, 15, 4, 0), False),
    (alarm.Alarm(7, 10, 1, 1), True),
    (alarm.Alarm(7, 0, 1, 0), False),
]

def clear_alarms(alarms_file):
    if os.path.isfile(alarms_file):
        os.system('rm ' + alarms_file)


def create_alarm_list_and_test_alarm():
    """
    Inits the alarm list and an alarm

    void -> (Alarm, AlarmList)
    """
    clear_alarms(ALARMS_TEST_FILE)
    alarms = alarm.AlarmList(ALARMS_TEST_FILE)
    al = alarm.Alarm(7, 0, 1, 0)
    return al, alarms


def init_alarm_app(alarm_list=None, button_control=None):
    """
    Inits an alarm app.

    void -> AlarmApplication
    AlarmList -> ButtonControl -> AlarmApplication
    """
    if alarm_list is None:
        _, alarm_list = create_alarm_list_and_test_alarm()
    display_ = display.Display()
    led_control = ledcontrol.LEDControl()
    if button_control is None:
        button_control = buttons.ButtonControl()
    return alarm_app.AlarmApplication(display_, 
                                      led_control,
                                      alarm_list,
                                      button_control)


class AlarmAppTests(unittest.TestCase):

    def test_init(self):
        app = init_alarm_app()
        self.assertIsNone(app.menu, msg="Menu is initialized in init")

    def test_setup_empty_alarm_list(self):
        app = init_alarm_app()
        app.setup()
        # There should be one less alarm 
        # than number of options (because of "new")
        self.assertTrue(app.alarm_list.num_alarms() == len(app.menu.options) - 1,
                       msg="An option was not created for each alarm")

    def test_setup_one_alarm(self):
        al, alarm_list = create_alarm_list_and_test_alarm()
        alarm_list.add_alarm(al, True)
        app = init_alarm_app(alarm_list)
        app.setup()
        self.assertFalse(app.alarm_list.is_empty(), 
                         msg="No placeholder was created")
        # There should be one less alarm 
        # than number of options (because of "new")
        self.assertTrue(app.alarm_list.num_alarms() == len(app.menu.options) - 1,
                        msg="An option was not created for each alarm")

    def test_delete_alarm(self):
        al, alarm_list = create_alarm_list_and_test_alarm()
        for alarm, activated in TEST_ALARMS:
            alarm_list.add_alarm(alarm, activated)

        sample_alarm = alarm_list.get_active_alarms()[0]

        button_control = buttons.ButtonControl()
        button_control.set_sequence([False, False, True], buttons.DELETE)
        app = init_alarm_app(alarm_list, button_control)
        app.setup()

        for i in range(2):
            active_alarms = app.alarm_list.get_active_alarms()
            self.assertIn(sample_alarm, active_alarms, 
                          msg="Alarm deleted too early")

            button_control.update()
            nav, child = app.update()
            self.assertIsNone(child, msg="Unexpected child")
            self.assertEqual(nav, MenuNode.NO_NAVIGATION, 
                             msg="Expected NO_NAVIGATION")

        active_alarms = app.alarm_list.get_active_alarms()
        self.assertNotIn(sample_alarm, active_alarms, 
                         msg="Alarm not deleted")

    def test_delete_alarm_inactive(self):
        al, alarm_list = create_alarm_list_and_test_alarm()
        for alarm, activated in TEST_ALARMS:
            alarm_list.add_alarm(alarm, activated)

        # needs to be the last one
        sample_alarm = alarm_list.get_inactive_alarms()[-1]

        button_control = buttons.ButtonControl()
        button_control.set_sequence([False, False, True], buttons.DELETE)
        # navigate left to the last inactivated alarm
        button_control.set_sequence([True, True, False], buttons.LEFT)
        app = init_alarm_app(alarm_list, button_control)
        app.setup()

        for i in range(2):
            inactive_alarms = app.alarm_list.get_inactive_alarms()
            self.assertIn(sample_alarm, inactive_alarms, 
                          msg="Alarm deleted too early")

            nav, child = app.update()
            self.assertIsNone(child, msg="Unexpected child")
            self.assertEqual(nav, MenuNode.NO_NAVIGATION, 
                             msg="Expected NO_NAVIGATION")
            button_control.update()

        nav, child = app.update()
        self.assertIsNone(child, msg="Unexpected child")
        self.assertEqual(nav, MenuNode.NO_NAVIGATION, 
                         msg="Expected NO_NAVIGATION")

        inactive_alarms = app.alarm_list.get_inactive_alarms()
        self.assertNotIn(sample_alarm, inactive_alarms, 
                         msg="Alarm not deleted")

    def test_inactivate_alarm(self):
        al, alarm_list = create_alarm_list_and_test_alarm()
        for alarm, activated in TEST_ALARMS:
            alarm_list.add_alarm(alarm, activated)

        sample_alarm = alarm_list.get_active_alarms()[0]

        button_control = buttons.ButtonControl()
        button_control.set_sequence([False, False, True], buttons.SET)
        app = init_alarm_app(alarm_list, button_control)
        app.setup()

        for i in range(2):
            inactive_alarms = app.alarm_list.get_inactive_alarms()
            active_alarms = app.alarm_list.get_active_alarms()
            self.assertIn(sample_alarm, active_alarms, 
                          msg="Alarm changed too early")
            self.assertNotIn(sample_alarm, inactive_alarms, 
                          msg="Alarm changed too early")

            button_control.update()
            nav, child = app.update()
            self.assertIsNone(child, msg="Unexpected child")
            self.assertEqual(nav, MenuNode.NO_NAVIGATION, 
                             msg="Expected NO_NAVIGATION")

        inactive_alarms = app.alarm_list.get_inactive_alarms()
        active_alarms = app.alarm_list.get_active_alarms()
        self.assertNotIn(sample_alarm, active_alarms, 
                         msg="Alarm not removed from active")
        self.assertIn(sample_alarm, inactive_alarms, 
                         msg="Alarm not added to inactive")
        
    def test_activate_alarm(self):
        al, alarm_list = create_alarm_list_and_test_alarm()
        for alarm, activated in TEST_ALARMS:
            alarm_list.add_alarm(alarm, activated)

        # needs to be the last one
        sample_alarm = alarm_list.get_inactive_alarms()[-1]

        button_control = buttons.ButtonControl()
        button_control.set_sequence([False, False, True], buttons.SET)

        # navigate left to the last inactivated alarm
        button_control.set_sequence([True, True, False], buttons.LEFT)
        app = init_alarm_app(alarm_list, button_control)
        app.setup()

        for i in range(2):
            inactive_alarms = app.alarm_list.get_inactive_alarms()
            active_alarms = app.alarm_list.get_active_alarms()
            self.assertIn(sample_alarm, inactive_alarms, 
                          msg="Alarm changed too early")
            self.assertNotIn(sample_alarm, active_alarms, 
                          msg="Alarm changed too early")

            nav, child = app.update()
            self.assertIsNone(child, msg="Unexpected child")
            self.assertEqual(nav, MenuNode.NO_NAVIGATION, 
                             msg="Expected NO_NAVIGATION")
            button_control.update()

        nav, child = app.update()
        self.assertIsNone(child, msg="Unexpected child")
        self.assertEqual(nav, MenuNode.NO_NAVIGATION, 
                         msg="Expected NO_NAVIGATION")

        inactive_alarms = app.alarm_list.get_inactive_alarms()
        active_alarms = app.alarm_list.get_active_alarms()
        self.assertNotIn(sample_alarm, inactive_alarms, 
                         msg="Alarm not removed from inactive")
        self.assertIn(sample_alarm, active_alarms, 
                         msg="Alarm not added to active")


    def test_create_new_alarm(self):
        al, alarm_list = create_alarm_list_and_test_alarm()
        for alarm, activated in TEST_ALARMS:
            alarm_list.add_alarm(alarm, activated)
        
        old_num_alarms = alarm_list.num_alarms()
        old_num_activated = alarm_list.num_active_alarms()

        button_control = buttons.ButtonControl()

        # press the "new"-button
        button_control.set_sequence([False, True], buttons.ENTER)

        # navigate left to the new-option
        button_control.set_sequence([True, False], buttons.LEFT)

        app = init_alarm_app(alarm_list, button_control)
        app.setup()

        num_alarms = app.alarm_list.num_alarms()
        num_activated = app.alarm_list.num_active_alarms()
        self.assertEqual(num_alarms, old_num_alarms,
                        msg="Alarm added too soon")
        self.assertEqual(num_activated, old_num_activated,
                        msg="Alarm added too soon")

        nav, child = app.update()
        self.assertIsNone(child, msg="Unexpected child")
        self.assertEqual(nav, MenuNode.NO_NAVIGATION,
                         msg="Expected NO_NAVIGATION")

        button_control.update()

        nav, child = app.update()
        self.assertIsNotNone(child, msg="Child should not be None")
        self.assertEqual(nav, MenuNode.ENTER,
                         msg="Expected NO_NAVIGATION")

        num_alarms = app.alarm_list.num_alarms()
        num_activated = app.alarm_list.num_active_alarms()
        self.assertEqual(num_alarms, old_num_alarms + 1,
                        msg="Alarm not added")
        self.assertEqual(num_activated, old_num_activated + 1,
                        msg="Alarm not active or added")


class AlarmListTests(unittest.TestCase):

    def setup(self):
        clear_alarms(ALARMS_TEST_FILE)

    def test_save_and_load_alarms(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, True)
        alarms.save()

        alarms = alarm.AlarmList(ALARMS_TEST_FILE)
        active_alarms = alarms.get_active_alarms()
        self.assertIn(al, active_alarms)
        self.assertTrue(len(alarms.get_inactive_alarms()) == 0)

    def test_add_alarm(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, True)
        self.assertIn(al, alarms.get_active_alarms())

    def test_add_then_delete(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, True)
        self.assertIn(al, alarms.get_active_alarms())

    def test_add_alarm_inactive(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, False)
        self.assertIn(al, alarms.get_inactive_alarms())

    def test_change_to_activated(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, False)
        alarms.set_alarm_activated(al, True, False)
        # check if alarm is now activated
        self.assertIn(al, alarms.get_active_alarms())
        self.assertNotIn(al, alarms.get_inactive_alarms())
        
    def test_change_to_inactivated(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, True)
        alarms.set_alarm_activated(al, False, True)
        # check if alarm is now inactivated
        self.assertIn(al, alarms.get_inactive_alarms())
        self.assertNotIn(al, alarms.get_active_alarms())
        
    def test_alarm_delete(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, True)
        alarms.delete_alarm(al, True)
        self.assertNotIn(al, alarms.get_inactive_alarms())
        self.assertNotIn(al, alarms.get_active_alarms())

    def test_alarm_delete_inactive(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, False)
        alarms.delete_alarm(al, False)
        self.assertNotIn(al, alarms.get_inactive_alarms())
        self.assertNotIn(al, alarms.get_active_alarms())

    def test_alarm_gone_off_empty_alarm_list(self):
        _, alarms = create_alarm_list_and_test_alarm()

        # check every possible time
        for day in range(7):
            for minute in range(60):
                for hour in range(24):
                    time = datetime(2017, 03, 20 + day, hour, minute).strftime(
                        alarm.TIME_FORMAT)
                    # the alarm should never go off
                    self.assertIsNone(alarms.get_gone_off_alarm(time))

    def test_alarm_gone_off_one_inactivated_alarm(self):
        al, alarms = create_alarm_list_and_test_alarm()
        alarms.add_alarm(al, False)

        # check every possible time
        for day in range(7):
            for minute in range(60):
                for hour in range(24):
                    time = datetime(2017, 03, 20 + day, hour, minute).strftime(
                        alarm.TIME_FORMAT)
                    # the alarm should never go off
                    self.assertIsNone(alarms.get_gone_off_alarm(time))

    def test_alarm_gone_off_mixed(self):
        _, alarms = create_alarm_list_and_test_alarm()
        al1 = alarm.Alarm(7, 30, 0, 0)
        alarms.add_alarm(al1, True)

        al2 = alarm.Alarm(10, 0, 0, 0)
        alarms.add_alarm(al2, False)

        al3 = alarm.Alarm(15, 30, 1, 0)
        alarms.add_alarm(al3, True)

        al4 = alarm.Alarm(16, 30, 2, 1)
        alarms.add_alarm(al4, True)

        al5 = alarm.Alarm(9, 30, 0, 2)
        alarms.add_alarm(al5, True)

        # should not go off
        time1 = datetime(2017, 03, 20, 10, 0)

        # al1 should go off
        time2 = datetime(2017, 03, 20, 7, 30)

        # should not go off
        time3 = datetime(2017, 03, 20, 10, 0)

        # al3 should go off
        time4 = datetime(2017, 03, 21, 15, 30)

        # al4 should go off, since repeated daily
        time5 = datetime(2017, 03, 20, 16, 30)

        # al5 should go off, since repeated weekly
        time6 = datetime(2017, 03, 27, 9, 30)

        # should not go off
        time7 = datetime(2017, 03, 28, 9, 30)

        # should not go off
        time8 = datetime(2017, 03, 27, 9, 29)

        self.assertIsNone(alarms.get_gone_off_alarm(time1),
                         msg="Alarm shouldn't go off but did")

        self.assertEquals(alarms.get_gone_off_alarm(time2), al1,
                         msg="Alarm 1 should go off but didn't")

        self.assertIsNone(alarms.get_gone_off_alarm(time3),
                         msg="Alarm shouldn't go off but did")

        self.assertEquals(alarms.get_gone_off_alarm(time4), al3,
                         msg="Alarm 3 should go off but didn't")

        self.assertEquals(alarms.get_gone_off_alarm(time5), al4,
                         msg="Alarm 4 should go off but didn't")

        self.assertEquals(alarms.get_gone_off_alarm(time6), al5,
                         msg="Alarm 5 should go off but didn't")

        self.assertIsNone(alarms.get_gone_off_alarm(time7),
                         msg="Alarm shouldn't go off but did")

        self.assertIsNone(alarms.get_gone_off_alarm(time8),
                         msg="Alarm shouldn't go off but did")

