import xml.etree.ElementTree as ET
import urllib2
import xmltodict

URL = "https://www.yr.no/sted/Sverige/%C3%96sterg%C3%B6tland/Link%C3%B6ping/varsel.xml"


def update_weather():
    f = urllib2.urlopen(URL)
    data = f.read()
    f.close()

    weather = xmltodict.parse(data)

    print weather['weatherdata']['forecast']['tabular']['time'][0]#['symbol']


class WeatherInfo:

    def __init__(self, time, weather, precipitation, temperature):
        self.time = time 
        self.weather = weather 
        self.precipitation = precipitation
        self.temperature = temperature 

    def __str__(self):
        return 'implement'

