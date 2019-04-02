import datetime
import requests
from datetime import timedelta
try:
    from .personal_info import INSIGHT_MEDITATION_LOGIN
except:
    from personal_info import INSIGHT_MEDITATION_LOGIN


class Meditation():
    '''The meditation class gets meditation data from
    insight timer and returns it in a dictionary that maps
    the date to the time meditated'''
    def __init__(self):
        self.insight_csv_url = "https://profile.insighttimer.com/sessions/export"
        self.meditation_data = self.get_insight_data()

    def get_insight_data(self):
        ''' Retrieves the meditation data in a CSV format from insight timer'''
        session = requests.Session()
        session.auth = (INSIGHT_MEDITATION_LOGIN['username'], INSIGHT_MEDITATION_LOGIN['password'])
        session.post(self.insight_csv_url)
        response = session.get(self.insight_csv_url)
        # This gets rid of the header and deletes the empty space
        return response.text.split("\n")[2:-1]


    def get_weekly_meditation_data(self):
        '''Takes in the response from insight timer CSV and returns
        a meditation dictionary containing the dates and times for the past week'''
        meditation_dict = {}
        dates = []
        data_values = []
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        for row in self.meditation_data:
            meditation_date = self.get_date(row)
            meditation_date_key = row.split(" ")[0]
            if meditation_date <= week_ago:
                break
            meditation_time = row.split(",")[1].split(":")[1]
            if meditation_date_key in meditation_dict:
                meditation_dict[meditation_date_key] += int(meditation_time)
            else:
                meditation_dict[meditation_date_key] = int(meditation_time)
        # If there was a day with no meditation, the day should be set it to 0
        for some_day in range(1, 7):
            some_day_ago = str(self.get_n_days_ago(some_day))
            if some_day_ago not in meditation_dict:
                meditation_dict[some_day_ago] = 0
        sorted_keys = sorted(meditation_dict.keys())
        for key in sorted_keys:
            month = key.split("/")[0]
            day = key.split("/")[1]
            dates.append(f'{day}/{month}')
            data_values.append(meditation_dict[key])
        meditation_history = [{"label" : "Minutes Meditated", "backgroundColor": "#33702a", "data" : data_values}]
        return meditation_history, dates


    def get_n_days_ago(self, day):
        today = datetime.datetime.now()
        days_ago = datetime.timedelta(days = day)
        day = today - days_ago
        day = str(day).split(" ")[0]
        date = day.split("-")
        year = date[0]
        month = date[1]
        day = date[2]
        date_formatted = f'{month}/{day}/{year}'
        return date_formatted


    def get_current_meditation_time(self):
        '''Takes in the response from insight timer CSV and returns
        how much you meditated today.'''
        meditation_dict = {}
        today = datetime.date.today()
        total_meditation = 0
        for row in self.meditation_data:
            meditation_date = self.get_date(row)
            if meditation_date != today:
                break
            meditation_time = row.split(",")[1].split(":")[1]
            total_meditation += int(meditation_time)
        return total_meditation


    def get_date(self, row):
        '''Takes in a insight row and returns only the meditation
         date in YYYY-MM-DD datetime format'''
        date_and_time = row.split(",")[0]
        month, day, year = map(int, date_and_time.split(" ")[0].split("/"))
        hour, mins, _ = map(int, date_and_time.split(" ")[1].split(":"))
        # minus 5 hours to get EST time since insight timer is in UTC
        converted_date = datetime.datetime(
            year, month, day, hour, mins) - timedelta(hours=5)
        # Since we only care about the date, thats the only thing we return
        return datetime.date(converted_date.year, converted_date.month, converted_date.day)
