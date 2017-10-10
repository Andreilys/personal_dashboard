from pytodoist import todoist
from .personal_info import TODOIST

#Todoist class has three methods: get_past_seven_completed_task which
#returns the number of tasks completed in the last 7 days, get_today_completed_task
# which returns the number of tasks finished today, and get_total_tasks which
# returns the number of total tasks left
class Todoist():
    def __init__(self):
        #This is meant as a safe guard against too many todoist API calls
        try:
            self.user = todoist.login(TODOIST["email"], TODOIST["password"])
            self.productivity = self.user.get_productivity_stats()
            self.days_items = self.productivity["days_items"]
        except:
            self.days_items = [{"total_completed" : 0}]


    def get_past_seven_completed_tasks(self):
        completed_tasks = 0
        for i in range(len(self.days_items)):
            completed_tasks += self.days_items[i]["total_completed"]
        return completed_tasks


    def get_daily_completed_tasks(self):
        return self.days_items[0]["total_completed"]


    def get_total_tasks(self):
        number_of_tasks = 0
        #This is meant as a safeguard against too many Todoist API calls
        try:
            projects = self.user.get_projects()
            for project in projects:
                tasks = project.get_tasks()
                number_of_tasks += len(tasks)
            return number_of_tasks
        except:
            return 0
