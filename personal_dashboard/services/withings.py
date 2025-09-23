from withings_api import WithingsAuth, WithingsApi, AuthScope
from withings_api.common import get_measure_value, MeasureType
import pickle

# TODO: Move these credentials to a separate file.
WITHINGS_KEYS = {'API_KEY': 'beb65f13184d5fcfecbaf3019621887425ebedf6cc43c54670b849913fcb2237',
                 'API_SECRET': '6912cfe93678941e17524ec2a16d75b269fb94197f8f1a207d9aa4c3578cdeb5'}

class Withings():
    def __init__(self):
        self.measures = []
        self.weight = 0
        # The following code is for authenticating and getting data from the Withings API.
        # It is commented out because it requires user interaction to authenticate.
        # To enable this, you will need to uncomment the code and follow the instructions
        # in the terminal to authorize the application.
        #
        # try:
        #     with open('personal_dashboard/withings_data.pkl', 'rb') as pickle_file:
        #         credentials = pickle.load(pickle_file)
        # except:
        #     auth = WithingsAuth(
        #         client_id=WITHINGS_KEYS['API_KEY'],
        #         consumer_secret=WITHINGS_KEYS['API_SECRET'],
        #         callback_uri='http://localhost:8888/withings_callback',
        #         scope=(
        #             AuthScope.USER_ACTIVITY,
        #             AuthScope.USER_METRICS,
        #             AuthScope.USER_INFO,
        #             AuthScope.USER_SLEEP_EVENTS,
        #         )
        #     )
        #     authorize_url = auth.get_authorize_url()
        #     print(f"Go to {authorize_url} to authorize the app.")
        #     code = input("Enter the code from the redirect URI: ")
        #     credentials = auth.get_credentials(code)
        #     with open('personal_dashboard/withings_data.pkl', 'wb') as output:
        #         pickle.dump(credentials, output, pickle.HIGHEST_PROTOCOL)
        #
        # api = WithingsApi(credentials)
        # self.measures = api.measure_get_meas().measures
        # if self.measures:
        #     self.weight = round(float(get_measure_value(self.measures[0], with_measure_type=MeasureType.WEIGHT)) * 2.20462, 2)

    def get_weight_line_data(self):
        weight_data = []
        dates = []
        # The following code is for parsing the measures from the Withings API.
        # It is commented out because the API call is disabled.
        #
        # for data in self.measures:
        #     if get_measure_value(data, with_measure_type=MeasureType.WEIGHT):
        #         year = str(data.date).split('-')[0]
        #         month = str(data.date).split('-')[1]
        #         day = str(data.date).split(' ')[0].split('-')[2]
        #         date = f"{month}-{day}-{year}"
        #         dates.append(date)
        #         weight_data.append(round(float(get_measure_value(data, with_measure_type=MeasureType.WEIGHT)) * 2.20462, 2))
        # weight_data.reverse()
        # dates.reverse()
        return weight_data, dates
