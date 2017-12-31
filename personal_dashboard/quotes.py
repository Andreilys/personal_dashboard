import requests

class Quote():
    def __init__(self):
        #Quote generated from https://quotes.rest/#!/qod/get_qod_categories
        headers = { "Accept": "application/json"}
        r = requests.get('https://quotes.rest/qod', headers=headers)
        #Quotes has a daily limit that we exceed unforunately
        try:
            self.content = r.json()["contents"]["quotes"][0]["quote"]
            self.author = r.json()["contents"]["quotes"][0]["author"]
        except:
            self.content = "Everything we hear is an opinion, not a fact. Everything we see is a perspective, not the truth."
            self.author =  "Marcus Aurelius"
