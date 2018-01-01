import requests
try:
    from .personal_info import RESCUETIME_API_KEY
except:
    from personal_info import RESCUETIME_API_KEY
import datetime as DT

#This rescuetime class interacts with the rescuetime API allowing it to pull current day and weekly data
# The methods that are used are the get_current_days_data() which returns the
# hours of productive, unproductive hours and the top three sources and get_past_seven_days_data()
# which returns
class RescueTime:
    def __init__(self):
        self.key = RESCUETIME_API_KEY

    #This method returns a dictionary containing the top three contributing sources to rescuetime,
    # productive minutes and unproductive minutes spent up until now
    def get_current_days_data(self):
        try:
            response = requests.get("https://www.rescuetime.com/anapi/data?key={0}&format=json".format(RESCUETIME_API_KEY))
            json = response.json()["rows"]
        # In the event that theres currently no daily data, return 0
        except:
            daily_data = {"productive_hours" : 0, "unproductive_hours" : 0, "top_three_sources" : "None"}
            return daily_data
        top_three_sources = []
        productive_hours = 0
        unproductive_hours = 0
        for index, data in enumerate(json):
            if index < 3:
                top_three_sources.append(str(data[3]).capitalize() + " - " + str(round(data[1]/60/60, 2)))
            if data[5] > 0:
                productive_hours += data[1]/60/60
            elif data[5] < 0:
                unproductive_hours += data[1]/60/60
        productive_hours = round(productive_hours, 2)
        unproductive_hours = round(unproductive_hours, 2)
        daily_data = {"productive_hours" : productive_hours, "unproductive_hours" : unproductive_hours, "top_three_sources" : ", ".join(top_three_sources)}
        return daily_data


    # This method is a helper method because the request get method occasionally throews
    # an error by returning a None object
    def get_weekly_data(self):
        try:
            today = DT.date.today()
            week_ago = today - DT.timedelta(days=7)
            response = requests.get("https://www.rescuetime.com/anapi/data?key={0}&perspective=rank&interval=week&restrict_begin={1}&restrict_end={2}&format=json".format(RESCUETIME_API_KEY, str(week_ago), str(today)))
            return response.json()["rows"]
        except:
            return 0

    #This method returns a dictionary containing the top five contributing sources to rescuetime,
    # productive hours and unproductive hours in the last 7 days
    def get_past_seven_days_data(self):
        json = self.get_weekly_data()
        #This is meant as a safeguard in case resucetime has no weekly data
        if json == 0:
            weekly_data = {"productive_hours" : 0, "unproductive_hours" : 0, "top_five_sources" : "None"}
        top_five_sources = []
        productive_hours = 0
        unproductive_hours = 0
        for index, data in enumerate(json):
            #Grab the first 5 sources since its sorted by ascending order in terms of hours
            if index < 5:
                top_five_sources.append(str(data[3]).capitalize() + " - " + str(round(data[1]/60/60, 2)))
            if data[5] > 0:
                productive_hours += data[1]/60/60
            elif data[5] < 0:
                unproductive_hours += data[1]/60/60
        productive_hours = round(productive_hours, 2)
        unproductive_hours = round(unproductive_hours, 2)
        weekly_data = {"productive_hours" : productive_hours, "unproductive_hours" : unproductive_hours, "top_five_sources" : ", ".join(top_five_sources)}
        return weekly_data

    def get_rescuetime_data(self, date):
            today = DT.date.today()
            date = today - DT.timedelta(days=date)
            response = requests.get("https://www.rescuetime.com/anapi/data?key={0}&perspective=rank&interval=week&restrict_begin={1}&restrict_end={2}&format=json".format(RESCUETIME_API_KEY, str(date), str(date)))
            while (response.status_code == 502):
                response = requests.get("https://www.rescuetime.com/anapi/data?key={0}&perspective=rank&interval=week&restrict_begin={1}&restrict_end={2}&format=json".format(RESCUETIME_API_KEY, str(date), str(date)))
            return date, response.json()["rows"]

    #This function is used to return dates and a formatted list containing dictionaries
    # for use in the create_rescuetime_bar function in scripts.js
    def get_daily_week_view(self):
        dates = []
        productive_array_values = []
        unproductive_array_values = []
        counter = 6
        for date in range(7):
            productive_sum = 0
            unproductive_sum = 0
            date, data = self.get_rescuetime_data(counter)
            counter -= 1
            for item in data:
                try:
                    #The 5 here is referring to the productivity/unproductivity identifier
                    if item[5] > 0:
                        productive_sum += item[1]/60/60
                    elif item[5] < 0:
                        unproductive_sum += item[1]/60/60
                except:
                    continue
            dates.append(date.strftime("%d/%m"))
            productive_array_values.append(round(productive_sum,2))
            unproductive_array_values.append(round(unproductive_sum, 2))
        rescuetime_data = [{"label" : "Productive Hours", "backgroundColor": "#33702a", "data" : productive_array_values},
                        {"label" : "Unproductive Hours", "backgroundColor": "#b30000", "data" : unproductive_array_values}]
        return rescuetime_data, dates
