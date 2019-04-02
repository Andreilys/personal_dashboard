import requests
from bs4 import BeautifulSoup
import datetime
try:
    from .personal_info import GOODREADS_INFO
except:
    from personal_info import GOODREADS_INFO

class Books():
    def __init__(self):
        self.goodreads_url = f'https://www.goodreads.com/review/list/{GOODREADS_INFO["user_id"]}.xml?key={GOODREADS_INFO["api_key"]}&v=2&shelf=read&per_page=80&page=1'
        self.response = requests.get(self.goodreads_url)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.reviews = self.soup.find('reviews')


    # Returns the past n books you've read
    def get_past_n_books(self, number_of_books):
        books = []
        urls = []
        for review in self.reviews.find_all('review'):
            for title in review.find('title'):
                books.append(title)
            for url in review.find('url'):
                urls.append(url)
        books_and_url = "<strong><a href=\"https://www.goodreads.com/user/show/44094887-andrei-lyskov\">Recently Read Books:</a></strong><ol>"
        for i in range(number_of_books):
            books_and_url += f'<li><a href={urls[i]}> {books[i]} </a></li>'
        books_and_url += "</ol>"
        return books_and_url

    # Returns a dict containing your reading history for the past 6 months
    def get_past_reading_history(self):
        dates = []
        data_values = []
        month_dict = {'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'Jun' : 6, 'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12}
        books_dict = {}
        seven_months_ago = self.get_n_months_ago(6)
        for review in self.reviews.find_all('review'):
            for date_read in review.find('date_added'):
                month = date_read.split(" ")[1]
                year = date_read.split(" ")[5]
                date = datetime.date(int(year), month_dict[month], 1)
                if date >= seven_months_ago:
                    date = str(date)
                    if date in books_dict:
                        books_dict[date] += 1
                    else:
                        books_dict[date] = 1
        #If there was a month that I didn't finish a book, I want to set it to 0
        for some_month in range(7):
            some_month_ago = str(self.get_n_months_ago(some_month))
            if some_month_ago not in books_dict:
                books_dict[some_month_ago] = 0
        sorted_keys = sorted(books_dict.keys())
        for key in sorted_keys:
            year = key.split("-")[0]
            month = key.split("-")[1]
            dates.append(f'{month}/{year}')
            data_values.append(books_dict[key])
        reading_history = [{"label" : "Number of Books Read", "backgroundColor": "#33702a", "data" : data_values}]
        return reading_history, dates


    # Helper function which returns n month ago from now
    def get_n_months_ago(self, month):
        past_month = datetime.datetime.now().month - month
        past_year = datetime.datetime.now().year
        if past_month < 1:
            past_month = 12 + past_month
            past_year = past_year - 1
        return datetime.date(past_year, past_month, 1)