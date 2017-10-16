import requests
from .personal_info import MOVES_KEYS
import pickle
from statistics import mean
from datetime import datetime

#The moves class has the following methods: get_current_days_steps() which
# returns the current days steps, get_average_past_seven_steps() which takes
# the 7 past days of steps and returns the average. The other methods are mostly
#helper methods although get_past_seven_days_places is currently unused it may
# be incorporated in the future
class Moves():
	def __init__(self):
		self.client_id = MOVES_KEYS['client_id']	   # Client ID, get this by creating an app
		self.client_secret = MOVES_KEYS['client_secret'] # Client Secret, get this by creating an app
		self.redirect_url = MOVES_KEYS['redirect_url']  # Callback URL for getting an access token
		self.auth_url = 'https://api.moves-app.com/oauth/v1/'
		self.base_url = 'https://api.moves-app.com/api/1.1/user/'
		with open('personal_dashboard/moves_data.pkl', 'rb') as input:
			moves = pickle.load(input)
			self.refresh_token = moves['refresh_token']
			self.access_token = moves['access_token']
			self.get_access_token()


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
			current_days_steps = str(current_days_steps[0]['summary'][0]["steps"])
			return current_days_steps
		except:
			return 0


	def get_past_seven_days_steps(self):
		past_seven_days_steps = requests.get(self.base_url + 'summary/daily?pastDays=8&access_token=' + self.access_token).json()
		past_seven_days_arr = []
		for index in range(len(past_seven_days_steps) - 1):
			past_seven_days_arr.append(past_seven_days_steps[index]['summary'][0]['steps'])
		return past_seven_days_arr


	def get_average_past_seven_steps(self):
		seven_days_steps_arr = self.get_past_seven_days_steps()
		return round(mean(seven_days_steps_arr))


	#Turn this method into a visualizaton for map
	def get_past_seven_days_places(self):
		past_seven_days_places = requests.get(self.base_url + 'places/daily?pastDays=8&access_token=' + self.access_token).json()
		# first 0 is for the length of places, second 0 is for length of segments
		past_seven_days_places_set = set()
		for i in range(len(past_seven_days_places) - 1):
			segment_length = len(past_seven_days_places[i]['segments'])
			for j in range(segment_length):
				try:
					past_seven_days_places_set.add(place)
				except:
					continue
		return ', '.join(past_seven_days_places_set)
