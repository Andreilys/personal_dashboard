import requests
from bs4 import BeautifulSoup
import datetime

# TODO: Move these credentials to a separate file.
GOODREADS_INFO = {"user_id": '44094887', 'api_key': 'NOb1kR9igNzL8EABBp0hg'}

class Books():
    def __init__(self):
        # The Goodreads API is defunct, so we will not be able to get any data.
        # The methods in this class will return empty data structures.
        pass

    def get_past_n_books(self, number_of_books):
        return ""

    def get_past_reading_history(self):
        return [], []