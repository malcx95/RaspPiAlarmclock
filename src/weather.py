import xml.etree.ElementTree as ET
import urllib2
import xmltodict

URL = "https://www.yr.no/sted/Sverige/%C3%96sterg%C3%B6tland/Link%C3%B6ping/varsel.xml"

SYMBOL_MAP = {
    1 : "Sunny",
    2 : "Almost sunny",
    3 : "Partly cloudy",
    4 : "Overcast",
    40 : "Light showers",
    5 : "Showers",
    41 : "Heavy showers",
    24 : "Light thunder showers",
    6 : "Thunder showers",
    25 : "Heavy thunder showers",
    42 : "Light sleet showers",
    7 : "Sleet showers",
    43 : "Heavy sleet showers",
    26 : "Light sleet and thunder showers",
    20 : "Sleet and thunder showers",
    27 : "Heavy sleet and thunder showers",
    44 : "Light snow showers",
    8 : "Snow showers",
    45 : "Heavy snow showers",
    28 : "Light snow and thunder showers",
    21 : "Snow and thunder showers",
    29 : "What the fuck. Heavy snow and thunder showers",
    46 : "Light rain",
    9 : "Rain",
    10 : "Heavy rain",
    30 : "Light rain and thunder",
    22 : "Rain and thunder",
    11 : "Heavy rain and thunder",
    47 : "Light sleet",
    12 : "Sleet",
    48 : "Heavy sleet",
    31 : "Light sleet and thunder",
    23 : "Sleet and thunder",
    32 : "Heavy sleet and thunder",
    49 : "Light snow",
    13 : "Snow",
    50 : "Heavy snow",
    33 : "Light snow and thunder",
    14 : "Snow and thunder",
    34 : "What the fuck. Heavy snow and thunder",
    15 : "Fog"
}

def update_weather(url):
    """
    Fetches the latest weather data from the given yr.no url. Returns None if 
    the weather couldn't be updated.

    str -> WeatherInfo
    """
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()

    weather_data = xmltodict.parse(data)

    start_time = ':'.join(weather_data['weatherdata']['forecast']['tabular']\
            ['time'][0]['@from'].split("T")[1].split(":")[:2])

    end_time = ':'.join(weather_data['weatherdata']['forecast']['tabular']\
            ['time'][0]['@to'].split("T")[1].split(":")[:2])

    weather = SYMBOL_MAP[int(weather_data['weatherdata']['forecast']['tabular']
                         ['time'][0]['symbol']['@number'])]

    precipitation = weather_data['weatherdata']['forecast']['tabular']\
            ['time'][0]['precipitation']['@value']
    
    temperature = weather_data['weatherdata']['forecast']['tabular']\
            ['time'][0]['temperature']['@value']
    
    return WeatherInfo(start_time, end_time, weather, precipitation, temperature)


class WeatherInfo:

    def __init__(self, start_time, end_time, weather, precipitation, temperature):
        """
        string -> string -> string -> int -> int -> WeatherInfo
        """
        self.start_time = start_time 
        self.end_time = end_time 
        self.weather = weather 
        self.precipitation = precipitation
        self.temperature = temperature 

    def __str__(self):
        return 'implement'

update_weather(URL)

