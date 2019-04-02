import requests
import json
import datetime
try:
    from .personal_info import MEDIUM_USER
except:
    from personal_info import MEDIUM_USER


class Articles():
    def __init__(self):
        self.medium_url = f'https://medium.com/@{MEDIUM_USER}/'
        self.response = requests.get(self.medium_url + 'latest?format=json')
        self.response_dict = json.loads(
            self.response.text.split('])}while(1);</x>')[1])
        self.posts = self.response_dict['payload']['references']['Post']


        # Returns the past n articles you've writte
    def get_past_n_articles(self, number_of_articles):
        titles = []
        urls = []
        for key in self.posts:
            titles.append(self.posts[key]['title'])
            urls.append(self.medium_url + self.posts[key]['id'])
        titles_and_url = "<strong><a href=" + "\"" + self.medium_url + \
            "\">Recently Written Articles:</a></strong><ol>"
        for i in range(number_of_articles):
            titles_and_url += f'<li><a href={urls[i]}> {titles[i]} </a></li>'
        titles_and_url += "</ol>"
        return titles_and_url


    # Returns a dict containing your reading history for the past n months
    def get_past_n_month_writing_history(self, months):
        dates = []
        data_values = []
        month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        article_count_dict = {}
        n_months_ago = self.get_n_months_ago(months)
        for key in self.posts:
            timestamp = int(self.posts[key]['firstPublishedAt']) / 1000
            month_published = datetime.datetime.fromtimestamp(timestamp).month
            year_published = datetime.datetime.fromtimestamp(timestamp).year
            dt = datetime.date(int(year_published), int(month_published), 1)
            if dt >= n_months_ago:
                dt = str(dt)
                if dt in article_count_dict:
                    article_count_dict[dt] += 1
                else:
                    article_count_dict[dt] = 1
        #If there was a month that I didn't finish an article, I want to set it to 0
        for some_month in range(7):
            some_month_ago = str(self.get_n_months_ago(some_month))
            if some_month_ago not in article_count_dict:
                article_count_dict[some_month_ago] = 0
        sorted_keys = sorted(article_count_dict.keys())
        for key in sorted_keys:
            year = key.split("-")[0]
            month = key.split("-")[1]
            dates.append(f'{month}/{year}')
            data_values.append(article_count_dict[key])
        writing_history = [{"label": "Number of Articles Written",
                            "backgroundColor": "#33702a", "data": data_values}]
        return writing_history, dates


    # Helper function which returns n month ago from now
    def get_n_months_ago(self, month):
        past_month = datetime.datetime.now().month - month
        past_year = datetime.datetime.now().year
        if past_month < 1:
            past_month = 12 + past_month
            past_year = past_year - 1
        return datetime.date(past_year, past_month, 1)

