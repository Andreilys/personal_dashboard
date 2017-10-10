from nokia import NokiaAuth, NokiaApi
import pickle
from .personal_info import WITHINGS_KEYS

#The withings class opens up the pickle file and saves it as the weight unless
# that file doesn't exist than the user needs to authenticate and save a new pickle
#file
class Withings():
    def __init__(self):
        try:
            with open('personal_dashboard/nokia_data.pkl', 'rb') as input:
                nokia = pickle.load(input)
                measures = nokia.get_measures(limit=1)
                self.weight = str(round(float(measures[0].weight)*2.20462, 2)) + " lbs"
        except:
            auth = NokiaAuth(WITHINGS_KEYS['API_KEY'], WITHINGS_KEYS['API_SECRET'])
            authorize_url = auth.get_authorize_url()
            print("Go to %s allow the app and copy your oauth_verifier" % authorize_url)
            oauth_verifier = input('Please enter your oauth_verifier: ')
            creds = auth.get_credentials(oauth_verifier)
            client = NokiaApi(creds)
            with open('nokia_data.pkl', 'wb') as output:
                pickle.dump(client, output, pickle.HIGHEST_PROTOCOL)
