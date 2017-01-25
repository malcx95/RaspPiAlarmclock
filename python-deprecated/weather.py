import threading
import xml.etree.ElementTree as ET


class WeatherInfo:

    def __init__(self):
        self._lock = threading.Lock()
        self.time = None
        self.weather = None
        self.precipitation = None
        self.temperature = None
        self.refresh()

    def refresh(self):
        self._lock.acquire()
        # TODO do something
        self._lock.release()

    def __str__(self):
        return 'implement'

