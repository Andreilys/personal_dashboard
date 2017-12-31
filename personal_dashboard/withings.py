from nokia import NokiaAuth, NokiaApi
import pickle
try:
    from .personal_info import WITHINGS_KEYS
except:
    from personal_info import WITHINGS_KEYS

#The withings class opens up the pickle file and saves it as the weight unless
# that file doesn't exist than the user needs to authenticate and save a new pickle
#file
class Withings():
    def __init__(self):
        try:
            with open('personal_dashboard/nokia_data.pkl', 'rb') as pickle_file:
                nokia = pickle.load(pickle_file)
                self.measures = nokia.get_measures()
                measures = nokia.get_measures(limit=1)
                self.weight = round(float(measures[0].weight)*2.20462, 2)
                pickle_file.close()
        except:
            auth = NokiaAuth(WITHINGS_KEYS['API_KEY'], WITHINGS_KEYS['API_SECRET'])
            authorize_url = auth.get_authorize_url()
            print("Go to %s allow the app and copy your oauth_verifier" % authorize_url)
            oauth_verifier = input('Please enter your oauth_verifier: ')
            creds = auth.get_credentials(oauth_verifier)
            client = NokiaApi(creds)
            with open('personal_dashboard/nokia_data.pkl', 'wb') as output:
                pickle.dump(client, output, pickle.HIGHEST_PROTOCOL)
            self.measures = client.get_measures()
            measures = client.get_measures(limit=1)
            #Convert Kg to Lbs
            self.weight = round(float(measures[0].weight)*2.20462, 2)



    def get_weight_line_data(self):
        weight_data = []
        dates = []
        for data in self.measures:
            if data.weight:
                year = str(data.date).split('-')[0]
                month = str(data.date).split('-')[1]
                day = str(data.date).split('-')[2].split("T")[0]
                date = month + "-" + day + "-" + year
                dates.append(date)
                weight_data.append(round(float(data.weight)*2.20462, 2))
        weight_data.reverse()
        dates.reverse()
        return weight_data, dates
