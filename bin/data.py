import csv
import pandas as pd


DATA_PATH = "data/"


def fetch_playlists(sp):
    results = sp.current_user_playlists()
    playlists = results['items']
    while results['next']:
        results = sp.next(results)
        playlists.extend(results['items'])
    playlists = playlists_to_df(playlists)
    playlists.to_csv("{}playlists.csv".format(DATA_PATH), sep=',', index=False)
    return playlists


def fetch_tracks_from_playlist(sp, playlist_uri):
    results = sp.playlist_tracks(playlist_uri)
    tracks = results['items']
    track_list = []
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    for item, track in enumerate(tracks):
        if track['track']['track'] and not track['is_local']:
            track = {'name': track['track']['name'],
                     'id': track['track']['id'],
                     'uri': track['track']['uri'],
                     'popularity': track['track']['popularity'],
                     'artist_name': track['track']['artists'][0]['name'],
                     'artist_id': track['track']['artists'][0]['id'],
                     'artist_uri': track['track']['artists'][0]['id'],
                     'album_name': track['track']['album']['name'],
                     'album_id': track['track']['album']['id'],
                     'album_uri': track['track']['album']['uri'],
                     'release_date': track['track']['album']['release_date'],
                     'duration_ms': track['track']['duration_ms'],
                     'image_url': track['track']['album']['images'][0]['url']}
            audio_features = fetch_audio_features(sp, track['uri'])
            track = track | audio_features
            track_list.append(track)
    return pd.DataFrame(track_list)


def fetch_audio_features(sp, track_uri):
    results = sp.audio_features(track_uri)
    audio_features = {
        'track_uri': track_uri,
        'danceability': results[0]['danceability'],
        'energy': results[0]['energy'],
        'key': results[0]['key'],
        'loudness': results[0]['loudness'],
        'mode': results[0]['mode'],
        'speechiness': results[0]['speechiness'],
        'acousticness': results[0]['acousticness'],
        'instrumentalness': results[0]['instrumentalness'],
        'liveness': results[0]['liveness'],
        'valence': results[0]['valence'],
        'tempo': results[0]['tempo'],
        'duration_ms': results[0]['duration_ms'],
        'time_signature': results[0]['time_signature']
    }
    return audio_features


def playlists_to_df(playlists):
    playlist_list = []
    for i, playlist in enumerate(playlists):
        playlist_list.append({
            'name': playlist['name'],
            'id': playlist['id'],
            'uri': playlist['uri'],
            'description': playlist['description'],
            'collaborative': playlist['collaborative'],
            'public': playlist['public'],
            'owner_name': playlist['owner']['display_name'],
            'owner_id': playlist['owner']['id'],
            'owner_uri': playlist['owner']['uri'],
            'track_count': playlist['tracks']['total']
        })
    return pd.DataFrame(playlist_list)