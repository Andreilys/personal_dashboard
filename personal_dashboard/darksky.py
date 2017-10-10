import requests
import datetime
from .personal_info import DARKSKY_KEY

# Dark sky initializes and pulls the weather forecast for the week (Weather_today)
# in addition to the current weather today, and temperature right now
class DarkSky():
    def __init__(self):
        r = requests.get('https://api.darksky.net/forecast/{0}/44.225228,%20-76.507983?units=auto'.format(DARKSKY_KEY))
        #This is in case we hit the API limit on darkskys
        if r.status_code != 403:
            json = r.json()
            self.weather_today = json["hourly"]["summary"]
            self.weather_hourly = json["minutely"]["summary"]
            degree_sign= u'\N{DEGREE SIGN}'
            self.temp = str(json["currently"]["apparentTemperature"]) + degree_sign + "C"
        else:
            self.weather_today = 0
            self.weather_hourly = 0
            degree_sign= u'\N{DEGREE SIGN}'
            self.temp = "0" + degree_sign + "C"
