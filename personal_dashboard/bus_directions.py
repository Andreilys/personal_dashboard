import googlemaps
from datetime import datetime
import time
try:
    from .personal_info import GOOGLE_MAPS_API_KEY, HOME, WORK
except:
    from personal_info import GOOGLE_MAPS_API_KEY, HOME, WORK

#The NextBus class interacts with Google Maps directions API to find out
# when the next bus will be arriving that will take me from my house to
# main campus
class NextBus:
    #This method takes the departure text, converts it into a datetime object and
    # then does the necessary math to get the minutes left to leave
    def get_mins_left(self, now, departure):
        #Convert 12 hour into 24 hour
        if departure[-2:] == "am" or departure[:2] == "12":
            departure = departure[:-2].replace(":", "")
        else:
            departure = str(int(departure[:-2].replace(":", "")) + 1200)
        length = len(departure)
        #Add the semicolon back in so we can turn the time into a datetime object
        if length == 4:
            departure = departure[:2] + ":" + departure[2:]
        else:
            departure = departure[:1] + ":" + departure[1:]
        datetime_object = datetime.strptime(departure, "%H:%M")
        time_difference = datetime_object - now
        if round(time_difference.seconds/60) > 40:
            return "0 mins"
        return str(round(time_difference.seconds/60)) + " mins"


    def get_next_bus(self):
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        now = datetime.now()
        directions_result = gmaps.directions(HOME,
                                         WORK,
                                         mode="transit",
                                         departure_time=now)
        try:
            #reformat the departure time so that we can subtract it later from current time
            departure = directions_result[0]["legs"][0]["departure_time"]["text"]
            return self.get_mins_left(now, departure)
        except:
            return "Faster to walk"
