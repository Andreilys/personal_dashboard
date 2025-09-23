import datetime
import requests
from datetime import timedelta

# TODO: Move these credentials to a separate file.
INSIGHT_MEDITATION_LOGIN = {"username": "andreilyskov@gmail.com", "password": "meditate"}

class Meditation():
    '''The meditation class gets meditation data from
    insight timer and returns it in a dictionary that maps
    the date to the time meditated'''
    def __init__(self):
        # The Insight Timer API is defunct, so we will not be able to get any data.
        # The methods in this class will return empty data structures.
        self.meditation_data = []

    def get_weekly_meditation_data(self):
        return [], []

    def get_current_meditation_time(self):
        return 0
