import spotipy
from spotipy.oauth2 import SpotifyOAuth

import bin.cred as cred
from bin.data import *

# API Permissions
scope = "playlist-read-collaborative playlist-read-private user-read-recently-played user-top-read"


def run_client():
    # Creates the spotify client with the given ids in cred.py file.
    auth_manager = SpotifyOAuth(client_id=cred.CLIENT_ID, client_secret= cred.CLIENT_SECRET, redirect_uri=cred.REDIRECT_URL, scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp


if __name__=='__main__':
    print("Creating connection...")
    sp = run_client()

    playlists = get_playlists(sp)
    tracks = get_tracks_from_playlist(sp, 'spotify:playlist:5VVrMk2Zna7wyySHMxakH5')

    print()

