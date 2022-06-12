import spotipy
from spotipy.oauth2 import SpotifyOAuth

import bin.cred as cred
from bin.fetch import fetch_user_playlist_tracks, fetch_user_top_tracks

# API Permissions
scope = "playlist-read-collaborative playlist-read-private user-read-recently-played user-top-read"

def run_client():
    # Creates the spotify client with the given ids in cred.py file.
    auth_manager = SpotifyOAuth(client_id=cred.CLIENT_ID, client_secret= cred.CLIENT_SECRET, redirect_uri=cred.REDIRECT_URL, scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=20)
    return sp


if __name__=='__main__':
    print("Creating connection...")
    sp = run_client()

    fetch_user_playlist_tracks(sp, debug=True)
    fetch_user_top_tracks(sp, debug=True)