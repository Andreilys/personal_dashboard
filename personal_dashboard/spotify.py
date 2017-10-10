import sys
import spotipy
import spotipy.util as util
try:
    from .personal_info import SPOTIFY
except:
    from personal_info import SPOTIFY



#The spotify class has two methods: get_monthly_top_tracks() which returns
# the top 5 tracks for that month, the get_monthly_top_artists() returns the top
# three artists for that month
class Spotify():
    def __init__(self):
        self.token = util.prompt_for_user_token(SPOTIFY['email'],'user-top-read',client_id=SPOTIFY['client_id'],client_secret=SPOTIFY['client_secret'],redirect_uri=SPOTIFY['redirect_uri'])
        self.sp = spotipy.Spotify(auth=self.token)

    def get_monthly_top_tracks(self):
        top_tracks = self.sp.current_user_top_tracks(limit=5, time_range='short_term')
        track_list = []
        for item in top_tracks['items']:
            track_name = item["name"]
            artist_name = item["artists"][0]["name"]
            external_url = item["external_urls"]["spotify"]
            track_list.append("<a target='_blank' href='{0}'>{1} by {2}</a><br>".format(external_url, track_name, artist_name))
        return ''.join(track_list)

    def get_monthly_top_artists(self):
        top_artists = self.sp.current_user_top_artists(limit=3, time_range='short_term')
        artist_list = []
        for item in top_artists['items']:
            artist = item['name']
            external_url = item['external_urls']['spotify']
            artist_list.append("<a target='_blank' href='{0}'>{1}</a><br>".format(external_url, artist))
        return artist_list
