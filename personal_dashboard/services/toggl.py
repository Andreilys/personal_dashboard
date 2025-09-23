import requests
import time
import datetime as DT

# TODO: Move these credentials to a separate file.
TOGGL_API_TOKEN = 'fab0834862bcf57035b57bb39f0ae13f'

class Toggl():
    def __init__(self):
        try:
            self.json = requests.get(
                'https://api.track.toggl.com/api/v9/me/time_entries',
                auth=(TOGGL_API_TOKEN, 'api_token')
            ).json()
        except Exception as e:
            print(f"Error getting data from Toggl: {e}")
            self.json = []

    def get_pomodoros(self, dates):
        pomodoro_dict = {}
        if not isinstance(self.json, list):
            return pomodoro_dict

        for time_entry in self.json:
            if 'start' not in time_entry or 'duration' not in time_entry:
                continue

            start_date_str = time_entry['start'].split('T')[0]
            if start_date_str in dates:
                duration_hours = time_entry['duration'] / 3600
                description = time_entry.get('description', "No description")

                if description != 'Pomodoro Break':
                    if duration_hours < 0:
                        # Handle running timers
                        duration_hours = (int(time.time()) + time_entry['duration']) / 3600

                    pomodoro_dict[description] = pomodoro_dict.get(description, 0) + round(duration_hours, 2)
        return pomodoro_dict

    def get_daily_pomodoros(self):
        today_str = DT.date.today().strftime("%Y-%m-%d")
        return self.get_pomodoros([today_str])

    def get_past_seven_days_pomodoros(self):
        dates = [(DT.date.today() - DT.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        return self.get_pomodoros(dates)

    def get_daily_week_view(self):
        toggl_data = []
        seven_day_pomodoros = self.get_past_seven_days_pomodoros()

        for description in seven_day_pomodoros:
            weekly_data = [description]
            for i in range(6, -1, -1):
                date = DT.date.today() - DT.timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")

                daily_pomodoros = self.get_pomodoros([date_str])
                value = daily_pomodoros.get(description, 0)

                daily_data = {'year': date.year, 'month': date.month, 'day': date.day, 'value': value}
                weekly_data.append(daily_data)
            toggl_data.append(weekly_data)

        return toggl_data