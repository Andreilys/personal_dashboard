import requests

#The chess class is used to get the number of wins/draws/losses (get_games()) as
# well as the current rating for blitz chess on lichess.org
class Chess():
    def __init__(self):
        r = requests.get('https://en.lichess.org/api/user/andreilys').json()
        self.draw = r['count']['draw']
        self.win = r['count']['win']
        self.loss =r['count']['loss']
        self.rating = r['perfs']['blitz']['rating']
        self.url = r['url']


    def get_games(self):
        return "Wins: {0}, Losses: {1}, Draws: {2}".format(self.win, self.loss, self.draw)


    def get_rating(self):
        return "<a href='{0}'>Blitz Chess rating: {1}</a>".format(self.url, self.rating)
