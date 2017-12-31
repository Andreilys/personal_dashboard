import requests
try:
	from .personal_info import MOVES_KEYS
except:
	from personal_info import MOVES_KEYS
import pickle
from statistics import mean
from datetime import datetime

#The moves class has the following methods: get_current_days_steps() which
# returns the current days steps, get_average_past_seven_steps() which takes
# the 7 past days of steps and returns the average. The other methods are mostly
#helper methods
class Moves():
    def __init__(self):
        self.client_id = MOVES_KEYS['client_id']
        self.client_secret = MOVES_KEYS['client_secret']
        self.redirect_uri = MOVES_KEYS['redirect_uri']
        self.auth_url = 'https://api.moves-app.com/oauth/v1/'
        self.base_url = 'https://api.moves-app.com/api/1.1/user/'
        try:
            with open('personal_dashboard/moves_data.pkl', 'rb') as pickle_file:
                moves = pickle.load(pickle_file)
                self.refresh_token = moves['refresh_token']
                self.access_token = moves['access_token']
                self.get_access_token()
        except:
            request_url = "https://api.moves-app.com/oauth/v1/authorize?response_type=code&client_id=" + MOVES_KEYS['client_id'] +"&scope=activity+location"
            print("Please go to this URL and authorize: " + request_url)
            auth_code = input("What is the authorization code in the code= slug? ")
            post_request = requests.post(self.auth_url + "access_token?grant_type=authorization_code&code=" + auth_code + "&client_id=" + self.client_id +
            "&client_secret=" + self.client_secret + "&redirect_uri="+ self.redirect_uri).json()
            self.access_token = post_request['access_token']
            self.refresh_token = post_request['refresh_token']
            moves = {"access_token" : self.access_token, "refresh_token" : self.refresh_token}
            with open('personal_dashboard/moves_data.pkl', 'wb') as output:
                pickle.dump(moves, output, pickle.HIGHEST_PROTOCOL)


    def get_access_token(self):
        data = requests.get(self.auth_url + 'tokeninfo?access_token=' + self.access_token)
        if data.status_code != 200:
            refresh = requests.post(self.auth_url + "access_token?grant_type=refresh_token&refresh_token=" + self.access_token + "&client_id=" + self.client_id + "&client_secret=" + client_secret).json()
            self.refresh_token = refresh["refresh_token"]
            self.access_token = refresh["access_token"]


    def get_current_days_steps(self):
    #This is meant as a catch in case no steps have been recorded today
        try:
            current_days_steps = requests.get(self.base_url + 'summary/daily?pastDays=1&access_token=' + self.access_token).json()
            step_count = 0
            for i in range(len(current_days_steps[0]["summary"])):
                try:
                    step_count += current_days_steps[0]["summary"][i]["steps"]
                except:
                    pass
            return step_count
        except Exception as e:
            return 0


    def get_past_seven_days_steps(self):
        past_seven_days_steps = requests.get(self.base_url + 'summary/daily?pastDays=8&access_token=' + self.access_token).json()
        past_seven_days_arr = []
        # Minus one to only look at the past 7 days instead of including the current as well
        for index in range(len(past_seven_days_steps) - 1):
            try:
                day_object_length = len(past_seven_days_steps[index]["summary"])
            except:
                day_object_length = 0
            for i in range(day_object_length):
                try:
                    past_seven_days_arr.append(past_seven_days_steps[index]["summary"][i]["steps"])
                except:
                    past_seven_days_arr.append(0)
        return past_seven_days_arr


    def get_average_past_seven_steps(self):
        seven_days_steps_arr = self.get_past_seven_days_steps()
        try:
            average = round(mean(seven_days_steps_arr))
        except:
            average = 0
        return average



    #Turn this method into a visualizaton for map
    def get_past_seven_days_places(self):
        past_seven_days_places = requests.get(self.base_url + 'places/daily?pastDays=7&access_token=' + self.access_token).json()
        # first 0 is for the length of places, second 0 is for length of segments
        past_seven_days_places_set = set()
        for i in range(len(past_seven_days_places)):
            try:
                segment_length = len(past_seven_days_places[i]['segments'])
            except:
                segment_length = 0
            for j in range(segment_length):
                try:
                    past_seven_days_places_set.add(past_seven_days_places[i]['segments'][j]['place']['name'])
                except:
                    continue
        return ', '.join(past_seven_days_places_set)

    #This function is used to return dates and a formatted list containing dictionaries
    # for use to create the steps_bar
    def get_daily_week_view(self):
        daily_steps_array = []
        average_steps_array = []
        avg = self.get_average_past_seven_steps()
        for i in range(7):
            average_steps_array.append(avg)
            past_seven_days_steps = requests.get(self.base_url + 'summary/daily?pastDays=7&access_token=' + self.access_token).json()
        for steps in past_seven_days_steps:
            try:
                daily_steps_array.append(steps['summary'][0]['steps'])
            except:
                daily_steps_array.append(0)
        steps_data = [{"label" : "Daily Steps", "backgroundColor": "#33702a", "data" : daily_steps_array},
        {"label" : "Average Steps", "backgroundColor": "#b30000", "data" : average_steps_array}]
        return steps_data
