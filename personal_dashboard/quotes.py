import requests

#Quote generated from https://quotes.rest/#!/qod/get_qod_categories
headers = { "Accept": "application/json"}
r = requests.get('https://quotes.rest/qod', headers=headers)

try:
    QUOTE = [r.json()["contents"]["quotes"][0]["quote"], r.json()["contents"]["quotes"][0]["author"]]
except:
    QUOTE = ["Everything we hear is an opinion, not a fact. Everything we see is a perspective, not the truth.", "Marcus Aurelius"]
