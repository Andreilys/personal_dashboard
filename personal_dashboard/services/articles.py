import requests
import json
import datetime

# TODO: Move these credentials to a separate file.
MEDIUM_USER = 'lyskovandrei'

class Articles():
    def __init__(self):
        # The Medium API is defunct, so we will not be able to get any data.
        # The methods in this class will return empty data structures.
        pass

    def get_past_n_articles(self, number_of_articles):
        return ""

    def get_past_n_month_writing_history(self, months):
        return [], []
