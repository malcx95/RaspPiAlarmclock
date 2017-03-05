import unittest
import alarm
import os

def clear_alarms(alarms_file):
    if os.path.isfile(alarms_file):
        os.system('rm ' + alarms_file)

# TODO add more tests

class AlarmListTests(unittest.TestCase):

    ALARMS_TEST_FILE = 'tests/alarms_test.json'
    
    def setup(self):
        clear_alarms(self.ALARMS_TEST_FILE)

    def test_save_and_load_alarms(self):
        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        al = alarm.Alarm(7, 0, 1, 0)
        alarms.add_alarm(al, True)
        alarms.save()

        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        active_alarms = alarms.get_active_alarms()
        self.assertIn(al, active_alarms)
        self.assertTrue(len(alarms.get_inactive_alarms()) == 0)

    def test_add_alarm(self):
        clear_alarms(self.ALARMS_TEST_FILE)
        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        al = alarm.Alarm(7, 0, 1, 0)
        alarms.add_alarm(al, True)
        self.assertIn(al, alarms.get_active_alarms())

    def test_add_alarm_inactive(self):
        clear_alarms(self.ALARMS_TEST_FILE)
        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        al = alarm.Alarm(7, 0, 1, 0)
        alarms.add_alarm(al, False)
        self.assertIn(al, alarms.get_inactive_alarms())

    def test_change_to_activated(self):
        clear_alarms(self.ALARMS_TEST_FILE)
        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        al = alarm.Alarm(7, 0, 1, 0)
        alarms.add_alarm(al, False)
        alarms.set_alarm_activated(al, True, False)
        # check if alarm is now activated
        self.assertIn(al, alarms.get_active_alarms())
        self.assertNotIn(al, alarms.get_inactive_alarms())
        
    def test_change_to_activated(self):
        clear_alarms(self.ALARMS_TEST_FILE)
        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        al = alarm.Alarm(7, 0, 1, 0)
        alarms.add_alarm(al, True)
        alarms.set_alarm_activated(al, False, True)
        # check if alarm is now activated
        self.assertIn(al, alarms.get_inactive_alarms())
        self.assertNotIn(al, alarms.get_active_alarms())
        
    def test_alarm_delete(self):
        clear_alarms(self.ALARMS_TEST_FILE)
        alarms = alarm.AlarmList(self.ALARMS_TEST_FILE)
        al = alarm.Alarm(7, 0, 1, 0)
        alarms.add_alarm(al, True)
        alarms.delete_alarm(al)
        self.assertNotIn(al, alarms)

