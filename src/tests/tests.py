import unittest
import alarm
import os

ALARMS_TEST_FILE = 'tests/alarms_test.json'

def clear_alarms(alarms_file):
    if os.path.isfile(alarms_file):
        os.system('rm ' + alarms_file)


# void -> (Alarm, AlarmList)
def create_alarm_list_and_test_alarm():
    """
    Inits the alarm list and an alarm
    """
    clear_alarms(ALARMS_TEST_FILE)
    alarms = alarm.AlarmList(ALARMS_TEST_FILE)
    al = alarm.Alarm(7, 0, 1, 0)
    return al, alarms

# TODO add more tests

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

