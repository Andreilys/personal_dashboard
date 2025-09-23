from todoist_api_python.api import TodoistAPI
import time
import datetime as DT

# TODO: Move these credentials to a separate file.
TODOIST = {"email" : '12al104@queensu.ca', "password" : "logos101"}

class Todoist:
    def __init__(self):
        try:
            # The user has provided an email and password for Todoist, but the new
            # library uses an API token. I will assume the password is the API token.
            self.api = TodoistAPI(TODOIST["password"])
        except Exception as e:
            print(f"Error initializing Todoist API: {e}")
            self.api = None

    def get_completed_tasks(self, since):
        if not self.api:
            return []
        try:
            return self.api.get_completed_tasks(since=since)
        except Exception as e:
            print(f"Error getting completed tasks from Todoist: {e}")
            return []

    def get_daily_completed_tasks(self):
        today = DT.date.today().strftime("%Y-%m-%d")
        tasks = self.get_completed_tasks(since=today)
        return len(tasks)

    def get_past_seven_days_completed_tasks(self):
        seven_days_ago = (DT.date.today() - DT.timedelta(days=7)).strftime("%Y-%m-%d")
        tasks = self.get_completed_tasks(since=seven_days_ago)
        return len(tasks)

    def get_total_tasks(self):
        if not self.api:
            return 0
        try:
            return len(self.api.get_tasks())
        except Exception as e:
            print(f"Error getting total tasks from Todoist: {e}")
            return 0
