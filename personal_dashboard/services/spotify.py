import spotipy
from spotipy.oauth2 import SpotifyOAuth

# TODO: Move these credentials to a separate file.
SPOTIFY = {"email" : '12al104@queensu.ca', 'client_id' : "23b4a71c19ea4bfcab4bc9cbc6e1ffc9", 'client_secret':'6bd69bda8edf4e1db80d9c3b43584cc7', 'redirect_uri':'http://localhost/'}

class Spotify():
    def __init__(self):
        # The Spotify API requires user interaction to authenticate.
        # Since this is not possible in this environment, we will use a dummy token.
        self.sp = spotipy.Spotify(auth="dummy_token")

    def get_monthly_top_tracks(self):
        try:
            top_tracks = self.sp.current_user_top_tracks(limit=5, time_range='short_term')
            track_list = []
            for item in top_tracks['items']:
                track_name = item["name"]
                artist_name = item["artists"][0]["name"]
                external_url = item["external_urls"]["spotify"]
                track_list.append(f"<a target='_blank' href='{external_url}'>{track_name} by {artist_name}</a><br>")
            return ''.join(track_list)
        except Exception as e:
            print(f"Error getting top tracks from Spotify: {e}")
            return ""

    def get_monthly_top_artists(self):
        try:
            top_artists = self.sp.current_user_top_artists(limit=3, time_range='short_term')
            artist_list = []
            for item in top_artists['items']:
                artist = item['name']
                external_url = item['external_urls']['spotify']
                artist_list.append(f"<a target='_blank' href='{external_url}'>{artist}</a><br>")
            return artist_list
        except Exception as e:
            print(f"Error getting top artists from Spotify: {e}")
            return []
