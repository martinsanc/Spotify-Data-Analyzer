from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from bin.credentials import CLIENT_ID, CLIENT_SECRET


redirect_uri = "http://localhost/"

scopes = ['playlist-read-collaborative',
          'playlist-read-private',
          'user-follow-read',
          'user-library-read',
          'user-read-recently-played',
          'user-top-read']


def spotify_auth():
    auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=redirect_uri, scope=scopes)
    sp = Spotify(auth_manager=auth_manager)
    return sp