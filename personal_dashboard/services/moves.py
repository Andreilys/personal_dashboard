import requests
import pickle
from statistics import mean
from datetime import datetime

# TODO: Move these credentials to a separate file.
MOVES_KEYS = {'client_id':'c418oY3nC9LbHQ4aRA3I79drjPGSjZpa', 'client_secret':'7s0DDpKVRg29kAgCaexjOIz2cnlnXWsOA4iscM6A6ly3coPqRIWfCLkHNiba905B', 'redirect_url': 'https://example.com/old/path'}

class Moves():
    def __init__(self):
        # The Moves API is defunct, so we will not be able to get any data.
        # The methods in this class will return empty data structures.
        pass

    def get_current_days_steps(self):
        return 0

    def get_past_seven_days_steps(self):
        return []

    def get_average_past_seven_steps(self):
        return 0

    def get_past_seven_days_places(self):
        return ""

    def get_daily_week_view(self):
        return []
