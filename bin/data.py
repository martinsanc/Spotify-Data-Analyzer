import csv
import pandas as pd

DATA_PATH = "data/"

def get_playlists(sp):
    results = sp.current_user_playlists()
    playlists = results['items']
    while results['next']:
        results = sp.next(results)
        playlists.extend(results['items'])
    return pd.DataFrame(playlists)[['uri', 'id', 'name']]
    


def get_tracks_from_playlist(sp, playlist_uri):
    results = sp.playlist_tracks(playlist_uri)
    tracks = results['items']['track']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items']['track'])
    return pd.DataFrame(tracks)